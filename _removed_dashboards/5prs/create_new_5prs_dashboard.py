#!/usr/bin/env python3
"""
새로운 5PRS 대시보드 생성 스크립트
input_files 폴더의 모든 5prs 데이터를 통합하여 대시보드 생성
"""

import pandas as pd
import json
import os
from datetime import datetime
import glob
from pathlib import Path

def load_and_merge_5prs_data():
    """input_files 폴더의 모든 5prs 데이터를 로드하고 병합"""
    
    # 파일 경로 패턴 - input_files 폴더 직접 참조
    file_patterns = [
        'input_files/5prs data*.csv',
        'input_files/5prs_data*.csv'
    ]
    
    all_files = []
    for pattern in file_patterns:
        all_files.extend(glob.glob(pattern))
    
    # 중복 제거
    all_files = list(set(all_files))
    
    if not all_files:
        print("No 5PRS data files found!")
        return None
    
    print(f"Found {len(all_files)} 5PRS data files:")
    for file in sorted(all_files):
        print(f"  - {file}")
    
    # 모든 파일을 DataFrame으로 읽기
    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            print(f"Loaded {len(df)} rows from {os.path.basename(file)}")
            dfs.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")
            continue
    
    if not dfs:
        print("No data could be loaded!")
        return None
    
    # 모든 DataFrame 병합
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # 중복 제거 (날짜, Inspector ID, 시간, TQC ID 기준)
    if all(['Inspection Date' in merged_df.columns, 
            'Inspector ID' in merged_df.columns, 
            'Time' in merged_df.columns, 
            'TQC ID' in merged_df.columns]):
        merged_df = merged_df.drop_duplicates(
            subset=['Inspection Date', 'Inspector ID', 'Time', 'TQC ID'], 
            keep='first'
        )
    
    print(f"\nTotal merged records: {len(merged_df)}")
    
    return merged_df

