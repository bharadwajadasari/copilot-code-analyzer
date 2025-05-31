const logger = require('../utils/logger');

const errorHandler = (err, req, res, next) => {
  logger.error('Error occurred:', {
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip
  });

  // Default error response
  let status = 500;
  let message = 'Internal server error';

  // Handle specific error types
  if (err.name === 'ValidationError') {
    status = 400;
    message = 'Validation failed';
  } else if (err.name === 'UnauthorizedError') {
    status = 401;
    message = 'Unauthorized';
  } else if (err.code === '23505') { // PostgreSQL unique violation
    status = 409;
    message = 'Resource already exists';
  }

  res.status(status).json({
    error: message,
    timestamp: new Date().toISOString(),
    path: req.path
  });
};

module.exports = errorHandler;