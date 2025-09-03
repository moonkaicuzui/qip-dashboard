#!/usr/bin/env python3
"""
Trace why team_stats gets 120 instead of 109 for ASSEMBLY
"""

import pandas as pd
import json
import sys
from generate_management_dashboard_v6_enhanced import DashboardGeneratorV6

# Initialize the generator
generator = DashboardGeneratorV6(month=8, year=2025)
generator.load_data()

# Check the data at different stages
df_current = generator.data['current']
print(f"Total rows in current data: {len(df_current)}")

# Check if real_team column exists
if 'real_team' in df_current.columns:
    print("real_team column exists")
    active_mask = df_current['RE MARK'] != 'Stop working' if 'RE MARK' in df_current.columns else df_current['Stop working Date'].isna()
    active_df = df_current[active_mask]
    
    assembly_count = len(active_df[active_df['real_team'] == 'ASSEMBLY'])
    print(f"ASSEMBLY count in real_team (active): {assembly_count}")
else:
    print("real_team column doesn't exist yet")

# Now let's calculate team stats the way the code does it
team_stats = generator.calculate_team_statistics()
print(f"\nteam_stats['ASSEMBLY']['total'] = {team_stats.get('ASSEMBLY', {}).get('total', 'NOT FOUND')}")

# Also check team members
team_members = generator.prepare_team_members()
assembly_members = team_members.get('ASSEMBLY', [])
print(f"len(team_members['ASSEMBLY']) = {len(assembly_members)}")

# Let's trace the issue
print("\n=== Tracing the Issue ===")

# Check what teams are in the data
df = generator.data['current']

# Check if the team assignment happened correctly
if 'real_team' in df.columns:
    print("\nTeam distribution in data:")
    team_counts = df['real_team'].value_counts()
    for team, count in team_counts.head(5).items():
        print(f"  {team}: {count}")
    
    # Active only
    active_mask = df['RE MARK'] != 'Stop working' if 'RE MARK' in df.columns else df['Stop working Date'].isna()
    active_df = df[active_mask]
    
    print("\nActive employee team distribution:")
    active_team_counts = active_df['real_team'].value_counts()
    for team, count in active_team_counts.head(5).items():
        print(f"  {team}: {count}")

print("\n=== Checking team_stats calculation source ===")
# The issue might be that calculate_team_statistics is using a different source
# Let's check what it's actually counting