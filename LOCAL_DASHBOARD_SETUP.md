# Local Dashboard Setup Guide

## How to Create Your Database Locally

**Problem:** When running the dashboard locally, the activity page appears empty because there's no database or activity data.

**Solution:** The local dashboard uses SQLite database (`analysis_data.db`) to store activity data. Here's how to create it:

## Quick Setup Steps

### 1. Create Local Database
```bash
python setup_database.py
```

This creates `analysis_data.db` with:
- Sample analysis results for 4 files
- Activity entries (modified, created, analyzed events)
- Repository monitoring status
- Confidence scores and risk levels

### 2. Start the Dashboard
```bash
python main.py dashboard --port 5000
```

### 3. Access the Dashboard
Open your browser to: `http://localhost:5000`

## What You'll See

### Activity Page Now Shows:
- **Recent file modifications and analyses**
- **Confidence scores and risk levels** 
- **Timeline of development activity**
- **File creation and modification events**

### Sample Activity Data:
1. `analyzer/balanced_detector.py` - Modified (38.9% confidence, HIGH risk)
2. `test_balanced_detector_debug.py` - Created (23.4% confidence, MEDIUM risk)
3. `main.py` - Analyzed (12.5% confidence, LOW risk)
4. `dashboard/server.py` - Modified (6.7% confidence, MINIMAL risk)

## Database Structure

The SQLite database includes these tables:
- `analysis_results` - Repository analysis data
- `file_analysis` - Individual file activity and events
- `monitoring_status` - Repository monitoring configuration

## API Endpoints Working

- `/api/activity` - Recent activity across repositories
- `/api/repositories` - List of monitored repositories
- `/api/repository/{path}/summary` - Repository summary data
- `/api/repository/{path}/files` - File-level analysis results

## Verification

To verify the database is set up correctly:
```bash
python test_local_dashboard.py
```

This shows:
- Activity data entries
- Analysis results
- Monitoring status

## Adding Real Data

To analyze your own code and populate with real data:
```bash
python main.py analyze -r /path/to/your/project
```

This will add actual analysis results to the database, and the activity page will show real file analysis events.

## Troubleshooting

**If activity page is still empty:**
1. Check that `analysis_data.db` exists in your project directory
2. Run the setup script again: `python setup_local_dashboard.py`
3. Verify API endpoint: `curl http://localhost:5000/api/activity`
4. Check browser console for JavaScript errors

**Database location:**
- Replit: Uses PostgreSQL (DATABASE_URL environment variable)
- Local: Uses SQLite file `analysis_data.db` in project root

The setup script ensures your local dashboard has the same functionality as the hosted version, including a fully populated activity page showing development events and AI detection results.