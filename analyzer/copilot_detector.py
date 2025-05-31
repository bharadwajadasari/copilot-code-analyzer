"""
Copilot Detection Engine
Implements heuristic-based detection of AI-generated code patterns.
"""

import re
import ast
import json
from typing import Dict, List, Any, Tuple
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CopilotDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.comment_patterns = indicators_config['comment_patterns']
        self.high_velocity_threshold = indicators_config['high_velocity_threshold']
        self.perfect_syntax_weight = indicators_config['perfect_syntax_weight']
        self.common_patterns_weight = indicators_config['common_patterns_weight']
        self.complexity_threshold = indicators_config.get('complexity_threshold', 10)
        
        # Common AI-generated code patterns
        self.ai_patterns = [
            r'def\s+\w+\(.*\)\s*->\s*\w+:',  # Type hints in Python
            r'const\s+\w+:\s*\w+\s*=',       # TypeScript const declarations
            r'function\s+\w+\([^)]*\):\s*\w+',  # TypeScript function declarations
            r'export\s+(const|function|default)',  # ES6 exports
            r'import\s+.*\s+from\s+[\'"].*[\'"]',  # ES6 imports
            r'@\w+(\([^)]*\))?',              # Decorators/Annotations
            r'async\s+def\s+\w+',             # Async functions
            r'lambda\s+\w*:',                 # Lambda functions
        ]
        
        # Compile regex patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.MULTILINE) for pattern in self.ai_patterns]
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Analyze content for Copilot-generated code indicators"""
        
        lines = content.split('\n')
        total_lines = len([line for line in lines if line.strip()])  # Non-empty lines
        
        if total_lines == 0:
            return self._create_empty_analysis()
        
        # Analyze different indicators
        comment_score = self._analyze_comments(content)
        pattern_score = self._analyze_patterns(content)
        syntax_score = self._analyze_syntax_quality(content, file_extension)
        structure_score = self._analyze_code_structure(content, file_extension)
        
        # Combine scores with weights
        confidence_weights = {
            'comments': 0.4,
            'patterns': 0.3,
            'syntax': 0.2,
            'structure': 0.1
        }
        
        overall_confidence = (
            comment_score * confidence_weights['comments'] +
            pattern_score * confidence_weights['patterns'] +
            syntax_score * confidence_weights['syntax'] +
            structure_score * confidence_weights['structure']
        )
        
        # Estimate number of Copilot-generated lines
        estimated_lines = int(total_lines * overall_confidence)
        
        return {
            'confidence_score': overall_confidence,
            'estimated_lines': estimated_lines,
            'total_analyzed_lines': total_lines,
            'indicators': {
                'explicit_comments': comment_score > 0.8,
                'ai_patterns_detected': pattern_score > 0.3,
                'perfect_syntax': syntax_score > 0.7,
                'consistent_structure': structure_score > 0.6
            },
            'detailed_scores': {
                'comment_analysis': comment_score,
                'pattern_analysis': pattern_score,
                'syntax_analysis': syntax_score,
                'structure_analysis': structure_score
            }
        }
    
    def _analyze_comments(self, content: str) -> float:
        """Analyze comments for explicit Copilot indicators"""
        score = 0.0
        
        # Check for explicit Copilot comments
        for pattern in self.comment_patterns:
            if pattern.lower() in content.lower():
                score = 1.0
                break
        
        # Check for AI-style comments
        ai_comment_patterns = [
            r'#\s*This\s+(function|method|class)\s+.*',
            r'//\s*This\s+(function|method|class)\s+.*',
            r'#\s*Generate\s+.*',
            r'//\s*Generate\s+.*',
            r'#\s*Create\s+a\s+.*',
            r'//\s*Create\s+a\s+.*'
        ]
        
        ai_comment_count = 0
        for pattern in ai_comment_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            ai_comment_count += len(matches)
        
        # Calculate score based on AI-style comments density
        lines = content.split('\n')
        if ai_comment_count > 0:
            comment_density = ai_comment_count / len(lines)
            score = max(score, min(comment_density * 10, 0.8))  # Cap at 0.8 unless explicit
        
        return score
    
    def _analyze_patterns(self, content: str) -> float:
        """Analyze code for common AI-generated patterns"""
        pattern_matches = 0
        total_possible_matches = len(self.compiled_patterns)
        
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                pattern_matches += 1
        
        # Additional pattern checks
        modern_patterns = [
            'const ' in content and 'let ' in content,  # Modern JS/TS patterns
            '=> ' in content,  # Arrow functions
            'async/await' in content.replace(' ', ''),  # Async patterns
            re.search(r'\.map\(.*=>', content) is not None,  # Functional programming
            re.search(r'\.filter\(.*=>', content) is not None,
            re.search(r'\.reduce\(.*=>', content) is not None,
        ]
        
        modern_pattern_score = sum(modern_patterns) / len(modern_patterns)
        
        # Combine scores
        base_score = pattern_matches / total_possible_matches if total_possible_matches > 0 else 0
        combined_score = (base_score + modern_pattern_score) / 2
        
        return combined_score
    
    def _analyze_syntax_quality(self, content: str, file_extension: str) -> float:
        """Analyze syntax quality (AI tends to produce syntactically perfect code)"""
        try:
            if file_extension == '.py':
                return self._analyze_python_syntax(content)
            elif file_extension in ['.js', '.ts', '.jsx', '.tsx']:
                return self._analyze_javascript_syntax(content)
            else:
                return self._analyze_generic_syntax(content)
        except Exception as e:
            logger.debug(f"Syntax analysis error: {e}")
            return 0.0
    
    def _analyze_python_syntax(self, content: str) -> float:
        """Analyze Python syntax quality"""
        try:
            # Try to parse as AST
            tree = ast.parse(content)
            
            # Check for modern Python features
            modern_features = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.AnnAssign):  # Type annotations
                    modern_features += 1
                elif isinstance(node, ast.AsyncFunctionDef):  # Async functions
                    modern_features += 1
                elif isinstance(node, ast.JoinedStr):  # f-strings
                    modern_features += 1
            
            # Perfect syntax score
            syntax_score = 0.8  # Base score for valid syntax
            
            # Bonus for modern features
            lines = len(content.split('\n'))
            modern_density = modern_features / max(lines, 1)
            syntax_score += min(modern_density * 2, 0.2)
            
            return min(syntax_score, 1.0)
            
        except SyntaxError:
            return 0.0
    
    def _analyze_javascript_syntax(self, content: str) -> float:
        """Analyze JavaScript/TypeScript syntax quality"""
        # Count modern JS features
        modern_features = [
            'const ' in content,
            'let ' in content,
            '=>' in content,  # Arrow functions
            '...' in content,  # Spread operator
            'async ' in content,
            'await ' in content,
            'import ' in content,
            'export ' in content,
        ]
        
        feature_score = sum(modern_features) / len(modern_features)
        
        # Check for consistent formatting (AI tends to be consistent)
        consistency_indicators = [
            content.count(';') > content.count('\n') * 0.8,  # Semicolon usage
            re.search(r'{\s*\n', content) is not None,  # Consistent bracing
        ]
        
        consistency_score = sum(consistency_indicators) / len(consistency_indicators)
        
        return (feature_score + consistency_score) / 2
    
    def _analyze_generic_syntax(self, content: str) -> float:
        """Generic syntax analysis for other languages"""
        # Basic indicators of clean, AI-like code
        indicators = [
            len(re.findall(r'\n\s*\n', content)) < len(content.split('\n')) * 0.1,  # Few empty lines
            content.count('\t') == 0 or content.count('    ') == 0,  # Consistent indentation
            len([line for line in content.split('\n') if len(line.strip()) > 120]) == 0,  # Reasonable line length
        ]
        
        return sum(indicators) / len(indicators) if indicators else 0.0
    
    def _analyze_code_structure(self, content: str, file_extension: str) -> float:
        """Analyze code structure patterns typical of AI generation"""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if not non_empty_lines:
            return 0.0
        
        # Check for consistent indentation
        indentations = []
        for line in non_empty_lines:
            if line.startswith(' ') or line.startswith('\t'):
                leading_spaces = len(line) - len(line.lstrip())
                indentations.append(leading_spaces)
        
        consistent_indentation = 0.0
        if indentations:
            # Check if indentation follows a pattern (AI tends to be very consistent)
            unique_indents = set(indentations)
            if len(unique_indents) <= 3:  # Very few indentation levels
                consistent_indentation = 0.8
        
        # Check for function/method organization
        function_patterns = [
            r'def\s+\w+',      # Python functions
            r'function\s+\w+', # JavaScript functions
            r'public\s+\w+',   # Java/C# methods
            r'private\s+\w+',
        ]
        
        function_count = 0
        for pattern in function_patterns:
            function_count += len(re.findall(pattern, content))
        
        # AI tends to create well-organized, single-purpose functions
        organization_score = 0.0
        if function_count > 0:
            avg_lines_per_function = len(non_empty_lines) / function_count
            if 5 <= avg_lines_per_function <= 20:  # Reasonable function size
                organization_score = 0.7
        
        return (consistent_indentation + organization_score) / 2
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create an empty analysis result"""
        return {
            'confidence_score': 0.0,
            'estimated_lines': 0,
            'total_analyzed_lines': 0,
            'indicators': {
                'explicit_comments': False,
                'ai_patterns_detected': False,
                'perfect_syntax': False,
                'consistent_structure': False
            },
            'detailed_scores': {
                'comment_analysis': 0.0,
                'pattern_analysis': 0.0,
                'syntax_analysis': 0.0,
                'structure_analysis': 0.0
            }
        }
