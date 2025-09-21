#!/usr/bin/env python3
"""
Verify consecutive AQL failure data in the dashboard HTML
"""

import json
import re
from pathlib import Path

def verify_dashboard_html():
    """Extract and verify consecutive failure data from dashboard HTML"""

    print("=" * 80)
    print("🔍 Dashboard HTML Consecutive Failure Verification")
    print("=" * 80)

    # Expected employees with consecutive failures
    jul_aug_expected = {622080106, 623030007, 623110220, 624020086, 624060384, 624080083, 625020179}
    aug_sep_expected = {622021338, 623090032, 623090194, 624030533, 624070060, 624080082, 624110274, 625030296}

    # Read the HTML file
    html_path = Path("output_files/Incentive_Dashboard_2025_09_Version_5.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract employeeData
    match = re.search(r'window\.employeeData = (\[.*?\]);', html, re.DOTALL)
    if not match:
        print("❌ Could not extract employeeData from HTML")
        return

    employee_data = json.loads(match.group(1))
    print(f"✅ Extracted {len(employee_data)} employees from dashboard HTML")

    # Find consecutive failures in dashboard
    jul_aug_found = []
    aug_sep_found = []
    all_three_found = []

    for emp in employee_data:
        emp_no = int(emp['Employee No']) if emp['Employee No'] else 0
        continuous_fail = emp.get('Continuous_FAIL', 'NO')

        if continuous_fail == '2MONTHS_JUL_AUG':
            jul_aug_found.append(emp_no)
        elif continuous_fail == '2MONTHS_AUG_SEP':
            aug_sep_found.append(emp_no)
        elif continuous_fail == '3MONTHS_JUL_AUG_SEP':
            all_three_found.append(emp_no)

    # Display results
    print(f"\n📊 Consecutive Failure Data in Dashboard:")
    print(f"  • Jul-Aug consecutive: {len(jul_aug_found)} employees")
    print(f"  • Aug-Sep consecutive: {len(aug_sep_found)} employees")
    print(f"  • All three months: {len(all_three_found)} employees")

    print(f"\n👥 Jul-Aug Consecutive Failures (7 expected):")
    for emp_no in sorted(jul_aug_found):
        status = "✅" if emp_no in jul_aug_expected else "❌ UNEXPECTED"
        print(f"    - {emp_no} {status}")

    print(f"\n👥 Aug-Sep Consecutive Failures (8 expected):")
    for emp_no in sorted(aug_sep_found):
        status = "✅" if emp_no in aug_sep_expected else "❌ UNEXPECTED"
        print(f"    - {emp_no} {status}")

    # Check for missing employees
    jul_aug_missing = jul_aug_expected - set(jul_aug_found)
    aug_sep_missing = aug_sep_expected - set(aug_sep_found)

    if jul_aug_missing:
        print(f"\n⚠️ Missing Jul-Aug failures: {jul_aug_missing}")
    if aug_sep_missing:
        print(f"\n⚠️ Missing Aug-Sep failures: {aug_sep_missing}")

    # Verification summary
    print("\n" + "=" * 80)
    print("✅ Verification Results:")
    print("=" * 80)

    jul_aug_correct = set(jul_aug_found) == jul_aug_expected
    aug_sep_correct = set(aug_sep_found) == aug_sep_expected
    all_three_correct = len(all_three_found) == 0

    print(f"  • Jul-Aug failures: {'✅ CORRECT' if jul_aug_correct else '❌ INCORRECT'} ({len(jul_aug_found)} found, 7 expected)")
    print(f"  • Aug-Sep failures: {'✅ CORRECT' if aug_sep_correct else '❌ INCORRECT'} ({len(aug_sep_found)} found, 8 expected)")
    print(f"  • All three months: {'✅ CORRECT' if all_three_correct else '❌ INCORRECT'} ({len(all_three_found)} found, 0 expected)")

    if jul_aug_correct and aug_sep_correct and all_three_correct:
        print("\n🎉 Dashboard HTML contains correct consecutive failure data!")
        print("✅ The user's concern about 50 Jul-Aug failures has been successfully resolved.")
        print("✅ Only 7 employees actually failed Jul-Aug consecutively (as verified).")
    else:
        print("\n⚠️ Some discrepancies found in dashboard HTML.")

    return {
        'jul_aug': jul_aug_found,
        'aug_sep': aug_sep_found,
        'all_three': all_three_found,
        'all_correct': jul_aug_correct and aug_sep_correct and all_three_correct
    }

if __name__ == "__main__":
    result = verify_dashboard_html()