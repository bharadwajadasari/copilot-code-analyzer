#!/usr/bin/env python3
"""
Test Local Dashboard Setup
Verify that the local dashboard database has activity data
"""

import sqlite3
import json
from datetime import datetime

def test_local_dashboard():
    """Test the local dashboard database setup"""
    
    print("Testing Local Dashboard Database")
    print("=" * 40)
    
    # Check if database file exists
    try:
        conn = sqlite3.connect("analysis_data.db")
        
        # Test activity data
        print("\n📊 ACTIVITY DATA:")
        print("-" * 30)
        cursor = conn.execute("""
            SELECT file_path, event_type, timestamp, copilot_confidence, language
            FROM file_analysis 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        activities = cursor.fetchall()
        if activities:
            for i, (file_path, event_type, timestamp, confidence, language) in enumerate(activities, 1):
                print(f"{i}. {file_path}")
                print(f"   Event: {event_type} | Confidence: {confidence:.1%} | Language: {language}")
                print(f"   Time: {timestamp}")
                print()
        else:
            print("❌ No activity data found")
        
        # Test analysis results
        print("📈 ANALYSIS RESULTS:")
        print("-" * 30)
        cursor = conn.execute("""
            SELECT repository_path, timestamp, summary_data
            FROM analysis_results 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        if results:
            for i, (repo_path, timestamp, summary_json) in enumerate(results, 1):
                summary = json.loads(summary_json) if summary_json else {}
                print(f"{i}. Repository: {repo_path}")
                print(f"   Time: {timestamp}")
                print(f"   Files: {summary.get('total_files', 0)}")
                print(f"   AI Lines: {summary.get('copilot_lines', 0)}")
                print()
        else:
            print("❌ No analysis results found")
        
        # Test monitoring status
        print("🔍 MONITORING STATUS:")
        print("-" * 30)
        cursor = conn.execute("""
            SELECT repository_path, is_active, last_scan, total_files, last_activity
            FROM monitoring_status
        """)
        
        monitoring = cursor.fetchall()
        if monitoring:
            for repo_path, is_active, last_scan, total_files, last_activity in monitoring:
                status = "Active" if is_active else "Inactive"
                print(f"Repository: {repo_path}")
                print(f"Status: {status}")
                print(f"Files: {total_files}")
                print(f"Last Activity: {last_activity}")
                print()
        else:
            print("❌ No monitoring data found")
        
        conn.close()
        
        print("✅ Database setup verification complete!")
        print("\nThe activity page should now display:")
        print("• Recent file modifications and analyses")
        print("• Confidence scores and risk levels") 
        print("• Timeline of development activity")
        
        print(f"\nTo start the dashboard locally:")
        print("python main.py dashboard --port 5000")
        print("Then visit: http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_local_dashboard()