#!/usr/bin/env python3
"""
Position NAME과 CODE 매핑 관계 전체 분석
모든 TYPE과 직급에 대한 불일치 확인
"""

import pandas as pd
import json
from collections import defaultdict

print("="*80)
print("🔍 Position NAME-CODE 매핑 전체 분석")
print("="*80)

# CSV 파일 로드
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv', encoding='utf-8-sig')

# 1. 전체 Position NAME과 CODE 매핑 분석
print("\n[1] 전체 Position NAME-CODE 매핑 분석")
print("-"*60)

position_mapping = defaultdict(set)
code_to_names = defaultdict(set)
type_position_analysis = defaultdict(lambda: defaultdict(set))

for idx, row in df.iterrows():
    role_type = row['ROLE TYPE STD']
    position_name = str(row['QIP POSITION 1ST  NAME']).strip().upper()
    position_code = str(row['FINAL QIP POSITION NAME CODE']).strip()

    # Position NAME -> CODE 매핑
    position_mapping[position_name].add(position_code)
    # CODE -> Position NAME 역매핑
    code_to_names[position_code].add(position_name)
    # TYPE별 분석
    type_position_analysis[role_type][position_name].add(position_code)

# 2. 불일치 케이스 찾기 (하나의 NAME이 여러 CODE를 가지는 경우)
print("\n[2] Position NAME이 여러 CODE를 가지는 케이스 (불일치)")
print("-"*60)

inconsistent_positions = {}
for name, codes in position_mapping.items():
    if len(codes) > 1:
        inconsistent_positions[name] = list(codes)
        print(f"⚠️ {name}: {codes}")

if not inconsistent_positions:
    print("✅ 모든 Position NAME이 일관된 CODE를 가지고 있습니다.")

# 3. Progressive Incentive 대상 직급 분석
print("\n[3] Progressive Incentive 대상 직급 CODE 분석")
print("-"*60)

progressive_positions = [
    'MODEL MASTER',
    'ASSEMBLY INSPECTOR',
    'AUDITOR',
    'TRAINER',
    'AUDIT & TRAINING'
]

for position in progressive_positions:
    matching_names = [name for name in position_mapping.keys() if position in name]
    if matching_names:
        print(f"\n📌 {position} 관련:")
        for name in matching_names:
            codes = position_mapping[name]
            count = len(df[(df['QIP POSITION 1ST  NAME'].str.upper() == name)])
            print(f"  - {name}: CODE={codes}, 인원={count}명")

# 4. CODE별 Position NAME 역매핑
print("\n[4] Position CODE별 NAME 매핑")
print("-"*60)

important_codes = ['D', 'E', 'F', 'G', 'H', 'AFFL-B', 'IB', 'IC', 'D1', 'D2', 'E1', 'E2']
for code in important_codes:
    if code in code_to_names:
        names = code_to_names[code]
        count = len(df[df['FINAL QIP POSITION NAME CODE'] == code])
        print(f"\n📌 CODE '{code}': 인원={count}명")
        for name in names:
            print(f"  - {name}")

# 5. TYPE별 직급 분석
print("\n[5] TYPE별 직급 분포")
print("-"*60)

for role_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
    print(f"\n[{role_type}]")
    type_data = type_position_analysis[role_type]

    # Progressive incentive 대상 찾기
    progressive_found = []
    management_found = []
    basic_found = []

    for position_name, codes in type_data.items():
        count = len(df[(df['ROLE TYPE STD'] == role_type) & (df['QIP POSITION 1ST  NAME'].str.upper() == position_name)])

        # Progressive incentive 대상
        if any(prog in position_name for prog in progressive_positions):
            progressive_found.append((position_name, codes, count))
        # Management positions
        elif any(mgmt in position_name for mgmt in ['MANAGER', 'HEAD', 'GROUP LEADER', 'SUPERVISOR']):
            management_found.append((position_name, codes, count))
        # Basic positions
        else:
            basic_found.append((position_name, codes, count))

    if progressive_found:
        print("  📊 Progressive Incentive 대상:")
        for name, codes, count in progressive_found:
            print(f"    - {name}: CODE={codes}, 인원={count}명")

    if management_found:
        print("  👔 Management 직급:")
        for name, codes, count in management_found[:5]:  # 상위 5개만
            print(f"    - {name}: CODE={codes}, 인원={count}명")

    if basic_found:
        print(f"  📋 Basic 직급: {len(basic_found)}개")

# 6. 문제가 있는 직원 찾기 (Progressive incentive 대상인데 0 VND)
print("\n[6] Progressive Incentive 대상인데 0 VND 받은 직원")
print("-"*60)

for position in progressive_positions:
    mask = (df['QIP POSITION 1ST  NAME'].str.upper().str.contains(position, na=False)) & \
           (df['September_Incentive'] == 0) & \
           (df['conditions_pass_rate'] == 100)

    problem_employees = df[mask]
    if len(problem_employees) > 0:
        print(f"\n⚠️ {position}:")
        for idx, emp in problem_employees.iterrows():
            print(f"  - {emp['Full Name']} (CODE={emp['FINAL QIP POSITION NAME CODE']}): " +
                  f"100% 충족했지만 0 VND")

# 7. 제안: Position CODE 매핑 테이블
print("\n[7] 제안: Position CODE 매핑 테이블")
print("-"*60)

code_mapping_suggestion = {
    "progressive_incentive_codes": [],
    "management_codes": [],
    "basic_type1_codes": []
}

# Progressive incentive codes 수집
for position in progressive_positions:
    for name, codes in position_mapping.items():
        if position in name:
            code_mapping_suggestion["progressive_incentive_codes"].extend(codes)

# 중복 제거
code_mapping_suggestion["progressive_incentive_codes"] = list(set(code_mapping_suggestion["progressive_incentive_codes"]))

print("제안하는 CODE 매핑:")
print(f"Progressive Incentive CODEs: {code_mapping_suggestion['progressive_incentive_codes']}")

# JSON 파일로 저장
with open('position_code_mapping_analysis.json', 'w', encoding='utf-8') as f:
    json.dump({
        "position_mapping": {k: list(v) for k, v in position_mapping.items()},
        "code_to_names": {k: list(v) for k, v in code_to_names.items()},
        "inconsistent_positions": inconsistent_positions,
        "suggested_code_mapping": code_mapping_suggestion
    }, f, ensure_ascii=False, indent=2)

print("\n✅ 분석 결과가 position_code_mapping_analysis.json에 저장되었습니다.")

# 8. 현재 코드의 문제점
print("\n[8] 현재 코드의 문제점")
print("-"*60)
print("❌ 현재 코드는 'QIP POSITION 1ST NAME'만 확인")
print("❌ 'FINAL QIP POSITION NAME CODE'를 무시")
print("❌ MODEL MASTER의 CODE 'D'를 인식하지 못함")
print("✅ 해결: NAME과 CODE 둘 다 확인하도록 수정 필요")

print("\n" + "="*80)
print("🎯 분석 완료")
print("="*80)