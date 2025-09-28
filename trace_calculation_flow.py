#!/usr/bin/env python3
"""계산 흐름 추적 및 문제 진단"""

import pandas as pd
import sys
import os

# 데이터 로드
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
df = pd.read_csv(source_file, encoding='utf-8-sig')

print("=== 소스 데이터 분석 ===")
print(f"총 직원 수: {len(df)}")

# September_Incentive 칼럼 확인
if 'September_Incentive' in df.columns:
    non_zero = df[df['September_Incentive'] != 0]
    print(f"September_Incentive 칼럼 있음: {len(non_zero)}명이 0이 아닌 값")
else:
    print("September_Incentive 칼럼 없음")

# Final Incentive amount 칼럼 확인
if 'Final Incentive amount' in df.columns:
    non_zero = df[df['Final Incentive amount'] != 0]
    print(f"Final Incentive amount 칼럼 있음: {len(non_zero)}명이 0이 아닌 값")
else:
    print("Final Incentive amount 칼럼 없음")

print("\n=== TYPE-2 GROUP LEADER 분석 ===")
type2_gl = df[(df['ROLE TYPE STD'] == 'TYPE-2') & (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')]
print(f"TYPE-2 GROUP LEADER: {len(type2_gl)}명")

for idx, row in type2_gl.iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']

    # 출근 조건 체크
    cond1 = row.get('attendancy condition 1 - acctual working days is zero', 'no')
    cond2 = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'no')
    cond3 = row.get('attendancy condition 3 - absent % is over 12%', 'no')
    cond4 = row.get('attendancy condition 4 - minimum working days', 'no')

    conditions_met = (cond1 != 'yes' and cond2 != 'yes' and cond3 != 'yes' and cond4 != 'yes')

    sept_incentive = row.get('September_Incentive', 0)
    final_incentive = row.get('Final Incentive amount', 0)

    print(f"\n{emp_no} | {name[:20]:20}")
    print(f"  조건1: {cond1}, 조건2: {cond2}, 조건3: {cond3}, 조건4: {cond4}")
    print(f"  조건 충족: {'YES' if conditions_met else 'NO'}")
    print(f"  September_Incentive: {sept_incentive:,.0f} VND")
    print(f"  Final Incentive: {final_incentive:,.0f} VND")

    if emp_no == '617100049':
        print(f"  ⚠️ ĐINH KIM NGOAN - 조건 충족했지만 0원!")

print("\n=== TYPE-2 LINE LEADER 분석 ===")
type2_line = df[
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    (df['QIP POSITION 1ST  NAME'].str.contains('LINE', na=False)) &
    (df['QIP POSITION 1ST  NAME'].str.contains('LEADER', na=False))
]

print(f"TYPE-2 LINE LEADER: {len(type2_line)}명")

if 'September_Incentive' in type2_line.columns:
    receiving = type2_line[type2_line['September_Incentive'] > 0]
    print(f"  인센티브 수령자: {len(receiving)}명")
    if len(receiving) > 0:
        avg = receiving['September_Incentive'].mean()
        print(f"  평균 인센티브: {avg:,.0f} VND")
        print(f"  GROUP LEADER 예상값 (평균×2): {avg*2:,.0f} VND")

print("\n=== 모델 마스터 분석 ===")
model_master = df[df['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False, case=False)]
print(f"모델 마스터: {len(model_master)}명")

for idx, row in model_master.iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']
    role_type = row['ROLE TYPE STD']
    sept_incentive = row.get('September_Incentive', 0)

    print(f"  {emp_no} | {name[:20]:20} | {role_type} | {sept_incentive:,.0f} VND")

print("\n=== 문제 진단 ===")
print("1. 소스 CSV에 이미 계산된 값이 있는가?")
print(f"   → {'YES' if 'September_Incentive' in df.columns else 'NO'}")

print("\n2. TYPE-2 GROUP LEADER가 정당한 금액을 받는가?")
if len(type2_gl) > 0:
    receiving_gl = type2_gl[type2_gl.get('September_Incentive', 0) > 0] if 'September_Incentive' in type2_gl.columns else []
    print(f"   → {len(receiving_gl)}/{len(type2_gl)}명이 인센티브 받음")

print("\n3. 모델 마스터가 정당한 금액을 받는가?")
if len(model_master) > 0 and 'September_Incentive' in model_master.columns:
    avg_mm = model_master['September_Incentive'].mean()
    print(f"   → 평균 {avg_mm:,.0f} VND")
else:
    print("   → 데이터 없음")