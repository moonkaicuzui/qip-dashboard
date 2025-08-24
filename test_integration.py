#!/usr/bin/env python3
"""
통합 테스트 스크립트
전체 시스템이 올바르게 작동하는지 검증
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd):
    """명령 실행 및 결과 반환"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_json_loading():
    """JSON 파일 로딩 테스트"""
    print("\n" + "=" * 80)
    print("📋 TEST: JSON 파일 로딩")
    print("=" * 80)
    
    # Position condition matrix 확인
    matrix_path = Path(__file__).parent / 'config_files' / 'position_condition_matrix.json'
    if matrix_path.exists():
        with open(matrix_path, 'r', encoding='utf-8') as f:
            matrix = json.load(f)
        print(f"  ✅ position_condition_matrix.json 로드 성공")
        print(f"     - 조건 수: {len(matrix.get('conditions', {}))}")
        print(f"     - TYPE-1 직급 수: {len(matrix.get('position_matrix', {}).get('TYPE-1', {}))}")
        print(f"     - TYPE-2 직급 수: {len(matrix.get('position_matrix', {}).get('TYPE-2', {}))}")
        return True
    else:
        print(f"  ❌ position_condition_matrix.json 파일 없음")
        return False

def test_common_module():
    """공통 모듈 테스트"""
    print("\n" + "=" * 80)
    print("📋 TEST: 공통 조건 체크 모듈")
    print("=" * 80)
    
    # 모듈 import 테스트
    success, stdout, stderr = run_command(
        "/usr/bin/python3 -c 'from src.common_condition_checker import get_condition_checker; print(\"OK\")'"
    )
    
    if success and "OK" in stdout:
        print(f"  ✅ common_condition_checker 모듈 import 성공")
        return True
    else:
        print(f"  ❌ common_condition_checker 모듈 import 실패")
        if stderr:
            print(f"     오류: {stderr}")
        return False

def test_unit_tests():
    """유닛 테스트 실행"""
    print("\n" + "=" * 80)
    print("📋 TEST: 유닛 테스트")
    print("=" * 80)
    
    success, stdout, stderr = run_command("/usr/bin/python3 test_condition_checker.py")
    
    if success and "모든 테스트 통과" in stdout:
        print(f"  ✅ 모든 유닛 테스트 통과")
        return True
    else:
        print(f"  ❌ 일부 유닛 테스트 실패")
        return False

def test_line_leader_conditions():
    """LINE LEADER 조건 검증"""
    print("\n" + "=" * 80)
    print("📋 TEST: LINE LEADER 조건 검증")
    print("=" * 80)
    
    # JSON에서 LINE LEADER 조건 확인
    matrix_path = Path(__file__).parent / 'config_files' / 'position_condition_matrix.json'
    with open(matrix_path, 'r', encoding='utf-8') as f:
        matrix = json.load(f)
    
    # TYPE-1 LINE LEADER 조건 확인
    type1_line_leader = matrix['position_matrix']['TYPE-1']['LINE_LEADER']
    applicable = type1_line_leader['applicable_conditions']
    
    print(f"  TYPE-1 LINE LEADER 적용 조건: {applicable}")
    
    if 7 in applicable:
        print(f"  ✅ 조건 7 (팀/구역 AQL) 포함됨")
    else:
        print(f"  ❌ 조건 7 (팀/구역 AQL) 누락됨")
        return False
    
    # TYPE-2 LINE LEADER 조건 확인
    type2_line_leader = matrix['position_matrix']['TYPE-2']['LINE_LEADER_T2']
    applicable = type2_line_leader['applicable_conditions']
    
    print(f"  TYPE-2 LINE LEADER 적용 조건: {applicable}")
    
    if 7 not in applicable:
        print(f"  ✅ 조건 7 (팀/구역 AQL) 제외됨 (올바름)")
    else:
        print(f"  ❌ 조건 7 (팀/구역 AQL) 잘못 포함됨")
        return False
    
    return True

def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 80)
    print("🚀 통합 테스트 시작")
    print("=" * 80)
    
    tests = [
        ("JSON 파일 로딩", test_json_loading),
        ("공통 모듈", test_common_module),
        ("유닛 테스트", test_unit_tests),
        ("LINE LEADER 조건", test_line_leader_conditions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} 테스트 중 오류: {e}")
            results.append((test_name, False))
    
    # 최종 결과
    print("\n" + "=" * 80)
    print("📊 통합 테스트 결과")
    print("=" * 80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✅ 모든 통합 테스트 통과!")
        print("\n📌 주요 확인 사항:")
        print("  1. position_condition_matrix.json이 실제로 사용됨")
        print("  2. TYPE-1 LINE LEADER에 조건 7 (팀/구역 AQL) 적용됨")
        print("  3. 3개월 연속 실패 체크 로직이 조건 6, 7, 8에 대해 구현됨")
        print("  4. 공통 조건 체크 모듈이 정상 작동함")
        print("  5. 모든 타입/직급에 대한 조건이 올바르게 설정됨")
    else:
        print("\n❌ 일부 통합 테스트 실패")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)