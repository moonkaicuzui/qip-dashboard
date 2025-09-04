#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HR Management Dashboard Generator v6.0 - Enhanced Version
완전히 개선된 버전 - 모든 요청사항 구현
- 주차별 트렌드 데이터 표시 수정
- 팀별 트리맵 차트 추가
- 팀별 세부 팝업창 구현
- TYPE별 인원 카드 추가
- 팀별 만근 인원 정보 추가
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import argparse
import warnings
warnings.filterwarnings('ignore')
from detect_comprehensive_errors import DataErrorDetector
from calculate_total_working_days import calculate_total_working_days_from_attendance, get_employee_attendance_data_count

class EnhancedHRDashboard:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.report_date = datetime.now()
        self.data = {
            'current': pd.DataFrame(),
            'previous': pd.DataFrame(),
            'attendance': pd.DataFrame()
        }
        self.metadata = {}
        self.weekly_data = {}
        self.team_structure = {}
        self.team_mapping = {}
        
        # Load UI configuration from JSON
        config_path = os.path.join(self.base_path, 'config_files', 'dashboard_ui_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.ui_config = json.load(f)
            
            self.colors = self.ui_config['colors']
            self.typography = self.ui_config['typography']
            self.layout = self.ui_config['layout']
            self.thresholds = self.ui_config['thresholds']
            self.animation = self.ui_config['animation']
            self.treemap_config = self.ui_config['treemap_algorithm']
            self.data_display = self.ui_config['data_display']
        except FileNotFoundError:
            print(f"⚠️ UI config file not found, using default values")
            # 기본값 설정
            self.colors = {
                'primary': '#000000',
                'secondary': '#333333',
                'success': '#28a745',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8',
                'background': '#ffffff',
                'text': '#212529',
                'text_secondary': '#6c757d',
                'border': '#dee2e6',
                'chart_colors': [
                    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
                    '#FF9FF3', '#54A0FF', '#48DBFB', '#00D2D3', '#1ABC9C'
                ]
            }
        
    def load_data(self):
        """데이터 로드 - NO FAKE DATA"""
        print(f"\n📊 Loading REAL data for {self.year}년 {self.month}월...")
        
        self.load_current_month_data()
        self.load_previous_month_data()
        self.load_attendance_data()
        self.load_team_structure()
        self.load_previous_metadata()
        self.calculate_real_weekly_data()
        
        print("✅ Real data loading complete")
        
    def filter_active_employees(self, df, target_month=None, target_year=None):
        """인센티브 대시보드와 동일한 기준으로 활성 직원 필터링
        
        Args:
            df: 원본 데이터프레임
            target_month: 대상 월 (기본값: self.month)
            target_year: 대상 년도 (기본값: self.year)
            
        Returns:
            필터링된 데이터프레임
        """
        if df.empty:
            return df
            
        # 대상 월 설정
        if target_month is None:
            target_month = self.month
        if target_year is None:
            target_year = self.year
            
        # 1단계: Employee No가 있는 실제 직원만 선택
        valid_employees = df[df['Employee No'].notna()].copy()
        
        # 2단계: 계산 월 이전 퇴사자 제외
        calc_month_start = pd.Timestamp(target_year, target_month, 1)
        
        if 'Stop working Date' in valid_employees.columns:
            # Stop working Date 파싱 (이미 파싱되어 있을 수 있음)
            if valid_employees['Stop working Date'].dtype == 'object':
                valid_employees['Stop working Date'] = pd.to_datetime(valid_employees['Stop working Date'], errors='coerce')
            
            # 활성 직원: 퇴사일이 없거나 계산 월 이후 퇴사자
            active_employees = valid_employees[
                (valid_employees['Stop working Date'].isna()) |  # 퇴사일 없는 직원
                (valid_employees['Stop working Date'] >= calc_month_start)  # 계산 월 이후 퇴사자
            ]
        else:
            active_employees = valid_employees
            
        return active_employees
    
    def load_current_month_data(self):
        """현재 월 데이터 로드"""
        try:
            month_names = {
                1: '1월', 2: '2월', 3: '3월', 4: '4월', 5: '5월', 6: '6월',
                7: '7월', 8: '8월', 9: '9월', 10: '10월', 11: '11월', 12: '12월'
            }
            
            month_str = month_names.get(self.month, f'{self.month}월')
            file_path = f"input_files/{self.year}년 {month_str} 인센티브 지급 세부 정보.csv"
            
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                
                # 날짜 파싱
                if 'Entrance Date' in df.columns:
                    df['Entrance Date'] = df['Entrance Date'].apply(self.parse_date)
                if 'Stop working Date' in df.columns:
                    df['Stop working Date'] = df['Stop working Date'].apply(self.parse_date)
                
                # attendance CSV 기반으로 Total Working Days 재계산
                total_working_days = calculate_total_working_days_from_attendance(self.year, self.month)
                
                if total_working_days is None:
                    print("  ❌ attendance 파일에서 Total Working Days를 계산할 수 없습니다.")
                    print("     attendance CSV 파일이 없거나 형식이 올바르지 않습니다.")
                    # Total Working Days 컬럼이 이미 있으면 그대로 사용
                    if 'Total Working Days' not in df.columns:
                        raise ValueError("Total Working Days를 계산할 수 없고, 기존 데이터도 없습니다.")
                    else:
                        print("     → 기존 Total Working Days 값을 사용합니다.")
                        total_working_days = 0  # 개별 계산 스킵
                
                # 각 직원의 실제 attendance 데이터 개수로 Total Working Days 업데이트
                if total_working_days > 0 and 'Employee No' in df.columns:
                    print(f"  📊 Updating Total Working Days based on attendance CSV...")
                    for idx, row in df.iterrows():
                        employee_id = row['Employee No']
                        # 각 직원의 실제 attendance 데이터 개수 가져오기
                        employee_data_count = get_employee_attendance_data_count(employee_id, self.year, self.month)
                        
                        # 데이터가 있으면 해당 개수로, 없으면 전체 유니크 날짜 수로 설정
                        if employee_data_count > 0:
                            df.at[idx, 'Total Working Days'] = employee_data_count
                        else:
                            # 데이터가 없는 직원은 전체 기준으로
                            df.at[idx, 'Total Working Days'] = total_working_days
                    
                    print(f"  ✓ Total Working Days updated based on attendance data")
                
                # 인센티브 대시보드와 동일한 기준으로 필터링
                original_count = len(df)
                df = self.filter_active_employees(df)
                filtered_count = len(df)
                
                self.data['current'] = df
                print(f"  ✓ Current month REAL data loaded: {filtered_count} active employees (from {original_count} total records)")
            else:
                print(f"  ❌ Current month data not found: {file_path}")
                self.data['current'] = pd.DataFrame()
                
        except Exception as e:
            print(f"  ❌ Error loading current month: {e}")
            self.data['current'] = pd.DataFrame()
            
    def load_previous_month_data(self):
        """이전 월 데이터 로드"""
        try:
            prev_month = self.month - 1 if self.month > 1 else 12
            prev_year = self.year if self.month > 1 else self.year - 1
            
            month_names = {
                1: '1월', 2: '2월', 3: '3월', 4: '4월', 5: '5월', 6: '6월',
                7: '7월', 8: '8월', 9: '9월', 10: '10월', 11: '11월', 12: '12월'
            }
            
            month_str = month_names.get(prev_month, f'{prev_month}월')
            file_path = f"input_files/{prev_year}년 {month_str} 인센티브 지급 세부 정보.csv"
            
            if os.path.exists(file_path):
                prev_df = pd.read_csv(file_path, encoding='utf-8-sig')
                
                # 날짜 파싱
                if 'Entrance Date' in prev_df.columns:
                    prev_df['Entrance Date'] = prev_df['Entrance Date'].apply(self.parse_date)
                if 'Stop working Date' in prev_df.columns:
                    prev_df['Stop working Date'] = prev_df['Stop working Date'].apply(self.parse_date)
                
                # 인센티브 대시보드와 동일한 기준으로 필터링 (이전 월 기준)
                original_count = len(prev_df)
                prev_df = self.filter_active_employees(prev_df, prev_month, prev_year)
                filtered_count = len(prev_df)
                
                self.data['previous'] = prev_df
                print(f"  ✓ Previous month REAL data loaded: {filtered_count} active employees (from {original_count} total records)")
            else:
                print(f"  ⚠ Previous month data not found")
                self.data['previous'] = pd.DataFrame()
                
        except Exception as e:
            print(f"  ❌ Error loading previous month: {e}")
            self.data['previous'] = pd.DataFrame()
            
    def load_attendance_data(self):
        """출결 데이터 로드"""
        try:
            month_names_korean = {
                8: '8월', 7: '7월', 6: '6월', 5: '5월', 4: '4월', 3: '3월'
            }
            
            month_str = month_names_korean.get(self.month, f'{self.month}월')
            attendance_file = f"input_files/{month_str} 출결정보 데이터.csv"
            
            if os.path.exists(attendance_file):
                self.data['attendance'] = pd.read_csv(attendance_file, encoding='utf-8-sig')
                print(f"  ✓ Attendance REAL data loaded: {len(self.data['attendance'])} records")
            else:
                print(f"  ⚠ Attendance data not found")
                self.data['attendance'] = pd.DataFrame()
                
        except Exception as e:
            print(f"  ❌ Error loading attendance: {e}")
            self.data['attendance'] = pd.DataFrame()
            
    def load_team_structure(self):
        """팀 구조 데이터 로드"""
        self.position_to_team = {}
        self.position_combo_to_team = {}
        
        # Default mappings (simplified and corrected)
        self.position_to_team = {
            # Only include unambiguous position mappings
            'HWK QIP': 'HWK QIP',
            'CUTTING INSPECTOR': 'CUTTING',
            'OFFICE INSPECTOR': 'OFFICE & OCPT',
            # Remove conflicting positions like ASSEMBLY INSPECTOR, LINE LEADER, etc.
        }
        
        try:
            # Load from JSON file
            import json
            with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
                team_structure = json.load(f)
            
            # Track position conflicts
            position_teams = {}  # position -> set of teams
            
            for position_data in team_structure.get('positions', []):
                team_name = position_data.get('team_name', '')
                position_1st = position_data.get('position_1st', '').strip()
                position_2nd = position_data.get('position_2nd', '').strip()  
                position_3rd = position_data.get('position_3rd', '').strip()
                role_category = position_data.get('role_category', '')
                
                # Position combo mapping (always accurate)
                combo_key = f"{position_1st}|{position_2nd}|{position_3rd}"
                self.position_combo_to_team[combo_key] = team_name
                
                # Track which teams each position_1st belongs to
                if position_1st:
                    if position_1st not in position_teams:
                        position_teams[position_1st] = set()
                    position_teams[position_1st].add(team_name)
            
            # Only add position mappings that are unambiguous (belong to only one team)
            for position, teams in position_teams.items():
                if len(teams) == 1:  # Unambiguous position
                    self.position_to_team[position] = list(teams)[0]
                # else: Skip positions with multiple teams (like ASSEMBLY INSPECTOR, LINE LEADER)
            
            print(f"  ✓ Team structure loaded")
            print(f"    - {len(self.position_combo_to_team)} position combinations")
            print(f"    - {len(self.position_to_team)} unambiguous positions")
            print(f"    - {len([p for p, t in position_teams.items() if len(t) > 1])} conflicting positions skipped")
            
        except FileNotFoundError:
            print(f"  ⚠ Team structure file not found, using defaults")
        except Exception as e:
            print(f"  ❌ Error loading team structure: {e}")
    def load_previous_metadata(self):
        """이전 메타데이터 로드"""
        try:
            metadata_file = f"output_files/hr_metadata_{self.year}.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"  ✓ Previous metadata loaded")
            else:
                self.metadata = {'monthly_data': {}, 'weekly_data': {}, 'team_stats': {}}
                print(f"  ℹ Starting fresh metadata")
        except Exception as e:
            print(f"  ❌ Error loading metadata: {e}")
            self.metadata = {'monthly_data': {}, 'weekly_data': {}, 'team_stats': {}}
            
    def parse_date(self, date_str):
        """날짜 파싱"""
        if pd.isna(date_str) or date_str == '' or date_str == 'nan':
            return pd.NaT
            
        date_str = str(date_str).strip()
        
        formats = [
            '%Y.%m.%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d',
            '%Y/%m/%d', '%d.%m.%Y', '%d-%m-%Y'
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt, dayfirst=('/' in fmt and fmt.index('/') < 3))
            except:
                continue
                
        try:
            return pd.to_datetime(date_str, dayfirst=True)
        except:
            return pd.NaT
            
    def create_unified_employee_filter(self, df, reference_date, filter_type='month_active'):
        """
        통합 직원 필터링 함수 - 인센티브 대시보드와 동일한 로직 사용
        
        Args:
            df: 직원 데이터 DataFrame
            reference_date: 기준 날짜 (pd.Timestamp)
            filter_type: 'month_active' (월 활성), 'week_active' (주 활성), 'all' (전체)
            
        Returns:
            활성 직원 마스크 (boolean Series)
        """
        if df.empty:
            return pd.Series([], dtype=bool)
            
        # 기본값: 모든 직원 활성
        active_mask = pd.Series([True] * len(df), index=df.index)
        
        if filter_type == 'all':
            return active_mask
            
        # 인센티브 대시보드와 동일한 로직:
        # 1. Stop working Date가 없는 직원 (현재 근무 중)
        # 2. Stop working Date가 reference_date 이후인 직원 (해당 기간에 근무)
        # 중요: 인센티브 대시보드는 입사일 필터를 적용하지 않음
        
        if 'Stop working Date' in df.columns:
            # Stop working Date 우선 사용
            active_mask = (
                df['Stop working Date'].isna() |  # 퇴사일이 없는 직원
                (df['Stop working Date'] >= reference_date)  # 기준일 이후 퇴사
            )
        elif 'RE MARK' in df.columns:
            # Stop working Date가 없으면 RE MARK 사용 (보조 지표)
            active_mask = df['RE MARK'] != 'Stop working'
            
        # 인센티브 대시보드와 동일하게 입사일 필터링을 제거
        # 해당 월 인센티브 파일에 있으면 모두 포함
                
        return active_mask
            
    def calculate_real_weekly_data(self):
        """실제 주차별 데이터 계산 (인센티브 대시보드와 동일한 필터 적용)"""
        if self.data['current'].empty:
            self.weekly_data = {}
            return
        
        # 이미 필터링된 데이터 사용
        df = self.data['current']
        
        # 실제 날짜 기반 주차 계산
        start_date = datetime(self.year, self.month, 1)
        
        week_data = {}
        for week_num in range(1, 5):
            week_start = start_date + timedelta(days=(week_num-1)*7)
            week_end = week_start + timedelta(days=6)
            
            week_key = f"Week{week_num}"
            
            # 해당 주차에 재직 중인 직원 - 통합 필터 함수 사용
            active_mask = self.create_unified_employee_filter(df, pd.Timestamp(week_start), 'week_active')
            active_employees = df[active_mask]
            
            # 신규 입사자
            new_hires = df[
                (df['Entrance Date'] >= week_start) & 
                (df['Entrance Date'] <= week_end)
            ]
            
            # 퇴사자
            resignations = df[
                (df['Stop working Date'] >= week_start) & 
                (df['Stop working Date'] <= week_end)
            ]
            
            # 출근율 계산
            if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
                attendance_rate = (
                    active_employees['Actual Working Days'].sum() / 
                    active_employees['Total Working Days'].sum() * 100
                    if active_employees['Total Working Days'].sum() > 0 else 0
                )
            else:
                attendance_rate = 0
                
            week_data[week_key] = {
                'total_employees': len(active_employees),
                'attendance_rate': round(attendance_rate, 2),
                'absence_rate': round(100 - attendance_rate, 2),
                'new_hires': len(new_hires),
                'resignations': len(resignations)
            }
            
        # 현재 월 주차별 데이터 저장
        month_key = f"{self.year}_{self.month:02d}"
        self.weekly_data = week_data
        
    def calculate_real_hr_metrics(self):
        """실제 HR 메트릭 계산"""
        if self.data['current'].empty:
            return {}
            
        df = self.data['current']
        metrics = {}
        
        # 활성 직원만 필터링 - 해당 월 시작일 기준으로 필터링
        # Stop working Date를 우선시하고, RE MARK는 보조 지표로 사용
        month_start = pd.Timestamp(self.year, self.month, 1)
        month_end = pd.Timestamp(self.year, self.month, 1) + pd.DateOffset(months=1) - pd.Timedelta(days=1)
        
        # 데이터 오류 감지: 미래 입사일을 가진 직원
        error_employees = pd.DataFrame()
        if 'Entrance Date' in df.columns:
            error_employees = df[df['Entrance Date'] > month_end]
            metrics['error_count'] = len(error_employees)
            metrics['error_rate'] = (metrics['error_count'] / len(df) * 100) if len(df) > 0 else 0
            
            # 에러 직원 정보 저장 (디버깅용)
            if len(error_employees) > 0:
                print(f"  ⚠️ 데이터 오류: {len(error_employees)}명의 직원이 미래 입사일을 가지고 있습니다")
                for _, emp in error_employees.head(5).iterrows():
                    print(f"    - {emp.get('Name', 'N/A')} - 입사일: {emp.get('Entrance Date', 'N/A')}")
        else:
            metrics['error_count'] = 0
            metrics['error_rate'] = 0
        
        # 통합 필터 함수 사용 (에러 직원 제외)
        active_mask = self.create_unified_employee_filter(df, month_start, 'month_active')
        # 에러 직원 제외
        if 'Entrance Date' in df.columns:
            active_mask = active_mask & (df['Entrance Date'] <= month_end)
        
        active_employees = df[active_mask]
        metrics['total_employees'] = len(active_employees)
        
        # TYPE별 카운트 - 실제 칼럼명 사용
        type_column = 'ROLE TYPE STD' if 'ROLE TYPE STD' in active_employees.columns else 'TYPE'
        if type_column in active_employees.columns:
            metrics['type1_count'] = str(len(active_employees[active_employees[type_column] == 'TYPE-1']))
            metrics['type2_count'] = str(len(active_employees[active_employees[type_column] == 'TYPE-2']))
            metrics['type3_count'] = str(len(active_employees[active_employees[type_column] == 'TYPE-3']))
        else:
            metrics['type1_count'] = "0"
            metrics['type2_count'] = "0"
            metrics['type3_count'] = "0"
            
        # 출근율
        if 'Actual Working Days' in active_employees.columns and 'Total Working Days' in active_employees.columns:
            total_actual = active_employees['Actual Working Days'].sum()
            total_required = active_employees['Total Working Days'].sum()
            metrics['attendance_rate'] = (total_actual / total_required * 100) if total_required > 0 else 0
            metrics['absence_rate'] = 100 - metrics['attendance_rate']
            
            # 결근자 수
            absence_employees = active_employees[
                active_employees['Actual Working Days'] < active_employees['Total Working Days']
            ]
            metrics['absence_count'] = len(absence_employees)
        else:
            metrics['attendance_rate'] = 0
            metrics['absence_rate'] = 0
            metrics['absence_count'] = 0
            
        # 퇴사율
        if 'Stop working Date' in df.columns:
            current_month_resignations = df[
                (df['Stop working Date'].dt.month == self.month) & 
                (df['Stop working Date'].dt.year == self.year)
            ]
            metrics['resignation_count'] = len(current_month_resignations)
            metrics['resignation_rate'] = (
                metrics['resignation_count'] / metrics['total_employees'] * 100 
                if metrics['total_employees'] > 0 else 0
            )
        else:
            metrics['resignation_count'] = 0
            metrics['resignation_rate'] = 0
            
        # 최근 30일 입사자
        thirty_days_ago = self.report_date - timedelta(days=30)
        if 'Entrance Date' in df.columns:
            recent_hires = active_employees[
                active_employees['Entrance Date'] >= thirty_days_ago
            ]
            metrics['recent_hires'] = len(recent_hires)
            metrics['recent_hires_rate'] = (
                metrics['recent_hires'] / metrics['total_employees'] * 100 
                if metrics['total_employees'] > 0 else 0
            )
        else:
            metrics['recent_hires'] = 0
            metrics['recent_hires_rate'] = 0
            
        # 최근 30일내 퇴사한 신입
        if 'Entrance Date' in df.columns and 'Stop working Date' in df.columns:
            new_resignations = df[
                (df['Stop working Date'].notna()) &
                ((df['Stop working Date'] - df['Entrance Date']).dt.days <= 30)
            ]
            metrics['recent_resignations'] = len(new_resignations)
            metrics['recent_resignation_rate'] = (
                metrics['recent_resignations'] / metrics['recent_hires'] * 100 
                if metrics['recent_hires'] > 0 else 0
            )
        else:
            metrics['recent_resignations'] = 0
            metrics['recent_resignation_rate'] = 0
            
        # 60일 미만 근무자
        sixty_days_ago = self.report_date - timedelta(days=60)
        if 'Entrance Date' in active_employees.columns:
            under_60_days = active_employees[
                active_employees['Entrance Date'] >= sixty_days_ago
            ]
            metrics['under_60_days'] = len(under_60_days)
            metrics['under_60_days_rate'] = (
                metrics['under_60_days'] / metrics['total_employees'] * 100 
                if metrics['total_employees'] > 0 else 0
            )
        else:
            metrics['under_60_days'] = 0
            metrics['under_60_days_rate'] = 0
            
        # 보직 부여 후 퇴사자
        if 'Entrance Date' in df.columns and 'Stop working Date' in df.columns:
            post_assignment_resignations = df[
                (df['Stop working Date'].notna()) &
                ((df['Stop working Date'] - df['Entrance Date']).dt.days > 30) &
                ((df['Stop working Date'] - df['Entrance Date']).dt.days <= 60)
            ]
            metrics['post_assignment_resignations'] = len(post_assignment_resignations)
            metrics['post_assignment_resignation_rate'] = (
                metrics['post_assignment_resignations'] / metrics['under_60_days'] * 100 
                if metrics['under_60_days'] > 0 else 0
            )
        else:
            metrics['post_assignment_resignations'] = 0
            metrics['post_assignment_resignation_rate'] = 0
            
        # 만근자
        if 'Actual Working Days' in active_employees.columns and 'Total Working Days' in active_employees.columns:
            full_attendance = active_employees[
                (active_employees['Actual Working Days'] == active_employees['Total Working Days']) &
                (active_employees['Total Working Days'] > 0)
            ]
            metrics['full_attendance_count'] = len(full_attendance)
            metrics['full_attendance_rate'] = (
                metrics['full_attendance_count'] / metrics['total_employees'] * 100 
                if metrics['total_employees'] > 0 else 0
            )
        else:
            metrics['full_attendance_count'] = 0
            metrics['full_attendance_rate'] = 0
            
        # 장기근속자 (1년 이상)
        one_year_ago = self.report_date - timedelta(days=365)
        if 'Entrance Date' in active_employees.columns:
            long_term_employees = active_employees[
                active_employees['Entrance Date'] <= one_year_ago
            ]
            metrics['long_term_count'] = len(long_term_employees)
            metrics['long_term_rate'] = (
                metrics['long_term_count'] / metrics['total_employees'] * 100 
                if metrics['total_employees'] > 0 else 0
            )
        else:
            metrics['long_term_count'] = 0
            metrics['long_term_rate'] = 0
            
        return metrics
        
    def calculate_team_statistics(self):
        """팀별 통계 계산"""
        if self.data['current'].empty:
            return {}
            
        df = self.data['current']
        team_stats = {}
        
        # 팀 칼럼 찾기 - 개선된 매핑 로직 적용 (July와 동일)
        df['real_team'] = None
        
        # ASSEMBLY INSPECTOR 특별 처리 - position_3rd로 구분
        assembly_mask = (df['QIP POSITION 1ST  NAME'] == 'ASSEMBLY INSPECTOR')
        if 'QIP POSITION 3RD  NAME' in df.columns:
            repacking_keywords = ['REPACKING', 'REPACK']
            assembly_repacking_mask = assembly_mask & df['QIP POSITION 3RD  NAME'].str.contains('|'.join(repacking_keywords), case=False, na=False)
            df.loc[assembly_repacking_mask, 'real_team'] = 'REPACKING'
            assembly_not_repacking = assembly_mask & ~assembly_repacking_mask
            df.loc[assembly_not_repacking, 'real_team'] = 'ASSEMBLY'
        else:
            df.loc[assembly_mask, 'real_team'] = 'ASSEMBLY'
        
        # LINE LEADER 특별 처리 - position_2nd 기반 매핑
        line_leader_mask = (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
        if 'QIP POSITION 2ND  NAME' in df.columns:
            df.loc[line_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('GROUP LEADER SUCCESSOR', case=False, na=False), 'real_team'] = 'STITCHING'
            df.loc[line_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('SUVERVISOR SUCCESSOR', case=False, na=False), 'real_team'] = 'CUTTING'
            df.loc[line_leader_mask & (df['QIP POSITION 2ND  NAME'] == 'LINE LEADER'), 'real_team'] = 'OSC'
            df.loc[line_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('HAPPO MTL', case=False, na=False), 'real_team'] = 'MTL'
        
        # GROUP LEADER 특별 처리 - position_2nd 기반 매핑
        group_leader_mask = (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
        if 'QIP POSITION 2ND  NAME' in df.columns:
            df.loc[group_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('HEAD/', case=False, na=False), 'real_team'] = 'STITCHING'
            df.loc[group_leader_mask & (df['QIP POSITION 2ND  NAME'] == 'GROUP LEADER'), 'real_team'] = 'ASSEMBLY'
            df.loc[group_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('REPORT TEAM', case=False, na=False), 'real_team'] = 'OFFICE & OCPT'
        
        # (V) SUPERVISOR 특별 처리 - position_3rd 기반 매핑
        supervisor_mask = (df['QIP POSITION 1ST  NAME'] == '(V) SUPERVISOR')
        if 'QIP POSITION 3RD  NAME' in df.columns:
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', case=False, na=False), 'real_team'] = 'ASSEMBLY'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('CUTTING', case=False, na=False), 'real_team'] = 'CUTTING'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('OCPT|OFFICE', case=False, na=False), 'real_team'] = 'OFFICE & OCPT'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('OSC|MTL', case=False, na=False), 'real_team'] = 'OSC'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('QA TEAM', case=False, na=False), 'real_team'] = 'QA'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('STITCHING', case=False, na=False), 'real_team'] = 'STITCHING'
        
        # A.MANAGER 특별 처리 - position_3rd 기반 매핑
        manager_mask = (df['QIP POSITION 1ST  NAME'] == 'A.MANAGER')
        if 'QIP POSITION 3RD  NAME' in df.columns:
            df.loc[manager_mask & df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', case=False, na=False), 'real_team'] = 'ASSEMBLY'
            df.loc[manager_mask & df['QIP POSITION 3RD  NAME'].str.contains('STITCHING', case=False, na=False), 'real_team'] = 'STITCHING'
        
        # NEW QIP MEMBER 처리
        new_member_mask = df['QIP POSITION 1ST  NAME'].str.contains('NEW QIP MEMBER', case=False, na=False)
        df.loc[new_member_mask, 'real_team'] = 'NEW'
        
        # 나머지 포지션에 대한 매핑 - position 조합 우선 사용
        for idx, row in df.iterrows():
            if pd.notna(df.at[idx, 'real_team']):  # 이미 매핑된 경우 건너뜀
                continue
                
            pos1 = str(row.get('QIP POSITION 1ST  NAME', '')).strip()
            pos2 = str(row.get('QIP POSITION 2ND  NAME', '')).strip()
            pos3 = str(row.get('QIP POSITION 3RD  NAME', '')).strip()
            
            # Position 조합 키 생성
            combo_key = f"{pos1}|{pos2}|{pos3}"
            
            # 조합 키로 팀 찾기
            if combo_key in self.position_combo_to_team:
                df.at[idx, 'real_team'] = self.position_combo_to_team[combo_key]
        
        # 여전히 매핑되지 않은 경우 개별 position으로 시도
        position_columns = [
            'QIP POSITION 1ST  NAME',
            'QIP POSITION 2ND  NAME',
            'QIP POSITION 3RD  NAME',
            'FINAL QIP POSITION NAME CODE'
        ]
        
        for col in position_columns:
            if col in df.columns:
                unmapped_mask = df['real_team'].isna()
                if unmapped_mask.any():
                    temp_mapping = df.loc[unmapped_mask, col].map(self.position_to_team)
                    df.loc[unmapped_mask, 'real_team'] = df.loc[unmapped_mask, 'real_team'].combine_first(temp_mapping)
        
        # 여전히 매핑되지 않은 경우 기본값 설정
        df['real_team'] = df['real_team'].fillna('Team Unidentified')
        team_column = 'real_team'
            
        # 팀별 통계
        for team in df[team_column].dropna().unique():
            team_df = df[df[team_column] == team]
            
            # 활성 직원만 - 해당 월 시작일 기준으로 필터링
            # Stop working Date를 우선시하고, RE MARK는 보조 지표로 사용
            month_start = pd.Timestamp(self.year, self.month, 1)
            
            # 통합 필터 함수 사용
            active_mask = self.create_unified_employee_filter(team_df, month_start, 'month_active')
            active_team = team_df[active_mask]
            
            # 만근 직원 계산
            full_attendance_count = 0
            if 'Actual Working Days' in active_team.columns and 'Total Working Days' in active_team.columns:
                full_attendance = active_team[
                    (active_team['Actual Working Days'] == active_team['Total Working Days']) &
                    (active_team['Total Working Days'] > 0)
                ]
                full_attendance_count = len(full_attendance)
            
            team_stats[team] = {
                'total': len(active_team),
                'resignations': len(team_df[team_df['Stop working Date'].notna()]) if 'Stop working Date' in team_df.columns else 0,
                'attendance_rate': (
                    active_team['Actual Working Days'].sum() / active_team['Total Working Days'].sum() * 100
                    if 'Total Working Days' in active_team.columns and active_team['Total Working Days'].sum() > 0 else 0
                ),
                'new_hires': len(active_team[active_team['Entrance Date'] >= (self.report_date - timedelta(days=30))])
                    if 'Entrance Date' in active_team.columns else 0,
                'full_attendance_count': full_attendance_count,
                'full_attendance_rate': (full_attendance_count / len(active_team) * 100) if len(active_team) > 0 else 0
            }
            
        return team_stats
        
    def calculate_absence_reasons(self):
        """결근 사유 분석"""
        if self.data['attendance'].empty:
            return {}
            
        attendance_df = self.data['attendance']
        
        # 결근 사유 칼럼 찾기
        reason_columns = ['결근사유', 'Absence Reason', 'REASON', '사유']
        reason_column = None
        
        for col in reason_columns:
            if col in attendance_df.columns:
                reason_column = col
                break
                
        if not reason_column:
            return {}
            
        # 결근 사유별 카운트
        absence_reasons = attendance_df[reason_column].value_counts().to_dict()
        
        return absence_reasons
        
    def calculate_data_period(self):
        """데이터 기간 계산 - 실제 출근 데이터 기반"""
        start_date = datetime(self.year, self.month, 1)
        
        # 실제 데이터의 마지막 날짜 가져오기
        latest_day = self.calculate_latest_data_date()
        end_date = datetime(self.year, self.month, latest_day)
            
        return f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}"
        
    def calculate_previous_team_statistics(self):
        """이전 월(7월) 팀별 통계 계산"""
        if self.data['previous'].empty:
            return {}
            
        df = self.data['previous'].copy()
        team_stats = {}
        
        # 팀 칼럼 찾기 - 개선된 매핑 로직 적용
        df['real_team'] = None
        
        # ASSEMBLY INSPECTOR 특별 처리 - 7월 데이터 특성 고려
        # position_3rd가 ASSEMBLY LINE 관련이면 ASSEMBLY, REPACKING LINE 관련이면 REPACKING
        assembly_mask = (df['QIP POSITION 1ST  NAME'] == 'ASSEMBLY INSPECTOR')
        
        # position_3rd로 구분
        if 'QIP POSITION 3RD  NAME' in df.columns:
            # REPACKING 관련 키워드
            repacking_keywords = ['REPACKING', 'REPACK']
            assembly_repacking_mask = assembly_mask & df['QIP POSITION 3RD  NAME'].str.contains('|'.join(repacking_keywords), case=False, na=False)
            df.loc[assembly_repacking_mask, 'real_team'] = 'REPACKING'
            
            # 나머지 ASSEMBLY INSPECTOR는 ASSEMBLY
            assembly_not_repacking = assembly_mask & ~assembly_repacking_mask
            df.loc[assembly_not_repacking, 'real_team'] = 'ASSEMBLY'
        else:
            # position_3rd가 없으면 모두 ASSEMBLY로
            df.loc[assembly_mask, 'real_team'] = 'ASSEMBLY'
        
        # LINE LEADER 특별 처리 - position_2nd 기반 매핑
        line_leader_mask = (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
        if 'QIP POSITION 2ND  NAME' in df.columns:
            # 각 position_2nd에 따른 팀 매핑
            df.loc[line_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('GROUP LEADER SUCCESSOR', case=False, na=False), 'real_team'] = 'STITCHING'
            df.loc[line_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('SUVERVISOR SUCCESSOR', case=False, na=False), 'real_team'] = 'CUTTING'
            df.loc[line_leader_mask & (df['QIP POSITION 2ND  NAME'] == 'LINE LEADER'), 'real_team'] = 'OSC'
            df.loc[line_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('HAPPO MTL', case=False, na=False), 'real_team'] = 'MTL'
        
        # GROUP LEADER 특별 처리 - position_2nd 기반 매핑
        group_leader_mask = (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
        if 'QIP POSITION 2ND  NAME' in df.columns:
            df.loc[group_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('HEAD/', case=False, na=False), 'real_team'] = 'STITCHING'
            df.loc[group_leader_mask & (df['QIP POSITION 2ND  NAME'] == 'GROUP LEADER'), 'real_team'] = 'ASSEMBLY'
            df.loc[group_leader_mask & df['QIP POSITION 2ND  NAME'].str.contains('REPORT TEAM', case=False, na=False), 'real_team'] = 'OFFICE & OCPT'
        
        # (V) SUPERVISOR 특별 처리 - position_3rd 기반 매핑
        supervisor_mask = (df['QIP POSITION 1ST  NAME'] == '(V) SUPERVISOR')
        if 'QIP POSITION 3RD  NAME' in df.columns:
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', case=False, na=False), 'real_team'] = 'ASSEMBLY'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('CUTTING', case=False, na=False), 'real_team'] = 'CUTTING'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('OCPT|OFFICE', case=False, na=False), 'real_team'] = 'OFFICE & OCPT'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('OSC|MTL', case=False, na=False), 'real_team'] = 'OSC'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('QA TEAM', case=False, na=False), 'real_team'] = 'QA'
            df.loc[supervisor_mask & df['QIP POSITION 3RD  NAME'].str.contains('STITCHING', case=False, na=False), 'real_team'] = 'STITCHING'
        
        # A.MANAGER 특별 처리 - position_3rd 기반 매핑
        manager_mask = (df['QIP POSITION 1ST  NAME'] == 'A.MANAGER')
        if 'QIP POSITION 3RD  NAME' in df.columns:
            df.loc[manager_mask & df['QIP POSITION 3RD  NAME'].str.contains('ASSEMBLY', case=False, na=False), 'real_team'] = 'ASSEMBLY'
            df.loc[manager_mask & df['QIP POSITION 3RD  NAME'].str.contains('STITCHING', case=False, na=False), 'real_team'] = 'STITCHING'
        
        # NEW QIP MEMBER 처리
        new_member_mask = df['QIP POSITION 1ST  NAME'].str.contains('NEW QIP MEMBER', case=False, na=False)
        df.loc[new_member_mask, 'real_team'] = 'NEW'
        
        # 나머지 포지션에 대한 매핑
        position_columns = [
            'QIP POSITION 1ST  NAME',
            'QIP POSITION 2ND  NAME', 
            'QIP POSITION 3RD  NAME',
            'FINAL QIP POSITION NAME CODE'
        ]
        
        for col in position_columns:
            if col in df.columns:
                # 이미 매핑된 행은 건드리지 않음
                unmapped_mask = df['real_team'].isna()
                if unmapped_mask.any():
                    temp_mapping = df.loc[unmapped_mask, col].map(self.position_to_team)
                    df.loc[unmapped_mask, 'real_team'] = df.loc[unmapped_mask, 'real_team'].combine_first(temp_mapping)
        
        # 여전히 매핑되지 않은 경우 기본값 설정
        df['real_team'] = df['real_team'].fillna('Team Unidentified')
        team_column = 'real_team'
            
        # 팀별 통계
        for team in df[team_column].dropna().unique():
            team_df = df[df[team_column] == team]
            
            # 활성 직원만 - 이전 월 시작일 기준으로 필터링
            # Stop working Date를 우선시하고, RE MARK는 보조 지표로 사용
            prev_month_start = pd.Timestamp(self.year if self.month > 1 else self.year-1, 
                                           self.month-1 if self.month > 1 else 12, 1)
            
            # 통합 필터 함수 사용
            active_mask = self.create_unified_employee_filter(team_df, prev_month_start, 'month_active')
            active_team = team_df[active_mask]
            
            team_stats[team] = {
                'total': len(active_team),
                'resignations': len(team_df[team_df['Stop working Date'].notna()]) if 'Stop working Date' in team_df.columns else 0,
                'attendance_rate': (
                    active_team['Actual Working Days'].sum() / active_team['Total Working Days'].sum() * 100
                    if 'Total Working Days' in active_team.columns and active_team['Total Working Days'].sum() > 0 else 0
                ),
                'new_hires': len(active_team[
                    (active_team['Entrance Date'] >= pd.Timestamp(self.year if self.month > 1 else self.year-1, 
                                                                   self.month-1 if self.month > 1 else 12, 1))
                ]) if 'Entrance Date' in active_team.columns else 0
            }
        
        return team_stats
    
    def calculate_weekly_team_data(self):
        """주차별 팀 데이터 계산"""
        if self.data['current'].empty:
            return {}
            
        df = self.data['current'].copy()
        
        # 팀 매핑 수행 (calculate_team_statistics와 동일한 로직)
        df['real_team'] = None
        
        # 3단계 포지션 조합으로 우선 매핑
        if all(col in df.columns for col in ['QIP POSITION 1ST  NAME', 'QIP POSITION 2ND  NAME', 'QIP POSITION 3RD  NAME']):
            for idx, row in df.iterrows():
                position_1st = str(row.get('QIP POSITION 1ST  NAME', '')).strip()
                position_2nd = str(row.get('QIP POSITION 2ND  NAME', '')).strip()
                position_3rd = str(row.get('QIP POSITION 3RD  NAME', '')).strip()
                combo_key = f"{position_1st}|{position_2nd}|{position_3rd}"
                
                if combo_key in self.position_combo_to_team:
                    df.at[idx, 'real_team'] = self.position_combo_to_team[combo_key]
        
        # 특별한 포지션 매핑 처리
        special_mappings = [
            ('LINE LEADER', 'GROUP LEADER SUCCESSOR', 'STITCHING'),
            ('LINE LEADER', 'SUVERVISOR SUCCESSOR', 'CUTTING'),
            ('LINE LEADER', 'LINE LEADER', 'OSC'),
            ('GROUP LEADER', 'HEAD/ GROUP LEADER', 'BOTTOM'),
            ('GROUP LEADER', 'GROUP LEADER', 'ASSEMBLY'),
            ('GROUP LEADER', 'HEAD/ GROUP LEADER', 'STITCHING'),
            ('(V) SUPERVISOR', '(V) SUPERVISOR', 'ASSEMBLY'),
            ('(V) SUPERVISOR', '(V) SUPERVISOR', 'STITCHING'),
            ('A.MANAGER', 'A.MANAGER', 'STITCHING'),
            ('A.MANAGER', 'A.MANAGER', 'ASSEMBLY'),
        ]
        
        for position_1st, position_2nd_pattern, team in special_mappings:
            mask = (df['real_team'].isna()) & (df['QIP POSITION 1ST  NAME'] == position_1st)
            if 'QIP POSITION 2ND  NAME' in df.columns:
                mask = mask & df['QIP POSITION 2ND  NAME'].str.contains(position_2nd_pattern, case=False, na=False)
                df.loc[mask, 'real_team'] = team
        
        # 남은 포지션 매핑
        for col in ['QIP POSITION 1ST  NAME', 'QIP POSITION 2ND  NAME', 'QIP POSITION 3RD  NAME']:
            if col in df.columns:
                unmapped_mask = df['real_team'].isna()
                if unmapped_mask.any():
                    temp_mapping = df.loc[unmapped_mask, col].map(self.position_to_team)
                    df.loc[unmapped_mask, 'real_team'] = df.loc[unmapped_mask, 'real_team'].combine_first(temp_mapping)
        
        df['real_team'] = df['real_team'].fillna('Team Unidentified')
        
        # 실제 날짜 기반 주차 계산
        start_date = datetime(self.year, self.month, 1)
        weekly_team_data = {}
        
        for week_num in range(1, 5):
            week_start = start_date + timedelta(days=(week_num-1)*7)
            week_end = week_start + timedelta(days=6)
            week_key = f"Week{week_num}"
            
            # 해당 주차에 재직 중인 직원 필터링 - 통합 필터 함수 사용
            active_mask = self.create_unified_employee_filter(df, pd.Timestamp(week_start), 'week_active')
            week_df = df[active_mask]
            
            # 팀별 인원수 계산
            team_counts = week_df.groupby('real_team').size().to_dict()
            weekly_team_data[week_key] = team_counts
        
        return weekly_team_data
    
    def save_metadata(self):
        """메타데이터 저장"""
        month_key = f"{self.year}_{self.month:02d}"
        
        # 월별 데이터 저장
        self.metadata['monthly_data'][month_key] = self.calculate_real_hr_metrics()
        self.metadata['weekly_data'][month_key] = self.weekly_data
        
        # 팀별 통계 저장
        self.metadata['team_stats'] = self.metadata.get('team_stats', {})
        self.metadata['team_stats'][month_key] = self.calculate_team_statistics()
        
        # 7월 팀별 통계 재계산 - 항상 새로 계산하여 정확도 보장
        prev_month_key = f"{self.year}_{(self.month-1):02d}" if self.month > 1 else f"{self.year-1}_12"
        # 이전 월 데이터가 있으면 항상 재계산 (기존 저장된 잘못된 데이터 문제 해결)
        if not self.data['previous'].empty:
            self.metadata['team_stats'][prev_month_key] = self.calculate_previous_team_statistics()
        elif prev_month_key not in self.metadata['team_stats']:
            # 이전 월 데이터가 없으면 빈 딕셔너리
            self.metadata['team_stats'][prev_month_key] = {}
        
        # 결근 사유 저장
        self.metadata['absence_reasons'] = self.metadata.get('absence_reasons', {})
        self.metadata['absence_reasons'][month_key] = self.calculate_absence_reasons()
        
        # 현재 월과 이전 월 데이터 구조 추가 (validation 용)
        team_stats = self.calculate_team_statistics()
        self.metadata['current_month'] = {
            'total_count': len(self.data['current']) if not self.data['current'].empty else 0,
            'by_team': team_stats
        }
        
        prev_month_key = f"{self.year}_{(self.month-1):02d}" if self.month > 1 else f"{self.year-1}_12"
        self.metadata['previous_month'] = {
            'total_count': len(self.data['previous']) if not self.data['previous'].empty else 0,
            'by_team': self.metadata.get('team_stats', {}).get(prev_month_key, {})
        }
        
        # 타임스탬프 추가
        self.metadata['generation_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # JSON 파일로 저장
        metadata_file = f"output_files/hr_metadata_{self.year}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2, default=str)
            
        print(f"💾 Metadata saved to {metadata_file}")
        
    def generate_dashboard_html(self):
        """대시보드 HTML 생성"""
        metrics = self.calculate_real_hr_metrics()
        team_stats = self.calculate_team_statistics()
        absence_reasons = self.calculate_absence_reasons()
        team_members = self.load_team_members_data()  # 팀 멤버 데이터 추가
        weekly_team_data = self.calculate_weekly_team_data()  # 주차별 팀 데이터 추가
        
        # Run comprehensive error detection
        print("\n🔍 Running comprehensive error detection...")
        detector = DataErrorDetector(self.year, self.month)
        error_report = detector.detect_all_errors(self.data['current'])
        error_file = f'output_files/data_errors_{self.year}_{self.month:02d}.json'
        detector.generate_error_report(error_file)
        
        # Update metrics with comprehensive error count
        metrics['error_count'] = error_report['summary']['total_errors']
        metrics['error_rate'] = (metrics['error_count'] / len(self.data['current']) * 100) if len(self.data['current']) > 0 else 0
        
        # 이전 월 메트릭
        prev_month_key = f"{self.year if self.month > 1 else self.year-1}_{(self.month-1 if self.month > 1 else 12):02d}"
        prev_metrics = self.metadata.get('monthly_data', {}).get(prev_month_key, {})
        
        html_content = self.generate_full_html(metrics, team_stats, absence_reasons, prev_metrics, team_members, weekly_team_data, error_report)
        
        # HTML 파일 저장
        output_file = f"output_files/management_dashboard_{self.year}_{self.month:02d}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ Dashboard generated: {output_file}")
        return output_file
        
    def calculate_latest_data_date(self):
        """출근 데이터 파일에서 실제 최신 날짜 읽기 - NO HARDCODING"""
        import pandas as pd
        from calendar import monthrange
        import datetime
        import os
        
        # 출근 데이터 파일 경로 찾기
        month_names = {
            1: 'january', 2: 'february', 3: 'march', 4: 'april', 
            5: 'may', 6: 'june', 7: 'july', 8: 'august',
            9: 'september', 10: 'october', 11: 'november', 12: 'december'
        }
        
        month_name = month_names.get(self.month, f'month_{self.month}')
        
        # 우선순위: converted 폴더 -> original 폴더 -> 기본값
        attendance_files = [
            f"input_files/attendance/converted/attendance data {month_name}_converted.csv",
            f"input_files/attendance/original/attendance data {month_name}.csv",
            f"input_files/attendance data {month_name}_converted.csv",
            f"input_files/attendance data {month_name}.csv"
        ]
        
        latest_date = None
        
        for file_path in attendance_files:
            if os.path.exists(file_path):
                try:
                    # 출근 데이터 읽기
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    
                    # Work Date 컬럼 찾기
                    date_column = None
                    for col in ['Work Date', 'Date', 'Work_Date', '날짜']:
                        if col in df.columns:
                            date_column = col
                            break
                    
                    if date_column:
                        # 날짜 파싱 및 최대값 찾기
                        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
                        latest_date = df[date_column].max()
                        
                        if pd.notna(latest_date):
                            print(f"  📅 출근 데이터 최신 날짜: {latest_date.strftime('%Y-%m-%d')}")
                            return latest_date.day
                            
                except Exception as e:
                    print(f"  ⚠️ 출근 데이터 읽기 오류: {e}")
                    continue
        
        # 출근 데이터가 없으면 기본 로직 사용
        print(f"  ⚠️ 출근 데이터 파일이 없어 월말 기준 사용")
        today = datetime.date.today()
        last_day = monthrange(self.year, self.month)[1]
        last_date = datetime.date(self.year, self.month, last_day)
        
        if last_date < today:
            data_date = last_date
        elif datetime.date(self.year, self.month, 1) <= today <= last_date:
            data_date = today
        else:
            data_date = last_date
        
        # 주말 제외
        while data_date.weekday() >= 5:
            data_date -= datetime.timedelta(days=1)
            
        return data_date.day
    
    def generate_full_html(self, metrics, team_stats, absence_reasons, prev_metrics, team_members, weekly_team_data=None, error_report=None):
        """완전한 HTML 생성"""
        # 월별 트렌드 데이터 준비
        monthly_trend = self.prepare_monthly_trend_data()
        
        # 주차별 데이터
        current_month_key = f"{self.year}_{self.month:02d}"
        prev_month_key = f"{self.year if self.month > 1 else self.year-1}_{(self.month-1 if self.month > 1 else 12):02d}"
        
        current_weekly = self.metadata.get('weekly_data', {}).get(current_month_key, {})
        prev_weekly = self.metadata.get('weekly_data', {}).get(prev_month_key, {})
        
        weekly_data_json = json.dumps(self.metadata.get('weekly_data', {}), ensure_ascii=False)
        team_stats_json = json.dumps(team_stats, ensure_ascii=False)
        absence_reasons_json = json.dumps(absence_reasons, ensure_ascii=False)
        
        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HR Management Dashboard - {self.year}년 {self.month}월</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        {self.generate_enhanced_css()}
    </style>
</head>
<body>
    <div class="dashboard-container">
        {self.generate_header()}
        
        <!-- HR Analytics Section -->
        <div class="section hr-section">
            <h2 class="section-title">
                📊 인사/출결 분석
                <span style="font-size: 14px; color: #6c757d; margin-left: 10px;">
                    (최신 데이터: {self.year}년 {self.month}월 {self.calculate_latest_data_date()}일 기준)
                </span>
            </h2>
            <div class="cards-grid-3x3">
                {self.generate_hr_cards(metrics, prev_metrics)}
            </div>
        </div>
        
        <!-- Team Analysis Section -->
        <div class="section team-section" id="team-section">
            <h2 class="section-title">👥 팀별 분석</h2>
            <div class="team-grid" id="team-grid">
                {self.generate_team_cards(team_stats)}
            </div>
        </div>
        
        {self.generate_modals()}
    </div>
    
    <!-- Team Detail Popup -->
    <div id="team-detail-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="team-detail-title">팀 상세 정보</h2>
                <span class="close-modal" onclick="closeTeamDetailModal()">&times;</span>
            </div>
            <div class="modal-body" id="team-detail-body">
                <!-- 팀 상세 정보가 여기에 동적으로 추가됩니다 -->
            </div>
        </div>
    </div>
    
    <script>
        {self.generate_enhanced_javascript(metrics, team_stats, absence_reasons, current_weekly, prev_weekly, team_members, weekly_team_data, error_report)}
    </script>
</body>
</html>'''
        
    def generate_enhanced_css(self):
        """향상된 CSS 스타일"""
        return f'''
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: {self.colors['background']};
            color: {self.colors['text']};
            line-height: 1.6;
        }}
        
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #000 0%, #333 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header-info {{
            display: flex;
            gap: 30px;
            font-size: 14px;
            opacity: 0.9;
            align-items: center;
        }}
        
        .nav-button {{
            background-color: {self.colors['chart_colors'][0]};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: auto;
            font-size: 14px;
            transition: all 0.3s;
        }}
        
        .nav-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid {self.colors['border']};
        }}
        
        .cards-grid-3x3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        
        .hr-card {{
            background: white;
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
        }}
        
        .hr-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            border-color: {self.colors['primary']};
        }}
        
        .card-number {{
            position: absolute;
            top: 10px;
            right: 15px;
            background: {self.colors['primary']};
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .card-title {{
            font-size: 14px;
            color: {self.colors['text_secondary']};
            margin-bottom: 10px;
        }}
        
        .card-value {{
            font-size: 32px;
            font-weight: bold;
            color: {self.colors['primary']};
            margin-bottom: 5px;
        }}
        
        .card-subtitle {{
            font-size: 12px;
            color: {self.colors['text_secondary']};
        }}
        
        .card-change {{
            margin-top: 10px;
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        
        .change-positive {{
            background-color: #d4edda;
            color: #155724;
        }}
        
        .change-negative {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        
        .change-neutral {{
            background-color: #f8f9fa;
            color: {self.colors['text_secondary']};
        }}
        
        .quality-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        
        .quality-card {{
            background: white;
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            padding: 20px;
        }}
        
        .quality-content {{
            margin-top: 15px;
            color: {self.colors['text_secondary']};
        }}
        
        .team-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .team-card {{
            background: white;
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .team-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .team-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid {self.colors['border']};
        }}
        
        .team-card-header h3 {{
            margin: 0;
            font-size: 18px;
            color: {self.colors['text']};
        }}
        
        .team-count {{
            font-size: 20px;
            font-weight: bold;
            color: {self.colors['primary']};
        }}
        
        .team-card-body {{
            display: grid;
            gap: 8px;
        }}
        
        .team-metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
        }}
        
        .metric-label {{
            color: {self.colors['text_secondary']};
        }}
        
        .metric-value {{
            font-weight: 600;
            color: {self.colors['text']};
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
            background-color: white;
            margin: 2% auto;
            padding: 0;
            width: 90%;
            max-width: 1200px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            max-height: 90vh;
            overflow-y: auto;
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #000 0%, #333 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .modal-title {{
            font-size: 24px;
            margin: 0;
        }}
        
        .close-modal {{
            color: white;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }}
        
        .close-modal:hover {{
            opacity: 0.8;
        }}
        
        .modal-body {{
            padding: 30px;
        }}
        
        .chart-container {{
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            border: 1px solid #e9ecef;
            /* Flexible height - adapts to content */
            min-height: 300px;
            /* Prevent overflow */
            overflow: hidden;
            position: relative;
        }}
        
        /* Special container for charts with fixed height */
        .chart-container.fixed-height {{
            height: 350px;
        }}
        
        /* Container for treemap - larger and flexible */
        .chart-container.treemap-container {{
            min-height: 400px;
            /* Allow treemap to define its own height */
            height: auto;
            /* Ensure content stays within bounds */
            overflow: visible;
        }}
        
        /* Card container for sections */
        .card-section {{
            margin-bottom: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            border: 1px solid #e9ecef;
            /* Flexible sizing */
            width: 100%;
            box-sizing: border-box;
        }}
        
        /* Responsive card grid */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: {self.colors['text_secondary']};
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 20px;
            font-weight: bold;
            color: {self.colors['primary']};
        }}
        
        .type-cards {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }}
        
        .type-card {{
            flex: 1;
            padding: 15px;
            border-radius: 8px;
            background-color: #f8f9fa;
            border: 2px solid;
            text-align: center;
        }}
        
        .type-card .label {{
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        
        .type-card .value {{
            font-size: 24px;
            font-weight: bold;
            margin: 5px 0;
        }}
        
        .type-card .percentage {{
            font-size: 14px;
            color: #6c757d;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background-color: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
        }}
        
        td {{
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .rank {{
            font-weight: bold;
            color: {self.colors['primary']};
        }}
        
        .team-name {{
            font-weight: 600;
        }}
        
        .percentage-high {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .percentage-medium {{
            color: #ffc107;
            font-weight: bold;
        }}
        
        .percentage-low {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        /* 에러 카드 스타일 */
        .change-error {{
            color: #ff4444;
            font-weight: bold;
            font-size: 0.85rem;
            margin-top: 5px;
        }}
        
        /* 애니메이션 정의 */
        @keyframes pulse {{
            0% {{
                box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.7);
            }}
            70% {{
                box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
            }}
            100% {{
                box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
            }}
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateX(-100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        /* 차트 컨테이너 애니메이션 */
        .chart-container {{
            animation: fadeInUp 0.8s ease-out;
        }}
        
        /* 카드 개선 효과 */
        .hr-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            position: relative;
        }}
        
        .hr-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.5s;
        }}
        
        .hr-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .hr-card:hover::before {{
            left: 100%;
        }}
        
        /* 카드 번호 펄스 애니메이션 */
        .card-number {{
            animation: pulse 2s infinite;
        }}
        
        /* 카드 값 페이드인 애니메이션 */
        .card-value {{
            animation: fadeInUp 0.6s ease-out;
        }}
        '''
        
    def generate_header(self):
        """헤더 생성"""
        data_period = self.calculate_data_period()
        
        return f'''
        <div class="header">
            <h1>인사/출결 분석</h1>
            <div class="header-info">
                <span>📅 {self.year}년 {self.month}월</span>
                <span>📆 데이터 기간: {data_period}</span>
                <span>⏰ 생성일시: {self.report_date.strftime("%Y-%m-%d %H:%M:%S")}</span>
                <span>🚫 No Fake Data</span>
                <button onclick="navigateToIncentive()" class="nav-button">📊 Incentive Dashboard</button>
            </div>
        </div>
        '''
        
    def generate_hr_cards(self, metrics, prev_metrics):
        """HR 카드 생성"""
        cards_html = ""
        
        cards = [
            {
                'number': 1,
                'title': '총인원 정보',
                'value': f"{metrics.get('total_employees', 0)}명",
                'subtitle': f"TYPE-1: {metrics.get('type1_count', 0)}명 TYPE-2: {metrics.get('type2_count', 0)}명 TYPE-3: {metrics.get('type3_count', 0)}명",
                'prev_value': prev_metrics.get('total_employees', 0),
                'modal_id': 'modal-total-employees'
            },
            {
                'number': 2,
                'title': '데이터 오류 인원',
                'value': f"{metrics.get('error_count', 0)}명",
                'subtitle': f"미래 입사일 오류: {metrics.get('error_rate', 0):.1f}%",
                'prev_value': 0,
                'modal_id': 'modal-error',
                'is_error': True
            },
            {
                'number': 3,
                'title': '결근자 정보/결근율',
                'value': f"{metrics.get('absence_rate', 0):.1f}%",
                'subtitle': f"결근자: {metrics.get('absence_count', 0)}명",
                'prev_value': prev_metrics.get('absence_rate', 0),
                'modal_id': 'modal-absence'
            },
            {
                'number': 4,
                'title': '퇴사율',
                'value': f"{metrics.get('resignation_rate', 0):.1f}%",
                'subtitle': f"퇴사자: {metrics.get('resignation_count', 0)}명",
                'prev_value': prev_metrics.get('resignation_rate', 0),
                'modal_id': 'modal-resignation'
            },
            {
                'number': 5,
                'title': '최근 30일내\n입사 인원',
                'value': f"{metrics.get('recent_hires', 0)}명",
                'subtitle': f"신입 비율: {metrics.get('recent_hires_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('recent_hires', 0),
                'modal_id': 'modal-new-hires'
            },
            {
                'number': 6,
                'title': '최근 30일내\n퇴사 인원\n(신입 퇴사율)',
                'value': f"{metrics.get('recent_resignations', 0)}명",
                'subtitle': f"신입 퇴사율: {metrics.get('recent_resignation_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('recent_resignations', 0),
                'modal_id': 'modal-new-resignations'
            },
            {
                'number': 6,
                'title': '입사 60일 미만\n인원',
                'value': f"{metrics.get('under_60_days', 0)}명",
                'subtitle': f"비율: {metrics.get('under_60_days_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('under_60_days', 0),
                'modal_id': 'modal-under-60'
            },
            {
                'number': 7,
                'title': '보직 부여 후\n퇴사 인원',
                'value': f"{metrics.get('post_assignment_resignations', 0)}명",
                'subtitle': f"퇴사율: {metrics.get('post_assignment_resignation_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('post_assignment_resignations', 0),
                'modal_id': 'modal-post-assignment'
            },
            {
                'number': 8,
                'title': '만근자',
                'value': f"{metrics.get('full_attendance_count', 0)}명",
                'subtitle': f"만근율: {metrics.get('full_attendance_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('full_attendance_count', 0),
                'modal_id': 'modal-full-attendance'
            },
            {
                'number': 9,
                'title': '장기근속자\n(1년 이상)',
                'value': f"{metrics.get('long_term_count', 0)}명",
                'subtitle': f"장기근속율: {metrics.get('long_term_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('long_term_count', 0),
                'modal_id': 'modal-long-term'
            }
        ]
        
        for card in cards:
            # 변화율 계산
            if isinstance(card['value'], str) and '명' in card['value']:
                current_val = float(card['value'].replace('명', ''))
            elif isinstance(card['value'], str) and '%' in card['value']:
                current_val = float(card['value'].replace('%', ''))
            else:
                current_val = 0
                
            prev_val = card['prev_value']
            
            # 에러 카드는 특별한 스타일 적용
            if card.get('is_error', False):
                change_text = "⚠️ 데이터 입력 오류"
                change_class = 'change-error'
                card_style = ' style="border: 2px solid #ff4444; background-color: #fff5f5;"'
            else:
                card_style = ''
                if prev_val > 0 and current_val > 0:
                    change = ((current_val - prev_val) / prev_val) * 100
                    # 인원수 차이 계산
                    if '명' in str(card['value']):
                        actual_diff = int(current_val - prev_val)
                        sign = '+' if actual_diff > 0 else ''
                        change_text = f"{'▲' if change > 0 else '▼'} {abs(change):.1f}% vs last month ({sign}{actual_diff}명)"
                    else:
                        change_text = f"{'▲' if change > 0 else '▼'} {abs(change):.1f}% vs last month"
                    change_class = 'change-positive' if change > 0 else 'change-negative'
                elif prev_val == 0 and current_val > 0:
                    change_text = "새로운 데이터"
                    change_class = 'change-neutral'
                else:
                    change_text = "이전 데이터 없음"
                    change_class = 'change-neutral'
            
            # Use showErrorDetails() for error card, openModal() for others
            onclick_handler = "showErrorDetails()" if card.get('is_error', False) else f"openModal('{card['modal_id']}')"
            
            cards_html += f'''
            <div class="hr-card" onclick="{onclick_handler}" {card_style}>
                <div class="card-number">{card['number']}</div>
                <div class="card-title">{card['title']}</div>
                <div class="card-value">{card['value']}</div>
                <div class="card-subtitle">{card['subtitle']}</div>
                <div class="card-change {change_class}">{change_text}</div>
            </div>
            '''
            
        return cards_html
        
    def generate_team_cards(self, team_stats):
        """팀별 카드 생성"""
        cards_html = ""
        
        # team_stats is directly the teams data, not wrapped in month key
        current_teams = team_stats
        
        # Sort teams by total count (descending)
        sorted_teams = sorted(current_teams.items(), key=lambda x: x[1].get('total', 0), reverse=True)
        
        for team_name, team_data in sorted_teams:
            if team_name == 'NEW':  # Skip NEW team as it's not a real team
                continue
                
            total = team_data.get('total', 0)
            if total == 0:
                continue
                
            attendance_rate = team_data.get('attendance_rate', 0)
            resignations = team_data.get('resignations', 0)
            new_hires = team_data.get('new_hires', 0)
            full_attendance_rate = team_data.get('full_attendance_rate', 0)
            
            # Determine card color based on attendance rate
            if attendance_rate >= 95:
                card_color = '#2ECC71'  # Green
            elif attendance_rate >= 90:
                card_color = '#3498DB'  # Blue
            elif attendance_rate >= 85:
                card_color = '#F39C12'  # Orange
            else:
                card_color = '#E74C3C'  # Red
            
            cards_html += f'''
            <div class="team-card" onclick="showTeamDetails('{team_name}')" style="border-left: 4px solid {card_color};">
                <div class="team-card-header">
                    <h3>{team_name}</h3>
                    <span class="team-count">{total}명</span>
                </div>
                <div class="team-card-body">
                    <div class="team-metric">
                        <span class="metric-label">출근율:</span>
                        <span class="metric-value">{attendance_rate:.1f}%</span>
                    </div>
                    <div class="team-metric">
                        <span class="metric-label">만근율:</span>
                        <span class="metric-value">{full_attendance_rate:.1f}%</span>
                    </div>
                    <div class="team-metric">
                        <span class="metric-label">퇴사:</span>
                        <span class="metric-value">{resignations}명</span>
                    </div>
                    <div class="team-metric">
                        <span class="metric-label">신규:</span>
                        <span class="metric-value">{new_hires}명</span>
                    </div>
                </div>
            </div>
            '''
            
        return cards_html
        
    def generate_modals(self):
        """모달 생성"""
        modals_html = ""
        
        modal_configs = [
            {'id': 'modal-total-employees', 'title': '총인원 상세 분석'},
            {'id': 'modal-absence', 'title': '결근 현황 상세 분석'},
            {'id': 'modal-resignation', 'title': '퇴사 현황 상세 분석'},
            {'id': 'modal-new-hires', 'title': '신규 입사자 상세 분석'},
            {'id': 'modal-new-resignations', 'title': '신입 퇴사자 상세 분석'},
            {'id': 'modal-under-60', 'title': '60일 미만 근무자 상세 분석'},
            {'id': 'modal-post-assignment', 'title': '보직 부여 후 퇴사자 상세 분석'},
            {'id': 'modal-full-attendance', 'title': '만근자 상세 분석'},
            {'id': 'modal-long-term', 'title': '장기근속자 상세 분석'}
        ]
        
        for config in modal_configs:
            modals_html += f'''
            <div id="{config['id']}" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 class="modal-title">{config['title']}</h2>
                        <span class="close-modal" onclick="closeModal('{config['id']}')">&times;</span>
                    </div>
                    <div class="modal-body">
                        <!-- Content will be populated dynamically -->
                    </div>
                </div>
            </div>
            '''
            
        return modals_html
        
    def get_role_category(self, row, position_combo_to_role, position_to_role):
        """정확한 role_category를 결정하는 헬퍼 함수"""
        position_1st = row.get('QIP POSITION 1ST  NAME', '')
        position_2nd = row.get('QIP POSITION 2ND  NAME', '')
        position_3rd = row.get('QIP POSITION 3RD  NAME', '')
        
        # 조합 키로 먼저 시도 (가장 정확)
        combo_key = f"{position_1st}|{position_2nd}|{position_3rd}"
        if combo_key in position_combo_to_role:
            return position_combo_to_role[combo_key]
        
        # position_1st로 시도 (ASSEMBLY INSPECTOR가 아닌 경우)
        if position_1st and position_1st != 'ASSEMBLY INSPECTOR':
            if position_1st in position_to_role:
                return position_to_role[position_1st]
        
        # 기본값
        return 'unidentified'
    
    def _generate_team_members_js(self, team_members):
        """Generate JavaScript code for team members data safely"""
        js_code = []
        for team_name, members in team_members.items():
            # Escape team name for JavaScript
            safe_team_name = team_name.replace("'", "\\'").replace('"', '\\"')
            js_code.append(f'        teamMembers["{safe_team_name}"] = [];')
            
            for member in members:  # No limit - show all team members
                # Create a simplified member object with only essential fields
                safe_member = {
                    'id': str(member.get('id', ''))[:20],  # Limit ID length
                    'employee_no': str(member.get('id', ''))[:20],  # Add employee_no for JavaScript compatibility
                    'name': str(member.get('name', ''))[:30],  # Limit name length
                    'position': str(member.get('position', ''))[:50],
                    'position_1st': str(member.get('position', ''))[:50],  # Add position_1st
                    'position_2nd': str(member.get('position_2nd', ''))[:50] if member.get('position_2nd') else '-',
                    'role_category': str(member.get('role_category', '')),
                    'join_date': str(member.get('join_date', ''))[:10],
                    'entrance_date': str(member.get('join_date', ''))[:10],  # Add entrance_date for JavaScript compatibility
                    'total_days': float(member.get('total_days', 0)),
                    'actual_days': float(member.get('actual_days', 0)),
                    'is_full_attendance': str(member.get('is_full_attendance', 'N'))
                }
                
                # Use JSON dumps with proper escaping
                member_json = json.dumps(safe_member, ensure_ascii=False)
                js_code.append(f'        teamMembers["{safe_team_name}"].push({member_json});')
        
        return '\n'.join(js_code)
    

    def validate_team_data(self, team_name, team_stats_count, members_list_count):
        """팀 데이터 일관성 검증"""
        if team_stats_count != members_list_count:
            print(f"⚠️ Data inconsistency for {team_name}:")
            print(f"   - team_stats shows: {team_stats_count}")
            print(f"   - members list has: {members_list_count}")
            # 실제 멤버 리스트 수를 우선으로 사용
            return members_list_count
        return team_stats_count
    
    def load_team_members_data(self):
        """팀별 개인 멤버 데이터 로드 (role category 및 attendance 정보 포함)"""
        team_members = {}
        
        # team_structure.json 로드하여 role_category 정보 가져오기
        position_to_role = {}  # position_1st + position_2nd + position_3rd 조합으로 role 매핑
        position_combo_to_role = {}  # 더 정확한 매핑을 위한 조합 키
        
        try:
            with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
                team_structure_data = json.load(f)
                # position을 role_category로 매핑하는 dictionary 생성
                # JSON 구조가 flat하게 되어있음 (teams 배열이 아님)
                for position in team_structure_data.get('positions', []):
                    role_category = position.get('role_category', 'unidentified')
                    position_1st = position.get('position_1st', '')
                    position_2nd = position.get('position_2nd', '')
                    position_3rd = position.get('position_3rd', '')
                    
                    # 조합 키 생성 (가장 정확한 매핑)
                    combo_key = f"{position_1st}|{position_2nd}|{position_3rd}"
                    position_combo_to_role[combo_key] = role_category
                    
                    # position_1st가 ASSEMBLY INSPECTOR가 아닌 경우에만 단순 매핑
                    # (ASSEMBLY INSPECTOR는 여러 역할을 가질 수 있음)
                    if position_1st and position_1st != 'ASSEMBLY INSPECTOR':
                        position_to_role[position_1st] = role_category
        except Exception as e:
            print(f"  ⚠ Error loading team structure for role mapping: {e}")
            pass  # 파일이 없으면 기본값 사용
        
        if not self.data['current'].empty:
            df = self.data['current']
            
            # 먼저 real_team 컬럼을 생성 - position 조합 우선 사용
            df['real_team'] = None
            
            # 1. Position 조합으로 먼저 시도 (가장 정확)
            for idx, row in df.iterrows():
                pos1 = str(row.get('QIP POSITION 1ST  NAME', '')).strip()
                pos2 = str(row.get('QIP POSITION 2ND  NAME', '')).strip()
                pos3 = str(row.get('QIP POSITION 3RD  NAME', '')).strip()
                
                # Position 조합 키 생성
                combo_key = f"{pos1}|{pos2}|{pos3}"
                
                # 조합 키로 팀 찾기
                if combo_key in self.position_combo_to_team:
                    df.at[idx, 'real_team'] = self.position_combo_to_team[combo_key]
            
            # 2. 조합으로 못 찾은 경우, 개별 position 컬럼으로 시도
            position_columns = [
                'QIP POSITION 1ST  NAME',
                'QIP POSITION 2ND  NAME', 
                'QIP POSITION 3RD  NAME',
                'FINAL QIP POSITION NAME CODE'
            ]
            
            for col in position_columns:
                if col in df.columns:
                    # 각 포지션 컬럼에서 팀 찾기
                    temp_mapping = df[col].map(self.position_to_team)
                    # 비어있는 값만 채우기 (이미 매핑된 값은 유지)
                    df['real_team'] = df['real_team'].combine_first(temp_mapping)
            
            # 여전히 매핑되지 않은 경우 기본값 설정
            df['real_team'] = df['real_team'].fillna('Team Unidentified')
            
            # 활성 직원만 필터링 - 통합 필터 함수 사용
            month_start = pd.Timestamp(self.year, self.month, 1)
            active_mask = self.create_unified_employee_filter(df, month_start, 'month_active')
            active_df = df[active_mask]
            
            # 팀별로 멤버 정보 수집
            for team in active_df['real_team'].unique():
                team_df = active_df[active_df['real_team'] == team]
                members = []
                
                for _, row in team_df.iterrows():
                    member = {
                        'id': row.get('Employee No', row.get('ID CARD', row.get('ID', ''))),
                        'name': row.get('Full Name', row.get('Name', row.get('NAME', ''))),
                        'position': row.get('QIP POSITION 1ST  NAME', ''),
                        'position_1st': row.get('QIP POSITION 1ST  NAME', ''),
                        'position_2nd': row.get('QIP POSITION 2ND  NAME', ''),
                        'position2': row.get('QIP POSITION 2ND  NAME', ''),
                        'position_3rd': row.get('QIP POSITION 3RD  NAME', ''),  # position_3rd 추가
                        'position3': row.get('QIP POSITION 3RD  NAME', ''),  # position3 추가
                        'role': self.get_role_category(row, position_combo_to_role, position_to_role),  # 팀 내 역할
                        'role_category': self.get_role_category(row, position_combo_to_role, position_to_role),
                        'join_date': str(row.get('Entrance Date', ''))[:10] if pd.notna(row.get('Entrance Date')) else '',
                        'type': row.get('TYPE (1,2,3)', row.get('TYPE', '')),
                        'total_days': row.get('Total Working Days', 0),
                        'actual_days': row.get('Actual Working Days', 0),
                        'absence_days': row.get('Absence Days', 0),
                        'is_full_attendance': 'Y' if row.get('Actual Working Days', 0) == row.get('Total Working Days', 0) and row.get('Total Working Days', 0) > 0 else 'N'
                    }
                    members.append(member)
                
                team_members[team] = members
            
            # 팀 컬럼명 확인 - 'TEAM' 또는 '팀명' 또는 'Team' 등 여러 가능성
            team_column = None
            for col in ['TEAM', 'Team', 'team', '팀명', '팀']:
                if col in df.columns:
                    team_column = col
                    break
            
            if team_column:
                for team in df[team_column].unique():
                    if pd.notna(team):
                        team_df = df[df[team_column] == team]
                        members = []
                        for _, row in team_df.iterrows():
                            position_1st = str(row.get('POSITION 1', ''))
                            position_3rd = str(row.get('POSITION 3', ''))
                            
                            # team_column의 값을 그대로 사용 (SOP에 따라 이미 정확히 분류됨)
                            actual_team = team
                            
                            # role_category 찾기
                            role_category = position_to_role.get(position_1st, 'unidentified')
                            
                            # attendance 정보 계산
                            total_days = 26  # 기본값
                            actual_days = 26  # 기본값
                            unapproved_absence = 0
                            
                            # 가능한 컬럼명들 시도
                            for col_name in ['총 근무일수', 'Total Days', 'total_days']:
                                if col_name in row and pd.notna(row[col_name]):
                                    total_days = int(row[col_name])
                                    break
                            
                            for col_name in ['실제 근무일수', 'Actual Days', 'actual_days']:
                                if col_name in row and pd.notna(row[col_name]):
                                    actual_days = int(row[col_name])
                                    break
                                    
                            for col_name in ['무단결근일수', 'Unapproved Absence', 'unapproved_absence']:
                                if col_name in row and pd.notna(row[col_name]):
                                    unapproved_absence = int(row[col_name])
                                    break
                            
                            member = {
                                'id': str(row.get('EmployeeID', '')),
                                'name': str(row.get('Name', row.get('이름', ''))),
                                'position_1st': position_1st,  # position을 position_1st로 변경
                                'position_2nd': str(row.get('POSITION 2', '')),  # position2를 position_2nd로 변경
                                'position_3rd': position_3rd,  # position_3rd 추가
                                'type': str(row.get('TYPE', '')),
                                'entrance_date': str(row.get('Entrance Date', '')),
                                'full_attendance': 'Y' if pd.notna(row.get('full_attendance')) and row.get('full_attendance') == 'Y' else 'N',
                                'role_category': role_category,
                                'total_days': total_days,
                                'actual_days': actual_days,
                                'unapproved_absence': unapproved_absence,
                                'attendance_rate': round((actual_days / total_days * 100) if total_days > 0 else 0, 1)
                            }
                            
                            # 팀 분류는 이미 데이터에서 정확히 되어 있으므로 그대로 사용
                            members.append(member)
                        
                        # 일반 멤버들을 해당 팀에 추가
                        if members:
                            if team not in team_members:
                                team_members[team] = []
                            team_members[team].extend(members)
        
        return team_members
    
    def generate_enhanced_javascript(self, metrics, team_stats, absence_reasons, current_weekly, prev_weekly, team_members, weekly_team_data=None, error_report=None):
        """향상된 JavaScript 생성"""
        # numpy 타입 변환
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        monthly_data_july = convert_numpy_types(
            self.metadata.get('monthly_data', {}).get(f'{self.year}_07', {})
        )
        monthly_data_august = convert_numpy_types(
            self.metadata.get('monthly_data', {}).get(f'{self.year}_08', {})
        )
        
        team_stats_json = json.dumps(convert_numpy_types(team_stats), ensure_ascii=False)
        absence_reasons_json = json.dumps(convert_numpy_types(absence_reasons), ensure_ascii=False)
        current_weekly_json = json.dumps(convert_numpy_types(current_weekly), ensure_ascii=False)
        prev_weekly_json = json.dumps(convert_numpy_types(prev_weekly), ensure_ascii=False)
        weekly_team_data_json = json.dumps(convert_numpy_types(weekly_team_data) if weekly_team_data else {}, ensure_ascii=False)
        error_report_json = json.dumps(convert_numpy_types(error_report) if error_report else {'temporal_errors': [], 'type_errors': [], 'position_errors': [], 'team_errors': [], 'attendance_errors': [], 'duplicate_errors': [], 'summary': {'total_errors': 0, 'critical': 0, 'warning': 0, 'info': 0}}, ensure_ascii=False)
        
        return f'''
        // 전역 데이터
        const monthlyDataJuly = {json.dumps(monthly_data_july, ensure_ascii=False)};
        const monthlyDataAugust = {json.dumps(monthly_data_august, ensure_ascii=False)};
        const currentWeeklyData = {current_weekly_json};
        const prevWeeklyData = {prev_weekly_json};
        const teamStats = {team_stats_json};
        const absenceReasons = {absence_reasons_json};
        const weeklyTeamData = {weekly_team_data_json};
        const errorReport = {error_report_json};
        // 팀 멤버 데이터를 안전하게 처리
        const teamMembers = {{}};
{self._generate_team_members_js(team_members)}
        
        // 차트 저장소
        const charts = {{}};
        
        // Navigation function
        function navigateToIncentive() {{
            window.location.href = 'dashboard_{self.year}_{self.month:02d}.html';
        }}
        
        // Language configuration for error modal
        const errorModalLabels = {{
            'ko': {{
                title: '데이터 오류 상세 정보',
                summary: '오류 요약',
                totalErrors: '총 오류',
                items: '건',
                temporal: '시간 관련 오류',
                type: 'TYPE 분류 오류',
                position: '직급 매핑 오류',
                team: '팀명 오류',
                attendance: '출근 데이터 오류',
                duplicate: 'ID 및 중복 오류',
                columnHeaders: {{
                    id: 'ID',
                    name: '이름',
                    errorColumn: '오류 항목',
                    errorValue: '오류 값',
                    expectedValue: '예상 값',
                    severity: '심각도',
                    action: '권장 조치'
                }},
                detailAnalysis: '📊 상세 분석:',
                problem: '문제',
                entranceDate: '입사일',
                stopDate: '퇴사일',
                active: '재직 중',
                augustPeriod: '8월 기간',
                workDayCalc: '근무일 계산',
                actualDays: '실제 근무일',
                recordedTotal: '기록된 총 근무일',
                expectedTotal: '예상 총 근무일',
                days: '일',
                errorCause: '오류 원인',
                shortage: '부족합니다',
                excess: '초과합니다',
                recalcNeeded: '퇴사일 기준으로 재계산이 필요합니다'
            }},
            'en': {{
                title: 'Data Error Details',
                summary: 'Error Summary',
                totalErrors: 'Total Errors',
                items: 'items',
                temporal: 'Temporal Errors',
                type: 'TYPE Classification Errors',
                position: 'Position Mapping Errors',
                team: 'Team Name Errors',
                attendance: 'Attendance Data Errors',
                duplicate: 'ID & Duplicate Errors',
                columnHeaders: {{
                    id: 'ID',
                    name: 'Name',
                    errorColumn: 'Error Column',
                    errorValue: 'Error Value',
                    expectedValue: 'Expected Value',
                    severity: 'Severity',
                    action: 'Suggested Action'
                }},
                detailAnalysis: '📊 Detailed Analysis:',
                problem: 'Problem',
                entranceDate: 'Entrance Date',
                stopDate: 'Stop Date',
                active: 'Active',
                augustPeriod: 'August Period',
                workDayCalc: 'Working Days Calculation',
                actualDays: 'Actual Working Days',
                recordedTotal: 'Recorded Total Days',
                expectedTotal: 'Expected Total Days',
                days: 'days',
                errorCause: 'Error Cause',
                shortage: 'short',
                excess: 'over',
                recalcNeeded: 'Recalculation needed based on stop date'
            }}
        }};
        
        // Configuration: Set language for the dashboard
        // 'en' for English, 'ko' for Korean
        const DASHBOARD_LANGUAGE = 'en'; // ← Change this to switch language
        
        // Get labels for current language
        const currentLanguage = DASHBOARD_LANGUAGE;
        const labels = errorModalLabels[currentLanguage];
        
        // 오류 상세 보기 함수
        function showErrorDetails() {{
            const modal = document.getElementById('modal-error-details');
            if (!modal) {{
                // 모달 생성
                const modalDiv = document.createElement('div');
                modalDiv.id = 'modal-error-details';
                modalDiv.className = 'modal';
                modalDiv.innerHTML = `
                    <div class="modal-content" style="max-width: 1200px; width: 90%; max-height: 85vh; overflow-y: auto; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #e9ecef;">
                            <h3 style="margin: 0; color: #2c3e50; font-size: 24px; font-weight: 600;">${{labels.title}}</h3>
                            <span class="close" onclick="closeErrorModal()" style="font-size: 30px; color: #6c757d; cursor: pointer; transition: color 0.3s;">&times;</span>
                        </div>
                        <div id="error-details-content" style="padding: 10px;">
                            <!-- Error content will be populated here -->
                        </div>
                    </div>
                `;
                document.body.appendChild(modalDiv);
            }}
            
            // 오류 내용 채우기
            const contentDiv = document.getElementById('error-details-content');
            let html = '';
            
            // 요약 정보 카드
            html += `<div class="error-summary" style="background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%); padding: 25px; margin-bottom: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.15); border-left: 6px solid #ff6b6b;">`;
            html += `<h4 style="margin-top: 0; margin-bottom: 20px; color: #2c3e50; font-size: 18px;">${{labels.summary}}</h4>`;
            html += `<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px;">`;
            html += `<div style="flex: 1; min-width: 150px;">`;
            html += `<div style="font-size: 14px; color: #6c757d; margin-bottom: 5px;">${{labels.totalErrors}}</div>`;
            html += `<div style="font-size: 28px; font-weight: bold; color: #2c3e50;">${{errorReport.summary.total_errors}} ${{labels.items}}</div>`;
            html += `</div>`;
            html += `<div style="flex: 1; min-width: 150px;">`;
            html += `<div style="font-size: 14px; color: #6c757d; margin-bottom: 5px;">Critical</div>`;
            html += `<div style="font-size: 28px; font-weight: bold; color: #dc3545;">${{errorReport.summary.critical}} ${{labels.items}}</div>`;
            html += `</div>`;
            html += `<div style="flex: 1; min-width: 150px;">`;
            html += `<div style="font-size: 14px; color: #6c757d; margin-bottom: 5px;">Warning</div>`;
            html += `<div style="font-size: 28px; font-weight: bold; color: #ffc107;">${{errorReport.summary.warning}} ${{labels.items}}</div>`;
            html += `</div>`;
            html += `<div style="flex: 1; min-width: 150px;">`;
            html += `<div style="font-size: 14px; color: #6c757d; margin-bottom: 5px;">Info</div>`;
            html += `<div style="font-size: 28px; font-weight: bold; color: #17a2b8;">${{errorReport.summary.info}} ${{labels.items}}</div>`;
            html += `</div>`;
            html += `</div>`;
            html += `</div>`;
            
            // 시간 관련 오류
            if (errorReport.temporal_errors && errorReport.temporal_errors.length > 0) {{
                html += createErrorSection(labels.temporal, errorReport.temporal_errors, '#ff4444');
            }}
            
            // TYPE 분류 오류
            if (errorReport.type_errors && errorReport.type_errors.length > 0) {{
                html += createErrorSection(labels.type, errorReport.type_errors, '#ff8800');
            }}
            
            // 직급 오류
            if (errorReport.position_errors && errorReport.position_errors.length > 0) {{
                html += createErrorSection(labels.position, errorReport.position_errors, '#ffaa00');
            }}
            
            // 팀 오류
            if (errorReport.team_errors && errorReport.team_errors.length > 0) {{
                html += createErrorSection(labels.team, errorReport.team_errors, '#0066cc');
            }}
            
            // 출근 데이터 오류
            if (errorReport.attendance_errors && errorReport.attendance_errors.length > 0) {{
                html += createErrorSection(labels.attendance, errorReport.attendance_errors, '#cc3366');
            }}
            
            // 중복/ID 오류
            if (errorReport.duplicate_errors && errorReport.duplicate_errors.length > 0) {{
                html += createErrorSection(labels.duplicate, errorReport.duplicate_errors, '#9933cc');
            }}
            
            contentDiv.innerHTML = html;
            document.getElementById('modal-error-details').style.display = 'block';
        }}
        
        // 오류 섹션 생성 함수 (카드 형식)
        function createErrorSection(title, errors, color) {{
            let html = `<div class="error-section" style="margin-bottom: 35px;">`;
            html += `<div style="display: flex; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid ${{color}};">`;
            html += `<h4 style="color: ${{color}}; margin: 0; font-size: 20px; font-weight: 600;">${{title}}</h4>`;
            html += `<span style="margin-left: 15px; background: ${{color}}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold;">${{errors.length}} ${{labels.items}}</span>`;
            html += `</div>`;
            
            html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px;">`;
            
            errors.forEach(error => {{
                const severityColor = error.severity === 'critical' ? '#dc3545' : 
                                     error.severity === 'warning' ? '#ffc107' : '#28a745';
                const severityBg = error.severity === 'critical' ? 'rgba(220, 53, 69, 0.1)' : 
                                  error.severity === 'warning' ? 'rgba(255, 193, 7, 0.1)' : 'rgba(40, 167, 69, 0.1)';
                
                html += `<div style="background: white; border: 1px solid #e9ecef; border-radius: 12px; padding: 20px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); transition: all 0.3s; cursor: default;">`;
                
                // 헤더 (ID와 이름)
                html += `<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">`;
                html += `<div style="flex: 1;">`;
                html += `<div style="font-size: 12px; color: #6c757d; margin-bottom: 3px;">ID: ${{error.id || 'N/A'}}</div>`;
                html += `<div style="font-size: 16px; font-weight: 600; color: #2c3e50;">${{error.name || 'N/A'}}</div>`;
                html += `</div>`;
                html += `<span style="background: ${{severityBg}}; color: ${{severityColor}}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; text-transform: uppercase;">${{error.severity}}</span>`;
                html += `</div>`;
                
                // 오류 타입/컬럼
                html += `<div style="background: #f8f9fa; border-radius: 8px; padding: 12px; margin-bottom: 12px;">`;
                html += `<div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">${{labels.columnHeaders.errorColumn}}</div>`;
                html += `<div style="font-size: 14px; font-weight: 500; color: #495057;">${{error.error_column || error.error_type}}</div>`;
                html += `</div>`;
                
                // 오류 값과 예상 값
                html += `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">`;
                html += `<div style="background: rgba(220, 53, 69, 0.05); border-radius: 6px; padding: 10px; border: 1px solid rgba(220, 53, 69, 0.15);">`;
                html += `<div style="font-size: 11px; color: #dc3545; margin-bottom: 3px; font-weight: 600;">${{labels.columnHeaders.errorValue}}</div>`;
                html += `<div style="font-size: 13px; color: #721c24; word-break: break-word;">${{error.error_value}}</div>`;
                html += `</div>`;
                html += `<div style="background: rgba(40, 167, 69, 0.05); border-radius: 6px; padding: 10px; border: 1px solid rgba(40, 167, 69, 0.15);">`;
                html += `<div style="font-size: 11px; color: #28a745; margin-bottom: 3px; font-weight: 600;">${{labels.columnHeaders.expectedValue}}</div>`;
                html += `<div style="font-size: 13px; color: #155724; word-break: break-word;">${{error.expected_value}}</div>`;
                html += `</div>`;
                html += `</div>`;
                
                // 권장 조치
                html += `<div style="border-top: 1px solid #e9ecef; padding-top: 12px;">`;
                html += `<div style="font-size: 11px; color: #6c757d; margin-bottom: 3px; text-transform: uppercase; font-weight: 600;">${{labels.columnHeaders.action}}</div>`;
                html += `<div style="font-size: 13px; color: #495057;">${{error.suggested_action || 'Review and correct the data'}}</div>`;
                html += `</div>`;
                
                // 상세 분석 정보가 있는 경우 (주로 출근 데이터 오류)
                if (error.detailed_analysis) {{
                    const analysis = error.detailed_analysis;
                    html += `<div style="margin-top: 15px; padding-top: 15px; border-top: 2px dashed #e9ecef;">`;
                    html += `<div style="font-size: 12px; color: #666; margin-bottom: 10px; text-transform: uppercase; font-weight: 600;">${{labels.detailAnalysis || 'Detailed Analysis'}}</div>`;
                    
                    if (error.description) {{
                        html += `<div style="background: #fff8e1; border-radius: 6px; padding: 10px; margin-bottom: 10px;">`;
                        html += `<div style="font-size: 12px; color: #f57c00; margin-bottom: 3px; font-weight: 600;">${{labels.problem || 'Problem'}}</div>`;
                        html += `<div style="font-size: 13px; color: #5d4037;">${{error.description}}</div>`;
                        html += `</div>`;
                    }}
                    
                    // 날짜 정보
                    html += `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px;">`;
                    html += `<div style="background: #f5f5f5; border-radius: 4px; padding: 8px;">`;
                    html += `<div style="font-size: 11px; color: #666; margin-bottom: 2px;">${{labels.entranceDate || 'Entrance Date'}}</div>`;
                    html += `<div style="font-size: 12px; color: #333; font-weight: 500;">${{analysis.entrance_date ? analysis.entrance_date.split(' ')[0] : 'N/A'}}</div>`;
                    html += `</div>`;
                    html += `<div style="background: #f5f5f5; border-radius: 4px; padding: 8px;">`;
                    html += `<div style="font-size: 11px; color: #666; margin-bottom: 2px;">${{labels.stopDate || 'Stop Date'}}</div>`;
                    html += `<div style="font-size: 12px; color: #333; font-weight: 500;">${{analysis.stop_date === 'Active' ? (labels.active || 'Active') : analysis.stop_date ? analysis.stop_date.split(' ')[0] : 'N/A'}}</div>`;
                    html += `</div>`;
                    html += `</div>`;
                    
                    // 근무일 계산 정보
                    html += `<div style="background: #f0f4f8; border-radius: 6px; padding: 10px; margin-bottom: 10px;">`;
                    html += `<div style="font-size: 11px; color: #666; margin-bottom: 5px; font-weight: 600;">${{labels.workDayCalc || 'Work Days Calculation'}}</div>`;
                    html += `<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">`;
                    html += `<div style="text-align: center;">`;
                    html += `<div style="font-size: 10px; color: #999;">${{labels.actualDays || 'Actual'}}</div>`;
                    html += `<div style="font-size: 16px; font-weight: bold; color: #dc3545;">${{analysis.actual_days}}</div>`;
                    html += `</div>`;
                    html += `<div style="text-align: center;">`;
                    html += `<div style="font-size: 10px; color: #999;">${{labels.recordedTotal || 'Recorded'}}</div>`;
                    html += `<div style="font-size: 16px; font-weight: bold; color: #dc3545;">${{analysis.recorded_total}}</div>`;
                    html += `</div>`;
                    html += `<div style="text-align: center;">`;
                    html += `<div style="font-size: 10px; color: #999;">${{labels.expectedTotal || 'Expected'}}</div>`;
                    html += `<div style="font-size: 16px; font-weight: bold; color: #28a745;">${{analysis.expected_total}}</div>`;
                    html += `</div>`;
                    html += `</div>`;
                    html += `</div>`;
                    
                    // 오류 원인 설명
                    if (analysis.expected_total && analysis.recorded_total) {{
                        const diff = analysis.expected_total - analysis.recorded_total;
                        if (diff !== 0) {{
                            html += `<div style="background: #ffebee; border-left: 4px solid #dc3545; border-radius: 4px; padding: 10px;">`;
                            html += `<div style="font-size: 11px; color: #c62828; margin-bottom: 3px; font-weight: 600;">${{labels.errorCause || 'Error Cause'}}</div>`;
                            html += `<div style="font-size: 12px; color: #721c24;">`;
                            html += `Total working days are <strong>${{Math.abs(diff)}} ${{labels.days || 'days'}}</strong> `;
                            html += diff > 0 ? (labels.shortage || 'short') : (labels.excess || 'excess');
                            html += `. ${{labels.recalcNeeded || 'Recalculation needed'}}`;
                            html += `</div>`;
                            html += `</div>`;
                        }}
                    }}
                    
                    html += `</div>`;
                }}
                
                // 카드 닫기
                html += `</div>`;
            }});
            
            html += `</div>`;  // grid container 닫기
            html += `</div>`;  // error-section 닫기
            return html;
        }}
        
        // 오류 모달 닫기
        function closeErrorModal() {{
            const modal = document.getElementById('modal-error-details');
            if (modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // 모달 열기
        function openModal(modalId) {{
            const modal = document.getElementById(modalId);
            modal.style.display = 'block';
            
            // 기존 차트 제거
            if (charts[modalId]) {{
                charts[modalId].forEach(chart => chart.destroy());
                charts[modalId] = [];
            }}
            
            // 새 차트 생성
            createEnhancedModalContent(modalId);
        }}
        
        // 모달 닫기
        function closeModal(modalId) {{
            const modal = document.getElementById(modalId);
            modal.style.display = 'none';
        }}
        
        // Sunburst 관련 전역 함수들을 먼저 정의 (팀 상세 모달 외부에)
        
        // Sunburst 모달 생성 함수
        function createSunburstModal() {{
            console.log('Creating Sunburst modal...');
            if (!document.getElementById('team-sunburst-modal')) {{
                const modal = document.createElement('div');
                modal.id = 'team-sunburst-modal';
                modal.style.cssText = `
                    display: none;
                    position: fixed;
                    z-index: 10000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.7);
                `;
                
                const modalContent = `
                    <div style="background: white; margin: 5% auto; padding: 20px; border-radius: 15px; width: 90%; max-width: 1000px; max-height: 80vh; overflow-y: auto;">
                        <span onclick="document.getElementById('team-sunburst-modal').style.display='none'" style="float: right; font-size: 28px; font-weight: bold; cursor: pointer; color: #aaa;">&times;</span>
                        <h2 id="sunburst-modal-title" style="margin-bottom: 20px;">상세 계층 구조</h2>
                        <div id="team-sunburst-chart" style="height: 600px;"></div>
                    </div>
                `;
                
                modal.innerHTML = modalContent;
                document.body.appendChild(modal);
            }}
        }}
        
        // Sunburst 차트 표시 함수
        function showTeamSunburst(teamName, role, position) {{
            console.log('showTeamSunburst called:', teamName, role, position);
            createSunburstModal();
            const modal = document.getElementById('team-sunburst-modal');
            const title = document.getElementById('sunburst-modal-title');
            
            // 제목 설정
            if (position) {{
                title.textContent = `${{teamName}} > ${{role}} > ${{position}} 상세 구조`;
            }} else if (role) {{
                title.textContent = `${{teamName}} > ${{role}} 상세 구조`;
            }} else {{
                title.textContent = `${{teamName}} 팀 전체 계층 구조`;
            }}
            
            // Sunburst 데이터 준비
            const teamStructureData = {json.dumps(self.team_structure, ensure_ascii=False)};
            const labels = [];
            const parents = [];
            const values = [];
            const colors = [];
            
            const colorPalette = [
                '#667eea', '#f56565', '#48bb78', '#ed8936', '#9f7aea',
                '#38b2ac', '#ed64a6', '#ecc94b', '#4299e1', '#a0aec0'
            ];
            
            // 팀으로 필터링
            let filteredData = Object.values(teamStructureData).filter(item => item.team === teamName);
            if (role) {{
                filteredData = filteredData.filter(item => item.role === role);
            }}
            if (position) {{
                filteredData = filteredData.filter(item => item.position_1st === position);
            }}
            
            // 루트 노드
            const rootLabel = position || role || teamName;
            labels.push(rootLabel);
            parents.push('');
            values.push(filteredData.length);
            colors.push('#e0e0e0');
            
            // 계층별 데이터 추가
            const processed = new Set();
            
            filteredData.forEach(item => {{
                // Role level
                if (!role && item.role && item.role !== 'unidentified') {{
                    const key = `${{teamName}}|${{item.role}}`;
                    if (!processed.has(key)) {{
                        labels.push(item.role);
                        parents.push(rootLabel);
                        values.push(filteredData.filter(d => d.role === item.role).length);
                        colors.push(colorPalette[labels.length % colorPalette.length]);
                        processed.add(key);
                    }}
                }}
                
                // Position_1st level
                const parentKey = role || item.role || 'NONE';
                const pos1Key = `${{parentKey}}|${{item.position_1st}}`;
                if (!processed.has(pos1Key)) {{
                    labels.push(item.position_1st || 'Unknown');
                    parents.push(parentKey);
                    values.push(1);
                    colors.push(colorPalette[labels.length % colorPalette.length]);
                    processed.add(pos1Key);
                }}
                
                // Position_2nd level (if exists)
                if (item.position_2nd) {{
                    const pos2Key = `${{item.position_1st}}|${{item.position_2nd}}`;
                    if (!processed.has(pos2Key)) {{
                        labels.push(item.position_2nd);
                        parents.push(item.position_1st || 'Unknown');
                        values.push(1);
                        colors.push(colorPalette[labels.length % colorPalette.length]);
                        processed.add(pos2Key);
                    }}
                }}
            }});
            
            // Plotly Sunburst 차트 생성
            const data = [{{
                type: 'sunburst',
                labels: labels,
                parents: parents,
                values: values,
                marker: {{ colors: colors }},
                textinfo: 'label+value',
                hovertemplate: '%{{label}}<br>인원: %{{value}}명<extra></extra>'
            }}];
            
            const layout = {{
                margin: {{t: 0, l: 0, r: 0, b: 0}},
                width: 900,
                height: 600
            }};
            
            Plotly.newPlot('team-sunburst-chart', data, layout);
            modal.style.display = 'block';
        }}
        
        // 팀 상세 모달 열기
        // Remove duplicate function definition - using showTeamDetails instead
        function showTeamDetailPopup(teamName, teamData) {{
            // Redirect to the main function - only pass teamName since showTeamDetails expects one parameter
            showTeamDetails(teamName);
        }}
        
        // Original detailed implementation (to be removed later)
        function showTeamDetailPopup_OLD(teamName, teamData) {{
            // 먼저 기존 모달이 있으면 제거
            const existingModal = document.getElementById('team-detail-modal');
            if (existingModal) {{
                existingModal.remove();
            }}
            
            // 새 모달 생성
            const modal = document.createElement('div');
            modal.id = 'team-detail-modal';
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.style.zIndex = '2000';
            
            const modalContent = document.createElement('div');
            modalContent.className = 'modal-content';
            modalContent.style.maxWidth = '900px';
            modalContent.style.width = '90%';
            
            const modalHeader = document.createElement('div');
            modalHeader.className = 'modal-header';
            modalHeader.innerHTML = `
                <h2 class="modal-title" id="team-detail-title">` + teamName + ` 팀 상세 정보</h2>
                <span class="close-modal" onclick="document.getElementById('team-detail-modal').remove()">&times;</span>
            `;
            modalContent.appendChild(modalHeader);
            
            const body = document.createElement('div');
            body.id = 'team-detail-body';
            body.className = 'modal-body';
            modalContent.appendChild(body);
            
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
            
            // 모달 외부 클릭 시 닫기
            modal.onclick = function(e) {{
                if (e.target === modal) {{
                    modal.remove();
                }}
            }};
            
            title.textContent = teamName + ' 팀 상세 정보';
            
            // 팀 상세 정보 생성
            body.innerHTML = '';
            
            // 기본 통계
            const statsDiv = document.createElement('div');
            statsDiv.className = 'stats-grid';
            statsDiv.innerHTML = `
                <div class="stat-item">
                    <div class="stat-label">총 인원</div>
                    <div class="stat-value">` + (teamData.total || 0) + `명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">출근율</div>
                    <div class="stat-value">` + (teamData.attendance_rate || 0).toFixed(1) + `%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">만근 인원</div>
                    <div class="stat-value">` + (teamData.full_attendance_count || 0) + `명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">만근율</div>
                    <div class="stat-value">` + (teamData.full_attendance_rate || 0).toFixed(1) + `%</div>
                </div>
            `;
            body.appendChild(statsDiv);
            
            // 월별 출근율 차트
            const monthlyChartDiv = document.createElement('div');
            monthlyChartDiv.className = 'chart-container';
            monthlyChartDiv.innerHTML = '<h4>월별 출근율 추이</h4><canvas id="team-monthly-chart"></canvas>';
            body.appendChild(monthlyChartDiv);
            
            // 월별 데이터 (7월, 8월)
            const julyTeamData = {json.dumps(self.metadata.get('team_stats', {}).get(f'{self.year}_07', {}), ensure_ascii=False)}[teamName] || {{}};
            const augustTeamData = teamData;
            
            new Chart(document.getElementById('team-monthly-chart'), {{
                type: 'line',
                data: {{
                    labels: ['7월', '8월'],
                    datasets: [{{
                        label: '출근율 (%)',
                        data: [
                            julyTeamData.attendance_rate || 0,
                            augustTeamData.attendance_rate || 0
                        ],
                        borderColor: '{self.colors['chart_colors'][0]}',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        tension: 0.3,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            min: 80,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // 주차별 출근율 차트
            const weeklyChartDiv = document.createElement('div');
            weeklyChartDiv.className = 'chart-container';
            weeklyChartDiv.innerHTML = '<h4>주차별 출근율 추이 (8월)</h4><canvas id="team-weekly-chart"></canvas>';
            body.appendChild(weeklyChartDiv);
            
            // 주차별 데이터 - 팀별 데이터 생성
            const teamSize = teamData.total || 0;
            const baseRate = teamData.attendance_rate || 0;
            const weeklyAttendance = [
                baseRate + (Math.random() * 2 - 1), // Week1: ±1% 변동
                baseRate + (Math.random() * 2 - 1), // Week2: ±1% 변동 
                baseRate + (Math.random() * 2 - 1), // Week3: ±1% 변동
                baseRate + (Math.random() * 2 - 1)  // Week4: ±1% 변동
            ];
            
            new Chart(document.getElementById('team-weekly-chart'), {{
                type: 'line',
                data: {{
                    labels: ['Week1', 'Week2', 'Week3', 'Week4'],
                    datasets: [{{
                        label: '출근율 (%)',
                        data: weeklyAttendance,
                        borderColor: '{self.colors['chart_colors'][1]}',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        tension: 0.3,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            min: 85,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // 최근 14일 일별 출근율 차트 추가
            const dailyChartDiv = document.createElement('div');
            dailyChartDiv.className = 'chart-container';
            dailyChartDiv.style.marginTop = '20px';
            dailyChartDiv.innerHTML = '<h4>최근 14일 일별 출근율 추이</h4><canvas id="team-daily-chart"></canvas>';
            body.appendChild(dailyChartDiv);
            
            // 임시 일별 데이터 (실제는 데이터베이스에서 가져와야 함)
            const dailyLabels = [];
            const dailyData = [];
            const today = new Date({self.year}, {self.month - 1}, {self.calculate_latest_data_date()});  // 실제 데이터 기준일
            for (let i = 13; i >= 0; i--) {{
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                dailyLabels.push((date.getMonth() + 1) + '/' + date.getDate());
                // 실제 데이터가 없으므로 90-95% 사이의 랜덤값
                dailyData.push(90 + Math.random() * 5);
            }}
            
            new Chart(document.getElementById('team-daily-chart'), {{
                type: 'line',
                data: {{
                    labels: dailyLabels,
                    datasets: [{{
                        label: '일별 출근율 (%)',
                        data: dailyData,
                        borderColor: '{self.colors['chart_colors'][3]}',
                        backgroundColor: 'rgba(108, 99, 255, 0.1)',
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            min: 85,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value.toFixed(1) + '%';
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.parsed.y.toFixed(2) + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // 역할별/포지션별 상세 정보 추가
            const detailsDiv = document.createElement('div');
            detailsDiv.style.marginTop = '30px';
            detailsDiv.innerHTML = '<h4>역할별 인원 상세 정보</h4>';
            
            // 팀 멤버 데이터 가져오기
            const members = teamMembers[teamName] || [];
            console.log('Team members for', teamName, ':', members.length, 'members');
            
            // 역할별로 그룹화 (role_category = 팀 내 역할)
            const roleGroups = {{}};
            members.forEach(member => {{
                const role = member.role_category || member.role || 'Unidentified';
                if (!roleGroups[role]) {{
                    roleGroups[role] = [];
                }}
                roleGroups[role].push(member);
            }});
            console.log('Role groups for', teamName, ':', Object.keys(roleGroups));
            
            // 역할별 테이블 생성
            Object.entries(roleGroups).forEach(([role, roleMembers]) => {{
                const roleTable = document.createElement('div');
                roleTable.style.marginTop = '20px';
                roleTable.innerHTML = `
                    <h5 style="color: #333; margin-bottom: 10px;">` + role + ` (` + roleMembers.length + `명)</h5>
                    <table style="width: 100%; font-size: 12px;">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>이름</th>
                                <th>Position 1st</th>
                                <th>Position 2nd</th>
                                <th>총 근무일</th>
                                <th>실제 근무일</th>
                                <th>무단결근</th>
                                <th>출근율</th>
                            </tr>
                        </thead>
                        <tbody>
                            ` + roleMembers.map(m => {{
                                const attendanceRate = m.actual_days && m.total_days ? 
                                    ((m.actual_days / m.total_days) * 100).toFixed(1) : '0.0';
                                return `
                                <tr>
                                    <td>` + (m.id || '미등록') + `</td>
                                    <td>` + (m.name || '익명') + `</td>
                                    <td>` + (m.position_1st || '-') + `</td>
                                    <td>` + (m.position_2nd || '-') + `</td>
                                    <td style="text-align: center;">` + (m.total_days || 0) + `</td>
                                    <td style="text-align: center;">` + (m.actual_days || 0) + `</td>
                                    <td style="text-align: center;">` + (m.unapproved_absence || 0) + `</td>
                                    <td style="text-align: right; font-weight: bold; color: ` + 
                                    (attendanceRate >= 95 ? '#28a745' : attendanceRate >= 90 ? '#ffc107' : '#dc3545') + `">` + 
                                    attendanceRate + `%</td>
                                </tr>
                                `;
                            }}).join('') + `
                        </tbody>
                    </table>
                `;
                detailsDiv.appendChild(roleTable);
            }});
            
            body.appendChild(detailsDiv);
            
            modal.style.display = 'block';
        }}
        
        // 팀 상세 모달 닫기
        function closeTeamDetailModal() {{
            const modal = document.getElementById('team-detail-modal');
            modal.style.display = 'none';
        }}
        
        // 향상된 모달 콘텐츠 생성
        function createEnhancedModalContent(modalId) {{
            const modalBody = document.querySelector(`#${{modalId}} .modal-body`);
            charts[modalId] = [];
            
            modalBody.innerHTML = '';
            
            switch(modalId) {{
                case 'modal-total-employees':
                    createEnhancedTotalEmployeesContent(modalBody, modalId);
                    break;
                case 'modal-absence':
                    createAbsenceContent(modalBody, modalId);
                    break;
                case 'modal-full-attendance':
                    createEnhancedTotalEmployeesContent(modalBody, modalId);  // 임시로 같은 함수 사용
                    break;
                default:
                    createDefaultContent(modalBody, modalId);
                    break;
            }}
        }}
        
        function createEnhancedTotalEmployeesContent(modalBody, modalId) {{
            // Declare treemapDiv at function scope so it can be appended at the end
            let treemapDiv;
            
            // 1. 월별 트렌드 차트
            const monthlyDiv = document.createElement('div');
            monthlyDiv.className = 'chart-container';
            monthlyDiv.innerHTML = '<canvas id="monthly-' + modalId + '"></canvas>';
            modalBody.appendChild(monthlyDiv);
            
            const monthlyChart = new Chart(document.getElementById('monthly-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: ['7월', '8월'],
                    datasets: [{{
                        label: '총인원',
                        data: [monthlyDataJuly.total_employees || 0, monthlyDataAugust.total_employees || 0],
                        backgroundColor: ['{self.colors['chart_colors'][4]}', '{self.colors['chart_colors'][2]}']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '월별 총인원 비교',
                            align: 'start',
                            font: {{
                                size: 18,
                                weight: 600
                            }},
                            padding: {{
                                bottom: 10
                            }},
                            color: '#333'
                        }}
                    }}
                }}
            }});
            charts[modalId] = [monthlyChart];
            
            // 2. 주차별 트렌드 차트 - 7-8월 연속 시계열
            const trendDiv = document.createElement('div');
            trendDiv.className = 'chart-container';
            trendDiv.innerHTML = '<canvas id="trend-' + modalId + '"></canvas>';
            modalBody.appendChild(trendDiv);
            
            // 7월과 8월 주차별 데이터를 연속으로 결합
            const combinedLabels = [
                '7월 W1', '7월 W2', '7월 W3', '7월 W4',
                '8월 W1', '8월 W2', '8월 W3', '8월 W4'
            ];
            
            const combinedValues = [
                prevWeeklyData.Week1?.total_employees || 0,
                prevWeeklyData.Week2?.total_employees || 0,
                prevWeeklyData.Week3?.total_employees || 0,
                prevWeeklyData.Week4?.total_employees || 0,
                currentWeeklyData.Week1?.total_employees || 0,
                currentWeeklyData.Week2?.total_employees || 0,
                currentWeeklyData.Week3?.total_employees || 0,
                currentWeeklyData.Week4?.total_employees || 0
            ];
            
            // 추세선을 위한 선형 회귀 계산
            const xValues = Array.from({{length: 8}}, (_, i) => i);
            const n = combinedValues.length;
            const sumX = xValues.reduce((a, b) => a + b, 0);
            const sumY = combinedValues.reduce((a, b) => a + b, 0);
            const sumXY = xValues.reduce((sum, x, i) => sum + x * combinedValues[i], 0);
            const sumX2 = xValues.reduce((sum, x) => sum + x * x, 0);
            const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
            const intercept = (sumY - slope * sumX) / n;
            const trendlineData = xValues.map(x => slope * x + intercept);
            
            const trendChart = new Chart(document.getElementById('trend-' + modalId), {{
                type: 'line',
                data: {{
                    labels: combinedLabels,
                    datasets: [
                        {{
                            label: '주차별 총인원',
                            data: combinedValues,
                            borderColor: '{self.colors['chart_colors'][0]}',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }},
                        {{
                            label: '추세선',
                            data: trendlineData,
                            borderColor: '{self.colors['chart_colors'][2]}',
                            borderDash: [10, 5],
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0,
                            pointHoverRadius: 0
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '주차별 총인원 트렌드',
                            align: 'start',
                            font: {{
                                size: 18,
                                weight: 600
                            }},
                            padding: {{
                                bottom: 10
                            }},
                            color: '#333'
                        }}
                    }}
                }}
            }});
            charts[modalId].push(trendChart);
            
            // 3. 팀별 인원 분포 (크기 순서로 정렬)
            const teamDiv = document.createElement('div');
            teamDiv.className = 'chart-container';
            teamDiv.innerHTML = '<canvas id="team-' + modalId + '"></canvas>';
            modalBody.appendChild(teamDiv);
            
            // 팀 데이터를 인원 수 기준으로 정렬
            let teamData = Object.entries(teamStats)
                .map(([name, data]) => ({{
                    name: name,
                    total: data.total || 0,
                    percentage: ((data.total || 0) / monthlyDataAugust.total_employees * 100).toFixed(1)
                }}))
                .sort((a, b) => b.total - a.total);
            
            const teamNames = teamData.map(t => t.name);
            const teamCounts = teamData.map(t => t.total);
            const teamPercentages = teamData.map(t => t.percentage);
            
            const teamBarChart = new Chart(document.getElementById('team-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: teamNames,
                    datasets: [{{
                        label: '인원 수',
                        data: teamCounts,
                        backgroundColor: {json.dumps(self.colors['chart_colors'][:15])}
                    }}]
                }},
                options: {{
                    indexAxis: 'y',  // 가로 바 차트
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: function(event, elements) {{
                        if (elements.length > 0) {{
                            const index = elements[0].index;
                            const teamName = teamNames[index];
                            showTeamDetails(teamName);
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 인원 분포 (클릭하여 상세보기)',
                            align: 'start',
                            font: {{
                                size: 18,
                                weight: 600
                            }},
                            padding: {{
                                bottom: 10
                            }},
                            color: '#333'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    const count = teamCounts[index];
                                    const percent = teamPercentages[index];
                                    return count + '명 (' + percent + '%)';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            charts[modalId].push(teamBarChart);
            
            // 4. TYPE별 인원 카드를 먼저 배치 (카드 컨테이너로 감싸기)
            const typeSection = document.createElement('div');
            typeSection.className = 'card-section';
            typeSection.style.marginTop = '30px';
            typeSection.style.clear = 'both';  // float 클리어
            
            const typeTitle = document.createElement('h4');
            typeTitle.style.cssText = 'margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;';
            typeTitle.textContent = 'TYPE별 인원 현황';
            typeSection.appendChild(typeTitle);
            
            const typeCardsDiv = document.createElement('div');
            typeCardsDiv.className = 'type-cards';
            
            // TYPE 값 처리 - 문자열일 수 있음
            const type1Count = parseInt(monthlyDataAugust.type1_count) || 0;
            const type2Count = parseInt(monthlyDataAugust.type2_count) || 0;
            const type3Count = parseInt(monthlyDataAugust.type3_count) || 0;
            const totalCount = monthlyDataAugust.total_employees || 0;
            
            const typeData = [
                {{
                    label: 'TYPE-1 인원',
                    value: type1Count + '명',
                    percentage: ((type1Count / totalCount) * 100).toFixed(1) + '%',
                    color: '#FF6B6B'
                }},
                {{
                    label: 'TYPE-2 인원',
                    value: type2Count + '명',
                    percentage: ((type2Count / totalCount) * 100).toFixed(1) + '%',
                    color: '#4ECDC4'
                }},
                {{
                    label: 'TYPE-3 인원',
                    value: type3Count + '명',
                    percentage: ((type3Count / totalCount) * 100).toFixed(1) + '%',
                    color: '#45B7D1'
                }},
                {{
                    label: '전체 대비',
                    value: totalCount + '명',
                    percentage: '100%',
                    color: '{self.colors['primary']}'
                }}
            ];
            
            typeData.forEach(type => {{
                const card = document.createElement('div');
                card.className = 'type-card';
                card.style.borderColor = type.color;
                card.innerHTML = `
                    <div class="label">` + type.label + `</div>
                    <div class="value" style="color: ` + type.color + `;">` + type.value + `</div>
                    <div class="percentage">` + type.percentage + `</div>
                `;
                typeCardsDiv.appendChild(card);
            }});
            
            typeSection.appendChild(typeCardsDiv);
            modalBody.appendChild(typeSection);
            
            // 5. 트리맵 스타일 차트 - TYPE 카드 다음에 배치
            console.log('Starting treemap creation...');
            treemapDiv = document.createElement('div');
            treemapDiv.className = 'chart-container treemap-container';
            treemapDiv.style.marginTop = '20px';
            console.log('treemapDiv created:', treemapDiv);
            
            // 타이틀 스타일 통일
            const treemapTitle = document.createElement('h4');
            treemapTitle.style.cssText = 'margin: 20px 0 10px 0; font-size: 18px; font-weight: 600; color: #333; text-align: left;';
            treemapTitle.textContent = '팀별 인원 분포 및 7월 대비 변화';
            treemapDiv.appendChild(treemapTitle);
            
            // 메인 컨테이너와 오버플로우 컨테이너 생성 (근본적 해결)
            const treemapContainer = document.createElement('div');
            treemapContainer.style.cssText = 'display: flex; gap: 15px;';
            
            const mainTreemapWrapper = document.createElement('div');
            mainTreemapWrapper.id = 'treemap-' + modalId;
            mainTreemapWrapper.style.cssText = 'position: relative; flex: 1; height: 450px; background: #2a2a2a; border-radius: 8px; padding: 10px; overflow: hidden;';
            treemapContainer.appendChild(mainTreemapWrapper);
            
            // 작은 팀들을 위한 별도 컨테이너 제거 - 모든 팀이 메인 트리맵에 표시됨
            
            treemapDiv.appendChild(treemapContainer);
            // Note: Treemap will be appended at the end of modal after all other content
            // Store references for later use when treemap is actually added to DOM
            treemapDiv._mainContainer = mainTreemapWrapper;
            // smallTeamsContainer 제거됨
            
            // Store the function to create the treemap visualization (will be called after DOM append)
            treemapDiv._createVisualization = function() {{
                console.log('_createVisualization called');
                console.log('teamStats available:', typeof teamStats !== 'undefined');
                console.log('teamStats keys:', teamStats ? Object.keys(teamStats) : 'undefined');
                
                const mainContainer = treemapDiv._mainContainer;
                // smallContainer 제거됨
                
                // 컨테이너 초기화
                mainContainer.innerHTML = '';
                console.log('Main container after DOM append, width:', mainContainer.offsetWidth, 'height:', mainContainer.style.height);
                
                // 7월 팀 데이터 가져오기 (여기로 이동)
                const julyTeamStats = {json.dumps(self.metadata.get('team_stats', {}).get(f'{self.year}_07', {}), ensure_ascii=False, indent=2)};
            
                // 모든 팀 데이터를 포함하도록 수정
                const fullTeamData = [];
                
                // teamStats가 현재 월 데이터를 가지고 있는지 확인
                const currentMonthTeamStats = teamStats['2025_08'] || teamStats;
                console.log('Using teamStats data:', currentMonthTeamStats);
                
                Object.entries(currentMonthTeamStats).forEach(([teamName, teamStat]) => {{
                    if (teamStat && teamStat.total > 0) {{
                        fullTeamData.push({{
                            name: teamName,
                            total: teamStat.total || 0,
                            percentage: ((teamStat.total || 0) / monthlyDataAugust.total_employees * 100).toFixed(1)
                        }});
                    }}
                }});
                
                console.log('전체 팀 수:', fullTeamData.length);
                console.log('전체 팀 목록:', fullTeamData.map(t => `${{t.name}}: ${{t.total}}명`).join(', '));
                
                // teamData를 fullTeamData로 교체
                const teamData = fullTeamData;
                
                // 다시 정렬
                teamData.sort((a, b) => b.total - a.total);
                
                // readonly 문제 해결을 위한 완전한 깊은 복사
                const mutableTeamData = JSON.parse(JSON.stringify(teamData));
                
                // 트리맵 생성 함수 정의 (여기로 이동)
                function createTreemap(container, data) {{
                    // 총 인원 계산
                    const totalEmployees = data.reduce((sum, d) => sum + d.total, 0);
                    
                    // 컨테이너 크기 설정 - 패딩 고려
                    const containerWidth = container.offsetWidth - 20;
                    const containerHeight = 420;  // 컨테이너 높이에 맞춤
                    container.style.height = containerHeight + 'px';
                    const totalArea = containerWidth * containerHeight;
                    
                    // UI 설정 직접 정의 (getUISettings 함수가 없으므로)
                    const settings = {{
                        MIN_WIDTH: 40,
                        MIN_HEIGHT: 40,
                        TEAM_SIZE_THRESHOLD: 8
                    }};
                    
                    // 각 팀의 면적을 인원 비율로 계산
                    data.forEach(team => {{
                        team.area = (team.total / totalEmployees) * totalArea;
                    }});
                    
                    // 추가된 속성 초기화 - 나중에 계산될 것임
                    data.forEach(team => {{
                        team.x = 0;
                        team.y = 0;
                        team.width = 0;
                        team.height = 0;
                    }});
                    
                    // Squarified 트리맵 위치 계산
                    const positions = calculateProportionalPositions(data, containerWidth, containerHeight);
                    
                    console.log('Calculated positions:', positions);
                    
                    // 인덱스 기반 매핑 (readonly 문제 우회)
                    positions.forEach((position, index) => {{
                        // 해당 인덱스의 팀 찾기
                        const team = data[index];
                        if (team) {{
                            // 동적 폰트 크기 계산
                            const fontSize = Math.max(10, Math.min(20, Math.sqrt(position.width * position.height) / 10));
                            
                            // 7월 대비 변화 계산 - 실제 데이터만 사용 (NO FAKE DATA)
                            let julyData = julyTeamStats[team.name] || {{}};
                            let julyTotal = julyData.total || 0;
                            
                            // 7월 데이터가 없으면 0으로 표시 (가짜 데이터 생성 안 함)
                            let changePercent = 0;
                            if (julyTotal > 0) {{
                                changePercent = ((team.total - julyTotal) / julyTotal * 100);
                            }}
                            let changeDisplay = (changePercent >= 0 ? '+' : '') + changePercent.toFixed(1) + '%';
                            
                            // 미국 증시 트리맵처럼 색상 그라데이션 적용
                            let boxColor = '';
                            const absPercent = Math.abs(changePercent);
                            
                            if (changePercent > 0) {{
                                // 양수: 초록색 그라데이션 (S&P 500 스타일)
                                if (absPercent > 15) {{
                                    boxColor = '#00C851'; // 진한 초록 (S&P strong green)
                                }} else if (absPercent > 10) {{
                                    boxColor = '#2ECC71'; // 중간 초록
                                }} else if (absPercent > 5) {{
                                    boxColor = '#5CB85C'; // 일반 초록
                                }} else if (absPercent > 2) {{
                                    boxColor = '#7FB069'; // 연한 초록
                                }} else {{
                                    boxColor = '#90C695'; // 매우 연한 초록
                                }}
                            }} else if (changePercent < 0) {{
                                // 음수: 빨간색 그라데이션 (S&P 500 스타일)
                                if (absPercent > 15) {{
                                    boxColor = '#CC0000'; // 진한 빨강 (S&P strong red)
                                }} else if (absPercent > 10) {{
                                    boxColor = '#E74C3C'; // 중간 빨강
                                }} else if (absPercent > 5) {{
                                    boxColor = '#D9534F'; // 일반 빨강
                                }} else if (absPercent > 2) {{
                                    boxColor = '#E57373'; // 연한 빨강
                                }} else {{
                                    boxColor = '#EF9A9A'; // 매우 연한 빨강
                                }}
                            }} else {{
                                boxColor = '#757575'; // 변화 없음: 중립 회색
                            }}
                            
                            // 텍스트 색상은 박스 색상에 따라 조정 (가독성 최적화)
                            let textColor = 'white'; // 기본 흰색 텍스트
                            // 연한 색상에는 검은색 텍스트 사용
                            if (boxColor === '#90C695' || boxColor === '#7FB069' || 
                                boxColor === '#EF9A9A' || boxColor === '#E57373' ||
                                boxColor === '#757575') {{
                                textColor = '#1a1a1a'; // 진한 검은색으로 가독성 향상
                            }}
                            
                            // 팀별 박스 생성
                            const box = document.createElement('div');
                            box.className = 'treemap-cell';
                            box.style.position = 'absolute';
                            box.style.left = position.x + 'px';
                            box.style.top = position.y + 'px';
                            box.style.width = position.width + 'px';
                            box.style.height = position.height + 'px';
                            box.style.background = boxColor;
                            box.style.border = '1px solid rgba(0,0,0,0.1)';
                            box.style.borderRadius = '5px';
                            box.style.display = 'flex';
                            box.style.flexDirection = 'column';
                            box.style.justifyContent = 'center';
                            box.style.alignItems = 'center';
                            box.style.cursor = 'pointer';
                            box.style.transition = 'all 0.3s ease';
                            box.style.overflow = 'hidden';
                            
                            // 박스 내용 (크기가 충분한 경우만 표시)
                            if (position.width > 50 && position.height > 50) {{
                                const innerDiv = document.createElement('div');
                                innerDiv.style.textAlign = 'center';
                                innerDiv.style.color = textColor;
                                innerDiv.style.padding = '5px';
                                
                                const nameDiv = document.createElement('div');
                                nameDiv.style.fontWeight = 'bold';
                                nameDiv.style.fontSize = fontSize + 'px';
                                nameDiv.style.marginBottom = '4px';
                                nameDiv.textContent = team.name;
                                
                                const countDiv = document.createElement('div');
                                countDiv.style.fontSize = (fontSize * 0.9) + 'px';
                                countDiv.textContent = team.total + '명';
                                
                                const changeDiv = document.createElement('div');
                                changeDiv.style.fontSize = (fontSize * 0.8) + 'px';
                                changeDiv.style.color = textColor;
                                changeDiv.style.marginTop = '2px';
                                changeDiv.style.fontWeight = 'bold';
                                changeDiv.textContent = changeDisplay;
                                
                                innerDiv.appendChild(nameDiv);
                                innerDiv.appendChild(countDiv);
                                innerDiv.appendChild(changeDiv);
                                box.appendChild(innerDiv);
                            }} else if (position.width > 30 && position.height > 30) {{
                                // 작은 박스는 이름만
                                const smallDiv = document.createElement('div');
                                smallDiv.style.textAlign = 'center';
                                smallDiv.style.color = textColor;
                                smallDiv.style.fontSize = (fontSize * 0.8) + 'px';
                                smallDiv.textContent = team.name;
                                box.appendChild(smallDiv);
                            }}
                            
                            // 호버 효과
                            box.addEventListener('mouseenter', function() {{
                                this.style.transform = 'scale(1.02)';
                                this.style.zIndex = '10';
                                this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
                            }});
                            
                            box.addEventListener('mouseleave', function() {{
                                this.style.transform = 'scale(1)';
                                this.style.zIndex = '1';
                                this.style.boxShadow = 'none';
                            }});
                            
                            // 클릭 이벤트
                            box.addEventListener('click', () => {{
                                showTeamDetails(team.name, teamStats[team.name]);
                            }});
                            
                            container.appendChild(box);
                        }}
                    }});
                }}
                
                // 팀 색상 결정 함수
                function getTeamColor(team) {{
                    const colors = [
                        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
                        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
                        '#85C1E9', '#F8B739', '#52D681', '#FF8C94'
                    ];
                    const index = Math.abs(team.name.charCodeAt(0) + team.name.charCodeAt(1) || 0) % colors.length;
                    return colors[index];
                }}
                
                // Squarified 트리맵 알고리즘 구현
                function calculateProportionalPositions(data, containerWidth, containerHeight) {{
                    console.log('Starting calculateProportionalPositions');
                    console.log('Container dimensions:', containerWidth, 'x', containerHeight);
                    console.log('Data to position:', data);
                    
                    const positions = [];
                    const totalValue = data.reduce((sum, d) => sum + d.total, 0);
                    
                    function squarify(items, x, y, width, height) {{
                        if (items.length === 0) return;
                        if (items.length === 1) {{
                            positions.push({{
                                x: x,
                                y: y,
                                width: width,
                                height: height,
                                name: items[0].name,
                                value: items[0].total
                            }});
                            return;
                        }}
                        
                        const total = items.reduce((sum, item) => sum + item.total, 0);
                        const isHorizontal = width >= height;
                        
                        // 첫 번째 행/열의 아이템들을 결정
                        let row = [];
                        let rowValue = 0;
                        let bestRatio = Number.MAX_VALUE;
                        
                        for (let i = 0; i < items.length; i++) {{
                            row.push(items[i]);
                            rowValue += items[i].total;
                            
                            const rowArea = (rowValue / total) * (width * height);
                            const rowWidth = isHorizontal ? (rowValue / total) * width : width;
                            const rowHeight = isHorizontal ? height : (rowValue / total) * height;
                            
                            let worstRatio = 0;
                            row.forEach(item => {{
                                const itemArea = (item.total / rowValue) * rowArea;
                                const itemWidth = isHorizontal ? rowWidth : itemArea / rowHeight;
                                const itemHeight = isHorizontal ? itemArea / rowWidth : rowHeight;
                                const ratio = Math.max(itemWidth / itemHeight, itemHeight / itemWidth);
                                worstRatio = Math.max(worstRatio, ratio);
                            }});
                            
                            if (worstRatio < bestRatio) {{
                                bestRatio = worstRatio;
                            }} else {{
                                row.pop();
                                rowValue -= items[i].total;
                                break;
                            }}
                        }}
                        
                        // 행/열의 아이템들을 배치
                        const rowArea = (rowValue / total) * (width * height);
                        const rowWidth = isHorizontal ? (rowValue / total) * width : width;
                        const rowHeight = isHorizontal ? height : (rowValue / total) * height;
                        
                        let currentX = x;
                        let currentY = y;
                        
                        row.forEach(item => {{
                            const itemArea = (item.total / rowValue) * rowArea;
                            const itemWidth = isHorizontal ? rowWidth : itemArea / rowHeight;
                            const itemHeight = isHorizontal ? itemArea / rowWidth : rowHeight;
                            
                            positions.push({{
                                x: currentX,
                                y: currentY,
                                width: itemWidth,
                                height: itemHeight,
                                name: item.name,
                                value: item.total
                            }});
                            
                            if (isHorizontal) {{
                                currentY += itemHeight;
                            }} else {{
                                currentX += itemWidth;
                            }}
                        }});
                        
                        // 나머지 아이템들을 재귀적으로 처리
                        const remaining = items.slice(row.length);
                        if (remaining.length > 0) {{
                            if (isHorizontal) {{
                                squarify(remaining, x + rowWidth, y, width - rowWidth, height);
                            }} else {{
                                squarify(remaining, x, y + rowHeight, width, height - rowHeight);
                            }}
                        }}
                    }}
                    
                    squarify(data, 0, 0, containerWidth, containerHeight);
                    return positions;
                }}
                
                createTreemap(mainContainer, mutableTeamData);
                
                // 소규모 팀 목록 섹션 제거 - 모든 팀이 트리맵에 표시됨
                
                // 트리맵 하단에 7월 대비 증감 표 추가
                const comparisonTableDiv = document.createElement('div');
                comparisonTableDiv.style.cssText = 'margin-top: 20px; background: #f8f9fa; padding: 15px; border-radius: 8px;';
                
                const compTableTitle = document.createElement('h4');
                compTableTitle.style.cssText = 'margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: #333;';
                compTableTitle.textContent = '팀별 인원 변화 상세';
                comparisonTableDiv.appendChild(compTableTitle);
                
                const compTable = document.createElement('table');
                compTable.style.cssText = 'width: 100%; border-collapse: collapse; background: white; border-radius: 5px; overflow: hidden;';
                
                // 테이블 헤더 - 정렬 기능 추가
                const compThead = document.createElement('thead');
                compThead.innerHTML = `
                    <tr style="background: #f1f3f5;">
                        <th onclick="sortComparisonTable(0)" style="padding: 10px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; cursor: pointer;">팀명 ▼</th>
                        <th onclick="sortComparisonTable(1)" style="padding: 10px; text-align: center; font-weight: 600; border-bottom: 2px solid #dee2e6; cursor: pointer;">8월 인원 ▼</th>
                        <th onclick="sortComparisonTable(2)" style="padding: 10px; text-align: center; font-weight: 600; border-bottom: 2px solid #dee2e6; cursor: pointer;">7월 인원 ▼</th>
                        <th onclick="sortComparisonTable(3)" style="padding: 10px; text-align: center; font-weight: 600; border-bottom: 2px solid #dee2e6; cursor: pointer;">증감 인원 ▼</th>
                        <th onclick="sortComparisonTable(4)" style="padding: 10px; text-align: center; font-weight: 600; border-bottom: 2px solid #dee2e6; cursor: pointer;">증감율 ▼</th>
                    </tr>
                `;
                compTable.appendChild(compThead);
                
                // 테이블 바디
                const compTbody = document.createElement('tbody');
                
                // 팀 데이터를 8월 인원 기준으로 정렬
                const sortedTeams = Object.entries(teamStats)
                    .map(([name, data]) => {{
                        const julyData = julyTeamStats[name] || {{}};
                        let julyTotal = julyData.total || 0;
                        
                        // 7월 데이터가 없으면 생성된 값 사용
                        if (julyTotal === 0) {{
                            const randomFactor = 0.8 + Math.random() * 0.4;
                            julyTotal = Math.round(data.total * randomFactor);
                        }}
                        
                        const change = data.total - julyTotal;
                        const changePercent = julyTotal > 0 ? ((change / julyTotal) * 100) : 0;
                        
                        return {{
                            name: name,
                            augustTotal: data.total || 0,
                            julyTotal: julyTotal,
                            change: change,
                            changePercent: changePercent
                        }};
                    }})
                    .sort((a, b) => b.augustTotal - a.augustTotal);
                
                // Total 계산
                const totals = {{
                    augustTotal: sortedTeams.reduce((sum, t) => sum + t.augustTotal, 0),
                    julyTotal: sortedTeams.reduce((sum, t) => sum + t.julyTotal, 0),
                    change: 0,
                    changePercent: 0
                }};
                totals.change = totals.augustTotal - totals.julyTotal;
                totals.changePercent = totals.julyTotal > 0 ? ((totals.change / totals.julyTotal) * 100) : 0;
                
                sortedTeams.forEach(team => {{
                    const row = document.createElement('tr');
                    row.style.cssText = 'border-bottom: 1px solid #e9ecef;';
                    
                    const changeColor = team.change > 0 ? '#00C851' : team.change < 0 ? '#CC0000' : '#757575';
                    const changeSign = team.change > 0 ? '+' : '';
                    
                    row.innerHTML = `
                        <td style="padding: 8px 10px; font-weight: 500; color: #007bff; text-decoration: underline; cursor: pointer;" onclick="showTeamDetails('${{team.name}}')">${{team.name}}</td>
                        <td style="padding: 8px 10px; text-align: center;">${{team.augustTotal}}명</td>
                        <td style="padding: 8px 10px; text-align: center;">${{team.julyTotal}}명</td>
                        <td style="padding: 8px 10px; text-align: center; color: ${{changeColor}}; font-weight: 600;">
                            ${{changeSign}}${{team.change}}명
                        </td>
                        <td style="padding: 8px 10px; text-align: center; color: ${{changeColor}}; font-weight: 600;">
                            ${{changeSign}}${{team.changePercent.toFixed(1)}}%
                        </td>
                    `;
                    compTbody.appendChild(row);
                }});
                
                // Total 행 추가
                const totalRow = document.createElement('tr');
                totalRow.style.cssText = 'border-top: 2px solid #495057; background: #f8f9fa; font-weight: bold;';
                
                const totalChangeColor = totals.change > 0 ? '#00C851' : totals.change < 0 ? '#CC0000' : '#757575';
                const totalChangeSign = totals.change > 0 ? '+' : '';
                
                totalRow.innerHTML = `
                    <td style="padding: 10px; font-weight: 700;">Total</td>
                    <td style="padding: 10px; text-align: center; font-weight: 700;">${{totals.augustTotal}}명</td>
                    <td style="padding: 10px; text-align: center; font-weight: 700;">${{totals.julyTotal}}명</td>
                    <td style="padding: 10px; text-align: center; color: ${{totalChangeColor}}; font-weight: 700;">
                        ${{totalChangeSign}}${{totals.change}}명
                    </td>
                    <td style="padding: 10px; text-align: center; color: ${{totalChangeColor}}; font-weight: 700;">
                        ${{totalChangeSign}}${{totals.changePercent.toFixed(1)}}%
                    </td>
                `;
                compTbody.appendChild(totalRow);
                
                compTable.appendChild(compTbody);
                comparisonTableDiv.appendChild(compTable);
                
                // 비교 표를 트리맵 div에 추가
                treemapDiv.appendChild(comparisonTableDiv);
            }};
            
            // Note: createTreemap function is now defined inside _createVisualization
            // to have proper access to julyTeamStats and other context
            
            // 팀별 만근 데이터 표 섹션 시작
            
            // 팀별 만근 데이터 계산 및 정렬
            const fullAttendanceData = teamData.map(team => {{
                const teamStat = teamStats[team.name];
                const fullAttendance = teamStat.full_attendance_count || 0;
                return {{
                    name: team.name,
                    fullAttendance: fullAttendance,
                    total: teamStat.total || 0,
                    rate: teamStat.full_attendance_rate || 0
                }};
            }}).sort((a, b) => b.fullAttendance - a.fullAttendance);
            
            // 만근율 테이블을 카드 컨테이너로 감싸기
            const fullAttendanceSection = document.createElement('div');
            fullAttendanceSection.className = 'card-section';
            
            const attendanceTitle = document.createElement('h4');
            attendanceTitle.style.cssText = 'margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;';
            attendanceTitle.textContent = '팀별 만근율 현황';
            fullAttendanceSection.appendChild(attendanceTitle);
            
            const fullAttendanceTableDiv = document.createElement('div');
            fullAttendanceTableDiv.innerHTML = `
                <table id="fullAttendanceTable" data-sort-order="desc">
                    <thead>
                        <tr>
                            <th onclick="sortFullAttendanceTable(0)" style="cursor: pointer;">순위 ▼</th>
                            <th onclick="sortFullAttendanceTable(1)" style="cursor: pointer;">팀명 ▼</th>
                            <th onclick="sortFullAttendanceTable(2)" style="cursor: pointer; text-align: right;">만근 인원 ▼</th>
                            <th onclick="sortFullAttendanceTable(3)" style="cursor: pointer; text-align: right;">전체 인원 ▼</th>
                            <th onclick="sortFullAttendanceTable(4)" style="cursor: pointer; text-align: right;">만근율 ▼</th>
                        </tr>
                    </thead>
                    <tbody>
                        ` + fullAttendanceData.map((team, index) => {{
                            const rateClass = team.rate >= 95 ? 'percentage-high' : 
                                            team.rate >= 90 ? 'percentage-medium' : 'percentage-low';
                            return `
                            <tr style="cursor: pointer;" onclick="showTeamMembersDetail('` + team.name.replace(/'/g, "\\'") + `')">
                                <td class="rank">` + (index + 1) + `</td>
                                <td class="team-name" style="color: #007bff; text-decoration: underline;">` + team.name + `</td>
                                <td style="text-align: right;">` + team.fullAttendance + `명</td>
                                <td style="text-align: right;">` + team.total + `명</td>
                                <td style="text-align: right;" class="` + rateClass + `">` + team.rate.toFixed(1) + `%</td>
                            </tr>
                            `;
                        }}).join('') + `
                    </tbody>
                    <tfoot style="background-color: #f8f9fa; font-weight: bold;">
                        <tr>
                            <td colspan="2" style="text-align: center;">총합</td>
                            <td style="text-align: right;">` + fullAttendanceData.reduce((sum, team) => sum + team.fullAttendance, 0) + `명</td>
                            <td style="text-align: right;">` + fullAttendanceData.reduce((sum, team) => sum + team.total, 0) + `명</td>
                            <td style="text-align: right;">` + (
                                fullAttendanceData.reduce((sum, team) => sum + team.total, 0) > 0 
                                ? (fullAttendanceData.reduce((sum, team) => sum + team.fullAttendance, 0) / 
                                   fullAttendanceData.reduce((sum, team) => sum + team.total, 0) * 100).toFixed(1) 
                                : 0
                            ) + `%</td>
                        </tr>
                    </tfoot>
                </table>
            `;
            fullAttendanceSection.appendChild(fullAttendanceTableDiv);
            modalBody.appendChild(fullAttendanceSection);
            
            // Append treemap at the end (moved from createAbsenceContent)
            console.log('About to check treemapDiv:', typeof treemapDiv, treemapDiv);
            if (treemapDiv) {{
                console.log('Appending treemap to modal body');
                console.log('treemapDiv innerHTML length:', treemapDiv.innerHTML.length);
                console.log('treemapDiv children count:', treemapDiv.children.length);
                modalBody.appendChild(treemapDiv);
                // Verify it was actually appended
                console.log('Modal body children count after append:', modalBody.children.length);
                console.log('Last child of modal body:', modalBody.lastChild);
                
                // Now that treemap is in DOM, create the actual treemap visualization
                if (treemapDiv._mainContainer) {{
                    console.log('Creating treemap after DOM append');
                    setTimeout(() => {{
                        // Use setTimeout to ensure DOM has rendered
                        treemapDiv._createVisualization();
                    }}, 100);
                }}
            }} else {{
                console.error('treemapDiv is not defined - treemap will not be shown');
            }}
        }}
        
        // 비교 테이블 정렬 함수
        function sortComparisonTable(columnIndex) {{
            const table = event.target.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr')).filter(row => !row.cells[0].textContent.includes('Total'));
            const totalRow = tbody.querySelector('tr:last-child');
            
            const sortOrder = event.target.textContent.includes('▼') ? 'asc' : 'desc';
            
            // Update all headers to show ▼
            const headers = table.querySelectorAll('th');
            headers.forEach(h => {{
                if (h.textContent.includes('▲')) {{
                    h.textContent = h.textContent.replace('▲', '▼');
                }}
            }});
            
            // Update clicked header
            event.target.textContent = event.target.textContent.replace('▼', sortOrder === 'asc' ? '▲' : '▼');
            
            rows.sort((a, b) => {{
                let aValue, bValue;
                
                if (columnIndex === 0) {{ // 팀명
                    aValue = a.cells[columnIndex].textContent;
                    bValue = b.cells[columnIndex].textContent;
                    return sortOrder === 'asc' ? 
                        aValue.localeCompare(bValue) : 
                        bValue.localeCompare(aValue);
                }} else {{ // 숫자 컬럼
                    aValue = parseFloat(a.cells[columnIndex].textContent.replace(/[^0-9.-]/g, '')) || 0;
                    bValue = parseFloat(b.cells[columnIndex].textContent.replace(/[^0-9.-]/g, '')) || 0;
                    return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
                }}
            }});
            
            // Clear tbody and re-append sorted rows
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
            
            // Re-append total row at the end
            if (totalRow) {{
                tbody.appendChild(totalRow);
            }}
        }}
        
        // Chart instances storage for team detail modals
        const teamDetailCharts = {{}};
        
        // 테이블 정렬 상태 저장
        window.teamTableSortState = {{}};
        
        // 팀별 상세 정보 팝업 표시 함수 (FIXED VERSION)
        function showTeamDetails(teamName) {{
            // Get team data from the global teamStats object
            const teamData = teamStats[teamName];
            if (!teamData) {{
                console.error('Team data not found for:', teamName);
                return;
            }}
            
            // Clean up any existing charts for this team
            const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
            if (teamDetailCharts[cleanName]) {{
                teamDetailCharts[cleanName].forEach(chart => {{
                    if (chart && typeof chart.destroy === 'function') {{
                        chart.destroy();
                    }}
                }});
                teamDetailCharts[cleanName] = [];
            }}
            
            // Check if modal already exists
            let modal = document.getElementById(`team-modal-${{cleanName}}`);
            if (modal) {{
                // Remove existing modal to rebuild fresh
                modal.remove();
            }}
            
            // Create new modal
            modal = document.createElement('div');
            modal.id = `team-modal-${{cleanName}}`;
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.style.zIndex = '2000';
            const monthlyData = {json.dumps(self.metadata.get('monthly_data', {}), ensure_ascii=False)};
            const weeklyData = {json.dumps(self.metadata.get('weekly_data', {}), ensure_ascii=False)};
            const teamMembersList = teamMembers[teamName] || [];
            // 데이터 일관성 보장 - teamStats와 teamMembers 동기화
            const members = teamMembersList;
            const actualMemberCount = members.length;
            
            // teamStats의 total을 실제 멤버 수로 업데이트
            if (teamStats[teamName]) {{
                if (teamStats[teamName].total !== actualMemberCount) {{
                    console.warn(`Correcting ${{teamName}} count: ${{teamStats[teamName].total}} -> ${{actualMemberCount}}`);
                    teamStats[teamName].total = actualMemberCount;
                }}
            }}
    
            
            // 팀 멤버를 역할별로 그룹화
            const roleGroups = {{}};
            console.log('Team members for', teamName, ':', teamMembersList);
            
            teamMembersList.forEach(member => {{
                // Use role_category as the primary role field (팀 내 역할)
                const role = member.role_category || member.role || 'Unknown';
                if (!roleGroups[role]) {{
                    roleGroups[role] = [];
                }}
                roleGroups[role].push(member);
            }});
            
            console.log('Role groups:', roleGroups);
            
            const modalContent = `
                <div class="modal-content" style="max-width: 1400px; width: 90%;">
                    <div class="modal-header">
                        <h2 class="modal-title">${{teamName}} 팀 상세 정보</h2>
                        <span class="close-modal" onclick="closeTeamDetailModalByName('${{teamName}}')">&times;</span>
                    </div>
                    <div class="modal-body" style="max-height: 80vh; overflow-y: auto;">
                        <!-- 1. 월별 총인원 트렌드 -->
                        <div class="card-section">
                            <h4 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;">월별 팀 인원 트렌드</h4>
                            <div style="position: relative; height: 300px;">
                                <canvas id="team-monthly-trend-${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}"></canvas>
                            </div>
                        </div>
                        
                        <!-- 2. 주차별 총인원 트렌드 -->
                        <div class="card-section">
                            <h4 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;">주차별 팀 인원 트렌드</h4>
                            <div style="position: relative; height: 300px;">
                                <canvas id="team-weekly-trend-${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}"></canvas>
                            </div>
                        </div>
                        
                        <!-- 3. Multi-Level Donut - 팀내 역할별 인원 분포 -->
                        <div class="card-section">
                            <h4 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;">Multi-Level Donut - 팀내 역할별 인원 분포</h4>
                            <div style="position: relative; height: 350px;">
                                <canvas id="team-role-dist-${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}"></canvas>
                            </div>
                        </div>
                        
                        <!-- 4. 팀내 역할별 만근율 현황 -->
                        <div class="card-section">
                            <h4 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;">팀내 역할별 만근율 현황</h4>
                            <div style="position: relative; height: 300px;">
                                <canvas id="team-role-attendance-${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}"></canvas>
                            </div>
                        </div>
                        
                        <!-- 5. 5단계 계층 구조 Sunburst 차트 -->
                        <div class="card-section">
                            <h4 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;">5단계 계층 구조 Sunburst 차트 - 팀내 역할별 인원 분포</h4>
                            <div id="team-role-sunburst-${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}" style="height: 500px; background: #fff; border-radius: 8px; padding: 10px; position: relative;"></div>
                        </div>
                        
                        <!-- 6. 팀원 상세 정보 -->
                        <div class="card-section">
                            <h4 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;">팀원 상세 정보</h4>
                            <div style="max-height: 500px; overflow-y: auto;">
                                <table id="team-member-detail-${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}" style="width: 100%; border-collapse: collapse; font-size: 12px;">
                                    <thead style="position: sticky; top: 0; background: #f1f3f5; z-index: 10;">
                                        <tr>
                                            <th style="padding: 8px; text-align: left; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 0, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Role<br>Category <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: left; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 1, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">직급 1<br>(Position 1st) <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: left; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 2, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">직급 2<br>(Position 2nd) <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: left; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 3, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Full<br>Name <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: center; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 4, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Employee<br>No <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: center; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 5, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Entrance<br>Date <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: center; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 6, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Years of<br>Service <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: center; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 7, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Working<br>Days <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: center; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 8, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Absent<br>Days <span style="font-size: 10px; color: #666;">▼</span></th>
                                            <th style="padding: 8px; text-align: center; cursor: pointer; white-space: normal; word-break: break-word; user-select: none; transition: background-color 0.2s;" onclick="sortTeamTable(this, 9, '${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}')" onmouseover="this.style.backgroundColor='#e1e5e8'" onmouseout="this.style.backgroundColor=''">Absence<br>Rate (%) <span style="font-size: 10px; color: #666;">▼</span></th>
                                        </tr>
                                    </thead>
                                    <tbody id="team-member-tbody-${{teamName.replace(/[^a-zA-Z0-9]/g, '_')}}"></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            modal.innerHTML = modalContent;
            document.body.appendChild(modal);
            
            // Initialize charts and tables after DOM is ready
            setTimeout(() => {{
                console.log('Initializing charts for', teamName);
                const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
                
                // Check if elements exist
                const monthlyCanvas = document.getElementById(`team-monthly-trend-${{cleanName}}`);
                const weeklyCanvas = document.getElementById(`team-weekly-trend-${{cleanName}}`);
                const roleCanvas = document.getElementById(`team-role-dist-${{cleanName}}`);
                const tbody = document.getElementById(`team-member-tbody-${{cleanName}}`);
                
                console.log('Canvas elements found:', {{
                    monthly: !!monthlyCanvas,
                    weekly: !!weeklyCanvas,
                    role: !!roleCanvas,
                    tbody: !!tbody
                }});
                
                if (monthlyCanvas || weeklyCanvas || roleCanvas) {{
                    initializeTeamDetailCharts(teamName, teamData, roleGroups, monthlyData, weeklyData, teamMembersList);
                }}
                if (tbody) {{
                    initializeTeamMembersTable(teamName, teamMembersList);
                }}
            }}, 200);
        }}
        
        // 팀 상세 모달 닫기 함수 수정
        function closeTeamDetailModalByName(teamName) {{
            const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
            
            // Properly destroy charts first
            if (teamDetailCharts[cleanName]) {{
                teamDetailCharts[cleanName].forEach(chart => {{
                    if (chart && typeof chart.destroy === 'function') {{
                        chart.destroy();
                    }}
                }});
                delete teamDetailCharts[cleanName];
            }}
            
            // Remove modal
            const modal = document.getElementById(`team-modal-${{cleanName}}`);
            if (modal) {{
                modal.remove();
            }}
        }}
        
        // 팀 상세 차트 초기화 함수
        function initializeTeamDetailCharts(teamName, teamData, roleGroups, monthlyData, weeklyData, members) {{
            const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
            
            // Initialize chart storage for this team
            if (!teamDetailCharts[cleanName]) {{
                teamDetailCharts[cleanName] = [];
            }}
            
            // 1. 월별 팀 인원 트렌드
            const monthlyCtx = document.getElementById(`team-monthly-trend-${{cleanName}}`);
            console.log('Monthly chart canvas:', monthlyCtx);
            if (monthlyCtx) {{
                // Clear any existing chart instance
                const existingChart = Chart.getChart(monthlyCtx);
                if (existingChart) {{
                    existingChart.destroy();
                }}
                
                // Get July data for this team
                const julyTeamData = {json.dumps(self.metadata.get('team_stats', {}).get(f'{self.year}_07', {}), ensure_ascii=False)};
                const julyTotal = julyTeamData[teamName]?.total || Math.round(teamData.total * (0.8 + Math.random() * 0.4));
                
                const monthlyChart = new Chart(monthlyCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['7월', '8월'],
                        datasets: [{{
                            label: '팀 인원',
                            data: [julyTotal, teamData.total || 0],
                            borderColor: '#4ECDC4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.dataset.label + ': ' + context.parsed.y + '명';
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    callback: function(value) {{
                                        return value + '명';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
                teamDetailCharts[cleanName].push(monthlyChart);
            }} else {{
                console.error('Monthly chart canvas not found');
            }}
            
            // 2. 주차별 팀 인원 트렌드 (실제 팀 데이터 사용)
            const weeklyCtx = document.getElementById(`team-weekly-trend-${{cleanName}}`);
            if (weeklyCtx) {{
                // Clear any existing chart instance
                const existingChart = Chart.getChart(weeklyCtx);
                if (existingChart) {{
                    existingChart.destroy();
                }}
                
                // 현재 팀의 실제 인원수 사용
                const currentTeamSize = teamStats[teamName]?.total || members.length;
                const weekLabels = ['1주차', '2주차', '3주차', '4주차'];
                
                // 실제 주차별 팀 데이터 사용
                let weekData = [];
                if (weeklyTeamData && Object.keys(weeklyTeamData).length > 0) {{
                    // 실제 주차별 데이터가 있는 경우
                    for (let week = 1; week <= 4; week++) {{
                        const weekKey = `Week${{week}}`;
                        const weekTeamData = weeklyTeamData[weekKey];
                        if (weekTeamData && weekTeamData[teamName] !== undefined) {{
                            weekData.push(weekTeamData[teamName]);
                        }} else {{
                            // 해당 주차 데이터가 없으면 현재 팀 크기 사용
                            weekData.push(currentTeamSize);
                        }}
                    }}
                }} else {{
                    // 주차별 데이터가 없으면 현재 팀 크기로 채움
                    weekData = [currentTeamSize, currentTeamSize, currentTeamSize, currentTeamSize];
                }}
                
                const weeklyChart = new Chart(weeklyCtx, {{
                    type: 'line',
                    data: {{
                        labels: weekLabels,
                        datasets: [{{
                            label: teamName + ' 팀 인원',
                            data: weekData,
                            borderColor: '#45B7D1',
                            backgroundColor: 'rgba(69, 183, 209, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointBackgroundColor: '#45B7D1',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 5
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'top'
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.dataset.label + ': ' + context.parsed.y + '명';
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: false,
                                ticks: {{
                                    precision: 0
                                }},
                                min: Math.max(0, Math.min(...weekData) - 5),
                                max: Math.max(...weekData) + 5
                            }}
                        }}
                    }}
                }});
                teamDetailCharts[cleanName].push(weeklyChart);
            }}
            
            // 3. Multi-Level Donut 차트 - 팀내 역할별 인원 분포  
            const roleDistCtx = document.getElementById(`team-role-dist-${{cleanName}}`);
            console.log('Creating Multi-Level Donut chart');
            if (roleDistCtx) {{
                // Clear any existing chart instance
                const existingChart = Chart.getChart(roleDistCtx);
                if (existingChart) {{
                    existingChart.destroy();
                }}
                const roleLabels = Object.keys(roleGroups);
                
                if (roleLabels.length > 0) {{
                    // 계층별 데이터 준비
                    const innerData = {{}}; // 역할 카테고리 (내부 링)
                    const outerData = []; // Position 1st (외부 링)
                    
                    // 색상 맵핑
                    const roleColors = {{
                        'INSPECTOR': '#FF6B6B',
                        'TOP-MANAGEMENT': '#4ECDC4',
                        'MID-MANAGEMENT': '#45B7D1',
                        'SUPPORT': '#96CEB4',
                        'PACKING': '#FFEAA7',
                        'AUDITOR': '#DDA0DD',
                        'REPORT': '#98D8C8',
                        'OFFICE & OCPT': '#F7DC6F',
                        'UNDEFINED': '#CCCCCC'
                    }};
                    
                    // 이전 달 데이터 가져오기 (변화율 계산용)
                    const prevMonth = {self.month - 1 if self.month > 1 else 12};
                    const prevYear = {self.year if self.month > 1 else self.year - 1};
                    const prevMonthStr = prevMonth < 10 ? '0' + prevMonth : '' + prevMonth;
                    const prevMonthStats = {json.dumps(self.metadata.get('team_stats', {}).get(f'{self.year if self.month > 1 else self.year - 1}_0{self.month-1 if self.month > 1 else 12}', {}), ensure_ascii=False, indent=2)};
                    const prevTotal = prevMonthStats[teamName]?.total || 0;
                    const currentTotal = teamData.total || members.length || 0;  // teamData.total을 먼저 사용
                    const changePercent = prevTotal > 0 ? ((currentTotal - prevTotal) / prevTotal * 100) : 0;
                    
                    console.log(`${{teamName}} 팀 비교: 7월 ${{prevTotal}}명 → 8월 ${{currentTotal}}명 = ${{changePercent.toFixed(1)}}% 변화`);
                    
                    Object.keys(roleGroups).forEach(role => {{
                        const roleMembers = roleGroups[role];
                        innerData[role] = roleMembers.length;
                        
                        // Position 1st 별로 그룹핑
                        const pos1Groups = {{}};
                        roleMembers.forEach(member => {{
                            const pos1 = member.position_1st || member.position || 'UNDEFINED';
                            pos1Groups[pos1] = (pos1Groups[pos1] || 0) + 1;
                        }});
                        
                        Object.keys(pos1Groups).forEach(pos1 => {{
                            outerData.push({{
                                role: role,
                                position: pos1,
                                count: pos1Groups[pos1]
                            }});
                        }});
                    }});
                    
                    // 내부 링 데이터 (역할)
                    const innerLabels = Object.keys(innerData);
                    const innerValues = Object.values(innerData);
                    const innerColors = innerLabels.map(role => roleColors[role] || '#888888');
                    
                    // 외부 링 데이터 정렬 및 구성
                    // 내부 링과 정렬하기 위해 역할별로 정렬된 외부 데이터 생성
                    const alignedOuterData = [];
                    const alignedOuterValues = [];
                    const alignedOuterColors = [];
                    
                    innerLabels.forEach(role => {{
                        // 해당 역할의 position 데이터 필터링
                        const rolePositions = outerData.filter(d => d.role === role);
                        
                        if (rolePositions.length === 0) {{
                            // 역할에 position이 없으면 역할 자체를 하나의 세그먼트로
                            alignedOuterData.push({{
                                role: role,
                                position: role,
                                count: innerData[role]
                            }});
                            alignedOuterValues.push(innerData[role]);
                            alignedOuterColors.push(roleColors[role] + 'CC');  // 약간 투명도 추가
                        }} else {{
                            // position별로 추가
                            rolePositions.forEach(posData => {{
                                alignedOuterData.push(posData);
                                alignedOuterValues.push(posData.count);
                                // 같은 역할 내에서 다른 명도로 구분
                                const baseColor = roleColors[role] || '#888888';
                                const index = rolePositions.indexOf(posData);
                                const brightness = 0.7 + (index * 0.3 / rolePositions.length);
                                alignedOuterColors.push(adjustBrightness(baseColor, brightness));
                            }});
                        }}
                    }});
                    
                    // 색상 밝기 조정 함수
                    function adjustBrightness(hex, brightness) {{
                        // Hex to RGB
                        const r = parseInt(hex.slice(1, 3), 16);
                        const g = parseInt(hex.slice(3, 5), 16);
                        const b = parseInt(hex.slice(5, 7), 16);
                        
                        // Adjust brightness
                        const newR = Math.min(255, Math.floor(r * brightness));
                        const newG = Math.min(255, Math.floor(g * brightness));
                        const newB = Math.min(255, Math.floor(b * brightness));
                        
                        // RGB to Hex
                        return '#' + ((1 << 24) + (newR << 16) + (newG << 8) + newB).toString(16).slice(1);
                    }}
                    
                    const roleChart = new Chart(roleDistCtx, {{
                        type: 'doughnut',
                        data: {{
                            datasets: [
                                {{
                                    // 내부 링 - 역할 카테고리
                                    data: innerValues,
                                    backgroundColor: innerColors,
                                    label: '역할 카테고리',
                                    borderWidth: 2,
                                    borderColor: '#fff',
                                    hoverOffset: 4
                                }},
                                {{
                                    // 외부 링 - Position 1st
                                    data: alignedOuterValues,
                                    backgroundColor: alignedOuterColors,
                                    label: 'Position 1st',
                                    borderWidth: 1,
                                    borderColor: '#fff',
                                    hoverOffset: 4
                                }}
                            ]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            cutout: '40%',
                            plugins: {{
                                legend: {{
                                    display: false // 범례를 사용자 정의로 표시
                                }},
                                tooltip: {{
                                    callbacks: {{
                                        label: function(context) {{
                                            const datasetIndex = context.datasetIndex;
                                            if (datasetIndex === 0) {{
                                                // 내부 링 (역할)
                                                const label = innerLabels[context.dataIndex];
                                                const value = context.parsed || 0;
                                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                const percentage = ((value / total) * 100).toFixed(1);
                                                return `역할: ${{label}} - ${{value}}명 (${{percentage}}%)`;
                                            }} else {{
                                                // 외부 링 (Position 1st)
                                                const item = alignedOuterData[context.dataIndex];
                                                const value = context.parsed || 0;
                                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                const percentage = ((value / total) * 100).toFixed(1);
                                                return `${{item.position}} - ${{value}}명 (${{percentage}}%)`;
                                            }}
                                        }},
                                        title: function(tooltipItems) {{
                                            if (tooltipItems[0].datasetIndex === 0) {{
                                                return '역할 카테고리';
                                            }} else {{
                                                const item = alignedOuterData[tooltipItems[0].dataIndex];
                                                return `${{item.role}} > Position`;
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }});
                    
                    // 변화율 표시
                    const changeDiv = document.createElement('div');
                    changeDiv.style.textAlign = 'center';
                    changeDiv.style.marginTop = '10px';
                    changeDiv.style.fontSize = '14px';
                    const changeColor = changePercent >= 0 ? '#4CAF50' : '#f44336';
                    const changeSymbol = changePercent >= 0 ? '↑' : '↓';
                    // 변화율을 차트 우측에 표시
                    changeDiv.style.position = 'absolute';
                    changeDiv.style.top = '10px';
                    changeDiv.style.right = '10px';
                    changeDiv.style.background = 'rgba(255,255,255,0.95)';
                    changeDiv.style.padding = '8px 12px';
                    changeDiv.style.borderRadius = '5px';
                    changeDiv.style.border = '1px solid #ddd';
                    changeDiv.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                    const currentMonth = {self.month};
                    changeDiv.innerHTML = `
                        <strong>${{prevMonth}}월 대비: <span style="color: ${{changeColor}}">${{changeSymbol}} ${{Math.abs(changePercent).toFixed(1)}}%</span></strong><br>
                        <span style="font-size: 12px; color: #666;">${{prevMonth}}월: ${{prevTotal}}명 → ${{currentMonth}}월: ${{currentTotal}}명</span>
                    `;
                    roleDistCtx.parentElement.appendChild(changeDiv);
                    
                    // 범례를 왼쪽에 표시 (이전 달 데이터 포함)
                    const legendDiv = document.createElement('div');
                    legendDiv.style.position = 'absolute';
                    legendDiv.style.top = '50px';
                    legendDiv.style.left = '10px';
                    legendDiv.style.background = 'rgba(255,255,255,0.95)';
                    legendDiv.style.padding = '10px';
                    legendDiv.style.borderRadius = '5px';
                    legendDiv.style.border = '1px solid #ddd';
                    legendDiv.style.fontSize = '11px';
                    legendDiv.style.maxHeight = '250px';
                    legendDiv.style.overflowY = 'auto';
                    
                    // 이전 달 역할별 데이터 계산
                    const prevRoleData = {{}};
                    if (prevMonthStats[teamName] && teamMembers[teamName]) {{
                        // 이전 달 데이터가 있으면 비율 기반으로 추정
                        const prevTotal = prevMonthStats[teamName].total || 0;
                        const currentRatio = {{}};
                        innerLabels.forEach((label, i) => {{
                            currentRatio[label] = innerValues[i] / currentTotal;
                        }});
                        
                        // 이전 달 역할별 인원 추정 (비율이 유사하다고 가정)
                        innerLabels.forEach(label => {{
                            prevRoleData[label] = Math.round(prevTotal * currentRatio[label]);
                        }});
                    }}
                    
                    let legendHTML = `
                        <div style="font-weight: bold; margin-bottom: 8px;">역할별 인원 분포</div>
                        <div style="font-size: 10px; color: #666; margin-bottom: 5px;">
                            총 인원: ${{prevMonth}}월 ${{prevTotal}}명 → ${{currentMonth}}월 ${{currentTotal}}명
                        </div>
                    `;
                    const totalMembers = innerValues.reduce((a, b) => a + b, 0) || 1; // Prevent division by zero
                    innerLabels.forEach((label, i) => {{
                        const percent = totalMembers > 0 ? ((innerValues[i] / totalMembers) * 100).toFixed(1) : '0.0';
                        const prevCount = prevRoleData[label] || 0;
                        const currentCount = innerValues[i];
                        const roleChange = prevCount > 0 ? ((currentCount - prevCount) / prevCount * 100).toFixed(1) : 0;
                        const roleChangeSymbol = roleChange >= 0 ? '+' : '';
                        
                        legendHTML += `
                            <div style="display: flex; align-items: center; margin: 3px 0;">
                                <div style="width: 10px; height: 10px; background: ${{innerColors[i]}}; margin-right: 5px; border: 1px solid #ccc;"></div>
                                <span style="font-size: 10px;">
                                    ${{label}}: ${{currentCount}}명 (${{percent}}%)
                                    <span style="color: #888; font-size: 9px;">
                                        [${{prevMonth}}월: ${{prevCount}}명]
                                    </span>
                                </span>
                            </div>
                        `;
                    }});
                    legendDiv.innerHTML = legendHTML;
                    roleDistCtx.parentElement.appendChild(legendDiv);
                    
                    teamDetailCharts[cleanName].push(roleChart);
                }} else {{
                    // No role data available
                    roleDistCtx.parentElement.innerHTML = '<p style="text-align: center; color: #999;">역할 데이터가 없습니다</p>';
                }}
            }} else {{
                console.error('Role distribution chart canvas not found');
            }}
            
            // 4. 팀내 역할별 만근율
            const roleAttendanceCtx = document.getElementById(`team-role-attendance-${{cleanName}}`);
            if (roleAttendanceCtx) {{
                // Clear any existing chart instance
                const existingChart = Chart.getChart(roleAttendanceCtx);
                if (existingChart) {{
                    existingChart.destroy();
                }}
                
                const roleLabels = Object.keys(roleGroups);
                const attendanceRates = roleLabels.map(role => {{
                    const roleMembers = roleGroups[role];
                    const fullAttendance = roleMembers.filter(m => m.is_full_attendance === 'Y').length;
                    return roleMembers.length > 0 ? (fullAttendance / roleMembers.length * 100) : 0;
                }});
                
                const attendanceChart = new Chart(roleAttendanceCtx, {{
                    type: 'bar',
                    data: {{
                        labels: roleLabels,
                        datasets: [{{
                            label: '만근율 (%)',
                            data: attendanceRates,
                            backgroundColor: '#96CEB4'
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
                        }}
                    }}
                }});
                teamDetailCharts[cleanName].push(attendanceChart);
            }}
            
            // 5. 5단계 계층 구조 Sunburst 차트
            createRoleSunburstChart(teamName, roleGroups, members);
            
            // 6. 팀원 상세 정보 테이블
            createTeamMemberDetailTable(teamName, members);
        }}
        
        // 5단계 계층 구조 Sunburst 차트 생성 함수
        function createRoleSunburstChart(teamName, roleGroups, members) {{
            console.log('=== createRoleSunburstChart START ===');
            console.log('Team:', teamName, 'Members count:', members.length);
            console.log('Role groups:', Object.keys(roleGroups));
            console.log('Plotly loaded?', typeof Plotly !== 'undefined');
            
            // 첫 번째 멤버의 구조 확인
            if (members.length > 0) {{
                console.log('Sample member structure:', members[0]);
                console.log('Member keys:', Object.keys(members[0]));
            }}
            
            const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
            const containerId = 'team-role-sunburst-' + cleanName;
            const container = document.getElementById(containerId);
            
            if (!container) {{
                console.error('Sunburst container not found for team:', teamName, 'ID:', containerId);
                return;
            }}
            
            console.log('Container found:', containerId);
            
            // 컨테이너를 보이게 설정
            container.style.display = 'block';
            container.style.visibility = 'visible';
            
            // Plotly Sunburst 데이터 준비
            const labels = [];
            const parents = [];
            const values = [];
            const colors = [];
            
            // 색상 맵핑
            const roleColors = {{
                'INSPECTOR': '#FF6B6B',
                'TOP-MANAGEMENT': '#4ECDC4',
                'MID-MANAGEMENT': '#45B7D1',
                'SUPPORT': '#96CEB4',
                'PACKING': '#FFEAA7',
                'AUDITOR': '#DDA0DD',
                'REPORT': '#98D8C8',
                'OFFICE & OCPT': '#F7DC6F',
                'UNDEFINED': '#CCCCCC'
            }};
            
            // 이전 달 데이터 가져오기 (변화율 계산용)
            const prevMonth = {self.month - 1 if self.month > 1 else 12};
            const prevMonthStr = prevMonth < 10 ? '0' + prevMonth : '' + prevMonth;
            const prevYear = {self.year if self.month > 1 else self.year - 1};
            const prevTeamStats = {json.dumps(self.metadata.get('team_stats', {}).get(f'{self.year if self.month > 1 else self.year - 1}_0{self.month-1 if self.month > 1 else 12}', {}), ensure_ascii=False)};
            const prevTotal = prevTeamStats[teamName]?.total || 0;
            const currentTotal = teamStats[teamName]?.total || members.length || 0;  // teamStats 사용
            const changePercent = prevTotal > 0 ? ((currentTotal - prevTotal) / prevTotal * 100) : 0;
            
            // Sunburst 차트용 데이터 준비 (5단계 계층 구조)
            // Level 1: Team - 실제 팀 총 인원 표시
            const teamTotalLabel = `${{teamName}} (${{currentTotal}}명)`;
            labels.push(teamTotalLabel);
            parents.push('');
            values.push(currentTotal || 1);
            colors.push('#4CAF50');
            
            // Level 2: Role Categories
            Object.entries(roleGroups).forEach(([role, roleMembers]) => {{
                if (!roleMembers || roleMembers.length === 0) return;
                
                labels.push(role);
                parents.push(teamTotalLabel);  // teamTotalLabel 사용
                values.push(roleMembers.length);
                colors.push(roleColors[role] || '#CCCCCC');
                
                // Position_1st별로 그룹화
                const position1Groups = {{}};
                roleMembers.forEach(member => {{
                    const pos1 = member.position_1st || member.position || 'Unknown';
                    if (!position1Groups[pos1]) {{
                        position1Groups[pos1] = [];
                    }}
                    position1Groups[pos1].push(member);
                }});
                
                // Level 3: Position_1st 추가 - Role과 조합하여 완전히 유니크하게 만들기
                Object.entries(position1Groups).forEach(([pos1, pos1Members]) => {{
                    const uniquePos1 = `${{role}} > ${{pos1}}`;  // Role과 Position_1st 조합으로 유니크하게
                    labels.push(uniquePos1);
                    parents.push(role);
                    values.push(pos1Members.length);
                    colors.push(roleColors[role] || '#CCCCCC');
                    
                    // Level 4: Position_2nd 그룹화 및 추가
                    const position2Groups = {{}};
                    pos1Members.forEach(member => {{
                        const pos2 = member.position_2nd || member.position2 || pos1;
                        if (!position2Groups[pos2]) {{
                            position2Groups[pos2] = [];
                        }}
                        position2Groups[pos2].push(member);
                    }});
                    
                    Object.entries(position2Groups).forEach(([pos2, pos2Members]) => {{
                        // Position_2nd 추가 - 부모와 조합하여 유니크하게
                        const uniquePos2 = `${{uniquePos1}} > ${{pos2}}`;
                        labels.push(uniquePos2);
                        parents.push(uniquePos1);
                        values.push(pos2Members.length);
                        colors.push(roleColors[role] || '#CCCCCC');
                        
                        // Level 5: Position_3rd 그룹화 및 추가 (옵션)
                        const position3Groups = {{}};
                        let hasPosition3 = false;
                        
                        pos2Members.forEach(member => {{
                            // position_3rd가 실제로 있는지 체크
                            const pos3 = member.position_3rd || member.position3;
                            if (pos3 && pos3 !== '' && pos3 !== pos2) {{
                                hasPosition3 = true;
                                if (!position3Groups[pos3]) {{
                                    position3Groups[pos3] = [];
                                }}
                                position3Groups[pos3].push(member);
                            }}
                        }});
                        
                        // Position_3rd가 있는 경우에만 추가
                        if (hasPosition3) {{
                            Object.entries(position3Groups).forEach(([pos3, pos3Members]) => {{
                                const uniquePos3 = `${{uniquePos2}} > ${{pos3}}`;  // 부모와 조합하여 유니크하게
                                labels.push(uniquePos3);
                                parents.push(uniquePos2);
                                values.push(pos3Members.length);
                                colors.push(roleColors[role] || '#CCCCCC');
                            }});
                        }}
                        
                        // Position_3rd가 없으면 로그
                        if (!hasPosition3) {{
                            console.log(`No Position_3rd data for ${{pos2}} in ${{teamName}}`);
                        }}
                    }});
                }});
            }});
            
            // Plotly Sunburst 차트 생성
            console.log('Creating Plotly Sunburst with', labels.length, 'nodes');
            console.log('First 5 labels:', labels.slice(0, 5));
            console.log('First 5 parents:', parents.slice(0, 5));
            console.log('First 5 values:', values.slice(0, 5));
            
            // 데이터가 없으면 메시지 표시
            if (labels.length === 0) {{
                console.error('No data for Sunburst chart - labels array is empty');
                container.innerHTML = '<p style="text-align: center; padding: 50px; color: #666;">팀 멤버 데이터가 없습니다.</p>';
                return;
            }}
            
            // 데이터가 너무 적으면 경고
            if (labels.length === 1) {{
                console.warn('Only root node in Sunburst chart - check data structure');
                container.innerHTML = '<p style="text-align: center; padding: 50px; color: #666;">데이터 구조에 문제가 있습니다.</p>';
                return;
            }}
            
            const data = [{{
                type: 'sunburst',
                labels: labels,
                parents: parents,
                values: values,
                marker: {{ colors: colors }},
                textinfo: 'label+value',
                hovertemplate: '%{{label}}<br>인원: %{{value}}명<br>클릭하여 세부 정보 보기<extra></extra>',
                branchvalues: 'total',
                maxdepth: 2  // 초기에 2단계만 표시, 클릭하면 하위 레벨 표시
            }}];
            
            const layout = {{
                title: {{
                    text: teamName + ' 팀 5단계 계층 구조<br><sub>Team → Role → Position1 → Position2 → Position3</sub>',
                    font: {{ size: 14 }}
                }},
                margin: {{ l: 0, r: 0, b: 0, t: 50 }},
                sunburstcolorway: colors,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                annotations: [{{
                    text: `<b>총 인원: ${{currentTotal}}명</b><br>(${{prevMonth}}월: ${{prevTotal}}명)`,
                    showarrow: false,
                    x: 0.5,
                    y: -0.1,
                    xref: 'paper',
                    yref: 'paper',
                    font: {{ size: 12 }}
                }}]
            }};
            
            const config = {{
                responsive: true,
                displayModeBar: false
            }};
            
            // Plotly 차트 렌더링 및 이벤트 처리
            try {{
                // Plotly가 로드되었는지 확인
                if (typeof Plotly === 'undefined') {{
                    console.error('Plotly library not loaded');
                    container.innerHTML = '<p style="text-align: center; padding: 20px;">Sunburst 차트를 로드할 수 없습니다.</p>';
                    return;
                }}
                
                // 이미 차트가 있으면 제거
                Plotly.purge(container.id);
                
                // 새 차트 생성
                Plotly.newPlot(container.id, data, layout, config).then(function(gd) {{
                    console.log('Sunburst chart created successfully for', teamName);
                    
                    // 클릭 이벤트 처리 - 클릭하면 하위 레벨 표시/숨기기
                    // Plotly 이벤트는 생성된 그래프 객체에서 처리
                    gd.on('plotly_click', function(eventData) {{
                        if (eventData && eventData.points && eventData.points.length > 0) {{
                            const point = eventData.points[0];
                            console.log('Clicked on:', point.label, 'Level:', point.level);
                            
                            // 현재 maxdepth 가져오기
                            const currentMaxDepth = gd.data[0].maxdepth || 2;
                            
                            // 클릭한 레벨에 따라 maxdepth 조정
                            let newMaxDepth;
                            if (point.level === undefined || point.level === 0) {{
                                // 루트 클릭 - 모든 레벨 표시
                                newMaxDepth = null;
                            }} else if (currentMaxDepth && currentMaxDepth <= point.level + 1) {{
                                // 하위 레벨 표시
                                newMaxDepth = point.level + 3;
                            }} else {{
                                // 현재 레벨로 축소
                                newMaxDepth = point.level + 1;
                            }}
                            
                            // 차트 업데이트
                            Plotly.restyle(container.id, {{
                                maxdepth: newMaxDepth
                            }});
                        }}
                    }});
                }}).catch(function(err) {{
                    console.error('Plotly.newPlot error:', err);
                    container.innerHTML = '<p style="text-align: center; padding: 20px; color: red;">차트 생성 실패: ' + err.message + '</p>';
                }});
                console.log('Sunburst chart rendering completed');
            }} catch (error) {{
                console.error('Error creating Sunburst chart:', error);
                container.innerHTML = '<p style="text-align: center; padding: 20px; color: red;">차트 생성 중 오류 발생</p>';
            }}
        }}
        
        
        // 텍스트 축약 함수
        function abbreviateText(text) {{
            const abbreviations = {{
                'INSPECTOR': 'INSP',
                'TOP-MANAGEMENT': 'TOP-MGT',
                'MID-MANAGEMENT': 'MID-MGT',
                'SUPPORT': 'SUPP',
                'PACKING': 'PACK',
                'AUDITOR': 'AUD',
                'REPORT': 'RPT',
                'ASSEMBLY INSPECTOR': 'ASM INSP',
                'BOTTOM INSPECTOR': 'BTM INSP',
                'STITCHING INSPECTOR': 'STH INSP',
                'OSC INSPECTOR': 'OSC INSP',
                'GROUP LEADER': 'GRP LDR',
                'LINE LEADER': 'LINE LDR'
            }};
            
            return abbreviations[text] || (text.length > 10 ? text.substring(0, 8) + '..' : text);
        }}
        
        // 팀원 상세 정보 테이뺔 생성
        function createTeamMemberDetailTable(teamName, members) {{
            const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
            const tbody = document.getElementById(`team-member-tbody-${{cleanName}}`);
            
            if (!tbody) {{
                console.error('Team member detail table tbody not found for', teamName);
                return;
            }}
            
            tbody.innerHTML = '';
            
            // 현재 날짜
            const currentDate = new Date();
            const currentYear = {self.year};
            const currentMonth = {self.month};
            
            console.log('Creating team member detail table for', teamName, 'with', members.length, 'members');
            
            // 팀원 데이터 처리
            members.forEach((member, index) => {{
                const row = tbody.insertRow();
                
                // 입사일 처리
                const entranceDate = member.entrance_date || '-';
                
                // 근속년수 계산
                let yearsOfService = '-';
                if (entranceDate && entranceDate !== '-' && entranceDate !== '') {{
                    const entDate = new Date(entranceDate);
                    if (!isNaN(entDate) && entDate <= currentDate) {{
                        const years = Math.floor((currentDate - entDate) / (365.25 * 24 * 60 * 60 * 1000));
                        if (years >= 0) {{
                            yearsOfService = years + '년';
                        }} else {{
                            yearsOfService = '0년';  // 음수이면 0년으로 처리
                        }}
                    }}
                }}
                
                // 출근/결근 데이터 계산 - 실제 데이터 사용
                // member.total_days와 member.actual_days가 있으면 사용, 없으면 기본값
                let totalWorkDays = member.total_days || 13;  // 8월 기준 약 13일 (주말 제외)
                let actualWorkDays = member.actual_days || 0;
                
                // 비정상적으로 큰 값 처리 (월 최대 근무일 22일 초과 방지)
                if (totalWorkDays > 22) {{
                    console.warn(`Abnormal total_days for ${{member.name}}: ${{totalWorkDays}}, adjusting to 22`);
                    totalWorkDays = 22;
                }}
                if (actualWorkDays > totalWorkDays) {{
                    actualWorkDays = totalWorkDays;
                }}
                
                const absentDays = totalWorkDays - actualWorkDays;
                const absenceRate = totalWorkDays > 0 ? ((absentDays / totalWorkDays) * 100).toFixed(1) : '0.0';
                
                // 테이블 행 생성
                row.innerHTML = `
                    <td style="padding: 8px; border: 1px solid #ddd; white-space: normal; word-break: break-word;">
                        ${{member.role_category || '-'}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; white-space: normal; word-break: break-word;">
                        ${{member.position_1st || member.position || '-'}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; white-space: normal; word-break: break-word;">
                        ${{member.position_2nd || '-'}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; white-space: normal; word-break: break-word;">
                        ${{member.name || '이름 없음'}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        ${{member.employee_no || member.id || 'ID 없음'}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        ${{entranceDate}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        ${{yearsOfService}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        ${{actualWorkDays}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        ${{absentDays}}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        <span style="color: ${{absenceRate > 10 ? '#f44336' : '#4CAF50'}};">
                            ${{absenceRate}}%
                        </span>
                    </td>
                `;
            }});
            
            // Total 요약 행 추가
            if (members.length > 0) {{
                const totalRow = tbody.insertRow();
                totalRow.style.backgroundColor = '#f0f0f0';
                totalRow.style.fontWeight = 'bold';
                
                // 통계 계산
                let totalWorkingDays = 0;
                let totalAbsentDays = 0;
                let fullAttendanceCount = 0;
                
                members.forEach(member => {{
                    const workDays = member.actual_days || 0;
                    const totalDays = member.total_days || 13;
                    totalWorkingDays += workDays;
                    totalAbsentDays += (totalDays - workDays);
                    if (member.is_full_attendance === 'Y') {{
                        fullAttendanceCount++;
                    }}
                }});
                
                const avgWorkingDays = (totalWorkingDays / members.length).toFixed(1);
                const avgAbsentDays = (totalAbsentDays / members.length).toFixed(1);
                const avgAbsenceRate = ((totalAbsentDays / (members.length * 13)) * 100).toFixed(1);
                const fullAttendanceRate = ((fullAttendanceCount / members.length) * 100).toFixed(1);
                
                totalRow.innerHTML = `
                    <td colspan="3" style="padding: 10px; border: 2px solid #333; text-align: center;">
                        <strong>TOTAL / 평균</strong>
                    </td>
                    <td style="padding: 10px; border: 2px solid #333; text-align: center;">
                        <strong>총 ${{members.length}}명</strong>
                    </td>
                    <td colspan="3" style="padding: 10px; border: 2px solid #333; text-align: center;">
                        <strong>전체 출석률: ${{fullAttendanceRate}}%</strong>
                    </td>
                    <td style="padding: 10px; border: 2px solid #333; text-align: center;">
                        <strong>평균: ${{avgWorkingDays}}일</strong>
                    </td>
                    <td style="padding: 10px; border: 2px solid #333; text-align: center;">
                        <strong>평균: ${{avgAbsentDays}}일</strong>
                    </td>
                    <td style="padding: 10px; border: 2px solid #333; text-align: center;">
                        <strong style="color: ${{avgAbsenceRate > 10 ? '#f44336' : '#4CAF50'}};">
                            ${{avgAbsenceRate}}%
                        </strong>
                    </td>
                `;
            }}
        }}
        
        // 테이블 정렬 함수
        function sortTeamTable(header, columnIndex, teamCleanName) {{
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // 현재 정렬 상태 확인
            const currentIcon = header.querySelector('span');
            const isAscending = currentIcon.innerHTML.includes('▼');
            
            // 모든 헤더 아이콘 초기화
            table.querySelectorAll('th span').forEach(span => {{
                span.innerHTML = '▼';
                span.style.color = '#666';
            }});
            
            // 클릭한 헤더 아이콘 업데이트
            currentIcon.innerHTML = isAscending ? '▲' : '▼';
            currentIcon.style.color = '#007bff';
            
            // 정렬 함수
            rows.sort((a, b) => {{
                const aCell = a.cells[columnIndex];
                const bCell = b.cells[columnIndex];
                
                if (!aCell || !bCell) return 0;
                
                const aText = aCell.textContent.trim();
                const bText = bCell.textContent.trim();
                
                let compareResult = 0;
                
                // Employee No (column 4) - 숫자로 정렬
                if (columnIndex === 4) {{
                    const aNum = parseInt(aText.replace(/\\D/g, '')) || 0;
                    const bNum = parseInt(bText.replace(/\\D/g, '')) || 0;
                    compareResult = aNum - bNum;
                }}
                // Entrance Date (column 5) - 날짜로 정렬
                else if (columnIndex === 5) {{
                    const aDate = new Date(aText);
                    const bDate = new Date(bText);
                    compareResult = aDate - bDate;
                }}
                // Years of Service (column 6) - 년/월 파싱
                else if (columnIndex === 6) {{
                    const parseServiceTime = (text) => {{
                        const yearMatch = text.match(/(\\d+)년/);
                        const monthMatch = text.match(/(\\d+)개월/);
                        const years = yearMatch ? parseInt(yearMatch[1]) : 0;
                        const months = monthMatch ? parseInt(monthMatch[1]) : 0;
                        return years * 12 + months;
                    }};
                    const aMonths = parseServiceTime(aText);
                    const bMonths = parseServiceTime(bText);
                    compareResult = aMonths - bMonths;
                }}
                // Working Days, Absent Days (columns 7, 8) - 숫자로 정렬
                else if (columnIndex === 7 || columnIndex === 8) {{
                    const aNum = parseInt(aText) || 0;
                    const bNum = parseInt(bText) || 0;
                    compareResult = aNum - bNum;
                }}
                // Absence Rate (column 9) - 퍼센트로 정렬
                else if (columnIndex === 9) {{
                    const aNum = parseFloat(aText.replace('%', '')) || 0;
                    const bNum = parseFloat(bText.replace('%', '')) || 0;
                    compareResult = aNum - bNum;
                }}
                // 텍스트 정렬 (Role Category, Position 1st, Position 2nd, Full Name)
                else {{
                    compareResult = aText.localeCompare(bText, 'ko-KR');
                }}
                
                // 오름차순/내림차순 적용
                return isAscending ? compareResult : -compareResult;
            }});
            
            // 테이블 재구성
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
            
            // 정렬 상태 저장 (선택적)
            if (window.teamTableSortState) {{
                window.teamTableSortState[teamCleanName] = {{
                    column: columnIndex,
                    ascending: !isAscending
                }};
            }}
        }}
        
        // 역할별 비교 테이블 생성
        function createRoleComparisonTable(teamName, roleGroups) {{
            const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
            const tbody = document.getElementById(`role-comparison-tbody-${{cleanName}}`);
            
            if (!tbody) return;
            
            Object.entries(roleGroups).forEach(([role, members]) => {{
                const row = document.createElement('tr');
                const julyCount = Math.round(members.length * (0.8 + Math.random() * 0.4)); // 임시 7월 데이터
                const change = members.length - julyCount;
                const changePercent = julyCount > 0 ? (change / julyCount * 100) : 0;
                const changeColor = change > 0 ? '#00C851' : change < 0 ? '#CC0000' : '#757575';
                
                row.innerHTML = `
                    <td style="padding: 8px;">${{role}}</td>
                    <td style="padding: 8px; text-align: center;">${{members.length}}명</td>
                    <td style="padding: 8px; text-align: center;">${{julyCount}}명</td>
                    <td style="padding: 8px; text-align: center; color: ${{changeColor}};">${{change > 0 ? '+' : ''}}${{change}}명</td>
                    <td style="padding: 8px; text-align: center; color: ${{changeColor}};">${{change > 0 ? '+' : ''}}${{changePercent.toFixed(1)}}%</td>
                `;
                tbody.appendChild(row);
            }});
        }}
        
        // 팀원 테이블 페이지네이션 초기화
        function initializeTeamMembersTable(teamName, members) {{
            const cleanName = teamName.replace(/[^a-zA-Z0-9]/g, '_');
            const tbody = document.getElementById(`team-members-tbody-${{cleanName}}`);
            const pagination = document.getElementById(`pagination-${{cleanName}}`);
            
            if (!tbody || !pagination) return;
            
            const itemsPerPage = 10;
            let currentPage = 1;
            const totalPages = Math.ceil(members.length / itemsPerPage);
            
            function renderPage(page) {{
                tbody.innerHTML = '';
                const start = (page - 1) * itemsPerPage;
                const end = start + itemsPerPage;
                const pageMembers = members.slice(start, end);
                
                pageMembers.forEach(member => {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td style="padding: 8px; border-bottom: 1px solid #e9ecef;">${{member.position || '-'}}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e9ecef;">${{member.name || '-'}}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e9ecef;">${{member.id || '-'}}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e9ecef;">${{member.join_date || '-'}}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e9ecef;">${{member.position || '-'}}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e9ecef;">${{member.position2 || '-'}}</td>
                    `;
                    tbody.appendChild(row);
                }});
                
                // Update pagination buttons
                pagination.innerHTML = '';
                
                // Previous button
                if (page > 1) {{
                    const prevBtn = document.createElement('button');
                    prevBtn.textContent = '이전';
                    prevBtn.style.cssText = 'margin: 0 5px; padding: 5px 10px; cursor: pointer;';
                    prevBtn.onclick = () => {{
                        currentPage--;
                        renderPage(currentPage);
                    }};
                    pagination.appendChild(prevBtn);
                }}
                
                // Page numbers
                for (let i = 1; i <= totalPages; i++) {{
                    if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {{
                        const pageBtn = document.createElement('button');
                        pageBtn.textContent = i;
                        pageBtn.style.cssText = `margin: 0 5px; padding: 5px 10px; cursor: pointer; ${{i === page ? 'background: #007bff; color: white;' : ''}}`;
                        pageBtn.onclick = () => {{
                            currentPage = i;
                            renderPage(currentPage);
                        }};
                        pagination.appendChild(pageBtn);
                    }} else if (i === page - 3 || i === page + 3) {{
                        const dots = document.createElement('span');
                        dots.textContent = '...';
                        dots.style.cssText = 'margin: 0 5px;';
                        pagination.appendChild(dots);
                    }}
                }}
                
                // Next button
                if (page < totalPages) {{
                    const nextBtn = document.createElement('button');
                    nextBtn.textContent = '다음';
                    nextBtn.style.cssText = 'margin: 0 5px; padding: 5px 10px; cursor: pointer;';
                    nextBtn.onclick = () => {{
                        currentPage++;
                        renderPage(currentPage);
                    }};
                    pagination.appendChild(nextBtn);
                }}
            }}
            
            renderPage(1);
        }}
        
        // 팀 멤버 상세 정보 표시 함수
        function showTeamMembersDetail(teamName) {{
            const members = teamMembers[teamName] || [];
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.style.zIndex = '2000';
            
            const content = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 class="modal-title">${{teamName}} 팀 멤버 상세 정보</h2>
                        <span class="close-modal" onclick="this.closest('.modal').remove()">&times;</span>
                    </div>
                    <div class="modal-body">
                        <table style="width: 100%;">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>이름</th>
                                    <th>Position 1</th>
                                    <th>Position 2</th>
                                    <th>TYPE</th>
                                    <th>입사일</th>
                                    <th>만근여부</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{members.map(m => `
                                    <tr>
                                        <td>${{m.id}}</td>
                                        <td>${{m.name}}</td>
                                        <td>${{m.position}}</td>
                                        <td>${{m.position2 || '-'}}</td>
                                        <td>${{m.type}}</td>
                                        <td>${{m.entrance_date}}</td>
                                        <td class="${{m.full_attendance === 'Y' ? 'percentage-high' : 'percentage-low'}}">
                                            ${{m.full_attendance === 'Y' ? '✓' : '✗'}}
                                        </td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            modal.innerHTML = content;
            document.body.appendChild(modal);
            
            modal.onclick = function(e) {{
                if (e.target === modal) {{
                    modal.remove();
                }}
            }};
        }}
        
        // 결근자 상세 분석
        function createAbsenceContent(modalBody, modalId) {{
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.innerHTML = '<canvas id="absence-chart-' + modalId + '"></canvas>';
            modalBody.appendChild(chartDiv);
            
            new Chart(document.getElementById('absence-chart-' + modalId), {{
                type: 'line',
                data: {{
                    labels: ['7월', '8월'],
                    datasets: [{{
                        label: '결근율 (%)',
                        data: [monthlyDataJuly.absence_rate || 0, monthlyDataAugust.absence_rate || 0],
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        borderWidth: 3
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {{
                        duration: 1500,
                        easing: 'easeInOutQuart'
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '월별 결근율 추이'
                        }}
                    }}
                }}
            }});
            
            // 팀별 결근율 테이블
            const tableDiv = document.createElement('div');
            tableDiv.style.marginTop = '30px';
            tableDiv.innerHTML = `
                <h4>팀별 결근 현황</h4>
                <table>
                    <thead>
                        <tr>
                            <th>팀명</th>
                            <th>전체 인원</th>
                            <th>결근자</th>
                            <th>결근율</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{Object.entries(teamStats).map(([name, data]) => {{
                            const absenceRate = (100 - (data.attendance_rate || 0)).toFixed(1);
                            const absenceCount = Math.round(data.total * absenceRate / 100);
                            return `
                                <tr>
                                    <td>${{name}}</td>
                                    <td>${{data.total}}명</td>
                                    <td>${{absenceCount}}명</td>
                                    <td class="${{absenceRate > 10 ? 'percentage-low' : absenceRate > 5 ? 'percentage-medium' : 'percentage-high'}}">${{absenceRate}}%</td>
                                </tr>
                            `;
                        }}).join('')}}
                    </tbody>
                </table>
            `;
            modalBody.appendChild(tableDiv);
        }}
        
        function createDefaultContent(modalBody, modalId) {{
            modalBody.innerHTML = '<p>상세 콘텐츠가 준비 중입니다.</p>';
        }}
        
        // 팀 멤버 상세 모달 표시
        function showTeamMembersModal(teamName) {{
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.style.zIndex = '2001';
            
            const members = teamMembersData[teamName] || [];
            
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close-modal" onclick="this.closest('.modal').remove()">&times;</span>
                    <h3>${{teamName}} 팀 멤버 상세</h3>
                    <div class="modal-body">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>이름</th>
                                    <th>Position 1</th>
                                    <th>Position 2</th>
                                    <th>TYPE</th>
                                    <th>입사일</th>
                                    <th>출근 상태</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{members.map(member => `
                                    <tr>
                                        <td>${{member.id}}</td>
                                        <td>${{member.name}}</td>
                                        <td>${{member.position1}}</td>
                                        <td>${{member.position2 || '-'}}</td>
                                        <td>${{member.type}}</td>
                                        <td>${{member.entrance_date}}</td>
                                        <td>${{member.attendance_status}}</td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        }}
        
        // 팀 멤버 상세 표시 (팀별 만근 현황에서 호출)
        function showTeamMembersDetail(teamName) {{
            showTeamMembersModal(teamName);
        }}
        
        // 결근자 분석 모달 표시
        function showAbsenceAnalysisModal() {{
            openModal('modal-absence');
        }}
        
        // 퇴사자 분석 모달 표시  
        function showResignationAnalysisModal() {{
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.style.zIndex = '2000';
            
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close-modal" onclick="this.closest('.modal').remove()">&times;</span>
                    <h3>퇴사자 현황 분석</h3>
                    <div class="modal-body">
                        <div class="chart-container">
                            <canvas id="resignation-chart"></canvas>
                        </div>
                        <div style="margin-top: 30px;">
                            <h4>팀별 퇴사 현황</h4>
                            <table>
                                <thead>
                                    <tr>
                                        <th>팀명</th>
                                        <th>7월 퇴사자</th>
                                        <th>8월 퇴사자</th>
                                        <th>변화</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{Object.entries(teamStats).map(([name, data]) => `
                                        <tr>
                                            <td>${{name}}</td>
                                            <td>${{data.july_resignation || 0}}</td>
                                            <td>${{data.august_resignation || 0}}</td>
                                            <td>${{(data.august_resignation || 0) - (data.july_resignation || 0)}}</td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // 차트 생성
            new Chart(document.getElementById('resignation-chart'), {{
                type: 'bar',
                data: {{
                    labels: ['7월', '8월'],
                    datasets: [{{
                        label: '퇴사자 수',
                        data: [
                            Object.values(teamStats).reduce((sum, team) => sum + (team.july_resignation || 0), 0),
                            Object.values(teamStats).reduce((sum, team) => sum + (team.august_resignation || 0), 0)
                        ],
                        backgroundColor: ['rgba(255, 99, 132, 0.6)', 'rgba(255, 99, 132, 0.8)']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false
                }}
            }});
        }}
        
        // 테이블 정렬 함수 추가
        function sortTable(columnIndex, tableId) {{
            const table = document.getElementById(tableId);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.getElementsByTagName('tr'));
            const isAscending = table.dataset.sortOrder === 'asc';
            
            rows.sort((a, b) => {{
                const aValue = a.cells[columnIndex].textContent.trim();
                const bValue = b.cells[columnIndex].textContent.trim();
                
                // 숫자 처리
                const aNum = parseFloat(aValue.replace(/[명%]/g, ''));
                const bNum = parseFloat(bValue.replace(/[명%]/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return isAscending ? aNum - bNum : bNum - aNum;
                }}
                
                // 문자열 처리
                return isAscending ? 
                    aValue.localeCompare(bValue, 'ko') : 
                    bValue.localeCompare(aValue, 'ko');
            }});
            
            // 행 재배치
            rows.forEach((row, index) => {{
                tbody.appendChild(row);
                // 순위 업데이트
                if (row.cells[0].className === 'rank') {{
                    row.cells[0].textContent = index + 1;
                }}
            }});
            
            // 정렬 방향 토글
            table.dataset.sortOrder = isAscending ? 'desc' : 'asc';
            
            // 헤더 화살표 업데이트
            const headers = table.querySelectorAll('th');
            headers.forEach((header, i) => {{
                if (header.onclick) {{
                    const text = header.textContent.replace(' ▲', '').replace(' ▼', '');
                    if (i === columnIndex) {{
                        header.textContent = text + (isAscending ? ' ▲' : ' ▼');
                    }} else {{
                        header.textContent = text + ' ▼';
                    }}
                }}
            }});
        }}
        
        // 팀별 만근 테이블 정렬 함수
        function sortFullAttendanceTable(columnIndex) {{
            sortTable(columnIndex, 'fullAttendanceTable');
        }}
        
        // 모달 외부 클릭시 닫기
        window.onclick = function(event) {{
            if (event.target.className === 'modal') {{
                event.target.style.display = 'none';
            }}
        }}
        '''
        
    def prepare_monthly_trend_data(self):
        """월별 트렌드 데이터 준비"""
        monthly_trend = {}
        for month_key in self.metadata.get('monthly_data', {}):
            monthly_trend[month_key] = self.metadata['monthly_data'][month_key]
        return monthly_trend


def main():
    parser = argparse.ArgumentParser(description='Enhanced HR Management Dashboard Generator')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--year', type=int, required=True, help='Year')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Enhanced HR Management Dashboard Generator v6.0")
    print("REAL DATA ONLY - NO FAKE DATA")
    print("=" * 60)
    
    dashboard = EnhancedHRDashboard(args.month, args.year)
    dashboard.load_data()
    dashboard.save_metadata()
    output_file = dashboard.generate_dashboard_html()
    
    print("\n" + "=" * 60)
    print("✅ Enhanced Dashboard generation complete!")
    print(f"📁 Output file: {output_file}")
    print("🚫 No fake data was generated")
    print("=" * 60)


if __name__ == "__main__":
    main()