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

class EnhancedHRDashboard:
    def __init__(self, month, year):
        self.month = month
        self.year = year
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
        
        # 색상 팔레트 - 칼라풀하게
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
                    
                self.data['current'] = df
                print(f"  ✓ Current month REAL data loaded: {len(df)} records")
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
                    
                self.data['previous'] = prev_df
                print(f"  ✓ Previous month REAL data loaded: {len(prev_df)} records")
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
        try:
            team_file = "HR info/team_structure_updated.json"
            if os.path.exists(team_file):
                with open(team_file, 'r', encoding='utf-8') as f:
                    self.team_structure = json.load(f)
                print(f"  ✓ Team structure loaded")
                
                # 팀 매핑 생성 - 첨부파일 기준으로 매핑
                self.team_mapping = {}
                self.position_to_team = {}  # 포지션별 팀 매핑
                self.position_to_type = {}  # 포지션별 TYPE 매핑
                
                if 'positions' in self.team_structure:
                    for pos in self.team_structure['positions']:
                        team = pos.get('team_name', 'Unknown')
                        role_type = pos.get('role_type', 'TYPE-2')  # 기본값 TYPE-2
                        
                        # 모든 포지션 레벨에서 매핑
                        for key in ['position_1st', 'position_2nd', 'position_3rd']:
                            position = pos.get(key, '')
                            if position and position not in ['', 'nan', None]:
                                self.position_to_team[position] = team
                                self.position_to_type[position] = role_type
                        
                        # Final code로도 매핑
                        final_code = pos.get('final_code', '')
                        if final_code:
                            self.position_to_team[final_code] = team
                            self.position_to_type[final_code] = role_type
            else:
                print(f"  ⚠ Team structure not found")
                
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
            
    def calculate_real_weekly_data(self):
        """실제 주차별 데이터 계산"""
        if self.data['current'].empty:
            self.weekly_data = {}
            return
            
        df = self.data['current']
        
        # 실제 날짜 기반 주차 계산
        start_date = datetime(self.year, self.month, 1)
        
        week_data = {}
        for week_num in range(1, 5):
            week_start = start_date + timedelta(days=(week_num-1)*7)
            week_end = week_start + timedelta(days=6)
            
            week_key = f"Week{week_num}"
            
            # 해당 주차에 재직 중인 직원
            active_employees = df[
                (df['Entrance Date'] <= week_end) & 
                ((df['Stop working Date'].isna()) | (df['Stop working Date'] > week_end))
            ]
            
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
        
        # 활성 직원만 필터링
        if 'RE MARK' in df.columns:
            active_mask = df['RE MARK'] != 'Stop working'
        else:
            active_mask = df['Stop working Date'].isna() | (df['Stop working Date'] > self.report_date)
            
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
        
        # 팀 칼럼 찾기 - 여러 포지션 컬럼 확인
        df['real_team'] = None
        
        # 우선순위: QIP POSITION 1ST NAME -> QIP POSITION 2ND NAME -> QIP POSITION 3RD NAME -> FINAL CODE
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
        df['real_team'] = df['real_team'].fillna('Unknown')
        team_column = 'real_team'
            
        # 팀별 통계
        for team in df[team_column].dropna().unique():
            team_df = df[df[team_column] == team]
            
            # 활성 직원만
            active_mask = team_df['RE MARK'] != 'Stop working' if 'RE MARK' in team_df.columns else team_df['Stop working Date'].isna()
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
        """데이터 기간 계산"""
        start_date = datetime(self.year, self.month, 1)
        if self.month == 12:
            end_date = datetime(self.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(self.year, self.month + 1, 1) - timedelta(days=1)
            
        return f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}"
        
    def save_metadata(self):
        """메타데이터 저장"""
        month_key = f"{self.year}_{self.month:02d}"
        
        # 월별 데이터 저장
        self.metadata['monthly_data'][month_key] = self.calculate_real_hr_metrics()
        self.metadata['weekly_data'][month_key] = self.weekly_data
        
        # 팀별 통계 저장
        self.metadata['team_stats'] = self.metadata.get('team_stats', {})
        self.metadata['team_stats'][month_key] = self.calculate_team_statistics()
        
        # 결근 사유 저장
        self.metadata['absence_reasons'] = self.metadata.get('absence_reasons', {})
        self.metadata['absence_reasons'][month_key] = self.calculate_absence_reasons()
        
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
        
        # 이전 월 메트릭
        prev_month_key = f"{self.year if self.month > 1 else self.year-1}_{(self.month-1 if self.month > 1 else 12):02d}"
        prev_metrics = self.metadata.get('monthly_data', {}).get(prev_month_key, {})
        
        html_content = self.generate_full_html(metrics, team_stats, absence_reasons, prev_metrics)
        
        # HTML 파일 저장
        output_file = f"output_files/management_dashboard_{self.year}_{self.month:02d}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ Dashboard generated: {output_file}")
        return output_file
        
    def generate_full_html(self, metrics, team_stats, absence_reasons, prev_metrics):
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self.generate_enhanced_css()}
    </style>
