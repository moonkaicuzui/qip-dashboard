import pandas as pd
import json
import re

print("="*80)
print("인센티브 총 금액 일치성 검증 - 모든 데이터 소스")
print("="*80)
print()

# 1. CSV 파일에서 총 금액 계산
print("1️⃣ CSV 파일:")
print("-" * 50)
csv_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv'
df_csv = pd.read_csv(csv_file)
csv_total = df_csv['August_Incentive'].sum()
csv_count = (df_csv['August_Incentive'] > 0).sum()
print(f"   파일: {csv_file}")
print(f"   총 금액: {csv_total:,.0f} VND")
print(f"   수령자 수: {csv_count}명")
print()

# 2. Excel 파일에서 총 금액 계산
print("2️⃣ Excel 파일:")
print("-" * 50)
excel_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.xlsx'
df_excel = pd.read_excel(excel_file, sheet_name='Sheet1')
excel_total = df_excel['August_Incentive'].sum()
excel_count = (df_excel['August_Incentive'] > 0).sum()
print(f"   파일: {excel_file}")
print(f"   총 금액: {excel_total:,.0f} VND")
print(f"   수령자 수: {excel_count}명")
print()

# 3. HTML 대시보드에서 총 금액 계산
print("3️⃣ HTML 대시보드:")
print("-" * 50)
html_file = 'output_files/Incentive_Dashboard_2025_08_Version_5.html'
print(f"   파일: {html_file}")

# HTML 파일에서 employeeData 추출
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# JavaScript에서 employeeData 추출
match = re.search(r'const employeeData = (\[.*?\]);', html_content, re.DOTALL)
if match:
    employee_data_str = match.group(1)
    employee_data = json.loads(employee_data_str)

    # 대시보드 총 금액 계산
    dashboard_total = sum(int(e.get('august_incentive', 0)) for e in employee_data)
    dashboard_count = sum(1 for e in employee_data if int(e.get('august_incentive', 0)) > 0)

    print(f"   총 금액: {dashboard_total:,.0f} VND")
    print(f"   수령자 수: {dashboard_count}명")
else:
    print("   ❌ employeeData를 찾을 수 없습니다.")
    dashboard_total = 0
    dashboard_count = 0
print()

# 4. 비교 결과
print("="*80)
print("📊 비교 결과:")
print("="*80)
print()
print(f"데이터 소스        총 금액                   수령자 수")
print("-" * 60)
print(f"CSV 파일:          {csv_total:>20,.0f} VND    {csv_count:>4}명")
print(f"Excel 파일:        {excel_total:>20,.0f} VND    {excel_count:>4}명")
print(f"HTML 대시보드:     {dashboard_total:>20,.0f} VND    {dashboard_count:>4}명")
print()

# 일치 여부 확인
if csv_total == excel_total == dashboard_total:
    print("✅ ✅ ✅ 모든 파일의 인센티브 총 금액이 완벽히 일치합니다! ✅ ✅ ✅")
    print()
    print(f"   일치하는 총 금액: {csv_total:,.0f} VND")
    print(f"   일치하는 수령자 수: {csv_count}명")
else:
    print("❌ 총 금액 불일치 발견!")
    if csv_total != excel_total:
        print(f"   CSV와 Excel 차이: {abs(csv_total - excel_total):,.0f} VND")
    if csv_total != dashboard_total:
        print(f"   CSV와 대시보드 차이: {abs(csv_total - dashboard_total):,.0f} VND")

print()
print("="*80)

# 추가 검증: 차이가 있다면 원인 분석
if csv_total == excel_total == dashboard_total:
    print("💡 추가 정보:")
    print("-" * 50)
    print("• CSV와 Excel 파일은 동일한 데이터 (형식만 다름)")
    print("• 대시보드는 퇴사자를 제외하지만 인센티브 총액은 동일")
    print("• 퇴사자는 이미 인센티브가 0이므로 총액에 영향 없음")
    print()

    # 상위 5명 인센티브 수령자
    top5 = df_csv.nlargest(5, 'August_Incentive')[['Full Name', 'QIP POSITION 1ST  NAME', 'August_Incentive']]
    print("📈 상위 5명 인센티브 수령자:")
    print("-" * 50)
    for _, row in top5.iterrows():
        print(f"   {row['Full Name'][:25]:<25} ({row['QIP POSITION 1ST  NAME'][:20]:<20}): {row['August_Incentive']:>12,.0f} VND")

print("="*80)