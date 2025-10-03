#!/usr/bin/env python3
"""
Auto-calculate actual working days from Attendance data and update Config file
Automatically executed by action.sh to ensure accurate working days
"""

import json
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

def find_attendance_file(month_name, year):
    """Find attendance file in multiple possible paths"""
    possible_paths = [
        f"input_files/attendance/converted/attendance data {month_name}_converted.csv",
        f"input_files/attendance data {month_name}.csv",
        f"input_files/{year}년 {month_name} attendance.csv",
        f"input_files/attendance/{month_name}_attendance.csv",
        # Try case variations
        f"input_files/attendance/converted/attendance data {month_name.lower()}_converted.csv",
        f"input_files/attendance/converted/attendance data {month_name.upper()}_converted.csv",
        f"input_files/attendance/converted/attendance data {month_name.capitalize()}_converted.csv",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def calculate_working_days(attendance_file):
    """Calculate actual working days from Attendance file (weekdays only)"""
    try:
        df = pd.read_csv(attendance_file)

        # Find Date column (try multiple possible names)
        date_columns = ['Date', 'date', 'DATE', '날짜', '일자', 'Work Date']
        date_col = None

        for col in date_columns:
            if col in df.columns:
                date_col = col
                break

        if not date_col:
            print(f"  ⚠️ Cannot find date column. Available columns: {list(df.columns)[:5]}...")
            return None

        # Parse dates
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        unique_dates = df[date_col].dropna().unique()

        if len(unique_dates) == 0:
            print(f"  ⚠️ No valid date data found.")
            return None

        # Calculate actual factory operating days (based on attendance count)
        # Vietnam factory operates on Saturdays too, so use actual attendance data

        # Calculate daily attendance count
        daily_attendance = df.groupby(df[date_col].dt.date)['ID No'].nunique() if 'ID No' in df.columns else df.groupby(df[date_col].dt.date).size()

        # Normal operating day: 300+ employees (or 70%+ of average)
        avg_attendance = daily_attendance.mean()
        threshold = max(300, avg_attendance * 0.7)  # Greater of 300 or 70% of average

        working_days_list = daily_attendance[daily_attendance >= threshold]
        working_days = len(working_days_list)

        # Print statistics
        total_days = len(unique_dates)
        non_working_days = total_days - working_days

        print(f"  📅 Total records: {total_days} days")
        print(f"  🏭 Normal operating days ({int(threshold)}+ employees): {working_days} days")
        print(f"  🛋️ Days off/Partial operation: {non_working_days} days")

        # Check weekend work status
        weekend_work_count = sum(1 for date, count in working_days_list.items()
                                if pd.Timestamp(date).weekday() >= 5)
        if weekend_work_count > 0:
            print(f"  🗓️ Saturday work: {weekend_work_count} days included")

        return working_days

    except Exception as e:
        print(f"  ❌ File read error: {e}")
        return None

def update_config_working_days(month_name, year, working_days):
    """Update working_days in Config file"""
    config_path = f"config_files/config_{month_name}_{year}.json"

    if not os.path.exists(config_path):
        print(f"  ⚠️ Config file not found: {config_path}")
        return False

    try:
        # Read existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        old_value = config.get('working_days', 'N/A')
        config['working_days'] = working_days
        config['working_days_source'] = 'attendance_data'
        config['working_days_updated_at'] = datetime.now().isoformat()

        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        if old_value != working_days:
            print(f"  ✅ Config updated: working_days {old_value} → {working_days}")
        else:
            print(f"  ✅ Config verified: working_days = {working_days} (no change)")

        return True

    except Exception as e:
        print(f"  ❌ Config update failed: {e}")
        return False

def main():
    """Main execution function"""
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python calculate_working_days_from_attendance.py <month> <year>")
        sys.exit(1)

    month_name = sys.argv[1].lower()
    year = sys.argv[2]

    print(f"\n🔄 Auto-calculating working days for {year} {month_name}...")
    print("-" * 50)

    # 1. Find Attendance file
    attendance_file = find_attendance_file(month_name, year)

    if not attendance_file:
        print(f"  ❌ Cannot find {month_name} attendance file.")
        print("  ℹ️ Please manually verify working_days in Config.")
        return

    print(f"  📁 Attendance file: {attendance_file}")

    # 2. Calculate working days
    working_days = calculate_working_days(attendance_file)

    if working_days is None:
        print("  ❌ Cannot calculate working days.")
        return

    print(f"  📊 Calculated working days: {working_days} days")

    # 3. Update Config file
    if update_config_working_days(month_name, year, working_days):
        print(f"\n✅ Working days for {year} {month_name} set to {working_days} days.")
    else:
        print("\n⚠️ Config file update failed.")

if __name__ == "__main__":
    main()
