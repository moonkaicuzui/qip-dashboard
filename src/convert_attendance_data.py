#!/usr/bin/env python3
"""
Attendance data conversion script
Converts attendance data from original folder to converted folder
"""

import pandas as pd
import os
import sys
from pathlib import Path

def convert_attendance(month, year=2025):
    """
    Convert attendance data

    Args:
        month: Month name (e.g., 'july', 'august')
        year: Year (default: 2025)

    Returns:
        bool: Success status
    """
    try:
        # Set paths
        base_dir = Path(__file__).parent.parent
        original_file = base_dir / f"input_files/attendance/original/attendance data {month}.csv"
        converted_file = base_dir / f"input_files/attendance/converted/attendance data {month}_converted.csv"

        # Create converted folder
        converted_file.parent.mkdir(parents=True, exist_ok=True)

        # Skip if original file doesn't exist
        if not original_file.exists():
            print(f"⚠️ Original file not found: {original_file}")
            return False

        # Skip if converted file exists and is newer than original
        if converted_file.exists():
            original_mtime = original_file.stat().st_mtime
            converted_mtime = converted_file.stat().st_mtime

            if converted_mtime >= original_mtime:
                print(f"ℹ️ Converted file is up to date: {converted_file}")
                return True
            else:
                print(f"🔄 Original file updated, reconverting: {original_file}")
                # Delete existing converted file
                converted_file.unlink()

        # Read CSV file
        df = pd.read_csv(original_file, encoding='utf-8-sig')

        # Simple conversion processing (add conversion logic here if needed)
        # Example: Clean column names, convert data types, etc.
        df.columns = df.columns.str.strip()

        # Save converted file
        df.to_csv(converted_file, index=False, encoding='utf-8-sig')
        print(f"✅ Attendance data conversion completed: {converted_file}")

        return True

    except Exception as e:
        print(f"❌ Attendance data conversion failed: {e}")
        return False

def convert_all_attendance():
    """Convert attendance data for all months"""
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']

    for month in months:
        convert_attendance(month)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        month = sys.argv[1]
        convert_attendance(month)
    else:
        # Convert all months
        convert_all_attendance()
