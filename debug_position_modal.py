#!/usr/bin/env python3
"""
Position Details 모달의 조건 통계 문제를 디버그하는 스크립트
"""

from playwright.sync_api import sync_playwright
import os
import time

def debug_position_modal():
    """Position Details 모달 디버깅"""

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False, devtools=True)
        page = browser.new_page()

        # 콘솔 메시지 캡처 설정
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(3000)

        print("="*80)
        print("🔍 Position Details 모달 조건 통계 디버깅")
        print("="*80)

        # Position Details 탭으로 이동
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
                            # 콘솔 메시지 초기화
                            console_messages.clear()

                            view_btn.click()
                            page.wait_for_timeout(3000)

                            # 콘솔 메시지 출력
                            print("\n📝 Console Messages:")
                            for msg in console_messages:
                                if 'conditionStats' in msg or 'Evaluating conditions' in msg or 'Initialized' in msg:
                                    print(f"  {msg}")

                            # JavaScript에서 conditionStats 직접 확인
                            condition_stats = page.evaluate("""() => {
                                // 마지막으로 계산된 conditionStats 찾기
                                const modal = document.getElementById('employeeModal');
                                if (!modal) return null;

                                // showPositionDetail 함수 내부에서 생성된 conditionStats에 접근하기 위해
                                // 테이블 데이터를 직접 확인
                                const table = modal.querySelector('.condition-fulfillment-table tbody');
                                const rows = table ? table.querySelectorAll('tr') : [];

                                const stats = {};
                                rows.forEach((row, index) => {
                                    const cells = row.querySelectorAll('td');
                                    if (cells.length >= 5) {
                                        stats[`condition_${index + 1}`] = {
                                            name: cells[1].innerText,
                                            total: cells[2].innerText,
                                            met: cells[3].innerText,
                                            unmet: cells[4].innerText
                                        };
                                    }
                                });

                                return {
                                    rowCount: rows.length,
                                    tableExists: !!table,
                                    stats: stats,
                                    innerHTML: table ? table.innerHTML.substring(0, 500) : 'No table'
                                };
                            }""")

                            print("\n📊 Condition Stats 테이블 상태:")
                            print(f"  - 테이블 존재: {condition_stats['tableExists']}")
                            print(f"  - 데이터 행 개수: {condition_stats['rowCount']}")
                            if condition_stats['rowCount'] > 0:
                                print("  - 조건별 데이터:")
                                for key, value in condition_stats['stats'].items():
                                    print(f"    • {key}: {value}")
                            else:
                                print(f"  - 테이블 HTML (처음 500자): {condition_stats['innerHTML']}")

                            # 직원 샘플 데이터 확인
                            sample_employee = page.evaluate("""() => {
                                const employees = window.employeeData.filter(e =>
                                    e.position === 'ASSEMBLY INSPECTOR' && e.type === 'TYPE-1'
                                );
                                if (employees.length > 0) {
                                    const emp = employees[0];
                                    return {
                                        name: emp.name,
                                        'Absence Rate (raw)': emp['Absence Rate (raw)'],
                                        'Attendance Rate': emp['Attendance Rate'],
                                        'Unapproved Absences': emp['Unapproved Absences'],
                                        'Actual Working Days': emp['Actual Working Days'],
                                        'Total Working Days': emp['Total Working Days'],
                                        'condition_results': emp.condition_results ? 'exists' : 'missing',
                                        'incentive_amount': emp.incentive_amount || emp.INCENTIVE_1
                                    };
                                }
                                return null;
                            }""")

                            if sample_employee:
                                print("\n🔍 샘플 직원 데이터:")
                                for key, value in sample_employee.items():
                                    print(f"  - {key}: {value}")

                            # Employee Details Status 확인
                            employee_rows = page.query_selector_all('#positionEmployeeTable tbody tr')
                            print(f"\n📋 Employee Details Status:")
                            print(f"  - 직원 수: {len(employee_rows)}")

                            if len(employee_rows) > 0:
                                # 첫 번째 직원의 Condition Fulfillment 확인
                                first_row = employee_rows[0]
                                cells = first_row.query_selector_all('td')
                                if len(cells) >= 5:
                                    badges_cell = cells[4]
                                    badges = badges_cell.query_selector_all('.badge')
                                    print(f"  - 첫 번째 직원의 배지 개수: {len(badges)}")
                                    for badge in badges[:3]:  # 처음 3개만 출력
                                        print(f"    • {badge.inner_text()}")

                        break

        print("\n" + "="*80)
        print("💡 분석 결과:")
        print("1. conditionStats가 제대로 초기화되고 있는지")
        print("2. 조건 평가 로직이 실행되는지")
        print("3. 테이블에 데이터가 렌더링되는지")
        print("4. 필드명 불일치 문제가 있는지")
        print("="*80)

        # 브라우저 30초 유지
        print("\n⏳ 30초 후 브라우저가 자동으로 닫힙니다...")
        time.sleep(30)

        browser.close()

if __name__ == '__main__':
    debug_position_modal()