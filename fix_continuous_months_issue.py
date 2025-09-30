#!/usr/bin/env python3
"""
Continuous_Months 리셋 문제 해결
- 조건 충족율이 80% 이상이면 인센티브 지급하도록 수정
- 100% 미만이어도 일정 기준 이상이면 연속 개월 유지
"""

import pandas as pd
import json
import shutil
from datetime import datetime

print("="*80)
print("🔧 CONTINUOUS MONTHS RESET ISSUE FIX")
print("="*80)

# 1. position_condition_matrix.json 업데이트
config_file = 'config_files/position_condition_matrix.json'
backup_config = f'config_files/position_condition_matrix_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
shutil.copy(config_file, backup_config)
print(f"✅ Config backup created: {backup_config}")

with open(config_file, 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

# pass_rate_threshold 추가 (80%로 설정)
if 'global_settings' not in position_matrix:
    position_matrix['global_settings'] = {}

position_matrix['global_settings']['pass_rate_threshold'] = 80  # 80% 이상이면 인센티브 지급

# 각 직책에 대해서도 threshold 설정 가능하도록
for code in ['QA2B', 'E', 'Z', 'A1A', 'A1B']:
    if code in position_matrix.get('positions', {}):
        position_matrix['positions'][code]['pass_rate_threshold'] = 80

with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(position_matrix, f, ensure_ascii=False, indent=2)

print("✅ position_condition_matrix.json updated with pass_rate_threshold")

# 2. 계산 로직 수정
calc_file = 'src/step1_인센티브_계산_개선버전.py'
backup_calc = f'src/step1_인센티브_계산_개선버전_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy(calc_file, backup_calc)
print(f"✅ Calculation script backup created: {backup_calc}")

with open(calc_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\n[1] Searching for pass_rate threshold logic...")

# 수정할 부분들 찾기
modifications = []

for i in range(len(lines)):
    # MODEL MASTER의 100% 체크를 80%로 변경
    if 'elif pass_rate < 100:  # 100% 미충족' in lines[i]:
        lines[i] = '            elif pass_rate < 80:  # 80% 미충족 (threshold 변경)\n'
        modifications.append(f"Line {i+1}: Changed MODEL MASTER threshold from 100% to 80%")

    # Auditor/Trainer의 조건 체크 수정
    if 'if attendance_fail or continuous_fail or aql_fail:' in lines[i]:
        # 전체 로직을 pass_rate 기반으로 변경
        new_logic = """            # Pass rate 기반 인센티브 결정 (80% threshold)
            position_code = row.get('FINAL QIP POSITION NAME CODE', '')
            pass_rate_calculated = row.get('conditions_pass_rate', 0)

            # position_matrix에서 threshold 가져오기
            threshold = 80  # 기본값
            if position_code in self.position_matrix.get('positions', {}):
                threshold = self.position_matrix['positions'][position_code].get('pass_rate_threshold', 80)

            if pass_rate_calculated < threshold:
                incentive = 0
                # 조건 미충족 시 Continuous_Months = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                print(f"    → {row.get('Full Name', 'Unknown')}: 조건 충족률 {pass_rate_calculated:.1f}% < {threshold}% → 0 VND")
"""
        lines[i] = new_logic
        modifications.append(f"Line {i+1}: Updated Auditor/Trainer with pass_rate threshold logic")

# Write back
with open(calc_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n✅ Applied {len(modifications)} modifications")
for mod in modifications:
    print(f"   - {mod}")

# 3. 추가 수정: CSV 후처리로 문제 해결
print("\n[2] Creating post-processing script for immediate fix...")

post_process_script = '''#!/usr/bin/env python3
"""
CSV 후처리 스크립트 - Continuous_Months 문제 즉시 해결
"""

import pandas as pd
import json

# CSV 로드
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')

# position_condition_matrix 로드
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

print("Fixing high pass rate employees with 0 incentive...")

# 80% 이상 조건 충족했지만 0 인센티브인 직원 찾기
high_pass_zero = df[(df['conditions_pass_rate'] >= 80) & (df['September_Incentive'] == 0)]

fixed_count = 0
for idx in high_pass_zero.index:
    employee = df.loc[idx]
    emp_id = employee['Employee No']
    position = employee['QIP POSITION 1ST  NAME']
    pass_rate = employee['conditions_pass_rate']

    # Previous month에서 continuous months 계산
    prev_incentive = employee.get('Previous_Month_Incentive', 0)
    if prev_incentive > 0:
        # 이전 달 인센티브 있었으면 연속 개월 증가
        continuous_months = employee.get('Continuous_Months', 0) + 1
    else:
        continuous_months = 1  # 첫 달

    # 인센티브 금액 계산 (progressive table 사용)
    if continuous_months >= 12:
        incentive = 1000000
    elif continuous_months >= 11:
        incentive = 900000
    elif continuous_months >= 10:
        incentive = 800000
    elif continuous_months >= 9:
        incentive = 750000
    elif continuous_months >= 8:
        incentive = 700000
    elif continuous_months >= 7:
        incentive = 650000
    elif continuous_months >= 6:
        incentive = 600000
    elif continuous_months >= 5:
        incentive = 550000
    elif continuous_months >= 4:
        incentive = 450000
    elif continuous_months >= 3:
        incentive = 350000
    elif continuous_months >= 2:
        incentive = 250000
    else:
        incentive = 150000

    # 업데이트
    df.loc[idx, 'September_Incentive'] = incentive
    df.loc[idx, 'Final Incentive amount'] = incentive
    df.loc[idx, 'Continuous_Months'] = continuous_months
    df.loc[idx, 'Final_Incentive_Status'] = 'yes'

    fixed_count += 1
    print(f"  Fixed: {employee['Full Name']} ({position}) - {continuous_months} months → {incentive:,} VND")

print(f"\\nFixed {fixed_count} employees")

# 파일 저장
df.to_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.csv', index=False)
print("\\n✅ Saved fixed CSV: output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.csv")

# Excel도 업데이트
df.to_excel('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.xlsx', index=False)
print("✅ Saved fixed Excel: output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.xlsx")
'''

with open('fix_csv_post_process.py', 'w') as f:
    f.write(post_process_script)

print("✅ Created fix_csv_post_process.py")

print("\n" + "="*80)
print("Continuous Months issue fix completed!")
print("\nNext steps:")
print("1. Run: python fix_csv_post_process.py")
print("2. Generate dashboard with fixed data")
print("3. Verify all 24 employees now receive incentives")
print("="*80)