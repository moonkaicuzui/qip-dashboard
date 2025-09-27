#!/usr/bin/env python3
"""
Version 6 대시보드의 AQL과 5PRS 모달 표시 테스트
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_v6_dashboard():
    """Version 6 대시보드 테스트"""

    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Dashboard_V6_Complete_2025_september.html"

    print("🚀 Testing Version 6 Dashboard with updated field mappings...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 브라우저 보기
        context = await browser.new_context()
        page = await context.new_page()

        print("📄 Loading V6 dashboard...")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(3000)

        # Position Details 탭으로 이동
        print("\n✅ Step 1: Navigate to Position Details tab")
        await page.click('div.tab[data-tab="position"]')
        await page.wait_for_timeout(1500)

        # TYPE-1 View 버튼 찾기
        print("\n✅ Step 2: Find and click View button")
        view_buttons = await page.query_selector_all('button.btn-outline-primary')
        print(f"Found {len(view_buttons)} View buttons")

        if len(view_buttons) > 0:
            # 첫 번째 View 버튼 클릭
            await view_buttons[0].click()
            await page.wait_for_timeout(2000)

            # 모달 확인
            modal = await page.query_selector('#employeeModal')
            if modal and await modal.is_visible():
                print("✅ Modal opened successfully!")

                # 조건별 충족 현황 확인
                print("\n✅ Step 3: Check condition statistics")
                stats = await page.evaluate("""() => {
                    const rows = document.querySelectorAll('#employeeModal .modal-body table tbody tr');
                    const conditions = [];
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 5) {
                            conditions.push({
                                name: cells[0].innerText,
                                applicable: cells[1].innerText,
                                total: cells[2].innerText,
                                met: cells[3].innerText,
                                unmet: cells[4].innerText,
                                rate: cells[5] ? cells[5].innerText : 'N/A'
                            });
                        }
                    });
                    return conditions;
                }""")

                # 조건 출력
                print("\nCondition Statistics Found:")
                for stat in stats:
                    print(f"\n{stat['name']}:")
                    print(f"  적용여부: {stat['applicable']}")
                    print(f"  평가대상: {stat['total']}")
                    print(f"  충족: {stat['met']}")
                    print(f"  미충족: {stat['unmet']}")
                    print(f"  충족률: {stat['rate']}")

                    # AQL과 5PRS 데이터 확인
                    if 'AQL' in stat['name'] and stat['total'] != '0' and stat['total'] != 'N/A':
                        print("  ✅ AQL data is properly displayed!")

                    if ('5PRS' in stat['name'] or 'PRS' in stat['name']) and stat['total'] != '0' and stat['total'] != 'N/A':
                        print("  ✅ 5PRS data is properly displayed!")

                # 직원 배지 확인
                print("\n✅ Step 4: Check employee badges")
                badges = await page.evaluate("""() => {
                    const table = document.querySelector('#positionEmployeeTable');
                    if (!table) return [];

                    const firstRow = table.querySelector('tbody tr');
                    if (!firstRow) return [];

                    const badges = [];
                    const badgeElements = firstRow.querySelectorAll('.badge');
                    badgeElements.forEach(b => {
                        badges.push(b.innerText);
                    });
                    return badges;
                }""")

                print(f"\nEmployee badges: {badges}")
                for badge in badges:
                    if 'N/A' not in badge:
                        print(f"  ✅ {badge} - shows actual data")
                    else:
                        print(f"  ⚠️ {badge} - still showing N/A")

                # 스크린샷 저장
                await page.screenshot(path="v6_modal_test.png")
                print("\n📸 Screenshot saved as v6_modal_test.png")

                # 모달 닫기
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(500)

            else:
                print("❌ Modal not visible!")
        else:
            print("❌ No View buttons found!")

        print("\n⏸️ Browser will remain open for manual inspection...")
        print("Press Ctrl+C to close the browser and exit")
        await asyncio.sleep(60)  # 60초 대기

        await browser.close()

    print("\n" + "="*50)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_v6_dashboard())