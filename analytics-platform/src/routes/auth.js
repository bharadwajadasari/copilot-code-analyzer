const express = require('express');
const { Pool } = require('pg');
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcryptjs');
const joi = require('joi');
const logger = require('../utils/logger');

const router = express.Router();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Validation schemas
const createKeySchema = joi.object({
  key_name: joi.string().required().min(3).max(255),
  expires_in_days: joi.number().integer().min(1).max(365).optional(),
  permissions: joi.array().items(joi.string()).optional()
});

// POST /api/auth/keys - Create new API key
router.post('/keys', async (req, res) => {
  try {
    const { error, value } = createKeySchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.details.map(d => d.message)
      });
    }

    const { key_name, expires_in_days, permissions = [] } = value;
    
    // Generate API key
    const apiKey = `ca_${uuidv4().replace(/-/g, '')}`;
    
    // Calculate expiration date if provided
    let expiresAt = null;
    if (expires_in_days) {
      expiresAt = new Date();
      expiresAt.setDate(expiresAt.getDate() + expires_in_days);
    }

    // Insert into database
    const result = await pool.query(
      `INSERT INTO api_keys (key_name, api_key, expires_at, permissions) 
       VALUES ($1, $2, $3, $4) 
       RETURNING id, key_name, api_key, created_at, expires_at`,
      [key_name, apiKey, expiresAt, JSON.stringify(permissions)]
    );

    const keyData = result.rows[0];

    logger.info(`New API key created: ${key_name}`);

    res.status(201).json({
      id: keyData.id,
      key_name: keyData.key_name,
      api_key: keyData.api_key,
      created_at: keyData.created_at,
      expires_at: keyData.expires_at,
      permissions: permissions,
      message: 'API key created successfully. Please store it securely - it will not be shown again.'
    });

  } catch (error) {
    logger.error('Error creating API key:', error);
    res.status(500).json({
      error: 'Failed to create API key',
      message: error.message
    });
  }
});

// GET /api/auth/keys - List API keys (without showing actual keys)
router.get('/keys', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT id, key_name, created_at, expires_at, is_active, permissions
       FROM api_keys 
       ORDER BY created_at DESC`
    );

    const keys = result.rows.map(row => ({
      id: row.id,
      key_name: row.key_name,
      created_at: row.created_at,
      expires_at: row.expires_at,
      is_active: row.is_active,
      permissions: row.permissions,
      status: row.expires_at && new Date() > new Date(row.expires_at) ? 'expired' : 'active'
    }));

    res.json({ keys });

  } catch (error) {
    logger.error('Error fetching API keys:', error);
    res.status(500).json({
      error: 'Failed to fetch API keys',
      message: error.message
    });
  }
});

// DELETE /api/auth/keys/:id - Deactivate API key
router.delete('/keys/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      'UPDATE api_keys SET is_active = false WHERE id = $1 RETURNING key_name',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'API key not found'
      });
    }

    logger.info(`API key deactivated: ${result.rows[0].key_name}`);

    res.json({
      message: 'API key deactivated successfully',
      key_name: result.rows[0].key_name
    });

  } catch (error) {
    logger.error('Error deactivating API key:', error);
    res.status(500).json({
      error: 'Failed to deactivate API key',
      message: error.message
    });
  }
});

module.exports = router;