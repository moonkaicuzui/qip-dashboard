#!/usr/bin/env python3
"""ĐINH KIM NGOAN 조건 상세 확인"""

import pandas as pd

# 출력 파일 확인
output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
df = pd.read_csv(output_file, encoding='utf-8-sig')

# ĐINH KIM NGOAN 찾기
ngoan = df[df['Employee No'] == '617100049']

if not ngoan.empty:
    row = ngoan.iloc[0]
    print("=== ĐINH KIM NGOAN (617100049) 상세 분석 ===")
    print(f"이름: {row['Full Name']}")
    print(f"포지션: {row['QIP POSITION 1ST  NAME']}")
    print(f"TYPE: {row['ROLE TYPE STD']}")

    print("\n출근 조건:")
    cond1 = row.get('attendancy condition 1 - acctual working days is zero', 'N/A')
    cond2 = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'N/A')
    cond3 = row.get('attendancy condition 3 - absent % is over 12%', 'N/A')
    cond4 = row.get('attendancy condition 4 - minimum working days', 'N/A')

    print(f"  조건 1 (근무일 0): {cond1}")
    print(f"  조건 2 (무단결근 >2): {cond2}")
    print(f"  조건 3 (결근율 >12%): {cond3}")
    print(f"  조건 4 (최소 근무일): {cond4}")

    # 실패 여부 판단
    attendance_fail = (
        cond1 == 'yes' or
        cond2 == 'yes' or
        cond3 == 'yes' or
        cond4 == 'yes'
    )

    print(f"\n출근 조건 실패: {attendance_fail}")

    print(f"\n근무 정보:")
    print(f"  Actual working days: {row.get('Actual working days', 'N/A')}")
    print(f"  Total working days: {row.get('Total working days', 'N/A')}")
    print(f"  Attendance Rate: {row.get('Attendance Rate', 'N/A')}%")
    print(f"  Unapproved Absences: {row.get('Unapproved Absences', 'N/A')}")

    print(f"\n계산 결과:")
    print(f"  조건 충족률: {row.get('conditions_pass_rate', 0)}%")
    print(f"  September_Incentive: {row.get('September_Incentive', 0):,.0f} VND")
    print(f"  Final Incentive amount: {row.get('Final Incentive amount', 0):,.0f} VND")

    print(f"\n기타:")
    print(f"  RE MARK: {row.get('RE MARK', '')}")
    print(f"  Stop working Date: {row.get('Stop working Date', '')}")

# 다른 TYPE-2 GROUP LEADER와 비교
print("\n=== 다른 TYPE-2 GROUP LEADER와 비교 ===")
type2_group = df[
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') &
    (df['conditions_pass_rate'] == 100)
]

for idx, row in type2_group.iterrows():
    print(f"{row['Employee No']} | {row['Full Name'][:20]:20} | {row.get('September_Incentive', 0):,.0f} VND")