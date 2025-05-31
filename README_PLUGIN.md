# Copilot Code Analyzer - IntelliJ IDEA Plugin

## Overview
This IntelliJ IDEA plugin continuously monitors code changes in real-time, analyzes AI vs human-written patterns, and publishes events to external analytics platforms.

## Features

### Real-time Monitoring
- **Continuous Code Analysis**: Monitors every keystroke and code change
- **Debounced Processing**: Waits 2 seconds after changes to avoid excessive analysis
- **Background Processing**: Non-intrusive analysis that doesn't affect IDE performance

### Analysis Engine
- **Pattern Detection**: Identifies AI-generated vs human-written code patterns
- **Multi-language Support**: Java, Kotlin, Python, JavaScript, TypeScript, C++, and more
- **Confidence Scoring**: Provides 0-100% confidence scores for AI detection

### Event Publishing
- **External API Integration**: Sends analysis events to your analytics platform
- **Batch Processing**: Efficiently batches events for optimal network usage
- **Retry Mechanism**: Handles network failures with exponential backoff

## Installation

### Building the Plugin
```bash
# Clone the repository
git clone https://github.com/bharadwajadasari/copilot-code-analyzer.git
cd copilot-code-analyzer

# Build the plugin
./gradlew buildPlugin

# The plugin JAR will be in build/distributions/
```

### Installing in IntelliJ IDEA
1. Open IntelliJ IDEA
2. Go to File → Settings → Plugins
3. Click the gear icon → Install Plugin from Disk
4. Select the built JAR file
5. Restart IntelliJ IDEA

## Configuration

### Plugin Settings
Access through: File → Settings → Tools → Copilot Code Analyzer

- **External API Endpoint**: Your analytics platform URL
- **API Key**: Authentication token for your platform
- **Batch Size**: Number of events to batch before sending
- **Analysis Interval**: Milliseconds to wait after code changes

### Example Configuration
```
API Endpoint: https://your-analytics-platform.com/api/events
API Key: your_secret_api_key_here
Batch Size: 10
Analysis Interval: 2000
```

## Usage

### Automatic Monitoring
Once configured, the plugin automatically:
1. Detects when you type or modify code
2. Waits for a pause in typing (2 seconds)
3. Analyzes the code for AI vs human patterns
4. Sends events to your external platform

### Manual Controls
- **Toggle Monitoring**: Use toolbar button or Tools menu
- **Analyze Current File**: Tools → Copilot Analyzer → Analyze Current File
- **View Statistics**: Tools → Copilot Analyzer → View Statistics

## Event Data Structure

### Real-time Code Change Events
```json
{
  "timestamp": 1685123456789,
  "event_type": "code_change",
  "project_name": "MyProject",
  "file_path": "/src/main/java/MyClass.java",
  "analysis_result": {
    "copilot_confidence": 0.75,
    "human_confidence": 0.25,
    "risk_level": "high",
    "indicators": {
      "explicit_ai_comments": true,
      "perfect_syntax": true,
      "structured_patterns": true
    }
  },
  "developer_id": "john.doe",
  "session_id": "1685123456789-john.doe-MyProject"
}
```

### Session Events
```json
{
  "timestamp": 1685123456789,
  "event_type": "session_started",
  "project_name": "MyProject",
  "developer_id": "john.doe",
  "ide_info": {
    "ide_name": "IntelliJ IDEA",
    "ide_version": "2023.1.2"
  }
}
```

## Analytics Platform Integration

### Webhook Endpoint Requirements
Your external analytics platform should provide a webhook endpoint that:
- Accepts POST requests with JSON payload
- Supports Bearer token authentication
- Returns 200 status for successful processing

### Example Server Implementation
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/events', methods=['POST'])
def receive_events():
    # Verify API key
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Invalid authorization'}), 401
    
    # Process events
    events = request.json.get('events', [])
    for event in events:
        # Store in database, trigger alerts, etc.
        process_event(event)
    
    return jsonify({'success': True, 'processed': len(events)})
```

## Troubleshooting

### Plugin Not Monitoring
1. Check if monitoring is enabled in toolbar
2. Verify API endpoint and key in settings
3. Check IDE logs for errors

### Events Not Reaching Platform
1. Verify network connectivity
2. Check API endpoint URL format
3. Validate API key permissions
4. Monitor IDE console for error messages

### Performance Issues
1. Increase analysis interval in settings
2. Reduce batch size if needed
3. Check for network latency to analytics platform

## Development

### Building from Source
```bash
./gradlew clean build
./gradlew runIde  # Test in development environment
```

### Testing
```bash
./gradlew test
./gradlew verifyPlugin
```

## Support
For issues and questions, please visit the GitHub repository or contact support.