const router = require('express').Router();
const { User } = require('../models');
const { isAuthenticated } = require('../middleware/auth');
const { AppError } = require('../middleware/errorHandler');
const Joi = require('joi');
const bcrypt = require('bcrypt');

// Validation schemas
const updateProfileSchema = Joi.object({
  name: Joi.string().optional().min(1).max(100),
  email: Joi.string().email().optional()
});

const changePasswordSchema = Joi.object({
  currentPassword: Joi.string().required(),
  newPassword: Joi.string().required().min(8).max(100)
    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .message('Password must contain at least one uppercase letter, one lowercase letter, one number and one special character')
});

// Get user profile
router.get('/profile', isAuthenticated, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    
    const user = await User.findByPk(userId, {
      attributes: [
        'id', 'email', 'name', 'profilePicture', 
        'twoFactorEnabled', 'isEmailVerified', 
        'createdAt', 'lastLoginAt'
      ]
    });
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    res.json({ user });
  } catch (error) {
    next(error);
  }
});

// Update user profile
router.put('/profile', isAuthenticated, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    
    // Validate input
    const { error, value } = updateProfileSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400);
    }
    
    const user = await User.findByPk(userId);
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    // Check if email is being changed and if it's already taken
    if (value.email && value.email !== user.email) {
      const existingUser = await User.findOne({ where: { email: value.email } });
      if (existingUser) {
        throw new AppError('Email already in use', 409);
      }
      // Mark email as unverified if changed
      value.isEmailVerified = false;
    }
    
    await user.update(value);
    
    res.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        profilePicture: user.profilePicture,
        twoFactorEnabled: user.twoFactorEnabled,
        isEmailVerified: user.isEmailVerified
      },
      message: 'Profile updated successfully'
    });
  } catch (error) {
    next(error);
  }
});

// Change password
router.post('/change-password', isAuthenticated, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    
    // Validate input
    const { error, value } = changePasswordSchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400);
    }
    
    const user = await User.findByPk(userId);
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    // OAuth users might not have a password
    if (!user.password) {
      throw new AppError('Password change not available for OAuth accounts', 400);
    }
    
    // Verify current password
    const isValid = await user.validatePassword(value.currentPassword);
    if (!isValid) {
      throw new AppError('Current password is incorrect', 401);
    }
    
    // Update password
    user.password = value.newPassword;
    await user.save();
    
    res.json({
      message: 'Password changed successfully'
    });
  } catch (error) {
    next(error);
  }
});

// Delete account
router.delete('/account', isAuthenticated, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const { password, confirmation } = req.body;
    
    if (confirmation !== 'DELETE MY ACCOUNT') {
      throw new AppError('Please confirm account deletion', 400);
    }
    
    const user = await User.findByPk(userId);
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    // Verify password for accounts with password
    if (user.password) {
      if (!password) {
        throw new AppError('Password is required', 400);
      }
      
      const isValid = await user.validatePassword(password);
      if (!isValid) {
        throw new AppError('Invalid password', 401);
      }
    }
    
    // Delete user (cascades to related data)
    await user.destroy();
    
    // Destroy session
    req.session.destroy();
    
    res.json({
      message: 'Account deleted successfully'
    });
  } catch (error) {
    next(error);
  }
});

// Export user data
router.get('/export', isAuthenticated, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    
    const user = await User.findByPk(userId, {
      include: [{
        association: 'apiKeys',
        attributes: ['id', 'name', 'service', 'description', 'createdAt', 'lastUsedAt', 'tags']
      }]
    });
    
    if (!user) {
      throw new AppError('User not found', 404);
    }
    
    const exportData = {
      user: {
        email: user.email,
        name: user.name,
        createdAt: user.createdAt,
        twoFactorEnabled: user.twoFactorEnabled
      },
      apiKeys: user.apiKeys.map(key => ({
        name: key.name,
        service: key.service,
        description: key.description,
        createdAt: key.createdAt,
        lastUsedAt: key.lastUsedAt,
        tags: key.tags
      })),
      exportedAt: new Date().toISOString()
    };
    
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Content-Disposition', `attachment; filename="api-keys-export-${Date.now()}.json"`);
    res.json(exportData);
  } catch (error) {
    next(error);
  }
});

module.exports = router;