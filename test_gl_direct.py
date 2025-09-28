#!/usr/bin/env python3
"""Direct test of GROUP LEADER calculation logic"""

import pandas as pd
import numpy as np
import sys
sys.path.append('src')

print("=== DIRECT GROUP LEADER CALCULATION TEST ===\n")

# Load data
df = pd.read_csv("input_files/2025년 9월 인센티브 지급 세부 정보.csv", encoding='utf-8-sig')

# Initialize September_Incentive column
df['September_Incentive'] = 0

print("1. Calculating TYPE-2 LINE LEADERs first (Step 1)...")
# Calculate LINE LEADERs
line_leader_mask = (
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
)

for idx, row in df[line_leader_mask].iterrows():
    # Check attendance
    attendance_fail = (
        row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
        row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
        row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
        row.get('attendancy condition 4 - minimum working days') == 'yes'
    )

    if not attendance_fail:
        df.loc[idx, 'September_Incentive'] = 107360  # Default LINE LEADER value

line_leader_avg = df[line_leader_mask & (df['September_Incentive'] > 0)]['September_Incentive'].mean()
print(f"   LINE LEADER average: {line_leader_avg:,.0f} VND")

print("\n2. Calculating TYPE-2 GROUP LEADERs (Step 2)...")
# Calculate GROUP LEADERs
group_leader_mask = (
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
)

print(f"   Found {group_leader_mask.sum()} GROUP LEADERs")

for idx, row in df[group_leader_mask].iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']

    print(f"\n   Processing: {name} ({emp_no})")

    # Special check for ĐINH KIM NGOAN
    if emp_no == 617100049 or str(emp_no) == '617100049' or name.startswith('ĐINH KIM NGOAN'):
        print(f"   >>> ĐINH KIM NGOAN FOUND! <<<")

    # Check attendance
    attendance_fail = (
        row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
        row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
        row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
        row.get('attendancy condition 4 - minimum working days') == 'yes'
    )

    print(f"      Attendance fail: {attendance_fail}")

    # Calculate incentive
    if attendance_fail:
        incentive = 0
        reason = "attendance_fail"
    elif line_leader_avg > 0:
        incentive = int(line_leader_avg * 2)
        reason = f"LINE×2 ({line_leader_avg:.0f}×2)"
    else:
        incentive = 107360 * 2
        reason = "default (107360×2)"

    df.loc[idx, 'September_Incentive'] = incentive
    print(f"      Calculated: {incentive:,.0f} VND ({reason})")

print("\n3. Final Results:")
print("-" * 60)
for idx, row in df[group_leader_mask].iterrows():
    emp_no = row['Employee No']
    name = row['Full Name'][:20]
    sept = df.loc[idx, 'September_Incentive']

    if emp_no == 617100049:
        print(f">>> {emp_no} | {name:20} | {sept:8,.0f} VND <<<")
    else:
        print(f"    {emp_no} | {name:20} | {sept:8,.0f} VND")

# Save the results
df['Final Incentive amount'] = df['September_Incentive']
df.to_csv('test_output_direct.csv', index=False, encoding='utf-8-sig')
print("\nResults saved to test_output_direct.csv")