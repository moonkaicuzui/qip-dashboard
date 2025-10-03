#!/usr/bin/env python3
"""Comprehensive comparison between original and improved dashboard calculations"""

import pandas as pd
import os
import sys
import json
from datetime import datetime

print("=== COMPREHENSIVE DASHBOARD COMPARISON ===\n")
print("Original (v5) vs Improved (v6) Dashboard Calculations")
print("=" * 60)

# Load both dashboard outputs
output_dir = "output_files"

# Load improved dashboard data
improved_csv = os.path.join(output_dir, "output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv")
if os.path.exists(improved_csv):
    df_improved = pd.read_csv(improved_csv, encoding='utf-8-sig')
    print(f"✅ Improved v6 loaded: {len(df_improved)} employees")
else:
    print("❌ Improved v6 CSV not found")
    sys.exit(1)

# Load original dashboard data (backup file contains original values)
backup_csv = os.path.join(output_dir, "output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.backup.csv")
if os.path.exists(backup_csv):
    df_original = pd.read_csv(backup_csv, encoding='utf-8-sig')
    print(f"✅ Original backup loaded: {len(df_original)} employees")
else:
    # Try other backup names
    backup_csv2 = os.path.join(output_dir, "output_backup_september_2025.csv")
    if os.path.exists(backup_csv2):
        df_original = pd.read_csv(backup_csv2, encoding='utf-8-sig')
        print(f"✅ Original backup loaded: {len(df_original)} employees")
    else:
        print("❌ Original backup data not found")
        sys.exit(1)

print("\n" + "=" * 60)

# 1. ĐINH KIM NGOAN specific analysis
print("\n📍 1. ĐINH KIM NGOAN (617100049) Analysis")
print("-" * 50)

ngoan_improved = df_improved[df_improved['Employee No'] == '617100049']
ngoan_original = df_original[df_original['Employee No'] == '617100049']

if not ngoan_improved.empty and not ngoan_original.empty:
    imp = ngoan_improved.iloc[0]
    org = ngoan_original.iloc[0]

    print(f"Name: {imp['Full Name']}")
    print(f"Position: {imp['QIP POSITION 1ST  NAME']}")
    print(f"TYPE: {imp['ROLE TYPE STD']}")
    print(f"\nCondition Fulfillment:")
    print(f"  Conditions Pass Rate: {imp.get('conditions_pass_rate', 0)}%")

    print(f"\n💰 Incentive Amounts:")
    print(f"  Original Dashboard:")
    print(f"    September_Incentive: {org.get('September_Incentive', 0):,.0f} VND")
    print(f"    Final Incentive: {org.get('Final Incentive amount', 0):,.0f} VND")
    print(f"  Improved Dashboard:")
    print(f"    September_Incentive: {imp.get('September_Incentive', 0):,.0f} VND")
    print(f"    Final Incentive: {imp.get('Final Incentive amount', 0):,.0f} VND")

    if imp.get('Final Incentive amount', 0) == 0:
        print(f"\n❌ STILL RECEIVING 0 VND - PROBLEM NOT FIXED!")
    else:
        print(f"\n✅ Fixed: Now receiving {imp.get('Final Incentive amount', 0):,.0f} VND")

# 2. All TYPE-2 GROUP LEADER comparison
print("\n\n📍 2. All TYPE-2 GROUP LEADERs Comparison")
print("-" * 50)

