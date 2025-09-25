"""
Comprehensive Data Error Detection System
데이터 품질 종합 검증 시스템
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

class DataErrorDetector:
    """포괄적 데이터 오류 감지 클래스"""

    def __init__(self, year, month, latest_data_date=None):
        self.year = year
        self.month = month
        self.month_start = pd.Timestamp(year, month, 1)
        self.month_end = pd.Timestamp(year, month, 1) + pd.DateOffset(months=1) - pd.Timedelta(days=1)
        self.latest_data_date = latest_data_date  # 실제 데이터 최신 날짜
        self.errors = {
            'temporal_errors': [],
            'type_errors': [],
            'position_errors': [],
            'team_errors': [],
            'attendance_errors': [],
            'duplicate_errors': [],
            'summary': {
                'total_errors': 0,
                'critical': 0,
                'warning': 0,
                'info': 0
            }
        }
        
    def detect_all_errors(self, df):
        """모든 오류 유형 감지"""
        print("\n🔍 Starting Comprehensive Error Detection...")
        
        # 1. Temporal Errors
        self.detect_temporal_errors(df)
        
        # 2. TYPE Errors
        self.detect_type_errors(df)
        
        # 3. Position Errors
        self.detect_position_errors(df)
        
        # 4. Team Errors
        self.detect_team_errors(df)
        
        # 5. Attendance Errors
        self.detect_attendance_errors(df)
        
        # 6. Duplicate Errors
        self.detect_duplicate_errors(df)
        
        # Summary
        self.calculate_summary()
        
        return self.errors
    
    def add_error(self, category, error_data):
        """오류 추가 헬퍼 함수"""
        self.errors[category].append(error_data)
        
        # Update summary
        severity = error_data.get('severity', 'info')
        if severity == 'critical':
            self.errors['summary']['critical'] += 1
        elif severity == 'warning':
            self.errors['summary']['warning'] += 1
        else:
            self.errors['summary']['info'] += 1
            
    def detect_temporal_errors(self, df):
        """시간 관련 오류 감지"""
        print("  📅 Detecting temporal errors...")

        # 미래 입사자 검사 - 실제 데이터 기준일 이후 입사자는 날짜 입력 오류로 판단
        from datetime import datetime
        from calendar import monthrange

        # 데이터 최신일 계산 - 실제 데이터 날짜 사용 (하드코딩 제거)
        if self.latest_data_date:
            # 실제 데이터 최신 날짜가 제공된 경우
            data_latest_date = self.latest_data_date
        else:
            # 제공되지 않은 경우 월말 사용 (폴백)
            last_day = monthrange(self.year, self.month)[1]
            data_latest_date = pd.Timestamp(self.year, self.month, last_day)

        if 'Entrance Date' in df.columns:
            # 미래 입사자 감지 (데이터 기준일 이후 입사)
            future_employees = df[
                (df['Entrance Date'].notna()) &
                (df['Entrance Date'] > data_latest_date)
            ]
            for _, row in future_employees.iterrows():
                entrance_date = row['Entrance Date']
                self.add_error('temporal_errors', {
                    'id': row.get('Employee No', row.get('ID No', 'N/A')),
                    'name': row.get('Full Name', row.get('Name', 'N/A')),
                    'error_type': '날짜 형태 오류',
                    'error_column': 'Entrance Date',
                    'error_value': str(entrance_date)[:10] if pd.notna(entrance_date) else 'N/A',
                    'expected_value': f'{data_latest_date.strftime("%Y-%m-%d")} 이전',
                    'severity': 'critical',
                    'description': f'입사일이 데이터 기준일({data_latest_date.strftime("%Y-%m-%d")}) 이후',
                    'suggested_action': f'날짜 형식 확인 및 수정 (정확한 형식: YYYY-MM-DD, 예: {data_latest_date.strftime("%Y-%m-%d")})'
                })
        
        if 'Stop working Date' in df.columns and 'Entrance Date' in df.columns:
            # Stop date before entrance date
            invalid_stop = df[
                (df['Stop working Date'].notna()) & 
                (df['Entrance Date'].notna()) &
                (df['Stop working Date'] < df['Entrance Date'])
            ]
            for _, row in invalid_stop.iterrows():
                self.add_error('temporal_errors', {
                    'id': row.get('Employee No', row.get('ID No', 'N/A')),
                    'name': row.get('Full Name', row.get('Name', 'N/A')),
                    'error_type': 'Invalid Date Sequence',
                    'error_column': 'Stop working Date',
                    'error_value': f"Stop: {row['Stop working Date']}, Enter: {row['Entrance Date']}",
                    'expected_value': 'Stop Date >= Entrance Date',
                    'severity': 'critical',
                    'description': 'Employee left before joining',
                    'suggested_action': 'Correct date sequence',
                    'is_resigned': True  # 퇴사자 표식을 위한 플래그
                })
                
    def detect_type_errors(self, df):
        """TYPE 분류 오류 감지"""
        print("  🏷️ Detecting TYPE classification errors...")
        
        type_column = 'ROLE TYPE STD' if 'ROLE TYPE STD' in df.columns else 'TYPE'
        
        if type_column in df.columns:
            # Missing TYPE
            missing_type = df[df[type_column].isna() | (df[type_column] == '')]
            for _, row in missing_type.iterrows():
                self.add_error('type_errors', {
                    'id': row.get('Employee No', row.get('ID No', 'N/A')),
                    'name': row.get('Full Name', row.get('Name', 'N/A')),
                    'error_type': 'Missing TYPE',
                    'error_column': type_column,
                    'error_value': 'NULL/Empty',
                    'expected_value': 'TYPE-1, TYPE-2, or TYPE-3',
                    'severity': 'critical',
                    'description': 'TYPE classification is missing',
                    'suggested_action': 'Assign appropriate TYPE'
                })
            
            # Invalid TYPE values
            valid_types = ['TYPE-1', 'TYPE-2', 'TYPE-3']
            invalid_type = df[
                df[type_column].notna() & 
                ~df[type_column].isin(valid_types)
            ]
            for _, row in invalid_type.iterrows():
                self.add_error('type_errors', {
                    'id': row.get('Employee No', row.get('ID No', 'N/A')),
                    'name': row.get('Full Name', row.get('Name', 'N/A')),
                    'error_type': 'Invalid TYPE',
                    'error_column': type_column,
                    'error_value': row[type_column],
                    'expected_value': 'TYPE-1, TYPE-2, or TYPE-3',
                    'severity': 'critical',
                    'description': f'Invalid TYPE value: {row[type_column]}',
                    'suggested_action': 'Correct to valid TYPE'
                })
            
            # TYPE Mismatch with position mapping
            self.detect_type_position_mismatch(df, type_column)
                
    def detect_type_position_mismatch(self, df, type_column):
        """직급과 TYPE 매핑 불일치 감지"""
        print("    🔍 Checking TYPE-Position mapping consistency...")
        
        # Load team structure mapping
        team_structure_path = 'HR info/team_structure_updated.json'
        position_matrix_path = 'config_files/position_condition_matrix.json'
        
        if os.path.exists(team_structure_path):
            with open(team_structure_path, 'r', encoding='utf-8') as f:
                team_structure = json.load(f)
                
            # Create mapping dictionary from team_structure
            position_to_type = {}
            for entry in team_structure.get('positions', []):
                key = (
                    entry.get('position_1st', ''),
                    entry.get('position_2nd', ''),
                    entry.get('position_3rd', ''),
                    entry.get('final_code', '')
                )
                expected_type = entry.get('role_type', '')
                if expected_type:
                    position_to_type[key] = expected_type
                    
            # Also load from position_condition_matrix if exists
            if os.path.exists(position_matrix_path):
                with open(position_matrix_path, 'r', encoding='utf-8') as f:
                    position_matrix = json.load(f)
                    
                # Build mapping from position matrix patterns
                for type_key, type_data in position_matrix.get('position_matrix', {}).items():
                    if isinstance(type_data, dict):
                        for position_key, position_data in type_data.items():
                            if position_key != 'default' and isinstance(position_data, dict):
                                patterns = position_data.get('patterns', [])
                                for pattern in patterns:
                                    # Map specific position patterns to TYPE
                                    if pattern == 'GROUP LEADER':
                                        # GROUP LEADER is TYPE-1 in TYPE-1 section, TYPE-2 in TYPE-2 section
                                        # Need to check context
                                        pass
            
            # Check each employee's TYPE against expected mapping
            for _, row in df.iterrows():
                actual_type = row.get(type_column, '')
                
                # Try to match using different column combinations
                position_1st = row.get('Position 1st', row.get('position_1st', ''))
                position_2nd = row.get('Position 2nd', row.get('position_2nd', ''))
                position_3rd = row.get('Position 3rd', row.get('position_3rd', ''))
                final_code = row.get('Final Code', row.get('final_code', ''))
                
                # Also check Position column which might contain the role
                position = row.get('Position', row.get('직급', ''))
                
                # Create lookup key
                lookup_key = (position_1st, position_2nd, position_3rd, final_code)
                
                # Check if we have an expected TYPE for this position combination
                expected_type = None
                
                # First try exact match with team_structure
                if lookup_key in position_to_type:
                    expected_type = position_to_type[lookup_key]
                
                # Special case handling based on user's example
                # GROUP LEADER with final_code Q should be TYPE-2
                if position_1st == 'GROUP LEADER' and final_code == 'Q':
                    expected_type = 'TYPE-2'
                elif position and 'GROUP LEADER' in position.upper() and final_code == 'Q':
                    expected_type = 'TYPE-2'
                    
                # Check position_matrix patterns for more general rules
                if not expected_type and position:
                    position_upper = position.upper()
                    
                    # TYPE-1 positions
                    type1_positions = ['MANAGER', 'A.MANAGER', 'ASSISTANT MANAGER', '(V) SUPERVISOR', 
                                      'V.SUPERVISOR', 'V SUPERVISOR', 'AQL INSPECTOR', 'CFA CERTIFIED',
                                      'ASSEMBLY INSPECTOR', 'AUDIT & TRAINING', 'MODEL MASTER', 'SAMPLE']
                    
                    # TYPE-2 positions 
                    type2_positions = ['BOTTOM INSPECTOR', 'CUTTING INSPECTOR', 'MTL INSPECTOR', 
                                      'MATERIAL INSPECTOR', 'OCPT STFF', 'OCPT STAFF', 'OSC INSPECTOR',
                                      'QA TEAM', 'QUALITY ASSURANCE', 'RQC', 'RANDOM QUALITY CHECK',
                                      'STITCHING INSPECTOR']
                    
                    # TYPE-3 positions
                    type3_positions = ['NEW QIP MEMBER', 'NEW MEMBER', '신입']
                    
                    for pos in type1_positions:
                        if pos in position_upper:
                            expected_type = 'TYPE-1'
                            break
                    
                    if not expected_type:
                        for pos in type2_positions:
                            if pos in position_upper:
                                expected_type = 'TYPE-2'
                                break
                    
                    if not expected_type:
                        for pos in type3_positions:
                            if pos in position_upper:
                                expected_type = 'TYPE-3'
                                break
                
                # If we found expected TYPE and it doesn't match actual
                if expected_type and actual_type and expected_type != actual_type:
                    position_info = f'{position_1st} / {position_2nd} / {position_3rd} / Code: {final_code}' if position_1st else position
                    self.add_error('type_errors', {
                        'id': row.get('Employee No', row.get('ID No', 'N/A')),
                        'name': row.get('Full Name', row.get('Name', 'N/A')),
                        'error_type': 'TYPE 매핑 불일치',
                        'error_column': type_column,
                        'error_value': actual_type,
                        'expected_value': expected_type,
                        'severity': 'critical',
                        'description': f'직급 매핑상 {expected_type}이어야 하나 {actual_type}로 등록됨',
                        'position_info': position_info,
                        'suggested_action': f'{actual_type}에서 {expected_type}로 변경 필요'
                    })
                
    def detect_position_errors(self, df):
        """직급 관련 오류 감지"""
        print("  👔 Detecting position errors...")
        
        # Load position matrix if exists
        position_matrix_path = 'config_files/position_condition_matrix.json'
        if os.path.exists(position_matrix_path):
            with open(position_matrix_path, 'r', encoding='utf-8') as f:
                position_matrix = json.load(f)
                valid_positions = position_matrix.get('position_definitions', {}).keys()
                
                if 'Position' in df.columns or '직급' in df.columns:
                    pos_col = 'Position' if 'Position' in df.columns else '직급'
                    
                    # Positions not in matrix
                    for _, row in df.iterrows():
                        position = row.get(pos_col, '')
                        if position and position not in valid_positions:
                            self.add_error('position_errors', {
                                'id': row.get('ID No', 'N/A'),
                                'name': row.get('Name', 'N/A'),
                                'error_type': 'Unknown Position',
                                'error_column': pos_col,
                                'error_value': position,
                                'expected_value': 'Valid position from matrix',
                                'severity': 'warning',
                                'description': f'Position not in configuration: {position}',
                                'suggested_action': 'Add to position matrix or correct position'
                            })
                            
    def detect_team_errors(self, df):
        """팀 관련 오류 감지"""
        print("  👥 Detecting team errors...")
        
        # Known team name variations that should be standardized
        team_variations = {
            'OSC TEAM': 'OSC',
            'ASSEMBLEY': 'ASSEMBLY',
            'STICHING': 'STITCHING'
        }
        
        team_col = None
        for col in ['Team', 'Department', '부서', 'TEAM']:
            if col in df.columns:
                team_col = col
                break
                
        if team_col:
            for _, row in df.iterrows():
                team = row.get(team_col, '')
                if team in team_variations:
                    self.add_error('team_errors', {
                        'id': row.get('ID No', 'N/A'),
                        'name': row.get('Name', 'N/A'),
                        'error_type': 'Inconsistent Team Name',
                        'error_column': team_col,
                        'error_value': team,
                        'expected_value': team_variations[team],
                        'severity': 'warning',
                        'description': f'Team name variation: {team}',
                        'suggested_action': f'Standardize to {team_variations[team]}'
                    })
                    
    def detect_attendance_errors(self, df):
        """출근 데이터 오류 감지 - attendance CSV 파일 기반"""
        print("  📊 Detecting attendance errors based on actual attendance CSV data...")
        
        # attendance CSV 파일 읽기
        attendance_file = 'input_files/attendance/converted/attendance data august_converted.csv'
        attendance_df = None
        
        try:
            attendance_df = pd.read_csv(attendance_file, encoding='utf-8-sig')
            print(f"    ✓ Loaded attendance data: {len(attendance_df)} records")
        except Exception as e:
            print(f"    ⚠️ Could not read attendance file: {e}")
            # attendance 파일 없으면 기존 로직으로 fallback
            
        if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
            for _, row in df.iterrows():
                employee_id = row.get('Employee No', row.get('ID No', 'N/A'))
                total_days = row.get('Total Working Days', 0)
                actual_days = row.get('Actual Working Days', 0)
                
                # Skip if no working days data
                if pd.isna(total_days) or total_days == 0:
                    continue
                
                # attendance CSV에서 해당 직원 데이터 확인
                expected_total_days = None
                attendance_dates = []
                actual_working_count = 0
                
                if attendance_df is not None and 'ID No' in attendance_df.columns:
                    employee_attendance = attendance_df[attendance_df['ID No'] == employee_id]
                    attendance_data_count = len(employee_attendance)
                    
                    if attendance_data_count > 0:
                        # 실제 데이터 개수가 Total Working Days여야 함
                        expected_total_days = attendance_data_count
                        
                        # 출근 날짜 리스트
                        if 'Work Date' in employee_attendance.columns:
                            employee_attendance['Work Date'] = pd.to_datetime(
                                employee_attendance['Work Date'], 
                                format='%Y.%m.%d', 
                                errors='coerce'
                            )
                            attendance_dates = employee_attendance['Work Date'].dt.strftime('%Y-%m-%d').tolist()
                        
                        # 실제 출근(Đi làm) 횟수
                        if 'compAdd' in employee_attendance.columns:
                            actual_working_count = (employee_attendance['compAdd'] == 'Đi làm').sum()
                
                # 오류 조건 체크
                error_conditions = []
                
                # 1. Actual > Total 체크
                if actual_days > total_days:
                    error_conditions.append(f"Actual ({actual_days}) > Total ({total_days})")
                
                # 2. Total이 attendance 데이터 개수와 다른 경우
                if expected_total_days is not None and total_days != expected_total_days:
                    error_conditions.append(f"Total ({total_days}) ≠ Attendance data count ({expected_total_days})")
                
                # 오류가 있으면 기록
                if error_conditions:
                    stop_date = row.get('Stop working Date', pd.NaT)
                    entrance_date = row.get('Entrance Date', pd.NaT)
                    
                    self.add_error('attendance_errors', {
                        'id': employee_id,
                        'name': row.get('Full Name', row.get('Name', 'N/A')),
                        'error_type': 'Invalid Attendance - Data Mismatch',
                        'error_column': 'Total Working Days vs Attendance Data',
                        'error_value': f"Total: {total_days}, Actual: {actual_days}, Data Count: {expected_total_days if expected_total_days else 'N/A'}",
                        'expected_value': f'Total should be {expected_total_days if expected_total_days else "based on attendance CSV"}',
                        'severity': 'critical',
                        'description': ' | '.join(error_conditions),
                        'suggested_action': f'Update Total Working Days to {expected_total_days if expected_total_days else "match attendance data"}',
                        'detailed_analysis': {
                            'entrance_date': str(entrance_date) if pd.notna(entrance_date) else None,
                            'stop_date': str(stop_date) if pd.notna(stop_date) else None,
                            'month_start': str(self.month_start),
                            'month_end': str(self.month_end),
                            'actual_working_days': actual_days,
                            'recorded_total_days': total_days,
                            'attendance_data_count': expected_total_days if expected_total_days else 0,
                            'actual_working_count': actual_working_count,
                            'sample_dates': attendance_dates[:5] if attendance_dates else []
                        }
                    })
                
            # Negative values check
            negative_actual = df[df['Actual Working Days'] < 0]
            for _, row in negative_actual.iterrows():
                self.add_error('attendance_errors', {
                    'id': row.get('Employee No', row.get('ID No', 'N/A')),
                    'name': row.get('Full Name', row.get('Name', 'N/A')),
                    'error_type': 'Negative Attendance',
                    'error_column': 'Actual Working Days',
                    'error_value': row['Actual Working Days'],
                    'expected_value': '>= 0',
                    'severity': 'critical',
                    'description': 'Negative working days recorded',
                    'suggested_action': 'Correct attendance data - negative values are invalid'
                })
                
    def detect_duplicate_errors(self, df):
        """중복 및 ID 오류 감지"""
        print("  🔄 Detecting duplicate and ID errors...")
        
        if 'ID No' in df.columns:
            # Duplicate IDs
            duplicate_ids = df[df.duplicated('ID No', keep=False)]
            if not duplicate_ids.empty:
                id_groups = duplicate_ids.groupby('ID No')
                for id_no, group in id_groups:
                    names = group['Name'].unique() if 'Name' in group.columns else []
                    self.add_error('duplicate_errors', {
                        'id': id_no,
                        'name': ', '.join([str(n) for n in names]),
                        'error_type': 'Duplicate ID',
                        'error_column': 'ID No',
                        'error_value': f'{len(group)} occurrences',
                        'expected_value': 'Unique ID',
                        'severity': 'critical',
                        'description': f'ID appears {len(group)} times with names: {names}',
                        'suggested_action': 'Resolve duplicate IDs'
                    })
                    
            # Missing IDs
            missing_ids = df[df['ID No'].isna() | (df['ID No'] == '')]
            for _, row in missing_ids.iterrows():
                self.add_error('duplicate_errors', {
                    'id': 'MISSING',
                    'name': row.get('Name', 'N/A'),
                    'error_type': 'Missing ID',
                    'error_column': 'ID No',
                    'error_value': 'NULL/Empty',
                    'expected_value': 'Valid ID',
                    'severity': 'critical',
                    'description': 'Employee ID is missing',
                    'suggested_action': 'Assign employee ID'
                })
                
    def calculate_summary(self):
        """오류 요약 계산"""
        total = 0
        for category in ['temporal_errors', 'type_errors', 'position_errors', 
                        'team_errors', 'attendance_errors', 'duplicate_errors']:
            total += len(self.errors[category])
        
        self.errors['summary']['total_errors'] = total
        
        print(f"\n📊 Error Detection Complete:")
        print(f"  Total Errors: {total}")
        print(f"  Critical: {self.errors['summary']['critical']}")
        print(f"  Warning: {self.errors['summary']['warning']}")
        print(f"  Info: {self.errors['summary']['info']}")
        
    def generate_error_report(self, output_path='error_report.json'):
        """오류 보고서 생성"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.errors, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n📁 Error report saved to: {output_path}")
        return self.errors


if __name__ == "__main__":
    # Test with August 2025 data
    import sys
    
    # Load data
    file_path = "input_files/2025년 8월 인센티브 지급 세부 정보.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Parse dates
        date_columns = ['Entrance Date', 'Stop working Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Run detection
        detector = DataErrorDetector(2025, 8)
        errors = detector.detect_all_errors(df)
        
        # Save report
        detector.generate_error_report('output_files/data_errors_2025_08.json')
        
        # Print sample errors
        print("\n📋 Sample Errors:")
        for category, error_list in errors.items():
            if category != 'summary' and error_list:
                print(f"\n{category.upper()}:")
                for error in error_list[:2]:  # Show first 2 of each type
                    print(f"  - {error['name']} ({error['id']}): {error['description']}")
    else:
        print(f"❌ File not found: {file_path}")