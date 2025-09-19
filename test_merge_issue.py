#!/usr/bin/env python3
"""
Test to identify why AQL failure data is lost during merge
"""

import pandas as pd
import sys
import os

# Add src to path
sys.path.append('src')

from step1_인센티브_계산_개선버전 import CompleteQIPCalculator, MonthConfig, DataProcessor, Month

print("=" * 80)
print("Testing AQL Data Merge Issue")
print("=" * 80)

# Create config for September
config = MonthConfig(
    year=2025,
    month=Month.SEPTEMBER,
    working_days=13,
    previous_months=[Month.JULY, Month.AUGUST],
    file_paths={},
    output_prefix='output_QIP_incentive_september_2025'
)

# Step 1: Load basic manpower data
print("\n1. Loading basic manpower data...")
basic_df = pd.read_csv('input_files/basic manpower data september.csv', encoding='utf-8-sig')
print(f"   Basic data shape: {basic_df.shape}")
print(f"   Employee No column exists: {'Employee No' in basic_df.columns}")

# Step 2: Get AQL data
print("\n2. Processing AQL data...")
data_processor = DataProcessor(config)
data_processor.df = basic_df
aql_conditions = data_processor.process_aql_conditions_with_history()
print(f"   AQL data shape: {aql_conditions.shape}")
print(f"   AQL columns: {list(aql_conditions.columns)}")

# Check September AQL Failures column
aql_col = "September AQL Failures"
if aql_col in aql_conditions.columns:
    fail_count = (aql_conditions[aql_col] > 0).sum()
    print(f"   {aql_col}: {fail_count} employees with failures")

# Step 3: Standardize Employee No in both dataframes
print("\n3. Standardizing Employee No...")

# Standardize basic_df
if 'Employee No' in basic_df.columns:
    basic_df['Employee No'] = basic_df['Employee No'].apply(
        lambda x: str(x).strip().zfill(9) if pd.notna(x) else ''
    )

# Standardize aql_conditions
aql_conditions['Employee No'] = aql_conditions['Employee No'].apply(
    lambda x: str(x).strip().zfill(9) if pd.notna(x) else ''
)

# Sample comparison
print(f"   Basic Employee No sample: {basic_df['Employee No'].iloc[:3].tolist()}")
print(f"   AQL Employee No sample: {aql_conditions['Employee No'].iloc[:3].tolist()}")

# Step 4: Perform merge
print("\n4. Merging data...")
merged_df = pd.merge(
    basic_df,
    aql_conditions,
    on='Employee No',
    how='left'
)
print(f"   Merged data shape: {merged_df.shape}")
print(f"   Merged columns with 'AQL': {[c for c in merged_df.columns if 'AQL' in c]}")

# Check if data is preserved
if aql_col in merged_df.columns:
    merged_fail_count = (merged_df[aql_col] > 0).sum()
    print(f"   After merge: {merged_fail_count} employees with failures")

    # Check specific employee
    test_emp = '625060019'
    test_row = merged_df[merged_df['Employee No'] == test_emp]
    if not test_row.empty:
        print(f"\n   Employee {test_emp} after merge:")
        print(f"   - {aql_col}: {test_row.iloc[0][aql_col]}")

# Step 5: Check what happens with fillna
print("\n5. Testing fillna operation...")
if aql_col not in merged_df.columns:
    print(f"   Creating {aql_col} column with 0")
    merged_df[aql_col] = 0
else:
    print(f"   Filling NaN values in {aql_col} with 0")
    before_fillna = (merged_df[aql_col] > 0).sum()
    merged_df[aql_col] = merged_df[aql_col].fillna(0)
    after_fillna = (merged_df[aql_col] > 0).sum()
    print(f"   Before fillna: {before_fillna} employees with failures")
    print(f"   After fillna: {after_fillna} employees with failures")

# Step 6: Check for duplicate columns
print("\n6. Checking for duplicate or conflicting columns...")
all_cols = list(merged_df.columns)
for col in all_cols:
    if 'AQL' in col or 'Fail' in col:
        print(f"   - {col}")

print("\n" + "=" * 80)
print("Analysis Complete")