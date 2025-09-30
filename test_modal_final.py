#!/usr/bin/env python3
"""
Final modal test with correct selectors
"""

from playwright.sync_api import sync_playwright
import os
import time

def test_modals_final():
    dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("="*70)
        print("🔍 Final Modal Verification Test")
        print("="*70)

        # Load dashboard
        print(f"\n📂 Opening: {dashboard_path}")
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        # Test 1: Position Details (직급별 상세)
        print("\n[1] Testing Position Details Modal (직급별 상세)")
        print("-"*50)

        # Click Position Details tab
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            print("✅ Found Position Details tab")
            position_tab.click()
            page.wait_for_timeout(2000)

            # Wait for tables to be generated
            page.wait_for_timeout(3000)

            # Check if positionTables div has content
            tables_container = page.query_selector('#positionTables')
            if tables_container:
                # Look for View buttons in the generated tables
                view_buttons = page.query_selector_all('#positionTables button.btn-outline-primary')
                print(f"✅ Found {len(view_buttons)} View buttons")

                if view_buttons and len(view_buttons) > 0:
                    print("📍 Clicking first View button...")
                    view_buttons[0].click()
                    page.wait_for_timeout(2000)

                    # Check if position modal is visible
                    if page.is_visible('#positionModal'):
                        print("✅ SUCCESS: Position modal is now open!")
                        page.screenshot(path='position_modal_success.png')

                        # Close modal
                        close_btn = page.query_selector('#positionModal .btn-close')
                        if close_btn:
                            close_btn.click()
                            page.wait_for_timeout(1000)
                    else:
                        print("❌ Position modal did not open")
                else:
                    print("❌ No View buttons found in Position Details")
        else:
            print("❌ Position Details tab not found")

        # Test 2: Individual Details (개인별 상세)
        print("\n[2] Testing Individual Details Modal (개인별 상세)")
        print("-"*50)

        # Click Individual Details tab (correct selector: data-tab="detail")
        detail_tab = page.query_selector('[data-tab="detail"]')
        if detail_tab:
            print("✅ Found Individual Details tab")
            detail_tab.click()
            page.wait_for_timeout(3000)

            # Look for View buttons in the employee table
            view_buttons = page.query_selector_all('#employeeTableContainer button.btn-primary')
            print(f"✅ Found {len(view_buttons)} View buttons")

            if view_buttons and len(view_buttons) > 0:
                print("📍 Clicking first View button...")
                view_buttons[0].click()
                page.wait_for_timeout(2000)

                # Check if employee modal is visible
                if page.is_visible('#employeeModal'):
                    print("✅ SUCCESS: Employee modal is now open!")
                    page.screenshot(path='employee_modal_success.png')

                    # Close modal
                    close_btn = page.query_selector('#employeeModal .btn-close')
                    if close_btn:
                        close_btn.click()
                        page.wait_for_timeout(1000)
                else:
                    print("❌ Employee modal did not open")
            else:
                print("❌ No View buttons found in Individual Details")
        else:
            print("❌ Individual Details tab not found")

        # Final summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)

        # Check if both modals exist in DOM
        position_modal_exists = page.query_selector('#positionModal') is not None
        employee_modal_exists = page.query_selector('#employeeModal') is not None

        print(f"Position Modal in DOM: {'✅ Yes' if position_modal_exists else '❌ No'}")
        print(f"Employee Modal in DOM: {'✅ Yes' if employee_modal_exists else '❌ No'}")

        # Take final screenshot
        page.screenshot(path='dashboard_modal_test_complete.png')
        print("\n📸 Screenshots saved:")
        print("   - position_modal_success.png")
        print("   - employee_modal_success.png")
        print("   - dashboard_modal_test_complete.png")

        print("\n💡 Browser will remain open for 30 seconds for manual inspection...")
        time.sleep(30)
        browser.close()

        print("\n✅ Test complete!")

if __name__ == "__main__":
    test_modals_final()