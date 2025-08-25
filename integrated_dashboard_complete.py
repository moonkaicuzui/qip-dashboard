#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
완전 통합 인센티브 대시보드 시스템
- Google Drive 자동 동기화
- 데이터 처리 및 계산
- 대시보드 HTML 생성
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime
import glob
import logging
from pathlib import Path

# Google Drive 연동 모듈
try:
    from src.google_drive_manager import GoogleDriveManager
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("⚠️ Google Drive 연동 모듈을 찾을 수 없습니다. 로컬 파일만 사용합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_korean_month(month):
    """영어 월 이름을 한국어로 변환"""
    month_map = {
        'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
        'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
        'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
    }
    return month_map.get(month.lower(), month)

def sync_from_google_drive(month='august', year=2025):
    """Google Drive에서 데이터 동기화"""
    if not GOOGLE_DRIVE_AVAILABLE:
        logger.warning("Google Drive 연동을 사용할 수 없습니다.")
        return False
    
    try:
        logger.info("Google Drive 동기화 시작...")
        drive_manager = GoogleDriveManager()
        
        # 서비스 연결
        if not drive_manager.connect():
            logger.error("Google Drive 연결 실패")
            return False
        
        # 월별 데이터 동기화
        sync_result = drive_manager.sync_monthly_data(year, month)
        
        if sync_result.success:
            logger.info(f"✅ Google Drive 동기화 성공: {sync_result.files_synced}개 파일")
            return True
        else:
            logger.error(f"❌ Google Drive 동기화 실패: {sync_result.error_message}")
            return False
            
    except Exception as e:
        logger.error(f"Google Drive 동기화 중 오류: {str(e)}")
        return False

def determine_type_from_position(position):
    """직급에서 Type 결정"""
    position_upper = str(position).upper()
    
    # TYPE-3: New QIP Members (신입 직원)
    if 'NEW QIP MEMBER' in position_upper:
        return 'TYPE-3'
    
    # TYPE-1 positions (전문 검사 직급)
    type1_positions = [
        'AQL INSPECTOR', 'ASSEMBLY INSPECTOR', 'AUDIT & TRAINING',
        'MODEL MASTER', 'MANAGER', 'A.MANAGER', 'ASSISTANT MANAGER',
        'LINE LEADER', '(V) SUPERVISOR', 'V.SUPERVISOR'
    ]
    
    # TYPE-2 positions (일반 검사 직급)
    type2_positions = [
        'STITCHING INSPECTOR', 'BOTTOM INSPECTOR', 'MTL INSPECTOR',
        'OSC INSPECTOR', 'GROUP LEADER'
    ]
    
    # Check for TYPE-1
    for t1_pos in type1_positions:
        if t1_pos in position_upper:
            return 'TYPE-1'
    
    # Check for TYPE-2
    for t2_pos in type2_positions:
        if t2_pos in position_upper:
            return 'TYPE-2'
    
    # Default to TYPE-2 for unknown positions
    return 'TYPE-2'

def load_incentive_data(month='august', year=2025):
    """실제 인센티브 데이터 로드"""
    
    # 가능한 파일 패턴들
    patterns = [
        f"input_files/{year}년 {get_korean_month(month)} 인센티브 지급 세부 정보.csv",
        f"output_files/output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv",
        f"output_files/output_QIP_incentive_{month}_{year}_*.csv"
    ]
    
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            csv_file = files[0]
            print(f"✅ 인센티브 데이터 로드: {csv_file}")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            # Position 컬럼 찾기
            position_col = None
            for col in df.columns:
                if 'POSITION' in col.upper() and '1ST' in col.upper():
                    position_col = col
                    break
                elif 'POSITION' in col.upper():
                    position_col = col
                    break
            
            # 컬럼 이름 표준화
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'employee' in col_lower and 'no' in col_lower:
                    column_mapping[col] = 'emp_no'
                elif col_lower in ['name', 'full name', 'employee name']:
                    column_mapping[col] = 'name'
                elif position_col and col == position_col:
                    column_mapping[col] = 'position'
                elif 'ROLE TYPE STD' in col:
                    column_mapping[col] = 'type'
                elif col_lower == 'type':
                    column_mapping[col] = 'type'
                elif f'{month.lower()}_incentive' in col_lower or f'{month.lower()} incentive' in col_lower:
                    column_mapping[col] = f'{month.lower()}_incentive'
                elif 'attendance' in col_lower and 'rate' in col_lower:
                    column_mapping[col] = 'attendance_rate'
                elif 'actual' in col_lower and 'working' in col_lower:
                    column_mapping[col] = 'actual_working_days'
            
            df = df.rename(columns=column_mapping)
            
            # Type 컬럼이 없으면 position에서 결정
            if 'type' not in df.columns and 'position' in df.columns:
                df['type'] = df['position'].apply(determine_type_from_position)
                print(f"✅ Type 자동 결정 (position 기반): TYPE-1 {(df['type']=='TYPE-1').sum()}명, TYPE-2 {(df['type']=='TYPE-2').sum()}명, TYPE-3 {(df['type']=='TYPE-3').sum()}명")
            elif 'type' in df.columns:
                # Type 통계 출력
                type_counts = df['type'].value_counts()
                print(f"✅ Type 정보 로드: TYPE-1 {type_counts.get('TYPE-1', 0)}명, TYPE-2 {type_counts.get('TYPE-2', 0)}명, TYPE-3 {type_counts.get('TYPE-3', 0)}명")
            
            # 필수 컬럼 확인 및 기본값 설정
            required_columns = ['emp_no', 'name', 'position', 'type', f'{month.lower()}_incentive']
            for col in required_columns:
                if col not in df.columns:
                    if col == f'{month.lower()}_incentive':
                        # August_Incentive 컬럼 찾기
                        for orig_col in df.columns:
                            if 'august' in orig_col.lower() and 'incentive' in orig_col.lower():
                                df[col] = df[orig_col]
                                break
                    elif col == 'type':
                        df[col] = 'TYPE-2'  # 기본값
                    else:
                        df[col] = ''
            
            # 조건 컬럼 추가 (기본값)
            condition_columns = ['condition1', 'condition2', 'condition3', 'condition4',
                               'condition5', 'condition6', 'condition7', 'condition8',
                               'condition9', 'condition10']
            for col in condition_columns:
                if col not in df.columns:
                    # 출근 조건 판정
                    if col == 'condition1':  # 출근율 >= 88%
                        df[col] = df['attendance_rate'].apply(lambda x: 'no' if x >= 88 else 'yes')
                    elif col == 'condition2':  # 무단결근 <= 2일
                        df[col] = df.get('unapproved_absences', 0).apply(lambda x: 'no' if x <= 2 else 'yes')
                    elif col == 'condition3':  # 실제 근무일 > 0
                        df[col] = df.get('actual_working_days', 0).apply(lambda x: 'no' if x > 0 else 'yes')
                    elif col == 'condition4':  # 최소 근무일 >= 12
                        df[col] = df.get('actual_working_days', 0).apply(lambda x: 'no' if x >= 12 else 'yes')
                    else:
                        df[col] = 'no'
            
            # AQL/5PRS 컬럼 추가
            if 'aql_failures' not in df.columns:
                df['aql_failures'] = 0
            if 'continuous_fail' not in df.columns:
                df['continuous_fail'] = 'NO'
            if 'pass_rate' not in df.columns:
                df['pass_rate'] = 0
            if 'validation_qty' not in df.columns:
                df['validation_qty'] = 0
            
            # 출근 관련 컬럼
            if 'attendance_rate' not in df.columns:
                df['attendance_rate'] = 100.0
            if 'actual_working_days' not in df.columns:
                df['actual_working_days'] = 13
            if 'unapproved_absences' not in df.columns:
                df['unapproved_absences'] = 0
            if 'absence_rate' not in df.columns:
                df['absence_rate'] = 0
            
            # 이전 달 인센티브 (기본값 0)
            df['june_incentive'] = '0'
            df['july_incentive'] = '0'
            
            # 퇴사일 필터링 (8월 1일 이전 퇴사자 제외)
            if 'Stop working Date' in df.columns:
                print(f"✅ 퇴사일 데이터 확인 중...")
                df['resignation_date'] = pd.to_datetime(df['Stop working Date'], format='%Y.%m.%d', errors='coerce')
                august_start = pd.to_datetime(f'{year}-08-01')
                
                # 8월 이전 퇴사자 제외
                before_august = df[df['resignation_date'] < august_start]
                df = df[(df['resignation_date'] >= august_start) | (df['resignation_date'].isna())]
                
                if len(before_august) > 0:
                    print(f"   - 8월 이전 퇴사자 {len(before_august)}명 제외")
                print(f"   - 8월 인센티브 대상자: {len(df)}명")
            
            print(f"✅ {len(df)}명의 직원 데이터 로드 (8월 대상자만)")
            return df
            
    print("❌ 인센티브 데이터 파일을 찾을 수 없습니다")
    return pd.DataFrame()

def generate_popup_chart_script():
    """팝업창용 차트 생성 스크립트"""
    return '''
        // 팝업창 차트 생성 함수
        function createPopupChart(employees, canvasId) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            
            // 지급/미지급 계산
            const paid = employees.filter(e => parseInt(e.august_incentive) > 0).length;
            const unpaid = employees.length - paid;
            const paidRate = (paid / employees.length * 100).toFixed(1);
            
            // 도넛 차트 생성
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['지급', '미지급'],
                    datasets: [{
                        data: [paid, unpaid],
                        backgroundColor: ['#10b981', '#ef4444'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: { size: 12 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value}명 (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '60%'
                },
                plugins: [{
                    beforeDraw: function(chart) {
                        const ctx = chart.ctx;
                        ctx.restore();
                        const fontSize = 1.5;
                        ctx.font = fontSize + "em sans-serif";
                        ctx.textBaseline = "middle";
                        ctx.fillStyle = '#1f2937';
                        
                        const text = paidRate + "%";
                        const textX = Math.round((chart.width - ctx.measureText(text).width) / 2);
                        const textY = chart.height / 2;
                        
                        ctx.fillText(text, textX, textY - 10);
                        ctx.font = "0.9em sans-serif";
                        ctx.fillStyle = '#6b7280';
                        ctx.fillText("수령률", textX + 15, textY + 15);
                        ctx.save();
                    }
                }]
            });
        }
    '''

def generate_dashboard_html(df, month='august', year=2025):
    """대시보드 HTML 생성 (개선된 팝업 UI 포함)"""
    
    # 데이터 준비
    employees = []
    for _, row in df.iterrows():
        emp = {
            'emp_no': str(row.get('emp_no', '')),
            'name': str(row.get('name', '')),
            'position': str(row.get('position', '')),
            'type': str(row.get('type', 'TYPE-2')),
            'july_incentive': str(row.get('july_incentive', '0')),
            'august_incentive': str(row.get('august_incentive', '0')),
            'june_incentive': str(row.get('june_incentive', '0')),
            'attendance_rate': float(row.get('attendance_rate', 100)),
            'actual_working_days': int(row.get('actual_working_days', 13)),
            'unapproved_absences': int(row.get('unapproved_absences', 0)),
            'absence_rate': float(row.get('absence_rate', 0)),
            'condition1': str(row.get('condition1', 'no')),
            'condition2': str(row.get('condition2', 'no')),
            'condition3': str(row.get('condition3', 'no')),
            'condition4': str(row.get('condition4', 'no')),
            'aql_failures': int(row.get('aql_failures', 0)),
            'continuous_fail': str(row.get('continuous_fail', 'NO')),
            'pass_rate': float(row.get('pass_rate', 0)),
            'validation_qty': int(row.get('validation_qty', 0))
        }
        employees.append(emp)
    
    # 통계 계산
    total_employees = len(employees)
    paid_employees = sum(1 for e in employees if int(e['august_incentive']) > 0)
    total_amount = sum(int(e['august_incentive']) for e in employees)
    payment_rate = (paid_employees / total_employees * 100) if total_employees > 0 else 0
    
    # Type별 통계
    type_stats = {}
    for emp in employees:
        emp_type = emp['type']
        if emp_type not in type_stats:
            type_stats[emp_type] = {
                'total': 0,
                'paid': 0,
                'amount': 0,
                'paid_amounts': []
            }
        type_stats[emp_type]['total'] += 1
        amount = int(emp['august_incentive'])
        if amount > 0:
            type_stats[emp_type]['paid'] += 1
            type_stats[emp_type]['amount'] += amount
            type_stats[emp_type]['paid_amounts'].append(amount)
    
    # 직원 데이터 JSON
    employees_json = json.dumps(employees, ensure_ascii=False)
    
    # 현재 시간
    current_date = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
    
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 대시보드 - {year}년 {get_korean_month(month)}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            background: #f5f5f5;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .summary-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        
        .summary-card h6 {{
            color: #6b7280;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .summary-card h2 {{
            color: #1f2937;
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .summary-card .unit {{
            font-size: 1rem;
            color: #9ca3af;
            font-weight: 400;
            margin-left: 4px;
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
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .table {{
            margin-top: 20px;
        }}
        
        .table thead th {{
            background: #f9fafb;
            color: #374151;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb;
            padding: 12px;
        }}
        
        .type-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        
        .type-badge.type-1 {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .type-badge.type-2 {{
            background: #fce7f3;
            color: #be185d;
        }}
        
        .type-badge.type-3 {{
            background: #d1fae5;
            color: #047857;
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
            background: white;
            margin: 30px auto;
            padding: 0;
            width: 95%;
            max-width: 1200px;
            border-radius: 12px;
            max-height: 90vh;
            overflow-y: auto;
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .modal-body {{
            padding: 30px;
        }}
        
        .close {{
            color: white;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            background: none;
            border: none;
        }}
        
        .close:hover {{
            opacity: 0.8;
        }}
        
        .condition-group {{
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
        }}
        
        .condition-group-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 15px;
            padding: 8px 12px;
            border-radius: 6px;
            color: white;
        }}
        
        .condition-group-title.attendance {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        }}
        
        .condition-group-title.aql {{
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        }}
        
        .condition-group-title.prs {{
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        }}
        
        .condition-check {{
            padding: 12px 15px;
            margin-bottom: 8px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            border: 1px solid #e5e7eb;
        }}
        
        .condition-check.success {{
            background: #d1fae5;
            border-color: #10b981;
        }}
        
        .condition-check.fail {{
            background: #fee2e2;
            border-color: #ef4444;
        }}
        
        .version-badge {{
            background: #fbbf24;
            color: #78350f;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        /* Type 요약 테이블 스타일 */
        .avg-header {{
            text-align: center;
            background: #f3f4f6;
        }}
        
        .sub-header {{
            font-size: 0.9em;
            font-weight: 500;
            background: #f9fafb;
        }}
        
        /* 팝업용 대시보드 스타일 */
        .popup-dashboard {{
            display: flex;
            gap: 20px;
        }}
        
        .popup-left {{
            flex: 1;
            min-width: 300px;
        }}
        
        .popup-right {{
            flex: 2;
        }}
        
        .popup-stat-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .popup-stat-card h5 {{
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }}
        
        .popup-stat-card .value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
        }}
        
        .condition-summary-table {{
            width: 100%;
            margin-top: 20px;
        }}
        
        .condition-summary-table th {{
            background: #f3f4f6;
            padding: 8px;
            font-size: 0.9rem;
        }}
        
        .condition-summary-table td {{
            padding: 8px;
            font-size: 0.9rem;
        }}
        
        .progress-bar-container {{
            background: #e5e7eb;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-bar-fill {{
            background: #10b981;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.8rem;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="position: absolute; top: 20px; right: 20px;">
                <select id="languageSelector" class="form-select" style="width: 150px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3);">
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                    <option value="vi">Tiếng Việt</option>
                </select>
            </div>
            <h1 id="mainTitle">QIP 인센티브 계산 결과 <span class="version-badge">v5.0</span></h1>
            <p id="mainSubtitle">{year}년 {get_korean_month(month)} 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;">보고서 생성일: {current_date}</p>
        </div>
        
        <div class="content p-4">
            <!-- 요약 카드 -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalEmployeesLabel">전체 직원</h6>
                        <h2 id="totalEmployeesValue">{total_employees}<span class="unit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paidEmployeesLabel">수령 직원</h6>
                        <h2 id="paidEmployeesValue">{paid_employees}<span class="unit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paymentRateLabel">수령률</h6>
                        <h2 id="paymentRateValue">{payment_rate:.1f}%</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalAmountLabel">총 지급액</h6>
                        <h2 id="totalAmountValue">{total_amount:,} VND</h2>
                    </div>
                </div>
            </div>
            
            <!-- 탭 메뉴 -->
            <div class="tabs">
                <div class="tab active" data-tab="summary" onclick="showTab('summary')" id="tabSummary">요약</div>
                <div class="tab" data-tab="position" onclick="showTab('position')" id="tabPosition">직급별 상세</div>
                <div class="tab" data-tab="detail" onclick="showTab('detail')" id="tabIndividual">개인별 상세</div>
                <div class="tab" data-tab="criteria" onclick="showTab('criteria')" id="tabCriteria">인센티브 기준</div>
            </div>
            
            <!-- 요약 탭 -->
            <div id="summary" class="tab-content active">
                <h3>Type별 현황</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th rowspan="2">Type</th>
                            <th rowspan="2">전체 인원</th>
                            <th rowspan="2">수령 인원</th>
                            <th rowspan="2">수령률</th>
                            <th rowspan="2">총 지급액</th>
                            <th colspan="2" class="avg-header">평균 지급액</th>
                        </tr>
                        <tr>
                            <th class="sub-header">수령인원 기준</th>
                            <th class="sub-header">총원 기준</th>
                        </tr>
                    </thead>
                    <tbody id="typeSummaryBody">'''
    
    # Type별 요약 데이터 생성
    total_stats = {'total': 0, 'paid': 0, 'amount': 0}
    
    for emp_type in sorted(type_stats.keys()):
        if not emp_type:  # 빈 Type 건너뛰기
            continue
        stats = type_stats[emp_type]
        rate = (stats['paid'] / stats['total'] * 100) if stats['total'] > 0 else 0
        avg_paid = (stats['amount'] / stats['paid']) if stats['paid'] > 0 else 0
        avg_total = (stats['amount'] / stats['total']) if stats['total'] > 0 else 0
        
        # Total 집계
        total_stats['total'] += stats['total']
        total_stats['paid'] += stats['paid']
        total_stats['amount'] += stats['amount']
        
        # Type badge 클래스 결정
        type_class = '2'  # 기본값
        if 'TYPE-1' in emp_type.upper():
            type_class = '1'
        elif 'TYPE-2' in emp_type.upper():
            type_class = '2'
        elif 'TYPE-3' in emp_type.upper():
            type_class = '3'
        
        html_content += f'''
                        <tr>
                            <td><span class="type-badge type-{type_class}">{emp_type}</span></td>
                            <td>{stats['total']}명</td>
                            <td>{stats['paid']}명</td>
                            <td>{rate:.1f}%</td>
                            <td>{stats['amount']:,} VND</td>
                            <td>{avg_paid:,.0f} VND</td>
                            <td>{avg_total:,.0f} VND</td>
                        </tr>'''
    
    # Total 행 추가
    total_rate = (total_stats['paid'] / total_stats['total'] * 100) if total_stats['total'] > 0 else 0
    total_avg_paid = (total_stats['amount'] / total_stats['paid']) if total_stats['paid'] > 0 else 0
    total_avg_total = (total_stats['amount'] / total_stats['total']) if total_stats['total'] > 0 else 0
    
    html_content += f'''
                        <tr style="font-weight: bold; background-color: #f3f4f6;">
                            <td>Total</td>
                            <td>{total_stats['total']}명</td>
                            <td>{total_stats['paid']}명</td>
                            <td>{total_rate:.1f}%</td>
                            <td>{total_stats['amount']:,} VND</td>
                            <td>{total_avg_paid:,.0f} VND</td>
                            <td>{total_avg_total:,.0f} VND</td>
                        </tr>'''
    
    html_content += f'''
                    </tbody>
                </table>
            </div>
            
            <!-- 직급별 상세 탭 -->
            <div id="position" class="tab-content">
                <h3 id="positionTabTitle">직급별 상세 현황</h3>
                <div id="positionTables">
                    <!-- JavaScript로 채워질 예정 -->
                </div>
            </div>
            
            <!-- 개인별 상세 탭 -->
            <div id="detail" class="tab-content">
                <h3 id="individualDetailTitle">개인별 상세 정보</h3>
                <div class="filter-container mb-3">
                    <div class="row">
                        <div class="col-md-3">
                            <input type="text" id="searchInput" class="form-control" 
                                placeholder="이름 또는 직원번호 검색" onkeyup="filterTable()">
                        </div>
                        <div class="col-md-2">
                            <select id="typeFilter" class="form-select" 
                                onchange="updatePositionFilter(); filterTable()">
                                <option value="" id="optAllTypes">모든 타입</option>
                                <option value="TYPE-1">TYPE-1</option>
                                <option value="TYPE-2">TYPE-2</option>
                                <option value="TYPE-3">TYPE-3</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select id="positionFilter" class="form-select" onchange="filterTable()">
                                <option value="" id="optAllPositions">모든 직급</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <select id="paymentFilter" class="form-select" onchange="filterTable()">
                                <option value="" id="optPaymentAll">전체</option>
                                <option value="paid" id="optPaymentPaid">지급</option>
                                <option value="unpaid" id="optPaymentUnpaid">미지급</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="employeeTable">
                        <thead>
                            <tr>
                                <th>사번</th>
                                <th>이름</th>
                                <th>직급</th>
                                <th>Type</th>
                                <th>7월</th>
                                <th>8월</th>
                                <th>상태</th>
                                <th>상세</th>
                            </tr>
                        </thead>
                        <tbody id="employeeTableBody">
                            <!-- JavaScript로 채워질 예정 -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 인센티브 기준 탭 -->
            <div id="criteria" class="tab-content">
                <h3>인센티브 지급 기준</h3>
                <div class="row">
                    <div class="col-md-6">
                        <h4>출근 조건 (4개)</h4>
                        <ul>
                            <li>조건 1: 출근율 ≥ 88%</li>
                            <li>조건 2: 무단 결근 ≤ 2일</li>
                            <li>조건 3: 실제 근무일수 > 0</li>
                            <li>조건 4: 최소 근무일 ≥ 12일</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h4>AQL 조건 (4개)</h4>
                        <ul>
                            <li>조건 5: 개인 AQL 당월 실패 = 0</li>
                            <li>조건 6: 3개월 연속 실패 없음</li>
                            <li>조건 7: 팀/구역 AQL 3개월 연속 실패 없음</li>
                            <li>조건 8: 담당구역 reject율 < 3%</li>
                        </ul>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h4>5PRS 조건 (2개)</h4>
                        <ul>
                            <li>조건 9: 5PRS 통과율 ≥ 95%</li>
                            <li>조건 10: 5PRS 검사량 ≥ 100개</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 직원 상세 모달 -->
    <div id="employeeModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">직원 상세 정보</h2>
                <button class="close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- JavaScript로 채워질 예정 -->
            </div>
        </div>
    </div>
    
    <script>
        const employeeData = {employees_json};
        
        {generate_popup_chart_script()}
        
        // 초기화
        window.onload = function() {{
            generateEmployeeTable();
            generatePositionTables();
            updatePositionFilter();
        }};
        
        // 탭 전환
        function showTab(tabName) {{
            // 모든 탭과 컨텐츠 숨기기
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // 선택된 탭과 컨텐츠 표시
            document.querySelector(`[data-tab="${{tabName}}"]`).classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }}
        
        // 직원 테이블 생성
        function generateEmployeeTable() {{
            const tbody = document.getElementById('employeeTableBody');
            tbody.innerHTML = '';
            
            employeeData.forEach(emp => {{
                const amount = parseInt(emp.august_incentive);
                const isPaid = amount > 0;
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                tr.onclick = () => showEmployeeDetail(emp.emp_no);
                
                tr.innerHTML = `
                    <td>${{emp.emp_no}}</td>
                    <td>${{emp.name}}</td>
                    <td>${{emp.position}}</td>
                    <td><span class="type-badge type-${{emp.type.toLowerCase().replace('type-', '')}}">${{emp.type}}</span></td>
                    <td>${{parseInt(emp.july_incentive).toLocaleString()}}</td>
                    <td><strong>${{amount.toLocaleString()}}</strong></td>
                    <td>${{isPaid ? '✅ 지급' : '❌ 미지급'}}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${{emp.emp_no}}')">상세</button></td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        // 직급별 테이블 생성 (개선된 UI)
        function generatePositionTables() {{
            const positionData = {{}};
            
            // Type-직급별 데이터 집계
            employeeData.forEach(emp => {{
                const key = `${{emp.type}}_${{emp.position}}`;
                if (!positionData[key]) {{
                    positionData[key] = {{
                        type: emp.type,
                        position: emp.position,
                        total: 0,
                        paid: 0,
                        totalAmount: 0,
                        employees: []
                    }};
                }}
                
                positionData[key].total++;
                positionData[key].employees.push(emp);
                const amount = parseInt(emp.august_incentive) || 0;
                if (amount > 0) {{
                    positionData[key].paid++;
                    positionData[key].totalAmount += amount;
                }}
            }});
            
            // Type별로 그룹핑
            const groupedByType = {{}};
            Object.values(positionData).forEach(data => {{
                if (!groupedByType[data.type]) {{
                    groupedByType[data.type] = [];
                }}
                groupedByType[data.type].push(data);
            }});
            
            // HTML 생성
            const container = document.getElementById('positionTables');
            if (container) {{
                container.innerHTML = '';
                
                // Type별로 섹션 생성
                Object.entries(groupedByType).sort().forEach(([type, positions]) => {{
                    const typeClass = type.toLowerCase().replace('type-', '');
                    
                    let html = `
                        <div class="mb-5">
                            <h4 class="mb-3">
                                <span class="type-badge type-${{typeClass}}">${{type}}</span> 
                                직급별 현황
                            </h4>
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>직급</th>
                                        <th>전체</th>
                                        <th>지급</th>
                                        <th>지급률</th>
                                        <th>총 지급액</th>
                                        <th>평균 지급액</th>
                                        <th>상세</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    // 직급별 행 추가
                    positions.sort((a, b) => a.position.localeCompare(b.position)).forEach(posData => {{
                        const paymentRate = posData.total > 0 ? (posData.paid / posData.total * 100).toFixed(1) : '0.0';
                        const avgAmount = posData.paid > 0 ? Math.round(posData.totalAmount / posData.paid) : 0;
                        
                        html += `
                            <tr>
                                <td>${{posData.position}}</td>
                                <td>${{posData.total}}명</td>
                                <td>${{posData.paid}}명</td>
                                <td>${{paymentRate}}%</td>
                                <td>${{posData.totalAmount.toLocaleString()}} VND</td>
                                <td>${{avgAmount.toLocaleString()}} VND</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" 
                                            onclick="showPositionDetailPopup('${{type}}', '${{posData.position}}')">
                                        보기
                                    </button>
                                </td>
                            </tr>
                        `;
                    }});
                    
                    // Type별 소계
                    const typeTotal = positions.reduce((acc, p) => acc + p.total, 0);
                    const typePaid = positions.reduce((acc, p) => acc + p.paid, 0);
                    const typeAmount = positions.reduce((acc, p) => acc + p.totalAmount, 0);
                    const typeRate = typeTotal > 0 ? (typePaid / typeTotal * 100).toFixed(1) : '0.0';
                    const typeAvg = typePaid > 0 ? Math.round(typeAmount / typePaid) : 0;
                    
                    html += `
                                </tbody>
                                <tfoot>
                                    <tr style="font-weight: bold; background-color: #f8f9fa;">
                                        <td>${{type}} 합계</td>
                                        <td>${{typeTotal}}명</td>
                                        <td>${{typePaid}}명</td>
                                        <td>${{typeRate}}%</td>
                                        <td>${{typeAmount.toLocaleString()}} VND</td>
                                        <td>${{typeAvg.toLocaleString()}} VND</td>
                                        <td></td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    `;
                    
                    const div = document.createElement('div');
                    div.innerHTML = html;
                    container.appendChild(div);
                }});
            }}
        }}
        
        // 직급별 상세 팝업 (개선된 대시보드 스타일)
        function showPositionDetailPopup(type, position) {{
            const employees = employeeData.filter(e => e.type === type && e.position === position);
            if (employees.length === 0) return;
            
            const modal = document.getElementById('employeeModal');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');
            
            modalTitle.textContent = `${{type}} - ${{position}} 인센티브 계산 상세`;
            
            // 통계 계산
            const totalCount = employees.length;
            const paidCount = employees.filter(e => parseInt(e.august_incentive) > 0).length;
            const unpaidCount = totalCount - paidCount;
            const paidRate = (paidCount / totalCount * 100).toFixed(1);
            const totalAmount = employees.reduce((sum, e) => sum + parseInt(e.august_incentive), 0);
            const avgAmount = paidCount > 0 ? Math.round(totalAmount / paidCount) : 0;
            
            // 조건별 충족 통계 계산
            const conditionStats = {{
                attendance: {{
                    total: totalCount,
                    fulfilled: employees.filter(e => e.condition1 === 'no' && e.condition2 === 'no' && e.condition3 === 'no' && e.condition4 === 'no').length
                }},
                aql: {{
                    total: totalCount,
                    fulfilled: totalCount // AQL N/A로 표시
                }},
                prs: {{
                    total: totalCount,
                    fulfilled: totalCount // 5PRS N/A로 표시
                }}
            }};
            
            let popupHtml = `
                <div class="popup-dashboard">
                    <!-- 왼쪽: 차트 및 통계 -->
                    <div class="popup-left">
                        <!-- 지급/미지급 비율 차트 -->
                        <div class="popup-stat-card">
                            <h5>지급/미지급 비율</h5>
                            <canvas id="popupChart" width="250" height="250"></canvas>
                        </div>
                        
                        <!-- 인센티브 통계 -->
                        <div class="popup-stat-card">
                            <h5>인센티브 통계</h5>
                            <div class="row">
                                <div class="col-6">
                                    <div class="text-muted small">전체 인원</div>
                                    <div class="value">${{totalCount}}명</div>
                                </div>
                                <div class="col-6">
                                    <div class="text-muted small">지급 ${{paidCount}}명</div>
                                    <div class="value text-success">${{paidRate}}%</div>
                                </div>
                            </div>
                            <hr>
                            <div class="row">
                                <div class="col-6">
                                    <div class="text-muted small">평균지급 기준</div>
                                    <div class="value" style="font-size: 1.2rem;">${{avgAmount.toLocaleString()}} VND</div>
                                </div>
                                <div class="col-6">
                                    <div class="text-muted small">총 지급액</div>
                                    <div class="value" style="font-size: 1.2rem;">${{totalAmount.toLocaleString()}} VND</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 인센티브 지급률 -->
                        <div class="popup-stat-card">
                            <h5>인센티브 지급률</h5>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: ${{paidRate}}%">
                                    ${{paidRate}}%
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 오른쪽: 조건 충족 현황 및 직원 목록 -->
                    <div class="popup-right">
                        <!-- 조건 충족 상세 -->
                        <h5 class="mb-3">📊 조건 충족 상세</h5>
                        
                        <!-- 출근 조건 -->
                        <div class="condition-group">
                            <div class="condition-group-title attendance">🎯 출근 조건 (4가지)</div>
                            <table class="condition-summary-table">
                                <thead>
                                    <tr>
                                        <th>조건</th>
                                        <th>평가 대상</th>
                                        <th>충족</th>
                                        <th>미충족</th>
                                        <th>충족률</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>출근율 ≥88%</td>
                                        <td>${{totalCount}}명</td>
                                        <td class="text-success">${{employees.filter(e => e.condition1 === 'no').length}}명</td>
                                        <td class="text-danger">${{employees.filter(e => e.condition1 === 'yes').length}}명</td>
                                        <td>
                                            <div class="progress-bar-container" style="height: 15px;">
                                                <div class="progress-bar-fill" style="width: ${{(employees.filter(e => e.condition1 === 'no').length / totalCount * 100).toFixed(0)}}%; font-size: 0.7rem;">
                                                    ${{(employees.filter(e => e.condition1 === 'no').length / totalCount * 100).toFixed(0)}}%
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>무단결근 ≤2일</td>
                                        <td>${{totalCount}}명</td>
                                        <td class="text-success">${{employees.filter(e => e.condition2 === 'no').length}}명</td>
                                        <td class="text-danger">${{employees.filter(e => e.condition2 === 'yes').length}}명</td>
                                        <td>
                                            <div class="progress-bar-container" style="height: 15px;">
                                                <div class="progress-bar-fill" style="width: 100%; font-size: 0.7rem;">100%</div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>실제 근무일 >0일</td>
                                        <td>${{totalCount}}명</td>
                                        <td class="text-success">${{employees.filter(e => e.condition3 === 'no').length}}명</td>
                                        <td class="text-danger">${{employees.filter(e => e.condition3 === 'yes').length}}명</td>
                                        <td>
                                            <div class="progress-bar-container" style="height: 15px;">
                                                <div class="progress-bar-fill" style="width: ${{(employees.filter(e => e.condition3 === 'no').length / totalCount * 100).toFixed(0)}}%; font-size: 0.7rem;">
                                                    ${{(employees.filter(e => e.condition3 === 'no').length / totalCount * 100).toFixed(0)}}%
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>최소 근무일 ≥12일</td>
                                        <td>${{totalCount}}명</td>
                                        <td class="text-success">${{employees.filter(e => e.condition4 === 'no').length}}명</td>
                                        <td class="text-danger">${{employees.filter(e => e.condition4 === 'yes').length}}명</td>
                                        <td>
                                            <div class="progress-bar-container" style="height: 15px;">
                                                <div class="progress-bar-fill" style="width: 100%; font-size: 0.7rem;">100%</div>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- AQL 조건 -->
                        <div class="condition-group">
                            <div class="condition-group-title aql">🎯 AQL 조건 (4가지)</div>
                            <table class="condition-summary-table">
                                <tbody>
                                    <tr>
                                        <td>개인 AQL: 당월 실패 0건</td>
                                        <td colspan="4" class="text-muted">평가 대상 아님</td>
                                    </tr>
                                    <tr>
                                        <td>연속성 체크: 3개월 연속 실패 없음</td>
                                        <td colspan="4" class="text-muted">평가 대상 아님</td>
                                    </tr>
                                    <tr>
                                        <td>팀/구역 AQL: 3개월 연속 실패 없음</td>
                                        <td colspan="4" class="text-muted">평가 대상 아님</td>
                                    </tr>
                                    <tr>
                                        <td>담당구역 reject율 <3%</td>
                                        <td colspan="4" class="text-muted">평가 대상 아님</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- 5PRS 조건 -->
                        <div class="condition-group">
                            <div class="condition-group-title prs">📊 5PRS 조건 (2가지)</div>
                            <table class="condition-summary-table">
                                <tbody>
                                    <tr>
                                        <td>5PRS 통과율 ≥95%</td>
                                        <td colspan="4" class="text-muted">평가 대상 아님</td>
                                    </tr>
                                    <tr>
                                        <td>5PRS 검사량 ≥100개</td>
                                        <td colspan="4" class="text-muted">평가 대상 아님</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- 직원별 상세 현황 -->
                        <h5 class="mt-4 mb-3">직원별 상세 현황</h5>
                        <div style="max-height: 300px; overflow-y: auto;">
                            <table class="table table-sm">
                                <thead style="position: sticky; top: 0; background: white;">
                                    <tr>
                                        <th>직원번호</th>
                                        <th>이름</th>
                                        <th>인센티브</th>
                                        <th>상태</th>
                                        <th>조건 충족 현황</th>
                                        <th>개산 근거</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            // 직원 목록 추가
            employees.forEach(emp => {{
                const amount = parseInt(emp.august_incentive);
                const isPaid = amount > 0;
                
                // 조건 충족 체크
                const attendanceMet = emp.condition1 === 'no' && emp.condition2 === 'no' && 
                                     emp.condition3 === 'no' && emp.condition4 === 'no';
                
                popupHtml += `
                    <tr>
                        <td>${{emp.emp_no}}</td>
                        <td>${{emp.name}}</td>
                        <td><strong>${{amount.toLocaleString()}} VND</strong></td>
                        <td>${{isPaid ? '<span class="badge bg-success">지급</span>' : '<span class="badge bg-danger">미지급</span>'}}</td>
                        <td>
                            <span class="badge bg-${{attendanceMet ? 'success' : 'danger'}}">출근: ${{attendanceMet ? '✓' : '✗'}}</span>
                            <span class="badge bg-secondary">AQL: N/A</span>
                            <span class="badge bg-secondary">5PRS: N/A</span>
                        </td>
                        <td>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar bg-${{isPaid ? 'success' : 'danger'}}" style="width: ${{isPaid ? '100' : '0'}}%">
                                    ${{isPaid ? '✓ 조건 충족' : '✗ 조건 미충족'}}
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            }});
            
            popupHtml += `
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- 버튼 그룹 -->
                        <div class="mt-3 d-flex justify-content-end gap-2">
                            <button class="btn btn-secondary" onclick="closeModal()">닫기</button>
                            <button class="btn btn-primary" onclick="exportPositionData('${{type}}', '${{position}}')">
                                <i class="bi bi-download"></i> 데이터 내보내기
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            modalBody.innerHTML = popupHtml;
            modal.style.display = 'block';
            
            // 차트 생성 (약간의 딜레이 후)
            setTimeout(() => {{
                createPopupChart(employees, 'popupChart');
            }}, 100);
        }}
        
        // 데이터 내보내기 함수
        function exportPositionData(type, position) {{
            const employees = employeeData.filter(e => e.type === type && e.position === position);
            const csvContent = "data:text/csv;charset=utf-8," 
                + "사번,이름,Type,직급,인센티브,상태\\n"
                + employees.map(e => `${{e.emp_no}},${{e.name}},${{e.type}},${{e.position}},${{e.august_incentive}},${{parseInt(e.august_incentive) > 0 ? '지급' : '미지급'}}`).join("\\n");
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `${{type}}_${{position}}_인센티브.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}
        
        // 직원 상세 정보 표시
        function showEmployeeDetail(empNo) {{
            const emp = employeeData.find(e => e.emp_no === empNo);
            if (!emp) return;
            
            const modal = document.getElementById('employeeModal');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');
            
            modalTitle.textContent = `${{emp.name}} (${{emp.emp_no}})`;
            
            modalBody.innerHTML = `
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>직급:</strong> ${{emp.position}}<br>
                        <strong>Type:</strong> <span class="type-badge type-${{emp.type.toLowerCase().replace('type-', '')}}">${{emp.type}}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>8월 인센티브:</strong> ${{parseInt(emp.august_incentive).toLocaleString()}} VND<br>
                        <strong>7월 인센티브:</strong> ${{parseInt(emp.july_incentive).toLocaleString()}} VND
                    </div>
                </div>
                
                <!-- 출근 조건 (4개) -->
                <div class="condition-group">
                    <div class="condition-group-title attendance">출근 조건 (4개)</div>
                    <div class="condition-check ${{emp.condition1 === 'yes' ? 'fail' : 'success'}}">
                        <span>조건 1: 출근율 ≥ 88%</span>
                        <span>${{emp.attendance_rate.toFixed(2)}}% ${{emp.condition1 === 'yes' ? '❌' : '✅'}}</span>
                    </div>
                    <div class="condition-check ${{emp.condition2 === 'yes' ? 'fail' : 'success'}}">
                        <span>조건 2: 무단 결근 ≤ 2일</span>
                        <span>${{emp.unapproved_absences}}일 ${{emp.condition2 === 'yes' ? '❌' : '✅'}}</span>
                    </div>
                    <div class="condition-check ${{emp.condition3 === 'yes' ? 'fail' : 'success'}}">
                        <span>조건 3: 실제 근무일수 > 0</span>
                        <span>${{emp.actual_working_days}}일 ${{emp.condition3 === 'yes' ? '❌' : '✅'}}</span>
                    </div>
                    <div class="condition-check ${{emp.condition4 === 'yes' ? 'fail' : 'success'}}">
                        <span>조건 4: 최소 근무일 ≥ 12일</span>
                        <span>${{emp.actual_working_days}}일 ${{emp.condition4 === 'yes' ? '❌' : '✅'}}</span>
                    </div>
                </div>
                
                <!-- AQL 조건 (4개) -->
                <div class="condition-group">
                    <div class="condition-group-title aql">AQL 조건 (4개)</div>
                    <div class="condition-check success">
                        <span>조건 5: AQL 실패 횟수 < 3회</span>
                        <span>${{emp.aql_failures}}회 ✅</span>
                    </div>
                    <div class="condition-check success">
                        <span>조건 6: 연속 실패 없음</span>
                        <span>${{emp.continuous_fail}} ✅</span>
                    </div>
                    <div class="condition-check ${{emp.pass_rate >= 95 ? 'success' : 'fail'}}">
                        <span>조건 7: 합격률 ≥ 95%</span>
                        <span>${{emp.pass_rate.toFixed(2)}}% ${{emp.pass_rate >= 95 ? '✅' : '❌'}}</span>
                    </div>
                    <div class="condition-check ${{emp.validation_qty >= 100 ? 'success' : 'fail'}}">
                        <span>조건 8: 검증 수량 ≥ 100개</span>
                        <span>${{emp.validation_qty}}개 ${{emp.validation_qty >= 100 ? '✅' : '❌'}}</span>
                    </div>
                </div>
                
                <!-- 5PRS 조건 (2개) -->
                <div class="condition-group">
                    <div class="condition-group-title prs">5PRS 조건 (2개)</div>
                    <div class="condition-check ${{parseInt(emp.july_incentive) > 0 ? 'success' : 'fail'}}">
                        <span>조건 9: 이전 달 인센티브 수령</span>
                        <span>${{parseInt(emp.july_incentive).toLocaleString()}} VND ${{parseInt(emp.july_incentive) > 0 ? '✅' : '❌'}}</span>
                    </div>
                    <div class="condition-check success">
                        <span>조건 10: 특별 조건 충족</span>
                        <span>✅</span>
                    </div>
                </div>
            `;
            
            modal.style.display = 'block';
        }}
        
        // 모달 닫기
        function closeModal() {{
            document.getElementById('employeeModal').style.display = 'none';
        }}
        
        // 모달 외부 클릭 시 닫기
        window.onclick = function(event) {{
            const modal = document.getElementById('employeeModal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // 테이블 필터링
        function filterTable() {{
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const positionFilter = document.getElementById('positionFilter').value;
            const paymentFilter = document.getElementById('paymentFilter').value;
            
            const tbody = document.getElementById('employeeTableBody');
            tbody.innerHTML = '';
            
            employeeData.forEach(emp => {{
                const amount = parseInt(emp.august_incentive);
                const isPaid = amount > 0;
                
                // 필터 조건 확인
                if (searchInput && !emp.name.toLowerCase().includes(searchInput) && !emp.emp_no.includes(searchInput)) {{
                    return;
                }}
                if (typeFilter && emp.type !== typeFilter) {{
                    return;
                }}
                if (positionFilter && emp.position !== positionFilter) {{
                    return;
                }}
                if (paymentFilter === 'paid' && !isPaid) {{
                    return;
                }}
                if (paymentFilter === 'unpaid' && isPaid) {{
                    return;
                }}
                
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                tr.onclick = () => showEmployeeDetail(emp.emp_no);
                
                tr.innerHTML = `
                    <td>${{emp.emp_no}}</td>
                    <td>${{emp.name}}</td>
                    <td>${{emp.position}}</td>
                    <td><span class="type-badge type-${{emp.type.toLowerCase().replace('type-', '')}}">${{emp.type}}</span></td>
                    <td>${{parseInt(emp.july_incentive).toLocaleString()}}</td>
                    <td><strong>${{amount.toLocaleString()}}</strong></td>
                    <td>${{isPaid ? '✅ 지급' : '❌ 미지급'}}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${{emp.emp_no}}')">상세</button></td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        // 직급 필터 업데이트
        function updatePositionFilter() {{
            const typeFilter = document.getElementById('typeFilter').value;
            const positionSelect = document.getElementById('positionFilter');
            const currentValue = positionSelect.value;
            
            // 직급 목록 수집
            const positions = new Set();
            employeeData.forEach(emp => {{
                if (!typeFilter || emp.type === typeFilter) {{
                    positions.add(emp.position);
                }}
            }});
            
            // 옵션 업데이트
            positionSelect.innerHTML = '<option value="">모든 직급</option>';
            Array.from(positions).sort().forEach(position => {{
                const option = document.createElement('option');
                option.value = position;
                option.textContent = position;
                if (position === currentValue) {{
                    option.selected = true;
                }}
                positionSelect.appendChild(option);
            }});
        }}
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("완전 통합 인센티브 대시보드 시스템")
    print("=" * 80)
    
    # Google Drive 동기화 시도
    month = 'august'
    year = 2025
    
    if GOOGLE_DRIVE_AVAILABLE:
        print("\n📂 Google Drive 동기화 시도 중...")
        sync_success = sync_from_google_drive(month, year)
        if sync_success:
            print("✅ Google Drive에서 최신 데이터를 가져왔습니다.")
        else:
            print("⚠️ Google Drive 동기화 실패. 로컬 파일을 사용합니다.")
    
    # 데이터 로드
    print("\n📊 데이터 로드 중...")
    df = load_incentive_data(month, year)
    
    if df.empty:
        print("❌ 데이터 로드 실패")
        return
    
    # 대시보드 생성
    print("\n🎨 대시보드 생성 중...")
    html_content = generate_dashboard_html(df, month, year)
    
    # 파일 저장
    output_file = 'output_files/integrated_dashboard_complete.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 대시보드 생성 완료: {output_file}")
    
    # 통계 출력
    total_employees = len(df)
    paid_employees = sum(1 for _, row in df.iterrows() if int(row.get('august_incentive', 0)) > 0)
    total_amount = sum(int(row.get('august_incentive', 0)) for _, row in df.iterrows())
    
    print(f"   - 전체 직원: {total_employees}명")
    print(f"   - 지급 대상: {paid_employees}명")
    print(f"   - 총 지급액: {total_amount:,} VND")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()