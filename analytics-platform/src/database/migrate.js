const { Pool } = require('pg');
const logger = require('../utils/logger');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

const migrations = [
  // API Keys table
  `CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    permissions JSONB DEFAULT '[]'
  )`,

  // Teams table
  `CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'
  )`,

  // Developers table
  `CREATE TABLE IF NOT EXISTS developers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    team_id INTEGER REFERENCES teams(id),
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
  )`,

  // Projects table
  `CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    team_id INTEGER REFERENCES teams(id),
    repository_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'
  )`,

  // Sessions table
  `CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    developer_id INTEGER REFERENCES developers(id),
    project_id INTEGER REFERENCES projects(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    ide_info JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}'
  )`,

  // Code events table
  `CREATE TABLE IF NOT EXISTS code_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    session_id INTEGER REFERENCES sessions(id),
    developer_id INTEGER REFERENCES developers(id),
    project_id INTEGER REFERENCES projects(id),
    file_path VARCHAR(1000),
    file_extension VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_result JSONB NOT NULL,
    raw_event JSONB NOT NULL
  )`,

  // Analytics cache table
  `CREATE TABLE IF NOT EXISTS analytics_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
  )`,

  // Alerts table
  `CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    alert_type VARCHAR(100) NOT NULL,
    threshold_value NUMERIC,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config JSONB DEFAULT '{}'
  )`,

  // Alert notifications table
  `CREATE TABLE IF NOT EXISTS alert_notifications (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(id),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    data JSONB DEFAULT '{}',
    acknowledged BOOLEAN DEFAULT false
  )`
];

const indexes = [
  'CREATE INDEX IF NOT EXISTS idx_code_events_timestamp ON code_events(timestamp)',
  'CREATE INDEX IF NOT EXISTS idx_code_events_developer ON code_events(developer_id)',
  'CREATE INDEX IF NOT EXISTS idx_code_events_project ON code_events(project_id)',
  'CREATE INDEX IF NOT EXISTS idx_code_events_session ON code_events(session_id)',
  'CREATE INDEX IF NOT EXISTS idx_code_events_file_ext ON code_events(file_extension)',
  'CREATE INDEX IF NOT EXISTS idx_sessions_developer ON sessions(developer_id)',
  'CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_id)',
  'CREATE INDEX IF NOT EXISTS idx_analytics_cache_expires ON analytics_cache(expires_at)',
  'CREATE INDEX IF NOT EXISTS idx_developers_username ON developers(username)',
  'CREATE INDEX IF NOT EXISTS idx_projects_team ON projects(team_id)'
];

async function runMigrations() {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    logger.info('Running database migrations...');
    
    // Create tables
    for (const migration of migrations) {
      await client.query(migration);
      logger.info('Migration executed successfully');
    }
    
    // Create indexes
    for (const index of indexes) {
      await client.query(index);
      logger.info('Index created successfully');
    }
    
    await client.query('COMMIT');
    logger.info('All migrations completed successfully');
    
  } catch (error) {
    await client.query('ROLLBACK');
    logger.error('Migration failed:', error);
    throw error;
  } finally {
    client.release();
  }
}

// Run migrations if this file is executed directly
if (require.main === module) {
  runMigrations()
    .then(() => {
      logger.info('Database migrations completed');
      process.exit(0);
    })
    .catch((error) => {
      logger.error('Migration error:', error);
      process.exit(1);
    });
}

module.exports = { runMigrations };