import pandas as pd
import json

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

print("="*80)
print("NGUYỄN THANH TRÚC 인센티브 0 VND 원인 분석")
print("="*80)
print()

# Find employee
emp = df[(df['Employee No'] == '620070013') | (df['Employee No'] == 620070013)].iloc[0]

print(f"직원: {emp['Full Name']} ({emp['Employee No']})")
print(f"직급: {emp['QIP POSITION 1ST  NAME']}")
print()

# 1. Check attendance conditions
print("1. 출근 조건 체크:")
attendance_cols = [
    'attendancy condition 1 - acctual working days is zero',
    'attendancy condition 2 - unapproved Absence Day is more than 2 days',
    'attendancy condition 3 - absent % is over 12%',
    'attendancy condition 4 - minimum working days'
]

attendance_fail = False
for col in attendance_cols:
    if col in emp.index:
        value = emp[col]
        if value == 'yes':
            attendance_fail = True
            print(f"  ❌ {col}: {value}")
        else:
            print(f"  ✅ {col}: {value}")
    else:
        print(f"  ? {col}: 컬럼 없음")

print(f"  → 출근 조건 실패: {attendance_fail}")
print()

# 2. Check AQL failures
print("2. AQL 실패 체크:")
aql_col = 'August AQL Failures'
if aql_col in emp.index:
    aql_failures = emp[aql_col]
    print(f"  8월 AQL 실패: {aql_failures}")
    aql_fail = aql_failures > 0 if pd.notna(aql_failures) else False
else:
    print(f"  {aql_col} 컬럼 없음")
    aql_fail = False

# Check continuous fail
continuous_fail_col = 'Continuous_FAIL'
if continuous_fail_col in emp.index:
    continuous_fail = emp[continuous_fail_col]
    print(f"  연속 실패: {continuous_fail}")
    continuous_fail = continuous_fail == 'YES'
else:
    print(f"  {continuous_fail_col} 컬럼 없음")
    continuous_fail = False

print(f"  → AQL/연속 실패: {aql_fail or continuous_fail}")
print()

# 3. Check area reject rate (from condition 8)
print("3. 담당 구역 reject율 체크:")
area_reject = emp.get('cond_8_value', 0)
print(f"  담당 구역 reject율: {area_reject}%")
print(f"  → reject율 ≥ 3%: {area_reject >= 3}")
print()

# 4. Check for continuous failures in factory
print("4. 담당 공장 3개월 연속 실패자 체크:")
print("  이 정보는 코드 실행 중에 계산되므로 CSV에서 직접 확인 불가")
print("  하지만 조건 7(팀/구역 AQL)이 PASS이므로 이 조건도 PASS일 가능성이 높음")
print()

# 5. Check July incentive and continuous months
print("5. Progressive Incentive 체크:")
july_incentive = emp.get('July_Incentive', 0)
print(f"  7월 인센티브: {july_incentive:,.0f} VND")

if july_incentive == 450000:
    print("  → 7월에 5개월차 또는 6개월차였음")
    print("  → 8월 조건 충족 시 6개월차 또는 7개월차로 450,000 또는 500,000 VND 예상")
    print()

# Load auditor_trainer_areas.json to check area mapping
try:
    with open('config_files/auditor_trainer_areas.json', 'r', encoding='utf-8') as f:
        area_mapping = json.load(f)

    if '620070013' in area_mapping.get('auditor_trainer_areas', {}):
        area_info = area_mapping['auditor_trainer_areas']['620070013']
        print("6. 담당 구역 매핑 정보:")
        print(f"  담당 구역: {area_info}")

        # Check if there's a specific condition causing 0
        if 'enabled' in area_info and not area_info['enabled']:
            print("  ⚠️ 담당 구역 매핑이 비활성화되어 있음!")
    else:
        print("6. 담당 구역 매핑 없음")
except FileNotFoundError:
    print("6. auditor_trainer_areas.json 파일 없음")

print()
print("="*80)
print("결론:")
print("="*80)

if not attendance_fail and not aql_fail and not continuous_fail and area_reject < 3:
    print("⚠️ 모든 명시적 조건을 충족했는데도 0 VND!")
    print()
    print("가능한 원인:")
    print("1. 담당 공장에 3개월 연속 실패자가 있음 (코드 라인 2206-2209)")
    print("2. calculate_continuous_months_from_history가 0을 반환")
    print("3. 특별한 예외 처리나 하드코딩된 조건")
    print("4. 데이터 타입 문제나 계산 오류")
else:
    print("위 조건 중 하나 이상 실패하여 0 VND")