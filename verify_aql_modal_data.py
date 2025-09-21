#!/usr/bin/env python3
"""
AQL 모달 데이터 검증 스크립트
- CSV에서 AQL 통계 데이터 확인
- 대시보드 HTML의 JavaScript 데이터 확인
"""

import pandas as pd
import json
import re
from pathlib import Path

# CSV 파일 읽기
csv_path = Path('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')
df = pd.read_csv(csv_path)

# AQL 실패자 필터링
aql_fail_df = df[df['September AQL Failures'] > 0].copy()

print("=" * 80)
print("📊 AQL FAIL 모달 데이터 검증")
print("=" * 80)

print(f"\n✅ AQL 실패 보유자: {len(aql_fail_df)}명\n")

# 샘플 직원 데이터 출력
print("📋 샘플 직원 데이터 (처음 5명):")
print("-" * 80)

for idx, row in aql_fail_df.head(5).iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']
    boss_name = row.get('boss_name', 'N/A')
    aql_failures = int(row['September AQL Failures'])
    total_tests = int(row.get('AQL_Total_Tests', 0))
    pass_count = int(row.get('AQL_Pass_Count', 0))
    fail_percent = float(row.get('AQL_Fail_Percent', 0))

    print(f"직원번호: {emp_no}")
    print(f"  이름: {name}")
    print(f"  직속상사: {boss_name}")
    print(f"  AQL 실패 횟수: {aql_failures}회")
    print(f"  총 검사 횟수: {total_tests}회")
    print(f"  PASS 횟수: {pass_count}회")
    print(f"  FAIL 비율: {fail_percent:.1f}%")
    print()

# HTML 파일에서 JavaScript 데이터 확인
html_path = Path('output_files/Incentive_Dashboard_2025_09_Version_5.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# employeeData 추출
match = re.search(r'const employeeData = (\[.*?\]);', html_content, re.DOTALL)
if match:
    try:
        # JavaScript 배열을 Python 리스트로 파싱
        employees_js = match.group(1)
        # NaN을 null로 변환
        employees_js = employees_js.replace('NaN', 'null')
        employees = json.loads(employees_js)

        # AQL 실패자 필터링
        aql_fail_employees = [emp for emp in employees if emp.get('September AQL Failures', 0) > 0]

        print("=" * 80)
        print("🌐 HTML/JavaScript 데이터 검증")
        print("=" * 80)
        print(f"\n✅ JavaScript에서 AQL 실패자: {len(aql_fail_employees)}명")

        # 첫 번째 실패자의 AQL 통계 확인
        if aql_fail_employees:
            emp = aql_fail_employees[0]
            print(f"\n📋 JavaScript 데이터 샘플 (직원번호: {emp.get('emp_no')}):")
            print(f"  이름: {emp.get('name')}")
            print(f"  직속상사: {emp.get('boss_name', 'N/A')}")
            print(f"  AQL_Total_Tests: {emp.get('AQL_Total_Tests', 'NOT FOUND')}")
            print(f"  AQL_Pass_Count: {emp.get('AQL_Pass_Count', 'NOT FOUND')}")
            print(f"  AQL_Fail_Percent: {emp.get('AQL_Fail_Percent', 'NOT FOUND')}")

            if emp.get('AQL_Total_Tests') is not None:
                print("\n✅ AQL 통계 필드가 JavaScript 데이터에 포함되어 있습니다!")
            else:
                print("\n❌ 경고: AQL 통계 필드가 JavaScript 데이터에 없습니다!")

    except json.JSONDecodeError as e:
        print(f"❌ JavaScript 데이터 파싱 오류: {e}")
else:
    print("❌ employeeData를 HTML에서 찾을 수 없습니다.")

print("\n" + "=" * 80)
print("💡 검증 완료")
print("=" * 80)
print("\n대시보드를 브라우저에서 열고 AQL FAIL KPI (20명)를 클릭하여")
print("모달창에서 실제 데이터가 표시되는지 확인하세요:")
print("  - DƯƠNG THỊ HẬU: 15회 검사, 13회 PASS, 13.3% FAIL")
print("  - NGUYỄN THỊ BÍCH NGỌC: 14회 검사, 13회 PASS, 7.1% FAIL")