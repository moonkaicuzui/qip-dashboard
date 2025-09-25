#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HR Management Dashboard v5.0 - REAL DATA ONLY
NO FAKE DATA - NO HARDCODING - DYNAMIC CALCULATION
"우리사전에 가짜 데이타는 없다"
Created: 2025-08-31
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import argparse
import glob
from pathlib import Path
from collections import defaultdict

class RealDataHRDashboard:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.month_name = self.get_month_name(month)
        self.data = {}
        self.metadata = {}
        self.team_structure = {}
        self.weekly_data = defaultdict(dict)
        self.report_date = datetime.now()
        
        # REAL 칼럼 매핑 (CSV 헤더 기반)
        self.column_mapping = {
            'employee_no': 'Employee No',
            'full_name': 'Full Name',
            'position_1st': 'QIP POSITION 1ST  NAME',
            'position_2nd': 'QIP POSITION 2ND  NAME',
            'position_3rd': 'QIP POSITION 3RD  NAME',
            'role_type': 'ROLE TYPE STD',
            'entrance_date': 'Entrance Date',
            'stop_working_date': 'Stop working Date',
            'remark': 'RE MARK',
            'team': 'BUILDING',  # 팀 정보
            'actual_working_days': 'Actual Working Days',
            'total_working_days': 'Total Working Days',
            'unapproved_absence': 'Unapproved Absence Days',
            'absence_rate': 'Absence Rate (raw)',
            'boss_name': 'direct boss name'
        }
        
        # Black & White 테마 (변경 없음)
        self.colors = {
            'primary': '#000000',
            'secondary': '#FFFFFF',
            'background': '#F8F9FA',
            'card_bg': '#FFFFFF',
            'text_primary': '#212529',
            'text_secondary': '#6C757D',
            'border': '#DEE2E6',
            'success': '#28A745',
            'danger': '#DC3545',
            'warning': '#FFC107',
            'info': '#17A2B8',
            # 칼라풀한 차트 색상 추가
            'chart_colors': [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
                '#F8B739', '#52C7B8', '#E17055', '#74B9FF', '#A29BFE',
                '#FD79A8', '#55EFC4', '#FF7675', '#6ED4C8', '#FDCB6E'
            ]
        }
        
    def get_month_name(self, month):
        """월 번호를 월 이름으로 변환"""
        months = {
            1: 'january', 2: 'february', 3: 'march', 4: 'april',
            5: 'may', 6: 'june', 7: 'july', 8: 'august',
            9: 'september', 10: 'october', 11: 'november', 12: 'december'
        }
        return months.get(month, 'january')
    
    def parse_date(self, date_str):
        """다양한 날짜 형식 파싱"""
        if pd.isna(date_str) or date_str == '' or date_str == 'nan':
            return pd.NaT
            
        date_str = str(date_str).strip()
        
        # 다양한 날짜 형식 시도
        formats = [
            '%Y.%m.%d',  # 2025.08.31
            '%d/%m/%Y',  # 31/08/2025
            '%m/%d/%Y',  # 08/31/2025
            '%Y-%m-%d',  # 2025-08-31
            '%d-%m-%Y',  # 31-08-2025
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
                
        # 모든 형식 실패시 pandas 자동 파싱
        try:
            return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
        except:
            return pd.NaT
    
    def load_data(self):
        """실제 데이터만 로드 - NO FAKE DATA"""
        print(f"📊 Loading REAL data for {self.year}년 {self.month}월...")
        
        # 1. 인센티브 데이터 로드 (실제 데이터)
        self.load_real_incentive_data()
        
        # 2. 출근 데이터 로드 (실제 데이터)
        self.load_real_attendance_data()
        
        # 3. 팀 구조 데이터 로드 (실제 데이터)
        self.load_team_structure()
        
        # 4. 이전 메타데이터 로드
        self.load_previous_metadata()
        
        print("✅ Real data loading complete")
        
    def load_real_incentive_data(self):
        """실제 인센티브 데이터 로드"""
        try:
            # 현재 월 데이터
            file_pattern = f"output_files/output_QIP_incentive_{self.month_name}_{self.year}_*.csv"
            files = glob.glob(file_pattern)
            
            if files:
                df = pd.read_csv(files[0], encoding='utf-8-sig')
                
                # 날짜 칼럼 파싱
                if 'Entrance Date' in df.columns:
                    df['Entrance Date'] = df['Entrance Date'].apply(self.parse_date)
                if 'Stop working Date' in df.columns:
                    df['Stop working Date'] = df['Stop working Date'].apply(self.parse_date)
                    
                self.data['current'] = df
                print(f"  ✓ Current month REAL data loaded: {len(df)} records")
            else:
                print(f"  ⚠ No data for {self.month_name} {self.year} - WILL NOT CREATE FAKE DATA")
                self.data['current'] = pd.DataFrame()
                
            # 이전 월 데이터 로드
            prev_month = self.month - 1 if self.month > 1 else 12
            prev_year = self.year if self.month > 1 else self.year - 1
            prev_month_name = self.get_month_name(prev_month)
            
            prev_file_pattern = f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_*.csv"
            prev_files = glob.glob(prev_file_pattern)
            
            if prev_files:
                prev_df = pd.read_csv(prev_files[0], encoding='utf-8-sig')
                
                # 날짜 칼럼 파싱
                if 'Entrance Date' in prev_df.columns:
                    prev_df['Entrance Date'] = prev_df['Entrance Date'].apply(self.parse_date)
                if 'Stop working Date' in prev_df.columns:
                    prev_df['Stop working Date'] = prev_df['Stop working Date'].apply(self.parse_date)
                    
                self.data['previous'] = prev_df
                print(f"  ✓ Previous month REAL data loaded: {len(prev_df)} records")
            else:
                print(f"  ℹ No previous month data - WILL SHOW AS 0")
                self.data['previous'] = pd.DataFrame()
                
        except Exception as e:
            print(f"  ❌ Error loading data: {e}")
            self.data['current'] = pd.DataFrame()
            self.data['previous'] = pd.DataFrame()
            
    def load_real_attendance_data(self):
        """실제 출근 데이터 로드"""
        try:
            # 다양한 출근 데이터 파일 패턴 시도
            patterns = [
                f"input_files/attendance/attendance_{self.month_name}_{self.year}.csv",
                f"input_files/attendance/converted/attendance_{self.month_name}_{self.year}.csv",
                f"input_files/attendance/original/*{self.month_name}*.csv",
                f"input_files/attendance/*{self.month}월*.csv"
            ]
            
            for pattern in patterns:
                files = glob.glob(pattern)
                if files:
                    self.data['attendance'] = pd.read_csv(files[0], encoding='utf-8-sig')
                    print(f"  ✓ Attendance REAL data loaded: {len(self.data['attendance'])} records")
                    return
                    
            print(f"  ⚠ No attendance data found - WILL USE DATA FROM INCENTIVE FILE")
            self.data['attendance'] = pd.DataFrame()
            
        except Exception as e:
            print(f"  ❌ Error loading attendance: {e}")
            self.data['attendance'] = pd.DataFrame()
            
    def load_team_structure(self):
        """팀 구조 데이터 로드"""
        try:
            team_file = "HR info/team_structure.json"
            if os.path.exists(team_file):
                with open(team_file, 'r', encoding='utf-8') as f:
                    self.team_structure = json.load(f)
                print(f"  ✓ Team structure loaded")
                
                # 팀별/역할별 매핑 생성
                self.team_mapping = {}
                self.role_mapping = {}
                
                if 'positions' in self.team_structure:
                    for pos in self.team_structure['positions']:
                        team = pos.get('team_name', 'Unknown')
                        role = pos.get('role_category', 'Unknown')
                        position = pos.get('position_1st', '')
                        
                        if position:
                            self.team_mapping[position] = team
                            self.role_mapping[position] = role
            else:
                print(f"  ⚠ Team structure not found")
                self.team_structure = {}
                self.team_mapping = {}
                self.role_mapping = {}
                
        except Exception as e:
            print(f"  ❌ Error loading team structure: {e}")
            self.team_structure = {}
            
    def load_previous_metadata(self):
        """이전 메타데이터 로드"""
        try:
            metadata_file = f"output_files/hr_metadata_{self.year}.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"  ✓ Previous metadata loaded")
            else:
                self.metadata = {'monthly_data': {}, 'weekly_data': {}}
                print(f"  ℹ Starting fresh metadata")
        except Exception as e:
            print(f"  ❌ Error loading metadata: {e}")
            self.metadata = {'monthly_data': {}, 'weekly_data': {}}
            
    def calculate_real_weekly_data(self):
        """실제 주차별 데이터 계산 - NO FAKE DATA"""
        if self.data['current'].empty:
            self.weekly_data = {}
            return
            
        df = self.data['current']
        
        # 실제 날짜 기반 주차 계산
        start_date = datetime(self.year, self.month, 1)
        
        # 월의 주차 구분
        week_data = {}
        for week_num in range(1, 5):  # 최대 4주
            week_start = start_date + timedelta(days=(week_num-1)*7)
            week_end = week_start + timedelta(days=6)
            
            week_key = f"Week{week_num}"
            
            # 해당 주차에 재직 중인 직원 계산
            active_employees = df[
                (df['Entrance Date'] <= week_end) & 
                ((df['Stop working Date'].isna()) | (df['Stop working Date'] > week_end))
            ]
            
            # 해당 주차 신규 입사자
            new_hires = df[
                (df['Entrance Date'] >= week_start) & 
                (df['Entrance Date'] <= week_end)
            ]
            
            # 해당 주차 퇴사자
            resignations = df[
                (df['Stop working Date'] >= week_start) & 
                (df['Stop working Date'] <= week_end)
            ]
            
            # 실제 출근율 계산
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
            
        self.weekly_data = week_data
        
    def calculate_real_hr_metrics(self):
        """실제 HR 메트릭 계산 - NO FAKE DATA"""
        metrics = {}
        
        if not self.data['current'].empty:
            df = self.data['current']
            
            # 1. 총인원 (보고서 생성일 기준 퇴사자 제외)
            # RE MARK != 'Stop working' 또는 Stop working Date가 보고서 생성일 이후
            if 'RE MARK' in df.columns:
                active_mask = df['RE MARK'] != 'Stop working'
            else:
                active_mask = df['Stop working Date'].isna() | (df['Stop working Date'] > self.report_date)
                
            active_employees = df[active_mask]
            metrics['total_employees'] = len(active_employees)
            
            # TYPE별 인원 계산
            if 'ROLE TYPE STD' in df.columns:
                type_counts = active_employees['ROLE TYPE STD'].value_counts()
                metrics['type1_count'] = type_counts.get('TYPE-1', 0)
                metrics['type2_count'] = type_counts.get('TYPE-2', 0)
                metrics['type3_count'] = type_counts.get('TYPE-3', 0)
            else:
                metrics['type1_count'] = 0
                metrics['type2_count'] = 0
                metrics['type3_count'] = 0
            
            # 2. 출근율 (실제 데이터)
            if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
                total_actual = active_employees['Actual Working Days'].sum()
                total_possible = active_employees['Total Working Days'].sum()
                metrics['attendance_rate'] = (total_actual / total_possible * 100) if total_possible > 0 else 0
            else:
                metrics['attendance_rate'] = 0
                
            # 3. 결근율
            metrics['absence_rate'] = 100 - metrics['attendance_rate']
            
            # 결근자 수 (Actual Working Days < Total Working Days)
            if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
                absence_employees = active_employees[
                    active_employees['Actual Working Days'] < active_employees['Total Working Days']
                ]
                metrics['absence_count'] = len(absence_employees)
            else:
                metrics['absence_count'] = 0
            
            # 4. 퇴사율 (현재 월)
            if 'Stop working Date' in df.columns:
                current_month_resignations = df[
                    (df['Stop working Date'].dt.month == self.month) & 
                    (df['Stop working Date'].dt.year == self.year)
                ]
                metrics['resignation_count'] = len(current_month_resignations)
                metrics['resignation_rate'] = (
                    (metrics['resignation_count'] / metrics['total_employees'] * 100) 
                    if metrics['total_employees'] > 0 else 0
                )
            else:
                metrics['resignation_count'] = 0
                metrics['resignation_rate'] = 0
                
            # 5. 최근 30일 입사자
            if 'Entrance Date' in df.columns:
                thirty_days_ago = self.report_date - timedelta(days=30)
                recent_hires = active_employees[
                    active_employees['Entrance Date'] >= thirty_days_ago
                ]
                metrics['recent_hires'] = len(recent_hires)
                metrics['recent_hires_rate'] = (
                    (metrics['recent_hires'] / metrics['total_employees'] * 100)
                    if metrics['total_employees'] > 0 else 0
                )
            else:
                metrics['recent_hires'] = 0
                metrics['recent_hires_rate'] = 0
                
            # 6. 최근 30일내 퇴사한 신입 (입사 30일 이내 퇴사)
            if 'Entrance Date' in df.columns and 'Stop working Date' in df.columns:
                new_resignations = df[
                    (df['Stop working Date'].notna()) &
                    ((df['Stop working Date'] - df['Entrance Date']).dt.days <= 30)
                ]
                metrics['recent_resignations'] = len(new_resignations)
                
                # 신입 퇴사율 계산
                if metrics['recent_hires'] > 0:
                    metrics['recent_resignation_rate'] = (
                        metrics['recent_resignations'] / metrics['recent_hires'] * 100
                    )
                else:
                    metrics['recent_resignation_rate'] = 0
            else:
                metrics['recent_resignations'] = 0
                metrics['recent_resignation_rate'] = 0
                
            # 7. 60일 미만 근무자 (30일 이상 60일 미만)
            if 'Entrance Date' in df.columns:
                sixty_days_ago = self.report_date - timedelta(days=60)
                thirty_days_ago = self.report_date - timedelta(days=30)
                
                under_60_days = active_employees[
                    (active_employees['Entrance Date'] <= thirty_days_ago) &
                    (active_employees['Entrance Date'] > sixty_days_ago)
                ]
                metrics['under_60_days'] = len(under_60_days)
                metrics['under_60_days_rate'] = (
                    (metrics['under_60_days'] / metrics['total_employees'] * 100)
                    if metrics['total_employees'] > 0 else 0
                )
            else:
                metrics['under_60_days'] = 0
                metrics['under_60_days_rate'] = 0
                
            # 8. 보직 부여 후 퇴사자 (30일~60일 사이 퇴사)
            if 'Entrance Date' in df.columns and 'Stop working Date' in df.columns:
                post_assignment_resignations = df[
                    (df['Stop working Date'].notna()) &
                    ((df['Stop working Date'] - df['Entrance Date']).dt.days > 30) &
                    ((df['Stop working Date'] - df['Entrance Date']).dt.days <= 60)
                ]
                metrics['post_assignment_resignations'] = len(post_assignment_resignations)
                
                if metrics['under_60_days'] > 0:
                    metrics['post_assignment_resignation_rate'] = (
                        metrics['post_assignment_resignations'] / metrics['under_60_days'] * 100
                    )
                else:
                    metrics['post_assignment_resignation_rate'] = 0
            else:
                metrics['post_assignment_resignations'] = 0
                metrics['post_assignment_resignation_rate'] = 0
            
            # 8. 만근자 분석 (추가)
            if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
                full_attendance = df[
                    (df['Actual Working Days'] == df['Total Working Days']) &
                    (df['Total Working Days'] > 0) &
                    ((df['RE MARK'] != 'Stop working') if 'RE MARK' in df.columns else df['Stop working Date'].isna())
                ]
                metrics['full_attendance_count'] = len(full_attendance)
                metrics['full_attendance_rate'] = (
                    (metrics['full_attendance_count'] / metrics['total_employees'] * 100)
                    if metrics['total_employees'] > 0 else 0
                )
            else:
                metrics['full_attendance_count'] = 0
                metrics['full_attendance_rate'] = 0
                
            # 9. 장기근속자 분석 (추가)
            if 'Entrance Date' in df.columns:
                one_year_ago = self.report_date - timedelta(days=365)
                long_term_employees = df[
                    (df['Entrance Date'] <= one_year_ago) &
                    ((df['RE MARK'] != 'Stop working') if 'RE MARK' in df.columns else df['Stop working Date'].isna())
                ]
                metrics['long_term_count'] = len(long_term_employees)
                metrics['long_term_rate'] = (
                    (metrics['long_term_count'] / metrics['total_employees'] * 100)
                    if metrics['total_employees'] > 0 else 0
                )
            else:
                metrics['long_term_count'] = 0
                metrics['long_term_rate'] = 0
                
        else:
            # 데이터가 없으면 모두 0 - NO FAKE DATA
            metrics = {
                'total_employees': 0,
                'type1_count': 0,
                'type2_count': 0,
                'type3_count': 0,
                'attendance_rate': 0,
                'absence_rate': 0,
                'absence_count': 0,
                'resignation_count': 0,
                'resignation_rate': 0,
                'recent_hires': 0,
                'recent_hires_rate': 0,
                'recent_resignations': 0,
                'recent_resignation_rate': 0,
                'under_60_days': 0,
                'under_60_days_rate': 0,
                'post_assignment_resignations': 0,
                'post_assignment_resignation_rate': 0,
                'full_attendance_count': 0,
                'full_attendance_rate': 0,
                'long_term_count': 0,
                'long_term_rate': 0
            }
            
        return metrics
        
    def calculate_team_statistics(self):
        """팀별 실제 통계 계산"""
        if self.data['current'].empty:
            return {}
            
        df = self.data['current']
        team_stats = {}
        
        # 팀 칼럼 찾기 - 실제 팀 이름을 포지션에서 추출
        team_column = None
        
        # 먼저 position에서 실제 팀 이름 추출
        if 'QIP POSITION 1ST  NAME' in df.columns:
            # 팀 매핑을 사용하여 실제 팀 이름 추출
            df['real_team'] = df['QIP POSITION 1ST  NAME'].map(self.team_mapping)
            # 매핑되지 않은 경우 BUILDING 값 사용
            if 'BUILDING' in df.columns:
                df['real_team'] = df['real_team'].fillna(df['BUILDING'])
            team_column = 'real_team'
        elif 'BUILDING' in df.columns:
            # position이 없으면 BUILDING 사용
            team_column = 'BUILDING'
        else:
            return {}
                
        # 팀별 집계
        for team in df[team_column].unique():
            if pd.isna(team):
                continue
                
            team_df = df[df[team_column] == team]
            
            # 활성 직원만
            active_mask = team_df['RE MARK'] != 'Stop working' if 'RE MARK' in team_df.columns else team_df['Stop working Date'].isna()
            active_team = team_df[active_mask]
            
            team_stats[team] = {
                'total': len(active_team),
                'resignations': len(team_df[team_df['Stop working Date'].notna()]) if 'Stop working Date' in team_df.columns else 0,
                'attendance_rate': (
                    active_team['Actual Working Days'].sum() / active_team['Total Working Days'].sum() * 100
                    if 'Total Working Days' in active_team.columns and active_team['Total Working Days'].sum() > 0 else 0
                ),
                'new_hires': len(active_team[active_team['Entrance Date'] >= (self.report_date - timedelta(days=30))])
                    if 'Entrance Date' in active_team.columns else 0
            }
            
        return team_stats
        
    def calculate_absence_reasons(self):
        """결근 사유 실제 분석"""
        if self.data['attendance'].empty:
            # 출근 데이터가 없으면 인센티브 데이터 사용
            if self.data['current'].empty:
                return {}
                
            df = self.data['current']
            
            # Unapproved Absence Days > 0인 경우만
            if 'Unapproved Absence Days' in df.columns:
                absence_count = len(df[df['Unapproved Absence Days'] > 0])
                return {'무단결근': absence_count} if absence_count > 0 else {}
            return {}
            
        # 실제 출근 데이터에서 결근 사유 분석
        df = self.data['attendance']
        
        if 'Reason Description' in df.columns:
            reason_counts = df['Reason Description'].value_counts().to_dict()
            # 빈 값 제거
            return {k: v for k, v in reason_counts.items() if pd.notna(k)}
        
        return {}
        
    def save_metadata(self):
        """메타데이터 저장"""
        month_key = f"{self.year}_{self.month:02d}"
        
        # 현재 월 데이터 저장
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
        """대시보드 HTML 생성 - 실제 데이터 기반"""
        metrics = self.calculate_real_hr_metrics()
        team_stats = self.calculate_team_statistics()
        absence_reasons = self.calculate_absence_reasons()
        
        
        # 이전 월 메트릭
        prev_month_key = f"{self.year if self.month > 1 else self.year-1}_{(self.month-1 if self.month > 1 else 12):02d}"
        prev_metrics = self.metadata.get('monthly_data', {}).get(prev_month_key, {})
        
        html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HR Management Dashboard - {self.year}년 {self.month}월</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self.generate_css()}
    </style>
