const express = require('express');
const AnalyticsService = require('../services/analyticsService');
const authMiddleware = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// GET /api/dashboard/summary - Dashboard summary data
router.get('/summary', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '24h' } = req.query;
    const analyticsService = new AnalyticsService();
    
    const overview = await analyticsService.getOverview(timeframe);
    const topDevelopers = await analyticsService.getDeveloperAnalytics(timeframe, 5);
    const topProjects = await analyticsService.getProjectAnalytics(timeframe, 5);
    const languages = await analyticsService.getLanguageAnalytics(timeframe);

    res.json({
      overview,
      top_developers: topDevelopers,
      top_projects: topProjects,
      languages: languages.slice(0, 10),
      generated_at: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Error fetching dashboard summary:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard data' });
  }
});

// GET /api/dashboard/realtime - Real-time statistics
router.get('/realtime', authMiddleware, async (req, res) => {
  try {
    const analyticsService = new AnalyticsService();
    
    const last5Minutes = await analyticsService.getOverview('5m');
    const lastHour = await analyticsService.getOverview('1h');

    res.json({
      last_5_minutes: last5Minutes,
      last_hour: lastHour,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Error fetching realtime data:', error);
    res.status(500).json({ error: 'Failed to fetch realtime data' });
  }
});

module.exports = router;