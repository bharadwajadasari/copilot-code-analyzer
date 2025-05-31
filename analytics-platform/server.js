const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: false
});

// Create API key endpoint
app.post('/api/auth/keys', async (req, res) => {
  try {
    const { key_name = 'IntelliJ Plugin' } = req.body;
    const apiKey = `ca_${Math.random().toString(36).substr(2, 32)}`;
    
    const result = await pool.query(
      'INSERT INTO api_keys (key_name, api_key) VALUES ($1, $2) RETURNING *',
      [key_name, apiKey]
    );
    
    console.log(`Created API key: ${apiKey} for ${key_name}`);
    res.json({ 
      success: true, 
      api_key: apiKey, 
      key_name,
      message: 'Use this API key in your IntelliJ plugin configuration'
    });
  } catch (error) {
    console.error('Error creating API key:', error);
    res.status(500).json({ error: error.message });
  }
});

// Receive events from IntelliJ plugin
app.post('/api/events', async (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'API key required in Authorization header' });
    }

    const apiKey = authHeader.substring(7);
    
    // Verify API key
    const keyResult = await pool.query(
      'SELECT * FROM api_keys WHERE api_key = $1 AND is_active = true',
      [apiKey]
    );

    if (keyResult.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid API key' });
    }

    const { events } = req.body;
    console.log(`Received ${events?.length || 0} events from IntelliJ plugin`);
    
    // Process each event
    for (const event of events || []) {
      console.log(`Event: ${event.event_type} | File: ${event.file_path} | AI Confidence: ${event.analysis_result?.copilot_confidence}`);
      
      // Store in database (simplified)
      await pool.query(
        `INSERT INTO code_events (event_type, file_path, file_extension, timestamp, analysis_result, raw_event)
         VALUES ($1, $2, $3, CURRENT_TIMESTAMP, $4, $5)`,
        [
          event.event_type,
          event.file_path || '',
          event.file_extension || '',
          JSON.stringify(event.analysis_result),
          JSON.stringify(event)
        ]
      );
    }

    res.json({ 
      success: true, 
      processed: events?.length || 0,
      message: 'Events processed successfully'
    });

  } catch (error) {
    console.error('Error processing events:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get analytics overview
app.get('/api/analytics/overview', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        COUNT(*) as total_events,
        AVG((analysis_result->>'copilot_confidence')::numeric) as avg_ai_confidence,
        COUNT(*) FILTER (WHERE (analysis_result->>'copilot_confidence')::numeric > 0.7) as high_ai_events,
        COUNT(DISTINCT file_extension) as file_types
      FROM code_events 
      WHERE timestamp >= NOW() - INTERVAL '24 hours'
    `);

    const stats = result.rows[0];
    res.json({
      total_events: parseInt(stats.total_events),
      avg_ai_confidence: parseFloat(stats.avg_ai_confidence || 0).toFixed(2),
      high_ai_events: parseInt(stats.high_ai_events),
      file_types: parseInt(stats.file_types),
      ai_percentage: stats.total_events > 0 ? 
        ((stats.high_ai_events / stats.total_events) * 100).toFixed(1) : 0
    });

  } catch (error) {
    console.error('Error fetching analytics:', error);
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'Copilot Analytics Platform running', 
    port: 3000,
    endpoints: {
      create_api_key: 'POST /api/auth/keys',
      receive_events: 'POST /api/events',
      analytics: 'GET /api/analytics/overview'
    }
  });
});

app.listen(3000, '0.0.0.0', () => {
  console.log('Copilot Analytics Platform running on port 3000');
  console.log('Ready to receive events from IntelliJ plugin');
});