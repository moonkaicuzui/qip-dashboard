import pandas as pd

print("="*80)
print("9월 이후 입사자 인센티브 수령 예외 케이스 분석")
print("="*80)
print()

# CSV 파일 로드
csv_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv'
df = pd.read_csv(csv_file)

# 날짜 변환
df['Entrance Date'] = pd.to_datetime(df['Entrance Date'], errors='coerce')

# 9월 이후 입사자 중 인센티브 받은 사람 찾기
september_start = pd.Timestamp('2025-09-01')
september_with_incentive = df[(df['Entrance Date'] >= september_start) & (df['August_Incentive'] > 0)]

print("예외 케이스 상세 분석:")
print("-" * 80)

for idx, emp in september_with_incentive.iterrows():
    print(f"\n직원 정보:")
    print(f"  이름: {emp['Full Name']}")
    print(f"  사원번호: {emp['Employee No']}")
    print(f"  직급: {emp['QIP POSITION 1ST  NAME']}")
    print(f"  TYPE: {emp.get('ROLE TYPE STD', 'N/A')}")
    print(f"  입사일: {emp['Entrance Date'].strftime('%Y-%m-%d') if pd.notna(emp['Entrance Date']) else 'N/A'}")
    print(f"  8월 인센티브: {emp['August_Incentive']:,.0f} VND")
    print()

    print("  근무 관련 데이터:")
    print(f"    - Actual Working Days: {emp.get('Actual Working Days', 'N/A')}")
    print(f"    - Total Working Days: {emp.get('Total Working Days', 'N/A')}")
    print(f"    - Attendance Rate: {emp.get('Attendance Rate (raw)', 'N/A')}%")
    print(f"    - Absence Rate: {emp.get('Absence Rate (raw)', 'N/A')}%")
    print()

    print("  조건 충족 현황:")
    print(f"    - 조건1 (출근율): {emp.get('cond_1_attendance_rate', 'N/A')}")
    print(f"    - 조건2 (무단결근): {emp.get('cond_2_unapproved_absence', 'N/A')}")
    print(f"    - 조건3 (실제근무일): {emp.get('cond_3_actual_working_days', 'N/A')}")
    print(f"    - 조건4 (최소근무일): {emp.get('cond_4_minimum_days', 'N/A')}")
    print()

    # 입사일이 정말 9월 이후인지 재확인
    entrance_str = str(emp.get('Entrance Date', ''))
    print(f"  입사일 원본 데이터: {entrance_str}")

    # 날짜 형식 문제 가능성 확인
    if '2025-11-06' in entrance_str or '2025-12-05' in entrance_str:
        print("  ⚠️ 주의: 입사일이 11월 또는 12월로 되어 있습니다.")
        print("          → 데이터 입력 오류 가능성 (실제로는 2024년일 수 있음)")

print()
print("="*80)
print("가능한 원인 분석:")
print("="*80)

if len(september_with_incentive) > 0:
    print("1. 데이터 입력 오류:")
    print("   - 입사일이 잘못 입력됨 (연도 오타)")
    print("   - 예: 2024년을 2025년으로 잘못 입력")
    print()
    print("2. 특수 케이스:")
    print("   - 재입사자")
    print("   - 부서 이동")
    print("   - 특별 규정 적용")
    print()

    # 실제로 근무일수가 있는지 확인
    for _, emp in september_with_incentive.iterrows():
        actual_days = emp.get('Actual Working Days', 0)
        if actual_days > 0:
            print(f"⚠️ {emp['Full Name']}의 실제 근무일: {actual_days}일")
            print("   → 9월 이후 입사인데 8월에 근무일이 있음 = 데이터 오류 확실")

print()
print("권장 조치:")
print("-" * 50)
print("• 해당 직원의 입사일 데이터 재확인 필요")
print("• 실제 입사일이 2024년인지 확인")
print("• HR 부서와 데이터 정합성 검증 필요")
print("="*80)