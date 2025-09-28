#!/usr/bin/env python3
"""Direct test of ĐINH KIM NGOAN calculation"""

import pandas as pd
import sys
import os

# Add src to path
sys.path.append('src')

# Load the data
output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
if os.path.exists(output_file):
    df = pd.read_csv(output_file, encoding='utf-8-sig')

    # Find ĐINH KIM NGOAN
    ngoan = df[df['Employee No'] == 617100049]
    if not ngoan.empty:
        row = ngoan.iloc[0]
        print("=== ĐINH KIM NGOAN Current Status ===")
        print(f"Employee No: {row['Employee No']} (type: {type(row['Employee No'])})")
        print(f"Name: {row['Full Name']}")
        print(f"Position: {row['QIP POSITION 1ST  NAME']}")
        print(f"TYPE: {row['ROLE TYPE STD']}")
        print(f"September_Incentive: {row.get('September_Incentive', 0):,.0f} VND")
        print(f"Final Incentive amount: {row.get('Final Incentive amount', 0):,.0f} VND")
        print(f"conditions_pass_rate: {row.get('conditions_pass_rate', 0)}%")
    else:
        print("❌ ĐINH KIM NGOAN not found in output")
else:
    print("❌ Output file not found")

print("\n=== Running fresh calculation ===")

# Import and run calculation
from step1_인센티브_계산_개선버전 import IncentiveCalculator

# Create calculator instance for September 2025
class Config:
    def __init__(self):
        self.month = type('obj', (object,), {'number': 9, 'name': 'september', 'korean': '9월'})()
        self.year = 2025

    def get_month_str(self, format_type):
        if format_type == 'capital':
            return 'September'
        elif format_type == 'lower':
            return 'september'
        elif format_type == 'korean':
            return '9월'
        else:
            return 'september'

config = Config()
calculator = IncentiveCalculator(config, base_path='.')

# Just test the GROUP LEADER calculation
print("\nLoading data...")
calculator.month_data = pd.read_csv("input_files/2025년 9월 인센티브 지급 세부 정보.csv", encoding='utf-8-sig')

# Initialize September_Incentive column
incentive_col = f"{config.get_month_str('capital')}_Incentive"
if incentive_col not in calculator.month_data.columns:
    calculator.month_data[incentive_col] = 0

print(f"Total employees: {len(calculator.month_data)}")

# Find TYPE-2 GROUP LEADERs
type2_group_mask = (
    (calculator.month_data['ROLE TYPE STD'] == 'TYPE-2') &
    (calculator.month_data['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
)
print(f"TYPE-2 GROUP LEADERs: {type2_group_mask.sum()}")

# Check ĐINH KIM NGOAN specifically
ngoan_mask = calculator.month_data['Employee No'] == 617100049
if ngoan_mask.sum() > 0:
    ngoan_row = calculator.month_data[ngoan_mask].iloc[0]
    print(f"\n✅ Found ĐINH KIM NGOAN:")
    print(f"  Employee No: {ngoan_row['Employee No']} (type: {type(ngoan_row['Employee No'])})")
    print(f"  Position: {ngoan_row['QIP POSITION 1ST  NAME']}")
    print(f"  TYPE: {ngoan_row['ROLE TYPE STD']}")
    print(f"  Is TYPE-2 GROUP LEADER: {type2_group_mask[ngoan_mask.index[0]]}")

    # Check str comparison
    emp_id = ngoan_row['Employee No']
    print(f"\nComparison tests:")
    print(f"  emp_id == '617100049': {emp_id == '617100049'}")
    print(f"  str(emp_id) == '617100049': {str(emp_id) == '617100049'}")
    print(f"  emp_id == 617100049: {emp_id == 617100049}")
else:
    print("❌ ĐINH KIM NGOAN not found in source data")