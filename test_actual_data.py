#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
actual_data 확인 테스트
"""

import pandas as pd
from pathlib import Path

# CSV 파일 읽기
csv_path = Path("output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv")
df = pd.read_csv(csv_path)

# TYPE-1 (V) SUPERVISOR 테스트
emp_no = '618040412'
emp_row = df[df['Employee No'] == 618040412]

print("=" * 80)
print("actual_data 확인")
print("=" * 80)

if not emp_row.empty:
    emp_row = emp_row.iloc[0]
    
    print(f"\n직원 {emp_no} 데이터:")
    print(f"  Employee No 타입: {type(emp_row['Employee No'])}")
    print(f"  Employee No 값: {emp_row['Employee No']}")
    
    # actual_data 생성 (step2_dashboard_version4.py 코드 복사)
    actual_data = {
        'attendance_rate': 100 - emp_row.get('Absence Rate (raw)', 0) if pd.notna(emp_row.get('Absence Rate (raw)')) else None,
        'unapproved_absences': emp_row.get('Unapproved Absence Days', 0) if pd.notna(emp_row.get('Unapproved Absence Days')) else 0,
        'actual_working_days': emp_row.get('Actual Working Days', 0) if pd.notna(emp_row.get('Actual Working Days')) else 0,
        'july_aql_failures': emp_row.get('July AQL Failures', 0) if pd.notna(emp_row.get('July AQL Failures')) else 0,
        'continuous_fail': emp_row.get('Continuous_FAIL', 'NO') if pd.notna(emp_row.get('Continuous_FAIL')) else 'NO',
        'total_validation_qty': emp_row.get('Total Valiation Qty', 0) if pd.notna(emp_row.get('Total Valiation Qty')) else 0,
        'pass_percent': emp_row.get('Pass %', 0) if pd.notna(emp_row.get('Pass %')) else 0,
        'building': emp_row.get('BUILDING', '') if pd.notna(emp_row.get('BUILDING')) else ''
    }
    
    print("\nactual_data 내용:")
    for key, value in actual_data.items():
        print(f"  {key}: {value} (타입: {type(value).__name__})")
    
    print("\n조건 체크:")
    print(f"  actual_working_days is not None: {actual_data.get('actual_working_days') is not None}")
    print(f"  actual_working_days 값: {actual_data.get('actual_working_days')}")
    
    if actual_data.get('actual_working_days') is not None:
        actual_days = int(actual_data['actual_working_days'])
        print(f"  int 변환 후: {actual_days}")
        print(f"  조건 통과 여부 (≥12): {actual_days >= 12}")
else:
    print(f"직원 {emp_no}를 찾을 수 없습니다.")

# analyze_conditions_with_actual_values 함수에서 emp_no 매칭 테스트
print("\n" + "=" * 80)
print("emp_no 매칭 테스트")
print("=" * 80)

# 문자열로 전달된 emp_no
emp_no_str = '618040412'
emp_row_str = df[df['Employee No'] == emp_no_str]
print(f"문자열 '{emp_no_str}'로 검색: {len(emp_row_str)}개 결과")

# 정수로 전달된 emp_no
emp_no_int = 618040412
emp_row_int = df[df['Employee No'] == emp_no_int]
print(f"정수 {emp_no_int}로 검색: {len(emp_row_int)}개 결과")

# 실제 Employee No 컬럼 값 확인
print(f"\nEmployee No 컬럼 샘플 (처음 5개):")
for idx, val in enumerate(df['Employee No'].head()):
    print(f"  {idx}: {val} (타입: {type(val).__name__})")