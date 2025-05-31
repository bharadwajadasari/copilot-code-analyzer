const express = require('express');
const AnalyticsService = require('../services/analyticsService');
const authMiddleware = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// GET /api/reports/team-summary - Generate team summary report
router.get('/team-summary', authMiddleware, async (req, res) => {
  try {
    const { timeframe = '30d' } = req.query;
    const analyticsService = new AnalyticsService();
    
    const overview = await analyticsService.getOverview(timeframe);
    const developers = await analyticsService.getDeveloperAnalytics(timeframe, 100);
    const projects = await analyticsService.getProjectAnalytics(timeframe, 100);
    const trends = await analyticsService.getTrends(timeframe, 'daily');
    const languages = await analyticsService.getLanguageAnalytics(timeframe);

    const report = {
      report_type: 'team_summary',
      timeframe,
      generated_at: new Date().toISOString(),
      summary: overview,
      team_metrics: {
        total_developers: developers.length,
        active_developers: overview.active_developers,
        total_projects: projects.length,
        most_active_developer: developers[0]?.username || 'N/A',
        most_active_project: projects[0]?.project_name || 'N/A',
        top_language: languages[0]?.language || 'N/A'
      },
      ai_usage_insights: {
        overall_ai_percentage: overview.ai_usage.ai_percentage,
        high_ai_users: developers.filter(d => parseFloat(d.metrics.ai_usage_percentage) > 70).length,
        projects_with_high_ai: projects.filter(p => parseFloat(p.metrics.ai_usage_percentage) > 70).length
      },
      trends: trends.data,
      detailed_metrics: {
        developers: developers.slice(0, 20),
        projects: projects.slice(0, 20),
        languages
      }
    };

    res.json(report);

  } catch (error) {
    logger.error('Error generating team summary report:', error);
    res.status(500).json({ error: 'Failed to generate team summary report' });
  }
});

// GET /api/reports/developer/:username - Generate individual developer report
router.get('/developer/:username', authMiddleware, async (req, res) => {
  try {
    const { username } = req.params;
    const { timeframe = '30d' } = req.query;
    const analyticsService = new AnalyticsService();
    
    const developers = await analyticsService.getDeveloperAnalytics(timeframe, 1000);
    const developer = developers.find(d => d.username === username);
    
    if (!developer) {
      return res.status(404).json({ error: 'Developer not found' });
    }

    const trends = await analyticsService.getTrends(timeframe, 'daily');
    
    const report = {
      report_type: 'developer_individual',
      developer: username,
      timeframe,
      generated_at: new Date().toISOString(),
      metrics: developer.metrics,
      performance_insights: {
        activity_level: developer.metrics.total_events > 1000 ? 'high' : 
                       developer.metrics.total_events > 100 ? 'medium' : 'low',
        ai_usage_level: parseFloat(developer.metrics.ai_usage_percentage) > 70 ? 'high' :
                       parseFloat(developer.metrics.ai_usage_percentage) > 30 ? 'medium' : 'low',
        project_diversity: developer.metrics.projects_worked
      },
      trends: trends.data
    };

    res.json(report);

  } catch (error) {
    logger.error('Error generating developer report:', error);
    res.status(500).json({ error: 'Failed to generate developer report' });
  }
});

module.exports = router;