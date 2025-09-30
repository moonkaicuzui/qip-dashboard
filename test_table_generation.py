#!/usr/bin/env python3
"""
Test table generation and View button creation
"""

from playwright.sync_api import sync_playwright
import os
import time

def test_table_generation():
    dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Monitor console messages
        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

        print("="*70)
        print("🔍 Table Generation & View Button Test")
        print("="*70)

        # Load dashboard
        print(f"\n📂 Opening: {dashboard_path}")
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        # Test 1: Check if employeeData is loaded
        print("\n[1] Checking employeeData...")
        print("-"*50)

        employee_count = page.evaluate("window.employeeData ? window.employeeData.length : 0")
        print(f"✅ employeeData loaded: {employee_count} employees")

        if employee_count > 0:
            # Sample first employee
            first_emp = page.evaluate("window.employeeData[0]")
            print(f"📊 First employee keys: {list(first_emp.keys())[:5]}...")

        # Test 2: Check if generatePositionTables function exists
        print("\n[2] Checking generatePositionTables function...")
        print("-"*50)

        func_exists = page.evaluate("typeof generatePositionTables === 'function'")
        print(f"✅ generatePositionTables exists: {func_exists}")

        # Test 3: Try to generate Position Tables manually
        print("\n[3] Manually triggering generatePositionTables...")
        print("-"*50)

        # Click Position Details tab
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            print("📍 Clicking Position Details tab...")
            position_tab.click()
            page.wait_for_timeout(2000)

            # Check if positionTables div exists
            tables_div = page.query_selector('#positionTables')
            if tables_div:
                print("✅ positionTables div exists")

                # Try to call generatePositionTables manually
                try:
                    result = page.evaluate("""
                        () => {
                            if (typeof generatePositionTables === 'function' && window.employeeData) {
                                generatePositionTables();
                                // Check if tables were created
                                const container = document.getElementById('positionTables');
                                const tables = container.querySelectorAll('table');
                                const buttons = container.querySelectorAll('button');
                                return {
                                    success: true,
                                    tableCount: tables.length,
                                    buttonCount: buttons.length,
                                    html: container.innerHTML.substring(0, 200)
                                };
                            }
                            return { success: false, reason: 'Function or data not available' };
                        }
                    """)

                    if result['success']:
                        print(f"✅ Tables generated: {result['tableCount']} tables")
                        print(f"✅ View buttons created: {result['buttonCount']} buttons")
                        print(f"📄 HTML snippet: {result['html']}...")
                    else:
                        print(f"❌ Generation failed: {result['reason']}")
                except Exception as e:
                    print(f"❌ Error generating tables: {e}")
            else:
                print("❌ positionTables div not found")

        # Test 4: Check Individual Details
        print("\n[4] Checking Individual Details (개인별 상세)...")
        print("-"*50)

        detail_tab = page.query_selector('[data-tab="detail"]')
        if detail_tab:
            print("📍 Clicking Individual Details tab...")
            detail_tab.click()
            page.wait_for_timeout(2000)

            # Check if generateDetailTable function exists
            func_exists = page.evaluate("typeof generateDetailTable === 'function'")
            print(f"✅ generateDetailTable exists: {func_exists}")

            # Try to call generateDetailTable manually
            try:
                result = page.evaluate("""
                    () => {
                        if (typeof generateDetailTable === 'function' && window.employeeData) {
                            generateDetailTable();
                            // Check if table was created
                            const container = document.getElementById('employeeTableContainer');
                            const tables = container.querySelectorAll('table');
                            const buttons = container.querySelectorAll('button');
                            return {
                                success: true,
                                tableCount: tables.length,
                                buttonCount: buttons.length
                            };
                        }
                        return { success: false, reason: 'Function or data not available' };
                    }
                """)

                if result['success']:
                    print(f"✅ Tables generated: {result['tableCount']} tables")
                    print(f"✅ View buttons created: {result['buttonCount']} buttons")
                else:
                    print(f"❌ Generation failed: {result['reason']}")
            except Exception as e:
                print(f"❌ Error generating tables: {e}")

        # Test 5: Check for JavaScript errors
        print("\n[5] Checking for JavaScript errors...")
        print("-"*50)

        errors = page.evaluate("""
            () => {
                const errors = [];
                // Check key functions
                const funcs = ['generatePositionTables', 'generateDetailTable', 'showPositionDetail', 'showEmployeeDetail'];
                for (const func of funcs) {
                    if (typeof window[func] !== 'function') {
                        errors.push(`${func} is not defined`);
                    }
                }
                // Check key data
                if (!window.employeeData) errors.push('employeeData not loaded');
                if (!window.dashboardTexts) errors.push('dashboardTexts not loaded');
                return errors;
            }
        """)

        if errors:
            print("❌ Errors found:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ No critical errors found")

        # Final summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)

        print(f"employeeData loaded: {employee_count > 0}")
        print(f"Functions defined: {not errors}")

        # Take screenshot
        page.screenshot(path='table_generation_test.png')
        print("\n📸 Screenshot saved: table_generation_test.png")

        print("\n💡 Browser will remain open for 30 seconds for manual inspection...")
        time.sleep(30)
        browser.close()

        print("\n✅ Test complete!")

if __name__ == "__main__":
    test_table_generation()