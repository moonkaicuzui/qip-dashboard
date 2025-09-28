#!/usr/bin/env python3
"""Test Previous Month Incentive Display"""

import asyncio
from playwright.async_api import async_playwright
import os

async def test_prev_month():
    """Test that previous month incentive shows correctly"""

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

        # Check if the previous month column shows august
        print("\n[2] Checking previous month column header...")

        # Get the previous month header text
        prev_month_header = await page.locator('#prevMonthHeader').text_content()
        print(f"   Previous Month Header: '{prev_month_header}'")

        # Get any employee's previous month incentive in the summary table
        print("\n[3] Checking previous month incentive in summary table...")

        # Find first few rows and check their previous month values
        rows = await page.locator('#individualSummaryTable tbody tr').all()

        if rows:
            for i in range(min(3, len(rows))):  # Check first 3 rows
                row = rows[i]
                cells = await row.locator('td').all()
                if len(cells) >= 5:  # Should have at least 5 columns
                    name = await cells[0].text_content()
                    prev_month_value = await cells[3].text_content()  # 4th column is previous month
                    print(f"   Row {i+1}: {name} - Previous month: {prev_month_value}")

        # Test opening a modal to check previous month display
        print("\n[4] Opening individual employee modal...")

        # Click on first Details button
        details_buttons = await page.locator('button:has-text("Details")').all()
        if details_buttons:
            await details_buttons[0].click()
            await page.wait_for_timeout(1500)

            # Check for previous month incentive in modal
            modal_text = await page.locator('.modal-body').text_content()

            # Look for "Last month" or similar text
            if '이전 월' in modal_text or 'Last month' in modal_text or 'Tháng trước' in modal_text:
                print("   ✅ Previous month text found in modal")

                # Extract the actual incentive value
                import re
                # Pattern to find VND amounts
                vnd_pattern = r'(\d{1,3}(?:,\d{3})*)\s*VND'
                matches = re.findall(vnd_pattern, modal_text)
                if len(matches) >= 2:  # Should have current and previous
                    print(f"   Previous month incentive value found: {matches[-1]} VND")
                else:
                    print(f"   Found {len(matches)} VND values in modal")
            else:
                print("   ⚠️ No previous month text found in modal")

            # Close modal
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(500)

        # Summary
        print("\n" + "="*50)
        print("📊 Test Results:")
        print("="*50)

        issues = []

        # Check if header shows correct month
        expected_months = ['8월', 'August', 'Tháng 8']  # August in Korean, English, Vietnamese
        if not any(month in prev_month_header for month in expected_months):
            issues.append(f"Previous month header doesn't show August: '{prev_month_header}'")
        else:
            print(f"✅ Previous month header correctly shows August")

        if issues:
            print("\n🚨 Issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n🎉 Previous month incentive display working correctly!")

        # Also check in JavaScript console
        print("\n[5] Checking JavaScript data...")
        result = await page.evaluate("""
            () => {
                if (typeof employeeData !== 'undefined' && employeeData.length > 0) {
                    const emp = employeeData[0];
                    const keys = Object.keys(emp);
                    const incentiveKeys = keys.filter(k => k.includes('_incentive'));
                    return {
                        totalEmployees: employeeData.length,
                        firstEmployee: emp.name || emp.Full_Name,
                        incentiveKeys: incentiveKeys,
                        augustIncentive: emp.august_incentive,
                        previousIncentive: emp.previous_incentive
                    };
                }
                return null;
            }
        """)

        if result:
            print(f"\n   JavaScript data check:")
            print(f"   - Total employees: {result['totalEmployees']}")
            print(f"   - First employee: {result['firstEmployee']}")
            print(f"   - Incentive keys found: {result['incentiveKeys']}")
            print(f"   - August incentive: {result['augustIncentive']}")
            print(f"   - Previous incentive: {result['previousIncentive']}")

        print("\n💡 Browser will stay open for manual verification...")
        await page.wait_for_timeout(30000)  # Keep browser open for 30 seconds

        await browser.close()

if __name__ == "__main__":
    print("="*50)
    print("🔍 Testing Previous Month Incentive Display")
    print("="*50)
    asyncio.run(test_prev_month())