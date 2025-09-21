#!/usr/bin/env python3
"""
Fix consecutive AQL failure data by analyzing actual AQL history files
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_consecutive_aql_failures():
    """Analyze AQL history files to find actual consecutive failures"""

    print("=" * 80)
    print("🔍 Analyzing Actual Consecutive AQL Failures")
    print("=" * 80)

    # Read AQL history files
    july_file = Path("input_files/AQL history/1.HSRG AQL REPORT-JULY.2025.csv")
    august_file = Path("input_files/AQL history/1.HSRG AQL REPORT-AUGUST.2025.csv")
    september_file = Path("input_files/AQL history/1.HSRG AQL REPORT-SEPTEMBER.2025.csv")

    # Read each month's data
    july_df = pd.read_csv(july_file, encoding='utf-8-sig')
    august_df = pd.read_csv(august_file, encoding='utf-8-sig')
    september_df = pd.read_csv(september_file, encoding='utf-8-sig')

    # Get unique employees who failed each month
    # RESULT = 'FAIL' indicates failure
    # Convert to int to match Excel format
    july_failures = set(july_df[july_df['RESULT'] == 'FAIL']['EMPLOYEE NO'].dropna().astype(int).unique())
    august_failures = set(august_df[august_df['RESULT'] == 'FAIL']['EMPLOYEE NO'].dropna().astype(int).unique())
    september_failures = set(september_df[september_df['RESULT'] == 'FAIL']['EMPLOYEE NO'].dropna().astype(int).unique())

    # Find consecutive failures
    jul_aug_consecutive = july_failures & august_failures
    aug_sep_consecutive = august_failures & september_failures
    all_three_consecutive = july_failures & august_failures & september_failures

    print(f"\n📊 AQL Failure Analysis:")
    print(f"  • July failures: {len(july_failures)} employees")
    print(f"  • August failures: {len(august_failures)} employees")
    print(f"  • September failures: {len(september_failures)} employees")

    print(f"\n🔗 Consecutive Failures:")
    print(f"  • Jul-Aug consecutive: {len(jul_aug_consecutive)} employees")
    print(f"  • Aug-Sep consecutive: {len(aug_sep_consecutive)} employees")
    print(f"  • All three months: {len(all_three_consecutive)} employees")

    # List the specific employees
    print(f"\n👥 Employees with Jul-Aug Consecutive Failures:")
    for emp in sorted(jul_aug_consecutive):
        print(f"    - {emp}")

    print(f"\n👥 Employees with Aug-Sep Consecutive Failures:")
    for emp in sorted(aug_sep_consecutive):
        print(f"    - {emp}")

    print(f"\n👥 Employees with All Three Months Failures:")
    for emp in sorted(all_three_consecutive):
        print(f"    - {emp}")

    return {
        'jul_aug': jul_aug_consecutive,
        'aug_sep': aug_sep_consecutive,
        'all_three': all_three_consecutive
    }

def update_excel_with_correct_data(consecutive_failures):
    """Update the Excel file with correct consecutive failure data"""

    print("\n" + "=" * 80)
    print("📝 Updating Excel with Correct Data")
    print("=" * 80)

    # Read the current Excel file
    csv_file = Path("output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_enhanced.csv")
    df = pd.read_csv(csv_file, encoding='utf-8-sig')

    # Reset all Continuous_FAIL to "NO" first
    df['Continuous_FAIL'] = 'NO'

    # Mark employees with consecutive failures
    for idx, row in df.iterrows():
        emp_num = row['Employee No']

        if emp_num in consecutive_failures['all_three']:
            df.at[idx, 'Continuous_FAIL'] = '3MONTHS_JUL_AUG_SEP'
        elif emp_num in consecutive_failures['jul_aug']:
            # Only mark as Jul-Aug if they recovered in September
            if emp_num not in consecutive_failures['aug_sep']:
                df.at[idx, 'Continuous_FAIL'] = '2MONTHS_JUL_AUG'
        elif emp_num in consecutive_failures['aug_sep']:
            df.at[idx, 'Continuous_FAIL'] = '2MONTHS_AUG_SEP'

    # Count the updated values
    value_counts = df['Continuous_FAIL'].value_counts()
    print(f"\n📊 Updated Continuous_FAIL Distribution:")
    for value, count in value_counts.items():
        print(f"  • {value}: {count} employees")

    # Save the corrected file
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Excel file updated: {csv_file}")

    # Also save as Excel
    excel_file = csv_file.with_suffix('.xlsx')
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Incentive Report', index=False)
    print(f"✅ Excel file saved: {excel_file}")

    return df

def main():
    """Main execution function"""

    # Step 1: Analyze consecutive failures
    consecutive_failures = analyze_consecutive_aql_failures()

    # Step 2: Update Excel with correct data
    updated_df = update_excel_with_correct_data(consecutive_failures)

    print("\n" + "=" * 80)
    print("🎯 Summary of Corrections:")
    print("=" * 80)

    print("\n✅ Key Findings:")
    print(f"  1. Only {len(consecutive_failures['jul_aug'])} employees actually failed Jul-Aug consecutively (not 50)")
    print(f"  2. {len(consecutive_failures['aug_sep'])} employees failed Aug-Sep consecutively")
    print(f"  3. {len(consecutive_failures['all_three'])} employees failed all three months")
    print("\n📌 The Continuous_Months field in the original data does NOT indicate AQL failures")
    print("   It likely tracks employment continuity or another metric")

    return updated_df

if __name__ == "__main__":
    main()