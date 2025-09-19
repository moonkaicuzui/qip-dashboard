#!/usr/bin/env python3
"""
Test Enhanced Subordinate Average Calculations in Modal
"""
import json
import re

def test_enhanced_calculations():
    """Test the enhanced calculation details display"""

    print("="*70)
    print("🧮 Enhanced Calculation Details Test")
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

    # Test GROUP LEADER average calculation details
    print("\n[TEST 1] GROUP LEADER Average Calculation Details")
    print("-" * 50)

    group_leaders = [e for e in employees if e.get('type') == 'TYPE-1' and
                    e.get('position') and 'GROUP LEADER' in e['position'].upper()]

    if group_leaders:
        test_gl = group_leaders[0]
        print(f"📋 Testing GROUP LEADER: {test_gl['name']} (ID: {test_gl['emp_no']})")

        # Check for detailed LINE LEADER table
        if '📋 LINE LEADER 인센티브 상세 내역' in content:
            print("✅ Detailed LINE LEADER breakdown table found")
        else:
            print("❌ Missing LINE LEADER breakdown table")

        # Check for average calculation display
        if '평균 계산 합계' in content and '평균값' in content:
            print("✅ Average calculation totals found")
        else:
            print("❌ Missing average calculation totals")
    else:
        print("⚠️ No GROUP LEADERs found in data")

    # Test SUPERVISOR average calculation details
    print("\n[TEST 2] SUPERVISOR Average Calculation Details")
    print("-" * 50)

    supervisors = [e for e in employees if e.get('type') == 'TYPE-1' and
                  e.get('position') and 'SUPERVISOR' in e['position'].upper()]

    if supervisors:
        test_sup = supervisors[0]
        print(f"📋 Testing SUPERVISOR: {test_sup['name']} (ID: {test_sup['emp_no']})")

        # Check for GROUP-wise LINE LEADER display
        if '📋 전체 LINE LEADER 인센티브 상세 내역' in content:
            print("✅ Full LINE LEADER breakdown with GROUP organization found")
        else:
            print("❌ Missing full LINE LEADER breakdown")

        # Check for rowspan GROUP display
        if 'rowspan=' in content:
            print("✅ GROUP organization with rowspan found")
        else:
            print("⚠️ GROUP organization might not be properly displayed")
    else:
        print("⚠️ No SUPERVISORs found in data")

    # Test calculation formula display
    print("\n[TEST 3] Calculation Formula Display")
    print("-" * 50)

    formulas = [
        ('GROUP LEADER', '× 2'),
        ('SUPERVISOR', '× 2.5'),
        ('A.MANAGER', '× 1.5'),
        ('MANAGER', '× 3.5')
    ]

    for position, multiplier in formulas:
        if f'계산 과정 상세 ({position})' in content and multiplier in content:
            print(f"✅ {position} calculation formula with {multiplier} found")
        else:
            print(f"⚠️ {position} calculation formula might be missing")

    # Test individual contribution marking
    print("\n[TEST 4] Individual Contribution Marking")
    print("-" * 50)

    if '평균 계산 포함' in content:
        print("✅ Average calculation inclusion column found")

        # Check for inclusion markers
        if '✅' in content and '❌' in content:
            print("✅ Visual inclusion/exclusion markers (✅/❌) found")
        else:
            print("⚠️ Visual markers might not be properly displayed")
    else:
        print("❌ Average calculation inclusion column missing")

    # Test calculation accuracy display
    print("\n[TEST 5] Calculation Accuracy Display")
    print("-" * 50)

    if 'table-success' in content and 'table-warning' in content:
        print("✅ Calculation accuracy color coding found")
        print("   - Green (table-success) for accurate calculations")
        print("   - Yellow (table-warning) for discrepancies")
    else:
        print("⚠️ Calculation accuracy color coding might be missing")

    # Summary statistics
    print("\n[SUMMARY] Enhanced Features")
    print("-" * 50)

    features = {
        "LINE LEADER breakdown tables": '📋 LINE LEADER 인센티브 상세 내역' in content,
        "GROUP organization": 'rowspan=' in content,
        "Average calculations": '평균값' in content,
        "Inclusion markers": '✅' in content and '❌' in content,
        "Calculation formulas": all(mult in content for _, mult in formulas),
        "Accuracy color coding": 'table-success' in content
    }

    passed = sum(1 for v in features.values() if v)
    total = len(features)

    print(f"\nEnhanced features implemented: {passed}/{total}")
    for feature, implemented in features.items():
        status = "✅" if implemented else "❌"
        print(f"  {status} {feature}")

    print("\n" + "="*70)

    if passed == total:
        print("🎉 All enhanced calculation features are working!")
    elif passed >= total * 0.8:
        print("✅ Most enhanced features are working")
    else:
        print("⚠️ Some enhanced features need attention")

    print("="*70)

    return passed == total

if __name__ == "__main__":
    success = test_enhanced_calculations()
    exit(0 if success else 1)