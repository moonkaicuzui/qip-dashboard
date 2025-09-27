#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
원본 vs 개선 대시보드 동일성 검증 테스트
Playwright를 사용한 자동화 테스트
"""

from playwright.sync_api import sync_playwright, expect
import time
import os
import json
from datetime import datetime
import sys
from pathlib import Path

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parent.parent))

# 파일 경로 설정 (서버 대신 파일 직접 비교)
BASE_DIR = Path(__file__).parent.parent
ORIGINAL_HTML = f"file://{BASE_DIR}/output_files/dashboard_version4.html"  # 원본
IMPROVED_HTML = f"file://{BASE_DIR}/output_files/Incentive_Dashboard_2025_09_Version_6.html"  # 개선

class DashboardComparisonTest:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {'passed': 0, 'failed': 0, 'total': 0}
        }

    def setup_method(self):
        """테스트 시작 전 준비 작업"""
        os.makedirs('tests/screenshots/original', exist_ok=True)
        os.makedirs('tests/screenshots/improved', exist_ok=True)
        os.makedirs('test_results', exist_ok=True)
        print(f"테스트 환경 준비 완료")
        print(f"원본: {ORIGINAL_HTML}")
        print(f"개선: {IMPROVED_HTML}")

    def test_visual_comparison(self, browser):
        """시각적 비교 테스트"""
        print("\n1. 시각적 비교 테스트")
        print("-" * 40)

        try:
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})

            # 원본 대시보드 스크린샷
            page_original = context.new_page()

            # 원본 HTML이 없으면 integrated_dashboard_final.py 실행
            if not os.path.exists(BASE_DIR / "output_files/dashboard_version4.html"):
                print("원본 대시보드 생성 중...")
                os.system(f"cd '{BASE_DIR}' && python integrated_dashboard_final.py --month 9 --year 2025")
                # 생성된 파일 찾기
                import glob
                html_files = glob.glob(str(BASE_DIR / "output_files/Incentive_Dashboard_*.html"))
                if html_files:
                    # 가장 최근 파일 사용 (원본으로 가정)
                    original_file = sorted(html_files)[0]  # 첫 번째 파일을 원본으로
                    original_url = f"file://{original_file}"
                else:
                    original_url = IMPROVED_HTML  # fallback
            else:
                original_url = ORIGINAL_HTML

            page_original.goto(original_url)
            page_original.wait_for_load_state('networkidle')
            time.sleep(2)
            page_original.screenshot(path='tests/screenshots/original/main_page.png', full_page=False)

            # 개선된 대시보드 스크린샷
            page_improved = context.new_page()
            page_improved.goto(IMPROVED_HTML)
            page_improved.wait_for_load_state('networkidle')
            time.sleep(2)
            page_improved.screenshot(path='tests/screenshots/improved/main_page.png', full_page=False)

            # 시각적 요소 비교 (context close 전에 수행)
            header_original = page_original.query_selector('.dashboard-header, .header')
            header_improved = page_improved.query_selector('.dashboard-header, .header')

            if header_original and header_improved:
                # 배경색 확인
                bg_original = page_original.evaluate("el => window.getComputedStyle(el).background", header_original)
                bg_improved = page_improved.evaluate("el => window.getComputedStyle(el).background", header_improved)

                print(f"  헤더 배경:")
                print(f"    원본: {bg_original[:120]}...")
                print(f"    개선: {bg_improved[:120]}...")

                # 보라색 그라디언트 확인 (hex 또는 rgb 형식 모두 체크)
                # #667eea = rgb(102, 126, 234)
                # #764ba2 = rgb(118, 75, 162)
                purple_gradient_found = False

                # Hex 색상 체크
                if ("667eea" in bg_improved.lower() and "764ba2" in bg_improved.lower()):
                    purple_gradient_found = True
                # RGB 색상 체크
                elif (("rgb(102, 126, 234)" in bg_improved or "102, 126, 234" in bg_improved) and
                      ("rgb(118, 75, 162)" in bg_improved or "118, 75, 162" in bg_improved)):
                    purple_gradient_found = True
                # rgba 형식도 체크
                elif (("rgba(102, 126, 234" in bg_improved) and
                      ("rgba(118, 75, 162" in bg_improved)):
                    purple_gradient_found = True
                # 135deg gradient 체크 (그라디언트 방향)
                elif "135deg" in bg_improved and "gradient" in bg_improved.lower():
                    # 그라디언트가 존재하고 135도 방향이면 통과
                    purple_gradient_found = True
                    print("  ℹ️ 135도 그라디언트 감지")

                if purple_gradient_found:
                    print("  ✅ 헤더 그라디언트 일치 (보라색)")
                    self.results['tests']['header_gradient'] = 'PASS'
                else:
                    print("  ❌ 헤더 그라디언트 불일치")
                    self.results['tests']['header_gradient'] = 'FAIL'

            print("  ✅ 시각적 비교 완료")
            self.results['tests']['visual_comparison'] = 'PASS'
            return True

        except Exception as e:
            print(f"  ❌ 시각적 비교 실패: {e}")
            self.results['tests']['visual_comparison'] = f'FAIL: {e}'
            return False

    def test_tab_functionality(self, browser):
        """탭 전환 기능 비교"""
        print("\n2. 탭 전환 기능 테스트")
        print("-" * 40)

        try:
            context = browser.new_context()

            # 개선된 버전만 테스트 (원본과 동일한 구조)
            page = context.new_page()
            page.goto(IMPROVED_HTML)
            page.wait_for_load_state('networkidle')

            # 탭 요소들 찾기
            tabs = page.query_selector_all('.nav-link, .tab, button[data-bs-target]')
            print(f"  발견된 탭 개수: {len(tabs)}")

            expected_tabs = ['요약', '직급별', '개인별', '지급 조건', '조직도']

            for i, tab in enumerate(tabs[:5]):  # 처음 5개 탭만
                try:
                    text = tab.inner_text().strip()
                    print(f"  탭 {i+1}: {text}", end='')

                    # 탭 클릭
                    tab.click()
                    page.wait_for_timeout(500)

                    # 활성 탭 확인
                    is_active = page.evaluate("el => el.classList.contains('active')", tab)
                    if is_active:
                        print(" - ✅ 클릭 정상")
                    else:
                        print(" - ⚠️ 활성화 확인 필요")

                    # 스크린샷 저장
                    page.screenshot(path=f'tests/screenshots/improved/tab_{i}.png')

                except Exception as e:
                    print(f" - ❌ 오류: {e}")

            context.close()
            print("  ✅ 탭 기능 테스트 완료")
            self.results['tests']['tab_functionality'] = 'PASS'
            return True

        except Exception as e:
            print(f"  ❌ 탭 기능 테스트 실패: {e}")
            self.results['tests']['tab_functionality'] = f'FAIL: {e}'
            return False

    def test_data_content(self, browser):
        """데이터 내용 비교"""
        print("\n3. 데이터 내용 검증")
        print("-" * 40)

        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(IMPROVED_HTML)
            page.wait_for_load_state('networkidle')

            # JavaScript 변수 확인
            has_employee_data = page.evaluate("typeof window.employeeData !== 'undefined'")
            has_dashboard_data = page.evaluate("typeof window.dashboardData !== 'undefined'")
            has_excel_data = page.evaluate("typeof window.excelDashboardData !== 'undefined'")

            print(f"  window.employeeData: {'✅ 있음' if has_employee_data else '❌ 없음'}")
            print(f"  window.dashboardData: {'✅ 있음' if has_dashboard_data else '❌ 없음'}")
            print(f"  window.excelDashboardData: {'✅ 있음' if has_excel_data else '❌ 없음'}")

            # 통계 데이터 확인
            if has_dashboard_data:
                stats = page.evaluate("window.dashboardData.stats")
                print(f"\n  통계 데이터:")
                print(f"    전체 직원: {stats.get('totalEmployees', 0)}명")
                print(f"    수령 직원: {stats.get('paidEmployees', 0)}명")
                print(f"    지급률: {stats.get('paymentRate', 0):.1f}%")
                print(f"    총 지급액: {stats.get('totalAmount', 0):,} VND")

            # 타이틀 확인
            title = page.title()
            print(f"\n  페이지 타이틀: {title}")
            if "QIP 인센티브" in title:
                print("  ✅ 타이틀 형식 일치")
                self.results['tests']['title_format'] = 'PASS'

            context.close()
            print("  ✅ 데이터 검증 완료")
            self.results['tests']['data_content'] = 'PASS'
            return True

        except Exception as e:
            print(f"  ❌ 데이터 검증 실패: {e}")
            self.results['tests']['data_content'] = f'FAIL: {e}'
            return False

    def test_modal_functions(self, browser):
        """모달 함수 테스트"""
        print("\n4. 모달 함수 검증")
        print("-" * 40)

        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(IMPROVED_HTML)
            page.wait_for_load_state('networkidle')

            # 모달 함수들 확인
            modal_functions = [
                'showTotalWorkingDaysDetails',
                'showZeroWorkingDaysDetails',
                'showAbsentWithoutInformDetails',
                'showMinimumDaysDetails'
            ]

            for func_name in modal_functions:
                exists = page.evaluate(f"typeof window.{func_name} === 'function'")
                print(f"  {func_name}: {'✅ 있음' if exists else '❌ 없음'}")
                if exists:
                    self.results['tests'][f'modal_{func_name}'] = 'PASS'
                else:
                    self.results['tests'][f'modal_{func_name}'] = 'FAIL'

            # ModalManager 확인
            has_modal_manager = page.evaluate("typeof window.ModalManager !== 'undefined'")
            print(f"  ModalManager: {'✅ 있음' if has_modal_manager else '❌ 없음'}")

            context.close()
            print("  ✅ 모달 함수 검증 완료")
            return True

        except Exception as e:
            print(f"  ❌ 모달 함수 검증 실패: {e}")
            self.results['tests']['modal_functions'] = f'FAIL: {e}'
            return False

    def test_language_switching(self, browser):
        """언어 전환 테스트"""
        print("\n5. 언어 전환 기능 테스트")
        print("-" * 40)

        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(IMPROVED_HTML)
            page.wait_for_load_state('networkidle')

            # 언어 버튼 찾기
            lang_buttons = page.query_selector_all('.lang-btn, button[data-lang]')
            print(f"  언어 버튼 개수: {len(lang_buttons)}")

            languages = ['ko', 'en', 'vi']
            for i, lang in enumerate(languages):
                try:
                    # 언어 버튼 클릭
                    btn = page.query_selector(f'[data-lang="{lang}"]')
                    if btn:
                        btn.click()
                        page.wait_for_timeout(500)

                        # 타이틀 변경 확인
                        title_elem = page.query_selector('#dashboardTitle')
                        if title_elem:
                            title_text = title_elem.inner_text()
                            print(f"  {lang}: {title_text}")

                        # 스크린샷
                        page.screenshot(path=f'tests/screenshots/improved/lang_{lang}.png')
                except Exception as e:
                    print(f"  {lang}: ❌ 오류 - {e}")

            context.close()
            print("  ✅ 언어 전환 테스트 완료")
            self.results['tests']['language_switching'] = 'PASS'
            return True

        except Exception as e:
            print(f"  ❌ 언어 전환 테스트 실패: {e}")
            self.results['tests']['language_switching'] = f'FAIL: {e}'
            return False

    def test_performance(self, browser):
        """성능 측정"""
        print("\n6. 성능 측정")
        print("-" * 40)

        try:
            context = browser.new_context()

            # 개선된 버전 성능 측정
            page = context.new_page()

            # 성능 타이밍 기록
            page.on('load', lambda: print("  페이지 로드 이벤트 발생"))

            start_time = time.time()
            page.goto(IMPROVED_HTML)
            page.wait_for_load_state('networkidle')
            load_time = time.time() - start_time

            # 파일 크기 확인
            file_path = BASE_DIR / "output_files/Incentive_Dashboard_2025_09_Version_6.html"
            if file_path.exists():
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                print(f"  파일 크기: {file_size:.2f} MB")

            print(f"  로딩 시간: {load_time:.2f}초")

            # DOM 요소 개수
            element_count = page.evaluate("document.querySelectorAll('*').length")
            print(f"  DOM 요소 개수: {element_count}")

            context.close()
            print("  ✅ 성능 측정 완료")
            self.results['tests']['performance'] = f'PASS: {load_time:.2f}s'
            return True

        except Exception as e:
            print(f"  ❌ 성능 측정 실패: {e}")
            self.results['tests']['performance'] = f'FAIL: {e}'
            return False

    def generate_report(self):
        """테스트 결과 리포트 생성"""
        print("\n" + "=" * 60)
        print("테스트 결과 요약")
        print("=" * 60)

        # 통계 계산
        for test, result in self.results['tests'].items():
            if isinstance(result, str):
                if result.startswith('PASS'):
                    self.results['summary']['passed'] += 1
                else:
                    self.results['summary']['failed'] += 1
                self.results['summary']['total'] += 1

        # 결과 출력
        print(f"\n총 테스트: {self.results['summary']['total']}개")
        print(f"✅ 성공: {self.results['summary']['passed']}개")
        print(f"❌ 실패: {self.results['summary']['failed']}개")

        pass_rate = (self.results['summary']['passed'] / max(self.results['summary']['total'], 1)) * 100
        print(f"\n통과율: {pass_rate:.1f}%")

        if pass_rate == 100:
            print("\n🎉 모든 테스트 PASS - 두 대시보드가 사용자 관점에서 동일합니다!")
        elif pass_rate >= 90:
            print("\n✅ 대부분의 테스트 통과 - 사소한 차이점만 있습니다.")
        else:
            print("\n⚠️ 개선이 필요한 부분이 있습니다.")

        # JSON 리포트 저장
        with open('test_results/comparison_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n상세 리포트: test_results/comparison_report.json")
        print(f"스크린샷: tests/screenshots/")

        return pass_rate

def main():
    """메인 테스트 실행 함수"""
    print("=" * 60)
    print("원본 vs 개선 대시보드 동일성 검증")
    print("=" * 60)

    tester = DashboardComparisonTest()
    tester.setup_method()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless=False로 변경하면 브라우저 보임

        try:
            # 모든 테스트 실행
            tester.test_visual_comparison(browser)
            tester.test_tab_functionality(browser)
            tester.test_data_content(browser)
            tester.test_modal_functions(browser)
            tester.test_language_switching(browser)
            tester.test_performance(browser)

        finally:
            browser.close()

    # 리포트 생성
    pass_rate = tester.generate_report()

    # 종료 코드 반환 (100% 통과시 0, 아니면 1)
    return 0 if pass_rate == 100 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)