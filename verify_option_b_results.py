#!/usr/bin/env python3
"""
Verify Option B implementation results for MODEL MASTER employees
"""

import pandas as pd
import json
import sys

print("="*80)
print("🔍 OPTION B VERIFICATION: MODEL MASTER INCENTIVE CHECK")
print("="*80)

# Check if Excel file has been updated
excel_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx'
csv_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'

print("\n[1] Checking position_condition_matrix.json for fallback positions...")
with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
    position_matrix = json.load(f)

if 'fallback_positions' in position_matrix:
    print("✅ Fallback positions found in configuration:")
    for pos_name, config in position_matrix['fallback_positions'].items():
        print(f"   - {pos_name}: {config.get('base_amount', 0):,} VND")
else:
    print("❌ No fallback positions found in configuration")

print("\n[2] Checking MODEL MASTER employees in CSV...")
df_csv = pd.read_csv(csv_file)

# Find MODEL MASTER employees
model_masters = df_csv[df_csv['QIP POSITION 1ST  NAME'] == 'MODEL MASTER']
print(f"\nFound {len(model_masters)} MODEL MASTER employees:")

total_before = 0
total_after = 0

for idx, row in model_masters.iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']
    final_code = row['FINAL QIP POSITION NAME CODE']

    # Check current incentive
    september_incentive = row.get('September_Incentive', 0)

    # Check conditions
    conditions_pass = row.get('conditions_pass_rate', 0)

    print(f"\n  [{idx+1}] {name} ({emp_no})")
    print(f"      Position Code: {final_code}")
    print(f"      Conditions Pass Rate: {conditions_pass}%")
    print(f"      September Incentive: {september_incentive:,.0f} VND")

    total_before += 0  # What they had before
    total_after += september_incentive

    # Check if using fallback
    if final_code not in position_matrix.get('positions', {}):
        print(f"      ✅ Using FALLBACK configuration (Code '{final_code}' not in matrix)")
    else:
        print(f"      ❌ Using standard configuration")

print("\n" + "-"*60)
print("📊 SUMMARY:")
print(f"  Total MODEL MASTER employees: {len(model_masters)}")
print(f"  Total incentive amount: {total_after:,.0f} VND")

# Check other unmapped codes
print("\n[3] Checking other unmapped position codes...")
unmapped_codes = ['D', 'Z', 'X', 'OF3', 'A4B', 'A2B']
unmapped_employees = df_csv[df_csv['FINAL QIP POSITION NAME CODE'].isin(unmapped_codes)]

print(f"\nTotal employees with unmapped codes: {len(unmapped_employees)}")

# Group by position name
position_groups = unmapped_employees.groupby('QIP POSITION 1ST  NAME').agg({
    'Employee No': 'count',
    'September_Incentive': 'sum'
}).rename(columns={'Employee No': 'Count', 'September_Incentive': 'Total_Incentive'})

print("\nBreakdown by position name:")
for pos_name, data in position_groups.iterrows():
    print(f"  {pos_name}: {data['Count']} employees, {data['Total_Incentive']:,.0f} VND")

# Final verification
print("\n" + "="*80)
if total_after > 0:
    print("✅ OPTION B IMPLEMENTATION SUCCESSFUL!")
    print(f"   MODEL MASTER employees are now receiving incentives: {total_after:,.0f} VND")
else:
    print("⚠️ OPTION B VERIFICATION ISSUE:")
    print("   MODEL MASTER employees still showing 0 incentive.")
    print("   Please run the full calculation pipeline:")
    print("   1. echo '4' | python src/step1_인센티브_계산_개선버전.py")
    print("   2. python integrated_dashboard_final.py --month 9 --year 2025")

print("="*80)