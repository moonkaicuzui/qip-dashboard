#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright를 사용한 모달 동작 테스트
"""
import asyncio
import http.server
import socketserver
import threading
import time
from pathlib import Path

async def test_modal():
    from playwright.async_api import async_playwright

    # HTTP 서버 시작 (백그라운드)
    PORT = 8765
    Handler = http.server.SimpleHTTPRequestHandler

    class QuietHTTPRequestHandler(Handler):
        def log_message(self, format, *args):
            pass  # 로그 출력 억제

    def start_server():
        with socketserver.TCPServer(("", PORT), QuietHTTPRequestHandler) as httpd:
            httpd.serve_forever()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # 서버 시작 대기

    print('=' * 80)
    print('Playwright 모달 동작 테스트')
    print('=' * 80)

    url = f'http://localhost:{PORT}/output_files/Incentive_Dashboard_2025_09_Version_6.html'

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # 콘솔 메시지 수집
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f'[{msg.type}] {msg.text}'))

        # 에러 수집
        errors = []
        page.on('pageerror', lambda exc: errors.append(str(exc)))

        print(f'\n📡 대시보드 로드 중: {url}')
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)  # JavaScript 실행 대기

        print('✅ 페이지 로드 완료')

        # 1. 개인별 상세 탭으로 이동
        print('\n🔍 Step 1: 개인별 상세 탭 클릭')
        detail_tab = await page.query_selector('[data-tab="detail"]')
        if detail_tab:
            await detail_tab.click()
            await page.wait_for_timeout(500)
            print('   ✅ 개인별 상세 탭 클릭 완료')
        else:
            print('   ❌ 개인별 상세 탭을 찾을 수 없음')
            await browser.close()
            return

        # 2. 테이블이 생성되었는지 확인
        print('\n🔍 Step 2: 테이블 확인')
        tbody = await page.query_selector('#employeeTableBody')
        if tbody:
            rows = await tbody.query_selector_all('tr')
            print(f'   ✅ 테이블 발견: {len(rows)}개 행')

            if len(rows) == 0:
                print('   ❌ 테이블에 데이터가 없음!')
                await browser.close()
                return
        else:
            print('   ❌ employeeTableBody를 찾을 수 없음')
            await browser.close()
            return

        # 3. 첫 번째 행의 상세 보기 버튼 찾기
        print('\n🔍 Step 3: 상세 보기 버튼 찾기')

        # 버튼이 있는지 확인
        detail_button = await page.query_selector('#employeeTableBody tr:first-child button')
        if detail_button:
            button_text = await detail_button.inner_text()
            print(f'   ✅ 상세 보기 버튼 발견: "{button_text}"')

            # onclick 속성 확인
            onclick = await detail_button.get_attribute('onclick')
            print(f'   📋 onclick 속성: {onclick[:100] if onclick else "None"}...')
        else:
            print('   ❌ 상세 보기 버튼을 찾을 수 없음')
            await browser.close()
            return

        # 4. 모달이 이미 존재하는지 확인
        print('\n🔍 Step 4: 모달 DOM 요소 확인')
        modal = await page.query_selector('#employeeModal')
        if modal:
            is_visible = await modal.is_visible()
            print(f'   ✅ employeeModal 존재 (보이는 상태: {is_visible})')
        else:
            print('   ❌ employeeModal이 DOM에 없음!')

        # 5. 버튼 클릭
        print('\n🔍 Step 5: 상세 보기 버튼 클릭')
        try:
            await detail_button.click()
            await page.wait_for_timeout(1000)  # 모달 애니메이션 대기
            print('   ✅ 버튼 클릭 완료')
        except Exception as e:
            print(f'   ❌ 버튼 클릭 실패: {str(e)}')

        # 6. 모달이 열렸는지 확인
        print('\n🔍 Step 6: 모달 열림 확인')
        modal = await page.query_selector('#employeeModal')
        if modal:
            is_visible = await modal.is_visible()
            display = await modal.evaluate('el => window.getComputedStyle(el).display')
            has_show_class = await modal.evaluate('el => el.classList.contains("show")')

            print(f'   모달 보이는 상태: {is_visible}')
            print(f'   CSS display: {display}')
            print(f'   .show 클래스: {has_show_class}')

            if is_visible:
                print('   ✅ 모달이 정상적으로 열렸습니다!')
            else:
                print('   ❌ 모달이 열리지 않았습니다!')
        else:
            print('   ❌ 모달 요소를 찾을 수 없음')

        # 7. 콘솔 메시지 출력
        print('\n📊 브라우저 콘솔 메시지:')
        if console_messages:
            for msg in console_messages[-20:]:  # 마지막 20개만
                print(f'   {msg}')
        else:
            print('   (콘솔 메시지 없음)')

        # 8. 에러 메시지 출력
        print('\n🚨 JavaScript 에러:')
        if errors:
            for error in errors:
                print(f'   ❌ {error}')
        else:
            print('   ✅ 에러 없음')

        # 9. showEmployeeDetail 함수가 정의되어 있는지 확인
        print('\n🔍 Step 7: showEmployeeDetail 함수 확인')
        func_exists = await page.evaluate('typeof showEmployeeDetail === "function"')
        print(f'   showEmployeeDetail 함수 존재: {func_exists}')

        if func_exists:
            # 함수를 직접 호출해보기
            print('\n🧪 직접 함수 호출 테스트:')
            try:
                # employeeData에서 첫 번째 직원 ID 가져오기
                first_emp_no = await page.evaluate('''
                    () => {
                        if (typeof employeeData !== 'undefined' && employeeData.length > 0) {
                            const emp = employeeData[0];
                            return emp.emp_no || emp['Employee No'] || emp['emp_no'];
                        }
                        return null;
                    }
                ''')

                if first_emp_no:
                    print(f'   테스트 ID: {first_emp_no}')
                    await page.evaluate(f'showEmployeeDetail("{first_emp_no}")')
                    await page.wait_for_timeout(1000)

                    # 모달 확인
                    modal = await page.query_selector('#employeeModal')
                    is_visible = await modal.is_visible()
                    print(f'   직접 호출 후 모달 보이는 상태: {is_visible}')
                else:
                    print('   ❌ employeeData에서 직원 ID를 가져올 수 없음')
            except Exception as e:
                print(f'   ❌ 직접 호출 실패: {str(e)}')

        # 스크린샷 저장
        await page.screenshot(path='output_files/modal_test_screenshot.png')
        print('\n📸 스크린샷 저장: output_files/modal_test_screenshot.png')

        await browser.close()

    print('\n' + '=' * 80)
    print('테스트 완료')
    print('=' * 80)

if __name__ == '__main__':
    asyncio.run(test_modal())