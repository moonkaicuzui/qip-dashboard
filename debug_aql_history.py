#!/usr/bin/env python3
"""
Debug script to check AQL history processing and data merging
"""

import sys
import pandas as pd
sys.path.append('src')

from step1_인센티브_계산_개선버전 import DataProcessor, ConfigManager

# Load config using static method
config = ConfigManager.load_config('config_files/config_september_2025.json')

# Create processor
processor = DataProcessor(config)

# Load main data
basic_data = pd.read_csv('input_files/basic manpower data september.csv', encoding='utf-8-sig')
processor.df = basic_data

# Process AQL with history
print("📊 Processing AQL conditions with history...")
aql_result = processor.process_aql_conditions_with_history()

print(f"\n✅ Returned DataFrame shape: {aql_result.shape}")
print(f"✅ Columns: {aql_result.columns.tolist()}")

# Check September AQL Failures column
sept_col = 'September AQL Failures'
if sept_col in aql_result.columns:
    non_zero = aql_result[aql_result[sept_col] > 0]
    print(f"\n📊 September AQL Failures:")
    print(f"  - Total employees: {len(aql_result)}")
    print(f"  - Employees with failures: {len(non_zero)}")
    print(f"  - Failure counts: {aql_result[sept_col].value_counts().to_dict()}")

    if len(non_zero) > 0:
        print(f"\n📋 Sample employees with failures:")
        print(non_zero[['Employee No', sept_col, 'Continuous_FAIL']].head(10))
else:
    print(f"❌ '{sept_col}' column not found!")

# Check if employee IDs match between datasets
print("\n📊 Employee ID matching:")
basic_ids = set(basic_data['Employee No'].astype(str).str.strip().str.zfill(9))
aql_ids = set(aql_result['Employee No'].astype(str).str.strip())

print(f"  - Basic data employees: {len(basic_ids)}")
print(f"  - AQL result employees: {len(aql_ids)}")
print(f"  - Common employees: {len(basic_ids & aql_ids)}")

# Sample ID comparison
print("\n📋 Sample IDs from each dataset:")
print(f"  Basic (first 5): {list(basic_ids)[:5]}")
print(f"  AQL (first 5): {list(aql_ids)[:5]}")