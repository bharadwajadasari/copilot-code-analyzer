#!/usr/bin/env python3
"""
Performance Optimization Test
Tests the optimized conservative detector performance on large file sets
"""

import time
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer.conservative_evasion_detector import ConservativeEvasionDetector
from analyzer.optimized_conservative_detector import OptimizedConservativeDetector

def create_test_content():
    """Create test content samples"""
    
    # Small file
    small_file = '''
def process_data(data):
    if data is None:
        return None
    return data.upper()
'''
    
    # Medium file
    medium_file = '''
class DataProcessor:
    def __init__(self, config=None):
        self.config = config or {}
    
    def process_user_data(self, userData, validateInput=True):
        """Process user data with validation"""
        if userData is None or len(userData) == 0:
            return {}
        
        result = {}
        try:
            if validateInput:
                userData = self.validateUserData(userData)
            
            processedData = []
            for item in userData:
                if item is not None:
                    processedItem = self.transformUserItem(item)
                    processedData.append(processedItem)
            
            result["data"] = processedData
            result["count"] = len(processedData)
            
        except Exception as e:
            print(f"Error: {e}")
            return {}
        
        return result
    
    def validateUserData(self, userData):
        return [item for item in userData if item]
    
    def transformUserItem(self, item):
        return str(item).lower()
'''
    
    # Large file (simulated)
    large_file = medium_file * 10  # Repeat to make it larger
    
    return {
        'small': small_file,
        'medium': medium_file,  
        'large': large_file
    }

def test_detector_performance(detector, content_samples, detector_name):
    """Test detector performance on different file sizes"""
    
    print(f"\n{detector_name} Performance Test")
    print("-" * 50)
    
    results = {}
    
    for size_name, content in content_samples.items():
        file_size = len(content)
        
        # Time the analysis
        start_time = time.time()
        analysis = detector.analyze_content(content, '.py')
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        results[size_name] = {
            'size_bytes': file_size,
            'processing_time': processing_time,
            'confidence': analysis['copilot_confidence'],
            'risk_level': analysis['risk_level']
        }
        
        print(f"{size_name.capitalize()} file ({file_size:,} bytes): {processing_time:.4f}s - {analysis['copilot_confidence']:.1%} confidence")
    
    return results

def benchmark_large_file_set():
    """Benchmark performance on simulated large file set"""
    
    print("\n" + "=" * 60)
    print("LARGE FILE SET BENCHMARK")
    print("=" * 60)
    
    # Create test samples
    content_samples = create_test_content()
    
    # Initialize detectors
    config = {'conservative_mode': True, 'ai_indicators': {}}
    
    standard_detector = ConservativeEvasionDetector(config)
    optimized_detector = OptimizedConservativeDetector(config)
    
    # Test standard detector
    print("\n🐌 Testing Standard Conservative Detector")
    standard_results = test_detector_performance(standard_detector, content_samples, "Standard")
    
    # Test optimized detector
    print("\n🚀 Testing Optimized Conservative Detector")
    optimized_results = test_detector_performance(optimized_detector, content_samples, "Optimized")
    
    # Compare performance
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)
    
    for size_name in content_samples.keys():
        standard_time = standard_results[size_name]['processing_time']
        optimized_time = optimized_results[size_name]['processing_time']
        
        if standard_time > 0:
            speedup = standard_time / optimized_time
            improvement = ((standard_time - optimized_time) / standard_time) * 100
        else:
            speedup = 1.0
            improvement = 0.0
        
        print(f"{size_name.capitalize()} file:")
        print(f"  Standard:  {standard_time:.4f}s")
        print(f"  Optimized: {optimized_time:.4f}s")
        print(f"  Speedup:   {speedup:.1f}x ({improvement:.1f}% faster)")
        
        # Check accuracy consistency
        std_conf = standard_results[size_name]['confidence']
        opt_conf = optimized_results[size_name]['confidence']
        accuracy_diff = abs(std_conf - opt_conf)
        
        print(f"  Accuracy:  {accuracy_diff:.2%} difference")
        print()
    
    # Simulate large repository analysis
    print("🏢 LARGE REPOSITORY SIMULATION")
    print("-" * 50)
    
    # Simulate 1000 files of varying sizes
    simulated_files = []
    for i in range(1000):
        if i % 3 == 0:
            simulated_files.append(content_samples['large'])
        elif i % 3 == 1:
            simulated_files.append(content_samples['medium'])
        else:
            simulated_files.append(content_samples['small'])
    
    print(f"Simulating analysis of {len(simulated_files)} files...")
    
    # Test optimized detector on large set
    start_time = time.time()
    
    total_confidence = 0
    for i, content in enumerate(simulated_files):
        analysis = optimized_detector.analyze_content(content, '.py')
        total_confidence += analysis['copilot_confidence']
        
        if i % 100 == 0 and i > 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            print(f"  Processed {i} files in {elapsed:.1f}s ({rate:.1f} files/sec)")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_confidence = total_confidence / len(simulated_files)
    
    print(f"\nLarge Repository Results:")
    print(f"  Total files: {len(simulated_files):,}")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Rate: {len(simulated_files)/total_time:.1f} files/second")
    print(f"  Average confidence: {avg_confidence:.1%}")
    
    # Show cache statistics
    if hasattr(optimized_detector, 'get_cache_stats'):
        cache_stats = optimized_detector.get_cache_stats()
        print(f"  Cache utilization: {cache_stats['cache_size']}/{cache_stats['cache_limit']}")
    
    # Performance recommendations
    print("\n💡 PERFORMANCE RECOMMENDATIONS")
    print("-" * 50)
    
    files_per_second = len(simulated_files) / total_time
    
    if files_per_second > 50:
        print("✅ Excellent performance for large codebases")
        print("   System can handle enterprise-scale repositories efficiently")
    elif files_per_second > 20:
        print("✅ Good performance for medium to large codebases")
        print("   Consider using batch processing for very large repositories")
    else:
        print("⚠️  Performance may be slow for very large codebases")
        print("   Recommendations:")
        print("   • Increase max_workers in config.json")
        print("   • Use smaller batch sizes")
        print("   • Consider file filtering")
    
    print(f"\nOptimizations enabled:")
    print("• Pre-compiled regex patterns")
    print("• Content-based caching")
    print("• Early exit optimizations")
    print("• Sampling for large files")
    print("• Batch processing with memory management")

if __name__ == "__main__":
    benchmark_large_file_set()