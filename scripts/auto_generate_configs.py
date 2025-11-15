#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Config 파일 자동 생성 스크립트
Google Drive에서 다운로드한 데이터를 기반으로 필요한 config 파일을 자동으로 생성합니다.
"""

import os
import sys
import json
import glob
import re
from datetime import datetime
from pathlib import Path

# 상위 디렉토리를 경로에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def detect_months_from_drive():
    """
    Google Drive에서 다운로드한 데이터에서 월 정보 감지

    Returns:
        list: [(year, month_name, month_num), ...]
    """
    months_data = []

    # Drive 다운로드 경로 확인
    drive_pattern = "input_files/monthly_data/*/basic_manpower_data.csv"
    drive_files = glob.glob(drive_pattern)

    month_names = {
        1: 'january', 2: 'february', 3: 'march', 4: 'april',
        5: 'may', 6: 'june', 7: 'july', 8: 'august',
        9: 'september', 10: 'october', 11: 'november', 12: 'december'
    }

    for file_path in drive_files:
        # 폴더명에서 년도/월 추출: monthly_data/2025_11/
        match = re.search(r'monthly_data/(\d{4})_(\d{1,2})/', file_path)
        if match:
            year = int(match.group(1))
            month_num = int(match.group(2))
            month_name = month_names.get(month_num)

            if month_name:
                months_data.append((year, month_name, month_num))
                print(f"  ✅ 발견: {year}년 {month_num}월 ({month_name})")

    # 정렬 (최신 월 우선)
    months_data.sort(key=lambda x: (x[0], x[2]), reverse=True)

    return months_data

def get_previous_months(month_name):
    """이전 2개월 계산"""
    months = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    ]

    current_idx = months.index(month_name.lower())
    prev_months = []

    for i in range(1, 3):  # 이전 2개월
        prev_idx = (current_idx - i) % 12
        prev_months.append(months[prev_idx])

    prev_months.reverse()  # 오래된 순서로
    return prev_months

def detect_previous_incentive_file(year, month_name):
    """
    이전 달 인센티브 파일 자동 감지

    우선순위:
    1. Automated output file (output_files/)
    2. Manual input file (input_files/)
    """
    # 이전 달 계산
    months = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    ]
    month_nums = {name: idx + 1 for idx, name in enumerate(months)}

    current_month_num = month_nums[month_name.lower()]
    prev_month_num = current_month_num - 1 if current_month_num > 1 else 12
    prev_year = year if current_month_num > 1 else year - 1
    prev_month_name = months[prev_month_num - 1]

    # 1순위: Automated output file
    output_file = f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv"
    if Path(output_file).exists():
        print(f"  → Previous incentive: {output_file} (automated)")
        return output_file

    # 2순위: Manual input file (Korean format)
    input_file = f"input_files/{prev_year}년 {prev_month_num}월 인센티브 지급 세부 정보.csv"
    if Path(input_file).exists():
        print(f"  → Previous incentive: {input_file} (manual)")
        return input_file

    # 3순위: Manual input file (English format)
    input_file_en = f"input_files/{prev_year}year {prev_month_name.capitalize()} incentive 지급 세부 정보.csv"
    if Path(input_file_en).exists():
        print(f"  → Previous incentive: {input_file_en} (manual)")
        return input_file_en

    # 없으면 output 경로 사용 (나중에 생성될 예정)
    print(f"  ⚠️ Previous incentive file not found, using expected path: {output_file}")
    return output_file

def generate_config(year, month_name, month_num):
    """
    특정 월의 config 파일 생성

    Args:
        year: 연도
        month_name: 월 이름 (예: 'november')
        month_num: 월 번호 (1-12)

    Returns:
        str: 생성된 config 파일 경로
    """
    config_file = f"config_files/config_{month_name}_{year}.json"

    # 이미 존재하는지 확인
    if Path(config_file).exists():
        print(f"  ℹ️ Config already exists: {config_file}")

        # Previous_incentive 경로 확인 및 업데이트
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Previous_incentive 키가 없으면 추가
        if 'previous_incentive' not in config.get('file_paths', {}):
            print(f"  🔧 Updating config with previous_incentive path...")
            prev_incentive_path = detect_previous_incentive_file(year, month_name)
            config['file_paths']['previous_incentive'] = prev_incentive_path

            # 업데이트 타임스탬프 추가
            config['config_updated_at'] = datetime.now().isoformat()

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"  ✅ Config updated: {config_file}")

        return config_file

    print(f"  🆕 Creating new config: {config_file}")

    # Previous months 계산
    prev_months = get_previous_months(month_name)

    # Previous incentive 파일 감지
    prev_incentive_path = detect_previous_incentive_file(year, month_name)

    # Config 생성
    config = {
        "year": year,
        "month": month_name,
        "working_days": 23,  # Default, will be updated from attendance data
        "previous_months": prev_months,
        "file_paths": {
            "basic_manpower": f"drive://monthly_data/{year}_{month_num:02d}/basic_manpower_data.csv",
            "attendance": f"drive://monthly_data/{year}_{month_num:02d}/attendance_data.csv",
            "5prs": f"drive://monthly_data/{year}_{month_num:02d}/5prs_data.csv",
            "aql_current": f"drive://aql_history/AQL_REPORT_{month_name.upper()}_{year}.csv",
            "aql_history": "drive://aql_history/",
            "previous_incentive": prev_incentive_path
        },
        "output_prefix": f"output_QIP_incentive_{month_name}_{year}",
        "created_at": datetime.now().isoformat(),
        "data_source": "google_drive",
        "working_days_source": "attendance_data"
    }

    # Config 폴더 생성
    os.makedirs("config_files", exist_ok=True)

    # Config 저장
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Config created: {config_file}")
    return config_file

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("🔧 Config 자동 생성 시작")
    print("=" * 70)

    # Google Drive에서 다운로드한 데이터 감지
    print("\n📂 Google Drive 데이터 감지 중...")
    months_data = detect_months_from_drive()

    if not months_data:
        print("⚠️ Google Drive 데이터를 찾을 수 없습니다")
        print("먼저 scripts/download_from_gdrive.py를 실행하세요")
        sys.exit(1)

    print(f"\n📊 {len(months_data)}개월 데이터 발견\n")

    # 각 월별로 config 생성
    generated_configs = []
    for year, month_name, month_num in months_data:
        print(f"🔧 {year}년 {month_num}월 ({month_name}) Config 처리 중...")
        config_file = generate_config(year, month_name, month_num)
        generated_configs.append(config_file)
        print()

    # 결과 출력
    print("=" * 70)
    if generated_configs:
        print(f"✅ 총 {len(generated_configs)}개 Config 처리 완료\n")
        print("생성/업데이트된 Config:")
        for config_file in generated_configs:
            print(f"  - {config_file}")
    else:
        print("❌ 생성된 Config가 없습니다")
        sys.exit(1)

    print("=" * 70)

if __name__ == "__main__":
    main()
