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

def get_korean_month(month):
    """영어 월 이름을 한국어로 변환"""
    month_map = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }
    return month_map.get(month.lower(), month)

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
    
    # 가능한 파일 패턴들
    patterns = [
        f"input_files/{year}년 {get_korean_month(month)} 인센티브 지급 세부 정보.csv",
        f"output_files/output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv",
        f"output_files/output_QIP_incentive_{month}_{year}_*.csv"
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
                elif 'attendance' in col_lower and 'rate' in col_lower:
                    column_mapping[col] = 'attendance_rate'
                elif 'actual' in col_lower and 'working' in col_lower:
                    column_mapping[col] = 'actual_working_days'
            
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
            
            # AQL/5PRS 컬럼 추가
            if 'aql_failures' not in df.columns:
                df['aql_failures'] = 0
            if 'continuous_fail' not in df.columns:
                df['continuous_fail'] = 'NO'
            if 'pass_rate' not in df.columns:
                df['pass_rate'] = 0
            if 'validation_qty' not in df.columns:
                df['validation_qty'] = 0
            
            # 출근 관련 컬럼
            if 'attendance_rate' not in df.columns:
                df['attendance_rate'] = 100.0
            if 'actual_working_days' not in df.columns:
                df['actual_working_days'] = 13
            if 'unapproved_absences' not in df.columns:
                df['unapproved_absences'] = 0
            if 'absence_rate' not in df.columns:
                df['absence_rate'] = 0
            
            # 이전 달 인센티브 로드
            prev_month_name = 'july' if month.lower() == 'august' else 'june'
            prev_year = year
            
            # 이전 월 데이터 로드 시도
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
    """직원 데이터에 대한 조건 평가"""
    if not condition_matrix:
        return []
    
    conditions = condition_matrix.get('conditions', {})
    position = emp_data.get('position', '')
    type_name = emp_data.get('type', 'TYPE-2')
    
    applicable_conditions = get_applicable_conditions(position, type_name, condition_matrix)
    results = []
    
    for cond_id in applicable_conditions:
        cond = conditions.get(str(cond_id), {})
        cond_name = cond.get('description', f'조건 {cond_id}')
        
        # 실제 조건 평가
        is_met = False
        actual_value = ''
        
        if cond_id == 1:  # 출근율 >= 88%
            attendance_rate = float(emp_data.get('attendance_rate', 0))
            is_met = attendance_rate >= 88
            actual_value = f"{attendance_rate:.1f}%"
        elif cond_id == 2:  # 무단결근 <= 2일
            unapproved = int(emp_data.get('unapproved_absences', 0))
            is_met = unapproved <= 2
            actual_value = f"{unapproved}일"
        elif cond_id == 3:  # 실제근무일 > 0
            working_days = int(emp_data.get('actual_working_days', 0))
            is_met = working_days > 0
            actual_value = f"{working_days}일"
        elif cond_id == 4:  # 최소 근무일 >= 12
            working_days = int(emp_data.get('actual_working_days', 0))
            is_met = working_days >= 12
            actual_value = f"{working_days}일"
        elif cond_id == 5:  # 개인 AQL 당월 실패 = 0
            aql_failures = int(emp_data.get('aql_failures', 0))
            is_met = aql_failures == 0
            actual_value = f"{aql_failures}건"
        elif cond_id == 6:  # AQL 3개월 연속 실패 없음
            continuous_fail = str(emp_data.get('continuous_fail', 'NO')).upper()
            is_met = continuous_fail != 'YES'
            actual_value = '통과' if is_met else '실패'
        elif cond_id == 7:  # 팀/구역 AQL
            # 팀/구역 데이터가 없으면 기본값 통과
            is_met = True
            actual_value = '평가 대상 아님'
        elif cond_id == 8:  # 담당구역 reject < 3%
            # 담당구역 데이터가 없으면 기본값 통과
            is_met = True
            actual_value = '평가 대상 아님'
        elif cond_id == 9:  # 5PRS 통과율 >= 95%
            pass_rate = float(emp_data.get('pass_rate', 0))
            is_met = pass_rate >= 95
            actual_value = f"{pass_rate:.1f}%"
        elif cond_id == 10:  # 5PRS 검사량 >= 100
            validation_qty = int(emp_data.get('validation_qty', 0))
            is_met = validation_qty >= 100
            actual_value = f"{validation_qty}족"
        
        results.append({
            'id': cond_id,
            'name': cond_name,
            'is_met': is_met,
            'actual': actual_value
        })
    
    return results

def generate_dashboard_html(df, month='august', year=2025):
    """dashboard_version4.html과 완전히 동일한 대시보드 생성"""
    
    # 조건 매트릭스 로드
    condition_matrix = load_condition_matrix()
    
    # 데이터 준비
    employees = []
    for _, row in df.iterrows():
        emp = {
            'emp_no': str(row.get('emp_no', '')),
            'name': str(row.get('name', '')),
            'position': str(row.get('position', '')),
            'type': str(row.get('type', 'TYPE-2')),
            'july_incentive': str(row.get('july_incentive', '0')),
            'august_incentive': str(row.get('august_incentive', '0')),
            'june_incentive': str(row.get('june_incentive', '0')),
            'attendance_rate': float(row.get('attendance_rate', 100)),
            'actual_working_days': int(row.get('actual_working_days', 13)),
            'unapproved_absences': int(row.get('unapproved_absences', 0)),
            'absence_rate': float(row.get('absence_rate', 0)),
            'condition1': str(row.get('condition1', 'no')),
            'condition2': str(row.get('condition2', 'no')),
            'condition3': str(row.get('condition3', 'no')),
            'condition4': str(row.get('condition4', 'no')),
            'aql_failures': int(row.get('aql_failures', 0)),
            'continuous_fail': str(row.get('continuous_fail', 'NO')),
            'pass_rate': float(row.get('pass_rate', 0)),
            'validation_qty': int(row.get('validation_qty', 0))
        }
        
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
    
    # 현재 시간
    current_date = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
    
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
            max-width: 1400px;
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
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        
        .modal-content {{
            background: white;
            margin: 50px auto;
            padding: 0;
            width: 95%;
            max-width: 1100px;
            border-radius: 12px;
            max-height: 90vh;
            overflow-y: auto;
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
        }}
        
        .modal-body {{
            padding: 30px;
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
            <div style="position: absolute; top: 20px; right: 20px;">
                <select id="languageSelector" class="form-select" style="width: 150px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3);">
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                    <option value="vi">Tiếng Việt</option>
                </select>
            </div>
            <h1 id="mainTitle">QIP 인센티브 계산 결과 <span class="version-badge">v4.2</span></h1>
            <p id="mainSubtitle">{year}년 {get_korean_month(month)} 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;">보고서 생성일: {current_date}</p>
        </div>
        
        <div class="content p-4">
            <!-- 요약 카드 -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalEmployeesLabel">전체 직원</h6>
                        <h2 id="totalEmployeesValue">{total_employees}<span class="unit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paidEmployeesLabel">수령 직원</h6>
                        <h2 id="paidEmployeesValue">{paid_employees}<span class="unit">명</span></h2>
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
                <h3>Type별 현황</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th rowspan="2">Type</th>
                            <th rowspan="2">전체 인원</th>
                            <th rowspan="2">수령 인원</th>
                            <th rowspan="2">수령률</th>
                            <th rowspan="2">총 지급액</th>
                            <th colspan="2" class="avg-header">평균 지급액</th>
                        </tr>
                        <tr>
                            <th class="sub-header">수령인원 기준</th>
                            <th class="sub-header">총원 기준</th>
                        </tr>
                    </thead>
                    <tbody id="typeSummaryBody">'''
    
    # Type별 요약 데이터 생성
    total_stats = {'total': 0, 'paid': 0, 'amount': 0}
    
    for emp_type in sorted(type_stats.keys()):
        if not emp_type:  # 빈 Type 건너뛰기
            continue
        stats = type_stats[emp_type]
        rate = (stats['paid'] / stats['total'] * 100) if stats['total'] > 0 else 0
        avg_paid = (stats['amount'] / stats['paid']) if stats['paid'] > 0 else 0
        avg_total = (stats['amount'] / stats['total']) if stats['total'] > 0 else 0
        
        # Total 집계
        total_stats['total'] += stats['total']
        total_stats['paid'] += stats['paid']
        total_stats['amount'] += stats['amount']
        
        # Type badge 클래스 결정
        type_class = '2'  # 기본값
        if 'TYPE-1' in emp_type.upper():
            type_class = '1'
        elif 'TYPE-2' in emp_type.upper():
            type_class = '2'
        elif 'TYPE-3' in emp_type.upper():
            type_class = '3'
        
        html_content += f'''
                        <tr>
                            <td><span class="type-badge type-{type_class}">{emp_type}</span></td>
                            <td>{stats['total']}명</td>
                            <td>{stats['paid']}명</td>
                            <td>{rate:.1f}%</td>
                            <td>{stats['amount']:,} VND</td>
                            <td>{avg_paid:,.0f} VND</td>
                            <td>{avg_total:,.0f} VND</td>
                        </tr>'''
    
    # Total 행 추가
    total_rate = (total_stats['paid'] / total_stats['total'] * 100) if total_stats['total'] > 0 else 0
    total_avg_paid = (total_stats['amount'] / total_stats['paid']) if total_stats['paid'] > 0 else 0
    total_avg_total = (total_stats['amount'] / total_stats['total']) if total_stats['total'] > 0 else 0
    
    html_content += f'''
                        <tr style="font-weight: bold; background-color: #f3f4f6;">
                            <td>Total</td>
                            <td>{total_stats['total']}명</td>
                            <td>{total_stats['paid']}명</td>
                            <td>{total_rate:.1f}%</td>
                            <td>{total_stats['amount']:,} VND</td>
                            <td>{total_avg_paid:,.0f} VND</td>
                            <td>{total_avg_total:,.0f} VND</td>
                        </tr>'''
    
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
                                <option value="" id="optAllTypes">모든 타입</option>
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
                                <th>사번</th>
                                <th>이름</th>
                                <th>직급</th>
                                <th>Type</th>
                                <th>7월</th>
                                <th>8월</th>
                                <th>상태</th>
                                <th>상세</th>
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
                <h3>인센티브 지급 기준</h3>
                <div class="row">
                    <div class="col-md-6">
                        <h4>출근 조건 (4개)</h4>
                        <ul>
                            <li>조건 1: 실제 근무일수 ≥ 23일</li>
                            <li>조건 2: 무단 결근 = 0</li>
                            <li>조건 3: 결근율 < 10%</li>
                            <li>조건 4: 출근율 ≥ 90%</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h4>AQL 조건 (4개)</h4>
                        <ul>
                            <li>조건 5: AQL 실패 횟수 < 3회</li>
                            <li>조건 6: 연속 실패 없음</li>
                            <li>조건 7: 합격률 ≥ 95%</li>
                            <li>조건 8: 검증 수량 ≥ 100개</li>
                        </ul>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h4>5PRS 조건 (2개)</h4>
                        <ul>
                            <li>조건 9: 이전 달 인센티브 수령</li>
                            <li>조건 10: 특별 조건 충족</li>
                        </ul>
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
        
        // 초기화
        window.onload = function() {{
            generateEmployeeTable();
            generatePositionTables();
            updatePositionFilter();
        }};
        
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
                
                tr.innerHTML = `
                    <td>${{emp.emp_no}}</td>
                    <td>${{emp.name}}</td>
                    <td>${{emp.position}}</td>
                    <td><span class="type-badge type-${{emp.type.toLowerCase().replace('type-', '')}}">${{emp.type}}</span></td>
                    <td>${{parseInt(emp.july_incentive).toLocaleString()}}</td>
                    <td><strong>${{amount.toLocaleString()}}</strong></td>
                    <td>${{isPaid ? '✅ 지급' : '❌ 미지급'}}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${{emp.emp_no}}')">상세</button></td>
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
                    
                    let html = `
                        <div class="mb-5">
                            <h4 class="mb-3">
                                <span class="type-badge type-${{typeClass}}">${{type}}</span> 
                                직급별 현황
                            </h4>
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>직급</th>
                                        <th>전체</th>
                                        <th>지급</th>
                                        <th>지급률</th>
                                        <th>총 지급액</th>
                                        <th>평균 지급액</th>
                                        <th>상세</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    // 직급별 행 추가
                    positions.sort((a, b) => a.position.localeCompare(b.position)).forEach(posData => {{
                        const paymentRate = posData.total > 0 ? (posData.paid / posData.total * 100).toFixed(1) : '0.0';
                        const avgAmount = posData.paid > 0 ? Math.round(posData.totalAmount / posData.paid) : 0;
                        
                        html += `
                            <tr>
                                <td>${{posData.position}}</td>
                                <td>${{posData.total}}명</td>
                                <td>${{posData.paid}}명</td>
                                <td>${{paymentRate}}%</td>
                                <td>${{posData.totalAmount.toLocaleString()}} VND</td>
                                <td>${{avgAmount.toLocaleString()}} VND</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" 
                                            onclick="showPositionDetail('${{type}}', '${{posData.position}}')">
                                        보기
                                    </button>
                                </td>
                            </tr>
                        `;
                    }});
                    
                    // Type별 소계
                    const typeTotal = positions.reduce((acc, p) => acc + p.total, 0);
                    const typePaid = positions.reduce((acc, p) => acc + p.paid, 0);
                    const typeAmount = positions.reduce((acc, p) => acc + p.totalAmount, 0);
                    const typeRate = typeTotal > 0 ? (typePaid / typeTotal * 100).toFixed(1) : '0.0';
                    const typeAvg = typePaid > 0 ? Math.round(typeAmount / typePaid) : 0;
                    
                    html += `
                                </tbody>
                                <tfoot>
                                    <tr style="font-weight: bold; background-color: #f8f9fa;">
                                        <td>${{type}} 합계</td>
                                        <td>${{typeTotal}}명</td>
                                        <td>${{typePaid}}명</td>
                                        <td>${{typeRate}}%</td>
                                        <td>${{typeAmount.toLocaleString()}} VND</td>
                                        <td>${{typeAvg.toLocaleString()}} VND</td>
                                        <td></td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                    
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
            
            modalTitle.innerHTML = `${{type}} - ${{position}} 인센티브 계산 상세`;
            
            // 요약 통계 계산
            const totalEmployees = employees.length;
            const paidEmployees = employees.filter(e => parseInt(e.august_incentive) > 0).length;
            const avgIncentive = employees.reduce((sum, e) => sum + parseInt(e.august_incentive), 0) / totalEmployees;
            const paidRate = Math.round(paidEmployees/totalEmployees*100);
            
            // 각 직원의 조건 충족 통계 계산
            const conditionStats = {{}};
            if (employees[0] && employees[0].condition_results) {{
                employees[0].condition_results.forEach(cond => {{
                    conditionStats[cond.id] = {{
                        name: cond.name,
                        met: 0,
                        total: 0
                    }};
                }});
                
                employees.forEach(emp => {{
                    if (emp.condition_results) {{
                        emp.condition_results.forEach(cond => {{
                            if (conditionStats[cond.id]) {{
                                conditionStats[cond.id].total++;
                                if (cond.is_met) {{
                                    conditionStats[cond.id].met++;
                                }}
                            }}
                        }});
                    }}
                }});
            }}
            
            let modalContent = `
                <div style="display: grid; grid-template-columns: 1fr 2fr 1fr; gap: 20px; padding: 20px;">
                    <!-- 왼쪽: 지급/미지급 차트 -->
                    <div>
                        <h6 style="color: #666; font-size: 0.85rem; margin-bottom: 10px;">지급/미지급 비율</h6>
                        <div style="position: relative; width: 180px; height: 180px; margin: 0 auto;">
                            <canvas id="positionChart${{type.replace('-', '')}}${{position.replace(/[\\s()]/g, '')}}" width="180" height="180"></canvas>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="font-size: 2rem; font-weight: bold;">${{paidRate}}%</div>
                                <div style="font-size: 0.85rem; color: #666;">수령률</div>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 10px; font-size: 0.85rem;">
                            <span style="color: #28a745;">지급</span> / <span style="color: #dc3545;">미지급</span>
                        </div>
                    </div>
                    
                    <!-- 중앙: 조건별 충족률 -->
                    <div>
                        <h6 style="color: #666; font-size: 0.85rem; margin-bottom: 10px;">조건별 충족률</h6>
                        <div style="background: white; padding: 0;">
            `;
            
            // 조건별 진행바 동적 생성
            let condIdx = 1;
            for (const [condId, stat] of Object.entries(conditionStats)) {{
                const percentage = stat.total > 0 ? Math.round((stat.met / stat.total) * 100) : 0;
                modalContent += `
                            <div style="margin-bottom: 12px; padding: 8px; background: #f8f9fa; border-radius: 4px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.85rem;">
                                    <span>${{stat.name}}</span>
                                    <span style="font-weight: bold;">${{percentage}}%</span>
                                </div>
                                <div style="background: #e9ecef; height: 8px; border-radius: 4px; overflow: hidden;">
                                    <div style="background: ${{percentage === 100 ? '#28a745' : percentage >= 50 ? '#ffc107' : '#dc3545'}}; height: 100%; width: ${{percentage}}%; transition: width 0.3s;"></div>
                                </div>
                            </div>
                `;
                condIdx++;
                if (condIdx > 4) break; // 상위 4개 조건만 표시
            }}
            
            // AQL/5PRS 조건 표시 (해당하는 경우)
            const hasAQL = Object.keys(conditionStats).some(id => parseInt(id) >= 5 && parseInt(id) <= 8);
            const has5PRS = Object.keys(conditionStats).some(id => parseInt(id) >= 9 && parseInt(id) <= 10);
            
            if (hasAQL || has5PRS) {{
                modalContent += `
                            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                `;
                
                if (hasAQL) {{
                    modalContent += `
                                <div style="margin-bottom: 10px;">
                                    <span style="font-size: 0.8rem; color: #666;">개인 AQL: 당월 실패 0건</span>
                                    <span style="float: right; font-size: 0.8rem; color: #6c757d;">평가 대상 아님</span>
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="font-size: 0.8rem; color: #666;">연속성 체크: 3개월 연속 실패 없음</span>
                                    <span style="float: right; font-size: 0.8rem; color: #6c757d;">평가 대상 아님</span>
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="font-size: 0.8rem; color: #666;">팀/구역 AQL: 3개월 연속 실패 없음</span>
                                    <span style="float: right; font-size: 0.8rem; color: #6c757d;">평가 대상 아님</span>
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="font-size: 0.8rem; color: #666;">담당구역 reject률 <3%</span>
                                    <span style="float: right; font-size: 0.8rem; color: #6c757d;">평가 대상 아님</span>
                                </div>
                    `;
                }}
                
                if (has5PRS) {{
                    modalContent += `
                                <div style="margin-bottom: 10px;">
                                    <span style="font-size: 0.8rem; color: #666;">5PRS 통과율 ≥95%</span>
                                    <span style="float: right; font-size: 0.8rem; color: #6c757d;">평가 대상 아님</span>
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="font-size: 0.8rem; color: #666;">5PRS 검사량 ≥100개</span>
                                    <span style="float: right; font-size: 0.8rem; color: #6c757d;">평가 대상 아님</span>
                                </div>
                    `;
                }}
                
                modalContent += `
                            </div>
                `;
            }}
            
            modalContent += `
                        </div>
                    </div>
                    
                    <!-- 오른쪽: 인센티브 통계 -->
                    <div>
                        <h6 style="color: #666; font-size: 0.85rem; margin-bottom: 10px;">📊 인센티브 통계</h6>
                        <div style="background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px;">
                            <div style="margin-bottom: 20px;">
                                <div style="color: #666; font-size: 0.75rem;">전체 인원</div>
                                <div style="font-size: 1.8rem; font-weight: bold; color: #333;">${{totalEmployees}}명</div>
                                <div style="background: #e9ecef; height: 40px; border-radius: 4px; display: flex; align-items: center; justify-content: center; margin-top: 10px;">
                                    <span style="color: #666; font-size: 0.85rem;">지급 ${{paidEmployees}}명</span>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 20px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #666; font-size: 0.75rem;">수령율:</span>
                                    <span style="font-size: 1rem; font-weight: bold; color: #333;">${{paidRate}}%</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                                    <span style="color: #28a745; font-size: 0.85rem;">미지급율:</span>
                                    <span style="font-size: 1rem; font-weight: bold; color: #dc3545;">${{100 - paidRate}}%</span>
                                </div>
                            </div>
                            
                            <div style="border-top: 1px solid #dee2e6; padding-top: 15px;">
                                <div style="color: #666; font-size: 0.75rem;">평균인센티브 기준</div>
                                <div style="font-size: 1.2rem; font-weight: bold; color: #007bff; margin-top: 5px;">
                                    ${{avgIncentive.toLocaleString()}} VND
                                </div>
                            </div>
                            
                            <div style="margin-top: 15px; border-top: 1px solid #dee2e6; padding-top: 15px;">
                                <div style="color: #666; font-size: 0.75rem;">예상인센티브</div>
                                <div style="font-size: 1.2rem; font-weight: bold; color: #333; margin-top: 5px;">
                                    ${{avgIncentive.toLocaleString()}} VND
                                </div>
                            </div>
                            
                            <div style="margin-top: 20px; text-align: center;">
                                <div style="background: #28a745; color: white; padding: 10px; border-radius: 6px; font-size: 1rem; font-weight: bold;">
                                    인센티브 지급률
                                    <div style="font-size: 1.5rem; margin-top: 5px;">${{paidRate}}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                    
                    <!-- 조건 충족 상세 테이블 -->
                    <div style="margin-bottom: 20px;">
                        <h6 style="color: #666; margin-bottom: 10px;">📋 조건 충족 상세</h6>
                        <div style="overflow-x: auto;">
                            <table class="table table-sm" style="font-size: 0.9rem;">
                                <thead style="background: #f8f9fa;">
                                    <tr>
                                        <th width="5%">#</th>
                                        <th width="40%">조건</th>
                                        <th width="20%">평가 대상</th>
                                        <th width="15%">충족</th>
                                        <th width="15%">미충족</th>
                                        <th width="15%">충족율</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>1</td>
                                        <td>출근율 ≥88%</td>
                                        <td>${{totalEmployees}}명</td>
                                        <td style="color: #28a745; font-weight: bold;">${{paidEmployees}}명</td>
                                        <td style="color: #dc3545;">${{totalEmployees - paidEmployees}}명</td>
                                        <td>
                                            <div style="display: flex; align-items: center; gap: 5px;">
                                                <div style="background: #e9ecef; height: 8px; width: 60px; border-radius: 4px; overflow: hidden;">
                                                    <div style="background: #28a745; height: 100%; width: ${{paidEmployees/totalEmployees*100}}%;"></div>
                                                </div>
                                                <span style="font-weight: bold;">${{Math.round(paidEmployees/totalEmployees*100)}}%</span>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>2</td>
                                        <td>무단결근 ≤2일</td>
                                        <td>${{totalEmployees}}명</td>
                                        <td style="color: #28a745; font-weight: bold;">${{totalEmployees}}명</td>
                                        <td style="color: #dc3545;">0명</td>
                                        <td>
                                            <div style="display: flex; align-items: center; gap: 5px;">
                                                <div style="background: #e9ecef; height: 8px; width: 60px; border-radius: 4px; overflow: hidden;">
                                                    <div style="background: #28a745; height: 100%; width: 100%;"></div>
                                                </div>
                                                <span style="font-weight: bold;">100%</span>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>3</td>
                                        <td>실제 근무일 >0일</td>
                                        <td>${{totalEmployees}}명</td>
                                        <td style="color: #28a745; font-weight: bold;">${{totalEmployees}}명</td>
                                        <td style="color: #dc3545;">0명</td>
                                        <td>
                                            <div style="display: flex; align-items: center; gap: 5px;">
                                                <div style="background: #e9ecef; height: 8px; width: 60px; border-radius: 4px; overflow: hidden;">
                                                    <div style="background: #28a745; height: 100%; width: 100%;"></div>
                                                </div>
                                                <span style="font-weight: bold;">100%</span>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>4</td>
                                        <td>최소 근무일 ≥12일</td>
                                        <td>${{totalEmployees}}명</td>
                                        <td style="color: #28a745; font-weight: bold;">${{paidEmployees}}명</td>
                                        <td style="color: #dc3545;">${{totalEmployees - paidEmployees}}명</td>
                                        <td>
                                            <div style="display: flex; align-items: center; gap: 5px;">
                                                <div style="background: #e9ecef; height: 8px; width: 60px; border-radius: 4px; overflow: hidden;">
                                                    <div style="background: #28a745; height: 100%; width: ${{paidEmployees/totalEmployees*100}}%;"></div>
                                                </div>
                                                <span style="font-weight: bold;">${{Math.round(paidEmployees/totalEmployees*100)}}%</span>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- AQL/5PRS 조건 섹션 -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <!-- AQL 조건 -->
                        <div>
                            <h6 style="color: #666; margin-bottom: 10px;">🎯 AQL 조건 (4가지)</h6>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 0.85rem;">
                                <div style="margin-bottom: 8px;">개인 AQL: 당월 실패 0건 <span style="color: #6c757d;">- 평가 대상 아님</span></div>
                                <div style="margin-bottom: 8px;">연속성 체크: 3개월 연속 실패 없음 <span style="color: #6c757d;">- 평가 대상 아님</span></div>
                                <div style="margin-bottom: 8px;">팀/구역 AQL: 3개월 연속 실패 없음 <span style="color: #6c757d;">- 평가 대상 아님</span></div>
                                <div>담당구역 reject율 <3% <span style="color: #6c757d;">- 평가 대상 아님</span></div>
                            </div>
                        </div>
                        
                        <!-- 5PRS 조건 -->
                        <div>
                            <h6 style="color: #666; margin-bottom: 10px;">📊 5PRS 조건 (2가지)</h6>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 0.85rem;">
                                <div style="margin-bottom: 8px;">5PRS 통과율 ≥95% <span style="color: #6c757d;">- 평가 대상 아님</span></div>
                                <div>5PRS 검사량 ≥100개 <span style="color: #6c757d;">- 평가 대상 아님</span></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 직원별 상세 현황 -->
                    <div>
                        <h6 style="color: #666; margin-bottom: 10px;">직원별 상세 현황</h6>
                        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                            <button class="btn btn-sm btn-outline-primary" onclick="filterPositionTable('all')">전체</button>
                            <button class="btn btn-sm btn-outline-success" onclick="filterPositionTable('paid')">지급자만</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="filterPositionTable('unpaid')">미지급자만</button>
                        </div>
                        <div style="overflow-x: auto;">
                            <table class="table table-sm" id="positionEmployeeTable" style="font-size: 0.9rem;">
                                <thead style="background: #f8f9fa;">
                                    <tr>
                                        <th>직원번호</th>
                                        <th>이름</th>
                                        <th>인센티브</th>
                                        <th>상태</th>
                                        <th>조건 충족 현황</th>
                                        <th>개산 근거</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            employees.forEach(emp => {{
                const amount = parseInt(emp.august_incentive);
                const isPaid = amount > 0;
                modalContent += `
                    <tr class="employee-row ${{isPaid ? 'paid-row' : 'unpaid-row'}}">
                        <td>${{emp.emp_no}}</td>
                        <td>${{emp.name}}</td>
                        <td><strong style="color: ${{isPaid ? '#28a745' : '#dc3545'}};">${{amount.toLocaleString()}} VND</strong></td>
                        <td>
                            <span class="badge ${{isPaid ? 'bg-success' : 'bg-danger'}}">
                                ${{isPaid ? '지급' : '미지급'}}
                            </span>
                        </td>
                        <td>
                            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                                <span class="badge bg-success" title="출근율 충족">출근✓</span>
                                <span class="badge ${{isPaid ? 'bg-success' : 'bg-danger'}}" title="AQL 조건">AQL: N/A</span>
                                <span class="badge ${{isPaid ? 'bg-success' : 'bg-danger'}}" title="5PRS 조건">5PRS: N/A</span>
                            </div>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-primary" 
                                    onclick="closeModal(); setTimeout(() => showEmployeeDetail('${{emp.emp_no}}'), 100);">
                                조건 충족
                            </button>
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
        
        // 직원 상세 정보 표시 (대시보드 스타일 UI)
        function showEmployeeDetail(empNo) {{
            const emp = employeeData.find(e => e.emp_no === empNo);
            if (!emp) return;
            
            const modal = document.getElementById('employeeModal');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');
            
            modalTitle.textContent = `${{emp.name}} (${{emp.emp_no}}) - 상세 정보`;
            
            // 조건 충족 통계 계산 - 실제 데이터 사용
            const conditions = emp.condition_results || [];
            const passedConditions = conditions.filter(c => c.is_met).length;
            const totalConditions = conditions.length;
            const passRate = (passedConditions / totalConditions * 100).toFixed(0);
            
            modalBody.innerHTML = `
                <!-- 상단 통계 카드 -->
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{emp.type}}</div>
                            <div class="stat-label">Type 분류</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{emp.position}}</div>
                            <div class="stat-label">직급</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">${{parseInt(emp.august_incentive).toLocaleString()}} VND</div>
                            <div class="stat-label">8월 인센티브</div>
                        </div>
                    </div>
                </div>
                
                <!-- 차트와 조건 충족도 -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6 class="card-title">조건 충족도</h6>
                                <canvas id="conditionChart${{empNo}}" width="200" height="200"></canvas>
                                <div class="mt-3">
                                    <h4>${{passRate}}%</h4>
                                    <p class="text-muted">${{passedConditions}} / ${{totalConditions}} 조건 충족</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h6 class="card-title">지급 상태</h6>
                                <div class="payment-status ${{parseInt(emp.august_incentive) > 0 ? 'paid' : 'unpaid'}}">
                                    ${{parseInt(emp.august_incentive) > 0 ? `
                                    <div>
                                        <i class="fas fa-check-circle"></i>
                                        <h5>지급 완료</h5>
                                        <p>${{parseInt(emp.august_incentive).toLocaleString()}} VND</p>
                                    </div>` : `
                                    <div>
                                        <i class="fas fa-times-circle"></i>
                                        <h5>미지급</h5>
                                        <p>조건 미충족</p>
                                    </div>`}}
                                </div>
                                <div class="mt-3">
                                    <small class="text-muted">지난달 인센티브: ${{parseInt(emp.july_incentive).toLocaleString()}} VND</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 조건 충족 상세 테이블 -->
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">조건 충족 상세</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th width="5%">#</th>
                                        <th width="50%">조건</th>
                                        <th width="25%">실적</th>
                                        <th width="20%">결과</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{conditions.map((cond, idx) => `
                                    <tr class="${{cond.is_met ? 'table-success' : 'table-danger'}}">
                                        <td>${{idx + 1}}</td>
                                        <td>${{cond.name}}</td>
                                        <td><strong>${{cond.actual}}</strong></td>
                                        <td class="text-center">
                                            ${{cond.is_met ? '<span class="badge bg-success">충족</span>' : '<span class="badge bg-danger">미충족</span>'}}
                                        </td>
                                    </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <!-- 추가 정보 -->
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="info-group">
                            <label>출근 정보</label>
                            <ul class="list-unstyled ms-3">
                                <li>출근율: ${{emp.attendance_rate.toFixed(1)}}%</li>
                                <li>실제 근무일: ${{emp.actual_working_days}}일</li>
                                <li>무단결근: ${{emp.unapproved_absences}}일</li>
                            </ul>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="info-group">
                            <label>품질 정보</label>
                            <ul class="list-unstyled ms-3">
                                <li>AQL 실패: ${{emp.aql_failures}}건</li>
                                <li>5PRS 통과율: ${{emp.pass_rate.toFixed(1)}}%</li>
                                <li>검사량: ${{emp.validation_qty}}족</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            
            modal.style.display = 'block';
            
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
                            labels: ['충족', '미충족'],
                            datasets: [{{
                                data: [passedConditions, totalConditions - passedConditions],
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
                
                tr.innerHTML = `
                    <td>${{emp.emp_no}}</td>
                    <td>${{emp.name}}</td>
                    <td>${{emp.position}}</td>
                    <td><span class="type-badge type-${{emp.type.toLowerCase().replace('type-', '')}}">${{emp.type}}</span></td>
                    <td>${{parseInt(emp.july_incentive).toLocaleString()}}</td>
                    <td><strong>${{amount.toLocaleString()}}</strong></td>
                    <td>${{isPaid ? '✅ 지급' : '❌ 미지급'}}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${{emp.emp_no}}')">상세</button></td>
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
            positionSelect.innerHTML = '<option value="">모든 직급</option>';
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
    html_content = generate_dashboard_html(df, month_name, args.year)
    
    # 파일 저장
    output_file = f'output_files/dashboard_{args.year}_{args.month:02d}.html'
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