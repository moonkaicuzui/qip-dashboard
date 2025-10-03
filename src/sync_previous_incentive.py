#!/usr/bin/env python3
"""
Previous month incentive file synchronization script
Downloads previous month incentive file from Google Drive
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

def get_previous_month(year, month):
    """Calculate previous month"""
    date = datetime(year, month, 1) - timedelta(days=1)
    return date.year, date.month

def get_korean_month(month):
    """Convert month number to Korean format"""
    months = {
        1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
        7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12"
    }
    return months.get(month, str(month))

def sync_previous_incentive(month_str, year):
    """
    Synchronize previous month incentive file

    Args:
        month_str: Month name (e.g., 'august')
        year: Year (e.g., 2025)
    """
    # Convert month name to number
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    current_month = month_map.get(month_str.lower())
    if not current_month:
        print(f"❌ Invalid month name: {month_str}")
        return False

    # Calculate previous month
    prev_year, prev_month = get_previous_month(year, current_month)
    prev_month_kr = get_korean_month(prev_month)

    # Set file paths
    base_dir = Path(__file__).parent.parent
    target_file = base_dir / f"input_files/{prev_year}년 {prev_month_kr}월 인센티브 지급 세부 정보.csv"

    print(f"📥 Checking {prev_year} {prev_month_kr}월 incentive file...")

    if target_file.exists():
        print(f"✅ Already exists: {target_file.name}")
        return True

    # Try downloading from Google Drive
    try:
        # Download using google_drive_manager
        from google_drive_manager import GoogleDriveManager

        # Load config file
        config_path = base_dir / 'config_files' / 'drive_config.json'
        manager = GoogleDriveManager(str(config_path))

        # Set file pattern
        drive_pattern = f"monthly_data/{prev_year}_{prev_month:02d}/{prev_year}년 {prev_month_kr}월 인센티브 지급 세부 정보.csv"

        print(f"🔍 Searching in Google Drive: {drive_pattern}")

        # Execute download
        success = manager.download_specific_file(drive_pattern, str(target_file))

        if success:
            print(f"✅ Successfully downloaded from Google Drive!")
            return True
        else:
            print(f"❌ Google Drive download failed")
            print(f"📂 Please download manually:")
            print(f"   Google Drive: {drive_pattern}")
            print(f"   Save to: {target_file}")
            return False

    except ImportError:
        print(f"⚠️ Cannot load Google Drive Manager.")
        print(f"📂 Please download manually:")
        print(f"   Google Drive: monthly_data/{prev_year}_{prev_month:02d}/")
        print(f"   Filename: {prev_year}년 {prev_month_kr}월 인센티브 지급 세부 정보.csv")
        print(f"   Save to: {target_file}")
        return False
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        month = sys.argv[1]
        year = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
        sync_previous_incentive(month, year)
    else:
        print("Usage: python sync_previous_incentive.py [month] [year]")
        print("Example: python sync_previous_incentive.py august 2025")
