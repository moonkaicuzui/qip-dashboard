#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모달 수정 사항 검증 스크립트
"""

import re
import os

def verify_modal_fixes():
    """integrated_dashboard_final.py 파일에서 모달 수정사항 확인"""

    file_path = "integrated_dashboard_final.py"

    print("=" * 60)
    print("🔍 모달 수정사항 검증")
    print("=" * 60)
    print()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 검증 항목들
    checks = {
        "✅ backdrop: true 설정": "backdrop: true,",
        "✅ keyboard: true 설정": "keyboard: true,",
        "✅ 백드롭 클릭 이벤트": "backdrop.addEventListener\\('click'",
        "✅ ESC 키 핸들러": "if \\(e.key === 'Escape'\\)",
        "✅ forceCloseModal 함수": "window.forceCloseModal = function",
        "✅ tabindex 설정": "modalElement.setAttribute\\('tabindex', '-1'\\)",
        "✅ aria-hidden 설정": "modalElement.setAttribute\\('aria-hidden', 'true'\\)",
        "✅ 모달 dispose 처리": "modalInstance.dispose\\(\\)",
        "✅ 백드롭 제거": "querySelectorAll\\('.modal-backdrop'\\)",
        "✅ body 스타일 초기화": "document.body.style.removeProperty"
    }

    print("📋 필수 수정사항 체크리스트:")
    print("-" * 40)

    all_passed = True
    for desc, pattern in checks.items():
        if re.search(pattern, content):
            print(f"  {desc}")
        else:
            print(f"  ❌ {desc[2:]} - 찾을 수 없음")
            all_passed = False

    print()
    print("=" * 60)

    if all_passed:
        print("✅ 모든 수정사항이 올바르게 적용되었습니다!")
        print()
        print("📊 예상 동작:")
        print("  1. 모달 외부 클릭 → 닫힘")
        print("  2. ESC 키 → 닫힘")
        print("  3. X 버튼 → 닫힘")
        print("  4. '닫기' 버튼 → 닫힘")
        print("  5. 화면 정지 현상 → 해결")
        print()
        print("💡 추가 안전장치:")
        print("  - 기존 모달 자동 정리")
        print("  - 백드롭 강제 제거")
        print("  - body 스타일 완전 초기화")
        print("  - forceCloseModal() 비상 탈출 함수")
    else:
        print("⚠️ 일부 수정사항이 누락되었습니다!")
        print("다시 확인이 필요합니다.")

    print("=" * 60)

    # HTML 파일 확인
    output_dir = "output_files"
    html_files = [f for f in os.listdir(output_dir) if f.endswith('.html') and 'Dashboard' in f]

    if html_files:
        latest_html = max(html_files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)))
        print(f"\n📁 테스트 파일: {os.path.join(output_dir, latest_html)}")
        print("\n🧪 브라우저에서 직접 테스트해주세요:")
        print("  1. 조직도 탭 클릭")
        print("  2. 직원 노드 클릭")
        print("  3. 모달 밖 클릭으로 닫기 확인")

    return all_passed

if __name__ == "__main__":
    verify_modal_fixes()