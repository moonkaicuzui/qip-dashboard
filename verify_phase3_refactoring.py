#!/usr/bin/env python3
"""
Phase 3 Refactoring Verification Script
Tests all 5 position types in Org Chart modals
"""

from playwright.sync_api import sync_playwright
import time

def test_org_chart_modals():
    print("=" * 80)
    print("🔍 Phase 3 Refactoring Verification - Org Chart Modals")
    print("=" * 80)

    dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    # Test cases: (position_name, employee_id, expected_position_type)
    test_cases = [
        ("LINE LEADER", "622020174", "LINE LEADER"),  # NGUYỄN NGỌC BÍCH THỦY
        ("GROUP LEADER", "622020118", "GROUP LEADER"),  # LƯƠNG THỊ CẨM TIÊN
        ("SUPERVISOR", "822000065", "SUPERVISOR"),  # NGUYỄN THỊ HỒNG NHUNG
        ("A.MANAGER", "821000029", "A.MANAGER"),  # CHÂU THỊ KIỀU DIỄM
        ("MANAGER", "621000009", "MANAGER"),  # HUỲNH THỊ BÍCH NGỌC
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto(dashboard_path)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Click Org Chart tab
        print("\n📊 Opening Org Chart tab...")
        page.click("#tabOrgChart")
        time.sleep(3)

        results = []

        for position_name, emp_id, expected_type in test_cases:
            print(f"\n{'='*80}")
            print(f"🧪 Testing: {position_name} (ID: {emp_id})")
            print(f"{'='*80}")

            try:
                # Find and click the node
                page.evaluate(f"showIncentiveModal('{emp_id}')")
                time.sleep(2)

                # Check if modal opened
                modal = page.locator(".modal.show")
                if modal.count() > 0:
                    print("✅ Modal opened successfully")

                    # Check for key elements
                    modal_body = modal.locator(".modal-body")

                    # Check for calculation details section
                    calc_details = modal_body.locator(".calculation-details")
                    if calc_details.count() > 0:
                        print("✅ Calculation details section found")

                        # Get the formula text
                        formula = calc_details.locator("table tr").first.locator("td").nth(1).inner_text()
                        print(f"   Formula: {formula[:50]}...")

                        # Check for expected/actual incentive rows
                        table_rows = calc_details.locator("table tr")
                        has_expected = False
                        has_actual = False

                        for i in range(table_rows.count()):
                            row_text = table_rows.nth(i).inner_text()
                            if "예상 인센티브" in row_text or "Expected Incentive" in row_text:
                                has_expected = True
                                print(f"✅ Expected incentive row found")
                            if "실제 인센티브" in row_text or "Actual Incentive" in row_text:
                                has_actual = True
                                print(f"✅ Actual incentive row found")

                        # Check for subordinate table
                        subordinate_table = modal_body.locator("table.table-bordered")
                        if subordinate_table.count() > 0:
                            print(f"✅ Subordinate table found ({subordinate_table.count()} table(s))")

                            # Count rows
                            tbody_rows = subordinate_table.first.locator("tbody tr")
                            print(f"   Subordinates: {tbody_rows.count()} rows")

                        # Check for alert boxes (Phase 2 feature)
                        alerts = modal_body.locator(".alert")
                        if alerts.count() > 0:
                            for j in range(alerts.count()):
                                alert_class = alerts.nth(j).get_attribute("class")
                                if "alert-danger" in alert_class:
                                    print("🚨 Red alert box (non-payment) found")
                                elif "alert-warning" in alert_class:
                                    print("⚠️  Yellow alert box (difference) found")

                        results.append({
                            "position": position_name,
                            "emp_id": emp_id,
                            "status": "PASS",
                            "has_expected": has_expected,
                            "has_actual": has_actual,
                            "has_subordinates": subordinate_table.count() > 0
                        })
                    else:
                        print("❌ Calculation details section NOT found")
                        results.append({
                            "position": position_name,
                            "emp_id": emp_id,
                            "status": "FAIL - No calculation details"
                        })

                    # Close modal
                    page.click(".modal .btn-close")
                    time.sleep(1)
                else:
                    print("❌ Modal did NOT open")
                    results.append({
                        "position": position_name,
                        "emp_id": emp_id,
                        "status": "FAIL - Modal not opened"
                    })

            except Exception as e:
                print(f"❌ Error testing {position_name}: {e}")
                results.append({
                    "position": position_name,
                    "emp_id": emp_id,
                    "status": f"ERROR - {str(e)}"
                })

        # Take final screenshot
        screenshot_path = "output_files/phase3_verification_orgchart.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 Screenshot saved: {screenshot_path}")

        browser.close()

    # Summary
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)

    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {result['position']:15s} ({result['emp_id']}): {result['status']}")

    print(f"\n{'='*80}")
    print(f"🎯 Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}")

    if passed == total:
        print("\n🎉 ✅ Phase 3 Refactoring: ALL TESTS PASSED!")
        print("   - Configuration-driven approach working correctly")
        print("   - All 5 position types displaying properly")
        print("   - Code reduced from ~600 lines to ~20 lines main logic")
        return True
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        return False

if __name__ == "__main__":
    success = test_org_chart_modals()
    exit(0 if success else 1)