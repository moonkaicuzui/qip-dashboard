#!/usr/bin/env python3
"""
통합 인센티브 대시보드 - 수정 버전
Step2 dashboard_version4.html과 동일한 UI 적용
실제 인센티브 금액 데이터 사용
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_incentive_data(month='august', year=2025):
    """실제 인센티브 데이터 로드"""
    # 여러 파일명 패턴 시도
    patterns = [
        f"input_files/{year}년 {get_korean_month(month)} 인센티브 지급 세부 정보.csv",
        f"output_files/output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv",
        f"output_files/output_QIP_incentive_{month}_{year}.csv"
    ]
    
    for pattern in patterns:
        if os.path.exists(pattern):
            print(f"✅ 인센티브 데이터 로드: {pattern}")
            df = pd.read_csv(pattern, encoding='utf-8-sig')
            
            # 필요한 컬럼 확인 및 정규화
            month_col = f"{month.capitalize()}_Incentive"
            if month_col not in df.columns:
                # July_Incentive, August_Incentive 등 찾기
                for col in df.columns:
                    if 'Incentive' in col and month[:3].lower() in col.lower():
                        df[month_col] = df[col]
                        break
            
            return df
    
    print(f"❌ {month} 인센티브 데이터를 찾을 수 없습니다")
    return None

def get_korean_month(month):
    """영문 월을 한글로 변환"""
    months = {
        'january': '1월', 'february': '2월', 'march': '3월',
        'april': '4월', 'may': '5월', 'june': '6월',
        'july': '7월', 'august': '8월', 'september': '9월',
        'october': '10월', 'november': '11월', 'december': '12월'
    }
    return months.get(month.lower(), month)

def load_position_matrix():
    """Position condition matrix 로드"""
    try:
        matrix_path = Path('config_files/position_condition_matrix.json')
        if matrix_path.exists():
            with open(matrix_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Position matrix 로드 실패: {e}")
    return {}

def create_employee_data(df, month='august'):
    """직원 데이터를 JavaScript 형식으로 변환"""
    employees = []
    month_incentive_col = f"{month.capitalize()}_Incentive"
    
    for _, row in df.iterrows():
        emp = {
            'emp_no': str(row.get('Employee No', '')),
            'name': row.get('Full Name', ''),
            'position': row.get('QIP POSITION 1ST  NAME', ''),
            'type': row.get('ROLE TYPE STD', ''),
            'july_incentive': '0',  # 이전 달
            'august_incentive': str(int(row.get(month_incentive_col, 0))),  # 현재 달
            'june_incentive': '0',  # 이전이전 달
            
            # 조건 데이터
            'attendance_rate': float(row.get('Actual Working Days', 0)) / float(row.get('Total Working Days', 23)) * 100 if float(row.get('Total Working Days', 23)) > 0 else 0,
            'actual_working_days': int(row.get('Actual Working Days', 0)),
            'unapproved_absences': int(row.get('Unapproved Absence Days', 0)),
            'absence_rate': float(row.get('Absence Rate (raw)', 0)),
            
            # 조건 충족 여부
            'condition1': row.get('attendancy condition 1 - acctual working days is zero', 'no'),
            'condition2': row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days', 'no'),
            'condition3': row.get('attendancy condition 3 - absent % is over 12%', 'no'),
            'condition4': row.get('attendancy condition 4 - minimum working days', 'no'),
            
            # AQL/5PRS
            'aql_failures': int(row.get(f'{month.capitalize()} AQL Failures', 0)),
            'continuous_fail': row.get('Continuous_FAIL', 'NO'),
            'pass_rate': float(row.get('Pass %', 0)) if pd.notna(row.get('Pass %')) else 0,
            'validation_qty': int(row.get('Total Valiation Qty', 0)) if pd.notna(row.get('Total Valiation Qty')) else 0,
        }
        employees.append(emp)
    
    return employees

def generate_dashboard_html(employees, month='august', year=2025):
    """dashboard_version4.html과 동일한 UI로 대시보드 생성"""
    
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
            type_stats[emp_type] = {'total': 0, 'paid': 0, 'amount': 0}
        type_stats[emp_type]['total'] += 1
        amount = int(emp['august_incentive'])
        if amount > 0:
            type_stats[emp_type]['paid'] += 1
            type_stats[emp_type]['amount'] += amount
    
    # 직원 데이터 JSON
    employees_json = json.dumps(employees, ensure_ascii=False)
    
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 대시보드 - {get_korean_month(month)} {year}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {generate_css()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>QIP 인센티브 대시보드</h1>
            <p>{get_korean_month(month)} {year} - 통합 시스템</p>
            <div style="position: absolute; top: 20px; right: 20px;">
                <select id="languageSelector" class="form-select" style="width: 150px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3);">
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                    <option value="vi">Tiếng Việt</option>
                </select>
            </div>
        </div>
        
        <div class="content">
            <div class="summary-card">
                <div class="row">
                    <div class="col-md-3">
                        <div class="stat-box">
                            <div class="stat-value">{total_employees}</div>
                            <div class="stat-label">전체 직원</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-box">
                            <div class="stat-value">{paid_employees}</div>
                            <div class="stat-label">지급 대상</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-box">
                            <div class="stat-value">{payment_rate:.1f}%</div>
                            <div class="stat-label">지급률</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-box">
                            <div class="stat-value">{total_amount:,} VND</div>
                            <div class="stat-label">총 지급액</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Tabs -->
            <div class="tabs">
                <div class="tab active" onclick="showTab('summary')">요약</div>
                <div class="tab" onclick="showTab('employees')">직원별 상세</div>
                <div class="tab" onclick="showTab('criteria')">지급 기준</div>
            </div>
            
            <!-- Tab Contents -->
            <div id="summaryContent" class="tab-content active">
                {generate_summary_content(type_stats)}
            </div>
            
            <div id="employeesContent" class="tab-content">
                <div class="search-box mb-3">
                    <input type="text" class="form-control" id="searchInput" placeholder="직원 검색 (이름, 사번)">
                </div>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>사번</th>
                                <th>이름</th>
                                <th>직급</th>
                                <th>Type</th>
                                <th>6월</th>
                                <th>{get_korean_month(month)}</th>
                                <th>8월</th>
                                <th>평균</th>
                            </tr>
                        </thead>
                        <tbody id="employeeTableBody">
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div id="criteriaContent" class="tab-content">
                <h3>인센티브 지급 기준</h3>
                <div class="criteria-section">
                    <h4>1. 출근 조건</h4>
                    <ul>
                        <li>출근율 88% 이상</li>
                        <li>무단결근 2일 이하</li>
                        <li>실제 근무일 0일 초과</li>
                        <li>최소 근무일 12일 이상</li>
                    </ul>
                </div>
                <div class="criteria-section">
                    <h4>2. AQL 조건</h4>
                    <ul>
                        <li>당월 AQL 실패 0건</li>
                        <li>3개월 연속 실패 없음</li>
                    </ul>
                </div>
                <div class="criteria-section">
                    <h4>3. 5PRS 조건</h4>
                    <ul>
                        <li>검사량 100개 이상</li>
                        <li>통과율 95% 이상</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Employee Detail Modal -->
    <div class="modal fade" id="employeeModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">직원 상세 정보</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="modalBody">
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const employeeData = {employees_json};
        {generate_javascript()}
    </script>
</body>
</html>'''
    
    return html_content

def generate_css():
    """dashboard_version4와 동일한 CSS"""
    return '''
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .content {
            padding: 30px;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }
        
        .stat-box {
            text-align: center;
            padding: 20px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #6c757d;
            margin-top: 10px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab.active {
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: bold;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        table th {
            background: #5a67d8 !important;
            color: white !important;
            padding: 12px;
            text-align: left;
            font-weight: 500;
            border: none;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tr:hover {
            background: #f5f5f5;
            cursor: pointer;
        }
        
        .type-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .type-1 { background: #e8f5e8; color: #2e7d2e; }
        .type-2 { background: #e8f0ff; color: #1e3a8a; }
        .type-3 { background: #fff5e8; color: #9a3412; }
        
        .modal-content {
            background: white;
            border: 1px solid #dee2e6;
            color: #212529;
        }
        
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom: 1px solid #dee2e6;
        }
        
        .condition-group {
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .condition-group-title {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 15px;
            padding: 8px 12px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .condition-group-title.attendance {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
        }
        
        .condition-group-title.aql {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            color: white;
        }
        
        .condition-group-title.prs {
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            color: white;
        }
        
        .condition-check {
            padding: 12px 15px;
            margin-bottom: 8px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            transition: all 0.3s ease;
        }
        
        .condition-check.success {
            background: linear-gradient(135deg, rgba(72, 187, 120, 0.2) 0%, rgba(56, 161, 105, 0.2) 100%);
            border-color: #48bb78;
        }
        
        .condition-check.fail {
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.2) 0%, rgba(229, 62, 62, 0.2) 100%);
            border-color: #f56565;
        }
    '''

def generate_summary_content(type_stats):
    """Type별 요약 테이블 생성"""
    html = '''
    <h3>Type별 요약</h3>
    <table class="table">
        <thead>
            <tr>
                <th>Type</th>
                <th>전체 인원</th>
                <th>지급 인원</th>
                <th>지급률</th>
                <th>총 지급액</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for emp_type in sorted(type_stats.keys()):
        stats = type_stats[emp_type]
        rate = (stats['paid'] / stats['total'] * 100) if stats['total'] > 0 else 0
        html += f'''
            <tr>
                <td><span class="type-badge type-{emp_type[-1].lower()}">{emp_type}</span></td>
                <td>{stats['total']}명</td>
                <td>{stats['paid']}명</td>
                <td>{rate:.1f}%</td>
                <td>{stats['amount']:,} VND</td>
            </tr>
        '''
    
    html += '''
        </tbody>
    </table>
    '''
    return html

def generate_javascript():
    """JavaScript 코드"""
    return '''
        // Tab switching
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + 'Content').classList.add('active');
            event.target.classList.add('active');
        }
        
        // Generate employee table
        function generateEmployeeTable() {
            const tbody = document.getElementById('employeeTableBody');
            tbody.innerHTML = '';
            
            employeeData.forEach(emp => {
                const row = document.createElement('tr');
                row.onclick = () => showEmployeeDetail(emp);
                
                const juneAmount = parseInt(emp.june_incentive) || 0;
                const augustAmount = parseInt(emp.august_incentive) || 0;
                const avgAmount = Math.round((juneAmount + augustAmount) / 2);
                
                row.innerHTML = `
                    <td>${emp.emp_no}</td>
                    <td>${emp.name}</td>
                    <td>${emp.position}</td>
                    <td><span class="type-badge type-${emp.type.slice(-1).toLowerCase()}">${emp.type}</span></td>
                    <td>${juneAmount.toLocaleString()}</td>
                    <td><strong>${augustAmount.toLocaleString()}</strong></td>
                    <td></td>
                    <td>${avgAmount.toLocaleString()}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        // Show employee detail modal
        function showEmployeeDetail(emp) {
            const modalBody = document.getElementById('modalBody');
            const amount = parseInt(emp.august_incentive);
            
            modalBody.innerHTML = `
                <h4>${emp.name} (${emp.emp_no})</h4>
                <p>직급: ${emp.position} | Type: ${emp.type}</p>
                <hr>
                
                <div class="condition-group">
                    <div class="condition-group-title attendance">출근 조건 (4개)</div>
                    <div class="condition-check ${emp.condition1 === 'no' ? 'success' : 'fail'}">
                        <span>실제 근무일 > 0</span>
                        <span>${emp.actual_working_days}일</span>
                    </div>
                    <div class="condition-check ${emp.condition2 === 'no' ? 'success' : 'fail'}">
                        <span>무단결근 ≤ 2일</span>
                        <span>${emp.unapproved_absences}일</span>
                    </div>
                    <div class="condition-check ${emp.condition3 === 'no' ? 'success' : 'fail'}">
                        <span>결근율 ≤ 12%</span>
                        <span>${emp.absence_rate.toFixed(1)}%</span>
                    </div>
                    <div class="condition-check ${emp.condition4 === 'no' ? 'success' : 'fail'}">
                        <span>최소 근무일 ≥ 12일</span>
                        <span>${emp.actual_working_days}일</span>
                    </div>
                </div>
                
                <div class="condition-group">
                    <div class="condition-group-title aql">AQL 조건 (4개)</div>
                    <div class="condition-check ${emp.aql_failures === 0 ? 'success' : 'fail'}">
                        <span>당월 AQL 실패</span>
                        <span>${emp.aql_failures}건</span>
                    </div>
                    <div class="condition-check ${emp.continuous_fail === 'NO' ? 'success' : 'fail'}">
                        <span>3개월 연속 실패</span>
                        <span>${emp.continuous_fail}</span>
                    </div>
                </div>
                
                <div class="condition-group">
                    <div class="condition-group-title prs">5PRS 조건 (2개)</div>
                    <div class="condition-check ${emp.validation_qty >= 100 ? 'success' : 'fail'}">
                        <span>검사량 ≥ 100</span>
                        <span>${emp.validation_qty}개</span>
                    </div>
                    <div class="condition-check ${emp.pass_rate >= 95 ? 'success' : 'fail'}">
                        <span>통과율 ≥ 95%</span>
                        <span>${emp.pass_rate.toFixed(1)}%</span>
                    </div>
                </div>
                
                <hr>
                <h5>인센티브 금액: ${amount.toLocaleString()} VND</h5>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
            modal.show();
        }
        
        // Search functionality
        document.getElementById('searchInput').addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#employeeTableBody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
        
        // Initialize
        generateEmployeeTable();
    '''

def main():
    """메인 실행"""
    print("\n" + "="*80)
    print("통합 인센티브 대시보드 생성 - 수정 버전")
    print("="*80)
    
    # 월 설정 (기본: 8월)
    month = 'august'
    year = 2025
    
    # 데이터 로드
    df = load_incentive_data(month, year)
    if df is None:
        print("❌ 데이터 로드 실패")
        return
    
    print(f"✅ {len(df)}명의 직원 데이터 로드")
    
    # 직원 데이터 변환
    employees = create_employee_data(df, month)
    
    # HTML 생성
    html_content = generate_dashboard_html(employees, month, year)
    
    # 파일 저장
    output_path = Path('output_files/integrated_dashboard_fixed.html')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 대시보드 생성 완료: {output_path}")
    print(f"   - 전체 직원: {len(employees)}명")
    print(f"   - 지급 대상: {sum(1 for e in employees if int(e['august_incentive']) > 0)}명")
    print(f"   - 총 지급액: {sum(int(e['august_incentive']) for e in employees):,} VND")

if __name__ == "__main__":
    main()