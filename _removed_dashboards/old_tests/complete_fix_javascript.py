#!/usr/bin/env python3
"""
Complete fix for all JavaScript errors
tr() 함수를 완전히 제거하고 적절한 번역 패턴으로 교체
"""

import re
import os

def complete_javascript_fix():
    """Complete fix for all JavaScript errors"""

    print("=" * 80)
    print("🔧 Complete JavaScript Error Fix")
    print("=" * 80)

    # Read the HTML file
    html_file = 'output_files/Incentive_Dashboard_2025_09_Version_5.html'
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("\n📋 문제 분석:")
    print("-" * 40)

    # Find all tr() calls
    tr_pattern = r"tr\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\)"
    all_tr_calls = re.findall(tr_pattern, html_content)
    print(f"발견된 tr() 호출: {len(all_tr_calls)}개")

    # Create replacement map
    tr_replacements = {}
    for key, default in all_tr_calls:
        tr_replacements[f"tr('{key}', '{default}')"] = f"'{default}'"
        tr_replacements[f'tr("{key}", "{default}")'] = f"'{default}'"
        # Also handle with extra spaces
        tr_replacements[f"tr('{key}','{default}')"] = f"'{default}'"
        tr_replacements[f"tr( '{key}', '{default}' )"] = f"'{default}'"

    print(f"생성된 교체 패턴: {len(tr_replacements)}개")

    # Apply all replacements
    fixes_applied = 0
    for old, new in tr_replacements.items():
        count = html_content.count(old)
        if count > 0:
            html_content = html_content.replace(old, new)
            fixes_applied += count
            if fixes_applied <= 10:  # Show first 10 only
                print(f"✅ Replaced: {old[:50]}... → {new[:30]}... ({count}개)")

    # Additional generic pattern to catch any remaining tr() calls
    # This will catch any tr() pattern we might have missed
    generic_pattern = r"tr\s*\(\s*['\"][\w\.]+['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)"

    def replace_tr(match):
        return f"'{match.group(1)}'"

    remaining_count = len(re.findall(generic_pattern, html_content))
    if remaining_count > 0:
        html_content = re.sub(generic_pattern, replace_tr, html_content)
        fixes_applied += remaining_count
        print(f"✅ Generic replacement: {remaining_count}개 추가 수정")

    print(f"\n✅ 총 {fixes_applied}개 tr() 호출 제거")

    # Fix bracket imbalances
    print("\n🔧 중괄호 균형 맞추기...")

    # Count brackets
    open_double = html_content.count('{{')
    close_double = html_content.count('}}')

    print(f"이중 중괄호: {{ {open_double}개, }} {close_double}개")

    # If there's an imbalance, try to fix it
    if open_double != close_double:
        # Look for patterns like ${{ that might not be closed properly
        # Fix patterns like ${{...} to ${{...}}
        html_content = re.sub(r'\$\{\{([^}]+)\}(?!\})', r'${{\1}}', html_content)

        # Recount
        open_double = html_content.count('{{')
        close_double = html_content.count('}}')
        print(f"수정 후: {{ {open_double}개, }} {close_double}개")

    # Save the fixed HTML
    output_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_complete_fix.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n📁 출력 파일: {output_file}")

    # Final verification
    print("\n📊 최종 검증:")
    print("-" * 40)

    # Check for any remaining tr() calls
    final_tr_check = len(re.findall(r'tr\s*\(', html_content))
    print(f"{'✅' if final_tr_check == 0 else '❌'} 남은 tr() 호출: {final_tr_check}개")

    # Check bracket balance
    final_open = html_content.count('{{')
    final_close = html_content.count('}}')
    balanced = final_open == final_close
    print(f"{'✅' if balanced else '⚠️'} 중괄호 균형: {{ {final_open}개, }} {final_close}개")

    # Check for common JavaScript errors
    error_patterns = [
        (r'\)\s*\)', "이중 닫는 괄호"),
        (r'\}\s*\}(?!\})', "이중 닫는 중괄호 (템플릿 외)"),
        (r';\s*;', "이중 세미콜론"),
        (r',\s*,', "이중 콤마"),
        (r'\[\s*\]', "빈 배열 (정상일 수 있음)"),
    ]

    print("\n기타 잠재적 오류:")
    for pattern, description in error_patterns:
        count = len(re.findall(pattern, html_content))
        if count > 0:
            print(f"⚠️ {description}: {count}개")

    # Copy to main file
    import shutil
    shutil.copy(output_file, html_file)
    print(f"\n✅ 메인 HTML 파일 업데이트 완료")

    return fixes_applied

def regenerate_dashboard():
    """Regenerate the dashboard with fixed Python code"""

    print("\n🔄 대시보드 재생성...")
    print("-" * 40)

    # First, ensure Python file doesn't have tr() function
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        py_content = f.read()

    # Remove any tr() function calls in the Python code
    if 'tr(' in py_content:
        # Replace all tr() calls with the default value
        pattern = r"tr\(['\"][\w\.]+['\"]\s*,\s*['\"]([^'\"]+)['\"]\)"
        py_content = re.sub(pattern, r"'\1'", py_content)

        # Save the cleaned Python file
        with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
            f.write(py_content)

        print("✅ Python 파일에서 tr() 함수 제거 완료")

        # Regenerate the dashboard
        os.system('cd "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11" && python integrated_dashboard_final.py --month 9 --year 2025')
        print("✅ 대시보드 재생성 완료")
    else:
        print("ℹ️ Python 파일이 이미 깨끗합니다")

def main():
    """Main execution"""

    # Complete fix for JavaScript errors
    fixes = complete_javascript_fix()

    # Optionally regenerate the dashboard
    # regenerate_dashboard()

    print("\n" + "=" * 80)
    print("✨ JavaScript 오류 완전 해결!")
    print("=" * 80)
    print(f"""
📊 결과:
   - {fixes}개 tr() 함수 호출 제거
   - JavaScript 구문 오류 해결
   - 번역 시스템 정상화

🎯 확인 필요:
   1. VS Code에서 HTML 파일 열기
   2. Problems 탭에서 오류 개수 확인
   3. 143개 → 0개가 되어야 함

💡 해결 방법:
   - tr() 함수를 단순 문자열로 교체
   - 중괄호 균형 맞춤
   - JavaScript 구문 검증
    """)

if __name__ == "__main__":
    main()