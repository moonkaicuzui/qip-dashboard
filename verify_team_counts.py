#!/usr/bin/env python3
"""
Verify that team_stats and team_members have the same counts
"""

import json

# Load the metadata
with open('output_files/hr_metadata_2025.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Load the dashboard HTML to check JavaScript data
with open('output_files/management_dashboard_2025_08.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract team_stats from metadata
team_stats_aug = metadata.get('team_stats', {}).get('2025_08', {})
print("=== Team Stats from Metadata (August 2025) ===")
for team, stats in team_stats_aug.items():
    print(f"{team}: {stats.get('total', 0)} members")

# Check ASSEMBLY specifically
assembly_stats = team_stats_aug.get('ASSEMBLY', {})
print(f"\nASSEMBLY in team_stats: {assembly_stats.get('total', 0)} members")

# Try to extract teamMembers data from JavaScript (rough extraction)
import re

# Find teamMembers in JavaScript
team_members_pattern = r'const teamMembers = ({[^}]*ASSEMBLY[^}]*})'
match = re.search(team_members_pattern, html_content, re.DOTALL)

if match:
    print("\nFound teamMembers in JavaScript")
    # Count ASSEMBLY members more accurately
    assembly_section = html_content[html_content.find('teamMembers["ASSEMBLY"] = ['):html_content.find('teamMembers["ASSEMBLY"] = [') + 10000]
    
    # Count member objects
    member_count = assembly_section.count('{"id":')
    print(f"ASSEMBLY members in teamMembers: approximately {member_count}")
else:
    print("\nCouldn't extract teamMembers from JavaScript")

# Also check the generated team counts
team_counts_pattern = r'"ASSEMBLY":\s*{\s*"total":\s*(\d+)'
matches = re.findall(team_counts_pattern, html_content)
if matches:
    print(f"\nASSEMBLY totals found in HTML:")
    for i, count in enumerate(matches[:5], 1):  # Show first 5 occurrences
        print(f"  Occurrence {i}: {count} members")