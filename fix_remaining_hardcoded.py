#!/usr/bin/env python3
"""
Fix remaining hardcoded Korean text in integrated_dashboard_final.py
Replace with translation system calls
"""

import re

def fix_remaining_hardcoded():
    """Fix all remaining hardcoded Korean text"""

    # Read the current file
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    changes_made = 0

    for i, line in enumerate(lines):
        original_line = line

        # 1. Fix validation tab name
        if "'요약 및 시스템 검증'" in line and 'validationTab' in lines[max(0, i-5):i+5]:
            line = line.replace("'요약 및 시스템 검증'",
                              "${{translations.tabs?.validation?.[lang] || '요약 및 시스템 검증'}}")
            if line != original_line:
                changes_made += 1

        # 2. Fix pass/fail status in individual details
        if "'통과'" in line:
            # Check context - if it's in condition evaluation
            if 'cond_' in line or 'condition' in line.lower():
                line = re.sub(r"'통과'",
                            "${{translations.individualDetails?.conditionStatus?.pass?.[lang] || '통과'}}", line)
                if line != original_line:
                    changes_made += 1

        if "'실패'" in line:
            if 'cond_' in line or 'condition' in line.lower():
                line = re.sub(r"'실패'",
                            "${{translations.individualDetails?.conditionStatus?.fail?.[lang] || '실패'}}", line)
                if line != original_line:
                    changes_made += 1

        # 3. Fix org chart texts
        if '참고: AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다.' in line:
            line = line.replace('참고: AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다.',
                              "${{translations.orgChart?.excludedPositionsNote?.[lang] || '참고: AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다.'}}")
            if line != original_line:
                changes_made += 1

        if "'전체 조직'" in line:
            line = line.replace("'전체 조직'",
                              "${{translations.orgChart?.entireOrganization?.[lang] || '전체 조직'}}")
            if line != original_line:
                changes_made += 1

        if 'TYPE-1 관리자 인센티브 구조' in line:
            line = line.replace('TYPE-1 관리자 인센티브 구조',
                              "${{translations.orgChart?.type1ManagerStructure?.[lang] || 'TYPE-1 관리자 인센티브 구조'}}")
            if line != original_line:
                changes_made += 1

        # 4. Fix org chart modal labels
        if '>직급:' in line or '"직급"' in line:
            line = re.sub(r'>직급:',
                         ">${{translations.orgChartModal?.position?.[lang] || '직급'}}:", line)
            line = re.sub(r'"직급"',
                         "${{translations.orgChartModal?.position?.[lang] || '직급'}}", line)
            if line != original_line:
                changes_made += 1

        if '계산 과정 상세' in line:
            line = line.replace('계산 과정 상세',
                              "${{translations.orgChartModal?.calculationDetails?.[lang] || '계산 과정 상세'}}")
            if line != original_line:
                changes_made += 1

        if '팀 내 LINE LEADER 수' in line:
            line = line.replace('팀 내 LINE LEADER 수',
                              "${{translations.orgChartModal?.teamLineLeaderCount?.[lang] || '팀 내 LINE LEADER 수'}}")
            if line != original_line:
                changes_made += 1

        if '인센티브 받은 LINE LEADER' in line:
            line = line.replace('인센티브 받은 LINE LEADER',
                              "${{translations.orgChartModal?.lineLeadersReceiving?.[lang] || '인센티브 받은 LINE LEADER'}}")
            if line != original_line:
                changes_made += 1

        if 'LINE LEADER 평균 인센티브' in line:
            line = line.replace('LINE LEADER 평균 인센티브',
                              "${{translations.orgChartModal?.lineLeaderAverage?.[lang] || 'LINE LEADER 평균 인센티브'}}")
            if line != original_line:
                changes_made += 1

        if '>계산식' in line or '"계산식"' in line:
            line = re.sub(r'>계산식',
                         ">${{translations.orgChartModal?.calculationFormula?.[lang] || '계산식'}}", line)
            line = re.sub(r'"계산식"',
                         "${{translations.orgChartModal?.calculationFormula?.[lang] || '계산식'}}", line)
            if line != original_line:
                changes_made += 1

        # 5. Fix table headers in org chart modal
        if '팀 내 LINE LEADER 인센티브 내역' in line:
            line = line.replace('팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)',
                              "${{translations.orgChartModal?.teamLineLeaderDetails?.[lang] || '팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)'}}")
            if line != original_line:
                changes_made += 1

        if 'ASSEMBLY INSPECTOR 인센티브 내역' in line:
            line = line.replace('ASSEMBLY INSPECTOR 인센티브 내역 (합계 계산 대상)',
                              "${{translations.orgChartModal?.assemblyInspectorDetails?.[lang] || 'ASSEMBLY INSPECTOR 인센티브 내역 (합계 계산 대상)'}}")
            if line != original_line:
                changes_made += 1

        # Table headers: 이름, 인센티브, 평균 계산 포함, 수령 여부
        if '>이름<' in line and 'th>' in line:
            line = re.sub(r'>이름<',
                         ">${{translations.orgChartModal?.name?.[lang] || '이름'}}<", line)
            if line != original_line:
                changes_made += 1

        if '>인센티브<' in line and 'th>' in line:
            line = re.sub(r'>인센티브<',
                         ">${{translations.orgChartModal?.incentive?.[lang] || '인센티브'}}<", line)
            if line != original_line:
                changes_made += 1

        if '평균 계산 포함' in line:
            line = line.replace('평균 계산 포함',
                              "${{translations.orgChartModal?.includeInAverage?.[lang] || '평균 계산 포함'}}")
            if line != original_line:
                changes_made += 1

        if '수령 여부' in line:
            line = line.replace('수령 여부',
                              "${{translations.orgChartModal?.receivingStatus?.[lang] || '수령 여부'}}")
            if line != original_line:
                changes_made += 1

        # Total and average
        if '>합계<' in line:
            line = re.sub(r'>합계<',
                         ">${{translations.orgChartModal?.total?.[lang] || '합계'}}<", line)
            if line != original_line:
                changes_made += 1

        if '>평균' in line and ('수령자' in line or 'recipients' in line):
            # Handle average with recipients format
            pattern = r'평균 \(수령자 (\d+)명 / 전체 (\d+)명\)'
            if re.search(pattern, line):
                line = re.sub(pattern,
                            "${{translations.orgChartModal?.average?.[lang] || '평균'}} ${{translations.orgChartModal?.averageRecipients?.[lang]?.replace('{recipients}', '\\1').replace('{total}', '\\2') || '(수령자 \\1명 / 전체 \\2명)'}}", line)
                if line != original_line:
                    changes_made += 1

        # 6. Fix non-payment reasons
        if '실제 근무일 0일 (출근 조건 1번 미충족)' in line:
            line = line.replace('실제 근무일 0일 (출근 조건 1번 미충족)',
                              "${{translations.orgChartModal?.nonPaymentReasons?.actualWorkingDays0?.[lang] || '실제 근무일 0일 (출근 조건 1번 미충족)'}}")
            if line != original_line:
                changes_made += 1

        if '무단결근 2일 초과 (출근 조건 2번 미충족)' in line:
            line = line.replace('무단결근 2일 초과 (출근 조건 2번 미충족)',
                              "${{translations.orgChartModal?.nonPaymentReasons?.unauthorizedAbsence?.[lang] || '무단결근 2일 초과 (출근 조건 2번 미충족)'}}")
            if line != original_line:
                changes_made += 1

        if '결근율 12% 초과 (출근 조건 3번 미충족)' in line:
            line = line.replace('결근율 12% 초과 (출근 조건 3번 미충족)',
                              "${{translations.orgChartModal?.nonPaymentReasons?.absenceRate12?.[lang] || '결근율 12% 초과 (출근 조건 3번 미충족)'}}")
            if line != original_line:
                changes_made += 1

        if '최소 근무일 미달 (출근 조건 4번 미충족)' in line:
            line = line.replace('최소 근무일 미달 (출근 조건 4번 미충족)',
                              "${{translations.orgChartModal?.nonPaymentReasons?.minWorkingDays?.[lang] || '최소 근무일 미달 (출근 조건 4번 미충족)'}}")
            if line != original_line:
                changes_made += 1

        if '팀/구역 AQL 실패 (AQL 조건 7번 미충족)' in line:
            line = line.replace('팀/구역 AQL 실패 (AQL 조건 7번 미충족)',
                              "${{translations.orgChartModal?.nonPaymentReasons?.teamAreaAQL?.[lang] || '팀/구역 AQL 실패 (AQL 조건 7번 미충족)'}}")
            if line != original_line:
                changes_made += 1

        if '5PRS 검증 부족 또는 합격률 95% 미달 (5PRS 조건 1번 미충족)' in line:
            line = line.replace('5PRS 검증 부족 또는 합격률 95% 미달 (5PRS 조건 1번 미충족)',
                              "${{translations.orgChartModal?.nonPaymentReasons?.fprsPassRate?.[lang] || '5PRS 검증 부족 또는 합격률 95% 미달 (5PRS 조건 1번 미충족)'}}")
            if line != original_line:
                changes_made += 1

        if '5PRS 총 검증 수량 0 (5PRS 조건 2번 미충족)' in line:
            line = line.replace('5PRS 총 검증 수량 0 (5PRS 조건 2번 미충족)',
                              "${{translations.orgChartModal?.nonPaymentReasons?.fprsZeroQty?.[lang] || '5PRS 총 검증 수량 0 (5PRS 조건 2번 미충족)'}}")
            if line != original_line:
                changes_made += 1

        # People count (명)
        if re.search(r'(\d+)명', line) and ('LINE LEADER' in line or 'recipients' in line):
            # Replace number + 명 pattern
            line = re.sub(r'(\d+)명',
                         "\\1${{translations.orgChartModal?.people?.[lang] || '명'}}", line)
            if line != original_line:
                changes_made += 1

        lines[i] = line

    # Write the updated file
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"✅ Fixed {changes_made} hardcoded text instances")
    print("\n📋 Fixed categories:")
    print("  - Validation tab name")
    print("  - Pass/Fail status in conditions")
    print("  - Org chart main texts")
    print("  - Org chart modal labels")
    print("  - Table headers")
    print("  - Non-payment reasons")
    print("  - People count units")

if __name__ == "__main__":
    fix_remaining_hardcoded()