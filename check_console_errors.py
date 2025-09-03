#!/usr/bin/env python3
"""
Check for JavaScript console errors in the dashboard
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def check_errors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        
        # Navigate to dashboard
        dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트8.3_구글 연동 완료_by Macbook pro_조건 매트릭스 JSON 파일 도입_버전 5_action.sh 테스트/output_files/management_dashboard_2025_08.html"
        await page.goto(dashboard_path)
        
        print("=" * 80)
        print("Dashboard Console Error Check")
        print("=" * 80)
        
        # Wait for page to load
        await page.wait_for_timeout(2000)
        
        # Check for errors
        errors = [msg for msg in console_messages if msg.startswith("error")]
        warnings = [msg for msg in console_messages if msg.startswith("warning")]
        logs = [msg for msg in console_messages if msg.startswith("log")]
        
        if errors:
            print("\n❌ JavaScript Errors Found:")
            for error in errors:
                print(f"  {error}")
        else:
            print("\n✅ No JavaScript errors found")
        
        if warnings:
            print("\n⚠️ Warnings:")
            for warning in warnings[:5]:  # Show first 5 warnings
                print(f"  {warning}")
        
        # Show recent console logs
        print("\n📝 Recent Console Logs:")
        for log in logs[-10:]:  # Show last 10 logs
            print(f"  {log}")
        
        # Try to click on a stat card to trigger the modal
        print("\n🔍 Testing modal functionality...")
        
        # First, click on a stat card to open the modal
        stat_card = await page.query_selector(".stat-card")
        if stat_card:
            print("  Found stat card, clicking to open modal...")
            await stat_card.click()
            await page.wait_for_timeout(2000)
            
            # Now look for treemap cells in the modal
            assembly_cell = await page.query_selector(".treemap-cell:has-text('ASSEMBLY')")
        else:
            assembly_cell = None
            print("  ❌ No stat card found to click")
        
        if assembly_cell:
            print("  Found ASSEMBLY team cell, clicking...")
            await assembly_cell.click()
            await page.wait_for_timeout(1000)
            
            # Check if modal appeared
            modal = await page.query_selector(".modal")
            if modal:
                print("  ✅ Modal appeared!")
                
                # Check for role treemap container
                treemap_container = await page.query_selector("#team-role-treemap-ASSEMBLY")
                if treemap_container:
                    print("  ✅ Role treemap container found!")
                    
                    # Check container content
                    inner_html = await treemap_container.inner_html()
                    if inner_html:
                        print(f"  📊 Treemap container has content: {len(inner_html)} characters")
                    else:
                        print("  ⚠️ Treemap container is empty")
                else:
                    print("  ❌ Role treemap container not found")
            else:
                print("  ❌ Modal did not appear")
        else:
            print("  ❌ ASSEMBLY team cell not found in main treemap")
        
        # Keep browser open for manual inspection
        print("\n⏳ Browser will remain open for 10 seconds for inspection...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_errors())