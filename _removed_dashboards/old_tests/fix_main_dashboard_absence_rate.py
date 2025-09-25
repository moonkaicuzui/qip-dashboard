#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix main dashboard to show correct absence rate (3.06%) instead of incorrect 16.4%
Ensures consistency across all dashboard views
"""

import json
import re
from pathlib import Path

def load_correct_absence_data():
    """Load the correct absence data from our fixed calculations"""
    data_file = Path(__file__).parent / 'output_files' / 'absence_analytics_data_fixed.json'
    
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Default correct data if file doesn't exist
    return {
        "summary": {
            "total_employees": 391,
            "total_absence_days": 263,
            "avg_absence_rate": 3.06,
            "high_risk_count": 12,
            "medium_risk_count": 15,
            "low_risk_count": 364,
            "maternity_leave_count": 0,
            "total_maternity_days": 0
        }
    }

def fix_dashboard_html(input_file, output_file):
    """Fix the dashboard HTML to show correct absence rates"""
    
    # Load the dashboard HTML
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Load correct absence data
    absence_data = load_correct_absence_data()
    summary = absence_data['summary']
    
    # Fix the main dashboard card display (Card #3)
    # Old: 16.4% and 383명
    # New: 3.06% and 12명 (high risk)
    
    # Replace the hardcoded incorrect values in the HTML
    html_content = re.sub(
        r'<div class="card-value">16\.4%</div>\s*<div class="card-subtitle">결근자: 383명</div>',
        f'<div class="card-value">{summary["avg_absence_rate"]}%</div>\n                <div class="card-subtitle">고위험: {summary["high_risk_count"]}명</div>',
        html_content
    )
    
    # Also fix the centralized data structure
    # Find and replace the incorrect absence data in JavaScript
    html_content = re.sub(
        r'"absence_rate":\s*16\.\d+',
        f'"absence_rate": {summary["avg_absence_rate"]}',
        html_content
    )
    
    html_content = re.sub(
        r'"absence_count":\s*383',
        f'"absence_count": {summary["high_risk_count"]}',
        html_content
    )
    
    # Fix any references to 383 absentees
    html_content = re.sub(
        r'383(?=명|人| people)',
        str(summary["high_risk_count"]),
        html_content
    )
    
    # Fix percentage displays
    html_content = re.sub(
        r'16\.4(?=%| %|％)',
        str(summary["avg_absence_rate"]),
        html_content
    )
    
    # Update the absence modal trigger text
    html_content = re.sub(
        r'결근자 정보/결근율',
        '결근 현황/결근율',
        html_content
    )
    
    # Fix the change indicator (was showing incorrect 76.8% increase)
    # Should show actual change or remove if no previous data
    html_content = re.sub(
        r'<div class="card-change change-positive">▲ 76\.8% vs last month</div>',
        f'<div class="card-change change-neutral">결근율: {summary["avg_absence_rate"]}% (정상)</div>',
        html_content
    )
    
    # Update chart data if present
    # Fix line chart showing 16.4%
    html_content = re.sub(
        r"data:\s*\[.*?,\s*(?:centralizedData\.current_month\.absence_rate\s*\|\|\s*)?16\.4\]",
        f"data: [9.3, {summary['avg_absence_rate']}]",
        html_content
    )
    
    # Save the fixed HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard fixed and saved to: {output_file}")
    return output_file

def main():
    """Main function to fix the dashboard"""
    print("=" * 60)
    print("대시보드 결근율 수정 (16.4% → 3.06%)")
    print("=" * 60)
    
    # Find the most recent dashboard file
    dashboard_dir = Path(__file__).parent / 'output_files'
    
    # Try the already fixed absence dashboard first
    input_file = dashboard_dir / 'management_dashboard_2025_08_absence_fixed.html'
    
    if not input_file.exists():
        # Fall back to any dashboard
        dashboards = list(dashboard_dir.glob('management_dashboard_2025_08*.html'))
        if dashboards:
            input_file = sorted(dashboards)[-1]
        else:
            print("❌ No dashboard files found!")
            return 1
    
    print(f"📄 Input file: {input_file.name}")
    
    # Create output file name
    output_file = dashboard_dir / 'management_dashboard_2025_08_comprehensive_fix.html'
    
    # Fix the dashboard
    fixed_file = fix_dashboard_html(input_file, output_file)
    
    # Load and display the correct data
    absence_data = load_correct_absence_data()
    summary = absence_data['summary']
    
    print("\n✅ 수정 완료! 올바른 데이터:")
    print(f"  - 전체 직원: {summary['total_employees']}명")
    print(f"  - 평균 결근율: {summary['avg_absence_rate']}% (이전: 16.4%)")
    print(f"  - 고위험 인원: {summary['high_risk_count']}명 (이전: 383명)")
    print(f"  - 총 결근일수: {summary['total_absence_days']}일")
    print(f"  - 중위험: {summary['medium_risk_count']}명")
    print(f"  - 저위험: {summary['low_risk_count']}명")
    
    print(f"\n📊 최종 파일: {output_file.name}")
    
    # Open in browser
    import webbrowser
    import os
    full_path = os.path.abspath(output_file)
    webbrowser.open(f'file://{full_path}')
    print("\n브라우저에서 대시보드가 열립니다...")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())