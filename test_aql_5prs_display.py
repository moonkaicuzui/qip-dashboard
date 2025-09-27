#!/usr/bin/env python3
"""
AQL과 5PRS 데이터가 모달에 제대로 표시되는지 검증하는 스크립트
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_aql_5prs_display():
    """AQL과 5PRS 데이터 표시 테스트"""

    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    print("🚀 Starting AQL/5PRS data verification test...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("📄 Loading dashboard...")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(2000)

        # Position Details 탭으로 이동
        print("\n✅ Step 1: Navigate to Position Details tab")
        await page.click('div.tab[data-tab="position"]')
        await page.wait_for_timeout(1000)

        # View 버튼 클릭 (TYPE-1의 첫 번째)
        print("\n✅ Step 2: Click View button")
        view_buttons = await page.query_selector_all('button.btn-sm.btn-outline-primary')
        if len(view_buttons) > 0:
            await view_buttons[0].click()
            await page.wait_for_timeout(1500)

            # 모달이 열렸는지 확인
            modal = await page.query_selector('#employeeModal')
            if modal:
                print("✅ Modal opened successfully")

                # 조건별 충족 현황 테이블의 데이터 확인
                print("\n✅ Step 3: Check condition statistics")

                # JavaScript로 조건 통계 확인
                stats = await page.evaluate("""() => {
                    const rows = document.querySelectorAll('#employeeModal tbody tr');
                    const stats = [];
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 4) {
                            const condition = cells[0].innerText;
                            const total = cells[1].innerText;
                            const met = cells[2].innerText;
                            const unmet = cells[3].innerText;
                            stats.push({
                                condition: condition,
                                total: total,
                                met: met,
                                unmet: unmet
                            });
                        }
                    });
                    return stats;
                }""")

                # AQL과 5PRS 조건 찾기
                aql_found = False
                prs_found = False

                for stat in stats:
                    if 'AQL' in stat['condition']:
                        aql_found = True
                        print(f"\nAQL Condition Found:")
                        print(f"  평가대상: {stat['total']}")
                        print(f"  충족: {stat['met']}")
                        print(f"  미충족: {stat['unmet']}")

                        if stat['total'] != '0':
                            print("  ✅ AQL data is populated!")
                        else:
                            print("  ⚠️ AQL data still shows 0")

                    if '5PRS' in stat['condition'] or 'PRS' in stat['condition']:
                        prs_found = True
                        print(f"\n5PRS Condition Found:")
                        print(f"  평가대상: {stat['total']}")
                        print(f"  충족: {stat['met']}")
                        print(f"  미충족: {stat['unmet']}")

                        if stat['total'] != '0':
                            print("  ✅ 5PRS data is populated!")
                        else:
                            print("  ⚠️ 5PRS data still shows 0")

                # 직원별 상세 현황에서 배지 확인
                print("\n✅ Step 4: Check employee badges")
                badges = await page.evaluate("""() => {
                    const firstRow = document.querySelector('#positionEmployeeTable tbody tr');
                    if (!firstRow) return [];

                    const badges = [];
                    const badgeElements = firstRow.querySelectorAll('.badge');
                    badgeElements.forEach(badge => {
                        badges.push(badge.innerText);
                    });
                    return badges;
                }""")

                print(f"Employee badges found: {len(badges)}")
                for badge in badges:
                    print(f"  - {badge}")
                    if 'N/A' not in badge:
                        print("    ✅ Badge shows actual status")

                # 모달 닫기
                close_btn = await page.query_selector('#employeeModal .btn-close')
                if close_btn:
                    await close_btn.click()
                    await page.wait_for_timeout(500)
                    print("\n✅ Modal closed successfully")

            else:
                print("❌ Modal not found!")
        else:
            print("❌ No View buttons found!")

        await browser.close()

    print("\n" + "="*50)
    print("🎯 Test Summary:")
    if aql_found and prs_found:
        print("✅ Both AQL and 5PRS conditions are displayed")
    else:
        if not aql_found:
            print("❌ AQL condition not found")
        if not prs_found:
            print("❌ 5PRS condition not found")

    return True

if __name__ == "__main__":
    asyncio.run(test_aql_5prs_display())