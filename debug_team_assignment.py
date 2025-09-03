#!/usr/bin/env python3
"""
Debug the team assignment to understand why we get 120 instead of 109
"""

import pandas as pd
import json

# Simulate what the code does
df = pd.read_csv('input_files/basic manpower data august.csv')

# Load team structure
with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
    team_structure = json.load(f)

# Build mappings EXACTLY as the code does
position_to_team = {
    'ASSEMBLY INSPECTOR': 'ASSEMBLY',
    'ASSEMBLY LINE LEADER': 'ASSEMBLY', 
    'ASSEMBLY GROUP LEADER': 'ASSEMBLY',
    'BOTTOM INSPECTOR': 'BOTTOM',
    'STITCHING INSPECTOR': 'STITCHING',
    'OSC INSPECTOR': 'OSC',
    'REPACKING': 'REPACKING',
    'AQL INSPECTOR': 'AQL',
    'QA INSPECTOR': 'QA',
    'LINE LEADER': 'MTL',
    'GROUP LEADER': 'ASSEMBLY',
    '(V) SUPERVISOR': 'STITCHING',
    'A.MANAGER': 'STITCHING',
    # Add more default mappings
}

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

print(f"Total position combos in mapping: {len(position_combo_to_team)}")
print(f"Total individual positions in mapping: {len(position_to_team)}")

# Now apply the EXACT same logic as calculate_team_statistics
df['real_team'] = None

# Step 1: Position combo mapping
for idx, row in df.iterrows():
    pos1 = str(row.get('QIP POSITION 1ST  NAME', '')).strip()
    pos2 = str(row.get('QIP POSITION 2ND  NAME', '')).strip()
    pos3 = str(row.get('QIP POSITION 3RD  NAME', '')).strip()
    
    combo_key = f"{pos1}|{pos2}|{pos3}"
    if combo_key in position_combo_to_team:
        df.at[idx, 'real_team'] = position_combo_to_team[combo_key]

print(f"\nAfter combo mapping: {df['real_team'].notna().sum()} rows have teams")

# Step 2: Individual position mapping (with priority)
position_columns = [
    'QIP POSITION 3RD  NAME',
    'FINAL QIP POSITION NAME CODE',
    'QIP POSITION 2ND  NAME',
    'QIP POSITION 1ST  NAME'
]

for col in position_columns:
    if col in df.columns:
        temp_mapping = df[col].map(position_to_team)
        before = df['real_team'].notna().sum()
        df['real_team'] = df['real_team'].combine_first(temp_mapping)
        after = df['real_team'].notna().sum()
        print(f"After {col}: {after - before} new assignments (total: {after})")

df['real_team'] = df['real_team'].fillna('Team Unidentified')

# Filter active employees
active_mask = df['RE MARK'] != 'Stop working' if 'RE MARK' in df.columns else df['Stop working Date'].isna()
active_df = df[active_mask]

print(f"\nActive employees: {len(active_df)}")

# Count ASSEMBLY
assembly_df = active_df[active_df['real_team'] == 'ASSEMBLY']
print(f"\n=== RESULT ===")
print(f"ASSEMBLY team count: {len(assembly_df)}")

# Show team distribution
print("\nTeam distribution:")
team_counts = active_df['real_team'].value_counts()
for team, count in team_counts.head(10).items():
    print(f"  {team}: {count}")

# Debug: Check if there are ASSEMBLY positions in the wrong teams
print("\n=== Checking for misassigned ASSEMBLY positions ===")
for team in ['STITCHING', 'MTL', 'REPACKING']:
    team_df = active_df[active_df['real_team'] == team]
    has_assembly = team_df[
        team_df['QIP POSITION 1ST  NAME'].str.contains('ASSEMBLY', na=False) |
        team_df['QIP POSITION 2ND  NAME'].str.contains('ASSEMBLY', na=False) |
        team_df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', na=False)
    ]
    if len(has_assembly) > 0:
        print(f"{team} has {len(has_assembly)} employees with ASSEMBLY in their position")