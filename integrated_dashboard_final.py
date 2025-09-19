#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
통합 인센티브 대시보드 생성 시스템 - 최종 버전
dashboard_version4.html의 정확한 UI 복제
실제 인센티브 데이터 사용
Google Drive 연동 기능 포함
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime
import glob
import argparse
from src.google_drive_manager import GoogleDriveManager

# 전역 변수로 번역 데이터 저장
TRANSLATIONS = {}

def load_translations():
    """번역 파일 로드"""
    global TRANSLATIONS
    translations_file = 'config_files/dashboard_translations.json'
    try:
        with open(translations_file, 'r', encoding='utf-8') as f:
            TRANSLATIONS = json.load(f)
        print(f"✅ 번역 파일 로드 완료: {translations_file}")
        return True
    except Exception as e:
        print(f"❌ 번역 파일 로드 실패: {e}")
        # 기본값 설정
        TRANSLATIONS = {
            "languages": {"ko": "한국어", "en": "English", "vi": "Tiếng Việt"},
            "headers": {"title": {"ko": "QIP 인센티브 대시보드", "en": "QIP Incentive Dashboard", "vi": "Bảng điều khiển khen thưởng QIP"}}
        }
        return False

def get_translation(key_path, lang='ko'):
    """번역 값 가져오기 (key_path는 점으로 구분된 경로)"""
    try:
        keys = key_path.split('.')
        value = TRANSLATIONS
        for key in keys:
            value = value[key]
        return value.get(lang, value.get('ko', key_path))
    except (KeyError, AttributeError):
        return key_path

def get_month_translation(month, lang='ko'):
    """월 이름 번역"""
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
    """하위 호환성을 위한 함수 유지"""
    return get_month_translation(month, 'ko')

def determine_type_from_position(position):
    """직급에서 Type 결정"""
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
    
    # TYPE-2 positions (일반 검사 직급)
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
    """이전 월 데이터 자동 생성"""
    import random
    
    # 이전 월 계산
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
    
    # 이전 월 파일 확인
    prev_patterns = [
        f"input_files/{prev_year}년 {get_korean_month(prev_month_name)} 인센티브 지급 세부 정보.csv",
        f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_*.csv"
    ]
    
    for pattern in prev_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"✅ 이전 월({prev_month_name}) 데이터 발견: {files[0]}")
            return prev_month_name, prev_year
    
    # 이전 월 데이터가 없으면 빈 데이터로 처리
    print(f"⚠️ {prev_month_name} 데이터가 없습니다. 빈 데이터로 처리됩니다.")
    
    # 가짜 데이터를 생성하지 않고 빈 값으로 반환
    # 실제 데이터가 없을 때는 0 또는 빈 값으로 표시
    
    return prev_month_name, prev_year

def load_incentive_data(month='august', year=2025, generate_prev=True):
    """실제 인센티브 데이터 로드"""
    
    # 이전 월 데이터 생성/로드
    if generate_prev:
        prev_month_name, prev_year = generate_previous_month_data(month, year)
    
    # 가능한 파일 패턴들 - output_files를 먼저 확인
    month_str = 'august' if month == 8 else 'september' if month == 9 else str(month)
    patterns = [
        f"output_files/output_QIP_incentive_{month_str}_{year}_최종완성버전_v6.0_Complete.csv",
        f"output_files/output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv",
        f"output_files/output_QIP_incentive_{month_str}_{year}_*.csv",
        f"input_files/{year}년 {get_korean_month(month)} 인센티브 지급 세부 정보.csv"
    ]
    
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            csv_file = files[0]
            print(f"✅ 인센티브 데이터 로드: {csv_file}")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            # Position 컬럼 찾기
            position_col = None
            for col in df.columns:
                if 'POSITION' in col.upper() and '1ST' in col.upper():
                    position_col = col
                    break
                elif 'POSITION' in col.upper():
                    position_col = col
                    break
            
            # 컬럼 이름 표준화
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'employee' in col_lower and 'no' in col_lower:
                    column_mapping[col] = 'emp_no'
                elif col_lower in ['name', 'full name', 'employee name']:
                    column_mapping[col] = 'name'
                elif position_col and col == position_col:
                    column_mapping[col] = 'position'
                elif 'ROLE TYPE STD' in col:
                    column_mapping[col] = 'type'
                elif col_lower == 'type':
                    column_mapping[col] = 'type'
                elif f'{month.lower()}_incentive' in col_lower or f'{month.lower()} incentive' in col_lower:
                    column_mapping[col] = f'{month.lower()}_incentive'
                elif f'{month.capitalize()}_Incentive' in col:  # Handle capitalized month names
                    column_mapping[col] = f'{month.lower()}_incentive'
                elif 'August_Incentive' in col:  # For other months showing August data
                    column_mapping[col] = 'august_incentive'
                elif 'July_Incentive' in col:
                    column_mapping[col] = 'july_incentive'
                elif 'Previous_Incentive' in col:
                    column_mapping[col] = 'previous_incentive'
                elif col_lower == 'attendance_rate' or (col_lower == 'attendance rate'):
                    column_mapping[col] = 'attendance_rate'
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

            # 디버그: 매핑된 컬럼 확인
            print(f"✅ 컬럼 매핑 완료: {month}_incentive 컬럼 존재: {f'{month.lower()}_incentive' in df.columns}")
            if f'{month.lower()}_incentive' in df.columns:
                non_zero = (df[f'{month.lower()}_incentive'] > 0).sum()
                print(f"   - {month}_incentive 값이 0이 아닌 직원: {non_zero}명")

            # Type 컬럼이 없으면 position에서 결정
            if 'type' not in df.columns and 'position' in df.columns:
                df['type'] = df['position'].apply(determine_type_from_position)
                print(f"✅ Type 자동 결정 (position 기반): TYPE-1 {(df['type']=='TYPE-1').sum()}명, TYPE-2 {(df['type']=='TYPE-2').sum()}명, TYPE-3 {(df['type']=='TYPE-3').sum()}명")
            elif 'type' in df.columns:
                # Type 통계 출력
                type_counts = df['type'].value_counts()
                print(f"✅ Type 정보 로드: TYPE-1 {type_counts.get('TYPE-1', 0)}명, TYPE-2 {type_counts.get('TYPE-2', 0)}명, TYPE-3 {type_counts.get('TYPE-3', 0)}명")
            
            # 필수 컬럼 확인 및 기본값 설정
            required_columns = ['emp_no', 'name', 'position', 'type', f'{month.lower()}_incentive']
            for col in required_columns:
                if col not in df.columns:
                    if col == f'{month.lower()}_incentive':
                        # 해당 월의 Incentive 컬럼 찾기
                        for orig_col in df.columns:
                            if month.lower() in orig_col.lower() and 'incentive' in orig_col.lower():
                                df[col] = df[orig_col]
                                break
                    elif col == 'type':
                        df[col] = 'TYPE-2'  # 기본값
                    else:
                        df[col] = ''
            
            # 조건 컬럼 추가 (기본값)
            condition_columns = ['condition1', 'condition2', 'condition3', 'condition4',
                               'condition5', 'condition6', 'condition7', 'condition8',
                               'condition9', 'condition10']
            for col in condition_columns:
                if col not in df.columns:
                    df[col] = 'no'
            
            # 담당구역 매핑 로드
            area_mapping = load_area_mapping()
            
            # AQL 데이터 로드 및 병합
            aql_file = f"input_files/AQL history/1.HSRG AQL REPORT-{month.upper()}.{year}.csv"
            if os.path.exists(aql_file):
                print(f"✅ AQL 데이터 로드: {aql_file}")
                aql_df = pd.read_csv(aql_file, encoding='utf-8-sig')
                
                # Employee NO 기준으로 FAIL 집계
                aql_df['EMPLOYEE NO'] = aql_df['EMPLOYEE NO'].fillna(0).astype(float).astype(int).astype(str).str.zfill(9)
                
                # 각 직원별 실패 건수 계산
                aql_summary = aql_df[aql_df['RESULT'] == 'FAIL'].groupby('EMPLOYEE NO').size().reset_index(name='aql_failures')
                aql_summary.columns = ['emp_no', 'aql_failures']
                
                # Building별 통계 계산
                if 'BUILDING' in aql_df.columns:
                    building_stats = aql_df.groupby('BUILDING')['RESULT'].apply(
                        lambda x: (x == 'FAIL').sum() / len(x) * 100
                    ).to_frame('area_reject_rate')
                    
                    total_reject_rate = (aql_df['RESULT'] == 'FAIL').mean() * 100
                    
                    # 3개월 연속 실패 체크
                    building_consecutive_fail = check_consecutive_failures(
                        month, year, 'BUILDING', 'input_files/AQL history'
                    )
                    
                    # 직원별 담당구역 매핑 및 계산
                    if area_mapping:
                        emp_area_stats = [
                            calculate_employee_area_stats(
                                str(emp_no).zfill(9), area_mapping, building_stats, 
                                building_consecutive_fail, total_reject_rate, aql_df
                            )
                            for emp_no in df['emp_no'].unique()
                        ]
                    
                    # DataFrame으로 변환
                    if emp_area_stats:
                        emp_area_df = pd.DataFrame(emp_area_stats)
                        aql_summary = aql_summary.merge(emp_area_df, on='emp_no', how='left')
                    
                    # NaN 값 처리
                    if 'area_reject_rate' not in aql_summary.columns:
                        aql_summary['area_reject_rate'] = 0
                    if 'area_consecutive_fail' not in aql_summary.columns:
                        aql_summary['area_consecutive_fail'] = 'NO'
                    
                    aql_summary['area_reject_rate'] = aql_summary['area_reject_rate'].fillna(0)
                    aql_summary['area_consecutive_fail'] = aql_summary['area_consecutive_fail'].fillna('NO')
                
                # 개인별 3개월 연속 실패 체크
                continuous_fail_dict = check_consecutive_failures(
                    month, year, 'EMPLOYEE NO', 'input_files/AQL history', is_employee=True
                )
                
                # DataFrame과 병합
                df['emp_no'] = df['emp_no'].astype(str).str.zfill(9)
                df = df.merge(aql_summary, on='emp_no', how='left')
                
                # NaN 값을 0으로 채우기
                df['aql_failures'] = df['aql_failures'].fillna(0).astype(int)
                df['area_reject_rate'] = df['area_reject_rate'].fillna(0)
                df['area_consecutive_fail'] = df['area_consecutive_fail'].fillna('NO')
                
                # 3개월 연속 실패 정보 추가
                df['continuous_fail'] = df['emp_no'].map(continuous_fail_dict).fillna('NO')
                
                print(f"✅ AQL 데이터 병합 완료: {len(aql_summary)}명 실패 기록")
                print(f"   - 팀/구역 reject rate 데이터 포함")
            else:
                print(f"⚠️ AQL 데이터 파일이 없습니다: {aql_file}")
                df['aql_failures'] = 0
                df['continuous_fail'] = 'NO'
                df['area_reject_rate'] = 0
                df['area_consecutive_fail'] = 'NO'
            
            # 5PRS 데이터 로드 및 병합
            prs_file = f"input_files/5prs data {month.lower()}.csv"
            if os.path.exists(prs_file):
                print(f"✅ 5PRS 데이터 로드: {prs_file}")
                prs_df = pd.read_csv(prs_file, encoding='utf-8-sig')
                
                # TQC ID 기준으로 집계
                prs_summary = prs_df.groupby('TQC ID').agg({
                    'Valiation Qty': 'sum',
                    'Pass Qty': 'sum'
                }).reset_index()
                
                prs_summary.columns = ['emp_no', 'validation_qty', 'pass_qty']
                prs_summary['emp_no'] = prs_summary['emp_no'].astype(str)
                
                # Pass rate 계산
                prs_summary['pass_rate'] = 0.0
                mask = prs_summary['validation_qty'] > 0
                prs_summary.loc[mask, 'pass_rate'] = (prs_summary.loc[mask, 'pass_qty'] / prs_summary.loc[mask, 'validation_qty']) * 100
                
                # DataFrame과 병합
                df['emp_no'] = df['emp_no'].astype(str)
                df = df.merge(prs_summary[['emp_no', 'pass_rate', 'validation_qty']], 
                            on='emp_no', how='left')
                
                # NaN 값을 0으로 채우기
                df['pass_rate'] = df['pass_rate'].fillna(0)
                df['validation_qty'] = df['validation_qty'].fillna(0)
                
                print(f"✅ 5PRS 데이터 병합 완료: {len(prs_summary)}명 데이터")
            else:
                print(f"⚠️ 5PRS 데이터 파일이 없습니다: {prs_file}")
                df['pass_rate'] = 0
                df['validation_qty'] = 0
            
            # 출근 관련 컬럼 - Excel 데이터를 그대로 사용 (하드코딩 제거)
            # Excel이 단일 진실 소스(Single Source of Truth)
            missing_columns = []

            if 'attendance_rate' not in df.columns:
                missing_columns.append('attendance_rate')
                # attendance_rate를 실제 데이터로 계산
                if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
                    df['attendance_rate'] = (df['Actual Working Days'] / df['Total Working Days'] * 100).fillna(0)
                    df.loc[df['Total Working Days'] == 0, 'attendance_rate'] = 0
                else:
                    df['attendance_rate'] = 0  # 데이터 없음을 명시적으로 표시
            if 'actual_working_days' not in df.columns:
                missing_columns.append('actual_working_days')
                df['actual_working_days'] = 0  # 데이터 없음을 명시적으로 표시
            if 'unapproved_absences' not in df.columns:
                missing_columns.append('unapproved_absences')
                df['unapproved_absences'] = 0  # 데이터 없음을 명시적으로 표시
            if 'absence_rate' not in df.columns:
                missing_columns.append('absence_rate')
                df['absence_rate'] = 0  # 데이터 없음을 명시적으로 표시

            if missing_columns:
                print(f"⚠️ 누락된 출근 관련 컬럼: {missing_columns}")
                print("   → Excel에서 데이터를 확인하세요. 하드코딩 없이 0으로 표시됩니다.")
            
            # 이전 달 인센티브 로드
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

            print(f"✅ 이전 월 계산: {month} → {prev_month_name}")
            
            # 모든 직원의 7월 인센티브는 JSON 설정 파일에서 로드
            july_incentive_data = {}
            if month.lower() == 'august' and os.path.exists("config_files/july_incentive_all_employees.json"):
                try:
                    with open("config_files/july_incentive_all_employees.json", 'r', encoding='utf-8') as f:
                        july_data = json.load(f)
                        # JSON에서 모든 직원의 7월 인센티브 정보 추출
                        for emp_id, emp_info in july_data.get('employees', {}).items():
                            july_incentive_data[emp_id] = emp_info.get('july_incentive', 0)
                        print(f"✅ 7월 인센티브 JSON 설정 로드: {len(july_incentive_data)}명의 데이터")
                except Exception as e:
                    print(f"⚠️ JSON 설정 파일 로드 실패: {e}")
            
            # 이전 월 데이터 로드 시도 (다른 직급을 위해)
            prev_patterns = [
                f"input_files/{prev_year}년 {get_korean_month(prev_month_name)} 인센티브 지급 세부 정보.csv",
                f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_*.csv"
            ]
            
            prev_df = pd.DataFrame()
            for pattern in prev_patterns:
                prev_files = glob.glob(pattern)
                if prev_files:
                    try:
                        prev_df = pd.read_csv(prev_files[0], encoding='utf-8-sig')
                        print(f"✅ {prev_month_name} 인센티브 데이터 로드: {prev_files[0]}")
                        break
                    except:
                        pass
            
            # 이전 월 데이터와 병합
            if not prev_df.empty:
                # 직원번호를 기준으로 이전 월 인센티브 매칭
                for col in prev_df.columns:
                    if 'employee' in col.lower() and 'no' in col.lower():
                        prev_df.rename(columns={col: 'emp_no'}, inplace=True)
                        break
                
                # 이전 월 인센티브 컬럼 찾기
                incentive_col_found = False
                for col in prev_df.columns:
                    col_lower = col.lower()
                    # 다양한 형식 처리: August_Incentive, august_incentive, Final Incentive amount 등
                    if (f'{prev_month_name.lower()}_incentive' in col_lower or
                        f'{prev_month_name.lower()} incentive' in col_lower or
                        f'{prev_month_name.capitalize()}_Incentive' in col or
                        (prev_month_name.lower() == 'august' and 'August_Incentive' in col)):
                        prev_df.rename(columns={col: f'{prev_month_name}_incentive'}, inplace=True)
                        incentive_col_found = True
                        print(f"   - 이전 월 인센티브 컬럼 찾음: {col} → {prev_month_name}_incentive")
                        break

                # Final Incentive amount를 대체로 사용
                if not incentive_col_found and 'Final Incentive amount' in prev_df.columns:
                    prev_df.rename(columns={'Final Incentive amount': f'{prev_month_name}_incentive'}, inplace=True)
                    print(f"   - Final Incentive amount를 {prev_month_name}_incentive로 사용")
                
                # 사번 기준으로 병합
                if 'emp_no' in prev_df.columns and f'{prev_month_name}_incentive' in prev_df.columns:
                    prev_df['emp_no'] = prev_df['emp_no'].astype(str)
                    df['emp_no'] = df['emp_no'].astype(str)
                    
                    # 이전 월 인센티브 데이터 병합
                    df = df.merge(
                        prev_df[['emp_no', f'{prev_month_name}_incentive']], 
                        on='emp_no', 
                        how='left',
                        suffixes=('', '_prev')
                    )
                    
                    # NaN 값을 '0'으로 대체
                    df[f'{prev_month_name}_incentive'] = df[f'{prev_month_name}_incentive'].fillna('0')
                    print(f"✅ {prev_month_name} 인센티브 데이터 병합 완료")
                else:
                    df[f'{prev_month_name}_incentive'] = '0'
            else:
                df[f'{prev_month_name}_incentive'] = '0'
            
            # 다른 월 인센티브도 기본값 설정
            df['june_incentive'] = df.get('june_incentive', '0')
            df['july_incentive'] = df.get('july_incentive', '0')
            
            # 모든 직원의 7월 인센티브를 JSON 설정에서 덮어쓰기
            if july_incentive_data and month.lower() == 'august':
                updated_count = 0
                for idx, row in df.iterrows():
                    emp_id = str(row['emp_no'])
                    if emp_id in july_incentive_data:
                        df.at[idx, 'july_incentive'] = str(july_incentive_data[emp_id])
                        updated_count += 1
                print(f"✅ 7월 인센티브 JSON 설정 적용 완료: {updated_count}명 업데이트")
            
            # 입사일 및 퇴사일 필터링 (해당 월 기준)
            print(f"✅ 직원 데이터 필터링 중...")

            # 해당 월의 날짜 범위 계산
            month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                           'july', 'august', 'september', 'october', 'november', 'december']
            month_num = month_names.index(month.lower()) + 1
            month_start = pd.to_datetime(f'{year}-{month_num:02d}-01')

            # 다음 달 1일 계산 (월말 계산용)
            import calendar
            last_day = calendar.monthrange(year, month_num)[1]
            month_end = pd.to_datetime(f'{year}-{month_num:02d}-{last_day}')

            initial_count = len(df)

            # 1. 퇴사일 필터링 (해당 월 1일 이전 퇴사자 제외)
            if 'Stop working Date' in df.columns:
                df['resignation_date'] = pd.to_datetime(df['Stop working Date'], errors='coerce')
                before_month = df[df['resignation_date'] < month_start]
                df = df[(df['resignation_date'] >= month_start) | (df['resignation_date'].isna())]

                if len(before_month) > 0:
                    print(f"   - {get_korean_month(month)} 이전 퇴사자 {len(before_month)}명 제외")

            # 2. 입사일 필터링 (해당 월 이후 입사자 제외)
            if 'Entrance Date' in df.columns:
                df['entrance_date'] = pd.to_datetime(df['Entrance Date'], errors='coerce')
                after_month = df[df['entrance_date'] > month_end]
                df = df[(df['entrance_date'] <= month_end) | (df['entrance_date'].isna())]

                if len(after_month) > 0:
                    print(f"   - {get_korean_month(month)} 이후 입사 예정자 {len(after_month)}명 제외")

            print(f"   - {get_korean_month(month)} 인센티브 대상자: {len(df)}명 (전체 {initial_count}명 중)")
            
            print(f"✅ {len(df)}명의 직원 데이터 로드 ({get_korean_month(month)} 기준)")
            return df
            
    print("❌ 인센티브 데이터 파일을 찾을 수 없습니다")
    return pd.DataFrame()

def load_condition_matrix():
    """조건 매트릭스 JSON 파일 로드"""
    try:
        with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        print("⚠️ 조건 매트릭스 파일을 찾을 수 없습니다. 기본 설정 사용")
        return None

def load_area_mapping():
    """담당구역 매핑 JSON 파일 로드"""
    try:
        with open('config_files/auditor_trainer_area_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        print("⚠️ 담당구역 매핑 파일을 찾을 수 없습니다.")
        return None

def get_applicable_conditions(position, type_name, condition_matrix):
    """직급과 타입에 따른 적용 조건 가져오기"""
    if not condition_matrix:
        # 기본값
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
    
    # 기본값 반환
    return type_matrix.get('default', {}).get('applicable_conditions', [1, 2, 3, 4])

def evaluate_conditions(emp_data, condition_matrix):
    """직원 데이터에 대한 조건 평가 - Excel 데이터 우선 사용"""
    if not condition_matrix:
        return []

    conditions = condition_matrix.get('conditions', {})
    type_name = emp_data.get('type', 'TYPE-2')

    # TYPE-3: 모든 조건 N/A
    if type_name == 'TYPE-3':
        return [create_na_result(cond_id, conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}'))
                for cond_id in range(1, 11)]

    results = []

    # Excel에서 조건 결과 가져오기 (있으면 사용, 없으면 자체 계산)
    condition_names = [
        'attendance_rate', 'unapproved_absence', 'actual_working_days', 'minimum_days',
        'aql_personal_failure', 'aql_continuous', 'aql_team_area', 'area_reject',
        '5prs_pass_rate', '5prs_inspection_qty'
    ]

    for cond_id in range(1, 11):
        cond_col = f'cond_{cond_id}_{condition_names[cond_id-1]}'

        # Excel에 조건 평가 결과가 있으면 사용
        if cond_col in emp_data:
            excel_result = emp_data.get(cond_col, 'N/A')
            value_col = f'cond_{cond_id}_value'
            value = emp_data.get(value_col, '')

            if excel_result == 'PASS':
                # 조건별로 적절한 표시 값 설정
                if cond_id == 7:  # 팀/구역 AQL
                    actual_display = '통과' if value == 'NO' else str(value)
                else:
                    actual_display = str(value) if value else '통과'

                results.append({
                    'id': cond_id,
                    'name': conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}'),
                    'is_met': True,
                    'actual': actual_display,
                    'is_na': False
                })
            elif excel_result == 'FAIL':
                # 조건별로 적절한 표시 값 설정
                if cond_id == 7:  # 팀/구역 AQL
                    actual_display = '실패' if value == 'YES' else str(value)
                else:
                    actual_display = str(value) if value else '실패'

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
            # Excel에 없으면 기존 자체 계산 로직 사용 (fallback)
            applicable = get_applicable_conditions(emp_data.get('position', ''), type_name, condition_matrix)

            # 조건 평가 함수 매핑 (기존 로직 유지)
            evaluators = {
                1: lambda d: (d.get('attendance_rate', 0) >= 88, f"{d.get('attendance_rate', 0):.1f}%"),
                2: lambda d: (d.get('unapproved_absences', 0) <= 2, f"{d.get('unapproved_absences', 0)}일"),
                3: lambda d: (d.get('actual_working_days', 0) > 0, f"{d.get('actual_working_days', 0)}일"),
                4: lambda d: (d.get('actual_working_days', 0) >= 12, f"{d.get('actual_working_days', 0)}일"),
                5: lambda d: (d.get('aql_failures', 0) == 0, f"{d.get('aql_failures', 0)}건"),
                6: lambda d: (d.get('continuous_fail', 'NO') != 'YES', '통과' if d.get('continuous_fail', 'NO') != 'YES' else '실패'),
                7: lambda d: (d.get('area_consecutive_fail', 'NO') != 'YES', '통과' if d.get('area_consecutive_fail', 'NO') != 'YES' else '3개월 연속 실패'),
                8: lambda d: evaluate_area_reject(d),
                9: lambda d: (d.get('pass_rate', 0) >= 95, f"{d.get('pass_rate', 0):.1f}%"),
                10: lambda d: (d.get('validation_qty', 0) >= 100, f"{d.get('validation_qty', 0)}족")
            }

            if cond_id not in applicable:
                results.append(create_na_result(cond_id, conditions.get(str(cond_id), {}).get('description', f'조건 {cond_id}')))
            else:
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
    """N/A 결과 생성 헬퍼"""
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

def check_consecutive_failures(month, year, group_col, data_path, is_employee=False):
    """3개월 연속 실패 체크 (통합 함수)"""
    months_map = {
        'august': ['JUNE', 'JULY', 'AUGUST'],
        'july': ['MAY', 'JUNE', 'JULY']
    }
    months_to_check = months_map.get(month.lower(), [])
    
    if not months_to_check:
        return {}
    
    monthly_fails = {}
    for check_month in months_to_check:
        check_file = f"{data_path}/1.HSRG AQL REPORT-{check_month}.{year}.csv"
        if os.path.exists(check_file):
            month_df = pd.read_csv(check_file, encoding='utf-8-sig')
            
            if is_employee:
                month_df['EMPLOYEE NO'] = month_df['EMPLOYEE NO'].fillna(0).astype(float).astype(int).astype(str).str.zfill(9)
                fails = month_df[month_df['RESULT'] == 'FAIL'].groupby('EMPLOYEE NO').size()
                monthly_fails[check_month] = set(fails[fails > 0].index)
            else:
                if group_col in month_df.columns:
                    fails = month_df[month_df['RESULT'] == 'FAIL'][group_col].unique()
                    monthly_fails[check_month] = set(fails)
    
    # 3개월 모두 실패한 항목 찾기
    if len(monthly_fails) == 3:
        consecutive_fails = set.intersection(*monthly_fails.values())
        return {item: 'YES' for item in consecutive_fails}
    
    return {}

def calculate_employee_area_stats(emp_no_str, area_mapping, building_stats, 
                                 building_consecutive_fail, total_reject_rate, aql_df):
    """직원별 담당구역 통계 계산"""
    emp_stats = {'emp_no': emp_no_str}
    
    # MODEL MASTER
    if emp_no_str in area_mapping.get('model_master', {}).get('employees', {}):
        emp_stats['area_reject_rate'] = total_reject_rate
        emp_stats['area_consecutive_fail'] = 'YES' if any(v == 'YES' for v in building_consecutive_fail.values()) else 'NO'
    
    # AUDIT & TRAINING
    elif emp_no_str in area_mapping.get('auditor_trainer_areas', {}):
        emp_info = area_mapping['auditor_trainer_areas'][emp_no_str]
        for condition in emp_info.get('conditions', []):
            for filter_item in condition.get('filters', []):
                if filter_item.get('column') == 'BUILDING':
                    building = filter_item.get('value')
                    emp_stats['area_reject_rate'] = building_stats.get(building, {}).get('area_reject_rate', 0) if isinstance(building_stats, dict) else building_stats.loc[building, 'area_reject_rate'] if building in building_stats.index else 0
                    emp_stats['area_consecutive_fail'] = building_consecutive_fail.get(building, 'NO')
                    break
    
    # 기타 직원
    else:
        emp_df = aql_df[aql_df['EMPLOYEE NO'] == emp_no_str]
        if not emp_df.empty and 'BUILDING' in emp_df.columns:
            emp_building = emp_df['BUILDING'].iloc[0]
            if emp_building and emp_building in building_stats.index:
                emp_stats['area_reject_rate'] = building_stats.loc[emp_building, 'area_reject_rate']
                emp_stats['area_consecutive_fail'] = building_consecutive_fail.get(emp_building, 'NO')
            else:
                emp_stats['area_reject_rate'] = 0
                emp_stats['area_consecutive_fail'] = 'NO'
        else:
            emp_stats['area_reject_rate'] = 0
            emp_stats['area_consecutive_fail'] = 'NO'
    
    return emp_stats

