const { Sequelize } = require('sequelize');
const path = require('path');

// Initialize Sequelize
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: path.join(__dirname, '..', 'database.sqlite'),
  logging: process.env.NODE_ENV === 'development' ? console.log : false,
  define: {
    timestamps: true,
    underscored: true,
  }
});

// Import models
const User = require('./User')(sequelize);
const ApiKey = require('./ApiKey')(sequelize);
const TwoFactorBackup = require('./TwoFactorBackup')(sequelize);

// Define associations
User.hasMany(ApiKey, {
  foreignKey: 'user_id',
  as: 'apiKeys',
  onDelete: 'CASCADE'
});

ApiKey.belongsTo(User, {
  foreignKey: 'user_id',
  as: 'user'
});

User.hasMany(TwoFactorBackup, {
  foreignKey: 'user_id',
  as: 'backupCodes',
  onDelete: 'CASCADE'
});

TwoFactorBackup.belongsTo(User, {
  foreignKey: 'user_id',
  as: 'user'
});

module.exports = {
  sequelize,
  User,
  ApiKey,
  TwoFactorBackup
};