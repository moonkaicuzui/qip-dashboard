import re
from datetime import datetime
import json
import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def load_incentive_csv_data(csv_path):
    """인센티브 CSV 파일에서 상세 데이터 로드"""
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # 컬럼명 정리
        df.columns = df.columns.str.strip()
        
        # Employee No를 문자열로 변환
        df['Employee No'] = df['Employee No'].astype(str).str.strip()
        
        return df
    except Exception as e:
        print(f"Warning: Could not load CSV data: {e}")
        return None

def load_aql_history(month='july'):
    """AQL history 파일에서 3개월 실패 데이터 로드"""
    try:
        aql_history = {}
        base_path = Path(__file__).parent.parent / "input_files" / "AQL history"
        
        # 월 이름 매핑
        month_mapping = {
            'july': ['JULY', 'JUNE', 'MAY'],
            'june': ['JUNE', 'MAY', 'APRIL'],
            'may': ['MAY', 'APRIL', 'MARCH']
        }
        
        months = month_mapping.get(month.lower(), ['JULY', 'JUNE', 'MAY'])
        
        for month_name in months:
            file_path = base_path / f"1.HSRG AQL REPORT-{month_name}.2025.csv"
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    # AQL 실패 데이터 처리
                    for _, row in df.iterrows():
                        emp_no = str(row.get('Employee No', '')).strip()
                        if emp_no:
                            if emp_no not in aql_history:
                                aql_history[emp_no] = {}
                            # Fail 여부 확인 (컬럼명에 따라 조정 필요)
                            fail_count = 0
                            for col in df.columns:
                                if 'FAIL' in str(row[col]).upper():
                                    fail_count += 1
                            aql_history[emp_no][month_name] = fail_count
                except Exception as e:
                    print(f"Warning: Could not load AQL history for {month_name}: {e}")
        
        return aql_history
    except Exception as e:
        print(f"Warning: Could not load AQL history: {e}")
        return {}

def extract_data_from_html(html_file_path, month='july', year=2025):
    """기존 HTML 파일에서 데이터 추출 - Version 4 개선"""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 월 이름 매핑 (한국어)
    month_kr_map = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }
    month_kr = month_kr_map.get(month.lower(), '7월')
    
    # CSV 데이터 로드 - 동적 경로
    csv_path = Path(__file__).parent.parent / "input_files" / f"{year}년 {month_kr} 인센티브 지급 세부 정보.csv"
    if not csv_path.exists():
        # 대체 경로 시도
        csv_path = Path(__file__).parent.parent / "output_files" / f"output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv"
    
    csv_data = None
    if csv_path.exists():
        csv_data = load_incentive_csv_data(csv_path)
    else:
        print(f"Warning: CSV 파일을 찾을 수 없습니다: {csv_path}")
    
    # AQL history 로드
    aql_history = load_aql_history(month)
    
    # 직원 데이터 추출 패턴
    pattern = r'<td>(\d+)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td><span class="type-badge type-\d">(.*?)</span></td>\s*<td>(.*?)</td>\s*<td><strong>(.*?)</strong></td>\s*<td[^>]*>(.*?)</td>\s*<td>(.*?)</td>'
    
    employees = []
    for match in re.finditer(pattern, content):
        emp = {
            'emp_no': match.group(1),
            'name': match.group(2),
            'position': match.group(3),
            'type': match.group(4),
            'june_incentive': match.group(5),
            'july_incentive': match.group(6),
            'change': match.group(7),
            'reason': match.group(8)
        }
        
        # 조건 분석 (직급 포함) - Version 4: 실제 값 포함
        conditions = analyze_conditions_with_actual_values(
            emp['reason'], 
            emp['type'], 
            emp['position'],
            emp['emp_no'],
            csv_data,
            aql_history
        )
        emp['conditions'] = conditions
        
        # 디버깅: 처음 몇 개 직원의 조건 출력
        if len(employees) < 3:
            print(f"Employee {emp['emp_no']} conditions: {list(conditions.keys()) if conditions else 'None'}")
        
        employees.append(emp)
    
    # Excel 파일에서 Stop working Date 정보 추가
    employees = add_stop_working_date(employees)
    
    return employees

def add_stop_working_date(employees):
    """Excel 파일에서 Stop working Date 정보 추가"""
    try:
        import pandas as pd
        from pathlib import Path
        
        # Excel 파일 경로 - 루트의 output_files에서 찾기
        # 동적으로 파일 찾기 (가장 최신 Complete.xlsx 파일)
        output_dir = Path(__file__).parent.parent / "output_files"
        excel_files = list(output_dir.glob("output_QIP_incentive_*_Complete.xlsx"))
        
        if excel_files:
            # 가장 최신 파일 사용
            excel_file = max(excel_files, key=lambda p: p.stat().st_mtime)
        else:
            # 파일이 없으면 기본 패턴 사용
            excel_file = output_dir / "output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.xlsx"
        
        if excel_file.exists():
            df = pd.read_excel(excel_file)
            
            # Employee No를 키로 Stop working Date 매핑
            stop_dates = {}
            for _, row in df.iterrows():
                emp_no = str(row.get('Employee No', '')).strip()
                stop_date = row.get('Stop working Date')
                if emp_no and pd.notna(stop_date):
                    stop_dates[emp_no] = pd.to_datetime(stop_date)
            
            # 각 직원에 Stop working Date 추가
            for emp in employees:
                emp_no = emp['emp_no'].strip()
                stop_date = stop_dates.get(emp_no)
                # Timestamp를 문자열로 변환 (JSON serializable)
                if stop_date:
                    emp['stop_working_date'] = stop_date
                    emp['stop_working_date_str'] = stop_date.strftime('%Y-%m-%d')
                else:
                    emp['stop_working_date'] = None
                    emp['stop_working_date_str'] = None
    except Exception as e:
        print(f"Warning: Could not load Stop working Date from Excel: {e}")
        # Excel 파일이 없거나 오류 발생 시 None으로 설정
        for emp in employees:
            emp['stop_working_date'] = None
            emp['stop_working_date_str'] = None
    
    return employees