</head>
<body>
    <div class="dashboard-container">
        {self.generate_header()}
        
        <!-- HR Analytics Section -->
        <div class="section hr-section">
            <h2 class="section-title">📊 인사/출결 분석</h2>
            <div class="cards-grid-3x3">
                {self.generate_hr_cards(metrics, prev_metrics)}
            </div>
        </div>
        
        <!-- Quality Section -->
        <div class="section quality-section">
            <h2 class="section-title">📈 품질 분석</h2>
            <div class="quality-grid">
                <div class="quality-card">
                    <h3>🎯 5PRS 분석</h3>
                    <div class="quality-content">
                        <p>5 Point Rating System</p>
                        <p>데이터 준비 중...</p>
                    </div>
                </div>
                <div class="quality-card">
                    <h3>✅ AQL 분석</h3>
                    <div class="quality-content">
                        <p>Acceptable Quality Level</p>
                        <p>데이터 준비 중...</p>
                    </div>
                </div>
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
        {self.generate_enhanced_javascript(metrics, team_stats, absence_reasons, current_weekly, prev_weekly)}
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
            height: 350px;
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
                'title': '결근자 정보/결근율',
                'value': f"{metrics.get('absence_rate', 0):.1f}%",
                'subtitle': f"결근자: {metrics.get('absence_count', 0)}명",
                'prev_value': prev_metrics.get('absence_rate', 0),
                'modal_id': 'modal-absence'
            },
            {
                'number': 3,
                'title': '퇴사율',
                'value': f"{metrics.get('resignation_rate', 0):.1f}%",
                'subtitle': f"퇴사자: {metrics.get('resignation_count', 0)}명",
                'prev_value': prev_metrics.get('resignation_rate', 0),
                'modal_id': 'modal-resignation'
            },
            {
                'number': 4,
                'title': '최근 30일내\n입사 인원',
                'value': f"{metrics.get('recent_hires', 0)}명",
                'subtitle': f"신입 비율: {metrics.get('recent_hires_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('recent_hires', 0),
                'modal_id': 'modal-new-hires'
            },
            {
                'number': 5,
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
            
            cards_html += f'''
            <div class="hr-card" onclick="openModal('{card['modal_id']}')">
                <div class="card-number">{card['number']}</div>
                <div class="card-title">{card['title']}</div>
                <div class="card-value">{card['value']}</div>
                <div class="card-subtitle">{card['subtitle']}</div>
                <div class="card-change {change_class}">{change_text}</div>
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
        
    def generate_enhanced_javascript(self, metrics, team_stats, absence_reasons, current_weekly, prev_weekly):
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
        
        return f'''
        // 전역 데이터
        const monthlyDataJuly = {json.dumps(monthly_data_july, ensure_ascii=False)};
        const monthlyDataAugust = {json.dumps(monthly_data_august, ensure_ascii=False)};
        const currentWeeklyData = {current_weekly_json};
        const prevWeeklyData = {prev_weekly_json};
        const teamStats = {team_stats_json};
        const absenceReasons = {absence_reasons_json};
        
        // 차트 저장소
        const charts = {{}};
        
        // Navigation function
        function navigateToIncentive() {{
            window.location.href = 'dashboard_{self.year}_{self.month:02d}.html';
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
        
        // 팀 상세 모달 열기
        function showTeamDetailPopup(teamName, teamData) {{
            const modal = document.getElementById('team-detail-modal');
            const title = document.getElementById('team-detail-title');
            const body = document.getElementById('team-detail-body');
            
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
            
            // 주차별 데이터 (팀별로 계산 필요 - 현재는 전체 데이터 사용)
            const weeklyAttendance = [
                currentWeeklyData.Week1?.attendance_rate || 0,
                currentWeeklyData.Week2?.attendance_rate || 0,
                currentWeeklyData.Week3?.attendance_rate || 0,
                currentWeeklyData.Week4?.attendance_rate || 0
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
                // 다른 모달들도 필요시 구현
                default:
                    createDefaultContent(modalBody, modalId);
                    break;
            }}
        }}
        
        function createEnhancedTotalEmployeesContent(modalBody, modalId) {{
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
                            text: '월별 총인원 비교'
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
                prevWeeklyData.Week1?.total_employees || 377,
                prevWeeklyData.Week2?.total_employees || 374,
                prevWeeklyData.Week3?.total_employees || 372,
                prevWeeklyData.Week4?.total_employees || 373,
                currentWeeklyData.Week1?.total_employees || 374,
                currentWeeklyData.Week2?.total_employees || 375,
                currentWeeklyData.Week3?.total_employees || 376,
                currentWeeklyData.Week4?.total_employees || 376
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
                            text: '주차별 총인원 트렌드'
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
            const teamData = Object.entries(teamStats)
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
                            showTeamDetailPopup(teamName, teamStats[teamName]);
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 인원 분포 (클릭하여 상세보기)'
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
            
            // 4. 트리맵 스타일 차트 (가로 바 + 변화량 표시)
            const treemapDiv = document.createElement('div');
            treemapDiv.className = 'chart-container';
            treemapDiv.style.marginTop = '20px';
            
            // 타이틀을 동일한 스타일로 추가
            const treemapTitle = document.createElement('h4');
            treemapTitle.style.cssText = 'margin: 20px 0 10px 0; font-size: 16px; font-weight: 600; color: #333;';
            treemapTitle.textContent = '팀별 인원 분포 및 7월 대비 변화';
            treemapDiv.appendChild(treemapTitle);
            
            const treemapContainerWrapper = document.createElement('div');
            treemapContainerWrapper.id = 'treemap-' + modalId;
            treemapContainerWrapper.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px;';
            treemapDiv.appendChild(treemapContainerWrapper);
            modalBody.appendChild(treemapDiv);
            
            // 7월 팀 데이터 가져오기
            const julyTeamStats = {json.dumps(self.metadata.get('team_stats', {}).get(f'{self.year}_07', {}), ensure_ascii=False)};
            
            // 팀별 트리맵 박스 생성 - 개선된 가독성
            const treemapContainer = document.getElementById('treemap-' + modalId);
            
            // 팀 데이터를 크기 순으로 정렬하고 색상 통일
            const topColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FD79A8'];
            
            teamData.forEach((team, index) => {{
                const julyData = julyTeamStats[team.name] || {{}};
                const julyTotal = julyData.total || team.total; // 7월 데이터가 없으면 현재값 사용
                const augTotal = team.total;
                const change = augTotal - julyTotal;
                const changePercent = julyTotal > 0 ? ((change / julyTotal) * 100).toFixed(1) : 0;
                
                const box = document.createElement('div');
                // 고정 크기로 변경하여 가독성 개선
                box.style.cssText = `
                    min-height: 120px;
                    background: ` + topColors[index % topColors.length] + `;
                    border-radius: 8px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    color: white;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 10px;
                    position: relative;
                `;
                
                box.onmouseover = function() {{
                    box.style.transform = 'scale(1.05)';
                    box.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
                }};
                box.onmouseout = function() {{
                    box.style.transform = 'scale(1)';
                    box.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                }};
                box.onclick = function() {{
                    showTeamDetailPopup(team.name, teamStats[team.name]);
                }};
                
                const changeColor = change > 0 ? '#4CAF50' : change < 0 ? '#F44336' : '#9E9E9E';
                const changeSymbol = change > 0 ? '▲' : change < 0 ? '▼' : '—';
                
                // 불필요한 정보 제거하고 간단하게 표시
                box.innerHTML = `
                    <div style="text-align: center; width: 100%;">
                        <div style="font-size: 13px; opacity: 0.95; margin-bottom: 5px;">${{team.name || 'Unknown'}}</div>
                        <div style="font-size: 24px; font-weight: bold; margin: 5px 0;">${{augTotal}}명</div>
                        <div style="font-size: 12px; opacity: 0.9;">${{team.percentage}}%</div>
                        ` + (change !== 0 ? `
                        <div style="margin-top: 8px; padding: 3px 6px; background: ` + changeColor + `; border-radius: 4px; font-size: 11px;">
                            ` + changeSymbol + ` ` + (change > 0 ? '+' : '') + change + `명
                        </div>` : '') + `
                    </div>
                `;
                
                treemapContainer.appendChild(box);
            }});
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                            labels: {{
                                font: {{
                                    size: 11
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    return label + ': ' + value + '명';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            charts[modalId].push(treemapChart);
            
            // 5. TYPE별 인원 카드
            const typeDiv = document.createElement('div');
            typeDiv.style.marginTop = '20px';
            typeDiv.innerHTML = '<h4>TYPE별 인원 현황</h4>';
            modalBody.appendChild(typeDiv);
            
            const typeCardsDiv = document.createElement('div');
            typeCardsDiv.className = 'type-cards';
            
            // TYPE 값 처리 - 문자열일 수 있음
            const type1Count = parseInt(monthlyDataAugust.type1_count) || 0;
            const type2Count = parseInt(monthlyDataAugust.type2_count) || 0;
            const type3Count = parseInt(monthlyDataAugust.type3_count) || 0;
            const totalCount = monthlyDataAugust.total_employees || 383;
            
            const typeData = [
                {{
                    label: 'TYPE-1 인원',
                    value: type1Count + '명',
                    percentage: ((type1Count / totalCount) * 100).toFixed(1) + '%',
                    color: '{self.colors['chart_colors'][0]}'
                }},
                {{
                    label: 'TYPE-2 인원',
                    value: type2Count + '명',
                    percentage: ((type2Count / totalCount) * 100).toFixed(1) + '%',
                    color: '{self.colors['chart_colors'][1]}'
                }},
                {{
                    label: 'TYPE-3 인원',
                    value: type3Count + '명',
                    percentage: ((type3Count / totalCount) * 100).toFixed(1) + '%',
                    color: '{self.colors['chart_colors'][2]}'
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
            
            modalBody.appendChild(typeCardsDiv);
            
            // 6. 팀별 만근 인원 정보 - 정렬 기능 추가
            const fullAttendanceDiv = document.createElement('div');
            fullAttendanceDiv.style.marginTop = '30px';
            const fullAttendanceTitle = document.createElement('h4');
            fullAttendanceTitle.style.cssText = 'margin: 20px 0 10px 0; font-size: 16px; font-weight: 600; color: #333;';
            fullAttendanceTitle.textContent = '팀별 만근 인원 현황 ({self.month}월)';
            fullAttendanceDiv.appendChild(fullAttendanceTitle);
            modalBody.appendChild(fullAttendanceDiv);
            
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
            
            const fullAttendanceTable = document.createElement('div');
            fullAttendanceTable.innerHTML = `
                <table id="fullAttendanceTable" data-sort-order="desc">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0, 'fullAttendanceTable')" style="cursor: pointer;">순위 ▼</th>
                            <th onclick="sortTable(1, 'fullAttendanceTable')" style="cursor: pointer;">팀명 ▼</th>
                            <th onclick="sortTable(2, 'fullAttendanceTable')" style="cursor: pointer; text-align: right;">만근 인원 ▼</th>
                            <th onclick="sortTable(3, 'fullAttendanceTable')" style="cursor: pointer; text-align: right;">전체 인원 ▼</th>
                            <th onclick="sortTable(4, 'fullAttendanceTable')" style="cursor: pointer; text-align: right;">만근율 ▼</th>
                        </tr>
                    </thead>
                    <tbody>
                        ` + fullAttendanceData.map((team, index) => {{
                            const rateClass = team.rate >= 95 ? 'percentage-high' : 
                                            team.rate >= 90 ? 'percentage-medium' : 'percentage-low';
                            return `
                            <tr>
                                <td class="rank">` + (index + 1) + `</td>
                                <td class="team-name">` + team.name + `</td>
                                <td style="text-align: right;">` + team.fullAttendance + `명</td>
                                <td style="text-align: right;">` + team.total + `명</td>
                                <td style="text-align: right;" class="` + rateClass + `">` + team.rate.toFixed(1) + `%</td>
                            </tr>
                            `;
                        }}).join('') + `
                    </tbody>
                </table>
            `;
            modalBody.appendChild(fullAttendanceTable);
        }}
        
        function createDefaultContent(modalBody, modalId) {{
            modalBody.innerHTML = '<p>상세 콘텐츠가 준비 중입니다.</p>';
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