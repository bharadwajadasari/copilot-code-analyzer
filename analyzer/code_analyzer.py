"""
Code Analysis Engine
Analyzes code repositories to detect Copilot vs human-written code patterns.
"""

import os
import ast
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from git import Repo, InvalidGitRepositoryError
from utils.logger import setup_logger
from .balanced_detector import BalancedCopilotDetector
from .evasion_resistant_detector import EvasionResistantDetector
from .optimized_conservative_detector import OptimizedConservativeDetector
from .metrics_calculator import MetricsCalculator

logger = setup_logger(__name__)

class CodeAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.copilot_detector = BalancedCopilotDetector(config['analysis']['copilot_indicators'])
        self.evasion_detector = EvasionResistantDetector(config['analysis']['copilot_indicators'])
        self.optimized_detector = OptimizedConservativeDetector(config['analysis']['copilot_indicators'])
        self.metrics_calculator = MetricsCalculator()
        self.supported_extensions = set(config['analysis']['supported_extensions'])
        self.ignore_patterns = config['analysis']['ignore_patterns']
        self.use_evasion_resistance = config['analysis'].get('evasion_resistance', True)
        self.use_optimized_mode = config['analysis'].get('optimized_mode', True)
        self.max_workers = config['analysis'].get('max_workers', 4)
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze an entire repository for Copilot vs human-written code"""
        logger.info(f"Starting analysis of repository: {repo_path}")
        
        repo_path = Path(repo_path).resolve()
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        # Initialize results structure
        results = {
            'repository_path': str(repo_path),
            'timestamp': datetime.now().isoformat(),
            'files': {},
            'summary': {},
            'language_breakdown': {},
            'git_info': {}
        }
        
        # Get Git information if available
        try:
            repo = Repo(repo_path)
            results['git_info'] = {
                'current_branch': repo.active_branch.name,
                'last_commit': repo.head.commit.hexsha[:8],
                'last_commit_date': repo.head.commit.committed_datetime.isoformat(),
                'total_commits': len(list(repo.iter_commits()))
            }
        except (InvalidGitRepositoryError, Exception) as e:
            logger.warning(f"Could not access Git information: {e}")
            results['git_info'] = {'error': str(e)}
        
        # Find all code files
        code_files = self._find_code_files(repo_path)
        logger.info(f"Found {len(code_files)} code files to analyze")
        
        # Analyze files in optimized parallel batches
        batch_size = self.config['analysis'].get('batch_size', 100)
        total_batches = (len(code_files) + batch_size - 1) // batch_size
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, len(code_files))
                batch_files = code_files[start_idx:end_idx]
                
                if total_batches > 1:
                    logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_files)} files)")
                
                future_to_file = {
                    executor.submit(self._analyze_file, file_path): file_path 
                    for file_path in batch_files
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        file_result = future.result()
                        if file_result:
                            relative_path = str(file_path.relative_to(repo_path))
                            results['files'][relative_path] = file_result
                    except Exception as e:
                        logger.error(f"Error analyzing file {file_path}: {e}")
                
                # Clear cache periodically for memory management
                if hasattr(self.optimized_detector, 'clear_cache') and batch_num % 5 == 0:
                    self.optimized_detector.clear_cache()
        
        # Calculate summary metrics
        results['summary'] = self.metrics_calculator.calculate_repository_summary(results['files'])
        results['language_breakdown'] = self.metrics_calculator.calculate_language_breakdown(results['files'])
        
        logger.info(f"Analysis complete. Processed {len(results['files'])} files")
        return results
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for Copilot vs human-written code"""
        return self._analyze_file(Path(file_path))
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Internal method to analyze a single file"""
        try:
            if not file_path.exists() or file_path.is_dir():
                return None
            
            # Skip if file extension not supported
            if file_path.suffix not in self.supported_extensions:
                return None
            
            # Skip if file matches ignore patterns
            if self._should_ignore_file(file_path):
                return None
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError) as e:
                logger.warning(f"Could not read file {file_path}: {e}")
                return None
            
            if not content.strip():
                return None
            
            # Get file statistics
            file_stats = self._get_file_stats(file_path, content)
            
            # Detect Copilot patterns using appropriate detector
            if self.use_optimized_mode:
                # Use optimized detector for large file sets
                copilot_analysis = self.optimized_detector.analyze_content(content, file_path.suffix)
            elif self.use_evasion_resistance:
                # Use evasion-resistant detector for enhanced detection
                copilot_analysis = self.evasion_detector.analyze_content(content, file_path.suffix)
                # Map to standard format for backward compatibility
                if 'copilot_confidence' in copilot_analysis:
                    copilot_analysis['confidence_score'] = copilot_analysis['copilot_confidence']
                    copilot_analysis['estimated_lines'] = int(
                        file_stats['code_lines'] * copilot_analysis['confidence_score']
                    )
            else:
                # Use standard balanced detector
                copilot_analysis = self.copilot_detector.analyze_content(content, file_path.suffix)
            
            # Combine results
            result = {
                'file_path': str(file_path),
                'language': self._detect_language(file_path.suffix),
                'file_size': file_stats['size'],
                'total_lines': file_stats['total_lines'],
                'code_lines': file_stats['code_lines'],
                'comment_lines': file_stats['comment_lines'],
                'blank_lines': file_stats['blank_lines'],
                'last_modified': file_stats['last_modified'],
                'file_hash': file_stats['file_hash'],
                'copilot_analysis': copilot_analysis,
                'estimated_copilot_lines': copilot_analysis.get('estimated_lines', 0),
                'estimated_human_lines': file_stats['code_lines'] - copilot_analysis.get('estimated_lines', 0),
                'copilot_confidence': copilot_analysis.get('confidence_score', copilot_analysis.get('copilot_confidence', 0)),
                'evasion_resistance': copilot_analysis.get('evasion_resistance', {})
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return None
    
    def _find_code_files(self, repo_path: Path) -> List[Path]:
        """Find all code files in the repository"""
        code_files = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]
            
            root_path = Path(root)
            for file_name in files:
                file_path = root_path / file_name
                
                # Check if file has supported extension
                if file_path.suffix in self.supported_extensions:
                    if not self._should_ignore_file(file_path):
                        code_files.append(file_path)
        
        return code_files
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns"""
        file_str = str(file_path)
        
        for pattern in self.ignore_patterns:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            if re.search(regex_pattern, file_str):
                return True
        
        return False
    
    def _get_file_stats(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Get basic file statistics"""
        lines = content.split('\n')
        total_lines = len(lines)
        
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        # Simple line classification (could be improved per language)
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                comment_lines += 1
            else:
                code_lines += 1
        
        # File metadata
        stat = file_path.stat()
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        return {
            'size': stat.st_size,
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'file_hash': file_hash
        }
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        
        return language_map.get(extension, 'Unknown')
