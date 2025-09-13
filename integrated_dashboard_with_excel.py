#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
통합 인센티브 대시보드 생성 시스템 - Excel Export 기능 포함 버전
dashboard_version4.html의 정확한 UI 복제
실제 인센티브 데이터 사용
Google Drive 연동 기능 포함
Excel Export 기능 추가
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime
import glob
import argparse
from pathlib import Path
import base64

# Import the original dashboard functions
sys.path.append(str(Path(__file__).parent))
from integrated_dashboard_final import (
    load_translations, get_korean_month, get_translation,
    load_incentive_data, generate_dashboard_html,
    sync_google_drive_data
)
from src.create_incentive_excel_export import create_incentive_excel_export

def generate_dashboard_with_excel(month='august', year='2025', sync=False, input_file=None):
    """
    대시보드 생성 (Excel Export 기능 포함)
    """
    
    # Load translations first
    load_translations()
    
    print(f"=== {year}년 {get_korean_month(month)} 인센티브 대시보드 생성 시작 (Excel Export 포함) ===")
    
    # Google Drive 동기화 실행
    if sync:
        print("\n🔄 Google Drive 동기화 시작...")
        # Convert month to number for sync
        month_num = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }.get(month.lower(), 8)
        sync_google_drive_data(month_num, int(year))
    
    # 이전 달 데이터 체크
    prev_month_number = {
        'january': 12, 'february': 1, 'march': 2, 'april': 3,
        'may': 4, 'june': 5, 'july': 6, 'august': 7,
        'september': 8, 'october': 9, 'november': 10, 'december': 11
    }.get(month.lower(), 0)
    
    prev_year = year if prev_month_number < 12 else str(int(year) - 1)
    prev_month_name = ['december', 'january', 'february', 'march', 'april', 'may', 
                       'june', 'july', 'august', 'september', 'october', 'november'][prev_month_number]
    
    # 데이터 로드 - integrated_dashboard_final.py의 함수 사용
    try:
        # load_incentive_data returns a DataFrame
        df = load_incentive_data(month, year, generate_prev=False)
        if df is None or df.empty:
            print(f"❌ 데이터 로드 실패")
            return None
        print(f"✅ 데이터 로드 성공: {len(df)} 행")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return None
    
    # Generate Excel report first
    excel_file_path = None
    try:
        print("\n📊 Excel 보고서 생성 중...")
        # Convert month name to number if needed
        month_num = month if month.isdigit() else str({
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }.get(month.lower(), 8))
        excel_file_path = create_incentive_excel_export(month_num, year)
        if excel_file_path and Path(excel_file_path).exists():
            print(f"✅ Excel 보고서 생성 완료: {excel_file_path}")
        else:
            print("⚠️ Excel 보고서 생성 실패")
    except Exception as e:
        print(f"❌ Excel 보고서 생성 오류: {e}")
    
    # HTML 대시보드 생성 (Excel export 버튼 포함)
    # Generate using the integrated dashboard function
    month_num = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }.get(month.lower(), 8)
    
    html_content = generate_dashboard_html(df, month, int(year), month_num)
    
    # Add Excel export functionality
    if excel_file_path:
        html_content = add_excel_export_to_html(html_content, excel_file_path, month, year)
    
    # 파일 저장
    output_file = f"output_files/dashboard_{year}_{month}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 대시보드 생성 완료: {output_file}")
    
    if excel_file_path:
        print(f"✅ Excel 파일 생성 완료: {excel_file_path}")
    
    return output_file

def add_excel_export_to_html(html_content, excel_file_path, month, year):
    """
    Add Excel export functionality to existing HTML
    """
    
    # Add Excel export button and functionality
    if excel_file_path and Path(excel_file_path).exists():
        # Read the Excel file and convert to base64 for download
        with open(excel_file_path, 'rb') as f:
            excel_data = f.read()
            excel_base64 = base64.b64encode(excel_data).decode('utf-8')
        
        # Insert the export button in the header
        export_button_html = f'''
                <button id="exportExcelBtn" class="btn btn-success" onclick="downloadExcel()" style="background: rgba(34,197,94,0.9); border: none; padding: 10px 20px; border-radius: 8px; color: white; font-weight: 500;">
                    <i class="fas fa-file-excel"></i> Excel Export
                </button>'''
        
        # Add JavaScript for Excel download
        excel_download_script = f'''
        <script>
        // Excel export data
        const excelData = "{excel_base64}";
        const excelFileName = "Incentive_Report_{year}_{month}.xlsx";
        
        function downloadExcel() {{
            // Convert base64 to blob
            const byteCharacters = atob(excelData);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {{
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }}
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], {{type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}});
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = excelFileName;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Show success message
            showNotification('Excel 파일 다운로드가 시작되었습니다!', 'success');
        }}
        
        function showNotification(message, type) {{
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${{type === 'success' ? '#10b981' : '#ef4444'}};
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                z-index: 10000;
                animation: slideIn 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {{
                    document.body.removeChild(notification);
                }}, 300);
            }}, 3000);
        }}
        
        // Add animation styles
        if (!document.getElementById('exportAnimations')) {{
            const style = document.createElement('style');
            style.id = 'exportAnimations';
            style.textContent = `
                @keyframes slideIn {{
                    from {{ transform: translateX(100%); opacity: 0; }}
                    to {{ transform: translateX(0); opacity: 1; }}
                }}
                @keyframes slideOut {{
                    from {{ transform: translateX(0); opacity: 1; }}
                    to {{ transform: translateX(100%); opacity: 0; }}
                }}
            `;
            document.head.appendChild(style);
        }}
        </script>'''
        
        # Insert the export button into the header section
        html_content = html_content.replace(
            '</select>\n            </div>',
            f'</select>\n{export_button_html}\n            </div>'
        )
        
        # Add the Excel download script before closing body tag
        html_content = html_content.replace(
            '</body>',
            f'{excel_download_script}\n</body>'
        )
    
    return html_content

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='QIP 인센티브 대시보드 생성 (Excel Export 포함)')
    parser.add_argument('--month', type=str, default='august', help='월 (예: august)')
    parser.add_argument('--year', type=str, default='2025', help='연도 (예: 2025)')
    parser.add_argument('--sync', action='store_true', help='Google Drive 동기화 실행')
    parser.add_argument('--input', type=str, help='입력 파일 경로 (선택사항)')
    
    args = parser.parse_args()
    
    # 대시보드 생성
    output_file = generate_dashboard_with_excel(
        month=args.month,
        year=args.year,
        sync=args.sync,
        input_file=args.input
    )
    
    if output_file:
        print(f"\n✨ 대시보드 생성 완료!")
        print(f"📄 파일 위치: {output_file}")
        print(f"📊 Excel Export 기능이 포함되었습니다.")
        print(f"\n브라우저에서 파일을 열어 확인하세요.")
        
        # 자동으로 브라우저에서 열기 (선택사항)
        import webbrowser
        import os
        full_path = os.path.abspath(output_file)
        webbrowser.open(f'file://{full_path}')

if __name__ == "__main__":
    main()