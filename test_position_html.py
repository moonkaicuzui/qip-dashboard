#!/usr/bin/env python3
"""Check the actual HTML structure in Position tab"""

import asyncio
from playwright.async_api import async_playwright
import os

async def test_position_html():
    dashboard = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(f'file://{dashboard}')
        await page.wait_for_timeout(2000)

        # Click Position tab
        await page.click('[data-tab="position"]')
        await page.wait_for_timeout(2000)

        # Get the HTML content of the position tab
        position_html = await page.evaluate('''() => {
            const positionContent = document.getElementById('positionContent');
            return positionContent ? positionContent.innerHTML : 'NOT FOUND';
        }''')

        print("Position Tab HTML Structure:")
        print("=" * 60)

        # Extract first 2000 characters to see structure
        if position_html != 'NOT FOUND':
            # Look for buttons and onclick handlers
            import re
            buttons = re.findall(r'<button[^>]*>.*?</button>', position_html[:5000])
            print(f"Found {len(buttons)} buttons")
            for i, btn in enumerate(buttons[:3]):
                print(f"Button {i+1}: {btn[:150]}")

            # Look for onclick handlers
            onclicks = re.findall(r'onclick="([^"]*)"', position_html[:5000])
            print(f"\nFound {len(onclicks)} onclick handlers")
            for i, onclick in enumerate(onclicks[:3]):
                print(f"Onclick {i+1}: {onclick}")

            # Check for showPositionDetail function
            has_function = 'showPositionDetail' in position_html
            print(f"\nHas showPositionDetail function: {has_function}")
        else:
            print("Position content not found!")

        # Try clicking using JavaScript directly
        print("\n" + "=" * 60)
        print("Attempting direct JavaScript click on TYPE-2 position...")

        result = await page.evaluate('''() => {
            // Find TYPE-2 positions
            const cards = document.querySelectorAll('.position-card');
            for (const card of cards) {
                const text = card.innerText;
                if (text.includes('TYPE-2') && text.includes('SUPERVISOR')) {
                    // Try to find and click button
                    const btn = card.querySelector('button');
                    if (btn) {
                        btn.click();
                        return 'Clicked TYPE-2 SUPERVISOR button';
                    }
                }
            }

            // Alternative: try calling function directly
            if (typeof window.showPositionDetail === 'function') {
                window.showPositionDetail('TYPE-2', '(V) SUPERVISOR');
                return 'Called showPositionDetail directly';
            }

            return 'No TYPE-2 position found or function not available';
        }''')

        print(f"Result: {result}")

        await page.wait_for_timeout(2000)

        # Check if modal opened
        modal_exists = await page.evaluate('''() => {
            const modal = document.getElementById('employeeModal');
            return modal !== null;
        }''')

        print(f"Modal opened: {modal_exists}")

        if modal_exists:
            # Get modal content for TYPE-2
            modal_info = await page.evaluate('''() => {
                const modal = document.getElementById('employeeModal');
                const modalText = modal.innerText;

                // Count conditions
                let conditionCount = 0;
                for (let i = 1; i <= 10; i++) {
                    if (modalText.includes('조건 ' + i) || modalText.includes('Condition ' + i)) {
                        conditionCount++;
                    }
                }

                return {
                    totalLength: modalText.length,
                    conditionCount: conditionCount,
                    hasCondition5: modalText.includes('조건 5') || modalText.includes('Condition 5'),
                    hasCondition6: modalText.includes('조건 6') || modalText.includes('Condition 6'),
                    hasCondition7: modalText.includes('조건 7') || modalText.includes('Condition 7'),
                    hasCondition8: modalText.includes('조건 8') || modalText.includes('Condition 8')
                };
            }''')

            print("\nModal Analysis:")
            print(f"  Total conditions shown: {modal_info['conditionCount']}")
            print(f"  Has condition 5-8: {any([modal_info['hasCondition5'], modal_info['hasCondition6'], modal_info['hasCondition7'], modal_info['hasCondition8']])}")

            if modal_info['conditionCount'] <= 4:
                print("  ✅ SUCCESS: TYPE-2 correctly showing only conditions 1-4")
            else:
                print("  ❌ ERROR: TYPE-2 showing too many conditions")

        await page.wait_for_timeout(10000)
        await browser.close()

asyncio.run(test_position_html())