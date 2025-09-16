import pandas as pd
from datetime import datetime

print("="*80)
print("9월 1일 이후 입사자 인센티브 지급 현황 (Entrance Date 기준)")
print("="*80)
print()

# CSV 파일 로드
csv_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv'
df = pd.read_csv(csv_file)

# Entrance Date 컬럼 사용
if 'Entrance Date' in df.columns:
    # 날짜 형식으로 변환
    df['Entrance Date'] = pd.to_datetime(df['Entrance Date'], errors='coerce')

    # 유효한 입사일이 있는 직원 수
    has_entrance_date = df['Entrance Date'].notna().sum()
    print(f"입사일 정보가 있는 직원: {has_entrance_date}명 / 전체 {len(df)}명")
    print()

    # 9월 1일 이후 입사자 필터링
    september_start = pd.Timestamp('2025-09-01')
    september_employees = df[df['Entrance Date'] >= september_start]

    print("1. 9월 1일 이후 입사자 현황:")
    print("-" * 50)
    print(f"9월 이후 입사자: {len(september_employees)}명")

    if len(september_employees) > 0:
        print("\n상세 명단:")
        print("-" * 100)
        print(f"{'이름':<30} {'사원번호':<12} {'입사일':<12} {'직급':<30} {'8월 인센티브':>15}")
        print("-" * 100)

        for _, emp in september_employees.iterrows():
            name = str(emp['Full Name'])[:30]
            emp_no = emp['Employee No']
            entrance_date = emp['Entrance Date'].strftime('%Y-%m-%d') if pd.notna(emp['Entrance Date']) else 'N/A'
            position = str(emp['QIP POSITION 1ST  NAME'])[:30]
            incentive = emp['August_Incentive']

            print(f"{name:<30} {str(emp_no):<12} {entrance_date:<12} {position:<30} {incentive:>12,.0f} VND")

        print("-" * 100)

        # 통계
        total_incentive = september_employees['August_Incentive'].sum()
        paid_count = (september_employees['August_Incentive'] > 0).sum()

        print(f"요약: 총 {len(september_employees)}명")
        print(f"      인센티브 수령: {paid_count}명")
        print(f"      총 지급액: {total_incentive:,.0f} VND")

    print()

    # 8월 입사자 분석 (비교용)
    august_start = pd.Timestamp('2025-08-01')
    august_end = pd.Timestamp('2025-08-31')
    august_employees = df[(df['Entrance Date'] >= august_start) & (df['Entrance Date'] <= august_end)]

    print("2. 8월 입사자 현황 (비교):")
    print("-" * 50)
    print(f"8월 입사자: {len(august_employees)}명")

    if len(august_employees) > 0:
        august_paid = (august_employees['August_Incentive'] > 0).sum()
        august_unpaid = (august_employees['August_Incentive'] == 0).sum()

        print(f"  - 인센티브 수령: {august_paid}명")
        print(f"  - 인센티브 미수령: {august_unpaid}명")

        # 8월 후반 입사자 분석
        august_late = df[df['Entrance Date'] >= pd.Timestamp('2025-08-15')]
        august_late_paid = (august_late['August_Incentive'] > 0).sum()

        print(f"\n8월 15일 이후 입사자: {len(august_late)}명")
        print(f"  - 인센티브 수령: {august_late_paid}명")

        if august_paid > 0:
            print("\n8월 입사자 중 인센티브 받은 사례 (상위 5명):")
            august_with_incentive = august_employees[august_employees['August_Incentive'] > 0].nlargest(5, 'August_Incentive')

            for _, emp in august_with_incentive.iterrows():
                name = str(emp['Full Name'])[:30]
                entrance = emp['Entrance Date'].strftime('%m/%d') if pd.notna(emp['Entrance Date']) else 'N/A'
                working_days = emp.get('Actual Working Days', 0)
                incentive = emp['August_Incentive']
                position = str(emp['QIP POSITION 1ST  NAME'])[:25]

                print(f"  - {name}: {entrance} 입사, 근무 {working_days}일, {position}, {incentive:,.0f} VND")

    print()

    # 최근 입사자 전체 현황
    print("3. 최근 3개월 입사자 전체 현황:")
    print("-" * 50)

    july_start = pd.Timestamp('2025-07-01')
    recent_employees = df[df['Entrance Date'] >= july_start]

    # 월별 그룹화
    for month in [7, 8, 9]:
        month_start = pd.Timestamp(f'2025-{month:02d}-01')
        if month < 12:
            month_end = pd.Timestamp(f'2025-{month+1:02d}-01') - pd.Timedelta(days=1)
        else:
            month_end = pd.Timestamp('2025-12-31')

        month_employees = df[(df['Entrance Date'] >= month_start) & (df['Entrance Date'] <= month_end)]
        month_paid = (month_employees['August_Incentive'] > 0).sum()

        month_name = ['', '', '', '', '', '', '7월', '8월', '9월'][month-1]
        print(f"{month_name} 입사: {len(month_employees):3}명 (8월 인센티브 수령: {month_paid}명)")

    print()

    # 인센티브 지급 조건 확인
    print("4. 인센티브 지급 조건:")
    print("-" * 50)
    print("• 최소 근무일: 12일 이상")
    print("• 출근율: 88% 이상")
    print("• 무단결근: 2일 이하")
    print("• 기타: 직급별 추가 조건")
    print()
    print("※ 9월 1일 이후 입사자는 8월 근무일이 0일이므로")
    print("  최소 근무일 조건을 충족할 수 없어 인센티브 지급 대상이 아닙니다.")

else:
    print("❌ 'Entrance Date' 컬럼이 없습니다.")

print()
print("="*80)
print("최종 결론:")
print("="*80)

if 'Entrance Date' in df.columns:
    if len(september_employees) > 0:
        total = september_employees['August_Incentive'].sum()
        if total == 0:
            print(f"✅ 9월 1일 이후 입사자 {len(september_employees)}명 모두 8월 인센티브 미지급")
            print("   → 8월 근무일 0일로 최소 근무일(12일) 조건 미충족")
        else:
            print(f"⚠️ 9월 입사자 중 일부가 인센티브를 받았습니다.")
            print(f"   → 총 {len(september_employees)}명 중 {(september_employees['August_Incentive'] > 0).sum()}명 수령")
            print(f"   → 총액: {total:,.0f} VND")
    else:
        print("✅ 9월 1일 이후 입사자가 없습니다.")
else:
    print("데이터를 확인할 수 없습니다.")

print("="*80)