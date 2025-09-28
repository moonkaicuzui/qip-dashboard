#!/usr/bin/env python3
"""Test Incentive Criteria tab translations"""

import asyncio
from playwright.async_api import async_playwright
import os

async def test_criteria_translation():
    """Test that Incentive Criteria tab translates correctly"""

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

        # Navigate to Incentive Criteria tab
        print("\n[1] Navigating to Incentive Criteria tab...")
        await page.click('#tabCriteria')
        await page.wait_for_timeout(1000)

        # Test 1: Check initial Korean text
        print("\n[2] Korean language (default):")
        ko_title = await page.locator('#criteriaMainTitle').text_content()
        ko_th_name = await page.locator('.cond-th-name').first.text_content()
        ko_cond1 = await page.locator('.cond-name-1').text_content()
        ko_desc1 = await page.locator('.cond-desc-1').text_content()

        print(f"   Main Title: '{ko_title}'")
        print(f"   Table Header: '{ko_th_name}'")
        print(f"   Condition 1 Name: '{ko_cond1}'")
        print(f"   Condition 1 Desc: '{ko_desc1[:50]}...'")

        # Test 2: Switch to English and check
        print("\n[3] Switching to English...")
        await page.select_option('#languageSelector', 'en')
        await page.wait_for_timeout(1000)

        en_title = await page.locator('#criteriaMainTitle').text_content()
        en_th_name = await page.locator('.cond-th-name').first.text_content()
        en_cond1 = await page.locator('.cond-name-1').text_content()
        en_desc1 = await page.locator('.cond-desc-1').text_content()

        print(f"   Main Title: '{en_title}'")
        print(f"   Table Header: '{en_th_name}'")
        print(f"   Condition 1 Name: '{en_cond1}'")
        print(f"   Condition 1 Desc: '{en_desc1[:50]}...'")

        # Test 3: Switch to Vietnamese and check
        print("\n[4] Switching to Vietnamese...")
        await page.select_option('#languageSelector', 'vi')
        await page.wait_for_timeout(1000)

        vi_title = await page.locator('#criteriaMainTitle').text_content()
        vi_th_name = await page.locator('.cond-th-name').first.text_content()
        vi_cond1 = await page.locator('.cond-name-1').text_content()
        vi_desc1 = await page.locator('.cond-desc-1').text_content()

        print(f"   Main Title: '{vi_title}'")
        print(f"   Table Header: '{vi_th_name}'")
        print(f"   Condition 1 Name: '{vi_cond1}'")
        print(f"   Condition 1 Desc: '{vi_desc1[:50]}...'")

        # Check for Notes section
        print("\n[5] Checking for Notes section...")
        notes_sections = await page.locator('text=Notes').count() + await page.locator('text=참고').count() + await page.locator('text=Ghi chú').count()
        print(f"   Found {notes_sections} Notes sections")

        # Check all 10 conditions
        print("\n[6] Checking all 10 conditions translation...")
        await page.select_option('#languageSelector', 'en')
        await page.wait_for_timeout(1000)

        all_translated = True
        for i in range(1, 11):
            cond_name_selector = f'.cond-name-{i}'
            cond_desc_selector = f'.cond-desc-{i}'

            try:
                name = await page.locator(cond_name_selector).text_content()
                desc = await page.locator(cond_desc_selector).text_content()

                # Check if still Korean
                if any(korean in name for korean in ['출근', '무단', '실제', '최소', '개인', '팀', '통과', '검사']):
                    print(f"   ❌ Condition {i} name still in Korean: '{name}'")
                    all_translated = False
                else:
                    print(f"   ✅ Condition {i} name translated: '{name}'")

            except:
                print(f"   ⚠️ Could not find condition {i}")

        # Summary
        print("\n" + "="*50)
        print("📊 Test Results:")
        print("="*50)

        issues = []

        # Check if main title changes
        if ko_title == en_title:
            issues.append("Main title doesn't change when switching to English")
        else:
            print("✅ Main title translates correctly")

        # Check if table headers change
        if ko_th_name == en_th_name:
            issues.append("Table headers don't change when switching to English")
        else:
            print("✅ Table headers translate correctly")

        # Check if condition names change
        if ko_cond1 == en_cond1:
            issues.append("Condition names don't change when switching to English")
        else:
            print("✅ Condition names translate correctly")

        # Check all conditions
        if not all_translated:
            issues.append("Some conditions not fully translated")
        else:
            print("✅ All 10 conditions translate correctly")

        if issues:
            print("\n🚨 Issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n🎉 Incentive Criteria tab translations working correctly!")

        print("\n💡 Browser will stay open for manual verification...")
        await page.wait_for_timeout(30000)  # Keep browser open for 30 seconds

        await browser.close()

if __name__ == "__main__":
    print("="*50)
    print("🔍 Testing Incentive Criteria Tab Translations")
    print("="*50)
    asyncio.run(test_criteria_translation())