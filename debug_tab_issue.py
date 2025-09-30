#!/usr/bin/env python3
"""
탭 전환 문제 디버깅 스크립트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 탭 전환 문제 디버깅")
print(f"대시보드: {dashboard_path}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 콘솔 메시지 캡처
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

    # 페이지 오류 캡처
    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    print("\n📋 콘솔 메시지:")
    for msg in console_messages:
        print(f"  {msg}")

    if page_errors:
        print("\n❌ JavaScript 오류:")
        for err in page_errors:
            print(f"  {err}")
    else:
        print("\n✅ JavaScript 오류 없음")

    # showTab 함수 존재 확인
    print("\n🔍 showTab 함수 확인...")
    try:
        result = page.evaluate("typeof showTab")
        print(f"  typeof showTab: {result}")

        if result == "function":
            print("  ✅ showTab 함수가 정의되어 있음")
        else:
            print("  ❌ showTab 함수가 정의되지 않음")
    except Exception as e:
        print(f"  ❌ 오류: {e}")

    # 탭 버튼 확인
    print("\n🔍 탭 버튼 확인...")
    tabs = page.locator(".tab")
    count = tabs.count()
    print(f"  탭 버튼 수: {count}")

    # Org Chart 탭 클릭 시도
    print("\n🖱️  Org Chart 탭 클릭 시도...")
    try:
        orgchart_tab = page.locator("#tabOrgChart")
        if orgchart_tab.count() > 0:
            print("  ✅ Org Chart 탭 버튼 발견")

            # 클릭 전 콘솔 메시지 초기화
            console_messages.clear()
            page_errors.clear()

            orgchart_tab.click()
            time.sleep(2)

            print("\n  클릭 후 콘솔 메시지:")
            for msg in console_messages:
                print(f"    {msg}")

            if page_errors:
                print("\n  ❌ 클릭 후 JavaScript 오류:")
                for err in page_errors:
                    print(f"    {err}")

            # active 클래스 확인
            active_tab = page.locator(".tab.active")
            if active_tab.count() > 0:
                active_text = active_tab.inner_text()
                print(f"\n  ✅ Active 탭: {active_text}")
            else:
                print("\n  ❌ Active 탭 없음")
        else:
            print("  ❌ Org Chart 탭 버튼 없음")
    except Exception as e:
        print(f"  ❌ 클릭 오류: {e}")

    print("\n⏸️  브라우저를 10초간 유지합니다. 직접 탭을 클릭해보세요...")
    time.sleep(10)

    browser.close()

print("\n✅ 디버깅 완료")