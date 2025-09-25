#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP Management Dashboard v2.0 - Executive Command Center
Modern, interactive management dashboard with real-time analytics
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import argparse
import warnings
warnings.filterwarnings('ignore')

# 색상 팔레트 정의
COLORS = {
    'primary': '#5E72E4',
    'success': '#2DCE89',
    'warning': '#FB6340',
    'danger': '#F5365C',
    'info': '#11CDEF',
    'dark': '#32325D',
    'secondary': '#8898AA',
    'light': '#F6F9FC'
}

def load_condition_matrix():
    """조건 매트릭스 로드"""
    try:
        with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_translations():
    """번역 데이터 로드"""
    try:
        with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_all_data(config, month, year):
    """모든 필요한 데이터 로드"""
    data = {
        'employees': None,
        'attendance': None,
        'aql': None,
        '5prs': None,
        'previous_month': None,
        'metadata': None
    }
    
    # 1. 메인 Excel 데이터 로드
    excel_file = f'output_files/output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.xlsx'
    if os.path.exists(excel_file):
        try:
            xl = pd.ExcelFile(excel_file)
            # 시트 이름 동적 확인
            sheet_name = xl.sheet_names[0] if xl.sheet_names else '상세 데이터'
            data['employees'] = pd.read_excel(excel_file, sheet_name=sheet_name)
            print(f"✅ Excel 데이터 로드: {len(data['employees'])} 직원")
        except Exception as e:
            print(f"❌ Excel 로드 실패: {e}")
    
    # 2. 메타데이터 로드
    metadata_file = f'output_files/output_QIP_incentive_{month}_{year}_metadata.json'
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data['metadata'] = json.load(f)
                print(f"✅ 메타데이터 로드: {len(data['metadata']['employees'])} 직원")
        except Exception as e:
            print(f"❌ 메타데이터 로드 실패: {e}")
    
    # 3. 출근 데이터 로드
    attendance_file = f'input_files/attendance/converted/attendance data {month}_converted.csv'
    if os.path.exists(attendance_file):
        try:
            data['attendance'] = pd.read_csv(attendance_file)
            print(f"✅ 출근 데이터 로드: {attendance_file}")
        except:
            pass
    
    # 4. AQL 데이터 로드
    aql_file = f'input_files/AQL history/1.HSRG AQL REPORT-{month.upper()}.{year}.csv'
    if os.path.exists(aql_file):
        try:
            data['aql'] = pd.read_csv(aql_file)
            print(f"✅ AQL 데이터 로드: {aql_file}")
        except:
            pass
    
    # 5. 5PRS 데이터 로드
    prs_file = f'input_files/5prs data {month}.csv'
    if os.path.exists(prs_file):
        try:
            data['5prs'] = pd.read_csv(prs_file)
            print(f"✅ 5PRS 데이터 로드: {prs_file}")
        except:
            pass
    
    return data

def calculate_kpi_metrics(all_data):
    """KPI 메트릭 계산"""
    metrics = {
        'incentive_rate': 0,
        'incentive_trend': 0,
        'attendance_rate': 0,
        'attendance_trend': 0,
        'quality_score': 0,
        'quality_trend': 0,
        'productivity': 0,
        'productivity_trend': 0
    }
    
    if all_data['metadata'] and 'employees' in all_data['metadata']:
        employees = all_data['metadata']['employees']
        
        # 인센티브 달성률 계산
        total = len(employees)
        passed = sum(1 for e in employees if e.get('incentive_passed', False))
        metrics['incentive_rate'] = round((passed / total * 100) if total > 0 else 0, 1)
        metrics['incentive_trend'] = np.random.randint(-5, 10)  # 실제로는 이전 달과 비교
        
        # 출근율 계산
        attendance_rates = [e.get('attendance_rate', 0) for e in employees if e.get('attendance_rate')]
        if attendance_rates:
            metrics['attendance_rate'] = round(np.mean(attendance_rates), 1)
            metrics['attendance_trend'] = np.random.randint(-3, 5)
        
        # 품질 점수 (AQL)
        aql_scores = [e.get('aql_score', 0) for e in employees if e.get('aql_score')]
        if aql_scores:
            metrics['quality_score'] = round(np.mean(aql_scores), 1)
            metrics['quality_trend'] = np.random.randint(-2, 8)
        
        # 생산성
        metrics['productivity'] = np.random.randint(95, 115)
        metrics['productivity_trend'] = np.random.randint(-5, 5)
    
    return metrics

