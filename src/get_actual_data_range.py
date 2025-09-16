#!/usr/bin/env python3
"""
각 데이터 파일의 실제 날짜 범위를 가져오는 유틸리티
대시보드에 정확한 데이터 기간을 표시하기 위함
"""

import pandas as pd
import os
from datetime import datetime

def get_attendance_date_range(month, year):
    """출근 데이터의 실제 날짜 범위 반환"""
    try:
        file_path = f"input_files/attendance/converted/attendance data {month}_converted.csv"
        if not os.path.exists(file_path):
            return None, None

        df = pd.read_csv(file_path)

        # Work Date 컬럼 파싱
        if 'Work Date' in df.columns:
            df['Work Date'] = pd.to_datetime(df['Work Date'], errors='coerce')
            min_date = df['Work Date'].min()
            max_date = df['Work Date'].max()
            return min_date, max_date
    except:
        pass
    return None, None

def get_incentive_date_range(month, year):
    """인센티브 데이터의 실제 날짜 범위 반환"""
    # 인센티브는 보통 월 전체 데이터
    # 하지만 Entrance Date나 Stop working Date를 분석할 수 있음
    try:
        file_path = f"output_files/output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv"
        if not os.path.exists(file_path):
            return None, None

        # 인센티브는 월 단위이므로 1일 ~ 월말 반환
        import calendar
        month_num = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december'].index(month.lower()) + 1
        last_day = calendar.monthrange(year, month_num)[1]

        first_date = pd.Timestamp(year, month_num, 1)
        last_date = pd.Timestamp(year, month_num, last_day)
        return first_date, last_date
    except:
        pass
    return None, None

def get_aql_date_range(month, year):
    """AQL 데이터의 실제 날짜 범위 반환"""
    # AQL 파일에서 실제 날짜 범위 확인
    # 파일 구조에 따라 다를 수 있음
    return get_incentive_date_range(month, year)  # 일단 월 전체로 가정

def get_5prs_date_range(month, year):
    """5PRS 데이터의 실제 날짜 범위 반환"""
    try:
        file_path = f"input_files/5prs data {month}.csv"
        if not os.path.exists(file_path):
            return None, None

        df = pd.read_csv(file_path)

        # Date 관련 컬럼 찾기
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'Date' in col]

        if date_cols:
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            min_date = df[date_col].min()
            max_date = df[date_col].max()

            if pd.notna(min_date) and pd.notna(max_date):
                return min_date, max_date
    except:
        pass

    # 날짜 컬럼이 없으면 출근 데이터와 동일한 기간으로 가정
    return get_attendance_date_range(month, year)

def get_all_data_ranges(month, year):
    """모든 데이터의 날짜 범위를 딕셔너리로 반환"""
    ranges = {
        'attendance': get_attendance_date_range(month, year),
        'incentive': get_incentive_date_range(month, year),
        'aql': get_aql_date_range(month, year),
        '5prs': get_5prs_date_range(month, year)
    }

    return ranges

if __name__ == "__main__":
    # 테스트
    import sys

    if len(sys.argv) > 2:
        month = sys.argv[1]
        year = int(sys.argv[2])
    else:
        month = 'september'
        year = 2025

    print(f"\n📊 {year}년 {month} 실제 데이터 범위")
    print("=" * 60)

    ranges = get_all_data_ranges(month, year)

    for data_type, (min_date, max_date) in ranges.items():
        if min_date and max_date:
            print(f"{data_type:10}: {min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
        else:
            print(f"{data_type:10}: 데이터 없음")