#!/usr/bin/env python3
"""
TYPE 테이블 완전 수정 스크립트
- 직원 데이터 base64 인코딩 확인
- HTML에 데이터 임베딩 수정
- generateTypeTable 전역 노출
"""

import re

def fix_type_table_completely():
    print("🔧 TYPE 테이블 완전 수정 시작...")

    # 1. integrated_dashboard_final.py 읽기
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 직원_json_base64가 템플릿에서 사용되는 부분 확인
    # 이미 line 7767에 있음: {직원_json_base64}
    # 문제는 이 변수가 generate_dashboard_html 함수 내에서 정의되지 않았을 수 있음

    # generate_dashboard_html 함수 안에서 직원 데이터 처리 부분 찾기
    # 직원 = excel_dashboard_data['직원'] 이후에 base64 인코딩 추가

    # 함수 내에서 직원 데이터 처리 부분을 찾아서 base64 인코딩 추가
    pattern = r'(# 직원 데이터 preparation.*?\n)([\s\S]*?)(\s+# Generate HTML template)'

    def add_base64_encoding(match):
        prefix = match.group(1)
        middle = match.group(2)
        suffix = match.group(3)

        # base64 인코딩 코드가 없으면 추가
        if '직원_json_base64' not in middle:
            encoding_code = '''
    # Base64 인코딩 추가 (JavaScript에서 안전하게 사용하기 위해)
    import base64

    # 직원 데이터를 JSON으로 변환하고 base64 인코딩
    직원_json_str = json.dumps(직원_clean, ensure_ascii=False, separators=(',', ':'))
    직원_json_base64 = base64.b64encode(직원_json_str.encode('utf-8')).decode('ascii')

    print(f"🔍 [DEBUG] 직원 데이터: {len(직원_clean)}명")
    print(f"🔍 [DEBUG] Base64 인코딩 길이: {len(직원_json_base64)} characters")
'''
            return prefix + middle + encoding_code + suffix
        return prefix + middle + suffix

    # content = re.sub(pattern, add_base64_encoding, content, flags=re.DOTALL)

    # 3. generateTypeTable 함수를 전역으로 노출
    # window.generateTypeTable = generateTypeTable; 추가
    pattern = r'(function generateTypeTable\(\) \{[\s\S]*?\n\s+\}\})'

    def expose_globally(match):
        func = match.group(1)
        # 함수 정의 직후에 전역 노출 추가
        if 'window.generateTypeTable = generateTypeTable;' not in content:
            return func + '\n            window.generateTypeTable = generateTypeTable;'
        return func

    content = re.sub(pattern, expose_globally, content, flags=re.DOTALL)

    # 4. DOMContentLoaded에서 generateTypeTable 호출 확인
    # showTab('summary'); 다음에 generateTypeTable(); 호출
    pattern = r"(showTab\('summary'\);)"
    if 'generateTypeTable();' not in content:
        replacement = r"\1\n            generateTypeTable();  // TYPE 테이블 초기 생성"
        content = re.sub(pattern, replacement, content, count=1)

    # 5. showTab 함수에서 summary 탭 선택 시 TYPE 테이블 재생성
    pattern = r"(if \(tabName === 'summary'\) \{[^}]*?)(\})"

    def add_regenerate(match):
        func_body = match.group(1)
        closing = match.group(2)
        if 'generateTypeTable();' not in func_body:
            return func_body + '\n                generateTypeTable();  // TYPE 테이블 재생성' + closing
        return func_body + closing

    content = re.sub(pattern, add_regenerate, content, count=1)

    # 6. 전역 함수 노출 섹션 추가/업데이트
    # DOMContentLoaded 끝 부분에 전역 노출 확인
    if 'window.showTab = showTab;' not in content:
        # 전역 노출 섹션이 없으면 추가
        dom_end_pattern = r'(\}\);[\s]*//[\s]*DOMContentLoaded)'
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
    elif 'window.generateTypeTable = generateTypeTable;' not in content:
        # showTab은 있지만 generateTypeTable이 없으면 추가
        pattern = r'(window\.showTab = showTab;)'
        content = re.sub(pattern, r'\1\n        window.generateTypeTable = generateTypeTable;', content)

    # 7. 파일 저장
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ TYPE 테이블 완전 수정 완료!")
    print("\n주요 수정 사항:")
    print("  1. generateTypeTable 함수 전역 노출")
    print("  2. DOMContentLoaded에서 TYPE 테이블 초기 생성")
    print("  3. summary 탭 선택 시 TYPE 테이블 재생성")
    print("  4. 전역 함수 노출 섹션 업데이트")
    print("\n다음 명령어로 대시보드를 재생성하세요:")
    print("  python integrated_dashboard_final.py --month 10 --year 2025")

if __name__ == "__main__":
    fix_type_table_completely()