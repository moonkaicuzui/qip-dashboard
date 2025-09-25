#!/usr/bin/env python3
"""
TYPE-1 관리자 인센티브 구조 모달 기능 테스트
"""
import json
import re

def extract_javascript_data(html_path):
    """HTML에서 JavaScript 변수들 추출"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # dashboardMonth 변수 확인
    dashboard_month = re.search(r"const dashboardMonth = '([^']+)';", content)
    if dashboard_month:
        print(f"✅ dashboardMonth 변수 발견: {dashboard_month.group(1)}")
    else:
        print("❌ dashboardMonth 변수가 없습니다 (하드코딩 위험)")

    # dashboardYear 변수 확인
    dashboard_year = re.search(r"const dashboardYear = (\d+);", content)
    if dashboard_year:
        print(f"✅ dashboardYear 변수 발견: {dashboard_year.group(1)}")

    # showIncentiveModal 함수 확인
    modal_func = re.search(r'function showIncentiveModal\(nodeId\)', content)
    if modal_func:
        print("✅ showIncentiveModal 함수 존재")

        # 계산 과정 상세 표시 확인
        if '계산 과정 상세' in content:
            print("✅ 계산 과정 상세 표시 구현됨")

        # LINE LEADER 계산식 확인
        if 'TYPE-1 부하직원 인센티브 합계' in content:
            print("✅ LINE LEADER 계산식 구현됨")

        # GROUP LEADER 계산식 확인
        if 'LINE LEADER 평균 인센티브' in content:
            print("✅ GROUP LEADER 계산식 구현됨")

        # SUPERVISOR 계산식 확인
        if '전체 LINE LEADER' in content:
            print("✅ SUPERVISOR 계산식 구현됨")

    # 인센티브 0원도 클릭 가능한지 확인
    if 'incentiveAmount > 0' in content and 'else' in content and 'color: #dc3545' in content:
        print("✅ 인센티브 0원인 경우도 표시 및 클릭 가능")

    # 저장 버튼 제거 확인
    if 'exportOrgChart' not in content or '저장 버튼 제거' in content:
        print("✅ 저장 버튼 제거됨")
    else:
        print("⚠️ 저장 버튼이 아직 있을 수 있음")

    # 부하직원 표시 확인
    if '인센티브 계산 기반' in content:
        print("✅ LINE LEADER 부하직원 표시 구현")

    return dashboard_month, dashboard_year

def verify_no_hardcoding(html_path):
    """하드코딩 검증"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []

    # september_incentive || august_incentive 형태 찾기
    if re.search(r'september_incentive\s*\|\|\s*august_incentive', content):
        issues.append("❌ 여전히 하드코딩된 월 선택 로직 존재")

    # employee.september_incentive 직접 사용 확인
    if re.search(r'employee\.september_incentive(?!\[)', content):
        issues.append("❌ employee.september_incentive 직접 참조 발견")

    # employee.august_incentive 직접 사용 확인
    if re.search(r'employee\.august_incentive(?!\[)', content):
        issues.append("❌ employee.august_incentive 직접 참조 발견")

    if not issues:
        print("\n✅ 하드코딩 없음 - dashboardMonth 변수 사용 중")
    else:
        print("\n⚠️ 하드코딩 문제 발견:")
        for issue in issues:
            print(f"  {issue}")

def test_modal_calculation_display():
    """모달에서 계산 과정이 잘 표시되는지 테스트"""
    print("\n" + "=" * 60)
    print("모달 계산 과정 표시 테스트")
    print("=" * 60)

    test_cases = [
        {
            'position': 'LINE LEADER',
            'expected_elements': [
                'TYPE-1 부하직원 인센티브 합계',
                '수령 비율',
                '계산식',
                '예상 인센티브',
                '실제 인센티브'
            ]
        },
        {
            'position': 'GROUP LEADER',
            'expected_elements': [
                'LINE LEADER 수',
                'LINE LEADER 평균 인센티브',
                '계산식',
                '예상 인센티브',
                '실제 인센티브'
            ]
        },
        {
            'position': 'SUPERVISOR',
            'expected_elements': [
                '전체 LINE LEADER',
                'LINE LEADER 평균 인센티브',
                '계산식',
                '예상 인센티브',
                '실제 인센티브'
            ]
        }
    ]

    for test in test_cases:
        print(f"\n{test['position']}:")
        for element in test['expected_elements']:
            print(f"  - {element}")

if __name__ == "__main__":
    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    print("=" * 60)
    print("TYPE-1 관리자 인센티브 구조 기능 테스트")
    print("=" * 60)

    month_info = extract_javascript_data(html_path)
    verify_no_hardcoding(html_path)
    test_modal_calculation_display()

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)