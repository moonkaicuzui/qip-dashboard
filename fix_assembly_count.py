#!/usr/bin/env python3
"""
Fix the ASSEMBLY team count issue by:
1. Clearing incorrect cached metadata
2. Regenerating with correct logic
"""

import os
import json
import shutil
from datetime import datetime

print("=== Fixing ASSEMBLY Team Count Issue ===\n")

# Step 1: Backup and clear incorrect metadata
metadata_file = "output_files/hr_metadata_2025.json"
if os.path.exists(metadata_file):
    # Backup the old file
    backup_file = f"output_files/hr_metadata_2025_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy(metadata_file, backup_file)
    print(f"✓ Backed up old metadata to: {backup_file}")
    
    # Load and check the incorrect values
    with open(metadata_file, 'r', encoding='utf-8') as f:
        old_metadata = json.load(f)
    
    if 'team_stats' in old_metadata and '2025_08' in old_metadata['team_stats']:
        old_assembly = old_metadata['team_stats']['2025_08'].get('ASSEMBLY', {})
        print(f"❌ Old incorrect ASSEMBLY total: {old_assembly.get('total', 'N/A')}")
    
    # Delete the incorrect file
    os.remove(metadata_file)
    print("✓ Removed incorrect metadata file")
else:
    print("ℹ️ No existing metadata file found")

print("\n=== Regenerating Dashboard with Correct Logic ===\n")

# Step 2: Run the dashboard generator (it will create fresh metadata)
import subprocess

result = subprocess.run([
    'python', 'generate_management_dashboard_v6_enhanced.py',
    '--month', '8',
    '--year', '2025'
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Step 3: Verify the fix
if os.path.exists(metadata_file):
    with open(metadata_file, 'r', encoding='utf-8') as f:
        new_metadata = json.load(f)
    
    if 'team_stats' in new_metadata and '2025_08' in new_metadata['team_stats']:
        new_assembly = new_metadata['team_stats']['2025_08'].get('ASSEMBLY', {})
        new_total = new_assembly.get('total', 'N/A')
        
        print(f"\n=== Verification ===")
        print(f"✓ New ASSEMBLY total: {new_total}")
        
        if new_total == 109:
            print("✅ SUCCESS! ASSEMBLY count is now correct (109)")
        else:
            print(f"⚠️ Warning: Expected 109 but got {new_total}")
            print("\nThis might be because the team mapping logic needs further adjustment.")
else:
    print("❌ Error: Metadata file was not recreated")

print("\n=== Next Steps ===")
print("1. Open output_files/management_dashboard_2025_08.html")
print("2. Click on ASSEMBLY team card")
print("3. Verify all charts show consistent member count (109)")
print("4. Check that team member table shows 100 actual rows (109 - 9 resignations or filters)")