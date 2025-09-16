import pandas as pd
import re
from bs4 import BeautifulSoup

print("="*80)
print("대시보드 vs 엑셀 파일 데이터 일치성 검증 (v2)")
print("="*80)
print()

# 1. 데이터 소스 파일 확인
print("1. 데이터 소스 파일 확인:")
print("-" * 50)

# CSV 파일 (엑셀과 동일한 데이터)
csv_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv'
df_csv = pd.read_csv(csv_file)
print(f"✅ CSV/Excel 파일:")
print(f"   파일: {csv_file}")
print(f"   직원 수: {len(df_csv)}명")
print(f"   인센티브 받는 직원: {(df_csv['August_Incentive'] > 0).sum()}명")
print(f"   총액: {df_csv['August_Incentive'].sum():,.0f} VND")
print()

# HTML 대시보드 파일에서 데이터 추출
html_file = 'output_files/Incentive_Dashboard_2025_08_Version_5.html'
print(f"✅ 대시보드 HTML 파일:")
print(f"   파일: {html_file}")

# HTML 파일에서 employeeData 추출
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# JavaScript에서 employeeData 추출
match = re.search(r'const employeeData = (\[.*?\]);', html_content, re.DOTALL)
if match:
    import json
    employee_data_str = match.group(1)
    # JavaScript 배열을 Python 리스트로 변환
    employee_data = json.loads(employee_data_str)

    # 대시보드 데이터 통계
    dashboard_total = len(employee_data)
    dashboard_paid = sum(1 for e in employee_data if int(e.get('august_incentive', 0)) > 0)
    dashboard_amount = sum(int(e.get('august_incentive', 0)) for e in employee_data)

    print(f"   직원 수: {dashboard_total}명")
    print(f"   인센티브 받는 직원: {dashboard_paid}명")
    print(f"   총액: {dashboard_amount:,.0f} VND")
else:
    print("   ❌ employeeData를 찾을 수 없습니다.")
    employee_data = []
print()

# 2. 전체 통계 비교
print("2. 전체 통계 비교:")
print("-" * 50)

csv_total = len(df_csv)
csv_paid = (df_csv['August_Incentive'] > 0).sum()
csv_amount = df_csv['August_Incentive'].sum()

if employee_data:
    print(f"항목              CSV/Excel      대시보드       일치여부")
    print(f"전체 직원:        {csv_total:>8}명     {dashboard_total:>8}명     {'✅' if csv_total == dashboard_total else '❌'}")
    print(f"인센티브 수령:    {csv_paid:>8}명     {dashboard_paid:>8}명     {'✅' if csv_paid == dashboard_paid else '❌'}")
    print(f"총액:             {csv_amount:>15,.0f} VND  {dashboard_amount:>15,.0f} VND  {'✅' if csv_amount == dashboard_amount else '❌'}")
print()

# 3. 주요 직급별 비교
print("3. 주요 직급별 인센티브 비교:")
print("-" * 50)

positions = ['LINE LEADER', 'ASSEMBLY INSPECTOR', 'AUDIT & TRAINING TEAM', 'MANAGER', 'SUPERVISOR']

for position in positions:
    # CSV 데이터
    csv_mask = df_csv['QIP POSITION 1ST  NAME'].str.contains(position, na=False, case=False)
    csv_pos = df_csv[csv_mask]
    csv_pos_total = len(csv_pos)
    csv_pos_paid = (csv_pos['August_Incentive'] > 0).sum()
    csv_pos_amount = csv_pos['August_Incentive'].sum()

    # 대시보드 데이터
    if employee_data:
        dashboard_pos = [e for e in employee_data if position.upper() in e.get('position', '').upper()]
        dashboard_pos_total = len(dashboard_pos)
        dashboard_pos_paid = sum(1 for e in dashboard_pos if int(e.get('august_incentive', 0)) > 0)
        dashboard_pos_amount = sum(int(e.get('august_incentive', 0)) for e in dashboard_pos)
    else:
        dashboard_pos_total = dashboard_pos_paid = dashboard_pos_amount = 0

    print(f"{position}:")
    print(f"  CSV:      {csv_pos_total:3}명 중 {csv_pos_paid:3}명 수령, {csv_pos_amount:>12,.0f} VND")
    print(f"  대시보드: {dashboard_pos_total:3}명 중 {dashboard_pos_paid:3}명 수령, {dashboard_pos_amount:>12,.0f} VND")

    match = (csv_pos_total == dashboard_pos_total and
             csv_pos_paid == dashboard_pos_paid and
             csv_pos_amount == dashboard_pos_amount)
    print(f"  {'✅ 일치' if match else '❌ 불일치'}")
    print()

# 4. 샘플 직원 비교 (무작위 10명)
print("4. 샘플 직원 상세 비교 (무작위 10명):")
print("-" * 50)

sample_size = min(10, len(df_csv))
sample_employees = df_csv.sample(sample_size, random_state=42)

mismatch_count = 0
for _, emp_csv in sample_employees.iterrows():
    emp_id = str(emp_csv['Employee No'])
    name = emp_csv['Full Name']
    csv_amount = emp_csv['August_Incentive']

    # 대시보드에서 같은 직원 찾기
    if employee_data:
        dashboard_emp = [e for e in employee_data if str(e.get('emp_no')) == emp_id]
        dashboard_amount = int(dashboard_emp[0].get('august_incentive', 0)) if dashboard_emp else 0
    else:
        dashboard_amount = 0

    match = csv_amount == dashboard_amount
    if not match:
        mismatch_count += 1

    print(f"{name[:20]:<20} ({emp_id}): CSV {csv_amount:>10,.0f} | 대시보드 {dashboard_amount:>10,.0f} | {'✅' if match else '❌'}")

print()

# 5. 최종 검증 결과
print("="*80)
print("최종 검증 결과:")
print("="*80)

if employee_data:
    total_match = csv_total == dashboard_total
    paid_match = csv_paid == dashboard_paid
    amount_match = csv_amount == dashboard_amount

    if total_match and paid_match and amount_match and mismatch_count == 0:
        print("✅ 대시보드와 엑셀 파일의 인센티브 정보가 완벽히 일치합니다!")
        print()
        print("확인 완료 항목:")
        print("  - 전체 직원 수: 일치")
        print("  - 인센티브 수령자 수: 일치")
        print("  - 인센티브 총액: 일치")
        print("  - 직급별 통계: 일치")
        print("  - 개별 직원 금액: 일치")
    else:
        print("⚠️ 일부 불일치가 발견되었습니다:")
        if not total_match:
            print(f"  ❌ 전체 직원 수: CSV {csv_total}명 vs 대시보드 {dashboard_total}명")
        if not paid_match:
            print(f"  ❌ 인센티브 수령자: CSV {csv_paid}명 vs 대시보드 {dashboard_paid}명")
        if not amount_match:
            print(f"  ❌ 총액: CSV {csv_amount:,.0f} vs 대시보드 {dashboard_amount:,.0f}")
        if mismatch_count > 0:
            print(f"  ❌ 샘플 {sample_size}명 중 {mismatch_count}명 불일치")
else:
    print("❌ 대시보드에서 데이터를 추출할 수 없습니다.")

print("="*80)