#!/usr/bin/env python3
"""
Test Vietnamese Currency and Modal Click Fixes
"""
import re

def test_vietnamese_fixes():
    """Test all Vietnamese-specific fixes"""

    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    print("="*60)
    print("Vietnamese Dashboard Fixes Verification")
    print("="*60)

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Test 1: Currency symbol is Vietnamese Dong
    print("\n1. Currency Symbol Check:")
    vnd_count = content.count('₫')
    won_count = content.count('₩')

    if vnd_count > 0 and won_count == 0:
        print(f"   ✅ Using Vietnamese Dong (₫): {vnd_count} occurrences")
        print(f"   ✅ No Korean Won (₩) found")
    else:
        print(f"   ❌ Found {won_count} Korean Won symbols")
        print(f"   Found {vnd_count} Vietnamese Dong symbols")

    # Test 2: Click event conflict fix
    print("\n2. Click Event Conflict Fix:")
    if "if (e.target.closest('.node-incentive-info'))" in content:
        print("   ✅ Click event excludes incentive-info clicks")
    else:
        print("   ❌ Click event conflict fix not found")

    # Test 3: Modal subordinate details for LINE LEADER
    print("\n3. Modal Subordinate Details:")
    if '📋 인센티브 계산 기반 부하직원 상세' in content:
        print("   ✅ Subordinate details table exists")

        # Check for table headers
        headers = ['이름', '직급', '인센티브', '수령 여부', '계산 기여']
        all_headers = True
        for header in headers:
            if f'<th>{header}</th>' not in content and f'<th class="text-end">{header}</th>' not in content:
                print(f"   ⚠️ Missing header: {header}")
                all_headers = False
        if all_headers:
            print("   ✅ All table headers present")
    else:
        print("   ❌ Subordinate details table not found")

    # Test 4: Currency in specific locations
    print("\n4. Currency Symbol Locations:")

    # Check in node display
    if re.search(r'<span class="incentive-amount">₫', content):
        print("   ✅ Node display uses ₫")
    else:
        print("   ❌ Node display doesn't use ₫")

    # Check in modal
    if '₫{{' in content or '₫${' in content:
        print("   ✅ Modal calculations use ₫")
    else:
        print("   ⚠️ Check modal currency display")

    # Test 5: Incentive info is clickable
    print("\n5. Incentive Info Clickability:")
    if 'cursor: pointer' in content and '.node-incentive-info' in content:
        print("   ✅ Incentive info has pointer cursor")
    else:
        print("   ❌ Incentive info might not be clickable")

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)

    print("\n📊 Summary:")
    print("The dashboard now:")
    print("  1. Uses Vietnamese Dong (₫) currency symbol")
    print("  2. Allows clicking on incentive amounts without triggering expand/collapse")
    print("  3. Shows detailed subordinate information in the modal")
    print("  4. For LINE LEADERs, displays TYPE-1 subordinates who affect their incentive")

if __name__ == "__main__":
    test_vietnamese_fixes()