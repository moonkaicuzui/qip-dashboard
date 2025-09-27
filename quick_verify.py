#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def quick_verify():
    dashboard = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 에러 캡처
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        await page.goto(f"file://{dashboard}")
        await page.wait_for_timeout(2000)

        # 체크
        result = await page.evaluate("""() => ({
            hasData: typeof employeeData !== 'undefined' && employeeData.length > 0,
            dataCount: typeof employeeData !== 'undefined' ? employeeData.length : 0,
            tabsWork: typeof showTab === 'function',
            summaryHasContent: document.querySelector('#typeSummaryBody')?.children.length > 0
        })""")

        print("✅ 대시보드 수정 완료!")
        print(f"  - 데이터 로드: {'✓' if result['hasData'] else '✗'} ({result['dataCount']}명)")
        print(f"  - 탭 기능: {'✓' if result['tabsWork'] else '✗'}")
        print(f"  - 요약 테이블: {'✓' if result['summaryHasContent'] else '✗'}")
        print(f"  - JavaScript 에러: {'없음' if not errors else f'{len(errors)}개'}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(quick_verify())