#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동적 월 참조 검증 스크립트
모든 탭과 모달이 올바른 월 데이터를 표시하는지 검증
"""

import re

def verify_dynamic_month():
    """대시보드 코드에서 하드코딩된 월 참조 검증"""

    print("=" * 60)
    print("🔍 동적 월 참조 검증")
    print("=" * 60)
    print()

    # integrated_dashboard_final.py 파일 검사
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 하드코딩 패턴 검사
    issues = []

    # 1. august_incentive 하드코딩 검사 (Python 코드 제외)
    pattern1 = r'emp\.august_incentive(?![^{]*})'  # JavaScript 코드만
    matches1 = re.findall(pattern1, content)
    if matches1:
        issues.append(f"❌ JavaScript에서 'emp.august_incentive' 하드코딩 발견: {len(matches1)}건")

    # 2. data.august_incentive 패턴 검사
    pattern2 = r'data\.august_incentive'
    matches2 = re.findall(pattern2, content)
    if matches2:
        issues.append(f"❌ 'data.august_incentive' 하드코딩 발견: {len(matches2)}건")

    # 3. 하드코딩된 월 텍스트 검사 (한국어)
    pattern3 = r'["\']\s*8월\s*["\']'
    matches3 = re.findall(pattern3, content)
    # 번역 키나 주석 제외
    actual_issues = [m for m in matches3 if '기준' in content[content.find(m)-50:content.find(m)+50]]
    if actual_issues:
        issues.append(f"⚠️ 하드코딩된 '8월' 텍스트 발견: {len(actual_issues)}건")

    # 4. 하드코딩된 년도-월 조합
    pattern4 = r'2025년\s*8월'
    matches4 = re.findall(pattern4, content)
    if matches4:
        issues.append(f"❌ 하드코딩된 '2025년 8월' 발견: {len(matches4)}건")

    # 동적 참조 패턴 검사
    dynamic_patterns = {
        "dashboardMonth + '_incentive'": len(re.findall(r"dashboardMonth\s*\+\s*'_incentive'", content)),
        "{month_kor}": len(re.findall(r'\{month_kor\}', content)),
        "{year}": len(re.findall(r'\{year\}(?!s)', content)),
        "동적 월 계산": len(re.findall(r'month_kor_map|monthText', content))
    }

    print("📋 검증 결과:")
    print("-" * 40)

    if issues:
        print("⚠️ 발견된 문제:")
        for issue in issues:
            print(f"  {issue}")
        print()
    else:
        print("✅ 하드코딩된 월 참조를 찾을 수 없습니다!")
        print()

    print("✅ 동적 참조 사용 현황:")
    for pattern, count in dynamic_patterns.items():
        if count > 0:
            print(f"  - {pattern}: {count}회 사용")

    print()
    print("=" * 60)
    print("🎯 권장 사항:")
    print("  1. 모든 인센티브 필드는 dashboardMonth + '_incentive' 사용")
    print("  2. 월 표시는 {month_kor} 변수 사용")
    print("  3. 년도는 {year} 변수 사용")
    print("  4. JavaScript에서도 동적 월 변수 활용")
    print()
    print("📊 각 탭별 확인 포인트:")
    print("  - 대시보드 요약: 월별 통계가 올바른지")
    print("  - 조직도: 인센티브 계산이 현재 월 기준인지")
    print("  - 직급별 상세: LINE LEADER 등 통계가 정확한지")
    print("  - 인센티브 계산 설명: 예시가 현재 월로 표시되는지")
    print("  - 모달: 예상/실제 인센티브가 현재 월 데이터인지")
    print("=" * 60)

if __name__ == "__main__":
    verify_dynamic_month()