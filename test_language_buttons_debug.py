#!/usr/bin/env python3
"""
언어 버튼 Validation 탭 문제 디버깅
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 언어 버튼 Validation 탭 디버깅\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
    
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 초기 언어 확인
    initial_lang = page.evaluate("() => window.currentLanguage || 'ko'")
    print(f"초기 언어: {initial_lang}")
    
    # 언어 버튼 위치 확인
    lang_buttons = page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('[data-lang]');
            return Array.from(buttons).map(btn => ({
                lang: btn.getAttribute('data-lang'),
                text: btn.textContent.trim(),
                visible: btn.offsetParent !== null,
                inHeader: btn.closest('.language-switcher') !== null,
                x: btn.getBoundingClientRect().x,
                y: btn.getBoundingClientRect().y
            }));
        }
    """)
    
    print(f"\n발견된 언어 버튼: {len(lang_buttons)}개")
    for btn in lang_buttons:
        print(f"  - {btn['lang']}: visible={btn['visible']}, inHeader={btn['inHeader']}, pos=({btn['x']:.0f}, {btn['y']:.0f})")
    
    # Validation 탭으로 이동
    print("\n📊 Validation 탭으로 이동...")
    page.click("#tabValidation")
    time.sleep(2)
    
    # Validation 탭에서 언어 버튼 재확인
    lang_buttons_validation = page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('[data-lang]');
            return Array.from(buttons).map(btn => ({
                lang: btn.getAttribute('data-lang'),
                visible: btn.offsetParent !== null,
                x: btn.getBoundingClientRect().x,
                y: btn.getBoundingClientRect().y,
                width: btn.getBoundingClientRect().width,
                height: btn.getBoundingClientRect().height
            }));
        }
    """)
    
    print(f"\nValidation 탭에서 언어 버튼:")
    for btn in lang_buttons_validation:
        print(f"  - {btn['lang']}: visible={btn['visible']}, pos=({btn['x']:.0f}, {btn['y']:.0f}), size=({btn['width']:.0f}x{btn['height']:.0f})")
    
    # 영어 버튼 클릭 시도
    print("\n🖱️  영어 버튼 클릭 시도...")
    try:
        page.click('[data-lang="en"]', timeout=5000)
        time.sleep(2)
        
        new_lang = page.evaluate("() => window.currentLanguage || 'ko'")
        print(f"✅ 클릭 성공! 현재 언어: {new_lang}")
        
    except Exception as e:
        print(f"❌ 클릭 실패: {e}")
        
        # 수동으로 클릭 시도
        print("\n수동 클릭 시도...")
        clicked = page.evaluate("""
            () => {
                const btn = document.querySelector('[data-lang="en"]');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            }
        """)
        
        if clicked:
            time.sleep(2)
            new_lang = page.evaluate("() => window.currentLanguage || 'ko'")
            print(f"✅ 수동 클릭 성공! 현재 언어: {new_lang}")
        else:
            print("❌ 버튼을 찾을 수 없음")
    
    time.sleep(3)
    browser.close()

print("\n✅ 디버그 테스트 완료")
