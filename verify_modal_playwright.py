#!/usr/bin/env python3
"""
Comprehensive Playwright Modal Verification Script
Tests both Position Details and Individual Details modals
"""

from playwright.sync_api import sync_playwright
import os
import json

def test_modals():
    dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Collect console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        # Collect errors
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        print("="*70)
        print("🔍 Comprehensive Modal Verification with Playwright")
        print("="*70)

        # Load dashboard
        print(f"\n📂 Loading dashboard: {dashboard_path}")
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        # 1. Check if Bootstrap is loaded
        print("\n[1] Bootstrap Library Check")
        print("-"*50)
        has_bootstrap = page.evaluate('''() => {
            return typeof bootstrap !== 'undefined';
        }''')
        print(f"Bootstrap loaded: {'✅ Yes' if has_bootstrap else '❌ No'}")

        if has_bootstrap:
            bootstrap_version = page.evaluate('''() => {
                return bootstrap.Modal ? 'Modal class available' : 'Modal class NOT available';
            }''')
            print(f"Bootstrap Modal: {bootstrap_version}")

        # 2. Check if employeeData is loaded
        print("\n[2] Data Loading Check")
        print("-"*50)
        employee_data_loaded = page.evaluate('''() => {
            return typeof employeeData !== 'undefined' && Array.isArray(employeeData);
        }''')

        if employee_data_loaded:
            employee_count = page.evaluate('() => employeeData.length')
            print(f"✅ employeeData loaded: {employee_count} records")
        else:
            print("❌ employeeData not loaded")

        # 3. Check modal elements exist
        print("\n[3] Modal HTML Structure Check")
        print("-"*50)
        position_modal_exists = page.evaluate('''() => {
            const modal = document.getElementById('positionModal');
            return modal !== null;
        }''')

        employee_modal_exists = page.evaluate('''() => {
            const modal = document.getElementById('employeeModal');
            return modal !== null;
        }''')

        print(f"Position Modal (#positionModal): {'✅ Exists' if position_modal_exists else '❌ Not found'}")
        print(f"Employee Modal (#employeeModal): {'✅ Exists' if employee_modal_exists else '❌ Not found'}")

        # 4. Check if functions exist
        print("\n[4] JavaScript Function Check")
        print("-"*50)
        functions_check = page.evaluate('''() => {
            return {
                showPositionDetail: typeof showPositionDetail === 'function',
                showEmployeeDetail: typeof showEmployeeDetail === 'function',
                generatePositionTables: typeof generatePositionTables === 'function'
            };
        }''')

        for func_name, exists in functions_check.items():
            print(f"{func_name}: {'✅ Defined' if exists else '❌ Not defined'}")

        # 5. Test Position Details Modal
        print("\n[5] Testing Position Details Modal")
        print("-"*50)

        # Click on Position Details tab
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            print("✅ Clicked Position Details tab")
            page.wait_for_timeout(2000)

            # Check if tables are generated
            tables = page.query_selector_all('#positionTables table')
            print(f"Tables generated: {len(tables)}")

            # Find View buttons
            view_buttons = page.query_selector_all('#positionTables button.btn-outline-primary')
            print(f"View buttons found: {len(view_buttons)}")

            if view_buttons and len(view_buttons) > 0:
                # Get onclick attribute of first button
                first_button_onclick = view_buttons[0].get_attribute('onclick')
                print(f"First button onclick: {first_button_onclick}")

                # Try clicking the button
                print("\nClicking first View button...")
                view_buttons[0].click()
                page.wait_for_timeout(2000)

                # Check if modal is visible
                modal_visible = page.is_visible('#positionModal')
                if modal_visible:
                    print("✅ SUCCESS: Position modal opened!")
                    page.screenshot(path='position_modal_open.png')
                    print("📸 Screenshot saved: position_modal_open.png")

                    # Close modal
                    close_btn = page.query_selector('#positionModal .btn-close')
                    if close_btn:
                        close_btn.click()
                        page.wait_for_timeout(1000)
                else:
                    print("❌ FAIL: Modal did not open after button click")

                    # Try manual JavaScript execution
                    print("\n🔧 Attempting manual JavaScript fix...")

                    # Extract parameters from onclick
                    import re
                    match = re.match(r"showPositionDetail\('([^']+)',\s*'([^']+)'\)", first_button_onclick or "")
                    if match:
                        type_param, position_param = match.groups()
                        print(f"Parameters: type='{type_param}', position='{position_param}'")

                        # Try calling the function directly with debugging
                        result = page.evaluate(f'''() => {{
                            console.log('Attempting to show modal for:', '{type_param}', '{position_param}');

                            // Check if function exists
                            if (typeof showPositionDetail !== 'function') {{
                                console.error('showPositionDetail is not a function');
                                return 'Function not found';
                            }}

                            // Check modal element
                            const modal = document.getElementById('positionModal');
                            if (!modal) {{
                                console.error('Modal element not found');
                                return 'Modal element not found';
                            }}

                            // Try calling the function
                            try {{
                                showPositionDetail('{type_param}', '{position_param}');
                                return 'Function called';
                            }} catch(e) {{
                                console.error('Error calling function:', e);
                                return 'Error: ' + e.toString();
                            }}
                        }}''')
                        print(f"Direct call result: {result}")

                        page.wait_for_timeout(2000)

                        # Check again
                        modal_visible_after = page.is_visible('#positionModal')
                        if modal_visible_after:
                            print("✅ Modal opened after direct JavaScript call")
                        else:
                            print("❌ Modal still not visible after direct call")

                            # Try Bootstrap Modal directly
                            print("\n🔧 Attempting Bootstrap Modal.show() directly...")
                            bootstrap_result = page.evaluate('''() => {
                                try {
                                    const modalElement = document.getElementById('positionModal');
                                    const modal = new bootstrap.Modal(modalElement);
                                    modal.show();
                                    return 'Bootstrap modal.show() called';
                                } catch(e) {
                                    return 'Error: ' + e.toString();
                                }
                            }''')
                            print(f"Bootstrap result: {bootstrap_result}")

                            page.wait_for_timeout(2000)
                            modal_visible_bootstrap = page.is_visible('#positionModal')
                            if modal_visible_bootstrap:
                                print("✅ Modal opened with Bootstrap Modal.show()")
                                page.screenshot(path='position_modal_bootstrap.png')
                            else:
                                print("❌ Modal still won't open even with Bootstrap")
                    else:
                        print("Could not parse onclick parameters")
        else:
            print("❌ Position Details tab not found")

        # 6. Test Individual Details Modal
        print("\n[6] Testing Individual Details Modal")
        print("-"*50)

        # Click on Individual Details tab
        employee_tab = page.query_selector('[data-tab="employees"]')
        if employee_tab:
            employee_tab.click()
            print("✅ Clicked Individual Details tab")
            page.wait_for_timeout(2000)

            # Find View buttons
            view_buttons = page.query_selector_all('#employeeTableContainer button.btn-primary')
            print(f"View buttons found: {len(view_buttons)}")

            if view_buttons and len(view_buttons) > 0:
                # Try clicking the button
                print("\nClicking first View button...")
                view_buttons[0].click()
                page.wait_for_timeout(2000)

                # Check if modal is visible
                modal_visible = page.is_visible('#employeeModal')
                if modal_visible:
                    print("✅ SUCCESS: Employee modal opened!")
                    page.screenshot(path='employee_modal_open.png')
                    print("📸 Screenshot saved: employee_modal_open.png")
                else:
                    print("❌ FAIL: Employee modal did not open")
        else:
            print("❌ Individual Details tab not found")

        # 7. Console Messages and Errors
        print("\n[7] Console Messages and Errors")
        print("-"*50)

        if errors:
            print("❌ Page Errors Found:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ No page errors")

        error_messages = [msg for msg in console_messages if 'error' in msg.lower()]
        if error_messages:
            print("\n❌ Console Errors Found:")
            for msg in error_messages:
                print(f"   - {msg}")
        else:
            print("✅ No console errors")

        # 8. Final Diagnosis
        print("\n" + "="*70)
        print("🔬 DIAGNOSIS SUMMARY")
        print("="*70)

        issues = []

        if not has_bootstrap:
            issues.append("Bootstrap library not loaded")
        if not employee_data_loaded:
            issues.append("Employee data not loaded")
        if not position_modal_exists:
            issues.append("Position modal HTML not found")
        if not employee_modal_exists:
            issues.append("Employee modal HTML not found")
        if not functions_check.get('showPositionDetail'):
            issues.append("showPositionDetail function not defined")
        if not functions_check.get('showEmployeeDetail'):
            issues.append("showEmployeeDetail function not defined")

        if issues:
            print("🚨 Critical Issues Found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("⚠️ No critical issues found. The problem might be:")
            print("   - Event binding issue in showPositionDetail/showEmployeeDetail")
            print("   - Incorrect field mapping in filter conditions")
            print("   - Bootstrap Modal initialization timing issue")

        # Take final screenshot
        page.screenshot(path='dashboard_final_state.png')
        print("\n📸 Final screenshot saved: dashboard_final_state.png")

        print("\n💡 Browser will remain open for 30 seconds for manual inspection...")
        import time
        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    test_modals()