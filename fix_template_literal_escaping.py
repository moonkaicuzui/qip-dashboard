#!/usr/bin/env python3
"""
JavaScript template literal escaping 오류 수정 스크립트
Python f-string에서 JavaScript template literal을 올바르게 생성하도록 수정
"""

import re
import sys

def fix_template_literals():
    """Python 코드에서 잘못된 template literal 패턴 수정"""

    # integrated_dashboard_final.py 읽기
    file_path = 'integrated_dashboard_final.py'
    print(f"📖 {file_path} 파일 읽는 중...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 수정이 필요한 패턴들
    patterns_to_fix = [
        # ${{getTranslation(...) 패턴을 ${getTranslation(...) 로 변경
        (r'\$\{\{getTranslation\(', r'${getTranslation('),

        # 닫는 중괄호도 수정 (}} → })
        # getTranslation 함수 호출 뒤의 }}를 }로 변경
        (r"(getTranslation\([^)]+\)[^}]*)\}\}", r"\1}"),

        # 기타 ${{ 패턴들도 수정
        (r'\$\{\{([a-zA-Z_][a-zA-Z0-9_]*)', r'${\1'),  # 변수명 시작 패턴
        (r'\$\{\{(\()', r'${('),  # 함수 호출 시작 패턴
    ]

    changes_made = 0

    for pattern, replacement in patterns_to_fix:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  🔍 패턴 발견: {pattern[:30]}... ({len(matches)}개)")
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)

    # 특별 케이스: 중첩된 template literal 수정
    # 예: ${days}${{getTranslation → ${days}${getTranslation
    content = re.sub(r'\}\$\{\{', r'}${', content)

    # 잘못된 이중 중괄호 수정
    # 예: '}} VND' → '} VND' (template literal 컨텍스트에서)
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # JavaScript 코드가 포함된 라인 찾기 (f-string 내부)
        if 'getTranslation' in line and '}}' in line:
            # template literal 내부의 }} 를 }로 수정
            # 하지만 Python f-string의 정상적인 }}는 유지
            if '${' in line:  # JavaScript template literal이 있는 경우
                # getTranslation 이후의 }}를 }로 변경
                line = re.sub(r"(getTranslation\([^)]+\)[^}]*)\}\}(?!')", r"\1}", line)
                changes_made += 1
        fixed_lines.append(line)

    content = '\n'.join(fixed_lines)

    # 백업 파일 생성
    if content != original_content:
        print(f"\n💾 백업 파일 생성 중...")
        with open(f'{file_path}.backup', 'w', encoding='utf-8') as f:
            f.write(original_content)

        # 수정된 내용 저장
        print(f"✏️ 수정된 내용 저장 중...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n✅ 총 {changes_made}개의 패턴 수정 완료!")

        # 수정 예시 보여주기
        print("\n📋 수정 예시:")
        print("  변경 전: ${{getTranslation('key', lang) || 'default'}}")
        print("  변경 후: ${getTranslation('key', lang) || 'default'}")

        return True
    else:
        print("\n⚠️ 수정할 패턴을 찾지 못했습니다.")
        return False

def verify_fix():
    """수정이 올바르게 되었는지 검증"""
    print("\n🔍 수정 사항 검증 중...")

    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 잘못된 패턴이 남아있는지 확인
    bad_patterns = [
        r'\$\{\{getTranslation',
        r'\}\$\{\{',
    ]

    issues = []
    for pattern in bad_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append((pattern, len(matches)))

    if issues:
        print("❌ 아직 수정되지 않은 패턴이 있습니다:")
        for pattern, count in issues:
            print(f"  - {pattern}: {count}개")
        return False
    else:
        print("✅ 모든 패턴이 올바르게 수정되었습니다!")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("JavaScript Template Literal 수정 스크립트")
    print("=" * 60)

    # 수정 실행
    if fix_template_literals():
        # 검증
        if verify_fix():
            print("\n🎉 수정이 성공적으로 완료되었습니다!")
            print("\n다음 단계:")
            print("1. python integrated_dashboard_final.py --month 9 --year 2025")
            print("2. 브라우저에서 대시보드 확인")
            sys.exit(0)
        else:
            print("\n⚠️ 일부 패턴이 완전히 수정되지 않았습니다. 수동 확인이 필요합니다.")
            sys.exit(1)
    else:
        print("\n❌ 수정 실패")
        sys.exit(1)