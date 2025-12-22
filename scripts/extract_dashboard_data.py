#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Data Extractor
========================
@DataAnalyst & @BackendEngineer 협업 개발

대시보드 HTML에서 데이터를 추출하여 별도 JSON 파일로 저장
- employeeData: 직원 인센티브 데이터
- excelDashboardData: 요약 통계 데이터
- aqlIncentiveConfig: AQL Inspector 설정

사용법:
    python scripts/extract_dashboard_data.py --month 12 --year 2025
    python scripts/extract_dashboard_data.py --all
"""

import re
import os
import sys
import json
import base64
import gzip
import argparse
from pathlib import Path
from datetime import datetime


def extract_base64_data(content: str, pattern: str) -> dict:
    """Base64로 인코딩된 데이터 추출"""
    match = re.search(pattern, content)
    if match:
        try:
            decoded = base64.b64decode(match.group(1))
            return json.loads(decoded.decode('utf-8'))
        except Exception as e:
            print(f"  ⚠️ Base64 디코딩 실패: {e}")
    return None


def extract_inline_json(content: str, var_name: str) -> dict:
    """인라인 JSON 데이터 추출"""
    # Try different patterns
    patterns = [
        rf'const {var_name} = (\{{.*?\n\s*\}});',
        rf'let {var_name} = (\{{.*?\n\s*\}});',
        rf'var {var_name} = (\{{.*?\n\s*\}});',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            try:
                # Clean up JavaScript-style JSON
                json_str = match.group(1)
                # Remove trailing commas before }
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"  ⚠️ JSON 파싱 실패 ({var_name}): {e}")
    return None


def extract_data_from_html(html_path: str) -> dict:
    """HTML 파일에서 모든 데이터 추출"""
    print(f"\n📦 데이터 추출: {Path(html_path).name}")
    print("=" * 60)

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        'metadata': {
            'source': Path(html_path).name,
            'extracted_at': datetime.now().isoformat(),
            'version': '1.0'
        },
        'employeeData': None,
        'excelDashboardData': None,
        'aqlIncentiveConfig': None
    }

    # 1. employeeData 추출 (hidden div Base64)
    print("  🔍 employeeData 추출 중...")
    # Pattern: <div id="employeeDataBase64" ...>BASE64_DATA</div>
    employee_pattern = r'id="employeeDataBase64"[^>]*>([^<]+)<'
    match = re.search(employee_pattern, content)
    if match:
        try:
            base64_data = match.group(1).strip()
            decoded = base64.b64decode(base64_data)
            data['employeeData'] = json.loads(decoded.decode('utf-8'))
            print(f"    ✅ {len(data['employeeData'])} 직원 데이터 추출 ({len(base64_data):,} bytes)")
        except Exception as e:
            print(f"    ❌ 추출 실패: {e}")

    # 2. excelDashboardData 추출 (hidden div Base64)
    print("  🔍 excelDashboardData 추출 중...")
    # Pattern: <div id="excelDashboardDataBase64" ...>BASE64_DATA</div>
    excel_pattern = r'id="excelDashboardDataBase64"[^>]*>([^<]+)<'
    match = re.search(excel_pattern, content)
    if match:
        try:
            base64_data = match.group(1).strip()
            decoded = base64.b64decode(base64_data)
            data['excelDashboardData'] = json.loads(decoded.decode('utf-8'))
            print(f"    ✅ excelDashboardData 추출 완료 ({len(base64_data):,} bytes)")
        except Exception as e:
            print(f"    ❌ 추출 실패: {e}")

    # 3. aqlIncentiveConfig 추출 (hidden div Base64)
    print("  🔍 aqlIncentiveConfig 추출 중...")
    # Pattern: <div id="aqlIncentiveConfigBase64" ...>BASE64_DATA</div>
    aql_pattern = r'id="aqlIncentiveConfigBase64"[^>]*>([^<]+)<'
    match = re.search(aql_pattern, content)
    if match:
        try:
            base64_data = match.group(1).strip()
            decoded = base64.b64decode(base64_data)
            data['aqlIncentiveConfig'] = json.loads(decoded.decode('utf-8'))
            inspector_count = len(data['aqlIncentiveConfig'].get('aql_inspectors', {}))
            print(f"    ✅ {inspector_count} AQL Inspector 설정 추출 ({len(base64_data):,} bytes)")
        except Exception as e:
            print(f"    ❌ 추출 실패: {e}")

    return data


def save_data_files(data: dict, output_dir: str, month: int, year: int):
    """추출된 데이터를 파일로 저장"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    month_names = {
        1: 'january', 2: 'february', 3: 'march', 4: 'april',
        5: 'may', 6: 'june', 7: 'july', 8: 'august',
        9: 'september', 10: 'october', 11: 'november', 12: 'december'
    }
    month_name = month_names.get(month, str(month))

    saved_files = []

    # Save employeeData
    if data.get('employeeData'):
        filename = f"employee_data_{month_name}_{year}.json"
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data['employeeData'], f, ensure_ascii=False, indent=2)
        size = filepath.stat().st_size
        saved_files.append((filename, size))

        # Also save gzipped version
        gz_filepath = output_path / f"{filename}.gz"
        with gzip.open(gz_filepath, 'wt', encoding='utf-8') as f:
            json.dump(data['employeeData'], f, ensure_ascii=False)
        gz_size = gz_filepath.stat().st_size
        print(f"  💾 {filename}: {size:,} bytes → gzip: {gz_size:,} bytes ({gz_size/size*100:.1f}%)")

    # Save aqlIncentiveConfig
    if data.get('aqlIncentiveConfig'):
        filename = f"aql_config_{month_name}_{year}.json"
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data['aqlIncentiveConfig'], f, ensure_ascii=False, indent=2)
        size = filepath.stat().st_size
        saved_files.append((filename, size))
        print(f"  💾 {filename}: {size:,} bytes")

    # Save summary
    if data.get('excelDashboardData') and not isinstance(data['excelDashboardData'].get('_raw'), str):
        filename = f"dashboard_summary_{month_name}_{year}.json"
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data['excelDashboardData'], f, ensure_ascii=False, indent=2)
        size = filepath.stat().st_size
        saved_files.append((filename, size))
        print(f"  💾 {filename}: {size:,} bytes")

    return saved_files


