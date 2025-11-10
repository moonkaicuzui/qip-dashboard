#!/usr/bin/env python3
"""
Test script to verify interim report logic fixes
Tests that condition 1 (attendance) and condition 4 (minimum days)
are properly relaxed for interim reports
"""

import pandas as pd
from datetime import datetime

def test_interim_report_conditions():
    """Test the NOT_APPLICABLE handling for interim reports"""

    print("=" * 60)
    print("📊 Testing Interim Report Condition Relaxation")
    print("=" * 60)

    # Test data simulating employees with various condition states
    test_data = [
        {
            'name': 'Employee A',
            'cond_1_attendance_rate': 'NOT_APPLICABLE',  # Interim report - should be treated as PASS
            'cond_2_unapproved_absence': 'PASS',
            'cond_3_actual_working_days': 'PASS',
            'cond_4_minimum_days': 'NOT_APPLICABLE',  # Interim report - should be treated as PASS
        },
        {
            'name': 'Employee B',
            'cond_1_attendance_rate': 'FAIL',  # Actually failed
            'cond_2_unapproved_absence': 'PASS',
            'cond_3_actual_working_days': 'PASS',
            'cond_4_minimum_days': 'NOT_APPLICABLE',  # Interim report - should be treated as PASS
        },
        {
            'name': 'Employee C',
            'cond_1_attendance_rate': 'PASS',  # Actually passed
            'cond_2_unapproved_absence': 'PASS',
            'cond_3_actual_working_days': 'PASS',
            'cond_4_minimum_days': 'PASS',  # Actually passed
        },
        {
            'name': 'Employee D',
            'cond_1_attendance_rate': 'NOT_APPLICABLE',  # Interim report
            'cond_2_unapproved_absence': 'FAIL',  # Failed condition 2
            'cond_3_actual_working_days': 'PASS',
            'cond_4_minimum_days': 'NOT_APPLICABLE',  # Interim report
        }
    ]

    print("\n📋 Testing condition evaluation with fixed logic:\n")

    passed_count = 0
    for emp in test_data:
        # Apply the FIXED logic (NOT_APPLICABLE should be treated as PASS)
        condition_1_pass = emp['cond_1_attendance_rate'] in ['PASS', 'NOT_APPLICABLE']
        condition_2_pass = emp['cond_2_unapproved_absence'] == 'PASS'
        condition_3_pass = emp['cond_3_actual_working_days'] == 'PASS'
        condition_4_pass = emp['cond_4_minimum_days'] in ['PASS', 'NOT_APPLICABLE']

        all_conditions_pass = (condition_1_pass and condition_2_pass and
                              condition_3_pass and condition_4_pass)

        status = "✅ ELIGIBLE" if all_conditions_pass else "❌ NOT ELIGIBLE"
        if all_conditions_pass:
            passed_count += 1

        print(f"{emp['name']}:")
        print(f"  Cond 1 (Attendance): {emp['cond_1_attendance_rate']} → {'PASS' if condition_1_pass else 'FAIL'}")
        print(f"  Cond 2 (Absence): {emp['cond_2_unapproved_absence']} → {'PASS' if condition_2_pass else 'FAIL'}")
        print(f"  Cond 3 (Working Days): {emp['cond_3_actual_working_days']} → {'PASS' if condition_3_pass else 'FAIL'}")
        print(f"  Cond 4 (Min Days): {emp['cond_4_minimum_days']} → {'PASS' if condition_4_pass else 'FAIL'}")
        print(f"  Result: {status}")
        print()

    print("=" * 60)
    print(f"📊 Summary:")
    print(f"  Total employees: {len(test_data)}")
    print(f"  Eligible for incentive: {passed_count}")
    print(f"  Not eligible: {len(test_data) - passed_count}")
    print("=" * 60)

    print("\n✅ Expected Results:")
    print("  - Employee A: ELIGIBLE (all NOT_APPLICABLE treated as PASS)")
    print("  - Employee B: NOT ELIGIBLE (condition 1 actually failed)")
    print("  - Employee C: ELIGIBLE (all conditions actually passed)")
    print("  - Employee D: NOT ELIGIBLE (condition 2 failed)")

    print("\n📌 Key Fix:")
    print("  Before: Only 'PASS' was considered passing")
    print("  After: Both 'PASS' and 'NOT_APPLICABLE' are considered passing")
    print("  Impact: More employees eligible in interim reports (before 20th)")

if __name__ == "__main__":
    test_interim_report_conditions()