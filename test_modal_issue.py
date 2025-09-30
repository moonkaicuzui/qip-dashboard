#!/usr/bin/env python3
"""
모달 작동 검증 스크립트
"""

from playwright.sync_api import sync_playwright
import os
import time

dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("="*60)
    print("🔍 Position/Individual Details 모달 테스트")
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
        page.wait_for_timeout(1000)
        print("✅ Position Details 탭 클릭됨")

        # TYPE-1 행 찾기
        type1_rows = page.query_selector_all('tr:has-text("TYPE-1")')
        print(f"TYPE-1 행 개수: {len(type1_rows)}")

        if type1_rows and len(type1_rows) > 0:
            # 첫 번째 TYPE-1 행의 View 버튼 클릭
            view_button = type1_rows[0].query_selector('button:has-text("View")')
            if view_button:
                print("View 버튼 클릭 시도...")
                view_button.click()
                page.wait_for_timeout(1000)

                # 모달이 열렸는지 확인
                modal = page.query_selector('#positionModal')
                if modal:
                    is_visible = modal.is_visible()
                    print(f"모달 visibility: {is_visible}")

                    if is_visible:
                        print("✅ Position Details 모달이 정상적으로 열림!")
                        # 모달 닫기
                        close_button = modal.query_selector('.btn-close')
                        if close_button:
                            close_button.click()
                    else:
                        print("❌ 모달이 존재하지만 보이지 않음")
                        # display:none 확인
                        style = page.evaluate('() => document.querySelector("#positionModal").style.display')
                        print(f"   모달 display style: {style}")
                else:
                    print("❌ #positionModal을 찾을 수 없음")
            else:
                print("❌ View 버튼을 찾을 수 없음")
        else:
            print("❌ TYPE-1 행이 없음")

    # 2. Individual Details 탭 테스트
    print("\n[2] Individual Details 탭 테스트")
    print("-"*40)

    individual_tab = page.query_selector('[data-tab="employees"]')
    if individual_tab:
        individual_tab.click()
        page.wait_for_timeout(1000)
        print("✅ Individual Details 탭 클릭됨")

        # 첫 번째 직원 행 찾기
        employee_rows = page.query_selector_all('#employeeTable tbody tr')
        print(f"직원 행 개수: {len(employee_rows)}")

        if employee_rows and len(employee_rows) > 0:
            # 첫 번째 직원의 View 버튼 클릭
            view_button = employee_rows[0].query_selector('button:has-text("View")')
            if view_button:
                print("View 버튼 클릭 시도...")
                view_button.click()
                page.wait_for_timeout(1000)

                # 모달이 열렸는지 확인
                modal = page.query_selector('#employeeModal')
                if modal:
                    is_visible = modal.is_visible()
                    print(f"모달 visibility: {is_visible}")

                    if is_visible:
                        print("✅ Employee Details 모달이 정상적으로 열림!")
                    else:
                        print("❌ 모달이 존재하지만 보이지 않음")
                        # display:none 확인
                        style = page.evaluate('() => document.querySelector("#employeeModal").style.display')
                        print(f"   모달 display style: {style}")
                else:
                    print("❌ #employeeModal을 찾을 수 없음")
            else:
                print("❌ View 버튼을 찾을 수 없음")
        else:
            print("❌ 직원 행이 없음")

    # 3. JavaScript 에러 확인
    print("\n[3] JavaScript 콘솔 에러 확인")
    print("-"*40)

    # 콘솔 메시지 수집
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

    # 페이지 리로드하여 에러 수집
    page.reload()
    page.wait_for_timeout(2000)

    errors = [msg for msg in console_messages if "error" in msg.lower()]
    if errors:
        print("❌ JavaScript 에러 발견:")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ JavaScript 에러 없음")

    # 4. positionData 전역 변수 확인
    print("\n[4] 전역 변수 확인")
    print("-"*40)

    has_position_data = page.evaluate('() => typeof window.positionData !== "undefined"')
    print(f"window.positionData 존재: {has_position_data}")

    if has_position_data:
        data_length = page.evaluate('() => Object.keys(window.positionData).length')
        print(f"positionData 항목 개수: {data_length}")

    has_employee_data = page.evaluate('() => typeof window.employeeData !== "undefined"')
    print(f"window.employeeData 존재: {has_employee_data}")

    if has_employee_data:
        data_length = page.evaluate('() => Object.keys(window.employeeData).length')
        print(f"employeeData 항목 개수: {data_length}")

    print("\n" + "="*60)
    print("🎯 테스트 완료")
    print("="*60)

    # 브라우저 유지 (수동 확인용)
    print("\n브라우저를 30초 동안 유지합니다. 수동으로 확인해보세요...")
    time.sleep(30)

    browser.close()