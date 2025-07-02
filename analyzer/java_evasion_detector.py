"""
Java-Specific Evasion-Resistant AI Code Detection
Handles Java formatting tools like Spotless, Google Java Format, and IDE refactoring
"""

import re
import ast
import json
from typing import Dict, List, Any, Set, Tuple, Optional
from collections import Counter, defaultdict
import statistics

class JavaEvasionDetector:
    def __init__(self, indicators_config: Dict[str, Any]):
        self.config = indicators_config
        self._initialize_java_patterns()
        self._initialize_java_semantics()
        self._initialize_weights()
    
    def _initialize_java_patterns(self):
        """Initialize Java-specific AI detection patterns"""
        
        # Java semantic patterns that survive formatting
        self.java_semantic_patterns = {
            'ai_exception_handling': [
                r'try\s*\{[^}]*\}\s*catch\s*\(\s*Exception\s+\w+\s*\)\s*\{[^}]*\}',  # Generic exception catching
                r'catch\s*\(\s*Exception\s+e\s*\)\s*\{\s*e\.printStackTrace\(\)\s*;\s*\}',  # AI-style exception printing
                r'try\s*\{[^}]*\}\s*catch\s*\([^)]+\)\s*\{\s*//\s*(?:TODO|FIXME)',  # AI placeholder comments
                r'throws\s+Exception\s*(?:,\s*\w+Exception)*',  # AI generic throws declarations
            ],
            
            'ai_method_patterns': [
                r'public\s+(?:static\s+)?(?:void|[\w<>]+)\s+\w+\([^)]*\)\s+throws\s+Exception',  # AI method signatures
                r'private\s+(?:static\s+)?(?:void|[\w<>]+)\s+validate\w+\([^)]*\)',  # AI validation methods
                r'public\s+(?:static\s+)?boolean\s+is\w+\([^)]*\)',  # AI predicate methods
                r'public\s+(?:static\s+)?void\s+set\w+\([^)]*\)',  # AI setter patterns
                r'public\s+(?:static\s+)?[\w<>]+\s+get\w+\(\s*\)',  # AI getter patterns
            ],
            
            'ai_null_checking': [
                r'if\s*\(\s*\w+\s*!=\s*null\s*&&\s*\w+\.[^)]+\)',  # AI null checks with method calls
                r'if\s*\(\s*\w+\s*!=\s*null\s*&&\s*!\w+\.isEmpty\(\)\s*\)',  # AI null and empty checks
                r'Objects\.nonNull\(\w+\)\s*&&',  # AI Objects.nonNull usage
                r'Optional\.ofNullable\([^)]+\)\.isPresent\(\)',  # AI Optional patterns
            ],
            
            'ai_collection_patterns': [
                r'new\s+ArrayList<[^>]*>\(\s*\)',  # AI ArrayList initialization
                r'new\s+HashMap<[^>]*>\(\s*\)',  # AI HashMap initialization
                r'\.stream\(\)\.filter\([^)]+\)\.collect\([^)]+\)',  # AI stream patterns
                r'\.forEach\(\w+\s*->\s*\{[^}]*\}\)',  # AI lambda forEach
            ],
            
            'ai_string_patterns': [
                r'String\.format\([^)]+\)',  # AI String.format usage
                r'StringBuilder\s+\w+\s*=\s*new\s+StringBuilder\(\)',  # AI StringBuilder patterns
                r'\.toString\(\)\.trim\(\)',  # AI method chaining
                r'\.equals\(\s*"[^"]*"\s*\)',  # AI string literal comparisons
            ]
        }
        
        # Java-specific code structure patterns
        self.java_structure_patterns = {
            'ai_class_organization': [
                r'public\s+class\s+\w+\s*\{[\s\S]*?private\s+static\s+final',  # AI constant organization
                r'public\s+static\s+void\s+main\([^)]*\)[\s\S]*?System\.out\.println',  # AI main method patterns
                r'@Override\s*\n\s*public\s+(?:boolean\s+equals|int\s+hashCode|String\s+toString)',  # AI override patterns
            ],
            
            'ai_annotation_usage': [
                r'@Autowired\s*\n\s*private\s+\w+\s+\w+;',  # AI dependency injection
                r'@RequestMapping\([^)]*\)\s*\n\s*public\s+\w+',  # AI Spring annotations
                r'@Test\s*\n\s*public\s+void\s+test\w+\(\s*\)',  # AI test method patterns
                r'@Service\s*\n\s*public\s+class',  # AI service annotations
            ]
        }
    
    def _initialize_java_semantics(self):
        """Initialize Java semantic analysis patterns"""
        
        # Java complexity indicators
        self.java_complexity = {
            'method_complexity': {
                'ai_range': (5, 12),  # AI methods tend to be moderately complex
                'human_range': (1, 25)  # Humans have wider variance
            },
            
            'class_size': {
                'ai_pattern': (50, 200),  # AI classes tend to be medium-sized
                'human_pattern': (10, 500)  # Humans vary more widely
            },
            
            'inheritance_depth': {
                'ai_preference': 1,  # AI rarely uses deep inheritance
                'human_tolerance': 3  # Humans may use deeper hierarchies
            }
        }
        
        # Java naming conventions
        self.java_naming_patterns = {
            'ai_naming_indicators': [
                r'\b(?:data|result|response|output|input|value)\d*\b',  # AI generic names
                r'\b(?:temp|tmp)(?:[A-Z]\w*|\d+)\b',  # AI temporary variables
                r'\b(?:item|element|obj|object)\d*\b',  # AI generic object names
                r'\b(?:list|map|set)(?:[A-Z]\w*)?\b',  # AI collection names
            ],
            
            'ai_method_naming': [
                r'\b(?:process|handle|execute|perform|validate|check)\w*\b',  # AI action verbs
                r'\b(?:is|has|can|should)\w+\b',  # AI predicate naming
                r'\b(?:create|build|generate|construct)\w*\b',  # AI factory methods
                r'\b(?:convert|transform|parse|format)\w*\b',  # AI transformation methods
            ]
        }
        
        # Java API usage patterns
        self.java_api_patterns = {
            'ai_preferred_apis': [
                r'java\.util\.(?:List|Map|Set|Collection)',  # AI collection preferences
                r'java\.util\.stream\.(?:Stream|Collectors)',  # AI stream API usage
                r'java\.util\.Optional',  # AI Optional usage
                r'java\.time\.(?:LocalDate|LocalDateTime|Instant)',  # AI modern time API
                r'java\.nio\.file\.(?:Files|Paths)',  # AI NIO usage
            ],
            
            'ai_exception_preferences': [
                r'IllegalArgumentException',  # AI common exceptions
                r'IllegalStateException',
                r'UnsupportedOperationException',
                r'RuntimeException',
            ]
        }
    
    def _initialize_weights(self):
        """Initialize Java-specific scoring weights"""
        self.weights = {
            'semantic_patterns': 0.25,
            'structure_patterns': 0.20,
            'complexity_analysis': 0.15,
            'naming_conventions': 0.15,
            'api_usage_patterns': 0.15,
            'formatting_resistance': 0.10
        }
    
    def analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Analyze Java content with evasion-resistant techniques"""
        
        if file_extension != '.java':
            return self._create_empty_analysis()
        
        # Normalize Java code (remove formatting variations)
        normalized_content = self._normalize_java_code(content)
        
        # Multi-layer Java analysis
        semantic_score = self._analyze_java_semantics(normalized_content)
        structure_score = self._analyze_java_structure(normalized_content)
        complexity_score = self._analyze_java_complexity(content)
        naming_score = self._analyze_java_naming(normalized_content)
        api_score = self._analyze_java_api_usage(normalized_content)
        formatting_score = self._analyze_formatting_resistance(content, normalized_content)
        
        # Calculate weighted confidence
        confidence = (
            semantic_score * self.weights['semantic_patterns'] +
            structure_score * self.weights['structure_patterns'] +
            complexity_score * self.weights['complexity_analysis'] +
            naming_score * self.weights['naming_conventions'] +
            api_score * self.weights['api_usage_patterns'] +
            formatting_score * self.weights['formatting_resistance']
        )
        
        # Detect Java-specific evasion attempts
        evasion_indicators = self._detect_java_evasion(content, normalized_content)
        
        return {
            'copilot_confidence': confidence,
            'risk_level': self._calculate_risk_level(confidence),
            'language': 'java',
            'java_analysis': {
                'semantic_score': semantic_score,
                'structure_score': structure_score,
                'complexity_score': complexity_score,
                'naming_score': naming_score,
                'api_score': api_score,
                'formatting_score': formatting_score
            },
            'evasion_resistance': {
                'evasion_detected': len(evasion_indicators) > 0,
                'evasion_indicators': evasion_indicators,
                'java_specific_patterns': self._get_java_pattern_summary(content)
            },
            'explanation': self._generate_java_explanation(confidence, semantic_score, structure_score, evasion_indicators)
        }
    
    def _normalize_java_code(self, content: str) -> str:
        """Normalize Java code to remove formatting variations"""
        # Remove excessive whitespace while preserving structure
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                # Normalize common Java formatting variations
                normalized = stripped
                # Normalize brace styles
                normalized = re.sub(r'\s*\{\s*', ' { ', normalized)
                normalized = re.sub(r'\s*\}\s*', ' } ', normalized)
                # Normalize method calls
                normalized = re.sub(r'\s*\(\s*', '(', normalized)
                normalized = re.sub(r'\s*\)\s*', ') ', normalized)
                # Normalize semicolons
                normalized = re.sub(r'\s*;\s*', '; ', normalized)
                
                normalized_lines.append(normalized.strip())
        
        return '\n'.join(normalized_lines)
    
    def _analyze_java_semantics(self, content: str) -> float:
        """Analyze Java semantic patterns"""
        total_score = 0.0
        pattern_count = 0
        
        for category, patterns in self.java_semantic_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                if matches:
                    total_score += min(len(matches) * 0.2, 0.8)  # Cap individual pattern contribution
                pattern_count += 1
        
        return min(total_score / max(pattern_count, 1), 1.0)
    
    def _analyze_java_structure(self, content: str) -> float:
        """Analyze Java code structure patterns"""
        structure_score = 0.0
        
        # Analyze class organization
        class_matches = re.findall(r'public\s+class\s+\w+', content)
        if class_matches:
            # Check for AI-typical class structure
            for category, patterns in self.java_structure_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                        structure_score += 0.15
        
        return min(structure_score, 1.0)
    
    def _analyze_java_complexity(self, content: str) -> float:
        """Analyze Java complexity patterns"""
        # Count methods
        method_matches = re.findall(r'(?:public|private|protected)\s+(?:static\s+)?(?:void|\w+)\s+\w+\s*\([^)]*\)', content)
        
        if not method_matches:
            return 0.0
        
        # Analyze method complexity (simplified)
        total_complexity = 0
        for method_match in method_matches:
            # Count decision points in method vicinity
            method_complexity = 1  # Base complexity
            method_complexity += len(re.findall(r'\b(?:if|while|for|switch|catch)\b', method_match))
            total_complexity += method_complexity
        
        avg_complexity = total_complexity / len(method_matches)
        
        # AI tends to have moderate, consistent complexity
        if 5 <= avg_complexity <= 12:
            return 0.8  # High AI likelihood
        elif avg_complexity < 3:
            return 0.3  # Too simple for AI
        else:
            return 0.2  # Too complex for typical AI
    
    def _analyze_java_naming(self, content: str) -> float:
        """Analyze Java naming convention patterns"""
        naming_score = 0.0
        
        # Extract variable and method names
        variable_names = re.findall(r'\b[a-z][a-zA-Z0-9]*\b', content)
        method_names = re.findall(r'(?:public|private|protected)\s+(?:static\s+)?(?:void|\w+)\s+(\w+)\s*\(', content)
        
        total_names = len(set(variable_names + method_names))
        ai_name_count = 0
        
        if total_names == 0:
            return 0.0
        
        # Check for AI naming patterns
        all_names = variable_names + method_names
        for category, patterns in self.java_naming_patterns.items():
            for pattern in patterns:
                ai_matches = [name for name in all_names if re.match(pattern, name)]
                ai_name_count += len(ai_matches)
        
        naming_score = min(ai_name_count / total_names, 1.0)
        return naming_score
    
    def _analyze_java_api_usage(self, content: str) -> float:
        """Analyze Java API usage patterns"""
        api_score = 0.0
        
        # Check for AI-preferred APIs
        for api_pattern in self.java_api_patterns['ai_preferred_apis']:
            if re.search(api_pattern, content):
                api_score += 0.15
        
        # Check exception usage patterns
        for exception_pattern in self.java_api_patterns['ai_exception_preferences']:
            if re.search(exception_pattern, content):
                api_score += 0.1
        
        return min(api_score, 1.0)
    
    def _analyze_formatting_resistance(self, original: str, normalized: str) -> float:
        """Analyze resistance to Java formatting tools"""
        # Check if original code shows signs of formatter processing
        formatting_indicators = 0
        
        # Check for consistent indentation (formatter characteristic)
        lines = original.split('\n')
        indent_pattern = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_pattern.append(indent)
        
        if len(indent_pattern) > 5:
            # Check for consistent indentation increments (formatter sign)
            indent_diffs = [indent_pattern[i+1] - indent_pattern[i] for i in range(len(indent_pattern)-1)]
            consistent_indents = len([diff for diff in indent_diffs if abs(diff) in [0, 2, 4]])
            if consistent_indents / len(indent_diffs) > 0.8:
                formatting_indicators += 1
        
        # Check for consistent brace style
        open_braces = len(re.findall(r'\{\s*$', original, re.MULTILINE))
        total_braces = len(re.findall(r'\{', original))
        if total_braces > 0 and open_braces / total_braces > 0.8:
            formatting_indicators += 1
        
        # Return score based on formatting evidence
        return min(formatting_indicators * 0.3, 1.0)
    
    def _detect_java_evasion(self, original: str, normalized: str) -> List[str]:
        """Detect Java-specific evasion attempts"""
        evasion_indicators = []
        
        # Check for IDE refactoring patterns
        if self._detect_variable_renaming_pattern(original):
            evasion_indicators.append('systematic_variable_renaming')
        
        # Check for import optimization (common in Java IDEs)
        import_lines = [line for line in original.split('\n') if line.strip().startswith('import')]
        if len(import_lines) > 10:
            # Check for alphabetical ordering (IDE auto-organization)
            import_names = [line.split()[-1].rstrip(';') for line in import_lines]
            if import_names == sorted(import_names):
                evasion_indicators.append('ide_import_organization')
        
        # Check for method extraction patterns
        method_count = len(re.findall(r'private\s+(?:static\s+)?(?:void|\w+)\s+\w+\s*\([^)]*\)', original))
        total_lines = len([line for line in original.split('\n') if line.strip()])
        
        if total_lines > 50 and method_count / (total_lines / 10) > 1.5:
            evasion_indicators.append('excessive_method_extraction')
        
        # Check for formatter-specific patterns
        if self._detect_java_formatter_signature(original):
            evasion_indicators.append('java_formatter_processing')
        
        return evasion_indicators
    
    def _detect_variable_renaming_pattern(self, content: str) -> bool:
        """Detect systematic variable renaming in Java"""
        variable_names = re.findall(r'\b[a-z][a-zA-Z0-9]*\b', content)
        
        # Check for sequential naming patterns
        sequential_count = 0
        for i in range(1, 10):
            for base in ['var', 'temp', 'data', 'result', 'obj']:
                if f'{base}{i}' in variable_names:
                    sequential_count += 1
        
        return sequential_count > 3
    
    def _detect_java_formatter_signature(self, content: str) -> bool:
        """Detect Java formatter processing signatures"""
        # Google Java Format signatures
        if re.search(r'import\s+java\.util\.\*;\s*\n\s*\n\s*import\s+javax', content):
            return True
        
        # Spotless formatter signatures
        if re.search(r'\{\s*\n\s*$', content, re.MULTILINE):
            line_count = content.count('\n')
            brace_newlines = len(re.findall(r'\{\s*\n', content))
            if line_count > 20 and brace_newlines / line_count > 0.1:
                return True
        
        return False
    
    def _get_java_pattern_summary(self, content: str) -> Dict[str, int]:
        """Get summary of detected Java patterns"""
        summary = {}
        
        for category, patterns in self.java_semantic_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, content, re.MULTILINE | re.DOTALL))
            summary[category] = count
        
        return summary
    
    def _calculate_risk_level(self, confidence: float) -> str:
        """Calculate risk level for Java code"""
        if confidence >= 0.75:
            return "HIGH"
        elif confidence >= 0.45:
            return "MEDIUM"
        elif confidence >= 0.25:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_java_explanation(self, confidence: float, semantic_score: float, 
                                 structure_score: float, evasion_indicators: List[str]) -> List[str]:
        """Generate Java-specific explanation"""
        explanation = []
        
        if confidence >= 0.6:
            explanation.append("Strong Java AI-generated code patterns detected")
        elif confidence >= 0.3:
            explanation.append("Moderate Java AI-generated code patterns detected")
        else:
            explanation.append("Minimal Java AI-generated code patterns detected")
        
        if semantic_score > 0.5:
            explanation.append("Java semantic patterns typical of AI code generation")
        
        if structure_score > 0.4:
            explanation.append("Java class structure patterns consistent with AI generation")
        
        if evasion_indicators:
            explanation.append(f"Java-specific evasion attempts: {', '.join(evasion_indicators)}")
        
        return explanation
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis for non-Java files"""
        return {
            'copilot_confidence': 0.0,
            'risk_level': 'MINIMAL',
            'language': 'unknown',
            'java_analysis': {},
            'evasion_resistance': {'evasion_detected': False, 'evasion_indicators': []},
            'explanation': ['File is not Java - analysis skipped']
        }