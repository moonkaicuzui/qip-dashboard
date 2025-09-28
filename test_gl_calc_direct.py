#!/usr/bin/env python3
"""Test GROUP LEADER calculation directly"""

import sys
import os
sys.path.append('src')

# Mock input for September 2025
class MockInput:
    def __init__(self):
        self.responses = [
            '3',      # Custom month
            '2025',   # Year
            '9',      # Month
            '23',     # Working days
            'yes',    # Create output
            'yes',    # Create config
            'yes'     # Create dashboard
        ]
        self.index = 0

    def __call__(self, prompt=''):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            print(f"{prompt}{response}")
            return response
        return ''

import builtins
builtins.input = MockInput()

print("=== RUNNING GROUP LEADER CALCULATION TEST ===\n")

from step1_인센티브_계산_개선버전 import main

# Redirect stdout to capture debug output
import io
from contextlib import redirect_stdout

f = io.StringIO()
with redirect_stdout(f):
    main()

output = f.getvalue()

# Find ĐINH KIM NGOAN debug output
if 'ĐINH KIM NGOAN' in output:
    print("Debug output found for ĐINH KIM NGOAN:")
    print("-" * 60)

    lines = output.split('\n')
    capturing = False
    for i, line in enumerate(lines):
        if 'ĐINH KIM NGOAN' in line or '617100049' in line:
            capturing = True
            # Print context around the match
            start = max(0, i-2)
            end = min(len(lines), i+10)
            for j in range(start, end):
                if j == i:
                    print(f">>> {lines[j]}")
                else:
                    print(f"    {lines[j]}")
            print()

# Check the output file
print("\n=== CHECKING OUTPUT FILE ===")
import pandas as pd
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv', encoding='utf-8-sig')

# Check ĐINH KIM NGOAN
ngoan = df[df['Employee No'] == 617100049]
if not ngoan.empty:
    row = ngoan.iloc[0]
    print(f"ĐINH KIM NGOAN (617100049):")
    print(f"  - September_Incentive: {row.get('September_Incentive', 0):,.0f} VND")
    print(f"  - Final Incentive: {row.get('Final Incentive amount', 0):,.0f} VND")
    print(f"  - Pass Rate: {row.get('conditions_pass_rate', 0)}%")

# Check other GROUP LEADERs
print("\nOther TYPE-2 GROUP LEADERs with 100% pass rate:")
type2_gl = df[(df['ROLE TYPE STD'] == 'TYPE-2') &
              (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') &
              (df['conditions_pass_rate'] == 100)]

for idx, row in type2_gl.iterrows():
    emp_no = row['Employee No']
    name = row['Full Name'][:20]
    sept = row.get('September_Incentive', 0)
    final = row.get('Final Incentive amount', 0)

    if emp_no != 617100049:
        print(f"  {emp_no} | {name:20} | Sept: {sept:8,.0f} | Final: {final:8,.0f} VND")