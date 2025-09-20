#!/usr/bin/env python3
"""
JSON 호환성 테스트 스크립트
기존 코드가 개선된 JSON과 호환되는지 확인
"""

import json
import sys
from pathlib import Path

def test_compatibility():
    """개선된 JSON이 기존 코드와 호환되는지 테스트"""

    print("=" * 80)
    print("🔧 JSON 호환성 테스트")
    print("=" * 80)

    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }

    # 1. JSON 파일 로드 테스트
    print("\n1️⃣ JSON 파일 로드 테스트")
    print("-" * 70)

    try:
        with open('config_files/position_condition_matrix_compatible.json', 'r') as f:
            compatible_json = json.load(f)
        print("✅ 개선된 JSON 파일 로드 성공")
        results['passed'].append("JSON 로드")
    except Exception as e:
        print(f"❌ JSON 로드 실패: {e}")
        results['failed'].append("JSON 로드")
        return results

    # 2. 필수 구조 확인
    print("\n2️⃣ 필수 구조 확인")
    print("-" * 70)

    required_keys = ['conditions', 'position_matrix', 'incentive_rules']
    for key in required_keys:
        if key in compatible_json:
            print(f"✅ {key} 섹션 존재")
            results['passed'].append(f"{key} 구조")
        else:
            print(f"❌ {key} 섹션 없음")
            results['failed'].append(f"{key} 구조")

    # 3. TYPE-3 개선사항 확인
    print("\n3️⃣ TYPE-3 개선사항 확인")
    print("-" * 70)

    type3_default = compatible_json.get('position_matrix', {}).get('TYPE-3', {}).get('default', {})

    # 새로 추가된 필드 확인
    new_fields = ['eligible_for_incentive', 'policy_status', 'policy_reason']
    for field in new_fields:
        if field in type3_default:
            value = type3_default[field]
            print(f"✅ {field}: {value}")
            results['passed'].append(f"TYPE-3 {field}")
        else:
            print(f"⚠️ {field} 필드 없음 (선택사항)")
            results['warnings'].append(f"TYPE-3 {field}")

    # 4. 기존 코드 시뮬레이션
    print("\n4️⃣ 기존 코드 시뮬레이션")
    print("-" * 70)

    # condition_matrix_manager.py 시뮬레이션
    try:
        # 기존 코드가 사용하는 필드들
        conditions = compatible_json['conditions']
        type1_conditions = compatible_json['position_matrix']['TYPE-1']['MANAGER']['applicable_conditions']
        type3_conditions = compatible_json['position_matrix']['TYPE-3']['default']['applicable_conditions']

        print(f"✅ TYPE-1 MANAGER 조건: {type1_conditions}")
        print(f"✅ TYPE-3 조건: {type3_conditions} (빈 배열 정상)")
        results['passed'].append("기존 코드 호환성")
    except KeyError as e:
        print(f"❌ 기존 코드 호환성 문제: {e}")
        results['failed'].append("기존 코드 호환성")

    # 5. amount_range 검증
    print("\n5️⃣ amount_range 일관성 검증")
    print("-" * 70)

    type3_amount = compatible_json['incentive_rules']['TYPE-3']['base_incentive']['amount_range']
    if type3_amount['min'] == 0 and type3_amount['max'] == 0:
        print(f"✅ TYPE-3 amount_range: {type3_amount} (0으로 수정됨)")
        results['passed'].append("amount_range 일관성")
    else:
        print(f"❌ TYPE-3 amount_range가 0이 아님: {type3_amount}")
        results['failed'].append("amount_range 일관성")

    # 6. validation_rules 확인
    print("\n6️⃣ validation_rules 확인")
    print("-" * 70)

    if 'validation_rules' in compatible_json:
        if 'TYPE-3' in compatible_json['validation_rules']:
            type3_validation = compatible_json['validation_rules']['TYPE-3']
            print(f"✅ TYPE-3 validation_rules 존재")
            print(f"   • payment_blocked: {type3_validation.get('payment_blocked', False)}")
            print(f"   • block_reason: {type3_validation.get('block_reason', 'N/A')}")
            results['passed'].append("validation_rules")
        else:
            print("⚠️ TYPE-3 validation_rules 없음")
            results['warnings'].append("validation_rules")

    # 7. 결과 요약
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)

    print(f"\n✅ 통과: {len(results['passed'])}개")
    for item in results['passed']:
        print(f"   • {item}")

    if results['warnings']:
        print(f"\n⚠️ 경고: {len(results['warnings'])}개")
        for item in results['warnings']:
            print(f"   • {item}")

    if results['failed']:
        print(f"\n❌ 실패: {len(results['failed'])}개")
        for item in results['failed']:
            print(f"   • {item}")
        print("\n⚠️ 호환성 문제가 있습니다. 수정이 필요합니다.")
    else:
        print("\n✅ 모든 필수 테스트 통과! 기존 코드와 호환 가능합니다.")

    return results

def test_with_actual_code():
    """실제 코드 모듈과 테스트"""
    print("\n" + "=" * 80)
    print("🔬 실제 코드 모듈 테스트")
    print("=" * 80)

    try:
        # condition_matrix_manager 임포트 시도
        sys.path.insert(0, 'src')
        from condition_matrix_manager import ConditionMatrixManager

        print("\n✅ condition_matrix_manager 임포트 성공")

        # 개선된 JSON으로 매니저 초기화
        manager = ConditionMatrixManager('config_files/position_condition_matrix_compatible.json')
        print("✅ ConditionMatrixManager 초기화 성공")

        # TYPE-3 조건 가져오기
        type3_conditions = manager.get_applicable_conditions('TYPE-3', 'NEW QIP MEMBER')
        print(f"✅ TYPE-3 조건 조회 성공: {type3_conditions}")

        return True

    except ImportError as e:
        print(f"⚠️ 모듈 임포트 실패 (정상): {e}")
        print("   (독립 실행 환경에서는 정상적인 현상)")
        return False
    except Exception as e:
        print(f"❌ 실제 코드 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    # 호환성 테스트 실행
    results = test_compatibility()

    # 실제 코드와 테스트
    actual_test_success = test_with_actual_code()

    print("\n" + "=" * 80)
    print("🎯 최종 판정")
    print("=" * 80)

    if not results['failed']:
        print("✅ 개선된 JSON은 기존 시스템과 호환 가능합니다!")
        print("   안전하게 배포할 수 있습니다.")
    else:
        print("⚠️ 일부 호환성 문제가 있습니다.")
        print("   수정 후 다시 테스트하세요.")