#!/usr/bin/env python3
"""Debug GROUP LEADER calculation in detail"""

import pandas as pd
import numpy as np

# Load the source data
df = pd.read_csv("input_files/2025년 9월 인센티브 지급 세부 정보.csv", encoding='utf-8-sig')

print("=== DEBUGGING GROUP LEADER CALCULATION ===\n")

# Get TYPE-2 GROUP LEADERs
type2_gl_mask = (
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
)

print(f"1. TYPE-2 GROUP LEADERs found: {type2_gl_mask.sum()}")

# Get TYPE-1 GROUP average
type1_group = df[(df['ROLE TYPE STD'] == 'TYPE-1') & (df['QIP POSITION 1ST  NAME'] == 'GROUP')]
type1_group_avg = type1_group['Final Incentive amount'].mean() if len(type1_group) > 0 else 0
print(f"\n2. TYPE-1 GROUP average: {type1_group_avg:,.0f}")

# Get TYPE-2 LINE LEADER average
type2_line = df[(df['ROLE TYPE STD'] == 'TYPE-2') & (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER')]
type2_line_avg = type2_line['Final Incentive amount'].mean() if len(type2_line) > 0 else 0
print(f"3. TYPE-2 LINE LEADER average: {type2_line_avg:,.0f}")

print(f"\n4. GROUP LEADER calculation should use:")
if type1_group_avg > 0:
    print(f"   → TYPE-1 GROUP avg: {type1_group_avg:,.0f}")
elif type2_line_avg > 0:
    print(f"   → TYPE-2 LINE LEADER avg × 2: {type2_line_avg:,.0f} × 2 = {type2_line_avg * 2:,.0f}")
else:
    print(f"   → Default: 107360 × 2 = 214,720")

print("\n5. SIMULATING calculation for each GROUP LEADER:")
print("-" * 80)

for idx, row in df[type2_gl_mask].iterrows():
    emp_no = row['Employee No']
    name = row['Full Name'][:20]

    # Check attendance
    attendance_fail = (
        row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
        row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
        row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
        row.get('attendancy condition 4 - minimum working days') == 'yes'
    )

    # Calculate incentive
    if attendance_fail:
        calculated = 0
        reason = "attendance_fail"
    elif type1_group_avg > 0:
        calculated = type1_group_avg
        reason = "TYPE-1 GROUP avg"
    elif type2_line_avg > 0:
        calculated = type2_line_avg * 2
        reason = "TYPE-2 LINE×2"
    else:
        calculated = 107360 * 2
        reason = "default"

    source_final = row.get('Final Incentive amount', 0)

    print(f"{emp_no} | {name:20} | Fail:{str(attendance_fail):5} | Calc:{calculated:8,.0f} ({reason:15}) | Source:{source_final:8,.0f}")

    if emp_no == 617100049:
        print(f"   ⚠️ ĐINH KIM NGOAN: Should get {calculated:,.0f} but source has {source_final:,.0f}")

print("-" * 80)

# Check if the issue is with LINE LEADER calculation
print("\n6. TYPE-2 LINE LEADER values (for reference):")
for idx, row in type2_line.head(5).iterrows():
    emp_no = row['Employee No']
    name = row['Full Name'][:20]
    final = row.get('Final Incentive amount', 0)
    print(f"   {emp_no} | {name:20} | {final:,.0f} VND")