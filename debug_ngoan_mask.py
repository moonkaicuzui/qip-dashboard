#!/usr/bin/env python3
"""Debug why ĐINH KIM NGOAN is not being calculated"""

import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv", encoding='utf-8-sig')

print("=== DEBUGGING TYPE-2 GROUP LEADER MASK ===\n")

# Create the mask exactly as in the calculation code
type2_group_mask = (
    (df['ROLE TYPE STD'] == 'TYPE-2') &
    ((df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') |
     (df['QIP POSITION 1ST  NAME'] == 'QA3A'))
)

print(f"Total TYPE-2 GROUP LEADER/QA3A: {type2_group_mask.sum()}")

# List all TYPE-2 GROUP LEADERs
type2_gl = df[type2_group_mask]
print("\nAll TYPE-2 GROUP LEADERs:")
for idx, row in type2_gl.iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']
    position = row['QIP POSITION 1ST  NAME']
    print(f"  {emp_no} | {name[:20]:20} | {position}")

# Check ĐINH KIM NGOAN specifically
print("\n=== ĐINH KIM NGOAN CHECK ===")
ngoan_mask = df['Employee No'] == 617100049
if ngoan_mask.sum() > 0:
    ngoan = df[ngoan_mask].iloc[0]
    print(f"Found: YES")
    print(f"Employee No: {ngoan['Employee No']} (type: {type(ngoan['Employee No'])})")
    print(f"Position: '{ngoan['QIP POSITION 1ST  NAME']}'")
    print(f"TYPE: '{ngoan['ROLE TYPE STD']}'")

    # Check each condition separately
    print("\nCondition checks:")
    print(f"  ROLE TYPE STD == 'TYPE-2': {ngoan['ROLE TYPE STD'] == 'TYPE-2'}")
    print(f"  Position == 'GROUP LEADER': {ngoan['QIP POSITION 1ST  NAME'] == 'GROUP LEADER'}")
    print(f"  Position == 'QA3A': {ngoan['QIP POSITION 1ST  NAME'] == 'QA3A'}")

    # Check if she's in the mask
    ngoan_idx = ngoan_mask.idxmax()
    print(f"\nIs in TYPE-2 GROUP LEADER mask: {type2_group_mask[ngoan_idx]}")

    if not type2_group_mask[ngoan_idx]:
        print("❌ ĐINH KIM NGOAN is NOT in the GROUP LEADER mask!")
        print("   This is why she's not getting calculated!")
else:
    print("❌ ĐINH KIM NGOAN not found!")

# Debug the loop behavior
print("\n=== SIMULATING CALCULATION LOOP ===")
for idx, row in df[type2_group_mask].iterrows():
    emp_id = row.get('Employee No', '')
    name = row.get('Full Name', '')

    # Check if this is ĐINH KIM NGOAN
    if str(emp_id) == '617100049':
        print(f"✅ ĐINH KIM NGOAN IS in the loop!")
        print(f"   emp_id: {emp_id} (type: {type(emp_id)})")
        print(f"   str(emp_id): '{str(emp_id)}'")
        break
else:
    print("❌ ĐINH KIM NGOAN is NOT in the loop!")