#!/usr/bin/env python3
"""
Comprehensive Automated Modal Test Suite
Tests all modal functionality without manual intervention
"""
import json
import re
import sys
from datetime import datetime

def automated_modal_test():
    """완전 자동화된 모달 기능 테스트"""

    print("="*70)
    print("🤖 완전 자동화 모달 테스트 시작")
    print("="*70)

    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"
    test_results = {
        'critical': {'passed': [], 'failed': []},
        'functional': {'passed': [], 'failed': []},
        'data': {'passed': [], 'failed': []},
        'ui': {'passed': [], 'failed': []}
    }

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ================== CRITICAL TESTS ==================
    print("\n[🚨 CRITICAL] Bootstrap JavaScript 로드 검증")
    print("-" * 50)

    # Test 1: Bootstrap JS CDN 포함 확인
    if 'bootstrap.bundle.min.js' in content:
        test_results['critical']['passed'].append("Bootstrap JS 포함")
        print("✅ Bootstrap JavaScript CDN 포함됨")

        # Bootstrap 버전 확인
        if 'bootstrap@5.1.3' in content:
            test_results['critical']['passed'].append("Bootstrap 5.1.3 버전")
            print("✅ Bootstrap 버전: 5.1.3 (정확)")
        else:
            test_results['critical']['failed'].append("Bootstrap 버전 불일치")
            print("⚠️ Bootstrap 버전이 5.1.3이 아님")
    else:
        test_results['critical']['failed'].append("Bootstrap JS 누락")
        print("❌ CRITICAL: Bootstrap JavaScript가 로드되지 않음!")

    # Test 2: 전역 모달 함수 존재
    if "window.showIncentiveModal = function" in content:
        test_results['critical']['passed'].append("전역 모달 함수")
        print("✅ window.showIncentiveModal 전역 함수 존재")
    else:
        test_results['critical']['failed'].append("전역 모달 함수 누락")
        print("❌ CRITICAL: 모달 함수가 전역에 없음!")

    # Test 3: Bootstrap Modal 초기화
    if "new bootstrap.Modal" in content:
        test_results['critical']['passed'].append("Bootstrap Modal 초기화")
        print("✅ Bootstrap Modal 초기화 코드 존재")
    else:
        test_results['critical']['failed'].append("Bootstrap Modal 초기화 누락")
        print("❌ CRITICAL: Bootstrap Modal 초기화 코드 없음!")

    # ================== FUNCTIONAL TESTS ==================
    print("\n[⚙️ FUNCTIONAL] 기능 구현 검증")
    print("-" * 50)

    # Test 4: 이벤트 위임 구현
    if "window.incentiveButtonHandler" in content:
        test_results['functional']['passed'].append("이벤트 위임 핸들러")
        print("✅ 이벤트 위임 핸들러 구현됨")
    else:
        test_results['functional']['failed'].append("이벤트 위임 미구현")
        print("❌ 이벤트 위임이 구현되지 않음")

    # Test 5: stopPropagation 구현
    if "stopPropagation()" in content and "stopImmediatePropagation()" in content:
        test_results['functional']['passed'].append("이벤트 전파 차단")
        print("✅ 이벤트 전파 차단 구현 (stopPropagation + stopImmediatePropagation)")
    else:
        test_results['functional']['failed'].append("이벤트 전파 차단 미구현")
        print("⚠️ 이벤트 전파 차단이 불완전함")

    # Test 6: 테스트 버튼 존재
    if 'id="testModalBtn"' in content:
        test_results['functional']['passed'].append("테스트 버튼")
        print("✅ 테스트 버튼 존재")
    else:
        test_results['functional']['failed'].append("테스트 버튼 누락")
        print("⚠️ 테스트 버튼이 없음")

    # Test 7: 정보 버튼 (ℹ️) 구현
    if 'class="incentive-detail-btn"' in content:
        test_results['functional']['passed'].append("인센티브 상세 버튼")
        print("✅ 인센티브 상세 버튼 (ℹ️) 구현됨")

        # span으로 구현되었는지 확인
        if '<span class="incentive-detail-btn"' in content:
            test_results['functional']['passed'].append("버튼을 span으로 구현")
            print("✅ 버튼이 span 요소로 구현됨 (충돌 방지)")
        else:
            test_results['functional']['failed'].append("버튼 요소 타입 문제")
            print("⚠️ 버튼이 span이 아닌 다른 요소로 구현됨")
    else:
        test_results['functional']['failed'].append("상세 버튼 누락")
        print("❌ 인센티브 상세 버튼이 없음")

    # ================== DATA TESTS ==================
    print("\n[📊 DATA] 데이터 및 통화 검증")
    print("-" * 50)

    # Test 8: 베트남 동 통화 기호
    vnd_count = content.count('₫')
    won_count = content.count('₩')

    if vnd_count > 0 and won_count == 0:
        test_results['data']['passed'].append(f"베트남 동 통화 ({vnd_count}개)")
        print(f"✅ 베트남 동(₫) 올바르게 사용: {vnd_count}개")
        print(f"✅ 원화(₩) 없음: 정확")
    else:
        test_results['data']['failed'].append(f"통화 오류 (₫:{vnd_count}, ₩:{won_count})")
        print(f"❌ 통화 문제: ₫={vnd_count}, ₩={won_count}")

    # Test 9: 부하직원 테이블 구조
    if '📋 인센티브 계산 기반 부하직원 상세' in content:
        test_results['data']['passed'].append("부하직원 상세 테이블")
        print("✅ 부하직원 상세 테이블 구조 존재")

        # 테이블 헤더 확인
        headers = ['이름', '직급', '인센티브', '수령 여부', '계산 기여']
        missing = []
        for header in headers:
            if f'<th>{header}</th>' not in content and f'>{header}<' not in content:
                missing.append(header)

        if not missing:
            test_results['data']['passed'].append("테이블 헤더 완전")
            print("✅ 모든 테이블 헤더 존재")
        else:
            test_results['data']['failed'].append(f"헤더 누락: {', '.join(missing)}")
            print(f"⚠️ 누락된 헤더: {', '.join(missing)}")
    else:
        test_results['data']['failed'].append("부하직원 테이블 없음")
        print("❌ 부하직원 상세 테이블이 없음")

    # Test 10: 직원 데이터 확인
    emp_data_match = re.search(r'const employeeData = (\[.*?\]);', content, re.DOTALL)
    if emp_data_match:
        try:
            data_str = emp_data_match.group(1)
            data_str = re.sub(r'\bNaN\b', 'null', data_str)
            employees = json.loads(data_str)

            test_results['data']['passed'].append(f"직원 데이터 ({len(employees)}명)")
            print(f"✅ 직원 데이터 로드 성공: {len(employees)}명")

            # LINE LEADER 확인
            line_leaders = [e for e in employees if e.get('type') == 'TYPE-1' and
                          'LEADER' in (e.get('position', '').upper())]
            if line_leaders:
                test_results['data']['passed'].append(f"LINE LEADER ({len(line_leaders)}명)")
                print(f"✅ TYPE-1 LINE LEADER: {len(line_leaders)}명")
            else:
                test_results['data']['failed'].append("LINE LEADER 없음")
                print("⚠️ LINE LEADER가 데이터에 없음")

        except Exception as e:
            test_results['data']['failed'].append(f"데이터 파싱 오류: {str(e)}")
            print(f"❌ 데이터 파싱 오류: {e}")
    else:
        test_results['data']['failed'].append("직원 데이터 없음")
        print("❌ 직원 데이터를 찾을 수 없음")

    # ================== UI TESTS ==================
    print("\n[🎨 UI] 사용자 인터페이스 검증")
    print("-" * 50)

    # Test 11: 디버깅 로그
    debug_logs = [
        "🔍 모달 함수 호출됨",
        "🖱️ 클릭 이벤트 발생",
        "ℹ️ 정보 버튼 클릭됨"
    ]

    debug_found = 0
    for log in debug_logs:
        if log in content:
            debug_found += 1

    if debug_found >= 2:
        test_results['ui']['passed'].append(f"디버깅 로그 ({debug_found}/3)")
        print(f"✅ 디버깅 로그 구현: {debug_found}/3")
    else:
        test_results['ui']['failed'].append(f"디버깅 로그 부족 ({debug_found}/3)")
        print(f"⚠️ 디버깅 로그 부족: {debug_found}/3")

    # Test 12: CSS 스타일링
    if 'cursor: pointer' in content and '.incentive-detail-btn' in content:
        test_results['ui']['passed'].append("포인터 커서 스타일")
        print("✅ 인센티브 버튼에 포인터 커서 적용")
    else:
        test_results['ui']['failed'].append("커서 스타일 누락")
        print("⚠️ 포인터 커서 스타일이 없음")

    # ================== FINAL REPORT ==================
    print("\n" + "="*70)
    print("📊 최종 테스트 결과")
    print("="*70)

    total_passed = 0
    total_failed = 0

    for category, results in test_results.items():
        passed = len(results['passed'])
        failed = len(results['failed'])
        total_passed += passed
        total_failed += failed

        if category == 'critical':
            emoji = "🚨"
            name = "핵심 기능"
        elif category == 'functional':
            emoji = "⚙️"
            name = "기능 구현"
        elif category == 'data':
            emoji = "📊"
            name = "데이터"
        else:
            emoji = "🎨"
            name = "UI/UX"

        print(f"\n{emoji} {name}: ✅ {passed} / ❌ {failed}")

        if results['failed']:
            print(f"   실패 항목:")
            for item in results['failed']:
                print(f"   - {item}")

    # 종합 점수
    total_tests = total_passed + total_failed
    if total_tests > 0:
        score = (total_passed / total_tests) * 100

        print(f"\n{'='*50}")
        print(f"종합 점수: {score:.1f}% ({total_passed}/{total_tests})")

        if score == 100:
            print("🎉 완벽! 모든 테스트를 통과했습니다!")
            verdict = "PERFECT"
        elif score >= 90:
            print("✅ 우수: 모달이 정상적으로 작동합니다.")
            verdict = "EXCELLENT"
        elif score >= 80:
            print("👍 양호: 대부분 기능이 작동하지만 일부 개선 필요.")
            verdict = "GOOD"
        elif score >= 70:
            print("⚠️ 주의: 중요한 기능이 누락되었습니다.")
            verdict = "WARNING"
        else:
            print("❌ 실패: 핵심 기능이 작동하지 않습니다.")
            verdict = "FAILED"

    # Critical 카테고리에 실패가 있으면 경고
    if test_results['critical']['failed']:
        print("\n" + "🚨"*20)
        print("CRITICAL 오류가 있습니다! Bootstrap이 제대로 로드되지 않았을 수 있습니다!")
        print("🚨"*20)
        verdict = "CRITICAL_FAILURE"

    print("\n" + "="*70)
    print(f"테스트 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # 결과를 JSON으로 저장
    with open('/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/modal_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'verdict': verdict,
            'score': score if 'score' in locals() else 0,
            'results': test_results,
            'summary': {
                'total_passed': total_passed,
                'total_failed': total_failed,
                'critical_failures': len(test_results['critical']['failed'])
            }
        }, f, ensure_ascii=False, indent=2)

    print("\n📁 테스트 결과가 modal_test_results.json에 저장되었습니다.")

    return verdict == "PERFECT" or verdict == "EXCELLENT"

if __name__ == "__main__":
    success = automated_modal_test()
    sys.exit(0 if success else 1)