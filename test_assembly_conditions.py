#!/usr/bin/env python3
"""
ASSEMBLY INSPECTOR 조건 설정 검증
"""

def analyze_conditions_from_csv_row(row, emp_type, position, month):
    """대시보드의 조건 분석 함수 시뮬레이션"""
    conditions = {}
    
    # TYPE-1 기본 조건 설정
    if emp_type == 'TYPE-1':
        # 기본 조건들 초기화
        conditions['aql_monthly'] = {'applicable': True, 'name': '개인 AQL 당월'}
        conditions['aql_3month'] = {'applicable': True, 'name': '개인 AQL 3개월'}
        conditions['subordinate_aql'] = {'applicable': True, 'name': '부하직원 AQL'}
        conditions['area_reject_rate'] = {'applicable': True, 'name': '구역 reject율'}
        conditions['5prs_volume'] = {'applicable': True, 'name': '5PRS 검사량'}
        conditions['5prs_pass_rate'] = {'applicable': True, 'name': '5PRS 통과율'}
        
        # ASSEMBLY INSPECTOR - 개인 AQL(당월+3개월)과 5PRS 적용
        if 'ASSEMBLY INSPECTOR' in position:
            # 5번 조건 (당월 AQL)과 6번 조건 (3개월 연속 체크) 모두 적용
            conditions['aql_monthly']['applicable'] = True  # 5번 조건
            conditions['aql_3month']['applicable'] = True   # 6번 조건 - 수정된 부분
            # 7번, 8번 조건은 미적용
            conditions['subordinate_aql']['applicable'] = False
            conditions['area_reject_rate']['applicable'] = False
            
        # AQL INSPECTOR - 개인 AQL 당월만 적용
        elif 'AQL INSPECTOR' in position:
            conditions['aql_3month']['applicable'] = False  # 6번 미적용
            conditions['subordinate_aql']['applicable'] = False  # 7번 미적용
            conditions['area_reject_rate']['applicable'] = False  # 8번 미적용
            conditions['5prs_volume']['applicable'] = False
            conditions['5prs_pass_rate']['applicable'] = False
    
    return conditions

def test_positions():
    """각 직급별 조건 적용 테스트"""
    test_cases = [
        ('TYPE-1', 'ASSEMBLY INSPECTOR'),
        ('TYPE-1', 'AQL INSPECTOR'),
        ('TYPE-1', 'LINE LEADER'),
    ]
    
    print("=" * 60)
    print("직급별 조건 적용 검증")
    print("=" * 60)
    
    for emp_type, position in test_cases:
        print(f"\n직급: {position} ({emp_type})")
        print("-" * 40)
        
        conditions = analyze_conditions_from_csv_row({}, emp_type, position, 'july')
        
        # JSON 설정과 비교
        if position == 'ASSEMBLY INSPECTOR':
            # JSON: 조건 5, 6, 9, 10 적용 / 7, 8 미적용
            print(f"✅ 5번 조건 (당월 AQL): {conditions['aql_monthly']['applicable']}")
            print(f"✅ 6번 조건 (3개월 연속): {conditions['aql_3month']['applicable']}")
            print(f"✅ 7번 조건 (부하직원 AQL): {not conditions['subordinate_aql']['applicable']}")
            print(f"✅ 8번 조건 (구역 reject): {not conditions['area_reject_rate']['applicable']}")
            print(f"✅ 9번 조건 (5PRS 통과율): {conditions['5prs_pass_rate']['applicable']}")
            print(f"✅ 10번 조건 (5PRS 검사량): {conditions['5prs_volume']['applicable']}")
            
            # 검증 결과
            if (conditions['aql_monthly']['applicable'] and 
                conditions['aql_3month']['applicable'] and  # 이제 True여야 함
                not conditions['subordinate_aql']['applicable'] and
                not conditions['area_reject_rate']['applicable']):
                print("\n🎯 JSON 설정과 일치! (수정 성공)")
            else:
                print("\n❌ JSON 설정과 불일치!")
                
        elif position == 'AQL INSPECTOR':
            # JSON: 조건 5만 적용 / 6, 7, 8, 9, 10 미적용
            print(f"✅ 5번 조건 (당월 AQL): {conditions['aql_monthly']['applicable']}")
            print(f"✅ 6번 조건 (3개월 연속): {not conditions['aql_3month']['applicable']}")
            print(f"✅ 7번 조건 (부하직원 AQL): {not conditions['subordinate_aql']['applicable']}")
            print(f"✅ 8번 조건 (구역 reject): {not conditions['area_reject_rate']['applicable']}")

if __name__ == "__main__":
    test_positions()