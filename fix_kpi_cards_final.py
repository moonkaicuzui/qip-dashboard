#!/usr/bin/env python3
"""
KPI 카드 명칭 및 로직 최종 수정
1. 실제 근무일 0일에서 퇴사자 제외
2. KPI 카드 명칭과 모달 매칭
3. 출근율 88% 미만 카드 올바른 위치에 추가
"""

import re
from pathlib import Path

def fix_kpi_cards():
    file_path = Path('integrated_dashboard_final.py')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("=" * 80)
    print("🔧 KPI 카드 최종 수정")
    print("=" * 80)

    # 1. 실제 근무일 0일 계산 로직 수정 (퇴사자 제외)
    print("\n1️⃣ 실제 근무일 0일 계산 수정 (퇴사자 제외)...")

    # JavaScript에서 employeeData 필터링 (9월 기준 401명만)
    old_zero_days = """            // 3. 실제 근무일 0일
            const zeroWorkingDays = employeeData.filter(emp =>
                parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0) === 0
            ).length;"""

    new_zero_days = """            // 3. 실제 근무일 0일 (9월 현재 재직자만)
            const zeroWorkingDays = employeeData.filter(emp => {
                const actualDays = parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0);
                // employeeData는 이미 9월 기준 필터링된 401명
                return actualDays === 0;
            }).length;"""

    content = content.replace(old_zero_days, new_zero_days)

    # 2. KPI 카드 순서 및 명칭 정리
    print("\n2️⃣ KPI 카드 순서 및 명칭 정리...")

    # 기존 출근율 88% 미만 카드를 찾아서 제거 (잘못된 위치에 있는 것)
    # 그리고 올바른 위치에 다시 추가

    # 먼저 잘못 추가된 출근율 카드 제거
    pattern = r'<!-- KPI 카드 4-1: 출근율 88% 미만 -->[\s\S]*?</div>\s*\n\s*\n'
    content = re.sub(pattern, '', content)

    # 올바른 순서로 KPI 카드들 재배치
    # 5번 위치에 출근율 88% 미만 추가

    # 먼저 기존 5번 카드(AQL FAIL)를 6번으로 변경
    content = content.replace(
        '<!-- KPI 카드 5: AQL FAIL 보유자 -->',
        '<!-- KPI 카드 6: AQL FAIL 보유자 -->'
    )

    # 기존 6번을 7번으로
    content = content.replace(
        '<!-- KPI 카드 6: 3개월 연속 AQL FAIL -->',
        '<!-- KPI 카드 7: 3개월 연속 AQL FAIL -->'
    )

    # 기존 7번을 8번으로
    content = content.replace(
        '<!-- KPI 카드 7: 구역 AQL Reject Rate -->',
        '<!-- KPI 카드 8: 구역 AQL Reject 3% 이상 -->'
    )

    # 기존 8번을 9번으로
    content = content.replace(
        '<!-- KPI 카드 8: 5PRS 통과율 < 95% -->',
        '<!-- KPI 카드 9: 5PRS 통과율 < 95% -->'
    )

    # 기존 9번을 10번으로
    content = content.replace(
        '<!-- KPI 카드 9: 5PRS 검사량 < 100족 -->',
        '<!-- KPI 카드 10: 5PRS 검사량 < 100족 -->'
    )

    # 출근율 88% 미만 카드를 5번 위치에 추가
    attendance_kpi = """
                <!-- KPI 카드 5: 출근율 88% 미만 -->
                <div class="kpi-card" onclick="showValidationModal('attendanceBelow88')" style="--card-color-1: #9b59b6; --card-color-2: #8e44ad; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.1);">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value" id="kpiAttendanceBelow88">-</div>
                    <div class="kpi-label">출근율 88% 미만</div>
                </div>
"""

    # 최소 근무일 미충족 카드 다음에 삽입
    pattern = r'(<!-- KPI 카드 4: 최소 근무일 미충족 -->[\s\S]*?</div>\s*)\n'
    replacement = r'\1\n' + attendance_kpi
    content = re.sub(pattern, replacement, content, count=1)

    # 3. JavaScript 계산 순서도 맞춰서 수정
    print("\n3️⃣ JavaScript 계산 로직 순서 수정...")

    # 기존 출근율 계산 제거
    pattern = r'// 4-1\. 출근율 88% 미만[\s\S]*?document\.getElementById\(\'kpiAttendanceBelow88\'\)\.textContent = attendanceBelow88 \+ \'명\';\s*\n'
    content = re.sub(pattern, '', content)

    # 5번 위치에 출근율 계산 추가
    attendance_js = """
            // 5. 출근율 88% 미만
            const attendanceBelow88 = employeeData.filter(emp =>
                parseFloat(emp['attendance_rate'] || 0) < 88
            ).length;
            document.getElementById('kpiAttendanceBelow88').textContent = attendanceBelow88 + '명';
"""

    # AQL FAIL 계산 앞에 추가하고 번호 조정
    content = content.replace(
        '            // 5. AQL FAIL 보유자',
        attendance_js + '\n            // 6. AQL FAIL 보유자'
    )

    # 나머지 번호들도 조정
    content = content.replace(
        '            // 6. 3개월 연속 AQL FAIL',
        '            // 7. 3개월 연속 AQL FAIL'
    )

    content = content.replace(
        '            // 7. 구역 AQL Reject Rate 3% 초과',
        '            // 8. 구역 AQL Reject Rate 3% 초과'
    )

    content = content.replace(
        '            // 8. 5PRS 통과율',
        '            // 9. 5PRS 통과율'
    )

    content = content.replace(
        '            // 9. 5PRS 검사량',
        '            // 10. 5PRS 검사량'
    )

    # 4. KPI 레이블 텍스트 확인 및 수정
    print("\n4️⃣ KPI 레이블 텍스트 확인...")

    # 구역 AQL Reject 레이블 확인
    if '구역 AQL Reject 3% 이상' not in content:
        content = content.replace(
            '<div class="kpi-label">Area AQL Reject > 0.65%</div>',
            '<div class="kpi-label">구역 AQL Reject 3% 이상</div>'
        )

    # 5. 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ 수정 완료:")
    print("  1. 실제 근무일 0일: 퇴사자 제외 (401명 기준)")
    print("  2. KPI 카드 순서 정리:")
    print("     - 카드 1: 총 근무일수")
    print("     - 카드 2: 무단결근 3일 이상")
    print("     - 카드 3: 실제 근무일 0일")
    print("     - 카드 4: 최소 근무일 미충족")
    print("     - 카드 5: 출근율 88% 미만 (새로 추가)")
    print("     - 카드 6: AQL FAIL 보유자")
    print("     - 카드 7: 3개월 연속 AQL FAIL")
    print("     - 카드 8: 구역 AQL Reject 3% 이상")
    print("     - 카드 9: 5PRS 통과율 < 95%")
    print("     - 카드 10: 5PRS 검사량 < 100족")

    return True

if __name__ == "__main__":
    success = fix_kpi_cards()
    if success:
        print("\n🎉 KPI 카드 최종 수정 완료!")
        print("대시보드를 재생성하세요: python integrated_dashboard_final.py --month 9 --year 2025")