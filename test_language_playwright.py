#!/usr/bin/env python3
"""
Playwright를 사용한 자동 언어 전환 테스트
"""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

async def test_language_comprehensive():
    """모든 탭과 모달에서 언어 전환 테스트"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # HTML 파일 열기
        html_path = Path("output_files/Incentive_Dashboard_2025_09_Version_5.html").absolute()
        await page.goto(f"file://{html_path}")
        await page.wait_for_timeout(2000)

        print("=" * 60)
        print("🌐 Playwright 언어 전환 테스트")
        print("=" * 60)

        # 각 언어별 테스트
        for lang in ["ko", "en", "vi"]:
            print(f"\n📋 {lang} 언어 테스트")

            # 언어 변경
            await page.evaluate(f"changeLanguage('{lang}')")
            await page.wait_for_timeout(500)

            # 현재 언어 확인
            current_lang = await page.evaluate("currentLanguage")
            print(f"  현재 언어: {current_lang}")

            # 각 탭 확인
            tabs = await page.query_selector_all(".nav-link")
            for tab in tabs:
                text = await tab.text_content()
                print(f"  탭: {text.strip()}")

            # Type별 요약 테이블 확인
            tbody = await page.query_selector("#typeSummaryBody")
            if tbody:
                rows = await tbody.query_selector_all("tr")
                print(f"  Type별 요약 행 수: {len(rows)}")

            # System Validation 탭으로 이동
            await page.evaluate("showTab('validation')")
            await page.wait_for_timeout(500)

            # KPI 카드 확인
            kpi_cards = await page.query_selector_all(".kpi-card h5")
            for card in kpi_cards:
                text = await card.text_content()
                print(f"  KPI 카드: {text.strip()}")

            # 모달 버튼 확인
            modal_buttons = await page.query_selector_all("[data-bs-toggle='modal']")
            print(f"  모달 버튼 수: {len(modal_buttons)}")

            # 첫 번째 모달 테스트
            if modal_buttons:
                await modal_buttons[0].click()
                await page.wait_for_timeout(500)

                # 모달 제목 확인
                modal_title = await page.query_selector(".modal-title")
                if modal_title:
                    title_text = await modal_title.text_content()
                    print(f"  모달 제목: {title_text.strip()}")

                # 모달 닫기
                close_btn = await page.query_selector(".modal .btn-close")
                if close_btn:
                    await close_btn.click()
                await page.wait_for_timeout(500)

        # 스크린샷 저장
        await page.screenshot(path="language_test_result.png")
        print("\n✅ 스크린샷 저장: language_test_result.png")

        await browser.close()
        print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_language_comprehensive())
