#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def show_condition_summary():
    """각 TYPE별 조건 적용 요약"""
    
    with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)
    
    conditions = matrix['conditions']
    
    print("=" * 80)
    print("TYPE별 조건 적용 요약")
    print("=" * 80)
    
    # TYPE-1 요약
    print("\n### TYPE-1 직급별 적용 조건 ###")
    type1_positions = {
        "MANAGER, A.MANAGER, (V) SUPERVISOR, GROUP LEADER": [1,2,3,4],
        "LINE LEADER": [1,2,3,4,7],
        "AQL INSPECTOR": [1,2,3,4,5],
        "ASSEMBLY INSPECTOR": [1,2,3,4,5,6,9,10],
        "AUDIT & TRAINING": [1,2,3,4,7,8],
        "MODEL MASTER": [1,2,3,4,8]
    }
    for positions, conds in type1_positions.items():
        print(f"  {positions}:")
        print(f"    출근: {[c for c in conds if c <= 4]}")
        print(f"    AQL: {[c for c in conds if 5 <= c <= 8] or 'N/A'}")
        print(f"    5PRS: {[c for c in conds if 9 <= c <= 10] or 'N/A'}")
    
    print("\n### TYPE-2 모든 직급 ###")
    print("  모든 직급: 출근 조건[1,2,3,4]만 적용")
    print("  AQL 조건[5,6,7,8]: N/A")
    print("  5PRS 조건[9,10]: N/A")
    
    print("\n### TYPE-3 모든 직급 ###")
    print("  모든 조건[1-10]: N/A")
    
    print("\n" + "=" * 80)
    print("조건 상세:")
    for cond_id, cond in conditions.items():
        print(f"  {cond_id}. {cond['description']}")
    print("=" * 80)

if __name__ == "__main__":
    show_condition_summary()