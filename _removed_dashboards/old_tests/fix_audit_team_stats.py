import pandas as pd
import json

print("="*80)
print("AUDIT & TRAINING TEAM 통계 불일치 수정 방안")
print("="*80)
print()

# Load CSV
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

# Filter AUDIT & TRAINING TEAM
audit_team = df[
    (df['QIP POSITION 1ST  NAME'].str.contains('AUDIT|TRAINING', na=False, case=False)) &
    (df['ROLE TYPE STD'] == 'TYPE-1')
]

print("현재 상황:")
print("-" * 50)
print(f"AUDIT & TRAINING TEAM: {len(audit_team)}명")
print()

# Count actual incentive receivers
incentive_receivers = (audit_team['August_Incentive'] > 0).sum()
no_incentive = (audit_team['August_Incentive'] == 0).sum()

print(f"인센티브 수령자: {incentive_receivers}명")
print(f"인센티브 미수령자: {no_incentive}명")
print()

# Count by condition status
all_conditions_pass = 0
for _, emp in audit_team.iterrows():
    conditions = [
        'cond_1_attendance_rate',
        'cond_2_unapproved_absence',
        'cond_3_actual_working_days',
        'cond_4_minimum_days',
        'cond_7_aql_team_area',
        'cond_8_area_reject'
    ]

    all_pass = True
    for cond_col in conditions:
        if cond_col in emp.index and emp[cond_col] == 'FAIL':
            all_pass = False
            break
    if all_pass:
        all_conditions_pass += 1

print(f"CSV 조건 모두 충족: {all_conditions_pass}명")
print(f"CSV 조건 미충족: {len(audit_team) - all_conditions_pass}명")
print()

print("문제점:")
print("-" * 50)
print("1. CSV의 조건 충족 상태(6명 충족)와 실제 인센티브 수령(5명)이 다름")
print("2. NGUYỄN THANH TRÚC: 모든 조건 충족했지만 Building A 연속 실패자로 인센티브 0")
print()

print("해결 방안:")
print("-" * 50)
print()

print("방안 1: CSV에 '최종 인센티브 조건' 컬럼 추가")
print("  - 연속 실패자 영향을 포함한 최종 조건 상태를 CSV에 저장")
print("  - 예: 'final_condition_status' = 'FAIL' (연속 실패자 영향)")
print()

print("방안 2: 대시보드에서 실제 인센티브 기준으로 통계 계산")
print("  - 조건 충족 통계를 CSV 조건이 아닌 실제 인센티브 수령 여부로 계산")
print("  - JavaScript 코드 수정:")
print()

print("수정할 코드 (integrated_dashboard_final.py):")
print("-" * 50)
print("""
// 기존 코드 (라인 5141-5169)
// 각 직원의 조건 충족 통계 계산
const conditionStats = {};
...

// 수정된 코드 - 실제 인센티브 기준으로 계산
const actualPassCount = employees.filter(emp =>
    parseInt(emp.august_incentive) > 0
).length;

const actualFailCount = employees.filter(emp =>
    parseInt(emp.august_incentive) === 0
).length;

// 통계 표시 부분도 수정
// "조건 충족" → "인센티브 수령"
// "조건 미충족" → "인센티브 미수령"
""")

print()
print("방안 3: 별도 설명 추가")
print("  - 조건 충족과 인센티브 수령이 다를 수 있음을 명시")
print("  - '※ 담당 구역 연속 실패자로 인해 조건 충족해도 인센티브 미지급 가능'")
print()

print("권장 방안: 방안 2")
print("  - 사용자가 실제로 관심있는 것은 인센티브 수령 여부")
print("  - 통계를 '조건 충족'이 아닌 '인센티브 수령' 기준으로 표시")