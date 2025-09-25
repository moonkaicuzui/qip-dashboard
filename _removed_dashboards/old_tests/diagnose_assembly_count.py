#!/usr/bin/env python3
"""
Diagnose ASSEMBLY team member count discrepancy
Find why team_stats shows 120 but team_members shows 100
"""

import pandas as pd
import json

def diagnose_assembly_count():
    # Load the August data
    df = pd.read_csv('input_files/basic manpower data august.csv')
    print(f"Total rows in CSV: {len(df)}")
    
    # Load team structure for mapping
    with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
        team_structure = json.load(f)
    
    # Build position to team mapping
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
    
    # Filter active employees
    active_mask = df['RE MARK'] != 'Stop working' if 'RE MARK' in df.columns else df['Stop working Date'].isna()
    active_df = df[active_mask].copy()
    print(f"Active employees: {len(active_df)}")
    
    # Method 1: Direct team assignment (used in team_stats calculation)
    # Check what happens if we directly look for ASSEMBLY positions
    assembly_positions = [
        'ASSEMBLY INSPECTOR', 'ASSEMBLY LINE LEADER', 'ASSEMBLY GROUP LEADER',
        'ASSEMBLY TECHNICIAN', 'ASSEMBLY', 'ASSEMBLY SUPERVISOR'
    ]
    
    assembly_direct = active_df[
        active_df['QIP POSITION 1ST  NAME'].str.contains('ASSEMBLY', na=False) |
        active_df['QIP POSITION 2ND  NAME'].str.contains('ASSEMBLY', na=False) |
        active_df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', na=False)
    ]
    print(f"\nDirect ASSEMBLY search (contains 'ASSEMBLY'): {len(assembly_direct)}")
    
    # Method 2: Using position mapping (used in team_members)
    active_df['real_team'] = None
    
    # Apply position combo mapping
    for idx, row in active_df.iterrows():
        pos1 = str(row.get('QIP POSITION 1ST  NAME', '')).strip()
        pos2 = str(row.get('QIP POSITION 2ND  NAME', '')).strip()
        pos3 = str(row.get('QIP POSITION 3RD  NAME', '')).strip()
        
        combo_key = f"{pos1}|{pos2}|{pos3}"
        if combo_key in position_combo_to_team:
            active_df.at[idx, 'real_team'] = position_combo_to_team[combo_key]
    
    # Apply individual position mapping for unmapped rows
    position_columns = [
        'QIP POSITION 1ST  NAME',
        'QIP POSITION 2ND  NAME', 
        'QIP POSITION 3RD  NAME',
    ]
    
    for col in position_columns:
        if col in active_df.columns:
            temp_mapping = active_df[col].map(position_to_team)
            active_df['real_team'] = active_df['real_team'].combine_first(temp_mapping)
    
    active_df['real_team'] = active_df['real_team'].fillna('Team Unidentified')
    
    assembly_mapped = active_df[active_df['real_team'] == 'ASSEMBLY']
    print(f"ASSEMBLY via mapping: {len(assembly_mapped)}")
    
    # Find the missing members
    print("\n=== Analyzing Discrepancy ===")
    
    # Members in direct search but not in mapped
    direct_ids = set(assembly_direct['Employee No'].astype(str))
    mapped_ids = set(assembly_mapped['Employee No'].astype(str))
    
    missing_from_mapped = direct_ids - mapped_ids
    print(f"Found in direct search but not in mapping: {len(missing_from_mapped)} members")
    
    if missing_from_mapped:
        missing_df = active_df[active_df['Employee No'].astype(str).isin(missing_from_mapped)]
        print("\nMissing members details:")
        for _, row in missing_df.head(10).iterrows():
            print(f"  - {row['Full Name']} ({row['Employee No']})")
            print(f"    Pos1: {row.get('QIP POSITION 1ST  NAME', '')}")
            print(f"    Pos2: {row.get('QIP POSITION 2ND  NAME', '')}")
            print(f"    Pos3: {row.get('QIP POSITION 3RD  NAME', '')}")
            print(f"    Mapped to: {row.get('real_team', 'Unknown')}")
    
    # Team distribution
    print("\n=== Team Distribution ===")
    team_counts = active_df['real_team'].value_counts()
    for team, count in team_counts.items():
        print(f"{team}: {count}")
    
    # Check if any ASSEMBLY positions are mapped to other teams
    print("\n=== ASSEMBLY Positions in Other Teams ===")
    for team in active_df['real_team'].unique():
        if team != 'ASSEMBLY':
            team_df = active_df[active_df['real_team'] == team]
            assembly_in_team = team_df[
                team_df['QIP POSITION 1ST  NAME'].str.contains('ASSEMBLY', na=False) |
                team_df['QIP POSITION 2ND  NAME'].str.contains('ASSEMBLY', na=False) |
                team_df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', na=False)
            ]
            if len(assembly_in_team) > 0:
                print(f"\n{team} has {len(assembly_in_team)} ASSEMBLY positions:")
                for _, row in assembly_in_team.head(3).iterrows():
                    print(f"  - {row['Full Name']}: {row['QIP POSITION 1ST  NAME']}")

if __name__ == "__main__":
    diagnose_assembly_count()