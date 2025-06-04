"""
Conservative Copilot Detection Engine
Ultra-conservative approach that only flags obvious AI-generated code patterns.
Designed to minimize false positives for real-world human code analysis.
"""

import re
import ast
from typing import Dict, List, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ConservativeCopilotDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.config = indicators_config
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize very conservative detection patterns"""
        
        # Only detect EXPLICIT AI generation markers
        self.explicit_ai_markers = [
            r'@generated\s*$',  # Explicit generated marker
            r'#\s*@generated\s*$',  # Python generated comment
            r'//\s*@generated\s*$',  # JS/Java generated comment
            r'/\*\s*@generated\s*\*/',  # Block generated comment
            r'This\s+code\s+was\s+generated\s+by',  # Explicit generation statement
            r'Auto-generated\s+by',  # Auto-generation statement
            r'Generated\s+on\s+\d{4}-\d{2}-\d{2}',  # Date-stamped generation
        ]
        
        # Ultra-specific AI code signatures (very rare patterns)
        self.ai_signatures = [
            # Perfect template-like code with exact patterns
            r'def\s+\w+\(.*\)\s*->\s*Optional\[.*\]:\s*\n\s*""".+?"""\s*\n\s*try:\s*\n.+?\n\s*except\s+\w+Exception\s+as\s+e:\s*\n\s*logger\.error\(f".+?{e}"\)\s*\n\s*return\s+None\s*\n\s*finally:',
            # Very specific AI comment patterns
            r'#\s*TODO:\s*Implement\s+proper\s+error\s+handling\s*$',
            r'#\s*FIXME:\s*This\s+is\s+a\s+placeholder\s+implementation\s*$',
        ]
        
        # Compile patterns
        self.compiled_explicit = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in self.explicit_ai_markers]
        self.compiled_signatures = [re.compile(p, re.MULTILINE | re.DOTALL) for p in self.ai_signatures]
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Ultra-conservative analysis - only flag obvious AI generation"""
        
        if not content.strip():
            return self._create_empty_analysis()
        
        lines = [line for line in content.split('\n') if line.strip()]
        total_lines = len(lines)
        
        if total_lines == 0:
            return self._create_empty_analysis()
        
        # Check for explicit AI markers
        explicit_markers = self._count_explicit_markers(content)
        
        # Check for AI signatures
        signature_matches = self._count_signature_matches(content)
        
        # Ultra-conservative scoring
        confidence_score = 0.0
        
        # Only flag if we find explicit markers
        if explicit_markers > 0:
            confidence_score = min(explicit_markers * 0.3, 0.9)  # Max 90% even with multiple markers
        
        # Slight boost for AI signatures, but very conservative
        if signature_matches > 0:
            confidence_score += min(signature_matches * 0.1, 0.2)  # Max 20% boost
        
        # Cap at 95% - never 100% certain
        confidence_score = min(confidence_score, 0.95)
        
        # Risk assessment
        risk_level = self._calculate_conservative_risk(confidence_score, explicit_markers, signature_matches)
        
        # Estimated AI lines - very conservative
        estimated_ai_lines = 0
        if confidence_score > 0.7:  # Only count lines if high confidence
            estimated_ai_lines = int(total_lines * confidence_score * 0.5)  # Further reduce estimate
        
        return {
            'confidence_score': confidence_score,
            'estimated_lines': estimated_ai_lines,
            'total_analyzed_lines': total_lines,
            'risk_level': risk_level,
            'language': self._detect_language(file_extension),
            'indicators': {
                'explicit_ai_markers': explicit_markers > 0,
                'ai_signatures_detected': signature_matches > 0,
                'high_confidence_ai': confidence_score > 0.8,
                'moderate_confidence_ai': 0.5 < confidence_score <= 0.8,
                'low_confidence_ai': 0.2 < confidence_score <= 0.5
            },
            'detailed_scores': {
                'explicit_markers': explicit_markers,
                'signature_matches': signature_matches,
                'total_markers_found': explicit_markers + signature_matches,
                'confidence_from_markers': min(explicit_markers * 0.3, 0.9),
                'confidence_from_signatures': min(signature_matches * 0.1, 0.2)
            },
            'analysis_notes': self._generate_analysis_notes(explicit_markers, signature_matches, confidence_score)
        }
    
    def _count_explicit_markers(self, content: str) -> int:
        """Count explicit AI generation markers"""
        count = 0
        for pattern in self.compiled_explicit:
            matches = pattern.findall(content)
            count += len(matches)
        return count
    
    def _count_signature_matches(self, content: str) -> int:
        """Count AI code signature matches"""
        count = 0
        for pattern in self.compiled_signatures:
            if pattern.search(content):
                count += 1
        return count
    
    def _calculate_conservative_risk(self, confidence: float, explicit_markers: int, signatures: int) -> str:
        """Conservative risk assessment"""
        
        if explicit_markers > 2 or confidence > 0.8:
            return "HIGH"
        elif explicit_markers > 0 or confidence > 0.5:
            return "MEDIUM"  
        elif signatures > 0 or confidence > 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_analysis_notes(self, explicit_markers: int, signatures: int, confidence: float) -> List[str]:
        """Generate human-readable analysis notes"""
        notes = []
        
        if explicit_markers > 0:
            notes.append(f"Found {explicit_markers} explicit AI generation marker(s)")
        
        if signatures > 0:
            notes.append(f"Detected {signatures} potential AI code signature(s)")
        
        if confidence > 0.8:
            notes.append("High confidence of AI generation based on explicit markers")
        elif confidence > 0.5:
            notes.append("Moderate confidence of AI assistance based on patterns")
        elif confidence > 0.2:
            notes.append("Low confidence - may have some AI assistance")
        else:
            notes.append("Appears to be primarily human-written code")
        
        if explicit_markers == 0 and signatures == 0:
            notes.append("No clear AI generation markers found")
        
        return notes
    
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
        """Create empty analysis result for empty files"""
        return {
            'confidence_score': 0.0,
            'estimated_lines': 0,
            'total_analyzed_lines': 0,
            'risk_level': 'MINIMAL',
            'language': 'unknown',
            'indicators': {
                'explicit_ai_markers': False,
                'ai_signatures_detected': False,
                'high_confidence_ai': False,
                'moderate_confidence_ai': False,
                'low_confidence_ai': False
            },
            'detailed_scores': {
                'explicit_markers': 0,
                'signature_matches': 0,
                'total_markers_found': 0,
                'confidence_from_markers': 0.0,
                'confidence_from_signatures': 0.0
            },
            'analysis_notes': ["Empty file - no analysis possible"]
        }