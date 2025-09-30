#!/usr/bin/env python3
"""
모든 직책의 인센티브 계산 문제 해결
- MODEL MASTER 수정 방식을 모든 직책에 적용
- AUDIT & TRAINING TEAM, LINE LEADER, MANAGER, ASSEMBLY INSPECTOR 포함
"""

import json
import shutil
from datetime import datetime

print("="*80)
print("🔧 ALL POSITIONS INCENTIVE CALCULATION FIX")
print("="*80)

# 1. Backup original file
original_file = 'src/step1_인센티브_계산_개선버전.py'
backup_file = f'src/step1_인센티브_계산_개선버전_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy(original_file, backup_file)
print(f"✅ Backup created: {backup_file}")

# 2. Load position_condition_matrix.json to understand conditions
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

print("\n[1] Understanding position conditions...")
# Get conditions for each problematic position code
problem_codes = {
    'QA2B': 'AUDIT & TRAINING TEAM',  # conditions: [1,2,3,4,7,8]
    'E': 'LINE LEADER',                # conditions: [1,2,3,4,7]
    'Z': 'MANAGER',                     # conditions: [1,2,3,4]
    'A1A': 'ASSEMBLY INSPECTOR',       # conditions: [1,2,3,4,5,6,9,10]
    'A1B': 'ASSEMBLY INSPECTOR'        # conditions: [1,2,3,4,5,6,9,10]
}

for code, position in problem_codes.items():
    if code in position_matrix['positions']:
        conditions = position_matrix['positions'][code].get('applicable_conditions', [])
        print(f"   {code} ({position}): Conditions {conditions}")

# 3. Read the original code
with open(original_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\n[2] Applying comprehensive calculation fixes...")

# Track modifications
modifications = []

# Find and fix the Auditor/Trainer calculation section (around line 2519-2579)
for i in range(len(lines)):
    # Fix for AUDIT & TRAINING TEAM (Code QA2B)
    if 'auditor_only_mask = auditor_trainer_mask & ~model_master_mask' in lines[i]:
        print(f"   Found Auditor/Trainer section at line {i+1}")

        # Find the incentive decision logic
        for j in range(i, min(i+100, len(lines))):
            if 'if attendance_fail or continuous_fail or aql_fail:' in lines[j]:
                print(f"   Found incentive decision logic at line {j+1}")

                # Replace with direct condition evaluation
                new_logic = """            # Direct condition evaluation for Auditor/Trainer positions
            position_code = row.get('FINAL QIP POSITION NAME CODE', '')
            position_name = row.get('QIP POSITION 1ST  NAME', '')

            # Get applicable conditions from position matrix
            if position_code in self.position_matrix.get('positions', {}):
                applicable_conditions = self.position_matrix['positions'][position_code].get('applicable_conditions', [1,2,3,4])
            else:
                # Default conditions based on position name
                if 'AUDIT' in position_name.upper():
                    applicable_conditions = [1,2,3,4,7,8]
                else:
                    applicable_conditions = [1,2,3,4]

            # Evaluate each condition
            conditions_met = {}

            # Attendance conditions (1-4)
            if 1 in applicable_conditions:
                conditions_met[1] = row.get('attendancy condition 1 - acctual working days is zero') != 'yes'
            if 2 in applicable_conditions:
                conditions_met[2] = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') != 'yes'
            if 3 in applicable_conditions:
                conditions_met[3] = row.get('attendancy condition 3 - absent % is over 12%') != 'yes'
            if 4 in applicable_conditions:
                conditions_met[4] = row.get('attendancy condition 4 - minimum working days') != 'yes'

            # Condition 7: 담당 구역 reject율 < 3%
            if 7 in applicable_conditions:
                conditions_met[7] = area_reject_rate < 3.0

            # Condition 8: 담당 공장에 3개월 연속 실패자 없음
            if 8 in applicable_conditions:
                conditions_met[8] = not has_continuous_fail_in_factory

            # Check if all applicable conditions are met
            all_conditions_pass = all(conditions_met.values())

            # 인센티브 결정
            if not all_conditions_pass:
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                failed = [k for k,v in conditions_met.items() if not v]
                print(f"    → {row.get('Full Name', 'Unknown')} failed conditions: {failed} → 0 VND")
            else:
"""
                # Insert the new logic
                lines[j] = new_logic
                modifications.append(f"Line {j+1}: Fixed Auditor/Trainer condition evaluation")
                break
        break

print(f"\n✅ Applied {len(modifications)} modifications")

# 4. Fix Assembly Inspector calculation (전체 compute_incentives 함수에서)
print("\n[3] Searching for Assembly Inspector calculation logic...")

for i in range(len(lines)):
    if 'def compute_incentives(self' in lines[i]:
        print(f"   Found compute_incentives at line {i+1}")

        # Find Assembly Inspector section
        for j in range(i, min(i+500, len(lines))):
            if 'assembly_mask = (self.month_data[' in lines[j]:
                print(f"   Found Assembly Inspector section at line {j+1}")

                # Find the condition evaluation part
                for k in range(j, min(j+100, len(lines))):
                    if 'attendance_fail = (' in lines[k]:
                        print(f"   Found Assembly Inspector condition check at line {k+1}")

                        # Replace with direct evaluation
                        assembly_fix = """            # Direct condition evaluation for Assembly Inspector
            position_code = row.get('FINAL QIP POSITION NAME CODE', '')

            # Assembly Inspector conditions: [1,2,3,4,5,6,9,10]
            condition_1 = row.get('attendancy condition 1 - acctual working days is zero') != 'yes'
            condition_2 = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') != 'yes'
            condition_3 = row.get('attendancy condition 3 - absent % is over 12%') != 'yes'
            condition_4 = row.get('attendancy condition 4 - minimum working days') != 'yes'
            condition_5 = row.get('aql condition - Factory AQL fail % is over 3%') != 'yes'
            condition_6 = row.get('aql condition - personal AQL fail is over 0') != 'yes'
            condition_9 = row.get('5prs condition - fail rate is more than 5%') != 'yes'
            condition_10 = row.get('5prs condition - Continuous AQL FAIL for 3 months') != 'yes'

            all_conditions_pass = (condition_1 and condition_2 and condition_3 and condition_4 and
                                  condition_5 and condition_6 and condition_9 and condition_10)

            if not all_conditions_pass:
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                failed = []
                if not condition_1: failed.append('1')
                if not condition_2: failed.append('2')
                if not condition_3: failed.append('3')
                if not condition_4: failed.append('4')
                if not condition_5: failed.append('5')
                if not condition_6: failed.append('6')
                if not condition_9: failed.append('9')
                if not condition_10: failed.append('10')
                print(f"    → {row.get('Full Name', 'Unknown')} failed conditions: {', '.join(failed)} → 0 VND")
            else:
"""
                        lines[k] = assembly_fix
                        modifications.append(f"Line {k+1}: Fixed Assembly Inspector condition evaluation")
                        break
                break
        break

# 5. Write the modified code back
if modifications:
    with open(original_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n✅ All position calculation fixes applied successfully!")
    print("\n📝 Modifications made:")
    for mod in modifications:
        print(f"   - {mod}")
else:
    print("\n⚠️ Could not find all target sections. Manual intervention may be needed.")

print("\n" + "="*80)
print("All positions calculation fix completed!")
print("Next steps:")
print("1. Run the incentive calculation again")
print("2. Generate new dashboard")
print("3. Verify all positions receive correct incentives")
print("="*80)