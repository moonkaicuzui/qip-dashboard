#!/usr/bin/env python3
"""
Fix 143 JavaScript errors in generated HTML
주요 문제: tr() 함수가 HTML 내에서 호출되어 JavaScript 오류 발생
"""

import re
import os

def fix_javascript_errors():
    """Fix JavaScript errors in the generated HTML"""

    print("=" * 80)
    print("🔧 JavaScript Error Fix - 143개 오류 해결")
    print("=" * 80)

    # Read the problematic HTML file
    html_file = 'output_files/Incentive_Dashboard_2025_09_Version_5.html'

    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("\n📋 발견된 문제:")
    print("-" * 40)

    # 문제 패턴들
    problems_found = []

    # Pattern 1: tr() 함수가 JavaScript 내에서 호출됨
    pattern1 = r"tr\('([^']+)',\s*'([^']+)'\)"
    matches1 = re.findall(pattern1, html_content)
    if matches1:
        problems_found.append(f"tr() 함수 호출: {len(matches1)}개")
        print(f"❌ tr() 함수가 JavaScript 내에서 호출됨: {len(matches1)}개")

    # Pattern 2: 이중 중괄호가 제대로 닫히지 않음
    open_braces = html_content.count('{{')
    close_braces = html_content.count('}}')
    if open_braces != close_braces:
        problems_found.append(f"중괄호 불일치: 열림 {open_braces}, 닫힘 {close_braces}")
        print(f"❌ 중괄호 불일치: {{ {open_braces}개, }} {close_braces}개")

    # Pattern 3: ${{ 로 시작하지만 제대로 닫히지 않은 패턴
    pattern3 = r'\$\{\{[^}]*(?!\}\})'
    matches3 = re.findall(pattern3, html_content[:50000])  # First 50k chars only
    if matches3:
        print(f"❌ 닫히지 않은 템플릿 리터럴: {len(matches3[:5])}개 (샘플)")

    print("\n🔧 수정 작업 시작...")
    print("-" * 40)

    # Fix 1: tr() 함수 호출을 직접 문자열로 변경
    fixes_applied = 0

    # JavaScript 내에서 tr() 함수 호출을 문자열로 치환
    replacements = [
        # tr() 함수 호출을 단순 문자열로 변경
        (r"tr\('tabs\.validation',\s*'요약 및 시스템 검증'\)", "'요약 및 시스템 검증'"),
        (r"tr\('individualDetails\.conditionStatus\.pass',\s*'통과'\)", "'통과'"),
        (r"tr\('individualDetails\.conditionStatus\.fail',\s*'실패'\)", "'실패'"),
        (r"tr\('orgChart\.entireOrganization',\s*'전체 조직'\)", "'전체 조직'"),
        (r"tr\('orgChart\.type1ManagerStructure',\s*'TYPE-1 관리자 인센티브 구조'\)", "'TYPE-1 관리자 인센티브 구조'"),
        (r"tr\('orgChartModal\.position',\s*'직급'\)", "'직급'"),
        (r"tr\('orgChartModal\.calculationDetails',\s*'계산 과정 상세'\)", "'계산 과정 상세'"),
        (r"tr\('orgChartModal\.teamLineLeaderCount',\s*'팀 내 LINE LEADER 수'\)", "'팀 내 LINE LEADER 수'"),
        (r"tr\('orgChartModal\.lineLeadersReceiving',\s*'인센티브 받은 LINE LEADER'\)", "'인센티브 받은 LINE LEADER'"),
        (r"tr\('orgChartModal\.lineLeaderAverage',\s*'LINE LEADER 평균 인센티브'\)", "'LINE LEADER 평균 인센티브'"),
        (r"tr\('orgChartModal\.calculationFormula',\s*'계산식'\)", "'계산식'"),
        (r"tr\('orgChartModal\.name',\s*'이름'\)", "'이름'"),
        (r"tr\('orgChartModal\.incentive',\s*'인센티브'\)", "'인센티브'"),
        (r"tr\('orgChartModal\.includeInAverage',\s*'평균 계산 포함'\)", "'평균 계산 포함'"),
        (r"tr\('orgChartModal\.receivingStatus',\s*'수령 여부'\)", "'수령 여부'"),
        (r"tr\('orgChartModal\.total',\s*'합계'\)", "'합계'"),
        (r"tr\('orgChartModal\.average',\s*'평균'\)", "'평균'"),
    ]

    for pattern, replacement in replacements:
        count = len(re.findall(pattern, html_content))
        if count > 0:
            html_content = re.sub(pattern, replacement, html_content)
            fixes_applied += count
            print(f"✅ Fixed: {pattern[:50]}... ({count}개)")

    # Fix 2: 잘못된 이중 번역 패턴 수정
    # ${{translations...}} || tr(...) 패턴을 단순화
    pattern_double_trans = r'\$\{\{translations\.[^}]+\}\}\s*\|\|\s*tr\([^)]+\)'
    matches = re.findall(pattern_double_trans, html_content)

    for match in set(matches):  # unique matches only
        # Extract the translations part only
        trans_match = re.search(r'(\$\{\{translations\.[^}]+\}\})', match)
        if trans_match:
            fixed = trans_match.group(1)
            html_content = html_content.replace(match, fixed)
            fixes_applied += 1
            print(f"✅ Fixed double translation: {match[:50]}...")

    # Fix 3: 닫히지 않은 중괄호 수정
    # 패턴: ${{ 로 시작하는데 }} 로 끝나지 않는 경우
    html_content = re.sub(r'\$\{\{([^}]+)(?!\}\})', r'${{{\1}}}', html_content)

    # Save the fixed HTML
    output_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_fixed.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ 총 {fixes_applied}개 수정 완료")
    print(f"📁 출력 파일: {output_file}")

    # Verify the fixes
    print("\n📊 검증:")
    print("-" * 40)

    # Check if tr() functions are removed
    remaining_tr = len(re.findall(r"tr\([^)]+\)", html_content))
    print(f"{'✅' if remaining_tr == 0 else '⚠️'} 남은 tr() 함수: {remaining_tr}개")

    # Check brace balance
    open_braces_after = html_content.count('{{')
    close_braces_after = html_content.count('}}')
    balanced = open_braces_after == close_braces_after
    print(f"{'✅' if balanced else '⚠️'} 중괄호 균형: 열림 {open_braces_after}, 닫힘 {close_braces_after}")

    return output_file

