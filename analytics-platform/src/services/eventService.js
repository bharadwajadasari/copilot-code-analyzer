const { Pool } = require('pg');
const logger = require('../utils/logger');

class EventService {
  constructor() {
    this.pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
    });
  }

  async processEvents(events, apiKey) {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');
      
      const results = {
        processed: 0,
        errors: [],
        summary: {
          totalEvents: events.length,
          aiConfidenceHigh: 0,
          humanConfidenceHigh: 0,
          newDevelopers: 0,
          newProjects: 0
        }
      };

      for (const event of events) {
        try {
          await this.processEvent(client, event, apiKey);
          results.processed++;
          
          // Update summary stats
          const confidence = event.analysis_result?.copilot_confidence || 0;
          if (confidence > 0.7) results.summary.aiConfidenceHigh++;
          else if (confidence < 0.3) results.summary.humanConfidenceHigh++;
          
        } catch (error) {
          results.errors.push({
            event: event.session_id,
            error: error.message
          });
        }
      }

      await client.query('COMMIT');
      return results;

    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  async processEvent(client, event, apiKey) {
    // Get or create developer
    const developerId = await this.getOrCreateDeveloper(client, event.developer_id);
    
    // Get or create project
    const projectId = await this.getOrCreateProject(client, event.project_name);
    
    // Get or create session
    const sessionId = await this.getOrCreateSession(client, event.session_id, developerId, projectId, event);
    
    // Insert event
    await this.insertEvent(client, event, sessionId, developerId, projectId);
    
    // Update session metrics
    await this.updateSessionMetrics(client, sessionId, event);
  }

  async getOrCreateDeveloper(client, username) {
    const result = await client.query(
      'SELECT id FROM developers WHERE username = $1',
      [username]
    );

    if (result.rows.length > 0) {
      // Update last seen
      await client.query(
        'UPDATE developers SET last_seen = CURRENT_TIMESTAMP WHERE id = $1',
        [result.rows[0].id]
      );
      return result.rows[0].id;
    }

    // Create new developer
    const insertResult = await client.query(
      'INSERT INTO developers (username, first_seen, last_seen) VALUES ($1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) RETURNING id',
      [username]
    );
    
    return insertResult.rows[0].id;
  }

  async getOrCreateProject(client, projectName) {
    const result = await client.query(
      'SELECT id FROM projects WHERE name = $1',
      [projectName]
    );

    if (result.rows.length > 0) {
      return result.rows[0].id;
    }

    // Create new project
    const insertResult = await client.query(
      'INSERT INTO projects (name, created_at) VALUES ($1, CURRENT_TIMESTAMP) RETURNING id',
      [projectName]
    );
    
    return insertResult.rows[0].id;
  }

  async getOrCreateSession(client, sessionId, developerId, projectId, event) {
    const result = await client.query(
      'SELECT id FROM sessions WHERE session_id = $1',
      [sessionId]
    );

    if (result.rows.length > 0) {
      return result.rows[0].id;
    }

    // Create new session
    const ideInfo = {
      ide_name: 'IntelliJ IDEA',
      ide_version: event.ide_version || 'unknown'
    };

    const insertResult = await client.query(
      'INSERT INTO sessions (session_id, developer_id, project_id, started_at, ide_info) VALUES ($1, $2, $3, CURRENT_TIMESTAMP, $4) RETURNING id',
      [sessionId, developerId, projectId, JSON.stringify(ideInfo)]
    );
    
    return insertResult.rows[0].id;
  }

  async insertEvent(client, event, sessionId, developerId, projectId) {
    await client.query(
      `INSERT INTO code_events 
       (event_type, session_id, developer_id, project_id, file_path, file_extension, timestamp, analysis_result, raw_event)
       VALUES ($1, $2, $3, $4, $5, $6, to_timestamp($7/1000), $8, $9)`,
      [
        event.event_type,
        sessionId,
        developerId,
        projectId,
        event.file_path || '',
        event.file_extension || '',
        event.timestamp,
        JSON.stringify(event.analysis_result),
        JSON.stringify(event)
      ]
    );
  }

  async updateSessionMetrics(client, sessionId, event) {
    const confidence = event.analysis_result?.copilot_confidence || 0;
    
    await client.query(
      `UPDATE sessions 
       SET metrics = COALESCE(metrics, '{}') || jsonb_build_object(
         'total_events', COALESCE((metrics->>'total_events')::int, 0) + 1,
         'avg_ai_confidence', CASE 
           WHEN COALESCE((metrics->>'total_events')::int, 0) = 0 THEN $2
           ELSE (COALESCE((metrics->>'avg_ai_confidence')::numeric, 0) * COALESCE((metrics->>'total_events')::int, 0) + $2) / (COALESCE((metrics->>'total_events')::int, 0) + 1)
         END,
         'last_activity', $3
       )
       WHERE id = $1`,
      [sessionId, confidence, event.timestamp]
    );
  }

  async getRecentEvents(hours, limit) {
    const result = await this.pool.query(
      `SELECT 
         ce.*,
         d.username as developer_username,
         p.name as project_name,
         s.session_id
       FROM code_events ce
       JOIN developers d ON ce.developer_id = d.id
       JOIN projects p ON ce.project_id = p.id
       JOIN sessions s ON ce.session_id = s.id
       WHERE ce.timestamp >= NOW() - INTERVAL '${hours} hours'
       ORDER BY ce.timestamp DESC
       LIMIT $1`,
      [limit]
    );

    return result.rows;
  }

  async getEventsByDeveloper(developerId, days, limit) {
    const result = await this.pool.query(
      `SELECT 
         ce.*,
         p.name as project_name,
         s.session_id
       FROM code_events ce
       JOIN projects p ON ce.project_id = p.id
       JOIN sessions s ON ce.session_id = s.id
       JOIN developers d ON ce.developer_id = d.id
       WHERE d.username = $1 
         AND ce.timestamp >= NOW() - INTERVAL '${days} days'
       ORDER BY ce.timestamp DESC
       LIMIT $2`,
      [developerId, limit]
    );

    return result.rows;
  }

  async getEventsByProject(projectName, days, limit) {
    const result = await this.pool.query(
      `SELECT 
         ce.*,
         d.username as developer_username,
         s.session_id
       FROM code_events ce
       JOIN developers d ON ce.developer_id = d.id
       JOIN sessions s ON ce.session_id = s.id
       JOIN projects p ON ce.project_id = p.id
       WHERE p.name = $1 
         AND ce.timestamp >= NOW() - INTERVAL '${days} days'
       ORDER BY ce.timestamp DESC
       LIMIT $2`,
      [projectName, limit]
    );

    return result.rows;
  }

  async getEventStats(timeframe) {
    const interval = this.parseTimeframe(timeframe);
    
    const result = await this.pool.query(
      `SELECT 
         COUNT(*) as total_events,
         COUNT(DISTINCT developer_id) as unique_developers,
         COUNT(DISTINCT project_id) as unique_projects,
         COUNT(DISTINCT session_id) as unique_sessions,
         AVG((analysis_result->>'copilot_confidence')::numeric) as avg_ai_confidence,
         COUNT(*) FILTER (WHERE (analysis_result->>'copilot_confidence')::numeric > 0.7) as high_ai_confidence,
         COUNT(*) FILTER (WHERE (analysis_result->>'copilot_confidence')::numeric < 0.3) as high_human_confidence
       FROM code_events
       WHERE timestamp >= NOW() - INTERVAL '${interval}'`
    );

    return result.rows[0];
  }

  parseTimeframe(timeframe) {
    const timeframeMap = {
      '1h': '1 hour',
      '24h': '24 hours',
      '7d': '7 days',
      '30d': '30 days'
    };
    
    return timeframeMap[timeframe] || '24 hours';
  }
}

module.exports = EventService;