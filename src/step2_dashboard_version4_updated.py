import re
from datetime import datetime
import json
import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def get_month_year_text(month, year, lang='ko'):
    """Generate month/year text for different languages"""
    month_names = {
        'ko': {
            'january': '1월', 'february': '2월', 'march': '3월', 'april': '4월',
            'may': '5월', 'june': '6월', 'july': '7월', 'august': '8월',
            'september': '9월', 'october': '10월', 'november': '11월', 'december': '12월'
        },
        'en': {
            'january': 'January', 'february': 'February', 'march': 'March', 'april': 'April',
            'may': 'May', 'june': 'June', 'july': 'July', 'august': 'August',
            'september': 'September', 'october': 'October', 'november': 'November', 'december': 'December'
        },
        'vi': {
            'january': 'Tháng 1', 'february': 'Tháng 2', 'march': 'Tháng 3', 'april': 'Tháng 4',
            'may': 'Tháng 5', 'june': 'Tháng 6', 'july': 'Tháng 7', 'august': 'Tháng 8',
            'september': 'Tháng 9', 'october': 'Tháng 10', 'november': 'Tháng 11', 'december': 'Tháng 12'
        }
    }
    
    if lang == 'ko':
        return f"{year}년 {month_names[lang].get(month.lower(), month)} 인센티브 지급 현황"
    elif lang == 'en':
        return f"{month_names[lang].get(month.lower(), month)} {year} Incentive Payment Status"
    elif lang == 'vi':
        return f"Tình trạng thanh toán khuyến khích {month_names[lang].get(month.lower(), month)} năm {year}"
    return f"{year} {month}"

def get_generation_date_text(lang='ko'):
    """Generate report generation date text for different languages"""
    now = datetime.now()
    
    if lang == 'ko':
        return f"보고서 생성일: {now.strftime('%Y년 %m월 %d일 %H:%M')}"
    elif lang == 'en':
        return f"Report Generated: {now.strftime('%B %d, %Y %H:%M')}"
    elif lang == 'vi':
        return f"Báo cáo được tạo: {now.strftime('%d/%m/%Y %H:%M')}"
    return now.strftime('%Y-%m-%d %H:%M')

# Copy all the original functions from step2_dashboard_version4.py here
# (I'll add a placeholder for now, but the actual functions should be copied)

def generate_improved_dashboard(input_html, output_html, month='july', year=2025):
    """개선된 대시보드 HTML 생성 - Version 4.2 (동적 월/년 표시 + 생성일자)
    
    주요 개선사항:
    - 버전 v4.2로 업데이트
    - 동적 월/년 표시
    - 보고서 생성일자 추가
    - 다국어 지원 강화
    
    Args:
        input_html: 입력 HTML 파일 경로
        output_html: 출력 HTML 파일 경로
        month: 월 이름 (예: 'july', 'august')
        year: 년도 (예: 2025)
    """
    
    # Generate dynamic text
    month_year_text_ko = get_month_year_text(month, year, 'ko')
    month_year_text_en = get_month_year_text(month, year, 'en')
    month_year_text_vi = get_month_year_text(month, year, 'vi')
    
    generation_date_ko = get_generation_date_text('ko')
    generation_date_en = get_generation_date_text('en')
    generation_date_vi = get_generation_date_text('vi')
    
    # HTML template with dynamic values
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 대시보드 - Version 4.2</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Copy all styles from original file */
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
            <h1 id="mainTitle">QIP 인센티브 계산 결과 <span class="version-badge">v4.2</span></h1>
            <p id="mainSubtitle">{month_year_text_ko}</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.8;">{generation_date_ko}</p>
        </div>
        
        <!-- Rest of the HTML content -->
    </div>
    
    <script>
        const translations = {{
            ko: {{
                title: 'QIP 인센티브 대시보드',
                subtitle: '{month_year_text_ko}',
                generationDate: '{generation_date_ko}',
                // Other translations...
            }},
            en: {{
                title: 'QIP Incentive Dashboard',
                subtitle: '{month_year_text_en}',
                generationDate: '{generation_date_en}',
                // Other translations...
            }},
            vi: {{
                title: 'Bảng điều khiển khuyến khích QIP',
                subtitle: '{month_year_text_vi}',
                generationDate: '{generation_date_vi}',
                // Other translations...
            }}
        }};
        
        // Language switching logic
        document.getElementById('languageSelector').addEventListener('change', function(e) {{
            const lang = e.target.value;
            const trans = translations[lang];
            
            document.getElementById('mainSubtitle').textContent = trans.subtitle;
            document.getElementById('generationDate').textContent = trans.generationDate;
            // Update other elements...
        }});
    </script>
</body>
</html>"""
    
    # Write the HTML file
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard v4.2 generated successfully!")
    print(f"📁 File: {output_html}")

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate QIP Incentive Dashboard')
    parser.add_argument('--month', type=str, default='july', 
                       help='Month name (e.g., july, august)')
    parser.add_argument('--year', type=int, default=2025,
                       help='Year (e.g., 2025)')
    
    args = parser.parse_args()
    
    # Set up directories
    base_dir = Path(__file__).parent
    root_dir = base_dir.parent
    
    local_output_dir = base_dir / "output_files"
    local_output_dir.mkdir(exist_ok=True)
    
    root_output_dir = root_dir / "output_files"
    root_output_dir.mkdir(exist_ok=True)
    
    # Determine input file based on month/year
    month_num = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }.get(args.month.lower(), '07')
    
    # Try to find the appropriate input file
    input_file = root_output_dir / f"QIP_Incentive_Report_{args.month.capitalize()}_{args.year}.html"
    if not input_file.exists():
        # Fallback to July 2025 if specific month not found
        input_file = root_output_dir / "QIP_Incentive_Report_July_2025.html"
        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
            exit(1)
    
    print(f"✅ Input file: {input_file}")
    
    # Generate output files
    output_file_local = local_output_dir / "dashboard_version4.html"
    output_file_root = root_output_dir / "dashboard_version4.html"
    
    print(f"✅ Output file 1 (local): {output_file_local}")
    print(f"✅ Output file 2 (root): {output_file_root}")
    
    # Generate dashboard with month/year parameters
    generate_improved_dashboard(str(input_file), str(output_file_local), 
                              month=args.month, year=args.year)
    
    # Copy to root folder
    import shutil
    shutil.copy2(str(output_file_local), str(output_file_root))
    print(f"✅ Copied to root folder: {output_file_root}")