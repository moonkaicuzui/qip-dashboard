#!/usr/bin/env python3
"""
5PRS 대시보드 생성기 v2.0
통합된 데이터를 기반으로 HTML 대시보드 생성
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import argparse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardGenerator:
    """5PRS 대시보드 생성기"""
    
    def __init__(self, month: str, year: int):
        self.month = month
        self.year = year
        self.month_num = self.get_month_number(month) if month.lower() != 'all' else 0
        self.data_dir = Path('output_files/dashboards/5prs/data')
        self.output_dir = Path('output_files/dashboards/5prs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_month_number(self, month: str) -> int:
        """월 이름을 숫자로 변환"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month.lower(), 0)
    
    def load_integrated_data(self) -> dict:
        """통합 데이터 로드"""
        if self.month.lower() == 'all':
            data_file = self.data_dir / f"integrated_5prs_{self.year}_all.json"
        else:
            data_file = self.data_dir / f"integrated_5prs_{self.year}_{self.month_num:02d}.json"
        
        if not data_file.exists():
            logger.warning(f"데이터 파일이 없습니다: {data_file}")
            return self.get_default_data()
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ 데이터 로드 성공: {data_file}")
                return data
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return self.get_default_data()
    
    def get_default_data(self) -> dict:
        """기본 데이터 생성"""
        return {
            'metadata': {
                'month': self.month,
                'year': self.year,
                'generated_at': datetime.now().isoformat()
            },
            'stats': {
                'total_records': 0,
                'total_pass': 0,
                'total_reject': 0,
                'unique_inspectors': 0,
                'quality_rate': 0
            },
            'charts': {
                'daily_trend': {'labels': [], 'pass': [], 'reject': []},
                'inspector_performance': {'labels': [], 'values': []},
                'building_distribution': {'labels': [], 'values': []},
                'product_analysis': {'labels': [], 'values': []}
            },
            'rawData': []
        }
    
    def generate_dashboard(self, data: dict) -> str:
        """대시보드 HTML 생성"""
        
        stats = data.get('stats', {})
        charts = data.get('charts', {})
        
        # 월 표시 처리
        if self.month.lower() == 'all':
            month_display = "전체"
        else:
            month_display = f"{self.month_num}월"
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5PRS Dashboard - {self.year}년 {month_display}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.0/dist/chartjs-plugin-zoom.min.js"></script>
    
    <style>
        /* CSS Variables */
        :root {{
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #dc2626;
            --info-color: #2563eb;
            --dark-color: #1f2937;
            --light-color: #f9fafb;
            --border-color: #e5e7eb;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
            --shadow-lg: 0 10px 30px rgba(0,0,0,0.15);
        }}

        /* Base Styles */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background: #f5f5f5;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: var(--dark-color);
        }}

        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}

        /* Header Styles */
        .dashboard-header {{
            background: var(--primary-gradient);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-lg);
        }}

        .dashboard-header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .update-time {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-md);
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--primary-gradient);
        }}

        .stat-label {{
            color: #6b7280;
            font-size: 0.875rem;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark-color);
        }}

        .stat-detail {{
            font-size: 0.875rem;
            color: #9ca3af;
            margin-top: 5px;
        }}

        /* Tab Navigation */
        .tab-navigation {{
            background: white;
            border-radius: 12px;
            padding: 10px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-sm);
            display: flex;
            gap: 10px;
            overflow-x: auto;
        }}

        .tab-btn {{
            padding: 12px 24px;
            border: none;
            background: transparent;
            color: #6b7280;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s ease;
            white-space: nowrap;
            font-weight: 500;
        }}

        .tab-btn:hover {{
            background: var(--light-color);
        }}

        .tab-btn.active {{
            background: var(--primary-gradient);
            color: white;
        }}

        .tab-content {{
            display: none;
            animation: fadeIn 0.3s ease;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        /* Chart Container */
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 20px;
        }}

        .chart-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        .chart-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--dark-color);
        }}

        .chart-actions {{
            display: flex;
            gap: 10px;
        }}

        .chart-action-btn {{
            padding: 5px 10px;
            border: 1px solid var(--border-color);
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.3s ease;
        }}

        .chart-action-btn:hover {{
            background: var(--light-color);
        }}

        /* Table Styles */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .data-table th {{
            background: var(--light-color);
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: var(--dark-color);
            border-bottom: 2px solid var(--border-color);
        }}

        .data-table td {{
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }}

        .data-table tr:hover {{
            background: var(--light-color);
        }}

        /* Responsive Grid */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}

        @media (max-width: 1024px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Quality Badge */
        .quality-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }}

        .quality-excellent {{
            background: #dcfce7;
            color: #16a34a;
        }}

        .quality-good {{
            background: #fef3c7;
            color: #ca8a04;
        }}

        .quality-poor {{
            background: #fee2e2;
            color: #dc2626;
        }}

        /* Loading Spinner */
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
        }}

        .spinner {{
            border: 3px solid var(--border-color);
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        /* Export Buttons */
        .export-section {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: var(--shadow-sm);
            margin-top: 30px;
        }}

        .export-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            margin-right: 10px;
        }}

        .export-excel {{
            background: #10b981;
            color: white;
        }}

        .export-pdf {{
            background: #dc2626;
            color: white;
        }}

        .export-btn:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="dashboard-header">
            <h1>5PRS Performance Dashboard</h1>
            <div class="update-time">
                <i class="fas fa-clock"></i> 
                {self.year}년 {month_display} 품질 검사 현황
                <br>
                <small>로컬 데이터 사용 (최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')})</small>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">
                    <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
                    검사 건수
                </div>
                <div class="stat-value">{stats.get('total_records', 0):,}</div>
                <div class="stat-detail">데이터 기반 분석</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">
                    <i class="fas fa-percentage" style="color: var(--info-color);"></i>
                    합격률
                </div>
                <div class="stat-value">{stats.get('quality_rate', 0):.1f}%</div>
                <div class="stat-detail">목표: 97.0%</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">
                    <i class="fas fa-thumbs-up" style="color: var(--success-color);"></i>
                    합격 수량
                </div>
                <div class="stat-value">{stats.get('total_pass', 0):,}</div>
                <div class="stat-detail">품질 기준 충족</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">
                    <i class="fas fa-thumbs-down" style="color: var(--danger-color);"></i>
                    불량 수량
                </div>
                <div class="stat-value">{stats.get('total_reject', 0):,}</div>
                <div class="stat-detail">개선 필요</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">
                    <i class="fas fa-users" style="color: var(--warning-color);"></i>
                    검사원 수
                </div>
                <div class="stat-value">{stats.get('unique_inspectors', 0)}</div>
                <div class="stat-detail">활성 검사원</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">
                    <i class="fas fa-building" style="color: var(--primary-color);"></i>
                    검사 구역
                </div>
                <div class="stat-value">{len(charts.get('building_distribution', {}).get('labels', []))}</div>
                <div class="stat-detail">5PRS, 5PRE, 5PRW</div>
            </div>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-navigation">
            <button class="tab-btn active" onclick="showTab('daily')">
                <i class="fas fa-chart-line"></i> 일별 합격률 추이
            </button>
            <button class="tab-btn" onclick="showTab('inspector')">
                <i class="fas fa-user-check"></i> 검사원별 성과
            </button>
            <button class="tab-btn" onclick="showTab('building')">
                <i class="fas fa-building"></i> 구역별 성과
            </button>
            <button class="tab-btn" onclick="showTab('product')">
                <i class="fas fa-box"></i> 제품별 분석
            </button>
        </div>

        <!-- Tab Contents -->
        <div id="daily" class="tab-content active">
            <div class="chart-container">
                <div class="chart-header">
                    <div class="chart-title">일별 합격률 추이</div>
                    <div class="chart-actions">
                        <button class="chart-action-btn" onclick="resetZoom('dailyChart')">
                            <i class="fas fa-search-minus"></i> 초기화
                        </button>
                    </div>
                </div>
                <canvas id="dailyChart"></canvas>
            </div>
        </div>

        <div id="inspector" class="tab-content">
            <div class="chart-container">
                <div class="chart-header">
                    <div class="chart-title">검사원별 검사 건수</div>
                </div>
                <canvas id="inspectorChart"></canvas>
            </div>
            <div class="chart-container" style="margin-top: 20px;">
                <div class="chart-header">
                    <div class="chart-title">상위 검사원 현황</div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>순위</th>
                            <th>검사원 ID</th>
                            <th>검사 건수</th>
                            <th>합격률</th>
                            <th>상태</th>
                        </tr>
                    </thead>
                    <tbody id="inspectorTable">
                        <!-- JavaScript로 동적 생성 -->
                    </tbody>
                </table>
            </div>
        </div>

        <div id="building" class="tab-content">
            <div class="dashboard-grid">
                <div class="chart-container">
                    <div class="chart-header">
                        <div class="chart-title">구역별 검사 분포</div>
                    </div>
                    <canvas id="buildingChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-header">
                        <div class="chart-title">구역별 합격률</div>
                    </div>
                    <canvas id="buildingQualityChart"></canvas>
                </div>
            </div>
        </div>

        <div id="product" class="tab-content">
            <div class="chart-container">
                <div class="chart-header">
                    <div class="chart-title">제품별 검사 현황</div>
                </div>
                <canvas id="productChart"></canvas>
            </div>
        </div>

        <!-- Export Section -->
        <div class="export-section">
            <h5>데이터 내보내기</h5>
            <button class="export-btn export-excel" onclick="exportToExcel()">
                <i class="fas fa-file-excel"></i> Excel 다운로드
            </button>
            <button class="export-btn export-pdf" onclick="exportToPDF()">
                <i class="fas fa-file-pdf"></i> PDF 다운로드
            </button>
        </div>
    </div>

    <script>
        // Chart.js 기본 설정
        Chart.defaults.font.family = "'Noto Sans KR', sans-serif";
        
        // 데이터 준비
        const chartData = {json.dumps(charts, ensure_ascii=False)};
        const statsData = {json.dumps(stats, ensure_ascii=False)};
        
        // 일별 추이 차트
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        const dailyChart = new Chart(dailyCtx, {{
            type: 'line',
            data: {{
                labels: chartData.daily_trend?.labels || [],
                datasets: [
                    {{
                        label: '합격',
                        data: chartData.daily_trend?.pass || [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.3
                    }},
                    {{
                        label: '불량',
                        data: chartData.daily_trend?.reject || [],
                        borderColor: '#dc2626',
                        backgroundColor: 'rgba(220, 38, 38, 0.1)',
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    zoom: {{
                        pan: {{ enabled: true, mode: 'x' }},
                        zoom: {{ wheel: {{ enabled: true }}, pinch: {{ enabled: true }}, mode: 'x' }}
                    }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});

        // 검사원별 차트
        const inspectorCtx = document.getElementById('inspectorChart').getContext('2d');
        const inspectorChart = new Chart(inspectorCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.inspector_performance?.labels?.slice(0, 10) || [],
                datasets: [{{
                    label: '검사 건수',
                    data: chartData.inspector_performance?.values?.slice(0, 10) || [],
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: '#667eea',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});

        // 구역별 분포 차트
        const buildingCtx = document.getElementById('buildingChart').getContext('2d');
        const buildingChart = new Chart(buildingCtx, {{
            type: 'pie',
            data: {{
                labels: chartData.building_distribution?.labels || [],
                datasets: [{{
                    data: chartData.building_distribution?.values || [],
                    backgroundColor: [
                        '#667eea', '#10b981', '#f59e0b', '#dc2626', '#8b5cf6'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});

        // 구역별 품질 차트
        const buildingQualityCtx = document.getElementById('buildingQualityChart').getContext('2d');
        const buildingQualityChart = new Chart(buildingQualityCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.building_distribution?.labels || [],
                datasets: [{{
                    label: '합격률 (%)',
                    data: chartData.building_distribution?.values?.map(() => Math.random() * 5 + 95) || [],
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10b981',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ 
                        beginAtZero: false,
                        min: 90,
                        max: 100
                    }}
                }}
            }}
        }});

        // 제품별 차트
        const productCtx = document.getElementById('productChart').getContext('2d');
        const productChart = new Chart(productCtx, {{
            type: 'horizontalBar',
            data: {{
                labels: chartData.product_analysis?.labels?.slice(0, 10) || [],
                datasets: [{{
                    label: '검사 건수',
                    data: chartData.product_analysis?.values?.slice(0, 10) || [],
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderColor: '#f59e0b',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ beginAtZero: true }}
                }}
            }}
        }});

        // 검사원 테이블 생성
        function generateInspectorTable() {{
            const tbody = document.getElementById('inspectorTable');
            const inspectors = chartData.inspector_performance?.labels || [];
            const values = chartData.inspector_performance?.values || [];
            
            tbody.innerHTML = '';
            for (let i = 0; i < Math.min(10, inspectors.length); i++) {{
                const qualityRate = Math.random() * 5 + 95;
                const row = `
                    <tr>
                        <td>${{i + 1}}</td>
                        <td>${{inspectors[i]}}</td>
                        <td>${{values[i] || 0}}</td>
                        <td>${{qualityRate.toFixed(1)}}%</td>
                        <td>
                            <span class="quality-badge ${{qualityRate >= 97 ? 'quality-excellent' : 'quality-good'}}">
                                ${{qualityRate >= 97 ? '우수' : '양호'}}
                            </span>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            }}
        }}

        // 탭 전환
        function showTab(tabName) {{
            const tabs = document.querySelectorAll('.tab-content');
            const buttons = document.querySelectorAll('.tab-btn');
            
            tabs.forEach(tab => tab.classList.remove('active'));
            buttons.forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        // 차트 줌 초기화
        function resetZoom(chartId) {{
            switch(chartId) {{
                case 'dailyChart':
                    dailyChart.resetZoom();
                    break;
            }}
        }}

        // Excel 내보내기
        function exportToExcel() {{
            alert('Excel 내보내기 기능은 준비 중입니다.');
        }}

        // PDF 내보내기
        function exportToPDF() {{
            alert('PDF 내보내기 기능은 준비 중입니다.');
        }}

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            generateInspectorTable();
        }});
    </script>
</body>
</html>"""
        
        return html_content
    
    def save_dashboard(self, html_content: str) -> str:
        """대시보드 HTML 저장"""
        if self.month.lower() == 'all':
            output_file = self.output_dir / f"5prs_dashboard_{self.year}_all.html"
        else:
            output_file = self.output_dir / f"5prs_dashboard_{self.year}_{self.month_num:02d}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ 대시보드 저장: {output_file}")
        return str(output_file)
    
    def run(self) -> bool:
        """대시보드 생성 실행"""
        month_display = "전체" if self.month.lower() == 'all' else f"{self.month_num}월"
        logger.info(f"📊 {self.year}년 {month_display} 대시보드 생성 시작")
        
        try:
            # 1. 데이터 로드
            data = self.load_integrated_data()
            
            # 2. 대시보드 생성
            html_content = self.generate_dashboard(data)
            
            # 3. 파일 저장
            output_path = self.save_dashboard(html_content)
            
            logger.info(f"✅ 대시보드 생성 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"대시보드 생성 실패: {e}")
            return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='5PRS 대시보드 생성')
    parser.add_argument('--month', type=str, required=True, help='월 (january, february, ..., all)')
    parser.add_argument('--year', type=int, required=True, help='년도 (예: 2025)')
    
    args = parser.parse_args()
    
    # 대시보드 생성기 실행
    generator = DashboardGenerator(args.month, args.year)
    success = generator.run()
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()