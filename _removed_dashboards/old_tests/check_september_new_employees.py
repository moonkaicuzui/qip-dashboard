import pandas as pd
from datetime import datetime

print("="*80)
print("9월 1일 이후 입사자 인센티브 지급 현황")
print("="*80)
print()

# CSV 파일 로드
csv_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv'
df = pd.read_csv(csv_file)

# 입사일 관련 컬럼 확인
print("1. 입사일 관련 컬럼 확인:")
print("-" * 50)
date_columns = [col for col in df.columns if 'date' in col.lower() or 'start' in col.lower() or 'join' in col.lower()]
print(f"관련 컬럼: {date_columns}")
print()

# Joining Date가 있다면 사용
if 'Joining Date' in df.columns:
    # 날짜 형식으로 변환
    df['Joining Date'] = pd.to_datetime(df['Joining Date'], errors='coerce')

    # 9월 1일 이후 입사자 필터링
    september_start = pd.Timestamp('2025-09-01')

    # 9월 이후 입사자
    september_employees = df[df['Joining Date'] >= september_start]

    print("2. 9월 1일 이후 입사자 현황:")
    print("-" * 50)
    print(f"총 인원: {len(september_employees)}명")

    if len(september_employees) > 0:
        print("\n상세 명단:")
        print("-" * 80)
        print(f"{'이름':<25} {'사원번호':<12} {'입사일':<12} {'직급':<25} {'인센티브':<15}")
        print("-" * 80)

        total_incentive = 0
        paid_count = 0

        for _, emp in september_employees.iterrows():
            name = emp['Full Name'][:25]
            emp_no = emp['Employee No']
            join_date = emp['Joining Date'].strftime('%Y-%m-%d') if pd.notna(emp['Joining Date']) else 'N/A'
            position = str(emp['QIP POSITION 1ST  NAME'])[:25]
            incentive = emp['August_Incentive']

            print(f"{name:<25} {str(emp_no):<12} {join_date:<12} {position:<25} {incentive:>12,.0f} VND")

            total_incentive += incentive
            if incentive > 0:
                paid_count += 1

        print("-" * 80)
        print(f"합계: {len(september_employees)}명, 인센티브 수령: {paid_count}명, 총액: {total_incentive:,.0f} VND")

    print()

    # 8월 입사자도 확인 (비교용)
    august_start = pd.Timestamp('2025-08-01')
    august_end = pd.Timestamp('2025-08-31')
    august_employees = df[(df['Joining Date'] >= august_start) & (df['Joining Date'] <= august_end)]

    print("3. 8월 입사자 현황 (비교용):")
    print("-" * 50)
    print(f"총 인원: {len(august_employees)}명")

    if len(august_employees) > 0:
        # 인센티브 받은 사람과 못 받은 사람 분석
        august_with_incentive = august_employees[august_employees['August_Incentive'] > 0]
        august_without_incentive = august_employees[august_employees['August_Incentive'] == 0]

        print(f"인센티브 받은 8월 입사자: {len(august_with_incentive)}명")
        print(f"인센티브 못 받은 8월 입사자: {len(august_without_incentive)}명")

        if len(august_with_incentive) > 0:
            print("\n8월 입사자 중 인센티브 받은 사람:")
            for _, emp in august_with_incentive.head(5).iterrows():
                name = emp['Full Name'][:30]
                join_date = emp['Joining Date'].strftime('%Y-%m-%d') if pd.notna(emp['Joining Date']) else 'N/A'
                actual_days = emp.get('Actual Working Days', 0)
                incentive = emp['August_Incentive']
                print(f"  - {name}: 입사 {join_date}, 근무 {actual_days}일, {incentive:,.0f} VND")

    print()

    # 최소 근무일 조건 확인
    print("4. 인센티브 지급 조건 분석:")
    print("-" * 50)
    print("최소 근무일 조건: 12일 이상")
    print("8월 총 근무일: 약 22-27일")

    if len(september_employees) > 0:
        print("\n9월 1일 이후 입사자:")
        print("  → 8월 근무일 = 0일")
        print("  → 최소 근무일 12일 미충족")
        print("  → 인센티브 지급 대상 아님")

else:
    print("❌ 'Joining Date' 컬럼이 없습니다.")

print()
print("="*80)
print("결론:")
print("="*80)

# 결론 도출
if 'Joining Date' in df.columns and len(september_employees) > 0:
    if september_employees['August_Incentive'].sum() == 0:
        print("✅ 9월 1일 이후 입사자는 8월 인센티브를 받지 않습니다.")
        print("   이유: 8월에 근무하지 않아 최소 근무일 조건(12일) 미충족")
    else:
        print("⚠️ 일부 9월 입사자가 인센티브를 받았습니다. (데이터 확인 필요)")
else:
    print("9월 1일 이후 입사자가 없거나 데이터를 확인할 수 없습니다.")

print("="*80)