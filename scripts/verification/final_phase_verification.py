#!/usr/bin/env python3
"""
최종 Phase 1, 2, 3 검증 스크립트
HTML 소스 정적 검증 + Playwright 동적 검증
"""

from playwright.sync_api import sync_playwright
import time
import os

def verify_html_source():
    """HTML 소스에서 Phase 2, 3 코드 존재 확인"""
    print("\n" + "=" * 80)
    print("📄 HTML 소스 정적 검증")
    print("=" * 80)

    html_path = "output_files/Incentive_Dashboard_2025_09_Version_6.html"

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    results = {
        # Phase 3: 리팩토링
        'Phase 3 - POSITION_CONFIG 객체': 'const POSITION_CONFIG = {' in html_content,
        'Phase 3 - getPositionConfig()': 'function getPositionConfig(position) {' in html_content,
        'Phase 3 - calculateExpectedIncentive()': 'function calculateExpectedIncentive(subordinates, config) {' in html_content,
        'Phase 3 - generateSubordinateTable()': 'function generateSubordinateTable(' in html_content,
        'Phase 3 - generateCalculationDetails()': 'function generateCalculationDetails(' in html_content,
        'Phase 3 - useAlternatingColors 설정': 'useAlternatingColors: true' in html_content,

        # Phase 2: 알림 박스
        'Phase 2 - 빨간색 알림 (alert-danger)': 'alert alert-danger' in html_content,
        'Phase 2 - 노란색 알림 (alert-warning)': 'alert alert-warning' in html_content,
        'Phase 2 - 미지급 사유 제목': 'orgChart.modal.alerts.nonPaymentTitle' in html_content,
        'Phase 2 - 차이 안내 제목': 'orgChart.modal.alerts.differenceTitle' in html_content,

        # Phase 1: 번역 키
        'Phase 1 - expectedIncentive 번역 키': 'orgChart.modal.labels.expectedIncentive' in html_content,
        'Phase 1 - actualIncentive 번역 키': 'orgChart.modal.labels.actualIncentive' in html_content,
    }

    passed = 0
    failed = 0

    for check_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 80}")
    print(f"HTML 소스 검증 결과: {passed}/{len(results)} 통과 ({passed/len(results)*100:.1f}%)")
    print(f"{'=' * 80}")

    return results, passed, failed


def verify_with_playwright():
    """Playwright로 Phase 1 시각적 요소 확인"""
    print("\n" + "=" * 80)
    print("🎭 Playwright 동적 검증")
    print("=" * 80)

    dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

    results = {}
    passed = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        try:
            print(f"\n📂 대시보드 열기: {dashboard_path}")
            page.goto(dashboard_path)
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            print("✅ 대시보드 로드 완료")

            # Org Chart 탭 클릭
            print("\n📊 Org Chart 탭 클릭...")
            try:
                page.click("#tabOrgChart")
                time.sleep(3)
                print("✅ Org Chart 탭 열림")

                # 스크린샷 저장
                page.screenshot(path="output_files/phase_verification_orgchart_tab.png")
                print("📸 스크린샷 저장: phase_verification_orgchart_tab.png")

            except Exception as e:
                print(f"❌ Org Chart 탭 열기 실패: {e}")
                results['Org Chart 탭 열기'] = False
                failed += 1
                browser.close()
                return results, passed, failed

            # showIncentiveModal 함수 존재 확인
            print("\n⏳ showIncentiveModal 함수 로드 대기...")
            try:
                page.wait_for_function(
                    "typeof window.showIncentiveModal === 'function'",
                    timeout=15000
                )
                print("✅ showIncentiveModal 함수 로드됨")
                results['showIncentiveModal 함수 존재'] = True
                passed += 1
            except Exception as e:
                print(f"❌ showIncentiveModal 함수 로드 실패: {e}")
                results['showIncentiveModal 함수 존재'] = False
                failed += 1
                browser.close()
                return results, passed, failed

            # SUPERVISOR (822000065) modal 열기
            print("\n🔍 SUPERVISOR (822000065) modal 열기...")
            try:
                page.evaluate("showIncentiveModal('822000065')")
                time.sleep(2)

                # Modal 표시 대기
                modal = page.wait_for_selector(".modal.show", state="visible", timeout=10000)
                if modal:
                    print("✅ SUPERVISOR modal 열림")
                    results['SUPERVISOR modal 열기'] = True
                    passed += 1

                    # 스크린샷 저장
                    page.screenshot(path="output_files/phase_verification_supervisor_modal.png", full_page=True)
                    print("📸 스크린샷 저장: phase_verification_supervisor_modal.png")
                else:
                    print("❌ Modal이 표시되지 않음")
                    results['SUPERVISOR modal 열기'] = False
                    failed += 1
                    browser.close()
                    return results, passed, failed

            except Exception as e:
                print(f"❌ Modal 열기 실패: {e}")
                results['SUPERVISOR modal 열기'] = False
                failed += 1
                browser.close()
                return results, passed, failed

            # Phase 1 검증: 번역 키
            print("\n🔤 Phase 1 - 번역 키 확인...")
            try:
                modal_body = page.locator(".modal-body")
                modal_text = modal_body.inner_text()

                has_expected = "예상 인센티브" in modal_text
                has_actual = "실제 인센티브" in modal_text

                if has_expected:
                    print("✅ '예상 인센티브' 텍스트 발견")
                    results['Phase 1 - 예상 인센티브 텍스트'] = True
                    passed += 1
                else:
                    print("❌ '예상 인센티브' 텍스트 없음")
                    results['Phase 1 - 예상 인센티브 텍스트'] = False
                    failed += 1

                if has_actual:
                    print("✅ '실제 인센티브' 텍스트 발견")
                    results['Phase 1 - 실제 인센티브 텍스트'] = True
                    passed += 1
                else:
                    print("❌ '실제 인센티브' 텍스트 없음")
                    results['Phase 1 - 실제 인센티브 텍스트'] = False
                    failed += 1

            except Exception as e:
                print(f"❌ 번역 키 확인 실패: {e}")
                results['Phase 1 - 예상 인센티브 텍스트'] = False
                results['Phase 1 - 실제 인센티브 텍스트'] = False
                failed += 2

            # Phase 1 검증: 배경색 교대
            print("\n🎨 Phase 1 - 배경색 교대 확인...")
            try:
                table_light_rows = page.locator(".modal-body table tbody tr.table-light")
                count = table_light_rows.count()

                if count > 0:
                    print(f"✅ table-light 클래스 발견: {count}개 행")
                    results['Phase 1 - 배경색 교대 (table-light)'] = True
                    passed += 1
                else:
                    print("❌ table-light 클래스 없음 (배경색 교대 미적용)")
                    results['Phase 1 - 배경색 교대 (table-light)'] = False
                    failed += 1

            except Exception as e:
                print(f"❌ 배경색 교대 확인 실패: {e}")
                results['Phase 1 - 배경색 교대 (table-light)'] = False
                failed += 1

            # 최종 스크린샷
            print("\n📸 최종 스크린샷 저장...")
            page.screenshot(path="output_files/phase_verification_final.png", full_page=True)

        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")

        finally:
            browser.close()

    print(f"\n{'=' * 80}")
    print(f"Playwright 검증 결과: {passed}/{passed+failed} 통과 ({passed/(passed+failed)*100:.1f}%)")
    print(f"{'=' * 80}")

    return results, passed, failed


