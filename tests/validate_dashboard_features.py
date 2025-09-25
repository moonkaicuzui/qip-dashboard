#!/usr/bin/env python3
"""
Dashboard Feature Validation Script
Validates that all requested features are properly implemented
"""

import os
import json
import re
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
    
    # Critical fixes checklist
    print("\n🔧 Critical Fixes:")
    critical_fixes = {
        "Deep copy for readonly fix": "JSON.parse(JSON.stringify(teamData))" in content or "const mutableTeamData = teamData.map(team =>" in content,
        "Date shows Aug 29th": re.search(r'2025년 8월 29일', content) is not None,
        "Treemap function exists": "createTreemap(mainContainer, mutableTeamData)" in content,
        "JSON config embedded": "UI_CONFIG" in content,
        "Small teams handling": "smallTeamsContainer" in content or "// Small teams" in content or "소규모 팀 목록" in content,
        "Position initialization": "x: 0," in content and "y: 0," in content and "width: 0," in content and "height: 0" in content,
    }
    
    critical_passed = True
    for fix, check in critical_fixes.items():
        if check:
            print(f"  ✅ {fix}")
        else:
            print(f"  ❌ {fix}")
            critical_passed = False
    
    # Feature checklist
    print("\n📋 Feature Checklist:")
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
        
        # Check for specific teams that were reported missing
        print(f"\n👥 Team Inclusion Check:")
        critical_teams = ["OFFICE & OCPT", "CUTTING", "HWK QIP"]
        teams_in_data = metadata.get('team_stats', {}).get('2025_08', {}).keys()
        
        for team in critical_teams:
            if team in teams_in_data:
                team_data = metadata['team_stats']['2025_08'][team]
                print(f"  ✅ {team}: {team_data.get('total', 0)} members")
            else:
                print(f"  ⚠️  {team}: Not in current data")
        
        # Check all teams
        print(f"\n  All teams in data: {', '.join(teams_in_data)}")
    
    # Size check
    file_size = os.path.getsize(dashboard_path) / 1024 / 1024  # MB
    print(f"\n📁 Dashboard file size: {file_size:.2f} MB")
    
    if all_passed and critical_passed:
        print("\n✅ All features and critical fixes validated successfully!")
    elif critical_passed:
        print("\n⚠️ Critical fixes OK but some features need attention")
    else:
        print("\n❌ Critical fixes need immediate attention!")
    
    print("="*60)
    return all_passed and critical_passed

if __name__ == "__main__":
    validate_dashboard()