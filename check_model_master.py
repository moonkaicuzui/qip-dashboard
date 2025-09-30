#!/usr/bin/env python3
"""
Model Master 직원들의 인센티브 금액 검증
Excel, CSV, Dashboard 간 데이터 일관성 확인
"""

import pandas as pd
import json
import base64
from bs4 import BeautifulSoup

print("="*80)
print("🔍 MODEL MASTER 인센티브 금액 심층 분석")
print("="*80)

# 1. Excel 파일에서 Model Master 데이터 확인
print("\n[1] Excel 파일에서 Model Master 데이터 추출")
print("-"*60)

excel_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx'
excel_df = pd.read_excel(excel_file, sheet_name='Sheet1')

# Model Master 직원 필터링
model_master_excel = excel_df[excel_df['FINAL QIP POSITION NAME CODE'] == 'Model Master'].copy()
print(f"✅ Excel에서 Model Master 직원 수: {len(model_master_excel)}명")

# Excel에서 인센티브 금액 확인
if len(model_master_excel) > 0:
    print("\nExcel - Model Master 인센티브 상세:")
    for idx, row in model_master_excel.iterrows():
        emp_no = row['Employee No']
        name = row['Full Name']
        position = row['FINAL QIP POSITION NAME CODE']
        incentive = row.get('September_Incentive', 0)
        type_val = row.get('TYPE', 'N/A')

        print(f"  [{idx+1}] {emp_no} - {name}")
        print(f"      Position: {position}")
        print(f"      TYPE: {type_val}")
        print(f"      September Incentive: {incentive:,.0f} VND")

        # 조건 충족 상태 확인
        if 'Incentive Determination' in row:
            print(f"      Incentive Determination: {row['Incentive Determination']}")
        print()

    total_excel = model_master_excel['September_Incentive'].sum()
    print(f"📊 Excel 총 인센티브: {total_excel:,.0f} VND")

# 2. CSV 파일에서 Model Master 데이터 확인
print("\n[2] CSV 파일에서 Model Master 데이터 확인")
print("-"*60)

csv_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
csv_df = pd.read_csv(csv_file)

# CSV에서 Model Master 직원 확인
model_master_csv = csv_df[csv_df['FINAL QIP POSITION NAME CODE'] == 'Model Master'].copy()
print(f"✅ CSV에서 Model Master 직원 수: {len(model_master_csv)}명")

if len(model_master_csv) > 0:
    print("\nCSV - Model Master 인센티브 상세:")
    for idx, row in model_master_csv.iterrows():
        emp_no = row['Employee No']
        name = row['Full Name']
        incentive = row.get('september_incentive', 0)

        print(f"  [{idx+1}] {emp_no} - {name}")
        print(f"      september_incentive: {incentive:,.0f} VND")

    total_csv = model_master_csv['september_incentive'].sum()
    print(f"📊 CSV 총 인센티브: {total_csv:,.0f} VND")

# 3. 대시보드 HTML 파일에서 Model Master 데이터 확인
print("\n[3] Dashboard HTML에서 Model Master 데이터 확인")
print("-"*60)

dashboard_file = 'output_files/Incentive_Dashboard_2025_09_Version_6.html'
with open(dashboard_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# employeeDataBase64 추출
import re
match = re.search(r'<script type="application/json" id="employeeDataBase64">\s*(.*?)\s*</script>', html_content, re.DOTALL)

if match:
    base64_data = match.group(1).strip()

    # Base64 디코딩
    try:
        decoded_bytes = base64.b64decode(base64_data)
        decoded_str = decoded_bytes.decode('utf-8')
        employee_data = json.loads(decoded_str)

        # Model Master 직원 필터링
        model_master_dashboard = [emp for emp in employee_data if emp.get('position') == 'Model Master']
        print(f"✅ Dashboard에서 Model Master 직원 수: {len(model_master_dashboard)}명")

        if model_master_dashboard:
            print("\nDashboard - Model Master 인센티브 상세:")
            total_dashboard = 0
            for idx, emp in enumerate(model_master_dashboard):
                emp_no = emp.get('emp_no', emp.get('Employee No'))
                name = emp.get('name', emp.get('Full Name'))
                incentive = emp.get('september_incentive', 0)
                type_val = emp.get('type', 'N/A')

                print(f"  [{idx+1}] {emp_no} - {name}")
                print(f"      TYPE: {type_val}")
                print(f"      september_incentive: {incentive:,.0f} VND")
                total_dashboard += incentive

            print(f"📊 Dashboard 총 인센티브: {total_dashboard:,.0f} VND")
    except Exception as e:
        print(f"❌ Dashboard 데이터 파싱 오류: {e}")

# 4. 데이터 비교 분석
print("\n" + "="*80)
print("📊 데이터 일관성 분석 결과")
print("="*80)

# Excel vs CSV 비교
if len(model_master_excel) > 0 and len(model_master_csv) > 0:
    print("\n[Excel vs CSV 비교]")

    # 직원별 비교
    for idx, excel_row in model_master_excel.iterrows():
        emp_no = excel_row['Employee No']
        csv_row = model_master_csv[model_master_csv['Employee No'] == emp_no]

        if not csv_row.empty:
            excel_incentive = excel_row.get('September_Incentive', 0)
            csv_incentive = csv_row.iloc[0].get('september_incentive', 0)

            if excel_incentive != csv_incentive:
                print(f"⚠️ 불일치 발견: {emp_no}")
                print(f"   Excel: {excel_incentive:,.0f} VND")
                print(f"   CSV: {csv_incentive:,.0f} VND")
                print(f"   차이: {abs(excel_incentive - csv_incentive):,.0f} VND")
            else:
                print(f"✅ 일치: {emp_no} - {excel_incentive:,.0f} VND")

# 5. Model Master 특별 정책 확인
print("\n[5] Model Master 특별 정책 확인")
print("-"*60)

# position_condition_matrix.json 확인
try:
    with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
        position_matrix = json.load(f)

    # Model Master 조건 확인
    if 'Model Master' in position_matrix.get('positions', {}):
        mm_config = position_matrix['positions']['Model Master']
        print(f"✅ Model Master 설정:")
        print(f"   - TYPE: {mm_config.get('type', 'N/A')}")
        print(f"   - 조건: {mm_config.get('conditions', [])}")
        print(f"   - 인센티브 범위: {mm_config.get('incentive_amount', 'N/A')}")
    else:
        print("⚠️ position_condition_matrix.json에 Model Master 설정 없음")

except Exception as e:
    print(f"❌ position_condition_matrix.json 읽기 오류: {e}")

# 6. 최종 검증 결과
print("\n" + "="*80)
print("🎯 최종 검증 결과")
print("="*80)

if 'total_excel' in locals() and 'total_csv' in locals():
    if total_excel == total_csv:
        print("✅ Excel과 CSV 총액 일치")
    else:
        print(f"❌ Excel과 CSV 총액 불일치:")
        print(f"   Excel: {total_excel:,.0f} VND")
        print(f"   CSV: {total_csv:,.0f} VND")
        print(f"   차이: {abs(total_excel - total_csv):,.0f} VND")

if 'total_dashboard' in locals():
    if total_csv == total_dashboard:
        print("✅ CSV와 Dashboard 총액 일치")
    else:
        print(f"❌ CSV와 Dashboard 총액 불일치:")
        print(f"   CSV: {total_csv:,.0f} VND")
        print(f"   Dashboard: {total_dashboard:,.0f} VND")
        print(f"   차이: {abs(total_csv - total_dashboard):,.0f} VND")

print("\n" + "="*80)
print("분석 완료!")
print("="*80)