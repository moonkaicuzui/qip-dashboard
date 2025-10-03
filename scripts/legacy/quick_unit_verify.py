#!/usr/bin/env python3
"""
단위 표시 빠른 검증 - 여러 직원의 모달 확인
"""

from playwright.sync_api import sync_playwright
import time

def verify_unit_display():
    print("=" * 60)
    print("🔍 단위 표시 검증: 여러 직원 모달 확인")
    print("=" * 60)

    dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto(dashboard_path)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 개인별 상세 탭
        page.click("#tabIndividual")
        time.sleep(2)

        # 테스트할 직원들
        test_employees = [
            ("622020174", "NGUYỄN NGỌC BÍCH THỦY - Condition 1,3,4 with 0 values"),
            ("619020468", "THỊ MY - Conditions with Pass status")
        ]

        for emp_id, description in test_employees:
            print(f"\n{'='*80}")
            print(f"📋 직원: {emp_id} ({description})")
            print(f"{'='*80}")

            # JavaScript로 직접 모달 열기
            page.evaluate(f"showEmployeeDetail('{emp_id}')")
            time.sleep(2)

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
                        if "실적" in header_text or "Performance" in header_text:
                            has_performance = True
                            break

                    if has_performance:
                        print(f"📊 Condition Fulfillment Details:")
                        print("=" * 100)

                        rows = table.locator("tbody tr")
                        for i in range(rows.count()):
                            row = rows.nth(i)
                            cells = row.locator("td")

                            if cells.count() >= 4:
                                cond_num = cells.nth(0).inner_text().strip()
                                cond_name = cells.nth(1).inner_text().strip()
                                performance = cells.nth(2).inner_text().strip()
                                result = cells.nth(3).inner_text().strip()

                                # 결과 아이콘
                                icon = "✅" if "Met" in result or "충족" in result else "❌"

                                print(f"{icon} 조건 {cond_num}: {cond_name}")
                                print(f"      실적: [{performance}]")
                                print(f"      결과: {result}")

                                # 단위 표시 체크
                                if cond_num == "1" and ("%" in performance):
                                    if " %" in performance:
                                        print(f"      ✅ 조건 1 단위 OK: 공백 포함 '%'")
                                    else:
                                        print(f"      ⚠️  조건 1 단위 문제: 공백 없는 '%'")

                                if cond_num in ["2", "3", "4"] and performance not in ["Pass", "통과"]:
                                    if "days" in performance or "일" in performance:
                                        print(f"      ✅ 조건 {cond_num} 단위 OK: days/일 표시")
                                    else:
                                        print(f"      ⚠️  조건 {cond_num} 단위 문제: 단위 없음")

                                if cond_num == "5" and performance not in ["Pass", "통과"]:
                                    if "PO reject" in performance or "건" in performance:
                                        print(f"      ✅ 조건 5 단위 OK: PO reject/건 표시")
                                    else:
                                        print(f"      ⚠️  조건 5 단위 문제: 단위 없음")

                        break

                # 스크린샷
                screenshot_path = f"output_files/unit_verify_{emp_id}.png"
                modal.screenshot(path=screenshot_path)
                print(f"\n📸 스크린샷: {screenshot_path}")

                # 모달 닫기
                close_button = modal.locator("button.btn-close, button[data-bs-dismiss='modal']")
                if close_button.count() > 0:
                    close_button.first.click()
                    time.sleep(1)
            else:
                print("❌ 모달이 열리지 않음")

        browser.close()

    print("\n" + "=" * 60)
    print("✅ 단위 표시 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    verify_unit_display()