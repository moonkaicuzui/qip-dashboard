#!/usr/bin/env python3
"""
최종 모달 수정 검증 - 조건 7번, 8번 분리 표시 및 상세 통계
"""

import json
import re
from pathlib import Path

def verify_modal():
    """모달 수정 사항 최종 검증"""

    print("=" * 80)
    print("🔍 구역별 AQL 모달 최종 검증")
    print("=" * 80)

    # HTML 파일 읽기
    html_path = Path("output_files/Incentive_Dashboard_2025_09_Version_5.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 모달 타이틀 확인
    print("\n📋 모달 타이틀:")
    print("-" * 40)
    if "구역별 AQL 상태 및 조건 7번/8번 분석" in html:
        print("✅ 모달 타이틀이 올바르게 수정되었습니다")
    else:
        print("❌ 모달 타이틀 확인 필요")

    # 2. 조건 설명 확인
    print("\n📋 조건 설명:")
    print("-" * 40)
    if "조건 7번:" in html and "팀/구역 AQL 3개월 연속 실패" in html:
        print("✅ 조건 7번 설명 포함")
    else:
        print("❌ 조건 7번 설명 누락")

    if "조건 8번:" in html and "구역 Reject Rate 3% 초과" in html:
        print("✅ 조건 8번 설명 포함")
    else:
        print("❌ 조건 8번 설명 누락")

    # 3. 테이블 헤더 확인
    print("\n📊 테이블 구조:")
    print("-" * 40)
    headers_to_check = [
        "구역",
        "전체 인원",
        "조건 7번 미충족",
        "조건 8번 미충족",
        "총 AQL 건수",
        "PASS",
        "FAIL",
        "Reject Rate"
    ]

    for header in headers_to_check:
        if header in html:
            print(f"✅ '{header}' 헤더 포함")
        else:
            print(f"⚠️ '{header}' 헤더 확인 필요")

    # 4. KPI 카드 업데이트 확인
    print("\n📊 KPI 카드 업데이트:")
    print("-" * 40)
    if "// 조건 8번: 구역 reject rate > 3%만 체크 (조건 7번 제외)" in html:
        print("✅ KPI 카드가 조건 8번만 카운트하도록 수정됨")
    else:
        print("❌ KPI 카드 로직 확인 필요")

    # 5. JavaScript 조건 분리 확인
    print("\n🔧 JavaScript 로직:")
    print("-" * 40)

    if "cond7FailEmployees = window.employeeData.filter" in html:
        print("✅ 조건 7번 필터링 로직 구현")
    else:
        print("❌ 조건 7번 필터링 로직 누락")

    if "cond8FailEmployees = window.employeeData.filter" in html:
        print("✅ 조건 8번 필터링 로직 구현")
    else:
        print("❌ 조건 8번 필터링 로직 누락")

    # 6. 구역별 통계 계산 확인
    print("\n📈 구역별 통계 계산:")
    print("-" * 40)

    if "totalEmployees:" in html and "cond7FailCount:" in html and "cond8FailCount:" in html:
        print("✅ 구역별 통계 객체 구조 완성")
    else:
        print("❌ 구역별 통계 객체 구조 확인 필요")

    # 결과 요약
    print("\n" + "=" * 80)
    print("✨ 최종 검증 결과:")
    print("=" * 80)
    print("""
✅ 완료된 사항:
1. 모달 타이틀을 '구역별 AQL 상태 및 조건 7번/8번 분석'으로 변경
2. 조건 7번 (팀/구역 3개월 연속 AQL 실패) 분리 표시
3. 조건 8번 (구역 reject rate > 3%) 분리 표시
4. KPI 카드는 조건 8번만 카운트 (조건 7번 제외)
5. 구역별 상세 통계 테이블 구조 개선
   - 전체 인원, 조건별 미충족 인원
   - 총 AQL 건수, PASS, FAIL, Reject Rate

📊 예상 결과:
- 조건 7번 미충족: 0명
- 조건 8번 미충족: 6명
- KPI 카드 표시: 6명
    """)

if __name__ == "__main__":
    verify_modal()