#!/usr/bin/env python3
"""
최종 모달 시각적 검증 - 브라우저에서 직접 확인
"""

from playwright.sync_api import sync_playwright
import os
import time

def final_visual_test():
    """브라우저에서 모달 동작 시각적 검증"""

    with sync_playwright() as p:
        # 브라우저 실행 (visible)
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000  # 1초 딜레이로 천천히 동작
        )
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        print("="*80)
        print("🎯 최종 모달 시각적 검증 시작")
        print("="*80)

        # 1. Dashboard 기본 정보 확인
        print("\n📊 Dashboard 기본 정보:")

        # Total Employees
        total_emp = page.query_selector('h6:has-text("Total Employees") + h2')
        if total_emp:
            print(f"  - Total Employees: {total_emp.inner_text()}")

        # Paid Employees
        paid_emp = page.query_selector('h6:has-text("Paid Employees") + h2')
        if paid_emp:
            print(f"  - Paid Employees: {paid_emp.inner_text()}")

        # Total Paid Amount
        total_amount = page.query_selector('h6:has-text("Total Paid Amount") + h2')
        if total_amount:
            print(f"  - Total Paid Amount: {total_amount.inner_text()}")

        # 2. Position Details 탭 테스트
        print("\n📌 Position Details 탭 테스트:")
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(2000)
            print("  ✅ Position Details 탭 열림")

            # Position 테이블에서 GROUP LEADER 찾기
            rows = page.query_selector_all('#positionTable tbody tr')
            print(f"  - Position 테이블 행 수: {len(rows)}")

            group_leader_found = False
            for i, row in enumerate(rows):
                cells = row.query_selector_all('td')
                if len(cells) >= 4:
                    position = cells[0].inner_text()
                    type_text = cells[1].inner_text()
                    count = cells[2].inner_text()

                    print(f"  - 행 {i+1}: {position} / {type_text} / {count}명")

                    # GROUP LEADER TYPE-2 찾으면 클릭
                    if 'GROUP LEADER' in position and 'TYPE-2' in type_text:
                        group_leader_found = True
                        print(f"\n  🎯 GROUP LEADER TYPE-2 발견! ({count}명)")

                        view_btn = cells[3].query_selector('button')
                        if view_btn:
                            print("    - View 버튼 클릭...")
                            view_btn.click()
                            page.wait_for_timeout(3000)

                            # 모달 확인
                            modal = page.query_selector('#employeeModal')
                            if modal and modal.is_visible():
                                print("    ✅ Position Details 모달 열림!")

                                # Condition Fulfillment 테이블 확인
                                condition_table = page.query_selector('.condition-fulfillment-table tbody')
                                if condition_table:
                                    condition_rows = condition_table.query_selector_all('tr')
                                    if len(condition_rows) > 0:
                                        print(f"    ✅ Condition Fulfillment 테이블: {len(condition_rows)}개 조건")
                                        for j, cond_row in enumerate(condition_rows[:3]):
                                            cells = cond_row.query_selector_all('td')
                                            if len(cells) >= 4:
                                                cond_name = cells[1].inner_text()
                                                total = cells[2].inner_text()
                                                met = cells[3].inner_text()
                                                print(f"      • 조건 {j+1}: {cond_name} - {met}/{total}")
                                    else:
                                        print("    ❌ Condition Fulfillment 테이블이 비어있음")

                                # 모달 닫기
                                close_btn = page.query_selector('.modal .btn-close')
                                if close_btn:
                                    close_btn.click()
                                    page.wait_for_timeout(1000)
                        break

            if not group_leader_found:
                print("  ❌ GROUP LEADER TYPE-2를 찾을 수 없음")

        # 3. Individual Details 탭 테스트
        print("\n📌 Individual Details 탭 테스트:")
        individual_tab = page.query_selector('[data-tab="individual"]')
        if individual_tab:
            individual_tab.click()
            page.wait_for_timeout(2000)
            print("  ✅ Individual Details 탭 열림")

            # 첫 번째 TYPE-2 직원 찾기
            table_rows = page.query_selector_all('#employeeTable tbody tr')
            print(f"  - Individual 테이블 행 수: {len(table_rows[:10])}")

            type2_found = False
            for i, row in enumerate(table_rows[:20]):  # 처음 20개만 확인
                if row.is_visible():
                    cells = row.query_selector_all('td')
                    if len(cells) >= 6:
                        name = cells[1].inner_text()
                        position = cells[2].inner_text()
                        emp_type = cells[3].inner_text()
                        amount = cells[4].inner_text()

                        if 'TYPE-2' in emp_type:
                            type2_found = True
                            print(f"\n  🎯 TYPE-2 직원 발견:")
                            print(f"    - 이름: {name}")
                            print(f"    - 직급: {position}")
                            print(f"    - 타입: {emp_type}")
                            print(f"    - 인센티브: {amount}")

                            view_btn = cells[5].query_selector('button')
                            if view_btn:
                                print("    - View 버튼 클릭...")
                                view_btn.click()
                                page.wait_for_timeout(3000)

                                # Individual 모달 확인
                                modal = page.query_selector('#individualModal')
                                if modal and modal.is_visible():
                                    print("    ✅ Individual Details 모달 열림!")

                                    # Condition Status 확인
                                    condition_list = page.query_selector('#individualConditionList')
                                    if condition_list:
                                        items = condition_list.query_selector_all('li')
                                        if len(items) > 0:
                                            print(f"    ✅ Condition Status: {len(items)}개 조건")
                                            for j, item in enumerate(items[:3]):
                                                text = item.inner_text()
                                                print(f"      • {text}")

                                                if "No applicable conditions" in text:
                                                    print("      ❌ 'No applicable conditions' 메시지 표시됨")
                                        else:
                                            print("    ❌ Condition Status가 비어있음")

                                    # 모달 닫기
                                    close_btn = modal.query_selector('.btn-close')
                                    if close_btn:
                                        close_btn.click()
                                        page.wait_for_timeout(1000)
                            break

            if not type2_found:
                print("  ❌ TYPE-2 직원을 찾을 수 없음")

        # 4. 스크린샷 저장
        print("\n📸 스크린샷 저장...")
        page.screenshot(path='final_visual_test.png', full_page=True)
        print("  ✅ final_visual_test.png 저장됨")

        print("\n" + "="*80)
        print("💡 검증 완료!")
        print("  브라우저를 열어두었습니다. 직접 확인해보세요:")
        print("  1. Position Details 탭에서 GROUP LEADER (TYPE-2) View 버튼 클릭")
        print("  2. Condition Fulfillment by Category 테이블 확인")
        print("  3. Individual Details 탭에서 TYPE-2 직원 View 버튼 클릭")
        print("  4. Condition Status 리스트 확인")
        print("="*80)

        print("\n⏳ 60초 후 브라우저가 자동으로 닫힙니다...")
        time.sleep(60)

        browser.close()

if __name__ == '__main__':
    final_visual_test()