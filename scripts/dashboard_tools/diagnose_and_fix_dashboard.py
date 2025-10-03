#!/usr/bin/env python3
"""
Diagnose and fix Version 6 dashboard initialization issue using Playwright
"""

import asyncio
from playwright.async_api import async_playwright
import os
import json

async def diagnose_dashboard():
    """Diagnose why the dashboard doesn't display data on load"""

    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"[Console {msg.type}]: {msg.text}"))

        print("Loading dashboard...")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(2000)

        # Check if data exists
        print("\n=== Checking Data Presence ===")
        data_exists = await page.evaluate("() => typeof window.employeeData !== 'undefined' && window.employeeData.length > 0")
        print(f"Employee data exists: {data_exists}")

        if data_exists:
            employee_count = await page.evaluate("() => window.employeeData.length")
            print(f"Number of employees: {employee_count}")

        # Check if functions exist
        print("\n=== Checking Functions ===")
        functions_to_check = [
            'updateTypeSummaryTable',
            'updateSummaryCards',
            'updateOrgChart',
            'showTab',
            'changeLanguage',
            'updateAllTexts'
        ]

        for func in functions_to_check:
            exists = await page.evaluate(f"() => typeof {func} === 'function'")
            print(f"{func}: {'✓ exists' if exists else '✗ missing'}")

        # Check current state of summary cards
        print("\n=== Current Summary Card Values ===")
        total_employees = await page.text_content("#totalEmployees")
        paid_employees = await page.text_content("#paidEmployees")
        payment_rate = await page.text_content("#paymentRate")
        total_amount = await page.text_content("#totalAmount")

        print(f"Total Employees: {total_employees}")
        print(f"Paid Employees: {paid_employees}")
        print(f"Payment Rate: {payment_rate}")
        print(f"Total Amount: {total_amount}")

        # Check if DOMContentLoaded handler exists
        print("\n=== Checking Initialization ===")
        has_init = await page.evaluate("""() => {
            // Check if there's any initialization code
            const scripts = document.querySelectorAll('script');
            let hasInitCode = false;
            for (let script of scripts) {
                if (script.textContent && script.textContent.includes('DOMContentLoaded')) {
                    hasInitCode = true;
                    break;
                }
            }
            return hasInitCode;
        }""")
        print(f"Has DOMContentLoaded handler: {has_init}")

        # Try to manually initialize
        print("\n=== Manual Initialization Test ===")
        print("Calling updateTypeSummaryTable()...")
        await page.evaluate("() => { if (typeof updateTypeSummaryTable === 'function') updateTypeSummaryTable(); }")

        print("Calling updateSummaryCards()...")
        await page.evaluate("() => { if (typeof updateSummaryCards === 'function') updateSummaryCards(); }")

        await page.wait_for_timeout(1000)

        # Check values after manual initialization
        print("\n=== After Manual Initialization ===")
        total_employees_after = await page.text_content("#totalEmployees")
        paid_employees_after = await page.text_content("#paidEmployees")
        payment_rate_after = await page.text_content("#paymentRate")
        total_amount_after = await page.text_content("#totalAmount")

        print(f"Total Employees: {total_employees_after}")
        print(f"Paid Employees: {paid_employees_after}")
        print(f"Payment Rate: {payment_rate_after}")
        print(f"Total Amount: {total_amount_after}")

        # Check for errors
        print("\n=== Checking for Errors ===")
        errors = await page.evaluate("""() => {
            const errors = [];
            // Check if currentLanguage is defined
            if (typeof currentLanguage === 'undefined') {
                errors.push('currentLanguage is undefined');
            }
            // Check if translations exist
            if (typeof translations === 'undefined') {
                errors.push('translations is undefined');
            }
            return errors;
        }""")

        if errors:
            print("Found issues:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("No JavaScript errors found")

        # Take screenshot for verification
        await page.screenshot(path="dashboard_after_manual_init.png")
        print("\nScreenshot saved as dashboard_after_manual_init.png")

        await browser.close()

        return data_exists and (paid_employees_after != paid_employees)

async def fix_dashboard():
    """Fix the dashboard by adding proper initialization code"""

    print("\n=== Fixing Dashboard Initialization ===")

    # Read the current HTML
    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Find the location to add initialization code
    # We need to add it after all the functions are defined
    # Look for the end of the dashboard_complete.js content

    # Check if initialization code already exists
    if "document.addEventListener('DOMContentLoaded'" in html_content:
        print("DOMContentLoaded handler already exists, checking if it's working...")

    # Add proper initialization code before </script>
    init_code = """
    // Dashboard Initialization
    console.log('Dashboard initialization starting...');

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDashboard);
    } else {
        // DOM is already loaded
        initializeDashboard();
    }

    function initializeDashboard() {
        console.log('Initializing dashboard with', window.employeeData ? window.employeeData.length : 0, 'employees');

        // Set default language if not set
        if (typeof currentLanguage === 'undefined') {
            window.currentLanguage = localStorage.getItem('dashboardLanguage') || 'ko';
        }

        // Initialize all components
        try {
            // Update summary cards
            if (typeof updateSummaryCards === 'function') {
                updateSummaryCards();
                console.log('Summary cards updated');
            }

            // Update type summary table
            if (typeof updateTypeSummaryTable === 'function') {
                updateTypeSummaryTable();
                console.log('Type summary table updated');
            }

            // Show default tab
            if (typeof showTab === 'function') {
                showTab('summary');
                console.log('Summary tab displayed');
            }

            // Update all texts for current language
            if (typeof updateAllTexts === 'function') {
                updateAllTexts();
                console.log('Language texts updated');
            }

            console.log('Dashboard initialization complete!');
        } catch (error) {
            console.error('Error during dashboard initialization:', error);
        }
    }
    """

    # Find the last </script> tag and insert before it
    last_script_end = html_content.rfind('</script>')
    if last_script_end > 0:
        # Insert the initialization code before the last </script>
        new_html = html_content[:last_script_end] + init_code + html_content[last_script_end:]

        # Save as a new version
        fixed_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6_Fixed.html"
        with open(fixed_path, 'w', encoding='utf-8') as f:
            f.write(new_html)

        print(f"Fixed dashboard saved as: {fixed_path}")
        return fixed_path
    else:
        print("Could not find </script> tag to insert initialization code")
        return None

async def test_fixed_dashboard(fixed_path):
    """Test the fixed dashboard to verify it works"""

    print("\n=== Testing Fixed Dashboard ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"[Console]: {msg.text}"))

        print(f"Loading fixed dashboard from: {fixed_path}")
        await page.goto(f"file://{fixed_path}")
        await page.wait_for_timeout(3000)

        # Check if data is displayed correctly
        print("\n=== Checking Fixed Dashboard ===")

        total_employees = await page.text_content("#totalEmployees")
        paid_employees = await page.text_content("#paidEmployees")
        payment_rate = await page.text_content("#paymentRate")
        total_amount = await page.text_content("#totalAmount")

        print(f"Total Employees: {total_employees}")
        print(f"Paid Employees: {paid_employees}")
        print(f"Payment Rate: {payment_rate}")
        print(f"Total Amount: {total_amount}")

        # Check if table has data
        table_rows = await page.query_selector_all("#typeSummaryTableBody tr")
        print(f"Number of rows in summary table: {len(table_rows)}")

        # Take screenshot
        await page.screenshot(path="dashboard_fixed_result.png")
        print("\nScreenshot saved as dashboard_fixed_result.png")

        # Test language switching
        print("\n=== Testing Language Switch ===")
        await page.click("button:has-text('EN')")
        await page.wait_for_timeout(1000)

        # Check if language changed
        dashboard_title = await page.text_content("h1.mb-0")
        print(f"Dashboard title after language switch: {dashboard_title}")

        await browser.close()

        return "0" not in paid_employees  # Success if paid employees is not 0

async def main():
    # Step 1: Diagnose the issue
    diagnosis_result = await diagnose_dashboard()

    if diagnosis_result:
        print("\n✓ Manual initialization works - the issue is with automatic initialization")

    # Step 2: Fix the dashboard
    fixed_path = await fix_dashboard()

    if fixed_path:
        # Step 3: Test the fixed version
        success = await test_fixed_dashboard(fixed_path)

        if success:
            print("\n✓ Dashboard fixed successfully!")
            print(f"Fixed version saved as: {fixed_path}")
            print("\nTo use the fixed dashboard:")
            print("1. Open the fixed HTML file in your browser")
            print("2. Or replace the original with the fixed version")
        else:
            print("\n✗ Fix didn't work as expected, manual intervention may be needed")
    else:
        print("\n✗ Could not create fixed version")

if __name__ == "__main__":
    asyncio.run(main())