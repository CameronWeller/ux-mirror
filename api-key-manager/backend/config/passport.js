const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const MicrosoftStrategy = require('passport-microsoft').Strategy;
const { User } = require('../models');

// Serialize user for session
passport.serializeUser((user, done) => {
  done(null, user.id);
});

// Deserialize user from session
passport.deserializeUser(async (id, done) => {
  try {
    const user = await User.findByPk(id);
    done(null, user);
  } catch (error) {
    done(error, null);
  }
});

// Google OAuth Strategy
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: process.env.GOOGLE_CALLBACK_URL,
  scope: ['profile', 'email']
}, async (accessToken, refreshToken, profile, done) => {
  try {
    // Check if user exists with Google ID
    let user = await User.findOne({ where: { googleId: profile.id } });
    
    if (user) {
      // Update last login
      await user.resetLoginAttempts();
      return done(null, user);
    }
    
    // Check if user exists with same email
    user = await User.findOne({ where: { email: profile.emails[0].value } });
    
    if (user) {
      // Link Google account to existing user
      user.googleId = profile.id;
      user.profilePicture = profile.photos[0]?.value || user.profilePicture;
      user.isEmailVerified = true;
      await user.save();
      await user.resetLoginAttempts();
      return done(null, user);
    }
    
    // Create new user
    user = await User.create({
      googleId: profile.id,
      email: profile.emails[0].value,
      name: profile.displayName,
      profilePicture: profile.photos[0]?.value,
      isEmailVerified: true
    });
    
    return done(null, user);
  } catch (error) {
    return done(error, null);
  }
}));

// Microsoft OAuth Strategy
passport.use(new MicrosoftStrategy({
  clientID: process.env.MICROSOFT_CLIENT_ID,
  clientSecret: process.env.MICROSOFT_CLIENT_SECRET,
  callbackURL: process.env.MICROSOFT_CALLBACK_URL,
  scope: ['user.read']
}, async (accessToken, refreshToken, profile, done) => {
  try {
    // Check if user exists with Microsoft ID
    let user = await User.findOne({ where: { microsoftId: profile.id } });
    
    if (user) {
      // Update last login
      await user.resetLoginAttempts();
      return done(null, user);
    }
    
    // Check if user exists with same email
    user = await User.findOne({ where: { email: profile.emails[0].value } });
    
    if (user) {
      // Link Microsoft account to existing user
      user.microsoftId = profile.id;
      user.isEmailVerified = true;
      await user.save();
      await user.resetLoginAttempts();
      return done(null, user);
    }
    
    // Create new user
    user = await User.create({
      microsoftId: profile.id,
      email: profile.emails[0].value,
      name: profile.displayName,
      isEmailVerified: true
    });
    
    return done(null, user);
  } catch (error) {
    return done(error, null);
  }
}));

module.exports = passport;