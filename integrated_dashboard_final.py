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
                        # August_Incentive 컬럼 찾기
                        for orig_col in df.columns:
                            if 'august' in orig_col.lower() and 'incentive' in orig_col.lower():
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
            prev_month_name = 'july' if month.lower() == 'august' else 'june'
            prev_year = year
            
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
                for col in prev_df.columns:
                    if f'{prev_month_name.lower()}_incentive' in col.lower() or f'{prev_month_name.lower()} incentive' in col.lower():
                        prev_df.rename(columns={col: f'{prev_month_name}_incentive'}, inplace=True)
                        break
                
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
            
            # 퇴사일 필터링 (8월 1일 이전 퇴사자 제외)
            if 'Stop working Date' in df.columns:
                print(f"✅ 퇴사일 데이터 확인 중...")
                df['resignation_date'] = pd.to_datetime(df['Stop working Date'], format='%Y.%m.%d', errors='coerce')
                august_start = pd.to_datetime(f'{year}-08-01')
                
                # 8월 이전 퇴사자 제외
                before_august = df[df['resignation_date'] < august_start]
                df = df[(df['resignation_date'] >= august_start) | (df['resignation_date'].isna())]
                
                if len(before_august) > 0:
                    print(f"   - 8월 이전 퇴사자 {len(before_august)}명 제외")
                print(f"   - 8월 인센티브 대상자: {len(df)}명")
            
            print(f"✅ {len(df)}명의 직원 데이터 로드 (8월 대상자만)")
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
    
    # 데이터 준비
    employees = []
    for _, row in df.iterrows():
        # Convert Series to dict
        row_dict = row.to_dict()

        emp = {
            'emp_no': str(row_dict.get('emp_no', '')),
            'name': str(row_dict.get('name', '')),
            'position': str(row_dict.get('position', '')),
            'type': str(row_dict.get('type', 'TYPE-2')),
            'july_incentive': str(row_dict.get('july_incentive', '0')),
            'august_incentive': str(row_dict.get('august_incentive', '0')),
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
        
        employees.append(emp)
    
    # 통계 계산
    total_employees = len(employees)
    paid_employees = sum(1 for e in employees if int(e['august_incentive']) > 0)
    total_amount = sum(int(e['august_incentive']) for e in employees)
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
        amount = int(emp['august_incentive'])
        if amount > 0:
            type_stats[emp_type]['paid'] += 1
            type_stats[emp_type]['amount'] += amount
            type_stats[emp_type]['paid_amounts'].append(amount)
    
    # 직원 데이터 JSON
    employees_json = json.dumps(employees, ensure_ascii=False)
    
    # 현재 시간 - ISO 형식으로 저장
    current_datetime = datetime.now()
    current_date_iso = current_datetime.strftime('%Y-%m-%d %H:%M')
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day
    current_hour = current_datetime.hour
    current_minute = current_datetime.minute

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
        if att_min and att_max:
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
        if prs_min and prs_max:
            prs_start_day = prs_min.day
            prs_end_day = prs_max.day
            prs_start_str = prs_min.strftime('%d')
            prs_end_str = prs_max.strftime('%d')
        else:
            prs_start_day = 1
            prs_end_day = month_last_day
            prs_start_str = '01'
            prs_end_str = f'{month_last_day:02d}'

        # AQL 데이터 범위 (보통 월 전체)
        aql_start_str = '01'
        aql_end_str = f'{month_last_day:02d}'

        # 인센티브 데이터 범위 (항상 월 전체)
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                                <th id="julyHeader">7월</th>
                                <th id="augustHeader">8월</th>
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
                                    <th width="40%" class="calc-header-example">실제 계산 예시 (2025년 8월)</th>
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
                                    <th width="25%">2025년 8월 평균</th>
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
                                <span id="faqMemberNote">* 8월 기준 모든 AUDIT & TRAINING TEAM 멤버가 reject율 조건 미충족으로 인센티브 0원</span>
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
        let currentLanguage = 'ko';
        
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
                memberNote.textContent = translations.incentiveCalculation?.faq?.memberNote?.[lang] || '* 8월 기준 모든 AUDIT & TRAINING TEAM 멤버가 reject율 조건 미충족으로 인센티브 0원';
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
                    const lastDay = element.getAttribute('data-lastday');
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
                            periodText = `• ${{dataLabel}}: ${{year}}년 ${{month}}월 01일 ~ ${{lastDay}}일`;
                        }} else if (currentLanguage === 'en') {{
                            const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                            periodText = `• ${{dataLabel}}: ${{monthNames[parseInt(month)-1]}} 01 - ${{lastDay}}, ${{year}}`;
                        }} else {{
                            periodText = `• ${{dataLabel}}: 01/${{month}} - ${{lastDay}}/${{month}}/${{year}}`;
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
                'tabCriteria': 'tabs.criteria'
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
                'julyHeader': 'common.july',
                'augustHeader': 'common.august',
                'statusHeader': 'individual.table.columns.status',
                'detailsHeader': 'individual.table.columns.details'
            }};
            
            for (const [id, key] of Object.entries(individualHeaders)) {{
                const elem = document.getElementById(id);
                if (elem) elem.textContent = getTranslation(key, currentLanguage);
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

                    const amount = parseInt(emp.august_incentive) || 0;
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
        }}
        
        // 직원 테이블 생성
        function generateEmployeeTable() {{
            const tbody = document.getElementById('employeeTableBody');
            tbody.innerHTML = '';
            
            employeeData.forEach(emp => {{
                const amount = parseInt(emp.august_incentive);
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
                const amount = parseInt(emp.august_incentive) || 0;
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
            const paidEmployees = employees.filter(e => parseInt(e.august_incentive) > 0).length;
            const avgIncentive = Math.round(employees.reduce((sum, e) => sum + parseInt(e.august_incentive), 0) / totalEmployees);
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
            const actualPassCount = employees.filter(emp => parseInt(emp.august_incentive) > 0).length;
            const actualFailCount = employees.filter(emp => parseInt(emp.august_incentive) === 0).length;

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
            const incentiveAmounts = employees.map(emp => parseInt(emp.august_incentive)).filter(amt => amt > 0);
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
                const amount = parseInt(emp.august_incentive);
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
                            <div class="stat-value">${{parseInt(emp.august_incentive).toLocaleString()}} VND</div>
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
                                <div class="payment-status ${{parseInt(emp.august_incentive) > 0 ? 'paid' : 'unpaid'}}">
                                    ${{parseInt(emp.august_incentive) > 0 ? `
                                    <div>
                                        <i class="fas fa-check-circle"></i>
                                        <h5>` + getTranslation('modal.payment.paid', currentLanguage) + `</h5>
                                        <p class="mb-1">${{parseInt(emp.august_incentive).toLocaleString()}} VND</p>
                                        ${{emp.Talent_Pool_Member === 'Y' ? `
                                        <div style="background: linear-gradient(135deg, #FFD700, #FFA500); padding: 8px; border-radius: 8px; margin-top: 10px;">
                                            <small style="color: white; font-weight: bold;">
                                                🌟 Talent Pool 보너스 포함<br>
                                                기본: ${{(parseInt(emp.august_incentive) - parseInt(emp.Talent_Pool_Bonus || 0)).toLocaleString()}} VND<br>
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
                const amount = parseInt(emp.august_incentive);
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
        # august_incentive 컬럼명 사용 (하드코딩된 경우)
        incentive_col = 'august_incentive'
    
    paid_employees = sum(1 for _, row in df.iterrows() if int(row.get(incentive_col, 0)) > 0)
    total_amount = sum(int(row.get(incentive_col, 0)) for _, row in df.iterrows())
    
    print(f"   - 전체 직원: {total_employees}명")
    print(f"   - 지급 대상: {paid_employees}명")
    print(f"   - 총 지급액: {total_amount:,} VND")

if __name__ == "__main__":
    main()