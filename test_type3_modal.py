#!/usr/bin/env python3
"""Test TYPE-3 employee Individual Details modal"""

import asyncio
from playwright.async_api import async_playwright
import os
import json

async def test_type3_modal():
    """Test TYPE-3 employee Individual Details modal display"""

    html_path = os.path.join(os.getcwd(), 'output_files', 'Incentive_Dashboard_2025_09_Version_6.html')

    if not os.path.exists(html_path):
        print(f"❌ Dashboard file not found: {html_path}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("📂 Loading dashboard...")
        await page.goto(f'file://{html_path}')
        await page.wait_for_timeout(2000)

        # Navigate to Individual Details tab
        print("\n[1] Navigating to Individual Details tab...")
        await page.click('#tabIndividual')
        await page.wait_for_timeout(1000)

        # Find TYPE-3 employees
        print("\n[2] Finding TYPE-3 employees...")

        # Get all rows with TYPE-3 that also have a Details button (actual employee rows)
        type3_rows = await page.locator('tr:has(td:text-is("TYPE-3")):has(button:has-text("Details"))').all()

        if not type3_rows:
            print("❌ No TYPE-3 employees found")
            # Try to get any TYPE-3 rows for debugging
            debug_rows = await page.locator('tr:has-text("TYPE-3")').all()
            print(f"   Debug: Found {len(debug_rows)} rows with TYPE-3 text")
            await browser.close()
            return

        print(f"   Found {len(type3_rows)} TYPE-3 employees")

        # Test first TYPE-3 employee
        print("\n[3] Testing first TYPE-3 employee...")
        first_type3 = type3_rows[0]

        # Get employee info
        emp_id = await first_type3.locator('td:nth-child(1)').text_content()
        emp_name = await first_type3.locator('td:nth-child(2)').text_content()
        print(f"   Employee: {emp_id} - {emp_name}")

        # Click Details button
        details_button = first_type3.locator('button.btn-primary')
        await details_button.click()
        await page.wait_for_timeout(1500)

        # Check modal content
        print("\n[4] Checking modal content...")

        # Get incentive amount
        incentive_text = await page.locator('#modalIncentiveAmount').text_content()
        print(f"   Incentive Amount: {incentive_text}")

        # Get condition fulfillment percentage
        fulfillment_text = await page.locator('#modalConditionFulfillment').text_content()
        print(f"   Condition Fulfillment: {fulfillment_text}")

        # Get policy excluded message
        excluded_message_elem = await page.locator('text=Policy Excluded').count()
        if excluded_message_elem > 0:
            print("   ✅ 'Policy Excluded' message found")
        else:
            excluded_message_elem = await page.locator('text=정책제외').count()
            if excluded_message_elem > 0:
                print("   ✅ '정책제외' message found (Korean)")
            else:
                print("   ⚠️ No 'Policy Excluded' message found")

        # Check chart display
        print("\n[5] Checking chart display...")
        chart_canvas = await page.locator('#conditionChart').is_visible()
        if chart_canvas:
            print("   ✅ Chart is visible")

            # Check if chart shows N/A
            chart_title = await page.locator('.modal-body:has(#conditionChart) h5').text_content()
            print(f"   Chart title: {chart_title}")
        else:
            print("   ❌ Chart not visible")

        # Get condition details
        print("\n[6] Checking condition details...")
        condition_rows = await page.locator('#employeeConditionDetails tr').all()

        for i, row in enumerate(condition_rows[:5], 1):  # Check first 5 conditions
            condition = await row.locator('td:nth-child(1)').text_content()
            status = await row.locator('td:nth-child(2) .badge').text_content()
            print(f"   Condition {i}: {status}")

        # Close modal
        close_button = await page.locator('.modal:visible button.btn-close').first
        if close_button:
            await close_button.click()
            await page.wait_for_timeout(1000)

        # Summary
        print("\n" + "="*50)
        print("📊 Test Results:")
        print("="*50)

        issues = []

        # Check incentive amount
        if '0 VND' in incentive_text or '0' == incentive_text.replace(' VND', '').strip():
            print("✅ Incentive amount correctly shows 0 VND")
        else:
            issues.append(f"❌ Incentive amount unexpected: {incentive_text}")

        # Check condition fulfillment
        if 'N/A' in fulfillment_text or '해당없음' in fulfillment_text:
            print("✅ Condition fulfillment correctly shows N/A")
        elif '0%' in fulfillment_text:
            print("⚠️ Condition fulfillment shows 0% (should be N/A)")
            issues.append("Condition fulfillment should show N/A, not 0%")
        elif '100%' in fulfillment_text:
            issues.append("❌ Condition fulfillment incorrectly shows 100%")
        else:
            print(f"⚠️ Unexpected fulfillment text: {fulfillment_text}")

        if issues:
            print("\n🚨 Issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n🎉 TYPE-3 modal display working correctly!")

        print("\n💡 Browser will stay open for manual verification...")
        await page.wait_for_timeout(30000)  # Keep browser open for 30 seconds

        await browser.close()

if __name__ == "__main__":
    print("="*50)
    print("🔍 Testing TYPE-3 Employee Modal")
    print("="*50)
    asyncio.run(test_type3_modal())