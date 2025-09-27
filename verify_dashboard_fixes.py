#!/usr/bin/env python3
"""
대시보드 수정사항 검증 스크립트
"""

import os
from pathlib import Path

print("=" * 60)
print("🔍 대시보드 수정사항 검증")
print("=" * 60)

# 대시보드 파일 확인
dashboard_file = Path("output_files/Incentive_Dashboard_2025_09_Version_6.html")

if not dashboard_file.exists():
    print("❌ 대시보드 파일이 존재하지 않습니다!")
    exit(1)

# HTML 내용 읽기
with open(dashboard_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 검증 항목들
checks = {
    "1. 통합된 초기화 함수": {
        "pattern": "function initializeDashboard()",
        "found": False
    },
    "2. 단일 DOMContentLoaded": {
        "pattern": "document.addEventListener('DOMContentLoaded'",
        "found": False,
        "count": 0
    },
    "3. window.onload 제거": {
        "pattern": "window.onload = function()",
        "found": False
    },
    "4. renderCriteriaTab 함수": {
        "pattern": "function renderCriteriaTab()",
        "found": False
    },
    "5. updateTypeSummaryTable 함수": {
        "pattern": "function updateTypeSummaryTable()",
        "found": False
    },
    "6. showTab 함수": {
        "pattern": "window.showTab = function showTab",
        "found": False
    },
    "7. 탭 이벤트 리스너": {
        "pattern": "setupTabEventListeners()",
        "found": False
    },
    "8. employeeData 배열": {
        "pattern": "window.employeeData =",
        "found": False
    }
}

# 패턴 검색
for name, check in checks.items():
    if name == "2. 단일 DOMContentLoaded":
        # DOMContentLoaded 개수 카운트
        count = content.count(check["pattern"])
        check["count"] = count
        check["found"] = (count == 1)
    elif name == "3. window.onload 제거":
        # window.onload가 없어야 함
        check["found"] = check["pattern"] not in content
    else:
        check["found"] = check["pattern"] in content

# 결과 출력
print("\n📋 검증 결과:\n")
all_passed = True

for name, check in checks.items():
    if name == "2. 단일 DOMContentLoaded":
        if check["found"]:
            print(f"✅ {name}: 1개 (정상)")
        else:
            print(f"❌ {name}: {check['count']}개 발견 (1개여야 함)")
            all_passed = False
    elif name == "3. window.onload 제거":
        if check["found"]:
            print(f"✅ {name}: 제거됨")
        else:
            print(f"❌ {name}: 아직 존재함")
            all_passed = False
    else:
        if check["found"]:
            print(f"✅ {name}")
        else:
            print(f"❌ {name}: 찾을 수 없음")
            all_passed = False

# JavaScript 에러 체크를 위한 패턴
error_patterns = [
    "Cannot read property",
    "undefined is not",
    "null is not",
    "is not defined",
    "Uncaught TypeError",
    "Uncaught ReferenceError"
]

print("\n🐛 JavaScript 에러 패턴 검사:")
js_errors_found = False
for pattern in error_patterns:
    if pattern in content:
        print(f"⚠️ 에러 패턴 발견: {pattern}")
        js_errors_found = True

if not js_errors_found:
    print("✅ JavaScript 에러 패턴이 발견되지 않았습니다.")

# 데이터 필드 매핑 확인
print("\n📊 데이터 필드 매핑 확인:")
field_mappings = {
    "type 필드": "emp['type']",
    "position 필드": "emp['position']",
    "name 필드": "emp['name']",
    "emp_no 필드": "emp['emp_no']"
}

for field_name, pattern in field_mappings.items():
    if pattern in content:
        print(f"✅ {field_name}: 매핑 존재")
    else:
        print(f"⚠️ {field_name}: 직접 매핑 없음 (변환 필요할 수 있음)")

# 최종 결과
print("\n" + "=" * 60)
if all_passed and not js_errors_found:
    print("✅ 모든 검증 항목 통과! 대시보드가 정상적으로 수정되었습니다.")
else:
    print("⚠️ 일부 검증 항목이 실패했습니다. 추가 수정이 필요할 수 있습니다.")
print("=" * 60)

# 파일 크기 정보
file_size_mb = dashboard_file.stat().st_size / (1024 * 1024)
print(f"\n📁 파일 정보:")
print(f"  • 파일명: {dashboard_file}")
print(f"  • 크기: {file_size_mb:.2f} MB")
print(f"  • 생성 시간: {Path(dashboard_file).stat().st_mtime}")