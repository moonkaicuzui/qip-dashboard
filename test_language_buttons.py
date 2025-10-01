#!/usr/bin/env python3
"""
언어 버튼 위치 확인 테스트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 언어 버튼 위치 확인 테스트\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # 언어 버튼 확인
    lang_buttons = page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('[data-lang]');
            return Array.from(buttons).map(btn => ({
                lang: btn.getAttribute('data-lang'),
                text: btn.textContent,
                visible: btn.offsetParent !== null
            }));
        }
    """)

    print(f"발견된 언어 버튼: {len(lang_buttons)}개")
    for btn in lang_buttons:
        print(f"  - {btn['lang']}: {btn['text']} (visible: {btn['visible']})")

    # Org Chart 탭으로 이동
    print("\n📊 Org Chart 탭으로 이동...")
    page.click("#tabOrgChart")
    time.sleep(2)

    # 다시 언어 버튼 확인
    lang_buttons_after = page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('[data-lang]');
            return Array.from(buttons).map(btn => ({
                lang: btn.getAttribute('data-lang'),
                text: btn.textContent,
                visible: btn.offsetParent !== null
            }));
        }
    """)

    print(f"\nOrg Chart 탭 후 언어 버튼: {len(lang_buttons_after)}개")
    for btn in lang_buttons_after:
        print(f"  - {btn['lang']}: {btn['text']} (visible: {btn['visible']})")

    browser.close()

print("\n✅ 테스트 완료")