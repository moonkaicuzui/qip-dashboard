#!/usr/bin/env python3
"""
자동 모달 기능 테스트 및 검증
"""
import re
import json

def auto_test_modal_functionality():
    """모달 기능 자동 테스트"""

    print("="*60)
    print("🤖 자동 모달 기능 테스트 시작")
    print("="*60)

    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"
    issues_found = []

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Test 1: window.showIncentiveModal 전역 함수 확인
    print("\n[TEST 1] 모달 함수 전역 스코프 확인")
    if "window.showIncentiveModal = function" in content:
        print("✅ window.showIncentiveModal 전역 함수 존재")
    else:
        print("❌ 모달 함수가 전역 스코프가 아님")
        issues_found.append("MODAL_NOT_GLOBAL")

    # Test 2: 테스트 버튼 존재 확인
    print("\n[TEST 2] 테스트 버튼 확인")
    if 'id="testModalBtn"' in content and 'onclick="testIncentiveModal()"' in content:
        print("✅ 테스트 버튼 존재")
    else:
        print("❌ 테스트 버튼 없음")
        issues_found.append("NO_TEST_BUTTON")

    # Test 3: 이벤트 위임 확인
    print("\n[TEST 3] 이벤트 위임 구현 확인")
    if "handleIncentiveClick" in content and "orgContainer.addEventListener('click', handleIncentiveClick)" in content:
        print("✅ 이벤트 위임 구현됨")
    else:
        print("❌ 이벤트 위임 미구현")
        issues_found.append("NO_EVENT_DELEGATION")

    # Test 4: 클릭 충돌 방지 확인
    print("\n[TEST 4] 클릭 충돌 방지 확인")
    if "if (e.target.closest('.node-incentive-info'))" in content:
        print("✅ 클릭 충돌 방지 코드 존재")
    else:
        print("❌ 클릭 충돌 방지 코드 없음")
        issues_found.append("NO_CLICK_CONFLICT_PREVENTION")

    # Test 5: 디버깅 로그 확인
    print("\n[TEST 5] 디버깅 로그 확인")
    debug_logs = [
        "🏗️ === 조직도 그리기 시작 ===",
        "📌 인센티브 클릭 이벤트 리스너 등록 중",
        "💰 인센티브 클릭 감지",
        "🔍 모달 함수 호출됨"
    ]

    missing_logs = []
    for log in debug_logs:
        if log in content:
            print(f"✅ 로그 존재: {log}")
        else:
            print(f"❌ 로그 없음: {log}")
            missing_logs.append(log)

    if missing_logs:
        issues_found.append("MISSING_DEBUG_LOGS")

    # Test 6: 통화 기호 확인
    print("\n[TEST 6] 베트남 동 통화 기호 확인")
    vnd_count = content.count('₫')
    won_count = content.count('₩')

    if vnd_count > 0 and won_count == 0:
        print(f"✅ 베트남 동(₫) 사용: {vnd_count}개")
    else:
        print(f"❌ 통화 기호 문제: ₫={vnd_count}, ₩={won_count}")
        issues_found.append("WRONG_CURRENCY")

    # Test 7: 부하직원 상세 테이블 확인
    print("\n[TEST 7] 부하직원 상세 테이블 확인")
    if '📋 인센티브 계산 기반 부하직원 상세' in content:
        print("✅ 부하직원 상세 테이블 존재")
    else:
        print("❌ 부하직원 상세 테이블 없음")
        issues_found.append("NO_SUBORDINATE_TABLE")

    # Test 8: 데이터 매핑 확인
    print("\n[TEST 8] 인센티브 데이터 동적 매핑 확인")
    if "dashboardMonth + '_incentive'" in content:
        print("✅ 동적 월 매핑 사용")
    else:
        print("❌ 하드코딩된 월 사용")
        issues_found.append("HARDCODED_MONTH")

    # Test 9: Bootstrap Modal 구조 확인
    print("\n[TEST 9] Bootstrap Modal 구조 확인")
    modal_elements = [
        'id="incentiveModal"',
        'class="modal fade"',
        'data-bs-dismiss="modal"',
        'new bootstrap.Modal'
    ]

    missing_modal_elements = []
    for element in modal_elements:
        if element in content:
            print(f"✅ Modal 요소 존재: {element[:30]}...")
        else:
            print(f"❌ Modal 요소 없음: {element}")
            missing_modal_elements.append(element)

    if missing_modal_elements:
        issues_found.append("INCOMPLETE_MODAL_STRUCTURE")

    # Test 10: 함수 접근성 확인
    print("\n[TEST 10] 함수 스코프 접근성 확인")

    # showIncentiveModal이 drawCollapsibleOrgChart 안에 있는지 확인
    pattern = r'function drawCollapsibleOrgChart.*?function showIncentiveModal'
    if re.search(pattern, content, re.DOTALL):
        print("❌ showIncentiveModal이 여전히 drawCollapsibleOrgChart 내부에 있음")
        issues_found.append("MODAL_FUNCTION_NESTED")
    else:
        print("✅ showIncentiveModal이 독립적으로 존재")

    return issues_found

