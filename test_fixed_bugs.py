#!/usr/bin/env python3
"""
버그 수정 후 재계산 테스트
"""

import pandas as pd
import numpy as np

# 수정된 Excel 파일 읽기
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv', encoding='utf-8-sig')

print("="*80)
print("🔍 버그 수정 후 재계산 결과 검증")
print("="*80)

# 1. TRẦN THỊ THÚY ANH (MODEL MASTER) 확인
tran = df[df['Full Name'].str.contains('TRẦN THỊ THÚY ANH', na=False)]
if not tran.empty:
    emp = tran.iloc[0]
    print("\n📌 TRẦN THỊ THÚY ANH (MODEL MASTER) 재계산 결과:")
    print(f"  - 이름: {emp['Full Name']}")
    print(f"  - 직급: {emp['FINAL QIP POSITION NAME CODE']}")
    print(f"  - TYPE: {emp['ROLE TYPE STD']}")
    print(f"  - 적용 조건: {emp.get('conditions_applicable', 'N/A')}개")
    print(f"  - 통과 조건: {emp.get('conditions_passed', 'N/A')}개")
    print(f"  - 통과율: {emp.get('conditions_pass_rate', 'N/A')}%")
    print(f"  - 9월 인센티브: {emp['September_Incentive']:,} VND")
    print(f"  - 최종 인센티브: {emp['Final Incentive amount']:,} VND")

    # 조건 8 (구역 Reject율) 확인
    if 'cond_8_area_reject' in emp.index:
        print(f"\n  📊 조건 8 (구역 Reject율) 상태:")
        print(f"    - 상태: {emp['cond_8_area_reject']}")
        print(f"    - 실제값: {emp.get('cond_8_value', 'N/A')}%")
        print(f"    - 기준: {emp.get('cond_8_threshold', 'N/A')}%")

    if 'Area_Reject_Rate' in emp.index:
        print(f"    - Area_Reject_Rate: {emp['Area_Reject_Rate']}%")

    # 100% 충족 검증
    if emp['conditions_pass_rate'] < 100:
        print(f"\n  ⚠️ 경고: 100% 미충족 ({emp['conditions_pass_rate']}%)")
        if emp['September_Incentive'] > 0:
            print(f"  ❌ 버그 여전히 존재: 100% 미충족인데 인센티브 지급됨!")
        else:
            print(f"  ✅ 수정 성공: 100% 미충족이므로 인센티브 0 VND")
    else:
        print(f"\n  ✅ 100% 충족 확인")
        if emp['September_Incentive'] > 0:
            print(f"  ✅ 정상: 100% 충족이므로 인센티브 지급")
        else:
            print(f"  ⚠️ 주의: 100% 충족했는데 인센티브 0 VND")

# 2. 다른 MODEL MASTER들 확인
print("\n📊 전체 MODEL MASTER 현황:")
model_masters = df[df['FINAL QIP POSITION NAME CODE'].str.contains('MODEL MASTER', na=False)]
print(f"  - MODEL MASTER 인원: {len(model_masters)}명")

for idx, emp in model_masters.iterrows():
    pass_rate = emp.get('conditions_pass_rate', 0)
    incentive = emp['September_Incentive']
    print(f"\n  👤 {emp['Full Name']}:")
    print(f"    - 조건 충족률: {pass_rate}%")
    print(f"    - 인센티브: {incentive:,} VND")

    if pass_rate < 100 and incentive > 0:
        print(f"    ❌ 버그: 100% 미충족인데 인센티브 지급")
    elif pass_rate == 100 and incentive == 0:
        print(f"    ⚠️ 주의: 100% 충족인데 인센티브 미지급")
    elif pass_rate == 100 and incentive > 0:
        print(f"    ✅ 정상")
    elif pass_rate < 100 and incentive == 0:
        print(f"    ✅ 정상")

# 3. TYPE-1 전체 100% 충족 검증
print("\n📊 TYPE-1 전체 100% 충족 검증:")
type1_df = df[df['ROLE TYPE STD'] == 'TYPE-1'].copy()
type1_df['pass_rate'] = pd.to_numeric(type1_df['conditions_pass_rate'], errors='coerce')

# 100% 미충족인데 인센티브 받은 직원
problematic = type1_df[(type1_df['pass_rate'] < 100) & (type1_df['September_Incentive'] > 0)]
print(f"  - TYPE-1 전체: {len(type1_df)}명")
print(f"  - 100% 미충족인데 인센티브 받은 직원: {len(problematic)}명")

if len(problematic) > 0:
    print("\n  ❌ 여전히 버그 있음! 100% 미충족 인센티브 수령자:")
    for idx, emp in problematic.head(10).iterrows():
        print(f"    - {emp['Full Name']} ({emp['FINAL QIP POSITION NAME CODE']}): {emp['pass_rate']}% → {emp['September_Incentive']:,} VND")
else:
    print("\n  ✅ 버그 수정 성공! 모든 TYPE-1이 100% 충족 시에만 인센티브 받음")

print("\n" + "="*80)
print("🎯 검증 완료")
print("="*80)