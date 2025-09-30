#!/usr/bin/env python3
"""
완전한 모달 수정 검증 스크립트
ĐINH KIM NGOAN 및 TYPE-2 직원들의 모달이 올바르게 표시되는지 확인
"""

from playwright.sync_api import sync_playwright
import os
import time
import json

def verify_modal_fixes():
    """Position Details와 Individual Details 모달 수정사항 검증"""

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False, slow_mo=500)  # 천천히 실행하여 확인 가능
        page = browser.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        print("="*80)
        print("🎯 모달 수정사항 완전 검증 - ĐINH KIM NGOAN (TYPE-2)")
        print("="*80)

        verification_results = {
            "position_details_modal": False,
            "individual_details_modal": False,
            "đinh_kim_ngoan_verified": False,
            "condition_data_shown": False
        }

        # 1. Position Details 탭에서 GROUP LEADER TYPE-2 확인
        print("\n📌 STEP 1: Position Details 탭에서 GROUP LEADER (TYPE-2) 확인")
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(2000)
            print("✅ Position Details 탭으로 이동")

            # GROUP LEADER TYPE-2 찾기
            rows = page.query_selector_all('#positionTable tbody tr')
            group_leader_found = False

            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 4:
                    position = cells[0].inner_text()
                    emp_type = cells[1].inner_text()

                    if 'GROUP LEADER' in position and 'TYPE-2' in emp_type:
                        group_leader_found = True
                        employee_count = cells[2].inner_text()
                        print(f"✅ GROUP LEADER (TYPE-2) 발견: {employee_count}명")

                        # View 버튼 클릭
                        view_btn = cells[3].query_selector('button')
                        if view_btn:
                            view_btn.click()
                            page.wait_for_timeout(2000)

                            # 모달이 열렸는지 확인
                            modal = page.query_selector('#employeeModal.show')
                            if modal:
                                print("✅ Position Details 모달 열림")

                                # Condition Fulfillment by Category 테이블 확인
                                condition_table = page.query_selector('.condition-fulfillment-table tbody')
                                if condition_table:
                                    condition_rows = condition_table.query_selector_all('tr')

                                    if len(condition_rows) > 0:
                                        print(f"✅ Condition Fulfillment 테이블: {len(condition_rows)}개 조건 표시됨")
                                        verification_results["condition_data_shown"] = True

                                        # 각 조건의 데이터 출력
                                        for i, row in enumerate(condition_rows):
                                            cells = row.query_selector_all('td')
                                            if len(cells) >= 4:
                                                condition_name = cells[1].inner_text()
                                                total_count = cells[2].inner_text()
                                                met_count = cells[3].inner_text()
                                                print(f"  • 조건 {i+1}: {condition_name}")
                                                print(f"    - Total: {total_count}, Met: {met_count}")

                                                # 데이터가 0이 아닌지 확인
                                                if total_count != "0" or met_count != "0":
                                                    verification_results["position_details_modal"] = True
                                    else:
                                        print("❌ Condition Fulfillment 테이블이 비어있음")

                                # Employee Details에서 ĐINH KIM NGOAN 찾기
                                print("\n📌 ĐINH KIM NGOAN 찾기:")
                                employee_rows = page.query_selector_all('#positionEmployeeTable tbody tr')

                                for emp_row in employee_rows:
                                    cells = emp_row.query_selector_all('td')
                                    if len(cells) >= 5:
                                        emp_name = cells[1].inner_text()

                                        if 'ĐINH KIM NGOAN' in emp_name:
                                            amount = cells[2].inner_text()
                                            status = cells[3].inner_text()

                                            print(f"✅ ĐINH KIM NGOAN 발견!")
                                            print(f"  - 이름: {emp_name}")
                                            print(f"  - 인센티브: {amount}")
                                            print(f"  - 상태: {status}")

                                            # 325,312 VND 확인
                                            if '325,312' in amount or '325312' in amount.replace(',', ''):
                                                print(f"  ✅ 올바른 인센티브 금액: 325,312 VND")
                                                verification_results["đinh_kim_ngoan_verified"] = True

                                            # Condition Fulfillment 배지 확인
                                            badges = cells[4].query_selector_all('.badge')
                                            if len(badges) > 0:
                                                print(f"  - 조건 배지: {len(badges)}개")
                                                for badge in badges:
                                                    print(f"    • {badge.inner_text()}")
                                            break

                                # 모달 닫기
                                close_btn = page.query_selector('.modal .btn-close')
                                if close_btn:
                                    close_btn.click()
                                    page.wait_for_timeout(1000)
                        break

        # 2. Individual Details 탭에서 ĐINH KIM NGOAN 검색
        print("\n" + "="*80)
        print("📌 STEP 2: Individual Details 탭에서 ĐINH KIM NGOAN 직접 검색")
        print("="*80)

        individual_tab = page.query_selector('[data-tab="individual"]')
        if individual_tab:
            individual_tab.click()
            page.wait_for_timeout(2000)
            print("✅ Individual Details 탭으로 이동")

            # 검색창에 ĐINH KIM NGOAN 입력
            search_input = page.query_selector('#employeeSearch')
            if search_input:
                search_input.fill("ĐINH KIM NGOAN")
                page.wait_for_timeout(1000)
                print("✅ 'ĐINH KIM NGOAN' 검색")

                # 검색 결과 확인
                table_rows = page.query_selector_all('#employeeTable tbody tr')
                for row in table_rows:
                    if row.is_visible():
                        cells = row.query_selector_all('td')
                        if len(cells) >= 6:
                            emp_name = cells[1].inner_text()

                            if 'ĐINH KIM NGOAN' in emp_name:
                                position = cells[2].inner_text()
                                emp_type = cells[3].inner_text()
                                amount = cells[4].inner_text()

                                print(f"✅ ĐINH KIM NGOAN 검색 결과:")
                                print(f"  - 이름: {emp_name}")
                                print(f"  - 직급: {position}")
                                print(f"  - 타입: {emp_type}")
                                print(f"  - 인센티브: {amount}")

                                # View 버튼 클릭
                                view_btn = cells[5].query_selector('button')
                                if view_btn:
                                    view_btn.click()
                                    page.wait_for_timeout(2000)

                                    # Individual Details 모달 확인
                                    modal = page.query_selector('#individualModal.show')
                                    if modal:
                                        print("✅ Individual Details 모달 열림")

                                        # Condition Status 확인
                                        condition_list = page.query_selector('#individualConditionList')
                                        if condition_list:
                                            condition_items = condition_list.query_selector_all('li')

                                            if len(condition_items) > 0:
                                                print(f"✅ Condition Status: {len(condition_items)}개 조건 표시됨")
                                                verification_results["individual_details_modal"] = True

                                                for item in condition_items:
                                                    condition_text = item.inner_text()
                                                    print(f"  • {condition_text}")

                                                    # "No applicable conditions" 메시지가 없는지 확인
                                                    if "No applicable conditions" not in condition_text:
                                                        print("    ✅ 조건이 올바르게 표시됨")
                                            else:
                                                print("❌ Condition Status가 비어있음")

                                        # 모달 닫기
                                        close_btn = modal.query_selector('.btn-close')
                                        if close_btn:
                                            close_btn.click()
                                            page.wait_for_timeout(1000)
                                break

        # 3. JavaScript 콘솔에서 데이터 직접 확인
        print("\n" + "="*80)
        print("📌 STEP 3: JavaScript 콘솔에서 데이터 검증")
        print("="*80)

        # ĐINH KIM NGOAN의 데이터를 직접 확인
        dinh_data = page.evaluate("""() => {
            const employees = window.employeeData || [];
            const dinh = employees.find(emp =>
                emp.name && emp.name.includes('ĐINH KIM NGOAN')
            );

            if (dinh) {
                return {
                    found: true,
                    name: dinh.name,
                    position: dinh.position,
                    type: dinh.type,
                    amount: dinh.amount,
                    attendance_rate: dinh.attendance_rate || dinh['attendance_rate'],
                    cond_1_value: dinh.cond_1_value,
                    cond_2_value: dinh.cond_2_value,
                    cond_3_value: dinh.cond_3_value,
                    cond_4_value: dinh.cond_4_value,
                    condition_results: dinh.condition_results,
                    fields: Object.keys(dinh).slice(0, 20)  // 처음 20개 필드명
                };
            }
            return { found: false, total_employees: employees.length };
        }""")

        if dinh_data['found']:
            print("✅ JavaScript 데이터에서 ĐINH KIM NGOAN 확인:")
            print(f"  - 이름: {dinh_data['name']}")
            print(f"  - 직급: {dinh_data['position']}")
            print(f"  - 타입: {dinh_data['type']}")
            print(f"  - 금액: {dinh_data['amount']}")
            print(f"  - attendance_rate: {dinh_data['attendance_rate']}")
            print(f"  - cond_1_value: {dinh_data['cond_1_value']}")
            print(f"  - cond_2_value: {dinh_data['cond_2_value']}")
            print(f"  - 사용 가능한 필드들: {', '.join(dinh_data['fields'][:10])}")
        else:
            print(f"❌ JavaScript 데이터에서 ĐINH KIM NGOAN을 찾을 수 없음")
            print(f"  - 전체 직원 수: {dinh_data['total_employees']}")

        # 최종 검증 결과
        print("\n" + "="*80)
        print("💡 최종 검증 결과")
        print("="*80)

        all_passed = all(verification_results.values())
        passed_count = sum(verification_results.values())
        total_count = len(verification_results)

        for key, value in verification_results.items():
            status = "✅" if value else "❌"
            print(f"{status} {key.replace('_', ' ').title()}: {'통과' if value else '실패'}")

        print(f"\n총 {total_count}개 중 {passed_count}개 통과 ({passed_count/total_count*100:.1f}%)")

        if all_passed:
            print("\n🎉 모든 검증 항목 통과! 모달 수정이 성공적으로 작동합니다.")
            print("✅ ĐINH KIM NGOAN (TYPE-2)의 325,312 VND 인센티브가 올바르게 표시됩니다.")
            print("✅ Position Details 모달의 Condition Fulfillment 테이블이 데이터를 표시합니다.")
            print("✅ Individual Details 모달이 조건을 올바르게 표시합니다.")
        else:
            print("\n⚠️ 일부 검증 항목 실패. 추가 수정이 필요할 수 있습니다.")

        # 스크린샷 저장
        page.screenshot(path='modal_verification_complete.png', full_page=True)
        print("\n📸 스크린샷 저장: modal_verification_complete.png")

        print("\n⏳ 브라우저를 30초 동안 열어두고 있습니다. 직접 확인하세요...")
        time.sleep(30)

        browser.close()

if __name__ == '__main__':
    verify_modal_fixes()