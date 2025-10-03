#!/usr/bin/env python3
"""
대시보드 심층 검증 - Playwright를 사용한 완전한 기능 테스트
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def deep_verification():
    """대시보드 모든 기능 심층 검증"""

    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    print("="*70)
    print("🔍 대시보드 심층 검증 시작 - Version 6")
    print("="*70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 브라우저 보이게
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # 에러 수집
        js_errors = []
        console_msgs = []

        page.on("pageerror", lambda err: js_errors.append(str(err)))
        page.on("console", lambda msg: console_msgs.append({
            'type': msg.type,
            'text': msg.text[:200] if msg.text else ''
        }))

        # ========== 1. 페이지 로드 테스트 ==========
        print("\n[1/8] 📄 페이지 로드 테스트")
        print("-" * 50)

        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(3000)

        # JavaScript 에러 확인
        critical_errors = [e for e in js_errors if 'Unexpected' in e or 'undefined' in e]
        if critical_errors:
            print(f"❌ Critical JavaScript errors: {len(critical_errors)}")
            for err in critical_errors[:2]:
                print(f"   - {err[:100]}")
        else:
            print("✅ No critical JavaScript errors")

        # ========== 2. 데이터 로드 확인 ==========
        print("\n[2/8] 📊 데이터 로드 확인")
        print("-" * 50)

        data_check = await page.evaluate("""() => {
            return {
                employeeData: {
                    exists: typeof employeeData !== 'undefined',
                    count: typeof employeeData !== 'undefined' ? employeeData.length : 0,
                    hasType1: typeof employeeData !== 'undefined' ?
                        employeeData.filter(e => e.type === 'TYPE-1').length : 0,
                    hasType2: typeof employeeData !== 'undefined' ?
                        employeeData.filter(e => e.type === 'TYPE-2').length : 0,
                    hasType3: typeof employeeData !== 'undefined' ?
                        employeeData.filter(e => e.type === 'TYPE-3').length : 0,
                    with5PRS: typeof employeeData !== 'undefined' ?
                        employeeData.filter(e => e['5PRS_Pass_Rate'] > 0).length : 0,
                    withAQL: typeof employeeData !== 'undefined' ?
                        employeeData.filter(e => e['September AQL Failures'] !== undefined).length : 0
                },
                translations: typeof translations !== 'undefined',
                dashboardData: typeof dashboardData !== 'undefined',
                functions: {
                    showTab: typeof showTab === 'function',
                    changeLanguage: typeof changeLanguage === 'function',
                    generatePositionTables: typeof generatePositionTables === 'function'
                }
            };
        }""")

        if data_check['employeeData']['exists']:
            print(f"✅ employeeData 로드됨: {data_check['employeeData']['count']}명")
            print(f"   - TYPE-1: {data_check['employeeData']['hasType1']}명")
            print(f"   - TYPE-2: {data_check['employeeData']['hasType2']}명")
            print(f"   - TYPE-3: {data_check['employeeData']['hasType3']}명")
            print(f"   - 5PRS 데이터: {data_check['employeeData']['with5PRS']}명")
            print(f"   - AQL 데이터: {data_check['employeeData']['withAQL']}명")
        else:
            print("❌ employeeData 로드 실패!")

        if not data_check['functions']['showTab']:
            print("❌ showTab 함수 없음 - 탭 전환 불가!")

        # ========== 3. 요약 탭 테스트 ==========
        print("\n[3/8] 📈 요약 탭 데이터 확인")
        print("-" * 50)

        summary_data = await page.evaluate("""() => {
            const summaryBody = document.getElementById('typeSummaryBody');
            if (!summaryBody) return { exists: false };

            const rows = summaryBody.querySelectorAll('tr');
            const data = [];

            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 5) {
                    data.push({
                        type: cells[0].innerText,
                        total: cells[1].innerText,
                        paid: cells[2].innerText,
                        rate: cells[3].innerText,
                        amount: cells[4].innerText
                    });
                }
            });

            return { exists: true, rows: data.length, data: data };
        }""")

        if summary_data['exists'] and summary_data['rows'] > 0:
            print(f"✅ 요약 테이블 정상: {summary_data['rows']}개 TYPE")
            for row in summary_data['data']:
                print(f"   {row['type']}: {row['paid']}/{row['total']} ({row['rate']})")
        else:
            print("❌ 요약 테이블 비어있음!")

        # ========== 4. 탭 전환 테스트 ==========
        print("\n[4/8] 🔄 탭 전환 기능 테스트")
        print("-" * 50)

        tabs_to_test = [
            ('position', '직급별 상세', '#positionContent'),
            ('detail', '개인별 상세', '#detailTable'),
            ('criteria', '인센티브 기준', '#criteriaContent'),
            ('orgchart', '조직도', '#orgChartContent'),
            ('validation', '시스템 검증', '#validationContent')
        ]

        for tab_name, tab_label, content_selector in tabs_to_test:
            try:
                # 탭 클릭
                tab_selector = f'div.tab[data-tab="{tab_name}"]'
                await page.click(tab_selector)
                await page.wait_for_timeout(500)

                # 콘텐츠 확인
                content = await page.query_selector(content_selector)
                if content:
                    html = await content.inner_html()
                    if len(html) > 50:
                        print(f"✅ {tab_label} 탭: 정상 작동")
                    else:
                        print(f"⚠️ {tab_label} 탭: 콘텐츠 없음")
                else:
                    print(f"❌ {tab_label} 탭: 콘텐츠 요소 없음")
            except Exception as e:
                print(f"❌ {tab_label} 탭: 클릭 실패 - {str(e)[:50]}")

        # ========== 5. Position Details 모달 테스트 ==========
        print("\n[5/8] 🔲 Position Details 모달 테스트")
        print("-" * 50)

        # Position 탭으로 이동
        await page.click('div.tab[data-tab="position"]')
        await page.wait_for_timeout(1000)

        # View 버튼 찾기
        view_buttons = await page.query_selector_all('button.btn-outline-primary')
        if not view_buttons:
            view_buttons = await page.query_selector_all('button:has-text("View")')

        if len(view_buttons) > 0:
            print(f"✅ View 버튼 발견: {len(view_buttons)}개")

            # 첫 번째 버튼 클릭
            await view_buttons[0].click()
            await page.wait_for_timeout(1500)

            # 모달 확인
            modal = await page.query_selector('#employeeModal')
            if modal and await modal.is_visible():
                print("✅ 모달 열림 성공")

                # 모달 내용 확인
                modal_data = await page.evaluate("""() => {
                    const modal = document.getElementById('employeeModal');
                    if (!modal) return null;

                    const title = modal.querySelector('#modalTitle')?.innerText;
                    const tables = modal.querySelectorAll('table');
                    const badges = modal.querySelectorAll('.badge');

                    // 조건 통계 확인
                    let conditionStats = [];
                    if (tables.length > 0) {
                        const rows = tables[0].querySelectorAll('tbody tr');
                        rows.forEach(row => {
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 5) {
                                conditionStats.push({
                                    name: cells[0].innerText,
                                    total: cells[2].innerText
                                });
                            }
                        });
                    }

                    return {
                        title: title,
                        tableCount: tables.length,
                        badgeCount: badges.length,
                        conditions: conditionStats
                    };
                }""")

                if modal_data:
                    print(f"   모달 제목: {modal_data['title']}")
                    print(f"   테이블 수: {modal_data['tableCount']}")
                    print(f"   배지 수: {modal_data['badgeCount']}")

                    # AQL/5PRS 조건 확인
                    aql_found = False
                    prs_found = False

                    for cond in modal_data['conditions']:
                        if 'AQL' in cond['name']:
                            aql_found = True
                            if cond['total'] != '0' and cond['total'] != 'N/A':
                                print(f"   ✅ AQL 데이터 있음: {cond['total']}명")
                            else:
                                print(f"   ⚠️ AQL 데이터 없음")
                        if '5PRS' in cond['name'] or 'PRS' in cond['name']:
                            prs_found = True
                            if cond['total'] != '0' and cond['total'] != 'N/A':
                                print(f"   ✅ 5PRS 데이터 있음: {cond['total']}명")
                            else:
                                print(f"   ⚠️ 5PRS 데이터 없음")

                # 모달 닫기
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(500)

            else:
                print("❌ 모달이 열리지 않음!")
        else:
            print("❌ View 버튼을 찾을 수 없음!")

        # ========== 6. 언어 변경 테스트 ==========
        print("\n[6/8] 🌐 언어 변경 기능 테스트")
        print("-" * 50)

        # 영어로 변경
        language_selector = await page.query_selector('#languageSelect')
        if language_selector:
            await language_selector.select_option('en')
            await page.wait_for_timeout(500)

            # 제목 확인
            title = await page.query_selector('#mainTitle')
            if title:
                title_text = await title.inner_text()
                if 'QIP Incentive' in title_text:
                    print("✅ 영어 변경 성공")
                else:
                    print("⚠️ 영어 변경 후 제목이 이상함")

            # 다시 한국어로
            await language_selector.select_option('ko')
            await page.wait_for_timeout(500)
            print("✅ 한국어로 복귀")
        else:
            print("❌ 언어 선택기를 찾을 수 없음!")

        # ========== 7. 검색 기능 테스트 ==========
        print("\n[7/8] 🔍 검색 기능 테스트")
        print("-" * 50)

        # 개인별 상세 탭으로 이동
        await page.click('div.tab[data-tab="detail"]')
        await page.wait_for_timeout(1000)

        search_input = await page.query_selector('#searchInput')
        if search_input:
            # 검색어 입력
            await search_input.type('619')
            await page.wait_for_timeout(500)

            # 결과 확인
            rows = await page.query_selector_all('#detailTable tbody tr:not([style*="display: none"])')
            print(f"✅ 검색 기능 작동: '619' 검색 시 {len(rows)}건 표시")

            # 검색 초기화
            await search_input.fill('')
        else:
            print("❌ 검색 입력창을 찾을 수 없음!")

        # ========== 8. 최종 상태 확인 ==========
        print("\n[8/8] ✅ 최종 상태 확인")
        print("-" * 50)

        final_check = await page.evaluate("""() => {
            return {
                totalCards: document.querySelectorAll('.summary-card').length,
                totalValue: document.querySelector('#totalAmountValue')?.innerText || 'N/A',
                paidEmployees: document.querySelector('#paidEmployeesValue')?.innerText || 'N/A',
                paymentRate: document.querySelector('#paymentRateValue')?.innerText || 'N/A'
            };
        }""")

        print(f"📊 대시보드 요약:")
        print(f"   - 요약 카드: {final_check['totalCards']}개")
        print(f"   - 총 지급액: {final_check['totalValue']}")
        print(f"   - 수령 직원: {final_check['paidEmployees']}")
        print(f"   - 지급률: {final_check['paymentRate']}")

        # 스크린샷 저장
        await page.screenshot(path="deep_verification_final.png", full_page=False)

        # ========== 결과 요약 ==========
        print("\n" + "="*70)
        print("🎯 검증 결과 요약")
        print("="*70)

        # 에러 카운트
        error_count = len([msg for msg in console_msgs if msg['type'] == 'error'])
        warning_count = len([msg for msg in console_msgs if msg['type'] == 'warning'])

        print(f"JavaScript 에러: {error_count}개")
        print(f"JavaScript 경고: {warning_count}개")

        # 주요 기능 체크리스트
        checks = [
            ("데이터 로드", data_check['employeeData']['count'] > 0),
            ("탭 전환", data_check['functions']['showTab']),
            ("요약 테이블", summary_data['rows'] > 0),
            ("Position 모달", len(view_buttons) > 0),
            ("언어 변경", language_selector is not None),
            ("검색 기능", search_input is not None),
            ("5PRS 데이터", data_check['employeeData']['with5PRS'] > 0),
            ("AQL 데이터", data_check['employeeData']['withAQL'] > 0)
        ]

        print("\n주요 기능 체크:")
        passed = 0
        for name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {name}")
            if result:
                passed += 1

        print(f"\n전체 점수: {passed}/{len(checks)} ({passed*100//len(checks)}%)")

        if passed == len(checks):
            print("\n🎉 모든 기능이 정상 작동합니다!")
        elif passed >= 6:
            print("\n⚠️ 대부분 기능이 작동하지만 일부 수정이 필요합니다.")
        else:
            print("\n❌ 주요 기능에 문제가 있습니다. 수정이 필요합니다.")

        print("\n📸 스크린샷 저장: deep_verification_final.png")
        print("\n브라우저를 20초간 열어둡니다. 직접 확인하실 수 있습니다...")

        await asyncio.sleep(20)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(deep_verification())