#!/usr/bin/env python3
"""
Create Granular Analysis Reporter
Shows specific files with AI detection instead of just percentages
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def analyze_files_with_ai_markers():
    """Analyze current analysis and show file-level AI detection details"""
    
    # Load current analysis
    analysis_file = Path("current_analysis.json")
    if not analysis_file.exists():
        print("No analysis data found. Run analysis first.")
        return
    
    with open(analysis_file, 'r') as f:
        data = json.load(f)
    
    # Extract files with AI detection
    ai_files = []
    total_files = 0
    total_ai_lines = 0
    total_lines = 0
    
    for filename, file_data in data.get('files', {}).items():
        total_files += 1
        
        analysis = file_data.get('copilot_analysis', {})
        confidence = analysis.get('confidence_score', 0)
        estimated_lines = analysis.get('estimated_lines', 0)
        total_analyzed = analysis.get('total_analyzed_lines', 0)
        
        total_lines += total_analyzed
        total_ai_lines += estimated_lines
        
        # Include files with any AI detection
        if confidence > 0.05:  # 5% threshold
            ai_files.append({
                'file': filename,
                'confidence': confidence,
                'ai_lines': estimated_lines,
                'total_lines': total_analyzed,
                'risk_level': analysis.get('risk_level', 'UNKNOWN'),
                'has_explicit_markers': any(
                    indicator for key, indicator in analysis.get('indicators', {}).items()
                    if 'marker' in key.lower() and indicator
                ),
                'markers': analysis.get('copilot_markers', []),
                'explanation': analysis.get('analysis_explanation', [])
            })
    
    # Sort by confidence (highest first)
    ai_files.sort(key=lambda x: x['confidence'], reverse=True)
    
    print("=" * 70)
    print("🔍 GRANULAR AI DETECTION ANALYSIS")
    print("=" * 70)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total files analyzed: {total_files}")
    print(f"   Files with AI detection: {len(ai_files)}")
    print(f"   Overall AI percentage: {(total_ai_lines / total_lines * 100):.1f}%" if total_lines > 0 else "   Overall AI percentage: 0.0%")
    print(f"   Total AI lines: {total_ai_lines:,}")
    print(f"   Total lines: {total_lines:,}")
    
    if not ai_files:
        print(f"\n❌ No files detected with AI assistance above 5% threshold")
        print(f"   This suggests either:")
        print(f"   • The repository contains mostly human-written code")
        print(f"   • AI markers are not being detected properly")
        print(f"   • Detection thresholds are too conservative")
        return
    
    print(f"\n📁 FILES WITH AI DETECTION:")
    print(f"   {'File':<40} {'Confidence':<12} {'AI Lines':<10} {'Risk':<10} {'Markers'}")
    print(f"   {'-'*40} {'-'*12} {'-'*10} {'-'*10} {'-'*7}")
    
    for file_info in ai_files:
        file_short = file_info['file'][-37:] + "..." if len(file_info['file']) > 40 else file_info['file']
        confidence_pct = f"{file_info['confidence']:.1%}"
        ai_lines = f"{file_info['ai_lines']}/{file_info['total_lines']}"
        risk = file_info['risk_level']
        has_markers = "✓" if file_info['has_explicit_markers'] else "✗"
        
        print(f"   {file_short:<40} {confidence_pct:<12} {ai_lines:<10} {risk:<10} {has_markers}")
    
    print(f"\n🎯 TOP AI-DETECTED FILES:")
    for i, file_info in enumerate(ai_files[:5], 1):
        print(f"\n   {i}. {file_info['file']}")
        print(f"      Confidence: {file_info['confidence']:.1%}")
        print(f"      AI Lines: {file_info['ai_lines']} / {file_info['total_lines']}")
        print(f"      Risk Level: {file_info['risk_level']}")
        
        if file_info['markers']:
            print(f"      Explicit Markers Found:")
            for marker in file_info['markers']:
                print(f"        Line {marker.get('line_number', '?')}: {marker.get('content', 'Unknown')}")
        
        if file_info['explanation']:
            print(f"      Analysis: {'; '.join(file_info['explanation'])}")
    
    # Check for specific "AI-generated" markers
    print(f"\n🏷️  EXPLICIT AI MARKER ANALYSIS:")
    files_with_markers = [f for f in ai_files if f['has_explicit_markers']]
    
    if files_with_markers:
        print(f"   Found {len(files_with_markers)} files with explicit AI markers:")
        for file_info in files_with_markers:
            print(f"   • {file_info['file']}")
            for marker in file_info['markers']:
                print(f"     Line {marker.get('line_number', '?')}: {marker.get('content', 'Unknown')}")
    else:
        print(f"   No explicit AI markers detected in analyzed files")
        print(f"   If you added '# AI-generated Class File' comments, they may not be detected")
        print(f"   Supported patterns: '# AI-generated', '# Generated by Copilot', etc.")

if __name__ == "__main__":
    analyze_files_with_ai_markers()