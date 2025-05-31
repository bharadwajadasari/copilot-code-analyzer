# Copilot Analytics Platform

A comprehensive external analytics platform that receives events from the IntelliJ Copilot Code Analyzer plugin and provides real-time analytics, reporting, and team insights.

## Features

- **Real-time Event Processing**: Receives and processes code analysis events from IntelliJ plugin
- **Team Analytics**: Track AI usage across developers and projects
- **Trend Analysis**: Historical trends and patterns in AI code generation
- **API Key Management**: Secure authentication system for plugin integration
- **WebSocket Support**: Real-time dashboard updates
- **Comprehensive Reporting**: Team and individual developer reports

## Quick Start

### Prerequisites
- Node.js 16+ 
- PostgreSQL database
- Git

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd analytics-platform
npm install
```

2. **Database Setup**
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env

# Run database migrations
npm run migrate
```

3. **Create API Key**
```bash
# Start the server
npm start

# Create an API key for your IntelliJ plugin
curl -X POST http://localhost:5000/api/auth/keys \
  -H "Content-Type: application/json" \
  -d '{"key_name": "IntelliJ Plugin"}'
```

4. **Configure IntelliJ Plugin**
- Use the API endpoint: `http://localhost:5000/api/events`
- Use the API key from step 3

## API Endpoints

### Authentication
- `POST /api/auth/keys` - Create new API key
- `GET /api/auth/keys` - List API keys
- `DELETE /api/auth/keys/:id` - Deactivate API key

### Events (Plugin Integration)
- `POST /api/events` - Receive events from IntelliJ plugin
- `GET /api/events/recent` - Get recent events
- `GET /api/events/developer/:id` - Get events by developer
- `GET /api/events/project/:name` - Get events by project

### Analytics
- `GET /api/analytics/overview` - High-level analytics overview
- `GET /api/analytics/developers` - Developer analytics
- `GET /api/analytics/projects` - Project analytics
- `GET /api/analytics/trends` - Trend analysis
- `GET /api/analytics/languages` - Programming language analytics

### Dashboard
- `GET /api/dashboard/summary` - Dashboard summary data
- `GET /api/dashboard/realtime` - Real-time statistics

### Reports
- `GET /api/reports/team-summary` - Generate team summary report
- `GET /api/reports/developer/:username` - Individual developer report

## Event Data Structure

The platform expects events in this format from the IntelliJ plugin:

```json
{
  "events": [
    {
      "timestamp": 1685123456789,
      "event_type": "code_change",
      "project_name": "MyProject",
      "file_path": "/src/main/java/MyClass.java",
      "file_extension": "java",
      "analysis_result": {
        "copilot_confidence": 0.75,
        "human_confidence": 0.25,
        "risk_level": "high",
        "indicators": {
          "explicit_ai_comments": true,
          "perfect_syntax": true
        }
      },
      "developer_id": "john.doe",
      "session_id": "unique_session_id"
    }
  ],
  "source": "intellij-plugin",
  "version": "1.0.0"
}
```

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/copilot_analytics
PORT=5000
NODE_ENV=production
LOG_LEVEL=info
```

### Database Schema
The platform automatically creates these tables:
- `api_keys` - API key management
- `developers` - Developer information
- `projects` - Project tracking
- `sessions` - Development sessions
- `code_events` - Individual code analysis events
- `analytics_cache` - Performance optimization

## Real-time Features

### WebSocket Connection
Connect to receive real-time updates:
```javascript
const socket = io('http://localhost:5000');
socket.emit('join-dashboard');
socket.on('new-events', (data) => {
  console.log('New events received:', data);
});
```

## Analytics Examples

### Team Overview
```bash
curl -H "Authorization: Bearer your_api_key" \
  "http://localhost:5000/api/analytics/overview?timeframe=7d"
```

Response:
```json
{
  "total_events": 1250,
  "active_developers": 8,
  "active_projects": 3,
  "ai_usage": {
    "average_confidence": "0.42",
    "ai_percentage": "35.2"
  }
}
```

### Developer Analytics
```bash
curl -H "Authorization: Bearer your_api_key" \
  "http://localhost:5000/api/analytics/developers?timeframe=30d"
```

## Deployment

### Production Setup
```bash
# Set environment to production
export NODE_ENV=production

# Install PM2 for process management
npm install -g pm2

# Start with PM2
pm2 start src/server.js --name copilot-analytics

# Setup SSL/TLS (recommended)
# Configure reverse proxy (nginx/apache)
```

### Docker Deployment
```bash
# Build container
docker build -t copilot-analytics .

# Run with database
docker-compose up -d
```

## Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Logs
```bash
# View logs
tail -f logs/combined.log

# Error logs only
tail -f logs/error.log
```

## Security

- All API endpoints require valid API keys
- Rate limiting prevents abuse
- Input validation on all endpoints
- SQL injection protection
- CORS configuration for web access

## Performance

- Database indexing for fast queries
- Analytics caching for repeated requests
- Batch event processing
- Connection pooling
- Gzip compression

## Support

For issues or questions:
- Check logs in `logs/` directory
- Verify database connectivity
- Confirm API key validity
- Review network configuration for IntelliJ plugin connectivity