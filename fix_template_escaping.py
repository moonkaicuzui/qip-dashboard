#!/usr/bin/env python3
"""
Fix template literal escaping in integrated_dashboard_final.py
Properly escape JavaScript template literals within Python f-strings
"""

import re

def fix_template_escaping():
    """Fix JavaScript template literals within Python f-strings"""

    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and fix problematic template literals within f-strings
    # These need to have their braces doubled: ${...} becomes ${{...}}

    replacements = [
        # Fix the specific lines causing syntax errors
        (r"\$\{translations\.common\?\.tableHeaders\?\.employeeNo\?\.\[lang\] \|\| '사번'\}",
         "${{translations.common?.tableHeaders?.employeeNo?.[lang] || '사번'}}"),

        (r"\$\{translations\.common\?\.tableHeaders\?\.name\?\.\[lang\] \|\| '이름'\}",
         "${{translations.common?.tableHeaders?.name?.[lang] || '이름'}}"),

        (r"\$\{translations\.common\?\.tableHeaders\?\.position\?\.\[lang\] \|\| '직책'\}",
         "${{translations.common?.tableHeaders?.position?.[lang] || '직책'}}"),

        # Fix modal translations
        (r"\$\{translations\.modals\?\.areaAQL\?\.title\?\.\[lang\] \|\| '구역별 AQL 상태 및 조건 7번/8번 분석'\}",
         "${{translations.modals?.areaAQL?.title?.[lang] || '구역별 AQL 상태 및 조건 7번/8번 분석'}}"),

        (r"\$\{translations\.modals\?\.areaAQL\?\.area\?\.\[lang\] \|\| '구역'\}",
         "${{translations.modals?.areaAQL?.area?.[lang] || '구역'}}"),

        (r"\$\{translations\.modals\?\.areaAQL\?\.totalEmployees\?\.\[lang\] \|\| '전체 인원'\}",
         "${{translations.modals?.areaAQL?.totalEmployees?.[lang] || '전체 인원'}}"),

        # Fix 5PRS modal translations
        (r"\$\{translations\.modals\?\.fprs\?\.lowPassRateTitle\?\.\[lang\] \|\| '5PRS 통과율 95% 미만 직원 상세'\}",
         "${{translations.modals?.fprs?.lowPassRateTitle?.[lang] || '5PRS 통과율 95% 미만 직원 상세'}}"),

        (r"\$\{translations\.modals\?\.fprs\?\.lowInspectionTitle\?\.\[lang\] \|\| '5PRS 검증 수량 100개 미만 직원 상세'\}",
         "${{translations.modals?.fprs?.lowInspectionTitle?.[lang] || '5PRS 검증 수량 100개 미만 직원 상세'}}"),

        (r"\$\{translations\.modals\?\.fprs\?\.positionHierarchy\?\.\[lang\] \|\| '직책 \(1단계 > 2단계 > 3단계\)'\}",
         "${{translations.modals?.fprs?.positionHierarchy?.[lang] || '직책 (1단계 > 2단계 > 3단계)'}}"),

        (r"\$\{translations\.modals\?\.fprs\?\.totalTests\?\.\[lang\] \|\| '총 검증'\}",
         "${{translations.modals?.fprs?.totalTests?.[lang] || '총 검증'}}"),

        (r"\$\{translations\.modals\?\.fprs\?\.passRate\?\.\[lang\] \|\| '통과율'\}",
         "${{translations.modals?.fprs?.passRate?.[lang] || '통과율'}}"),

        (r"\$\{translations\.modals\?\.fprs\?\.conditionMet\?\.\[lang\] \|\| '조건 충족'\}",
         "${{translations.modals?.fprs?.conditionMet?.[lang] || '조건 충족'}}"),

        (r"\$\{translations\.modals\?\.fprs\?\.met\?\.\[lang\] \|\| '충족'\}",
         "${{translations.modals?.fprs?.met?.[lang] || '충족'}}"),

        (r"\$\{translations\.modals\?\.fprs\?\.conditionNotMet\?\.\[lang\] \|\| '미충족'\}",
         "${{translations.modals?.fprs?.conditionNotMet?.[lang] || '미충족'}}"),

        # Fix validation tab KPI translations
        (r"\$\{translations\.validationTab\?\.kpiCards\?\.totalWorkingDays\?\.title\?\.\[lang\] \|\| '총 근무일수'\}",
         "${{translations.validationTab?.kpiCards?.totalWorkingDays?.title?.[lang] || '총 근무일수'}}"),

        (r"\$\{translations\.validationTab\?\.kpiCards\?\.unauthorizedAbsence\?\.title\?\.\[lang\] \|\| '무단결근 3일 이상'\}",
         "${{translations.validationTab?.kpiCards?.unauthorizedAbsence?.title?.[lang] || '무단결근 3일 이상'}}"),

        (r"\$\{translations\.validationTab\?\.kpiCards\?\.lowAttendance\?\.title\?\.\[lang\] \|\| '출근율 88% 미만'\}",
         "${{translations.validationTab?.kpiCards?.lowAttendance?.title?.[lang] || '출근율 88% 미만'}}"),

        (r"\$\{translations\.validationTab\?\.kpiCards\?\.minWorkingDays\?\.title\?\.\[lang\] \|\| '최소 근무일 미충족'\}",
         "${{translations.validationTab?.kpiCards?.minWorkingDays?.title?.[lang] || '최소 근무일 미충족'}}"),

        (r"\$\{translations\.validationTab\?\.kpiCards\?\.areaRejectRate\?\.title\?\.\[lang\] \|\| '구역 AQL Reject 3% 이상'\}",
         "${{translations.validationTab?.kpiCards?.areaRejectRate?.title?.[lang] || '구역 AQL Reject 3% 이상'}}"),

        # Fix complex condition descriptions
        (r"\$\{translations\.modals\?\.areaAQL\?\.condition7\?\.\[lang\]\?\.split\(':'\)\[0\] \|\| '조건 7번'\}",
         "${{translations.modals?.areaAQL?.condition7?.[lang]?.split(':')[0] || '조건 7번'}}"),

        (r"\$\{translations\.modals\?\.areaAQL\?\.condition7\?\.\[lang\]\?\.split\(': '\)\[1\] \|\| '팀/구역 AQL 3개월 연속 실패'\}",
         "${{translations.modals?.areaAQL?.condition7?.[lang]?.split(': ')[1] || '팀/구역 AQL 3개월 연속 실패'}}"),

        (r"\$\{translations\.modals\?\.areaAQL\?\.condition8\?\.\[lang\]\?\.split\(':'\)\[0\] \|\| '조건 8번'\}",
         "${{translations.modals?.areaAQL?.condition8?.[lang]?.split(':')[0] || '조건 8번'}}"),

        (r"\$\{translations\.modals\?\.areaAQL\?\.condition8\?\.\[lang\]\?\.split\(': '\)\[1\] \|\| '구역 Reject Rate 3% 초과'\}",
         "${{translations.modals?.areaAQL?.condition8?.[lang]?.split(': ')[1] || '구역 Reject Rate 3% 초과'}}"),

        # Fix area statistics translation
        (r"\$\{translations\.modals\?\.areaAQL\?\.areaStatistics\?\.\[lang\] \|\| '구역별 Reject Rate 통계'\}",
         "${{translations.modals?.areaAQL?.areaStatistics?.[lang] || '구역별 Reject Rate 통계'}}"),

        (r"\$\{translations\.modals\?\.areaAQL\?\.employeeDetails\?\.\[lang\] \|\| '조건 미충족 직원 상세'\}",
         "${{translations.modals?.areaAQL?.employeeDetails?.[lang] || '조건 미충족 직원 상세'}}"),
    ]

    # Apply all replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Write back the fixed content
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Fixed template literal escaping")
    print(f"📊 Applied {len(replacements)} replacement patterns")
    print("\n✨ The file should now run without syntax errors")

if __name__ == "__main__":
    fix_template_escaping()