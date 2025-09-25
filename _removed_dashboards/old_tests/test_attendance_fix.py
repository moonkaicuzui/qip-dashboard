#!/usr/bin/env python3
"""
Test script to verify attendance data processing fix
"""

import pandas as pd
from pathlib import Path

def test_ar1_detection():
    """Test AR1 absence detection with actual data patterns"""

    # Load September attendance data
    att_file = Path("input_files/attendance/converted/attendance data september_converted.csv")
    att_df = pd.read_csv(att_file, encoding='utf-8-sig')

    print("📊 Testing AR1 Absence Detection:")
    print("=" * 60)

    # Find employees with AR1 absences
    ar1_records = att_df[att_df['Reason Description'].str.contains('AR1', na=False)]
    print(f"\n✅ Found {len(ar1_records)} AR1 absence records")

    # Group by employee to count AR1 days per person
    ar1_by_employee = ar1_records.groupby('ID No').size().reset_index(name='AR1_Days')
    ar1_by_employee = ar1_by_employee.sort_values('AR1_Days', ascending=False)

    print(f"✅ {len(ar1_by_employee)} employees have AR1 absences")
    print("\nTop 10 employees with AR1 absences:")
    print(ar1_by_employee.head(10).to_string())

    # Test the new logic for a specific employee
    test_employee = ar1_by_employee.iloc[0]['ID No'] if len(ar1_by_employee) > 0 else None

    if test_employee:
        print(f"\n📋 Detailed test for employee {test_employee}:")
        emp_data = att_df[att_df['ID No'] == test_employee]

        worked_dates = set()
        unapproved_absence = 0

        for idx, row in emp_data.iterrows():
            comp_add = row.get('compAdd', '')
            work_date = row.get('Work Date')
            reason_desc = row.get('Reason Description', '')

            if pd.notna(comp_add):
                comp_str = str(comp_add).strip()
                reason_str = str(reason_desc).strip() if pd.notna(reason_desc) else ''

                # Using the fixed logic
                if comp_str == 'Đi làm' and pd.notna(work_date):
                    worked_dates.add(str(work_date))
                elif reason_str == 'Đi công tác' and pd.notna(work_date):
                    worked_dates.add(str(work_date))
                elif comp_str == 'Vắng mặt':
                    if 'AR1' in reason_str or 'Vắng không phép' in reason_str or 'không phép' in reason_str.lower():
                        unapproved_absence += 1
                        print(f"  - Found AR1 absence on {work_date}: {reason_str}")

        print(f"\n  Result for {test_employee}:")
        print(f"  - Working days: {len(worked_dates)}")
        print(f"  - AR1/Unapproved absences: {unapproved_absence}")
        print(f"  - Condition 2 (AR1 > 2): {'YES' if unapproved_absence > 2 else 'NO'}")

    return ar1_by_employee

if __name__ == "__main__":
    test_ar1_detection()