"""
Verify Working Days Calculation for THỊ MINH PHƯỢNG
Proper calculation excluding weekends
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_working_days(start_date, end_date):
    """Calculate working days excluding weekends (Saturday and Sunday)"""
    if pd.isna(start_date) or pd.isna(end_date):
        return 0
    
    # Ensure we have datetime objects
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    # Generate all dates in the range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Count only weekdays (Monday=0, Sunday=6)
    # Exclude Saturday (5) and Sunday (6)
    working_days = sum(1 for date in date_range if date.weekday() < 5)
    
    return working_days

def analyze_thi_minh_phuong_case():
    """Analyze the specific case of THỊ MINH PHƯỢNG"""
    
    print("=" * 60)
    print("THỊ MINH PHƯỢNG Working Days Analysis")
    print("=" * 60)
    
    # Employee data
    employee_id = "620080271"
    employee_name = "THỊ MINH PHƯỢNG"
    entrance_date = pd.to_datetime("2020-08-25")
    stop_date = pd.to_datetime("2025-08-15")
    
    # August 2025 period
    month_start = pd.to_datetime("2025-08-01")
    month_end = pd.to_datetime("2025-08-31")
    
    # Data from error report
    recorded_total_days = 11
    actual_working_days = 12
    
    print(f"\n📋 Employee Information:")
    print(f"  ID: {employee_id}")
    print(f"  Name: {employee_name}")
    print(f"  Entrance Date: {entrance_date.date()}")
    print(f"  Stop Working Date: {stop_date.date()}")
    
    print(f"\n📅 August 2025 Analysis:")
    print(f"  Month Period: {month_start.date()} to {month_end.date()}")
    print(f"  Employee worked: {month_start.date()} to {stop_date.date()}")
    
    # Calculate calendar days
    calendar_days = (stop_date - month_start).days + 1
    print(f"\n📊 Calendar Days Calculation:")
    print(f"  From Aug 1 to Aug 15: {calendar_days} days")
    
    # Calculate working days (excluding weekends)
    working_days = calculate_working_days(month_start, stop_date)
    print(f"\n💼 Working Days Calculation (excluding weekends):")
    print(f"  Expected Working Days: {working_days} days")
    
    # Show day-by-day breakdown
    print(f"\n📆 Day-by-Day Breakdown (Aug 1-15, 2025):")
    current_date = month_start
    working_day_count = 0
    weekend_count = 0
    
    while current_date <= stop_date:
        day_name = current_date.strftime("%A")
        is_weekend = current_date.weekday() >= 5
        
        if is_weekend:
            weekend_count += 1
            status = "Weekend (excluded)"
        else:
            working_day_count += 1
            status = "Working day"
        
        print(f"  {current_date.date()} ({day_name}): {status}")
        current_date += timedelta(days=1)
    
    print(f"\n📈 Summary:")
    print(f"  Calendar days (Aug 1-15): {calendar_days} days")
    print(f"  Weekends in period: {weekend_count} days")
    print(f"  Expected Working days: {working_day_count} days")
    print(f"  Recorded Total days: {recorded_total_days} days")
    print(f"  Actual Working days: {actual_working_days} days")
    
    print(f"\n🔍 Analysis Result:")
    if working_day_count == recorded_total_days:
        print(f"  ✅ Recorded Total Days ({recorded_total_days}) is CORRECT")
        if actual_working_days > recorded_total_days:
            print(f"  ❌ Actual Working Days ({actual_working_days}) exceeds Total - this is the real error")
            print(f"     The employee cannot work more days than available working days")
    elif working_day_count == actual_working_days:
        print(f"  ✅ Actual Working Days ({actual_working_days}) is CORRECT")
        print(f"  ❌ Recorded Total Days ({recorded_total_days}) is WRONG")
        print(f"     Should be {working_day_count} days, not {recorded_total_days}")
    else:
        print(f"  ⚠️ Both values seem incorrect:")
        print(f"     Expected: {working_day_count} working days")
        print(f"     Recorded Total: {recorded_total_days} days")
        print(f"     Actual Working: {actual_working_days} days")
    
    # Check for Korean holidays in August 2025
    print(f"\n🎌 Note about holidays:")
    print(f"  August 15, 2025 (Friday) - Korea Liberation Day (광복절)")
    print(f"  If this is a holiday, working days would be 10, not 11")
    
    # Recalculate excluding Aug 15 as holiday
    working_days_with_holiday = working_day_count - 1  # Exclude Aug 15
    print(f"\n📊 With Aug 15 as holiday:")
    print(f"  Expected Working days: {working_days_with_holiday} days")
    print(f"  This would make Recorded Total ({recorded_total_days}) closer to correct")

if __name__ == "__main__":
    analyze_thi_minh_phuong_case()