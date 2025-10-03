#!/usr/bin/env python3
"""
TYPE-1 직원 랜덤 샘플링 검증
조건 충족률과 인센티브 지급 관계 분석
"""

import pandas as pd
import json
import random

# Excel 파일 읽기
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv', encoding='utf-8-sig')

# TYPE-1 직원만 필터링
type1_df = df[df['ROLE TYPE STD'] == 'TYPE-1'].copy()

print("="*80)
print("🔍 TYPE-1 직원 랜덤 샘플링 검증")
print("="*80)
print(f"\n전체 TYPE-1 직원 수: {len(type1_df)}명")

# position_condition_matrix.json 로드
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

# 충족률별 그룹 분석
print("\n📊 조건 충족률별 분포:")
print("-" * 50)

# 충족률 계산
type1_df['pass_rate'] = pd.to_numeric(type1_df['conditions_pass_rate'], errors='coerce')

# 충족률 구간별 분석
bins = [0, 50, 80, 90, 99.99, 100]
labels = ['0-50%', '51-80%', '81-90%', '91-99%', '100%']
type1_df['pass_rate_group'] = pd.cut(type1_df['pass_rate'], bins=bins, labels=labels)

# 각 구간별 인센티브 지급 현황
for group in labels:
    group_df = type1_df[type1_df['pass_rate_group'] == group]
    if len(group_df) > 0:
        paid = group_df[group_df['September_Incentive'] > 0]
        print(f"\n충족률 {group}:")
        print(f"  - 직원 수: {len(group_df)}명")
        print(f"  - 인센티브 지급: {len(paid)}명")
        print(f"  - 지급률: {len(paid)/len(group_df)*100:.1f}%")

# 100% 미만 충족인데 인센티브 받은 직원들
problematic = type1_df[(type1_df['pass_rate'] < 100) & (type1_df['September_Incentive'] > 0)]
print(f"\n⚠️ 100% 미충족인데 인센티브 받은 직원: {len(problematic)}명")

# 샘플 직원 상세 분석
if len(problematic) > 0:
    print("\n📋 문제 사례 랜덤 샘플 (최대 5명):")
    print("-" * 50)

    samples = problematic.sample(min(5, len(problematic)))

    for idx, emp in samples.iterrows():
        print(f"\n👤 {emp['Full Name']}")
        print(f"  직급: {emp['FINAL QIP POSITION NAME CODE']}")
        print(f"  TYPE: {emp['ROLE TYPE STD']}")
        print(f"  적용 조건: {emp['conditions_applicable']}개")
        print(f"  통과 조건: {emp['conditions_passed']}개")
        print(f"  통과율: {emp['conditions_pass_rate']}%")
        print(f"  인센티브: {emp['September_Incentive']:,} VND")

        # 어떤 조건을 통과/실패했는지
        passed_conditions = []
        failed_conditions = []
        na_conditions = []

        for i in range(1, 11):
            cond_col = f'cond_{i}_'
            for col in emp.index:
                if col.startswith(cond_col) and not col.endswith('_value') and not col.endswith('_threshold'):
                    if emp[col] == 'PASS' or emp[col] == True or emp[col] == 1:
                        passed_conditions.append(i)
                    elif emp[col] == 'N/A' or pd.isna(emp[col]):
                        na_conditions.append(i)
                    else:
                        failed_conditions.append(i)
                    break

        print(f"  ✅ 통과: {passed_conditions}")
        print(f"  ❌ 실패: {failed_conditions}")
        print(f"  ⚫ N/A: {na_conditions}")

# JSON 설정과 비교
print("\n🔧 JSON 설정 vs Excel 실제 적용 비교:")
print("-" * 50)

# TYPE-1 특수 직급별 분석
special_positions = {
    'ASSEMBLY INSPECTOR': [1,2,3,4,5,6,9,10],
    'MODEL MASTER': [1,2,3,4,8],
    'LINE LEADER': [1,2,3,4,7],
    'AUDITOR': [1,2,3,4,7,8],
    'TRAINER': [1,2,3,4,7,8],
    'AQL INSPECTOR': [1,2,3,4,5]
}

for position, expected_conditions in special_positions.items():
    position_df = type1_df[type1_df['FINAL QIP POSITION NAME CODE'].str.contains(position, na=False)]
    if len(position_df) > 0:
        print(f"\n{position} ({len(position_df)}명):")
        print(f"  JSON 설정 조건: {expected_conditions} ({len(expected_conditions)}개)")

        # 실제 적용된 조건 수 평균
        avg_applicable = position_df['conditions_applicable'].mean()
        print(f"  Excel 평균 적용 조건: {avg_applicable:.1f}개")

        # 100% 미만 충족률
        under_100 = position_df[position_df['pass_rate'] < 100]
        if len(under_100) > 0:
            print(f"  ⚠️ 100% 미충족: {len(under_100)}명")

print("\n" + "="*80)
print("🎯 분석 완료")
print("="*80)