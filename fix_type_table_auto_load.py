#!/usr/bin/env python3
"""
TYPE 테이블 자동 로딩 수정 스크립트
- generateTypeTable 함수를 전역으로 노출
- 데이터 로딩 후 자동으로 TYPE 테이블 생성
- showTab('summary') 호출 시에도 TYPE 테이블 재생성
"""

import re

def fix_type_table_loading():
    print("🔧 TYPE 테이블 자동 로딩 수정 시작...")

    # 1. integrated_dashboard_final.py 읽기
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. generateTypeTable 함수가 window 객체에 노출되었는지 확인
    # 함수 정의 후 즉시 window에 할당하도록 수정

    # generateTypeTable 함수 정의를 찾아서 바로 아래에 window 할당 추가
    pattern = r'(function generateTypeTable\(\) \{[^}]*?\n\s+\}\})'

    def add_window_exposure(match):
        function_def = match.group(1)
        # 함수 정의 바로 뒤에 window 노출 추가
        return function_def + '\n            window.generateTypeTable = generateTypeTable;'

    # 이미 window.generateTypeTable이 없으면 추가
    if 'window.generateTypeTable = generateTypeTable;' not in content:
        content = re.sub(pattern, add_window_exposure, content, flags=re.DOTALL)

    # 3. DOMContentLoaded 내에서 초기 호출 확인
    # showTab('summary') 다음에 generateTypeTable() 호출 추가

    # showTab('summary') 호출 찾기
    showtab_pattern = r"(showTab\('summary'\);)"

    # generateTypeTable 호출이 없으면 추가
    if not re.search(r"showTab\('summary'\);\s*generateTypeTable\(\);", content):
        replacement = r"\1\n            generateTypeTable();  // TYPE 테이블 초기 생성"
        content = re.sub(showtab_pattern, replacement, content, count=1)

    # 4. showTab 함수 내에서 summary 탭 선택 시 TYPE 테이블 재생성
    # showTab 함수를 찾아서 summary 탭 처리 부분에 generateTypeTable() 추가

    showtab_func_pattern = r'(function showTab\(tabName\) \{[^}]*?if \(tabName === \'summary\'\) \{[^}]*?)'

    def add_type_table_regeneration(match):
        func_content = match.group(1)
        # summary 탭 처리 부분에 generateTypeTable 호출이 없으면 추가
        if 'generateTypeTable();' not in func_content:
            return func_content + '\n                generateTypeTable();  // summary 탭 표시 시 TYPE 테이블 재생성'
        return func_content

    content = re.sub(showtab_func_pattern, add_type_table_regeneration, content, flags=re.DOTALL)

    # 5. 데이터 로딩 직후 TYPE 테이블 생성 확인
    # window.employeeData = employeeData; 다음에 타임아웃으로 호출

    data_load_pattern = r'(window\.employeeData = employeeData;[^}]*?console\.log\(\'Employee data loaded successfully:\'[^}]*?\);)'

    def ensure_type_table_call(match):
        data_load = match.group(1)
        # TYPE 테이블 호출이 없으면 추가
        if 'setTimeout(() => {' not in data_load:
            type_table_call = '''

            // TYPE 테이블 초기 생성 (데이터 로드 직후)
            setTimeout(() => {
                if (typeof generateTypeTable === 'function') {
                    console.log('Calling generateTypeTable after data load...');
                    generateTypeTable();
                } else {
                    console.error('generateTypeTable function not found');
                }
            }, 100);'''
            return data_load + type_table_call
        return data_load

    content = re.sub(data_load_pattern, ensure_type_table_call, content, flags=re.DOTALL)

    # 6. 전역 함수 노출 섹션 확인 및 추가
    # DOMContentLoaded 끝 부분에 전역 함수 노출 코드 추가

    # 먼저 window.showTab 등이 노출되는 부분 찾기
    if 'window.showTab = showTab;' in content:
        # 이미 전역 노출 섹션이 있으면 generateTypeTable 추가
        if 'window.generateTypeTable = generateTypeTable;' not in content:
            expose_pattern = r'(window\.showTab = showTab;)'
            content = re.sub(
                expose_pattern,
                r'\1\n        window.generateTypeTable = generateTypeTable;',
                content
            )
    else:
        # 전역 노출 섹션이 없으면 새로 생성
        # DOMContentLoaded 끝 부분을 찾아서 추가
        dom_end_pattern = r'(}\);[\s]*//[\s]*DOMContentLoaded)'
        if re.search(dom_end_pattern, content):
            global_expose = '''
        // 전역 함수로 노출
        window.showTab = showTab;
        window.generateTypeTable = generateTypeTable;
        window.changeLanguage = changeLanguage;
        window.openPositionModal = openPositionModal;
        window.generateEmployeeTable = generateEmployeeTable;
        window.generatePositionTables = generatePositionTables;

    });  // DOMContentLoaded'''
            content = re.sub(dom_end_pattern, global_expose, content)

    # 7. 수정된 파일 저장
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ TYPE 테이블 자동 로딩 수정 완료!")
    print("\n주요 수정 사항:")
    print("  1. generateTypeTable 함수를 window 객체에 노출")
    print("  2. 데이터 로딩 후 자동으로 TYPE 테이블 생성")
    print("  3. summary 탭 선택 시 TYPE 테이블 재생성")
    print("  4. DOMContentLoaded에서 초기 TYPE 테이블 생성")
    print("\n다음 명령어로 대시보드를 재생성하세요:")
    print("  python integrated_dashboard_final.py --month 10 --year 2025")
    print("  또는")
    print("  ./action.sh")

if __name__ == "__main__":
    fix_type_table_loading()