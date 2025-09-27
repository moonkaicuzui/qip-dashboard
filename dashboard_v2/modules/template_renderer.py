#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard V2 - Template Rendering Module
Handles HTML template rendering with data injection
"""

import json
import os
from pathlib import Path
from datetime import datetime


class TemplateRenderer:
    """Renders HTML templates with dashboard data"""

    def __init__(self):
        self.template_path = Path(__file__).parent.parent / 'templates' / 'base.html'
        self.css_path = '../dashboard_v2/static/css/dashboard.css'
        self.js_path = '../dashboard_v2/static/js/dashboard.js'

    def render(self, data, output_path=None):
        """
        Render the dashboard HTML with provided data

        Args:
            data: Dictionary containing all dashboard data
            output_path: Optional path to save the rendered HTML

        Returns:
            Rendered HTML string
        """
        # Load template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Prepare data for injection
        month_num = self._get_month_number(data['config']['month'])
        month_display = self._format_month_display(
            data['config']['month'],
            data['config']['year']
        )

        # Prepare JSON data for embedding
        employees_json = json.dumps(data['employees'], ensure_ascii=False)
        translations_json = json.dumps(data['translations'], ensure_ascii=False)
        position_matrix_json = json.dumps(
            data.get('positionMatrix', {}), ensure_ascii=False
        )
        stats_json = json.dumps(data['stats'], ensure_ascii=False)

        # Replace template variables
        html = template
        replacements = {
            '{{ title }}': f"인센티브 대시보드 - {month_display}",
            '{{ dashboard_title }}': '인센티브 대시보드',
            '{{ subtitle }}': f"{data['config']['year']}년 {month_num}월",
            '{{ css_path }}': self.css_path,
            '{{ js_path }}': self.js_path,
            '{{ employees_json }}': employees_json,
            '{{ translations_json }}': translations_json,
            '{{ position_matrix_json }}': position_matrix_json,
            '{{ stats_json }}': stats_json,
            '{{ month }}': data['config']['month'],
            '{{ year }}': str(data['config']['year']),
            '{{ working_days }}': str(data['config'].get('workingDays', 0))
        }

        for key, value in replacements.items():
            html = html.replace(key, value)

        # Save if output path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ Dashboard saved to: {output_path}")

        return html

    def _get_month_number(self, month_str):
        """Convert month string to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3,
            'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9,
            'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month_str.lower(), 0)

    def _format_month_display(self, month_str, year):
        """Format month and year for display"""
        month_num = self._get_month_number(month_str)
        return f"{year}년 {month_num}월"

    def render_standalone(self, data, output_path):
        """
        Render a fully standalone HTML file matching Version 5 exactly

        Args:
            data: Dictionary containing all dashboard data
            output_path: Path to save the rendered HTML

        Returns:
            Path to the saved file
        """
        # Load CSS from Version 5
        month_num = self._get_month_number(data['config']['month'])

        # Get current date/time
        from datetime import datetime
        now = datetime.now()

        # Calculate generation day and report type
        generation_day = now.day
        is_final_report = generation_day >= 25

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 계산 결과 - {data['config']['year']}년 {month_num}월</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
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
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}

        .version-badge {{
            background: rgba(255, 204, 0, 0.9);
            color: #333;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
            font-weight: bold;
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

        .report-type-banner {{
            background: {"linear-gradient(135deg, #10b981 0%, #34d399 100%)" if is_final_report else "linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)"};
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .report-type-banner .icon {{
            font-size: 1.5rem;
            margin-right: 15px;
        }}

        .report-type-banner .title {{
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 2px;
        }}

        .report-type-banner .description {{
            font-size: 0.9rem;
            opacity: 0.95;
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

        /* Language selector */
        .language-selector {{
            position: absolute;
            top: 20px;
            right: 20px;
        }}

        .dashboard-selector {{
            position: absolute;
            top: 20px;
            right: 250px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <!-- Dashboard Selector -->
            <div class="dashboard-selector">
                <select class="form-select form-select-sm" style="width: 200px;" id="dashboardSelector">
                    <option value="incentive">💰 Incentive Dashboard</option>
                    <option value="management">📊 Management Dashboard</option>
                    <option value="statistics">📈 Statistics Dashboard</option>
                </select>
            </div>
            <!-- Language Selector -->
            <div class="language-selector">
                <select class="form-select form-select-sm" id="languageSelect" onchange="changeLanguage(this.value)">
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                    <option value="vi">Tiếng Việt</option>
                </select>
            </div>

            <h1 id="mainTitle">QIP 인센티브 계산 결과 <span class="version-badge">v5.1</span></h1>
            <p id="mainSubtitle">{data['config']['year']}년 {month_num}월 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;">
                보고서 생성일: {now.strftime('%Y년 %m월 %d일 %H:%M')}
            </p>
            <div id="dataPeriodSection" style="color: white; font-size: 0.85em; margin-top: 15px; opacity: 0.85; line-height: 1.6;">
                <p style="margin: 5px 0; font-weight: bold;">📊 사용 데이터 기간:</p>
                <p style="margin: 3px 0; padding-left: 20px;">• 인센티브 데이터: {data['config']['year']}년 {month_num:02d}월 01일 ~ 30일</p>
                <p style="margin: 3px 0; padding-left: 20px;">• 출근 데이터: {data['config']['year']}년 {month_num:02d}월 01일 ~ 23일</p>
                <p style="margin: 3px 0; padding-left: 20px;">• AQL 데이터: {data['config']['year']}년 {month_num:02d}월 01일 ~ 30일</p>
                <p style="margin: 3px 0; padding-left: 20px;">• 5PRS 데이터: {data['config']['year']}년 {month_num:02d}월 03일 ~ 23일</p>
                <p style="margin: 3px 0; padding-left: 20px;">• 기본 인력 데이터: {data['config']['year']}년 {month_num:02d}월 기준</p>
            </div>
        </div>

        <!-- Report Type Banner -->
        <div class="report-type-banner">
            <div style="display: flex; align-items: center;">
                <span class="icon">{"✅" if is_final_report else "⚠️"}</span>
                <div class="message">
                    <div class="title">{"최종 보고서" if is_final_report else "중간 점검용 리포트"}</div>
                    <div class="description">
                        {"이 보고서는 월말 최종 보고서입니다. 모든 인센티브 조건이 정상적으로 적용됩니다." if is_final_report else "이 리포트는 중간 점검용입니다. 일부 조건이 아직 확정되지 않았을 수 있습니다."}
                    </div>
                </div>
            </div>
            <div>
                <span style="font-size: 0.85rem; opacity: 0.9;">생성일: {generation_day}일</span>
            </div>
        </div>

        <div class="content p-4">
            <!-- Summary Cards -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted">전체 직원</h6>
                        <h2>{len(data['employees'])}<span class="unit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted">수령 직원</h6>
                        <h2>{data['stats']['paidEmployees']}<span class="unit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted">지급률</h6>
                        <h2>{data['stats']['paymentRate']:.1f}%</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted">총 지급액</h6>
                        <h2>{data['stats']['totalAmount']:,.0f} VND</h2>
                    </div>
                </div>
            </div>

            <!-- Tab Menu -->
            <div class="tabs">
                <div class="tab active" data-tab="summary" onclick="showTab('summary')">요약</div>
                <div class="tab" data-tab="position" onclick="showTab('position')">직급별 상세</div>
                <div class="tab" data-tab="detail" onclick="showTab('detail')">개인별 상세</div>
                <div class="tab" data-tab="criteria" onclick="showTab('criteria')">인센티브 기준</div>
                <div class="tab" data-tab="orgchart" onclick="showTab('orgchart')">조직도</div>
                <div class="tab" data-tab="validation" onclick="showTab('validation')">요약 및 시스템 검증</div>
            </div>

            <!-- Tab Content will be here -->
            <div id="summary" class="tab-content active">
                <h3>Type별 요약</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>전체 인원</th>
                            <th>지급 대상</th>
                            <th>지급률</th>
                            <th>총 지급액</th>
                            <th>평균 지급액</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Data will be filled by JavaScript -->
                    </tbody>
                </table>
            </div>

            <div id="position" class="tab-content">
                <!-- Position content -->
            </div>

            <div id="detail" class="tab-content">
                <!-- Detail content -->
            </div>

            <div id="criteria" class="tab-content">
                <!-- Criteria content -->
            </div>

            <div id="orgchart" class="tab-content">
                <!-- Org Chart content -->
            </div>

            <div id="validation" class="tab-content">
                <!-- Validation content -->
            </div>
        </div>
    </div>

    <script>
        // Data embedding
        window.employeeData = {json.dumps(data['employees'], ensure_ascii=False)};
        window.dashboardData = {{
            employees: {json.dumps(data['employees'], ensure_ascii=False)},
            stats: {json.dumps(data['stats'], ensure_ascii=False)},
            config: {{
                month: "{data['config']['month']}",
                year: {data['config']['year']},
                workingDays: {data['config'].get('workingDays', 0)}
            }}
        }};

        // Tab switching function
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // Remove active from all tab buttons
            document.querySelectorAll('.tab').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // Show selected tab
            const selectedTab = document.getElementById(tabName);
            if (selectedTab) {{
                selectedTab.classList.add('active');
            }}

            // Add active to selected button
            const selectedBtn = document.querySelector(`[data-tab="${{tabName}}"]`);
            if (selectedBtn) {{
                selectedBtn.classList.add('active');
            }}
        }}

        // Language change function
        function changeLanguage(lang) {{
            console.log('Language changed to:', lang);
            // Implementation for language change
        }}
    </script>
</body>
</html>"""

        # Save the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Standalone dashboard saved to: {output_path}")
        return output_path


def main():
    """Test the template renderer"""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))

    from modules.data_processor import DataProcessor

    # Load data
    processor = DataProcessor('september', 2025)
    processor.load_configurations()
    processor.load_data()
    data = processor.export_to_json()

    # Render template
    renderer = TemplateRenderer()

    # Test standalone render
    output_path = 'output_files/test_dashboard_v2.html'
    renderer.render_standalone(data, output_path)

    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"📊 File size: {file_size:.2f} MB")


if __name__ == "__main__":
    main()