#!/usr/bin/env python3
"""
모달 작동 검증 및 수정 스크립트
"""

from playwright.sync_api import sync_playwright
import os
import time

dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("="*60)
    print("🔍 Position/Individual Details 모달 테스트 (수정판)")
    print("="*60)

    # 대시보드 열기
    page.goto(f'file://{dashboard_path}')
    page.wait_for_timeout(3000)

    # 1. Position Details 탭 테스트
    print("\n[1] Position Details 탭 테스트")
    print("-"*40)

    position_tab = page.query_selector('[data-tab="position"]')
    if position_tab:
        position_tab.click()
        page.wait_for_timeout(2000)
        print("✅ Position Details 탭 클릭됨")

        # 테이블이 생성될 때까지 잠시 대기
        page.wait_for_timeout(1000)

        # btn-outline-primary 버튼 찾기
        view_buttons = page.query_selector_all('button.btn-outline-primary')
        print(f"View 버튼 개수: {len(view_buttons)}")

        if view_buttons and len(view_buttons) > 0:
            # 첫 번째 View 버튼 클릭
            print("첫 번째 View 버튼 클릭 시도...")
            view_buttons[0].click()
            page.wait_for_timeout(1500)

            # 모달이 열렸는지 확인
            modal = page.query_selector('#positionModal')
            if modal:
                is_visible = modal.is_visible()
                print(f"모달 visibility: {is_visible}")

                # Bootstrap modal의 show 클래스 확인
                modal_dialog = page.query_selector('#positionModal .modal-dialog')
                if modal_dialog:
                    print("✅ Position Details 모달이 정상적으로 열림!")

                    # 모달 내용 확인
                    modal_title = page.query_selector('#positionModalLabel')
                    if modal_title:
                        title_text = modal_title.inner_text()
                        print(f"   모달 제목: {title_text}")

                    # 모달 닫기
                    close_button = page.query_selector('#positionModal .btn-close')
                    if close_button:
                        close_button.click()
                        page.wait_for_timeout(500)
                        print("   모달 닫기 성공")
                else:
                    print("❌ 모달 대화상자가 표시되지 않음")
            else:
                print("❌ #positionModal을 찾을 수 없음")
        else:
            print("❌ View 버튼이 없음 - 테이블이 비어있을 수 있음")

    # 2. Individual Details 탭 테스트
    print("\n[2] Individual Details 탭 테스트")
    print("-"*40)

    individual_tab = page.query_selector('[data-tab="employees"]')
    if individual_tab:
        individual_tab.click()
        page.wait_for_timeout(2000)
        print("✅ Individual Details 탭 클릭됨")

        # View 버튼 찾기 (btn-primary 클래스)
        view_buttons = page.query_selector_all('button.btn-primary')
        print(f"View 버튼 개수: {len(view_buttons)}")

        if view_buttons and len(view_buttons) > 0:
            print("첫 번째 View 버튼 클릭 시도...")
            view_buttons[0].click()
            page.wait_for_timeout(1500)

            # 모달이 열렸는지 확인
            modal = page.query_selector('#employeeModal')
            if modal:
                modal_dialog = page.query_selector('#employeeModal .modal-dialog')
                if modal_dialog:
                    print("✅ Employee Details 모달이 정상적으로 열림!")

                    # 모달 내용 확인
                    modal_title = page.query_selector('#employeeModalLabel')
                    if modal_title:
                        title_text = modal_title.inner_text()
                        print(f"   모달 제목: {title_text}")

                    # 모달 닫기
                    close_button = page.query_selector('#employeeModal .btn-close')
                    if close_button:
                        close_button.click()
                        page.wait_for_timeout(500)
                        print("   모달 닫기 성공")
                else:
                    print("❌ 모달 대화상자가 표시되지 않음")
            else:
                print("❌ #employeeModal을 찾을 수 없음")
        else:
            print("❌ View 버튼이 없음")

    # 3. showPositionDetail 함수 확인
    print("\n[3] JavaScript 함수 존재 확인")
    print("-"*40)

    has_show_position = page.evaluate('() => typeof showPositionDetail === "function"')
    print(f"showPositionDetail 함수 존재: {has_show_position}")

    has_show_employee = page.evaluate('() => typeof showEmployeeDetail === "function"')
    print(f"showEmployeeDetail 함수 존재: {has_show_employee}")

    # 4. 직접 함수 호출 테스트
    if has_show_position:
        print("\n[4] 직접 함수 호출 테스트")
        print("-"*40)

        # Position Details 탭으로 이동
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(1000)

        # TYPE-1 데이터가 있는지 확인
        has_type1_data = page.evaluate('() => window.positionData && window.positionData["TYPE-1"] && window.positionData["TYPE-1"].length > 0')

        if has_type1_data:
            first_position = page.evaluate('() => window.positionData["TYPE-1"][0].position')
            print(f"TYPE-1 첫 번째 직급: {first_position}")

            # 직접 함수 호출
            print("showPositionDetail 함수 직접 호출...")
            page.evaluate(f'showPositionDetail("TYPE-1", "{first_position}")')
            page.wait_for_timeout(1500)

            # 모달 확인
            modal_visible = page.query_selector('#positionModal .modal-dialog')
            if modal_visible:
                print("✅ 직접 호출로 모달이 정상 작동함!")

                # 모달 닫기
                page.evaluate('() => { const modal = bootstrap.Modal.getInstance(document.getElementById("positionModal")); if(modal) modal.hide(); }')
            else:
                print("❌ 직접 호출에도 모달이 열리지 않음")
        else:
            print("TYPE-1 데이터가 없음")

    print("\n" + "="*60)
    print("🎯 테스트 완료")
    print("="*60)

    # 브라우저 유지 (수동 확인용)
    print("\n브라우저를 30초 동안 유지합니다. 수동으로 확인해보세요...")
    time.sleep(30)

    browser.close()