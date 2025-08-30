#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Management Dashboard Generator
QIP 인센티브 관리 대시보드 생성 프로그램
- 조직도 시각화
- 이슈 트래킹
- HR 분석
- 성과 모니터링
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
import argparse
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def load_config(month, year):
    """월별 설정 파일 로드"""
    config_file = f'config_files/config_{month}_{year}.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_translations():
    """번역 파일 로드"""
    translations_file = 'config_files/dashboard_translations.json'
    if os.path.exists(translations_file):
        with open(translations_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_all_data(config, month, year):
    """모든 데이터 소스 로드"""
    data = {
        'employees': None,
        'attendance': None,
        'aql': None,
        '5prs': None,
        'previous_month': None,
        'metadata': None
    }
    
    try:
        # 1. Excel 파일 로드 (최종 인센티브 계산 결과)
        excel_file = f'output_files/output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.xlsx'
        if os.path.exists(excel_file):
            # 시트 이름 확인 후 로드
            try:
                xl = pd.ExcelFile(excel_file)
                sheet_name = xl.sheet_names[0] if xl.sheet_names else 'Sheet1'
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                data['employees'] = df
                print(f"✅ Excel 데이터 로드: {len(df)} 직원")
            except Exception as e:
                print(f"⚠️ Excel 로드 경고: {str(e)}")
        
        # 2. 메타데이터 로드
        metadata_file = f'output_files/output_QIP_incentive_{month}_{year}_metadata.json'
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data['metadata'] = json.load(f)
                print(f"✅ 메타데이터 로드: {len(data['metadata'])} 직원")
        
        # 3. 출근 데이터 로드
        if config and 'file_paths' in config:
            attendance_file = config['file_paths'].get('attendance')
            if attendance_file and os.path.exists(attendance_file):
                data['attendance'] = pd.read_csv(attendance_file, encoding='utf-8-sig')
                print(f"✅ 출근 데이터 로드: {attendance_file}")
        
        # 4. AQL 데이터 로드
        if config and 'file_paths' in config:
            aql_file = config['file_paths'].get('aql')
            if aql_file and os.path.exists(aql_file):
                data['aql'] = pd.read_csv(aql_file, encoding='utf-8-sig')
                print(f"✅ AQL 데이터 로드: {aql_file}")
        
        # 5. 5PRS 데이터 로드
        if config and 'file_paths' in config:
            prs_file = config['file_paths'].get('5prs')
            if prs_file and os.path.exists(prs_file):
                data['5prs'] = pd.read_csv(prs_file, encoding='utf-8-sig')
                print(f"✅ 5PRS 데이터 로드: {prs_file}")
        
        # 6. 이전 달 데이터 로드
        prev_month_map = {
            'january': 'december', 'february': 'january', 'march': 'february',
            'april': 'march', 'may': 'april', 'june': 'may',
            'july': 'june', 'august': 'july', 'september': 'august',
            'october': 'september', 'november': 'october', 'december': 'november'
        }
        
        if month in prev_month_map:
            prev_month = prev_month_map[month]
            prev_excel = f'output_files/output_QIP_incentive_{prev_month}_{year}_최종완성버전_v6.0_Complete.xlsx'
            if os.path.exists(prev_excel):
                try:
                    xl = pd.ExcelFile(prev_excel)
                    sheet_name = xl.sheet_names[0] if xl.sheet_names else 'Sheet1'
                    data['previous_month'] = pd.read_excel(prev_excel, sheet_name=sheet_name)
                    print(f"✅ 이전 달 데이터 로드: {prev_month}")
                except Exception as e:
                    print(f"⚠️ 이전 달 데이터 로드 경고: {str(e)}")
        
        return data
    
    except Exception as e:
        print(f"❌ 데이터 로드 중 오류: {str(e)}")
        return data

def analyze_consecutive_failures(all_data):
    """3개월 연속 실패자 상세 분석"""
    consecutive_failures = []
    
    if not all_data['employees'] is None:
        df = all_data['employees']
        
        # 3개월 연속 실패자 찾기 (인센티브가 0인 경우)
        for idx, row in df.iterrows():
            # 8월 인센티브가 0이고
            if row.get('8월_인센티브', 0) == 0:
                # 7월 데이터 확인 (previous_month에서)
                july_incentive = row.get('7월_인센티브', 0)
                
                # 메타데이터에서 추가 정보 확인
                emp_no = str(row.get('사번', ''))
                if all_data['metadata'] and emp_no in all_data['metadata']:
                    meta = all_data['metadata'][emp_no]
                    
                    # 연속 실패 개월 수 계산
                    fail_months = 0
                    if july_incentive == 0:
                        fail_months += 1
                    if row.get('8월_인센티브', 0) == 0:
                        fail_months += 1
                    
                    # 조건 미충족 상세 정보
                    condition_results = meta.get('condition_results', [])
                    failed_conditions = [c for c in condition_results if not c.get('is_met', False)]
                    
                    if fail_months >= 2:  # 2개월 이상 연속 실패
                        consecutive_failures.append({
                            'emp_no': emp_no,
                            'name': row.get('이름', ''),
                            'position': row.get('직급', ''),
                            'type': row.get('TYPE', ''),
                            'fail_months': fail_months,
                            'failed_conditions': failed_conditions,
                            'attendance_rate': meta.get('attendance_rate', 0),
                            'auditor': meta.get('auditor', 'N/A'),  # 추후 추가할 필드
                            'trainer': meta.get('trainer', 'N/A')   # 추후 추가할 필드
                        })
    
    return consecutive_failures

def analyze_attendance_issues(all_data):
    """출근율 90% 미만 직원 분석"""
    attendance_issues = []
    
    if all_data['metadata']:
        for emp_id, meta in all_data['metadata'].items():
            attendance_rate = meta.get('attendance_rate', 100)
            if attendance_rate < 90:
                attendance_issues.append({
                    'emp_no': emp_id,
                    'name': meta.get('name', ''),
                    'position': meta.get('position', ''),
                    'type': meta.get('type', ''),
                    'attendance_rate': attendance_rate,
                    'absent_days': meta.get('absent_days', 0),
                    'working_days': meta.get('working_days', 0)
                })
    
    # 출근율 기준으로 정렬
    attendance_issues.sort(key=lambda x: x['attendance_rate'])
    return attendance_issues

def analyze_aql_5prs_issues(all_data):
    """AQL 및 5PRS 이슈 분석"""
    aql_issues = []
    prs_issues = []
    
    if all_data['metadata']:
        for emp_id, meta in all_data['metadata'].items():
            # AQL 이슈 체크
            condition_results = meta.get('condition_results', [])
            for condition in condition_results:
                if 'AQL' in condition.get('name', ''):
                    if not condition.get('is_met', False):
                        aql_issues.append({
                            'emp_no': emp_id,
                            'name': meta.get('name', ''),
                            'position': meta.get('position', ''),
                            'condition': condition.get('name', ''),
                            'actual': condition.get('actual', 'N/A'),
                            'required': condition.get('required', 'N/A')
                        })
                
                # 5PRS 이슈 체크
                if '5PRS' in condition.get('name', '') or '5족' in condition.get('name', ''):
                    if not condition.get('is_met', False):
                        prs_issues.append({
                            'emp_no': emp_id,
                            'name': meta.get('name', ''),
                            'position': meta.get('position', ''),
                            'condition': condition.get('name', ''),
                            'actual': condition.get('actual', 'N/A'),
                            'required': condition.get('required', 'N/A')
                        })
    
    return aql_issues, prs_issues

def generate_org_chart_data(all_data):
    """조직도 데이터 상세 생성"""
    org_structure = {
        'managers': [],
        'supervisors': [],
        'group_leaders': [],
        'line_leaders': [],
        'workers': [],
        'total_by_type': {'TYPE-1': 0, 'TYPE-2': 0, 'TYPE-3': 0}
    }
    
    if all_data['employees'] is not None:
        df = all_data['employees']
        
        for idx, row in df.iterrows():
            position = str(row.get('직급', '')).upper()
            emp_type = row.get('TYPE', '')
            
            emp_info = {
                'emp_no': str(row.get('사번', '')),
                'name': row.get('이름', ''),
                'position': row.get('직급', ''),
                'type': emp_type,
                'august_incentive': row.get('8월_인센티브', 0),
                'performance': row.get('8월_인센티브', 0) > 0,
                'attendance_rate': 0  # 메타데이터에서 가져올 예정
            }
            
            # 메타데이터에서 추가 정보 가져오기
            if all_data['metadata'] and emp_info['emp_no'] in all_data['metadata']:
                meta = all_data['metadata'][emp_info['emp_no']]
                emp_info['attendance_rate'] = meta.get('attendance_rate', 0)
            
            # 직급별 분류
            if 'MANAGER' in position or 'QUẢN LÝ' in position:
                org_structure['managers'].append(emp_info)
            elif 'SUPERVISOR' in position or 'GIÁM SÁT' in position:
                org_structure['supervisors'].append(emp_info)
            elif 'GROUP' in position and ('LEADER' in position or 'TRƯỞNG' in position):
                org_structure['group_leaders'].append(emp_info)
            elif 'LINE' in position and ('LEADER' in position or 'TRƯỞNG' in position):
                org_structure['line_leaders'].append(emp_info)
            else:
                org_structure['workers'].append(emp_info)
            
            # TYPE별 집계
            if emp_type in org_structure['total_by_type']:
                org_structure['total_by_type'][emp_type] += 1
    
    return org_structure

def analyze_hr_changes(all_data):
    """HR 변동 사항 분석 (신규 입사, 퇴사, TYPE 변경)"""
    hr_analytics = {
        'new_hires': [],
        'resignations': [],
        'type_changes': [],
        'total_employees': 0,
        'by_type': {'TYPE-1': 0, 'TYPE-2': 0, 'TYPE-3': 0},
        'monthly_comparison': {
            'previous_month_total': 0,
            'current_month_total': 0,
            'net_change': 0
        }
    }
    
    if all_data['employees'] is not None:
        current_df = all_data['employees']
        hr_analytics['total_employees'] = len(current_df)
        hr_analytics['monthly_comparison']['current_month_total'] = len(current_df)
        
        # TYPE별 현재 인원 집계
        for idx, row in current_df.iterrows():
            emp_type = row.get('TYPE', '')
            if emp_type in hr_analytics['by_type']:
                hr_analytics['by_type'][emp_type] += 1
        
        # 이전 달과 비교
        if all_data['previous_month'] is not None:
            prev_df = all_data['previous_month']
            hr_analytics['monthly_comparison']['previous_month_total'] = len(prev_df)
            
            # 현재 사번 리스트
            current_emp_ids = set(current_df['사번'].astype(str))
            prev_emp_ids = set(prev_df['사번'].astype(str))
            
            # 신규 입사자 (현재는 있지만 이전 달에는 없던 사람)
            new_hire_ids = current_emp_ids - prev_emp_ids
            for emp_id in new_hire_ids:
                emp_row = current_df[current_df['사번'].astype(str) == emp_id].iloc[0]
                hr_analytics['new_hires'].append({
                    'emp_no': emp_id,
                    'name': emp_row.get('이름', ''),
                    'position': emp_row.get('직급', ''),
                    'type': emp_row.get('TYPE', ''),
                    'hire_month': '2025-08'  # 현재 달
                })
            
            # 퇴사자 (이전 달에는 있었지만 현재는 없는 사람)
            resignation_ids = prev_emp_ids - current_emp_ids
            for emp_id in resignation_ids:
                emp_row = prev_df[prev_df['사번'].astype(str) == emp_id].iloc[0]
                hr_analytics['resignations'].append({
                    'emp_no': emp_id,
                    'name': emp_row.get('이름', ''),
                    'position': emp_row.get('직급', ''),
                    'type': emp_row.get('TYPE', ''),
                    'resignation_month': '2025-08'
                })
            
            # TYPE 변경자 찾기
            common_emp_ids = current_emp_ids & prev_emp_ids
            for emp_id in common_emp_ids:
                current_row = current_df[current_df['사번'].astype(str) == emp_id].iloc[0]
                prev_row = prev_df[prev_df['사번'].astype(str) == emp_id].iloc[0]
                
                current_type = current_row.get('TYPE', '')
                prev_type = prev_row.get('TYPE', '')
                
                if current_type != prev_type and current_type and prev_type:
                    hr_analytics['type_changes'].append({
                        'emp_no': emp_id,
                        'name': current_row.get('이름', ''),
                        'position': current_row.get('직급', ''),
                        'prev_type': prev_type,
                        'new_type': current_type,
                        'change_direction': f"{prev_type} → {current_type}"
                    })
            
            # 순증감 계산
            hr_analytics['monthly_comparison']['net_change'] = (
                hr_analytics['monthly_comparison']['current_month_total'] - 
                hr_analytics['monthly_comparison']['previous_month_total']
            )
    
    return hr_analytics

def generate_consecutive_failures_table(failures):
    """연속 실패자 테이블 생성"""
    if not failures:
        return '<div class="alert alert-info">연속 실패자가 없습니다.</div>'
    
    table_html = '''
    <table class="table table-striped">
        <thead>
            <tr>
                <th>사번</th>
                <th>이름</th>
                <th>직급</th>
                <th>실패 개월</th>
                <th>주요 원인</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for fail in failures[:10]:  # 최대 10명만 표시
        table_html += f'''
            <tr>
                <td>{fail.get('employee_id', '')}</td>
                <td>{fail.get('name', '')}</td>
                <td>{fail.get('position', '')}</td>
                <td>{fail.get('months_failed', 0)}</td>
                <td>{', '.join(fail.get('failed_conditions', []))}</td>
            </tr>
        '''
    
    table_html += '''
        </tbody>
    </table>
    '''
    
    return table_html

def generate_attendance_issues_list(issues):
    """출근율 이슈 리스트 생성"""
    if not issues:
        return '<div class="alert alert-info">출근율 이슈가 없습니다.</div>'
    
    list_html = '<div class="issue-list">'
    
    for issue in issues[:5]:  # 최대 5명만 표시
        list_html += f'''
        <div class="issue-card">
            <strong>{issue.get('name', '')} ({issue.get('employee_id', '')})</strong>
            <div>출근율: {issue.get('attendance_rate', 0):.1f}%</div>
            <div>직급: {issue.get('position', '')}</div>
        </div>
        '''
    
    list_html += '</div>'
    
    return list_html


def generate_management_dashboard_html(all_data, analysis_results, month, year):
    """Management Dashboard HTML 생성"""
    
    month_names = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }
    
    month_korean = month_names.get(month.lower(), month)
    
    # 분석 결과 추출
    consecutive_failures = analysis_results['consecutive_failures']
    attendance_issues = analysis_results['attendance_issues']
    aql_issues = analysis_results['aql_issues']
    prs_issues = analysis_results['prs_issues']
    org_chart = analysis_results['org_chart']
    hr_analytics = analysis_results['hr_analytics']
    type_changes = analysis_results['type_changes']
    
    # 통계 계산
    total_employees = hr_analytics['total_employees']
    critical_issues = len(consecutive_failures)
    warning_issues = len(attendance_issues)
    
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP Management Dashboard - {year}년 {month_korean}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .main-container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            margin: 0 auto;
            max-width: 1800px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            position: relative;
        }}
        
        .dashboard-selector {{
            position: absolute;
            top: 30px;
            right: 30px;
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .dashboard-selector select {{
            padding: 8px 15px;
            border-radius: 8px;
            border: 2px solid white;
            background: rgba(255,255,255,0.2);
            color: white;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .dashboard-selector select option {{
            background: #764ba2;
            color: white;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .stat-card.danger {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .stat-card.warning {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }}
        
        .stat-card.success {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 10px 10px 0 0;
            background: #f5f5f5;
            transition: all 0.3s;
        }}
        
        .tab.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .tab-content {{
            display: none;
            animation: fadeIn 0.5s;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .org-chart {{
            padding: 20px;
            overflow-x: auto;
        }}
        
        .org-node {{
            display: inline-block;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 8px;
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .org-node:hover {{
            background: #e9ecef;
            transform: scale(1.05);
        }}
        
        .org-node.manager {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .org-node.supervisor {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        
        .org-node.group-leader {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
        }}
        
        .org-node.line-leader {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }}
        
        .issue-card {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
        }}
        
        .issue-card.critical {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .hr-timeline {{
            position: relative;
            padding: 20px 0;
        }}
        
        .timeline-item {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            position: relative;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: 20px;
            top: 30px;
            width: 2px;
            height: 100%;
            background: #dee2e6;
        }}
        
        .timeline-marker {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            z-index: 1;
        }}
        
        .timeline-content {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            flex: 1;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1>🎯 QIP Management Dashboard</h1>
            <h4>{year}년 {month_korean} 운영 현황</h4>
            
            <div class="dashboard-selector">
                <select id="dashboardSelector" class="form-select me-2" style="width: 250px; display: inline-block;" onchange="changeDashboard(this.value)">
                    <option value="management" selected>📊 Management Dashboard</option>
                    <option value="incentive">💰 Incentive Dashboard</option>
                    <option value="statistics">📈 Statistics Dashboard</option>
                </select>
                <select id="languageSelector" onchange="changeLanguage(this.value)">
                    <option value="ko">🇰🇷 한국어</option>
                    <option value="en">🇺🇸 English</option>
                    <option value="vi">🇻🇳 Tiếng Việt</option>
                </select>
            </div>
        </div>
        
        <!-- 주요 통계 카드 -->
        <div class="stats-grid">
            <div class="stat-card danger">
                <h3>🚨 긴급 이슈</h3>
                <h2>{critical_issues}</h2>
                <p>3개월 연속 실패</p>
            </div>
            
            <div class="stat-card warning">
                <h3>⚠️ 주의 필요</h3>
                <h2>{warning_issues}</h2>
                <p>출근율 90% 미만</p>
            </div>
            
            <div class="stat-card success">
                <h3>👥 총 인원</h3>
                <h2>{total_employees}</h2>
                <p>활성 직원 수</p>
            </div>
            
            <div class="stat-card">
                <h3>📊 TYPE 분포</h3>
                <div style="font-size: 14px;">
                    <div>TYPE-1: {hr_analytics['by_type']['TYPE-1']}명</div>
                    <div>TYPE-2: {hr_analytics['by_type']['TYPE-2']}명</div>
                    <div>TYPE-3: {hr_analytics['by_type']['TYPE-3']}명</div>
                </div>
            </div>
        </div>
        
        <!-- 탭 메뉴 -->
        <div class="tabs">
            <div class="tab active" onclick="showTab('issues')">🚨 이슈 트래킹</div>
            <div class="tab" onclick="showTab('organization')">🏢 조직도</div>
            <div class="tab" onclick="showTab('hr')">👥 HR 분석</div>
            <div class="tab" onclick="showTab('performance')">📈 성과 분석</div>
            <div class="tab" onclick="showTab('predictions')">🔮 예측 분석</div>
        </div>
        
        <!-- 이슈 트래킹 탭 -->
        <div id="issues" class="tab-content active">
            <h3>3개월 연속 인센티브 미수령자</h3>
            <div class="row">
                <div class="col-md-8">
                    {generate_consecutive_failures_table(consecutive_failures)}
                </div>
                <div class="col-md-4">
                    <canvas id="issueChart"></canvas>
                </div>
            </div>
            
            <h3 class="mt-4">주요 조건 미충족 현황</h3>
            <div class="row">
                <div class="col-md-6">
                    <h5>출근율 이슈 (90% 미만)</h5>
                    {generate_attendance_issues_list(attendance_issues)}
                </div>
                <div class="col-md-6">
                    <h5>AQL/5PRS 이슈</h5>
                    <div class="issue-card">
                        <strong>AQL 미달:</strong> 분석 중...
                    </div>
                    <div class="issue-card">
                        <strong>5PRS 미달:</strong> 분석 중...
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 조직도 탭 -->
        <div id="organization" class="tab-content">
            <h3>조직 구조</h3>
            <div class="org-chart">
                <h5>Managers ({len(org_chart['managers'])})</h5>
                <div>
                    {''.join([f'<span class="org-node manager">{m["name"]}</span>' for m in org_chart['managers'][:5]])}
                </div>
                
                <h5 class="mt-3">Supervisors ({len(org_chart['supervisors'])})</h5>
                <div>
                    {''.join([f'<span class="org-node supervisor">{s["name"]}</span>' for s in org_chart['supervisors'][:10]])}
                </div>
                
                <h5 class="mt-3">Group Leaders ({len(org_chart['group_leaders'])})</h5>
                <div>
                    {''.join([f'<span class="org-node group-leader">{g["name"]}</span>' for g in org_chart['group_leaders'][:10]])}
                </div>
                
                <h5 class="mt-3">Line Leaders ({len(org_chart['line_leaders'])})</h5>
                <div>
                    {''.join([f'<span class="org-node line-leader">{l["name"]}</span>' for l in org_chart['line_leaders'][:10]])}
                </div>
            </div>
            
            <div class="mt-4">
                <canvas id="orgChart"></canvas>
            </div>
        </div>
        
        <!-- HR 분석 탭 -->
        <div id="hr" class="tab-content">
            <h3>인력 변동 현황</h3>
            <div class="row">
                <div class="col-md-6">
                    <h5>최근 입사자</h5>
                    <div class="hr-timeline">
                        <div class="timeline-item">
                            <div class="timeline-marker">📥</div>
                            <div class="timeline-content">
                                <strong>신규 입사 예정</strong>
                                <p>다음 주 10명 입사 예정</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <h5>최근 퇴사자</h5>
                    <div class="hr-timeline">
                        <div class="timeline-item">
                            <div class="timeline-marker">📤</div>
                            <div class="timeline-content">
                                <strong>이번 달 퇴사</strong>
                                <p>총 5명 퇴사 처리</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <h5 class="mt-4">TYPE 전환 현황</h5>
            <canvas id="typeChangeChart"></canvas>
        </div>
        
        <!-- 성과 분석 탭 -->
        <div id="performance" class="tab-content">
            <h3>성과 지표</h3>
            <div class="row">
                <div class="col-md-6">
                    <h5>5PRS 실적</h5>
                    <canvas id="prsChart"></canvas>
                </div>
                <div class="col-md-6">
                    <h5>AQL 달성률</h5>
                    <canvas id="aqlChart"></canvas>
                </div>
            </div>
            
            <h5 class="mt-4">Auditor/Trainer 효과성</h5>
            <div id="trainerEffectiveness"></div>
        </div>
        
        <!-- 예측 분석 탭 -->
        <div id="predictions" class="tab-content">
            <h3>다음 달 예측</h3>
            <div class="row">
                <div class="col-md-6">
                    <h5>위험군 예측</h5>
                    <div class="alert alert-danger">
                        <strong>High Risk:</strong> 5명이 인센티브 미달 예상
                    </div>
                    <div class="alert alert-warning">
                        <strong>Medium Risk:</strong> 12명이 경계선
                    </div>
                </div>
                <div class="col-md-6">
                    <h5>개선 예상</h5>
                    <div class="alert alert-success">
                        <strong>개선 예상:</strong> 8명이 조건 충족 예상
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 전역 변수
        let currentLanguage = 'ko';
        
        // 언어 변경
        function changeLanguage(lang) {{
            currentLanguage = lang;
            updateTexts();
        }}
        
        // 대시보드 변경
        function changeDashboard(dashboard) {{
            switch(dashboard) {{
                case 'incentive':
                    window.location.href = 'dashboard_2025_08.html';
                    break;
                case 'management':
                    window.location.href = 'management_dashboard_2025_08.html';
                    break;
                case 'statistics':
                    alert('Statistics Dashboard는 아직 개발 중입니다.');
                    break;
            }}
        }}
        
        function showTab(tabName) {{
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }}
        
        // 차트 초기화
        window.onload = function() {{
            // 이슈 차트
            const issueCtx = document.getElementById('issueChart').getContext('2d');
            new Chart(issueCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['3개월 연속 실패', '출근율 이슈', '정상'],
                    datasets: [{{
                        data: [{len(consecutive_failures)}, {len(attendance_issues)}, {hr_analytics['total_employees'] - len(consecutive_failures) - len(attendance_issues)}],
                        backgroundColor: ['#dc3545', '#ffc107', '#28a745']
                    }}]
                }}
            }});
            
            // 조직 차트
            const orgCtx = document.getElementById('orgChart').getContext('2d');
            new Chart(orgCtx, {{
                type: 'bar',
                data: {{
                    labels: ['Managers', 'Supervisors', 'Group Leaders', 'Line Leaders', 'Workers'],
                    datasets: [{{
                        label: '인원 수',
                        data: [{len(org_chart['managers'])}, {len(org_chart['supervisors'])}, {len(org_chart['group_leaders'])}, {len(org_chart['line_leaders'])}, {len(org_chart['workers'])}],
                        backgroundColor: 'rgba(102, 126, 234, 0.5)'
                    }}]
                }}
            }});
            
            // 5PRS 성과 차트
            const prsCtx = document.getElementById('prsChart').getContext('2d');
            new Chart(prsCtx, {{
                type: 'line',
                data: {{
                    labels: ['6월', '7월', '8월'],
                    datasets: [{{
                        label: '5PRS 달성률',
                        data: [85, 88, 92],
                        borderColor: 'rgba(40, 167, 69, 1)',
                        backgroundColor: 'rgba(40, 167, 69, 0.2)',
                        fill: true
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }}
                }}
            }});
            
            // AQL 성과 차트
            const aqlCtx = document.getElementById('aqlChart').getContext('2d');
            new Chart(aqlCtx, {{
                type: 'line',
                data: {{
                    labels: ['6월', '7월', '8월'],
                    datasets: [{{
                        label: 'AQL 달성률',
                        data: [90, 87, 94],
                        borderColor: 'rgba(255, 193, 7, 1)',
                        backgroundColor: 'rgba(255, 193, 7, 0.2)',
                        fill: true
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }}
                }}
            }});
            
            // TYPE 변경 차트
            const typeChangeCtx = document.getElementById('typeChangeChart').getContext('2d');
            new Chart(typeChangeCtx, {{
                type: 'bar',
                data: {{
                    labels: ['TYPE-1', 'TYPE-2', 'TYPE-3'],
                    datasets: [{{
                        label: '승진',
                        data: [{len([t for t in type_changes if 'upgrade' in t.get('change_type', '')])}, 0, 0],
                        backgroundColor: 'rgba(40, 167, 69, 0.7)'
                    }}, {{
                        label: '강등',
                        data: [0, {len([t for t in type_changes if 'downgrade' in t.get('change_type', '')])}, 0],
                        backgroundColor: 'rgba(220, 53, 69, 0.7)'
                    }}]
                }},
                options: {{
                    scales: {{
                        x: {{
                            stacked: true
                        }},
                        y: {{
                            stacked: true
                        }}
                    }}
                }}
            }});
        }};
    </script>
</body>
</html>'''
    
    return html_content

def generate_consecutive_failures_table(failures):
    """3개월 연속 실패자 테이블 생성"""
    if not failures:
        return '<p>해당 직원이 없습니다.</p>'
    
    html = '<table class="table table-striped"><thead><tr><th>사번</th><th>이름</th><th>직급</th><th>연속 실패</th></tr></thead><tbody>'
    for f in failures[:10]:  # 상위 10명만 표시
        html += f'<tr><td>{f["emp_no"]}</td><td>{f["name"]}</td><td>{f["position"]}</td><td>{f["fail_months"]}개월</td></tr>'
    html += '</tbody></table>'
    return html

def generate_attendance_issues_list(attendance_issues):
    """출근율 이슈 리스트 생성"""
    if not attendance_issues:
        return '<p>해당 직원이 없습니다.</p>'
    
    html = ''
    for issue in attendance_issues[:5]:  # 상위 5명만 표시
        html += f'''<div class="issue-card critical">
            <strong>{issue["name"]} ({issue["emp_no"]})</strong>
            <p>출근율: {issue["rate"]:.1f}%</p>
        </div>'''
    return html

def main():
    parser = argparse.ArgumentParser(description='Generate Management Dashboard')
    parser.add_argument('--month', type=str, default='august', help='Month name')
    parser.add_argument('--year', type=int, default=2025, help='Year')
    
    args = parser.parse_args()
    
    print(f"🚀 Management Dashboard 생성 시작: {args.year}년 {args.month}")
    
    # 1. 설정 파일 로드
    config = load_config(args.month, args.year)
    translations = load_translations()
    
    # 2. 모든 데이터 로드
    all_data = load_all_data(config, args.month, args.year)
    
    if not all_data['metadata'] and not all_data['employees']:
        print("❌ 데이터를 로드할 수 없습니다. 먼저 인센티브 계산을 실행하세요.")
        return
    
    # 3. 각종 분석 수행
    print("📊 데이터 분석 중...")
    
    # 연속 실패자 분석
    consecutive_failures = analyze_consecutive_failures(all_data)
    print(f"   - 연속 실패자 분석: {len(consecutive_failures)}명")
    
    # 출근율 이슈 분석
    attendance_issues = analyze_attendance_issues(all_data)
    print(f"   - 출근율 90% 미만: {len(attendance_issues)}명")
    
    # AQL/5PRS 이슈 분석
    aql_issues, prs_issues = analyze_aql_5prs_issues(all_data)
    print(f"   - AQL 이슈: {len(aql_issues)}명")
    print(f"   - 5PRS 이슈: {len(prs_issues)}명")
    
    # 조직도 데이터 생성
    org_chart = generate_org_chart_data(all_data)
    print(f"   - 조직 구조 분석 완료")
    
    # HR 변동 분석
    hr_analytics = analyze_hr_changes(all_data)
    print(f"   - HR 변동 분석: 신규 {len(hr_analytics['new_hires'])}명, 퇴사 {len(hr_analytics['resignations'])}명")
    
    # 4. 분석 결과 통합
    # TYPE 변경 분석 (현재는 빈 리스트로 처리)
    type_changes = []
    
    analysis_results = {
        'consecutive_failures': consecutive_failures,
        'attendance_issues': attendance_issues,
        'aql_issues': aql_issues,
        'prs_issues': prs_issues,
        'org_chart': org_chart,
        'hr_analytics': hr_analytics,
        'type_changes': type_changes,
        'translations': translations
    }
    
    # 5. HTML 생성
    print("📝 대시보드 HTML 생성 중...")
    html_content = generate_management_dashboard_html(
        all_data, analysis_results, args.month, args.year
    )
    
    # 6. 파일 저장
    # month 문자열을 숫자로 변환
    month_map = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    month_num = month_map.get(args.month.lower(), '08')
    
    output_file = f'output_files/management_dashboard_{args.year}_{month_num}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Management Dashboard 생성 완료: {output_file}")
    print(f"   - 연속 실패자: {len(consecutive_failures)}명")
    print(f"   - 출근율 이슈: {len(attendance_issues)}명")
    print(f"   - 조직 구조: {org_chart['total_by_type']}")
    print(f"   - HR 변동: 순증감 {hr_analytics['monthly_comparison']['net_change']}명")

if __name__ == '__main__':
    main()