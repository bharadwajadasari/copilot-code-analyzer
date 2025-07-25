#!/usr/bin/env python3
"""
Simple Database Setup for Local Dashboard
Creates SQLite database with proper schema and sample data
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

def setup_database():
    """Create and initialize SQLite database"""
    
    db_file = "analysis_data.db"
    
    # Remove existing file if it exists
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing {db_file}")
    
    print("Creating new database...")
    
    # Create connection
    conn = sqlite3.connect(db_file)
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create tables
    print("Creating tables...")
    
    # Analysis results table
    conn.execute("""
        CREATE TABLE analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_path TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            data TEXT NOT NULL,
            summary_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # File analysis table (for activity)
    conn.execute("""
        CREATE TABLE file_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            repository_path TEXT,
            timestamp DATETIME NOT NULL,
            event_type TEXT DEFAULT 'analysis',
            data TEXT NOT NULL,
            copilot_confidence REAL,
            language TEXT,
            code_lines INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Monitoring status table
    conn.execute("""
        CREATE TABLE monitoring_status (
            repository_path TEXT PRIMARY KEY,
            is_active BOOLEAN DEFAULT 1,
            last_scan DATETIME,
            total_files INTEGER DEFAULT 0,
            last_activity DATETIME,
            config TEXT
        )
    """)
    
    print("Adding sample data...")
    
    # Add sample activity entries
    now = datetime.now()
    repo_path = "."
    
    activities = [
        {
            "file_path": "analyzer/balanced_detector.py",
            "event_type": "modified",
            "confidence": 0.389,
            "language": "python",
            "lines": 344,
            "minutes_ago": 15
        },
        {
            "file_path": "main.py",
            "event_type": "analyzed", 
            "confidence": 0.125,
            "language": "python",
            "lines": 187,
            "minutes_ago": 30
        },
        {
            "file_path": "dashboard/server.py",
            "event_type": "modified",
            "confidence": 0.067,
            "language": "python", 
            "lines": 280,
            "minutes_ago": 45
        },
        {
            "file_path": "test_balanced_detector_debug.py",
            "event_type": "created",
            "confidence": 0.234,
            "language": "python",
            "lines": 120,
            "minutes_ago": 60
        }
    ]
    
    for activity in activities:
        timestamp = (now - timedelta(minutes=activity["minutes_ago"])).isoformat()
        data = json.dumps({
            "action": f"file_{activity['event_type']}",
            "confidence": activity["confidence"],
            "lines": activity["lines"]
        })
        
        conn.execute("""
            INSERT INTO file_analysis 
            (file_path, repository_path, timestamp, event_type, data, 
             copilot_confidence, language, code_lines)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            activity["file_path"],
            repo_path,
            timestamp,
            activity["event_type"],
            data,
            activity["confidence"],
            activity["language"],
            activity["lines"]
        ))
    
    # Add monitoring status
    conn.execute("""
        INSERT INTO monitoring_status 
        (repository_path, is_active, last_scan, total_files, last_activity, config)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        repo_path,
        1,
        now.isoformat(),
        len(activities),
        now.isoformat(),
        json.dumps({"monitoring_enabled": True})
    ))
    
    # Add sample analysis result
    summary_data = {
        "total_files": len(activities),
        "copilot_lines": sum(int(act["lines"] * act["confidence"]) for act in activities),
        "human_lines": sum(int(act["lines"] * (1 - act["confidence"])) for act in activities),
        "total_lines": sum(act["lines"] for act in activities),
        "copilot_percentage": sum(act["confidence"] for act in activities) / len(activities) * 100
    }
    
    conn.execute("""
        INSERT INTO analysis_results 
        (repository_path, timestamp, data, summary_data)
        VALUES (?, ?, ?, ?)
    """, (
        repo_path,
        now.isoformat(),
        json.dumps({"files_analyzed": len(activities)}),
        json.dumps(summary_data)
    ))
    
    # Commit changes
    conn.commit()
    
    # Verify data
    cursor = conn.execute("SELECT COUNT(*) FROM file_analysis")
    activity_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM analysis_results")
    results_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM monitoring_status")
    monitoring_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Database created successfully!")
    print(f"File: {os.path.abspath(db_file)}")
    print(f"Size: {os.path.getsize(db_file)} bytes")
    print(f"Activity entries: {activity_count}")
    print(f"Analysis results: {results_count}")  
    print(f"Monitored repositories: {monitoring_count}")
    
    return True

if __name__ == "__main__":
    setup_database()
    print("\nNext steps:")
    print("1. Start dashboard: python main.py dashboard --port 5000")
    print("2. Open browser: http://localhost:5000")
    print("3. Check activity page for sample data")