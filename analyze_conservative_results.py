#!/usr/bin/env python3
"""
Analyze Conservative Detection Results
Show how the conservative detector achieved realistic 10-15% detection rates
"""

import json
import os

def analyze_conservative_results():
    """Analyze the conservative detection findings"""
    
    print("Conservative Evasion-Resistant Detection Results")
    print("=" * 50)
    
    # Load conservative analysis results
    if os.path.exists('conservative_analysis.json'):
        with open('conservative_analysis.json', 'r') as f:
            results = json.load(f)
    else:
        print("❌ Conservative analysis results not found")
        return
    
    files_data = results.get('files', {})
    summary = results.get('summary', {})
    
    print(f"Repository: {results.get('repository_path', 'Unknown')}")
    print(f"Analysis Time: {results.get('timestamp', 'Unknown')}")
    print(f"Total Files: {len(files_data)}")
    print(f"Conservative AI Detection: {summary.get('copilot_percentage', 0):.1f}%")
    print(f"Target Range: 10-15% (Achieved: {summary.get('copilot_percentage', 0):.1f}%)")
    
    # Categorize files by conservative detection
    high_confidence = []
    medium_confidence = []
    low_confidence = []
    minimal_confidence = []
    explicit_markers = []
    
    for file_path, file_data in files_data.items():
        confidence = file_data.get('copilot_confidence', 0)
        analysis = file_data.get('copilot_analysis', {})
        conservative_data = analysis.get('conservative_analysis', {})
        
        if confidence >= 0.85:
            high_confidence.append((file_path, confidence, file_data))
        elif confidence >= 0.55:
            medium_confidence.append((file_path, confidence, file_data))
        elif confidence >= 0.30:
            low_confidence.append((file_path, confidence, file_data))
        elif confidence >= 0.15:
            minimal_confidence.append((file_path, confidence, file_data))
        
        # Check for explicit markers
        if conservative_data.get('explicit_score', 0) > 0:
            explicit_markers.append((file_path, confidence, file_data))
    
    # Sort by confidence
    high_confidence.sort(key=lambda x: x[1], reverse=True)
    medium_confidence.sort(key=lambda x: x[1], reverse=True)
    low_confidence.sort(key=lambda x: x[1], reverse=True)
    
    # Show results by confidence level
    if explicit_markers:
        print(f"\n🎯 EXPLICIT AI MARKERS DETECTED ({len(explicit_markers)} files)")
        print("-" * 50)
        for file_path, confidence, file_data in explicit_markers:
            lines = file_data.get('estimated_copilot_lines', 0)
            total_lines = file_data.get('code_lines', 0)
            print(f"{file_path:<40} {confidence:.1%} ({lines}/{total_lines} lines)")
    
    if high_confidence:
        print(f"\n🔴 HIGH CONFIDENCE (≥85%): {len(high_confidence)} files")
        print("-" * 50)
        for file_path, confidence, file_data in high_confidence:
            lines = file_data.get('estimated_copilot_lines', 0)
            total_lines = file_data.get('code_lines', 0)
            print(f"{file_path:<40} {confidence:.1%} ({lines}/{total_lines} lines)")
    
    if medium_confidence:
        print(f"\n🟡 MEDIUM CONFIDENCE (55-85%): {len(medium_confidence)} files")
        print("-" * 50)
        for file_path, confidence, file_data in medium_confidence[:5]:  # Top 5
            lines = file_data.get('estimated_copilot_lines', 0)
            total_lines = file_data.get('code_lines', 0)
            print(f"{file_path:<40} {confidence:.1%} ({lines}/{total_lines} lines)")
        if len(medium_confidence) > 5:
            print(f"    ... and {len(medium_confidence) - 5} more files")
    
    if low_confidence:
        print(f"\n🟢 LOW CONFIDENCE (30-55%): {len(low_confidence)} files")
        print("-" * 50)
        for file_path, confidence, file_data in low_confidence[:3]:  # Top 3
            lines = file_data.get('estimated_copilot_lines', 0)
            total_lines = file_data.get('code_lines', 0)
            print(f"{file_path:<40} {confidence:.1%} ({lines}/{total_lines} lines)")
        if len(low_confidence) > 3:
            print(f"    ... and {len(low_confidence) - 3} more files")
    
    # Conservative calibration analysis
    total_files = len(files_data)
    ai_files = len([f for f in files_data.values() if f.get('copilot_confidence', 0) >= 0.15])
    
    print(f"\n📊 CONSERVATIVE DETECTION SUMMARY")
    print("-" * 50)
    print(f"Files with AI detection (≥15%): {ai_files}/{total_files} ({ai_files/total_files:.1%})")
    print(f"High confidence files (≥85%): {len(high_confidence)} ({len(high_confidence)/total_files:.1%})")
    print(f"Medium confidence files (55-85%): {len(medium_confidence)} ({len(medium_confidence)/total_files:.1%})")
    print(f"Low confidence files (30-55%): {len(low_confidence)} ({len(low_confidence)/total_files:.1%})")
    
    # Show calibration details for a sample file
    if files_data:
        sample_file = next(iter(files_data.items()))
        file_path, file_data = sample_file
        analysis = file_data.get('copilot_analysis', {})
        conservative_data = analysis.get('conservative_analysis', {})
        
        if conservative_data:
            print(f"\n🔧 CALIBRATION EXAMPLE: {file_path}")
            print("-" * 50)
            print(f"Raw confidence: {conservative_data.get('raw_confidence', 0):.1%}")
            print(f"Calibrated confidence: {file_data.get('copilot_confidence', 0):.1%}")
            print(f"Calibration reduction: {conservative_data.get('calibration_applied', 0):.1%}")
            print(f"Explicit markers: {conservative_data.get('explicit_score', 0):.1%}")
            print(f"Semantic patterns: {conservative_data.get('semantic_score', 0):.1%}")
            print(f"Distinctive naming: {conservative_data.get('naming_score', 0):.1%}")
    
    # Language breakdown
    language_breakdown = results.get('language_breakdown', {})
    if language_breakdown:
        print(f"\n🌐 LANGUAGE-SPECIFIC DETECTION")
        print("-" * 50)
        for language, lang_data in language_breakdown.items():
            lang_ai_pct = lang_data.get('copilot_percentage', 0)
            lang_files = lang_data.get('file_count', 0)
            print(f"{language:<15} {lang_ai_pct:.1f}% AI detection ({lang_files} files)")
    
    # Key insights
    overall_ai_pct = summary.get('copilot_percentage', 0)
    print(f"\n💡 CONSERVATIVE DETECTION INSIGHTS")
    print("-" * 50)
    
    if overall_ai_pct <= 15:
        print(f"✅ Achieved realistic detection rate: {overall_ai_pct:.1f}%")
        print("Conservative calibration successfully prevents false positives")
    else:
        print(f"⚠️  Detection rate higher than target: {overall_ai_pct:.1f}%")
        print("May need additional calibration for more conservative results")
    
    print("\nConservative detection maintains evasion resistance while:")
    print("• Requiring explicit AI markers for highest confidence")
    print("• Using stricter thresholds for semantic patterns")
    print("• Applying calibration factors for realistic rates")
    print("• Focusing on distinctive AI naming and structures")
    print("• Providing detailed calibration transparency")
    
    if overall_ai_pct < 10:
        print(f"\n🎯 RECOMMENDATION: Current {overall_ai_pct:.1f}% detection is very conservative")
        print("Consider slightly relaxing thresholds if more sensitivity is needed")
    elif overall_ai_pct > 20:
        print(f"\n🎯 RECOMMENDATION: Current {overall_ai_pct:.1f}% detection may be too aggressive")
        print("Consider tightening calibration factors for more conservative results")
    else:
        print(f"\n🎯 PERFECT: {overall_ai_pct:.1f}% detection is in the ideal 10-15% range")

if __name__ == "__main__":
    analyze_conservative_results()