#!/usr/bin/env python3
"""
Option B: QIP POSITION 1ST NAME 기반 매핑 테스트
MODEL MASTER 등 누락된 직위를 위한 대체 매핑 로직
"""

import pandas as pd
import json

print("="*80)
print("🔧 OPTION B: QIP POSITION 1ST NAME 매핑 테스트")
print("="*80)

# CSV 파일 로드
csv_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
df = pd.read_csv(csv_file)

# Position Name to Incentive 매핑 (예시 금액)
position_name_incentives = {
    'MODEL MASTER': {
        'base_amount': 200000,  # 기본 금액 200K VND
        'conditions': ['attendance', 'working_days']
    },
    'MANAGER': {
        'base_amount': 500000,  # 기본 금액 500K VND
        'conditions': ['attendance']
    },
    'GROUP LEADER': {
        'base_amount': 300000,  # 기본 금액 300K VND
        'conditions': ['attendance', 'working_days']
    }
}

# 현재 MODEL MASTER 상태
print("\n[1] 현재 MODEL MASTER 상태 (Option A - FINAL CODE 기반)")
print("-"*60)

model_masters = df[df['QIP POSITION 1ST  NAME'] == 'MODEL MASTER']
for idx, row in model_masters.iterrows():
    print(f"직원: {row['Full Name']}")
    print(f"  FINAL CODE: {row['FINAL QIP POSITION NAME CODE']}")
    print(f"  현재 인센티브: {row['September_Incentive']:,.0f} VND")
    print(f"  Source: {row['Source_Final_Incentive']:,.0f} VND")
    print(f"  조건 충족: {row['conditions_pass_rate']:.0f}%")
    print()

current_total = model_masters['September_Incentive'].sum()
print(f"현재 총액: {current_total:,.0f} VND")

# Option B 시뮬레이션
print("\n[2] Option B 시뮬레이션 (QIP POSITION 1ST NAME 기반)")
print("-"*60)

# 새로운 계산 로직
def calculate_incentive_by_position_name(row):
    position_name = row['QIP POSITION 1ST  NAME']

    # position_name_incentives에 있는 경우
    if position_name in position_name_incentives:
        config = position_name_incentives[position_name]
        base_amount = config['base_amount']

        # 조건 충족 확인
        if row['conditions_pass_rate'] >= 100:
            return base_amount
        else:
            # 부분 충족 시 비율 적용
            return base_amount * (row['conditions_pass_rate'] / 100)

    # 기존 로직 (FINAL CODE 기반) 사용
    return row['September_Incentive']

# MODEL MASTER에 새 계산 적용
simulated_incentives = []
for idx, row in model_masters.iterrows():
    new_incentive = calculate_incentive_by_position_name(row)
    simulated_incentives.append({
        'name': row['Full Name'],
        'current': row['September_Incentive'],
        'new': new_incentive,
        'difference': new_incentive - row['September_Incentive']
    })

    print(f"직원: {row['Full Name']}")
    print(f"  현재: {row['September_Incentive']:,.0f} VND")
    print(f"  Option B 적용: {new_incentive:,.0f} VND")
    print(f"  차이: +{new_incentive - row['September_Incentive']:,.0f} VND")
    print()

# 전체 영향 분석
print("\n[3] 전체 영향 분석")
print("-"*60)

# 모든 누락된 코드에 대해 시뮬레이션
missing_codes = ['D', 'Z', 'X', 'OF3', 'A4B', 'A2B']
affected_employees = df[df['FINAL QIP POSITION NAME CODE'].isin(missing_codes)]

print(f"영향받는 직원 수: {len(affected_employees)}명")

total_current = affected_employees['September_Incentive'].sum()
total_new = 0

for idx, row in affected_employees.iterrows():
    new_incentive = calculate_incentive_by_position_name(row)
    total_new += new_incentive

print(f"현재 총 인센티브: {total_current:,.0f} VND")
print(f"Option B 적용 시: {total_new:,.0f} VND")
print(f"추가 지급액: {total_new - total_current:,.0f} VND")

# 상세 분석
print("\n[4] 직위별 영향 분석")
print("-"*60)

position_impact = {}
for idx, row in affected_employees.iterrows():
    position_name = row['QIP POSITION 1ST  NAME']
    if position_name not in position_impact:
        position_impact[position_name] = {
            'count': 0,
            'current_total': 0,
            'new_total': 0
        }

    position_impact[position_name]['count'] += 1
    position_impact[position_name]['current_total'] += row['September_Incentive']
    new_incentive = calculate_incentive_by_position_name(row)
    position_impact[position_name]['new_total'] += new_incentive

for position, data in position_impact.items():
    print(f"{position}:")
    print(f"  인원: {data['count']}명")
    print(f"  현재: {data['current_total']:,.0f} VND")
    print(f"  Option B: {data['new_total']:,.0f} VND")
    print(f"  증가액: +{data['new_total'] - data['current_total']:,.0f} VND")
    print()

# 권고사항
print("\n[5] 권고사항")
print("-"*60)
print("✅ Option B 장점:")
print("  - 즉시 적용 가능 (코드 수정만으로)")
print("  - position_condition_matrix.json 수정 불필요")
print("  - MODEL MASTER 등 누락 직위 즉시 해결")
print()
print("⚠️ Option B 단점:")
print("  - 이중 매핑 로직 (복잡도 증가)")
print("  - 향후 유지보수 어려움")
print()
print("📌 추천:")
print("  1. Option B로 즉시 문제 해결")
print("  2. 이후 Option A (position_matrix.json 업데이트) 진행")
print("  3. 최종적으로 통합된 단일 매핑 체계 구축")