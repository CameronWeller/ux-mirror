const { DataTypes } = require('sequelize');
const { encrypt, decrypt } = require('../utils/encryption');

module.exports = (sequelize) => {
  const ApiKey = sequelize.define('ApiKey', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    keyValue: {
      type: DataTypes.TEXT,
      allowNull: false,
      get() {
        const rawValue = this.getDataValue('keyValue');
        return rawValue ? decrypt(rawValue) : null;
      },
      set(value) {
        this.setDataValue('keyValue', encrypt(value));
      }
    },
    service: {
      type: DataTypes.STRING,
      allowNull: false
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    lastUsedAt: {
      type: DataTypes.DATE,
      allowNull: true
    },
    expiresAt: {
      type: DataTypes.DATE,
      allowNull: true
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true
    },
    permissions: {
      type: DataTypes.JSON,
      defaultValue: [],
      allowNull: true
    },
    usageCount: {
      type: DataTypes.INTEGER,
      defaultValue: 0
    },
    tags: {
      type: DataTypes.JSON,
      defaultValue: [],
      allowNull: true
    }
  }, {
    indexes: [
      {
        fields: ['service']
      },
      {
        fields: ['user_id']
      },
      {
        fields: ['is_active']
      }
    ]
  });

  // Instance methods
  ApiKey.prototype.isExpired = function() {
    return this.expiresAt && this.expiresAt < new Date();
  };

  ApiKey.prototype.incrementUsage = async function() {
    return this.update({
      usageCount: this.usageCount + 1,
      lastUsedAt: new Date()
    });
  };

  ApiKey.prototype.toSafeJSON = function() {
    const values = this.toJSON();
    // Only show partial key for security
    if (values.keyValue) {
      const key = values.keyValue;
      values.keyValue = key.substring(0, 8) + '...' + key.substring(key.length - 4);
    }
    return values;
  };

  return ApiKey;
};