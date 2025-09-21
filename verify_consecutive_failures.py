#!/usr/bin/env python3
"""
Verify consecutive AQL failure data in dashboard
"""

import pandas as pd
import json
from pathlib import Path

def verify_corrections():
    """Verify the corrected consecutive failure data"""

    print("=" * 80)
    print("🔍 Consecutive AQL Failure Data Verification")
    print("=" * 80)

    # Load the corrected Excel file
    csv_file = Path("output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_enhanced.csv")
    df = pd.read_csv(csv_file, encoding='utf-8-sig')

    # Count Continuous_FAIL values
    print("\n📊 Excel Data (Continuous_FAIL Distribution):")
    value_counts = df['Continuous_FAIL'].value_counts()
    for value, count in value_counts.items():
        print(f"  • {value}: {count} employees")

    # Load dashboard JSON data
    json_file = Path("output_files/dashboard_data_from_excel.json")
    with open(json_file, 'r', encoding='utf-8') as f:
        dashboard_data = json.load(f)

    # Extract employees with consecutive failures from JSON
    employees = dashboard_data.get('employee_data', [])

    jul_aug_failures = []
    aug_sep_failures = []
    all_three_failures = []

    for emp in employees:
        continuous_fail = emp.get('Continuous_FAIL', 'NO')
        if continuous_fail == '2MONTHS_JUL_AUG':
            jul_aug_failures.append(emp['Employee No'])
        elif continuous_fail == '2MONTHS_AUG_SEP':
            aug_sep_failures.append(emp['Employee No'])
        elif continuous_fail == '3MONTHS_JUL_AUG_SEP':
            all_three_failures.append(emp['Employee No'])

    print("\n📊 Dashboard JSON Data:")
    print(f"  • 2MONTHS_JUL_AUG: {len(jul_aug_failures)} employees")
    print(f"  • 2MONTHS_AUG_SEP: {len(aug_sep_failures)} employees")
    print(f"  • 3MONTHS_JUL_AUG_SEP: {len(all_three_failures)} employees")

    # List the specific employees
    print("\n👥 Employees with Jul-Aug Consecutive Failures (7 expected):")
    for emp_no in sorted(jul_aug_failures):
        print(f"    - {emp_no}")

    print(f"\n👥 Employees with Aug-Sep Consecutive Failures (8 expected):")
    for emp_no in sorted(aug_sep_failures):
        print(f"    - {emp_no}")

    # Verification summary
    print("\n" + "=" * 80)
    print("✅ Verification Results:")
    print("=" * 80)

    jul_aug_correct = len(jul_aug_failures) == 7
    aug_sep_correct = len(aug_sep_failures) == 8
    all_three_correct = len(all_three_failures) == 0

    print(f"  • Jul-Aug failures: {'✅ CORRECT' if jul_aug_correct else '❌ INCORRECT'} ({len(jul_aug_failures)} found, 7 expected)")
    print(f"  • Aug-Sep failures: {'✅ CORRECT' if aug_sep_correct else '❌ INCORRECT'} ({len(aug_sep_failures)} found, 8 expected)")
    print(f"  • All three months: {'✅ CORRECT' if all_three_correct else '❌ INCORRECT'} ({len(all_three_failures)} found, 0 expected)")

    if jul_aug_correct and aug_sep_correct and all_three_correct:
        print("\n🎉 All consecutive failure data is correctly updated!")
        print("📌 The issue of 50 employees incorrectly marked as Jul-Aug failures has been fixed.")
    else:
        print("\n⚠️ Some discrepancies found. Please review the data.")

    return {
        'jul_aug': jul_aug_failures,
        'aug_sep': aug_sep_failures,
        'all_three': all_three_failures
    }

if __name__ == "__main__":
    verify_corrections()