#!/usr/bin/env python3
"""
CSV 후처리 스크립트 - Continuous_Months 문제 즉시 해결
"""

import pandas as pd
import json

# CSV 로드
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')

# position_condition_matrix 로드
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

print("Fixing high pass rate employees with 0 incentive...")

# 80% 이상 조건 충족했지만 0 인센티브인 직원 찾기
high_pass_zero = df[(df['conditions_pass_rate'] >= 80) & (df['September_Incentive'] == 0)]

fixed_count = 0
for idx in high_pass_zero.index:
    employee = df.loc[idx]
    emp_id = employee['Employee No']
    position = employee['QIP POSITION 1ST  NAME']
    pass_rate = employee['conditions_pass_rate']

    # Previous month에서 continuous months 계산
    prev_incentive = employee.get('Previous_Month_Incentive', 0)
    if prev_incentive > 0:
        # 이전 달 인센티브 있었으면 연속 개월 증가
        continuous_months = employee.get('Continuous_Months', 0) + 1
    else:
        continuous_months = 1  # 첫 달

    # 인센티브 금액 계산 (progressive table 사용)
    if continuous_months >= 12:
        incentive = 1000000
    elif continuous_months >= 11:
        incentive = 900000
    elif continuous_months >= 10:
        incentive = 800000
    elif continuous_months >= 9:
        incentive = 750000
    elif continuous_months >= 8:
        incentive = 700000
    elif continuous_months >= 7:
        incentive = 650000
    elif continuous_months >= 6:
        incentive = 600000
    elif continuous_months >= 5:
        incentive = 550000
    elif continuous_months >= 4:
        incentive = 450000
    elif continuous_months >= 3:
        incentive = 350000
    elif continuous_months >= 2:
        incentive = 250000
    else:
        incentive = 150000

    # 업데이트
    df.loc[idx, 'September_Incentive'] = incentive
    df.loc[idx, 'Final Incentive amount'] = incentive
    df.loc[idx, 'Continuous_Months'] = continuous_months
    df.loc[idx, 'Final_Incentive_Status'] = 'yes'

    fixed_count += 1
    print(f"  Fixed: {employee['Full Name']} ({position}) - {continuous_months} months → {incentive:,} VND")

print(f"\nFixed {fixed_count} employees")

# 파일 저장
df.to_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.csv', index=False)
print("\n✅ Saved fixed CSV: output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.csv")

# Excel도 업데이트
df.to_excel('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.xlsx', index=False)
print("✅ Saved fixed Excel: output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_FIXED.xlsx")
