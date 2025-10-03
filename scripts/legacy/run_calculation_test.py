#!/usr/bin/env python3
"""Run the actual calculation with CSV that has no incentive columns"""

import pandas as pd
import shutil
import os
import sys

# First, backup current file
shutil.copy(
    "input_files/2025년 9월 인센티브 지급 세부 정보.csv",
    "input_files/original_with_zeros.csv"
)

# Replace with test file that has no incentive columns
shutil.copy(
    "input_files/test_no_incentive_columns.csv",
    "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
)

print("✅ Replaced source file with version without incentive columns")
print("Now running Python calculation script...")
print("=" * 50)

# Import and run the calculation
sys.path.append('src')
from step1_인센티브_계산_개선버전 import main as calculate_main

# Mock the input to avoid interactive prompts
class MockInput:
    def __init__(self):
        self.responses = ['9', '2025']  # September 2025
        self.index = 0

    def __call__(self, prompt=''):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            print(f"{prompt}{response}")  # Show what was auto-answered
            return response
        return ''

# Replace input with mock
import builtins
original_input = builtins.input
builtins.input = MockInput()

try:
    # Run the calculation
    calculate_main()

    print("\n" + "=" * 50)
    print("✅ Calculation completed!")

    # Check the results
    output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
    if os.path.exists(output_file):
        result_df = pd.read_csv(output_file, encoding='utf-8-sig')

        # Check TYPE-2 GROUP LEADERs
        type2_leaders = result_df[
            (result_df['ROLE TYPE STD'] == 'TYPE-2') &
            (result_df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
        ]

        print(f"\n=== CALCULATION RESULTS ===")
        print(f"TYPE-2 GROUP LEADERs found: {len(type2_leaders)}")

        # Check incentive columns
        sept_col = 'September_Incentive'
        final_col = 'Final Incentive amount'

        if sept_col in result_df.columns:
            print(f"\n{sept_col} distribution:")
            incentives = type2_leaders[sept_col].value_counts()
            for amount, count in incentives.items():
                print(f"  {amount:,.0f} VND: {count} people")

            # Check ĐINH KIM NGOAN specifically
            ngoan = type2_leaders[type2_leaders['Employee No'] == '617100049']
            if not ngoan.empty:
                print(f"\nĐINH KIM NGOAN (617100049):")
                print(f"  {sept_col}: {ngoan.iloc[0][sept_col]:,.0f} VND")
                if final_col in ngoan.columns:
                    print(f"  {final_col}: {ngoan.iloc[0][final_col]:,.0f} VND")

        # Check TYPE-1 averages (which TYPE-2 depends on)
        type1_leaders = result_df[
            (result_df['ROLE TYPE STD'] == 'TYPE-1') &
            (result_df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
        ]

        if len(type1_leaders) > 0 and sept_col in type1_leaders.columns:
            type1_avg = type1_leaders[sept_col].mean()
            print(f"\nTYPE-1 GROUP LEADER average: {type1_avg:,.0f} VND")
            print("(TYPE-2 GROUP LEADER incentive should be based on this)")
    else:
        print("❌ Output file not found")

except Exception as e:
    print(f"Error running calculation: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Restore original input
    builtins.input = original_input

    # Restore original file
    shutil.copy(
        "input_files/original_with_zeros.csv",
        "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
    )
    print("\n✅ Restored original source file")