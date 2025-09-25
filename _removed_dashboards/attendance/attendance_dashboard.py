#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 출결 대시보드 생성 시스템
HR info/ATTENDANCE.xlsx 파일을 기반으로 출결 현황 대시보드 생성
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
import numpy as np
import argparse

def load_attendance_data(file_path):
    """출결 데이터 로드"""
    try:
        # CSV 파일 읽기
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8-sig')  # BOM 처리를 위해 utf-8-sig 사용
        else:
            df = pd.read_excel(file_path, sheet_name='Sheet1')
        
        print(f"✅ 출결 데이터 로드 완료: {len(df)} 행")
        
        # Work Date를 datetime으로 변환
        df['Work Date'] = pd.to_datetime(df['Work Date'], format='%Y.%m.%d')
        
        # 출근 여부를 boolean으로 변환
        df['is_present'] = df['compAdd'] == 'Đi làm'
        
        # 무단결근 여부 확인
        df['is_unapproved'] = (df['compAdd'] == 'Vắng mặt') & (df['Reason Description'].isna())
        
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
        '5I': 8.9, '5J': 8.9, '5K': 8.9, '5N': 8.9, '5O': 8.9,  # 임산부 ADMIN (5분 일찍)
        '7I': 8.0, '7J': 8.0, '7K': 8.0, '7P': 8.0, '7T': 8.0, '7U': 8.0,  # 임산부 ADMIN (1시간 일찍)
        '9B': 9.0, '9I': 8.0, '9J': 9.0, '9K': 9.5, '9N': 9.0,  # 일반 ADMIN
        '9R': 9.0, '9S': 9.0, '9U': 9.0, '9V': 9.0
    }
    return work_hours.get(wtime_code, 9.0)  # 기본값 9시간

def process_attendance_by_period(df, period='daily'):
    """기간별 출결 데이터 처리"""
    
    if period == 'daily':
        # 일별 집계
        grouped = df.groupby('Work Date')
    elif period == 'weekly':
        # 주별 집계
        df['Week'] = df['Work Date'].dt.isocalendar().week
        df['Year'] = df['Work Date'].dt.year
        grouped = df.groupby(['Year', 'Week'])
    elif period == 'monthly':
        # 월별 집계
        df['Month'] = df['Work Date'].dt.month
        df['Year'] = df['Work Date'].dt.year
        grouped = df.groupby(['Year', 'Month'])
    elif period == 'quarterly':
        # 분기별 집계
        df['Quarter'] = df['Work Date'].dt.quarter
        df['Year'] = df['Work Date'].dt.year
        grouped = df.groupby(['Year', 'Quarter'])
    else:
        grouped = df.groupby('Work Date')
    
    # 집계 계산
    result = grouped.agg({
        'ID No': 'nunique',  # 전체 인원
        'is_present': 'sum',  # 출근 인원
        'is_unapproved': 'sum',  # 무단결근 인원
        'WTime': lambda x: np.mean([calculate_work_hours(t) for t in x])  # 평균 근무시간
    }).reset_index()
    
    # 칼럼명 변경 - period 유형에 따라 다르게 처리
    if period == 'daily':
        result.columns = ['Period', 'Total_Employees', 'Present_Count', 'Unapproved_Absence', 'Avg_Work_Hours']
    elif period == 'weekly':
        result.columns = ['Year', 'Week', 'Total_Employees', 'Present_Count', 'Unapproved_Absence', 'Avg_Work_Hours']
    elif period in ['monthly', 'quarterly']:
        period_name = 'Month' if period == 'monthly' else 'Quarter'
        result.columns = ['Year', period_name, 'Total_Employees', 'Present_Count', 'Unapproved_Absence', 'Avg_Work_Hours']
        # Period_Num으로 통일
        result.rename(columns={period_name: 'Period_Num'}, inplace=True)
    
    # 출근율 계산
    result['Attendance_Rate'] = (result['Present_Count'] / result['Total_Employees']) * 100
    result['Absence_Count'] = result['Total_Employees'] - result['Present_Count']
    
    return result

