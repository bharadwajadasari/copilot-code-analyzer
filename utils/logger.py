"""
Logging Configuration and Setup
Provides centralized logging functionality for the application.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(name: str, level: str = None, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting and handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Determine log level
    log_level = _get_log_level(level)
    logger.setLevel(log_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use simple format for console unless debug level
    if log_level <= logging.DEBUG:
        console_handler.setFormatter(detailed_formatter)
    else:
        console_handler.setFormatter(simple_formatter)
    
    logger.addHandler(console_handler)
    
    # File handler (if specified or default)
    if log_file or _should_log_to_file():
        file_path = log_file or _get_default_log_file()
        file_handler = _create_file_handler(file_path, detailed_formatter)
        if file_handler:
            logger.addHandler(file_handler)
    
    # Error file handler for warnings and above
    error_file = _get_error_log_file()
    if error_file:
        error_handler = _create_file_handler(
            error_file, 
            detailed_formatter, 
            level=logging.WARNING
        )
        if error_handler:
            logger.addHandler(error_handler)
    
    logger.debug(f"Logger '{name}' initialized with level {logging.getLevelName(log_level)}")
    return logger

def _get_log_level(level: Optional[str]) -> int:
    """Determine the appropriate log level"""
    # Check environment variable first
    env_level = os.getenv('LOG_LEVEL', '').upper()
    if env_level:
        level = env_level
    
    # Default to INFO if not specified
    if not level:
        level = 'INFO'
    
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    return level_map.get(level.upper(), logging.INFO)

def _should_log_to_file() -> bool:
    """Check if logging to file is enabled"""
    return os.getenv('LOG_TO_FILE', 'true').lower() in ('true', '1', 'yes', 'on')

def _get_default_log_file() -> str:
    """Get the default log file path"""
    log_dir = Path(os.getenv('LOG_DIR', 'logs'))
    log_dir.mkdir(exist_ok=True)
    
    # Use date-based log files
    date_str = datetime.now().strftime('%Y-%m-%d')
    return str(log_dir / f'copilot_analyzer_{date_str}.log')

def _get_error_log_file() -> Optional[str]:
    """Get the error log file path"""
    if not _should_log_to_file():
        return None
    
    log_dir = Path(os.getenv('LOG_DIR', 'logs'))
    log_dir.mkdir(exist_ok=True)
    
    return str(log_dir / 'errors.log')

def _create_file_handler(file_path: str, formatter: logging.Formatter, level: int = None) -> Optional[logging.Handler]:
    """Create a file handler with rotation"""
    try:
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to prevent large log files
        handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        if level:
            handler.setLevel(level)
        
        handler.setFormatter(formatter)
        return handler
        
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not create log file {file_path}: {e}", file=sys.stderr)
        return None

class LoggerMixin:
    """Mixin class to add logging capability to other classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__module__ + '.' + self.__class__.__name__)
        return self._logger

def configure_third_party_loggers():
    """Configure logging for third-party libraries"""
    # Reduce verbosity of external libraries
    external_loggers = [
        'requests',
        'urllib3',
        'git',
        'watchdog',
        'flask'
    ]
    
    for logger_name in external_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)

def setup_application_logging():
    """Set up logging for the entire application"""
    # Configure third-party loggers
    configure_third_party_loggers()
    
    # Set up root logger
    root_logger = setup_logger('copilot_analyzer')
    
    # Add handler for uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        root_logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception
    
    return root_logger

class ContextualLogger:
    """Logger with contextual information"""
    
    def __init__(self, base_logger: logging.Logger, context: dict = None):
        self.base_logger = base_logger
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Format message with context"""
        if not self.context:
            return message
        
        context_str = ', '.join(f"{k}={v}" for k, v in self.context.items())
        return f"[{context_str}] {message}"
    
    def debug(self, message: str, *args, **kwargs):
        self.base_logger.debug(self._format_message(message), *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self.base_logger.info(self._format_message(message), *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self.base_logger.warning(self._format_message(message), *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self.base_logger.error(self._format_message(message), *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self.base_logger.critical(self._format_message(message), *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        self.base_logger.exception(self._format_message(message), *args, **kwargs)
    
    def with_context(self, **context) -> 'ContextualLogger':
        """Create a new logger with additional context"""
        new_context = {**self.context, **context}
        return ContextualLogger(self.base_logger, new_context)

def get_contextual_logger(name: str, **context) -> ContextualLogger:
    """Get a contextual logger with initial context"""
    base_logger = setup_logger(name)
    return ContextualLogger(base_logger, context)

# Performance logging utilities
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: logging.Logger, operation_name: str, log_level: int = logging.INFO):
        self.logger = logger
        self.operation_name = operation_name
        self.log_level = log_level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.log_level, f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = datetime.now() - self.start_time
            duration_ms = duration.total_seconds() * 1000
            
            if exc_type:
                self.logger.error(f"{self.operation_name} failed after {duration_ms:.2f}ms")
            else:
                self.logger.log(self.log_level, f"{self.operation_name} completed in {duration_ms:.2f}ms")

def time_operation(logger: logging.Logger, operation_name: str, log_level: int = logging.INFO):
    """Decorator for timing function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceTimer(logger, f"{operation_name} ({func.__name__})", log_level):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Initialize application logging when module is imported
if __name__ != '__main__':
    setup_application_logging()
