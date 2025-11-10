#!/usr/bin/env python3
"""
TYPE 테이블 자동 로딩 구문 오류 수정
- JavaScript 코드의 중괄호를 이중 중괄호로 수정
"""

import re

def fix_syntax_error():
    print("🔧 TYPE 테이블 구문 오류 수정 시작...")

    # integrated_dashboard_final.py 읽기
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 문제가 되는 부분 찾아서 수정
    # Line 7849 근처의 setTimeout 블록을 찾아서 중괄호를 이중으로 수정

    # 잘못된 패턴: setTimeout(() => { ... })
    wrong_pattern = r'''// TYPE 테이블 초기 생성 \(데이터 로드 직후\)
            setTimeout\(\(\) => \{
                if \(typeof generateTypeTable === 'function'\) \{
                    console\.log\('Calling generateTypeTable after data load\.\.\.'\);
                    generateTypeTable\(\);
                \} else \{
                    console\.error\('generateTypeTable function not found'\);
                \}
            \}, 100\);'''

    # 올바른 패턴: 중괄호를 이중으로
    correct_pattern = '''// TYPE 테이블 초기 생성 (데이터 로드 직후)
            setTimeout(() => {{
                if (typeof generateTypeTable === 'function') {{
                    console.log('Calling generateTypeTable after data load...');
                    generateTypeTable();
                }} else {{
                    console.error('generateTypeTable function not found');
                }}
            }}, 100);'''

    # 수정 적용
    content = re.sub(wrong_pattern, correct_pattern, content, flags=re.DOTALL)

    # 다른 잠재적 문제도 수정: window.generateTypeTable = generateTypeTable; 부분
    # 이것도 f-string 안에 있다면 문제가 될 수 있음

    # 기존의 단일 중괄호를 이중 중괄호로 변경 (JavaScript 코드 내에서)
    # 하지만 이미 이중인 것은 건드리지 않음

    # Line 7848-7853 근처 확인
    lines_to_check = content.split('\n')
    for i in range(7845, min(7855, len(lines_to_check))):
        if i < len(lines_to_check):
            line = lines_to_check[i]
            # 단일 중괄호를 찾아서 이중으로 (이미 이중이 아닌 경우)
            if '{' in line and '{{' not in line and 'function' in line:
                lines_to_check[i] = line.replace('{', '{{').replace('}', '}}')

    # 다시 합치기
    content = '\n'.join(lines_to_check)

    # 수정된 파일 저장
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 구문 오류 수정 완료!")
    print("\n다음 명령어로 대시보드를 재생성하세요:")
    print("  python integrated_dashboard_final.py --month 10 --year 2025")

if __name__ == "__main__":
    fix_syntax_error()