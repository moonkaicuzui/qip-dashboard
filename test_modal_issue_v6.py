#!/usr/bin/env python3
"""
Version 6 대시보드 모달 문제 진단 및 수정 스크립트
"""

from playwright.sync_api import sync_playwright
import os

dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 콘솔 메시지 수집
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

    print("="*60)
    print("🔍 Version 6 대시보드 모달 문제 진단")
    print("="*60)

    # 대시보드 열기
    print(f"\n📂 대시보드 파일: {dashboard_path}")
    page.goto(f'file://{dashboard_path}')
    page.wait_for_timeout(2000)

    # JavaScript 에러 확인
    print("\n[1] JavaScript 에러 확인")
    print("-"*40)
    errors = [msg for msg in console_messages if "error" in msg.lower()]
    if errors:
        print("❌ JavaScript 에러 발견:")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ JavaScript 에러 없음")

    # 모달 HTML 구조 확인
    print("\n[2] 모달 HTML 구조 확인")
    print("-"*40)

    position_modal = page.query_selector('#positionModal')
    employee_modal = page.query_selector('#employeeModal')

    if position_modal:
        print("✅ #positionModal 존재")
    else:
        print("❌ #positionModal 없음")

    if employee_modal:
        print("✅ #employeeModal 존재")
    else:
        print("❌ #employeeModal 없음")

    # 함수 존재 확인
    print("\n[3] JavaScript 함수 확인")
    print("-"*40)

    has_show_position = page.evaluate('() => typeof showPositionDetail === "function"')
    has_show_employee = page.evaluate('() => typeof showEmployeeDetail === "function"')

    print(f"showPositionDetail 함수: {'✅ 존재' if has_show_position else '❌ 없음'}")
    print(f"showEmployeeDetail 함수: {'✅ 존재' if has_show_employee else '❌ 없음'}")

    # Position Details 탭 테스트
    print("\n[4] Position Details 탭 테스트")
    print("-"*40)

    position_tab = page.query_selector('[data-tab="position"]')
    if position_tab:
        position_tab.click()
        page.wait_for_timeout(1000)
        print("✅ Position Details 탭 클릭됨")

        # View 버튼 찾기
        view_buttons = page.query_selector_all('button.btn-outline-primary:has-text("View")')
        print(f"View 버튼 개수: {len(view_buttons)}")

        if view_buttons and len(view_buttons) > 0:
            print("첫 번째 View 버튼 클릭 시도...")

            # onclick 속성 확인
            onclick_attr = view_buttons[0].get_attribute('onclick')
            print(f"onclick 속성: {onclick_attr}")

            # 버튼 클릭
            view_buttons[0].click()
            page.wait_for_timeout(1000)

            # 모달 상태 확인
            modal_visible = page.is_visible('#positionModal')
            if modal_visible:
                print("✅ Position Details 모달이 열림!")

                # 모달 닫기
                close_btn = page.query_selector('#positionModal .btn-close')
                if close_btn:
                    close_btn.click()
                    print("   모달 닫기 성공")
            else:
                print("❌ 모달이 열리지 않음")

                # Bootstrap 모달 인스턴스 확인
                has_bootstrap = page.evaluate('() => typeof bootstrap !== "undefined"')
                print(f"   Bootstrap 라이브러리: {'✅ 로드됨' if has_bootstrap else '❌ 없음'}")

                if has_bootstrap:
                    # 수동으로 모달 열기 시도
                    print("\n   수동으로 모달 열기 시도...")
                    page.evaluate('''() => {
                        const modal = new bootstrap.Modal(document.getElementById('positionModal'));
                        modal.show();
                    }''')
                    page.wait_for_timeout(1000)

                    if page.is_visible('#positionModal'):
                        print("   ✅ 수동 열기 성공!")
                    else:
                        print("   ❌ 수동 열기도 실패")
        else:
            print("❌ View 버튼이 없음")
    else:
        print("❌ Position Details 탭을 찾을 수 없음")

    # Individual Details 탭 테스트
    print("\n[5] Individual Details 탭 테스트")
    print("-"*40)

    employees_tab = page.query_selector('[data-tab="employees"]')
    if employees_tab:
        employees_tab.click()
        page.wait_for_timeout(1000)
        print("✅ Individual Details 탭 클릭됨")

        # View 버튼 찾기
        view_buttons = page.query_selector_all('button.btn-primary:has-text("View")')
        print(f"View 버튼 개수: {len(view_buttons)}")

        if view_buttons and len(view_buttons) > 0:
            print("첫 번째 View 버튼 클릭 시도...")

            # onclick 속성 확인
            onclick_attr = view_buttons[0].get_attribute('onclick')
            print(f"onclick 속성: {onclick_attr}")

            # 버튼 클릭
            view_buttons[0].click()
            page.wait_for_timeout(1000)

            # 모달 상태 확인
            modal_visible = page.is_visible('#employeeModal')
            if modal_visible:
                print("✅ Employee Details 모달이 열림!")
            else:
                print("❌ 모달이 열리지 않음")

    # 최종 진단
    print("\n" + "="*60)
    print("🔬 진단 결과")
    print("="*60)

    if errors:
        print("❌ JavaScript 에러가 있음 - 이것이 원인일 수 있음")
    elif not has_bootstrap:
        print("❌ Bootstrap이 로드되지 않음 - 모달이 작동하지 않는 원인")
    elif not has_show_position or not has_show_employee:
        print("❌ 모달 함수가 정의되지 않음 - JavaScript 코드 문제")
    else:
        print("⚠️ 이벤트 바인딩 문제일 가능성이 높음")
        print("   - onclick 속성이 제대로 설정되지 않았거나")
        print("   - 함수 호출 시 매개변수 문제일 수 있음")

    print("\n💡 브라우저를 30초 동안 유지합니다. 수동으로 확인해보세요...")
    import time
    time.sleep(30)

    browser.close()