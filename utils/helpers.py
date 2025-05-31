"""
Helper Utilities
Configuration management, validation, and common utility functions.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

from utils.logger import setup_logger

logger = setup_logger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
        ValueError: If config file is empty or invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            raise ValueError(f"Configuration file is empty: {config_path}")
        
        config = json.loads(content)
        
        if not isinstance(config, dict):
            raise ValueError(f"Configuration must be a JSON object: {config_path}")
        
        # Merge with environment variables
        config = merge_environment_config(config)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in config file {config_path}: {e.msg}", e.doc, e.pos)

def merge_environment_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge configuration with environment variables.
    Environment variables take precedence over file configuration.
    
    Args:
        config: Base configuration dictionary
        
    Returns:
        Updated configuration with environment overrides
    """
    # API configuration from environment
    api_config = config.setdefault('api', {})
    
    if os.getenv('API_ENDPOINT'):
        api_config['endpoint'] = os.getenv('API_ENDPOINT')
    
    if os.getenv('API_KEY'):
        api_config['api_key'] = os.getenv('API_KEY')
    
    if os.getenv('API_ENABLED'):
        api_config['enabled'] = os.getenv('API_ENABLED').lower() in ('true', '1', 'yes', 'on')
    
    if os.getenv('API_TIMEOUT'):
        try:
            api_config['timeout'] = int(os.getenv('API_TIMEOUT'))
        except ValueError:
            logger.warning(f"Invalid API_TIMEOUT value: {os.getenv('API_TIMEOUT')}")
    
    # Storage configuration
    storage_config = config.setdefault('storage', {})
    
    if os.getenv('DATA_FILE'):
        storage_config['data_file'] = os.getenv('DATA_FILE')
    
    # Analysis configuration
    analysis_config = config.setdefault('analysis', {})
    
    if os.getenv('SUPPORTED_EXTENSIONS'):
        extensions = [ext.strip() for ext in os.getenv('SUPPORTED_EXTENSIONS').split(',')]
        analysis_config['supported_extensions'] = extensions
    
    # Monitoring configuration
    monitoring_config = config.setdefault('monitoring', {})
    
    if os.getenv('DEBOUNCE_DELAY'):
        try:
            monitoring_config['debounce_delay'] = float(os.getenv('DEBOUNCE_DELAY'))
        except ValueError:
            logger.warning(f"Invalid DEBOUNCE_DELAY value: {os.getenv('DEBOUNCE_DELAY')}")
    
    return config

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Required sections
    required_sections = ['analysis', 'storage']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate analysis configuration
    _validate_analysis_config(config['analysis'])
    
    # Validate storage configuration
    _validate_storage_config(config['storage'])
    
    # Validate API configuration if present
    if 'api' in config:
        _validate_api_config(config['api'])
    
    # Validate monitoring configuration if present
    if 'monitoring' in config:
        _validate_monitoring_config(config['monitoring'])
    
    logger.debug("Configuration validation passed")

def _validate_analysis_config(analysis_config: Dict[str, Any]) -> None:
    """Validate analysis configuration section"""
    required_fields = ['supported_extensions', 'copilot_indicators']
    
    for field in required_fields:
        if field not in analysis_config:
            raise ValueError(f"Missing required analysis configuration field: {field}")
    
    # Validate supported extensions
    extensions = analysis_config['supported_extensions']
    if not isinstance(extensions, list) or not extensions:
        raise ValueError("supported_extensions must be a non-empty list")
    
    for ext in extensions:
        if not isinstance(ext, str) or not ext.startswith('.'):
            raise ValueError(f"Invalid file extension: {ext}")
    
    # Validate copilot indicators
    indicators = analysis_config['copilot_indicators']
    if not isinstance(indicators, dict):
        raise ValueError("copilot_indicators must be a dictionary")
    
    required_indicator_fields = ['comment_patterns', 'high_velocity_threshold']
    for field in required_indicator_fields:
        if field not in indicators:
            raise ValueError(f"Missing required copilot indicator field: {field}")

def _validate_storage_config(storage_config: Dict[str, Any]) -> None:
    """Validate storage configuration section"""
    if 'data_file' not in storage_config:
        raise ValueError("Missing required storage configuration field: data_file")
    
    data_file = storage_config['data_file']
    if not isinstance(data_file, str) or not data_file:
        raise ValueError("data_file must be a non-empty string")

def _validate_api_config(api_config: Dict[str, Any]) -> None:
    """Validate API configuration section"""
    if api_config.get('enabled', False):
        if not api_config.get('endpoint'):
            raise ValueError("API endpoint is required when API is enabled")
        
        endpoint = api_config['endpoint']
        if not isinstance(endpoint, str) or not endpoint.startswith(('http://', 'https://')):
            raise ValueError("API endpoint must be a valid HTTP/HTTPS URL")
    
    # Validate timeout if present
    if 'timeout' in api_config:
        timeout = api_config['timeout']
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("API timeout must be a positive integer")

def _validate_monitoring_config(monitoring_config: Dict[str, Any]) -> None:
    """Validate monitoring configuration section"""
    if 'debounce_delay' in monitoring_config:
        delay = monitoring_config['debounce_delay']
        if not isinstance(delay, (int, float)) or delay < 0:
            raise ValueError("debounce_delay must be a non-negative number")
    
    if 'file_patterns' in monitoring_config:
        patterns = monitoring_config['file_patterns']
        if not isinstance(patterns, list):
            raise ValueError("file_patterns must be a list")

