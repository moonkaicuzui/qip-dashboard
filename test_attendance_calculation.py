#!/usr/bin/env python3
"""
Test script to debug attendance data calculation issues
"""

import pandas as pd
from pathlib import Path
import json

def test_attendance_processing():
    """Test attendance data processing for September 2025"""

    # Load September attendance data
    att_file = Path("input_files/attendance/converted/attendance data september_converted.csv")
    print(f"Loading attendance file: {att_file}")

    if not att_file.exists():
        print(f"Error: File not found - {att_file}")
        return

    att_df = pd.read_csv(att_file, encoding='utf-8-sig')
    print(f"✅ Loaded {len(att_df)} rows, {len(att_df['ID No'].unique())} unique employees")
    print(f"Columns: {att_df.columns.tolist()}")
    print()

    # Sample employee analysis
    sample_id = '617100049'  # First employee in file
    sample_data = att_df[att_df['ID No'] == sample_id]

    if not sample_data.empty:
        print(f"📊 Sample Analysis for Employee {sample_id}:")
        print(f"  - Total records: {len(sample_data)}")
        print(f"  - Unique work dates: {sample_data['Work Date'].nunique()}")
        print(f"  - CompAdd values: {sample_data['compAdd'].value_counts().to_dict()}")
        print(f"  - Reason descriptions: {sample_data['Reason Description'].value_counts().to_dict()}")
        print()

    # Process all employees like the main script does
    print("📊 Processing all employees:")
    results = []

    for emp_id in att_df['ID No'].unique()[:10]:  # First 10 employees for testing
        if pd.isna(emp_id):
            continue

        emp_data = att_df[att_df['ID No'] == emp_id]

        # Count unique work dates where they attended
        worked_dates = set()
        unapproved_absences = 0
        ar1_absences = 0

        for idx, row in emp_data.iterrows():
            comp_add = row.get('compAdd', '')
            work_date = row.get('Work Date')
            reason = row.get('Reason Description', '')

            if pd.notna(comp_add):
                comp_str = str(comp_add).strip()
                reason_str = str(reason).strip() if pd.notna(reason) else ''

                # Check for attendance
                if comp_str == 'Đi làm' and pd.notna(work_date):
                    worked_dates.add(str(work_date))
                elif reason_str == 'Đi công tác' and pd.notna(work_date):  # Business trip
                    worked_dates.add(str(work_date))
                # Check for absences
                elif 'nghỉ' in comp_str.lower() or 'vắng' in comp_str.lower():
                    if 'không phép' in comp_str.lower() or 'unapp' in comp_str.lower():
                        unapproved_absences += 1
                        ar1_absences += 1

        actual_days = len(worked_dates)
        total_days = 27  # September working days
        absence_rate = ((total_days - actual_days) / total_days * 100) if total_days > 0 else 0

        results.append({
            'Employee ID': emp_id,
            'Total Days': total_days,
            'Actual Days': actual_days,
            'AR1 Absences': ar1_absences,
            'Unapproved Absences': unapproved_absences,
            'Absence Rate %': round(absence_rate, 2),
            'Cond1 (zero days)': 'yes' if actual_days == 0 else 'no',
            'Cond2 (unapp > 2)': 'yes' if ar1_absences > 2 else 'no',
            'Cond3 (rate > 12%)': 'yes' if absence_rate > 12 else 'no',
            'Cond4 (< 12 days)': 'yes' if actual_days < 12 else 'no'
        })

    # Display results
    results_df = pd.DataFrame(results)
    print(results_df.to_string())
    print()

    # Summary statistics
    print("📊 Summary Statistics:")
    print(f"  - Employees with 0 actual days: {len(results_df[results_df['Actual Days'] == 0])}")
    print(f"  - Employees with AR1 absences > 2: {len(results_df[results_df['AR1 Absences'] > 2])}")
    print(f"  - Employees with absence rate > 12%: {len(results_df[results_df['Absence Rate %'] > 12])}")
    print(f"  - Employees with < 12 working days: {len(results_df[results_df['Actual Days'] < 12])}")

    # Check what the main calculation produces
    print("\n📊 Checking main calculation output:")
    output_file = Path("output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv")
    if output_file.exists():
        output_df = pd.read_csv(output_file, encoding='utf-8-sig')

        # Check first 10 employees' attendance conditions
        for i, emp_id in enumerate(results_df['Employee ID'].head(10)):
            emp_output = output_df[output_df['Employee No'] == str(emp_id).zfill(9)]
            if not emp_output.empty:
                cond2_val = emp_output.iloc[0].get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'N/A')
                print(f"  Employee {emp_id}: Cond2 in output = '{cond2_val}'")

    return results_df

if __name__ == "__main__":
    test_attendance_processing()