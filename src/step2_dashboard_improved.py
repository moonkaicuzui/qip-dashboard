"""
개선된 대시보드 생성 스크립트
CSV 파일에서 직접 데이터를 읽어 대시보드 생성
"""

import pandas as pd
import json
import argparse
from pathlib import Path
from datetime import datetime

def load_incentive_data(month, year):
    """CSV 파일에서 직접 인센티브 데이터 로드"""
    # CSV 파일 경로
    csv_pattern = f"output_QIP_incentive_{month}_{year}_*Complete.csv"
    output_dir = Path(__file__).parent.parent / "output_files"
    
    # 파일 찾기
    csv_files = list(output_dir.glob(csv_pattern))
    if not csv_files:
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_pattern}")
    
    # 가장 최신 파일 사용
    csv_file = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"✅ CSV 파일 로드: {csv_file}")
    
    # 데이터 로드
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # 필요한 컬럼만 선택
    required_columns = [
        'Employee No', 'Name_vi', 'Position', 'TYPE',
        'June_Incentive', 'July_Incentive', 'August_Incentive',
        'Attendance Rate (%)', 'Unapproved Absences',
        'July AQL Failures', '5PRS Pass %'
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in required_columns if col in df.columns]
    df = df[available_columns]
    
    return df

def generate_dashboard_html(df, month, year):
    """데이터프레임에서 직접 대시보드 HTML 생성"""
    
    # 통계 계산
    total_employees = len(df)
    
    # 인센티브 컬럼 찾기
    incentive_columns = [col for col in df.columns if 'Incentive' in col and month.title() in col]
    if incentive_columns:
        current_incentive = incentive_columns[0]
        paid_employees = (df[current_incentive] > 0).sum()
        total_amount = df[current_incentive].sum()
    else:
        paid_employees = 0
        total_amount = 0
    
    payment_rate = (paid_employees / total_employees * 100) if total_employees > 0 else 0
    
    # HTML 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 대시보드 - {year}년 {month}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        table {{
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>QIP 인센티브 대시보드 <span class="badge bg-primary">v5.0</span></h1>
            <p class="text-muted">{year}년 {month} 인센티브 지급 현황</p>
            <p class="text-muted">생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="row">
            <div class="col-md-3">
                <div class="stat-card">
                    <div>전체 직원</div>
                    <div class="stat-number">{total_employees:,}명</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div>수령 직원</div>
                    <div class="stat-number">{paid_employees:,}명</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div>지급률</div>
                    <div class="stat-number">{payment_rate:.1f}%</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div>총 지급액</div>
                    <div class="stat-number">{total_amount:,.0f} VND</div>
                </div>
            </div>
        </div>
        
        <h2 class="mt-4">직원별 상세 내역</h2>
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>직원번호</th>
                        <th>이름</th>
                        <th>직급</th>
                        <th>TYPE</th>
                        <th>인센티브</th>
                        <th>출근율</th>
                        <th>AQL</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # 테이블 데이터 추가
    for _, row in df.head(100).iterrows():  # 처음 100명만 표시
        incentive_value = row.get(current_incentive, 0) if incentive_columns else 0
        html_content += f"""
                    <tr>
                        <td>{row.get('Employee No', '')}</td>
                        <td>{row.get('Name_vi', '')}</td>
                        <td>{row.get('Position', '')}</td>
                        <td>{row.get('TYPE', '')}</td>
                        <td>{incentive_value:,.0f}</td>
                        <td>{row.get('Attendance Rate (%)', 0):.1f}%</td>
                        <td>{row.get('July AQL Failures', 0)}</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

def main():
    parser = argparse.ArgumentParser(description='Generate Improved Dashboard')
    parser.add_argument('--month', type=str, default='july', help='Month name')
    parser.add_argument('--year', type=int, default=2025, help='Year')
    
    args = parser.parse_args()
    
    try:
        # 데이터 로드
        df = load_incentive_data(args.month, args.year)
        
        # 대시보드 생성
        html_content = generate_dashboard_html(df, args.month, args.year)
        
        # 파일 저장
        output_dir = Path(__file__).parent.parent / "output_files"
        output_file = output_dir / "dashboard_improved.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 개선된 대시보드 생성 완료: {output_file}")
        print(f"📊 CSV 데이터에서 직접 생성 (HTML 파싱 없음)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())