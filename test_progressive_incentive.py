#!/usr/bin/env python3
"""
Progressive Incentive Logic Test Script
Verifies that TYPE-1 positions correctly track continuous months and incentive amounts
"""

import pandas as pd
import os
import json

def test_progressive_incentive():
    """Test the progressive incentive implementation"""

    print("="*60)
    print("🔍 Progressive Incentive Implementation Test")
    print("="*60)

    # 1. Run the incentive calculation first
    print("\n1️⃣ Running September 2025 incentive calculation...")
    result = os.system('cd "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일" && python src/step1_인센티브_계산_개선버전.py --config config_files/config_september_2025.json')

    if result != 0:
        print("❌ Failed to run incentive calculation")
        return False

    # 2. Load the output file
    output_file = '/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx'

    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False

    print(f"\n2️⃣ Loading output file: {output_file}")
    df = pd.read_excel(output_file)

    # 3. Check Model Masters
    print("\n3️⃣ Checking Model Masters progressive incentive...")
    model_masters = df[
        (df['ROLE TYPE STD'] == 'TYPE-1') &
        (df['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False))
    ]

    print(f"   Found {len(model_masters)} Model Masters")

    for idx, row in model_masters.iterrows():
        emp_id = row['Employee No']
        name = row['Full Name']
        incentive = row.get('September_Incentive', 0)
        continuous_months = row.get('Continuous_Months', 0)

        # Check if incentive and continuous months match
        if incentive == 300000 and continuous_months != 3:
            print(f"   ❌ {emp_id} ({name}): {incentive:,} VND but Continuous_Months={continuous_months} (should be 3)")
        elif incentive == 250000 and continuous_months != 2:
            print(f"   ❌ {emp_id} ({name}): {incentive:,} VND but Continuous_Months={continuous_months} (should be 2)")
        elif incentive == 350000 and continuous_months != 4:
            print(f"   ❌ {emp_id} ({name}): {incentive:,} VND but Continuous_Months={continuous_months} (should be 4)")
        elif incentive == 150000 and continuous_months != 1:
            print(f"   ❌ {emp_id} ({name}): {incentive:,} VND but Continuous_Months={continuous_months} (should be 1)")
        elif incentive > 0:
            print(f"   ✅ {emp_id} ({name}): {incentive:,} VND, Continuous_Months={continuous_months}")
        else:
            print(f"   ⚠️ {emp_id} ({name}): No incentive (0 VND), Continuous_Months={continuous_months}")

    # 4. Check Assembly Inspectors
    print("\n4️⃣ Checking Assembly Inspectors progressive incentive...")
    assembly_inspectors = df[
        (df['ROLE TYPE STD'] == 'TYPE-1') &
        (df['QIP POSITION 1ST  NAME'].str.contains('ASSEMBLY', na=False)) &
        (df['QIP POSITION 1ST  NAME'].str.contains('INSPECTOR', na=False))
    ]

    print(f"   Found {len(assembly_inspectors)} Assembly Inspectors")

    # Show a few examples
    for idx, row in assembly_inspectors.head(5).iterrows():
        emp_id = row['Employee No']
        name = row['Full Name']
        incentive = row.get('September_Incentive', 0)
        continuous_months = row.get('Continuous_Months', 0)

        if incentive > 0:
            print(f"   → {emp_id} ({name}): {incentive:,} VND, Continuous_Months={continuous_months}")

    # 5. Check Auditor/Trainers
    print("\n5️⃣ Checking Auditor/Trainers progressive incentive...")
    auditors = df[
        (df['ROLE TYPE STD'] == 'TYPE-1') &
        ((df['QIP POSITION 1ST  NAME'].str.contains('AUDIT', na=False)) |
         (df['QIP POSITION 1ST  NAME'].str.contains('TRAINER', na=False)) |
         (df['QIP POSITION 1ST  NAME'].str.contains('TRAINING', na=False)))
    ]

    # Exclude Model Masters
    auditors = auditors[~auditors['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False)]

    print(f"   Found {len(auditors)} Auditor/Trainers")

    # Show a few examples
    for idx, row in auditors.head(5).iterrows():
        emp_id = row['Employee No']
        name = row['Full Name']
        incentive = row.get('September_Incentive', 0)
        continuous_months = row.get('Continuous_Months', 0)

        if incentive > 0:
            print(f"   → {emp_id} ({name}): {incentive:,} VND, Continuous_Months={continuous_months}")

    # 6. Summary statistics
    print("\n6️⃣ Progressive Incentive Summary:")
    type1_employees = df[df['ROLE TYPE STD'] == 'TYPE-1']

    # Count by continuous months
    continuous_months_counts = type1_employees['Continuous_Months'].value_counts().sort_index()

    print("\n   Continuous Months Distribution:")
    for months, count in continuous_months_counts.items():
        if pd.notna(months):
            print(f"   {int(months)} months: {count} employees")

    # Check for mismatches between incentive amount and continuous months
    print("\n   Checking for mismatches...")

    # Expected mapping for Assembly Inspector/Model Master/Auditor
    expected_mapping = {
        150000: 1,
        250000: 2,
        300000: 3,
        350000: 4,
        400000: 5,
        450000: 6,
        500000: 7,
        650000: 8,
        750000: 9,
        850000: 10,
        950000: 11,
        1000000: 12
    }

    mismatches = []
    for idx, row in type1_employees.iterrows():
        if row['QIP POSITION 1ST  NAME'] and 'LINE LEADER' not in str(row['QIP POSITION 1ST  NAME']).upper():
            incentive = row.get('September_Incentive', 0)
            continuous_months = row.get('Continuous_Months', 0)

            if incentive in expected_mapping:
                expected_months = expected_mapping[incentive]
                if continuous_months != expected_months and continuous_months > 0:
                    mismatches.append({
                        'emp_id': row['Employee No'],
                        'name': row['Full Name'],
                        'position': row['QIP POSITION 1ST  NAME'],
                        'incentive': incentive,
                        'continuous_months': continuous_months,
                        'expected_months': expected_months
                    })

    if mismatches:
        print(f"\n   ⚠️ Found {len(mismatches)} mismatches:")
        for m in mismatches[:5]:  # Show first 5
            print(f"      {m['emp_id']} ({m['name']}): {m['incentive']:,} VND → {m['continuous_months']} months (expected {m['expected_months']})")
    else:
        print("\n   ✅ No mismatches found between incentive amounts and continuous months!")

    # 7. Load and check JSON file
    json_file = '/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/config_files/assembly_inspector_continuous_months.json'
    if os.path.exists(json_file):
        print(f"\n7️⃣ Checking JSON tracking file...")
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        if 'september_continuous_months' in json_data:
            sept_data = json_data['september_continuous_months']
            print(f"   JSON file has {len(sept_data)} entries for September")

            # Check a few entries
            for emp_id, months in list(sept_data.items())[:3]:
                df_row = df[df['Employee No'] == emp_id]
                if not df_row.empty:
                    df_months = df_row.iloc[0].get('Continuous_Months', 0)
                    if months != df_months:
                        print(f"   ❌ {emp_id}: JSON={months}, DataFrame={df_months}")
                    else:
                        print(f"   ✅ {emp_id}: JSON and DataFrame both show {months} months")

    print("\n" + "="*60)
    print("✅ Progressive Incentive Test Complete!")
    print("="*60)

    return True

if __name__ == '__main__':
    test_progressive_incentive()