#!/usr/bin/env python3
"""
Final Test for Dashboard Fixes
- Modal click functionality
- Correct incentive amounts display
- Dynamic month handling
"""
import json
import re

def test_dashboard_fixes():
    """Test all dashboard fixes"""

    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    print("="*60)
    print("Dashboard Final Fixes Verification")
    print("="*60)

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Test 1: dashboardMonth variable exists
    print("\n1. Dynamic Month Handling:")
    month_match = re.search(r"const dashboardMonth = '([^']+)';", content)
    if month_match:
        month = month_match.group(1)
        print(f"   ✅ dashboardMonth = '{month}'")
        if month == 'september':
            print("   ✅ Correctly set to September")
        else:
            print(f"   ❌ Wrong month: {month}")
    else:
        print("   ❌ dashboardMonth variable not found")

    # Test 2: Check that we're using dashboardMonth in calculations
    if "employee[dashboardMonth + '_incentive']" in content:
        print("\n2. Dynamic Incentive Access:")
        print("   ✅ Using dashboardMonth + '_incentive' pattern")
    else:
        print("\n2. Dynamic Incentive Access:")
        print("   ⚠️ Check if using dynamic month access")

    # Test 3: Check modal click event listener
    if re.search(r"document\.querySelectorAll\('.node-incentive-info'\)\.forEach", content):
        print("\n3. Modal Click Event:")
        print("   ✅ Event listener attached to .node-incentive-info elements")

        # Check for showIncentiveModal function
        if "function showIncentiveModal(nodeId)" in content:
            print("   ✅ showIncentiveModal function exists")
        else:
            print("   ❌ showIncentiveModal function not found")
    else:
        print("\n3. Modal Click Event:")
        print("   ❌ Event listener not found")

    # Test 4: Check employee data has correct incentive fields
    print("\n4. Employee Data Structure:")
    emp_data_match = re.search(r'const employeeData = (\[.*?\]);', content, re.DOTALL)
    if emp_data_match:
        try:
            # Clean up NaN values
            data_str = emp_data_match.group(1)
            data_str = re.sub(r'\bNaN\b', 'null', data_str)
            employees = json.loads(data_str)

            if employees:
                sample = employees[0]
                print(f"   Sample employee fields: {list(sample.keys())[:10]}...")

                # Check for september_incentive field
                if 'september_incentive' in sample:
                    print("   ✅ september_incentive field exists")
                    # Check if values are numeric strings
                    non_numeric = []
                    for emp in employees[:5]:
                        val = emp.get('september_incentive', '0')
                        if val and not val.replace('.', '').replace('-', '').isdigit():
                            if val != '0' and val != '0.0':
                                non_numeric.append(val)

                    if non_numeric:
                        print(f"   ⚠️ Non-numeric values found: {non_numeric[:3]}")
                    else:
                        print("   ✅ All incentive values are numeric")
                else:
                    print("   ❌ september_incentive field not found")

                # Check for august_incentive field
                if 'august_incentive' in sample:
                    print("   ✅ august_incentive field exists (for compatibility)")
        except:
            print("   ❌ Failed to parse employee data")

    # Test 5: Check subordinate details in modal
    print("\n5. Modal Subordinate Details:")
    if '📋 인센티브 계산 기반 부하직원 상세' in content:
        print("   ✅ Subordinate detail table exists")
    else:
        print("   ❌ Subordinate detail table not found")

    # Test 6: Check CSS for clickability
    if '.node-incentive-info' in content and 'cursor: pointer' in content:
        print("\n6. UI Clickability:")
        print("   ✅ Incentive info has pointer cursor")
    else:
        print("\n6. UI Clickability:")
        print("   ⚠️ Check cursor style for incentive info")

    # Test 7: No hardcoding check
    print("\n7. No Hardcoding Check:")
    if "september_incentive || august_incentive" in content:
        print("   ❌ Hardcoded month fallback detected")
    else:
        print("   ✅ No hardcoded month fallback")

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)

    print("\n📊 Summary:")
    print("The dashboard should now:")
    print("  1. Show correct September incentive amounts")
    print("  2. Allow clicking on incentive amounts to show modal")
    print("  3. Display detailed subordinate information in modal")
    print("  4. Use dynamic month handling without hardcoding")

if __name__ == "__main__":
    test_dashboard_fixes()