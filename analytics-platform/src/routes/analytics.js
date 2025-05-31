const express = require('express');
const AnalyticsService = require('../services/analyticsService');
const authMiddleware = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// GET /api/analytics/overview - High-level analytics overview
router.get('/overview', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '7d' } = req.query;
    const analyticsService = new AnalyticsService();
    
    const overview = await analyticsService.getOverview(timeframe);
    
    res.json(overview);
  } catch (error) {
    logger.error('Error fetching analytics overview:', error);
    res.status(500).json({ error: 'Failed to fetch analytics overview' });
  }
});

// GET /api/analytics/developers - Developer analytics
router.get('/developers', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '7d', limit = 50 } = req.query;
    const analyticsService = new AnalyticsService();
    
    const developers = await analyticsService.getDeveloperAnalytics(timeframe, limit);
    
    res.json(developers);
  } catch (error) {
    logger.error('Error fetching developer analytics:', error);
    res.status(500).json({ error: 'Failed to fetch developer analytics' });
  }
});

// GET /api/analytics/projects - Project analytics
router.get('/projects', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '7d', limit = 50 } = req.query;
    const analyticsService = new AnalyticsService();
    
    const projects = await analyticsService.getProjectAnalytics(timeframe, limit);
    
    res.json(projects);
  } catch (error) {
    logger.error('Error fetching project analytics:', error);
    res.status(500).json({ error: 'Failed to fetch project analytics' });
  }
});

// GET /api/analytics/trends - Trend analysis
router.get('/trends', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '30d', granularity = 'daily' } = req.query;
    const analyticsService = new AnalyticsService();
    
    const trends = await analyticsService.getTrends(timeframe, granularity);
    
    res.json(trends);
  } catch (error) {
    logger.error('Error fetching trends:', error);
    res.status(500).json({ error: 'Failed to fetch trends' });
  }
});

// GET /api/analytics/languages - Programming language analytics
router.get('/languages', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '7d' } = req.query;
    const analyticsService = new AnalyticsService();
    
    const languages = await analyticsService.getLanguageAnalytics(timeframe);
    
    res.json(languages);
  } catch (error) {
    logger.error('Error fetching language analytics:', error);
    res.status(500).json({ error: 'Failed to fetch language analytics' });
  }
});

module.exports = router;