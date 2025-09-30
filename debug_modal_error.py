#!/usr/bin/env python3
"""
모달 표시 오류 디버깅
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 모달 표시 오류 디버깅\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 콘솔 메시지와 오류 캡처
    console_messages = []
    page_errors = []

    page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Org Chart 탭 클릭
    print("📊 Org Chart 탭 열기...")
    page.click("#tabOrgChart")
    time.sleep(2)

    print("\n🖱️  첫 번째 직원 카드 클릭 시도...")

    # 인센티브 정보 버튼 찾기
    try:
        # .btn-info 또는 인센티브 버튼 클릭
        incentive_buttons = page.locator("button.btn-info, .incentive-btn, [onclick*='showIncentiveModal']")
        button_count = incentive_buttons.count()
        print(f"  발견된 인센티브 버튼: {button_count}개")

        if button_count > 0:
            # 첫 번째 버튼 클릭
            incentive_buttons.first.click()
            time.sleep(2)

            print("\n📋 클릭 후 콘솔 메시지:")
            for msg in console_messages[-20:]:  # 최근 20개
                print(f"  {msg}")

            if page_errors:
                print("\n❌ JavaScript 오류:")
                for err in page_errors:
                    print(f"  {err}")

            # 모달이 표시되었는지 확인
            modal = page.locator(".modal.show, .modal[style*='display: block']")
            if modal.count() > 0:
                print("\n✅ 모달이 성공적으로 표시되었습니다!")
            else:
                print("\n❌ 모달이 표시되지 않았습니다.")
        else:
            print("  ❌ 인센티브 버튼을 찾을 수 없습니다.")

    except Exception as e:
        print(f"\n❌ 버튼 클릭 오류: {e}")

    print("\n⏸️  브라우저를 15초간 유지합니다...")
    time.sleep(15)

    browser.close()

print("\n✅ 디버깅 완료")