def process_data_for_dashboard(df):
    """대시보드용 데이터 처리 및 통계 계산"""
    
    # 날짜 파싱
    if 'Inspection Date' in df.columns:
        # 다양한 날짜 형식 처리
        for fmt in ['%d/%m/%y', '%m/%d/%y', '%Y-%m-%d', '%d-%m-%Y']:
            try:
                df['Inspection Date'] = pd.to_datetime(df['Inspection Date'], format=fmt, errors='coerce')
                break
            except:
                continue
    
    # 수치형 데이터 변환
    numeric_cols = ['Valiation Qty', 'Pass Qty', 'Reject Qty']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 불량률 계산
    if 'Reject Qty' in df.columns and 'Valiation Qty' in df.columns:
        df['Reject Rate'] = df.apply(
            lambda row: (row['Reject Qty'] / row['Valiation Qty'] * 100) 
            if row['Valiation Qty'] > 0 else 0, axis=1
        ).round(2)
    
    # 통계 계산
    stats = {
        'total_validation': int(df['Valiation Qty'].sum()) if 'Valiation Qty' in df.columns else 0,
        'total_pass': int(df['Pass Qty'].sum()) if 'Pass Qty' in df.columns else 0,
        'total_reject': int(df['Reject Qty'].sum()) if 'Reject Qty' in df.columns else 0,
        'overall_reject_rate': 0,
        'unique_inspectors': int(df['Inspector ID'].nunique()) if 'Inspector ID' in df.columns else 0,
        'unique_tqc': int(df['TQC ID'].nunique()) if 'TQC ID' in df.columns else 0,
        'total_records': len(df),
        'date_range': {
            'start': '',
            'end': ''
        }
    }
    
    # 전체 불량률 계산
    if stats['total_validation'] > 0:
        stats['overall_reject_rate'] = round((stats['total_reject'] / stats['total_validation'] * 100), 2)
    
    # 날짜 범위 설정
    if 'Inspection Date' in df.columns:
        valid_dates = df['Inspection Date'].dropna()
        if len(valid_dates) > 0:
            stats['date_range']['start'] = valid_dates.min().strftime('%Y-%m-%d') if pd.notna(valid_dates.min()) else ''
            stats['date_range']['end'] = valid_dates.max().strftime('%Y-%m-%d') if pd.notna(valid_dates.max()) else ''
    
    # Inspector별 통계
    inspector_stats = []
    if all(col in df.columns for col in ['Inspector ID', 'Inspector Name', 'Valiation Qty', 'Pass Qty', 'Reject Qty']):
        inspector_agg = df.groupby(['Inspector ID', 'Inspector Name']).agg({
            'Valiation Qty': 'sum',
            'Pass Qty': 'sum',
            'Reject Qty': 'sum'
        }).reset_index()
        inspector_agg['Reject Rate'] = inspector_agg.apply(
            lambda row: (row['Reject Qty'] / row['Valiation Qty'] * 100) 
            if row['Valiation Qty'] > 0 else 0, axis=1
        ).round(2)
        inspector_agg = inspector_agg.sort_values('Valiation Qty', ascending=False).head(20)
        inspector_stats = inspector_agg.to_dict('records')
    
    # TQC별 통계
    tqc_stats = []
    if all(col in df.columns for col in ['TQC ID', 'TQC Name', 'Valiation Qty', 'Pass Qty', 'Reject Qty']):
        tqc_agg = df.groupby(['TQC ID', 'TQC Name']).agg({
            'Valiation Qty': 'sum',
            'Pass Qty': 'sum',
            'Reject Qty': 'sum'
        }).reset_index()
        tqc_agg['Reject Rate'] = tqc_agg.apply(
            lambda row: (row['Reject Qty'] / row['Valiation Qty'] * 100) 
            if row['Valiation Qty'] > 0 else 0, axis=1
        ).round(2)
        tqc_agg = tqc_agg.sort_values('Reject Rate', ascending=False).head(20)
        tqc_stats = tqc_agg.to_dict('records')
    
    # 일별 추세 데이터
    daily_trend = []
    if 'Inspection Date' in df.columns and 'Valiation Qty' in df.columns and 'Reject Qty' in df.columns:
        daily_agg = df.groupby(df['Inspection Date'].dt.date).agg({
            'Valiation Qty': 'sum',
            'Pass Qty': 'sum',
            'Reject Qty': 'sum'
        }).reset_index()
        daily_agg['Reject Rate'] = daily_agg.apply(
            lambda row: (row['Reject Qty'] / row['Valiation Qty'] * 100) 
            if row['Valiation Qty'] > 0 else 0, axis=1
        ).round(2)
        daily_agg['Inspection Date'] = daily_agg['Inspection Date'].astype(str)
        daily_trend = daily_agg.to_dict('records')
    
    # Building별 통계
    building_stats = []
    if 'Building' in df.columns and 'Valiation Qty' in df.columns and 'Reject Qty' in df.columns:
        building_agg = df.groupby('Building').agg({
            'Valiation Qty': 'sum',
            'Pass Qty': 'sum',
            'Reject Qty': 'sum'
        }).reset_index()
        building_agg['Reject Rate'] = building_agg.apply(
            lambda row: (row['Reject Qty'] / row['Valiation Qty'] * 100) 
            if row['Valiation Qty'] > 0 else 0, axis=1
        ).round(2)
        building_stats = building_agg.to_dict('records')
    
    # 고위험 TQC (불량률 > 5%)
    high_risk_tqc = []
    high_risk_count = 0
    if tqc_stats:
        high_risk_tqc = [tqc for tqc in tqc_stats if tqc.get('Reject Rate', 0) > 5.0]
        high_risk_count = len(high_risk_tqc)
    
    # 일평균 검증량 계산
    if daily_trend:
        avg_daily_validation = sum(d.get('Valiation Qty', 0) for d in daily_trend) / len(daily_trend)
    else:
        avg_daily_validation = 0
    
    stats['avg_daily_validation'] = round(avg_daily_validation)
    
    return {
        'stats': stats,
        'inspector_stats': inspector_stats,
        'tqc_stats': tqc_stats,
        'daily_trend': daily_trend,
        'building_stats': building_stats,
        'high_risk_tqc': high_risk_tqc,
        'high_risk_count': high_risk_count
    }

