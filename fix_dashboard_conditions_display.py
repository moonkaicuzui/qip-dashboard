#!/usr/bin/env python3
"""
대시보드 JavaScript 조건 표시 문제 해결
- position_condition_matrix.json을 참조하여 올바른 조건 표시
"""

import json
import shutil
from datetime import datetime

print("="*80)
print("🔧 DASHBOARD CONDITIONS DISPLAY FIX")
print("="*80)

# Load position_condition_matrix.json to understand correct conditions
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

print("[1] Understanding position conditions from JSON...")
# Build a mapping of FINAL CODE to conditions
code_to_conditions = {}
for code, config in position_matrix.get('positions', {}).items():
    code_to_conditions[code] = {
        'type': config.get('type'),
        'conditions': config.get('applicable_conditions', []),
        'position_name': config.get('position_name', '')
    }

# Also add fallback positions
if 'fallback_positions' in position_matrix:
    for position_name, config in position_matrix['fallback_positions'].items():
        code_to_conditions[f'FALLBACK_{position_name}'] = {
            'type': config.get('type'),
            'conditions': config.get('conditions', []),
            'position_name': position_name
        }

print(f"   Loaded {len(code_to_conditions)} position configurations")

# Show MODEL MASTER configuration
if 'D' in code_to_conditions:
    print(f"   MODEL MASTER (Code 'D'): Conditions {code_to_conditions['D']['conditions']}")

# 2. Backup and modify integrated_dashboard_final.py
original_file = 'integrated_dashboard_final.py'
backup_file = f'integrated_dashboard_final_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy(original_file, backup_file)
print(f"\n✅ Backup created: {backup_file}")

print("\n[2] Fixing dashboard JavaScript condition display logic...")

with open(original_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the JavaScript section where conditions are determined
# We need to inject the position_condition_matrix data into JavaScript

# Create JavaScript object with position conditions
js_position_conditions = "const positionConditionsMatrix = " + json.dumps(code_to_conditions, ensure_ascii=False) + ";\n"

# Find where to inject this data (before the evaluateEmployeeConditions function)
if 'function evaluateEmployeeConditions' in content:
    # Insert the position conditions matrix before this function
    content = content.replace(
        'function evaluateEmployeeConditions',
        js_position_conditions + '\n        function evaluateEmployeeConditions'
    )
    print("   ✅ Injected position_condition_matrix data into JavaScript")

# Now modify the evaluateEmployeeConditions function to use this data
# Find and replace the condition determination logic

# Create a new function that uses position_condition_matrix
new_condition_logic = """
        // Helper function to get conditions from position_condition_matrix
        function getConditionsForEmployee(employee) {
            const finalCode = employee['FINAL QIP POSITION NAME CODE'];
            const positionName = employee['QIP POSITION 1ST  NAME'];
            const type = employee['Type'];

            // First try: Use FINAL CODE from position matrix
            if (finalCode && positionConditionsMatrix[finalCode]) {
                return positionConditionsMatrix[finalCode].conditions || [];
            }

            // Second try: Use fallback based on position name
            if (positionName) {
                const fallbackKey = 'FALLBACK_' + positionName.toUpperCase().replace(/ /g, '_');
                if (positionConditionsMatrix[fallbackKey]) {
                    return positionConditionsMatrix[fallbackKey].conditions || [];
                }
            }

            // Third try: Default based on type
            if (type === 'TYPE-1') {
                // Check specific position names
                if (positionName && positionName.toUpperCase().includes('MODEL MASTER')) {
                    return [1, 2, 3, 4, 8];  // MODEL MASTER conditions
                } else if (positionName && positionName.toUpperCase().includes('ASSEMBLY INSPECTOR')) {
                    return [1, 2, 3, 4, 5, 6, 9, 10];  // Assembly Inspector conditions
                } else {
                    return [1, 2, 3, 4];  // Default TYPE-1
                }
            } else if (type === 'TYPE-2') {
                return [1, 2, 3, 4];  // TYPE-2 only attendance
            } else {
                return [];  // TYPE-3 no conditions
            }
        }
"""

# Insert this helper function
if 'function evaluateEmployeeConditions' in content:
    content = content.replace(
        'function evaluateEmployeeConditions',
        new_condition_logic + '\n        function evaluateEmployeeConditions'
    )
    print("   ✅ Added getConditionsForEmployee helper function")

# Now update evaluateEmployeeConditions to use the helper
# Replace the hardcoded condition logic with a call to getConditionsForEmployee

# Find the section where applicableConditions is set
# This is around the part with "if (typeUpper === 'TYPE-1')"

import re

# Pattern to find the condition assignment logic
pattern = r'let applicableConditions = \[\];[\s\S]*?// Ensure no duplicates'

# Replace with new logic using the helper function
replacement = """let applicableConditions = getConditionsForEmployee(employee);

            // Ensure no duplicates"""

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content, count=1)
    print("   ✅ Updated evaluateEmployeeConditions to use position_condition_matrix")
else:
    print("   ⚠️ Could not find exact pattern to replace condition logic")

# Save the modified content
with open(original_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Dashboard JavaScript condition display logic fixed!")

# 3. Also check dashboard_v2 if it exists
dashboard_v2_file = 'dashboard_v2/static/js/dashboard_complete.js'
import os
if os.path.exists(dashboard_v2_file):
    print("\n[3] Checking dashboard_v2 JavaScript...")
    backup_v2 = f'dashboard_v2/static/js/dashboard_complete_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.js'
    shutil.copy(dashboard_v2_file, backup_v2)
    print(f"   ✅ Backup created: {backup_v2}")

    # Similar fixes would need to be applied here
    print("   ⚠️ Note: dashboard_v2 also needs similar fixes")

print("\n" + "="*80)
print("Dashboard condition display fix completed!")
print("Next steps:")
print("1. Run the incentive calculation with fixed MODEL MASTER logic")
print("2. Generate new dashboard with fixed condition display")
print("3. Verify MODEL MASTER shows conditions 1,2,3,4,8")
print("="*80)