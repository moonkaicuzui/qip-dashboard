#!/usr/bin/env python3
"""Debug Position tab and modal functionality"""

import asyncio
from playwright.async_api import async_playwright
import os

async def test_position_tab():
    dashboard = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Collect console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))

        # Navigate to dashboard
        await page.goto(f'file://{dashboard}')
        await page.wait_for_timeout(2000)

        # Click Position tab
        print("Clicking Position tab...")
        await page.click('[data-tab="position"]')
        await page.wait_for_timeout(1000)

        # Get all position cards
        position_cards = await page.query_selector_all('.position-card')
        print(f"Found {len(position_cards)} position cards")

        # Find TYPE-2 positions
        for card in position_cards:
            card_text = await card.inner_text()
            if 'TYPE-2' in card_text and 'SUPERVISOR' in card_text:
                print(f"\n📋 Found TYPE-2 card:\n{card_text[:200]}...")

                # Try clicking the view details button
                details_btn = await card.query_selector('button')
                if details_btn:
                    btn_text = await details_btn.inner_text()
                    print(f"Clicking button: {btn_text}")

                    await details_btn.click()
                    await page.wait_for_timeout(2000)

                    # Check if modal opened
                    modal = await page.query_selector('#employeeModal')
                    if modal:
                        print("✅ Modal opened!")

                        # Get modal content
                        modal_text = await modal.inner_text()

                        # Check conditions shown
                        lines = modal_text.split('\n')
                        print("\n📊 Modal Condition Information:")
                        for line in lines:
                            if '조건' in line or 'Condition' in line or '충족' in line or 'Fulfillment' in line:
                                print(f"  {line[:100]}")

                        # Look for condition numbers
                        if any(num in modal_text for num in ['조건 5', '조건 6', '조건 7', '조건 8', 'Condition 5', 'Condition 6', 'Condition 7', 'Condition 8']):
                            print("\n❌ ERROR: TYPE-2 showing conditions 5-8!")
                        else:
                            print("\n✅ SUCCESS: TYPE-2 only showing conditions 1-4")

                        break
                    else:
                        print("❌ Modal did not open")

        # Print debug console logs
        print("\n📋 Debug Console Logs:")
        for log in console_logs[-20:]:  # Last 20 logs
            if 'type' in log.lower() or 'condition' in log.lower() or 'modal' in log.lower():
                print(log)

        await page.wait_for_timeout(10000)  # Keep open for inspection
        await browser.close()

asyncio.run(test_position_tab())