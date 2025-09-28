#!/usr/bin/env python3
"""Find why ĐINH KIM NGOAN is getting 0 VND"""

import pandas as pd
import json

# Load source data
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
df = pd.read_csv(source_file, encoding='utf-8-sig')

# Find ĐINH KIM NGOAN (Employee No is stored as integer)
ngoan = df[df['Employee No'] == 617100049]

if ngoan.empty:
    print("❌ ĐINH KIM NGOAN not found in source data!")
else:
    row = ngoan.iloc[0]
    print("=== ĐINH KIM NGOAN DATA ===")
    print(f"Employee No: {row['Employee No']}")
    print(f"Name: {row['Full Name']}")
    print(f"Position: {row['QIP POSITION 1ST  NAME']}")
    print(f"TYPE: {row['ROLE TYPE STD']}")

    print("\n=== ATTENDANCE CONDITIONS ===")
    print(f"Condition 1 (working days = 0): {row.get('attendancy condition 1 - acctual working days is zero', 'N/A')}")
    print(f"Condition 2 (unapproved > 2): {row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'N/A')}")
    print(f"Condition 3 (absent > 12%): {row.get('attendancy condition 3 - absent % is over 12%', 'N/A')}")
    print(f"Condition 4 (min working days): {row.get('attendancy condition 4 - minimum working days', 'N/A')}")

    # Check if any condition fails
    cond1_fail = row.get('attendancy condition 1 - acctual working days is zero') == 'yes'
    cond2_fail = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes'
    cond3_fail = row.get('attendancy condition 3 - absent % is over 12%') == 'yes'
    cond4_fail = row.get('attendancy condition 4 - minimum working days') == 'yes'

    attendance_fail = cond1_fail or cond2_fail or cond3_fail or cond4_fail

    print(f"\nAttendance conditions fail: {attendance_fail}")
    if attendance_fail:
        if cond1_fail: print("  ❌ Condition 1 failed")
        if cond2_fail: print("  ❌ Condition 2 failed")
        if cond3_fail: print("  ❌ Condition 3 failed")
        if cond4_fail: print("  ❌ Condition 4 failed")
    else:
        print("  ✅ All attendance conditions passed")

    print("\n=== OTHER INFORMATION ===")
    print(f"Stop working Date: '{row.get('Stop working Date', '')}'")
    print(f"RE MARK: '{row.get('RE MARK', '')}'")
    print(f"Actual working days: {row.get('Actual working days', 'N/A')}")
    print(f"Total working days: {row.get('Total working days', 'N/A')}")
    print(f"conditions_pass_rate: {row.get('conditions_pass_rate', 'N/A')}%")

    print("\n=== INCENTIVE VALUES ===")
    print(f"September_Incentive: {row.get('September_Incentive', 0)}")
    print(f"Final Incentive amount: {row.get('Final Incentive amount', 0)}")

    # Check if GROUP LEADER position matches exactly
    print("\n=== POSITION MATCHING ===")
    pos_upper = row['QIP POSITION 1ST  NAME'].upper() if pd.notna(row['QIP POSITION 1ST  NAME']) else ''
    print(f"Position uppercase: '{pos_upper}'")
    print(f"Matches 'GROUP LEADER': {pos_upper == 'GROUP LEADER'}")
    print(f"Matches 'QA3A': {pos_upper == 'QA3A'}")

    # Check TYPE matching
    print("\n=== TYPE MATCHING ===")
    type_val = row['ROLE TYPE STD']
    print(f"TYPE value: '{type_val}'")
    print(f"Matches 'TYPE-2': {type_val == 'TYPE-2'}")

print("\n=== EXPECTED CALCULATION ===")
print("For TYPE-2 GROUP LEADER with all conditions passed:")
print("  Should get: TYPE-2 LINE LEADER average × 2")
print("  Expected: 107,360 × 2 = 214,720 VND")
print("\nBut ĐINH KIM NGOAN gets: 0 VND")
print("\n❌ This is the problem we need to fix!")