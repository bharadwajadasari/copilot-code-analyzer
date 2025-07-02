"""
Realistic Copilot Detection Engine
Designed to detect 2-5% AI usage patterns typical of real-world development
"""

import re
import statistics
from typing import Dict, Any, List

class RealisticCopilotDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.config = indicators_config
        self._initialize_patterns()
        self._initialize_weights()
    
    def _initialize_patterns(self):
        """Initialize patterns focused on realistic AI detection"""
        
        # Explicit markers - only these get high confidence
        self.explicit_markers = [
            r'#.*[Cc]ode [Gg]enerated by [Cc]opilot',
            r'#.*[Gg]enerated by [Cc]opilot',
            r'#.*[Cc]opilot [Gg]enerated',
            r'#.*[Aa][Ii][-\s]*[Gg]enerated',
            r'//.*[Cc]opilot',
            r'@generated'
        ]
        
        # Subtle AI patterns - low confidence indicators
        self.subtle_patterns = [
            r'def\s+\w+\(.*\)\s*->\s*[A-Z]\w*:',  # Perfect type hints
            r'from\s+typing\s+import.*Optional.*Union',  # Heavy typing imports
            r'"""[\s\S]{100,}?Args:[\s\S]*?Returns:[\s\S]*?"""',  # Perfect docstrings
            r'try:\s*\n.*?\nexcept\s+\w+Exception\s+as\s+\w+:',  # Standard exception handling
        ]
        
        # Compile patterns
        self.compiled_explicit = [re.compile(p, re.IGNORECASE) for p in self.explicit_markers]
        self.compiled_subtle = [re.compile(p, re.MULTILINE | re.DOTALL) for p in self.subtle_patterns]
    
    def _initialize_weights(self):
        """Initialize realistic weights"""
        self.weights = {
            'explicit_markers': 0.8,  # High weight for explicit markers
            'subtle_patterns': 0.1,   # Very low weight for subtle patterns
            'length_bonus': 0.05,     # Small bonus for longer files
            'consistency_bonus': 0.05  # Small bonus for consistency
        }
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Realistic analysis focused on 2-5% detection rates"""
        
        if not content.strip():
            return self._create_empty_analysis()
        
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Check for explicit markers first
        explicit_score = self._analyze_explicit_markers(content)
        
        # Only check subtle patterns if no explicit markers
        subtle_score = 0
        if explicit_score == 0:
            subtle_score = self._analyze_subtle_patterns(content, code_lines)
        
        # Calculate final confidence
        confidence = (
            explicit_score * self.weights['explicit_markers'] +
            subtle_score * self.weights['subtle_patterns']
        )
        
        # Apply realistic thresholds
        confidence = self._apply_realistic_thresholds(confidence, total_lines, explicit_score > 0)
        
        # Risk assessment
        risk_level = self._calculate_risk_level(confidence, explicit_score > 0)
        
        # Estimated lines
        estimated_lines = int(total_lines * confidence) if confidence > 0.02 else 0
        
        return {
            'confidence_score': confidence,
            'estimated_lines': estimated_lines,
            'total_analyzed_lines': total_lines,
            'risk_level': risk_level,
            'language': self._detect_language(file_extension),
            'indicators': {
                'explicit_markers': explicit_score > 0,
                'subtle_patterns': subtle_score > 0.1,
                'file_complexity': code_lines > 50
            },
            'detailed_scores': {
                'explicit_markers': explicit_score,
                'subtle_patterns': subtle_score,
                'final_confidence': confidence
            },
            'analysis_explanation': self._generate_explanation(confidence, explicit_score, subtle_score)
        }
    
    def _analyze_explicit_markers(self, content: str) -> float:
        """Check for explicit AI generation markers"""
        marker_count = 0
        for pattern in self.compiled_explicit:
            marker_count += len(pattern.findall(content))
        
        return min(marker_count * 0.3, 1.0)  # Each marker adds 30%
    
    def _analyze_subtle_patterns(self, content: str, code_lines: int) -> float:
        """Check for subtle AI patterns with very low weight"""
        if code_lines < 10:
            return 0  # Too small to reliably detect
        
        pattern_matches = 0
        for pattern in self.compiled_subtle:
            pattern_matches += len(pattern.findall(content))
        
        # Normalize by code length and apply very conservative scaling
        normalized_score = min(pattern_matches / (code_lines / 20), 0.5)
        return normalized_score * 0.2  # Very low weight
    
    def _apply_realistic_thresholds(self, confidence: float, total_lines: int, has_explicit: bool) -> float:
        """Apply thresholds targeting 2-5% detection rates"""
        
        # Files with explicit markers can have higher confidence
        if has_explicit:
            return min(confidence, 0.95)
        
        # For files without explicit markers, be very conservative
        if total_lines < 30:
            confidence *= 0.3  # Very small files rarely show clear AI patterns
        elif total_lines < 100:
            confidence *= 0.5
        
        # Cap confidence for typical code patterns
        if confidence > 0.1:
            confidence = min(confidence * 0.4, 0.08)  # Cap at 8%
        
        # Apply noise threshold
        if confidence < 0.02:
            confidence = 0.0
        
        return confidence
    
    def _calculate_risk_level(self, confidence: float, has_explicit: bool) -> str:
        """Calculate risk level"""
        if has_explicit and confidence > 0.7:
            return "VERY HIGH"
        elif confidence > 0.3:
            return "HIGH"
        elif confidence > 0.05:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_explanation(self, confidence: float, explicit: float, subtle: float) -> List[str]:
        """Generate explanation for the analysis"""
        explanations = []
        
        if explicit > 0:
            explanations.append(f"Explicit AI markers detected ({explicit:.1%} confidence)")
        elif subtle > 0:
            explanations.append(f"Subtle AI patterns detected ({subtle:.1%} confidence)")
        else:
            explanations.append("No clear AI indicators found")
        
        if confidence > 0.05:
            explanations.append(f"Overall confidence: {confidence:.1%}")
        else:
            explanations.append("Confidence below detection threshold")
        
        return explanations
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust'
        }
        return extension_map.get(file_extension.lower(), 'unknown')
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis for empty files"""
        return {
            'confidence_score': 0.0,
            'estimated_lines': 0,
            'total_analyzed_lines': 0,
            'risk_level': 'MINIMAL',
            'language': 'unknown',
            'indicators': {
                'explicit_markers': False,
                'subtle_patterns': False,
                'file_complexity': False
            },
            'detailed_scores': {
                'explicit_markers': 0.0,
                'subtle_patterns': 0.0,
                'final_confidence': 0.0
            },
            'analysis_explanation': ['Empty or invalid file']
        }