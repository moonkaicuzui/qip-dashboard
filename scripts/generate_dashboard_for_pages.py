#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Pages용 대시보드 자동 생성 스크립트
Google Drive에서 다운로드한 CSV 파일들로 HTML 대시보드 생성
"""

import os
import sys
import glob
import subprocess
from datetime import datetime

# 상위 디렉토리를 경로에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def find_csv_files():
    """output_files 디렉토리에서 CSV 파일 찾기"""
    csv_pattern = "output_files/output_QIP_incentive_*_Complete_V*.csv"
    csv_files = glob.glob(csv_pattern)

    # 파일명에서 월과 연도 추출
    files_info = []
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

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
    print("=" * 60)
    print("🚀 GitHub Pages용 대시보드 생성 시작")
    print("=" * 60)

    # CSV 파일 찾기
    csv_files = find_csv_files()

    if not csv_files:
        print("⚠️ CSV 파일을 찾을 수 없습니다")
        print("Google Drive 다운로드를 먼저 실행하세요")
        sys.exit(1)

    print(f"\n📊 {len(csv_files)}개월 데이터 발견")

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