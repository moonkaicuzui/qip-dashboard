#!/usr/bin/env python3
"""
JSON 조건 매트릭스 검증 스크립트
모든 타입/직급별로 조건이 올바르게 적용되는지 확인
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import the modules
from step1_인센티브_계산_개선버전 import load_position_condition_matrix, get_position_config_from_matrix
from step2_dashboard_version4 import load_position_condition_matrix as load_matrix_v2

def verify_all_positions():
    """모든 타입/직급별 JSON 적용 검증"""
    
    # Load matrix
    matrix = load_position_condition_matrix()
    if not matrix:
        print("❌ Matrix 로드 실패!")
        return False
    
    print("=" * 80)
    print("📊 모든 타입/직급별 JSON 조건 적용 검증")
    print("=" * 80)
    
    # Test cases for all positions
    test_cases = [
        # TYPE-1
        ('TYPE-1', 'MANAGER', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-1', 'A.MANAGER', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-1', '(V) SUPERVISOR', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-1', 'GROUP LEADER', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-1', 'LINE LEADER', [1,2,3,4,7], [5,6,8,9,10]),  # 중요: 조건 7 포함!
        ('TYPE-1', 'AQL INSPECTOR', [1,2,3,4,5], [6,7,8,9,10]),
        ('TYPE-1', 'ASSEMBLY INSPECTOR', [1,2,3,4,5,6,9,10], [7,8]),
        ('TYPE-1', 'AUDIT & TRAINING TEAM', [1,2,3,4,7,8], [5,6,9,10]),
        ('TYPE-1', 'MODEL MASTER', [1,2,3,4,8], [5,6,7,9,10]),
        
        # TYPE-2
        ('TYPE-2', 'LINE LEADER', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'GROUP LEADER', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'AQL INSPECTOR', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'ASSEMBLY INSPECTOR', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'BOTTOM INSPECTOR', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'CUTTING INSPECTOR', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'MTL INSPECTOR', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'STITCHING INSPECTOR', [1,2,3,4], [5,6,7,8,9,10]),
        ('TYPE-2', 'QA TEAM', [1,2,3,4], [5,6,7,8,9,10]),
        
        # TYPE-3
        ('TYPE-3', 'NEW QIP MEMBER', [], [1,2,3,4,5,6,7,8,9,10]),
    ]
    
    all_passed = True
    failed_cases = []
    
    for emp_type, position, expected_applicable, expected_excluded in test_cases:
        config = get_position_config_from_matrix(emp_type, position)
        
        if config:
            actual_applicable = config.get('applicable_conditions', [])
            actual_excluded = config.get('excluded_conditions', [])
            
            # 검증
            applicable_match = set(actual_applicable) == set(expected_applicable)
            excluded_match = set(actual_excluded) == set(expected_excluded)
            
            if applicable_match and excluded_match:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
                all_passed = False
                failed_cases.append({
                    'type': emp_type,
                    'position': position,
                    'expected_applicable': expected_applicable,
                    'actual_applicable': actual_applicable,
                    'expected_excluded': expected_excluded,
                    'actual_excluded': actual_excluded
                })
            
            print(f"\n{status} {emp_type} - {position}")
            print(f"  적용 조건: {actual_applicable} (예상: {expected_applicable})")
            print(f"  제외 조건: {actual_excluded} (예상: {expected_excluded})")
        else:
            print(f"\n❌ {emp_type} - {position}: 설정을 찾을 수 없음")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 모든 타입/직급에 대한 JSON 조건이 올바르게 적용됩니다!")
    else:
        print(f"❌ {len(failed_cases)}개의 불일치 발견:")
        for case in failed_cases:
            print(f"\n  • {case['type']} - {case['position']}:")
            print(f"    - 적용 조건 불일치: {case['actual_applicable']} ≠ {case['expected_applicable']}")
            print(f"    - 제외 조건 불일치: {case['actual_excluded']} ≠ {case['expected_excluded']}")
    
    return all_passed

def check_condition_descriptions():
    """조건 설명 확인"""
    matrix = load_position_condition_matrix()
    if not matrix:
        return
    
    print("\n" + "=" * 80)
    print("📋 조건 ID 매핑 확인")
    print("=" * 80)
    
    conditions = matrix.get('conditions', {})
    for cond_id, cond_info in conditions.items():
        print(f"  조건 {cond_id}: {cond_info.get('description', 'N/A')}")
        if int(cond_id) in [6, 7, 8]:
            print(f"    → ⚠️ 3개월 연속 체크 필요!")

if __name__ == "__main__":
    verify_all_positions()
    check_condition_descriptions()