const express = require('express');
const joi = require('joi');
const EventService = require('../services/eventService');
const authMiddleware = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// Event validation schema
const eventSchema = joi.object({
  events: joi.array().items(
    joi.object({
      timestamp: joi.number().required(),
      event_type: joi.string().required(),
      project_name: joi.string().required(),
      file_path: joi.string().allow(''),
      file_name: joi.string().allow(''),
      file_extension: joi.string().allow(''),
      analysis_result: joi.object().required(),
      developer_id: joi.string().required(),
      session_id: joi.string().required(),
      ide_version: joi.string().allow('')
    })
  ).required(),
  timestamp: joi.number().required(),
  source: joi.string().required(),
  version: joi.string().required()
});

// POST /api/events - Receive events from IntelliJ plugin
router.post('/', authMiddleware, async (req, res) => {
  try {
    // Validate request body
    const { error, value } = eventSchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'Invalid event data',
        details: error.details.map(d => d.message)
      });
    }

    const { events } = value;
    const eventService = new EventService();
    
    // Process each event
    const results = await eventService.processEvents(events, req.apiKey);
    
    // Emit real-time updates via WebSocket
    const io = req.app.get('io');
    io.to('dashboard').emit('new-events', {
      count: events.length,
      timestamp: Date.now(),
      summary: results.summary
    });

    logger.info(`Processed ${events.length} events from ${req.apiKey.key_name}`);

    res.json({
      success: true,
      processed: events.length,
      results: results.summary
    });

  } catch (error) {
    logger.error('Event processing error:', error);
    res.status(500).json({
      error: 'Failed to process events',
      message: error.message
    });
  }
});

// GET /api/events/recent - Get recent events
router.get('/recent', authMiddleware, async (req, res) => {
  try {
    const { hours = 24, limit = 100 } = req.query;
    const eventService = new EventService();
    
    const events = await eventService.getRecentEvents(
      parseInt(hours), 
      parseInt(limit)
    );

    res.json({
      events,
      count: events.length,
      timeframe: `${hours} hours`
    });

  } catch (error) {
    logger.error('Error fetching recent events:', error);
    res.status(500).json({
      error: 'Failed to fetch recent events',
      message: error.message
    });
  }
});

// GET /api/events/developer/:developerId - Get events by developer
router.get('/developer/:developerId', authMiddleware, async (req, res) => {
  try {
    const { developerId } = req.params;
    const { days = 7, limit = 100 } = req.query;
    
    const eventService = new EventService();
    const events = await eventService.getEventsByDeveloper(
      developerId, 
      parseInt(days), 
      parseInt(limit)
    );

    res.json({
      developer_id: developerId,
      events,
      count: events.length,
      timeframe: `${days} days`
    });

  } catch (error) {
    logger.error('Error fetching developer events:', error);
    res.status(500).json({
      error: 'Failed to fetch developer events',
      message: error.message
    });
  }
});

// GET /api/events/project/:projectName - Get events by project
router.get('/project/:projectName', authMiddleware, async (req, res) => {
  try {
    const { projectName } = req.params;
    const { days = 7, limit = 100 } = req.query;
    
    const eventService = new EventService();
    const events = await eventService.getEventsByProject(
      projectName, 
      parseInt(days), 
      parseInt(limit)
    );

    res.json({
      project_name: projectName,
      events,
      count: events.length,
      timeframe: `${days} days`
    });

  } catch (error) {
    logger.error('Error fetching project events:', error);
    res.status(500).json({
      error: 'Failed to fetch project events',
      message: error.message
    });
  }
});

// GET /api/events/stats - Get event statistics
router.get('/stats', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '24h' } = req.query;
    const eventService = new EventService();
    
    const stats = await eventService.getEventStats(timeframe);

    res.json(stats);

  } catch (error) {
    logger.error('Error fetching event stats:', error);
    res.status(500).json({
      error: 'Failed to fetch event statistics',
      message: error.message
    });
  }
});

module.exports = router;