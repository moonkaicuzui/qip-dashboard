import pandas as pd
import json

print("="*80)
print("AUDIT & TRAINING TEAM 통계 불일치 분석")
print("="*80)
print()

# Load CSV data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

# Filter AUDIT & TRAINING TEAM
audit_team = df[
    (df['QIP POSITION 1ST  NAME'].str.contains('AUDIT|TRAINING', na=False, case=False)) &
    (df['ROLE TYPE STD'] == 'TYPE-1')
]

print(f"AUDIT & TRAINING TEAM 총 인원: {len(audit_team)}명")
print()

# Analyze each condition
conditions = [
    ('조건 1 (출근율 88%)', 'cond_1_attendance_rate'),
    ('조건 2 (무단결근 2일)', 'cond_2_unapproved_absence'),
    ('조건 3 (실제근무일 0일 초과)', 'cond_3_actual_working_days'),
    ('조건 4 (최소 근무일 12일)', 'cond_4_minimum_days'),
    ('조건 7 (팀/구역 AQL)', 'cond_7_aql_team_area'),
    ('조건 8 (담당구역 reject < 3%)', 'cond_8_area_reject')
]

print("개별 조건 분석:")
print("-" * 50)
for cond_name, cond_col in conditions:
    if cond_col in audit_team.columns:
        pass_count = (audit_team[cond_col] == 'PASS').sum()
        fail_count = (audit_team[cond_col] == 'FAIL').sum()
        na_count = audit_team[cond_col].isna().sum()

        print(f"{cond_name}:")
        print(f"  PASS: {pass_count}명")
        print(f"  FAIL: {fail_count}명")
        if na_count > 0:
            print(f"  N/A: {na_count}명")
        print()

# Check individual employees
print("="*80)
print("직원별 상세 분석:")
print("="*80)
print()

# Load mapping for area information
with open('config_files/auditor_trainer_area_mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

for _, emp in audit_team.iterrows():
    emp_id = str(emp['Employee No'])
    name = emp['Full Name']
    incentive = emp['August_Incentive']

    print(f"{name} ({emp_id})")

    # Get area mapping
    if emp_id in mapping['auditor_trainer_areas']:
        area = mapping['auditor_trainer_areas'][emp_id]['description']
    else:
        area = "매핑 없음"
    print(f"  담당: {area}")

    # Check all conditions
    all_pass = True
    failed_conditions = []

    for cond_name, cond_col in conditions:
        if cond_col in emp.index:
            result = emp[cond_col]
            if result == 'FAIL':
                all_pass = False
                failed_conditions.append(cond_name)

    if all_pass:
        print(f"  조건: ✅ 모두 충족")
    else:
        print(f"  조건: ❌ 실패 ({', '.join(failed_conditions)})")

    print(f"  인센티브: {incentive:,.0f} VND")

    # Special case analysis
    if all_pass and incentive == 0:
        print(f"  ⚠️ 문제: 모든 조건 충족했는데 인센티브 0")
        if area == "Building A":
            print(f"     → Building A 연속 실패자 영향")
        elif area == "All Buildings - Team Leader":
            print(f"     → Team Leader 전체 구역 연속 실패자 영향 (수정 필요)")
    elif not all_pass and incentive > 0:
        print(f"  ⚠️ 문제: 조건 실패했는데 인센티브 받음")

    print()

# Summary statistics
print("="*80)
print("통계 요약:")
print("="*80)

# Count by actual incentive
incentive_receivers = (audit_team['August_Incentive'] > 0).sum()
no_incentive = (audit_team['August_Incentive'] == 0).sum()

print(f"실제 인센티브 수령: {incentive_receivers}명")
print(f"인센티브 미수령: {no_incentive}명")
print()

# Count by condition status (all conditions pass)
all_conditions_pass = 0
for _, emp in audit_team.iterrows():
    all_pass = True
    for _, cond_col in conditions:
        if cond_col in emp.index and emp[cond_col] == 'FAIL':
            all_pass = False
            break
    if all_pass:
        all_conditions_pass += 1

print(f"모든 조건 충족: {all_conditions_pass}명")
print(f"조건 미충족: {len(audit_team) - all_conditions_pass}명")
print()

print("불일치 분석:")
if all_conditions_pass != incentive_receivers:
    print(f"  ⚠️ 불일치 발견!")
    print(f"     조건 충족자({all_conditions_pass}명) ≠ 인센티브 수령자({incentive_receivers}명)")
    print(f"     차이: {abs(all_conditions_pass - incentive_receivers)}명")
else:
    print(f"  ✅ 일치")

# Find specific discrepancies
print()
print("불일치 케이스:")
for _, emp in audit_team.iterrows():
    all_pass = True
    for _, cond_col in conditions:
        if cond_col in emp.index and emp[cond_col] == 'FAIL':
            all_pass = False
            break

    has_incentive = emp['August_Incentive'] > 0

    if all_pass and not has_incentive:
        print(f"  - {emp['Full Name']}: 조건 충족했지만 인센티브 0")
    elif not all_pass and has_incentive:
        print(f"  - {emp['Full Name']}: 조건 미충족했지만 인센티브 받음")