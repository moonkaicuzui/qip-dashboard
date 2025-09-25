#!/usr/bin/env python3
"""
Final validation of AQL fix for September 2025 data
"""

import pandas as pd
import json
import os
from datetime import datetime

print("=" * 80)
print("최종 AQL 데이터 검증 보고서")
print("=" * 80)
print(f"\n검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 1. AQL 원본 데이터 검증
print("\n1️⃣ AQL 원본 데이터 검증")
print("-" * 40)
aql_file = "input_files/AQL history/1.HSRG AQL REPORT-SEPTEMBER.2025.csv"
if os.path.exists(aql_file):
    aql_df = pd.read_csv(aql_file, encoding='utf-8-sig')
    fail_df = aql_df[aql_df['RESULT'].str.contains('FAIL', na=False)]
    unique_emp = fail_df['EMPLOYEE NO'].nunique()
    print(f"✅ September AQL 파일 존재")
    print(f"   - 총 레코드: {len(aql_df)}건")
    print(f"   - FAIL 레코드: {len(fail_df)}건")
    print(f"   - FAIL 직원 수: {unique_emp}명")
else:
    print(f"❌ AQL 파일을 찾을 수 없습니다: {aql_file}")

# 2. 생성된 Excel 파일 검증
print("\n2️⃣ 생성된 Excel 파일 검증")
print("-" * 40)
excel_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
if os.path.exists(excel_file):
    excel_df = pd.read_csv(excel_file, encoding='utf-8-sig')
    print(f"✅ Excel 파일 존재")
    print(f"   - 총 직원 수: {len(excel_df)}명")

    if 'September AQL Failures' in excel_df.columns:
        fail_count = (excel_df['September AQL Failures'] > 0).sum()
        total_failures = excel_df['September AQL Failures'].sum()
        print(f"   - September AQL Failures 컬럼 존재 ✅")
        print(f"   - AQL 실패 직원: {fail_count}명")
        print(f"   - 총 실패 건수: {int(total_failures)}건")

        # 샘플 출력
        if fail_count > 0:
            print("\n   📋 AQL 실패 직원 샘플 (최대 5명):")
            fail_employees = excel_df[excel_df['September AQL Failures'] > 0].head(5)
            for _, row in fail_employees.iterrows():
                print(f"      • {row['Employee No']}: {row['Full Name'][:20]} - {int(row['September AQL Failures'])}건")
    else:
        print(f"   ❌ September AQL Failures 컬럼이 없습니다")
else:
    print(f"❌ Excel 파일을 찾을 수 없습니다: {excel_file}")

# 3. 대시보드 파일 검증
print("\n3️⃣ 대시보드 HTML 파일 검증")
print("-" * 40)
dashboard_file = "output_files/Incentive_Dashboard_2025_09_Version_5.html"
if os.path.exists(dashboard_file):
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"✅ 대시보드 파일 존재")
    print(f"   - 파일 크기: {len(content):,} bytes")

    # employeeData 존재 확인
    if 'window.employeeData' in content:
        print(f"   - window.employeeData 정의됨 ✅")
    else:
        print(f"   - ⚠️ window.employeeData가 정의되지 않음")

    # September AQL Failures 데이터 확인
    import re
    matches = re.findall(r'"September AQL Failures":\s*(\d+)', content)
    if matches:
        non_zero = [int(m) for m in matches if int(m) > 0]
        print(f"   - September AQL Failures 데이터 존재 ✅")
        print(f"   - 0이 아닌 값 개수: {len(non_zero)}개")
    else:
        print(f"   - ⚠️ September AQL Failures 데이터를 찾을 수 없음")
else:
    print(f"❌ 대시보드 파일을 찾을 수 없습니다: {dashboard_file}")

# 4. 메타데이터 파일 검증
print("\n4️⃣ 메타데이터 JSON 파일 검증")
print("-" * 40)
metadata_file = "output_files/output_QIP_incentive_september_2025_metadata.json"
if os.path.exists(metadata_file):
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    print(f"✅ 메타데이터 파일 존재")

    # AQL 관련 정보 확인
    employees_with_aql = 0
    for emp_id, emp_data in metadata.get('employees', {}).items():
        conditions = emp_data.get('condition_details', {}).get('conditions', {})
        aql_data = conditions.get('aql', {})
        if aql_data.get('monthly_failure', {}).get('value', 0) > 0:
            employees_with_aql += 1

    print(f"   - 메타데이터 내 AQL 실패 직원: {employees_with_aql}명")
else:
    print(f"❌ 메타데이터 파일을 찾을 수 없습니다: {metadata_file}")

# 5. 최종 검증 결과
print("\n" + "=" * 80)
print("📊 최종 검증 결과")
print("=" * 80)

success = True
messages = []

# AQL 데이터 일치성 확인
if 'unique_emp' in locals() and 'fail_count' in locals():
    if unique_emp == fail_count:
        messages.append(f"✅ AQL 원본({unique_emp}명)과 Excel({fail_count}명) 데이터가 일치합니다")
    else:
        messages.append(f"⚠️ AQL 원본({unique_emp}명)과 Excel({fail_count}명) 데이터가 불일치합니다")
        success = False

# 대시보드 데이터 확인
if 'non_zero' in locals() and 'fail_count' in locals():
    if len(non_zero) == fail_count:
        messages.append(f"✅ Excel({fail_count}명)과 대시보드({len(non_zero)}명) 데이터가 일치합니다")
    else:
        messages.append(f"⚠️ Excel({fail_count}명)과 대시보드({len(non_zero)}명) 데이터가 불일치합니다")

# 메타데이터 확인
if 'employees_with_aql' in locals() and 'fail_count' in locals():
    if employees_with_aql == fail_count:
        messages.append(f"✅ Excel({fail_count}명)과 메타데이터({employees_with_aql}명) 데이터가 일치합니다")
    else:
        messages.append(f"⚠️ Excel({fail_count}명)과 메타데이터({employees_with_aql}명) 데이터가 불일치합니다")

for msg in messages:
    print(msg)

if success and len(messages) > 0:
    print("\n🎉 모든 검증을 통과했습니다! AQL 데이터가 올바르게 처리되고 있습니다.")
else:
    print("\n⚠️ 일부 검증에서 문제가 발견되었습니다. 확인이 필요합니다.")

print("\n" + "=" * 80)