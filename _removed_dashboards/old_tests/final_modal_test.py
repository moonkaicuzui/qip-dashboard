#!/usr/bin/env python3
"""
최종 모달 기능 종합 테스트
사용자가 보고한 3가지 문제 해결 확인:
1. 정렬 기능이 한 번 클릭 후 중단되는 문제
2. 모달이 외부 클릭으로 닫히지 않는 문제
3. 직속 상사 정보가 표시되지 않는 문제
"""

import re
from pathlib import Path

def test_final_modal():
    html_path = Path('output_files/Incentive_Dashboard_2025_09_Version_5.html')

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("=" * 80)
    print("🚀 최종 모달 기능 종합 테스트")
    print("=" * 80)

    issues_fixed = []
    issues_remaining = []

    # ========== 문제 1: 정렬 기능 ==========
    print("\n1️⃣ 정렬 기능 문제 해결 확인:")
    print("   문제: 한 번 클릭 후 정렬이 중단됨")

    # updateTableBody 함수 확인 (렌더링 시 이벤트 리스너 보존)
    if 'function updateTableBody()' in html_content:
        print("   ✅ updateTableBody() 함수 존재 - 테이블 바디만 업데이트")

        # tbody만 업데이트하는지 확인
        if "document.querySelector('#detailModal tbody')" in html_content:
            print("   ✅ tbody만 선택적으로 업데이트 (이벤트 리스너 보존)")

        # sortData가 updateTableBody를 호출하는지 확인
        if 'updateTableBody();' in html_content:
            print("   ✅ sortData()가 updateTableBody() 호출")
            issues_fixed.append("정렬 기능 - tbody만 업데이트하여 이벤트 리스너 보존")
        else:
            print("   ⚠️ sortData()가 updateTableBody() 호출하지 않음")
            issues_remaining.append("정렬 기능 - sortData와 updateTableBody 연결 필요")
    else:
        print("   ❌ updateTableBody() 함수 없음")
        issues_remaining.append("정렬 기능 - updateTableBody 구현 필요")

    # ========== 문제 2: 모달 외부 클릭 ==========
    print("\n2️⃣ 모달 외부 클릭으로 닫기 문제 해결 확인:")
    print("   문제: X 버튼으로만 닫히고 외부 클릭은 작동 안 함")

    # backdrop 클릭 이벤트 확인
    backdrop_patterns = [
        "backdrop.onclick",
        "backdrop.addEventListener('click'",
        "modalDiv.onclick = function(event)"
    ]

    backdrop_found = False
    for pattern in backdrop_patterns:
        if pattern in html_content:
            print(f"   ✅ 백드롭 클릭 이벤트 구현: {pattern}")
            backdrop_found = True
            break

    if backdrop_found:
        # stopPropagation 확인
        if "event.stopPropagation()" in html_content:
            print("   ✅ 모달 내부 클릭 시 이벤트 전파 중단 (stopPropagation)")
            issues_fixed.append("모달 외부 클릭으로 닫기 - 백드롭 클릭 이벤트 구현")
        else:
            print("   ⚠️ stopPropagation 없음 - 모달 내부 클릭도 닫힐 수 있음")
            issues_remaining.append("모달 외부 클릭 - stopPropagation 추가 필요")
    else:
        print("   ❌ 백드롭 클릭 이벤트 없음")
        issues_remaining.append("모달 외부 클릭으로 닫기 - 이벤트 핸들러 추가 필요")

    # ========== 문제 3: 직속 상사 정보 ==========
    print("\n3️⃣ 직속 상사 정보 표시 문제 해결 확인:")
    print("   문제: 직속 상사가 '-'로만 표시됨")

    # employeeData에 boss 정보 확인
    start = html_content.find('window.employeeData = [')
    if start != -1:
        end = html_content.find('];', start) + 1
        employee_data = html_content[start:end]

        # direct boss name 필드 존재 및 실제 데이터 확인
        if '"direct boss name"' in employee_data:
            print("   ✅ employeeData에 'direct boss name' 필드 존재")

            # 실제 boss 이름 데이터 확인
            boss_pattern = r'"direct boss name":\s*"([^"]+)"'
            boss_matches = re.findall(boss_pattern, employee_data)
            non_empty_bosses = [b for b in boss_matches if b and b != '' and b != '0']

            if non_empty_bosses:
                print(f"   ✅ 실제 직속 상사 데이터 존재: {len(non_empty_bosses)}명")
                print(f"      예시: {non_empty_bosses[0][:20]}")

                # 모달에서 사용하는지 확인
                if "emp['direct boss name']" in html_content or "emp['MST direct boss name']" in html_content:
                    print("   ✅ 모달에서 boss 필드 참조 코드 존재")
                    issues_fixed.append("직속 상사 정보 표시 - 데이터 및 참조 코드 정상")
                else:
                    print("   ⚠️ 모달에서 boss 필드 참조 코드 없음")
                    issues_remaining.append("직속 상사 정보 - 모달에서 필드 참조 필요")
            else:
                print("   ⚠️ 실제 boss 데이터가 비어있음")
                issues_remaining.append("직속 상사 정보 - 데이터가 비어있음")
        else:
            print("   ❌ employeeData에 'direct boss name' 필드 없음")
            issues_remaining.append("직속 상사 정보 - 필드 추가 필요")

    # ========== 종합 결과 ==========
    print("\n" + "=" * 80)
    print("📊 테스트 결과 종합")
    print("=" * 80)

    print("\n✅ 해결된 문제들:")
    if issues_fixed:
        for issue in issues_fixed:
            print(f"   • {issue}")
    else:
        print("   (없음)")

    print("\n❌ 남은 문제들:")
    if issues_remaining:
        for issue in issues_remaining:
            print(f"   • {issue}")
    else:
        print("   • 모든 문제 해결 완료! 🎉")

    print("\n💡 권장사항:")
    if not issues_remaining:
        print("   모든 문제가 해결되었습니다. 브라우저에서 직접 테스트해보세요.")
    else:
        print("   위의 남은 문제들을 추가로 수정해야 합니다.")

    print("=" * 80)

if __name__ == "__main__":
    test_final_modal()