def main():
    print("\n" + "=" * 80)
    print("🔍 Phase 1 + 2 + 3 최종 검증")
    print("=" * 80)
    print("\n📋 검증 계획:")
    print("  1. HTML 소스 정적 검증 (Phase 2, 3 코드 존재)")
    print("  2. Playwright 동적 검증 (Phase 1 시각적 요소)")
    print()

    # 1. HTML 소스 검증
    html_results, html_passed, html_failed = verify_html_source()

    # 2. Playwright 검증
    pw_results, pw_passed, pw_failed = verify_with_playwright()

    # 최종 요약
    total_passed = html_passed + pw_passed
    total_failed = html_failed + pw_failed
    total_tests = total_passed + total_failed

    print("\n" + "=" * 80)
    print("📊 최종 검증 요약")
    print("=" * 80)

    print(f"\n✅ Phase 1 (번역 & 테이블):")
    print(f"   - 번역 키 통일: {'✅' if html_results.get('Phase 1 - expectedIncentive 번역 키') else '❌'}")
    print(f"   - 예상 인센티브 텍스트: {'✅' if pw_results.get('Phase 1 - 예상 인센티브 텍스트') else '❌'}")
    print(f"   - 실제 인센티브 텍스트: {'✅' if pw_results.get('Phase 1 - 실제 인센티브 텍스트') else '❌'}")
    print(f"   - 배경색 교대: {'✅' if pw_results.get('Phase 1 - 배경색 교대 (table-light)') else '❌'}")

    print(f"\n✅ Phase 2 (알림 박스):")
    print(f"   - 빨간색 알림 코드: {'✅' if html_results.get('Phase 2 - 빨간색 알림 (alert-danger)') else '❌'}")
    print(f"   - 노란색 알림 코드: {'✅' if html_results.get('Phase 2 - 노란색 알림 (alert-warning)') else '❌'}")
    print(f"   - 미지급 사유 제목: {'✅' if html_results.get('Phase 2 - 미지급 사유 제목') else '❌'}")
    print(f"   - 차이 안내 제목: {'✅' if html_results.get('Phase 2 - 차이 안내 제목') else '❌'}")

    print(f"\n✅ Phase 3 (리팩토링):")
    print(f"   - POSITION_CONFIG: {'✅' if html_results.get('Phase 3 - POSITION_CONFIG 객체') else '❌'}")
    print(f"   - Helper 함수 4개: {'✅' if all([html_results.get(f'Phase 3 - {func}') for func in ['getPositionConfig()', 'calculateExpectedIncentive()', 'generateSubordinateTable()', 'generateCalculationDetails()']]) else '❌'}")
    print(f"   - useAlternatingColors 설정: {'✅' if html_results.get('Phase 3 - useAlternatingColors 설정') else '❌'}")

    print(f"\n{'=' * 80}")
    print(f"🎯 전체 결과: {total_passed}/{total_tests} 테스트 통과 ({total_passed/total_tests*100:.1f}%)")
    print(f"{'=' * 80}")

    if total_passed == total_tests:
        print("\n🎉 ✅ 모든 검증 통과! Phase 1, 2, 3 개선사항이 성공적으로 적용되었습니다.")
        return True
    else:
        print(f"\n⚠️  {total_failed}개 테스트 실패. 위 내용을 확인하세요.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)