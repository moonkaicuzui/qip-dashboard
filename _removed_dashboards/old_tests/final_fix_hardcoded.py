#!/usr/bin/env python3
"""
Final fix for remaining hardcoded text
Ensures all text uses translation system
"""

import re

def final_fix_hardcoded():
    """Apply final fixes for hardcoded text"""

    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Track changes
    changes = []

    # 1. Fix validation tab name in tab bar
    pattern = r'<div class="tab" data-tab="validation"[^>]*>요약 및 시스템 검증</div>'
    replacement = '<div class="tab" data-tab="validation" onclick="showTab(\'validation\')" id="tabValidation">${{translations.tabs?.validation?.[lang] || \'요약 및 시스템 검증\'}}</div>'
    content, count = re.subn(pattern, replacement, content)
    if count > 0:
        changes.append(f"Fixed validation tab name in tab bar: {count} occurrences")

    # 2. Fix validation tab title
    pattern = r'<h3 id="validationTabTitle">요약 및 시스템 검증</h3>'
    replacement = '<h3 id="validationTabTitle">${{translations.tabs?.validation?.[lang] || \'요약 및 시스템 검증\'}}</h3>'
    content, count = re.subn(pattern, replacement, content)
    if count > 0:
        changes.append(f"Fixed validation tab title: {count} occurrences")

    # 3. Fix pass/fail status - need to update the Python logic
    # Find the condition evaluation section
    pattern = r"'통과' if ([^']+) else '실패'"
    replacement = r"${{translations.individualDetails?.conditionStatus?.pass?.[lang] || '통과'}} if \1 else ${{translations.individualDetails?.conditionStatus?.fail?.[lang] || '실패'}}"
    content, count = re.subn(pattern, replacement, content)
    if count > 0:
        changes.append(f"Fixed pass/fail status: {count} occurrences")

    # 4. Fix org chart texts in HTML generation
    # Fix excluded positions note
    pattern = r'참고: AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다\.'
    replacement = '${{translations.orgChart?.excludedPositionsNote?.[lang] || \'참고: AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다.\'}}'
    content = content.replace(pattern, replacement)

    # Fix "전체 조직"
    pattern = r"'전체 조직'"
    replacement = "${{translations.orgChart?.entireOrganization?.[lang] || '전체 조직'}}"
    content = re.sub(pattern, replacement, content)

    # Fix table headers in modals - need to ensure they're in the right context
    # Find table header sections and replace
    modal_headers = {
        '>이름</th>': '>${{translations.orgChartModal?.name?.[lang] || \'이름\'}}</th>',
        '>인센티브</th>': '>${{translations.orgChartModal?.incentive?.[lang] || \'인센티브\'}}</th>',
        '>평균 계산 포함</th>': '>${{translations.orgChartModal?.includeInAverage?.[lang] || \'평균 계산 포함\'}}</th>',
        '>수령 여부</th>': '>${{translations.orgChartModal?.receivingStatus?.[lang] || \'수령 여부\'}}</th>',
    }

    for old, new in modal_headers.items():
        if old in content:
            content = content.replace(old, new)
            changes.append(f"Fixed table header: {old}")

    # Fix average with recipients pattern
    pattern = r'평균 \(수령자 (\d+)명 / 전체 (\d+)명\)'
    def replace_average(match):
        return f"${{{{translations.orgChartModal?.average?.[lang] || '평균'}}}} ${{{{translations.orgChartModal?.averageRecipients?.[lang]?.replace('{{recipients}}', '{match.group(1)}').replace('{{total}}', '{match.group(2)}') || '(수령자 {match.group(1)}명 / 전체 {match.group(2)}명)'}}}}"

    content = re.sub(pattern, replace_average, content)

    # Fix people count - more specific pattern
    pattern = r'(\d+)명'
    def replace_people(match):
        # Only replace if in specific contexts
        context = content[max(0, match.start()-50):match.end()+50]
        if 'LINE LEADER' in context or '수령자' in context or '전체' in context:
            return f"{match.group(1)}${{{{translations.orgChartModal?.people?.[lang] || '명'}}}}"
        return match.group(0)

    # Apply people replacement carefully
    # content = re.sub(pattern, replace_people, content)

    # Write the updated file
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Applied final fixes for hardcoded text")
    print("\n📋 Changes made:")
    for change in changes:
        print(f"  - {change}")

    return len(changes)

if __name__ == "__main__":
    changes = final_fix_hardcoded()
    print(f"\n📊 Total: {changes} fixes applied")