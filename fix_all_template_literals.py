#!/usr/bin/env python3
"""
모든 JavaScript template literal 문제를 해결하는 스크립트
${{getTranslation 패턴을 string concatenation으로 변경
"""

import re
import sys

def fix_all_template_literals():
    """모든 problematic template literals를 string concatenation으로 변경"""

    file_path = 'integrated_dashboard_final.py'
    print(f"📖 {file_path} 파일 읽는 중...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 백업 생성
    with open(f'{file_path}.backup_final', 'w', encoding='utf-8') as f:
        f.write(original_content)

    print("🔍 문제 패턴 찾는 중...")

    # 수정 패턴들
    replacements = [
        # 기본 패턴: ${{getTranslation(...) || 'default'}}
        # JavaScript template literal 내에서 변환
        (r"\$\{\{getTranslation\('([^']+)',\s*currentLanguage\)\s*\|\|\s*'([^']+)'\}\}",
         r"' + (getTranslation('\1', currentLanguage) || '\2') + '"),

        # 변수와 함께: ${variable}${{getTranslation(...)}}
        (r"\$\{([^}]+)\}\$\{\{getTranslation\('([^']+)',\s*currentLanguage\)\s*\|\|\s*'([^']+)'\}\}",
         r"' + \1 + (getTranslation('\2', currentLanguage) || '\3') + '"),

        # 단순 변수 참조: ${{variable}}
        (r"\$\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}",
         r"' + \1 + '"),

        # toLocaleString과 함께: ${{variable.toLocaleString(...)}}
        (r"\$\{\{([^}]+\.toLocaleString\([^)]*\))\}\}",
         r"' + \1 + '"),

        # 복잡한 표현식: ${{expression}}
        (r"\$\{\{([^}]+)\}\}",
         r"' + (\1) + '"),
    ]

    changes_made = 0
    for pattern, replacement in replacements:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  🔍 패턴 발견: {pattern[:50]}... ({len(matches)}개)")
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)

    # 특수 케이스 처리 - template literal 내부에서 string concatenation으로 전환된 것들 정리
    # 예: <tag>내용' + expr + '</tag> → 올바른 형태 유지
    content = re.sub(r"'\s*\+\s*'", "", content)  # 빈 문자열 연결 제거

    print(f"\n✅ 총 {changes_made}개 패턴 수정 완료!")

    # 수정된 내용 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def verify_syntax():
    """Python 구문 체크"""
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
        print(f"  문제 코드: {e.text}")
        print("\n💡 백업 복원 명령어:")
        print("  cp integrated_dashboard_final.py.backup_final integrated_dashboard_final.py")
        return False

def count_remaining():
    """남은 문제 패턴 확인"""
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    problematic = re.findall(r'\$\{\{', content)
    if problematic:
        print(f"\n⚠️ 아직 {len(problematic)}개의 '${{{{' 패턴이 남아있습니다.")
        # 샘플 보여주기
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '${{' in line:
                print(f"  라인 {i}: {line.strip()[:80]}...")
                if i > 5:  # 처음 5개만 보여주기
                    break
    else:
        print("\n✅ 모든 '${{{{' 패턴이 제거되었습니다!")

if __name__ == "__main__":
    print("=" * 60)
    print("전체 JavaScript Template Literal 수정 스크립트")
    print("=" * 60)

    if fix_all_template_literals():
        if verify_syntax():
            count_remaining()
            print("\n🎉 수정이 성공적으로 완료되었습니다!")
            print("\n다음 단계:")
            print("1. python integrated_dashboard_final.py --month 9 --year 2025")
            print("2. 브라우저에서 대시보드 확인")
            sys.exit(0)
        else:
            print("\n❌ Python 구문 오류로 인해 수정 실패")
            sys.exit(1)
    else:
        print("\n❌ 수정 실패")
        sys.exit(1)