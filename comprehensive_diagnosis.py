#!/usr/bin/env python3
"""
포괄적인 MODEL MASTER 및 전체 포지션 진단 스크립트
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("🔍 COMPREHENSIVE POSITION DIAGNOSIS")
print("="*80)

# 1. position_condition_matrix.json 검증
print("\n[1] position_condition_matrix.json 검증")
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

# Check positions section
positions_count = len(position_matrix.get('positions', {}))
print(f"   - positions 섹션에 {positions_count}개 코드 등록됨")

# Check if 'D' exists for MODEL MASTER
if 'D' in position_matrix.get('positions', {}):
    d_config = position_matrix['positions']['D']
    print(f"   ✅ CODE 'D' (MODEL MASTER) 설정:")
    print(f"      - Type: {d_config.get('type')}")
    print(f"      - Conditions: {d_config.get('applicable_conditions')}")
    print(f"      - Incentive: {d_config.get('incentive_amount')}")
else:
    print("   ❌ CODE 'D' not found in positions")

# Check fallback_positions
if 'fallback_positions' in position_matrix:
    print(f"\n   - fallback_positions 섹션 존재: {list(position_matrix['fallback_positions'].keys())}")
else:
    print("   - fallback_positions 섹션 없음")

# 2. CSV 데이터 분석
print("\n[2] CSV 데이터 분석")
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')

# 모든 포지션별 인센티브 현황
position_summary = df.groupby('QIP POSITION 1ST  NAME').agg({
    'Employee No': 'count',
    'September_Incentive': ['mean', 'sum', lambda x: (x == 0).sum()]
}).round(0)
position_summary.columns = ['Count', 'Avg_Incentive', 'Total_Incentive', 'Zero_Count']

print("\n   포지션별 인센티브 현황:")
for pos_name, data in position_summary.iterrows():
    if data['Zero_Count'] > 0:
        print(f"   ⚠️ {pos_name}: {int(data['Count'])}명 중 {int(data['Zero_Count'])}명이 0 VND")
    else:
        print(f"   ✅ {pos_name}: {int(data['Count'])}명, 평균 {data['Avg_Incentive']:,.0f} VND")

# 3. 조건 충족률 분석
print("\n[3] 조건 충족률 이상 케이스 분석")
# conditions_pass_rate가 높은데 incentive가 0인 케이스
anomalies = df[(df['conditions_pass_rate'] >= 80) & (df['September_Incentive'] == 0)]
if len(anomalies) > 0:
    print(f"\n   ❌ 조건 충족률 80% 이상인데 인센티브 0인 직원: {len(anomalies)}명")
    for idx, row in anomalies.head(10).iterrows():
        print(f"      - {row['Full Name']} ({row['Employee No']}): {row['QIP POSITION 1ST  NAME']}, 충족률 {row['conditions_pass_rate']}%")

# 4. 매핑되지 않은 코드 확인
print("\n[4] 매핑되지 않은 FINAL CODE 분석")
unmapped_codes = []
for idx, row in df.iterrows():
    final_code = row.get('FINAL QIP POSITION NAME CODE', '')
    if final_code and final_code not in position_matrix.get('positions', {}):
        if final_code not in unmapped_codes:
            unmapped_codes.append(final_code)

if unmapped_codes:
    print(f"   ❌ 매핑되지 않은 코드: {unmapped_codes}")
    for code in unmapped_codes:
        affected = df[df['FINAL QIP POSITION NAME CODE'] == code]
        positions = affected['QIP POSITION 1ST  NAME'].unique()
        print(f"      - Code '{code}': {len(affected)}명 ({', '.join(positions)})")
else:
    print("   ✅ 모든 FINAL CODE가 매핑됨")

# 5. 계산 로직 검증 포인트
print("\n[5] 계산 로직 검증 필요 사항")
print("   1. MODEL MASTER의 pass_rate 계산 시점 확인 필요")
print("   2. fallback_positions 실제 적용 여부 확인 필요")
print("   3. 대시보드 JavaScript의 조건 표시 로직 확인 필요")

# 6. MODEL MASTER 상세 분석
print("\n[6] MODEL MASTER 상세 분석")
model_masters = df[df['QIP POSITION 1ST  NAME'] == 'MODEL MASTER']
for idx, row in model_masters.iterrows():
    print(f"\n   {row['Full Name']} ({row['Employee No']}):")
    print(f"      - FINAL CODE: {row['FINAL QIP POSITION NAME CODE']}")
    print(f"      - TYPE: {row.get('Type', 'N/A')}")
    print(f"      - conditions_pass_rate: {row['conditions_pass_rate']}%")
    print(f"      - September_Incentive: {row['September_Incentive']} VND")
    print(f"      - Attendance: {row.get('Actual Working Days', 0)}/{row.get('Total Working Days', 0)} days")
    print(f"      - Area Reject Rate: {row.get('Area_Reject_Rate', 0):.2f}%")

    # Check what conditions are shown in Excel
    condition_cols = [col for col in df.columns if col.startswith('Condition_')]
    if condition_cols:
        print("      - Individual Conditions in Excel:")
        for col in condition_cols:
            if pd.notna(row[col]):
                print(f"         {col}: {row[col]}")

print("\n" + "="*80)
print("진단 완료 - 개선 필요 사항 확인됨")
print("="*80)