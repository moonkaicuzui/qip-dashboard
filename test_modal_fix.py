#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모달 창 수정 테스트 스크립트
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_dashboard():
    """대시보드를 실행하고 모달 테스트를 안내합니다"""
    print("=" * 60)
    print("🔧 조직도 탭 모달 창 수정 테스트")
    print("=" * 60)
    print()

    print("📋 수정 내용:")
    print("  1. backdrop: 'static' → true (배경 클릭으로 닫기 가능)")
    print("  2. e.preventDefault() 제거 (Bootstrap 기본 동작 허용)")
    print("  3. 불필요한 이벤트 핸들러 제거")
    print("  4. 에러 처리 강화")
    print()

    print("🧪 테스트 방법:")
    print("  1. 대시보드가 열리면 '조직도' 탭을 클릭하세요")
    print("  2. 조직도에서 아무 직원 노드를 클릭하세요")
    print("  3. 모달이 열리면 다음을 테스트하세요:")
    print("     - X 버튼 클릭으로 닫기")
    print("     - '닫기' 버튼 클릭으로 닫기")
    print("     - 배경 클릭으로 닫기")
    print("     - ESC 키로 닫기")
    print("  4. 여러 번 열고 닫아도 정상 작동하는지 확인하세요")
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

                print("\n✨ 테스트 준비 완료!")
                print("\n💡 팁: 개발자 콘솔(F12)을 열어 로그를 확인하면 더 자세한 정보를 볼 수 있습니다.")
                print("   - '모달 완전히 닫힘' 메시지 확인")
                print("   - 에러 메시지 없음 확인")

            else:
                print("⚠️ HTML 파일을 찾을 수 없습니다.")

        else:
            print("❌ 대시보드 생성 중 오류가 발생했습니다:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    run_dashboard()