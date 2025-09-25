import pandas as pd
import json

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

print("="*80)
print("NGUYỄN THANH TRÚC 인센티브 분석")
print("="*80)
print()

# Find employee
emp = df[(df['Employee No'] == '620070013') | (df['Employee No'] == 620070013)]
if emp.empty:
    print("직원을 찾을 수 없습니다.")
else:
    emp = emp.iloc[0]
    print(f"직원: {emp['Full Name']} ({emp['Employee No']})")
    print(f"직급: {emp['QIP POSITION 1ST  NAME']}")
    print(f"타입: {emp['ROLE TYPE STD']}")
    print(f"8월 인센티브: {emp['August_Incentive']:,.0f} VND")
    print()

    # Check attendance conditions
    print("출근 조건:")
    print(f"  1. 출근율 88% 이상: {emp.get('cond_1_attendance_rate', 'N/A')} (값: {emp.get('cond_1_value', 'N/A')})")
    print(f"  2. 무단결근 2일 이하: {emp.get('cond_2_unapproved_absence', 'N/A')} (값: {emp.get('cond_2_value', 'N/A')})")
    print(f"  3. 실제근무일 0일 초과: {emp.get('cond_3_actual_working_days', 'N/A')} (값: {emp.get('cond_3_value', 'N/A')})")
    print(f"  4. 최소 근무일 12일 이상: {emp.get('cond_4_minimum_days', 'N/A')} (값: {emp.get('cond_4_value', 'N/A')})")
    print()

    # Check specific conditions for AUDIT & TRAINING
    print("AUDIT & TRAINING TEAM 특수 조건:")
    print(f"  7. 팀/구역 AQL: {emp.get('cond_7_aql_team_area', 'N/A')} (값: {emp.get('cond_7_value', 'N/A')})")
    print(f"  8. 담당구역 reject %: {emp.get('cond_8_area_reject', 'N/A')} (값: {emp.get('cond_8_value', 'N/A')})")
    print()

    # Check July incentive
    print("이전 월 데이터:")
    print(f"  7월 인센티브: {emp.get('July_Incentive', 'N/A')}")

    # Check progressive status
    if 'continuous_month' in emp.index:
        print(f"  연속 개월 수: {emp.get('continuous_month', 'N/A')}")

    print()

    # Check actual working days
    print("추가 정보:")
    print(f"  실제 근무일: {emp.get('ACTUAL WORKING DAY', 'N/A')}")
    print(f"  출근율: {emp.get('attendancy %', 'N/A')}%")
    print(f"  무단결근일: {emp.get('Unapproved Absence Day', 'N/A')}")

    # Check Stop Working Date
    if 'Stop working Date' in emp.index:
        stop_date = emp.get('Stop working Date', '')
        if pd.notna(stop_date) and stop_date != '':
            print(f"  ⚠️ 퇴사일: {stop_date}")

    print()

    # Check if conditions are all passed
    conditions_passed = True
    failed_conditions = []

    # Check attendance conditions
    if emp.get('cond_1_attendance_rate') == 'FAIL':
        conditions_passed = False
        failed_conditions.append("출근율")
    if emp.get('cond_2_unapproved_absence') == 'FAIL':
        conditions_passed = False
        failed_conditions.append("무단결근")
    if emp.get('cond_3_actual_working_days') == 'FAIL':
        conditions_passed = False
        failed_conditions.append("실제근무일")
    if emp.get('cond_4_minimum_days') == 'FAIL':
        conditions_passed = False
        failed_conditions.append("최소근무일")

    # Check AUDIT & TRAINING specific conditions
    if emp.get('cond_7_aql_team_area') == 'FAIL':
        conditions_passed = False
        failed_conditions.append("팀/구역 AQL")
    if emp.get('cond_8_area_reject') == 'FAIL':
        conditions_passed = False
        failed_conditions.append("담당구역 reject")

    if conditions_passed:
        print("✅ 모든 조건을 충족했는데도 인센티브가 0입니다!")
        print("   가능한 원인:")
        print("   1. Progressive incentive 로직에서 실패 후 리셋")
        print("   2. 특별한 제외 조건 존재")
        print("   3. 계산 로직 오류")
    else:
        print(f"❌ 실패한 조건: {', '.join(failed_conditions)}")

# Load position condition matrix to check progressive rules
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

print()
print("="*80)
print("Progressive Incentive 규칙 확인:")
print("="*80)
print()

if 'incentive_progression' in matrix:
    progression = matrix['incentive_progression'].get('TYPE_1_PROGRESSIVE', {})
    if 'AUDITOR_TRAINER' in progression.get('applies_to', []):
        print("✅ AUDIT & TRAINING TEAM은 Progressive Incentive 대상입니다.")
        print(f"   리셋 조건: {progression.get('reset_on_fail', False)}")
        print(f"   다음 달 이월: {progression.get('carry_over_next_month', False)}")
        print()
        print("   7월에 450,000 VND를 받았다면 5개월차였습니다.")
        print("   8월에 조건을 충족했다면 6개월차로 450,000 VND를 받아야 합니다.")
        print("   하지만 0 VND를 받았다는 것은 특별한 이유가 있을 것입니다.")
    else:
        print("❌ AUDIT & TRAINING TEAM은 Progressive Incentive 대상이 아닙니다.")