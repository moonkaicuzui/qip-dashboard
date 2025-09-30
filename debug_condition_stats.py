#!/usr/bin/env python3
"""
조건 통계가 계산되지 않는 문제를 디버깅하는 스크립트
JavaScript 콘솔에서 데이터를 확인하고 문제점을 파악
"""

from playwright.sync_api import sync_playwright
import os
import json
import time

def debug_condition_stats():
    """조건 통계 디버깅"""

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        print("="*80)
        print("🔍 조건 통계 디버깅 시작")
        print("="*80)

        # JavaScript 콘솔에서 데이터 확인
        print("\n📊 JavaScript 데이터 구조 확인:")

        # 1. employeeData 확인
        employee_data_check = page.evaluate("""() => {
            if (typeof employeeData !== 'undefined' && employeeData.length > 0) {
                // 첫 번째 직원 데이터 샘플
                const sample = employeeData[0];
                const fields = Object.keys(sample);

                // TYPE-1 직원 찾기
                const type1Employee = employeeData.find(e => e.type === 'TYPE-1');
                const type2Employee = employeeData.find(e => e.type === 'TYPE-2');

                return {
                    totalCount: employeeData.length,
                    sampleFields: fields,
                    type1Sample: type1Employee ? {
                        name: type1Employee.name,
                        position: type1Employee.position,
                        type: type1Employee.type,
                        'Absence Rate (raw)': type1Employee['Absence Rate (raw)'],
                        'Attendance Rate': type1Employee['Attendance Rate'],
                        'Actual Working Days': type1Employee['Actual Working Days'],
                        'Total Working Days': type1Employee['Total Working Days'],
                        'Unapproved Absences': type1Employee['Unapproved Absences'],
                        '5PRS_Pass_Rate': type1Employee['5PRS_Pass_Rate'],
                        '5PRS_Inspection_Qty': type1Employee['5PRS_Inspection_Qty'],
                        'AQL_july_result': type1Employee['AQL_july_result'],
                        'AQL_august_result': type1Employee['AQL_august_result'],
                        'AQL_september_result': type1Employee['AQL_september_result']
                    } : null,
                    type2Sample: type2Employee ? {
                        name: type2Employee.name,
                        position: type2Employee.position,
                        type: type2Employee.type,
                        'Absence Rate (raw)': type2Employee['Absence Rate (raw)'],
                        'Attendance Rate': type2Employee['Attendance Rate']
                    } : null
                };
            }
            return null;
        }""")

        if employee_data_check:
            print(f"✅ employeeData 확인됨: {employee_data_check['totalCount']}명")
            print(f"\n📝 필드 목록 (총 {len(employee_data_check['sampleFields'])}개):")
            for i, field in enumerate(employee_data_check['sampleFields'][:10]):
                print(f"  {i+1}. {field}")

            if employee_data_check['type1Sample']:
                print(f"\n📌 TYPE-1 샘플: {employee_data_check['type1Sample']['name']}")
                for key, value in employee_data_check['type1Sample'].items():
                    if key != 'name':
                        print(f"  - {key}: {value}")

            if employee_data_check['type2Sample']:
                print(f"\n📌 TYPE-2 샘플: {employee_data_check['type2Sample']['name']}")
                for key, value in employee_data_check['type2Sample'].items():
                    if key != 'name':
                        print(f"  - {key}: {value}")

        # Position Details 탭으로 이동하여 테스트
        print("\n" + "="*80)
        print("📊 Position Details 탭 테스트")
        print("="*80)

        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(2000)

            # TYPE-1 ASSEMBLY INSPECTOR 찾아서 클릭
            rows = page.query_selector_all('#positionTable tbody tr')
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 4:
                    position = cells[0].inner_text()
                    emp_type = cells[1].inner_text()

                    if 'ASSEMBLY INSPECTOR' in position and 'TYPE-1' in emp_type:
                        print(f"✅ {position} ({emp_type}) 발견")

                        # View 버튼 클릭
                        view_btn = cells[3].query_selector('button')
                        if view_btn:
                            view_btn.click()
                            page.wait_for_timeout(2000)

                            # JavaScript에서 직접 evaluateEmployeeConditions 함수 호출 테스트
                            condition_test = page.evaluate("""() => {
                                // evaluateEmployeeConditions 함수가 있는지 확인
                                if (typeof evaluateEmployeeConditions === 'function') {
                                    // TYPE-1 ASSEMBLY INSPECTOR 찾기
                                    const testEmployee = employeeData.find(e =>
                                        e.position === 'ASSEMBLY INSPECTOR' &&
                                        e.type === 'TYPE-1'
                                    );

                                    if (testEmployee) {
                                        const result = evaluateEmployeeConditions(testEmployee);
                                        return {
                                            functionExists: true,
                                            employee: testEmployee.name,
                                            conditions: result,
                                            rawData: {
                                                'Absence Rate (raw)': testEmployee['Absence Rate (raw)'],
                                                'Attendance Rate': testEmployee['Attendance Rate'],
                                                'Actual Working Days': testEmployee['Actual Working Days'],
                                                'Total Working Days': testEmployee['Total Working Days']
                                            }
                                        };
                                    }
                                }
                                return { functionExists: false };
                            }""")

                            if condition_test:
                                if condition_test['functionExists']:
                                    print(f"\n✅ evaluateEmployeeConditions 함수 확인됨")
                                    if 'employee' in condition_test:
                                        print(f"테스트 직원: {condition_test['employee']}")
                                        print(f"조건 평가 결과: {condition_test['conditions']}")
                                        print(f"원본 데이터: {condition_test['rawData']}")
                                else:
                                    print("❌ evaluateEmployeeConditions 함수를 찾을 수 없음")

                            # 모달 내용 확인
                            modal = page.query_selector('#employeeModal')
                            if modal:
                                # 조건별 통계 테이블 확인
                                condition_table = modal.query_selector('.condition-fulfillment-table')
                                if condition_table:
                                    print("\n📊 조건 충족 테이블 확인:")
                                    headers = condition_table.query_selector_all('th')
                                    if headers:
                                        print(f"  - 헤더 개수: {len(headers)}")
                                        for h in headers[:4]:
                                            print(f"    • {h.inner_text()}")

                                    tbody = condition_table.query_selector('tbody')
                                    if tbody:
                                        rows = tbody.query_selector_all('tr')
                                        print(f"  - 데이터 행 개수: {len(rows)}")
                                        if len(rows) == 0:
                                            print("  ❌ 테이블이 비어있음!")

                                            # JavaScript 콘솔에서 conditionStats 직접 확인
                                            stats_check = page.evaluate("""() => {
                                                // 현재 모달의 데이터 확인
                                                const modal = document.getElementById('employeeModal');
                                                if (modal && modal.dataset) {
                                                    return {
                                                        position: modal.dataset.position,
                                                        type: modal.dataset.type,
                                                        // conditionStats 변수가 있는지 확인
                                                        statsExists: typeof conditionStats !== 'undefined' ? conditionStats : null
                                                    };
                                                }
                                                return null;
                                            }""")

                                            if stats_check:
                                                print(f"\n🔍 모달 데이터 상태:")
                                                print(f"  - Position: {stats_check.get('position')}")
                                                print(f"  - Type: {stats_check.get('type')}")
                                                print(f"  - conditionStats: {stats_check.get('statsExists')}")

                            # 모달 닫기
                            close_btn = modal.query_selector('.btn-close')
                            if close_btn:
                                close_btn.click()
                        break

        print("\n" + "="*80)
        print("💡 디버깅 결과 요약")
        print("="*80)
        print("1. employeeData 구조와 필드명 확인 완료")
        print("2. evaluateEmployeeConditions 함수 동작 여부 확인")
        print("3. 조건 통계 테이블 렌더링 상태 확인")
        print("4. 문제점 파악을 위한 추가 디버깅 필요")

        # 브라우저 30초 유지
        print("\n⏳ 30초 후 브라우저가 자동으로 닫힙니다...")
        time.sleep(30)

        browser.close()

if __name__ == '__main__':
    debug_condition_stats()