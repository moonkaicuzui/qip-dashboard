#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
조건 데이터 직렬화 테스트
"""

import pandas as pd
from pathlib import Path
import json
import sys

# step2_dashboard_version4.py의 함수 가져오기
sys.path.append('src')
from step2_dashboard_version4 import analyze_conditions_with_actual_values

# CSV 파일 읽기
csv_path = Path("output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv")
df = pd.read_csv(csv_path)

# TYPE-1 (V) SUPERVISOR 중 하나 테스트 (618040412)
emp_row = df[df['Employee No'] == 618040412].iloc[0]

# 조건 분석
conditions = analyze_conditions_with_actual_values(
    reason='', 
    emp_type='TYPE-1',
    position='(V) SUPERVISOR',
    emp_no='618040412',
    csv_data=df,
    aql_history=None
)

print("=" * 80)
print("조건 데이터 직렬화 테스트")
print("=" * 80)

print("\n1. Python Dictionary 구조:")
print(f"조건 개수: {len(conditions)}")
for key, value in conditions.items():
    if isinstance(value, dict):
        print(f"  {key}:")
        print(f"    passed: {value.get('passed')}")
        print(f"    actual: {value.get('actual')}")
        print(f"    applicable: {value.get('applicable')}")

print("\n2. JSON 직렬화 테스트:")
json_str = json.dumps(conditions, ensure_ascii=False, default=str)
print(f"JSON 길이: {len(json_str)} 문자")

# JSON 파싱 테스트
parsed = json.loads(json_str)
print(f"파싱 후 조건 개수: {len(parsed)}")

print("\n3. minimum_working_days 조건 확인:")
if 'minimum_working_days' in conditions:
    mwd = conditions['minimum_working_days']
    print(f"  name: {mwd.get('name')}")
    print(f"  passed: {mwd.get('passed')}")
    print(f"  actual: {mwd.get('actual')}")
    print(f"  value: {mwd.get('value')}")
    print(f"  applicable: {mwd.get('applicable')}")
else:
    print("  ⚠️ minimum_working_days 조건이 없습니다!")

print("\n4. 직원 객체 시뮬레이션:")
emp = {
    'emp_no': '618040412',
    'name': 'CAO THỊ MIỀN',
    'position': '(V) SUPERVISOR',
    'type': 'TYPE-1',
    'july_incentive': '80,390 VND',
    'conditions': conditions
}

# 전체 직원 데이터 JSON 직렬화
employees = [emp]
json_employees = json.dumps(employees, ensure_ascii=False, default=str)
print(f"직원 데이터 JSON 길이: {len(json_employees)} 문자")

# JavaScript 코드에서 사용될 형태
js_code = f"const employeeData = {json.dumps([dict((k, v) for k, v in emp.items() if k != 'stop_working_date') for emp in employees], ensure_ascii=False, default=str)};"
print(f"\n5. JavaScript 코드 생성:")
print(f"코드 길이: {len(js_code)} 문자")

# 샘플 출력
print("\n6. JavaScript 변수 샘플 (처음 500자):")
print(js_code[:500] + "...")