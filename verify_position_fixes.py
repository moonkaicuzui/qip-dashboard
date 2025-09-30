#!/usr/bin/env python3
"""
Position NAME-CODE 매핑 수정 후 검증
"""

import pandas as pd
import numpy as np

# CSV 파일 읽기
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv', encoding='utf-8-sig')

print("="*80)
print("🔍 Position NAME-CODE 매핑 수정 후 검증")
print("="*80)

# 1. MODEL MASTER 검증
print("\n[1] MODEL MASTER 검증")
print("-"*60)

# MODEL MASTER를 NAME 또는 CODE로 찾기
model_masters_by_name = df[df['QIP POSITION 1ST  NAME'].str.upper().str.contains('MODEL MASTER', na=False)]
model_masters_by_code = df[df['FINAL QIP POSITION NAME CODE'] == 'D']

# 합집합 (NAME 또는 CODE로 찾은 모든 MODEL MASTER)
model_masters = pd.concat([model_masters_by_name, model_masters_by_code]).drop_duplicates()

print(f"MODEL MASTER 총 인원: {len(model_masters)}명")
print(f"  - NAME으로 찾은 인원: {len(model_masters_by_name)}명")
print(f"  - CODE 'D'로 찾은 인원: {len(model_masters_by_code)}명")

for idx, emp in model_masters.iterrows():
    print(f"\n👤 {emp['Full Name']}")
    print(f"   - Position NAME: {emp['QIP POSITION 1ST  NAME']}")
    print(f"   - Position CODE: {emp['FINAL QIP POSITION NAME CODE']}")
    print(f"   - TYPE: {emp['ROLE TYPE STD']}")
    print(f"   - 조건 충족률: {emp.get('conditions_pass_rate', 0)}%")
    print(f"   - 9월 인센티브: {emp['September_Incentive']:,} VND")

    if emp['Full Name'] == 'TRẦN THỊ THÚY ANH':
        print(f"   ⭐ TRẦN THỊ THÚY ANH 확인!")
        if emp.get('conditions_pass_rate', 0) == 100 and emp['September_Incentive'] > 0:
            print(f"   ✅✅✅ 수정 성공! 100% 충족으로 인센티브 지급됨")
        elif emp.get('conditions_pass_rate', 0) == 100 and emp['September_Incentive'] == 0:
            print(f"   ❌❌❌ 여전히 버그! 100% 충족인데 0 VND")
        elif emp.get('conditions_pass_rate', 0) < 100 and emp['September_Incentive'] == 0:
            print(f"   ✅ 정상: 조건 미충족으로 0 VND")

# 2. ASSEMBLY INSPECTOR 검증
print("\n[2] ASSEMBLY INSPECTOR 검증")
print("-"*60)

# ASSEMBLY INSPECTOR를 NAME 또는 CODE로 찾기
assembly_by_name = df[
    (df['QIP POSITION 1ST  NAME'].str.upper().str.contains('ASSEMBLY', na=False)) &
    (df['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
]
assembly_by_code = df[df['FINAL QIP POSITION NAME CODE'].str.match(r'^A[1-5][AB]?$', na=False)]

# 합집합
assembly_inspectors = pd.concat([assembly_by_name, assembly_by_code]).drop_duplicates()

print(f"ASSEMBLY INSPECTOR 총 인원: {len(assembly_inspectors)}명")
print(f"  - NAME으로 찾은 인원: {len(assembly_by_name)}명")
print(f"  - CODE로 찾은 인원: {len(assembly_by_code)}명")

# 인센티브 받은 인원 확인
assembly_with_incentive = assembly_inspectors[assembly_inspectors['September_Incentive'] > 0]
print(f"  - 인센티브 받은 인원: {len(assembly_with_incentive)}명")

if len(assembly_with_incentive) > 0:
    print("\n  샘플 (인센티브 받은 직원 3명):")
    for idx, emp in assembly_with_incentive.head(3).iterrows():
        print(f"    - {emp['Full Name']} ({emp['FINAL QIP POSITION NAME CODE']}): {emp['September_Incentive']:,} VND")

# 3. 전체 통계
print("\n[3] 전체 통계")
print("-"*60)

type1_total = df[df['ROLE TYPE STD'] == 'TYPE-1']['September_Incentive'].sum()
type2_total = df[df['ROLE TYPE STD'] == 'TYPE-2']['September_Incentive'].sum()
type3_total = df[df['ROLE TYPE STD'] == 'TYPE-3']['September_Incentive'].sum()

print(f"TYPE-1 총 지급액: {type1_total:,} VND")
print(f"TYPE-2 총 지급액: {type2_total:,} VND")
print(f"TYPE-3 총 지급액: {type3_total:,} VND")
print(f"전체 총 지급액: {type1_total + type2_total + type3_total:,} VND")

# 4. 문제 직원 확인
print("\n[4] 100% 충족했는데 0 VND 받은 직원")
print("-"*60)

problem_employees = df[
    (df['conditions_pass_rate'] == 100) &
    (df['September_Incentive'] == 0) &
    (df['ROLE TYPE STD'] == 'TYPE-1')
]

if len(problem_employees) > 0:
    print(f"❌ 문제 직원 {len(problem_employees)}명 발견:")
    for idx, emp in problem_employees.head(10).iterrows():
        print(f"  - {emp['Full Name']} ({emp['FINAL QIP POSITION NAME CODE']}): 100% 충족 → 0 VND")
else:
    print("✅ 문제 없음! 모든 100% 충족 직원이 인센티브를 받음")

print("\n" + "="*80)
print("🎯 검증 완료")
print("="*80)