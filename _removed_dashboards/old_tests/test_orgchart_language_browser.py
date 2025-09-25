#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조직도 탭 언어 전환 브라우저 자동 테스트
Selenium을 사용한 실제 브라우저 테스트
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_orgchart_language_switching():
    """조직도 탭의 언어 전환을 브라우저에서 실제로 테스트"""

    print("=" * 80)
    print("🌐 조직도 탭 언어 전환 브라우저 자동 테스트")
    print("=" * 80)
    print()

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 백그라운드 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    # 번역 파일 로드
    with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # WebDriver 초기화
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        # 대시보드 열기
        dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"
        driver.get(dashboard_path)
        time.sleep(2)  # 페이지 로드 대기

        print("✅ 대시보드 로드 완료")
        print()

        # 테스트 결과 저장
        test_results = {
            'tab_button': {},
            'filter_options': {},
            'legend_items': {},
            'modal_content': {}
        }

        # 1. 조직도 탭으로 이동
        print("📋 1. 조직도 탭 클릭 테스트")
        print("-" * 60)

        try:
            org_tab = driver.find_element(By.ID, "tabOrgChart")
            initial_text = org_tab.text
            print(f"초기 탭 텍스트: '{initial_text}'")

            # JavaScript로 클릭 (더 안정적)
            driver.execute_script("arguments[0].click();", org_tab)
            time.sleep(1)

            # 조직도 컨테이너 표시 확인
            org_container = driver.find_element(By.ID, "orgChartContainer")
            if org_container.is_displayed():
                print("✅ 조직도 탭 활성화 성공")
            else:
                print("❌ 조직도 탭 활성화 실패")
        except NoSuchElementException:
            print("❌ 조직도 탭 버튼을 찾을 수 없습니다")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

        print()

        # 2. 각 언어로 전환하며 테스트
        languages = ['ko', 'en', 'vi']
        language_names = {'ko': '한국어', 'en': 'English', 'vi': 'Tiếng Việt'}

        for lang in languages:
            print(f"🔤 {language_names[lang]} 언어 전환 테스트")
            print("-" * 40)

            # 언어 변경
            driver.execute_script(f"changeLanguage('{lang}')")
            time.sleep(1)

            # 2.1 탭 버튼 텍스트 확인
            try:
                tab_text = driver.find_element(By.ID, "tabOrgChart").text
                expected = translations['tabs']['orgChart'][lang]
                test_results['tab_button'][lang] = {
                    'actual': tab_text,
                    'expected': expected,
                    'match': tab_text == expected
                }
                status = "✅" if tab_text == expected else "❌"
                print(f"   탭 버튼: {status} '{tab_text}' (예상: '{expected}')")
            except Exception as e:
                print(f"   탭 버튼: ❌ 확인 실패 - {e}")

            # 2.2 필터 옵션 확인
            filter_ids = ['filterAll', 'filterPaid', 'filterUnpaid']
            filter_keys = ['viewAll', 'paidOnly', 'unpaidOnly']

            for filter_id, filter_key in zip(filter_ids, filter_keys):
                try:
                    filter_elem = driver.find_element(By.ID, filter_id)
                    actual_text = filter_elem.text
                    expected = translations['orgChart']['filters'][filter_key][lang]

                    if lang not in test_results['filter_options']:
                        test_results['filter_options'][lang] = {}

                    test_results['filter_options'][lang][filter_id] = {
                        'actual': actual_text,
                        'expected': expected,
                        'match': actual_text == expected
                    }

                    status = "✅" if actual_text == expected else "❌"
                    print(f"   {filter_id}: {status} '{actual_text}'")
                except Exception as e:
                    print(f"   {filter_id}: ❌ 확인 실패")

            # 2.3 범례 텍스트 확인
            legend_ids = ['legendReceived', 'legendNotReceived']
            legend_keys = ['incentiveReceived', 'incentiveNotReceived']

            for legend_id, legend_key in zip(legend_ids, legend_keys):
                try:
                    legend_elem = driver.find_element(By.ID, legend_id)
                    actual_text = legend_elem.text
                    expected = translations['orgChart'][legend_key][lang]

                    if lang not in test_results['legend_items']:
                        test_results['legend_items'][lang] = {}

                    test_results['legend_items'][lang][legend_id] = {
                        'actual': actual_text,
                        'expected': expected,
                        'match': actual_text == expected
                    }

                    status = "✅" if actual_text == expected else "❌"
                    print(f"   {legend_id}: {status} '{actual_text}'")
                except Exception as e:
                    print(f"   {legend_id}: ❌ 확인 실패")

            print()

        # 3. 조직도 노드 클릭 및 모달 테스트
        print("📋 3. 모달 창 언어 전환 테스트")
        print("-" * 60)

        # 첫 번째 노드 클릭 (MANAGER)
        try:
            # 조직도가 렌더링될 시간 대기
            time.sleep(2)

            # SVG 내의 첫 번째 rect 요소 찾기 (노드)
            first_node = driver.find_element(By.CSS_SELECTOR, "#orgChartContainer svg rect")
            driver.execute_script("arguments[0].dispatchEvent(new Event('click', {bubbles: true}));", first_node)
            time.sleep(1)

            # 모달이 열렸는지 확인
            modal = driver.find_element(By.ID, "incentiveModal")
            if modal.is_displayed():
                print("✅ 모달 창 열기 성공")

                # 각 언어로 전환하며 모달 내용 확인
                for lang in languages:
                    driver.execute_script(f"changeLanguage('{lang}')")
                    time.sleep(0.5)

                    # 모달 제목 확인
                    modal_title = driver.find_element(By.ID, "modalTitle").text
                    print(f"   {language_names[lang]} 모달 제목: '{modal_title}'")

                # 모달 닫기
                close_button = driver.find_element(By.CSS_SELECTOR, "#incentiveModal .close")
                close_button.click()
                time.sleep(0.5)
                print("✅ 모달 창 닫기 성공")
            else:
                print("❌ 모달 창이 열리지 않았습니다")
        except Exception as e:
            print(f"❌ 모달 테스트 실패: {e}")

        print()

        # 4. 테스트 결과 요약
        print("=" * 80)
        print("📊 테스트 결과 요약")
        print("-" * 60)

        total_tests = 0
        passed_tests = 0

        for category, results in test_results.items():
            for lang, items in results.items():
                if isinstance(items, dict):
                    for item_id, result in items.items():
                        if isinstance(result, dict) and 'match' in result:
                            total_tests += 1
                            if result['match']:
                                passed_tests += 1

        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"총 테스트: {total_tests}")
            print(f"성공: {passed_tests}")
            print(f"실패: {total_tests - passed_tests}")
            print(f"성공률: {success_rate:.1f}%")

            if success_rate == 100:
                print("\n✅ 모든 언어 전환 테스트가 성공했습니다!")
            elif success_rate >= 80:
                print("\n⚠️ 대부분의 테스트가 성공했지만 일부 문제가 있습니다.")
            else:
                print("\n❌ 언어 전환에 문제가 있습니다. 수정이 필요합니다.")
        else:
            print("❌ 테스트를 실행할 수 없었습니다.")

    except Exception as e:
        print(f"❌ 브라우저 초기화 실패: {e}")
        print("Selenium WebDriver가 설치되어 있는지 확인하세요:")
        print("pip install selenium")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("\n✅ 브라우저 종료 완료")

    print("=" * 80)

if __name__ == "__main__":
    test_orgchart_language_switching()