def create_dashboard_html(data):
    """대시보드 HTML 생성"""
    
    html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5PRS Quality Dashboard</title>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.2.0/chartjs-plugin-datalabels.min.js"></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary-color: #2563eb;
            --primary-light: #60a5fa;
            --primary-dark: #1e40af;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-500: #6b7280;
            --gray-700: #374151;
            --gray-900: #111827;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: var(--gray-50);
            color: var(--gray-900);
            line-height: 1.6;
        }
        
        .header {
            background-color: white;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 1.875rem;
            font-weight: 700;
            color: var(--gray-900);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .grid {
            display: grid;
            gap: 1.5rem;
        }
        
        .grid-cols-5 {
            grid-template-columns: repeat(5, 1fr);
        }
        
        .grid-cols-2 {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: var(--shadow);
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--gray-500);
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--gray-900);
        }
        
        .chart-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: var(--shadow);
        }
        
        .chart-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 1rem;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
        }
        
        .table-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: var(--shadow);
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background-color: var(--gray-50);
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
            color: var(--gray-700);
            border-bottom: 2px solid var(--gray-200);
        }
        
        td {
            padding: 0.75rem;
            border-bottom: 1px solid var(--gray-100);
        }
        
        tr:hover {
            background-color: var(--gray-50);
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .badge-danger {
            background-color: #fee2e2;
            color: var(--danger-color);
        }
        
        .badge-warning {
            background-color: #fef3c7;
            color: var(--warning-color);
        }
        
        .badge-success {
            background-color: #d1fae5;
            color: var(--success-color);
        }
        
        .info-text {
            color: var(--gray-500);
            font-size: 0.875rem;
            margin-top: 1rem;
            text-align: center;
        }
        
        @media (max-width: 1024px) {
            .grid-cols-5 {
                grid-template-columns: repeat(2, 1fr);
            }
            .grid-cols-2 {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 640px) {
            .grid-cols-5 {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>5PRS Quality Dashboard</h1>
            <div style="color: var(--gray-500); font-size: 0.875rem;">
                데이터 기간: <span id="dateRange"></span>
            </div>
        </div>
    </div>
    
    <div class="container">
        <!-- 상단 통계 카드 -->
        <div class="grid grid-cols-5" style="margin-bottom: 2rem;">
            <div class="stat-card">
                <div class="stat-label">총 검증 수량</div>
                <div class="stat-value" id="totalValidation">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">전체 불량률</div>
                <div class="stat-value" id="totalRejectRate">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">고위험 TQC</div>
                <div class="stat-value" id="highRiskTQC">0명</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">검사원 수</div>
                <div class="stat-value" id="activeInspectors">0명</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">일평균 검증량</div>
                <div class="stat-value" id="avgValidationQty">0</div>
            </div>
        </div>
        
        <!-- 차트 섹션 -->
        <div class="grid grid-cols-2" style="margin-bottom: 2rem;">
            <div class="chart-card">
                <h3 class="chart-title">일별 불량률 추이</h3>
                <div class="chart-container">
                    <canvas id="dailyTrendChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3 class="chart-title">건물별 품질 현황</h3>
                <div class="chart-container">
                    <canvas id="buildingChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Top Inspector 테이블 -->
        <div class="table-card" style="margin-bottom: 2rem;">
            <h3 class="chart-title">Top 10 검사원 성과</h3>
            <table id="inspectorTable">
                <thead>
                    <tr>
                        <th>검사원 ID</th>
                        <th>검사원 이름</th>
                        <th>검증 수량</th>
                        <th>합격 수량</th>
                        <th>불량 수량</th>
                        <th>불량률</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- High Risk TQC 테이블 -->
        <div class="table-card">
            <h3 class="chart-title">고위험 TQC (불량률 > 5%)</h3>
            <table id="tqcTable">
                <thead>
                    <tr>
                        <th>TQC ID</th>
                        <th>TQC 이름</th>
                        <th>검증 수량</th>
                        <th>불량 수량</th>
                        <th>불량률</th>
                        <th>상태</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <div class="info-text">
            * 데이터는 input_files 폴더의 모든 5PRS 데이터를 통합하여 표시됩니다.
        </div>
    </div>
    
    <script>
        // 대시보드 데이터
        const dashboardData = ''' + json.dumps(data, ensure_ascii=False) + ''';
        
        // 통계 카드 업데이트
        document.getElementById('totalValidation').textContent = dashboardData.stats.total_validation.toLocaleString();
        document.getElementById('totalRejectRate').textContent = dashboardData.stats.overall_reject_rate + '%';
        document.getElementById('highRiskTQC').textContent = dashboardData.high_risk_count + '명';
        document.getElementById('activeInspectors').textContent = dashboardData.stats.unique_inspectors + '명';
        document.getElementById('avgValidationQty').textContent = dashboardData.stats.avg_daily_validation.toLocaleString();
        
        // 날짜 범위 표시
        const dateRange = dashboardData.stats.date_range;
        if (dateRange.start && dateRange.end) {
            document.getElementById('dateRange').textContent = `${dateRange.start} ~ ${dateRange.end}`;
        } else {
            document.getElementById('dateRange').textContent = '데이터 없음';
        }
        
        // 일별 추세 차트
        if (dashboardData.daily_trend && dashboardData.daily_trend.length > 0) {
            const ctx1 = document.getElementById('dailyTrendChart').getContext('2d');
            new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: dashboardData.daily_trend.map(d => d['Inspection Date']),
                    datasets: [{
                        label: '불량률 (%)',
                        data: dashboardData.daily_trend.map(d => d['Reject Rate']),
                        borderColor: 'rgb(239, 68, 68)',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // 건물별 차트
        if (dashboardData.building_stats && dashboardData.building_stats.length > 0) {
            const ctx2 = document.getElementById('buildingChart').getContext('2d');
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: dashboardData.building_stats.map(b => b.Building),
                    datasets: [{
                        label: '검증 수량',
                        data: dashboardData.building_stats.map(b => b['Valiation Qty']),
                        backgroundColor: 'rgba(37, 99, 235, 0.8)'
                    }, {
                        label: '불량 수량',
                        data: dashboardData.building_stats.map(b => b['Reject Qty']),
                        backgroundColor: 'rgba(239, 68, 68, 0.8)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Inspector 테이블 채우기
        const inspectorTableBody = document.querySelector('#inspectorTable tbody');
        dashboardData.inspector_stats.slice(0, 10).forEach(inspector => {
            const row = inspectorTableBody.insertRow();
            row.innerHTML = `
                <td>${inspector['Inspector ID']}</td>
                <td>${inspector['Inspector Name']}</td>
                <td>${inspector['Valiation Qty'].toLocaleString()}</td>
                <td>${inspector['Pass Qty'].toLocaleString()}</td>
                <td>${inspector['Reject Qty'].toLocaleString()}</td>
                <td>
                    <span class="badge ${inspector['Reject Rate'] > 5 ? 'badge-danger' : inspector['Reject Rate'] > 3 ? 'badge-warning' : 'badge-success'}">
                        ${inspector['Reject Rate']}%
                    </span>
                </td>
            `;
        });
        
        // TQC 테이블 채우기
        const tqcTableBody = document.querySelector('#tqcTable tbody');
        if (dashboardData.high_risk_tqc.length > 0) {
            dashboardData.high_risk_tqc.forEach(tqc => {
                const row = tqcTableBody.insertRow();
                row.innerHTML = `
                    <td>${tqc['TQC ID']}</td>
                    <td>${tqc['TQC Name']}</td>
                    <td>${tqc['Valiation Qty'].toLocaleString()}</td>
                    <td>${tqc['Reject Qty'].toLocaleString()}</td>
                    <td>${tqc['Reject Rate']}%</td>
                    <td>
                        <span class="badge badge-danger">고위험</span>
                    </td>
                `;
            });
        } else {
            const row = tqcTableBody.insertRow();
            row.innerHTML = '<td colspan="6" style="text-align: center; color: var(--gray-500);">고위험 TQC가 없습니다.</td>';
        }
        
        // 페이지 로드 완료 메시지
        console.log('5PRS Dashboard loaded successfully');
        console.log('Total records:', dashboardData.stats.total_records);
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("5PRS Dashboard Creation Script")
    print("=" * 60)
    
    # 1. 데이터 로드 및 병합
    print("\n1. Loading and merging data...")
    merged_df = load_and_merge_5prs_data()
    
    if merged_df is None:
        print("Failed to load data. Exiting.")
        return
    
    # 2. 데이터 처리
    print("\n2. Processing data for dashboard...")
    processed_data = process_data_for_dashboard(merged_df)
    
    # 3. 대시보드 HTML 생성
    print("\n3. Creating dashboard HTML...")
    html_content = create_dashboard_html(processed_data)
    
    # 4. 파일 저장
    output_dir = Path('output_files/dashboards/5prs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'new_5prs_dashboard.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n4. Dashboard saved to: {output_file}")
    
    # 5. 요약 출력
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total Validation Qty: {processed_data['stats']['total_validation']:,}")
    print(f"  Overall Reject Rate: {processed_data['stats']['overall_reject_rate']}%")
    print(f"  Unique Inspectors: {processed_data['stats']['unique_inspectors']}")
    print(f"  Unique TQC: {processed_data['stats']['unique_tqc']}")
    print(f"  High Risk TQC Count: {processed_data['high_risk_count']}")
    print(f"  Date Range: {processed_data['stats']['date_range']['start']} to {processed_data['stats']['date_range']['end']}")
    print("=" * 60)
    
    print("\n✅ Dashboard created successfully!")
    print(f"Open the file: {output_file}")

if __name__ == "__main__":
    main()