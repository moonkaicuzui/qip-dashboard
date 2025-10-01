#!/usr/bin/env python3
"""
무단 결근 모달 JavaScript 오류 확인 스크립트
"""
import sys
from playwright.sync_api import sync_playwright
import time

def test_modal_js_errors():
    """모달 열기 및 JavaScript 오류 확인"""
    print("📊 무단 결근 모달 JavaScript 오류 확인...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Console 메시지 캡처
        console_messages = []
        errors = []

        def handle_console(msg):
            console_messages.append(f"[{msg.type}] {msg.text}")
            if msg.type == 'error':
                errors.append(msg.text)
                print(f"❌ Console Error: {msg.text}")

        page.on('console', handle_console)

        # Page error 캡처
        def handle_page_error(error):
            errors.append(str(error))
            print(f"❌ Page Error: {error}")

        page.on('pageerror', handle_page_error)

        # 대시보드 열기
        dashboard_path = f"file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"
        print(f"📂 대시보드 로드: {dashboard_path}")
        page.goto(dashboard_path)

        # 페이지 로드 대기
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("\n✅ 페이지 로드 완료")
        print(f"   Console 메시지: {len(console_messages)}개")
        print(f"   에러: {len(errors)}개")

        # 요약 및 시스템 검증 탭 클릭
        print("\n🔍 요약 및 시스템 검증 탭 이동...")
        page.click('a[href="#validation"]')
        time.sleep(1)

        # 무단결근 3일 이상 카드 클릭
        print("\n🔍 무단결근 3일 이상 카드 클릭...")
        try:
            page.click('.kpi-card:has-text("무단결근 3일 이상")')
            time.sleep(2)
        except Exception as e:
            print(f"❌ 카드 클릭 실패: {e}")

        # 모달이 열렸는지 확인
        modal_visible = page.is_visible('#detailModal')
        print(f"\n모달 상태: {'열림' if modal_visible else '닫힘'}")

        if modal_visible:
            # 모달 내용 확인
            modal_content = page.locator('#detailModalContent').inner_html()

            # ${getTranslation...} 코드가 그대로 있는지 확인
            if '${' in modal_content:
                print("\n❌ Template literal이 평가되지 않음!")
                print("   다음 코드가 그대로 표시됨:")
                # ${로 시작하는 부분 찾기
                import re
                matches = re.findall(r'\$\{[^}]+\}', modal_content)
                for match in matches[:5]:  # 처음 5개만 출력
                    print(f"   - {match}")
            else:
                print("\n✅ Template literal 정상 평가됨")

        # 에러 요약
        print("\n" + "="*60)
        if errors:
            print(f"❌ 총 {len(errors)}개의 에러 발생:")
            for i, error in enumerate(errors[:10], 1):
                print(f"   {i}. {error[:200]}")
        else:
            print("✅ JavaScript 에러 없음")
        print("="*60)

        # 스크린샷
        screenshot_path = "test_modal_error.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 스크린샷 저장: {screenshot_path}")

        # 5초 대기
        time.sleep(5)
        browser.close()

        return len(errors) == 0

if __name__ == "__main__":
    try:
        result = test_modal_js_errors()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
