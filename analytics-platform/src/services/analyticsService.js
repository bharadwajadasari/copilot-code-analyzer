const { Pool } = require('pg');
const logger = require('../utils/logger');

class AnalyticsService {
  constructor() {
    this.pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
    });
  }

  async getOverview(timeframe) {
    const interval = this.parseTimeframe(timeframe);
    
    const result = await this.pool.query(
      `SELECT 
         COUNT(*) as total_events,
         COUNT(DISTINCT developer_id) as active_developers,
         COUNT(DISTINCT project_id) as active_projects,
         COUNT(DISTINCT session_id) as total_sessions,
         AVG((analysis_result->>'copilot_confidence')::numeric) as avg_ai_confidence,
         COUNT(*) FILTER (WHERE (analysis_result->>'copilot_confidence')::numeric > 0.7) as high_ai_events,
         COUNT(*) FILTER (WHERE (analysis_result->>'copilot_confidence')::numeric < 0.3) as high_human_events,
         COUNT(*) FILTER (WHERE event_type = 'code_change') as code_changes,
         COUNT(*) FILTER (WHERE event_type = 'session_started') as new_sessions
       FROM code_events
       WHERE timestamp >= NOW() - INTERVAL '${interval}'`
    );

    const stats = result.rows[0];
    
    return {
      timeframe,
      total_events: parseInt(stats.total_events),
      active_developers: parseInt(stats.active_developers),
      active_projects: parseInt(stats.active_projects),
      total_sessions: parseInt(stats.total_sessions),
      ai_usage: {
        average_confidence: parseFloat(stats.avg_ai_confidence || 0).toFixed(2),
        high_ai_events: parseInt(stats.high_ai_events),
        high_human_events: parseInt(stats.high_human_events),
        ai_percentage: stats.total_events > 0 ? 
          ((stats.high_ai_events / stats.total_events) * 100).toFixed(1) : 0
      },
      activity: {
        code_changes: parseInt(stats.code_changes),
        new_sessions: parseInt(stats.new_sessions)
      }
    };
  }

  async getDeveloperAnalytics(timeframe, limit) {
    const interval = this.parseTimeframe(timeframe);
    
    const result = await this.pool.query(
      `SELECT 
         d.username,
         d.first_seen,
         d.last_seen,
         COUNT(ce.id) as total_events,
         COUNT(DISTINCT ce.project_id) as projects_worked,
         COUNT(DISTINCT ce.session_id) as sessions,
         AVG((ce.analysis_result->>'copilot_confidence')::numeric) as avg_ai_confidence,
         COUNT(*) FILTER (WHERE (ce.analysis_result->>'copilot_confidence')::numeric > 0.7) as high_ai_events,
         COUNT(*) FILTER (WHERE (ce.analysis_result->>'copilot_confidence')::numeric < 0.3) as high_human_events
       FROM developers d
       LEFT JOIN code_events ce ON d.id = ce.developer_id 
         AND ce.timestamp >= NOW() - INTERVAL '${interval}'
       GROUP BY d.id, d.username, d.first_seen, d.last_seen
       HAVING COUNT(ce.id) > 0
       ORDER BY COUNT(ce.id) DESC
       LIMIT $1`,
      [limit]
    );

    return result.rows.map(row => ({
      username: row.username,
      first_seen: row.first_seen,
      last_seen: row.last_seen,
      metrics: {
        total_events: parseInt(row.total_events),
        projects_worked: parseInt(row.projects_worked),
        sessions: parseInt(row.sessions),
        avg_ai_confidence: parseFloat(row.avg_ai_confidence || 0).toFixed(2),
        high_ai_events: parseInt(row.high_ai_events),
        high_human_events: parseInt(row.high_human_events),
        ai_usage_percentage: row.total_events > 0 ? 
          ((row.high_ai_events / row.total_events) * 100).toFixed(1) : 0
      }
    }));
  }

  async getProjectAnalytics(timeframe, limit) {
    const interval = this.parseTimeframe(timeframe);
    
    const result = await this.pool.query(
      `SELECT 
         p.name as project_name,
         p.created_at,
         COUNT(ce.id) as total_events,
         COUNT(DISTINCT ce.developer_id) as contributors,
         COUNT(DISTINCT ce.session_id) as sessions,
         AVG((ce.analysis_result->>'copilot_confidence')::numeric) as avg_ai_confidence,
         COUNT(*) FILTER (WHERE (ce.analysis_result->>'copilot_confidence')::numeric > 0.7) as high_ai_events,
         COUNT(DISTINCT ce.file_extension) as file_types,
         COUNT(DISTINCT ce.file_path) as unique_files
       FROM projects p
       LEFT JOIN code_events ce ON p.id = ce.project_id 
         AND ce.timestamp >= NOW() - INTERVAL '${interval}'
       GROUP BY p.id, p.name, p.created_at
       HAVING COUNT(ce.id) > 0
       ORDER BY COUNT(ce.id) DESC
       LIMIT $1`,
      [limit]
    );

    return result.rows.map(row => ({
      project_name: row.project_name,
      created_at: row.created_at,
      metrics: {
        total_events: parseInt(row.total_events),
        contributors: parseInt(row.contributors),
        sessions: parseInt(row.sessions),
        avg_ai_confidence: parseFloat(row.avg_ai_confidence || 0).toFixed(2),
        high_ai_events: parseInt(row.high_ai_events),
        file_types: parseInt(row.file_types),
        unique_files: parseInt(row.unique_files),
        ai_usage_percentage: row.total_events > 0 ? 
          ((row.high_ai_events / row.total_events) * 100).toFixed(1) : 0
      }
    }));
  }

  async getTrends(timeframe, granularity) {
    const interval = this.parseTimeframe(timeframe);
    const groupBy = granularity === 'hourly' ? 'hour' : 'day';
    
    const result = await this.pool.query(
      `SELECT 
         date_trunc('${groupBy}', timestamp) as period,
         COUNT(*) as events,
         COUNT(DISTINCT developer_id) as active_developers,
         COUNT(DISTINCT project_id) as active_projects,
         AVG((analysis_result->>'copilot_confidence')::numeric) as avg_ai_confidence,
         COUNT(*) FILTER (WHERE (analysis_result->>'copilot_confidence')::numeric > 0.7) as high_ai_events
       FROM code_events
       WHERE timestamp >= NOW() - INTERVAL '${interval}'
       GROUP BY date_trunc('${groupBy}', timestamp)
       ORDER BY period`
    );

    return {
      timeframe,
      granularity,
      data: result.rows.map(row => ({
        period: row.period,
        events: parseInt(row.events),
        active_developers: parseInt(row.active_developers),
        active_projects: parseInt(row.active_projects),
        avg_ai_confidence: parseFloat(row.avg_ai_confidence || 0).toFixed(2),
        high_ai_events: parseInt(row.high_ai_events),
        ai_percentage: row.events > 0 ? 
          ((row.high_ai_events / row.events) * 100).toFixed(1) : 0
      }))
    };
  }

  async getLanguageAnalytics(timeframe) {
    const interval = this.parseTimeframe(timeframe);
    
    const result = await this.pool.query(
      `SELECT 
         file_extension,
         COUNT(*) as events,
         COUNT(DISTINCT developer_id) as developers,
         COUNT(DISTINCT project_id) as projects,
         AVG((analysis_result->>'copilot_confidence')::numeric) as avg_ai_confidence,
         COUNT(*) FILTER (WHERE (analysis_result->>'copilot_confidence')::numeric > 0.7) as high_ai_events
       FROM code_events
       WHERE timestamp >= NOW() - INTERVAL '${interval}'
         AND file_extension IS NOT NULL 
         AND file_extension != ''
       GROUP BY file_extension
       ORDER BY COUNT(*) DESC`
    );

    return result.rows.map(row => ({
      language: this.mapExtensionToLanguage(row.file_extension),
      file_extension: row.file_extension,
      metrics: {
        events: parseInt(row.events),
        developers: parseInt(row.developers),
        projects: parseInt(row.projects),
        avg_ai_confidence: parseFloat(row.avg_ai_confidence || 0).toFixed(2),
        high_ai_events: parseInt(row.high_ai_events),
        ai_usage_percentage: row.events > 0 ? 
          ((row.high_ai_events / row.events) * 100).toFixed(1) : 0
      }
    }));
  }

  parseTimeframe(timeframe) {
    const timeframeMap = {
      '1h': '1 hour',
      '24h': '24 hours',
      '7d': '7 days',
      '30d': '30 days',
      '90d': '90 days'
    };
    
    return timeframeMap[timeframe] || '7 days';
  }

  mapExtensionToLanguage(extension) {
    const languageMap = {
      'js': 'JavaScript',
      'ts': 'TypeScript',
      'py': 'Python',
      'java': 'Java',
      'kt': 'Kotlin',
      'cpp': 'C++',
      'c': 'C',
      'cs': 'C#',
      'go': 'Go',
      'rs': 'Rust',
      'php': 'PHP',
      'rb': 'Ruby',
      'swift': 'Swift',
      'html': 'HTML',
      'css': 'CSS',
      'sql': 'SQL'
    };
    
    return languageMap[extension] || extension.toUpperCase();
  }
}

module.exports = AnalyticsService;