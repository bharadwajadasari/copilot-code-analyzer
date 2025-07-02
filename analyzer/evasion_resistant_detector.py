"""
Evasion-Resistant AI Code Detection Engine
Detects AI-generated code even when processed through formatting tools like Prettier, Black, ESLint, etc.
"""

import re
import ast
import json
import hashlib
from typing import Dict, List, Any, Set, Tuple
from collections import Counter, defaultdict
import statistics
from .java_evasion_detector import JavaEvasionDetector
from .conservative_evasion_detector import ConservativeEvasionDetector

class EvasionResistantDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.config = indicators_config
        self.java_detector = JavaEvasionDetector(indicators_config)
        self.conservative_detector = ConservativeEvasionDetector(indicators_config)
        self.use_conservative_mode = indicators_config.get('conservative_mode', True)
        self._initialize_deep_patterns()
        self._initialize_semantic_analysis()
        self._initialize_weights()
    
    def _initialize_deep_patterns(self):
        """Initialize patterns that survive formatting tools"""
        
        # Semantic patterns (survive formatting)
        self.semantic_patterns = {
            'ai_logic_structures': [
                r'if\s+\w+\s*(?:is\s+not\s+None|!=\s*None)\s*and\s+\w+',  # AI-style null checks
                r'(?:result|data|response|output)\s*=\s*(?:None|{}|\[\])',  # AI variable initialization
                r'try:\s*\n\s*.*\n\s*except\s+\w*Error.*:\s*\n\s*(?:pass|continue|return|raise)',  # AI exception patterns
                r'for\s+\w+\s+in\s+(?:range\(len\(|enumerate\()',  # AI-style loops
                r'(?:if|while)\s+.*\s+and\s+.*\s+or\s+.*',  # Complex AI conditionals
            ],
            
            'ai_naming_semantics': [
                r'\b(?:temp|tmp)_\w+\b',  # AI temporary variables
                r'\b(?:result|data|response|output|value)_\d+\b',  # AI numbered variables
                r'\b(?:handle|process|execute|perform)_\w+\b',  # AI function naming
                r'\b(?:is|has|can|should)_\w+\b',  # AI boolean naming
                r'\b(?:get|set|create|update|delete)_\w+_\w+\b',  # AI CRUD patterns
            ],
            
            'ai_code_structure': [
                r'def\s+\w+\([^)]*\)\s*->\s*(?:Dict|List|Optional|Union)',  # AI type hints
                r'(?:Args|Returns|Raises):\s*\n\s*\w+.*:',  # AI docstring patterns
                r'"""[\s\S]*?"""',  # AI comprehensive docstrings
                r'#\s*(?:TODO|FIXME|NOTE|WARNING):\s*\w+',  # AI-style comments
                r'assert\s+\w+\s*(?:is\s+not\s+None|!=\s*None)',  # AI assertions
            ]
        }
        
        # Abstract Syntax Tree patterns (format-independent)
        self.ast_patterns = {
            'ai_node_sequences': [
                'Try-Except-Pass',
                'If-Not-None-And',
                'For-Range-Len',
                'Lambda-Filter-Map',
                'Dict-Comprehension-Condition'
            ],
            
            'ai_function_signatures': [
                'multiple_optional_params',
                'type_hints_all_params',
                'default_none_pattern',
                'args_kwargs_pattern'
            ]
        }
    
    def _initialize_semantic_analysis(self):
        """Initialize semantic analysis that looks beyond formatting"""
        
        # Code complexity patterns typical of AI
        self.complexity_indicators = {
            'cyclomatic_complexity': {
                'ai_range': (3, 8),  # AI tends to generate moderate complexity
                'human_range': (1, 15)  # Humans have wider variance
            },
            
            'nesting_depth': {
                'ai_pattern': [2, 3, 2],  # AI consistent nesting
                'human_pattern': [1, 2, 4, 1]  # Human irregular nesting
            },
            
            'variable_scope_usage': {
                'ai_indicators': ['consistent_naming', 'predictable_scope'],
                'human_indicators': ['variable_reuse', 'scope_mixing']
            }
        }
        
        # Mathematical and algorithmic patterns
        self.algorithmic_patterns = {
            'ai_algorithm_choices': [
                'nested_loops_for_simple_tasks',
                'explicit_type_checking',
                'defensive_programming_overuse',
                'standard_library_preference'
            ],
            
            'mathematical_expressions': [
                r'(?:math|np)\.(?:sqrt|pow|log|exp)\([^)]+\)',
                r'(?:sum|max|min|len)\([^)]+\)',
                r'(?:float|int|str)\([^)]+\)',
                r'(?:isinstance|hasattr|getattr)\([^)]+\)'
            ]
        }
    
    def _initialize_weights(self):
        """Initialize scoring weights for evasion-resistant detection"""
        self.weights = {
            'semantic_patterns': 0.30,
            'ast_structure': 0.25,
            'complexity_analysis': 0.20,
            'algorithmic_patterns': 0.15,
            'deep_linguistic': 0.10
        }
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Analyze content with evasion-resistant techniques"""
        
        # Use conservative mode by default for realistic detection rates
        if self.use_conservative_mode:
            return self.conservative_detector.analyze_content(content, file_extension)
        
        # Use Java-specific detector for Java files
        if file_extension == '.java':
            return self.java_detector.analyze_content(content, file_extension)
        
        # Remove formatting to analyze core structure for other languages
        normalized_content = self._normalize_code(content)
        
        # Multi-layer analysis
        semantic_score = self._analyze_semantic_patterns(normalized_content)
        ast_score = self._analyze_ast_structure(content, file_extension)
        complexity_score = self._analyze_complexity_patterns(content)
        algorithmic_score = self._analyze_algorithmic_patterns(normalized_content)
        linguistic_score = self._analyze_deep_linguistic(content)
        
        # Calculate weighted confidence
        confidence = (
            semantic_score * self.weights['semantic_patterns'] +
            ast_score * self.weights['ast_structure'] +
            complexity_score * self.weights['complexity_analysis'] +
            algorithmic_score * self.weights['algorithmic_patterns'] +
            linguistic_score * self.weights['deep_linguistic']
        )
        
        # Detect evasion attempts
        evasion_indicators = self._detect_evasion_attempts(content, normalized_content)
        
        return {
            'copilot_confidence': confidence,
            'risk_level': self._calculate_risk_level(confidence),
            'language': self._detect_language(file_extension),
            'evasion_resistance': {
                'semantic_score': semantic_score,
                'ast_score': ast_score,
                'complexity_score': complexity_score,
                'algorithmic_score': algorithmic_score,
                'linguistic_score': linguistic_score,
                'evasion_detected': len(evasion_indicators) > 0,
                'evasion_indicators': evasion_indicators
            },
            'explanation': self._generate_explanation(confidence, semantic_score, ast_score, evasion_indicators)
        }
    
    def _normalize_code(self, content: str) -> str:
        """Normalize code to remove formatting variations"""
        # Remove extra whitespace while preserving structure
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remove leading/trailing whitespace but preserve indentation structure
            stripped = line.strip()
            if stripped:
                # Count original indentation
                indent_count = len(line) - len(line.lstrip())
                # Normalize to consistent indentation
                normalized_line = '  ' * (indent_count // 2) + stripped
                normalized_lines.append(normalized_line)
        
        return '\n'.join(normalized_lines)
    
    def _analyze_semantic_patterns(self, content: str) -> float:
        """Analyze semantic patterns that survive formatting"""
        total_patterns = 0
        detected_patterns = 0
        
        for category, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                total_patterns += 1
                if matches:
                    detected_patterns += min(len(matches), 3)  # Cap contribution
        
        return min(detected_patterns / max(total_patterns, 1), 1.0)
    
    def _analyze_ast_structure(self, content: str, file_extension: str) -> float:
        """Analyze Abstract Syntax Tree structure"""
        if file_extension != '.py':
            return 0.0  # Currently only supports Python AST
        
        try:
            tree = ast.parse(content)
            
            # Analyze node patterns
            node_patterns = self._extract_node_patterns(tree)
            ai_pattern_score = self._score_node_patterns(node_patterns)
            
            # Analyze function signatures
            function_signatures = self._extract_function_signatures(tree)
            signature_score = self._score_function_signatures(function_signatures)
            
            return (ai_pattern_score + signature_score) / 2
            
        except (SyntaxError, ValueError):
            return 0.0
    
    def _analyze_complexity_patterns(self, content: str) -> float:
        """Analyze code complexity patterns"""
        lines = content.split('\n')
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(content)
        
        # Calculate nesting depth patterns
        nesting_pattern = self._calculate_nesting_pattern(lines)
        
        # Analyze variable scope usage
        scope_score = self._analyze_variable_scope(content)
        
        # AI tends to have moderate, consistent complexity
        complexity_score = 0.0
        if 3 <= complexity <= 8:  # AI sweet spot
            complexity_score = 0.7
        elif complexity > 15:  # Too complex for typical AI
            complexity_score = 0.1
        
        nesting_score = self._score_nesting_pattern(nesting_pattern)
        
        return (complexity_score + nesting_score + scope_score) / 3
    
    def _analyze_algorithmic_patterns(self, content: str) -> float:
        """Analyze algorithmic choices and mathematical patterns"""
        score = 0.0
        
        # Check for AI-typical algorithm choices
        for pattern in self.algorithmic_patterns['ai_algorithm_choices']:
            if self._detect_algorithmic_choice(content, pattern):
                score += 0.2
        
        # Check mathematical expressions
        math_patterns = 0
        for pattern in self.algorithmic_patterns['mathematical_expressions']:
            matches = re.findall(pattern, content)
            if matches:
                math_patterns += len(matches)
        
        if math_patterns > 0:
            score += min(math_patterns * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _analyze_deep_linguistic(self, content: str) -> float:
        """Analyze linguistic patterns in comments and strings"""
        # Extract comments and strings
        comments = re.findall(r'#.*$', content, re.MULTILINE)
        strings = re.findall(r'["\']([^"\']*)["\']', content)
        
        ai_linguistic_indicators = 0
        total_text = len(comments) + len(strings)
        
        if total_text == 0:
            return 0.0
        
        # AI linguistic patterns
        ai_patterns = [
            r'\b(?:should|must|will|shall)\b',  # AI modal verbs
            r'\b(?:ensure|verify|validate|check)\b',  # AI verification language
            r'\b(?:parameter|argument|variable|function)\b',  # AI technical terms
            r'\b(?:returns?|raises?|provides?)\b',  # AI documentation language
        ]
        
        for text in comments + strings:
            for pattern in ai_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    ai_linguistic_indicators += 1
        
        return min(ai_linguistic_indicators / total_text, 1.0)
    
    def _detect_evasion_attempts(self, original: str, normalized: str) -> List[str]:
        """Detect attempts to evade AI detection"""
        evasion_indicators = []
        
        # Check for excessive formatting changes
        original_lines = len(original.split('\n'))
        normalized_lines = len(normalized.split('\n'))
        
        if abs(original_lines - normalized_lines) > original_lines * 0.2:
            evasion_indicators.append('excessive_formatting_changes')
        
        # Check for unusual whitespace patterns
        whitespace_ratio = len(re.findall(r'\s+', original)) / len(original)
        if whitespace_ratio > 0.4:
            evasion_indicators.append('unusual_whitespace_patterns')
        
        # Check for comment insertion patterns
        comment_lines = len(re.findall(r'^\s*#', original, re.MULTILINE))
        code_lines = len([line for line in original.split('\n') if line.strip() and not line.strip().startswith('#')])
        
        if code_lines > 0 and comment_lines / code_lines > 0.5:
            evasion_indicators.append('excessive_comment_insertion')
        
        # Check for variable renaming patterns
        if self._detect_systematic_renaming(original):
            evasion_indicators.append('systematic_variable_renaming')
        
        return evasion_indicators
    
    def _detect_systematic_renaming(self, content: str) -> bool:
        """Detect systematic variable renaming attempts"""
        # Extract variable names
        variable_names = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content)
        
        # Check for patterns indicating systematic renaming
        single_letter_vars = len([name for name in variable_names if len(name) == 1])
        total_vars = len(set(variable_names))
        
        # High ratio of single-letter variables might indicate obfuscation
        if total_vars > 10 and single_letter_vars / total_vars > 0.3:
            return True
        
        # Check for sequential naming patterns (var1, var2, var3)
        numbered_vars = [name for name in variable_names if re.match(r'^\w+\d+$', name)]
        if len(numbered_vars) > 5:
            return True
        
        return False
    
    def _calculate_risk_level(self, confidence: float) -> str:
        """Calculate risk level based on confidence"""
        if confidence >= 0.7:
            return "HIGH"
        elif confidence >= 0.4:
            return "MEDIUM"
        elif confidence >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_explanation(self, confidence: float, semantic_score: float, 
                            ast_score: float, evasion_indicators: List[str]) -> List[str]:
        """Generate human-readable explanation"""
        explanation = []
        
        if confidence >= 0.6:
            explanation.append("Strong AI-generated code patterns detected")
        elif confidence >= 0.3:
            explanation.append("Moderate AI-generated code patterns detected")
        else:
            explanation.append("Minimal AI-generated code patterns detected")
        
        if semantic_score > 0.5:
            explanation.append("Semantic patterns typical of AI code generation")
        
        if ast_score > 0.5:
            explanation.append("Code structure patterns consistent with AI generation")
        
        if evasion_indicators:
            explanation.append(f"Potential evasion attempts detected: {', '.join(evasion_indicators)}")
        
        return explanation
    
    # Helper methods (abbreviated for space)
    def _extract_node_patterns(self, tree) -> List[str]:
        """Extract AST node patterns"""
        patterns = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                patterns.append('Try-Except-Pass')
            elif isinstance(node, ast.ListComp):
                patterns.append('List-Comprehension')
            # Add more pattern extraction logic
        return patterns
    
    def _score_node_patterns(self, patterns: List[str]) -> float:
        """Score AST node patterns"""
        ai_patterns = {'Try-Except-Pass', 'List-Comprehension', 'Dict-Comprehension'}
        ai_pattern_count = sum(1 for pattern in patterns if pattern in ai_patterns)
        return min(ai_pattern_count / max(len(patterns), 1), 1.0)
    
    def _extract_function_signatures(self, tree) -> List[Dict]:
        """Extract function signatures from AST"""
        signatures = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                sig = {
                    'name': node.name,
                    'args_count': len(node.args.args),
                    'has_defaults': len(node.args.defaults) > 0,
                    'has_type_hints': any(arg.annotation for arg in node.args.args)
                }
                signatures.append(sig)
        return signatures
    
    def _score_function_signatures(self, signatures: List[Dict]) -> float:
        """Score function signatures for AI patterns"""
        if not signatures:
            return 0.0
        
        ai_indicators = 0
        for sig in signatures:
            if sig['has_type_hints']:
                ai_indicators += 1
            if sig['has_defaults'] and sig['args_count'] > 2:
                ai_indicators += 1
        
        return ai_indicators / len(signatures)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity"""
        # Simplified complexity calculation
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_points = [
            r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\bexcept\b',
            r'\band\b', r'\bor\b', r'\?', r'\bcase\b'
        ]
        
        for pattern in decision_points:
            complexity += len(re.findall(pattern, content))
        
        return complexity
    
    def _calculate_nesting_pattern(self, lines: List[str]) -> List[int]:
        """Calculate nesting depth pattern"""
        nesting_depths = []
        current_depth = 0
        
        for line in lines:
            if line.strip():
                # Calculate indentation depth
                indent = len(line) - len(line.lstrip())
                depth = indent // 4  # Assuming 4-space indentation
                nesting_depths.append(depth)
        
        return nesting_depths
    
    def _score_nesting_pattern(self, pattern: List[int]) -> float:
        """Score nesting pattern for AI characteristics"""
        if not pattern:
            return 0.0
        
        # AI tends to have consistent, moderate nesting
        avg_depth = statistics.mean(pattern)
        std_dev = statistics.stdev(pattern) if len(pattern) > 1 else 0
        
        # AI characteristics: moderate average depth, low variance
        if 1.5 <= avg_depth <= 3.0 and std_dev <= 1.0:
            return 0.8
        else:
            return 0.2
    
    def _analyze_variable_scope(self, content: str) -> float:
        """Analyze variable scope usage patterns"""
        # Extract variable assignments
        assignments = re.findall(r'(\w+)\s*=', content)
        
        if not assignments:
            return 0.0
        
        # AI tends to use consistent variable naming
        unique_vars = set(assignments)
        if len(unique_vars) / len(assignments) > 0.8:  # High uniqueness ratio
            return 0.7
        else:
            return 0.3
    
    def _detect_algorithmic_choice(self, content: str, pattern: str) -> bool:
        """Detect specific algorithmic choice patterns"""
        if pattern == 'nested_loops_for_simple_tasks':
            return bool(re.search(r'for.*for.*in', content))
        elif pattern == 'explicit_type_checking':
            return bool(re.search(r'isinstance\(|type\(.*\) ==', content))
        elif pattern == 'defensive_programming_overuse':
            return bool(re.search(r'if.*is not None.*if.*is not None', content))
        elif pattern == 'standard_library_preference':
            return bool(re.search(r'import (?:os|sys|json|re|math)', content))
        return False
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        return language_map.get(file_extension.lower(), 'unknown')