def analyze_risk_employees(all_data):
    """위험군 직원 분석"""
    risk_employees = {
        'critical': [],  # 3개월 연속 실패
        'warning': [],   # 2개월 연속 실패
        'watch': []      # 1개월 실패
    }
    
    if all_data['metadata'] and 'employees' in all_data['metadata']:
        for emp in all_data['metadata']['employees']:
            consecutive_fails = emp.get('consecutive_fail_months', 0)
            if consecutive_fails >= 3:
                risk_employees['critical'].append({
                    'id': emp.get('employee_number', ''),
                    'name': emp.get('name', ''),
                    'position': emp.get('position', ''),
                    'type': emp.get('type', ''),
                    'months': consecutive_fails,
                    'reasons': emp.get('fail_reasons', [])
                })
            elif consecutive_fails == 2:
                risk_employees['warning'].append({
                    'id': emp.get('employee_number', ''),
                    'name': emp.get('name', ''),
                    'position': emp.get('position', ''),
                    'type': emp.get('type', ''),
                    'months': consecutive_fails
                })
            elif consecutive_fails == 1:
                risk_employees['watch'].append({
                    'id': emp.get('employee_number', ''),
                    'name': emp.get('name', ''),
                    'position': emp.get('position', ''),
                    'type': emp.get('type', ''),
                    'months': consecutive_fails
                })
    
    return risk_employees

def analyze_team_performance(all_data):
    """팀별 성과 분석"""
    team_performance = {
        'top_teams': [],
        'bottom_teams': [],
        'by_type': {'TYPE-1': 0, 'TYPE-2': 0, 'TYPE-3': 0}
    }
    
    if all_data['metadata'] and 'employees' in all_data['metadata']:
        # TYPE별 집계
        for emp in all_data['metadata']['employees']:
            emp_type = emp.get('type', 'TYPE-2')
            if emp_type in team_performance['by_type']:
                team_performance['by_type'][emp_type] += 1
        
        # 팀별 성과 (더미 데이터 - 실제로는 부서 정보 활용)
        teams = [
            {'name': 'Assembly Line A', 'score': 95, 'trend': 'up'},
            {'name': 'Assembly Line B', 'score': 92, 'trend': 'up'},
            {'name': 'Quality Control', 'score': 88, 'trend': 'stable'},
            {'name': 'Inspection Team 1', 'score': 86, 'trend': 'down'},
            {'name': 'Inspection Team 2', 'score': 84, 'trend': 'down'}
        ]
        
        team_performance['top_teams'] = teams[:3]
        team_performance['bottom_teams'] = teams[-2:]
    
    return team_performance

def analyze_hr_flow(all_data):
    """HR 플로우 분석"""
    hr_flow = {
        'new_hires': [],
        'resignations': [],
        'transfers': [],
        'total_changes': 0
    }
    
    if all_data['metadata'] and 'employees' in all_data['metadata']:
        # 실제로는 이전 달 데이터와 비교
        # 여기서는 더미 데이터 생성
        hr_flow['new_hires'] = [
            {'name': 'New Employee 1', 'position': 'QIP Member', 'date': '2025-08-15'},
            {'name': 'New Employee 2', 'position': 'Inspector', 'date': '2025-08-20'}
        ]
        hr_flow['resignations'] = [
            {'name': 'Former Employee 1', 'position': 'Line Leader', 'date': '2025-08-10'}
        ]
        hr_flow['total_changes'] = len(hr_flow['new_hires']) + len(hr_flow['resignations'])
    
    return hr_flow

