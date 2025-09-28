#!/usr/bin/env python3
"""Check ĐINH KIM NGOAN's exact TYPE and position"""

import pandas as pd

# Check in source file
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
df_source = pd.read_csv(source_file, encoding='utf-8-sig')

ngoan_source = df_source[df_source['Employee No'] == '617100049']
if not ngoan_source.empty:
    row = ngoan_source.iloc[0]
    print("=== SOURCE CSV ===")
    print(f"Employee No: {row['Employee No']}")
    print(f"Full Name: {row['Full Name']}")
    print(f"QIP POSITION 1ST  NAME: '{row['QIP POSITION 1ST  NAME']}'")
    print(f"ROLE TYPE STD: '{row['ROLE TYPE STD']}'")
    print(f"Final Incentive amount: {row.get('Final Incentive amount', 0)}")

# Check in output file
output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
df_output = pd.read_csv(output_file, encoding='utf-8-sig')

ngoan_output = df_output[df_output['Employee No'] == '617100049']
if not ngoan_output.empty:
    row = ngoan_output.iloc[0]
    print("\n=== OUTPUT CSV ===")
    print(f"Employee No: {row['Employee No']}")
    print(f"Full Name: {row['Full Name']}")
    print(f"QIP POSITION 1ST  NAME: '{row['QIP POSITION 1ST  NAME']}'")
    print(f"ROLE TYPE STD: '{row['ROLE TYPE STD']}'")
    print(f"September_Incentive: {row.get('September_Incentive', 0)}")
    print(f"Final Incentive amount: {row.get('Final Incentive amount', 0)}")

    # Check if GROUP LEADER position is exactly matching
    print("\n=== POSITION CHECK ===")
    print(f"Position upper: '{row['QIP POSITION 1ST  NAME'].upper()}'")
    print(f"Is 'GROUP LEADER': {row['QIP POSITION 1ST  NAME'].upper() == 'GROUP LEADER'}")
    print(f"Contains 'GROUP': {'GROUP' in row['QIP POSITION 1ST  NAME'].upper()}")
    print(f"Contains 'LEADER': {'LEADER' in row['QIP POSITION 1ST  NAME'].upper()}")

    # Check TYPE
    print(f"\n=== TYPE CHECK ===")
    print(f"TYPE: '{row['ROLE TYPE STD']}'")
    print(f"Is TYPE-2: {row['ROLE TYPE STD'] == 'TYPE-2'}")
    print(f"TYPE stripped: '{row['ROLE TYPE STD'].strip() if pd.notna(row['ROLE TYPE STD']) else 'None'}'")

    # Check if she's somehow being marked as TYPE-3
    if row['ROLE TYPE STD'] == 'TYPE-3':
        print("\n⚠️ WARNING: ĐINH KIM NGOAN is marked as TYPE-3!")
    elif row['ROLE TYPE STD'] != 'TYPE-2':
        print(f"\n⚠️ WARNING: ĐINH KIM NGOAN TYPE is '{row['ROLE TYPE STD']}', not TYPE-2!")