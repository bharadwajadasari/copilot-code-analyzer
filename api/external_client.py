"""
External API Client
Handles communication with external visualization platforms.
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)

class ExternalAPIClient:
    def __init__(self, api_config: Dict[str, Any]):
        self.endpoint = api_config.get('endpoint', '')
        self.api_key = api_config.get('api_key', '')
        self.timeout = api_config.get('timeout', 30)
        self.retry_attempts = api_config.get('retry_attempts', 3)
        self.retry_delay = 2  # seconds
        
        # Set up session
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CopilotAnalyzer/1.0'
        })
        
        # Add API key to headers if provided
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'X-API-Key': self.api_key
            })
    
    def send_metrics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Send analysis metrics to external platform"""
        if not self.endpoint:
            raise ValueError("API endpoint not configured")
        
        # Prepare payload
        payload = self._prepare_payload(analysis_results)
        
        # Send with retry logic
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Sending metrics to {self.endpoint} (attempt {attempt + 1})")
                
                response = self.session.post(
                    self.endpoint,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    logger.info("Metrics sent successfully")
                    return response.json()
                elif response.status_code == 401:
                    raise ValueError("Authentication failed - check API key")
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    if attempt == self.retry_attempts - 1:
                        response.raise_for_status()
            
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.retry_attempts - 1:
                    raise
            
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    raise
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    raise
            
            # Wait before retry
            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay)
        
        raise Exception("All retry attempts failed")
    
    def send_real_time_update(self, file_path: str, analysis_result: Dict[str, Any]) -> bool:
        """Send real-time file analysis update"""
        if not self.endpoint:
            return False
        
        try:
            payload = {
                'type': 'file_update',
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'analysis': analysis_result
            }
            
            response = self.session.post(
                f"{self.endpoint}/realtime",
                json=payload,
                timeout=10  # Shorter timeout for real-time updates
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.debug(f"Real-time update failed: {e}")
            return False
    
    def send_batch_metrics(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send batch of metrics for multiple repositories"""
        if not self.endpoint:
            raise ValueError("API endpoint not configured")
        
        payload = {
            'type': 'batch_metrics',
            'timestamp': datetime.now().isoformat(),
            'batch_size': len(batch_results),
            'results': batch_results
        }
        
        try:
            response = self.session.post(
                f"{self.endpoint}/batch",
                json=payload,
                timeout=self.timeout * 2  # Longer timeout for batch operations
            )
            
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Batch metrics upload failed: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the external API"""
        if not self.endpoint:
            return {'status': 'error', 'message': 'No endpoint configured'}
        
        try:
            test_payload = {
                'type': 'connection_test',
                'timestamp': datetime.now().isoformat(),
                'client_version': '1.0'
            }
            
            response = self.session.post(
                f"{self.endpoint}/test",
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': 'Connection successful',
                    'response': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
        
        except requests.exceptions.Timeout:
            return {'status': 'error', 'message': 'Connection timeout'}
        
        except requests.exceptions.ConnectionError:
            return {'status': 'error', 'message': 'Connection failed'}
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_dashboard_url(self, repository_id: Optional[str] = None) -> str:
        """Get dashboard URL for viewing metrics"""
        if not self.endpoint:
            return ""
        
        base_url = self.endpoint.replace('/api/', '/dashboard/')
        if repository_id:
            return f"{base_url}/repository/{repository_id}"
        return base_url
    
    def _prepare_payload(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare payload for API submission"""
        summary = analysis_results.get('summary', {})
        
        payload = {
            'timestamp': datetime.now().isoformat(),
            'repository_path': analysis_results.get('repository_path', ''),
            'analysis_timestamp': analysis_results.get('timestamp', ''),
            'metrics': {
                'total_files': summary.get('total_files', 0),
                'total_lines': summary.get('total_lines', 0),
                'copilot_lines': summary.get('copilot_lines', 0),
                'human_lines': summary.get('human_lines', 0),
                'copilot_percentage': summary.get('copilot_percentage', 0),
                'human_percentage': summary.get('human_percentage', 0),
                'average_confidence': summary.get('average_confidence', 0)
            },
            'language_breakdown': analysis_results.get('language_breakdown', {}),
            'git_info': analysis_results.get('git_info', {}),
            'metadata': {
                'client_version': '1.0',
                'analysis_tool': 'CopilotAnalyzer'
            }
        }
        
        # Add file-level data (limited to avoid large payloads)
        files_data = analysis_results.get('files', {})
        if files_data:
            # Send summary of top files by confidence
            file_summaries = []
            for file_path, file_data in files_data.items():
                file_summaries.append({
                    'path': file_path,
                    'language': file_data.get('language', 'Unknown'),
                    'copilot_confidence': file_data.get('copilot_confidence', 0),
                    'code_lines': file_data.get('code_lines', 0),
                    'estimated_copilot_lines': file_data.get('estimated_copilot_lines', 0)
                })
            
            # Sort by confidence and take top 50
            file_summaries.sort(key=lambda x: x['copilot_confidence'], reverse=True)
            payload['top_files'] = file_summaries[:50]
        
        return payload
    
    def register_repository(self, repo_info: Dict[str, Any]) -> str:
        """Register repository with external platform and return repository ID"""
        if not self.endpoint:
            raise ValueError("API endpoint not configured")
        
        payload = {
            'type': 'repository_registration',
            'timestamp': datetime.now().isoformat(),
            'repository': repo_info
        }
        
        try:
            response = self.session.post(
                f"{self.endpoint}/repositories",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get('repository_id', '')
        
        except Exception as e:
            logger.error(f"Repository registration failed: {e}")
            raise
    
    def update_repository_config(self, repo_id: str, config: Dict[str, Any]) -> bool:
        """Update repository configuration on external platform"""
        if not self.endpoint:
            return False
        
        try:
            response = self.session.put(
                f"{self.endpoint}/repositories/{repo_id}/config",
                json=config,
                timeout=self.timeout
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Repository config update failed: {e}")
            return False
