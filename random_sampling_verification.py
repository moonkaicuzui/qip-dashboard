#!/usr/bin/env python3
"""
랜덤 샘플링 검증 스크립트
모든 타입과 모든 직책에 대해 개선사항이 정상 적용되었는지 확인
"""

from playwright.sync_api import sync_playwright
import os
import random
import time

def random_sampling_verification():
    """모든 타입과 직책에 대한 랜덤 샘플링 검증"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 대시보드 열기
        dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(2000)

        print("=" * 80)
        print("🎯 랜덤 샘플링 검증 시작")
        print("=" * 80)

        # 1. 전체 데이터 구조 확인
        print("\n📊 1. 데이터 구조 확인:")
        data_structure = page.evaluate("""
            () => {
                const result = {
                    employeeDataExists: typeof window.employeeData !== 'undefined',
                    positionDataExists: typeof window.positionData !== 'undefined',
                    employeeCount: 0,
                    typeBreakdown: { 'TYPE-1': 0, 'TYPE-2': 0, 'TYPE-3': 0 },
                    positionSamples: {}
                };

                if (window.employeeData) {
                    result.employeeCount = window.employeeData.length;

                    // TYPE별 카운트
                    window.employeeData.forEach(emp => {
                        const type = emp['ROLE TYPE STD'] || emp.type;
                        if (type && result.typeBreakdown.hasOwnProperty(type)) {
                            result.typeBreakdown[type]++;
                        }
                    });

                    // 각 TYPE별로 랜덤 직원 선택
                    ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {
                        const typeEmployees = window.employeeData.filter(emp =>
                            (emp['ROLE TYPE STD'] || emp.type) === type
                        );

                        if (typeEmployees.length > 0) {
                            // 랜덤으로 최대 3명 선택
                            const sampleSize = Math.min(3, typeEmployees.length);
                            const samples = [];
                            const shuffled = typeEmployees.sort(() => 0.5 - Math.random());

                            for (let i = 0; i < sampleSize; i++) {
                                const emp = shuffled[i];
                                samples.push({
                                    name: emp['영문명'] || emp['Full Name'],
                                    position: emp['FINAL QIP POSITION NAME CODE'],
                                    type: type,
                                    incentive: emp.september_incentive || 0
                                });
                            }

                            result.positionSamples[type] = samples;
                        }
                    });
                }

                return result;
            }
        """)

        print(f"  - employeeData 존재: {data_structure.get('employeeDataExists', False)}")
        print(f"  - positionData 존재: {data_structure.get('positionDataExists', False)}")
        print(f"  - 전체 직원 수: {data_structure.get('employeeCount', 0)}명")
        print(f"  - TYPE별 분포:")
        for type_name, count in data_structure.get('typeBreakdown', {}).items():
            print(f"    • {type_name}: {count}명")

        # 2. Individual Details 탭 테스트
        print("\n📊 2. Individual Details 모달 테스트 (랜덤 샘플):")

        individual_tab = page.query_selector('[data-tab="individual"]')
        if individual_tab:
            individual_tab.click()
            page.wait_for_timeout(1500)

            for type_name, samples in data_structure.get('positionSamples', {}).items():
                if samples:
                    print(f"\n  🎯 {type_name} 테스트:")

                    for sample in samples[:1]:  # 각 타입별로 1명씩만 테스트
                        print(f"    직원: {sample['name']} ({sample['position']})")
                        print(f"    인센티브: {sample['incentive']:,} VND")

                        # 해당 직원의 View 버튼 찾기
                        rows = page.query_selector_all('#employeeTable tbody tr')
                        found = False

                        for row in rows:
                            cells = row.query_selector_all('td')
                            if len(cells) >= 2:
                                name_text = cells[1].inner_text() if cells[1] else ""
                                if sample['name'] in name_text:
                                    found = True
                                    view_btn = cells[5].query_selector('button') if len(cells) > 5 else None

                                    if view_btn:
                                        view_btn.click()
                                        page.wait_for_timeout(1500)

                                        # 모달 확인
                                        modal = page.query_selector('#individualModal')
                                        if modal and modal.is_visible():
                                            print(f"      ✅ 모달 열림")

                                            # 조건 확인
                                            conditions = page.evaluate("""
                                                () => {
                                                    const list = document.querySelector('#individualConditionList');
                                                    if (!list) return [];

                                                    const items = list.querySelectorAll('li');
                                                    const conditions = [];
                                                    items.forEach(item => {
                                                        const text = item.innerText;
                                                        const isPassed = text.includes('✓') || text.includes('PASS');
                                                        conditions.push({
                                                            text: text.substring(0, 50),
                                                            passed: isPassed
                                                        });
                                                    });
                                                    return conditions;
                                                }
                                            """)

                                            if conditions:
                                                passed = sum(1 for c in conditions if c['passed'])
                                                print(f"      조건: {passed}/{len(conditions)} 충족")

                                            # 모달 닫기
                                            close_btn = modal.query_selector('.btn-close')
                                            if close_btn:
                                                close_btn.click()
                                                page.wait_for_timeout(1000)
                                        else:
                                            print(f"      ❌ 모달 열리지 않음")
                                    break

                        if not found:
                            print(f"      ⚠️ 직원을 테이블에서 찾을 수 없음")

        # 3. Position Details 탭 테스트
        print("\n📊 3. Position Details 테이블 테스트:")

        position_tab = page.query_selector('[data-tab="position"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(2000)

            # positionData 확인
            position_check = page.evaluate("""
                () => {
                    if (!window.positionData) return { error: 'positionData not found' };

                    const keys = Object.keys(window.positionData);
                    const typePositions = {
                        'TYPE-1': [],
                        'TYPE-2': [],
                        'TYPE-3': []
                    };

                    keys.forEach(key => {
                        const data = window.positionData[key];
                        if (data && data.type && typePositions.hasOwnProperty(data.type)) {
                            typePositions[data.type].push({
                                position: data.position,
                                total: data.total,
                                paid: data.paid
                            });
                        }
                    });

                    return typePositions;
                }
            """)

            if isinstance(position_check, dict) and 'error' not in position_check:
                print("  ✅ positionData 정상 생성됨")

                for type_name, positions in position_check.items():
                    if positions:
                        print(f"\n  {type_name}: {len(positions)}개 직급")
                        # 랜덤으로 2개 직급 표시
                        for pos in random.sample(positions, min(2, len(positions))):
                            print(f"    • {pos['position']}: {pos['total']}명 (지급: {pos['paid']}명)")

                # 첫 번째 테이블의 첫 번째 행 클릭 테스트
                print("\n  📋 Position 모달 테스트:")
                first_row = page.query_selector('#positionTables tbody tr')
                if first_row:
                    cells = first_row.query_selector_all('td')
                    if len(cells) >= 2:
                        position_name = cells[0].inner_text() if cells[0] else ""
                        print(f"    테스트 직급: {position_name}")

                        first_row.click()
                        page.wait_for_timeout(1500)

                        modal = page.query_selector('#positionModal')
                        if modal and modal.is_visible():
                            print("    ✅ Position 모달 정상 열림")

                            # 직원 리스트 확인
                            employee_count = page.evaluate("""
                                () => {
                                    const list = document.querySelector('#positionEmployeeList');
                                    if (!list) return 0;
                                    return list.querySelectorAll('li').length;
                                }
                            """)

                            print(f"    직원 수: {employee_count}명 표시됨")

                            # 모달 닫기
                            close_btn = modal.query_selector('.btn-close')
                            if close_btn:
                                close_btn.click()
                                page.wait_for_timeout(1000)
                        else:
                            print("    ❌ Position 모달이 열리지 않음")
            else:
                print(f"  ❌ {position_check.get('error', 'Unknown error')}")

        # 4. 언어 전환 테스트
        print("\n📊 4. 언어 전환 테스트:")

        languages = [
            {'code': 'en', 'name': 'English', 'test': 'Total Employees'},
            {'code': 'ko', 'name': '한국어', 'test': '전체 직원'},
            {'code': 'vi', 'name': 'Tiếng Việt', 'test': 'Tổng số nhân viên'}
        ]

        for lang in languages:
            # 언어 전환
            lang_btn = page.query_selector(f'button[onclick*="changeLanguage(\'{lang["code"]}\')"]')
            if lang_btn:
                lang_btn.click()
                page.wait_for_timeout(1000)

                # 텍스트 확인
                header_text = page.evaluate("""
                    () => {
                        const card = document.querySelector('.stat-card h6');
                        return card ? card.innerText : '';
                    }
                """)

                if lang['test'] in header_text:
                    print(f"  ✅ {lang['name']}: 정상 전환")
                else:
                    print(f"  ❌ {lang['name']}: 전환 실패 ('{header_text}' != '{lang['test']}')")

        # 스크린샷 저장
        print("\n📸 최종 스크린샷 저장...")
        page.screenshot(path='random_sampling_verification.png', full_page=False)
        print("  ✅ random_sampling_verification.png 저장됨")

        print("\n" + "=" * 80)
        print("💡 랜덤 샘플링 검증 완료!")
        print("=" * 80)

        time.sleep(20)  # 20초 대기
        browser.close()

if __name__ == '__main__':
    random_sampling_verification()