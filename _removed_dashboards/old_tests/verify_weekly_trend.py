#!/usr/bin/env python3
"""
Verify that the ASSEMBLY team weekly trend shows consistent 109 members.
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

async def verify_weekly_trend():
    """Verify ASSEMBLY team weekly trend chart."""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Load the dashboard
        dashboard_path = Path.cwd() / "output_files" / "management_dashboard_2025_08.html"
        await page.goto(f"file://{dashboard_path}")
        
        print("=" * 70)
        print("ASSEMBLY Team Weekly Trend Verification")
        print("=" * 70)
        
        # Wait for dashboard to load
        await page.wait_for_timeout(2000)
        
        # 1. Find and click ASSEMBLY card to open modal
        print("\n📊 Opening ASSEMBLY Team Modal...")
        assembly_card = await page.query_selector('div.team-card:has-text("ASSEMBLY")')
        if assembly_card:
            await assembly_card.click()
            await page.wait_for_timeout(1500)
            
            # Check if modal is open
            modal = await page.query_selector('div.modal.show')
            if modal:
                print("  ✅ Modal opened successfully")
                
                # Get weekly trend canvas data
                weekly_data = await page.evaluate('''() => {
                    const canvas = document.getElementById('team-weekly-trend-ASSEMBLY');
                    if (canvas && canvas.chart) {
                        const chart = canvas.chart;
                        return {
                            labels: chart.data.labels,
                            data: chart.data.datasets[0].data
                        };
                    }
                    
                    // Try to find the chart instance another way
                    for (let id in Chart.instances) {
                        const chart = Chart.instances[id];
                        if (chart.canvas.id === 'team-weekly-trend-ASSEMBLY') {
                            return {
                                labels: chart.data.labels,
                                data: chart.data.datasets[0].data
                            };
                        }
                    }
                    return null;
                }''')
                
                if weekly_data:
                    print("\n📈 Weekly Trend Data:")
                    for i, label in enumerate(weekly_data['labels']):
                        count = weekly_data['data'][i]
                        print(f"  {label}: {count}명")
                        
                    # Check consistency
                    week4_count = weekly_data['data'][3]  # 4주차 데이터
                    if week4_count == 109:
                        print("\n✅ SUCCESS: Week 4 shows correct count of 109!")
                    else:
                        print(f"\n❌ ISSUE: Week 4 shows {week4_count} instead of 109")
                else:
                    print("  ⚠️ Could not retrieve weekly trend data")
                
                # Take screenshot of modal
                await page.screenshot(path="assembly_modal_weekly_trend.png", full_page=False)
                print("\n📸 Screenshot saved as assembly_modal_weekly_trend.png")
                
                # Close modal
                close_btn = await page.query_selector('button.close')
                if close_btn:
                    await close_btn.click()
            else:
                print("  ❌ Modal did not open")
        else:
            print("  ❌ ASSEMBLY card not found")
        
        await browser.close()

async def main():
    """Main test runner."""
    try:
        await verify_weekly_trend()
        return 0
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)