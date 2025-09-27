#!/usr/bin/env python3
"""Test Position modal after fixes"""

import asyncio
from playwright.async_api import async_playwright
import os
import json

async def test_position_modal():
    dashboard = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for testing
        page = await browser.new_page()

        # Collect console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))

        # Navigate to dashboard
        await page.goto(f'file://{dashboard}')
        await page.wait_for_timeout(2000)

        # Click Position tab
        await page.click('[data-tab="position"]')
        await page.wait_for_timeout(1000)

        # Find and click on TYPE-2 V SUPERVISOR
        # Look for the position element
        type2_positions = await page.query_selector_all('text="(V) SUPERVISOR"')
        if type2_positions:
            print(f"Found {len(type2_positions)} (V) SUPERVISOR position(s)")

            # Click on the first one to open modal
            await type2_positions[0].click()
            await page.wait_for_timeout(2000)

            # Check modal content
            modal = await page.query_selector('#employeeModal')
            if modal:
                print("✅ Position modal opened successfully")

                # Extract condition statistics from the modal
                condition_rows = await page.query_selector_all('#employeeModal tbody tr')
                print(f"\n📊 Condition Statistics in Modal:")
                print("=" * 50)

                for i, row in enumerate(condition_rows[:10], 1):  # First 10 rows should be conditions
                    row_text = await row.text_content()
                    print(f"Row {i}: {row_text}")

                # Check for TYPE-2 specific conditions (should only have 1-4)
                modal_content = await modal.inner_text()
                if "조건 5" in modal_content or "Condition 5" in modal_content:
                    print("\n❌ ERROR: TYPE-2 is showing condition 5 (AQL) which shouldn't apply!")
                else:
                    print("\n✅ SUCCESS: TYPE-2 correctly shows only conditions 1-4")

                # Look for the statistics
                stats_section = await page.query_selector('#employeeModal .modal-body')
                if stats_section:
                    # Get total/paid/unpaid counts
                    stats_text = await stats_section.inner_text()
                    lines = stats_text.split('\n')
                    for line in lines[:20]:  # First 20 lines to find statistics
                        if '명' in line or 'people' in line:
                            print(f"Stat: {line}")

            else:
                print("❌ Modal not found")
        else:
            print("❌ (V) SUPERVISOR position not found")

        # Print relevant console logs
        print("\n📋 Console logs related to conditions:")
        for log in console_logs:
            if 'condition' in log.lower() or 'type-2' in log.lower() or 'applicable' in log.lower():
                print(log)

        await page.wait_for_timeout(5000)  # Keep open for manual inspection
        await browser.close()

asyncio.run(test_position_modal())