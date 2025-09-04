#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THỊ MINH PHƯỢNG 직원의 출결 데이터 분석
"""

import pandas as pd
from datetime import datetime

# CSV 파일 읽기
file_path = 'input_files/attendance/converted/attendance data august_converted.csv'
df = pd.read_csv(file_path)

# THỊ MINH PHƯỢNG의 데이터만 필터링
employee_id = 620080271
employee_data = df[df['ID No'] == employee_id].copy()

# 날짜 컬럼 변환
employee_data['Work Date'] = pd.to_datetime(employee_data['Work Date'], format='%Y.%m.%d')

# 데이터 분석
print("=" * 60)
print("THỊ MINH PHƯỢNG (ID: 620080271) 8월 출결 데이터 분석")
print("=" * 60)

# 1. 총 데이터 개수
total_records = len(employee_data)
print(f"\n1. 총 데이터 개수: {total_records}개")

# 2. 출근/결근 상태 분석
attendance_status = employee_data['compAdd'].value_counts()
print(f"\n2. 출결 상태 분석:")
for status, count in attendance_status.items():
    print(f"   - {status}: {count}개")

# 3. 날짜별 상세 정보
print(f"\n3. 날짜별 상세 정보:")
print("-" * 40)
for idx, row in employee_data.iterrows():
    date_str = row['Work Date'].strftime('%Y-%m-%d (%a)')
    status = row['compAdd']
    reason = row['Reason Description'] if pd.notna(row['Reason Description']) else '-'
    print(f"   {date_str}: {status} (사유: {reason})")

# 4. 근무일 계산 (평일만)
start_date = datetime(2025, 8, 1)
end_date = datetime(2025, 8, 15)  # Stop working Date

actual_working_days = 0
current_date = start_date

print(f"\n4. 8월 1일 ~ 8월 15일 평일 분석:")
print("-" * 40)
weekday_count = 0
while current_date <= end_date:
    if current_date.weekday() < 5:  # 월-금 (0-4)
        weekday_count += 1
        # 해당 날짜의 출결 확인
        date_str = current_date.strftime('%Y.%m.%d')
        date_records = employee_data[employee_data['Work Date'] == current_date]
        if not date_records.empty:
            status = date_records.iloc[0]['compAdd']
            if status == 'Đi làm':
                actual_working_days += 1
                print(f"   {current_date.strftime('%Y-%m-%d (%a)')}: 출근")
            else:
                print(f"   {current_date.strftime('%Y-%m-%d (%a)')}: {status}")
        else:
            print(f"   {current_date.strftime('%Y-%m-%d (%a)')}: 데이터 없음")
    current_date += pd.Timedelta(days=1)

print(f"\n5. 결과 요약:")
print("-" * 40)
print(f"   - 8월 1일 ~ 8월 15일 총 평일 수: {weekday_count}일")
print(f"   - 실제 출근일 (Đi làm): {actual_working_days}일")
print(f"   - 총 기록된 데이터: {total_records}개")

# 6. 인센티브 파일 데이터와 비교
incentive_file = 'input_files/2025년 8월 인센티브 지급 세부 정보.csv'
incentive_df = pd.read_csv(incentive_file)
employee_incentive = incentive_df[incentive_df['Employee No'] == employee_id]

if not employee_incentive.empty:
    print(f"\n6. 인센티브 파일 데이터:")
    print("-" * 40)
    print(f"   - Total Working Days: {employee_incentive.iloc[0]['Total Working Days']}")
    print(f"   - Actual Working Days: {employee_incentive.iloc[0]['Actual Working Days']}")
    print(f"   - Stop working Date: {employee_incentive.iloc[0]['Stop working Date']}")