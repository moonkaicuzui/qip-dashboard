#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
from collections import defaultdict

def verify_all_conditions():
    """모든 직급의 조건 매핑 검증"""
    
    # JSON 설정 파일 로드
    with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)
    
    # 인센티브 데이터 로드
    df = pd.read_csv('input_files/2025년 8월 인센티브 지급 세부 정보.csv')
    
    # Type 정보 로드를 위한 함수
    def determine_type_from_position(position):
        """직급명으로부터 Type 결정"""
        position_upper = str(position).upper()
        
        # TYPE-3: NEW QIP MEMBER
        if 'NEW QIP MEMBER' in position_upper:
            return 'TYPE-3'
        
        # TYPE-1 패턴들
        type1_patterns = [
            'MANAGER', 'A.MANAGER', 'A. MANAGER', 'ASSISTANT MANAGER',
            '(V) SUPERVISOR', 'V.SUPERVISOR', 'V SUPERVISOR',
            'GROUP LEADER', 'GROUP-LEADER',
            'LINE LEADER', 'LINE-LEADER',
            'AQL INSPECTOR', 'AQL', 'CFA CERTIFIED',
            'ASSEMBLY INSPECTOR',
            'AUDIT & TRAINING', 'AUDITOR', 'TRAINER',
            'MODEL MASTER', 'SAMPLE'
        ]
        
        for pattern in type1_patterns:
            if pattern in position_upper:
                return 'TYPE-1'
        
        # 기본값 TYPE-2
        return 'TYPE-2'
    
    # 직급별 통계
    position_stats = defaultdict(lambda: {'count': 0, 'types': set()})
    
    for _, row in df.iterrows():
        position = row['QIP POSITION 1ST  NAME']
        emp_type = determine_type_from_position(position)
        position_stats[position]['count'] += 1
        position_stats[position]['types'].add(emp_type)
    
    print("=" * 80)
    print("직급별 조건 매핑 검증")
    print("=" * 80)
    
    # TYPE별로 그룹화
    for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        print(f"\n### {type_name} ###")
        type_positions = [(pos, stats) for pos, stats in position_stats.items() 
                         if type_name in stats['types']]
        
        if not type_positions:
            print("  해당 TYPE에 직원 없음")
            continue
        
        type_matrix = matrix['position_matrix'].get(type_name, {})
        
        for position, stats in sorted(type_positions):
            # 매칭 찾기
            position_upper = position.upper()
            matched_config = None
            matched_key = None
            
            for pos_key, pos_config in type_matrix.items():
                if pos_key == 'default':
                    continue
                patterns = pos_config.get('patterns', [])
                for pattern in patterns:
                    if pattern in position_upper:
                        matched_config = pos_config
                        matched_key = pos_key
                        break
                if matched_config:
                    break
            
            if not matched_config:
                matched_config = type_matrix.get('default', {})
                matched_key = 'default'
            
            applicable = matched_config.get('applicable_conditions', [])
            
            # 카테고리별 분류
            attendance = [c for c in applicable if c <= 4]
            aql = [c for c in applicable if 5 <= c <= 8]
            prs = [c for c in applicable if 9 <= c <= 10]
            
            print(f"\n  {position} ({stats['count']}명) → {matched_key}")
            print(f"    출근: {attendance if attendance else 'N/A'}")
            print(f"    AQL: {aql if aql else 'N/A'}")
            print(f"    5PRS: {prs if prs else 'N/A'}")

if __name__ == "__main__":
    verify_all_conditions()