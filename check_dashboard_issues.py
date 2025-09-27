#!/usr/bin/env python3
"""
대시보드 문제점 체크리스트 및 원본과 비교 분석
"""

import os
from pathlib import Path

print("=" * 60)
print("📋 대시보드 문제점 체크리스트")
print("=" * 60)

# 체크리스트 작성
checklist = {
    "1. 데이터 구조 문제": {
        "employeeData 배열 형식": "❓",
        "type 필드 매핑": "❓",
        "position 필드 매핑": "❓",
        "name 필드 매핑": "❓",
        "인센티브 금액 필드": "❓"
    },
    "2. JavaScript 초기화 문제": {
        "DOMContentLoaded 이벤트": "❓",
        "window.onload 이벤트": "❓",
        "updateTypeSummaryTable 호출": "❓",
        "generatePositionTables 호출": "❓",
        "initValidationTab 호출": "❓"
    },
    "3. 탭 전환 문제": {
        "showTab 함수 정의": "❓",
        "탭 클릭 이벤트": "❓",
        "active 클래스 전환": "❓",
        "콘텐츠 영역 표시/숨김": "❓"
    },
    "4. 요약 탭 문제": {
        "typeSummaryBody 요소 존재": "❓",
        "TYPE별 집계 로직": "❓",
        "테이블 HTML 생성": "❓",
        "innerHTML 설정": "❓"
    },
    "5. 인센티브 기준 탭": {
        "criteriaContent 요소": "❓",
        "조건 매트릭스 데이터": "❓",
        "렌더링 함수": "❓"
    },
    "6. 조직도 탭": {
        "orgChartContent 요소": "❓",
        "drawOrgChart 함수": "❓",
        "D3.js 라이브러리": "❓"
    },
    "7. 시스템 검증 탭": {
        "validationContent 요소": "❓",
        "initValidationTab 함수": "❓",
        "KPI 데이터": "❓"
    }
}

# 체크리스트 출력
for category, items in checklist.items():
    print(f"\n{category}")
    print("-" * 40)
    for item, status in items.items():
        print(f"  {status} {item}")

# 원본과 새 버전 비교
print("\n" + "=" * 60)
print("🔍 원본(V5)과 새 버전(V6) 비교 분석")
print("=" * 60)

# 원본 파일 확인
original_file = Path("integrated_dashboard_final.py")
new_renderer = Path("dashboard_v2/modules/complete_renderer.py")
new_js = Path("dashboard_v2/static/js/dashboard_complete.js")

if original_file.exists():
    with open(original_file, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # 주요 패턴 확인
    print("\n원본(V5)에서 확인된 패턴:")
    if "window.onload" in original_content:
        print("  ✓ window.onload 사용")
    if "DOMContentLoaded" in original_content:
        print("  ✓ DOMContentLoaded 사용")
    if "updateTypeSummaryTable()" in original_content:
        print("  ✓ updateTypeSummaryTable() 호출")

# JavaScript 파일 분석
if new_js.exists():
    with open(new_js, 'r', encoding='utf-8') as f:
        js_content = f.read()

    print("\n새 버전(V6) JavaScript 분석:")

    # 중복 초기화 확인
    dom_content_loaded_count = js_content.count("DOMContentLoaded")
    window_onload_count = js_content.count("window.onload")

    print(f"  • DOMContentLoaded 이벤트: {dom_content_loaded_count}개")
    print(f"  • window.onload 이벤트: {window_onload_count}개")

    if dom_content_loaded_count > 1 or window_onload_count > 1:
        print("  ⚠️ 경고: 중복된 초기화 이벤트 발견!")

# 해결 방안 제시
print("\n" + "=" * 60)
print("💡 해결 방안")
print("=" * 60)

solutions = [
    "1. 모든 초기화 코드를 하나의 DOMContentLoaded 이벤트로 통합",
    "2. employeeData가 배열인지 확인하고 필요한 필드가 모두 매핑되었는지 검증",
    "3. 탭 전환 이벤트 리스너가 제대로 등록되었는지 확인",
    "4. 각 탭의 렌더링 함수가 초기화 시 호출되는지 확인",
    "5. 콘솔 에러 메시지를 확인하여 JavaScript 실행 중단 원인 파악"
]

for solution in solutions:
    print(f"  • {solution}")

print("\n" + "=" * 60)