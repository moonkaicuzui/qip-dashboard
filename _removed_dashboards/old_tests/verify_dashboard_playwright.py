"""
Playwright test to verify dashboard fixes
"""

import asyncio
import json
from pathlib import Path

# Test configuration
DASHBOARD_PATH = Path("output_files/management_dashboard_2025_08.html")
TEAM_NAME = "ASSEMBLY"

async def verify_dashboard():
    """Verify dashboard components are working correctly"""
    
    print("=" * 60)
    print("Dashboard Verification with Playwright")
    print("=" * 60)
    
    # Load the dashboard
    dashboard_url = f"file://{DASHBOARD_PATH.absolute()}"
    print(f"\n📁 Opening dashboard: {dashboard_url}")
    
    # Navigate to the dashboard
    await page.goto(dashboard_url)
    await page.wait_for_load_state('networkidle')
    print("✅ Dashboard loaded")
    
    # Wait for the page to fully render
    await page.wait_for_timeout(2000)
    
    # Take initial screenshot
    await page.screenshot(path="output_files/dashboard_initial.png", full_page=False)
    print("📸 Initial screenshot saved")
    
    # Find and click on ASSEMBLY team card
    print(f"\n🎯 Looking for {TEAM_NAME} team card...")
    assembly_card = await page.query_selector(f"text={TEAM_NAME}")
    
    if assembly_card:
        print(f"✅ Found {TEAM_NAME} team card")
        
        # Click to open team details modal
        await assembly_card.click()
        print(f"🖱️ Clicked on {TEAM_NAME} team")
        
        # Wait for modal to appear
        await page.wait_for_timeout(1500)
        
        # Check if modal is visible
        modal = await page.query_selector("#team-detail-modal")
        if modal:
            print("✅ Team detail modal opened")
            
            # Take screenshot of modal
            await page.screenshot(path="output_files/team_modal.png", full_page=False)
            print("📸 Team modal screenshot saved")
            
            # Verify components exist
            issues = []
            
            # 1. Check Weekly Trend Chart
            weekly_chart = await page.query_selector("#team-weekly-chart")
            if weekly_chart:
                # Check if chart has data
                chart_rect = await weekly_chart.bounding_box()
                if chart_rect and chart_rect['height'] > 50:
                    print("✅ Weekly trend chart: OK")
                else:
                    issues.append("Weekly trend chart appears empty")
                    print("❌ Weekly trend chart: Empty or too small")
            else:
                issues.append("Weekly trend chart not found")
                print("❌ Weekly trend chart: Not found")
            
            # 2. Check Multi-Level Donut Chart
            donut_chart = await page.query_selector('[id^="team-role-dist-"]')
            if donut_chart:
                # Check for NaN in legend
                legend_text = await page.text_content('body')
                if 'NaN%' in legend_text:
                    issues.append("Multi-Level Donut chart shows NaN%")
                    print("❌ Multi-Level Donut: NaN% in legend")
                else:
                    print("✅ Multi-Level Donut: No NaN% found")
            else:
                issues.append("Multi-Level Donut chart not found")
                print("❌ Multi-Level Donut: Not found")
            
            # 3. Check Sunburst Chart
            sunburst_container = await page.query_selector('[id^="team-role-sunburst-"]')
            if sunburst_container:
                # Check if Plotly rendered
                plotly_element = await page.query_selector('.plotly')
                if plotly_element:
                    print("✅ Sunburst chart: Rendered")
                else:
                    issues.append("Sunburst chart not rendered")
                    print("❌ Sunburst chart: Not rendered")
            else:
                issues.append("Sunburst chart container not found")
                print("❌ Sunburst chart: Container not found")
            
            # 4. Check Team Member Detail Table
            detail_table = await page.query_selector('[id^="team-member-tbody-"]')
            if detail_table:
                # Count rows
                rows = await detail_table.query_selector_all('tr')
                if len(rows) > 0:
                    print(f"✅ Team member detail table: {len(rows)} rows")
                else:
                    issues.append("Team member detail table has no data")
                    print("❌ Team member detail table: No data")
            else:
                issues.append("Team member detail table not found")
                print("❌ Team member detail table: Not found")
            
            # 5. Check for old team member table
            old_table = await page.query_selector('[id^="team-members-tbody-"]')
            if old_table:
                issues.append("Old team member table still exists")
                print("❌ Old team member table: Still exists")
            else:
                print("✅ Old team member table: Removed")
            
            # 6. Check legend position
            legend_elements = await page.query_selector_all('.legend')
            for legend in legend_elements:
                box = await legend.bounding_box()
                if box and box['x'] < 100:  # Left side
                    print("✅ Legend position: Left side")
                    break
            
            # Summary
            print("\n" + "=" * 60)
            if issues:
                print("❌ ISSUES FOUND:")
                for issue in issues:
                    print(f"  - {issue}")
                print("\n🔄 Need to iterate and fix remaining issues")
                return False
            else:
                print("✅ ALL CHECKS PASSED!")
                print("🎉 Dashboard is working correctly")
                return True
        else:
            print("❌ Team detail modal did not open")
            return False
    else:
        print(f"❌ Could not find {TEAM_NAME} team card")
        return False

async def main():
    """Main test runner"""
    global page
    
    # Import Playwright
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"[Console] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[Page Error] {err}"))
        
        # Run verification
        try:
            success = await verify_dashboard()
            
            if not success:
                print("\n🔧 Fixes needed. Will iterate...")
            
            # Keep browser open for manual inspection
            print("\n📌 Browser will stay open for 10 seconds for manual inspection...")
            await page.wait_for_timeout(10000)
            
        finally:
            await browser.close()
            
        return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)