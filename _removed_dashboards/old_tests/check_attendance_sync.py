#!/usr/bin/env python3
"""
출결 데이터 동기화 상태 점검 스크립트
Original → Converted 폴더 동기화 상태를 확인하고 필요시 재변환
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd


def check_attendance_sync():
    """출결 데이터 동기화 상태 점검"""

    base_dir = Path(__file__).parent
    original_dir = base_dir / "input_files/attendance/original"
    converted_dir = base_dir / "input_files/attendance/converted"

    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']

    print("="*70)
    print("📊 출결 데이터 동기화 상태 점검")
    print("="*70)
    print()

    sync_status = []
    need_conversion = []

    for month in months:
        original_file = original_dir / f"attendance data {month}.csv"
        converted_file = converted_dir / f"attendance data {month}_converted.csv"

        if not original_file.exists():
            continue

        original_mtime = datetime.fromtimestamp(original_file.stat().st_mtime)
        original_size = original_file.stat().st_size

        status = {
            'month': month.capitalize(),
            'original_exists': True,
            'original_time': original_mtime,
            'original_size': original_size,
            'converted_exists': converted_file.exists(),
            'sync_status': 'N/A',
            'action_needed': None
        }

        if converted_file.exists():
            converted_mtime = datetime.fromtimestamp(converted_file.stat().st_mtime)
            converted_size = converted_file.stat().st_size

            status['converted_time'] = converted_mtime
            status['converted_size'] = converted_size

            # 동기화 상태 판단
            if converted_mtime >= original_mtime:
                status['sync_status'] = '✅ 최신'
            else:
                status['sync_status'] = '⚠️ 업데이트 필요'
                status['action_needed'] = 'convert'
                need_conversion.append(month)
        else:
            status['sync_status'] = '❌ 변환 필요'
            status['action_needed'] = 'convert'
            need_conversion.append(month)

        sync_status.append(status)

    # 상태 출력
    print(f"{'월':<10} | {'Original':<20} | {'Converted':<20} | {'상태':<15}")
    print("-"*70)

    for status in sync_status:
        original_info = f"{status['original_time'].strftime('%Y-%m-%d %H:%M')}"

        if status['converted_exists']:
            converted_info = f"{status['converted_time'].strftime('%Y-%m-%d %H:%M')}"
        else:
            converted_info = "파일 없음"

        print(f"{status['month']:<10} | {original_info:<20} | {converted_info:<20} | {status['sync_status']:<15}")

    # 파일 크기 비교
    print("\n" + "="*70)
    print("📏 파일 크기 비교")
    print("-"*70)

    for status in sync_status:
        if status['converted_exists']:
            size_diff = status['converted_size'] - status['original_size']
            size_percent = (size_diff / status['original_size']) * 100

            print(f"{status['month']:<10}: Original {status['original_size']:,} bytes → "
                  f"Converted {status['converted_size']:,} bytes "
                  f"({size_percent:+.1f}%)")

    # 작업 필요 항목
    if need_conversion:
        print("\n" + "="*70)
        print(f"🔄 변환이 필요한 파일: {len(need_conversion)}개")
        print("-"*70)

        for month in need_conversion:
            print(f"  - {month.capitalize()}")

        print("\n변환하시겠습니까? (y/n): ", end='')
        answer = input().strip().lower()

        if answer == 'y':
            print("\n📥 변환 시작...")
            for month in need_conversion:
                print(f"  변환 중: {month}...", end='')

                # convert_attendance_data.py 실행
                result = os.system(f"python src/convert_attendance_data.py {month} > /dev/null 2>&1")

                if result == 0:
                    print(" ✅")
                else:
                    print(" ❌")

            print("\n✅ 변환 완료!")
    else:
        print("\n✅ 모든 파일이 최신 상태입니다!")

    print("\n" + "="*70)


if __name__ == "__main__":
    check_attendance_sync()