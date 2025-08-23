#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
타입별/직급별 조건 설정 및 인센티브 지급 검증 스크립트
"""

import pandas as pd
from pathlib import Path
import json

def verify_condition_settings():
    """타입별/직급별 조건 설정 검증"""
    
    # CSV 파일 읽기
    csv_path = Path("output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv")
    if not csv_path.exists():
        csv_path = Path("output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv")
    
    df = pd.read_csv(csv_path)
    
    print("=" * 80)
    print("타입별/직급별 조건 설정 및 인센티브 지급 검증")
    print("=" * 80)
    
    # 조건 매트릭스 정의 (10개 조건 체계)
    condition_matrix = {
        "(V) SUPERVISOR": {
            "conditions": ["출근 4개만"],
            "total": 4,
            "attendance": True,
            "aql": False,
            "5prs": False
        },
        "TYPE-1": {
            "SUPERVISOR": {"conditions": ["출근 4", "AQL 3(5,7,8)", "5PRS 2"], "total": 9},
            "MANAGER": {"conditions": ["출근 4", "AQL 3(5,7,8)", "5PRS 2"], "total": 9},
            "A.MANAGER": {"conditions": ["출근 4", "AQL 3(5,7,8)", "5PRS 2"], "total": 9},
            "DEPUTY MANAGER": {"conditions": ["출근 4", "AQL 3(5,7,8)", "5PRS 2"], "total": 9},
            "TEAM LEADER": {"conditions": ["출근 4", "AQL 3(5,7,8)", "5PRS 2"], "total": 9},
            "GROUP LEADER": {"conditions": ["출근 4", "AQL 2(5,8)", "5PRS 2"], "total": 8},
            "ASSEMBLY INSPECTOR": {"conditions": ["출근 4", "AQL 2(5,6)", "5PRS 2"], "total": 8},
            "AQL INSPECTOR": {"conditions": ["출근 4", "AQL 2(5,6)", "5PRS 2"], "total": 8},
            "MODEL MASTER": {"conditions": ["출근 4", "AQL 1(8)"], "total": 5},
            "AUDIT & TRAINING TEAM": {"conditions": ["출근 4", "AQL 2(7,8)"], "total": 6},
            "LINE LEADER": {"conditions": ["출근 4", "AQL 1(7)"], "total": 5},
            "BOTTOM INSPECTOR": {"conditions": ["출근 4", "5PRS 2"], "total": 6},
            "STITCHING INSPECTOR": {"conditions": ["출근 4", "5PRS 2"], "total": 6},
            "MTL INSPECTOR": {"conditions": ["출근 4", "5PRS 2"], "total": 6}
        },
        "TYPE-2": {
            "DEFAULT": {"conditions": ["출근 4", "5PRS 2"], "total": 6}
        },
        "TYPE-3": {
            "DEFAULT": {"conditions": ["출근 4개만"], "total": 4}
        }
    }
    
    # 1. 타입별 직급별 인센티브 지급 현황
    print("\n### 1. 타입별 직급별 인센티브 지급 현황")
    print("-" * 60)
    
    for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        type_df = df[df['ROLE TYPE STD'] == type_name]
        
        print(f"\n{type_name} (총 {len(type_df)}명)")
        
        # 직급별 통계
        positions = type_df.groupby('QIP POSITION 1ST  NAME').agg({
            'Employee No': 'count',
            'July_Incentive': lambda x: (pd.to_numeric(x.astype(str).str.replace(',', '').str.replace(' VND', ''), errors='coerce') > 0).sum()
        }).rename(columns={'Employee No': '전체', 'July_Incentive': '지급'})
        
        for position, stats in positions.iterrows():
            if pd.isna(position):
                continue
            
            # 예상 조건 수 확인
            expected_conditions = None
            if "(V) SUPERVISOR" in str(position).upper():
                expected_conditions = 4
            elif type_name == "TYPE-1":
                for key in condition_matrix["TYPE-1"]:
                    if key in str(position).upper():
                        expected_conditions = condition_matrix["TYPE-1"][key]["total"]
                        break
            elif type_name == "TYPE-2":
                if "(V) SUPERVISOR" not in str(position).upper():
                    expected_conditions = 6
                else:
                    expected_conditions = 4
            else:  # TYPE-3
                expected_conditions = 4
            
            rate = (stats['지급'] / stats['전체'] * 100) if stats['전체'] > 0 else 0
            status = "✅" if rate > 0 else "⚠️"
            
            print(f"  {status} {position:30s}: {stats['전체']:3d}명 중 {stats['지급']:3d}명 지급 ({rate:.1f}%) - 조건: {expected_conditions}개")
    
    # 2. 조건 충족 상세 분석 (샘플)
    print("\n### 2. 조건 충족 상세 분석 (샘플)")
    print("-" * 60)
    
    # 각 타입별로 샘플 직원 선택
    samples = [
        ("TYPE-1", "(V) SUPERVISOR"),
        ("TYPE-1", "SUPERVISOR"),
        ("TYPE-1", "GROUP LEADER"),
        ("TYPE-1", "MODEL MASTER"),
        ("TYPE-2", "ASSEMBLY INSPECTOR"),
        ("TYPE-2", "(V) SUPERVISOR"),
        ("TYPE-3", "NEW QIP MEMBER")
    ]
    
    for type_name, position_key in samples:
        sample_df = df[(df['ROLE TYPE STD'] == type_name)]
        if position_key:
            sample_df = sample_df[sample_df['QIP POSITION 1ST  NAME'].str.contains(position_key, na=False)]
        
        if len(sample_df) > 0:
            emp = sample_df.iloc[0]
            print(f"\n{type_name} - {position_key}")
            print(f"  직원: {emp['Employee No']} - {emp['Full Name']}")
            print(f"  인센티브: {emp.get('July_Incentive', '0 VND')}")
            
            # Conditions Met 컬럼 확인
            conditions_met = emp.get('Conditions Met', '')
            if conditions_met:
                print(f"  조건 충족 상태: {conditions_met}")
            else:
                print(f"  조건 충족 상태: 데이터 없음")
    
    # 3. 인센티브 지급 로직 검증
    print("\n### 3. 인센티브 지급 로직 검증")
    print("-" * 60)
    
    # 인센티브가 0인 직원 분석
    zero_incentive = df[df['July_Incentive'] == '0 VND']
    print(f"\n인센티브 미지급 직원: {len(zero_incentive)}명")
    
    # 타입별 미지급 분석
    for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        type_zero = zero_incentive[zero_incentive['ROLE TYPE STD'] == type_name]
        if len(type_zero) > 0:
            print(f"\n{type_name} 미지급: {len(type_zero)}명")
            
            # 주요 미지급 사유 분석 (상위 5개 직급)
            top_positions = type_zero['QIP POSITION 1ST  NAME'].value_counts().head(5)
            for position, count in top_positions.items():
                print(f"  - {position}: {count}명")
    
    # 4. (V) SUPERVISOR 특별 검증
    print("\n### 4. (V) SUPERVISOR 특별 검증")
    print("-" * 60)
    
    v_supervisor_df = df[df['QIP POSITION 1ST  NAME'].str.contains('(V) SUPERVISOR', na=False, regex=False)]
    
    if len(v_supervisor_df) > 0:
        print(f"(V) SUPERVISOR 총 {len(v_supervisor_df)}명")
        
        # 타입별 분포
        type_dist = v_supervisor_df['ROLE TYPE STD'].value_counts()
        for type_name, count in type_dist.items():
            v_type_df = v_supervisor_df[v_supervisor_df['ROLE TYPE STD'] == type_name]
            
            # 인센티브 지급 현황
            paid_count = (pd.to_numeric(v_type_df['July_Incentive'].astype(str).str.replace(',', '').str.replace(' VND', ''), errors='coerce') > 0).sum()
            
            print(f"  {type_name}: {count}명 (지급: {paid_count}명)")
            print(f"    → 4개 조건만 적용되어야 함 (출근 조건만)")

if __name__ == "__main__":
    verify_condition_settings()
    print("\n" + "=" * 80)
    print("검증 완료")
    print("=" * 80)