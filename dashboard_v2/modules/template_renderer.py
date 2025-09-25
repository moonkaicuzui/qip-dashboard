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
        Render a fully standalone HTML file with embedded CSS and JavaScript

        Args:
            data: Dictionary containing all dashboard data
            output_path: Path to save the rendered HTML

        Returns:
            Path to the saved file
        """
        # Load CSS content
        css_file = Path(__file__).parent.parent / 'static' / 'css' / 'dashboard.css'
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # Load JavaScript content
        js_file = Path(__file__).parent.parent / 'static' / 'js' / 'dashboard.js'
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Create standalone HTML
        month_num = self._get_month_number(data['config']['month'])
        month_display = self._format_month_display(
            data['config']['month'],
            data['config']['year']
        )

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>인센티브 대시보드 - {month_display}</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">

    <!-- Embedded CSS -->
    <style>
    {css_content}
    </style>
</head>
<body>
    <!-- Header Section -->
    <div class="dashboard-header">
        <div class="container-fluid">
            <div class="row align-items-center py-3">
                <div class="col-md-6">
                    <h1 class="dashboard-title">
                        <i class="fas fa-chart-line me-2"></i>
                        <span id="dashboardTitle">인센티브 대시보드</span>
                    </h1>
                    <p class="dashboard-subtitle" id="dashboardSubtitle">{data['config']['year']}년 {month_num}월</p>
                </div>
                <div class="col-md-6 text-end">
                    <!-- Language Selector -->
                    <div class="language-selector">
                        <button class="btn btn-sm btn-outline-primary lang-btn active" data-lang="ko">한국어</button>
                        <button class="btn btn-sm btn-outline-primary lang-btn" data-lang="en">English</button>
                        <button class="btn btn-sm btn-outline-primary lang-btn" data-lang="vi">Tiếng Việt</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container-fluid mt-3">
        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs" id="dashboardTabs" role="tablist">
            <!-- Tabs will be dynamically inserted here -->
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="dashboardTabContent">
            <!-- Tab panels will be dynamically inserted here -->
        </div>
    </div>

    <!-- Modals Container -->
    <div id="modalsContainer">
        <!-- Modals will be dynamically inserted here -->
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>

    <!-- Data Variables -->
    <script>
        // Global data variables
        window.dashboardData = {{
            employees: {json.dumps(data['employees'], ensure_ascii=False)},
            translations: {json.dumps(data['translations'], ensure_ascii=False)},
            positionMatrix: {json.dumps(data.get('positionMatrix', {}), ensure_ascii=False)},
            config: {{
                month: "{data['config']['month']}",
                year: {data['config']['year']},
                workingDays: {data['config'].get('workingDays', 0)},
                currentLang: 'ko'
            }},
            stats: {json.dumps(data['stats'], ensure_ascii=False)}
        }};
    </script>

    <!-- Embedded JavaScript -->
    <script>
    {js_content}
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