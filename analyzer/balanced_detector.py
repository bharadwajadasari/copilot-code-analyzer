"""
Balanced Copilot Detection Engine
Accurately detects AI-generated code while minimizing false positives on human code.
Uses contextual analysis and realistic thresholds.
"""

import re
import ast
import statistics
from typing import Dict, List, Any, Tuple
from collections import Counter
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BalancedCopilotDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.config = indicators_config
        self._initialize_patterns()
        self._initialize_weights()
        
    def _initialize_patterns(self):
        """Initialize balanced detection patterns"""
        
        # Strong AI indicators - high confidence patterns
        self.strong_ai_patterns = {
            'explicit_markers': [
                r'#\s*AI-generated',  # Your specific marker
                r'#\s*Generated\s+by\s+(AI|Copilot|GitHub\s+Copilot)',
                r'@generated\s*$',
                r'#\s*@generated\s*$',
                r'This\s+code\s+was\s+(generated|created)\s+by\s+(AI|Copilot|assistant)',
                r'Auto-generated\s+by',
                r'Code\s+Generated\s+by\s+Copilot',
                r'Copilot\s+(Detection|Analysis|Code)',  # AI tool references
                r'machine\s+learning\s+techniques',  # AI terminology
                r'detection\s+(algorithms?|engine)',  # AI detection context
            ],
            'ai_documentation_style': [
                r'"""[\s\S]*?Args:[\s\S]*?Returns:[\s\S]*?"""',  # Perfect docstring format
                r'"""[\s\S]*?Parameters:[\s\S]*?Returns:[\s\S]*?"""',
                r'"""[\s\S]*?Example:[\s\S]*?>>>[\s\S]*?"""',  # Docstring with examples
                r'def\s+\w+\([^)]*\):\s*\n\s*"""[^"]*"""',  # Function with immediate docstring
                r'class\s+\w+[^:]*:\s*\n\s*"""[^"]*"""',  # Class with immediate docstring
                r'"""[\s\S]*?(Initialize|Analyze|Calculate|Process)[\s\S]*?"""',  # AI-style descriptions
            ],
            'ai_code_patterns': [
                r'def\s+\w+\([^)]*\)\s*->\s*(Optional\[|Union\[|List\[|Dict\[)',  # Complex type hints
                r'try:\s*\n[\s\S]*?\nexcept\s+\w*Exception\s+as\s+\w+:\s*\n\s*logger\.',  # Perfect exception handling
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]:\s*\n\s*main\(\)',  # Perfect main guard
                r'from\s+typing\s+import\s+.*Dict.*Any',  # Complex typing imports
                r'def\s+_[a-z_]+\([^)]*\)\s*->\s*(float|int|str|bool):', # Private methods with type hints
                r'self\.\w+\s*=\s*\w+\s*or\s*\{\}',  # Default dict initialization pattern
            ]
        }
        
        # Moderate AI indicators - medium confidence patterns
        self.moderate_ai_patterns = {
            'consistent_naming': [
                r'\bget_[a-z_]+\b',  # Consistent getter naming
                r'\bset_[a-z_]+\b',  # Consistent setter naming
                r'\bcalculate_[a-z_]+\b',  # Consistent calculation naming
                r'\bprocess_[a-z_]+\b',  # Consistent processing naming
                r'\bvalidate_[a-z_]+\b',  # Consistent validation naming
            ],
            'structural_consistency': [
                r'from\s+typing\s+import\s+.*Optional.*Union',  # Heavy typing usage
                r'@\w+\s*\n\s*def\s+\w+',  # Consistent decorator usage
                r'class\s+\w+\([A-Z]\w*\):\s*\n\s*"""',  # Documented classes
            ],
            'modern_patterns': [
                r'f[\'"][^\'\"]*{[^}]+}[^\'\"]*[\'"]',  # F-string usage
                r'with\s+open\([^)]*\)\s+as\s+\w+:',  # Context manager usage
                r'lambda\s+\w+:\s+\w+\.',  # Functional programming
            ]
        }
        
        # Weak AI indicators - low confidence patterns
        self.weak_ai_patterns = [
            r'#\s*TODO:',  # TODO comments
            r'#\s*FIXME:',  # FIXME comments
            r'#\s*NOTE:',  # NOTE comments
        ]
        
        # Human-specific patterns that reduce AI confidence
        self.human_patterns = [
            r'#\s*(hack|quick\s+fix|temporary)',  # Informal comments
            r'\b(wtf|damn|shit|crap)\b',  # Informal language
            r'#\s*[a-z]',  # Lowercase comment starts (informal)
            r'\w{1,2}\s*=\s*\w{1,2}',  # Short variable names
            r'def\s+[a-z]{1,3}\(',  # Very short function names
        ]
        
        # Compile patterns
        self.compiled_strong = {}
        for category, patterns in self.strong_ai_patterns.items():
            self.compiled_strong[category] = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in patterns]
        
        self.compiled_moderate = {}
        for category, patterns in self.moderate_ai_patterns.items():
            self.compiled_moderate[category] = [re.compile(p, re.MULTILINE) for p in patterns]
        
        self.compiled_weak = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in self.weak_ai_patterns]
        self.compiled_human = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in self.human_patterns]
    
    def _initialize_weights(self):
        """Initialize balanced scoring weights"""
        self.weights = {
            'strong_indicators': 0.5,    # Strong evidence of AI
            'moderate_indicators': 0.3,  # Moderate evidence
            'weak_indicators': 0.15,    # Weak evidence
            'consistency_bonus': 0.05,  # Consistency across file
            'human_penalty': -0.15      # Evidence of human patterns (reduced)
        }
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Balanced analysis of code content"""
        
        if not content.strip():
            return self._create_empty_analysis()
        
        lines = [line for line in content.split('\n') if line.strip()]
        total_lines = len(lines)
        
        if total_lines == 0:
            return self._create_empty_analysis()
        
        # Analyze different indicator levels
        strong_score = self._analyze_strong_indicators(content)
        moderate_score = self._analyze_moderate_indicators(content)
        weak_score = self._analyze_weak_indicators(content)
        consistency_score = self._analyze_consistency(content, lines)
        human_score = self._analyze_human_patterns(content)
        
        # Calculate weighted confidence
        base_confidence = (
            strong_score * self.weights['strong_indicators'] +
            moderate_score * self.weights['moderate_indicators'] +
            weak_score * self.weights['weak_indicators'] +
            consistency_score * self.weights['consistency_bonus']
        )
        
        # Apply human pattern penalty only when human patterns are very strong
        human_penalty = 0
        if human_score > 0.85:  # Only penalize when human patterns are overwhelming
            human_penalty = (human_score - 0.85) * self.weights['human_penalty']
        
        final_confidence = max(0.0, base_confidence + human_penalty)
        
        # Apply realistic thresholds
        final_confidence = self._apply_realistic_thresholds(final_confidence, total_lines)
        
        # Risk assessment
        risk_level = self._calculate_balanced_risk(final_confidence, strong_score, moderate_score)
        
        # Estimated AI lines
        estimated_ai_lines = int(total_lines * final_confidence) if final_confidence > 0.05 else 0
        
        return {
            'confidence_score': final_confidence,
            'estimated_lines': estimated_ai_lines,
            'total_analyzed_lines': total_lines,
            'risk_level': risk_level,
            'language': self._detect_language(file_extension),
            'indicators': {
                'strong_ai_patterns': strong_score > 0.3,
                'moderate_ai_patterns': moderate_score > 0.3,
                'weak_ai_patterns': weak_score > 0.3,
                'high_consistency': consistency_score > 0.6,
                'human_patterns_detected': human_score > 0.3
            },
            'detailed_scores': {
                'strong_indicators': strong_score,
                'moderate_indicators': moderate_score,
                'weak_indicators': weak_score,
                'consistency_score': consistency_score,
                'human_patterns': human_score,
                'base_confidence': base_confidence,
                'human_penalty_applied': human_penalty
            },
            'analysis_explanation': self._generate_explanation(
                final_confidence, strong_score, moderate_score, weak_score, human_score
            )
        }
    
    def _analyze_strong_indicators(self, content: str) -> float:
        """Analyze strong AI indicators"""
        total_matches = 0
        max_possible = 0
        
        for category, patterns in self.compiled_strong.items():
            category_matches = 0
            for pattern in patterns:
                if pattern.search(content):
                    category_matches += 1
            
            total_matches += min(category_matches, 2)  # Cap per category
            max_possible += 2
        
        return total_matches / max_possible if max_possible > 0 else 0.0
    
    def _analyze_moderate_indicators(self, content: str) -> float:
        """Analyze moderate AI indicators"""
        total_matches = 0
        max_possible = 0
        
        for category, patterns in self.compiled_moderate.items():
            category_matches = 0
            for pattern in patterns:
                matches = pattern.findall(content)
                category_matches += len(matches)
            
            # Normalize by content length
            normalized_matches = min(category_matches / (len(content.split('\n')) / 10), 1.0)
            total_matches += normalized_matches
            max_possible += 1
        
        return total_matches / max_possible if max_possible > 0 else 0.0
    
    def _analyze_weak_indicators(self, content: str) -> float:
        """Analyze weak AI indicators"""
        matches = 0
        for pattern in self.compiled_weak:
            matches += len(pattern.findall(content))
        
        # Normalize by file size
        lines = len(content.split('\n'))
        return min(matches / (lines / 20), 1.0)  # At most 1 match per 20 lines = 100%
    
    def _analyze_consistency(self, content: str, lines: List[str]) -> float:
        """Analyze code consistency (AI tends to be very consistent)"""
        
        # Check indentation consistency
        indentations = []
        for line in lines:
            if line.strip():
                indentations.append(len(line) - len(line.lstrip()))
        
        indentation_consistency = self._calculate_indentation_consistency(indentations)
        
        # Check naming consistency
        function_names = re.findall(r'def\s+(\w+)\(', content)
        variable_names = re.findall(r'\b([a-z_][a-z0-9_]*)\s*=', content)
        
        naming_consistency = self._calculate_naming_consistency(function_names + variable_names)
        
        # Check comment consistency
        comments = re.findall(r'#\s*(.+)$', content, re.MULTILINE)
        comment_consistency = self._calculate_comment_consistency(comments)
        
        return (indentation_consistency + naming_consistency + comment_consistency) / 3
    
    def _analyze_human_patterns(self, content: str) -> float:
        """Analyze patterns typical of human-written code"""
        matches = 0
        for pattern in self.compiled_human:
            matches += len(pattern.findall(content))
        
        # Normalize by content length
        lines = len(content.split('\n'))
        return min(matches / (lines / 30), 1.0)  # Human patterns are less frequent
    
    def _apply_realistic_thresholds(self, confidence: float, total_lines: int) -> float:
        """Apply realistic thresholds based on file characteristics"""
        
        # Very small files are harder to classify accurately
        if total_lines < 20:
            confidence *= 0.5
        elif total_lines < 50:
            confidence *= 0.7
        
        # For files without explicit AI markers, apply moderate scaling but don't over-restrict
        if confidence > 0.25 and total_lines > 30:
            # Scale down but allow higher confidence for strong patterns
            confidence = min(confidence * 0.75, 0.40)  # Allow up to 40% for strong AI patterns
        
        # Apply minimum threshold - anything below 5% is likely noise
        if confidence < 0.05:
            confidence = 0.0
        
        # Only allow very high confidence with clear indicators
        if confidence > 0.6:
            confidence = 0.6 + (confidence - 0.6) * 0.5  # Compress very high values
        
        return min(max(confidence, 0.0), 0.75)  # Cap at 75%
    
    def _calculate_balanced_risk(self, confidence: float, strong_score: float, moderate_score: float) -> str:
        """Calculate balanced risk assessment"""
        
        if strong_score > 0.5 or confidence > 0.7:
            return "HIGH"
        elif strong_score > 0.2 or moderate_score > 0.5 or confidence > 0.4:
            return "MEDIUM"
        elif moderate_score > 0.2 or confidence > 0.15:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _calculate_indentation_consistency(self, indentations: List[int]) -> float:
        """Calculate indentation consistency"""
        if len(indentations) <= 1:
            return 1.0
        
        # Check for consistent step size
        unique_indents = sorted(set(indentations))
        if len(unique_indents) > 1:
            steps = [unique_indents[i+1] - unique_indents[i] for i in range(len(unique_indents)-1)]
            if len(set(steps)) == 1:  # All steps are the same
                return 1.0
        
        # Calculate based on variance
        variance = statistics.variance(indentations) if len(indentations) > 1 else 0
        max_indent = max(indentations) if indentations else 1
        
        return max(0.0, 1.0 - (variance / (max_indent + 1)))
    
    def _calculate_naming_consistency(self, names: List[str]) -> float:
        """Calculate naming convention consistency"""
        if not names:
            return 0.5  # Neutral
        
        snake_case = sum(1 for name in names if '_' in name and name.islower())
        camel_case = sum(1 for name in names if name != name.lower() and '_' not in name)
        
        total = len(names)
        max_convention = max(snake_case, camel_case)
        
        return max_convention / total if total > 0 else 0.5
    
    def _calculate_comment_consistency(self, comments: List[str]) -> float:
        """Calculate comment style consistency"""
        if not comments:
            return 0.5  # Neutral
        
        # Check for consistent comment capitalization
        capitalized = sum(1 for comment in comments if comment.strip() and comment.strip()[0].isupper())
        lowercase = sum(1 for comment in comments if comment.strip() and comment.strip()[0].islower())
        
        total = len(comments)
        max_style = max(capitalized, lowercase)
        
        return max_style / total if total > 0 else 0.5
    
    def _generate_explanation(self, confidence: float, strong: float, moderate: float, 
                            weak: float, human: float) -> List[str]:
        """Generate human-readable explanation"""
        explanations = []
        
        if confidence > 0.6:
            explanations.append(f"High confidence ({confidence:.1%}) of AI assistance")
        elif confidence > 0.3:
            explanations.append(f"Moderate confidence ({confidence:.1%}) of AI assistance")
        elif confidence > 0.1:
            explanations.append(f"Low confidence ({confidence:.1%}) of AI assistance")
        else:
            explanations.append("Appears to be primarily human-written")
        
        if strong > 0.3:
            explanations.append("Strong AI patterns detected (documentation style, perfect structure)")
        if moderate > 0.3:
            explanations.append("Moderate AI patterns detected (consistent naming, modern syntax)")
        if weak > 0.3:
            explanations.append("Weak AI indicators present (TODO comments, standard patterns)")
        if human > 0.3:
            explanations.append("Human coding patterns detected (informal style, shortcuts)")
        
        return explanations
    
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
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis result"""
        return {
            'confidence_score': 0.0,
            'estimated_lines': 0,
            'total_analyzed_lines': 0,
            'risk_level': 'MINIMAL',
            'language': 'unknown',
            'indicators': {
                'strong_ai_patterns': False,
                'moderate_ai_patterns': False,
                'weak_ai_patterns': False,
                'high_consistency': False,
                'human_patterns_detected': False
            },
            'detailed_scores': {
                'strong_indicators': 0.0,
                'moderate_indicators': 0.0,
                'weak_indicators': 0.0,
                'consistency_score': 0.0,
                'human_patterns': 0.0,
                'base_confidence': 0.0,
                'human_penalty_applied': 0.0
            },
            'analysis_explanation': ["Empty file - no analysis possible"]
        }