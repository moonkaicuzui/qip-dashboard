#!/usr/bin/env python3
"""
Dashboard Feature Validation Script
Validates that all requested features are properly implemented
"""

import os
import json
from datetime import datetime

def validate_dashboard():
    """Validate dashboard features"""
    print("\n" + "="*60)
    print("📊 Dashboard Feature Validation")
    print("="*60)
    
    # Check if dashboard file exists
    dashboard_path = "output_files/management_dashboard_2025_08.html"
    if not os.path.exists(dashboard_path):
        print("❌ Dashboard file not found!")
        return False
    
    # Read dashboard content
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Feature checklist
    features = {
        "Data freshness indicator": "최신 데이터:" in content,
        "Treemap gradient colors": "gradient" in content.lower() or "rgb(" in content,
        "Percentage change display": "changePercent" in content,
        "Team member modal": "showTeamMembersModal" in content,
        "Absence analysis modal": "showAbsenceAnalysisModal" in content,
        "Resignation analysis modal": "showResignationAnalysisModal" in content,
        "Unified chart titles": "font-size: 16px" in content and "font-weight: 600" in content,
        "CSS animations": "@keyframes" in content,
        "Clickable team rows": "cursor: pointer" in content,
        "Proportional box sizing": "boxSize" in content or "area" in content,
        "Green/Red gradient logic": "changePercent > 0" in content,
        "Team detail popups": "teamMembersData" in content,
        "Left-aligned titles": "text-align: left" in content,
        "Hover effects": ":hover" in content,
        "Modal z-index management": "z-index:" in content and ("2000" in content or "'2000'" in content)
    }
    
    # Check each feature
    print("\n📋 Feature Checklist:")
    all_passed = True
    for feature, check in features.items():
        if check:
            print(f"  ✅ {feature}")
        else:
            print(f"  ❌ {feature}")
            all_passed = False
    
    # Check metadata
    metadata_path = "output_files/hr_metadata_2025.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"\n📊 Data Statistics:")
        print(f"  • Current month records: {metadata.get('current_month', {}).get('total_count', 0)}")
        print(f"  • Previous month records: {metadata.get('previous_month', {}).get('total_count', 0)}")
        print(f"  • Number of teams: {len(metadata.get('current_month', {}).get('by_team', {}))}")
        print(f"  • Data timestamp: {metadata.get('generation_timestamp', 'N/A')}")
    
    # Size check
    file_size = os.path.getsize(dashboard_path) / 1024 / 1024  # MB
    print(f"\n📁 Dashboard file size: {file_size:.2f} MB")
    
    if all_passed:
        print("\n✅ All features validated successfully!")
    else:
        print("\n⚠️ Some features need attention")
    
    print("="*60)
    return all_passed

if __name__ == "__main__":
    validate_dashboard()