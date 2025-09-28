#!/usr/bin/env python3
"""TYPE-2 GROUP LEADER 계산 로직 점검"""

import pandas as pd

# 출력 파일 로드
output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
df = pd.read_csv(output_file, encoding='utf-8-sig')

print("=== TYPE-2 GROUP LEADER 계산 로직 점검 ===\n")

# 1. TYPE-1 GROUP LEADER 평균 확인
type1_group_leaders = df[
    (df['ROLE TYPE STD'] == 'TYPE-1') &
    (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
]
print(f"1. TYPE-1 GROUP LEADER: {len(type1_group_leaders)}명")
if len(type1_group_leaders) > 0 and 'September_Incentive' in df.columns:
    type1_avg = type1_group_leaders['September_Incentive'].mean()
    print(f"   평균 인센티브: {type1_avg:,.0f} VND")
else:
    type1_avg = 0
    print("   평균 인센티브: 0 VND (데이터 없음)")

print("\n2. TYPE-2 LINE LEADER 분석:")
# TYPE-2 LINE LEADER 찾기
type2_line_leaders = df[
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    (df['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
    (df['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
]

print(f"   TYPE-2 LINE LEADER: {len(type2_line_leaders)}명")
if len(type2_line_leaders) > 0 and 'September_Incentive' in df.columns:
    # 인센티브 분포
    incentive_dist = type2_line_leaders['September_Incentive'].value_counts()
    print("   인센티브 분포:")
    for amount, count in incentive_dist.items():
        print(f"     {amount:,.0f} VND: {count}명")

    # 인센티브를 받는 LINE LEADER들의 평균
    receiving_line_leaders = type2_line_leaders[type2_line_leaders['September_Incentive'] > 0]
    if len(receiving_line_leaders) > 0:
        line_avg = receiving_line_leaders['September_Incentive'].mean()
        print(f"   인센티브 수령자 평균: {line_avg:,.0f} VND")
        print(f"   → GROUP LEADER 계산값 (평균×2): {line_avg*2:,.0f} VND")
    else:
        print("   인센티브 수령자: 0명")
        print("   → GROUP LEADER 계산값: 0 VND")

print("\n3. TYPE-2 GROUP LEADER 실제 값:")
type2_group_leaders = df[
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
]

for idx, row in type2_group_leaders.iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']
    incentive = row.get('September_Incentive', 0)
    pass_rate = row.get('conditions_pass_rate', 0)
    print(f"   {emp_no} | {name[:20]:20} | 조건충족: {pass_rate:5.1f}% | 인센티브: {incentive:,.0f} VND")

print("\n4. 계산 로직 검증:")
print(f"   TYPE-1 GROUP LEADER 평균: {type1_avg:,.0f} VND")
if type1_avg == 0:
    print("   → TYPE-1 평균이 0이므로 독립 계산 사용")
    print("   → 독립 계산 = 전체 TYPE-2 LINE LEADER 평균 × 2")
else:
    print("   → TYPE-1 평균 사용")

# ĐINH KIM NGOAN 관련 LINE LEADER 확인
print("\n5. ĐINH KIM NGOAN 관련 분석:")
ngoan = df[df['Employee No'] == '617100049']
if not ngoan.empty:
    ngoan_row = ngoan.iloc[0]
    print(f"   Employee: {ngoan_row['Full Name']}")
    print(f"   Position: {ngoan_row.get('QIP POSITION 1ST  NAME', '')}")
    print(f"   조건 충족률: {ngoan_row.get('conditions_pass_rate', 0)}%")
    print(f"   September_Incentive: {ngoan_row.get('September_Incentive', 0):,.0f} VND")

    # 같은 부서의 LINE LEADER 확인 (만약 부서 정보가 있다면)
    if 'Department' in df.columns:
        dept = ngoan_row.get('Department', '')
        dept_line_leaders = df[
            (df['Department'] == dept) &
            (df['ROLE TYPE STD'] == 'TYPE-2') &
            (df['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
            (df['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
        ]
        print(f"   같은 부서 LINE LEADER: {len(dept_line_leaders)}명")

print("\n=== 분석 결과 ===")
print("TYPE-2 GROUP LEADER 계산 로직:")
print("1. TYPE-1 GROUP LEADER 평균이 있으면 → 그 값 사용")
print("2. TYPE-1 평균이 0이면 → TYPE-2 LINE LEADER 평균 × 2")
print("3. LINE LEADER도 모두 0이면 → GROUP LEADER도 0")
print("\n문제: 일부 LINE LEADER만 인센티브를 받는 경우,")
print("      해당 LINE LEADER와 관련없는 GROUP LEADER도 영향받음")