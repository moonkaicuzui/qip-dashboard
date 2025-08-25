import re
from datetime import datetime
import json
import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Import the new condition matrix manager
try:
    from condition_matrix_manager import ConditionMatrixManager, get_condition_manager
except ImportError:
    print("Warning: Could not import ConditionMatrixManager. Using fallback logic.")
    ConditionMatrixManager = None

# Position condition matrix 로드
def load_position_condition_matrix():
    """position_condition_matrix.json 파일 로드"""
    try:
        config_path = Path(__file__).parent.parent / 'config_files' / 'position_condition_matrix.json'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                matrix = json.load(f)
                print("✅ Position condition matrix 로드 성공")
                return matrix
        else:
            print(f"⚠️ Position condition matrix 파일을 찾을 수 없습니다: {config_path}")
    except Exception as e:
        print(f"❌ Position condition matrix 로드 실패: {e}")
    return None

# 전역 변수로 matrix 로드
POSITION_CONDITION_MATRIX = load_position_condition_matrix()

def get_position_config_from_matrix(emp_type, position, matrix):
    """JSON matrix에서 해당 직급의 설정을 찾아 반환"""
    if not matrix:
        return None
        
    position_upper = position.upper()
    type_config = matrix.get('position_matrix', {}).get(emp_type, {})
    
    # 직급별 설정 찾기
    for pos_key, pos_config in type_config.items():
        if pos_key == 'default':
            continue
        patterns = pos_config.get('patterns', [])
        for pattern in patterns:
            if pattern in position_upper:
                return pos_config
    
    # 기본값 반환
    return type_config.get('default', {})

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

def load_calculation_metadata(month='july', year=2025):
    """계산 메타데이터 로드 (조건 충족 상세 정보 포함)"""
    try:
        metadata_path = Path(__file__).parent.parent / "output_files" / f"output_QIP_incentive_{month}_{year}_metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                print(f"✅ 메타데이터 로드 성공: {len(metadata)} 직원 정보")
                return metadata
        else:
            print(f"⚠️ 메타데이터 파일이 없습니다: {metadata_path}")
            return {}
    except Exception as e:
        print(f"Warning: Could not load metadata: {e}")
        return {}

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
    """기존 HTML 파일에서 데이터 추출 - Version 4 개선
    
    수정: HTML 파일이 없으면 CSV에서 직접 데이터 읽기
    """
    # HTML 파일이 없으면 CSV에서 직접 읽기
    if not Path(html_file_path).exists():
        print(f"ℹ️ HTML 파일이 없어 CSV에서 직접 데이터를 읽습니다.")
        return extract_data_from_csv(month, year)
    
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

def extract_data_from_csv(month='july', year=2025):
    """
    CSV 파일에서 직접 데이터 추출
    HTML 파싱 없이 CSV에서 직접 읽기
    """
    import pandas as pd
    from pathlib import Path
    
    # CSV 파일 경로
    csv_path = Path(__file__).parent.parent / "output_files" / f"output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
    
    print(f"✅ CSV 파일에서 데이터 로드: {csv_path.name}")
    
    # CSV 데이터 로드
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # AQL history 로드
    aql_history = load_aql_history(month)
    
    # 메타데이터 로드
    metadata = load_calculation_metadata(month, year)
    
    # CSV 데이터를 employees 형식으로 변환
    employees = []
    for idx, row in df.iterrows():
        # Type 값 처리 - 'ROLE TYPE STD' 컬럼에서 읽기
        type_value = row.get('ROLE TYPE STD', '')
        if pd.isna(type_value):
            type_value = ''
        else:
            type_value = str(type_value).strip()
            
        emp = {
            'emp_no': str(row.get('Employee No', '')),
            'name': row.get('Name_vi', row.get('Full Name', '')),
            'position': row.get('QIP POSITION 1ST  NAME', ''),
            'type': type_value,
            'june_incentive': str(row.get('June_Incentive', '0')),
            'july_incentive': str(row.get('July_Incentive', '0')),
            'august_incentive': str(row.get('August_Incentive', '0')),
            'change': '',  # CSV에서 계산
            'reason': row.get('Remarks', '')
        }
        
        # 인센티브 값 포맷팅
        current_month_col = f'{month.capitalize()}_Incentive'
        if current_month_col in df.columns:
            current_incentive = row.get(current_month_col, 0)
        else:
            # 월 이름 매핑
            current_incentive = row.get('August_Incentive', 0)
        
        # 조건 분석 - CSV 데이터 사용 (메타데이터 포함)
        # 메타데이터에서 조건 정보 우선 사용
        emp_metadata = metadata.get(str(emp['emp_no']), {})
        if emp_metadata and 'conditions' in emp_metadata:
            # 메타데이터의 조건 정보를 기존 형식으로 변환
            conditions_from_metadata = {}
            
            # 출근 조건
            if 'attendance' in emp_metadata['conditions']:
                att = emp_metadata['conditions']['attendance']
                for key, value in att.items():
                    if isinstance(value, dict):
                        conditions_from_metadata[key] = value
            
            # AQL 조건
            if 'aql' in emp_metadata['conditions']:
                aql = emp_metadata['conditions']['aql']
                if isinstance(aql, dict):
                    for key, value in aql.items():
                        if isinstance(value, dict):
                            # 키 이름 매핑
                            if key == 'monthly_failure':
                                conditions_from_metadata['aql_monthly'] = value
                            elif key == '3month_continuous':
                                conditions_from_metadata['aql_3month'] = value
                            else:
                                conditions_from_metadata[key] = value
            
            # 5PRS 조건
            if '5prs' in emp_metadata['conditions']:
                prs = emp_metadata['conditions']['5prs']
                if isinstance(prs, dict) and 'applicable' not in prs:
                    for key, value in prs.items():
                        if isinstance(value, dict):
                            conditions_from_metadata[f'5prs_{key}'] = value
            
            emp['conditions'] = conditions_from_metadata
            emp['metadata'] = emp_metadata
            emp['condition_summary'] = {}
        else:
            # 메타데이터가 없으면 기존 방식으로 분석
            analysis_result = analyze_conditions_from_csv_row(row, emp['type'], emp['position'], month)
            
            # 새로운 반환 형식 처리
            if isinstance(analysis_result, dict) and 'conditions' in analysis_result:
                emp['conditions'] = analysis_result['conditions']
                emp['metadata'] = analysis_result.get('metadata', {})
                emp['condition_summary'] = analysis_result.get('summary', {})
            else:
                # 이전 버전 호환성 (fallback)
                emp['conditions'] = analysis_result
                emp['metadata'] = {}
                emp['condition_summary'] = {}
        
        # Stop working Date 추가
        if pd.notna(row.get('Stop working Date')):
            emp['stop_working_date'] = pd.to_datetime(row.get('Stop working Date'))
            emp['stop_working_date_str'] = emp['stop_working_date'].strftime('%Y-%m-%d')
        else:
            emp['stop_working_date'] = None
            emp['stop_working_date_str'] = None
        
        employees.append(emp)
    
    print(f"✅ {len(employees)}명의 직원 데이터 로드 완료")
    return employees

def _get_condition_key(condition_id):
    """조건 ID를 기존 키로 매핑"""
    mapping = {
        1: 'working_days',
        2: 'absence_days', 
        3: 'attendance_rate',
        4: 'minimum_working_days',
        5: 'aql_current',
        6: 'aql_continuous',
        7: 'subordinate_aql',  # Team/Area AQL - was incorrectly '5prs_validation_qty'
        8: 'area_reject_rate',  # Area Reject Rate - was incorrectly '5prs_pass_rate'
        9: '5prs_volume',  # 5PRS Inspection Quantity
        10: '5prs_pass_rate'  # 5PRS Pass Rate
    }
    return mapping.get(condition_id)

def analyze_conditions_from_csv_row(row, emp_type, position='', month='august', language='ko'):
    """
    CSV row에서 직접 조건 분석 - 100% JSON 매트릭스 기반 (폴백 없음)
    
    Returns:
        {
            'conditions': evaluation results,
            'metadata': UI metadata for dynamic rendering
        }
    """
    if not ConditionMatrixManager:
        raise ImportError("ConditionMatrixManager is required for condition analysis")
    
    manager = get_condition_manager()
    
    # 직원 데이터를 딕셔너리로 변환
    employee_data = row.to_dict() if hasattr(row, 'to_dict') else row
    
    # 데이터 전처리 (TYPE-1 STITCHING INSPECTOR 수정 등)
    employee_data = manager.preprocess_employee_data(employee_data)
    
    # 수정된 타입과 직급 가져오기
    corrected_type = employee_data.get('ROLE TYPE STD', emp_type)
    corrected_position = employee_data.get('QIP POSITION 1ST NAME', position)
    
    # 매트릭스 기반 조건 평가
    evaluation_result = manager.evaluate_all_conditions(employee_data, corrected_type, corrected_position)
    
    # UI 메타데이터 생성
    ui_metadata = manager.get_ui_metadata(corrected_type, corrected_position, language)
    
    # 결과를 기존 형식으로 변환
    conditions = {}
    for result in evaluation_result.get('all_results', []):
        condition_key = _get_condition_key(result.condition_id)
        if condition_key:
            conditions[condition_key] = {
                'passed': result.is_passed if result.is_applicable else None,
                'value': result.actual_value,
                'threshold': result.threshold_value,
                'actual': result.message,
                'applicable': result.is_applicable,
                'category': _get_condition_category(result.condition_id),
                'name': manager.get_condition_info(result.condition_id).get('name', '')
            }
    
    return {
        'conditions': conditions,
        'metadata': ui_metadata,
        'summary': evaluation_result.get('summary', {})
    }

