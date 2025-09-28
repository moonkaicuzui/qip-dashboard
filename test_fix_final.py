#!/usr/bin/env python3
"""Final test of the ĐINH KIM NGOAN fix"""

import pandas as pd
import os

print("=== ĐINH KIM NGOAN FIX TEST ===\n")

# 1. Check source data
print("1. SOURCE DATA CHECK:")
source = pd.read_csv("input_files/2025년 9월 인센티브 지급 세부 정보.csv", encoding='utf-8-sig')
ngoan_source = source[source['Employee No'] == 617100049]
if not ngoan_source.empty:
    row = ngoan_source.iloc[0]
    print(f"   Found in source: YES")
    print(f"   Position: {row['QIP POSITION 1ST  NAME']}")
    print(f"   TYPE: {row['ROLE TYPE STD']}")
    print(f"   Source Final Incentive: {row.get('Final Incentive amount', 0)}")

# 2. Run calculation using action.sh
print("\n2. RUNNING CALCULATION:")
print("   Executing: ./action.sh")
os.system("./action.sh > /dev/null 2>&1")

# 3. Check output
print("\n3. OUTPUT CHECK:")
output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
if os.path.exists(output_file):
    df = pd.read_csv(output_file, encoding='utf-8-sig')

    # Check ĐINH KIM NGOAN
    ngoan = df[df['Employee No'] == 617100049]
    if not ngoan.empty:
        row = ngoan.iloc[0]
        sept = row.get('September_Incentive', 0)
        final = row.get('Final Incentive amount', 0)
        pass_rate = row.get('conditions_pass_rate', 0)

        print(f"   ĐINH KIM NGOAN (617100049):")
        print(f"   - Pass Rate: {pass_rate}%")
        print(f"   - September_Incentive: {sept:,.0f} VND")
        print(f"   - Final Incentive: {final:,.0f} VND")

        if final == 214720:
            print(f"   ✅ SUCCESS! Now receiving correct 214,720 VND!")
        elif final == 0:
            print(f"   ❌ STILL BROKEN: Still receiving 0 VND")
        else:
            print(f"   ⚠️ UNEXPECTED: Receiving {final:,.0f} VND")

    # Check other TYPE-2 GROUP LEADERs
    print("\n4. OTHER TYPE-2 GROUP LEADERs:")
    type2_gl = df[(df['ROLE TYPE STD'] == 'TYPE-2') &
                  (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') &
                  (df['conditions_pass_rate'] == 100)]

    for idx, row in type2_gl.iterrows():
        emp_no = row['Employee No']
        name = row['Full Name']
        final = row.get('Final Incentive amount', 0)
        print(f"   {emp_no} | {name[:20]:20} | {final:,.0f} VND")

    # Summary
    unique_amounts = type2_gl['Final Incentive amount'].unique()
    if len(unique_amounts) == 1 and unique_amounts[0] == 214720:
        print(f"\n   ✅ ALL TYPE-2 GROUP LEADERs get same amount: 214,720 VND")
    else:
        print(f"\n   ❌ UNFAIR: Different amounts: {unique_amounts}")

print("\n" + "=" * 60)
print("TEST COMPLETE")