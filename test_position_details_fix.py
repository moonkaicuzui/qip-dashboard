#!/usr/bin/env python3
"""
Position Details 탭 수정사항 검증 스크립트
"""

from playwright.sync_api import sync_playwright
import os
import time

def test_position_details_fix():
    """Position Details 탭이 제대로 작동하는지 검증"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(2000)

        print("=" * 80)
        print("🔧 Position Details 탭 수정사항 검증")
        print("=" * 80)

        # 1. 함수 존재 여부 확인
        print("\n📌 1. JavaScript 함수 및 변수 상태:")
        functions_check = page.evaluate("""
            () => {
                return {
                    showEmployeeDetail: typeof window.showEmployeeDetail,
                    showPositionDetail: typeof window.showPositionDetail,
                    showEmployeeDetailFromPosition: typeof window.showEmployeeDetailFromPosition,
                    updatePositionTable: typeof window.updatePositionTable,
                    generatePositionTables: typeof window.generatePositionTables,
                    employeeData: typeof window.employeeData,
                    positionData: typeof window.positionData
                };
            }
        """)

        for func, type_str in functions_check.items():
            if func in ['employeeData', 'positionData']:
                status = "✅" if type_str == "object" else "❌"
            else:
                status = "✅" if type_str == "function" else "❌"
            print(f"  {status} {func}: {type_str}")

        # 2. Position Details 탭 클릭
        print("\n📌 2. Position Details 탭 테스트:")
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            print("  - Position Details 탭 클릭...")
            position_tab.click()
            page.wait_for_timeout(2000)  # 테이블 생성 대기

            # 3. positionData 확인
            position_data_check = page.evaluate("""
                () => {
                    if (!window.positionData) return { error: 'positionData not found' };

                    const types = Object.keys(window.positionData);
                    const result = {
                        totalTypes: types.length,
                        types: {}
                    };

                    for (const type of types) {
                        result.types[type] = {
                            totalPositions: window.positionData[type].length,
                            samplePositions: window.positionData[type].slice(0, 2).map(p => ({
                                position: p.position,
                                count: p.count,
                                paid: p.paid
                            }))
                        };
                    }

                    return result;
                }
            """)

            if 'error' in position_data_check:
                print(f"  ❌ {position_data_check['error']}")
            else:
                print(f"  ✅ positionData 생성됨: {position_data_check.get('totalTypes', 0)} types")
                for type_name, type_data in position_data_check.get('types', {}).items():
                    print(f"\n  📊 {type_name}:")
                    print(f"    Total Positions: {type_data['totalPositions']}")
                    if type_data.get('samplePositions'):
                        for pos in type_data['samplePositions']:
                            print(f"      • {pos['position']}: {pos['count']}명 (지급: {pos['paid']}명)")

            # 4. Position 테이블 확인
            print("\n📌 3. Position 테이블 상태:")
            table_check = page.evaluate("""
                () => {
                    const tables = document.querySelectorAll('#positionTables table');
                    const result = {
                        tableCount: tables.length,
                        tables: []
                    };

                    tables.forEach(table => {
                        const tbody = table.querySelector('tbody');
                        const rows = tbody ? tbody.querySelectorAll('tr') : [];
                        result.tables.push({
                            rowCount: rows.length,
                            isEmpty: tbody ? tbody.innerHTML.trim() === '' : true
                        });
                    });

                    return result;
                }
            """)

            print(f"  - 테이블 수: {table_check.get('tableCount', 0)}개")
            for i, table_info in enumerate(table_check.get('tables', [])):
                print(f"  - 테이블 {i+1}: {table_info['rowCount']}행 (비어있음: {table_info['isEmpty']})")

            # 5. 테이블 행 클릭 테스트 (첫 번째 행)
            print("\n📌 4. Position 상세 모달 테스트:")
            first_row = page.query_selector('#positionTables tbody tr')
            if first_row:
                cells = first_row.query_selector_all('td')
                if len(cells) >= 3:
                    position_name = cells[0].inner_text() if cells[0] else "Unknown"
                    count = cells[1].inner_text() if cells[1] else "0"
                    print(f"  - 첫 번째 행 클릭: {position_name} ({count}명)")

                    first_row.click()
                    page.wait_for_timeout(1500)

                    # 모달 확인
                    modal = page.query_selector('#positionModal')
                    if modal and modal.is_visible():
                        print("  ✅ Position 상세 모달 열림!")

                        # 모달 내용 확인
                        modal_content = page.evaluate("""
                            () => {
                                const modal = document.getElementById('positionModal');
                                if (!modal) return null;

                                const title = modal.querySelector('.modal-title')?.innerText;
                                const employeeList = modal.querySelector('#positionEmployeeList');
                                const employees = [];

                                if (employeeList) {
                                    const items = employeeList.querySelectorAll('li');
                                    items.forEach(item => {
                                        employees.push(item.innerText);
                                    });
                                }

                                return {
                                    title: title,
                                    employeeCount: employees.length,
                                    employees: employees.slice(0, 3)
                                };
                            }
                        """)

                        if modal_content:
                            print(f"    📋 모달 내용:")
                            print(f"      • 제목: {modal_content.get('title', 'N/A')}")
                            print(f"      • 직원 수: {modal_content.get('employeeCount', 0)}명")
                            if modal_content.get('employees'):
                                print(f"      • 샘플 직원:")
                                for emp in modal_content['employees']:
                                    print(f"        - {emp}")

                        # 모달 닫기
                        close_btn = modal.query_selector('.btn-close')
                        if close_btn:
                            close_btn.click()
                            page.wait_for_timeout(1000)
                            print("    모달 닫음")
                    else:
                        print("  ❌ 모달이 열리지 않음")
            else:
                print("  ❌ Position 테이블에 행이 없음")
        else:
            print("  ❌ Position Details 탭을 찾을 수 없음")

        # 스크린샷
        print("\n📸 스크린샷 저장...")
        page.screenshot(path='position_details_fix_test.png', full_page=False)
        print("  ✅ position_details_fix_test.png 저장됨")

        print("\n" + "=" * 80)
        print("💡 검증 완료! 브라우저를 30초간 열어둡니다...")
        print("=" * 80)

        time.sleep(30)
        browser.close()

if __name__ == '__main__':
    test_position_details_fix()