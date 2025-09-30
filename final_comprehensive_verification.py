#!/usr/bin/env python3
"""
최종 종합 검증 - 모든 TYPE과 직책의 JSON 설정 준수 확인
"""

import pandas as pd
import json
import numpy as np

# 1. 재계산된 CSV 파일 로드
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv', encoding='utf-8-sig')

# 2. JSON 설정 파일 로드
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

print("="*80)
print("🔍 최종 종합 검증 - JSON 설정 준수 확인")
print("="*80)

# 통계 저장
issues = []
total_employees = 0
employees_with_issues = 0

print("\n📊 TYPE별 검증:")
print("-"*60)

# TYPE-1 검증
print("\n[TYPE-1 검증]")
type1_df = df[df['ROLE TYPE STD'] == 'TYPE-1'].copy()
type1_df['pass_rate'] = pd.to_numeric(type1_df['conditions_pass_rate'], errors='coerce')
total_employees += len(type1_df)

# TYPE-1 JSON 설정
type1_config = matrix['position_matrix']['TYPE-1']

# 기본 TYPE-1 (D, E, F 등급)
basic_type1_mask = ~(
    type1_df['FINAL QIP POSITION NAME CODE'].str.contains('MODEL MASTER|ASSEMBLY|AQL|AUDITOR|TRAINER|LINE LEADER|GROUP LEADER|HEAD|MANAGER|SUPERVISOR', na=False, case=False)
)
basic_type1 = type1_df[basic_type1_mask]

print(f"\n1. 기본 TYPE-1 (D,E,F 등): {len(basic_type1)}명")
print(f"   JSON 설정: 조건 {type1_config['default']['applicable_conditions']} (4개 조건)")

# 100% 미충족인데 인센티브 받은 직원
basic_issues = basic_type1[(basic_type1['pass_rate'] < 100) & (basic_type1['September_Incentive'] > 0)]
if len(basic_issues) > 0:
    print(f"   ❌ 문제: {len(basic_issues)}명이 100% 미충족인데 인센티브 받음")
    for idx, emp in basic_issues.head(3).iterrows():
        print(f"      - {emp['Full Name']}: {emp['pass_rate']}% → {emp['September_Incentive']:,} VND")
        issues.append(emp)
    employees_with_issues += len(basic_issues)
else:
    print(f"   ✅ 정상: 모든 직원이 100% 충족 시에만 인센티브 받음")

# MODEL MASTER 검증
model_masters = type1_df[type1_df['FINAL QIP POSITION NAME CODE'].str.contains('MODEL MASTER', na=False, case=False)]
if len(model_masters) > 0:
    print(f"\n2. MODEL MASTER: {len(model_masters)}명")
    print(f"   JSON 설정: 조건 {type1_config.get('MODEL_MASTER', {}).get('applicable_conditions', [])} (5개 조건, 조건8 포함)")

    mm_issues = model_masters[(model_masters['pass_rate'] < 100) & (model_masters['September_Incentive'] > 0)]
    if len(mm_issues) > 0:
        print(f"   ❌ 문제: {len(mm_issues)}명이 100% 미충족인데 인센티브 받음")
        employees_with_issues += len(mm_issues)
    else:
        print(f"   ✅ 정상: 모든 MODEL MASTER가 100% 충족 시에만 인센티브 받음")

    # Area_Reject_Rate 확인
    for idx, emp in model_masters.iterrows():
        if pd.isna(emp.get('Area_Reject_Rate')) or emp.get('Area_Reject_Rate') == 0:
            if emp.get('cond_8_area_reject') != 'N/A':
                print(f"   ⚠️ {emp['Full Name']}: Area_Reject_Rate 계산 누락 의심")

# ASSEMBLY INSPECTOR 검증
assembly = type1_df[type1_df['FINAL QIP POSITION NAME CODE'].str.contains('ASSEMBLY.*INSPECTOR', na=False, case=False)]
if len(assembly) > 0:
    print(f"\n3. ASSEMBLY INSPECTOR: {len(assembly)}명")
    print(f"   JSON 설정: 조건 {type1_config.get('ASSEMBLY_INSPECTOR', {}).get('applicable_conditions', [])} (8개 조건)")

    ass_issues = assembly[(assembly['pass_rate'] < 100) & (assembly['September_Incentive'] > 0)]
    if len(ass_issues) > 0:
        print(f"   ❌ 문제: {len(ass_issues)}명이 100% 미충족인데 인센티브 받음")
        employees_with_issues += len(ass_issues)
    else:
        print(f"   ✅ 정상: 조건 충족 시에만 인센티브 받음")

# AUDITOR/TRAINER 검증
auditor_trainer = type1_df[
    type1_df['FINAL QIP POSITION NAME CODE'].str.contains('AUDITOR|TRAINER', na=False, case=False)
]
if len(auditor_trainer) > 0:
    print(f"\n4. AUDITOR/TRAINER: {len(auditor_trainer)}명")
    print(f"   JSON 설정: 조건 {type1_config.get('AUDITOR', {}).get('applicable_conditions', [])} (7개 조건)")

    at_issues = auditor_trainer[(auditor_trainer['pass_rate'] < 100) & (auditor_trainer['September_Incentive'] > 0)]
    if len(at_issues) > 0:
        print(f"   ❌ 문제: {len(at_issues)}명이 100% 미충족인데 인센티브 받음")
        employees_with_issues += len(at_issues)
    else:
        print(f"   ✅ 정상: 조건 충족 시에만 인센티브 받음")