def analyze_conditions_with_actual_values(reason, emp_type, position='', emp_no='', csv_data=None, aql_history=None):
    """계산 근거에서 조건 분석 (직급별 적용 조건 차별화) - Version 4 실제 값 포함
    
    조건 구조:
    - 출근 조건: 3가지 (출근율, 무단결근, 실제 근무일)
    - AQL 조건: 4가지 (개인 당월, 개인 3개월, 팀/구역, reject율)
    - 5PRS 조건: 2가지 (검사량, 통과율)
    """
    
    # 실제 값 추출 함수
    def extract_actual_value(reason, pattern):
        import re
        match = re.search(pattern, reason)
        if match:
            return match.group(1)
        return None
    
    # CSV에서 실제 값 가져오기
    actual_data = {}
    if csv_data is not None and emp_no:
        emp_row = csv_data[csv_data['Employee No'] == emp_no]
        if not emp_row.empty:
            emp_row = emp_row.iloc[0]
            actual_data = {
                'attendance_rate': 100 - emp_row.get('Absence Rate (raw)', 0) if pd.notna(emp_row.get('Absence Rate (raw)')) else None,
                'unapproved_absences': emp_row.get('Unapproved Absences', 0) if pd.notna(emp_row.get('Unapproved Absences')) else 0,
                'actual_working_days': emp_row.get('Actual Working Days', 0) if pd.notna(emp_row.get('Actual Working Days')) else 0,
                'july_aql_failures': emp_row.get('July AQL Failures', 0) if pd.notna(emp_row.get('July AQL Failures')) else 0,
                'continuous_fail': emp_row.get('Continuous_FAIL', 'NO') if pd.notna(emp_row.get('Continuous_FAIL')) else 'NO',
                'total_validation_qty': emp_row.get('Total Valiation Qty', 0) if pd.notna(emp_row.get('Total Valiation Qty')) else 0,
                'pass_percent': emp_row.get('Pass %', 0) if pd.notna(emp_row.get('Pass %')) else 0,
                'building': emp_row.get('BUILDING', '') if pd.notna(emp_row.get('BUILDING')) else ''
            }
    
    # 관리자급 직급 확인
    manager_positions = [
        'SUPERVISOR', '(V) SUPERVISOR', '(VICE) SUPERVISOR', 'V.SUPERVISOR',
        'MANAGER', 'A.MANAGER', 'ASSISTANT MANAGER', 'SENIOR MANAGER',
        'GROUP LEADER'
    ]
    is_manager = any(pos in position.upper() for pos in manager_positions)
    
    # 기본 조건 설정 - 카테고리 정보 추가
    conditions = {}
    
    # TYPE별 직급별 조건 적용
    if emp_type == 'TYPE-1':
        # TYPE-1 기본 조건 - 출근 조건 세분화 (3가지)
        conditions['attendance_rate'] = {
            'name': '출근율 ≥88%',
            'category': 'attendance',
            'passed': True,
            'value': '정상',
            'actual': None,
            'threshold': '88%',
            'applicable': True
        }
        conditions['absence_days'] = {
            'name': '무단결근 ≤2일',
            'category': 'attendance',
            'passed': True,
            'value': '0일',
            'actual': None,
            'threshold': '2일 이하',
            'applicable': True
        }
        conditions['working_days'] = {
            'name': '실제 근무일 >0일',
            'category': 'attendance',
            'passed': True,
            'value': '정상',
            'actual': None,
            'threshold': '1일 이상',
            'applicable': True
        }
        
        # AQL 조건 세분화 (4가지)
        conditions['aql_monthly'] = {
            'name': '개인 AQL: 당월 실패 0건',
            'category': 'aql',
            'passed': True,
            'value': 'Pass',
            'actual': None,
            'threshold': '0건',
            'applicable': True
        }
        conditions['aql_3month'] = {
            'name': '연속성 체크: 3개월 연속 실패 없음',
            'category': 'aql',
            'passed': True,
            'value': 'Pass',
            'actual': None,
            'threshold': 'Pass',
            'applicable': True
        }
        conditions['subordinate_aql'] = {
            'name': '팀/구역 AQL: 부하직원 3개월 연속 실패자 없음',
            'category': 'aql',
            'passed': True,
            'value': 'Pass',
            'actual': None,
            'threshold': 'Pass',
            'applicable': True
        }
        conditions['area_reject_rate'] = {
            'name': '담당구역 reject율 <3%',
            'category': 'aql',
            'passed': True,
            'value': 'Pass',
            'actual': None,
            'threshold': '<3%',
            'applicable': True
        }
        
        # 5PRS 조건 세분화 (2가지)
        conditions['5prs_volume'] = {
            'name': '5PRS 검사량 ≥100개',
            'category': '5prs',
            'passed': True,
            'value': 'Pass',
            'actual': None,
            'threshold': '≥100개',
            'applicable': True
        }
        conditions['5prs_pass_rate'] = {
            'name': '5PRS 통과율 ≥95%',
            'category': '5prs',
            'passed': True,
            'value': 'Pass',
            'actual': None,
            'threshold': '≥95%',
            'applicable': True
        }
        
        # 직급별 조건 적용 차별화
        # ASSEMBLY INSPECTOR - 개인 AQL과 5PRS만 적용 (부하직원/구역 미적용)
        if 'ASSEMBLY INSPECTOR' in position:
            conditions['subordinate_aql']['applicable'] = False
            conditions['subordinate_aql']['value'] = 'N/A'
            conditions['area_reject_rate']['applicable'] = False
            conditions['area_reject_rate']['value'] = 'N/A'
            
        # AQL INSPECTOR - 개인 AQL 당월만 적용
        elif 'AQL INSPECTOR' in position:
            conditions['aql_3month']['applicable'] = False
            conditions['aql_3month']['value'] = 'N/A'
            conditions['subordinate_aql']['applicable'] = False
            conditions['subordinate_aql']['value'] = 'N/A'
            conditions['area_reject_rate']['applicable'] = False
            conditions['area_reject_rate']['value'] = 'N/A'
            conditions['5prs_volume']['applicable'] = False
            conditions['5prs_volume']['value'] = 'N/A'
            conditions['5prs_pass_rate']['applicable'] = False
            conditions['5prs_pass_rate']['value'] = 'N/A'
            
        # 관리자급은 AQL, 5PRS 조건 미적용
        elif is_manager:
            for key in ['aql_monthly', 'aql_3month', 'subordinate_aql', 'area_reject_rate']:
                conditions[key]['applicable'] = False
                conditions[key]['value'] = 'N/A'
            for key in ['5prs_volume', '5prs_pass_rate']:
                conditions[key]['applicable'] = False
                conditions[key]['value'] = 'N/A'
                
        # LINE LEADER - 부하직원 AQL만 적용
        elif 'LINE LEADER' in position:
            conditions['aql_monthly']['applicable'] = False
            conditions['aql_monthly']['value'] = 'N/A'
            conditions['aql_3month']['applicable'] = False
            conditions['aql_3month']['value'] = 'N/A'
            conditions['area_reject_rate']['applicable'] = False
            conditions['area_reject_rate']['value'] = 'N/A'
            conditions['5prs_volume']['applicable'] = False
            conditions['5prs_volume']['value'] = 'N/A'
            conditions['5prs_pass_rate']['applicable'] = False
            conditions['5prs_pass_rate']['value'] = 'N/A'
            
        # AUDIT & TRAINING TEAM - 부하직원 AQL + 구역 reject율 적용
        elif 'AUDIT' in position or 'TRAINING' in position:
            conditions['aql_monthly']['applicable'] = False
            conditions['aql_monthly']['value'] = 'N/A'
            conditions['aql_3month']['applicable'] = False
            conditions['aql_3month']['value'] = 'N/A'
            conditions['5prs_volume']['applicable'] = False
            conditions['5prs_volume']['value'] = 'N/A'
            conditions['5prs_pass_rate']['applicable'] = False
            conditions['5prs_pass_rate']['value'] = 'N/A'
            
        # MODEL MASTER - 구역 reject율만 적용 (전체구역)
        elif 'MODEL MASTER' in position:
            conditions['aql_monthly']['applicable'] = False
            conditions['aql_monthly']['value'] = 'N/A'
            conditions['aql_3month']['applicable'] = False
            conditions['aql_3month']['value'] = 'N/A'
            conditions['subordinate_aql']['applicable'] = False
            conditions['subordinate_aql']['value'] = 'N/A'
            conditions['5prs_volume']['applicable'] = False
            conditions['5prs_volume']['value'] = 'N/A'
            conditions['5prs_pass_rate']['applicable'] = False
            conditions['5prs_pass_rate']['value'] = 'N/A'
            
    elif emp_type == 'TYPE-2':
        # TYPE-2 기본 조건 (AQL, 5PRS 미적용) - 출근 조건만 적용
        conditions['attendance_rate'] = {
            'name': '출근율 ≥88%',
            'category': 'attendance',
            'passed': True,
            'value': '정상',
            'actual': None,
            'threshold': '88%',
            'applicable': True
        }
        conditions['absence_days'] = {
            'name': '무단결근 ≤2일',
            'category': 'attendance',
            'passed': True,
            'value': '0일',
            'actual': None,
            'threshold': '2일 이하',
            'applicable': True
        }
        conditions['working_days'] = {
            'name': '실제 근무일 >0일',
            'category': 'attendance',
            'passed': True,
            'value': '정상',
            'actual': None,
            'threshold': '1일 이상',
            'applicable': True
        }
        
        # AQL 조건 - TYPE-2는 미적용
        conditions['aql_monthly'] = {
            'name': '개인 AQL: 당월 실패 0건',
            'category': 'aql',
            'passed': True,
            'value': 'N/A',
            'actual': None,
            'threshold': 'N/A',
            'applicable': False
        }
        conditions['aql_3month'] = {
            'name': '연속성 체크: 3개월 연속 실패 없음',
            'category': 'aql',
            'passed': True,
            'value': 'N/A',
            'actual': None,
            'threshold': 'N/A',
            'applicable': False
        }
        conditions['subordinate_aql'] = {
            'name': '팀/구역 AQL: 부하직원 3개월 연속 실패자 없음',
            'category': 'aql',
            'passed': True,
            'value': 'N/A',
            'actual': None,
            'threshold': 'N/A',
            'applicable': False
        }
        conditions['area_reject_rate'] = {
            'name': '담당구역 reject율 <3%',
            'category': 'aql',
            'passed': True,
            'value': 'N/A',
            'actual': None,
            'threshold': 'N/A',
            'applicable': False
        }
        
        # 5PRS 조건 - TYPE-2는 미적용
        conditions['5prs_volume'] = {
            'name': '5PRS 검사량 ≥100개',
            'category': '5prs',
            'passed': True,
            'value': 'N/A',
            'actual': None,
            'threshold': 'N/A',
            'applicable': False
        }
        conditions['5prs_pass_rate'] = {
            'name': '5PRS 통과율 ≥95%',
            'category': '5prs',
            'passed': True,
            'value': 'N/A',
            'actual': None,
            'threshold': 'N/A',
            'applicable': False
        }
    
    # CSV 데이터에서 실제 값 설정 (Version 4 추가)
    if actual_data:
        # 출근율 실제 값 - 항상 실제 값 설정
        if 'attendance_rate' in conditions and conditions['attendance_rate']['applicable']:
            if actual_data.get('attendance_rate') is not None:
                actual_rate = actual_data['attendance_rate']
                conditions['attendance_rate']['actual'] = f"{actual_rate:.1f}%"
                if actual_rate < 88:
                    conditions['attendance_rate']['passed'] = False
                    conditions['attendance_rate']['value'] = '기준 미달'
                else:
                    conditions['attendance_rate']['passed'] = True
                    conditions['attendance_rate']['value'] = '정상'
        
        # 무단결근 실제 값 - 항상 실제 값 설정
        if 'absence_days' in conditions and conditions['absence_days']['applicable']:
            if actual_data.get('unapproved_absences') is not None:
                actual_days = int(actual_data['unapproved_absences'])
                conditions['absence_days']['actual'] = f"{actual_days}일"
                if actual_days > 2:
                    conditions['absence_days']['passed'] = False
                    conditions['absence_days']['value'] = '기준 초과'
                else:
                    conditions['absence_days']['passed'] = True
                    conditions['absence_days']['value'] = '정상'
        
        # 실제 근무일 실제 값 - 항상 실제 값 설정
        if 'working_days' in conditions and conditions['working_days']['applicable']:
            if actual_data.get('actual_working_days') is not None:
                actual_days = int(actual_data['actual_working_days'])
                conditions['working_days']['actual'] = f"{actual_days}일"
                if actual_days == 0:
                    conditions['working_days']['passed'] = False
                    conditions['working_days']['value'] = '기준 미달'
                else:
                    conditions['working_days']['passed'] = True
                    conditions['working_days']['value'] = '정상'
        
        # AQL 실패 건수 실제 값 - 항상 실제 값 설정
        if 'aql_monthly' in conditions and conditions['aql_monthly']['applicable']:
            if actual_data.get('july_aql_failures') is not None:
                failures = int(actual_data['july_aql_failures'])
                conditions['aql_monthly']['actual'] = f"{failures}건"
                if failures > 0:
                    conditions['aql_monthly']['passed'] = False
                    conditions['aql_monthly']['value'] = 'Fail'
                else:
                    conditions['aql_monthly']['passed'] = True
                    conditions['aql_monthly']['value'] = 'Pass'
        
        # 3개월 연속 실패 실제 값
        if 'aql_3month' in conditions and conditions['aql_3month']['applicable']:
            if actual_data.get('continuous_fail') == 'YES':
                conditions['aql_3month']['passed'] = False
                conditions['aql_3month']['value'] = 'Fail'
                # AQL history에서 월별 실패 건수 가져오기
                if aql_history and emp_no in aql_history:
                    emp_aql = aql_history[emp_no]
                    monthly_details = []
                    for month in ['JULY', 'JUNE', 'MAY']:
                        if month in emp_aql:
                            monthly_details.append(f"{month[:3]}: {emp_aql[month]}건")
                    if monthly_details:
                        conditions['aql_3month']['actual'] = ', '.join(monthly_details)
                    else:
                        conditions['aql_3month']['actual'] = '3개월 연속 실패'
                else:
                    conditions['aql_3month']['actual'] = '3개월 연속 실패'
        
        # 5PRS 검사량 실제 값 - 항상 실제 값 설정
        if '5prs_volume' in conditions and conditions['5prs_volume']['applicable']:
            if actual_data.get('total_validation_qty') is not None:
                qty = actual_data['total_validation_qty']
                if pd.notna(qty) and qty != 0:
                    qty = int(qty)
                    conditions['5prs_volume']['actual'] = f"{qty}개"
                    if qty < 100:
                        conditions['5prs_volume']['passed'] = False
                        conditions['5prs_volume']['value'] = 'Fail'
                    else:
                        conditions['5prs_volume']['passed'] = True
                        conditions['5prs_volume']['value'] = 'Pass'
        
        # 5PRS 통과율 실제 값 - 항상 실제 값 설정
        if '5prs_pass_rate' in conditions and conditions['5prs_pass_rate']['applicable']:
            if actual_data.get('pass_percent') is not None:
                pass_rate = actual_data['pass_percent']
                if pd.notna(pass_rate) and pass_rate != 0:
                    pass_rate = float(pass_rate)
                    conditions['5prs_pass_rate']['actual'] = f"{pass_rate:.1f}%"
                    if pass_rate < 95:
                        conditions['5prs_pass_rate']['passed'] = False
                        conditions['5prs_pass_rate']['value'] = 'Fail'
                    else:
                        conditions['5prs_pass_rate']['passed'] = True
                        conditions['5prs_pass_rate']['value'] = 'Pass'
    
    # 실패 조건 파싱 및 실제 값 추출 (기존 reason 파싱 유지)
    if 'AQL 실패' in reason:
        # 당월 AQL 실패 처리
        if conditions.get('aql_monthly', {}).get('applicable', False):
            conditions['aql_monthly']['passed'] = False
            conditions['aql_monthly']['value'] = 'Fail'
            # AQL 실패 횟수 추출
            aql_fails = extract_actual_value(reason, r'AQL[\s:]*([\d]+)건')
            if aql_fails:
                conditions['aql_monthly']['actual'] = f"{aql_fails}건 실패"
            else:
                conditions['aql_monthly']['actual'] = '실패'
        
        # 3개월 연속 실패 체크
        if '3개월 연속' in reason and conditions.get('aql_3month', {}).get('applicable', False):
            conditions['aql_3month']['passed'] = False
            conditions['aql_3month']['value'] = 'Fail'
            conditions['aql_3month']['actual'] = '3개월 연속 실패'
    elif conditions.get('aql_monthly', {}).get('applicable', False) and conditions.get('aql_monthly', {}).get('passed', True):
        conditions['aql_monthly']['actual'] = '0건'
    
    if '결근율' in reason:
        # 실제 결근율 값 추출 - CSV 데이터를 우선하고, 없는 경우에만 reason에서 추출
        if '>12%' in reason:
            conditions['attendance_rate']['passed'] = False
            conditions['attendance_rate']['value'] = '기준 초과'
            # 실제 값이 이미 설정되지 않은 경우에만 reason에서 추출
            if not conditions['attendance_rate'].get('actual'):
                actual_rate = extract_actual_value(reason, r'([\d.]+)%')
                if actual_rate:
                    conditions['attendance_rate']['actual'] = f"{actual_rate}%"
                else:
                    conditions['attendance_rate']['actual'] = '>12%'
    elif conditions.get('attendance_rate', {}).get('applicable', True) and 'attendance_rate' in conditions:
        # 출근율 정상인 경우 실제 값 - CSV 데이터가 없는 경우에만 기본값 설정
        if '출근일수 0' not in reason and not conditions['attendance_rate'].get('actual'):
            conditions['attendance_rate']['actual'] = '≥88%'
    
    if '무단결근' in reason:
        if '>2일' in reason:
            conditions['absence_days']['passed'] = False
            conditions['absence_days']['value'] = '기준 초과'
            # 실제 값이 이미 설정되지 않은 경우에만 reason에서 추출
            if not conditions['absence_days'].get('actual'):
                actual_days = extract_actual_value(reason, r'([\d]+)일')
                if actual_days:
                    conditions['absence_days']['actual'] = f"{actual_days}일"
                else:
                    conditions['absence_days']['actual'] = '>2일'
        else:
            # 무단결근 없거나 기준 충족 - CSV 데이터가 없는 경우에만
            if not conditions['absence_days'].get('actual'):
                conditions['absence_days']['actual'] = '0일'
    elif conditions.get('absence_days', {}).get('applicable', True) and 'absence_days' in conditions:
        if not conditions['absence_days'].get('actual'):
            conditions['absence_days']['actual'] = '0일'
    
    if '5PRS' in reason:
        if '5PRS 조건 미달' in reason:
            # 검사량 부족 체크
            if '검사량' in reason and conditions.get('5prs_volume', {}).get('applicable', False):
                conditions['5prs_volume']['passed'] = False
                conditions['5prs_volume']['value'] = 'Fail'
                # 실제 값이 이미 설정되지 않은 경우에만
                if not conditions['5prs_volume'].get('actual'):
                    volume = extract_actual_value(reason, r'검사량[\s:]*(\d+)')
                    if volume:
                        conditions['5prs_volume']['actual'] = f"{volume}개"
                    else:
                        conditions['5prs_volume']['actual'] = '<100개'
            
            # 통과율 부족 체크
            if '통과율' in reason and conditions.get('5prs_pass_rate', {}).get('applicable', False):
                conditions['5prs_pass_rate']['passed'] = False
                conditions['5prs_pass_rate']['value'] = 'Fail'
                # 실제 값이 이미 설정되지 않은 경우에만
                if not conditions['5prs_pass_rate'].get('actual'):
                    pass_rate = extract_actual_value(reason, r'통과율[\s:]?([\d.]+)%')
                    if pass_rate:
                        conditions['5prs_pass_rate']['actual'] = f"{pass_rate}%"
                    else:
                        conditions['5prs_pass_rate']['actual'] = '<95%'
            # 5PRS 조건 미달이지만 세부 정보가 없는 경우
            elif conditions.get('5prs_volume', {}).get('applicable', False) or conditions.get('5prs_pass_rate', {}).get('applicable', False):
                if conditions.get('5prs_volume', {}).get('applicable', False):
                    conditions['5prs_volume']['passed'] = False
                    conditions['5prs_volume']['value'] = 'Fail'
                    if not conditions['5prs_volume'].get('actual'):
                        conditions['5prs_volume']['actual'] = '<100개'
                if conditions.get('5prs_pass_rate', {}).get('applicable', False):
                    conditions['5prs_pass_rate']['passed'] = False
                    conditions['5prs_pass_rate']['value'] = 'Fail'
                    if not conditions['5prs_pass_rate'].get('actual'):
                        conditions['5prs_pass_rate']['actual'] = '<95%'
        elif conditions.get('5prs_volume', {}).get('applicable', False):
            if not conditions['5prs_volume'].get('actual'):
                conditions['5prs_volume']['actual'] = '≥100개'
            if conditions.get('5prs_pass_rate', {}).get('applicable', False) and not conditions['5prs_pass_rate'].get('actual'):
                conditions['5prs_pass_rate']['actual'] = '≥95%'
    
    if '출근일수' in reason:
        if not conditions['working_days'].get('actual'):
            actual_days = extract_actual_value(reason, r'출근일수[\s:]*([\d]+)')
            if actual_days:
                conditions['working_days']['actual'] = f"{actual_days}일"
        
        if '출근일수 0' in reason:
            conditions['working_days']['passed'] = False
            conditions['working_days']['value'] = '기준 미달'
            if not conditions['working_days'].get('actual'):
                conditions['working_days']['actual'] = '0일'
    elif conditions.get('working_days', {}).get('applicable', True) and 'working_days' in conditions:
        if not conditions['working_days'].get('actual'):
            conditions['working_days']['actual'] = '≥1일'
    
    # 특수 조건들 - 담당구역/전체공장 reject율
    if '담당 구역 reject율' in reason or 'reject율' in reason:
        if conditions.get('area_reject_rate', {}).get('applicable', False):
            conditions['area_reject_rate']['passed'] = False
            conditions['area_reject_rate']['value'] = 'Fail'
            reject_rate = extract_actual_value(reason, r'reject율[\s:]?([\d.]+)%')
            if reject_rate:
                conditions['area_reject_rate']['actual'] = f"{reject_rate}%"
            else:
                conditions['area_reject_rate']['actual'] = '≥3%'
    
    # 부하직원/담당구역 3개월 연속 실패자
    if ('부하직원' in reason or '담당 구역' in reason) and '3개월 연속' in reason:
        if conditions.get('subordinate_aql', {}).get('applicable', False):
            conditions['subordinate_aql']['passed'] = False
            conditions['subordinate_aql']['value'] = 'Fail'
            conditions['subordinate_aql']['actual'] = '3개월 연속 실패자 있음'
    
    return conditions

