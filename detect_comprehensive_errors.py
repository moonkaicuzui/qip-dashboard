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
    
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.month_start = pd.Timestamp(year, month, 1)
        self.month_end = pd.Timestamp(year, month, 1) + pd.DateOffset(months=1) - pd.Timedelta(days=1)
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
        
        # Note: Entrance date can be after month_end because basic_manpower_data.csv 
        # is updated daily. If report is generated on Sept 15th for August,
        # employees who joined on Sept 15th will be in the data.
        # This is NOT an error - it's normal business operation.
        
        # We'll only check for clearly invalid dates (e.g., far future dates)
        # For now, we'll skip the future entrance date check entirely
        # since the business logic allows for this scenario
        
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
                    'suggested_action': 'Correct date sequence'
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