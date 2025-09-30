#!/usr/bin/env python3
"""
모달 기능 상세 검증 스크립트
"""

from playwright.sync_api import sync_playwright
import os
import json
import time

def test_modals():
    """Individual Details 모달 집중 테스트"""

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(2000)

        print("=" * 80)
        print("🎯 모달 기능 상세 검증")
        print("=" * 80)

        # 1. 데이터 로드 확인
        result = page.evaluate("""
            () => {
                const data = window.employeeData;
                if (!data) return { error: 'employeeData not found' };

                // TYPE별 카운트
                const typeCounts = {
                    'TYPE-1': 0,
                    'TYPE-2': 0,
                    'TYPE-3': 0
                };

                // 조건 결과가 있는 직원 찾기
                const employeesWithConditions = [];

                data.forEach(emp => {
                    const type = emp['ROLE TYPE STD'] || emp.type;
                    if (type && typeCounts.hasOwnProperty(type)) {
                        typeCounts[type]++;
                    }

                    // condition_results 확인
                    if (emp.condition_results && emp.condition_results.length > 0) {
                        employeesWithConditions.push({
                            name: emp['영문명'] || emp.name,
                            type: type,
                            position: emp['FINAL QIP POSITION NAME CODE'] || emp.position,
                            conditions: emp.condition_results.length,
                            incentive: emp.september_incentive || 0
                        });
                    }
                });

                return {
                    total: data.length,
                    typeCounts: typeCounts,
                    withConditions: employeesWithConditions.length,
                    samples: employeesWithConditions.slice(0, 5)
                };
            }
        """)

        print("\n📊 데이터 로드 상태:")
        print(f"  - 전체 직원 수: {result.get('total', 0)}명")
        print(f"  - TYPE별 분포:")
        for t, c in result.get('typeCounts', {}).items():
            print(f"    • {t}: {c}명")
        print(f"  - 조건 데이터가 있는 직원: {result.get('withConditions', 0)}명")

        if result.get('samples'):
            print("\n  샘플 직원:")
            for sample in result['samples']:
                print(f"    • {sample['name']} ({sample['type']}, {sample['position']})")
                incentive_value = f"{sample['incentive']:,.0f}" if isinstance(sample['incentive'], (int, float)) else str(sample['incentive'])
                print(f"      조건: {sample['conditions']}개, 인센티브: {incentive_value} VND")

        # 2. Individual Details 탭으로 이동
        print("\n📌 Individual Details 탭 테스트:")
        individual_tab = page.query_selector('[data-tab="individual"]')
        if individual_tab:
            individual_tab.click()
            page.wait_for_timeout(2000)
            print("  ✅ Individual Details 탭 열림")

            # 테이블 확인
            rows = page.query_selector_all('#employeeTable tbody tr:visible')
            print(f"  - 표시된 행 수: {len(rows)}개")

            # TYPE-2 직원 찾기
            found_type2 = False
            for i, row in enumerate(rows[:30]):  # 처음 30개만
                cells = row.query_selector_all('td')
                if len(cells) >= 6:
                    name = cells[1].inner_text() if cells[1] else ""
                    emp_type = cells[3].inner_text() if cells[3] else ""

                    if 'TYPE-2' in emp_type:
                        found_type2 = True
                        position = cells[2].inner_text() if cells[2] else ""
                        amount = cells[4].inner_text() if cells[4] else ""

                        print(f"\n  🎯 TYPE-2 직원 발견 (행 {i+1}):")
                        print(f"    이름: {name}")
                        print(f"    직급: {position}")
                        print(f"    타입: {emp_type}")
                        print(f"    인센티브: {amount}")

                        # View 버튼 클릭
                        view_btn = cells[5].query_selector('button')
                        if view_btn:
                            print("    View 버튼 클릭...")
                            view_btn.click()
                            page.wait_for_timeout(2000)

                            # 모달 확인
                            modal = page.query_selector('#individualModal')
                            if modal and modal.is_visible():
                                print("    ✅ Individual Details 모달 열림!")

                                # 모달 내용 확인
                                modal_content = page.evaluate("""
                                    () => {
                                        const modal = document.getElementById('individualModal');
                                        if (!modal) return null;

                                        const title = modal.querySelector('.modal-title')?.innerText;
                                        const conditionList = modal.querySelector('#individualConditionList');
                                        const conditions = [];

                                        if (conditionList) {
                                            const items = conditionList.querySelectorAll('li');
                                            items.forEach(item => {
                                                conditions.push(item.innerText);
                                            });
                                        }

                                        return {
                                            title: title,
                                            conditionCount: conditions.length,
                                            conditions: conditions.slice(0, 5)  // 처음 5개만
                                        };
                                    }
                                """)

                                if modal_content:
                                    print(f"    📋 모달 내용:")
                                    print(f"      • 제목: {modal_content.get('title', 'N/A')}")
                                    print(f"      • 조건 수: {modal_content.get('conditionCount', 0)}개")
                                    if modal_content.get('conditions'):
                                        print(f"      • 조건 상태:")
                                        for cond in modal_content['conditions']:
                                            status = "✅" if "PASS" in cond else "❌" if "FAIL" in cond else "⚠️"
                                            print(f"        {status} {cond}")

                                # 모달 닫기
                                close_btn = modal.query_selector('.btn-close')
                                if close_btn:
                                    close_btn.click()
                                    page.wait_for_timeout(1000)
                                    print("    모달 닫음")
                            else:
                                print("    ❌ 모달이 열리지 않음")
                        else:
                            print("    ❌ View 버튼을 찾을 수 없음")
                        break

            if not found_type2:
                print("  ❌ TYPE-2 직원을 찾을 수 없음")

        # 3. JavaScript 콘솔 에러 확인
        print("\n📊 JavaScript 상태 확인:")
        js_check = page.evaluate("""
            () => {
                const checks = {
                    employeeData: typeof window.employeeData !== 'undefined',
                    employeeDataLength: window.employeeData ? window.employeeData.length : 0,
                    conditionResults: 0,
                    errors: []
                };

                if (window.employeeData) {
                    window.employeeData.forEach(emp => {
                        if (emp.condition_results && emp.condition_results.length > 0) {
                            checks.conditionResults++;
                        }
                    });
                }

                // 함수 존재 확인
                checks.showIndividualDetail = typeof window.showIndividualDetail === 'function';
                checks.showPositionDetail = typeof window.showPositionDetail === 'function';

                return checks;
            }
        """)

        print(f"  - employeeData 존재: {js_check.get('employeeData', False)}")
        print(f"  - 직원 데이터 수: {js_check.get('employeeDataLength', 0)}명")
        print(f"  - condition_results가 있는 직원: {js_check.get('conditionResults', 0)}명")
        print(f"  - showIndividualDetail 함수: {js_check.get('showIndividualDetail', False)}")
        print(f"  - showPositionDetail 함수: {js_check.get('showPositionDetail', False)}")

        # 스크린샷
        print("\n📸 스크린샷 저장...")
        page.screenshot(path='detailed_modal_test.png', full_page=False)
        print("  ✅ detailed_modal_test.png 저장됨")

        print("\n" + "=" * 80)
        print("💡 테스트 완료! 브라우저를 30초간 열어둡니다...")
        print("=" * 80)

        time.sleep(30)
        browser.close()

if __name__ == '__main__':
    test_modals()