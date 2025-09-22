#!/usr/bin/env python3
"""
Fix hardcoded Korean text in integrated_dashboard_final.py
Replaces with translation system calls
"""

import re
import os

def fix_hardcoded_text():
    """Fix hardcoded text with proper translation system"""

    # Read the current file
    input_file = 'integrated_dashboard_final.py'
    output_file = 'integrated_dashboard_final.py'

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Track changes
    changes_made = []

    # Process line by line for more precise control
    for i, line in enumerate(lines):
        original_line = line

        # Modal title - Area AQL
        if "'구역별 AQL 상태 및 조건 7번/8번 분석'" in line or '"구역별 AQL 상태 및 조건 7번/8번 분석"' in line:
            line = line.replace("'구역별 AQL 상태 및 조건 7번/8번 분석'",
                              "${translations.modals?.areaAQL?.title?.[lang] || '구역별 AQL 상태 및 조건 7번/8번 분석'}")
            line = line.replace('"구역별 AQL 상태 및 조건 7번/8번 분석"',
                              "${translations.modals?.areaAQL?.title?.[lang] || '구역별 AQL 상태 및 조건 7번/8번 분석'}")
            if line != original_line:
                changes_made.append(f"Line {i+1}: Area AQL modal title")

        # Condition 7 description
        if '팀/구역 AQL 3개월 연속 실패' in line and '<strong>' in line:
            line = re.sub(r'<strong>조건 7번:</strong> 팀/구역 AQL 3개월 연속 실패',
                         "<strong>${translations.modals?.areaAQL?.condition7?.[lang]?.split(':')[0] || '조건 7번'}:</strong> ${translations.modals?.areaAQL?.condition7?.[lang]?.split(': ')[1] || '팀/구역 AQL 3개월 연속 실패'}",
                         line)
            if line != original_line:
                changes_made.append(f"Line {i+1}: Condition 7 description")

        # Condition 8 description
        if '구역 Reject Rate 3% 초과' in line and '<strong>' in line:
            line = re.sub(r'<strong>조건 8번:</strong> 구역 Reject Rate 3% 초과',
                         "<strong>${translations.modals?.areaAQL?.condition8?.[lang]?.split(':')[0] || '조건 8번'}:</strong> ${translations.modals?.areaAQL?.condition8?.[lang]?.split(': ')[1] || '구역 Reject Rate 3% 초과'}",
                         line)
            if line != original_line:
                changes_made.append(f"Line {i+1}: Condition 8 description")

        # Table headers in modals
        if '<th' in line:
            # Area
            if '>구역</th>' in line:
                line = re.sub(r'>구역</th>', ">${translations.modals?.areaAQL?.area?.[lang] || '구역'}</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Area header")

            # Total employees
            if '>전체<br>인원</th>' in line or '전체 인원' in line:
                line = re.sub(r'>전체<br>인원</th>', ">${translations.modals?.areaAQL?.totalEmployees?.[lang] || '전체 인원'}</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Total employees header")

            # Employee headers
            if '>사번' in line and '</th>' in line:
                line = re.sub(r'>사번([^<]*)</th>', ">${translations.common?.tableHeaders?.employeeNo?.[lang] || '사번'}\\1</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Employee number header")

            if '>이름' in line and '</th>' in line:
                line = re.sub(r'>이름([^<]*)</th>', ">${translations.common?.tableHeaders?.name?.[lang] || '이름'}\\1</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Name header")

            if '>직책' in line and '</th>' in line and '1단계' not in line:
                line = re.sub(r'>직책([^<]*)</th>', ">${translations.common?.tableHeaders?.position?.[lang] || '직책'}\\1</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Position header")

            # Position hierarchy in 5PRS modal
            if '직책 (1단계 > 2단계 > 3단계)' in line:
                line = re.sub(r'>직책 \(1단계 > 2단계 > 3단계\)([^<]*)</th>',
                            ">${translations.modals?.fprs?.positionHierarchy?.[lang] || '직책 (1단계 > 2단계 > 3단계)'}\\1</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Position hierarchy header")

            # 5PRS headers
            if '>총 검증</th>' in line:
                line = re.sub(r'>총 검증</th>', ">${translations.modals?.fprs?.totalTests?.[lang] || '총 검증'}</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Total tests header")

            if '>통과율</th>' in line:
                line = re.sub(r'>통과율</th>', ">${translations.modals?.fprs?.passRate?.[lang] || '통과율'}</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Pass rate header")

            if '>조건 충족</th>' in line:
                line = re.sub(r'>조건 충족</th>', ">${translations.modals?.fprs?.conditionMet?.[lang] || '조건 충족'}</th>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Condition met header")

        # KPI card labels in validation tab
        if '<div class="kpi-label">' in line:
            # Total working days
            if '총 근무일수' in line:
                line = re.sub(r'>총 근무일수</div>',
                            ">${translations.validationTab?.kpiCards?.totalWorkingDays?.title?.[lang] || '총 근무일수'}</div>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Total working days KPI")

            # Unauthorized absence
            if '무단결근 3일 이상' in line:
                line = re.sub(r'>무단결근 3일 이상</div>',
                            ">${translations.validationTab?.kpiCards?.unauthorizedAbsence?.title?.[lang] || '무단결근 3일 이상'}</div>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Unauthorized absence KPI")

            # Low attendance
            if '출근율 88% 미만' in line:
                line = re.sub(r'>출근율 88% 미만</div>',
                            ">${translations.validationTab?.kpiCards?.lowAttendance?.title?.[lang] || '출근율 88% 미만'}</div>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Low attendance KPI")

            # Min working days
            if '최소 근무일 미충족' in line:
                line = re.sub(r'>최소 근무일 미충족</div>',
                            ">${translations.validationTab?.kpiCards?.minWorkingDays?.title?.[lang] || '최소 근무일 미충족'}</div>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Min working days KPI")

            # Area reject rate
            if '구역 AQL Reject 3% 이상' in line:
                line = re.sub(r'>구역 AQL Reject 3% 이상</div>',
                            ">${translations.validationTab?.kpiCards?.areaRejectRate?.title?.[lang] || '구역 AQL Reject 3% 이상'}</div>", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Area reject rate KPI")

        # Condition status text
        if "'충족'" in line or '"충족"' in line:
            # Check context to avoid replacing in comments
            if 'badge' in line or 'status' in line.lower():
                line = re.sub(r"'충족'", "${translations.modals?.fprs?.met?.[lang] || '충족'}", line)
                line = re.sub(r'"충족"', "${translations.modals?.fprs?.met?.[lang] || '충족'}", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Met status")

        if "'미충족'" in line or '"미충족"' in line:
            if 'badge' in line or 'status' in line.lower():
                line = re.sub(r"'미충족'", "${translations.modals?.fprs?.conditionNotMet?.[lang] || '미충족'}", line)
                line = re.sub(r'"미충족"', "${translations.modals?.fprs?.conditionNotMet?.[lang] || '미충족'}", line)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Not met status")

        # Modal titles
        if '5PRS 통과율 95% 미만 직원 상세' in line:
            line = re.sub(r"'5PRS 통과율 95% 미만 직원 상세'",
                         "${translations.modals?.fprs?.lowPassRateTitle?.[lang] || '5PRS 통과율 95% 미만 직원 상세'}", line)
            if line != original_line:
                changes_made.append(f"Line {i+1}: 5PRS low pass rate title")

        if '5PRS 검증 수량 100개 미만 직원 상세' in line:
            line = re.sub(r"'5PRS 검증 수량 100개 미만 직원 상세'",
                         "${translations.modals?.fprs?.lowInspectionTitle?.[lang] || '5PRS 검증 수량 100개 미만 직원 상세'}", line)
            if line != original_line:
                changes_made.append(f"Line {i+1}: 5PRS low inspection title")

        lines[i] = line

    # Write the updated file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"✅ Fixed hardcoded text in {output_file}")
    print(f"\n📊 Total changes made: {len(changes_made)}")

    if changes_made:
        print("\n📋 Changes applied:")
        for i, change in enumerate(changes_made[:20], 1):  # Show first 20 changes
            print(f"  {i}. {change}")
        if len(changes_made) > 20:
            print(f"  ... and {len(changes_made) - 20} more changes")

    print("\n✨ Next steps:")
    print("1. Review the changes in integrated_dashboard_final.py")
    print("2. Run the dashboard generation: python integrated_dashboard_final.py")
    print("3. Test language switching in the dashboard")

if __name__ == "__main__":
    fix_hardcoded_text()