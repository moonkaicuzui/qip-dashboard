#!/usr/bin/env python3
"""
대시보드 JavaScript 에러 및 데이터 로딩 문제 디버깅
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def debug_dashboard():
    """대시보드 디버깅"""

    # 가능한 대시보드 파일들 확인
    dashboard_files = [
        "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html",
        "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Dashboard_V6_Complete_2025_september.html",
        "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_5.html"
    ]

    import os
    dashboard_path = None
    for path in dashboard_files:
        if os.path.exists(path):
            dashboard_path = path
            print(f"✅ Found dashboard: {path}")
            break

    if not dashboard_path:
        print("❌ No dashboard file found!")
        return

    print("\n🔍 Starting dashboard debugging...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 콘솔 메시지 캡처
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            'type': msg.type,
            'text': msg.text,
            'location': f"{msg.location['url']}:{msg.location['lineNumber']}" if msg.location else "unknown"
        }))

        # 페이지 에러 캡처
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print(f"\n📄 Loading dashboard: {dashboard_path}")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(3000)

        # JavaScript 에러 확인
        print("\n🚨 JavaScript Errors:")
        print("-" * 50)
        if page_errors:
            for error in page_errors:
                print(f"❌ {error}")
        else:
            print("✅ No page errors")

        # 콘솔 에러 확인
        print("\n📋 Console Messages:")
        print("-" * 50)
        error_count = 0
        for msg in console_messages:
            if msg['type'] == 'error':
                print(f"❌ ERROR: {msg['text']}")
                print(f"   Location: {msg['location']}")
                error_count += 1
            elif msg['type'] == 'warning':
                print(f"⚠️ WARNING: {msg['text']}")

        if error_count == 0:
            print("✅ No console errors")

        # 데이터 확인
        print("\n📊 Data Check:")
        print("-" * 50)

        data_check = await page.evaluate("""() => {
            const result = {
                employeeData: null,
                translations: null,
                dashboardData: null,
                windowVariables: [],
                errors: []
            };

            // Check employeeData
            if (typeof employeeData !== 'undefined') {
                result.employeeData = {
                    exists: true,
                    length: Array.isArray(employeeData) ? employeeData.length : 0,
                    sample: Array.isArray(employeeData) && employeeData.length > 0 ? employeeData[0] : null
                };
            } else if (typeof window.employeeData !== 'undefined') {
                result.employeeData = {
                    exists: true,
                    length: Array.isArray(window.employeeData) ? window.employeeData.length : 0,
                    sample: Array.isArray(window.employeeData) && window.employeeData.length > 0 ? window.employeeData[0] : null
                };
            } else {
                result.employeeData = { exists: false };
                result.errors.push("employeeData not found");
            }

            // Check translations
            if (typeof translations !== 'undefined') {
                result.translations = { exists: true, languages: Object.keys(translations) };
            } else {
                result.translations = { exists: false };
                result.errors.push("translations not found");
            }

            // Check window variables
            for (let key in window) {
                if (key.includes('employee') || key.includes('dashboard') || key.includes('Data')) {
                    result.windowVariables.push(key);
                }
            }

            return result;
        }""")

        if data_check['employeeData']['exists']:
            print(f"✅ employeeData exists: {data_check['employeeData']['length']} employees")
            if data_check['employeeData']['sample']:
                sample = data_check['employeeData']['sample']
                print(f"   Sample employee type: {sample.get('type', 'N/A')}")
        else:
            print("❌ employeeData not found!")

        if data_check['translations']['exists']:
            print(f"✅ translations exists: {data_check['translations']['languages']}")
        else:
            print("❌ translations not found!")

        if data_check['windowVariables']:
            print(f"\n📦 Window variables found:")
            for var in data_check['windowVariables'][:10]:
                print(f"   - window.{var}")

        # 탭 기능 확인
        print("\n🔄 Tab Functionality Check:")
        print("-" * 50)

        tab_check = await page.evaluate("""() => {
            const tabs = document.querySelectorAll('.tab');
            const tabData = [];

            tabs.forEach(tab => {
                const tabName = tab.getAttribute('data-tab');
                const onclick = tab.getAttribute('onclick');
                tabData.push({
                    name: tabName,
                    text: tab.innerText,
                    hasOnclick: onclick !== null,
                    onclick: onclick
                });
            });

            // Check if showTab function exists
            const showTabExists = typeof showTab === 'function';

            return {
                tabs: tabData,
                showTabExists: showTabExists
            };
        }""")

        print(f"Tabs found: {len(tab_check['tabs'])}")
        for tab in tab_check['tabs']:
            print(f"  - {tab['text']} (data-tab={tab['name']})")
            if not tab['hasOnclick']:
                print(f"    ⚠️ No onclick handler!")

        if tab_check['showTabExists']:
            print("✅ showTab function exists")
        else:
            print("❌ showTab function not found!")

        # 요약 테이블 확인
        print("\n📊 Summary Table Check:")
        print("-" * 50)

        summary_check = await page.evaluate("""() => {
            const summaryBody = document.getElementById('typeSummaryBody');
            if (!summaryBody) {
                return { exists: false };
            }

            const rows = summaryBody.querySelectorAll('tr');
            return {
                exists: true,
                rowCount: rows.length,
                isEmpty: rows.length === 0,
                innerHTML: summaryBody.innerHTML.substring(0, 200)
            };
        }""")

        if summary_check['exists']:
            print(f"✅ Summary table exists")
            print(f"   Rows: {summary_check['rowCount']}")
            if summary_check['isEmpty']:
                print("   ⚠️ Table is empty!")
        else:
            print("❌ Summary table not found!")

        print("\n" + "="*60)
        print("🔍 Debugging Complete")
        print("="*60)

        print("\n⏸️ Browser will remain open for 30 seconds for manual inspection...")
        print("   Open Developer Console (F12) to see more details")

        await asyncio.sleep(30)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_dashboard())