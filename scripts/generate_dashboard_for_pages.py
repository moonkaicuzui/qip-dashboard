#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Pages용 대시보드 자동 생성 스크립트 (최적화 버전)
- 기본: 현재 월만 생성 (성능 최적화)
- --all: 모든 월 생성 (필요시)

@PerformanceEngineer 최적화: 5-8분 → 1-2분 (현재 월만 처리)
"""

import os
import sys
import glob
import subprocess
import argparse
from datetime import datetime

# 상위 디렉토리를 경로에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def get_current_month_year():
    """현재 월과 연도 반환"""
    now = datetime.now()
    return now.month, now.year


def find_csv_files(current_only=True):
    """output_files 디렉토리에서 CSV 파일 찾기

    Args:
        current_only: True면 현재 월만, False면 모든 월
    """
    csv_pattern = "output_files/output_QIP_incentive_*_Complete_V*.csv"
    csv_files = glob.glob(csv_pattern)

    # 파일명에서 월과 연도 추출
    files_info = []
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    current_month, current_year = get_current_month_year()

    for file in csv_files:
        try:
            # 파일명 파싱
            filename = os.path.basename(file)
            parts = filename.split('_')

            # 월 찾기
            month_str = None
            month_num = None
            for part in parts:
                if part.lower() in month_names:
                    month_str = part.lower()
                    month_num = month_names[month_str]
                    break

            # 연도 찾기
            year = None
            for part in parts:
                if part.isdigit() and len(part) == 4:
                    year = int(part)
                    break

            if month_num and year:
                # 현재 월만 처리 모드
                if current_only:
                    if month_num == current_month and year == current_year:
                        files_info.append({
                            'file': file,
                            'month': month_num,
                            'month_str': month_str,
                            'year': year,
                            'sort_key': year * 100 + month_num
                        })
                        print(f"✅ 현재 월 발견: {month_str.capitalize()} {year} - {file}")
                else:
                    # 모든 월 처리 모드
                    files_info.append({
                        'file': file,
                        'month': month_num,
                        'month_str': month_str,
                        'year': year,
                        'sort_key': year * 100 + month_num
                    })
                    print(f"✅ 발견: {month_str.capitalize()} {year} - {file}")

        except Exception as e:
            print(f"⚠️ 파일 파싱 실패 {file}: {e}")
            continue

    # 정렬 (최신 월 순)
    files_info.sort(key=lambda x: x['sort_key'], reverse=True)

    return files_info


def generate_dashboard(month, year):
    """특정 월의 대시보드 생성"""
    try:
        print(f"\n🎨 대시보드 생성 중: {year}년 {month}월")

        # integrated_dashboard_final.py 실행
        cmd = [
            sys.executable,
            "integrated_dashboard_final.py",
            "--month", str(month),
            "--year", str(year)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=parent_dir
        )

        if result.returncode == 0:
            print(f"  ✅ 대시보드 생성 성공")

            # 생성된 파일 확인
            html_pattern = f"output_files/Incentive_Dashboard_{year}_{month:02d}_Version_*.html"
            html_files = glob.glob(html_pattern)

            if html_files:
                print(f"  📄 생성된 파일: {html_files[0]}")
                return html_files[0]
            else:
                print(f"  ⚠️ HTML 파일을 찾을 수 없습니다")
                return None
        else:
            print(f"  ❌ 대시보드 생성 실패")
            print(f"  오류: {result.stderr}")
            return None

    except Exception as e:
        print(f"  ❌ 오류 발생: {e}")
        return None


def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='GitHub Pages용 대시보드 생성')
    parser.add_argument('--all', action='store_true',
                        help='모든 월 대시보드 생성 (기본: 현재 월만)')
    parser.add_argument('--force-month', type=int,
                        help='특정 월만 생성 (1-12)')
    parser.add_argument('--force-year', type=int,
                        help='특정 연도 지정 (예: 2025)')
    args = parser.parse_args()

    print("=" * 60)
    if args.all:
        print("🚀 GitHub Pages용 대시보드 생성 (전체 월 모드)")
    elif args.force_month:
        print(f"🚀 GitHub Pages용 대시보드 생성 (특정 월: {args.force_month}월)")
    else:
        print("🚀 GitHub Pages용 대시보드 생성 (현재 월만 - 최적화 모드)")
        print("   💡 모든 월 생성: --all 옵션 사용")
    print("=" * 60)

    # 특정 월 강제 지정
    if args.force_month:
        year = args.force_year or datetime.now().year
        dashboard_file = generate_dashboard(args.force_month, year)
        if dashboard_file:
            print(f"\n✅ 대시보드 생성 완료: {dashboard_file}")
        else:
            print("\n❌ 대시보드 생성 실패")
            sys.exit(1)
        return

    # CSV 파일 찾기
    csv_files = find_csv_files(current_only=not args.all)

    if not csv_files:
        if args.all:
            print("⚠️ CSV 파일을 찾을 수 없습니다")
            print("Google Drive 다운로드를 먼저 실행하세요")
            sys.exit(1)
        else:
            # 현재 월 파일이 없으면 가장 최신 월 처리
            print("⚠️ 현재 월 CSV 파일이 없습니다. 최신 월 파일을 찾습니다...")
            csv_files = find_csv_files(current_only=False)
            if csv_files:
                # 가장 최신 1개만 처리
                csv_files = [csv_files[0]]
                print(f"📌 최신 파일 처리: {csv_files[0]['month_str'].capitalize()} {csv_files[0]['year']}")
            else:
                print("⚠️ CSV 파일을 찾을 수 없습니다")
                sys.exit(1)

    print(f"\n📊 {len(csv_files)}개월 데이터 처리 예정")

    # 각 월별로 대시보드 생성
    generated_dashboards = []
    for file_info in csv_files:
        dashboard_file = generate_dashboard(file_info['month'], file_info['year'])
        if dashboard_file:
            generated_dashboards.append({
                'file': dashboard_file,
                'month': file_info['month'],
                'year': file_info['year'],
                'month_str': file_info['month_str']
            })

    # 결과 출력
    print("\n" + "=" * 60)
    if generated_dashboards:
        print(f"✅ 총 {len(generated_dashboards)}개 대시보드 생성 완료")
        print("\n생성된 대시보드:")
        for dashboard in generated_dashboards:
            print(f"  - {dashboard['year']}년 {dashboard['month']}월")
    else:
        print("❌ 생성된 대시보드가 없습니다")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()
