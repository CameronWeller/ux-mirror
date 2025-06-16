const { DataTypes } = require('sequelize');
const bcrypt = require('bcrypt');

module.exports = (sequelize) => {
  const TwoFactorBackup = sequelize.define('TwoFactorBackup', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    code: {
      type: DataTypes.STRING,
      allowNull: false
    },
    isUsed: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    },
    usedAt: {
      type: DataTypes.DATE,
      allowNull: true
    }
  }, {
    hooks: {
      beforeCreate: async (backup) => {
        // Hash the backup code before storing
        backup.code = await bcrypt.hash(backup.code, 10);
      }
    }
  });

  // Instance methods
  TwoFactorBackup.prototype.verify = async function(code) {
    if (this.isUsed) {
      return false;
    }
    
    const isValid = await bcrypt.compare(code, this.code);
    
    if (isValid) {
      await this.update({
        isUsed: true,
        usedAt: new Date()
      });
    }
    
    return isValid;
  };

  return TwoFactorBackup;
};