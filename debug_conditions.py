#!/usr/bin/env python3
"""Debug ĐINH KIM NGOAN's attendance conditions"""

import pandas as pd

# Load the source data (before calculation)
df = pd.read_csv("input_files/2025년 9월 인센티브 지급 세부 정보.csv", encoding='utf-8-sig')

# Find ĐINH KIM NGOAN
ngoan = df[df['Employee No'] == 617100049]

if not ngoan.empty:
    row = ngoan.iloc[0]
    print("=== ĐINH KIM NGOAN SOURCE DATA CONDITIONS ===\n")

    # Check each condition individually
    cond1 = row.get('attendancy condition 1 - acctual working days is zero', 'N/A')
    cond2 = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'N/A')
    cond3 = row.get('attendancy condition 3 - absent % is over 12%', 'N/A')
    cond4 = row.get('attendancy condition 4 - minimum working days', 'N/A')

    print(f"Condition 1 (working days = 0): '{cond1}'")
    print(f"Condition 2 (unapproved > 2): '{cond2}'")
    print(f"Condition 3 (absent > 12%): '{cond3}'")
    print(f"Condition 4 (min working days): '{cond4}'")

    print("\n=== FAILURE CHECK (as in calculation code) ===")
    print("attendance_fail = (")
    print(f"    row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or  # {cond1} == 'yes' -> {cond1 == 'yes'}")
    print(f"    row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or  # {cond2} == 'yes' -> {cond2 == 'yes'}")
    print(f"    row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or  # {cond3} == 'yes' -> {cond3 == 'yes'}")
    print(f"    row.get('attendancy condition 4 - minimum working days') == 'yes'  # {cond4} == 'yes' -> {cond4 == 'yes'}")
    print(")")

    # Calculate the actual failure result
    attendance_fail = (
        cond1 == 'yes' or
        cond2 == 'yes' or
        cond3 == 'yes' or
        cond4 == 'yes'
    )

    print(f"\nResult: attendance_fail = {attendance_fail}")

    if attendance_fail:
        print("❌ ATTENDANCE FAILED - This is why she gets 0!")
        if cond1 == 'yes': print("   - Failed condition 1")
        if cond2 == 'yes': print("   - Failed condition 2")
        if cond3 == 'yes': print("   - Failed condition 3")
        if cond4 == 'yes': print("   - Failed condition 4")
    else:
        print("✅ All attendance conditions passed")
        print("   She should get 214,720 VND")

    print("\n=== OTHER TYPE-2 GROUP LEADERs FOR COMPARISON ===")
    type2_gl = df[(df['ROLE TYPE STD'] == 'TYPE-2') &
                  (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')]

    for idx, gl_row in type2_gl.iterrows():
        emp_no = gl_row['Employee No']
        name = gl_row['Full Name'][:20]
        c1 = gl_row.get('attendancy condition 1 - acctual working days is zero', 'N/A')
        c2 = gl_row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'N/A')
        c3 = gl_row.get('attendancy condition 3 - absent % is over 12%', 'N/A')
        c4 = gl_row.get('attendancy condition 4 - minimum working days', 'N/A')

        fail = (c1 == 'yes' or c2 == 'yes' or c3 == 'yes' or c4 == 'yes')

        print(f"{emp_no} | {name:20} | c1:{c1} c2:{c2} c3:{c3} c4:{c4} | Fail:{fail}")