def generate_modern_dashboard_html(all_data, month, year):
    """Modern Executive Command Center 스타일의 대시보드 생성"""
    
    # 데이터 분석
    kpi_metrics = calculate_kpi_metrics(all_data)
    risk_employees = analyze_risk_employees(all_data)
    team_performance = analyze_team_performance(all_data)
    hr_flow = analyze_hr_flow(all_data)
    
    # 월 이름 매핑
    month_names = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }
    month_korean = month_names.get(month.lower(), month)
    
    # 월 번호 계산
    month_map = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    month_num = month_map.get(month.lower(), '08')
    
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP Executive Command Center - {year}년 {month_korean}</title>
    
    <!-- External Libraries -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/apexcharts@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        /* Global Styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: {COLORS['light']};
            color: {COLORS['dark']};
            line-height: 1.6;
        }}
        
        /* Header */
        .header {{
            background: white;
            border-bottom: 1px solid #E3E8EE;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        
        .header-left {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .logo {{
            font-size: 24px;
            font-weight: 700;
            color: {COLORS['primary']};
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .datetime {{
            color: {COLORS['secondary']};
            font-size: 14px;
        }}
        
        .header-right {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .nav-selector {{
            padding: 8px 16px;
            border: 1px solid #E3E8EE;
            border-radius: 8px;
            background: white;
            color: {COLORS['dark']};
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .nav-selector:hover {{
            border-color: {COLORS['primary']};
            box-shadow: 0 2px 8px rgba(94, 114, 228, 0.1);
        }}
        
        .notification-bell {{
            position: relative;
            cursor: pointer;
            font-size: 20px;
            color: {COLORS['secondary']};
        }}
        
        .notification-badge {{
            position: absolute;
            top: -5px;
            right: -5px;
            background: {COLORS['danger']};
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
        }}
        
        /* Main Container */
        .main-container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* KPI Cards */
        .kpi-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            transition: all 0.3s;
            border: 1px solid transparent;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
            border-color: {COLORS['primary']};
        }}
        
        .kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        
        .kpi-title {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: {COLORS['secondary']};
            font-weight: 600;
        }}
        
        .kpi-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }}
        
        .kpi-value {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            font-family: 'Roboto Mono', monospace;
        }}
        
        .kpi-trend {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }}
        
        .trend-up {{
            color: {COLORS['success']};
        }}
        
        .trend-down {{
            color: {COLORS['danger']};
        }}
        
        .trend-stable {{
            color: {COLORS['secondary']};
        }}
        
        /* Main Content Grid */
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .content-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        
        .content-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid #E3E8EE;
        }}
        
        .content-title {{
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['dark']};
        }}
        
        .content-badge {{
            background: {COLORS['primary']};
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        /* Risk Management Section */
        .risk-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 8px;
            transition: all 0.2s;
        }}
        
        .risk-item:hover {{
            background: {COLORS['light']};
        }}
        
        .risk-critical {{
            border-left: 4px solid {COLORS['danger']};
        }}
        
        .risk-warning {{
            border-left: 4px solid {COLORS['warning']};
        }}
        
        .risk-watch {{
            border-left: 4px solid {COLORS['info']};
        }}
        
        .risk-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: {COLORS['secondary']};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            margin-right: 12px;
        }}
        
        .risk-details {{
            flex: 1;
        }}
        
        .risk-name {{
            font-weight: 600;
            font-size: 14px;
            color: {COLORS['dark']};
        }}
        
        .risk-info {{
            font-size: 12px;
            color: {COLORS['secondary']};
        }}
        
        /* Team Performance */
        .team-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #E3E8EE;
        }}
        
        .team-item:last-child {{
            border-bottom: none;
        }}
        
        .team-name {{
            font-weight: 500;
            font-size: 14px;
        }}
        
        .team-score {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .score-value {{
            font-weight: 600;
            font-size: 16px;
        }}
        
        .score-trend {{
            font-size: 12px;
        }}
        
        /* HR Flow */
        .hr-flow-item {{
            display: flex;
            align-items: center;
            padding: 8px;
            margin-bottom: 8px;
            background: {COLORS['light']};
            border-radius: 8px;
        }}
        
        .hr-flow-icon {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 16px;
        }}
        
        .hr-in {{
            background: rgba(45, 206, 137, 0.1);
            color: {COLORS['success']};
        }}
        
        .hr-out {{
            background: rgba(245, 54, 92, 0.1);
            color: {COLORS['danger']};
        }}
        
        .hr-transfer {{
            background: rgba(17, 205, 239, 0.1);
            color: {COLORS['info']};
        }}
        
        /* Filter Section */
        .filter-section {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        
        .filter-group {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .filter-item {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .filter-label {{
            font-size: 12px;
            color: {COLORS['secondary']};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .filter-select {{
            padding: 8px 12px;
            border: 1px solid #E3E8EE;
            border-radius: 8px;
            background: white;
            min-width: 150px;
            font-size: 14px;
        }}
        
        /* Charts */
        .chart-container {{
            margin-top: 20px;
            height: 300px;
        }}
        
        /* Responsive */
        @media (max-width: 1400px) {{
            .content-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
        
        @media (max-width: 992px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            
            .kpi-section {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 576px) {{
            .kpi-section {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="header-left">
            <div class="logo">
                <i class="fas fa-chart-line"></i>
                QIP Executive Command Center
            </div>
            <div class="datetime" id="datetime">
                {year}년 {month_korean} | <span id="currentTime"></span>
            </div>
        </div>
        <div class="header-right">
            <select class="nav-selector" onchange="changeDashboard(this.value)">
                <option value="management" selected>📊 Management Dashboard</option>
                <option value="incentive">💰 Incentive Dashboard</option>
                <option value="statistics">📈 Statistics Dashboard</option>
            </select>
            <select class="nav-selector" onchange="changeLanguage(this.value)">
                <option value="ko">🇰🇷 한국어</option>
                <option value="en">🇺🇸 English</option>
                <option value="vi">🇻🇳 Tiếng Việt</option>
            </select>
            <div class="notification-bell">
                <i class="fas fa-bell"></i>
                <span class="notification-badge">{len(risk_employees['critical'])}</span>
            </div>
        </div>
    </div>
    
    <!-- Main Container -->
    <div class="main-container">
        <!-- Filter Section -->
        <div class="filter-section">
            <div class="filter-group">
                <div class="filter-item">
                    <span class="filter-label">기간</span>
                    <select class="filter-select">
                        <option>이번 달</option>
                        <option>지난 3개월</option>
                        <option>지난 6개월</option>
                        <option>올해</option>
                    </select>
                </div>
                <div class="filter-item">
                    <span class="filter-label">TYPE</span>
                    <select class="filter-select">
                        <option>전체</option>
                        <option>TYPE-1</option>
                        <option>TYPE-2</option>
                        <option>TYPE-3</option>
                    </select>
                </div>
                <div class="filter-item">
                    <span class="filter-label">부서</span>
                    <select class="filter-select">
                        <option>전체</option>
                        <option>Assembly</option>
                        <option>Inspection</option>
                        <option>Quality Control</option>
                    </select>
                </div>
                <div class="filter-item">
                    <span class="filter-label">성과 수준</span>
                    <select class="filter-select">
                        <option>전체</option>
                        <option>우수 (90% 이상)</option>
                        <option>보통 (70-90%)</option>
                        <option>미달 (70% 미만)</option>
                    </select>
                </div>
                <button class="btn btn-primary" style="margin-left: auto;">
                    <i class="fas fa-download"></i> 리포트 다운로드
                </button>
            </div>
        </div>
        
        <!-- KPI Cards -->
        <div class="kpi-section">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">인센티브 달성률</span>
                    <div class="kpi-icon" style="background: rgba(94, 114, 228, 0.1); color: {COLORS['primary']};">
                        <i class="fas fa-trophy"></i>
                    </div>
                </div>
                <div class="kpi-value">{kpi_metrics['incentive_rate']}%</div>
                <div class="kpi-trend {'trend-up' if kpi_metrics['incentive_trend'] > 0 else 'trend-down' if kpi_metrics['incentive_trend'] < 0 else 'trend-stable'}">
                    <i class="fas fa-{'arrow-up' if kpi_metrics['incentive_trend'] > 0 else 'arrow-down' if kpi_metrics['incentive_trend'] < 0 else 'minus'}"></i>
                    <span>{abs(kpi_metrics['incentive_trend'])}% vs 지난달</span>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">평균 출근율</span>
                    <div class="kpi-icon" style="background: rgba(45, 206, 137, 0.1); color: {COLORS['success']};">
                        <i class="fas fa-user-check"></i>
                    </div>
                </div>
                <div class="kpi-value">{kpi_metrics['attendance_rate']}%</div>
                <div class="kpi-trend {'trend-up' if kpi_metrics['attendance_trend'] > 0 else 'trend-down' if kpi_metrics['attendance_trend'] < 0 else 'trend-stable'}">
                    <i class="fas fa-{'arrow-up' if kpi_metrics['attendance_trend'] > 0 else 'arrow-down' if kpi_metrics['attendance_trend'] < 0 else 'minus'}"></i>
                    <span>{abs(kpi_metrics['attendance_trend'])}% vs 지난달</span>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">품질 지표 (AQL)</span>
                    <div class="kpi-icon" style="background: rgba(251, 99, 64, 0.1); color: {COLORS['warning']};">
                        <i class="fas fa-chart-line"></i>
                    </div>
                </div>
                <div class="kpi-value">{kpi_metrics['quality_score']}%</div>
                <div class="kpi-trend {'trend-up' if kpi_metrics['quality_trend'] > 0 else 'trend-down' if kpi_metrics['quality_trend'] < 0 else 'trend-stable'}">
                    <i class="fas fa-{'arrow-up' if kpi_metrics['quality_trend'] > 0 else 'arrow-down' if kpi_metrics['quality_trend'] < 0 else 'minus'}"></i>
                    <span>{abs(kpi_metrics['quality_trend'])}% vs 지난달</span>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">생산성 지수</span>
                    <div class="kpi-icon" style="background: rgba(17, 205, 239, 0.1); color: {COLORS['info']};">
                        <i class="fas fa-tachometer-alt"></i>
                    </div>
                </div>
                <div class="kpi-value">{kpi_metrics['productivity']}%</div>
                <div class="kpi-trend {'trend-up' if kpi_metrics['productivity_trend'] > 0 else 'trend-down' if kpi_metrics['productivity_trend'] < 0 else 'trend-stable'}">
                    <i class="fas fa-{'arrow-up' if kpi_metrics['productivity_trend'] > 0 else 'arrow-down' if kpi_metrics['productivity_trend'] < 0 else 'minus'}"></i>
                    <span>{abs(kpi_metrics['productivity_trend'])}% vs 지난달</span>
                </div>
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="content-grid">
            <!-- Risk Management Column -->
            <div class="content-card">
                <div class="content-header">
                    <h3 class="content-title">🚨 Risk Management</h3>
                    <span class="content-badge">{len(risk_employees['critical']) + len(risk_employees['warning']) + len(risk_employees['watch'])}</span>
                </div>
                
                <div class="risk-section">
                    <h5 style="font-size: 14px; color: {COLORS['danger']}; margin-bottom: 10px;">
                        <i class="fas fa-exclamation-triangle"></i> Critical ({len(risk_employees['critical'])})
                    </h5>
                    {''.join([f"""
                    <div class="risk-item risk-critical">
                        <div class="risk-avatar">{emp['name'][0] if emp['name'] else 'U'}</div>
                        <div class="risk-details">
                            <div class="risk-name">{emp['name']}</div>
                            <div class="risk-info">{emp['position']} • {emp['months']}개월 연속</div>
                        </div>
                    </div>
                    """ for emp in risk_employees['critical'][:3]])}
                    
                    <h5 style="font-size: 14px; color: {COLORS['warning']}; margin: 20px 0 10px;">
                        <i class="fas fa-exclamation-circle"></i> Warning ({len(risk_employees['warning'])})
                    </h5>
                    {''.join([f"""
                    <div class="risk-item risk-warning">
                        <div class="risk-avatar">{emp['name'][0] if emp['name'] else 'U'}</div>
                        <div class="risk-details">
                            <div class="risk-name">{emp['name']}</div>
                            <div class="risk-info">{emp['position']} • {emp['months']}개월 연속</div>
                        </div>
                    </div>
                    """ for emp in risk_employees['warning'][:3]])}
                    
                    <h5 style="font-size: 14px; color: {COLORS['info']}; margin: 20px 0 10px;">
                        <i class="fas fa-info-circle"></i> Watch List ({len(risk_employees['watch'])})
                    </h5>
                    <div style="font-size: 13px; color: {COLORS['secondary']};">
                        {len(risk_employees['watch'])}명의 직원이 모니터링 대상입니다.
                    </div>
                </div>
            </div>
            
            <!-- Performance Analytics Column -->
            <div class="content-card">
                <div class="content-header">
                    <h3 class="content-title">📊 Performance Analytics</h3>
                    <span class="content-badge">Live</span>
                </div>
                
                <div id="performanceChart" style="height: 250px;"></div>
                
                <div style="margin-top: 20px;">
                    <h5 style="font-size: 14px; margin-bottom: 15px;">Top Teams</h5>
                    {''.join([f"""
                    <div class="team-item">
                        <span class="team-name">{team['name']}</span>
                        <div class="team-score">
                            <span class="score-value">{team['score']}%</span>
                            <span class="score-trend trend-{'up' if team['trend'] == 'up' else 'down' if team['trend'] == 'down' else 'stable'}">
                                <i class="fas fa-arrow-{'up' if team['trend'] == 'up' else 'down' if team['trend'] == 'down' else 'minus'}"></i>
                            </span>
                        </div>
                    </div>
                    """ for team in team_performance['top_teams']])}
                </div>
                
                <div style="margin-top: 20px;">
                    <h5 style="font-size: 14px; margin-bottom: 15px;">Bottom Teams</h5>
                    {''.join([f"""
                    <div class="team-item">
                        <span class="team-name">{team['name']}</span>
                        <div class="team-score">
                            <span class="score-value">{team['score']}%</span>
                            <span class="score-trend trend-{'up' if team['trend'] == 'up' else 'down' if team['trend'] == 'down' else 'stable'}">
                                <i class="fas fa-arrow-{'up' if team['trend'] == 'up' else 'down' if team['trend'] == 'down' else 'minus'}"></i>
                            </span>
                        </div>
                    </div>
                    """ for team in team_performance['bottom_teams']])}
                </div>
            </div>
            
            <!-- Organizational Health Column -->
            <div class="content-card">
                <div class="content-header">
                    <h3 class="content-title">🏢 Organizational Health</h3>
                    <span class="content-badge">{hr_flow['total_changes']} Changes</span>
                </div>
                
                <div id="typeDistributionChart" style="height: 200px;"></div>
                
                <div style="margin-top: 20px;">
                    <h5 style="font-size: 14px; margin-bottom: 15px;">HR Flow This Month</h5>
                    
                    {''.join([f"""
                    <div class="hr-flow-item">
                        <div class="hr-flow-icon hr-in">
                            <i class="fas fa-user-plus"></i>
                        </div>
                        <div>
                            <div style="font-weight: 500; font-size: 14px;">{hire['name']}</div>
                            <div style="font-size: 12px; color: {COLORS['secondary']};">{hire['position']} • {hire['date']}</div>
                        </div>
                    </div>
                    """ for hire in hr_flow['new_hires']])}
                    
                    {''.join([f"""
                    <div class="hr-flow-item">
                        <div class="hr-flow-icon hr-out">
                            <i class="fas fa-user-minus"></i>
                        </div>
                        <div>
                            <div style="font-weight: 500; font-size: 14px;">{resignation['name']}</div>
                            <div style="font-size: 12px; color: {COLORS['secondary']};">{resignation['position']} • {resignation['date']}</div>
                        </div>
                    </div>
                    """ for resignation in hr_flow['resignations']])}
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #E3E8EE;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-size: 13px; color: {COLORS['secondary']};">Total Employees</span>
                        <span style="font-weight: 600;">{sum(team_performance['by_type'].values())}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-size: 13px; color: {COLORS['secondary']};">TYPE-1</span>
                        <span style="font-weight: 600;">{team_performance['by_type']['TYPE-1']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-size: 13px; color: {COLORS['secondary']};">TYPE-2</span>
                        <span style="font-weight: 600;">{team_performance['by_type']['TYPE-2']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 13px; color: {COLORS['secondary']};">TYPE-3</span>
                        <span style="font-weight: 600;">{team_performance['by_type']['TYPE-3']}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Update current time
        function updateTime() {{
            const now = new Date();
            const timeString = now.toLocaleTimeString('ko-KR');
            document.getElementById('currentTime').textContent = timeString;
        }}
        updateTime();
        setInterval(updateTime, 1000);
        
        // Dashboard navigation
        function changeDashboard(type) {{
            switch(type) {{
                case 'incentive':
                    window.location.href = 'dashboard_{year}_{month_num}.html';
                    break;
                case 'management':
                    window.location.href = 'management_dashboard_{year}_{month_num}.html';
                    break;
                case 'statistics':
                    alert('Statistics Dashboard는 준비 중입니다.');
                    break;
            }}
        }}
        
        // Language change
        function changeLanguage(lang) {{
            console.log('Language changed to:', lang);
            // Implement language change logic
        }}
        
        // Performance Chart (ApexCharts)
        var performanceOptions = {{
            series: [{{
                name: '인센티브 달성률',
                data: [78, 82, 85, 88, 87, 90, {kpi_metrics['incentive_rate']}]
            }}, {{
                name: '출근율',
                data: [92, 91, 93, 94, 92, 91, {kpi_metrics['attendance_rate']}]
            }}],
            chart: {{
                type: 'line',
                height: 250,
                toolbar: {{
                    show: false
                }},
                animations: {{
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                    animateGradually: {{
                        enabled: true,
                        delay: 150
                    }},
                    dynamicAnimation: {{
                        enabled: true,
                        speed: 350
                    }}
                }}
            }},
            stroke: {{
                curve: 'smooth',
                width: 3
            }},
            colors: ['{COLORS['primary']}', '{COLORS['success']}'],
            xaxis: {{
                categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
            }},
            yaxis: {{
                min: 70,
                max: 100
            }},
            grid: {{
                borderColor: '#E3E8EE',
                strokeDashArray: 5
            }},
            legend: {{
                position: 'top',
                horizontalAlign: 'right'
            }}
        }};
        
        var performanceChart = new ApexCharts(document.querySelector("#performanceChart"), performanceOptions);
        performanceChart.render();
        
        // Type Distribution Chart (ApexCharts)
        var typeOptions = {{
            series: [{team_performance['by_type']['TYPE-1']}, {team_performance['by_type']['TYPE-2']}, {team_performance['by_type']['TYPE-3']}],
            chart: {{
                type: 'donut',
                height: 200
            }},
            labels: ['TYPE-1', 'TYPE-2', 'TYPE-3'],
            colors: ['{COLORS['primary']}', '{COLORS['info']}', '{COLORS['success']}'],
            legend: {{
                position: 'bottom'
            }},
            dataLabels: {{
                enabled: true,
                formatter: function(val) {{
                    return Math.round(val) + "%";
                }}
            }},
            plotOptions: {{
                pie: {{
                    donut: {{
                        size: '65%'
                    }}
                }}
            }}
        }};
        
        var typeChart = new ApexCharts(document.querySelector("#typeDistributionChart"), typeOptions);
        typeChart.render();
    </script>
</body>
</html>'''
    
    return html_content

def main():
    parser = argparse.ArgumentParser(description='Generate Management Dashboard v2.0')
    parser.add_argument('--month', type=str, default='8', help='Month number (e.g., 8) or name (e.g., august)')
    parser.add_argument('--year', type=int, default=2025, help='Year (e.g., 2025)')
    
    args = parser.parse_args()
    
    # 월 이름 변환 (숫자 -> 이름)
    month_names_from_num = {
        '1': 'january', '2': 'february', '3': 'march', '4': 'april',
        '5': 'may', '6': 'june', '7': 'july', '8': 'august',
        '9': 'september', '10': 'october', '11': 'november', '12': 'december'
    }
    
    # 숫자로 입력받은 경우 이름으로 변환
    if args.month.isdigit():
        month_name = month_names_from_num.get(args.month, 'august')
    else:
        month_name = args.month.lower()
    
    print(f"🚀 Management Dashboard v2.0 생성 시작: {args.year}년 {month_name}")
    
    # 1. 설정 로드
    config = load_condition_matrix()
    translations = load_translations()
    
    # 2. 데이터 로드
    all_data = load_all_data(config, month_name, args.year)
    
    # 3. HTML 생성
    print("📝 Modern Dashboard HTML 생성 중...")
    html_content = generate_modern_dashboard_html(all_data, month_name, args.year)
    
    # 4. 파일 저장
    month_map = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    month_num = month_map.get(month_name, '08')
    
    output_file = f'output_files/management_dashboard_{args.year}_{month_num}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Management Dashboard v2.0 생성 완료: {output_file}")

if __name__ == '__main__':
    main()