def _get_condition_category(condition_id):
    """Get category for a condition ID"""
    if condition_id in [1, 2, 3, 4]:
        return 'attendance'
    elif condition_id in [5, 6, 7, 8]:
        return 'aql'
    elif condition_id in [9, 10]:
        return '5prs'
    return 'unknown'

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
        # emp_no를 정수로 변환하여 비교 (CSV의 Employee No는 정수형)
        try:
            emp_no_int = int(emp_no)
            emp_row = csv_data[csv_data['Employee No'] == emp_no_int]
        except (ValueError, TypeError):
            emp_row = csv_data[csv_data['Employee No'] == emp_no]
        
        if not emp_row.empty:
            emp_row = emp_row.iloc[0]
            actual_data = {
                'attendance_rate': 100 - emp_row.get('Absence Rate (raw)', 0) if pd.notna(emp_row.get('Absence Rate (raw)')) else None,
                'unapproved_absences': emp_row.get('Unapproved Absence Days', 0) if pd.notna(emp_row.get('Unapproved Absence Days')) else 0,
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
        'MANAGER', 'A.MANAGER', 'ASSISTANT MANAGER', 'SENIOR MANAGER'
        # GROUP LEADER는 별도 처리
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
        conditions['minimum_working_days'] = {
            'name': '최소 근무일 ≥12일',
            'category': 'attendance',
            'passed': True,
            'value': '정상',
            'actual': None,
            'threshold': '12일 이상',
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
        
        # JSON matrix 기반 조건 적용
        if POSITION_CONDITION_MATRIX:
            pos_config = get_position_config_from_matrix(emp_type, position, POSITION_CONDITION_MATRIX)
            if pos_config:
                applicable_conditions = pos_config.get('applicable_conditions', [])
                excluded_conditions = pos_config.get('excluded_conditions', [])
                
                # 조건 ID와 실제 조건 매핑
                condition_mapping = {
                    5: 'aql_monthly',      # 개인 AQL: 당월 실패
                    6: 'aql_3month',       # 개인 AQL: 3개월 연속
                    7: 'subordinate_aql',  # 팀/구역 AQL
                    8: 'area_reject_rate', # 담당구역 reject율
                    9: '5prs_volume',      # 5PRS 검사량
                    10: '5prs_pass_rate'   # 5PRS 통과율
                }
                
                # 제외된 조건들을 N/A로 설정
                for cond_id in excluded_conditions:
                    if cond_id in condition_mapping:
                        cond_key = condition_mapping[cond_id]
                        if cond_key in conditions:
                            conditions[cond_key]['applicable'] = False
                            conditions[cond_key]['value'] = 'N/A'
                
                # 적용되는 조건들을 활성화
                for cond_id in applicable_conditions:
                    if cond_id in condition_mapping:
                        cond_key = condition_mapping[cond_id]
                        if cond_key in conditions:
                            conditions[cond_key]['applicable'] = True
                            
                print(f"  📋 {position} - JSON 기반 조건 적용: {applicable_conditions}, 제외: {excluded_conditions}")
        else:
            # 폴백: 기존 하드코딩 로직 (JSON 로드 실패 시)
            print(f"  ⚠️ {position} - 폴백 로직 사용 (JSON 미사용)")
            # ASSEMBLY INSPECTOR - 개인 AQL(당월+3개월)과 5PRS 적용 (부하직원/구역 미적용)
            if 'ASSEMBLY INSPECTOR' in position:
                # 5번 조건 (당월 AQL)과 6번 조건 (3개월 연속 체크) 모두 적용
                conditions['aql_monthly']['applicable'] = True  # 5번 조건 - 명시적 설정
                conditions['aql_3month']['applicable'] = True   # 6번 조건 - 이전에 누락되었던 부분
                # 7번, 8번 조건은 미적용
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
                
            # GROUP LEADER - 출근 조건만 적용 (부하직원 AQL 제외)
            elif 'GROUP LEADER' in position:
                conditions['aql_monthly']['applicable'] = False
                conditions['aql_monthly']['value'] = 'N/A'
                conditions['aql_3month']['applicable'] = False
                conditions['aql_3month']['value'] = 'N/A'
                conditions['subordinate_aql']['applicable'] = False  # 7번 조건 미적용
                conditions['subordinate_aql']['value'] = 'N/A'
                conditions['area_reject_rate']['applicable'] = False
                conditions['area_reject_rate']['value'] = 'N/A'
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
        conditions['minimum_working_days'] = {
            'name': '최소 근무일 ≥12일',
            'category': 'attendance',
            'passed': True,
            'value': '정상',
            'actual': None,
            'threshold': '12일 이상',
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
    
    elif emp_type == 'TYPE-3':
        # TYPE-3는 신입직원으로 인센티브 대상이 아님 - 모든 조건 미적용
        # 정책상 제외 이유를 명확히 표시
        policy_reason = 'TYPE-3 신입직원 정책 제외'
        
        # 출근 조건들 - 모두 미적용
        conditions['attendance_rate'] = {
            'name': '출근율 ≥88%',
            'category': 'attendance',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        conditions['absence_days'] = {
            'name': '무단결근 ≤2일',
            'category': 'attendance',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        conditions['working_days'] = {
            'name': '실제 근무일 >0일',
            'category': 'attendance',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        conditions['minimum_working_days'] = {
            'name': '최소 근무일 ≥12일',
            'category': 'attendance',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        
        # AQL 조건들 - 모두 미적용
        conditions['aql_monthly'] = {
            'name': '개인 AQL: 당월 실패 0건',
            'category': 'aql',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        conditions['aql_3month'] = {
            'name': '연속성 체크: 3개월 연속 실패 없음',
            'category': 'aql',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        conditions['subordinate_aql'] = {
            'name': '팀/구역 AQL: 부하직원 3개월 연속 실패자 없음',
            'category': 'aql',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        conditions['area_reject_rate'] = {
            'name': '담당구역 reject율 <3%',
            'category': 'aql',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        
        # 5PRS 조건들 - 모두 미적용
        conditions['5prs_volume'] = {
            'name': '5PRS 검사량 ≥100개',
            'category': '5prs',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        conditions['5prs_pass_rate'] = {
            'name': '5PRS 통과율 ≥95%',
            'category': '5prs',
            'passed': False,
            'value': 'N/A',
            'actual': 'N/A',
            'threshold': 'N/A',
            'applicable': False,
            'reason': policy_reason
        }
        
        # 특별 정책 상태 추가
        conditions['policy_status'] = {
            'name': '인센티브 정책',
            'category': 'policy',
            'passed': False,
            'value': '신입직원 제외',
            'actual': 'TYPE-3',
            'threshold': 'N/A',
            'applicable': False,
            'message': 'TYPE-3 신입직원은 인센티브 지급 대상이 아닙니다'
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
        
        # 최소 근무일 12일 실제 값 - 항상 실제 값 설정
        if 'minimum_working_days' in conditions and conditions['minimum_working_days']['applicable']:
            if actual_data.get('actual_working_days') is not None:
                actual_days = int(actual_data['actual_working_days'])
                conditions['minimum_working_days']['actual'] = f"{actual_days}일"
                if actual_days < 12:
                    conditions['minimum_working_days']['passed'] = False
                    conditions['minimum_working_days']['value'] = '기준 미달'
                else:
                    conditions['minimum_working_days']['passed'] = True
                    conditions['minimum_working_days']['value'] = '정상'
        
        # AQL 실패 건수 실제 값 - 항상 실제 값 설정
        if 'aql_monthly' in conditions and conditions['aql_monthly']['applicable']:
            # AQL INSPECTOR 특별 처리: 인센티브를 받았으면 조건 충족으로 간주
            if 'AQL INSPECTOR' in position and amount > 0:
                conditions['aql_monthly']['passed'] = True
                conditions['aql_monthly']['value'] = 'Pass'
                conditions['aql_monthly']['actual'] = '0건 (충족)'
            elif actual_data.get('july_aql_failures') is not None:
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
    - 팝업창 조건 그룹별 표시 (4-4-2 구조)
    - 각 카테고리별 시각적 구분
    - 직급별 적용 조건 명확화
    - 다국어 지원 (한국어, 영어, 베트남어)
    
    Args:
        input_html: 입력 HTML 파일 경로
        output_html: 출력 HTML 파일 경로
        calculation_month: 인센티브 계산 기준 월 (기본값: '2025-07')
    """
    
    # 월 이름 매핑
    month_korean = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }.get(month.lower(), '7월')
    
    month_english = {
        'january': 'January', 'february': 'February', 'march': 'March', 'april': 'April',
        'may': 'May', 'june': 'June', 'july': 'July', 'august': 'August',
        'september': 'September', 'october': 'October', 'november': 'November', 'december': 'December'
    }.get(month.lower(), 'July')
    
    month_vietnamese = {
        'january': 'Tháng 1 năm', 'february': 'Tháng 2 năm', 'march': 'Tháng 3 năm', 'april': 'Tháng 4 năm',
        'may': 'Tháng 5 năm', 'june': 'Tháng 6 năm', 'july': 'Tháng 7 năm', 'august': 'Tháng 8 năm',
        'september': 'Tháng 9 năm', 'october': 'Tháng 10 năm', 'november': 'Tháng 11 năm', 'december': 'Tháng 12 năm'
    }.get(month.lower(), 'Tháng 7 năm')
    
    # 이전 월 계산
    month_order = ['january', 'february', 'march', 'april', 'may', 'june', 
                   'july', 'august', 'september', 'october', 'november', 'december']
    current_index = month_order.index(month.lower()) if month.lower() in month_order else 6
    previous_index = (current_index - 1) if current_index > 0 else 11
    previous_month = month_order[previous_index]
    
    # 이전 월 이름 매핑
    previous_month_korean = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }.get(previous_month, '6월')
    
    previous_month_english = {
        'january': 'January', 'february': 'February', 'march': 'March', 'april': 'April',
        'may': 'May', 'june': 'June', 'july': 'July', 'august': 'August',
        'september': 'September', 'october': 'October', 'november': 'November', 'december': 'December'
    }.get(previous_month, 'June')
    
    previous_month_vietnamese = {
        'january': 'Tháng 1', 'february': 'Tháng 2', 'march': 'Tháng 3', 'april': 'Tháng 4',
        'may': 'Tháng 5', 'june': 'Tháng 6', 'july': 'Tháng 7', 'august': 'Tháng 8',
        'september': 'Tháng 9', 'october': 'Tháng 10', 'november': 'Tháng 11', 'december': 'Tháng 12'
    }.get(previous_month, 'Tháng 6')
    
    # 현재 월 이름 (평균 등에 사용)
    current_month_korean = month_korean
    current_month_english = month_english
    current_month_vietnamese = {
        'january': 'Tháng 1', 'february': 'Tháng 2', 'march': 'Tháng 3', 'april': 'Tháng 4',
        'may': 'Tháng 5', 'june': 'Tháng 6', 'july': 'Tháng 7', 'august': 'Tháng 8',
        'september': 'Tháng 9', 'october': 'Tháng 10', 'november': 'Tháng 11', 'december': 'Tháng 12'
    }.get(month.lower(), 'Tháng 7')
    
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
        .type-unknown {{ background: #f0f0f0; color: #666666; }}
        
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
        
        /* 조건 카드 스타일 - 4-4-2 구조 */
        .condition-group {{
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .condition-group-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 15px;
            padding: 8px 12px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .condition-group-title.attendance {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
        }}
        
        .condition-group-title.aql {{
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            color: white;
        }}
        
        .condition-group-title.prs {{
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            color: white;
        }}
        
        .condition-check {{
            padding: 12px 15px;
            margin-bottom: 8px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            transition: all 0.3s ease;
        }}
        
        .condition-check:last-child {{
            margin-bottom: 0;
        }}
        
        .condition-check:hover {{
            background: rgba(255, 255, 255, 0.12);
            transform: translateX(3px);
        }}
        
        .condition-check.success {{
            background: linear-gradient(135deg, rgba(72, 187, 120, 0.2) 0%, rgba(56, 161, 105, 0.2) 100%);
            border-color: #48bb78;
            color: #68d391;
        }}
        
        .condition-check.fail {{
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.2) 0%, rgba(229, 62, 62, 0.2) 100%);
            border-color: #f56565;
            color: #fc8181;
        }}
        
        .condition-check.not-applicable {{
            background: rgba(107, 114, 128, 0.1);
            border-color: rgba(107, 114, 128, 0.3);
            color: #a0aec0;
            opacity: 0.7;
        }}
        
        /* 실제 값 표시 스타일 - 다크 테마 */
        .actual-value-container {{
            margin-top: 8px;
            padding: 6px 10px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 6px;
            display: inline-block;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .actual-label {{
            font-weight: 600;
            color: #cbd5e0;
            margin-right: 8px;
            font-size: 0.9em;
        }}
        
        .actual-value {{
            font-weight: 700;
            font-size: 14px;
            padding: 3px 10px;
            border-radius: 4px;
        }}
        
        .actual-value.actual-success {{
            color: #68d391;
            background: rgba(72, 187, 120, 0.25);
            border: 1px solid rgba(72, 187, 120, 0.5);
        }}
        
        .actual-value.actual-fail {{
            color: #fc8181;
            background: rgba(245, 101, 101, 0.25);
            border: 1px solid rgba(245, 101, 101, 0.5);
        }}
        
        .condition-icon {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
        
        .condition-value {{
            text-align: right;
            font-weight: 500;
        }}
        
        /* 밝은 테마 모달 스타일 */
        .modal-content {{
            background: white;
            border: 1px solid #dee2e6;
            color: #212529;
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .modal-body {{
            background: white;
            color: #212529;
        }}
        
        .modal-footer {{
            background: white;
            border-top: 1px solid #dee2e6;
        }}
        
        /* 모달 내 테이블 스타일 */
        .modal-body table {{
            color: #212529;
        }}
        
        .modal-body table th {{
            background: #f8f9fa !important;
            color: #495057 !important;
            border-color: #dee2e6 !important;
        }}
        
        .modal-body table td {{
            border-color: #dee2e6;
            color: #212529;
        }}
        
        .modal-body table tr:hover {{
            background: #f8f9fa;
        }}
        
        .modal-body .table-row-paid {{
            background: rgba(72, 187, 120, 0.1);
        }}
        
        .modal-body .table-row-paid:hover {{
            background: rgba(72, 187, 120, 0.15);
        }}
        
        .modal-body .table-row-unpaid {{
            background: rgba(245, 101, 101, 0.1);
        }}
        
        .modal-body .table-row-unpaid:hover {{
            background: rgba(245, 101, 101, 0.15);
        }}
        
        /* 조건 요약 텍스트 스타일 */
        .modal-body .text-muted {{
            color: #a0aec0 !important;
        }}
        
        .modal-body small {{
            color: #cbd5e0;
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
            <p id="mainSubtitle">{year}년 {month_korean} 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;">보고서 생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
        </div>
        
        <div class="content p-4">
            <!-- 데이터 오류 경고 메시지 -->
            {f'''
            <div class="alert alert-danger mb-4" role="alert" style="display: {'block' if stats['total_amount'] == 0 else 'none'};">
                <h4 class="alert-heading">⚠️ 데이터 오류</h4>
                <p>인센티브 계산에 필요한 데이터가 누락되었습니다:</p>
                <ul class="mb-0">
                    <li>출근 데이터 파일: <code>attendance data {month}_converted.csv</code> - 누락</li>
                    <li>이전 월 인센티브 파일: <code>{year}년 {month_korean} 인센티브 지급 세부 정보.csv</code> - 누락</li>
                    <li>설정 파일: <code>type2_position_mapping.json</code> - 누락</li>
                    <li>설정 파일: <code>auditor_trainer_area_mapping.json</code> - 누락</li>
                </ul>
                <hr>
                <p class="mb-0"><strong>해결 방법:</strong> Google Drive에서 필요한 데이터 파일을 동기화하거나, 시스템 관리자에게 문의하세요.</p>
            </div>
            ''' if stats['total_amount'] == 0 else ''}
            
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
                {generate_detail_tab(employees, month)}
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
                            <h6 class="mb-0">조건 충족 현황 (4-4-2 구조)</h6>
                        </div>
                        <div class="card-body p-0" id="employeeConditions"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 다국어 번역 데이터 (확장판)
        const translations = {{
            ko: {{
                title: 'QIP 인센티브 계산 결과',
                subtitle: '{year}년 {month_korean} 인센티브 지급 현황',
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
                augustIncentive: '8월 인센티브',
                previousMonthIncentive: '{previous_month_korean} 인센티브',
                currentMonthIncentive: '{current_month_korean} 인센티브',
                change: '변동',
                reason: '사유',
                // 팝업창 관련 추가
                paymentStatus: '지급 현황',
                paid: '지급',
                unpaid: '미지급',
                conditionFulfillmentRate: '충족률',
                unpaidRate: '미지급률',
                avgFulfillmentRate: '인센티브 지급률',
                average: '평균',
                conditionDetails: '조건별 충족 현황',
                // 조건 카테고리
                attendanceConditions: '출근 조건',
                aqlConditions: 'AQL 조건',
                prsConditions: '5PRS 조건',
                unitPeopleForTable: '명',
                calculationBasisHeader: '계산 근거',
                conditionFulfillmentHeader: '조건 충족 현황',
                employeeNoHeader: '직원번호',
                nameHeader: '이름',
                incentiveHeader: '인센티브',
                statusHeader: '상태',
                attendanceLabel: '출근',
                aqlLabel: 'AQL',
                prsLabel: '5PRS',
                // 테이블 헤더
                condition: '조건',
                evaluationTarget: '평가 대상',
                fulfilled: '충족',
                notFulfilled: '미충족',
                fulfillmentRate: '충족률',
                notApplicable: '평가 대상 아님',
                // 조건 텍스트
                attendanceRate: '출근율',
                attendanceRateCondition: '출근율 ≥88%',
                unexcusedAbsence: '무단결근',
                unexcusedAbsenceCondition: '무단결근 ≤2일',
                actualWorkDays: '실제 근무일',
                actualWorkDaysCondition: '실제 근무일 >0일',
                personalAQL: '개인 AQL: 당월 실패',
                personalAQLCondition: '개인 AQL: 당월 실패 0건',
                continuityCheck: '연속성 체크',
                continuityCheckCondition: '연속성 체크: 3개월 연속 실패 없음',
                teamAreaAQL: '팀/구역 AQL',
                teamAreaAQLCondition: '팀/구역 AQL: 3개월 연속 실패 없음',
                areaRejectRate: '담당구역 reject율',
                areaRejectRateCondition: '담당구역 reject율 <3%',
                prsPassRate: '5PRS 통과율',
                prsPassRateCondition: '5PRS 통과율 ≥95%',
                prsInspectionVolume: '5PRS 검사량',
                prsInspectionVolumeCondition: '5PRS 검사량 ≥100개',
                // 필터 옵션
                allPositions: '모든 직급',
                resetFilter: '필터 초기화',
                paidOnly: '지급자만',
                unpaidOnly: '미지급자만',
                all: '전체',
                // 상세 정보
                incentiveStatistics: '인센티브 통계',
                monthIncentiveInfo: '{month}월 인센티브 정보',
                paymentAmount: '지급액',
                changeAmount: '변동',
                status: '상태',
                conditionFulfillmentStatus: '조건 충족 상태',
                notEvaluationTarget: '평가 대상 아님',
                prsConditions: '5PRS 조건',
                calculationBasis: '계산 근거',
                typeCriteriaMet: 'TYPE 기준 충족',
                additionalInfo: '추가',
                absenteeismRate: '결근율',
                // 값 번역
                passed: '충족',
                failed: '미충족',
                normal: '정상',
                exceeded: '기준 초과',
                insufficient: '기준 미달',
                notEvaluated: '평가 대상 아님',
                pass: 'Pass',
                fail: 'Fail',
                // 단위
                cases: '건',
                days: '일',
                pieces: '개',
                people: '명',
                // 기타
                incentiveDetail: '인센티브 계산 상세',
                calculationResult: '계산 결과',
                fulfillmentRate: '충족율',
                detailView: '상세보기',
                positionDetailTitle: '직급별 상세 현황',
                positionStatus: '직급별 현황',
                detail: '상세',
                detailButton: '상세 보기',
                unitPeople: '명',
                positionModalTitle: '직급별 인센티브 현황',
                positionStatusByType: '직급별 현황',
                employeeDetailStatus: '직원별 상세 현황',
                viewPaidOnly: '지급자만',
                viewUnpaidOnly: '미지급자만',
                viewAll: '전체',
                chartPaymentStatus: '지급/미지급 비율',
                chartConditionStatus: '조건별 충족률',
                statisticsTitle: '인센티브 통계',
                basicInfo: '기본 정보',
                conditionCheck: '조건 충족 체크',
                conditionStatus: '조건 충족 현황',
                workDays: '출근일수',
                actualValue: '실제값',
                threshold: '기준',
                employeeDetailTitle: '직원별 상세 현황',
                allTypes: '모든 타입',
                items: '가지',
                actualReason: '사유',
                conditionsMet: '조건 충족',
                noConditionsFailed: '조건 미달',
                allConditionsMet: '✅ 조건 충족',
                attendanceRateShort: '출근율',
                unauthorizedAbsenceShort: '무단결근',
                actualWorkingDaysShort: '실제 근무일',
                aqlMonthlyShort: '당월 AQL',
                subordinateAqlFailed: '부하직원 AQL 실패',
                inspectionVolumeShort: '검사량',
                passRateShort: '합격률',
                required: '기준',
                days: '일'
            }},
            en: {{
                title: 'QIP Incentive Calculation Results',
                subtitle: '{month_english} {year} Incentive Payment Status',
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
                augustIncentive: 'August Incentive',
                previousMonthIncentive: '{previous_month_english} Incentive',
                currentMonthIncentive: '{current_month_english} Incentive',
                change: 'Change',
                reason: 'Reason',
                // Popup related additions
                paymentStatus: 'Payment Status',
                paid: 'Paid',
                unpaid: 'Unpaid',
                conditionFulfillmentRate: 'Fulfillment Rate',
                unpaidRate: 'Unpaid Rate',
                avgFulfillmentRate: 'Incentive Payment Rate',
                average: 'Average',
                conditionDetails: 'Condition Fulfillment Details',
                // Condition categories
                attendanceConditions: 'Attendance Conditions',
                aqlConditions: 'AQL Conditions',
                prsConditions: '5PRS Conditions',
                // Table headers
                condition: 'Condition',
                evaluationTarget: 'Evaluation Target',
                fulfilled: 'Fulfilled',
                notFulfilled: 'Not Fulfilled',
                fulfillmentRate: 'Fulfillment Rate',
                notApplicable: 'Not Applicable',
                // Condition texts
                attendanceRate: 'Attendance Rate',
                attendanceRateCondition: 'Attendance Rate ≥88%',
                unexcusedAbsence: 'Unexcused Absence',
                unexcusedAbsenceCondition: 'Unexcused Absence ≤2 days',
                actualWorkDays: 'Actual Work Days',
                actualWorkDaysCondition: 'Actual Work Days >0 days',
                personalAQL: 'Personal AQL: Monthly Failures',
                personalAQLCondition: 'Personal AQL: 0 Monthly Failures',
                continuityCheck: 'Continuity Check',
                continuityCheckCondition: 'Continuity Check: No 3-month consecutive failures',
                teamAreaAQL: 'Team/Area AQL',
                teamAreaAQLCondition: 'Team/Area AQL: No 3-month failures',
                areaRejectRate: 'Area Reject Rate',
                areaRejectRateCondition: 'Area Reject Rate <3%',
                prsPassRate: '5PRS Pass Rate',
                prsPassRateCondition: '5PRS Pass Rate ≥95%',
                prsInspectionVolume: '5PRS Inspection Volume',
                prsInspectionVolumeCondition: '5PRS Inspection Volume ≥100 pieces',
                // Filter options
                allPositions: 'All Positions',
                resetFilter: 'Reset Filter',
                paidOnly: 'Paid Only',
                unpaidOnly: 'Unpaid Only',
                all: 'All',
                // Detail information
                incentiveStatistics: 'Incentive Statistics',
                monthIncentiveInfo: '{month} Incentive Information',
                paymentAmount: 'Payment Amount',
                changeAmount: 'Change',
                status: 'Status',
                conditionFulfillmentStatus: 'Condition Fulfillment Status',
                notEvaluationTarget: 'Not Applicable',
                prsConditions: '5PRS Conditions',
                calculationBasis: 'Calculation Basis',
                typeCriteriaMet: 'TYPE Criteria Met',
                additionalInfo: 'Additional',
                absenteeismRate: 'Absenteeism Rate',
                // Value translations
                passed: 'Passed',
                failed: 'Failed',
                normal: 'Normal',
                exceeded: 'Exceeded',
                insufficient: 'Insufficient',
                notEvaluated: 'Not Evaluated',
                pass: 'Pass',
                fail: 'Fail',
                // Units
                cases: ' cases',
                days: ' days',
                pieces: ' pieces',
                people: ' people',
                // Others
                incentiveDetail: 'Incentive Calculation Detail',
                calculationResult: 'Calculation Result',
                fulfillmentRate: 'Fulfillment Rate',
                detailView: 'View Details',
                positionDetailTitle: 'Position Detail Status',
                positionStatus: 'Position Status',
                detail: 'Detail',
                detailButton: 'View Details',
                unitPeople: ' people',
                positionModalTitle: 'Position Incentive Status',
                positionStatusByType: 'Position Status',
                employeeDetailStatus: 'Employee Detail Status',
                viewPaidOnly: 'Paid Only',
                viewUnpaidOnly: 'Unpaid Only',
                viewAll: 'All',
                chartPaymentStatus: 'Payment/Unpaid Ratio',
                chartConditionStatus: 'Condition Fulfillment Rate',
                statisticsTitle: 'Incentive Statistics',
                basicInfo: 'Basic Information',
                conditionCheck: 'Condition Check',
                conditionStatus: 'Condition Fulfillment Status',
                workDays: 'Work Days',
                actualValue: 'Actual Value',
                threshold: 'Threshold',
                employeeDetailTitle: 'Employee Detail Status',
                allTypes: 'All Types',
                items: ' items',
                actualReason: 'Reason',
                unitPeopleForTable: ' people',
                calculationBasisHeader: 'Calculation Basis',
                conditionFulfillmentHeader: 'Condition Fulfillment',
                employeeNoHeader: 'Employee No',
                nameHeader: 'Name',
                incentiveHeader: 'Incentive',
                statusHeader: 'Status',
                attendanceLabel: 'Attendance',
                aqlLabel: 'AQL',
                prsLabel: '5PRS',
                conditionsMet: 'conditions met',
                noConditionsFailed: 'conditions not met',
                allConditionsMet: '✅ All conditions met',
                attendanceRateShort: 'Attendance rate',
                unauthorizedAbsenceShort: 'Unexcused absence',
                actualWorkingDaysShort: 'Actual working days',
                aqlMonthlyShort: 'Monthly AQL',
                subordinateAqlFailed: 'Subordinate AQL failed',
                inspectionVolumeShort: 'Inspection volume',
                passRateShort: 'Pass rate',
                required: 'Required',
                days: ' days'
            }},
            vi: {{
                title: 'Kết quả tính toán khuyến khích QIP',
                subtitle: 'Tình trạng thanh toán khuyến khích {month_vietnamese} {year}',
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
                augustIncentive: 'Khuyến khích tháng 8',
                previousMonthIncentive: 'Khuyến khích {previous_month_vietnamese}',
                currentMonthIncentive: 'Khuyến khích {current_month_vietnamese}',
                change: 'Thay đổi',
                reason: 'Lý do',
                // Popup liên quan
                paymentStatus: 'Tình trạng thanh toán',
                paid: 'Đã trả',
                unpaid: 'Chưa trả',
                conditionFulfillmentRate: 'Tỷ lệ đáp ứng',
                unpaidRate: 'Tỷ lệ chưa trả',
                avgFulfillmentRate: 'Tỷ lệ thanh toán khuyến khích',
                average: 'Trung bình',
                conditionDetails: 'Chi tiết đáp ứng điều kiện',
                // Danh mục điều kiện
                attendanceConditions: 'Điều kiện chấm công',
                aqlConditions: 'Điều kiện AQL',
                prsConditions: 'Điều kiện 5PRS',
                // Tiêu đề bảng
                condition: 'Điều kiện',
                evaluationTarget: 'Đối tượng đánh giá',
                fulfilled: 'Đáp ứng',
                notFulfilled: 'Không đáp ứng',
                fulfillmentRate: 'Tỷ lệ đáp ứng',
                notApplicable: 'Không áp dụng',
                // Văn bản điều kiện
                attendanceRate: 'Tỷ lệ đi làm',
                attendanceRateCondition: 'Tỷ lệ đi làm ≥88%',
                unexcusedAbsence: 'Vắng không phép',
                unexcusedAbsenceCondition: 'Vắng không phép ≤2 ngày',
                actualWorkDays: 'Ngày làm thực tế',
                actualWorkDaysCondition: 'Ngày làm thực tế >0 ngày',
                personalAQL: 'AQL cá nhân: Thất bại trong tháng',
                personalAQLCondition: 'AQL cá nhân: 0 lần thất bại trong tháng',
                continuityCheck: 'Kiểm tra liên tục',
                continuityCheckCondition: 'Kiểm tra liên tục: Không có 3 tháng liên tiếp thất bại',
                teamAreaAQL: 'AQL nhóm/khu vực',
                teamAreaAQLCondition: 'AQL nhóm/khu vực: Không thất bại 3 tháng',
                areaRejectRate: 'Tỷ lệ từ chối khu vực',
                areaRejectRateCondition: 'Tỷ lệ từ chối khu vực <3%',
                prsPassRate: 'Tỷ lệ đạt 5PRS',
                prsPassRateCondition: 'Tỷ lệ đạt 5PRS ≥95%',
                prsInspectionVolume: 'Khối lượng kiểm tra 5PRS',
                prsInspectionVolumeCondition: 'Khối lượng kiểm tra 5PRS ≥100 cái',
                // Tùy chọn lọc
                allTypes: 'Tất cả loại',
                allPositions: 'Tất cả chức vụ',
                resetFilter: 'Đặt lại bộ lọc',
                paidOnly: 'Chỉ người được trả',
                unpaidOnly: 'Chỉ người chưa trả',
                all: 'Tất cả',
                // Thông tin chi tiết
                incentiveStatistics: 'Thống kê khuyến khích',
                monthIncentiveInfo: 'Thông tin khuyến khích {month}',
                paymentAmount: 'Số tiền thanh toán',
                changeAmount: 'Thay đổi',
                status: 'Trạng thái',
                conditionFulfillmentStatus: 'Trạng thái đáp ứng điều kiện',
                calculationBasis: 'Cơ sở tính toán',
                typeCriteriaMet: 'Đáp ứng tiêu chí TYPE',
                additionalInfo: 'Bổ sung',
                absenteeismRate: 'Tỷ lệ vắng mặt',
                // Dịch giá trị
                passed: 'Đạt',
                failed: 'Không đạt',
                normal: 'Bình thường',
                exceeded: 'Vượt mức',
                insufficient: 'Thiếu',
                notEvaluated: 'Không đánh giá',
                pass: 'Đạt',
                fail: 'Không đạt',
                // Đơn vị
                cases: ' trường hợp',
                days: ' ngày',
                pieces: ' cái',
                people: ' người',
                // Khác
                incentiveDetail: 'Chi tiết tính toán khuyến khích',
                calculationResult: 'Kết quả tính toán',
                fulfillmentRate: 'Tỷ lệ đáp ứng',
                detailView: 'Xem chi tiết',
                detailButton: 'Xem chi tiết',
                unitPeople: ' người',
                positionStatusByType: 'Trạng thái theo chức vụ',
                positionDetailTitle: 'Tình trạng chi tiết theo chức vụ',
                positionStatus: 'Tình trạng theo chức vụ',
                detail: 'Chi tiết',
                positionModalTitle: 'Tình trạng khuyến khích theo chức vụ',
                employeeDetailStatus: 'Tình trạng chi tiết nhân viên',
                viewPaidOnly: 'Chỉ người được trả',
                viewUnpaidOnly: 'Chỉ người chưa trả',
                viewAll: 'Tất cả',
                chartPaymentStatus: 'Tỷ lệ Đã trả/Chưa trả',
                chartConditionStatus: 'Tỷ lệ đáp ứng điều kiện',
                statisticsTitle: 'Thống kê khuyến khích',
                basicInfo: 'Thông tin cơ bản',
                conditionCheck: 'Kiểm tra điều kiện',
                conditionStatus: 'Tình trạng đáp ứng điều kiện',
                workDays: 'Ngày làm việc',
                actualValue: 'Giá trị thực tế',
                threshold: 'Ngưỡng',
                employeeDetailTitle: 'Tình trạng chi tiết nhân viên',
                allTypes: 'Tất cả loại',
                items: ' mục',
                actualReason: 'Lý do',
                notEvaluationTarget: 'Không phải đối tượng đánh giá',
                prsConditions: 'Điều kiện 5PRS',
                '5prsConditions': 'Điều kiện 5PRS',
                unitPeopleForTable: ' người',
                calculationBasisHeader: 'Cơ sở tính toán',
                conditionFulfillmentHeader: 'Tình trạng đáp ứng điều kiện',
                employeeNoHeader: 'Mã nhân viên',
                nameHeader: 'Tên',
                incentiveHeader: 'Khuyến khích',
                statusHeader: 'Trạng thái',
                attendanceLabel: 'Đi làm',
                aqlLabel: 'AQL',
                prsLabel: '5PRS',
                employeeNumber: 'Mã nhân viên',
                incentive: 'Tiền thưởng',
                employeeDetailStatus: 'Tình trạng chi tiết nhân viên',
                paidOnly: 'Chỉ người được trả',
                unpaidOnly: 'Chỉ người chưa được trả',
                viewAll: 'Xem tất cả',
                conditionsMet: 'điều kiện đáp ứng',
                noConditionsFailed: 'điều kiện không đạt',
                allConditionsMet: '✅ Tất cả điều kiện đáp ứng',
                attendanceRateShort: 'Tỷ lệ đi làm',
                unauthorizedAbsenceShort: 'Vắng không phép',
                actualWorkingDaysShort: 'Ngày làm việc thực tế',
                aqlMonthlyShort: 'AQL tháng',
                subordinateAqlFailed: 'AQL nhân viên cấp dưới thất bại',
                inspectionVolumeShort: 'Khối lượng kiểm tra',
                passRateShort: 'Tỷ lệ đạt',
                required: 'Yêu cầu',
                days: ' ngày'
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
            if (t.title && document.getElementById('mainTitle')) {{
                document.getElementById('mainTitle').innerHTML = t.title + ' <span class="version-badge">v4.2</span>';
            }}
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
            
            // 팝업창 내 텍스트 업데이트 - 아래에서 처리
            
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
            
            // Type별 요약 및 직급별 데이터 재생성 (단위 반영을 위해)
            generateSummaryData();
            generatePositionData();
            generateCriteriaContent();
            
            // 검색 플레이스홀더 업데이트
            const searchInput = document.querySelector('input[placeholder*="검색"]');
            if (searchInput) searchInput.placeholder = t.searchPlaceholder;
            
            // 팩업창 내 텍스트 업데이트
            const conditionFulfillmentTitle = document.getElementById('conditionFulfillmentTitle');
            if (conditionFulfillmentTitle) conditionFulfillmentTitle.textContent = t.conditionFulfillmentStatus || '조건별 충족 현황';
            
            // 조건 테이블 헤더 업데이트
            const conditionHeaders = document.querySelectorAll('.condition-group .th-condition');
            conditionHeaders.forEach(th => {{ th.textContent = t.condition || '조건'; }});
            
            const evaluationHeaders = document.querySelectorAll('.condition-group .th-evaluation-target');
            evaluationHeaders.forEach(th => {{ th.textContent = t.evaluationTarget || '평가 대상'; }});
            
            const fulfilledHeaders = document.querySelectorAll('.condition-group .th-fulfilled');
            fulfilledHeaders.forEach(th => {{ th.textContent = t.fulfilled || '충족'; }});
            
            const unfulfilledHeaders = document.querySelectorAll('.condition-group .th-unfulfilled');
            unfulfilledHeaders.forEach(th => {{ th.textContent = t.notFulfilled || '미충족'; }});
            
            const rateHeaders = document.querySelectorAll('.condition-group .th-fulfillment-rate');
            rateHeaders.forEach(th => {{ th.textContent = t.fulfillmentRate || '충족률'; }});
            
            // 개인별 상세 탭 업데이트
            const individualDetailTitle = document.getElementById('individualDetailTitle');
            if (individualDetailTitle) individualDetailTitle.textContent = t.individualDetail || '개인별 상세 정보';
            
            const optAllTypes = document.getElementById('optAllTypes');
            if (optAllTypes) optAllTypes.textContent = t.allTypes || '모든 타입';
            
            const optAllPositions = document.getElementById('optAllPositions');
            if (optAllPositions) optAllPositions.textContent = t.allPositions || '모든 직급';
            
            const optPaymentAll = document.getElementById('optPaymentAll');
            if (optPaymentAll) optPaymentAll.textContent = t.all || '전체';
            
            const optPaymentPaid = document.getElementById('optPaymentPaid');
            if (optPaymentPaid) optPaymentPaid.textContent = t.paid || '지급';
            
            const optPaymentUnpaid = document.getElementById('optPaymentUnpaid');
            if (optPaymentUnpaid) optPaymentUnpaid.textContent = t.unpaid || '미지급';
            
            const btnResetFilterText = document.getElementById('btnResetFilterText');
            if (btnResetFilterText) btnResetFilterText.textContent = t.resetFilter || '필터 초기화';
            
            // 차트 재생성 (언어 변경 시)
            if (window.doughnutChart) {{
                window.doughnutChart.destroy();
                window.doughnutChart = null;
            }}
            if (window.barChart) {{
                window.barChart.destroy();
                window.barChart = null;
            }}
            
            // 팩업이 열려 있으면 닫고 다시 열기 (차트 재생성을 위해)
            const openModal = document.querySelector('.modal.show');
            if (openModal) {{
                const modalId = openModal.id;
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                if (modalInstance) {{
                    modalInstance.hide();
                    // 모달이 완전히 닫힌 후 다시 열기
                    setTimeout(() => {{
                        if (modalId === 'positionDetailModal') {{
                            // 저장된 데이터로 다시 열기
                            const lastType = window.lastPositionDetailType;
                            const lastPosition = window.lastPositionDetailPosition;
                            if (lastType && lastPosition) {{
                                showPositionDetail(lastType, lastPosition);
                            }}
                        }}
                    }}, 300);
                }}
            }}
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
            if (document.getElementById('thEmployeeNo')) document.getElementById('thEmployeeNo').textContent = t.employeeNo || '직원번호';
            if (document.getElementById('thName')) document.getElementById('thName').textContent = t.name || '이름';
            if (document.getElementById('thPosition')) document.getElementById('thPosition').textContent = t.position || '직급';
            if (document.getElementById('thType')) document.getElementById('thType').textContent = t.type || 'Type';
            if (document.getElementById('thPreviousMonthIncentive')) document.getElementById('thPreviousMonthIncentive').textContent = t.previousMonthIncentive || '6월 인센티브';
            if (document.getElementById('thCurrentMonthIncentive')) document.getElementById('thCurrentMonthIncentive').textContent = t.currentMonthIncentive || '7월 인센티브';
            if (document.getElementById('thChange')) document.getElementById('thChange').textContent = t.change || '증감';
            if (document.getElementById('thCalculationBasis')) document.getElementById('thCalculationBasis').textContent = t.calculationBasis || '계산 근거';
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
            // 마지막 열린 정보 저장 (언어 변경 시 재생성을 위해)
            window.lastPositionDetailType = type;
            window.lastPositionDetailPosition = position;
            
            const modal = new bootstrap.Modal(document.getElementById('positionDetailModal'));
            const t = translations[currentLanguage]; // 현재 언어 가져오기
            document.getElementById('positionModalTitle').textContent = `${{type}} - ${{translateDataValue('position', position)}} ${{t.incentiveDetail || '인센티브 현황'}}`;
            
            // 해당 직급 데이터 필터링
            const filteredData = employeeData.filter(emp => 
                emp.type === type && emp.position === position
            );
            
            // 지급/미지급 정확한 계산
            const paid = filteredData.filter(emp => {{
                const amount = parseFloat(emp.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
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
            
            // paymentRate를 window 객체에 저장하여 플러그인에서 사용 가능하게 함
            window.currentPaymentRate = paymentRate;
            
            const ctxDoughnut = document.getElementById('positionDoughnutChart').getContext('2d');
            doughnutChart = new Chart(ctxDoughnut, {{
                type: 'doughnut',
                data: {{
                    labels: [t.paid || '지급', t.unpaid || '미지급'],
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
                                    return `${{label}}: ${{value}}${{currentLanguage === 'ko' ? '명' : currentLanguage === 'vi' ? ' người' : ''}} (${{percentage}}%)`;
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
                        
                        // paymentRate를 안전하게 가져오기
                        let displayRate = '0';
                        try {{
                            displayRate = window.currentPaymentRate || '0';
                        }} catch(e) {{
                            console.warn('Failed to get paymentRate:', e);
                        }}
                        const text = `${{displayRate}}%`;
                        const textX = width / 2;
                        const textY = height / 2 - 10;
                        
                        ctx.fillStyle = '#2e7d32';  // 진한 초록색
                        ctx.fillText(text, textX, textY);
                        
                        // 지급률 텍스트
                        ctx.font = '14px sans-serif';
                        ctx.fillStyle = '#333';  // 진한 회색
                        ctx.fillText(t.paymentRate || '지급률', textX, textY + 25);
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
                        label: t.fulfillmentRate || '충족률' + ' (%)',
                        data: Object.values(conditions).map(c => c.rate),
                        backgroundColor: Object.values(conditions).map(c => {{
                            if (c.rate >= 80) return '#28a745';  // 초록색
                            if (c.rate >= 50) return '#ffc107';  // 노란색
                            return '#dc3545';  // 빨간색
                        }}),
                        borderColor: Object.values(conditions).map(c => {{
                            if (c.rate >= 80) return '#1e7e34';
                            if (c.rate >= 50) return '#d39e00';
                            return '#bd2130';
                        }}),
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    indexAxis: 'y',  // 가로 막대 차트로 변경
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }},
                        y: {{
                            ticks: {{
                                font: {{
                                    size: 10  // 레이블 폰트 크기 축소
                                }},
                                autoSkip: false  // 레이블 자동 건너뛰기 비활성화
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: translations[currentLanguage].chartConditionStatus || '조건별 충족률'
                        }},
                        legend: {{
                            display: false  // 범례 숨기기 (단일 데이터셋이므로)
                        }}
                    }}
                }}
            }});
            
            // 통계 표시 - 개선된 구조
            const stats = calculatePositionStats(filteredData);
            
            // 인센티브 지급률 계산 (지급된 직원 비율)
            let paidCount = 0;
            let totalCount = filteredData.length;
            filteredData.forEach(emp => {{
                const amount = parseFloat(emp.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
                if (amount > 0) {{
                    paidCount++;
                }}
            }});
            const statsPaymentRate = totalCount > 0 ? ((paidCount / totalCount) * 100).toFixed(1) : 0;
            
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
                                <span class="text-danger">${{t.unpaidRate || '미지급률'}}: ${{(unpaid/filteredData.length*100).toFixed(1)}}%</span>
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
                        
                        <!-- 인센티브 지급률 -->
                        <div class="stat-section">
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="text-muted">${{t.avgFulfillmentRate || '인센티브 지급률'}}</span>
                                <span class="badge bg-${{statsPaymentRate >= 80 ? 'success' : statsPaymentRate >= 50 ? 'warning' : 'danger'}} fs-6">
                                    ${{statsPaymentRate}}%
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 조건별 테이블 - 3-4-2 그룹으로 재구성
            const conditionGroups = {{
                attendance: {{
                    title: '📅 ' + (t.attendanceConditions || '출근 조건') + ' (4' + (t.items || '가지') + ')',
                    conditions: [],
                    bgClass: 'bg-primary bg-opacity-10'
                }},
                aql: {{
                    title: '🎯 ' + (t.aqlConditions || 'AQL 조건') + ' (4' + (t.items || '가지') + ')', 
                    conditions: [],
                    bgClass: 'bg-success bg-opacity-10'
                }},
                '5prs': {{
                    title: '📊 ' + (t['5prsConditions'] || '5PRS 조건') + ' (2' + (t.items || '가지') + ')',
                    conditions: [],
                    bgClass: 'bg-info bg-opacity-10'
                }}
            }};
            
            // 조건을 그룹별로 분류 (10개 조건) - 언어 비의존적
            Object.entries(conditions).forEach(([name, data]) => {{
                // 출근 조건 (4개) - 모든 언어에서 작동하도록 개선
                if (name.includes('출근율') || name.includes('Attendance Rate') || name.includes('Tỷ lệ đi làm') ||
                    name.includes('무단결근') || name.includes('Unexcused Absence') || name.includes('Vắng không phép') ||
                    name.includes('실제 근무일') || name.includes('Actual Work Days') || name.includes('Ngày làm thực tế') ||
                    name.includes('최소 근무일') || name.includes('Minimum Work Days') || name.includes('Ngày làm tối thiểu')) {{
                    conditionGroups.attendance.conditions.push({{name, ...data}});
                }}
                // AQL 조건 (4개) - 모든 언어에서 작동하도록 개선
                else if (name.includes('AQL') || 
                    name.includes('연속성 체크') || name.includes('Continuity Check') || name.includes('Kiểm tra liên tục') ||
                    name.includes('reject율') || name.includes('Reject Rate') || name.includes('Tỷ lệ từ chối')) {{
                    conditionGroups.aql.conditions.push({{name, ...data}});
                }}
                // 5PRS 조건 (2개)
                else if (name.includes('5PRS') || name.includes('PRS')) {{
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
                                        <th width="30%" class="th-condition">${{t.condition || '조건'}}</th>
                                        <th width="20%" class="th-evaluation-target">${{t.evaluationTarget || '평가 대상'}}</th>
                                        <th width="15%" class="th-fulfilled">${{t.fulfilled || '충족'}}</th>
                                        <th width="15%" class="th-unfulfilled">${{t.notFulfilled || '미충족'}}</th>
                                        <th width="20%" class="th-fulfillment-rate">${{t.fulfillmentRate || '충족률'}}</th>
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
                                    <td colspan="4" class="text-center text-muted">${{t.notEvaluationTarget || '평가 대상 아님'}}</td>
                                </tr>
                            `;
                        }} else {{
                            const notApplicableText = condition.notApplicable > 0 ? ` <small class="text-muted">(${{condition.notApplicable}}명 제외)</small>` : '';
                            const rateClass = condition.rate >= 80 ? 'text-success' : condition.rate >= 50 ? 'text-warning' : 'text-danger';
                            conditionHtml += `
                                <tr>
                                    <td>${{condition.name}}</td>
                                    <td>${{applicable}}${{applicable > 0 ? (currentLanguage === 'ko' ? '명' : currentLanguage === 'vi' ? ' người' : '') : ''}}</td>
                                    <td class="text-success">${{condition.passed}}${{condition.passed > 0 ? (currentLanguage === 'ko' ? '명' : currentLanguage === 'vi' ? ' người' : '') : ''}}</td>
                                    <td class="text-danger">${{condition.failed}}${{condition.failed > 0 ? (currentLanguage === 'ko' ? '명' : currentLanguage === 'vi' ? ' người' : '') : ''}}</td>
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
                    <h6 class="fw-bold mb-3" id="conditionFulfillmentTitle">${{t.conditionFulfillmentStatus || t.conditionDetails || '조건별 충족 현황'}}</h6>
                    ${{conditionHtml}}
                `;
            }}
            
            // 직원별 상세 테이블 - 개선된 시각화
            const employeeDetailHtml = `
                <div class="mt-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold mb-0" id="employeeDetailTitle">${{t.employeeDetailStatus || '직원별 상세 현황'}}</h6>
                        <div class="btn-group btn-group-sm" role="group">
                            <button type="button" class="btn btn-outline-success" onclick="filterPositionTable('paid')" id="btnPaidOnly">
                                ${{t.paidOnly || '지급자만'}}
                            </button>
                            <button type="button" class="btn btn-outline-danger" onclick="filterPositionTable('unpaid')" id="btnUnpaidOnly">
                                ${{t.unpaidOnly || '미지급자만'}}
                            </button>
                            <button type="button" class="btn btn-outline-secondary" onclick="filterPositionTable('all')" id="btnViewAll">
                                ${{t.viewAll || '전체'}}
                            </button>
                        </div>
                    </div>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-sm table-hover" id="positionEmployeeTable">
                            <thead style="position: sticky; top: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; z-index: 10;">
                                <tr>
                                    <th width="10%">${{t.employeeNoHeader || '직원번호'}}</th>
                                    <th width="12%">${{t.nameHeader || '이름'}}</th>
                                    <th width="12%">${{t.incentiveHeader || '인센티브'}}</th>
                                    <th width="8%">${{t.statusHeader || '상태'}}</th>
                                    <th width="38%">${{t.conditionFulfillmentHeader || '조건 충족 현황'}}</th>
                                    <th width="20%">${{t.calculationBasisHeader || '계산 근거'}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{filteredData.map(emp => {{
                                    const amount = parseFloat(emp.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
                                    const isPaid = amount > 0;
                                    const rowClass = isPaid ? 'table-row-paid' : 'table-row-unpaid';
                                    
                                    // 조건 충족률 계산 (메타데이터 기반)
                                    const fulfillmentRate = calculateFulfillmentRate(emp);
                                    
                                    // 조건 상태 미니 표시 (출근/AQL/5PRS 3개만 표시) - TYPE 확인 추가
                                    const getConditionBadge = (conditions, type, empType, position) => {{
                                        let condition = null;
                                        let label = '';
                                        
                                        // MANAGER 계열 체크 (A.MANAGER, MANAGER, SENIOR MANAGER 등)
                                        const isManagerType = position && (
                                            position.toUpperCase().includes('MANAGER') && 
                                            !position.toUpperCase().includes('DEPUTY') && 
                                            !position.toUpperCase().includes('TEAM')
                                        );
                                        
                                        // AQL INSPECTOR 체크
                                        const isAQLInspector = position && position.toUpperCase().includes('AQL INSPECTOR');
                                        
                                        // ASSEMBLY INSPECTOR 체크 (AQL INSPECTOR와 구분 필요)
                                        const isAssemblyInspector = position && 
                                            position.toUpperCase().includes('ASSEMBLY INSPECTOR');
                                        
                                        // AUDIT & TRAINING TEAM 체크
                                        const isAuditTrainer = position && (
                                            position.toUpperCase().includes('AUDIT') || 
                                            position.toUpperCase().includes('TRAINING')
                                        );
                                        
                                        // (V) SUPERVISOR는 AQL과 5PRS 조건이 적용되지 않음 (타입 무관)
                                        const isVSupervisor = position && (
                                            position.toUpperCase().includes('(V) SUPERVISOR') ||
                                            position.toUpperCase().includes('(VICE) SUPERVISOR') ||
                                            position.toUpperCase().includes('V.SUPERVISOR')
                                        );
                                        
                                        // AQL INSPECTOR는 5PRS 조건이 적용되지 않음
                                        if (isAQLInspector && type === '5prs') {{
                                            label = t.prsLabel || '5PRS';
                                            return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        }}
                                        
                                        // AUDIT & TRAINING TEAM는 5PRS 조건이 적용되지 않음
                                        if (isAuditTrainer && type === '5prs') {{
                                            label = t.prsLabel || '5PRS';
                                            return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        }}
                                        
                                        // MANAGER 계열은 5PRS 조건이 적용되지 않음
                                        if (isManagerType && type === '5prs') {{
                                            label = t.prsLabel || '5PRS';
                                            return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        }}
                                        
                                        // MANAGER 계열은 AQL 조건이 적용되지 않음
                                        if (isManagerType && type === 'aql') {{
                                            label = t.aqlLabel || 'AQL';
                                            return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        }}
                                        
                                        if (isVSupervisor && (type === 'aql' || type === '5prs')) {{
                                            if (type === 'aql') {{
                                                label = t.aqlLabel || 'AQL';
                                            }} else if (type === '5prs') {{
                                                label = t.prsLabel || '5PRS';
                                            }}
                                            return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        }}
                                        
                                        // TYPE-2 직원은 AQL 조건이 적용되지 않음 (V) SUPERVISOR 제외
                                        if (empType === 'TYPE-2' && type === 'aql' && !isVSupervisor) {{
                                            label = t.aqlLabel || 'AQL';
                                            return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        }}
                                        
                                        // TYPE-3 직원은 AQL과 5PRS 조건이 적용되지 않음
                                        if (empType === 'TYPE-3' && (type === 'aql' || type === '5prs')) {{
                                            if (type === 'aql') {{
                                                label = t.aqlLabel || 'AQL';
                                            }} else if (type === '5prs') {{
                                                label = t.prsLabel || '5PRS';
                                            }}
                                            return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                        }}
                                        
                                        if (type === 'attendance') {{
                                            // 출근 조건은 3가지 (출근율, 무단결근, 실제근무일)를 종합
                                            label = t.attendanceLabel || '출근';
                                            
                                            // 먼저 모든 조건이 해당없음인지 체크
                                            if (conditions?.attendance_rate?.applicable === false &&
                                                conditions?.absence_days?.applicable === false &&
                                                conditions?.working_days?.applicable === false) {{
                                                return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                            }}
                                            
                                            // 적용 가능한 조건만 체크
                                            const attendanceOk = conditions?.attendance_rate?.applicable !== false && conditions?.attendance_rate?.passed === true;
                                            const absenceOk = conditions?.absence_days?.applicable !== false && conditions?.absence_days?.passed === true;
                                            const workdaysOk = conditions?.working_days?.applicable !== false && conditions?.working_days?.passed === true;
                                            
                                            // 하나라도 실패한 경우 빨간색
                                            const hasFailure = (conditions?.attendance_rate?.applicable !== false && conditions?.attendance_rate?.passed !== true) ||
                                                             (conditions?.absence_days?.applicable !== false && conditions?.absence_days?.passed !== true) ||
                                                             (conditions?.working_days?.applicable !== false && conditions?.working_days?.passed !== true);
                                            
                                            if (hasFailure) {{
                                                return `<span class="badge bg-danger" style="font-size: 0.9em;">${{label}}: ✗</span>`;
                                            }} else {{
                                                return `<span class="badge bg-success" style="font-size: 0.9em;">${{label}}: ✓</span>`;
                                            }}
                                        }}
                                        else if (type === 'aql') {{
                                            // AQL 조건들을 종합
                                            label = t.aqlLabel || 'AQL';
                                            
                                            // AQL INSPECTOR는 AQL 조건 중 일부만 적용 (5번만 적용, 6,7,8번 제외)
                                            if (isAQLInspector) {{
                                                // AQL INSPECTOR는 당월 실패(5번)만 체크
                                                if (conditions?.aql_monthly?.passed === false) {{
                                                    return `<span class="badge bg-danger" style="font-size: 0.9em;">${{label}}: ✗</span>`;
                                                }} else {{
                                                    return `<span class="badge bg-success" style="font-size: 0.9em;">${{label}}: ✓</span>`;
                                                }}
                                            }}
                                            
                                            // ASSEMBLY INSPECTOR는 5번, 6번 조건만 체크 (7,8번 제외)
                                            if (isAssemblyInspector) {{
                                                // 당월 실패(5번)와 3개월 연속(6번)만 체크
                                                const monthlyOk = conditions?.aql_monthly?.applicable !== false && conditions?.aql_monthly?.passed === true;
                                                const continuityOk = conditions?.aql_3month?.applicable !== false && conditions?.aql_3month?.passed === true;
                                                
                                                const hasFailure = (conditions?.aql_monthly?.applicable !== false && conditions?.aql_monthly?.passed !== true) ||
                                                                 (conditions?.aql_3month?.applicable !== false && conditions?.aql_3month?.passed !== true);
                                                
                                                if (hasFailure) {{
                                                    return `<span class="badge bg-danger" style="font-size: 0.9em;">${{label}}: ✗</span>`;
                                                }} else {{
                                                    return `<span class="badge bg-success" style="font-size: 0.9em;">${{label}}: ✓</span>`;
                                                }}
                                            }}
                                            
                                            // AUDIT & TRAINING TEAM는 팀 AQL과 구역 reject율만 체크 (5,6번 제외, 7,8번만 적용)
                                            if (isAuditTrainer) {{
                                                // 팀 AQL(7번)과 구역 reject율(8번)만 체크
                                                const teamOk = conditions?.subordinate_aql?.applicable !== false && conditions?.subordinate_aql?.passed === true;
                                                const rejectOk = conditions?.area_reject_rate?.applicable !== false && conditions?.area_reject_rate?.passed === true;
                                                
                                                const hasFailure = (conditions?.subordinate_aql?.applicable !== false && conditions?.subordinate_aql?.passed !== true) ||
                                                                 (conditions?.area_reject_rate?.applicable !== false && conditions?.area_reject_rate?.passed !== true);
                                                
                                                if (hasFailure) {{
                                                    return `<span class="badge bg-danger" style="font-size: 0.9em;">${{label}}: ✗</span>`;
                                                }} else {{
                                                    return `<span class="badge bg-success" style="font-size: 0.9em;">${{label}}: ✓</span>`;
                                                }}
                                            }}
                                            
                                            // 먼저 모든 조건이 해당없음인지 체크
                                            if (conditions?.aql_monthly?.applicable === false &&
                                                conditions?.aql_3month?.applicable === false &&
                                                conditions?.subordinate_aql?.applicable === false &&
                                                conditions?.area_reject_rate?.applicable === false) {{
                                                return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                            }}
                                            
                                            // 적용 가능한 조건만 체크
                                            const monthlyOk = conditions?.aql_monthly?.applicable !== false && conditions?.aql_monthly?.passed === true;
                                            const continuityOk = conditions?.aql_3month?.applicable !== false && conditions?.aql_3month?.passed === true;
                                            const teamOk = conditions?.subordinate_aql?.applicable !== false && conditions?.subordinate_aql?.passed === true;
                                            const rejectOk = conditions?.area_reject_rate?.applicable !== false && conditions?.area_reject_rate?.passed === true;
                                            
                                            // 하나라도 실패한 경우 빨간색
                                            const hasFailure = (conditions?.aql_monthly?.applicable !== false && conditions?.aql_monthly?.passed !== true) ||
                                                             (conditions?.aql_3month?.applicable !== false && conditions?.aql_3month?.passed !== true) ||
                                                             (conditions?.subordinate_aql?.applicable !== false && conditions?.subordinate_aql?.passed !== true) ||
                                                             (conditions?.area_reject_rate?.applicable !== false && conditions?.area_reject_rate?.passed !== true);
                                            
                                            if (hasFailure) {{
                                                return `<span class="badge bg-danger" style="font-size: 0.9em;">${{label}}: ✗</span>`;
                                            }} else {{
                                                return `<span class="badge bg-success" style="font-size: 0.9em;">${{label}}: ✓</span>`;
                                            }}
                                        }}
                                        else if (type === '5prs') {{
                                            // 5PRS 조건들을 종합
                                            label = t.prsLabel || '5PRS';
                                            
                                            // 먼저 모든 조건이 해당없음인지 체크
                                            if (conditions?.['5prs_volume']?.applicable === false &&
                                                conditions?.['5prs_pass_rate']?.applicable === false) {{
                                                return `<span class="badge bg-secondary" style="font-size: 0.9em;">${{label}}: N/A</span>`;
                                            }}
                                            
                                            // 적용 가능한 조건만 체크
                                            const volumeOk = conditions?.['5prs_volume']?.applicable !== false && conditions?.['5prs_volume']?.passed === true;
                                            const passRateOk = conditions?.['5prs_pass_rate']?.applicable !== false && conditions?.['5prs_pass_rate']?.passed === true;
                                            
                                            // 하나라도 실패한 경우 빨간색
                                            const hasFailure = (conditions?.['5prs_volume']?.applicable !== false && conditions?.['5prs_volume']?.passed !== true) ||
                                                             (conditions?.['5prs_pass_rate']?.applicable !== false && conditions?.['5prs_pass_rate']?.passed !== true);
                                            
                                            if (hasFailure) {{
                                                return `<span class="badge bg-danger" style="font-size: 0.9em;">${{label}}: ✗</span>`;
                                            }} else {{
                                                return `<span class="badge bg-success" style="font-size: 0.9em;">${{label}}: ✓</span>`;
                                            }}
                                        }}
                                        
                                        return '';
                                    }};
                                    
                                    return `
                                        <tr class="${{rowClass}}" data-payment="${{isPaid ? 'paid' : 'unpaid'}}" onclick="showEmployeeDetail('${{emp.emp_no}}')" style="cursor: pointer;">
                                            <td>${{emp.emp_no}}</td>
                                            <td><strong>${{emp.name}}</strong></td>
                                            <td class="fw-bold ${{isPaid ? 'text-success' : 'text-danger'}}">${{emp.{month.lower()}_incentive}}</td>
                                            <td>
                                                <span class="badge ${{isPaid ? 'bg-success' : 'bg-danger'}}">
                                                    ${{isPaid ? (t.paid || '지급') : (t.unpaid || '미지급')}}
                                                </span>
                                            </td>
                                            <td>
                                                <div class="d-flex flex-wrap gap-2">
                                                    ${{getConditionBadge(emp.conditions, 'attendance', emp.type, emp.position)}}
                                                    ${{getConditionBadge(emp.conditions, 'aql', emp.type, emp.position)}}
                                                    ${{getConditionBadge(emp.conditions, '5prs', emp.type, emp.position)}}
                                                </div>
                                                <div class="progress mt-1" style="height: 15px;">
                                                    <div class="progress-bar ${{fulfillmentRate >= 80 ? 'bg-success' : fulfillmentRate >= 50 ? 'bg-warning' : 'bg-danger'}}" 
                                                         style="width: ${{fulfillmentRate}}%" 
                                                         title="충족률: ${{fulfillmentRate}}%">
                                                    </div>
                                                </div>
                                            </td>
                                            <td><small class="text-muted">${{(() => {{
                                                // Generate calculation basis text based on conditions
                                                if (!emp.conditions) return '-';
                                                
                                                let basis = [];
                                                let amount = parseFloat(emp.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
                                                
                                                // AQL INSPECTOR 체크
                                                const isAQLInspector = emp.position && emp.position.toUpperCase().includes('AQL INSPECTOR');
                                                
                                                // ASSEMBLY INSPECTOR 체크
                                                const isAssemblyInspector = emp.position && 
                                                    emp.position.toUpperCase().includes('ASSEMBLY INSPECTOR');
                                                
                                                // AUDIT & TRAINING TEAM 체크
                                                const isAuditTrainer = emp.position && (
                                                    emp.position.toUpperCase().includes('AUDIT') || 
                                                    emp.position.toUpperCase().includes('TRAINING')
                                                );
                                                
                                                if (amount > 0) {{
                                                    // Paid - show all conditions met
                                                    basis.push(t.allConditionsMet || '✅ 조건 충족');
                                                }} else {{
                                                    // Not paid - show specific failed conditions with values
                                                    let failedDetails = [];
                                                    
                                                    // 출근 조건 체크
                                                    if (emp.conditions.attendance_rate?.applicable !== false && emp.conditions.attendance_rate?.passed === false) {{
                                                        let rate = emp.conditions.attendance_rate?.value || 'N/A';
                                                        // 출근율을 소수점 1자리로 표시
                                                        if (typeof rate === 'number' || (typeof rate === 'string' && !isNaN(parseFloat(rate)))) {{
                                                            rate = parseFloat(rate).toFixed(1) + '%';
                                                        }}
                                                        const threshold = emp.conditions.attendance_rate?.threshold || '88%';
                                                        failedDetails.push(`${{t.attendanceRateShort || '출근율'}}: ${{rate}} (${{t.required || '기준'}}: ≥${{threshold}})`);
                                                    }}
                                                    
                                                    if (emp.conditions.absence_days?.applicable !== false && emp.conditions.absence_days?.passed === false) {{
                                                        const days = emp.conditions.absence_days?.value || 'N/A';
                                                        const threshold = emp.conditions.absence_days?.threshold || '2';
                                                        failedDetails.push(`${{t.unauthorizedAbsenceShort || '무단결근'}}: ${{days}}${{t.days || '일'}} (${{t.required || '기준'}}: ≤${{threshold}}${{t.days || '일'}})`);
                                                    }}
                                                    
                                                    if (emp.conditions.working_days?.applicable !== false && emp.conditions.working_days?.passed === false) {{
                                                        const days = emp.conditions.working_days?.value || 'N/A';
                                                        const threshold = emp.conditions.working_days?.threshold || '12';
                                                        failedDetails.push(`${{t.actualWorkingDaysShort || '실제 근무일'}}: ${{days}}${{t.days || '일'}} (${{t.required || '기준'}}: ≥${{threshold}}${{t.days || '일'}})`);
                                                    }}
                                                    
                                                    // AQL 조건 체크
                                                    if (emp.conditions.aql_monthly?.applicable !== false && emp.conditions.aql_monthly?.passed === false) {{
                                                        failedDetails.push(`${{t.aqlMonthlyShort || '당월 AQL'}}: FAIL`);
                                                    }}
                                                    
                                                    if (emp.conditions.subordinate_aql?.applicable !== false && emp.conditions.subordinate_aql?.passed === false) {{
                                                        const subordinateId = emp.conditions.subordinate_aql?.subordinate_id || '';
                                                        if (subordinateId) {{
                                                            failedDetails.push(`${{t.subordinateAqlFailed || '부하직원 AQL 실패'}}: ${{subordinateId}}`);
                                                        }} else {{
                                                            failedDetails.push(`${{t.subordinateAqlFailed || '부하직원 AQL 실패'}}`);
                                                        }}
                                                    }}
                                                    
                                                    // 구역 reject율 체크 (AUDIT & TRAINING TEAM만)
                                                    if (isAuditTrainer && emp.conditions.area_reject_rate?.applicable !== false && emp.conditions.area_reject_rate?.passed === false) {{
                                                        const rate = emp.conditions.area_reject_rate?.value || 'N/A';
                                                        const threshold = emp.conditions.area_reject_rate?.threshold || '3%';
                                                        failedDetails.push(`${{t.areaRejectRateShort || '구역 reject율'}}: ${{rate}} (${{t.required || '기준'}}: <${{threshold}})`);
                                                    }}
                                                    
                                                    // 5PRS 조건 체크 (AQL INSPECTOR와 AUDIT & TRAINING TEAM은 제외)
                                                    if (!isAQLInspector && !isAuditTrainer) {{
                                                        if (emp.conditions['5prs_volume']?.applicable !== false && emp.conditions['5prs_volume']?.passed === false) {{
                                                            const volume = emp.conditions['5prs_volume']?.value || 'N/A';
                                                            const threshold = emp.conditions['5prs_volume']?.threshold || '100';
                                                            failedDetails.push(`${{t.inspectionVolumeShort || '검사량'}}: ${{volume}} (${{t.required || '기준'}}: ≥${{threshold}})`);
                                                        }}
                                                        
                                                        if (emp.conditions['5prs_pass_rate']?.applicable !== false && emp.conditions['5prs_pass_rate']?.passed === false) {{
                                                            const rate = emp.conditions['5prs_pass_rate']?.value || 'N/A';
                                                            const threshold = emp.conditions['5prs_pass_rate']?.threshold || '90%';
                                                            failedDetails.push(`${{t.passRateShort || '합격률'}}: ${{rate}} (${{t.required || '기준'}}: ≥${{threshold}})`);
                                                        }}
                                                    }}
                                                    
                                                    // 최대 3개까지만 표시
                                                    if (failedDetails.length > 3) {{
                                                        failedDetails = failedDetails.slice(0, 3);
                                                        failedDetails.push('...');
                                                    }}
                                                    
                                                    if (failedDetails.length > 0) {{
                                                        basis.push(failedDetails.join('<br>'));
                                                    }} else {{
                                                        basis.push(t.noConditionsFailed || '조건 미달');
                                                    }}
                                                }}
                                                
                                                return basis.join(' / ');
                                            }})()}}</small></td>
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
            const incentiveAmount = parseFloat(employee.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
            const status = incentiveAmount > 0 ? (t.paid || '지급') : (t.unpaid || '미지급');
            const statusClass = incentiveAmount > 0 ? 'payment-success' : 'payment-fail';
            
            // 충족율 계산 (메타데이터 기반)
            const fulfillmentRate = calculateFulfillmentRate(employee);
            
            // 개인 인센티브 정보 표시
            document.getElementById('employeeCalculation').innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="fw-bold mb-3">${{t.previousMonthIncentive || '{previous_month_korean} 인센티브'}}</h6>
                        <table class="table table-sm">
                            <tr>
                                <td width="50%">${{t.paymentAmount || '지급액'}}:</td>
                                <td class="text-end"><strong>${{employee.june_incentive}}</strong></td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6 class="fw-bold mb-3">${{t.currentMonthIncentive || '{current_month_korean} 인센티브'}}</h6>
                        <table class="table table-sm">
                            <tr>
                                <td width="50%">${{t.paymentAmount || '지급액'}}:</td>
                                <td class="text-end"><strong>${{employee.{month.lower()}_incentive}}</strong></td>
                            </tr>
                            <tr>
                                <td>${{t.changeAmount || '변동'}}:</td>
                                <td class="text-end">
                                    <span class="${{employee.change.includes('+') ? 'text-success' : employee.change.includes('-') ? 'text-danger' : 'text-secondary'}}">
                                        ${{employee.change}}
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td>${{t.status || '상태'}}:</td>
                                <td class="text-end">
                                    <span class="${{statusClass}}">${{status}}</span>
                                </td>
                            </tr>
                            <tr>
                                <td>${{t.conditionFulfillmentRate || '조건 충족율'}}:</td>
                                <td class="text-end">
                                    <span class="${{fulfillmentRate >= 80 ? 'text-success' : fulfillmentRate >= 50 ? 'text-warning' : 'text-danger'}}">
                                        <strong>${{fulfillmentRate}}%</strong>
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td>${{t.reason || '사유'}}:</td>
                                <td class="text-end"><small>${{employee.reason}}</small></td>
                            </tr>
                        </table>
                    </div>
                </div>
            `;
            
            // 동적 UI 생성 - 메타데이터 기반
            let conditionsHtml = '';
            
            if (employee.metadata && employee.metadata.condition_groups) {{
                // 메타데이터 기반 동적 렌더링
                conditionsHtml = renderConditionGroupsDynamic(employee);
            }} else if (employee.conditions) {{
                // 폴백: 기존 방식 (legacy)
                conditionsHtml = renderConditionGroupsLegacy(employee);
            }}
            
            document.getElementById('employeeConditions').innerHTML = conditionsHtml || 
                '<p class="text-muted p-3">조건 정보 없음</p>';
            
            modal.show();
        }}
        
        // 동적 조건 그룹 렌더링 (메타데이터 기반)
        function renderConditionGroupsDynamic(employee) {{
            const metadata = employee.metadata;
            const conditions = employee.conditions;
            const t = translations[currentLanguage];
            
            if (!metadata || !metadata.condition_groups) return '';
            
            let html = '';
            const groupOrder = metadata.display_config?.group_order || ['attendance', 'aql', '5prs'];
            
            groupOrder.forEach(groupKey => {{
                const group = metadata.condition_groups[groupKey];
                if (!group) return;
                
                // 적용 가능한 조건이 없고 show_empty_groups가 false면 그룹 자체를 표시하지 않음
                if (group.applicable_count === 0 && !metadata.display_config?.show_empty_groups) {{
                    return;
                }}
                
                // 그룹 헤더
                html += `
                    <div class="condition-section">
                        <div class="condition-section-header ${{groupKey}}">
                            ${{group.icon}} ${{group.name}}
                            ${{group.applicable_count > 0 ? 
                                `(${{group.applicable_count}}${{t.items || '가지'}})` : 
                                `<span class="text-muted">(${{t.notApplicable || '해당없음'}})</span>`
                            }}
                        </div>
                        <div class="condition-section-body">
                `;
                
                // 각 조건 렌더링
                if (group.conditions && group.conditions.length > 0) {{
                    group.conditions.forEach(condDef => {{
                        const conditionKey = _getConditionKeyById(condDef.id);
                        const conditionData = conditions[conditionKey] || {{}};
                        
                        if (!condDef.applicable) {{
                            // N/A 조건
                            html += `
                                <div class="condition-check not-applicable">
                                    <div>
                                        <span class="condition-icon">➖</span>
                                        <strong>${{condDef.name}}</strong>
                                    </div>
                                    <div class="condition-value">
                                        <span class="badge bg-secondary">N/A</span>
                                    </div>
                                </div>
                            `;
                        }} else {{
                            // 적용 가능한 조건
                            const passed = conditionData.passed || false;
                            const statusClass = passed ? 'success' : 'fail';
                            const statusIcon = passed ? '✅' : '❌';
                            
                            html += `
                                <div class="condition-check ${{statusClass}}">
                                    <div>
                                        <span class="condition-icon">${{statusIcon}}</span>
                                        <strong>${{condDef.name}}</strong>
                                    </div>
                                    <div class="condition-value">
                                        <strong>${{conditionData.actual || '-'}}</strong>
                                        <br>
                                        <small class="text-muted">(${{t.threshold || '기준'}}: ${{conditionData.threshold || '-'}})</small>
                                    </div>
                                </div>
                            `;
                        }}
                    }});
                }} else {{
                    html += `<p class="text-muted p-2">${{t.noConditionData || '조건 데이터 없음'}}</p>`;
                }}
                
                html += `
                        </div>
                    </div>
                `;
            }});
            
            return html;
        }}
        
        // 조건 ID로 키 가져오기
        function _getConditionKeyById(conditionId) {{
            const mapping = {{
                1: 'working_days',
                2: 'absence_days',
                3: 'attendance_rate',
                4: 'minimum_working_days',
                5: 'aql_current',
                6: 'aql_continuous',
                7: 'subordinate_aql',  // Team/Area AQL
                8: 'area_reject_rate',  // Area Reject Rate
                9: '5prs_volume',  // 5PRS Inspection Quantity
                10: '5prs_pass_rate'  // 5PRS Pass Rate
            }};
            return mapping[conditionId] || `condition_${{conditionId}}`;
        }}
        
        // 레거시 조건 그룹 렌더링 (폴백) - 4-4-2 구조 개선
        function renderConditionGroupsLegacy(employee) {{
            let html = '';
            const t = translations[currentLanguage];
            
            // 기존 하드코딩 방식
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
            
            // 4-4-2 구조로 렌더링
            const categoryInfo = {{
                attendance: {{
                    icon: '📅', 
                    name: t.attendanceConditions || '출근 조건', 
                    count: 4,
                    gradient: 'attendance'
                }},
                aql: {{
                    icon: '🎯', 
                    name: t.aqlConditions || 'AQL 조건', 
                    count: 4,
                    gradient: 'aql'
                }},
                '5prs': {{
                    icon: '📊', 
                    name: t.prsConditions || '5PRS 조건', 
                    count: 2,
                    gradient: 'prs'
                }}
            }};
            
            // 각 그룹 렌더링 - 4-4-2 구조
            ['attendance', 'aql', '5prs'].forEach(category => {{
                const info = categoryInfo[category];
                const conditions = groupedConditions[category];
                const applicableCount = conditions.filter(c => c.applicable !== false).length;
                
                // 그룹 컨테이너 시작
                html += `
                    <div class="condition-group">
                        <div class="condition-group-title ${{info.gradient}}">
                            ${{info.icon}} ${{info.name}} 
                            <span style="float: right; font-size: 0.9em; opacity: 0.9;">
                                ${{applicableCount}}/${{info.count}} 조건
                            </span>
                        </div>
                        <div class="condition-group-body">
                `;
                
                // 각 조건 렌더링
                if (conditions.length > 0) {{
                    conditions.forEach(condition => {{
                        html += renderCondition(condition);
                    }});
                }} else {{
                    // 해당 카테고리에 조건이 없는 경우
                    html += `
                        <div class="condition-check not-applicable">
                            <div class="text-center w-100">
                                <span class="text-muted">${{t.noConditionsInCategory || '이 카테고리에 적용되는 조건이 없습니다'}}</span>
                            </div>
                        </div>
                    `;
                }}
                
                html += `
                        </div>
                    </div>
                `;
            }});
            
            return html;
        }}
        
        // 조건 충족률 계산 함수 (메타데이터 기반)
        function calculateFulfillmentRate(employee) {{
            // 개선된 로직: 인센티브 지급 여부 기준 (100% 또는 0%)
            
            // 1. 인센티브 금액으로 직접 판단 (가장 정확)
            const incentiveAmount = parseFloat(employee.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
            if (incentiveAmount > 0) {{
                return 100; // 인센티브 받음 = 모든 조건 충족
            }}
            
            // 2. 메타데이터 확인
            if (employee.metadata && employee.metadata.statistics) {{
                const stats = employee.metadata.statistics;
                
                // 특별 계산 직급 체크 (관리자급 등)
                const managerialPositions = ['SUPERVISOR', 'MANAGER', 'GROUP LEADER', 'HEAD'];
                const isManagerial = managerialPositions.some(pos => 
                    employee.position && employee.position.toUpperCase().includes(pos)
                );
                
                if (isManagerial) {{
                    // 관리자급은 인센티브 여부로만 판단
                    return incentiveAmount > 0 ? 100 : 0;
                }}
                
                // 일반 직급: 모든 적용 조건 충족 여부
                if (stats.applicable_conditions > 0) {{
                    let passed = 0;
                    if (employee.condition_summary && employee.condition_summary.total_passed) {{
                        passed = employee.condition_summary.total_passed;
                    }} else if (employee.conditions) {{
                        Object.values(employee.conditions).forEach(cond => {{
                            if (cond.applicable !== false && cond.passed) {{
                                passed++;
                            }}
                        }});
                    }}
                    
                    // 모든 조건 충족 시 100%, 하나라도 미충족 시 0%
                    return (passed === stats.applicable_conditions) ? 100 : 0;
                }}
                
                return incentiveAmount > 0 ? 100 : 0;
            }}
            
            // 3. 폴백: 조건 데이터 직접 확인
            if (employee.conditions) {{
                let metConditions = 0;
                let totalConditions = 0;
                Object.values(employee.conditions).forEach(cond => {{
                    if (cond.applicable !== false) {{
                        totalConditions++;
                        if (cond.passed) metConditions++;
                    }}
                }});
                
                if (totalConditions > 0) {{
                    // 모든 조건 충족 시 100%, 하나라도 미충족 시 0%
                    return (metConditions === totalConditions) ? 100 : 0;
                }}
            }}
            
            // 4. 최종 폴백: 인센티브 금액 기준
            return incentiveAmount > 0 ? 100 : 0;
        }}
        
        // 조건 렌더링 헬퍼 함수
        function renderCondition(condition) {{
            const t = translations[currentLanguage];
            
            if (condition.applicable === false) {{
                return `
                    <div class="condition-check not-applicable">
                        <div>
                            <span class="condition-icon">➖</span>
                            <strong>${{translateConditionName(condition.name)}}</strong>
                        </div>
                        <div class="condition-value">
                            <span class="text-muted">${{t.notApplicable || '해당 없음'}}</span>
                        </div>
                    </div>
                `;
            }} else {{
                const statusClass = condition.passed ? 'success' : 'fail';
                const statusIcon = condition.passed ? '✅' : '❌';
                const statusText = condition.passed ? (t.passed || '충족') : (t.failed || '미충족');
                
                // 실적값과 기준값 포맷팅
                let actualValue = '';
                let thresholdValue = '';
                
                // 실제 값 처리
                if (condition.actual) {{
                    actualValue = condition.actual;
                }} else if (condition.value !== undefined && condition.value !== null) {{
                    // value를 실적값으로 사용
                    if (typeof condition.value === 'number') {{
                        if (condition.name.includes('율') || condition.name.includes('Rate')) {{
                            actualValue = `${{(condition.value * 100).toFixed(1)}}%`;
                        }} else {{
                            actualValue = `${{condition.value}}`;
                        }}
                    }} else {{
                        actualValue = `${{condition.value}}`;
                    }}
                }}
                
                // 기준값 처리
                if (condition.threshold !== undefined && condition.threshold !== null) {{
                    if (typeof condition.threshold === 'number') {{
                        if (condition.name.includes('율') || condition.name.includes('Rate')) {{
                            thresholdValue = `${{(condition.threshold * 100).toFixed(1)}}%`;
                        }} else {{
                            thresholdValue = `${{condition.threshold}}`;
                        }}
                    }} else {{
                        thresholdValue = `${{condition.threshold}}`;
                    }}
                }}
                
                return `
                    <div class="condition-check ${{statusClass}}">
                        <div style="margin-bottom: 8px;">
                            <span class="condition-icon">${{statusIcon}}</span>
                            <strong>${{translateConditionName(condition.name)}}</strong>
                        </div>
                        <div class="condition-value" style="font-size: 0.9em;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span>${{t.actualValue || '실적'}}:</span>
                                <strong>${{actualValue || 'N/A'}}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span>${{t.threshold || '기준'}}:</span>
                                <strong>${{thresholdValue || 'N/A'}}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; border-top: 1px solid #dee2e6; padding-top: 4px; margin-top: 4px;">
                                <span>${{t.result || '결과'}}:</span>
                                <strong class="${{statusClass === 'success' ? 'text-success' : 'text-danger'}}">${{statusText}}</strong>
                            </div>
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
            positionSelect.innerHTML = `<option value="">${{t.allPositions || '모든 직급'}}</option>`;
            
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
            // 언어별 조건 라벨 정의
            const conditionLabels = {{
                ko: {{
                    attendance: '출근율 ≥88%',
                    absence: '무단결근 ≤2일',
                    workdays: '실제 근무일 >0일',
                    minimumDays: '최소 근무일 ≥12일',
                    personalAQL: '개인 AQL: 당월 실패 0건',
                    continuity: '연속성 체크: 3개월 연속 실패 없음',
                    teamAQL: '팀/구역 AQL: 3개월 연속 실패 없음',
                    rejectRate: '담당구역 reject율 <3%',
                    prsPassRate: '5PRS 통과율 ≥95%',
                    prsVolume: '5PRS 검사량 ≥100개'
                }},
                en: {{
                    attendance: 'Attendance Rate ≥88%',
                    absence: 'Unexcused Absence ≤2 days',
                    workdays: 'Actual Work Days >0',
                    minimumDays: 'Minimum Work Days ≥12',
                    personalAQL: 'Personal AQL: Monthly Failures 0',
                    continuity: 'Continuity Check: No 3-Month Consecutive Failures',
                    teamAQL: 'Team/Area AQL: No 3-Month Failures',
                    rejectRate: 'Area Reject Rate <3%',
                    prsPassRate: '5PRS Pass Rate ≥95%',
                    prsVolume: '5PRS Inspection Volume ≥100'
                }},
                vi: {{
                    attendance: 'Tỷ lệ đi làm ≥88%',
                    absence: 'Vắng không phép ≤2 ngày',
                    workdays: 'Ngày làm thực tế >0',
                    minimumDays: 'Ngày làm tối thiểu ≥12',
                    personalAQL: 'AQL cá nhân: Thất bại trong tháng 0',
                    continuity: 'Kiểm tra liên tục: Không thất bại 3 tháng liên tiếp',
                    teamAQL: 'AQL nhóm/khu vực: Không thất bại 3 tháng',
                    rejectRate: 'Tỷ lệ từ chối khu vực <3%',
                    prsPassRate: 'Tỷ lệ đạt 5PRS ≥95%',
                    prsVolume: 'Khối lượng kiểm tra 5PRS ≥100'
                }}
            }};
            
            const labels = conditionLabels[currentLanguage] || conditionLabels.ko;
            
            const conditions = {{
                [labels.attendance]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.absence]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.workdays]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.minimumDays]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.personalAQL]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.continuity]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.teamAQL]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.rejectRate]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.prsPassRate]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }},
                [labels.prsVolume]: {{ passed: 0, failed: 0, notApplicable: 0, rate: 0, applicable: true }}
            }};
            
            // 관리자급 직급 확인 - (V) SUPERVISOR 제외
            const managerPositions = [
                'SUPERVISOR',  // (V) SUPERVISOR는 제외
                'MANAGER', 'A.MANAGER', 'ASSISTANT MANAGER', 'SENIOR MANAGER'
                // GROUP LEADER는 별도 처리
            ];
            // (V) SUPERVISOR가 아닌 경우에만 관리자로 판단
            const isManager = !position.toUpperCase().includes('(V) SUPERVISOR') && 
                             !position.toUpperCase().includes('(VICE) SUPERVISOR') && 
                             !position.toUpperCase().includes('V.SUPERVISOR') &&
                             managerPositions.some(pos => position.toUpperCase().includes(pos));
            
            // 타입별/직급별 조건 적용 여부 결정 (10개 조건 체계)
            if (type === 'TYPE-2') {{
                // (V) SUPERVISOR는 Type-2에서도 4개 조건만 (출근 조건만)
                if (position.toUpperCase().includes('(V) SUPERVISOR') || 
                    position.toUpperCase().includes('(VICE) SUPERVISOR') || 
                    position.toUpperCase().includes('V.SUPERVISOR')) {{
                    conditions[labels.personalAQL].applicable = false;
                    conditions[labels.continuity].applicable = false;
                    conditions[labels.teamAQL].applicable = false;
                    conditions[labels.rejectRate].applicable = false;
                    conditions[labels.prsPassRate].applicable = false;  // 5PRS도 제외
                    conditions[labels.prsVolume].applicable = false;    // 5PRS도 제외
                }}
                // 일반 TYPE-2는 출근 4개 + 5PRS 2개 조건 적용
                else {{
                    conditions[labels.personalAQL].applicable = false;
                    conditions[labels.continuity].applicable = false;
                    conditions[labels.teamAQL].applicable = false;
                    conditions[labels.rejectRate].applicable = false;
                    // 5PRS 조건은 적용됨 (prsPassRate, prsVolume)
                }}
            }}
            // TYPE-3는 신입직원으로 인센티브 대상이 아님 - 모든 조건 미적용
            else if (type === 'TYPE-3') {{
                // 모든 조건을 미적용으로 설정
                Object.keys(conditions).forEach(key => {{
                    conditions[key].applicable = false;
                    conditions[key].value = 'N/A';
                    conditions[key].passed = false;
                    conditions[key].reason = 'TYPE-3 신입직원 정책 제외';
                }});
                
                // 특별 메시지 추가
                return {{
                    conditions: conditions,
                    summary: {{
                        total: 0,
                        fulfilled: 0,
                        percentage: 0,
                        status: 'N/A',
                        message: {{
                            ko: 'TYPE-3 신입직원은 인센티브 지급 대상이 아닙니다',
                            en: 'TYPE-3 new employees are not eligible for incentives',
                            vi: 'Nhân viên mới TYPE-3 không đủ điều kiện nhận khuyến khích'
                        }}[currentLanguage]
                    }}
                }};
            }}
            // TYPE-1 직급별 차별화 (10개 조건 체계)
            else if (type === 'TYPE-1') {{
                // (V) SUPERVISOR - 4개 조건 (출근 조건만)
                if (position.toUpperCase().includes('(V) SUPERVISOR') || 
                    position.toUpperCase().includes('(VICE) SUPERVISOR') || 
                    position.toUpperCase().includes('V.SUPERVISOR')) {{
                    conditions[labels.personalAQL].applicable = false;  // 5번 제외
                    conditions[labels.continuity].applicable = false;   // 6번 제외
                    conditions[labels.teamAQL].applicable = false;      // 7번 제외
                    conditions[labels.rejectRate].applicable = false;   // 8번 제외
                    conditions[labels.prsPassRate].applicable = false;  // 9번 제외
                    conditions[labels.prsVolume].applicable = false;    // 10번 제외
                }}
                // GROUP LEADER - 8개 조건 (7번 부하직원 체크 제외)
                else if (position.toUpperCase().includes('GROUP LEADER')) {{
                    conditions[labels.continuity].applicable = false;  // 6번 제외
                    conditions[labels.teamAQL].applicable = false;     // 7번 제외
                }}
                // ASSEMBLY INSPECTOR - 8개 조건 (6번 3개월 연속 적용)
                else if (position.toUpperCase().includes('ASSEMBLY INSPECTOR')) {{
                    conditions[labels.teamAQL].applicable = false;     // 7번 제외
                    conditions[labels.rejectRate].applicable = false;  // 8번 제외
                }}
                // AQL INSPECTOR - 5개 조건 (5PRS 조건과 6번 조건 제외)
                else if (position.toUpperCase().includes('AQL INSPECTOR')) {{
                    conditions[labels.continuity].applicable = false;   // 6번 제외 (3개월 연속 체크 안함)
                    conditions[labels.teamAQL].applicable = false;     // 7번 제외
                    conditions[labels.rejectRate].applicable = false;  // 8번 제외
                    conditions[labels.prsPassRate].applicable = false;  // 9번 제외 (5PRS 통과율)
                    conditions[labels.prsVolume].applicable = false;    // 10번 제외 (5PRS 검사량)
                }}
                // MANAGER, A.MANAGER - 4개 조건 (출근 조건만)
                else if (position.toUpperCase().includes('MANAGER') && 
                         !position.toUpperCase().includes('DEPUTY') && 
                         !position.toUpperCase().includes('TEAM')) {{
                    // MANAGER와 A.MANAGER는 출근 4개 조건만 적용
                    conditions[labels.personalAQL].applicable = false;  // 5번 제외
                    conditions[labels.continuity].applicable = false;   // 6번 제외
                    conditions[labels.teamAQL].applicable = false;      // 7번 제외
                    conditions[labels.rejectRate].applicable = false;   // 8번 제외
                    conditions[labels.prsPassRate].applicable = false;  // 9번 제외
                    conditions[labels.prsVolume].applicable = false;    // 10번 제외
                }}
                // 일반 SUPERVISOR - 9개 조건 (6번만 제외)
                else if (position.toUpperCase().includes('SUPERVISOR') && 
                         !position.toUpperCase().includes('(V)') && 
                         !position.toUpperCase().includes('(VICE)') && 
                         !position.toUpperCase().includes('V.')) {{
                    conditions[labels.continuity].applicable = false;  // 6번만 제외
                }}
                // 기타 검사원 (BOTTOM, STITCHING, MTL INSPECTOR) - 6개 조건 (출근 4 + 5PRS 2)
                else if (position.toUpperCase().includes('BOTTOM INSPECTOR') || 
                         position.toUpperCase().includes('STITCHING INSPECTOR') ||
                         position.toUpperCase().includes('MTL INSPECTOR')) {{
                    conditions[labels.personalAQL].applicable = false;
                    conditions[labels.continuity].applicable = false;
                    conditions[labels.teamAQL].applicable = false;
                    conditions[labels.rejectRate].applicable = false;
                }}
                // DEPUTY MANAGER, TEAM LEADER - 9개 조건 (6번만 제외)
                else if (position.toUpperCase().includes('DEPUTY MANAGER') || 
                         position.toUpperCase().includes('TEAM LEADER')) {{
                    conditions[labels.continuity].applicable = false;  // 6번만 제외
                }}
                // MODEL MASTER - 5개 조건 (출근 4 + 구역담당 1)
                else if (position.toUpperCase().includes('MODEL MASTER')) {{
                    conditions[labels.personalAQL].applicable = false;  // 5번 제외
                    conditions[labels.continuity].applicable = false;   // 6번 제외
                    conditions[labels.teamAQL].applicable = false;      // 7번 제외
                    // 8번 구역담당은 적용
                    conditions[labels.prsPassRate].applicable = false;  // 9번 제외
                    conditions[labels.prsVolume].applicable = false;    // 10번 제외
                }}
                // AUDIT & TRAINING TEAM - 6개 조건 (출근 4 + 팀AQL 1 + 구역담당 1)
                else if (position.toUpperCase().includes('AUDIT') || position.toUpperCase().includes('TRAINING')) {{
                    conditions[labels.personalAQL].applicable = false;  // 5번 제외
                    conditions[labels.continuity].applicable = false;   // 6번 제외
                    // 7번 팀AQL은 적용
                    // 8번 구역담당은 적용
                    conditions[labels.prsPassRate].applicable = false;  // 9번 제외
                    conditions[labels.prsVolume].applicable = false;    // 10번 제외
                }}
                // LINE LEADER - 5개 조건 (출근 4 + 팀AQL 1)
                else if (position.toUpperCase().includes('LINE LEADER')) {{
                    conditions[labels.personalAQL].applicable = false;  // 5번 제외
                    conditions[labels.continuity].applicable = false;   // 6번 제외
                    // 7번 팀AQL은 적용
                    conditions[labels.rejectRate].applicable = false;   // 8번 제외
                    conditions[labels.prsPassRate].applicable = false;  // 9번 제외
                    conditions[labels.prsVolume].applicable = false;    // 10번 제외
                }}
            }}
            
            // 디버깅용 로그
            console.log(`analyzeConditions - type: ${{type}}, position: ${{position}}, employees: ${{employees.length}}`);
            
            // 실제로 조건이 있는 직원 수 체크
            let hasConditionsCount = 0;
            employees.forEach(emp => {{
                if (emp.conditions && Object.keys(emp.conditions).length > 0) {{
                    hasConditionsCount++;
                }}
            }});
            console.log(`Employees with conditions: ${{hasConditionsCount}}/${{employees.length}}`);
            
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
                    if (conditions[labels.attendance].applicable) {{
                        if (emp.conditions.attendance_rate) {{
                            if (emp.conditions.attendance_rate.applicable === false) {{
                                conditions[labels.attendance].notApplicable++;
                            }} else if (emp.conditions.attendance_rate.passed) {{
                                conditions[labels.attendance].passed++;
                            }} else {{
                                conditions[labels.attendance].failed++;
                            }}
                        }} else {{
                            // 조건 데이터가 없으면 failed로 처리
                            conditions[labels.attendance].failed++;
                        }}
                    }} else {{
                        conditions[labels.attendance].notApplicable++;
                    }}
                    // 2. 무단결근
                    if (conditions[labels.absence].applicable) {{
                        if (emp.conditions.absence_days) {{
                            if (emp.conditions.absence_days.applicable === false) {{
                                conditions[labels.absence].notApplicable++;
                            }} else if (emp.conditions.absence_days.passed) {{
                                conditions[labels.absence].passed++;
                            }} else {{
                                conditions[labels.absence].failed++;
                            }}
                        }} else {{
                            conditions[labels.absence].failed++;
                        }}
                    }} else {{
                        conditions[labels.absence].notApplicable++;
                    }}
                    // 3. 실제 근무일 (working_days)
                    if (conditions[labels.workdays].applicable) {{
                        if (emp.conditions.working_days) {{
                            if (emp.conditions.working_days.applicable === false) {{
                                conditions[labels.workdays].notApplicable++;
                            }} else if (emp.conditions.working_days.passed) {{
                                conditions[labels.workdays].passed++;
                            }} else {{
                                conditions[labels.workdays].failed++;
                            }}
                        }} else {{
                            conditions[labels.workdays].failed++;
                        }}
                    }} else {{
                        conditions[labels.workdays].notApplicable++;
                    }}
                    // 4. 최소 근무일 12일 (minimum_working_days)
                    if (conditions[labels.minimumDays].applicable) {{
                        if (emp.conditions.minimum_working_days) {{
                            if (emp.conditions.minimum_working_days.applicable === false) {{
                                conditions[labels.minimumDays].notApplicable++;
                            }} else if (emp.conditions.minimum_working_days.passed) {{
                                conditions[labels.minimumDays].passed++;
                            }} else {{
                                conditions[labels.minimumDays].failed++;
                            }}
                        }} else {{
                            conditions[labels.minimumDays].failed++;
                        }}
                    }} else {{
                        conditions[labels.minimumDays].notApplicable++;
                    }}
                    // 5. 개인 AQL (aql_monthly)
                    if (conditions[labels.personalAQL].applicable) {{
                        if (emp.conditions.aql_monthly) {{
                            if (emp.conditions.aql_monthly.applicable === false) {{
                                conditions[labels.personalAQL].notApplicable++;
                            }} else if (emp.conditions.aql_monthly.passed) {{
                                conditions[labels.personalAQL].passed++;
                            }} else {{
                                // AQL INSPECTOR 특별 처리: 인센티브를 받았으면 조건 충족으로 간주
                                const amount = parseFloat(emp.{month.lower()}_incentive?.replace(/[^0-9]/g, '')) || 0;
                                if (position.toUpperCase().includes('AQL INSPECTOR') && amount > 0) {{
                                    conditions[labels.personalAQL].passed++;
                                }} else {{
                                    conditions[labels.personalAQL].failed++;
                                }}
                            }}
                        }} else {{
                            // AQL INSPECTOR 특별 처리: 인센티브를 받았으면 조건 충족으로 간주
                            const amount = parseFloat(emp.{month.lower()}_incentive?.replace(/[^0-9]/g, '')) || 0;
                            if (position.toUpperCase().includes('AQL INSPECTOR') && amount > 0) {{
                                conditions[labels.personalAQL].passed++;
                            }} else {{
                                conditions[labels.personalAQL].failed++;
                            }}
                        }}
                    }} else {{
                        conditions[labels.personalAQL].notApplicable++;
                    }}
                    // 6. 3개월 연속 실패 없음 (aql_3month)
                    if (conditions[labels.continuity].applicable) {{
                        if (emp.conditions.aql_3month) {{
                            if (emp.conditions.aql_3month.applicable === false) {{
                                conditions[labels.continuity].notApplicable++;
                            }} else if (emp.conditions.aql_3month.passed) {{
                                conditions[labels.continuity].passed++;
                            }} else {{
                                conditions[labels.continuity].failed++;
                            }}
                        }} else {{
                            conditions[labels.continuity].failed++;
                        }}
                    }} else {{
                        conditions[labels.continuity].notApplicable++;
                    }}
                    // 7. 부하직원 AQL (subordinate_aql)
                    if (conditions[labels.teamAQL].applicable) {{
                        if (emp.conditions.subordinate_aql) {{
                            if (emp.conditions.subordinate_aql.applicable === false) {{
                                conditions[labels.teamAQL].notApplicable++;
                            }} else if (emp.conditions.subordinate_aql.passed) {{
                                conditions[labels.teamAQL].passed++;
                            }} else {{
                                conditions[labels.teamAQL].failed++;
                            }}
                        }} else {{
                            conditions[labels.teamAQL].failed++;
                        }}
                    }} else {{
                        conditions[labels.teamAQL].notApplicable++;
                    }}
                    // 8. 담당구역 reject율 (area_reject_rate)
                    if (conditions[labels.rejectRate].applicable) {{
                        if (emp.conditions.area_reject_rate) {{
                            if (emp.conditions.area_reject_rate.applicable === false) {{
                                conditions[labels.rejectRate].notApplicable++;
                            }} else if (emp.conditions.area_reject_rate.passed) {{
                                conditions[labels.rejectRate].passed++;
                            }} else {{
                                conditions[labels.rejectRate].failed++;
                            }}
                        }} else {{
                            conditions[labels.rejectRate].failed++;
                        }}
                    }} else {{
                        conditions[labels.rejectRate].notApplicable++;
                    }}
                    // 9. 5PRS 통과율 (5prs_pass_rate)
                    if (conditions[labels.prsPassRate].applicable) {{
                        if (emp.conditions['5prs_pass_rate']) {{
                            if (emp.conditions['5prs_pass_rate'].applicable === false) {{
                                conditions[labels.prsPassRate].notApplicable++;
                            }} else if (emp.conditions['5prs_pass_rate'].passed) {{
                                conditions[labels.prsPassRate].passed++;
                            }} else {{
                                conditions[labels.prsPassRate].failed++;
                            }}
                        }} else {{
                            conditions[labels.prsPassRate].failed++;
                        }}
                    }} else {{
                        conditions[labels.prsPassRate].notApplicable++;
                    }}
                    // 10. 5PRS 검사량 (5prs_volume)
                    if (conditions[labels.prsVolume].applicable) {{
                        if (emp.conditions['5prs_volume']) {{
                            if (emp.conditions['5prs_volume'].applicable === false) {{
                                conditions[labels.prsVolume].notApplicable++;
                            }} else if (emp.conditions['5prs_volume'].passed) {{
                                conditions[labels.prsVolume].passed++;
                            }} else {{
                                conditions[labels.prsVolume].failed++;
                            }}
                        }} else {{
                            conditions[labels.prsVolume].failed++;
                        }}
                    }} else {{
                        conditions[labels.prsVolume].notApplicable++;
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
                const amount = parseFloat(emp.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
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
            const t = translations[currentLanguage];
            console.log('generateSummaryData called');
            console.log('Employee data count:', employeeData.length);
            console.log('Current language:', currentLanguage);
            console.log('Unit people:', t.unitPeople);
            
            const typeSummary = {{}};
            
            // Type별 데이터 집계
            if (!employeeData || employeeData.length === 0) {{
                console.error('employeeData is empty or undefined!');
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">데이터가 없습니다</td></tr>';
                return;
            }}
            
            employeeData.forEach(emp => {{
                const type = emp.type;
                if (!type) {{
                    console.warn('Employee without type:', emp);
                    return;
                }}
                
                if (!typeSummary[type]) {{
                    typeSummary[type] = {{
                        total: 0,
                        paid: 0,
                        totalAmount: 0
                    }};
                }}
                
                typeSummary[type].total++;
                const incentiveField = '{month.lower()}_incentive';
                const incentiveValue = emp[incentiveField];
                
                if (!incentiveValue) {{
                    console.warn('No incentive value for:', emp.emp_no, 'field:', incentiveField);
                    return;
                }}
                
                const amount = parseFloat(incentiveValue.replace(/[^0-9]/g, '')) || 0;
                if (amount > 0) {{
                    typeSummary[type].paid++;
                    typeSummary[type].totalAmount += amount;
                }}
            }});
            
            console.log('Type summary:', typeSummary);
            console.log('Type summary keys:', Object.keys(typeSummary));
            
            // 테이블 생성
            const tbody = document.getElementById('typeSummaryBody');
            if (!tbody) {{
                console.error('typeSummaryBody element not found!');
                return;
            }}
            
            console.log('tbody element found:', tbody);
            tbody.innerHTML = '';
            
            // 타입 데이터가 있는지 확인
            if (Object.keys(typeSummary).length === 0) {{
                console.error('No type data to display!');
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">Type 데이터가 없습니다</td></tr>';
                return;
            }}
            
            Object.entries(typeSummary).sort().forEach(([type, data]) => {{
                console.log('Processing type:', type, 'with data:', data);
                const paymentRate = (data.paid / data.total * 100).toFixed(1);
                // 평균 지급액 (소수점 제거)
                const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid).toLocaleString() : '0';
                const avgTotal = data.total > 0 ? Math.round(data.totalAmount / data.total).toLocaleString() : '0';
                
                const unitText = t.unitPeople || '명';
                
                const rowHtml = `
                    <tr>
                        <td><span class="type-badge type-${{type.slice(-1).toLowerCase()}}">${{type}}</span></td>
                        <td>${{data.total}}${{unitText}}</td>
                        <td>${{data.paid}}${{unitText}}</td>
                        <td>${{paymentRate}}%</td>
                        <td>${{data.totalAmount.toLocaleString()}} VND</td>
                        <td>${{avgPaid}} VND</td>
                        <td>${{avgTotal}} VND</td>
                    </tr>
                `;
                console.log('Adding row HTML for type', type, ':', rowHtml);
                tbody.innerHTML += rowHtml;
            }});
            
            console.log('Table updated with', Object.keys(typeSummary).length, 'types');
        }}
        
        // 직급별 상세 탭 데이터 생성
        function generatePositionData() {{
            const t = translations[currentLanguage];
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
                const amount = parseFloat(emp.{month.lower()}_incentive.replace(/[^0-9]/g, '')) || 0;
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
                            <h4><span class="type-badge ${{typeClass}}">${{type}}</span> ${{t.positionStatusByType}}</h4>
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>${{t.position}}</th>
                                        <th>${{t.totalCount}}</th>
                                        <th>${{t.paidCount}}</th>
                                        <th>${{t.paymentRate}}</th>
                                        <th>${{t.totalAmount}}</th>
                                        <th>${{t.paidBasis}}<br>${{t.avgAmount}}</th>
                                        <th>${{t.totalBasis}}<br>${{t.avgAmount}}</th>
                                        <th>${{t.detail}}</th>
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
                                <td>${{pos.total}}${{t.unitPeople}}</td>
                                <td>${{pos.paid}}${{t.unitPeople}}</td>
                                <td>${{paymentRate}}%</td>
                                <td>${{pos.totalAmount.toLocaleString()}} VND</td>
                                <td>${{avgPaid}} VND</td>
                                <td>${{avgTotal}} VND</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" 
                                        onclick="showPositionDetail('${{type}}', '${{pos.position}}')"
                                        style="padding: 2px 8px; font-size: 0.85em;">
                                        📈 ${{t.detailButton}}
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
        
        // 인센티브 기준 콘텐츠 생성
        function generateCriteriaContent() {{
            const t = translations[currentLanguage];
            
            // 언어별 기준 콘텐츠 정의
            const criteriaContent = {{
                ko: {{
                    title: '인센티브 지급 기준',
                    section1: '1. 기본 자격 요건',
                    attendance: '출근율: 88% 이상 (결근율 12% 이하)',
                    absence: '무단결근: 2일 이하',
                    workdays: '실제 근무일: 15일 이상',
                    section2: '2. 업무 성과 기준',
                    aqlTitle: 'AQL (Acceptable Quality Level)',
                    monthlyAql: '당월 AQL: PASS 필수',
                    consecutive: '3개월 연속 실패: 인센티브 지급 제외',
                    subordinate: '부하직원 AQL: 관리자의 경우 팀/구역 AQL PASS 필수',
                    prsTitle: '5PRS (5 Point Rating System)',
                    inspectionVolume: '검사량: 월 100건 이상',
                    passRate: '합격률: 90% 이상',
                    section3: '3. 직급별 특별 조건',
                    managerCondition: '관리자급 (Supervisor, Manager): 팀/구역 성과 반영',
                    employeeCondition: '일반 직원: 개인 성과 중심 평가',
                    section4: '4. 인센티브 금액',
                    colType: 'TYPE',
                    colAmount: '지급액',
                    colNote: '비고',
                    type1Note: '정규직 생산직',
                    type2Note: '계약직/신입',
                    type3Note: '인센티브 제외 대상',
                    section5: '5. 지급 제외 사유',
                    exclude1: '출근일수 0일',
                    exclude2: '무단결근 3일 이상',
                    exclude3: '결근율 12% 초과',
                    exclude4: '3개월 연속 AQL 실패',
                    exclude5: '월중 퇴사자',
                    exclude6: 'TYPE-3 정책 제외 대상',
                    note: '참고: 인센티브는 매월 말일 기준으로 평가되며, 익월 급여와 함께 지급됩니다.'
                }},
                en: {{
                    title: 'Incentive Payment Criteria',
                    section1: '1. Basic Qualification Requirements',
                    attendance: 'Attendance Rate: 88% or higher (Absence rate 12% or lower)',
                    absence: 'Unexcused Absence: 2 days or less',
                    workdays: 'Actual Working Days: 15 days or more',
                    section2: '2. Work Performance Criteria',
                    aqlTitle: 'AQL (Acceptable Quality Level)',
                    monthlyAql: 'Monthly AQL: PASS required',
                    consecutive: '3 Consecutive Months Failure: Excluded from incentive',
                    subordinate: 'Subordinate AQL: Team/Area AQL PASS required for managers',
                    prsTitle: '5PRS (5 Point Rating System)',
                    inspectionVolume: 'Inspection Volume: 100 items or more per month',
                    passRate: 'Pass Rate: 90% or higher',
                    section3: '3. Position-specific Conditions',
                    managerCondition: 'Management Level (Supervisor, Manager): Team/Area performance reflected',
                    employeeCondition: 'General Employee: Individual performance-focused evaluation',
                    section4: '4. Incentive Amount',
                    colType: 'TYPE',
                    colAmount: 'Payment Amount',
                    colNote: 'Remarks',
                    type1Note: 'Regular Production Staff',
                    type2Note: 'Contract/New Employee',
                    type3Note: 'Excluded from Incentive',
                    section5: '5. Exclusion Reasons',
                    exclude1: 'Working days: 0 days',
                    exclude2: 'Unexcused absence: 3 days or more',
                    exclude3: 'Absence rate exceeds 12%',
                    exclude4: '3 consecutive months of AQL failure',
                    exclude5: 'Mid-month resignation',
                    exclude6: 'TYPE-3 policy exclusion',
                    note: 'Note: Incentives are evaluated on the last day of each month and paid with the following month\\'s salary.'
                }},
                vi: {{
                    title: 'Tiêu chuẩn thanh toán khuyến khích',
                    section1: '1. Yêu cầu trình độ cơ bản',
                    attendance: 'Tỷ lệ đi làm: 88% trở lên (Tỷ lệ vắng mặt 12% trở xuống)',
                    absence: 'Vắng không phép: 2 ngày trở xuống',
                    workdays: 'Ngày làm việc thực tế: 15 ngày trở lên',
                    section2: '2. Tiêu chuẩn hiệu suất công việc',
                    aqlTitle: 'AQL (Mức chất lượng chấp nhận được)',
                    monthlyAql: 'AQL hàng tháng: Bắt buộc ĐẠT',
                    consecutive: 'Thất bại 3 tháng liên tiếp: Loại trừ khỏi khuyến khích',
                    subordinate: 'AQL cấp dưới: Quản lý phải ĐẠT AQL nhóm/khu vực',
                    prsTitle: '5PRS (Hệ thống đánh giá 5 điểm)',
                    inspectionVolume: 'Khối lượng kiểm tra: 100 mục trở lên mỗi tháng',
                    passRate: 'Tỷ lệ đạt: 90% trở lên',
                    section3: '3. Điều kiện theo chức vụ',
                    managerCondition: 'Cấp quản lý (Giám sát, Quản lý): Phản ánh hiệu suất nhóm/khu vực',
                    employeeCondition: 'Nhân viên chung: Đánh giá tập trung vào hiệu suất cá nhân',
                    section4: '4. Số tiền khuyến khích',
                    colType: 'LOẠI',
                    colAmount: 'Số tiền thanh toán',
                    colNote: 'Ghi chú',
                    type1Note: 'Nhân viên sản xuất chính thức',
                    type2Note: 'Hợp đồng/Nhân viên mới',
                    type3Note: 'Loại trừ khỏi khuyến khích',
                    section5: '5. Lý do loại trừ',
                    exclude1: 'Ngày làm việc: 0 ngày',
                    exclude2: 'Vắng không phép: 3 ngày trở lên',
                    exclude3: 'Tỷ lệ vắng mặt vượt quá 12%',
                    exclude4: '3 tháng liên tiếp thất bại AQL',
                    exclude5: 'Nghỉ việc giữa tháng',
                    exclude6: 'Loại trừ theo chính sách TYPE-3',
                    note: 'Lưu ý: Khuyến khích được đánh giá vào ngày cuối cùng của mỗi tháng và được thanh toán cùng với lương tháng sau.'
                }}
            }};
            
            const content = criteriaContent[currentLanguage] || criteriaContent.ko;
            
            // HTML 생성
            const html = `
                <h2 class="section-title">${{content.title}}</h2>
                <div class="criteria-content">
                    <h3>${{content.section1}}</h3>
                    <ul>
                        <li><strong>${{content.attendance.split(':')[0]}}:</strong> ${{content.attendance.split(':')[1]}}</li>
                        <li><strong>${{content.absence.split(':')[0]}}:</strong> ${{content.absence.split(':')[1]}}</li>
                        <li><strong>${{content.workdays.split(':')[0]}}:</strong> ${{content.workdays.split(':')[1]}}</li>
                    </ul>
                    
                    <h3>${{content.section2}}</h3>
                    <h4>${{content.aqlTitle}}</h4>
                    <ul>
                        <li><strong>${{content.monthlyAql.split(':')[0]}}:</strong> ${{content.monthlyAql.split(':')[1]}}</li>
                        <li><strong>${{content.consecutive.split(':')[0]}}:</strong> ${{content.consecutive.split(':')[1]}}</li>
                        <li><strong>${{content.subordinate.split(':')[0]}}:</strong> ${{content.subordinate.split(':')[1]}}</li>
                    </ul>
                    
                    <h4>${{content.prsTitle}}</h4>
                    <ul>
                        <li><strong>${{content.inspectionVolume.split(':')[0]}}:</strong> ${{content.inspectionVolume.split(':')[1]}}</li>
                        <li><strong>${{content.passRate.split(':')[0]}}:</strong> ${{content.passRate.split(':')[1]}}</li>
                    </ul>
                    
                    <h3>${{content.section3}}</h3>
                    <ul>
                        <li><strong>${{content.managerCondition.split(':')[0]}}:</strong> ${{content.managerCondition.split(':')[1]}}</li>
                        <li><strong>${{content.employeeCondition.split(':')[0]}}:</strong> ${{content.employeeCondition.split(':')[1]}}</li>
                    </ul>
                    
                    <h3>${{content.section4}}</h3>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>${{content.colType}}</th>
                                <th>${{content.colAmount}}</th>
                                <th>${{content.colNote}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>TYPE-1</td>
                                <td>500,000 VND</td>
                                <td>${{content.type1Note}}</td>
                            </tr>
                            <tr>
                                <td>TYPE-2</td>
                                <td>300,000 VND</td>
                                <td>${{content.type2Note}}</td>
                            </tr>
                            <tr>
                                <td>TYPE-3</td>
                                <td>-</td>
                                <td>${{content.type3Note}}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <h3>${{content.section5}}</h3>
                    <ul>
                        <li>${{content.exclude1}}</li>
                        <li>${{content.exclude2}}</li>
                        <li>${{content.exclude3}}</li>
                        <li>${{content.exclude4}}</li>
                        <li>${{content.exclude5}}</li>
                        <li>${{content.exclude6}}</li>
                    </ul>
                    
                    <div class="alert alert-info mt-4">
                        <strong>${{content.note.split(':')[0]}}:</strong> ${{content.note.substring(content.note.indexOf(':') + 1).trim()}}
                    </div>
                </div>
            `;
            
            // 콘텐츠 업데이트
            const container = document.getElementById('criteriaContent');
            if (container) {{
                container.innerHTML = html;
            }}
        }}
        
        // 페이지 로드 시 초기화
        window.onload = function() {{
            console.log('Window onload triggered');
            try {{
                updatePositionFilter();
                console.log('updatePositionFilter completed');
            }} catch(e) {{
                console.error('Error in updatePositionFilter:', e);
            }}
            
            try {{
                generateSummaryData();
                console.log('generateSummaryData completed');
            }} catch(e) {{
                console.error('Error in generateSummaryData:', e);
            }}
            
            try {{
                generatePositionData();
                console.log('generatePositionData completed');
            }} catch(e) {{
                console.error('Error in generatePositionData:', e);
            }}
            
            try {{
                generateCriteriaContent();
                console.log('generateCriteriaContent completed');
            }} catch(e) {{
                console.error('Error in generateCriteriaContent:', e);
            }}
            showTab('summary');
            
            // 디버깅: 로드 완료 후 데이터 확인
            console.log('=== Window onload complete ===');
            console.log('EmployeeData length:', employeeData.length);
            console.log('First 3 employees:', employeeData.slice(0, 3));
            
            // 수동으로 generateSummaryData 재실행 테스트
            setTimeout(() => {{
                console.log('=== Manual retry generateSummaryData ===');
                generateSummaryData();
            }}, 1000);
            
            // 언어 선택 이벤트 리스너
            document.getElementById('languageSelector').addEventListener('change', function(e) {{
                changeLanguage(e.target.value);
            }});
        }};
    </script>
</body>
</html>"""
    
    # 변수 치환
    html_content = html_content.replace('{year}', str(year))
    html_content = html_content.replace('{month_korean}', month_korean)
    html_content = html_content.replace('{month_english}', month_english)
    html_content = html_content.replace('{month_vietnamese}', month_vietnamese)
    html_content = html_content.replace('{previous_month_korean}', previous_month_korean)
    html_content = html_content.replace('{previous_month_english}', previous_month_english)
    html_content = html_content.replace('{previous_month_vietnamese}', previous_month_vietnamese)
    html_content = html_content.replace('{current_month_korean}', current_month_korean)
    html_content = html_content.replace('{current_month_english}', current_month_english)
    html_content = html_content.replace('{current_month_vietnamese}', current_month_vietnamese)
    html_content = html_content.replace('{month}', month)  # JavaScript에서 사용하는 월 변수
    html_content = html_content.replace('{month-1}', str(int(month_korean[:-1]) - 1) if month_korean != '1월' else '12')  # 이전 월 숫자
    
    # HTML 파일 저장
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 개선된 대시보드 Version 4가 성공적으로 생성되었습니다!")
    print(f"📁 파일 경로: {output_html}")
    print(f"📊 처리된 직원 수: {len(employees)}명")
    print(f"💰 총 지급액: {format_currency(stats['total_amount'])}")
    print(f"📈 지급률: {stats['payment_rate']:.1f}%")
    print(f"🎯 주요 개선사항: 팝업창 조건 4-4-2 구조로 세분화")

def calculate_statistics(employees, calculation_month=None, exclude_types=None):
    """통계 계산
    
    Args:
        employees: 직원 데이터 리스트
        calculation_month: 인센티브 계산 기준 월 (예: '2025-07')
                          None인 경우 모든 직원 포함
        exclude_types: 제외할 TYPE 리스트 (예: ['TYPE-3'])
    """
    import pandas as pd
    
    # calculation_month에서 월 이름 추출 (예: '2025-08' → 'august')
    month_num_to_name = {
        '01': 'january', '02': 'february', '03': 'march', '04': 'april',
        '05': 'may', '06': 'june', '07': 'july', '08': 'august', 
        '09': 'september', '10': 'october', '11': 'november', '12': 'december'
    }
    
    if calculation_month and '-' in calculation_month:
        month_num = calculation_month.split('-')[1]
        incentive_field = f"{month_num_to_name.get(month_num, 'july')}_incentive"
    else:
        incentive_field = 'july_incentive'  # 기본값
    
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
    paid = sum(1 for emp in active_employees if not emp[incentive_field].startswith('0 VND'))
    
    total_amount = 0
    for emp in active_employees:
        amount_str = emp[incentive_field].replace(' VND', '').replace(',', '')
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
    """요약 탭 HTML 생성 - 동적 JavaScript 생성"""
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
                <!-- JavaScript로 동적 생성됨 -->
            </tbody>
        </table>
        <!-- generateSummaryData는 window.onload에서 호출됨 -->
    """

def generate_position_tab(employees):
    """직급별 상세 탭 HTML 생성"""
    return """
        <h3 id="positionTabTitle">직급별 상세 현황</h3>
        <div id="positionTables">
            <!-- JavaScript로 채워질 예정 -->
        </div>
    """

def generate_detail_tab(employees, month='july'):
    """개인별 상세 탭 HTML 생성"""
    html = """
        <h3 id="individualDetailTitle">개인별 상세 정보</h3>
        <div class="filter-container">
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
                <div class="col-md-2">
                    <button class="btn btn-secondary w-100" onclick="clearFilters()">
                        <span id="btnResetFilterText">필터 초기화</span>
                    </button>
                </div>
            </div>
        </div>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th id="thEmployeeNo">직원번호</th>
                        <th id="thName">이름</th>
                        <th id="thPosition">직급</th>
                        <th id="thType">Type</th>
                        <th id="thPreviousMonthIncentive">6월 인센티브</th>
                        <th id="thCurrentMonthIncentive">7월 인센티브</th>
                        <th id="thChange">증감</th>
                        <th id="thCalculationBasis">계산 근거</th>
                    </tr>
                </thead>
                <tbody id="detailTableBody">
    """
    
    # 직원 데이터 추가
    for emp in employees:
        # Type이 비어있을 경우 처리
        if emp.get('type') and len(emp['type']) > 0:
            type_class = f"type-{emp['type'][-1].lower()}"
            type_display = emp['type']
        else:
            type_class = "type-unknown"
            type_display = "N/A"
            
        html += f"""
            <tr onclick="showEmployeeDetail('{emp['emp_no']}')" style="cursor: pointer;">
                <td>{emp['emp_no']}</td>
                <td>{emp['name']}</td>
                <td>{emp['position']}</td>
                <td><span class="type-badge {type_class}">{type_display}</span></td>
                <td>{emp['june_incentive']}</td>
                <td><strong>{emp[f'{month.lower()}_incentive']}</strong></td>
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
    """인센티브 기준 탭 HTML 생성 - 포괄적 정책 문서"""
    return """
        <div id="criteriaContent" style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
            <h2 class="mb-4" style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px;">
                QIP 인센티브 지급 정책 가이드
            </h2>
            
            <!-- 정책 요약 섹션 -->
            <div class="alert alert-info mb-4">
                <h5 class="alert-heading">📌 핵심 원칙</h5>
                <p class="mb-2">모든 직원은 해당 직급별로 지정된 <strong>모든 조건을 충족</strong>해야 인센티브를 받을 수 있습니다.</p>
                <p class="mb-0">조건은 출근(4개), AQL(4개), 5PRS(2개)로 구성되며, 직급별로 적용 조건이 다릅니다.</p>
            </div>
            
            <!-- 10가지 조건 상세 설명 -->
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">📊 10가지 평가 조건 상세</h5>
                </div>
                <div class="card-body">
                    <!-- 출근 조건 -->
                    <h6 class="text-success mb-3">📅 출근 조건 (4개)</h6>
                    <table class="table table-sm table-bordered mb-4">
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
                    <h6 class="text-primary mb-3">🎯 AQL 조건 (4개)</h6>
                    <table class="table table-sm table-bordered mb-4">
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
                                <td>담당구역 Reject율</td>
                                <td><3%</td>
                                <td>담당 구역의 품질 불량률이 3% 미만이어야 합니다</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <!-- 5PRS 조건 -->
                    <h6 class="text-warning mb-3">📊 5PRS 조건 (2개)</h6>
                    <table class="table table-sm table-bordered">
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
                                <td>5점 평가 시스템에서 95% 이상 통과해야 합니다</td>
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
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">
                    <h5 class="mb-0">🎖️ 직급별 적용 조건</h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-warning mb-3">
                        <strong>중요:</strong> AUDITOR & TRAINING TEAM은 조건 7(팀/구역 AQL)과 조건 8(담당구역 Reject율)이 적용됩니다.
                    </div>
                    
                    <h6 class="text-info mb-3">TYPE-1 직급별 조건</h6>
                    <table class="table table-sm table-bordered table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>직급</th>
                                <th>적용 조건</th>
                                <th>조건 수</th>
                                <th>특이사항</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>MANAGER</strong></td>
                                <td>1, 2, 3, 4</td>
                                <td>4개</td>
                                <td>출근 조건만</td>
                            </tr>
                            <tr>
                                <td><strong>A.MANAGER</strong></td>
                                <td>1, 2, 3, 4</td>
                                <td>4개</td>
                                <td>출근 조건만</td>
                            </tr>
                            <tr>
                                <td><strong>(V) SUPERVISOR</strong></td>
                                <td>1, 2, 3, 4</td>
                                <td>4개</td>
                                <td>출근 조건만</td>
                            </tr>
                            <tr>
                                <td><strong>GROUP LEADER</strong></td>
                                <td>1, 2, 3, 4</td>
                                <td>4개</td>
                                <td>출근 조건만</td>
                            </tr>
                            <tr class="table-info">
                                <td><strong>LINE LEADER</strong></td>
                                <td>1, 2, 3, 4, 7</td>
                                <td>5개</td>
                                <td>출근 + 팀/구역 AQL</td>
                            </tr>
                            <tr>
                                <td><strong>AQL INSPECTOR</strong></td>
                                <td>1, 2, 3, 4, 5</td>
                                <td>5개</td>
                                <td>출근 + 당월 AQL (특별 계산)</td>
                            </tr>
                            <tr>
                                <td><strong>ASSEMBLY INSPECTOR</strong></td>
                                <td>1, 2, 3, 4, 5, 6, 9, 10</td>
                                <td>8개</td>
                                <td>출근 + 개인 AQL + 5PRS</td>
                            </tr>
                            <tr class="table-warning">
                                <td><strong>AUDIT & TRAINING TEAM</strong></td>
                                <td>1, 2, 3, 4, 7, 8</td>
                                <td>6개</td>
                                <td>출근 + 팀/구역 AQL + 담당구역 reject</td>
                            </tr>
                            <tr>
                                <td><strong>MODEL MASTER</strong></td>
                                <td>1, 2, 3, 4, 8</td>
                                <td>5개</td>
                                <td>출근 + 담당구역 reject</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <h6 class="text-info mb-3 mt-4">TYPE-2 직급별 조건</h6>
                    <table class="table table-sm table-bordered table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>직급</th>
                                <th>적용 조건</th>
                                <th>조건 수</th>
                                <th>특이사항</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>모든 TYPE-2 직급</strong></td>
                                <td>1, 2, 3, 4</td>
                                <td>4개</td>
                                <td>출근 조건만 적용</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <h6 class="text-info mb-3 mt-4">TYPE-3 직급별 조건</h6>
                    <table class="table table-sm table-bordered table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>직급</th>
                                <th>적용 조건</th>
                                <th>조건 수</th>
                                <th>특이사항</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="table-secondary">
                                <td><strong>NEW QIP MEMBER</strong></td>
                                <td>없음</td>
                                <td>0개</td>
                                <td>신입직원 - 조건 없이 기본 인센티브</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 인센티브 금액 정보 -->
            <div class="card mb-4">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">💰 인센티브 지급액 기준</h5>
                </div>
                <div class="card-body">
                    <table class="table table-sm table-bordered">
                        <thead class="table-light">
                            <tr>
                                <th>타입</th>
                                <th>기본 지급 범위</th>
                                <th>특별 케이스</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>TYPE-1</strong></td>
                                <td>150,000 ~ 500,000 VND</td>
                                <td>
                                    AQL INSPECTOR: 최대 2,600,000 VND<br>
                                    (Part1: 1,000,000 + Part2: 700,000 + Part3: 900,000)
                                </td>
                            </tr>
                            <tr>
                                <td><strong>TYPE-2</strong></td>
                                <td>50,000 ~ 300,000 VND</td>
                                <td>-</td>
                            </tr>
                            <tr>
                                <td><strong>TYPE-3</strong></td>
                                <td>30,000 ~ 150,000 VND</td>
                                <td>신입직원 기본 지급</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- FAQ 섹션 -->
            <div class="card">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">❓ 자주 묻는 질문</h5>
                </div>
                <div class="card-body">
                    <div class="accordion" id="faqAccordion">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                                    Q1. 조건 중 하나만 미충족해도 인센티브를 못 받나요?
                                </button>
                            </h2>
                            <div id="faq1" class="accordion-collapse collapse show" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <strong>네, 맞습니다.</strong> 해당 직급에 적용되는 모든 조건을 충족해야만 인센티브를 받을 수 있습니다.
                                    예를 들어, LINE LEADER는 5개 조건(1,2,3,4,7)을 모두 충족해야 합니다.
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                                    Q2. AQL INSPECTOR의 특별 계산이란 무엇인가요?
                                </button>
                            </h2>
                            <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    AQL INSPECTOR는 3가지 파트로 나누어 계산됩니다:
                                    <ul>
                                        <li>Part 1: AQL 평가 결과 (최대 1,000,000 VND)</li>
                                        <li>Part 2: CFA 자격증 보유 (700,000 VND)</li>
                                        <li>Part 3: HWK 클레임 방지 (최대 900,000 VND)</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                                    Q3. 신입직원(TYPE-3)은 왜 조건이 없나요?
                                </button>
                            </h2>
                            <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    신입직원은 아직 업무에 적응 중이므로 성과 조건 없이 기본 인센티브를 지급합니다.
                                    이는 신입직원의 동기부여와 안정적인 정착을 돕기 위한 정책입니다.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
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