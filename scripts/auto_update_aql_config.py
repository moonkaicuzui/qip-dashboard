#!/usr/bin/env python3
"""
AQL Inspector Config 자동 업데이트 스크립트
GitHub Actions workflow에서 인센티브 계산 후 자동 실행
"""

import json
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def load_config():
    """기존 config 파일 로드"""
    config_path = Path("config_files/aql_inspector_incentive_config.json")

    if not config_path.exists():
        print(f"❌ ERROR: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_latest_output_file(year, month_name):
    """최신 인센티브 계산 결과 파일 찾기"""
    output_dir = Path("output_files")

    # Version priority: V9.1 > V9.0 > V8.02
    patterns = [
        f"output_QIP_incentive_{month_name}_{year}_Complete_V9.1_Complete.csv",
        f"output_QIP_incentive_{month_name}_{year}_Complete_V9.0_Complete.csv",
        f"output_QIP_incentive_{month_name}_{year}_Complete_V8.02_Complete.csv",
    ]

    for pattern in patterns:
        file_path = output_dir / pattern
        if file_path.exists():
            print(f"✅ Found output file: {file_path.name}")
            return file_path

    print(f"❌ ERROR: No output file found for {month_name} {year}")
    sys.exit(1)

def update_config_from_data(config, csv_path, month_name, year):
    """CSV 데이터에서 config 업데이트"""

    # CSV 파일 읽기
    df = pd.read_csv(csv_path)

    # Employee No를 문자열로 변환
    df['Employee No'] = df['Employee No'].astype(str)

    # AQL Inspector 필터링
    aql_inspectors = df[
        (df['ROLE TYPE STD'] == 'TYPE-1') &
        (df['QIP POSITION 1ST  NAME'] == 'AQL INSPECTOR')
    ]

    print(f"\n📊 Found {len(aql_inspectors)} AQL Inspectors in {month_name} {year} data")

    # 월 이름을 소문자로 변환 (config key로 사용)
    month_key = f"{month_name.lower()}_{year}_incentive"
    incentive_col = f"{month_name.capitalize()}_Incentive"

    updated_count = 0

    for emp_id, inspector_config in config['aql_inspectors'].items():
        # 직원 데이터 찾기
        emp_data = aql_inspectors[aql_inspectors['Employee No'] == str(emp_id)]

        if emp_data.empty:
            print(f"⚠️  {inspector_config['name']} ({emp_id}): No data found (resigned or position changed)")
            continue

        emp_row = emp_data.iloc[0]

        # Continuous_Months 읽기
        continuous_months = emp_row.get('Continuous_Months', 0)
        if pd.isna(continuous_months):
            continuous_months = 0
        else:
            continuous_months = int(continuous_months)

        # 인센티브 읽기
        incentive = emp_row.get(incentive_col, 0)
        if pd.isna(incentive):
            incentive = 0
        else:
            incentive = int(incentive)

        # Part 3 months (다음 달 계산용)
        part3_months = min(continuous_months + 1, 15)  # Cap at 15

        # Config 업데이트
        new_data = {
            "part1_months": continuous_months,
            "part3_months": part3_months,
            "total": incentive
        }

        inspector_config[month_key] = new_data

        print(f"✅ {inspector_config['name']} ({emp_id}): "
              f"{continuous_months}개월 → {incentive:,} VND")

        updated_count += 1

    print(f"\n✅ Updated {updated_count} AQL Inspectors")

    return config

def save_config(config):
    """업데이트된 config 저장"""
    config_path = Path("config_files/aql_inspector_incentive_config.json")

    # 백업 생성
    backup_path = config_path.with_suffix(f'.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    if config_path.exists():
        import shutil
        shutil.copy2(config_path, backup_path)
        print(f"\n💾 Backup created: {backup_path.name}")

    # 저장
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✅ Config saved: {config_path}")

def main():
    """메인 함수"""

    if len(sys.argv) < 3:
        print("Usage: python auto_update_aql_config.py <month> <year>")
        print("Example: python auto_update_aql_config.py november 2025")
        sys.exit(1)

    month_name = sys.argv[1].lower()
    year = int(sys.argv[2])

    print("=" * 70)
    print(f"🔄 AQL Inspector Config Auto-Update")
    print(f"📅 Month: {month_name.capitalize()} {year}")
    print("=" * 70)

    # 1. Config 로드
    print("\n📂 Loading config...")
    config = load_config()

    # 2. 최신 output 파일 찾기
    print(f"\n🔍 Finding latest output file for {month_name} {year}...")
    csv_path = find_latest_output_file(year, month_name)

    # 3. Config 업데이트
    print(f"\n🔄 Updating config from {csv_path.name}...")
    config = update_config_from_data(config, csv_path, month_name, year)

    # 4. 저장
    print(f"\n💾 Saving updated config...")
    save_config(config)

    print("\n" + "=" * 70)
    print("✅ AQL Inspector config auto-update completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
