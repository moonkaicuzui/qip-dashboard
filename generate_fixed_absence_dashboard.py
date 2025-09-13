#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate fixed absence analytics dashboard with all improvements
- All 12 charts in detailed analysis tab working
- Correct absence rate calculations (around 3%, not 100%)
- Enhanced team and individual detail popups
- Real employee data throughout
"""

import json
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from inject_absence_improvements_fixed import generate_fixed_absence_functions

def read_dashboard_template():
    """Read the latest management dashboard template"""
    dashboard_path = Path(__file__).parent / 'output_files' / 'management_dashboard_2025_08_multilang.html'
    
    if not dashboard_path.exists():
        # Fallback to any available dashboard
        dashboard_files = list(Path(__file__).parent.glob('output_files/management_dashboard_*.html'))
        if dashboard_files:
            dashboard_path = sorted(dashboard_files)[-1]
        else:
            raise FileNotFoundError("No management dashboard found")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        return f.read()

def inject_fixed_absence_code(html_content):
    """Inject the fixed absence analytics code into the dashboard"""
    
    # Generate the fixed JavaScript code
    fixed_js_code = generate_fixed_absence_functions(lang='ko')
    
    # Find the right place to inject the code (after Chart.js but before other scripts)
    injection_point = html_content.find('</script>', html_content.find('new Chart'))
    
    if injection_point == -1:
        # Fallback: inject before closing body tag
        injection_point = html_content.find('</body>')
        html_content = html_content[:injection_point] + f"""
    <script>
        // Fixed Absence Analytics Implementation
        {fixed_js_code}
    </script>
    """ + html_content[injection_point:]
    else:
        # Inject after the found script tag
        injection_point += len('</script>')
        html_content = html_content[:injection_point] + f"""
    
    <script>
        // Fixed Absence Analytics Implementation
        {fixed_js_code}
    </script>
    """ + html_content[injection_point:]
    
    return html_content

def main():
    """Main function to generate the fixed dashboard"""
    
    print("=" * 60)
    print("결근 현황 분석 대시보드 수정 버전 생성")
    print("=" * 60)
    
    try:
        # Read the template
        print("1. 대시보드 템플릿 읽기...")
        html_content = read_dashboard_template()
        
        # Inject fixed absence analytics code
        print("2. 수정된 결근 분석 코드 삽입...")
        html_content = inject_fixed_absence_code(html_content)
        
        # Save the fixed dashboard
        output_path = Path(__file__).parent / 'output_files' / 'management_dashboard_2025_08_absence_fixed.html'
        print(f"3. 최종 대시보드 저장: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("\n✅ 대시보드 생성 완료!")
        print(f"📄 파일 위치: {output_path}")
        print("\n수정된 내용:")
        print("  ✓ 상세분석 탭: 12개 차트 모두 구현 완료")
        print("  ✓ 팀별 탭: 결근율 계산 수정 (3% 수준으로 정상화)")
        print("  ✓ 팀 상세 팝업: 차트 및 팀원 목록 추가")
        print("  ✓ 개인별 탭: 실제 직원 데이터 사용")
        print("  ✓ 개인 상세 팝업: 결근 이력 및 추이 차트 추가")
        
        # Open in browser
        import webbrowser
        import os
        full_path = os.path.abspath(output_path)
        webbrowser.open(f'file://{full_path}')
        print("\n브라우저에서 대시보드가 열립니다...")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())