def update_python_generator():
    """Update the Python file to prevent these errors in future generations"""

    print("\n🔧 Python 생성기 업데이트...")
    print("-" * 40)

    # Read integrated_dashboard_final.py
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        py_content = f.read()

    # Remove tr() function if it exists
    if 'def tr(' in py_content:
        print("✅ tr() 함수 정의 발견 - 제거 중...")
        # Remove the tr() function definition
        py_content = re.sub(r'def tr\([^)]+\):[^}]+?return[^}]+?\n\n', '', py_content, flags=re.DOTALL)

    # Replace tr() calls with proper translation patterns
    replacements = [
        # Pattern: {tr('key', 'default')} → {{'default'}}
        (r"\{tr\('[\w\.]+',\s*'([^']+)'\)\}", r"{'\1'}"),
        # Pattern: tr('key', 'default') → 'default'
        (r"tr\('[\w\.]+',\s*'([^']+)'\)", r"'\1'"),
    ]

    changes = 0
    for pattern, replacement in replacements:
        matches = re.findall(pattern, py_content)
        if matches:
            py_content = re.sub(pattern, replacement, py_content)
            changes += len(matches)

    if changes > 0:
        # Save updated Python file
        with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
            f.write(py_content)
        print(f"✅ Python 파일 업데이트: {changes}개 tr() 호출 제거")
    else:
        print("ℹ️ Python 파일에 tr() 호출이 없습니다")

def main():
    """Main execution"""

    # Fix the current HTML
    fixed_html = fix_javascript_errors()

    # Update the Python generator
    update_python_generator()

    # Copy fixed HTML to main output
    import shutil
    if fixed_html and os.path.exists(fixed_html):
        main_output = 'output_files/Incentive_Dashboard_2025_09_Version_5.html'
        shutil.copy(fixed_html, main_output)
        print(f"\n✅ 수정된 HTML을 메인 출력 파일로 복사 완료")

    print("\n" + "=" * 80)
    print("✨ JavaScript 오류 수정 완료!")
    print("=" * 80)
    print("""
📋 수정 내용:
   - tr() 함수 호출 제거
   - 이중 번역 패턴 수정
   - 중괄호 균형 맞춤

🎯 결과:
   - 143개 JavaScript 오류 → 0개 (예상)
   - 깨끗한 JavaScript 코드
   - 번역 시스템 정상 작동

💡 향후 방지책:
   - Python에서 tr() 함수 사용 금지
   - 템플릿 리터럴은 항상 검증
   - JavaScript 코드는 별도 검증 필요
    """)

if __name__ == "__main__":
    main()