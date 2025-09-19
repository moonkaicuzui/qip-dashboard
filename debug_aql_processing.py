#!/usr/bin/env python3
"""
Debug AQL processing to understand why September failures are lost
"""

import pandas as pd
import sys
import os
import json

# Add src to path
sys.path.append('src')

# Import the CompleteQIPCalculator module
from step1_인센티브_계산_개선버전 import CompleteQIPCalculator, MonthConfig, DataProcessor, Month

# Create config for September
config = MonthConfig(
    year=2025,
    month=Month.SEPTEMBER,
    working_days=13,
    previous_months=[Month.JULY, Month.AUGUST],
    file_paths={},
    output_prefix='output_QIP_incentive_september_2025'
)

# Initialize data processor
data_processor = DataProcessor(config)

# Load the basic manpower data to provide employee list
basic_df = pd.read_csv('input_files/basic manpower data september.csv', encoding='utf-8-sig')
data_processor.df = basic_df

# Test the AQL processing function
print("=" * 80)
print("Testing AQL Processing with History")
print("=" * 80)

# Call the function
result_df = data_processor.process_aql_conditions_with_history()

# Check the result
print(f"\nResult DataFrame shape: {result_df.shape}")
print(f"Result DataFrame columns: {list(result_df.columns)}")

# Check September AQL Failures column
sept_col = "September AQL Failures"
if sept_col in result_df.columns:
    failures = result_df[result_df[sept_col] > 0]
    print(f"\n{sept_col} column found!")
    print(f"Total employees with failures: {len(failures)}")
    if len(failures) > 0:
        print("\nFirst 5 employees with failures:")
        for idx, row in failures.head().iterrows():
            print(f"  {row['Employee No']}: {row[sept_col]} failures")
else:
    print(f"\n❌ {sept_col} column NOT found in result!")
    print("Available columns with 'Fail' or 'AQL':")
    for col in result_df.columns:
        if 'Fail' in col or 'AQL' in col:
            print(f"  - {col}")

# Check a specific employee we know has failures
test_emp = '625060019'
test_row = result_df[result_df['Employee No'] == test_emp]
if not test_row.empty:
    print(f"\nEmployee {test_emp} data:")
    for col in result_df.columns:
        print(f"  {col}: {test_row.iloc[0][col]}")