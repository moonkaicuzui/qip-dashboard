#!/usr/bin/env python3
"""
Visual test using Playwright to verify ASSEMBLY team count consistency in the dashboard.
This test interacts with the actual dashboard UI to confirm all components show 109.
"""

import asyncio
from pathlib import Path
import sys
import os

# Try to import Playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("⚠️ Playwright not installed. Installing...")
    os.system("pip install playwright")
    os.system("playwright install chromium")
    from playwright.async_api import async_playwright

async def test_assembly_counts():
    """Test ASSEMBLY team counts across all dashboard components."""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Load the dashboard
        dashboard_path = Path.cwd() / "output_files" / "management_dashboard_2025_08.html"
        await page.goto(f"file://{dashboard_path}")
        
        print("=" * 70)
        print("ASSEMBLY Team Visual Verification with Playwright")
        print("=" * 70)
        
        # Expected count after fix
        EXPECTED_COUNT = 109
        issues = []
        
        # Wait for dashboard to load
        await page.wait_for_timeout(2000)
        
        # 1. Check ASSEMBLY card
        print("\n📊 Checking ASSEMBLY Team Card...")
        assembly_card = await page.query_selector('div.team-card:has-text("ASSEMBLY")')
        if assembly_card:
            # Find the total count in the card
            card_text = await assembly_card.text_content()
            print(f"  Card content: {card_text[:100]}...")
            
            # Look for total number
            import re
            total_match = re.search(r'총원:\s*(\d+)명', card_text)
            if total_match:
                card_total = int(total_match.group(1))
                print(f"  Card total: {card_total}")
                if card_total != EXPECTED_COUNT:
                    issues.append(f"Card shows {card_total} instead of {EXPECTED_COUNT}")
            
            # Click to open modal
            await assembly_card.click()
            await page.wait_for_timeout(1000)
            
            # Check modal content
            modal = await page.query_selector('div.modal.show')
            if modal:
                modal_text = await modal.text_content()
                
                # Check monthly trend value
                trend_match = re.search(r'8월:\s*(\d+)명', modal_text)
                if trend_match:
                    trend_count = int(trend_match.group(1))
                    print(f"  Modal trend count: {trend_count}")
                    if trend_count != EXPECTED_COUNT:
                        issues.append(f"Modal trend shows {trend_count} instead of {EXPECTED_COUNT}")
                
                # Check table footer total
                table_total = await page.query_selector('div.modal.show table tfoot td:nth-child(2)')
                if table_total:
                    total_text = await table_total.text_content()
                    try:
                        table_count = int(total_text)
                        print(f"  Table total: {table_count}")
                        if table_count != EXPECTED_COUNT:
                            issues.append(f"Table shows {table_count} instead of {EXPECTED_COUNT}")
                    except ValueError:
                        pass
                
                # Close modal
                close_btn = await page.query_selector('button.close')
                if close_btn:
                    await close_btn.click()
                    await page.wait_for_timeout(500)
        
        # 2. Check console for JavaScript data
        print("\n🔍 Checking JavaScript Data...")
        
        # Execute JavaScript to get teamStats
        team_stats_assembly = await page.evaluate('''() => {
            if (typeof teamStats !== 'undefined' && teamStats.ASSEMBLY) {
                return teamStats.ASSEMBLY.total;
            }
            return null;
        }''')
        
        if team_stats_assembly:
            print(f"  JavaScript teamStats: {team_stats_assembly}")
            if team_stats_assembly != EXPECTED_COUNT:
                issues.append(f"JavaScript teamStats shows {team_stats_assembly} instead of {EXPECTED_COUNT}")
        
        # Get role distribution sum
        role_sum = await page.evaluate('''() => {
            if (typeof roleData !== 'undefined' && roleData.ASSEMBLY) {
                const roles = roleData.ASSEMBLY;
                let sum = 0;
                for (let role in roles) {
                    sum += roles[role];
                }
                return sum;
            }
            return null;
        }''')
        
        if role_sum:
            print(f"  Role distribution sum: {role_sum}")
            if role_sum != EXPECTED_COUNT:
                issues.append(f"Role distribution sum is {role_sum} instead of {EXPECTED_COUNT}")
        
        # Take screenshot
        await page.screenshot(path="test_assembly_result.png", full_page=True)
        print("\n📸 Screenshot saved as test_assembly_result.png")
        
        # Results
        print("\n" + "=" * 70)
        if not issues:
            print("✅ SUCCESS: All ASSEMBLY counts are consistent at 109!")
            print("The position mapping conflict fix is working correctly in the UI.")
        else:
            print("❌ ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        
        await browser.close()
        return 0 if not issues else 1

async def main():
    """Main test runner."""
    try:
        return await test_assembly_counts()
    except Exception as e:
        print(f"❌ Test error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)