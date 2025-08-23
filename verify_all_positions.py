#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
전체 타입별 직급별 조건 적용 검증 스크립트
각 타입과 직급별로 조건이 올바르게 적용되는지 확인
"""

import pandas as pd
from pathlib import Path

def verify_all_positions():
    """모든 타입별 직급별 조건 적용 검증"""
    
    # CSV 파일 읽기
    csv_path = Path("output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv")
    df = pd.read_csv(csv_path)
    
    print("=" * 80)
    print("전체 타입별 직급별 조건 적용 검증")
    print("=" * 80)
    
    # 조건 정의
    condition_matrix = {
        # 특수 직급 (타입 무관)
        "(V) SUPERVISOR": {
            "applicable_conditions": 4,
            "description": "출근 4개만 (타입 무관)",
            "exclude": ["AQL 전체", "5PRS 전체"]
        },
        
        # TYPE-1 직급별 조건
        "TYPE-1": {
            "SUPERVISOR": {
                "applicable_conditions": 9,
                "description": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
                "exclude": ["6번 3개월 연속"]
            },
            "MANAGER": {
                "applicable_conditions": 9,
                "description": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
                "exclude": ["6번 3개월 연속"]
            },
            "A.MANAGER": {
                "applicable_conditions": 9,
                "description": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
                "exclude": ["6번 3개월 연속"]
            },
            "DEPUTY MANAGER": {
                "applicable_conditions": 9,
                "description": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
                "exclude": ["6번 3개월 연속"]
            },
            "TEAM LEADER": {
                "applicable_conditions": 9,
                "description": "출근 4 + AQL 3(5,7,8) + 5PRS 2",
                "exclude": ["6번 3개월 연속"]
            },
            "GROUP LEADER": {
                "applicable_conditions": 8,
                "description": "출근 4 + AQL 2(5,8) + 5PRS 2",
                "exclude": ["6번 3개월 연속", "7번 부하직원"]
            },
            "ASSEMBLY INSPECTOR": {
                "applicable_conditions": 8,
                "description": "출근 4 + AQL 2(5,6) + 5PRS 2",
                "exclude": ["7번 부하직원", "8번 구역담당"]
            },
            "AQL INSPECTOR": {
                "applicable_conditions": 8,
                "description": "출근 4 + AQL 2(5,6) + 5PRS 2",
                "exclude": ["7번 부하직원", "8번 구역담당"]
            },
            "MODEL MASTER": {
                "applicable_conditions": 5,
                "description": "출근 4 + AQL 1(8번만)",
                "exclude": ["5번 개인", "6번 연속", "7번 부하", "9번 합격률", "10번 물량"]
            },
            "AUDIT & TRAINING TEAM": {
                "applicable_conditions": 6,
                "description": "출근 4 + AQL 2(7,8)",
                "exclude": ["5번 개인", "6번 연속", "9번 합격률", "10번 물량"]
            },
            "LINE LEADER": {
                "applicable_conditions": 5,
                "description": "출근 4 + AQL 1(7번만)",
                "exclude": ["5번 개인", "6번 연속", "8번 구역", "9번 합격률", "10번 물량"]
            },
            "BOTTOM INSPECTOR": {
                "applicable_conditions": 6,
                "description": "출근 4 + 5PRS 2",
                "exclude": ["AQL 전체"]
            },
            "STITCHING INSPECTOR": {
                "applicable_conditions": 6,
                "description": "출근 4 + 5PRS 2",
                "exclude": ["AQL 전체"]
            },
            "MTL INSPECTOR": {
                "applicable_conditions": 6,
                "description": "출근 4 + 5PRS 2",
                "exclude": ["AQL 전체"]
            }
        },
        
        # TYPE-2 직급별 조건
        "TYPE-2": {
            "DEFAULT": {
                "applicable_conditions": 6,
                "description": "출근 4 + 5PRS 2",
                "exclude": ["AQL 전체"]
            }
        },
        
        # TYPE-3 직급별 조건
        "TYPE-3": {
            "DEFAULT": {
                "applicable_conditions": 4,
                "description": "출근 4개만",
                "exclude": ["AQL 전체", "5PRS 전체"]
            }
        }
    }
    
    # 문제점 발견 목록
    issues = []
    
    # 타입별 직급별 검증
    for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        type_df = df[df['ROLE TYPE STD'] == type_name]
        positions = type_df['QIP POSITION 1ST  NAME'].value_counts()
        
        print(f"\n### {type_name} 검증")
        print("-" * 60)
        
        for position, count in positions.items():
            if pd.isna(position):
                continue
            
            # (V) SUPERVISOR 특수 처리
            if "(V) SUPERVISOR" in position.upper():
                expected = condition_matrix["(V) SUPERVISOR"]
                print(f"  {position:30s} ({count:3d}명)")
                print(f"    예상: {expected['description']}")
                print(f"    ✅ 특수 직급 - 타입 무관 4개 조건만 적용")
                continue
            
            # 해당 타입의 직급별 조건 찾기
            expected = None
            
            if type_name == "TYPE-1":
                # TYPE-1의 특정 직급 찾기
                for key, value in condition_matrix["TYPE-1"].items():
                    if key in position.upper():
                        expected = value
                        break
                
                # 매칭되지 않은 직급 확인
                if not expected:
                    issues.append(f"{type_name} - {position}: 조건 매핑 없음")
                    print(f"  ⚠️ {position:30s} ({count:3d}명) - 조건 매핑 없음!")
                else:
                    print(f"  {position:30s} ({count:3d}명)")
                    print(f"    예상: {expected['description']}")
            
            elif type_name == "TYPE-2":
                # (V) SUPERVISOR가 아닌 모든 TYPE-2는 동일
                expected = condition_matrix["TYPE-2"]["DEFAULT"]
                print(f"  {position:30s} ({count:3d}명)")
                print(f"    예상: {expected['description']}")
            
            else:  # TYPE-3
                expected = condition_matrix["TYPE-3"]["DEFAULT"]
                print(f"  {position:30s} ({count:3d}명)")
                print(f"    예상: {expected['description']}")
    
    # 문제점 요약
    if issues:
        print("\n" + "=" * 80)
        print("⚠️ 발견된 문제점")
        print("=" * 80)
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n" + "=" * 80)
        print("✅ 모든 타입별 직급별 조건 매핑 정상")
        print("=" * 80)
    
    # 특별 검증: STITCHING INSPECTOR가 TYPE-1에 있는지 확인
    type1_df = df[df['ROLE TYPE STD'] == 'TYPE-1']
    stitching_in_type1 = type1_df[type1_df['QIP POSITION 1ST  NAME'].str.contains('STITCHING', na=False)]
    if len(stitching_in_type1) > 0:
        print("\n⚠️ STITCHING INSPECTOR가 TYPE-1에 있음 (TYPE-2여야 함)")
        print(f"  발견: {len(stitching_in_type1)}명")
    
    # 특별 검증: (V) SUPERVISOR 조건 확인
    v_supervisor_df = df[df['QIP POSITION 1ST  NAME'].str.contains('(V) SUPERVISOR', na=False, regex=False)]
    if len(v_supervisor_df) > 0:
        print(f"\n(V) SUPERVISOR 검증: {len(v_supervisor_df)}명")
        for type_name in v_supervisor_df['ROLE TYPE STD'].unique():
            count = len(v_supervisor_df[v_supervisor_df['ROLE TYPE STD'] == type_name])
            print(f"  {type_name}: {count}명 - 모두 4개 조건만 적용되어야 함")

if __name__ == "__main__":
    verify_all_positions()
    print("\n검증 완료")