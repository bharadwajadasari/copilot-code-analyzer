"""
Accurate AI Code Detection Engine
Properly identifies AI-generated code including modern AI assistants like Claude, GPT, etc.
"""

import re
from typing import Dict, Any, List

class AccurateAIDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.config = indicators_config
        self._initialize_ai_patterns()
        self._initialize_scoring()
    
    def _initialize_ai_patterns(self):
        """Initialize comprehensive AI detection patterns"""
        
        # Very strong AI indicators - almost certain AI generation
        self.strong_ai_indicators = [
            # Comprehensive documentation patterns
            r'"""[\s\S]{150,}?"""',  # Very long docstrings
            r'Args:\s*\n[\s\S]*?Returns:\s*\n[\s\S]*?"""',  # Perfect docstring format
            r'Attributes:\s*\n[\s\S]*?"""',  # Detailed attribute documentation
            r'Raises:\s*\n[\s\S]*?"""',  # Exception documentation
            
            # Perfect code structure patterns
            r'from\s+typing\s+import.*List.*Dict.*Optional.*Any',  # Heavy typing
            r'@dataclass\s*\nclass\s+\w+:',  # Modern Python patterns
            r'logger\s*=\s*logging\.getLogger\(__name__\)',  # Proper logging
            r'if\s+not\s+isinstance\([^)]+\):\s*\n\s*raise\s+ValueError',  # Type validation
            
            # AI-style error handling
            r'try:\s*\n[\s\S]*?except\s+Exception\s+as\s+\w+:\s*\n\s*logger\.',  # Perfect exception handling
            r'raise\s+ValueError\(f[\'"][^\'\"]*{[^}]+}[^\'\"]*[\'"]',  # F-string errors
            
            # AI naming patterns
            r'def\s+(get|set|calculate|process|validate|analyze|initialize)_[a-z_]+\(',  # Consistent naming
            r'class\s+[A-Z][a-zA-Z]+(?:Manager|Service|Handler|Processor|Analyzer|Detector):',  # AI class names
        ]
        
        # Moderate AI indicators
        self.moderate_ai_indicators = [
            # Modern Python features
            r'f[\'"][^\'\"]*{[^}]+}[^\'\"]*[\'"]',  # F-strings
            r'with\s+open\([^)]*\)\s+as\s+\w+:',  # Context managers
            r'List\[Dict\[str,\s*Any\]\]',  # Complex type hints
            r'Optional\[.*\]',  # Optional types
            
            # Consistent code style
            r'def\s+_[a-z_]+\(.*\)\s*->\s*\w+:',  # Private methods with type hints
            r'@staticmethod\s*\n\s*def',  # Static method usage
            r'@classmethod\s*\n\s*def',  # Class method usage
            
            # AI comment patterns
            r'#\s*[A-Z][^#\n]{30,}',  # Long, formal comments
            r'#\s*(Initialize|Calculate|Process|Validate|Check)',  # AI comment starters
        ]
        
        # Weak AI indicators
        self.weak_ai_indicators = [
            r'return\s+[A-Z_][A-Z0-9_]*\s+if\s+.*\s+else\s+[A-Z_][A-Z0-9_]*',  # Ternary with constants
            r'#\s*TODO:|#\s*FIXME:|#\s*NOTE:',  # Standard TODO comments
            r'super\(\)\.__init__\(',  # Modern super() usage
        ]
        
        # Human-style patterns (reduce AI confidence)
        self.human_indicators = [
            r'#\s*[a-z]',  # Lowercase comment starts
            r'\b(wtf|damn|shit|crap|hack|quick\s*fix)\b',  # Informal language
            r'\w{1,2}\s*=\s*\w{1,2}',  # Very short variable names
            r'def\s+[a-z]{1,3}\(',  # Very short function names
            r'print\([\'"].*[\'\"]\)',  # Debug prints
        ]
        
        # Compile patterns
        self.compiled_strong = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in self.strong_ai_indicators]
        self.compiled_moderate = [re.compile(p, re.MULTILINE) for p in self.moderate_ai_indicators]
        self.compiled_weak = [re.compile(p, re.MULTILINE) for p in self.weak_ai_indicators]
        self.compiled_human = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in self.human_indicators]
    
    def _initialize_scoring(self):
        """Initialize scoring weights"""
        self.weights = {
            'strong': 0.6,      # Strong indicators
            'moderate': 0.3,    # Moderate indicators  
            'weak': 0.1,        # Weak indicators
            'human_penalty': 0.2  # Human pattern penalty
        }
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Analyze content for AI-generated code patterns"""
        
        if not content.strip():
            return self._create_empty_analysis()
        
        lines = content.split('\n')
        total_lines = len([line for line in lines if line.strip()])
        
        # Calculate pattern scores
        strong_score = self._calculate_pattern_score(content, self.compiled_strong)
        moderate_score = self._calculate_pattern_score(content, self.compiled_moderate)
        weak_score = self._calculate_pattern_score(content, self.compiled_weak)
        human_score = self._calculate_pattern_score(content, self.compiled_human)
        
        # Calculate base confidence using weighted scoring
        base_confidence = (
            strong_score * self.weights['strong'] +
            moderate_score * self.weights['moderate'] +
            weak_score * self.weights['weak']
        )
        
        # Apply human penalty only for very obvious human patterns
        human_penalty = min(human_score * self.weights['human_penalty'], 0.3)
        
        # Final confidence score
        confidence = max(0.0, min(1.0, base_confidence - human_penalty))
        
        # Apply file size adjustments
        if total_lines < 20:
            confidence *= 0.7  # Reduce confidence for very small files
        elif total_lines > 200:
            confidence *= 1.2  # Increase confidence for large, well-structured files
            confidence = min(confidence, 1.0)
        
        # Risk assessment
        risk_level = self._calculate_risk_level(confidence)
        
        # Estimated AI lines
        estimated_ai_lines = int(total_lines * confidence) if confidence > 0.05 else 0
        
        return {
            'confidence_score': confidence,
            'estimated_lines': estimated_ai_lines,
            'total_analyzed_lines': total_lines,
            'risk_level': risk_level,
            'language': self._detect_language(file_extension),
            'indicators': {
                'strong_ai_patterns': strong_score > 0.3,
                'moderate_ai_patterns': moderate_score > 0.3,
                'weak_ai_patterns': weak_score > 0.3,
                'human_patterns_detected': human_score > 0.3
            },
            'detailed_scores': {
                'strong_indicators': strong_score,
                'moderate_indicators': moderate_score,
                'weak_indicators': weak_score,
                'human_patterns': human_score,
                'base_confidence': base_confidence,
                'human_penalty_applied': human_penalty
            },
            'analysis_explanation': self._generate_explanation(confidence, strong_score, moderate_score, human_score)
        }
    
    def _calculate_pattern_score(self, content: str, compiled_patterns: List) -> float:
        """Calculate score for a set of patterns"""
        matches = 0
        for pattern in compiled_patterns:
            if pattern.search(content):
                matches += 1
        
        # Normalize by number of patterns
        return min(matches / len(compiled_patterns), 1.0) if compiled_patterns else 0.0
    
    def _calculate_risk_level(self, confidence: float) -> str:
        """Calculate risk level based on confidence"""
        if confidence >= 0.7:
            return "VERY HIGH"
        elif confidence >= 0.5:
            return "HIGH"
        elif confidence >= 0.3:
            return "MEDIUM"
        elif confidence >= 0.1:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_explanation(self, confidence: float, strong: float, moderate: float, human: float) -> List[str]:
        """Generate human-readable explanation"""
        explanations = []
        
        if confidence >= 0.7:
            explanations.append(f"Very high confidence ({confidence:.1%}) of AI generation")
        elif confidence >= 0.5:
            explanations.append(f"High confidence ({confidence:.1%}) of AI assistance")
        elif confidence >= 0.3:
            explanations.append(f"Moderate confidence ({confidence:.1%}) of AI assistance")
        elif confidence >= 0.1:
            explanations.append(f"Low confidence ({confidence:.1%}) of AI assistance")
        else:
            explanations.append("Appears to be primarily human-written")
        
        if strong > 0.3:
            explanations.append("Strong AI patterns detected (perfect documentation, error handling)")
        if moderate > 0.3:
            explanations.append("Moderate AI patterns detected (consistent naming, modern syntax)")
        if human > 0.3:
            explanations.append("Some human coding patterns detected")
        
        return explanations
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust'
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
                'human_patterns_detected': False
            },
            'detailed_scores': {
                'strong_indicators': 0.0,
                'moderate_indicators': 0.0,
                'weak_indicators': 0.0,
                'human_patterns': 0.0,
                'base_confidence': 0.0,
                'human_penalty_applied': 0.0
            },
            'analysis_explanation': ['Empty file or no analyzable content']
        }