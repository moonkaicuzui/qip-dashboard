#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
integrated incentive dashboard creation 시스템 - final version
dashboard_version4.html의 정확한 UI 복제
actual incentive data use
Google Drive 연동 기능 포함
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime
import glob
import argparse
import base64
from src.google_drive_manager import GoogleDriveManager

# 전역 변count로 번역 data 저장
TRANSLATIONS = {}

def load_translations():
    """번역 file load"""
    global TRANSLATIONS
    translations_file = 'config_files/dashboard_translations.json'
    try:
        with open(translations_file, 'r', encoding='utf-8') as f:
            TRANSLATIONS = json.load(f)
        print(f"✅ Translation file loaded successfully: {translations_file}")
        return True
    except Exception as e:
        print(f"❌ Translation file load failed: {e}")
        # default value 설정
        TRANSLATIONS = {
            "languages": {"ko": "한국어", "en": "English", "vi": "Tiếng Việt"},
            "headers": {"title": {"ko": "QIP incentive dashboard", "en": "QIP Incentive Dashboard", "vi": "Bảng điều khiển khen thưởng QIP"}}
        }
        return False

def get_translation(key_path, lang='ko'):
    """번역 값 fetch (key_path는 점으로 구분된 경로)"""
    try:
        keys = key_path.split('.')
        value = TRANSLATIONS
        for key in keys:
            value = value[key]
        return value.get(lang, value.get('ko', key_path))
    except (KeyError, AttributeError):
        return key_path

def get_month_translation(month, lang='ko'):
    """month 이름 번역"""
    month_translations = {
        'january': {'ko': '1월', 'en': 'January', 'vi': 'Tháng 1'},
        'february': {'ko': '2월', 'en': 'February', 'vi': 'Tháng 2'},
        'march': {'ko': '3월', 'en': 'March', 'vi': 'Tháng 3'},
        'april': {'ko': '4월', 'en': 'April', 'vi': 'Tháng 4'},
        'may': {'ko': '5월', 'en': 'May', 'vi': 'Tháng 5'},
        'june': {'ko': '6월', 'en': 'June', 'vi': 'Tháng 6'},
        'july': {'ko': '7월', 'en': 'July', 'vi': 'Tháng 7'},
        'august': {'ko': '8월', 'en': 'August', 'vi': 'Tháng 8'},
        'september': {'ko': '9월', 'en': 'September', 'vi': 'Tháng 9'},
        'october': {'ko': '10월', 'en': 'October', 'vi': 'Tháng 10'},
        'november': {'ko': '11월', 'en': 'November', 'vi': 'Tháng 11'},
        'december': {'ko': '12월', 'en': 'December', 'vi': 'Tháng 12'}
    }
    
    month_key = month.lower()
    if month_key in month_translations:
        return month_translations[month_key].get(lang, month_translations[month_key]['ko'])
    return month

def get_korean_month(month):
    """하위 호환성을 위한 함count 유지"""
    return get_month_translation(month, 'ko')

def determine_type_from_position(position):
    """직급에서 Type determination"""
    position_upper = str(position).upper()
    
    # TYPE-3: New QIP Members (신입 직원)
    if 'NEW QIP MEMBER' in position_upper:
        return 'TYPE-3'
    
    # TYPE-1 positions (전문 검사 직급)
    type1_positions = [
        'AQL INSPECTOR', 'ASSEMBLY INSPECTOR', 'AUDIT & TRAINING',
        'MODEL MASTER', 'MANAGER', 'A.MANAGER', 'ASSISTANT MANAGER',
        'LINE LEADER', '(V) SUPERVISOR', 'V.SUPERVISOR'
    ]
    
    # TYPE-2 positions (th반 검사 직급)
    type2_positions = [
        'STITCHING INSPECTOR', 'BOTTOM INSPECTOR', 'MTL INSPECTOR',
        'OSC INSPECTOR', 'GROUP LEADER'
    ]
    
    # Check for TYPE-1
    for t1_pos in type1_positions:
        if t1_pos in position_upper:
            return 'TYPE-1'
    
    # Check for TYPE-2
    for t2_pos in type2_positions:
        if t2_pos in position_upper:
            return 'TYPE-2'
    
    # Default to TYPE-2 for unknown positions
    return 'TYPE-2'

def generate_previous_month_data(current_month='august', current_year=2025):
    """Previous month data 자동 creation"""
    import random
    
    # Previous month calculation
    month_map = {
        'january': 12, 'february': 1, 'march': 2, 'april': 3,
        'may': 4, 'june': 5, 'july': 6, 'august': 7,
        'september': 8, 'october': 9, 'november': 10, 'december': 11
    }
    
    month_names = ['january', 'february', 'march', 'april', 'may', 'june', 
                   'july', 'august', 'september', 'october', 'november', 'december']
    
    current_month_num = month_map.get(current_month.lower(), 7)
    prev_month_name = month_names[current_month_num - 1] if current_month_num > 0 else 'december'
    prev_year = current_year if current_month_num > 0 else current_year - 1
    
    # Single Source of Truth: Excel file에 Previous month data가 포함되어 있음
    # by도 file load 불필요
    print(f"✅ Previous month({prev_month_name}) data uses Previous_Incentive column from Excel")
    
    # 가짜 data를 creation하지 않고 빈 값으로 반환
    # actual data가 없을 때는 0 또는 빈 값으로 표시
    
    return prev_month_name, prev_year

def load_incentive_data(month='august', year=2025, generate_prev=True):
    """actual Incentive data loaded"""
    
    # Previous month data creation/load
    if generate_prev:
        prev_month_name, prev_year = generate_previous_month_data(month, year)
    
    # available file 패턴들 - output_files를 먼저 확인
    # V9.1 → V9.0 → V8.02 순서로 확인 - 통일된 fallback 패턴 (2025-12-01)
    month_str = 'august' if month == 8 else 'september' if month == 9 else str(month)
    patterns = [
        f"output_files/output_QIP_incentive_{month_str}_{year}_Complete_V9.1_Complete.csv",  # V9.1 exact match
        f"output_files/output_QIP_incentive_{month_str}_{year}_Complete_V9.0_Complete.csv",  # V9.0 fallback
        f"output_files/output_QIP_incentive_{month_str}_{year}_Complete_V8.02_Complete.csv",  # V8.02 fallback
        f"output_files/output_QIP_incentive_{month_str}_{year}_final완성version_v6.0_Complete_enhanced.csv",
        f"output_files/output_QIP_incentive_{month_str}_{year}_final완성version_v6.0_Complete.csv",
        f"output_files/output_QIP_incentive_{month}_{year}_final완성version_v6.0_Complete.csv",
        f"input_files/{year}년 {get_korean_month(month)} 인센티브 지급 세부 정보.csv"
    ]

    # Try exact patterns first
    csv_file = None
    for pattern in patterns:
        if os.path.exists(pattern):
            csv_file = pattern
            break

    # Fallback to glob with .backup exclusion
    if not csv_file:
        wildcard_pattern = f"output_files/output_QIP_incentive_{month_str}_{year}_*.csv"
        files = [f for f in glob.glob(wildcard_pattern) if '.backup.' not in f]
        if files:
            csv_file = files[0]

    if csv_file:
            print(f"✅ Incentive data loaded: {csv_file}")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            # Position column 찾기
            position_col = None
            for col in df.columns:
                if 'POSITION' in col.upper() and '1ST' in col.upper():
                    position_col = col
                    break
                elif 'POSITION' in col.upper():
                    position_col = col
                    break
            
            # column 이름 표준화
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'employee' in col_lower and 'no' in col_lower:
                    column_mapping[col] = 'emp_no'
                elif col_lower in ['name', 'full name', 'employee name'] or col == 'Full Name':
                    column_mapping[col] = 'name'
                elif position_col and col == position_col:
                    column_mapping[col] = 'position'
                elif 'ROLE TYPE STD' in col:
                    column_mapping[col] = 'type'
                elif col_lower == 'type':
                    column_mapping[col] = 'type'
                elif col == 'Unapproved Absences':
                    column_mapping[col] = 'unapproved_absences'
                elif col == 'Actual Working Days':
                    column_mapping[col] = 'actual_working_days'
                elif f'{month.lower()}_incentive' in col_lower or f'{month.lower()} incentive' in col_lower:
                    column_mapping[col] = f'{month.lower()}_incentive'
                elif f'{month.capitalize()}_Incentive' in col:  # Handle capitalized month names
                    column_mapping[col] = f'{month.lower()}_incentive'
                elif col == 'Final Incentive amount':  # Map Final Incentive amount to current month's incentive
                    column_mapping[col] = f'{month.lower()}_incentive'
                elif 'August_Incentive' in col:  # For other months showing August data
                    column_mapping[col] = 'august_incentive'
                elif 'July_Incentive' in col:
                    column_mapping[col] = 'july_incentive'
                elif 'Previous_Incentive' in col:
                    column_mapping[col] = 'previous_incentive'
                elif col_lower == '출근율_Attendance_Rate_Percent' or (col_lower == 'attendance rate'):
                    column_mapping[col] = '출근율_Attendance_Rate_Percent'
                elif col_lower.startswith('cond_'):
                    # Skip condition columns
                    pass
                elif 'actual' in col_lower and 'working' in col_lower:
                    column_mapping[col] = 'actual_working_days'
                elif 'talent_pool_member' in col_lower:
                    column_mapping[col] = 'Talent_Pool_Member'
                elif 'talent_pool_bonus' in col_lower:
                    column_mapping[col] = 'Talent_Pool_Bonus'
            
            df = df.rename(columns=column_mapping)

            # 디버그: 매핑된 column 확인
            print(f"✅ Column mapping completed: {month}_incentive column exists: {f'{month.lower()}_incentive' in df.columns}")
            if f'{month.lower()}_incentive' in df.columns:
                non_zero = (df[f'{month.lower()}_incentive'] > 0).sum()
                print(f"   - {month}_incentive 직원 with non-zero values: {non_zero}직원")

            # Type column이 없으면 position에서 determination
            if 'type' not in df.columns and 'position' in df.columns:
                df['type'] = df['position'].apply(determine_type_from_position)
                print(f"✅ Type auto-determined (position-based): TYPE-1 {(df['type']=='TYPE-1').sum()}직원, TYPE-2 {(df['type']=='TYPE-2').sum()}직원, TYPE-3 {(df['type']=='TYPE-3').sum()}직원")
            elif 'type' in df.columns:
                # Type 통계 출력
                type_counts = df['type'].value_counts()
                print(f"✅ Type information loaded: TYPE-1 {type_counts.get('TYPE-1', 0)}직원, TYPE-2 {type_counts.get('TYPE-2', 0)}직원, TYPE-3 {type_counts.get('TYPE-3', 0)}직원")
            
            # 필count column 확인 및 default value 설정
            required_columns = ['emp_no', 'name', 'position', 'type', f'{month.lower()}_incentive']
            for col in required_columns:
                if col not in df.columns:
                    if col == f'{month.lower()}_incentive':
                        # corresponding month의 Incentive column 찾기
                        for orig_col in df.columns:
                            if month.lower() in orig_col.lower() and 'incentive' in orig_col.lower():
                                df[col] = df[orig_col]
                                break
                    elif col == 'type':
                        df[col] = 'TYPE-2'  # default value
                    else:
                        df[col] = ''
            
            # 조건 column 추가 (default value)
            condition_columns = ['condition1', 'condition2', 'condition3', 'condition4',
                               'condition5', 'condition6', 'condition7', 'condition8',
                               'condition9', 'condition10']
            for col in condition_columns:
                if col not in df.columns:
                    df[col] = 'no'
            
            # 담당구역 매핑 load
            area_mapping = load_area_mapping()
            
            # Single Source of Truth: AQL data는 이미 Excel에 포함됨
            # Excel의 data를 그대로 use (by도 CSV load 없음)
            print("✅ AQL data: Used directly from Excel file (Single Source of Truth)")

            # Excel에 이미 있는 AQL 관련 column들 확인 및 매핑 (현재 월 기준 동적 컬럼명)
            aql_column_name = f'{month.capitalize()} AQL Failures'
            if aql_column_name in df.columns:
                df['aql_failures'] = df[aql_column_name].fillna(0).astype(int)
            else:
                df['aql_failures'] = 0

            if 'Continuous_FAIL' in df.columns:
                df['continuous_fail'] = df['Continuous_FAIL'].fillna('NO')
            else:
                df['continuous_fail'] = 'NO'

            if 'Area_Reject_Rate' in df.columns:
                df['area_reject_rate'] = df['Area_Reject_Rate'].fillna(0)
            else:
                df['area_reject_rate'] = 0

            # area_consecutive_fail은 Excel에 없으면 default value use
            df['area_consecutive_fail'] = 'NO'  # Excel에 column이 없으므로 default value

            print(f"   - 직원 with AQL failure records: {(df['aql_failures'] > 0).sum()}직원")
            print(f"   - 3연속 개월 실패: {(df['continuous_fail'] == 'YES').sum()}직원")
            
            # Single Source of Truth: 5PRS data는 이미 Excel에 포함됨
            # Excel의 data를 그대로 use (by도 CSV load 없음)
            print("✅ 5PRS data: Used directly from Excel file (Single Source of Truth)")

            # Excel에 이미 있는 5PRS 관련 column들 확인 및 매핑
            if '5PRS_Pass_Rate' in df.columns:
                df['pass_rate'] = df['5PRS_Pass_Rate'].fillna(0)
            else:
                df['pass_rate'] = 0

            if '5PRS_Inspection_Qty' in df.columns:
                df['validation_qty'] = df['5PRS_Inspection_Qty'].fillna(0)
            else:
                df['validation_qty'] = 0

            print(f"   - 직원 with 5PRS inspection data: {(df['validation_qty'] > 0).sum()}직원")
            print(f"   - 5PRS pass rate >= 95%: {(df['pass_rate'] >= 95).sum()}직원")
            
            # 출근 관련 column - Excel data를 그대로 use (하드코딩 제거)
            # Excel이 단th 진실 소스(Single Source of Truth)
            missing_columns = []

            if '출근율_Attendance_Rate_Percent' not in df.columns:
                missing_columns.append('출근율_Attendance_Rate_Percent')
                # attendance_rate를 actual data로 calculation
                if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
                    df['출근율_Attendance_Rate_Percent'] = (df['Actual Working Days'] / df['Total Working Days'] * 100).fillna(0)
                    df.loc[df['Total Working Days'] == 0, '출근율_Attendance_Rate_Percent'] = 0
                else:
                    df['출근율_Attendance_Rate_Percent'] = 0  # data 없음을 직원시적으로 표시
            # Check for column variations and normalize
            if 'actual_working_days' not in df.columns:
                if 'Actual Working Days' in df.columns:
                    df['actual_working_days'] = df['Actual Working Days']
                else:
                    missing_columns.append('actual_working_days')
                    df['actual_working_days'] = 0  # data 없음을 직원시적으로 표시

            if 'unapproved_absences' not in df.columns:
                if 'Unapproved Absences' in df.columns:
                    df['unapproved_absences'] = df['Unapproved Absences']
                else:
                    missing_columns.append('unapproved_absences')
                    df['unapproved_absences'] = 0  # data 없음을 직원시적으로 표시

            if 'absence_rate' not in df.columns:
                if '결근율_Absence_Rate_Percent' in df.columns:
                    df['absence_rate'] = df['결근율_Absence_Rate_Percent']
                else:
                    missing_columns.append('absence_rate')
                    df['absence_rate'] = 0  # data 없음을 직원시적으로 표시

            # Previous_Incentive column 매핑 추가
            if 'previous_incentive' not in df.columns:
                if 'Previous_Incentive' in df.columns:
                    df['previous_incentive'] = df['Previous_Incentive']
                else:
                    df['previous_incentive'] = 0  # data 없음

            # AQL 통계 column 매핑 추가
            if 'AQL_Total_Tests' not in df.columns:
                df['AQL_Total_Tests'] = df.get('AQL_Total_Tests', 0)
            if 'AQL_Pass_Count' not in df.columns:
                df['AQL_Pass_Count'] = df.get('AQL_Pass_Count', 0)
            if 'AQL_Fail_Percent' not in df.columns:
                df['AQL_Fail_Percent'] = df.get('AQL_Fail_Percent', 0)

            if missing_columns:
                print(f"⚠️ Missing attendance-related columns: {missing_columns}")
                print("   → Please check data in Excel. Will be displayed as 0 without hardcoding.")
            
            # 이전 달 incentive load
            month_names = ['', 'january', 'february', 'march', 'april', 'may', 'june',
                          'july', 'august', 'september', 'october', 'november', 'december']
            month_map = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }

            current_month_num = month_map.get(month.lower(), 8)
            if current_month_num == 1:
                prev_month_name = 'december'
                prev_year = year - 1
            else:
                prev_month_name = month_names[current_month_num - 1]
                prev_year = year

            print(f"✅ Previous month calculation: {month} → {prev_month_name}")
            
            # 모든 직원의 July incentive는 JSON 설정 file에서 load
            july_incentive_data = {}
            if month.lower() == 'august' and os.path.exists("config_files/july_incentive_all_직원.json"):
                try:
                    with open("config_files/july_incentive_all_직원.json", 'r', encoding='utf-8') as f:
                        july_data = json.load(f)
                        # JSON에서 모든 직원의 July incentive 정보 추출
                        for emp_id, emp_info in july_data.get('직원', {}).items():
                            july_incentive_data[emp_id] = emp_info.get('july_incentive', 0)
                        print(f"✅ July Incentive JSON configuration loaded: {len(july_incentive_data)}employee data")
                except Exception as e:
                    print(f"⚠️ JSON configuration file load failed: {e}")
            
            # Single Source of Truth: Excel의 Previous_Incentive column use
            # Previous month incentive는 Excel file에 이미 포함되어 있음
            # column 이름이 이미 'previous_incentive'로 변경되었으므로 이를 확인
            if 'previous_incentive' in df.columns:
                # previous_incentive column을 prev_month_incentive로 매핑
                df[f'{prev_month_name}_incentive'] = df['previous_incentive'].fillna(0).astype(str)
                print(f"✅ Using Previous_Incentive column from Excel (Single Source of Truth)")

                # actual data가 있는 직원 count 확인
                non_zero_count = (pd.to_numeric(df['previous_incentive'], errors='coerce') > 0).sum()
                total_amount = pd.to_numeric(df['previous_incentive'], errors='coerce').sum()
                print(f"   - {prev_month_name} incentive: {non_zero_count}직원, total {total_amount:,.0f} VND")
            else:
                # Previous_Incentive column이 없는 경우 (이전 version Excel)
                print(f"⚠️ Previous_Incentive column not found in Excel.")
                df[f'{prev_month_name}_incentive'] = '0'
            
            # 다른 month incentive도 default value 설정
            df['june_incentive'] = df.get('june_incentive', '0')
            df['july_incentive'] = df.get('july_incentive', '0')
            
            # 모든 직원의 July incentive를 JSON 설정에서 덮어쓰기
            if july_incentive_data and month.lower() == 'august':
                updated_count = 0
                for idx, row in df.iterrows():
                    emp_id = str(row['emp_no'])
                    if emp_id in july_incentive_data:
                        df.at[idx, 'july_incentive'] = str(july_incentive_data[emp_id])
                        updated_count += 1
                print(f"✅ July incentive JSON configuration applied successfully: {updated_count}직원 updated")
            
            # 입사th 및 퇴사th 필터링 (corresponding month 기준)
            print(f"✅ Filtering employee data...")

            # corresponding month의 날짜 range calculation
            month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                           'july', 'august', 'september', 'october', 'november', 'december']
            month_num = month_names.index(month.lower()) + 1
            month_start = pd.to_datetime(f'{year}-{month_num:02d}-01')

            # 다음 달 1일 calculation (month말 calculation용)
            import calendar
            last_day = calendar.monthrange(year, month_num)[1]
            month_end = pd.to_datetime(f'{year}-{month_num:02d}-{last_day}')

            initial_count = len(df)

            # 1. 퇴사th 필터링 (corresponding month 1일 resigned before 제외)
            if 'Stop working Date' in df.columns:
                df['resignation_date'] = pd.to_datetime(df['Stop working Date'], errors='coerce')
                before_month = df[df['resignation_date'] < month_start]
                df = df[(df['resignation_date'] >= month_start) | (df['resignation_date'].isna())]

                if len(before_month) > 0:
                    print(f"   - {get_korean_month(month)} resigned before {len(before_month)}직원 excluded")

            # 2. 입사th 필터링 (corresponding month 이후 입사자 제외)
            if 'Entrance Date' in df.columns:
                df['entrance_date'] = pd.to_datetime(df['Entrance Date'], errors='coerce')
                after_month = df[df['entrance_date'] > month_end]
                df = df[(df['entrance_date'] <= month_end) | (df['entrance_date'].isna())]

                if len(after_month) > 0:
                    print(f"   - {get_korean_month(month)} future hires after {len(after_month)}직원 excluded")

            print(f"   - {get_korean_month(month)} incentive eligible: {len(df)}직원 (total {initial_count}out of)")
            
            print(f"✅ {len(df)}명 직원 데이터 로드 완료 ({get_korean_month(month)} 기준)")
            return df
            
    print("❌ incentive data file not found")
    return pd.DataFrame()

def load_condition_matrix():
    """조건 매트릭스 JSON file load"""
    try:
        with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        print("⚠️ Condition matrix file not found. Using default configuration")
        return None

def load_area_mapping():
    """담당구역 매핑 JSON file load"""
    try:
        with open('config_files/auditor_trainer_area_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        print("⚠️ Area assignment mapping file not found.")
        return None

def get_applicable_conditions(position, type_name, condition_matrix):
    """직급과 type에 따른 apply 조건 fetch"""
    if not condition_matrix:
        # default value
        return [1, 2, 3, 4]  # 출근 조건만
    
    position_upper = str(position).upper()
    type_matrix = condition_matrix.get('position_matrix', {}).get(type_name, {})
    
    # 특정 직급 패턴 확인
    for pos_key, pos_config in type_matrix.items():
        if pos_key == 'default':
            continue
        patterns = pos_config.get('patterns', [])
        for pattern in patterns:
            if pattern in position_upper:
                return pos_config.get('applicable_conditions', [1, 2, 3, 4])
    
    # default value 반환
    return type_matrix.get('default', {}).get('applicable_conditions', [1, 2, 3, 4])

def evaluate_conditions(emp_data, condition_matrix):
    """직원 data에 대한 조건 평가 - Excel data 우선 use"""
    if not condition_matrix:
        return []

    conditions = condition_matrix.get('conditions', {})
    type_name = emp_data.get('type', 'TYPE-2')

    # TYPE-3: 모든 조건 N/A
    if type_name == 'TYPE-3':
        return [create_na_result(cond_id, conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}'))
                for cond_id in range(1, 11)]

    results = []

    # corresponding 직급/type에 apply되는 조건 목록 fetch (CRITICAL FIX)
    applicable = get_applicable_conditions(emp_data.get('position', ''), type_name, condition_matrix)

    # Excel에서 조건 결과 fetch (있으면 use, 없으면 자체 calculation)
    # CRITICAL FIX: Match exact CSV column names
    condition_names = [
        'attendance_rate', 'unapproved_absence', 'actual_working_days', 'minimum_days',
        'aql_personal_failure', 'aql_continuous', 'aql_team_area', 'area_reject',
        '5prs_pass_rate', '5prs_inspection_qty'
    ]

    for cond_id in range(1, 11):
        cond_col = f'cond_{cond_id}_{condition_names[cond_id-1]}'

        # 먼저 apply available 조건인지 확인 (CRITICAL FIX)
        if cond_id not in applicable:
            # excluded_conditions에 있는 조건은 Excel 결과와 관계without N/A
            results.append(create_na_result(cond_id, conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}')))
            continue

        # Excel에 조건 평가 결과가 있으면 use
        if cond_col in emp_data:
            excel_result = emp_data.get(cond_col, 'N/A')

            # CRITICAL FIX: NOT_APPLICABLE인 조건은 N/A로 처리
            if excel_result == 'NOT_APPLICABLE':
                results.append(create_na_result(cond_id, conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}')))
                continue

            value_col = f'cond_{cond_id}_value'
            value = emp_data.get(value_col, '')

            # CRITICAL FIX: value가 not exist or 의미없는 텍스트면 actual data 필드에서 fetch
            # FAIL/Fail/[FAIL] 같은 텍스트도 actual data로 교체
            # 주의: 0, 0.0 같은 숫자는 falsy지만 유효한 값이므로 is None으로 체크
            if value is None or value == '' or (isinstance(value, str) and str(value).upper() in ['FAIL', '[FAIL]', 'PASS', '[PASS]']):
                value_mappings = {
                    1: ('Attendance Rate', '%'),
                    2: ('Unapproved Absences', 'th'),
                    3: ('Actual Working Days', 'th'),
                    4: ('Actual Working Days', 'th'),
                    5: ('personal_aql_failure', 'cases'),
                    6: (None, None),  # 연속 failed는 PASS/FAIL만
                    7: (None, None),  # 팀 AQL은 PASS/FAIL만
                    8: ('area_reject_rate', '%'),
                    9: ('pass_rate', '%'),
                    10: ('validation_qty', '족')
                }

                if cond_id in value_mappings and value_mappings[cond_id][0]:
                    field_name, unit = value_mappings[cond_id]
                    raw_value = emp_data.get(field_name)
                    if raw_value is not None and raw_value != '':
                        # 숫자 포맷팅 (소count점은 첫째자리까지)
                        try:
                            num_value = float(raw_value)
                            if cond_id in [1, 8, 9]:  # 퍼센트인 경우
                                value = f"{num_value:.1f}{unit}"
                            else:  # thcount, casescount, 족count
                                value = f"{int(num_value)}{unit}"
                        except (ValueError, TypeError):
                            value = str(raw_value)

            # CRITICAL FIX: Excel의 값이 숫자만 있고 단위가 없는 경우 단위 추가
            # 예: "0.0" → "0.0%", "3" → "3일", "400" → "400족"
            elif cond_id in [1, 2, 3, 4, 5, 8, 9, 10]:
                # 조건 6, 7은 제외 (PASS/NO/YES 등 상태값)
                unit_map = {
                    1: '%', 2: 'th', 3: 'th', 4: 'th', 5: 'cases',
                    8: '%', 9: '%', 10: '족'
                }

                # value가 숫자만 있고 단위가 없으면 단위 추가
                try:
                    if isinstance(value, (int, float)):
                        # value가 숫자형이면 단위 추가
                        if cond_id in [1, 8, 9]:  # 퍼센트
                            value = f"{float(value):.1f}{unit_map[cond_id]}"
                        else:  # th, cases, 족
                            value = f"{int(value)}{unit_map[cond_id]}"
                    elif isinstance(value, str):
                        # string이지만 숫자로만 구성되어 있고 단위가 없으면 단위 추가
                        if value and not any(unit in str(value) for unit in ['%', 'th', 'cases', '족', 'PASS', 'FAIL', 'YES', 'NO']):
                            num_value = float(value)
                            if cond_id in [1, 8, 9]:  # 퍼센트
                                value = f"{num_value:.1f}{unit_map[cond_id]}"
                            else:  # th, cases, 족
                                value = f"{int(num_value)}{unit_map[cond_id]}"
                except (ValueError, TypeError):
                    # conversion failed시 원래 값 유지
                    pass

            if excel_result == 'PASS':
                # 조건by로 적절한 표시 값 설정
                if cond_id == 7:  # 팀/구역 AQL
                    actual_display = '[PASS]' if value == 'NO' or value is None or value == '' else str(value)
                elif cond_id == 6:  # 연속 failed
                    actual_display = '[PASS]' if value is None or value == '' else str(value)
                else:
                    # 0, 0.0 같은 falsy 값도 유효한 data이므로 None과 빈string만 체크
                    actual_display = str(value) if (value is not None and value != '') else '[PASS]'

                results.append({
                    'id': cond_id,
                    'name': conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}'),
                    'is_met': True,
                    'actual': actual_display,
                    'is_na': False
                })
            elif excel_result == 'FAIL':
                # 조건by로 적절한 표시 값 설정
                if cond_id == 7:  # 팀/구역 AQL
                    if value == 'YES':
                        actual_display = '[CONSECUTIVE_FAIL]'
                    elif value is not None and value != '':
                        actual_display = str(value)
                    else:
                        actual_display = '[FAIL]'
                elif cond_id == 6:  # 연속 failed
                    actual_display = '[CONSECUTIVE_FAIL]' if (value is None or value == '') else str(value)
                else:
                    # 0, 0.0 같은 falsy 값도 유효한 data이므로 None과 빈string만 체크
                    actual_display = str(value) if (value is not None and value != '') else '[FAIL]'

                results.append({
                    'id': cond_id,
                    'name': conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}'),
                    'is_met': False,
                    'actual': actual_display,
                    'is_na': False
                })
            else:  # N/A
                results.append(create_na_result(cond_id, conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}')))
        else:
            # Excel에 없으면 existing 자체 calculation logic use (fallback)
            # applicable은 이미 Line 517에서 가져옴

            # 조건 평가 함count 매핑 (existing logic 유지)
            evaluators = {
                1: lambda d: (d.get('출근율_Attendance_Rate_Percent', 0) >= 88, f"{d.get('출근율_Attendance_Rate_Percent', 0):.1f}%"),
                2: lambda d: (d.get('unapproved_absences', 0) <= 2, f"{d.get('unapproved_absences', 0)}th"),
                3: lambda d: (d.get('actual_working_days', 0) > 0, f"{d.get('actual_working_days', 0)}th"),
                4: lambda d: (d.get('actual_working_days', 0) >= 12, f"{d.get('actual_working_days', 0)}th"),
                5: lambda d: (d.get('aql_failures', 0) == 0, f"{d.get('aql_failures', 0)}cases"),
                6: lambda d: (d.get('continuous_fail', 'NO') != 'YES', '[PASS]' if d.get('continuous_fail', 'NO') != 'YES' else '[FAIL]'),
                7: lambda d: (d.get('area_consecutive_fail', 'NO') != 'YES', '[PASS]' if d.get('area_consecutive_fail', 'NO') != 'YES' else '[CONSECUTIVE_FAIL]'),
                8: lambda d: evaluate_area_reject(d),
                9: lambda d: (d.get('pass_rate', 0) >= 95, f"{d.get('pass_rate', 0):.1f}%"),
                10: lambda d: (d.get('validation_qty', 0) >= 100, f"{d.get('validation_qty', 0)}족")
            }

            # applicable 체크는 이미 Line 530-533에서 count행됨 (중복 제거)
            is_met, actual = evaluators[cond_id](emp_data)
            results.append({
                'id': cond_id,
                'name': conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}'),
                'is_met': is_met,
                'actual': actual,
                'is_na': False
            })

    return results

def create_na_result(cond_id, cond_name):
    """N/A 결과 creation 헬퍼"""
    return {
        'id': cond_id,
        'name': cond_name,
        'is_met': False,
        'actual': 'N/A',
        'is_na': True
    }

def evaluate_area_reject(emp_data):
    """조건 8 평가 헬퍼"""
    rate = float(emp_data.get('area_reject_rate', 0))
    if rate > 0:
        return rate < 3.0, f"{rate:.1f}%"
    return True, '0.0%'

# Single Source of Truth: 함count들은 더 이상 필요하지 않음
# Excel에서 모든 data가 처리되므로 Dashboard는 read만 함
'''
def check_consecutive_failures(month, year, group_col, data_path, is_employee=False):
    pass

def calculate_employee_area_stats(emp_no_str, area_mapping, building_stats,
                                building_consecutive_fail, total_reject_rate, aql_df):
    pass
'''

def generate_dashboard_html(df, month='august', year=2025, month_num=8, working_days=13, excel_dashboard_data=None, config_last_updated=""):
    """dashboard_version4.html과 완전히 동th한 dashboard creation - Excel data based"""

    # Load progression table from JSON (Single Source of Truth)
    progression_table = {}
    try:
        with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
            position_config = json.load(f)
            prog_table_str = position_config['incentive_progression']['TYPE_1_PROGRESSIVE']['progression_table']
            progression_table = {int(k): int(v) for k, v in prog_table_str.items()}
            print(f"✅ Progression table loaded from JSON: {len(progression_table)} months")
    except Exception as e:
        print(f"⚠️ Failed to load progression table from JSON: {e}")
        # Fallback to hardcoded values (should not happen)
        progression_table = {
            1: 150000, 2: 250000, 3: 300000, 4: 350000, 5: 400000,
            6: 450000, 7: 500000, 8: 650000, 9: 750000, 10: 850000,
            11: 950000, 12: 1000000
        }

    # 요일 배열 생성 (실제 달력 기준)
    import calendar
    # calendar.monthrange(year, month) returns (weekday of first day, number of days)
    # weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
    first_weekday, days_in_month = calendar.monthrange(year, month_num)

    # JavaScript 배열 생성: [요일index for day 1, 2, 3, ...]
    # weekday index를 JavaScript에서 사용하는 형식으로 변환
    # Python calendar: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    # JavaScript weekdays: [일(Sun), 월(Mon), 화(Tue), 수(Wed), 목(Thu), 금(Fri), 토(Sat)]
    # 변환 공식: js_index = (python_weekday + 1) % 7
    weekdays_indices = []
    for day in range(1, days_in_month + 1):
        # Python weekday index for this day
        python_weekday = (first_weekday + day - 1) % 7
        # Convert to JavaScript array index (Sunday-based)
        js_weekday_index = (python_weekday + 1) % 7
        weekdays_indices.append(js_weekday_index)

    # JavaScript 배열 문자열로 변환
    weekdays_array_js = str(weekdays_indices)
    print(f"📅 Weekdays array for {year}-{month_num:02d}: {weekdays_array_js}")

    # AQL 통계는 이제 Excel file에서 directly 가져옴 (Single Source of Truth)
    print("📊 AQL statistics used directly from Excel file (Single Source of Truth)")

    # AQL file directly load하여 inspectors 통계 calculation
    aql_inspector_stats = {}
    try:
        month_upper = month.upper()
        aql_file = f"input_files/AQL history/1.HSRG AQL REPORT-{month_upper}.{year}.csv"
        if os.path.exists(aql_file):
            aql_df = pd.read_csv(aql_file)
            # 모든 PO TYPE use (NORMAL PO + FAIL PO 등 total)
            # FAIL은 주로 FAIL PO에 있으므로 total를 봐야 정확함
            all_po_df = aql_df.copy()

            # Buildingby 검사 casescount 및 inspectors 통계 calculation
            aql_file_stats = {}  # 검사 casescount 기준 통계 (Table 1용)

            for building in ['A', 'B', 'B3', 'C', 'D']:
                building_df = all_po_df[all_po_df['BUILDING'] == building]
                if len(building_df) == 0:
                    continue

                # Table 1: 검사 casescount 기준 통계
                total_tests = len(building_df)
                pass_count = len(building_df[building_df['RESULT'] == 'PASS'])
                fail_count = total_tests - pass_count
                test_reject_rate = (fail_count / total_tests * 100) if total_tests > 0 else 0

                aql_file_stats[f'Building {building}'] = {
                    'total': total_tests,
                    'pass': pass_count,
                    'fail': fail_count,
                    'rejectRate': round(test_reject_rate, 1)
                }

                # Table 2: inspectors 인원 기준 통계
                inspector_results = {}
                for emp_no in building_df['EMPLOYEE NO'].unique():
                    emp_tests = building_df[building_df['EMPLOYEE NO'] == emp_no]
                    has_fail = (emp_tests['RESULT'] == 'FAIL').any()
                    inspector_results[emp_no] = has_fail

                total_inspectors = len(inspector_results)
                reject_inspectors = sum(1 for has_fail in inspector_results.values() if has_fail)
                pass_only_inspectors = total_inspectors - reject_inspectors
                inspector_reject_rate = (reject_inspectors / total_inspectors * 100) if total_inspectors > 0 else 0

                aql_inspector_stats[f'Building {building}'] = {
                    'totalInspectors': total_inspectors,
                    'rejectInspectors': reject_inspectors,
                    'passOnlyInspectors': pass_only_inspectors,
                    'rejectRate': f'{inspector_reject_rate:.1f}',
                    'totalTests': total_tests
                }

            # total 통계 (검사 casescount 기준)
            total_tests_all = len(all_po_df)
            pass_count_all = len(all_po_df[all_po_df['RESULT'] == 'PASS'])
            fail_count_all = total_tests_all - pass_count_all
            test_reject_rate_all = (fail_count_all / total_tests_all * 100) if total_tests_all > 0 else 0

            aql_file_stats['total'] = {
                'total': total_tests_all,
                'pass': pass_count_all,
                'fail': fail_count_all,
                'rejectRate': round(test_reject_rate_all, 1)
            }

            # total 통계 (inspectors 인원 기준)
            all_inspector_results = {}
            for emp_no in all_po_df['EMPLOYEE NO'].unique():
                emp_tests = all_po_df[all_po_df['EMPLOYEE NO'] == emp_no]
                has_fail = (emp_tests['RESULT'] == 'FAIL').any()
                all_inspector_results[emp_no] = has_fail

            total_all = len(all_inspector_results)
            reject_all = sum(1 for has_fail in all_inspector_results.values() if has_fail)
            pass_all = total_all - reject_all
            reject_rate_all = (reject_all / total_all * 100) if total_all > 0 else 0

            aql_inspector_stats['total'] = {
                'totalInspectors': total_all,
                'rejectInspectors': reject_all,
                'passOnlyInspectors': pass_all,
                'rejectRate': f'{reject_rate_all:.1f}',
                'totalTests': total_tests_all
            }

            print(f"✅ Inspector statistics calculation from AQL file completed: {total_all}직원 (with Rejects {reject_all}직원), {total_tests_all}cases")
            print(f"   - Inspection count Reject Rate: {test_reject_rate_all:.1f}% (Fail {fail_count_all}/{total_tests_all})")
            print(f"   - Inspector headcount Reject Rate: {reject_rate_all:.1f}% (with Rejects {reject_all}/{total_all}직원)")
        else:
            print(f"⚠️ AQL file not found: {aql_file}")
    except Exception as e:
        print(f"❌ AQL file load failed: {e}")
        import traceback
        traceback.print_exc()

    # Previous month calculation
    month_map = {
        'january': 0, 'february': 1, 'march': 2, 'april': 3,
        'may': 4, 'june': 5, 'july': 6, 'august': 7,
        'september': 8, 'october': 9, 'november': 10, 'december': 11
    }
    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']

    # 한국어 month 이름 매핑
    month_kor_map = {
        'january': '1month', 'february': '2month', 'march': '3month', 'april': '4month',
        'may': '5month', 'june': '6month', 'july': 'July', 'august': '8month',
        'september': '9month', 'october': '10month', 'november': '11month', 'december': '12month'
    }
    month_kor = month_kor_map.get(month.lower(), f'{month_num}month')

    current_month_num = month_map.get(month.lower(), 7)
    prev_month_name = month_names[current_month_num - 1] if current_month_num > 0 else 'december'
    prev_year = year if current_month_num > 0 else year - 1

    # 조건 매트릭스 load
    condition_matrix = load_condition_matrix()

    # metadata file load
    metadata = {}
    metadata_file = f"output_files/output_QIP_incentive_{month}_{year}_metadata.json"
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            print(f"✅ Metadata loaded successfully: {metadata_file}")
    else:
        print(f"⚠️ Metadata file not found: {metadata_file}")

    # Basic manpower data load하여 보스 정보 보완
    basic_df = None
    basic_file = f'input_files/basic manpower data {month}.csv'
    if os.path.exists(basic_file):
        try:
            basic_df = pd.read_csv(basic_file, encoding='utf-8-sig')
            # data 정리
            basic_df = basic_df.dropna(subset=['Employee No', 'Full Name'], how='all')
            basic_df = basic_df[basic_df['Employee No'].notna()]

            # Employee No를 정count로 conversion 후 string로 (소count점 제거)
            basic_df['Employee No'] = basic_df['Employee No'].apply(lambda x: str(int(float(x))) if pd.notna(x) and x != '' else '')

            # MST direct boss name도 동th하게 처리
            basic_df['MST direct boss name'] = basic_df['MST direct boss name'].apply(
                lambda x: str(int(float(x))) if pd.notna(x) and x != '' and x != 0 else ''
            )

            print(f"✅ Basic manpower data loaded successfully: {len(basic_df)} 직원")
        except Exception as e:
            print(f"⚠️ Basic manpower data load failed: {e}")

    # data 준비
    # Single Source of Truth를 위해 excel_dashboard_data를 use (df 대신)
    if excel_dashboard_data and 'employee_data' in excel_dashboard_data:
        # from excel_dashboard_data directly 직원 creation
        직원 = []
        # 퇴사th 필터링을 위한 month startth 설정
        month_start = datetime(year, month_num, 1)

        for emp_data in excel_dashboard_data['employee_data']:
            # 퇴사th 필터링 (corresponding month 1일 resigned before 제외)
            if 'Stop working Date' in emp_data and emp_data['Stop working Date']:
                try:
                    resignation_date = pd.to_datetime(emp_data['Stop working Date'], errors='coerce')
                    if pd.notna(resignation_date) and resignation_date < month_start:
                        # corresponding month resigned before는 제외
                        continue
                except:
                    pass  # 날짜 conversion failed 시 포함

            # 필드직원 매핑 (excel_dashboard_data는 CSV column직원 use)
            emp = emp_data.copy()
            # type 필드 추가 (ROLE TYPE STD에서 가져옴)
            emp['type'] = emp.get('ROLE TYPE STD', 'TYPE-2')

            emp['emp_no'] = str(emp.get('Employee No', ''))
            emp['name'] = emp.get('Full Name', '')
            emp['position'] = emp.get('QIP POSITION 1ST  NAME', '')

            # CRITICAL FIX: JavaScript needs POSITION CODE (not name) for filtering
            # JavaScript checks: ['A1A', 'A1B', 'A1C'].includes(positionCode)
            # This field MUST be preserved for 5PRS modal filtering
            emp['position_code'] = emp.get('FINAL QIP POSITION NAME CODE', '')

            # incentive 필드 매핑 (동적 month 기반)
            # Current month incentive (e.g., october_incentive for October report)
            # Try month-specific column first (e.g., October_Incentive), then fallback to 'Final Incentive amount'
            month_col = f'{month.capitalize()}_Incentive'
            current_incentive = emp.get(month_col, emp.get('Final Incentive amount', '0'))
            emp[f'{month.lower()}_incentive'] = str(current_incentive if pd.notna(current_incentive) else '0')

            # Previous month incentive (e.g., september_incentive for October report)
            emp[f'{prev_month_name}_incentive'] = str(emp.get('Previous_Incentive', '0'))

            # Backward compatibility fields for JavaScript fallback chains
            emp['previous_incentive'] = str(emp.get('Previous_Incentive', '0'))

            # CRITICAL FIX: 5PRS 필드 추가 (JavaScript에서 use)
            emp['pass_rate'] = emp.get('5PRS_Pass_Rate', 0) if pd.notna(emp.get('5PRS_Pass_Rate')) else 0
            emp['validation_qty'] = emp.get('5PRS_Inspection_Qty', 0) if pd.notna(emp.get('5PRS_Inspection_Qty')) else 0

            # CRITICAL FIX: condition4 필드 추가 (JavaScript 호환성)
            emp['condition4'] = str(emp.get('attendancy condition 4 - minimum working days', 'no'))

            # CRITICAL FIX: condition_results 추가
            emp['condition_results'] = evaluate_conditions(emp, condition_matrix)

            직원.append(emp)
        print(f"✅ Single Source of Truth: from excel_dashboard_data {len(excel_dashboard_data['employee_data'])}out of active 직원 {len(직원)}직원 loaded (resigned {len(excel_dashboard_data['employee_data']) - len(직원)}직원 excluded)")
    else:
        # Fallback: existing 방식 (df use)
        직원 = []
        for _, row in df.iterrows():
            # Convert Series to dict
            row_dict = row.to_dict()

            # Employee No fetch
            emp_no = str(row_dict.get('emp_no', ''))

            # Basic manpower에서 보스 정보 fetch
            boss_id = ''
            boss_name = ''
            if basic_df is not None and emp_no:
                # emp_no에서 .0 제거 (혹시 있다면)
                emp_no_clean = emp_no.replace('.0', '') if '.0' in emp_no else emp_no
                basic_row = basic_df[basic_df['Employee No'] == emp_no_clean]
                if not basic_row.empty:
                    boss_id = str(basic_row['MST direct boss name'].iloc[0]) if pd.notna(basic_row['MST direct boss name'].iloc[0]) else ''
                    boss_name = str(basic_row['direct boss name'].iloc[0]) if pd.notna(basic_row['direct boss name'].iloc[0]) else ''
                    # nan, 0, 0.0, 빈 string 등을 빈 string로 처리
                    if boss_id in ['nan', '0', '0.0', '']:
                        boss_id = ''
                    if boss_name in ['nan', '0', '0.0', '']:
                        boss_name = ''

            emp = {
            'emp_no': emp_no,
            'employee_no': emp_no,  # JavaScript 호환성을 위한 중복 필드
            'Employee No': emp_no,  # CSV column직원과 th치
            'name': str(row_dict.get('name', '')),
            'full_name': str(row_dict.get('name', '')),  # JavaScript 호환성을 위한 중복 필드
            'Full Name': str(row_dict.get('name', '')),  # CSV column직원과 th치
            'position': str(row_dict.get('position', '')),
            'qip_position': str(row_dict.get('position', '')),  # JavaScript 호환성을 위한 중복 필드
            'QIP POSITION 1ST  NAME': str(row_dict.get('position', '')),  # CSV column직원과 th치
            'type': str(row_dict.get('type', 'TYPE-2')),
            'boss_id': boss_id,  # Basic manpower에서 가져온 상사 ID
            'boss_name': boss_name,  # Basic manpower에서 가져온 상사 이름
            'MST direct boss name': boss_id,  # JavaScript에서 찾는 Excel column직원
            'direct boss name': boss_name,  # JavaScript에서 찾는 Excel column직원
            # 동적 month incentive 매핑
            f'{month.lower()}_incentive': str(row_dict.get(f'{month.lower()}_incentive', '0')),  # 현재 month incentive
            f'{prev_month_name.lower()}_incentive': str(row_dict.get(f'{prev_month_name.lower()}_incentive', '0')),  # Previous month incentive
            # 호환성을 위해 추가
            'august_incentive': str(row_dict.get('august_incentive', '0')) if 'august_incentive' in row_dict else '0',
            'july_incentive': str(row_dict.get('july_incentive', '0')) if 'july_incentive' in row_dict else '0',
            'september_incentive': str(row_dict.get('september_incentive', '0')) if 'september_incentive' in row_dict else '0',
            'june_incentive': str(row_dict.get('june_incentive', '0')),
            '출근율_Attendance_Rate_Percent': float(row_dict.get('출근율_Attendance_Rate_Percent', 0) if pd.notna(row_dict.get('출근율_Attendance_Rate_Percent')) else 0),
            'actual_working_days': int(row_dict.get('actual_working_days', 0) if pd.notna(row_dict.get('actual_working_days')) else 0),
            'Actual Working Days': int(row_dict.get('actual_working_days', 0) if pd.notna(row_dict.get('actual_working_days')) else 0),  # JavaScript 호환성
            'unapproved_absences': int(row_dict.get('unapproved_absences', 0) if pd.notna(row_dict.get('unapproved_absences')) else 0),
            'Unapproved Absences': int(row_dict.get('unapproved_absences', 0) if pd.notna(row_dict.get('unapproved_absences')) else 0),  # JavaScript 호환성
            'absence_rate': float(row_dict.get('absence_rate', 0) if pd.notna(row_dict.get('absence_rate')) else 0),
            'condition1': str(row_dict.get('attendancy condition 1 - acctual working days is zero', 'no')),
            'condition2': str(row_dict.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'no')),
            'condition3': str(row_dict.get('attendancy condition 3 - absent % is over 12%', 'no')),
            'condition4': str(row_dict.get('attendancy condition 4 - minimum working days', 'no')),
            'aql_failures': int(row_dict.get('aql_failures', 0)),
            'continuous_fail': str(row_dict.get('continuous_fail', 'NO')),
            'area_reject_rate': float(row_dict.get('area_reject_rate', 0)),  # 값은 metadata에서 덮어씌워짐
            'area_consecutive_fail': str(row_dict.get('area_consecutive_fail', 'NO')),
            'pass_rate': float(row_dict.get('pass_rate', 0)),
            'validation_qty': int(row_dict.get('validation_qty', 0)),
            'Talent_Pool_Member': str(row_dict.get('Talent_Pool_Member', 'N')),
            'Talent_Pool_Bonus': int(row_dict.get('Talent_Pool_Bonus', 0)),
            # 퇴사일 추가 (2025-12-01): LINE LEADER 평균 계산에서 퇴사자 제외용
            'stop_date': str(row_dict.get('Stop working Date', '')) if pd.notna(row_dict.get('Stop working Date')) else '',
            'Stop working Date': str(row_dict.get('Stop working Date', '')) if pd.notna(row_dict.get('Stop working Date')) else ''
        }

        # 조건 관련 column 추가 (cond_1 ~ cond_10)
        for cond_id in range(1, 11):
            condition_names = [
                '출근율_Attendance_Rate_Percent', 'unapproved_absence', 'actual_working_days', 'minimum_days',
                'aql_personal_failure', 'aql_continuous', 'aql_team_area', 'area_reject',
                '5prs_pass_rate', '5prs_inspection_qty'
            ]
            cond_col = f'cond_{cond_id}_{condition_names[cond_id-1]}'
            value_col = f'cond_{cond_id}_value'
            threshold_col = f'cond_{cond_id}_threshold'

            # CSV에서 조건 평가 결과와 값 fetch
            if cond_col in row_dict:
                emp[cond_col] = row_dict[cond_col]
            if value_col in row_dict:
                emp[value_col] = row_dict[value_col]
                if threshold_col in row_dict:
                    emp[threshold_col] = row_dict[threshold_col]

            # metadata에서 area_reject_rate fetch
            emp_no = str(emp['emp_no']).zfill(9)
            if emp_no in metadata:
                emp_metadata = metadata[emp_no]
                if 'conditions' in emp_metadata and 'aql' in emp_metadata['conditions']:
                    if 'area_reject_rate' in emp_metadata['conditions']['aql']:
                        emp['area_reject_rate'] = float(emp_metadata['conditions']['aql']['area_reject_rate'].get('value', 0))

            # 조건 평가 결과 추가
            emp['condition_results'] = evaluate_conditions(emp, condition_matrix)

            # failed 사유 표시를 위한 조건 필드 추가 - CSV에서 directly fetch
            emp['attendancy condition 1 - acctual working days is zero'] = str(row_dict.get('attendancy condition 1 - acctual working days is zero', 'no'))
            emp['attendancy condition 2 - unapproved Absence Day is more than 2 days'] = str(row_dict.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'no'))
            emp['attendancy condition 3 - absent % is over 12%'] = str(row_dict.get('attendancy condition 3 - absent % is over 12%', 'no'))
            emp['attendancy condition 4 - minimum working days'] = str(row_dict.get('attendancy condition 4 - minimum working days', 'no'))

            # AQL 조건 필드 추가 (현재 월 기준 동적 컬럼명 사용)
            aql_column_name = f'{month.capitalize()} AQL Failures'
            emp['aql condition 7 - team/area fail AQL'] = str(row_dict.get('aql condition 7 - team/area fail AQL', 'no'))
            emp[aql_column_name] = int(row_dict.get(aql_column_name, row_dict.get('aql_failures', 0)))
            emp['Continuous_FAIL'] = str(row_dict.get('Continuous_FAIL', row_dict.get('continuous_fail', 'NO')))
            emp['Continuous_FAIL_2Month'] = str(row_dict.get('Continuous_FAIL_2Month', 'NO'))  # 2개월 연속 실패 컬럼 추가
            emp['Consecutive_Fail_Months'] = int(row_dict.get('Consecutive_Fail_Months', 0))

            # 5PRS 조건 필드 추가
            emp['5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%'] = str(row_dict.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%', 'yes'))
            emp['5prs condition 2 - Total Valiation Qty is zero'] = str(row_dict.get('5prs condition 2 - Total Valiation Qty is zero', 'no'))

            # conditions_pass_rate 필드 추가
            emp['conditions_pass_rate'] = float(row_dict.get('conditions_pass_rate', 0))
            emp['conditions_passed'] = int(row_dict.get('conditions_passed', 0))
            emp['conditions_applicable'] = int(row_dict.get('conditions_applicable', 0))

            # Working Days 필드 추가
            emp['Working Days'] = int(row_dict.get('actual_working_days', 0))

            # AQL 통계 필드 추가 (Excel에서 가져온 actual data)
            emp['AQL_Total_Tests'] = int(row_dict.get('AQL_Total_Tests', 0))
            emp['AQL_Pass_Count'] = int(row_dict.get('AQL_Pass_Count', 0))
            emp['AQL_Fail_Percent'] = float(row_dict.get('AQL_Fail_Percent', 0))

            직원.append(emp)
    
    # 통계 calculation
    total_직원 = len(직원)
    # 현재 month incentive 필드 이름
    current_month_field = f'{month.lower()}_incentive'
    paid_직원 = sum(1 for e in 직원 if int(float(e.get(current_month_field, '0') or '0')) > 0)
    total_amount = sum(int(float(e.get(current_month_field, '0') or '0')) for e in 직원)
    지급_rate = (paid_직원 / total_직원 * 100) if total_직원 > 0 else 0
    
    # Typeby 통계
    type_stats = {}
    for emp in 직원:
        emp_type = emp['type']
        if emp_type not in type_stats:
            type_stats[emp_type] = {
                'total': 0,
                'paid': 0,
                'amount': 0,
                'paid_amounts': []
            }
        type_stats[emp_type]['total'] += 1
        amount = int(float(emp.get(current_month_field, '0') or '0'))
        if amount > 0:
            type_stats[emp_type]['paid'] += 1
            type_stats[emp_type]['amount'] += amount
            type_stats[emp_type]['paid_amounts'].append(amount)
    
    # 직원 data JSON - NaN 값을 null로 conversion
    import math
    def convert_nan(obj):
        """Convert NaN values to null for JSON"""
        if isinstance(obj, float) and math.isnan(obj):
            return None
        elif isinstance(obj, dict):
            return {k: convert_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_nan(item) for item in obj]
        # Convert any string that might have special characters
        elif isinstance(obj, str):
            # Remove any control characters and ensure proper escaping
            return obj.replace('\r', '').replace('\n', ' ').replace('\t', ' ')
        return obj

    # Clean up field names with double spaces
    for emp in 직원:
        # Create new dict with cleaned keys
        cleaned_emp = {}
        for key, value in emp.items():
            # Replace double spaces with single space in keys
            clean_key = ' '.join(key.split()) if isinstance(key, str) else key
            cleaned_emp[clean_key] = value
        # Update the employee record
        emp.clear()
        emp.update(cleaned_emp)

    직원_clean = convert_nan(직원)
    # Use base64 encoding for safe JavaScript embedding
    직원_json_str = json.dumps(직원_clean, ensure_ascii=False, separators=(',', ':'))
    직원_json_base64 = base64.b64encode(직원_json_str.encode('utf-8')).decode('ascii')

    # AQL Inspector Stats를 Base64로 encoding
    aql_inspector_stats_str = json.dumps(aql_inspector_stats, ensure_ascii=False, separators=(',', ':'))
    aql_inspector_stats_b64 = base64.b64encode(aql_inspector_stats_str.encode('utf-8')).decode('ascii')

    # AQL File Stats (검사 casescount 기준)를 Base64로 encoding
    aql_file_stats_str = json.dumps(aql_file_stats if 'aql_file_stats' in locals() else {}, ensure_ascii=False, separators=(',', ':'))
    aql_file_stats_b64 = base64.b64encode(aql_file_stats_str.encode('utf-8')).decode('ascii')

    # AQL Inspector 인센티브 Config 로드 (Part 1/2/3 breakdown 표시용)
    try:
        aql_incentive_config_path = os.path.join('config_files', 'aql_inspector_incentive_config.json')
        with open(aql_incentive_config_path, 'r', encoding='utf-8') as f:
            aql_incentive_config = json.load(f)
        aql_incentive_config_str = json.dumps(aql_incentive_config, ensure_ascii=False, separators=(',', ':'))
        aql_incentive_config_b64 = base64.b64encode(aql_incentive_config_str.encode('utf-8')).decode('ascii')
        print(f"✅ AQL Inspector incentive config loaded: {len(aql_incentive_config.get('aql_inspectors', {}))} inspectors")
    except Exception as e:
        print(f"⚠️ Failed to load aql_inspector_incentive_config.json: {e}")
        aql_incentive_config_b64 = base64.b64encode('{"aql_inspectors":{}}'.encode('utf-8')).decode('ascii')

    # Auditor/Trainer Area Mapping JSON load and encode to Base64
    try:
        auditor_mapping_path = os.path.join('config_files', 'auditor_trainer_area_mapping.json')
        with open(auditor_mapping_path, 'r', encoding='utf-8') as f:
            auditor_area_mapping = json.load(f)
        auditor_mapping_str = json.dumps(auditor_area_mapping, ensure_ascii=False, separators=(',', ':'))
        auditor_mapping_b64 = base64.b64encode(auditor_mapping_str.encode('utf-8')).decode('ascii')
        print(f"✅ Auditor/Trainer area mapping loaded: {len(auditor_area_mapping.get('auditor_trainer_areas', {}))} auditors, {len(auditor_area_mapping.get('model_master', {}).get('employees', {}))} model masters")
    except Exception as e:
        print(f"⚠️ Failed to load auditor_trainer_area_mapping.json: {e}")
        auditor_mapping_b64 = base64.b64encode('{}}'.encode('utf-8')).decode('ascii')

    # Position matrix data load
    position_matrix = load_condition_matrix()
    position_matrix_json = json.dumps(position_matrix, ensure_ascii=False)

    # 현재 시간 - ISO 형식으로 저장
    current_datetime = datetime.now()
    current_date_iso = current_datetime.strftime('%Y-%m-%d %H:%M')
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day
    current_hour = current_datetime.hour
    current_minute = current_datetime.minute

    # Report type determination (중간 vs final)
    # 처리하는 월이 현재 월보다 이전이면 Final Report
    # 처리하는 월이 현재 월과 같고, 현재 날짜가 20일 미만이면 Interim Report
    if year < current_year or (year == current_year and month_num < current_month):
        # 이전 월/년도 데이터는 항상 Final Report
        is_interim_report = False
    elif year == current_year and month_num == current_month and current_day < 20:
        # 현재 월 데이터이고 20일 이전이면 Interim Report
        is_interim_report = True
    else:
        # 그 외는 Final Report (20일 이후 또는 미래 월)
        is_interim_report = False

    report_type_ko = '중간 점검용' if is_interim_report else 'final'
    report_type_en = 'Interim' if is_interim_report else 'Final'
    report_type_vi = 'Tạm thời' if is_interim_report else 'Cuối cùng'

    # corresponding month의 last 날 calculation
    import calendar
    # month_num is the actual month number passed from main
    month_last_day = calendar.monthrange(year, month_num)[1]

    # actual data range fetch
    try:
        from src.get_actual_data_range import get_all_data_ranges
        data_ranges = get_all_data_ranges(month, year)

        # 각 data typeby actual range
        att_min, att_max = data_ranges.get('attendance', (None, None))
        inc_min, inc_max = data_ranges.get('incentive', (None, None))
        aql_min, aql_max = data_ranges.get('aql', (None, None))
        prs_min, prs_max = data_ranges.get('5prs', (None, None))

        # 출근 data range 포맷팅
        if att_min is not None and att_max is not None:
            attendance_start_day = att_min.day
            attendance_end_day = att_max.day
            attendance_start_str = att_min.strftime('%d')
            attendance_end_str = att_max.strftime('%d')
        else:
            attendance_start_day = 1
            attendance_end_day = month_last_day
            attendance_start_str = '01'
            attendance_end_str = f'{month_last_day:02d}'

        # 5PRS data range 포맷팅
        if prs_min is not None and prs_max is not None:
            prs_start_day = prs_min.day
            prs_end_day = prs_max.day
            prs_start_str = prs_min.strftime('%d')
            prs_end_str = prs_max.strftime('%d')
        else:
            prs_start_day = 1
            prs_end_day = month_last_day
            prs_start_str = '01'
            prs_end_str = f'{month_last_day:02d}'

        # AQL data range 포맷팅
        if aql_min is not None and aql_max is not None:
            aql_start_str = aql_min.strftime('%d')
            aql_end_str = aql_max.strftime('%d')
        else:
            aql_start_str = '01'
            aql_end_str = f'{month_last_day:02d}'

        # incentive data range 포맷팅
        if inc_min is not None and inc_max is not None:
            incentive_start_str = inc_min.strftime('%d')
            incentive_end_str = inc_max.strftime('%d')
        else:
            # incentive 데이터가 없으면 attendance 데이터의 마지막 날 사용
            # (중간 보고서 판정을 위해 실제 데이터 범위 사용)
            if att_max is not None:
                incentive_start_str = '01'
                incentive_end_str = att_max.strftime('%d')
                print(f"  ℹ️ incentive data range not found - using attendance end day: {incentive_end_str}")
            else:
                incentive_start_str = '01'
                incentive_end_str = f'{month_last_day:02d}'

    except Exception as e:
        # 에러 발생 시 default value use (month total)
        print(f"⚠️ Failed to fetch actual data range: {e}")
        attendance_start_str = '01'
        attendance_end_str = f'{month_last_day:02d}'
        prs_start_str = '01'
        prs_end_str = f'{month_last_day:02d}'
        aql_start_str = '01'
        aql_end_str = f'{month_last_day:02d}'
        incentive_start_str = '01'
        incentive_end_str = f'{month_last_day:02d}'

    # report type 재determination (incentive data 기간 및 현재 날짜 기준)
    try:
        incentive_end_day = int(incentive_end_str)

        # 처리하는 월이 현재 월보다 이전이면 Final Report
        # 처리하는 월이 현재 월과 같고, 현재 날짜가 20일 미만이면 Interim Report
        # 데이터가 전체 월(20일 이상)을 포함하면 Final Report
        if year < current_year or (year == current_year and month_num < current_month):
            # 이전 월/년도 데이터는 항상 Final Report
            is_interim_report = False
        elif year == current_year and month_num == current_month and current_day < 20 and incentive_end_day < 20:
            # 현재 월 데이터이고, 현재 날짜와 데이터 종료일 모두 20일 미만이면 Interim Report
            is_interim_report = True
        else:
            # 그 외는 Final Report (20일 이후 데이터 포함 또는 이전 월)
            is_interim_report = False

        report_type_ko = '중간 점검용' if is_interim_report else 'final'
        report_type_en = 'Interim' if is_interim_report else 'Final'
        report_type_vi = 'Tạm thời' if is_interim_report else 'Cuối cùng'
        print(f"📊 Report type determination: data last day={incentive_end_day}th → {'interim report' if is_interim_report else 'final report'}")
    except ValueError:
        print(f"⚠️ incentive endth conversion failed, existing logic use: {incentive_end_str}")
        pass  # existing 값 유지 (current_day 기준)

    # JavaScript용 번역 data creation
    translations_js = json.dumps(TRANSLATIONS, ensure_ascii=False, indent=2)

    # Excel based dashboard data를 JavaScript용으로 준비
    # 큰 JSON data는 Base64로 encoding하여 파싱 오류 방지
    if excel_dashboard_data:
        excel_data_json = json.dumps(excel_dashboard_data, ensure_ascii=False)
        excel_data_b64 = base64.b64encode(excel_data_json.encode('utf-8')).decode('utf-8')
    else:
        excel_data_b64 = ''

    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- 검색엔진 차단 -->
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
    <meta name="googlebot" content="noindex, nofollow">
    <meta name="bingbot" content="noindex, nofollow">
    <title>QIP 인센티브 계산 결과 - {year}년 {get_korean_month(month)}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Google Fonts for better Unicode support -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Noto+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Bootstrap JavaScript Bundle with Popper (필count!) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    '''

    # 모달 함count들 추가 (template 방식으로 정의)
    modal_scripts = """
    function showTotalWorkingDaysDetails() {
        /* Excel data에서 actual 근무일 정보 fetch (Single Source of Truth) */
        let workDays = [];
        let holidays = [];
        let totalWorkingDays = __WORKING_DAYS__; /* Config에서 가져온 actual 값 */
        const daysInMonth = __DAYS_IN_MONTH__; /* Python에서 계산된 실제 월 일수 */

        if (window.excelDashboardData && window.excelDashboardData.attendance) {
            /* actual 출근 data에서 근무일과 휴th 추출 */
            const dailyData = window.excelDashboardData.attendance.daily_data;
            totalWorkingDays = window.excelDashboardData.attendance.total_working_days;

            /* thby data 분석 - total month range 확인 */
            for (let day = 1; day <= daysInMonth; day++) {
                if (dailyData && dailyData[day]) {
                    if (dailyData[day].is_working_day) {
                        workDays.push(day);
                    } else {
                        holidays.push(day);
                    }
                } else {
                    /* data가 없는 날은 휴th로 처리 */
                    holidays.push(day);
                }
            }
            console.log('actual 근무일:', workDays);
            console.log('휴th/data없음:', holidays);
            console.log('total 근무일count:', totalWorkingDays);
        } else {
            /* Fallback: 기본 근무일 data use */
            console.warn('Excel dashboard data가 not found. default value use.');
            workDays = [2,3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,26,27,30];
            holidays = [1,7,8,14,15,21,22,28,29];
        }

        /* 요th 번역 fetch */
        const weekdaysArray = getTranslation('workingDaysModal.weekdays', currentLanguage);
        const weekdaySuffix = getTranslation('workingDaysModal.weekdaySuffix', currentLanguage);
        const dayLabel = getTranslation('workingDaysModal.dayLabel', currentLanguage);
        const employeeCountLabel = getTranslation('workingDaysModal.employeeCount', currentLanguage);
        const noDataText = getTranslation('workingDaysModal.noData', currentLanguage);

        /* Python에서 계산된 실제 요일 배열 (각 날짜의 요일 index) */
        const weekdaysIndices = __WEEKDAYS_ARRAY__;

        const getWeekday = (day) => {
            /* Python에서 전달받은 실제 요일 index 사용 (day는 1부터 시작) */
            const dayIndex = weekdaysIndices[day - 1];
            return weekdaysArray[dayIndex];
        };

        let calendarHTML = '<div class="calendar-grid">';
        for (let day = 1; day <= daysInMonth; day++) {
            const isWorkDay = workDays.includes(day);
            const hasNoData = !isWorkDay;
            const dayClass = isWorkDay ? 'work-day' : 'no-data';
            const icon = isWorkDay ? '💼' : '';
            const weekday = getWeekday(day);

            /* Excel data에서 corresponding 날짜의 출근 인원 count fetch */
            let attendanceCount = '';
            if (isWorkDay && window.excelDashboardData && window.excelDashboardData.attendance && window.excelDashboardData.attendance.daily_data && window.excelDashboardData.attendance.daily_data[day]) {
                const count = window.excelDashboardData.attendance.daily_data[day].count;
                if (count > 0) {
                    attendanceCount = `<div class="attendance-count">${count}${employeeCountLabel}</div>`;
                }
            } else if (hasNoData) {
                attendanceCount = `<div class="attendance-count no-data-text">
                    <i class="fas fa-times-circle"></i>
                    <span>${noDataText}</span>
                </div>`;
            }

            calendarHTML += `
                <div class="calendar-day ${dayClass}">
                    <div class="day-number">${day}</div>
                    <div class="day-weekday">${weekday}${weekdaySuffix}</div>
                    ${icon ? `<div class="day-icon">${icon}</div>` : ''}
                    ${attendanceCount}
                </div>
            `;
        }
        calendarHTML += '</div>';

        /* 모달 번역 텍스트 */
        const modalTitle = getTranslation('workingDaysModal.title', currentLanguage);
        const totalWorkingDaysLabel = getTranslation('workingDaysModal.totalWorkingDays', currentLanguage);
        const totalDaysLabel = getTranslation('workingDaysModal.totalDays', currentLanguage);
        const noDataLabel = getTranslation('workingDaysModal.noData', currentLanguage);
        const legendWorkDay = getTranslation('workingDaysModal.legendWorkDay', currentLanguage);
        const legendNoDataText = getTranslation('workingDaysModal.legendNoData', currentLanguage);

        /* month 이름 fetch */
        const yearText = __YEAR__;
        const monthNames = {
            'ko': '__MONTH_KO__',
            'en': '__MONTH_EN__',
            'vi': '__MONTH_VI__'
        };
        const monthText = monthNames[currentLanguage] || monthNames['en'];

        const modalContent = `
            <div class="unified-modal-header">
                <h5 class="unified-modal-title">
                    <i class="fas fa-calendar-alt me-2"></i> ${yearText} ${monthText} ${modalTitle}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stat-card text-center p-3 border rounded">
                            <div class="stat-icon">💼</div>
                            <div class="stat-label">${totalWorkingDaysLabel}</div>
                            <div class="stat-value text-primary h3">${totalWorkingDays}${dayLabel}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card text-center p-3 border rounded">
                            <div class="stat-icon">📅</div>
                            <div class="stat-label">${totalDaysLabel}</div>
                            <div class="stat-value text-info h3">${daysInMonth}${dayLabel}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card text-center p-3 border rounded">
                            <div class="stat-icon">❌</div>
                            <div class="stat-label">${noDataLabel}</div>
                            <div class="stat-value text-secondary h3">${holidays.length}${dayLabel}</div>
                        </div>
                    </div>
                </div>
                ${calendarHTML}
                <div class="mt-3">
                    <span class="legend-badge legend-workday">💼 ${legendWorkDay}</span>
                    <span class="legend-badge legend-nodata">❌ ${legendNoDataText}</span>
                </div>
            </div>
        `;

        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;

        /* Bootstrap 5 Modal 처리 */
        const modalElement = document.getElementById('detailModal');

        // existing 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 creation with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',  // 모달 내부 클릭시 닫히지 않도록 설정
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가 (once: true로 중복 방지)
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
                document.body.style.overflow = '';  // 명시적으로 빈 문자열 설정
            }, 50);
        }, { once: true });
    }

    function showZeroWorkingDaysDetails() {
        // Excel data use (Single Source of Truth)
        let zeroWorkingEmployees = [];

        if (window.excelDashboardData && window.excelDashboardData.modal_data && window.excelDashboardData.modal_data.zero_working_days_직원) {
            // Excel에서 이미 필터링된 data use
            zeroWorkingEmployees = window.excelDashboardData.modal_data.zero_working_days_직원;
        } else if (window.employeeData) {
            // Fallback to employeeData (TYPE-3 제외)
            zeroWorkingEmployees = window.employeeData.filter(emp => {
                // TYPE-3 제외 (incentive 대상 아님)
                if (emp['type'] === 'TYPE-3' || emp['ROLE TYPE STD'] === 'TYPE-3') {
                    return false;
                }
                const actualDays = parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0);
                return actualDays === 0;
            });
        }

        // 0일 근무자 분류 함수 (Option 1 + Option 3)
        function classifyZeroWorkingEmployee(emp, lang) {
            const remark = (emp['RE MARK'] || '').toLowerCase();
            const pregnant = (emp['pregnant vacation-yes or no'] || '').toLowerCase();

            // 출산휴가 (파란색 - 정당한 사유)
            if (pregnant === 'yes' || remark.includes('maternity') || remark.includes('출산')) {
                return {
                    category: 'maternity',
                    badge: getTranslation('zeroWorkingDaysModal.categories.maternity', lang),
                    color: 'info',
                    priority: 3
                };
            }

            // 퇴사 (회색 - 정당한 사유)
            if (remark.includes('stop working') || remark.includes('퇴사') || remark.includes('resign')) {
                return {
                    category: 'resigned',
                    badge: getTranslation('zeroWorkingDaysModal.categories.resigned', lang),
                    color: 'secondary',
                    priority: 3
                };
            }

            // 직무변경 (노란색 - 확인 필요)
            if (remark.includes('change') || remark.includes('변경') || remark.includes('transfer')) {
                return {
                    category: 'jobChange',
                    badge: getTranslation('zeroWorkingDaysModal.categories.jobChange', lang),
                    color: 'warning',
                    priority: 2
                };
            }

            // 사유 없음 (빨간색 - 관리 필요)
            return {
                category: 'noReason',
                badge: getTranslation('zeroWorkingDaysModal.categories.noReason', lang),
                color: 'danger',
                priority: 1
            };
        }

        // 정렬 상태 관리 (기본값: priority로 정렬하여 관리 필요 케이스를 상단에 표시)
        let sortColumn = 'priority';
        let sortOrder = 'asc';

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            zeroWorkingEmployees.sort((a, b) => {
                let aVal, bVal;

                switch(column) {
                    case 'empNo':
                        aVal = a['Employee No'] || '';
                        bVal = b['Employee No'] || '';
                        break;
                    case 'name':
                        aVal = a['Full Name'] || '';
                        bVal = b['Full Name'] || '';
                        break;
                    case 'position':
                        aVal = a['QIP POSITION 1ST NAME'] || '';  // Fixed: single space (normalized)
                        bVal = b['QIP POSITION 1ST NAME'] || '';  // Fixed: single space (normalized)
                        break;
                    case 'totalDays':
                        aVal = a['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18);
                        bVal = b['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18);
                        break;
                    case 'actualDays':
                        aVal = a['Actual Working Days'] || 0;
                        bVal = b['Actual Working Days'] || 0;
                        break;
                    case 'stopDate':
                        aVal = a['Stop working Date'] || '';
                        bVal = b['Stop working Date'] || '';
                        break;
                    case 'pregnant':
                        aVal = a['pregnant vacation-yes or no'] || '';
                        bVal = b['pregnant vacation-yes or no'] || '';
                        break;
                    case 'remark':
                        aVal = a['RE MARK'] || '';  // Fixed: no trailing space (normalized)
                        bVal = b['RE MARK'] || '';  // Fixed: no trailing space (normalized)
                        break;
                    case 'status':
                        // 새로운 분류 시스템 사용 (Option 1 + Option 3)
                        const langStatus = currentLanguage || 'ko';
                        const aClassificationStatus = classifyZeroWorkingEmployee(a, langStatus);
                        const bClassificationStatus = classifyZeroWorkingEmployee(b, langStatus);
                        aVal = aClassificationStatus.category; // 'maternity', 'resigned', 'jobChange', 'noReason'
                        bVal = bClassificationStatus.category;
                        break;
                    case 'priority':
                        // Priority 정렬 추가 (1=관리필요, 2=확인필요, 3=정당한사유)
                        const lang = currentLanguage || 'ko';
                        const aClassification = classifyZeroWorkingEmployee(a, lang);
                        const bClassification = classifyZeroWorkingEmployee(b, lang);
                        aVal = aClassification.priority;
                        bVal = bClassification.priority;
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal, 'ko') : bVal.localeCompare(aVal, 'ko');
                } else {
                    return sortOrder === 'asc' ? (aVal - bVal) : (bVal - aVal);
                }
            });

            renderTable();
        }

        function renderTable() {
            const lang = currentLanguage || 'ko';
            let tableRows = '';

            // 요약 통계 계산 (Option 3)
            const total = zeroWorkingEmployees.length;
            const maternity = zeroWorkingEmployees.filter(emp => {
                const classification = classifyZeroWorkingEmployee(emp, lang);
                return classification.category === 'maternity';
            }).length;
            const resigned = zeroWorkingEmployees.filter(emp => {
                const classification = classifyZeroWorkingEmployee(emp, lang);
                return classification.category === 'resigned';
            }).length;
            const jobChange = zeroWorkingEmployees.filter(emp => {
                const classification = classifyZeroWorkingEmployee(emp, lang);
                return classification.category === 'jobChange';
            }).length;
            const noReason = zeroWorkingEmployees.filter(emp => {
                const classification = classifyZeroWorkingEmployee(emp, lang);
                return classification.category === 'noReason';
            }).length;

            const legitimateReasons = maternity + resigned;

            if (zeroWorkingEmployees.length === 0) {
                tableRows = `<tr><td colspan="11" class="text-center py-4"><i class="fas fa-check-circle text-success fa-2x mb-2 d-block"></i>${getTranslation('zeroWorkingDaysModal.description', lang)}</td></tr>`;
            } else {
                tableRows = zeroWorkingEmployees.map(emp => {
                    // Excel에서 가져온 필드 use (Single Source of Truth)
                    const actualDays = emp['Actual Working Days'] || 0;

                    // 출결 data file 기준 Total Days calculation
                    const empNo = String(emp['Employee No'] || '').padStart(9, '0');
                    let totalDays = 0;  // default value: 출결 data 없음

                    // attendance raw data에서 corresponding 직원의 unique 날짜 count calculation
                    if (window.attendanceRawData && window.attendanceRawData[empNo]) {
                        totalDays = window.attendanceRawData[empNo].uniqueDates || 0;
                    }
                    // 출결 data가 없으면 0으로 표시 (fact 반영)

                    const stopDate = emp['Stop working Date'] || '-';
                    const position = emp['QIP POSITION 1ST NAME'] || '-';  // Fixed: single space (normalized)
                    const pregnant = emp['pregnant vacation-yes or no'] || '';
                    const remark = emp['RE MARK'] || '-';  // Fixed: no trailing space (normalized)

                    // 새로운 분류 로직 사용 (Option 1)
                    const classification = classifyZeroWorkingEmployee(emp, lang);
                    const statusLabel = classification.badge;
                    const statusClass = `bg-${classification.color}`;

                    // 임신 휴가 번역
                    const pregnantLabel = pregnant === 'yes'
                        ? getTranslation('zeroWorkingDaysModal.statusLabels.yes', lang)
                        : pregnant === 'no'
                        ? getTranslation('zeroWorkingDaysModal.statusLabels.no', lang)
                        : '-';

                    // 인센티브 정보 가져오기 (수령 여부 및 금액)
                    const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                    const isReceived = incentiveAmount > 0;
                    const receivedCell = isReceived
                        ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                        : `<span style="color: #e74c3c;">❌</span>`;
                    const amountCell = incentiveAmount > 0
                        ? `<span style="color: #27ae60; font-weight: bold;">${incentiveAmount.toLocaleString()} ₫</span>`
                        : `<span style="color: #95a5a6;">0 ₫</span>`;

                    return `
                        <tr class="unified-table-row">
                            <td class="unified-table-cell">${emp['Employee No'] || ''}</td>
                            <td class="unified-table-cell">${emp['Full Name'] || ''}</td>
                            <td class="unified-table-cell">${position}</td>
                            <td class="unified-table-cell text-center">${totalDays}</td>
                            <td class="unified-table-cell text-center">
                                <span class="badge bg-danger">${actualDays}</span>
                            </td>
                            <td class="unified-table-cell text-center">
                                <span class="badge ${statusClass}">${statusLabel}</span>
                            </td>
                            <td class="unified-table-cell text-center">${stopDate}</td>
                            <td class="unified-table-cell text-center">${pregnantLabel}</td>
                            <td class="unified-table-cell">${remark}</td>
                            <td class="unified-table-cell text-center">${receivedCell}</td>
                            <td class="unified-table-cell text-end">${amountCell}</td>
                        </tr>
                    `;
                }).join('');
            }

            const modalContent = `
                <div class="unified-modal-header">
                    <h5 class="unified-modal-title">
                        <i class="fas fa-exclamation-triangle me-2"></i><span data-i18n="zeroWorkingDaysModal.title">${getTranslation('zeroWorkingDaysModal.title', lang)}</span>
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-light border-start border-4 border-danger mb-3">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-info-circle text-danger me-2"></i>
                            <span data-i18n="zeroWorkingDaysModal.description">${getTranslation('zeroWorkingDaysModal.description', lang)}</span>
                        </div>
                    </div>
                    ${total > 0 ? `
                    <div class="row mb-3">
                        <div class="col-12">
                            <div class="card border-0 shadow-sm">
                                <div class="card-body">
                                    <h6 class="card-title mb-3">
                                        <i class="fas fa-chart-pie me-2"></i>
                                        <span data-i18n="zeroWorkingDaysModal.summary.title">${getTranslation('zeroWorkingDaysModal.summary.title', lang)}</span>
                                    </h6>
                                    <div class="row g-2">
                                        <div class="col-md-3 col-6">
                                            <div class="p-2 bg-light rounded text-center">
                                                <div class="fs-4 fw-bold text-primary">${total}</div>
                                                <small class="text-muted" data-i18n="zeroWorkingDaysModal.summary.total">${getTranslation('zeroWorkingDaysModal.summary.total', lang)}</small>
                                            </div>
                                        </div>
                                        <div class="col-md-3 col-6">
                                            <div class="p-2 bg-danger bg-opacity-10 rounded text-center border border-danger">
                                                <div class="fs-4 fw-bold text-danger">${noReason}</div>
                                                <small class="text-danger" data-i18n="zeroWorkingDaysModal.summary.managementNeeded">${getTranslation('zeroWorkingDaysModal.summary.managementNeeded', lang)}</small>
                                            </div>
                                        </div>
                                        <div class="col-md-3 col-6">
                                            <div class="p-2 bg-warning bg-opacity-10 rounded text-center border border-warning">
                                                <div class="fs-4 fw-bold text-warning">${jobChange}</div>
                                                <small class="text-warning" data-i18n="zeroWorkingDaysModal.summary.reviewNeeded">${getTranslation('zeroWorkingDaysModal.summary.reviewNeeded', lang)}</small>
                                            </div>
                                        </div>
                                        <div class="col-md-3 col-6">
                                            <div class="p-2 bg-info bg-opacity-10 rounded text-center border border-info">
                                                <div class="fs-4 fw-bold text-info">${legitimateReasons}</div>
                                                <small class="text-info" data-i18n="zeroWorkingDaysModal.summary.legitimateReasons">${getTranslation('zeroWorkingDaysModal.summary.legitimateReasons', lang)}</small>
                                                <div class="mt-1 small text-muted">
                                                    <span data-i18n="zeroWorkingDaysModal.categories.maternity">${getTranslation('zeroWorkingDaysModal.categories.maternity', lang)}</span>: ${maternity} |
                                                    <span data-i18n="zeroWorkingDaysModal.categories.resigned">${getTranslation('zeroWorkingDaysModal.categories.resigned', lang)}</span>: ${resigned}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    <div class="table-responsive">
                        <table class="table table-hover table-sm">
                            <thead class="unified-table-header">
                                <tr>
                                    <th class="sortable-header ${sortColumn === 'empNo' ? sortOrder : ''}" onclick="window.zeroModalSort('empNo')" data-i18n="zeroWorkingDaysModal.headers.empNo">${getTranslation('zeroWorkingDaysModal.headers.empNo', lang)}</th>
                                    <th class="sortable-header ${sortColumn === 'name' ? sortOrder : ''}" onclick="window.zeroModalSort('name')" data-i18n="zeroWorkingDaysModal.headers.name">${getTranslation('zeroWorkingDaysModal.headers.name', lang)}</th>
                                    <th class="sortable-header ${sortColumn === 'position' ? sortOrder : ''}" onclick="window.zeroModalSort('position')" data-i18n="zeroWorkingDaysModal.headers.position">${getTranslation('zeroWorkingDaysModal.headers.position', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'totalDays' ? sortOrder : ''}" onclick="window.zeroModalSort('totalDays')" data-i18n="zeroWorkingDaysModal.headers.totalDays">${getTranslation('zeroWorkingDaysModal.headers.totalDays', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'actualDays' ? sortOrder : ''}" onclick="window.zeroModalSort('actualDays')" data-i18n="zeroWorkingDaysModal.headers.actualDays">${getTranslation('zeroWorkingDaysModal.headers.actualDays', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'status' ? sortOrder : ''}" onclick="window.zeroModalSort('status')" data-i18n="zeroWorkingDaysModal.headers.status">${getTranslation('zeroWorkingDaysModal.headers.status', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'stopDate' ? sortOrder : ''}" onclick="window.zeroModalSort('stopDate')" data-i18n="zeroWorkingDaysModal.headers.stopDate">${getTranslation('zeroWorkingDaysModal.headers.stopDate', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'pregnant' ? sortOrder : ''}" onclick="window.zeroModalSort('pregnant')" data-i18n="zeroWorkingDaysModal.headers.pregnantVacation">${getTranslation('zeroWorkingDaysModal.headers.pregnantVacation', lang)}</th>
                                    <th class="sortable-header ${sortColumn === 'remark' ? sortOrder : ''}" onclick="window.zeroModalSort('remark')" data-i18n="zeroWorkingDaysModal.headers.remark">${getTranslation('zeroWorkingDaysModal.headers.remark', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'received' ? sortOrder : ''}" onclick="window.zeroModalSort('received')" data-i18n="validationTab.tableHeaders.incentiveReceived">${getTranslation('validationTab.tableHeaders.incentiveReceived', lang)}</th>
                                    <th class="text-end sortable-header ${sortColumn === 'amount' ? sortOrder : ''}" onclick="window.zeroModalSort('amount')" data-i18n="validationTab.tableHeaders.incentiveAmount">${getTranslation('validationTab.tableHeaders.incentiveAmount', lang)}</th>
                                </tr>
                            </thead>
                            <tbody>${tableRows}</tbody>
                        </table>
                    </div>
                </div>
            `;

            // 모달이 없으면 creation
            let modal = document.getElementById('detailModal');
            if (!modal) {
                const modalHTML = `
                    <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="true" style="z-index: 1055;">
                        <div class="modal-dialog modal-fullscreen" style="margin: 0; width: 100vw; height: 100vh;">
                            <div class="modal-content" id="detailModalContent" style="height: 100%; border: none; border-radius: 0; display: flex; flex-direction: column;"></div>
                        </div>
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', modalHTML);
                modal = document.getElementById('detailModal');
            }

            document.getElementById('detailModalContent').innerHTML = modalContent;
        }

        // 전역 정렬 함count 등록
        window.zeroModalSort = sortData;

        // 초기 렌더링
        renderTable();

        // Bootstrap 5 Modal 처리
        const modalElement = document.getElementById('detailModal');

        // existing 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 creation with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',  // 모달 내부 클릭시 닫히지 않도록 설정
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가 (once: true로 중복 방지)
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
                document.body.style.overflow = '';  // 명시적으로 빈 문자열 설정
            }, 50);
        }, { once: true });
    }

    function showAbsentWithoutInformDetails() {
        let absentEmployees = window.employeeData.filter(emp => {
            const unapproved = parseFloat(emp.unapproved_absences || emp['Unapproved Absences'] || 0);
            // Filter >= 1 day to show all unapproved absences
            return unapproved >= 1;
        });

        // 정렬 상태 관리
        let sortColumn = 'days';
        let sortOrder = 'desc';

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            absentEmployees.sort((a, b) => {
                let aVal, bVal;

                switch(column) {
                    case 'empNo':
                        aVal = a['Employee No'] || '';
                        bVal = b['Employee No'] || '';
                        break;
                    case 'name':
                        aVal = a['Full Name'] || '';
                        bVal = b['Full Name'] || '';
                        break;
                    case 'position':
                        aVal = a['QIP POSITION 1ST NAME'] || '';  // Fixed: single space (normalized)
                        bVal = b['QIP POSITION 1ST NAME'] || '';  // Fixed: single space (normalized)
                        break;
                    case 'days':
                        aVal = parseFloat(a['Unapproved Absences'] || 0);
                        bVal = parseFloat(b['Unapproved Absences'] || 0);
                        break;
                    case 'stopDate':
                        aVal = a['Stop working Date'] || '';
                        bVal = b['Stop working Date'] || '';
                        break;
                    case 'pregnant':
                        aVal = a['pregnant vacation-yes or no'] || '';
                        bVal = b['pregnant vacation-yes or no'] || '';
                        break;
                    case 'remark':
                        aVal = a['RE MARK'] || '';  // Fixed: no trailing space (normalized)
                        bVal = b['RE MARK'] || '';  // Fixed: no trailing space (normalized)
                        break;
                    case 'status':
                        const aDays = parseFloat(a['Unapproved Absences'] || 0);
                        const bDays = parseFloat(b['Unapproved Absences'] || 0);
                        aVal = aDays > 2 ? 3 : (aDays === 2 ? 2 : 1);
                        bVal = bDays > 2 ? 3 : (bDays === 2 ? 2 : 1);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal, 'ko') : bVal.localeCompare(aVal, 'ko');
                } else {
                    return sortOrder === 'asc' ? (aVal - bVal) : (bVal - aVal);
                }
            });

            renderTable();
        }

        function renderTable() {
            const lang = currentLanguage || 'ko';

            // Calculate statistics before rendering
            const total = absentEmployees.length;
            const excluded = absentEmployees.filter(emp => {
                const days = parseFloat(emp['Unapproved Absences'] || 0);
                return days >= 3;
            }).length;
            const warning = absentEmployees.filter(emp => {
                const days = parseFloat(emp['Unapproved Absences'] || 0);
                return days === 2;
            }).length;
            const caution = total - excluded - warning;

            let tableRows = absentEmployees.map(emp => {
                const days = parseFloat(emp['Unapproved Absences'] || 0);
                const position = emp['QIP POSITION 1ST NAME'] || '-';  // Fixed: single space (normalized)
                const stopDate = emp['Stop working Date'] || '-';
                const pregnant = emp['pregnant vacation-yes or no'] || '';
                const remark = emp['RE MARK'] || '-';  // Fixed: no trailing space (normalized)

                // 상태 및 스타th
                let statusLabel, statusClass, daysBadgeClass;
                if (days >= 3) {
                    statusLabel = getTranslation('validationTab.status.excluded', lang);
                    statusClass = 'bg-danger';
                    daysBadgeClass = 'bg-danger';
                } else if (days === 2) {
                    statusLabel = getTranslation('validationTab.status.warning', lang);
                    statusClass = 'bg-warning text-dark';
                    daysBadgeClass = 'bg-warning text-dark';
                } else {
                    statusLabel = getTranslation('validationTab.status.caution', lang);
                    statusClass = 'bg-info';
                    daysBadgeClass = 'bg-info';
                }

                // 임신 휴가 번역
                const pregnantLabel = pregnant === 'yes'
                    ? getTranslation('zeroWorkingDaysModal.statusLabels.yes', lang)
                    : pregnant === 'no'
                    ? getTranslation('zeroWorkingDaysModal.statusLabels.no', lang)
                    : '-';

                // 인센티브 수령 여부 및 금액
                const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                const isReceived = incentiveAmount > 0;
                const receivedCell = isReceived
                    ? '<span class="badge bg-success">✅</span>'
                    : '<span style="color: #e74c3c; font-size: 1.2em;">❌</span>';
                const amountCell = incentiveAmount > 0
                    ? `<span style="color: #27ae60; font-weight: bold;">${incentiveAmount.toLocaleString()} ₫</span>`
                    : '<span style="color: #95a5a6;">0 ₫</span>';

                return `
                    <tr class="unified-table-row">
                        <td class="unified-table-cell">${emp['Employee No'] || ''}</td>
                        <td class="unified-table-cell">${emp['Full Name'] || ''}</td>
                        <td class="unified-table-cell">${position}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${daysBadgeClass}">${days}</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${statusClass}">${statusLabel}</span>
                        </td>
                        <td class="unified-table-cell text-center">${stopDate}</td>
                        <td class="unified-table-cell text-center">${pregnantLabel}</td>
                        <td class="unified-table-cell">${remark}</td>
                        <td class="unified-table-cell text-center">${receivedCell}</td>
                        <td class="unified-table-cell text-center">${amountCell}</td>
                    </tr>
                `;
            }).join('');

            // Add Total row if there are employees
            if (total > 0) {
                tableRows += `
                    <tr class="table-active fw-bold" style="border-top: 2px solid #dee2e6;">
                        <td colspan="3" class="unified-table-cell text-end">Total</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-secondary">${total}</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger me-1">${excluded}</span>
                            <span class="badge bg-warning text-dark me-1">${warning}</span>
                            <span class="badge bg-info">${caution}</span>
                        </td>
                        <td colspan="5" class="unified-table-cell"></td>
                    </tr>
                `;
            } else {
                tableRows = `
                    <tr>
                        <td colspan="10" class="text-center py-5">
                            <i class="fas fa-check-circle text-success fa-3x mb-3"></i>
                            <div class="text-muted">무단결근자가 not found</div>
                        </td>
                    </tr>`;
            }

        // 통계 섹션 추가
        const statsSection = total > 0 ? `
            <div class="alert alert-light border-start border-4 border-warning mb-4">
                <div class="row text-center">
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">${getTranslation('validationTab.stats.total', currentLanguage) || 'Total'}</span>
                            <span class="fs-4 fw-bold text-dark">${total}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">${getTranslation('validationTab.stats.caution', currentLanguage) || 'Caution'} (1${getTranslation('validationTab.units.day', currentLanguage) || ' day'})</span>
                            <span class="fs-4 fw-bold text-info">${caution}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">${getTranslation('validationTab.stats.warning', currentLanguage) || 'Warning'} (2${getTranslation('validationTab.units.days', currentLanguage) || ' days'})</span>
                            <span class="fs-4 fw-bold text-warning">${warning}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">${getTranslation('validationTab.stats.excluded', currentLanguage) || 'Excluded'} (3${getTranslation('validationTab.units.days', currentLanguage) || ' days'}+)</span>
                            <span class="fs-4 fw-bold text-danger">${excluded}</span>
                        </div>
                    </div>
                </div>
            </div>
        ` : '';

            const modalContent = `
                <div class="unified-modal-header" style="flex-shrink: 0;">
                    <h5 class="unified-modal-title">
                        <i class="fas fa-user-times me-2"></i><span data-i18n="validationTab.modals.absentWithoutInform.title">${getTranslation('validationTab.modals.absentWithoutInform.title', lang)}</span>
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" style="flex: 1; overflow-y: auto; overflow-x: hidden;">
                    <div class="alert alert-light border-start border-4 border-danger mb-3">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-info-circle text-danger me-2"></i>
                            <span data-i18n="validationTab.warnings.absentExclusion">${getTranslation('validationTab.warnings.absentExclusion', lang)}</span>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover table-sm">
                            <thead class="unified-table-header">
                                <tr>
                                    <th class="sortable-header ${sortColumn === 'empNo' ? sortOrder : ''}" onclick="window.absentModalSort('empNo')" data-i18n="validationTab.tableHeaders.empNo">${getTranslation('validationTab.tableHeaders.empNo', lang)}</th>
                                    <th class="sortable-header ${sortColumn === 'name' ? sortOrder : ''}" onclick="window.absentModalSort('name')" data-i18n="validationTab.tableHeaders.name">${getTranslation('validationTab.tableHeaders.name', lang)}</th>
                                    <th class="sortable-header ${sortColumn === 'position' ? sortOrder : ''}" onclick="window.absentModalSort('position')" data-i18n="validationTab.tableHeaders.position">${getTranslation('validationTab.tableHeaders.position', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'days' ? sortOrder : ''}" onclick="window.absentModalSort('days')" data-i18n="validationTab.tableHeaders.absentDays">${getTranslation('validationTab.tableHeaders.absentDays', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'status' ? sortOrder : ''}" onclick="window.absentModalSort('status')" data-i18n="validationTab.tableHeaders.status">${getTranslation('validationTab.tableHeaders.status', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'stopDate' ? sortOrder : ''}" onclick="window.absentModalSort('stopDate')" data-i18n="zeroWorkingDaysModal.headers.stopDate">${getTranslation('zeroWorkingDaysModal.headers.stopDate', lang)}</th>
                                    <th class="text-center sortable-header ${sortColumn === 'pregnant' ? sortOrder : ''}" onclick="window.absentModalSort('pregnant')" data-i18n="zeroWorkingDaysModal.headers.pregnantVacation">${getTranslation('zeroWorkingDaysModal.headers.pregnantVacation', lang)}</th>
                                    <th class="sortable-header ${sortColumn === 'remark' ? sortOrder : ''}" onclick="window.absentModalSort('remark')" data-i18n="zeroWorkingDaysModal.headers.remark">${getTranslation('zeroWorkingDaysModal.headers.remark', lang)}</th>
                                    <th class="text-center sortable-header" data-i18n="validationTab.tableHeaders.incentiveReceived">${getTranslation('validationTab.tableHeaders.incentiveReceived', lang) || (lang === 'ko' ? '수령' : lang === 'en' ? 'Received' : 'Nhận')}</th>
                                    <th class="text-center sortable-header" data-i18n="validationTab.tableHeaders.incentiveAmount">${getTranslation('validationTab.tableHeaders.incentiveAmount', lang) || (lang === 'ko' ? '인센티브 금액' : lang === 'en' ? 'Incentive Amount' : 'Số tiền')}</th>
                                </tr>
                            </thead>
                            <tbody>${tableRows}</tbody>
                        </table>
                    </div>
                </div>
            `;

            document.getElementById('detailModalContent').innerHTML = modalContent;
        }

        // 모달 표시 처리 (sortData 호출 전에 creation)
        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-fullscreen">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        // 전역 정렬 함count 등록
        window.absentModalSort = sortData;

        // 초기 정렬 상태로 렌더링
        sortData('days');

        /* Bootstrap 5 Modal 처리 */
        const modalElement = document.getElementById('detailModal');

        // existing 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 creation with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',  // 모달 내부 클릭시 닫히지 않도록 설정
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가 (once: true로 중복 방지)
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
                document.body.style.overflow = '';  // 명시적으로 빈 문자열 설정
            }, 50);
        }, { once: true });
    }

    function showMinimumDaysNotMetDetails() {
        // Excel의 Minimum_Working_Days_Required use (Single Source of Truth)
        const firstEmp = window.employeeData[0] || {};
        const minimumRequired = firstEmp['Minimum_Working_Days_Required'] || 12;

        // C4 조건 사용 (Single Source of Truth)
        let notMetEmployees = window.employeeData.filter(emp => {
            // TYPE-3 제외 (incentive 대상 아님)
            if (emp['type'] === 'TYPE-3' || emp['ROLE TYPE STD'] === 'TYPE-3') {
                return false;
            }
            // C4 조건: cond_4_minimum_days = 'FAIL'
            return emp['cond_4_minimum_days'] === 'FAIL';
        });

        // 정렬 상태 관리
        let sortColumn = 'actualDays';
        let sortOrder = 'asc';

        function renderTable() {
            const lang = currentLanguage || 'ko';
            const daysUnit = getTranslation('validationTab.units.days', lang);

            // 정렬 apply
            const sorted = [...notMetEmployees].sort((a, b) => {
                let aVal, bVal;

                switch(sortColumn) {
                    case 'empNo':
                        aVal = a.employee_no || a['Employee No'] || '';
                        bVal = b.employee_no || b['Employee No'] || '';
                        break;
                    case 'name':
                        aVal = a.full_name || a['Full Name'] || '';
                        bVal = b.full_name || b['Full Name'] || '';
                        break;
                    case 'position':
                        aVal = a['QIP POSITION 1ST NAME'] || '';  // Fixed: single space (normalized)
                        bVal = b['QIP POSITION 1ST NAME'] || '';  // Fixed: single space (normalized)
                        break;
                    case 'type':
                        aVal = a['type'] || a['ROLE TYPE STD'] || '';
                        bVal = b['type'] || b['ROLE TYPE STD'] || '';
                        break;
                    case 'actualDays':
                        aVal = parseFloat(a.actual_working_days || a['Actual Working Days'] || 0);
                        bVal = parseFloat(b.actual_working_days || b['Actual Working Days'] || 0);
                        break;
                    case 'shortage':
                        aVal = minimumRequired - parseFloat(a.actual_working_days || a['Actual Working Days'] || 0);
                        bVal = minimumRequired - parseFloat(b.actual_working_days || b['Actual Working Days'] || 0);
                        break;
                    case 'status':
                        aVal = parseFloat(a.actual_working_days || a['Actual Working Days'] || 0) >= minimumRequired ? 1 : 0;
                        bVal = parseFloat(b.actual_working_days || b['Actual Working Days'] || 0) >= minimumRequired ? 1 : 0;
                        break;
                    default:
                        aVal = 0;
                        bVal = 0;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                } else {
                    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
                }
            });

            let tableRows = sorted.map(emp => {
                const actualDays = parseFloat(emp.actual_working_days || emp['Actual Working Days'] || 0);
                const shortage = minimumRequired - actualDays;
                const percentage = (actualDays / minimumRequired * 100).toFixed(1);

                // 더 직원확한 색상 구분
                let progressColor = 'danger';
                let textColor = 'text-white';
                if (percentage >= 75) {
                    progressColor = 'info';
                    textColor = 'text-dark';  // 하늘색 배경에 검은색 텍스트
                } else if (percentage >= 50) {
                    progressColor = 'warning';
                    textColor = 'text-dark';  // 노란색 배경에 검은색 텍스트
                }
                // percentage < 50은 danger (빨간색) 유지

                const isMet = actualDays >= minimumRequired;

                const empType = emp['type'] || emp['ROLE TYPE STD'] || '-';
                const typeColor = empType === 'TYPE-3' ? 'bg-secondary' : (empType === 'TYPE-1' ? 'bg-primary' : 'bg-success');

                return `
                    <tr class="unified-table-row">
                        <td style="padding: 12px 8px; font-weight: 500;">${emp['Employee No'] || ''}</td>
                        <td style="padding: 12px 8px; font-weight: 500;">${emp['Full Name'] || ''}</td>
                        <td style="padding: 12px 8px; font-size: 13px;">${emp['QIP POSITION 1ST NAME'] || '-'}</td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <span class="badge ${typeColor}" style="font-size: 12px;">${empType}</span>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <div class="d-flex align-items-center justify-content-center">
                                <span class="badge bg-${progressColor} ${textColor}" style="font-size: 14px; padding: 8px 12px;">
                                    ${actualDays}${daysUnit}
                                </span>
                            </div>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <span class="badge bg-primary" style="font-size: 14px; padding: 8px 12px;">${minimumRequired}${daysUnit}</span>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <span class="badge bg-danger" style="font-size: 14px; padding: 8px 12px;">-${shortage}${daysUnit}</span>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <span class="badge ${isMet ? 'bg-success' : 'bg-danger'}" style="font-size: 13px; padding: 6px 10px;" data-i18n="validationTab.modals.minimumDaysNotMet.statusLabels.${isMet ? 'met' : 'notMet'}">
                                ${isMet ? getTranslation('validationTab.modals.minimumDaysNotMet.statusLabels.met', lang) : getTranslation('validationTab.modals.minimumDaysNotMet.statusLabels.notMet', lang)}
                            </span>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            ${(() => {
                                const incentive = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                                const received = incentive > 0;
                                return received ?
                                    '<span class="badge bg-success">✅</span>' :
                                    '<span class="badge bg-secondary">❌</span>';
                            })()}
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            ${(() => {
                                const incentive = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                                return incentive > 0 ?
                                    '<span class="badge bg-info text-dark">' + incentive.toLocaleString() + ' ₫</span>' :
                                    '<span class="text-muted">0 ₫</span>';
                            })()}
                        </td>
                    </tr>
                `;
            }).join('') || (() => {
                // 리포트 타입에 따라 다른 메시지 표시
                const isInterim = reportType === 'interim';
                const messageKey = isInterim ? 'interimMessage' : 'emptyMessage';
                const iconClass = isInterim ? 'fa-info-circle text-info' : 'fa-check-circle text-success';
                return `<tr><td colspan="10" class="text-center py-4"><i class="fas ${iconClass} fa-2x mb-2 d-block"></i><div data-i18n="validationTab.modals.minimumDaysNotMet.${messageKey}">${getTranslation('validationTab.modals.minimumDaysNotMet.' + messageKey, lang)}</div></td></tr>`;
            })();

            return tableRows;
        }

        function setSorting(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            const tbody = document.querySelector('#detailModal tbody');
            if (tbody) {
                tbody.innerHTML = renderTable();
            }

            // 헤더 클래스 업데이트
            document.querySelectorAll('#detailModal .sortable-header').forEach(th => {
                th.classList.remove('asc', 'desc');
            });
            const currentHeader = document.querySelector(`#detailModal .sortable-header[data-sort="${column}"]`);
            if (currentHeader) {
                currentHeader.classList.add(sortOrder);
            }
        }

        const lang = currentLanguage || 'ko';

        const modalContent = `
            <div class="unified-modal-header" style="flex-shrink: 0;">
                <h5 class="unified-modal-title">
                    <i class="fas fa-clock me-2"></i><span data-i18n="validationTab.modals.minimumDaysNotMet.title">${getTranslation('validationTab.modals.minimumDaysNotMet.title', lang)}</span>
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" style="flex: 1; overflow-y: auto; overflow-x: hidden;">
                <div class="alert alert-light border-start border-4 border-warning mb-3">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-info-circle text-warning me-2"></i>
                        <div>
                            <div>
                                <span data-i18n="validationTab.modals.minimumDaysNotMet.alertMessage">${getTranslation('validationTab.modals.minimumDaysNotMet.alertMessage', lang)}</span> ${minimumRequired}<span data-i18n="validationTab.units.days">${getTranslation('validationTab.units.days', lang)}</span>
                            </div>
                            <div class="text-muted small mt-1">
                                <span data-i18n="validationTab.modals.minimumDaysNotMet.excludeNote">${getTranslation('validationTab.modals.minimumDaysNotMet.excludeNote', lang)}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover" id="minimumDaysTable" style="font-size: 14px;">
                        <thead class="unified-table-header">
                            <tr>
                                <th class="sortable-header" data-sort="empNo" onclick="window.minDaysSort('empNo')" style="min-width: 100px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.empNo">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.empNo', lang)}</th>
                                <th class="sortable-header" data-sort="name" onclick="window.minDaysSort('name')" style="min-width: 130px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.name">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.name', lang)}</th>
                                <th class="sortable-header" data-sort="position" onclick="window.minDaysSort('position')" style="min-width: 150px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.position">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.position', lang)}</th>
                                <th class="sortable-header" data-sort="type" onclick="window.minDaysSort('type')" style="min-width: 80px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.type">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.type', lang)}</th>
                                <th class="text-center sortable-header asc" data-sort="actualDays" onclick="window.minDaysSort('actualDays')" style="min-width: 110px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.actualDays">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.actualDays', lang)}</th>
                                <th class="text-center" style="min-width: 80px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.minimumRequired">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.minimumRequired', lang)}</th>
                                <th class="text-center sortable-header" data-sort="shortage" onclick="window.minDaysSort('shortage')" style="min-width: 70px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.shortage">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.shortage', lang)}</th>
                                <th class="text-center sortable-header" data-sort="status" onclick="window.minDaysSort('status')" style="min-width: 80px;" data-i18n="validationTab.modals.minimumDaysNotMet.headers.status">${getTranslation('validationTab.modals.minimumDaysNotMet.headers.status', lang)}</th>
                                <th class="text-center sortable-header" data-sort="received" onclick="window.minDaysSort('received')" style="min-width: 80px;" data-i18n="validationTab.modals.common.headers.received">${getTranslation('validationTab.modals.common.headers.received', lang) || (lang === 'ko' ? '수령' : lang === 'en' ? 'Received' : 'Nhận')}</th>
                                <th class="text-center sortable-header" data-sort="incentive" onclick="window.minDaysSort('incentive')" style="min-width: 120px;" data-i18n="validationTab.modals.common.headers.incentiveAmount">${getTranslation('validationTab.modals.common.headers.incentiveAmount', lang) || (lang === 'ko' ? '인센티브' : lang === 'en' ? 'Incentive' : 'Thưởng')}</th>
                            </tr>
                        </thead>
                        <tbody>${renderTable()}</tbody>
                    </table>
                </div>
            </div>
        `;

        // 전역 정렬 함count 설정
        window.minDaysSort = setSorting;

        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;

        /* Bootstrap 5 Modal 처리 */
        const modalElement = document.getElementById('detailModal');

        // existing 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 creation with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',  // 모달 내부 클릭시 닫히지 않도록 설정
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가 (once: true로 중복 방지)
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
                document.body.style.overflow = '';  // 명시적으로 빈 문자열 설정
            }, 50);
        }, { once: true });
    }

    function showAttendanceBelow88Details() {
        // 출근율 88% 미만 직원 필터링 (TYPE-3 제외)
        let below88Employees = window.employeeData.filter(emp => {
            // TYPE-3 제외 (incentive 대상 아님)
            if (emp['type'] === 'TYPE-3' || emp['ROLE TYPE STD'] === 'TYPE-3') {
                return false;
            }
            const attendanceRate = parseFloat(emp['출근율_Attendance_Rate_Percent'] || emp['Attendance Rate'] || 0);
            return attendanceRate < 88;
        });

        let sortColumn = 'attendanceRate';
        let sortOrder = 'asc';

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = column === 'attendanceRate' ? 'asc' : 'desc';
            }
            updateTableBody();
        }

        function updateTableBody() {
            const tbody = document.querySelector('#attendanceModal tbody');
            if (!tbody) return;

            // 정렬
            below88Employees.sort((a, b) => {
                let aVal, bVal;
                switch (sortColumn) {
                    case 'empNo':
                        aVal = a['Employee No'] || a['emp_no'];
                        bVal = b['Employee No'] || b['emp_no'];
                        break;
                    case 'name':
                        aVal = a['Full Name'] || a['name'];
                        bVal = b['Full Name'] || b['name'];
                        break;
                    case 'position':
                        aVal = a['QIP POSITION 1ST NAME'] || '';
                        bVal = b['QIP POSITION 1ST NAME'] || '';
                        break;
                    case 'type':
                        aVal = a['type'] || a['ROLE TYPE STD'] || '';
                        bVal = b['type'] || b['ROLE TYPE STD'] || '';
                        break;
                    case 'attendanceRate':
                        aVal = parseFloat(a['출근율_Attendance_Rate_Percent'] || 0);
                        bVal = parseFloat(b['출근율_Attendance_Rate_Percent'] || 0);
                        break;
                    case 'actualDays':
                        aVal = parseFloat(a['Actual Working Days'] || a['actual_working_days'] || 0);
                        bVal = parseFloat(b['Actual Working Days'] || b['actual_working_days'] || 0);
                        break;
                    case 'totalDays':
                        aVal = parseFloat(a['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18));
                        bVal = parseFloat(b['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18));
                        break;
                    case 'resignDate':
                        aVal = a['Stop working Date'] || '9999-12-31';
                        bVal = b['Stop working Date'] || '9999-12-31';
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }
                return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
            });

            // 테이블 업데이트 (다국어 지원)
            const lang = currentLanguage || 'ko';
            const dayText = getTranslation('validationTab.units.day', lang);
            const metText = getTranslation('validationTab.modals.attendanceBelow88.statusLabels.met', lang);
            const notMetText = getTranslation('validationTab.modals.attendanceBelow88.statusLabels.notMet', lang);

            tbody.innerHTML = '';
            below88Employees.forEach(emp => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                let name = emp['Full Name'] || emp['name'];
                const attendanceRate = parseFloat(emp['Attendance Rate'] || emp['출근율_Attendance_Rate_Percent'] || 0).toFixed(1);
                const actualDays = parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0);
                const totalDays = parseFloat(emp['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18));

                // 조기 퇴사 확인 (해당 월 10일 이내 퇴사)
                let earlyResignBadge = '';
                let resignDateDisplay = '-';
                const stopDate = emp['Stop working Date'];
                if (stopDate) {
                    resignDateDisplay = stopDate;
                    try {
                        // Parse date (MM/DD/YYYY or YYYY-MM-DD format)
                        let resignDate;
                        if (stopDate.includes('/')) {
                            const parts = stopDate.split('/');
                            resignDate = new Date(parts[2], parts[0] - 1, parts[1]); // MM/DD/YYYY
                        } else {
                            resignDate = new Date(stopDate); // YYYY-MM-DD
                        }

                        const resignDay = resignDate.getDate();
                        const resignMonth = resignDate.getMonth() + 1;
                        // Check if resigned in current month within first 10 days
                        if (resignMonth === MONTH_NUM_PLACEHOLDER && resignDay <= 10) {
                            const badgeText = getTranslation('validationTab.modals.attendanceBelow88.earlyResignBadge', lang);
                            const resignLabel = getTranslation('validationTab.modals.attendanceBelow88.resignationDate', lang);
                            earlyResignBadge = `<span class="badge bg-warning text-dark ms-2" style="font-size: 11px;" title="${resignLabel}: ${stopDate}">⚠️ ${badgeText}</span>`;
                        }
                    } catch (e) {
                        // Date parsing failed, ignore
                    }
                }

                // 출근율에 따른 색상과 텍스트 색상 - 더 직원확한 구분
                let badgeClass = 'bg-danger';
                let textColor = 'text-white';
                let customStyle = '';

                if (attendanceRate >= 70) {
                    badgeClass = 'bg-info';  // 70% 이상은 하늘색
                    textColor = 'text-dark';
                } else if (attendanceRate >= 50) {
                    badgeClass = 'bg-warning';  // 50-70%는 노란색
                    textColor = 'text-dark';
                } else if (attendanceRate >= 30) {
                    // 30-50%는 주황색 (커스텀 스타th)
                    badgeClass = '';
                    customStyle = 'background-color: #ff6b35 !important; color: white !important;';
                }
                // attendanceRate < 30은 bg-danger (빨간색) 유지

                const conditionMet = attendanceRate >= 88;
                const statusText = conditionMet ? metText : notMetText;
                const statusBadge = conditionMet ? 'bg-success' : 'bg-danger';

                const empType = emp['type'] || emp['ROLE TYPE STD'] || '-';
                const typeColor = empType === 'TYPE-3' ? 'bg-secondary' : (empType === 'TYPE-1' ? 'bg-primary' : 'bg-success');
                const position = emp['QIP POSITION 1ST NAME'] || '-';

                // 인센티브 정보 가져오기
                const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                const receivedCell = incentiveAmount > 0
                    ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                    : `<span style="color: #e74c3c;">❌</span>`;
                const amountCell = incentiveAmount > 0
                    ? `<span style="color: #27ae60; font-weight: bold;">${incentiveAmount.toLocaleString()} ₫</span>`
                    : `<span style="color: #95a5a6;">0 ₫</span>`;

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="padding: 10px; font-weight: 500;">${empNo}</td>
                    <td style="padding: 10px; font-weight: 500;">${name}${earlyResignBadge}</td>
                    <td style="padding: 10px; font-size: 13px;">${position}</td>
                    <td style="padding: 10px;"><span class="badge ${typeColor}" style="font-size: 12px;">${empType}</span></td>
                    <td style="padding: 10px;"><span class="badge ${badgeClass} ${textColor}" style="font-size: 14px; padding: 6px 10px; ${customStyle}">${attendanceRate}%</span></td>
                    <td style="padding: 10px;">${actualDays}${dayText}</td>
                    <td style="padding: 10px;">${totalDays}${dayText}</td>
                    <td style="padding: 10px; font-size: 13px;">${resignDateDisplay}</td>
                    <td style="padding: 10px;"><span class="badge ${statusBadge}" style="font-size: 13px; padding: 4px 8px;" data-i18n="validationTab.modals.attendanceBelow88.statusLabels.${conditionMet ? 'met' : 'notMet'}">${statusText}</span></td>
                    <td style="padding: 10px; text-align: center;">${receivedCell}</td>
                    <td style="padding: 10px;">${amountCell}</td>
                `;
                tbody.appendChild(row);
            });
        }

        function getSortIcon(column) {
            if (sortColumn !== column) return '';
            return sortOrder === 'asc' ? '▲' : '▼';
        }

        // Bootstrap 모달 HTML creation (다국어 지원)
        const lang = currentLanguage || 'ko';

        const modalHTML = `
            <div class="modal fade" id="attendanceModal" tabindex="-1" role="dialog" aria-labelledby="attendanceModalLabel" aria-hidden="true" style="z-index: 1055;">
                <div class="modal-dialog modal-fullscreen" role="document" style="margin: 0; width: 100vw; height: 100vh;">
                    <div class="modal-content" style="height: 100%; border: none; border-radius: 0;">
                        <div class="modal-header unified-modal-header" style="flex-shrink: 0;">
                            <h5 class="modal-title unified-modal-title" id="attendanceModalLabel">
                                <i class="fas fa-percentage me-2"></i><span data-i18n="validationTab.modals.attendanceBelow88.title">${getTranslation('validationTab.modals.attendanceBelow88.title', lang)}</span>
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body" style="flex: 1; overflow-y: auto; overflow-x: hidden;">
                            <div class="mb-3">
                                <div class="alert alert-light border-start border-4 border-warning">
                                    <div class="d-flex align-items-center">
                                        <i class="fas fa-info-circle text-warning me-2"></i>
                                        <div>
                                            <div>
                                                <span data-i18n="validationTab.modals.attendanceBelow88.alertMessage">${getTranslation('validationTab.modals.attendanceBelow88.alertMessage', lang)}</span>
                                            </div>
                                            <div class="text-muted small mt-1">
                                                <span data-i18n="validationTab.modals.attendanceBelow88.excludeNote">${getTranslation('validationTab.modals.attendanceBelow88.excludeNote', lang)}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <p class="text-muted"><i class="fas fa-users me-2"></i><span data-i18n="common.total">${getTranslation('common.total', lang)}</span> ${below88Employees.length} <span data-i18n="common.people">${getTranslation('common.people', lang)}</span></p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-hover" style="font-size: 14px;">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th class="sortable-header" data-sort="empNo" style="min-width: 100px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.headers.empNo">${getTranslation('validationTab.modals.attendanceBelow88.headers.empNo', lang)} ${getSortIcon('empNo')}</th>
                                            <th class="sortable-header" data-sort="name" style="min-width: 130px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.headers.name">${getTranslation('validationTab.modals.attendanceBelow88.headers.name', lang)} ${getSortIcon('name')}</th>
                                            <th class="sortable-header" data-sort="position" style="min-width: 150px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.headers.position">${getTranslation('validationTab.modals.attendanceBelow88.headers.position', lang)} ${getSortIcon('position')}</th>
                                            <th class="sortable-header" data-sort="type" style="min-width: 80px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.headers.type">${getTranslation('validationTab.modals.attendanceBelow88.headers.type', lang)} ${getSortIcon('type')}</th>
                                            <th class="sortable-header" data-sort="attendanceRate" style="min-width: 100px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.headers.attendanceRate">${getTranslation('validationTab.modals.attendanceBelow88.headers.attendanceRate', lang)} ${getSortIcon('attendanceRate')}</th>
                                            <th class="sortable-header" data-sort="actualDays" style="min-width: 110px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.headers.actualDays">${getTranslation('validationTab.modals.attendanceBelow88.headers.actualDays', lang)} ${getSortIcon('actualDays')}</th>
                                            <th class="sortable-header" data-sort="totalDays" style="min-width: 100px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.headers.totalDays">${getTranslation('validationTab.modals.attendanceBelow88.headers.totalDays', lang)} ${getSortIcon('totalDays')}</th>
                                            <th class="sortable-header" data-sort="resignDate" style="min-width: 100px; padding: 12px; cursor: pointer;" data-i18n="validationTab.modals.attendanceBelow88.resignationDate">${getTranslation('validationTab.modals.attendanceBelow88.resignationDate', lang)} ${getSortIcon('resignDate')}</th>
                                            <th style="min-width: 90px; padding: 12px;" data-i18n="validationTab.modals.attendanceBelow88.headers.conditionMet">${getTranslation('validationTab.modals.attendanceBelow88.headers.conditionMet', lang)}</th>
                                            <th style="min-width: 80px; padding: 12px;" data-i18n="validationTab.tableHeaders.incentiveReceived">${getTranslation('validationTab.tableHeaders.incentiveReceived', lang)}</th>
                                            <th style="min-width: 120px; padding: 12px;" data-i18n="validationTab.tableHeaders.incentiveAmount">${getTranslation('validationTab.tableHeaders.incentiveAmount', lang)}</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // existing 모달이 있으면 제거
        const existingModal = document.getElementById('attendanceModal');
        if (existingModal) {
            const existingBsModal = bootstrap.Modal.getInstance(existingModal);
            if (existingBsModal) {
                existingBsModal.dispose();
            }
            existingModal.remove();
        }

        // 모달을 body에 추가
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // 모달 엘리먼트 참조
        const modalElement = document.getElementById('attendanceModal');

        // Bootstrap 모달 인스턴스 creation 및 표시
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',  // 모달 내부 클릭시 닫히지 않도록 설정
            keyboard: true,      // ESC 키로 닫기 활성화
            focus: true
        });

        // 정렬 이벤트 추가
        modalElement.querySelectorAll('.sortable-header').forEach(header => {
            header.addEventListener('click', function() {
                const column = this.getAttribute('data-sort');
                sortData(column);

                // 헤더 업데이트
                modalElement.querySelectorAll('.sortable-header').forEach(h => {
                    const col = h.getAttribute('data-sort');
                    const icon = getSortIcon(col);
                    h.innerHTML = h.textContent.replace(/[▲▼]/g, '').trim() + ' ' + icon;
                });
            });
        });

        // 초기 data load
        updateTableBody();

        // 모달 표시
        bsModal.show();

        // 백드롭 클릭 이벤트 직원시적 처리 (출근율 모달)
        setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.cursor = 'pointer';
                backdrop.addEventListener('click', function(e) {
                    if (e.target === backdrop) {
                        bsModal.hide();
                    }
                });
            }
        }, 100);

        // 모달이 닫힐 때 DOM에서 제거
        modalElement.addEventListener('hidden.bs.modal', function () {
            modalElement.remove();
        });
    }


    function showConsecutiveAqlFailDetails() {
        // 전역 언어와 synchronization
        let currentLang = (typeof window.currentLanguage !== 'undefined' ? window.currentLanguage : null) ||
                         (typeof currentLanguage !== 'undefined' ? currentLanguage : null) ||
                         'ko';

        // 현재 보고서 월 가져오기 (from HTML data attributes)
        const reportMonthNum = parseInt(document.getElementById('incentiveDataPeriod').getAttribute('data-month'));

        // 월 약어 매핑 (1=Jan, 2=Feb, ..., 12=Dec)
        const monthAbbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthKorean = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];

        // N-1, N-2, N-3 월 계산
        const month_N = reportMonthNum;  // 현재 월
        const month_N1 = month_N - 1 > 0 ? month_N - 1 : 12;  // 1개월 전
        const month_N2 = month_N - 2 > 0 ? month_N - 2 : month_N - 2 + 12;  // 2개월 전
        const month_N3 = month_N - 3 > 0 ? month_N - 3 : month_N - 3 + 12;  // 3개월 전

        // 동적 월 패턴 생성
        const pattern3Months = `${monthAbbr[month_N2-1]}-${monthAbbr[month_N1-1]}-${monthAbbr[month_N-1]}`;  // 예: Aug-Sep-Oct

        // 언어별 월 패턴
        const getMonthPattern = (lang, monthIdx1, monthIdx2) => {
            if (lang === 'ko') {
                return `${monthKorean[monthIdx1-1].replace('월','')}-${monthKorean[monthIdx2-1]}`;
            } else if (lang === 'en') {
                return `${monthAbbr[monthIdx1-1]}-${monthAbbr[monthIdx2-1]}`;
            } else if (lang === 'vi') {
                return `Tháng ${monthIdx1}-${monthIdx2}`;
            }
            return `${monthAbbr[monthIdx1-1]}-${monthAbbr[monthIdx2-1]}`;
        };

        const pattern2MonthsHigh = getMonthPattern(currentLang, month_N1, month_N);  // 최근 2개월
        const pattern2MonthsMedium = getMonthPattern(currentLang, month_N2, month_N1);  // 중간 2개월

        // Continuous_FAIL 필터링용 대문자 패턴
        const filterPatternHigh = `${monthAbbr[month_N1-1].toUpperCase()}_${monthAbbr[month_N-1].toUpperCase()}`;  // 예: SEP_OCT
        const filterPatternMedium = `${monthAbbr[month_N2-1].toUpperCase()}_${monthAbbr[month_N1-1].toUpperCase()}`;  // 예: AUG_SEP

        // 3연속 개월 실패자와 2연속 개월 실패자 분리
        const threeMonthFails = window.employeeData.filter(emp =>
            emp['Continuous_FAIL'] === 'YES_3MONTHS'
        );

        // 수정: Continuous_FAIL_2Month 컬럼 사용 (별도 컬럼으로 분리되어 있음)
        const twoMonthFails = window.employeeData.filter(emp =>
            emp['Continuous_FAIL_2Month'] === 'YES'
        );

        // 번역 함count
        const t = (key) => getTranslation(key, currentLang);

        // Custom HTML for this specific modal
        const existingModal = document.getElementById('consecutiveAqlFailModal');
        if (existingModal) {
            existingModal.remove();
        }

        let modalHTML = '<div id="consecutiveAqlFailModal" class="modal" style="display: block; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);">';
        modalHTML += '<div class="modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 0; border: 1px solid #888; width: 80%; max-width: 1200px; border-radius: 10px;">';
        modalHTML += '<div class="modal-header unified-modal-header">';
        modalHTML += '<h5 class="modal-title unified-modal-title"><i class="fas fa-exclamation-triangle me-2"></i>' + t('validationTab.modals.aqlFail.consecutiveAqlFail.title') + '</h5>';
        modalHTML += '<button type="button" class="btn-close" onclick="document.getElementById(&apos;consecutiveAqlFailModal&apos;).remove()"></button>';
        modalHTML += '</div>';
        modalHTML += '<div class="modal-body" style="padding: 20px;">';

        // 3연속 개월 실패 섹션
        modalHTML += '<div class="section-container" style="margin-bottom: 30px;">';
        modalHTML += '<h3 style="color: #c0392b; margin-bottom: 15px;">🔴 ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.threeMonthSection') + '</h3>';

        if (threeMonthFails.length === 0) {
            modalHTML += '<div class="alert alert-success" style="padding: 15px; background: #d4edda; color: #155724; border-radius: 5px;">';
            modalHTML += '✅ ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.noThreeMonth');
            modalHTML += '</div>';
        } else {
            modalHTML += '<table style="width: 100%; border-collapse: collapse;">';
            modalHTML += '<thead><tr style="background: #f8f9fa;">';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.empNo') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.name') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.position') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.supervisor') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.failPattern') + '</th>';
            modalHTML += '</tr></thead><tbody>';

            threeMonthFails.forEach(emp => {
                modalHTML += '<tr>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['Employee No'] || emp['emp_no']) + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['Full Name'] || emp['name']) + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['QIP POSITION 1ST  NAME'] || emp['position'] || '-') + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['direct boss name'] || emp['MST direct boss name'] || emp['boss_name'] || '-') + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['AQL_Fail_Pattern'] || pattern3Months) + '</td>';
                modalHTML += '</tr>';
            });

            modalHTML += '</tbody></table>';
        }
        modalHTML += '</div>';

        // 2연속 개월 실패 섹션
        modalHTML += '<div class="section-container">';
        modalHTML += '<h3 style="color: #e67e22; margin-bottom: 15px;">⚠️ ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.twoMonthSection') + '</h3>';

        // 동적 월 패턴으로 필터링
        const augSepFailsList = twoMonthFails.filter(emp => emp['Continuous_FAIL'].includes(filterPatternHigh));
        const julAugFailsList = twoMonthFails.filter(emp => emp['Continuous_FAIL'].includes(filterPatternMedium));

        if (twoMonthFails.length === 0) {
            modalHTML += '<div class="alert alert-info" style="padding: 15px; background: #d1ecf1; color: #0c5460; border-radius: 5px;">';
            modalHTML += t('validationTab.modals.aqlFail.consecutiveAqlFail.noTwoMonth');
            modalHTML += '<br><br>';
            modalHTML += '<strong>📊 상세 현황:</strong><br>';
            modalHTML += '• ' + pattern2MonthsHigh + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.consecutiveFailure') + '<span style="color: #dc3545; font-weight: bold;">0</span>' + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.people') + '<br>';
            modalHTML += '• ' + pattern2MonthsMedium + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.consecutiveFailure') + '<span style="color: #ffc107; font-weight: bold;">0</span>' + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.people');
            modalHTML += '</div>';
        } else {
            modalHTML += '<table style="width: 100%; border-collapse: collapse;">';
            modalHTML += '<thead><tr style="background: #f8f9fa;">';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.empNo') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.name') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.position') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.supervisor') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.failPattern') + '</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">' + t('validationTab.modals.aqlFail.consecutiveAqlFail.headers.risk') + '</th>';
            modalHTML += '</tr></thead><tbody>';

            // 2개월 연속 실패자 모두 표시 (Continuous_FAIL_2Month === 'YES'인 직원)
            // 위험도: 현재 월에 가까울수록 높음 (10-11월 > 9-10월)
            twoMonthFails.forEach(emp => {
                modalHTML += '<tr style="background: #fff5f5;">';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['Employee No'] || emp['emp_no']) + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['Full Name'] || emp['name']) + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['QIP POSITION 1ST  NAME'] || emp['position'] || '-') + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['direct boss name'] || emp['MST direct boss name'] || emp['boss_name'] || '-') + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;">' + (emp['AQL_Fail_Pattern'] || pattern2MonthsHigh) + '</td>';
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;"><span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px;">🔴 ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.riskLevels.high') + '</span></td>';
                modalHTML += '</tr>';
            });

            modalHTML += '</tbody></table>';

            // 범례 추가
            modalHTML += '<div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px;">';
            modalHTML += '<strong>' + t('validationTab.modals.aqlFail.consecutiveAqlFail.riskExplanation.title') + '</strong><br>';
            modalHTML += '🔴 <strong>' + t('validationTab.modals.aqlFail.consecutiveAqlFail.riskLevels.high') + ' (' + pattern2MonthsHigh + '):</strong> ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.riskExplanation.highDesc') + '<br>';
            modalHTML += '🟡 <strong>' + t('validationTab.modals.aqlFail.consecutiveAqlFail.riskLevels.medium') + ' (' + pattern2MonthsMedium + '):</strong> ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.riskExplanation.mediumDesc');
            modalHTML += '</div>';
        }
        modalHTML += '</div>';

        // 요약 통계
        modalHTML += '<div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 5px;">';
        modalHTML += '<strong>📊 ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.title') + '</strong><br>';
        modalHTML += '• ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.threeMonthFails') + ' <strong>' + threeMonthFails.length + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.people') + '</strong><br>';
        modalHTML += '• ' + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.twoMonthFails') + ' <strong>' + twoMonthFails.length + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.people') + '</strong><br>';
        modalHTML += '&nbsp;&nbsp;- <span style="color: #dc3545; font-weight: bold;">🔴 ' + pattern2MonthsHigh + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.consecutiveFailure') + augSepFailsList.length + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.people') + '</span><br>';
        modalHTML += '&nbsp;&nbsp;- <span style="color: #ffc107; font-weight: bold;">🟡 ' + pattern2MonthsMedium + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.consecutiveFailure') + julAugFailsList.length + t('validationTab.modals.aqlFail.consecutiveAqlFail.summary.people') + '</span>';
        modalHTML += '</div>';

        // Close modal HTML
        modalHTML += '</div>';
        modalHTML += '</div>';
        modalHTML += '</div>';

        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // 언어 전환 함count 등록
        window.switchConsecutiveLang = function(lang) {
            // 전역 언어 상태 업데이트
            if (typeof window.currentLanguage !== 'undefined') {
                window.currentLanguage = lang;
            }
            if (typeof currentLanguage !== 'undefined') {
                currentLanguage = lang;
            }
            // 모달 재creation
            document.getElementById('consecutiveAqlFailModal').remove();
            showConsecutiveAqlFailDetails();
        };

        // Add click outside to close functionality
        const modal = document.getElementById('consecutiveAqlFailModal');
        modal.onclick = function(event) {
            if (event.대상 === modal) {
                modal.remove();
                delete window.switchConsecutiveLang;
            }
        };
    }

    function showAqlFailDetails() {
        // AQL FAIL이 있는 직원 필터링
        let aqlFailEmployees = window.employeeData.filter(emp => {
            const aqlFailures = parseFloat(emp[window.aqlFailuresColumn] || emp['aql_failures'] || 0);
            return aqlFailures > 0;
        });

        // 정렬 상태 관리
        let sortColumn = 'failPercent';
        let sortOrder = 'desc';
        let modalDiv = null;
        let backdrop = null;

        // 현재 언어 상태 - 전역 언어와 synchronization
        let currentLang = (typeof window.currentLanguage !== 'undefined' ? window.currentLanguage : null) ||
                         (typeof currentLanguage !== 'undefined' ? currentLanguage : null) ||
                         'ko';

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            aqlFailEmployees.sort((a, b) => {
                let aVal, bVal;

                switch(column) {
                    case 'empNo':
                        aVal = a['Employee No'] || a.employee_no || '';
                        bVal = b['Employee No'] || b.employee_no || '';
                        break;
                    case 'name':
                        aVal = a['Full Name'] || a.full_name || '';
                        bVal = b['Full Name'] || b.full_name || '';
                        break;
                    case 'supervisor':
                        aVal = a['direct boss name'] || '';
                        bVal = b['direct boss name'] || '';
                        break;
                    case 'inspectorId':
                        aVal = a['MST direct boss name'] || '';
                        bVal = b['MST direct boss name'] || '';
                        break;
                    case 'passCount':
                        aVal = parseFloat(a['AQL_Pass_Count'] || 0);
                        bVal = parseFloat(b['AQL_Pass_Count'] || 0);
                        break;
                    case 'failures':
                        aVal = parseFloat(a[window.aqlFailuresColumn] || 0);
                        bVal = parseFloat(b[window.aqlFailuresColumn] || 0);
                        break;
                    case 'failPercent':
                        aVal = parseFloat(a['AQL_Fail_Percent'] || 0);
                        bVal = parseFloat(b['AQL_Fail_Percent'] || 0);
                        break;
                    default:
                        aVal = '';
                        bVal = '';
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal, 'ko') : bVal.localeCompare(aVal, 'ko');
                } else {
                    return sortOrder === 'asc' ? (aVal - bVal) : (bVal - aVal);
                }
            });

            updateTableBody();
        }

        function switchLanguage(lang) {
            currentLang = lang;
            // 전역 언어 상태도 synchronization
            if (typeof window.currentLanguage !== 'undefined') {
                window.currentLanguage = lang;
            }
            if (typeof currentLanguage !== 'undefined') {
                currentLanguage = lang;
            }
            updateAllModalContent();
            // 언어 버튼 상태 업데이트
            updateLanguageButtons();
        }

        function updateLanguageButtons() {
            const buttons = document.querySelectorAll('#aqlFailModal .btn-group button');
            buttons.forEach(btn => {
                const btnLang = btn.getAttribute('onclick').match(/'(\\w+)'/)[1];
                if (btnLang === currentLang) {
                    btn.classList.remove('btn-outline-primary');
                    btn.classList.add('btn-primary');
                } else {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-primary');
                }
            });
        }

        function updateAllModalContent() {
            // 모달 제목 업데이트
            const titleEl = document.querySelector('#aqlFailModal .modal-title span[data-i18n]');
            if (titleEl) {
                titleEl.textContent = getTranslation('validationTab.modals.aqlFail.title', currentLang);
            }

            // Alert 메시지 업데이트
            const alertEl = document.querySelector('#aqlFailModal .alert span[data-i18n="aqlFailAlert"]');
            if (alertEl) {
                alertEl.textContent = getTranslation('validationTab.modals.aqlFail.alertMessage', currentLang);
            }

            // 카운트 메시지 업데이트
            const countEl = document.querySelector('#aqlFailModal .alert span[data-i18n="aqlFailCount"]');
            if (countEl) {
                // 현재 월 이름을 언어별로 생성
                const monthNamesMap = {
                    'ko': '__MONTH_KO__',
                    'en': '__MONTH_EN__',
                    'vi': '__MONTH_VI__'
                };
                const localizedMonth = monthNamesMap[currentLang] || monthNamesMap['en'];

                const countMsg = getTranslation('validationTab.modals.aqlFail.totalCount', currentLang);
                countEl.textContent = countMsg.replace('{' + '{count}' + '}', aqlFailEmployees.length).replace('{' + '{month}' + '}', localizedMonth);
            }

            // 테이블 헤더 업데이트
            const headers = {
                'empNo': 'validationTab.modals.aqlFail.headers.empNo',
                'name': 'validationTab.modals.aqlFail.headers.name',
                'supervisor': 'validationTab.modals.aqlFail.headers.supervisor',
                'inspectorId': 'validationTab.modals.aqlFail.headers.inspectorId',
                'aqlPass': 'validationTab.modals.aqlFail.headers.aqlPass',
                'aqlFail': 'validationTab.modals.aqlFail.headers.aqlFail',
                'failPercent': 'validationTab.modals.aqlFail.headers.failPercent'
            };

            Object.keys(headers).forEach(key => {
                const headerEl = document.querySelector(`#aqlFailModal th[data-i18n="${key}"]`);
                if (headerEl) {
                    const iconSpan = headerEl.querySelector('.sort-icon');
                    const icon = iconSpan ? iconSpan.textContent : '';
                    headerEl.innerHTML = `<span data-i18n="${key}">${getTranslation(headers[key], currentLang)}</span><span class="sort-icon">${icon}</span>`;
                }
            });

            // 라인리더 집계 섹션 헤더 업데이트
            const lineLeaderTitleEl = document.querySelector('#aqlFailModal h6[data-i18n="lineLeaderTitle"]');
            if (lineLeaderTitleEl) {
                lineLeaderTitleEl.innerHTML = `<i class="fas fa-users me-2"></i><span data-i18n="lineLeaderTitle">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.title', currentLang)}</span>`;
            }

            const lineLeaderDescEl = document.querySelector('#aqlFailModal p[data-i18n="lineLeaderDesc"]');
            if (lineLeaderDescEl) {
                lineLeaderDescEl.textContent = getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.description', currentLang);
            }

            // 라인리더 테이블 헤더 업데이트
            const lineLeaderHeaders = {
                'leaderName': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderName',
                'leaderSupervisor': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderSupervisor',
                'subordinatePass': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinatePass',
                'subordinateFail': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinateFail',
                'failPercent': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.failPercent'
            };

            Object.keys(lineLeaderHeaders).forEach(key => {
                const headerEl = document.querySelector(`#lineLeaderTable th[data-i18n="${key}"]`);
                if (headerEl) {
                    headerEl.textContent = getTranslation(lineLeaderHeaders[key], currentLang);
                }
            });
        }

        function updateTableBody() {
            const tbody = document.querySelector('#aqlFailModal tbody');
            if (!tbody) return;

            let tableRows = aqlFailEmployees.map(emp => {
                const failures = parseFloat(emp[window.aqlFailuresColumn] || 0);
                const supervisorName = emp['direct boss name'] || '-';
                const supervisorId = emp['MST direct boss name'] || '-';

                const totalTests = emp['AQL_Total_Tests'] || 10;
                const passCount = emp['AQL_Pass_Count'] || Math.max(0, totalTests - failures);
                const failPercent = emp['AQL_Fail_Percent'] ? emp['AQL_Fail_Percent'].toFixed(1) : ((failures / totalTests * 100).toFixed(1));

                // failed율에 따른 색상 구분
                let failBadgeClass = '';
                let failBadgeText = '';
                if (failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                    failBadgeText = currentLang === 'ko' ? `${failPercent}% (심각)` : currentLang === 'en' ? `${failPercent}% (Critical)` : `${failPercent}% (Nghiêm trọng)`;
                } else if (failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                    failBadgeText = currentLang === 'ko' ? `${failPercent}% (경고)` : currentLang === 'en' ? `${failPercent}% (Warning)` : `${failPercent}% (Cảnh báo)`;
                } else {
                    failBadgeClass = 'bg-info';
                    failBadgeText = `${failPercent}%`;
                }

                // 인센티브 수령 여부 및 금액 (updateTableBody에서도 표시)
                const incentiveAmount = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                const isReceived = incentiveAmount > 0;
                const receivedCell = isReceived
                    ? '<span class="badge bg-success">✅</span>'
                    : '<span class="badge bg-secondary">❌</span>';
                const amountCell = incentiveAmount > 0
                    ? '<span class="badge bg-info text-dark">' + incentiveAmount.toLocaleString() + ' ₫</span>'
                    : '<span class="text-muted">0 ₫</span>';

                return `
                    <tr class="unified-table-row">
                        <td class="unified-table-cell">${emp['Employee No'] || ''}</td>
                        <td class="unified-table-cell">${emp['Full Name'] || ''}</td>
                        <td class="unified-table-cell">${supervisorName}</td>
                        <td class="unified-table-cell text-center">${supervisorId}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${passCount}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${failures}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${failBadgeText}</span>
                        </td>
                        <td class="unified-table-cell text-center">${receivedCell}</td>
                        <td class="unified-table-cell text-center">${amountCell}</td>
                    </tr>
                `;
            }).join('');

            const emptyMessage = currentLang === 'ko' ? 'AQL FAIL이 not found' : currentLang === 'en' ? 'No AQL FAIL records' : 'Không có bản ghi AQL FAIL';
            tbody.innerHTML = tableRows || `<tr><td colspan="9" class="text-center text-muted">${emptyMessage}</td></tr>`;

            // 정렬 아이콘 업데이트
            document.querySelectorAll('#aqlFailModal th[data-sort]').forEach(th => {
                const column = th.getAttribute('data-sort');
                const sortIcon = th.querySelector('.sort-icon');
                if (sortIcon) {
                    if (sortColumn === column) {
                        sortIcon.textContent = sortOrder === 'asc' ? ' ▲' : ' ▼';
                    } else {
                        sortIcon.textContent = ' ⇅';
                    }
                }
            });
        }

        function aggregateLineLeaderStats() {
            const lineLeaderStats = {};

            // 라인리더by 집계
            aqlFailEmployees.forEach(emp => {
                const supervisorId = emp['MST direct boss name'];
                const supervisorName = emp['direct boss name'];

                if (!supervisorId || !supervisorName) return;

                if (!lineLeaderStats[supervisorId]) {
                    // 라인리더의 상사 정보 찾기
                    const supervisorData = window.employeeData.find(e => e['Employee No'] === supervisorId);
                    const supervisorOfSupervisor = supervisorData ? (supervisorData['direct boss name'] || '-') : '-';

                    lineLeaderStats[supervisorId] = {
                        name: supervisorName,
                        supervisor: supervisorOfSupervisor,
                        totalPass: 0,
                        totalFail: 0
                    };
                }

                const passCount = parseFloat(emp['AQL_Pass_Count'] || 0);
                const failCount = parseFloat(emp[window.aqlFailuresColumn] || 0);

                lineLeaderStats[supervisorId].totalPass += passCount;
                lineLeaderStats[supervisorId].totalFail += failCount;
            });

            // 배열로 conversion 및 FAIL % calculation
            return Object.values(lineLeaderStats).map(stat => {
                const total = stat.totalPass + stat.totalFail;
                const failPercent = total > 0 ? ((stat.totalFail / total) * 100).toFixed(1) : '0.0';
                return { ...stat, failPercent: parseFloat(failPercent) };
            }).sort((a, b) => b.failPercent - a.failPercent); // FAIL % 내림차순
        }

        function renderLineLeaderTable() {
            const lineLeaderStats = aggregateLineLeaderStats();
            const tbody = document.querySelector('#lineLeaderTable tbody');
            if (!tbody) return;

            const rows = lineLeaderStats.map(stat => {
                let failBadgeClass = '';
                if (stat.failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                } else if (stat.failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                } else {
                    failBadgeClass = 'bg-info';
                }

                return `
                    <tr>
                        <td class="unified-table-cell">${stat.name}</td>
                        <td class="unified-table-cell">${stat.supervisor}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${stat.totalPass}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${stat.totalFail}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${stat.failPercent}%</span>
                        </td>
                    </tr>
                `;
            }).join('');

            const emptyMessage = currentLang === 'ko' ? '라인리더 data가 not found' : currentLang === 'en' ? 'No Line Leader data' : 'Không có dữ liệu Line Leader';
            tbody.innerHTML = rows || `<tr><td colspan="5" class="text-center text-muted">${emptyMessage}</td></tr>`;
        }

        function createAqlFailModal() {
            const lang = currentLang;

            function getSortIcon(column) {
                if (sortColumn === column) {
                    return sortOrder === 'asc' ? ' ▲' : ' ▼';
                }
                return ' ⇅';
            }

            let tableRows = aqlFailEmployees.map(emp => {
                const failures = parseFloat(emp[window.aqlFailuresColumn] || 0);
                const supervisorName = emp['direct boss name'] || '-';
                const supervisorId = emp['MST direct boss name'] || '-';

                const totalTests = emp['AQL_Total_Tests'] || 10;
                const passCount = emp['AQL_Pass_Count'] || Math.max(0, totalTests - failures);
                const failPercent = emp['AQL_Fail_Percent'] ? emp['AQL_Fail_Percent'].toFixed(1) : ((failures / totalTests * 100).toFixed(1));

                let failBadgeClass = '';
                let failBadgeText = '';
                if (failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                    failBadgeText = lang === 'ko' ? `${failPercent}% (심각)` : lang === 'en' ? `${failPercent}% (Critical)` : `${failPercent}% (Nghiêm trọng)`;
                } else if (failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                    failBadgeText = lang === 'ko' ? `${failPercent}% (경고)` : lang === 'en' ? `${failPercent}% (Warning)` : `${failPercent}% (Cảnh báo)`;
                } else {
                    failBadgeClass = 'bg-info';
                    failBadgeText = `${failPercent}%`;
                }

                return `
                    <tr class="unified-table-row">
                        <td class="unified-table-cell">${emp['Employee No'] || ''}</td>
                        <td class="unified-table-cell">${emp['Full Name'] || ''}</td>
                        <td class="unified-table-cell">${supervisorName}</td>
                        <td class="unified-table-cell text-center">${supervisorId}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${passCount}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${failures}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${failBadgeText}</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            ${(() => {
                                const incentive = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                                return incentive > 0 ?
                                    '<span class="badge bg-success">✅</span>' :
                                    '<span class="badge bg-secondary">❌</span>';
                            })()}
                        </td>
                        <td class="unified-table-cell text-center">
                            ${(() => {
                                const incentive = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                                return incentive > 0 ?
                                    '<span class="badge bg-info text-dark">' + incentive.toLocaleString() + ' ₫</span>' :
                                    '<span class="text-muted">0 ₫</span>';
                            })()}
                        </td>
                    </tr>
                `;
            }).join('');

            // 라인리더 집계 테이블
            const lineLeaderStats = aggregateLineLeaderStats();
            const lineLeaderRows = lineLeaderStats.map(stat => {
                let failBadgeClass = '';
                if (stat.failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                } else if (stat.failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                } else {
                    failBadgeClass = 'bg-info';
                }

                return `
                    <tr>
                        <td class="unified-table-cell">${stat.name}</td>
                        <td class="unified-table-cell">${stat.supervisor}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${stat.totalPass}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${stat.totalFail}cases</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${stat.failPercent}%</span>
                        </td>
                    </tr>
                `;
            }).join('');

            // 현재 월 이름을 언어별로 생성
            const monthNamesMap = {
                'ko': '__MONTH_KO__',
                'en': '__MONTH_EN__',
                'vi': '__MONTH_VI__'
            };
            const localizedMonth = monthNamesMap[lang] || monthNamesMap['en'];

            const countMsg = getTranslation('validationTab.modals.aqlFail.totalCount', lang).replace('{' + '{count}' + '}', aqlFailEmployees.length).replace('{' + '{month}' + '}', localizedMonth);

            let modalContent = `
                <div class="modal-dialog modal-xl" style="max-width: 95%; margin: 20px auto;">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <span data-i18n="validationTab.modals.aqlFail.title">${getTranslation('validationTab.modals.aqlFail.title', lang)}</span>
                            </h5>
                            <div class="d-flex align-items-center">
                                <div class="btn-group btn-group-sm me-2">
                                    <button type="button" class="btn btn-sm ${lang === 'ko' ? 'btn-primary' : 'btn-outline-primary'}" onclick="window.switchAqlLang('ko')">한국어</button>
                                    <button type="button" class="btn btn-sm ${lang === 'en' ? 'btn-primary' : 'btn-outline-primary'}" onclick="window.switchAqlLang('en')">English</button>
                                    <button type="button" class="btn btn-sm ${lang === 'vi' ? 'btn-primary' : 'btn-outline-primary'}" onclick="window.switchAqlLang('vi')">Tiếng Việt</button>
                                </div>
                                <button type="button" class="btn-close" onclick="window.closeAqlModal()"></button>
                            </div>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning d-flex align-items-center mb-3">
                                <i class="fas fa-info-circle me-2"></i>
                                <div>
                                    <strong><span data-i18n="aqlFailAlert">${getTranslation('validationTab.modals.aqlFail.alertMessage', lang)}</span></strong><br>
                                    <span data-i18n="aqlFailCount">${countMsg}</span>
                                </div>
                            </div>

                            <h6 class="mb-3" data-i18n="validationTab.modals.aqlFail.title"><i class="fas fa-list me-2"></i>${getTranslation('validationTab.modals.aqlFail.title', lang)}</h6>

                            <table class="table table-hover" id="aqlFailEmployeeTable">
                                <thead class="unified-table-header">
                                    <tr>
                                        <th style="cursor: pointer;" data-sort="empNo" onclick="window.sortAqlData('empNo')">
                                            <span data-i18n="empNo">${getTranslation('validationTab.modals.aqlFail.headers.empNo', lang)}</span><span class="sort-icon">${getSortIcon('empNo')}</span>
                                        </th>
                                        <th style="cursor: pointer;" data-sort="name" onclick="window.sortAqlData('name')">
                                            <span data-i18n="name">${getTranslation('validationTab.modals.aqlFail.headers.name', lang)}</span><span class="sort-icon">${getSortIcon('name')}</span>
                                        </th>
                                        <th style="cursor: pointer;" data-sort="supervisor" onclick="window.sortAqlData('supervisor')">
                                            <span data-i18n="supervisor">${getTranslation('validationTab.modals.aqlFail.headers.supervisor', lang)}</span><span class="sort-icon">${getSortIcon('supervisor')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="inspectorId" onclick="window.sortAqlData('inspectorId')">
                                            <span data-i18n="inspectorId">${getTranslation('validationTab.modals.aqlFail.headers.inspectorId', lang)}</span><span class="sort-icon">${getSortIcon('inspectorId')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="passCount" onclick="window.sortAqlData('passCount')">
                                            <span data-i18n="aqlPass">${getTranslation('validationTab.modals.aqlFail.headers.aqlPass', lang)}</span><span class="sort-icon">${getSortIcon('passCount')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="failures" onclick="window.sortAqlData('failures')">
                                            <span data-i18n="aqlFail">${getTranslation('validationTab.modals.aqlFail.headers.aqlFail', lang)}</span><span class="sort-icon">${getSortIcon('failures')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="failPercent" onclick="window.sortAqlData('failPercent')">
                                            <span data-i18n="failPercent">${getTranslation('validationTab.modals.aqlFail.headers.failPercent', lang)}</span><span class="sort-icon">${getSortIcon('failPercent')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="received" onclick="window.sortAqlData('received')">
                                            <span data-i18n="received">${lang === 'ko' ? '수령' : lang === 'en' ? 'Received' : 'Nhận'}</span><span class="sort-icon">${getSortIcon('received')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="incentive" onclick="window.sortAqlData('incentive')">
                                            <span data-i18n="incentiveAmount">${lang === 'ko' ? '인센티브' : lang === 'en' ? 'Incentive' : 'Thưởng'}</span><span class="sort-icon">${getSortIcon('incentive')}</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tableRows || '<tr><td colspan="9" class="text-center text-muted">AQL FAIL이 not found</td></tr>'}
                                </tbody>
                            </table>

                            <hr class="my-4">

                            <h6 class="mb-3" data-i18n="lineLeaderTitle"><i class="fas fa-users me-2"></i>${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.title', lang)}</h6>
                            <p class="text-muted small" data-i18n="lineLeaderDesc">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.description', lang)}</p>

                            <table class="table table-hover" id="lineLeaderTable">
                                <thead class="unified-table-header">
                                    <tr>
                                        <th data-i18n="leaderName">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderName', lang)}</th>
                                        <th data-i18n="leaderSupervisor">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderSupervisor', lang)}</th>
                                        <th class="text-center" data-i18n="subordinatePass">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinatePass', lang)}</th>
                                        <th class="text-center" data-i18n="subordinateFail">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinateFail', lang)}</th>
                                        <th class="text-center" data-i18n="failPercent">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.failPercent', lang)}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${lineLeaderRows || '<tr><td colspan="5" class="text-center text-muted">라인리더 data가 not found</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            // existing 모달 제거
            const existingModal = document.getElementById('aqlFailModal');
            if (existingModal) {
                existingModal.remove();
            }

            // 백드롭 제거
            const existingBackdrop = document.querySelector('.modal-backdrop');
            if (existingBackdrop) {
                existingBackdrop.remove();
            }

            // 새 모달 creation
            modalDiv = document.createElement('div');
            modalDiv.id = 'aqlFailModal';
            modalDiv.className = 'modal fade show';
            modalDiv.style.display = 'block';
            modalDiv.style.zIndex = '1055';
            modalDiv.innerHTML = modalContent;

            // 백드롭 creation
            backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.style.zIndex = '1050';

            document.body.appendChild(backdrop);
            document.body.appendChild(modalDiv);
            document.body.style.overflow = 'hidden';

            // 전역 함count 등록
            window.sortAqlData = sortData;
            window.switchAqlLang = switchLanguage;

            // 초기 언어 버튼 상태 설정
            updateLanguageButtons();
        }

        // 모달 닫기 함count
        window.closeAqlModal = function() {
            if (modalDiv) {
                modalDiv.remove();
                modalDiv = null;
            }
            if (backdrop) {
                backdrop.remove();
                backdrop = null;
            }
            document.body.style.overflow = '';
        };

        // 초기 렌더링
        sortData('failPercent');  // FAIL %로 정렬
        createAqlFailModal();
    }

    // Area AQL Reject Rate 상세 모달 (조건 7번, 8번 구분 표시)
    function showAreaRejectRateDetails() {
        // ========================================================================
        // Buildingby AQL 검사 성과 분석 - 3개 테이블 구조
        // 테이블 1: Buildingby AQL 검사 실적 (AQL file 기준)
        // 테이블 2: Assembly Inspector 인력 기준 검사 실적 (Employee CSV 기준)
        // 테이블 3: Auditor/Trainer incentive 현황 (책임 range)
        // ========================================================================

        // 현재 보고서 연도/월 가져오기
        const reportYear = parseInt(document.getElementById('incentiveDataPeriod').getAttribute('data-year'));
        const reportMonthNum = parseInt(document.getElementById('incentiveDataPeriod').getAttribute('data-month'));
        const monthAbbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthKorean = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
        const reportMonthName = monthAbbr[reportMonthNum - 1];
        const reportMonthKorean = monthKorean[reportMonthNum - 1];

        // AQL file data (Python에서 calculation된 actual data use)
        // Buildingby actual 검사 통계 (검사 casescount 기준 Reject Rate)
        const aqlFileStats = window.aqlFileStats || {
            // Fallback: window.aqlFileStats가 없는 경우 빈 객체 use
            'Building B': { total: 0, pass: 0, fail: 0, rejectRate: 0.0 },
            'Building B3': { total: 0, pass: 0, fail: 0, rejectRate: 0.0 },
            'Building D': { total: 0, pass: 0, fail: 0, rejectRate: 0.0 },
            'Building A': { total: 0, pass: 0, fail: 0, rejectRate: 0.0 },
            'Building C': { total: 0, pass: 0, fail: 0, rejectRate: 0.0 },
            'total': { total: 0, pass: 0, fail: 0, rejectRate: 0.0 }
        };

        console.log('[AQL Modal] Using AQL File Stats:', aqlFileStats);

        // Total AQL tests count 계산 (window.aqlFileStats의 total에서)
        const totalAqlTests = aqlFileStats['total'] ? aqlFileStats['total'].total : 0;

        // AQL 관련 직원 필터링 함count
        function isAqlRelevantEmployee(emp) {
            const aqlTests = parseFloat(emp['AQL_Total_Tests'] || 0);
            const areaRate = parseFloat(emp['Area_Reject_Rate'] || 0);

            // 조건 1: actual AQL 검사 count행 (28employees)
            if (aqlTests > 0) return true;

            // 조건 2: Auditor/Trainer (Area_Reject_Rate > 0인 10명)
            if (areaRate > 0) return true;

            // 나머지는 Non-AQL Staff로 제외
            return false;
        }

        // Building 매핑 함수 (JSON 기반 동적 매핑)
        function getEmployeeArea(emp) {
            const building = emp['BUILDING'];
            const aqlTests = parseFloat(emp['AQL_Total_Tests'] || 0);
            const empNo = String(emp['Employee No'] || emp['emp_no'] || '');

            // 1순위: BUILDING column (actual 검사 수행 Assembly Inspectors)
            if (building && aqlTests > 0) {
                return 'Building ' + building;
            }

            // 2순위: JSON 매핑 데이터로 Auditor/Trainer/Model Master 분류
            if (window.auditorAreaMapping && empNo) {
                // Model Master 체크 (All Buildings 담당)
                const modelMasters = window.auditorAreaMapping.model_master?.employees || {};
                if (modelMasters[empNo]) {
                    return 'All Buildings';
                }

                // Auditor/Trainer 체크 (Building별 담당)
                const auditorAreas = window.auditorAreaMapping.auditor_trainer_areas || {};
                if (auditorAreas[empNo]) {
                    const config = auditorAreas[empNo];
                    // conditions에서 BUILDING 값 추출
                    for (const condition of (config.conditions || [])) {
                        if (condition.type === 'AND') {
                            for (const filter of (condition.filters || [])) {
                                if (filter.column === 'BUILDING') {
                                    return 'Building ' + filter.value;
                                }
                            }
                        }
                    }
                }
            }

            // Fallback (발생하면 안 됨)
            return 'Unknown';
        }

        // AQL 관련 직원만 필터링 (38employees: 검사자 28employees + Auditor 10명)
        const aqlRelevantEmployees = window.employeeData.filter(isAqlRelevantEmployee);

        // 조건 7번: 팀/구역 AQL 3연속 개월 실패 (AQL 관련 직원 중)
        let cond7FailEmployees = aqlRelevantEmployees.filter(emp => {
            const cond7 = emp['cond_7_aql_team_area'] || 'PASS';
            return cond7 === 'FAIL';
        });

        // 조건 8번: 구역 reject rate > 3% (AQL 관련 직원 중)
        let cond8FailEmployees = aqlRelevantEmployees.filter(emp => {
            const cond8 = emp['cond_8_area_reject'] || 'PASS';
            const areaRejectRate = parseFloat(emp['Area_Reject_Rate'] || 0);
            return cond8 === 'FAIL' || areaRejectRate > 3;
        });

        // 조건별 실패 인원 수 계산
        const cond7FailCount = cond7FailEmployees.length;
        const cond8FailCount = cond8FailEmployees.length;

        // 테이블 2: Assembly Inspector 인원 기준 검사 실적 calculation
        function calculateInspectorStats() {
            // Python에서 AQL file 기준으로 calculation한 data use
            if (window.aqlInspectorStats) {
                return window.aqlInspectorStats;
            }

            // Fallback: Employee CSV 기준 calculation (AQL file data가 없는 경우)
            const inspectorStats = {};

            // Assembly Inspector만 필터 (AQL_Total_Tests > 0)
            const inspectors = window.employeeData.filter(emp =>
                parseFloat(emp['AQL_Total_Tests'] || 0) > 0
            );

            inspectors.forEach(emp => {
                const building = emp['BUILDING'];
                if (!building) return;

                const area = 'Building ' + building;
                const totalTests = parseFloat(emp['AQL_Total_Tests'] || 0);
                const passCount = parseFloat(emp['AQL_Pass_Count'] || 0);
                const failCount = totalTests - passCount;

                if (!inspectorStats[area]) {
                    inspectorStats[area] = {
                        totalInspectors: 0,      // total inspectors count
                        rejectInspectors: 0,     // with Rejects시킨 inspectors count
                        passOnlyInspectors: 0    // Pass만 발생시킨 inspectors count
                    };
                }

                // inspectors count 카운트
                inspectorStats[area].totalInspectors += 1;

                // with Rejects 여부
                if (failCount > 0) {
                    inspectorStats[area].rejectInspectors += 1;
                } else {
                    inspectorStats[area].passOnlyInspectors += 1;
                }
            });

            // 인원 기준 Reject Rate calculation
            Object.keys(inspectorStats).forEach(area => {
                const stats = inspectorStats[area];
                stats.rejectRate = stats.totalInspectors > 0 ?
                    ((stats.rejectInspectors / stats.totalInspectors) * 100).toFixed(1) : '0.0';
            });

            // total 통계
            const totalAll = Object.values(inspectorStats).reduce((sum, s) => sum + s.totalInspectors, 0);
            const rejectAll = Object.values(inspectorStats).reduce((sum, s) => sum + s.rejectInspectors, 0);
            const passAll = Object.values(inspectorStats).reduce((sum, s) => sum + s.passOnlyInspectors, 0);

            inspectorStats['total'] = {
                totalInspectors: totalAll,
                rejectInspectors: rejectAll,
                passOnlyInspectors: passAll,
                rejectRate: totalAll > 0 ? ((rejectAll / totalAll) * 100).toFixed(1) : '0.0'
            };

            return inspectorStats;
        }

        // 테이블 3: Auditor/Trainer incentive 현황 calculation (JSON + CSV 동적 조합)
        function calculateAuditorStats() {
            const auditorStats = [];

            if (!window.auditorAreaMapping) {
                console.warn('Auditor Area Mapping not loaded');
                return auditorStats;
            }

            // Building 순서 정의 (표시 순서: B → D → A → C → All Buildings)
            const buildingOrder = { 'B': 1, 'D': 2, 'A': 3, 'C': 4, 'All': 5 };

            // Auditor/Trainer 수집 (JSON에서)
            const auditorAreas = window.auditorAreaMapping.auditor_trainer_areas || {};
            Object.keys(auditorAreas).forEach(empNo => {
                const config = auditorAreas[empNo];
                const emp = window.employeeData.find(e =>
                    String(e['Employee No']) === empNo ||
                    String(e['emp_no']) === empNo
                );

                if (emp) {
                    // Building 추출
                    let building = 'Unknown';
                    for (const condition of (config.conditions || [])) {
                        if (condition.type === 'AND') {
                            for (const filter of (condition.filters || [])) {
                                if (filter.column === 'BUILDING') {
                                    building = 'Building ' + filter.value;
                                    break;
                                }
                            }
                        }
                    }

                    const areaRate = parseFloat(emp['Area_Reject_Rate'] || 0);
                    const cond7 = emp['cond_7_aql_team_area'] !== 'FAIL';
                    const cond8 = emp['cond_8_area_reject'] !== 'FAIL';

                    auditorStats.push({
                        empNo: empNo,
                        name: config.name || emp['Full Name'],
                        building: building,
                        jobTitle: 'Auditor/Trainer',
                        count: 1,
                        rejectRate: areaRate.toFixed(1),
                        consecutive: 0,
                        cond7: cond7,
                        cond8: cond8,
                        incentiveStatus: cond7 && cond8 ? '지급' : '미지급',
                        sortOrder: buildingOrder[building.replace('Building ', '')] || 99
                    });
                }
            });

            // Model Master 수집 (JSON에서)
            const modelMasters = window.auditorAreaMapping.model_master?.employees || {};
            Object.keys(modelMasters).forEach(empNo => {
                const config = modelMasters[empNo];
                const emp = window.employeeData.find(e =>
                    String(e['Employee No']) === empNo ||
                    String(e['emp_no']) === empNo
                );

                if (emp) {
                    const areaRate = parseFloat(emp['Area_Reject_Rate'] || 0);
                    const cond7 = emp['cond_7_aql_team_area'] !== 'FAIL';
                    const cond8 = emp['cond_8_area_reject'] !== 'FAIL';

                    // Position에서 Job Title 추출
                    const position = String(emp['QIP POSITION 1ST  NAME'] || '').toUpperCase();
                    let jobTitle = 'Model Master';
                    if (position.includes('TEAM LEADER')) {
                        jobTitle = 'Team Leader';
                    }

                    auditorStats.push({
                        empNo: empNo,
                        name: config.name || emp['Full Name'],
                        building: 'All Buildings',
                        jobTitle: jobTitle,
                        count: 1,
                        rejectRate: areaRate.toFixed(1),
                        consecutive: 0,
                        cond7: cond7,
                        cond8: cond8,
                        incentiveStatus: cond7 && cond8 ? '지급' : '미지급',
                        sortOrder: 5  // All Buildings는 마지막
                    });
                }
            });

            // Building 순서대로 정렬
            auditorStats.sort((a, b) => a.sortOrder - b.sortOrder);

            return auditorStats;
        }

        const inspectorStats = calculateInspectorStats();
        const auditorStats = calculateAuditorStats();

        // 번역 텍스트 미리 fetch
        const t = {
            title: getTranslation('aqlModal.title'),
            summaryTitle: getTranslation('aqlModal.summaryTitle'),
            condition7: getTranslation('aqlModal.condition7'),
            condition7Detail: getTranslation('aqlModal.condition7Detail').replace(/0명|0 people|0 người/, cond7FailCount + (currentLanguage === 'ko' ? '명' : currentLanguage === 'en' ? ' people' : ' người')),
            condition8: getTranslation('aqlModal.condition8'),
            condition8Detail: getTranslation('aqlModal.condition8Detail'),
            auditorTrainer: getTranslation('aqlModal.auditorTrainer'),
            tableNote: getTranslation('aqlModal.tableNote'),
            tableNoteDetail: getTranslation('aqlModal.tableNoteDetail'),
            table1Title: getTranslation('aqlModal.table1Title'),
            table2Title: getTranslation('aqlModal.table2Title'),
            table2InspectorTitle: getTranslation('aqlModal.table2InspectorTitle'),
            table3Title: getTranslation('aqlModal.table3Title'),
            table3AuditorTitle: getTranslation('aqlModal.table3AuditorTitle'),
            dataSource: getTranslation('aqlModal.dataSource'),
            aqlFile: getTranslation('aqlModal.aqlFile'),
            building: getTranslation('aqlModal.building'),
            totalTests: getTranslation('aqlModal.totalTests'),
            pass: getTranslation('aqlModal.pass'),
            fail: getTranslation('aqlModal.fail'),
            rejectRate: getTranslation('aqlModal.rejectRate'),
            performanceGrade: getTranslation('aqlModal.performanceGrade'),
            totalInspectors: getTranslation('aqlModal.totalInspectors'),
            rejectInspectors: getTranslation('aqlModal.rejectInspectors'),
            passOnlyInspectors: getTranslation('aqlModal.passOnlyInspectors'),
            personnelRejectRate: getTranslation('aqlModal.personnelRejectRate'),
            jobTitle: getTranslation('aqlModal.jobTitle'),
            responsibleArea: getTranslation('aqlModal.responsibleArea'),
            personnel: getTranslation('aqlModal.personnel'),
            consecutiveMonths: getTranslation('aqlModal.consecutiveMonths'),
            incentiveStatus: getTranslation('aqlModal.incentiveStatus'),
            performanceExcellent: getTranslation('aqlModal.performanceExcellent'),
            performanceGood: getTranslation('aqlModal.performanceGood'),
            performanceWarning: getTranslation('aqlModal.performanceWarning'),
            performanceImprovement: getTranslation('aqlModal.performanceImprovement'),
            paid: getTranslation('aqlModal.paid'),
            notPaid: getTranslation('aqlModal.notPaid'),
            noteTitle: getTranslation('aqlModal.noteTitle'),
            condition7Description: getTranslation('aqlModal.condition7Description'),
            condition8Description: getTranslation('aqlModal.condition8Description'),
            incentiveNote: getTranslation('aqlModal.incentiveNote'),
            unitTests: getTranslation('aqlModal.unitTests'),
            unitPeople: getTranslation('aqlModal.unitPeople'),
            unitYear: getTranslation('aqlModal.unitYear'),
            total: getTranslation('aqlModal.total'),
            allBuildings: getTranslation('aqlModal.allBuildings')
        };

        // Bootstrap 모달 creation 및 표시
        const modalContent = `
            <div class="modal-header unified-modal-header">
                <h5 class="modal-title unified-modal-title">
                    <i class="bi bi-graph-up-arrow"></i>
                    ${t.title}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <div class="alert alert-info">
                        <strong>📊 ${t.summaryTitle}:</strong> ${totalAqlTests}${t.unitTests} (NORMAL PO)<br>
                        <strong>${t.condition7}:</strong> ${t.condition7Detail}<br>
                        <strong>${t.condition8}:</strong> ${t.condition8Detail} ${cond8FailCount}${t.unitPeople} ${t.auditorTrainer}
                    </div>
                    <p><strong>${t.tableNote}:</strong><br><br>${t.tableNoteDetail}</p>
                </div>

                <!-- 테이블 1: Buildingby AQL 검사 실적 (AQL file 기준) -->
                <div class="mb-4">
                    <h6 class="mb-3"><i class="fas fa-chart-bar me-2"></i>📊 ${t.table1Title}</h6>
                    <p class="text-muted small mb-2">${t.dataSource}: ${reportYear}${t.unitYear} ${reportMonthNum}month ${t.aqlFile} ${totalAqlTests}${t.unitTests} (NORMAL PO)</p>
                    <div class="table-responsive">
                        <table class="table table-bordered" style="font-size: 13px;">
                            <thead class="table-light">
                                <tr>
                                    <th style="padding: 10px;">${t.building}</th>
                                    <th style="padding: 10px; text-align: center;">${t.totalTests}</th>
                                    <th style="padding: 10px; text-align: center;">${t.pass}</th>
                                    <th style="padding: 10px; text-align: center;">${t.fail}</th>
                                    <th style="padding: 10px; text-align: center;">${t.rejectRate}</th>
                                    <th style="padding: 10px; text-align: center;">${t.performanceGrade}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${['Building B', 'Building B3', 'Building D', 'Building A', 'Building C', 'All Buildings', 'total'].map(building => {
                                    const stats = aqlFileStats[building];
                                    if (!stats) return '';

                                    const isTotal = building === 'total';
                                    const displayName = isTotal ? t.total : building;
                                    const rejectRate = stats.rejectRate;
                                    let badgeClass = 'bg-success';
                                    let statusText = t.performanceExcellent;

                                    if (rejectRate > 3) {
                                        badgeClass = 'bg-danger';
                                        statusText = t.performanceImprovement;
                                    } else if (rejectRate > 2.5) {
                                        badgeClass = 'bg-warning';
                                        statusText = t.performanceWarning;
                                    } else if (rejectRate > 1.5) {
                                        badgeClass = 'bg-info';
                                        statusText = t.performanceGood;
                                    }

                                    return `
                                        <tr class="${isTotal ? 'table-primary fw-bold' : ''}">
                                            <td style="padding: 8px;">${displayName}</td>
                                            <td style="padding: 8px; text-align: center;"><strong>${stats.total}${t.unitTests}</strong></td>
                                            <td style="padding: 8px; text-align: center;">${stats.pass}${t.unitTests}</td>
                                            <td style="padding: 8px; text-align: center;">${stats.fail}${t.unitTests}</td>
                                            <td style="padding: 8px; text-align: center;">
                                                <span class="badge ${badgeClass}" style="font-size: 13px; padding: 5px 10px;">
                                                    ${stats.rejectRate}%
                                                </span>
                                            </td>
                                            <td style="padding: 8px; text-align: center;">
                                                <span class="badge ${badgeClass}" style="font-size: 12px; padding: 4px 8px;">
                                                    ${statusText}
                                                </span>
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 테이블 2: Assembly Inspector 인력 기준 검사 실적 -->
                <div class="mb-4">
                    <h6 class="mb-3"><i class="fas fa-users me-2"></i>👥 ${t.table2Title}</h6>
                    <p class="text-muted small mb-2">${t.dataSource}: ${t.aqlFile} (${t.total} PO TYPE) - ${t.table2InspectorTitle}</p>
                    <div class="table-responsive">
                        <table class="table table-bordered" style="font-size: 13px;">
                            <thead class="table-light">
                                <tr>
                                    <th style="padding: 10px;">${t.building}</th>
                                    <th style="padding: 10px; text-align: center;">${t.totalInspectors}</th>
                                    <th style="padding: 10px; text-align: center;">${t.rejectInspectors}</th>
                                    <th style="padding: 10px; text-align: center;">${t.passOnlyInspectors}</th>
                                    <th style="padding: 10px; text-align: center;">${t.personnelRejectRate}</th>
                                    <th style="padding: 10px; text-align: center;">${t.performanceGrade}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${['Building B', 'Building B3', 'Building D', 'Building A', 'Building C', 'total'].map(building => {
                                    const stats = inspectorStats[building];
                                    if (!stats) return '';

                                    const isTotal = building === 'total';
                                    const displayName = isTotal ? t.total : building;
                                    const rejectRate = parseFloat(stats.rejectRate);
                                    let badgeClass = 'bg-success';
                                    let statusText = t.performanceExcellent;

                                    if (rejectRate > 3) {
                                        badgeClass = 'bg-danger';
                                        statusText = t.performanceImprovement;
                                    } else if (rejectRate > 2.5) {
                                        badgeClass = 'bg-warning';
                                        statusText = t.performanceWarning;
                                    } else if (rejectRate > 1.5) {
                                        badgeClass = 'bg-info';
                                        statusText = t.performanceGood;
                                    }

                                    return `
                                        <tr class="${isTotal ? 'table-primary fw-bold' : ''}">
                                            <td style="padding: 8px;">${displayName}</td>
                                            <td style="padding: 8px; text-align: center;"><strong>${stats.totalInspectors}${t.unitPeople}</strong></td>
                                            <td style="padding: 8px; text-align: center;">${stats.rejectInspectors}${t.unitPeople}</td>
                                            <td style="padding: 8px; text-align: center;">${stats.passOnlyInspectors}${t.unitPeople}</td>
                                            <td style="padding: 8px; text-align: center;">
                                                <span class="badge ${badgeClass}" style="font-size: 13px; padding: 5px 10px;">
                                                    ${stats.rejectRate}%
                                                </span>
                                            </td>
                                            <td style="padding: 8px; text-align: center;">
                                                <span class="badge ${badgeClass}" style="font-size: 12px; padding: 4px 8px;">
                                                    ${statusText}
                                                </span>
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 테이블 3: Auditor/Trainer incentive 현황 -->
                <div class="mb-4">
                    <h6 class="mb-3">🎯 ${t.table3Title}</h6>
                    <p class="text-muted small mb-2">${t.table3AuditorTitle}</p>
                    <div class="table-responsive">
                        <table class="table table-bordered" style="font-size: 13px;">
                            <thead class="table-light">
                                <tr>
                                    <th style="padding: 10px;">${t.jobTitle}</th>
                                    <th style="padding: 10px;">${t.responsibleArea}</th>
                                    <th style="padding: 10px;">${t.personnel}</th>
                                    <th style="padding: 10px; text-align: center;">${t.rejectRate}</th>
                                    <th style="padding: 10px; text-align: center;">${t.consecutiveMonths}</th>
                                    <th style="padding: 10px; text-align: center;">${t.condition7}</th>
                                    <th style="padding: 10px; text-align: center;">${t.condition8}</th>
                                    <th style="padding: 10px; text-align: center;">${t.incentiveStatus}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${auditorStats.map(stats => {
                                    const isPayment = stats.incentiveStatus === t.paid || stats.incentiveStatus === '지급';
                                    const badgeClass = isPayment ? 'bg-success' : 'bg-danger';
                                    const cond7Badge = stats.cond7 ? '<span class="badge bg-success">✅</span>' : '<span class="badge bg-danger">❌</span>';
                                    const cond8Badge = stats.cond8 ? '<span class="badge bg-success">✅</span>' : '<span class="badge bg-danger">❌</span>';
                                    const statusText = isPayment ? t.paid : t.notPaid;

                                    return `
                                        <tr>
                                            <td style="padding: 8px;">${stats.jobTitle}</td>
                                            <td style="padding: 8px;"><strong>${stats.building}</strong></td>
                                            <td style="padding: 8px;">${stats.name}</td>
                                            <td style="padding: 8px; text-align: center;">
                                                <span class="badge ${parseFloat(stats.rejectRate) > 3 ? 'bg-danger' : 'bg-success'}" style="font-size: 13px;">
                                                    ${stats.rejectRate}%
                                                </span>
                                            </td>
                                            <td style="padding: 8px; text-align: center;">${stats.consecutive}${t.unitPeople}</td>
                                            <td style="padding: 8px; text-align: center;">${cond7Badge}</td>
                                            <td style="padding: 8px; text-align: center;">${cond8Badge}</td>
                                            <td style="padding: 8px; text-align: center;">
                                                <span class="badge ${badgeClass}" style="font-size: 12px; padding: 4px 8px;">
                                                    ${isPayment ? '🟢' : '🔴'} ${statusText}
                                                </span>
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                                ${(() => {
                                    // 테이블 3 Total 행 계산
                                    const totalCount = auditorStats.length;
                                    const paidCount = auditorStats.filter(s => s.incentiveStatus === t.paid || s.incentiveStatus === '지급').length;
                                    const notPaidCount = totalCount - paidCount;
                                    return `
                                        <tr class="table-primary fw-bold">
                                            <td style="padding: 8px;" colspan="2"><strong>${t.total}</strong></td>
                                            <td style="padding: 8px;"><strong>${totalCount}${t.unitPeople}</strong></td>
                                            <td style="padding: 8px; text-align: center;">-</td>
                                            <td style="padding: 8px; text-align: center;">-</td>
                                            <td style="padding: 8px; text-align: center;">-</td>
                                            <td style="padding: 8px; text-align: center;">-</td>
                                            <td style="padding: 8px; text-align: center;">
                                                <span class="badge bg-success" style="font-size: 11px;">🟢${paidCount}</span>
                                                <span class="badge bg-danger" style="font-size: 11px;">🔴${notPaidCount}</span>
                                            </td>
                                        </tr>
                                    `;
                                })()}
                            </tbody>
                        </table>
                    </div>
                    <p class="small text-muted mt-2">
                        <strong>${t.noteTitle}:</strong><br>
                        • ${t.condition7Description}<br>
                        • ${t.condition8Description}<br>
                        • ${t.incentiveNote}
                    </p>
                </div>
            </div>
        </div>
    </div>
            `;

        // Bootstrap 모달 처리
        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;

        // Bootstrap 5 Modal 처리
        const modalElement = document.getElementById('detailModal');

        // existing 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 creation with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',  // 모달 내부 클릭시 닫히지 않도록 설정
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 백드롭 클릭 이벤트 직원시적 처리 (구역 AQL 모달)
        setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.cursor = 'pointer';
                backdrop.addEventListener('click', function(e) {
                    if (e.target === backdrop) {
                        bsModal.hide();
                    }
                });
            }
        }, 100);

        // 모달 닫기 이벤트 리스너 추가
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        });
    }

    // 5PRS 통과율 < 95% 상세 모달
    function showLowPassRateDetails() {
        // 전역 언어와 동기화
        let currentLang = (typeof window.currentLanguage !== 'undefined' ? window.currentLanguage : null) ||
                         (typeof currentLanguage !== 'undefined' ? currentLanguage : null) ||
                         'ko';

        // Load translations
        const t = {
            title: getTranslation('fivePrsModal.title'),
            description: getTranslation('fivePrsModal.description'),
            totalCount: getTranslation('fivePrsModal.totalCount'),
            table1Title: getTranslation('fivePrsModal.table1Title'),
            table2Title: getTranslation('fivePrsModal.table2Title'),
            employeeId: getTranslation('fivePrsModal.employeeId'),
            name: getTranslation('fivePrsModal.name'),
            position: getTranslation('fivePrsModal.position'),
            type: getTranslation('fivePrsModal.type'),
            totalQuantity: getTranslation('fivePrsModal.totalQuantity'),
            passQuantity: getTranslation('fivePrsModal.passQuantity'),
            passRate: getTranslation('fivePrsModal.passRate'),
            conditionStatus: getTranslation('fivePrsModal.conditionStatus'),
            rank: getTranslation('fivePrsModal.rank'),
            unitPcs: getTranslation('fivePrsModal.unitPcs')
        };

        // Move these variables outside so they can be accessed by nested functions
        let allType1Inspectors = [];
        let lowPassEmployees = [];
        let sortColumn = 'passRate';
        let sortOrder = 'asc';
        let sortColumn2 = 'passRate';
        let sortOrder2 = 'asc';
        let modalDiv = null;
        let backdrop = null;

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = column === 'passRate' ? 'asc' : 'desc';
            }
            updateTableBody();
        }

        function sortData2(column) {
            if (sortColumn2 === column) {
                sortOrder2 = sortOrder2 === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn2 = column;
                sortOrder2 = column === 'passRate' ? 'asc' : 'desc';
            }
            updateTableBody2();
        }

        function updateTableBody() {
            const tbody = document.querySelector('#lowPassRateModal tbody');
            if (!tbody) return;

            // 정렬
            lowPassEmployees.sort((a, b) => {
                let aVal, bVal;
                switch (sortColumn) {
                    case 'empNo':
                        aVal = a['Employee No'] || a['emp_no'];
                        bVal = b['Employee No'] || b['emp_no'];
                        break;
                    case 'name':
                        aVal = a['Full Name'] || a['name'];
                        bVal = b['Full Name'] || b['name'];
                        break;
                    case 'position':
                        aVal = a['position'] || a['FINAL QIP POSITION NAME CODE'] || '';
                        bVal = b['position'] || b['FINAL QIP POSITION NAME CODE'] || '';
                        break;
                    case 'totalQty':
                        aVal = parseFloat(a['validation_qty'] || a['5PRS_Inspection_Qty'] || a['5PRS Inspection Quantity'] || 0);
                        bVal = parseFloat(b['validation_qty'] || b['5PRS_Inspection_Qty'] || b['5PRS Inspection Quantity'] || 0);
                        break;
                    case 'passQty':
                        const aPassRate = parseFloat(a['pass_rate'] || a['5PRS_Pass_Rate'] || a['5PRS Pass Rate'] || 0);
                        const aTotalQty = parseFloat(a['validation_qty'] || a['5PRS_Inspection_Qty'] || a['5PRS Inspection Quantity'] || 0);
                        aVal = Math.round(aTotalQty * aPassRate / 100);
                        const bPassRate = parseFloat(b['pass_rate'] || b['5PRS_Pass_Rate'] || b['5PRS Pass Rate'] || 0);
                        const bTotalQty = parseFloat(b['validation_qty'] || b['5PRS_Inspection_Qty'] || b['5PRS Inspection Quantity'] || 0);
                        bVal = Math.round(bTotalQty * bPassRate / 100);
                        break;
                    case 'passRate':
                        aVal = parseFloat(a['pass_rate'] || a['5PRS_Pass_Rate'] || a['5PRS Pass Rate'] || 100);
                        bVal = parseFloat(b['pass_rate'] || b['5PRS_Pass_Rate'] || b['5PRS Pass Rate'] || 100);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }
                return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
            });

            // 테이블 업데이트
            tbody.innerHTML = '';
            lowPassEmployees.forEach(emp => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                const name = emp['Full Name'] || emp['name'];
                const position = emp['position'] || emp['FINAL QIP POSITION NAME CODE'] || '-';
                const totalQty = parseFloat(emp['validation_qty'] || emp['5PRS_Inspection_Qty'] || emp['5PRS Inspection Quantity'] || 0);
                const passRate = parseFloat(emp['pass_rate'] || emp['5PRS_Pass_Rate'] || emp['5PRS Pass Rate'] || 0);
                const passQty = Math.round(totalQty * passRate / 100);

                // Pass Rate에 따른 색상
                let badgeClass = 'bg-danger';
                if (passRate >= 90) badgeClass = 'bg-warning';
                else if (passRate >= 80) badgeClass = 'bg-orange';

                const incentive = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                const received = incentive > 0;

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${empNo}</td>
                    <td>${name}</td>
                    <td>${position}</td>
                    <td>TYPE-1</td>
                    <td>${totalQty.toFixed(0)}${t.unitPcs}</td>
                    <td>${passQty}${t.unitPcs}</td>
                    <td><span class="badge ${badgeClass}">${passRate.toFixed(1)}%</span></td>
                    <td>${passRate < 95 ? t.conditionStatus.split('/')[1] : t.conditionStatus.split('/')[0]}</td>
                    <td class="text-center">${received ? '<span class="badge bg-success">✅</span>' : '<span class="badge bg-secondary">❌</span>'}</td>
                    <td class="text-center">${incentive > 0 ? '<span class="badge bg-info text-dark">' + incentive.toLocaleString() + ' ₫</span>' : '<span class="text-muted">0 ₫</span>'}</td>
                `;
                tbody.appendChild(row);
            });
        }

        function updateTableBody2() {
            const tbody = document.querySelector('#lowPassRateModal2 tbody');
            if (!tbody) return;

            // Get top 10 lowest pass rates from ALL TYPE-1 ASSEMBLY INSPECTORS
            let top10Lowest = [...allType1Inspectors].sort((a, b) => {
                const aRate = parseFloat(a['pass_rate'] || a['5PRS_Pass_Rate'] || a['5PRS Pass Rate'] || 100);
                const bRate = parseFloat(b['pass_rate'] || b['5PRS_Pass_Rate'] || b['5PRS Pass Rate'] || 100);
                return aRate - bRate;
            }).slice(0, 10);

            // Apply secondary sorting
            top10Lowest.sort((a, b) => {
                let aVal, bVal;
                switch (sortColumn2) {
                    case 'empNo':
                        aVal = a['Employee No'] || a['emp_no'];
                        bVal = b['Employee No'] || b['emp_no'];
                        break;
                    case 'name':
                        aVal = a['Full Name'] || a['name'];
                        bVal = b['Full Name'] || b['name'];
                        break;
                    case 'position':
                        aVal = a['position'] || a['FINAL QIP POSITION NAME CODE'] || '';
                        bVal = b['position'] || b['FINAL QIP POSITION NAME CODE'] || '';
                        break;
                    case 'totalQty':
                        aVal = parseFloat(a['validation_qty'] || a['5PRS_Inspection_Qty'] || a['5PRS Inspection Quantity'] || 0);
                        bVal = parseFloat(b['validation_qty'] || b['5PRS_Inspection_Qty'] || b['5PRS Inspection Quantity'] || 0);
                        break;
                    case 'passQty':
                        const aPassRate = parseFloat(a['pass_rate'] || a['5PRS_Pass_Rate'] || a['5PRS Pass Rate'] || 0);
                        const aTotalQty = parseFloat(a['validation_qty'] || a['5PRS_Inspection_Qty'] || a['5PRS Inspection Quantity'] || 0);
                        aVal = Math.round(aTotalQty * aPassRate / 100);
                        const bPassRate = parseFloat(b['pass_rate'] || b['5PRS_Pass_Rate'] || b['5PRS Pass Rate'] || 0);
                        const bTotalQty = parseFloat(b['validation_qty'] || b['5PRS_Inspection_Qty'] || b['5PRS Inspection Quantity'] || 0);
                        bVal = Math.round(bTotalQty * bPassRate / 100);
                        break;
                    case 'passRate':
                        aVal = parseFloat(a['pass_rate'] || a['5PRS_Pass_Rate'] || a['5PRS Pass Rate'] || 100);
                        bVal = parseFloat(b['pass_rate'] || b['5PRS_Pass_Rate'] || b['5PRS Pass Rate'] || 100);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder2 === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }
                return sortOrder2 === 'asc' ? aVal - bVal : bVal - aVal;
            });

            // 테이블 업데이트
            tbody.innerHTML = '';
            top10Lowest.forEach((emp, index) => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                const name = emp['Full Name'] || emp['name'];
                const position = emp['position'] || emp['FINAL QIP POSITION NAME CODE'] || '-';
                const totalQty = parseFloat(emp['validation_qty'] || emp['5PRS_Inspection_Qty'] || emp['5PRS Inspection Quantity'] || 0);
                const passRate = parseFloat(emp['pass_rate'] || emp['5PRS_Pass_Rate'] || emp['5PRS Pass Rate'] || 0);
                const passQty = Math.round(totalQty * passRate / 100);

                // Pass Rate에 따른 색상
                let badgeClass = 'bg-danger';
                if (passRate >= 90) badgeClass = 'bg-warning';
                else if (passRate >= 80) badgeClass = 'bg-orange';

                const incentive = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                const received = incentive > 0;

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${index + 1}</strong></td>
                    <td>${empNo}</td>
                    <td>${name}</td>
                    <td>${position}</td>
                    <td>TYPE-1</td>
                    <td>${totalQty.toFixed(0)}${t.unitPcs}</td>
                    <td>${passQty}${t.unitPcs}</td>
                    <td><span class="badge ${badgeClass}">${passRate.toFixed(1)}%</span></td>
                    <td>${passRate < 95 ? t.conditionStatus.split('/')[1] : t.conditionStatus.split('/')[0]}</td>
                    <td class="text-center">${received ? '<span class="badge bg-success">✅</span>' : '<span class="badge bg-secondary">❌</span>'}</td>
                    <td class="text-center">${incentive > 0 ? '<span class="badge bg-info text-dark">' + incentive.toLocaleString() + ' ₫</span>' : '<span class="text-muted">0 ₫</span>'}</td>
                `;
                tbody.appendChild(row);
            });
        }

        function create5PrsModal() {
            // CRITICAL FIX: Filter data when modal is created, not when function is defined
            console.log('[5PRS Modal] window.employeeData length:', window.employeeData ? window.employeeData.length : 0);

            // TYPE-1 ASSEMBLY INSPECTOR total (position code based)
            // A1A, A1B, A1C = ASSEMBLY INSPECTOR
            allType1Inspectors = (window.employeeData || []).filter(emp => {
                const isType1 = emp['type'] === 'TYPE-1' || emp['ROLE TYPE STD'] === 'TYPE-1';
                // CRITICAL FIX: Use position_code field (FINAL QIP POSITION NAME CODE)
                const positionCode = (emp['position_code'] || '').toUpperCase().trim();
                const isAssemblyInspector = ['A1A', 'A1B', 'A1C'].includes(positionCode);
                // Debug log removed for performance (was causing browser freeze with 400+ employees)
                return isType1 && isAssemblyInspector;
            });

            // TYPE-1 ASSEMBLY INSPECTOR with pass rate < 95% 필터링 (첫 번째 테이블용)
            lowPassEmployees = allType1Inspectors.filter(emp => {
                const passRate = parseFloat(emp['pass_rate'] || emp['5PRS_Pass_Rate'] || emp['5PRS Pass Rate'] || 100);
                // Debug log removed for performance
                return passRate < 95;
            });

            // 백드롭 creation
            backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.style.zIndex = '1040';
            document.body.appendChild(backdrop);

            // 모달 creation
            modalDiv = document.createElement('div');
            modalDiv.className = 'modal fade show d-block';
            modalDiv.style.zIndex = '1050';
            modalDiv.setAttribute('id', 'lowPassRateModal');

            const modalHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                <i class="bi bi-graph-down"></i>
                                ${t.title}
                            </h5>
                            <button type="button" class="btn-close" onclick="window.closeLowPassRateModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <div class="alert alert-warning">
                                    <strong>${t.description}</strong>
                                </div>
                                <p>${t.totalCount.replace('{count}', lowPassEmployees.length)}</p>
                            </div>

                            <!-- Table 1: All 직원 with pass rate < 95% -->
                            <h6 class="mb-3">${t.table1Title}</h6>
                            <div class="table-responsive mb-4">
                                <table class="table table-hover">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th class="sortable-header" data-sort="empNo">${t.employeeId} ${getSortIcon('empNo')}</th>
                                            <th class="sortable-header" data-sort="name">${t.name} ${getSortIcon('name')}</th>
                                            <th class="sortable-header" data-sort="position">${t.position} ${getSortIcon('position')}</th>
                                            <th>${t.type}</th>
                                            <th class="sortable-header" data-sort="totalQty">${t.totalQuantity} ${getSortIcon('totalQty')}</th>
                                            <th class="sortable-header" data-sort="passQty">${t.passQuantity} ${getSortIcon('passQty')}</th>
                                            <th class="sortable-header" data-sort="passRate">${t.passRate} ${getSortIcon('passRate')}</th>
                                            <th>${t.conditionStatus.split('/')[2]}</th>
                                            <th class="sortable-header" data-sort="received">${currentLang === 'ko' ? '수령' : currentLang === 'en' ? 'Received' : 'Nhận'}</th>
                                            <th class="sortable-header" data-sort="incentive">${currentLang === 'ko' ? '인센티브' : currentLang === 'en' ? 'Incentive' : 'Thưởng'}</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>

                            <!-- Table 2: Top 10 lowest pass rates -->
                            <h6 class="mb-3">${t.table2Title}</h6>
                            <div class="table-responsive">
                                <table class="table table-hover" id="lowPassRateModal2">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th>${t.rank}</th>
                                            <th class="sortable-header-2" data-sort="empNo">${t.employeeId} ${getSortIcon2('empNo')}</th>
                                            <th class="sortable-header-2" data-sort="name">${t.name} ${getSortIcon2('name')}</th>
                                            <th class="sortable-header-2" data-sort="position">${t.position} ${getSortIcon2('position')}</th>
                                            <th>${t.type}</th>
                                            <th class="sortable-header-2" data-sort="totalQty">${t.totalQuantity} ${getSortIcon2('totalQty')}</th>
                                            <th class="sortable-header-2" data-sort="passQty">${t.passQuantity} ${getSortIcon2('passQty')}</th>
                                            <th class="sortable-header-2" data-sort="passRate">${t.passRate} ${getSortIcon2('passRate')}</th>
                                            <th>${t.conditionStatus.split('/')[2]}</th>
                                            <th class="sortable-header-2" data-sort="received">${currentLang === 'ko' ? '수령' : currentLang === 'en' ? 'Received' : 'Nhận'}</th>
                                            <th class="sortable-header-2" data-sort="incentive">${currentLang === 'ko' ? '인센티브' : currentLang === 'en' ? 'Incentive' : 'Thưởng'}</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            modalDiv.innerHTML = modalHTML;
            document.body.appendChild(modalDiv);
            document.body.classList.add('modal-open');

            // 정렬 이벤트 추가 - Table 1
            modalDiv.querySelectorAll('.sortable-header').forEach(header => {
                header.addEventListener('click', function() {
                    const column = this.getAttribute('data-sort');
                    sortData(column);

                    // 헤더 업데이트
                    modalDiv.querySelectorAll('.sortable-header').forEach(h => {
                        const col = h.getAttribute('data-sort');
                        const icon = getSortIcon(col);
                        const text = h.textContent.replace(/[▲▼]/g, '').trim();
                        h.innerHTML = text + ' ' + icon;
                    });
                });
            });

            // 정렬 이벤트 추가 - Table 2
            modalDiv.querySelectorAll('.sortable-header-2').forEach(header => {
                header.addEventListener('click', function() {
                    const column = this.getAttribute('data-sort');
                    sortData2(column);

                    // 헤더 업데이트
                    modalDiv.querySelectorAll('.sortable-header-2').forEach(h => {
                        const col = h.getAttribute('data-sort');
                        const icon = getSortIcon2(col);
                        const text = h.textContent.replace(/[▲▼]/g, '').trim();
                        h.innerHTML = text + ' ' + icon;
                    });
                });
            });

            // 초기 data load
            updateTableBody();
            updateTableBody2();

            // 닫기 함count
            window.closeLowPassRateModal = function() {
                if (modalDiv) {
                    modalDiv.remove();
                    modalDiv = null;
                }
                if (backdrop) {
                    backdrop.remove();
                    backdrop = null;
                }
                document.body.classList.remove('modal-open');
                window.closeLowPassRateModal = null;
            };

            // 백드롭 클릭으로 닫기
            backdrop.onclick = function(e) {
                if (e.target === backdrop) {
                    window.closeLowPassRateModal();
                }
            };

            // 모달 내부 클릭 시 이벤트 전파 중단
            modalDiv.querySelector('.modal-content').onclick = function(e) {
                e.stopPropagation();
            };
        }

        function getSortIcon(column) {
            if (sortColumn !== column) return '';
            return sortOrder === 'asc' ? '▲' : '▼';
        }

        function getSortIcon2(column) {
            if (sortColumn2 !== column) return '';
            return sortOrder2 === 'asc' ? '▲' : '▼';
        }

        create5PrsModal();
    }

    // 5PRS 검사량 < 100족 상세 모달
    function showLowInspectionQtyDetails() {
        // CRITICAL FIX: 5PRS data file에 actual로 있는 직원만 표시
        // TYPE-1 ASSEMBLY INSPECTOR with inspection qty < 100 필터링
        let lowQtyEmployees = window.employeeData.filter(emp => {
            const isType1 = emp['type'] === 'TYPE-1' || emp['ROLE TYPE STD'] === 'TYPE-1';
            const positionCode = (emp['position_code'] || '').toUpperCase().trim();
            const isAssemblyInspector = ['A1A', 'A1B', 'A1C'].includes(positionCode);

            // CRITICAL: validation_qty가 actual로 존재하고(NaN 아님) 100 미만인 경우만
            const hasValidationData = emp['validation_qty'] !== null &&
                                     emp['validation_qty'] !== undefined &&
                                     emp['validation_qty'] !== '' &&
                                     !isNaN(parseFloat(emp['validation_qty']));
            const inspectionQty = hasValidationData ? parseFloat(emp['validation_qty']) : 999999;

            return isType1 && isAssemblyInspector && hasValidationData && inspectionQty < 100;
        });

        let sortColumn = 'inspectionQty';
        let sortOrder = 'asc';
        let modalDiv = null;
        let backdrop = null;

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = column === 'inspectionQty' ? 'asc' : 'desc';
            }
            updateTableBody();
        }

        function updateTableBody() {
            const tbody = document.querySelector('#lowInspectionQtyModal tbody');
            if (!tbody) return;

            // 정렬
            lowQtyEmployees.sort((a, b) => {
                let aVal, bVal;
                switch (sortColumn) {
                    case 'empNo':
                        aVal = a['Employee No'] || a['emp_no'];
                        bVal = b['Employee No'] || b['emp_no'];
                        break;
                    case 'name':
                        aVal = a['Full Name'] || a['name'];
                        bVal = b['Full Name'] || b['name'];
                        break;
                    case 'position':
                        aVal = a['position'] || a['FINAL QIP POSITION NAME CODE'] || '';
                        bVal = b['position'] || b['FINAL QIP POSITION NAME CODE'] || '';
                        break;
                    case 'inspectionQty':
                        aVal = parseFloat(a['validation_qty'] || a['5PRS Inspection Quantity'] || 0);
                        bVal = parseFloat(b['validation_qty'] || b['5PRS Inspection Quantity'] || 0);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }
                return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
            });

            // 테이블 업데이트
            tbody.innerHTML = '';
            lowQtyEmployees.forEach(emp => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                const name = emp['Full Name'] || emp['name'];
                const position = emp['position'] || emp['FINAL QIP POSITION NAME CODE'] || '-';
                const inspectionQty = Math.round(parseFloat(emp['validation_qty'] || emp['5PRS Inspection Quantity'] || 0));

                // Inspection Qty에 따른 색상 및 텍스트 색상
                // 0-49족: 빨간색 (심각), 50-79족: 주황색 (주의), 80-99족: 노란색 (경고)
                let badgeClass = 'bg-danger text-white';
                if (inspectionQty >= 80) {
                    badgeClass = 'bg-warning text-dark';
                } else if (inspectionQty >= 50) {
                    badgeClass = 'bg-orange text-white';
                }

                // 언어별 단위 및 상태 텍스트
                const qtyUnit = currentLanguage === 'ko' ? '족' : currentLanguage === 'en' ? ' prs' : ' đôi';
                const statusText = inspectionQty < 100 ?
                    (currentLanguage === 'ko' ? '미충족' : currentLanguage === 'en' ? 'Not Met' : 'Không đạt') :
                    (currentLanguage === 'ko' ? '충족' : currentLanguage === 'en' ? 'Met' : 'Đạt');

                const row = document.createElement('tr');
                row.style.cursor = 'pointer';
                row.onclick = function(e) {
                    e.stopPropagation();
                    showInlineDetail(emp, this);
                };
                const incentive = parseFloat(emp['incentive'] || emp['November_Incentive'] || emp['final_incentive'] || 0);
                const received = incentive > 0;

                row.innerHTML = `
                    <td>${empNo}</td>
                    <td>${name}</td>
                    <td>${position}</td>
                    <td>TYPE-1</td>
                    <td><span class="badge ${badgeClass}">${inspectionQty}${qtyUnit}</span></td>
                    <td>${statusText}</td>
                    <td class="text-center">${received ? '<span class="badge bg-success">✅</span>' : '<span class="badge bg-secondary">❌</span>'}</td>
                    <td class="text-center">${incentive > 0 ? '<span class="badge bg-info text-dark">' + incentive.toLocaleString() + ' ₫</span>' : '<span class="text-muted">0 ₫</span>'}</td>
                `;
                tbody.appendChild(row);
            });
        }

        // 인라인 상세 팝업 표시 함수 (Added 2025-11-30)
        function showInlineDetail(emp, rowElement) {
            // 기존 팝업 제거
            closeInlineDetail();

            const lang = currentLanguage || 'ko';

            // 다국어 라벨
            const labels = {
                ko: {
                    title: '직원 상세 정보',
                    entranceDate: '입사일',
                    stopDate: '퇴사일',
                    actualDays: '실제 근무일',
                    status: '상태',
                    normal: '정상 근무',
                    resigned: '퇴사',
                    maternity: '출산휴가',
                    days: '일',
                    none: '-',
                    clickHint: '행을 클릭하면 상세정보를 볼 수 있습니다'
                },
                en: {
                    title: 'Employee Details',
                    entranceDate: 'Entrance Date',
                    stopDate: 'Stop Date',
                    actualDays: 'Actual Working Days',
                    status: 'Status',
                    normal: 'Active',
                    resigned: 'Resigned',
                    maternity: 'Maternity Leave',
                    days: ' days',
                    none: '-',
                    clickHint: 'Click row to see details'
                },
                vi: {
                    title: 'Chi tiết nhân viên',
                    entranceDate: 'Ngày vào làm',
                    stopDate: 'Ngày nghỉ việc',
                    actualDays: 'Ngày làm thực tế',
                    status: 'Trạng thái',
                    normal: 'Đang làm',
                    resigned: 'Đã nghỉ',
                    maternity: 'Nghỉ thai sản',
                    days: ' ngày',
                    none: '-',
                    clickHint: 'Nhấp hàng để xem chi tiết'
                }
            };
            const t = labels[lang] || labels.ko;

            // 직원 데이터 추출
            const entranceDate = emp['Entrance Date'] || emp['entrance_date'] || t.none;
            const stopDate = emp['Stop working Date'] || emp['stop_working_date'] || t.none;
            const actualDays = emp['Actual Working Days'] || emp['actual_working_days'] || emp['Actual_Working_Days'] || 0;

            // 상태 결정
            let status = t.normal;
            let statusClass = 'status-normal';
            const pregnant = (emp['Pregnant vacation'] || emp['pregnant_vacation'] || emp['Display Pregnant Women'] || '').toString().toLowerCase();
            const remark = (emp['Remark'] || emp['remark'] || emp['RE MARK'] || '').toString().toLowerCase();

            if (stopDate && stopDate !== t.none && stopDate !== '-') {
                status = t.resigned;
                statusClass = 'status-resigned';
            } else if (pregnant === 'yes' || pregnant === 'thai san' || remark.includes('maternity') || remark.includes('출산') || remark.includes('thai san')) {
                status = t.maternity;
                statusClass = 'status-maternity';
            }

            // 팝업 HTML 생성
            const popupHTML = `
                <div id="inlineDetailPopup" class="inline-detail-popup">
                    <div class="popup-header">
                        <h6><i class="fas fa-user me-2"></i>${t.title}</h6>
                        <button class="popup-close" onclick="closeInlineDetail()">&times;</button>
                    </div>
                    <div class="popup-body">
                        <div class="detail-item">
                            <span class="detail-label">${t.entranceDate}</span>
                            <span class="detail-value">${entranceDate}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">${t.stopDate}</span>
                            <span class="detail-value">${stopDate}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">${t.actualDays}</span>
                            <span class="detail-value">${actualDays}${t.days}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">${t.status}</span>
                            <span class="detail-value">
                                <span class="status-badge ${statusClass}">${status}</span>
                            </span>
                        </div>
                    </div>
                </div>
            `;

            // 팝업 추가
            const modalBody = document.querySelector('#lowInspectionQtyModal .modal-body');
            if (!modalBody) return;

            modalBody.style.position = 'relative';
            modalBody.insertAdjacentHTML('beforeend', popupHTML);

            // 팝업 위치 계산
            const popup = document.getElementById('inlineDetailPopup');
            const rowRect = rowElement.getBoundingClientRect();
            const modalRect = modalBody.getBoundingClientRect();

            // 모달 바디 기준 상대 위치
            let topPos = rowRect.top - modalRect.top + modalBody.scrollTop + rowElement.offsetHeight + 5;
            let leftPos = rowRect.left - modalRect.left + 50;

            // 화면 경계 체크
            if (leftPos + popup.offsetWidth > modalBody.offsetWidth) {
                leftPos = modalBody.offsetWidth - popup.offsetWidth - 20;
            }
            if (leftPos < 10) leftPos = 10;

            popup.style.top = topPos + 'px';
            popup.style.left = leftPos + 'px';
        }

        // 인라인 팝업 닫기 (글로벌 함수로 등록)
        window.closeInlineDetail = function() {
            const popup = document.getElementById('inlineDetailPopup');
            if (popup) {
                popup.remove();
            }
        };
        function closeInlineDetail() {
            window.closeInlineDetail();
        }

        function createInspectionModal() {
            // Get current language
            const lang = currentLanguage || 'ko';
            const t = (key) => getTranslation(key, lang);

            // 백드롭 creation
            backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.style.zIndex = '1040';
            document.body.appendChild(backdrop);

            // 모달 creation
            modalDiv = document.createElement('div');
            modalDiv.className = 'modal fade show d-block';
            modalDiv.style.zIndex = '1050';
            modalDiv.setAttribute('id', 'lowInspectionQtyModal');

            const countText = t('validationTab.modals.lowInspectionQty.count').replace('{count}', lowQtyEmployees.length);

            const modalHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title" data-i18n="validationTab.modals.lowInspectionQty.title">
                                <i class="bi bi-search"></i>
                                ${t('validationTab.modals.lowInspectionQty.title')}
                            </h5>
                            <button type="button" class="btn-close" onclick="window.closeLowInspectionQtyModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <div class="alert alert-warning" data-i18n="validationTab.modals.lowInspectionQty.alert">
                                    ${t('validationTab.modals.lowInspectionQty.alert')}
                                </div>
                                <p data-i18n="validationTab.modals.lowInspectionQty.count">${countText}</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th class="sortable-header" data-sort="empNo" data-i18n="validationTab.modals.lowInspectionQty.headers.empNo">${t('validationTab.modals.lowInspectionQty.headers.empNo')} ${getSortIcon('empNo')}</th>
                                            <th class="sortable-header" data-sort="name" data-i18n="validationTab.modals.lowInspectionQty.headers.name">${t('validationTab.modals.lowInspectionQty.headers.name')} ${getSortIcon('name')}</th>
                                            <th class="sortable-header" data-sort="position" data-i18n="validationTab.modals.lowInspectionQty.headers.position">${t('validationTab.modals.lowInspectionQty.headers.position')} ${getSortIcon('position')}</th>
                                            <th data-i18n="validationTab.modals.lowInspectionQty.headers.type">${t('validationTab.modals.lowInspectionQty.headers.type')}</th>
                                            <th class="sortable-header" data-sort="inspectionQty" data-i18n="validationTab.modals.lowInspectionQty.headers.inspectionQty">${t('validationTab.modals.lowInspectionQty.headers.inspectionQty')} ${getSortIcon('inspectionQty')}</th>
                                            <th data-i18n="validationTab.modals.lowInspectionQty.headers.conditionMet">${t('validationTab.modals.lowInspectionQty.headers.conditionMet')}</th>
                                            <th class="sortable-header" data-sort="received">${currentLanguage === 'ko' ? '수령' : currentLanguage === 'en' ? 'Received' : 'Nhận'}</th>
                                            <th class="sortable-header" data-sort="incentive">${currentLanguage === 'ko' ? '인센티브' : currentLanguage === 'en' ? 'Incentive' : 'Thưởng'}</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            modalDiv.innerHTML = modalHTML;
            document.body.appendChild(modalDiv);
            document.body.classList.add('modal-open');

            // 정렬 이벤트 추가
            modalDiv.querySelectorAll('.sortable-header').forEach(header => {
                header.addEventListener('click', function() {
                    const column = this.getAttribute('data-sort');
                    sortData(column);

                    // 헤더 업데이트
                    modalDiv.querySelectorAll('.sortable-header').forEach(h => {
                        const col = h.getAttribute('data-sort');
                        const icon = getSortIcon(col);
                        h.innerHTML = h.textContent.replace(/[▲▼]/g, '').trim() + ' ' + icon;
                    });
                });
            });

            // 초기 data load
            updateTableBody();

            // 닫기 함count
            window.closeLowInspectionQtyModal = function() {
                if (modalDiv) {
                    modalDiv.remove();
                    modalDiv = null;
                }
                if (backdrop) {
                    backdrop.remove();
                    backdrop = null;
                }
                document.body.classList.remove('modal-open');
                window.closeLowInspectionQtyModal = null;
            };

            // 백드롭 클릭으로 닫기
            backdrop.onclick = function(e) {
                if (e.target === backdrop) {
                    window.closeLowInspectionQtyModal();
                }
            };

            // 모달 내부 클릭 시 이벤트 전파 중단
            modalDiv.querySelector('.modal-content').onclick = function(e) {
                e.stopPropagation();
            };
        }

        function getSortIcon(column) {
            if (sortColumn !== column) return '';
            return sortOrder === 'asc' ? '▲' : '▼';
        }

        createInspectionModal();
    }
    """

    # Replace month_num placeholder
    modal_scripts = modal_scripts.replace('MONTH_NUM_PLACEHOLDER', str(month_num))

    # 모달 CSS 추가
    modal_styles = """
    /* 통th된 모달 스타th */
    .unified-modal-header {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
        border-bottom: 3px solid #2196f3 !important;
        padding: 1.2rem 1.5rem !important;
        border-radius: 0.5rem 0.5rem 0 0 !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;  /* 중앙 정렬 유지 */
        position: relative !important;  /* 닫기 버튼 절대 위치 기준 */
    }
    /* 닫기 버튼을 우측 상단에 절대 위치로 고정 */
    .unified-modal-header .btn-close {
        position: absolute !important;
        top: 1rem !important;
        right: 1.5rem !important;
    }
    /* AQL Fail 모달의 버튼 그룹 내 닫기 버튼도 동th하게 처리 */
    .unified-modal-header .d-flex {
        margin-right: 3rem !important;  /* 닫기 버튼 공간 확보 */
    }
    .unified-modal-header .d-flex .btn-close {
        position: absolute !important;
        top: 1rem !important;
        right: 1.5rem !important;
    }
    .unified-modal-title {
        color: #1565c0 !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        flex: 1 !important;  /* 타이틀이 available 공간 모두 차지 */
        margin-right: 3rem !important;  /* 닫기 버튼 공간 확보 */
    }
    .unified-modal-content {
        padding: 1.5rem !important;
    }
    .unified-summary-section {
        display: flex !important;
        justify-content: space-around !important;
        padding: 1.5rem !important;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef) !important;
        border-radius: 10px !important;
        margin-bottom: 1.5rem !important;
    }
    .unified-stat-item {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    .unified-stat-label {
        color: #6c757d !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
    }
    .unified-stat-value {
        color: #1565c0 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    .unified-info-card {
        padding: 1.25rem !important;
        border-radius: 10px !important;
        margin-bottom: 1rem !important;
    }
    .unified-section-title {
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.75rem !important;
        color: #495057 !important;
    }
    .unified-list-content {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    .unified-action-buttons {
        display: flex !important;
        justify-content: center !important;
        gap: 0.75rem !important;
        margin-top: 1.5rem !important;
    }
    .unified-table-header {
        background: #f5f5f5 !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 10 !important;
    }
    .unified-table-header th {
        padding: 12px !important;
        font-weight: 700 !important;
        color: #424242 !important;
        border-bottom: 2px solid #e0e0e0 !important;
        white-space: nowrap !important;
    }
    .unified-table-row {
        transition: all 0.3s ease !important;
    }
    .unified-table-row:hover {
        transform: translateX(5px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        background-color: #f8f9fa !important;
    }
    .sortable-header {
        cursor: pointer !important;
        user-select: none !important;
        position: relative !important;
        padding-right: 25px !important;
    }
    .sortable-header:hover {
        background: #e9ecef !important;
    }
    .sortable-header::after {
        content: '⇅' !important;
        position: absolute !important;
        right: 8px !important;
        opacity: 0.3 !important;
        font-size: 12px !important;
    }
    .sortable-header.asc::after {
        content: '▲' !important;
        opacity: 1 !important;
    }
    .sortable-header.desc::after {
        content: '▼' !important;
        opacity: 1 !important;
    }

    /* 5PRS 인라인 상세 팝업 스타일 (Added 2025-11-30) */
    .inline-detail-popup {
        position: absolute;
        background: white;
        border: 2px solid #2196f3;
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        padding: 15px;
        z-index: 1100;
        min-width: 300px;
        max-width: 380px;
    }
    .inline-detail-popup .popup-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }
    .inline-detail-popup .popup-header h6 {
        margin: 0;
        color: #1565c0;
        font-weight: bold;
        font-size: 1rem;
    }
    .inline-detail-popup .popup-close {
        background: none;
        border: none;
        font-size: 22px;
        cursor: pointer;
        color: #666;
        padding: 0;
        line-height: 1;
    }
    .inline-detail-popup .popup-close:hover {
        color: #c62828;
    }
    .inline-detail-popup .detail-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .inline-detail-popup .detail-item:last-child {
        border-bottom: none;
    }
    .inline-detail-popup .detail-label {
        color: #666;
        font-weight: 500;
    }
    .inline-detail-popup .detail-value {
        color: #333;
        font-weight: 600;
    }
    .inline-detail-popup .status-badge {
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 600;
    }
    .inline-detail-popup .status-maternity {
        background: #e3f2fd;
        color: #1565c0;
    }
    .inline-detail-popup .status-resigned {
        background: #ffebee;
        color: #c62828;
    }
    .inline-detail-popup .status-normal {
        background: #e8f5e9;
        color: #2e7d32;
    }
    /* 행 클릭 가능 표시 */
    #lowInspectionQtyModal tbody tr {
        cursor: pointer;
        transition: background-color 0.2s;
    }
    #lowInspectionQtyModal tbody tr:hover {
        background-color: #e3f2fd !important;
    }

    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-top: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
    }
    .calendar-day {
        min-height: 100px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        padding: 8px;
        transition: all 0.2s ease;
        position: relative;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .calendar-day:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .calendar-day.work-day {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border: none;
    }
    .calendar-day.no-data {
        background: #f8f9fa;
        color: #495057;
        border: 2px dashed #dee2e6;
    }
    .day-number {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 2px;
        line-height: 1;
    }
    .day-weekday {
        font-size: 0.75rem;
        font-weight: 500;
        opacity: 0.85;
        margin-bottom: 4px;
        letter-spacing: -0.3px;
    }
    .day-icon {
        font-size: 1.2rem;
        margin: 4px 0;
    }
    .attendance-count {
        font-size: 0.85rem !important;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        margin-top: 3px;
    }
    .calendar-day.work-day .attendance-count {
        background: rgba(255,255,255,0.25);
        color: white !important;
    }
    .calendar-day.no-data .attendance-count {
        background: rgba(220, 53, 69, 0.1);
        color: #dc3545 !important;
        font-size: 0.75rem !important;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 3px;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .calendar-day.no-data .attendance-count i {
        font-size: 0.65rem;
        color: #dc3545;
    }
    .calendar-day.no-data .attendance-count span {
        color: #495057 !important;
    }
    .legend-badge {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 2px solid;
    }
    .legend-badge.legend-workday {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white !important;
        border-color: #ef4444;
    }
    .legend-badge.legend-nodata {
        background: #f8f9fa;
        color: #212529 !important;
        border-color: #dee2e6;
        border-style: dashed;
    }
    .stat-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        transition: all 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.12);
    }
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .stat-label {
        color: #495057;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .stat-value {
        color: #212529;
        font-weight: 700;
    }
    """

    # Continue HTML content with modal scripts included
    html_content += f'''
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        /* Universal font for better Unicode support */
        * {{
            font-family: 'Noto Sans KR', 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji' !important;
        }}

        body {{
            background: #f5f5f5;
            font-family: 'Noto Sans KR', 'Noto Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .summary-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        
        .summary-card h6 {{
            color: #6b7280;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .summary-card h2 {{
            color: #1f2937;
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .summary-card .unit {{
            font-size: 1rem;
            color: #9ca3af;
            font-weight: 400;
            margin-left: 4px;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            background: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .tab {{
            padding: 12px 24px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
            font-weight: 500;
            color: #6b7280;
        }}
        
        .tab:hover {{
            background: #f3f4f6;
        }}
        
        .tab.active {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }}
        
        .tab-content {{
            display: none;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .table {{
            margin-top: 20px;
        }}
        
        .table thead th {{
            background: #f9fafb;
            color: #374151;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb;
            padding: 12px;
        }}
        
        .type-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            white-space: nowrap;
            display: inline-block;
        }}
        
        .type-badge.type-1 {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .type-badge.type-2 {{
            background: #fce7f3;
            color: #be185d;
        }}
        
        .type-badge.type-3 {{
            background: #d1fae5;
            color: #047857;
        }}
        
        /* Talent Pool 강조 스타th */
        @keyframes starPulse {{
            0% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.2); opacity: 0.8; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
        
        .talent-pool-row {{
            background: linear-gradient(90deg, #fff9e6 0%, #fffdf5 50%, #fff9e6 100%);
            animation: goldShimmer 3s ease-in-out infinite;
            position: relative;
        }}
        
        @keyframes goldShimmer {{
            0% {{ background: linear-gradient(90deg, #fff9e6 0%, #fffdf5 50%, #fff9e6 100%); }}
            50% {{ background: linear-gradient(90deg, #fffdf5 0%, #fff9e6 50%, #fffdf5 100%); }}
            100% {{ background: linear-gradient(90deg, #fff9e6 0%, #fffdf5 50%, #fff9e6 100%); }}
        }}
        
        .talent-pool-row:hover {{
            background: linear-gradient(90deg, #fff3cc 0%, #fff9e6 50%, #fff3cc 100%);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
            transform: translateX(2px);
            transition: all 0.3s ease;
        }}
        
        .talent-pool-star {{
            display: inline-block;
            animation: starPulse 2s ease-in-out infinite;
            font-size: 1.2em;
        }}
        
        .talent-pool-badge {{
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            display: inline-block;
            margin-left: 8px;
            box-shadow: 0 2px 4px rgba(255, 165, 0, 0.3);
        }}
        
        .talent-pool-tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
        }}
        
        .talent-pool-tooltip .tooltiptext {{
            visibility: hidden;
            width: 250px;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: white;
            text-align: center;
            border-radius: 8px;
            padding: 10px;
            position: absolute;
            z-index: 1001;
            bottom: 125%;
            left: 50%;
            margin-left: -125px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.875rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .talent-pool-tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        
        .talent-pool-tooltip .tooltiptext::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #FFA500 transparent transparent transparent;
        }}

        /* report type 알림 */
        .report-type-banner {{
            background: {'linear-gradient(135deg, #FFA500 0%, #FFD700 100%)' if is_interim_report else 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'};
            color: white;
            padding: 15px 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: slideDown 0.5s ease-out;
        }}

        .report-type-banner .icon {{
            font-size: 1.5rem;
            margin-right: 10px;
        }}

        .report-type-banner .message {{
            flex-grow: 1;
        }}

        .report-type-banner .title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 3px;
        }}

        .report-type-banner .description {{
            font-size: 0.9rem;
            opacity: 0.95;
        }}

        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            overflow: hidden; /* 모달 배경 스크롤 방지 */
        }}

        /* 최소 근무일 모달 가독성 개선 스타th */
        #minimumDaysTable {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }}

        #minimumDaysTable thead th {{
            background-color: #f8f9fa;
            font-weight: 600;
            font-size: 13px;
            padding: 12px 8px;
            white-space: nowrap;
            border-bottom: 2px solid #dee2e6;
        }}

        #minimumDaysTable tbody tr {{
            transition: background-color 0.2s;
        }}

        #minimumDaysTable tbody tr:hover {{
            background-color: #f8f9fa;
        }}

        #minimumDaysTable .badge {{
            font-weight: 500;
            letter-spacing: 0.5px;
        }}

        /* 진행률 색상 개선 */
        .badge.bg-danger {{
            background-color: #dc3545 !important;
        }}

        .badge.bg-warning {{
            background-color: #ffc107 !important;
            color: #000 !important;
        }}

        .badge.bg-info {{
            background-color: #0dcaf0 !important;
            color: #000 !important;
        }}

        .badge.bg-primary {{
            background-color: #0d6efd !important;
        }}

        .badge.bg-success {{
            background-color: #198754 !important;
        }}

        .badge.bg-orange {{
            background-color: #fd7e14 !important;
            color: #fff !important;
        }}
        
        .modal-content {{
            background: white;
            margin: 30px auto; /* 상단 여백 줄임 */
            padding: 0;
            width: 95%;
            max-width: 1100px;
            border-radius: 12px;
            height: 85vh; /* 고정 높이 */
            max-height: 85vh; /* 최대 높이 */
            display: flex;
            flex-direction: column;
            overflow: hidden; /* 오버플로우 방지 */
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }}
        
        /* 팝업 내 통계 카드 */
        .stat-card {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 15px;
        }}
        
        .stat-card .stat-value {{
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .stat-label {{
            font-size: 0.875rem;
            opacity: 0.9;
        }}
        
        /* 지급 상태 스타th */
        .지급-status {{
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            height: 100%;
        }}
        
        .지급-status.paid {{
            background: #d4edda;
            color: #155724;
        }}
        
        .지급-status.unpaid {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .지급-status i {{
            font-size: 3rem;
            margin-bottom: 10px;
            display: block;
        }}
        
        /* 조건 테이블 스타th */
        .table-success {{
            background-color: #d4edda !important;
        }}
        
        .table-danger {{
            background-color: #f8d7da !important;
        }}
        
        .info-group {{
            margin-bottom: 15px;
        }}
        
        .info-group label {{
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
            display: block;
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px 12px 0 0;
            flex: 0 0 auto; /* 고정 높이 */
            min-height: 60px;
            max-height: 60px;
        }}
        
        .modal-body {{
            padding: 30px;
            overflow-y: auto !important; /* 본문만 스크롤 */
            overflow-x: hidden; /* 가로 스크롤 방지 */
            max-height: 70vh !important; /* 최대 높이 설정으로 스크롤 활성화 */
            flex: 1 1 auto; /* 유연한 크기 */
            min-height: 0; /* flexbox 버그 방지 */
            max-height: calc(85vh - 120px); /* 헤더 공간 뺄고 높이 제한 */
        }}
        
        .close {{
            color: white;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close:hover {{
            opacity: 0.8;
        }}
        
        .condition-group {{
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
        }}
        
        .condition-group-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 15px;
            padding: 8px 12px;
            border-radius: 6px;
            color: white;
        }}
        
        .condition-group-title.attendance {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        }}
        
        .condition-group-title.aql {{
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        }}
        
        .condition-group-title.prs {{
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        }}
        
        .condition-check {{
            padding: 12px 15px;
            margin-bottom: 8px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            border: 1px solid #e5e7eb;
        }}
        
        .condition-check.success {{
            background: #d1fae5;
            border-color: #10b981;
        }}
        
        .condition-check.fail {{
            background: #fee2e2;
            border-color: #ef4444;
        }}
        
        .version-badge {{
            background: #fbbf24;
            color: #78350f;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        /* Type 요약 테이블 스타th */
        .avg-header {{
            text-align: center;
            background: #f3f4f6;
        }}
        
        .sub-header {{
            font-size: 0.9em;
            font-weight: 500;
            background: #f9fafb;
        }}

        /* 모달 관련 스타th count정 */
        #incentiveModal {{
            z-index: 1055 !important;
        }}

        #incentiveModal .modal-dialog {{
            z-index: 1056 !important;
        }}

        #incentiveModal .modal-content {{
            z-index: 1057 !important;
            position: relative !important;
            background: white !important;
            user-select: text !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
        }}

        #incentiveModal .modal-content * {{
            user-select: text !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
        }}

        .modal-backdrop {{
            z-index: 1040 !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
        }}

        #detailModal {{
            z-index: 1050 !important;
        }}

        #detailModal .modal-dialog {{
            z-index: 1051 !important;
        }}

        #detailModal .modal-content {{
            z-index: 1052 !important;
        }}

        #detailModal .modal-header {{
            position: relative;
            z-index: 1053 !important;
        }}

        #detailModal .btn-close {{
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            z-index: 1054 !important;
            opacity: 1;
            cursor: pointer;
        }}

        #detailModal .btn-close-white::after {{
            content: '×';
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }}

        .modal.show .modal-dialog {{
            z-index: 1056 !important;
        }}

        /* 새로운 접이식 조직도 스타th */
        .collapsible-tree {{
            padding: 30px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .collapsible-tree ul {{
            position: relative;
            padding: 20px 0 0 30px;
            margin: 0;
            list-style: none;
        }}

        .collapsible-tree li {{
            position: relative;
            padding: 15px 0;
        }}

        /* 연결선 스타th */
        .collapsible-tree li::before {{
            content: '';
            position: absolute;
            left: -30px;
            top: 0;
            border-left: 2px solid #ef4444;
            height: 100%;
        }}

        .collapsible-tree li::after {{
            content: '';
            position: absolute;
            left: -30px;
            top: 40px;
            width: 30px;
            border-top: 2px solid #ef4444;
        }}

        .collapsible-tree li:last-child::before {{
            height: 40px;
        }}

        .collapsible-tree li.no-children::before,
        .collapsible-tree li.no-children::after {{
            display: none;
        }}

        /* 노드 카드 스타th */
        .org-node {{
            display: inline-block;
            padding: 15px 20px;
            background: white;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            position: relative;
            min-width: 200px;
            border-left: 4px solid;
        }}

        .org-node:hover {{
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}

        /* 직급별 색상 - 모던하고 세련된 색상 */
        .org-node.manager {{
            border-left-color: #6366f1;
            background: linear-gradient(135deg, #ffffff 0%, #eef2ff 100%);
        }}

        .org-node.supervisor {{
            border-left-color: #8b5cf6;
            background: linear-gradient(135deg, #ffffff 0%, #f3e8ff 100%);
        }}

        .org-node.group-leader {{
            border-left-color: #ec4899;
            background: linear-gradient(135deg, #ffffff 0%, #fce7f3 100%);
        }}

        .org-node.line-leader {{
            border-left-color: #f59e0b;
            background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%);
        }}

        .org-node.inspector {{
            border-left-color: #10b981;
            background: linear-gradient(135deg, #ffffff 0%, #d1fae5 100%);
        }}

        .org-node.default {{
            border-left-color: #6b7280;
            background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
        }}

        /* incentive 여부 표시 */
        .org-node.has-incentive {{
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
        }}

        .org-node.no-incentive {{
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
        }}

        /* 노드 내용 스타th */
        .node-position {{
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}

        .node-name {{
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 3px;
        }}

        .node-id {{
            font-size: 11px;
            color: #9ca3af;
        }}

        /* incentive 정보 스타th - 개선된 version */
        .node-incentive-info {{
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px dashed transparent;
            border-radius: 6px;
            padding: 6px;
        }}

        .node-incentive-info:hover {{
            background: rgba(99, 102, 241, 0.2);
            border: 2px dashed #6366f1;
            border-radius: 6px;
            padding: 6px;
            transform: scale(1.02);
            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
        }}

        .incentive-amount {{
            font-size: 14px;
            font-weight: 700;
            color: #059669;
            margin-right: 8px;
        }}

        .incentive-detail-btn {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            min-width: 30px;
            min-height: 30px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
            position: relative;
        }}

        .incentive-detail-btn:hover {{
            transform: scale(1.2);
            box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        }}

        .incentive-info-icon {{
            font-size: 16px;
            color: #6366f1;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }}

        .incentive-info-icon:hover {{
            opacity: 1;
        }}

        .node-incentive {{
            position: absolute;
            top: 8px;
            right: 8px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}

        .node-incentive.received {{
            background-color: #22c55e;
            box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
        }}

        .node-incentive.not-received {{
            background-color: #ef4444;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
        }}

        /* 접기/펼치기 버튼 */
        .toggle-btn {{
            position: absolute;
            right: -30px;
            top: 50%;
            transform: translateY(-50%);
            width: 24px;
            height: 24px;
            background: white;
            border: 2px solid #ef4444;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 16px;
            color: #ef4444;
            font-weight: bold;
            transition: all 0.3s;
            z-index: 10;
        }}

        .toggle-btn:hover {{
            background: #ef4444;
            color: white;
            transform: translateY(-50%) scale(1.1);
        }}

        /* 자식 count 표시 */
        .child-count {{
            background: #ef4444;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            margin-left: 8px;
            font-size: 11px;
            font-weight: 600;
        }}

        /* 접힌 상태 */
        .collapsed > ul {{
            display: none;
        }}

        .collapsed .toggle-btn::after {{
            content: '+';
        }}

        /* 검색 및 필터 컨트롤 */
        .org-controls {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .org-header {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .org-header h4 {{
            color: #1f2937;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .org-header p {{
            color: #6b7280;
            font-size: 14px;
        }}

        /* 범례 스타th */
        .org-legend {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .org-legend h6 {{
            color: #374151;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .legend-items {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .legend-item {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
            color: #4b5563;
        }}

        .legend-box {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}

        .legend-dot {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid;
        }}

        .legend-dot.received {{
            border-color: #10b981;
            background: #10b981;
        }}

        .legend-dot.not-received {{
            border-color: #ef4444;
            background: transparent;
        }}

        /* 검색 하이라이트 */
        .search-hidden {{
            opacity: 0.2;
            filter: grayscale(100%);
        }}

        .search-highlight {{
            background: #fef08a !important;
            border-color: #facc15 !important;
            animation: pulse 1s infinite;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}

        /* 로딩 스피너 */
        .org-loading {{
            text-align: center;
            padding: 50px;
        }}

        .org-loading-spinner {{
            border: 4px solid #f3f4f6;
            border-top: 4px solid #6366f1;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .expanded .toggle-btn::after {{
            content: '−';
        }}

        /* 조직도 통계 패널 */
        .org-stats-panel {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-top: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}

        .org-stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}

        .org-stat-item {{
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            border-radius: 10px;
            color: white;
        }}

        .org-stat-number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .org-stat-label {{
            font-size: 12px;
            opacity: 0.9;
        }}

        /* 로딩 상태 */
        .org-loading {{
            display: flex;
            align-items: center;
            justify-content: center;
            height: 400px;
            color: #6b7280;
        }}

        .org-loading-spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid #e5e7eb;
            border-top-color: #ef4444;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            to {{
                transform: rotate(360deg);
            }}
        }}

        /* Modal Styles for improved validation modals */
        {modal_styles}

        /* Position Modal 전용 스타th - 스크롤 및 클릭 문제 해결 */
        #positionModal {{
            z-index: 1050 !important;
        }}
        #positionModal .modal-dialog {{
            max-width: 90% !important;
            margin: 1.75rem auto !important;
            z-index: 1051 !important;
            pointer-events: auto !important;
        }}
        #positionModal .modal-content {{
            z-index: 1052 !important;
            position: relative !important;
            pointer-events: auto !important;
            background: white !important;
        }}
        #positionModal .modal-body {{
            max-height: 70vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            pointer-events: auto !important;
            position: relative !important;
        }}
        #positionModal .modal-body * {{
            pointer-events: auto !important;
        }}
        #positionModal .btn-close,
        #positionModal button {{
            pointer-events: auto !important;
            cursor: pointer !important;
        }}

        /* Employee Modal 전용 스타th */
        #employeeModal {{
            z-index: 1060 !important;
        }}
        #employeeModal .modal-dialog {{
            max-width: 80% !important;
            margin: 1.75rem auto !important;
            z-index: 1061 !important;
        }}
        #employeeModal .modal-body {{
            max-height: 70vh !important;
            overflow-y: auto !important;
        }}

        /* ================================================== */
        /* Mobile Mode Styles (User-Selected View)            */
        /* Activated by body.mobile-mode class                */
        /* ================================================== */

        /* Tab Navigation: Vertical stacked */
        body.mobile-mode .tabs {{
            display: flex !important;
            flex-direction: column !important;
            gap: 8px !important;
        }}

        body.mobile-mode .tab {{
            width: 100% !important;
            text-align: center !important;
            padding: 16px !important;
            font-size: 1.1rem !important;
            border-radius: 12px !important;
            justify-content: center !important;
        }}

        /* Summary Cards: Single column */
        body.mobile-mode .row.mb-4 > [class*="col-md-3"] {{
            flex: 0 0 100% !important;
            max-width: 100% !important;
            margin-bottom: 15px !important;
        }}

        body.mobile-mode .summary-card {{
            padding: 20px !important;
        }}

        /* Filter Controls: Stack vertically */
        body.mobile-mode .filter-container .row {{
            flex-direction: column !important;
        }}

        body.mobile-mode .filter-container [class*="col-md-"] {{
            flex: 0 0 100% !important;
            max-width: 100% !important;
            margin-bottom: 10px !important;
        }}

        /* Tables: Hide table, show card view */
        body.mobile-mode .table-wrapper,
        body.mobile-mode .table-responsive {{
            display: none !important;
        }}

        body.mobile-mode .card-view-wrapper {{
            display: block !important;
        }}

        /* Default: Show table, hide card view */
        .card-view-wrapper {{
            display: none;
        }}

        /* Employee Card Styles */
        .employee-card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #28a745;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .employee-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }}

        .employee-card:active {{
            transform: scale(0.98);
        }}

        .employee-card.unpaid {{
            border-left-color: #dc3545;
        }}

        .employee-card .emp-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}

        .employee-card .emp-name {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #212529;
            flex: 1;
        }}

        .employee-card .emp-info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.95rem;
        }}

        .employee-card .emp-info-row:last-child {{
            border-bottom: none;
        }}

        .employee-card .emp-label {{
            color: #6c757d;
        }}

        .employee-card .emp-value {{
            font-weight: 600;
            color: #212529;
        }}

        .employee-card .incentive-amount {{
            font-size: 1.15rem;
            font-weight: 700;
        }}

        .employee-card .incentive-amount.paid {{
            color: #28a745;
        }}

        .employee-card .incentive-amount.unpaid {{
            color: #dc3545;
        }}

        /* Chart containers: Reduced height in mobile mode */
        body.mobile-mode .chart-container {{
            height: 220px !important;
        }}

        /* Organization Chart Mobile: Card-based list */
        body.mobile-mode #orgChartSvg {{
            display: none !important;
        }}

        body.mobile-mode .mobile-org-list {{
            display: flex !important;
            flex-direction: column;
            gap: 12px;
        }}

        .mobile-org-list {{
            display: none;
        }}

        .org-manager-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #6c757d;
        }}

        .org-manager-card.paid {{
            border-left-color: #28a745;
        }}

        .org-manager-card.unpaid {{
            border-left-color: #dc3545;
        }}

        .org-card-header {{
            padding: 16px;
            background: #f8f9fa;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .org-card-header:active {{
            background: #e9ecef;
        }}

        .org-card-info {{
            flex: 1;
        }}

        .org-card-name {{
            font-weight: 700;
            font-size: 1.1rem;
            color: #212529;
        }}

        .org-card-position {{
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 4px;
        }}

        .org-card-incentive {{
            font-weight: 700;
            font-size: 1rem;
            text-align: right;
        }}

        .org-card-incentive.paid {{
            color: #28a745;
        }}

        .org-card-incentive.unpaid {{
            color: #dc3545;
        }}

        .org-card-toggle {{
            font-size: 1.2rem;
            color: #6c757d;
            transition: transform 0.3s ease;
        }}

        .org-manager-card.expanded .org-card-toggle {{
            transform: rotate(180deg);
        }}

        .org-subordinates {{
            padding: 0;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, padding 0.3s ease;
            background: white;
        }}

        .org-manager-card.expanded .org-subordinates {{
            max-height: 2000px;
            padding: 12px;
        }}

        .org-subordinate-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-size: 0.95rem;
            cursor: pointer;
        }}

        .org-subordinate-item:last-child {{
            border-bottom: none;
        }}

        .org-subordinate-item:active {{
            background: #f8f9fa;
        }}

        .org-subordinate-name {{
            flex: 1;
            font-weight: 500;
        }}

        .org-subordinate-amount {{
            font-weight: 600;
        }}

        .org-subordinate-amount.paid {{
            color: #28a745;
        }}

        .org-subordinate-amount.unpaid {{
            color: #dc3545;
        }}

        /* View Mode Toggle Button in Dashboard Header */
        .view-mode-toggle {{
            display: flex;
            gap: 5px;
            background: rgba(255, 255, 255, 0.2);
            padding: 4px;
            border-radius: 20px;
            margin-left: 10px;
        }}

        .view-mode-btn {{
            padding: 6px 12px;
            border: none;
            background: transparent;
            color: white;
            font-size: 0.85rem;
            font-weight: 600;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            opacity: 0.7;
        }}

        .view-mode-btn:hover {{
            opacity: 1;
        }}

        .view-mode-btn.active {{
            background: white;
            color: #ef4444;
            opacity: 1;
        }}

        /* 모바일 반응형 최적화 */
        @media (max-width: 768px) {{
            /* 컨테이너 여백 조정 */
            .container {{
                padding: 15px !important;
            }}

            /* 헤더 크기 조정 */
            .header h1 {{
                font-size: 2rem !important;
                line-height: 1.3 !important;
            }}

            /* 통계 카드 그리드 조정 */
            .stats-grid {{
                grid-template-columns: 1fr !important;
                gap: 15px !important;
            }}

            .stat-card {{
                padding: 24px !important;
            }}

            .stat-card h4 {{
                font-size: 1.2rem !important;
            }}

            .stat-card .stat-value {{
                font-size: 2rem !important;
            }}

            /* 테이블 스크롤 컨테이너 */
            .table-responsive {{
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
                margin: 10px -15px !important;
                padding: 0 15px !important;
            }}

            /* 테이블 최소 너비 설정 */
            .table {{
                min-width: 900px !important;
                font-size: 1.05rem !important;
            }}

            .table thead th {{
                padding: 14px 10px !important;
                font-size: 1rem !important;
                white-space: nowrap !important;
            }}

            .table tbody td {{
                padding: 14px 10px !important;
                font-size: 1rem !important;
            }}

            /* TYPE 배지 크기 조정 */
            .type-badge {{
                font-size: 0.9rem !important;
                padding: 5px 12px !important;
            }}

            /* 탭 버튼 조정 */
            .tab-button {{
                padding: 14px 18px !important;
                font-size: 1.05rem !important;
                min-height: 50px !important;
            }}

            /* 차트 컨테이너 높이 조정 */
            .chart-container {{
                height: 300px !important;
                margin-bottom: 20px !important;
            }}

            /* 모달 전체 화면 스타일 - 모든 모달에 적용 */
            #employeeModal .modal-dialog,
            #positionModal .modal-dialog,
            #incentiveModal .modal-dialog,
            #detailModal .modal-dialog,
            .modal-dialog {{
                max-width: 100% !important;
                margin: 0 !important;
                height: 100vh !important;
                width: 100vw !important;
            }}

            #employeeModal .modal-content,
            #positionModal .modal-content,
            #incentiveModal .modal-content,
            #detailModal .modal-content,
            .modal-content {{
                height: 100vh !important;
                border-radius: 0 !important;
                display: flex !important;
                flex-direction: column !important;
            }}

            #employeeModal .modal-header,
            #positionModal .modal-header,
            #incentiveModal .modal-header,
            #detailModal .modal-header,
            .modal-header {{
                padding: 20px !important;
                flex-shrink: 0 !important;
            }}

            #employeeModal .modal-title,
            #positionModal .modal-title,
            #incentiveModal .modal-title,
            #detailModal .modal-title,
            .modal-title {{
                font-size: 1.4rem !important;
                font-weight: 600 !important;
            }}

            #employeeModal .modal-body,
            #positionModal .modal-body,
            #incentiveModal .modal-body,
            #detailModal .modal-body,
            .modal-body {{
                padding: 20px !important;
                font-size: 1.1rem !important;
                overflow-y: auto !important;
                flex: 1 !important;
                -webkit-overflow-scrolling: touch !important;
            }}

            #employeeModal .modal-body h6,
            #positionModal .modal-body h6,
            .modal-body h6 {{
                font-size: 1.25rem !important;
                margin-bottom: 15px !important;
            }}

            #employeeModal .modal-body .table,
            #positionModal .modal-body .table,
            .modal-body .table {{
                font-size: 1rem !important;
                min-width: 100% !important;
            }}

            #employeeModal .modal-body .table td,
            #employeeModal .modal-body .table th,
            #positionModal .modal-body .table td,
            #positionModal .modal-body .table th,
            .modal-body .table td,
            .modal-body .table th {{
                padding: 12px 8px !important;
                font-size: 1rem !important;
            }}

            #employeeModal .modal-footer,
            #positionModal .modal-footer,
            .modal-footer {{
                padding: 20px !important;
                flex-shrink: 0 !important;
            }}

            #employeeModal .modal-footer .btn,
            #positionModal .modal-footer .btn,
            .modal-footer .btn {{
                min-width: 120px !important;
                padding: 14px 28px !important;
                font-size: 1.2rem !important;
                min-height: 54px !important;
                font-weight: 600 !important;
            }}

            /* Talent Pool 카드 조정 */
            .talent-pool-card {{
                padding: 24px !important;
            }}

            .talent-pool-card h4 {{
                font-size: 1.3rem !important;
            }}

            .talent-pool-card h3 {{
                font-size: 2.2rem !important;
            }}

            /* 버튼 크기 조정 - 터치 타겟 최소 48px */
            .btn {{
                padding: 14px 22px !important;
                font-size: 1.05rem !important;
                min-height: 48px !important;
            }}

            .btn-lg {{
                padding: 16px 32px !important;
                font-size: 1.2rem !important;
                min-height: 54px !important;
            }}

            /* 언어 선택기 조정 */
            .lang-btn {{
                padding: 12px 16px !important;
                font-size: 1rem !important;
                min-height: 44px !important;
            }}

            /* 카드 조정 */
            .card {{
                margin-bottom: 24px !important;
            }}

            .card-header h5 {{
                font-size: 1.3rem !important;
            }}

            .card-body {{
                padding: 24px !important;
            }}

            /* 탭 컨테이너 조정 */
            .tabs {{
                gap: 8px !important;
                margin-bottom: 20px !important;
            }}

            .tab {{
                padding: 14px 18px !important;
                font-size: 1.05rem !important;
                min-height: 50px !important;
            }}

            /* 보기 버튼들 크기 증가 */
            .view-details-btn {{
                padding: 10px 18px !important;
                font-size: 1rem !important;
                min-height: 44px !important;
            }}
        }}

        /* 작은 모바일 기기 (320px - 480px) - 매우 공격적인 스타일 */
        @media (max-width: 480px) {{
            /* 헤더 조정 */
            .header h1 {{
                font-size: 1.6rem !important;
                padding-top: 15px !important;
            }}

            .container {{
                padding: 12px !important;
                padding-top: 70px !important;
            }}

            /* 언어/대시보드 선택기 */
            #languageSelector,
            #dashboardSelector {{
                font-size: 0.95rem !important;
                padding: 10px !important;
                min-height: 44px !important;
            }}

            /* 테이블 스타일 */
            .table {{
                font-size: 1rem !important;
                min-width: 750px !important;
            }}

            .table thead th,
            .table tbody td {{
                padding: 12px 8px !important;
                font-size: 1rem !important;
            }}

            /* 차트 컨테이너 */
            .chart-container {{
                height: 250px !important;
                margin-bottom: 20px !important;
            }}

            /* 탭 버튼 */
            .tab-button,
            .tab {{
                padding: 12px 14px !important;
                font-size: 1rem !important;
                min-height: 48px !important;
            }}

            /* 통계 카드 */
            .stat-card {{
                padding: 18px !important;
            }}

            .stat-card .stat-value {{
                font-size: 1.8rem !important;
            }}

            /* 모달 스타일 - 전체 화면 유지 */
            #employeeModal .modal-dialog,
            #positionModal .modal-dialog,
            #incentiveModal .modal-dialog,
            #detailModal .modal-dialog,
            .modal-dialog {{
                max-width: 100% !important;
                margin: 0 !important;
                height: 100vh !important;
                width: 100vw !important;
            }}

            #employeeModal .modal-content,
            #positionModal .modal-content,
            #incentiveModal .modal-content,
            #detailModal .modal-content,
            .modal-content {{
                height: 100vh !important;
                border-radius: 0 !important;
            }}

            #employeeModal .modal-header,
            #positionModal .modal-header,
            .modal-header {{
                padding: 18px !important;
            }}

            #employeeModal .modal-title,
            #positionModal .modal-title,
            .modal-title {{
                font-size: 1.3rem !important;
                font-weight: 600 !important;
            }}

            #employeeModal .modal-body,
            #positionModal .modal-body,
            .modal-body {{
                padding: 18px !important;
                font-size: 1.05rem !important;
            }}

            #employeeModal .modal-body h6,
            #positionModal .modal-body h6,
            .modal-body h6 {{
                font-size: 1.2rem !important;
                margin-bottom: 12px !important;
            }}

            #employeeModal .modal-body .table,
            #positionModal .modal-body .table,
            .modal-body .table {{
                font-size: 0.95rem !important;
            }}

            #employeeModal .modal-body .table td,
            #employeeModal .modal-body .table th,
            #positionModal .modal-body .table td,
            #positionModal .modal-body .table th,
            .modal-body .table td,
            .modal-body .table th {{
                padding: 10px 6px !important;
                font-size: 0.95rem !important;
            }}

            #employeeModal .modal-footer,
            #positionModal .modal-footer,
            .modal-footer {{
                padding: 18px !important;
            }}

            #employeeModal .modal-footer .btn,
            #positionModal .modal-footer .btn,
            .modal-footer .btn {{
                padding: 14px 24px !important;
                font-size: 1.1rem !important;
                min-height: 50px !important;
            }}

            /* 버튼 크기 */
            .btn {{
                padding: 12px 20px !important;
                font-size: 1rem !important;
                min-height: 46px !important;
            }}

            .btn-lg {{
                padding: 14px 28px !important;
                font-size: 1.1rem !important;
                min-height: 50px !important;
            }}

            /* 카드 스타일 */
            .card {{
                margin-bottom: 20px !important;
            }}

            .card-header h5 {{
                font-size: 1.2rem !important;
            }}

            .card-body {{
                padding: 20px !important;
            }}

            /* 보기 버튼 */
            .view-details-btn {{
                padding: 10px 16px !important;
                font-size: 0.95rem !important;
                min-height: 44px !important;
            }}

            /* Talent Pool 카드 */
            .talent-pool-card {{
                padding: 20px !important;
            }}

            .talent-pool-card h4 {{
                font-size: 1.2rem !important;
            }}

            .talent-pool-card h3 {{
                font-size: 2rem !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="position: absolute; top: 20px; right: 20px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; max-width: 600px;">
                <select id="languageSelector" class="form-select" onchange="changeLanguage(this.value)" style="width: 150px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3);">
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                    <option value="vi">Tiếng Việt</option>
                </select>
                <select id="dashboardSelector" class="form-select" onchange="changeDashboard(this.value)" style="width: 200px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3);">
                    <option value="incentive">💰 Incentive Dashboard</option>
                    <option value="management">📊 Management Dashboard</option>
                    <option value="statistics">📈 Statistics Dashboard</option>
                </select>
                <button id="viewModeToggle" onclick="toggleViewMode()" class="btn btn-sm view-mode-toggle" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); white-space: nowrap;">
                    <span id="viewModeToggleText">📱 모바일 뷰</span>
                </button>
                <button id="downloadHtmlBtn" onclick="downloadDashboard()" class="btn btn-sm" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); white-space: nowrap;">
                    <span id="downloadHtmlBtnText">📦 Offline 버전</span>
                </button>
                <button id="downloadExcelBtn" onclick="downloadExcel()" class="btn btn-sm" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); white-space: nowrap;">
                    <span id="downloadExcelBtnText">📗 Excel 다운로드</span>
                </button>
            </div>
            <h1 id="mainTitle">QIP 인센티브 계산 결과 <span class="version-badge">V9.0</span></h1>
            <p id="mainSubtitle" data-year="{year}" data-month="{month}" data-month-name="{get_korean_month(month)}">{year}년 {get_korean_month(month)} 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;" data-year="{current_year}" data-month="{current_month:02d}" data-day="{current_day:02d}" data-hour="{current_hour:02d}" data-minute="{current_minute:02d}">보고서 생성일: {current_year}년 {current_month:02d}월 {current_day:02d}일 {current_hour:02d}:{current_minute:02d}</p>

            <!-- 데이터 신선도 인디케이터 -->
            <div id="dataFreshnessBadge" style="display: inline-flex; align-items: center; gap: 12px; margin-top: 15px; padding: 12px 20px; border-radius: 8px; font-size: 0.95em; font-weight: 500; background: rgba(255,255,255,0.95); color: #333; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <span id="freshnessIcon" style="font-size: 1.5em;"></span>
                <div style="display: flex; flex-direction: column; gap: 3px;">
                    <span id="freshnessText" style="font-weight: 600; color: #333;"></span>
                    <span id="freshnessDetail" style="font-size: 0.85em; color: #666;"></span>
                </div>
            </div>

            <div id="dataPeriodSection" style="color: white; font-size: 0.85em; margin-top: 15px; opacity: 0.85; line-height: 1.6;">
                <p id="dataPeriodTitle" style="margin: 5px 0; font-weight: bold;">📊 사용 데이터 기간:</p>
                <p id="incentiveDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{incentive_start_str}" data-endday="{incentive_end_str}">• 인센티브 데이터: {year}년 {month_num:02d}월 {incentive_start_str}일 ~ {incentive_end_str}일</p>
                <p id="attendanceDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{attendance_start_str}" data-endday="{attendance_end_str}">• 출근 데이터: {year}년 {month_num:02d}월 {attendance_start_str}일 ~ {attendance_end_str}일</p>
                <p id="aqlDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{aql_start_str}" data-endday="{aql_end_str}">• AQL 데이터: {year}년 {month_num:02d}월 {aql_start_str}일 ~ {aql_end_str}일</p>
                <p id="5prsDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{prs_start_str}" data-endday="{prs_end_str}">• 5PRS 데이터: {year}년 {month_num:02d}월 {prs_start_str}일 ~ {prs_end_str}일</p>
                <p id="manpowerDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}">• 기본 인력 데이터: {year}년 {month_num:02d}월 기준</p>
            </div>
        </div>

        <!-- report type 알림 배너 -->
        <div class="report-type-banner" id="reportTypeBanner">
            <div style="display: flex; align-items: center;">
                <span class="icon">{'⚠️' if is_interim_report else '✅'}</span>
                <div class="message">
                    <div class="title" id="reportTypeTitle">{'중간 보고서' if is_interim_report else '최종 보고서'}</div>
                    <div class="description" id="reportTypeDesc">
                        {'이 보고서는 월중 점검용 중간 보고서입니다. 최소 근무일(12일) 및 결근율(12%) 조건이 적용되지 않습니다.' if is_interim_report else '이 보고서는 월말 최종 보고서입니다. 모든 인센티브 조건이 정상적으로 적용됩니다.'}
                    </div>
                </div>
            </div>
            <div>
                <span style="font-size: 0.85rem; opacity: 0.9;">생성일: {current_day}일</span>
            </div>
        </div>

        <div class="content p-4">
            <!-- 요약 카드 -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalEmployeesLabel">전체 직원</h6>
                        <h2><span id="totalEmployeesValue">{total_직원}</span> <span class="unit" id="totalEmployeesUnit"></span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paidEmployeesLabel">수령 직원</h6>
                        <h2><span id="paidEmployeesValue">{paid_직원}</span> <span class="unit" id="paidEmployeesUnit"></span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paymentRateLabel">지급률</h6>
                        <h2 id="paymentRateValue">{지급_rate:.1f}%</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalAmountLabel">총 지급액</h6>
                        <h2 id="totalAmountValue">{total_amount:,} VND</h2>
                    </div>
                </div>
            </div>
            
            
            <!-- 탭 메뉴 -->
            <div class="tabs">
                <div class="tab active" data-tab="summary" onclick="showTab('summary')" id="tabSummary">요약</div>
                <div class="tab" data-tab="position" onclick="showTab('position')" id="tabPosition" data-translate-tab="position">직급별 상세</div>
                <div class="tab" data-tab="detail" onclick="showTab('detail')" id="tabIndividual" data-translate-tab="individual">개인별 상세</div>
                <div class="tab" data-tab="criteria" onclick="showTab('criteria')" id="tabCriteria" data-translate-tab="criteria">인센티브 기준</div>
                <div class="tab" data-tab="orgchart" onclick="showTab('orgchart')" id="tabOrgChart">조직도</div>
                <div class="tab" data-tab="validation" onclick="showTab('validation')" id="tabValidation">요약 및 시스템 검증</div>
            </div>
            
            <!-- 요약 탭 -->
            <div id="summary" class="tab-content active">
                <h3 id="summaryTabTitle" data-translate="typeSummary">Type별 현황</h3>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th rowspan="2" id="summaryTypeHeader">Type</th>
                                <th rowspan="2" id="summaryTotalHeader">전체 인원</th>
                                <th rowspan="2" id="summaryEligibleHeader">수령 인원</th>
                                <th rowspan="2" id="summaryPaymentRateHeader">지급률</th>
                                <th rowspan="2" id="summaryTotalAmountHeader">총 지급액</th>
                                <th colspan="2" class="avg-header" id="summaryAvgAmountHeader">평균 지급액</th>
                            </tr>
                            <tr>
                                <th class="sub-header" id="summaryAvgEligibleHeader" data-translate="avgPaymentPaidBasis">수령인원 기준</th>
                                <th class="sub-header" id="summaryAvgTotalHeader" data-translate="avgPaymentTotalBasis">전체인원 기준</th>
                            </tr>
                        </thead>
                        <tbody id="typeSummaryBody">
                            <!-- JavaScript로 동적으로 채워질 예정 -->'''
    
    html_content += f'''
                    </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 직급별 상세 탭 -->
            <div id="position" class="tab-content">
                <h3 id="positionTabTitle" data-translate="positionDetails">직급별 상세 현황</h3>
                <div id="positionTables">
                    <!-- JavaScript로 채워질 예정 -->
                </div>
                
                <!-- Talent Pool 시각화 섹션 -->
                <div class="row mb-4" id="talentPoolSection" style="display: none;">
                    <div class="col-12">
                        <div class="card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white;">
                            <div class="card-body">
                                <h4 class="mb-3" id="talentPoolTitle">🌟 QIP Talent Pool 특별 incentive</h4>
                                <div class="row">
                                    <div class="col-md-3">
                                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                                            <h6 style="opacity: 0.9;" id="talentPoolMemberCountLabel">Talent Pool 인원</h6>
                                            <h3 id="talentPoolCount">0명</h3>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                                            <h6 style="opacity: 0.9;" id="talentPoolMonthlyBonusLabel">월 보너스 금액</h6>
                                            <h3 id="talentPoolMonthlyBonus">0 VND</h3>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                                            <h6 style="opacity: 0.9;" id="talentPoolTotalBonusLabel">total 보너스 지급액</h6>
                                            <h3 id="talentPoolTotalBonus">0 VND</h3>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                                            <h6 style="opacity: 0.9;" id="talentPoolPaymentPeriodLabel">지급 기간</h6>
                                            <h3 id="talentPoolPeriod">-</h3>
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-3" id="talentPoolMembers">
                                    <!-- Talent Pool 멤버 목록이 여기에 표시됩니다 -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 개인별 상세 탭 -->
            <div id="detail" class="tab-content">
                <h3 id="individualDetailTitle" data-translate="individualDetails">개인별 상세 정보</h3>
                <div class="filter-container mb-3">
                    <div class="row">
                        <div class="col-md-3">
                            <input type="text" id="searchInput" class="form-control" 
                                placeholder="이름 또는 직원번호 검색" onkeyup="filterTable()">
                        </div>
                        <div class="col-md-2">
                            <select id="typeFilter" class="form-select" 
                                onchange="updatePositionFilter(); filterTable()">
                                <option value="" id="optAllTypes">모든 Type</option>
                                <option value="TYPE-1">TYPE-1</option>
                                <option value="TYPE-2">TYPE-2</option>
                                <option value="TYPE-3">TYPE-3</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select id="positionFilter" class="form-select" onchange="filterTable()">
                                <option value="" id="optAllPositions">모든 직급</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <select id="paymentFilter" class="form-select" onchange="filterTable()">
                                <option value="" id="optPaymentAll">total</option>
                                <option value="paid" id="optPaymentPaid">지급</option>
                                <option value="unpaid" id="optPaymentUnpaid">미지급</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="employeeTable">
                        <thead>
                            <tr>
                                <th id="empIdHeader">사번</th>
                                <th id="nameHeader">이름</th>
                                <th id="positionHeader">직급</th>
                                <th id="typeHeader">Type</th>
                                <th id="prevMonthHeader">{get_korean_month(prev_month_name)}</th>
                                <th id="currentMonthHeader">{get_korean_month(month)}</th>
                                <th id="talentPoolHeader">Talent Pool</th>
                                <th id="statusHeader">상태</th>
                                <th id="detailsHeader">상세</th>
                            </tr>
                        </thead>
                        <tbody id="employeeTableBody">
                            <!-- JavaScript로 채워질 예정 -->
                        </tbody>
                    </table>
                </div>

                <!-- 모바일 카드 뷰 컨테이너 (모바일 모드에서만 표시) -->
                <div id="employeeCardView" class="card-view-wrapper">
                    <!-- JavaScript에서 동적으로 생성됨 -->
                </div>
            </div>

            <!-- incentive 기준 탭 -->
            <div id="criteria" class="tab-content">
                <h1 class="section-title" style="text-align: center; font-size: 28px; margin-bottom: 30px;" id="criteriaMainTitle">
                    QIP incentive 정책 및 calculation 기준
                </h1>
                
                <!-- 정책 요약 섹션 -->
                <div class="alert alert-info mb-4">
                    <h5 class="alert-heading" id="corePrinciplesTitle">📌 핵심 principle</h5>
                    <p class="mb-2" id="corePrinciplesDesc1">모든 직원은 corresponding 직급별로 지정된 <strong>모든 조건을 충족</strong>해야 incentive를 받을 count 있습니다.</p>
                    <p class="mb-0" id="corePrinciplesDesc2">조건은 출근(4개), AQL(4개), 5PRS(2개)로 구성되며, 직급별로 apply 조건이 다릅니다.</p>
                </div>
                
                <!-- 10가지 조건 상세 설직원 -->
                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0" id="evaluationConditionsTitle">📊 10가지 평가 조건 상세</h5>
                    </div>
                    <div class="card-body">
                        <!-- 출근 조건 -->
                        <h6 class="text-success mb-3" id="attendanceConditionTitle">📅 출근 조건 (4개)</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered mb-4" id="attendanceTable">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%" class="cond-th-number">#</th>
                                    <th width="25%" class="cond-th-name">조건직원</th>
                                    <th width="20%" class="cond-th-criteria">기준</th>
                                    <th width="50%" class="cond-th-desc">설직원</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td class="cond-name-1">출근율</td>
                                    <td>≥88%</td>
                                    <td class="cond-desc-1">월간 출근율이 88% 이상이어야 합니다 (결근율 12% 이하)</td>
                                </tr>
                                <tr>
                                    <td>2</td>
                                    <td class="cond-name-2">무단결근</td>
                                    <td>≤2일</td>
                                    <td class="cond-desc-2">사전 승인 없는 결근이 month 2일 이하여야 합니다</td>
                                </tr>
                                <tr>
                                    <td>3</td>
                                    <td class="cond-name-3">actual 근무일</td>
                                    <td>>0일</td>
                                    <td class="cond-desc-3">actual 출근한 날이 1일 이상이어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>4</td>
                                    <td class="cond-name-4">최소 근무일</td>
                                    <td>≥12일</td>
                                    <td class="cond-desc-4">월간 최소 12일 이상 work해야 합니다</td>
                                </tr>
                            </tbody>
                            </table>
                        </div>

                        <!-- AQL 조건 -->
                        <h6 class="text-primary mb-3" id="aqlConditionTitle">🎯 AQL 조건 (4개)</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered mb-4" id="aqlTable">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%" class="cond-th-number">#</th>
                                    <th width="25%" class="cond-th-name">조건직원</th>
                                    <th width="20%" class="cond-th-criteria">기준</th>
                                    <th width="50%" class="cond-th-desc">설직원</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>5</td>
                                    <td class="cond-name-5">개인 AQL (당month)</td>
                                    <td>failed 0cases</td>
                                    <td class="cond-desc-5">당month 개인 AQL 검사 failed가 없어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>6</td>
                                    <td class="cond-name-6">개인 AQL (연속성)</td>
                                    <td>3연속 개월 실패 없음</td>
                                    <td class="cond-desc-6">최근 3개월간 연속으로 AQL failed가 없어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>7</td>
                                    <td class="cond-name-7">팀/구역 AQL</td>
                                    <td>3연속 개월 실패 없음</td>
                                    <td class="cond-desc-7">관리하는 팀/구역에서 3연속 개월 실패자가 없어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>8</td>
                                    <td class="cond-name-8">담당구역 AQL Reject율</td>
                                    <td><3%</td>
                                    <td class="cond-desc-8">담당 구역의 AQL 리젝률이 3% 미만이어야 합니다</td>
                                </tr>
                            </tbody>
                            </table>
                        </div>

                        <!-- 5PRS 조건 -->
                        <h6 class="text-warning mb-3" id="prsConditionTitle">📊 5PRS 조건 (2개)</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered" id="prsTable">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%" class="cond-th-number">#</th>
                                    <th width="25%" class="cond-th-name">조건직원</th>
                                    <th width="20%" class="cond-th-criteria">기준</th>
                                    <th width="50%" class="cond-th-desc">설직원</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>9</td>
                                    <td class="cond-name-9">5PRS 통과율</td>
                                    <td>≥95%</td>
                                    <td class="cond-desc-9">5족 평가 시스템에서 95% 이상 통과해야 합니다</td>
                                </tr>
                                <tr>
                                    <td>10</td>
                                    <td class="cond-name-10">5PRS 검사량</td>
                                    <td>≥100개</td>
                                    <td class="cond-desc-10">월간 최소 100개 이상 검사를 count행해야 합니다</td>
                                </tr>
                            </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <!-- 직급별 apply 조건 매트릭스 -->
                <div class="card mb-4 border-0 shadow-sm">
                    <div class="card-header" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white;">
                        <h5 class="mb-0" id="positionMatrixTitle">🎖️ 직급별 apply 조건</h5>
                    </div>
                    <div class="card-body">
                        
                        <h6 style="color: #ef4444; font-weight: 600;" class="mb-3" id="type1Header">TYPE-1 직급별 조건</h6>
                        <table class="table table-sm table-hover position-matrix-table" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                <tr>
                                    <th class="pos-header-position">직급</th>
                                    <th class="pos-header-conditions">apply 조건</th>
                                    <th class="pos-header-count">조건 count</th>
                                    <th class="pos-header-notes">비고</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>MANAGER</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만 적용</td>
                                </tr>
                                <tr>
                                    <td><strong>A.MANAGER</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만 적용</td>
                                </tr>
                                <tr>
                                    <td><strong>(V) SUPERVISOR</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만 적용</td>
                                </tr>
                                <tr>
                                    <td><strong>GROUP LEADER</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만 적용</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>LINE LEADER</strong></td>
                                    <td>1, 2, 3, 4, 7</td>
                                    <td class="condition-count">5개</td>
                                    <td>출근 + 팀/구역 AQL</td>
                                </tr>
                                <tr>
                                    <td><strong>AQL INSPECTOR</strong></td>
                                    <td>1, 2, 3, 4, 5</td>
                                    <td class="condition-count">5개</td>
                                    <td>출근 + 당month AQL (특별 calculation)</td>
                                </tr>
                                <tr>
                                    <td><strong>ASSEMBLY INSPECTOR</strong></td>
                                    <td>1, 2, 3, 4, 5, 6, 9, 10</td>
                                    <td class="condition-count">8개</td>
                                    <td>출근 + 개인 AQL + 5PRS</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>AUDIT & TRAINING TEAM</strong></td>
                                    <td>1, 2, 3, 4, 7, 8</td>
                                    <td class="condition-count">6개</td>
                                    <td>출근 + 팀/구역 AQL + 담당구역 reject</td>
                                </tr>
                                <tr>
                                    <td><strong>MODEL MASTER</strong></td>
                                    <td>1, 2, 3, 4, 8</td>
                                    <td class="condition-count">5개</td>
                                    <td>출근 + 담당구역 reject</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <h6 style="color: #ef4444; font-weight: 600;" class="mb-3 mt-4" id="type2Header">TYPE-2 직급별 조건</h6>
                        <table class="table table-sm table-hover" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                <tr>
                                    <th class="type2-header-position">직급</th>
                                    <th class="type2-header-conditions">apply 조건</th>
                                    <th class="type2-header-count">조건 count</th>
                                    <th class="type2-header-notes">특이사항</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong id="type2AllPositions">모든 TYPE-2 직급</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td id="type2FourConditions">4개</td>
                                    <td id="type2AttendanceOnly">출근 조건만 적용</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <h6 style="color: #ef4444; font-weight: 600;" class="mb-3 mt-4" id="type3Header">TYPE-3 직급별 조건</h6>
                        <table class="table table-sm table-hover" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                <tr>
                                    <th class="type3-header-position">직급</th>
                                    <th class="type3-header-conditions">apply 조건</th>
                                    <th class="type3-header-count">조건 count</th>
                                    <th class="type3-header-notes">특이사항</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="background-color: #fafafa;">
                                    <td><strong id="type3NewMember">NEW QIP MEMBER</strong></td>
                                    <td id="type3NoConditions">없음</td>
                                    <td id="type3ZeroConditions">0개</td>
                                    <td id="type3NewMemberNote">신입직원 - incentive 없음</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- incentive 금액 정보 -->
                <div class="card mb-4 border-0 shadow-sm">
                    <div class="card-header" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white;">
                        <h5 class="mb-0">💰 incentive 지급액 calculation 방법</h5>
                    </div>
                    <div class="card-body">
                        <!-- TYPE-1 incentive 테이블 -->
                        <h6 style="color: #ef4444; font-weight: 600;" class="mb-3" id="type1CalculationTitle">TYPE-1 직급별 incentive calculation 방법 및 actual 예시</h6>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                <tr>
                                    <th width="20%" class="calc-header-position">직급</th>
                                    <th width="40%" class="calc-header-method">calculation 방법</th>
                                    <th width="40%" class="calc-header-example">actual calculation 예시 ({year}year {month_kor})</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong><span class="calc-position-manager">1. MANAGER</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 incentive</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">incentive</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 3.5</span><br>
                                        <span class="calc-apply-condition-attendance">apply 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-line-leader-avg">Line Leader 평균</span>: 138,485 VND<br>
                                        <span class="calc-calculation-label">calculation</span>: 138,485 × 3.5 = <strong>484,698 VND</strong><br>
                                        <span class="calc-condition-not-met-zero">조건 미충족 → 0 VND</span></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-amanager">2. A.MANAGER</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 incentive</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">incentive</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 3</span><br>
                                        <span class="calc-apply-condition-attendance">apply 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="618030049">예시: 618030049 직원</span><br>
                                        <span class="calc-line-leader-avg">Line Leader 평균</span>: 127,767 VND<br>
                                        <span class="calc-calculation-label">calculation</span>: 127,767 × 3 = <strong>383,301 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-vsupervisor">3. (V) SUPERVISOR</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 incentive</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">incentive</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 2.5</span><br>
                                        <span class="calc-apply-condition-attendance">apply 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="618040412">예시: 618040412 직원</span><br>
                                        <span class="calc-line-leader-avg">Line Leader 평균</span>: 115,500 VND<br>
                                        <span class="calc-calculation-label">calculation</span>: 115,500 × 2.5 = <strong>288,750 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-groupleader">4. GROUP LEADER</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 incentive</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">incentive</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 2</span><br>
                                        <span class="calc-apply-condition-attendance">apply 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="619030390">예시: 619030390 직원</span><br>
                                        <span class="calc-condition-not-met-days" data-days="4">조건 미충족(근무일 4일)</span><br>
                                        → <strong>0 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-lineleader">5. LINE LEADER</span></strong></td>
                                    <td><strong><span class="calc-subordinate-incentive">부하직원 incentive based calculation</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">incentive</span> = (<span class="calc-subordinate-total">부하직원 total</span> <span class="calc-incentive-label">incentive</span> × 12%) × (<span class="calc-receive-ratio">수령 비율</span>)</span><br>
                                        <span class="calc-apply-condition-lineleader">apply 조건: 출근(1-4) + 팀/구역 AQL(7) = 5개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="619020468">예시: 619020468 직원</span><br>
                                        <span class="calc-subordinate-total">부하직원 total</span>: 1,270,585 VND<br>
                                        <span class="calc-calculation-label">calculation</span>: 1,270,585 × 0.12 × (8/10)<br>
                                        = <strong>152,470 VND</strong></td>
                                </tr>
                                <tr style="background-color: #fff3e0;">
                                    <td><strong><span class="calc-position-aqlinspector">6. AQL INSPECTOR</span></strong></td>
                                    <td><strong><span class="calc-special-calculation">Part1 + Part2 + Part3 특별 계산</span></strong><br>
                                        <div style="margin-top: 8px;"><strong><span class="calc-aql-evaluation">Part 1: AQL 평가 결과</span></strong></div>
                                        <small><span class="calc-level-a">Level-A</span> <span class="calc-month-range-1">1개월</span>: 150,000 | <span class="calc-month-range-2">2개월</span>: 250,000<br>
                                        <span class="calc-month-range-3">3개월</span>: 300,000 | <span class="calc-month-range-4">4개월</span>: 350,000<br>
                                        <span class="calc-month-range-5">5개월</span>: 400,000 | <span class="calc-month-range-6">6개월</span>: 450,000<br>
                                        <span class="calc-month-range-7">7개월</span>: 500,000 | <span class="calc-month-range-8">8개월</span>: 650,000<br>
                                        <span class="calc-month-range-9">9개월</span>: 750,000 | <span class="calc-month-range-10">10개월</span>: 850,000<br>
                                        <span class="calc-month-range-11">11개월</span>: 950,000 | <span class="calc-month-range-12plus">12개월+</span>: 1,000,000</small><br>
                                        <div style="margin-top: 8px;"><strong><span class="calc-cfa-certificate">Part 2: CFA 자격증</span></strong></div>
                                        <small><span class="calc-cfa-holder-bonus">CFA 자격증 보유시</span>: 700,000</small><br>
                                        <div style="margin-top: 8px;"><strong><span class="calc-hwk-claim">Part 3: HWK 클레임 방지</span></strong></div>
                                        <small><span class="calc-month-range-1-3">1-3개월</span>: 0 (<span class="calc-waiting-period">대기 기간</span>)<br>
                                        <span class="calc-month-range-4-6">4-6개월</span>: 300,000<br>
                                        <span class="calc-month-range-7-9">7-9개월</span>: 500,000<br>
                                        <span class="calc-month-range-10-12">10-12개월</span>: 700,000<br>
                                        <span class="calc-month-range-13plus">13개월+</span>: 900,000</small></td>
                                    <td><span class="calc-example-employee" data-employee="618110077">예시: 618110077 직원</span><br>
                                        Part1: 1,000,000 (<span class="calc-months-text" data-months="12">12개월</span>)<br>
                                        Part2: 700,000 (<span class="calc-cfa-holder">CFA 보유</span>)<br>
                                        Part3: 900,000 (<span class="calc-months-text" data-months="13">13개월</span>)<br>
                                        <span class="calc-total-label">합계</span>: 2,600,000 VND</td>
                                </tr>
                                <tr style="background-color: #f0f4ff;">
                                    <td><strong><span class="calc-position-assemblyinspector">7. ASSEMBLY INSPECTOR</span></strong></td>
                                    <td><strong><span class="calc-consecutive-month-incentive">연속 충족 개월 기준 incentive</span></strong><br>
                                        <small><span class="calc-apply-condition-assembly">apply 조건: 1-4(출근), 5-6(개인AQL), 9-10(5PRS)</span></small><br>
                                        <span class="calc-month-range-0to1">0-1개월</span>: 150,000 | <span class="calc-month-range-2">2개월</span>: 250,000<br>
                                        <span class="calc-month-range-3">3개월</span>: 300,000 | <span class="calc-month-range-4">4개월</span>: 350,000<br>
                                        <span class="calc-month-range-5">5개월</span>: 400,000 | <span class="calc-month-range-6">6개월</span>: 450,000<br>
                                        <span class="calc-month-range-7">7개월</span>: 500,000 | <span class="calc-month-range-8">8개월</span>: 650,000<br>
                                        <span class="calc-month-range-9">9개월</span>: 750,000 | <span class="calc-month-range-10">10개월</span>: 850,000<br>
                                        <span class="calc-month-range-11">11개월</span>: 950,000 | <span class="calc-month-range-12plus">12개월+</span>: 1,000,000</td>
                                    <td><strong><span class="calc-example-consecutive" data-months="10">예시: 10개월 연속 충족</span></strong><br>
                                        ✅ <span class="calc-attendance-rate">출근율</span> 92% ≥88%<br>
                                        ✅ <span class="calc-unauthorized-absence">무단결근</span> <span class="calc-days-text" data-days="0">0일</span> ≤<span class="calc-days-text" data-days="2">2일</span><br>
                                        ✅ <span class="calc-working-days">근무일</span> <span class="calc-days-text" data-days="20">20일</span> ≥<span class="calc-days-text" data-days="12">12일</span><br>
                                        ✅ <span class="calc-personal-aql-failures">개인AQL failed</span> <span class="calc-cases-text" data-cases="0">0cases</span><br>
                                        ✅ 5PRS <span class="calc-pass-rate">통과율</span> 98% ≥95%<br>
                                        ✅ 5PRS <span class="calc-inspection-quantity">검사량</span> <span class="calc-pieces-text" data-pieces="250">250족</span> ≥100<br>
                                        → <strong>850,000 VND</strong></td>
                                </tr>
                                <tr style="background-color: #f0f4ff;">
                                    <td><strong><span class="calc-position-audittraining">8. AUDIT & TRAINING</span></strong></td>
                                    <td><strong><span class="calc-consecutive-month-incentive">연속 충족 개월 기준 incentive</span></strong><br>
                                        <small><span class="calc-apply-condition-audit">apply 조건: 1-4(출근), 7(팀AQL), 8(reject율)</span></small><br>
                                        <span class="calc-month-range-0to1">0-1개월</span>: 150,000 | <span class="calc-month-range-2">2개월</span>: 250,000<br>
                                        <span class="calc-month-range-3">3개월</span>: 300,000 | <span class="calc-month-range-4">4개월</span>: 350,000<br>
                                        <span class="calc-month-range-5">5개월</span>: 400,000 | <span class="calc-month-range-6">6개월</span>: 450,000<br>
                                        <span class="calc-month-range-7">7개월</span>: 500,000 | <span class="calc-month-range-8">8개월</span>: 650,000<br>
                                        <span class="calc-month-range-9">9개월</span>: 750,000 | <span class="calc-month-range-10">10개월</span>: 850,000<br>
                                        <span class="calc-month-range-11">11개월</span>: 950,000 | <span class="calc-month-range-12plus">12개월+</span>: 1,000,000</td>
                                    <td><strong><span class="calc-example-not-met-reset">예시: 조건 미충족 → 리셋</span></strong><br>
                                        <span class="calc-previous-month">전month</span>: <span class="calc-consecutive-months" data-months="11">11개월 연속</span> → 950,000<br>
                                        <span class="calc-current-month-eval">당month 평가</span>:<br>
                                        ✅ <span class="calc-all-attendance-met">출근 조건 모두 충족</span><br>
                                        ✅ <span class="calc-team-aql-no-fail">팀AQL 연속failed 없음</span><br>
                                        ❌ <span class="calc-reject-rate">reject율</span> 4.35% >3%<br>
                                        → <span class="calc-reset-to-zero">연속개월 0으로 리셋</span><br>
                                        → <strong>0 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-modelmaster">9. MODEL MASTER</span></strong></td>
                                    <td><strong><span class="calc-consecutive-month-incentive">연속 충족 개월 기준 incentive</span></strong><br>
                                        <small><span class="calc-apply-condition-model">apply 조건: 1-4(출근), 8(reject율 <3%)</span></small><br>
                                        <span class="calc-month-range-0to1">0-1개월</span>: 150,000 | <span class="calc-month-range-2">2개월</span>: 250,000<br>
                                        <span class="calc-month-range-3">3개월</span>: 300,000 | <span class="calc-month-range-4">4개월</span>: 350,000<br>
                                        <span class="calc-month-range-5">5개월</span>: 400,000 | <span class="calc-month-range-6">6개월</span>: 450,000<br>
                                        <span class="calc-month-range-7">7개월</span>: 500,000 | <span class="calc-month-range-8">8개월</span>: 650,000<br>
                                        <span class="calc-month-range-9">9개월</span>: 750,000 | <span class="calc-month-range-10">10개월</span>: 850,000<br>
                                        <span class="calc-month-range-11">11개월</span>: 950,000 | <span class="calc-month-range-12plus">12개월+</span>: 1,000,000</td>
                                    <td><strong><span class="calc-example-max-achieved" data-months="12">예시: 12개월 이상 최대</span></strong><br>
                                        <span class="calc-previous-month">전month</span>: <span class="calc-months-text" data-months="15">15개월</span> → 1,000,000<br>
                                        <span class="calc-current-month-eval">당month 평가</span>:<br>
                                        ✅ <span class="calc-attendance-rate">출근율</span> 95% ≥88%<br>
                                        ✅ <span class="calc-unauthorized-absence">무단결근</span> <span class="calc-days-text" data-days="1">1일</span> ≤<span class="calc-days-text" data-days="2">2일</span><br>
                                        ✅ <span class="calc-working-days">근무일</span> <span class="calc-days-text" data-days="18">18일</span> ≥<span class="calc-days-text" data-days="12">12일</span><br>
                                        ✅ <span class="calc-reject-rate">reject율</span> 2.5% <3%<br>
                                        → <span class="calc-consecutive-months" data-months="16">16개월 연속 충족</span><br>
                                        → <strong>1,000,000 VND</strong></td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- TYPE-1 ASSEMBLY INSPECTOR 연속 목표 달성시 incentive 지급 기준 -->
                        <h6 style="color: #ef4444; font-weight: 600;" class="mb-3" id="assemblyInspectorIncentiveTitle">TYPE-1 ASSEMBLY INSPECTOR 연속 work incentive</h6>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                <tr>
                                    <th class="consecutive-achievement-header">연속 목표 달성 개월</th>
                                    <th class="incentive-amount-header">incentive 금액 (VND)</th>
                                </tr>
                            </thead>
                            <tbody>'''

    # Generate progression table rows outside f-string to avoid # and \ issues
    highlight_style = " style='background-color: #e8f5e9; font-weight: bold;'"
    month_or_more_span = "<span class='month-or-more'>이상</span>"

    for progression_month in range(1, 13):
        row_style = highlight_style if progression_month >= 12 else ""
        month_suffix = month_or_more_span if progression_month == 12 else ""
        amount = progression_table.get(progression_month, 0)
        html_content += f'''
                                <tr{row_style}>
                                    <td><span class="month-text-{progression_month}">{progression_month}개월</span>{month_suffix}</td>
                                    <td>{amount:,}</td>
                                </tr>'''

    html_content += f'''
                            </tbody>
                        </table>

                        <!-- TYPE-1 관리자 직급 인센티브 계산 방법 (2025-12-04 추가) -->
                        <h6 style="color: #2563eb; font-weight: 600;" class="mb-3 mt-4" id="type1ManagerCalculationTitle">TYPE-1 관리자 직급 incentive calculation 방법</h6>
                        <div class="alert" style="background-color: #dbeafe; border-left: 4px solid #2563eb; color: #1e40af;" class="mb-3">
                            <strong>👔 <span id="type1ManagerPrincipleLabel">TYPE-1 관리자 calculation principle:</span></strong>
                            <span id="type1ManagerPrincipleText">TYPE-1 관리자 직급은 자신에게 속한 <strong>부하 LINE LEADER들의 수령자 평균 incentive</strong>에 직급별 배수를 곱하여 calculation됩니다.</span>
                        </div>
                        <div class="alert" style="background-color: #e8f5e9; border-left: 4px solid #4caf50; color: #1b5e20;" class="mb-3">
                            <strong>✅ <span id="type1ManagerReceivingLabel">평균 계산 기준:</span></strong>
                            <span id="type1ManagerReceivingText">부하 LINE LEADER 평균 계산 시 <strong style="color: #d32f2f;">수령자만 대상</strong>으로 합니다. (0 VND 제외)</span>
                            <br><small id="type1ManagerReceivingNote" style="color: #555;">예: 부하 LINE LEADER 10명 중 7명만 인센티브 수령 시, 7명의 평균으로 계산</small>
                        </div>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #2563eb;">
                                <tr>
                                    <th width="25%" class="type1-manager-position-header">TYPE-1 관리자 직급</th>
                                    <th width="35%" class="type1-manager-method-header">calculation 방법</th>
                                    <th width="15%" class="type1-manager-multiplier-header">배수</th>
                                    <th width="25%" class="type1-manager-condition-header">적용 조건</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>1. S.MANAGER</strong></td>
                                    <td>부하 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균</td>
                                    <td style="text-align: center; font-weight: bold;">× 4.0</td>
                                    <td>출근 조건 (1-4번) 100% 충족</td>
                                </tr>
                                <tr>
                                    <td><strong>2. MANAGER</strong></td>
                                    <td>부하 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균</td>
                                    <td style="text-align: center; font-weight: bold;">× 3.5</td>
                                    <td>출근 조건 (1-4번) 100% 충족</td>
                                </tr>
                                <tr>
                                    <td><strong>3. A.MANAGER</strong></td>
                                    <td>부하 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균</td>
                                    <td style="text-align: center; font-weight: bold;">× 3.0</td>
                                    <td>출근 조건 (1-4번) 100% 충족</td>
                                </tr>
                                <tr style="background-color: #fef3c7;">
                                    <td><strong>4. (V) SUPERVISOR</strong></td>
                                    <td>부하 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균</td>
                                    <td style="text-align: center; font-weight: bold;">× 2.5</td>
                                    <td>출근 조건 (1-4번) 100% 충족</td>
                                </tr>
                                <tr style="background-color: #fef3c7;">
                                    <td><strong>5. SUPERVISOR</strong></td>
                                    <td>부하 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균</td>
                                    <td style="text-align: center; font-weight: bold;">× 2.5</td>
                                    <td>출근 조건 (1-4번) 100% 충족</td>
                                </tr>
                                <tr style="background-color: #ecfdf5;">
                                    <td><strong>6. GROUP LEADER</strong></td>
                                    <td>부하 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균</td>
                                    <td style="text-align: center; font-weight: bold;">× 2.0</td>
                                    <td>출근 조건 (1-4번) 100% 충족</td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="alert alert-info mb-4">
                            <h6 style="color: #0c4a6e;" id="type1ManagerNoteTitle">📌 TYPE-1 관리자 계산 특이사항</h6>
                            <ul class="mb-0">
                                <li id="type1ManagerNote1"><strong>부하직원 범위:</strong> 조직도 상 직접 + 간접 부하 LINE LEADER 모두 포함 (BFS 탐색)</li>
                                <li id="type1ManagerNote2"><strong>수령자만 평균:</strong> 인센티브 0 VND인 LINE LEADER는 평균 계산에서 제외</li>
                                <li id="type1ManagerNote3"><strong>Fallback:</strong> 부하 LINE LEADER가 없는 경우, 전체 TYPE-1 LINE LEADER 수령자 평균 사용</li>
                                <li id="type1ManagerNote4"><strong>조건 미충족:</strong> 출근 조건 (1-4번) 중 하나라도 미충족 시 0 VND</li>
                            </ul>
                        </div>

                        <!-- TYPE-2 incentive calculation 방법 -->
                        <h6 style="color: #ef4444; font-weight: 600;" class="mb-3" id="type2CalculationTitle">TYPE-2 total 직급 incentive calculation 방법</h6>
                        <div class="alert" style="background-color: #f0f4ff; border-left: 4px solid #ef4444; color: #333;" class="mb-3">
                            <strong>📊 <span id="type2PrincipleLabel">TYPE-2 calculation principle:</span></strong> <span id="type2PrincipleText">TYPE-2 직급은 corresponding하는 TYPE-1 직급의 평균 incentive를 기준으로 calculation됩니다.</span>
                        </div>
                        <!-- 수령자만 평균 원칙 설명 (2025-12-04 추가) -->
                        <div class="alert" style="background-color: #e8f5e9; border-left: 4px solid #4caf50; color: #1b5e20;" class="mb-3">
                            <strong>✅ <span id="receivingOnlyLabel">평균 계산 기준:</span></strong>
                            <span id="receivingOnlyText">모든 평균 계산은 <strong style="color: #d32f2f;">수령자만 대상</strong>으로 합니다. (0 VND 제외)</span>
                            <br><small id="receivingOnlyNote" style="color: #555;">예: LINE LEADER 10명 중 7명만 인센티브 수령 시, 7명의 평균으로 계산 (10명 전체 평균 아님)</small>
                        </div>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                <tr>
                                    <th width="25%" class="type2-calc-header-position">TYPE-2 직급</th>
                                    <th width="25%" class="type2-calc-header-reference">참조 TYPE-1 직급</th>
                                    <th width="25%" class="type2-calc-header-method">calculation 방법</th>
                                    <th width="25%" class="type2-calc-header-average">{year}year {month_kor} 평균</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>1. (V) SUPERVISOR</strong></td>
                                    <td>TYPE-1 (V) SUPERVISOR</td>
                                    <td>(V) SUPERVISOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>969,758 VND</td>
                                </tr>
                                <tr>
                                    <td><strong>2. A.MANAGER</strong></td>
                                    <td>TYPE-1 A.MANAGER</td>
                                    <td>A.MANAGER <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>990,000 VND</td>
                                </tr>
                                <tr style="background-color: #fff9e6;">
                                    <td><strong>3. GROUP LEADER</strong></td>
                                    <td>TYPE-1 LINE LEADER</td>
                                    <td>TYPE-1 LINE LEADER <span class="average-text" style="color: #d32f2f;">수령자 평균</span> × 2</td>
                                    <td>679,866 VND</td>
                                </tr>
                                <tr style="background-color: #e8f5ff;">
                                    <td><strong>4. LINE LEADER</strong></td>
                                    <td>TYPE-1 LINE LEADER</td>
                                    <td>TYPE-1 LINE LEADER <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>339,933 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>5. AQL INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>6. ASSEMBLY INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>7. STITCHING INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>8. BOTTOM INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>9. CUTTING INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>10. MTL INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>11. OCPT STAFF</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>12. OSC INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #fff3cd;">
                                    <td><strong>13. QA TEAM (QA3B)</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                                <tr style="background-color: #d4edda;">
                                    <td><strong>14. QA TEAM (QA3A)</strong></td>
                                    <td>TYPE-1 GROUP LEADER</td>
                                    <td>GROUP LEADER <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>662,400 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>15. RQC</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text" style="color: #d32f2f;">수령자 평균</span></td>
                                    <td>359,210 VND</td>
                                </tr>
                            </tbody>
                        </table>

                        <!-- TYPE-2 GROUP LEADER 특별 calculation 규칙 설직원 -->
                        <div class="alert alert-warning mb-4">
                            <h6 style="color: #856404;" id="type2GroupLeaderSpecialTitle">⚠️ TYPE-2 GROUP LEADER 특별 calculation 규칙</h6>
                            <ul class="mb-0">
                                <li id="type2BaseCalc"><strong>기본 calculation:</strong> TYPE-1 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균 incentive × 2</li>
                                <li id="type2IndependentCalc"><strong>Fallback (TYPE-1 평균 0 VND):</strong> TYPE-2 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균 × 2로 calculation</li>
                                <li id="type2Important"><strong>중요:</strong> 모든 평균은 인센티브 수령자만 대상 (0 VND 제외)</li>
                                <li id="type2Conditions"><strong>apply 조건:</strong> TYPE-2는 출근 조건(1-4번)만 충족하면 incentive 지급</li>
                            </ul>
                        </div>

                        <!-- TYPE-2 QA TEAM 특별 calculation 규칙 (2025-12-05 수정: QA3A = TYPE-1 LINE LEADER × 2) -->
                        <div class="alert" style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; color: #0c5460;" class="mb-4">
                            <h6 style="color: #0c5460;" id="type2QATeamSpecialTitle">📋 TYPE-2 QA TEAM 특별 calculation 규칙</h6>
                            <ul class="mb-0">
                                <li id="type2QATeamQA3B"><strong>QA3B 코드:</strong> TYPE-1 ASSEMBLY INSPECTOR <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균 = <strong>359,210 VND</strong></li>
                                <li id="type2QATeamQA3A"><strong>QA3A 코드:</strong> TYPE-1 LINE LEADER <span style="color: #d32f2f; font-weight: bold;">수령자</span> 평균 × 2 = <strong>679,866 VND</strong> (GROUP LEADER와 동일)</li>
                                <li id="type2QATeamNote"><strong>구분 기준:</strong> 직원의 FINAL QIP POSITION NAME CODE 값으로 QA3A/QA3B 구분</li>
                            </ul>
                        </div>

                        <!-- TYPE-3 incentive -->
                        <h6 style="color: #ef4444; font-weight: 600;" class="mb-3" id="type3SectionTitle">TYPE-3 신입 직원 incentive</h6>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                <tr>
                                    <th class="type3-position-header">구분</th>
                                    <th class="type3-standard-incentive-header">기준 incentive</th>
                                    <th class="type3-calculation-method-header">calculation 방법</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="type3-new-qip-member">NEW QIP MEMBER</td>
                                    <td>0 VND</td>
                                    <td><span class="type3-no-incentive">신입 직원은 incentive 지급 없음.</span><br>
                                        <span class="type3-one-month-training">단, 1달 후 work지 배치한 다음부터</span><br>
                                        <span class="type3-type-reclassification">TYPE을 변경하며, incentive 지급 조건 부여됨</span></td>
                                </tr>
                            </tbody>
                        </table>
                        
                    </div>
                </div>
                
                <!-- 추가 정보 섹션 -->
                <div class="card mb-4">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0" id="goodToKnowTitle">💡 Good to Know</h5>
                    </div>
                    <div class="card-body">
                        <h6 class="text-primary mb-3" id="corePrinciplesSubtitle">Core Principles of Incentive Calculation</h6>
                        <ul class="list-group mb-3">
                            <li class="list-group-item">
                                <strong>📌 <span class="failure-principle-label">actual 지급액:</span></strong> <span class="failure-principle-text">표시된 금액 range는 예시이며, actual 지급액은 개인의 성과와 조건 충족 여부에 따라 달라집니다.</span>
                            </li>
                            <li class="list-group-item">
                                <strong>📊 <span class="type2-principle-label">TYPE-2 동적 calculation:</span></strong> <span class="type2-principle-text">TYPE-2 직원의 incentive는 매month corresponding TYPE-1 직급의 actual 평균값으로 자동 calculation됩니다.</span>
                            </li>
                            <li class="list-group-item">
                                <strong>🔄 <span class="consecutive-bonus-label">연속성 보상:</span></strong> <span class="consecutive-bonus-text">ASSEMBLY INSPECTOR는 연속 work 개월이 증가할수록 incentive가 단계적으로 상승합니다.</span>
                            </li>
                            <li class="list-group-item">
                                <strong>⚡ <span class="special-calculation-label">특별 calculation 직급:</span></strong> <span class="special-calculation-text">AQL INSPECTOR(3단계 합산: Part1 + Part2 + Part3)</span>
                            </li>
                            <li class="list-group-item">
                                <strong>🎯 <span class="condition-failure-label">조건 미충족시:</span></strong> <span class="condition-failure-text">하나라도 필count 조건을 충족하지 못하면 incentive가 0이 됩니다.</span>
                            </li>
                        </ul>
                        
                        <h6 class="text-success mb-3" id="monthlyIncentiveChangeReasonsTitle">monthby incentive 변동 요인</h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th class="change-factors-header">변동 요인</th>
                                    <th class="impact-header">영향</th>
                                    <th class="example-header">예시</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="minimum-days-label">근무일count</td>
                                    <td class="less-than-12-days">12일 미만시 미지급</td>
                                    <td class="november-11-days">11일 work → 0 VND</td>
                                </tr>
                                <tr>
                                    <td class="attendance-rate-label">출근율</td>
                                    <td class="less-than-88-percent">88% 미만시 미지급</td>
                                    <td class="attendance-example">87% 출근율 → 0 VND</td>
                                </tr>
                                <tr>
                                    <td class="unauthorized-absence-label">무단결근</td>
                                    <td class="more-than-3-days">3일 이상시 미지급</td>
                                    <td class="unauthorized-example">3일 무단결근 → 0 VND</td>
                                </tr>
                                <tr>
                                    <td class="aql-failure-label">AQL failed</td>
                                    <td class="current-month-failure">corresponding 직급만 영향</td>
                                    <td class="aql-failure-example">AQL failed → 조건 미충족</td>
                                </tr>
                                <tr>
                                    <td class="fprs-pass-rate-label">5PRS 통과율</td>
                                    <td class="less-than-95-percent">95% 미만시 미지급 (corresponding자)</td>
                                    <td class="fprs-example">94% → 0 VND</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- calculation 예시 섹션 / Calculation Example Section -->
                <div class="card mb-4">
                    <div class="card-header bg-warning">
                        <h5 class="mb-0" id="faqCalculationExampleTitle">📐 actual calculation 예시</h5>
                    </div>
                    <div class="card-body">
                        <h6 class="text-primary mb-3" id="faqCase1Title">예시 1: TYPE-1 ASSEMBLY INSPECTOR (10개월 연속 work)</h6>
                        <div class="alert alert-light">
                            <p><strong id="faqCase1EmployeeLabel">직원:</strong> BÙI THỊ KIỀU LY (619060201)</p>
                            <p><strong id="faqCase1PrevMonthLabel">전month 상태:</strong> <span id="faqCase1PrevMonthText">9개월 연속 work, 750,000 VND 수령</span></p>
                            <p><strong id="faqCase1ConditionsLabel">당month 조건 충족:</strong></p>
                            <ul id="faqCase1ConditionsList">
                                <li>✅ <span class="faq-attendance-label">출근율:</span> 92% (≥88%)</li>
                                <li>✅ <span class="faq-absence-label">무단결근:</span> <span class="faq-absence-value">0일</span> (≤<span class="faq-absence-limit">2일</span>)</li>
                                <li>✅ <span class="faq-actual-days-label">actual 근무일:</span> <span class="faq-actual-days-value">20일</span> (><span class="faq-actual-days-min">0일</span>)</li>
                                <li>✅ <span class="faq-min-days-label">최소 근무일:</span> <span class="faq-min-days-value">20일</span> (≥<span class="faq-min-days-req">12일</span>)</li>
                                <li>✅ <span class="faq-aql-current-label">개인 AQL (당month):</span> <span class="faq-aql-current-value">failed 0cases</span></li>
                                <li>✅ <span class="faq-aql-consecutive-label">개인 AQL (연속):</span> <span class="faq-aql-consecutive-value">3연속 개월 실패 없음</span></li>
                                <li>✅ <span class="faq-fprs-rate-label">5PRS 통과율:</span> 97% (≥95%)</li>
                                <li>✅ <span class="faq-fprs-qty-label">5PRS 검사량:</span> <span class="faq-fprs-qty-value">150개</span> (≥<span class="faq-fprs-qty-min">100개</span>)</li>
                            </ul>
                            <p><strong id="faqCase1ResultLabel">결과:</strong> <span id="faqCase1ResultText">모든 조건 충족 → <span class="badge bg-success">10개월 연속 → 850,000 VND 지급</span></span></p>
                        </div>
                        
                        <h6 class="text-primary mb-3 mt-4" id="faqCase2Title">예시 2: AUDIT & TRAINING TEAM (담당구역 reject율 calculation)</h6>
                        <div class="alert alert-light">
                            <p><strong id="faqCase2EmployeeLabel">직원:</strong> VÕ THỊ THÙY LINH (AUDIT & TRAINING TEAM LEADER)</p>
                            <p><strong id="faqCase2AreaLabel">담당 구역:</strong> Building B </p>
                            <p><strong><span id="faqCase2InspectionLabel">Building B 구역 생산 total AQL 검사 PO count량:</span> <span id="faqCase2InspectionQty">100개</span></strong></p>
                            <p><strong><span id="faqCase2RejectLabel">Building B 구역 생산 total AQL 리젝 PO count량:</span> <span id="faqCase2RejectQty">2개</span></strong></p>
                            <p><strong id="faqCase2CalcLabel">calculation:</strong> 2 / 100 × 100 = 2%</p>
                            <p><strong id="faqCase2ResultLabel">결과:</strong> ✅ 2% < 3% → <span class="badge bg-success" id="faqCase2ResultBadge">조건 충족</span></p>
                        </div>
                        
                        <h6 class="text-primary mb-3 mt-4" id="faqMemberTableTitle">AUDIT & TRAINING TEAM 멤버by 담당 구역</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #ef4444;">
                                        <th id="faqTableHeaderName">직원employees</th>
                                        <th id="faqTableHeaderBuilding">담당 Building</th>
                                        <th id="faqTableHeaderDesc">설직원</th>
                                        <th id="faqTableHeaderReject">Reject율</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>VÕ THỊ THÙY LINH</strong></td>
                                        <td class="faq-building-whole">total</td>
                                        <td class="faq-team-leader-desc">Team Leader - total Building total괄</td>
                                        <td style="color: #dc3545;">3.9% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>CAO THỊ TỐ NGUYÊN</td>
                                        <td>Building B</td>
                                        <td>Building B & Repacking BS</td>
                                        <td style="color: #dc3545;">4.3% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>NGUYỄN THÚY HẰNG</td>
                                        <td>Building C</td>
                                        <td><span>Building C </span><span class="faq-building-whole">total</span></td>
                                        <td style="color: #dc3545;">3.4% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>DANH THỊ KIM ANH</td>
                                        <td>Building D</td>
                                        <td><span>Building D </span><span class="faq-building-whole">total</span></td>
                                        <td style="color: #dc3545;">3.3% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>NGUYỄN THANH TRÚC</td>
                                        <td>Building A</td>
                                        <td><span>Building A </span><span class="faq-building-whole">total</span></td>
                                        <td style="color: #dc3545;">4.7% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>PHẠM MỸ HUYỀN</td>
                                        <td>Building D</td>
                                        <td><span>Building D </span><span class="faq-building-whole">total</span></td>
                                        <td style="color: #dc3545;">3.3% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>SẦM TRÍ THÀNH</td>
                                        <td>Building C</td>
                                        <td><span>Building C </span><span class="faq-building-whole">total</span></td>
                                        <td style="color: #dc3545;">3.4% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>LÝ DĨ CƯỜNG</td>
                                        <td>-</td>
                                        <td class="faq-other-conditions">기타 조건 미충족</td>
                                        <td>-</td>
                                    </tr>
                                </tbody>
                            </table>
                            <p class="text-muted small mt-2">
                                <span id="faqRejectRateNote">* Reject율 기준: 3% 미만 (✅ 충족, ❌ 미충족)</span><br>
                                <span id="faqMemberNote">* {month_kor} 기준 모든 AUDIT & TRAINING TEAM 멤버가 reject율 조건 미충족으로 incentive 0원</span>
                            </p>
                        </div>
                        
                        <h6 class="text-primary mb-3 mt-4" id="faqCase3Title">예시 3: TYPE-2 STITCHING INSPECTOR</h6>
                        <div class="alert alert-light">
                            <p><strong id="faqCase3EmployeeLabel">직원:</strong> PHẠM THỊ HOA (STITCHING INSPECTOR)</p>
                            <p><strong id="faqCase3TypeLabel">직급 type:</strong> TYPE-2</p>
                            <p><strong id="faqCase3StatusLabel">조건 충족 현황:</strong></p>
                            <ul id="faqCase3ConditionsList">
                                <li>✅ <span class="faq-case3-attendance-label">출근율:</span> 95% (≥88% <span class="faq-case3-met">충족</span>)</li>
                                <li>✅ <span class="faq-case3-absence-label">무단결근:</span> <span class="faq-case3-absence-value">0일</span> (≤<span class="faq-case3-absence-limit">2일</span> <span class="faq-case3-met">충족</span>)</li>
                                <li>✅ <span class="faq-case3-actual-label">actual근무일:</span> <span class="faq-case3-actual-value">19일</span> (><span class="faq-case3-actual-min">0일</span> <span class="faq-case3-met">충족</span>)</li>
                                <li>✅ <span class="faq-case3-min-label">최소근무일:</span> <span class="faq-case3-min-value">19일</span> (≥<span class="faq-case3-min-req">12일</span> <span class="faq-case3-met">충족</span>)</li>
                            </ul>
                            <p><strong id="faqCase3CalcLabel">incentive calculation:</strong></p>
                            <p id="faqCase3Explanation">TYPE-2 STITCHING INSPECTOR는 출근 조건(1-4번)만 확인하며, 모든 조건을 충족했으므로 기본 incentive를 받습니다.</p>
                            <p><strong id="faqCase3PaymentLabel">지급액:</strong> 150,000 VND (<span id="faqCase3BasicText">TYPE-2 기본 incentive</span>)</p>
                            <p class="text-muted" id="faqCase3Note">* TYPE-2는 AQL이나 5PRS 조건 without 출근 조건만으로 incentive가 determination됩니다.</p>
                        </div>
                    </div>
                </div>
                
                <!-- 출근 calculation 공식 -->
                <div class="card mb-4">
                    <div class="card-header bg-secondary text-white">
                        <h5 class="mb-0" id="attendanceCalcTitle">📊 출근율 calculation 방식</h5>
                    </div>
                    <div class="card-body">
                        <div class="formula-box p-3 bg-light rounded mb-3">
                            <h6 id="attendanceFormulaTitle">actual calculation 공식 (시스템 구현):</h6>
                            <code class="d-block p-2 bg-white rounded mb-2" id="attendanceFormula1">
                                출근율(%) = 100 - 결근율(%)
                            </code>
                            <code class="d-block p-2 bg-white rounded" id="attendanceFormula2">
                                결근율(%) = (결근 thcount / total 근무일) × 100
                            </code>
                            <p class="mt-2 text-muted small" id="attendanceFormulaNote">* 결근 thcount = total 근무일 - actual 근무일 - 승인된 휴가</p>
                        </div>
                        
                        <div class="formula-box p-3 bg-light rounded mb-3">
                            <h6 id="attendanceExamplesTitle">결근율 calculation 예시:</h6>
                            <div class="alert alert-light">
                                <strong id="attendanceExample1Title">예시 1: 정상 work자</strong><br>
                                • <span class="att-total-days-label">total 근무일</span>: 27<span class="att-days-unit">th</span><br>
                                • <span class="att-actual-days-label">actual 근무일</span>: 25<span class="att-days-unit">th</span><br>
                                • <span class="att-approved-leave-label">승인된 휴가</span>: 2<span class="att-days-unit">th</span> (<span class="att-annual-leave">연차</span>)<br>
                                • <span class="att-absence-days-label">결근 thcount</span>: 27 - 25 - 2 = 0<span class="att-days-unit">th</span><br>
                                • <span class="att-absence-rate-label">결근율</span>: (0 / 27) × 100 = <strong>0%</strong><br>
                                • <span class="att-attendance-rate-label">출근율</span>: 100 - 0 = <strong>100%</strong> ✅
                            </div>
                            <div class="alert alert-light">
                                <strong id="attendanceExample2Title">예시 2: 무단결근 포함</strong><br>
                                • <span class="att-total-days-label">total 근무일</span>: 27<span class="att-days-unit">th</span><br>
                                • <span class="att-actual-days-label">actual 근무일</span>: 22<span class="att-days-unit">th</span><br>
                                • <span class="att-approved-leave-label">승인된 휴가</span>: 1<span class="att-days-unit">th</span> (<span class="att-sick-leave">병가</span>)<br>
                                • <span class="att-unauthorized-absence-label">무단결근</span>: 4<span class="att-days-unit">th</span> (AR1)<br>
                                • <span class="att-absence-days-label">결근 thcount</span>: 27 - 22 - 1 = 4<span class="att-days-unit">th</span><br>
                                • <span class="att-absence-rate-label">결근율</span>: (4 / 27) × 100 = <strong>14.8%</strong><br>
                                • <span class="att-attendance-rate-label">출근율</span>: 100 - 14.8 = <strong>85.2%</strong> ❌ (<span class="att-less-than-88">88% 미만</span>)
                            </div>
                            <div class="alert alert-light">
                                <strong id="attendanceExample3Title">예시 3: 조건 충족 경계선</strong><br>
                                • <span class="att-total-days-label">total 근무일</span>: 27<span class="att-days-unit">th</span><br>
                                • <span class="att-actual-days-label">actual 근무일</span>: 24<span class="att-days-unit">th</span><br>
                                • <span class="att-approved-leave-label">승인된 휴가</span>: 0<span class="att-days-unit">th</span><br>
                                • <span class="att-unauthorized-absence-label">무단결근</span>: 3<span class="att-days-unit">th</span> (AR1)<br>
                                • <span class="att-absence-days-label">결근 thcount</span>: 27 - 24 - 0 = 3<span class="att-days-unit">th</span><br>
                                • <span class="att-absence-rate-label">결근율</span>: (3 / 27) × 100 = <strong>11.1%</strong><br>
                                • <span class="att-attendance-rate-label">출근율</span>: 100 - 11.1 = <strong>88.9%</strong> ✅ (<span class="att-more-than-88">88% 이상</span>)<br>
                                • <span id="attendanceCondition2NotMet">단, 무단결근 3일로 조건 2 미충족 → incentive 0원</span>
                            </div>
                        </div>
                        
                        <div class="formula-box p-3 bg-light rounded mb-3">
                            <h6 id="attendanceClassificationTitle">결근 사유by 분류:</h6>
                            <div class="row">
                                <div class="col-md-6">
                                    <p class="text-success"><strong id="attendanceNotIncludedTitle">✅ 결근율에 포함 안됨 (승인된 휴가):</strong></p>
                                    <ul class="small">
                                        <li>Sinh thường 1 con (<span class="att-maternity-leave">출산휴가</span>)</li>
                                        <li>Phép năm (<span class="att-annual-leave-vn">연차휴가</span>)</li>
                                        <li>Vắng có phép (<span class="att-approved-absence">승인된 휴가</span>)</li>
                                        <li>Dưỡng sức sinh thường (<span class="att-postpartum-rest">출산 후 요양</span>)</li>
                                        <li>Khám thai bình thường (<span class="att-prenatal-checkup">산전검진</span>)</li>
                                        <li>Con dưới 3 tuổi bị bệnh (<span class="att-childcare-leave">육아휴가</span>)</li>
                                        <li>AR2 - ốm ngắn ngày (<span class="att-short-sick-leave">병가</span>)</li>
                                        <li>Đi công tác (<span class="att-business-trip">출장</span>)</li>
                                        <li>Nghĩa vụ quân sự (<span class="att-military-service">군복무</span>)</li>
                                        <li class="text-info"><strong>Đi làm không quẹt thẻ</strong> (<span class="att-card-not-swiped">출퇴근 체크 누락</span>)</li>
                                        <li class="text-info"><strong>Công nhân viên mới</strong> (<span class="att-new-employee">신규입사 특례</span>)</li>
                                        <li class="text-info"><strong>Nghỉ bù</strong> (<span class="att-compensatory-leave">대체휴무</span>)</li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <p class="text-danger"><strong id="attendanceIncludedTitle">❌ 결근율에 포함됨 (무단결근):</strong></p>
                                    <ul class="small">
                                        <li><strong>AR1 - Vắng không phép</strong> (<span class="att-unauthorized-absence-ar1">무단결근</span>)</li>
                                        <li><strong>AR1 - Gửi thư</strong> (<span class="att-written-notice-absence">서면통지 결근</span>)</li>
                                    </ul>
                                    <div class="alert alert-warning mt-3">
                                        <strong id="attendanceCountingRulesTitle">📢 무단결근 카운팅 규칙:</strong>
                                        <ul class="mb-0 small">
                                            <li id="attendanceCountingRule1">AR1 카테고리만 무단결근으로 카운트</li>
                                            <li id="attendanceCountingRule2">2일까지는 incentive 지급 가능</li>
                                            <li id="attendanceCountingRule3">3일 이상 → incentive 0원</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="formula-box p-3 bg-light rounded">
                            <h6 id="attendanceConditionCriteriaTitle">조건 충족 기준:</h6>
                            <ul>
                                <li id="attendanceCriteria1"><strong>출근율:</strong> ≥ 88% (결근율 ≤ 12%)</li>
                                <li id="attendanceCriteria2"><strong>무단결근:</strong> ≤ 2일 (AR1 카테고리만 corresponding)</li>
                                <li id="attendanceCriteria3"><strong>actual 근무일:</strong> > 0일</li>
                                <li id="attendanceCriteria4"><strong>최소 근무일:</strong> ≥ 12일</li>
                            </ul>
                            <div class="alert alert-info mt-2">
                                <strong id="attendanceUnapprovedTitle">📊 Unapproved Absence Days 설직원:</strong>
                                <ul class="mb-0 small">
                                    <li id="attendanceUnapproved1">HR 시스템에서 제공하는 무단결근 thcount data</li>
                                    <li id="attendanceUnapproved2">AR1 (Vắng không phép) 카테고리만 집계</li>
                                    <li id="attendanceUnapproved3">서면통지 결근(Gửi thư)도 AR1에 포함</li>
                                    <li id="attendanceUnapproved4">incentive 조건: ≤2일 (개인별 최대 허용치)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- QIP Talent Pool 프로그램 설직원 섹션 -->
                <div class="card mb-4">
                    <div class="card-header" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white;">
                        <h5 class="mb-0" id="talentProgramTitle">🌟 QIP Talent Pool incentive 프로그램</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info mb-4">
                            <p class="mb-0" id="talentProgramIntro">
                                <strong>QIP Talent Pool</strong>은 우수한 성과를 보이는 인원들을 대상으로 하는 특별 incentive 프로그램입니다.
                                선정된 인원은 6개월간 매month 추가 보너스를 받게 됩니다.
                            </p>
                        </div>
                        
                        <h6 class="mb-3" id="talentProgramQualificationTitle">🎯 선정 기준</h6>
                        <ul id="talentProgramQualifications">
                            <li>업무 성과 우수자</li>
                            <li>품질 목표 달성률 상위 10%</li>
                            <li>팀워크 및 리더십 발휘</li>
                            <li>지속적인 개선 활동 참여</li>
                        </ul>
                        
                        <h6 class="mb-3 mt-4" id="talentProgramBenefitsTitle">💰 혜택</h6>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 id="talentProgramMonthlyBonusTitle">month 특별 보너스</h6>
                                        <h4 class="text-primary">150,000 VND</h4>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 id="talentProgramTotalBonusTitle">total 지급 예정액 (6개월)</h6>
                                        <h4 class="text-success">900,000 VND</h4>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <h6 class="mb-3" id="talentProgramProcessTitle">📋 평가 프로세스 (6개월 주기)</h6>
                        <div class="timeline-container">
                            <style>
                                .timeline-container {{
                                    position: relative;
                                    padding: 20px 0;
                                }}
                                .timeline-step {{
                                    display: flex;
                                    align-items: center;
                                    margin-bottom: 20px;
                                    position: relative;
                                }}
                                .timeline-step:not(:last-child)::before {{
                                    content: '';
                                    position: absolute;
                                    left: 20px;
                                    top: 40px;
                                    width: 2px;
                                    height: calc(100% + 20px);
                                    background: #dee2e6;
                                }}
                                .timeline-number {{
                                    width: 40px;
                                    height: 40px;
                                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                                    color: white;
                                    border-radius: 50%;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-weight: bold;
                                    flex-shrink: 0;
                                    margin-right: 15px;
                                }}
                                .timeline-content {{
                                    background: #f8f9fa;
                                    padding: 10px 15px;
                                    border-radius: 8px;
                                    flex: 1;
                                }}
                            </style>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">1</div>
                                <div class="timeline-content">
                                    <strong id="talentStep1Title">후보자 추천</strong>
                                    <p class="mb-0 text-muted small" id="talentStep1Desc">각 부서에서 우수 인원 추천</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">2</div>
                                <div class="timeline-content">
                                    <strong id="talentStep2Title">성과 평가</strong>
                                    <p class="mb-0 text-muted small" id="talentStep2Desc">최근 3개월간 성과 data 분석</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">3</div>
                                <div class="timeline-content">
                                    <strong id="talentStep3Title">위원회 심사</strong>
                                    <p class="mb-0 text-muted small" id="talentStep3Desc">QIP 운영위원회 final 심사</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">4</div>
                                <div class="timeline-content">
                                    <strong id="talentStep4Title">final 선정</strong>
                                    <p class="mb-0 text-muted small" id="talentStep4Desc">Talent Pool 멤버 확정 및 공지</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">5</div>
                                <div class="timeline-content">
                                    <strong id="talentStep5Title">보너스 지급</strong>
                                    <p class="mb-0 text-muted small" id="talentStep5Desc">매month 정기 incentive와 함께 지급</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">6</div>
                                <div class="timeline-content">
                                    <strong id="talentStep6Title">재평가</strong>
                                    <p class="mb-0 text-muted small" id="talentStep6Desc">6개월 후 재평가 실시</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="alert alert-warning mt-4">
                            <h6 id="talentProgramImportantTitle">⚠️ 중요 사항</h6>
                            <ul class="mb-0" id="talentProgramImportantNotes">
                                <li>Talent Pool 보너스는 기본 incentive와 by도로 지급됩니다</li>
                                <li>지급 기간 중 퇴사 시 자격이 자동 상실됩니다</li>
                                <li>성과 미달 시 조기 end될 count 있습니다</li>
                                <li>매 6개월마다 재평가를 통해 갱신 여부가 determination됩니다</li>
                            </ul>
                        </div>
                        
                        <div class="card mt-4" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                            <div class="card-body text-center">
                                <h5 id="talentProgramCurrentTitle">🎉 현재 Talent Pool 멤버</h5>
                                <div id="talentProgramCurrentMembers" class="mt-3">
                                    <!-- JavaScript로 현재 멤버 표시 -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- FAQ 섹션 -->
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0" id="faqSectionTitle">❓ 자주 묻는 질문 (FAQ)</h5>
                    </div>
                    <div class="card-body">
                        <style>
                            .faq-item {{
                                border: 1px solid #ddd;
                                border-radius: 5px;
                                margin-bottom: 10px;
                            }}
                            .faq-question {{
                                background-color: #f8f9fa;
                                padding: 15px;
                                cursor: pointer;
                                font-weight: bold;
                                border-radius: 5px;
                                transition: background-color 0.3s;
                            }}
                            .faq-question:hover {{
                                background-color: #e9ecef;
                            }}
                            .faq-question::before {{
                                content: "▶ ";
                                display: inline-block;
                                transition: transform 0.3s;
                            }}
                            .faq-question.active::before {{
                                transform: rotate(90deg);
                            }}
                            .faq-answer {{
                                padding: 15px;
                                display: none;
                                background-color: #fff;
                                border-top: 1px solid #ddd;
                            }}
                            .faq-answer.show {{
                                display: block;
                            }}
                        </style>
                        
                        <div class="faq-container">
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion1">
                                    Q1. 왜 나는 incentive를 못 받았나요? 조건을 확인하는 방법은?
                                </div>
                                <div class="faq-answer">
                                    <strong id="faqAnswer1Main">incentive를 받지 못한 주요 이유:</strong>
                                    <ul>
                                        <li id="faqAnswer1Reason1">최소 근무일 12일 미충족</li>
                                        <li id="faqAnswer1Reason2">출근율 88% 미만</li>
                                        <li id="faqAnswer1Reason3">무단결근 3일 이상</li>
                                        <li id="faqAnswer1Reason4">AQL failed (corresponding 직급)</li>
                                        <li id="faqAnswer1Reason5">5PRS 통과율 95% 미만 (corresponding 직급)</li>
                                    </ul>
                                    <span id="faqAnswer1CheckMethod">개인별 상세 페이지에서 본인의 조건 충족 여부를 확인할 count 있습니다.</span>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion2">
                                    Q2. 무단결근이 며칠까지 허용되나요?
                                </div>
                                <div class="faq-answer">
                                    <strong id="faqAnswer2Main">무단결근은 최대 2일까지 허용됩니다.</strong> <span id="faqAnswer2Detail">3일 이상 무단결근시 corresponding month incentive를 받을 count not found. 사전 승인된 휴가나 병가는 무단결근에 포함되지 not.</span>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion3">
                                    Q3. TYPE-2 직급의 incentive는 어떻게 calculation되나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer3Main">TYPE-2 직급의 incentive는 corresponding하는 TYPE-1 직급의 평균 incentive를 기준으로 calculation됩니다.</span>
                                    <span id="faqAnswer3Example">예를 들어:</span>
                                    <ul>
                                        <li id="faqAnswer3Example1">TYPE-2 GROUP LEADER는 TYPE-1 LINE LEADER 평균 incentive × 2</li>
                                        <li id="faqAnswer3Example2">TYPE-2 STITCHING INSPECTOR는 TYPE-1 ASSEMBLY INSPECTOR들의 평균 incentive</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion4">
                                    Q4. ASSEMBLY INSPECTOR의 연속 work 개월은 어떻게 calculation되나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer4Main">TYPE-1 ASSEMBLY INSPECTOR만 corresponding되며, 조건을 충족하며 incentive를 받은 개월count가 누적됩니다.</span>
                                    <ul>
                                        <li id="faqAnswer4Detail1">조건 미충족으로 incentive를 못 받으면 0개월로 리셋</li>
                                        <li id="faqAnswer4Detail2">12개월 이상 연속시 최대 incentive 1,000,000 VND</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion5">
                                    Q5. AQL failed가 무엇이고 어떤 영향을 미치나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer5Main">AQL(Acceptable Quality Limit)은 품질 검사 기준입니다.</span>
                                    <ul>
                                        <li id="faqAnswer5Detail1">개인 AQL failed: corresponding month에 품질 검사 failed한 경우</li>
                                        <li id="faqAnswer5Detail2">3연속 개월 실패: 지난 3개월 동안 연속으로 failed한 경우</li>
                                        <li id="faqAnswer5Detail3">AQL 관련 직급만 영향받음 (INSPECTOR 계열 등)</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion6">
                                    Q6. 5PRS 검사량이 부족하면 어떻게 되나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer6Main">5PRS 관련 직급은 다음 조건을 충족해야 합니다:</span>
                                    <ul>
                                        <li id="faqAnswer6Detail1">검사량 100족 이상</li>
                                        <li id="faqAnswer6Detail2">통과율 95% 이상</li>
                                    </ul>
                                    <strong id="faqAnswer6Conclusion">둘 중 하나라도 미충족시 incentive를 받을 count not found.</strong>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion7">
                                    Q7. 출산휴가나 병가 중에도 incentive를 받을 count 있나요?
                                </div>
                                <div class="faq-answer">
                                    <strong id="faqAnswer7Main">출산휴가나 장기 병가 중에는 incentive가 지급되지 not.</strong>
                                    <ul>
                                        <li id="faqAnswer7Detail1">최소 근무일 12일 조건을 충족할 count 없기 때문</li>
                                        <li id="faqAnswer7Detail2">복귀 후 조건 충족시 다시 incentive 수령 가능</li>
                                        <li id="faqAnswer7Detail3">ASSEMBLY INSPECTOR의 경우 연속 개월count는 0으로 리셋</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion8">
                                    Q8. 전month incentive와 차이가 나는 이유는 무엇인가요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer8Main">incentive 금액이 변동하는 주요 이유:</span>
                                    <ul>
                                        <li id="faqAnswer8Reason1"><strong>ASSEMBLY INSPECTOR</strong>: 연속 work 개월 변화</li>
                                        <li id="faqAnswer8Reason2"><strong>TYPE-2 직급</strong>: TYPE-1 평균값 변동</li>
                                        <li id="faqAnswer8Reason3"><strong>AQL INSPECTOR</strong>: Part1, Part2, Part3 조건 변화</li>
                                        <li id="faqAnswer8Reason4"><strong>조건 미충족</strong>: 하나라도 미충족시 0</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion9">
                                    Q9. TYPE-3에서 TYPE-2로 승진하면 incentive가 어떻게 변하나요?
                                </div>
                                <div class="faq-answer">
                                    <ul>
                                        <li id="faqAnswer9Detail1"><strong>TYPE-3</strong>: 조건 without 기본 150,000 VND (work시 자동 지급)</li>
                                        <li id="faqAnswer9Detail2"><strong>TYPE-2</strong>: 조건 충족 필요, TYPE-1 평균 기준 calculation</li>
                                        <li id="faqAnswer9Detail3">승진 후 조건 충족시 th반적으로 incentive 증가</li>
                                        <li id="faqAnswer9Detail4">하지만 조건 미충족시 0이 될 count 있으므로 주의 필요</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion10">
                                    Q10. 조건을 모두 충족했는데도 incentive가 0인 이유는 무엇인가요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer10Main">다음 사항을 재확인해 보세요:</span>
                                    <ul>
                                        <li id="faqAnswer10Reason1"><strong>숨겨진 조건</strong>: 직급별로 apply되는 모든 조건 확인</li>
                                        <li id="faqAnswer10Reason2"><strong>데이터 업데이트</strong>: 최신 data 반영 여부</li>
                                        <li id="faqAnswer10Reason3"><strong>특별한 사유</strong>: 징계, 경고 등 특별 사유</li>
                                        <li id="faqAnswer10Reason4"><strong>시스템 오류</strong>: HR 부서에 문의</li>
                                    </ul>
                                    <span id="faqAnswer10Conclusion">개인별 상세 페이지에서 조건별 충족 여부를 상세히 확인하시기 바랍니다.</span>
                                </div>
                            </div>

                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion11">
                                    Q11. TYPE-2 GROUP LEADER가 incentive를 못 받는 경우가 있나요?
                                </div>
                                <div class="faq-answer">
                                    <!-- 2025-12-05 수정: TYPE-2 GROUP LEADER는 TYPE-2 LINE LEADER 평균 우선 사용 -->
                                    <span id="faqAnswer11Main">TYPE-2 GROUP LEADER는 특별한 calculation 규칙이 apply됩니다:</span>
                                    <ul>
                                        <li id="faqAnswer11Detail1"><strong>기본 calculation:</strong> TYPE-2 LINE LEADER 평균 incentive × 2를 받습니다</li>
                                        <li id="faqAnswer11Detail2"><strong>Fallback calculation:</strong> TYPE-2 LINE LEADER 평균이 0 VND인 경우, TYPE-1 LINE LEADER 평균 × 2로 calculation됩니다</li>
                                        <li id="faqAnswer11Detail3"><strong>중요:</strong> TYPE-2 LINE LEADER 평균 기준으로 계산하여 동일 TYPE 직원들과의 일관성 유지</li>
                                        <li id="faqAnswer11Detail4"><strong>조건:</strong> TYPE-2는 출근 조건(1-4번)만 충족하면 incentive를 받을 count 있습니다</li>
                                    </ul>
                                    <span id="faqAnswer11Conclusion">따라서 출근 조건을 충족한 TYPE-2 GROUP LEADER는 항상 incentive를 받을 count 있도록 보장됩니다.</span>
                                </div>
                            </div>
                        </div>
                        
                        <script>
                            function toggleFAQ(element) {{
                                const answer = element.nextElementSibling;
                                const allAnswers = document.querySelectorAll('.faq-answer');
                                const allQuestions = document.querySelectorAll('.faq-question');
                                
                                // 다른 모든 답변 닫기
                                allAnswers.forEach(a => {{
                                    if (a !== answer) {{
                                        a.classList.remove('show');
                                    }}
                                }});
                                allQuestions.forEach(q => {{
                                    if (q !== element) {{
                                        q.classList.remove('active');
                                    }}
                                }});
                                
                                // 현재 항목 토글
                                answer.classList.toggle('show');
                                element.classList.toggle('active');
                            }}
                        </script>
                    </div>
                </div>
                
                <!-- Multi-language Script - Removed duplicate event listener -->
            </div>

            <!-- 조직도 탭 -->
            <div id="orgchart" class="tab-content">
                <div class="card">
                    <div class="card-body">
                        <h3 id="orgChartTitle" class="mb-4">조직 구조도 (TYPE-1)</h3>

                        <!-- 제외된 직급 안내 -->
                        <div class="alert alert-info mb-3" style="background: #e3f2fd; border: 1px solid #1976d2; color: #0d47a1;">
                            <i class="fas fa-info-circle"></i>
                            <strong><span id="orgChartNoteLabel">참고</span>:</strong>
                            <span id="orgChartExcludedPositions">AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다.</span>
                        </div>

                        <!-- 동적 경로 표시 (Breadcrumb) -->
                        <div id="orgBreadcrumb" class="breadcrumb mb-3" style="background: #f8f9fa; padding: 10px; border-radius: 4px;">
                            <span id="orgBreadcrumbText" style="color: #666;">total 조직</span>
                        </div>

                        <!-- Building별 QC 요약 카드 (SUPERVISOR, A.MANAGER 요청 - 2025-12-16) -->
                        <div id="buildingSummaryCards" class="row mb-4">
                            <!-- JavaScript에서 동적으로 생성 -->
                        </div>

                        <!-- 필터 옵션 -->
                        <div class="row mb-3">
                            <div class="col-md-3">
                                <select id="orgIncentiveFilter" class="form-select" onchange="updateOrgChart()">
                                    <option value="" id="filterAll">total 보기</option>
                                    <option value="paid" id="filterPaid">incentive 수령자</option>
                                    <option value="unpaid" id="filterUnpaid">incentive 미수령자</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <select id="orgBuildingFilter" class="form-select" onchange="filterOrgChartByBuilding()">
                                    <option value="all" id="buildingFilterAll">전체 Building</option>
                                    <option value="A">Building A</option>
                                    <option value="B">Building B</option>
                                    <option value="B3">Building B3</option>
                                    <option value="C">Building C</option>
                                    <option value="D">Building D</option>
                                </select>
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-primary w-100" onclick="expandAll()">
                                    <i class="fas fa-expand"></i> <span id="expandAllBtn">전체 펼치기</span>
                                </button>
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-secondary w-100" onclick="collapseAll()">
                                    <i class="fas fa-compress"></i> <span id="collapseAllBtn">전체 접기</span>
                                </button>
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-primary w-100" onclick="resetOrgChart()">
                                    <i class="fas fa-redo"></i> <span id="resetViewBtn">초기화</span>
                                </button>
                            </div>
                        </div>

                        <!-- 범례 -->
                        <div class="mb-3">
                            <div class="d-flex flex-wrap gap-3">
                                <span><span style="display:inline-block; width:15px; height:15px; background:#1f77b4; border-radius:3px;"></span> Manager</span>
                                <span><span style="display:inline-block; width:15px; height:15px; background:#2ca02c; border-radius:3px;"></span> Supervisor</span>
                                <span><span style="display:inline-block; width:15px; height:15px; background:#ff7f0e; border-radius:3px;"></span> Group Leader</span>
                                <span><span style="display:inline-block; width:15px; height:15px; background:#d62728; border-radius:3px;"></span> Line Leader</span>
                                <span><span style="display:inline-block; width:15px; height:15px; background:#9467bd; border-radius:3px;"></span> Inspector</span>
                                <span><span style="display:inline-block; width:15px; height:15px; background:#8c564b; border-radius:3px;"></span> Others</span>
                                <span class="ms-3"><span style="display:inline-block; width:15px; height:15px; border: 2px solid #28a745; border-radius:3px;"></span> <span id="legendReceived">incentive 수령</span></span>
                                <span><span style="display:inline-block; width:15px; height:15px; border: 2px solid #dc3545; border-radius:3px;"></span> <span id="legendNotReceived">incentive 미수령</span></span>
                            </div>
                        </div>

                        <!-- 새로운 접이식 조직도 컨테이너 -->
                        <div id="orgChartContainer" class="collapsible-tree">
                            <!-- 제목 및 설직원 -->
                            <div class="org-header">
                                <h4 id="orgChartTitleMain">TYPE-1 관리자 incentive 구조</h4>
                                <p id="orgChartSubtitleMain" class="text-muted">TYPE-1 managers receiving incentive 기준 subordinate performance</p>
                            </div>

                            <!-- 검색 및 필터 컨트롤 -->
                            <div class="org-controls mb-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="input-group">
                                            <span class="input-group-text"><i class="fas fa-search"></i></span>
                                            <input type="text" id="orgSearchInput" class="form-control" placeholder="직원 이름 또는 ID 검색...">
                                            <button class="btn btn-outline-secondary" id="orgSearchClear" type="button">
                                                <i class="fas fa-times"></i>
                                            </button>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="btn-group" role="group">
                                            <button id="expandAllBtn" class="btn btn-outline-primary">
                                                <i class="fas fa-expand"></i> <span id="expandAllText">모두 펼치기</span>
                                            </button>
                                            <button id="collapseAllBtn" class="btn btn-outline-primary">
                                                <i class="fas fa-compress"></i> <span id="collapseAllText">모두 접기</span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 사용 안내 -->
                            <div class="alert alert-info mb-3" role="alert" style="background: linear-gradient(135deg, #ef444415 0%, #dc262615 100%); border-left: 4px solid #6366f1;">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>💡 <span id="usageGuideTitle"></span></strong> <span id="usageGuideText"></span>
                                <span class="float-end text-muted small" id="usageGuideHelpText"></span>
                            </div>

                            <!-- 범례 -->
                            <div class="org-legend mb-3">
                                <h6 id="legendTitle">범례</h6>
                                <div class="legend-items">
                                    <span class="legend-item">
                                        <span class="legend-box" style="background:#2ca02c;"></span>
                                        <span id="legendManager">Manager</span>
                                    </span>
                                    <span class="legend-item">
                                        <span class="legend-box" style="background:#1f77b4;"></span>
                                        <span id="legendSupervisor">Supervisor</span>
                                    </span>
                                    <span class="legend-item">
                                        <span class="legend-box" style="background:#ff7f0e;"></span>
                                        <span id="legendGroupLeader">Group Leader</span>
                                    </span>
                                    <span class="legend-item">
                                        <span class="legend-box" style="background:#d62728;"></span>
                                        <span id="legendLineLeader">Line Leader</span>
                                    </span>
                                    <span class="legend-item ms-3">
                                        <span class="legend-dot received"></span>
                                        <span id="legendIncentiveReceived">incentive 수령</span>
                                    </span>
                                    <span class="legend-item">
                                        <span class="legend-dot not-received"></span>
                                        <span id="legendNoIncentive">incentive 미수령</span>
                                    </span>
                                </div>
                            </div>

                            <div id="orgTreeContent">
                                <!-- JavaScript로 동적 creation됨 -->
                            </div>
                        </div>

                        <!-- 모바일 조직도 리스트 컨테이너 (모바일 모드에서만 표시) -->
                        <div id="mobileOrgList" class="mobile-org-wrapper">
                            <!-- JavaScript에서 동적으로 생성됨 -->
                        </div>


                        <!-- 직원 정보 툴팁 -->
                        <div id="orgTooltip" style="position: absolute; visibility: hidden; background: white; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 1000;">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 검증 탭 -->
        <div id="validation" class="tab-content">
            <h3 id="validationTabTitle">요약 및 시스템 검증</h3>

            <!-- interim report 알림 (20일 이전 report인 경우에만 표시) -->
            <div id="interimReportNotice" class="alert alert-warning" style="display: none;">
                <i class="fas fa-info-circle"></i>
                <span id="interimReportText">interim report - 최소 근무일(12일) 및 출근율(88%) 조건이 apply되지 not</span>
            </div>

            <!-- KPI 카드 스타th -->
            <style>
                .kpi-cards-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .kpi-card {{
                    padding: 25px;
                    border-radius: 15px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                    background: white;
                    border: 1px solid #e0e0e0;
                }}

                .kpi-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                }}

                .kpi-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 5px;
                    background: linear-gradient(90deg, var(--card-color-1), var(--card-color-2));
                }}

                .kpi-icon {{
                    font-size: 2.5em;
                    margin-bottom: 15px;
                    display: inline-block;
                    background: linear-gradient(135deg, var(--card-color-1), var(--card-color-2));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
                }}

                .kpi-value {{
                    font-size: 2.8em;
                    font-weight: 700;
                    color: #2c3e50;
                    margin: 10px 0;
                    letter-spacing: -0.5px;
                }}

                .kpi-label {{
                    color: #7f8c8d;
                    font-size: 0.95em;
                    font-weight: 500;
                    margin-top: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .kpi-subtitle {{
                    color: #95a5a6;
                    font-size: 0.75em;
                    font-weight: 400;
                    margin-top: 5px;
                    font-style: italic;
                    opacity: 0.9;
                }}

                .kpi-card.warning {{
                    background: #fff3cd;
                    border-color: #ffc107;
                }}

                .kpi-card.danger {{
                    background: #f8d7da;
                    border-color: #dc3545;
                }}

                .kpi-card.success {{
                    background: #d4edda;
                    border-color: #28a745;
                }}

                .kpi-card.info {{
                    background: #d1ecf1;
                    border-color: #17a2b8;
                }}
            </style>

            <!-- KPI 카드 그리드 -->
            <div class="kpi-cards-grid">
                <!-- KPI 카드 1: 총 근무일수 -->
                <div class="kpi-card" onclick="showValidationModal('totalWorkingDays')" style="--card-color-1: #4a90e2; --card-color-2: #5ca0f2; box-shadow: 0 4px 15px rgba(74, 144, 226, 0.1);">
                    <div class="kpi-icon">📅</div>
                    <div class="kpi-value" id="kpiTotalWorkingDays">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.totalWorkingDays">총 근무일수</div>
                </div>

                <!-- KPI 카드 2: 무단결근 3일 이상 -->
                <div class="kpi-card" onclick="showValidationModal('absentWithoutInform')" style="--card-color-1: #f39c12; --card-color-2: #f1c40f; box-shadow: 0 4px 15px rgba(243, 156, 18, 0.1);"
                     title="" data-i18n-title="validationKpi.absentWithoutInformTooltip">
                    <div class="kpi-icon">⚠️</div>
                    <div class="kpi-value" id="kpiAbsentWithoutInform">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.absentWithoutInform">무단결근 ≥3일</div>
                    <div class="kpi-subtitle" data-i18n="validationKpi.absentWithoutInformSubtitle">인센티브 자동 제외</div>
                </div>

                <!-- KPI 카드 3: 실제 근무일 0일 -->
                <div class="kpi-card" onclick="showValidationModal('zeroWorkingDays')" style="--card-color-1: #e74c3c; --card-color-2: #c0392b; box-shadow: 0 4px 15px rgba(231, 76, 60, 0.1);"
                     title="" data-i18n-title="validationKpi.zeroWorkingDaysTooltip">
                    <div class="kpi-icon">🚫</div>
                    <div class="kpi-value" id="kpiZeroWorkingDays">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.zeroWorkingDays">실제 근무일 0일</div>
                    <div class="kpi-subtitle" data-i18n="validationKpi.zeroWorkingDaysSubtitle">정당한 사유 포함</div>
                </div>

                <!-- KPI 카드 4: 최소 근무일 미충족 -->
                <div class="kpi-card" onclick="showValidationModal('minimumDaysNotMet')" style="--card-color-1: #95a5a6; --card-color-2: #7f8c8d; box-shadow: 0 4px 15px rgba(149, 165, 166, 0.1);">
                    <div class="kpi-icon">📉</div>
                    <div class="kpi-value" id="kpiMinimumDaysNotMet">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.minimumDaysNotMet">최소 근무일 미충족</div>
                </div>

                <!-- KPI 카드 5: 출근율 88% 미만 -->
                <div class="kpi-card" onclick="showValidationModal('attendanceBelow88')" style="--card-color-1: #9b59b6; --card-color-2: #8e44ad; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.1);"
                     title="" data-i18n-title="validationKpi.attendanceBelow88Tooltip">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value" id="kpiAttendanceBelow88">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.attendanceBelow88">출근율 88% 미만</div>
                    <div class="kpi-subtitle" data-i18n="validationKpi.attendanceBelow88Subtitle">정당한 사유 제외</div>
                </div>

                <!-- KPI 카드 6: AQL FAIL 보유자 -->
                <div class="kpi-card" onclick="showValidationModal('aqlFail')" style="--card-color-1: #e67e22; --card-color-2: #d35400; box-shadow: 0 4px 15px rgba(230, 126, 34, 0.1);">
                    <div class="kpi-icon">❌</div>
                    <div class="kpi-value" id="kpiAqlFail">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.aqlFail">AQL FAIL 보유자</div>
                </div>

                <!-- KPI 카드 7: 3개월 연속 AQL FAIL -->
                <div class="kpi-card" onclick="showValidationModal('consecutiveAqlFail')" style="--card-color-1: #c0392b; --card-color-2: #a93226; box-shadow: 0 4px 15px rgba(192, 57, 43, 0.1);">
                    <div class="kpi-icon">🔴</div>
                    <div class="kpi-value" id="kpiConsecutiveAqlFail">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.consecutiveAqlFail">3개월 연속 AQL FAIL</div>
                </div>

                <!-- KPI 카드 8: 구역 AQL Reject 3% 이상 -->
                <div class="kpi-card" onclick="showValidationModal('areaRejectRate')" style="--card-color-1: #3498db; --card-color-2: #2980b9; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.1);">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value" id="kpiAreaRejectRate">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.areaRejectRate">구역 AQL Reject ≥3%</div>
                </div>

                <!-- KPI 카드 9: 5PRS 통과율 < 95% -->
                <div class="kpi-card" onclick="showValidationModal('lowPassRate')" style="--card-color-1: #9b59b6; --card-color-2: #8e44ad; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.1);">
                    <div class="kpi-icon">📉</div>
                    <div class="kpi-value" id="kpiLowPassRate">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.lowPassRate">5PRS Pass Rate < 95%</div>
                </div>

                <!-- KPI 카드 10: 5PRS 검사량 < 100족 -->
                <div class="kpi-card" onclick="showValidationModal('lowInspectionQty')" style="--card-color-1: #1abc9c; --card-color-2: #16a085; box-shadow: 0 4px 15px rgba(26, 188, 156, 0.1);">
                    <div class="kpi-icon">🔍</div>
                    <div class="kpi-value" id="kpiLowInspectionQty">-</div>
                    <div class="kpi-label" data-i18n="validationKpi.lowInspectionQty">5PRS Inspection < 100 pairs</div>
                </div>
            </div>
        </div>
    </div>

    <!-- 직원 상세 모달 (Bootstrap 5) -->
    <div class="modal fade" id="employeeModal" tabindex="-1" aria-labelledby="modalTitle" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modalTitle">직원 상세 정보</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="modalBody">
                    <!-- JavaScript로 채워질 예정 -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary btn-lg" data-bs-dismiss="modal" id="employeeModalCloseBtn" data-translate="closeButton">닫기</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Position 상세 모달 (Bootstrap 5) -->
    <div class="modal fade" id="positionModal" tabindex="-1" aria-labelledby="positionModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="positionModalLabel" data-translate="positionModal">직급별 상세 정보</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="positionModalBody">
                    <!-- JavaScript로 채워질 예정 -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary btn-lg" data-bs-dismiss="modal" id="positionModalCloseBtn" data-translate="closeButton">닫기</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 모든 JSON data를 by도의 script 태그에 저장 -->
    <script type="application/json" id="employeeDataBase64">
        {직원_json_base64}
    </script>

    <script type="application/json" id="translationsData">
        {translations_js}
    </script>

    <script type="application/json" id="positionMatrixData">
        {position_matrix_json}
    </script>

    <script type="application/json" id="excelDashboardDataBase64">
        {excel_data_b64}
    </script>

    <script type="application/json" id="aqlInspectorStatsBase64">
        {aql_inspector_stats_b64}
    </script>

    <script type="application/json" id="aqlFileStatsBase64">
        {aql_file_stats_b64}
    </script>

    <script type="application/json" id="auditorMappingBase64">
        {auditor_mapping_b64}
    </script>

    <script type="application/json" id="aqlIncentiveConfigBase64">
        {aql_incentive_config_b64}
    </script>

    <script>
        // ==================== 보안: 세션 검증 ====================
        (function() {{
            const SESSION_KEY = 'qip_auth_session_v2';
            const SESSION_TIMEOUT = 30 * 60 * 1000; // 30분

            function validateSession() {{
                const session = sessionStorage.getItem(SESSION_KEY);

                if (!session) {{
                    // 세션 없음 - 인증 페이지로 리다이렉트
                    window.location.href = 'auth.html';
                    return false;
                }}

                try {{
                    const sessionData = JSON.parse(session);
                    const now = Date.now();

                    if (now - sessionData.loginTime > SESSION_TIMEOUT) {{
                        // 세션 만료
                        sessionStorage.removeItem(SESSION_KEY);
                        alert('Session expired. Please login again.\\n세션이 만료되었습니다. 다시 로그인하세요.');
                        window.location.href = 'auth.html';
                        return false;
                    }}

                    return true;
                }} catch (e) {{
                    sessionStorage.removeItem(SESSION_KEY);
                    window.location.href = 'auth.html';
                    return false;
                }}
            }}

            // 페이지 로드 시 세션 검증
            if (!validateSession()) {{
                return;
            }}

            // 주기적 세션 검증 (1분마다)
            setInterval(validateSession, 60000);

            // 우클릭 방지
            document.addEventListener('contextmenu', function(e) {{
                e.preventDefault();
                return false;
            }});

            // 복사 방지 (선택적)
            document.addEventListener('copy', function(e) {{
                // 복사 허용하되 경고만 표시
                console.warn('⚠️ 데이터 복사가 감지되었습니다. 기밀 정보 유출에 주의하세요.');
            }});

            // Ctrl+S, Ctrl+P 방지 (저장/인쇄 방지)
            document.addEventListener('keydown', function(e) {{
                if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'p')) {{
                    e.preventDefault();
                    alert('This action is disabled for security reasons.\\n보안상 이 기능은 비활성화되어 있습니다.');
                    return false;
                }}
            }});

            // 개발자 도구 경고
            const devtoolsWarning = () => {{
                console.clear();
                console.log('%c⚠️ WARNING / 경고', 'font-size: 30px; color: red; font-weight: bold;');
                console.log('%cThis dashboard contains confidential employee information.', 'font-size: 16px; color: orange;');
                console.log('%c이 대시보드는 기밀 직원 정보를 포함하고 있습니다.', 'font-size: 16px; color: orange;');
                console.log('%cUnauthorized access or data extraction is prohibited and will be reported.', 'font-size: 14px;');
                console.log('%c무단 접근 또는 데이터 추출은 금지되며 보고됩니다.', 'font-size: 14px;');
                console.log('%c', 'font-size: 1px;'); // Clear previous console output
            }};

            devtoolsWarning();
            setInterval(devtoolsWarning, 3000);
        }})();
        // ==================== 보안 코드 종료 ====================

        // UTF-8 Base64 디코딩 함count 추가
        function base64DecodeUnicode(str) {{
            // Base64 디코딩 후 UTF-8 처리
            try {{
                const binaryString = atob(str);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {{
                    bytes[i] = binaryString.charCodeAt(i);
                }}
                const decoder = new TextDecoder('utf-8');
                return decoder.decode(bytes);
            }} catch (e) {{
                console.error('UTF-8 decoding failed:', e);
                // Fallback to regular atob
                return atob(str);
            }}
        }}

        // Make employeeData globally accessible for validation tab
        // Decode base64 and parse JSON safely
        // CRITICAL FIX: Wrap in DOMContentLoaded to ensure DOM elements exist

        // Declare global variables that will be populated after DOM loads
        let translations = {{}};
        let positionMatrix = {{}};
        let excelDashboardData = {{}};

        // CRITICAL FIX: Initialize employeeData globally BEFORE DOMContentLoaded
        window.employeeData = [];

        // CRITICAL FIX: Define showEmployeeDetail globally BEFORE DOMContentLoaded
        // This ensures onclick handlers work immediately after page load
        window.showEmployeeDetail = function(empNo) {{
            // Safety check: wait for data to be loaded
            if (!window.employeeData || window.employeeData.length === 0) {{
                console.error('Employee data not yet loaded. Please wait...');
                setTimeout(() => window.showEmployeeDetail(empNo), 500);
                return;
            }}

            // Safety check: wait for DOM elements
            const modal = document.getElementById('employeeModal');
            if (!modal) {{
                console.error('Modal element not found. DOM not ready.');
                return;
            }}

            // Actual function will be replaced after DOMContentLoaded
            // This is just a placeholder to prevent errors
            console.log('showEmployeeDetail called for:', empNo);
        }};

        document.addEventListener('DOMContentLoaded', function() {{
            // employeeData already initialized globally
            window.aqlInspectorStats = null;
            try {{
                // DOM에서 Base64 data read
                const base64Element = document.getElementById('employeeDataBase64');

                if (!base64Element) {{
                    console.error('[ERROR] employeeDataBase64 element not found in DOM!');
                    throw new Error('employeeDataBase64 element not found');
                }}

                const base64Data = base64Element.textContent.trim();
            const jsonStr = base64DecodeUnicode(base64Data);  // UTF-8 지원 디코딩 use
            const employeeData = JSON.parse(jsonStr);
            window.employeeData = employeeData;
            console.log('Employee data loaded successfully:', employeeData.length, '직원');

            // TYPE 테이블 생성 함수 정의 (데이터 로드 직후, 호출 전에)
            function generateTypeTable() {{
                console.log('Generating TYPE table...');

                const typeSummaryBody = document.getElementById('typeSummaryBody');
                if (!typeSummaryBody) {{
                    console.error('typeSummaryBody element not found');
                    return;
                }}

                // 데이터가 없으면 employeeData를 사용
                if (!window.employeeData || window.employeeData.length === 0) {{
                    console.log('No employee data available for TYPE table');
                    typeSummaryBody.innerHTML = '<tr><td colspan="7" class="text-center">데이터 없음</td></tr>';
                    return;
                }}

                // TYPE별 집계
                const typeStats = {{
                    'TYPE-1': {{ total: 0, eligible: 0, amount: 0 }},
                    'TYPE-2': {{ total: 0, eligible: 0, amount: 0 }},
                    'TYPE-3': {{ total: 0, eligible: 0, amount: 0 }}
                }};

                window.employeeData.forEach(emp => {{
                    const empType = emp['type'] || emp['ROLE TYPE STD'] || 'TYPE-2';
                    // 현재 월의 인센티브 컬럼 동적으로 찾기
                    const monthLower = '{month.lower()}';
                    const monthCapitalized = monthLower.charAt(0).toUpperCase() + monthLower.slice(1);
                    const incentiveAmount = parseFloat(
                        emp[monthLower + '_incentive'] ||
                        emp[monthCapitalized + '_Incentive'] ||
                        emp['Final Incentive amount']
                    ) || 0;

                    if (typeStats[empType]) {{
                        typeStats[empType].total++;
                        if (incentiveAmount > 0) {{
                            typeStats[empType].eligible++;
                            typeStats[empType].amount += incentiveAmount;
                        }}
                    }}
                }});

                // 테이블 생성
                let tableHTML = '';
                let totalAll = 0, eligibleAll = 0, amountAll = 0;

                // 현재 언어에 맞는 단위 가져오기
                const peopleUnit = getUnit('people');

                ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {{
                    const stats = typeStats[type];
                    const paymentRate = stats.total > 0 ? ((stats.eligible / stats.total) * 100).toFixed(1) : '0.0';
                    const avgEligible = stats.eligible > 0 ? Math.round(stats.amount / stats.eligible) : 0;
                    const avgTotal = stats.total > 0 ? Math.round(stats.amount / stats.total) : 0;

                    totalAll += stats.total;
                    eligibleAll += stats.eligible;
                    amountAll += stats.amount;

                    const typeClass = type === 'TYPE-1' ? 'primary' : (type === 'TYPE-2' ? 'warning' : 'success');

                    tableHTML += `
                        <tr>
                            <td><span class="badge bg-${{typeClass}}">${{type}}</span></td>
                            <td>${{stats.total}}${{peopleUnit}}</td>
                            <td>${{stats.eligible}}${{peopleUnit}}</td>
                            <td>${{paymentRate}}%</td>
                            <td>${{stats.amount.toLocaleString()}} VND</td>
                            <td>${{avgEligible.toLocaleString()}} VND</td>
                            <td>${{avgTotal.toLocaleString()}} VND</td>
                        </tr>
                    `;
                }});

                // 합계 행 추가
                const totalPaymentRate = totalAll > 0 ? ((eligibleAll / totalAll) * 100).toFixed(1) : '0.0';
                const totalAvgEligible = eligibleAll > 0 ? Math.round(amountAll / eligibleAll) : 0;
                const totalAvgTotal = totalAll > 0 ? Math.round(amountAll / totalAll) : 0;

                tableHTML += `
                    <tr class="table-info fw-bold">
                        <td>Total</td>
                        <td>${{totalAll}}${{peopleUnit}}</td>
                        <td>${{eligibleAll}}${{peopleUnit}}</td>
                        <td>${{totalPaymentRate}}%</td>
                        <td>${{amountAll.toLocaleString()}} VND</td>
                        <td>${{totalAvgEligible.toLocaleString()}} VND</td>
                        <td>${{totalAvgTotal.toLocaleString()}} VND</td>
                    </tr>
                `;

                typeSummaryBody.innerHTML = tableHTML;
                console.log('TYPE table generated successfully');
            }}

            // 전역 스코프에 함수 노출
            window.generateTypeTable = generateTypeTable;

            // TYPE 테이블 즉시 생성 (함수 정의 및 노출 완료 직후)
            console.log('Calling generateTypeTable immediately after definition...');
            generateTypeTable();

            // AQL Inspector Stats load (inspectors 인원 기준)
            const aqlStatsElement = document.getElementById('aqlInspectorStatsBase64');
            if (aqlStatsElement) {{
                const aqlStatsBase64 = aqlStatsElement.textContent.trim();
                const aqlStatsJson = base64DecodeUnicode(aqlStatsBase64);
                window.aqlInspectorStats = JSON.parse(aqlStatsJson);
                console.log('AQL Inspector Stats loaded successfully:', Object.keys(window.aqlInspectorStats).length, 'areas');
            }}

            // AQL File Stats load (검사 casescount 기준 - Table 1용)
            const aqlFileStatsElement = document.getElementById('aqlFileStatsBase64');
            if (aqlFileStatsElement) {{
                const aqlFileStatsBase64 = aqlFileStatsElement.textContent.trim();
                const aqlFileStatsJson = base64DecodeUnicode(aqlFileStatsBase64);
                window.aqlFileStats = JSON.parse(aqlFileStatsJson);
                console.log('AQL File Stats loaded successfully:', Object.keys(window.aqlFileStats).length, 'areas');
            }} else {{
                console.warn('AQL File Stats element not found, using empty object');
                window.aqlFileStats = {{}};
            }}

            // Auditor/Trainer Area Mapping load
            const auditorMappingElement = document.getElementById('auditorMappingBase64');
            if (auditorMappingElement) {{
                const auditorMappingBase64 = auditorMappingElement.textContent.trim();
                const auditorMappingJson = base64DecodeUnicode(auditorMappingBase64);
                window.auditorAreaMapping = JSON.parse(auditorMappingJson);
                console.log('Auditor Area Mapping loaded:',
                    Object.keys(window.auditorAreaMapping.auditor_trainer_areas || {{}}).length, 'auditors,',
                    Object.keys(window.auditorAreaMapping.model_master?.employees || {{}}).length, 'model masters');
            }} else {{
                console.warn('Auditor Area Mapping element not found, using empty object');
                window.auditorAreaMapping = {{}};
            }}

            // AQL Inspector 인센티브 Config 로드 (Part 1/2/3 breakdown 표시용)
            const aqlIncentiveConfigElement = document.getElementById('aqlIncentiveConfigBase64');
            if (aqlIncentiveConfigElement) {{
                const aqlIncentiveConfigBase64 = aqlIncentiveConfigElement.textContent.trim();
                const aqlIncentiveConfigJson = base64DecodeUnicode(aqlIncentiveConfigBase64);
                window.aqlIncentiveConfig = JSON.parse(aqlIncentiveConfigJson);
                console.log('AQL Inspector Incentive Config loaded:',
                    Object.keys(window.aqlIncentiveConfig.aql_inspectors || {{}}).length, 'inspectors');
            }} else {{
                console.warn('AQL Incentive Config element not found, using empty object');
                window.aqlIncentiveConfig = {{ aql_inspectors: {{}}, parts: {{}} }};
            }}

            // Build condition_results array from individual condition fields
            // CRITICAL FIX: Python이 이미 condition_results를 creation했다면 그것을 use
            employeeData.forEach(emp => {{
                // Python에서 이미 condition_results를 creation했는지 확인
                if (!emp.condition_results || emp.condition_results.length === 0) {{
                    // JavaScript에서 fallback으로 creation (Python data가 없는 경우)
                    emp.condition_results = [];

                    // Map condition names for display
                    const conditionNames = {{
                        1: '출근율 (Attendance Rate)',
                        2: '무단결근 (Unapproved Absence)',
                        3: 'actual 근무일count (Actual Working Days)',
                        4: '최소 근무일count (Minimum Working Days)',
                        5: 'AQL 개인 failed (Personal AQL Failure)',
                        6: 'AQL 연속 failed (Continuous AQL Failure)',
                        7: 'AQL 팀 영역 (Team Area AQL)',
                        8: '영역 거부 (Area Reject)',
                        9: '5PRS 합격률 (5PRS Pass Rate)',
                        10: '5PRS 검사 count량 (5PRS Inspection Qty)'
                    }};

                    // Process up to 10 conditions
                    for (let i = 1; i <= 10; i++) {{
                        const valueField = `cond_${{i}}_value`;
                        const thresholdField = `cond_${{i}}_threshold`;

                        // statusField 먼저 확인 (CRITICAL FIX)
                        let statusField = '';
                        if (i === 1) statusField = 'cond_1_attendance_rate';
                        else if (i === 2) statusField = 'cond_2_unapproved_absence';
                        else if (i === 3) statusField = 'cond_3_actual_working_days';
                        else if (i === 4) statusField = 'cond_4_minimum_days';
                        else if (i === 5) statusField = 'cond_5_aql_personal_failure';
                        else if (i === 6) statusField = 'cond_6_aql_continuous';
                        else if (i === 7) statusField = 'cond_7_aql_team_area';
                        else if (i === 8) statusField = 'cond_8_area_reject';
                        else if (i === 9) statusField = 'cond_9_5prs_pass_rate';
                        else if (i === 10) statusField = 'cond_10_5prs_inspection_qty';

                        // statusField가 null/undefined/'N/A'/'NOT_APPLICABLE'이면 조건은 corresponding 직원에게 apply되지 않음
                        const statusValue = emp[statusField];
                        if (statusValue === null || statusValue === undefined ||
                            statusValue === 'N/A' || statusValue === 'NOT_APPLICABLE' || statusValue === '' ||
                            (typeof statusValue === 'number' && isNaN(statusValue))) {{
                            // excluded_conditions: 조건 자체가 N/A이므로 추가하지 않음
                            continue;
                        }}

                        // Check if this condition exists in the data
                        if (emp[valueField] !== undefined) {{
                            const value = emp[valueField];
                            const threshold = emp[thresholdField];

                            // Determine if condition is met
                            let is_met = false;
                            let is_na = false;

                            // Check for N/A values
                            if (value === 'N/A' || value === null || value === '' ||
                                (typeof value === 'number' && isNaN(value))) {{
                                is_na = true;
                            }} else {{
                                // Check if condition is met
                                if (statusValue === 'PASS') {{
                                    is_met = true;
                                }} else if (emp[`cond_${{i}}_met`] === 'PASS' || emp[`cond_${{i}}_met`] === true) {{
                                    is_met = true;
                                }}
                            }}

                            // Add condition result
                            emp.condition_results.push({{
                                id: i,
                                name: conditionNames[i] || `Condition ${{i}}`,
                                actual: value,
                                threshold: threshold,
                                is_met: is_met,
                                is_na: is_na
                            }});
                        }}
                    }}

                    console.log(`Employee ${{emp['Employee No'] || emp.employee_no}} - JavaScript generated ${{emp.condition_results.length}} conditions`);
                }} else {{
                    console.log(`Employee ${{emp['Employee No'] || emp.employee_no}} - Using Python's ${{emp.condition_results.length}} conditions`);
                }}
            }});

            // data load 후 즉시 상단 카드 업데이트
            let totalCount = employeeData.length;
            let paidCount = 0;
            let totalAmount = 0;

            employeeData.forEach(emp => {{
                const amount = parseInt(
                    emp['{month.lower()}_incentive'] ||
                    emp['{month.capitalize()}_Incentive'] ||
                    emp['Final Incentive amount'] ||
                    0
                );
                if (amount > 0) {{
                    paidCount++;
                    totalAmount += amount;
                }}
            }});

            // 초기 통계 저장
            window.dashboardStats = {{
                total: totalCount,
                paid: paidCount,
                amount: totalAmount,
                rate: totalCount > 0 ? (paidCount / totalCount * 100).toFixed(1) : '0.0'
            }};

            console.log('초기 통계: total ' + totalCount + '직원, 지급 ' + paidCount + '직원, total액 ' + totalAmount + ' VND');

            }} catch (e) {{
                console.error("Failed to parse employee data:", e);
                window.employeeData = [];
                window.dashboardStats = {{ total: 0, paid: 0, amount: 0, rate: '0.0' }};
            }}

            // DOM에서 translations data read
            try {{
                const translationsElement = document.getElementById('translationsData');
                if (!translationsElement) {{
                    console.error('[ERROR] translationsData element not found in DOM!');
                }} else {{
                    translations = JSON.parse(translationsElement.textContent.trim());
                    console.log('Translations loaded successfully');
                }}
            }} catch (e) {{
                console.error("Failed to parse translations data:", e);
            }}

            // DOM에서 positionMatrix data read
            try {{
                const positionMatrixElement = document.getElementById('positionMatrixData');
                if (!positionMatrixElement) {{
                    console.error('[ERROR] positionMatrixData element not found in DOM!');
                }} else {{
                    positionMatrix = JSON.parse(positionMatrixElement.textContent.trim());
                    console.log('Position matrix loaded successfully');
                }}
            }} catch (e) {{
                console.error("Failed to parse position matrix data:", e);
            }}

            // AQL 통계 data (actual 검사 횟count)
            // AQL 통계는 이제 Excel file에서 directly use (Single Source of Truth)

            // DOM에서 Excel dashboard data read (Base64 디코딩)
            try {{
                const excelDataElement = document.getElementById('excelDashboardDataBase64');
                if (!excelDataElement) {{
                    console.error('[ERROR] excelDashboardDataBase64 element not found in DOM!');
                }} else if (excelDataElement.textContent.trim()) {{
                    const base64Data = excelDataElement.textContent.trim();
                    const jsonStr = atob(base64Data);
                    excelDashboardData = JSON.parse(jsonStr);
                    window.excelDashboardData = excelDashboardData; // Also store in window for backward compatibility

                    // attendance raw data를 전역 변count로 설정
                    if (excelDashboardData.attendance_raw_data) {{
                        window.attendanceRawData = excelDashboardData.attendance_raw_data;
                        console.log('Attendance raw data loaded:', Object.keys(window.attendanceRawData).length, '직원');
                    }}

                    console.log('Excel dashboard data loaded successfully');
                }}
            }} catch (e) {{
                console.error("Failed to parse excel dashboard data:", e);
            }}

            // Excel의 employee_data를 employeeData와 병합 (Single Source of Truth)
            if (excelDashboardData && excelDashboardData.employee_data) {{
                const excelEmployeeMap = {{}};
                excelDashboardData.employee_data.forEach(excelEmp => {{
                    const empNo = excelEmp['Employee No'] || excelEmp.employee_no;
                    if (empNo) {{
                        excelEmployeeMap[empNo] = excelEmp;
                    }}
                }});

                // employeeData에 Excel data 병합
                employeeData.forEach(emp => {{
                    const empNo = emp.employee_no || emp['Employee No'];
                    if (empNo && excelEmployeeMap[empNo]) {{
                        const excelData = excelEmployeeMap[empNo];
                        // Excel의 Minimum_Days_Met 필드 추가
                        emp['Minimum_Days_Met'] = excelData['Minimum_Days_Met'];
                        emp['Minimum_Working_Days_Required'] = excelData['Minimum_Working_Days_Required'];
                        emp['Minimum_Days_Shortage'] = excelData['Minimum_Days_Shortage'];
                        // 기타 Excel 필드도 병합
                        emp['Actual Working Days'] = excelData['Actual Working Days'] || emp['Actual Working Days'];
                        emp['Adjusted_Total_Working_Days'] = excelData['Adjusted_Total_Working_Days'];
                        emp['Adjusted_Attendance_Rate'] = excelData['Adjusted_Attendance_Rate'];
                    }}
                }});
            }}

            // employeeData 필드 정규화 - boss_id 매핑 추가
            employeeData.forEach(emp => {{
                // 기본 필드 정규화
                emp.emp_no = String(emp.emp_no || emp['Employee No'] || '');
                emp.position = emp.position || emp['QIP POSITION 1ST  NAME'] || '';
                emp.name = emp.name || emp['Full Name'] || emp.employee_name || '';
                emp.type = emp.type || emp['ROLE TYPE STD'] || '';

                // boss_id 설정 - MST direct boss name이 actual로는 상사의 emp_no임!
                if (!emp.boss_id || emp.boss_id === '') {{
                    const mstBossId = String(emp['MST direct boss name'] || '').replace('.0', '').trim();
                    if (mstBossId && mstBossId !== 'nan' && mstBossId !== '0') {{
                        emp.boss_id = mstBossId;
                    }}
                }}
            }});

        }}); // End of DOMContentLoaded event listener

        // Global variables that need to be accessible outside DOMContentLoaded
        let currentLanguage = 'ko';
        let reportType = 'final'; // 전역 변count로 정의
        const dashboardMonth = '{month.lower()}';
        let positionData = {{}}; // Position Details data를 저장할 전역 변count
        const dashboardYear = {year};

        // 번역 함count
        function getTranslation(keyPath, lang = currentLanguage) {{
            const keys = keyPath.split('.');
            let value = translations;

            try {{
                for (const key of keys) {{
                    if (value[key] === undefined) {{
                        console.warn(`Translation key not found: ${{keyPath}} at segment "${{key}}"`);
                        return keyPath;
                    }}
                    value = value[key];
                }}
                if (typeof value === 'object' && value.hasOwnProperty(lang)) {{
                    return value[lang];
                }} else if (typeof value === 'object' && value.hasOwnProperty('ko')) {{
                    return value['ko'];
                }} else {{
                    console.warn(`No translation found for: ${{keyPath}} in lang: ${{lang}}`);
                    return keyPath;
                }}
            }} catch (e) {{
                console.error(`Translation error for ${{keyPath}}:`, e);
                return keyPath;
            }}
        }}

        // 모달 제목 날짜 형식 함수
        function formatModalDate(year, month, lang) {{
            const monthNames = {{
                ko: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
                en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                vi: ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
            }};

            const monthIndex = month - 1;
            const monthName = monthNames[lang] ? monthNames[lang][monthIndex] : month;

            if (lang === 'ko') {{
                return `${{year}}년 ${{monthName}}`;
            }} else if (lang === 'vi') {{
                return `${{monthName}} năm ${{year}}`;
            }} else {{
                return `${{monthName}} ${{year}}`;
            }}
        }}

        // FAQ 예시 섹션 업데이트 함count
        function updateFAQExamples() {{
            const lang = currentLanguage;
            console.log('Updating FAQ examples for language:', lang);
            
            // FAQ calculation 예시 타이틀
            const calcTitle = document.getElementById('faqCalculationExampleTitle');
            if (calcTitle) {{
                calcTitle.textContent = translations.incentiveCalculation?.faq?.calculationExampleTitle?.[lang] || '📐 actual calculation 예시';
            }}
            
            // Case 1 - TYPE-1 ASSEMBLY INSPECTOR
            const case1Title = document.getElementById('faqCase1Title');
            if (case1Title) {{
                case1Title.textContent = translations.incentiveCalculation?.faq?.case1Title?.[lang] || '예시 1: TYPE-1 ASSEMBLY INSPECTOR (10개월 연속 work)';
            }}
            
            const case1EmployeeLabel = document.getElementById('faqCase1EmployeeLabel');
            if (case1EmployeeLabel) {{
                case1EmployeeLabel.textContent = translations.incentiveCalculation?.faq?.employee?.[lang] || '직원:';
            }}
            
            const case1PrevMonthLabel = document.getElementById('faqCase1PrevMonthLabel');
            if (case1PrevMonthLabel) {{
                case1PrevMonthLabel.textContent = translations.incentiveCalculation?.faq?.previousMonth?.[lang] || '전month 상태:';
            }}
            
            const case1PrevMonthText = document.getElementById('faqCase1PrevMonthText');
            if (case1PrevMonthText) {{
                const months = translations.incentiveCalculation?.faq?.consecutiveMonthsWorked?.[lang] || '개월 연속 →';
                const received = translations.incentiveCalculation?.faq?.incentiveReceived?.[lang] || 'VND 수령';
                case1PrevMonthText.textContent = `9${{months}} 750,000 ${{received}}`;
            }}
            
            const case1ConditionsLabel = document.getElementById('faqCase1ConditionsLabel');
            if (case1ConditionsLabel) {{
                case1ConditionsLabel.textContent = translations.incentiveCalculation?.faq?.conditionEvaluation?.[lang] || '당month 조건 충족:';
            }}
            
            // Case 1 조건들 업데이트
            document.querySelectorAll('.faq-attendance-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.attendanceRateMet?.[lang] || '출근율:';
            }});
            document.querySelectorAll('.faq-absence-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.unauthorizedAbsenceMet?.[lang] || '무단결근:';
            }});
            document.querySelectorAll('.faq-actual-days-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.actualWorkingDays?.[lang] || 'actual 근무일:';
            }});
            document.querySelectorAll('.faq-min-days-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.minimumWorkingDays?.[lang] || '최소 근무일:';
            }});
            document.querySelectorAll('.faq-aql-current-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.personalAql?.[lang] || '개인 AQL (당month):';
            }});
            document.querySelectorAll('.faq-aql-consecutive-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.personalAqlContinuous?.[lang] || '개인 AQL (연속):';
            }});
            document.querySelectorAll('.faq-fprs-rate-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.fprsPassRate?.[lang] || '5PRS 통과율:';
            }});
            document.querySelectorAll('.faq-fprs-qty-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.fprsInspection?.[lang] || '5PRS 검사량:';
            }});
            
            // 값들 업데이트
            const days = translations.incentiveCalculation?.faq?.days?.[lang] || 'th';
            const items = translations.incentiveCalculation?.faq?.items?.[lang] || '개';
            
            document.querySelectorAll('.faq-absence-value').forEach(el => {{
                el.textContent = '0' + days;
            }});
            document.querySelectorAll('.faq-absence-limit').forEach(el => {{
                el.textContent = '2' + days;
            }});
            document.querySelectorAll('.faq-actual-days-value').forEach(el => {{
                el.textContent = '20' + days;
            }});
            document.querySelectorAll('.faq-actual-days-min').forEach(el => {{
                el.textContent = '0' + days;
            }});
            document.querySelectorAll('.faq-min-days-value').forEach(el => {{
                el.textContent = '20' + days;
            }});
            document.querySelectorAll('.faq-min-days-req').forEach(el => {{
                el.textContent = '12' + days;
            }});
            document.querySelectorAll('.faq-aql-current-value').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.failureText?.[lang] || 'failed 0cases';
            }});
            document.querySelectorAll('.faq-aql-consecutive-value').forEach(el => {{
                el.textContent = '3' + (translations.incentiveCalculation?.faq?.monthsConsecutiveNoFailure?.[lang] || '연속 개월 실패 없음');
            }});
            document.querySelectorAll('.faq-fprs-qty-value').forEach(el => {{
                el.textContent = '150' + items;
            }});
            document.querySelectorAll('.faq-fprs-qty-min').forEach(el => {{
                el.textContent = '100' + items;
            }});
            
            const case1ResultLabel = document.getElementById('faqCase1ResultLabel');
            if (case1ResultLabel) {{
                case1ResultLabel.textContent = translations.incentiveCalculation?.faq?.result?.[lang] || '결과:';
            }}
            
            const case1ResultText = document.getElementById('faqCase1ResultText');
            if (case1ResultText) {{
                const allMet = translations.incentiveCalculation?.faq?.allConditionsMet?.[lang] || '모든 조건 충족';
                const consecutive = translations.incentiveCalculation?.faq?.consecutiveMonthsWorked?.[lang] || '개월 연속 →';
                const 지급 = translations.incentiveCalculation?.faq?.incentivePayment?.[lang] || 'VND 지급';
                case1ResultText.innerHTML = `${{allMet}} → <span class="badge bg-success">10${{consecutive}} 850,000 ${{지급}}</span>`;
            }}
            
            // Case 2 - AUDIT & TRAINING TEAM
            const case2Title = document.getElementById('faqCase2Title');
            if (case2Title) {{
                case2Title.textContent = translations.incentiveCalculation?.faq?.case2Title?.[lang] || '예시 2: AUDIT & TRAINING TEAM (담당구역 reject율 calculation)';
            }}
            
            const case2EmployeeLabel = document.getElementById('faqCase2EmployeeLabel');
            if (case2EmployeeLabel) {{
                case2EmployeeLabel.textContent = translations.incentiveCalculation?.faq?.employee?.[lang] || '직원:';
            }}
            
            const case2AreaLabel = document.getElementById('faqCase2AreaLabel');
            if (case2AreaLabel) {{
                case2AreaLabel.textContent = translations.incentiveCalculation?.faq?.teamLeader?.[lang] || '담당 구역:';
            }}
            
            const case2InspectionLabel = document.getElementById('faqCase2InspectionLabel');
            if (case2InspectionLabel) {{
                const label = translations.incentiveCalculation?.faq?.aqlInspectionPassed?.[lang] || '구역 생산 total AQL 검사 PO count량:';
                case2InspectionLabel.textContent = 'Building B ' + label;
            }}
            
            const case2InspectionQty = document.getElementById('faqCase2InspectionQty');
            if (case2InspectionQty) {{
                case2InspectionQty.textContent = '100' + items;
            }}
            
            const case2RejectLabel = document.getElementById('faqCase2RejectLabel');
            if (case2RejectLabel) {{
                const label = translations.incentiveCalculation?.faq?.aqlRejectPo?.[lang] || '구역 생산 total AQL 리젝 PO count량:';
                case2RejectLabel.textContent = 'Building B ' + label;
            }}
            
            const case2RejectQty = document.getElementById('faqCase2RejectQty');
            if (case2RejectQty) {{
                case2RejectQty.textContent = '2' + items;
            }}
            
            const case2CalcLabel = document.getElementById('faqCase2CalcLabel');
            if (case2CalcLabel) {{
                case2CalcLabel.textContent = translations.incentiveCalculation?.faq?.calculation?.[lang] || 'calculation:';
            }}
            
            const case2ResultLabel = document.getElementById('faqCase2ResultLabel');
            if (case2ResultLabel) {{
                case2ResultLabel.textContent = translations.incentiveCalculation?.faq?.resultCondition?.[lang] || '결과:';
            }}
            
            const case2ResultBadge = document.getElementById('faqCase2ResultBadge');
            if (case2ResultBadge) {{
                case2ResultBadge.textContent = translations.incentiveCalculation?.faq?.conditionMet?.[lang] || '조건 충족';
            }}
            
            // 멤버 테이블 타이틀
            const memberTableTitle = document.getElementById('faqMemberTableTitle');
            if (memberTableTitle) {{
                memberTableTitle.textContent = translations.incentiveCalculation?.faq?.memberTable?.[lang] || 'AUDIT & TRAINING TEAM 멤버by 담당 구역';
            }}
            
            // 테이블 헤더
            const headerName = document.getElementById('faqTableHeaderName');
            if (headerName) {{
                headerName.textContent = translations.incentiveCalculation?.faq?.employeeNameLabel?.[lang] || '직원employees';
            }}
            
            const headerBuilding = document.getElementById('faqTableHeaderBuilding');
            if (headerBuilding) {{
                headerBuilding.textContent = translations.incentiveCalculation?.faq?.assignedBuilding?.[lang] || '담당 Building';
            }}
            
            const headerDesc = document.getElementById('faqTableHeaderDesc');
            if (headerDesc) {{
                headerDesc.textContent = translations.incentiveCalculation?.faq?.buildingDescription?.[lang] || '설직원';
            }}
            
            const headerReject = document.getElementById('faqTableHeaderReject');
            if (headerReject) {{
                headerReject.textContent = translations.incentiveCalculation?.faq?.rejectRate?.[lang] || 'Reject율';
            }}
            
            // 테이블 내용
            document.querySelectorAll('.faq-building-whole').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.buildingWhole?.[lang] || 'total';
            }});
            
            document.querySelectorAll('.faq-team-leader-desc').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.teamLeaderDescription?.[lang] || 'Team Leader - total Building total괄';
            }});
            
            document.querySelectorAll('.faq-other-conditions').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.noMissingData?.[lang] || '기타 조건 미충족';
            }});
            
            const rejectRateNote = document.getElementById('faqRejectRateNote');
            if (rejectRateNote) {{
                rejectRateNote.textContent = translations.incentiveCalculation?.faq?.rejectRateNote?.[lang] || '* Reject율 기준: 3% 미만 (✅ 충족, ❌ 미충족)';
            }}
            
            const memberNote = document.getElementById('faqMemberNote');
            if (memberNote) {{
                const monthText = '{month.lower()}' === 'september' ? '9month' : '{month.lower()}' === 'august' ? '8month' : '{month.lower()}' === 'july' ? 'July' : '{month.lower()}';
                memberNote.textContent = translations.incentiveCalculation?.faq?.memberNote?.[lang] || `* ${{monthText}} 기준 모든 AUDIT & TRAINING TEAM 멤버가 reject율 조건 미충족으로 incentive 0원`;
            }}
            
            // Case 3 - TYPE-2 STITCHING INSPECTOR
            const case3Title = document.getElementById('faqCase3Title');
            if (case3Title) {{
                case3Title.textContent = translations.incentiveCalculation?.faq?.case3Title?.[lang] || '예시 3: TYPE-2 STITCHING INSPECTOR';
            }}
            
            const case3EmployeeLabel = document.getElementById('faqCase3EmployeeLabel');
            if (case3EmployeeLabel) {{
                case3EmployeeLabel.textContent = translations.incentiveCalculation?.faq?.employee?.[lang] || '직원:';
            }}
            
            const case3TypeLabel = document.getElementById('faqCase3TypeLabel');
            if (case3TypeLabel) {{
                case3TypeLabel.textContent = translations.incentiveCalculation?.faq?.positionType?.[lang] || '직급 type:';
            }}
            
            const case3StatusLabel = document.getElementById('faqCase3StatusLabel');
            if (case3StatusLabel) {{
                case3StatusLabel.textContent = translations.incentiveCalculation?.faq?.conditionStatus?.[lang] || '조건 충족 현황:';
            }}
            
            // Case 3 조건들
            document.querySelectorAll('.faq-case3-attendance-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.attendanceRateMet?.[lang] || '출근율:';
            }});
            document.querySelectorAll('.faq-case3-absence-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.unauthorizedAbsenceMet?.[lang] || '무단결근:';
            }});
            document.querySelectorAll('.faq-case3-actual-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.actualWorkingDays?.[lang] || 'actual근무일:';
            }});
            document.querySelectorAll('.faq-case3-min-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.minimumWorkingDays?.[lang] || '최소근무일:';
            }});
            
            // Case 3 값들
            document.querySelectorAll('.faq-case3-met').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.conditionsMet?.[lang] || '충족';
            }});
            document.querySelectorAll('.faq-case3-absence-value').forEach(el => {{
                el.textContent = '0' + days;
            }});
            document.querySelectorAll('.faq-case3-absence-limit').forEach(el => {{
                el.textContent = '2' + days;
            }});
            document.querySelectorAll('.faq-case3-actual-value').forEach(el => {{
                el.textContent = '19' + days;
            }});
            document.querySelectorAll('.faq-case3-actual-min').forEach(el => {{
                el.textContent = '0' + days;
            }});
            document.querySelectorAll('.faq-case3-min-value').forEach(el => {{
                el.textContent = '19' + days;
            }});
            document.querySelectorAll('.faq-case3-min-req').forEach(el => {{
                el.textContent = '12' + days;
            }});
            
            const case3CalcLabel = document.getElementById('faqCase3CalcLabel');
            if (case3CalcLabel) {{
                case3CalcLabel.textContent = translations.incentiveCalculation?.faq?.incentiveCalculation?.[lang] || 'incentive calculation:';
            }}
            
            const case3Explanation = document.getElementById('faqCase3Explanation');
            if (case3Explanation) {{
                case3Explanation.textContent = translations.incentiveCalculation?.faq?.type2Explanation?.[lang] || 'TYPE-2 STITCHING INSPECTOR는 출근 조건(1-4번)만 확인하며, 모든 조건을 충족했으므로 기본 incentive를 받습니다.';
            }}
            
            const case3PaymentLabel = document.getElementById('faqCase3PaymentLabel');
            if (case3PaymentLabel) {{
                case3PaymentLabel.textContent = translations.incentiveCalculation?.faq?.paymentAmount?.[lang] || '지급액:';
            }}
            
            const case3BasicText = document.getElementById('faqCase3BasicText');
            if (case3BasicText) {{
                case3BasicText.textContent = translations.incentiveCalculation?.faq?.type2BasicIncentive?.[lang] || 'TYPE-2 기본 incentive';
            }}
            
            const case3Note = document.getElementById('faqCase3Note');
            if (case3Note) {{
                case3Note.textContent = translations.incentiveCalculation?.faq?.type2Note?.[lang] || '* TYPE-2는 AQL이나 5PRS 조건 without 출근 조건만으로 incentive가 determination됩니다.';
            }}
        }}
        
        // 출근율 calculation 방식 섹션 업데이트 함count
        function updateAttendanceSection() {{
            const lang = currentLanguage;
            console.log('Updating attendance section for language:', lang);
            
            // 제목
            const title = document.getElementById('attendanceCalcTitle');
            if (title) {{
                title.textContent = translations.incentive?.attendance?.title?.[lang] || '📊 출근율 calculation 방식';
            }}
            
            // 공식 제목
            const formulaTitle = document.getElementById('attendanceFormulaTitle');
            if (formulaTitle) {{
                formulaTitle.textContent = translations.incentive?.attendance?.formulaTitle?.[lang] || 'actual calculation 공식 (시스템 구현):';
            }}
            
            // 공식들
            const formula1 = document.getElementById('attendanceFormula1');
            if (formula1) {{
                formula1.textContent = translations.incentive?.attendance?.attendanceFormula?.[lang] || '출근율(%) = 100 - 결근율(%)';
            }}
            
            const formula2 = document.getElementById('attendanceFormula2');
            if (formula2) {{
                formula2.textContent = translations.incentive?.attendance?.absenceFormula?.[lang] || '결근율(%) = (결근 thcount / total 근무일) × 100';
            }}
            
            const formulaNote = document.getElementById('attendanceFormulaNote');
            if (formulaNote) {{
                formulaNote.textContent = translations.incentive?.attendance?.absenceDaysNote?.[lang] || '* 결근 thcount = total 근무일 - actual 근무일 - 승인된 휴가';
            }}
            
            // 예시 제목
            const examplesTitle = document.getElementById('attendanceExamplesTitle');
            if (examplesTitle) {{
                examplesTitle.textContent = translations.incentive?.attendance?.examplesTitle?.[lang] || '결근율 calculation 예시:';
            }}
            
            const example1Title = document.getElementById('attendanceExample1Title');
            if (example1Title) {{
                example1Title.textContent = translations.incentive?.attendance?.example1Title?.[lang] || '예시 1: 정상 work자';
            }}
            
            const example2Title = document.getElementById('attendanceExample2Title');
            if (example2Title) {{
                example2Title.textContent = translations.incentive?.attendance?.example2Title?.[lang] || '예시 2: 무단결근 포함';
            }}
            
            const example3Title = document.getElementById('attendanceExample3Title');
            if (example3Title) {{
                example3Title.textContent = translations.incentive?.attendance?.example3Title?.[lang] || '예시 3: 조건 충족 경계선';
            }}
            
            // 라벨들 업데이트
            document.querySelectorAll('.att-total-days-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.totalWorkingDays?.[lang] || 'total 근무일';
            }});
            document.querySelectorAll('.att-actual-days-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.actualWorkingDays?.[lang] || 'actual 근무일';
            }});
            document.querySelectorAll('.att-approved-leave-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.approvedLeave?.[lang] || '승인된 휴가';
            }});
            document.querySelectorAll('.att-absence-days-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.absenceDays?.[lang] || '결근 thcount';
            }});
            document.querySelectorAll('.att-absence-rate-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.absenceRate?.[lang] || '결근율';
            }});
            document.querySelectorAll('.att-attendance-rate-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.attendanceRate?.[lang] || '출근율';
            }});
            document.querySelectorAll('.att-unauthorized-absence-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.unauthorizedAbsence?.[lang] || '무단결근';
            }});
            document.querySelectorAll('.att-annual-leave').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.annualLeave?.[lang] || '연차';
            }});
            document.querySelectorAll('.att-sick-leave').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.sickLeave?.[lang] || '병가';
            }});
            document.querySelectorAll('.att-days-unit').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.days?.[lang] || 'th';
            }});
            document.querySelectorAll('.att-less-than-88').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.lessThan88?.[lang] || '88% 미만';
            }});
            document.querySelectorAll('.att-more-than-88').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.moreThan88?.[lang] || '88% 이상';
            }});
            
            const condition2NotMet = document.getElementById('attendanceCondition2NotMet');
            if (condition2NotMet) {{
                condition2NotMet.textContent = translations.incentive?.attendance?.condition2NotMet?.[lang] || '단, 무단결근 3일로 조건 2 미충족 → incentive 0원';
            }}
            
            // 결근 분류 섹션
            const classificationTitle = document.getElementById('attendanceClassificationTitle');
            if (classificationTitle) {{
                classificationTitle.textContent = translations.incentive?.attendance?.absenceClassificationTitle?.[lang] || '결근 사유by 분류:';
            }}
            
            const notIncludedTitle = document.getElementById('attendanceNotIncludedTitle');
            if (notIncludedTitle) {{
                notIncludedTitle.textContent = translations.incentive?.attendance?.notIncludedInAbsence?.[lang] || '✅ 결근율에 포함 안됨 (승인된 휴가):';
            }}
            
            const includedTitle = document.getElementById('attendanceIncludedTitle');
            if (includedTitle) {{
                includedTitle.textContent = translations.incentive?.attendance?.includedInAbsence?.[lang] || '❌ 결근율에 포함됨 (무단결근):';
            }}
            
            // 휴가 type 번역
            document.querySelectorAll('.att-maternity-leave').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.maternityLeave?.[lang] || '출산휴가';
            }});
            document.querySelectorAll('.att-annual-leave-vn').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.annualLeaveVn?.[lang] || '연차휴가';
            }});
            document.querySelectorAll('.att-approved-absence').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.approvedAbsence?.[lang] || '승인된 휴가';
            }});
            document.querySelectorAll('.att-postpartum-rest').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.postpartumRest?.[lang] || '출산 후 요양';
            }});
            document.querySelectorAll('.att-prenatal-checkup').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.prenatalCheckup?.[lang] || '산전검진';
            }});
            document.querySelectorAll('.att-childcare-leave').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.childcareLeave?.[lang] || '육아휴가';
            }});
            document.querySelectorAll('.att-short-sick-leave').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.shortSickLeave?.[lang] || '병가';
            }});
            document.querySelectorAll('.att-business-trip').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.businessTrip?.[lang] || '출장';
            }});
            document.querySelectorAll('.att-military-service').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.militaryService?.[lang] || '군복무';
            }});
            document.querySelectorAll('.att-card-not-swiped').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.cardNotSwiped?.[lang] || '출퇴근 체크 누락';
            }});
            document.querySelectorAll('.att-new-employee').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.newEmployee?.[lang] || '신규입사 특례';
            }});
            document.querySelectorAll('.att-compensatory-leave').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.compensatoryLeave?.[lang] || '대체휴무';
            }});
            document.querySelectorAll('.att-unauthorized-absence-ar1').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.unauthorizedAbsenceAR1?.[lang] || '무단결근';
            }});
            document.querySelectorAll('.att-written-notice-absence').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.writtenNoticeAbsence?.[lang] || '서면통지 결근';
            }});
            
            // 카운팅 규칙
            const countingRulesTitle = document.getElementById('attendanceCountingRulesTitle');
            if (countingRulesTitle) {{
                countingRulesTitle.textContent = translations.incentive?.attendance?.countingRulesTitle?.[lang] || '📢 무단결근 카운팅 규칙:';
            }}
            
            const countingRule1 = document.getElementById('attendanceCountingRule1');
            if (countingRule1) {{
                countingRule1.textContent = translations.incentive?.attendance?.countingRule1?.[lang] || 'AR1 카테고리만 무단결근으로 카운트';
            }}
            
            const countingRule2 = document.getElementById('attendanceCountingRule2');
            if (countingRule2) {{
                countingRule2.textContent = translations.incentive?.attendance?.countingRule2?.[lang] || '2일까지는 incentive 지급 가능';
            }}
            
            const countingRule3 = document.getElementById('attendanceCountingRule3');
            if (countingRule3) {{
                countingRule3.textContent = translations.incentive?.attendance?.countingRule3?.[lang] || '3일 이상 → incentive 0원';
            }}
            
            // 조건 충족 기준
            const conditionCriteriaTitle = document.getElementById('attendanceConditionCriteriaTitle');
            if (conditionCriteriaTitle) {{
                conditionCriteriaTitle.textContent = translations.incentive?.attendance?.conditionCriteriaTitle?.[lang] || '조건 충족 기준:';
            }}
            
            const criteria1 = document.getElementById('attendanceCriteria1');
            if (criteria1) {{
                criteria1.innerHTML = translations.incentive?.attendance?.attendanceCriteria?.[lang] || '<strong>출근율:</strong> ≥ 88% (결근율 ≤ 12%)';
            }}
            
            const criteria2 = document.getElementById('attendanceCriteria2');
            if (criteria2) {{
                criteria2.innerHTML = translations.incentive?.attendance?.unauthorizedAbsenceCriteria?.[lang] || '<strong>무단결근:</strong> ≤ 2일 (AR1 카테고리만 corresponding)';
            }}
            
            const criteria3 = document.getElementById('attendanceCriteria3');
            if (criteria3) {{
                criteria3.innerHTML = translations.incentive?.attendance?.actualWorkingDaysCriteria?.[lang] || '<strong>actual 근무일:</strong> > 0일';
            }}
            
            const criteria4 = document.getElementById('attendanceCriteria4');
            if (criteria4) {{
                criteria4.innerHTML = translations.incentive?.attendance?.minimumWorkingDaysCriteria?.[lang] || '<strong>최소 근무일:</strong> ≥ 12일';
            }}
            
            // Unapproved Absence 설직원
            const unapprovedTitle = document.getElementById('attendanceUnapprovedTitle');
            if (unapprovedTitle) {{
                unapprovedTitle.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanationTitle?.[lang] || '📊 Unapproved Absence Days 설직원:';
            }}
            
            const unapproved1 = document.getElementById('attendanceUnapproved1');
            if (unapproved1) {{
                unapproved1.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation1?.[lang] || 'HR 시스템에서 제공하는 무단결근 thcount data';
            }}
            
            const unapproved2 = document.getElementById('attendanceUnapproved2');
            if (unapproved2) {{
                unapproved2.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation2?.[lang] || 'AR1 (Vắng không phép) 카테고리만 집계';
            }}
            
            const unapproved3 = document.getElementById('attendanceUnapproved3');
            if (unapproved3) {{
                unapproved3.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation3?.[lang] || '서면통지 결근(Gửi thư)도 AR1에 포함';
            }}
            
            const unapproved4 = document.getElementById('attendanceUnapproved4');
            if (unapproved4) {{
                unapproved4.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation4?.[lang] || 'incentive 조건: ≤2일 (개인별 최대 허용치)';
            }}
        }}
        
        // FAQ Q&A 섹션 업데이트 함count
        function updateFAQQASection() {{
            const lang = currentLanguage;
            console.log('Updating FAQ Q&A section for language:', lang);
            console.log('FAQ translations available:', translations.incentive?.faq);
            console.log('Question1 translations:', translations.incentiveCalculation?.faq?.question1);
            
            // FAQ 섹션 제목
            const faqTitle = document.getElementById('faqSectionTitle');
            if (faqTitle) {{
                faqTitle.textContent = translations.incentiveCalculation?.faq?.faqSectionTitle?.[lang] || '❓ 자주 묻는 질문 (FAQ)';
            }}
            
            // Q1
            const q1 = document.getElementById('faqQuestion1');
            if (q1) {{
                console.log('Updating Q1, current text:', q1.textContent);
                const newText = translations.incentiveCalculation?.faq?.question1?.[lang] || 'Q1. 왜 나는 incentive를 못 받았나요? 조건을 확인하는 방법은?';
                console.log('New text for Q1:', newText);
                q1.textContent = newText;
            }}
            document.getElementById('faqAnswer1Main').textContent = translations.incentiveCalculation?.faq?.answer1Main?.[lang] || 'incentive를 받지 못한 주요 이유:';
            document.getElementById('faqAnswer1Reason1').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.minDays?.[lang] || '최소 근무일 12일 미충족';
            document.getElementById('faqAnswer1Reason2').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.attendance?.[lang] || '출근율 88% 미만';
            document.getElementById('faqAnswer1Reason3').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.absence?.[lang] || '무단결근 3일 이상';
            document.getElementById('faqAnswer1Reason4').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.aql?.[lang] || 'AQL failed (corresponding 직급)';
            document.getElementById('faqAnswer1Reason5').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.fprs?.[lang] || '5PRS 통과율 95% 미만 (corresponding 직급)';
            document.getElementById('faqAnswer1CheckMethod').textContent = translations.incentiveCalculation?.faq?.answer1CheckMethod?.[lang] || '개인별 상세 페이지에서 본인의 조건 충족 여부를 확인할 count 있습니다.';
            
            // Q2
            const q2 = document.getElementById('faqQuestion2');
            if (q2) {{
                q2.textContent = translations.incentiveCalculation?.faq?.question2?.[lang] || 'Q2. 무단결근이 며칠까지 허용되나요?';
            }}
            document.getElementById('faqAnswer2Main').textContent = translations.incentiveCalculation?.faq?.answer2Main?.[lang] || '무단결근은 최대 2일까지 허용됩니다.';
            document.getElementById('faqAnswer2Detail').textContent = translations.incentiveCalculation?.faq?.answer2Detail?.[lang] || '3일 이상 무단결근시 corresponding month incentive를 받을 count not found. 사전 승인된 휴가나 병가는 무단결근에 포함되지 not.';
            
            // Q3
            const q3 = document.getElementById('faqQuestion3');
            if (q3) {{
                q3.textContent = translations.incentiveCalculation?.faq?.question3?.[lang] || 'Q3. TYPE-2 직급의 incentive는 어떻게 calculation되나요?';
            }}
            document.getElementById('faqAnswer3Main').textContent = translations.incentiveCalculation?.faq?.answer3Main?.[lang] || 'TYPE-2 직급의 incentive는 corresponding하는 TYPE-1 직급의 평균 incentive를 기준으로 calculation됩니다.';
            document.getElementById('faqAnswer3Example').textContent = translations.incentiveCalculation?.faq?.answer3Example?.[lang] || '예를 들어:';
            document.getElementById('faqAnswer3Example1').textContent = translations.incentiveCalculation?.faq?.answer3Example1?.[lang] || 'TYPE-2 GROUP LEADER는 TYPE-1 LINE LEADER 평균 incentive × 2';
            document.getElementById('faqAnswer3Example2').textContent = translations.incentiveCalculation?.faq?.answer3Example2?.[lang] || 'TYPE-2 STITCHING INSPECTOR는 TYPE-1 ASSEMBLY INSPECTOR들의 평균 incentive';
            
            // Q4
            const q4 = document.getElementById('faqQuestion4');
            if (q4) {{
                q4.textContent = translations.incentiveCalculation?.faq?.question4?.[lang] || 'Q4. ASSEMBLY INSPECTOR의 연속 work 개월은 어떻게 calculation되나요?';
            }}
            document.getElementById('faqAnswer4Main').textContent = translations.incentiveCalculation?.faq?.answer4Main?.[lang] || 'TYPE-1 ASSEMBLY INSPECTOR만 corresponding되며, 조건을 충족하며 incentive를 받은 개월count가 누적됩니다.';
            document.getElementById('faqAnswer4Detail1').textContent = translations.incentiveCalculation?.faq?.answer4Detail1?.[lang] || '조건 미충족으로 incentive를 못 받으면 0개월로 리셋';
            document.getElementById('faqAnswer4Detail2').textContent = translations.incentiveCalculation?.faq?.answer4Detail2?.[lang] || '12개월 이상 연속시 최대 incentive 1,000,000 VND';
            
            // Q5
            const q5 = document.getElementById('faqQuestion5');
            if (q5) {{
                q5.textContent = translations.incentiveCalculation?.faq?.question5?.[lang] || 'Q5. AQL failed가 무엇이고 어떤 영향을 미치나요?';
            }}
            document.getElementById('faqAnswer5Main').textContent = translations.incentiveCalculation?.faq?.answer5Main?.[lang] || 'AQL(Acceptable Quality Limit)은 품질 검사 기준입니다.';
            document.getElementById('faqAnswer5Detail1').textContent = translations.incentiveCalculation?.faq?.answer5Detail1?.[lang] || '개인 AQL failed: corresponding month에 품질 검사 failed한 경우';
            document.getElementById('faqAnswer5Detail2').textContent = translations.incentiveCalculation?.faq?.answer5Detail2?.[lang] || '3연속 개월 실패: 지난 3개월 동안 연속으로 failed한 경우';
            document.getElementById('faqAnswer5Detail3').textContent = translations.incentiveCalculation?.faq?.answer5Detail3?.[lang] || 'AQL 관련 직급만 영향받음 (INSPECTOR 계열 등)';
            
            // Q6
            const q6 = document.getElementById('faqQuestion6');
            if (q6) {{
                q6.textContent = translations.incentiveCalculation?.faq?.question6?.[lang] || 'Q6. 5PRS 검사량이 부족하면 어떻게 되나요?';
            }}
            document.getElementById('faqAnswer6Main').textContent = translations.incentiveCalculation?.faq?.answer6Main?.[lang] || '5PRS 관련 직급은 다음 조건을 충족해야 합니다:';
            document.getElementById('faqAnswer6Detail1').textContent = translations.incentiveCalculation?.faq?.answer6Detail1?.[lang] || '검사량 100족 이상';
            document.getElementById('faqAnswer6Detail2').textContent = translations.incentiveCalculation?.faq?.answer6Detail2?.[lang] || '통과율 95% 이상';
            document.getElementById('faqAnswer6Conclusion').textContent = translations.incentiveCalculation?.faq?.answer6Conclusion?.[lang] || '둘 중 하나라도 미충족시 incentive를 받을 count not found.';
            
            // Q7
            const q7 = document.getElementById('faqQuestion7');
            if (q7) {{
                q7.textContent = translations.incentiveCalculation?.faq?.question7?.[lang] || 'Q7. 출산휴가나 병가 중에도 incentive를 받을 count 있나요?';
            }}
            document.getElementById('faqAnswer7Main').textContent = translations.incentiveCalculation?.faq?.answer7Main?.[lang] || '출산휴가나 장기 병가 중에는 incentive가 지급되지 not.';
            document.getElementById('faqAnswer7Detail1').textContent = translations.incentiveCalculation?.faq?.answer7Detail1?.[lang] || '최소 근무일 12일 조건을 충족할 count 없기 때문';
            document.getElementById('faqAnswer7Detail2').textContent = translations.incentiveCalculation?.faq?.answer7Detail2?.[lang] || '복귀 후 조건 충족시 다시 incentive 수령 가능';
            document.getElementById('faqAnswer7Detail3').textContent = translations.incentiveCalculation?.faq?.answer7Detail3?.[lang] || 'ASSEMBLY INSPECTOR의 경우 연속 개월count는 0으로 리셋';
            
            // Q8
            const q8 = document.getElementById('faqQuestion8');
            if (q8) {{
                q8.textContent = translations.incentiveCalculation?.faq?.question8?.[lang] || 'Q8. 전month incentive와 차이가 나는 이유는 무엇인가요?';
            }}
            const answer8Main = document.getElementById('faqAnswer8Main');
            if (answer8Main) {{
                answer8Main.textContent = translations.incentiveCalculation?.faq?.answer8Main?.[lang] || 'incentive 금액이 변동하는 주요 이유:';
            }}
            const answer8Reason1 = document.getElementById('faqAnswer8Reason1');
            if (answer8Reason1) {{
                answer8Reason1.innerHTML = `<strong>ASSEMBLY INSPECTOR</strong>: ${{translations.incentiveCalculation?.faq?.answer8Reason1?.[lang] || '연속 work 개월 변화'}}`;
            }}
            const answer8Reason2 = document.getElementById('faqAnswer8Reason2');
            if (answer8Reason2) {{
                answer8Reason2.innerHTML = `<strong>TYPE-2 ${{lang === 'ko' ? '직급' : lang === 'en' ? 'positions' : 'vị trí'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer8Reason2?.[lang] || 'TYPE-1 평균값 변동'}}`;
            }}
            const answer8Reason3 = document.getElementById('faqAnswer8Reason3');
            if (answer8Reason3) {{
                answer8Reason3.innerHTML = `<strong>AQL INSPECTOR</strong>: ${{translations.incentiveCalculation?.faq?.answer8Reason3?.[lang] || 'Part1, Part2, Part3 조건 변화'}}`;
            }}
            const answer8Reason4 = document.getElementById('faqAnswer8Reason4');
            if (answer8Reason4) {{
                answer8Reason4.innerHTML = `<strong>${{lang === 'ko' ? '조건 미충족' : lang === 'en' ? 'Unmet conditions' : 'Điều kiện không đạt'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer8Reason4?.[lang] || '하나라도 미충족시 0'}}`;
            }}
            
            // Q9
            const q9 = document.getElementById('faqQuestion9');
            if (q9) {{
                q9.textContent = translations.incentiveCalculation?.faq?.question9?.[lang] || 'Q9. TYPE-3에서 TYPE-2로 승진하면 incentive가 어떻게 변하나요?';
            }}
            const answer9Detail1 = document.getElementById('faqAnswer9Detail1');
            if (answer9Detail1) {{
                answer9Detail1.innerHTML = `<strong>TYPE-3</strong>: ${{translations.incentiveCalculation?.faq?.answer9Detail1?.[lang] || '조건 without 기본 150,000 VND (work시 자동 지급)'}}`;
            }}
            const answer9Detail2 = document.getElementById('faqAnswer9Detail2');
            if (answer9Detail2) {{
                answer9Detail2.innerHTML = `<strong>TYPE-2</strong>: ${{translations.incentiveCalculation?.faq?.answer9Detail2?.[lang] || '조건 충족 필요, TYPE-1 평균 기준 calculation'}}`;
            }}
            const answer9Detail3 = document.getElementById('faqAnswer9Detail3');
            if (answer9Detail3) {{
                answer9Detail3.textContent = translations.incentiveCalculation?.faq?.answer9Detail3?.[lang] || '승진 후 조건 충족시 th반적으로 incentive 증가';
            }}
            const answer9Detail4 = document.getElementById('faqAnswer9Detail4');
            if (answer9Detail4) {{
                answer9Detail4.textContent = translations.incentiveCalculation?.faq?.answer9Detail4?.[lang] || '하지만 조건 미충족시 0이 될 count 있으므로 주의 필요';
            }}
            
            // Q10
            const q10 = document.getElementById('faqQuestion10');
            if (q10) {{
                q10.textContent = translations.incentiveCalculation?.faq?.question10?.[lang] || 'Q10. 조건을 모두 충족했는데도 incentive가 0인 이유는 무엇인가요?';
            }}
            const answer10Main = document.getElementById('faqAnswer10Main');
            if (answer10Main) {{
                answer10Main.textContent = translations.incentiveCalculation?.faq?.answer10Main?.[lang] || '다음 사항을 재확인해 보세요:';
            }}
            const answer10Reason1 = document.getElementById('faqAnswer10Reason1');
            if (answer10Reason1) {{
                answer10Reason1.innerHTML = `<strong>${{lang === 'ko' ? '숨겨진 조건' : lang === 'en' ? 'Hidden conditions' : 'Điều kiện ẩn'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer10Reason1?.[lang]?.replace(/.*: (.*)/, '$1') || '직급별로 apply되는 모든 조건 확인'}}`;
            }}
            const answer10Reason2 = document.getElementById('faqAnswer10Reason2');
            if (answer10Reason2) {{
                answer10Reason2.innerHTML = `<strong>${{lang === 'ko' ? '데이터 업데이트' : lang === 'en' ? 'Data update' : 'Cập nhật dữ liệu'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer10Reason2?.[lang]?.replace(/.*: (.*)/, '$1') || '최신 data 반영 여부'}}`;
            }}
            const answer10Reason3 = document.getElementById('faqAnswer10Reason3');
            if (answer10Reason3) {{
                answer10Reason3.innerHTML = `<strong>${{lang === 'ko' ? '특별한 사유' : lang === 'en' ? 'Special reasons' : 'Lý do đặc biệt'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer10Reason3?.[lang]?.replace(/.*: (.*)/, '$1') || '징계, 경고 등 특별 사유'}}`;
            }}
            const answer10Reason4 = document.getElementById('faqAnswer10Reason4');
            if (answer10Reason4) {{
                answer10Reason4.innerHTML = `<strong>${{lang === 'ko' ? '시스템 오류' : lang === 'en' ? 'System error' : 'Lỗi hệ thống'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer10Reason4?.[lang]?.replace(/.*: (.*)/, '$1') || 'HR 부서에 문의'}}`;
            }}
            const answer10Conclusion = document.getElementById('faqAnswer10Conclusion');
            if (answer10Conclusion) {{
                answer10Conclusion.textContent = translations.incentiveCalculation?.faq?.answer10Conclusion?.[lang] || '개인별 상세 페이지에서 조건별 충족 여부를 상세히 확인하시기 바랍니다.';
            }}

            // FAQ Q11 translations
            const q11 = document.getElementById('faqQuestion11');
            if (q11) {{
                q11.textContent = translations.incentiveCalculation?.faq?.question11?.[lang] || 'Q11. TYPE-2 GROUP LEADER가 incentive를 못 받는 경우가 있나요?';
            }}
            const answer11Main = document.getElementById('faqAnswer11Main');
            if (answer11Main) {{
                answer11Main.textContent = translations.incentiveCalculation?.faq?.answer11Main?.[lang] || 'TYPE-2 GROUP LEADER는 특별한 calculation 규칙이 apply됩니다:';
            }}
            const answer11Detail1 = document.getElementById('faqAnswer11Detail1');
            if (answer11Detail1) {{
                const baseCalc = translations.incentiveCalculation?.faq?.answer11Detail1?.[lang] || '기본 calculation: TYPE-1 LINE LEADER 평균 incentive × 2를 받습니다';
                answer11Detail1.innerHTML = `<strong>${{baseCalc.split(':')[0]}}:</strong> ${{baseCalc.split(':')[1] || ''}}`;
            }}
            const answer11Detail2 = document.getElementById('faqAnswer11Detail2');
            if (answer11Detail2) {{
                const indepCalc = translations.incentiveCalculation?.faq?.answer11Detail2?.[lang] || 'Fallback calculation: TYPE-1 LINE LEADER 평균이 0 VND인 경우, TYPE-2 LINE LEADER 평균 × 2로 calculation됩니다';
                answer11Detail2.innerHTML = `<strong>${{indepCalc.split(':')[0]}}:</strong> ${{indepCalc.split(':')[1] || ''}}`;
            }}
            const answer11Detail3 = document.getElementById('faqAnswer11Detail3');
            if (answer11Detail3) {{
                const improvement = translations.incentiveCalculation?.faq?.answer11Detail3?.[lang] || '중요: 모든 평균은 인센티브 수령자만 대상 (0 VND 제외)';
                answer11Detail3.innerHTML = `<strong>${{improvement.split(':')[0]}}:</strong> ${{improvement.split(':')[1] || ''}}`;
            }}
            const answer11Detail4 = document.getElementById('faqAnswer11Detail4');
            if (answer11Detail4) {{
                const conditions = translations.incentiveCalculation?.faq?.answer11Detail4?.[lang] || '조건: TYPE-2는 출근 조건(1-4번)만 충족하면 incentive를 받을 count 있습니다';
                answer11Detail4.innerHTML = `<strong>${{conditions.split(':')[0]}}:</strong> ${{conditions.split(':')[1] || ''}}`;
            }}
            const answer11Conclusion = document.getElementById('faqAnswer11Conclusion');
            if (answer11Conclusion) {{
                answer11Conclusion.textContent = translations.incentiveCalculation?.faq?.answer11Conclusion?.[lang] || '따라서 출근 조건을 충족한 TYPE-2 GROUP LEADER는 항상 incentive를 받을 count 있도록 보장됩니다.';
            }}

            // TYPE-2 GROUP LEADER Special Calculation Box translations
            const type2SpecialTitle = document.getElementById('type2GroupLeaderSpecialTitle');
            if (type2SpecialTitle) {{
                type2SpecialTitle.textContent = translations.type2GroupLeaderSpecial?.title?.[lang] || '⚠️ TYPE-2 GROUP LEADER 특별 calculation 규칙';
            }}
            const type2BaseCalc = document.getElementById('type2BaseCalc');
            if (type2BaseCalc) {{
                const baseText = translations.type2GroupLeaderSpecial?.baseCalculation?.[lang] || '기본 calculation: TYPE-1 LINE LEADER 평균 incentive × 2 use';
                type2BaseCalc.innerHTML = `<strong>${{baseText.split(':')[0]}}:</strong> ${{baseText.split(':')[1] || ''}}`;
            }}
            const type2IndependentCalc = document.getElementById('type2IndependentCalc');
            if (type2IndependentCalc) {{
                const indepText = translations.type2GroupLeaderSpecial?.independentCalculation?.[lang] || 'Fallback (TYPE-1 평균 0 VND): TYPE-2 LINE LEADER 평균 × 2로 calculation';
                type2IndependentCalc.innerHTML = `<strong>${{indepText.split(':')[0]}}:</strong> ${{indepText.split(':')[1] || ''}}`;
            }}
            const type2Important = document.getElementById('type2Important');
            if (type2Important) {{
                const importantText = translations.type2GroupLeaderSpecial?.important?.[lang] || '중요: 모든 평균은 인센티브 수령자만 대상 (0 VND 제외)';
                type2Important.innerHTML = `<strong>${{importantText.split(':')[0]}}:</strong> ${{importantText.split(':')[1] || ''}}`;
            }}
            const type2Conditions = document.getElementById('type2Conditions');
            if (type2Conditions) {{
                const conditionsText = translations.type2GroupLeaderSpecial?.conditions?.[lang] || 'apply 조건: TYPE-2는 출근 조건(1-4번)만 충족하면 incentive 지급';
                type2Conditions.innerHTML = `<strong>${{conditionsText.split(':')[0]}}:</strong> ${{conditionsText.split(':')[1] || ''}}`;
            }}

            // Talent Pool 섹션 번역 업데이트
            const talentPoolTitle = document.getElementById('talentPoolTitle');
            if (talentPoolTitle) {{
                talentPoolTitle.textContent = getTranslation('talentPool.title', lang);
            }}

            const talentPoolMemberCountLabel = document.getElementById('talentPoolMemberCountLabel');
            if (talentPoolMemberCountLabel) {{
                talentPoolMemberCountLabel.textContent = getTranslation('talentPool.memberCount', lang);
            }}

            const talentPoolMonthlyBonusLabel = document.getElementById('talentPoolMonthlyBonusLabel');
            if (talentPoolMonthlyBonusLabel) {{
                talentPoolMonthlyBonusLabel.textContent = getTranslation('talentPool.monthlyBonus', lang);
            }}

            const talentPoolTotalBonusLabel = document.getElementById('talentPoolTotalBonusLabel');
            if (talentPoolTotalBonusLabel) {{
                // totalBonus 키가 없으므로 fallback 사용
                talentPoolTotalBonusLabel.textContent = getTranslation('talentPool.totalBenefit', lang) ||
                    (lang === 'ko' ? '총 보너스 지급액' : lang === 'en' ? 'Total Bonus Amount' : 'Tổng tiền thưởng');
            }}

            const talentPoolPaymentPeriodLabel = document.getElementById('talentPoolPaymentPeriodLabel');
            if (talentPoolPaymentPeriodLabel) {{
                // paymentPeriod 키가 없으므로 직접 번역
                talentPoolPaymentPeriodLabel.textContent = lang === 'ko' ? '지급 기간' :
                    lang === 'en' ? 'Payment Period' : 'Thời gian thanh toán';
            }}
            
            // 조직도 탭 번역 업데이트
            const tabOrgChart = document.getElementById('tabOrgChart');
            if (tabOrgChart) {{
                tabOrgChart.textContent = getTranslation('tabs.orgChart', currentLanguage);
            }}

            // 조직도 제목 및 부제
            const orgChartTitle = document.getElementById('orgChartTitle');
            if (orgChartTitle) {{
                orgChartTitle.textContent = getTranslation('orgChart.title', currentLanguage);
            }}

            const orgChartSubtitle = document.getElementById('orgChartSubtitle');
            if (orgChartSubtitle) {{
                orgChartSubtitle.textContent = getTranslation('orgChart.subtitle', currentLanguage);
            }}

            // use 안내 텍스트
            const usageGuideTitle = document.getElementById('usageGuideTitle');
            if (usageGuideTitle) {{
                usageGuideTitle.textContent = getTranslation('orgChart.usageGuide.title', currentLanguage);
            }}
            const usageGuideText = document.getElementById('usageGuideText');
            if (usageGuideText) {{
                const text = getTranslation('orgChart.usageGuide.text', currentLanguage);
                const subtext = getTranslation('orgChart.usageGuide.subtext', currentLanguage);
                usageGuideText.innerHTML = text + ' <span class="badge bg-primary">ℹ️</span> ' + subtext;
            }}
            const usageGuideHelpText = document.getElementById('usageGuideHelpText');
            if (usageGuideHelpText) {{
                usageGuideHelpText.textContent = getTranslation('orgChart.helpText', currentLanguage);
            }}

            // 버튼 텍스트 - span 요소 내부의 텍스트만 업데이트
            const expandAllBtnSpan = document.querySelector('#expandAllBtn');
            if (expandAllBtnSpan) {{
                const iconElement = expandAllBtnSpan.parentElement.querySelector('i');
                expandAllBtnSpan.textContent = getTranslation('orgChart.buttons.expandAll', currentLanguage);
            }}
            const collapseAllBtnSpan = document.querySelector('#collapseAllBtn');
            if (collapseAllBtnSpan) {{
                const iconElement = collapseAllBtnSpan.parentElement.querySelector('i');
                collapseAllBtnSpan.textContent = getTranslation('orgChart.buttons.collapseAll', currentLanguage);
            }}
            const resetViewBtnSpan = document.querySelector('#resetViewBtn');
            if (resetViewBtnSpan) {{
                const iconElement = resetViewBtnSpan.parentElement.querySelector('i');
                resetViewBtnSpan.textContent = getTranslation('orgChart.buttons.reset', currentLanguage);
            }}

            // 모달 내부 텍스트 번역
            document.querySelectorAll('.modal-actual-incentive').forEach(elem => {{
                elem.textContent = getTranslation('orgChart.modalLabels.actualIncentive', currentLanguage);
            }});
            document.querySelectorAll('.modal-calc-method').forEach(elem => {{
                elem.textContent = getTranslation('orgChart.modalLabels.calculationMethod', currentLanguage);
            }});
            document.querySelectorAll('.modal-no-지급-reason').forEach(elem => {{
                elem.textContent = getTranslation('orgChart.modalLabels.noPaymentReason', currentLanguage);
            }});
            document.querySelectorAll('.modal-calc-detail-line-leader').forEach(elem => {{
                elem.textContent = getTranslation('orgChart.modalLabels.calcDetailLineLeader', currentLanguage);
            }});
            document.querySelectorAll('.modal-close-btn').forEach(elem => {{
                elem.textContent = getTranslation('orgChart.buttons.close', currentLanguage);
            }});
            document.querySelectorAll('.modal-team-line-leader-list').forEach(elem => {{
                elem.textContent = getTranslation('modal.teamLineLeaderList', currentLanguage);
            }});
            document.querySelectorAll('.modal-team-line-leader-count').forEach(elem => {{
                elem.textContent = getTranslation('modal.teamLineLeaderCount', currentLanguage);
            }});
            document.querySelectorAll('.modal-calc-detail-line-leader').forEach(elem => {{
                elem.textContent = getTranslation('modal.calcDetailLineLeader', currentLanguage);
            }});
            document.querySelectorAll('.modal-calc-detail-group-leader').forEach(elem => {{
                elem.textContent = getTranslation('modal.calcDetailGroupLeader', currentLanguage);
            }});
            document.querySelectorAll('.modal-calc-detail-supervisor').forEach(elem => {{
                elem.textContent = getTranslation('modal.calcDetailSupervisor', currentLanguage);
            }});
            document.querySelectorAll('.modal-calc-detail-amanager').forEach(elem => {{
                elem.textContent = getTranslation('modal.calcDetailAManager', currentLanguage);
            }});
            document.querySelectorAll('.modal-calc-detail-manager').forEach(elem => {{
                elem.textContent = getTranslation('modal.calcDetailManager', currentLanguage);
            }})

            // 조직도 안내 텍스트
            const orgChartNoteLabel = document.getElementById('orgChartNoteLabel');
            if (orgChartNoteLabel) {{
                orgChartNoteLabel.textContent = getTranslation('orgChart.noteLabel', currentLanguage);
            }}

            const orgChartExcludedPositions = document.getElementById('orgChartExcludedPositions');
            if (orgChartExcludedPositions) {{
                orgChartExcludedPositions.textContent = getTranslation('orgChart.excludedPositions', currentLanguage);
            }}

            const orgChartHelpText = document.getElementById('orgChartHelpText');
            if (orgChartHelpText) {{
                orgChartHelpText.textContent = getTranslation('orgChart.helpText', currentLanguage);
            }}

            // 조직도 필터 옵션 업데이트
            const filterAll = document.getElementById('filterAll');
            if (filterAll) filterAll.textContent = getTranslation('orgChart.filters.viewAll', currentLanguage);

            const filterPaid = document.getElementById('filterPaid');
            if (filterPaid) filterPaid.textContent = getTranslation('orgChart.filters.paidOnly', currentLanguage);

            const filterUnpaid = document.getElementById('filterUnpaid');
            if (filterUnpaid) filterUnpaid.textContent = getTranslation('orgChart.filters.unpaidOnly', currentLanguage);

            // Building 필터 옵션 업데이트 (SUPERVISOR, A.MANAGER 요청 - 2025-12-16)
            const buildingFilterAll = document.getElementById('buildingFilterAll');
            if (buildingFilterAll) buildingFilterAll.textContent = getTranslation('orgChart.filters.allBuildings', currentLanguage);

            // 조직도 범례 업데이트
            const legendReceived = document.getElementById('legendReceived');
            if (legendReceived) legendReceived.textContent = getTranslation('orgChart.incentiveReceived', currentLanguage);

            const legendNotReceived = document.getElementById('legendNotReceived');
            if (legendNotReceived) legendNotReceived.textContent = getTranslation('orgChart.incentiveNotReceived', currentLanguage);

            const legendIncentiveReceived = document.getElementById('legendIncentiveReceived');
            if (legendIncentiveReceived) legendIncentiveReceived.textContent = getTranslation('orgChart.incentiveReceived', currentLanguage);

            const legendNoIncentive = document.getElementById('legendNoIncentive');
            if (legendNoIncentive) legendNoIncentive.textContent = getTranslation('orgChart.incentiveNotReceived', currentLanguage);

            // 조직도가 이미 그려져 있다면 다시 그리기
            if (typeof updateOrgChart === 'function' && document.getElementById('orgTreeContent').innerHTML !== '') {{
                updateOrgChart();
            }}

            // 테이블 재creation하여 툴팁 번역 apply
            generateEmployeeTable();
            updatePositionFilter();
        }}
        
        // 언어 변경 함수 - 모든 UI 요소 업데이트
        function changeLanguage(lang) {{
            console.log('Language changed to:', lang);

            // 전역 언어 변수 모두 업데이트
            currentLanguage = lang;
            window.currentLanguage = lang;
            if (typeof currentLang !== 'undefined') currentLang = lang;

            // 저장 먼저 (페이지 새로고침 시 복원용)
            localStorage.setItem('dashboardLanguage', lang);

            // 1. 모든 텍스트 업데이트 (헤더, 탭, 테이블 등)
            updateAllTexts();

            // 2. 데이터 신선도 배지 업데이트
            updateDataFreshness();

            // 3. TYPE 요약 테이블 업데이트
            updateTypeSummaryTable();

            // 4. Validation 탭 KPI 카드 업데이트 (언어 단위 변경)
            if (typeof updateValidationKPIs === 'function') {{
                // isInterimReport 계산 (validation 탭에서 사용하는 것과 동일한 로직)
                const totalWorkingDays = (window.excelDashboardData && window.excelDashboardData.attendance)
                    ? window.excelDashboardData.attendance.total_working_days
                    : 18;
                const isInterim = totalWorkingDays < 20;
                updateValidationKPIs(isInterim);
            }}

            // 5. Validation 탭 라벨 텍스트 업데이트
            if (typeof updateValidationTexts === 'function') {{
                updateValidationTexts();
            }}

            // 6. 직원 테이블 재생성 (상태 텍스트 번역)
            if (typeof generateEmployeeTable === 'function') {{
                generateEmployeeTable();
            }}

            // 7. 조직도 텍스트 업데이트
            if (typeof updateOrgChartUIText === 'function') {{
                updateOrgChartUIText();
            }}

            console.log('All UI elements updated for language:', lang);
        }}
        
        // dashboard 변경 함count
        function changeDashboard(type) {{
            const currentMonth = '{str(month_num).zfill(2)}';  // month 번호를 2자리로 패딩
            const currentYear = '{year}';

            switch(type) {{
                case 'management':
                    // Management Dashboard로 이동
                    window.location.href = `management_dashboard_${{currentYear}}_${{currentMonth}}.html`;
                    break;
                case 'statistics':
                    // Statistics Dashboard로 이동 (향후 구현)
                    alert('Statistics Dashboard는 준비 중입니다.');
                    document.getElementById('dashboardSelector').value = 'incentive';
                    break;
                case 'incentive':
                default:
                    // 현재 페이지 유지
                    break;
            }}
        }}

        // HTML 대시보드 다운로드 함수 (Self-Contained Offline Version)
        function downloadDashboard() {{
            const currentYear = '{year}';
            const currentMonth = '{str(month_num).zfill(2)}';
            const filename = `Incentive_Dashboard_${{currentYear}}_${{currentMonth}}_Version_9.0_SelfContained.html`;

            // 안내 메시지
            const infoMessages = {{
                'ko': '📦 Offline 버전 다운로드\\n\\n✅ 인터넷 없이 작동\\n✅ 비밀번호 불필요\\n✅ 더블클릭으로 바로 열림\\n❌ Excel 다운로드 기능 없음\\n\\n다운로드하시겠습니까?',
                'en': '📦 Download Offline Version\\n\\n✅ Works without internet\\n✅ No password required\\n✅ Double-click to open\\n❌ Excel download not available\\n\\nDo you want to download?',
                'vi': '📦 Tải phiên bản ngoại tuyến\\n\\n✅ Hoạt động không cần internet\\n✅ Không cần mật khẩu\\n✅ Nhấp đúp để mở\\n❌ Không có tải xuống Excel\\n\\nBạn có muốn tải xuống không?'
            }};

            // 사용자 확인
            if (!confirm(infoMessages[currentLanguage] || infoMessages['ko'])) {{
                return; // 취소 시 다운로드 중단
            }}

            // Self-Contained 파일 경로 (GitHub Pages에서 다운로드)
            const link = document.createElement('a');
            link.href = filename;  // Same directory as current page
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // 다운로드 확인 메시지
            const successMessages = {{
                'ko': '✅ Offline 버전이 다운로드되었습니다!\\n\\n📝 사용 방법:\\n1. 다운로드된 파일을 더블클릭\\n2. 브라우저에서 바로 열림\\n3. 비밀번호 입력 불필요\\n\\n💡 파일을 다른 사람에게 공유할 수 있습니다.',
                'en': '✅ Offline version downloaded!\\n\\n📝 How to use:\\n1. Double-click the downloaded file\\n2. Opens directly in browser\\n3. No password needed\\n\\n💡 You can share this file with others.',
                'vi': '✅ Đã tải xuống phiên bản ngoại tuyến!\\n\\n📝 Cách sử dụng:\\n1. Nhấp đúp vào tệp đã tải xuống\\n2. Mở trực tiếp trong trình duyệt\\n3. Không cần mật khẩu\\n\\n💡 Bạn có thể chia sẻ tệp này với người khác.'
            }};

            setTimeout(() => {{
                alert(successMessages[currentLanguage] || successMessages['ko']);
            }}, 500);
        }}

        // CSV download function removed per user request (2025-11-19)
        // Reason: CSV download button has been removed from the dashboard
        /*
        function downloadCSV() {{
            // Function disabled - CSV download removed
        }}
        */

        // Excel 파일 다운로드 함수
        function downloadExcel() {{
            const currentYear = '{year}';
            const currentMonth = '{str(month_num).zfill(2)}';
            const monthName = '{month}';
            const filename = `output_QIP_incentive_${{monthName}}_${{currentYear}}_Complete_V9.0_Complete.xlsx`;

            // Excel 파일 경로 (GitHub Pages 호스팅)
            const excelPath = filename;

            // 다운로드 링크 생성
            const link = document.createElement('a');
            link.href = excelPath;
            link.download = filename;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // 다운로드 확인 메시지
            const messages = {{
                'ko': '✅ Excel 파일이 다운로드되었습니다.',
                'en': '✅ Excel file has been downloaded.',
                'vi': '✅ Tệp Excel đã được tải xuống.'
            }};
            alert(messages[currentLanguage] || messages['ko']);
        }}

        // 데이터 신선도 업데이트 함수
        function updateDataFreshness() {{
            // Config의 last_updated 타임스탬프 (embedded in HTML during generation)
            const configLastUpdated = '{config_last_updated}'; // Format: "2025-11-21T12:54:38.600870"

            if (!configLastUpdated || configLastUpdated === '') {{
                console.warn('Config last_updated timestamp not found');
                return;
            }}

            try {{
                const lastUpdate = new Date(configLastUpdated);
                const now = new Date();
                const minutesAgo = Math.floor((now - lastUpdate) / 60000);

                const badge = document.getElementById('dataFreshnessBadge');
                const icon = document.getElementById('freshnessIcon');
                const text = document.getElementById('freshnessText');
                const detail = document.getElementById('freshnessDetail');

                if (!badge || !icon || !text || !detail) return;

                // 언어별 텍스트
                const texts = {{
                    ko: {{
                        fresh: '🟢 최신 데이터',
                        moderate: '🟡 업데이트 권장',
                        stale: '🔴 데이터 오래됨',
                        lastUpdate: '데이터 동기화',
                        minutesAgo: '분 전',
                        nextUpdate: '다음 자동 동기화',
                        minutes: '분 후'
                    }},
                    en: {{
                        fresh: '🟢 Fresh Data',
                        moderate: '🟡 Update Recommended',
                        stale: '🔴 Data Outdated',
                        lastUpdate: 'Data Sync',
                        minutesAgo: 'min ago',
                        nextUpdate: 'Next Auto Sync',
                        minutes: 'min'
                    }},
                    vi: {{
                        fresh: '🟢 Dữ liệu mới',
                        moderate: '🟡 Nên cập nhật',
                        stale: '🔴 Dữ liệu cũ',
                        lastUpdate: 'Đồng bộ dữ liệu',
                        minutesAgo: 'phút trước',
                        nextUpdate: 'Tự động đồng bộ tiếp',
                        minutes: 'phút'
                    }}
                }};

                const lang = currentLanguage || 'ko';
                const t = texts[lang];

                // 다음 자동 업데이트 시간 계산 (30분 주기)
                const nextUpdateMinutes = 30 - (minutesAgo % 30);

                // 시간/분 단위 처리
                let timeAgoText;
                if (minutesAgo >= 60) {{
                    const hoursAgo = Math.floor(minutesAgo / 60);
                    const remainingMinutes = minutesAgo % 60;
                    const hourUnit = currentLanguage === 'ko' ? '시간' : currentLanguage === 'vi' ? 'giờ' : 'hr';
                    timeAgoText = remainingMinutes > 0
                        ? `${{hoursAgo}}${{hourUnit}} ${{remainingMinutes}}${{t.minutesAgo}}`
                        : `${{hoursAgo}}${{hourUnit}} ${{t.minutesAgo.replace('분 ', '').replace('min ', '').replace('phút ', '')}}`;
                }} else {{
                    timeAgoText = `${{minutesAgo}}${{t.minutesAgo}}`;
                }}

                // 상태 텍스트 및 테두리 색상 결정
                let statusText, borderColor;
                if (minutesAgo < 20) {{
                    statusText = t.fresh;
                    borderColor = '#28a745';  // 초록
                }} else if (minutesAgo < 40) {{
                    statusText = t.moderate;
                    borderColor = '#ffc107';  // 노랑
                }} else {{
                    statusText = t.stale;
                    borderColor = '#dc3545';  // 빨강
                }}

                // 스타일 업데이트 (흰색 배경 유지, 테두리 색상만 변경)
                badge.style.borderLeft = `4px solid ${{borderColor}}`;

                text.textContent = statusText;
                detail.textContent = `${{t.lastUpdate}}: ${{timeAgoText}} | ${{t.nextUpdate}}: ${{nextUpdateMinutes}}${{t.minutes}}`;

            }} catch (error) {{
                console.error('Error updating data freshness:', error);
            }}
        }}

        // 모든 텍스트 업데이트 - 완전한 구현
        function updateAllTexts() {{
            // === 1단계: data-i18n 속성을 가진 모든 요소 자동 업데이트 ===
            document.querySelectorAll('[data-i18n]').forEach(element => {{
                const key = element.getAttribute('data-i18n');
                if (key) {{
                    const translation = getTranslation(key, currentLanguage);
                    if (translation && translation !== key) {{
                        element.textContent = translation;
                    }}
                }}
            }});

            // data-i18n-title 속성 (툴팁) 업데이트
            document.querySelectorAll('[data-i18n-title]').forEach(element => {{
                const key = element.getAttribute('data-i18n-title');
                if (key) {{
                    const translation = getTranslation(key, currentLanguage);
                    if (translation && translation !== key) {{
                        element.setAttribute('title', translation);
                    }}
                }}
            }});

            // === 2단계: 개별 요소 업데이트 ===
            // 메인 헤더 업데이트
            const mainTitleElement = document.getElementById('mainTitle');
            if (mainTitleElement) {{
                mainTitleElement.innerHTML = getTranslation('headers.mainTitle', currentLanguage) + ' <span class="version-badge">V9.0</span>';
            }}
            
            // 날짜 관련 업데이트
            const yearText = '{year}';
            const monthText = currentLanguage === 'ko' ? '{get_korean_month(month)}' :
                              currentLanguage === 'en' ? '{month.capitalize()}' :
                              '{get_month_translation(month, "vi")}';

            const mainSubtitle = document.getElementById('mainSubtitle');
            if (mainSubtitle) {{
                const yearUnit = currentLanguage === 'ko' ? '년' : '';
                const incentiveText = getTranslation('headers.incentiveStatus', currentLanguage);
                mainSubtitle.innerHTML = yearText + yearUnit + ' ' + monthText + ' ' + incentiveText;
            }}
            
            const generationDate = document.getElementById('generationDate');
            if (generationDate) {{
                const dateLabel = getTranslation('headers.reportDateLabel', currentLanguage);
                const year = generationDate.getAttribute('data-year');
                const month = generationDate.getAttribute('data-month');
                const day = generationDate.getAttribute('data-day');
                const hour = generationDate.getAttribute('data-hour');
                const minute = generationDate.getAttribute('data-minute');
                
                let formattedDate;
                if (currentLanguage === 'ko') {{
                    formattedDate = `${{year}}년 ${{month}}월 ${{day}}일 ${{hour}}:${{minute}}`;
                }} else if (currentLanguage === 'en') {{
                    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    formattedDate = `${{monthNames[parseInt(month)-1]}} ${{day}}, ${{year}} ${{hour}}:${{minute}}`;
                }} else {{
                    formattedDate = `${{day}}/${{month}}/${{year}} ${{hour}}:${{minute}}`;
                }}
                generationDate.innerHTML = dateLabel + ' ' + formattedDate;
            }}

            // data 기간 섹션 업데이트
            const dataPeriodTitle = document.getElementById('dataPeriodTitle');
            if (dataPeriodTitle) {{
                dataPeriodTitle.innerHTML = getTranslation('headers.dataPeriod.title', currentLanguage);
            }}

            // 각 data 기간 항목 업데이트
            const dataPeriodItems = [
                {{id: 'incentiveDataPeriod', key: 'incentiveData'}},
                {{id: 'attendanceDataPeriod', key: 'attendanceData'}},
                {{id: 'aqlDataPeriod', key: 'aqlData'}},
                {{id: '5prsDataPeriod', key: '5prsData'}},
                {{id: 'manpowerDataPeriod', key: 'manpowerData'}}
            ];

            dataPeriodItems.forEach(item => {{
                const element = document.getElementById(item.id);
                if (element) {{
                    const year = element.getAttribute('data-year');
                    const month = element.getAttribute('data-month');
                    const startDay = element.getAttribute('data-startday');
                    const endDay = element.getAttribute('data-endday');
                    const dataLabel = getTranslation('headers.dataPeriod.' + item.key, currentLanguage);

                    let periodText;
                    if (item.key === 'manpowerData') {{
                        // 기본 인력 데이터는 월 기준만 표시
                        if (currentLanguage === 'ko') {{
                            periodText = `• ${{dataLabel}}: ${{year}}년 ${{month}}월 기준`;
                        }} else if (currentLanguage === 'en') {{
                            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                            periodText = `• ${{dataLabel}}: Based on ${{monthNames[parseInt(month)-1]}} ${{year}}`;
                        }} else {{
                            periodText = `• ${{dataLabel}}: Dựa trên tháng ${{month}}/${{year}}`;
                        }}
                    }} else {{
                        // 다른 데이터는 기간 표시
                        if (currentLanguage === 'ko') {{
                            periodText = `• ${{dataLabel}}: ${{year}}년 ${{month}}월 ${{startDay}}일 ~ ${{endDay}}일`;
                        }} else if (currentLanguage === 'en') {{
                            const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                            periodText = `• ${{dataLabel}}: ${{monthNames[parseInt(month)-1]}} ${{startDay}} - ${{endDay}}, ${{year}}`;
                        }} else {{
                            periodText = `• ${{dataLabel}}: ${{startDay}}/${{month}} - ${{endDay}}/${{month}}/${{year}}`;
                        }}
                    }}
                    element.innerHTML = periodText;
                }}
            }});

            // 요약 카드 라벨 업데이트
            const cardLabels = {{
                'totalEmployeesLabel': 'summary.cards.totalEmployees',
                'paidEmployeesLabel': 'summary.cards.paidEmployees',
                'eligibleEmployeesLabel': 'summary.cards.eligibleEmployees',
                'paymentRateLabel': 'summary.cards.paymentRate',
                'totalAmountLabel': 'summary.cards.totalAmount'
            }};
            
            for (const [id, key] of Object.entries(cardLabels)) {{
                const elem = document.getElementById(id);
                if (elem) elem.textContent = getTranslation(key, currentLanguage);
            }}
            
            // 단위 업데이트 - getUnit 함count use
            const totalEmployeesUnit = document.getElementById('totalEmployeesUnit');
            const paidEmployeesUnit = document.getElementById('paidEmployeesUnit');

            if (totalEmployeesUnit) {{
                totalEmployeesUnit.textContent = getUnit('people');
            }}

            if (paidEmployeesUnit) {{
                paidEmployeesUnit.textContent = getUnit('people');
            }}
            
            // 탭 메뉴 업데이트
            const tabs = {{
                'tabSummary': 'tabs.summary',
                'tabPosition': 'tabs.position',
                'tabIndividual': 'tabs.individual',
                'tabCriteria': 'tabs.criteria',
                'tabOrgChart': 'tabs.orgChart',
                'tabValidation': 'tabs.validation'
            }};
            
            for (const [id, key] of Object.entries(tabs)) {{
                const elem = document.getElementById(id);
                if (elem) elem.textContent = getTranslation(key, currentLanguage);
            }}
            
            // 탭 컨텐츠 제목 업데이트
            const tabTitles = {{
                'summaryTabTitle': 'summary.typeTable.title',
                'positionTabTitle': 'position.title',
                'individualDetailTitle': 'individual.title',
                'validationTabTitle': 'tabs.validation'
            }};
            
            for (const [id, key] of Object.entries(tabTitles)) {{
                const elem = document.getElementById(id);
                if (elem) elem.textContent = getTranslation(key, currentLanguage);
            }}
            
            // 요약 테이블 헤더 업데이트
            const summaryHeaders = {{
                'summaryTypeHeader': 'summary.typeTable.columns.type',
                'summaryTotalHeader': 'summary.typeTable.columns.totalEmployees',
                'summaryEligibleHeader': 'summary.typeTable.columns.eligible',
                'summaryPaymentRateHeader': 'summary.typeTable.columns.paymentRate',
                'summaryTotalAmountHeader': 'summary.typeTable.columns.totalAmount',
                'summaryAvgAmountHeader': 'summary.cards.avgAmount',
                'summaryAvgEligibleHeader': 'summary.chartLabels.recipientBased',
                'summaryAvgTotalHeader': 'summary.chartLabels.totalBased'
            }};
            
            for (const [id, key] of Object.entries(summaryHeaders)) {{
                const elem = document.getElementById(id);
                if (elem) elem.textContent = getTranslation(key, currentLanguage);
            }}
            
            // 개인별 상세 테이블 헤더 업데이트
            const individualHeaders = {{
                'empIdHeader': 'individual.table.columns.employeeId',
                'nameHeader': 'individual.table.columns.name',
                'positionHeader': 'individual.table.columns.position',
                'typeHeader': 'individual.table.columns.type',
                'statusHeader': 'individual.table.columns.status',
                'detailsHeader': 'individual.table.columns.details'
            }};
            
            for (const [id, key] of Object.entries(individualHeaders)) {{
                const elem = document.getElementById(id);
                if (elem) elem.textContent = getTranslation(key, currentLanguage);
            }}

            // monthby 헤더 동적 업데이트
            const prevMonthHeader = document.getElementById('prevMonthHeader');
            const currentMonthHeader = document.getElementById('currentMonthHeader');

            // Previous month과 현재 month 이름 설정
            const prevMonthName = '{prev_month_name}';
            const currentMonthName = '{month}';

            // AQL Failures 컬럼명 (현재 월 기준으로 동적 생성)
            const aqlFailuresColumn = currentMonthName.charAt(0).toUpperCase() + currentMonthName.slice(1) + ' AQL Failures';
            window.aqlFailuresColumn = aqlFailuresColumn; // 전역 변수로 저장

            if (prevMonthHeader) {{
                if (currentLanguage === 'ko') {{
                    prevMonthHeader.textContent = '{get_korean_month(prev_month_name)}';
                }} else if (currentLanguage === 'en') {{
                    prevMonthHeader.textContent = prevMonthName.charAt(0).toUpperCase() + prevMonthName.slice(1);
                }} else {{
                    // Vietnamese
                    const monthNum = {{'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}}[prevMonthName.toLowerCase()];
                    prevMonthHeader.textContent = 'Tháng ' + monthNum;
                }}
            }}

            if (currentMonthHeader) {{
                if (currentLanguage === 'ko') {{
                    currentMonthHeader.textContent = '{get_korean_month(month)}';
                }} else if (currentLanguage === 'en') {{
                    currentMonthHeader.textContent = currentMonthName.charAt(0).toUpperCase() + currentMonthName.slice(1);
                }} else {{
                    // Vietnamese
                    const monthNum = {{'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}}[currentMonthName.toLowerCase()];
                    currentMonthHeader.textContent = 'Tháng ' + monthNum;
                }}
            }}
            
            // 필터 업데이트
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {{
                searchInput.placeholder = getTranslation('individual.filters.search', currentLanguage);
            }}
            
            // 필터 옵션 텍스트 업데이트
            const optAllTypes = document.getElementById('optAllTypes');
            if (optAllTypes) optAllTypes.textContent = getTranslation('individual.filters.allTypes', currentLanguage);
            
            const optPaymentAll = document.getElementById('optPaymentAll');
            if (optPaymentAll) optPaymentAll.textContent = getTranslation('individual.filters.allStatus', currentLanguage);
            
            const optPaymentPaid = document.getElementById('optPaymentPaid');
            if (optPaymentPaid) optPaymentPaid.textContent = getTranslation('status.paid', currentLanguage);
            
            const optPaymentUnpaid = document.getElementById('optPaymentUnpaid');
            if (optPaymentUnpaid) optPaymentUnpaid.textContent = getTranslation('status.unpaid', currentLanguage);
            
            // Report Type Banner 업데이트
            const reportTypeBanner = document.getElementById('reportTypeBanner');
            if (reportTypeBanner) {{
                const isInterim = {str(is_interim_report).lower()};
                reportType = isInterim ? 'interim' : 'final'; // const 제거, 전역 변count use

                // Title 업데이트
                const reportTypeTitle = document.getElementById('reportTypeTitle');
                if (reportTypeTitle) {{
                    reportTypeTitle.textContent = getTranslation('reportTypeBanner.' + reportType + '.title', currentLanguage);
                }}

                // Description 업데이트
                const reportTypeDesc = document.getElementById('reportTypeDesc');
                if (reportTypeDesc) {{
                    reportTypeDesc.textContent = getTranslation('reportTypeBanner.' + reportType + '.description', currentLanguage);
                }}

                // Generated on date 업데이트
                const generatedText = getTranslation('reportTypeBanner.generatedOn', currentLanguage);
                const dayText = currentLanguage === 'ko' ? '{current_day}th' :
                               currentLanguage === 'en' ? 'Day {current_day}' :
                               'Ngày {current_day}';
                const dateSpan = reportTypeBanner.querySelector('span[style*="font-size: 0.85rem"]');
                if (dateSpan) {{
                    dateSpan.textContent = generatedText + ': ' + dayText;
                }}
            }}

            // Summary 테이블의 "직원" 단위 업데이트
            const typeSummaryBody = document.getElementById('typeSummaryBody');
            if (typeSummaryBody) {{
                const rows = typeSummaryBody.querySelectorAll('tr');
                rows.forEach(row => {{
                    const cells = row.querySelectorAll('td');
                    // 2번째 칼럼 (Total)과 3번째 칼럼 (Eligible)에 "직원" 단위가 있음
                    if (cells.length > 2) {{
                        // Total 칼럼 - 모든 available 단위를 체크
                        const totalText = cells[1].textContent;
                        if (totalText.includes('직원') || totalText.includes('people') || totalText.includes('người')) {{
                            // 숫자만 추출
                            const number = totalText.replace(/[^\\\\d]/g, '');
                            cells[1].textContent = number + getTranslation('common.people', currentLanguage);
                        }}
                        // Eligible 칼럼 - 모든 available 단위를 체크
                        const eligibleText = cells[2].textContent;
                        if (eligibleText.includes('직원') || eligibleText.includes('people') || eligibleText.includes('người')) {{
                            // 숫자만 추출
                            const number = eligibleText.replace(/[^\\d]/g, '');
                            cells[2].textContent = number + getTranslation('common.people', currentLanguage);
                        }}
                    }}
                }});
            }}
            
            // incentive 기준 탭 텍스트 업데이트
            updateCriteriaTabTexts();
            
            // Talent Program 섹션 텍스트 업데이트
            updateTalentProgramTexts();

            // Org Chart 텍스트 업데이트
            updateOrgChartUIText();

            // 차트 업데이트 (차트가 있는 경우)
            if (window.pieChart) {{
                updateChartLabels();
            }}

            // 다운로드 버튼 텍스트 업데이트
            const downloadHtmlBtnText = document.getElementById('downloadHtmlBtnText');
            if (downloadHtmlBtnText) {{
                const htmlTexts = {{
                    'ko': '📦 Offline 버전',
                    'en': '📦 Offline Version',
                    'vi': '📦 Phiên bản ngoại tuyến'
                }};
                downloadHtmlBtnText.textContent = htmlTexts[currentLanguage] || htmlTexts['ko'];
            }}

            // CSV download button removed per user request

            const downloadExcelBtnText = document.getElementById('downloadExcelBtnText');
            if (downloadExcelBtnText) {{
                const excelTexts = {{
                    'ko': '📗 Excel 다운로드',
                    'en': '📗 Download Excel',
                    'vi': '📗 Tải Excel'
                }};
                downloadExcelBtnText.textContent = excelTexts[currentLanguage] || excelTexts['ko'];
            }}

            // 직급별 테이블 및 개인별 테이블 재creation
            updateTabContents();
        }}
        
        // 탭 콘텐츠 업데이트
        function updateTabContents() {{
            // Summary 테이블 재생성
            if (typeof generateTypeTable === 'function') {{
                generateTypeTable();
            }}
            // 개by 테이블 재creation
            generateEmployeeTable();
            generatePositionTables();
        }}
        
        // incentive 기준 탭 텍스트 업데이트 - 완전한 동적 번역
        function updateCriteriaTabTexts() {{
            // 메인 제목
            const criteriaTitle = document.getElementById('criteriaMainTitle');
            if (criteriaTitle) {{
                criteriaTitle.textContent = getTranslation('criteria.mainTitle', currentLanguage);
            }}
            
            // 핵심 principle 섹션
            const corePrinciplesTitle = document.getElementById('corePrinciplesTitle');
            if (corePrinciplesTitle) {{
                corePrinciplesTitle.innerHTML = getTranslation('criteria.corePrinciples.title', currentLanguage);
            }}
            
            const corePrinciplesDesc1 = document.getElementById('corePrinciplesDesc1');
            if (corePrinciplesDesc1) {{
                corePrinciplesDesc1.innerHTML = getTranslation('criteria.corePrinciples.description1', currentLanguage);
            }}
            
            const corePrinciplesDesc2 = document.getElementById('corePrinciplesDesc2');
            if (corePrinciplesDesc2) {{
                corePrinciplesDesc2.innerHTML = getTranslation('criteria.corePrinciples.description2', currentLanguage);
            }}
            
            // 10가지 평가 조건 제목
            const evaluationTitle = document.getElementById('evaluationConditionsTitle');
            if (evaluationTitle) {{
                evaluationTitle.textContent = getTranslation('criteria.evaluationConditions.title', currentLanguage);
            }}
            
            // 테이블 헤더 업데이트 - 더 정확한 선택자 use
            document.querySelectorAll('.cond-th-number').forEach(th => {{
                th.textContent = '#';
            }});
            document.querySelectorAll('.cond-th-name').forEach(th => {{
                th.textContent = getTranslation('criteria.evaluationConditions.tableHeaders.conditionName', currentLanguage) || '조건직원';
            }});
            document.querySelectorAll('.cond-th-criteria').forEach(th => {{
                th.textContent = getTranslation('criteria.evaluationConditions.tableHeaders.criteria', currentLanguage) || '기준';
            }});
            document.querySelectorAll('.cond-th-desc').forEach(th => {{
                th.textContent = getTranslation('criteria.evaluationConditions.tableHeaders.description', currentLanguage) || '설직원';
            }});

            // 조건직원과 설직원 updated
            const conditionTranslations = {{
                1: {{
                    name: getTranslation('criteria.conditions.1.name', currentLanguage) || '출근율',
                    desc: getTranslation('criteria.conditions.1.description', currentLanguage) || '월간 출근율이 88% 이상이어야 합니다'
                }},
                2: {{
                    name: getTranslation('criteria.conditions.2.name', currentLanguage) || '무단결근',
                    desc: getTranslation('criteria.conditions.2.description', currentLanguage) || '사전 승인 없는 결근이 month 2일 이하여야 합니다'
                }},
                3: {{
                    name: getTranslation('criteria.conditions.3.name', currentLanguage) || 'actual 근무일',
                    desc: getTranslation('criteria.conditions.3.description', currentLanguage) || 'actual 출근한 날이 1일 이상이어야 합니다'
                }},
                4: {{
                    name: getTranslation('criteria.conditions.4.name', currentLanguage) || '최소 근무일',
                    desc: getTranslation('criteria.conditions.4.description', currentLanguage) || '월간 최소 12일 이상 work해야 합니다'
                }},
                5: {{
                    name: getTranslation('criteria.conditions.5.name', currentLanguage) || '개인 AQL (당month)',
                    desc: getTranslation('criteria.conditions.5.description', currentLanguage) || '당month 개인 AQL 검사 failed가 없어야 합니다'
                }},
                6: {{
                    name: getTranslation('criteria.conditions.6.name', currentLanguage) || '개인 AQL (연속성)',
                    desc: getTranslation('criteria.conditions.6.description', currentLanguage) || '최근 3개월간 연속으로 AQL failed가 없어야 합니다'
                }},
                7: {{
                    name: getTranslation('criteria.conditions.7.name', currentLanguage) || '팀/구역 AQL',
                    desc: getTranslation('criteria.conditions.7.description', currentLanguage) || '관리하는 팀/구역에서 3연속 개월 실패자가 없어야 합니다'
                }},
                8: {{
                    name: getTranslation('criteria.conditions.8.name', currentLanguage) || '담당구역 AQL Reject율',
                    desc: getTranslation('criteria.conditions.8.description', currentLanguage) || '담당 구역의 AQL 리젝률이 3% 미만이어야 합니다'
                }},
                9: {{
                    name: getTranslation('criteria.conditions.9.name', currentLanguage) || '5PRS 통과율',
                    desc: getTranslation('criteria.conditions.9.description', currentLanguage) || '5족 평가 시스템에서 95% 이상 통과해야 합니다'
                }},
                10: {{
                    name: getTranslation('criteria.conditions.10.name', currentLanguage) || '5PRS 검사량',
                    desc: getTranslation('criteria.conditions.10.description', currentLanguage) || '월간 최소 100개 이상 검사를 count행해야 합니다'
                }}
            }};

            // 조건 테이블 내용 업데이트
            for (let i = 1; i <= 10; i++) {{
                const nameEl = document.querySelector(`.cond-name-${{i}}`);
                const descEl = document.querySelector(`.cond-desc-${{i}}`);
                if (nameEl && conditionTranslations[i]) {{
                    nameEl.textContent = conditionTranslations[i].name;
                }}
                if (descEl && conditionTranslations[i]) {{
                    descEl.textContent = conditionTranslations[i].desc;
                }}
            }}
            
            // 출근 조건 섹션
            const attendanceTitle = document.getElementById('attendanceConditionTitle');
            if (attendanceTitle) {{
                attendanceTitle.textContent = getTranslation('criteria.conditions.attendance.title', currentLanguage);
            }}
            
            // AQL 조건 섹션
            const aqlTitle = document.getElementById('aqlConditionTitle');
            if (aqlTitle) {{
                aqlTitle.textContent = getTranslation('criteria.conditions.aql.title', currentLanguage);
            }}
            
            // 5PRS 조건 섹션
            const prsTitle = document.getElementById('prsConditionTitle');
            if (prsTitle) {{
                prsTitle.textContent = getTranslation('criteria.conditions.5prs.title', currentLanguage);
            }}
            
            // 직급별 apply 조건 섹션
            const positionMatrixTitle = document.getElementById('positionMatrixTitle');
            if (positionMatrixTitle) {{
                positionMatrixTitle.textContent = getTranslation('criteria.positionMatrix.title', currentLanguage);
            }}

            // 직급별 테이블 헤더 번역
            document.querySelectorAll('.pos-header-position').forEach(th => {{
                th.textContent = getTranslation('criteria.positionMatrix.tableHeaders.position', currentLanguage) || '직급';
            }});
            document.querySelectorAll('.pos-header-conditions').forEach(th => {{
                th.textContent = getTranslation('criteria.positionMatrix.tableHeaders.conditions', currentLanguage) || 'apply 조건';
            }});
            document.querySelectorAll('.pos-header-count').forEach(th => {{
                th.textContent = getTranslation('criteria.positionMatrix.tableHeaders.count', currentLanguage) || '조건 count';
            }});
            document.querySelectorAll('.pos-header-notes').forEach(th => {{
                th.textContent = getTranslation('criteria.positionMatrix.tableHeaders.notes', currentLanguage) || '비고';
            }})
            
            // TYPE 헤더 업데이트
            const type1Header = document.getElementById('type1Header');
            if (type1Header) {{
                type1Header.textContent = getTranslation('criteria.positionMatrix.typeHeaders.type1', currentLanguage);
            }}
            
            // TYPE-2, TYPE-3 헤더 및 테이블 내용 업데이트
            const type2Header = document.getElementById('type2Header');
            if (type2Header) {{
                type2Header.textContent = getTranslation('criteria.positionMatrix.typeHeaders.type2', currentLanguage);
            }}
            
            const type3Header = document.getElementById('type3Header');
            if (type3Header) {{
                type3Header.textContent = getTranslation('criteria.positionMatrix.typeHeaders.type3', currentLanguage);
            }}
            
            // TYPE-2 테이블 내용
            const type2AllPositions = document.getElementById('type2AllPositions');
            if (type2AllPositions) {{
                type2AllPositions.textContent = getTranslation('criteria.positionMatrix.type2Table.allType2', currentLanguage);
            }}
            
            const type2FourConditions = document.getElementById('type2FourConditions');
            if (type2FourConditions) {{
                type2FourConditions.textContent = getTranslation('criteria.positionMatrix.type2Table.fourConditions', currentLanguage);
            }}
            
            const type2AttendanceOnly = document.getElementById('type2AttendanceOnly');
            if (type2AttendanceOnly) {{
                type2AttendanceOnly.textContent = getTranslation('criteria.positionMatrix.type2Table.attendanceOnly', currentLanguage);
            }}
            
            // TYPE-3 테이블 내용
            const type3NewMember = document.getElementById('type3NewMember');
            if (type3NewMember) {{
                type3NewMember.textContent = getTranslation('criteria.positionMatrix.type3Table.newMember', currentLanguage);
            }}
            
            const type3NoConditions = document.getElementById('type3NoConditions');
            if (type3NoConditions) {{
                type3NoConditions.textContent = getTranslation('criteria.positionMatrix.type3Table.noConditions', currentLanguage);
            }}
            
            const type3ZeroConditions = document.getElementById('type3ZeroConditions');
            if (type3ZeroConditions) {{
                type3ZeroConditions.textContent = getTranslation('criteria.positionMatrix.type3Table.zeroConditions', currentLanguage);
            }}
            
            const type3NewMemberNote = document.getElementById('type3NewMemberNote');
            if (type3NewMemberNote) {{
                type3NewMemberNote.textContent = getTranslation('criteria.positionMatrix.type3Table.newMemberNote', currentLanguage);
            }}
            
            // TYPE-2 테이블 헤더
            const type2Headers = document.querySelectorAll('.type2-header-position, .type2-header-conditions, .type2-header-count, .type2-header-notes');
            type2Headers.forEach(header => {{
                if (header.classList.contains('type2-header-position')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.position', currentLanguage);
                }} else if (header.classList.contains('type2-header-conditions')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.appliedConditions', currentLanguage);
                }} else if (header.classList.contains('type2-header-count')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.conditionCount', currentLanguage);
                }} else if (header.classList.contains('type2-header-notes')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.notes', currentLanguage);
                }}
            }});
            
            // TYPE-3 테이블 헤더
            const type3Headers = document.querySelectorAll('.type3-header-position, .type3-header-conditions, .type3-header-count, .type3-header-notes');
            type3Headers.forEach(header => {{
                if (header.classList.contains('type3-header-position')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.position', currentLanguage);
                }} else if (header.classList.contains('type3-header-conditions')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.appliedConditions', currentLanguage);
                }} else if (header.classList.contains('type3-header-count')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.conditionCount', currentLanguage);
                }} else if (header.classList.contains('type3-header-notes')) {{
                    header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.notes', currentLanguage);
                }}
            }});
            
            // TYPE-2 calculation 방법 섹션 업데이트
            const type2CalculationTitle = document.getElementById('type2CalculationTitle');
            if (type2CalculationTitle) {{
                type2CalculationTitle.textContent = getTranslation('incentiveCalculation.type2CalculationTitle', currentLanguage);
            }}

            const type2PrincipleLabel = document.getElementById('type2PrincipleLabel');
            if (type2PrincipleLabel) {{
                type2PrincipleLabel.textContent = getTranslation('incentiveCalculation.type2CalculationPrincipleLabel', currentLanguage);
            }}

            const type2PrincipleText = document.getElementById('type2PrincipleText');
            if (type2PrincipleText) {{
                type2PrincipleText.textContent = getTranslation('incentiveCalculation.type2CalculationPrincipleText', currentLanguage);
            }}

            // TYPE-2 calculation 테이블 헤더
            document.querySelectorAll('.type2-calc-header-position').forEach(th => {{
                th.textContent = getTranslation('incentiveCalculation.type2CalcHeaderPosition', currentLanguage);
            }});
            document.querySelectorAll('.type2-calc-header-reference').forEach(th => {{
                th.textContent = getTranslation('incentiveCalculation.type2CalcHeaderReference', currentLanguage);
            }});
            document.querySelectorAll('.type2-calc-header-method').forEach(th => {{
                th.textContent = getTranslation('incentiveCalculation.type2CalcHeaderMethod', currentLanguage);
            }});
            document.querySelectorAll('.type2-calc-header-average').forEach(th => {{
                // "2025년 9월 평균" → 동적 생성
                const monthText = getTranslation('common.{month.lower()}', currentLanguage);
                th.textContent = getTranslation('incentiveCalculation.type2CalcHeaderAverage', currentLanguage).replace('{{{{month}}}}', monthText).replace('{{{{year}}}}', '{year}');
            }});

            // "평균" 텍스트 업데이트
            document.querySelectorAll('.average-text').forEach(span => {{
                span.textContent = getTranslation('incentiveCalculation.average', currentLanguage);
            }});

            // TYPE-1 테이블 조건 count 업데이트
            const conditionCounts = document.querySelectorAll('.condition-count');
            conditionCounts.forEach(count => {{
                const num = count.textContent.replace(/\\D/g, '');
                if (currentLanguage === 'ko') {{
                    count.textContent = num + '개';
                }} else if (currentLanguage === 'en') {{
                    count.textContent = num;
                }} else if (currentLanguage === 'vi') {{
                    count.textContent = num;
                }}
            }});
            
            // 직급 테이블 헤더
            const positionHeaders = document.querySelectorAll('.pos-header-position');
            positionHeaders.forEach(header => {{
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.position', currentLanguage);
            }});
            
            const conditionHeaders = document.querySelectorAll('.pos-header-conditions');
            conditionHeaders.forEach(header => {{
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.appliedConditions', currentLanguage);
            }});
            
            const countHeaders = document.querySelectorAll('.pos-header-count');
            countHeaders.forEach(header => {{
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.conditionCount', currentLanguage);
            }});
            
            const notesHeaders = document.querySelectorAll('.pos-header-notes');
            notesHeaders.forEach(header => {{
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.notes', currentLanguage);
            }});
            
            // incentive 금액 calculation 섹션
            const incentiveAmountTitle = document.querySelectorAll('#criteria .card')[2]?.querySelector('.card-header h5');
            if (incentiveAmountTitle) {{
                incentiveAmountTitle.textContent = getTranslation('criteria.incentiveAmount.title', currentLanguage);
            }}
            
            // Incentive Amount Table Translations
            const assemblyIncentiveTitle = document.getElementById('assemblyInspectorIncentiveTitle');
            if (assemblyIncentiveTitle) {{
                assemblyIncentiveTitle.textContent = getTranslation('incentiveCalculation.assemblyInspectorIncentiveTitle', currentLanguage);
            }}
            
            document.querySelectorAll('.consecutive-achievement-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.consecutiveAchievementMonths', currentLanguage);
            }});
            
            document.querySelectorAll('.incentive-amount-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.incentiveAmountVND', currentLanguage);
            }});
            
            // Month texts in table
            document.querySelectorAll('.month-text-1').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month1', currentLanguage);
            }});
            document.querySelectorAll('.month-text-2').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month2', currentLanguage);
            }});
            document.querySelectorAll('.month-text-3').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month3', currentLanguage);
            }});
            document.querySelectorAll('.month-text-4').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month4', currentLanguage);
            }});
            document.querySelectorAll('.month-text-5').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month5', currentLanguage);
            }});
            document.querySelectorAll('.month-text-6').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month6', currentLanguage);
            }});
            document.querySelectorAll('.month-text-7').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month7', currentLanguage);
            }});
            document.querySelectorAll('.month-text-8').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month8', currentLanguage);
            }});
            document.querySelectorAll('.month-text-9').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month9', currentLanguage);
            }});
            document.querySelectorAll('.month-text-10').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month10', currentLanguage);
            }});
            document.querySelectorAll('.month-text-11').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month11', currentLanguage);
            }});
            document.querySelectorAll('.month-text-12').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.simpleMonths.month12', currentLanguage);
            }});
            document.querySelectorAll('.month-or-more').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.orMore', currentLanguage);
            }});
            
            // TYPE-2 calculation section
            const type2CalcTitle = document.getElementById('type2CalculationTitle');
            if (type2CalcTitle) {{
                type2CalcTitle.textContent = getTranslation('incentiveCalculation.type2CalculationTitle', currentLanguage);
            }}
            
            document.querySelectorAll('.type2-principle-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type2CalculationPrincipleLabel', currentLanguage);
            }});
            
            document.querySelectorAll('.type2-principle-text').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type2CalculationPrincipleText', currentLanguage);
            }});
            
            document.querySelectorAll('.average-text').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.average', currentLanguage);
            }})
            
            // TYPE-1 incentive calculation 테이블 번역
            // 타이틀
            const type1CalcTitle = document.getElementById('type1CalculationTitle');
            if (type1CalcTitle) {{
                type1CalcTitle.textContent = getTranslation('incentiveCalculation.type1Title', currentLanguage);
            }}
            
            // 테이블 헤더
            document.querySelectorAll('.calc-header-position').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.tableHeaders.position', currentLanguage);
            }});
            document.querySelectorAll('.calc-header-method').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.tableHeaders.calculationMethod', currentLanguage);
            }});
            document.querySelectorAll('.calc-header-example').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.tableHeaders.actualExample', currentLanguage);
            }});
            
            // 직급직원
            document.querySelectorAll('.calc-position-manager').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.manager', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-amanager').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.aManager', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-vsupervisor').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.vSupervisor', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-groupleader').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.groupLeader', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-lineleader').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.lineLeader', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-aqlinspector').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.aqlInspector', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-assemblyinspector').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.assemblyInspector', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-audittraining').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.auditTraining', currentLanguage);
            }});
            document.querySelectorAll('.calc-position-modelmaster').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.positions.modelMaster', currentLanguage);
            }});
            
            // calculation 방법 관련 텍스트
            document.querySelectorAll('.calc-conditions-met').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.conditionsMet', currentLanguage);
            }});
            document.querySelectorAll('.calc-incentive-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.incentive', currentLanguage);
            }});
            document.querySelectorAll('.calc-line-leader-avg').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.lineLeaderAverage', currentLanguage);
            }});
            document.querySelectorAll('.calc-calculation-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.calculation', currentLanguage);
            }});
            document.querySelectorAll('.calc-condition-not-met-zero').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.conditionsNotMetZero', currentLanguage);
            }});
            
            // apply 조건 텍스트
            document.querySelectorAll('.calc-apply-condition-attendance').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.applyConditionAttendance', currentLanguage);
            }});
            document.querySelectorAll('.calc-apply-condition-lineleader').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.applyConditionLineLeader', currentLanguage);
            }});
            document.querySelectorAll('.calc-apply-condition-assembly').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.applyConditionAssembly', currentLanguage);
            }});
            document.querySelectorAll('.calc-apply-condition-audit').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.applyConditionAudit', currentLanguage);
            }});
            document.querySelectorAll('.calc-apply-condition-model').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.applyConditionModel', currentLanguage);
            }});
            
            // 특별 calculation 텍스트
            document.querySelectorAll('.calc-subordinate-incentive').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.subordinateIncentive', currentLanguage);
            }});
            document.querySelectorAll('.calc-subordinate-total').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.subordinateTotal', currentLanguage);
            }});
            document.querySelectorAll('.calc-receive-ratio').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.receivingRatio', currentLanguage);
            }});
            document.querySelectorAll('.calc-special-calculation').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.specialCalculation', currentLanguage);
            }});
            document.querySelectorAll('.calc-aql-evaluation').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.aqlEvaluation', currentLanguage);
            }});
            document.querySelectorAll('.calc-cfa-certificate').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.cfaCertificate', currentLanguage);
            }});
            document.querySelectorAll('.calc-cfa-holder-bonus').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.cfaHolderBonus', currentLanguage);
            }});
            document.querySelectorAll('.calc-hwk-claim').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.hwkClaim', currentLanguage);
            }});
            document.querySelectorAll('.calc-cfa-holder').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.cfaHolder', currentLanguage);
            }});
            document.querySelectorAll('.calc-consecutive-month-incentive').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.consecutiveMonthIncentive', currentLanguage);
            }});
            document.querySelectorAll('.calc-total-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.total', currentLanguage);
            }});
            
            // 예시 관련 텍스트
            document.querySelectorAll('.calc-example-employee').forEach(el => {{
                const employeeId = el.dataset.employee;
                el.textContent = getTranslation('incentiveCalculation.exampleEmployee', currentLanguage).replace('{{{{employeeId}}}}', employeeId);
            }});
            document.querySelectorAll('.calc-condition-not-met-days').forEach(el => {{
                const days = el.dataset.days;
                el.textContent = getTranslation('incentiveCalculation.conditionNotMetDays', currentLanguage).replace('{{{{days}}}}', days);
            }});
            document.querySelectorAll('.calc-example-consecutive').forEach(el => {{
                const months = el.dataset.months;
                el.textContent = getTranslation('incentiveCalculation.exampleConsecutiveFulfillment', currentLanguage).replace('{{{{months}}}}', months);
            }});
            document.querySelectorAll('.calc-example-max-achieved').forEach(el => {{
                const months = el.dataset.months;
                el.textContent = getTranslation('incentiveCalculation.exampleMaxAchieved', currentLanguage).replace('{{{{months}}}}', months);
            }});
            document.querySelectorAll('.calc-example-not-met-reset').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.exampleConditionsNotMetReset', currentLanguage);
            }});
            document.querySelectorAll('.calc-consecutive-months').forEach(el => {{
                const months = el.dataset.months;
                el.textContent = getTranslation('incentiveCalculation.consecutiveMonths', currentLanguage).replace('{{{{months}}}}', months);
            }});
            
            // 조건 평가 텍스트
            document.querySelectorAll('.calc-attendance-rate').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.attendanceRate', currentLanguage);
            }});
            document.querySelectorAll('.calc-unauthorized-absence').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.unauthorizedAbsence', currentLanguage);
            }});
            document.querySelectorAll('.calc-working-days').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.workingDays', currentLanguage);
            }});
            document.querySelectorAll('.calc-previous-month').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.previousMonth', currentLanguage);
            }});
            document.querySelectorAll('.calc-current-month-eval').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.currentMonthEvaluation', currentLanguage);
            }});
            document.querySelectorAll('.calc-all-attendance-met').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.allAttendanceConditionsMet', currentLanguage);
            }});
            document.querySelectorAll('.calc-team-aql-no-fail').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.teamAqlNoConsecutiveFail', currentLanguage);
            }});
            document.querySelectorAll('.calc-reject-rate').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.rejectRate', currentLanguage);
            }});
            document.querySelectorAll('.calc-reset-to-zero').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.resetToZeroMonths', currentLanguage);
            }});
            document.querySelectorAll('.calc-personal-aql-failures').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.personalAqlFailures', currentLanguage);
            }});
            document.querySelectorAll('.calc-pass-rate').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.passRate', currentLanguage);
            }});
            document.querySelectorAll('.calc-inspection-quantity').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.inspectionQuantity', currentLanguage);
            }});
            
            // th/개월/족/cases 단위 conversion
            document.querySelectorAll('.calc-days-text').forEach(el => {{
                const days = el.dataset.days;
                const unit = parseInt(days) <= 1 ? getTranslation('common.day', currentLanguage) : getTranslation('common.days', currentLanguage);
                el.textContent = currentLanguage === 'ko' ? `${{days}}${{unit}}` : `${{days}} ${{unit}}`;
            }});
            document.querySelectorAll('.calc-months-text').forEach(el => {{
                const months = el.dataset.months;
                const unit = getTranslation('incentiveCalculation.months', currentLanguage);
                el.textContent = currentLanguage === 'ko' ? `${{months}}${{unit}}` : `${{months}} ${{unit}}`;
            }});
            document.querySelectorAll('.calc-pieces-text').forEach(el => {{
                const pieces = el.dataset.pieces;
                const unit = getTranslation('incentiveCalculation.pieces', currentLanguage);
                el.textContent = currentLanguage === 'ko' ? `${{pieces}}${{unit}}` : `${{pieces}} ${{unit}}`;
            }});
            document.querySelectorAll('.calc-cases-text').forEach(el => {{
                const cases = el.dataset.cases;
                const unit = getTranslation('incentiveCalculation.cases', currentLanguage);
                el.textContent = currentLanguage === 'ko' ? `${{cases}}${{unit}}` : `${{cases}} ${{unit}}`;
            }});
            
            // Month range translations
            document.querySelectorAll('.calc-month-range-0to1').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month0to1', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-1').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month1', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-2').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month2', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-3').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month3', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-4').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month4', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-5').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month5', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-6').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month6', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-7').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month7', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-8').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month8', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-9').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month9', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-9plus').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month9plus', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-10').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month10', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-11').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month11', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-12plus').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month12plus', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-13plus').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month13plus', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-1-3').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month1to3', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-4-6').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month4to6', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-7-9').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month7to9', currentLanguage);
            }});
            document.querySelectorAll('.calc-month-range-10-12').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.monthRanges.month10to12', currentLanguage);
            }});
            document.querySelectorAll('.calc-waiting-period').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.waitingPeriod', currentLanguage);
            }});
            document.querySelectorAll('.calc-months-text').forEach(el => {{
                const months = el.dataset.months;
                const monthUnit = getTranslation('incentiveCalculation.month', currentLanguage);
                el.textContent = months + monthUnit;
            }});
            document.querySelectorAll('.calc-level-a').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.levelA', currentLanguage);
            }})
            
            // 특별 규칙 섹션
            const specialRulesTitle = document.querySelectorAll('#criteria .card')[3]?.querySelector('.card-header h5');
            if (specialRulesTitle) {{
                specialRulesTitle.textContent = getTranslation('criteria.specialRules.title', currentLanguage);
            }}
            
            // Good to Know 섹션
            const goodToKnowTitle = document.getElementById('goodToKnowTitle');
            if (goodToKnowTitle) {{
                goodToKnowTitle.textContent = getTranslation('criteria.goodToKnow.title', currentLanguage);
            }}
            
            const corePrinciplesSubtitle = document.getElementById('corePrinciplesSubtitle');
            if (corePrinciplesSubtitle) {{
                corePrinciplesSubtitle.textContent = getTranslation('criteria.goodToKnow.corePrinciplesSubtitle', currentLanguage);
            }}
            
            // FAQ 섹션
            const faqTitle = document.querySelectorAll('#criteria .card')[4]?.querySelector('.card-header h5');
            if (faqTitle) {{
                faqTitle.textContent = getTranslation('criteria.faq.title', currentLanguage);
            }}
            
            // FAQ calculation 예시 섹션 번역
            updateFAQExamples();
            
            // 출근율 calculation 방식 섹션 번역
            updateAttendanceSection();
            
            // FAQ Q&A 섹션 번역
            updateFAQQASection();
            
            // TYPE-3 섹션 번역
            const type3SectionTitle = document.getElementById('type3SectionTitle');
            if (type3SectionTitle) {{
                type3SectionTitle.textContent = getTranslation('incentiveCalculation.type3Section.title', currentLanguage);
            }}
            
            document.querySelectorAll('.type3-position-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type3Section.position', currentLanguage);
            }});
            document.querySelectorAll('.type3-standard-incentive-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type3Section.standardIncentive', currentLanguage);
            }});
            document.querySelectorAll('.type3-calculation-method-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type3Section.calculationMethod', currentLanguage);
            }});
            document.querySelectorAll('.type3-new-qip-member').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type3Section.newQipMember', currentLanguage);
            }});
            document.querySelectorAll('.type3-no-incentive').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type3Section.noIncentive', currentLanguage);
            }});
            document.querySelectorAll('.type3-one-month-training').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type3Section.oneMonthTraining', currentLanguage);
            }});
            document.querySelectorAll('.type3-type-reclassification').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.type3Section.typeReclassification', currentLanguage);
            }});
            
            // Good to Know 섹션 번역
            const goodToKnowTitleElem = document.getElementById('goodToKnowTitle');
            if (goodToKnowTitleElem) {{
                goodToKnowTitleElem.innerHTML = '💡 ' + getTranslation('incentiveCalculation.goodToKnow.title', currentLanguage);
            }}
            
            const corePrinciplesTitleElem = document.getElementById('corePrinciplesSubtitle');
            if (corePrinciplesTitleElem) {{
                corePrinciplesTitleElem.textContent = getTranslation('incentiveCalculation.goodToKnow.corePrinciples', currentLanguage);
            }}
            
            document.querySelectorAll('.failure-principle-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.failurePrinciple', currentLanguage).split(':')[0] + ':';
            }});
            document.querySelectorAll('.failure-principle-text').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.failurePrinciple', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.failurePrinciple', currentLanguage);
            }});
            
            document.querySelectorAll('.type2-principle-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.type2Principle', currentLanguage).split(':')[0] + ':';
            }});
            document.querySelectorAll('.type2-principle-text').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.type2Principle', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.type2Principle', currentLanguage);
            }});
            
            document.querySelectorAll('.consecutive-bonus-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.consecutiveBonus', currentLanguage).split(':')[0] + ':';
            }});
            document.querySelectorAll('.consecutive-bonus-text').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.consecutiveBonus', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.consecutiveBonus', currentLanguage);
            }});
            
            document.querySelectorAll('.special-calculation-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.specialCalculation', currentLanguage).split(':')[0] + ':';
            }});
            document.querySelectorAll('.special-calculation-text').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.specialCalculation', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.specialCalculation', currentLanguage);
            }});
            
            document.querySelectorAll('.condition-failure-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.conditionFailure', currentLanguage).split(':')[0] + ':';
            }});
            document.querySelectorAll('.condition-failure-text').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.conditionFailure', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.conditionFailure', currentLanguage);
            }});
            
            // monthby incentive 변동 요인 테이블
            const monthlyChangeTitle = document.getElementById('monthlyIncentiveChangeReasonsTitle');
            if (monthlyChangeTitle) {{
                monthlyChangeTitle.textContent = getTranslation('incentiveCalculation.goodToKnow.monthlyIncentiveChangeReasons', currentLanguage);
            }}
            
            document.querySelectorAll('.change-factors-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.changeFactors', currentLanguage);
            }});
            document.querySelectorAll('.impact-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.impact', currentLanguage);
            }});
            document.querySelectorAll('.example-header').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.example', currentLanguage);
            }});
            
            document.querySelectorAll('.minimum-days-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.minimumDays', currentLanguage);
            }});
            document.querySelectorAll('.less-than-12-days').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.lessThan12Days', currentLanguage);
            }});
            document.querySelectorAll('.november-11-days').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.november11Days', currentLanguage);
            }});
            
            document.querySelectorAll('.attendance-rate-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.attendanceRate', currentLanguage);
            }});
            document.querySelectorAll('.less-than-88-percent').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.lessThan88Percent', currentLanguage);
            }});
            document.querySelectorAll('.attendance-example').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.attendanceExample', currentLanguage);
            }});
            
            document.querySelectorAll('.unauthorized-absence-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.unauthorizedAbsence', currentLanguage);
            }});
            document.querySelectorAll('.more-than-3-days').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.moreThan3Days', currentLanguage);
            }});
            document.querySelectorAll('.unauthorized-example').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.unauthorizedExample', currentLanguage);
            }});
            
            document.querySelectorAll('.aql-failure-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.aqlFailure', currentLanguage);
            }});
            document.querySelectorAll('.current-month-failure').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.currentMonthFailure', currentLanguage);
            }});
            document.querySelectorAll('.aql-failure-example').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.aqlFailureExample', currentLanguage);
            }});
            
            document.querySelectorAll('.fprs-pass-rate-label').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.fprsPassRate', currentLanguage);
            }});
            document.querySelectorAll('.less-than-95-percent').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.lessThan95Percent', currentLanguage);
            }});
            document.querySelectorAll('.fprs-example').forEach(el => {{
                el.textContent = getTranslation('incentiveCalculation.goodToKnow.fprsExample', currentLanguage);
            }});
            
            // 조건 테이블 내용 업데이트
            updateConditionTablesContent();
        }}
        
        // 조건 테이블 내용 동적 업데이트 함count
        function updateConditionTablesContent() {{
            // 출근 조건 테이블 업데이트
            const attendanceTable = document.getElementById('attendanceTable');
            if (attendanceTable) {{
                const tbody = attendanceTable.querySelector('tbody');
                if (tbody) {{
                    const rows = tbody.querySelectorAll('tr');
                    if (rows.length >= 4) {{
                        // 조건 1: 출근율
                        rows[0].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.attendanceRate.name', currentLanguage);
                        rows[0].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.attendanceRate.criteria', currentLanguage);
                        rows[0].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.attendanceRate.description', currentLanguage);
                        
                        // 조건 2: 무단결근
                        rows[1].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.unapprovedAbsence.name', currentLanguage);
                        rows[1].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.unapprovedAbsence.criteria', currentLanguage);
                        rows[1].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.unapprovedAbsence.description', currentLanguage);
                        
                        // 조건 3: actual 근무일
                        rows[2].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.actualWorkingDays.name', currentLanguage);
                        rows[2].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.actualWorkingDays.criteria', currentLanguage);
                        rows[2].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.actualWorkingDays.description', currentLanguage);
                        
                        // 조건 4: 최소 근무일
                        rows[3].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.minimumWorkingDays.name', currentLanguage);
                        rows[3].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.minimumWorkingDays.criteria', currentLanguage);
                        rows[3].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.minimumWorkingDays.description', currentLanguage);
                    }}
                }}
            }}
            
            // AQL 조건 테이블 업데이트
            const aqlTable = document.getElementById('aqlTable');
            if (aqlTable) {{
                const tbody = aqlTable.querySelector('tbody');
                if (tbody) {{
                    const rows = tbody.querySelectorAll('tr');
                    if (rows.length >= 4) {{
                        // 조건 5: 개인 AQL (당month)
                        rows[0].cells[1].textContent = getTranslation('criteria.conditions.aql.items.personalFailure.name', currentLanguage);
                        rows[0].cells[2].textContent = getTranslation('criteria.conditions.aql.items.personalFailure.criteria', currentLanguage);
                        rows[0].cells[3].textContent = getTranslation('criteria.conditions.aql.items.personalFailure.description', currentLanguage);
                        
                        // 조건 6: 개인 AQL (연속성)
                        rows[1].cells[1].textContent = getTranslation('criteria.conditions.aql.items.personalContinuous.name', currentLanguage);
                        rows[1].cells[2].textContent = getTranslation('criteria.conditions.aql.items.personalContinuous.criteria', currentLanguage);
                        rows[1].cells[3].textContent = getTranslation('criteria.conditions.aql.items.personalContinuous.description', currentLanguage);
                        
                        // 조건 7: 팀/구역 AQL
                        rows[2].cells[1].textContent = getTranslation('criteria.conditions.aql.items.teamArea.name', currentLanguage);
                        rows[2].cells[2].textContent = getTranslation('criteria.conditions.aql.items.teamArea.criteria', currentLanguage);
                        rows[2].cells[3].textContent = getTranslation('criteria.conditions.aql.items.teamArea.description', currentLanguage);
                        
                        // 조건 8: 담당구역 reject
                        rows[3].cells[1].textContent = getTranslation('criteria.conditions.aql.items.areaReject.name', currentLanguage);
                        rows[3].cells[2].textContent = getTranslation('criteria.conditions.aql.items.areaReject.criteria', currentLanguage);
                        rows[3].cells[3].textContent = getTranslation('criteria.conditions.aql.items.areaReject.description', currentLanguage);
                    }}
                }}
            }}
            
            // 5PRS 조건 테이블 업데이트
            const prsTable = document.getElementById('prsTable');
            if (prsTable) {{
                const tbody = prsTable.querySelector('tbody');
                if (tbody) {{
                    const rows = tbody.querySelectorAll('tr');
                    if (rows.length >= 2) {{
                        // 조건 9: 5PRS 통과율
                        rows[0].cells[1].textContent = getTranslation('criteria.conditions.5prs.items.passRate.name', currentLanguage);
                        rows[0].cells[2].textContent = getTranslation('criteria.conditions.5prs.items.passRate.criteria', currentLanguage);
                        rows[0].cells[3].textContent = getTranslation('criteria.conditions.5prs.items.passRate.description', currentLanguage);
                        
                        // 조건 10: 5PRS 검사량
                        rows[1].cells[1].textContent = getTranslation('criteria.conditions.5prs.items.inspectionQty.name', currentLanguage);
                        rows[1].cells[2].textContent = getTranslation('criteria.conditions.5prs.items.inspectionQty.criteria', currentLanguage);
                        rows[1].cells[3].textContent = getTranslation('criteria.conditions.5prs.items.inspectionQty.description', currentLanguage);
                    }}
                }}
            }}
            
            // 직급별 특이사항 업데이트
            updatePositionMatrixNotes();
        }}
        
        // 직급별 특이사항 동적 업데이트
        function updatePositionMatrixNotes() {{
            // TYPE-1 테이블의 특이사항 column 업데이트
            const type1Tables = document.querySelectorAll('#criteria table');
            type1Tables.forEach(table => {{
                const tbody = table.querySelector('tbody');
                if (tbody) {{
                    const rows = tbody.querySelectorAll('tr');
                    rows.forEach(row => {{
                        const cells = row.querySelectorAll('td');
                        if (cells.length === 4) {{
                            const noteText = cells[3].textContent.trim();
                            // 특이사항 매핑 (모든 언어 매칭 조건 포함 - 베트남어 추가)
                            if (noteText.includes('출근 조건만') || noteText.includes('Attendance only') || noteText.includes('Chỉ điều kiện chấm công')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceOnly', currentLanguage);
                            }} else if ((noteText.includes('출근 + 팀/구역 AQL') || noteText.includes('Attendance + Team/Area AQL') || noteText.includes('Chấm công + AQL nhóm/khu vực')) && !noteText.includes('reject') && !noteText.includes('Từ chối')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceTeamAql', currentLanguage);
                            }} else if (noteText.includes('특별 계산') || noteText.includes('Special calculation') || noteText.includes('Đặc biệt')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceMonthAql', currentLanguage);
                            }} else if (noteText.includes('출근 + 개인 AQL + 5PRS') || noteText.includes('Attendance + Personal AQL + 5PRS') || noteText.includes('Chấm công + AQL cá nhân + 5PRS')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendancePersonalAql5prs', currentLanguage);
                            }} else if (noteText.includes('출근 + 팀/구역 AQL + 담당구역 reject') || noteText.includes('Attendance + Team/Area AQL + Area reject') || noteText.includes('Chấm công + AQL nhóm/khu vực + Từ chối khu vực')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceTeamAreaReject', currentLanguage);
                            }} else if (noteText.includes('출근 + 담당구역 reject') || noteText.includes('Attendance + Area reject') || noteText.includes('Chấm công + Từ chối khu vực')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceAreaReject', currentLanguage);
                            }} else if (noteText.includes('모든 조건') || noteText.includes('All conditions') || noteText.includes('Tất cả điều kiện')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.allConditions', currentLanguage);
                            }} else if (noteText.includes('조건 없음') || noteText.includes('No conditions') || noteText.includes('Không có điều kiện')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.noConditions', currentLanguage);
                            }}
                        }}
                    }});
                }}
            }});
        }}
        
        
            // 탭 버튼 텍스트 업데이트 (data-translate-tab 속성 사용)
            document.querySelectorAll('[data-translate-tab]').forEach(elem => {{
                const tabKey = elem.getAttribute('data-translate-tab');
                if (translations.tabs && translations.tabs[tabKey]) {{
                    elem.textContent = translations.tabs[tabKey][lang] || elem.textContent;
                }}
            }});

            // 테이블 헤더 업데이트 (data-translate 속성 사용)
            document.querySelectorAll('[data-translate]').forEach(elem => {{
                const key = elem.getAttribute('data-translate');
                if (translations.tableHeaders && translations.tableHeaders[key]) {{
                    elem.textContent = translations.tableHeaders[key][lang] || elem.textContent;
                }}
                if (translations.sectionTitles && translations.sectionTitles[key]) {{
                    elem.textContent = translations.sectionTitles[key][lang] || elem.textContent;
                }}
                if (translations.modalTitles && translations.modalTitles[key]) {{
                    elem.textContent = translations.modalTitles[key][lang] || elem.textContent;
                }}
            }});
            
            // 차트 라벨 업데이트
        function updateChartLabels() {{
            // 예제 차트 업데이트 코드
        }}
        
        // Typeby 요약 테이블 업데이트 함count
        function updateTypeSummaryTable() {{
            try {{
                // employeeData가 없으면 window.employeeData use
                const dataSource = window.employeeData || employeeData || [];

                if (!dataSource || dataSource.length === 0) {{
                    console.warn('No employee data available for Type summary');
                    return;
                }}

            // Typeby data 집계
            const typeData = {{
                'TYPE-1': {{ total: 0, paid: 0, totalAmount: 0 }},
                'TYPE-2': {{ total: 0, paid: 0, totalAmount: 0 }},
                'TYPE-3': {{ total: 0, paid: 0, totalAmount: 0 }}
            }};

            // total data 집계
            let grandTotal = 0;
            let grandPaid = 0;
            let grandAmount = 0;

            // 직원 data 순회하며 집계
            dataSource.forEach(emp => {{
                // type 필드를 여러 available 이름에서 찾기
                const type = emp.type || emp['ROLE TYPE STD'] || emp['Type'] || 'UNKNOWN';
                if (typeData[type]) {{
                    typeData[type].total++;
                    grandTotal++;

                    // 여러 available incentive 필드직원 확인
                    const amount = parseInt(
                        emp['{month.lower()}_incentive'] ||
                        emp['{month.lower().capitalize()}_Incentive'] ||
                        emp['Final Incentive amount'] ||
                        0
                    );

                    console.log('Type 확인:', type, '직원:', emp.name || emp['Full Name'], '금액:', amount);
                    if (amount > 0) {{
                        typeData[type].paid++;
                        typeData[type].totalAmount += amount;
                        grandPaid++;
                        grandAmount += amount;
                    }}
                }}
            }});

            // 테이블 tbody 업데이트
            const tbody = document.getElementById('typeSummaryBody');
            if (tbody) {{
                let html = '';
                const personUnit = getUnit('people');  // 언어별 단위 가져오기

                // 각 Type별 행 생성
                ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {{
                    const data = typeData[type];
                    const paymentRate = data.total > 0 ? (data.paid / data.total * 100).toFixed(1) : '0.0';
                    const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid) : 0;
                    const avgTotal = data.total > 0 ? Math.round(data.totalAmount / data.total) : 0;
                    const typeClass = type.toLowerCase().replace('type-', '');

                    html += '<tr>';
                    html += '<td><span class="type-badge type-' + typeClass + '">' + type + '</span></td>';
                    html += '<td>' + data.total + personUnit + '</td>';
                    html += '<td>' + data.paid + personUnit + '</td>';
                    html += '<td>' + paymentRate + '%</td>';
                    html += '<td>' + data.totalAmount.toLocaleString() + ' VND</td>';
                    html += '<td>' + avgPaid.toLocaleString() + ' VND</td>';
                    html += '<td>' + avgTotal.toLocaleString() + ' VND</td>';
                    html += '</tr>';
                }});

                // 합계 행 생성
                const totalPaymentRate = grandTotal > 0 ? (grandPaid / grandTotal * 100).toFixed(1) : '0.0';
                const totalAvgPaid = grandPaid > 0 ? Math.round(grandAmount / grandPaid) : 0;
                const totalAvgTotal = grandTotal > 0 ? Math.round(grandAmount / grandTotal) : 0;

                html += '<tr style="font-weight: bold; background-color: #f3f4f6;">';
                html += '<td>Total</td>';
                html += '<td>' + grandTotal + personUnit + '</td>';
                html += '<td>' + grandPaid + personUnit + '</td>';
                html += '<td>' + totalPaymentRate + '%</td>';
                html += '<td>' + grandAmount.toLocaleString() + ' VND</td>';
                html += '<td>' + totalAvgPaid.toLocaleString() + ' VND</td>';
                html += '<td>' + totalAvgTotal.toLocaleString() + ' VND</td>';
                html += '</tr>';

                tbody.innerHTML = html;
                console.log('Type별 요약 테이블 업데이트 완료');
            }}
            }} catch (e) {{
                console.error('updateTypeSummaryTable 오류:', e);
                // 오류 발생 시에도 기본 동작 시도
                if (window.employeeData && window.employeeData.length > 0) {{
                    console.log('오류 복구 시도 중...');
                }}
            }}
        }}
        
        // 초기화
        // 조직도 관련 함count들
        let orgChartData = null;
        let orgChartRoot = null;

        // 검증 탭 관련 함count들
        function initValidationTab() {{
            console.log('Initializing validation tab...');

            // interim report 여부 확인 (data 기간의 last 날 기준)
            const incentiveDataPeriod = document.getElementById('incentiveDataPeriod');
            const dataEndDay = incentiveDataPeriod ? parseInt(incentiveDataPeriod.getAttribute('data-endday')) : 0;
            const isInterimReport = dataEndDay < 20;

            // interim report 알림 표시
            if (isInterimReport) {{
                const notice = document.getElementById('interimReportNotice');
                if (notice) {{
                    notice.style.display = 'block';
                }}
            }}

            // KPI 카드 값 calculation 및 표시
            updateValidationKPIs(isInterimReport);

            // 탭 제목과 라벨 번역 업데이트
            updateValidationTexts();
        }}

        // 단위 번역 함수
        function getUnit(unitKey) {{
            const units = {{
                'people': {{
                    'ko': '명',
                    'en': ' people',
                    'vi': ' người'
                }},
                'days': {{
                    'ko': '일',
                    'en': ' days',
                    'vi': ' ngày'
                }}
            }};

            if (units[unitKey] && units[unitKey][currentLanguage]) {{
                return units[unitKey][currentLanguage];
            }}
            return unitKey; // 번역이 없으면 원본 반환
        }}

        function updateValidationKPIs(isInterimReport) {{
            // existing employeeData에서 directly 값을 가져옴 (새로운 calculation 없음)

            // 단위 fetch
            const peopleUnit = getUnit('people');
            const daysUnit = getUnit('days');

            // 1. total 근무일count - actual attendance data에서 계산 (NOT config값)
            const totalWorkingDays = (window.excelDashboardData && window.excelDashboardData.attendance)
                ? window.excelDashboardData.attendance.total_working_days
                : 18; // Fallback: default값
            document.getElementById('kpiTotalWorkingDays').textContent = totalWorkingDays + daysUnit;

            // 2. 무단결근 현황
            // 3일 이상 무단결근 (인센티브 자동 제외)
            const absent3Plus = employeeData.filter(emp =>
                parseFloat(emp['unapproved_absences'] || emp['Unapproved Absences'] || 0) >= 3
            ).length;
            document.getElementById('kpiAbsentWithoutInform').textContent = absent3Plus + peopleUnit;

            // 3. actual 근무일 0일 (9month 현재 재직자만, TYPE-3 제외)
            const zeroWorkingDays = employeeData.filter(emp => {{
                // TYPE-3 제외 (incentive 대상 아님)
                if (emp['type'] === 'TYPE-3' || emp['ROLE TYPE STD'] === 'TYPE-3') {{
                    return false;
                }}
                const actualDays = parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0);
                // employeeData는 이미 9month 기준 필터링된 401employees
                return actualDays === 0;
            }}).length;
            document.getElementById('kpiZeroWorkingDays').textContent = zeroWorkingDays + peopleUnit;

            // 4. 최소 근무일 미충족 (interim report면 N/A)
            if (isInterimReport) {{
                document.getElementById('kpiMinimumDaysNotMet').textContent = 'N/A';
                document.getElementById('kpiMinimumDaysNotMet').parentElement.style.opacity = '0.5';
            }} else {{
                const minimumDaysNotMet = employeeData.filter(emp => {{
                    // TYPE-3 제외 (incentive 대상 아님)
                    if (emp['type'] === 'TYPE-3' || emp['ROLE TYPE STD'] === 'TYPE-3') {{
                        return false;
                    }}
                    // C4 조건 사용 (Single Source of Truth)
                    return emp['cond_4_minimum_days'] === 'FAIL';
                }}).length;
                document.getElementById('kpiMinimumDaysNotMet').textContent = minimumDaysNotMet + peopleUnit;
            }}

            
            
            // 5. 출근율 88% 미만 (TYPE-3 제외)
            const attendanceBelow88 = employeeData.filter(emp => {{
                // TYPE-3 제외 (incentive 대상 아님)
                if (emp['type'] === 'TYPE-3' || emp['ROLE TYPE STD'] === 'TYPE-3') {{
                    return false;
                }}
                return parseFloat(emp['출근율_Attendance_Rate_Percent'] || emp['Attendance Rate'] || 0) < 88;
            }}).length;
            document.getElementById('kpiAttendanceBelow88').textContent = attendanceBelow88 + peopleUnit;

            // 6. AQL FAIL 보유자 (모든 직원 대상)
            const aqlFailEmployees = employeeData.filter(emp => {{
                // September AQL Failures column 확인 (Excel data에서 directly 가져옴)
                const aqlFailures = parseFloat(emp[window.aqlFailuresColumn] || emp['aql_failures'] || 0);
                return aqlFailures > 0;
            }}).length;
            document.getElementById('kpiAqlFail').textContent = aqlFailEmployees + peopleUnit;

            // 7. 3개월 연속 AQL FAIL (Excel의 Continuous_FAIL column use)
            const consecutiveFail = employeeData.filter(emp => {{
                const continuous_fail = emp['Continuous_FAIL'] || emp['continuous_fail'] || 'NO';
                return continuous_fail === 'YES_3MONTHS';
            }}).length;
            document.getElementById('kpiConsecutiveAqlFail').textContent = consecutiveFail + peopleUnit;

            // 8. 구역 AQL Reject Rate 3% 초과 직원 count (조건 8번만 카운트)
            const highRejectRate = employeeData.filter(emp => {{
                // 조건 8번: 구역 reject rate > 3%만 체크 (조건 7번 제외)
                const cond8 = emp['cond_8_area_reject'] || 'PASS';
                const areaRejectRate = parseFloat(emp['Area_Reject_Rate'] || emp['area_reject_rate'] || 0);
                return cond8 === 'FAIL' || areaRejectRate > 3;
            }}).length;
            document.getElementById('kpiAreaRejectRate').textContent = highRejectRate + peopleUnit;

            // 9. 5PRS 통과율 < 95% (TYPE-1 ASSEMBLY INSPECTOR만)
            const lowPassRate = employeeData.filter(emp => {{
                const isType1 = emp['type'] === 'TYPE-1';
                const position = (emp['position'] || '').toUpperCase();
                const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
                const passRate = parseFloat(emp['pass_rate'] || 100);
                return isType1 && isAssemblyInspector && passRate < 95 && passRate > 0;
            }}).length;
            document.getElementById('kpiLowPassRate').textContent = lowPassRate + peopleUnit;

            // 10. 5PRS 검사량 < 100족 (TYPE-1 ASSEMBLY INSPECTOR만)
            // CRITICAL FIX: 5PRS data file에 actual로 있는 직원만 카운트
            // NaN(data 없음)은 제외, actual 검사량이 있고 < 100인 경우만 포함
            const lowInspectionQty = employeeData.filter(emp => {{
                const isType1 = emp['type'] === 'TYPE-1';
                const positionCode = (emp['position_code'] || '').toUpperCase().trim();
                const isAssemblyInspector = ['A1A', 'A1B', 'A1C'].includes(positionCode);

                // CRITICAL: validation_qty가 actual로 존재하고(NaN 아님) 100 미만인 경우만
                const hasValidationData = emp['validation_qty'] !== null &&
                                         emp['validation_qty'] !== undefined &&
                                         emp['validation_qty'] !== '' &&
                                         !isNaN(parseFloat(emp['validation_qty']));
                const inspectionQty = hasValidationData ? parseFloat(emp['validation_qty']) : 999999;

                return isType1 && isAssemblyInspector && hasValidationData && inspectionQty < 100;
            }}).length;
            document.getElementById('kpiLowInspectionQty').textContent = lowInspectionQty + peopleUnit;
        }}

        function updateValidationTexts() {{
            // 검증 탭 텍스트 번역 업데이트
            const tabTitle = document.getElementById('validationTabTitle');
            if (tabTitle) {{
                tabTitle.textContent = getTranslation('validationTab.title', currentLanguage);
            }}

            const interimText = document.getElementById('interimReportText');
            if (interimText) {{
                interimText.textContent = getTranslation('validationTab.interimNotice', currentLanguage);
            }}

            // KPI 카드 라벨 업데이트
            document.querySelectorAll('.kpi-label').forEach((label, index) => {{
                const kpiKeys = [
                    'totalWorkingDays', 'absentWithoutInform', 'zeroWorkingDays',
                    'minimumDaysNotMet', 'attendanceBelow88', 'aqlFail', 'consecutiveAqlFail',
                    'areaRejectRate', 'lowPassRate', 'lowInspectionQty'
                ];
                if (kpiKeys[index]) {{
                    label.textContent = getTranslation(`validationTab.kpiCards.${{kpiKeys[index]}}.title`, currentLanguage);
                }}
            }});

            // KPI 카드 부제목 업데이트
            document.querySelectorAll('.kpi-subtitle').forEach(subtitle => {{
                const i18nKey = subtitle.getAttribute('data-i18n');
                if (i18nKey) {{
                    subtitle.textContent = getTranslation(i18nKey, currentLanguage);
                }}
            }});

            // KPI 카드 툴팁 업데이트
            document.querySelectorAll('[data-i18n-title]').forEach(element => {{
                const i18nKey = element.getAttribute('data-i18n-title');
                if (i18nKey) {{
                    element.setAttribute('title', getTranslation(i18nKey, currentLanguage));
                }}
            }});

            // KPI 값 업데이트하여 단위 번역 apply
            const isInterimReport = reportType === 'interim';
            updateValidationKPIs(isInterimReport);
        }}

        // 개선된 모달 함count들 추가
        {modal_scripts.replace('__WORKING_DAYS__', str(working_days)).replace('__YEAR__', str(year)).replace('__MONTH_KO__', get_month_translation(month, 'ko')).replace('__MONTH_EN__', get_month_translation(month, 'en')).replace('__MONTH_VI__', get_month_translation(month, 'vi')).replace('__WEEKDAYS_ARRAY__', weekdays_array_js).replace('__DAYS_IN_MONTH__', str(days_in_month))}

        // 검증 모달 표시 함count
        function showValidationModal(conditionType) {{
            console.log('Showing validation modal for:', conditionType);

            // 새로운 개선된 모달 함count 호출
            if (conditionType === 'totalWorkingDays') {{
                showTotalWorkingDaysDetails();
                return;
            }} else if (conditionType === 'zeroWorkingDays') {{
                showZeroWorkingDaysDetails();
                return;
            }} else if (conditionType === 'absentWithoutInform') {{
                showAbsentWithoutInformDetails();
                return;
            }} else if (conditionType === 'minimumDaysNotMet') {{
                showMinimumDaysNotMetDetails();
                return;
            }} else if (conditionType === 'attendanceBelow88') {{
                showAttendanceBelow88Details();
                return;
            }} else if (conditionType === 'aqlFail') {{
                showAqlFailDetails();
                return;
            }} else if (conditionType === 'consecutiveAqlFail') {{
                showConsecutiveAqlFailDetails();
                return;
            }} else if (conditionType === 'areaRejectRate') {{
                showAreaRejectRateDetails();
                return;
            }} else if (conditionType === 'lowPassRate') {{
                showLowPassRateDetails();
                return;
            }} else if (conditionType === 'lowInspectionQty') {{
                showLowInspectionQtyDetails();
                return;
            }}

            // existing 모달 처리 (다른 type의 경우)
            const modalHtml = createValidationModalContent(conditionType);

            // existing 모달 제거
            const existingModal = document.getElementById('validationModal');
            if (existingModal) {{
                existingModal.remove();
            }}

            // 모달 추가
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // 모달 표시
            const modal = document.getElementById('validationModal');
            if (modal) {{
                // existing backdrop 제거
                const existingBackdrop = document.querySelector('.modal-backdrop');
                if (existingBackdrop) {{
                    existingBackdrop.remove();
                }}

                // Bootstrap 5 modal 표시 - 더 안전한 방법
                try {{
                    // existing 모달 인스턴스가 있으면 먼저 처리
                    const existingModal = bootstrap.Modal.getInstance(modal);
                    if (existingModal) {{
                        existingModal.dispose();
                    }}

                    // 새 모달 인스턴스 creation 및 표시
                    const bootstrapModal = new bootstrap.Modal(modal, {{
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    }});
                    bootstrapModal.show();
                }} catch (e) {{
                    console.error('Bootstrap modal error:', e);
                    // Fallback: count동으로 모달 표시
                    modal.classList.add('show');
                    modal.style.display = 'block';
                    modal.setAttribute('aria-modal', 'true');
                    modal.setAttribute('role', 'dialog');
                    document.body.classList.add('modal-open');

                    // count동으로 backdrop 추가
                    const backdrop = document.createElement('div');
                    backdrop.className = 'modal-backdrop fade show';
                    document.body.appendChild(backdrop);
                }}

                // 테이블 정렬 기능 초기화
                initSortableTable('validationModalTable');

                // 검색 필터 초기화
                initTableFilter('validationModalSearch', 'validationModalTable');
            }}
        }}

        function createValidationModalContent(conditionType) {{
            let modalTitle = '';
            let tableHeaders = [];
            let tableData = [];

            // interim report 여부 확인 (data 기간의 last 날 기준)
            const incentiveDataPeriod = document.getElementById('incentiveDataPeriod');
            const dataEndDay = incentiveDataPeriod ? parseInt(incentiveDataPeriod.getAttribute('data-endday')) : 0;
            const isInterimReport = dataEndDay < 20;

            switch(conditionType) {{
                case 'totalWorkingDays':
                    modalTitle = getTranslation('validationTab.modalTitles.totalWorkingDays', currentLanguage);
                    tableHeaders = ['날짜', '요th', 'work 인원count'];
                    // actual로는 thby data가 없으므로 total 근무일count만 표시
                    const totalDays = employeeData[0]?.['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18);
                    tableData = [[
                        `{year}year {get_korean_month(month)}month`,
                        '-',
                        `total ${{totalDays}}th`
                    ]];
                    break;

                case 'absentWithoutInform':
                    modalTitle = getTranslation('validationTab.modalTitles.absentWithoutInform', currentLanguage);

                    // 무단결근 분포 계산
                    const absenceData = employeeData.filter(emp => parseFloat(emp['Unapproved Absences'] || 0) >= 1);
                    const absence1 = absenceData.filter(emp => parseFloat(emp['Unapproved Absences']) === 1).length;
                    const absence2 = absenceData.filter(emp => parseFloat(emp['Unapproved Absences']) === 2).length;
                    const absence3plus = absenceData.filter(emp => parseFloat(emp['Unapproved Absences']) >= 3).length;

                    // 요약 섹션 HTML
                    const summaryHtml = `
                        <div style="margin-bottom: 20px; padding: 15px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 8px;">
                            <div style="display: flex; justify-content: space-around; text-align: center;">
                                <div style="flex: 1;">
                                    <div style="font-size: 24px; font-weight: bold; color: #3498db;">${'${absence1}'}</div>
                                    <div style="font-size: 14px; color: #7f8c8d;">1일</div>
                                </div>
                                <div style="flex: 1;">
                                    <div style="font-size: 24px; font-weight: bold; color: #f39c12;">${'${absence2}'}</div>
                                    <div style="font-size: 14px; color: #7f8c8d;">2일</div>
                                </div>
                                <div style="flex: 1;">
                                    <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">${'${absence3plus}'}</div>
                                    <div style="font-size: 14px; color: #7f8c8d;">3일 이상 (조건 초과)</div>
                                </div>
                            </div>
                        </div>
                    `;

                    tableHeaders = [
                        getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                        getTranslation('validationTab.tableHeaders.name', currentLanguage),
                        getTranslation('validationTab.tableHeaders.position', currentLanguage),
                        getTranslation('validationTab.tableHeaders.ar1Days', currentLanguage),
                        getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveReceived', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveAmount', currentLanguage)
                    ];
                    tableData = absenceData
                        .map(emp => {{
                            const days = parseFloat(emp['Unapproved Absences']);
                            const daysCell = days >= 3 ? `<span style="color: #e74c3c; font-weight: bold;">${'${days}'}</span>` : days;
                            // 인센티브 금액 가져오기 (November_Incentive 또는 Incentive 필드)
                            const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                            const isReceived = incentiveAmount > 0;
                            const receivedCell = isReceived
                                ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                                : `<span style="color: #e74c3c;">❌</span>`;
                            const amountCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">${'${incentiveAmount.toLocaleString()}'} ₫</span>`
                                : `<span style="color: #95a5a6;">0 ₫</span>`;
                            return [
                                emp['Employee No'],
                                emp['Full Name'],
                                emp['FINAL QIP POSITION NAME CODE'],
                                daysCell,
                                emp['attendancy condition 2 - unapproved Absence Day is more than 2 days'] || (days > 2 ? 'FAIL' : 'PASS'),
                                receivedCell,
                                amountCell
                            ];
                        }});

                    // 요약 섹션을 모달에 추가
                    modalContent = summaryHtml;
                    break;

                case 'zeroWorkingDays':
                    modalTitle = getTranslation('validationTab.modalTitles.zeroWorkingDays', currentLanguage);
                    tableHeaders = [
                        getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                        getTranslation('validationTab.tableHeaders.name', currentLanguage),
                        getTranslation('validationTab.tableHeaders.position', currentLanguage),
                        getTranslation('validationTab.tableHeaders.totalDays', currentLanguage),
                        getTranslation('validationTab.tableHeaders.actualDays', currentLanguage),
                        getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveReceived', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveAmount', currentLanguage)
                    ];
                    tableData = employeeData
                        .filter(emp => parseFloat(emp['Actual Working Days'] || 0) === 0)
                        .map(emp => {{
                            const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                            const receivedCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                                : `<span style="color: #e74c3c;">❌</span>`;
                            const amountCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">${'${incentiveAmount.toLocaleString()}'} ₫</span>`
                                : `<span style="color: #95a5a6;">0 ₫</span>`;
                            return [
                                emp['Employee No'],
                                emp['Full Name'],
                                emp['FINAL QIP POSITION NAME CODE'],
                                emp['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18),
                                emp['Actual Working Days'],
                                emp['attendancy condition 1 - acctual working days is zero'] || 'FAIL',
                                receivedCell,
                                amountCell
                            ];
                        }});
                    break;

                case 'minimumDaysNotMet':
                    modalTitle = getTranslation('validationTab.modalTitles.minimumDaysNotMet', currentLanguage);
                    const isInterim = new Date().getDate() < 20;
                    tableHeaders = [
                        getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                        getTranslation('validationTab.tableHeaders.name', currentLanguage),
                        getTranslation('validationTab.tableHeaders.position', currentLanguage),
                        getTranslation('validationTab.tableHeaders.actualDays', currentLanguage),
                        getTranslation('validationTab.tableHeaders.minimumRequired', currentLanguage),
                        getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveReceived', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveAmount', currentLanguage)
                    ];

                    // 중간보고 시에는 조건 4를 apply하지 않음
                    if (isInterim) {{
                        tableData = []; // 중간보고 시 표시 안함
                    }} else {{
                        const totalWorkingDays = parseFloat(employeeData[0]?.['Total Working Days'] || (window.excelDashboardData?.attendance?.total_working_days || 18));
                        const minDays = Math.ceil(totalWorkingDays / 2);
                        tableData = employeeData
                            .filter(emp => parseFloat(emp['Actual Working Days'] || 0) < minDays)
                            .map(emp => {{
                                const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                                const receivedCell = incentiveAmount > 0
                                    ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                                    : `<span style="color: #e74c3c;">❌</span>`;
                                const amountCell = incentiveAmount > 0
                                    ? `<span style="color: #27ae60; font-weight: bold;">${'${incentiveAmount.toLocaleString()}'} ₫</span>`
                                    : `<span style="color: #95a5a6;">0 ₫</span>`;
                                return [
                                    emp['Employee No'],
                                    emp['Full Name'],
                                    emp['FINAL QIP POSITION NAME CODE'],
                                    emp['Actual Working Days'],
                                    minDays,
                                    emp['attendancy condition 4 - minimum working days'] || 'FAIL',
                                    receivedCell,
                                    amountCell
                                ];
                            }});
                    }}
                    break;

                case 'aqlFail':
                    modalTitle = getTranslation('validationTab.modalTitles.aqlFail', currentLanguage);
                    tableHeaders = [
                        getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                        getTranslation('validationTab.tableHeaders.name', currentLanguage),
                        getTranslation('validationTab.tableHeaders.position', currentLanguage),
                        getTranslation('validationTab.tableHeaders.type', currentLanguage),
                        getTranslation('validationTab.tableHeaders.aqlFailures', currentLanguage),
                        getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveReceived', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveAmount', currentLanguage)
                    ];

                    // TYPE-1에서 조건 5가 apply되는 포지션만 필터링
                    const aqlPositions = ['SUPERVISOR', 'A.MANAGER', 'MANAGER', 'S.MANAGER', 'AQL INSPECTOR'];
                    tableData = employeeData
                        .filter(emp => {{
                            const position = (emp['FINAL QIP POSITION NAME CODE'] || '').toUpperCase();
                            const isType1 = emp['ROLE TYPE STD'] === 'TYPE-1';
                            const hasAqlCondition = aqlPositions.some(pos => position.includes(pos));
                            const hasAqlFail = parseFloat(emp[window.aqlFailuresColumn] || 0) > 0;
                            return isType1 && hasAqlCondition && hasAqlFail;
                        }})
                        .map(emp => {{
                            const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                            const receivedCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                                : `<span style="color: #e74c3c;">❌</span>`;
                            const amountCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">${'${incentiveAmount.toLocaleString()}'} ₫</span>`
                                : `<span style="color: #95a5a6;">0 ₫</span>`;
                            return [
                                emp['Employee No'],
                                emp['Full Name'],
                                emp['FINAL QIP POSITION NAME CODE'],
                                emp['ROLE TYPE STD'] || 'TYPE-1',
                                emp[window.aqlFailuresColumn],
                                emp['cond_5_aql_personal_failure'] || 'FAIL',
                                receivedCell,
                                amountCell
                            ];
                        }});
                    break;

                case 'consecutiveAqlFail':
                    // This case is now handled by showConsecutiveAqlFailDetails()
                    // But we still need to handle it here as a fallback
                    modalTitle = getTranslation('validationTab.modalTitles.consecutiveAqlFail', currentLanguage);
                    tableHeaders = ['직원번호', '이름', '직책', '연속 failed 개월'];
                    tableData = employeeData
                        .filter(emp => emp['Consecutive_Fail_Months'] > 0)
                        .map(emp => [
                            emp['Employee No'],
                            emp['Full Name'],
                            emp['QIP POSITION 1ST  NAME'] || '-',
                            emp['Consecutive_Fail_Months'] + '개월'
                        ]);
                    break;

                case 'areaRejectRate':
                    modalTitle = getTranslation('validationTab.modalTitles.areaRejectRate', currentLanguage);
                    tableHeaders = [
                        getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                        getTranslation('validationTab.tableHeaders.name', currentLanguage),
                        getTranslation('validationTab.tableHeaders.area', currentLanguage),
                        getTranslation('validationTab.tableHeaders.rejectRate', currentLanguage),
                        getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                    ];

                    // Area AQL reject rate > 3% 필터링 (구역by AQL Reject 3% 이상)
                    tableData = employeeData
                        .filter(emp => parseFloat(emp['area_reject_rate'] || 0) > 3)
                        .map(emp => [
                            emp['Employee No'],
                            emp['Full Name'],
                            emp['area'] || '-',
                            (parseFloat(emp['area_reject_rate'] || 0).toFixed(2)) + '%',
                            emp['aql condition 7 - team area or reject'] || 'FAIL'
                        ]);
                    break;

                case 'lowPassRate':
                    modalTitle = getTranslation('validationTab.modalTitles.lowPassRate', currentLanguage);
                    tableHeaders = [
                        getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                        getTranslation('validationTab.tableHeaders.name', currentLanguage),
                        getTranslation('validationTab.tableHeaders.position', currentLanguage),
                        getTranslation('validationTab.tableHeaders.type', currentLanguage),
                        getTranslation('validationTab.tableHeaders.passRate', currentLanguage),
                        getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveReceived', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveAmount', currentLanguage)
                    ];

                    // TYPE-1 ASSEMBLY INSPECTOR만 필터링
                    tableData = employeeData
                        .filter(emp => {{
                            const position = (emp['position'] || '').toUpperCase();
                            const isType1 = emp['type'] === 'TYPE-1';
                            const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
                            const lowPassRate = parseFloat(emp['pass_rate'] || 100) < 95;
                            return isType1 && isAssemblyInspector && lowPassRate;
                        }})
                        .map(emp => {{
                            const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                            const receivedCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                                : `<span style="color: #e74c3c;">❌</span>`;
                            const amountCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">${'${incentiveAmount.toLocaleString()}'} ₫</span>`
                                : `<span style="color: #95a5a6;">0 ₫</span>`;
                            return [
                                emp['emp_no'],
                                emp['name'],
                                emp['position'],
                                emp['type'] || 'TYPE-1',
                                (parseFloat(emp['pass_rate'] || 0).toFixed(1)) + '%',
                                emp['cond_9_5prs_pass_rate'] || 'FAIL',
                                receivedCell,
                                amountCell
                            ];
                        }});
                    break;

                case 'lowInspectionQty':
                    modalTitle = getTranslation('validationTab.modalTitles.lowInspectionQty', currentLanguage);
                    tableHeaders = [
                        getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                        getTranslation('validationTab.tableHeaders.name', currentLanguage),
                        getTranslation('validationTab.tableHeaders.position', currentLanguage),
                        getTranslation('validationTab.tableHeaders.type', currentLanguage),
                        getTranslation('validationTab.tableHeaders.inspectionQty', currentLanguage),
                        getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveReceived', currentLanguage),
                        getTranslation('validationTab.tableHeaders.incentiveAmount', currentLanguage)
                    ];

                    // TYPE-1 ASSEMBLY INSPECTOR만 필터링
                    tableData = employeeData
                        .filter(emp => {{
                            const position = (emp['position'] || '').toUpperCase();
                            const isType1 = emp['type'] === 'TYPE-1';
                            const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
                            const lowQty = parseFloat(emp['validation_qty'] || 0) < 100;
                            return isType1 && isAssemblyInspector && lowQty;
                        }})
                        .map(emp => {{
                            const incentiveAmount = parseFloat(emp['November_Incentive'] || emp['Incentive'] || emp['incentive'] || 0);
                            const receivedCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">✅</span>`
                                : `<span style="color: #e74c3c;">❌</span>`;
                            const amountCell = incentiveAmount > 0
                                ? `<span style="color: #27ae60; font-weight: bold;">${'${incentiveAmount.toLocaleString()}'} ₫</span>`
                                : `<span style="color: #95a5a6;">0 ₫</span>`;
                            return [
                                emp['emp_no'],
                                emp['name'],
                                emp['position'],
                                emp['type'] || 'TYPE-1',
                                emp['validation_qty'] || '0',
                                emp['cond_10_5prs_inspection_qty'] || 'FAIL',
                                receivedCell,
                                amountCell
                            ];
                        }});
                    break;

                default:
                    modalTitle = 'Details';
                    tableHeaders = ['No Data'];
                    tableData = [['No data available']];
            }}

            // 모달 HTML creation
            return `
                <div id="validationModal" class="modal" onclick="if(event.대상 === this) closeValidationModal();" style="display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);">
                    <div class="modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 0; border: 1px solid #888; width: 80%; max-width: 1200px; border-radius: 10px;">
                        <div class="modal-header" style="padding: 20px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; border-radius: 10px 10px 0 0;">
                            <span class="close" onclick="closeValidationModal()" style="color: white; float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
                            <h2>${{modalTitle}}</h2>
                        </div>
                        <div class="modal-body" style="padding: 20px;">
                            <div class="search-box" style="margin-bottom: 20px;">
                                <input type="text" id="validationModalSearch" placeholder="${{getTranslation('validationTab.tableHeaders.searchPlaceholder', currentLanguage)}}"
                                       style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                            </div>
                            <div style="overflow-x: auto;">
                                <table id="validationModalTable" class="table" style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background-color: #f2f2f2;">
                                            ${{tableHeaders.map((header, index) => `
                                                <th onclick="sortValidationTable(${{index}})" style="cursor: pointer; padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">
                                                    ${{header}} <span class="sort-icon">↕</span>
                                                </th>
                                            `).join('')}}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${{tableData.map(row => `
                                            <tr>
                                                ${{row.map(cell => `<td style="padding: 10px; border-bottom: 1px solid #ddd;">${{cell || '-'}}</td>`).join('')}}
                                            </tr>
                                        `).join('')}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer" style="padding: 20px; text-align: right; border-top: 1px solid #ddd;">
                            <button onclick="closeValidationModal()" class="btn btn-secondary" style="padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                ${{getTranslation('validationTab.tableHeaders.close', currentLanguage)}}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }}

        function closeValidationModal() {{
            const modal = document.getElementById('validationModal');
            if (modal) {{
                modal.remove();
            }}
        }}

        function initSortableTable(tableId) {{
            // 테이블 정렬 기능 초기화
            const table = document.getElementById(tableId);
            if (!table) return;

            const headers = table.querySelectorAll('th');
            headers.forEach((header, index) => {{
                header.setAttribute('data-sort-direction', 'none');
            }});
        }}

        function sortValidationTable(columnIndex) {{
            const table = document.getElementById('validationModalTable');
            if (!table) return;

            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const header = table.querySelectorAll('th')[columnIndex];

            let sortDirection = header.getAttribute('data-sort-direction') || 'none';
            sortDirection = sortDirection === 'none' || sortDirection === 'desc' ? 'asc' : 'desc';

            rows.sort((a, b) => {{
                const aValue = a.children[columnIndex].textContent.trim();
                const bValue = b.children[columnIndex].textContent.trim();

                // 숫자 비교
                const aNum = parseFloat(aValue);
                const bNum = parseFloat(bValue);

                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
                }}

                // string 비교
                if (sortDirection === 'asc') {{
                    return aValue.localeCompare(bValue);
                }} else {{
                    return bValue.localeCompare(aValue);
                }}
            }});

            // 정렬된 행 다시 추가
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));

            // 정렬 방향 업데이트
            header.setAttribute('data-sort-direction', sortDirection);

            // 정렬 아이콘 업데이트
            table.querySelectorAll('.sort-icon').forEach(icon => icon.textContent = '↕');
            header.querySelector('.sort-icon').textContent = sortDirection === 'asc' ? '↑' : '↓';
        }}

        function initTableFilter(searchInputId, tableId) {{
            const searchInput = document.getElementById(searchInputId);
            const table = document.getElementById(tableId);

            if (!searchInput || !table) return;

            searchInput.addEventListener('keyup', function() {{
                const filter = this.value.toLowerCase();
                const rows = table.querySelector('tbody').querySelectorAll('tr');

                rows.forEach(row => {{
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(filter) ? '' : 'none';
                }});
            }});
        }}

        // ============================================
        // View Mode Selector (Mobile vs PC/Tablet)
        // ============================================
        function initViewMode() {{
            // Read preference from localStorage
            let viewMode = 'desktop';
            try {{
                viewMode = localStorage.getItem('viewMode') || 'desktop';
            }} catch (e) {{
                console.warn('localStorage unavailable, using default view mode');
            }}

            if (viewMode === 'mobile') {{
                document.body.classList.add('mobile-mode');
            }} else {{
                document.body.classList.remove('mobile-mode');
            }}

            window.currentViewMode = viewMode;
            console.log('[ViewMode] Dashboard initialized with:', viewMode);

            // Update view mode toggle buttons if they exist
            updateViewModeButtons(viewMode);
        }}

        function switchViewMode(mode) {{
            try {{
                localStorage.setItem('viewMode', mode);
            }} catch (e) {{
                console.warn('localStorage unavailable');
            }}

            if (mode === 'mobile') {{
                document.body.classList.add('mobile-mode');
            }} else {{
                document.body.classList.remove('mobile-mode');
            }}

            window.currentViewMode = mode;
            updateViewModeButtons(mode);

            // Regenerate card views when switching to mobile mode
            if (mode === 'mobile') {{
                generateEmployeeCardView();
                generateMobileOrgChart();
            }}

            console.log('[ViewMode] Switched to:', mode);
        }}

        function updateViewModeButtons(mode) {{
            document.querySelectorAll('.view-mode-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            const activeBtn = document.querySelector(`.view-mode-btn[data-mode="${{mode}}"]`);
            if (activeBtn) {{
                activeBtn.classList.add('active');
            }}

            // Update header toggle button text
            const toggleText = document.getElementById('viewModeToggleText');
            if (toggleText) {{
                const lang = window.currentLanguage || 'ko';
                const toggleTexts = {{
                    ko: {{ mobile: '📱 모바일 뷰', desktop: '💻 데스크톱 뷰' }},
                    en: {{ mobile: '📱 Mobile View', desktop: '💻 Desktop View' }},
                    vi: {{ mobile: '📱 Xem di động', desktop: '💻 Xem máy tính' }}
                }};
                // Show the opposite mode as button text (what you can switch TO)
                const oppositeMode = mode === 'mobile' ? 'desktop' : 'mobile';
                toggleText.textContent = toggleTexts[lang]?.[oppositeMode] || toggleTexts.ko[oppositeMode];
            }}
        }}

        // Toggle between mobile and desktop view modes
        function toggleViewMode() {{
            const currentMode = window.currentViewMode || 'desktop';
            const newMode = currentMode === 'mobile' ? 'desktop' : 'mobile';
            switchViewMode(newMode);

            // Haptic feedback for mobile devices
            if ('vibrate' in navigator) {{
                navigator.vibrate(30);
            }}
        }}

        // Generate employee card view for mobile mode
        function generateEmployeeCardView() {{
            const cardContainer = document.getElementById('employeeCardView');
            if (!cardContainer || !window.employeeData) {{
                console.log('Card container or employee data not available');
                return;
            }}

            const currentLang = window.currentLanguage || 'ko';
            const translations = {{
                ko: {{ empNo: '사번', position: '직급', incentive: '인센티브', status: '상태', paid: '수령', unpaid: '미수령' }},
                en: {{ empNo: 'Emp No', position: 'Position', incentive: 'Incentive', status: 'Status', paid: 'Paid', unpaid: 'Unpaid' }},
                vi: {{ empNo: 'Mã NV', position: 'Chức vụ', incentive: 'Thưởng', status: 'Trạng thái', paid: 'Đã nhận', unpaid: 'Chưa nhận' }}
            }};
            const t = translations[currentLang] || translations.ko;

            let cardHTML = '';
            const month = '{month}'.toLowerCase();
            const incentiveCol = month + '_incentive';

            window.employeeData.forEach(emp => {{
                const empNo = emp.emp_no || emp['Employee No'] || '';
                const empName = emp.name || emp['Full Name'] || '';
                const empPosition = emp.position || emp['QIP POSITION 1ST NAME'] || '';
                const empType = emp.type || emp['ROLE TYPE STD'] || 'TYPE-2';
                const amount = parseInt(emp[incentiveCol] || emp['November_Incentive'] || 0);
                const isPaid = amount > 0;
                const talentPool = emp.Talent_Pool_Member === 'Y' || emp.Talent_Pool_Member === 'YES';

                cardHTML += `
                    <div class="employee-card ${{isPaid ? '' : 'unpaid'}}" onclick="showEmployeeDetail('${{empNo}}')">
                        <div class="emp-header">
                            <span class="emp-name">
                                ${{empName}}
                                ${{talentPool ? '<span class="badge bg-warning text-dark ms-2" style="font-size: 0.7rem;">TALENT</span>' : ''}}
                            </span>
                            <span class="type-badge type-${{empType.toLowerCase().replace('type-', '')}}">${{empType}}</span>
                        </div>
                        <div class="emp-info-row">
                            <span class="emp-label">${{t.empNo}}</span>
                            <span class="emp-value">${{empNo}}</span>
                        </div>
                        <div class="emp-info-row">
                            <span class="emp-label">${{t.position}}</span>
                            <span class="emp-value">${{empPosition}}</span>
                        </div>
                        <div class="emp-info-row">
                            <span class="emp-label">${{t.incentive}}</span>
                            <span class="emp-value incentive-amount ${{isPaid ? 'paid' : 'unpaid'}}">${{amount.toLocaleString()}} VND</span>
                        </div>
                        <div class="emp-info-row">
                            <span class="emp-label">${{t.status}}</span>
                            <span class="emp-value">${{isPaid ? '✅ ' + t.paid : '❌ ' + t.unpaid}}</span>
                        </div>
                    </div>
                `;
            }});

            cardContainer.innerHTML = cardHTML;
            console.log('[CardView] Generated', window.employeeData.length, 'employee cards');
        }}

        // Generate mobile-friendly organization chart
        function generateMobileOrgChart() {{
            const container = document.getElementById('mobileOrgList');
            if (!container || !window.employeeData) {{
                console.log('Mobile org container or employee data not available');
                return;
            }}

            const month = '{month}'.toLowerCase();
            const incentiveCol = month + '_incentive';

            // Get managers (LINE LEADER and above)
            const managers = window.employeeData.filter(emp => {{
                const position = (emp.position || emp['QIP POSITION 1ST NAME'] || '').toUpperCase();
                return position.includes('LINE LEADER') ||
                       position.includes('GROUP LEADER') ||
                       position.includes('SUPERVISOR') ||
                       position.includes('MANAGER');
            }});

            let html = '';
            managers.forEach(manager => {{
                const mgrNo = manager.emp_no || manager['Employee No'] || '';
                const mgrName = manager.name || manager['Full Name'] || '';
                const mgrPosition = manager.position || manager['QIP POSITION 1ST NAME'] || '';
                const mgrAmount = parseInt(manager[incentiveCol] || manager['November_Incentive'] || 0);
                const isPaid = mgrAmount > 0;

                // Find subordinates
                const subordinates = window.employeeData.filter(emp => {{
                    const bossId = String(emp.boss_id || emp['BOSS ID'] || '');
                    return bossId === String(mgrNo);
                }});

                html += `
                    <div class="org-manager-card ${{isPaid ? 'paid' : 'unpaid'}}" data-manager-id="${{mgrNo}}">
                        <div class="org-card-header" onclick="toggleOrgCard(this.parentElement)">
                            <div class="org-card-info">
                                <div class="org-card-name">${{mgrName}}</div>
                                <div class="org-card-position">${{mgrPosition}}</div>
                            </div>
                            <div class="org-card-incentive ${{isPaid ? 'paid' : 'unpaid'}}">${{mgrAmount.toLocaleString()}} VND</div>
                            <span class="org-card-toggle">▼</span>
                        </div>
                        <div class="org-subordinates">
                `;

                subordinates.forEach(sub => {{
                    const subNo = sub.emp_no || sub['Employee No'] || '';
                    const subName = sub.name || sub['Full Name'] || '';
                    const subAmount = parseInt(sub[incentiveCol] || sub['November_Incentive'] || 0);
                    const subPaid = subAmount > 0;

                    html += `
                            <div class="org-subordinate-item" onclick="showEmployeeDetail('${{subNo}}')">
                                <span class="org-subordinate-name">${{subName}}</span>
                                <span class="org-subordinate-amount ${{subPaid ? 'paid' : 'unpaid'}}">${{subAmount.toLocaleString()}} VND</span>
                            </div>
                    `;
                }});

                html += `
                        </div>
                    </div>
                `;
            }});

            container.innerHTML = html;
            console.log('[MobileOrg] Generated', managers.length, 'manager cards');
        }}

        // Toggle organization card expand/collapse
        function toggleOrgCard(card) {{
            card.classList.toggle('expanded');
        }}

        // 페이지 load 시 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('=== DOMContentLoaded Event Fired ===');
            console.log('Total 직원 in data:', employeeData ? employeeData.length : 'No data');

            // View mode initialization (must be early)
            initViewMode();

            // Bootstrap 툴팁 초기화
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {{
                return new bootstrap.Tooltip(tooltipTriggerEl);
            }});
            console.log('Bootstrap tooltips initialized:', tooltipList.length);

            // D3.js 라이브러리 확인
            if (typeof d3 === 'undefined') {{
                console.error('D3.js library not loaded!');
                alert('D3.js 라이브러리가 load되지 않았습니다. 페이지를 새로고침해주세요.');
                return;
            }}
            console.log('D3.js version:', d3.version);

            // Validation 탭 초기화 - 항상 호출하여 KPI 카드가 비어있지 않도록 함
            setTimeout(() => {{
                console.log('Initializing validation tab KPIs on page load...');
                initValidationTab();
            }}, 100);

            // TYPE 테이블 초기 생성
            setTimeout(() => {{
                console.log('Generating TYPE table on page load...');
                if (typeof generateTypeTable === 'function') {{
                    generateTypeTable();
                }} else {{
                    console.log('generateTypeTable function not available yet');
                }}
            }}, 200);

            // Bootstrap 탭 이벤트 리스너 등록
            // 다양한 선택자 시도
            let orgChartTabButton = document.querySelector('button[data-bs-대상="#orgchart"]');
            if (!orgChartTabButton) {{
                orgChartTabButton = document.querySelector('a[data-bs-대상="#orgchart"]');
            }}
            if (!orgChartTabButton) {{
                orgChartTabButton = document.querySelector('[data-bs-대상="#orgchart"]');
            }}
            if (!orgChartTabButton) {{
                // 네 번째 탭 버튼 directly 선택 (0-indexed이므로 3)
                const allTabButtons = document.querySelectorAll('.nav-link');
                if (allTabButtons.length > 3) {{
                    orgChartTabButton = allTabButtons[3];
                    console.log('네 번째 탭 버튼 use');
                }}
            }}
            if (orgChartTabButton) {{
                console.log('조직도 탭 버튼 발견, 이벤트 리스너 등록');
                orgChartTabButton.addEventListener('shown.bs.tab', function(event) {{
                    console.log('🎯 조직도 탭 활성화됨');
                    drawOrgChart();
                }});

                // 클릭 이벤트도 추가 (shown.bs.tab이 작동 안할 경우 대비)
                orgChartTabButton.addEventListener('click', function() {{
                    setTimeout(() => {{
                        const orgTab = document.getElementById('orgchart');
                        if (orgTab && orgTab.classList.contains('active')) {{
                            console.log('🎯 조직도 탭 클릭 - 차트 그리기');
                            drawOrgChart();
                        }}
                    }}, 100);
                }});
            }}

            // 조직도 탭이 초기에 활성화되어 있는지 확인
            setTimeout(() => {{
                const orgTab = document.getElementById('orgchart');
                console.log('Organization chart tab element:', orgTab);

                if (orgTab) {{
                    if (orgTab.classList.contains('active') && orgTab.classList.contains('show')) {{
                        console.log('Org chart tab is active, drawing initial chart...');
                        drawOrgChart();
                    }} else {{
                        console.log('Org chart tab is not active initially');
                    }}
                }} else {{
                    console.error('Org chart tab element not found!');
                }}
            }}, 500); // data load를 위한 약간의 지연

            // 조직도 검색 기능 이벤트 핸들러
            const orgSearchInput = document.getElementById('orgSearchInput');
            const orgSearchClear = document.getElementById('orgSearchClear');

            if (orgSearchInput) {{
                console.log('Org chart search input found, attaching event listener');
                orgSearchInput.addEventListener('input', function(e) {{
                    const searchTerm = e.target.value.trim();
                    searchInTree(searchTerm);
                }});

                // Enter 키 처리
                orgSearchInput.addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        const searchTerm = e.target.value.trim();
                        searchInTree(searchTerm);
                    }}
                }});
            }}

            if (orgSearchClear) {{
                console.log('Org chart search clear button found, attaching event listener');
                orgSearchClear.addEventListener('click', function() {{
                    if (orgSearchInput) {{
                        orgSearchInput.value = '';
                        searchInTree('');
                    }}
                }});
            }}

            // 하단 Expand All / Collapse All 버튼 이벤트 핸들러
            const expandAllBtns = document.querySelectorAll('button[id="expandAllBtn"]');
            const collapseAllBtns = document.querySelectorAll('button[id="collapseAllBtn"]');

            if (expandAllBtns.length > 0) {{
                console.log(`Found ${{expandAllBtns.length}} Expand All buttons, attaching event listeners`);
                expandAllBtns.forEach(btn => {{
                    btn.addEventListener('click', function() {{
                        expandAll();
                    }});
                }});
            }}

            if (collapseAllBtns.length > 0) {{
                console.log(`Found ${{collapseAllBtns.length}} Collapse All buttons, attaching event listeners`);
                collapseAllBtns.forEach(btn => {{
                    btn.addEventListener('click', function() {{
                        collapseAll();
                    }});
                }});
            }}
        }});

        // 직급 계층 레벨 정의
        function getPositionLevel(position) {{
            const pos = position.toUpperCase();
            // S.Manager가 최상위
            if (pos.includes('S.MANAGER') || pos.includes('SENIOR MANAGER')) return 1;
            // Manager가 S.Manager의 부하
            if (pos.includes('MANAGER') && !pos.includes('A.') && !pos.includes('ASSISTANT')) return 2;
            // A.Manager가 Manager의 부하
            if (pos.includes('A.MANAGER') || pos.includes('ASSISTANT MANAGER')) return 3;
            // Supervisor가 A.Manager의 부하
            if (pos.includes('SUPERVISOR')) return 4;
            // Group Leader
            if (pos.includes('GROUP') && pos.includes('LEADER')) return 5;
            // Line Leader
            if (pos.includes('LINE') && pos.includes('LEADER')) return 6;
            // Inspector
            if (pos.includes('INSPECTOR')) return 7;
            // Others
            return 8;
        }}

        // Breadcrumb 업데이트 함count
        function updateBreadcrumb(current) {{
            const breadcrumb = document.getElementById('orgBreadcrumb');
            if (breadcrumb) {{
                breadcrumb.innerHTML = `
                    <span style="color: #666;">조직도</span>
                    <span style="color: #999;"> › </span>
                    <span style="color: #333; font-weight: bold;">${{current}}</span>
                `;
            }}
        }}

        // 줌 컨트롤 함count들
        let currentZoomBehavior = null;

        function zoomIn() {{
            const svg = d3.select("#orgChartSvg");
            if (currentZoomBehavior && svg.node()) {{
                svg.transition().duration(300).call(
                    currentZoomBehavior.scaleBy, 1.3
                );
            }}
        }}

        function zoomOut() {{
            const svg = d3.select("#orgChartSvg");
            if (currentZoomBehavior && svg.node()) {{
                svg.transition().duration(300).call(
                    currentZoomBehavior.scaleBy, 0.7
                );
            }}
        }}

        function resetZoom() {{
            const svg = d3.select("#orgChartSvg");
            if (currentZoomBehavior && svg.node()) {{
                svg.transition().duration(500).call(
                    currentZoomBehavior.transform,
                    d3.zoomIdentity
                );
            }}
        }}

        // incentive 값을 안전하게 파싱하는 헬퍼 함count
        function parseIncentive(value) {{
            if (!value) return 0;
            // string 형태의 값 처리
            const strValue = String(value).trim();
            // 쉼표 제거 후 파싱
            const parsed = parseInt(strValue.replace(/,/g, ''), 10);
            return isNaN(parsed) ? 0 : parsed;
        }}

        // incentive 수령 여부 확인 함count
        function hasIncentive(data) {{
            const amount = parseIncentive(data.incentive || data['{month.lower()}_incentive'] || 0);
            return amount > 0;
        }}

        // 직급별 색상 정의
        function getPositionColor(position) {{
            if (!position) return '#8c564b'; // Others (brown)
            const pos = position.toUpperCase();

            if (pos.includes('MANAGER') && !pos.includes('A.') && !pos.includes('ASSISTANT')) {{
                return '#1f77b4'; // Manager (blue)
            }}
            if (pos.includes('SUPERVISOR')) {{
                return '#2ca02c'; // Supervisor (green)
            }}
            if (pos.includes('GROUP') && pos.includes('LEADER')) {{
                return '#ff7f0e'; // Group Leader (orange)
            }}
            if (pos.includes('LINE') && pos.includes('LEADER')) {{
                return '#d62728'; // Line Leader (red)
            }}
            if (pos.includes('INSPECTOR')) {{
                return '#9467bd'; // Inspector (purple)
            }}
            return '#8c564b'; // Others (brown)
        }}

        // Building별 QC 요약 카드 생성 (SUPERVISOR, A.MANAGER 요청 - 2025-12-16)
        function buildBuildingSummaryCards() {{
            const container = document.getElementById('buildingSummaryCards');
            if (!container || !employeeData) return;

            // Building별 통계 계산
            const buildingStats = {{}};
            const buildings = ['A', 'B', 'B3', 'C', 'D'];

            buildings.forEach(b => {{
                buildingStats[b] = {{ total: 0, paid: 0, totalAmount: 0 }};
            }});

            employeeData.forEach(emp => {{
                const building = (emp.BUILDING || emp.building || '').toUpperCase();
                if (buildingStats[building]) {{
                    buildingStats[building].total++;
                    const amount = parseInt(emp['{month.lower()}_incentive'] || 0);
                    if (amount > 0) {{
                        buildingStats[building].paid++;
                        buildingStats[building].totalAmount += amount;
                    }}
                }}
            }});

            // 카드 HTML 생성
            let cardsHTML = '';
            const colors = {{ 'A': '#ef4444', 'B': '#3b82f6', 'B3': '#8b5cf6', 'C': '#10b981', 'D': '#f59e0b' }};

            buildings.forEach(b => {{
                const stats = buildingStats[b];
                if (stats.total > 0) {{
                    const rate = ((stats.paid / stats.total) * 100).toFixed(1);
                    cardsHTML += `
                        <div class="col-md-2 col-sm-4 col-6 mb-2">
                            <div class="card h-100" style="border-left: 4px solid ${{colors[b]}}; cursor: pointer;"
                                 onclick="document.getElementById('orgBuildingFilter').value='${{b}}'; filterOrgChartByBuilding();">
                                <div class="card-body py-2 px-3">
                                    <h6 class="card-title mb-1" style="color: ${{colors[b]}};">Building ${{b}}</h6>
                                    <div class="small">
                                        <div><strong>${{stats.total}}</strong> <span id="bldgCardTotal_${{b}}">${{getTranslation('buildingSummary.employees')}}</span></div>
                                        <div><strong>${{stats.paid}}</strong> <span id="bldgCardPaid_${{b}}">${{getTranslation('buildingSummary.recipients')}}</span> (${{rate}}%)</div>
                                        <div style="color: ${{colors[b]}}; font-weight: 600;">₫${{stats.totalAmount.toLocaleString()}}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }}
            }});

            container.innerHTML = cardsHTML;
        }}

        // 새로운 접이식 조직도 그리기 함count
        function drawOrgChart() {{
            console.log('Drawing new collapsible org chart...');
            buildBuildingSummaryCards();  // Building 요약 카드 업데이트
            drawCollapsibleOrgChart();
        }}

        function drawCollapsibleOrgChart() {{
            console.log('🏗️ === 조직도 그리기 start ===');
            console.log('   Employee Data count:', employeeData ? employeeData.length : 0);
            console.log('   Dashboard Month:', dashboardMonth);

            const container = document.getElementById('orgTreeContent');
            if (!container) {{
                console.error('orgTreeContent container not found!');
                return;
            }}

            // 로딩 표시
            container.innerHTML = `<div class="org-loading"><div class="org-loading-spinner"></div><p>${{getTranslation('orgChart.loadingMessage')}}</p></div>`;

            // 계층 구조 data creation
            const hierarchyData = buildHierarchyData();
            if (!hierarchyData || hierarchyData.length === 0) {{
                container.innerHTML = `<div class="alert alert-warning">${{getTranslation('orgChart.noDataMessage')}}</div>`;
                return;
            }}

            // HTML 트리 creation
            const treeHTML = buildTreeHTML(hierarchyData);
            container.innerHTML = treeHTML;

            // 이벤트 리스너 추가
            attachTreeEventListeners();

            // 통계 업데이트

            // UI 텍스트 업데이트
            updateOrgChartUIText();
        }}

        // 계층 구조 data 빌드
        function buildHierarchyData() {{
            console.log('Building TYPE-1 manager hierarchy data...');

            if (!employeeData || employeeData.length === 0) {{
                console.error('No employee data available');
                return null;
            }}

            // Building 필터 값 가져오기 (SUPERVISOR, A.MANAGER 요청 기능 - 2025-12-16)
            const buildingFilterElement = document.getElementById('orgBuildingFilter');
            const selectedBuilding = buildingFilterElement ? buildingFilterElement.value : 'all';
            console.log('Building filter selected:', selectedBuilding);

            // Special calculation positions 확인 함count
            function hasSpecialCalculation(position) {{
                if (!position || !positionMatrix) return false;
                const pos = position.toUpperCase();

                // TYPE-1 positions 확인
                const type1Positions = positionMatrix.position_matrix?.['TYPE-1'] || {{}};

                // 각 직급 체크
                for (const [key, config] of Object.entries(type1Positions)) {{
                    if (key === 'default') continue;

                    // patterns 매칭 확인
                    if (config.patterns) {{
                        for (const pattern of config.patterns) {{
                            if (pos.includes(pattern.toUpperCase())) {{
                                // special_calculation 필드 확인
                                if (config.special_calculation) {{
                                    return true;
                                }}
                            }}
                        }}
                    }}
                }}

                return false;
            }}

            // TYPE-1 직원 중 LINE LEADER 이상만 포함 (관리자 계층 구조)
            const type1Employees = employeeData.filter(emp => {{
                // Building 필터 적용 (SUPERVISOR, A.MANAGER 요청 - 2025-12-16)
                if (selectedBuilding !== 'all') {{
                    const empBuilding = (emp.BUILDING || emp.building || '').toUpperCase();
                    if (empBuilding !== selectedBuilding.toUpperCase()) {{
                        return false;
                    }}
                }}

                // TYPE-1이 아닌 경우 제외
                if (emp.type !== 'TYPE-1') {{
                    return false;
                }}

                // Special calculation positions 제외 (AQL INSPECTOR, AUDIT & TRAINING, MODEL MASTER)
                if (hasSpecialCalculation(emp.position)) {{
                    console.log(`Excluding special calculation position: ${{emp.position}} - ${{emp.name}}`);
                    return false;
                }}

                // LINE LEADER 이상의 관리자 포지션만 포함
                const position = (emp.position || '').toUpperCase();
                const isManagerLevel = position.includes('MANAGER') ||
                                      position.includes('SUPERVISOR') ||
                                      position.includes('GROUP LEADER') ||
                                      position.includes('LINE LEADER');

                if (!isManagerLevel) {{
                    console.log(`Excluding non-manager position: ${{emp.position}} - ${{emp.name}}`);
                    return false;
                }}

                return true;
            }});

            console.log(`TYPE-1 직원 for hierarchy: ${{type1Employees.length}} (excluded ${{employeeData.length - type1Employees.length}})`);

            // 직원 ID로 매핑 - 모든 TYPE-1 직원 포함
            const employeeMap = {{}};
            const rootNodes = [];

            // 모든 TYPE-1 직원을 맵에 저장 (계층 구조 형성을 위해)
            type1Employees.forEach(emp => {{
                // incentive calculation 방법 determination
                let calculationMethod = '';
                const pos = (emp.position || '').toUpperCase();

                if (pos.includes('LINE LEADER')) {{
                    calculationMethod = getTranslation('orgChart.calculationFormulas.lineLeader');
                }} else if (pos.includes('GROUP LEADER')) {{
                    calculationMethod = getTranslation('orgChart.calculationFormulas.groupLeader');
                }} else if (pos.includes('SUPERVISOR')) {{
                    calculationMethod = getTranslation('orgChart.calculationFormulas.supervisor');
                }} else if (pos.includes('A.MANAGER') || pos.includes('ASSISTANT')) {{
                    calculationMethod = getTranslation('orgChart.calculationFormulas.assistantManager');
                }} else if (pos.includes('MANAGER')) {{
                    calculationMethod = getTranslation('orgChart.calculationFormulas.manager');
                }}

                employeeMap[emp.emp_no] = {{
                    id: emp.emp_no,
                    name: emp.name,
                    position: emp.position,
                    type: emp.type,
                    incentive: emp['{month.lower()}_incentive'] || 0,
                    boss_id: emp.boss_id,
                    calculationMethod: calculationMethod,
                    children: []
                }};
            }});

            // 부모-자식 관계 설정 - employeeMap의 모든 직원에 대해 처리
            Object.values(employeeMap).forEach(node => {{
                if (node.boss_id && node.boss_id !== '' && node.boss_id !== 'nan' && node.boss_id !== '0') {{
                    const boss = employeeMap[node.boss_id];
                    if (boss) {{
                        boss.children.push(node);
                    }} else {{
                        // 보스가 employeeMap에 없으면 루트 노드로 추가
                        rootNodes.push(node);
                    }}
                }} else {{
                    // 보스 ID가 없으면 루트 노드
                    rootNodes.push(node);
                }}
            }});

            console.log(`Hierarchy built: ${{rootNodes.length}} root nodes`);
            return rootNodes;
        }}

        // HTML 트리 creation
        function buildTreeHTML(nodes, depth = 0) {{
            if (!nodes || nodes.length === 0) return '';

            let html = '<ul>';

            nodes.forEach(node => {{
                const hasChildren = node.children && node.children.length > 0;
                const liClass = hasChildren ? 'expanded' : 'no-children';
                const nodeClass = getNodeClass(node.position);
                const incentiveClass = node.incentive > 0 ? 'has-incentive' : 'no-incentive';
                const incentiveDot = node.incentive > 0 ? 'received' : 'not-received';

                html += `<li class="${{liClass}}">`;
                html += `<div class="org-node ${{nodeClass}} ${{incentiveClass}}">`;

                // incentive 표시 점
                html += `<div class="node-incentive ${{incentiveDot}}"></div>`;

                // 노드 내용
                html += `<div class="node-position">${{node.position || 'N/A'}}</div>`;
                html += `<div class="node-name">${{node.name}}</div>`;
                html += `<div class="node-id">ID: ${{node.id}}</div>`;

                // incentive 정보 (모든 경우 클릭 가능)
                const incentiveAmount = Number(node.incentive) || 0;
                const incentiveFormatted = incentiveAmount.toLocaleString('ko-KR');
                html += `<div class="node-incentive-info" data-node-id="${{node.id}}">`;
                html += `<div style="display: flex; align-items: center;">`;
                if (incentiveAmount > 0) {{
                    html += `<span class="incentive-amount">₫${{incentiveFormatted}}</span>`;
                }} else {{
                    html += `<span class="incentive-amount" style="color: #dc3545;">₫0</span>`;
                }}
                html += `</div>`;
                html += `<span class="incentive-detail-btn"
                            data-node-id="${{node.id}}"
                            title="클릭하여 상세 정보 보기"
                            role="button"
                            tabindex="0"
                            data-bs-toggle="tooltip"
                            data-bs-placement="top">ℹ️</span>`;
                html += '</div>';

                // LINE LEADER의 경우 부하직원 표시
                if (node.position && node.position.toUpperCase().includes('LINE LEADER')) {{
                    // 부하직원 찾기 (incentive calculation에 영향을 미치는 TYPE-1 부하만)
                    // CRITICAL FIX (2025-12-05): String() 변환으로 타입 불일치 방지
                    const subordinates = employeeData.filter(emp =>
                        String(emp.boss_id || '') === String(node.id || '') &&
                        emp.type === 'TYPE-1'
                    );

                    const receivingCount = subordinates.filter(sub => {{
                        const incentive = sub['{month.lower()}_incentive'] || 0;
                        return Number(incentive) > 0;
                    }}).length;

                    if (subordinates.length > 0) {{
                        html += `<div class="subordinate-info">`;
                        html += `<span class="subordinate-label">incentive calculation based:</span>`;
                        html += `<span class="subordinate-count" data-i18n-subordinates="${{receivingCount}}/${{subordinates.length}}"></span>`;
                        html += '</div>';
                    }}
                }}

                // 자식이 있으면 접기/펼치기 버튼과 자식 count 표시
                if (hasChildren) {{
                    html += `<span class="child-count">${{node.children.length}}</span>`;
                    html += `<span class="toggle-btn"></span>`;
                }}

                html += '</div>';

                // 재귀적으로 자식 노드 추가
                if (hasChildren) {{
                    html += buildTreeHTML(node.children, depth + 1);
                }}

                html += '</li>';
            }});

            html += '</ul>';
            return html;
        }}

        // 노드 클래스 determination
        function getNodeClass(position) {{
            if (!position) return 'default';
            const pos = position.toUpperCase();

            if (pos.includes('MANAGER') && !pos.includes('ASSISTANT')) return 'manager';
            if (pos.includes('SUPERVISOR')) return 'supervisor';
            if (pos.includes('GROUP LEADER')) return 'group-leader';
            if (pos.includes('LINE LEADER')) return 'line-leader';
            if (pos.includes('INSPECTOR')) return 'inspector';
            return 'default';
        }}

        // 트리 이벤트 리스너
        function attachTreeEventListeners() {{
            console.log('📎 attachTreeEventListeners 호출됨');

            // 정보 버튼 클릭 이벤트 - 이벤트 위임 방식으로 변경
            const treeContent = document.getElementById('orgTreeContent');
            if (treeContent) {{
                // existing 리스너 제거 (중복 방지)
                if (window.incentiveButtonHandler) {{
                    treeContent.removeEventListener('click', window.incentiveButtonHandler, true);
                }}

                // 핸들러 함count를 전역에 저장하여 나중에 제거 가능
                window.incentiveButtonHandler = function(e) {{
                    console.log('🖱️ 클릭 이벤트 발생:', e.target.className);

                    // 정보 버튼이 클릭된 경우
                    if (e.target && e.target.classList && e.target.classList.contains('incentive-detail-btn')) {{
                        console.log('ℹ️ 정보 버튼 클릭됨 (이벤트 위임)');
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();

                        const nodeId = e.target.getAttribute('data-node-id');
                        console.log('📌 노드 ID:', nodeId);
                        console.log('📌 showIncentiveModal 함수 존재:', typeof window.showIncentiveModal);

                        if (window.showIncentiveModal && nodeId) {{
                            console.log('🎯 관리자 계산 모달 호출 시도:', nodeId);
                            try {{
                                // 조직도 탭에서는 관리자 계산 모달 표시 (부하직원 계산 상세)
                                window.showIncentiveModal(String(nodeId));
                                console.log('✅ 관리자 계산 모달 호출 성공');
                            }} catch(error) {{
                                console.error('❌ 관리자 계산 모달 호출 중 오류:', error);
                            }}
                        }} else {{
                            console.error('❌ showIncentiveModal 함수가 없거나 노드 ID가 없음');
                            console.error('   - showIncentiveModal:', typeof window.showIncentiveModal);
                            console.error('   - nodeId:', nodeId);
                        }}
                        return false;
                    }}
                }};

                // 이벤트 위임으로 처리 (동적으로 creation되는 버튼도 처리 가능)
                treeContent.addEventListener('click', window.incentiveButtonHandler, true); // capture 단계에서 처리
                console.log('✅ incentive 버튼 이벤트 리스너 등록 completed');
            }} else {{
                console.error('❌ orgTreeContent 요소를 find count 없음');
            }}

            // 토글 버튼 클릭 이벤트
            document.querySelectorAll('.toggle-btn').forEach(btn => {{
                btn.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    const li = this.closest('li');
                    if (li.classList.contains('collapsed')) {{
                        li.classList.remove('collapsed');
                        li.classList.add('expanded');
                    }} else {{
                        li.classList.remove('expanded');
                        li.classList.add('collapsed');
                    }}
                }});
            }});

            // incentive 정보 클릭 이벤트 (이벤트 위임 방식)
            console.log('📌 incentive 클릭 이벤트 리스너 등록 중...');
            const orgContainer = document.getElementById('orgTreeContent');
            if (orgContainer) {{
                // existing 리스너 제거 (중복 방지)
                orgContainer.removeEventListener('click', handleIncentiveClick);
                // 새 리스너 추가
                orgContainer.addEventListener('click', handleIncentiveClick);
                console.log('✅ 이벤트 위임 리스너 등록 completed');
            }}

            // incentive 클릭 핸들러 함수
            function handleIncentiveClick(e) {{
                const incentiveInfo = e.target.closest('.node-incentive-info');
                if (incentiveInfo) {{
                    e.preventDefault();
                    e.stopPropagation();
                    const nodeId = incentiveInfo.getAttribute('data-node-id');
                    console.log('💰 incentive 클릭 감지 - Node ID:', nodeId);

                    if (window.showIncentiveModal) {{
                        // 조직도 탭에서는 관리자 계산 모달 표시 (부하직원 계산 상세)
                        window.showIncentiveModal(String(nodeId));
                    }} else {{
                        console.error('❌ showIncentiveModal 함수가 not found');
                    }}
                }}
            }}

            // 조직도가 그려진 후 툴팁 재초기화
            setTimeout(() => {{
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.forEach(function (tooltipTriggerEl) {{
                    new bootstrap.Tooltip(tooltipTriggerEl);
                }});
                console.log('✅ 조직도 툴팁 초기화 completed:', tooltipTriggerList.length, '개');
            }}, 500);

            // 검색 기능
            const searchInput = document.getElementById('orgSearchInput');
            const searchClear = document.getElementById('orgSearchClear');

            if (searchInput) {{
                searchInput.addEventListener('input', function() {{
                    const searchTerm = this.value.toLowerCase();
                    searchInTree(searchTerm);
                }});
            }}

            if (searchClear) {{
                searchClear.addEventListener('click', function() {{
                    searchInput.value = '';
                    searchInTree('');
                }});
            }}

            // 모두 펼치기/접기 버튼
            const expandAllBtn = document.getElementById('expandAllBtn');
            const collapseAllBtn = document.getElementById('collapseAllBtn');

            if (expandAllBtn) {{
                expandAllBtn.addEventListener('click', function() {{
                    document.querySelectorAll('.collapsible-tree li').forEach(li => {{
                        if (li.querySelector('.toggle-btn')) {{
                            li.classList.remove('collapsed');
                            li.classList.add('expanded');
                        }}
                    }});
                }});
            }}

            if (collapseAllBtn) {{
                collapseAllBtn.addEventListener('click', function() {{
                    document.querySelectorAll('.collapsible-tree li').forEach(li => {{
                        if (li.querySelector('.toggle-btn')) {{
                            li.classList.remove('expanded');
                            li.classList.add('collapsed');
                        }}
                    }});
                }});
            }}

            // 노드 클릭 이벤트 (incentive 정보 클릭 제외)
            document.querySelectorAll('.org-node').forEach(node => {{
                node.addEventListener('click', function(e) {{
                    // incentive 정보를 클릭한 경우는 제외
                    if (e.target.closest('.node-incentive-info')) {{
                        console.log('🚫 incentive 클릭이므로 expand/collapse 무시');
                        return;
                    }}
                    const toggleBtn = this.querySelector('.toggle-btn');
                    if (toggleBtn) {{
                        console.log('📂 노드 expand/collapse 토글');
                        toggleBtn.click();
                    }}
                }});
            }});
        }}

        // total 펼치기
        function expandAll() {{
            document.querySelectorAll('.collapsible-tree li.collapsed').forEach(li => {{
                li.classList.remove('collapsed');
                li.classList.add('expanded');
            }});
        }}

        // total 접기
        function collapseAll() {{
            document.querySelectorAll('.collapsible-tree li.expanded').forEach(li => {{
                if (li.querySelector('ul')) {{ // 자식이 있는 경우만
                    li.classList.remove('expanded');
                    li.classList.add('collapsed');
                }}
            }});
        }}

        // 검색 기능
        function searchInTree(searchTerm) {{
            const nodes = document.querySelectorAll('.org-node');
            const allLis = document.querySelectorAll('.collapsible-tree li');

            if (!searchTerm) {{
                // 검색어가 없으면 모두 표시
                nodes.forEach(node => {{
                    node.classList.remove('search-hidden');
                    node.classList.remove('search-highlight');
                }});
                return;
            }}

            // 모든 노드 숨기기
            nodes.forEach(node => {{
                node.classList.add('search-hidden');
                node.classList.remove('search-highlight');
            }});

            // 검색어와 th치하는 노드 찾기
            nodes.forEach(node => {{
                const name = node.querySelector('.node-name')?.textContent.toLowerCase() || '';
                const id = node.querySelector('.node-id')?.textContent.toLowerCase() || '';
                const position = node.querySelector('.node-position')?.textContent.toLowerCase() || '';

                if (name.includes(searchTerm) || id.includes(searchTerm) || position.includes(searchTerm)) {{
                    node.classList.remove('search-hidden');
                    node.classList.add('search-highlight');

                    // 부모 노드들도 표시
                    let parent = node.closest('li');
                    while (parent) {{
                        const parentNode = parent.querySelector(':scope > .org-node');
                        if (parentNode) {{
                            parentNode.classList.remove('search-hidden');
                        }}
                        // 부모 li를 펼치기
                        if (parent.classList.contains('collapsed')) {{
                            parent.classList.remove('collapsed');
                            parent.classList.add('expanded');
                        }}
                        parent = parent.parentElement?.closest('li');
                    }}
                }}
            }});
        }}

        // 모달 테스트 함count (전역 스코프)
        // 모달 강제 닫기 함count (전역 스코프)
        window.forceCloseModal = function() {{
            console.log('🚨 모달 강제 닫기 실행');
            const modal = document.getElementById('incentiveModal');
            if (modal) {{
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {{
                    modalInstance.hide();
                    modalInstance.dispose();
                }}
                modal.remove();
            }}
            // 백드롭과 body 상태 정리
            document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        }};

        // 팀 내 모든 LINE LEADER 찾기 (재귀적) - Excel logic과 동th
        function findTeamLineLeaders(managerId, depth = 0, visited = null) {{
            if (depth > 5) return []; // 무한 루프 방지

            if (!visited) {{
                visited = new Set();
            }}

            // managerId를 string로 통th
            managerId = String(managerId || '');
            if (!managerId || managerId === 'nan' || managerId === '0' || managerId === '') {{
                return [];
            }}

            if (visited.has(managerId)) {{
                return [];
            }}
            visited.add(managerId);

            let lineLeaders = [];

            // boss_id를 string로 비교하여 directly 부하들 찾기
            const directSubordinates = employeeData.filter(emp => {{
                const bossId = String(emp.boss_id || '');
                return bossId === managerId && bossId !== '';
            }});

            directSubordinates.forEach(sub => {{
                const position = (sub.position || '').toUpperCase();

                // 퇴사자 제외: stop_date가 있으면 평균 계산에서 제외
                // 2025-12-01 추가: 퇴사자는 인센티브가 0이므로 평균 계산에서 제외해야 공정함
                const stopDate = sub.stop_date || '';
                if (stopDate && stopDate.trim() !== '') {{
                    // 퇴사자는 건너뜀
                    // 하지만 재귀 탐색은 계속 (퇴사자 아래에 근무중인 부하가 있을 수 있음)
                    const subLineLeaders = findTeamLineLeaders(String(sub.emp_no || ''), depth + 1, visited);
                    lineLeaders = lineLeaders.concat(subLineLeaders);
                    return; // continue to next iteration
                }}

                // TYPE-1 LINE LEADER인 경우 추가 (퇴사자가 아닌 경우만)
                if (sub.type === 'TYPE-1' && position.includes('LINE') && position.includes('LEADER')) {{
                    lineLeaders.push(sub);
                }}

                // 재귀적으로 부하의 부하 탐색 (emp_no를 string로 conversion)
                const subLineLeaders = findTeamLineLeaders(String(sub.emp_no || ''), depth + 1, visited);
                lineLeaders = lineLeaders.concat(subLineLeaders);
            }});

            return lineLeaders;
        }}

        // incentive 미지급 사유 분석 함count
        function getIncentiveFailureReasons(employee) {{
            const reasons = [];
            const position = (employee.position || '').toUpperCase();

            // 10개 조건 상태 체크 (cond_1 through cond_10)
            const conditionFields = [
                'cond_1_attendance_rate',
                'cond_2_unapproved_absence',
                'cond_3_actual_working_days',
                'cond_4_minimum_days',
                'cond_5_aql_personal_failure',
                'cond_6_aql_continuous',
                'cond_7_aql_team_area',
                'cond_8_area_reject',
                'cond_9_5prs_pass_rate',
                'cond_10_5prs_inspection_qty'
            ];

            let applicableCount = 0;
            let passedCount = 0;
            const failedConditions = [];

            // 각 조건 체크
            conditionFields.forEach((field, index) => {{
                const status = employee[field];
                const condNum = index + 1;

                // N/A 또는 NOT_APPLICABLE이 아닌 경우만 적용 조건으로 카운트
                if (status && status !== 'N/A' && status !== 'NOT_APPLICABLE') {{
                    applicableCount++;

                    if (status === 'PASS') {{
                        passedCount++;
                    }} else if (status === 'FAIL') {{
                        // 실패한 조건 기록
                        const condKey = field.replace('cond_', 'cond').replace(/_/g, '_');
                        failedConditions.push({{
                            num: condNum,
                            key: condKey,
                            name: getTranslation(`orgChart.modal.nonPaymentReasons.${{condKey}}`, currentLanguage)
                        }});
                    }}
                }}
            }});

            // 조건 미충족이 있는 경우
            if (applicableCount > 0 && passedCount < applicableCount) {{
                const passRate = ((passedCount / applicableCount) * 100).toFixed(1);
                const summaryText = getTranslation('orgChart.modal.nonPaymentReasons.conditionPassRateInsufficient', currentLanguage);
                reasons.push(summaryText
                    .replace('{{{{passed}}}}', passedCount)
                    .replace('{{{{applicable}}}}', applicableCount)
                    .replace('{{{{passRate}}}}', passRate));

                // 실패한 조건 나열
                if (failedConditions.length > 0) {{
                    const labelText = getTranslation('orgChart.modal.nonPaymentReasons.failedConditionsLabel', currentLanguage);
                    const condList = failedConditions.map(c => `• ${{c.name}}`).join('<br>');
                    reasons.push(`<strong>${{labelText}}:</strong><br>${{condList}}`);
                }}
            }}

            // 사유가 없는 경우 기본 메시지
            if (reasons.length === 0) {{
                if (employee['{month.lower()}_incentive'] === 0) {{
                    reasons.push(getTranslation('orgChart.modal.nonPaymentReasons.conditionInfoUnavailable', currentLanguage));
                }}
            }}

            return reasons;
        }}

        // Position Configuration Object
        const POSITION_CONFIG = {{
            'LINE LEADER': {{
                multiplier: 0.12,
                subordinateType: 'ASSEMBLY INSPECTOR',
                formulaKey: 'orgChart.modal.formulas.lineLeader',
                useGrouping: false,
                useAlternatingColors: false,
                subordinateLabel: 'assemblyInspectorList',
                countLabel: 'inspectorCount',
                findSubordinates: (nodeId) => {{
                    // CRITICAL FIX (2025-12-05): String() 변환으로 타입 불일치 방지
                    // emp.boss_id (number)와 nodeId (string) 비교 시 === 실패 방지
                    const nodeIdStr = String(nodeId || '');
                    return employeeData.filter(emp =>
                        String(emp.boss_id || '') === nodeIdStr &&
                        emp.position &&
                        emp.position.toUpperCase().includes('ASSEMBLY INSPECTOR')
                    );
                }}
            }},
            'GROUP LEADER': {{
                multiplier: 2,
                subordinateType: 'LINE LEADER',
                formulaKey: 'orgChart.modal.formulas.groupLeader',
                useGrouping: false,
                useAlternatingColors: false,
                subordinateLabel: 'lineLeaderList',
                countLabel: 'lineLeaderCount',
                findSubordinates: (nodeId) => findTeamLineLeaders(nodeId)
            }},
            'SUPERVISOR': {{
                multiplier: 2.5,
                subordinateType: 'LINE LEADER',
                formulaKey: 'orgChart.modal.formulas.supervisor',
                useGrouping: true,
                useAlternatingColors: true,
                subordinateLabel: 'lineLeaderList',
                countLabel: 'lineLeaderCount',
                findSubordinates: (nodeId) => findTeamLineLeaders(nodeId)
            }},
            'A.MANAGER': {{
                multiplier: 3,
                subordinateType: 'LINE LEADER',
                formulaKey: 'orgChart.modal.formulas.amanager',
                useGrouping: true,
                useAlternatingColors: false,
                subordinateLabel: 'lineLeaderList',
                countLabel: 'lineLeaderCount',
                findSubordinates: (nodeId) => findTeamLineLeaders(nodeId)
            }},
            'MANAGER': {{
                multiplier: 3.5,
                subordinateType: 'LINE LEADER',
                formulaKey: 'orgChart.modal.formulas.manager',
                useGrouping: true,
                useAlternatingColors: true,
                subordinateLabel: 'lineLeaderList',
                countLabel: 'lineLeaderCount',
                findSubordinates: (nodeId) => findTeamLineLeaders(nodeId)
            }}
        }};

        // Helper: Get position configuration
        function getPositionConfig(position) {{
            const posUpper = (position || '').toUpperCase();

            // Exact match priority
            if (posUpper.includes('LINE LEADER')) return POSITION_CONFIG['LINE LEADER'];
            if (posUpper.includes('GROUP LEADER')) return POSITION_CONFIG['GROUP LEADER'];
            if (posUpper.includes('SUPERVISOR')) return POSITION_CONFIG['SUPERVISOR'];
            if (posUpper.includes('A.MANAGER') || posUpper.includes('ASSISTANT')) return POSITION_CONFIG['A.MANAGER'];
            if (posUpper.includes('MANAGER') && !posUpper.includes('A.MANAGER') && !posUpper.includes('ASSISTANT')) return POSITION_CONFIG['MANAGER'];

            return null;
        }}

        // Helper: Calculate expected incentive
        function calculateExpectedIncentive(subordinates, config) {{
            const receivingSubordinates = subordinates.filter(sub =>
                Number(sub['{month.lower()}_incentive'] || 0) > 0
            );

            if (config.multiplier === 0.12) {{
                // LINE LEADER: sum × 12% × receiving ratio
                const totalIncentive = subordinates.reduce((sum, sub) =>
                    sum + Number(sub['{month.lower()}_incentive'] || 0), 0
                );
                const receivingRatio = subordinates.length > 0 ?
                    receivingSubordinates.length / subordinates.length : 0;
                return {{
                    expected: Math.round(totalIncentive * 0.12 * receivingRatio),
                    metrics: {{
                        total: totalIncentive,
                        receiving: receivingSubordinates.length,
                        count: subordinates.length,
                        receivingRatio: receivingRatio,
                        average: 0
                    }}
                }};
            }} else {{
                // Others: average × multiplier (수령자만 평균 - 0 제외, 2025-12-04 수정)
                // 사용자 확인: "인센티브를 받는 사람만으로 계산하는게 맞다"
                const receivingIncentive = receivingSubordinates.reduce((sum, sub) =>
                    sum + Number(sub['{month.lower()}_incentive'] || 0), 0
                );
                const avgIncentive = receivingSubordinates.length > 0 ?
                    receivingIncentive / receivingSubordinates.length : 0;
                return {{
                    expected: Math.round(avgIncentive * config.multiplier),
                    metrics: {{
                        total: receivingIncentive,
                        receiving: receivingSubordinates.length,
                        count: subordinates.length,
                        receivingRatio: 0,
                        average: avgIncentive
                    }}
                }};
            }}
        }}

        // Helper: Generate subordinate table HTML
        function generateSubordinateTable(subordinates, config, currentLanguage) {{
            if (subordinates.length === 0) return '';

            const receivingSubordinates = subordinates.filter(sub =>
                Number(sub['{month.lower()}_incentive'] || 0) > 0
            );

            if (config.useGrouping) {{
                // Grouped table (SUPERVISOR, A.MANAGER, MANAGER)
                const subordinatesByGroup = {{}};
                subordinates.forEach(sub => {{
                    // CRITICAL FIX (2025-12-05): String() 변환으로 타입 불일치 방지
                    const groupLeader = employeeData.find(emp => String(emp.emp_no || '') === String(sub.boss_id || ''));
                    const groupName = groupLeader ? groupLeader.name : 'Unknown';
                    if (!subordinatesByGroup[groupName]) {{
                        subordinatesByGroup[groupName] = [];
                    }}
                    subordinatesByGroup[groupName].push(sub);
                }});

                // CRITICAL FIX (2025-12-05): totalIncentive 변수 누락으로 인한 ReferenceError 수정
                // 문제: config.useGrouping === true 브랜치에서 totalIncentive 미정의
                // 원인: 2025-12-04 수정 시 receivingIncentive만 추가하고 totalIncentive 누락
                const totalIncentive = subordinates.reduce((sum, sub) =>
                    sum + Number(sub['{month.lower()}_incentive'] || 0), 0
                );
                // 수령자만 평균 (0 제외) - 2025-12-04 수정
                // 사용자 확인: "인센티브를 받는 사람만으로 계산하는게 맞다"
                const receivingIncentive = receivingSubordinates.reduce((sum, sub) =>
                    sum + Number(sub['{month.lower()}_incentive'] || 0), 0
                );
                const avgIncentive = receivingSubordinates.length > 0 ?
                    receivingIncentive / receivingSubordinates.length : 0;

                return `
                    <div class="mt-3">
                        <h6>📋 ${{getTranslation(`orgChart.modal.${{config.subordinateLabel}}`, currentLanguage)}}</h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>${{getTranslation('orgChart.modal.tableHeaders.groupLeader', currentLanguage)}}</th>
                                    <th>${{getTranslation('orgChart.modal.tableHeaders.lineLeader', currentLanguage)}}</th>
                                    <th>${{getTranslation('orgChart.modal.tableHeaders.id', currentLanguage)}}</th>
                                    <th class="text-end">${{getTranslation('orgChart.modal.tableHeaders.incentive', currentLanguage)}}</th>
                                    <th class="text-center">${{getTranslation('orgChart.modal.tableHeaders.included', currentLanguage)}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{Object.entries(subordinatesByGroup).map(([groupName, subs], groupIdx) => {{
                                    const bgClass = config.useAlternatingColors && groupIdx % 2 === 0 ? '' : 'table-light';
                                    return subs.map((sub, idx) => {{
                                        const subIncentive = Number(sub['{month.lower()}_incentive'] || 0);
                                        const included = subIncentive > 0;
                                        const rowClass = included ? bgClass : `text-muted ${{bgClass}}`;
                                        return `
                                            <tr class="${{rowClass}}">
                                                ${{idx === 0 ? `<td rowspan="${{subs.length}}">${{groupName}}</td>` : ''}}
                                                <td>${{sub.name || sub.employee_name || 'Unknown'}}</td>
                                                <td>${{sub.emp_no || sub.employee_id || ''}}</td>
                                                <td class="text-end">${{included ? '₫' + subIncentive.toLocaleString('ko-KR') : '-'}}</td>
                                                <td class="text-center">${{included ? '✅' : '❌'}}</td>
                                            </tr>
                                        `;
                                    }}).join('');
                                }}).join('')}}
                            </tbody>
                            <tfoot class="table-secondary">
                                <tr>
                                    <th colspan="3">${{getTranslation('orgChart.modal.total', currentLanguage)}}</th>
                                    <th class="text-end">₫${{totalIncentive.toLocaleString('ko-KR')}}</th>
                                    <th></th>
                                </tr>
                                <tr>
                                    <th colspan="3">${{getTranslation('orgChart.modal.averageReceiving', currentLanguage)
                                        .replace('{{{{receiving}}}}', receivingSubordinates.length)
                                        .replace('{{{{total}}}}', subordinates.length)}}</th>
                                    <th class="text-end">₫${{Math.round(avgIncentive).toLocaleString('ko-KR')}}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            }} else {{
                // Simple table (LINE LEADER, GROUP LEADER) - 수령자만 평균 (0 제외, 2025-12-04 수정)
                // 사용자 확인: "인센티브를 받는 사람만으로 계산하는게 맞다"
                const totalIncentive = subordinates.reduce((sum, sub) =>
                    sum + Number(sub['{month.lower()}_incentive'] || 0), 0
                );
                const receivingIncentive = receivingSubordinates.reduce((sum, sub) =>
                    sum + Number(sub['{month.lower()}_incentive'] || 0), 0
                );
                const avgIncentive = receivingSubordinates.length > 0 ?
                    receivingIncentive / receivingSubordinates.length : 0;

                return `
                    <div class="mt-3">
                        <h6>📋 ${{getTranslation(`orgChart.modal.${{config.subordinateLabel}}`, currentLanguage)}}</h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>${{getTranslation('orgChart.modal.tableHeaders.name', currentLanguage)}}</th>
                                    <th>${{getTranslation('orgChart.modal.tableHeaders.id', currentLanguage)}}</th>
                                    <th class="text-end">${{getTranslation('orgChart.modal.tableHeaders.incentive', currentLanguage)}}</th>
                                    <th class="text-center">${{getTranslation(`orgChart.modal.tableHeaders.${{config.subordinateType === 'ASSEMBLY INSPECTOR' ? 'received' : 'included'}}`, currentLanguage)}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{subordinates.map(sub => {{
                                    const subIncentive = Number(sub['{month.lower()}_incentive'] || 0);
                                    const isReceiving = subIncentive > 0;
                                    return `
                                        <tr class="${{isReceiving ? '' : 'text-muted'}}">
                                            <td>${{sub.name || sub.employee_name || 'Unknown'}}</td>
                                            <td>${{sub.emp_no || sub.employee_id || ''}}</td>
                                            <td class="text-end">${{isReceiving ? '₫' + subIncentive.toLocaleString('ko-KR') : '-'}}</td>
                                            <td class="text-center">${{isReceiving ? '✅' : '❌'}}</td>
                                        </tr>
                                    `;
                                }}).join('')}}
                            </tbody>
                            <tfoot class="table-secondary">
                                <tr>
                                    <th colspan="2">${{getTranslation('orgChart.modal.total', currentLanguage)}}</th>
                                    <th class="text-end">₫${{totalIncentive.toLocaleString('ko-KR')}}</th>
                                    <th></th>
                                </tr>
                                <tr>
                                    <th colspan="2">${{getTranslation('orgChart.modal.averageReceiving', currentLanguage)
                                        .replace('{{{{receiving}}}}', receivingSubordinates.length)
                                        .replace('{{{{total}}}}', subordinates.length)}}</th>
                                    <th class="text-end">₫${{Math.round(avgIncentive).toLocaleString('ko-KR')}}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            }}
        }}

        // Helper: Generate calculation details HTML
        function generateCalculationDetails(positionData, config, metrics, expectedIncentive, actualIncentive, currentLanguage) {{
            const positionStr = positionData.positionStr || '';
            const subordinateTable = generateSubordinateTable(
                config.findSubordinates(positionData.nodeId),
                config,
                currentLanguage
            );

            if (config.multiplier === 0.12) {{
                // LINE LEADER specific calculation
                return `
                    <div class="calculation-details">
                        <h6>📊 ${{getTranslation('orgChart.modal.calculationDetails', currentLanguage)}} (LINE LEADER)</h6>
                        <table class="table table-sm">
                            <tr>
                                <td>${{getTranslation('orgChart.modal.labels.formula', currentLanguage)}}:</td>
                                <td class="text-end"><strong>${{getTranslation(config.formulaKey, currentLanguage)}}</strong></td>
                            </tr>
                            <tr>
                                <td>${{getTranslation(`orgChart.modal.labels.${{config.countLabel}}`, currentLanguage)}}:</td>
                                <td class="text-end">${{metrics.count}}${{getTranslation('common.people', currentLanguage)}} (${{getTranslation('orgChart.modal.labels.receiving', currentLanguage)}}: ${{metrics.receiving}}${{getTranslation('common.people', currentLanguage)}})</td>
                            </tr>
                            <tr>
                                <td>${{getTranslation('orgChart.modal.labels.incentiveSum', currentLanguage)}}:</td>
                                <td class="text-end">₫${{metrics.total.toLocaleString('ko-KR')}}</td>
                            </tr>
                            <tr>
                                <td>${{getTranslation('orgChart.modal.labels.receivingRatio', currentLanguage)}}:</td>
                                <td class="text-end">${{metrics.receiving}}/${{metrics.count}} = ${{(metrics.receivingRatio * 100).toFixed(1)}}%</td>
                            </tr>
                            <tr>
                                <td>${{getTranslation('orgChart.modal.labels.calculation', currentLanguage)}}:</td>
                                <td class="text-end">₫${{metrics.total.toLocaleString('ko-KR')}} × 12% × ${{(metrics.receivingRatio * 100).toFixed(1)}}%</td>
                            </tr>
                            <tr class="table-primary">
                                <td><strong>${{getTranslation('orgChart.modal.labels.expectedIncentive', currentLanguage)}}:</strong></td>
                                <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                            <tr class="${{Math.abs(actualIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}}">
                                <td><strong>${{getTranslation('orgChart.modal.labels.actualIncentive', currentLanguage)}}:</strong></td>
                                <td class="text-end"><strong>₫${{actualIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                        </table>
                        ${{subordinateTable}}
                    </div>
                `;
            }} else {{
                // Others: average-based calculation
                return `
                    <div class="calculation-details">
                        <h6>📊 ${{getTranslation('orgChart.modal.calculationDetails', currentLanguage)}} (${{positionStr.toUpperCase().includes('A.MANAGER') || positionStr.toUpperCase().includes('ASSISTANT') ? 'A.MANAGER' : positionStr.toUpperCase().includes('SUPERVISOR') ? 'SUPERVISOR' : positionStr.toUpperCase().includes('GROUP LEADER') ? 'GROUP LEADER' : 'MANAGER'}})</h6>
                        <table class="table table-sm">
                            <tr>
                                <td>${{getTranslation('orgChart.modal.labels.formula', currentLanguage)}}:</td>
                                <td class="text-end"><strong>${{getTranslation(config.formulaKey, currentLanguage)}}</strong></td>
                            </tr>
                            <tr>
                                <td>${{getTranslation(`orgChart.modal.labels.${{config.countLabel}}`, currentLanguage)}}:</td>
                                <td class="text-end">${{metrics.count}}${{getTranslation('common.people', currentLanguage)}} (${{getTranslation('orgChart.modal.labels.receiving', currentLanguage)}}: ${{metrics.receiving}}${{getTranslation('common.people', currentLanguage)}})</td>
                            </tr>
                            <tr>
                                <td>${{getTranslation('orgChart.modal.labels.lineLeaderAvg', currentLanguage)}}:</td>
                                <td class="text-end">₫${{Math.round(metrics.average).toLocaleString('ko-KR')}}</td>
                            </tr>
                            <tr>
                                <td>${{getTranslation('orgChart.modal.labels.calculation', currentLanguage)}}:</td>
                                <td class="text-end">₫${{Math.round(metrics.average).toLocaleString('ko-KR')}} × ${{config.multiplier}}</td>
                            </tr>
                            <tr class="table-primary">
                                <td><strong>${{getTranslation('orgChart.modal.labels.expectedIncentive', currentLanguage) || '예상 incentive'}}:</strong></td>
                                <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                            <tr class="${{Math.abs(actualIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}}">
                                <td><strong>${{getTranslation('orgChart.modal.labels.actualIncentive', currentLanguage) || 'actual incentive'}}:</strong></td>
                                <td class="text-end"><strong>₫${{actualIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                        </table>
                        ${{subordinateTable}}
                    </div>
                `;
            }}
        }}

        // incentive 상세 모달 (전역 스코프)
        window.showIncentiveModal = function(nodeId) {{
            console.log('🔍 모달 함count 호출됨 - Node ID:', nodeId);

            try {{
                // existing 모달이 있으면 강제 닫기
                window.forceCloseModal();

                // CRITICAL FIX: nodeId를 문자열로 변환하여 비교 (타입 불일치 방지)
                const nodeIdStr = String(nodeId);
                const employee = employeeData.find(emp => String(emp.emp_no) === nodeIdStr || String(emp['Employee No']) === nodeIdStr);
                if (!employee) {{
                    console.error('❌ 직원 data를 find count 없음:', nodeId, '(변환된 값:', nodeIdStr, ')');
                    alert('직원 data를 find count not found. ID: ' + nodeId);
                    return;
                }}
                console.log('✅ 직원 발견:', employee.name, employee.position);

                const position = (employee.position || '').toUpperCase();
                const employeeIncentive = Number(employee['{month.lower()}_incentive'] || 0);

                // 부하 직원 찾기 (TYPE-1만) - 문자열 비교로 수정
                const subordinates = employeeData.filter(emp => String(emp.boss_id) === nodeIdStr && emp.type === 'TYPE-1');
                const receivingSubordinates = subordinates.filter(sub => {{
                    const incentive = sub['{month.lower()}_incentive'] || 0;
                    return Number(incentive) > 0;
                }});

                // Configuration-driven calculation
                let calculationDetails = '';
                let expectedIncentive = 0;

                // Get position configuration
                const config = getPositionConfig(employee.position);

                if (config) {{
                    // Find subordinates using configuration
                    const subordinates = config.findSubordinates(nodeId);

                    // Calculate expected incentive and metrics
                    const result = calculateExpectedIncentive(subordinates, config);
                    expectedIncentive = result.expected;

                    // Generate calculation details HTML
                    calculationDetails = generateCalculationDetails(
                        {{ nodeId: nodeId, positionStr: employee.position }},
                        config,
                        result.metrics,
                        expectedIncentive,
                        employeeIncentive,
                        currentLanguage
                    );
                }}

                // 모달 HTML creation
                // 모든 월에 대한 동적 매핑 (CRITICAL FIX: 2025-12-05 - undefined 방지)
                const monthMapping = {{
                    'january': '1', 'february': '2', 'march': '3', 'april': '4',
                    'may': '5', 'june': '6', 'july': '7', 'august': '8',
                    'september': '9', 'october': '10', 'november': '11', 'december': '12'
                }};
                const monthNumber = monthMapping['{month.lower()}'] || '11';
                const modalHtml = `
                <div class="modal fade" id="incentiveModal" tabindex="-1" style="z-index: 1055;">
                    <div class="modal-dialog modal-xl" style="z-index: 1056;">
                        <div class="modal-content" style="z-index: 1057; position: relative; user-select: text; -webkit-user-select: text; -moz-user-select: text; -ms-user-select: text;">
                            <div class="modal-header">
                                <h5 class="modal-title" id="modalTitle">${{getTranslation('modal.modalTitle', currentLanguage)}} - ${{formatModalDate(dashboardYear, monthNumber, currentLanguage)}}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="employee-info mb-3">
                                    <h5>${{employee.name}}</h5>
                                    <p class="mb-1"><strong>${{getTranslation('orgChart.modal.basicInfo.position', currentLanguage)}}:</strong> ${{employee.position}}</p>
                                    <p class="mb-1"><strong>${{getTranslation('orgChart.modal.basicInfo.employeeId', currentLanguage)}}:</strong> ${{employee.emp_no}}</p>
                                    <p class="mb-1"><strong>${{getTranslation('orgChart.modal.basicInfo.type', currentLanguage)}}:</strong> ${{employee.type}}</p>
                                </div>
                                <hr>
                                <div class="incentive-summary mb-3">
                                    <h5 class="${{employeeIncentive > 0 ? 'text-success' : 'text-danger'}}">
                                        <span class="modal-actual-incentive">${{getTranslation('orgChart.modalLabels.actualIncentive', currentLanguage)}}</span>: ₫${{employeeIncentive.toLocaleString('ko-KR')}}
                                    </h5>
                                    <p class="text-muted"><span class="modal-calc-method">${{getTranslation('orgChart.modalLabels.calculationMethod', currentLanguage)}}</span>: ${{getCalculationFormula(employee.position) || '특별 calculation'}}</p>
                                    ${{(() => {{
                                        if (employeeIncentive === 0) {{
                                            const failureReasons = getIncentiveFailureReasons(employee);
                                            if (failureReasons.length > 0) {{
                                                return `
                                                    <div class="alert alert-danger mt-3">
                                                        <h6 class="alert-heading"><i class="bi bi-exclamation-triangle-fill"></i> <span class="modal-no-지급-reason">${{getTranslation('orgChart.modal.alerts.nonPaymentTitle', currentLanguage)}}</span></h6>
                                                        <ul class="mb-0">
                                                            ${{failureReasons.map(reason => `<li>${{reason}}</li>`).join('')}}
                                                        </ul>
                                                    </div>
                                                `;
                                            }}
                                        }} else if (expectedIncentive > 0 && Math.abs(expectedIncentive - employeeIncentive) >= 1000) {{
                                            return `
                                                <div class="alert alert-warning mt-3">
                                                    <h6 class="alert-heading"><i class="bi bi-info-circle-fill"></i> ${{getTranslation('orgChart.modal.alerts.differenceTitle', currentLanguage)}}</h6>
                                                    <table class="table table-sm table-borderless mb-2" style="font-size: 0.9em;">
                                                        <tr>
                                                            <td>${{getTranslation('orgChart.modal.labels.expectedIncentive', currentLanguage)}}:</td>
                                                            <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                                                        </tr>
                                                        <tr>
                                                            <td>${{getTranslation('orgChart.modal.labels.actualIncentive', currentLanguage)}}:</td>
                                                            <td class="text-end"><strong>₫${{employeeIncentive.toLocaleString('ko-KR')}}</strong></td>
                                                        </tr>
                                                        <tr class="border-top">
                                                            <td><strong>${{getTranslation('orgChart.modal.alerts.difference', currentLanguage)}}:</strong></td>
                                                            <td class="text-end"><strong>₫${{Math.abs(expectedIncentive - employeeIncentive).toLocaleString('ko-KR')}}</strong></td>
                                                        </tr>
                                                    </table>
                                                    <p class="mb-0"><small>💡 ${{getTranslation('orgChart.modal.alerts.differenceReason', currentLanguage)}}</small></p>
                                                </div>
                                            `;
                                        }}
                                        return '';
                                    }})()}}
                                </div>
                                ${{calculationDetails}}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"><span class="modal-close-btn">${{getTranslation('orgChart.buttons.close', currentLanguage) || '닫기'}}</span></button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

                // existing 모달 제거 (인스턴스 포함)
                const existingModal = document.getElementById('incentiveModal');
                if (existingModal) {{
                    try {{
                        // existing Bootstrap 모달 인스턴스 제거
                        const existingModalInstance = bootstrap.Modal.getInstance(existingModal);
                        if (existingModalInstance) {{
                            existingModalInstance.dispose();
                        }}
                        existingModal.remove();
                    }} catch (e) {{
                        console.error('existing 모달 제거 중 오류:', e);
                        existingModal.remove();
                    }}
                }}

                // 모달 추가
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                const modalElement = document.getElementById('incentiveModal');

                // Bootstrap 모달 인스턴스 creation 및 표시
                try {{
                    // 모달을 보여주기 전에 tabindex 설정
                    modalElement.setAttribute('tabindex', '-1');
                    modalElement.setAttribute('aria-hidden', 'true');

                    // 모달 컨텐츠에 텍스트 선택 가능하도록 설정
                    const modalContent = modalElement.querySelector('.modal-content');
                    if (modalContent) {{
                        modalContent.style.userSelect = 'text';
                        modalContent.style.webkitUserSelect = 'text';
                        modalContent.style.mozUserSelect = 'text';
                        modalContent.style.msUserSelect = 'text';
                        modalContent.style.position = 'relative';
                        modalContent.style.zIndex = '1057';
                    }}

                    const modal = new bootstrap.Modal(modalElement, {{
                        backdrop: true,      // 배경 클릭으로 닫기 가능
                        keyboard: true,      // ESC 키로 닫기 가능
                        focus: true
                    }});

                    // 모달 표시
                    modal.show();

                    // count동으로 백드롭 클릭 이벤트 추가 (Bootstrap이 제대로 처리 안 될 경우 대비)
                    setTimeout(() => {{
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {{
                        backdrop.style.cursor = 'pointer';
                        backdrop.style.zIndex = '1050';  // 모달보다 낮은 z-index
                        backdrop.addEventListener('click', function() {{
                            console.log('백드롭 클릭 감지');
                            modal.hide();
                        }});
                    }}

                    // 모달 자체의 z-index 확인
                    if (modalElement) {{
                        modalElement.style.zIndex = '1055';
                        const modalDialog = modalElement.querySelector('.modal-dialog');
                        if (modalDialog) {{
                            modalDialog.style.zIndex = '1056';
                        }}
                    }}

                    // ESC 키 이벤트도 count동 추가
                    document.addEventListener('keydown', function escHandler(e) {{
                        if (e.key === 'Escape') {{
                            console.log('ESC 키 감지');
                            modal.hide();
                            document.removeEventListener('keydown', escHandler);
                        }}
                    }});
                    }}, 100);

                    // 모달이 완전히 닫힌 후 정리
                    modalElement.addEventListener('hidden.bs.modal', function onHidden() {{
                    console.log('모달 완전히 닫힘 - 정리 작업 실행');

                    // 이벤트 리스너 제거
                    modalElement.removeEventListener('hidden.bs.modal', onHidden);

                    try {{
                        // 모달 인스턴스 정리
                        const modalInstance = bootstrap.Modal.getInstance(modalElement);
                        if (modalInstance) {{
                            modalInstance.dispose();
                        }}
                    }} catch (e) {{
                        console.error('모달 dispose 오류:', e);
                    }}

                    // 모달 DOM 요소 제거
                    setTimeout(() => {{
                        if (modalElement && modalElement.parentNode) {{
                            modalElement.parentNode.removeChild(modalElement);
                        }}
                        // 백드롭이 남아있다면 제거
                        const backdrops = document.querySelectorAll('.modal-backdrop');
                        backdrops.forEach(backdrop => backdrop.remove());
                        // body 상태 초기화
                        document.body.classList.remove('modal-open');
                        document.body.style.removeProperty('overflow');
                        document.body.style.removeProperty('padding-right');
                        // 추가로 body의 padding도 제거
                        document.body.style.paddingRight = '';
                        document.body.style.overflow = '';
                    }}, 300);  // Bootstrap 애니메이션이 completed될 때까지 대기
                    }});

                    // 모달이 표시된 후 포커스 설정
                    modalElement.addEventListener('shown.bs.modal', function() {{
                    console.log('모달 표시 completed');
                    // 닫기 버튼에 포커스 설정
                    const closeBtn = modalElement.querySelector('[data-bs-dismiss="modal"]');
                    if (closeBtn) {{
                            closeBtn.focus();
                        }}
                    }});

                }} catch (error) {{
                    console.error('모달 creation 오류:', error);
                    // 오류 발생 시 정리 작업
                    if (modalElement) {{
                        modalElement.remove();
                    }}
                    // 백드롭도 제거
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => backdrop.remove());
                    // body 상태 초기화
                    document.body.classList.remove('modal-open');
                    document.body.style.removeProperty('overflow');
                    document.body.style.removeProperty('padding-right');
                    document.body.style.paddingRight = '';
                    document.body.style.overflow = '';
                }}
            }} catch (mainError) {{
                console.error('showIncentiveModal 메인 오류:', mainError);
                alert('모달을 표시하는 중 오류가 발생했습니다.');
            }}
        }}

        // calculation 공식 fetch
        function getCalculationFormula(position) {{
            const pos = (position || '').toUpperCase();

            if (pos.includes('LINE LEADER')) {{
                return getTranslation('orgChart.calculationFormulas.lineLeader');
            }} else if (pos.includes('GROUP LEADER')) {{
                return getTranslation('orgChart.calculationFormulas.groupLeader');
            }} else if (pos.includes('SUPERVISOR')) {{
                return getTranslation('orgChart.calculationFormulas.supervisor');
            }} else if (pos.includes('A.MANAGER') || pos.includes('ASSISTANT')) {{
                return getTranslation('orgChart.calculationFormulas.assistantManager');
            }} else if (pos.includes('MANAGER')) {{
                return getTranslation('orgChart.calculationFormulas.manager');
            }}
            return '';
        }}

        // UI 텍스트 업데이트
        function updateOrgChartUIText() {{
            // 제목 및 설직원 updated
            const titleEl = document.getElementById('orgChartTitle');
            if (titleEl) titleEl.textContent = getTranslation('tabs.orgChart', currentLanguage) || getTranslation('tabs.orgchart', currentLanguage);

            const subtitleEl = document.getElementById('orgChartSubtitle');
            if (subtitleEl) subtitleEl.textContent = getTranslation('orgChart.subtitle', currentLanguage);

            // 메인 제목 업데이트
            const titleMainEl = document.getElementById('orgChartTitleMain');
            if (titleMainEl) titleMainEl.textContent = getTranslation('orgChart.title', currentLanguage);

            const subtitleMainEl = document.getElementById('orgChartSubtitleMain');
            if (subtitleMainEl) subtitleMainEl.textContent = getTranslation('orgChart.subtitle', currentLanguage);

            // 참고 레이블 및 제외된 직급 안내
            const noteLabelEl = document.getElementById('orgChartNoteLabel');
            if (noteLabelEl) noteLabelEl.textContent = getTranslation('orgChart.noteLabel', currentLanguage);

            const excludedEl = document.getElementById('orgChartExcludedPositions');
            if (excludedEl) excludedEl.textContent = getTranslation('orgChart.excludedPositions', currentLanguage);

            // 빵 부스러기 (total 조직)
            const breadcrumbEl = document.getElementById('orgBreadcrumbText');
            if (breadcrumbEl) breadcrumbEl.textContent = getTranslation('orgChart.entireOrganization', currentLanguage);

            // 검색 placeholder
            const searchEl = document.getElementById('orgSearchInput');
            if (searchEl) searchEl.placeholder = getTranslation('orgChart.searchPlaceholder', currentLanguage);

            // 버튼 텍스트
            const expandEl = document.getElementById('expandAllText');
            if (expandEl) expandEl.textContent = getTranslation('orgChart.expandAll', currentLanguage);

            const collapseEl = document.getElementById('collapseAllText');
            if (collapseEl) collapseEl.textContent = getTranslation('orgChart.collapseAll', currentLanguage);

            // 범례
            const legendTitleEl = document.getElementById('legendTitle');
            if (legendTitleEl) legendTitleEl.textContent = getTranslation('orgChart.legendTitle', currentLanguage);

            const legendReceivedEl = document.getElementById('legendIncentiveReceived');
            if (legendReceivedEl) legendReceivedEl.textContent = getTranslation('orgChart.incentiveReceived', currentLanguage);

            const legendNoIncentiveEl = document.getElementById('legendNoIncentive');
            if (legendNoIncentiveEl) legendNoIncentiveEl.textContent = getTranslation('orgChart.noIncentive', currentLanguage);

            // 조직도 내 부하 직원 텍스트 업데이트
            const subordinateCounts = document.querySelectorAll('.subordinate-count[data-i18n-subordinates]');
            subordinateCounts.forEach(el => {{
                const counts = el.getAttribute('data-i18n-subordinates');
                if (counts) {{
                    const type1Text = getTranslation('organizationChart.type1Subordinates', currentLanguage);
                    const employeeUnit = getTranslation('organizationChart.employeeUnit', currentLanguage);
                    el.textContent = `${{type1Text}} ${{counts}}${{employeeUnit}}`;
                }}
            }});
        }}

        // 조직도 초기화 함count
        function resetOrgChart() {{
            drawCollapsibleOrgChart();
        }}

        // 이전 drawCollapsibleTree 함count는 제거
        function drawCollapsibleTree() {{
            console.log('This function is deprecated. Using drawCollapsibleOrgChart instead.');
            drawCollapsibleOrgChart();
            const containerWidth = container.node().getBoundingClientRect().width;
            const width = Math.max(1200, containerWidth);
            const height = 800;
            const margin = {{ top: 20, right: 120, bottom: 20, left: 200 }};

            // SVG 초기화
            d3.select("#orgChartSvg").selectAll("*").remove();

            const svg = d3.select("#orgChartSvg")
                .attr("width", width)
                .attr("height", height);

            const g = svg.append("g")
                .attr("transform", `translate(${{margin.left}},${{height / 2}})`);

            const tree = d3.tree()
                .size([height - margin.top - margin.bottom, width - margin.left - margin.right - 200]);

            const hierarchyData = prepareHierarchyData();
            if (!hierarchyData || hierarchyData.length === 0) {{
                console.log('No hierarchy data available');
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 data를 불러올 count not found.");
                return;
            }}

            try {{
                const root = d3.stratify()
                    .id(d => d.id)
                    .parentId(d => d.parentId)(hierarchyData);

                root.x0 = (height - margin.top - margin.bottom) / 2;
                root.y0 = 0;

                // 초기에 2레벨까지만 펼치기
                root.descendants().forEach((d, i) => {{
                    d.id = i;
                    d._children = d.children;
                    if (d.depth && d.depth > 1) {{
                        d.children = null;
                    }}
                }});

                function update(source) {{
                    const treeData = tree(root);
                    const nodes = treeData.descendants();
                    const links = treeData.descendants().slice(1);

                    // 노드 위치 조정
                    nodes.forEach(d => {{ d.y = d.depth * 180; }});

                    // 노드 업데이트
                    const node = g.selectAll("g.node")
                        .data(nodes, d => d.id || (d.id = ++i));

                    // 새 노드 추가
                    const nodeEnter = node.enter().append("g")
                        .attr("class", "node")
                        .attr("transform", d => `translate(${{source.y0}},${{source.x0}})`)
                        .on("click", click);

                    nodeEnter.append("circle")
                        .attr("class", "node")
                        .attr("r", 1e-6)
                        .style("fill", d => d._children ? "lightsteelblue" : "#fff")
                        .style("stroke", d => getPositionColor(d.data.position))
                        .style("stroke-width", "2px");

                    nodeEnter.append("text")
                        .attr("dy", ".35em")
                        .attr("x", d => d.children || d._children ? -13 : 13)
                        .attr("text-anchor", d => d.children || d._children ? "end" : "start")
                        .style("font-size", "12px")
                        .text(d => d.data.name);

                    // 노드 위치 업데이트
                    const nodeUpdate = nodeEnter.merge(node);

                    nodeUpdate.transition()
                        .duration(750)
                        .attr("transform", d => `translate(${{d.y}},${{d.x}})`);

                    nodeUpdate.select("circle.node")
                        .attr("r", 10)
                        .style("fill", d => d._children ? "lightsteelblue" : "#fff")
                        .attr("cursor", "pointer");

                    // 노드 제거
                    const nodeExit = node.exit().transition()
                        .duration(750)
                        .attr("transform", d => `translate(${{source.y}},${{source.x}})`)
                        .remove();

                    nodeExit.select("circle")
                        .attr("r", 1e-6);

                    nodeExit.select("text")
                        .style("fill-opacity", 1e-6);

                    // 링크 업데이트
                    const link = g.selectAll("path.link")
                        .data(links, d => d.id);

                    const linkEnter = link.enter().insert("path", "g")
                        .attr("class", "link")
                        .style("fill", "none")
                        .style("stroke", "#ccc")
                        .style("stroke-width", "2px")
                        .attr("d", d => {{
                            const o = {{ x: source.x0, y: source.y0 }};
                            return diagonal(o, o);
                        }});

                    const linkUpdate = linkEnter.merge(link);

                    linkUpdate.transition()
                        .duration(750)
                        .attr("d", d => diagonal(d, d.parent));

                    const linkExit = link.exit().transition()
                        .duration(750)
                        .attr("d", d => {{
                            const o = {{ x: source.x, y: source.y }};
                            return diagonal(o, o);
                        }})
                        .remove();

                    // 이전 위치 저장
                    nodes.forEach(d => {{
                        d.x0 = d.x;
                        d.y0 = d.y;
                    }});

                    // 대각선 링크 creation 함count
                    function diagonal(s, d) {{
                        const path = `M ${{s.y}} ${{s.x}}
                                C ${{(s.y + d.y) / 2}} ${{s.x}},
                                  ${{(s.y + d.y) / 2}} ${{d.x}},
                                  ${{d.y}} ${{d.x}}`;
                        return path;
                    }}

                    // 클릭 이벤트 핸들러
                    function click(event, d) {{
                        if (d.children) {{
                            d._children = d.children;
                            d.children = null;
                        }} else {{
                            d.children = d._children;
                            d._children = null;
                        }}
                        update(d);
                    }}
                }}

                var i = 0;
                update(root);

                // Breadcrumb 업데이트
                updateBreadcrumb("접을 count 있는 트리");

                // 범례 추가
                const legend = svg.append("g")
                    .attr("class", "legend")
                    .attr("transform", `translate(${{width - 200}}, 20)`);

                const legendItems = [
                    {{ color: "#1f77b4", label: "Manager" }},
                    {{ color: "#2ca02c", label: "Supervisor" }},
                    {{ color: "#ff7f0e", label: "Group Leader" }},
                    {{ color: "#d62728", label: "Line Leader" }},
                    {{ color: "#9467bd", label: "Inspector" }},
                    {{ color: "#8c564b", label: "Others" }}
                ];

                legendItems.forEach((item, i) => {{
                    const legendItem = legend.append("g")
                        .attr("transform", `translate(0, ${{i * 20}})`);

                    legendItem.append("circle")
                        .attr("r", 6)
                        .style("fill", "white")
                        .style("stroke", item.color)
                        .style("stroke-width", "2px");

                    legendItem.append("text")
                        .attr("x", 15)
                        .attr("y", 5)
                        .style("font-size", "12px")
                        .text(item.label);
                }});

            }} catch (error) {{
                console.error("조직도 creation 오류:", error);
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 creation 중 오류가 발생했습니다: " + error.message);
            }}
        }}

        function drawRadialTree() {{
            const container = d3.select("#orgChartContainer");
            const containerWidth = container.node().getBoundingClientRect().width;
            const radius = Math.min(containerWidth, 1200) / 2; // 더 큰 반경
            const width = radius * 2;
            const height = radius * 2;

            const svg = d3.select("#orgChartSvg")
                .attr("width", width)
                .attr("height", height);

            const g = svg.append("g")
                .attr("transform", `translate(${{width / 2}},${{height / 2}})`);

            const tree = d3.tree()
                .size([2 * Math.PI, radius - 150]) // 더 큰 반경
                .separation((a, b) => {{
                    // 레벨by로 다른 간격 apply
                    if (a.depth <= 2) return 2;
                    if (a.depth === 3) return 1.5;
                    if (a.depth >= 4) return 1.2;
                    return (a.parent == b.parent ? 1 : 2) / a.depth;
                }});

            const hierarchyData = prepareHierarchyData();
            if (!hierarchyData || hierarchyData.length === 0) {{
                console.log('No hierarchy data available');
                return;
            }}

            try {{
                const root = d3.stratify()
                    .id(d => d.id)
                    .parentId(d => d.parentId)(hierarchyData);

                tree(root);

                // 링크 그리기
                const link = g.selectAll(".link")
                    .data(root.links())
                    .enter().append("path")
                    .attr("class", "link")
                    .style("fill", "none")
                    .style("stroke", "#ccc")
                    .style("stroke-width", d => Math.max(1, 3 - d.대상.depth)) // 깊이에 따라 두께 조정
                    .style("opacity", d => Math.max(0.3, 1 - d.대상.depth * 0.15)) // 깊이에 따라 투직원도
                    .attr("d", d3.linkRadial()
                        .angle(d => d.x)
                        .radius(d => d.y));

                // 노드 그리기
                const node = g.selectAll(".node")
                    .data(root.descendants())
                    .enter().append("g")
                    .attr("class", d => "node" + (d.children ? " node--internal" : " node--leaf"))
                    .attr("transform", d => `
                        rotate(${{(d.x * 180 / Math.PI - 90)}})
                        translate(${{d.y}},0)
                    `);

                // 노드 원 (크기를 깊이에 따라 조정, incentive 여부에 따라 색상)
                node.append("circle")
                    .attr("r", d => Math.max(4, 8 - d.depth)) // 깊이에 따라 크기 조정
                    .style("fill", d => {{
                        const baseColor = getPositionColor(d.data.position);
                        // incentive 여부에 따라 채우기 색상
                        if (hasIncentive(d.data)) {{
                            return d.children ? "#fff" : baseColor + "30";
                        }} else {{
                            return "#ffcccc"; // 연한 빨간색
                        }}
                    }})
                    .style("stroke", d => hasIncentive(d.data) ? "#28a745" : "#dc3545")
                    .style("stroke-width", d => Math.max(2, 4 - d.depth * 0.5))
                    .style("cursor", "pointer")
                    .on("mouseover", function(event, d) {{
                        // 툴팁 표시
                        const tooltip = d3.select("body").append("div")
                            .attr("class", "radial-tooltip")
                            .style("position", "absolute")
                            .style("padding", "10px")
                            .style("background", "rgba(0, 0, 0, 0.8)")
                            .style("color", "white")
                            .style("border-radius", "5px")
                            .style("pointer-events", "none")
                            .style("opacity", 0);

                        tooltip.transition()
                            .duration(200)
                            .style("opacity", 0.9);

                        tooltip.html(`
                            <strong>${{d.data.name}}</strong><br/>
                            ID: ${{d.data.id}}<br/>
                            ${{d.data.position}}<br/>
                            type: ${{d.data.type || 'N/A'}}<br/>
                            incentive: ${{hasIncentive(d.data) ? '수령' : '미수령'}}
                        `)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    }})
                    .on("mouseout", function() {{
                        d3.selectAll(".radial-tooltip").remove();
                    }});

                // 텍스트 라벨 (깊이에 따라 크기와 표시 조정)
                node.append("text")
                    .attr("dy", "0.31em")
                    .attr("x", d => d.x < Math.PI === !d.children ? 10 : -10) // 더 큰 간격
                    .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : "end")
                    .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
                    .style("font-size", d => {{
                        // 깊이에 따라 폰트 크기 조정
                        if (d.depth === 0) return "16px";
                        if (d.depth === 1) return "14px";
                        if (d.depth === 2) return "12px";
                        if (d.depth === 3) return "11px";
                        return "10px";
                    }})
                    .style("font-weight", d => d.depth <= 1 ? "bold" : "normal")
                    .text(d => {{
                        // 깊이가 깊을수록 텍스트 줄이기
                        if (d.depth >= 4) {{
                            // Inspector 레벨에서는 이름만 표시하고 줄임
                            const names = d.data.name.split(' ');
                            return names[names.length - 1]; // 성만 표시
                        }}
                        return d.data.name;
                    }});

                // 깊이가 얕은 노드에 대해 포지션 텍스트 추가
                node.filter(d => d.depth < 3)
                    .append("text")
                    .attr("dy", "1.5em")
                    .attr("x", d => d.x < Math.PI === !d.children ? 10 : -10)
                    .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : "end")
                    .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
                    .style("font-size", "9px")
                    .style("fill", "#666")
                    .text(d => d.data.position);

                // 줌 기능 추가 (개선된 초기 줌)
                const zoom = d3.zoom()
                    .scaleExtent([0.3, 4])
                    .on("zoom", (event) => {{
                        g.attr("transform", `translate(${{width / 2}},${{height / 2}}) scale(${{event.transform.k}})`);
                    }});

                svg.call(zoom);

                // 초기 줌을 total가 잘 보이도록 설정
                svg.call(zoom.transform, d3.zoomIdentity.scale(0.8));

                // Breadcrumb 업데이트
                updateBreadcrumb("방사형 트리");

            }} catch (error) {{
                console.error("방사형 조직도 creation 오류:", error);
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 creation 중 오류가 발생했습니다: " + error.message);
            }}
        }}

        // Old D3.js visualization functions - replaced with collapsible tree
        function drawHorizontalTree() {{
            console.log('Horizontal tree deprecated - using collapsible tree');
            return;

            const container = d3.select("#orgChartContainer");
            const containerWidth = container.node().getBoundingClientRect().width;
            const width = Math.max(2000, containerWidth); // 더 넓게
            const height = 3000; // 더 높게
            const margin = {{ top: 50, right: 300, bottom: 50, left: 150 }};
            const duration = 750; // 애니메이션 지속 시간

            const svg = d3.select("#orgChartSvg")
                .style("display", "block")  // SVG 다시 표시
                .attr("width", width)
                .attr("height", height);

            svg.selectAll("*").remove(); // existing 내용 제거

            const g = svg.append("g")
                .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

            // nodeSize를 use하여 고정된 노드 간격 설정
            const treeLayout = d3.tree()
                .nodeSize([50, 200]) // [count직 간격, count평 간격] 늘림
                .separation((a, b) => {{
                    // 같은 부모를 가진 노드들 사이의 간격
                    if (a.parent === b.parent) {{
                        // Inspector 레벨에서는 더 넓은 간격
                        if (a.data.position && a.data.position.includes('INSPECTOR')) {{
                            return 2;
                        }}
                        return 1.2;
                    }}
                    return 1.5;
                }});

            const hierarchyData = prepareHierarchyData();
            if (!hierarchyData || hierarchyData.length === 0) {{
                console.log('No hierarchy data available');
                return;
            }}

            try {{
                const root = d3.stratify()
                    .id(d => d.id)
                    .parentId(d => d.parentId)(hierarchyData);

                // 초기 위치 설정
                root.x0 = height / 2;
                root.y0 = 0;

                // 처음에는 1단계 깊이까지만 열어둠
                root.descendants().forEach((d, i) => {{
                    d.id = i; // 고유 ID 할당
                    if (d.depth > 1) {{
                        d._children = d.children;
                        d.children = null;
                    }}
                }});

                // 업데이트 함count 정의
                function update(source) {{
                    // 트리 레이아웃 calculation
                    const treeData = treeLayout(root);
                    const nodes = treeData.descendants();
                    const links = treeData.links();

                    // 노드 위치 조정 (중앙 정렬)
                    const minY = Math.min(...nodes.map(d => d.x));
                    const maxY = Math.max(...nodes.map(d => d.x));
                    const centerY = (height - margin.top - margin.bottom) / 2;
                    const offsetY = centerY - (maxY + minY) / 2;

                    nodes.forEach(d => {{
                        d.x += offsetY;
                    }});

                    // 노드 업데이트
                    const node = g.selectAll("g.node")
                        .data(nodes, d => d.id || (d.id = ++i));

                    // 새로운 노드 추가
                    const nodeEnter = node.enter().append("g")
                        .attr("class", "node")
                        .attr("transform", d => `translate(${{source.y0}},${{source.x0}})`)
                        .style("cursor", d => d._children || d.children ? "pointer" : "default")
                        .on("click", (event, d) => {{
                            if (d.children) {{
                                d._children = d.children;
                                d.children = null;
                            }} else if (d._children) {{
                                d.children = d._children;
                                d._children = null;
                            }}
                            update(d);
                        }});

                    // 노드 박스 및 내용 추가
                    let boxWidth = 140;
                    let boxHeight = 45;
                    let fontSize = 11;
                    let positionFontSize = 9;

                    // 깊이에 따라 크기 조정
                    if (d.data.depth === 0) {{
                        boxWidth = 160;
                        boxHeight = 50;
                        fontSize = 13;
                        positionFontSize = 10;
                    }} else if (d.data.depth === 1) {{
                        boxWidth = 150;
                        boxHeight = 48;
                        fontSize = 12;
                        positionFontSize = 10;
                    }} else if (d.data.depth >= 4) {{
                        boxWidth = 100;
                        boxHeight = 35;
                        fontSize = 9;
                        positionFontSize = 8;
                    }}

                    // 배경 사각형
                    nodeEnter.append("rect")
                        .attr("x", -boxWidth / 2)
                        .attr("y", -boxHeight / 2)
                        .attr("width", boxWidth)
                        .attr("height", boxHeight)
                        .attr("rx", 5)
                        .style("fill", () => {{
                            const color = getPositionColor(d.data.position);
                            return hasIncentive(d.data) ? color + "30" : color + "10";
                        }})
                        .style("stroke", d => hasIncentive(d.data) ? "#28a745" : "#dc3545")
                        .style("stroke-width", "2px");

                    // 접기/펼치기 심볼
                    nodeEnter.append("circle")
                        .attr("class", "expand-symbol")
                        .attr("r", 8)
                        .attr("cx", boxWidth / 2 + 10)
                        .attr("cy", 0)
                        .style("fill", d => d._children ? "#ff7f0e" : "#2ca02c")
                        .style("stroke", "#333")
                        .style("stroke-width", "1.5px")
                        .style("display", d => d._children || d.children ? "block" : "none");

                    nodeEnter.append("text")
                        .attr("class", "expand-text")
                        .attr("x", boxWidth / 2 + 10)
                        .attr("dy", "0.35em")
                        .attr("text-anchor", "middle")
                        .style("font-size", "12px")
                        .style("font-weight", "bold")
                        .style("fill", "white")
                        .style("pointer-events", "none")
                        .style("display", d => d._children || d.children ? "block" : "none")
                        .text(d => d._children ? "+" : "−");

                    // 텍스트 추가
                    const nameText = d => d.data.depth >= 4 ?
                        d.data.name.split(' ').slice(-1)[0] :
                        d.data.name;

                    // 포지션
                    nodeEnter.append("text")
                        .attr("class", "position-text")
                        .attr("dy", "-0.7em")
                        .attr("text-anchor", "middle")
                        .style("font-size", positionFontSize + "px")
                        .style("fill", "#333")
                        .style("font-weight", "bold")
                        .text(d => d.data.depth < 4 ? d.data.position : "");

                    // 이름
                    nodeEnter.append("text")
                        .attr("class", "name-text")
                        .attr("dy", d => d.data.depth < 4 ? "0.3em" : "0em")
                        .attr("text-anchor", "middle")
                        .style("font-size", fontSize + "px")
                        .style("font-weight", d => d.data.depth <= 1 ? "bold" : "normal")
                        .text(nameText);

                    // ID
                    nodeEnter.append("text")
                        .attr("class", "id-text")
                        .attr("dy", "1.4em")
                        .attr("text-anchor", "middle")
                        .style("font-size", (positionFontSize - 1) + "px")
                        .style("fill", "#666")
                        .text(d => d.data.depth < 4 && boxWidth >= 140 ? `ID: ${{d.data.id}}` : "");

                    // 노드 위치 업데이트 (애니메이션)
                    const nodeUpdate = nodeEnter.merge(node);

                    nodeUpdate.transition()
                        .duration(duration)
                        .attr("transform", d => `translate(${{d.y}},${{d.x}})`);

                    // end 노드 처리
                    const nodeExit = node.exit().transition()
                        .duration(duration)
                        .attr("transform", d => `translate(${{source.y}},${{source.x}})`)
                        .remove();

                    nodeExit.select("rect")
                        .style("opacity", 0);

                    nodeExit.selectAll("text")
                        .style("opacity", 0);

                    // 링크 업데이트
                    const link = g.selectAll("path.link")
                        .data(links, d => d.대상.id);

                    // 새로운 링크 추가
                    const linkEnter = link.enter().insert("path", "g")
                        .attr("class", "link")
                        .style("fill", "none")
                        .style("stroke", "#ccc")
                        .style("stroke-width", 2)
                        .style("opacity", 0.7)
                        .attr("d", d => {{
                            const o = {{x: source.x0, y: source.y0}};
                            return diagonal(o, o);
                        }});

                    // 링크 위치 업데이트
                    const linkUpdate = linkEnter.merge(link);

                    linkUpdate.transition()
                        .duration(duration)
                        .attr("d", d => diagonal(d.source, d.대상));

                    // end 링크 처리
                    const linkExit = link.exit().transition()
                        .duration(duration)
                        .attr("d", d => {{
                            const o = {{x: source.x, y: source.y}};
                            return diagonal(o, o);
                        }})
                        .remove();

                    // 이전 위치 저장
                    nodes.forEach(d => {{
                        d.x0 = d.x;
                        d.y0 = d.y;
                    }});

                    // 대각선 경로 creation 함count
                    function diagonal(s, d) {{
                        return `M ${{s.y}} ${{s.x}}
                                C ${{(s.y + d.y) / 2}} ${{s.x}},
                                  ${{(s.y + d.y) / 2}} ${{d.x}},
                                  ${{d.y}} ${{d.x}}`;
                    }}
                }}

                // 초기 렌더링
                update(root);

                // 줌 기능 추가
                currentZoomBehavior = d3.zoom()
                    .scaleExtent([0.2, 3])
                    .on("zoom", (event) => {{
                        g.attr("transform", event.transform);
                    }});

                svg.call(currentZoomBehavior);

                // 초기 줌 설정 (total가 보이도록)
                setTimeout(() => {{
                    const bounds = g.node().getBBox();
                    const fullWidth = width - margin.left - margin.right;
                    const fullHeight = height - margin.top - margin.bottom;
                    const midX = bounds.x + bounds.width / 2;
                    const midY = bounds.y + bounds.height / 2;
                    const scale = Math.min(fullWidth / bounds.width, fullHeight / bounds.height) * 0.8;

                    svg.call(currentZoomBehavior.transform, d3.zoomIdentity
                        .translate(width / 2, height / 2)
                        .scale(scale)
                        .translate(-midX, -midY));
                }}, 100);

                // Breadcrumb 업데이트
                updateBreadcrumb("count평 트리 (클릭하여 접기/펼치기)");

            }} catch (error) {{
                console.error("count평 조직도 creation 오류:", error);
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 creation 중 오류가 발생했습니다: " + error.message);
            }}
        }}

        function drawTreemap() {{
            console.log('Treemap deprecated - using collapsible tree');
            return;
            const containerWidth = container.node().getBoundingClientRect().width;
            const width = Math.max(1200, containerWidth);
            const height = 800;

            // existing SVG 숨기고 내용 제거
            d3.select("#orgChartSvg")
                .style("display", "none")
                .selectAll("*").remove();

            // existing treemap div 제거
            d3.select("#treemapDiv").remove();

            // treemap을 위한 컨테이너 div creation
            const treemapDiv = d3.select("#orgChartContainer")
                .append("div")
                .attr("id", "treemapDiv")
                .style("width", width + "px")
                .style("height", height + "px")
                .style("position", "relative")
                .style("margin", "20px auto")
                .style("border", "1px solid #dee2e6")
                .style("border-radius", "8px")
                .style("overflow", "hidden")
                .style("background", "#f8f9fa");

            const hierarchyData = prepareHierarchyData();
            if (!hierarchyData || hierarchyData.length === 0) {{
                console.log('No hierarchy data available for treemap');
                return;
            }}

            try {{
                // 계층 구조 creation
                const root = d3.stratify()
                    .id(d => d.id)
                    .parentId(d => d.parentId)(hierarchyData);

                // 각 노드의 value calculation (자식이 없으면 1, 있으면 자식 count)
                root.sum(d => d.children ? 0 : 1)
                    .sort((a, b) => b.value - a.value);

                // Treemap 레이아웃 creation
                d3.treemap()
                    .size([width, height])
                    .padding(2)
                    .round(true)(root);

                // 색상 맵핑
                const colorScale = d3.scaleOrdinal()
                    .domain(['MANAGER', 'SUPERVISOR', 'GROUP LEADER', 'LINE LEADER', 'INSPECTOR', 'Others'])
                    .range(['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']);

                // 노드 creation
                const nodes = treemapDiv.selectAll(".treemap-node")
                    .data(root.leaves())
                    .enter().append("div")
                    .attr("class", "treemap-node")
                    .style("position", "absolute")
                    .style("left", d => d.x0 + "px")
                    .style("top", d => d.y0 + "px")
                    .style("width", d => Math.max(0, d.x1 - d.x0 - 1) + "px")
                    .style("height", d => Math.max(0, d.y1 - d.y0 - 1) + "px")
                    .style("background", d => {{
                        const color = getPositionColor(d.data.position);
                        // incentive 여부에 따라 그라데이션 조정
                        if (hasIncentive(d.data)) {{
                            return `linear-gradient(135deg, ${{color}}, ${{d3.color(color).darker(0.3)}})`;
                        }} else {{
                            // incentive 미수령자는 더 어두운 색상
                            return `linear-gradient(135deg, ${{d3.color(color).darker(0.5)}}, ${{d3.color(color).darker(0.8)}})`;
                        }}
                    }})
                    .style("border", d => {{
                        // incentive 여부에 따라 테두리 색상
                        return hasIncentive(d.data) ? "3px solid #28a745" : "3px solid #dc3545";
                    }})
                    .style("overflow", "hidden")
                    .style("cursor", "pointer")
                    .style("transition", "all 0.3s ease")
                    .on("mouseover", function(event, d) {{
                        d3.select(this)
                            .style("z-index", 100)
                            .style("transform", "scale(1.02)")
                            .style("box-shadow", "0 4px 20px rgba(0,0,0,0.3)");

                        // Tooltip 표시
                        showTooltip(event, d);
                    }})
                    .on("mouseout", function() {{
                        d3.select(this)
                            .style("z-index", 1)
                            .style("transform", "scale(1)")
                            .style("box-shadow", "none");

                        hideTooltip();
                    }});

                // 라벨 추가
                nodes.append("div")
                    .style("padding", "8px")
                    .style("color", "white")
                    .style("font-size", d => {{
                        const width = d.x1 - d.x0;
                        const height = d.y1 - d.y0;
                        if (width > 100 && height > 60) return "14px";
                        if (width > 60 && height > 40) return "12px";
                        return "10px";
                    }})
                    .style("text-shadow", "1px 1px 2px rgba(0,0,0,0.5)")
                    .style("line-height", "1.3")
                    .html(d => {{
                        const width = d.x1 - d.x0;
                        const height = d.y1 - d.y0;

                        if (width > 100 && height > 100) {{
                            return `
                                <div style="font-weight: bold; font-size: 14px;">${{d.data.name}}</div>
                                <div style="font-size: 10px; margin-top: 2px;">ID: ${{d.data.id}}</div>
                                <div style="font-size: 11px; margin-top: 2px;">${{d.data.position}}</div>
                                <div style="font-size: 10px; opacity: 0.9; margin-top: 2px;">
                                    ${{hasIncentive(d.data) ? `✅ ${{getTranslation('orgChart.incentiveReceived', currentLanguage)}}` : `❌ ${{getTranslation('orgChart.incentiveNotReceived', currentLanguage)}}`}}
                                </div>
                            `;
                        }} else if (width > 60 && height > 60) {{
                            return `
                                <div style="font-weight: bold; font-size: 11px;">${{d.data.name}}</div>
                                <div style="font-size: 9px;">ID: ${{d.data.id}}</div>
                            `;
                        }} else if (width > 40 && height > 40) {{
                            const names = d.data.name.split(' ');
                            return `<div style="font-size: 10px;">${{names[names.length - 1]}}</div>`;
                        }}
                        return '';
                    }});

                // Tooltip 함count들
                function showTooltip(event, d) {{
                    const tooltip = d3.select("body").append("div")
                        .attr("class", "treemap-tooltip")
                        .style("position", "absolute")
                        .style("padding", "12px")
                        .style("background", "rgba(0, 0, 0, 0.9)")
                        .style("color", "white")
                        .style("border-radius", "8px")
                        .style("font-size", "14px")
                        .style("pointer-events", "none")
                        .style("opacity", 0)
                        .style("z-index", 1000);

                    tooltip.transition()
                        .duration(200)
                        .style("opacity", 0.9);

                    tooltip.html(`
                        <strong>${{d.data.name}}</strong><br/>
                        ID: ${{d.data.id}}<br/>
                        직위: ${{d.data.position}}<br/>
                        type: ${{d.data.type}}<br/>
                        incentive: ${{hasIncentive(d.data) ?
                            parseIncentive(d.data.incentive).toLocaleString() + ' VND ✅' :
                            '미수령 ❌'}}
                    `)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }}

                function hideTooltip() {{
                    d3.selectAll(".treemap-tooltip").remove();
                }}

                // Breadcrumb 업데이트
                updateBreadcrumb("Treemap 시각화");

            }} catch (error) {{
                console.error("트리맵 creation 오류:", error);
                treemapDiv.append("div")
                    .style("text-align", "center")
                    .style("padding", "20px")
                    .text("트리맵 creation 중 오류가 발생했습니다: " + error.message);
            }}
        }}

        function drawVerticalTree() {{
            console.log('Vertical tree deprecated - using collapsible tree');
            return;

            const container = d3.select("#orgChartContainer");
            if (!container.node()) {{
                console.error('Container not found in drawVerticalTree');
                return;
            }}
            const containerWidth = container.node().getBoundingClientRect().width;
            console.log('Container width in drawVerticalTree:', containerWidth);
            const width = Math.max(6000, containerWidth); // 더 넓게 설정하여 오버랩 방지
            const height = 3000; // 더 높게 설정하여 충분한 공간 확보
            const margin = {{ top: 120, right: 200, bottom: 200, left: 200 }};

            const svg = d3.select("#orgChartSvg")
                .style("display", "block")  // SVG 다시 표시
                .attr("width", width)
                .attr("height", height);

            // Breadcrumb 업데이트
            updateBreadcrumb("count직 트리 (기본)");

            const g = svg.append("g")
                .attr("transform", `translate(${{width / 2}},${{margin.top}})`); // 중앙 정렬

            // data 준비
            let hierarchyData;
            try {{
                hierarchyData = prepareHierarchyData();
                console.log('Hierarchy data prepared:', hierarchyData ? hierarchyData.length : 0, 'nodes');
            }} catch (error) {{
                console.error('Error preparing hierarchy data:', error);
                console.error('Stack trace:', error.stack);
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .style("font-size", "16px")
                    .style("fill", "#dc3545")
                    .text("data 준비 중 오류: " + error.message);
                return;
            }}

            if (!hierarchyData || hierarchyData.length === 0) {{
                console.error('No hierarchy data available');
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .style("font-size", "16px")
                    .style("fill", "#dc3545")
                    .text("조직도 data를 불러올 count not found. data를 확인해주세요.");
                return;
            }}

            // D3 계층 구조 creation
            try {{
                console.log('Creating D3 hierarchy...');
                console.log('Hierarchy data length:', hierarchyData.length);
                if (hierarchyData.length > 0) {{
                    console.log('Sample nodes:', hierarchyData.slice(0, 3));
                }}

                const stratify = d3.stratify()
                    .id(d => d.id)
                    .parentId(d => d.parentId);

                orgChartRoot = stratify(hierarchyData);
                console.log('Root created with', orgChartRoot.descendants().length, 'descendants');

                // count직 트리 레이아웃 creation - nodeSize use으로 더 유연한 간격
                const treeLayout = d3.tree()
                    .nodeSize([250, 200]) // [count평 간격, count직 간격] - 크게 증가시켜 오버랩 방지
                    .separation((a, b) => {{
                        // Inspector 레벨에서는 훨씬 더 넓은 간격
                        const aIsInspector = a.data.position && a.data.position.includes('INSPECTOR');
                        const bIsInspector = b.data.position && b.data.position.includes('INSPECTOR');

                        if (aIsInspector || bIsInspector) {{
                            return 3.0; // Inspector는 3배 간격으로 더 넓게
                        }}

                        // Line Leader도 더 넓게
                        const aIsLineLeader = a.data.position && a.data.position.includes('LINE LEADER');
                        const bIsLineLeader = b.data.position && b.data.position.includes('LINE LEADER');

                        if (aIsLineLeader || bIsLineLeader) {{
                            return 2.5; // Line Leader는 2.5배 간격
                        }}

                        // Supervisor 레벨
                        const aIsSupervisor = a.data.position && a.data.position.includes('SUPERVISOR');
                        const bIsSupervisor = b.data.position && b.data.position.includes('SUPERVISOR');

                        if (aIsSupervisor || bIsSupervisor) {{
                            return 2.0;
                        }}

                        if (a.parent === b.parent) return 1.8; // 같은 부모 노드들도 간격 증가
                        return 2.0; // 기본 간격도 증가
                    }});

                treeLayout(orgChartRoot);

                // Inspector 레벨 노드들을 그리드 형태로 재배치
                const inspectorNodes = orgChartRoot.descendants().filter(d =>
                    d.data.position && d.data.position.includes('INSPECTOR')
                );

                if (inspectorNodes.length > 0) {{
                    // Inspector들을 부모by로 그룹화
                    const inspectorsByParent = {{}};
                    inspectorNodes.forEach(node => {{
                        const parentId = node.parent ? node.parent.data.id : 'root';
                        if (!inspectorsByParent[parentId]) {{
                            inspectorsByParent[parentId] = [];
                        }}
                        inspectorsByParent[parentId].push(node);
                    }});

                    // 각 그룹 내에서 Inspector들을 여러 줄로 배치
                    Object.keys(inspectorsByParent).forEach(parentId => {{
                        const group = inspectorsByParent[parentId];
                        const maxPerRow = 8; // 한 줄에 최대 8employees

                        group.forEach((node, index) => {{
                            const row = Math.floor(index / maxPerRow);
                            const col = index % maxPerRow;
                            const groupCenter = group[0].parent ? group[0].parent.x : 0;

                            // count평 위치: 그룹 중앙을 기준으로 배치
                            const totalWidth = Math.min(maxPerRow, group.length) * 100;
                            const startX = groupCenter - totalWidth / 2;
                            node.x = startX + col * 100;

                            // count직 위치: 행에 따라 조정
                            if (row > 0) {{
                                node.y = node.y + row * 100;
                            }}
                        }});
                    }});
                }}

                // 링크 그리기 - count직 연결선
                const link = g.selectAll(".link")
                    .data(orgChartRoot.links())
                    .enter().append("g")
                    .attr("class", "link");

                // 계단식 연결선 (더 직원확한 계층 표현)
                link.append("path")
                    .attr("fill", "none")
                    .attr("stroke", "#999")
                    .attr("stroke-width", 2)
                    .attr("d", d => {{
                        // count직 계단식 경로
                        const sourceX = d.source.x - width / 2 + margin.left;
                        const sourceY = d.source.y;
                        const targetX = d.대상.x - width / 2 + margin.left;
                        const targetY = d.대상.y;
                        const midY = (sourceY + targetY) / 2;

                        return `M ${{sourceX}} ${{sourceY}}
                                L ${{sourceX}} ${{midY}}
                                L ${{targetX}} ${{midY}}
                                L ${{targetX}} ${{targetY}}`;
                    }});

                // 노드 그룹 creation
                const node = g.selectAll(".node")
                    .data(orgChartRoot.descendants())
                    .enter().append("g")
                    .attr("class", "node")
                    .attr("transform", d => `translate(${{d.x - width / 2 + margin.left}},${{d.y}})`)
                    .on("mouseover", showTooltip)
                    .on("mouseout", hideTooltip)
                    .on("click", nodeClick);

                // 노드 박스 그리기 (incentive 여부에 따라 색상 변경)
                node.append("rect")
                    .attr("width", 180)  // 박스 폭 더 크게 (ID 추가를 위해)
                    .attr("height", 90)  // 박스 높이 더 크게
                    .attr("x", -90)
                    .attr("y", -45)
                    .attr("fill", d => {{
                        const baseColor = getNodeColor(d.data);
                        // incentive 수령 여부에 따라 색상 조정
                        if (hasIncentive(d.data)) {{
                            return baseColor; // 원래 색상 유지
                        }} else {{
                            return baseColor + "40"; // 40% 투직원도로 희미하게
                        }}
                    }})
                    .attr("stroke", d => hasIncentive(d.data) ? "#28a745" : "#dc3545")
                    .attr("stroke-width", 3)
                    .attr("rx", 5)
                    .attr("ry", 5)
                    .style("filter", "drop-shadow(2px 2px 4px rgba(0,0,0,0.2))");

                // 직급 텍스트
                node.append("text")
                    .attr("dy", "-22px")  // 상단 위치
                    .attr("text-anchor", "middle")
                    .style("font-size", "11px")
                    .style("font-weight", "bold")
                    .style("fill", "white")
                    .text(d => d.data.position);

                // 이름 텍스트
                node.append("text")
                    .attr("dy", "0px")  // 중간 위치
                    .attr("text-anchor", "middle")
                    .style("font-size", "12px")
                    .style("fill", "white")
                    .style("font-weight", "bold")
                    .text(d => d.data.name);

                // ID 텍스트 추가
                node.append("text")
                    .attr("dy", "22px")  // 하단 위치
                    .attr("text-anchor", "middle")
                    .style("font-size", "10px")
                    .style("fill", "white")
                    .text(d => `ID: ${{d.data.id}}`);

                // 줌 및 패닝 기능 추가
                currentZoomBehavior = d3.zoom()
                    .scaleExtent([0.1, 3])  // 더 작게 축소 가능
                    .on("zoom", (event) => {{
                        g.attr("transform", event.transform);
                    }});

                svg.call(currentZoomBehavior);

                // 초기 줌 레벨 설정 (total가 보이도록) - 더 작게
                const initialScale = 0.4;  // 더 작은 초기 줌 (total 조직도가 보이도록)
                svg.call(currentZoomBehavior.transform, d3.zoomIdentity
                    .translate(width / 2, margin.top)
                    .scale(initialScale));

            }} catch (error) {{
                console.error("조직도 creation 오류:", error);
                console.error("Error details:", error.message);
                console.error("Error stack:", error.stack);
                console.error("Problematic data sample:", hierarchyData ? hierarchyData.slice(0, 5) : 'No data');

                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 creation 중 오류가 발생했습니다: " + error.message);
            }}
        }}

        function prepareHierarchyData() {{
            console.log('Preparing organization hierarchy data...');
            console.log('Total 직원:', employeeData.length);

            // 먼저 data가 비어있는지 확인
            if (!employeeData || employeeData.length === 0) {{
                console.error('No employee data available!');
                return [];
            }}

            // 첫 몇 직원의 직원 data 확인
            console.log('First employee sample:', employeeData[0]);

            // 제외할 포지션 정의
            const excludedPositions = ['MODEL MASTER', 'AUDIT & TRAINING TEAM', 'AQL INSPECTOR'];

            // TYPE-1 직원 중 특정 포지션 제외
            const type1Employees = employeeData.filter(e =>
                e.type === 'TYPE-1' &&
                !excludedPositions.includes(e.position)
            );
            console.log('TYPE-1 직원 (excluding excluded positions):', type1Employees.length);

            // 전략 determination: TYPE-1이 너무 적으면 total 조직도 표시
            let useAllEmployees = false;
            let requiredIds = new Set();

            if (type1Employees.length < 5) {{
                console.log('Too few TYPE-1 직원, showing full organization chart');
                useAllEmployees = true;

                // 모든 직원 추가 (제외 포지션 제외)
                employeeData.forEach(emp => {{
                    if (!excludedPositions.includes(emp.position)) {{
                        requiredIds.add(emp.emp_no);
                    }}
                }});
            }} else {{
                // TYPE-1 직원들을 먼저 추가
                type1Employees.forEach(emp => {{
                    requiredIds.add(emp.emp_no);
                }});

                // 상사 체인을 재귀적으로 추가 (actual 존재하는 직원만)
                const addBossChain = (empId) => {{
                    const emp = employeeData.find(e => e.emp_no === empId);
                    if (!emp) return;

                    if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== '0') {{
                        // 상사가 actual로 employeeData에 존재하는지 확인
                        // CRITICAL FIX (2025-12-05): String() 변환으로 타입 불일치 방지
                        const bossExists = employeeData.some(e => String(e.emp_no || '') === String(emp.boss_id || ''));

                        if (bossExists && !requiredIds.has(emp.boss_id)) {{
                            requiredIds.add(emp.boss_id);
                            addBossChain(emp.boss_id); // 재귀적으로 상사의 상사 추가
                        }} else if (!bossExists) {{
                            console.log(`Boss ID ${{emp.boss_id}} not found in data for employee ${{emp.name}} (${{emp.emp_no}})`);
                        }}
                    }}
                }};

                // 모든 TYPE-1 직원의 상사 체인 추가
                type1Employees.forEach(emp => {{
                    addBossChain(emp.emp_no);
                }});
            }}

            console.log('Total required nodes:', requiredIds.size, useAllEmployees ? '(showing all 직원)' : '(TYPE-1 + bosses)');

            // 디버깅: 첫 5개 직원 data 확인
            if (employeeData.length > 0) {{
                console.log('Sample employee data:', employeeData.slice(0, 5).map(e => ({{
                    name: e.name,
                    position: e.position,
                    boss_id: e.boss_id,
                    boss_name: e.boss_name
                }})));
            }}

            const data = [];
            const employeeById = {{}};

            // 직원 ID 맵 creation (빈 data 필터링)
            employeeData.forEach(emp => {{
                // nan이거나 빈 emp_no는 제외
                if (emp.emp_no && emp.emp_no !== 'nan' && emp.emp_no !== '') {{
                    employeeById[emp.emp_no] = emp;
                }}
            }});

            // 모든 직원을 노드로 추가 (actual boss_id use)
            let noParentCount = 0;
            let hasParentCount = 0;

            employeeData.forEach(emp => {{
                // 빈 data cases너뛰기
                if (!emp.emp_no || emp.emp_no === 'nan' || emp.emp_no === '') {{
                    return;
                }}

                // 제외할 포지션이면 cases너뛰기
                if (excludedPositions.includes(emp.position)) {{
                    console.log(`Excluding ${{emp.name}} (${{emp.position}}) from org chart`);
                    return;
                }}

                // 필요한 직원이 아니면 cases너뛰기 (TYPE-1이거나 TYPE-1의 상사 체인에 포함)
                if (!requiredIds.has(emp.emp_no)) {{
                    return;
                }}

                // boss_id가 있으면 use, 없으면 boss_name으로 찾기
                let parentId = null;

                if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== 'None' && emp.boss_id !== '0') {{
                    // boss_id가 직원 목록에 있고 requiredIds에도 포함되어 있는지 확인
                    if (employeeById[emp.boss_id] && requiredIds.has(emp.boss_id)) {{
                        parentId = emp.boss_id;
                    }} else if (employeeById[emp.boss_id]) {{
                        // 상사가 does not exist만 TYPE-1 체인에 포함되지 않음
                        console.log(`Boss ${{emp.boss_id}} exists but not in TYPE-1 chain for ${{emp.name}}`);
                    }} else {{
                        console.log(`Warning: Boss ${{emp.boss_id}} not found in data for ${{emp.name}}`);
                        // 상사가 목록에 없으면 parent 없음으로 처리
                    }}
                }}

                if (!parentId && emp.boss_name && emp.boss_name !== '') {{
                    // boss_name으로 boss 찾기
                    const boss = employeeData.find(e => e.name === emp.boss_name);
                    if (boss) {{
                        parentId = boss.emp_no;
                    }}
                }}

                if (parentId) {{
                    hasParentCount++;
                }} else {{
                    noParentCount++;
                }}

                data.push({{
                    id: emp.emp_no,
                    name: emp.name,
                    position: emp.position || 'Unknown',
                    type: emp.type || '',
                    incentive: emp['{month.lower()}_incentive'] || '0',
                    parentId: parentId
                }});
            }});

            console.log(`Created ${{data.length}} nodes: ${{hasParentCount}} with parent, ${{noParentCount}} without parent`);

            // 루트 노드 확인
            const rootNodes = data.filter(d => !d.parentId);
            console.log('Root nodes found:', rootNodes.length);

            // 항상 가상 루트 creation (조직도의 start점)
            const rootTitle = requiredIds.size > 100 ? "Hwaseung Organization" : "Hwaseung TYPE-1 Organization";
            const rootSubtitle = requiredIds.size > 100 ? "Full Organization Chart" : "TYPE-1 Management";
            data.unshift({{
                id: "root",
                name: rootTitle,
                position: rootSubtitle,
                type: "ROOT",
                incentive: "0",
                parentId: null
            }});

            if (rootNodes.length === 0) {{
                console.log('No natural root found, connecting managers to virtual root...');
                // Manager 레벨 직원들을 루트에 연결
                const managers = data.filter(d => {{
                    if (d.id === "root") return false;
                    const pos = (d.position || '').toUpperCase();
                    return pos.includes('MANAGER') && !pos.includes('A.') && !pos.includes('ASSISTANT');
                }});

                if (managers.length === 0) {{
                    // Manager가 없으면 A.Manager를 찾음
                    const aManagers = data.filter(d => {{
                        if (d.id === "root") return false;
                        const pos = (d.position || '').toUpperCase();
                        return pos.includes('A.MANAGER') || pos.includes('ASSISTANT MANAGER');
                    }});

                    aManagers.forEach(manager => {{
                        const idx = data.findIndex(d => d.id === manager.id);
                        if (idx !== -1) {{
                            data[idx].parentId = "root";
                        }}
                    }});
                }} else {{
                    managers.forEach(manager => {{
                        const idx = data.findIndex(d => d.id === manager.id);
                        if (idx !== -1) {{
                            data[idx].parentId = "root";
                        }}
                    }});
                }}
            }} else {{
                console.log(`${{rootNodes.length}} natural root nodes found, connecting to virtual root...`);

                // 루트 노드들을 가상 루트에 연결
                rootNodes.forEach(node => {{
                    // Manager 또는 상위 직급만 루트에 directly 연결
                    const pos = (node.position || '').toUpperCase();
                    if (pos.includes('MANAGER') || pos.includes('SUPERVISOR') || rootNodes.length <= 5) {{
                        const idx = data.findIndex(d => d.id === node.id);
                        if (idx !== -1) {{
                            data[idx].parentId = "root";
                        }}
                    }}
                    // 그 외는 적절한 상위 직급 찾기
                    else {{
                        // 같은 type의 상위 직급 찾기
                        const superiors = data.filter(d => {{
                            if (d.id === "root" || d.id === node.id) return false;
                            const dPos = (d.position || '').toUpperCase();
                            return dPos.includes('MANAGER') || dPos.includes('SUPERVISOR');
                        }});

                        if (superiors.length > 0) {{
                            const idx = data.findIndex(d => d.id === node.id);
                            if (idx !== -1) {{
                                data[idx].parentId = superiors[0].id;
                            }}
                        }} else {{
                            // 상위 직급이 없으면 루트에 연결
                            const idx = data.findIndex(d => d.id === node.id);
                            if (idx !== -1) {{
                                data[idx].parentId = "root";
                            }}
                        }}
                    }}
                }});
            }}




            // 필터 apply
            const typeFilterElement = document.getElementById('orgTypeFilter');
            const incentiveFilterElement = document.getElementById('orgIncentiveFilter');

            const typeFilter = typeFilterElement ? typeFilterElement.value : '';
            const incentiveFilter = incentiveFilterElement ? incentiveFilterElement.value : '';

            let filteredData = data;

            if (typeFilter) {{
                filteredData = filteredData.filter(d => d.type === typeFilter || d.id === "root");
            }}

            if (incentiveFilter === 'paid') {{
                filteredData = filteredData.filter(d => parseIncentive(d.incentive) > 0 || d.id === "root");
            }} else if (incentiveFilter === 'unpaid') {{
                filteredData = filteredData.filter(d => parseIncentive(d.incentive) === 0 || d.id === "root");
            }}

            console.log('Hierarchy data prepared:', filteredData.length, 'nodes');
            return filteredData;
        }}

        function getNodeColor(node) {{
            const position = node.position.toUpperCase();
            if (position.includes('MANAGER')) return '#1f77b4';
            if (position.includes('SUPERVISOR')) return '#2ca02c';
            if (position.includes('GROUP') && position.includes('LEADER')) return '#ff7f0e';
            if (position.includes('LINE') && position.includes('LEADER')) return '#d62728';
            if (position.includes('INSPECTOR')) return '#9467bd';
            return '#8c564b';
        }}

        function showTooltip(event, d) {{
            const tooltip = d3.select("#orgTooltip");
            const incentive = parseIncentive(d.data.incentive);

            tooltip.html(`
                <strong>${{d.data.name}}</strong><br/>
                ${{getTranslation('orgChart.tooltipLabels.empNo', currentLanguage)}}: ${{d.data.id}}<br/>
                ${{getTranslation('orgChart.tooltipLabels.position', currentLanguage)}}: ${{d.data.position}}<br/>
                ${{getTranslation('orgChart.tooltipLabels.type', currentLanguage)}}: ${{d.data.type}}<br/>
                ${{getTranslation('orgChart.tooltipLabels.incentive', currentLanguage)}}: ${{incentive.toLocaleString()}} VND<br/>
                ${{getTranslation('orgChart.tooltipLabels.boss', currentLanguage)}}: ${{d.data.boss_name || getTranslation('orgChart.tooltipLabels.none', currentLanguage)}}
            `);

            tooltip.style("visibility", "visible")
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}

        function hideTooltip() {{
            d3.select("#orgTooltip").style("visibility", "hidden");
        }}

        function nodeClick(event, d) {{
            // 노드 클릭시 corresponding 직원 상세 정보 표시
            // CRITICAL FIX (2025-12-05): String() 변환으로 타입 불일치 방지
            const emp = employeeData.find(e => String(e.emp_no || '') === String(d.data.id || ''));
            if (emp) {{
                showEmployeeDetail(emp);
            }}
        }}

        function updateOrgChart() {{
            drawOrgChart();
        }}

        // Building 필터 함수 (SUPERVISOR, A.MANAGER 요청 - 2025-12-16)
        function filterOrgChartByBuilding() {{
            console.log('Building filter changed, redrawing org chart...');
            drawOrgChart();
        }}

        function resetOrgChart() {{
            const typeFilterElement = document.getElementById('orgTypeFilter');
            const incentiveFilterElement = document.getElementById('orgIncentiveFilter');
            const buildingFilterElement = document.getElementById('orgBuildingFilter');

            if (typeFilterElement) typeFilterElement.value = '';
            if (incentiveFilterElement) incentiveFilterElement.value = '';
            if (buildingFilterElement) buildingFilterElement.value = 'all';
            drawOrgChart();
        }}

        function exportOrgChart() {{
            // SVG를 이미지로 저장
            const svg = document.getElementById('orgChartSvg');
            const serializer = new XMLSerializer();
            const svgStr = serializer.serializeToString(svg);
            const svgBlob = new Blob([svgStr], {{ type: 'image/svg+xml;charset=utf-8' }});
            const url = URL.createObjectURL(svgBlob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `organization_chart_${{new Date().toISOString().slice(0,10)}}.svg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}

        window.onload = function() {{
            try {{
                // 저장된 언어 설정 복원
                const savedLang = localStorage.getItem('dashboardLanguage') || 'ko';
                currentLanguage = savedLang;
                document.getElementById('languageSelector').value = savedLang;

                // 상단 카드 초기화 - 이미 load된 통계 use
                if (window.dashboardStats) {{
                    // ID가 Value로 끝나는 경우와 그렇지 않은 경우 모두 처리
                    const totalElem = document.getElementById('totalEmployees') || document.getElementById('totalEmployeesValue');
                    const paidElem = document.getElementById('paidEmployees') || document.getElementById('paidEmployeesValue');
                    const rateElem = document.getElementById('paymentRate') || document.getElementById('paymentRateValue');
                    const amountElem = document.getElementById('totalAmount') || document.getElementById('totalAmountValue');

                    // 숫자만 표시 (단위는 별도 Unit 엘리먼트에서 처리)
                    if (totalElem) totalElem.textContent = window.dashboardStats.total;
                    if (paidElem) paidElem.textContent = window.dashboardStats.paid;
                    if (rateElem) rateElem.textContent = window.dashboardStats.rate + '%';
                    if (amountElem) amountElem.textContent = window.dashboardStats.amount.toLocaleString() + ' VND';

                    console.log('상단 카드 초기화 completed:', window.dashboardStats);
                }}

                generateEmployeeTable();
                generatePositionTables();
                updatePositionFilter();
                updateAllTexts();
                updateDataFreshness();  // 데이터 신선도 업데이트
                updateTalentPoolSection();

                // Typeby 테이블 업데이트 시도
                if (typeof updateTypeSummaryTable === 'function') {{
                    updateTypeSummaryTable();
                }} else {{
                    console.error('updateTypeSummaryTable 함count가 정의되지 않았습니다.');
                    // 함count가 없으면 directly 실행
                    console.log('Type 테이블 directly 업데이트 start...');
                    if (window.employeeData && window.employeeData.length > 0) {{
                        const typeData = {{
                            'TYPE-1': {{ total: 0, paid: 0, totalAmount: 0 }},
                            'TYPE-2': {{ total: 0, paid: 0, totalAmount: 0 }},
                            'TYPE-3': {{ total: 0, paid: 0, totalAmount: 0 }}
                        }};

                        let grandTotal = 0;
                        let grandPaid = 0;
                        let grandAmount = 0;

                        window.employeeData.forEach(emp => {{
                            const type = emp.type || emp['ROLE TYPE STD'] || 'UNKNOWN';
                            if (typeData[type]) {{
                                typeData[type].total++;
                                grandTotal++;

                                const amount = parseInt(
                                    emp['{month.lower()}_incentive'] ||
                                    emp['{month.capitalize()}_Incentive'] ||
                                    emp['Final Incentive amount'] ||
                                    0
                                );

                                if (amount > 0) {{
                                    typeData[type].paid++;
                                    typeData[type].totalAmount += amount;
                                    grandPaid++;
                                    grandAmount += amount;
                                }}
                            }}
                        }});

                        const tbody = document.getElementById('typeSummaryBody');
                        if (tbody) {{
                            const personUnit = getUnit('people');  // 언어별 단위 가져오기
                            let html = '';

                            ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {{
                                const data = typeData[type];
                                if (data.total > 0) {{
                                    const paymentRate = ((data.paid / data.total) * 100).toFixed(1);
                                    const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid) : 0;
                                    const avgTotal = Math.round(data.totalAmount / data.total);

                                    html += '<tr>';
                                    html += '<td><span class="badge bg-primary">' + type + '</span></td>';
                                    html += '<td>' + data.total + personUnit + '</td>';
                                    html += '<td>' + data.paid + personUnit + '</td>';
                                    html += '<td>' + paymentRate + '%</td>';
                                    html += '<td>' + data.totalAmount.toLocaleString() + ' VND</td>';
                                    html += '<td>' + avgPaid.toLocaleString() + ' VND</td>';
                                    html += '<td>' + avgTotal.toLocaleString() + ' VND</td>';
                                    html += '</tr>';
                                }}
                            }});

                            // 합계 행
                            if (grandTotal > 0) {{
                                const totalPaymentRate = ((grandPaid / grandTotal) * 100).toFixed(1);
                                const totalAvgPaid = grandPaid > 0 ? Math.round(grandAmount / grandPaid) : 0;
                                const totalAvgTotal = Math.round(grandAmount / grandTotal);

                                html += '<tr class="table-active fw-bold">';
                                html += '<td>Total</td>';
                                html += '<td>' + grandTotal + personUnit + '</td>';
                                html += '<td>' + grandPaid + personUnit + '</td>';
                                html += '<td>' + totalPaymentRate + '%</td>';
                                html += '<td>' + grandAmount.toLocaleString() + ' VND</td>';
                                html += '<td>' + totalAvgPaid.toLocaleString() + ' VND</td>';
                                html += '<td>' + totalAvgTotal.toLocaleString() + ' VND</td>';
                                html += '</tr>';
                            }}

                            tbody.innerHTML = html;
                            console.log('Type 테이블 directly 업데이트 completed');
                        }}
                    }}
                }}
            }} catch (e) {{
                console.error('window.onload 에러:', e);
            }}

            // Typeby 테이블 강제 업데이트 함count
            window.forceUpdateTypeSummary = function() {{
                console.log('=== Typeby 요약 테이블 강제 업데이트 실행 ===');
                updateTypeSummaryTable();
            }};

            // 페이지 load 후 1초 뒤 자동 실행
            setTimeout(function() {{
                console.log('Typeby 테이블 자동 업데이트 시도...');
                if (typeof updateTypeSummaryTable === 'function') {{
                    updateTypeSummaryTable();
                }}
                if (window.forceUpdateTypeSummary) {{
                    window.forceUpdateTypeSummary();
                }}
            }}, 1000);
        }};

        // Talent Program 텍스트 업데이트 함count
        function updateTalentProgramTexts() {{
            const lang = currentLanguage;
            
            // 메인 제목
            const programTitle = document.getElementById('talentProgramTitle');
            if (programTitle) {{
                programTitle.innerHTML = getTranslation('talentProgram.title', lang) || '🌟 QIP Talent Pool incentive 프로그램';
            }}
            
            // 소개 텍스트
            const programIntro = document.getElementById('talentProgramIntro');
            if (programIntro) {{
                programIntro.innerHTML = `<strong>QIP Talent Pool</strong> ${{getTranslation('talentProgram.intro', lang) || 'QIP Talent Pool은 우수한 성과를 보이는 인원들을 대상으로 하는 특별 incentive 프로그램입니다. 선정된 인원은 6개월간 매month 추가 보너스를 받게 됩니다.'}}`;
            }}
            
            // 선정 기준 제목
            const qualificationTitle = document.getElementById('talentProgramQualificationTitle');
            if (qualificationTitle) {{
                qualificationTitle.textContent = getTranslation('talentProgram.qualificationTitle', lang) || '🎯 선정 기준';
            }}
            
            // 선정 기준 목록
            const qualifications = document.getElementById('talentProgramQualifications');
            if (qualifications) {{
                const items = [
                    lang === 'en' ? 'Outstanding work performance' : 
                    lang === 'vi' ? 'Hiệu suất làm việc xuất sắc' : '업무 성과 우수자',
                    
                    lang === 'en' ? 'Top 10% in quality target achievement' :
                    lang === 'vi' ? 'Top 10% đạt mục tiêu chất lượng' : '품질 목표 달성률 상위 10%',
                    
                    lang === 'en' ? 'Demonstrated teamwork and leadership' :
                    lang === 'vi' ? 'Thể hiện tinh thần đồng đội và lãnh đạo' : '팀워크 및 리더십 발휘',
                    
                    lang === 'en' ? 'Active participation in continuous improvement' :
                    lang === 'vi' ? 'Tham gia tích cực vào hoạt động cải tiến liên tục' : '지속적인 개선 활동 참여'
                ];
                qualifications.innerHTML = items.map(item => `<li>${{item}}</li>`).join('');
            }}
            
            // 혜택 제목
            const benefitsTitle = document.getElementById('talentProgramBenefitsTitle');
            if (benefitsTitle) {{
                benefitsTitle.textContent = getTranslation('talentProgram.benefitsTitle', lang) || '💰 혜택';
            }}
            
            // 월 보너스 제목
            const monthlyBonusTitle = document.getElementById('talentProgramMonthlyBonusTitle');
            if (monthlyBonusTitle) {{
                monthlyBonusTitle.textContent = getTranslation('talentProgram.monthlyBonusTitle', lang) || 'month 특별 보너스';
            }}
            
            // total 보너스 제목
            const totalBonusTitle = document.getElementById('talentProgramTotalBonusTitle');
            if (totalBonusTitle) {{
                totalBonusTitle.textContent = getTranslation('talentProgram.totalBonusTitle', lang) || 'total 지급 예정액 (6개월)';
            }}
            
            // 프로세스 제목
            const processTitle = document.getElementById('talentProgramProcessTitle');
            if (processTitle) {{
                processTitle.textContent = getTranslation('talentProgram.processTitle', lang) || '📋 평가 프로세스 (6개월 주기)';
            }}
            
            // 6단계 프로세스 업데이트
            const steps = [
                {{
                    titleId: 'talentStep1Title',
                    descId: 'talentStep1Desc',
                    titleKo: '후보자 추천',
                    titleEn: 'Candidate Nomination',
                    titleVi: 'Đề cử ứng viên',
                    descKo: '각 부서에서 우수 인원 추천',
                    descEn: 'Departments nominate outstanding 직원',
                    descVi: 'Các phòng ban đề cử nhân viên xuất sắc'
                }},
                {{
                    titleId: 'talentStep2Title',
                    descId: 'talentStep2Desc',
                    titleKo: '성과 평가',
                    titleEn: 'Performance Evaluation',
                    titleVi: 'Đánh giá hiệu suất',
                    descKo: '최근 3개월간 성과 data 분석',
                    descEn: 'Analysis of last 3 months performance data',
                    descVi: 'Phân tích dữ liệu hiệu suất 3 tháng gần nhất'
                }},
                {{
                    titleId: 'talentStep3Title',
                    descId: 'talentStep3Desc',
                    titleKo: '위원회 심사',
                    titleEn: 'Committee Review',
                    titleVi: 'Xét duyệt của ủy ban',
                    descKo: 'QIP 운영위원회 final 심사',
                    descEn: 'Final review by QIP committee',
                    descVi: 'Xét duyệt cuối cùng bởi ủy ban QIP'
                }},
                {{
                    titleId: 'talentStep4Title',
                    descId: 'talentStep4Desc',
                    titleKo: 'final 선정',
                    titleEn: 'Final Selection',
                    titleVi: 'Lựa chọn cuối cùng',
                    descKo: 'Talent Pool 멤버 확정 및 공지',
                    descEn: 'Confirmation and announcement of Talent Pool members',
                    descVi: 'Xác nhận và thông báo thành viên Talent Pool'
                }},
                {{
                    titleId: 'talentStep5Title',
                    descId: 'talentStep5Desc',
                    titleKo: '보너스 지급',
                    titleEn: 'Bonus Payment',
                    titleVi: 'Thanh toán thưởng',
                    descKo: '매month 정기 incentive와 함께 지급',
                    descEn: 'Paid together with regular monthly incentives',
                    descVi: 'Thanh toán cùng với khen thưởng định kỳ hàng tháng'
                }},
                {{
                    titleId: 'talentStep6Title',
                    descId: 'talentStep6Desc',
                    titleKo: '재평가',
                    titleEn: 'Re-evaluation',
                    titleVi: 'Đánh giá lại',
                    descKo: '6개월 후 재평가 실시',
                    descEn: 'Re-evaluation after 6 months',
                    descVi: 'Đánh giá lại sau 6 tháng'
                }}
            ];
            
            steps.forEach(step => {{
                const titleEl = document.getElementById(step.titleId);
                if (titleEl) {{
                    titleEl.textContent = lang === 'en' ? step.titleEn : lang === 'vi' ? step.titleVi : step.titleKo;
                }}
                const descEl = document.getElementById(step.descId);
                if (descEl) {{
                    descEl.textContent = lang === 'en' ? step.descEn : lang === 'vi' ? step.descVi : step.descKo;
                }}
            }});
            
            // 중요 사항 제목
            const importantTitle = document.getElementById('talentProgramImportantTitle');
            if (importantTitle) {{
                importantTitle.textContent = getTranslation('talentProgram.importantTitle', lang) || '⚠️ 중요 사항';
            }}
            
            // 중요 사항 목록
            const importantNotes = document.getElementById('talentProgramImportantNotes');
            if (importantNotes) {{
                const notes = [
                    lang === 'en' ? 'Talent Pool bonus is paid separately from regular incentives' :
                    lang === 'vi' ? 'Thưởng Talent Pool được thanh toán riêng biệt với khen thưởng thường xuyên' :
                    'Talent Pool 보너스는 기본 incentive와 by도로 지급됩니다',
                    
                    lang === 'en' ? 'Eligibility is automatically lost upon resignation during the 지급 period' :
                    lang === 'vi' ? 'Tư cách sẽ tự động mất khi nghỉ việc trong thời gian thanh toán' :
                    '지급 기간 중 퇴사 시 자격이 자동 상실됩니다',
                    
                    lang === 'en' ? 'May be terminated early if performance is insufficient' :
                    lang === 'vi' ? 'Có thể kết thúc sớm nếu hiệu suất không đủ' :
                    '성과 미달 시 조기 end될 count 있습니다',
                    
                    lang === 'en' ? 'Renewal is determined through re-evaluation every 6 months' :
                    lang === 'vi' ? 'Việc gia hạn được quyết định thông qua đánh giá lại mỗi 6 tháng' :
                    '매 6개월마다 재평가를 통해 갱신 여부가 determination됩니다'
                ];
                importantNotes.innerHTML = notes.map(note => `<li>${{note}}</li>`).join('');
            }}
            
            // 현재 멤버 제목
            const currentTitle = document.getElementById('talentProgramCurrentTitle');
            if (currentTitle) {{
                currentTitle.textContent = getTranslation('talentProgram.currentTitle', lang) || '🎉 현재 Talent Pool 멤버';
            }}
            
            // 멤버가 없을 때 메시지 업데이트
            const currentMembersDiv = document.getElementById('talentProgramCurrentMembers');
            if (currentMembersDiv && currentMembersDiv.innerHTML.includes('현재 Talent Pool 멤버가 not found')) {{
                currentMembersDiv.innerHTML = `<p>${{getTranslation('talentProgram.noMembers', lang) || '현재 Talent Pool 멤버가 not found.'}}</p>`;
            }}
        }}
        
        // Talent Pool 섹션 업데이트
        function updateTalentPoolSection() {{
            const talentPoolMembers = employeeData.filter(emp => emp.Talent_Pool_Member === 'Y' || emp.Talent_Pool_Member === true);
            
            if (talentPoolMembers.length > 0) {{
                // Talent Pool 섹션 표시
                document.getElementById('talentPoolSection').style.display = 'block';

                // 통계 업데이트
                const totalBonus = talentPoolMembers.reduce((sum, emp) => sum + parseInt(emp.Talent_Pool_Bonus || 0), 0);
                const monthlyBonus = talentPoolMembers[0]?.Talent_Pool_Bonus || 0; // 첫 번째 멤버의 월 보너스

                // 직원 수 번역 처리
                const countSuffix = currentLanguage === 'ko' ? '직원' :
                    currentLanguage === 'en' ? (talentPoolMembers.length > 1 ? ' employees' : ' employee') : ' nhân viên';
                document.getElementById('talentPoolCount').textContent = talentPoolMembers.length + countSuffix;
                document.getElementById('talentPoolMonthlyBonus').textContent = parseInt(monthlyBonus).toLocaleString() + ' VND';
                document.getElementById('talentPoolTotalBonus').textContent = totalBonus.toLocaleString() + ' VND';
                document.getElementById('talentPoolPeriod').textContent = '2025.07 - 2025.12';
                
                // 멤버 목록 creation
                const membersLabel = currentLanguage === 'ko' ? 'Talent Pool 멤버:' :
                    currentLanguage === 'en' ? 'Talent Pool Members:' : 'Thành viên Talent Pool:';
                let membersHtml = `<div class="mt-2"><small style="opacity: 0.9;">${{membersLabel}}</small><br>`;
                talentPoolMembers.forEach(emp => {{
                    membersHtml += `
                        <span class="badge" style="background: rgba(255,255,255,0.3); margin: 2px; padding: 5px 10px;">
                            ${{emp.name}} (${{emp.emp_no}}) - ${{emp.position}}
                        </span>
                    `;
                }});
                membersHtml += '</div>';
                document.getElementById('talentPoolMembers').innerHTML = membersHtml;
                
                // incentive 기준 탭의 Talent Program 현재 멤버 섹션도 업데이트
                const currentMembersDiv = document.getElementById('talentProgramCurrentMembers');
                if (currentMembersDiv) {{
                    let currentMembersHtml = '';
                    talentPoolMembers.forEach(emp => {{
                        currentMembersHtml += `
                            <div class="badge" style="background: rgba(255,255,255,0.3); font-size: 1.1em; margin: 5px; padding: 8px 15px;">
                                <i class="fas fa-star"></i> ${{emp.name}} (${{emp.emp_no}}) - ${{emp.position}}
                            </div>
                        `;
                    }});
                    if (currentMembersHtml === '') {{
                        currentMembersHtml = '<p>현재 Talent Pool 멤버가 not found.</p>';
                    }}
                    currentMembersDiv.innerHTML = currentMembersHtml;
                }}
            }} else {{
                // Talent Pool 멤버가 없는 경우
                const currentMembersDiv = document.getElementById('talentProgramCurrentMembers');
                if (currentMembersDiv) {{
                    currentMembersDiv.innerHTML = '<p>현재 Talent Pool 멤버가 not found.</p>';
                }}
            }}
        }}
        
        // 탭 전환
        function showTab(tabName) {{
            // 모든 탭과 컨텐츠 숨기기
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});

            // 선택된 탭과 컨텐츠 표시
            document.querySelector(`[data-tab="${{tabName}}"]`).classList.add('active');
            document.getElementById(tabName).classList.add('active');

            // CRITICAL FIX: 언어 전환 상태 유지 - 탭 전환 후 언어 재적용
            if (window.currentLanguage) {{
                console.log('[Language] Preserving language state on tab change:', window.currentLanguage);
                // 탭 전환 후 언어 업데이트를 다시 적용
                setTimeout(() => {{
                    if (typeof updateAllTexts === 'function') {{
                        updateAllTexts();
                    }}
                    // 탭별 특별 언어 업데이트
                    if (tabName === 'validation' && typeof updateValidationTabTexts === 'function') {{
                        updateValidationTabTexts(window.currentLanguage);
                    }}
                }}, 50);
            }}

            // 요약 탭이면 TYPE 테이블 생성
            if (tabName === 'summary') {{
                console.log('Summary tab selected');
                if (typeof generateTypeTable === 'function') {{
                    generateTypeTable();
                }} else {{
                    console.log('generateTypeTable function not found');
                }}
            }}

            // 조직도 탭이면 조직도 그리기
            if (tabName === 'orgchart') {{
                console.log('Organization chart tab selected');
                setTimeout(() => {{
                    console.log('Calling drawOrgChart from showTab...');
                    drawOrgChart();
                }}, 100);
            }}

            // 검증 탭이면 KPI 카드 초기화
            if (tabName === 'validation') {{
                console.log('Validation tab selected');
                setTimeout(() => {{
                    initValidationTab();
                }}, 100);
            }}

            // Position Details 탭이면 테이블 creation
            if (tabName === 'position') {{
                console.log('Position tab selected');
                setTimeout(() => {{
                    console.log('Calling generatePositionTables...');
                    generatePositionTables();
                }}, 100);
            }}

            // Individual Details 탭이면 테이블 creation
            if (tabName === 'detail') {{
                console.log('Individual Details tab selected');
                setTimeout(() => {{
                    console.log('Calling generateEmployeeTable...');
                    generateEmployeeTable();
                }}, 100);
            }}
        }}
        
        // 직원 테이블 creation
        function generateEmployeeTable() {{
            const tbody = document.getElementById('employeeTableBody');
            tbody.innerHTML = '';

            employeeData.forEach(emp => {{
                // CRITICAL FIX: 필드직원 통th - Employee No와 emp_no 모두 지원
                const empNo = emp.emp_no || emp['Employee No'] || emp['emp_no'];
                const empName = emp.name || emp['Full Name'];
                const empPosition = emp.position || emp['QIP POSITION 1ST NAME'];
                const empType = emp.type || emp['ROLE TYPE STD'] || 'TYPE-2';

                const amount = parseInt(emp['{month.lower()}_incentive'] || emp.september_incentive || 0);
                const isPaid = amount > 0;
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';

                // CRITICAL FIX: empNo를 string로 전달
                tr.onclick = () => showEmployeeDetail(String(empNo));

                // Talent Pool 멤버인 경우 특별 스타th apply
                if (emp.Talent_Pool_Member === 'Y') {{
                    tr.className = 'talent-pool-row';
                }}

                // Talent Pool 정보 HTML creation
                let talentPoolHTML = '-';
                if (emp.Talent_Pool_Member === 'Y') {{
                    talentPoolHTML = `
                        <div class="talent-pool-tooltip">
                            <span class="talent-pool-star">🌟</span>
                            <strong>${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND</strong>
                            <span class="tooltiptext">
                                <strong>${{getTranslation('talentPool.special', currentLanguage) || 'QIP Talent Pool'}}</strong><br>
                                ${{getTranslation('talentPool.monthlyBonus', currentLanguage) || 'month 특별 보너스'}}: ${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND<br>
                                ${{getTranslation('talentPool.period', currentLanguage) || '지급 기간'}}: 2025.07 - 2025.12
                            </span>
                        </div>
                    `;
                }}

                tr.innerHTML = `
                    <td>${{empNo}}</td>
                    <td>${{empName}}${{emp.Talent_Pool_Member === 'Y' ? '<span class="talent-pool-badge">TALENT</span>' : ''}}</td>
                    <td>${{empPosition}}</td>
                    <td><span class="type-badge type-${{empType.toLowerCase().replace('type-', '')}}">${{empType}}</span></td>
                    <td>${{parseInt(emp['{prev_month_name}_incentive'] || emp.previous_incentive || emp.august_incentive || 0).toLocaleString()}}</td>
                    <td><strong>${{amount.toLocaleString()}}</strong></td>
                    <td>${{talentPoolHTML}}</td>
                    <td>${{isPaid ? '✅ ' + getTranslation('status.paid') : '❌ ' + getTranslation('status.unpaid')}}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${{empNo}}')">${{getTranslation('individual.table.detailButton')}}</button></td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        // 직급별 테이블 creation (dashboard_version4.html과 동th한 UI)
        function generatePositionTables() {{
            window.positionData = {{}}; // 전역 변count를 window 객체로 직원시적 접근
            
            // Type-직급별 data 집계
            employeeData.forEach(emp => {{
                const key = `${{emp.type}}_${{emp.position}}`;
                if (!window.positionData[key]) {{
                    window.positionData[key] = {{
                        type: emp.type,
                        position: emp.position,
                        total: 0,
                        paid: 0,
                        totalAmount: 0,
                        직원: []
                    }};
                }}
                
                window.positionData[key].total++;
                window.positionData[key].직원.push(emp);
                const amount = parseInt(emp['{month.lower()}_incentive']) || 0;
                if (amount > 0) {{
                    window.positionData[key].paid++;
                    window.positionData[key].totalAmount += amount;
                }}
            }});
            
            // Typeby로 그룹핑
            const groupedByType = {{}};
            Object.values(window.positionData).forEach(data => {{
                if (!groupedByType[data.type]) {{
                    groupedByType[data.type] = [];
                }}
                groupedByType[data.type].push(data);
            }});

            // CRITICAL FIX (2025-12-05): TYPE-1 평균을 먼저 계산하고 저장
            // TYPE-2가 TYPE-1 평균을 참조할 때 반올림 차이(1 VND)가 발생하지 않도록
            // TYPE-1 평균을 미리 계산하여 캐싱
            window.type1Averages = {{}};
            if (groupedByType['TYPE-1']) {{
                groupedByType['TYPE-1'].forEach(posData => {{
                    const avgAmount = posData.paid > 0 ? Math.round(posData.totalAmount / posData.paid) : 0;
                    window.type1Averages[posData.position] = avgAmount;
                }});
            }}

            // HTML creation
            const container = document.getElementById('positionTables');
            if (container) {{
                container.innerHTML = '';
                
                // Typeby로 섹션 creation
                Object.entries(groupedByType).sort().forEach(([type, positions]) => {{
                    const typeClass = type.toLowerCase().replace('type-', '');
                    
                    // 섹션 제목 번역
                    const sectionTitle = type === 'TYPE-1' ? getTranslation('position.sectionTitles.type1', currentLanguage) :
                                       type === 'TYPE-2' ? getTranslation('position.sectionTitles.type2', currentLanguage) :
                                       type === 'TYPE-3' ? getTranslation('position.sectionTitles.type3', currentLanguage) : 
                                       `${{type}} 직급별 현황`;
                    
                    // 칼럼 헤더 번역 먼저 준비
                    const colPosition = getTranslation('position.positionTable.columns.position', currentLanguage);
                    const colTotal = getTranslation('position.positionTable.columns.total', currentLanguage);
                    const colPaid = getTranslation('position.positionTable.columns.paid', currentLanguage);
                    const colPaymentRate = getTranslation('position.positionTable.columns.paymentRate', currentLanguage);
                    const colTotalAmount = getTranslation('position.positionTable.columns.totalAmount', currentLanguage);
                    const colAvgAmount = getTranslation('position.positionTable.columns.avgAmount', currentLanguage);
                    const colDetails = getTranslation('position.positionTable.columns.details', currentLanguage);
                    
                    let html = '';
                    html += '<div class="mb-5">';
                    html += '<h4 class="mb-3">';
                    html += '<span class="type-badge type-' + typeClass + '">' + type + '</span> ';
                    html += sectionTitle.replace(type + ' ', '');
                    html += '</h4>';
                    html += '<table class="table table-hover">';
                    html += '<thead>';
                    html += '<tr>';
                    html += '<th>' + colPosition + '</th>';
                    html += '<th>' + colTotal + '</th>';
                    html += '<th>' + colPaid + '</th>';
                    html += '<th>' + colPaymentRate + '</th>';
                    html += '<th>' + colTotalAmount + '</th>';
                    html += '<th>' + colAvgAmount + '</th>';
                    html += '<th>' + colDetails + '</th>';
                    html += '</tr>';
                    html += '</thead>';
                    html += '<tbody>';
                    
                    // 직급별 행 추가
                    positions.sort((a, b) => a.position.localeCompare(b.position)).forEach(posData => {{
                        const paymentRate = posData.total > 0 ? (posData.paid / posData.total * 100).toFixed(1) : '0.0';

                        // CRITICAL FIX (2025-12-05): TYPE-2는 TYPE-1 평균을 참조하여 일관성 유지
                        // 문제: TYPE-2 평균과 TYPE-1 평균 사이에 1 VND 차이 발생 (반올림 타이밍)
                        // 해결: TYPE-2는 해당 TYPE-1 직급의 캐싱된 평균을 사용
                        let avgAmount;
                        if (type === 'TYPE-2' && window.type1Averages && window.type1Averages[posData.position]) {{
                            // TYPE-2: TYPE-1 평균 참조 (반올림 이미 적용됨)
                            avgAmount = window.type1Averages[posData.position];
                        }} else {{
                            // TYPE-1, TYPE-3: 직접 계산
                            avgAmount = posData.paid > 0 ? Math.round(posData.totalAmount / posData.paid) : 0;
                        }}

                        const peopleUnit = getTranslation('common.people', currentLanguage);
                        const viewBtnText = getTranslation('position.viewButton', currentLanguage);

                        html += '<tr>';
                        html += '<td>' + posData.position + '</td>';
                        html += '<td>' + posData.total + ' ' + peopleUnit + '</td>';
                        html += '<td>' + posData.paid + ' ' + peopleUnit + '</td>';
                        html += '<td>' + paymentRate + '%</td>';
                        html += '<td>' + posData.totalAmount.toLocaleString() + ' VND</td>';
                        html += '<td>' + avgAmount.toLocaleString() + ' VND</td>';
                        html += '<td>';
                        html += '<button class="btn btn-sm btn-outline-primary" ';
                        html += 'onclick="showPositionDetail(\\'' + type + '\\', \\'' + posData.position + '\\')">';
                        html += viewBtnText;
                        html += '</button>';
                        html += '</td>';
                        html += '</tr>';
                    }});
                    
                    // Typeby 소계
                    const typeTotal = positions.reduce((acc, p) => acc + p.total, 0);
                    const typePaid = positions.reduce((acc, p) => acc + p.paid, 0);
                    const typeAmount = positions.reduce((acc, p) => acc + p.totalAmount, 0);
                    const typeRate = typeTotal > 0 ? (typePaid / typeTotal * 100).toFixed(1) : '0.0';
                    const typeAvg = typePaid > 0 ? Math.round(typeAmount / typePaid) : 0;
                    
                    // 푸터 텍스트 준비
                    const footerTitle = type === 'TYPE-1' ? getTranslation('position.sectionTitles.type1Total', currentLanguage) :
                                      type === 'TYPE-2' ? getTranslation('position.sectionTitles.type2Total', currentLanguage) :
                                      type === 'TYPE-3' ? getTranslation('position.sectionTitles.type3Total', currentLanguage) :
                                      type + ' 합계';
                    const peopleUnit2 = getTranslation('common.people', currentLanguage);
                    
                    html += '</tbody>';
                    html += '<tfoot>';
                    html += '<tr style="font-weight: bold; background-color: #f8f9fa;">';
                    html += '<td>' + footerTitle + '</td>';
                    html += '<td>' + typeTotal + ' ' + peopleUnit2 + '</td>';
                    html += '<td>' + typePaid + ' ' + peopleUnit2 + '</td>';
                    html += '<td>' + typeRate + '%</td>';
                    html += '<td>' + typeAmount.toLocaleString() + ' VND</td>';
                    html += '<td>' + typeAvg.toLocaleString() + ' VND</td>';
                    html += '<td></td>';
                    html += '</tr>';
                    html += '</tfoot>';
                    html += '</table>';
                    html += '</div>';
                    
                    const div = document.createElement('div');
                    div.innerHTML = html;
                    container.appendChild(div);
                }});
            }}
        }}

        // Position 테이블 업데이트 함count (필터링 등에서 use)
        function updatePositionTable() {{
            // Position Details 탭이 활성화되어 있을 때만 업데이트
            const positionTab = document.getElementById('position');
            if (positionTab && positionTab.classList.contains('active')) {{
                console.log('Updating position table...');
                generatePositionTables();
            }}
        }}

        // 직급별 상세 팝업 - 완전 새로운 UI
        function showPositionDetail(type, position) {{
            const 직원 = employeeData.filter(e => e['ROLE TYPE STD'] === type && e['position'] === position);
            if (직원.length === 0) return;

            const modal = document.getElementById('positionModal');
            const modalBody = document.getElementById('positionModalBody');
            const modalTitle = document.getElementById('positionModalLabel');

            modalTitle.innerHTML = `${{type}} - ${{position}} ` + getTranslation('modal.modalTitle', currentLanguage);
            
            // 요약 통계 calculation
            const totalEmployees = 직원.length;
            const paidEmployees = 직원.filter(e => parseInt(e['{month.lower()}_incentive']) > 0).length;
            const avgIncentive = Math.round(직원.reduce((sum, e) => sum + parseInt(e['{month.lower()}_incentive']), 0) / totalEmployees);
            const paidRate = Math.round(paidEmployees/totalEmployees*100);
            
            // 조건 ID를 번역 키로 매핑
            const conditionTranslationMap = {{
                '1': 'modal.tenConditions.1',
                '2': 'modal.tenConditions.2',
                '3': 'modal.tenConditions.3',
                '4': 'modal.tenConditions.4',
                '5': 'modal.tenConditions.5',
                '6': 'modal.tenConditions.6',
                '7': 'modal.tenConditions.7',
                '8': 'modal.tenConditions.8',
                '9': 'modal.tenConditions.9',
                '10': 'modal.tenConditions.10'
            }};
            
            // actual incentive 기준으로 통계 calculation (방안 2 apply)
            const actualPassCount = 직원.filter(emp => parseInt(emp['{month.lower()}_incentive']) > 0).length;
            const actualFailCount = 직원.filter(emp => parseInt(emp['{month.lower()}_incentive']) === 0).length;

            // 각 직원의 조건 충족 통계 calculation (참고용 유지)
            // corresponding 직급에 actual로 apply되는 조건만 표시 (모든 직원이 N/A인 조건 제외)
            const conditionStats = {{}};
            if (직원[0] && 직원[0].condition_results) {{
                // 첫 번째 직원의 조건 중 N/A가 아닌 것만 초기화
                직원[0].condition_results.forEach(cond => {{
                    // 모든 직원에게 N/A인 조건은 cases너뛰기
                    const allNA = 직원.every(e => {{
                        const empCond = e.condition_results?.find(c => c.id === cond.id);
                        return empCond && (empCond.is_na || empCond.actual === 'N/A');
                    }});

                    if (allNA) return;  // 모든 직원이 N/A면 조건 제외

                    const translationKey = conditionTranslationMap[cond.id] || null;
                    const translatedName = translationKey ? getTranslation(translationKey, currentLanguage) : cond.name;
                    conditionStats[cond.id] = {{
                        name: translatedName,
                        met: 0,
                        total: 0,
                        na_count: 0
                    }};
                }});

                직원.forEach(emp => {{
                    if (emp.condition_results) {{
                        emp.condition_results.forEach(cond => {{
                            if (conditionStats[cond.id]) {{
                                if (cond.is_na || cond.actual === 'N/A') {{
                                    conditionStats[cond.id].na_count++;
                                }} else {{
                                    conditionStats[cond.id].total++;
                                    if (cond.is_met) {{
                                        conditionStats[cond.id].met++;
                                    }}
                                }}
                            }}
                        }});
                    }}
                }});
            }}
            
            // incentive 통계 calculation
            const incentiveAmounts = 직원.map(emp => parseInt(emp['{month.lower()}_incentive'])).filter(amt => amt > 0);
            const maxIncentive = incentiveAmounts.length > 0 ? Math.max(...incentiveAmounts) : 0;
            const minIncentive = incentiveAmounts.length > 0 ? Math.min(...incentiveAmounts) : 0;
            const medianIncentive = incentiveAmounts.length > 0 ?
                incentiveAmounts.sort((a, b) => a - b)[Math.floor(incentiveAmounts.length / 2)] : 0;

            modalContent = `
                <div style="display: grid; grid-template-columns: 1fr; gap: 20px; padding: 20px;">
                    <!-- incentive 통계 (1행 4열 배치) -->
                    <div>
                        <h6 style="color: #666; margin-bottom: 15px;">📊 ${{getTranslation('modal.incentiveStats', currentLanguage)}}</h6>
                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px;">
                                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                    <div style="color: #666; font-size: 0.85rem;">${{getTranslation('modal.totalPersonnel', currentLanguage)}}</div>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">${{totalEmployees}}${{getTranslation('common.people', currentLanguage)}}</div>
                                </div>
                                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                    <div style="color: #666; font-size: 0.85rem;">${{getTranslation('modal.paidPersonnel', currentLanguage)}}</div>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;">${{paidEmployees}}${{getTranslation('common.people', currentLanguage)}}</div>
                                </div>
                                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                    <div style="color: #666; font-size: 0.85rem;">${{getTranslation('modal.unpaidPersonnel', currentLanguage)}}</div>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #dc3545;">${{totalEmployees - paidEmployees}}${{getTranslation('common.people', currentLanguage)}}</div>
                                </div>
                                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                    <div style="color: #666; font-size: 0.85rem;">${{getTranslation('modal.paymentRate', currentLanguage)}}</div>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #007bff;">${{paidRate}}%</div>
                                </div>
                            </div>
                            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px;">
                                    <div>
                                        <div style="color: #666; font-size: 0.8rem;">${{getTranslation('modal.avgIncentive', currentLanguage)}}</div>
                                        <div style="font-weight: bold;">${{avgIncentive.toLocaleString()}} VND</div>
                                    </div>
                                    <div>
                                        <div style="color: #666; font-size: 0.8rem;">${{getTranslation('modal.maxIncentive', currentLanguage)}}</div>
                                        <div style="font-weight: bold;">${{maxIncentive.toLocaleString()}} VND</div>
                                    </div>
                                    <div>
                                        <div style="color: #666; font-size: 0.8rem;">${{getTranslation('modal.minIncentive', currentLanguage)}}</div>
                                        <div style="font-weight: bold;">${{minIncentive.toLocaleString()}} VND</div>
                                    </div>
                                    <div>
                                        <div style="color: #666; font-size: 0.8rem;">${{getTranslation('modal.median', currentLanguage)}}</div>
                                        <div style="font-weight: bold;">${{medianIncentive.toLocaleString()}} VND</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- incentive 수령 상세 및 조건by 통계 -->
                    <div style="margin-bottom: 20px;">
                        <h6 style="color: #666; margin-bottom: 10px;">📋 ${{getTranslation('modal.incentiveReceiptStatus.title', currentLanguage)}}</h6>
                        <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div style="padding: 10px; background: #d4edda; border-radius: 5px; border-left: 4px solid #28a745;">
                                    <div style="color: #155724; font-size: 0.85rem;">${{getTranslation('modal.incentiveReceiptStatus.received', currentLanguage)}}</div>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #155724;">${{actualPassCount}}${{getTranslation('common.people', currentLanguage)}}</div>
                                </div>
                                <div style="padding: 10px; background: #f8d7da; border-radius: 5px; border-left: 4px solid #dc3545;">
                                    <div style="color: #721c24; font-size: 0.85rem;">${{getTranslation('modal.incentiveReceiptStatus.notReceived', currentLanguage)}}</div>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #721c24;">${{actualFailCount}}${{getTranslation('common.people', currentLanguage)}}</div>
                                </div>
                            </div>
                        </div>
                        <h6 style="color: #666; margin-bottom: 10px;">📊 ${{getTranslation('modal.incentiveReceiptStatus.conditionsByReference', currentLanguage)}}</h6>
                        <div style="overflow-x: auto;">
                            <table class="table table-sm" style="font-size: 0.9rem;">
                                <thead style="background: #f8f9fa;">
                                    <tr>
                                        <th width="5%">#</th>
                                        <th width="35%">${{getTranslation('modal.condition', currentLanguage)}}</th>
                                        <th width="15%">${{getTranslation('modal.evaluationTarget', currentLanguage)}}</th>
                                        <th width="12%">${{getTranslation('modal.fulfilled', currentLanguage)}}</th>
                                        <th width="12%">${{getTranslation('modal.notFulfilled', currentLanguage)}}</th>
                                        <th width="11%" style="background: #f0f0f0;">N/A</th>
                                        <th width="15%">${{getTranslation('modal.fulfillmentRate', currentLanguage)}}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{Object.entries(conditionStats).map(([id, stat], index) => {{
                                        const isNA = stat.na_count > 0 && stat.total === 0;  // 모든 직원이 N/A인 경우
                                        const rate = stat.total > 0 ? Math.round((stat.met / stat.total) * 100) : 0;
                                        const unmet = stat.total - stat.met;
                                        const evaluatedCount = stat.total;  // N/A가 아닌 평가 eligible count
                                        
                                        return `
                                        <tr>
                                            <td style="color: ${{isNA ? '#999' : '#000'}};">${{index + 1}}</td>
                                            <td style="color: ${{isNA ? '#999' : '#000'}};">${{stat.name}}</td>
                                            <td>${{isNA ? `<span style="color: #999;">N/A</span>` : `${{evaluatedCount}}${{getTranslation('common.people', currentLanguage)}}`}}</td>
                                            <td style="color: ${{isNA ? '#999' : '#28a745'}}; font-weight: bold;">
                                                ${{isNA ? 'N/A' : `${{stat.met}}${{getTranslation('common.people', currentLanguage)}}`}}
                                            </td>
                                            <td style="color: ${{isNA ? '#999' : '#dc3545'}};">
                                                ${{isNA ? 'N/A' : `${{unmet}}${{getTranslation('common.people', currentLanguage)}}`}}
                                            </td>
                                            <td style="background: #f8f8f8; color: #999;">
                                                ${{stat.na_count > 0 ? `${{stat.na_count}}${{getTranslation('common.people', currentLanguage)}}` : '-'}}
                                            </td>
                                            <td>
                                                ${{isNA ? `<span style="color: #999;">N/A</span>` : `
                                                <div style="display: flex; align-items: center; gap: 5px;">
                                                    <div style="background: #e9ecef; height: 8px; width: 60px; border-radius: 4px; overflow: hidden;">
                                                        <div style="background: #28a745; height: 100%; width: ${{rate}}%;"></div>
                                                    </div>
                                                    <span style="font-weight: bold;">${{rate}}%</span>
                                                </div>
                                                `}}
                                            </td>
                                        </tr>
                                        `;
                                    }}).join('')}}
                                </tbody>
                            </table>
                        </div>

                        <!-- TYPE-1 연속 개월 수 규칙 설명 -->
                        ${{type === 'TYPE-1' ? `
                        <div class="alert alert-info mt-3" style="border-left: 4px solid #17a2b8; background: #e7f5f7;">
                            <h6 style="margin-bottom: 10px;"><i class="fas fa-info-circle"></i> <strong>${{getTranslation('modal.type1ContinuousMonthsRule.title', currentLanguage)}}</strong></h6>
                            <ul class="mb-0" style="font-size: 0.9rem; line-height: 1.6;">
                                <li>${{getTranslation('modal.type1ContinuousMonthsRule.allConditionsMet', currentLanguage)}}</li>
                                <li>${{getTranslation('modal.type1ContinuousMonthsRule.anyConditionFailed', currentLanguage)}}</li>
                                <li>${{getTranslation('modal.type1ContinuousMonthsRule.zeroMonthsResult', currentLanguage)}}</li>
                                <li>${{getTranslation('modal.type1ContinuousMonthsRule.example', currentLanguage)}}</li>
                            </ul>
                        </div>
                        ` : ''}}
                    </div>

                    <!-- 직원by 상세 현황 -->
                    <div>
                        <h6 style="color: #666; margin-bottom: 10px;">${{getTranslation('modal.employeeDetails', currentLanguage)}}</h6>
                        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                            <button class="btn btn-sm btn-outline-primary" onclick="filterPositionTable('all')">${{getTranslation('modal.all', currentLanguage)}}</button>
                            <button class="btn btn-sm btn-outline-success" onclick="filterPositionTable('paid')">${{getTranslation('modal.paidOnly', currentLanguage)}}</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="filterPositionTable('unpaid')">${{getTranslation('modal.unpaidOnly', currentLanguage)}}</button>
                        </div>
                        <div style="overflow-x: auto;">
                            <table class="table table-sm" id="positionEmployeeTable" style="font-size: 0.9rem;">
                                <thead style="background: #f8f9fa;">
                                    <tr>
                                        <th>${{getTranslation('modal.tableHeaders.employeeNo', currentLanguage)}}</th>
                                        <th>${{getTranslation('modal.tableHeaders.name', currentLanguage)}}</th>
                                        <th>${{getTranslation('modal.tableHeaders.incentive', currentLanguage)}}</th>
                                        <th>${{getTranslation('modal.tableHeaders.status', currentLanguage)}}</th>
                                        <th>${{getTranslation('modal.tableHeaders.conditionFulfillment', currentLanguage)}}</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            직원.forEach(emp => {{
                const amount = parseInt(emp['{month.lower()}_incentive']);
                const isPaid = amount > 0;
                modalContent += `
                    <tr class="employee-row ${{isPaid ? 'paid-row' : 'unpaid-row'}}" data-emp-no="${{emp.emp_no}}" style="cursor: pointer;">
                        <td>${{emp.emp_no}}</td>
                        <td>${{emp.name}}</td>
                        <td><strong style="color: ${{isPaid ? '#28a745' : '#dc3545'}};">${{amount.toLocaleString()}} VND</strong></td>
                        <td>
                            <span class="badge ${{isPaid ? 'bg-success' : 'bg-danger'}}">
                                ${{isPaid ? getTranslation('modal.paymentStatus.paid', currentLanguage) : getTranslation('modal.paymentStatus.unpaid', currentLanguage)}}
                            </span>
                        </td>
                        <td>
                            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                                ${{(() => {{
                                    if (!emp.condition_results || emp.condition_results.length === 0) return '';

                                    // 카테고리별로 조건 그룹화 (id 기준으로 필터링)
                                    const attendance = emp.condition_results.filter(c => c.id >= 1 && c.id <= 4); // 조건 1-4: 출근
                                    const aql = emp.condition_results.filter(c => c.id >= 5 && c.id <= 8); // 조건 5-8: AQL
                                    const prs = emp.condition_results.filter(c => c.id >= 9 && c.id <= 10); // 조건 9-10: 5PRS

                                    let badges = [];

                                    // 출근 카테고리 평가 (실제 조건 결과 기반)
                                    if (attendance.length > 0) {{
                                        const applicableAttendance = attendance.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const attendanceNA = attendance.every(c => c.is_na || c.actual === 'N/A');

                                        if (attendanceNA) {{
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ': N/A</span>');
                                        }} else {{
                                            const attendanceMet = applicableAttendance.length > 0 && applicableAttendance.every(c => c.is_met);
                                            if (attendanceMet) {{
                                                badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✓</span>');
                                            }} else {{
                                                badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✗</span>');
                                            }}
                                        }}
                                    }}

                                    // AQL 카테고리 평가 (실제 조건 결과 기반)
                                    if (aql.length > 0) {{
                                        const applicableAql = aql.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const aqlNA = aql.every(c => c.is_na || c.actual === 'N/A');

                                        if (aqlNA) {{
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ': N/A</span>');
                                        }} else {{
                                            const aqlMet = applicableAql.length > 0 && applicableAql.every(c => c.is_met);
                                            if (aqlMet) {{
                                                badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✓</span>');
                                            }} else {{
                                                badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✗</span>');
                                            }}
                                        }}
                                    }}

                                    // 5PRS 카테고리 평가 (실제 조건 결과 기반)
                                    if (prs.length > 0) {{
                                        const applicablePrs = prs.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const prsNA = prs.every(c => c.is_na || c.actual === 'N/A');

                                        if (prsNA) {{
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ': N/A</span>');
                                        }} else {{
                                            const prsMet = applicablePrs.length > 0 && applicablePrs.every(c => c.is_met);
                                            if (prsMet) {{
                                                badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✓</span>');
                                            }} else {{
                                                badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✗</span>');
                                            }}
                                        }}
                                    }}

                                    return badges.join('');
                                }})()
                                }}
                            </div>
                        </td>
                    </tr>
                `;
            }});
            
            modalContent += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            modalBody.innerHTML = modalContent;

            // existing backdrop 제거
            const existingBackdrop = document.querySelector('.modal-backdrop');
            if (existingBackdrop) {{
                existingBackdrop.remove();
            }}

            // Bootstrap 5 modal 표시 - 더 안전한 방법
            try {{
                // existing 모달 인스턴스가 있으면 먼저 처리
                const existingModal = bootstrap.Modal.getInstance(modal);
                if (existingModal) {{
                    existingModal.dispose();
                }}

                // 새 모달 인스턴스 creation 및 표시
                const bootstrapModal = new bootstrap.Modal(modal, {{
                    backdrop: true,
                    keyboard: true,
                    focus: true
                }});
                bootstrapModal.show();
            }} catch (e) {{
                console.error('Bootstrap modal error:', e);
                // Fallback: count동으로 모달 표시
                modal.classList.add('show');
                modal.style.display = 'block';
                modal.setAttribute('aria-modal', 'true');
                modal.setAttribute('role', 'dialog');
                document.body.classList.add('modal-open');

                // count동으로 backdrop 추가
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }}

            // 모달 스크롤 초기화 (맨 위로)
            modalBody.scrollTop = 0;
            const modalContentElement = document.querySelector('.modal-content');
            if (modalContentElement) modalContentElement.scrollTop = 0;
            
            // Event delegation을 use하여 직원 행 클릭 이벤트 처리
            setTimeout(() => {{
                const table = document.getElementById('positionEmployeeTable');
                if (!table) {{
                    console.error('Position employee table not found');
                    return;
                }}
                
                // 이전 이벤트 리스너 제거 (중복 방지)
                if (window.positionTableClickHandler) {{
                    table.removeEventListener('click', window.positionTableClickHandler);
                }}
                
                // 새로운 이벤트 핸들러 creation 및 저장
                window.positionTableClickHandler = function(event) {{
                    // tbody 내의 tr을 찾기
                    const row = event.target.closest('tbody tr.employee-row');
                    if (!row) return;
                    
                    // data-emp-no 속성에서 직원번호 fetch
                    const empNo = row.getAttribute('data-emp-no');
                    console.log('Employee row clicked, empNo:', empNo);
                    
                    if (empNo) {{
                        showEmployeeDetailFromPosition(empNo);
                    }}
                }};
                
                // 테이블에 이벤트 리스너 추가
                table.addEventListener('click', window.positionTableClickHandler);
                console.log('Event delegation set up for employee table');
            }}, 100);
            
            // 차트 그리기
            setTimeout(() => {{
                const chartId = `positionChart${{type.replace('-', '')}}${{position.replace(/[\\s()]/g, '')}}`;
                const canvas = document.getElementById(chartId);
                if (canvas) {{
                    const ctx = canvas.getContext('2d');
                    
                    // existing 차트 삭제
                    if (window[`chart_${{chartId}}`]) {{
                        window[`chart_${{chartId}}`].destroy();
                    }}
                    
                    // 새 차트 creation
                    window[`chart_${{chartId}}`] = new Chart(ctx, {{
                        type: 'doughnut',
                        data: {{
                            labels: ['지급', '미지급'],
                            datasets: [{{
                                data: [paidEmployees, totalEmployees - paidEmployees],
                                backgroundColor: ['#28a745', '#dc3545'],
                                borderWidth: 0
                            }}]
                        }},
                        options: {{
                            responsive: false,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{
                                    display: false
                                }}
                            }},
                            cutout: '70%'
                        }}
                    }});
                }}
            }}, 100);
        }}
        
        // 직급별 테이블 필터링
        function filterPositionTable(filter) {{
            const rows = document.querySelectorAll('#positionEmployeeTable tbody tr');
            rows.forEach(row => {{
                if (filter === 'all') {{
                    row.style.display = '';
                }} else if (filter === 'paid' && row.classList.contains('paid-row')) {{
                    row.style.display = '';
                }} else if (filter === 'unpaid' && row.classList.contains('unpaid-row')) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
        
        // 직급별 상세 팝업에서 호출하는 개인별 상세 팝업 함count
        function showEmployeeDetailFromPosition(empNo) {{
            console.log('showEmployeeDetailFromPosition called with empNo:', empNo);
            
            try {{
                // 먼저 직급별 상세 팝업을 닫기
                const positionModal = document.getElementById('positionModal');
                console.log('Position modal element:', positionModal);
                
                if (positionModal) {{
                    const bsPositionModal = bootstrap.Modal.getInstance(positionModal);
                    console.log('Position modal instance:', bsPositionModal);
                    
                    if (bsPositionModal) {{
                        bsPositionModal.hide();
                    }}
                }}
                
                // 잠시 후에 개인별 상세 팝업 열기 (애니메이션 충돌 방지)
                setTimeout(() => {{
                    console.log('Opening employee detail modal for:', empNo);
                    showEmployeeDetail(empNo);
                }}, 300);
            }} catch (error) {{
                console.error('Error in showEmployeeDetailFromPosition:', error);
                // 오류가 있어도 개인별 상세 팝업은 열려야 함
                showEmployeeDetail(empNo);
            }}
        }}

        // showEmployeeDetailFromPosition 함수를 전역으로 노출
        window.showEmployeeDetailFromPosition = showEmployeeDetailFromPosition;

        // 직원 상세 정보 표시 - 전역 함수 업데이트
        // CRITICAL: DOMContentLoaded 내부에서 재정의하지 않고 전역 함수를 업데이트만 함
        window.showEmployeeDetail = function(empNo) {{
            // CRITICAL FIX: type 통th하여 비교 (string로 통th)
            const empNoStr = String(empNo);
            const emp = employeeData.find(e => {{
                const eEmpNo = String(e['Employee No'] || e.emp_no || e['emp_no'] || '');
                return eEmpNo === empNoStr;
            }});

            if (!emp) {{
                console.error('Employee not found:', empNo);
                console.log('Available employee IDs:', employeeData.map(e => e['Employee No'] || e.emp_no).slice(0, 5));
                return;
            }}

            const modal = document.getElementById('employeeModal');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');

            modalTitle.textContent = `${{emp['Full Name']}} (${{emp['Employee No']}}) - ${{getTranslation('modal.title')}}`;

            // 조건 충족 통계 calculation - N/A 제외
            const conditions = emp.condition_results || [];
            const applicableConditions = conditions.filter(c => !c.is_na && c.actual !== 'N/A');
            const passedConditions = applicableConditions.filter(c => c.is_met).length;
            const totalConditions = applicableConditions.length;

            // incentive 지급 여부 확인
            const isPaidEmployee = parseInt(emp['{month.lower()}_incentive']) > 0;

            // FIXED: isInterimReport를 함수 내부에서 직접 계산 (스코프 에러 해결)
            const incentiveDataPeriod = document.getElementById('incentiveDataPeriod');
            const dataEndDay = incentiveDataPeriod ? parseInt(incentiveDataPeriod.getAttribute('data-endday')) : 0;
            const isInterimReport = dataEndDay < 20;

            // TYPE-3 처리: 모든 조건이 N/A인 경우
            let passRate = 0;
            if (emp['ROLE TYPE STD'] === 'TYPE-3') {{
                passRate = 'N/A'; // TYPE-3는 정책적으로 제외
            }} else if (!isPaidEmployee) {{
                // incentive를 받지 못한 경우 0%로 표시
                passRate = 0;
            }} else if (totalConditions > 0) {{
                passRate = (passedConditions / totalConditions * 100).toFixed(0);
            }}

            // AQL Inspector 특별 처리: Part 1/2/3 breakdown
            const isAqlInspector = (emp['QIP POSITION 1ST NAME'] || emp['QIP POSITION 1ST  NAME'] || '').toUpperCase().includes('AQL INSPECTOR');
            let aqlInspectorSection = '';

            if (isAqlInspector && window.aqlIncentiveConfig) {{
                const aqlConfig = window.aqlIncentiveConfig;
                const inspectorData = aqlConfig.aql_inspectors?.[empNoStr] || {{}};
                const monthKey = '{month.lower()}_{year}_incentive';
                const monthData = inspectorData[monthKey] || {{}};

                // Part 1/2/3 테이블 구성
                const part1Months = monthData.part1_months || 0;
                const part3Months = monthData.part3_months || 0;
                const isCfaCertified = inspectorData.cfa_certified || false;

                // Part 1 금액 계산 (progression table)
                const part1Table = aqlConfig.parts?.part1?.incentive_table?.sustained_performance?.amounts || {{}};
                const part1Amount = part1Table[String(part1Months)] || 0;

                // Part 2 금액 (CFA 자격증)
                const part2Amount = isCfaCertified ? (aqlConfig.parts?.part2?.amount || 700000) : 0;

                // Part 3 금액 계산 (HWK)
                const part3Table = aqlConfig.parts?.part3?.incentive_table || {{}};
                const part3Amount = part3Table[String(part3Months)] || 0;

                // 총액
                const totalAmount = part1Amount + part2Amount + part3Amount;

                // 번역
                const langLabels = {{
                    ko: {{
                        title: '🎯 AQL Inspector 인센티브 상세 (3-Part 계산)',
                        part1: 'Part 1: AQL 검사 평가',
                        part2: 'Part 2: CFA 자격증',
                        part3: 'Part 3: HWK 클레임 방지',
                        months: '개월',
                        certified: '보유',
                        notCertified: '미보유',
                        total: '합계',
                        conditionFailed: '⚠️ 출근 조건 미충족으로 지급 보류'
                    }},
                    en: {{
                        title: '🎯 AQL Inspector Incentive Details (3-Part Calculation)',
                        part1: 'Part 1: AQL Evaluation',
                        part2: 'Part 2: CFA Certificate',
                        part3: 'Part 3: HWK Claim Prevention',
                        months: 'months',
                        certified: 'Certified',
                        notCertified: 'Not Certified',
                        total: 'Total',
                        conditionFailed: '⚠️ Payment suspended due to attendance condition not met'
                    }},
                    vi: {{
                        title: '🎯 Chi tiết khuyến khích AQL Inspector (Tính toán 3 phần)',
                        part1: 'Phần 1: Đánh giá AQL',
                        part2: 'Phần 2: Chứng chỉ CFA',
                        part3: 'Phần 3: Ngăn ngừa khiếu nại HWK',
                        months: 'tháng',
                        certified: 'Đã có',
                        notCertified: 'Chưa có',
                        total: 'Tổng cộng',
                        conditionFailed: '⚠️ Tạm ngưng thanh toán do không đạt điều kiện chuyên cần'
                    }}
                }};

                const labels = langLabels[currentLanguage] || langLabels.ko;
                const conditionFailedMsg = !isPaidEmployee ? `<div class="alert alert-warning mt-2 mb-0" style="font-size: 0.9rem;">${{labels.conditionFailed}}</div>` : '';

                aqlInspectorSection = `
                <div class="card mb-4" style="border: 2px solid #17a2b8; background: linear-gradient(135deg, #f8f9fa 0%, #e8f4f8 100%);">
                    <div class="card-body">
                        <h6 class="card-title" style="color: #17a2b8; font-weight: bold;">
                            ${{labels.title}}
                        </h6>
                        <table class="table table-sm table-bordered mb-0">
                            <thead style="background-color: #17a2b8; color: white;">
                                <tr>
                                    <th width="50%">구분</th>
                                    <th width="25%">조건</th>
                                    <th width="25%" class="text-end">금액</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>${{labels.part1}}</strong></td>
                                    <td>${{part1Months}} ${{labels.months}}</td>
                                    <td class="text-end">${{part1Amount.toLocaleString()}} VND</td>
                                </tr>
                                <tr>
                                    <td><strong>${{labels.part2}}</strong></td>
                                    <td>${{isCfaCertified ? '✅ ' + labels.certified : '❌ ' + labels.notCertified}}</td>
                                    <td class="text-end">${{part2Amount.toLocaleString()}} VND</td>
                                </tr>
                                <tr>
                                    <td><strong>${{labels.part3}}</strong></td>
                                    <td>${{part3Months}} ${{labels.months}}</td>
                                    <td class="text-end">${{part3Amount.toLocaleString()}} VND</td>
                                </tr>
                                <tr style="background-color: #d4edda;">
                                    <td colspan="2"><strong>${{labels.total}}</strong></td>
                                    <td class="text-end"><strong>${{totalAmount.toLocaleString()}} VND</strong></td>
                                </tr>
                            </tbody>
                        </table>
                        ${{conditionFailedMsg}}
                    </div>
                </div>
                `;
            }}

            modalBody.innerHTML = `
                <!-- 상단 통계 카드 -->
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{emp['ROLE TYPE STD']}}</div>
                            <div class="stat-label">${{getTranslation('modal.basicInfo.type')}}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{emp['QIP POSITION 1ST NAME'] || emp.position || emp['FINAL QIP POSITION NAME CODE'] || 'N/A'}}</div>
                            <div class="stat-label">${{getTranslation('modal.basicInfo.position')}}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{parseInt(emp['{month.lower()}_incentive']).toLocaleString()}} VND</div>
                            <div class="stat-label">${{getTranslation('modal.incentiveInfo.amount')}}</div>
                        </div>
                    </div>
                </div>

                <!-- AQL Inspector 특별 섹션 (Part 1/2/3 breakdown) -->
                ${{aqlInspectorSection}}

                <!-- 차트와 조건 충족도 -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6 class="card-title">` + getTranslation('modal.detailPopup.conditionFulfillment', currentLanguage) + `</h6>
                                <div style="width: 200px; height: 200px; margin: 0 auto; position: relative;">
                                    <canvas id="conditionChart${{empNo}}" width="200" height="200"></canvas>
                                </div>
                                <div class="mt-3">
                                    <h4>${{passRate === 'N/A' ? 'N/A' : passRate + '%'}}</h4>
                                    <p class="text-muted">${{
                                        emp['ROLE TYPE STD'] === 'TYPE-3' ? getTranslation('modal.detailPopup.type3PolicyExcluded', currentLanguage) || 'TYPE-3: 정책적 제외 대상' :
                                        !isPaidEmployee && totalConditions > 0 ? getTranslation('modal.detailPopup.conditionNotMet', currentLanguage) :
                                        totalConditions > 0 ? passedConditions + ' / ' + totalConditions + ' ' + getTranslation('modal.detailPopup.conditionsFulfilled', currentLanguage) :
                                        getTranslation('modal.detailPopup.noConditions', currentLanguage)
                                    }}</p>
                                    ${{
                                        // 특이 케이스: 중간 리포트에서 100% 표시되지만 최소 근무일 미충족
                                        isInterimReport && passRate === 100.0 && !isPaidEmployee &&
                                        emp['Actual Working Days'] && parseFloat(emp['Actual Working Days']) < 12 ?
                                        `<div class="alert alert-warning mt-2 mb-0" style="font-size: 0.85rem; padding: 0.5rem;">
                                            <i class="fas fa-exclamation-triangle"></i>
                                            <strong>${{currentLanguage === 'ko' ? '중간 리포트 특이 케이스' :
                                                      currentLanguage === 'en' ? 'Interim Report Special Case' :
                                                      'Trường hợp đặc biệt báo cáo tạm thời'}}</strong><br>
                                            <small>${{currentLanguage === 'ko' ?
                                                '최소 근무일 조건이 중간 리포트에서 미평가되었습니다.' :
                                                currentLanguage === 'en' ?
                                                'Minimum working days condition not evaluated in interim report.' :
                                                'Điều kiện số ngày làm việc tối thiểu chưa được đánh giá trong báo cáo tạm thời.'}}</small><br>
                                            <small>${{currentLanguage === 'ko' ?
                                                `현재 근무일: ${{parseFloat(emp['Actual Working Days']).toFixed(1)}}일 / 필요: 12일` :
                                                currentLanguage === 'en' ?
                                                `Current: ${{parseFloat(emp['Actual Working Days']).toFixed(1)}} days / Required: 12 days` :
                                                `Hiện tại: ${{parseFloat(emp['Actual Working Days']).toFixed(1)}} ngày / Yêu cầu: 12 ngày`}}</small>
                                        </div>` : ''
                                    }}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h6 class="card-title">` + getTranslation('modal.detailPopup.paymentStatus', currentLanguage) + `</h6>
                                <div class="지급-status ${{parseInt(emp['{month.lower()}_incentive']) > 0 ? 'paid' : 'unpaid'}}">
                                    ${{parseInt(emp['{month.lower()}_incentive']) > 0 ? `
                                    <div>
                                        <div style="font-size: 48px; margin-bottom: 10px;">✅</div>
                                        <h5>` + getTranslation('status.paid', currentLanguage) + `</h5>
                                        <p class="mb-1">${{parseInt(emp['{month.lower()}_incentive']).toLocaleString()}} VND</p>
                                        ${{emp.Talent_Pool_Member === 'Y' ? `
                                        <div style="background: linear-gradient(135deg, #FFD700, #FFA500); padding: 8px; border-radius: 8px; margin-top: 10px;">
                                            <small style="color: white; font-weight: bold;">
                                                🌟 Talent Pool 보너스 포함<br>
                                                기본: ${{(parseInt(emp['{month.lower()}_incentive']) - parseInt(emp.Talent_Pool_Bonus || 0)).toLocaleString()}} VND<br>
                                                보너스: +${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND
                                            </small>
                                        </div>` : ''}}
                                    </div>` : `
                                    <div>
                                        <div style="font-size: 48px; margin-bottom: 10px;">❌</div>
                                        <h5>` + getTranslation('status.unpaid', currentLanguage) + `</h5>
                                        <p>` + getTranslation('modal.detailPopup.conditionNotMet', currentLanguage) + `</p>
                                    </div>`}}
                                </div>
                                <div class="mt-3">
                                    <small class="text-muted">` + getTranslation('modal.detailPopup.lastMonthIncentive', currentLanguage) + `: ${{parseInt(emp['{prev_month_name}_incentive'] || emp.previous_incentive || 0).toLocaleString()}} VND</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 출근 상세 정보 (Added 2025-11-29) -->
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">` + getTranslation('modal.detailPopup.attendanceDetails', currentLanguage) + `</h6>
                        ${{(() => {{
                            const totalDays = parseFloat(emp['Total Working Days'] || 0);
                            const actualDays = parseFloat(emp['Actual Working Days'] || 0);
                            const approvedLeave = parseFloat(emp['Approved Leave Days'] || 0);
                            const absenceDays = Math.max(0, totalDays - actualDays - approvedLeave);
                            const absenceRate = totalDays > 0 ? ((absenceDays / totalDays) * 100).toFixed(1) : 0;
                            const attendanceRate = totalDays > 0 ? (100 - absenceRate).toFixed(1) : 0;

                            const translations = {{
                                ko: {{
                                    totalDays: '총 근무일',
                                    actualDays: '실제 근무일',
                                    approvedLeave: '승인휴가',
                                    absenceDays: '결근일',
                                    absenceRate: '결근율',
                                    attendanceRate: '출근율',
                                    formula: '계산식',
                                    days: '일'
                                }},
                                en: {{
                                    totalDays: 'Total Working Days',
                                    actualDays: 'Actual Working Days',
                                    approvedLeave: 'Approved Leave',
                                    absenceDays: 'Absence Days',
                                    absenceRate: 'Absence Rate',
                                    attendanceRate: 'Attendance Rate',
                                    formula: 'Formula',
                                    days: 'days'
                                }},
                                vi: {{
                                    totalDays: 'Tổng ngày làm việc',
                                    actualDays: 'Ngày làm việc thực tế',
                                    approvedLeave: 'Nghỉ phép',
                                    absenceDays: 'Ngày vắng mặt',
                                    absenceRate: 'Tỷ lệ vắng',
                                    attendanceRate: 'Tỷ lệ đi làm',
                                    formula: 'Công thức',
                                    days: 'ngày'
                                }}
                            }};
                            const t = translations[currentLanguage] || translations.ko;

                            return `
                            <div class="row">
                                <div class="col-md-6">
                                    <table class="table table-sm table-borderless mb-0">
                                        <tr><td><strong>${{t.totalDays}}:</strong></td><td>${{totalDays}} ${{t.days}}</td></tr>
                                        <tr><td><strong>${{t.actualDays}}:</strong></td><td>${{actualDays}} ${{t.days}}</td></tr>
                                        <tr><td><strong>${{t.approvedLeave}}:</strong></td><td>${{approvedLeave}} ${{t.days}}</td></tr>
                                        <tr><td><strong>${{t.absenceDays}}:</strong></td><td>${{absenceDays}} ${{t.days}}</td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <table class="table table-sm table-borderless mb-0">
                                        <tr><td><strong>${{t.absenceRate}}:</strong></td><td>${{absenceRate}}%</td></tr>
                                        <tr class="${{parseFloat(attendanceRate) >= 88 ? 'table-success' : 'table-danger'}}">
                                            <td><strong>${{t.attendanceRate}}:</strong></td>
                                            <td><strong>${{attendanceRate}}%</strong> ${{parseFloat(attendanceRate) >= 88 ? '✅' : '❌'}}</td>
                                        </tr>
                                    </table>
                                    <small class="text-muted d-block mt-2">
                                        <strong>${{t.formula}}:</strong><br>
                                        ${{t.absenceDays}} = ${{totalDays}} - ${{actualDays}} - ${{approvedLeave}} = ${{absenceDays}}<br>
                                        ${{t.attendanceRate}} = 100 - (${{absenceDays}}/${{totalDays}}×100) = ${{attendanceRate}}%
                                    </small>
                                </div>
                            </div>
                            `;
                        }})()}}
                    </div>
                </div>

                <!-- 조건 충족 상세 테이블 -->
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">` + getTranslation('modal.detailPopup.conditionDetails', currentLanguage) + `</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th width="5%">#</th>
                                        <th width="50%">` + getTranslation('modal.detailPopup.condition', currentLanguage) + `</th>
                                        <th width="25%">` + getTranslation('modal.detailPopup.performance', currentLanguage) + `</th>
                                        <th width="20%">` + getTranslation('modal.detailPopup.result', currentLanguage) + `</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{conditions
                                        .filter(cond => !cond.is_na && cond.actual !== 'N/A')  // N/A 조건 제외
                                        .map((cond, idx) => {{
                                        let rowClass = 'table-success';
                                        let badgeHtml = '';
                                        let actualHtml = '';

                                        // N/A는 이미 필터링되었으므로 else 블록만 실행
                                        {{
                                            rowClass = cond.is_met ? 'table-success' : 'table-danger';

                                            // 실적 값의 단위 번역 처리
                                            let actualValue = cond.actual;

                                            // CRITICAL FIX: 소count점은 첫째자리까지만 표시
                                            if (typeof actualValue === 'number') {{
                                                actualValue = Number(actualValue).toFixed(1);
                                            }} else if (typeof actualValue === 'string') {{
                                                // 숫자 string인 경우 소count점 처리
                                                const numMatch = actualValue.match(/^([0-9]+\\.[0-9]+)/);
                                                if (numMatch) {{
                                                    const roundedNum = Number(numMatch[1]).toFixed(1);
                                                    actualValue = actualValue.replace(numMatch[1], roundedNum);
                                                }}
                                            }}

                                            if (actualValue && typeof actualValue === 'string') {{
                                                // Placeholder 번역 처리 - 하지만 actual data를 우선 표시
                                                actualValue = actualValue.replace('[PASS]', getTranslation('modal.conditions.pass', currentLanguage));
                                                actualValue = actualValue.replace('[FAIL]', getTranslation('modal.conditions.fail', currentLanguage));
                                                actualValue = actualValue.replace('[CONSECUTIVE_FAIL]', getTranslation('modal.conditions.consecutiveFail', currentLanguage));

                                                // 조건by 단위 추가/conversion (영어 표시 개선)
                                                // 조건 1, 8, 9: % 앞에 공백 추가 "100.0%" → "100.0 %"
                                                if (cond.id === 1 || cond.id === 8 || cond.id === 9) {{
                                                    actualValue = actualValue.replace(/([0-9.]+)%/g, '$1 %');
                                                }}

                                                // 조건 2, 3, 4: "0일" → "0.0 days"
                                                if (cond.id === 2 || cond.id === 3 || cond.id === 4) {{
                                                    actualValue = actualValue.replace(/(\\d+\\.?\\d*)th/g, function(match, num) {{
                                                        if (currentLanguage === 'en') {{
                                                            return num + (parseFloat(num) === 1 ? ' day' : ' days');
                                                        }} else if (currentLanguage === 'vi') {{
                                                            return num + ' ngày';
                                                        }} else {{
                                                            return match;  // 한국어는 그대로
                                                        }}
                                                    }});
                                                }}

                                                // 조건 5: "0cases" → "0.0 PO reject"
                                                if (cond.id === 5) {{
                                                    actualValue = actualValue.replace(/(\\d+\\.?\\d*)cases/g, function(match, num) {{
                                                        if (currentLanguage === 'en') {{
                                                            return num + ' PO reject';
                                                        }} else if (currentLanguage === 'vi') {{
                                                            return num + ' PO từ chối';
                                                        }} else {{
                                                            return match;  // 한국어는 그대로
                                                        }}
                                                    }});
                                                }}

                                                // 조건 10: "400족" → "400.0 prs" (영어/베트남어에서 prs로 변경)
                                                if (cond.id === 10) {{
                                                    actualValue = actualValue.replace(/(\\d+\\.?\\d*)족/g, function(match, num) {{
                                                        if (currentLanguage === 'en' || currentLanguage === 'vi') {{
                                                            return num + ' prs';
                                                        }} else {{
                                                            return match;  // 한국어는 "족" 유지
                                                        }}
                                                    }});
                                                }}
                                            }}

                                            actualHtml = `<strong>${{actualValue}}</strong>`;
                                            badgeHtml = cond.is_met ? '<span class="badge bg-success">' + getTranslation('modal.conditions.met', currentLanguage) + '</span>' : '<span class="badge bg-danger">' + getTranslation('modal.conditions.notMet', currentLanguage) + '</span>';
                                        }}
                                        
                                        // 조건 이름 번역
                                        let condName = cond.name;
                                        if (cond.id && cond.id >= 1 && cond.id <= 10) {{
                                            condName = getTranslation('modal.tenConditions.' + cond.id, currentLanguage);
                                        }}
                                        
                                        return `
                                        <tr class="${{rowClass}}">
                                            <td>${{idx + 1}}</td>
                                            <td>${{condName}}</td>
                                            <td>${{actualHtml}}</td>
                                            <td class="text-center">${{badgeHtml}}</td>
                                        </tr>
                                        `;
                                    }}).join('')}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            // existing backdrop 제거
            const existingBackdrop = document.querySelector('.modal-backdrop');
            if (existingBackdrop) {{
                existingBackdrop.remove();
            }}

            // Bootstrap 5 modal 표시 - 더 안전한 방법
            try {{
                // existing 모달 인스턴스가 있으면 먼저 처리
                const existingModal = bootstrap.Modal.getInstance(modal);
                if (existingModal) {{
                    existingModal.dispose();
                }}

                // 새 모달 인스턴스 creation 및 표시
                const bootstrapModal = new bootstrap.Modal(modal, {{
                    backdrop: true,
                    keyboard: true,
                    focus: true
                }});
                bootstrapModal.show();
            }} catch (e) {{
                console.error('Bootstrap modal error:', e);
                // Fallback: count동으로 모달 표시
                modal.classList.add('show');
                modal.style.display = 'block';
                modal.setAttribute('aria-modal', 'true');
                modal.setAttribute('role', 'dialog');
                document.body.classList.add('modal-open');

                // count동으로 backdrop 추가
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }}
            
            // 모달 스크롤 초기화 (맨 위로)
            modalBody.scrollTop = 0;
            document.querySelector('.modal-content').scrollTop = 0;

            // 차트 그리기
            setTimeout(() => {{
                const canvas = document.getElementById(`conditionChart${{empNo}}`);
                if (canvas) {{
                    const ctx = canvas.getContext('2d');
                    
                    // existing 차트 삭제
                    if (window[`chart_${{empNo}}`]) {{
                        window[`chart_${{empNo}}`].destroy();
                    }}
                    
                    // 새 차트 creation
                    // TYPE-3 또는 조건이 없는 경우 특별 처리
                    let chartData, chartLabels, chartColors;

                    if (emp.type === 'TYPE-3') {{
                        // TYPE-3: N/A 표시
                        chartData = [1];
                        chartLabels = ['N/A - 정책적 제외'];
                        chartColors = ['#999999'];
                    }} else if (totalConditions === 0) {{
                        // 조건이 없는 경우
                        chartData = [1];
                        chartLabels = [getTranslation('modal.detailPopup.noConditions', currentLanguage)];
                        chartColors = ['#cccccc'];
                    }} else {{
                        // th반적인 경우
                        chartData = [passedConditions, Math.max(0, totalConditions - passedConditions)];
                        chartLabels = [getTranslation('modal.conditions.met', currentLanguage), getTranslation('modal.conditions.notMet', currentLanguage)];
                        chartColors = ['#28a745', '#dc3545'];
                    }}

                    window[`chart_${{empNo}}`] = new Chart(ctx, {{
                        type: 'doughnut',
                        data: {{
                            labels: chartLabels,
                            datasets: [{{
                                data: chartData,
                                backgroundColor: chartColors,
                                borderWidth: 0
                            }}]
                        }},
                        options: {{
                            responsive: false,
                            maintainAspectRatio: true,
                            plugins: {{
                                legend: {{
                                    position: 'bottom'
                                }}
                            }}
                        }}
                    }});
                }}
            }}, 100);
        }};  // window.showEmployeeDetail 함수 끝

        // REMOVED: 중복 할당 제거 (이미 위에서 window.showEmployeeDetail로 정의함)
        // window.showEmployeeDetail = showEmployeeDetail; <- 이 줄이 문제였음!

        // Validation modal 함수들을 전역으로 노출 (onclick 이벤트에서 접근 가능하도록)
        window.showValidationModal = showValidationModal;
        window.showTotalWorkingDaysDetails = showTotalWorkingDaysDetails;
        window.showZeroWorkingDaysDetails = showZeroWorkingDaysDetails;
        window.showAbsentWithoutInformDetails = showAbsentWithoutInformDetails;
        window.showMinimumDaysNotMetDetails = showMinimumDaysNotMetDetails;
        window.showAttendanceBelow88Details = showAttendanceBelow88Details;
        window.showAqlFailDetails = showAqlFailDetails;
        window.showConsecutiveAqlFailDetails = showConsecutiveAqlFailDetails;
        window.showAreaRejectRateDetails = showAreaRejectRateDetails;
        window.showLowPassRateDetails = showLowPassRateDetails;
        window.showLowInspectionQtyDetails = showLowInspectionQtyDetails;

        // 모달 닫기
        function closeModal() {{
            // 모든 차트 정리
            Object.keys(window).forEach(key => {{
                if (key.startsWith('chart_') && window[key]) {{
                    window[key].destroy();
                    delete window[key];
                }}
            }});
            document.getElementById('employeeModal').style.display = 'none';
        }}

        // Position 모달 닫기
        function closePositionModal() {{
            document.getElementById('positionModal').style.display = 'none';
        }}
        
        // 모달 외부 클릭 시 닫기
        window.onclick = function(event) {{
            const modal = document.getElementById('employeeModal');
            if (event.대상 === modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // 테이블 필터링
        function filterTable() {{
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const positionFilter = document.getElementById('positionFilter').value;
            const paymentFilter = document.getElementById('paymentFilter').value;
            
            const tbody = document.getElementById('employeeTableBody');
            tbody.innerHTML = '';
            
            employeeData.forEach(emp => {{
                const amount = parseInt(emp['{month.lower()}_incentive']);
                const isPaid = amount > 0;
                
                // 필터 조건 확인
                if (searchInput && !emp.name.toLowerCase().includes(searchInput) && !emp.emp_no.includes(searchInput)) {{
                    return;
                }}
                if (typeFilter && emp.type !== typeFilter) {{
                    return;
                }}
                if (positionFilter && emp.position !== positionFilter) {{
                    return;
                }}
                if (paymentFilter === 'paid' && !isPaid) {{
                    return;
                }}
                if (paymentFilter === 'unpaid' && isPaid) {{
                    return;
                }}
                
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                tr.onclick = () => showEmployeeDetail(emp.emp_no);
                
                // Talent Pool 멤버인 경우 특별 스타th apply
                if (emp.Talent_Pool_Member === 'Y') {{
                    tr.className = 'talent-pool-row';
                }}
                
                // Talent Pool 정보 HTML creation
                let talentPoolHTML = '-';
                if (emp.Talent_Pool_Member === 'Y') {{
                    talentPoolHTML = `
                        <div class="talent-pool-tooltip">
                            <span class="talent-pool-star">🌟</span>
                            <strong>${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND</strong>
                            <span class="tooltiptext">
                                <strong>${{getTranslation('talentPool.special', currentLanguage) || 'QIP Talent Pool'}}</strong><br>
                                ${{getTranslation('talentPool.monthlyBonus', currentLanguage) || 'month 특별 보너스'}}: ${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND<br>
                                ${{getTranslation('talentPool.period', currentLanguage) || '지급 기간'}}: 2025.07 - 2025.12
                            </span>
                        </div>
                    `;
                }}
                
                tr.innerHTML = `
                    <td>${{emp.emp_no}}</td>
                    <td>${{emp.name}}${{emp.Talent_Pool_Member === 'Y' ? '<span class="talent-pool-badge">TALENT</span>' : ''}}</td>
                    <td>${{emp.position}}</td>
                    <td><span class="type-badge type-${{emp.type.toLowerCase().replace('type-', '')}}">${{emp.type}}</span></td>
                    <td>${{parseInt(emp['{prev_month_name}_incentive'] || emp.previous_incentive || 0).toLocaleString()}}</td>
                    <td><strong>${{amount.toLocaleString()}}</strong></td>
                    <td>${{talentPoolHTML}}</td>
                    <td>${{isPaid ? '✅ ' + getTranslation('status.paid') : '❌ ' + getTranslation('status.unpaid')}}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${{emp.emp_no}}')">${{getTranslation('individual.table.detailButton')}}</button></td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        // 직급 필터 업데이트
        function updatePositionFilter() {{
            const typeFilter = document.getElementById('typeFilter').value;
            const positionSelect = document.getElementById('positionFilter');
            const currentValue = positionSelect.value;
            
            // 직급 목록 count집
            const positions = new Set();
            employeeData.forEach(emp => {{
                if (!typeFilter || emp.type === typeFilter) {{
                    positions.add(emp.position);
                }}
            }});
            
            // 옵션 업데이트
            positionSelect.innerHTML = '<option value="" id="optAllPositionsInner">' + getTranslation('individual.filters.allPositions', currentLanguage) + '</option>';
            Array.from(positions).sort().forEach(position => {{
                const option = document.createElement('option');
                option.value = position;
                option.textContent = position;
                if (position === currentValue) {{
                    option.selected = true;
                }}
                positionSelect.appendChild(option);
            }});
        }}
    </script>
</body>
</html>'''
    
    return html_content

def sync_google_drive_data(month_num, year):
    """Google Drive에서 data synchronization"""
    try:
        print("\n🔄 Google Drive data synchronization start...")
        drive_manager = GoogleDriveManager()
        
        # incentive data 다운load
        file_pattern = f"{year}year {month_num}month incentive"
        files = drive_manager.download_files(file_pattern, 'input_files')
        
        if files:
            print(f"✅ {len(files)}개 file synchronization completed")
            for file in files:
                print(f"   - {file}")
            return True
        else:
            print("⚠️ Google Drive에서 corresponding month data를 find count not found")
            return False
    except Exception as e:
        print(f"❌ Google Drive synchronization failed: {e}")
        return False

def main():
    """메인 실행 함count"""
    # 번역 file load
    load_translations()

    parser = argparse.ArgumentParser(description='integrated incentive dashboard creation')
    parser.add_argument('--month', type=int, default=8, help='month (1-12)')
    parser.add_argument('--year', type=int, default=2025, help='연도')
    parser.add_argument('--sync', action='store_true', help='Google Drive synchronization')
    args = parser.parse_args()

    print("=" * 80)
    print("integrated incentive dashboard creation - final version")
    print(f"대상: {args.year}year {args.month}month")
    print("=" * 80)

    # Google Drive synchronization (옵션)
    if args.sync:
        if not sync_google_drive_data(args.month, args.year):
            print("Google Drive synchronization failed. local file use.")

    # month 이름 conversion
    month_names = ['', 'january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
    month_name = month_names[args.month]

    # data load
    df = load_incentive_data(month_name, args.year)

    if df.empty:
        print("❌ data load failed")
        return

    # Single Source of Truth 개선: JSON cache 제거, CSV directly read
    print("📊 Single Source of Truth principle apply - CSV/Excel directly read")

    # CSV file에서 directly data creation (JSON cache use 안 함)
    excel_dashboard_data = None
    working_days = 13  # default value

    # CSV를 directly 읽어서 dashboard data 구조 creation
    # V9.1 → V9.0 → V8.02 순서로 확인 - 통일된 fallback 패턴 (2025-12-01)
    csv_file_v91 = f'output_files/output_QIP_incentive_{month_name}_{args.year}_Complete_V9.1_Complete.csv'
    csv_file_v9 = f'output_files/output_QIP_incentive_{month_name}_{args.year}_Complete_V9.0_Complete.csv'
    csv_file_v8 = f'output_files/output_QIP_incentive_{month_name}_{args.year}_Complete_V8.02_Complete.csv'
    csv_file_enhanced = f'output_files/output_QIP_incentive_{month_name}_{args.year}_final완성version_v6.0_Complete_enhanced.csv'
    csv_file = f'output_files/output_QIP_incentive_{month_name}_{args.year}_final완성version_v6.0_Complete.csv'

    # Try V9.1 version first, then V9.0, then V8.02, then enhanced, then normal
    if os.path.exists(csv_file_v91):
        csv_file = csv_file_v91
    elif os.path.exists(csv_file_v9):
        csv_file = csv_file_v9
    elif os.path.exists(csv_file_v8):
        csv_file = csv_file_v8
    elif os.path.exists(csv_file_enhanced):
        csv_file = csv_file_enhanced

    if os.path.exists(csv_file):
        try:
            # CSV directly load
            df_csv = pd.read_csv(csv_file, encoding='utf-8-sig')
            print(f"✅ CSV file directly load: {csv_file}")

            # actual 근무일count calculation - config file에서 read
            import json
            config_path = f'config_files/config_{month_name}_{args.year}.json'
            attendance_file_path = None
            config_last_updated = ""  # 데이터 신선도 표시용
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    working_days = config_data.get('working_days', 22)
                    attendance_file_path = config_data.get('file_paths', {}).get('attendance', None)
                    config_last_updated = config_data.get('last_updated', config_data.get('working_days_updated_at', ""))
                    print(f"📊 actual total 근무일count (Config based): {working_days}th")
                    print(f"🕐 Config last updated: {config_last_updated}")
            else:
                working_days = 22  # attendance data에서 calculation된 actual 값
                print(f"📊 actual total 근무일count (default value): {working_days}th")

            # attendance daily_data 및 직원by raw data creation
            daily_data = {}
            attendance_raw_data = {}  # 직원by unique 날짜 count 저장

            if attendance_file_path and os.path.exists(attendance_file_path):
                try:
                    print(f"📅 Attendance file load: {attendance_file_path}")
                    df_attendance = pd.read_csv(attendance_file_path, encoding='utf-8-sig')

                    # Work Date column이 있는지 확인
                    if 'Work Date' in df_attendance.columns:
                        # Work Date를 datetime으로 conversion하고 th자만 추출
                        df_attendance['Work Date'] = pd.to_datetime(df_attendance['Work Date'], format='%Y.%m.%d', errors='coerce')
                        df_attendance = df_attendance.dropna(subset=['Work Date'])

                        # ID No column 찾기
                        id_col = None
                        for col in ['ID No', 'ID', 'Employee No', 'Emp No']:
                            if col in df_attendance.columns:
                                id_col = col
                                break

                        # th자by 직원 count calculation
                        for _, row in df_attendance.iterrows():
                            day = row['Work Date'].day
                            if day not in daily_data:
                                daily_data[day] = {'is_working_day': True, 'count': 0}
                            daily_data[day]['count'] += 1

                            # 직원by unique 날짜 count calculation
                            if id_col and pd.notna(row[id_col]):
                                emp_no = str(row[id_col]).strip().lstrip('0').zfill(9)
                                if emp_no not in attendance_raw_data:
                                    attendance_raw_data[emp_no] = {'dates': set()}
                                attendance_raw_data[emp_no]['dates'].add(row['Work Date'].strftime('%Y-%m-%d'))

                        # set을 길이로 conversion (unique 날짜 count)
                        for emp_no in attendance_raw_data:
                            attendance_raw_data[emp_no]['uniqueDates'] = len(attendance_raw_data[emp_no]['dates'])
                            del attendance_raw_data[emp_no]['dates']  # set 제거 (JSON 직렬화 불가)

                        print(f"✅ Daily attendance data creation completed: {len(daily_data)}th")
                        print(f"✅ 직원by attendance raw data creation completed: {len(attendance_raw_data)}직원")
                    else:
                        print("⚠️ Work Date column을 find count not found.")
                except Exception as e:
                    print(f"⚠️ Attendance file load failed: {e}")
            else:
                print("⚠️ Attendance file 경로가 not exist or file이 does not exist not.")

            # dashboard_data 구조 directly creation (JSON cache 대체)
            # numpy int64를 Python int로 conversion
            employee_data = []
            for _, row in df_csv.iterrows():
                record = {}
                for key, value in row.items():
                    # numpy type을 Python 네이티브 type으로 conversion
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, (np.int64, np.int32)):
                        record[key] = int(value)
                    elif isinstance(value, (np.float64, np.float32)):
                        record[key] = float(value)
                    else:
                        record[key] = value
                employee_data.append(record)

            excel_dashboard_data = {
                'employee_data': employee_data,
                'attendance': {
                    'total_working_days': int(working_days),
                    'daily_data': daily_data
                },
                'attendance_raw_data': attendance_raw_data,  # 직원by unique 날짜 count
                'summary': {
                    'total_직원': int(len(df_csv)),
                    '직원_with_incentive': int(sum(1 for _, row in df_csv.iterrows() if row.get('Final Incentive amount', 0) > 0)),
                    'total_incentive_amount': float(df_csv['Final Incentive amount'].sum()) if 'Final Incentive amount' in df_csv.columns else 0
                }
            }
            print("✅ Single Source of Truth apply completed - JSON cache without CSV에서 directly data creation")

        except Exception as e:
            print(f"⚠️ CSV directly load failed: {e}")
            working_days = 13  # Fallback
    else:
        print(f"⚠️ CSV file이 not found: {csv_file}")
        working_days = 13  # Fallback

    # dashboard creation - Excel data를 전달
    # df_csv를 사용 (최신 데이터)
    dashboard_df = df_csv if 'df_csv' in locals() else df
    html_content = generate_dashboard_html(dashboard_df, month_name, args.year, args.month, working_days, excel_dashboard_data, config_last_updated)

    # file 저장
    # file직원 형식 변경: Incentive_Dashboard_YYYY_MM_Version_9.0.html
    output_file = f'output_files/Incentive_Dashboard_{args.year}_{args.month:02d}_Version_9.0.html'
    os.makedirs('output_files', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ dashboard creation completed: {output_file}")

    # 통계 출력 - dashboard_df 사용
    total_직원 = len(dashboard_df)
    # 동적 incentive column 찾기 - Excel 컬럼명 사용 (October_Incentive)
    incentive_col = f'{month_name.capitalize()}_Incentive'
    if incentive_col not in dashboard_df.columns:
        # 대체 column직원 시도
        print(f"⚠️ {incentive_col} column을 find count not found. use available column을 checking.")
        # 가장 최근 month의 incentive column을 찾음
        possible_cols = [col for col in dashboard_df.columns if '_incentive' in col.lower() or '_Incentive' in col]
        if possible_cols:
            incentive_col = possible_cols[-1]  # 가장 last incentive column use
            print(f"   → {incentive_col} column을 uses.")

    # Handle potential duplicate columns or Series values
    def get_incentive_value(row, col):
        val = row.get(col, 0)
        # If it's a Series (due to duplicate columns), take the first value
        if hasattr(val, 'iloc'):
            val = val.iloc[0] if len(val) > 0 else 0
        # Convert to number safely
        try:
            return int(float(val)) if pd.notna(val) else 0
        except (ValueError, TypeError):
            return 0

    paid_직원 = sum(1 for _, row in dashboard_df.iterrows() if get_incentive_value(row, incentive_col) > 0)
    total_amount = sum(get_incentive_value(row, incentive_col) for _, row in dashboard_df.iterrows())
    
    print(f"   - total 직원: {total_직원}직원")
    print(f"   - 지급 대상: {paid_직원}직원")
    print(f"   - total 지급액: {total_amount:,} VND")

if __name__ == "__main__":
    main()