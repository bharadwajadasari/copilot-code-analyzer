"""
Enhanced Copilot Detection Engine
Implements sophisticated pattern recognition and statistical analysis for AI code detection.
"""

import re
import ast
import json
import statistics
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
from utils.logger import setup_logger

logger = setup_logger(__name__)

class EnhancedCopilotDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.config = indicators_config
        self._initialize_patterns()
        self._initialize_weights()
        
    def _initialize_patterns(self):
        """Initialize comprehensive detection patterns"""
        
        # Explicit AI indicators - highest confidence
        self.explicit_patterns = [
            r'#\s*(generated|copilot|ai|auto-generated|gpt)',
            r'//\s*(generated|copilot|ai|auto-generated|gpt)',
            r'/\*.*?(generated|copilot|ai|gpt).*?\*/',
            r'""".*?(generated|copilot|ai|gpt).*?"""',
            r'@generated',
            r'@copilot',
        ]
        
        # Structural patterns - AI tends to create perfect structure
        self.structural_patterns = {
            'python': [
                r'def\s+\w+\(.*\)\s*->\s*[A-Z]\w*:',  # Perfect type hints
                r'class\s+\w+\([A-Z]\w*\):\s*\n\s*""".*?""".*?\n\s*def\s+__init__',  # Documented classes
                r'try:\s*\n.*?\nexcept\s+\w+Exception\s+as\s+\w+:\s*\n.*?\nfinally:',  # Complete exception handling
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]:\s*\n',  # Main guard
                r'@\w+\s*\n\s*def\s+\w+',  # Decorated functions
                r'from\s+typing\s+import\s+.*Union.*Optional',  # Complex typing imports
            ],
            'javascript': [
                r'const\s+\w+:\s*\w+\s*=',  # TypeScript declarations
                r'export\s+(const|function|default|interface)',  # ES6 exports
                r'async\s+function\s+\w+\([^)]*\):\s*Promise<\w+>',  # Async with return types
                r'interface\s+\w+\s*{[^}]*}',  # Interface definitions
                r'try\s*{[^}]*}\s*catch\s*\([^)]*\)\s*{[^}]*}',  # Try-catch blocks
            ],
            'java': [
                r'public\s+class\s+\w+\s*{',  # Public class declarations
                r'@Override\s*\n\s*public\s+\w+',  # Override annotations
                r'try\s*{[^}]*}\s*catch\s*\([^)]*\)\s*{[^}]*}\s*finally\s*{[^}]*}',  # Complete try-catch-finally
            ]
        }
        
        # Naming patterns - AI uses consistent naming
        self.naming_patterns = [
            r'\bget[A-Z]\w*\b',      # getProperty
            r'\bset[A-Z]\w*\b',      # setProperty
            r'\bcalculate[A-Z]\w*\b', # calculateTotal
            r'\bprocess[A-Z]\w*\b',   # processData
            r'\bvalidate[A-Z]\w*\b',  # validateInput
            r'\bhandle[A-Z]\w*\b',    # handleError
            r'\bcreate[A-Z]\w*\b',    # createElement
            r'\bupdate[A-Z]\w*\b',    # updateValue
            r'\bdelete[A-Z]\w*\b',    # deleteItem
        ]
        
        # Code complexity patterns - AI prefers certain constructs
        self.complexity_patterns = [
            r'lambda\s+\w+:\s*\w+\([^)]*\)',  # Complex lambdas
            r'list\(filter\(.*?,.*?\)\)',     # Functional programming
            r'\[.*?\s+for\s+.*?\s+in\s+.*?\s+if\s+.*?\]',  # List comprehensions with conditions
            r'\w+\.\w+\.\w+\.\w+',            # Deep method chaining
            r'with\s+open\([^)]*\)\s+as\s+\w+:',  # Context managers
        ]
        
        # Compile all patterns
        self.compiled_explicit = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in self.explicit_patterns]
        self.compiled_naming = [re.compile(p) for p in self.naming_patterns]
        self.compiled_complexity = [re.compile(p, re.MULTILINE) for p in self.complexity_patterns]
        
        self.compiled_structural = {}
        for lang, patterns in self.structural_patterns.items():
            self.compiled_structural[lang] = [re.compile(p, re.MULTILINE) for p in patterns]
    
    def _initialize_weights(self):
        """Initialize scoring weights for different indicators"""
        self.weights = {
            'explicit_indicators': 0.35,    # Direct mentions of AI
            'structural_perfection': 0.25,  # Perfect code structure
            'naming_consistency': 0.15,     # Consistent naming patterns
            'complexity_patterns': 0.15,    # Specific complexity signatures
            'syntax_quality': 0.10          # Overall syntax quality
        }
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Comprehensive analysis of code content for AI generation indicators"""
        
        if not content.strip():
            return self._create_empty_analysis()
        
        # Basic metrics
        lines = [line for line in content.split('\n') if line.strip()]
        total_lines = len(lines)
        
        if total_lines == 0:
            return self._create_empty_analysis()
        
        # Detect programming language
        language = self._detect_language(file_extension)
        
        # Perform different analyses
        explicit_score = self._analyze_explicit_indicators(content)
        structural_score = self._analyze_structural_patterns(content, language)
        naming_score = self._analyze_naming_patterns(content)
        complexity_score = self._analyze_complexity_patterns(content)
        syntax_score = self._analyze_syntax_quality(content, language)
        
        # Statistical analysis
        statistical_indicators = self._analyze_statistical_patterns(content, lines)
        
        # Calculate weighted confidence
        weighted_confidence = (
            explicit_score * self.weights['explicit_indicators'] +
            structural_score * self.weights['structural_perfection'] +
            naming_score * self.weights['naming_consistency'] +
            complexity_score * self.weights['complexity_patterns'] +
            syntax_score * self.weights['syntax_quality']
        )
        
        # Apply statistical adjustments
        final_confidence = self._apply_statistical_adjustments(
            weighted_confidence, statistical_indicators, total_lines
        )
        
        # Calculate risk assessment
        risk_level = self._calculate_risk_level(final_confidence, {
            'explicit': explicit_score > 0.8,
            'structural': structural_score > 0.7,
            'naming': naming_score > 0.6,
            'complexity': complexity_score > 0.5
        })
        
        return {
            'confidence_score': final_confidence,
            'estimated_lines': int(total_lines * final_confidence),
            'total_analyzed_lines': total_lines,
            'risk_level': risk_level,
            'language': language,
            'indicators': {
                'explicit_ai_mentions': explicit_score > 0.8,
                'perfect_structure': structural_score > 0.7,
                'consistent_naming': naming_score > 0.6,
                'ai_complexity_patterns': complexity_score > 0.5,
                'high_syntax_quality': syntax_score > 0.8
            },
            'detailed_scores': {
                'explicit_indicators': explicit_score,
                'structural_patterns': structural_score,
                'naming_consistency': naming_score,
                'complexity_patterns': complexity_score,
                'syntax_quality': syntax_score
            },
            'statistical_analysis': statistical_indicators
        }
    
    def _analyze_explicit_indicators(self, content: str) -> float:
        """Check for explicit AI/Copilot mentions"""
        matches = 0
        for pattern in self.compiled_explicit:
            if pattern.search(content):
                matches += 1
        
        # Scale: any explicit mention gives high confidence
        return min(matches * 0.9, 1.0)
    
    def _analyze_structural_patterns(self, content: str, language: str) -> float:
        """Analyze code structure for AI-typical patterns"""
        if language not in self.compiled_structural:
            return 0.0
        
        patterns = self.compiled_structural[language]
        matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            if pattern.search(content):
                matches += 1
        
        # Calculate structural perfection score
        structure_score = matches / total_patterns if total_patterns > 0 else 0.0
        
        # Check for overly perfect structure (AI indicator)
        lines = content.split('\n')
        indentation_consistency = self._check_indentation_consistency(lines)
        comment_ratio = self._calculate_comment_ratio(lines)
        
        # AI tends to have very consistent indentation and moderate commenting
        perfection_bonus = 0.0
        if indentation_consistency > 0.9 and 0.1 < comment_ratio < 0.3:
            perfection_bonus = 0.2
        
        return min(structure_score + perfection_bonus, 1.0)
    
    def _analyze_naming_patterns(self, content: str) -> float:
        """Analyze naming patterns for AI consistency"""
        total_matches = 0
        total_functions = 0
        
        # Count function/method definitions
        function_patterns = [
            r'def\s+(\w+)\(',      # Python functions
            r'function\s+(\w+)\(', # JavaScript functions
            r'public\s+\w+\s+(\w+)\(',  # Java methods
        ]
        
        for pattern in function_patterns:
            functions = re.findall(pattern, content)
            total_functions += len(functions)
            
            # Check how many follow AI naming patterns
            for func_name in functions:
                for naming_pattern in self.compiled_naming:
                    if naming_pattern.search(func_name):
                        total_matches += 1
                        break
        
        if total_functions == 0:
            return 0.0
        
        consistency_ratio = total_matches / total_functions
        
        # Check for variable naming consistency
        variable_consistency = self._analyze_variable_naming(content)
        
        return min((consistency_ratio + variable_consistency) / 2, 1.0)
    
    def _analyze_complexity_patterns(self, content: str) -> float:
        """Analyze complexity patterns typical of AI code"""
        matches = 0
        for pattern in self.compiled_complexity:
            matches += len(pattern.findall(content))
        
        lines = content.split('\n')
        complexity_density = matches / len(lines) if lines else 0
        
        # AI tends to use certain complexity patterns moderately
        if 0.05 <= complexity_density <= 0.2:
            return min(complexity_density * 5, 1.0)
        elif complexity_density > 0.2:
            return 0.8  # Too complex might indicate human code
        else:
            return complexity_density * 2
    
    def _analyze_syntax_quality(self, content: str, language: str) -> float:
        """Analyze syntax quality (AI tends to produce perfect syntax)"""
        try:
            if language == 'python':
                return self._analyze_python_syntax(content)
            elif language in ['javascript', 'typescript']:
                return self._analyze_javascript_syntax(content)
            else:
                return self._analyze_generic_syntax(content)
        except Exception:
            return 0.0
    
    def _analyze_python_syntax(self, content: str) -> float:
        """Analyze Python syntax quality"""
        try:
            ast.parse(content)
            syntax_perfect = 1.0
        except SyntaxError:
            syntax_perfect = 0.0
        
        # Check for PEP 8 compliance indicators
        pep8_indicators = [
            r'import\s+\w+$',  # Clean imports
            r'^\s{4}',         # 4-space indentation
            r':\s*\n',         # Proper colon usage
        ]
        
        pep8_score = sum(1 for pattern in pep8_indicators 
                        if re.search(pattern, content, re.MULTILINE)) / len(pep8_indicators)
        
        return (syntax_perfect + pep8_score) / 2
    
    def _analyze_javascript_syntax(self, content: str) -> float:
        """Analyze JavaScript/TypeScript syntax quality"""
        # Check for modern JS patterns
        modern_patterns = [
            r'const\s+\w+\s*=',     # const declarations
            r'=>',                   # Arrow functions
            r'async\s+\w+',         # Async functions
            r'\.then\(',            # Promise chains
        ]
        
        modern_score = sum(1 for pattern in modern_patterns 
                          if re.search(pattern, content)) / len(modern_patterns)
        
        # Check for consistent semicolon usage
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        semicolon_lines = [line for line in lines if line.endswith(';')]
        semicolon_consistency = len(semicolon_lines) / len(lines) if lines else 0
        
        return (modern_score + semicolon_consistency) / 2
    
    def _analyze_generic_syntax(self, content: str) -> float:
        """Generic syntax analysis for other languages"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Check for balanced brackets
        brackets = {'(': ')', '[': ']', '{': '}'}
        bracket_balance = 0
        
        for char in content:
            if char in brackets:
                bracket_balance += 1
            elif char in brackets.values():
                bracket_balance += 1
        
        # Simple heuristic: balanced code tends to be AI-generated
        return min(bracket_balance / len(lines) if lines else 0, 1.0)
    
    def _analyze_statistical_patterns(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze statistical patterns in the code"""
        
        # Line length analysis
        line_lengths = [len(line) for line in lines]
        avg_line_length = statistics.mean(line_lengths) if line_lengths else 0
        line_length_std = statistics.stdev(line_lengths) if len(line_lengths) > 1 else 0
        
        # Indentation analysis
        indentations = []
        for line in lines:
            if line.strip():  # Non-empty lines
                indentations.append(len(line) - len(line.lstrip()))
        
        indentation_consistency = self._calculate_indentation_consistency(indentations)
        
        # Token frequency analysis
        tokens = re.findall(r'\w+', content.lower())
        token_frequency = Counter(tokens)
        
        return {
            'avg_line_length': avg_line_length,
            'line_length_variance': line_length_std,
            'indentation_consistency': indentation_consistency,
            'unique_token_ratio': len(set(tokens)) / len(tokens) if tokens else 0,
            'most_common_tokens': token_frequency.most_common(5)
        }
    
    def _apply_statistical_adjustments(self, base_confidence: float, 
                                     statistical_indicators: Dict[str, Any], 
                                     total_lines: int) -> float:
        """Apply statistical adjustments to base confidence"""
        
        adjusted_confidence = base_confidence
        
        # AI code tends to have consistent line lengths
        if 60 <= statistical_indicators['avg_line_length'] <= 90:
            adjusted_confidence += 0.1
        
        # AI code tends to have very consistent indentation
        if statistical_indicators['indentation_consistency'] > 0.95:
            adjusted_confidence += 0.1
        
        # Very short files are harder to classify
        if total_lines < 10:
            adjusted_confidence *= 0.7
        
        # Very long files with high confidence are likely AI
        if total_lines > 100 and base_confidence > 0.7:
            adjusted_confidence += 0.05
        
        return min(adjusted_confidence, 1.0)
    
    def _calculate_risk_level(self, confidence: float, indicators: Dict[str, bool]) -> str:
        """Calculate risk level based on confidence and indicators"""
        
        high_risk_indicators = sum(indicators.values())
        
        if confidence >= 0.8 or high_risk_indicators >= 3:
            return "HIGH"
        elif confidence >= 0.6 or high_risk_indicators >= 2:
            return "MEDIUM"
        elif confidence >= 0.3 or high_risk_indicators >= 1:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
        }
        return language_map.get(file_extension.lower(), 'unknown')
    
    def _check_indentation_consistency(self, lines: List[str]) -> float:
        """Check consistency of indentation"""
        if not lines:
            return 1.0
        
        indents = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indents.append(indent)
        
        if not indents:
            return 1.0
        
        # Calculate consistency based on standard deviation
        if len(indents) == 1:
            return 1.0
        
        std_dev = statistics.stdev(indents)
        max_indent = max(indents)
        
        if max_indent == 0:
            return 1.0
        
        consistency = 1.0 - (std_dev / max_indent)
        return max(0.0, consistency)
    
    def _calculate_indentation_consistency(self, indentations: List[int]) -> float:
        """Calculate indentation consistency score"""
        if len(indentations) <= 1:
            return 1.0
        
        # Check if indentations follow a consistent pattern
        unique_indents = sorted(set(indentations))
        
        if not unique_indents:
            return 1.0
        
        # Check for consistent step size
        if len(unique_indents) > 1:
            steps = [unique_indents[i+1] - unique_indents[i] for i in range(len(unique_indents)-1)]
            if len(set(steps)) == 1:  # All steps are the same
                return 1.0
        
        # Calculate based on variance
        variance = statistics.variance(indentations)
        max_indent = max(indentations) if indentations else 1
        
        return max(0.0, 1.0 - (variance / (max_indent + 1)))
    
    def _calculate_comment_ratio(self, lines: List[str]) -> float:
        """Calculate ratio of comment lines to total lines"""
        if not lines:
            return 0.0
        
        comment_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                comment_lines += 1
        
        return comment_lines / len(lines)
    
    def _analyze_variable_naming(self, content: str) -> float:
        """Analyze variable naming consistency"""
        
        # Extract variable names
        variable_patterns = [
            r'\b([a-z_][a-z0-9_]*)\s*=',  # Python/JS variables
            r'let\s+([a-z_][a-z0-9_]*)',   # JS let declarations
            r'const\s+([a-z_][a-z0-9_]*)', # JS const declarations
            r'var\s+([a-z_][a-z0-9_]*)',   # JS var declarations
        ]
        
        variables = []
        for pattern in variable_patterns:
            variables.extend(re.findall(pattern, content, re.IGNORECASE))
        
        if not variables:
            return 0.0
        
        # Check naming convention consistency
        snake_case = sum(1 for var in variables if '_' in var and var.islower())
        camel_case = sum(1 for var in variables if var != var.lower() and '_' not in var)
        
        total_vars = len(variables)
        max_convention = max(snake_case, camel_case)
        
        consistency = max_convention / total_vars if total_vars > 0 else 0
        
        # AI tends to be very consistent with naming
        return consistency
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis result for empty files"""
        return {
            'confidence_score': 0.0,
            'estimated_lines': 0,
            'total_analyzed_lines': 0,
            'risk_level': 'MINIMAL',
            'language': 'unknown',
            'indicators': {
                'explicit_ai_mentions': False,
                'perfect_structure': False,
                'consistent_naming': False,
                'ai_complexity_patterns': False,
                'high_syntax_quality': False
            },
            'detailed_scores': {
                'explicit_indicators': 0.0,
                'structural_patterns': 0.0,
                'naming_consistency': 0.0,
                'complexity_patterns': 0.0,
                'syntax_quality': 0.0
            },
            'statistical_analysis': {
                'avg_line_length': 0,
                'line_length_variance': 0,
                'indentation_consistency': 1.0,
                'unique_token_ratio': 0,
                'most_common_tokens': []
            }
        }