def generate_improved_dashboard(input_html, output_html, calculation_month='2025-07', month='july', year=2025):
    """개선된 대시보드 HTML 생성 - Version 4 (실제 값 표시 + 다국어 지원)
    
    주요 개선사항:
    - 팝업창 조건 그룹별 표시 (3-4-2 구조)
    - 각 카테고리별 시각적 구분
    - 직급별 적용 조건 명확화
    - 다국어 지원 (한국어, 영어, 베트남어)
    
    Args:
        input_html: 입력 HTML 파일 경로
        output_html: 출력 HTML 파일 경로
        calculation_month: 인센티브 계산 기준 월 (기본값: '2025-07')
    """
    
    # 데이터 추출
    employees = extract_data_from_html(input_html, month=month, year=year)
    
    # 통계 계산 (calculation_month 파라미터 전달)
    stats = calculate_statistics(employees, calculation_month)
    
    # HTML 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 대시보드 - Version 4 (다국어 지원)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }}
        
        .language-selector {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            color: #333;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        /* 테이블 헤더 색상 수정 - 더 진하게 */
        table th {{
            background: #5a67d8 !important;
            color: white !important;
            padding: 12px;
            text-align: left;
            font-weight: 500;
            border: none;
        }}
        
        /* 평균 지급액 헤더 구분 */
        .avg-header {{
            background: #4c5bc0 !important;
            text-align: center !important;
        }}
        
        .sub-header {{
            background: #667eea !important;
            font-size: 0.9em;
        }}
        
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .clickable-cell {{
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .clickable-cell:hover {{
            background-color: #e8f0ff !important;
            text-decoration: underline;
            font-weight: 500;
        }}
        
        .type-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .type-1 {{ background: #e8f5e8; color: #2e7d2e; }}
        .type-2 {{ background: #e8f0ff; color: #1e3a8a; }}
        .type-3 {{ background: #fff5e8; color: #9a3412; }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}
        
        .tab.active {{
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: bold;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        /* Version 4: 실제 값 표시를 위한 스타일 */
        .condition-section {{
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .condition-section-header {{
            padding: 10px 15px;
            font-weight: bold;
            color: white;
        }}
        
        .condition-section-header.attendance {{
            background: #4a5568;
        }}
        
        .condition-section-header.aql {{
            background: #2d3748;
        }}
        
        .condition-section-header.prs {{
            background: #1a202c;
        }}
        
        .condition-check {{
            padding: 12px 15px;
            margin: 0;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .condition-check:last-child {{
            border-bottom: none;
        }}
        
        .condition-check.success {{
            background: #f0fdf4;
            color: #166534;
        }}
        
        .condition-check.fail {{
            background: #fef2f2;
            color: #991b1b;
        }}
        
        .condition-check.not-applicable {{
            background: #f9fafb;
            color: #6b7280;
        }}
        
        /* 실제 값 표시 스타일 추가 */
        .actual-value-container {{
            margin-top: 8px;
            padding: 6px 10px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 6px;
            display: inline-block;
        }}
        
        .actual-label {{
            font-weight: 600;
            color: #374151;
            margin-right: 8px;
        }}
        
        .actual-value {{
            font-weight: 700;
            font-size: 14px;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .actual-value.actual-success {{
            color: #059669;
            background: #d1fae5;
        }}
        
        .actual-value.actual-fail {{
            color: #dc2626;
            background: #fee2e2;
        }}
        
        .condition-icon {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
        
        .condition-value {{
            text-align: right;
            font-weight: 500;
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        
        /* 개선된 필터 스타일 */
        .filter-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .filter-select, .filter-input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-right: 10px;
        }}
        
        .payment-badge {{
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .payment-success {{
            background: #e8f5e8;
            color: #2e7d2e;
        }}
        
        .payment-fail {{
            background: #ffe8e8;
            color: #d32f2f;
        }}
        
        /* 직급별 팝업 테이블 스타일 */
        .table-row-paid {{
            background: #f0fdf4;
        }}
        
        .table-row-paid:hover {{
            background: #dcfce7;
        }}
        
        .table-row-unpaid {{
            background: #fef2f2;
        }}
        
        .table-row-unpaid:hover {{
            background: #fee2e2;
        }}
        
        .stat-section {{
            border-left: 3px solid #667eea;
            padding-left: 10px;
        }}
        
        /* Version 4 추가 스타일 */
        .version-badge {{
            background: #fbbf24;
            color: #78350f;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
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
            <p id="mainSubtitle">2025년 7월 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;">보고서 생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
        </div>
        
        <div class="content p-4">
            <!-- 요약 카드 -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalEmployeesLabel">전체 직원</h6>
                        <h2 id="totalEmployeesValue">{stats['total_employees']}<span class="unit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paidEmployeesLabel">수령 직원</h6>
                        <h2 id="paidEmployeesValue">{stats['paid_employees']}<span class="unit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paymentRateLabel">수령률</h6>
                        <h2 id="paymentRateValue">{stats['payment_rate']:.1f}%</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalAmountLabel">총 지급액</h6>
                        <h2 id="totalAmountValue">{format_currency(stats['total_amount'])}</h2>
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
                {generate_summary_tab(stats)}
            </div>
            
            <!-- 직급별 상세 탭 -->
            <div id="position" class="tab-content">
                {generate_position_tab(employees)}
            </div>
            
            <!-- 개인별 상세 탭 -->
            <div id="detail" class="tab-content">
                {generate_detail_tab(employees)}
            </div>
            
            <!-- 인센티브 기준 탭 -->
            <div id="criteria" class="tab-content">
                {generate_criteria_tab()}
            </div>
        </div>
    </div>
    
    <!-- 직급별 상세 모달 -->
    <div class="modal fade" id="positionDetailModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="positionModalTitle">직급별 인센티브 현황</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="chart-container">
                                <canvas id="positionDoughnutChart"></canvas>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="chart-container">
                                <canvas id="positionBarChart"></canvas>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div id="positionStats"></div>
                        </div>
                    </div>
                    <!-- 조건별 충족 현황 섹션 -->
                    <div class="mt-4 condition-section">
                        <!-- JavaScript로 동적 생성 -->
                    </div>
                    <!-- 직원별 상세 테이블 섹션 -->
                    <div class="employee-detail-table">
                        <!-- JavaScript로 동적 생성 -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 개인별 상세 모달 -->
    <div class="modal fade" id="employeeDetailModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="employeeModalTitle">인센티브 계산 상세</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-header bg-light">
                                    <h6 class="mb-0">기본 정보</h6>
                                </div>
                                <div class="card-body" id="employeeBasicInfo"></div>
                            </div>
                        </div>
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-header bg-light">
                                    <h6 class="mb-0">인센티브 통계</h6>
                                </div>
                                <div class="card-body" id="employeeCalculation"></div>
                            </div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header bg-light">
                            <h6 class="mb-0">조건 충족 현황 (3-4-2 구조)</h6>
                        </div>
                        <div class="card-body p-0" id="employeeConditions"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 다국어 번역 데이터
        const translations = {{
            ko: {{
                title: 'QIP 인센티브 대시보드',
                subtitle: '2025년 7월 인센티브 지급 현황',
                generationDate: '보고서 생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}',
                totalEmployees: '전체 직원',
                paidEmployees: '수령 직원',
                paymentRate: '수령률',
                totalAmount: '총 지급액',
                unit: '명',
                summary: '요약',
                positionDetail: '직급별 상세',
                individualDetail: '개인별 상세',
                incentiveCriteria: '인센티브 기준',
                typeStatus: 'Type별 현황',
                type: 'Type',
                totalCount: '전체 인원',
                paidCount: '수령 인원',
                avgAmount: '평균 지급액',
                paidBasis: '수령인원 기준',
                totalBasis: '총원 기준',
                searchPlaceholder: '이름 또는 직원번호 검색',
                employeeNo: '직원번호',
                name: '이름',
                position: '직급',
                juneIncentive: '6월 인센티브',
                julyIncentive: '7월 인센티브',
                change: '변동',
                reason: '사유',
                attendanceRate: '출근율',
                absenceDays: '무단결근',
                workingDays: '실제 근무일',
                actualValue: '실제값',
                threshold: '기준',
                notApplicable: '평가 대상 아님',
                absenceRateCalc: '결근율 계산 방법',
                paid: '지급',
                unpaid: '미지급',
                passed: '충족',
                failed: '미충족',
                normal: '정상',
                exceeded: '기준 초과',
                insufficient: '기준 미달',
                notEvaluated: '평가 대상 아님',
                pass: 'Pass',
                fail: 'Fail',
                incentiveDetail: '인센티브 계산 상세',
                calculationResult: '계산 결과',
                conditionFulfillment: '조건별 충족 현황',
                fulfillmentRate: '충족율',
                detailView: '상세보기',
                positionDetailTitle: '직급별 상세 현황',
                positionStatus: '직급별 현황',
                detail: '상세',
                positionModalTitle: '직급별 인센티브 현황',
                employeeDetailStatus: '직원별 상세 현황',
                viewPaidOnly: '지급자만',
                viewUnpaidOnly: '미지급자만',
                viewAll: '전체',
                chartPaymentStatus: '지급별 충족 현황',
                chartConditionStatus: '조건별 충족률',
                statisticsTitle: '인센티브 통계',
                basicInfo: '기본 정보',
                conditionCheck: '조건 충족 체크'
            }},
            en: {{
                title: 'QIP Incentive Dashboard',
                subtitle: 'July 2025 Incentive Payment Status',
                generationDate: 'Report Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}',
                totalEmployees: 'Total Employees',
                paidEmployees: 'Paid Employees',
                paymentRate: 'Payment Rate',
                totalAmount: 'Total Amount',
                unit: ' people',
                summary: 'Summary',
                positionDetail: 'Position Detail',
                individualDetail: 'Individual Detail',
                incentiveCriteria: 'Incentive Criteria',
                typeStatus: 'Status by Type',
                type: 'Type',
                totalCount: 'Total Count',
                paidCount: 'Paid Count',
                avgAmount: 'Average Amount',
                paidBasis: 'Based on Paid',
                totalBasis: 'Based on Total',
                searchPlaceholder: 'Search by name or employee number',
                employeeNo: 'Employee No',
                name: 'Name',
                position: 'Position',
                juneIncentive: 'June Incentive',
                julyIncentive: 'July Incentive',
                change: 'Change',
                reason: 'Reason',
                attendanceRate: 'Attendance Rate',
                absenceDays: 'Unapproved Absences',
                workingDays: 'Actual Working Days',
                actualValue: 'Actual',
                threshold: 'Threshold',
                notApplicable: 'Not Applicable',
                absenceRateCalc: 'Absence Rate Calculation Method',
                paid: 'Paid',
                unpaid: 'Unpaid',
                passed: 'Passed',
                failed: 'Failed',
                normal: 'Normal',
                exceeded: 'Exceeded',
                insufficient: 'Insufficient',
                notEvaluated: 'Not Evaluated',
                pass: 'Pass',
                fail: 'Fail',
                incentiveDetail: 'Incentive Calculation Detail',
                calculationResult: 'Calculation Result',
                conditionFulfillment: 'Condition Fulfillment Status',
                fulfillmentRate: 'Fulfillment Rate',
                detailView: 'View Details',
                positionDetailTitle: 'Position Detail Status',
                positionStatus: 'Position Status',
                detail: 'Detail',
                positionModalTitle: 'Position Incentive Status',
                employeeDetailStatus: 'Employee Detail Status',
                viewPaidOnly: 'Paid Only',
                viewUnpaidOnly: 'Unpaid Only',
                viewAll: 'All',
                chartPaymentStatus: 'Payment Status',
                chartConditionStatus: 'Condition Fulfillment Rate',
                statisticsTitle: 'Incentive Statistics',
                basicInfo: 'Basic Information',
                conditionCheck: 'Condition Check'
            }},
            vi: {{
                title: 'Bảng điều khiển Khuyến khích QIP',
                subtitle: 'Tình trạng thanh toán khuyến khích Tháng 7 năm 2025',
                generationDate: 'Báo cáo được tạo: {datetime.now().strftime('%d/%m/%Y %H:%M')}',
                totalEmployees: 'Tổng số nhân viên',
                paidEmployees: 'Nhân viên được trả',
                paymentRate: 'Tỷ lệ thanh toán',
                totalAmount: 'Tổng số tiền',
                unit: ' người',
                summary: 'Tóm tắt',
                positionDetail: 'Chi tiết theo chức vụ',
                individualDetail: 'Chi tiết cá nhân',
                incentiveCriteria: 'Tiêu chí khuyến khích',
                typeStatus: 'Trạng thái theo loại',
                type: 'Loại',
                totalCount: 'Tổng số',
                paidCount: 'Số người được trả',
                avgAmount: 'Số tiền trung bình',
                paidBasis: 'Dựa trên người được trả',
                totalBasis: 'Dựa trên tổng số',
                searchPlaceholder: 'Tìm kiếm theo tên hoặc mã nhân viên',
                employeeNo: 'Mã nhân viên',
                name: 'Họ tên',
                position: 'Chức vụ',
                juneIncentive: 'Khuyến khích tháng 6',
                julyIncentive: 'Khuyến khích tháng 7',
                change: 'Thay đổi',
                reason: 'Lý do',
                attendanceRate: 'Tỷ lệ đi làm',
                absenceDays: 'Ngày vắng không phép',
                workingDays: 'Ngày làm việc thực tế',
                actualValue: 'Thực tế',
                threshold: 'Ngưỡng',
                notApplicable: 'Không áp dụng',
                absenceRateCalc: 'Phương pháp tính tỷ lệ vắng mặt',
                paid: 'Đã trả',
                unpaid: 'Chưa trả',
                passed: 'Đạt',
                failed: 'Không đạt',
                normal: 'Bình thường',
                exceeded: 'Vượt mức',
                insufficient: 'Thiếu',
                notEvaluated: 'Không đánh giá',
                pass: 'Đạt',
                fail: 'Không đạt',
                incentiveDetail: 'Chi tiết tính toán khuyến khích',
                calculationResult: 'Kết quả tính toán',
                conditionFulfillment: 'Trạng thái đáp ứng điều kiện',
                fulfillmentRate: 'Tỷ lệ đáp ứng',
                detailView: 'Xem chi tiết',
                positionDetailTitle: 'Tình trạng chi tiết theo chức vụ',
                positionStatus: 'Tình trạng theo chức vụ',
                detail: 'Chi tiết',
                positionModalTitle: 'Tình trạng khuyến khích theo chức vụ',
                employeeDetailStatus: 'Tình trạng chi tiết nhân viên',
                viewPaidOnly: 'Chỉ người được trả',
                viewUnpaidOnly: 'Chỉ người chưa trả',
                viewAll: 'Tất cả',
                chartPaymentStatus: 'Tình trạng thanh toán',
                chartConditionStatus: 'Tỷ lệ đáp ứng điều kiện',
                statisticsTitle: 'Thống kê khuyến khích',
                basicInfo: 'Thông tin cơ bản',
                conditionCheck: 'Kiểm tra điều kiện'
            }}
        }};
        
        // 현재 언어 (기본값: 한국어)
        let currentLanguage = 'ko';
        
        // 직원 데이터 (JSON serializable하게 변환)
        const employeeData = {json.dumps([dict((k, v) for k, v in emp.items() if k != 'stop_working_date') for emp in employees], ensure_ascii=False, default=str)};
        
        // 차트 인스턴스 저장
        let doughnutChart = null;
        let barChart = null;
        
        // 전역 변수로 현재 번역 객체 저장
        let t = translations[currentLanguage];
        
        // 언어 변경 함수
        function changeLanguage(lang) {{
            currentLanguage = lang;
            t = translations[lang];
            
            // 메인 타이틀과 서브타이틀 업데이트
            document.getElementById('mainTitle').innerHTML = t.title + ' <span class="version-badge">v4.2</span>';
            document.getElementById('mainSubtitle').textContent = t.subtitle;
            if (document.getElementById('generationDate')) {{
                document.getElementById('generationDate').textContent = t.generationDate;
            }}
            
            // 요약 카드 업데이트
            const summaryCards = document.querySelectorAll('.summary-card h6');
            if (summaryCards.length >= 4) {{
                summaryCards[0].textContent = t.totalEmployees;
                summaryCards[1].textContent = t.paidEmployees;
                summaryCards[2].textContent = t.paymentRate;
                summaryCards[3].textContent = t.totalAmount;
            }}
            
            // 숫자 단위 업데이트
            const unitSpans = document.querySelectorAll('.summary-card .unit');
            unitSpans.forEach(span => {{
                span.textContent = t.unit || '명';
            }});
            
            // 탭 버튼 업데이트
            document.getElementById('tabSummary').textContent = t.summary;
            document.getElementById('tabPosition').textContent = t.positionDetail;
            document.getElementById('tabIndividual').textContent = t.individualDetail;
            document.getElementById('tabCriteria').textContent = t.incentiveCriteria;
            
            // Type별 현황 제목 업데이트
            const typeTitle = document.querySelector('#summary h3');
            if (typeTitle) typeTitle.textContent = t.typeStatus;
            
            // 직급별 상세 탭 제목 업데이트
            const positionTabTitle = document.getElementById('positionTabTitle');
            if (positionTabTitle) positionTabTitle.textContent = t.positionDetailTitle;
            
            // 팝업창 제목 업데이트
            const positionModalTitle = document.getElementById('positionModalTitle');
            if (positionModalTitle) positionModalTitle.textContent = t.positionModalTitle;
            
            // 팝업창 내 텍스트 업데이트
            const conditionFulfillmentTitle = document.getElementById('conditionFulfillmentTitle');
            if (conditionFulfillmentTitle) conditionFulfillmentTitle.textContent = t.conditionFulfillment;
            
            const employeeDetailTitle = document.getElementById('employeeDetailTitle');
            if (employeeDetailTitle) employeeDetailTitle.textContent = t.employeeDetailStatus;
            
            // 팝업창 버튼 업데이트
            const btnPaidOnly = document.getElementById('btnPaidOnly');
            if (btnPaidOnly) btnPaidOnly.textContent = t.viewPaidOnly;
            
            const btnUnpaidOnly = document.getElementById('btnUnpaidOnly');
            if (btnUnpaidOnly) btnUnpaidOnly.textContent = t.viewUnpaidOnly;
            
            const btnViewAll = document.getElementById('btnViewAll');
            if (btnViewAll) btnViewAll.textContent = t.viewAll;
            
            // 테이블 헤더 업데이트
            updateTableHeaders();
            
            // 테이블 데이터 업데이트
            updateTableData();
            
            // 검색 플레이스홀더 업데이트
            const searchInput = document.querySelector('input[placeholder*="검색"]');
            if (searchInput) searchInput.placeholder = t.searchPlaceholder;
        }}
        
        // 테이블 데이터 업데이트 함수
        function updateTableData() {{
            
            // 개인별 상세 테이블 데이터 업데이트
            const individualRows = document.querySelectorAll('#individual tbody tr');
            individualRows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                if (cells.length >= 7) {{
                    // 직급 번역
                    const position = cells[2].textContent.trim();
                    cells[2].textContent = translateDataValue('position', position);
                    
                    // 사유 번역 (여러 사유가 있을 수 있음)
                    const reasonCell = cells[6];
                    const reasons = reasonCell.textContent.split(',').map(r => r.trim());
                    const translatedReasons = reasons.map(r => translateDataValue('reason', r));
                    reasonCell.textContent = translatedReasons.join(', ');
                }}
            }});
            
            // 직급별 상세 테이블의 직급명 번역
            const positionRows = document.querySelectorAll('#position tbody tr');
            positionRows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                if (cells.length > 0) {{
                    const position = cells[0].textContent.trim();
                    cells[0].textContent = translateDataValue('position', position);
                }}
            }});
        }}
        
        // 번역 헬퍼 함수들
        function translateConditionName(name) {{
            const nameMap = {{
                '출근율': {{ ko: '출근율', en: 'Attendance Rate', vi: 'Tỷ lệ đi làm' }},
                '무단결근': {{ ko: '무단결근', en: 'Unexcused Absence', vi: 'Vắng không phép' }},
                '실제 근무일': {{ ko: '실제 근무일', en: 'Actual Work Days', vi: 'Ngày làm thực tế' }},
                'AQL 실패': {{ ko: 'AQL 실패', en: 'AQL Failures', vi: 'Thất bại AQL' }},
                '5PRS 검사량': {{ ko: '5PRS 검사량', en: '5PRS Volume', vi: 'Khối lượng 5PRS' }},
                '5PRS 합격률': {{ ko: '5PRS 합격률', en: '5PRS Pass Rate', vi: 'Tỷ lệ đạt 5PRS' }},
                '부하직원 조건': {{ ko: '부하직원 조건', en: 'Subordinate Condition', vi: 'Điều kiện nhân viên' }}
            }};
            return nameMap[name] ? nameMap[name][currentLanguage] : name;
        }}
        
        function translateConditionValue(value) {{
            const valueMap = {{
                'Pass': {{ ko: '충족', en: 'Pass', vi: 'Đạt' }},
                'Fail': {{ ko: '미충족', en: 'Fail', vi: 'Không đạt' }},
                '정상': {{ ko: '정상', en: 'Normal', vi: 'Bình thường' }},
                '기준 초과': {{ ko: '기준 초과', en: 'Exceeded', vi: 'Vượt tiêu chuẩn' }},
                '기준 미달': {{ ko: '기준 미달', en: 'Below Standard', vi: 'Dưới tiêu chuẩn' }},
                '평가 대상 아님': {{ ko: '평가 대상 아님', en: 'Not Applicable', vi: 'Không áp dụng' }}
            }};
            return valueMap[value] ? valueMap[value][currentLanguage] : value;
        }}
        
        function translateThreshold(threshold) {{
            // 숫자와 단위 분리
            if (threshold.includes('≥')) {{
                return threshold; // 이미 포맷된 경우 그대로 반환
            }}
            if (threshold.includes('≤')) {{
                return threshold;
            }}
            if (threshold.includes('<')) {{
                return threshold;
            }}
            if (threshold.includes('>')) {{
                return threshold;
            }}
            
            // 특수 케이스 번역
            const specialMap = {{
                '0건': {{ ko: '0건', en: '0 cases', vi: '0 trường hợp' }},
                '2일 이하': {{ ko: '2일 이하', en: '≤2 days', vi: '≤2 ngày' }},
                '0일': {{ ko: '0일', en: '0 days', vi: '0 ngày' }},
                'N/A': {{ ko: 'N/A', en: 'N/A', vi: 'N/A' }}
            }};
            
            return specialMap[threshold] ? specialMap[threshold][currentLanguage] : threshold;
        }}
        
        function translateDataValue(key, value) {{
            
            // 타입 번역
            if (key === 'type' || key === 'Type') {{
                return value; // TYPE-1, TYPE-2, TYPE-3는 그대로 유지
            }}
            
            // 직급 번역
            if (key === 'position' || key === 'Position') {{
                const positionMap = {{
                    'Assembly Inspector': {{ ko: '조립 검사자', en: 'Assembly Inspector', vi: 'Kiểm tra lắp ráp' }},
                    'AQL Inspector': {{ ko: 'AQL 검사자', en: 'AQL Inspector', vi: 'Kiểm tra AQL' }},
                    'Line Leader': {{ ko: '라인 리더', en: 'Line Leader', vi: 'Trưởng dây chuyền' }},
                    'Auditor/Trainer': {{ ko: '감사/교육담당', en: 'Auditor/Trainer', vi: 'Kiểm toán/Đào tạo' }},
                    'Model Master': {{ ko: '모델 마스터', en: 'Model Master', vi: 'Chuyên gia mẫu' }}
                }};
                return positionMap[value] ? positionMap[value][currentLanguage] : value;
            }}
            
            // 지급/미지급 상태
            if (value === '지급' || value === 'Paid' || value === 'Đã trả') {{
                return {{ ko: '지급', en: 'Paid', vi: 'Đã trả' }}[currentLanguage];
            }}
            if (value === '미지급' || value === 'Unpaid' || value === 'Chưa trả') {{
                return {{ ko: '미지급', en: 'Unpaid', vi: 'Chưa trả' }}[currentLanguage];
            }}
            
            // 사유 번역
            if (key === 'reason' || key === 'Reason') {{
                const reasonMap = {{
                    '출근일수 0': {{ ko: '출근일수 0', en: 'Zero attendance', vi: 'Không đi làm' }},
                    '무단결근 >2일': {{ ko: '무단결근 >2일', en: 'Unexcused absence >2 days', vi: 'Vắng không phép >2 ngày' }},
                    '결근율 >12%': {{ ko: '결근율 >12%', en: 'Absence rate >12%', vi: 'Tỷ lệ vắng >12%' }},
                    '최소근무일 미달': {{ ko: '최소근무일 미달', en: 'Below minimum workdays', vi: 'Dưới ngày làm tối thiểu' }},
                    '3개월 연속 AQL 실패': {{ ko: '3개월 연속 AQL 실패', en: '3 months consecutive AQL failure', vi: 'Thất bại AQL 3 tháng liên tiếp' }},
                    '퇴사': {{ ko: '퇴사', en: 'Resigned', vi: 'Nghỉ việc' }},
                    'TYPE-3 정책 제요': {{ ko: 'TYPE-3 정책 제외', en: 'TYPE-3 policy exclusion', vi: 'Loại trừ chính sách TYPE-3' }}
                }};
                return reasonMap[value] ? reasonMap[value][currentLanguage] : value;
            }}
            
            return value;
        }}
        
        // 테이블 헤더 업데이트 함수
        function updateTableHeaders() {{
            
            // Type별 테이블 헤더
            const typeTableHeaders = document.querySelectorAll('#summary table th');
            if (typeTableHeaders.length > 0) {{
                typeTableHeaders[0].textContent = t.type;
                typeTableHeaders[1].textContent = t.totalCount;
                typeTableHeaders[2].textContent = t.paidCount;
                typeTableHeaders[3].textContent = t.paymentRate;
                typeTableHeaders[4].textContent = t.totalAmount;
                typeTableHeaders[5].textContent = t.avgAmount;
                // 평균 지급액 서브헤더
                if (typeTableHeaders[6]) typeTableHeaders[6].textContent = t.paidBasis;
                if (typeTableHeaders[7]) typeTableHeaders[7].textContent = t.totalBasis;
            }}
            
            // 직급별 상세 테이블 헤더
            const positionTableHeaders = document.querySelectorAll('#position table th');
            if (positionTableHeaders.length > 0) {{
                positionTableHeaders[0].textContent = t.position;
                positionTableHeaders[1].textContent = t.type;
                positionTableHeaders[2].textContent = t.totalCount;
                positionTableHeaders[3].textContent = t.paidCount;
                positionTableHeaders[4].textContent = t.paymentRate;
                positionTableHeaders[5].textContent = t.totalAmount;
                positionTableHeaders[6].textContent = t.avgAmount;
            }}
            
            // 개인별 상세 테이블 헤더
            const individualTableHeaders = document.querySelectorAll('#individual table th');
            if (individualTableHeaders.length > 0) {{
                individualTableHeaders[0].textContent = t.employeeNo;
                individualTableHeaders[1].textContent = t.name;
                individualTableHeaders[2].textContent = t.position;
                individualTableHeaders[3].textContent = t.type;
                individualTableHeaders[4].textContent = t.juneIncentive;
                individualTableHeaders[5].textContent = t.julyIncentive;
                individualTableHeaders[6].textContent = t.change;
                individualTableHeaders[7].textContent = t.reason;
            }}
        }}
        
        // 탭 전환
        function showTab(tabName) {{
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.toggle('active', tab.dataset.tab === tabName);
            }});
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.toggle('active', content.id === tabName);
            }});
        }}
        
        // 직급별 상세 팝업
        function showPositionDetail(type, position) {{
            const modal = new bootstrap.Modal(document.getElementById('positionDetailModal'));
            document.getElementById('positionModalTitle').textContent = `${{type}} - ${{translateDataValue('position', position)}} ${{t.incentiveDetail || '인센티브 현황'}}`;
            
            // 해당 직급 데이터 필터링
            const filteredData = employeeData.filter(emp => 
                emp.type === type && emp.position === position
            );
            
            // 지급/미지급 정확한 계산
            const paid = filteredData.filter(emp => {{
                const amount = parseFloat(emp.july_incentive.replace(/[^0-9]/g, '')) || 0;
                return amount > 0;
            }}).length;
            const unpaid = filteredData.length - paid;
            
            // 기존 차트 제거
            if (doughnutChart) doughnutChart.destroy();
            if (barChart) barChart.destroy();
            
            // 도넛 차트 - 중앙에 지급률 표시 (NaN 방지)
            const paymentRate = filteredData.length > 0 
                ? ((paid / filteredData.length) * 100).toFixed(1) 
                : '0.0';
            const ctxDoughnut = document.getElementById('positionDoughnutChart').getContext('2d');
            doughnutChart = new Chart(ctxDoughnut, {{
                type: 'doughnut',
                data: {{
                    labels: ['지급', '미지급'],
                    datasets: [{{
                        data: [paid, unpaid],
                        backgroundColor: ['#4caf50', '#f44336'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '60%',  // 도넛 중앙 공간 확대
                    plugins: {{
                        legend: {{ position: 'bottom' }},
                        title: {{
                            display: true,
                            text: translations[currentLanguage].chartPaymentStatus || '지급/미지급 비율'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}}명 (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }},
                plugins: [{{
                    id: 'centerText',
                    beforeDraw: function(chart) {{
                        const ctx = chart.ctx;
                        const width = chart.width;
                        const height = chart.height;
                        
                        ctx.restore();
                        const fontSize = (height / 100).toFixed(2);
                        
                        // 지급률 숫자 - 더 크고 진하게
                        ctx.font = `bold 32px sans-serif`;
                        ctx.textBaseline = 'middle';
                        ctx.textAlign = 'center';
                        
                        const text = `${{paymentRate}}%`;
                        const textX = width / 2;
                        const textY = height / 2 - 10;
                        
                        ctx.fillStyle = '#2e7d32';  // 진한 초록색
                        ctx.fillText(text, textX, textY);
                        
                        // 지급률 텍스트
                        ctx.font = '14px sans-serif';
                        ctx.fillStyle = '#333';  // 진한 회색
                        ctx.fillText('지급률', textX, textY + 25);
                        ctx.save();
                    }}
                }}]
            }});
            
            // 막대 차트 - 조건별 충족률 (타입/직급별 차별화)
            console.log('showPositionDetail - Filtered data for conditions:', filteredData);
            const conditions = analyzeConditions(filteredData, type, position);
            console.log('showPositionDetail - Analyzed conditions result:', conditions);
            const ctxBar = document.getElementById('positionBarChart').getContext('2d');
            barChart = new Chart(ctxBar, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(conditions),
                    datasets: [{{
                        label: '충족률 (%)',
                        data: Object.values(conditions).map(c => c.rate),
                        backgroundColor: '#667eea',
                        borderColor: '#5a67d8',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: translations[currentLanguage].chartConditionStatus || '조건별 충족률'
                        }}
                    }}
                }}
            }});
            
            // 통계 표시 - 개선된 구조
            const stats = calculatePositionStats(filteredData);
            
            // 평균 충족률 계산
            let totalFulfillment = 0;
            let fulfillmentCount = 0;
            filteredData.forEach(emp => {{
                if (emp.conditions) {{
                    let metConditions = 0;
                    let totalConditions = 0;
                    Object.values(emp.conditions).forEach(cond => {{
                        if (cond.applicable !== false) {{
                            totalConditions++;
                            if (cond.passed) metConditions++;
                        }}
                    }});
                    if (totalConditions > 0) {{
                        totalFulfillment += (metConditions / totalConditions) * 100;
                        fulfillmentCount++;
                    }}
                }}
            }});
            const avgFulfillment = fulfillmentCount > 0 ? (totalFulfillment / fulfillmentCount).toFixed(1) : 0;
            
            // 직급별 통계 표시 - 간소화된 버전
            document.getElementById('positionStats').innerHTML = `
                <div class="card">
                    <div class="card-body p-3">
                        <h6 class="fw-bold mb-3">📊 ${{t.statisticsTitle || '인원 현황'}}</h6>
                        
                        <!-- 인원 현황 -->
                        <div class="stat-section mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="text-muted">${{t.totalCount || '총원'}}</span>
                                <span class="fw-bold">${{filteredData.length}}${{t.unit || '명'}}</span>
                            </div>
                            <div class="progress mb-2" style="height: 25px;">
                                <div class="progress-bar bg-success" style="width: ${{(paid/filteredData.length*100)}}%">
                                    ${{t.paid || '지급'}} ${{paid}}${{t.unit || '명'}}
                                </div>
                                <div class="progress-bar bg-danger" style="width: ${{(unpaid/filteredData.length*100)}}%">
                                    ${{t.unpaid || '미지급'}} ${{unpaid}}${{t.unit || '명'}}
                                </div>
                            </div>
                            <div class="d-flex justify-content-between small">
                                <span class="text-success">${{t.paymentRate || '지급률'}}: ${{(paid/filteredData.length*100).toFixed(1)}}%</span>
                                <span class="text-danger">${{t.unpaid || '미지급'}}률: ${{(unpaid/filteredData.length*100).toFixed(1)}}%</span>
                            </div>
                        </div>
                        
                        <!-- 금액 통계 -->
                        <div class="stat-section mb-3">
                            <div class="alert alert-info p-2 mb-2">
                                <div class="d-flex justify-content-between">
                                    <small>${{t.paidBasis || '수령인원 기준'}}</small>
                                    <strong>${{stats.avgPaid}}</strong>
                                </div>
                            </div>
                            <div class="alert alert-secondary p-2">
                                <div class="d-flex justify-content-between">
                                    <small>${{t.totalBasis || '총원 기준'}}</small>
                                    <strong>${{stats.avgTotal}}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 조건 충족률 -->
                        <div class="stat-section">
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="text-muted">${{t.average || '평균'}} ${{t.fulfillmentRate || '충족률'}}</span>
                                <span class="badge bg-${{avgFulfillment >= 80 ? 'success' : avgFulfillment >= 50 ? 'warning' : 'danger'}} fs-6">
                                    ${{avgFulfillment}}%
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 조건별 테이블 - 3-4-2 그룹으로 재구성
            const conditionGroups = {{
                attendance: {{
                    title: '📅 출근 조건 (3가지)',
                    conditions: [],
                    bgClass: 'bg-primary bg-opacity-10'
                }},
                aql: {{
                    title: '🎯 AQL 조건 (4가지)', 
                    conditions: [],
                    bgClass: 'bg-success bg-opacity-10'
                }},
                '5prs': {{
                    title: '📊 5PRS 조건 (2가지)',
                    conditions: [],
                    bgClass: 'bg-info bg-opacity-10'
                }}
            }};
            
            // 조건을 그룹별로 분류 (9개 조건)
            Object.entries(conditions).forEach(([name, data]) => {{
                // 출근 조건 (3개)
                if (name.includes('출근율') || name.includes('무단결근') || name.includes('실제 근무일')) {{
                    conditionGroups.attendance.conditions.push({{name, ...data}});
                }}
                // AQL 조건 (4개)
                else if (name.includes('AQL') || name.includes('연속성 체크') || name.includes('reject율')) {{
                    conditionGroups.aql.conditions.push({{name, ...data}});
                }}
                // 5PRS 조건 (2개)
                else if (name.includes('5PRS')) {{
                    conditionGroups['5prs'].conditions.push({{name, ...data}});
                }}
            }});
            
            // 조건별 충족 현황 HTML 생성
            let conditionHtml = '';
            Object.entries(conditionGroups).forEach(([groupKey, group]) => {{
                if (group.conditions.length > 0) {{
                    conditionHtml += `
                        <div class="condition-group mb-3">
                            <h6 class="p-2 mb-0 ${{group.bgClass}} rounded-top">
                                ${{group.title}}
                            </h6>
                            <table class="table table-sm table-bordered mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th width="30%">조건</th>
                                        <th width="20%">평가 대상</th>
                                        <th width="15%">충족</th>
                                        <th width="15%">미충족</th>
                                        <th width="20%">충족률</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    group.conditions.forEach(condition => {{
                        const applicable = condition.passed + condition.failed;
                        if (!condition.applicable || applicable === 0) {{
                            conditionHtml += `
                                <tr class="table-secondary">
                                    <td>${{condition.name}}</td>
                                    <td colspan="4" class="text-center text-muted">평가 대상 아님</td>
                                </tr>
                            `;
                        }} else {{
                            const notApplicableText = condition.notApplicable > 0 ? ` <small class="text-muted">(${{condition.notApplicable}}명 제외)</small>` : '';
                            const rateClass = condition.rate >= 80 ? 'text-success' : condition.rate >= 50 ? 'text-warning' : 'text-danger';
                            conditionHtml += `
                                <tr>
                                    <td>${{condition.name}}</td>
                                    <td>${{applicable}}명${{notApplicableText}}</td>
                                    <td class="text-success">${{condition.passed}}명</td>
                                    <td class="text-danger">${{condition.failed}}명</td>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="progress flex-grow-1 me-2" style="height: 20px;">
                                                <div class="progress-bar bg-success" style="width: ${{condition.rate}}%">
                                                    ${{condition.rate.toFixed(1)}}%
                                                </div>
                                            </div>
                                            <span class="fw-bold ${{rateClass}}">${{condition.rate.toFixed(1)}}%</span>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }}
                    }});
                    
                    conditionHtml += `
                                </tbody>
                            </table>
                        </div>
                    `;
                }}
            }});
            
            // 조건별 충족 현황 섹션 업데이트 - ID 추가하여 명확히 구분
            const conditionSection = document.querySelector('#positionDetailModal .condition-section');
            if (conditionSection) {{
                conditionSection.innerHTML = `
                    <h6 class="fw-bold mb-3" id="conditionFulfillmentTitle">조건별 충족 현황</h6>
                    ${{conditionHtml}}
                `;
            }}
            
            // 직원별 상세 테이블 - 개선된 시각화
            const employeeDetailHtml = `
                <div class="mt-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-0" id="employeeDetailTitle">직원별 상세 현황</h6>
                        <div class="btn-group btn-group-sm" role="group">
                            <button type="button" class="btn btn-outline-success" onclick="filterPositionTable('paid')" id="btnPaidOnly">
                                지급자만
                            </button>
                            <button type="button" class="btn btn-outline-danger" onclick="filterPositionTable('unpaid')" id="btnUnpaidOnly">
                                미지급자만
                            </button>
                            <button type="button" class="btn btn-outline-secondary" onclick="filterPositionTable('all')" id="btnViewAll">
                                전체
                            </button>
                        </div>
                    </div>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-sm table-hover" id="positionEmployeeTable">
                            <thead style="position: sticky; top: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; z-index: 10;">
                                <tr>
                                    <th width="10%">직원번호</th>
                                    <th width="12%">이름</th>
                                    <th width="12%">인센티브</th>
                                    <th width="8%">상태</th>
                                    <th width="38%">조건 충족 현황</th>
                                    <th width="20%">계산 근거</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{filteredData.map(emp => {{
                                    const amount = parseFloat(emp.july_incentive.replace(/[^0-9]/g, '')) || 0;
                                    const isPaid = amount > 0;
                                    const rowClass = isPaid ? 'table-row-paid' : 'table-row-unpaid';
                                    
                                    // 조건 충족률 계산
                                    let metConditions = 0;
                                    let totalConditions = 0;
                                    if (emp.conditions) {{
                                        Object.values(emp.conditions).forEach(cond => {{
                                            if (cond.applicable !== false) {{
                                                totalConditions++;
                                                if (cond.passed) metConditions++;
                                            }}
                                        }});
                                    }}
                                    const fulfillmentRate = totalConditions > 0 ? Math.round((metConditions / totalConditions) * 100) : 0;
                                    
                                    // 조건 상태 미니 표시
                                    const getConditionBadge = (condition, label) => {{
                                        if (!condition) return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: -</span>`;
                                        if (condition.applicable === false) return `<span class="badge bg-light text-dark" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        const bgClass = condition.passed ? 'bg-success' : 'bg-danger';
                                        const icon = condition.passed ? '✓' : '✗';
                                        return `<span class="badge ${{bgClass}}" style="font-size: 0.9em;" title="${{condition.actual || condition.value}}">${{label}}: ${{icon}}</span>`;
                                    }};
                                    
                                    return `
                                        <tr class="${{rowClass}}" data-payment="${{isPaid ? 'paid' : 'unpaid'}}" onclick="showEmployeeDetail('${{emp.emp_no}}')" style="cursor: pointer;">
                                            <td>${{emp.emp_no}}</td>
                                            <td><strong>${{emp.name}}</strong></td>
                                            <td class="fw-bold ${{isPaid ? 'text-success' : 'text-danger'}}">${{emp.july_incentive}}</td>
                                            <td>
                                                <span class="badge ${{isPaid ? 'bg-success' : 'bg-danger'}}">
                                                    ${{isPaid ? '지급' : '미지급'}}
                                                </span>
                                            </td>
                                            <td>
                                                <div class="d-flex flex-wrap gap-2">
                                                    ${{getConditionBadge(emp.conditions?.attendance_rate, '출근')}}
                                                    ${{getConditionBadge(emp.conditions?.aql_status, 'AQL')}}
                                                    ${{getConditionBadge(emp.conditions?.absence_days, '결근')}}
                                                    ${{getConditionBadge(emp.conditions?.['5prs_condition'], '5PRS')}}
                                                </div>
                                                <div class="progress mt-1" style="height: 15px;">
                                                    <div class="progress-bar ${{fulfillmentRate >= 80 ? 'bg-success' : fulfillmentRate >= 50 ? 'bg-warning' : 'bg-danger'}}" 
                                                         style="width: ${{fulfillmentRate}}%" 
                                                         title="충족률: ${{fulfillmentRate}}%">
                                                    </div>
                                                </div>
                                            </td>
                                            <td><small class="text-muted">${{emp.reason}}</small></td>
                                        </tr>
                                    `;
                                }}).join('')}}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            
            // 직원별 상세 테이블 추가 - 기존 섹션에 직접 삽입
            const employeeDetailSection = document.querySelector('#positionDetailModal .employee-detail-table');
            if (employeeDetailSection) {{
                employeeDetailSection.innerHTML = employeeDetailHtml;
            }}
            
            modal.show();
        }}
        
        // 개인별 상세 팝업 - Version 4 실제 값 표시
        function showEmployeeDetail(empNo) {{
            const modal = new bootstrap.Modal(document.getElementById('employeeDetailModal'));
            const employee = employeeData.find(emp => emp.emp_no === empNo);
            
            if (!employee) return;
            
            document.getElementById('employeeModalTitle').textContent = 
                `${{employee.name}} (${{employee.emp_no}}) ${{t.incentiveDetail || '인센티브 계산 상세'}}`;
            
            // 기본 정보
            document.getElementById('employeeBasicInfo').innerHTML = `
                <table class="table table-sm mb-0">
                    <tr><td width="40%">${{t.employeeNo}}:</td><td><strong>${{employee.emp_no}}</strong></td></tr>
                    <tr><td>${{t.name}}:</td><td><strong>${{employee.name}}</strong></td></tr>
                    <tr><td>${{t.position}}:</td><td>${{translateDataValue('position', employee.position)}}</td></tr>
                    <tr><td>${{t.type}}:</td><td><span class="type-badge type-${{employee.type.slice(-1).toLowerCase()}}">${{employee.type}}</span></td></tr>
                </table>
            `;
            
            // 계산 결과 - 직급별 현황과 동일한 형식으로 개선
            const julyAmount = parseFloat(employee.july_incentive.replace(/[^0-9]/g, '')) || 0;
            const status = julyAmount > 0 ? '지급' : '미지급';
            const statusClass = julyAmount > 0 ? 'payment-success' : 'payment-fail';
            
            // 충족율 계산
            let metConditions = 0;
            let totalConditions = 0;
            if (employee.conditions) {{
                Object.values(employee.conditions).forEach(cond => {{
                    if (cond.applicable !== false) {{
                        totalConditions++;
                        if (cond.passed) metConditions++;
                    }}
                }});
            }}
            const fulfillmentRate = totalConditions > 0 ? Math.round((metConditions / totalConditions) * 100) : 0;
            
            // 개인 인센티브 정보 표시
            document.getElementById('employeeCalculation').innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="fw-bold mb-3">6월 인센티브</h6>
                        <table class="table table-sm">
                            <tr>
                                <td width="50%">지급액:</td>
                                <td class="text-end"><strong>${{employee.june_incentive}}</strong></td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6 class="fw-bold mb-3">7월 인센티브</h6>
                        <table class="table table-sm">
                            <tr>
                                <td width="50%">지급액:</td>
                                <td class="text-end"><strong>${{employee.july_incentive}}</strong></td>
                            </tr>
                            <tr>
                                <td>변동:</td>
                                <td class="text-end">
                                    <span class="${{employee.change.includes('+') ? 'text-success' : employee.change.includes('-') ? 'text-danger' : 'text-secondary'}}">
                                        ${{employee.change}}
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td>상태:</td>
                                <td class="text-end">
                                    <span class="${{statusClass}}">${{status}}</span>
                                </td>
                            </tr>
                            <tr>
                                <td>조건 충족율:</td>
                                <td class="text-end">
                                    <span class="${{fulfillmentRate >= 80 ? 'text-success' : fulfillmentRate >= 50 ? 'text-warning' : 'text-danger'}}">
                                        <strong>${{fulfillmentRate}}%</strong>
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td>사유:</td>
                                <td class="text-end"><small>${{employee.reason}}</small></td>
                            </tr>
                        </table>
                    </div>
                </div>
            `;
            
            // Version 4: 조건 충족 현황 - 실제 값 표시 (3-4-2 구조)
            let conditionsHtml = '';
            
            if (employee.conditions) {{
                // 조건을 카테고리별로 그룹핑
                const groupedConditions = {{
                    attendance: [],
                    aql: [],
                    '5prs': []
                }};
                
                Object.entries(employee.conditions).forEach(([key, value]) => {{
                    if (value.category) {{
                        groupedConditions[value.category].push({{key, ...value}});
                    }}
                }});
                
                // 출근 조건 섹션 (3가지)
                if (groupedConditions.attendance.length > 0) {{
                    conditionsHtml += `
                        <div class="condition-section">
                            <div class="condition-section-header attendance">
                                📅 출근 조건 (3가지)
                            </div>
                            <div class="condition-section-body">
                    `;
                    
                    groupedConditions.attendance.forEach(condition => {{
                        conditionsHtml += renderCondition(condition);
                    }});
                    
                    conditionsHtml += `
                            </div>
                        </div>
                    `;
                }}
                
                // AQL 조건 섹션 (4가지)
                if (groupedConditions.aql.length > 0) {{
                    conditionsHtml += `
                        <div class="condition-section">
                            <div class="condition-section-header aql">
                                🎯 AQL 조건 (4가지)
                            </div>
                            <div class="condition-section-body">
                    `;
                    
                    groupedConditions.aql.forEach(condition => {{
                        conditionsHtml += renderCondition(condition);
                    }});
                    
                    conditionsHtml += `
                            </div>
                        </div>
                    `;
                }}
                
                // 5PRS 조건 섹션 (2가지)
                if (groupedConditions['5prs'].length > 0) {{
                    conditionsHtml += `
                        <div class="condition-section">
                            <div class="condition-section-header prs">
                                📊 5PRS 조건 (2가지)
                            </div>
                            <div class="condition-section-body">
                    `;
                    
                    groupedConditions['5prs'].forEach(condition => {{
                        conditionsHtml += renderCondition(condition);
                    }});
                    
                    conditionsHtml += `
                            </div>
                        </div>
                    `;
                }}
            }}
            
            document.getElementById('employeeConditions').innerHTML = conditionsHtml || 
                '<p class="text-muted p-3">조건 정보 없음</p>';
            
            modal.show();
        }}
        
        // 조건 렌더링 헬퍼 함수
        function renderCondition(condition) {{
            
            if (condition.applicable === false) {{
                return `
                    <div class="condition-check not-applicable">
                        <div>
                            <span class="condition-icon">➖</span>
                            <strong>${{translateConditionName(condition.name)}}</strong>
                        </div>
                        <div class="condition-value">
                            ${{t.notApplicable}}
                        </div>
                    </div>
                `;
            }} else {{
                const statusClass = condition.passed ? 'success' : 'fail';
                const statusIcon = condition.passed ? '✅' : '❌';
                let displayValue = translateConditionValue(condition.value);
                let actualValueHtml = '';
                
                // Version 4: 실제 값 표시 - 개선된 버전
                if (condition.actual) {{
                    const actualClass = condition.passed ? 'actual-success' : 'actual-fail';
                    actualValueHtml = `
                        <div class="actual-value-container">
                            <span class="actual-label">${{t.actualValue}}:</span>
                            <span class="actual-value ${{actualClass}}">${{condition.actual}}</span>
                        </div>`;
                }}
                
                return `
                    <div class="condition-check ${{statusClass}}">
                        <div>
                            <span class="condition-icon">${{statusIcon}}</span>
                            <strong>${{translateConditionName(condition.name)}}</strong>
                        </div>
                        <div class="condition-value">
                            <strong>${{displayValue}}</strong>
                            <br>
                            <small class="text-muted">(${{t.threshold}}: ${{translateThreshold(condition.threshold)}})</small>
                            ${{actualValueHtml}}
                        </div>
                    </div>
                `;
            }}
        }}
        
        // 직급별 팝업 내 테이블 필터링 함수
        function filterPositionTable(filter) {{
            const table = document.getElementById('positionEmployeeTable');
            if (!table) return;
            
            const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            
            for (let row of rows) {{
                const paymentStatus = row.getAttribute('data-payment');
                
                if (filter === 'all') {{
                    row.style.display = '';
                }} else if (filter === 'paid' && paymentStatus === 'paid') {{
                    row.style.display = '';
                }} else if (filter === 'unpaid' && paymentStatus === 'unpaid') {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }}
        }}
        
        // 필터 함수들
        function updatePositionFilter() {{
            const typeFilter = document.getElementById('typeFilter').value;
            const positionSelect = document.getElementById('positionFilter');
            
            // 기존 옵션 초기화
            positionSelect.innerHTML = '<option value="">모든 직급</option>';
            
            // 직급 목록 수집
            const positions = new Set();
            employeeData.forEach(emp => {{
                if (!typeFilter || emp.type === typeFilter) {{
                    positions.add(emp.position);
                }}
            }});
            
            // 옵션 추가
            Array.from(positions).sort().forEach(position => {{
                const option = document.createElement('option');
                option.value = position;
                option.textContent = position;
                positionSelect.appendChild(option);
            }});
        }}
        
        function filterTable() {{
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const positionFilter = document.getElementById('positionFilter').value;
            const paymentFilter = document.getElementById('paymentFilter').value;
            
            const tbody = document.getElementById('detailTableBody');
            const rows = tbody.getElementsByTagName('tr');
            
            for (let row of rows) {{
                const empNo = row.cells[0].textContent.toLowerCase();
                const name = row.cells[1].textContent.toLowerCase();
                const position = row.cells[2].textContent;
                const type = row.cells[3].textContent;
                const paymentAmount = row.cells[6].textContent;
                
                // 지급/미지급 판단 수정 (7월 인센티브가 0보다 크면 지급)
                const julyAmount = parseFloat(row.cells[5].querySelector('strong').textContent.replace(/[^0-9]/g, '')) || 0;
                const isPaid = julyAmount > 0;
                
                const matchSearch = empNo.includes(searchInput) || name.includes(searchInput);
                const matchType = !typeFilter || type.includes(typeFilter);
                const matchPosition = !positionFilter || position === positionFilter;
                const matchPayment = !paymentFilter || 
                    (paymentFilter === 'paid' && isPaid) ||
                    (paymentFilter === 'unpaid' && !isPaid);
                
                row.style.display = (matchSearch && matchType && matchPosition && matchPayment) ? '' : 'none';
            }}
        }}
        
        function clearFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('typeFilter').value = '';
            document.getElementById('positionFilter').value = '';
            document.getElementById('paymentFilter').value = '';
            updatePositionFilter();
            filterTable();
        }}
        
        // 유틸리티 함수들
        function analyzeConditions(employees, type, position) {{
            const conditions = {{
                '출근율 ≥88%': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '무단결근 ≤2일': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '실제 근무일 >0일': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '개인 AQL: 당월 실패 0건': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '연속성 체크: 3개월 연속 실패 없음': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '팀/구역 AQL: 부하직원 3개월 연속 실패자 없음': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '담당구역 reject율 <3%': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '5PRS 통과율 ≥95%': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                '5PRS 검사량 ≥100개': {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }}
            }};
            
            // 관리자급 직급 확인 - AUDIT & TRAINING TEAM, MODEL MASTER 추가
            const managerPositions = [
                'SUPERVISOR', '(V) SUPERVISOR', '(VICE) SUPERVISOR', 'V.SUPERVISOR',
                'MANAGER', 'A.MANAGER', 'ASSISTANT MANAGER', 'SENIOR MANAGER',
                'GROUP LEADER'
            ];
            const isManager = managerPositions.some(pos => position.toUpperCase().includes(pos));
            
            // 타입별/직급별 조건 적용 여부 결정 (정확한 규칙 적용)
            if (type === 'TYPE-2') {{
                // TYPE-2는 출근 조건만 적용 (3개)
                conditions['개인 AQL: 당월 실패 0건'].applicable = false;
                conditions['연속성 체크: 3개월 연속 실패 없음'].applicable = false;
                conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].applicable = false;
                conditions['담당구역 reject율 <3%'].applicable = false;
                conditions['5PRS 통과율 ≥95%'].applicable = false;
                conditions['5PRS 검사량 ≥100개'].applicable = false;
            }}
            // TYPE-1 직급별 차별화
            else if (type === 'TYPE-1') {{
                // ASSEMBLY INSPECTOR - 7개 (출근 3 + 개인AQL 2 + 5PRS 2)
                if (position.toUpperCase().includes('ASSEMBLY INSPECTOR')) {{
                    conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].applicable = false;
                    conditions['담당구역 reject율 <3%'].applicable = false;
                }}
                // AQL INSPECTOR - 4개 (출근 3 + 개인AQL 당월만 1)
                else if (position.toUpperCase().includes('AQL INSPECTOR')) {{
                    conditions['연속성 체크: 3개월 연속 실패 없음'].applicable = false;
                    conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].applicable = false;
                    conditions['담당구역 reject율 <3%'].applicable = false;
                    conditions['5PRS 통과율 ≥95%'].applicable = false;
                    conditions['5PRS 검사량 ≥100개'].applicable = false;
                }}
                // 관리자급 - 출근 조건만 (3개)
                else if (isManager) {{
                    conditions['개인 AQL: 당월 실패 0건'].applicable = false;
                    conditions['연속성 체크: 3개월 연속 실패 없음'].applicable = false;
                    conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].applicable = false;
                    conditions['담당구역 reject율 <3%'].applicable = false;
                    conditions['5PRS 통과율 ≥95%'].applicable = false;
                    conditions['5PRS 검사량 ≥100개'].applicable = false;
                }}
                // LINE LEADER - 4개 (출근 3 + 팀AQL 1)
                else if (position.toUpperCase().includes('LINE LEADER')) {{
                    conditions['개인 AQL: 당월 실패 0건'].applicable = false;
                    conditions['연속성 체크: 3개월 연속 실패 없음'].applicable = false;
                    conditions['담당구역 reject율 <3%'].applicable = false;
                    conditions['5PRS 통과율 ≥95%'].applicable = false;
                    conditions['5PRS 검사량 ≥100개'].applicable = false;
                }}
                // AUDIT & TRAINING TEAM - 5개 (출근 3 + 팀AQL 1 + reject율 1)
                else if (position.toUpperCase().includes('AUDIT') || position.toUpperCase().includes('TRAINING')) {{
                    conditions['개인 AQL: 당월 실패 0건'].applicable = false;
                    conditions['연속성 체크: 3개월 연속 실패 없음'].applicable = false;
                    conditions['5PRS 통과율 ≥95%'].applicable = false;
                    conditions['5PRS 검사량 ≥100개'].applicable = false;
                }}
                // MODEL MASTER - 4개 (출근 3 + reject율 1)
                else if (position.toUpperCase().includes('MODEL MASTER')) {{
                    conditions['개인 AQL: 당월 실패 0건'].applicable = false;
                    conditions['연속성 체크: 3개월 연속 실패 없음'].applicable = false;
                    conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].applicable = false;
                    conditions['5PRS 통과율 ≥95%'].applicable = false;
                    conditions['5PRS 검사량 ≥100개'].applicable = false;
                }}
            }}
            
            // 디버깅용 로그
            console.log(`analyzeConditions - type: ${{type}}, position: ${{position}}, employees: ${{employees.length}}`);
            if (employees.length > 0) {{
                console.log('First employee:', employees[0]);
                console.log('First employee conditions:', employees[0]?.conditions);
                if (employees[0]?.conditions) {{
                    console.log('Conditions keys:', Object.keys(employees[0].conditions));
                }}
            }}
            
            employees.forEach(emp => {{
                // 모든 직원을 먼저 카운트 (조건이 없어도)
                if (!emp.conditions) {{
                    console.log('Employee without conditions:', emp.emp_no);
                    // 조건이 없으면 기본적으로 평가 대상으로 카운트하고 failed로 처리
                    Object.keys(conditions).forEach(key => {{
                        if (conditions[key].applicable) {{
                            conditions[key].failed++;
                        }} else {{
                            conditions[key].notApplicable++;
                        }}
                    }});
                }} else {{
                    // 1. 출근율
                    if (conditions['출근율 ≥88%'].applicable) {{
                        if (emp.conditions.attendance_rate) {{
                            if (emp.conditions.attendance_rate.applicable === false) {{
                                conditions['출근율 ≥88%'].notApplicable++;
                            }} else if (emp.conditions.attendance_rate.passed) {{
                                conditions['출근율 ≥88%'].passed++;
                            }} else {{
                                conditions['출근율 ≥88%'].failed++;
                            }}
                        }} else {{
                            // 조건 데이터가 없으면 failed로 처리
                            conditions['출근율 ≥88%'].failed++;
                        }}
                    }} else {{
                        conditions['출근율 ≥88%'].notApplicable++;
                    }}
                    // 2. 무단결근
                    if (conditions['무단결근 ≤2일'].applicable) {{
                        if (emp.conditions.absence_days) {{
                            if (emp.conditions.absence_days.applicable === false) {{
                                conditions['무단결근 ≤2일'].notApplicable++;
                            }} else if (emp.conditions.absence_days.passed) {{
                                conditions['무단결근 ≤2일'].passed++;
                            }} else {{
                                conditions['무단결근 ≤2일'].failed++;
                            }}
                        }} else {{
                            conditions['무단결근 ≤2일'].failed++;
                        }}
                    }} else {{
                        conditions['무단결근 ≤2일'].notApplicable++;
                    }}
                    // 3. 실제 근무일 (working_days)
                    if (conditions['실제 근무일 >0일'].applicable) {{
                        if (emp.conditions.working_days) {{
                            if (emp.conditions.working_days.applicable === false) {{
                                conditions['실제 근무일 >0일'].notApplicable++;
                            }} else if (emp.conditions.working_days.passed) {{
                                conditions['실제 근무일 >0일'].passed++;
                            }} else {{
                                conditions['실제 근무일 >0일'].failed++;
                            }}
                        }} else {{
                            conditions['실제 근무일 >0일'].failed++;
                        }}
                    }} else {{
                        conditions['실제 근무일 >0일'].notApplicable++;
                    }}
                    // 4. 개인 AQL (aql_monthly)
                    if (conditions['개인 AQL: 당월 실패 0건'].applicable) {{
                        if (emp.conditions.aql_monthly) {{
                            if (emp.conditions.aql_monthly.applicable === false) {{
                                conditions['개인 AQL: 당월 실패 0건'].notApplicable++;
                            }} else if (emp.conditions.aql_monthly.passed) {{
                                conditions['개인 AQL: 당월 실패 0건'].passed++;
                            }} else {{
                                conditions['개인 AQL: 당월 실패 0건'].failed++;
                            }}
                        }} else {{
                            conditions['개인 AQL: 당월 실패 0건'].failed++;
                        }}
                    }} else {{
                        conditions['개인 AQL: 당월 실패 0건'].notApplicable++;
                    }}
                    // 5. 3개월 연속 실패 없음 (aql_3month)
                    if (conditions['연속성 체크: 3개월 연속 실패 없음'].applicable) {{
                        if (emp.conditions.aql_3month) {{
                            if (emp.conditions.aql_3month.applicable === false) {{
                                conditions['연속성 체크: 3개월 연속 실패 없음'].notApplicable++;
                            }} else if (emp.conditions.aql_3month.passed) {{
                                conditions['연속성 체크: 3개월 연속 실패 없음'].passed++;
                            }} else {{
                                conditions['연속성 체크: 3개월 연속 실패 없음'].failed++;
                            }}
                        }} else {{
                            conditions['연속성 체크: 3개월 연속 실패 없음'].failed++;
                        }}
                    }} else {{
                        conditions['연속성 체크: 3개월 연속 실패 없음'].notApplicable++;
                    }}
                    // 6. 부하직원 AQL (subordinate_aql)
                    if (conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].applicable) {{
                        if (emp.conditions.subordinate_aql) {{
                            if (emp.conditions.subordinate_aql.applicable === false) {{
                                conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].notApplicable++;
                            }} else if (emp.conditions.subordinate_aql.passed) {{
                                conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].passed++;
                            }} else {{
                                conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].failed++;
                            }}
                        }} else {{
                            conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].failed++;
                        }}
                    }} else {{
                        conditions['팀/구역 AQL: 부하직원 3개월 연속 실패자 없음'].notApplicable++;
                    }}
                    // 7. 담당구역 reject율 (area_reject_rate)
                    if (conditions['담당구역 reject율 <3%'].applicable) {{
                        if (emp.conditions.area_reject_rate) {{
                            if (emp.conditions.area_reject_rate.applicable === false) {{
                                conditions['담당구역 reject율 <3%'].notApplicable++;
                            }} else if (emp.conditions.area_reject_rate.passed) {{
                                conditions['담당구역 reject율 <3%'].passed++;
                            }} else {{
                                conditions['담당구역 reject율 <3%'].failed++;
                            }}
                        }} else {{
                            conditions['담당구역 reject율 <3%'].failed++;
                        }}
                    }} else {{
                        conditions['담당구역 reject율 <3%'].notApplicable++;
                    }}
                    // 8. 5PRS 통과율 (5prs_pass_rate)
                    if (conditions['5PRS 통과율 ≥95%'].applicable) {{
                        if (emp.conditions['5prs_pass_rate']) {{
                            if (emp.conditions['5prs_pass_rate'].applicable === false) {{
                                conditions['5PRS 통과율 ≥95%'].notApplicable++;
                            }} else if (emp.conditions['5prs_pass_rate'].passed) {{
                                conditions['5PRS 통과율 ≥95%'].passed++;
                            }} else {{
                                conditions['5PRS 통과율 ≥95%'].failed++;
                            }}
                        }} else {{
                            conditions['5PRS 통과율 ≥95%'].failed++;
                        }}
                    }} else {{
                        conditions['5PRS 통과율 ≥95%'].notApplicable++;
                    }}
                    // 9. 5PRS 검사량 (5prs_volume)
                    if (conditions['5PRS 검사량 ≥100개'].applicable) {{
                        if (emp.conditions['5prs_volume']) {{
                            if (emp.conditions['5prs_volume'].applicable === false) {{
                                conditions['5PRS 검사량 ≥100개'].notApplicable++;
                            }} else if (emp.conditions['5prs_volume'].passed) {{
                                conditions['5PRS 검사량 ≥100개'].passed++;
                            }} else {{
                                conditions['5PRS 검사량 ≥100개'].failed++;
                            }}
                        }} else {{
                            conditions['5PRS 검사량 ≥100개'].failed++;
                        }}
                    }} else {{
                        conditions['5PRS 검사량 ≥100개'].notApplicable++;
                    }}
                }}
            }});
            
            // 디버깅용 로그
            console.log('Condition results:', conditions);
            
            // 충족률 계산 (평가 대상자 기준)
            Object.keys(conditions).forEach(key => {{
                const applicable = conditions[key].passed + conditions[key].failed;
                conditions[key].rate = applicable > 0 ? (conditions[key].passed / applicable * 100) : 0;
            }});
            
            return conditions;
        }}
        
        function calculatePositionStats(employees) {{
            let totalAmount = 0;
            let paidCount = 0;
            
            employees.forEach(emp => {{
                const amount = parseFloat(emp.july_incentive.replace(/[^0-9]/g, '')) || 0;
                if (amount > 0) {{
                    totalAmount += amount;
                    paidCount++;
                }}
            }});
            
            // 평균 지급액 (소수점 제거)
            const avgPaid = paidCount > 0 ? Math.round(totalAmount / paidCount).toLocaleString() + ' VND' : '0 VND';
            const avgTotal = employees.length > 0 ? Math.round(totalAmount / employees.length).toLocaleString() + ' VND' : '0 VND';
            
            return {{ avgPaid, avgTotal }};
        }}
        
        // 요약 탭 데이터 생성
        function generateSummaryData() {{
            const typeSummary = {{}};
            
            // Type별 데이터 집계
            employeeData.forEach(emp => {{
                const type = emp.type;
                if (!typeSummary[type]) {{
                    typeSummary[type] = {{
                        total: 0,
                        paid: 0,
                        totalAmount: 0
                    }};
                }}
                
                typeSummary[type].total++;
                const amount = parseFloat(emp.july_incentive.replace(/[^0-9]/g, '')) || 0;
                if (amount > 0) {{
                    typeSummary[type].paid++;
                    typeSummary[type].totalAmount += amount;
                }}
            }});
            
            // 테이블 생성
            const tbody = document.getElementById('typeSummaryBody');
            if (tbody) {{
                tbody.innerHTML = '';
                
                Object.entries(typeSummary).sort().forEach(([type, data]) => {{
                    const paymentRate = (data.paid / data.total * 100).toFixed(1);
                    // 평균 지급액 (소수점 제거)
                    const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid).toLocaleString() : '0';
                    const avgTotal = data.total > 0 ? Math.round(data.totalAmount / data.total).toLocaleString() : '0';
                    
                    tbody.innerHTML += `
                        <tr>
                            <td><span class="type-badge type-${{type.slice(-1).toLowerCase()}}">${{type}}</span></td>
                            <td>${{data.total}}명</td>
                            <td>${{data.paid}}명</td>
                            <td>${{paymentRate}}%</td>
                            <td>${{data.totalAmount.toLocaleString()}} VND</td>
                            <td>${{avgPaid}} VND</td>
                            <td>${{avgTotal}} VND</td>
                        </tr>
                    `;
                }});
            }}
        }}
        
        // 직급별 상세 탭 데이터 생성
        function generatePositionData() {{
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
                const amount = parseFloat(emp.july_incentive.replace(/[^0-9]/g, '')) || 0;
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
                
                Object.entries(groupedByType).sort().forEach(([type, positions]) => {{
                    const typeClass = `type-${{type.slice(-1).toLowerCase()}}`;
                    
                    let html = `
                        <div class="mb-4">
                            <h4><span class="type-badge ${{typeClass}}">${{type}}</span> 직급별 현황</h4>
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>직급</th>
                                        <th>전체 인원</th>
                                        <th>수령 인원</th>
                                        <th>수령률</th>
                                        <th>총 지급액</th>
                                        <th>수령인원 기준<br>평균 지급액</th>
                                        <th>총원 기준<br>평균 지급액</th>
                                        <th>상세</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    positions.sort((a, b) => a.position.localeCompare(b.position)).forEach(pos => {{
                        const paymentRate = (pos.paid / pos.total * 100).toFixed(1);
                        // 평균 지급액 (소수점 제거)
                        const avgPaid = pos.paid > 0 ? Math.round(pos.totalAmount / pos.paid).toLocaleString() : '0';
                        const avgTotal = pos.total > 0 ? Math.round(pos.totalAmount / pos.total).toLocaleString() : '0';
                        
                        html += `
                            <tr>
                                <td>${{pos.position}}</td>
                                <td>${{pos.total}}명</td>
                                <td>${{pos.paid}}명</td>
                                <td>${{paymentRate}}%</td>
                                <td>${{pos.totalAmount.toLocaleString()}} VND</td>
                                <td>${{avgPaid}} VND</td>
                                <td>${{avgTotal}} VND</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" 
                                        onclick="showPositionDetail('${{type}}', '${{pos.position}}')"
                                        style="padding: 2px 8px; font-size: 0.85em;">
                                        📈 ${{t.detailView}}
                                    </button>
                                </td>
                            </tr>
                        `;
                    }});
                    
                    html += `
                                </tbody>
                            </table>
                        </div>
                    `;
                    
                    container.innerHTML += html;
                }});
            }}
        }}
        
        // 페이지 로드 시 초기화
        window.onload = function() {{
            updatePositionFilter();
            generateSummaryData();
            generatePositionData();
            showTab('summary');
            
            // 언어 선택 이벤트 리스너
            document.getElementById('languageSelector').addEventListener('change', function(e) {{
                changeLanguage(e.target.value);
            }});
        }};
    </script>
</body>
</html>"""
    
    # HTML 파일 저장
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 개선된 대시보드 Version 4가 성공적으로 생성되었습니다!")
    print(f"📁 파일 경로: {output_html}")
    print(f"📊 처리된 직원 수: {len(employees)}명")
    print(f"💰 총 지급액: {format_currency(stats['total_amount'])}")
    print(f"📈 지급률: {stats['payment_rate']:.1f}%")
    print(f"🎯 주요 개선사항: 팝업창 조건 3-4-2 구조로 세분화")

def calculate_statistics(employees, calculation_month=None, exclude_types=None):
    """통계 계산
    
    Args:
        employees: 직원 데이터 리스트
        calculation_month: 인센티브 계산 기준 월 (예: '2025-07')
                          None인 경우 모든 직원 포함
        exclude_types: 제외할 TYPE 리스트 (예: ['TYPE-3'])
    """
    import pandas as pd
    
    # Stop working Date 기준으로 필터링
    active_employees = []
    
    if calculation_month == '2025-07':
        # 7월 기준: 2025년 7월 1일 이전 퇴사자 제외
        calc_month_start = pd.Timestamp(2025, 7, 1)
        
        for emp in employees:
            stop_date = emp.get('stop_working_date')
            
            # Stop working Date가 없거나 7월 1일 이후인 경우 포함
            if stop_date is None or stop_date >= calc_month_start:
                active_employees.append(emp)
    else:
        # 기본: 모든 직원 포함
        active_employees = employees
    
    # TYPE 필터링은 기본적으로 하지 않음 (원본과 동일하게)
    # QIP 원본은 TYPE-3도 전체 직원 수에 포함
    if exclude_types:
        active_employees = [emp for emp in active_employees 
                           if emp.get('type') not in exclude_types]
    
    total = len(active_employees)
    paid = sum(1 for emp in active_employees if not emp['july_incentive'].startswith('0 VND'))
    
    total_amount = 0
    for emp in active_employees:
        amount_str = emp['july_incentive'].replace(' VND', '').replace(',', '')
        try:
            amount = float(amount_str)
            total_amount += amount
        except:
            pass
    
    return {
        'total_employees': total,
        'paid_employees': paid,
        'payment_rate': (paid / total * 100) if total > 0 else 0,
        'total_amount': total_amount
    }

def format_currency(amount):
    """통화 포맷"""
    return f"{amount:,.0f} VND"

def generate_summary_tab(stats):
    """요약 탭 HTML 생성"""
    return """
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
            <tbody id="typeSummaryBody">
            </tbody>
        </table>
    """

def generate_position_tab(employees):
    """직급별 상세 탭 HTML 생성"""
    return """
        <h3 id="positionTabTitle">직급별 상세 현황</h3>
        <div id="positionTables">
            <!-- JavaScript로 채워질 예정 -->
        </div>
    """

def generate_detail_tab(employees):
    """개인별 상세 탭 HTML 생성"""
    html = """
        <h3>개인별 상세 정보</h3>
        <div class="filter-container">
            <div class="row">
                <div class="col-md-3">
                    <input type="text" id="searchInput" class="form-control" 
                        placeholder="이름 또는 직원번호 검색" onkeyup="filterTable()">
                </div>
                <div class="col-md-2">
                    <select id="typeFilter" class="form-select" 
                        onchange="updatePositionFilter(); filterTable()">
                        <option value="">모든 타입</option>
                        <option value="TYPE-1">TYPE-1</option>
                        <option value="TYPE-2">TYPE-2</option>
                        <option value="TYPE-3">TYPE-3</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select id="positionFilter" class="form-select" onchange="filterTable()">
                        <option value="">모든 직급</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <select id="paymentFilter" class="form-select" onchange="filterTable()">
                        <option value="">전체</option>
                        <option value="paid">지급</option>
                        <option value="unpaid">미지급</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-secondary w-100" onclick="clearFilters()">
                        필터 초기화
                    </button>
                </div>
            </div>
        </div>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>직원번호</th>
                        <th>이름</th>
                        <th>직급</th>
                        <th>Type</th>
                        <th>6월 인센티브</th>
                        <th>7월 인센티브</th>
                        <th>증감</th>
                        <th>계산 근거</th>
                    </tr>
                </thead>
                <tbody id="detailTableBody">
    """
    
    # 직원 데이터 추가
    for emp in employees:
        type_class = f"type-{emp['type'][-1].lower()}"
        html += f"""
            <tr onclick="showEmployeeDetail('{emp['emp_no']}')" style="cursor: pointer;">
                <td>{emp['emp_no']}</td>
                <td>{emp['name']}</td>
                <td>{emp['position']}</td>
                <td><span class="type-badge {type_class}">{emp['type']}</span></td>
                <td>{emp['june_incentive']}</td>
                <td><strong>{emp['july_incentive']}</strong></td>
                <td>{emp['change']}</td>
                <td>{emp['reason']}</td>
            </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    """
    return html

def generate_criteria_tab():
    """인센티브 기준 탭 HTML 생성 - dashboard_version2.html과 동일"""
    # criteria_content.html 파일 읽기
    criteria_file = Path(__file__).parent / "criteria_content.html"
    if criteria_file.exists():
        with open(criteria_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # 파일이 없으면 기본 내용 반환
    return """
        <h2 class="section-title">인센티브 기준</h2>
        <p>인센티브 기준 내용을 로드할 수 없습니다.</p>
    """

# 메인 실행
if __name__ == "__main__":
    # 커맨드 라인 인자 처리
    parser = argparse.ArgumentParser(description='Generate QIP Incentive Dashboard')
    parser.add_argument('--month', type=str, default='july', 
                       help='Month name (e.g., july, august)')
    parser.add_argument('--year', type=int, default=2025,
                       help='Year (e.g., 2025)')
    
    args = parser.parse_args()
    
    # 현재 스크립트의 디렉토리 경로
    base_dir = Path(__file__).parent
    
    # 프로젝트 루트 디렉토리 (dashboard_version3 폴더의 상위 폴더)
    root_dir = base_dir.parent
    
    # 1. dashboard_version3 폴더 내 output_files 폴더
    local_output_dir = base_dir / "output_files"
    local_output_dir.mkdir(exist_ok=True)
    
    # 2. 루트 디렉토리의 output_files 폴더
    root_output_dir = root_dir / "output_files"
    root_output_dir.mkdir(exist_ok=True)
    
    # 입력 파일 경로 설정 (동적으로 월/년도 기반)
    month_map = {
        'january': 'January', 'february': 'February', 'march': 'March',
        'april': 'April', 'may': 'May', 'june': 'June',
        'july': 'July', 'august': 'August', 'september': 'September',
        'october': 'October', 'november': 'November', 'december': 'December'
    }
    month_title = month_map.get(args.month.lower(), 'July')
    input_file = root_output_dir / f"QIP_Incentive_Report_{month_title}_{args.year}.html"
    
    # 파일 존재 확인 - HTML 파일이 없어도 CSV 파일로 진행 가능
    if not input_file.exists():
        print(f"⚠️ HTML 파일이 없습니다: {input_file}")
        print("CSV 파일에서 직접 데이터를 읽어 진행합니다.")
        # CSV 파일 확인
        csv_pattern = f"output_QIP_incentive_{args.month}_{args.year}_*Complete.csv"
        csv_files = list(root_output_dir.glob(csv_pattern))
        if not csv_files:
            print(f"❌ CSV 파일도 찾을 수 없습니다: {csv_pattern}")
            print(f"먼저 step1_인센티브_계산_개선버전.py를 실행해주세요.")
            exit(1)
        print(f"✅ CSV 파일을 찾았습니다: {csv_files[0].name}")
    
    print(f"✅ 입력 파일 경로: {input_file}")
    
    # 두 위치에 모두 저장
    output_file_local = local_output_dir / "dashboard_version4.html"
    output_file_root = root_output_dir / "dashboard_version4.html"
    
    print(f"✅ 출력 파일 경로 1 (로컬): {output_file_local}")
    print(f"✅ 출력 파일 경로 2 (루트): {output_file_root}")
    
    # 먼저 로컬 폴더에 생성 (calculation_month 동적 생성)
    month_num = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }.get(args.month.lower(), '07')
    calculation_month = f'{args.year}-{month_num}'
    generate_improved_dashboard(str(input_file), str(output_file_local), 
                               calculation_month=calculation_month,
                               month=args.month, year=args.year)
    
    # 루트 폴더에도 복사
    import shutil
    shutil.copy2(str(output_file_local), str(output_file_root))
    print(f"✅ 루트 폴더에도 복사 완료: {output_file_root}")