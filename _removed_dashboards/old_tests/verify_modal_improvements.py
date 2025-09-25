#!/usr/bin/env python3
"""
대시보드 모달 개선사항 검증 스크립트
"""

import os
import re
from bs4 import BeautifulSoup

def verify_modal_improvements():
    """모달 개선사항 검증"""

    dashboard_path = 'output_files/Incentive_Dashboard_2025_09_Version_5.html'

    print("=" * 60)
    print("🔍 대시보드 모달 개선사항 검증")
    print("=" * 60)

    # HTML 파일 읽기
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 검증 항목들
    checks = {
        'Modal Functions': {
            'showTotalWorkingDaysDetails': False,
            'showZeroWorkingDaysDetails': False,
            'showAbsentWithoutInformDetails': False,
            'showMinimumDaysNotMetDetails': False
        },
        'Calendar Features': {
            'calendar-grid': False,
            'calendar-day': False,
            'work-day': False,
            'weekend': False,
            '💼': False,  # 근무일 이모티콘
            '🏖️': False,  # 주말 이모티콘
            '🎉': False   # 공휴일 이모티콘
        },
        'Progress Bar': {
            'progress-bar': False,
            'bg-danger': False,
            'bg-warning': False,
            'bg-info': False
        },
        'Badge Components': {
            'badge-primary': False,
            'badge-danger': False,
            'badge-warning': False,
            'badge-success': False
        }
    }

    # 각 항목 체크
    for category, items in checks.items():
        for item in items:
            if item in html_content:
                checks[category][item] = True

    # 결과 출력
    all_passed = True

    for category, items in checks.items():
        print(f"\n📋 {category}:")
        for item, found in items.items():
            status = "✅" if found else "❌"
            print(f"  {status} {item}: {'Found' if found else 'Not Found'}")
            if not found:
                all_passed = False

    # 추가 검증: JavaScript 함수 내용 확인
    print("\n📊 JavaScript 함수 내용 검증:")

    # showTotalWorkingDaysDetails 함수 내용 확인
    if 'const workDays = [2,3,4,5,6,9,10,11,12,13,16,17,18,19]' in html_content:
        print("  ✅ Total Working Days: 근무일 배열 정의 확인")
    else:
        print("  ❌ Total Working Days: 근무일 배열 정의 없음")
        all_passed = False

    # showZeroWorkingDaysDetails 함수 내용 확인
    if 'const zeroWorkingEmployees = window.employeeData.filter' in html_content:
        print("  ✅ Zero Working Days: 직원 필터링 로직 확인")
    else:
        print("  ❌ Zero Working Days: 직원 필터링 로직 없음")
        all_passed = False

    # showAbsentWithoutInformDetails 함수 내용 확인
    if 'unapproved_absence_days' in html_content:
        print("  ✅ Absent Without Inform: 무단결근 데이터 처리 확인")
    else:
        print("  ❌ Absent Without Inform: 무단결근 데이터 처리 없음")
        all_passed = False

    # showMinimumDaysNotMetDetails 함수 내용 확인
    if 'const minimumRequired = currentDay < 20 ? 7 : 12' in html_content:
        print("  ✅ Minimum Days Not Met: 최소 근무일 계산 로직 확인")
    else:
        print("  ❌ Minimum Days Not Met: 최소 근무일 계산 로직 없음")
        all_passed = False

    # 데이터 확인
    print("\n📈 대시보드 데이터 확인:")

    # window.employeeData 확인
    employee_data_match = re.search(r'window\.employeeData\s*=\s*(\[[\s\S]*?\]);', html_content)
    if employee_data_match:
        print("  ✅ window.employeeData 정의됨")
        # 데이터 크기 확인
        employee_count = html_content.count('"Employee No"')
        print(f"  📊 직원 데이터: 약 {employee_count}개 레코드")
    else:
        print("  ❌ window.employeeData 정의되지 않음")
        all_passed = False

    # 최종 결과
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 모든 모달 개선사항이 정상적으로 적용되었습니다!")
    else:
        print("⚠️ 일부 모달 개선사항이 누락되었습니다.")
    print("=" * 60)

    # 상세 통계
    print("\n📊 상세 통계:")
    total_checks = sum(len(items) for items in checks.values())
    passed_checks = sum(1 for items in checks.values() for found in items.values() if found)
    print(f"  • 전체 검증 항목: {total_checks}개")
    print(f"  • 통과 항목: {passed_checks}개")
    print(f"  • 성공률: {passed_checks/total_checks*100:.1f}%")

    return all_passed

if __name__ == "__main__":
    verify_modal_improvements()