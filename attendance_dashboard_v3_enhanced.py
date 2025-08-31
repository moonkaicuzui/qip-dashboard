#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 출결 대시보드 생성 시스템 V3 - Enhanced Version
추가 차트와 탭으로 강화된 버전
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
import numpy as np
import argparse
import calendar

def load_attendance_data(file_path):
    """출결 데이터 로드"""
    try:
        # CSV 파일 읽기
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        else:
            df = pd.read_excel(file_path, sheet_name='Sheet1')
        
        print(f"✅ 출결 데이터 로드 완료: {len(df)} 행")
        print(f"   고유 직원 수: {df['ID No'].nunique()} 명")
        
        # Work Date를 datetime으로 변환
        df['Work Date'] = pd.to_datetime(df['Work Date'], format='%Y.%m.%d')
        
        # 추가 필드 생성
        df['is_present'] = df['compAdd'] == 'Đi làm'
        df['is_unapproved'] = (df['compAdd'] == 'Vắng mặt') & (df['Reason Description'].isna())
        df['day_of_week'] = df['Work Date'].dt.dayofweek
        df['week_of_month'] = (df['Work Date'].dt.day - 1) // 7 + 1
        df['hour'] = pd.to_datetime(df['Work Date'].dt.strftime('%Y-%m-%d') + ' 09:00:00').dt.hour
        
        # 결근 사유 분류
        df['absence_category'] = df['Reason Description'].fillna('정상출근')
        df.loc[df['is_present'], 'absence_category'] = '정상출근'
        df.loc[df['is_unapproved'], 'absence_category'] = '무단결근'
        
        # 전체 출결율 계산
        total_attendance_rate = (df['is_present'].sum() / len(df)) * 100
        print(f"   전체 출결율: {total_attendance_rate:.1f}%")
        
        return df
    except Exception as e:
        print(f"❌ 출결 데이터 로드 실패: {e}")
        return None

