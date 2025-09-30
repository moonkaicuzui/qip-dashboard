#!/usr/bin/env python3
"""
심층 문제 분석 스크립트
1. Position Details 테이블이 비어있는 이유
2. 조건 5/6 충족인데 인센티브 받는 이유
3. 모달 함수 작동 여부
"""

from playwright.sync_api import sync_playwright
import os
import json
import time

def analyze_issues():
    """대시보드 문제 심층 분석"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(2000)

        print("=" * 80)
        print("🔍 심층 문제 분석")
        print("=" * 80)

        # 1. 함수 존재 여부 확인
        print("\n📌 1. JavaScript 함수 상태:")
        functions_check = page.evaluate("""
            () => {
                return {
                    showEmployeeDetail: typeof window.showEmployeeDetail,
                    showPositionDetail: typeof window.showPositionDetail,
                    showEmployeeDetailFromPosition: typeof window.showEmployeeDetailFromPosition,
                    updatePositionTable: typeof window.updatePositionTable,
                    employeeData: typeof window.employeeData,
                    positionData: typeof window.positionData
                };
            }
        """)
        for func, type_str in functions_check.items():
            status = "✅" if type_str == "function" or (func == "employeeData" and type_str == "object") else "❌"
            print(f"  {status} {func}: {type_str}")

        # 2. Position Data 분석
        print("\n📌 2. Position Data 분석:")
        position_analysis = page.evaluate("""
            () => {
                if (!window.positionData) return { error: 'positionData not found' };

                const analysis = {
                    totalTypes: Object.keys(window.positionData).length,
                    types: {}
                };

                for (const type in window.positionData) {
                    analysis.types[type] = {
                        totalPositions: window.positionData[type].length,
                        samplePositions: window.positionData[type].slice(0, 3).map(p => ({
                            position: p.position,
                            count: p.count,
                            paid: p.paid
                        }))
                    };
                }

                return analysis;
            }
        """)

        if 'error' in position_analysis:
            print(f"  ❌ {position_analysis['error']}")
        else:
            print(f"  - Total Types: {position_analysis.get('totalTypes', 0)}")
            for type_name, type_data in position_analysis.get('types', {}).items():
                print(f"\n  📊 {type_name}:")
                print(f"    Total Positions: {type_data['totalPositions']}")
                if type_data.get('samplePositions'):
                    print("    Sample Positions:")
                    for pos in type_data['samplePositions']:
                        print(f"      • {pos['position']}: {pos['count']}명 (지급: {pos['paid']}명)")

        # 3. Position Details 탭 테스트
        print("\n📌 3. Position Details 탭 테이블 확인:")
        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(2000)

            # 테이블 행 확인
            table_check = page.evaluate("""
                () => {
                    const tbody = document.querySelector('#positionTable tbody');
                    if (!tbody) return { error: 'tbody not found' };

                    const rows = tbody.querySelectorAll('tr');
                    return {
                        rowCount: rows.length,
                        isEmpty: tbody.innerHTML.trim() === '',
                        htmlLength: tbody.innerHTML.length,
                        firstRow: rows[0]?.innerHTML?.substring(0, 200)
                    };
                }
            """)

            print(f"  - Table Body Found: {'✅' if 'rowCount' in table_check else '❌'}")
            if 'rowCount' in table_check:
                print(f"  - Row Count: {table_check['rowCount']}")
                print(f"  - Is Empty: {table_check['isEmpty']}")
                print(f"  - HTML Length: {table_check['htmlLength']}")
                if table_check.get('firstRow'):
                    print(f"  - First Row Preview: {table_check['firstRow'][:100]}...")

            # updatePositionTable 함수 호출 테스트
            print("\n  🔧 updatePositionTable 함수 수동 호출:")
            update_result = page.evaluate("""
                () => {
                    try {
                        if (typeof window.updatePositionTable === 'function') {
                            window.updatePositionTable();

                            // 함수 호출 후 테이블 상태 확인
                            const tbody = document.querySelector('#positionTable tbody');
                            const rows = tbody.querySelectorAll('tr');

                            return {
                                success: true,
                                afterRowCount: rows.length,
                                afterIsEmpty: tbody.innerHTML.trim() === ''
                            };
                        } else {
                            return { error: 'updatePositionTable is not a function' };
                        }
                    } catch (error) {
                        return { error: error.message };
                    }
                }
            """)

            if update_result.get('success'):
                print(f"    ✅ 함수 호출 성공")
                print(f"    - 호출 후 행 수: {update_result['afterRowCount']}")
                print(f"    - 여전히 비어있음: {update_result['afterIsEmpty']}")
            else:
                print(f"    ❌ 오류: {update_result.get('error', 'Unknown')}")

        # 4. 조건 로직 분석 (TRẦN THỊ THÚY ANH)
        print("\n📌 4. 조건 로직 분석 (TRẦN THỊ THÚY ANH):")
        employee_analysis = page.evaluate("""
            () => {
                const emp = window.employeeData.find(e =>
                    e['영문명'] === 'TRẦN THỊ THÚY ANH' ||
                    e['Full Name'] === 'TRẦN THỊ THÚY ANH'
                );

                if (!emp) return { error: 'Employee not found' };

                const conditions = emp.condition_results || [];
                const metConditions = conditions.filter(c => c.is_met);
                const failedConditions = conditions.filter(c => !c.is_met && !c.is_na);

                return {
                    name: emp['영문명'] || emp['Full Name'],
                    type: emp['ROLE TYPE STD'],
                    position: emp['FINAL QIP POSITION NAME CODE'],
                    incentive: emp.september_incentive || 0,
                    totalConditions: conditions.length,
                    metCount: metConditions.length,
                    failedCount: failedConditions.length,
                    failedDetails: failedConditions.map(c => ({
                        id: c.id,
                        name: c.name,
                        actual: c.actual,
                        threshold: c.threshold
                    }))
                };
            }
        """)

        if 'error' in employee_analysis:
            print(f"  ❌ {employee_analysis['error']}")
        else:
            print(f"  직원: {employee_analysis['name']}")
            print(f"  타입: {employee_analysis['type']}")
            print(f"  직급: {employee_analysis['position']}")
            incentive_value = int(employee_analysis['incentive']) if employee_analysis['incentive'] else 0
            print(f"  인센티브: {incentive_value:,} VND")
            print(f"  조건: {employee_analysis['metCount']}/{employee_analysis['totalConditions']} 충족")

            if employee_analysis['failedCount'] > 0:
                print(f"\n  ❌ 미충족 조건 ({employee_analysis['failedCount']}개):")
                for fail in employee_analysis['failedDetails']:
                    print(f"    • 조건 {fail['id']}: {fail['name']}")
                    print(f"      실제: {fail['actual']}, 기준: {fail['threshold']}")

            print(f"\n  💡 분석:")
            if employee_analysis['failedCount'] > 0 and incentive_value > 0:
                print(f"    ⚠️ 조건을 모두 충족하지 못했는데 인센티브를 받았습니다!")
                print(f"    이는 TYPE-1의 경우 일부 조건만 충족해도 인센티브를 받을 수 있음을 의미합니다.")

        # 스크린샷
        print("\n📸 스크린샷 저장...")
        page.screenshot(path='deep_analysis.png', full_page=False)
        print("  ✅ deep_analysis.png 저장됨")

        print("\n" + "=" * 80)
        print("💡 분석 완료! 브라우저를 30초간 열어둡니다...")
        print("=" * 80)

        time.sleep(30)
        browser.close()

if __name__ == '__main__':
    analyze_issues()