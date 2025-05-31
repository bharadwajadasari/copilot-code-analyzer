"""
Data Management and Persistence
Handles local storage of analysis results and metrics.
"""

import json
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataManager:
    def __init__(self, db_path: str = "analysis_data.db"):
        self.db_path = Path(db_path)
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Analysis results table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repository_path TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        data JSON NOT NULL,
                        summary_data JSON,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # File analysis table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_analysis (
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
                
                # Monitoring status table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS monitoring_status (
                        repository_path TEXT PRIMARY KEY,
                        is_active BOOLEAN DEFAULT 1,
                        last_scan DATETIME,
                        total_files INTEGER DEFAULT 0,
                        last_activity DATETIME,
                        config JSON
                    )
                """)
                
                # Metrics cache table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metrics_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cache_key TEXT UNIQUE NOT NULL,
                        data JSON NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME
                    )
                """)
                
                # Create indexes for better performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_analysis_repo_time ON analysis_results(repository_path, timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_file_path_time ON file_analysis(file_path, timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_file_repo_time ON file_analysis(repository_path, timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON metrics_cache(cache_key)")
                
                conn.commit()
                logger.info(f"Database initialized: {self.db_path}")
                
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise
            finally:
                conn.close()
    
    def store_analysis_result(self, repository_path: str, results: Dict[str, Any]):
        """Store complete repository analysis results"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                timestamp = results.get('timestamp', datetime.now().isoformat())
                summary_data = results.get('summary', {})
                
                conn.execute("""
                    INSERT INTO analysis_results 
                    (repository_path, timestamp, data, summary_data)
                    VALUES (?, ?, ?, ?)
                """, (
                    repository_path,
                    timestamp,
                    json.dumps(results),
                    json.dumps(summary_data)
                ))
                
                # Update monitoring status
                conn.execute("""
                    INSERT OR REPLACE INTO monitoring_status 
                    (repository_path, last_scan, total_files, last_activity)
                    VALUES (?, ?, ?, ?)
                """, (
                    repository_path,
                    timestamp,
                    summary_data.get('total_files', 0),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                logger.debug(f"Stored analysis result for {repository_path}")
                
            except Exception as e:
                logger.error(f"Failed to store analysis result: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def store_file_analysis(self, file_path: str, result: Dict[str, Any], event_type: str = "analysis"):
        """Store individual file analysis result"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Extract repository path from file path
                repo_path = self._extract_repository_path(file_path)
                
                conn.execute("""
                    INSERT INTO file_analysis 
                    (file_path, repository_path, timestamp, event_type, data, 
                     copilot_confidence, language, code_lines)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_path,
                    repo_path,
                    datetime.now().isoformat(),
                    event_type,
                    json.dumps(result),
                    result.get('copilot_confidence', 0),
                    result.get('language', 'Unknown'),
                    result.get('code_lines', 0)
                ))
                
                # Update last activity
                if repo_path:
                    conn.execute("""
                        UPDATE monitoring_status 
                        SET last_activity = ? 
                        WHERE repository_path = ?
                    """, (datetime.now().isoformat(), repo_path))
                
                conn.commit()
                logger.debug(f"Stored file analysis for {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to store file analysis: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def store_batch_results(self, batch_results: List[Dict[str, Any]]):
        """Store multiple file analysis results in a batch"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                timestamp = datetime.now().isoformat()
                
                for item in batch_results:
                    file_path = item['file_path']
                    result = item['result']
                    event_type = item.get('event_type', 'batch_analysis')
                    repo_path = self._extract_repository_path(file_path)
                    
                    conn.execute("""
                        INSERT INTO file_analysis 
                        (file_path, repository_path, timestamp, event_type, data, 
                         copilot_confidence, language, code_lines)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_path,
                        repo_path,
                        timestamp,
                        event_type,
                        json.dumps(result),
                        result.get('copilot_confidence', 0),
                        result.get('language', 'Unknown'),
                        result.get('code_lines', 0)
                    ))
                
                conn.commit()
                logger.info(f"Stored batch of {len(batch_results)} file analyses")
                
            except Exception as e:
                logger.error(f"Failed to store batch results: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def get_latest_results(self, repository_path: str) -> Optional[Dict[str, Any]]:
        """Get the latest analysis results for a repository"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT data FROM analysis_results 
                    WHERE repository_path = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (repository_path,))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
                
            except Exception as e:
                logger.error(f"Failed to get latest results: {e}")
                return None
            finally:
                conn.close()
    
    def get_historical_data(self, repository_path: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical analysis data for a repository"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                since_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor = conn.execute("""
                    SELECT timestamp, summary_data FROM analysis_results 
                    WHERE repository_path = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (repository_path, since_date))
                
                results = []
                for row in cursor:
                    timestamp, summary_json = row
                    summary = json.loads(summary_json) if summary_json else {}
                    results.append({
                        'timestamp': timestamp,
                        'summary': summary
                    })
                
                return results
                
            except Exception as e:
                logger.error(f"Failed to get historical data: {e}")
                return []
            finally:
                conn.close()
    
    def get_monitored_repositories(self) -> List[str]:
        """Get list of repositories being monitored"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT DISTINCT repository_path FROM monitoring_status 
                    WHERE is_active = 1
                """)
                
                return [row[0] for row in cursor.fetchall()]
                
            except Exception as e:
                logger.error(f"Failed to get monitored repositories: {e}")
                return []
            finally:
                conn.close()
    
    def get_recent_file_activity(self, repository_path: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent file activity for a repository"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                
                cursor = conn.execute("""
                    SELECT file_path, timestamp, event_type, copilot_confidence, language, code_lines
                    FROM file_analysis 
                    WHERE repository_path = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, (repository_path, since_time))
                
                results = []
                for row in cursor:
                    file_path, timestamp, event_type, confidence, language, code_lines = row
                    results.append({
                        'file_path': file_path,
                        'timestamp': timestamp,
                        'event_type': event_type,
                        'copilot_confidence': confidence,
                        'language': language,
                        'code_lines': code_lines
                    })
                
                return results
                
            except Exception as e:
                logger.error(f"Failed to get recent file activity: {e}")
                return []
            finally:
                conn.close()
    
    def get_file_history(self, file_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get analysis history for a specific file"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT timestamp, event_type, data 
                    FROM file_analysis 
                    WHERE file_path = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (file_path, limit))
                
                results = []
                for row in cursor:
                    timestamp, event_type, data_json = row
                    data = json.loads(data_json)
                    results.append({
                        'timestamp': timestamp,
                        'event_type': event_type,
                        'analysis': data
                    })
                
                return results
                
            except Exception as e:
                logger.error(f"Failed to get file history: {e}")
                return []
            finally:
                conn.close()
    
    def cache_metrics(self, cache_key: str, data: Dict[str, Any], ttl_hours: int = 1):
        """Cache computed metrics for performance"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
                
                conn.execute("""
                    INSERT OR REPLACE INTO metrics_cache 
                    (cache_key, data, expires_at)
                    VALUES (?, ?, ?)
                """, (cache_key, json.dumps(data), expires_at))
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"Failed to cache metrics: {e}")
            finally:
                conn.close()
    
    def get_cached_metrics(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached metrics if not expired"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT data FROM metrics_cache 
                    WHERE cache_key = ? AND expires_at > ?
                """, (cache_key, datetime.now().isoformat()))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
                
            except Exception as e:
                logger.error(f"Failed to get cached metrics: {e}")
                return None
            finally:
                conn.close()
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old analysis data"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
                
                # Clean old analysis results
                cursor = conn.execute("""
                    DELETE FROM analysis_results 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                results_deleted = cursor.rowcount
                
                # Clean old file analysis
                cursor = conn.execute("""
                    DELETE FROM file_analysis 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                files_deleted = cursor.rowcount
                
                # Clean expired cache
                cursor = conn.execute("""
                    DELETE FROM metrics_cache 
                    WHERE expires_at < ?
                """, (datetime.now().isoformat(),))
                
                cache_deleted = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Cleanup complete: {results_deleted} analysis results, "
                           f"{files_deleted} file analyses, {cache_deleted} cache entries deleted")
                
            except Exception as e:
                logger.error(f"Data cleanup failed: {e}")
                conn.rollback()
            finally:
                conn.close()
    
    def _extract_repository_path(self, file_path: str) -> Optional[str]:
        """Extract repository path from file path (simplified)"""
        # This is a simplified implementation
        # In practice, you might want to look for .git directories
        path = Path(file_path)
        
        # Look for .git directory in parent directories
        for parent in path.parents:
            if (parent / '.git').exists():
                return str(parent)
        
        # Fallback to the directory containing the file
        return str(path.parent) if path.parent != path else None
    
    def get_dashboard_data(self, repository_path: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive data for dashboard display"""
        cache_key = f"dashboard_data_{repository_path or 'all'}"
        cached = self.get_cached_metrics(cache_key)
        
        if cached:
            return cached
        
        # Compute dashboard data
        dashboard_data = {
            'repositories': [],
            'summary': {},
            'recent_activity': [],
            'top_files': []
        }
        
        if repository_path:
            # Single repository data
            latest = self.get_latest_results(repository_path)
            if latest:
                dashboard_data['repositories'] = [latest]
                dashboard_data['summary'] = latest.get('summary', {})
            
            dashboard_data['recent_activity'] = self.get_recent_file_activity(repository_path)
        else:
            # All repositories data
            repos = self.get_monitored_repositories()
            for repo in repos:
                latest = self.get_latest_results(repo)
                if latest:
                    dashboard_data['repositories'].append(latest)
        
        # Cache for 15 minutes
        self.cache_metrics(cache_key, dashboard_data, ttl_hours=0.25)
        
        return dashboard_data
