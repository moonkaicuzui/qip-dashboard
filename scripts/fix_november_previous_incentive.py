#!/usr/bin/env python3
"""
Fix November 2025 Previous_Incentive from October V9.1 data

This script updates November CSV with correct Previous_Incentive values from October V9.1.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def fix_november_previous_incentive():
    """Update November Previous_Incentive from October V9.1"""

    root = Path(__file__).parent.parent

    # File paths
    october_file = root / "output_files/output_QIP_incentive_october_2025_Complete_V9.1_Complete.csv"
    november_file = root / "output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"

    print("=" * 80)
    print("🔧 November 2025 Previous_Incentive 수정")
    print("=" * 80)

    # Load October V9.1 data
    print(f"\n📥 Loading October V9.1 data...")
    print(f"   {october_file.name}")

    df_oct = pd.read_csv(october_file)
    print(f"   ✓ Loaded: {len(df_oct)} employees")

    # Check October columns
    oct_cols = [col for col in df_oct.columns if 'incentive' in col.lower() or 'final' in col.lower()]
    print(f"\n   October incentive columns:")
    for col in oct_cols:
        print(f"      • {col}")

    # Find the correct incentive column in October
    october_incentive_col = None
    for col in ['October_Incentive', 'Final_Incentive', 'November_Incentive', 'Final Incentive amount']:
        if col in df_oct.columns:
            october_incentive_col = col
            print(f"\n   ✓ Using October column: {october_incentive_col}")
            break

    if not october_incentive_col:
        print(f"\n   ❌ Cannot find October incentive column!")
        return False

    # Load November data
    print(f"\n📥 Loading November V9.0 data...")
    print(f"   {november_file.name}")

    df_nov = pd.read_csv(november_file)
    print(f"   ✓ Loaded: {len(df_nov)} employees")

    # Backup original file
    backup_file = november_file.parent / f"{november_file.stem}.backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_nov.to_csv(backup_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 Backup created: {backup_file.name}")

    # Find employee ID column
    emp_col = None
    for col in ['Employee No', 'EMP.NO', 'Emp No']:
        if col in df_oct.columns and col in df_nov.columns:
            emp_col = col
            break

    if not emp_col:
        print(f"\n❌ Cannot find employee ID column!")
        return False

    print(f"\n   ✓ Employee ID column: {emp_col}")

    # Create mapping: Employee No → October Incentive
    # Keep as int for matching
    oct_incentive_map = df_oct.set_index(emp_col)[october_incentive_col].to_dict()

    print(f"\n   📊 October incentive map sample:")
    for emp_no in list(oct_incentive_map.keys())[:3]:
        print(f"      {emp_no} ({type(emp_no).__name__}): {oct_incentive_map[emp_no]:,.0f} VND")

    # Update November Previous_Incentive
    print(f"\n🔄 Updating Previous_Incentive...")

    if 'Previous_Incentive' not in df_nov.columns:
        print(f"   ❌ Previous_Incentive column not found in November!")
        return False

    # Count changes
    changed_count = 0
    error_count = 0

    for idx, row in df_nov.iterrows():
        emp_no = row[emp_col]  # Keep as int, don't convert to str

        if emp_no in oct_incentive_map:
            old_value = row['Previous_Incentive']
            new_value = oct_incentive_map[emp_no]

            # Handle NaN
            if pd.isna(new_value):
                new_value = 0

            if old_value != new_value:
                df_nov.at[idx, 'Previous_Incentive'] = new_value
                changed_count += 1

                # Log specific employee 621040446
                if emp_no == 621040446:
                    print(f"\n   🎯 직원 621040446:")
                    print(f"      Old Previous_Incentive: {old_value:,.0f} VND")
                    print(f"      New Previous_Incentive: {new_value:,.0f} VND")
        else:
            error_count += 1

    print(f"\n   ✓ Changed: {changed_count} employees")
    if error_count > 0:
        print(f"   ⚠️  Not found in October: {error_count} employees")

    # Save updated November data
    print(f"\n💾 Saving updated November data...")
    df_nov.to_csv(november_file, index=False, encoding='utf-8-sig')
    print(f"   ✓ Saved: {november_file.name}")

    # Verify employee 621040446
    print(f"\n✅ Verification:")
    emp_621 = df_nov[df_nov[emp_col] == 621040446]

    if not emp_621.empty:
        emp_621 = emp_621.iloc[0]
        print(f"   직원 621040446:")
        print(f"      Previous_Incentive: {emp_621['Previous_Incentive']:,.0f} VND")

        # Check if it's correct (should be 1,000,000)
        if emp_621['Previous_Incentive'] == 1000000:
            print(f"      ✅ CORRECT!")
        else:
            print(f"      ⚠️  Expected: 1,000,000 VND")

    print("\n" + "=" * 80)
    print("✅ November Previous_Incentive 수정 완료!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = fix_november_previous_incentive()
    exit(0 if success else 1)
