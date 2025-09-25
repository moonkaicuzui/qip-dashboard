import pandas as pd
import json

print("="*80)
print("VÕ THỊ THÙY LINH (620080295) 인센티브 분석")
print("="*80)
print()

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

# Find VÕ THỊ THÙY LINH
linh = df[(df['Employee No'] == '620080295') | (df['Employee No'] == 620080295)]
if not linh.empty:
    linh = linh.iloc[0]
    print(f"직원: {linh['Full Name']} ({linh['Employee No']})")
    print(f"직급: {linh['QIP POSITION 1ST  NAME']}")
    print(f"타입: {linh['ROLE TYPE STD']}")
    print(f"8월 인센티브: {linh['August_Incentive']:,.0f} VND")
    print(f"7월 인센티브: {linh.get('July_Incentive', 0):,.0f} VND")
    print()

    # Check conditions
    print("조건 충족 상태:")
    print(f"  1. 출근율: {linh.get('cond_1_attendance_rate', 'N/A')} (값: {linh.get('cond_1_value', 'N/A')})")
    print(f"  2. 무단결근: {linh.get('cond_2_unapproved_absence', 'N/A')} (값: {linh.get('cond_2_value', 'N/A')})")
    print(f"  3. 실제근무일: {linh.get('cond_3_actual_working_days', 'N/A')} (값: {linh.get('cond_3_value', 'N/A')})")
    print(f"  4. 최소근무일: {linh.get('cond_4_minimum_days', 'N/A')} (값: {linh.get('cond_4_value', 'N/A')})")
    print(f"  7. 팀/구역 AQL: {linh.get('cond_7_aql_team_area', 'N/A')} (값: {linh.get('cond_7_value', 'N/A')})")
    print(f"  8. 담당구역 reject: {linh.get('cond_8_area_reject', 'N/A')} (값: {linh.get('cond_8_value', 'N/A')}%)")
    print()

# Load mapping
with open('config_files/auditor_trainer_area_mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Check VÕ THỊ THÙY LINH's mapping
if '620080295' in mapping['auditor_trainer_areas']:
    linh_mapping = mapping['auditor_trainer_areas']['620080295']
    print("담당 구역 매핑:")
    print(f"  이름: {linh_mapping['name']}")
    print(f"  설명: {linh_mapping['description']}")
    print(f"  조건: {linh_mapping['conditions']}")
    print()

    if linh_mapping['conditions'][0]['type'] == 'ALL':
        print("  ⚠️ 전체 구역 담당 (All Buildings)")
        print("     → 모든 건물의 연속 실패자가 영향을 미침")
else:
    print("매핑 정보 없음")

print()

# Check continuous failures
continuous_fail = df[df['Continuous_FAIL'] == 'YES']
print(f"3개월 연속 실패자 현황:")
print(f"  전체: {len(continuous_fail)}명")

if len(continuous_fail) > 0:
    for _, fail_emp in continuous_fail.iterrows():
        building = fail_emp.get('BUILDING', 'N/A')
        print(f"  - {fail_emp['Full Name']} (건물: {building})")

print()
print("="*80)
print("원인 분석:")
print("="*80)
print()

if len(continuous_fail) > 0 and linh_mapping['conditions'][0]['type'] == 'ALL':
    print("✅ 원인 확인됨!")
    print()
    print("VÕ THỊ THÙY LINH는 'All Buildings - Team Leader'로")
    print("전체 구역을 담당합니다.")
    print()
    print("전체 구역 중 어느 곳이든 3개월 연속 실패자가 있으면")
    print("인센티브를 받을 수 없습니다.")
    print()
    print(f"현재 Building A에 NGUYỄN THỊ KIM THOA가")
    print(f"3개월 연속 실패했으므로 인센티브가 0 VND입니다.")
    print()
    print("이는 Team Leader의 책임 범위가 전체 공장이기 때문입니다.")
else:
    print("다른 원인 확인 필요")

print()
print("="*80)
print("AUDIT & TRAINING TEAM 전체 현황:")
print("="*80)
print()

# Check all AUDIT & TRAINING TEAM members
audit_team = df[df['QIP POSITION 1ST  NAME'].str.contains('AUDIT|TRAINING', na=False, case=False)]
audit_team = audit_team[audit_team['ROLE TYPE STD'] == 'TYPE-1']

print(f"AUDIT & TRAINING TEAM 멤버: {len(audit_team)}명")
print()
for _, member in audit_team.iterrows():
    emp_id = str(member['Employee No'])
    name = member['Full Name']
    incentive = member['August_Incentive']

    # Check mapping
    if emp_id in mapping['auditor_trainer_areas']:
        area = mapping['auditor_trainer_areas'][emp_id]['description']
    else:
        area = "매핑 없음"

    print(f"{name} ({emp_id})")
    print(f"  담당: {area}")
    print(f"  인센티브: {incentive:,.0f} VND")

    if incentive == 0:
        if emp_id in ['620070013', '620080295']:
            if area == 'Building A' or area == 'All Buildings - Team Leader':
                print(f"  → Building A 연속 실패자로 인해 0 VND")
        elif emp_id == '619070185':
            print(f"  → 다른 조건 실패 확인 필요")
    print()