def main():
    parser = argparse.ArgumentParser(description='Dashboard Data Extractor')
    parser.add_argument('--month', '-m', type=int, help='월 (1-12)')
    parser.add_argument('--year', '-y', type=int, default=2025, help='연도 (기본: 2025)')
    parser.add_argument('--all', '-a', action='store_true', help='모든 대시보드 처리')
    parser.add_argument('--output', '-o', default='docs/data', help='출력 디렉토리')
    args = parser.parse_args()

    print("=" * 60)
    print("📊 Dashboard Data Extractor")
    print("=" * 60)

    docs_dir = Path('docs')

    if args.all:
        # Find all dashboard files
        pattern = re.compile(r'Incentive_Dashboard_(\d{4})_(\d{2})_Version_[\d.]+\.html$')
        html_files = []
        for f in docs_dir.glob('*.html'):
            match = pattern.match(f.name)
            if match and 'SelfContained' not in f.name:
                year, month = int(match.group(1)), int(match.group(2))
                html_files.append((f, month, year))

        if not html_files:
            print("❌ 대시보드 파일을 찾을 수 없습니다")
            return 1

        print(f"🔍 {len(html_files)}개 대시보드 발견")

        for html_file, month, year in sorted(html_files, key=lambda x: (x[2], x[1])):
            data = extract_data_from_html(str(html_file))
            save_data_files(data, args.output, month, year)

    elif args.month:
        # Single month
        html_pattern = f"Incentive_Dashboard_{args.year}_{args.month:02d}_Version_*.html"
        html_files = list(docs_dir.glob(html_pattern))
        html_files = [f for f in html_files if 'SelfContained' not in f.name]

        if not html_files:
            print(f"❌ {args.year}년 {args.month}월 대시보드 파일을 찾을 수 없습니다")
            return 1

        data = extract_data_from_html(str(html_files[0]))
        save_data_files(data, args.output, args.month, args.year)

    else:
        parser.print_help()
        print("\n예시:")
        print("  python scripts/extract_dashboard_data.py --month 12 --year 2025")
        print("  python scripts/extract_dashboard_data.py --all")
        return 1

    print("\n" + "=" * 60)
    print("✅ 데이터 추출 완료!")
    print(f"📁 출력 디렉토리: {args.output}")
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