def process_attendance_by_role(df, team_structure):
    """역할별 출결 데이터 처리"""
    
    # 직원별 역할 매핑
    position_role_map = {}
    for position in team_structure['positions']:
        # position_3rd를 키로 사용하여 role_category 매핑
        position_role_map[position['position_3rd']] = position['role_category']
    
    # 9개 역할별 집계
    role_categories = team_structure['role_categories']
    role_stats = []
    
    for role in role_categories:
        # 해당 역할의 직원들 필터링
        role_positions = [p['position_3rd'] for p in team_structure['positions'] if p['role_category'] == role]
        role_df = df[df['Last name'].isin(role_positions)]  # 실제로는 position 매칭이 필요
        
        if len(role_df) > 0:
            total = role_df['ID No'].nunique()
            present = role_df[role_df['is_present']]['ID No'].nunique()
            attendance_rate = (present / total * 100) if total > 0 else 0
            
            role_stats.append({
                'role': role,
                'total': total,
                'present': present,
                'absent': total - present,
                'attendance_rate': attendance_rate
            })
        else:
            role_stats.append({
                'role': role,
                'total': 0,
                'present': 0,
                'absent': 0,
                'attendance_rate': 0
            })
    
    return role_stats

def process_attendance_by_team(df, team_structure):
    """팀별 출결 데이터 처리"""
    
    teams = team_structure['teams']
    team_stats = []
    
    for team in teams:
        # 해당 팀의 직원들 필터링
        team_positions = [p['position_3rd'] for p in team_structure['positions'] if p['team_name'] == team]
        team_df = df[df['Last name'].isin(team_positions)]  # 실제로는 position 매칭이 필요
        
        if len(team_df) > 0:
            total = team_df['ID No'].nunique()
            present = team_df[team_df['is_present']]['ID No'].nunique()
            absent = total - present
            attendance_rate = (present / total * 100) if total > 0 else 0
            
            team_stats.append({
                'team': team,
                'total': total,
                'present': present,
                'absent': absent,
                'absence_rate': 100 - attendance_rate
            })
        else:
            team_stats.append({
                'team': team,
                'total': 0,
                'present': 0,
                'absent': 0,
                'absence_rate': 0
            })
    
    return team_stats

