#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
from collections import defaultdict

def verify_position_conditions():
    """모든 TYPE과 직급에 대한 조건 매핑 확인"""
    
    # JSON 설정 파일 로드
    with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)
    
    # Type 정보 로드
    type_df = pd.read_csv('input_files/Type Info_August.csv')
    
    # 직급별 Type 집계
    position_types = defaultdict(set)
    for _, row in type_df.iterrows():
        position_types[row['Position']].add(row['Type'])
    
    print("=" * 80)
    print("조건 매핑 검증 보고서")
    print("=" * 80)
    
    # 각 Type별 설정 확인
    for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        print(f"\n### {type_name} 검증 ###")
        type_config = matrix['position_matrix'].get(type_name, {})
        
        # TYPE-3는 특별 처리
        if type_name == 'TYPE-3':
            print("  ✓ TYPE-3: 모든 조건 N/A 처리 (하드코딩)")
            continue
        
        # 해당 Type의 모든 직급 확인
        type_positions = [pos for pos, types in position_types.items() if type_name in types]
        
        for position in sorted(type_positions):
            # 매칭되는 설정 찾기
            matched_config = None
            for config_key, config in type_config.items():
                if config_key == 'default':
                    continue
                patterns = config.get('patterns', [])
                if any(pattern in position for pattern in patterns):
                    matched_config = config
                    break
            
            if not matched_config:
                matched_config = type_config.get('default', {})
            
            applicable = matched_config.get('applicable_conditions', [])
            excluded = matched_config.get('excluded_conditions', [])
            
            # 조건 카테고리별 확인
            attendance_conds = [c for c in applicable if c <= 4]
            aql_conds = [c for c in applicable if 5 <= c <= 8]
            prs_conds = [c for c in applicable if 9 <= c <= 10]
            
            print(f"\n  직급: {position}")
            print(f"    - 출근 조건 (1-4): {attendance_conds if attendance_conds else 'N/A'}")
            print(f"    - AQL 조건 (5-8): {aql_conds if aql_conds else 'N/A'}")
            print(f"    - 5PRS 조건 (9-10): {prs_conds if prs_conds else 'N/A'}")
            
            if matched_config.get('special_calculation'):
                print(f"    ★ 특별 계산: {matched_config['special_calculation']}")
    
    print("\n" + "=" * 80)
    print("검증 완료")
    print("=" * 80)

if __name__ == "__main__":
    verify_position_conditions()