def create_default_config() -> Dict[str, Any]:
    """
    Create a default configuration dictionary.
    
    Returns:
        Default configuration
    """
    return {
        "analysis": {
            "supported_extensions": [".py", ".js", ".java", ".cpp", ".c", ".go", ".rs", ".ts", ".jsx", ".tsx"],
            "ignore_patterns": ["*.min.js", "node_modules/*", "__pycache__/*", ".git/*", "*.pyc", "dist/*", "build/*"],
            "copilot_indicators": {
                "comment_patterns": [
                    "# Copilot suggestion",
                    "// Copilot suggestion", 
                    "# Generated by GitHub Copilot",
                    "// Generated by GitHub Copilot",
                    "/* Copilot */",
                    "# AI-generated",
                    "// AI-generated"
                ],
                "high_velocity_threshold": 100,
                "perfect_syntax_weight": 0.3,
                "common_patterns_weight": 0.4,
                "complexity_threshold": 10
            }
        },
        "storage": {
            "data_file": "analysis_data.db"
        },
        "api": {
            "enabled": False,
            "endpoint": "",
            "api_key": "",
            "timeout": 30,
            "retry_attempts": 3
        },
        "monitoring": {
            "file_patterns": ["*.py", "*.js", "*.java", "*.cpp", "*.c", "*.go", "*.rs", "*.ts", "*.jsx", "*.tsx"],
            "debounce_delay": 2,
            "batch_size": 50
        },
        "dashboard": {
            "refresh_interval": 30,
            "max_recent_files": 100
        }
    }

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the configuration
    """
    config_file = Path(config_path)
    
    # Create directory if it doesn't exist
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, sort_keys=True)
        
        logger.info(f"Configuration saved to {config_path}")
        
    except (OSError, PermissionError) as e:
        raise ValueError(f"Could not save configuration to {config_path}: {e}")

def is_valid_repository_path(path: str) -> bool:
    """
    Check if a path is a valid repository directory.
    
    Args:
        path: Path to check
        
    Returns:
        True if path is a valid repository directory
    """
    if not path:
        return False
    
    repo_path = Path(path)
    
    # Check if path exists and is a directory
    if not repo_path.exists() or not repo_path.is_dir():
        return False
    
    # Check if it's readable
    if not os.access(repo_path, os.R_OK):
        return False
    
    return True

def is_valid_file_path(path: str, supported_extensions: List[str] = None) -> bool:
    """
    Check if a path is a valid code file.
    
    Args:
        path: File path to check
        supported_extensions: List of supported file extensions
        
    Returns:
        True if path is a valid code file
    """
    if not path:
        return False
    
    file_path = Path(path)
    
    # Check if file exists and is readable
    if not file_path.exists() or not file_path.is_file():
        return False
    
    if not os.access(file_path, os.R_OK):
        return False
    
    # Check extension if specified
    if supported_extensions:
        if file_path.suffix not in supported_extensions:
            return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe filesystem usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    
    # Trim whitespace and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed_file'
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_len = 255 - len(ext)
        filename = name[:max_name_len] + ext
    
    return filename

def parse_file_size(size_str: str) -> int:
    """
    Parse a human-readable file size string to bytes.
    
    Args:
        size_str: Size string like "10MB", "5.5GB", etc.
        
    Returns:
        Size in bytes
        
    Raises:
        ValueError: If size string is invalid
    """
    size_str = size_str.strip().upper()
    
    # Extract number and unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    number, unit = match.groups()
    size = float(number)
    
    # Convert to bytes
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    
    if unit in multipliers:
        size *= multipliers[unit]
    elif unit == '':
        # No unit specified, assume bytes
        pass
    else:
        raise ValueError(f"Unknown size unit: {unit}")
    
    return int(size)

def format_file_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)}B"
    else:
        return f"{size:.1f}{units[unit_index]}"

def normalize_path(path: str) -> str:
    """
    Normalize a file path for consistent usage.
    
    Args:
        path: Original path
        
    Returns:
        Normalized path
    """
    # Convert to Path object and resolve
    normalized = Path(path).resolve()
    
    # Convert back to string with forward slashes (platform independent)
    return str(normalized).replace('\\', '/')

def get_relative_path(file_path: str, base_path: str) -> str:
    """
    Get relative path from base path to file path.
    
    Args:
        file_path: Target file path
        base_path: Base directory path
        
    Returns:
        Relative path
    """
    try:
        file_path_obj = Path(file_path).resolve()
        base_path_obj = Path(base_path).resolve()
        
        relative = file_path_obj.relative_to(base_path_obj)
        return str(relative).replace('\\', '/')
    
    except ValueError:
        # Paths are not related, return absolute path
        return normalize_path(file_path)

def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, create it if necessary.
    
    Args:
        directory: Directory path
        
    Raises:
        OSError: If directory cannot be created
    """
    dir_path = Path(directory)
    
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Could not create directory {directory}: {e}")

def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary (non-text).
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first 1024 bytes
            chunk = f.read(1024)
            
        # Check for null bytes (common in binary files)
        if b'\x00' in chunk:
            return True
        
        # Try to decode as UTF-8
        try:
            chunk.decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True
            
    except (OSError, PermissionError):
        return True

def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
    Returns:
        Hexadecimal hash string
        
    Raises:
        ValueError: If algorithm is not supported
        OSError: If file cannot be read
    """
    import hashlib
    
    if algorithm not in ['md5', 'sha1', 'sha256']:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except OSError as e:
        raise OSError(f"Could not read file {file_path}: {e}")

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function calls on exception.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    return bool(url_pattern.match(url))

def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging and logging.
    
    Returns:
        Dictionary with system information
    """
    import platform
    
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'cwd': os.getcwd(),
        'pid': os.getpid()
    }