def generate_dashboard_html(df, month='august', year=2025, month_num=8):
    """dashboard_version4.html과 완전히 동일한 대시보드 생성"""

    # 이전 월 계산
    month_map = {
        'january': 0, 'february': 1, 'march': 2, 'april': 3,
        'may': 4, 'june': 5, 'july': 6, 'august': 7,
        'september': 8, 'october': 9, 'november': 10, 'december': 11
    }
    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']

    # 한국어 월 이름 매핑
    month_kor_map = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }
    month_kor = month_kor_map.get(month.lower(), f'{month_num}월')

    current_month_num = month_map.get(month.lower(), 7)
    prev_month_name = month_names[current_month_num - 1] if current_month_num > 0 else 'december'
    prev_year = year if current_month_num > 0 else year - 1

    # 조건 매트릭스 로드
    condition_matrix = load_condition_matrix()

    # 메타데이터 파일 로드
    metadata = {}
    metadata_file = f"output_files/output_QIP_incentive_{month}_{year}_metadata.json"
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            print(f"✅ 메타데이터 로드 완료: {metadata_file}")
    else:
        print(f"⚠️ 메타데이터 파일이 없습니다: {metadata_file}")

    # Basic manpower 데이터 로드하여 보스 정보 보완
    basic_df = None
    basic_file = f'input_files/basic manpower data {month}.csv'
    if os.path.exists(basic_file):
        try:
            basic_df = pd.read_csv(basic_file, encoding='utf-8-sig')
            # 데이터 정리
            basic_df = basic_df.dropna(subset=['Employee No', 'Full Name'], how='all')
            basic_df = basic_df[basic_df['Employee No'].notna()]

            # Employee No를 정수로 변환 후 문자열로 (소수점 제거)
            basic_df['Employee No'] = basic_df['Employee No'].apply(lambda x: str(int(float(x))) if pd.notna(x) and x != '' else '')

            # MST direct boss name도 동일하게 처리
            basic_df['MST direct boss name'] = basic_df['MST direct boss name'].apply(
                lambda x: str(int(float(x))) if pd.notna(x) and x != '' and x != 0 else ''
            )

            print(f"✅ Basic manpower 데이터 로드 완료: {len(basic_df)} 직원")
        except Exception as e:
            print(f"⚠️ Basic manpower 데이터 로드 실패: {e}")

    # 데이터 준비
    employees = []
    for _, row in df.iterrows():
        # Convert Series to dict
        row_dict = row.to_dict()

        # Employee No 가져오기
        emp_no = str(row_dict.get('emp_no', ''))

        # Basic manpower에서 보스 정보 가져오기
        boss_id = ''
        boss_name = ''
        if basic_df is not None and emp_no:
            # emp_no에서 .0 제거 (혹시 있다면)
            emp_no_clean = emp_no.replace('.0', '') if '.0' in emp_no else emp_no
            basic_row = basic_df[basic_df['Employee No'] == emp_no_clean]
            if not basic_row.empty:
                boss_id = str(basic_row['MST direct boss name'].iloc[0]) if pd.notna(basic_row['MST direct boss name'].iloc[0]) else ''
                boss_name = str(basic_row['direct boss name'].iloc[0]) if pd.notna(basic_row['direct boss name'].iloc[0]) else ''
                # nan, 0, 0.0, 빈 문자열 등을 빈 문자열로 처리
                if boss_id in ['nan', '0', '0.0', '']:
                    boss_id = ''
                if boss_name in ['nan', '0', '0.0', '']:
                    boss_name = ''

        emp = {
            'emp_no': emp_no,
            'name': str(row_dict.get('name', '')),
            'position': str(row_dict.get('position', '')),
            'type': str(row_dict.get('type', 'TYPE-2')),
            'boss_id': boss_id,  # Basic manpower에서 가져온 상사 ID
            'boss_name': boss_name,  # Basic manpower에서 가져온 상사 이름
            # 동적 월 인센티브 매핑
            f'{month.lower()}_incentive': str(row_dict.get(f'{month.lower()}_incentive', '0')),  # 현재 월 인센티브
            f'{prev_month_name.lower()}_incentive': str(row_dict.get(f'{prev_month_name.lower()}_incentive', '0')),  # 이전 월 인센티브
            # 호환성을 위해 추가
            'august_incentive': str(row_dict.get('august_incentive', '0')) if 'august_incentive' in row_dict else '0',
            'july_incentive': str(row_dict.get('july_incentive', '0')) if 'july_incentive' in row_dict else '0',
            'september_incentive': str(row_dict.get('september_incentive', '0')) if 'september_incentive' in row_dict else '0',
            'june_incentive': str(row_dict.get('june_incentive', '0')),
            'attendance_rate': float(row_dict.get('attendance_rate', 0)),
            'actual_working_days': int(row_dict.get('actual_working_days', 0)),
            'unapproved_absences': int(row_dict.get('unapproved_absences', 0)),
            'absence_rate': float(row_dict.get('absence_rate', 0)),
            'condition1': str(row_dict.get('condition1', 'no')),
            'condition2': str(row_dict.get('condition2', 'no')),
            'condition3': str(row_dict.get('condition3', 'no')),
            'condition4': str(row_dict.get('condition4', 'no')),
            'aql_failures': int(row_dict.get('aql_failures', 0)),
            'continuous_fail': str(row_dict.get('continuous_fail', 'NO')),
            'area_reject_rate': float(row_dict.get('area_reject_rate', 0)),  # 이 값은 metadata에서 덮어씌워짐
            'area_consecutive_fail': str(row_dict.get('area_consecutive_fail', 'NO')),
            'pass_rate': float(row_dict.get('pass_rate', 0)),
            'validation_qty': int(row_dict.get('validation_qty', 0)),
            'Talent_Pool_Member': str(row_dict.get('Talent_Pool_Member', 'N')),
            'Talent_Pool_Bonus': int(row_dict.get('Talent_Pool_Bonus', 0))
        }

        # 조건 관련 컬럼 추가 (cond_1 ~ cond_10)
        for cond_id in range(1, 11):
            condition_names = [
                'attendance_rate', 'unapproved_absence', 'actual_working_days', 'minimum_days',
                'aql_personal_failure', 'aql_continuous', 'aql_team_area', 'area_reject',
                '5prs_pass_rate', '5prs_inspection_qty'
            ]
            cond_col = f'cond_{cond_id}_{condition_names[cond_id-1]}'
            value_col = f'cond_{cond_id}_value'
            threshold_col = f'cond_{cond_id}_threshold'

            # CSV에서 조건 평가 결과와 값 가져오기
            if cond_col in row_dict:
                emp[cond_col] = row_dict[cond_col]
            if value_col in row_dict:
                emp[value_col] = row_dict[value_col]
            if threshold_col in row_dict:
                emp[threshold_col] = row_dict[threshold_col]
        
        # metadata에서 area_reject_rate 가져오기
        emp_no = str(emp['emp_no']).zfill(9)
        if emp_no in metadata:
            emp_metadata = metadata[emp_no]
            if 'conditions' in emp_metadata and 'aql' in emp_metadata['conditions']:
                if 'area_reject_rate' in emp_metadata['conditions']['aql']:
                    emp['area_reject_rate'] = float(emp_metadata['conditions']['aql']['area_reject_rate'].get('value', 0))
        
        # 조건 평가 결과 추가
        emp['condition_results'] = evaluate_conditions(emp, condition_matrix)

        # 실패 사유 표시를 위한 조건 필드 추가 - CSV에서 직접 가져오기
        emp['attendancy condition 1 - acctual working days is zero'] = str(row_dict.get('attendancy condition 1 - acctual working days is zero', 'no'))
        emp['attendancy condition 2 - unapproved Absence Day is more than 2 days'] = str(row_dict.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'no'))
        emp['attendancy condition 3 - absent % is over 12%'] = str(row_dict.get('attendancy condition 3 - absent % is over 12%', 'no'))
        emp['attendancy condition 4 - minimum working days'] = str(row_dict.get('attendancy condition 4 - minimum working days', 'no'))

        # AQL 조건 필드 추가
        emp['aql condition 7 - team/area fail AQL'] = str(row_dict.get('aql condition 7 - team/area fail AQL', 'no'))
        emp['September AQL Failures'] = int(row_dict.get('September AQL Failures', row_dict.get('aql_failures', 0)))
        emp['Continuous_FAIL'] = str(row_dict.get('Continuous_FAIL', row_dict.get('continuous_fail', 'NO')))

        # 5PRS 조건 필드 추가
        emp['5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%'] = str(row_dict.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%', 'yes'))
        emp['5prs condition 2 - Total Valiation Qty is zero'] = str(row_dict.get('5prs condition 2 - Total Valiation Qty is zero', 'no'))

        # conditions_pass_rate 필드 추가
        emp['conditions_pass_rate'] = float(row_dict.get('conditions_pass_rate', 0))
        emp['conditions_passed'] = int(row_dict.get('conditions_passed', 0))
        emp['conditions_applicable'] = int(row_dict.get('conditions_applicable', 0))

        # Working Days 필드 추가
        emp['Working Days'] = int(row_dict.get('actual_working_days', 0))

        employees.append(emp)
    
    # 통계 계산
    total_employees = len(employees)
    # 현재 월 인센티브 필드 이름
    current_month_field = f'{month.lower()}_incentive'
    paid_employees = sum(1 for e in employees if int(float(e.get(current_month_field, '0') or '0')) > 0)
    total_amount = sum(int(float(e.get(current_month_field, '0') or '0')) for e in employees)
    payment_rate = (paid_employees / total_employees * 100) if total_employees > 0 else 0
    
    # Type별 통계
    type_stats = {}
    for emp in employees:
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
    
    # 직원 데이터 JSON
    employees_json = json.dumps(employees, ensure_ascii=False)

    # Position matrix 데이터 로드
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

    # 보고서 타입 결정 (중간 vs 최종)
    is_interim_report = current_day < 20
    report_type_ko = '중간 점검용' if is_interim_report else '최종'
    report_type_en = 'Interim' if is_interim_report else 'Final'
    report_type_vi = 'Tạm thời' if is_interim_report else 'Cuối cùng'

    # 해당 월의 마지막 날 계산
    import calendar
    # month_num is the actual month number passed from main
    month_last_day = calendar.monthrange(year, month_num)[1]

    # 실제 데이터 범위 가져오기
    try:
        from src.get_actual_data_range import get_all_data_ranges
        data_ranges = get_all_data_ranges(month, year)

        # 각 데이터 타입별 실제 범위
        att_min, att_max = data_ranges.get('attendance', (None, None))
        inc_min, inc_max = data_ranges.get('incentive', (None, None))
        aql_min, aql_max = data_ranges.get('aql', (None, None))
        prs_min, prs_max = data_ranges.get('5prs', (None, None))

        # 출근 데이터 범위 포맷팅
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

        # 5PRS 데이터 범위 포맷팅
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

        # AQL 데이터 범위 포맷팅
        if aql_min is not None and aql_max is not None:
            aql_start_str = aql_min.strftime('%d')
            aql_end_str = aql_max.strftime('%d')
        else:
            aql_start_str = '01'
            aql_end_str = f'{month_last_day:02d}'

        # 인센티브 데이터 범위 포맷팅
        if inc_min is not None and inc_max is not None:
            incentive_start_str = inc_min.strftime('%d')
            incentive_end_str = inc_max.strftime('%d')
        else:
            incentive_start_str = '01'
            incentive_end_str = f'{month_last_day:02d}'

    except Exception as e:
        # 에러 발생 시 기본값 사용 (월 전체)
        print(f"⚠️ 실제 데이터 범위 가져오기 실패: {e}")
        attendance_start_str = '01'
        attendance_end_str = f'{month_last_day:02d}'
        prs_start_str = '01'
        prs_end_str = f'{month_last_day:02d}'
        aql_start_str = '01'
        aql_end_str = f'{month_last_day:02d}'
        incentive_start_str = '01'
        incentive_end_str = f'{month_last_day:02d}'

    # JavaScript용 번역 데이터 생성
    translations_js = json.dumps(TRANSLATIONS, ensure_ascii=False, indent=2)
    
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 계산 결과 - {year}년 {get_korean_month(month)}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Bootstrap JavaScript Bundle with Popper (필수!) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            background: #f5f5f5;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        
        /* Talent Pool 강조 스타일 */
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

        /* 보고서 타입 알림 */
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        
        /* 지급 상태 스타일 */
        .payment-status {{
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            height: 100%;
        }}
        
        .payment-status.paid {{
            background: #d4edda;
            color: #155724;
        }}
        
        .payment-status.unpaid {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .payment-status i {{
            font-size: 3rem;
            margin-bottom: 10px;
            display: block;
        }}
        
        /* 조건 테이블 스타일 */
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px 12px 0 0;
            flex: 0 0 auto; /* 고정 높이 */
            min-height: 60px;
            max-height: 60px;
        }}
        
        .modal-body {{
            padding: 30px;
            overflow-y: auto; /* 본문만 스크롤 */
            overflow-x: hidden; /* 가로 스크롤 방지 */
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
        
        /* Type 요약 테이블 스타일 */
        .avg-header {{
            text-align: center;
            background: #f3f4f6;
        }}
        
        .sub-header {{
            font-size: 0.9em;
            font-weight: 500;
            background: #f9fafb;
        }}

        /* 모달 관련 스타일 수정 */
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
            z-index: 1050 !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
        }}

        .modal.show .modal-dialog {{
            z-index: 1056 !important;
        }}

        /* 새로운 접이식 조직도 스타일 */
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

        /* 연결선 스타일 */
        .collapsible-tree li::before {{
            content: '';
            position: absolute;
            left: -30px;
            top: 0;
            border-left: 2px solid #667eea;
            height: 100%;
        }}

        .collapsible-tree li::after {{
            content: '';
            position: absolute;
            left: -30px;
            top: 40px;
            width: 30px;
            border-top: 2px solid #667eea;
        }}

        .collapsible-tree li:last-child::before {{
            height: 40px;
        }}

        .collapsible-tree li.no-children::before,
        .collapsible-tree li.no-children::after {{
            display: none;
        }}

        /* 노드 카드 스타일 */
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

        /* 인센티브 여부 표시 */
        .org-node.has-incentive {{
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
        }}

        .org-node.no-incentive {{
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
        }}

        /* 노드 내용 스타일 */
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

        /* 인센티브 정보 스타일 - 개선된 버전 */
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
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
            border: 2px solid #667eea;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 16px;
            color: #667eea;
            font-weight: bold;
            transition: all 0.3s;
            z-index: 10;
        }}

        .toggle-btn:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-50%) scale(1.1);
        }}

        /* 자식 수 표시 */
        .child-count {{
            background: #667eea;
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

        /* 범례 스타일 */
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            to {{
                transform: rotate(360deg);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="position: absolute; top: 20px; right: 20px; display: flex; gap: 10px;">
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
            </div>
            <h1 id="mainTitle">QIP 인센티브 계산 결과 <span class="version-badge">v5.1</span></h1>
            <p id="mainSubtitle">{year}년 {get_korean_month(month)} 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;" data-year="{current_year}" data-month="{current_month:02d}" data-day="{current_day:02d}" data-hour="{current_hour:02d}" data-minute="{current_minute:02d}">보고서 생성일: {current_year}년 {current_month:02d}월 {current_day:02d}일 {current_hour:02d}:{current_minute:02d}</p>
            <div id="dataPeriodSection" style="color: white; font-size: 0.85em; margin-top: 15px; opacity: 0.85; line-height: 1.6;">
                <p id="dataPeriodTitle" style="margin: 5px 0; font-weight: bold;">📊 사용 데이터 기간:</p>
                <p id="incentiveDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{incentive_start_str}" data-endday="{incentive_end_str}">• 인센티브 데이터: {year}년 {month_num:02d}월 {incentive_start_str}일 ~ {incentive_end_str}일</p>
                <p id="attendanceDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{attendance_start_str}" data-endday="{attendance_end_str}">• 출근 데이터: {year}년 {month_num:02d}월 {attendance_start_str}일 ~ {attendance_end_str}일</p>
                <p id="aqlDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{aql_start_str}" data-endday="{aql_end_str}">• AQL 데이터: {year}년 {month_num:02d}월 {aql_start_str}일 ~ {aql_end_str}일</p>
                <p id="5prsDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}" data-startday="{prs_start_str}" data-endday="{prs_end_str}">• 5PRS 데이터: {year}년 {month_num:02d}월 {prs_start_str}일 ~ {prs_end_str}일</p>
                <p id="manpowerDataPeriod" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}">• 기본 인력 데이터: {year}년 {month_num:02d}월 기준</p>
            </div>
        </div>

        <!-- 보고서 타입 알림 배너 -->
        <div class="report-type-banner" id="reportTypeBanner">
            <div style="display: flex; align-items: center;">
                <span class="icon">{'⚠️' if is_interim_report else '✅'}</span>
                <div class="message">
                    <div class="title" id="reportTypeTitle">{report_type_ko} 보고서</div>
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
                        <h2 id="totalEmployeesValue">{total_employees}<span class="unit" id="totalEmployeesUnit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paidEmployeesLabel">수령 직원</h6>
                        <h2 id="paidEmployeesValue">{paid_employees}<span class="unit" id="paidEmployeesUnit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paymentRateLabel">수령률</h6>
                        <h2 id="paymentRateValue">{payment_rate:.1f}%</h2>
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
                <div class="tab" data-tab="position" onclick="showTab('position')" id="tabPosition">직급별 상세</div>
                <div class="tab" data-tab="detail" onclick="showTab('detail')" id="tabIndividual">개인별 상세</div>
                <div class="tab" data-tab="criteria" onclick="showTab('criteria')" id="tabCriteria">인센티브 기준</div>
                <div class="tab" data-tab="orgchart" onclick="showTab('orgchart')" id="tabOrgChart">조직도</div>
            </div>
            
            <!-- 요약 탭 -->
            <div id="summary" class="tab-content active">
                <h3 id="summaryTabTitle">Type별 현황</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th rowspan="2" id="summaryTypeHeader">Type</th>
                            <th rowspan="2" id="summaryTotalHeader">전체 인원</th>
                            <th rowspan="2" id="summaryEligibleHeader">수령 인원</th>
                            <th rowspan="2" id="summaryPaymentRateHeader">수령률</th>
                            <th rowspan="2" id="summaryTotalAmountHeader">총 지급액</th>
                            <th colspan="2" class="avg-header" id="summaryAvgAmountHeader">평균 지급액</th>
                        </tr>
                        <tr>
                            <th class="sub-header" id="summaryAvgEligibleHeader">수령인원 기준</th>
                            <th class="sub-header" id="summaryAvgTotalHeader">총원 기준</th>
                        </tr>
                    </thead>
                    <tbody id="typeSummaryBody">
                        <!-- JavaScript로 동적으로 채워질 예정 -->'''
    
    html_content += f'''
                    </tbody>
                </table>
            </div>
            
            <!-- 직급별 상세 탭 -->
            <div id="position" class="tab-content">
                <h3 id="positionTabTitle">직급별 상세 현황</h3>
                <div id="positionTables">
                    <!-- JavaScript로 채워질 예정 -->
                </div>
                
                <!-- Talent Pool 시각화 섹션 -->
                <div class="row mb-4" id="talentPoolSection" style="display: none;">
                    <div class="col-12">
                        <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                            <div class="card-body">
                                <h4 class="mb-3" id="talentPoolTitle">🌟 QIP Talent Pool 특별 인센티브</h4>
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
                                            <h6 style="opacity: 0.9;" id="talentPoolTotalBonusLabel">총 보너스 지급액</h6>
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
                <h3 id="individualDetailTitle">개인별 상세 정보</h3>
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
                                <option value="" id="optPaymentAll">전체</option>
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
            </div>
            
            <!-- 인센티브 기준 탭 -->
            <div id="criteria" class="tab-content">
                <h1 class="section-title" style="text-align: center; font-size: 28px; margin-bottom: 30px;" id="criteriaMainTitle">
                    QIP 인센티브 정책 및 계산 기준
                </h1>
                
                <!-- 정책 요약 섹션 -->
                <div class="alert alert-info mb-4">
                    <h5 class="alert-heading" id="corePrinciplesTitle">📌 핵심 원칙</h5>
                    <p class="mb-2" id="corePrinciplesDesc1">모든 직원은 해당 직급별로 지정된 <strong>모든 조건을 충족</strong>해야 인센티브를 받을 수 있습니다.</p>
                    <p class="mb-0" id="corePrinciplesDesc2">조건은 출근(4개), AQL(4개), 5PRS(2개)로 구성되며, 직급별로 적용 조건이 다릅니다.</p>
                </div>
                
                <!-- 10가지 조건 상세 설명 -->
                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0" id="evaluationConditionsTitle">📊 10가지 평가 조건 상세</h5>
                    </div>
                    <div class="card-body">
                        <!-- 출근 조건 -->
                        <h6 class="text-success mb-3" id="attendanceConditionTitle">📅 출근 조건 (4개)</h6>
                        <table class="table table-sm table-bordered mb-4" id="attendanceTable">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%">#</th>
                                    <th width="25%">조건명</th>
                                    <th width="20%">기준</th>
                                    <th width="50%">설명</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>출근율</td>
                                    <td>≥88%</td>
                                    <td>월간 출근율이 88% 이상이어야 합니다 (결근율 12% 이하)</td>
                                </tr>
                                <tr>
                                    <td>2</td>
                                    <td>무단결근</td>
                                    <td>≤2일</td>
                                    <td>사전 승인 없는 결근이 월 2일 이하여야 합니다</td>
                                </tr>
                                <tr>
                                    <td>3</td>
                                    <td>실제 근무일</td>
                                    <td>>0일</td>
                                    <td>실제 출근한 날이 1일 이상이어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>4</td>
                                    <td>최소 근무일</td>
                                    <td>≥12일</td>
                                    <td>월간 최소 12일 이상 근무해야 합니다</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- AQL 조건 -->
                        <h6 class="text-primary mb-3" id="aqlConditionTitle">🎯 AQL 조건 (4개)</h6>
                        <table class="table table-sm table-bordered mb-4" id="aqlTable">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%">#</th>
                                    <th width="25%">조건명</th>
                                    <th width="20%">기준</th>
                                    <th width="50%">설명</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>5</td>
                                    <td>개인 AQL (당월)</td>
                                    <td>실패 0건</td>
                                    <td>당월 개인 AQL 검사 실패가 없어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>6</td>
                                    <td>개인 AQL (연속성)</td>
                                    <td>3개월 연속 실패 없음</td>
                                    <td>최근 3개월간 연속으로 AQL 실패가 없어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>7</td>
                                    <td>팀/구역 AQL</td>
                                    <td>3개월 연속 실패 없음</td>
                                    <td>관리하는 팀/구역에서 3개월 연속 실패자가 없어야 합니다</td>
                                </tr>
                                <tr>
                                    <td>8</td>
                                    <td>담당구역 AQL Reject율</td>
                                    <td><3%</td>
                                    <td>담당 구역의 AQL 리젝률이 3% 미만이어야 합니다</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- 5PRS 조건 -->
                        <h6 class="text-warning mb-3" id="prsConditionTitle">📊 5PRS 조건 (2개)</h6>
                        <table class="table table-sm table-bordered" id="prsTable">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%">#</th>
                                    <th width="25%">조건명</th>
                                    <th width="20%">기준</th>
                                    <th width="50%">설명</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>9</td>
                                    <td>5PRS 통과율</td>
                                    <td>≥95%</td>
                                    <td>5족 평가 시스템에서 95% 이상 통과해야 합니다</td>
                                </tr>
                                <tr>
                                    <td>10</td>
                                    <td>5PRS 검사량</td>
                                    <td>≥100개</td>
                                    <td>월간 최소 100개 이상 검사를 수행해야 합니다</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 직급별 적용 조건 매트릭스 -->
                <div class="card mb-4 border-0 shadow-sm">
                    <div class="card-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <h5 class="mb-0" id="positionMatrixTitle">🎖️ 직급별 적용 조건</h5>
                    </div>
                    <div class="card-body">
                        
                        <h6 style="color: #667eea; font-weight: 600;" class="mb-3" id="type1Header">TYPE-1 직급별 조건</h6>
                        <table class="table table-sm table-hover position-matrix-table" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                <tr>
                                    <th class="pos-header-position">직급</th>
                                    <th class="pos-header-conditions">적용 조건</th>
                                    <th class="pos-header-count">조건 수</th>
                                    <th class="pos-header-notes">특이사항</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>MANAGER</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만</td>
                                </tr>
                                <tr>
                                    <td><strong>A.MANAGER</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만</td>
                                </tr>
                                <tr>
                                    <td><strong>(V) SUPERVISOR</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만</td>
                                </tr>
                                <tr>
                                    <td><strong>GROUP LEADER</strong></td>
                                    <td>1, 2, 3, 4</td>
                                    <td class="condition-count">4개</td>
                                    <td>출근 조건만</td>
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
                                    <td>출근 + 당월 AQL (특별 계산)</td>
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
                        
                        <h6 style="color: #667eea; font-weight: 600;" class="mb-3 mt-4" id="type2Header">TYPE-2 직급별 조건</h6>
                        <table class="table table-sm table-hover" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                <tr>
                                    <th class="type2-header-position">직급</th>
                                    <th class="type2-header-conditions">적용 조건</th>
                                    <th class="type2-header-count">조건 수</th>
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
                        
                        <h6 style="color: #667eea; font-weight: 600;" class="mb-3 mt-4" id="type3Header">TYPE-3 직급별 조건</h6>
                        <table class="table table-sm table-hover" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                <tr>
                                    <th class="type3-header-position">직급</th>
                                    <th class="type3-header-conditions">적용 조건</th>
                                    <th class="type3-header-count">조건 수</th>
                                    <th class="type3-header-notes">특이사항</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="background-color: #fafafa;">
                                    <td><strong id="type3NewMember">NEW QIP MEMBER</strong></td>
                                    <td id="type3NoConditions">없음</td>
                                    <td id="type3ZeroConditions">0개</td>
                                    <td id="type3NewMemberNote">신입직원 - 인센티브 없음</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 인센티브 금액 정보 -->
                <div class="card mb-4 border-0 shadow-sm">
                    <div class="card-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <h5 class="mb-0">💰 인센티브 지급액 계산 방법</h5>
                    </div>
                    <div class="card-body">
                        <!-- TYPE-1 인센티브 테이블 -->
                        <h6 style="color: #667eea; font-weight: 600;" class="mb-3" id="type1CalculationTitle">TYPE-1 직급별 인센티브 계산 방법 및 실제 예시</h6>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                <tr>
                                    <th width="20%" class="calc-header-position">직급</th>
                                    <th width="40%" class="calc-header-method">계산 방법</th>
                                    <th width="40%" class="calc-header-example">실제 계산 예시 ({year}년 {month_kor})</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong><span class="calc-position-manager">1. MANAGER</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 인센티브</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">인센티브</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 3.5</span><br>
                                        <span class="calc-apply-condition-attendance">적용 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-line-leader-avg">Line Leader 평균</span>: 138,485 VND<br>
                                        <span class="calc-calculation-label">계산</span>: 138,485 × 3.5 = <strong>484,698 VND</strong><br>
                                        <span class="calc-condition-not-met-zero">조건 미충족 → 0 VND</span></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-amanager">2. A.MANAGER</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 인센티브</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">인센티브</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 3</span><br>
                                        <span class="calc-apply-condition-attendance">적용 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="618030049">예시: 618030049 직원</span><br>
                                        <span class="calc-line-leader-avg">Line Leader 평균</span>: 127,767 VND<br>
                                        <span class="calc-calculation-label">계산</span>: 127,767 × 3 = <strong>383,301 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-vsupervisor">3. (V) SUPERVISOR</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 인센티브</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">인센티브</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 2.5</span><br>
                                        <span class="calc-apply-condition-attendance">적용 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="618040412">예시: 618040412 직원</span><br>
                                        <span class="calc-line-leader-avg">Line Leader 평균</span>: 115,500 VND<br>
                                        <span class="calc-calculation-label">계산</span>: 115,500 × 2.5 = <strong>288,750 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-groupleader">4. GROUP LEADER</span></strong></td>
                                    <td><strong><span class="calc-conditions-met">조건 충족시 TYPE-1 평균 인센티브</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">인센티브</span> = <span class="calc-line-leader-avg">Line Leader 평균</span> × 2</span><br>
                                        <span class="calc-apply-condition-attendance">적용 조건: 출근(1-4) = 4개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="619030390">예시: 619030390 직원</span><br>
                                        <span class="calc-condition-not-met-days" data-days="4">조건 미충족(근무일 4일)</span><br>
                                        → <strong>0 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-lineleader">5. LINE LEADER</span></strong></td>
                                    <td><strong><span class="calc-subordinate-incentive">부하직원 인센티브 기반 계산</span></strong><br>
                                        <span class="text-primary"><span class="calc-incentive-label">인센티브</span> = (<span class="calc-subordinate-total">부하직원 총</span> <span class="calc-incentive-label">인센티브</span> × 12%) × (<span class="calc-receive-ratio">수령 비율</span>)</span><br>
                                        <span class="calc-apply-condition-lineleader">적용 조건: 출근(1-4) + 팀/구역 AQL(7) = 5개 조건</span></td>
                                    <td><span class="calc-example-employee" data-employee="619020468">예시: 619020468 직원</span><br>
                                        <span class="calc-subordinate-total">부하직원 총</span>: 1,270,585 VND<br>
                                        <span class="calc-calculation-label">계산</span>: 1,270,585 × 0.12 × (8/10)<br>
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
                                        <small><span class="calc-month-range-1">1개월</span>: 100,000 | <span class="calc-month-range-2">2개월</span>: 200,000<br>
                                        <span class="calc-month-range-3">3개월</span>: 300,000 | <span class="calc-month-range-4">4개월</span>: 400,000<br>
                                        <span class="calc-month-range-5">5개월</span>: 500,000 | <span class="calc-month-range-6">6개월</span>: 600,000<br>
                                        <span class="calc-month-range-7">7개월</span>: 700,000 | <span class="calc-month-range-8">8개월</span>: 800,000<br>
                                        <span class="calc-month-range-9plus">9개월+</span>: 900,000</small></td>
                                    <td><span class="calc-example-employee" data-employee="618110077">예시: 618110077 직원</span><br>
                                        Part1: 1,000,000 (<span class="calc-months-text" data-months="12">12개월</span>)<br>
                                        Part2: 700,000 (<span class="calc-cfa-holder">CFA 보유</span>)<br>
                                        Part3: 900,000 (<span class="calc-months-text" data-months="13">13개월</span>)<br>
                                        <span class="calc-total-label">합계</span>: 2,600,000 VND</td>
                                </tr>
                                <tr style="background-color: #f0f4ff;">
                                    <td><strong><span class="calc-position-assemblyinspector">7. ASSEMBLY INSPECTOR</span></strong></td>
                                    <td><strong><span class="calc-consecutive-month-incentive">연속 충족 개월 기준 인센티브</span></strong><br>
                                        <small><span class="calc-apply-condition-assembly">적용 조건: 1-4(출근), 5-6(개인AQL), 9-10(5PRS)</span></small><br>
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
                                        ✅ <span class="calc-personal-aql-failures">개인AQL 실패</span> <span class="calc-cases-text" data-cases="0">0건</span><br>
                                        ✅ 5PRS <span class="calc-pass-rate">통과율</span> 98% ≥95%<br>
                                        ✅ 5PRS <span class="calc-inspection-quantity">검사량</span> <span class="calc-pieces-text" data-pieces="250">250족</span> ≥100<br>
                                        → <strong>850,000 VND</strong></td>
                                </tr>
                                <tr style="background-color: #f0f4ff;">
                                    <td><strong><span class="calc-position-audittraining">8. AUDIT & TRAINING</span></strong></td>
                                    <td><strong><span class="calc-consecutive-month-incentive">연속 충족 개월 기준 인센티브</span></strong><br>
                                        <small><span class="calc-apply-condition-audit">적용 조건: 1-4(출근), 7(팀AQL), 8(reject율)</span></small><br>
                                        <span class="calc-month-range-0to1">0-1개월</span>: 150,000 | <span class="calc-month-range-2">2개월</span>: 250,000<br>
                                        <span class="calc-month-range-3">3개월</span>: 300,000 | <span class="calc-month-range-4">4개월</span>: 350,000<br>
                                        <span class="calc-month-range-5">5개월</span>: 400,000 | <span class="calc-month-range-6">6개월</span>: 450,000<br>
                                        <span class="calc-month-range-7">7개월</span>: 500,000 | <span class="calc-month-range-8">8개월</span>: 650,000<br>
                                        <span class="calc-month-range-9">9개월</span>: 750,000 | <span class="calc-month-range-10">10개월</span>: 850,000<br>
                                        <span class="calc-month-range-11">11개월</span>: 950,000 | <span class="calc-month-range-12plus">12개월+</span>: 1,000,000</td>
                                    <td><strong><span class="calc-example-not-met-reset">예시: 조건 미충족 → 리셋</span></strong><br>
                                        <span class="calc-previous-month">전월</span>: <span class="calc-consecutive-months" data-months="11">11개월 연속</span> → 950,000<br>
                                        <span class="calc-current-month-eval">당월 평가</span>:<br>
                                        ✅ <span class="calc-all-attendance-met">출근 조건 모두 충족</span><br>
                                        ✅ <span class="calc-team-aql-no-fail">팀AQL 연속실패 없음</span><br>
                                        ❌ <span class="calc-reject-rate">reject율</span> 4.35% >3%<br>
                                        → <span class="calc-reset-to-zero">연속개월 0으로 리셋</span><br>
                                        → <strong>0 VND</strong></td>
                                </tr>
                                <tr>
                                    <td><strong><span class="calc-position-modelmaster">9. MODEL MASTER</span></strong></td>
                                    <td><strong><span class="calc-consecutive-month-incentive">연속 충족 개월 기준 인센티브</span></strong><br>
                                        <small><span class="calc-apply-condition-model">적용 조건: 1-4(출근), 8(reject율 <3%)</span></small><br>
                                        <span class="calc-month-range-0to1">0-1개월</span>: 150,000 | <span class="calc-month-range-2">2개월</span>: 250,000<br>
                                        <span class="calc-month-range-3">3개월</span>: 300,000 | <span class="calc-month-range-4">4개월</span>: 350,000<br>
                                        <span class="calc-month-range-5">5개월</span>: 400,000 | <span class="calc-month-range-6">6개월</span>: 450,000<br>
                                        <span class="calc-month-range-7">7개월</span>: 500,000 | <span class="calc-month-range-8">8개월</span>: 650,000<br>
                                        <span class="calc-month-range-9">9개월</span>: 750,000 | <span class="calc-month-range-10">10개월</span>: 850,000<br>
                                        <span class="calc-month-range-11">11개월</span>: 950,000 | <span class="calc-month-range-12plus">12개월+</span>: 1,000,000</td>
                                    <td><strong><span class="calc-example-max-achieved" data-months="12">예시: 12개월 이상 최대</span></strong><br>
                                        <span class="calc-previous-month">전월</span>: <span class="calc-months-text" data-months="15">15개월</span> → 1,000,000<br>
                                        <span class="calc-current-month-eval">당월 평가</span>:<br>
                                        ✅ <span class="calc-attendance-rate">출근율</span> 95% ≥88%<br>
                                        ✅ <span class="calc-unauthorized-absence">무단결근</span> <span class="calc-days-text" data-days="1">1일</span> ≤<span class="calc-days-text" data-days="2">2일</span><br>
                                        ✅ <span class="calc-working-days">근무일</span> <span class="calc-days-text" data-days="18">18일</span> ≥<span class="calc-days-text" data-days="12">12일</span><br>
                                        ✅ <span class="calc-reject-rate">reject율</span> 2.5% <3%<br>
                                        → <span class="calc-consecutive-months" data-months="16">16개월 연속 충족</span><br>
                                        → <strong>1,000,000 VND</strong></td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- TYPE-1 ASSEMBLY INSPECTOR 연속 목표 달성시 인센티브 지급 기준 -->
                        <h6 style="color: #667eea; font-weight: 600;" class="mb-3" id="assemblyInspectorIncentiveTitle">TYPE-1 ASSEMBLY INSPECTOR 연속 근무 인센티브</h6>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                <tr>
                                    <th class="consecutive-achievement-header">연속 목표 달성 개월</th>
                                    <th class="incentive-amount-header">인센티브 금액 (VND)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td><span class="month-text-1">1개월</span></td><td>150,000</td></tr>
                                <tr><td><span class="month-text-2">2개월</span></td><td>250,000</td></tr>
                                <tr><td><span class="month-text-3">3개월</span></td><td>300,000</td></tr>
                                <tr><td><span class="month-text-4">4개월</span></td><td>350,000</td></tr>
                                <tr><td><span class="month-text-5">5개월</span></td><td>450,000</td></tr>
                                <tr><td><span class="month-text-6">6개월</span></td><td>500,000</td></tr>
                                <tr><td><span class="month-text-7">7개월</span></td><td>600,000</td></tr>
                                <tr><td><span class="month-text-8">8개월</span></td><td>700,000</td></tr>
                                <tr><td><span class="month-text-9">9개월</span></td><td>750,000</td></tr>
                                <tr><td><span class="month-text-10">10개월</span></td><td>850,000</td></tr>
                                <tr><td><span class="month-text-11">11개월</span></td><td>900,000</td></tr>
                                <tr style="background-color: #e8f5e9; font-weight: bold;"><td><span class="month-text-12">12개월</span> <span class="month-or-more">이상</span></td><td>1,000,000</td></tr>
                            </tbody>
                        </table>
                        
                        <!-- TYPE-2 인센티브 계산 방법 -->
                        <h6 style="color: #667eea; font-weight: 600;" class="mb-3" id="type2CalculationTitle">TYPE-2 전체 직급 인센티브 계산 방법</h6>
                        <div class="alert" style="background-color: #f0f4ff; border-left: 4px solid #667eea; color: #333;" class="mb-3">
                            <strong>📊 <span class="type2-principle-label">TYPE-2 계산 원칙:</span></strong> <span class="type2-principle-text">TYPE-2 직급은 해당하는 TYPE-1 직꺉의 평균 인센티브를 기준으로 계산됩니다.</span>
                        </div>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                <tr>
                                    <th width="25%">TYPE-2 직급</th>
                                    <th width="25%">참조 TYPE-1 직급</th>
                                    <th width="25%">계산 방법</th>
                                    <th width="25%">{year}년 {month_kor} 평균</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>1. (V) SUPERVISOR</strong></td>
                                    <td>TYPE-1 (V) SUPERVISOR</td>
                                    <td>(V) SUPERVISOR <span class="average-text">평균</span></td>
                                    <td>357,977 VND</td>
                                </tr>
                                <tr>
                                    <td><strong>2. A.MANAGER</strong></td>
                                    <td>TYPE-1 A.MANAGER</td>
                                    <td>A.MANAGER <span class="average-text">평균</span></td>
                                    <td>383,301 VND</td>
                                </tr>
                                <tr>
                                    <td><strong>3. GROUP LEADER</strong></td>
                                    <td>TYPE-1 GROUP LEADER</td>
                                    <td>GROUP LEADER <span class="average-text">평균</span><br>
                                        <small class="text-muted">(TYPE-1 평균 0시: 전체 TYPE-2 LINE LEADER 평균 × 2)</small></td>
                                    <td>254,659 VND</td>
                                </tr>
                                <tr>
                                    <td><strong>4. LINE LEADER</strong></td>
                                    <td>TYPE-1 LINE LEADER</td>
                                    <td>LINE LEADER <span class="average-text">평균</span></td>
                                    <td>127,767 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>5. AQL INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>6. ASSEMBLY INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>7. STITCHING INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>8. BOTTOM INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>9. CUTTING INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>10. MTL INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>11. OCPT STAFF</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>12. OSC INSPECTOR</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>13. QA TEAM</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                                <tr style="background-color: #fafafa;">
                                    <td><strong>14. RQC</strong></td>
                                    <td>TYPE-1 ASSEMBLY INSPECTOR</td>
                                    <td>ASSEMBLY INSPECTOR <span class="average-text">평균</span></td>
                                    <td>369,531 VND</td>
                                </tr>
                            </tbody>
                        </table>

                        <!-- TYPE-2 GROUP LEADER 특별 계산 규칙 설명 -->
                        <div class="alert alert-warning mb-4">
                            <h6 style="color: #856404;" id="type2GroupLeaderSpecialTitle">⚠️ TYPE-2 GROUP LEADER 특별 계산 규칙</h6>
                            <ul class="mb-0">
                                <li id="type2BaseCalc"><strong>기본 계산:</strong> TYPE-1 GROUP LEADER 평균 인센티브 사용</li>
                                <li id="type2IndependentCalc"><strong>TYPE-1 평균이 0 VND인 경우:</strong> 모든 TYPE-2 LINE LEADER 평균 × 2로 독립 계산</li>
                                <li id="type2Important"><strong>중요:</strong> 부하직원 관계 없이 전체 TYPE-2 LINE LEADER 평균 사용</li>
                                <li id="type2Conditions"><strong>적용 조건:</strong> TYPE-2는 출근 조건(1-4번)만 충족하면 인센티브 지급</li>
                            </ul>
                        </div>

                        <!-- TYPE-3 인센티브 -->
                        <h6 style="color: #667eea; font-weight: 600;" class="mb-3" id="type3SectionTitle">TYPE-3 신입 직원 인센티브</h6>
                        <table class="table table-sm table-hover mb-4" style="border: 1px solid #e0e0e0;">
                            <thead style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                <tr>
                                    <th class="type3-position-header">구분</th>
                                    <th class="type3-standard-incentive-header">기준 인센티브</th>
                                    <th class="type3-calculation-method-header">계산 방법</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="type3-new-qip-member">NEW QIP MEMBER</td>
                                    <td>0 VND</td>
                                    <td><span class="type3-no-incentive">신입 직원은 인센티브 지급 없음.</span><br>
                                        <span class="type3-one-month-training">단, 1달 후 근무지 배치한 다음부터</span><br>
                                        <span class="type3-type-reclassification">TYPE을 변경하며, 인센티브 지급 조건 부여됨</span></td>
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
                                <strong>📌 <span class="failure-principle-label">실제 지급액:</span></strong> <span class="failure-principle-text">표시된 금액 범위는 예시이며, 실제 지급액은 개인의 성과와 조건 충족 여부에 따라 달라집니다.</span>
                            </li>
                            <li class="list-group-item">
                                <strong>📊 <span class="type2-principle-label">TYPE-2 동적 계산:</span></strong> <span class="type2-principle-text">TYPE-2 직원의 인센티브는 매월 해당 TYPE-1 직급의 실제 평균값으로 자동 계산됩니다.</span>
                            </li>
                            <li class="list-group-item">
                                <strong>🔄 <span class="consecutive-bonus-label">연속성 보상:</span></strong> <span class="consecutive-bonus-text">ASSEMBLY INSPECTOR는 연속 근무 개월이 증가할수록 인센티브가 단계적으로 상승합니다.</span>
                            </li>
                            <li class="list-group-item">
                                <strong>⚡ <span class="special-calculation-label">특별 계산 직급:</span></strong> <span class="special-calculation-text">AQL INSPECTOR(3단계 합산: Part1 + Part2 + Part3)</span>
                            </li>
                            <li class="list-group-item">
                                <strong>🎯 <span class="condition-failure-label">조건 미충족시:</span></strong> <span class="condition-failure-text">하나라도 필수 조건을 충족하지 못하면 인센티브가 0이 됩니다.</span>
                            </li>
                        </ul>
                        
                        <h6 class="text-success mb-3" id="monthlyIncentiveChangeReasonsTitle">월별 인센티브 변동 요인</h6>
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
                                    <td class="minimum-days-label">근무일수</td>
                                    <td class="less-than-12-days">12일 미만시 미지급</td>
                                    <td class="november-11-days">11일 근무 → 0 VND</td>
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
                                    <td class="aql-failure-label">AQL 실패</td>
                                    <td class="current-month-failure">해당 직급만 영향</td>
                                    <td class="aql-failure-example">AQL 실패 → 조건 미충족</td>
                                </tr>
                                <tr>
                                    <td class="fprs-pass-rate-label">5PRS 통과율</td>
                                    <td class="less-than-95-percent">95% 미만시 미지급 (해당자)</td>
                                    <td class="fprs-example">94% → 0 VND</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 계산 예시 섹션 / Calculation Example Section -->
                <div class="card mb-4">
                    <div class="card-header bg-warning">
                        <h5 class="mb-0" id="faqCalculationExampleTitle">📐 실제 계산 예시</h5>
                    </div>
                    <div class="card-body">
                        <h6 class="text-primary mb-3" id="faqCase1Title">예시 1: TYPE-1 ASSEMBLY INSPECTOR (10개월 연속 근무)</h6>
                        <div class="alert alert-light">
                            <p><strong id="faqCase1EmployeeLabel">직원:</strong> BÙI THỊ KIỀU LY (619060201)</p>
                            <p><strong id="faqCase1PrevMonthLabel">전월 상태:</strong> <span id="faqCase1PrevMonthText">9개월 연속 근무, 750,000 VND 수령</span></p>
                            <p><strong id="faqCase1ConditionsLabel">당월 조건 충족:</strong></p>
                            <ul id="faqCase1ConditionsList">
                                <li>✅ <span class="faq-attendance-label">출근율:</span> 92% (≥88%)</li>
                                <li>✅ <span class="faq-absence-label">무단결근:</span> <span class="faq-absence-value">0일</span> (≤<span class="faq-absence-limit">2일</span>)</li>
                                <li>✅ <span class="faq-actual-days-label">실제 근무일:</span> <span class="faq-actual-days-value">20일</span> (><span class="faq-actual-days-min">0일</span>)</li>
                                <li>✅ <span class="faq-min-days-label">최소 근무일:</span> <span class="faq-min-days-value">20일</span> (≥<span class="faq-min-days-req">12일</span>)</li>
                                <li>✅ <span class="faq-aql-current-label">개인 AQL (당월):</span> <span class="faq-aql-current-value">실패 0건</span></li>
                                <li>✅ <span class="faq-aql-consecutive-label">개인 AQL (연속):</span> <span class="faq-aql-consecutive-value">3개월 연속 실패 없음</span></li>
                                <li>✅ <span class="faq-fprs-rate-label">5PRS 통과율:</span> 97% (≥95%)</li>
                                <li>✅ <span class="faq-fprs-qty-label">5PRS 검사량:</span> <span class="faq-fprs-qty-value">150개</span> (≥<span class="faq-fprs-qty-min">100개</span>)</li>
                            </ul>
                            <p><strong id="faqCase1ResultLabel">결과:</strong> <span id="faqCase1ResultText">모든 조건 충족 → <span class="badge bg-success">10개월 연속 → 850,000 VND 지급</span></span></p>
                        </div>
                        
                        <h6 class="text-primary mb-3 mt-4" id="faqCase2Title">예시 2: AUDIT & TRAINING TEAM (담당구역 reject율 계산)</h6>
                        <div class="alert alert-light">
                            <p><strong id="faqCase2EmployeeLabel">직원:</strong> VÕ THỊ THÙY LINH (AUDIT & TRAINING TEAM LEADER)</p>
                            <p><strong id="faqCase2AreaLabel">담당 구역:</strong> Building B </p>
                            <p><strong><span id="faqCase2InspectionLabel">Building B 구역 생산 총 AQL 검사 PO 수량:</span> <span id="faqCase2InspectionQty">100개</span></strong></p>
                            <p><strong><span id="faqCase2RejectLabel">Building B 구역 생산 총 AQL 리젝 PO 수량:</span> <span id="faqCase2RejectQty">2개</span></strong></p>
                            <p><strong id="faqCase2CalcLabel">계산:</strong> 2 / 100 × 100 = 2%</p>
                            <p><strong id="faqCase2ResultLabel">결과:</strong> ✅ 2% < 3% → <span class="badge bg-success" id="faqCase2ResultBadge">조건 충족</span></p>
                        </div>
                        
                        <h6 class="text-primary mb-3 mt-4" id="faqMemberTableTitle">AUDIT & TRAINING TEAM 멤버별 담당 구역</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr style="background-color: #f8f9fa; color: #333; border-bottom: 2px solid #667eea;">
                                        <th id="faqTableHeaderName">직원명</th>
                                        <th id="faqTableHeaderBuilding">담당 Building</th>
                                        <th id="faqTableHeaderDesc">설명</th>
                                        <th id="faqTableHeaderReject">Reject율</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>VÕ THỊ THÙY LINH</strong></td>
                                        <td class="faq-building-whole">전체</td>
                                        <td class="faq-team-leader-desc">Team Leader - 전체 Building 총괄</td>
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
                                        <td><span>Building C </span><span class="faq-building-whole">전체</span></td>
                                        <td style="color: #dc3545;">3.4% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>DANH THỊ KIM ANH</td>
                                        <td>Building D</td>
                                        <td><span>Building D </span><span class="faq-building-whole">전체</span></td>
                                        <td style="color: #dc3545;">3.3% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>NGUYỄN THANH TRÚC</td>
                                        <td>Building A</td>
                                        <td><span>Building A </span><span class="faq-building-whole">전체</span></td>
                                        <td style="color: #dc3545;">4.7% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>PHẠM MỸ HUYỀN</td>
                                        <td>Building D</td>
                                        <td><span>Building D </span><span class="faq-building-whole">전체</span></td>
                                        <td style="color: #dc3545;">3.3% ❌</td>
                                    </tr>
                                    <tr>
                                        <td>SẦM TRÍ THÀNH</td>
                                        <td>Building C</td>
                                        <td><span>Building C </span><span class="faq-building-whole">전체</span></td>
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
                                <span id="faqMemberNote">* {month_kor} 기준 모든 AUDIT & TRAINING TEAM 멤버가 reject율 조건 미충족으로 인센티브 0원</span>
                            </p>
                        </div>
                        
                        <h6 class="text-primary mb-3 mt-4" id="faqCase3Title">예시 3: TYPE-2 STITCHING INSPECTOR</h6>
                        <div class="alert alert-light">
                            <p><strong id="faqCase3EmployeeLabel">직원:</strong> PHẠM THỊ HOA (STITCHING INSPECTOR)</p>
                            <p><strong id="faqCase3TypeLabel">직급 타입:</strong> TYPE-2</p>
                            <p><strong id="faqCase3StatusLabel">조건 충족 현황:</strong></p>
                            <ul id="faqCase3ConditionsList">
                                <li>✅ <span class="faq-case3-attendance-label">출근율:</span> 95% (≥88% <span class="faq-case3-met">충족</span>)</li>
                                <li>✅ <span class="faq-case3-absence-label">무단결근:</span> <span class="faq-case3-absence-value">0일</span> (≤<span class="faq-case3-absence-limit">2일</span> <span class="faq-case3-met">충족</span>)</li>
                                <li>✅ <span class="faq-case3-actual-label">실제근무일:</span> <span class="faq-case3-actual-value">19일</span> (><span class="faq-case3-actual-min">0일</span> <span class="faq-case3-met">충족</span>)</li>
                                <li>✅ <span class="faq-case3-min-label">최소근무일:</span> <span class="faq-case3-min-value">19일</span> (≥<span class="faq-case3-min-req">12일</span> <span class="faq-case3-met">충족</span>)</li>
                            </ul>
                            <p><strong id="faqCase3CalcLabel">인센티브 계산:</strong></p>
                            <p id="faqCase3Explanation">TYPE-2 STITCHING INSPECTOR는 출근 조건(1-4번)만 확인하며, 모든 조건을 충족했으므로 기본 인센티브를 받습니다.</p>
                            <p><strong id="faqCase3PaymentLabel">지급액:</strong> 150,000 VND (<span id="faqCase3BasicText">TYPE-2 기본 인센티브</span>)</p>
                            <p class="text-muted" id="faqCase3Note">* TYPE-2는 AQL이나 5PRS 조건 없이 출근 조건만으로 인센티브가 결정됩니다.</p>
                        </div>
                    </div>
                </div>
                
                <!-- 출근 계산 공식 -->
                <div class="card mb-4">
                    <div class="card-header bg-secondary text-white">
                        <h5 class="mb-0" id="attendanceCalcTitle">📊 출근율 계산 방식</h5>
                    </div>
                    <div class="card-body">
                        <div class="formula-box p-3 bg-light rounded mb-3">
                            <h6 id="attendanceFormulaTitle">실제 계산 공식 (시스템 구현):</h6>
                            <code class="d-block p-2 bg-white rounded mb-2" id="attendanceFormula1">
                                출근율(%) = 100 - 결근율(%)
                            </code>
                            <code class="d-block p-2 bg-white rounded" id="attendanceFormula2">
                                결근율(%) = (결근 일수 / 총 근무일) × 100
                            </code>
                            <p class="mt-2 text-muted small" id="attendanceFormulaNote">* 결근 일수 = 총 근무일 - 실제 근무일 - 승인된 휴가</p>
                        </div>
                        
                        <div class="formula-box p-3 bg-light rounded mb-3">
                            <h6 id="attendanceExamplesTitle">결근율 계산 예시:</h6>
                            <div class="alert alert-light">
                                <strong id="attendanceExample1Title">예시 1: 정상 근무자</strong><br>
                                • <span class="att-total-days-label">총 근무일</span>: 27<span class="att-days-unit">일</span><br>
                                • <span class="att-actual-days-label">실제 근무일</span>: 25<span class="att-days-unit">일</span><br>
                                • <span class="att-approved-leave-label">승인된 휴가</span>: 2<span class="att-days-unit">일</span> (<span class="att-annual-leave">연차</span>)<br>
                                • <span class="att-absence-days-label">결근 일수</span>: 27 - 25 - 2 = 0<span class="att-days-unit">일</span><br>
                                • <span class="att-absence-rate-label">결근율</span>: (0 / 27) × 100 = <strong>0%</strong><br>
                                • <span class="att-attendance-rate-label">출근율</span>: 100 - 0 = <strong>100%</strong> ✅
                            </div>
                            <div class="alert alert-light">
                                <strong id="attendanceExample2Title">예시 2: 무단결근 포함</strong><br>
                                • <span class="att-total-days-label">총 근무일</span>: 27<span class="att-days-unit">일</span><br>
                                • <span class="att-actual-days-label">실제 근무일</span>: 22<span class="att-days-unit">일</span><br>
                                • <span class="att-approved-leave-label">승인된 휴가</span>: 1<span class="att-days-unit">일</span> (<span class="att-sick-leave">병가</span>)<br>
                                • <span class="att-unauthorized-absence-label">무단결근</span>: 4<span class="att-days-unit">일</span> (AR1)<br>
                                • <span class="att-absence-days-label">결근 일수</span>: 27 - 22 - 1 = 4<span class="att-days-unit">일</span><br>
                                • <span class="att-absence-rate-label">결근율</span>: (4 / 27) × 100 = <strong>14.8%</strong><br>
                                • <span class="att-attendance-rate-label">출근율</span>: 100 - 14.8 = <strong>85.2%</strong> ❌ (<span class="att-less-than-88">88% 미만</span>)
                            </div>
                            <div class="alert alert-light">
                                <strong id="attendanceExample3Title">예시 3: 조건 충족 경계선</strong><br>
                                • <span class="att-total-days-label">총 근무일</span>: 27<span class="att-days-unit">일</span><br>
                                • <span class="att-actual-days-label">실제 근무일</span>: 24<span class="att-days-unit">일</span><br>
                                • <span class="att-approved-leave-label">승인된 휴가</span>: 0<span class="att-days-unit">일</span><br>
                                • <span class="att-unauthorized-absence-label">무단결근</span>: 3<span class="att-days-unit">일</span> (AR1)<br>
                                • <span class="att-absence-days-label">결근 일수</span>: 27 - 24 - 0 = 3<span class="att-days-unit">일</span><br>
                                • <span class="att-absence-rate-label">결근율</span>: (3 / 27) × 100 = <strong>11.1%</strong><br>
                                • <span class="att-attendance-rate-label">출근율</span>: 100 - 11.1 = <strong>88.9%</strong> ✅ (<span class="att-more-than-88">88% 이상</span>)<br>
                                • <span id="attendanceCondition2NotMet">단, 무단결근 3일로 조건 2 미충족 → 인센티브 0원</span>
                            </div>
                        </div>
                        
                        <div class="formula-box p-3 bg-light rounded mb-3">
                            <h6 id="attendanceClassificationTitle">결근 사유별 분류:</h6>
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
                                            <li id="attendanceCountingRule2">2일까지는 인센티브 지급 가능</li>
                                            <li id="attendanceCountingRule3">3일 이상 → 인센티브 0원</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="formula-box p-3 bg-light rounded">
                            <h6 id="attendanceConditionCriteriaTitle">조건 충족 기준:</h6>
                            <ul>
                                <li id="attendanceCriteria1"><strong>출근율:</strong> ≥ 88% (결근율 ≤ 12%)</li>
                                <li id="attendanceCriteria2"><strong>무단결근:</strong> ≤ 2일 (AR1 카테고리만 해당)</li>
                                <li id="attendanceCriteria3"><strong>실제 근무일:</strong> > 0일</li>
                                <li id="attendanceCriteria4"><strong>최소 근무일:</strong> ≥ 12일</li>
                            </ul>
                            <div class="alert alert-info mt-2">
                                <strong id="attendanceUnapprovedTitle">📊 Unapproved Absence Days 설명:</strong>
                                <ul class="mb-0 small">
                                    <li id="attendanceUnapproved1">HR 시스템에서 제공하는 무단결근 일수 데이터</li>
                                    <li id="attendanceUnapproved2">AR1 (Vắng không phép) 카테고리만 집계</li>
                                    <li id="attendanceUnapproved3">서면통지 결근(Gửi thư)도 AR1에 포함</li>
                                    <li id="attendanceUnapproved4">인센티브 조건: ≤2일 (개인별 최대 허용치)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- QIP Talent Pool 프로그램 설명 섹션 -->
                <div class="card mb-4">
                    <div class="card-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <h5 class="mb-0" id="talentProgramTitle">🌟 QIP Talent Pool 인센티브 프로그램</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info mb-4">
                            <p class="mb-0" id="talentProgramIntro">
                                <strong>QIP Talent Pool</strong>은 우수한 성과를 보이는 인원들을 대상으로 하는 특별 인센티브 프로그램입니다.
                                선정된 인원은 6개월간 매월 추가 보너스를 받게 됩니다.
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
                                        <h6 id="talentProgramMonthlyBonusTitle">월 특별 보너스</h6>
                                        <h4 class="text-primary">150,000 VND</h4>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 id="talentProgramTotalBonusTitle">총 지급 예정액 (6개월)</h6>
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
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
                                    <p class="mb-0 text-muted small" id="talentStep2Desc">최근 3개월간 성과 데이터 분석</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">3</div>
                                <div class="timeline-content">
                                    <strong id="talentStep3Title">위원회 심사</strong>
                                    <p class="mb-0 text-muted small" id="talentStep3Desc">QIP 운영위원회 최종 심사</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">4</div>
                                <div class="timeline-content">
                                    <strong id="talentStep4Title">최종 선정</strong>
                                    <p class="mb-0 text-muted small" id="talentStep4Desc">Talent Pool 멤버 확정 및 공지</p>
                                </div>
                            </div>
                            
                            <div class="timeline-step">
                                <div class="timeline-number">5</div>
                                <div class="timeline-content">
                                    <strong id="talentStep5Title">보너스 지급</strong>
                                    <p class="mb-0 text-muted small" id="talentStep5Desc">매월 정기 인센티브와 함께 지급</p>
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
                                <li>Talent Pool 보너스는 기본 인센티브와 별도로 지급됩니다</li>
                                <li>지급 기간 중 퇴사 시 자격이 자동 상실됩니다</li>
                                <li>성과 미달 시 조기 종료될 수 있습니다</li>
                                <li>매 6개월마다 재평가를 통해 갱신 여부가 결정됩니다</li>
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
                                    Q1. 왜 나는 인센티브를 못 받았나요? 조건을 확인하는 방법은?
                                </div>
                                <div class="faq-answer">
                                    <strong id="faqAnswer1Main">인센티브를 받지 못한 주요 이유:</strong>
                                    <ul>
                                        <li id="faqAnswer1Reason1">최소 근무일 12일 미충족</li>
                                        <li id="faqAnswer1Reason2">출근율 88% 미만</li>
                                        <li id="faqAnswer1Reason3">무단결근 3일 이상</li>
                                        <li id="faqAnswer1Reason4">AQL 실패 (해당 직급)</li>
                                        <li id="faqAnswer1Reason5">5PRS 통과율 95% 미만 (해당 직급)</li>
                                    </ul>
                                    <span id="faqAnswer1CheckMethod">개인별 상세 페이지에서 본인의 조건 충족 여부를 확인할 수 있습니다.</span>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion2">
                                    Q2. 무단결근이 며칠까지 허용되나요?
                                </div>
                                <div class="faq-answer">
                                    <strong id="faqAnswer2Main">무단결근은 최대 2일까지 허용됩니다.</strong> <span id="faqAnswer2Detail">3일 이상 무단결근시 해당 월 인센티브를 받을 수 없습니다. 사전 승인된 휴가나 병가는 무단결근에 포함되지 않습니다.</span>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion3">
                                    Q3. TYPE-2 직급의 인센티브는 어떻게 계산되나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer3Main">TYPE-2 직급의 인센티브는 해당하는 TYPE-1 직급의 평균 인센티브를 기준으로 계산됩니다.</span>
                                    <span id="faqAnswer3Example">예를 들어:</span>
                                    <ul>
                                        <li id="faqAnswer3Example1">TYPE-2 GROUP LEADER는 TYPE-1 GROUP LEADER들의 평균 인센티브</li>
                                        <li id="faqAnswer3Example2">TYPE-2 STITCHING INSPECTOR는 TYPE-1 ASSEMBLY INSPECTOR들의 평균 인센티브</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion4">
                                    Q4. ASSEMBLY INSPECTOR의 연속 근무 개월은 어떻게 계산되나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer4Main">TYPE-1 ASSEMBLY INSPECTOR만 해당되며, 조건을 충족하며 인센티브를 받은 개월수가 누적됩니다.</span>
                                    <ul>
                                        <li id="faqAnswer4Detail1">조건 미충족으로 인센티브를 못 받으면 0개월로 리셋</li>
                                        <li id="faqAnswer4Detail2">12개월 이상 연속시 최대 인센티브 1,000,000 VND</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion5">
                                    Q5. AQL 실패가 무엇이고 어떤 영향을 미치나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer5Main">AQL(Acceptable Quality Limit)은 품질 검사 기준입니다.</span>
                                    <ul>
                                        <li id="faqAnswer5Detail1">개인 AQL 실패: 해당 월에 품질 검사 실패한 경우</li>
                                        <li id="faqAnswer5Detail2">3개월 연속 실패: 지난 3개월 동안 연속으로 실패한 경우</li>
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
                                    <strong id="faqAnswer6Conclusion">둘 중 하나라도 미충족시 인센티브를 받을 수 없습니다.</strong>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion7">
                                    Q7. 출산휴가나 병가 중에도 인센티브를 받을 수 있나요?
                                </div>
                                <div class="faq-answer">
                                    <strong id="faqAnswer7Main">출산휴가나 장기 병가 중에는 인센티브가 지급되지 않습니다.</strong>
                                    <ul>
                                        <li id="faqAnswer7Detail1">최소 근무일 12일 조건을 충족할 수 없기 때문</li>
                                        <li id="faqAnswer7Detail2">복귀 후 조건 충족시 다시 인센티브 수령 가능</li>
                                        <li id="faqAnswer7Detail3">ASSEMBLY INSPECTOR의 경우 연속 개월수는 0으로 리셋</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion8">
                                    Q8. 전월 인센티브와 차이가 나는 이유는 무엇인가요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer8Main">인센티브 금액이 변동하는 주요 이유:</span>
                                    <ul>
                                        <li id="faqAnswer8Reason1"><strong>ASSEMBLY INSPECTOR</strong>: 연속 근무 개월 변화</li>
                                        <li id="faqAnswer8Reason2"><strong>TYPE-2 직급</strong>: TYPE-1 평균값 변동</li>
                                        <li id="faqAnswer8Reason3"><strong>AQL INSPECTOR</strong>: Part1, Part2, Part3 조건 변화</li>
                                        <li id="faqAnswer8Reason4"><strong>조건 미충족</strong>: 하나라도 미충족시 0</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion9">
                                    Q9. TYPE-3에서 TYPE-2로 승진하면 인센티브가 어떻게 변하나요?
                                </div>
                                <div class="faq-answer">
                                    <ul>
                                        <li id="faqAnswer9Detail1"><strong>TYPE-3</strong>: 조건 없이 기본 150,000 VND (근무시 자동 지급)</li>
                                        <li id="faqAnswer9Detail2"><strong>TYPE-2</strong>: 조건 충족 필요, TYPE-1 평균 기준 계산</li>
                                        <li id="faqAnswer9Detail3">승진 후 조건 충족시 일반적으로 인센티브 증가</li>
                                        <li id="faqAnswer9Detail4">하지만 조건 미충족시 0이 될 수 있으므로 주의 필요</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion10">
                                    Q10. 조건을 모두 충족했는데도 인센티브가 0인 이유는 무엇인가요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer10Main">다음 사항을 재확인해 보세요:</span>
                                    <ul>
                                        <li id="faqAnswer10Reason1"><strong>숨겨진 조건</strong>: 직급별로 적용되는 모든 조건 확인</li>
                                        <li id="faqAnswer10Reason2"><strong>데이터 업데이트</strong>: 최신 데이터 반영 여부</li>
                                        <li id="faqAnswer10Reason3"><strong>특별한 사유</strong>: 징계, 경고 등 특별 사유</li>
                                        <li id="faqAnswer10Reason4"><strong>시스템 오류</strong>: HR 부서에 문의</li>
                                    </ul>
                                    <span id="faqAnswer10Conclusion">개인별 상세 페이지에서 조건별 충족 여부를 상세히 확인하시기 바랍니다.</span>
                                </div>
                            </div>

                            <div class="faq-item">
                                <div class="faq-question" onclick="toggleFAQ(this)" id="faqQuestion11">
                                    Q11. TYPE-2 GROUP LEADER가 인센티브를 못 받는 경우가 있나요?
                                </div>
                                <div class="faq-answer">
                                    <span id="faqAnswer11Main">TYPE-2 GROUP LEADER는 특별한 계산 규칙이 적용됩니다:</span>
                                    <ul>
                                        <li id="faqAnswer11Detail1"><strong>기본 계산:</strong> TYPE-1 GROUP LEADER 평균 인센티브를 받습니다</li>
                                        <li id="faqAnswer11Detail2"><strong>독립 계산:</strong> TYPE-1 GROUP LEADER 평균이 0 VND일 경우, 자동으로 전체 TYPE-2 LINE LEADER 평균 × 2로 계산됩니다</li>
                                        <li id="faqAnswer11Detail3"><strong>개선 사항:</strong> 부하직원 관계와 상관없이 전체 TYPE-2 LINE LEADER 평균을 사용하여 더 공정한 계산이 이루어집니다</li>
                                        <li id="faqAnswer11Detail4"><strong>조건:</strong> TYPE-2는 출근 조건(1-4번)만 충족하면 인센티브를 받을 수 있습니다</li>
                                    </ul>
                                    <span id="faqAnswer11Conclusion">따라서 출근 조건을 충족한 TYPE-2 GROUP LEADER는 항상 인센티브를 받을 수 있도록 보장됩니다.</span>
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
                            <i class="fas fa-info-circle"></i> <strong>참고:</strong> AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다.
                        </div>

                        <!-- 동적 경로 표시 (Breadcrumb) -->
                        <div id="orgBreadcrumb" class="breadcrumb mb-3" style="background: #f8f9fa; padding: 10px; border-radius: 4px;">
                            <span style="color: #666;">전체 조직</span>
                        </div>

                        <!-- 필터 옵션 -->
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <select id="orgIncentiveFilter" class="form-select" onchange="updateOrgChart()">
                                    <option value="" id="filterAll">전체 보기</option>
                                    <option value="paid" id="filterPaid">인센티브 수령자</option>
                                    <option value="unpaid" id="filterUnpaid">인센티브 미수령자</option>
                                </select>
                            </div>
                            <div class="col-md-3">
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
                                <button class="btn btn-primary" onclick="resetOrgChart()">
                                    <i class="fas fa-redo"></i> <span id="resetViewBtn">초기화</span>
                                </button>
                            </div>
                            <!-- 저장 버튼 제거 -->
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
                                <span class="ms-3"><span style="display:inline-block; width:15px; height:15px; border: 2px solid #28a745; border-radius:3px;"></span> <span id="legendReceived">인센티브 수령</span></span>
                                <span><span style="display:inline-block; width:15px; height:15px; border: 2px solid #dc3545; border-radius:3px;"></span> <span id="legendNotReceived">인센티브 미수령</span></span>
                            </div>
                        </div>

                        <!-- 새로운 접이식 조직도 컨테이너 -->
                        <div id="orgChartContainer" class="collapsible-tree">
                            <!-- 제목 및 설명 -->
                            <div class="org-header">
                                <h4 id="orgChartTitle">TYPE-1 관리자 인센티브 구조</h4>
                                <p id="orgChartSubtitle" class="text-muted">TYPE-1 managers receiving incentive based on subordinate performance</p>
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
                            <div class="alert alert-info mb-3" role="alert" style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border-left: 4px solid #6366f1;">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>💡 <span id="usageGuideTitle">사용 안내:</span></strong> <span id="usageGuideText">인센티브 금액 또는 <span class="badge bg-primary">ℹ️</span> 버튼을 클릭하면 상세 정보를 볼 수 있습니다.</span>
                                <span class="float-end text-muted small" id="usageGuideSubtext">각 직원의 인센티브 계산 기준과 부하직원 정보를 확인하세요</span>
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
                                        <span id="legendIncentiveReceived">인센티브 수령</span>
                                    </span>
                                    <span class="legend-item">
                                        <span class="legend-dot not-received"></span>
                                        <span id="legendNoIncentive">인센티브 미수령</span>
                                    </span>
                                </div>
                            </div>

                            <div id="orgTreeContent">
                                <!-- JavaScript로 동적 생성됨 -->
                            </div>
                        </div>


                        <!-- 직원 정보 툴팁 -->
                        <div id="orgTooltip" style="position: absolute; visibility: hidden; background: white; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 1000;">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 직원 상세 모달 -->
    <div id="employeeModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <span class="close" onclick="closeModal()">&times;</span>
                <h2 id="modalTitle">직원 상세 정보</h2>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- JavaScript로 채워질 예정 -->
            </div>
        </div>
    </div>
    
    <script>
        const employeeData = {employees_json};
        const translations = {translations_js};
        const positionMatrix = {position_matrix_json};
        let currentLanguage = 'ko';
        const dashboardMonth = '{month.lower()}';
        const dashboardYear = {year};

        // employeeData 필드 정규화 - boss_id 매핑 추가
        employeeData.forEach(emp => {{
            // boss_id 필드 생성 (여러 가능한 필드명 체크)
            emp.boss_id = emp.boss_id ||
                         emp.Direct_Manager_ID ||
                         emp['Direct Manager ID'] ||
                         emp.direct_manager_id ||
                         '';

            // emp_no도 문자열로 통일
            emp.emp_no = String(emp.emp_no || emp['Employee No'] || '');

            // position과 name 필드도 확인
            emp.position = emp.position || emp['QIP POSITION 1ST  NAME'] || '';
            emp.name = emp.name || emp['Full Name'] || emp.employee_name || '';
            emp.type = emp.type || emp['ROLE TYPE STD'] || '';
        }});

        console.log('Employee data normalized. Sample:', employeeData.slice(0, 2));

        // 번역 함수
        function getTranslation(keyPath, lang = currentLanguage) {{
            const keys = keyPath.split('.');
            let value = translations;
            
            try {{
                for (const key of keys) {{
                    value = value[key];
                }}
                return value[lang] || value['ko'] || keyPath;
            }} catch (e) {{
                return keyPath;
            }}
        }}
        
        // FAQ 예시 섹션 업데이트 함수
        function updateFAQExamples() {{
            const lang = currentLanguage;
            console.log('Updating FAQ examples for language:', lang);
            
            // FAQ 계산 예시 타이틀
            const calcTitle = document.getElementById('faqCalculationExampleTitle');
            if (calcTitle) {{
                calcTitle.textContent = translations.incentiveCalculation?.faq?.calculationExampleTitle?.[lang] || '📐 실제 계산 예시';
            }}
            
            // Case 1 - TYPE-1 ASSEMBLY INSPECTOR
            const case1Title = document.getElementById('faqCase1Title');
            if (case1Title) {{
                case1Title.textContent = translations.incentiveCalculation?.faq?.case1Title?.[lang] || '예시 1: TYPE-1 ASSEMBLY INSPECTOR (10개월 연속 근무)';
            }}
            
            const case1EmployeeLabel = document.getElementById('faqCase1EmployeeLabel');
            if (case1EmployeeLabel) {{
                case1EmployeeLabel.textContent = translations.incentiveCalculation?.faq?.employee?.[lang] || '직원:';
            }}
            
            const case1PrevMonthLabel = document.getElementById('faqCase1PrevMonthLabel');
            if (case1PrevMonthLabel) {{
                case1PrevMonthLabel.textContent = translations.incentiveCalculation?.faq?.previousMonth?.[lang] || '전월 상태:';
            }}
            
            const case1PrevMonthText = document.getElementById('faqCase1PrevMonthText');
            if (case1PrevMonthText) {{
                const months = translations.incentiveCalculation?.faq?.consecutiveMonthsWorked?.[lang] || '개월 연속 →';
                const received = translations.incentiveCalculation?.faq?.incentiveReceived?.[lang] || 'VND 수령';
                case1PrevMonthText.textContent = `9${{months}} 750,000 ${{received}}`;
            }}
            
            const case1ConditionsLabel = document.getElementById('faqCase1ConditionsLabel');
            if (case1ConditionsLabel) {{
                case1ConditionsLabel.textContent = translations.incentiveCalculation?.faq?.conditionEvaluation?.[lang] || '당월 조건 충족:';
            }}
            
            // Case 1 조건들 업데이트
            document.querySelectorAll('.faq-attendance-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.attendanceRateMet?.[lang] || '출근율:';
            }});
            document.querySelectorAll('.faq-absence-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.unauthorizedAbsenceMet?.[lang] || '무단결근:';
            }});
            document.querySelectorAll('.faq-actual-days-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.actualWorkingDays?.[lang] || '실제 근무일:';
            }});
            document.querySelectorAll('.faq-min-days-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.minimumWorkingDays?.[lang] || '최소 근무일:';
            }});
            document.querySelectorAll('.faq-aql-current-label').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.personalAql?.[lang] || '개인 AQL (당월):';
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
            const days = translations.incentiveCalculation?.faq?.days?.[lang] || '일';
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
                el.textContent = translations.incentiveCalculation?.faq?.failureText?.[lang] || '실패 0건';
            }});
            document.querySelectorAll('.faq-aql-consecutive-value').forEach(el => {{
                el.textContent = '3' + (translations.incentiveCalculation?.faq?.monthsConsecutiveNoFailure?.[lang] || '개월 연속 실패 없음');
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
                const payment = translations.incentiveCalculation?.faq?.incentivePayment?.[lang] || 'VND 지급';
                case1ResultText.innerHTML = `${{allMet}} → <span class="badge bg-success">10${{consecutive}} 850,000 ${{payment}}</span>`;
            }}
            
            // Case 2 - AUDIT & TRAINING TEAM
            const case2Title = document.getElementById('faqCase2Title');
            if (case2Title) {{
                case2Title.textContent = translations.incentiveCalculation?.faq?.case2Title?.[lang] || '예시 2: AUDIT & TRAINING TEAM (담당구역 reject율 계산)';
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
                const label = translations.incentiveCalculation?.faq?.aqlInspectionPassed?.[lang] || '구역 생산 총 AQL 검사 PO 수량:';
                case2InspectionLabel.textContent = 'Building B ' + label;
            }}
            
            const case2InspectionQty = document.getElementById('faqCase2InspectionQty');
            if (case2InspectionQty) {{
                case2InspectionQty.textContent = '100' + items;
            }}
            
            const case2RejectLabel = document.getElementById('faqCase2RejectLabel');
            if (case2RejectLabel) {{
                const label = translations.incentiveCalculation?.faq?.aqlRejectPo?.[lang] || '구역 생산 총 AQL 리젝 PO 수량:';
                case2RejectLabel.textContent = 'Building B ' + label;
            }}
            
            const case2RejectQty = document.getElementById('faqCase2RejectQty');
            if (case2RejectQty) {{
                case2RejectQty.textContent = '2' + items;
            }}
            
            const case2CalcLabel = document.getElementById('faqCase2CalcLabel');
            if (case2CalcLabel) {{
                case2CalcLabel.textContent = translations.incentiveCalculation?.faq?.calculation?.[lang] || '계산:';
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
                memberTableTitle.textContent = translations.incentiveCalculation?.faq?.memberTable?.[lang] || 'AUDIT & TRAINING TEAM 멤버별 담당 구역';
            }}
            
            // 테이블 헤더
            const headerName = document.getElementById('faqTableHeaderName');
            if (headerName) {{
                headerName.textContent = translations.incentiveCalculation?.faq?.employeeNameLabel?.[lang] || '직원명';
            }}
            
            const headerBuilding = document.getElementById('faqTableHeaderBuilding');
            if (headerBuilding) {{
                headerBuilding.textContent = translations.incentiveCalculation?.faq?.assignedBuilding?.[lang] || '담당 Building';
            }}
            
            const headerDesc = document.getElementById('faqTableHeaderDesc');
            if (headerDesc) {{
                headerDesc.textContent = translations.incentiveCalculation?.faq?.buildingDescription?.[lang] || '설명';
            }}
            
            const headerReject = document.getElementById('faqTableHeaderReject');
            if (headerReject) {{
                headerReject.textContent = translations.incentiveCalculation?.faq?.rejectRate?.[lang] || 'Reject율';
            }}
            
            // 테이블 내용
            document.querySelectorAll('.faq-building-whole').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.buildingWhole?.[lang] || '전체';
            }});
            
            document.querySelectorAll('.faq-team-leader-desc').forEach(el => {{
                el.textContent = translations.incentiveCalculation?.faq?.teamLeaderDescription?.[lang] || 'Team Leader - 전체 Building 총괄';
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
                const monthText = dashboardMonth === 'september' ? '9월' : dashboardMonth === 'august' ? '8월' : dashboardMonth === 'july' ? '7월' : dashboardMonth;
                memberNote.textContent = translations.incentiveCalculation?.faq?.memberNote?.[lang] || `* ${{monthText}} 기준 모든 AUDIT & TRAINING TEAM 멤버가 reject율 조건 미충족으로 인센티브 0원`;
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
                case3TypeLabel.textContent = translations.incentiveCalculation?.faq?.positionType?.[lang] || '직급 타입:';
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
                el.textContent = translations.incentiveCalculation?.faq?.actualWorkingDays?.[lang] || '실제근무일:';
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
                case3CalcLabel.textContent = translations.incentiveCalculation?.faq?.incentiveCalculation?.[lang] || '인센티브 계산:';
            }}
            
            const case3Explanation = document.getElementById('faqCase3Explanation');
            if (case3Explanation) {{
                case3Explanation.textContent = translations.incentiveCalculation?.faq?.type2Explanation?.[lang] || 'TYPE-2 STITCHING INSPECTOR는 출근 조건(1-4번)만 확인하며, 모든 조건을 충족했으므로 기본 인센티브를 받습니다.';
            }}
            
            const case3PaymentLabel = document.getElementById('faqCase3PaymentLabel');
            if (case3PaymentLabel) {{
                case3PaymentLabel.textContent = translations.incentiveCalculation?.faq?.paymentAmount?.[lang] || '지급액:';
            }}
            
            const case3BasicText = document.getElementById('faqCase3BasicText');
            if (case3BasicText) {{
                case3BasicText.textContent = translations.incentiveCalculation?.faq?.type2BasicIncentive?.[lang] || 'TYPE-2 기본 인센티브';
            }}
            
            const case3Note = document.getElementById('faqCase3Note');
            if (case3Note) {{
                case3Note.textContent = translations.incentiveCalculation?.faq?.type2Note?.[lang] || '* TYPE-2는 AQL이나 5PRS 조건 없이 출근 조건만으로 인센티브가 결정됩니다.';
            }}
        }}
        
        // 출근율 계산 방식 섹션 업데이트 함수
        function updateAttendanceSection() {{
            const lang = currentLanguage;
            console.log('Updating attendance section for language:', lang);
            
            // 제목
            const title = document.getElementById('attendanceCalcTitle');
            if (title) {{
                title.textContent = translations.incentive?.attendance?.title?.[lang] || '📊 출근율 계산 방식';
            }}
            
            // 공식 제목
            const formulaTitle = document.getElementById('attendanceFormulaTitle');
            if (formulaTitle) {{
                formulaTitle.textContent = translations.incentive?.attendance?.formulaTitle?.[lang] || '실제 계산 공식 (시스템 구현):';
            }}
            
            // 공식들
            const formula1 = document.getElementById('attendanceFormula1');
            if (formula1) {{
                formula1.textContent = translations.incentive?.attendance?.attendanceFormula?.[lang] || '출근율(%) = 100 - 결근율(%)';
            }}
            
            const formula2 = document.getElementById('attendanceFormula2');
            if (formula2) {{
                formula2.textContent = translations.incentive?.attendance?.absenceFormula?.[lang] || '결근율(%) = (결근 일수 / 총 근무일) × 100';
            }}
            
            const formulaNote = document.getElementById('attendanceFormulaNote');
            if (formulaNote) {{
                formulaNote.textContent = translations.incentive?.attendance?.absenceDaysNote?.[lang] || '* 결근 일수 = 총 근무일 - 실제 근무일 - 승인된 휴가';
            }}
            
            // 예시 제목
            const examplesTitle = document.getElementById('attendanceExamplesTitle');
            if (examplesTitle) {{
                examplesTitle.textContent = translations.incentive?.attendance?.examplesTitle?.[lang] || '결근율 계산 예시:';
            }}
            
            const example1Title = document.getElementById('attendanceExample1Title');
            if (example1Title) {{
                example1Title.textContent = translations.incentive?.attendance?.example1Title?.[lang] || '예시 1: 정상 근무자';
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
                el.textContent = translations.incentive?.attendance?.totalWorkingDays?.[lang] || '총 근무일';
            }});
            document.querySelectorAll('.att-actual-days-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.actualWorkingDays?.[lang] || '실제 근무일';
            }});
            document.querySelectorAll('.att-approved-leave-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.approvedLeave?.[lang] || '승인된 휴가';
            }});
            document.querySelectorAll('.att-absence-days-label').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.absenceDays?.[lang] || '결근 일수';
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
                el.textContent = translations.incentive?.attendance?.days?.[lang] || '일';
            }});
            document.querySelectorAll('.att-less-than-88').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.lessThan88?.[lang] || '88% 미만';
            }});
            document.querySelectorAll('.att-more-than-88').forEach(el => {{
                el.textContent = translations.incentive?.attendance?.moreThan88?.[lang] || '88% 이상';
            }});
            
            const condition2NotMet = document.getElementById('attendanceCondition2NotMet');
            if (condition2NotMet) {{
                condition2NotMet.textContent = translations.incentive?.attendance?.condition2NotMet?.[lang] || '단, 무단결근 3일로 조건 2 미충족 → 인센티브 0원';
            }}
            
            // 결근 분류 섹션
            const classificationTitle = document.getElementById('attendanceClassificationTitle');
            if (classificationTitle) {{
                classificationTitle.textContent = translations.incentive?.attendance?.absenceClassificationTitle?.[lang] || '결근 사유별 분류:';
            }}
            
            const notIncludedTitle = document.getElementById('attendanceNotIncludedTitle');
            if (notIncludedTitle) {{
                notIncludedTitle.textContent = translations.incentive?.attendance?.notIncludedInAbsence?.[lang] || '✅ 결근율에 포함 안됨 (승인된 휴가):';
            }}
            
            const includedTitle = document.getElementById('attendanceIncludedTitle');
            if (includedTitle) {{
                includedTitle.textContent = translations.incentive?.attendance?.includedInAbsence?.[lang] || '❌ 결근율에 포함됨 (무단결근):';
            }}
            
            // 휴가 타입 번역
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
                countingRule2.textContent = translations.incentive?.attendance?.countingRule2?.[lang] || '2일까지는 인센티브 지급 가능';
            }}
            
            const countingRule3 = document.getElementById('attendanceCountingRule3');
            if (countingRule3) {{
                countingRule3.textContent = translations.incentive?.attendance?.countingRule3?.[lang] || '3일 이상 → 인센티브 0원';
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
                criteria2.innerHTML = translations.incentive?.attendance?.unauthorizedAbsenceCriteria?.[lang] || '<strong>무단결근:</strong> ≤ 2일 (AR1 카테고리만 해당)';
            }}
            
            const criteria3 = document.getElementById('attendanceCriteria3');
            if (criteria3) {{
                criteria3.innerHTML = translations.incentive?.attendance?.actualWorkingDaysCriteria?.[lang] || '<strong>실제 근무일:</strong> > 0일';
            }}
            
            const criteria4 = document.getElementById('attendanceCriteria4');
            if (criteria4) {{
                criteria4.innerHTML = translations.incentive?.attendance?.minimumWorkingDaysCriteria?.[lang] || '<strong>최소 근무일:</strong> ≥ 12일';
            }}
            
            // Unapproved Absence 설명
            const unapprovedTitle = document.getElementById('attendanceUnapprovedTitle');
            if (unapprovedTitle) {{
                unapprovedTitle.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanationTitle?.[lang] || '📊 Unapproved Absence Days 설명:';
            }}
            
            const unapproved1 = document.getElementById('attendanceUnapproved1');
            if (unapproved1) {{
                unapproved1.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation1?.[lang] || 'HR 시스템에서 제공하는 무단결근 일수 데이터';
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
                unapproved4.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation4?.[lang] || '인센티브 조건: ≤2일 (개인별 최대 허용치)';
            }}
        }}
        
        // FAQ Q&A 섹션 업데이트 함수
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
                const newText = translations.incentiveCalculation?.faq?.question1?.[lang] || 'Q1. 왜 나는 인센티브를 못 받았나요? 조건을 확인하는 방법은?';
                console.log('New text for Q1:', newText);
                q1.textContent = newText;
            }}
            document.getElementById('faqAnswer1Main').textContent = translations.incentiveCalculation?.faq?.answer1Main?.[lang] || '인센티브를 받지 못한 주요 이유:';
            document.getElementById('faqAnswer1Reason1').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.minDays?.[lang] || '최소 근무일 12일 미충족';
            document.getElementById('faqAnswer1Reason2').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.attendance?.[lang] || '출근율 88% 미만';
            document.getElementById('faqAnswer1Reason3').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.absence?.[lang] || '무단결근 3일 이상';
            document.getElementById('faqAnswer1Reason4').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.aql?.[lang] || 'AQL 실패 (해당 직급)';
            document.getElementById('faqAnswer1Reason5').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.fprs?.[lang] || '5PRS 통과율 95% 미만 (해당 직급)';
            document.getElementById('faqAnswer1CheckMethod').textContent = translations.incentiveCalculation?.faq?.answer1CheckMethod?.[lang] || '개인별 상세 페이지에서 본인의 조건 충족 여부를 확인할 수 있습니다.';
            
            // Q2
            const q2 = document.getElementById('faqQuestion2');
            if (q2) {{
                q2.textContent = translations.incentiveCalculation?.faq?.question2?.[lang] || 'Q2. 무단결근이 며칠까지 허용되나요?';
            }}
            document.getElementById('faqAnswer2Main').textContent = translations.incentiveCalculation?.faq?.answer2Main?.[lang] || '무단결근은 최대 2일까지 허용됩니다.';
            document.getElementById('faqAnswer2Detail').textContent = translations.incentiveCalculation?.faq?.answer2Detail?.[lang] || '3일 이상 무단결근시 해당 월 인센티브를 받을 수 없습니다. 사전 승인된 휴가나 병가는 무단결근에 포함되지 않습니다.';
            
            // Q3
            const q3 = document.getElementById('faqQuestion3');
            if (q3) {{
                q3.textContent = translations.incentiveCalculation?.faq?.question3?.[lang] || 'Q3. TYPE-2 직급의 인센티브는 어떻게 계산되나요?';
            }}
            document.getElementById('faqAnswer3Main').textContent = translations.incentiveCalculation?.faq?.answer3Main?.[lang] || 'TYPE-2 직급의 인센티브는 해당하는 TYPE-1 직급의 평균 인센티브를 기준으로 계산됩니다.';
            document.getElementById('faqAnswer3Example').textContent = translations.incentiveCalculation?.faq?.answer3Example?.[lang] || '예를 들어:';
            document.getElementById('faqAnswer3Example1').textContent = translations.incentiveCalculation?.faq?.answer3Example1?.[lang] || 'TYPE-2 GROUP LEADER는 TYPE-1 GROUP LEADER들의 평균 인센티브';
            document.getElementById('faqAnswer3Example2').textContent = translations.incentiveCalculation?.faq?.answer3Example2?.[lang] || 'TYPE-2 STITCHING INSPECTOR는 TYPE-1 ASSEMBLY INSPECTOR들의 평균 인센티브';
            
            // Q4
            const q4 = document.getElementById('faqQuestion4');
            if (q4) {{
                q4.textContent = translations.incentiveCalculation?.faq?.question4?.[lang] || 'Q4. ASSEMBLY INSPECTOR의 연속 근무 개월은 어떻게 계산되나요?';
            }}
            document.getElementById('faqAnswer4Main').textContent = translations.incentiveCalculation?.faq?.answer4Main?.[lang] || 'TYPE-1 ASSEMBLY INSPECTOR만 해당되며, 조건을 충족하며 인센티브를 받은 개월수가 누적됩니다.';
            document.getElementById('faqAnswer4Detail1').textContent = translations.incentiveCalculation?.faq?.answer4Detail1?.[lang] || '조건 미충족으로 인센티브를 못 받으면 0개월로 리셋';
            document.getElementById('faqAnswer4Detail2').textContent = translations.incentiveCalculation?.faq?.answer4Detail2?.[lang] || '12개월 이상 연속시 최대 인센티브 1,000,000 VND';
            
            // Q5
            const q5 = document.getElementById('faqQuestion5');
            if (q5) {{
                q5.textContent = translations.incentiveCalculation?.faq?.question5?.[lang] || 'Q5. AQL 실패가 무엇이고 어떤 영향을 미치나요?';
            }}
            document.getElementById('faqAnswer5Main').textContent = translations.incentiveCalculation?.faq?.answer5Main?.[lang] || 'AQL(Acceptable Quality Limit)은 품질 검사 기준입니다.';
            document.getElementById('faqAnswer5Detail1').textContent = translations.incentiveCalculation?.faq?.answer5Detail1?.[lang] || '개인 AQL 실패: 해당 월에 품질 검사 실패한 경우';
            document.getElementById('faqAnswer5Detail2').textContent = translations.incentiveCalculation?.faq?.answer5Detail2?.[lang] || '3개월 연속 실패: 지난 3개월 동안 연속으로 실패한 경우';
            document.getElementById('faqAnswer5Detail3').textContent = translations.incentiveCalculation?.faq?.answer5Detail3?.[lang] || 'AQL 관련 직급만 영향받음 (INSPECTOR 계열 등)';
            
            // Q6
            const q6 = document.getElementById('faqQuestion6');
            if (q6) {{
                q6.textContent = translations.incentiveCalculation?.faq?.question6?.[lang] || 'Q6. 5PRS 검사량이 부족하면 어떻게 되나요?';
            }}
            document.getElementById('faqAnswer6Main').textContent = translations.incentiveCalculation?.faq?.answer6Main?.[lang] || '5PRS 관련 직급은 다음 조건을 충족해야 합니다:';
            document.getElementById('faqAnswer6Detail1').textContent = translations.incentiveCalculation?.faq?.answer6Detail1?.[lang] || '검사량 100족 이상';
            document.getElementById('faqAnswer6Detail2').textContent = translations.incentiveCalculation?.faq?.answer6Detail2?.[lang] || '통과율 95% 이상';
            document.getElementById('faqAnswer6Conclusion').textContent = translations.incentiveCalculation?.faq?.answer6Conclusion?.[lang] || '둘 중 하나라도 미충족시 인센티브를 받을 수 없습니다.';
            
            // Q7
            const q7 = document.getElementById('faqQuestion7');
            if (q7) {{
                q7.textContent = translations.incentiveCalculation?.faq?.question7?.[lang] || 'Q7. 출산휴가나 병가 중에도 인센티브를 받을 수 있나요?';
            }}
            document.getElementById('faqAnswer7Main').textContent = translations.incentiveCalculation?.faq?.answer7Main?.[lang] || '출산휴가나 장기 병가 중에는 인센티브가 지급되지 않습니다.';
            document.getElementById('faqAnswer7Detail1').textContent = translations.incentiveCalculation?.faq?.answer7Detail1?.[lang] || '최소 근무일 12일 조건을 충족할 수 없기 때문';
            document.getElementById('faqAnswer7Detail2').textContent = translations.incentiveCalculation?.faq?.answer7Detail2?.[lang] || '복귀 후 조건 충족시 다시 인센티브 수령 가능';
            document.getElementById('faqAnswer7Detail3').textContent = translations.incentiveCalculation?.faq?.answer7Detail3?.[lang] || 'ASSEMBLY INSPECTOR의 경우 연속 개월수는 0으로 리셋';
            
            // Q8
            const q8 = document.getElementById('faqQuestion8');
            if (q8) {{
                q8.textContent = translations.incentiveCalculation?.faq?.question8?.[lang] || 'Q8. 전월 인센티브와 차이가 나는 이유는 무엇인가요?';
            }}
            const answer8Main = document.getElementById('faqAnswer8Main');
            if (answer8Main) {{
                answer8Main.textContent = translations.incentiveCalculation?.faq?.answer8Main?.[lang] || '인센티브 금액이 변동하는 주요 이유:';
            }}
            const answer8Reason1 = document.getElementById('faqAnswer8Reason1');
            if (answer8Reason1) {{
                answer8Reason1.innerHTML = `<strong>ASSEMBLY INSPECTOR</strong>: ${{translations.incentiveCalculation?.faq?.answer8Reason1?.[lang] || '연속 근무 개월 변화'}}`;
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
                q9.textContent = translations.incentiveCalculation?.faq?.question9?.[lang] || 'Q9. TYPE-3에서 TYPE-2로 승진하면 인센티브가 어떻게 변하나요?';
            }}
            const answer9Detail1 = document.getElementById('faqAnswer9Detail1');
            if (answer9Detail1) {{
                answer9Detail1.innerHTML = `<strong>TYPE-3</strong>: ${{translations.incentiveCalculation?.faq?.answer9Detail1?.[lang] || '조건 없이 기본 150,000 VND (근무시 자동 지급)'}}`;
            }}
            const answer9Detail2 = document.getElementById('faqAnswer9Detail2');
            if (answer9Detail2) {{
                answer9Detail2.innerHTML = `<strong>TYPE-2</strong>: ${{translations.incentiveCalculation?.faq?.answer9Detail2?.[lang] || '조건 충족 필요, TYPE-1 평균 기준 계산'}}`;
            }}
            const answer9Detail3 = document.getElementById('faqAnswer9Detail3');
            if (answer9Detail3) {{
                answer9Detail3.textContent = translations.incentiveCalculation?.faq?.answer9Detail3?.[lang] || '승진 후 조건 충족시 일반적으로 인센티브 증가';
            }}
            const answer9Detail4 = document.getElementById('faqAnswer9Detail4');
            if (answer9Detail4) {{
                answer9Detail4.textContent = translations.incentiveCalculation?.faq?.answer9Detail4?.[lang] || '하지만 조건 미충족시 0이 될 수 있으므로 주의 필요';
            }}
            
            // Q10
            const q10 = document.getElementById('faqQuestion10');
            if (q10) {{
                q10.textContent = translations.incentiveCalculation?.faq?.question10?.[lang] || 'Q10. 조건을 모두 충족했는데도 인센티브가 0인 이유는 무엇인가요?';
            }}
            const answer10Main = document.getElementById('faqAnswer10Main');
            if (answer10Main) {{
                answer10Main.textContent = translations.incentiveCalculation?.faq?.answer10Main?.[lang] || '다음 사항을 재확인해 보세요:';
            }}
            const answer10Reason1 = document.getElementById('faqAnswer10Reason1');
            if (answer10Reason1) {{
                answer10Reason1.innerHTML = `<strong>${{lang === 'ko' ? '숨겨진 조건' : lang === 'en' ? 'Hidden conditions' : 'Điều kiện ẩn'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer10Reason1?.[lang]?.replace(/.*: (.*)/, '$1') || '직급별로 적용되는 모든 조건 확인'}}`;
            }}
            const answer10Reason2 = document.getElementById('faqAnswer10Reason2');
            if (answer10Reason2) {{
                answer10Reason2.innerHTML = `<strong>${{lang === 'ko' ? '데이터 업데이트' : lang === 'en' ? 'Data update' : 'Cập nhật dữ liệu'}}</strong>: ${{translations.incentiveCalculation?.faq?.answer10Reason2?.[lang]?.replace(/.*: (.*)/, '$1') || '최신 데이터 반영 여부'}}`;
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
                q11.textContent = translations.incentiveCalculation?.faq?.question11?.[lang] || 'Q11. TYPE-2 GROUP LEADER가 인센티브를 못 받는 경우가 있나요?';
            }}
            const answer11Main = document.getElementById('faqAnswer11Main');
            if (answer11Main) {{
                answer11Main.textContent = translations.incentiveCalculation?.faq?.answer11Main?.[lang] || 'TYPE-2 GROUP LEADER는 특별한 계산 규칙이 적용됩니다:';
            }}
            const answer11Detail1 = document.getElementById('faqAnswer11Detail1');
            if (answer11Detail1) {{
                const baseCalc = translations.incentiveCalculation?.faq?.answer11Detail1?.[lang] || '기본 계산: TYPE-1 GROUP LEADER 평균 인센티브를 받습니다';
                answer11Detail1.innerHTML = `<strong>${{baseCalc.split(':')[0]}}:</strong> ${{baseCalc.split(':')[1] || ''}}`;
            }}
            const answer11Detail2 = document.getElementById('faqAnswer11Detail2');
            if (answer11Detail2) {{
                const indepCalc = translations.incentiveCalculation?.faq?.answer11Detail2?.[lang] || '독립 계산: TYPE-1 GROUP LEADER 평균이 0 VND일 경우, 자동으로 전체 TYPE-2 LINE LEADER 평균 × 2로 계산됩니다';
                answer11Detail2.innerHTML = `<strong>${{indepCalc.split(':')[0]}}:</strong> ${{indepCalc.split(':')[1] || ''}}`;
            }}
            const answer11Detail3 = document.getElementById('faqAnswer11Detail3');
            if (answer11Detail3) {{
                const improvement = translations.incentiveCalculation?.faq?.answer11Detail3?.[lang] || '개선 사항: 부하직원 관계와 상관없이 전체 TYPE-2 LINE LEADER 평균을 사용하여 더 공정한 계산이 이루어집니다';
                answer11Detail3.innerHTML = `<strong>${{improvement.split(':')[0]}}:</strong> ${{improvement.split(':')[1] || ''}}`;
            }}
            const answer11Detail4 = document.getElementById('faqAnswer11Detail4');
            if (answer11Detail4) {{
                const conditions = translations.incentiveCalculation?.faq?.answer11Detail4?.[lang] || '조건: TYPE-2는 출근 조건(1-4번)만 충족하면 인센티브를 받을 수 있습니다';
                answer11Detail4.innerHTML = `<strong>${{conditions.split(':')[0]}}:</strong> ${{conditions.split(':')[1] || ''}}`;
            }}
            const answer11Conclusion = document.getElementById('faqAnswer11Conclusion');
            if (answer11Conclusion) {{
                answer11Conclusion.textContent = translations.incentiveCalculation?.faq?.answer11Conclusion?.[lang] || '따라서 출근 조건을 충족한 TYPE-2 GROUP LEADER는 항상 인센티브를 받을 수 있도록 보장됩니다.';
            }}

            // TYPE-2 GROUP LEADER Special Calculation Box translations
            const type2SpecialTitle = document.getElementById('type2GroupLeaderSpecialTitle');
            if (type2SpecialTitle) {{
                type2SpecialTitle.textContent = translations.type2GroupLeaderSpecial?.title?.[lang] || '⚠️ TYPE-2 GROUP LEADER 특별 계산 규칙';
            }}
            const type2BaseCalc = document.getElementById('type2BaseCalc');
            if (type2BaseCalc) {{
                const baseText = translations.type2GroupLeaderSpecial?.baseCalculation?.[lang] || '기본 계산: TYPE-1 GROUP LEADER 평균 인센티브 사용';
                type2BaseCalc.innerHTML = `<strong>${{baseText.split(':')[0]}}:</strong> ${{baseText.split(':')[1] || ''}}`;
            }}
            const type2IndependentCalc = document.getElementById('type2IndependentCalc');
            if (type2IndependentCalc) {{
                const indepText = translations.type2GroupLeaderSpecial?.independentCalculation?.[lang] || 'TYPE-1 평균이 0 VND인 경우: 모든 TYPE-2 LINE LEADER 평균 × 2로 독립 계산';
                type2IndependentCalc.innerHTML = `<strong>${{indepText.split(':')[0]}}:</strong> ${{indepText.split(':')[1] || ''}}`;
            }}
            const type2Important = document.getElementById('type2Important');
            if (type2Important) {{
                const importantText = translations.type2GroupLeaderSpecial?.important?.[lang] || '중요: 부하직원 관계 없이 전체 TYPE-2 LINE LEADER 평균 사용';
                type2Important.innerHTML = `<strong>${{importantText.split(':')[0]}}:</strong> ${{importantText.split(':')[1] || ''}}`;
            }}
            const type2Conditions = document.getElementById('type2Conditions');
            if (type2Conditions) {{
                const conditionsText = translations.type2GroupLeaderSpecial?.conditions?.[lang] || '적용 조건: TYPE-2는 출근 조건(1-4번)만 충족하면 인센티브 지급';
                type2Conditions.innerHTML = `<strong>${{conditionsText.split(':')[0]}}:</strong> ${{conditionsText.split(':')[1] || ''}}`;
            }}

            // Talent Pool 섹션 번역 업데이트
            const talentPoolTitle = document.getElementById('talentPoolTitle');
            if (talentPoolTitle) {{
                talentPoolTitle.textContent = getTranslation('talentPool.sectionTitle', lang);
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
                talentPoolTotalBonusLabel.textContent = getTranslation('talentPool.totalBonus', lang);
            }}
            
            const talentPoolPaymentPeriodLabel = document.getElementById('talentPoolPaymentPeriodLabel');
            if (talentPoolPaymentPeriodLabel) {{
                talentPoolPaymentPeriodLabel.textContent = getTranslation('talentPool.paymentPeriod', lang);
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

            // 사용 안내 텍스트
            const usageGuideTitle = document.getElementById('usageGuideTitle');
            if (usageGuideTitle) {{
                usageGuideTitle.textContent = getTranslation('orgChart.usageGuide.title', currentLanguage);
            }}
            const usageGuideText = document.getElementById('usageGuideText');
            if (usageGuideText) {{
                usageGuideText.innerHTML = getTranslation('orgChart.usageGuide.text', currentLanguage);
            }}
            const usageGuideSubtext = document.getElementById('usageGuideSubtext');
            if (usageGuideSubtext) {{
                usageGuideSubtext.textContent = getTranslation('orgChart.usageGuide.subtext', currentLanguage);
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
            document.querySelectorAll('.modal-no-payment-reason').forEach(elem => {{
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

            // 테이블 재생성하여 툴팁 번역 적용
            generateEmployeeTable();
            updatePositionFilter();
        }}
        
        // 언어 변경 함수
        function changeLanguage(lang) {{
            currentLanguage = lang;
            updateAllTexts();
            updateTypeSummaryTable();  // Type별 요약 테이블도 업데이트
            localStorage.setItem('dashboardLanguage', lang);
        }}
        
        // 대시보드 변경 함수
        function changeDashboard(type) {{
            const currentMonth = '{str(month_num).zfill(2)}';  // 월 번호를 2자리로 패딩
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
        
        // 모든 텍스트 업데이트 - 완전한 구현
        function updateAllTexts() {{
            // 메인 헤더 업데이트
            const mainTitleElement = document.getElementById('mainTitle');
            if (mainTitleElement) {{
                mainTitleElement.innerHTML = getTranslation('headers.mainTitle', currentLanguage) + ' <span class="version-badge">v5.1</span>';
            }}
            
            // 날짜 관련 업데이트
            const yearText = '{year}';
            const monthText = currentLanguage === 'ko' ? '{get_korean_month(month)}' : 
                              currentLanguage === 'en' ? '{month.capitalize()}' : 
                              'Tháng {month if month.isdigit() else "8"}';
            
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

            // 데이터 기간 섹션 업데이트
            const dataPeriodTitle = document.getElementById('dataPeriodTitle');
            if (dataPeriodTitle) {{
                dataPeriodTitle.innerHTML = getTranslation('headers.dataPeriod.title', currentLanguage);
            }}

            // 각 데이터 기간 항목 업데이트
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
            
            // 단위 업데이트
            const units = document.querySelectorAll('#totalEmployeesUnit, #paidEmployeesUnit');
            units.forEach(unit => {{
                if (unit) unit.textContent = getTranslation('common.people', currentLanguage);
            }});
            
            // 탭 메뉴 업데이트
            const tabs = {{
                'tabSummary': 'tabs.summary',
                'tabPosition': 'tabs.position',
                'tabIndividual': 'tabs.individual',
                'tabCriteria': 'tabs.criteria',
                'tabOrgChart': 'tabs.orgChart'
            }};
            
            for (const [id, key] of Object.entries(tabs)) {{
                const elem = document.getElementById(id);
                if (elem) elem.textContent = getTranslation(key, currentLanguage);
            }}
            
            // 탭 컨텐츠 제목 업데이트
            const tabTitles = {{
                'summaryTabTitle': 'summary.typeTable.title',
                'positionTabTitle': 'position.title',
                'individualDetailTitle': 'individual.title'
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

            // 월별 헤더 동적 업데이트
            const prevMonthHeader = document.getElementById('prevMonthHeader');
            const currentMonthHeader = document.getElementById('currentMonthHeader');

            // 이전 월과 현재 월 이름 설정
            const prevMonthName = '{prev_month_name}';
            const currentMonthName = '{month}';

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
                const reportType = isInterim ? 'interim' : 'final';

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
                const dayText = currentLanguage === 'ko' ? '{current_day}일' :
                               currentLanguage === 'en' ? 'Day {current_day}' :
                               'Ngày {current_day}';
                const dateSpan = reportTypeBanner.querySelector('span[style*="font-size: 0.85rem"]');
                if (dateSpan) {{
                    dateSpan.textContent = generatedText + ': ' + dayText;
                }}
            }}

            // Summary 테이블의 "명" 단위 업데이트
            const typeSummaryBody = document.getElementById('typeSummaryBody');
            if (typeSummaryBody) {{
                const rows = typeSummaryBody.querySelectorAll('tr');
                rows.forEach(row => {{
                    const cells = row.querySelectorAll('td');
                    // 2번째 칼럼 (Total)과 3번째 칼럼 (Eligible)에 "명" 단위가 있음
                    if (cells.length > 2) {{
                        // Total 칼럼 - 모든 가능한 단위를 체크
                        const totalText = cells[1].textContent;
                        if (totalText.includes('명') || totalText.includes('people') || totalText.includes('người')) {{
                            // 숫자만 추출
                            const number = totalText.replace(/[^\\\\d]/g, '');
                            cells[1].textContent = number + getTranslation('common.people', currentLanguage);
                        }}
                        // Eligible 칼럼 - 모든 가능한 단위를 체크
                        const eligibleText = cells[2].textContent;
                        if (eligibleText.includes('명') || eligibleText.includes('people') || eligibleText.includes('người')) {{
                            // 숫자만 추출
                            const number = eligibleText.replace(/[^\\d]/g, '');
                            cells[2].textContent = number + getTranslation('common.people', currentLanguage);
                        }}
                    }}
                }});
            }}
            
            // 인센티브 기준 탭 텍스트 업데이트
            updateCriteriaTabTexts();
            
            // Talent Program 섹션 텍스트 업데이트
            updateTalentProgramTexts();
            
            // 차트 업데이트 (차트가 있는 경우)
            if (window.pieChart) {{
                updateChartLabels();
            }}
            
            // 직급별 테이블 및 개인별 테이블 재생성
            updateTabContents();
        }}
        
        // 탭 콘텐츠 업데이트
        function updateTabContents() {{
            // 개별 테이블 재생성
            generateEmployeeTable();
            generatePositionTables();
        }}
        
        // 인센티브 기준 탭 텍스트 업데이트 - 완전한 동적 번역
        function updateCriteriaTabTexts() {{
            // 메인 제목
            const criteriaTitle = document.getElementById('criteriaMainTitle');
            if (criteriaTitle) {{
                criteriaTitle.textContent = getTranslation('criteria.mainTitle', currentLanguage);
            }}
            
            // 핵심 원칙 섹션
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
            
            // 테이블 헤더 업데이트
            const tableHeaders = document.querySelectorAll('#criteria table thead tr');
            tableHeaders.forEach(row => {{
                const ths = row.querySelectorAll('th');
                if (ths.length === 4) {{
                    ths[0].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.number', currentLanguage);
                    ths[1].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.conditionName', currentLanguage);
                    ths[2].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.criteria', currentLanguage);
                    ths[3].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.description', currentLanguage);
                }}
            }});
            
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
            
            // 직급별 적용 조건 섹션
            const positionMatrixTitle = document.getElementById('positionMatrixTitle');
            if (positionMatrixTitle) {{
                positionMatrixTitle.textContent = getTranslation('criteria.positionMatrix.title', currentLanguage);
            }}
            
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
            
            // TYPE-1 테이블 조건 수 업데이트 
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
            
            // 인센티브 금액 계산 섹션
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
            
            // TYPE-1 인센티브 계산 테이블 번역
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
            
            // 직급명
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
            
            // 계산 방법 관련 텍스트
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
            
            // 적용 조건 텍스트
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
            
            // 특별 계산 텍스트
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
            
            // 일/개월/족/건 단위 변환
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
            
            // FAQ 계산 예시 섹션 번역
            updateFAQExamples();
            
            // 출근율 계산 방식 섹션 번역
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
            
            // 월별 인센티브 변동 요인 테이블
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
        
        // 조건 테이블 내용 동적 업데이트 함수
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
                        
                        // 조건 3: 실제 근무일
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
                        // 조건 5: 개인 AQL (당월)
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
            // TYPE-1 테이블의 특이사항 컬럼 업데이트
            const type1Tables = document.querySelectorAll('#criteria table');
            type1Tables.forEach(table => {{
                const tbody = table.querySelector('tbody');
                if (tbody) {{
                    const rows = tbody.querySelectorAll('tr');
                    rows.forEach(row => {{
                        const cells = row.querySelectorAll('td');
                        if (cells.length === 4) {{
                            const noteText = cells[3].textContent.trim();
                            // 특이사항 매핑
                            if (noteText.includes('출근 조건만') || noteText.includes('Attendance only')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceOnly', currentLanguage);
                            }} else if (noteText.includes('출근 + 팀/구역 AQL') && !noteText.includes('reject')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceTeamAql', currentLanguage);
                            }} else if (noteText.includes('특별 계산') || noteText.includes('Special calculation')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceMonthAql', currentLanguage);
                            }} else if (noteText.includes('출근 + 개인 AQL + 5PRS')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendancePersonalAql5prs', currentLanguage);
                            }} else if (noteText.includes('출근 + 팀/구역 AQL + 담당구역 reject')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceTeamAreaReject', currentLanguage);
                            }} else if (noteText.includes('출근 + 담당구역 reject')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceAreaReject', currentLanguage);
                            }} else if (noteText.includes('모든 조건') || noteText.includes('All conditions')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.allConditions', currentLanguage);
                            }} else if (noteText.includes('조건 없음') || noteText.includes('No conditions')) {{
                                cells[3].textContent = getTranslation('criteria.positionMatrix.notes.noConditions', currentLanguage);
                            }}
                        }}
                    }});
                }}
            }});
        }}
        
        // 차트 라벨 업데이트
        function updateChartLabels() {{
            // 예제 차트 업데이트 코드
        }}
        
        // Type별 요약 테이블 업데이트 함수
        function updateTypeSummaryTable() {{
            // Type별 데이터 집계
            const typeData = {{
                'TYPE-1': {{ total: 0, paid: 0, totalAmount: 0 }},
                'TYPE-2': {{ total: 0, paid: 0, totalAmount: 0 }},
                'TYPE-3': {{ total: 0, paid: 0, totalAmount: 0 }}
            }};

            // 전체 데이터 집계
            let grandTotal = 0;
            let grandPaid = 0;
            let grandAmount = 0;

            // 직원 데이터 순회하며 집계
            employeeData.forEach(emp => {{
                const type = emp.type;
                if (typeData[type]) {{
                    typeData[type].total++;
                    grandTotal++;

                    const amount = parseInt(emp[dashboardMonth + '_incentive']) || 0;
                    if (amount > 0) {{
                        typeData[type].paid++;
                        typeData[type].totalAmount += amount;
                        grandPaid++;
                        grandAmount += amount;
                    }}
                }}
            }});

            // 언어별 단위 설정
            const personUnit = currentLanguage === 'ko' ? '명' :
                              currentLanguage === 'en' ? ' people' :
                              ' người';

            // 테이블 tbody 업데이트
            const tbody = document.getElementById('typeSummaryBody');
            if (tbody) {{
                let html = '';

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
            }}
        }}
        
        // 초기화
        // 조직도 관련 함수들
        let orgChartData = null;
        let orgChartRoot = null;

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('=== DOMContentLoaded Event Fired ===');
            console.log('Total employees in data:', employeeData ? employeeData.length : 'No data');

            // Bootstrap 툴팁 초기화
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {{
                return new bootstrap.Tooltip(tooltipTriggerEl);
            }});
            console.log('Bootstrap tooltips initialized:', tooltipList.length);

            // D3.js 라이브러리 확인
            if (typeof d3 === 'undefined') {{
                console.error('D3.js library not loaded!');
                alert('D3.js 라이브러리가 로드되지 않았습니다. 페이지를 새로고침해주세요.');
                return;
            }}
            console.log('D3.js version:', d3.version);

            // Bootstrap 탭 이벤트 리스너 등록
            // 다양한 선택자 시도
            let orgChartTabButton = document.querySelector('button[data-bs-target="#orgchart"]');
            if (!orgChartTabButton) {{
                orgChartTabButton = document.querySelector('a[data-bs-target="#orgchart"]');
            }}
            if (!orgChartTabButton) {{
                orgChartTabButton = document.querySelector('[data-bs-target="#orgchart"]');
            }}
            if (!orgChartTabButton) {{
                // 네 번째 탭 버튼 직접 선택 (0-indexed이므로 3)
                const allTabButtons = document.querySelectorAll('.nav-link');
                if (allTabButtons.length > 3) {{
                    orgChartTabButton = allTabButtons[3];
                    console.log('네 번째 탭 버튼 사용');
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
            }}, 500); // 데이터 로드를 위한 약간의 지연
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

        // Breadcrumb 업데이트 함수
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

        // 줌 컨트롤 함수들
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

        // 인센티브 값을 안전하게 파싱하는 헬퍼 함수
        function parseIncentive(value) {{
            if (!value) return 0;
            // 문자열 형태의 값 처리
            const strValue = String(value).trim();
            // 쉼표 제거 후 파싱
            const parsed = parseInt(strValue.replace(/,/g, ''), 10);
            return isNaN(parsed) ? 0 : parsed;
        }}

        // 인센티브 수령 여부 확인 함수
        function hasIncentive(data) {{
            const amount = parseIncentive(data.incentive || data[dashboardMonth + '_incentive'] || 0);
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

        // 새로운 접이식 조직도 그리기 함수
        function drawOrgChart() {{
            console.log('Drawing new collapsible org chart...');
            drawCollapsibleOrgChart();
        }}

        function drawCollapsibleOrgChart() {{
            console.log('🏗️ === 조직도 그리기 시작 ===');
            console.log('   Employee Data 수:', employeeData ? employeeData.length : 0);
            console.log('   Dashboard Month:', dashboardMonth);

            const container = document.getElementById('orgTreeContent');
            if (!container) {{
                console.error('orgTreeContent container not found!');
                return;
            }}

            // 로딩 표시
            container.innerHTML = `<div class="org-loading"><div class="org-loading-spinner"></div><p>${{getTranslation('orgChart.loadingMessage')}}</p></div>`;

            // 계층 구조 데이터 생성
            const hierarchyData = buildHierarchyData();
            if (!hierarchyData || hierarchyData.length === 0) {{
                container.innerHTML = `<div class="alert alert-warning">${{getTranslation('orgChart.noDataMessage')}}</div>`;
                return;
            }}

            // HTML 트리 생성
            const treeHTML = buildTreeHTML(hierarchyData);
            container.innerHTML = treeHTML;

            // 이벤트 리스너 추가
            attachTreeEventListeners();

            // 통계 업데이트

            // UI 텍스트 업데이트
            updateOrgChartUIText();
        }}

        // 계층 구조 데이터 빌드
        function buildHierarchyData() {{
            console.log('Building TYPE-1 manager hierarchy data...');

            if (!employeeData || employeeData.length === 0) {{
                console.error('No employee data available');
                return null;
            }}

            // Special calculation positions 확인 함수
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

            // TYPE-1 직원 중 관리자 포지션만 필터링 (special calculation 제외)
            const filteredEmployees = employeeData.filter(emp => {{
                // TYPE-1이 아닌 경우 제외
                if (emp.type !== 'TYPE-1') {{
                    return false;
                }}

                const position = (emp.position || '').toUpperCase();

                // Special calculation positions 제외 (AQL INSPECTOR, AUDIT & TRAINING, MODEL MASTER)
                if (hasSpecialCalculation(emp.position)) {{
                    console.log(`Excluding special calculation position: ${{emp.position}} - ${{emp.name}}`);
                    return false;
                }}

                // 관리자 포지션 확인 (부하 기반 계산하는 포지션)
                const isManager = position.includes('MANAGER') ||
                                 position.includes('SUPERVISOR') ||
                                 position.includes('GROUP LEADER') ||
                                 position.includes('LINE LEADER');

                return isManager;
            }});

            console.log(`Filtered employees: ${{filteredEmployees.length}} (excluded ${{employeeData.length - filteredEmployees.length}})`);

            // 직원 ID로 매핑
            const employeeMap = {{}};
            const rootNodes = [];

            // 먼저 필터된 직원을 맵에 저장
            filteredEmployees.forEach(emp => {{
                // 인센티브 계산 방법 결정
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
                    incentive: emp[dashboardMonth + '_incentive'] || 0,
                    boss_id: emp.boss_id,
                    calculationMethod: calculationMethod,
                    children: []
                }};
            }});

            // 부모-자식 관계 설정
            filteredEmployees.forEach(emp => {{
                if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== '0') {{
                    const boss = employeeMap[emp.boss_id];
                    if (boss) {{
                        boss.children.push(employeeMap[emp.emp_no]);
                    }} else {{
                        // 보스가 없으면 루트 노드로 추가
                        rootNodes.push(employeeMap[emp.emp_no]);
                    }}
                }} else {{
                    // 보스 ID가 없으면 루트 노드
                    rootNodes.push(employeeMap[emp.emp_no]);
                }}
            }});

            console.log(`Hierarchy built: ${{rootNodes.length}} root nodes`);
            return rootNodes;
        }}

        // HTML 트리 생성
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

                // 인센티브 표시 점
                html += `<div class="node-incentive ${{incentiveDot}}"></div>`;

                // 노드 내용
                html += `<div class="node-position">${{node.position || 'N/A'}}</div>`;
                html += `<div class="node-name">${{node.name}}</div>`;
                html += `<div class="node-id">ID: ${{node.id}}</div>`;

                // 인센티브 정보 (모든 경우 클릭 가능)
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
                    // 부하직원 찾기 (인센티브 계산에 영향을 미치는 TYPE-1 부하만)
                    const subordinates = employeeData.filter(emp =>
                        emp.boss_id === node.id &&
                        emp.type === 'TYPE-1'
                    );

                    const receivingCount = subordinates.filter(sub => {{
                        const incentive = sub[dashboardMonth + '_incentive'] || 0;
                        return Number(incentive) > 0;
                    }}).length;

                    if (subordinates.length > 0) {{
                        html += `<div class="subordinate-info">`;
                        html += `<span class="subordinate-label">인센티브 계산 기반:</span>`;
                        html += `<span class="subordinate-count">TYPE-1 부하 ${{receivingCount}}/${{subordinates.length}}명</span>`;
                        html += '</div>';
                    }}
                }}

                // 자식이 있으면 접기/펼치기 버튼과 자식 수 표시
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

        // 노드 클래스 결정
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
                // 기존 리스너 제거 (중복 방지)
                if (window.incentiveButtonHandler) {{
                    treeContent.removeEventListener('click', window.incentiveButtonHandler, true);
                }}

                // 핸들러 함수를 전역에 저장하여 나중에 제거 가능
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
                        console.log('📌 모달 함수 존재:', typeof window.showIncentiveModal);

                        if (window.showIncentiveModal && nodeId) {{
                            console.log('🎯 모달 함수 호출 시도:', nodeId);
                            try {{
                                window.showIncentiveModal(nodeId);
                                console.log('✅ 모달 함수 호출 성공');
                            }} catch(error) {{
                                console.error('❌ 모달 함수 호출 중 오류:', error);
                            }}
                        }} else {{
                            console.error('❌ 모달 함수가 없거나 노드 ID가 없음');
                            console.error('   - showIncentiveModal:', typeof window.showIncentiveModal);
                            console.error('   - nodeId:', nodeId);
                        }}
                        return false;
                    }}
                }};

                // 이벤트 위임으로 처리 (동적으로 생성되는 버튼도 처리 가능)
                treeContent.addEventListener('click', window.incentiveButtonHandler, true); // capture 단계에서 처리
                console.log('✅ 인센티브 버튼 이벤트 리스너 등록 완료');
            }} else {{
                console.error('❌ orgTreeContent 요소를 찾을 수 없음');
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

            // 인센티브 정보 클릭 이벤트 (이벤트 위임 방식)
            console.log('📌 인센티브 클릭 이벤트 리스너 등록 중...');
            const orgContainer = document.getElementById('orgTreeContent');
            if (orgContainer) {{
                // 기존 리스너 제거 (중복 방지)
                orgContainer.removeEventListener('click', handleIncentiveClick);
                // 새 리스너 추가
                orgContainer.addEventListener('click', handleIncentiveClick);
                console.log('✅ 이벤트 위임 리스너 등록 완료');
            }}

            // 인센티브 클릭 핸들러 함수
            function handleIncentiveClick(e) {{
                const incentiveInfo = e.target.closest('.node-incentive-info');
                if (incentiveInfo) {{
                    e.preventDefault();
                    e.stopPropagation();
                    const nodeId = incentiveInfo.getAttribute('data-node-id');
                    console.log('💰 인센티브 클릭 감지 - Node ID:', nodeId);

                    if (window.showIncentiveModal) {{
                        window.showIncentiveModal(nodeId);
                    }} else {{
                        console.error('❌ showIncentiveModal 함수가 없습니다');
                    }}
                }}
            }}

            // 조직도가 그려진 후 툴팁 재초기화
            setTimeout(() => {{
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.forEach(function (tooltipTriggerEl) {{
                    new bootstrap.Tooltip(tooltipTriggerEl);
                }});
                console.log('✅ 조직도 툴팁 초기화 완료:', tooltipTriggerList.length, '개');
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

            // 노드 클릭 이벤트 (인센티브 정보 클릭 제외)
            document.querySelectorAll('.org-node').forEach(node => {{
                node.addEventListener('click', function(e) {{
                    // 인센티브 정보를 클릭한 경우는 제외
                    if (e.target.closest('.node-incentive-info')) {{
                        console.log('🚫 인센티브 클릭이므로 expand/collapse 무시');
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

        // 전체 펼치기
        function expandAll() {{
            document.querySelectorAll('.collapsible-tree li.collapsed').forEach(li => {{
                li.classList.remove('collapsed');
                li.classList.add('expanded');
            }});
        }}

        // 전체 접기
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

            // 검색어와 일치하는 노드 찾기
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

        // 모달 테스트 함수 (전역 스코프)
        // 모달 강제 닫기 함수 (전역 스코프)
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

        // 팀 내 모든 LINE LEADER 찾기 (재귀적) - Excel 로직과 동일
        function findTeamLineLeaders(managerId, depth = 0, visited = null) {{
            if (depth > 5) return []; // 무한 루프 방지

            if (!visited) {{
                visited = new Set();
            }}

            // managerId를 문자열로 통일
            managerId = String(managerId || '');
            if (!managerId || managerId === 'nan' || managerId === '0' || managerId === '') {{
                return [];
            }}

            if (visited.has(managerId)) {{
                return [];
            }}
            visited.add(managerId);

            let lineLeaders = [];

            // boss_id를 문자열로 비교하여 직접 부하들 찾기
            const directSubordinates = employeeData.filter(emp => {{
                const bossId = String(emp.boss_id || '');
                return bossId === managerId && bossId !== '';
            }});

            directSubordinates.forEach(sub => {{
                const position = (sub.position || '').toUpperCase();

                // TYPE-1 LINE LEADER인 경우 추가
                if (sub.type === 'TYPE-1' && position.includes('LINE') && position.includes('LEADER')) {{
                    lineLeaders.push(sub);
                }}

                // 재귀적으로 부하의 부하 탐색 (emp_no를 문자열로 변환)
                const subLineLeaders = findTeamLineLeaders(String(sub.emp_no || ''), depth + 1, visited);
                lineLeaders = lineLeaders.concat(subLineLeaders);
            }});

            return lineLeaders;
        }}

        // 인센티브 미지급 사유 분석 함수
        function getIncentiveFailureReasons(employee) {{
            const reasons = [];
            const position = (employee.position || '').toUpperCase();

            // 출근 조건 체크 (모든 직급 공통)
            if (employee['attendancy condition 1 - acctual working days is zero'] === 'yes') {{
                reasons.push('실제 근무일 0일 (출근 조건 1번 미충족)');
            }}
            if (employee['attendancy condition 2 - unapproved Absence Day is more than 2 days'] === 'yes') {{
                reasons.push('무단결근 2일 초과 (출근 조건 2번 미충족)');
            }}
            if (employee['attendancy condition 3 - absent % is over 12%'] === 'yes') {{
                reasons.push('결근율 12% 초과 (출근 조건 3번 미충족)');
            }}
            if (employee['attendancy condition 4 - minimum working days'] === 'yes') {{
                reasons.push('최소 근무일 미달 (출근 조건 4번 미충족)');
            }}

            // LINE LEADER의 경우 AQL 조건 추가 체크
            if (position.includes('LINE') && position.includes('LEADER')) {{
                if (employee['aql condition 7 - team/area fail AQL'] === 'yes') {{
                    reasons.push('팀/구역 AQL 실패 (AQL 조건 7번 미충족)');
                }}
                if (employee['September AQL Failures'] > 0) {{
                    reasons.push(`9월 AQL 실패 ${{employee['September AQL Failures']}}건`);
                }}
                if (employee['Continuous_FAIL'] === 'YES') {{
                    reasons.push('3개월 연속 AQL 실패');
                }}
            }}

            // 5PRS 조건 체크 (해당 직급만)
            if (employee['5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%'] === 'no') {{
                reasons.push('5PRS 검증 부족 또는 합격률 95% 미달 (5PRS 조건 1번 미충족)');
            }}
            if (employee['5prs condition 2 - Total Valiation Qty is zero'] === 'yes') {{
                reasons.push('5PRS 총 검증 수량 0 (5PRS 조건 2번 미충족)');
            }}

            // 조건 통과율 체크
            if (employee['conditions_pass_rate'] !== undefined && employee['conditions_pass_rate'] < 100) {{
                const passRate = parseFloat(employee['conditions_pass_rate'] || 0).toFixed(1);
                const passed = employee['conditions_passed'] || 0;
                const applicable = employee['conditions_applicable'] || 0;
                if (reasons.length === 0 && passRate < 100) {{
                    reasons.push(`조건 통과율 부족: ${{passed}}/${{applicable}} (${{passRate}}%)`);
                }}
            }}

            // 사유가 없는 경우 기본 메시지
            if (reasons.length === 0) {{
                if (employee[dashboardMonth + '_incentive'] === 0) {{
                    reasons.push('조건 정보를 확인할 수 없습니다');
                }}
            }}

            return reasons;
        }}

        // 인센티브 상세 모달 (전역 스코프)
        window.showIncentiveModal = function(nodeId) {{
            console.log('🔍 모달 함수 호출됨 - Node ID:', nodeId);

            try {{
                // 기존 모달이 있으면 강제 닫기
                window.forceCloseModal();

                const employee = employeeData.find(emp => emp.emp_no === nodeId);
                if (!employee) {{
                    console.error('❌ 직원 데이터를 찾을 수 없음:', nodeId);
                    alert('직원 데이터를 찾을 수 없습니다. ID: ' + nodeId);
                    return;
                }}
                console.log('✅ 직원 발견:', employee.name, employee.position);

                const position = (employee.position || '').toUpperCase();
                const employeeIncentive = Number(employee[dashboardMonth + '_incentive'] || 0);

                // 부하 직원 찾기 (TYPE-1만)
                const subordinates = employeeData.filter(emp => emp.boss_id === nodeId && emp.type === 'TYPE-1');
                const receivingSubordinates = subordinates.filter(sub => {{
                    const incentive = sub[dashboardMonth + '_incentive'] || 0;
                    return Number(incentive) > 0;
                }});

                // 계산 과정 상세 내용 생성
                let calculationDetails = '';

                if (position.includes('LINE LEADER')) {{
                // LINE LEADER 계산 상세 - 부하직원 합계 × 12% × 수령율
                const assemblyInspectors = subordinates.filter(sub =>
                    sub.position && sub.position.toUpperCase().includes('ASSEMBLY INSPECTOR')
                );
                const totalSubIncentive = assemblyInspectors.reduce((sum, sub) => {{
                    return sum + Number(sub[dashboardMonth + '_incentive'] || 0);
                }}, 0);
                const receivingInspectors = assemblyInspectors.filter(ai =>
                    Number(ai[dashboardMonth + '_incentive'] || 0) > 0
                );
                const receivingRatio = assemblyInspectors.length > 0 ? receivingInspectors.length / assemblyInspectors.length : 0;
                const expectedIncentive = Math.round(totalSubIncentive * 0.12 * receivingRatio);

                // ASSEMBLY INSPECTOR 상세 내역 생성
                let inspectorDetails = '';
                if (assemblyInspectors.length > 0) {{
                    inspectorDetails = `
                        <div class="mt-3">
                            <h6>📋 ASSEMBLY INSPECTOR 인센티브 내역 (합계 계산 대상)</h6>
                            <table class="table table-sm table-bordered">
                                <thead class="table-light">
                                    <tr>
                                        <th>이름</th>
                                        <th>ID</th>
                                        <th class="text-end">인센티브</th>
                                        <th class="text-center">수령 여부</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{assemblyInspectors.map(ai => {{
                                        const aiIncentive = Number(ai[dashboardMonth + '_incentive'] || 0);
                                        const isReceiving = aiIncentive > 0;
                                        return `
                                            <tr class="${{isReceiving ? '' : 'text-muted'}}">
                                                <td>${{ai.name || ai.employee_name || 'Unknown'}}</td>
                                                <td>${{ai.emp_no || ai.employee_id || ''}}</td>
                                                <td class="text-end">₫${{aiIncentive.toLocaleString('ko-KR')}}</td>
                                                <td class="text-center">${{isReceiving ? '✅' : '❌'}}</td>
                                            </tr>
                                        `;
                                    }}).join('')}}
                                </tbody>
                                <tfoot class="table-secondary">
                                    <tr>
                                        <th colspan="2">합계</th>
                                        <th class="text-end">₫${{totalSubIncentive.toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                    <tr>
                                        <th colspan="2">평균 (수령자 ${{receivingInspectors.length}}명 / 전체 ${{assemblyInspectors.length}}명)</th>
                                        <th class="text-end">₫${{receivingInspectors.length > 0 ? Math.round(totalSubIncentive / receivingInspectors.length).toLocaleString('ko-KR') : '0'}}</th>
                                        <th></th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                }}

                calculationDetails = `
                    <div class="calculation-details">
                        <h6>📊 계산 과정 상세 (LINE LEADER)</h6>
                        <table class="table table-sm">
                            <tr>
                                <td>계산 공식:</td>
                                <td class="text-end"><strong>부하직원 합계 × 12% × 수령율</strong></td>
                            </tr>
                            <tr>
                                <td>ASSEMBLY INSPECTOR 수:</td>
                                <td class="text-end">${{assemblyInspectors.length}}명 (수령: ${{receivingInspectors.length}}명)</td>
                            </tr>
                            <tr>
                                <td>인센티브 합계:</td>
                                <td class="text-end">₫${{totalSubIncentive.toLocaleString('ko-KR')}}</td>
                            </tr>
                            <tr>
                                <td>수령 비율:</td>
                                <td class="text-end">${{receivingInspectors.length}}/${{assemblyInspectors.length}} = ${{(receivingRatio * 100).toFixed(1)}}%</td>
                            </tr>
                            <tr>
                                <td>계산식:</td>
                                <td class="text-end">₫${{totalSubIncentive.toLocaleString('ko-KR')}} × 12% × ${{(receivingRatio * 100).toFixed(1)}}%</td>
                            </tr>
                            <tr class="table-primary">
                                <td><strong>${{getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                            <tr class="${{Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}}">
                                <td><strong>${{getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{employeeIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                        </table>
                        ${{inspectorDetails}}
                    </div>
                `;
                }} else if (position.includes('GROUP LEADER')) {{
                // GROUP LEADER 계산 상세 - 팀 내 LINE LEADER 평균 × 2
                const teamLineLeaders = findTeamLineLeaders(employee.emp_no);
                const receivingLineLeaders = teamLineLeaders.filter(ll =>
                    Number(ll[dashboardMonth + '_incentive'] || 0) > 0
                );
                const avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                    receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
                const expectedIncentive = Math.round(avgLineLeaderIncentive * 2);

                // LINE LEADER별 상세 내역 생성
                let lineLeaderDetails = '';
                if (teamLineLeaders.length > 0) {{
                    lineLeaderDetails = `
                        <div class="mt-3">
                            <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                            <table class="table table-sm table-bordered">
                                <thead class="table-light">
                                    <tr>
                                        <th>이름</th>
                                        <th>ID</th>
                                        <th class="text-end">인센티브</th>
                                        <th class="text-center">평균 계산 포함</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{teamLineLeaders.map(ll => {{
                                        const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                        const included = llIncentive > 0;
                                        return `
                                            <tr class="${{included ? '' : 'text-muted'}}">
                                                <td>${{ll.name}}</td>
                                                <td>${{ll.emp_no}}</td>
                                                <td class="text-end">${{included ? '₫' + llIncentive.toLocaleString('ko-KR') : '-'}}</td>
                                                <td class="text-center">${{included ? '✅' : '❌'}}</td>
                                            </tr>
                                        `;
                                    }}).join('')}}
                                </tbody>
                                <tfoot class="table-secondary">
                                    <tr>
                                        <th colspan="2">합계</th>
                                        <th class="text-end">₫${{receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0).toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                    <tr>
                                        <th colspan="2">평균 (수령자 ${{receivingLineLeaders.length}}명 / 전체 ${{teamLineLeaders.length}}명)</th>
                                        <th class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                }}

                calculationDetails = `
                    <div class="calculation-details">
                        <h6>📊 계산 과정 상세 (GROUP LEADER)</h6>
                        <table class="table table-sm">
                            <tr>
                                <td>계산 공식:</td>
                                <td class="text-end"><strong>LINE LEADER 평균 × 2</strong></td>
                            </tr>
                            <tr>
                                <td><span class="modal-team-line-leader-count">팀 내 LINE LEADER 수:</span></td>
                                <td class="text-end">${{teamLineLeaders.length}}명 (수령: ${{receivingLineLeaders.length}}명)</td>
                            </tr>
                            <tr>
                                <td>LINE LEADER 평균 인센티브:</td>
                                <td class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</td>
                            </tr>
                            <tr>
                                <td>계산식:</td>
                                <td class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}} × 2</td>
                            </tr>
                            <tr class="table-primary">
                                <td><strong>${{getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                            <tr class="${{Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}}">
                                <td><strong>${{getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{employeeIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                        </table>
                        ${{lineLeaderDetails}}
                    </div>
                `;
                }} else if (position.includes('SUPERVISOR')) {{
                // SUPERVISOR 계산 상세 - 팀 내 LINE LEADER만
                const teamLineLeaders = findTeamLineLeaders(employee.emp_no);
                const receivingLineLeaders = teamLineLeaders.filter(ll =>
                    Number(ll[dashboardMonth + '_incentive'] || 0) > 0
                );
                const avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                    receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
                const expectedIncentive = Math.round(avgLineLeaderIncentive * 2.5);

                // 팀 내 LINE LEADER 상세 내역 생성
                let allLineLeaderDetails = '';
                if (teamLineLeaders.length > 0) {{
                    // LINE LEADER를 GROUP별로 그룹화
                    const lineLeadersByGroup = {{}};
                    teamLineLeaders.forEach(ll => {{
                        const groupLeader = employeeData.find(emp => emp.emp_no === ll.boss_id);
                        const groupName = groupLeader ? groupLeader.name : 'Unknown';
                        if (!lineLeadersByGroup[groupName]) {{
                            lineLeadersByGroup[groupName] = [];
                        }}
                        lineLeadersByGroup[groupName].push(ll);
                    }});

                    allLineLeaderDetails = `
                        <div class="mt-3">
                            <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                            <table class="table table-sm table-bordered">
                                <thead class="table-light">
                                    <tr>
                                        <th>GROUP</th>
                                        <th>LINE LEADER</th>
                                        <th>ID</th>
                                        <th class="text-end">인센티브</th>
                                        <th class="text-center">평균 계산 포함</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{Object.entries(lineLeadersByGroup).map(([groupName, leaders]) => {{
                                        return leaders.map((ll, idx) => {{
                                            const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                            const included = llIncentive > 0;
                                            return `
                                                <tr class="${{included ? '' : 'text-muted'}}">
                                                    ${{idx === 0 ? `<td rowspan="${{leaders.length}}">${{groupName}}</td>` : ''}}
                                                    <td>${{ll.name}}</td>
                                                    <td>${{ll.emp_no}}</td>
                                                    <td class="text-end">${{included ? '₫' + llIncentive.toLocaleString('ko-KR') : '-'}}</td>
                                                    <td class="text-center">${{included ? '✅' : '❌'}}</td>
                                                </tr>
                                            `;
                                        }}).join('');
                                    }}).join('')}}
                                </tbody>
                                <tfoot class="table-secondary">
                                    <tr>
                                        <th colspan="3">합계</th>
                                        <th class="text-end">₫${{receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0).toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                    <tr>
                                        <th colspan="3">평균 (수령자 ${{receivingLineLeaders.length}}명 / 전체 ${{teamLineLeaders.length}}명)</th>
                                        <th class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                }}

                calculationDetails = `
                    <div class="calculation-details">
                        <h6>📊 계산 과정 상세 (SUPERVISOR)</h6>
                        <table class="table table-sm">
                            <tr>
                                <td>계산 공식:</td>
                                <td class="text-end"><strong>LINE LEADER 평균 × 2.5</strong></td>
                            </tr>
                            <tr>
                                <td><span class="modal-team-line-leader-count">팀 내 LINE LEADER 수:</span></td>
                                <td class="text-end">${{teamLineLeaders.length}}명 (수령: ${{receivingLineLeaders.length}}명)</td>
                            </tr>
                            <tr>
                                <td>LINE LEADER 평균 인센티브:</td>
                                <td class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</td>
                            </tr>
                            <tr>
                                <td>계산식:</td>
                                <td class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}} × 2.5</td>
                            </tr>
                            <tr class="table-primary">
                                <td><strong>${{getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                            <tr class="${{Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}}">
                                <td><strong>${{getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{employeeIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                        </table>
                        ${{allLineLeaderDetails}}
                    </div>
                `;
                }} else if (position.includes('A.MANAGER') || position.includes('ASSISTANT')) {{
                // A.MANAGER 계산 상세 - 팀 내 LINE LEADER 평균 × 3
                let teamLineLeaders = [];
                let receivingLineLeaders = [];
                let avgLineLeaderIncentive = 0;
                let expectedIncentive = 0;

                // 에러 핸들링을 추가한 팀 LINE LEADER 찾기
                try {{
                    teamLineLeaders = findTeamLineLeaders(employee.emp_no);
                    receivingLineLeaders = teamLineLeaders.filter(ll =>
                        Number(ll[dashboardMonth + '_incentive'] || 0) > 0
                    );
                    avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                        receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
                    expectedIncentive = Math.round(avgLineLeaderIncentive * 3);
                }} catch (err) {{
                    console.error('❌ A.MANAGER 계산 중 오류:', err);
                    teamLineLeaders = [];
                    receivingLineLeaders = [];
                }}

                // LINE LEADER 인센티브 합계 계산
                const lineLeaderTotal = receivingLineLeaders.reduce((sum, ll) =>
                    sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0);

                // 팀 내 LINE LEADER 상세 내역 생성
                let lineLeaderBreakdown = '';
                if (teamLineLeaders.length > 0) {{
                    // LINE LEADER를 GROUP별로 그룹화
                    const lineLeadersByGroup = {{}};
                    teamLineLeaders.forEach(ll => {{
                        const groupLeader = employeeData.find(emp => emp.emp_no === ll.boss_id);
                        const groupName = groupLeader ? groupLeader.name : 'Unknown';
                        if (!lineLeadersByGroup[groupName]) {{
                            lineLeadersByGroup[groupName] = [];
                        }}
                        lineLeadersByGroup[groupName].push(ll);
                    }});

                    lineLeaderBreakdown = `
                        <div class="mt-3">
                            <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                            <table class="table table-sm table-bordered">
                                <thead class="table-light">
                                    <tr>
                                        <th>GROUP LEADER</th>
                                        <th>LINE LEADER</th>
                                        <th>ID</th>
                                        <th class="text-end">인센티브</th>
                                        <th class="text-center">평균 계산 포함</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{Object.entries(lineLeadersByGroup).map(([groupName, leaders]) => {{
                                        return leaders.map((ll, idx) => {{
                                            const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                            const included = llIncentive > 0;
                                            return `
                                                <tr class="${{included ? '' : 'text-muted'}}">
                                                    ${{idx === 0 ? `<td rowspan="${{leaders.length}}">${{groupName}}</td>` : ''}}
                                                    <td>${{ll.name || ll.employee_name || 'Unknown'}}</td>
                                                    <td>${{ll.emp_no || ll.employee_id || ''}}</td>
                                                    <td class="text-end">₫${{llIncentive.toLocaleString('ko-KR')}}</td>
                                                    <td class="text-center">${{included ? '✅' : '❌'}}</td>
                                                </tr>
                                            `;
                                        }}).join('');
                                    }}).join('')}}
                                </tbody>
                                <tfoot class="table-secondary">
                                    <tr>
                                        <th colspan="3">합계</th>
                                        <th class="text-end">₫${{lineLeaderTotal.toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                    <tr>
                                        <th colspan="3">평균 (수령자 ${{receivingLineLeaders.length}}명 / 전체 ${{teamLineLeaders.length}}명)</th>
                                        <th class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                }}

                calculationDetails = `
                    <div class="calculation-details">
                        <h6>📊 계산 과정 상세 (A.MANAGER)</h6>
                        <table class="table table-sm">
                            <tr>
                                <td>계산 공식:</td>
                                <td class="text-end"><strong>LINE LEADER 평균 × 3</strong></td>
                            </tr>
                            <tr>
                                <td>LINE LEADER 수:</td>
                                <td class="text-end">${{teamLineLeaders.length}}명 (수령: ${{receivingLineLeaders.length}}명)</td>
                            </tr>
                            <tr>
                                <td>LINE LEADER 평균 인센티브:</td>
                                <td class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</td>
                            </tr>
                            <tr>
                                <td>계산식:</td>
                                <td class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}} × 3</td>
                            </tr>
                            <tr class="table-primary">
                                <td><strong>${{getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                            <tr class="${{Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}}">
                                <td><strong>${{getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{employeeIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                        </table>
                        ${{lineLeaderBreakdown}}
                    </div>
                `;
                }} else if (position.includes('MANAGER') && !position.includes('A.MANAGER') && !position.includes('ASSISTANT')) {{
                // MANAGER 계산 상세 - 팀 내 LINE LEADER 평균 기준
                const teamLineLeaders = findTeamLineLeaders(employee.emp_no);
                const receivingLineLeaders = teamLineLeaders.filter(ll =>
                    Number(ll[dashboardMonth + '_incentive'] || 0) > 0
                );
                const avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                    receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
                const expectedIncentive = Math.round(avgLineLeaderIncentive * 3.5);

                // 팀 내 LINE LEADER 상세 내역 생성
                let lineLeaderBreakdown = '';
                if (teamLineLeaders.length > 0) {{
                    // LINE LEADER를 GROUP별로 그룹화
                    const lineLeadersByGroup = {{}};
                    teamLineLeaders.forEach(ll => {{
                        const groupLeader = employeeData.find(emp => emp.emp_no === ll.boss_id);
                        const groupName = groupLeader ? groupLeader.name : 'Unknown';
                        if (!lineLeadersByGroup[groupName]) {{
                            lineLeadersByGroup[groupName] = [];
                        }}
                        lineLeadersByGroup[groupName].push(ll);
                    }});

                    lineLeaderBreakdown = `
                        <div class="mt-3">
                            <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                            <table class="table table-sm table-bordered">
                                <thead class="table-light">
                                    <tr>
                                        <th>GROUP LEADER</th>
                                        <th>LINE LEADER</th>
                                        <th>ID</th>
                                        <th class="text-end">인센티브</th>
                                        <th class="text-center">평균 계산 포함</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{Object.entries(lineLeadersByGroup).map(([groupName, leaders]) => {{
                                        return leaders.map((ll, idx) => {{
                                            const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                            const included = llIncentive > 0;
                                            return `
                                                <tr class="${{included ? '' : 'text-muted'}}">
                                                    ${{idx === 0 ? `<td rowspan="${{leaders.length}}">${{groupName}}</td>` : ''}}
                                                    <td>${{ll.name}}</td>
                                                    <td>${{ll.emp_no}}</td>
                                                    <td class="text-end">${{included ? '₫' + llIncentive.toLocaleString('ko-KR') : '-'}}</td>
                                                    <td class="text-center">${{included ? '✅' : '❌'}}</td>
                                                </tr>
                                            `;
                                        }}).join('');
                                    }}).join('')}}
                                </tbody>
                                <tfoot class="table-secondary">
                                    <tr>
                                        <th colspan="3">합계</th>
                                        <th class="text-end">₫${{receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0).toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                    <tr>
                                        <th colspan="3">평균 (수령자 ${{receivingLineLeaders.length}}명 / 전체 ${{teamLineLeaders.length}}명)</th>
                                        <th class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</th>
                                        <th></th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                }}

                calculationDetails = `
                    <div class="calculation-details">
                        <h6>📊 계산 과정 상세 (MANAGER)</h6>
                        <table class="table table-sm">
                            <tr>
                                <td><span class="modal-team-line-leader-count">팀 내 LINE LEADER 수:</span></td>
                                <td class="text-end">${{teamLineLeaders.length}}명</td>
                            </tr>
                            <tr>
                                <td>인센티브 받은 LINE LEADER:</td>
                                <td class="text-end">${{receivingLineLeaders.length}}명</td>
                            </tr>
                            <tr>
                                <td>LINE LEADER 평균 인센티브:</td>
                                <td class="text-end">₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}}</td>
                            </tr>
                            <tr class="table-warning">
                                <td><strong>계산식:</strong></td>
                                <td class="text-end"><strong>₫${{Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}} × 3.5</strong></td>
                            </tr>
                            <tr class="table-primary">
                                <td><strong>${{getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{expectedIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                            <tr class="${{Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}}">
                                <td><strong>${{getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}}:</strong></td>
                                <td class="text-end"><strong>₫${{employeeIncentive.toLocaleString('ko-KR')}}</strong></td>
                            </tr>
                        </table>
                        ${{lineLeaderBreakdown}}
                    </div>
                `;
                }}

                // 모달 HTML 생성
                const monthNumber = dashboardMonth === 'september' ? '9' : dashboardMonth === 'august' ? '8' : dashboardMonth === 'july' ? '7' : '?';
                const modalHtml = `
                <div class="modal fade" id="incentiveModal" tabindex="-1" style="z-index: 1055;">
                    <div class="modal-dialog modal-lg" style="z-index: 1056;">
                        <div class="modal-content" style="z-index: 1057; position: relative; user-select: text; -webkit-user-select: text; -moz-user-select: text; -ms-user-select: text;">
                            <div class="modal-header">
                                <h5 class="modal-title" id="modalTitle">${{getTranslation('modal.modalTitle', currentLanguage)}} - ${{dashboardYear}}년 ${{monthNumber}}월</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="employee-info mb-3">
                                    <h5>${{employee.name}}</h5>
                                    <p class="mb-1"><strong>직급:</strong> ${{employee.position}}</p>
                                    <p class="mb-1"><strong>ID:</strong> ${{employee.emp_no}}</p>
                                    <p class="mb-1"><strong>Type:</strong> ${{employee.type}}</p>
                                </div>
                                <hr>
                                <div class="incentive-summary mb-3">
                                    <h5 class="${{employeeIncentive > 0 ? 'text-success' : 'text-danger'}}">
                                        <span class="modal-actual-incentive">${{getTranslation('orgChart.modalLabels.actualIncentive', currentLanguage)}}</span>: ₫${{employeeIncentive.toLocaleString('ko-KR')}}
                                    </h5>
                                    <p class="text-muted"><span class="modal-calc-method">${{getTranslation('orgChart.modalLabels.calculationMethod', currentLanguage)}}</span>: ${{getCalculationFormula(employee.position) || '특별 계산'}}</p>
                                    ${{(() => {{
                                        if (employeeIncentive === 0) {{
                                            const failureReasons = getIncentiveFailureReasons(employee);
                                            if (failureReasons.length > 0) {{
                                                return `
                                                    <div class="alert alert-warning mt-3">
                                                        <h6 class="alert-heading">📋 <span class="modal-no-payment-reason">${{getTranslation('orgChart.modalLabels.noPaymentReason', currentLanguage)}}</span></h6>
                                                        <ul class="mb-0">
                                                            ${{failureReasons.map(reason => `<li>${{reason}}</li>`).join('')}}
                                                        </ul>
                                                    </div>
                                                `;
                                            }}
                                        }}
                                        return '';
                                    }})()}}
                                </div>
                                ${{calculationDetails}}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"><span class="modal-close-btn">${{getTranslation('buttons.close', currentLanguage) || '닫기'}}</span></button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

                // 기존 모달 제거 (인스턴스 포함)
                const existingModal = document.getElementById('incentiveModal');
                if (existingModal) {{
                    try {{
                        // 기존 Bootstrap 모달 인스턴스 제거
                        const existingModalInstance = bootstrap.Modal.getInstance(existingModal);
                        if (existingModalInstance) {{
                            existingModalInstance.dispose();
                        }}
                        existingModal.remove();
                    }} catch (e) {{
                        console.error('기존 모달 제거 중 오류:', e);
                        existingModal.remove();
                    }}
                }}

                // 모달 추가
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                const modalElement = document.getElementById('incentiveModal');

                // Bootstrap 모달 인스턴스 생성 및 표시
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

                    // 수동으로 백드롭 클릭 이벤트 추가 (Bootstrap이 제대로 처리 안 될 경우 대비)
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

                    // ESC 키 이벤트도 수동 추가
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
                    }}, 300);  // Bootstrap 애니메이션이 완료될 때까지 대기
                    }});

                    // 모달이 표시된 후 포커스 설정
                    modalElement.addEventListener('shown.bs.modal', function() {{
                    console.log('모달 표시 완료');
                    // 닫기 버튼에 포커스 설정
                    const closeBtn = modalElement.querySelector('[data-bs-dismiss="modal"]');
                    if (closeBtn) {{
                            closeBtn.focus();
                        }}
                    }});

                }} catch (error) {{
                    console.error('모달 생성 오류:', error);
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

        // 계산 공식 가져오기
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
            // 제목 및 설명 업데이트
            const titleEl = document.getElementById('orgChartTitle');
            if (titleEl) titleEl.textContent = getTranslation('tabs.orgchart');

            const subtitleEl = document.getElementById('orgChartSubtitle');
            if (subtitleEl) subtitleEl.textContent = getTranslation('orgChart.subtitle');

            // 검색 placeholder
            const searchEl = document.getElementById('orgSearchInput');
            if (searchEl) searchEl.placeholder = getTranslation('orgChart.searchPlaceholder');

            // 버튼 텍스트
            const expandEl = document.getElementById('expandAllText');
            if (expandEl) expandEl.textContent = getTranslation('orgChart.expandAll');

            const collapseEl = document.getElementById('collapseAllText');
            if (collapseEl) collapseEl.textContent = getTranslation('orgChart.collapseAll');

            // 범례
            const legendTitleEl = document.getElementById('legendTitle');
            if (legendTitleEl) legendTitleEl.textContent = getTranslation('orgChart.legendTitle');

            const legendReceivedEl = document.getElementById('legendIncentiveReceived');
            if (legendReceivedEl) legendReceivedEl.textContent = getTranslation('orgChart.incentiveReceived');

            const legendNoIncentiveEl = document.getElementById('legendNoIncentive');
            if (legendNoIncentiveEl) legendNoIncentiveEl.textContent = getTranslation('orgChart.noIncentive');
        }}

        // 조직도 초기화 함수
        function resetOrgChart() {{
            drawCollapsibleOrgChart();
        }}

        // 이전 drawCollapsibleTree 함수는 제거
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
                    .text("조직도 데이터를 불러올 수 없습니다.");
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

                    // 대각선 링크 생성 함수
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
                updateBreadcrumb("접을 수 있는 트리");

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
                console.error("조직도 생성 오류:", error);
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
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
                    // 레벨별로 다른 간격 적용
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
                    .style("stroke-width", d => Math.max(1, 3 - d.target.depth)) // 깊이에 따라 두께 조정
                    .style("opacity", d => Math.max(0.3, 1 - d.target.depth * 0.15)) // 깊이에 따라 투명도
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

                // 노드 원 (크기를 깊이에 따라 조정, 인센티브 여부에 따라 색상)
                node.append("circle")
                    .attr("r", d => Math.max(4, 8 - d.depth)) // 깊이에 따라 크기 조정
                    .style("fill", d => {{
                        const baseColor = getPositionColor(d.data.position);
                        // 인센티브 여부에 따라 채우기 색상
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
                            타입: ${{d.data.type || 'N/A'}}<br/>
                            인센티브: ${{hasIncentive(d.data) ? '수령' : '미수령'}}
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

                // 초기 줌을 전체가 잘 보이도록 설정
                svg.call(zoom.transform, d3.zoomIdentity.scale(0.8));

                // Breadcrumb 업데이트
                updateBreadcrumb("방사형 트리");

            }} catch (error) {{
                console.error("방사형 조직도 생성 오류:", error);
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
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

            svg.selectAll("*").remove(); // 기존 내용 제거

            const g = svg.append("g")
                .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

            // nodeSize를 사용하여 고정된 노드 간격 설정
            const treeLayout = d3.tree()
                .nodeSize([50, 200]) // [수직 간격, 수평 간격] 늘림
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

                // 업데이트 함수 정의
                function update(source) {{
                    // 트리 레이아웃 계산
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

                    // 종료 노드 처리
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
                        .data(links, d => d.target.id);

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
                        .attr("d", d => diagonal(d.source, d.target));

                    // 종료 링크 처리
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

                    // 대각선 경로 생성 함수
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

                // 초기 줌 설정 (전체가 보이도록)
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
                updateBreadcrumb("수평 트리 (클릭하여 접기/펼치기)");

            }} catch (error) {{
                console.error("수평 조직도 생성 오류:", error);
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
            }}
        }}

        function drawTreemap() {{
            console.log('Treemap deprecated - using collapsible tree');
            return;
            const containerWidth = container.node().getBoundingClientRect().width;
            const width = Math.max(1200, containerWidth);
            const height = 800;

            // 기존 SVG 숨기고 내용 제거
            d3.select("#orgChartSvg")
                .style("display", "none")
                .selectAll("*").remove();

            // 기존 treemap div 제거
            d3.select("#treemapDiv").remove();

            // treemap을 위한 컨테이너 div 생성
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
                // 계층 구조 생성
                const root = d3.stratify()
                    .id(d => d.id)
                    .parentId(d => d.parentId)(hierarchyData);

                // 각 노드의 value 계산 (자식이 없으면 1, 있으면 자식 수)
                root.sum(d => d.children ? 0 : 1)
                    .sort((a, b) => b.value - a.value);

                // Treemap 레이아웃 생성
                d3.treemap()
                    .size([width, height])
                    .padding(2)
                    .round(true)(root);

                // 색상 맵핑
                const colorScale = d3.scaleOrdinal()
                    .domain(['MANAGER', 'SUPERVISOR', 'GROUP LEADER', 'LINE LEADER', 'INSPECTOR', 'Others'])
                    .range(['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']);

                // 노드 생성
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
                        // 인센티브 여부에 따라 그라데이션 조정
                        if (hasIncentive(d.data)) {{
                            return `linear-gradient(135deg, ${{color}}, ${{d3.color(color).darker(0.3)}})`;
                        }} else {{
                            // 인센티브 미수령자는 더 어두운 색상
                            return `linear-gradient(135deg, ${{d3.color(color).darker(0.5)}}, ${{d3.color(color).darker(0.8)}})`;
                        }}
                    }})
                    .style("border", d => {{
                        // 인센티브 여부에 따라 테두리 색상
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

                // Tooltip 함수들
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
                        타입: ${{d.data.type}}<br/>
                        인센티브: ${{hasIncentive(d.data) ?
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
                console.error("트리맵 생성 오류:", error);
                treemapDiv.append("div")
                    .style("text-align", "center")
                    .style("padding", "20px")
                    .text("트리맵 생성 중 오류가 발생했습니다: " + error.message);
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
            updateBreadcrumb("수직 트리 (기본)");

            const g = svg.append("g")
                .attr("transform", `translate(${{width / 2}},${{margin.top}})`); // 중앙 정렬

            // 데이터 준비
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
                    .text("데이터 준비 중 오류: " + error.message);
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
                    .text("조직도 데이터를 불러올 수 없습니다. 데이터를 확인해주세요.");
                return;
            }}

            // D3 계층 구조 생성
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

                // 수직 트리 레이아웃 생성 - nodeSize 사용으로 더 유연한 간격
                const treeLayout = d3.tree()
                    .nodeSize([250, 200]) // [수평 간격, 수직 간격] - 크게 증가시켜 오버랩 방지
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
                    // Inspector들을 부모별로 그룹화
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
                        const maxPerRow = 8; // 한 줄에 최대 8명

                        group.forEach((node, index) => {{
                            const row = Math.floor(index / maxPerRow);
                            const col = index % maxPerRow;
                            const groupCenter = group[0].parent ? group[0].parent.x : 0;

                            // 수평 위치: 그룹 중앙을 기준으로 배치
                            const totalWidth = Math.min(maxPerRow, group.length) * 100;
                            const startX = groupCenter - totalWidth / 2;
                            node.x = startX + col * 100;

                            // 수직 위치: 행에 따라 조정
                            if (row > 0) {{
                                node.y = node.y + row * 100;
                            }}
                        }});
                    }});
                }}

                // 링크 그리기 - 수직 연결선
                const link = g.selectAll(".link")
                    .data(orgChartRoot.links())
                    .enter().append("g")
                    .attr("class", "link");

                // 계단식 연결선 (더 명확한 계층 표현)
                link.append("path")
                    .attr("fill", "none")
                    .attr("stroke", "#999")
                    .attr("stroke-width", 2)
                    .attr("d", d => {{
                        // 수직 계단식 경로
                        const sourceX = d.source.x - width / 2 + margin.left;
                        const sourceY = d.source.y;
                        const targetX = d.target.x - width / 2 + margin.left;
                        const targetY = d.target.y;
                        const midY = (sourceY + targetY) / 2;

                        return `M ${{sourceX}} ${{sourceY}}
                                L ${{sourceX}} ${{midY}}
                                L ${{targetX}} ${{midY}}
                                L ${{targetX}} ${{targetY}}`;
                    }});

                // 노드 그룹 생성
                const node = g.selectAll(".node")
                    .data(orgChartRoot.descendants())
                    .enter().append("g")
                    .attr("class", "node")
                    .attr("transform", d => `translate(${{d.x - width / 2 + margin.left}},${{d.y}})`)
                    .on("mouseover", showTooltip)
                    .on("mouseout", hideTooltip)
                    .on("click", nodeClick);

                // 노드 박스 그리기 (인센티브 여부에 따라 색상 변경)
                node.append("rect")
                    .attr("width", 180)  // 박스 폭 더 크게 (ID 추가를 위해)
                    .attr("height", 90)  // 박스 높이 더 크게
                    .attr("x", -90)
                    .attr("y", -45)
                    .attr("fill", d => {{
                        const baseColor = getNodeColor(d.data);
                        // 인센티브 수령 여부에 따라 색상 조정
                        if (hasIncentive(d.data)) {{
                            return baseColor; // 원래 색상 유지
                        }} else {{
                            return baseColor + "40"; // 40% 투명도로 희미하게
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

                // 초기 줌 레벨 설정 (전체가 보이도록) - 더 작게
                const initialScale = 0.4;  // 더 작은 초기 줌 (전체 조직도가 보이도록)
                svg.call(currentZoomBehavior.transform, d3.zoomIdentity
                    .translate(width / 2, margin.top)
                    .scale(initialScale));

            }} catch (error) {{
                console.error("조직도 생성 오류:", error);
                console.error("Error details:", error.message);
                console.error("Error stack:", error.stack);
                console.error("Problematic data sample:", hierarchyData ? hierarchyData.slice(0, 5) : 'No data');

                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("text-anchor", "middle")
                    .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
            }}
        }}

        function prepareHierarchyData() {{
            console.log('Preparing organization hierarchy data...');
            console.log('Total employees:', employeeData.length);

            // 먼저 데이터가 비어있는지 확인
            if (!employeeData || employeeData.length === 0) {{
                console.error('No employee data available!');
                return [];
            }}

            // 첫 몇 명의 직원 데이터 확인
            console.log('First employee sample:', employeeData[0]);

            // 제외할 포지션 정의
            const excludedPositions = ['MODEL MASTER', 'AUDIT & TRAINING TEAM', 'AQL INSPECTOR'];

            // TYPE-1 직원 중 특정 포지션 제외
            const type1Employees = employeeData.filter(e =>
                e.type === 'TYPE-1' &&
                !excludedPositions.includes(e.position)
            );
            console.log('TYPE-1 employees (excluding excluded positions):', type1Employees.length);

            // 전략 결정: TYPE-1이 너무 적으면 전체 조직도 표시
            let useAllEmployees = false;
            let requiredIds = new Set();

            if (type1Employees.length < 5) {{
                console.log('Too few TYPE-1 employees, showing full organization chart');
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

                // 상사 체인을 재귀적으로 추가 (실제 존재하는 직원만)
                const addBossChain = (empId) => {{
                    const emp = employeeData.find(e => e.emp_no === empId);
                    if (!emp) return;

                    if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== '0') {{
                        // 상사가 실제로 employeeData에 존재하는지 확인
                        const bossExists = employeeData.some(e => e.emp_no === emp.boss_id);

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

            console.log('Total required nodes:', requiredIds.size, useAllEmployees ? '(showing all employees)' : '(TYPE-1 + bosses)');

            // 디버깅: 첫 5개 직원 데이터 확인
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

            // 직원 ID 맵 생성 (빈 데이터 필터링)
            employeeData.forEach(emp => {{
                // nan이거나 빈 emp_no는 제외
                if (emp.emp_no && emp.emp_no !== 'nan' && emp.emp_no !== '') {{
                    employeeById[emp.emp_no] = emp;
                }}
            }});

            // 모든 직원을 노드로 추가 (실제 boss_id 사용)
            let noParentCount = 0;
            let hasParentCount = 0;

            employeeData.forEach(emp => {{
                // 빈 데이터 건너뛰기
                if (!emp.emp_no || emp.emp_no === 'nan' || emp.emp_no === '') {{
                    return;
                }}

                // 제외할 포지션이면 건너뛰기
                if (excludedPositions.includes(emp.position)) {{
                    console.log(`Excluding ${{emp.name}} (${{emp.position}}) from org chart`);
                    return;
                }}

                // 필요한 직원이 아니면 건너뛰기 (TYPE-1이거나 TYPE-1의 상사 체인에 포함)
                if (!requiredIds.has(emp.emp_no)) {{
                    return;
                }}

                // boss_id가 있으면 사용, 없으면 boss_name으로 찾기
                let parentId = null;

                if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== 'None' && emp.boss_id !== '0') {{
                    // boss_id가 직원 목록에 있고 requiredIds에도 포함되어 있는지 확인
                    if (employeeById[emp.boss_id] && requiredIds.has(emp.boss_id)) {{
                        parentId = emp.boss_id;
                    }} else if (employeeById[emp.boss_id]) {{
                        // 상사가 존재하지만 TYPE-1 체인에 포함되지 않음
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
                    incentive: emp[dashboardMonth + '_incentive'] || '0',
                    parentId: parentId
                }});
            }});

            console.log(`Created ${{data.length}} nodes: ${{hasParentCount}} with parent, ${{noParentCount}} without parent`);

            // 루트 노드 확인
            const rootNodes = data.filter(d => !d.parentId);
            console.log('Root nodes found:', rootNodes.length);

            // 항상 가상 루트 생성 (조직도의 시작점)
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
                    // Manager 또는 상위 직급만 루트에 직접 연결
                    const pos = (node.position || '').toUpperCase();
                    if (pos.includes('MANAGER') || pos.includes('SUPERVISOR') || rootNodes.length <= 5) {{
                        const idx = data.findIndex(d => d.id === node.id);
                        if (idx !== -1) {{
                            data[idx].parentId = "root";
                        }}
                    }}
                    // 그 외는 적절한 상위 직급 찾기
                    else {{
                        // 같은 타입의 상위 직급 찾기
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




            // 필터 적용
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
                사번: ${{d.data.id}}<br/>
                직급: ${{d.data.position}}<br/>
                Type: ${{d.data.type}}<br/>
                인센티브: ${{incentive.toLocaleString()}} VND<br/>
                상사: ${{d.data.boss_name || '없음'}}
            `);

            tooltip.style("visibility", "visible")
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}

        function hideTooltip() {{
            d3.select("#orgTooltip").style("visibility", "hidden");
        }}

        function nodeClick(event, d) {{
            // 노드 클릭시 해당 직원 상세 정보 표시
            const emp = employeeData.find(e => e.emp_no === d.data.id);
            if (emp) {{
                showEmployeeDetail(emp);
            }}
        }}

        function updateOrgChart() {{
            drawOrgChart();
        }}

        function resetOrgChart() {{
            const typeFilterElement = document.getElementById('orgTypeFilter');
            const incentiveFilterElement = document.getElementById('orgIncentiveFilter');

            if (typeFilterElement) typeFilterElement.value = '';
            if (incentiveFilterElement) incentiveFilterElement.value = '';
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
            // 저장된 언어 설정 복원
            const savedLang = localStorage.getItem('dashboardLanguage') || 'ko';
            currentLanguage = savedLang;
            document.getElementById('languageSelector').value = savedLang;
            
            generateEmployeeTable();
            generatePositionTables();
            updatePositionFilter();
            updateAllTexts();
            updateTalentPoolSection();
            updateTypeSummaryTable();  // Type별 요약 테이블 업데이트 추가
        }};
        
        // Talent Program 텍스트 업데이트 함수
        function updateTalentProgramTexts() {{
            const lang = currentLanguage;
            
            // 메인 제목
            const programTitle = document.getElementById('talentProgramTitle');
            if (programTitle) {{
                programTitle.innerHTML = getTranslation('talentProgram.title', lang) || '🌟 QIP Talent Pool 인센티브 프로그램';
            }}
            
            // 소개 텍스트
            const programIntro = document.getElementById('talentProgramIntro');
            if (programIntro) {{
                programIntro.innerHTML = `<strong>QIP Talent Pool</strong> ${{getTranslation('talentProgram.intro', lang) || 'QIP Talent Pool은 우수한 성과를 보이는 인원들을 대상으로 하는 특별 인센티브 프로그램입니다. 선정된 인원은 6개월간 매월 추가 보너스를 받게 됩니다.'}}`;
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
                monthlyBonusTitle.textContent = getTranslation('talentProgram.monthlyBonusTitle', lang) || '월 특별 보너스';
            }}
            
            // 총 보너스 제목
            const totalBonusTitle = document.getElementById('talentProgramTotalBonusTitle');
            if (totalBonusTitle) {{
                totalBonusTitle.textContent = getTranslation('talentProgram.totalBonusTitle', lang) || '총 지급 예정액 (6개월)';
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
                    descEn: 'Departments nominate outstanding employees',
                    descVi: 'Các phòng ban đề cử nhân viên xuất sắc'
                }},
                {{
                    titleId: 'talentStep2Title',
                    descId: 'talentStep2Desc',
                    titleKo: '성과 평가',
                    titleEn: 'Performance Evaluation',
                    titleVi: 'Đánh giá hiệu suất',
                    descKo: '최근 3개월간 성과 데이터 분석',
                    descEn: 'Analysis of last 3 months performance data',
                    descVi: 'Phân tích dữ liệu hiệu suất 3 tháng gần nhất'
                }},
                {{
                    titleId: 'talentStep3Title',
                    descId: 'talentStep3Desc',
                    titleKo: '위원회 심사',
                    titleEn: 'Committee Review',
                    titleVi: 'Xét duyệt của ủy ban',
                    descKo: 'QIP 운영위원회 최종 심사',
                    descEn: 'Final review by QIP committee',
                    descVi: 'Xét duyệt cuối cùng bởi ủy ban QIP'
                }},
                {{
                    titleId: 'talentStep4Title',
                    descId: 'talentStep4Desc',
                    titleKo: '최종 선정',
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
                    descKo: '매월 정기 인센티브와 함께 지급',
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
                    'Talent Pool 보너스는 기본 인센티브와 별도로 지급됩니다',
                    
                    lang === 'en' ? 'Eligibility is automatically lost upon resignation during the payment period' :
                    lang === 'vi' ? 'Tư cách sẽ tự động mất khi nghỉ việc trong thời gian thanh toán' :
                    '지급 기간 중 퇴사 시 자격이 자동 상실됩니다',
                    
                    lang === 'en' ? 'May be terminated early if performance is insufficient' :
                    lang === 'vi' ? 'Có thể kết thúc sớm nếu hiệu suất không đủ' :
                    '성과 미달 시 조기 종료될 수 있습니다',
                    
                    lang === 'en' ? 'Renewal is determined through re-evaluation every 6 months' :
                    lang === 'vi' ? 'Việc gia hạn được quyết định thông qua đánh giá lại mỗi 6 tháng' :
                    '매 6개월마다 재평가를 통해 갱신 여부가 결정됩니다'
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
            if (currentMembersDiv && currentMembersDiv.innerHTML.includes('현재 Talent Pool 멤버가 없습니다')) {{
                currentMembersDiv.innerHTML = `<p>${{getTranslation('talentProgram.noMembers', lang) || '현재 Talent Pool 멤버가 없습니다.'}}</p>`;
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
                
                document.getElementById('talentPoolCount').textContent = talentPoolMembers.length + '명';
                document.getElementById('talentPoolMonthlyBonus').textContent = parseInt(monthlyBonus).toLocaleString() + ' VND';
                document.getElementById('talentPoolTotalBonus').textContent = totalBonus.toLocaleString() + ' VND';
                document.getElementById('talentPoolPeriod').textContent = '2025.07 - 2025.12';
                
                // 멤버 목록 생성
                const membersLabel = getTranslation('talentPool.membersList', currentLanguage) || 'Talent Pool 멤버:';
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
                
                // 인센티브 기준 탭의 Talent Program 현재 멤버 섹션도 업데이트
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
                        currentMembersHtml = '<p>현재 Talent Pool 멤버가 없습니다.</p>';
                    }}
                    currentMembersDiv.innerHTML = currentMembersHtml;
                }}
            }} else {{
                // Talent Pool 멤버가 없는 경우
                const currentMembersDiv = document.getElementById('talentProgramCurrentMembers');
                if (currentMembersDiv) {{
                    currentMembersDiv.innerHTML = '<p>현재 Talent Pool 멤버가 없습니다.</p>';
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

            // 조직도 탭이면 조직도 그리기
            if (tabName === 'orgchart') {{
                console.log('Organization chart tab selected');
                setTimeout(() => {{
                    console.log('Calling drawOrgChart from showTab...');
                    drawOrgChart();
                }}, 100);
            }}
        }}
        
        // 직원 테이블 생성
        function generateEmployeeTable() {{
            const tbody = document.getElementById('employeeTableBody');
            tbody.innerHTML = '';
            
            employeeData.forEach(emp => {{
                const amount = parseInt(emp[dashboardMonth + '_incentive']);
                const isPaid = amount > 0;
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                tr.onclick = () => showEmployeeDetail(emp.emp_no);
                
                // Talent Pool 멤버인 경우 특별 스타일 적용
                if (emp.Talent_Pool_Member === 'Y') {{
                    tr.className = 'talent-pool-row';
                }}
                
                // Talent Pool 정보 HTML 생성
                let talentPoolHTML = '-';
                if (emp.Talent_Pool_Member === 'Y') {{
                    talentPoolHTML = `
                        <div class="talent-pool-tooltip">
                            <span class="talent-pool-star">🌟</span>
                            <strong>${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND</strong>
                            <span class="tooltiptext">
                                <strong>${{getTranslation('talentPool.special', currentLanguage) || 'QIP Talent Pool'}}</strong><br>
                                ${{getTranslation('talentPool.monthlyBonus', currentLanguage) || '월 특별 보너스'}}: ${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND<br>
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
                    <td>${{parseInt(emp.july_incentive).toLocaleString()}}</td>
                    <td><strong>${{amount.toLocaleString()}}</strong></td>
                    <td>${{talentPoolHTML}}</td>
                    <td>${{isPaid ? '✅ ' + getTranslation('status.paid') : '❌ ' + getTranslation('status.unpaid')}}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${{emp.emp_no}}')">${{getTranslation('individual.table.detailButton')}}</button></td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        // 직급별 테이블 생성 (dashboard_version4.html과 동일한 UI)
        function generatePositionTables() {{
            const positionData = {{}};
            
            // Type-직급별 데이터 집계
            employeeData.forEach(emp => {{
                const key = `${{emp.type}}_${{emp.position}}`;
                if (!positionData[key]) {{
                    positionData[key] = {{
                        type: emp.type,
                        position: emp.position,
                        total: 0,
                        paid: 0,
                        totalAmount: 0,
                        employees: []
                    }};
                }}
                
                positionData[key].total++;
                positionData[key].employees.push(emp);
                const amount = parseInt(emp[dashboardMonth + '_incentive']) || 0;
                if (amount > 0) {{
                    positionData[key].paid++;
                    positionData[key].totalAmount += amount;
                }}
            }});
            
            // Type별로 그룹핑
            const groupedByType = {{}};
            Object.values(positionData).forEach(data => {{
                if (!groupedByType[data.type]) {{
                    groupedByType[data.type] = [];
                }}
                groupedByType[data.type].push(data);
            }});
            
            // HTML 생성
            const container = document.getElementById('positionTables');
            if (container) {{
                container.innerHTML = '';
                
                // Type별로 섹션 생성
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
                        const avgAmount = posData.paid > 0 ? Math.round(posData.totalAmount / posData.paid) : 0;
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
                    
                    // Type별 소계
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
        
        // 직급별 상세 팝업 - 완전 새로운 UI
        function showPositionDetail(type, position) {{
            const employees = employeeData.filter(e => e.type === type && e.position === position);
            if (employees.length === 0) return;
            
            const modal = document.getElementById('employeeModal');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');
            
            modalTitle.innerHTML = `${{type}} - ${{position}} ` + getTranslation('modal.modalTitle', currentLanguage);
            
            // 요약 통계 계산
            const totalEmployees = employees.length;
            const paidEmployees = employees.filter(e => parseInt(e[dashboardMonth + '_incentive']) > 0).length;
            const avgIncentive = Math.round(employees.reduce((sum, e) => sum + parseInt(e[dashboardMonth + '_incentive']), 0) / totalEmployees);
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
            
            // 실제 인센티브 기준으로 통계 계산 (방안 2 적용)
            const actualPassCount = employees.filter(emp => parseInt(emp[dashboardMonth + '_incentive']) > 0).length;
            const actualFailCount = employees.filter(emp => parseInt(emp[dashboardMonth + '_incentive']) === 0).length;

            // 각 직원의 조건 충족 통계 계산 (참고용 유지)
            const conditionStats = {{}};
            if (employees[0] && employees[0].condition_results) {{
                employees[0].condition_results.forEach(cond => {{
                    const translationKey = conditionTranslationMap[cond.id] || null;
                    const translatedName = translationKey ? getTranslation(translationKey, currentLanguage) : cond.name;
                    conditionStats[cond.id] = {{
                        name: translatedName,
                        met: 0,
                        total: 0,
                        na_count: 0
                    }};
                }});

                employees.forEach(emp => {{
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
            
            // 인센티브 통계 계산
            const incentiveAmounts = employees.map(emp => parseInt(emp[dashboardMonth + '_incentive'])).filter(amt => amt > 0);
            const maxIncentive = incentiveAmounts.length > 0 ? Math.max(...incentiveAmounts) : 0;
            const minIncentive = incentiveAmounts.length > 0 ? Math.min(...incentiveAmounts) : 0;
            const medianIncentive = incentiveAmounts.length > 0 ? 
                incentiveAmounts.sort((a, b) => a - b)[Math.floor(incentiveAmounts.length / 2)] : 0;
            
            let modalContent = `
                <div style="display: grid; grid-template-columns: 1fr; gap: 20px; padding: 20px;">
                    <!-- 인센티브 통계 (1행 4열 배치) -->
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
                    
                    <!-- 인센티브 수령 상세 및 조건별 통계 -->
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
                                        <th width="40%">${{getTranslation('modal.condition', currentLanguage)}}</th>
                                        <th width="20%">${{getTranslation('modal.evaluationTarget', currentLanguage)}}</th>
                                        <th width="15%">${{getTranslation('modal.fulfilled', currentLanguage)}}</th>
                                        <th width="15%">${{getTranslation('modal.notFulfilled', currentLanguage)}}</th>
                                        <th width="15%">${{getTranslation('modal.fulfillmentRate', currentLanguage)}}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{Object.entries(conditionStats).map(([id, stat], index) => {{
                                        const isNA = stat.na_count > 0 && stat.total === 0;  // 모든 직원이 N/A인 경우
                                        const rate = stat.total > 0 ? Math.round((stat.met / stat.total) * 100) : 0;
                                        const unmet = stat.total - stat.met;
                                        const evaluatedCount = stat.total;  // N/A가 아닌 평가 대상자 수
                                        
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
                    </div>
                    
                    <!-- 직원별 상세 현황 -->
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
            
            employees.forEach(emp => {{
                const amount = parseInt(emp[dashboardMonth + '_incentive']);
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
                                    
                                    // 출근 카테고리 평가
                                    if (attendance.length > 0) {{
                                        const attendanceNA = attendance.every(c => c.is_na || c.actual === 'N/A');
                                        // N/A가 아닌 조건들만 필터링하여 평가
                                        const applicableAttendance = attendance.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const attendanceMet = applicableAttendance.length > 0 && applicableAttendance.every(c => c.is_met);
                                        if (attendanceNA) {{
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ': N/A</span>');
                                        }} else if (attendanceMet) {{
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✓</span>');
                                        }} else {{
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✗</span>');
                                        }}
                                    }}
                                    
                                    // AQL 카테고리 평가
                                    if (aql.length > 0) {{
                                        const aqlNA = aql.every(c => c.is_na || c.actual === 'N/A');
                                        // N/A가 아닌 조건들만 필터링하여 평가
                                        const applicableAql = aql.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const aqlMet = applicableAql.length > 0 && applicableAql.every(c => c.is_met);
                                        if (aqlNA) {{
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ': N/A</span>');
                                        }} else if (aqlMet) {{
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✓</span>');
                                        }} else {{
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✗</span>');
                                        }}
                                    }} else {{
                                        badges.push('<span class="badge" style="background-color: #999;" title="AQL 조건">AQL: N/A</span>');
                                    }}
                                    
                                    // 5PRS 카테고리 평가
                                    if (prs.length > 0) {{
                                        const prsNA = prs.every(c => c.is_na || c.actual === 'N/A');
                                        // N/A가 아닌 조건들만 필터링하여 평가
                                        const applicablePrs = prs.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const prsMet = applicablePrs.length > 0 && applicablePrs.every(c => c.is_met);
                                        if (prsNA) {{
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ': N/A</span>');
                                        }} else if (prsMet) {{
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✓</span>');
                                        }} else {{
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✗</span>');
                                        }}
                                    }} else {{
                                        badges.push('<span class="badge" style="background-color: #999;" title="5PRS 조건">5PRS: N/A</span>');
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
            modal.style.display = 'block';
            
            // 모달 스크롤 초기화 (맨 위로)
            modalBody.scrollTop = 0;
            document.querySelector('.modal-content').scrollTop = 0;
            
            // Event delegation을 사용하여 직원 행 클릭 이벤트 처리
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
                
                // 새로운 이벤트 핸들러 생성 및 저장
                window.positionTableClickHandler = function(event) {{
                    // tbody 내의 tr을 찾기
                    const row = event.target.closest('tbody tr.employee-row');
                    if (!row) return;
                    
                    // data-emp-no 속성에서 직원번호 가져오기
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
                    
                    // 기존 차트 삭제
                    if (window[`chart_${{chartId}}`]) {{
                        window[`chart_${{chartId}}`].destroy();
                    }}
                    
                    // 새 차트 생성
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
        
        // 직급별 상세 팝업에서 호출하는 개인별 상세 팝업 함수
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
        
        // 직원 상세 정보 표시 (대시보드 스타일 UI)
        function showEmployeeDetail(empNo) {{
            const emp = employeeData.find(e => e.emp_no === empNo);
            if (!emp) return;
            
            const modal = document.getElementById('employeeModal');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');
            
            modalTitle.textContent = `${{emp.name}} (${{emp.emp_no}}) - ${{getTranslation('modal.title')}}`;
            
            // 조건 충족 통계 계산 - N/A 제외
            const conditions = emp.condition_results || [];
            const applicableConditions = conditions.filter(c => !c.is_na && c.actual !== 'N/A');
            const passedConditions = applicableConditions.filter(c => c.is_met).length;
            const totalConditions = applicableConditions.length;
            const passRate = totalConditions > 0 ? (passedConditions / totalConditions * 100).toFixed(0) : 0;
            
            modalBody.innerHTML = `
                <!-- 상단 통계 카드 -->
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{emp.type}}</div>
                            <div class="stat-label">${{getTranslation('modal.basicInfo.type')}}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{emp.position}}</div>
                            <div class="stat-label">${{getTranslation('modal.basicInfo.position')}}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{parseInt(emp[dashboardMonth + '_incentive']).toLocaleString()}} VND</div>
                            <div class="stat-label">${{getTranslation('modal.incentiveInfo.amount')}}</div>
                        </div>
                    </div>
                </div>
                
                <!-- 차트와 조건 충족도 -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6 class="card-title">` + getTranslation('modal.detailPopup.conditionFulfillment', currentLanguage) + `</h6>
                                <div style="width: 200px; height: 200px; margin: 0 auto; position: relative;">
                                    <canvas id="conditionChart${{empNo}}"></canvas>
                                </div>
                                <div class="mt-3">
                                    <h4>${{passRate}}%</h4>
                                    <p class="text-muted">${{totalConditions > 0 ? passedConditions + ' / ' + totalConditions + ' ' + getTranslation('modal.detailPopup.conditionsFulfilled', currentLanguage) : getTranslation('modal.detailPopup.noConditions', currentLanguage)}}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h6 class="card-title">` + getTranslation('modal.detailPopup.paymentStatus', currentLanguage) + `</h6>
                                <div class="payment-status ${{parseInt(emp[dashboardMonth + '_incentive']) > 0 ? 'paid' : 'unpaid'}}">
                                    ${{parseInt(emp[dashboardMonth + '_incentive']) > 0 ? `
                                    <div>
                                        <i class="fas fa-check-circle"></i>
                                        <h5>` + getTranslation('modal.payment.paid', currentLanguage) + `</h5>
                                        <p class="mb-1">${{parseInt(emp[dashboardMonth + '_incentive']).toLocaleString()}} VND</p>
                                        ${{emp.Talent_Pool_Member === 'Y' ? `
                                        <div style="background: linear-gradient(135deg, #FFD700, #FFA500); padding: 8px; border-radius: 8px; margin-top: 10px;">
                                            <small style="color: white; font-weight: bold;">
                                                🌟 Talent Pool 보너스 포함<br>
                                                기본: ${{(parseInt(emp[dashboardMonth + '_incentive']) - parseInt(emp.Talent_Pool_Bonus || 0)).toLocaleString()}} VND<br>
                                                보너스: +${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND
                                            </small>
                                        </div>` : ''}}
                                    </div>` : `
                                    <div>
                                        <i class="fas fa-times-circle"></i>
                                        <h5>` + getTranslation('status.unpaid', currentLanguage) + `</h5>
                                        <p>` + getTranslation('modal.detailPopup.conditionNotMet', currentLanguage) + `</p>
                                    </div>`}}
                                </div>
                                <div class="mt-3">
                                    <small class="text-muted">` + getTranslation('modal.detailPopup.lastMonthIncentive', currentLanguage) + `: ${{parseInt(emp.july_incentive).toLocaleString()}} VND</small>
                                </div>
                            </div>
                        </div>
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
                                    ${{conditions.map((cond, idx) => {{
                                        const isNA = cond.is_na || cond.actual === 'N/A';
                                        let rowClass = '';
                                        let badgeHtml = '';
                                        let actualHtml = '';
                                        
                                        if (isNA) {{
                                            actualHtml = '<span style="color: #999;">N/A</span>';
                                            badgeHtml = '<span class="badge" style="background-color: #999;">N/A</span>';
                                        }} else {{
                                            rowClass = cond.is_met ? 'table-success' : 'table-danger';
                                            
                                            // 실적 값의 단위 번역 처리
                                            let actualValue = cond.actual;
                                            if (actualValue && typeof actualValue === 'string') {{
                                                // "0일" -> "0 days" / "0 ngày"
                                                actualValue = actualValue.replace(/(\\d+)일/g, function(match, num) {{
                                                    const dayUnit = parseInt(num) <= 1 ? getTranslation('common.day', currentLanguage) : getTranslation('common.days', currentLanguage);
                                                    return num + (currentLanguage === 'ko' ? dayUnit : ' ' + dayUnit);
                                                }});
                                                // "0건" -> "0 cases" / "0 trường hợp"  
                                                actualValue = actualValue.replace(/(\\d+)건/g, function(match, num) {{
                                                    if (currentLanguage === 'en') return num + (parseInt(num) <= 1 ? ' case' : ' cases');
                                                    if (currentLanguage === 'vi') return num + ' trường hợp';
                                                    return match;
                                                }});
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
            
            modal.style.display = 'block';
            
            // 모달 스크롤 초기화 (맨 위로)
            modalBody.scrollTop = 0;
            document.querySelector('.modal-content').scrollTop = 0;
            
            // 차트 그리기
            setTimeout(() => {{
                const canvas = document.getElementById(`conditionChart${{empNo}}`);
                if (canvas) {{
                    const ctx = canvas.getContext('2d');
                    
                    // 기존 차트 삭제
                    if (window[`chart_${{empNo}}`]) {{
                        window[`chart_${{empNo}}`].destroy();
                    }}
                    
                    // 새 차트 생성
                    window[`chart_${{empNo}}`] = new Chart(ctx, {{
                        type: 'doughnut',
                        data: {{
                            labels: [getTranslation('modal.conditions.met', currentLanguage), getTranslation('modal.conditions.notMet', currentLanguage)],
                            datasets: [{{
                                data: [passedConditions, Math.max(0, totalConditions - passedConditions)],
                                backgroundColor: ['#28a745', '#dc3545'],
                                borderWidth: 0
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{
                                    position: 'bottom'
                                }}
                            }}
                        }}
                    }});
                }}
            }}, 100);
        }}
        
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
        
        // 모달 외부 클릭 시 닫기
        window.onclick = function(event) {{
            const modal = document.getElementById('employeeModal');
            if (event.target === modal) {{
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
                const amount = parseInt(emp[dashboardMonth + '_incentive']);
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
                
                // Talent Pool 멤버인 경우 특별 스타일 적용
                if (emp.Talent_Pool_Member === 'Y') {{
                    tr.className = 'talent-pool-row';
                }}
                
                // Talent Pool 정보 HTML 생성
                let talentPoolHTML = '-';
                if (emp.Talent_Pool_Member === 'Y') {{
                    talentPoolHTML = `
                        <div class="talent-pool-tooltip">
                            <span class="talent-pool-star">🌟</span>
                            <strong>${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND</strong>
                            <span class="tooltiptext">
                                <strong>${{getTranslation('talentPool.special', currentLanguage) || 'QIP Talent Pool'}}</strong><br>
                                ${{getTranslation('talentPool.monthlyBonus', currentLanguage) || '월 특별 보너스'}}: ${{parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()}} VND<br>
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
                    <td>${{parseInt(emp.july_incentive).toLocaleString()}}</td>
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
            
            // 직급 목록 수집
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
    """Google Drive에서 데이터 동기화"""
    try:
        print("\n🔄 Google Drive 데이터 동기화 시작...")
        drive_manager = GoogleDriveManager()
        
        # 인센티브 데이터 다운로드
        file_pattern = f"{year}년 {month_num}월 인센티브"
        files = drive_manager.download_files(file_pattern, 'input_files')
        
        if files:
            print(f"✅ {len(files)}개 파일 동기화 완료")
            for file in files:
                print(f"   - {file}")
            return True
        else:
            print("⚠️ Google Drive에서 해당 월 데이터를 찾을 수 없습니다")
            return False
    except Exception as e:
        print(f"❌ Google Drive 동기화 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    # 번역 파일 로드
    load_translations()
    
    parser = argparse.ArgumentParser(description='통합 인센티브 대시보드 생성')
    parser.add_argument('--month', type=int, default=8, help='월 (1-12)')
    parser.add_argument('--year', type=int, default=2025, help='연도')
    parser.add_argument('--sync', action='store_true', help='Google Drive 동기화')
    args = parser.parse_args()
    
    print("=" * 80)
    print("통합 인센티브 대시보드 생성 - 최종 버전")
    print(f"대상: {args.year}년 {args.month}월")
    print("=" * 80)
    
    # Google Drive 동기화 (옵션)
    if args.sync:
        if not sync_google_drive_data(args.month, args.year):
            print("Google Drive 동기화 실패. 로컬 파일 사용.")
    
    # 월 이름 변환
    month_names = ['', 'january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
    month_name = month_names[args.month]
    
    # 데이터 로드
    df = load_incentive_data(month_name, args.year)
    
    if df.empty:
        print("❌ 데이터 로드 실패")
        return
    
    # 대시보드 생성
    html_content = generate_dashboard_html(df, month_name, args.year, args.month)
    
    # 파일 저장
    # 파일명 형식 변경: Incentive_Dashboard_YYYY_MM_Version_5.html
    output_file = f'output_files/Incentive_Dashboard_{args.year}_{args.month:02d}_Version_5.html'
    os.makedirs('output_files', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 대시보드 생성 완료: {output_file}")
    
    # 통계 출력
    total_employees = len(df)
    # 동적 인센티브 컬럼 찾기
    incentive_col = f'{month_name}_incentive'
    if incentive_col not in df.columns:
        # 대체 컬럼명 시도
        print(f"⚠️ {incentive_col} 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼을 확인합니다.")
        # 가장 최근 월의 인센티브 컬럼을 찾음
        possible_cols = [col for col in df.columns if '_incentive' in col.lower() or '_Incentive' in col]
        if possible_cols:
            incentive_col = possible_cols[-1]  # 가장 마지막 인센티브 컬럼 사용
            print(f"   → {incentive_col} 컬럼을 사용합니다.")
    
    paid_employees = sum(1 for _, row in df.iterrows() if int(row.get(incentive_col, 0)) > 0)
    total_amount = sum(int(row.get(incentive_col, 0)) for _, row in df.iterrows())
    
    print(f"   - 전체 직원: {total_employees}명")
    print(f"   - 지급 대상: {paid_employees}명")
    print(f"   - 총 지급액: {total_amount:,} VND")

if __name__ == "__main__":
    main()