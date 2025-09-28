#!/usr/bin/env python3
"""Trace ĐINH KIM NGOAN's exact calculation path"""

import pandas as pd
import numpy as np

# Load the source data
df = pd.read_csv("input_files/2025년 9월 인센티브 지급 세부 정보.csv", encoding='utf-8-sig')

# Find ĐINH KIM NGOAN
ngoan_row = df[df['Employee No'] == 617100049]

if not ngoan_row.empty:
    row = ngoan_row.iloc[0]

    print("=== ĐINH KIM NGOAN CALCULATION TRACE ===\n")

    # 1. Check initial value from source
    source_sept = row.get('September_Incentive', 0)
    source_final = row.get('Final Incentive amount', 0)
    print(f"1. SOURCE VALUES:")
    print(f"   - September_Incentive: {source_sept}")
    print(f"   - Final Incentive amount: {source_final}")

    # 2. Check attendance conditions
    attendance_fail = (
        row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
        row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
        row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
        row.get('attendancy condition 4 - minimum working days') == 'yes'
    )
    print(f"\n2. ATTENDANCE CHECK:")
    print(f"   - attendance_fail: {attendance_fail}")

    # 3. Simulate the GROUP LEADER calculation
    print(f"\n3. GROUP LEADER CALCULATION SIMULATION:")

    # Get TYPE-1 GROUP average
    type1_group = df[(df['ROLE TYPE STD'] == 'TYPE-1') & (df['QIP POSITION 1ST  NAME'] == 'GROUP')]
    type1_group_avg = type1_group['Final Incentive amount'].mean() if len(type1_group) > 0 else 0
    print(f"   - TYPE-1 GROUP average: {type1_group_avg:,.0f}")

    # Get TYPE-2 LINE LEADER average
    type2_line = df[(df['ROLE TYPE STD'] == 'TYPE-2') & (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER')]
    type2_line_avg = type2_line['Final Incentive amount'].mean() if len(type2_line) > 0 else 0
    print(f"   - TYPE-2 LINE LEADER average: {type2_line_avg:,.0f}")

    # Calculate what she should get
    print(f"\n4. CALCULATION LOGIC:")
    print(f"   - Current value from source: {source_final}")
    print(f"   - Attendance fail: {attendance_fail}")

    if attendance_fail:
        calculated_value = 0
        print(f"   - Result: 0 (attendance failed)")
    elif source_final > 0:
        calculated_value = source_final
        print(f"   - Result: {calculated_value:,.0f} (using source value)")
    elif type1_group_avg > 0:
        calculated_value = type1_group_avg
        print(f"   - Result: {calculated_value:,.0f} (using TYPE-1 GROUP avg)")
    elif type2_line_avg > 0:
        calculated_value = type2_line_avg * 2
        print(f"   - Result: {calculated_value:,.0f} (using TYPE-2 LINE LEADER avg * 2)")
    else:
        calculated_value = 100000  # Default
        print(f"   - Result: {calculated_value:,.0f} (using default)")

    print(f"\n5. EXPECTED VS ACTUAL:")
    print(f"   - Expected (calculated): {calculated_value:,.0f} VND")
    print(f"   - Actual (in output): 0 VND")
    print(f"   - PROBLEM: She gets 0 instead of {calculated_value:,.0f}!")

    # Check other GROUP LEADERs for comparison
    print(f"\n6. OTHER GROUP LEADERS WITH SAME CONDITIONS:")
    other_gl = df[(df['ROLE TYPE STD'] == 'TYPE-2') &
                  (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') &
                  (df['Employee No'] != 617100049)]

    for idx, gl_row in other_gl.iterrows():
        gl_fail = (
            gl_row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
            gl_row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
            gl_row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
            gl_row.get('attendancy condition 4 - minimum working days') == 'yes'
        )

        if not gl_fail:  # Same as ĐINH KIM NGOAN
            emp_no = gl_row['Employee No']
            name = gl_row['Full Name'][:20]
            final = gl_row.get('Final Incentive amount', 0)
            print(f"   {emp_no} | {name:20} | Final: {final:,.0f} VND")