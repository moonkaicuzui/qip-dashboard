#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive 다운로드 후 Config 자동 업데이트 스크립트
download_from_gdrive.py 실행 후 자동으로 config 파일을 업데이트합니다.

주요 기능:
1. 실제 다운로드된 파일 경로를 config에 반영
2. attendance 데이터에서 working_days 자동 계산
3. 파일 존재 여부 검증
4. 타임스탬프 업데이트
"""

import os
import sys
import json
import glob
import pandas as pd
from datetime import datetime
from pathlib import Path
import re

# 상위 디렉토리를 경로에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def detect_downloaded_files(year, month_name):
    """
    실제 다운로드된 파일들의 경로를 감지

    Returns:
        dict: 파일 타입별 실제 경로
    """
    file_paths = {}

    # 1. Basic Manpower 파일 찾기
    basic_patterns = [
        f"input_files/basic manpower data {month_name}.csv",
        f"input_files/basic_manpower_data_{month_name}.csv",
        f"input_files/{year}_{month_name}_basic_manpower.csv"
    ]
    for pattern in basic_patterns:
        if os.path.exists(pattern):
            file_paths['basic_manpower'] = pattern
            print(f"  ✅ Basic Manpower: {pattern}")
            break

    # 2. Attendance 파일 찾기 (converted 버전 우선)
    attendance_patterns = [
        f"input_files/attendance/converted/attendance data {month_name}_converted.csv",
        f"input_files/attendance/original/attendance data {month_name}.csv",
        f"input_files/attendance/출근부_{month_name}_{year}.csv"
    ]
    for pattern in attendance_patterns:
        if os.path.exists(pattern):
            file_paths['attendance'] = pattern
            print(f"  ✅ Attendance: {pattern}")
            break

    # 3. 5PRS 파일 찾기
    prs_patterns = [
        f"input_files/5prs data {month_name}.csv",
        f"input_files/5PRS_{month_name}_{year}.csv",
        f"input_files/{month_name}_5PRS_DATA.csv"
    ]
    for pattern in prs_patterns:
        if os.path.exists(pattern):
            file_paths['5prs'] = pattern
            print(f"  ✅ 5PRS: {pattern}")
            break

    # 4. AQL Current Month 파일 찾기
    month_upper = month_name.upper()
    aql_patterns = [
        f"input_files/AQL history/1.HSRG AQL REPORT-{month_upper}.{year}.csv",
        f"input_files/AQL history/AQL_REPORT_{month_upper}_{year}.csv",
        f"input_files/AQL history/{month_upper}_AQL_HISTORY.csv"
    ]
    for pattern in aql_patterns:
        if os.path.exists(pattern):
            file_paths['aql_current'] = pattern
            print(f"  ✅ AQL Current: {pattern}")
            break

    # 5. Previous Incentive 파일 찾기
    prev_month_names = {
        'january': 'december', 'february': 'january', 'march': 'february',
        'april': 'march', 'may': 'april', 'june': 'may',
        'july': 'june', 'august': 'july', 'september': 'august',
        'october': 'september', 'november': 'october', 'december': 'november'
    }

    prev_month = prev_month_names.get(month_name.lower())
    prev_year = year if month_name.lower() != 'january' else year - 1

    # 여러 버전 패턴 시도 (V9.0 → V8.02 순서) - V9.1 제거됨 (2025-12-01)
    prev_incentive_patterns = [
        f"output_files/output_QIP_incentive_{prev_month}_{prev_year}_Complete_V9.0_Complete.csv",
        f"output_files/output_QIP_incentive_{prev_month}_{prev_year}_Complete_V8.02_Complete.csv"
    ]

    for pattern in prev_incentive_patterns:
        if os.path.exists(pattern):
            file_paths['previous_incentive'] = pattern
            print(f"  ✅ Previous Incentive: {pattern}")
            break

    # 없으면 예상 경로 설정 (나중에 생성될 예정)
    if 'previous_incentive' not in file_paths:
        expected_path = f"output_files/output_QIP_incentive_{prev_month}_{prev_year}_Complete_V9.0_Complete.csv"
        file_paths['previous_incentive'] = expected_path
        print(f"  ⚠️ Previous Incentive not found, using expected: {expected_path}")

    return file_paths

def calculate_working_days(attendance_file_path):
    """
    Attendance 데이터에서 실제 근무일수 계산
    """
    try:
        df = pd.read_csv(attendance_file_path, encoding='utf-8-sig')

        # Work Date 컬럼이 있는 경우
        if 'Work Date' in df.columns:
            unique_dates = df['Work Date'].dropna().unique()
            working_days = len(unique_dates)
            print(f"    📊 Work Date 기준 총 근무일수: {working_days}일")

            if working_days > 0:
                print(f"    첫 날: {min(unique_dates)}")
                print(f"    마지막 날: {max(unique_dates)}")

            return working_days

        # Day_XX 컬럼 형식인 경우
        day_columns = [col for col in df.columns if col.startswith('Day_')]
        if day_columns:
            working_days = len(day_columns)
            print(f"    📊 Day 컬럼 기준 총 근무일수: {working_days}일")
            return working_days

        print("    ⚠️ Working days 계산 불가 - 기본값 사용")
        return None

    except Exception as e:
        print(f"    ❌ Attendance 파일 분석 실패: {e}")
        return None

def update_config(year, month_name, month_num):
    """
    Config 파일을 실제 다운로드된 파일 경로로 업데이트
    """
    config_path = f"config_files/config_{month_name}_{year}.json"

    print(f"\n📝 Config 업데이트: {config_path}")

    # 1. 기존 config 로드 또는 새로 생성
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("  기존 config 파일 로드")
    else:
        print("  새 config 파일 생성")
        config = {
            "year": year,
            "month": month_name,
            "working_days": 23,  # 기본값, 곧 업데이트됨
            "previous_months": []
        }

    # 2. 실제 다운로드된 파일 경로 감지
    print("\n  📂 다운로드된 파일 감지 중...")
    file_paths = detect_downloaded_files(year, month_name)

    # 3. Config에 실제 파일 경로 반영
    config['file_paths'] = file_paths

    # 4. Working days 계산 및 업데이트
    if 'attendance' in file_paths and os.path.exists(file_paths['attendance']):
        print("\n  📊 Working days 계산 중...")
        working_days = calculate_working_days(file_paths['attendance'])

        if working_days:
            old_days = config.get('working_days', 'N/A')
            config['working_days'] = working_days
            config['working_days_source'] = 'attendance_data'
            config['working_days_updated_at'] = datetime.now().isoformat()
            print(f"    ✅ Working days 업데이트: {old_days} → {working_days}")

    # 5. Previous months 계산
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    month_idx = months.index(month_name.lower())
    prev_months = []
    for i in range(1, 3):  # 이전 2개월
        prev_idx = (month_idx - i) % 12
        prev_months.append(months[prev_idx])
    config['previous_months'] = list(reversed(prev_months))

    # 6. 기타 필드 업데이트
    config['output_prefix'] = f"output_QIP_incentive_{month_name}_{year}"
    config['data_source'] = 'google_drive'
    config['last_updated'] = datetime.now().isoformat()

    # 7. Config 저장
    os.makedirs('config_files', exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n  ✅ Config 업데이트 완료: {config_path}")

    # 8. 검증
    print("\n  🔍 파일 존재 여부 검증:")
    all_exist = True
    for key, path in file_paths.items():
        exists = os.path.exists(path)
        status = "✅" if exists else "⚠️"
        print(f"    {status} {key}: {os.path.basename(path)}")
        if not exists and key != 'previous_incentive':
            all_exist = False

    return config_path, all_exist

def detect_available_months():
    """
    다운로드된 데이터에서 사용 가능한 월 감지
    """
    months_data = []

    # basic manpower 파일에서 월 감지
    pattern = "input_files/basic manpower data *.csv"
    files = glob.glob(pattern)

    month_names = {
        1: 'january', 2: 'february', 3: 'march', 4: 'april',
        5: 'may', 6: 'june', 7: 'july', 8: 'august',
        9: 'september', 10: 'october', 11: 'november', 12: 'december'
    }
    month_name_to_num = {v: k for k, v in month_names.items()}

    for file_path in files:
        match = re.search(r'basic manpower data ([a-z]+)\.csv', file_path, re.IGNORECASE)
        if match:
            month_name = match.group(1).lower()
            month_num = month_name_to_num.get(month_name)
            if month_num:
                year = datetime.now().year
                months_data.append((year, month_name, month_num))

    # 정렬 (최신 월 우선)
    months_data.sort(key=lambda x: (x[0], x[2]), reverse=True)

    return months_data

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("🔄 Config 자동 업데이트 시작")
    print("=" * 70)

    # 사용 가능한 월 감지
    print("\n📂 다운로드된 데이터 감지 중...")
    months_data = detect_available_months()

    if not months_data:
        print("\n⚠️ 다운로드된 데이터를 찾을 수 없습니다.")
        print("먼저 scripts/download_from_gdrive.py를 실행하세요.")
        return False

    print(f"✅ {len(months_data)}개월 데이터 발견")

    # 각 월별로 config 업데이트
    success_configs = []
    failed_configs = []

    for year, month_name, month_num in months_data:
        print(f"\n{'='*50}")
        print(f"🗓️ {year}년 {month_num}월 ({month_name}) 처리 중...")

        config_path, all_exist = update_config(year, month_name, month_num)

        if all_exist:
            success_configs.append((month_name, config_path))
        else:
            failed_configs.append((month_name, config_path))

    # 최종 보고서
    print("\n" + "=" * 70)
    print("📊 최종 보고서")
    print("=" * 70)

    if success_configs:
        print(f"\n✅ 성공적으로 업데이트된 Config: {len(success_configs)}개")
        for month_name, path in success_configs:
            print(f"  - {month_name}: {path}")

    if failed_configs:
        print(f"\n⚠️ 일부 파일이 없는 Config: {len(failed_configs)}개")
        for month_name, path in failed_configs:
            print(f"  - {month_name}: {path}")
        print("\n  → download_from_gdrive.py를 다시 실행하거나 누락된 파일을 확인하세요.")

    print("\n" + "=" * 70)

    return len(failed_configs) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)