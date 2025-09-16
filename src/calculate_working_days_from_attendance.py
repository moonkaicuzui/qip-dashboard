#!/usr/bin/env python3
"""
Attendance 데이터에서 실제 근무일수를 자동 계산하여 Config 파일을 업데이트
action.sh에서 자동 실행되어 항상 정확한 근무일수 보장
"""

import json
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

def find_attendance_file(month_name, year):
    """여러 경로에서 attendance 파일 찾기"""
    possible_paths = [
        f"input_files/attendance/converted/attendance data {month_name}_converted.csv",
        f"input_files/attendance data {month_name}.csv",
        f"input_files/{year}년 {month_name} attendance.csv",
        f"input_files/attendance/{month_name}_attendance.csv",
        # 대소문자 변형도 시도
        f"input_files/attendance/converted/attendance data {month_name.lower()}_converted.csv",
        f"input_files/attendance/converted/attendance data {month_name.upper()}_converted.csv",
        f"input_files/attendance/converted/attendance data {month_name.capitalize()}_converted.csv",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def calculate_working_days(attendance_file):
    """Attendance 파일에서 실제 근무일수 계산 (평일만)"""
    try:
        df = pd.read_csv(attendance_file)

        # Date 컬럼 찾기 (여러 가능한 이름 시도)
        date_columns = ['Date', 'date', 'DATE', '날짜', '일자', 'Work Date']
        date_col = None

        for col in date_columns:
            if col in df.columns:
                date_col = col
                break

        if not date_col:
            print(f"  ⚠️ 날짜 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)[:5]}...")
            return None

        # 날짜 파싱
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        unique_dates = df[date_col].dropna().unique()

        if len(unique_dates) == 0:
            print(f"  ⚠️ 유효한 날짜 데이터가 없습니다.")
            return None

        # 실제 공장 가동일 계산 (출근 인원 기준)
        # 베트남 공장은 토요일도 근무하므로 실제 출근 데이터 기반 판단

        # 날짜별 출근 인원 계산
        daily_attendance = df.groupby(df[date_col].dt.date)['ID No'].nunique() if 'ID No' in df.columns else df.groupby(df[date_col].dt.date).size()

        # 정상 가동일: 300명 이상 출근 (또는 전체 평균의 70% 이상)
        avg_attendance = daily_attendance.mean()
        threshold = max(300, avg_attendance * 0.7)  # 300명 또는 평균의 70% 중 큰 값

        working_days_list = daily_attendance[daily_attendance >= threshold]
        working_days = len(working_days_list)

        # 통계 출력
        total_days = len(unique_dates)
        non_working_days = total_days - working_days

        print(f"  📅 전체 기록: {total_days}일")
        print(f"  🏭 정상 가동일 ({int(threshold)}명 이상): {working_days}일")
        print(f"  🛋️ 휴무/부분 가동: {non_working_days}일")

        # 주말 근무 현황 확인
        weekend_work_count = sum(1 for date, count in working_days_list.items()
                                if pd.Timestamp(date).weekday() >= 5)
        if weekend_work_count > 0:
            print(f"  🗓️ 토요일 근무: {weekend_work_count}일 포함")

        return working_days

    except Exception as e:
        print(f"  ❌ 파일 읽기 오류: {e}")
        return None

def update_config_working_days(month_name, year, working_days):
    """Config 파일의 working_days 업데이트"""
    config_path = f"config_files/config_{month_name}_{year}.json"

    if not os.path.exists(config_path):
        print(f"  ⚠️ Config 파일이 없습니다: {config_path}")
        return False

    try:
        # 기존 config 읽기
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        old_value = config.get('working_days', 'N/A')
        config['working_days'] = working_days
        config['working_days_source'] = 'attendance_data'
        config['working_days_updated_at'] = datetime.now().isoformat()

        # 업데이트된 config 저장
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        if old_value != working_days:
            print(f"  ✅ Config 업데이트: working_days {old_value} → {working_days}")
        else:
            print(f"  ✅ Config 확인: working_days = {working_days} (변경 없음)")

        return True

    except Exception as e:
        print(f"  ❌ Config 업데이트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱
    if len(sys.argv) < 3:
        print("사용법: python calculate_working_days_from_attendance.py <month> <year>")
        sys.exit(1)

    month_name = sys.argv[1].lower()
    year = sys.argv[2]

    print(f"\n🔄 {year}년 {month_name} 근무일수 자동 계산 중...")
    print("-" * 50)

    # 1. Attendance 파일 찾기
    attendance_file = find_attendance_file(month_name, year)

    if not attendance_file:
        print(f"  ❌ {month_name} attendance 파일을 찾을 수 없습니다.")
        print("  ℹ️ Config의 working_days를 수동으로 확인해주세요.")
        return

    print(f"  📁 Attendance 파일: {attendance_file}")

    # 2. 근무일수 계산
    working_days = calculate_working_days(attendance_file)

    if working_days is None:
        print("  ❌ 근무일수를 계산할 수 없습니다.")
        return

    print(f"  📊 계산된 근무일수: {working_days}일")

    # 3. Config 파일 업데이트
    if update_config_working_days(month_name, year, working_days):
        print(f"\n✅ {year}년 {month_name} 근무일수가 {working_days}일로 설정되었습니다.")
    else:
        print("\n⚠️ Config 파일 업데이트에 실패했습니다.")

if __name__ == "__main__":
    main()