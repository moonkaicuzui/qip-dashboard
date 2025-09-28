#!/usr/bin/env python3
"""
JavaScript template literal 정밀 수정 스크립트
특정 패턴만 정확하게 수정하여 JavaScript 파싱 오류 해결
"""

import re

def fix_template_literals_precise():
    """특정 getTranslation 패턴만 수정"""

    file_path = 'integrated_dashboard_final.py'
    print(f"📖 {file_path} 파일 읽는 중...")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 백업 생성
    with open(f'{file_path}.backup2', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("🔍 문제 패턴 찾는 중...")

    # 수정이 필요한 특정 라인 패턴들
    # ${{getTranslation을 ${getTranslation으로 변경해야 함
    patterns_to_fix = [
        # Pattern: ${{getTranslation(...) || 'default'}}
        # Fix to: ${getTranslation(...) || 'default'}
        (r'\$\{\{getTranslation\(([^)]+)\)([^}]*)\}\}', r'${getTranslation(\1)\2}'),

        # Pattern: }${{getTranslation
        # Fix to: }${getTranslation
        (r'\}\$\{\{getTranslation', r'}${getTranslation'),

        # Pattern: 변수 참조 ${{variable}}
        # Fix to: ${variable}
        (r'\$\{\{([a-zA-Z_][a-zA-Z0-9_.]*)\}\}', r'${\1}'),

        # Pattern: 함수 호출 ${{functionCall()}}
        # Fix to: ${functionCall()}
        (r'\$\{\{([a-zA-Z_][a-zA-Z0-9_]*\([^}]*\))\}\}', r'${\1}'),
    ]

    changes_made = 0
    modified_lines = []

    for i, line in enumerate(lines, 1):
        original_line = line

        # JavaScript 코드가 포함된 라인에서만 수정
        if 'getTranslation' in line and '${{' in line:
            for pattern, replacement in patterns_to_fix:
                if re.search(pattern, line):
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        print(f"  라인 {i}: 패턴 수정됨")
                        line = new_line
                        changes_made += 1
                        break

        # 특정 문제 라인들 직접 처리 (오류가 발생한 라인들)
        problem_lines = [1406, 1418, 1430, 1454, 1489, 1495, 1501, 1507, 1518,
                        1529, 1532, 1535, 1539, 1540, 1544, 1555, 9038, 9064]

        if i in problem_lines:
            # ${{ 를 ${ 로 변경 (getTranslation 앞에만)
            line = re.sub(r'\$\{\{(getTranslation)', r'${\1', line)
            # getTranslation 뒤의 }} 를 } 로 변경 (JavaScript block close가 아닌 경우)
            line = re.sub(r'(getTranslation\([^)]+\)[^}]*)\}\}(?=[\'"<])', r'\1}', line)

            if line != original_line:
                print(f"  라인 {i}: 특별 처리됨")
                changes_made += 1

        modified_lines.append(line)

    # 수정된 내용 저장
    print(f"\n✏️ 수정된 내용 저장 중...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)

    print(f"\n✅ 총 {changes_made}개 라인 수정 완료!")

    return True

def verify_syntax():
    """Python 구문 오류 확인"""
    import ast
    import sys

    print("\n🔍 Python 구문 확인 중...")

    try:
        with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
            source = f.read()

        # Python 구문 체크
        compile(source, 'integrated_dashboard_final.py', 'exec')
        print("✅ Python 구문 오류 없음!")
        return True

    except SyntaxError as e:
        print(f"❌ Python 구문 오류 발견:")
        print(f"  라인 {e.lineno}: {e.msg}")
        print(f"  {e.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("JavaScript Template Literal 정밀 수정 스크립트")
    print("=" * 60)

    if fix_template_literals_precise():
        if verify_syntax():
            print("\n🎉 수정이 성공적으로 완료되었습니다!")
            print("\n다음 단계:")
            print("1. python integrated_dashboard_final.py --month 9 --year 2025")
            print("2. 브라우저에서 대시보드 확인")
        else:
            print("\n⚠️ Python 구문 오류가 있습니다. 백업에서 복원하세요:")
            print("  cp integrated_dashboard_final.py.backup2 integrated_dashboard_final.py")