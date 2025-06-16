const router = require('express').Router();
const { Op } = require('sequelize');
const { sequelize, ApiKey } = require('../models');
const { isAuthenticated, requires2FA } = require('../middleware/auth');
const { AppError } = require('../middleware/errorHandler');
const Joi = require('joi');

// Validation schemas
const createKeySchema = Joi.object({
  name: Joi.string().required().min(1).max(100),
  keyValue: Joi.string().required(),
  service: Joi.string().required(),
  description: Joi.string().optional().max(500),
  expiresAt: Joi.date().optional().greater('now'),
  permissions: Joi.array().items(Joi.string()).optional(),
  tags: Joi.array().items(Joi.string()).optional()
});

const updateKeySchema = Joi.object({
  name: Joi.string().optional().min(1).max(100),
  description: Joi.string().optional().max(500),
  expiresAt: Joi.date().optional().allow(null),
  permissions: Joi.array().items(Joi.string()).optional(),
  tags: Joi.array().items(Joi.string()).optional(),
  isActive: Joi.boolean().optional()
});

// Get all API keys for user
router.get('/', isAuthenticated, requires2FA, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const { service, isActive, search, page = 1, limit = 20 } = req.query;
    
    const where = { user_id: userId };
    
    if (service) {
      where.service = service;
    }
    
    if (isActive !== undefined) {
      where.isActive = isActive === 'true';
    }
    
    if (search) {
      where[Op.or] = [
        { name: { [Op.like]: `%${search}%` } },
        { service: { [Op.like]: `%${search}%` } },
        { description: { [Op.like]: `%${search}%` } }
      ];
    }
    
    const offset = (page - 1) * limit;
    
    const { count, rows } = await ApiKey.findAndCountAll({
      where,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['created_at', 'DESC']]
    });
    
    // Use safe JSON method to hide full keys
    const safeKeys = rows.map(key => key.toSafeJSON());
    
    res.json({
      keys: safeKeys,
      pagination: {
        total: count,
        pages: Math.ceil(count / limit),
        currentPage: parseInt(page),
        perPage: parseInt(limit)
      }
    });
  } catch (error) {
    next(error);
  }
});

// Get single API key
router.get('/:id', isAuthenticated, requires2FA, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const { id } = req.params;
    const { reveal } = req.query;
    
    const apiKey = await ApiKey.findOne({
      where: {
        id,
        user_id: userId
      }
    });
    
    if (!apiKey) {
      throw new AppError('API key not found', 404);
    }
    
    // Only reveal full key if explicitly requested
    if (reveal === 'true') {
      // Log this action for security
      console.log(`User ${userId} revealed API key ${id}`);
      res.json({ key: apiKey.toJSON() });
    } else {
      res.json({ key: apiKey.toSafeJSON() });
    }
  } catch (error) {
    next(error);
  }
});

// Create new API key
router.post('/', isAuthenticated, requires2FA, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    
    // Validate input
    const { error, value } = createKeySchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400);
    }
    
    // Create API key
    const apiKey = await ApiKey.create({
      ...value,
      user_id: userId
    });
    
    // Return the full key only on creation
    res.status(201).json({
      key: apiKey.toJSON(),
      message: 'API key created successfully. Please save the key value as it won\'t be shown again.'
    });
  } catch (error) {
    next(error);
  }
});

// Update API key
router.put('/:id', isAuthenticated, requires2FA, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const { id } = req.params;
    
    // Validate input
    const { error, value } = updateKeySchema.validate(req.body);
    if (error) {
      throw new AppError(error.details[0].message, 400);
    }
    
    const apiKey = await ApiKey.findOne({
      where: {
        id,
        user_id: userId
      }
    });
    
    if (!apiKey) {
      throw new AppError('API key not found', 404);
    }
    
    // Update API key
    await apiKey.update(value);
    
    res.json({
      key: apiKey.toSafeJSON(),
      message: 'API key updated successfully'
    });
  } catch (error) {
    next(error);
  }
});

// Delete API key
router.delete('/:id', isAuthenticated, requires2FA, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const { id } = req.params;
    
    const apiKey = await ApiKey.findOne({
      where: {
        id,
        user_id: userId
      }
    });
    
    if (!apiKey) {
      throw new AppError('API key not found', 404);
    }
    
    await apiKey.destroy();
    
    res.json({
      message: 'API key deleted successfully'
    });
  } catch (error) {
    next(error);
  }
});

// Bulk operations
router.post('/bulk-delete', isAuthenticated, requires2FA, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    const { ids } = req.body;
    
    if (!Array.isArray(ids) || ids.length === 0) {
      throw new AppError('Invalid key IDs', 400);
    }
    
    const result = await ApiKey.destroy({
      where: {
        id: ids,
        user_id: userId
      }
    });
    
    res.json({
      message: `${result} API key(s) deleted successfully`
    });
  } catch (error) {
    next(error);
  }
});

// Get statistics
router.get('/stats/overview', isAuthenticated, requires2FA, async (req, res, next) => {
  try {
    const userId = req.user?.id || req.userId;
    
    const [totalKeys, activeKeys, expiredKeys, services] = await Promise.all([
      ApiKey.count({ where: { user_id: userId } }),
      ApiKey.count({ where: { user_id: userId, isActive: true } }),
      ApiKey.count({
        where: {
          user_id: userId,
          expiresAt: { [Op.lt]: new Date() }
        }
      }),
      ApiKey.findAll({
        where: { user_id: userId },
        attributes: [[sequelize.fn('DISTINCT', sequelize.col('service')), 'service']],
        raw: true
      })
    ]);
    
    res.json({
      total: totalKeys,
      active: activeKeys,
      expired: expiredKeys,
      services: services.map(s => s.service)
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;