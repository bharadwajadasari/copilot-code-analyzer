"""
File System Monitoring
Watches for file changes and triggers real-time analysis.
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Set, List, Union
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeFileHandler(FileSystemEventHandler):
    def __init__(self, analyzer, data_manager, supported_extensions: Set[str], debounce_delay: float = 2.0):
        self.analyzer = analyzer
        self.data_manager = data_manager
        self.supported_extensions = supported_extensions
        self.debounce_delay = debounce_delay
        self.pending_files = {}
        self.lock = threading.Lock()
        
        # Start debounce processor
        self.debounce_thread = threading.Thread(target=self._process_pending_files, daemon=True)
        self.debounce_thread.start()
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self._queue_file_for_analysis(str(event.src_path), 'modified')
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self._queue_file_for_analysis(str(event.src_path), 'created')
    
    def _queue_file_for_analysis(self, file_path: str, event_type: str):
        """Queue a file for analysis with debouncing"""
        file_path_obj = Path(file_path)
        
        # Check if file should be analyzed
        if not self._should_analyze_file(file_path_obj):
            return
        
        with self.lock:
            self.pending_files[file_path] = {
                'timestamp': time.time(),
                'event_type': event_type
            }
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""
        # Check file extension
        if file_path.suffix not in self.supported_extensions:
            return False
        
        # Check if file exists and is readable
        try:
            return file_path.exists() and file_path.is_file() and os.access(file_path, os.R_OK)
        except (OSError, PermissionError):
            return False
    
    def _process_pending_files(self):
        """Process pending files with debouncing"""
        while True:
            try:
                time.sleep(0.5)  # Check every 500ms
                current_time = time.time()
                files_to_process = []
                
                with self.lock:
                    for file_path, file_info in list(self.pending_files.items()):
                        if current_time - file_info['timestamp'] >= self.debounce_delay:
                            files_to_process.append((file_path, file_info))
                            del self.pending_files[file_path]
                
                # Process files outside the lock
                for file_path, file_info in files_to_process:
                    self._analyze_file(file_path, file_info['event_type'])
            
            except Exception as e:
                logger.error(f"Error in debounce processor: {e}")
    
    def _analyze_file(self, file_path: str, event_type: str):
        """Analyze a single file and store results"""
        try:
            logger.info(f"Analyzing {event_type} file: {file_path}")
            
            # Analyze the file
            result = self.analyzer.analyze_file(file_path)
            
            if result:
                # Store the result
                self.data_manager.store_file_analysis(file_path, result, event_type)
                logger.debug(f"Stored analysis result for {file_path}")
            else:
                logger.warning(f"No analysis result for {file_path}")
        
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")

class FileWatcher:
    def __init__(self, repository_path: str, analyzer, data_manager, config: Dict[str, Any] = None):
        self.repository_path = Path(repository_path).resolve()
        self.analyzer = analyzer
        self.data_manager = data_manager
        self.config = config or {}
        
        # Extract configuration
        monitoring_config = self.config.get('monitoring', {})
        self.supported_extensions = set(monitoring_config.get('file_patterns', ['*.py', '*.js']))
        self.debounce_delay = monitoring_config.get('debounce_delay', 2.0)
        
        # Convert file patterns to extensions
        self.supported_extensions = set()
        for pattern in monitoring_config.get('file_patterns', []):
            if pattern.startswith('*.'):
                self.supported_extensions.add(pattern[1:])  # Remove '*'
        
        self.observer = Observer()
        self.event_handler = CodeFileHandler(
            analyzer, data_manager, self.supported_extensions, self.debounce_delay
        )
        
        self.is_running = False
        self.stats = {
            'files_processed': 0,
            'start_time': None,
            'last_activity': None
        }
    
    def start(self):
        """Start monitoring the repository"""
        if self.is_running:
            logger.warning("File watcher is already running")
            return
        
        if not self.repository_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repository_path}")
        
        logger.info(f"Starting file watcher for: {self.repository_path}")
        
        # Schedule the observer
        self.observer.schedule(
            self.event_handler,
            str(self.repository_path),
            recursive=True
        )
        
        # Start the observer
        self.observer.start()
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info("File watcher started successfully")
    
    def stop(self):
        """Stop monitoring the repository"""
        if not self.is_running:
            logger.warning("File watcher is not running")
            return
        
        logger.info("Stopping file watcher...")
        
        self.observer.stop()
        self.observer.join(timeout=5.0)  # Wait up to 5 seconds
        
        self.is_running = False
        logger.info("File watcher stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'repository_path': str(self.repository_path),
            'supported_extensions': list(self.supported_extensions),
            'debounce_delay': self.debounce_delay,
            'stats': self.stats.copy(),
            'pending_files': len(self.event_handler.pending_files) if self.is_running else 0
        }
    
    def get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent file activity from the data manager"""
        try:
            return self.data_manager.get_recent_file_activity(
                str(self.repository_path), 
                hours
            )
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def force_rescan(self):
        """Force a complete rescan of the repository"""
        logger.info(f"Starting force rescan of {self.repository_path}")
        
        try:
            # Analyze the entire repository
            results = self.analyzer.analyze_repository(str(self.repository_path))
            
            # Store results
            self.data_manager.store_analysis_result(str(self.repository_path), results)
            
            logger.info("Force rescan completed successfully")
            return results
        
        except Exception as e:
            logger.error(f"Force rescan failed: {e}")
            raise

class BatchFileProcessor:
    """Process multiple files in batches for efficiency"""
    
    def __init__(self, analyzer, data_manager, batch_size: int = 10):
        self.analyzer = analyzer
        self.data_manager = data_manager
        self.batch_size = batch_size
        self.pending_batch = []
        self.lock = threading.Lock()
        
        # Start batch processor
        self.processor_thread = threading.Thread(target=self._process_batches, daemon=True)
        self.processor_thread.start()
    
    def add_file(self, file_path: str, event_type: str):
        """Add a file to the batch for processing"""
        with self.lock:
            self.pending_batch.append({
                'file_path': file_path,
                'event_type': event_type,
                'timestamp': time.time()
            })
    
    def _process_batches(self):
        """Process files in batches"""
        while True:
            try:
                time.sleep(1.0)  # Check every second
                
                batch_to_process = []
                with self.lock:
                    if len(self.pending_batch) >= self.batch_size:
                        batch_to_process = self.pending_batch[:self.batch_size]
                        self.pending_batch = self.pending_batch[self.batch_size:]
                
                if batch_to_process:
                    self._process_file_batch(batch_to_process)
            
            except Exception as e:
                logger.error(f"Error in batch processor: {e}")
    
    def _process_file_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of files"""
        logger.info(f"Processing batch of {len(batch)} files")
        
        results = []
        for file_info in batch:
            try:
                result = self.analyzer.analyze_file(file_info['file_path'])
                if result:
                    results.append({
                        'file_path': file_info['file_path'],
                        'result': result,
                        'event_type': file_info['event_type']
                    })
            except Exception as e:
                logger.error(f"Error processing file {file_info['file_path']}: {e}")
        
        # Store batch results
        if results:
            self.data_manager.store_batch_results(results)
