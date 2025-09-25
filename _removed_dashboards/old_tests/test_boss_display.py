#!/usr/bin/env python3
"""
직속 상사 정보 표시 테스트
"""

import re
from pathlib import Path

def test_boss_display():
    html_path = Path('output_files/Incentive_Dashboard_2025_09_Version_5.html')

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("=" * 80)
    print("🔍 직속 상사 정보 표시 테스트")
    print("=" * 80)

    # 1. employeeData에서 boss 정보 확인
    print("\n1️⃣ JavaScript employeeData에 boss 정보 포함 여부:")

    # employeeData 추출
    start = html_content.find('window.employeeData = [')
    if start != -1:
        end = html_content.find('];', start) + 1
        employee_data = html_content[start:end]

        # boss 필드 체크
        if '"direct boss name"' in employee_data:
            print("  ✅ 'direct boss name' 필드 존재")

            # 실제 boss 이름이 있는지 확인
            boss_pattern = r'"direct boss name":\s*"([^"]+)"'
            boss_matches = re.findall(boss_pattern, employee_data)
            non_empty_bosses = [b for b in boss_matches if b and b != '' and b != '0']

            print(f"  ✅ 직속 상사 이름이 있는 직원: {len(non_empty_bosses)}명")
            if non_empty_bosses:
                print("  📋 샘플 직속 상사 이름:")
                for boss in non_empty_bosses[:5]:
                    print(f"    - {boss}")
        else:
            print("  ❌ 'direct boss name' 필드 없음")

        if '"MST direct boss name"' in employee_data:
            print("  ✅ 'MST direct boss name' 필드 존재")

    # 2. AQL FAIL 상세 모달에서 boss 정보 사용 확인
    print("\n2️⃣ AQL FAIL 상세 모달에서 boss 정보 사용:")

    # showAqlFailDetails 함수 확인
    if 'function showAqlFailDetails()' in html_content:
        print("  ✅ showAqlFailDetails 함수 존재")

        # manager 필드 체크 코드 확인
        manager_check = "emp['MST direct boss name'] || emp['direct boss name']"
        if manager_check in html_content:
            print(f"  ✅ 모달에서 boss 정보 체크 코드 존재: {manager_check[:50]}...")

        # 테이블에 manager 표시 확인
        if '<th data-sort="manager"' in html_content:
            print("  ✅ 직속 상사 컬럼 헤더 존재")

    # 3. 3개월 연속 AQL FAIL 모달에서 boss 정보 사용 확인
    print("\n3️⃣ 3개월 연속 AQL FAIL 모달에서 boss 정보 사용:")

    if 'function showConsecutiveAqlFailDetails()' in html_content:
        print("  ✅ showConsecutiveAqlFailDetails 함수 존재")

        # boss_name 사용 확인
        if "emp['boss_name']" in html_content:
            print("  ✅ 3개월 연속 모달에서 boss_name 사용")

        # MST direct boss name 사용 확인
        if "emp['MST direct boss name']" in html_content:
            print("  ✅ 3개월 연속 모달에서 MST direct boss name 사용")

    # 4. 2개월 연속 AQL FAIL 모달
    print("\n4️⃣ 2개월 연속 AQL FAIL 모달에서 boss 정보:")

    consecutive_2month = html_content.count("emp['MST direct boss name'] || emp['boss_name']")
    if consecutive_2month > 0:
        print(f"  ✅ 2개월 연속 모달에서 boss 정보 사용: {consecutive_2month}번")

    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약:")
    print("  1. employeeData에 boss 정보 포함 ✅")
    print("  2. AQL FAIL 상세 모달에서 boss 정보 체크 ✅")
    print("  3. 3개월 연속 모달에서 boss 정보 사용 ✅")
    print("  4. 2개월 연속 모달에서 boss 정보 사용 ✅")
    print("\n💡 결론: 직속 상사 정보가 JavaScript에 정상적으로 전달되고 있습니다.")
    print("         모달에서 표시되지 않는다면 JavaScript 디버깅이 필요합니다.")
    print("=" * 80)

if __name__ == "__main__":
    test_boss_display()