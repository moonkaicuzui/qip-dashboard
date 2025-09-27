#!/usr/bin/env python3
"""
Version 6 Complete 대시보드 테스트
"""

import asyncio
from playwright.async_api import async_playwright

async def test_v6_complete():
    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Dashboard_V6_Complete_2025_september.html"

    print("🚀 Testing V6 Complete Dashboard...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 콘솔 에러 캡처
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("📄 Loading dashboard...")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(2000)

        # 에러 확인
        if errors:
            print("\n❌ JavaScript Errors found:")
            for err in errors[:3]:
                print(f"  - {err[:100]}")
        else:
            print("✅ No JavaScript errors")

        # 데이터 확인
        data = await page.evaluate("""() => ({
            employeeData: typeof employeeData !== 'undefined' ? employeeData.length : 0,
            tabs: document.querySelectorAll('.tab').length,
            summaryTable: document.querySelector('#typeSummaryBody')?.innerHTML.length || 0
        })""")

        print(f"\n📊 Data Check:")
        print(f"  Employees: {data['employeeData']}")
        print(f"  Tabs: {data['tabs']}")
        print(f"  Summary table: {'✅ Has content' if data['summaryTable'] > 0 else '❌ Empty'}")

        # 탭 클릭 테스트
        await page.click('div.tab[data-tab="position"]')
        await page.wait_for_timeout(1000)

        position_content = await page.query_selector('#positionContent')
        if position_content:
            html = await position_content.inner_html()
            if len(html) > 100:
                print("✅ Position tab works!")
            else:
                print("❌ Position tab empty")

        print("\n브라우저를 열어두고 있습니다...")
        await asyncio.sleep(30)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_v6_complete())