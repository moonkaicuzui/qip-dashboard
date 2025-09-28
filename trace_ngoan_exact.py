#!/usr/bin/env python3
"""Trace exact calculation flow for ĐINH KIM NGOAN"""

import pandas as pd
import json
import os

print("=== ĐINH KIM NGOAN (617100049) EXACT TRACE ===\n")

# 1. Check source CSV
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
df_source = pd.read_csv(source_file, encoding='utf-8-sig')

ngoan_source = df_source[df_source['Employee No'] == '617100049']
if not ngoan_source.empty:
    row = ngoan_source.iloc[0]
    print("📁 SOURCE CSV DATA:")
    print(f"  Name: {row['Full Name']}")
    print(f"  Position: {row['QIP POSITION 1ST  NAME']}")
    print(f"  TYPE: {row['ROLE TYPE STD']}")
    print(f"  Final Incentive amount: {row.get('Final Incentive amount', 0):,.0f} VND")
    print(f"  September_Incentive: {row.get('September_Incentive', 0):,.0f} VND")

# 2. Check backup CSV (before modifications)
backup_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.backup.csv"
if os.path.exists(backup_file):
    df_backup = pd.read_csv(backup_file, encoding='utf-8-sig')
    ngoan_backup = df_backup[df_backup['Employee No'] == '617100049']
    if not ngoan_backup.empty:
        row = ngoan_backup.iloc[0]
        print(f"\n📁 BACKUP CSV DATA (Original Calculation):")
        print(f"  September_Incentive: {row.get('September_Incentive', 0):,.0f} VND")
        print(f"  September_Incentive: {row.get('september_incentive', 0):,.0f} VND")
        print(f"  Final Incentive amount: {row.get('Final Incentive amount', 0):,.0f} VND")

# 3. Check current output CSV
output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
df_output = pd.read_csv(output_file, encoding='utf-8-sig')

ngoan_output = df_output[df_output['Employee No'] == '617100049']
if not ngoan_output.empty:
    row = ngoan_output.iloc[0]
    print(f"\n📁 CURRENT OUTPUT CSV:")
    print(f"  September_Incentive: {row.get('September_Incentive', 0):,.0f} VND")
    print(f"  september_incentive: {row.get('september_incentive', 0):,.0f} VND")
    print(f"  Final Incentive amount: {row.get('Final Incentive amount', 0):,.0f} VND")

# 4. Check attendance conditions
print("\n🔍 ATTENDANCE CONDITIONS:")
if not ngoan_output.empty:
    row = ngoan_output.iloc[0]
    cond1 = row.get('attendancy condition 1 - acctual working days is zero', 'N/A')
    cond2 = row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'N/A')
    cond3 = row.get('attendancy condition 3 - absent % is over 12%', 'N/A')
    cond4 = row.get('attendancy condition 4 - minimum working days', 'N/A')

    print(f"  Condition 1 (working days = 0): {cond1}")
    print(f"  Condition 2 (unapproved >2): {cond2}")
    print(f"  Condition 3 (absent >12%): {cond3}")
    print(f"  Condition 4 (min working days): {cond4}")

    attendance_pass = (cond1 == 'no' and cond2 == 'no' and cond3 == 'no' and cond4 == 'no')
    print(f"  All attendance conditions passed: {attendance_pass}")
    print(f"  Conditions pass rate: {row.get('conditions_pass_rate', 0)}%")

# 5. Check other TYPE-2 GROUP LEADERs for comparison
print("\n🔍 OTHER TYPE-2 GROUP LEADERs:")
type2_gl = df_output[
    (df_output['ROLE TYPE STD'] == 'TYPE-2') &
    (df_output['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
]

for idx, row in type2_gl.iterrows():
    emp_no = row['Employee No']
    name = row['Full Name']
    pass_rate = row.get('conditions_pass_rate', 0)
    sept_inc = row.get('September_Incentive', 0)
    final_inc = row.get('Final Incentive amount', 0)

    status = "✅" if final_inc > 0 else "❌"
    print(f"{status} {emp_no} | {name[:20]:20} | Pass: {pass_rate:3.0f}% | Sept: {sept_inc:,.0f} | Final: {final_inc:,.0f}")

# 6. Check TYPE-2 LINE LEADER average (basis for GROUP LEADER calculation)
print("\n🔍 TYPE-2 LINE LEADER AVERAGE (for GROUP LEADER calculation):")
type2_line = df_output[
    (df_output['ROLE TYPE STD'] == 'TYPE-2') &
    (df_output['QIP POSITION 1ST  NAME'].str.contains('LINE', na=False)) &
    (df_output['QIP POSITION 1ST  NAME'].str.contains('LEADER', na=False))
]

if len(type2_line) > 0:
    receiving_line = type2_line[type2_line['September_Incentive'] > 0]
    if len(receiving_line) > 0:
        avg_line = receiving_line['September_Incentive'].mean()
        print(f"  TYPE-2 LINE LEADERs receiving incentive: {len(receiving_line)}")
        print(f"  Average LINE LEADER incentive: {avg_line:,.0f} VND")
        print(f"  Expected GROUP LEADER amount (avg × 2): {avg_line * 2:,.0f} VND")
    else:
        print(f"  ❌ No TYPE-2 LINE LEADERs receiving incentive!")

# 7. Check if there's a special condition in JSON
matrix_file = "config_files/position_condition_matrix.json"
with open(matrix_file, 'r', encoding='utf-8') as f:
    matrix = json.load(f)

print("\n🔍 POSITION CONDITION MATRIX:")
if 'GROUP LEADER' in matrix['positions']:
    gl_config = matrix['positions']['GROUP LEADER']
    print(f"  GROUP LEADER TYPE mapping: {gl_config['type_mapping']}")
    print(f"  CONDITIONS for TYPE-2: {gl_config['type_mapping'].get('TYPE-2', {}).get('conditions', [])}")

# 8. Check for any special remarks
print("\n🔍 SPECIAL REMARKS:")
if not ngoan_output.empty:
    row = ngoan_output.iloc[0]
    remark = row.get('RE MARK', '')
    stop_date = row.get('Stop working Date', '')

    print(f"  RE MARK: {remark if remark else 'None'}")
    print(f"  Stop working Date: {stop_date if stop_date else 'None'}")

print("\n" + "=" * 60)
print("ANALYSIS SUMMARY:")
print("=" * 60)

if not ngoan_output.empty:
    row = ngoan_output.iloc[0]
    pass_rate = row.get('conditions_pass_rate', 0)
    sept_inc = row.get('September_Incentive', 0)
    final_inc = row.get('Final Incentive amount', 0)

    if pass_rate == 100 and final_inc == 0:
        print("❌ PROBLEM CONFIRMED: 100% conditions met but 0 VND received")
        print("   This is unfair treatment compared to other GROUP LEADERs")
        print("\nPOSSIBLE CAUSES:")
        print("1. Source CSV already has Final=0 (data issue)")
        print("2. Calculation order issue (LINE LEADER average not available)")
        print("3. Hidden exclusion logic not in position_condition_matrix.json")
        print("4. September_Incentive vs september_incentive column naming issue")