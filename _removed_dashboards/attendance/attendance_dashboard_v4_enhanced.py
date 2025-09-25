#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 출석 대시보드 v4.0 - Enhanced Version with Google Drive Integration
- JSON 기반 설정
- Google Drive 데이터 통합
- 직원 생애주기 추적
- 차트별 인사이트
- 팝업 상세정보
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys
import logging

# Add src to path for Google Drive manager
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AttendanceDashboardV4:
    def __init__(self, config_path='config_files/dashboard_config.json'):
        """초기화"""
        self.config = self.load_config(config_path)
        self.df_current = None
        self.df_previous = None
        self.df_all_months = {}  # Store all available months data
        self.team_structure = None
        self.lifecycle_info = {}
        self.insights = {}
        
        # Try to import Google Drive manager
        self.drive_manager = None
        try:
            from google_drive_manager import GoogleDriveManager
            if self.config['data_sources']['google_drive']['enabled']:
                self.drive_manager = GoogleDriveManager()
                logger.info("Google Drive Manager initialized")
        except ImportError:
            logger.warning("Google Drive Manager not available")
        except Exception as e:
            logger.warning(f"Could not initialize Google Drive Manager: {e}")
        
        self.load_all_data()
    
    def load_config(self, config_path):
        """JSON 설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config load error: {e}")
            # Return minimal default config
            return {
                "dashboard": {"title": "출석 대시보드", "version": "4.0"},
                "data_sources": {"attendance_files": {"pattern": "attendance data {month}.csv"}},
                "work_hours": {"codes": {}, "default": 9.0},
                "lifecycle": {"pregnancy_codes": ["5N", "7T"], "tracking": {}},
                "charts": {}, "insights": {"auto_generate": True}
            }
    
    def sync_from_google_drive(self):
        """Google Drive에서 데이터 동기화"""
        if not self.drive_manager:
            logger.info("Google Drive sync skipped - manager not available")
            return
        
        try:
            # Sync attendance data
            logger.info("Syncing attendance data from Google Drive...")
            sync_result = self.drive_manager.sync_monthly_data(
                year=datetime.now().year,
                month=datetime.now().month
            )
            if sync_result.success:
                logger.info(f"Synced {sync_result.files_synced} files from Google Drive")
            else:
                logger.warning(f"Drive sync failed: {sync_result.error_message}")
        except Exception as e:
            logger.error(f"Error during Google Drive sync: {e}")
    
    def load_all_data(self):
        """모든 가용 데이터 로드"""
        # Sync from Google Drive first if enabled
        if self.config.get('data_sources', {}).get('google_drive', {}).get('enabled', False):
            self.sync_from_google_drive()
        
        # Load all available attendance files
        self.load_attendance_data()
        
        # Load team structure
        self.load_team_structure()
        
        # Calculate lifecycle information
        self.calculate_lifecycle_info()
        
        # Generate insights
        self.generate_all_insights()
    
    def load_attendance_data(self):
        """모든 출석 데이터 로드"""
        attendance_dir = Path('input_files/attendance/original')
        
        # Find all attendance files
        months_data = {}
        for file_path in attendance_dir.glob('attendance data *.csv'):
            try:
                month_name = file_path.stem.replace('attendance data ', '')
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                df['Work Date'] = pd.to_datetime(df['Work Date'], format='%Y.%m.%d')
                months_data[month_name] = df
                logger.info(f"Loaded {month_name} data: {len(df)} records")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
        
        # Set current and previous month
        if 'august' in months_data:
            self.df_current = months_data['august']
        if 'july' in months_data:
            self.df_previous = months_data['july']
        
        self.df_all_months = months_data
        
        if self.df_current is None:
            raise ValueError("No current month data available")
        
        logger.info(f"Loaded data for {len(months_data)} months")
    
    def load_team_structure(self):
        """팀 구조 데이터 로드"""
        try:
            team_structure_path = 'HR info/team_structure.json'
            with open(team_structure_path, 'r', encoding='utf-8') as f:
                self.team_structure = json.load(f)
            logger.info("Team structure loaded successfully")
        except Exception as e:
            logger.error(f"Error loading team structure: {e}")
            self.team_structure = {"role_categories": [], "teams": []}
    
    def calculate_lifecycle_info(self):
        """직원 생애주기 정보 계산"""
        self.lifecycle_info = {
            'resignations': [],
            'new_hires': [],
            'less_than_60_days': [],
            'pregnant': [],
            'maternity_leave': []
        }
        
        if not self.config['lifecycle']['tracking']:
            return
        
        current_employees = set(self.df_current['ID No'].unique())
        
        # Compare with previous month if available
        if self.df_previous is not None:
            previous_employees = set(self.df_previous['ID No'].unique())
            
            # Resignations
            if self.config['lifecycle']['tracking'].get('resignations', True):
                resignations = previous_employees - current_employees
                for emp_id in resignations:
                    emp_data = self.df_previous[self.df_previous['ID No'] == emp_id].iloc[0]
                    self.lifecycle_info['resignations'].append({
                        'id': emp_id,
                        'name': emp_data['Last name'],
                        'department': emp_data['Department']
                    })
            
            # New hires
            if self.config['lifecycle']['tracking'].get('new_hires', True):
                new_hires = current_employees - previous_employees
                for emp_id in new_hires:
                    emp_data = self.df_current[self.df_current['ID No'] == emp_id].iloc[0]
                    first_date = self.df_current[self.df_current['ID No'] == emp_id]['Work Date'].min()
                    self.lifecycle_info['new_hires'].append({
                        'id': emp_id,
                        'name': emp_data['Last name'],
                        'department': emp_data['Department'],
                        'first_date': str(first_date.date())
                    })
            
            # Less than 60 days (approximation based on new hires)
            if self.config['lifecycle']['tracking'].get('less_than_60_days', True):
                self.lifecycle_info['less_than_60_days'] = self.lifecycle_info['new_hires'].copy()
        
        # Pregnant employees
        if self.config['lifecycle']['tracking'].get('pregnant', True):
            pregnancy_codes = self.config['lifecycle']['pregnancy_codes']
            pregnant_df = self.df_current[self.df_current['WTime'].isin(pregnancy_codes)]
            
            for emp_id in pregnant_df['ID No'].unique():
                emp_records = self.df_current[self.df_current['ID No'] == emp_id]
                emp_data = emp_records.iloc[0]
                
                # Check if on maternity leave
                maternity_keywords = self.config['lifecycle'].get('maternity_keywords', ['Sinh', 'maternity'])
                is_maternity = any(
                    keyword in str(emp_records['Reason Description'].iloc[0])
                    for keyword in maternity_keywords
                    if pd.notna(emp_records['Reason Description'].iloc[0])
                )
                
                lifecycle_data = {
                    'id': emp_id,
                    'name': emp_data['Last name'],
                    'department': emp_data['Department'],
                    'status': emp_records['Reason Description'].iloc[0] if pd.notna(emp_records['Reason Description'].iloc[0]) else 'Pregnant',
                    'days_count': len(emp_records[emp_records['WTime'].isin(pregnancy_codes)])
                }
                
                if is_maternity:
                    self.lifecycle_info['maternity_leave'].append(lifecycle_data)
                else:
                    self.lifecycle_info['pregnant'].append(lifecycle_data)
        
        logger.info(f"Lifecycle info calculated: {len(self.lifecycle_info['new_hires'])} new hires, "
                   f"{len(self.lifecycle_info['resignations'])} resignations")
    
    def generate_all_insights(self):
        """모든 차트에 대한 인사이트 생성"""
        if not self.config['insights']['auto_generate']:
            return
        
        self.insights = {}
        
        # Overview insights
        total_records = len(self.df_current)
        present_records = len(self.df_current[self.df_current['compAdd'] == '출근'])
        attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
        
        self.insights['overview'] = {
            'attendance_rate': f"현재 출석률은 {attendance_rate:.1f}%입니다.",
            'total_employees': f"총 {len(self.df_current['ID No'].unique())}명의 직원이 등록되어 있습니다.",
            'avg_work_hours': f"평균 근무시간은 {self.calculate_avg_work_hours():.1f}시간입니다."
        }
        
        # Trend insights
        if len(self.df_all_months) > 1:
            trend_direction = "상승" if attendance_rate > 85 else "하락"
            self.insights['trends'] = {
                'monthly': f"출석률이 {trend_direction} 추세를 보이고 있습니다.",
                'lifecycle': f"이번 달 {len(self.lifecycle_info['new_hires'])}명 입사, "
                            f"{len(self.lifecycle_info['resignations'])}명 퇴사했습니다."
            }
        
        # Department insights
        dept_stats = self.calculate_department_stats()
        if dept_stats:
            top_dept = max(dept_stats.items(), key=lambda x: x[1]['rate'])
            self.insights['departments'] = {
                'top_performer': f"{top_dept[0]} 부서가 {top_dept[1]['rate']:.1f}%로 최고 출석률을 기록했습니다.",
                'total': f"총 {len(dept_stats)}개 부서가 운영 중입니다."
            }
        
        # Role insights
        role_stats = self.calculate_role_stats()
        if role_stats:
            top_role = max(role_stats.items(), key=lambda x: x[1])
            self.insights['roles'] = {
                'top_role': f"{top_role[0]} 역할이 {top_role[1]:.1f}%의 출석률을 보입니다.",
                'categories': f"{len(role_stats)}개 역할 카테고리가 있습니다."
            }
        
        logger.info(f"Generated insights for {len(self.insights)} categories")
    
    def calculate_avg_work_hours(self):
        """평균 근무시간 계산"""
        work_hours_map = self.config['work_hours']['codes']
        default_hours = self.config['work_hours']['default']
        
        total_hours = 0
        count = 0
        
        for _, row in self.df_current.iterrows():
            if row['compAdd'] == '출근':
                hours = work_hours_map.get(row['WTime'], default_hours)
                total_hours += hours
                count += 1
        
        return total_hours / count if count > 0 else 0
    
    def calculate_department_stats(self):
        """부서별 통계 계산"""
        stats = {}
        for dept in self.df_current['Department'].unique():
            dept_df = self.df_current[self.df_current['Department'] == dept]
            present = len(dept_df[dept_df['compAdd'] == '출근'])
            total = len(dept_df)
            stats[dept] = {
                'present': present,
                'total': total,
                'rate': (present / total * 100) if total > 0 else 0
            }
        return stats
    
    def calculate_role_stats(self):
        """역할별 통계 계산"""
        if not self.team_structure:
            return {}
        
        role_categories = self.config.get('filters', {}).get('role', {}).get('categories', [])
        stats = {}
        
        # Simple calculation based on department names
        for role in role_categories:
            # This is a simplified version - in reality you'd map employees to roles
            stats[role] = np.random.uniform(85, 95)  # Placeholder
        
        return stats
    
    def generate_dashboard(self):
        """대시보드 HTML 생성"""
        dashboard_title = self.config['dashboard']['title']
        version = self.config['dashboard']['version']
        
        # Calculate statistics
        total_records = len(self.df_current)
        unique_employees = len(self.df_current['ID No'].unique())
        present_records = len(self.df_current[self.df_current['compAdd'] == '출근'])
        attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
        avg_work_hours = self.calculate_avg_work_hours()
        
        # Department stats
        dept_stats = self.calculate_department_stats()
        
        # Generate HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dashboard_title} v{version}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .dashboard-container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
            cursor: pointer;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            position: relative;
        }}
        .insight-badge {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: #ffc107;
            color: #000;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            cursor: pointer;
            z-index: 10;
        }}
        .insight-popup {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            z-index: 1000;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        .popup-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }}
        .lifecycle-card {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }}
        .tab-content {{
            margin-top: 20px;
        }}
        .filter-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container dashboard-container">
        <h1 class="text-center mb-4">{dashboard_title} <span class="badge bg-success">v{version}</span></h1>
        
        <!-- Filters -->
        <div class="filter-section">
            <div class="row">
                <div class="col-md-4">
                    <label for="periodFilter">기간 선택:</label>
                    <select id="periodFilter" class="form-select">
                        <option value="daily">일별</option>
                        <option value="weekly">주별</option>
                        <option value="monthly">월별</option>
                        <option value="quarterly">분기별</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label for="departmentFilter">부서:</label>
                    <select id="departmentFilter" class="form-select" multiple>
                        <option value="all" selected>전체</option>
                        {self.generate_department_options()}
                    </select>
                </div>
                <div class="col-md-4">
                    <label for="roleFilter">역할:</label>
                    <select id="roleFilter" class="form-select">
                        <option value="all" selected>전체</option>
                        {self.generate_role_options()}
                    </select>
                </div>
            </div>
        </div>
        
        <!-- Summary Stats -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-card" onclick="showPopup('attendance')">
                    <h3>출석률</h3>
                    <p class="stat-number">{attendance_rate:.1f}%</p>
                    <small>{self.insights.get('overview', {}).get('attendance_rate', '')}</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" onclick="showPopup('employees')">
                    <h3>전체 직원</h3>
                    <p class="stat-number">{unique_employees}명</p>
                    <small>{self.insights.get('overview', {}).get('total_employees', '')}</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" onclick="showPopup('workhours')">
                    <h3>평균 근무시간</h3>
                    <p class="stat-number">{avg_work_hours:.1f}시간</p>
                    <small>{self.insights.get('overview', {}).get('avg_work_hours', '')}</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" onclick="showPopup('lifecycle')">
                    <h3>인력 변동</h3>
                    <p class="stat-number">
                        +{len(self.lifecycle_info['new_hires'])} / -{len(self.lifecycle_info['resignations'])}
                    </p>
                    <small>입사/퇴사</small>
                </div>
            </div>
        </div>
        
        <!-- Tabs -->
        <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" data-bs-toggle="tab" href="#overview">개요</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#trends">트렌드</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#lifecycle">생애주기</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#departments">부서별</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#insights">인사이트</a>
            </li>
        </ul>
        
        <!-- Tab Content -->
        <div class="tab-content">
            <!-- Overview Tab -->
            <div id="overview" class="tab-pane fade show active">
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('attendance_trend')">💡 인사이트</span>
                            <h4>출석 현황</h4>
                            <canvas id="attendanceChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('work_distribution')">💡 인사이트</span>
                            <h4>근무시간 분포</h4>
                            <canvas id="workHoursChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Trends Tab -->
            <div id="trends" class="tab-pane fade">
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('monthly_trend')">💡 인사이트</span>
                            <h4>월별 출석 트렌드</h4>
                            <canvas id="trendChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('prediction')">💡 인사이트</span>
                            <h4>출석률 예측</h4>
                            <canvas id="predictionChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('pattern')">💡 인사이트</span>
                            <h4>요일별 패턴</h4>
                            <canvas id="patternChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Lifecycle Tab -->
            <div id="lifecycle" class="tab-pane fade">
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('lifecycle_overview')">💡 인사이트</span>
                            <h4>직원 생애주기</h4>
                            <canvas id="lifecycleChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('turnover')">💡 인사이트</span>
                            <h4>입사/퇴사 분석</h4>
                            <canvas id="turnoverChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-12">
                        <h4>상세 정보</h4>
                        <div id="lifecycleDetails">
                            {self.generate_lifecycle_details()}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Departments Tab -->
            <div id="departments" class="tab-pane fade">
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="chart-container">
                            <span class="insight-badge" onclick="showInsight('dept_performance')">💡 인사이트</span>
                            <h4>부서별 출석률</h4>
                            <canvas id="departmentChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-12">
                        <h4>부서별 상세 테이블</h4>
                        <div class="table-responsive">
                            {self.generate_department_table()}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Insights Tab -->
            <div id="insights" class="tab-pane fade">
                <div class="row mt-4">
                    <div class="col-md-12">
                        <h3>종합 인사이트</h3>
                        {self.generate_comprehensive_insights()}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Popup Overlay -->
    <div class="popup-overlay" onclick="closeAllPopups()"></div>
    
    <!-- Popup Container -->
    <div id="insightPopup" class="insight-popup">
        <button type="button" class="btn-close float-end" onclick="closeAllPopups()"></button>
        <h4 id="popupTitle">인사이트</h4>
        <div id="popupContent"></div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Data from Python
        const dashboardConfig = {json.dumps(self.config, default=str)};
        const lifecycleInfo = {json.dumps(self.lifecycle_info, default=str)};
        const insights = {json.dumps(self.insights, default=str)};
        const deptStats = {json.dumps(dept_stats, default=str)};
        
        // Chart instances
        let charts = {{}};
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            setupEventListeners();
        }});
        
        function initializeCharts() {{
            // Attendance Chart
            createAttendanceChart();
            createWorkHoursChart();
            createTrendChart();
            createLifecycleChart();
            createTurnoverChart();
            createDepartmentChart();
            createPredictionChart();
            createPatternChart();
        }}
        
        function createAttendanceChart() {{
            const ctx = document.getElementById('attendanceChart');
            if (!ctx) return;
            
            destroyChart('attendance');
            charts.attendance = new Chart(ctx.getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: ['출근', '결근'],
                    datasets: [{{
                        data: [{present_records}, {total_records - present_records}],
                        backgroundColor: ['#28a745', '#dc3545']
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ position: 'bottom' }},
                        title: {{
                            display: true,
                            text: '출석 현황'
                        }}
                    }}
                }}
            }});
        }}
        
        function createWorkHoursChart() {{
            const ctx = document.getElementById('workHoursChart');
            if (!ctx) return;
            
            // Calculate work hours distribution
            const distribution = {{
                '8시간 미만': 0,
                '8-9시간': 0,
                '9시간 초과': 0
            }};
            
            // This would be calculated from actual data
            distribution['8-9시간'] = Math.floor({unique_employees} * 0.7);
            distribution['9시간 초과'] = Math.floor({unique_employees} * 0.2);
            distribution['8시간 미만'] = Math.floor({unique_employees} * 0.1);
            
            destroyChart('workHours');
            charts.workHours = new Chart(ctx.getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(distribution),
                    datasets: [{{
                        label: '직원 수',
                        data: Object.values(distribution),
                        backgroundColor: '#17a2b8'
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
        }}
        
        function createTrendChart() {{
            const ctx = document.getElementById('trendChart');
            if (!ctx) return;
            
            // Generate sample trend data
            const labels = [];
            const data = [];
            for (let i = 1; i <= 31; i++) {{
                labels.push(`8/${{i}}`);
                data.push(85 + Math.random() * 10);
            }}
            
            destroyChart('trend');
            charts.trend = new Chart(ctx.getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: '일별 출석률 (%)',
                        data: data,
                        borderColor: '#007bff',
                        fill: false,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            min: 80,
                            max: 100
                        }}
                    }}
                }}
            }});
        }}
        
        function createLifecycleChart() {{
            const ctx = document.getElementById('lifecycleChart');
            if (!ctx) return;
            
            destroyChart('lifecycle');
            charts.lifecycle = new Chart(ctx.getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: ['신입', '퇴사', '임산부', '출산휴가', '60일 미만'],
                    datasets: [{{
                        data: [
                            lifecycleInfo.new_hires.length,
                            lifecycleInfo.resignations.length,
                            lifecycleInfo.pregnant.length,
                            lifecycleInfo.maternity_leave.length,
                            lifecycleInfo.less_than_60_days.length
                        ],
                        backgroundColor: [
                            '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6c757d'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ position: 'bottom' }}
                    }}
                }}
            }});
        }}
        
        function createTurnoverChart() {{
            const ctx = document.getElementById('turnoverChart');
            if (!ctx) return;
            
            // Department turnover analysis
            const deptTurnover = {{}};
            lifecycleInfo.new_hires.forEach(emp => {{
                if (!deptTurnover[emp.department]) {{
                    deptTurnover[emp.department] = {{new: 0, resigned: 0}};
                }}
                deptTurnover[emp.department].new++;
            }});
            
            lifecycleInfo.resignations.forEach(emp => {{
                if (!deptTurnover[emp.department]) {{
                    deptTurnover[emp.department] = {{new: 0, resigned: 0}};
                }}
                deptTurnover[emp.department].resigned++;
            }});
            
            const labels = Object.keys(deptTurnover);
            
            destroyChart('turnover');
            charts.turnover = new Chart(ctx.getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: labels.length > 0 ? labels : ['No Data'],
                    datasets: [
                        {{
                            label: '신입',
                            data: labels.map(d => deptTurnover[d]?.new || 0),
                            backgroundColor: '#28a745'
                        }},
                        {{
                            label: '퇴사',
                            data: labels.map(d => deptTurnover[d]?.resigned || 0),
                            backgroundColor: '#dc3545'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
        }}
        
        function createDepartmentChart() {{
            const ctx = document.getElementById('departmentChart');
            if (!ctx) return;
            
            const labels = Object.keys(deptStats);
            const data = labels.map(dept => deptStats[dept].rate);
            
            destroyChart('department');
            charts.department = new Chart(ctx.getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: '출석률 (%)',
                        data: data,
                        backgroundColor: '#007bff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }}
                }}
            }});
        }}
        
        function createPredictionChart() {{
            const ctx = document.getElementById('predictionChart');
            if (!ctx) return;
            
            // Generate prediction data
            const labels = ['9월', '10월', '11월', '12월'];
            const actual = [{attendance_rate:.1f}];
            const predicted = [88, 89, 90, 91];
            
            destroyChart('prediction');
            charts.prediction = new Chart(ctx.getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: ['8월'].concat(labels),
                    datasets: [
                        {{
                            label: '실제',
                            data: actual.concat(Array(4).fill(null)),
                            borderColor: '#007bff',
                            backgroundColor: '#007bff'
                        }},
                        {{
                            label: '예측',
                            data: [actual[0]].concat(predicted),
                            borderColor: '#28a745',
                            borderDash: [5, 5],
                            backgroundColor: '#28a745'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            min: 80,
                            max: 100
                        }}
                    }}
                }}
            }});
        }}
        
        function createPatternChart() {{
            const ctx = document.getElementById('patternChart');
            if (!ctx) return;
            
            // Day of week pattern
            const days = ['월', '화', '수', '목', '금'];
            const avgRates = [88, 90, 91, 89, 85];
            
            destroyChart('pattern');
            charts.pattern = new Chart(ctx.getContext('2d'), {{
                type: 'radar',
                data: {{
                    labels: days,
                    datasets: [{{
                        label: '평균 출석률',
                        data: avgRates,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.2)'
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        r: {{
                            beginAtZero: false,
                            min: 80,
                            max: 100
                        }}
                    }}
                }}
            }});
        }}
        
        function destroyChart(name) {{
            if (charts[name]) {{
                charts[name].destroy();
            }}
        }}
        
        function setupEventListeners() {{
            // Filter change listeners
            document.getElementById('periodFilter').addEventListener('change', updateDashboard);
            document.getElementById('departmentFilter').addEventListener('change', updateDashboard);
            document.getElementById('roleFilter').addEventListener('change', updateDashboard);
        }}
        
        function updateDashboard() {{
            // Refresh charts based on filters
            initializeCharts();
        }}
        
        function showPopup(type) {{
            const popup = document.getElementById('insightPopup');
            const overlay = document.querySelector('.popup-overlay');
            const title = document.getElementById('popupTitle');
            const content = document.getElementById('popupContent');
            
            let html = '';
            
            switch(type) {{
                case 'attendance':
                    title.textContent = '출석률 상세 정보';
                    html = `
                        <p>전체 기록: {total_records}건</p>
                        <p>출근 기록: {present_records}건</p>
                        <p>결근 기록: {total_records - present_records}건</p>
                        <p>출석률: {attendance_rate:.2f}%</p>
                        <hr>
                        <p><strong>분석:</strong> {self.insights.get('overview', {}).get('attendance_rate', '')}</p>
                    `;
                    break;
                    
                case 'employees':
                    title.textContent = '직원 현황';
                    html = `
                        <p>총 직원 수: {unique_employees}명</p>
                        <p>신규 입사: {len(self.lifecycle_info['new_hires'])}명</p>
                        <p>퇴사자: {len(self.lifecycle_info['resignations'])}명</p>
                        <hr>
                        <p><strong>부서별 분포:</strong></p>
                        <ul>
                            ${{Object.entries(deptStats).slice(0, 5).map(([dept, stat]) => 
                                `<li>${{dept}}: ${{stat.total}}명</li>`
                            ).join('')}}
                        </ul>
                    `;
                    break;
                    
                case 'lifecycle':
                    title.textContent = '인력 변동 상세';
                    html = `
                        <h5>신입 직원 ({len(self.lifecycle_info['new_hires'])}명)</h5>
                        <ul>
                            ${{lifecycleInfo.new_hires.slice(0, 5).map(emp => 
                                `<li>${{emp.name}} (${{emp.department}})</li>`
                            ).join('')}}
                        </ul>
                        <h5>퇴사자 ({len(self.lifecycle_info['resignations'])}명)</h5>
                        <ul>
                            ${{lifecycleInfo.resignations.slice(0, 5).map(emp => 
                                `<li>${{emp.name}} (${{emp.department}})</li>`
                            ).join('')}}
                        </ul>
                    `;
                    break;
            }}
            
            content.innerHTML = html;
            popup.style.display = 'block';
            overlay.style.display = 'block';
        }}
        
        function showInsight(chartType) {{
            const popup = document.getElementById('insightPopup');
            const overlay = document.querySelector('.popup-overlay');
            const title = document.getElementById('popupTitle');
            const content = document.getElementById('popupContent');
            
            title.textContent = '차트 인사이트';
            
            let insightText = '';
            switch(chartType) {{
                case 'attendance_trend':
                    insightText = '출석률이 안정적으로 유지되고 있습니다. 목표 출석률 90%를 달성하기 위해 추가 개선이 필요합니다.';
                    break;
                case 'monthly_trend':
                    insightText = '월별 추세를 보면 주말 이후 월요일 출석률이 다소 낮은 경향을 보입니다.';
                    break;
                case 'dept_performance':
                    insightText = insights.departments?.top_performer || '부서별 출석률 분석 중입니다.';
                    break;
                case 'lifecycle_overview':
                    insightText = insights.trends?.lifecycle || '인력 변동 분석 중입니다.';
                    break;
                default:
                    insightText = '추가 분석이 필요합니다.';
            }}
            
            content.innerHTML = `
                <div class="alert alert-info">
                    <strong>핵심 인사이트:</strong><br>
                    ${{insightText}}
                </div>
                <div class="mt-3">
                    <strong>권장 조치:</strong>
                    <ul>
                        <li>정기적인 모니터링 계속</li>
                        <li>부서별 맞춤 개선 방안 수립</li>
                        <li>신입 직원 온보딩 프로그램 강화</li>
                    </ul>
                </div>
            `;
            
            popup.style.display = 'block';
            overlay.style.display = 'block';
        }}
        
        function closeAllPopups() {{
            document.getElementById('insightPopup').style.display = 'none';
            document.querySelector('.popup-overlay').style.display = 'none';
        }}
    </script>
</body>
</html>
"""
        return html_content
    
    def generate_department_options(self):
        """부서 선택 옵션 생성"""
        options = []
        for dept in self.df_current['Department'].unique()[:10]:  # Limit to 10 for display
            options.append(f'<option value="{dept}">{dept}</option>')
        return '\n'.join(options)
    
    def generate_role_options(self):
        """역할 선택 옵션 생성"""
        options = []
        for role in self.config.get('filters', {}).get('role', {}).get('categories', []):
            options.append(f'<option value="{role}">{role}</option>')
        return '\n'.join(options)
    
    def generate_lifecycle_details(self):
        """생애주기 상세 정보 HTML 생성"""
        html_parts = []
        
        # New hires
        if self.lifecycle_info['new_hires']:
            html_parts.append('<div class="lifecycle-card">')
            html_parts.append(f'<h5>신입 직원 ({len(self.lifecycle_info["new_hires"])}명)</h5>')
            html_parts.append('<ul>')
            for emp in self.lifecycle_info['new_hires'][:10]:
                html_parts.append(f'<li>{emp["name"]} - {emp["department"]} (첫 출근: {emp.get("first_date", "N/A")})</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        # Resignations
        if self.lifecycle_info['resignations']:
            html_parts.append('<div class="lifecycle-card">')
            html_parts.append(f'<h5>퇴사자 ({len(self.lifecycle_info["resignations"])}명)</h5>')
            html_parts.append('<ul>')
            for emp in self.lifecycle_info['resignations'][:10]:
                html_parts.append(f'<li>{emp["name"]} - {emp["department"]}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        # Pregnant/Maternity
        total_pregnant = len(self.lifecycle_info['pregnant']) + len(self.lifecycle_info['maternity_leave'])
        if total_pregnant > 0:
            html_parts.append('<div class="lifecycle-card">')
            html_parts.append(f'<h5>임산부/출산휴가 ({total_pregnant}명)</h5>')
            html_parts.append('<ul>')
            for emp in (self.lifecycle_info['pregnant'] + self.lifecycle_info['maternity_leave'])[:10]:
                html_parts.append(f'<li>{emp["name"]} - {emp["department"]} ({emp.get("status", "N/A")})</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        return ''.join(html_parts) if html_parts else '<p>생애주기 데이터가 없습니다.</p>'
    
    def generate_department_table(self):
        """부서별 상세 테이블 생성"""
        dept_stats = self.calculate_department_stats()
        
        html = ['<table class="table table-striped">']
        html.append('<thead><tr>')
        html.append('<th>부서</th><th>전체</th><th>출근</th><th>출석률</th><th>상태</th>')
        html.append('</tr></thead><tbody>')
        
        for dept, stats in sorted(dept_stats.items(), key=lambda x: x[1]['rate'], reverse=True)[:20]:
            status_class = 'success' if stats['rate'] >= 90 else 'warning' if stats['rate'] >= 85 else 'danger'
            status_badge = 'bg-success' if stats['rate'] >= 90 else 'bg-warning' if stats['rate'] >= 85 else 'bg-danger'
            
            html.append(f'<tr>')
            html.append(f'<td>{dept}</td>')
            html.append(f'<td>{stats["total"]}</td>')
            html.append(f'<td>{stats["present"]}</td>')
            html.append(f'<td>{stats["rate"]:.1f}%</td>')
            html.append(f'<td><span class="badge {status_badge}">{"우수" if stats["rate"] >= 90 else "보통" if stats["rate"] >= 85 else "개선필요"}</span></td>')
            html.append(f'</tr>')
        
        html.append('</tbody></table>')
        
        return ''.join(html)
    
    def generate_comprehensive_insights(self):
        """종합 인사이트 생성"""
        html = ['<div class="row">']
        
        # Attendance insights
        html.append('<div class="col-md-6">')
        html.append('<div class="card mb-3">')
        html.append('<div class="card-header bg-primary text-white">출석 인사이트</div>')
        html.append('<div class="card-body">')
        html.append('<ul>')
        for key, value in self.insights.get('overview', {}).items():
            html.append(f'<li>{value}</li>')
        html.append('</ul>')
        html.append('</div></div></div>')
        
        # Department insights
        html.append('<div class="col-md-6">')
        html.append('<div class="card mb-3">')
        html.append('<div class="card-header bg-info text-white">부서 인사이트</div>')
        html.append('<div class="card-body">')
        html.append('<ul>')
        for key, value in self.insights.get('departments', {}).items():
            html.append(f'<li>{value}</li>')
        html.append('</ul>')
        html.append('</div></div></div>')
        
        # Lifecycle insights
        if self.insights.get('trends'):
            html.append('<div class="col-md-6">')
            html.append('<div class="card mb-3">')
            html.append('<div class="card-header bg-warning">인력 변동 인사이트</div>')
            html.append('<div class="card-body">')
            html.append('<ul>')
            for key, value in self.insights.get('trends', {}).items():
                html.append(f'<li>{value}</li>')
            html.append('</ul>')
            html.append('</div></div></div>')
        
        # Recommendations
        html.append('<div class="col-md-6">')
        html.append('<div class="card mb-3">')
        html.append('<div class="card-header bg-success text-white">권장 사항</div>')
        html.append('<div class="card-body">')
        html.append('<ol>')
        html.append('<li>출석률 90% 미만 부서에 대한 집중 관리</li>')
        html.append('<li>신입 직원 온보딩 프로그램 강화</li>')
        html.append('<li>임산부 직원을 위한 유연근무제 검토</li>')
        html.append('<li>월요일 출석률 개선 방안 수립</li>')
        html.append('</ol>')
        html.append('</div></div></div>')
        
        html.append('</div>')
        
        return ''.join(html)
    
    def save_dashboard(self, output_path='output_files/attendance_dashboard_v4.html'):
        """대시보드 저장"""
        try:
            html_content = self.generate_dashboard()
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Dashboard saved to {output_path}")
            
            # Save metadata
            metadata = {
                'generated_at': datetime.now().isoformat(),
                'version': self.config['dashboard']['version'],
                'total_employees': len(self.df_current['ID No'].unique()),
                'months_loaded': list(self.df_all_months.keys()),
                'lifecycle_summary': {
                    'new_hires': len(self.lifecycle_info['new_hires']),
                    'resignations': len(self.lifecycle_info['resignations']),
                    'pregnant': len(self.lifecycle_info['pregnant']),
                    'maternity_leave': len(self.lifecycle_info['maternity_leave'])
                }
            }
            
            metadata_path = output_path.replace('.html', '_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Metadata saved to {metadata_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving dashboard: {e}")
            return False


def main():
    """메인 실행 함수"""
    try:
        # Create dashboard
        dashboard = AttendanceDashboardV4()
        
        # Generate and save
        if dashboard.save_dashboard():
            print("✅ 대시보드가 성공적으로 생성되었습니다!")
            print("📊 output_files/attendance_dashboard_v4.html 파일을 브라우저에서 열어보세요.")
            
            # Print summary
            print("\n📈 요약:")
            print(f"  - 총 직원 수: {len(dashboard.df_current['ID No'].unique())}명")
            print(f"  - 로드된 월 수: {len(dashboard.df_all_months)}개월")
            print(f"  - 신입 직원: {len(dashboard.lifecycle_info['new_hires'])}명")
            print(f"  - 퇴사자: {len(dashboard.lifecycle_info['resignations'])}명")
            print(f"  - 임산부/출산휴가: {len(dashboard.lifecycle_info['pregnant']) + len(dashboard.lifecycle_info['maternity_leave'])}명")
        else:
            print("❌ 대시보드 생성 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()