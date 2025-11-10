#!/usr/bin/env python3
"""TYPE별 테이블 표시 문제 진단 스크립트"""

import pandas as pd
import json
import base64
import re

# CSV 파일 읽기
csv_file = "output_files/output_QIP_incentive_october_2025_Complete_V8.02_Complete.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

# TYPE별 집계
type_summary = df.groupby('ROLE TYPE STD').agg({
    'Employee No': 'count',
    'Final Incentive amount': ['sum', 'mean']
}).round(0)

print("CSV 파일의 TYPE별 집계:")
print(type_summary)
print()

# HTML 파일에서 JavaScript 확인
html_file = "output_files/Incentive_Dashboard_2025_10_Version_8.02.html"
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Base64 데이터 추출 및 디코딩
match = re.search(r'id="employeeDataBase64">\s*([A-Za-z0-9+/=]+)\s*</script>', html_content)
if match:
    base64_str = match.group(1).strip()
    decoded_bytes = base64.b64decode(base64_str)
    decoded_str = decoded_bytes.decode('utf-8')
    data = json.loads(decoded_str)

    # TYPE별 집계 (JavaScript 데이터)
    type_count = {}
    type_amount = {}

    for emp in data:
        emp_type = emp.get('type', emp.get('ROLE TYPE STD', 'UNKNOWN'))
        amount = int(emp.get('Final Incentive amount', 0))

        if emp_type not in type_count:
            type_count[emp_type] = 0
            type_amount[emp_type] = 0

        type_count[emp_type] += 1
        if amount > 0:
            type_amount[emp_type] += amount

    print("HTML Base64 데이터의 TYPE별 집계:")
    for t in sorted(type_count.keys()):
        print(f"{t}: {type_count[t]}명, 총 {type_amount[t]:,} VND")
    print()

# updateTypeSummaryTable 함수가 제대로 있는지 확인
if "function updateTypeSummaryTable()" in html_content:
    print("✅ updateTypeSummaryTable 함수 정의 있음")

    # 함수 호출 위치 확인
    call_count = html_content.count("updateTypeSummaryTable()")
    print(f"   함수 호출 횟수: {call_count}회")

    # window.onload에서 호출되는지 확인
    if "window.onload" in html_content and "updateTypeSummaryTable()" in html_content.split("window.onload")[1]:
        print("✅ window.onload에서 호출됨")
    else:
        print("❌ window.onload에서 호출 안됨")
else:
    print("❌ updateTypeSummaryTable 함수 정의 없음")

# typeSummaryBody 요소 확인
if 'id="typeSummaryBody"' in html_content:
    print("✅ typeSummaryBody 요소 있음")
else:
    print("❌ typeSummaryBody 요소 없음")