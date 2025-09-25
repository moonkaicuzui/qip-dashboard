#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Total Working Days 계산 모듈
attendance CSV 파일의 유니크 날짜 개수를 기준으로 계산
"""

import pandas as pd
from datetime import datetime

def calculate_total_working_days_from_attendance(year, month):
    """
    attendance CSV 파일에서 해당 월의 유니크 날짜 수를 계산하여
    Total Working Days를 반환
    
    Args:
        year: 연도
        month: 월
        
    Returns:
        int: 해당 월의 Total Working Days (유니크 날짜 수)
    """
    try:
        # attendance CSV 파일 경로
        attendance_file = 'input_files/attendance/converted/attendance data august_converted.csv'
        
        # CSV 파일 읽기
        df = pd.read_csv(attendance_file, encoding='utf-8-sig')
        
        # Work Date 컬럼 찾기
        date_cols = ['Work Date', 'WorkDate', 'Date', '날짜']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            print(f"❌ 오류: 날짜 컬럼을 찾을 수 없습니다.")
            print(f"   attendance CSV 파일에 'Work Date' 컬럼이 있는지 확인하세요.")
            return None
        
        # 해당 년월 패턴 (예: "2025.08")
        date_pattern = f"{year}.{month:02d}"
        
        # 해당 월의 데이터만 필터링
        month_dates = df[df[date_col].str.contains(date_pattern, na=False)][date_col]
        
        # 유니크한 날짜 추출
        unique_dates = month_dates.str.extract(r'(\d{4}\.\d{2}\.\d{2})')[0].unique()
        
        # 유니크 날짜 수가 Total Working Days
        total_working_days = len(unique_dates)
        
        print(f"✅ {year}년 {month}월 Total Working Days: {total_working_days}일 (attendance CSV 기준)")
        
        # 날짜별 상세 정보 (디버깅용)
        if total_working_days > 0:
            # 날짜를 datetime으로 변환하여 요일 확인
            dates_list = []
            for date_str in sorted(unique_dates):
                try:
                    date_obj = datetime.strptime(date_str, '%Y.%m.%d')
                    weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date_obj.weekday()]
                    dates_list.append(f"{date_str} ({weekday})")
                except:
                    pass
            
            # 평일과 주말 구분
            weekdays = sum(1 for d in unique_dates if datetime.strptime(d, '%Y.%m.%d').weekday() < 5)
            weekends = total_working_days - weekdays
            
            print(f"  - 평일: {weekdays}일")
            print(f"  - 주말: {weekends}일")
            
        return total_working_days
        
    except Exception as e:
        print(f"❌ Total Working Days 계산 실패: {e}")
        print(f"   attendance CSV 파일이 존재하고 올바른 형식인지 확인하세요.")
        return None


def get_employee_attendance_data_count(employee_id, year, month):
    """
    특정 직원의 attendance 데이터 개수 반환
    
    Args:
        employee_id: 직원 ID
        year: 연도
        month: 월
        
    Returns:
        int: 해당 직원의 attendance 데이터 개수
    """
    try:
        # attendance CSV 파일 경로
        attendance_file = 'input_files/attendance/converted/attendance data august_converted.csv'
        
        # CSV 파일 읽기
        df = pd.read_csv(attendance_file, encoding='utf-8-sig')
        
        # 해당 직원 데이터 필터링
        if 'ID No' in df.columns:
            employee_data = df[df['ID No'] == employee_id]
        elif 'Employee No' in df.columns:
            employee_data = df[df['Employee No'] == employee_id]
        else:
            return 0
        
        # 해당 년월 패턴
        date_pattern = f"{year}.{month:02d}"
        
        # Work Date 컬럼 찾기
        date_cols = ['Work Date', 'WorkDate', 'Date', '날짜']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if date_col and len(employee_data) > 0:
            # 해당 월의 데이터만 필터링
            month_data = employee_data[employee_data[date_col].str.contains(date_pattern, na=False)]
            return len(month_data)
        
        return 0
        
    except Exception as e:
        print(f"⚠️ 직원 attendance 데이터 개수 계산 실패: {e}")
        return 0


if __name__ == "__main__":
    # 테스트: 2025년 8월
    total_days = calculate_total_working_days_from_attendance(2025, 8)
    print(f"\n최종 Total Working Days: {total_days}일")
    
    # 특정 직원 테스트
    employee_id = 620080271  # THỊ MINH PHƯỢNG
    employee_count = get_employee_attendance_data_count(employee_id, 2025, 8)
    print(f"\n직원 {employee_id}의 데이터 개수: {employee_count}개")