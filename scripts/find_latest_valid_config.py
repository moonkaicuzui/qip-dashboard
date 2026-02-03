#!/usr/bin/env python3
"""
[Issue #57] 데이터가 실제 존재하는 최신 Config 파일 찾기

GitHub Actions에서 LATEST_CONFIG 감지 시 사용.
데이터 없는 월(예: 2월 초에 자동 생성된 config_february_2026.json)을
건너뛰고, 실제 attendance 데이터가 존재하는 최신 config를 반환합니다.

Usage:
    python scripts/find_latest_valid_config.py
    # Output: config_files/config_january_2026.json
"""

import json
import sys
from pathlib import Path

MONTH_ORDER = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}

def get_config_date(config_path):
    """config 파일명에서 (year, month_num) 추출"""
    parts = config_path.stem.split('_')
    if len(parts) >= 3:
        month_name = parts[1].lower()
        try:
            year_num = int(parts[2])
        except ValueError:
            return (0, 0)
        month_num = MONTH_ORDER.get(month_name, 0)
        return (year_num, month_num)
    return (0, 0)

def find_latest_valid_config():
    """데이터가 존재하는 최신 config 파일 경로 반환"""
    config_files = list(Path('config_files').glob('config_*_*.json'))

    if not config_files:
        fallback = 'config_files/config_december_2025.json'
        print(fallback)
        return

    # 날짜순 정렬 (최신 먼저)
    sorted_configs = sorted(config_files, key=get_config_date, reverse=True)

    for cfg_path in sorted_configs:
        try:
            with open(cfg_path) as f:
                cfg = json.load(f)
            month = cfg.get('month', '')

            # attendance 원본 파일 존재 여부 확인
            attendance_original = Path(f"input_files/attendance/original/attendance data {month}.csv")
            attendance_direct = Path(f"input_files/attendance/attendance data {month}.csv")
            basic_manpower = Path(f"input_files/basic manpower data {month}.csv")

            # 원본 데이터 파일이 하나라도 존재하면 유효한 config
            if attendance_original.exists() or attendance_direct.exists() or basic_manpower.exists():
                print(str(cfg_path))
                return
            else:
                # stderr로 로그 출력 (stdout은 결과만)
                sys.stderr.write(f"⏭️ {cfg_path.name} 건너뜀 (데이터 파일 없음: {month})\n")
        except (json.JSONDecodeError, KeyError) as e:
            sys.stderr.write(f"⚠️ {cfg_path.name} 파싱 실패: {e}\n")
            continue

    # 유효한 config 없으면 가장 최신 것 사용 (fallback)
    sys.stderr.write(f"⚠️ 데이터 존재하는 config 없음, fallback: {sorted_configs[0].name}\n")
    print(str(sorted_configs[0]))

if __name__ == '__main__':
    find_latest_valid_config()
