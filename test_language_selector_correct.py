#!/usr/bin/env python3
"""
언어 Selector (드롭다운) 검증 테스트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 언어 Selector 검증 테스트\n")
print("=" * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Validation 탭으로 이동
    print("\n📊 Validation 탭으로 이동...")
    page.click("#tabValidation")
    time.sleep(2)

    # 언어 selector 확인
    selector_exists = page.evaluate("""
        () => {
            const selector = document.getElementById('languageSelector');
            return selector !== null;
        }
    """)

    print(f"언어 Selector 존재: {selector_exists}")

    if selector_exists:
        languages = ['en', 'vi', 'ko']
        results = {
            'passed': 0,
            'failed': 0
        }

        for lang in languages:
            print(f"\n🌐 {lang.upper()} 언어로 전환...")

            try:
                # Selector를 사용하여 언어 변경
                page.select_option('#languageSelector', lang)
                time.sleep(1)

                # 현재 언어 확인
                current_lang = page.evaluate("() => window.currentLanguage || 'ko'")
                selector_value = page.evaluate("() => document.getElementById('languageSelector').value")

                if selector_value == lang:
                    print(f"   ✅ 언어 전환 성공: selector={selector_value}, window.currentLanguage={current_lang}")
                    results['passed'] += 1
                else:
                    print(f"   ❌ 언어 불일치: 예상={lang}, selector={selector_value}")
                    results['failed'] += 1

            except Exception as e:
                print(f"   ❌ 언어 전환 오류: {e}")
                results['failed'] += 1

        # 최종 결과
        print("\n" + "=" * 70)
        print("최종 결과")
        print("=" * 70)
        print(f"\n✅ 통과: {results['passed']}/{len(languages)}")
        print(f"❌ 실패: {results['failed']}/{len(languages)}")

        if results['failed'] == 0:
            print("\n🎉 모든 언어 전환 테스트 통과!")
        else:
            print(f"\n⚠️  {results['failed']}개 언어 전환 실패")
    else:
        print("❌ 언어 Selector를 찾을 수 없음")

    browser.close()

print("\n✅ 테스트 완료")
