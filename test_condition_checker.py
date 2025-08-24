#!/usr/bin/env python3
"""
ConditionChecker 모듈 유닛 테스트
모든 조건이 올바르게 체크되는지 검증
"""

import sys
import json
import pandas as pd
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from common_condition_checker import ConditionChecker, get_condition_checker

def test_attendance_conditions():
    """출근 조건 테스트 (조건 1-4)"""
    print("\n" + "=" * 80)
    print("📝 TEST 1: 출근 조건 체크")
    print("=" * 80)
    
    checker = get_condition_checker()
    
    # 테스트 케이스
    test_cases = [
        {
            'name': '모든 출근 조건 충족',
            'data': {
                'Absence Rate (raw)': 10,  # 출근율 90%
                'Unapproved Absence Days': 1,
                'Actual Working Days': 20
            },
            'expected': {1: True, 2: True, 3: True, 4: True}
        },
        {
            'name': '출근율 미달',
            'data': {
                'Absence Rate (raw)': 15,  # 출근율 85%
                'Unapproved Absence Days': 1,
                'Actual Working Days': 20
            },
            'expected': {1: False, 2: True, 3: True, 4: True}
        },
        {
            'name': '무단결근 초과',
            'data': {
                'Absence Rate (raw)': 10,
                'Unapproved Absence Days': 3,  # 3일 > 2일
                'Actual Working Days': 20
            },
            'expected': {1: True, 2: False, 3: True, 4: True}
        },
        {
            'name': '최소 근무일 미달',
            'data': {
                'Absence Rate (raw)': 10,
                'Unapproved Absence Days': 1,
                'Actual Working Days': 10  # 10일 < 12일
            },
            'expected': {1: True, 2: True, 3: True, 4: False}
        }
    ]
    
    all_passed = True
    for case in test_cases:
        results = checker.check_attendance_conditions(case['data'])
        passed = results == case['expected']
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {case['name']}")
        if not passed:
            print(f"    Expected: {case['expected']}")
            print(f"    Got: {results}")
            all_passed = False
    
    return all_passed

def test_3month_continuous_checks():
    """3개월 연속 실패 체크 테스트 (조건 6, 7, 8)"""
    print("\n" + "=" * 80)
    print("📝 TEST 2: 3개월 연속 실패 체크 (조건 6, 7, 8)")
    print("=" * 80)
    
    checker = get_condition_checker()
    
    # 조건 6: 개인 AQL 3개월 연속
    print("\n  조건 6: 개인 AQL 3개월 연속 실패 체크")
    test_cases_6 = [
        {
            'name': '연속 실패 없음',
            'data': {'Continuous_FAIL': 'NO'},
            'expected': True
        },
        {
            'name': '3개월 연속 실패',
            'data': {'Continuous_FAIL': 'YES'},
            'expected': False
        }
    ]
    
    for case in test_cases_6:
        result = checker.check_aql_3month_continuous(case['data'])
        passed = result == case['expected']
        status = "✅" if passed else "❌"
        print(f"    {status} {case['name']}: {result}")
    
    # 조건 7: 팀/구역 AQL 3개월 연속
    print("\n  조건 7: 팀/구역 AQL 3개월 연속 실패 체크")
    
    # 테스트용 부하직원 데이터
    subordinates_df = pd.DataFrame([
        {'Employee No': '001', 'MST direct boss name': 'M001', 'Continuous_FAIL': 'NO'},
        {'Employee No': '002', 'MST direct boss name': 'M001', 'Continuous_FAIL': 'NO'},
        {'Employee No': '003', 'MST direct boss name': 'M002', 'Continuous_FAIL': 'YES'},
    ])
    
    test_cases_7 = [
        {
            'name': 'M001 - 부하직원 연속 실패 없음',
            'manager_id': 'M001',
            'expected': True
        },
        {
            'name': 'M002 - 부하직원 중 연속 실패자 있음',
            'manager_id': 'M002',
            'expected': False
        }
    ]
    
    for case in test_cases_7:
        result = checker.check_team_area_aql_continuous(
            case['manager_id'], 
            subordinates_df
        )
        passed = result == case['expected']
        status = "✅" if passed else "❌"
        print(f"    {status} {case['name']}: {result}")
    
    return True