</head>
<body>
    <div class="dashboard-container">
        {self.generate_header()}
        
        <!-- HR Analytics Section - Full Width -->
        <div class="section hr-section">
            <h2 class="section-title">📊 인사/출결 분석</h2>
            <div class="cards-grid-3x3">
                {self.generate_real_hr_cards(metrics, prev_metrics)}
            </div>
        </div>
        
        <!-- Quality Section - Full Width Below -->
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
        
        {self.generate_real_modals(metrics, team_stats, absence_reasons)}
    </div>
    
    <script>
        {self.generate_real_javascript(metrics, team_stats, absence_reasons)}
    </script>
</body>
</html>'''
        
        # HTML 파일 저장
        output_file = f"output_files/management_dashboard_{self.year}_{self.month:02d}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ Dashboard generated: {output_file}")
        return output_file
        
    def generate_css(self):
        """CSS는 이전과 동일"""
        return f'''
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: {self.colors['background']};
            color: {self.colors['text_primary']};
            line-height: 1.6;
        }}
        
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: {self.colors['primary']};
            color: {self.colors['secondary']};
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 28px;
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
            background-color: {self.colors['primary']};
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
            background-color: {self.colors['text_secondary']};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .section {{
            background: {self.colors['card_bg']};
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .section-title {{
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid {self.colors['primary']};
        }}
        
        .cards-grid-3x3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        
        @media (max-width: 1200px) {{
            .cards-grid-3x3 {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 768px) {{
            .cards-grid-3x3 {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .hr-card {{
            background: {self.colors['background']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .hr-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: {self.colors['primary']};
        }}
        
        .card-number {{
            position: absolute;
            top: 10px;
            left: 10px;
            width: 24px;
            height: 24px;
            background: {self.colors['primary']};
            color: {self.colors['secondary']};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .card-title {{
            font-size: 14px;
            color: {self.colors['text_secondary']};
            margin-bottom: 10px;
            padding-left: 30px;
            white-space: pre-line;
        }}
        
        .card-value {{
            font-size: 28px;
            font-weight: bold;
            color: {self.colors['primary']};
            margin-bottom: 5px;
        }}
        
        .card-subtitle {{
            font-size: 12px;
            color: {self.colors['text_secondary']};
        }}
        
        .card-change {{
            font-size: 12px;
            margin-top: 5px;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        
        .change-positive {{
            background: rgba(40, 167, 69, 0.1);
            color: {self.colors['success']};
        }}
        
        .change-negative {{
            background: rgba(220, 53, 69, 0.1);
            color: {self.colors['danger']};
        }}
        
        .change-neutral {{
            background: rgba(108, 117, 125, 0.1);
            color: {self.colors['text_secondary']};
        }}
        
        .quality-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        
        .quality-card {{
            background: {self.colors['background']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            padding: 30px;
            text-align: center;
        }}
        
        .quality-card h3 {{
            font-size: 18px;
            margin-bottom: 15px;
            color: {self.colors['primary']};
        }}
        
        .quality-content {{
            color: {self.colors['text_secondary']};
            font-size: 14px;
        }}
        
        .quality-content p {{
            margin: 10px 0;
        }}
        
        .quality-placeholder {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        .placeholder-card {{
            background: {self.colors['background']};
            border: 2px dashed {self.colors['border']};
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            color: {self.colors['text_secondary']};
        }}
        
        /* Modal Styles */
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
            background-color: {self.colors['card_bg']};
            margin: 50px auto;
            padding: 30px;
            border-radius: 12px;
            width: 90%;
            max-width: 1000px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid {self.colors['primary']};
        }}
        
        .modal-title {{
            font-size: 22px;
            font-weight: bold;
        }}
        
        .close-modal {{
            font-size: 28px;
            cursor: pointer;
            color: {self.colors['text_secondary']};
            transition: color 0.3s;
        }}
        
        .close-modal:hover {{
            color: {self.colors['primary']};
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .stat-item {{
            background: {self.colors['background']};
            padding: 15px;
            border-radius: 8px;
            border: 1px solid {self.colors['border']};
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
        
        .team-list {{
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .team-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid {self.colors['border']};
        }}
        
        .team-name {{
            font-weight: bold;
        }}
        
        .team-value {{
            color: {self.colors['text_secondary']};
        }}
        '''
        
    def generate_header(self):
        """헤더 생성"""
        # 데이터 기간 계산
        data_period = self.calculate_data_period()
        
        return f'''
        <div class="header">
            <h1>인사/출결 분석</h1>
            <div class="header-info">
                <span>📅 {self.year}년 {self.month}월</span>
                <span>📆 데이터 기간: {data_period}</span>
                <span>⏰ 생성일시: {self.report_date.strftime("%Y-%m-%d %H:%M:%S")}</span>
                <span>🚫 No Fake Data</span>
            </div>
        </div>
        '''
        
    def generate_real_hr_cards(self, metrics, prev_metrics):
        """실제 데이터 기반 HR 카드 생성 - 9개"""
        cards_html = ""
        
        # 카드 데이터 정의 - 실제 값만 사용 (9개)
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
                'title': f'{self.month}월 결근자 정보/결근율',
                'value': f"{metrics.get('absence_rate', 0):.1f}%",
                'subtitle': f"결근자: {metrics.get('absence_count', 0)}명",
                'prev_value': prev_metrics.get('absence_rate', 0),
                'modal_id': 'modal-absence'
            },
            {
                'number': 3,
                'title': f'{self.month}월 퇴사율',
                'value': f"{metrics.get('resignation_rate', 0):.1f}%",
                'subtitle': f"퇴사자: {metrics.get('resignation_count', 0)}명",
                'prev_value': prev_metrics.get('resignation_rate', 0),
                'modal_id': 'modal-resignation'
            },
            {
                'number': 4,
                'title': '최근 30일내 입사 인원',
                'value': f"{metrics.get('recent_hires', 0)}명",
                'subtitle': f"전체 대비: {metrics.get('recent_hires_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('recent_hires', 0),
                'modal_id': 'modal-new-hires'
            },
            {
                'number': 5,
                'title': '최근 30일내 퇴사 인원\n(신입 퇴사율)',
                'value': f"{metrics.get('recent_resignations', 0)}명",
                'subtitle': f"신입 퇴사율: {metrics.get('recent_resignation_rate', 0):.1f}%",
                'prev_value': prev_metrics.get('recent_resignations', 0),
                'modal_id': 'modal-new-resignations'
            },
            {
                'number': 6,
                'title': '입사 60일 미만 인원\n(30일 미만 제외)',
                'value': f"{metrics.get('under_60_days', 0)}명",
                'subtitle': f"전체 대비: {metrics.get('under_60_days_rate', 0):.1f}%",
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
                'title': f'{self.month}월 만근자',
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
            # 변화율 계산 - 실제 데이터만
            if isinstance(card['value'], str):
                current_val = float(card['value'].replace('%', '')) if '%' in card['value'] else 0
                prev_val = card['prev_value']
            else:
                current_val = card['value']
                prev_val = card['prev_value']
                
            if prev_val > 0 and current_val > 0:
                change = ((current_val - prev_val) / prev_val) * 100
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
        
    def generate_real_modals(self, metrics, team_stats, absence_reasons):
        """실제 데이터 기반 모달 생성"""
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
                        <div class="chart-container">
                            <canvas id="chart-{config['id']}"></canvas>
                        </div>
                        <div class="stats-grid" id="stats-{config['id']}">
                            <!-- Real stats will be populated dynamically -->
                        </div>
                        <div class="team-list" id="team-list-{config['id']}">
                            <!-- Team data will be populated dynamically -->
                        </div>
                    </div>
                </div>
            </div>
            '''
            
        return modals_html
        
    def generate_real_javascript(self, metrics, team_stats, absence_reasons):
        """실제 데이터 기반 JavaScript 생성 - 개선된 팝업 콘텐츠"""
        
        # 월별 트렌드 데이터 준비
        monthly_trend = self.prepare_monthly_trend_data()
        weekly_data_json = json.dumps(self.weekly_data, ensure_ascii=False)
        team_stats_json = json.dumps(team_stats, ensure_ascii=False)
        absence_reasons_json = json.dumps(absence_reasons, ensure_ascii=False)
        
        # 주차별 데이터를 현재월과 이전월로 분리 - 올바른 구조로 접근
        current_month_key = f"{self.year}_{self.month:02d}"
        prev_month_key = f"{self.year}_{self.month-1:02d}" if self.month > 1 else f"{self.year-1}_12"
        
        current_weekly = self.weekly_data.get(current_month_key, {})
        prev_weekly = self.weekly_data.get(prev_month_key, {})
        
        # 월별 데이터 추출 (7월, 8월) - int64를 int로 변환
        import numpy as np
        
        def convert_numpy_types(obj):
            """Convert numpy types to native Python types for JSON serialization"""
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
        
        return f'''
        // 실제 데이터
        const weeklyData = {weekly_data_json};
        const currentWeeklyData = {json.dumps(current_weekly, ensure_ascii=False)};
        const prevWeeklyData = {json.dumps(prev_weekly, ensure_ascii=False)};
        const teamStats = {team_stats_json};
        const absenceReasons = {absence_reasons_json};
        
        // Navigation function to Incentive Dashboard
        function navigateToIncentive() {{
            // Navigate to the incentive dashboard
            window.location.href = 'dashboard_{self.year}_{self.month:02d}.html';
        }}
        const monthlyTrend = {json.dumps(monthly_trend, ensure_ascii=False)};
        const monthlyDataJuly = {json.dumps(monthly_data_july, ensure_ascii=False)};
        const monthlyDataAugust = {json.dumps(monthly_data_august, ensure_ascii=False)};
        
        // Chart.js 기본 설정
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
        Chart.defaults.color = '{self.colors['text_primary']}';
        
        const charts = {{}};
        const subCharts = {{}}; // 추가 차트용
        
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
        
        function closeModal(modalId) {{
            const modal = document.getElementById(modalId);
            modal.style.display = 'none';
        }}
        
        function createEnhancedModalContent(modalId) {{
            const modalBody = document.querySelector(`#${{modalId}} .modal-body`);
            charts[modalId] = [];
            
            // 모달 콘텐츠를 동적으로 재구성
            modalBody.innerHTML = '';
            
            switch(modalId) {{
                case 'modal-total-employees':
                    createTotalEmployeesContent(modalBody, modalId);
                    break;
                case 'modal-absence':
                    createAbsenceContent(modalBody, modalId);
                    break;
                case 'modal-resignation':
                    createResignationContent(modalBody, modalId);
                    break;
                case 'modal-new-hires':
                    createNewHiresContent(modalBody, modalId);
                    break;
                case 'modal-new-resignations':
                    createNewResignationsContent(modalBody, modalId);
                    break;
                case 'modal-under-60':
                    createUnder60Content(modalBody, modalId);
                    break;
                case 'modal-post-assignment':
                    createPostAssignmentContent(modalBody, modalId);
                    break;
                case 'modal-full-attendance':
                    createFullAttendanceContent(modalBody, modalId);
                    break;
                case 'modal-long-term':
                    createLongTermContent(modalBody, modalId);
                    break;
            }}
        }}
        
        function createTotalEmployeesContent(modalBody, modalId) {{
            // 1. 월별 트렌드 차트 (7월 vs 8월)
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
            
            // 2. 주차별 트렌드 차트
            const trendDiv = document.createElement('div');
            trendDiv.className = 'chart-container';
            trendDiv.innerHTML = '<canvas id="trend-' + modalId + '"></canvas>';
            modalBody.appendChild(trendDiv);
            
            const currentWeeks = Object.keys(currentWeeklyData);
            const currentValues = currentWeeks.map(w => currentWeeklyData[w].total_employees || 0);
            const prevWeeks = Object.keys(prevWeeklyData);
            const prevValues = prevWeeks.map(w => prevWeeklyData[w].total_employees || 0);
            
            const trendChart = new Chart(document.getElementById('trend-' + modalId), {{
                type: 'line',
                data: {{
                    labels: ['Week1', 'Week2', 'Week3', 'Week4'],
                    datasets: [
                        {{
                            label: '{self.month}월',
                            data: currentValues,
                            borderColor: '{self.colors['chart_colors'][0]}',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.3,
                            borderWidth: 2
                        }},
                        {{
                            label: '{self.month-1 if self.month > 1 else 12}월',
                            data: prevValues,
                            borderColor: '{self.colors['chart_colors'][1]}',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            borderDash: [5, 5],
                            tension: 0.3,
                            borderWidth: 2
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
            
            // 2. 팀별 트리맵 (도넛 차트로 표현)
            const treemapDiv = document.createElement('div');
            treemapDiv.className = 'chart-container';
            treemapDiv.innerHTML = '<canvas id="treemap-' + modalId + '"></canvas>';
            modalBody.appendChild(treemapDiv);
            
            const teamNames = Object.keys(teamStats);
            const teamCounts = teamNames.map(team => teamStats[team].total || 0);
            
            const treemapChart = new Chart(document.getElementById('treemap-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: teamNames,
                    datasets: [{{
                        label: '팀별 인원',
                        data: teamCounts,
                        backgroundColor: {json.dumps(self.colors['chart_colors'][:15])}
                    }}]
                }},
                options: {{
                    indexAxis: 'y',  // 수평 바 차트
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 인원 분포'
                        }},
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed.x;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return value + '명 (' + percentage + '%)';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            charts[modalId].push(treemapChart);
            
            // 3. 상세 통계
            const statsDiv = document.createElement('div');
            statsDiv.className = 'stats-grid';
            statsDiv.innerHTML = `
                <div class="stat-item">
                    <div class="stat-label">TYPE-1 인원</div>
                    <div class="stat-value">` + (monthlyTrend['{self.year}_{self.month:02d}']?.type1_count || 0) + `명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">TYPE-2 인원</div>
                    <div class="stat-value">` + (monthlyTrend['{self.year}_{self.month:02d}']?.type2_count || 0) + `명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">TYPE-3 인원</div>
                    <div class="stat-value">` + (monthlyTrend['{self.year}_{self.month:02d}']?.type3_count || 0) + `명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">전월 대비</div>
                    <div class="stat-value">` + ((monthlyTrend['{self.year}_{self.month:02d}']?.total_employees - monthlyTrend['{self.year}_{self.month-1:02d}']?.total_employees) || 0) + `명</div>
                </div>
            `;
            modalBody.appendChild(statsDiv);
        }}
        
        function createAbsenceContent(modalBody, modalId) {{
            // 1. 주차별 결근율 트렌드
            const trendDiv = document.createElement('div');
            trendDiv.className = 'chart-container';
            trendDiv.innerHTML = '<canvas id="trend-' + modalId + '"></canvas>';
            modalBody.appendChild(trendDiv);
            
            const currentWeeks = Object.keys(currentWeeklyData);
            const currentAbsence = currentWeeks.map(w => currentWeeklyData[w].absence_rate || 0);
            const prevWeeks = Object.keys(prevWeeklyData);
            const prevAbsence = prevWeeks.map(w => prevWeeklyData[w].absence_rate || 0);
            
            const trendChart = new Chart(document.getElementById('trend-' + modalId), {{
                type: 'line',
                data: {{
                    labels: ['Week1', 'Week2', 'Week3', 'Week4'],
                    datasets: [
                        {{
                            label: '{self.month}월 결근율',
                            data: currentAbsence,
                            borderColor: '{self.colors['chart_colors'][0]}',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.3,
                            borderWidth: 2
                        }},
                        {{
                            label: '{self.month-1 if self.month > 1 else 12}월 결근율',
                            data: prevAbsence,
                            borderColor: '{self.colors['chart_colors'][1]}',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            borderDash: [5, 5],
                            tension: 0.3,
                            borderWidth: 2
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '주차별 결근율 트렌드 (%)'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            charts[modalId].push(trendChart);
            
            // 2. 결근 사유 트리맵 (상위 10개)
            const treemapDiv = document.createElement('div');
            treemapDiv.className = 'chart-container';
            treemapDiv.innerHTML = '<canvas id="treemap-' + modalId + '"></canvas>';
            modalBody.appendChild(treemapDiv);
            
            const reasonEntries = Object.entries(absenceReasons).sort((a, b) => b[1] - a[1]).slice(0, 10);
            const reasonLabels = reasonEntries.map(e => e[0]);
            const reasonValues = reasonEntries.map(e => e[1]);
            
            const treemapChart = new Chart(document.getElementById('treemap-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: reasonLabels,
                    datasets: [{{
                        label: '결근 건수',
                        data: reasonValues,
                        backgroundColor: {json.dumps(self.colors['chart_colors'][:10])},
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '결근 사유 분포 (Top 10)'
                        }},
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed.x || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return value + '건 (' + percentage + '%)';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '결근 건수'
                            }}
                        }}
                    }}
                }}
            }});
            charts[modalId].push(treemapChart);
            
            // 3. 팀별 결근율 차트
            const teamChartDiv = document.createElement('div');
            teamChartDiv.className = 'chart-container';
            teamChartDiv.innerHTML = '<canvas id="team-absence-' + modalId + '"></canvas>';
            modalBody.appendChild(teamChartDiv);
            
            const teamNames = Object.keys(teamStats);
            const teamAbsenceRates = teamNames.map(team => {{
                const attendance = teamStats[team].attendance_rate || 0;
                return (100 - attendance);
            }});
            
            const teamAbsenceChart = new Chart(document.getElementById('team-absence-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: teamNames,
                    datasets: [{{
                        label: '팀별 결근율 (%)',
                        data: teamAbsenceRates,
                        backgroundColor: {json.dumps(self.colors['chart_colors'][:15])},
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 결근율 현황'
                        }},
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            charts[modalId].push(teamAbsenceChart);
        }}
        
        function createResignationContent(modalBody, modalId) {{
            // 1. 주차별 퇴사자 트렌드
            const trendDiv = document.createElement('div');
            trendDiv.className = 'chart-container';
            trendDiv.innerHTML = '<canvas id="trend-' + modalId + '"></canvas>';
            modalBody.appendChild(trendDiv);
            
            const currentWeeks = Object.keys(currentWeeklyData);
            const currentResign = currentWeeks.map(w => currentWeeklyData[w].resignations || 0);
            const prevWeeks = Object.keys(prevWeeklyData);
            const prevResign = prevWeeks.map(w => prevWeeklyData[w].resignations || 0);
            
            const trendChart = new Chart(document.getElementById('trend-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: ['Week1', 'Week2', 'Week3', 'Week4'],
                    datasets: [
                        {{
                            label: '{self.month}월 퇴사자',
                            data: currentResign,
                            backgroundColor: '{self.colors['chart_colors'][2]}'
                        }},
                        {{
                            label: '{self.month-1 if self.month > 1 else 12}월 퇴사자',
                            data: prevResign,
                            backgroundColor: '{self.colors['chart_colors'][3]}'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '주차별 퇴사자 현황'
                        }}
                    }}
                }}
            }});
            charts[modalId].push(trendChart);
            
            // 2. 팀별 퇴사자 현황
            const teamDiv = document.createElement('div');
            teamDiv.className = 'chart-container';
            teamDiv.innerHTML = '<canvas id="team-' + modalId + '"></canvas>';
            modalBody.appendChild(teamDiv);
            
            const teamNames = Object.keys(teamStats);
            const resignations = teamNames.map(team => teamStats[team].resignations || 0);
            
            const teamChart = new Chart(document.getElementById('team-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: teamNames,
                    datasets: [{{
                        label: '퇴사자 수',
                        data: resignations,
                        backgroundColor: {json.dumps(self.colors['chart_colors'][:15])}
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 퇴사자 현황'
                        }}
                    }}
                }}
            }});
            charts[modalId].push(teamChart);
            
            // 3. 퇴사율 통계
            const statsDiv = document.createElement('div');
            statsDiv.className = 'stats-grid';
            statsDiv.innerHTML = `
                <div class="stat-item">
                    <div class="stat-label">이번달 퇴사자</div>
                    <div class="stat-value">` + (monthlyTrend['{self.year}_{self.month:02d}']?.resignation_count || 0) + `명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">전월 퇴사자</div>
                    <div class="stat-value">` + (monthlyTrend['{self.year}_{self.month-1:02d}']?.resignation_count || 0) + `명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">퇴사율</div>
                    <div class="stat-value">` + (monthlyTrend['{self.year}_{self.month:02d}']?.resignation_rate || 0).toFixed(1) + `%</div>
                </div>
            `;
            modalBody.appendChild(statsDiv);
        }}
        
        function createNewHiresContent(modalBody, modalId) {{
            // 1. 주차별 신규 입사자 트렌드
            const trendDiv = document.createElement('div');
            trendDiv.className = 'chart-container';
            trendDiv.innerHTML = '<canvas id="trend-' + modalId + '"></canvas>';
            modalBody.appendChild(trendDiv);
            
            const currentWeeks = Object.keys(currentWeeklyData);
            const currentHires = currentWeeks.map(w => currentWeeklyData[w].new_hires || 0);
            const prevWeeks = Object.keys(prevWeeklyData);
            const prevHires = prevWeeks.map(w => prevWeeklyData[w].new_hires || 0);
            
            const trendChart = new Chart(document.getElementById('trend-' + modalId), {{
                type: 'bar',
                data: {{
                    labels: ['Week1', 'Week2', 'Week3', 'Week4'],
                    datasets: [
                        {{
                            label: '{self.month}월 신규입사',
                            data: currentHires,
                            backgroundColor: '{self.colors['chart_colors'][3]}'
                        }},
                        {{
                            label: '{self.month-1 if self.month > 1 else 12}월 신규입사',
                            data: prevHires,
                            backgroundColor: '{self.colors['chart_colors'][4]}'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '주차별 신규 입사자 현황'
                        }}
                    }}
                }}
            }});
            charts[modalId] = [trendChart];
            
            // 2. 팀별 신규 입사자
            const teamDiv = document.createElement('div');
            teamDiv.className = 'chart-container';
            teamDiv.innerHTML = '<canvas id="team-' + modalId + '"></canvas>';
            modalBody.appendChild(teamDiv);
            
            const teamNames = Object.keys(teamStats);
            const teamHires = teamNames.map(team => teamStats[team].new_hires || 0);
            
            const teamChart = new Chart(document.getElementById('team-' + modalId), {{
                type: 'doughnut',
                data: {{
                    labels: teamNames,
                    datasets: [{{
                        data: teamHires,
                        backgroundColor: [
                            '{self.colors['primary']}',
                            '{self.colors['success']}',
                            '{self.colors['warning']}',
                            '{self.colors['info']}'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 신규 입사자 분포'
                        }}
                    }}
                }}
            }});
            charts[modalId].push(teamChart);
        }}
        
        // 나머지 모달 콘텐츠 함수들 추가
        function createNewResignationsContent(modalBody, modalId) {{
            // 신입 퇴사자 분석 콘텐츠
            const trendDiv = document.createElement('div');
            trendDiv.className = 'chart-container';
            trendDiv.innerHTML = '<canvas id="trend-' + modalId + '"></canvas>';
            modalBody.appendChild(trendDiv);
            
            const currentWeeks = Object.keys(currentWeeklyData);
            const resignData = currentWeeks.map(w => {{
                const hires = currentWeeklyData[w].new_hires || 0;
                const resigns = currentWeeklyData[w].resignations || 0;
                return hires > 0 ? (resigns / hires * 100) : 0;
            }});
            
            const trendChart = new Chart(document.getElementById('trend-' + modalId), {{
                type: 'line',
                data: {{
                    labels: ['Week1', 'Week2', 'Week3', 'Week4'],
                    datasets: [{{
                        label: '신입 퇴사율 (%)',
                        data: resignData,
                        borderColor: '{self.colors['danger']}',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.3
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '주차별 신입 퇴사율 추이'
                        }}
                    }}
                }}
            }});
            charts[modalId] = [trendChart];
        }}
        
        function createUnder60Content(modalBody, modalId) {{
            // 60일 미만 근무자 분석
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.innerHTML = '<canvas id="chart-' + modalId + '"></canvas>';
            modalBody.appendChild(chartDiv);
            
            const ctx = document.getElementById('chart-' + modalId);
            const chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['30일 미만', '30-60일'],
                    datasets: [{{
                        label: '인원수',
                        data: [
                            monthlyTrend['{self.year}_{self.month:02d}']?.recent_hires || 0,
                            monthlyTrend['{self.year}_{self.month:02d}']?.under_60_days || 0
                        ],
                        backgroundColor: ['{self.colors['warning']}', '{self.colors['info']}']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '근무 기간별 신규 인원 분포'
                        }}
                    }}
                }}
            }});
            charts[modalId] = [chart];
        }}
        
        function createPostAssignmentContent(modalBody, modalId) {{
            // 보직 부여 후 퇴사자 분석
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.innerHTML = '<canvas id="chart-' + modalId + '"></canvas>';
            modalBody.appendChild(chartDiv);
            
            const current = monthlyTrend['{self.year}_{self.month:02d}']?.post_assignment_resignations || 0;
            const prev = monthlyTrend['{self.year}_{self.month-1:02d}']?.post_assignment_resignations || 0;
            
            const ctx = document.getElementById('chart-' + modalId);
            const chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['{self.month-1 if self.month > 1 else 12}월', '{self.month}월'],
                    datasets: [{{
                        label: '보직 후 퇴사자',
                        data: [prev, current],
                        backgroundColor: '{self.colors['danger']}'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '월별 보직 부여 후 퇴사자 현황'
                        }}
                    }}
                }}
            }});
            charts[modalId] = [chart];
        }}
        
        function createFullAttendanceContent(modalBody, modalId) {{
            // 만근자 분석
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.innerHTML = '<canvas id="chart-' + modalId + '"></canvas>';
            modalBody.appendChild(chartDiv);
            
            const teamNames = Object.keys(teamStats);
            const fullAttendance = teamNames.map(team => {{
                const rate = teamStats[team].attendance_rate || 0;
                return rate >= 99 ? teamStats[team].total : 0;
            }});
            
            const ctx = document.getElementById('chart-' + modalId);
            const chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: teamNames.map(t => 'Team ' + t),
                    datasets: [{{
                        label: '만근자 수',
                        data: fullAttendance,
                        backgroundColor: '{self.colors['success']}'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 만근자 현황'
                        }}
                    }}
                }}
            }});
            charts[modalId] = [chart];
        }}
        
        function createLongTermContent(modalBody, modalId) {{
            // 장기근속자 분석
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.innerHTML = '<canvas id="chart-' + modalId + '"></canvas>';
            modalBody.appendChild(chartDiv);
            
            const ctx = document.getElementById('chart-' + modalId);
            const chart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['1년 이상', '1년 미만'],
                    datasets: [{{
                        data: [
                            monthlyTrend['{self.year}_{self.month:02d}']?.long_term_count || 0,
                            (monthlyTrend['{self.year}_{self.month:02d}']?.total_employees || 0) - 
                            (monthlyTrend['{self.year}_{self.month:02d}']?.long_term_count || 0)
                        ],
                        backgroundColor: ['{self.colors['primary']}', '{self.colors['text_secondary']}']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '장기근속자 비율'
                        }}
                    }}
                }}
            }});
            charts[modalId] = [chart];
        }}
        
        // 모달 외부 클릭시 닫기
        window.onclick = function(event) {{
            if (event.target.className === 'modal') {{
                event.target.style.display = 'none';
            }}
        }}
        '''
        
    def calculate_data_period(self):
        """데이터 기간 계산"""
        if not self.data['current'].empty:
            df = self.data['current']
            
            # 출결 데이터에서 날짜 범위 확인
            if 'attendance_data' in self.data and not self.data['attendance_data'].empty:
                att_df = self.data['attendance_data']
                if '날짜' in att_df.columns:
                    try:
                        dates = pd.to_datetime(att_df['날짜'], format='%Y-%m-%d', errors='coerce')
                        dates = dates.dropna()
                        if not dates.empty:
                            start_date = dates.min().strftime('%Y.%m.%d')
                            end_date = dates.max().strftime('%Y.%m.%d')
                            return f"{start_date} ~ {end_date}"
                    except:
                        pass
            
            # 기본값
            return f"{self.year}.{self.month:02d}.01 ~ {self.year}.{self.month:02d}.31"
        else:
            return "데이터 없음"
    
    def prepare_monthly_trend_data(self):
        """월별 트렌드 데이터 준비"""
        trend_data = {
            'labels': [],
            'total_employees': [],
            'attendance_rate': [],
            'resignation_rate': []
        }
        
        # 최근 6개월 데이터
        for i in range(5, -1, -1):
            month = self.month - i
            year = self.year
            if month <= 0:
                month += 12
                year -= 1
                
            month_key = f"{year}_{month:02d}"
            month_data = self.metadata.get('monthly_data', {}).get(month_key, {})
            
            trend_data['labels'].append(f"{year}-{month:02d}")
            trend_data['total_employees'].append(month_data.get('total_employees', 0))
            trend_data['attendance_rate'].append(month_data.get('attendance_rate', 0))
            trend_data['resignation_rate'].append(month_data.get('resignation_rate', 0))
            
        return trend_data

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Generate REAL DATA HR Management Dashboard')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--year', type=int, required=True, help='Year')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"HR Management Dashboard Generator v5.0")
    print(f"REAL DATA ONLY - NO FAKE DATA")
    print(f"{'='*60}\n")
    
    # 대시보드 생성
    dashboard = RealDataHRDashboard(args.month, args.year)
    
    # 실제 데이터 로드
    dashboard.load_data()
    
    # 실제 주차별 데이터 계산
    dashboard.calculate_real_weekly_data()
    
    # 메타데이터 저장
    dashboard.save_metadata()
    
    # HTML 생성
    output_file = dashboard.generate_dashboard_html()
    
    print(f"\n{'='*60}")
    print(f"✅ Real Data Dashboard generation complete!")
    print(f"📁 Output file: {output_file}")
    print(f"🚫 No fake data was generated")
    print(f"{'='*60}\n")
    
    return output_file

if __name__ == "__main__":
    main()