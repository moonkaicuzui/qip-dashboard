#!/usr/bin/env python3
"""
TYPE 테이블 최종 수정 스크립트
- 전역 함수 노출 문제 완전 해결
- 자동 데이터 로딩 및 테이블 생성
"""

import re

def fix_type_table_final():
    print("🔧 TYPE 테이블 최종 수정 시작...")

    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. DOMContentLoaded 이벤트 리스너 내부를 찾기
    # 전역 노출이 필요한 모든 함수들을 window 객체에 할당

    # DOMContentLoaded 끝 부분 찾기 (대략 15700번째 줄 근처)
    # showEmployeeDetail 함수 이후에 전역 노출 코드 추가

    pattern = r'(window\.showEmployeeDetail = showEmployeeDetail;)'

    if 'window.generateTypeTable = generateTypeTable;' not in content:
        # showEmployeeDetail 노출 직후에 다른 함수들도 노출
        replacement = r'''\1
        window.generateTypeTable = generateTypeTable;
        window.showTab = showTab;
        window.changeLanguage = changeLanguage;
        window.openPositionModal = openPositionModal;'''

        content = re.sub(pattern, replacement, content, count=1)

    # 2. generateTypeTable 함수가 데이터 로드 직후 호출되도록 수정
    # 데이터가 로드된 직후 (line 7844-7845 근처)

    pattern = r'(window\.employeeData = employeeData;\s*console\.log\(\'Employee data loaded successfully:\'[^;]*\);)'

    if not re.search(r'generateTypeTable\(\);.*?// Initial TYPE table', content):
        replacement = r'''\1

            // Initial TYPE table generation right after data load
            if (typeof generateTypeTable === 'function') {
                generateTypeTable();
                console.log('TYPE table generated on data load');
            }'''

        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 3. showTab('summary') 호출 시에도 generateTypeTable 호출
    # DOMContentLoaded 내부에서 초기 showTab('summary') 호출 후

    pattern = r"(showTab\('summary'\);)(?!\s*generateTypeTable)"
    replacement = r'''\1
            generateTypeTable();  // Generate TYPE table after showing summary tab'''

    content = re.sub(pattern, replacement, content)

    # 4. showTab 함수 내부에서 summary 탭 선택 시 TYPE 테이블 재생성
    # if (tabName === 'summary') 블록 내부에 추가

    pattern = r"(if \(tabName === 'summary'\) \{[^}]*?)(document\.getElementById\('summaryContent'\)\.style\.display = 'block';)"

    def add_type_table_call(match):
        condition = match.group(1)
        display_line = match.group(2)

        if 'generateTypeTable();' not in condition:
            return condition + display_line + '''
                if (typeof generateTypeTable === 'function') {
                    generateTypeTable();  // Regenerate TYPE table when summary tab is shown
                }'''
        return condition + display_line

    content = re.sub(pattern, add_type_table_call, content, flags=re.DOTALL)

    # 5. 파일 저장
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ TYPE 테이블 최종 수정 완료!")
    print("\n주요 수정 사항:")
    print("  1. 전역 함수 노출 완료 (window.generateTypeTable)")
    print("  2. 데이터 로드 직후 TYPE 테이블 자동 생성")
    print("  3. Summary 탭 전환 시 TYPE 테이블 재생성")
    print("\n다음 명령어로 대시보드를 재생성하세요:")
    print("  python integrated_dashboard_final.py --month 10 --year 2025")
    print("  또는")
    print("  ./action.sh")

if __name__ == "__main__":
    fix_type_table_final()