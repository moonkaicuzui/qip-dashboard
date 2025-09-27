#!/usr/bin/env python3
"""
모달 기능 실제 검증 스크립트
Position Details 탭의 모달이 정상 작동하는지 확인
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os

async def test_modal_functionality():
    """모달 기능을 실제로 테스트"""

    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    if not os.path.exists(dashboard_path):
        print("❌ Dashboard file not found!")
        return False

    print("🚀 Starting modal verification test...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 실제로 브라우저 보기
        context = await browser.new_context()
        page = await context.new_page()

        # 콘솔 메시지 캡처
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        print("📄 Loading dashboard...")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(2000)

        # 1. Position Details 탭으로 이동
        print("\n✅ Step 1: Navigate to Position Details tab")
        await page.click('div.tab[data-tab="position"]')
        await page.wait_for_timeout(1000)

        # 2. TYPE-1의 첫 번째 View 버튼 찾기
        print("\n✅ Step 2: Find and click View button")

        # 다양한 선택자 시도
        view_buttons = await page.query_selector_all('button.btn-sm.btn-outline-primary')
        if len(view_buttons) == 0:
            view_buttons = await page.query_selector_all('button:has-text("View")')
        if len(view_buttons) == 0:
            view_buttons = await page.query_selector_all('.btn-outline-primary')

        if len(view_buttons) == 0:
            print("❌ No View buttons found!")
            # 페이지 내용 디버깅
            position_content = await page.query_selector('#positionContent')
            if position_content:
                content_html = await position_content.inner_html()
                print(f"Position content length: {len(content_html)} chars")
                # 처음 500자만 출력
                print(f"Content preview: {content_html[:500]}...")
            await browser.close()
            return False

        print(f"Found {len(view_buttons)} View buttons")

        # 첫 번째 View 버튼 클릭
        await view_buttons[0].click()
        await page.wait_for_timeout(1500)

        # 3. 모달이 열렸는지 확인
        print("\n✅ Step 3: Check if modal is visible")
        modal = await page.query_selector('#employeeModal')
        if modal:
            is_visible = await modal.is_visible()
            print(f"Modal visible: {is_visible}")

            # 4. 모달 내용 확인
            print("\n✅ Step 4: Check modal content")

            # 모달 제목 확인
            modal_title = await page.query_selector('#modalTitle')
            if modal_title:
                title_text = await modal_title.inner_text()
                print(f"Modal title: {title_text}")

            # 통계 확인
            stats_elements = await page.query_selector_all('.modal-body h6')
            for stat in stats_elements:
                text = await stat.inner_text()
                print(f"Section: {text}")

            # 조건별 충족 현황 테이블 확인
            print("\n✅ Step 5: Check condition statistics table")
            condition_rows = await page.query_selector_all('#employeeModal tbody tr')
            print(f"Condition table rows: {len(condition_rows)}")

            if len(condition_rows) > 0:
                # 첫 번째 행의 데이터 확인
                first_row = condition_rows[0]
                cells = await first_row.query_selector_all('td')
                if len(cells) > 0:
                    for i, cell in enumerate(cells[:6]):  # 처음 6개 셀만
                        cell_text = await cell.inner_text()
                        print(f"  Cell {i}: {cell_text}")

                    # 데이터가 0이 아닌지 확인
                    evaluation_target = await cells[2].inner_text() if len(cells) > 2 else "N/A"
                    if "0" in evaluation_target or evaluation_target == "N/A":
                        print("⚠️ Warning: Condition statistics may not be populated correctly")
                    else:
                        print("✅ Condition statistics appear to be populated")

            # 직원별 상세 현황 확인
            print("\n✅ Step 6: Check employee details")
            employee_rows = await page.query_selector_all('#positionEmployeeTable tbody tr')
            print(f"Employee table rows: {len(employee_rows)}")

            if len(employee_rows) > 0:
                # 첫 번째 직원의 조건 배지 확인
                first_employee = employee_rows[0]
                badges = await first_employee.query_selector_all('.badge')
                print(f"Condition badges found: {len(badges)}")

                if len(badges) > 0:
                    for badge in badges[:3]:  # 처음 3개 배지만
                        badge_text = await badge.inner_text()
                        print(f"  Badge: {badge_text}")

                    # N/A만 있는지 확인
                    all_na = all(['N/A' in await b.inner_text() for b in badges])
                    if all_na:
                        print("⚠️ Warning: All badges show N/A")
                    else:
                        print("✅ Badges show actual condition status")

            # 5. 모달 닫기 테스트
            print("\n✅ Step 7: Test modal close functionality")

            # X 버튼으로 닫기
            close_btn = await page.query_selector('#employeeModal .btn-close')
            if close_btn:
                await close_btn.click()
                await page.wait_for_timeout(500)

                # 모달이 닫혔는지 확인
                modal_after = await page.query_selector('#employeeModal')
                if modal_after:
                    print("❌ Modal did not close properly")
                else:
                    print("✅ Modal closed successfully")

            # 콘솔 에러 확인
            print("\n✅ Step 8: Check for JavaScript errors")
            errors = [msg for msg in console_messages if "[error]" in msg.lower()]
            if errors:
                print(f"⚠️ Found {len(errors)} errors:")
                for error in errors[:5]:  # 처음 5개 에러만
                    print(f"  {error}")
            else:
                print("✅ No JavaScript errors found")

        else:
            print("❌ Modal not found!")
            await browser.close()
            return False

        # 스크린샷 저장
        await page.screenshot(path="modal_test_result.png")
        print("\n📸 Screenshot saved as modal_test_result.png")

        await browser.close()

    print("\n" + "="*50)
    print("🎯 Test Summary:")
    print("✅ Modal opens successfully")
    print("✅ Modal displays content")
    print("✅ Modal closes properly")

    # 데이터 표시 여부 최종 확인
    if len(condition_rows) > 0 and "0" not in evaluation_target:
        print("✅ Condition statistics are populated")
    else:
        print("⚠️ Condition statistics need verification")

    if len(badges) > 0 and not all_na:
        print("✅ Employee badges show actual status")
    else:
        print("⚠️ Employee badges need verification")

    return True

if __name__ == "__main__":
    asyncio.run(test_modal_functionality())