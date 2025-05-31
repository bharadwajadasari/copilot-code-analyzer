const { Pool } = require('pg');
const logger = require('../utils/logger');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

const authMiddleware = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'Authorization header required',
        message: 'Please provide a valid API key in the Authorization header'
      });
    }

    const apiKey = authHeader.substring(7); // Remove 'Bearer ' prefix
    
    // Validate API key in database
    const result = await pool.query(
      'SELECT * FROM api_keys WHERE api_key = $1 AND is_active = true AND (expires_at IS NULL OR expires_at > NOW())',
      [apiKey]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({
        error: 'Invalid API key',
        message: 'The provided API key is invalid or expired'
      });
    }

    const keyData = result.rows[0];
    
    // Attach API key info to request
    req.apiKey = keyData;
    req.keyName = keyData.key_name;
    
    next();
    
  } catch (error) {
    logger.error('Authentication error:', error);
    res.status(500).json({
      error: 'Authentication failed',
      message: 'Internal server error during authentication'
    });
  }
};

module.exports = authMiddleware;