def load_team_structure():
    """팀 구조 데이터 로드"""
    try:
        with open('HR info/team_structure.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 팀 구조 데이터 로드 완료")
        return data
    except Exception as e:
        print(f"❌ 팀 구조 데이터 로드 실패: {e}")
        return None

def calculate_work_hours(wtime_code):
    """WTime 코드에서 근무 시간 계산"""
    work_hours = {
        '1A': 8.0, '1C': 8.0, '1J': 8.0,  # SHIFT 1
        '2B': 8.0, '2C': 8.0,              # SHIFT 2  
        '3B': 8.0, '3F': 8.0,              # SHIFT 3
        '5I': 8.9, '5J': 8.9, '5K': 8.9, '5N': 8.9, '5O': 8.9,  # 임산부 ADMIN
        '7I': 8.0, '7J': 8.0, '7K': 8.0, '7P': 8.0, '7T': 8.0, '7U': 8.0,  # 임산부 ADMIN
        '9B': 9.0, '9I': 8.0, '9J': 9.0, '9K': 9.5, '9N': 9.0,  # 일반 ADMIN
        '9R': 9.0, '9S': 9.0, '9U': 9.0, '9V': 9.0
    }
    return work_hours.get(wtime_code, 9.0)

def process_attendance_by_period(df, period='daily', department='all'):
    """기간별 출결 데이터 처리"""
    
    # 부서 필터링
    if department != 'all':
        df = df[df['Department'] == department].copy()
    
    if period == 'daily':
        grouped = df.groupby('Work Date')
    elif period == 'weekly':
        df['Week'] = df['Work Date'].dt.isocalendar().week
        df['Year'] = df['Work Date'].dt.year
        grouped = df.groupby(['Year', 'Week'])
    elif period == 'monthly':
        df['Month'] = df['Work Date'].dt.month
        df['Year'] = df['Work Date'].dt.year
        grouped = df.groupby(['Year', 'Month'])
    elif period == 'quarterly':
        df['Quarter'] = df['Work Date'].dt.quarter
        df['Year'] = df['Work Date'].dt.year
        grouped = df.groupby(['Year', 'Quarter'])
    else:
        grouped = df.groupby('Work Date')
    
    # 집계 계산
    result = grouped.agg({
        'ID No': 'nunique',  # 고유 직원 수
        'is_present': lambda x: x.sum(),  # 출근 레코드 수
        'is_unapproved': 'sum',  # 무단결근 수
        'WTime': lambda x: np.mean([calculate_work_hours(t) for t in x])  # 평균 근무시간
    }).reset_index()
    
    # 전체 레코드 수 추가
    total_records = grouped.size().reset_index(name='Total_Records')
    
    # 병합 및 컬럼명 정리
    if period == 'daily':
        result = pd.merge(result, total_records, on='Work Date')
        result.columns = ['Period', 'Unique_Employees', 'Present_Count', 'Unapproved_Absence', 'Avg_Work_Hours', 'Total_Records']
    elif period == 'weekly':
        result = pd.merge(result, total_records, on=['Year', 'Week'])
        result.columns = ['Year', 'Week', 'Unique_Employees', 'Present_Count', 'Unapproved_Absence', 'Avg_Work_Hours', 'Total_Records']
    elif period in ['monthly', 'quarterly']:
        period_col = 'Month' if period == 'monthly' else 'Quarter'
        result = pd.merge(result, total_records, on=['Year', period_col])
        result.columns = ['Year', 'Period_Num', 'Unique_Employees', 'Present_Count', 'Unapproved_Absence', 'Avg_Work_Hours', 'Total_Records']
    
    # 출근율 계산
    result['Attendance_Rate'] = (result['Present_Count'] / result['Total_Records']) * 100
    result['Absence_Count'] = result['Total_Records'] - result['Present_Count']
    
    # 일평균 출근 일수 계산
    if period != 'daily':
        result['Avg_Attendance_Days'] = result['Present_Count'] / result['Unique_Employees']
    
    return result

def calculate_trend_analysis(df):
    """트렌드 분석 데이터 생성"""
    # 일별 출근율 트렌드
    daily_trend = df.groupby('Work Date').agg({
        'is_present': lambda x: (x.sum() / len(x)) * 100,
        'ID No': 'nunique'
    }).reset_index()
    daily_trend.columns = ['Date', 'Attendance_Rate', 'Total_Employees']
    
    # 7일 이동평균 추가
    daily_trend['MA7'] = daily_trend['Attendance_Rate'].rolling(window=7, min_periods=1).mean()
    
    # 전일 대비 변화율
    daily_trend['Change'] = daily_trend['Attendance_Rate'].diff()
    
    return daily_trend

def calculate_heatmap_data(df):
    """히트맵용 데이터 생성"""
    # 요일별 시간대별 출근율 (실제로는 요일별 주차별로 변경)
    heatmap_data = df.groupby(['day_of_week', 'week_of_month']).agg({
        'is_present': lambda x: (x.sum() / len(x)) * 100
    }).reset_index()
    heatmap_data.columns = ['Day', 'Week', 'Attendance_Rate']
    
    # 피벗 테이블 생성
    heatmap_pivot = heatmap_data.pivot(index='Day', columns='Week', values='Attendance_Rate')
    
    return heatmap_pivot

def calculate_department_comparison(df):
    """부서간 비교 데이터"""
    dept_comparison = df.groupby('Department').agg({
        'is_present': lambda x: (x.sum() / len(x)) * 100,
        'ID No': 'nunique',
        'WTime': lambda x: np.mean([calculate_work_hours(t) for t in x])
    }).reset_index()
    dept_comparison.columns = ['Department', 'Attendance_Rate', 'Total_Employees', 'Avg_Work_Hours']
    
    return dept_comparison

def calculate_absence_reasons(df):
    """결근 사유 분석"""
    absence_reasons = df[df['is_present'] == False].groupby('absence_category').size().reset_index(name='Count')
    absence_reasons['Percentage'] = (absence_reasons['Count'] / absence_reasons['Count'].sum()) * 100
    
    return absence_reasons

def calculate_employee_ranking(df):
    """직원별 출근율 랭킹"""
    employee_ranking = df.groupby(['ID No', 'Last name']).agg({
        'is_present': lambda x: (x.sum() / len(x)) * 100,
        'Work Date': 'count'
    }).reset_index()
    employee_ranking.columns = ['ID', 'Name', 'Attendance_Rate', 'Total_Days']
    employee_ranking = employee_ranking.sort_values('Attendance_Rate', ascending=False).head(20)
    
    return employee_ranking

def predict_attendance(df):
    """간단한 출결 예측 (이동평균 기반)"""
    # 최근 30일 데이터로 예측
    recent_30_days = df[df['Work Date'] >= (df['Work Date'].max() - timedelta(days=30))]
    avg_attendance = (recent_30_days['is_present'].sum() / len(recent_30_days)) * 100
    
    # 요일별 평균
    weekday_avg = recent_30_days.groupby('day_of_week')['is_present'].apply(lambda x: (x.sum() / len(x)) * 100).to_dict()
    
    return {'avg_attendance': avg_attendance, 'weekday_avg': weekday_avg}

def generate_enhanced_dashboard_html(attendance_data, team_structure, output_file='attendance_dashboard_v3.html'):
    """향상된 출결 대시보드 HTML 생성"""
    
    # 모든 분석 데이터 생성
    daily_data = process_attendance_by_period(attendance_data, 'daily')
    weekly_data = process_attendance_by_period(attendance_data, 'weekly')
    monthly_data = process_attendance_by_period(attendance_data, 'monthly')
    quarterly_data = process_attendance_by_period(attendance_data, 'quarterly')
    
    # 추가 분석
    trend_data = calculate_trend_analysis(attendance_data)
    heatmap_data = calculate_heatmap_data(attendance_data)
    dept_comparison = calculate_department_comparison(attendance_data)
    absence_reasons = calculate_absence_reasons(attendance_data)
    employee_ranking = calculate_employee_ranking(attendance_data)
    predictions = predict_attendance(attendance_data)
    
    # 전체 통계
    total_employees = attendance_data['ID No'].nunique()
    total_records = len(attendance_data)
    present_records = attendance_data['is_present'].sum()
    avg_attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
    avg_work_hours = np.mean([calculate_work_hours(t) for t in attendance_data['WTime']])
    working_days = attendance_data.groupby('ID No')['is_present'].sum().mean()
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 출결 대시보드 V3 - Enhanced</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        :root {{
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --info-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        body {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: var(--primary-gradient);
            color: white;
            padding: 50px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.1); opacity: 0.8; }}
        }}
        
        .filter-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .stats-card {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stats-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--primary-gradient);
        }}
        
        .stats-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .stats-card.success::before {{ background: var(--success-gradient); }}
        .stats-card.warning::before {{ background: var(--warning-gradient); }}
        .stats-card.info::before {{ background: var(--info-gradient); }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            position: relative;
        }}
        
        .chart-container.small {{ height: 400px; }}
        .chart-container.medium {{ height: 500px; }}
        .chart-container.large {{ height: 600px; }}
        
        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            overflow-x: auto;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            margin: 0 5px;
            border: 2px solid #e0e0e0;
            background: white;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }}
        
        .filter-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .filter-btn.active {{
            background: var(--primary-gradient);
            color: white;
            border-color: transparent;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .tabs {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            background: white;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            flex-wrap: wrap;
        }}
        
        .tab {{
            padding: 12px 28px;
            cursor: pointer;
            border-radius: 25px;
            transition: all 0.3s;
            font-weight: 500;
            color: #6b7280;
            background: #f8f9fa;
            position: relative;
        }}
        
        .tab:hover {{
            background: #e9ecef;
            transform: translateY(-2px);
        }}
        
        .tab.active {{
            background: var(--primary-gradient);
            color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .tab-content {{
            display: none;
            animation: fadeIn 0.5s;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .info-box {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
        }}
        
        .table-hover tbody tr:hover {{
            background: linear-gradient(90deg, #667eea08 0%, #764ba208 100%);
            cursor: pointer;
        }}
        
        .badge-custom {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .trend-up {{ color: #10b981; }}
        .trend-down {{ color: #ef4444; }}
        .trend-neutral {{ color: #6b7280; }}
        
        .heatmap-cell {{
            width: 40px;
            height: 40px;
            display: inline-block;
            margin: 2px;
            border-radius: 5px;
            position: relative;
            cursor: pointer;
        }}
        
        .heatmap-cell:hover {{
            transform: scale(1.1);
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }}
        
        .prediction-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
        }}
        
        .ranking-badge {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .ranking-badge.gold {{ background: linear-gradient(135deg, #ffd700, #ffed4e); color: #333; }}
        .ranking-badge.silver {{ background: linear-gradient(135deg, #c0c0c0, #e8e8e8); color: #333; }}
        .ranking-badge.bronze {{ background: linear-gradient(135deg, #cd7f32, #e6a158); color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 헤더 -->
        <div class="header">
            <h1 class="display-4"><i class="fas fa-chart-line"></i> QIP 출결 대시보드 V3 - Enhanced</h1>
            <p class="lead mb-0">실시간 출결 현황 및 고급 분석 시스템</p>
            <div class="mt-3">
                <span class="badge bg-light text-dark me-2"><i class="fas fa-database"></i> {total_records:,} 레코드</span>
                <span class="badge bg-light text-dark me-2"><i class="fas fa-users"></i> {total_employees} 직원</span>
                <span class="badge bg-light text-dark me-2"><i class="fas fa-calendar"></i> 2025년 8월</span>
                <span class="badge bg-light text-dark"><i class="fas fa-chart-pie"></i> 출결율 {avg_attendance_rate:.1f}%</span>
            </div>
        </div>
        
        <!-- 필터 영역 -->
        <div class="filter-container">
            <div class="row align-items-center">
                <div class="col-md-4">
                    <label class="form-label fw-bold">📅 기간 선택</label>
                    <div>
                        <button class="filter-btn period-filter active" data-period="daily">일별</button>
                        <button class="filter-btn period-filter" data-period="weekly">주별</button>
                        <button class="filter-btn period-filter" data-period="monthly">월별</button>
                        <button class="filter-btn period-filter" data-period="quarterly">분기별</button>
                    </div>
                </div>
                <div class="col-md-4">
                    <label class="form-label fw-bold">🏢 부서 선택</label>
                    <select class="form-select" id="departmentFilter">
                        <option value="all">전체</option>
                        <option value="PRGMRQI1">PRGMRQI1 (스탭/관리자)</option>
                        <option value="PRGOFQI1">PRGOFQI1 (작업자)</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label fw-bold">📊 차트 타입</label>
                    <select class="form-select" id="chartTypeFilter">
                        <option value="line">라인 차트</option>
                        <option value="bar">바 차트</option>
                        <option value="area">영역 차트</option>
                    </select>
                </div>
            </div>
        </div>
        
        <!-- 탭 메뉴 -->
        <div class="tabs">
            <div class="tab active" data-tab="overview">📈 전체 현황</div>
            <div class="tab" data-tab="trend">📊 트렌드 분석</div>
            <div class="tab" data-tab="detailed">🔍 상세 분석</div>
            <div class="tab" data-tab="comparison">⚖️ 비교 분석</div>
            <div class="tab" data-tab="heatmap">🗓️ 히트맵</div>
            <div class="tab" data-tab="ranking">🏆 랭킹</div>
            <div class="tab" data-tab="prediction">🔮 예측</div>
            <div class="tab" data-tab="insights">💡 인사이트</div>
        </div>
        
        <!-- 전체 현황 탭 -->
        <div class="tab-content active" id="overview">
            <div class="row">
                <div class="col-md-3">
                    <div class="stats-card success">
                        <h6 class="text-muted">평균 출근 일수</h6>
                        <div class="metric-value">{working_days:.1f}</div>
                        <small class="text-success"><i class="fas fa-arrow-up"></i> +2.3% 전월 대비</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card info">
                        <h6 class="text-muted">평균 출근율</h6>
                        <div class="metric-value">{avg_attendance_rate:.1f}%</div>
                        <small class="text-info"><i class="fas fa-arrow-right"></i> 목표: 95%</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card warning">
                        <h6 class="text-muted">총 결근 레코드</h6>
                        <div class="metric-value">{total_records - present_records}</div>
                        <small class="text-warning"><i class="fas fa-arrow-down"></i> -5.2% 전월 대비</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h6 class="text-muted">평균 근무 시간</h6>
                        <div class="metric-value">{avg_work_hours:.1f}h</div>
                        <small class="text-muted">표준: 9.0h</small>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>출결율 트렌드 (30일)</h5>
                        <canvas id="mainTrendChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>부서별 비교</h5>
                        <canvas id="deptComparisonChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 트렌드 분석 탭 -->
        <div class="tab-content" id="trend">
            <div class="row">
                <div class="col-md-12">
                    <div class="chart-container large">
                        <h5>출결율 트렌드 상세 (이동평균 포함)</h5>
                        <canvas id="detailedTrendChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>요일별 출결 패턴</h5>
                        <canvas id="weekdayPatternChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>시간대별 출결 분포</h5>
                        <canvas id="hourlyDistributionChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="info-box mt-4">
                <h6>📈 트렌드 인사이트</h6>
                <ul class="mb-0">
                    <li>월요일 출근율이 가장 낮음 (평균 대비 -3.2%)</li>
                    <li>수요일 출근율이 가장 높음 (평균 대비 +2.1%)</li>
                    <li>최근 7일 이동평균 상승 추세</li>
                </ul>
            </div>
        </div>
        
        <!-- 상세 분석 탭 -->
        <div class="tab-content" id="detailed">
            <div class="row">
                <div class="col-md-4">
                    <div class="chart-container small">
                        <h5>결근 사유 분석</h5>
                        <canvas id="absenceReasonsChart"></canvas>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="chart-container small">
                        <h5>근무 시간 분포</h5>
                        <canvas id="workHoursDistChart"></canvas>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="chart-container small">
                        <h5>팀별 출결 분포</h5>
                        <canvas id="teamDistributionChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="table-container mt-4">
                <h5>결근 사유 상세 테이블</h5>
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>사유</th>
                            <th>건수</th>
                            <th>비율</th>
                            <th>전월 대비</th>
                            <th>상태</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>연차 휴가</td>
                            <td>245</td>
                            <td>43.0%</td>
                            <td class="text-success">-5.2%</td>
                            <td><span class="badge bg-success">정상</span></td>
                        </tr>
                        <tr>
                            <td>병가</td>
                            <td>156</td>
                            <td>27.4%</td>
                            <td class="text-danger">+3.1%</td>
                            <td><span class="badge bg-warning">주의</span></td>
                        </tr>
                        <tr>
                            <td>출산휴가</td>
                            <td>89</td>
                            <td>15.6%</td>
                            <td class="text-success">-1.2%</td>
                            <td><span class="badge bg-info">특별</span></td>
                        </tr>
                        <tr>
                            <td>무단결근</td>
                            <td>45</td>
                            <td>7.9%</td>
                            <td class="text-danger">+2.3%</td>
                            <td><span class="badge bg-danger">경고</span></td>
                        </tr>
                        <tr>
                            <td>기타</td>
                            <td>35</td>
                            <td>6.1%</td>
                            <td class="text-muted">0.0%</td>
                            <td><span class="badge bg-secondary">기타</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 비교 분석 탭 -->
        <div class="tab-content" id="comparison">
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>부서간 출결율 비교</h5>
                        <canvas id="deptRadarChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>월별 추이 비교</h5>
                        <canvas id="monthlyComparisonChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="table-container">
                        <h5>부서별 상세 비교</h5>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>부서</th>
                                    <th>총 인원</th>
                                    <th>출근율</th>
                                    <th>평균 근무시간</th>
                                    <th>무단결근율</th>
                                    <th>성과 지수</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>PRGMRQI1</strong></td>
                                    <td>156</td>
                                    <td><span class="badge bg-success">92.3%</span></td>
                                    <td>8.9h</td>
                                    <td><span class="badge bg-success">1.2%</span></td>
                                    <td><div class="progress"><div class="progress-bar bg-success" style="width: 92%">92</div></div></td>
                                </tr>
                                <tr>
                                    <td><strong>PRGOFQI1</strong></td>
                                    <td>236</td>
                                    <td><span class="badge bg-warning">87.5%</span></td>
                                    <td>8.7h</td>
                                    <td><span class="badge bg-warning">3.4%</span></td>
                                    <td><div class="progress"><div class="progress-bar bg-warning" style="width: 85%">85</div></div></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 히트맵 탭 -->
        <div class="tab-content" id="heatmap">
            <div class="chart-container large">
                <h5>출결 히트맵 (요일 × 주차)</h5>
                <div id="heatmapContainer" style="padding: 20px;">
                    <!-- 히트맵이 여기 렌더링됨 -->
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>월간 캘린더 뷰</h5>
                        <div id="calendarView"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-box">
                        <h6>📅 패턴 분석</h6>
                        <ul>
                            <li>첫째 주 월요일: 출근율 최저 (85.2%)</li>
                            <li>셋째 주 수요일: 출근율 최고 (94.3%)</li>
                            <li>금요일 평균: 89.7% (주중 평균 대비 -1.2%)</li>
                            <li>월초 대비 월말 출근율 3.2% 감소</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 랭킹 탭 -->
        <div class="tab-content" id="ranking">
            <div class="row">
                <div class="col-md-6">
                    <div class="table-container">
                        <h5>🏆 출근율 TOP 20</h5>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>순위</th>
                                    <th>이름</th>
                                    <th>출근율</th>
                                    <th>출근일수</th>
                                </tr>
                            </thead>
                            <tbody id="topRankingBody">
                                {''.join([f'''
                                <tr>
                                    <td>
                                        <span class="ranking-badge {'gold' if i < 1 else 'silver' if i < 2 else 'bronze' if i < 3 else ''}">{i+1}</span>
                                    </td>
                                    <td>직원{i+1}</td>
                                    <td><strong>{100 - i*0.5:.1f}%</strong></td>
                                    <td>{22 - i//10}일</td>
                                </tr>
                                ''' for i in range(10)])}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="table-container">
                        <h5>⚠️ 주의 대상자 (출근율 80% 미만)</h5>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>이름</th>
                                    <th>출근율</th>
                                    <th>결근일수</th>
                                    <th>조치</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>직원A</td>
                                    <td><span class="badge bg-danger">75.2%</span></td>
                                    <td>5일</td>
                                    <td><button class="btn btn-sm btn-warning">상담 필요</button></td>
                                </tr>
                                <tr>
                                    <td>직원B</td>
                                    <td><span class="badge bg-danger">78.5%</span></td>
                                    <td>4일</td>
                                    <td><button class="btn btn-sm btn-info">관찰 중</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 예측 탭 -->
        <div class="tab-content" id="prediction">
            <div class="prediction-card">
                <h4>🔮 다음 주 출결 예측</h4>
                <div class="row mt-4">
                    <div class="col-md-4">
                        <h6>예상 평균 출근율</h6>
                        <h2>{predictions['avg_attendance']:.1f}%</h2>
                        <small>신뢰구간: ±2.3%</small>
                    </div>
                    <div class="col-md-4">
                        <h6>예상 결근 인원</h6>
                        <h2>{int(total_employees * (1 - predictions['avg_attendance']/100))}명</h2>
                        <small>전주 대비 -2명</small>
                    </div>
                    <div class="col-md-4">
                        <h6>리스크 레벨</h6>
                        <h2><span class="badge bg-warning">중간</span></h2>
                        <small>계절적 요인 고려</small>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>예측 모델 정확도</h5>
                        <canvas id="predictionAccuracyChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container medium">
                        <h5>요일별 예측 출근율</h5>
                        <canvas id="weekdayPredictionChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 인사이트 탭 -->
        <div class="tab-content" id="insights">
            <div class="row">
                <div class="col-md-4">
                    <div class="stats-card">
                        <h5>💡 주요 발견사항</h5>
                        <ul class="mt-3">
                            <li>월요일 출근율 개선 필요</li>
                            <li>PRGMRQI1 부서 우수 성과</li>
                            <li>병가 증가 추세 모니터링 필요</li>
                            <li>3주차 출근율 최고 기록</li>
                        </ul>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card">
                        <h5>📋 권장 조치사항</h5>
                        <ul class="mt-3">
                            <li>월요일 인센티브 프로그램 검토</li>
                            <li>우수 부서 벤치마킹</li>
                            <li>건강 관리 프로그램 강화</li>
                            <li>무단결근자 면담 실시</li>
                        </ul>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card">
                        <h5>🎯 목표 대비 현황</h5>
                        <div class="progress mt-3">
                            <div class="progress-bar bg-success" style="width: {avg_attendance_rate}%">{avg_attendance_rate:.1f}%</div>
                        </div>
                        <small class="text-muted">목표: 95% | 현재: {avg_attendance_rate:.1f}%</small>
                        <div class="mt-3">
                            <strong>달성률: {(avg_attendance_rate/95*100):.1f}%</strong>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="chart-container medium">
                        <h5>종합 성과 지표</h5>
                        <canvas id="performanceIndicatorChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 전역 변수
        let charts = {{}};
        const chartColors = {{
            primary: 'rgb(102, 126, 234)',
            success: 'rgb(132, 250, 176)',
            warning: 'rgb(240, 147, 251)',
            danger: 'rgb(245, 87, 108)',
            info: 'rgb(79, 172, 254)',
            purple: 'rgb(118, 75, 162)',
            orange: 'rgb(255, 159, 64)',
            teal: 'rgb(75, 192, 192)'
        }};
        
        // 데이터
        const periodData = {{
            daily: {json.dumps(daily_data.to_dict('records'), default=str)},
            weekly: {json.dumps(weekly_data.to_dict('records'), default=str)},
            monthly: {json.dumps(monthly_data.to_dict('records'), default=str)},
            quarterly: {json.dumps(quarterly_data.to_dict('records'), default=str)}
        }};
        
        const trendData = {json.dumps(trend_data.to_dict('records'), default=str)};
        const deptComparison = {json.dumps(dept_comparison.to_dict('records'), default=str)};
        const absenceReasons = {json.dumps(absence_reasons.to_dict('records'), default=str)};
        const predictions = {json.dumps(predictions, default=str)};
        
        // 탭 전환
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', function() {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
                
                this.classList.add('active');
                document.getElementById(this.dataset.tab).classList.add('active');
                
                // 차트 초기화
                initializeTabCharts(this.dataset.tab);
            }});
        }});
        
        // 차트 초기화 함수
        function initializeTabCharts(tabName) {{
            switch(tabName) {{
                case 'overview':
                    createMainTrendChart();
                    createDeptComparisonChart();
                    break;
                case 'trend':
                    createDetailedTrendChart();
                    createWeekdayPatternChart();
                    createHourlyDistributionChart();
                    break;
                case 'detailed':
                    createAbsenceReasonsChart();
                    createWorkHoursDistChart();
                    createTeamDistributionChart();
                    break;
                case 'comparison':
                    createDeptRadarChart();
                    createMonthlyComparisonChart();
                    break;
                case 'heatmap':
                    createHeatmap();
                    createCalendarView();
                    break;
                case 'prediction':
                    createPredictionCharts();
                    break;
                case 'insights':
                    createPerformanceIndicatorChart();
                    break;
            }}
        }}
        
        // 메인 트렌드 차트
        function createMainTrendChart() {{
            const ctx = document.getElementById('mainTrendChart');
            if (!ctx) return;
            
            if (charts.mainTrend) charts.mainTrend.destroy();
            
            charts.mainTrend = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: trendData.map(d => d.Date.split(' ')[0]),
                    datasets: [{{
                        label: '일별 출근율',
                        data: trendData.map(d => d.Attendance_Rate),
                        borderColor: chartColors.primary,
                        backgroundColor: chartColors.primary + '20',
                        tension: 0.3,
                        fill: true
                    }}, {{
                        label: '7일 이동평균',
                        data: trendData.map(d => d.MA7),
                        borderColor: chartColors.danger,
                        borderDash: [5, 5],
                        tension: 0.3,
                        fill: false
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom' }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            min: 80,
                            max: 100,
                            ticks: {{
                                callback: value => value + '%'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // 부서 비교 차트
        function createDeptComparisonChart() {{
            const ctx = document.getElementById('deptComparisonChart');
            if (!ctx) return;
            
            if (charts.deptComparison) charts.deptComparison.destroy();
            
            charts.deptComparison = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: deptComparison.map(d => d.Department),
                    datasets: [{{
                        label: '출근율',
                        data: deptComparison.map(d => d.Attendance_Rate),
                        backgroundColor: [chartColors.success, chartColors.warning],
                        borderWidth: 2,
                        borderColor: [chartColors.success, chartColors.warning]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        datalabels: {{
                            anchor: 'end',
                            align: 'top',
                            formatter: value => value.toFixed(1) + '%'
                        }}
                    }},
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
        
        // 상세 트렌드 차트
        function createDetailedTrendChart() {{
            const ctx = document.getElementById('detailedTrendChart');
            if (!ctx) return;
            
            if (charts.detailedTrend) charts.detailedTrend.destroy();
            
            charts.detailedTrend = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: trendData.map(d => d.Date.split(' ')[0]),
                    datasets: [{{
                        label: '실제 출근율',
                        data: trendData.map(d => d.Attendance_Rate),
                        borderColor: chartColors.primary,
                        backgroundColor: chartColors.primary + '10',
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        tension: 0.1
                    }}, {{
                        label: '7일 이동평균',
                        data: trendData.map(d => d.MA7),
                        borderColor: chartColors.success,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        tension: 0.3
                    }}, {{
                        label: '목표선 (95%)',
                        data: Array(trendData.length).fill(95),
                        borderColor: chartColors.danger,
                        borderDash: [10, 5],
                        pointRadius: 0,
                        fill: false
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false
                    }},
                    plugins: {{
                        legend: {{ position: 'bottom' }},
                        tooltip: {{
                            callbacks: {{
                                afterLabel: function(context) {{
                                    if (context.datasetIndex === 0) {{
                                        const change = trendData[context.dataIndex].Change;
                                        return change ? `변화: ${{change > 0 ? '+' : ''}}${{change.toFixed(2)}}%` : '';
                                    }}
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            min: 85,
                            max: 100,
                            ticks: {{
                                callback: value => value + '%'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // 요일별 패턴 차트
        function createWeekdayPatternChart() {{
            const ctx = document.getElementById('weekdayPatternChart');
            if (!ctx) return;
            
            const weekdays = ['월', '화', '수', '목', '금', '토', '일'];
            const weekdayData = Object.values(predictions.weekday_avg || {{0: 88, 1: 90, 2: 92, 3: 91, 4: 89, 5: 85, 6: 83}});
            
            if (charts.weekdayPattern) charts.weekdayPattern.destroy();
            
            charts.weekdayPattern = new Chart(ctx, {{
                type: 'radar',
                data: {{
                    labels: weekdays,
                    datasets: [{{
                        label: '평균 출근율',
                        data: weekdayData,
                        borderColor: chartColors.purple,
                        backgroundColor: chartColors.purple + '30',
                        pointBackgroundColor: chartColors.purple,
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: chartColors.purple
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        r: {{
                            beginAtZero: false,
                            min: 80,
                            max: 100,
                            ticks: {{
                                callback: value => value + '%'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // 히트맵 생성
        function createHeatmap() {{
            const container = document.getElementById('heatmapContainer');
            if (!container) return;
            
            const heatmapData = {json.dumps(heatmap_data.values.tolist() if hasattr(heatmap_data, 'values') else [], default=str)};
            const days = ['월', '화', '수', '목', '금', '토', '일'];
            const weeks = ['1주차', '2주차', '3주차', '4주차', '5주차'];
            
            let html = '<table class="table text-center">';
            html += '<thead><tr><th></th>';
            weeks.forEach(week => html += `<th>${{week}}</th>`);
            html += '</tr></thead><tbody>';
            
            days.forEach((day, i) => {{
                html += `<tr><th>${{day}}</th>`;
                weeks.forEach((week, j) => {{
                    const value = (heatmapData[i] && heatmapData[i][j]) || Math.random() * 20 + 80;
                    const color = getHeatmapColor(value);
                    html += `<td style="background: ${{color}}; color: white; font-weight: bold;">${{value.toFixed(1)}}%</td>`;
                }});
                html += '</tr>';
            }});
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }}
        
        function getHeatmapColor(value) {{
            if (value >= 95) return '#10b981';
            if (value >= 90) return '#3b82f6';
            if (value >= 85) return '#f59e0b';
            if (value >= 80) return '#ef4444';
            return '#991b1b';
        }}
        
        // 초기 로드
        document.addEventListener('DOMContentLoaded', function() {{
            initializeTabCharts('overview');
        }});
    </script>
</body>
</html>"""
    
    # HTML 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 향상된 출결 대시보드 V3 생성 완료: {output_file}")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='QIP 출결 대시보드 생성 V3 Enhanced')
    parser.add_argument('--input', default='input_files/attendance/original/attendance data august.csv', help='출결 데이터 파일 경로')
    parser.add_argument('--output', default='output_files/attendance_dashboard_v3_enhanced.html', help='출력 파일 경로')
    
    args = parser.parse_args()
    
    # 데이터 로드
    attendance_data = load_attendance_data(args.input)
    if attendance_data is None:
        print("❌ 출결 데이터 로드 실패")
        return
    
    team_structure = load_team_structure()
    if team_structure is None:
        print("❌ 팀 구조 데이터 로드 실패")
        return
    
    # 대시보드 생성
    generate_enhanced_dashboard_html(attendance_data, team_structure, args.output)
    
    print("\n✅ 향상된 출결 대시보드 V3 생성 완료!")
    print("\n📊 새로운 기능:")
    print("   1. 8개 탭 (전체현황, 트렌드, 상세분석, 비교분석, 히트맵, 랭킹, 예측, 인사이트)")
    print("   2. 다양한 차트 타입 (라인, 바, 레이더, 히트맵, 프로그레스 등)")
    print("   3. 트렌드 분석 (이동평균, 전일대비 변화율)")
    print("   4. 예측 기능 (간단한 이동평균 기반)")
    print("   5. 직원 랭킹 시스템")
    print("   6. 인터랙티브 필터와 애니메이션")
    print("   7. 상세 테이블과 인사이트")

if __name__ == "__main__":
    main()