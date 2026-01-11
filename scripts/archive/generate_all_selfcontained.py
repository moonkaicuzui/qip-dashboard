#!/usr/bin/env python3
"""
Generate Self-Contained HTML for Dashboards (최적화 버전)
==========================================================
- 기본: 현재 월만 생성 (성능 최적화)
- --all: 모든 월 생성 (필요시)

@PerformanceEngineer 최적화: 모든 월 → 현재 월만 처리

Used by GitHub Actions to keep SelfContained HTML in sync
with web dashboards on every 30-minute update.
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from create_self_contained_html import create_self_contained_html


def get_current_month_year():
    """현재 월과 연도 반환"""
    now = datetime.now()
    return now.month, now.year


def find_dashboard_files(docs_dir: Path, current_only: bool = True) -> list:
    """Find dashboard HTML files (excluding SelfContained versions).

    Args:
        docs_dir: 문서 디렉토리
        current_only: True면 현재 월만, False면 모든 월
    """
    pattern = re.compile(r'Incentive_Dashboard_(\d{4})_(\d{2})_Version_[\d.]+\.html$')

    current_month, current_year = get_current_month_year()

    dashboard_files = []
    for html_file in docs_dir.glob('*.html'):
        # Skip SelfContained versions
        if 'SelfContained' in html_file.name:
            continue

        match = pattern.match(html_file.name)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))

            # 현재 월만 처리 모드
            if current_only:
                if month == current_month and year == current_year:
                    dashboard_files.append({
                        'path': html_file,
                        'year': year,
                        'month': month,
                        'name': html_file.name
                    })
            else:
                dashboard_files.append({
                    'path': html_file,
                    'year': year,
                    'month': month,
                    'name': html_file.name
                })

    return sorted(dashboard_files, key=lambda x: (x['year'], x['month']))


def generate_selfcontained(dashboard_info: dict) -> bool:
    """Generate SelfContained HTML for a single dashboard."""
    input_path = dashboard_info['path']
    output_name = input_path.stem + '_SelfContained.html'
    output_path = input_path.parent / output_name

    try:
        print(f"\n{'='*60}")
        print(f"📦 Generating: {output_name}")
        print(f"{'='*60}")

        create_self_contained_html(str(input_path), str(output_path))
        return True
    except Exception as e:
        print(f"❌ Error generating {output_name}: {e}")
        return False


def main():
    """Main function to generate SelfContained HTML files."""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='SelfContained HTML 생성')
    parser.add_argument('--all', action='store_true',
                        help='모든 월 SelfContained 생성 (기본: 현재 월만)')
    args = parser.parse_args()

    print("="*60)
    if args.all:
        print("🔄 Generate All SelfContained HTML Files (전체 월 모드)")
    else:
        print("🔄 Generate SelfContained HTML (현재 월만 - 최적화 모드)")
        print("   💡 모든 월 생성: --all 옵션 사용")
    print("="*60)

    # Find docs directory
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print(f"❌ Error: docs directory not found")
        return 1

    # Check if CDN libraries exist
    lib_dir = Path('static/cdn_libraries')
    required_libs = [
        'bootstrap.min.css',
        'bootstrap.bundle.min.js',
        'fontawesome.min.css',
        'chart.min.js',
        'd3.v7.min.js'
    ]

    missing_libs = []
    for lib in required_libs:
        if not (lib_dir / lib).exists():
            missing_libs.append(lib)

    if missing_libs:
        print(f"❌ Error: Missing CDN libraries: {missing_libs}")
        print(f"   Please ensure static/cdn_libraries/ contains all required files.")
        return 1

    print(f"✅ CDN libraries found: {len(required_libs)} files")

    # Find dashboard files
    dashboards = find_dashboard_files(docs_dir, current_only=not args.all)

    if not dashboards:
        if args.all:
            print(f"⚠️ No dashboard HTML files found in {docs_dir}")
            return 0
        else:
            # 현재 월 파일이 없으면 최신 월 처리
            print(f"⚠️ 현재 월 대시보드가 없습니다. 최신 월을 찾습니다...")
            dashboards = find_dashboard_files(docs_dir, current_only=False)
            if dashboards:
                # 가장 최신 1개만 처리
                dashboards = [dashboards[-1]]
                print(f"📌 최신 파일 처리: {dashboards[0]['year']}/{dashboards[0]['month']:02d}")
            else:
                print(f"⚠️ No dashboard HTML files found in {docs_dir}")
                return 0

    print(f"\n📋 처리할 대시보드: {len(dashboards)}개")
    for d in dashboards:
        print(f"   - {d['year']}/{d['month']:02d}: {d['name']}")

    # Generate SelfContained for each dashboard
    success_count = 0
    fail_count = 0

    for dashboard in dashboards:
        if generate_selfcontained(dashboard):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📁 Total: {success_count + fail_count}")

    if fail_count > 0:
        print(f"\n⚠️ Some SelfContained files failed to generate!")
        return 1

    print(f"\n✅ SelfContained HTML 생성 완료!")
    return 0


if __name__ == '__main__':
    exit(main())
