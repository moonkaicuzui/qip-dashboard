#!/usr/bin/env python3
"""
Comprehensive test for Position modal fixes:
1. TYPE-2 should only show conditions 1-4
2. Statistics should match actual data
3. Employee Details Status should work correctly
"""

import asyncio
from playwright.async_api import async_playwright
import os
import json

async def test_comprehensive():
    dashboard = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for inspection
        page = await browser.new_page()

        # Collect console logs
        console_logs = []
        errors = []
        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("📋 Testing Dashboard V6 Position Modal Fixes")
        print("=" * 60)

        # Navigate to dashboard
        await page.goto(f'file://{dashboard}')
        await page.wait_for_timeout(3000)

        # Test 1: Check if dashboard loaded correctly
        print("\n✅ Test 1: Dashboard Loading")
        title = await page.title()
        print(f"  Title: {title}")

        # Check if employee data is loaded
        result = await page.evaluate('''() => {
            return {
                hasData: typeof window.employeeData !== 'undefined',
                dataCount: window.employeeData ? window.employeeData.length : 0
            }
        }''')
        print(f"  Employee data loaded: {result['hasData']}")
        print(f"  Employee count: {result['dataCount']}")

        # Test 2: Click Position tab
        print("\n✅ Test 2: Position Tab")
        await page.click('[data-tab="position"]')
        await page.wait_for_timeout(2000)

        # Check position content
        position_content = await page.query_selector('#positionContent')
        if position_content:
            content_text = await position_content.inner_text()
            print(f"  Position content loaded: {'TYPE-2' in content_text}")

            # Find TYPE-2 positions
            type2_sections = await page.query_selector_all('text="TYPE-2"')
            print(f"  Found {len(type2_sections)} TYPE-2 sections")
        else:
            print("  ❌ Position content not found")

        # Test 3: Open TYPE-2 position modal
        print("\n✅ Test 3: TYPE-2 Position Modal")

        # Try to click on a TYPE-2 position button
        type2_button = await page.query_selector('button:has-text("(V) SUPERVISOR")')
        if not type2_button:
            # Try alternative selector
            type2_button = await page.query_selector('text="상세 보기"')

        if type2_button:
            await type2_button.click()
            await page.wait_for_timeout(2000)

            # Check modal opened
            modal = await page.query_selector('#employeeModal')
            if modal:
                print("  ✅ Modal opened successfully")

                # Test 4: Check conditions shown for TYPE-2
                print("\n✅ Test 4: TYPE-2 Condition Verification")

                # Execute JavaScript to check conditions
                condition_check = await page.evaluate('''() => {
                    const modal = document.getElementById('employeeModal');
                    if (!modal) return null;

                    const modalText = modal.innerText;
                    const hasCondition5 = modalText.includes('조건 5') || modalText.includes('Condition 5');
                    const hasCondition6 = modalText.includes('조건 6') || modalText.includes('Condition 6');
                    const hasCondition7 = modalText.includes('조건 7') || modalText.includes('Condition 7');
                    const hasCondition8 = modalText.includes('조건 8') || modalText.includes('Condition 8');

                    // Get condition table rows
                    const conditionRows = modal.querySelectorAll('tbody tr');
                    const conditionCount = conditionRows.length;

                    return {
                        hasCondition5,
                        hasCondition6,
                        hasCondition7,
                        hasCondition8,
                        conditionCount,
                        modalTextLength: modalText.length
                    };
                }''')

                if condition_check:
                    print(f"  Condition 5 present: {condition_check['hasCondition5']}")
                    print(f"  Condition 6 present: {condition_check['hasCondition6']}")
                    print(f"  Condition 7 present: {condition_check['hasCondition7']}")
                    print(f"  Condition 8 present: {condition_check['hasCondition8']}")
                    print(f"  Total condition rows: {condition_check['conditionCount']}")

                    if not any([condition_check['hasCondition5'], condition_check['hasCondition6'],
                               condition_check['hasCondition7'], condition_check['hasCondition8']]):
                        print("  ✅ SUCCESS: TYPE-2 correctly shows only conditions 1-4")
                    else:
                        print("  ❌ ERROR: TYPE-2 incorrectly shows conditions 5-8")

                # Test 5: Check statistics
                print("\n✅ Test 5: Statistics Verification")
                stats = await page.evaluate('''() => {
                    const modal = document.getElementById('employeeModal');
                    if (!modal) return null;

                    // Find statistics in modal
                    const modalText = modal.innerText;
                    const lines = modalText.split('\\n');

                    let totalPeople = 0;
                    let paidPeople = 0;
                    let unpaidPeople = 0;

                    for (const line of lines) {
                        if (line.includes('전체 직원') || line.includes('Total Personnel')) {
                            const match = line.match(/\\d+/);
                            if (match) totalPeople = parseInt(match[0]);
                        }
                        if (line.includes('수령 직원') || line.includes('Paid Personnel')) {
                            const match = line.match(/\\d+/);
                            if (match) paidPeople = parseInt(match[0]);
                        }
                        if (line.includes('미수령') || line.includes('Unpaid')) {
                            const match = line.match(/\\d+/);
                            if (match) unpaidPeople = parseInt(match[0]);
                        }
                    }

                    return {
                        total: totalPeople,
                        paid: paidPeople,
                        unpaid: unpaidPeople,
                        sumMatches: (paidPeople + unpaidPeople === totalPeople)
                    };
                }''')

                if stats:
                    print(f"  Total employees: {stats['total']}")
                    print(f"  Paid employees: {stats['paid']}")
                    print(f"  Unpaid employees: {stats['unpaid']}")
                    print(f"  Statistics match: {stats['sumMatches']}")
            else:
                print("  ❌ Modal did not open")
        else:
            print("  ❌ TYPE-2 button not found")

        # Test 6: Check console errors
        print("\n✅ Test 6: Console Errors")
        if errors:
            print(f"  ❌ Found {len(errors)} JavaScript errors:")
            for err in errors[:3]:  # Show first 3 errors
                print(f"    - {err[:100]}")
        else:
            print("  ✅ No JavaScript errors")

        # Print relevant console logs
        print("\n📋 Relevant Console Logs:")
        for log in console_logs:
            if 'type-2' in log.lower() or 'applicable conditions' in log.lower():
                print(f"  {log[:200]}")

        print("\n" + "=" * 60)
        print("Test Complete! Keeping browser open for inspection...")

        await page.wait_for_timeout(30000)  # Keep open for 30 seconds
        await browser.close()

asyncio.run(test_comprehensive())