def generate_dashboard_html(attendance_data, team_structure, output_file='attendance_dashboard.html'):
    """출결 대시보드 HTML 생성"""
    
    # 기간별 데이터 처리
    daily_data = process_attendance_by_period(attendance_data, 'daily')
    weekly_data = process_attendance_by_period(attendance_data, 'weekly')
    monthly_data = process_attendance_by_period(attendance_data, 'monthly')
    quarterly_data = process_attendance_by_period(attendance_data, 'quarterly')
    
    # 역할별, 팀별 데이터 처리
    role_stats = process_attendance_by_role(attendance_data, team_structure)
    team_stats = process_attendance_by_team(attendance_data, team_structure)
    
    # 전체 통계 계산
    total_employees = attendance_data['ID No'].nunique()
    total_present = attendance_data[attendance_data['is_present']]['ID No'].nunique()
    avg_attendance_rate = (total_present / total_employees * 100) if total_employees > 0 else 0
    total_absent = total_employees - total_present
    avg_work_hours = np.mean([calculate_work_hours(t) for t in attendance_data['WTime']])
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 출결 대시보드</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            background: #f5f5f5;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .filter-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .stats-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        
        .stats-card h6 {{
            color: #6b7280;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .stats-card h2 {{
            color: #1f2937;
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            position: relative;
            height: 400px;
        }}
        
        .table-container {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            margin: 0 5px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .filter-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            background: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .tab {{
            padding: 12px 24px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
            font-weight: 500;
            color: #6b7280;
        }}
        
        .tab:hover {{
            background: #f3f4f6;
        }}
        
        .tab.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 헤더 -->
        <div class="header">
            <h1><i class="fas fa-calendar-check"></i> QIP 출결 대시보드</h1>
            <p class="mb-0">실시간 출결 현황 및 분석</p>
        </div>
        
        <!-- 필터 영역 - 건물 필터 제거됨 -->
        <div class="filter-container">
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">기간 선택</label>
                    <div>
                        <button class="filter-btn period-filter active" data-period="daily">일별</button>
                        <button class="filter-btn period-filter" data-period="weekly">주별</button>
                        <button class="filter-btn period-filter" data-period="monthly">월별</button>
                        <button class="filter-btn period-filter" data-period="quarterly">분기별</button>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">부서 선택</label>
                    <select class="form-select" id="departmentFilter">
                        <option value="all">전체</option>
                        <option value="PRGMRQI1">PRGMRQI1 (스탭/관리자)</option>
                        <option value="PRGOFQI1">PRGOFQI1 (작업자)</option>
                    </select>
                </div>
            </div>
        </div>
        
        <!-- 탭 메뉴 -->
        <div class="tabs">
            <div class="tab active" data-tab="overview">전체 현황</div>
            <div class="tab" data-tab="trend">출결 트렌드</div>
            <div class="tab" data-tab="team">팀별 분석</div>
            <div class="tab" data-tab="role">역할별 분석</div>
        </div>
        
        <!-- 전체 현황 탭 -->
        <div class="tab-content active" id="overview">
            <div class="row">
                <div class="col-md-3">
                    <div class="stats-card">
                        <h6>평균 출근 일수</h6>
                        <h2 id="avgAttendanceDays">0<span style="font-size: 1rem; color: #9ca3af;">일</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h6>평균 출근율</h6>
                        <h2 id="avgAttendanceRate">{avg_attendance_rate:.1f}<span style="font-size: 1rem; color: #9ca3af;">%</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h6>결근자수</h6>
                        <h2 id="absentCount">{total_absent}<span style="font-size: 1rem; color: #9ca3af;">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h6>평균 근무 시간</h6>
                        <h2 id="avgWorkHours">{avg_work_hours:.1f}<span style="font-size: 1rem; color: #9ca3af;">시간</span></h2>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 출결 트렌드 탭 -->
        <div class="tab-content" id="trend">
            <div class="chart-container">
                <h5>출결 트렌드</h5>
                <canvas id="attendanceTrendChart"></canvas>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-container">
                        <h5>팀별 출결 트렌드</h5>
                        <canvas id="teamTrendChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <h5>역할별 출결 트렌드</h5>
                        <canvas id="roleTrendChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 팀별 분석 탭 -->
        <div class="tab-content" id="team">
            <div class="table-container">
                <h5>팀별 출결 현황</h5>
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>팀명</th>
                            <th>총 인원</th>
                            <th>출근 인원</th>
                            <th>결근 인원</th>
                            <th>결근율</th>
                        </tr>
                    </thead>
                    <tbody id="teamTableBody">
                        {''.join([f'''
                        <tr>
                            <td>{team['team']}</td>
                            <td>{team['total']}</td>
                            <td>{team['present']}</td>
                            <td>{team['absent']}</td>
                            <td>{team['absence_rate']:.1f}%</td>
                        </tr>
                        ''' for team in team_stats])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 역할별 분석 탭 -->
        <div class="tab-content" id="role">
            <div class="chart-container">
                <h5>역할별 출결 현황 (9개 역할 기준)</h5>
                <canvas id="roleChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // 전역 변수
        let attendanceTrendChart = null;
        let teamTrendChart = null;
        let roleTrendChart = null;
        let roleChart = null;
        
        // 데이터 저장
        const periodData = {{
            daily: {json.dumps(daily_data.to_dict('records'), default=str)},
            weekly: {json.dumps(weekly_data.to_dict('records'), default=str)},
            monthly: {json.dumps(monthly_data.to_dict('records'), default=str)},
            quarterly: {json.dumps(quarterly_data.to_dict('records'), default=str)}
        }};
        
        const roleStats = {json.dumps(role_stats)};
        const teamStats = {json.dumps(team_stats)};
        
        // 현재 선택된 기간
        let currentPeriod = 'daily';
        
        // 탭 전환
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', function() {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
                
                this.classList.add('active');
                document.getElementById(this.dataset.tab).classList.add('active');
                
                // 차트 업데이트
                if (this.dataset.tab === 'trend') {{
                    updateTrendCharts();
                }} else if (this.dataset.tab === 'role') {{
                    updateRoleChart();
                }}
            }});
        }});
        
        // 기간 필터
        document.querySelectorAll('.period-filter').forEach(btn => {{
            btn.addEventListener('click', function() {{
                document.querySelectorAll('.period-filter').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentPeriod = this.dataset.period;
                updateDashboard();
            }});
        }});
        
        // 부서 필터
        document.getElementById('departmentFilter').addEventListener('change', function() {{
            updateDashboard();
        }});
        
        // 대시보드 업데이트
        function updateDashboard() {{
            const data = periodData[currentPeriod];
            const dept = document.getElementById('departmentFilter').value;
            
            // 필터링된 데이터로 통계 재계산
            let filteredData = data;
            if (dept !== 'all') {{
                // 부서별 필터링 로직 필요
            }}
            
            // 전체 현황 업데이트
            if (filteredData.length > 0) {{
                const avgAttendance = filteredData.reduce((sum, d) => sum + d.Attendance_Rate, 0) / filteredData.length;
                const totalAbsent = filteredData.reduce((sum, d) => sum + d.Absence_Count, 0);
                const avgHours = filteredData.reduce((sum, d) => sum + d.Avg_Work_Hours, 0) / filteredData.length;
                
                document.getElementById('avgAttendanceRate').innerHTML = avgAttendance.toFixed(1) + '<span style="font-size: 1rem; color: #9ca3af;">%</span>';
                document.getElementById('absentCount').innerHTML = totalAbsent + '<span style="font-size: 1rem; color: #9ca3af;">명</span>';
                document.getElementById('avgWorkHours').innerHTML = avgHours.toFixed(1) + '<span style="font-size: 1rem; color: #9ca3af;">시간</span>';
            }}
            
            // 차트 업데이트
            updateTrendCharts();
        }}
        
        // 트렌드 차트 업데이트
        function updateTrendCharts() {{
            const data = periodData[currentPeriod];
            
            // 출결 트렌드 차트
            if (attendanceTrendChart) {{
                attendanceTrendChart.destroy();
            }}
            
            const ctx = document.getElementById('attendanceTrendChart');
            if (ctx) {{
                attendanceTrendChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: data.map(d => d.Period || `${{d.Year}}-${{d.Period_Num || d.Week}}`),
                        datasets: [{{
                            label: '출근율',
                            data: data.map(d => d.Attendance_Rate),
                            borderColor: 'rgb(102, 126, 234)',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'top'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}
                    }}
                }});
            }}
            
            // 팀별 트렌드 차트
            if (teamTrendChart) {{
                teamTrendChart.destroy();
            }}
            
            const teamCtx = document.getElementById('teamTrendChart');
            if (teamCtx) {{
                teamTrendChart = new Chart(teamCtx, {{
                    type: 'bar',
                    data: {{
                        labels: teamStats.slice(0, 10).map(t => t.team),
                        datasets: [{{
                            label: '출근율',
                            data: teamStats.slice(0, 10).map(t => 100 - t.absence_rate),
                            backgroundColor: 'rgba(102, 126, 234, 0.8)'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}
                    }}
                }});
            }}
            
            // 역할별 트렌드 차트
            if (roleTrendChart) {{
                roleTrendChart.destroy();
            }}
            
            const roleCtx = document.getElementById('roleTrendChart');
            if (roleCtx) {{
                roleTrendChart = new Chart(roleCtx, {{
                    type: 'bar',
                    data: {{
                        labels: roleStats.map(r => r.role),
                        datasets: [{{
                            label: '출근율',
                            data: roleStats.map(r => r.attendance_rate),
                            backgroundColor: 'rgba(118, 75, 162, 0.8)'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}
                    }}
                }});
            }}
        }}
        
        // 역할별 차트 업데이트
        function updateRoleChart() {{
            if (roleChart) {{
                roleChart.destroy();
            }}
            
            const ctx = document.getElementById('roleChart');
            if (ctx) {{
                roleChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: roleStats.map(r => r.role),
                        datasets: [{{
                            label: '출근율',
                            data: roleStats.map(r => r.attendance_rate),
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.8)',
                                'rgba(54, 162, 235, 0.8)',
                                'rgba(255, 206, 86, 0.8)',
                                'rgba(75, 192, 192, 0.8)',
                                'rgba(153, 102, 255, 0.8)',
                                'rgba(255, 159, 64, 0.8)',
                                'rgba(199, 199, 199, 0.8)',
                                'rgba(83, 102, 255, 0.8)',
                                'rgba(255, 99, 255, 0.8)'
                            ]
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const role = roleStats[context.dataIndex];
                                        return [
                                            `출근율: ${{role.attendance_rate.toFixed(1)}}%`,
                                            `총 인원: ${{role.total}}명`,
                                            `출근: ${{role.present}}명`,
                                            `결근: ${{role.absent}}명`
                                        ];
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}
                    }}
                }});
            }}
        }}
        
        // 초기 로드
        document.addEventListener('DOMContentLoaded', function() {{
            updateDashboard();
        }});
    </script>
</body>
</html>"""
    
    # HTML 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 출결 대시보드 생성 완료: {output_file}")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='QIP 출결 대시보드 생성')
    parser.add_argument('--input', default='input_files/attendance/original/attendance data august.csv', help='출결 데이터 파일 경로')
    parser.add_argument('--output', default='output_files/attendance_dashboard.html', help='출력 파일 경로')
    
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
    generate_dashboard_html(attendance_data, team_structure, args.output)
    
    print("✅ 출결 대시보드 생성 완료!")

if __name__ == "__main__":
    main()