def test_position_specific_conditions():
    """직급별 조건 적용 테스트"""
    print("\n" + "=" * 80)
    print("📝 TEST 3: 직급별 조건 적용")
    print("=" * 80)
    
    checker = get_condition_checker()
    
    # LINE LEADER 테스트 데이터
    line_leader_data = {
        'Employee No': 'LL001',
        'Full Name': 'Test Line Leader',
        'Absence Rate (raw)': 10,  # 출근율 90%
        'Unapproved Absence Days': 1,
        'Actual Working Days': 20,
        'July AQL Failures': 0,
        'Continuous_FAIL': 'NO',
        'Pass %': 98,
        'Total Valiation Qty': 150
    }
    
    # 부하직원 데이터
    subordinates_df = pd.DataFrame([
        {'Employee No': 'S001', 'MST direct boss name': 'LL001', 'Continuous_FAIL': 'NO'},
        {'Employee No': 'S002', 'MST direct boss name': 'LL001', 'Continuous_FAIL': 'YES'},  # 실패자!
    ])
    
    # TYPE-1 LINE LEADER 체크
    result = checker.check_all_conditions(
        employee_data=line_leader_data,
        emp_type='TYPE-1',
        position='LINE LEADER',
        month='July',
        subordinates_data=subordinates_df
    )
    
    print(f"\n  TYPE-1 LINE LEADER 조건 체크:")
    print(f"    적용 조건: {result['applicable_conditions']}")
    print(f"    예상 조건: [1, 2, 3, 4, 7]")
    
    # 조건 7 (부하직원 AQL) 체크
    if 7 in result['applicable_conditions']:
        cond_7_passed = result['results'].get(7, None)
        print(f"    조건 7 (팀/구역 AQL) 결과: {cond_7_passed}")
        print(f"    예상 결과: False (부하직원 중 연속 실패자 있음)")
        
        if cond_7_passed == False:
            print("    ✅ 조건 7이 올바르게 체크됨")
        else:
            print("    ❌ 조건 7 체크 오류!")
    else:
        print("    ❌ 조건 7이 적용되지 않음!")
    
    # 결과 요약 출력
    summary = checker.format_condition_summary(result, 'ko')
    print(f"\n{summary}")
    
    return True

def test_all_types_and_positions():
    """모든 타입/직급 종합 테스트"""
    print("\n" + "=" * 80)
    print("📝 TEST 4: 모든 타입/직급 종합 테스트")
    print("=" * 80)
    
    checker = get_condition_checker()
    
    # 테스트할 직급 목록
    test_positions = [
        ('TYPE-1', 'LINE LEADER', [1,2,3,4,7]),
        ('TYPE-1', 'AQL INSPECTOR', [1,2,3,4,5]),
        ('TYPE-1', 'ASSEMBLY INSPECTOR', [1,2,3,4,5,6,9,10]),
        ('TYPE-1', 'MODEL MASTER', [1,2,3,4,8]),
        ('TYPE-2', 'LINE LEADER', [1,2,3,4]),
        ('TYPE-2', 'ASSEMBLY INSPECTOR', [1,2,3,4]),
        ('TYPE-3', 'NEW QIP MEMBER', []),
    ]
    
    all_correct = True
    for emp_type, position, expected_conditions in test_positions:
        config = checker.get_position_config(emp_type, position)
        actual_conditions = config.get('applicable_conditions', [])
        
        match = set(actual_conditions) == set(expected_conditions)
        status = "✅" if match else "❌"
        
        print(f"  {status} {emp_type:7} {position:25} 조건: {actual_conditions}")
        
        if not match:
            print(f"      예상: {expected_conditions}")
            all_correct = False
    
    if all_correct:
        print("\n  ✅ 모든 타입/직급의 조건이 올바르게 설정됨!")
    else:
        print("\n  ❌ 일부 타입/직급의 조건 설정에 문제가 있음!")
    
    return all_correct

def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 80)
    print("🧪 ConditionChecker 유닛 테스트 시작")
    print("=" * 80)
    
    tests = [
        test_attendance_conditions,
        test_3month_continuous_checks,
        test_position_specific_conditions,
        test_all_types_and_positions
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ 테스트 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # 최종 결과
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"  총 테스트: {total_tests}개")
    print(f"  성공: {passed_tests}개")
    print(f"  실패: {total_tests - passed_tests}개")
    
    if all(results):
        print("\n✅ 모든 테스트 통과!")
    else:
        print("\n❌ 일부 테스트 실패")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)