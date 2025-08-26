#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd

def debug_position_matching():
    """디버그: 직급 매칭 확인"""
    
    # JSON 파일 로드
    with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)
    
    # 테스트할 직급들
    test_positions = [
        ('TYPE-1', 'MODEL MASTER'),
        ('TYPE-1', 'LINE LEADER'),
        ('TYPE-1', 'AUDIT & TRAINING TEAM'),
        ('TYPE-1', 'ASSEMBLY INSPECTOR'),
        ('TYPE-1', 'AQL INSPECTOR'),
        ('TYPE-1', '(V) SUPERVISOR'),
        ('TYPE-2', '(V) SUPERVISOR'),
    ]
    
    for type_name, position in test_positions:
        print(f"\n테스트: {type_name} - {position}")
        print("=" * 50)
        
        position_upper = position.upper()
        type_matrix = matrix['position_matrix'].get(type_name, {})
        
        matched = False
        for pos_key, pos_config in type_matrix.items():
            if pos_key == 'default':
                continue
            patterns = pos_config.get('patterns', [])
            for pattern in patterns:
                if pattern in position_upper:
                    print(f"  ✓ 매칭된 패턴: '{pattern}' in config '{pos_key}'")
                    print(f"    적용 조건: {pos_config.get('applicable_conditions', [])}")
                    print(f"    제외 조건: {pos_config.get('excluded_conditions', [])}")
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            default_config = type_matrix.get('default', {})
            print(f"  × 매칭된 패턴 없음 - default 사용")
            print(f"    적용 조건: {default_config.get('applicable_conditions', [])}")
            print(f"    제외 조건: {default_config.get('excluded_conditions', [])}")

if __name__ == "__main__":
    debug_position_matching()