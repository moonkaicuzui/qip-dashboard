#!/usr/bin/env python3
"""
Modal 문제 종합 디버깅 스크립트
"""

from playwright.sync_api import sync_playwright
import os
import time

dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 콘솔 메시지 수집
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

    print("="*60)
    print("🔍 Dashboard Modal 종합 디버깅")
    print("="*60)

    # 대시보드 열기
    print(f"\n📂 대시보드 열기: {dashboard_path}")
    page.goto(f'file://{dashboard_path}')
    page.wait_for_timeout(3000)

    # 1. employeeData 확인
    print("\n[1] employeeData 로딩 확인")
    print("-"*40)

    has_employee_data = page.evaluate('''() => {
        console.log('Checking employeeData...');
        return typeof employeeData !== 'undefined' && employeeData.length > 0;
    }''')

    if has_employee_data:
        employee_count = page.evaluate('() => employeeData.length')
        print(f"✅ employeeData 로드됨: {employee_count}개 레코드")

        # 샘플 데이터 확인
        sample = page.evaluate('() => employeeData[0]')
        print(f"   샘플 데이터 키: {list(sample.keys())[:5]}...")
    else:
        print("❌ employeeData가 로드되지 않음")

    # 2. Position Details 탭 테스트
    print("\n[2] Position Details 탭 테스트")
    print("-"*40)

    position_tab = page.query_selector('[data-tab="position"]')
    if position_tab:
        position_tab.click()
        page.wait_for_timeout(2000)
        print("✅ Position Details 탭 클릭됨")

        # generatePositionTables 함수 호출 확인
        tables_generated = page.evaluate('''() => {
            console.log('Calling generatePositionTables...');
            if (typeof generatePositionTables === 'function') {
                generatePositionTables();
                return true;
            }
            return false;
        }''')

        if tables_generated:
            print("✅ generatePositionTables 함수 호출됨")

            # positionData 생성 확인
            position_data = page.evaluate('''() => {
                return window.positionData ? Object.keys(window.positionData).length : 0;
            }''')
            print(f"   positionData 생성됨: {position_data}개 항목")

            # 테이블 확인
            position_tables = page.query_selector_all('#positionTables table')
            print(f"   테이블 개수: {len(position_tables)}")

            # View 버튼 확인
            view_buttons = page.query_selector_all('#positionTables button.btn-outline-primary')
            print(f"   View 버튼 개수: {len(view_buttons)}")

            if view_buttons and len(view_buttons) > 0:
                print("\n   첫 번째 View 버튼 클릭 시도...")

                # onclick 속성 확인
                onclick = view_buttons[0].get_attribute('onclick')
                print(f"   onclick 속성: {onclick}")

                # 버튼 클릭
                view_buttons[0].click()
                page.wait_for_timeout(1500)

                # 모달 상태 확인
                modal_visible = page.is_visible('#positionModal')
                if modal_visible:
                    print("   ✅ Position 모달이 열림!")

                    # 모달 닫기
                    close_btn = page.query_selector('#positionModal .btn-close')
                    if close_btn:
                        close_btn.click()
                        print("   모달 닫기 완료")
                else:
                    print("   ❌ 모달이 열리지 않음")

                    # showPositionDetail 함수 직접 호출 테스트
                    print("\n   showPositionDetail 함수 직접 호출...")
                    result = page.evaluate('''() => {
                        if (typeof showPositionDetail === 'function') {
                            // positionData에서 첫 번째 항목 가져오기
                            const keys = Object.keys(window.positionData);
                            if (keys.length > 0) {
                                const firstItem = window.positionData[keys[0]];
                                console.log('Calling showPositionDetail with:', firstItem.type, firstItem.position);
                                showPositionDetail(firstItem.type, firstItem.position);
                                return true;
                            }
                        }
                        return false;
                    }''')

                    if result:
                        page.wait_for_timeout(1500)
                        if page.is_visible('#positionModal'):
                            print("   ✅ 직접 호출로 모달이 열림!")
                        else:
                            print("   ❌ 직접 호출에도 모달이 안 열림")
        else:
            print("❌ generatePositionTables 함수를 찾을 수 없음")
    else:
        print("❌ Position Details 탭을 찾을 수 없음")

    # 3. Individual Details 탭 테스트
    print("\n[3] Individual Details 탭 테스트")
    print("-"*40)

    employee_tab = page.query_selector('[data-tab="employees"]')
    if employee_tab:
        employee_tab.click()
        page.wait_for_timeout(2000)
        print("✅ Individual Details 탭 클릭됨")

        # View 버튼 확인
        view_buttons = page.query_selector_all('#employeeTableContainer button.btn-primary')
        print(f"View 버튼 개수: {len(view_buttons)}")

        if view_buttons and len(view_buttons) > 0:
            print("\n첫 번째 View 버튼 클릭 시도...")
            view_buttons[0].click()
            page.wait_for_timeout(1500)

            # 모달 상태 확인
            modal_visible = page.is_visible('#employeeModal')
            if modal_visible:
                print("✅ Employee 모달이 열림!")
            else:
                print("❌ 모달이 열리지 않음")

    # 4. JavaScript 에러 확인
    print("\n[4] JavaScript 에러 확인")
    print("-"*40)
    errors = [msg for msg in console_messages if "error" in msg.lower()]
    if errors:
        print("❌ JavaScript 에러 발견:")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ JavaScript 에러 없음")

    # 5. 문제 진단
    print("\n[5] 문제 진단 결과")
    print("-"*40)

    if not has_employee_data:
        print("❌ 주요 문제: employeeData가 로드되지 않음")
        print("   → Base64 디코딩 또는 데이터 로딩 문제")
    elif position_data == 0:
        print("❌ 주요 문제: positionData가 생성되지 않음")
        print("   → generatePositionTables 함수 실행 문제")
    elif len(view_buttons) == 0:
        print("❌ 주요 문제: View 버튼이 생성되지 않음")
        print("   → 테이블 렌더링 또는 데이터 필터링 문제")
    else:
        print("⚠️ 이벤트 바인딩 또는 모달 초기화 문제일 가능성")

    print("\n💡 브라우저를 30초 동안 유지합니다. 수동으로 확인해보세요...")
    time.sleep(30)

    browser.close()