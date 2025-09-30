#!/usr/bin/env python3
"""
Position Details 모달 수정사항 테스트
"""

from playwright.sync_api import sync_playwright
import os
import time

def test_modal_fixes():
    """Position Details 모달의 Condition Fulfillment 테스트"""

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        print("="*80)
        print("🔍 Position Details 모달 수정사항 테스트")
        print("="*80)

        # Position Details 탭으로 이동
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(2000)
            print("✅ Position Details 탭으로 이동")

            # GROUP LEADER TYPE-2 테스트
            print("\n📌 GROUP LEADER (TYPE-2) 테스트:")
            rows = page.query_selector_all('#positionTable tbody tr')
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 4:
                    position = cells[0].inner_text()
                    emp_type = cells[1].inner_text()

                    if 'GROUP LEADER' in position and 'TYPE-2' in emp_type:
                        print(f"  - {position} ({emp_type}) 발견")
                        view_btn = cells[3].query_selector('button')
                        if view_btn:
                            view_btn.click()
                            page.wait_for_timeout(2000)

                            # Condition Fulfillment by Category 테이블 확인
                            condition_table = page.query_selector('.condition-fulfillment-table tbody')
                            if condition_table:
                                condition_rows = condition_table.query_selector_all('tr')
                                print(f"  - Condition Fulfillment by Category 테이블: {len(condition_rows)}개 조건")

                                if len(condition_rows) > 0:
                                    print("  ✅ 테이블에 데이터가 있음!")
                                    for i, row in enumerate(condition_rows[:2]):  # 처음 2개만 출력
                                        cells = row.query_selector_all('td')
                                        if len(cells) >= 4:
                                            name = cells[1].inner_text()
                                            total = cells[2].inner_text()
                                            met = cells[3].inner_text()
                                            print(f"    • {name}: {met}/{total}")
                                else:
                                    print("  ❌ 테이블이 비어있음")

                            # Employee Details Status 확인
                            employee_table = page.query_selector('#positionEmployeeTable tbody')
                            if employee_table:
                                employee_rows = employee_table.query_selector_all('tr')
                                print(f"\n  - Employee Details Status: {len(employee_rows)}명")

                                # 첫 번째 직원의 배지 확인
                                if len(employee_rows) > 0:
                                    first_row = employee_rows[0]
                                    cells = first_row.query_selector_all('td')
                                    if len(cells) >= 5:
                                        name = cells[1].inner_text()
                                        badges = cells[4].query_selector_all('.badge')
                                        print(f"    • {name}: {len(badges)}개 배지")
                                        for badge in badges:
                                            print(f"      - {badge.inner_text()}")

                                        if len(badges) == 0:
                                            print("      ❌ 배지가 없음")
                                        else:
                                            print("      ✅ 배지가 표시됨!")

                            # 모달 닫기
                            close_btn = page.query_selector('.modal .btn-close')
                            if close_btn:
                                close_btn.click()
                                page.wait_for_timeout(1000)
                        break

            # QA/QC INSPECTOR TYPE-1 테스트
            print("\n📌 QA/QC INSPECTOR (TYPE-1) 테스트:")
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 4:
                    position = cells[0].inner_text()
                    emp_type = cells[1].inner_text()

                    if 'QA/QC INSPECTOR' in position and 'TYPE-1' in emp_type:
                        print(f"  - {position} ({emp_type}) 발견")
                        view_btn = cells[3].query_selector('button')
                        if view_btn:
                            view_btn.click()
                            page.wait_for_timeout(2000)

                            # Condition Fulfillment by Category 테이블 확인
                            condition_table = page.query_selector('.condition-fulfillment-table tbody')
                            if condition_table:
                                condition_rows = condition_table.query_selector_all('tr')
                                print(f"  - Condition Fulfillment by Category 테이블: {len(condition_rows)}개 조건")

                                if len(condition_rows) > 0:
                                    print("  ✅ 테이블에 데이터가 있음!")
                                    for i, row in enumerate(condition_rows[:3]):  # 처음 3개만 출력
                                        cells = row.query_selector_all('td')
                                        if len(cells) >= 4:
                                            name = cells[1].inner_text()
                                            total = cells[2].inner_text()
                                            met = cells[3].inner_text()
                                            print(f"    • {name}: {met}/{total}")
                                else:
                                    print("  ❌ 테이블이 비어있음")

                            # Employee Details Status 확인
                            employee_table = page.query_selector('#positionEmployeeTable tbody')
                            if employee_table:
                                employee_rows = employee_table.query_selector_all('tr')
                                print(f"\n  - Employee Details Status: {len(employee_rows)}명")

                                # 첫 번째 직원의 배지 확인
                                if len(employee_rows) > 0:
                                    first_row = employee_rows[0]
                                    cells = first_row.query_selector_all('td')
                                    if len(cells) >= 5:
                                        name = cells[1].inner_text()
                                        badges = cells[4].query_selector_all('.badge')
                                        print(f"    • {name}: {len(badges)}개 배지")
                                        for badge in badges:
                                            print(f"      - {badge.inner_text()}")

                                        if len(badges) == 0:
                                            print("      ❌ 배지가 없음")
                                        else:
                                            print("      ✅ 배지가 표시됨!")

                            # 모달 닫기
                            close_btn = page.query_selector('.modal .btn-close')
                            if close_btn:
                                close_btn.click()
                                page.wait_for_timeout(1000)
                        break

        print("\n" + "="*80)
        print("💡 테스트 결과 요약:")
        print("1. Condition Fulfillment by Category 테이블 데이터 표시 여부")
        print("2. Employee Details Status 배지 표시 여부")
        print("3. TYPE-1과 TYPE-2 조건 차이 확인")
        print("="*80)

        # 브라우저 30초 유지
        print("\n⏳ 30초 후 브라우저가 자동으로 닫힙니다...")
        time.sleep(30)

        browser.close()

if __name__ == '__main__':
    test_modal_fixes()