def generate_fix_report(issues):
    """발견된 문제에 대한 수정 방안 생성"""

    fixes = {
        "MODAL_NOT_GLOBAL": {
            "issue": "모달 함수가 전역 스코프가 아님",
            "fix": "window.showIncentiveModal = function 으로 변경 필요"
        },
        "NO_TEST_BUTTON": {
            "issue": "테스트 버튼이 없음",
            "fix": "조직도 컨트롤에 테스트 버튼 추가 필요"
        },
        "NO_EVENT_DELEGATION": {
            "issue": "이벤트 위임이 구현되지 않음",
            "fix": "컨테이너에 이벤트 리스너 위임 구현 필요"
        },
        "NO_CLICK_CONFLICT_PREVENTION": {
            "issue": "클릭 충돌 방지 코드 없음",
            "fix": "node-incentive-info 클릭 시 이벤트 전파 중단 필요"
        },
        "MISSING_DEBUG_LOGS": {
            "issue": "디버깅 로그가 부족함",
            "fix": "각 단계별 console.log 추가 필요"
        },
        "WRONG_CURRENCY": {
            "issue": "잘못된 통화 기호 사용",
            "fix": "₩를 ₫로 모두 변경 필요"
        },
        "NO_SUBORDINATE_TABLE": {
            "issue": "부하직원 상세 테이블 없음",
            "fix": "모달에 부하직원 정보 테이블 추가 필요"
        },
        "HARDCODED_MONTH": {
            "issue": "월이 하드코딩되어 있음",
            "fix": "dashboardMonth 변수 사용하도록 수정 필요"
        },
        "INCOMPLETE_MODAL_STRUCTURE": {
            "issue": "Bootstrap 모달 구조 불완전",
            "fix": "완전한 Bootstrap 모달 HTML 구조 필요"
        },
        "MODAL_FUNCTION_NESTED": {
            "issue": "모달 함수가 다른 함수 내부에 중첩됨",
            "fix": "함수를 최상위 레벨로 이동 필요"
        }
    }

    print("\n" + "="*60)
    print("📋 문제 분석 및 수정 방안")
    print("="*60)

    if not issues:
        print("✅ 모든 테스트 통과! 문제 없음")
        return False

    print(f"\n발견된 문제: {len(issues)}개\n")
    for issue in issues:
        if issue in fixes:
            print(f"🔧 {fixes[issue]['issue']}")
            print(f"   → {fixes[issue]['fix']}\n")

    return True

def main():
    """메인 실행 함수"""
    # 테스트 실행
    issues = auto_test_modal_functionality()

    # 결과 분석 및 보고서 생성
    needs_fixing = generate_fix_report(issues)

    # 최종 결과
    print("="*60)
    if needs_fixing:
        print("⚠️ 수정이 필요한 문제들이 발견되었습니다.")
        print(f"   총 {len(issues)}개의 문제를 수정해야 합니다.")

        # 문제 목록 저장
        with open('/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/test_issues.json', 'w', encoding='utf-8') as f:
            json.dump(issues, f, ensure_ascii=False, indent=2)
        print("\n📁 문제 목록이 test_issues.json에 저장되었습니다.")
    else:
        print("✅ 모든 기능이 정상적으로 구현되었습니다!")
    print("="*60)

    return issues

if __name__ == "__main__":
    issues = main()
    # 문제가 있으면 exit code 1 반환
    exit(0 if not issues else 1)