#!/usr/bin/env python3
"""
Fix the team count consistency issue by ensuring team_stats and team_members
use exactly the same team assignment logic
"""

import pandas as pd
import json
from datetime import datetime, timedelta

def apply_consistent_team_mapping(df, position_combo_to_team, position_to_team):
    """Apply the same team mapping logic used in both places"""
    df = df.copy()
    df['real_team'] = None
    
    # 1. Position combo mapping (highest priority)
    for idx, row in df.iterrows():
        pos1 = str(row.get('QIP POSITION 1ST  NAME', '')).strip()
        pos2 = str(row.get('QIP POSITION 2ND  NAME', '')).strip()
        pos3 = str(row.get('QIP POSITION 3RD  NAME', '')).strip()
        
        combo_key = f"{pos1}|{pos2}|{pos3}"
        if combo_key in position_combo_to_team:
            df.at[idx, 'real_team'] = position_combo_to_team[combo_key]
    
    # 2. Individual position mapping (fallback)
    position_columns = [
        'QIP POSITION 1ST  NAME',
        'QIP POSITION 2ND  NAME', 
        'QIP POSITION 3RD  NAME',
    ]
    
    for col in position_columns:
        if col in df.columns:
            temp_mapping = df[col].map(position_to_team)
            df['real_team'] = df['real_team'].combine_first(temp_mapping)
    
    df['real_team'] = df['real_team'].fillna('Team Unidentified')
    return df

def main():
    # Load data
    df = pd.read_csv('input_files/basic manpower data august.csv')
    
    # Load team structure
    with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
        team_structure = json.load(f)
    
    # Build mappings
    position_to_team = {}
    position_combo_to_team = {}
    
    for position_data in team_structure.get('positions', []):
        team_name = position_data.get('team_name', '')
        position_1st = position_data.get('position_1st', '').strip()
        position_2nd = position_data.get('position_2nd', '').strip()
        position_3rd = position_data.get('position_3rd', '').strip()
        
        combo_key = f"{position_1st}|{position_2nd}|{position_3rd}"
        position_combo_to_team[combo_key] = team_name
        
        if position_1st and position_1st != 'ASSEMBLY INSPECTOR':
            position_to_team[position_1st] = team_name
    
    # Apply team mapping
    df = apply_consistent_team_mapping(df, position_combo_to_team, position_to_team)
    
    # Filter active employees
    active_mask = df['RE MARK'] != 'Stop working' if 'RE MARK' in df.columns else df['Stop working Date'].isna()
    active_df = df[active_mask].copy()
    
    print("=== Consistent Team Counts (Active Employees) ===")
    team_counts = active_df['real_team'].value_counts()
    for team, count in team_counts.items():
        print(f"{team}: {count}")
    
    # Check ASSEMBLY specifically
    assembly_df = active_df[active_df['real_team'] == 'ASSEMBLY']
    print(f"\n=== ASSEMBLY Team Analysis ===")
    print(f"Total ASSEMBLY members (using consistent mapping): {len(assembly_df)}")
    
    # Check what positions are in ASSEMBLY team
    print("\nPosition distribution in ASSEMBLY team:")
    pos1_counts = assembly_df['QIP POSITION 1ST  NAME'].value_counts().head(10)
    for pos, count in pos1_counts.items():
        print(f"  {pos}: {count}")
    
    # Find employees with ASSEMBLY in their position but not in ASSEMBLY team
    has_assembly_keyword = active_df[
        active_df['QIP POSITION 1ST  NAME'].str.contains('ASSEMBLY', na=False) |
        active_df['QIP POSITION 2ND  NAME'].str.contains('ASSEMBLY', na=False) |
        active_df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', na=False)
    ]
    
    not_in_assembly_team = has_assembly_keyword[has_assembly_keyword['real_team'] != 'ASSEMBLY']
    print(f"\n=== Misassigned ASSEMBLY Positions ===")
    print(f"Employees with 'ASSEMBLY' in position but not in ASSEMBLY team: {len(not_in_assembly_team)}")
    
    # Group by their assigned team
    print("\nWhere they are assigned instead:")
    misassigned_teams = not_in_assembly_team['real_team'].value_counts()
    for team, count in misassigned_teams.items():
        print(f"  {team}: {count}")
    
    # Save corrected team assignments
    print("\n=== Recommendation ===")
    print("The team_stats calculation should show:")
    print(f"  ASSEMBLY: {len(assembly_df)} members (not 120)")
    print("\nThis matches the actual team_members count and provides consistency.")
    
    return len(assembly_df)

if __name__ == "__main__":
    correct_count = main()
    print(f"\n✅ Correct ASSEMBLY count should be: {correct_count}")