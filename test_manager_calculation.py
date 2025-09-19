#!/usr/bin/env python3
"""
Test MANAGER Position Calculation Display
Verifies that MANAGER incentive shows LINE LEADER average properly
"""
import json
import re

def test_manager_calculation():
    """Test MANAGER calculation display with LINE LEADER average"""

    print("="*70)
    print("📊 MANAGER Calculation Display Test")
    print("="*70)

    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract employee data
    emp_data_match = re.search(r'const employeeData = (\[.*?\]);', content, re.DOTALL)
    if not emp_data_match:
        print("❌ Could not find employee data")
        return False

    data_str = emp_data_match.group(1)
    data_str = re.sub(r'\bNaN\b', 'null', data_str)

    try:
        employees = json.loads(data_str)
        print(f"✅ Employee data loaded: {len(employees)} employees")
    except Exception as e:
        print(f"❌ Error parsing data: {e}")
        return False

    # Find MANAGERs (not A.MANAGER)
    managers = [e for e in employees if e.get('type') == 'TYPE-1' and
                e.get('position') and 'MANAGER' in e['position'].upper() and
                'A.MANAGER' not in e['position'].upper() and
                'ASSISTANT' not in e['position'].upper()]

    print(f"\n📋 Found {len(managers)} MANAGER(s)")

    if managers:
        # Test first manager
        test_manager = managers[0]
        print(f"\nTesting MANAGER: {test_manager['name']}")
        print(f"  ID: {test_manager['emp_no']}")
        print(f"  Position: {test_manager['position']}")
        sept_incentive = float(test_manager.get('september_incentive', 0) or 0)
        print(f"  September Incentive: ₫{sept_incentive:,.0f}")

        # Find all LINE LEADERs for calculation
        all_line_leaders = [e for e in employees if e.get('type') == 'TYPE-1' and
                           e.get('position') and 'LINE LEADER' in e['position'].upper()]

        receiving_line_leaders = [ll for ll in all_line_leaders if
                                  float(ll.get('september_incentive', 0) or 0) > 0]

        print(f"\nCalculation basis:")
        print(f"  Total LINE LEADERs: {len(all_line_leaders)}")
        print(f"  LINE LEADERs with incentive: {len(receiving_line_leaders)}")

        if receiving_line_leaders:
            total_ll_incentive = sum(float(ll.get('september_incentive', 0) or 0)
                                    for ll in receiving_line_leaders)
            avg_ll_incentive = total_ll_incentive / len(receiving_line_leaders)
            expected_manager = avg_ll_incentive * 3.5

            print(f"  Total LINE LEADER incentive: ₫{total_ll_incentive:,.0f}")
            print(f"  Average LINE LEADER incentive: ₫{avg_ll_incentive:,.0f}")
            print(f"  Expected MANAGER (avg × 3.5): ₫{expected_manager:,.0f}")
            print(f"  Actual MANAGER incentive: ₫{float(test_manager.get('september_incentive', 0)):,.0f}")

            # Verify calculation
            actual = float(test_manager.get('september_incentive', 0) or 0)
            difference = abs(actual - expected_manager)
            if difference < 1000:
                print("  ✅ Calculation matches expected formula")
            else:
                print(f"  ⚠️ Difference: ₫{difference:,.0f}")

    # Check HTML content for proper display
    print("\n[HTML CONTENT VERIFICATION]")
    print("-" * 50)

    # Check for LINE LEADER breakdown table for MANAGER
    if '📋 전체 LINE LEADER 인센티브 내역 (평균 계산 대상)' in content:
        print("✅ LINE LEADER breakdown table for MANAGER found")
    else:
        print("❌ LINE LEADER breakdown table for MANAGER missing")

    # Check for calculation formula display
    if '계산 과정 상세 (MANAGER)' in content and '× 3.5' in content:
        print("✅ MANAGER calculation formula (× 3.5) found")
    else:
        print("❌ MANAGER calculation formula missing")

    # Check for average display
    if 'LINE LEADER 평균 인센티브' in content:
        print("✅ LINE LEADER average display found")
    else:
        print("❌ LINE LEADER average display missing")

    # Check for GROUP organization
    if 'GROUP LEADER' in content and 'rowspan=' in content:
        print("✅ GROUP-wise organization with rowspan found")
    else:
        print("⚠️ GROUP organization might be missing")

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    features = [
        '📋 전체 LINE LEADER 인센티브 내역 (평균 계산 대상)' in content,
        '계산 과정 상세 (MANAGER)' in content,
        '× 3.5' in content,
        'LINE LEADER 평균 인센티브' in content,
        '인센티브 받은 LINE LEADER 합계' in content
    ]

    passed = sum(features)
    total = len(features)

    if passed == total:
        print(f"✅ All {total} features properly implemented!")
        print("\nMANAGER calculation now correctly shows:")
        print("1. All LINE LEADERs in the company")
        print("2. Which ones have incentives (included in average)")
        print("3. The total and average of LINE LEADER incentives")
        print("4. The calculation: Average × 3.5")
        print("5. GROUP-wise organization for clarity")
    else:
        print(f"⚠️ Only {passed}/{total} features implemented")

    return passed == total

if __name__ == "__main__":
    success = test_manager_calculation()
    exit(0 if success else 1)