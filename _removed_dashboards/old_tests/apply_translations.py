#!/usr/bin/env python3
"""
Apply translations to integrated_dashboard_final.py
Replaces hardcoded Korean text with translation system calls
"""

import re

def apply_translations():
    """Replace hardcoded text with translation system"""

    # Read the current integrated_dashboard_final.py
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Create replacements dictionary
    replacements = {
        # Modal headers and content
        '구역별 AQL 상태 및 조건 7번/8번 분석': "${translations.modals?.areaAQL?.title?.[lang] || '구역별 AQL 상태 및 조건 7번/8번 분석'}",
        '<strong>조건 7번:</strong> 팀/구역 AQL 3개월 연속 실패': "<strong>${translations.modals?.areaAQL?.condition7?.[lang]?.split(':')[0] || '조건 7번'}:</strong> ${translations.modals?.areaAQL?.condition7?.[lang]?.split(':')[1] || '팀/구역 AQL 3개월 연속 실패'}",
        '<strong>조건 8번:</strong> 구역 Reject Rate 3% 초과': "<strong>${translations.modals?.areaAQL?.condition8?.[lang]?.split(':')[0] || '조건 8번'}:</strong> ${translations.modals?.areaAQL?.condition8?.[lang]?.split(':')[1] || '구역 Reject Rate 3% 초과'}",
        '<i class="fas fa-chart-bar me-2"></i>구역별 Reject Rate 통계': "<i class='fas fa-chart-bar me-2'></i>${translations.modals?.areaAQL?.areaStatistics?.[lang] || '구역별 Reject Rate 통계'}",
        '<i class="fas fa-users me-2"></i>조건 미충족 직원 상세': "<i class='fas fa-users me-2'></i>${translations.modals?.areaAQL?.employeeDetails?.[lang] || '조건 미충족 직원 상세'}",

        # Table headers in area AQL modal
        '<th style="padding: 10px;">구역</th>': "<th style='padding: 10px;'>${translations.modals?.areaAQL?.area?.[lang] || '구역'}</th>",
        '<th style="padding: 10px; text-align: center;">전체<br>인원</th>': "<th style='padding: 10px; text-align: center;'>${translations.modals?.areaAQL?.totalEmployees?.[lang] || '전체 인원'}</th>",
        '<th style="padding: 10px; text-align: center;">조건7<br>미충족</th>': "<th style='padding: 10px; text-align: center;'>${translations.modals?.areaAQL?.cond7Fail?.[lang] || '조건7 미충족'}</th>",
        '<th style="padding: 10px; text-align: center;">조건8<br>미충족</th>': "<th style='padding: 10px; text-align: center;'>${translations.modals?.areaAQL?.cond8Fail?.[lang] || '조건8 미충족'}</th>",
        '<th style="padding: 10px; text-align: center;">총 AQL<br>건수</th>': "<th style='padding: 10px; text-align: center;'>${translations.modals?.areaAQL?.totalAQL?.[lang] || '총 AQL 건수'}</th>",

        # 5PRS modal headers
        '5PRS 통과율 95% 미만 직원 상세': "${translations.modals?.fprs?.lowPassRateTitle?.[lang] || '5PRS 통과율 95% 미만 직원 상세'}",
        '5PRS 검증 수량 100개 미만 직원 상세': "${translations.modals?.fprs?.lowInspectionTitle?.[lang] || '5PRS 검증 수량 100개 미만 직원 상세'}",
        '<th class="sortable-header" data-sort="position">직책 (1단계 > 2단계 > 3단계) ${getSortIcon(\'position\')}</th>': "<th class='sortable-header' data-sort='position'>${translations.modals?.fprs?.positionHierarchy?.[lang] || '직책 (1단계 > 2단계 > 3단계)'} ${getSortIcon('position')}</th>",

        # Common table headers
        '"사번"': "${translations.common?.tableHeaders?.employeeNo?.[lang] || '사번'}",
        '"이름"': "${translations.common?.tableHeaders?.name?.[lang] || '이름'}",
        '"직책"': "${translations.common?.tableHeaders?.position?.[lang] || '직책'}",

        # Validation tab KPI cards
        '<div class="kpi-label">총 근무일수</div>': "<div class='kpi-label'>${translations.validationTab?.kpiCards?.totalWorkingDays?.title?.[lang] || '총 근무일수'}</div>",
        '<div class="kpi-label">무단결근 3일 이상</div>': "<div class='kpi-label'>${translations.validationTab?.kpiCards?.unauthorizedAbsence?.title?.[lang] || '무단결근 3일 이상'}</div>",
        '<div class="kpi-label">출근율 88% 미만</div>': "<div class='kpi-label'>${translations.validationTab?.kpiCards?.lowAttendance?.title?.[lang] || '출근율 88% 미만'}</div>",
        '<div class="kpi-label">최소 근무일 미충족</div>': "<div class='kpi-label'>${translations.validationTab?.kpiCards?.minWorkingDays?.title?.[lang] || '최소 근무일 미충족'}</div>",
        '<div class="kpi-label">구역 AQL Reject 3% 이상</div>': "<div class='kpi-label'>${translations.validationTab?.kpiCards?.areaRejectRate?.title?.[lang] || '구역 AQL Reject 3% 이상'}</div>",

        # Condition status badges
        "'충족'": "${translations.modals?.fprs?.met?.[lang] || '충족'}",
        "'미충족'": "${translations.modals?.fprs?.conditionNotMet?.[lang] || '미충족'}",
        "'조건 충족'": "${translations.modals?.fprs?.conditionMet?.[lang] || '조건 충족'}",

        # Pass/Fail labels
        '<th>PASS</th>': "<th>${translations.modals?.areaAQL?.pass?.[lang] || 'PASS'}</th>",
        '<th>FAIL</th>': "<th>${translations.modals?.areaAQL?.fail?.[lang] || 'FAIL'}</th>",
        '<th>Reject Rate</th>': "<th>${translations.modals?.areaAQL?.rejectRate?.[lang] || 'Reject Rate'}</th>",

        # 5PRS specific headers
        '<th>총 검증</th>': "<th>${translations.modals?.fprs?.totalTests?.[lang] || '총 검증'}</th>",
        '<th>통과율</th>': "<th>${translations.modals?.fprs?.passRate?.[lang] || '통과율'}</th>",
        '<th>검증 수량</th>': "<th>${translations.modals?.fprs?.inspectionQty?.[lang] || '검증 수량'}</th>",
    }

    # Apply replacements in specific contexts to avoid breaking code
    for old_text, new_text in replacements.items():
        # Only replace in HTML template strings (within backticks or quotes)
        if old_text.startswith('<'):
            # HTML replacements - be careful with context
            content = content.replace(old_text, new_text)
        else:
            # Text replacements - use more careful patterns
            # Replace in template literals
            pattern = f'`([^`]*){re.escape(old_text)}([^`]*)`'
            replacement = f'`\\1{new_text}\\2`'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)

            # Replace in single quotes
            pattern = f"'({re.escape(old_text)})'"
            replacement = f'`{new_text}`'  # Convert to template literal
            content = re.sub(pattern, replacement, content)

    # Write the updated content
    with open('integrated_dashboard_final_updated.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Created updated file: integrated_dashboard_final_updated.py")
    print("\n📋 Applied translations for:")
    print("  - Modal headers and content")
    print("  - Table headers")
    print("  - KPI card labels")
    print("  - Condition status badges")
    print("  - Pass/Fail labels")

    print("\n⚠️  Note: Please review the updated file and test thoroughly")
    print("    Some complex replacements may need manual adjustment")

if __name__ == "__main__":
    apply_translations()