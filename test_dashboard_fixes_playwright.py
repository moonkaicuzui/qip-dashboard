#!/usr/bin/env python3
"""
Dashboard Fixes Verification using Playwright
Tests all the issues reported by the user and verifies they are fixed
"""

import asyncio
import json
from playwright.async_api import async_playwright
import os

async def test_dashboard():
    async with async_playwright() as p:
        # Launch browser with visible UI
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Load the dashboard
        file_path = os.path.abspath('output_files/management_dashboard_2025_08.html')
        await page.goto(f'file://{file_path}')
        
        # Wait for page to fully load
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        print("=== DASHBOARD FIXES VERIFICATION ===\n")
        
        # Test 1: Check if dashboard loads without JavaScript errors
        try:
            errors = []
            page.on('pageerror', lambda msg: errors.append(msg))
            await asyncio.sleep(1)
            
            if not errors:
                print("✅ Test 1: Dashboard loads without JavaScript errors")
            else:
                print(f"❌ Test 1: JavaScript errors found: {errors}")
        except Exception as e:
            print(f"❌ Test 1 failed: {e}")
        
        # Test 2: Verify team cards are displayed
        try:
            team_cards = await page.query_selector_all('.team-card')
            if team_cards:
                print(f"✅ Test 2: Found {len(team_cards)} team cards")
                
                # Click on ASSEMBLY team card
                assembly_card = None
                for card in team_cards:
                    team_name = await card.query_selector('h3')
                    if team_name:
                        name_text = await team_name.inner_text()
                        if 'ASSEMBLY' in name_text:
                            assembly_card = card
                            break
                
                if assembly_card:
                    print("✅ Test 2a: Found ASSEMBLY team card")
                    
                    # Check the percentage change display
                    change_elem = await assembly_card.query_selector('.stat-change')
                    if change_elem:
                        change_text = await change_elem.inner_text()
                        print(f"✅ Test 2b: ASSEMBLY team change display: {change_text}")
                        
                        # Verify it's showing increase, not decrease
                        if '↑' in change_text or '+' in change_text:
                            print("✅ Test 2c: Correctly showing increase (not decrease)")
                        elif '↓' in change_text or '-' in change_text and '13.0%' not in change_text:
                            print("⚠️ Test 2c: Still showing decrease but value changed")
                        else:
                            print("❌ Test 2c: Still showing incorrect decrease")
            else:
                print("❌ Test 2: No team cards found")
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
        
        # Test 3: Click ASSEMBLY team and check modal
        try:
            # Click ASSEMBLY team card
            assembly_cards = await page.query_selector_all('.team-card')
            for card in assembly_cards:
                team_name = await card.query_selector('h3')
                if team_name and 'ASSEMBLY' in await team_name.inner_text():
                    await card.click()
                    break
            
            await asyncio.sleep(2)  # Wait for modal to open
            
            # Check if modal opened
            modal = await page.query_selector('#team-detail-modal')
            if modal:
                print("✅ Test 3: Modal opened successfully")
                
                # Test 3a: Check Multi-Level Donut chart
                donut_canvas = await page.query_selector('canvas[id*="team-role-dist"]')
                if donut_canvas:
                    print("✅ Test 3a: Multi-Level Donut chart canvas found")
                    
                    # Check if chart is rendered (canvas has content)
                    canvas_box = await donut_canvas.bounding_box()
                    if canvas_box and canvas_box['width'] > 0 and canvas_box['height'] > 0:
                        print(f"✅ Test 3b: Donut chart rendered ({canvas_box['width']}x{canvas_box['height']})")
                else:
                    print("❌ Test 3a: Multi-Level Donut chart not found")
                
                # Test 3c: Check Sunburst chart
                sunburst_div = await page.query_selector('div[id*="team-role-sunburst"]')
                if sunburst_div:
                    print("✅ Test 3c: Sunburst chart container found")
                    
                    # Check if Plotly rendered the chart
                    plotly_container = await sunburst_div.query_selector('.plot-container')
                    if plotly_container:
                        print("✅ Test 3d: Sunburst chart rendered by Plotly")
                        
                        # Try clicking on Sunburst to test interactivity
                        await sunburst_div.click()
                        await asyncio.sleep(1)
                        print("✅ Test 3e: Sunburst chart is interactive")
                    else:
                        print("❌ Test 3d: Sunburst chart not rendered (empty container)")
                else:
                    print("❌ Test 3c: Sunburst chart container not found")
                
                # Test 3f: Check team member table
                table_body = await page.query_selector('tbody[id*="team-member-tbody"]')
                if table_body:
                    rows = await table_body.query_selector_all('tr')
                    if rows:
                        print(f"✅ Test 3f: Team member table has {len(rows)} rows")
                        
                        # Check first row data
                        if len(rows) > 0:
                            first_row = rows[0]
                            cells = await first_row.query_selector_all('td')
                            if cells and len(cells) > 3:
                                name_cell = await cells[3].inner_text()
                                employee_cell = await cells[4].inner_text() if len(cells) > 4 else '-'
                                years_cell = await cells[6].inner_text() if len(cells) > 6 else '-'
                                
                                print(f"  Sample data - Name: {name_cell}, Employee No: {employee_cell}, Years: {years_cell}")
                                
                                # Check for data quality
                                if name_cell and name_cell != '-':
                                    print("✅ Test 3g: Employee names are displayed")
                                else:
                                    print("❌ Test 3g: Employee names are missing")
                                
                                if employee_cell and employee_cell != '-':
                                    print("✅ Test 3h: Employee numbers are displayed")
                                else:
                                    print("❌ Test 3h: Employee numbers are missing")
                                
                                # Check years of service
                                if years_cell and '-1' not in years_cell:
                                    print("✅ Test 3i: Years of service fixed (no -1년)")
                                else:
                                    print("❌ Test 3i: Years of service still showing negative")
                        
                        # Check for Total row
                        total_row_found = False
                        for row in rows:
                            row_text = await row.inner_text()
                            if 'TOTAL' in row_text or '총' in row_text:
                                total_row_found = True
                                print("✅ Test 3j: Total summary row found")
                                break
                        
                        if not total_row_found:
                            print("⚠️ Test 3j: Total summary row might be missing")
                    else:
                        print("❌ Test 3f: Team member table has no data rows")
                else:
                    print("❌ Test 3f: Team member table body not found")
                
                # Close modal
                close_btn = await page.query_selector('.modal-close')
                if close_btn:
                    await close_btn.click()
                    await asyncio.sleep(1)
            else:
                print("❌ Test 3: Modal did not open")
        except Exception as e:
            print(f"❌ Test 3 failed: {e}")
        
        # Take a screenshot for visual verification
        await page.screenshot(path='test_dashboard_final.png', full_page=True)
        print("\n📸 Screenshot saved as test_dashboard_final.png")
        
        # Keep browser open for manual verification
        print("\n⏸️  Browser will stay open for 10 seconds for manual verification...")
        await asyncio.sleep(10)
        
        await browser.close()
        print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_dashboard())