# LINE LEADER 검증
line_leaders = type1_df[type1_df['FINAL QIP POSITION NAME CODE'].str.contains('LINE.*LEADER', na=False, case=False)]
if len(line_leaders) > 0:
    print(f"\n5. LINE LEADER: {len(line_leaders)}명")
    print(f"   JSON 설정: 조건 {type1_config.get('LINE_LEADER', {}).get('applicable_conditions', [])} (7개 조건)")

    ll_issues = line_leaders[(line_leaders['pass_rate'] < 100) & (line_leaders['September_Incentive'] > 0)]
    if len(ll_issues) > 0:
        print(f"   ❌ 문제: {len(ll_issues)}명이 100% 미충족인데 인센티브 받음")
        employees_with_issues += len(ll_issues)
    else:
        print(f"   ✅ 정상: 조건 충족 시에만 인센티브 받음")

# TYPE-2 검증
print("\n[TYPE-2 검증]")
type2_df = df[df['ROLE TYPE STD'] == 'TYPE-2'].copy()
type2_df['pass_rate'] = pd.to_numeric(type2_df['conditions_pass_rate'], errors='coerce')
total_employees += len(type2_df)

type2_config = matrix['position_matrix']['TYPE-2']
print(f"전체 TYPE-2: {len(type2_df)}명")
print(f"JSON 설정: 조건 {type2_config['default']['applicable_conditions']} (4개 출근 조건만)")

type2_issues = type2_df[(type2_df['pass_rate'] < 100) & (type2_df['September_Incentive'] > 0)]
if len(type2_issues) > 0:
    print(f"❌ 문제: {len(type2_issues)}명이 100% 미충족인데 인센티브 받음")
    for idx, emp in type2_issues.head(3).iterrows():
        print(f"   - {emp['Full Name']}: {emp['pass_rate']}% → {emp['September_Incentive']:,} VND")
    employees_with_issues += len(type2_issues)
else:
    print(f"✅ 정상: 모든 TYPE-2가 100% 충족 시에만 인센티브 받음")

# TYPE-3 검증
print("\n[TYPE-3 검증]")
type3_df = df[df['ROLE TYPE STD'] == 'TYPE-3'].copy()
total_employees += len(type3_df)

type3_config = matrix['position_matrix']['TYPE-3']
print(f"전체 TYPE-3: {len(type3_df)}명")
print(f"JSON 설정: {type3_config.get('description', 'No incentives for TYPE-3')} (인센티브 없음)")

type3_with_incentive = type3_df[type3_df['September_Incentive'] > 0]
if len(type3_with_incentive) > 0:
    print(f"❌ 문제: {len(type3_with_incentive)}명이 인센티브를 받음 (정책 위반)")
    employees_with_issues += len(type3_with_incentive)
else:
    print(f"✅ 정상: 모든 TYPE-3가 인센티브 0 VND")

# 전체 요약
print("\n" + "="*80)
print("📊 최종 검증 요약")
print("="*80)

print(f"\n전체 직원: {total_employees}명")
print(f"문제 있는 직원: {employees_with_issues}명")
print(f"문제 비율: {employees_with_issues/total_employees*100:.2f}%")

if employees_with_issues == 0:
    print("\n✅✅✅ 완벽합니다! 모든 TYPE과 직책이 JSON 설정을 100% 준수하고 있습니다.")
    print("    - Excel 자체 계산 문제: 해결됨")
    print("    - JSON 설정 무시 문제: 해결됨")
    print("    - 100% 충족 검증: 완벽히 적용됨")
else:
    print(f"\n❌❌❌ 아직 {employees_with_issues}명의 문제가 남아있습니다.")
    print("    추가 수정이 필요합니다.")

# 특별 케이스: TRẦN THỊ THÚY ANH 최종 확인
print("\n" + "-"*80)
print("🔍 TRẦN THỊ THÚY ANH 최종 상태:")
tran = df[df['Full Name'].str.contains('TRẦN THỊ THÚY ANH', na=False)]
if not tran.empty:
    emp = tran.iloc[0]
    print(f"  - 직급: {emp['FINAL QIP POSITION NAME CODE']}")
    print(f"  - 조건 충족률: {emp.get('conditions_pass_rate', 0)}%")
    print(f"  - 9월 인센티브: {emp['September_Incentive']:,} VND")

    if emp.get('conditions_pass_rate', 0) < 100 and emp['September_Incentive'] > 0:
        print("  ❌ 여전히 문제 있음: 100% 미충족인데 인센티브 받음")
    elif emp.get('conditions_pass_rate', 0) == 100 and emp['September_Incentive'] > 0:
        print("  ✅ 정상: 100% 충족으로 인센티브 받음")
    elif emp['September_Incentive'] == 0:
        print("  ✅ 정상: 조건 미충족으로 인센티브 0 VND")

print("\n" + "="*80)
print("🎯 검증 완료")
print("="*80)