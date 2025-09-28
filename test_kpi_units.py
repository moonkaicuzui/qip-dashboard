#!/usr/bin/env python3
"""Test KPI unit translation in main dashboard"""

import asyncio
from playwright.async_api import async_playwright
import os

async def test_kpi_units():
    """Test main dashboard KPI unit translations"""

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

        # Test 1: Check initial Korean units
        print("\n[1] Korean language (default):")
        ko_total = await page.locator('#totalEmployeesUnit').text_content()
        ko_paid = await page.locator('#paidEmployeesUnit').text_content()
        print(f"   Total Employees Unit: '{ko_total}'")
        print(f"   Paid Employees Unit: '{ko_paid}'")

        # Test 2: Switch to English and check units
        print("\n[2] Switching to English...")
        await page.select_option('#languageSelector', 'en')
        await page.wait_for_timeout(1000)

        en_total = await page.locator('#totalEmployeesUnit').text_content()
        en_paid = await page.locator('#paidEmployeesUnit').text_content()
        print(f"   Total Employees Unit: '{en_total}'")
        print(f"   Paid Employees Unit: '{en_paid}'")

        # Test 3: Switch to Vietnamese and check units
        print("\n[3] Switching to Vietnamese...")
        await page.select_option('#languageSelector', 'vi')
        await page.wait_for_timeout(1000)

        vi_total = await page.locator('#totalEmployeesUnit').text_content()
        vi_paid = await page.locator('#paidEmployeesUnit').text_content()
        print(f"   Total Employees Unit: '{vi_total}'")
        print(f"   Paid Employees Unit: '{vi_paid}'")

        # Test 4: Switch back to Korean
        print("\n[4] Switching back to Korean...")
        await page.select_option('#languageSelector', 'ko')
        await page.wait_for_timeout(1000)

        ko_total2 = await page.locator('#totalEmployeesUnit').text_content()
        ko_paid2 = await page.locator('#paidEmployeesUnit').text_content()
        print(f"   Total Employees Unit: '{ko_total2}'")
        print(f"   Paid Employees Unit: '{ko_paid2}'")

        # Summary
        print("\n" + "="*50)
        print("📊 Test Results:")
        print("="*50)

        issues = []

        # Check Korean units
        if ko_total != '명' or ko_paid != '명':
            issues.append("❌ Korean units not showing '명'")
        else:
            print("✅ Korean units correct: '명'")

        # Check English units
        if ' people' not in en_total or ' people' not in en_paid:
            issues.append(f"❌ English units not showing ' people' (got: '{en_total}', '{en_paid}')")
        else:
            print("✅ English units correct: ' people'")

        # Check Vietnamese units
        if ' người' not in vi_total or ' người' not in vi_paid:
            issues.append(f"❌ Vietnamese units not showing ' người' (got: '{vi_total}', '{vi_paid}')")
        else:
            print("✅ Vietnamese units correct: ' người'")

        # Check consistency
        if ko_total != ko_total2 or ko_paid != ko_paid2:
            issues.append("❌ Korean units changed after switching back")
        else:
            print("✅ Language switching consistent")

        if issues:
            print("\n🚨 Issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n🎉 All KPI unit translations working correctly!")

        print("\n💡 Browser will stay open for manual verification...")
        await page.wait_for_timeout(30000)  # Keep browser open for 30 seconds

        await browser.close()

if __name__ == "__main__":
    print("="*50)
    print("🔍 Testing KPI Unit Translation")
    print("="*50)
    asyncio.run(test_kpi_units())