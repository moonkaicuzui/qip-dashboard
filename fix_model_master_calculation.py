#!/usr/bin/env python3
"""
MODEL MASTER 계산 문제 해결 스크립트
- 계산 시점에 conditions_pass_rate가 올바르게 평가되도록 수정
"""

import json
import pandas as pd
import shutil
from datetime import datetime

print("="*80)
print("🔧 MODEL MASTER CALCULATION FIX")
print("="*80)

# 1. Backup original file
original_file = 'src/step1_인센티브_계산_개선버전.py'
backup_file = f'src/step1_인센티브_계산_개선버전_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy(original_file, backup_file)
print(f"✅ Backup created: {backup_file}")

# 2. Read the original code
with open(original_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\n[1] Fixing MODEL MASTER calculation logic...")

# Find the problematic section (around line 2440-2455)
# We need to fix how pass_rate is calculated for MODEL MASTER

modified = False
for i in range(len(lines)):
    # Find the line where pass_rate is calculated for MODEL MASTER
    if 'pass_rate = row.get(' in lines[i] and 'conditions_pass_rate' in lines[i]:
        # Check if this is in the MODEL MASTER section
        # Look back to confirm we're in calculate_auditor_trainer_incentive
        in_model_master_section = False
        for j in range(max(0, i-20), i):
            if 'Model Master 처리' in lines[j] or 'model_master_mask' in lines[j]:
                in_model_master_section = True
                break

        if in_model_master_section:
            print(f"   Found MODEL MASTER pass_rate calculation at line {i+1}")

            # Replace the pass_rate calculation with proper condition checks
            # MODEL MASTER should check conditions 1,2,3,4,8 according to position_condition_matrix.json
            new_code = """            # MODEL MASTER 조건 체크 (1,2,3,4,8)
            # position_condition_matrix.json의 CODE 'D' 설정에 따라 조건 확인
            condition_1_pass = row.get('attendancy condition 1 - acctual working days is zero') != 'yes'
            condition_2_pass = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') != 'yes'
            condition_3_pass = row.get('attendancy condition 3 - absent % is over 12%') != 'yes'
            condition_4_pass = row.get('attendancy condition 4 - minimum working days') != 'yes'

            # Condition 8: 담당 구역 reject율 < 3%
            area_reject_rate = total_factory_reject_rate  # MODEL MASTER는 전체 공장 reject율 사용
            condition_8_pass = area_reject_rate < 3.0

            # MODEL MASTER는 모든 조건(1,2,3,4,8)을 충족해야 함
            all_conditions_pass = (condition_1_pass and condition_2_pass and
                                  condition_3_pass and condition_4_pass and
                                  condition_8_pass)

            # pass_rate 계산 (100% or 0%)
            if all_conditions_pass:
                pass_rate = 100
            else:
                failed_conditions = []
                if not condition_1_pass: failed_conditions.append('1')
                if not condition_2_pass: failed_conditions.append('2')
                if not condition_3_pass: failed_conditions.append('3')
                if not condition_4_pass: failed_conditions.append('4')
                if not condition_8_pass: failed_conditions.append('8')
                pass_rate = 0
                print(f"    → {row.get('Full Name', 'Unknown')} failed conditions: {', '.join(failed_conditions)}")
"""

            # Replace the single line with our new code block
            lines[i] = new_code + "\n"
            modified = True
            print("   ✅ Fixed pass_rate calculation for MODEL MASTER")
            break

if modified:
    # Write the modified code back
    with open(original_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("\n✅ Fixed MODEL MASTER calculation logic in step1_인센티브_계산_개선버전.py")
else:
    print("\n⚠️ Could not find the exact location to fix. Manual intervention may be needed.")

# 3. Also check if we need to update the conditions evaluation elsewhere
print("\n[2] Checking for other condition evaluation issues...")

# Load position_condition_matrix.json
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

# Check all position codes that might have similar issues
print("\n   Positions with potential calculation issues:")
codes_with_issues = []
for code, config in position_matrix.get('positions', {}).items():
    if config.get('type') == 'TYPE-1' and config.get('applicable_conditions'):
        # Check if this position might have the same issue
        if len(config['applicable_conditions']) > 4:  # More than standard conditions
            codes_with_issues.append({
                'code': code,
                'name': config.get('position_name', ''),
                'conditions': config['applicable_conditions']
            })

if codes_with_issues:
    print("   Found positions that might need similar fixes:")
    for pos in codes_with_issues:
        print(f"      - Code '{pos['code']}': {pos['name']} → Conditions: {pos['conditions']}")
else:
    print("   ✅ No other positions found with similar issues")

print("\n" + "="*80)
print("MODEL MASTER calculation fix completed!")
print("Next steps:")
print("1. Run the incentive calculation again")
print("2. Generate new dashboard")
print("3. Verify MODEL MASTER receives correct incentive")
print("="*80)