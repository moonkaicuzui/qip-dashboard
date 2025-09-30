#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TYPE-2 계산 방법 섹션 번역 확인
"""
import asyncio
import http.server
import socketserver
import threading
import time

async def test_translation():
    from playwright.async_api import async_playwright

    # HTTP 서버 시작
    PORT = 8766
    Handler = http.server.SimpleHTTPRequestHandler

    class QuietHTTPRequestHandler(Handler):
        def log_message(self, format, *args):
            pass

    def start_server():
        with socketserver.TCPServer(("", PORT), QuietHTTPRequestHandler) as httpd:
            httpd.serve_forever()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    print('=' * 80)
    print('TYPE-2 계산 방법 섹션 번역 확인')
    print('=' * 80)

    url = f'http://localhost:{PORT}/output_files/Incentive_Dashboard_2025_09_Version_6.html'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # 에러 및 콘솔 메시지 수집
        errors = []
        console_messages = []
        page.on('pageerror', lambda exc: errors.append(str(exc)))
        page.on('console', lambda msg: console_messages.append(f'[{msg.type}] {msg.text}'))

        print(f'\n📡 대시보드 로드 중...')
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        print('✅ 페이지 로드 완료')

        # 인센티브 기준 탭 클릭
        print('\n🔍 인센티브 기준 탭으로 이동')
        criteria_tab = await page.query_selector('[data-tab="criteria"]')
        if criteria_tab:
            await criteria_tab.click()
            await page.wait_for_timeout(1000)
            print('   ✅ 인센티브 기준 탭 클릭 완료')
        else:
            print('   ❌ 인센티브 기준 탭을 찾을 수 없음')
            await browser.close()
            return

        # TYPE-2 섹션 확인
        print('\n📊 TYPE-2 계산 방법 섹션 확인')

        # 제목
        title = await page.query_selector('#type2CalculationTitle')
        if title:
            title_text = await title.inner_text()
            print(f'   제목: {title_text}')
            if 'criteria.' in title_text or 'type2Calculation' in title_text:
                print('   ❌ 번역 키가 그대로 표시됨!')
            else:
                print('   ✅ 번역 정상')
        else:
            print('   ❌ type2CalculationTitle을 찾을 수 없음')

        # 원칙 레이블
        principle_label = await page.query_selector('#type2PrincipleLabel')
        if principle_label:
            label_text = await principle_label.inner_text()
            print(f'   원칙 레이블: {label_text}')
            if 'criteria.' in label_text or 'principleLabel' in label_text:
                print('   ❌ 번역 키가 그대로 표시됨!')
            else:
                print('   ✅ 번역 정상')

        # 원칙 텍스트
        principle_text = await page.query_selector('#type2PrincipleText')
        if principle_text:
            text = await principle_text.inner_text()
            print(f'   원칙 텍스트: {text}')
            if 'criteria.' in text or 'principleText' in text:
                print('   ❌ 번역 키가 그대로 표시됨!')
            else:
                print('   ✅ 번역 정상')

        # 테이블 헤더
        print('\n📋 테이블 헤더 확인')
        headers = {
            '.type2-calc-header-position': '직급',
            '.type2-calc-header-reference': '참고 기준',
            '.type2-calc-header-method': '계산 방법',
            '.type2-calc-header-average': '평균'
        }

        for selector, expected_ko in headers.items():
            header = await page.query_selector(selector)
            if header:
                header_text = await header.inner_text()
                print(f'   {expected_ko}: {header_text}')
                if 'criteria.' in header_text or 'tableHeaders' in header_text:
                    print(f'   ❌ 번역 키가 그대로 표시됨!')
                else:
                    print(f'   ✅ 번역 정상')
            else:
                print(f'   ⚠️ {selector} 를 찾을 수 없음')

        # 언어 전환 테스트
        print('\n🌐 언어 전환 테스트')

        # 영어로 전환
        en_btn = await page.query_selector('[data-lang="en"]')
        if en_btn:
            await en_btn.click()
            await page.wait_for_timeout(1000)

            title = await page.query_selector('#type2CalculationTitle')
            if title:
                title_text_en = await title.inner_text()
                print(f'   영어 제목: {title_text_en}')
                if 'TYPE-2 All Position' in title_text_en:
                    print('   ✅ 영어 번역 정상')
                elif 'criteria.' in title_text_en:
                    print('   ❌ 번역 키가 표시됨')
                else:
                    print('   ⚠️ 예상과 다른 텍스트')

        # 베트남어로 전환
        vi_btn = await page.query_selector('[data-lang="vi"]')
        if vi_btn:
            await vi_btn.click()
            await page.wait_for_timeout(1000)

            title = await page.query_selector('#type2CalculationTitle')
            if title:
                title_text_vi = await title.inner_text()
                print(f'   베트남어 제목: {title_text_vi}')
                if 'TYPE-2' in title_text_vi and 'Phương pháp' in title_text_vi:
                    print('   ✅ 베트남어 번역 정상')
                elif 'criteria.' in title_text_vi:
                    print('   ❌ 번역 키가 표시됨')
                else:
                    print('   ⚠️ 예상과 다른 텍스트')

        # 한국어로 복귀
        ko_btn = await page.query_selector('[data-lang="ko"]')
        if ko_btn:
            await ko_btn.click()
            await page.wait_for_timeout(500)

        # Console warnings 확인
        print('\n⚠️  Console Warnings:')
        warnings = [msg for msg in console_messages if 'warn' in msg or 'Translation' in msg]
        if warnings:
            for warn in warnings[-20:]:  # 마지막 20개만
                print(f'   {warn}')
        else:
            print('   ✅ 경고 없음')

        # JavaScript 에러 확인
        print('\n🚨 JavaScript 에러:')
        if errors:
            for error in errors:
                print(f'   ❌ {error}')
        else:
            print('   ✅ 에러 없음')

        # 스크린샷
        await page.screenshot(path='output_files/type2_translation_test.png')
        print('\n📸 스크린샷 저장: output_files/type2_translation_test.png')

        await browser.close()

    print('\n' + '=' * 80)
    print('테스트 완료')
    print('=' * 80)

if __name__ == '__main__':
    asyncio.run(test_translation())