#!/usr/bin/env python3
"""
Simple browser test for modal functionality
"""

from playwright.sync_api import sync_playwright
import os
import time

def test_modals_browser():
    dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Collect console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        print("="*70)
        print("🔍 Dashboard Modal Test")
        print("="*70)

        # Load dashboard
        print(f"\n📂 Opening: {dashboard_path}")
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        # Check for JavaScript errors
        print("\n[1] Checking for JavaScript Errors")
        print("-"*50)
        error_messages = [msg for msg in console_messages if 'error' in msg.lower()]
        if error_messages:
            print("❌ JavaScript Errors Found:")
            for msg in error_messages[:5]:
                print(f"   - {msg}")
        else:
            print("✅ No JavaScript errors")

        # Try to click on Position Details tab
        print("\n[2] Testing Position Details Tab")
        print("-"*50)
        try:
            # Click Position Details tab
            position_tab = page.query_selector('[data-tab="position"]')
            if position_tab:
                print("Found Position Details tab, clicking...")
                position_tab.click()
                page.wait_for_timeout(2000)

                # Look for View buttons
                view_buttons = page.query_selector_all('button:has-text("View")')
                print(f"Found {len(view_buttons)} View buttons")

                if view_buttons:
                    print("Clicking first View button...")
                    view_buttons[0].click()
                    page.wait_for_timeout(2000)

                    # Check if modal is visible
                    modal = page.query_selector('#positionModal')
                    if modal and page.is_visible('#positionModal'):
                        print("✅ SUCCESS: Position modal opened!")
                    else:
                        print("❌ Modal did not open")
            else:
                print("❌ Position Details tab not found")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Try Individual Details tab
        print("\n[3] Testing Individual Details Tab")
        print("-"*50)
        try:
            # Click Individual Details tab
            employee_tab = page.query_selector('[data-tab="employees"]')
            if employee_tab:
                print("Found Individual Details tab, clicking...")
                employee_tab.click()
                page.wait_for_timeout(2000)

                # Look for View buttons
                view_buttons = page.query_selector_all('button:has-text("View")')
                print(f"Found {len(view_buttons)} View buttons")

                if view_buttons:
                    print("Clicking first View button...")
                    view_buttons[0].click()
                    page.wait_for_timeout(2000)

                    # Check if modal is visible
                    modal = page.query_selector('#employeeModal')
                    if modal and page.is_visible('#employeeModal'):
                        print("✅ SUCCESS: Employee modal opened!")
                    else:
                        print("❌ Modal did not open")
            else:
                print("❌ Individual Details tab not found")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Take screenshot
        page.screenshot(path='modal_test_result.png')
        print("\n📸 Screenshot saved: modal_test_result.png")

        print("\n" + "="*70)
        print("💡 Browser will remain open for manual testing...")
        print("Please test the modals manually and observe any issues")
        print("="*70)

        # Keep browser open for manual testing
        time.sleep(60)
        browser.close()

if __name__ == "__main__":
    test_modals_browser()