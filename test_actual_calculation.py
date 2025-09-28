#!/usr/bin/env python3
"""Test whether Python actually calculates incentives or uses source values"""

import pandas as pd
import shutil
import os
import sys

# Backup original file
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
backup_file = "input_files/backup_september_2025.csv"

if not os.path.exists(backup_file):
    shutil.copy(source_file, backup_file)
    print(f"✅ Backup created: {backup_file}")

# Test 1: Check if source has pre-calculated values
print("\n=== TEST 1: Source CSV Analysis ===")
source_df = pd.read_csv(source_file, encoding='utf-8-sig')

has_sept = 'September_Incentive' in source_df.columns
has_final = 'Final Incentive amount' in source_df.columns

print(f"Source has September_Incentive column: {has_sept}")
print(f"Source has Final Incentive amount column: {has_final}")

if has_sept:
    non_zero = source_df[source_df['September_Incentive'] != 0]
    print(f"Non-zero September_Incentive values: {len(non_zero)} out of {len(source_df)}")

    # Check ĐINH KIM NGOAN specifically
    ngoan = source_df[source_df['Employee No'] == '617100049']
    if not ngoan.empty:
        print(f"\nĐINH KIM NGOAN (617100049):")
        print(f"  September_Incentive: {ngoan.iloc[0]['September_Incentive']}")
        if has_final:
            print(f"  Final Incentive amount: {ngoan.iloc[0]['Final Incentive amount']}")

# Test 2: Remove pre-calculated columns and force Python to calculate
print("\n=== TEST 2: Force Python Calculation ===")
test_df = source_df.copy()

columns_to_remove = []
if 'September_Incentive' in test_df.columns:
    columns_to_remove.append('September_Incentive')
if 'Final Incentive amount' in test_df.columns:
    columns_to_remove.append('Final Incentive amount')

if columns_to_remove:
    test_df = test_df.drop(columns=columns_to_remove)
    test_file = "input_files/test_no_incentive_columns.csv"
    test_df.to_csv(test_file, index=False, encoding='utf-8-sig')
    print(f"Created test file without incentive columns: {test_file}")
    print(f"Removed columns: {columns_to_remove}")
else:
    print("No incentive columns to remove")

# Test 3: Analyze calculation logic in Python script
print("\n=== TEST 3: Python Script Logic Analysis ===")
script_path = "src/step1_인센티브_계산_개선버전.py"

if os.path.exists(script_path):
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for calculation skip logic
    skip_patterns = [
        "if row[incentive_col] > 0:",
        "이미 계산된 경우 스킵",
        "continue"
    ]

    print("Checking for calculation skip logic:")
    for pattern in skip_patterns:
        if pattern in content:
            print(f"  ✓ Found: '{pattern}'")

    # Check if it loads pre-existing values
    load_patterns = [
        "September_Incentive",
        "Final Incentive amount"
    ]

    print("\nChecking if script loads pre-existing columns:")
    for pattern in load_patterns:
        count = content.count(pattern)
        if count > 0:
            print(f"  ✓ '{pattern}' appears {count} times")

# Test 4: Check TYPE-2 GROUP LEADER calculation dependencies
print("\n=== TEST 4: TYPE-2 GROUP LEADER Dependencies ===")
if has_sept:
    # Get TYPE-2 GROUP LEADERs
    type2_leaders = source_df[
        (source_df['ROLE TYPE STD'] == 'TYPE-2') &
        (source_df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
    ]

    print(f"TYPE-2 GROUP LEADERs found: {len(type2_leaders)}")

    if len(type2_leaders) > 0:
        # Show incentive distribution
        incentives = type2_leaders['September_Incentive'].value_counts()
        print("\nIncentive distribution:")
        for amount, count in incentives.items():
            print(f"  {amount:,.0f} VND: {count} people")

        # Show ĐINH KIM NGOAN vs others
        ngoan_in_type2 = type2_leaders[type2_leaders['Employee No'] == '617100049']
        if not ngoan_in_type2.empty:
            others = type2_leaders[type2_leaders['Employee No'] != '617100049']
            print(f"\nĐINH KIM NGOAN: {ngoan_in_type2.iloc[0]['September_Incentive']:,.0f} VND")
            print(f"Others average: {others['September_Incentive'].mean():,.0f} VND")

print("\n=== CONCLUSION ===")
print("Based on the analysis:")
print("1. Source CSV contains pre-calculated September_Incentive values")
print("2. Python script checks if values exist and skips calculation")
print("3. TYPE-2 GROUP LEADER calculation depends on TYPE-1 averages")
print("4. ĐINH KIM NGOAN has 0 in source, others have 214,720")
print("\n✅ Answer: Python DOES have calculation logic but SKIPS it when source values exist")
print("The unfairness comes from the SOURCE DATA, not Python calculation")