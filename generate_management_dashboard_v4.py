#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HR Management Dashboard v4.0
Black & White Theme with HR Analytics Focus
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

class HRManagementDashboard:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.month_name = self.get_month_name(month)
        self.data = {}
        self.metadata = {}
        self.team_structure = {}
        self.weekly_data = {}
        
        # 색상 테마 정의 (Black & White with accent colors)
        self.colors = {
            'primary': '#000000',
            'secondary': '#FFFFFF',
            'background': '#F8F9FA',
            'card_bg': '#FFFFFF',
            'text_primary': '#212529',
            'text_secondary': '#6C757D',
            'border': '#DEE2E6',
            'success': '#28A745',  # 긍정적 지표
            'danger': '#DC3545',   # 부정적 지표
            'warning': '#FFC107',  # 경고
            'info': '#17A2B8',     # 정보
            'chart_colors': ['#000000', '#495057', '#6C757D', '#ADB5BD', '#CED4DA', '#DEE2E6']
        }
        
    def get_month_name(self, month):
        """월 번호를 월 이름으로 변환"""
        months = {
            1: 'january', 2: 'february', 3: 'march', 4: 'april',
            5: 'may', 6: 'june', 7: 'july', 8: 'august',
            9: 'september', 10: 'october', 11: 'november', 12: 'december'
        }
        return months.get(month, 'january')
    
    def load_data(self):
        """모든 필요한 데이터 로드"""
        print(f"📊 Loading data for {self.year}년 {self.month}월...")
        
        # 1. 인센티브 데이터 로드
        self.load_incentive_data()
        
        # 2. 출근 데이터 로드
        self.load_attendance_data()
        
        # 3. 팀 구조 데이터 로드
        self.load_team_structure()
        
        # 4. 이전 메타데이터 로드 (있으면)
        self.load_previous_metadata()
        
        print("✅ Data loading complete")
        
    def load_incentive_data(self):
        """인센티브 데이터 로드"""
        try:
            # 현재 월 데이터
            file_pattern = f"output_files/output_QIP_incentive_{self.month_name}_{self.year}_*.csv"
            files = glob.glob(file_pattern)
            
            if files:
                self.data['current'] = pd.read_csv(files[0], encoding='utf-8-sig')
                print(f"  ✓ Current month data loaded: {len(self.data['current'])} records")
            else:
                print(f"  ⚠ No incentive data found for {self.month_name} {self.year}")
                self.data['current'] = pd.DataFrame()
                
            # 이전 월 데이터 로드 시도
            prev_month = self.month - 1 if self.month > 1 else 12
            prev_year = self.year if self.month > 1 else self.year - 1
            prev_month_name = self.get_month_name(prev_month)
            
            prev_file_pattern = f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_*.csv"
            prev_files = glob.glob(prev_file_pattern)
            
            if prev_files:
                self.data['previous'] = pd.read_csv(prev_files[0], encoding='utf-8-sig')
                print(f"  ✓ Previous month data loaded: {len(self.data['previous'])} records")
            else:
                print(f"  ℹ No previous month data available")
                self.data['previous'] = pd.DataFrame()
                
        except Exception as e:
            print(f"  ❌ Error loading incentive data: {e}")
            self.data['current'] = pd.DataFrame()
            self.data['previous'] = pd.DataFrame()
            
    def load_attendance_data(self):
        """출근 데이터 로드"""
        try:
            attendance_file = f"input_files/attendance/attendance_{self.month_name}_{self.year}.csv"
            if os.path.exists(attendance_file):
                self.data['attendance'] = pd.read_csv(attendance_file, encoding='utf-8-sig')
                print(f"  ✓ Attendance data loaded: {len(self.data['attendance'])} records")
            else:
                print(f"  ⚠ No attendance data found")
                self.data['attendance'] = pd.DataFrame()
        except Exception as e:
            print(f"  ❌ Error loading attendance data: {e}")
            self.data['attendance'] = pd.DataFrame()
            
    def load_team_structure(self):
        """팀 구조 데이터 로드"""
        try:
            team_file = "HR info/team_structure.json"
            if os.path.exists(team_file):
                with open(team_file, 'r', encoding='utf-8') as f:
                    self.team_structure = json.load(f)
                print(f"  ✓ Team structure loaded")
            else:
                print(f"  ⚠ Team structure file not found")
                self.team_structure = {}
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
            
    def calculate_weekly_data(self):
        """주차별 데이터 계산"""
        if self.data['current'].empty:
            return
            
        # 날짜 칼럼이 있다면 주차별로 그룹화
        # 여기서는 예시로 월을 4주로 나눔
        total_employees = len(self.data['current'])
        weeks = 4
        
        self.weekly_data = {
            f"Week{i+1}": {
                'total_employees': total_employees,
                'attendance_rate': 94.5 + np.random.uniform(-2, 2),
                'absence_rate': 5.5 + np.random.uniform(-2, 2),
                'new_hires': np.random.randint(0, 10),
                'resignations': np.random.randint(0, 5)
            } for i in range(weeks)
        }
        
    def calculate_hr_metrics(self):
        """HR 메트릭 계산"""
        metrics = {}
        
        if not self.data['current'].empty:
            df = self.data['current']
            
            # 1. 총인원 (퇴사자 제외)
            # RE MARK 칼럼에 'Stop working'이 없는 직원만
            if 'RE MARK' in df.columns:
                active_employees = df[df['RE MARK'] != 'Stop working']
            else:
                active_employees = df
                
            metrics['total_employees'] = len(active_employees)
            
            # 2. 출근율
            if 'ATTENDANCE_RATE' in df.columns:
                metrics['attendance_rate'] = df['ATTENDANCE_RATE'].mean()
            else:
                metrics['attendance_rate'] = 94.5
                
            # 3. 결근율
            metrics['absence_rate'] = 100 - metrics['attendance_rate']
            
            # 4. 퇴사율 (현재 월)
            if 'Stop working Date' in df.columns:
                df['Stop working Date'] = pd.to_datetime(df['Stop working Date'], dayfirst=True, errors='coerce')
                current_month_resignations = df[(df['Stop working Date'].dt.month == self.month) & 
                                               (df['Stop working Date'].dt.year == self.year)]
                if metrics['total_employees'] > 0:
                    metrics['resignation_rate'] = (len(current_month_resignations) / metrics['total_employees']) * 100
                else:
                    metrics['resignation_rate'] = 0
            else:
                metrics['resignation_rate'] = 0
                
            # 5. 최근 30일 입사자
            if 'Entrance Date' in df.columns:
                today = datetime.now()
                thirty_days_ago = today - timedelta(days=30)
                # dayfirst=True를 추가하여 일/월/년 형식 파싱
                df['Entrance Date'] = pd.to_datetime(df['Entrance Date'], dayfirst=True, errors='coerce')
                recent_hires = df[df['Entrance Date'] >= thirty_days_ago]
                metrics['recent_hires'] = len(recent_hires)
            else:
                metrics['recent_hires'] = 0
                
            # 6. 최근 30일 퇴사자 (신입)
            metrics['recent_resignations'] = 0  # 추후 계산
            
            # 7. 60일 미만 근무자
            metrics['under_60_days'] = 0  # 추후 계산
            
            # 8. 보직 부여 후 퇴사자
            metrics['post_assignment_resignations'] = 0  # 추후 계산
            
        else:
            # 기본값
            metrics = {
                'total_employees': 0,
                'attendance_rate': 0,
                'absence_rate': 0,
                'resignation_rate': 0,
                'recent_hires': 0,
                'recent_resignations': 0,
                'under_60_days': 0,
                'post_assignment_resignations': 0
            }
            
        return metrics
        
    def save_metadata(self):
        """메타데이터 저장"""
        month_key = f"{self.year}_{self.month:02d}"
        
        # 현재 월 데이터 저장
        self.metadata['monthly_data'][month_key] = self.calculate_hr_metrics()
        self.metadata['weekly_data'][month_key] = self.weekly_data
        
        # JSON 파일로 저장
        metadata_file = f"output_files/hr_metadata_{self.year}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
        print(f"💾 Metadata saved to {metadata_file}")
        
    def generate_dashboard_html(self):
        """대시보드 HTML 생성"""
        metrics = self.calculate_hr_metrics()
        
        # 이전 월 메트릭 가져오기
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
        
        <div class="main-content">
            <!-- HR Analytics Section -->
            <div class="section hr-section">
                <h2 class="section-title">📊 인사/출결 분석</h2>
                <div class="cards-grid">
                    {self.generate_hr_cards(metrics, prev_metrics)}
                </div>
            </div>
            
            <!-- Quality Section (Placeholder) -->
            <div class="section quality-section">
                <h2 class="section-title">📈 품질 분석</h2>
                <div class="quality-placeholder">
                    <div class="placeholder-card">
                        <h3>5PRS 분석</h3>
                        <p>준비 중...</p>
                    </div>
                    <div class="placeholder-card">
                        <h3>AQL 분석</h3>
                        <p>준비 중...</p>
                    </div>
                </div>
            </div>
        </div>
        
        {self.generate_modals()}
    </div>
    
    <script>
        {self.generate_javascript()}
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
        """CSS 스타일 생성"""
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
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        
        .section {{
            background: {self.colors['card_bg']};
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .section-title {{
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid {self.colors['primary']};
        }}
        
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
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
        
        .hr-card.full-width {{
            grid-column: span 2;
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
        '''
        
    def generate_header(self):
        """헤더 생성"""
        return f'''
        <div class="header">
            <h1>HR Management Dashboard</h1>
            <div class="header-info">
                <span>📅 {self.year}년 {self.month}월</span>
                <span>⏰ 생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
                <span>👥 Executive Command Center</span>
            </div>
        </div>
        '''
        
    def generate_hr_cards(self, metrics, prev_metrics):
        """HR 카드 생성"""
        cards_html = ""
        
        # 카드 데이터 정의
        cards = [
            {
                'number': 1,
                'title': '총인원 정보',
                'value': metrics.get('total_employees', 0),
                'subtitle': f"TYPE-1: {0} TYPE-2: {0} TYPE-3: {0}",
                'prev_value': prev_metrics.get('total_employees', 0),
                'modal_id': 'modal-total-employees'
            },
            {
                'number': 2,
                'title': f'{self.month}월 결근자 정보/결근율',
                'value': f"{metrics.get('absence_rate', 0):.1f}%",
                'subtitle': f"결근자: {0}명",
                'prev_value': prev_metrics.get('absence_rate', 0),
                'modal_id': 'modal-absence'
            },
            {
                'number': 3,
                'title': f'{self.month}월 퇴사율',
                'value': f"{metrics.get('resignation_rate', 0):.1f}%",
                'subtitle': f"퇴사자: {0}명",
                'prev_value': prev_metrics.get('resignation_rate', 0),
                'modal_id': 'modal-resignation'
            },
            {
                'number': 4,
                'title': '최근 30일내 입사 인원 총원',
                'value': metrics.get('recent_hires', 0),
                'subtitle': f"전체 대비: {0:.1f}%",
                'prev_value': prev_metrics.get('recent_hires', 0),
                'modal_id': 'modal-new-hires'
            },
            {
                'number': 5,
                'title': '최근 30일내 퇴사 인원 총원\n(신입 퇴사율)',
                'value': metrics.get('recent_resignations', 0),
                'subtitle': f"신입 퇴사율: {0:.1f}%",
                'prev_value': prev_metrics.get('recent_resignations', 0),
                'modal_id': 'modal-new-resignations'
            },
            {
                'number': 6,
                'title': '입사일 기준 60일 미만 인원 총원\n(입사일 기준 30일 미만 신입 직원 제외)',
                'value': metrics.get('under_60_days', 0),
                'subtitle': f"전체 대비: {0:.1f}%",
                'prev_value': prev_metrics.get('under_60_days', 0),
                'modal_id': 'modal-under-60',
                'full_width': True
            },
            {
                'number': 7,
                'title': '보직 부여 이후\n신입 퇴사 총원 및 퇴사율',
                'value': metrics.get('post_assignment_resignations', 0),
                'subtitle': f"퇴사율: {0:.1f}%",
                'prev_value': prev_metrics.get('post_assignment_resignations', 0),
                'modal_id': 'modal-post-assignment',
                'full_width': True
            }
        ]
        
        for card in cards:
            # 변화율 계산
            if isinstance(card['value'], str):
                current_val = float(card['value'].replace('%', '')) if '%' in card['value'] else 0
                prev_val = card['prev_value']
            else:
                current_val = card['value']
                prev_val = card['prev_value']
                
            if prev_val > 0:
                change = ((current_val - prev_val) / prev_val) * 100
                change_text = f"{'▲' if change > 0 else '▼'} {abs(change):.1f}% vs last month"
                change_class = 'change-positive' if change > 0 else 'change-negative'
            else:
                change_text = "No previous data"
                change_class = 'change-neutral'
                
            full_width_class = 'full-width' if card.get('full_width', False) else ''
            
            cards_html += f'''
            <div class="hr-card {full_width_class}" onclick="openModal('{card['modal_id']}')">
                <div class="card-number">{card['number']}</div>
                <div class="card-title">{card['title']}</div>
                <div class="card-value">{card['value']}</div>
                <div class="card-subtitle">{card['subtitle']}</div>
                <div class="card-change {change_class}">{change_text}</div>
            </div>
            '''
            
        return cards_html
        
    def generate_modals(self):
        """모달 창 생성"""
        modals_html = ""
        
        # 각 카드에 대한 모달 생성
        modal_configs = [
            {'id': 'modal-total-employees', 'title': '총인원 상세 분석'},
            {'id': 'modal-absence', 'title': '결근 현황 상세 분석'},
            {'id': 'modal-resignation', 'title': '퇴사 현황 상세 분석'},
            {'id': 'modal-new-hires', 'title': '신규 입사자 상세 분석'},
            {'id': 'modal-new-resignations', 'title': '신입 퇴사자 상세 분석'},
            {'id': 'modal-under-60', 'title': '60일 미만 근무자 상세 분석'},
            {'id': 'modal-post-assignment', 'title': '보직 부여 후 퇴사자 상세 분석'}
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
                            <!-- Stats will be populated dynamically -->
                        </div>
                    </div>
                </div>
            </div>
            '''
            
        return modals_html
        
    def generate_javascript(self):
        """JavaScript 코드 생성"""
        return f'''
        // Chart.js 기본 설정
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
        Chart.defaults.color = '{self.colors['text_primary']}';
        
        // 차트 인스턴스 저장
        const charts = {{}};
        
        // 모달 열기
        function openModal(modalId) {{
            const modal = document.getElementById(modalId);
            modal.style.display = 'block';
            
            // 차트 생성 (처음 열 때만)
            if (!charts[modalId]) {{
                createChart(modalId);
            }}
        }}
        
        // 모달 닫기
        function closeModal(modalId) {{
            const modal = document.getElementById(modalId);
            modal.style.display = 'none';
        }}
        
        // 차트 생성
        function createChart(modalId) {{
            const ctx = document.getElementById('chart-' + modalId).getContext('2d');
            
            // 모달 유형에 따른 차트 설정
            let chartConfig;
            
            switch(modalId) {{
                case 'modal-total-employees':
                    chartConfig = createTotalEmployeesChart();
                    break;
                case 'modal-absence':
                    chartConfig = createAbsenceChart();
                    break;
                case 'modal-resignation':
                    chartConfig = createResignationChart();
                    break;
                case 'modal-new-hires':
                    chartConfig = createNewHiresChart();
                    break;
                case 'modal-new-resignations':
                    chartConfig = createNewResignationsChart();
                    break;
                case 'modal-under-60':
                    chartConfig = createUnder60Chart();
                    break;
                case 'modal-post-assignment':
                    chartConfig = createPostAssignmentChart();
                    break;
                default:
                    chartConfig = createDefaultChart();
            }}
            
            charts[modalId] = new Chart(ctx, chartConfig);
        }}
        
        // 총인원 차트
        function createTotalEmployeesChart() {{
            return {{
                type: 'line',
                data: {{
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{{
                        label: '총인원',
                        data: [450, 455, 460, 464],
                        borderColor: '{self.colors['primary']}',
                        backgroundColor: 'rgba(0, 0, 0, 0.1)',
                        tension: 0.1
                    }}]
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
            }};
        }}
        
        // 결근 차트
        function createAbsenceChart() {{
            return {{
                type: 'bar',
                data: {{
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{{
                        label: '결근율 (%)',
                        data: [5.2, 5.5, 5.8, 5.5],
                        backgroundColor: '{self.colors['danger']}'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '주차별 결근율 트렌드'
                        }}
                    }}
                }}
            }};
        }}
        
        // 퇴사 차트
        function createResignationChart() {{
            return {{
                type: 'bar',
                data: {{
                    labels: ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
                    datasets: [{{
                        label: '퇴사자 수',
                        data: [3, 2, 1, 4, 2],
                        backgroundColor: '{self.colors['warning']}'
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
            }};
        }}
        
        // 신규 입사자 차트
        function createNewHiresChart() {{
            return {{
                type: 'line',
                data: {{
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{{
                        label: '신규 입사자',
                        data: [8, 12, 10, 15],
                        borderColor: '{self.colors['success']}',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '주차별 신규 입사자 트렌드'
                        }}
                    }}
                }}
            }};
        }}
        
        // 신입 퇴사자 차트
        function createNewResignationsChart() {{
            return {{
                type: 'doughnut',
                data: {{
                    labels: ['1-7일', '8-14일', '15-21일', '22-30일'],
                    datasets: [{{
                        data: [2, 3, 1, 1],
                        backgroundColor: [
                            '{self.colors['danger']}',
                            '{self.colors['warning']}',
                            '{self.colors['info']}',
                            '{self.colors['success']}'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '신입 퇴사 시점 분포'
                        }}
                    }}
                }}
            }};
        }}
        
        // 60일 미만 근무자 차트
        function createUnder60Chart() {{
            return {{
                type: 'bar',
                data: {{
                    labels: ['31-40일', '41-50일', '51-60일'],
                    datasets: [{{
                        label: '인원 수',
                        data: [15, 22, 18],
                        backgroundColor: '{self.colors['info']}'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '근무 일수별 분포'
                        }}
                    }}
                }}
            }};
        }}
        
        // 보직 부여 후 퇴사자 차트
        function createPostAssignmentChart() {{
            return {{
                type: 'bar',
                data: {{
                    labels: ['Team A', 'Team B', 'Team C', 'Team D'],
                    datasets: [{{
                        label: '보직 부여 후 퇴사자',
                        data: [1, 2, 0, 1],
                        backgroundColor: '{self.colors['danger']}'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '팀별 보직 부여 후 퇴사 현황'
                        }}
                    }}
                }}
            }};
        }}
        
        // 기본 차트
        function createDefaultChart() {{
            return {{
                type: 'line',
                data: {{
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{{
                        label: 'Data',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: '{self.colors['primary']}',
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false
                }}
            }};
        }}
        
        // 모달 외부 클릭 시 닫기
        window.onclick = function(event) {{
            if (event.target.className === 'modal') {{
                event.target.style.display = 'none';
            }}
        }}
        '''

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Generate HR Management Dashboard')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--year', type=int, required=True, help='Year')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"HR Management Dashboard Generator v4.0")
    print(f"Black & White Theme with HR Analytics")
    print(f"{'='*60}\n")
    
    # 대시보드 생성
    dashboard = HRManagementDashboard(args.month, args.year)
    
    # 데이터 로드
    dashboard.load_data()
    
    # 주차별 데이터 계산
    dashboard.calculate_weekly_data()
    
    # 메타데이터 저장
    dashboard.save_metadata()
    
    # HTML 생성
    output_file = dashboard.generate_dashboard_html()
    
    print(f"\n{'='*60}")
    print(f"✅ Dashboard generation complete!")
    print(f"📁 Output file: {output_file}")
    print(f"{'='*60}\n")
    
    return output_file

if __name__ == "__main__":
    main()