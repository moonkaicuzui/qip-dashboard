#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모달 창 긴급 수정 테스트 스크립트
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_dashboard():
    """대시보드를 실행하고 모달 수정 사항을 테스트합니다"""
    print("=" * 60)
    print("🚨 조직도 탭 모달 창 긴급 수정 테스트")
    print("=" * 60)
    print()

    print("🔧 수정 내용:")
    print("  1. tabindex와 aria 속성 추가로 접근성 개선")
    print("  2. 백드롭 클릭 이벤트 수동 추가 (fallback)")
    print("  3. ESC 키 이벤트 수동 추가 (fallback)")
    print("  4. 이벤트 리스너 정리 개선")
    print("  5. body 스타일 완전 초기화")
    print()

    print("🧪 테스트 항목:")
    print("  ✅ 모달 외부 클릭으로 닫기")
    print("  ✅ ESC 키로 닫기")
    print("  ✅ X 버튼 클릭으로 닫기")
    print("  ✅ '닫기' 버튼 클릭으로 닫기")
    print("  ✅ 여러 번 열고 닫아도 정상 작동")
    print("  ✅ 화면이 정지되지 않음")
    print()

    print("📊 대시보드 생성 중...")

    try:
        # integrated_dashboard_final.py 실행
        result = subprocess.run(
            [sys.executable, "integrated_dashboard_final.py"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ 대시보드가 성공적으로 생성되었습니다!")

            # HTML 파일 찾기
            output_dir = "output_files"
            html_files = [f for f in os.listdir(output_dir) if f.endswith('.html') and 'Dashboard' in f]

            if html_files:
                # 가장 최근 파일 선택
                latest_html = max(html_files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)))
                html_path = os.path.join(output_dir, latest_html)

                print(f"\n📁 생성된 파일: {html_path}")
                print("\n🌐 브라우저에서 대시보드를 엽니다...")

                # macOS에서 브라우저 열기
                subprocess.run(["open", html_path])

                print("\n" + "=" * 60)
                print("✨ 테스트 준비 완료!")
                print("=" * 60)
                print()
                print("📋 테스트 순서:")
                print("1. '조직도' 탭을 클릭하세요")
                print("2. 아무 직원 노드를 클릭하여 모달을 여세요")
                print("3. 다음 방법으로 모달을 닫아보세요:")
                print("   - 🖱️ 모달 밖의 어두운 영역 클릭")
                print("   - ⌨️ ESC 키 누르기")
                print("   - ❌ X 버튼 클릭")
                print("   - 🔘 '닫기' 버튼 클릭")
                print()
                print("⚠️ 중요: 모든 방법으로 모달이 닫혀야 합니다!")
                print("💡 개발자 콘솔에서 다음 로그를 확인하세요:")
                print("   - '백드롭 클릭 감지'")
                print("   - 'ESC 키 감지'")
                print("   - '모달 완전히 닫힘'")

            else:
                print("⚠️ HTML 파일을 찾을 수 없습니다.")

        else:
            print("❌ 대시보드 생성 중 오류가 발생했습니다:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    run_dashboard()