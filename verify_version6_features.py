#!/usr/bin/env python3
"""Version 6 핵심 기능 검증"""

import os
from bs4 import BeautifulSoup

def verify_features():
    """Version 6의 핵심 기능 검증"""
    
    v6_file = 'output_files/Incentive_Dashboard_2025_09_Version_6.html'
    
    with open(v6_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    print("🔍 Version 6 핵심 기능 검증")
    print("="*60)
    
    # 1. 데이터 검증
    has_employee_data = 'window.employeeData' in content
    has_excel_data = 'window.excelDashboardData' in content
    has_dashboard_data = 'window.dashboardData' in content
    
    print(f"✅ Employee Data: {'있음' if has_employee_data else '없음'}")
    print(f"✅ Excel Dashboard Data: {'있음' if has_excel_data else '없음'}")
    print(f"✅ Dashboard Data: {'있음' if has_dashboard_data else '없음'}")
    
    # 2. 탭 검증
    tabs = soup.find_all('div', class_='tab')
    print(f"\n📑 탭 개수: {len(tabs)}개")
    for tab in tabs:
        print(f"   - {tab.text.strip()}")
    
    # 3. 언어 지원 검증
    has_ko = 'ko:' in content or '"ko"' in content
    has_en = 'en:' in content or '"en"' in content  
    has_vi = 'vi:' in content or '"vi"' in content
    
    print(f"\n🌐 언어 지원:")
    print(f"   - 한국어: {'✅' if has_ko else '❌'}")
    print(f"   - English: {'✅' if has_en else '❌'}")
    print(f"   - Tiếng Việt: {'✅' if has_vi else '❌'}")
    
    # 4. 주요 JavaScript 함수
    js_functions = [
        'changeLanguage',
        'showTab',
        'updateAllTexts',
        'showEmployeeDetail',
        'filterTable',
        'drawOrgChart',
        'drawCollapsibleOrgChart'
    ]
    
    print(f"\n🔧 JavaScript 함수:")
    for func in js_functions:
        exists = f'function {func}' in content
        print(f"   - {func}: {'✅' if exists else '❌'}")
    
    # 5. CSS 스타일
    has_gradient = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' in content
    has_bootstrap = 'bootstrap@5.1.3' in content
    
    print(f"\n🎨 스타일:")
    print(f"   - Purple Gradient: {'✅' if has_gradient else '❌'}")
    print(f"   - Bootstrap 5: {'✅' if has_bootstrap else '❌'}")
    
    # 6. 차트 라이브러리
    has_chartjs = 'chart.js' in content.lower()
    has_d3 = 'd3js.org/d3.v7' in content or 'd3.v7' in content
    
    print(f"\n📊 차트 라이브러리:")
    print(f"   - Chart.js: {'✅' if has_chartjs else '❌'}")
    print(f"   - D3.js: {'✅' if has_d3 else '❌'}")
    
    print("="*60)
    print("✨ Version 6 검증 완료!")

if __name__ == "__main__":
    verify_features()