type2_gl_improved = df_improved[
    (df_improved['ROLE TYPE STD'] == 'TYPE-2') &
    (df_improved['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
]
type2_gl_original = df_original[
    (df_original['ROLE TYPE STD'] == 'TYPE-2') &
    (df_original['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
]

print(f"Found: {len(type2_gl_improved)} in improved, {len(type2_gl_original)} in original")

# Compare each GROUP LEADER
for idx, imp_row in type2_gl_improved.iterrows():
    emp_no = imp_row['Employee No']
    org_row = df_original[df_original['Employee No'] == emp_no]

    if not org_row.empty:
        org_row = org_row.iloc[0]
        imp_final = imp_row.get('Final Incentive amount', 0)
        org_final = org_row.get('Final Incentive amount', 0)

        status = "✅" if imp_final == org_final else "❌"
        print(f"{status} {emp_no} | {imp_row['Full Name'][:20]:20}")
        print(f"    Original: {org_final:,.0f} VND | Improved: {imp_final:,.0f} VND")

        if emp_no == '617100049':
            print(f"    ⚠️ ĐINH KIM NGOAN - Special case!")

# 3. Model Master comparison
print("\n\n📍 3. Model Master Team Comparison")
print("-" * 50)

model_master_improved = df_improved[
    df_improved['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False, case=False)
]
model_master_original = df_original[
    df_original['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False, case=False)
]

print(f"Found: {len(model_master_improved)} in improved, {len(model_master_original)} in original")

imp_avg = model_master_improved['Final Incentive amount'].mean() if len(model_master_improved) > 0 else 0
org_avg = model_master_original['Final Incentive amount'].mean() if len(model_master_original) > 0 else 0

print(f"Average Incentive:")
print(f"  Original: {org_avg:,.0f} VND")
print(f"  Improved: {imp_avg:,.0f} VND")

if abs(imp_avg - org_avg) < 1:
    print("✅ Model Master calculations match!")
else:
    print(f"❌ Model Master mismatch: Δ = {imp_avg - org_avg:,.0f} VND")

# 4. Position-level summary comparison
print("\n\n📍 4. Position-Level Summary Comparison")
print("-" * 50)

positions = ['GROUP LEADER', 'LINE LEADER', 'AUDITOR', 'TRAINER', 'ASSEMBLY INSPECTOR', 'MODEL MASTER']

for position in positions:
    pos_improved = df_improved[
        df_improved['QIP POSITION 1ST  NAME'].str.contains(position, na=False, case=False)
    ]
    pos_original = df_original[
        df_original['QIP POSITION 1ST  NAME'].str.contains(position, na=False, case=False)
    ]

    if len(pos_improved) > 0 or len(pos_original) > 0:
        imp_total = pos_improved['Final Incentive amount'].sum()
        org_total = pos_original['Final Incentive amount'].sum()
        imp_avg = pos_improved['Final Incentive amount'].mean() if len(pos_improved) > 0 else 0
        org_avg = pos_original['Final Incentive amount'].mean() if len(pos_original) > 0 else 0

        match = "✅" if abs(imp_total - org_total) < 1000 else "❌"
        print(f"\n{match} {position}")
        print(f"  Count: Original={len(pos_original)}, Improved={len(pos_improved)}")
        print(f"  Total: Original={org_total:,.0f}, Improved={imp_total:,.0f}")
        print(f"  Average: Original={org_avg:,.0f}, Improved={imp_avg:,.0f}")

        if abs(imp_total - org_total) >= 1000:
            print(f"  ⚠️ Discrepancy: Δ = {imp_total - org_total:,.0f} VND")

# 5. TYPE-level comparison
print("\n\n📍 5. TYPE-Level Summary Comparison")
print("-" * 50)

for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
    type_improved = df_improved[df_improved['ROLE TYPE STD'] == type_name]
    type_original = df_original[df_original['ROLE TYPE STD'] == type_name]

    imp_total = type_improved['Final Incentive amount'].sum()
    org_total = type_original['Final Incentive amount'].sum()
    imp_count = (type_improved['Final Incentive amount'] > 0).sum()
    org_count = (type_original['Final Incentive amount'] > 0).sum()

    match = "✅" if abs(imp_total - org_total) < 1000 else "❌"
    print(f"\n{match} {type_name}")
    print(f"  Recipients: Original={org_count}, Improved={imp_count}")
    print(f"  Total: Original={org_total:,.0f}, Improved={imp_total:,.0f}")

    if abs(imp_total - org_total) >= 1000:
        print(f"  ⚠️ Discrepancy: Δ = {imp_total - org_total:,.0f} VND")

# 6. Find all employees with calculation discrepancies
print("\n\n📍 6. All Employees with Discrepancies")
print("-" * 50)

discrepancies = []
for idx, imp_row in df_improved.iterrows():
    emp_no = imp_row['Employee No']
    org_row = df_original[df_original['Employee No'] == emp_no]

    if not org_row.empty:
        org_row = org_row.iloc[0]
        imp_amount = imp_row.get('Final Incentive amount', 0)
        org_amount = org_row.get('Final Incentive amount', 0)

        if abs(imp_amount - org_amount) > 1:  # Allow 1 VND tolerance
            discrepancies.append({
                'Employee No': emp_no,
                'Name': imp_row['Full Name'],
                'Position': imp_row['QIP POSITION 1ST  NAME'],
                'TYPE': imp_row['ROLE TYPE STD'],
                'Original': org_amount,
                'Improved': imp_amount,
                'Difference': imp_amount - org_amount
            })

if discrepancies:
    print(f"Found {len(discrepancies)} employees with discrepancies:\n")
    df_disc = pd.DataFrame(discrepancies)
    df_disc = df_disc.sort_values('Difference', ascending=False)

    print("Top 10 discrepancies:")
    for i, row in df_disc.head(10).iterrows():
        print(f"  {row['Employee No']} | {row['Name'][:20]:20} | {row['Position'][:15]:15}")
        print(f"    Original: {row['Original']:,.0f} | Improved: {row['Improved']:,.0f} | Δ: {row['Difference']:+,.0f}")

    # Save full discrepancy report
    disc_file = "discrepancy_report.csv"
    df_disc.to_csv(disc_file, index=False, encoding='utf-8-sig')
    print(f"\n📊 Full discrepancy report saved to: {disc_file}")
else:
    print("✅ No discrepancies found!")

# 7. Summary
print("\n\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)

total_original = df_original['Final Incentive amount'].sum()
total_improved = df_improved['Final Incentive amount'].sum()
recipients_original = (df_original['Final Incentive amount'] > 0).sum()
recipients_improved = (df_improved['Final Incentive amount'] > 0).sum()

print(f"Total Incentive Amount:")
print(f"  Original: {total_original:,.0f} VND")
print(f"  Improved: {total_improved:,.0f} VND")
print(f"  Difference: {total_improved - total_original:+,.0f} VND")

print(f"\nTotal Recipients:")
print(f"  Original: {recipients_original} employees")
print(f"  Improved: {recipients_improved} employees")
print(f"  Difference: {recipients_improved - recipients_original:+d} employees")

print(f"\nKey Issues:")
if ngoan_improved.iloc[0].get('Final Incentive amount', 0) == 0:
    print("  ❌ ĐINH KIM NGOAN still receiving 0 VND")
if len(discrepancies) > 0:
    print(f"  ❌ {len(discrepancies)} employees with calculation discrepancies")
if abs(imp_avg - org_avg) >= 1:
    print(f"  ❌ Model Master team calculations don't match")

print("\n" + "=" * 60)
print("Analysis Complete!")