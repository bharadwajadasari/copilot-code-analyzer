"""
Local Dashboard Web Server
Provides a web interface for viewing analysis results and metrics.
"""

import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_from_directory

from utils.logger import setup_logger

logger = setup_logger(__name__)

class DashboardServer:
    def __init__(self, data_manager, config):
        self.data_manager = data_manager
        self.config = config
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('index.html')
        
        @self.app.route('/api/repositories')
        def get_repositories():
            """Get list of monitored repositories"""
            try:
                repositories = self.data_manager.get_monitored_repositories()
                repo_data = []
                
                for repo_path in repositories:
                    latest = self.data_manager.get_latest_results(repo_path)
                    if latest:
                        summary = latest.get('summary', {})
                        repo_data.append({
                            'path': repo_path,
                            'name': os.path.basename(repo_path),
                            'last_analysis': latest.get('timestamp'),
                            'total_files': summary.get('total_files', 0),
                            'copilot_percentage': summary.get('copilot_percentage', 0),
                            'human_percentage': summary.get('human_percentage', 0)
                        })
                
                return jsonify({
                    'status': 'success',
                    'repositories': repo_data
                })
            
            except Exception as e:
                logger.error(f"Error getting repositories: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/repository/<path:repo_path>/summary')
        def get_repository_summary(repo_path):
            """Get summary for a specific repository"""
            try:
                latest = self.data_manager.get_latest_results(repo_path)
                if not latest:
                    return jsonify({
                        'status': 'error',
                        'message': 'Repository not found'
                    }), 404
                
                return jsonify({
                    'status': 'success',
                    'repository_path': repo_path,
                    'summary': latest.get('summary', {}),
                    'language_breakdown': latest.get('language_breakdown', {}),
                    'git_info': latest.get('git_info', {}),
                    'timestamp': latest.get('timestamp')
                })
            
            except Exception as e:
                logger.error(f"Error getting repository summary: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/repository/<path:repo_path>/history')
        def get_repository_history(repo_path):
            """Get historical data for a repository"""
            try:
                days = request.args.get('days', 30, type=int)
                history = self.data_manager.get_historical_data(repo_path, days)
                
                return jsonify({
                    'status': 'success',
                    'repository_path': repo_path,
                    'history': history,
                    'days': days
                })
            
            except Exception as e:
                logger.error(f"Error getting repository history: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/repository/<path:repo_path>/files')
        def get_repository_files(repo_path):
            """Get file-level analysis for a repository"""
            try:
                latest = self.data_manager.get_latest_results(repo_path)
                if not latest:
                    return jsonify({
                        'status': 'error',
                        'message': 'Repository not found'
                    }), 404
                
                files_data = latest.get('files', {})
                
                # Convert to list format for easier frontend handling
                files_list = []
                for file_path, file_data in files_data.items():
                    files_list.append({
                        'path': file_path,
                        'language': file_data.get('language', 'Unknown'),
                        'code_lines': file_data.get('code_lines', 0),
                        'copilot_confidence': file_data.get('copilot_confidence', 0),
                        'estimated_copilot_lines': file_data.get('estimated_copilot_lines', 0),
                        'estimated_human_lines': file_data.get('estimated_human_lines', 0),
                        'last_modified': file_data.get('last_modified')
                    })
                
                # Sort by copilot confidence (highest first)
                files_list.sort(key=lambda x: x['copilot_confidence'], reverse=True)
                
                return jsonify({
                    'status': 'success',
                    'repository_path': repo_path,
                    'files': files_list,
                    'total_files': len(files_list)
                })
            
            except Exception as e:
                logger.error(f"Error getting repository files: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/file/<path:file_path>/history')
        def get_file_history(file_path):
            """Get analysis history for a specific file"""
            try:
                limit = request.args.get('limit', 10, type=int)
                history = self.data_manager.get_file_history(file_path, limit)
                
                return jsonify({
                    'status': 'success',
                    'file_path': file_path,
                    'history': history
                })
            
            except Exception as e:
                logger.error(f"Error getting file history: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/activity')
        def get_recent_activity():
            """Get recent activity across all repositories"""
            try:
                hours = request.args.get('hours', 24, type=int)
                repositories = self.data_manager.get_monitored_repositories()
                
                all_activity = []
                for repo_path in repositories:
                    activity = self.data_manager.get_recent_file_activity(repo_path, hours)
                    for item in activity:
                        item['repository_path'] = repo_path
                        all_activity.append(item)
                
                # Sort by timestamp (most recent first)
                all_activity.sort(key=lambda x: x['timestamp'], reverse=True)
                
                return jsonify({
                    'status': 'success',
                    'activity': all_activity[:100],  # Limit to 100 items
                    'hours': hours
                })
            
            except Exception as e:
                logger.error(f"Error getting recent activity: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/stats/overview')
        def get_overview_stats():
            """Get overview statistics across all repositories"""
            try:
                repositories = self.data_manager.get_monitored_repositories()
                
                total_stats = {
                    'total_repositories': len(repositories),
                    'total_files': 0,
                    'total_lines': 0,
                    'total_copilot_lines': 0,
                    'total_human_lines': 0,
                    'languages': set(),
                    'last_activity': None
                }
                
                for repo_path in repositories:
                    latest = self.data_manager.get_latest_results(repo_path)
                    if latest:
                        summary = latest.get('summary', {})
                        total_stats['total_files'] += summary.get('total_files', 0)
                        total_stats['total_lines'] += summary.get('total_lines', 0)
                        total_stats['total_copilot_lines'] += summary.get('copilot_lines', 0)
                        total_stats['total_human_lines'] += summary.get('human_lines', 0)
                        
                        # Collect languages
                        language_breakdown = latest.get('language_breakdown', {})
                        total_stats['languages'].update(language_breakdown.keys())
                        
                        # Track latest activity
                        timestamp = latest.get('timestamp')
                        if timestamp and (not total_stats['last_activity'] or timestamp > total_stats['last_activity']):
                            total_stats['last_activity'] = timestamp
                
                # Calculate percentages
                total_code_lines = total_stats['total_copilot_lines'] + total_stats['total_human_lines']
                copilot_percentage = (total_stats['total_copilot_lines'] / total_code_lines * 100) if total_code_lines > 0 else 0
                human_percentage = (total_stats['total_human_lines'] / total_code_lines * 100) if total_code_lines > 0 else 0
                
                total_stats['languages'] = list(total_stats['languages'])
                total_stats['copilot_percentage'] = round(copilot_percentage, 2)
                total_stats['human_percentage'] = round(human_percentage, 2)
                
                return jsonify({
                    'status': 'success',
                    'stats': total_stats
                })
            
            except Exception as e:
                logger.error(f"Error getting overview stats: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/config')
        def get_config():
            """Get current configuration"""
            try:
                # Return safe configuration (without sensitive data)
                safe_config = {
                    'analysis': self.config.get('analysis', {}),
                    'monitoring': self.config.get('monitoring', {}),
                    'dashboard': self.config.get('dashboard', {}),
                    'api': {
                        'enabled': self.config.get('api', {}).get('enabled', False),
                        'endpoint': self.config.get('api', {}).get('endpoint', '')
                    }
                }
                
                return jsonify({
                    'status': 'success',
                    'config': safe_config
                })
            
            except Exception as e:
                logger.error(f"Error getting config: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'status': 'error',
                'message': 'Endpoint not found'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'status': 'error',
                'message': 'Internal server error'
            }), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the dashboard server"""
        logger.info(f"Starting dashboard server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)
