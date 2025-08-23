#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
모든 직급의 조건 적용 체크 스크립트
"""

import pandas as pd
from pathlib import Path

# CSV 파일 읽기
csv_path = Path("output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv")
df = pd.read_csv(csv_path)

print("=" * 80)
print("모든 직급별 조건 적용 매트릭스 점검")
print("=" * 80)

# Type별로 모든 직급 추출
for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
    print(f"\n### {type_name} 직급 목록")
    print("-" * 60)
    
    type_df = df[df['ROLE TYPE STD'] == type_name]
    positions = type_df['QIP POSITION 1ST  NAME'].value_counts()
    
    for position, count in positions.items():
        if pd.isna(position):
            continue
        print(f"  {position}: {count}명")

print("\n" + "=" * 80)
print("Type-1 직급별 예상 조건 매핑")
print("=" * 80)

# Type-1 직급별 조건 매핑 정의
type1_conditions = {
    # 관리자급 - 9개 조건 (6번만 제외)
    "SUPERVISOR": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
    "(V) SUPERVISOR": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
    "MANAGER": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
    "A.MANAGER": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
    "DEPUTY MANAGER": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
    "TEAM LEADER": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
    
    # GROUP LEADER - 8개 조건 (6,7번 제외)
    "GROUP LEADER": "출근 4 + AQL 2(5,8) + 5PRS 2",
    
    # 검사원 - 8개 조건 (7,8번 제외)
    "ASSEMBLY INSPECTOR": "출근 4 + AQL 2(5,6) + 5PRS 2",
    "AQL INSPECTOR": "출근 4 + AQL 2(5,6) + 5PRS 2",
    
    # 특수 직급
    "MODEL MASTER": "출근 4 + AQL 1(8번만)",
    "AUDIT & TRAINING TEAM": "출근 4 + AQL 2(7,8)",
    "LINE LEADER": "출근 4 + AQL 1(7번만)",
    
    # 기타 검사원 - 6개 조건
    "BOTTOM INSPECTOR": "출근 4 + 5PRS 2",
    "STITCHING INSPECTOR": "출근 4 + 5PRS 2",
    "MTL INSPECTOR": "출근 4 + 5PRS 2",
}

print("\nType-1 직급별 조건 매핑:")
for position, conditions in type1_conditions.items():
    print(f"  {position:25s} → {conditions}")

# 실제 데이터에서 Type-1 직급 확인
print("\n실제 Type-1 직급과 매핑 비교:")
print("-" * 60)

type1_df = df[df['ROLE TYPE STD'] == 'TYPE-1']
actual_positions = type1_df['QIP POSITION 1ST  NAME'].value_counts()

for position, count in actual_positions.items():
    if pd.isna(position):
        continue
    
    # 정의된 조건 찾기
    mapped = False
    for defined_pos, conditions in type1_conditions.items():
        if defined_pos in str(position).upper():
            print(f"✅ {position:30s} ({count:3d}명) → {conditions}")
            mapped = True
            break
    
    if not mapped:
        print(f"⚠️  {position:30s} ({count:3d}명) → 조건 매핑 없음!")

print("\n" + "=" * 80)
print("점검 완료")
print("=" * 80)