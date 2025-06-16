const router = require('express').Router();
const passport = require('passport');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');
const { User, TwoFactorBackup } = require('../models');
const { generateToken, isAuthenticated } = require('../middleware/auth');
const { generateBackupCodes } = require('../utils/encryption');
const { AppError } = require('../middleware/errorHandler');

// Load passport configuration
require('../config/passport');

// Local login
router.post('/login', async (req, res, next) => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      throw new AppError('Email and password are required', 400);
    }
    
    const user = await User.findOne({ where: { email } });
    
    if (!user) {
      throw new AppError('Invalid credentials', 401);
    }
    
    // Check if account is locked
    if (user.isLocked()) {
      throw new AppError('Account is locked. Please try again later.', 423);
    }
    
    // Validate password
    const isValid = await user.validatePassword(password);
    
    if (!isValid) {
      await user.incrementLoginAttempts();
      throw new AppError('Invalid credentials', 401);
    }
    
    // Reset login attempts
    await user.resetLoginAttempts();
    
    // Check if 2FA is enabled
    if (user.twoFactorEnabled) {
      req.session.pendingUserId = user.id;
      return res.json({
        requires2FA: true,
        message: 'Please provide 2FA code'
      });
    }
    
    // Generate token
    const token = generateToken(user.id);
    req.session.userId = user.id;
    
    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        profilePicture: user.profilePicture,
        twoFactorEnabled: user.twoFactorEnabled
      }
    });
  } catch (error) {
    next(error);
  }
});

// Verify 2FA code
router.post('/verify-2fa', async (req, res, next) => {
  try {
    const { code } = req.body;
    const userId = req.session.pendingUserId;
    
    if (!userId) {
      throw new AppError('No pending 2FA verification', 400);
    }
    
    if (!code) {
      throw new AppError('2FA code is required', 400);
    }
    
    const user = await User.findByPk(userId);
    
    if (!user || !user.twoFactorEnabled) {
      throw new AppError('Invalid request', 400);
    }
    
    // Try to verify with TOTP first
    const verified = speakeasy.totp.verify({
      secret: user.twoFactorSecret,
      encoding: 'base32',
      token: code,
      window: 2
    });
    
    if (verified) {
      const token = generateToken(user.id);
      req.session.userId = user.id;
      req.session.twoFactorVerified = true;
      delete req.session.pendingUserId;
      
      return res.json({
        token,
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          profilePicture: user.profilePicture,
          twoFactorEnabled: user.twoFactorEnabled
        }
      });
    }
    
    // Try backup codes
    const backupCodes = await TwoFactorBackup.findAll({
      where: { 
        user_id: userId,
        isUsed: false
      }
    });
    
    for (const backupCode of backupCodes) {
      const isValid = await backupCode.verify(code);
      if (isValid) {
        const token = generateToken(user.id);
        req.session.userId = user.id;
        req.session.twoFactorVerified = true;
        delete req.session.pendingUserId;
        
        return res.json({
          token,
          user: {
            id: user.id,
            email: user.email,
            name: user.name,
            profilePicture: user.profilePicture,
            twoFactorEnabled: user.twoFactorEnabled
          },
          message: 'Backup code used successfully'
        });
      }
    }
    
    throw new AppError('Invalid 2FA code', 401);
  } catch (error) {
    next(error);
  }
});

// Setup 2FA
router.post('/setup-2fa', isAuthenticated, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const user = await User.findByPk(userId);
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    if (user.twoFactorEnabled) {
      throw new AppError('2FA is already enabled', 400);
    }
    
    // Generate secret
    const secret = speakeasy.generateSecret({
      name: `${process.env.TWO_FACTOR_APP_NAME} (${user.email})`,
      issuer: process.env.TWO_FACTOR_ISSUER
    });
    
    // Generate QR code
    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);
    
    // Temporarily store secret (not enabled yet)
    req.session.tempSecret = secret.base32;
    
    res.json({
      qrCode: qrCodeUrl,
      secret: secret.base32,
      message: 'Scan QR code with your authenticator app and verify with a code'
    });
  } catch (error) {
    next(error);
  }
});

// Enable 2FA
router.post('/enable-2fa', isAuthenticated, async (req, res, next) => {
  try {
    const { code } = req.body;
    const userId = req.user?.id || req.userId;
    const tempSecret = req.session.tempSecret;
    
    if (!tempSecret) {
      throw new AppError('No 2FA setup in progress', 400);
    }
    
    if (!code) {
      throw new AppError('Verification code is required', 400);
    }
    
    // Verify the code
    const verified = speakeasy.totp.verify({
      secret: tempSecret,
      encoding: 'base32',
      token: code,
      window: 2
    });
    
    if (!verified) {
      throw new AppError('Invalid verification code', 401);
    }
    
    const user = await User.findByPk(userId);
    
    // Enable 2FA
    user.twoFactorSecret = tempSecret;
    user.twoFactorEnabled = true;
    await user.save();
    
    // Generate backup codes
    const backupCodes = generateBackupCodes();
    
    // Save backup codes
    for (const code of backupCodes) {
      await TwoFactorBackup.create({
        user_id: userId,
        code: code
      });
    }
    
    delete req.session.tempSecret;
    req.session.twoFactorVerified = true;
    
    res.json({
      message: '2FA enabled successfully',
      backupCodes: backupCodes
    });
  } catch (error) {
    next(error);
  }
});

// Disable 2FA
router.post('/disable-2fa', isAuthenticated, async (req, res, next) => {
  try {
    const { password } = req.body;
    const userId = req.user?.id || req.userId;
    
    const user = await User.findByPk(userId);
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    if (!user.twoFactorEnabled) {
      throw new AppError('2FA is not enabled', 400);
    }
    
    // Verify password
    if (user.password) {
      if (!password) {
        throw new AppError('Password is required', 400);
      }
      
      const isValid = await user.validatePassword(password);
      if (!isValid) {
        throw new AppError('Invalid password', 401);
      }
    }
    
    // Disable 2FA
    user.twoFactorEnabled = false;
    user.twoFactorSecret = null;
    await user.save();
    
    // Delete backup codes
    await TwoFactorBackup.destroy({
      where: { user_id: userId }
    });
    
    res.json({
      message: '2FA disabled successfully'
    });
  } catch (error) {
    next(error);
  }
});

// Google OAuth routes
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

router.get('/google/callback', 
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    const token = generateToken(req.user.id);
    res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${token}`);
  }
);

// Microsoft OAuth routes
router.get('/microsoft', passport.authenticate('microsoft'));

router.get('/microsoft/callback',
  passport.authenticate('microsoft', { failureRedirect: '/login' }),
  (req, res) => {
    const token = generateToken(req.user.id);
    res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${token}`);
  }
);

// Logout
router.post('/logout', (req, res) => {
  req.logout((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    req.session.destroy();
    res.json({ message: 'Logged out successfully' });
  });
});

// Get current user
router.get('/me', isAuthenticated, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const user = await User.findByPk(userId, {
      attributes: ['id', 'email', 'name', 'profilePicture', 'twoFactorEnabled']
    });
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    res.json({ user });
  } catch (error) {
    next(error);
  }
});

module.exports = router;