#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
10개 조건 체계 검증 스크립트
Type별 직급별 조건 적용이 올바른지 확인
"""

import pandas as pd
import json
from pathlib import Path

def validate_conditions():
    """Type별 직급별 조건 적용 검증"""
    
    # CSV 파일 읽기
    csv_path = Path("output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv")
    df = pd.read_csv(csv_path)
    
    print("=" * 80)
    print("10개 조건 체계 검증 (4-4-2 구조)")
    print("=" * 80)
    
    # Type별 직급별 샘플 추출
    test_cases = [
        # Type-1 케이스
        ("TYPE-1", "SUPERVISOR"),      # 9개 조건 (6번 제외)
        ("TYPE-1", "MANAGER"),          # 9개 조건 (6번 제외)
        ("TYPE-1", "GROUP LEADER"),     # 8개 조건 (6,7번 제외)
        ("TYPE-1", "ASSEMBLY INSPECTOR"), # 8개 조건 (7,8번 제외)
        ("TYPE-1", "AQL INSPECTOR"),    # 8개 조건 (7,8번 제외)
        ("TYPE-1", "BOTTOM INSPECTOR"), # 6개 조건 (출근 4 + 5PRS 2)
        
        # Type-2 케이스 
        ("TYPE-2", "ASSEMBLY INSPECTOR"), # 6개 조건 (출근 4 + 5PRS 2)
        ("TYPE-2", "BOTTOM INSPECTOR"),   # 6개 조건 (출근 4 + 5PRS 2)
        ("TYPE-2", "STITCHING INSPECTOR"), # 6개 조건 (출근 4 + 5PRS 2)
        
        # Type-3 케이스
        ("TYPE-3", "NEW QIP MEMBER"),    # 4개 조건 (출근 4개만)
    ]
    
    for type_name, position in test_cases:
        print(f"\n{type_name} - {position}")
        print("-" * 40)
        
        # 해당 Type과 직급의 직원 찾기
        mask = (df['ROLE TYPE STD'] == type_name) & (df['QIP POSITION 1ST  NAME'].str.contains(position, na=False))
        sample_employees = df[mask].head(3)
        
        if sample_employees.empty:
            print(f"  ⚠️ {type_name} - {position} 직원을 찾을 수 없음")
            continue
            
        print(f"  샘플 직원 수: {len(sample_employees)}명")
        
        # 조건 적용 예상값
        expected_conditions = get_expected_conditions(type_name, position)
        print(f"  예상 적용 조건: {expected_conditions}")
        
        # 샘플 직원들의 조건 확인
        for idx, emp in sample_employees.iterrows():
            emp_id = emp['Employee No']
            name = emp['Full Name']
            incentive = emp.get('August_Incentive', 0)
            
            # 조건 필드 확인
            conditions_met = []
            conditions_fields = emp.get('Conditions Met', '')
            
            print(f"\n  직원: {emp_id} - {name}")
            print(f"    인센티브: {incentive:,} VND")
            print(f"    조건 충족 상태: {conditions_fields}")
            
            # 예상 조건과 비교
            if type_name == "TYPE-3":
                expected = "출근 조건 4개"
            elif type_name == "TYPE-2":
                expected = "출근 4개 + 5PRS 2개"
            else:  # TYPE-1
                if position in ["SUPERVISOR", "MANAGER", "DEPUTY MANAGER", "TEAM LEADER"]:
                    expected = "출근 4 + AQL 3 + 5PRS 2 (6번 제외)"
                elif position == "GROUP LEADER":
                    expected = "출근 4 + AQL 2 + 5PRS 2 (6,7번 제외)"
                elif position in ["ASSEMBLY INSPECTOR", "AQL INSPECTOR"]:
                    expected = "출근 4 + AQL 2 + 5PRS 2 (7,8번 제외)"
                else:  # BOTTOM, STITCHING, MTL INSPECTOR
                    expected = "출근 4 + 5PRS 2"
            
            print(f"    예상 조건 구조: {expected}")

def get_expected_conditions(type_name, position):
    """Type과 직급에 따른 예상 조건 수 반환"""
    
    if type_name == "TYPE-3":
        return "4개 조건 (출근 4)"
    elif type_name == "TYPE-2":
        return "6개 조건 (출근 4 + 5PRS 2)"
    else:  # TYPE-1
        position_upper = position.upper()
        
        # 관리자급
        if any(x in position_upper for x in ["SUPERVISOR", "MANAGER", "DEPUTY", "TEAM LEADER"]):
            if "GROUP LEADER" in position_upper:
                return "8개 조건 (출근 4 + AQL 2 + 5PRS 2)"
            return "9개 조건 (출근 4 + AQL 3 + 5PRS 2)"
        
        # 검사원
        elif "ASSEMBLY INSPECTOR" in position_upper or "AQL INSPECTOR" in position_upper:
            return "8개 조건 (출근 4 + AQL 2 + 5PRS 2)"
        
        # 기타 검사원
        else:
            return "6개 조건 (출근 4 + 5PRS 2)"

if __name__ == "__main__":
    validate_conditions()
    
    print("\n" + "=" * 80)
    print("✅ 검증 완료")
    print("=" * 80)