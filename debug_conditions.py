#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
특정 직원의 조건 디버깅
"""

import pandas as pd
from pathlib import Path
import sys
import json

# step2_dashboard_version4.py의 일부 함수를 가져옴
sys.path.append('src')

# CSV 파일 읽기
csv_path = Path("output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv")
df = pd.read_csv(csv_path)

# TYPE-1 (V) SUPERVISOR 중 하나 선택 (618040412 - CAO THỊ MIỀN)
emp_id = 618040412
emp_row = df[df['Employee No'] == emp_id]
if emp_row.empty:
    print(f"직원 {emp_id}를 찾을 수 없습니다.")
    sys.exit(1)
emp_row = emp_row.iloc[0]

print("=" * 80)
print(f"직원 {emp_id} - {emp_row['Full Name']} 조건 디버깅")
print("=" * 80)

print(f"\n기본 정보:")
print(f"  Type: {emp_row['ROLE TYPE STD']}")
print(f"  Position: {emp_row['QIP POSITION 1ST  NAME']}")
print(f"  Incentive: {emp_row['July_Incentive']:,} VND")

print(f"\n실제 데이터:")
print(f"  Actual Working Days: {emp_row['Actual Working Days']}")
print(f"  Absence Rate (raw): {emp_row.get('Absence Rate (raw)', 'N/A')}")
print(f"  Unapproved Absence Days: {emp_row.get('Unapproved Absence Days', 'N/A')}")

print(f"\nCSV 조건 컬럼 값 (역논리 주의):")
print(f"  attendancy condition 1 (0일 여부): {emp_row['attendancy condition 1 - acctual working days is zero']}")
print(f"  attendancy condition 2 (무단결근>2): {emp_row['attendancy condition 2 - unapproved Absence Day is more than 2 days']}")
print(f"  attendancy condition 3 (결근>12%): {emp_row['attendancy condition 3 - absent % is over 12%']}")
print(f"  attendancy condition 4 (최소<12일): {emp_row['attendancy condition 4 - minimum working days']}")

print(f"\nPython 코드에서 생성될 조건 값:")
actual_days = emp_row['Actual Working Days']
print(f"  minimum_working_days:")
print(f"    actual: {actual_days}일")
print(f"    passed: {actual_days >= 12}")
print(f"    value: {'정상' if actual_days >= 12 else '기준 미달'}")

# 모든 TYPE-1 (V) SUPERVISOR 확인
type1_v_sup = df[(df['ROLE TYPE STD'] == 'TYPE-1') & (df['QIP POSITION 1ST  NAME'] == '(V) SUPERVISOR')]
print(f"\n\nTYPE-1 (V) SUPERVISOR 전체 현황:")
print(f"총 {len(type1_v_sup)}명")

for idx, row in type1_v_sup.iterrows():
    emp_id = row['Employee No']
    name = row['Full Name']
    days = row['Actual Working Days']
    incentive = row['July_Incentive']
    cond4 = row['attendancy condition 4 - minimum working days']
    
    print(f"\n{emp_id} - {name}:")
    print(f"  실제 근무일: {days}일")
    print(f"  조건4 CSV값: {cond4} (no=통과, yes=실패)")
    print(f"  Python 평가: {'통과' if days >= 12 else '실패'}")
    print(f"  인센티브: {incentive:,} VND")
    
    # 조건 불일치 체크
    csv_says_pass = (cond4 == 'no')
    actual_pass = (days >= 12)
    if csv_says_pass != actual_pass:
        print(f"  ⚠️ 불일치! CSV={csv_says_pass}, 실제={actual_pass}")