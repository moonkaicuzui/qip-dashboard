#!/usr/bin/env python3
"""
영어 모드에서 단위 표시 검증
"""

from playwright.sync_api import sync_playwright
import time

def verify_english_units():
    print("=" * 60)
    print("🔍 영어 모드 단위 표시 검증")
    print("=" * 60)

    dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto(dashboard_path)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 영어로 전환
        print("\n🌐 영어 모드로 전환...")
        lang_button = page.locator("#languageSwitch")
        if lang_button.count() > 0:
            # 현재 언어 확인
            current_lang = lang_button.inner_text().strip()
            print(f"   현재 언어 버튼: {current_lang}")

            # 영어가 아니면 클릭
            if "English" not in current_lang:
                lang_button.click()
                time.sleep(1)
                print("   ✅ 영어로 전환 완료")

        # 개인별 상세 탭
        page.click("#tabIndividual")
        time.sleep(2)

        # 테스트할 직원: 622020174 (다양한 조건 포함)
        emp_id = "622020174"
        print(f"\n{'='*80}")
        print(f"📋 직원: {emp_id} (NGUYỄN NGỌC BÍCH THỦY)")
        print(f"{'='*80}")

        # JavaScript로 직접 모달 열기
        page.evaluate(f"showEmployeeDetail('{emp_id}')")
        time.sleep(3)

        # 모달 확인
        modal = page.locator(".modal.show")
        if modal.count() > 0:
            print("✅ 모달 열림 성공\n")

            # 조건 테이블 찾기
            tables = modal.locator("table")

            for table_idx in range(tables.count()):
                table = tables.nth(table_idx)
                headers = table.locator("thead th")

                # Performance 컬럼이 있는 테이블 찾기
                has_performance = False
                for h_idx in range(headers.count()):
                    header_text = headers.nth(h_idx).inner_text().strip()
                    if "Performance" in header_text or "실적" in header_text:
                        has_performance = True
                        break

                if has_performance:
                    print(f"📊 Condition Fulfillment Details (English Mode):")
                    print("=" * 100)

                    rows = table.locator("tbody tr")
                    unit_checks = {
                        '1': {'expected': ' %', 'desc': 'Percentage with space'},
                        '2': {'expected': 'day', 'desc': 'Days unit'},
                        '3': {'expected': 'day', 'desc': 'Days unit'},
                        '4': {'expected': 'day', 'desc': 'Days unit'},
                        '5': {'expected': 'PO reject', 'desc': 'PO reject unit'},
                    }

                    for i in range(rows.count()):
                        row = rows.nth(i)
                        cells = row.locator("td")

                        if cells.count() >= 4:
                            cond_num = cells.nth(0).inner_text().strip()
                            cond_name = cells.nth(1).inner_text().strip()
                            performance = cells.nth(2).inner_text().strip()
                            result = cells.nth(3).inner_text().strip()

                            # 결과 아이콘
                            icon = "✅" if "Met" in result else "❌"

                            print(f"{icon} Condition {cond_num}: {cond_name}")
                            print(f"      Performance: [{performance}]")
                            print(f"      Result: {result}")

                            # 단위 변환 체크
                            if cond_num in unit_checks:
                                expected = unit_checks[cond_num]['expected']
                                desc = unit_checks[cond_num]['desc']

                                if expected in performance:
                                    print(f"      ✅ Unit OK: {desc} found")
                                else:
                                    print(f"      ⚠️  Unit Issue: Expected '{expected}' in '{performance}'")

                            # 특별 체크: 조건 1은 공백 포함 확인
                            if cond_num == "1" and "%" in performance:
                                if " %" in performance:
                                    print(f"      ✅ Space before % confirmed")
                                else:
                                    print(f"      ⚠️  Missing space before %")

                    break

            # 스크린샷
            screenshot_path = f"output_files/english_mode_verify.png"
            modal.screenshot(path=screenshot_path)
            print(f"\n📸 스크린샷: {screenshot_path}")

            time.sleep(3)
        else:
            print("❌ 모달이 열리지 않음")

        browser.close()

    print("\n" + "=" * 60)
    print("✅ 영어 모드 단위 표시 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    verify_english_units()