"""
Metrics Calculator
Calculates and aggregates various metrics from code analysis results.
"""

from typing import Dict, List, Any
from collections import defaultdict
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MetricsCalculator:
    def __init__(self):
        pass
    
    def calculate_repository_summary(self, file_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary metrics for the entire repository"""
        if not file_results:
            return self._create_empty_summary()
        
        total_files = len(file_results)
        total_lines = sum(file_data.get('total_lines', 0) for file_data in file_results.values())
        total_code_lines = sum(file_data.get('code_lines', 0) for file_data in file_results.values())
        total_copilot_lines = sum(file_data.get('estimated_copilot_lines', 0) for file_data in file_results.values())
        total_human_lines = sum(file_data.get('estimated_human_lines', 0) for file_data in file_results.values())
        
        # Calculate percentages
        copilot_percentage = (total_copilot_lines / total_code_lines * 100) if total_code_lines > 0 else 0
        human_percentage = (total_human_lines / total_code_lines * 100) if total_code_lines > 0 else 0
        
        # Calculate average confidence
        confidences = [file_data.get('copilot_confidence', 0) for file_data in file_results.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # File size distribution
        file_sizes = [file_data.get('code_lines', 0) for file_data in file_results.values()]
        file_size_stats = self._calculate_distribution_stats(file_sizes)
        
        # High confidence files (likely Copilot)
        high_confidence_files = len([
            f for f in file_results.values() 
            if f.get('copilot_confidence', 0) > 0.7
        ])
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_code_lines': total_code_lines,
            'copilot_lines': total_copilot_lines,
            'human_lines': total_human_lines,
            'copilot_percentage': round(copilot_percentage, 2),
            'human_percentage': round(human_percentage, 2),
            'average_confidence': round(avg_confidence, 3),
            'high_confidence_files': high_confidence_files,
            'high_confidence_percentage': round((high_confidence_files / total_files * 100), 2) if total_files > 0 else 0,
            'file_size_stats': file_size_stats
        }
    
    def calculate_language_breakdown(self, file_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics breakdown by programming language"""
        language_stats = defaultdict(lambda: {
            'files': 0,
            'total_lines': 0,
            'code_lines': 0,
            'copilot_lines': 0,
            'human_lines': 0,
            'confidence_scores': []
        })
        
        for file_data in file_results.values():
            language = file_data.get('language', 'Unknown')
            stats = language_stats[language]
            
            stats['files'] += 1
            stats['total_lines'] += file_data.get('total_lines', 0)
            stats['code_lines'] += file_data.get('code_lines', 0)
            stats['copilot_lines'] += file_data.get('estimated_copilot_lines', 0)
            stats['human_lines'] += file_data.get('estimated_human_lines', 0)
            stats['confidence_scores'].append(file_data.get('copilot_confidence', 0))
        
        # Calculate percentages and averages for each language
        result = {}
        for language, stats in language_stats.items():
            code_lines = stats['code_lines']
            copilot_percentage = (stats['copilot_lines'] / code_lines * 100) if code_lines > 0 else 0
            human_percentage = (stats['human_lines'] / code_lines * 100) if code_lines > 0 else 0
            avg_confidence = sum(stats['confidence_scores']) / len(stats['confidence_scores']) if stats['confidence_scores'] else 0
            
            result[language] = {
                'files': stats['files'],
                'total_lines': stats['total_lines'],
                'code_lines': stats['code_lines'],
                'copilot_lines': stats['copilot_lines'],
                'human_lines': stats['human_lines'],
                'copilot_percentage': round(copilot_percentage, 2),
                'human_percentage': round(human_percentage, 2),
                'average_confidence': round(avg_confidence, 3)
            }
        
        return result
    
    def calculate_time_series_metrics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate time series metrics from historical analysis data"""
        if not historical_data:
            return {}
        
        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x.get('timestamp', ''))
        
        time_series = []
        for data in sorted_data:
            summary = data.get('summary', {})
            time_series.append({
                'timestamp': data.get('timestamp'),
                'copilot_percentage': summary.get('copilot_percentage', 0),
                'human_percentage': summary.get('human_percentage', 0),
                'total_files': summary.get('total_files', 0),
                'total_lines': summary.get('total_lines', 0)
            })
        
        # Calculate trends
        if len(time_series) >= 2:
            first = time_series[0]
            last = time_series[-1]
            
            copilot_trend = last['copilot_percentage'] - first['copilot_percentage']
            files_trend = last['total_files'] - first['total_files']
            lines_trend = last['total_lines'] - first['total_lines']
        else:
            copilot_trend = files_trend = lines_trend = 0
        
        return {
            'time_series': time_series,
            'trends': {
                'copilot_percentage_change': round(copilot_trend, 2),
                'files_change': files_trend,
                'lines_change': lines_trend
            },
            'total_analyses': len(time_series)
        }
    
    def calculate_file_metrics(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed metrics for a single file"""
        copilot_analysis = file_data.get('copilot_analysis', {})
        indicators = copilot_analysis.get('indicators', {})
        detailed_scores = copilot_analysis.get('detailed_scores', {})
        
        code_lines = file_data.get('code_lines', 0)
        copilot_lines = file_data.get('estimated_copilot_lines', 0)
        human_lines = file_data.get('estimated_human_lines', 0)
        
        # Calculate line distribution
        line_distribution = {
            'code_lines': code_lines,
            'comment_lines': file_data.get('comment_lines', 0),
            'blank_lines': file_data.get('blank_lines', 0),
            'copilot_lines': copilot_lines,
            'human_lines': human_lines
        }
        
        # Risk assessment
        risk_level = self._assess_copilot_risk_level(
            file_data.get('copilot_confidence', 0),
            indicators
        )
        
        return {
            'file_path': file_data.get('file_path'),
            'language': file_data.get('language'),
            'line_distribution': line_distribution,
            'confidence_breakdown': detailed_scores,
            'indicators': indicators,
            'risk_level': risk_level,
            'last_modified': file_data.get('last_modified'),
            'file_size': file_data.get('file_size', 0)
        }
    
    def calculate_project_complexity(self, file_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate project complexity metrics"""
        if not file_results:
            return {}
        
        # Language diversity
        languages = set(file_data.get('language', 'Unknown') for file_data in file_results.values())
        language_diversity = len(languages)
        
        # File size distribution
        file_sizes = [file_data.get('code_lines', 0) for file_data in file_results.values()]
        size_complexity = self._calculate_complexity_from_distribution(file_sizes)
        
        # Confidence distribution
        confidences = [file_data.get('copilot_confidence', 0) for file_data in file_results.values()]
        confidence_variance = self._calculate_variance(confidences)
        
        # Overall complexity score
        complexity_score = self._calculate_overall_complexity(
            language_diversity, size_complexity, confidence_variance
        )
        
        return {
            'language_diversity': language_diversity,
            'size_complexity': size_complexity,
            'confidence_variance': round(confidence_variance, 3),
            'overall_complexity': complexity_score,
            'complexity_level': self._get_complexity_level(complexity_score)
        }
    
    def _calculate_distribution_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate basic distribution statistics"""
        if not values:
            return {'min': 0, 'max': 0, 'mean': 0, 'median': 0}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'mean': sum(sorted_values) / n,
            'median': sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_complexity_from_distribution(self, values: List[int]) -> float:
        """Calculate complexity score from value distribution"""
        if not values:
            return 0.0
        
        # Normalize complexity based on variance and range
        variance = self._calculate_variance(values)
        value_range = max(values) - min(values) if values else 0
        
        # Simple complexity score (0-1)
        complexity = min((variance + value_range) / (max(values) + 1), 1.0) if values else 0.0
        return complexity
    
    def _calculate_overall_complexity(self, lang_diversity: int, size_complexity: float, conf_variance: float) -> float:
        """Calculate overall project complexity score"""
        # Normalize and weight different complexity factors
        normalized_lang = min(lang_diversity / 10, 1.0)  # Cap at 10 languages
        normalized_size = size_complexity
        normalized_conf = min(conf_variance, 1.0)
        
        # Weighted average
        weights = {'language': 0.3, 'size': 0.4, 'confidence': 0.3}
        
        overall = (
            normalized_lang * weights['language'] +
            normalized_size * weights['size'] +
            normalized_conf * weights['confidence']
        )
        
        return round(overall, 3)
    
    def _get_complexity_level(self, score: float) -> str:
        """Convert complexity score to human-readable level"""
        if score < 0.3:
            return 'Low'
        elif score < 0.6:
            return 'Medium'
        elif score < 0.8:
            return 'High'
        else:
            return 'Very High'
    
    def _assess_copilot_risk_level(self, confidence: float, indicators: Dict[str, bool]) -> str:
        """Assess the risk level of Copilot usage in a file"""
        if confidence > 0.8 or indicators.get('explicit_comments', False):
            return 'High'
        elif confidence > 0.6:
            return 'Medium'
        elif confidence > 0.3:
            return 'Low'
        else:
            return 'Minimal'
    
    def _create_empty_summary(self) -> Dict[str, Any]:
        """Create an empty summary for repositories with no files"""
        return {
            'total_files': 0,
            'total_lines': 0,
            'total_code_lines': 0,
            'copilot_lines': 0,
            'human_lines': 0,
            'copilot_percentage': 0.0,
            'human_percentage': 0.0,
            'average_confidence': 0.0,
            'high_confidence_files': 0,
            'high_confidence_percentage': 0.0,
            'file_size_stats': {'min': 0, 'max': 0, 'mean': 0, 'median': 0}
        }
