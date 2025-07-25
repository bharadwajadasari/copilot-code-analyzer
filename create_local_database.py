#!/usr/bin/env python3
"""
Create Local Database for Dashboard
Simple script to create and initialize SQLite database locally
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_local_database():
    """Create and initialize local SQLite database"""
    
    print("Creating Local Database for Copilot Analysis Dashboard")
    print("=" * 55)
    
    db_path = "analysis_data.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)
    
    # Create new database
    print(f"Creating new database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    try:
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        print("Creating database tables...")
        
        # 1. Analysis results table
        conn.execute("""
            CREATE TABLE analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository_path TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                data JSON NOT NULL,
                summary_data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created analysis_results table")
        
        # 2. File analysis table (for activity tracking)
        conn.execute("""
            CREATE TABLE file_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                repository_path TEXT,
                timestamp DATETIME NOT NULL,
                event_type TEXT DEFAULT 'analysis',
                data JSON NOT NULL,
                copilot_confidence REAL,
                language TEXT,
                code_lines INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created file_analysis table")
        
        # 3. Monitoring status table
        conn.execute("""
            CREATE TABLE monitoring_status (
                repository_path TEXT PRIMARY KEY,
                is_active BOOLEAN DEFAULT 1,
                last_scan DATETIME,
                total_files INTEGER DEFAULT 0,
                last_activity DATETIME,
                config JSON
            )
        """)
        print("✓ Created monitoring_status table")
        
        # 4. Metrics cache table
        conn.execute("""
            CREATE TABLE metrics_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                cache_data JSON NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
        """)
        print("✓ Created metrics_cache table")
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX idx_analysis_repo_time ON analysis_results(repository_path, timestamp)")
        conn.execute("CREATE INDEX idx_file_analysis_time ON file_analysis(timestamp)")
        conn.execute("CREATE INDEX idx_file_analysis_repo ON file_analysis(repository_path)")
        print("✓ Created database indexes")
        
        conn.commit()
        print("✓ Database structure created successfully")
        
        # Verify tables were created
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Created tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        conn.close()
    
    print(f"\n✅ Local database created successfully!")
    print(f"Database file: {os.path.abspath(db_path)}")
    print(f"Size: {os.path.getsize(db_path)} bytes")
    
    return True

def add_sample_data():
    """Add sample data to test the database"""
    
    print("\nAdding sample data for testing...")
    print("-" * 40)
    
    conn = sqlite3.connect("analysis_data.db")
    
    try:
        # Add sample repository
        repo_path = str(Path.cwd())
        
        # Add monitoring status
        conn.execute("""
            INSERT INTO monitoring_status 
            (repository_path, is_active, last_scan, total_files, last_activity, config)
            VALUES (?, 1, ?, ?, ?, ?)
        """, (
            repo_path,
            datetime.now().isoformat(),
            0,
            datetime.now().isoformat(),
            json.dumps({"monitoring_enabled": True})
        ))
        
        # Add sample activity entries
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
            }
        ]
        
        for activity in activities:
            timestamp = (datetime.now() - timedelta(minutes=activity["minutes_ago"])).isoformat()
            
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
                json.dumps({
                    "action": f"file_{activity['event_type']}",
                    "confidence": activity["confidence"],
                    "lines": activity["lines"]
                }),
                activity["confidence"],
                activity["language"],
                activity["lines"]
            ))
        
        conn.commit()
        print(f"✓ Added {len(activities)} sample activity entries")
        
        # Verify data was added
        cursor = conn.execute("SELECT COUNT(*) FROM file_analysis")
        count = cursor.fetchone()[0]
        print(f"✓ Total activity entries: {count}")
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
    finally:
        conn.close()

def verify_database():
    """Verify the database was created correctly"""
    
    print("\nVerifying database...")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect("analysis_data.db")
        
        # Check tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables created: {len(tables)}")
        
        # Check activity data
        cursor = conn.execute("SELECT COUNT(*) FROM file_analysis")
        activity_count = cursor.fetchone()[0]
        print(f"Activity entries: {activity_count}")
        
        # Check monitoring
        cursor = conn.execute("SELECT COUNT(*) FROM monitoring_status")
        monitoring_count = cursor.fetchone()[0]
        print(f"Monitored repositories: {monitoring_count}")
        
        conn.close()
        
        print("✅ Database verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main setup function"""
    
    # Create database
    if not create_local_database():
        return
    
    # Add sample data
    add_sample_data()
    
    # Verify setup
    if verify_database():
        print("\n" + "=" * 55)
        print("LOCAL DASHBOARD DATABASE READY")
        print("=" * 55)
        print("Next steps:")
        print("1. Start the dashboard: python main.py dashboard --port 5000")
        print("2. Open browser to: http://localhost:5000")
        print("3. The activity page will now show sample data")
        print("\nTo add real data, run analysis on your code:")
        print("python main.py analyze -r /path/to/your/project")

if __name__ == "__main__":
    main()