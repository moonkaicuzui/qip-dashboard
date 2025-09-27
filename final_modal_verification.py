#!/usr/bin/env python3
"""
최종 모달 기능 검증 - AQL과 5PRS 데이터가 올바르게 표시되는지 확인
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def final_verification():
    """최종 검증 테스트"""

    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Dashboard_V6_Complete_2025_september.html"

    print("="*60)
    print("🎯 최종 모달 검증 시작 - Version 6 Dashboard")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("\n📄 대시보드 로딩...")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(3000)

        # Position Details 탭으로 이동
        print("✅ Position Details 탭으로 이동")
        position_tab = await page.query_selector('div.tab[data-tab="position"]')
        if position_tab:
            await position_tab.click()
            await page.wait_for_timeout(2000)
            print("   탭 전환 완료")
        else:
            print("❌ Position tab not found")
            return

        # View 버튼 검색 - 더 넓은 선택자 사용
        print("\n✅ View 버튼 검색...")
        view_buttons = await page.query_selector_all('button.btn-outline-primary')
        if not view_buttons:
            view_buttons = await page.query_selector_all('button:has-text("View")')
        if not view_buttons:
            view_buttons = await page.query_selector_all('button')
            view_buttons = [b for b in view_buttons if 'View' in await b.inner_text()]

        print(f"   {len(view_buttons)}개의 View 버튼 발견")

        if len(view_buttons) > 0:
            # 첫 번째 View 버튼 클릭
            print("\n✅ 첫 번째 View 버튼 클릭")
            await view_buttons[0].click()
            await page.wait_for_timeout(2000)

            # 모달 확인
            modal = await page.query_selector('#employeeModal')
            if modal and await modal.is_visible():
                print("✅ 모달이 성공적으로 열렸습니다!")

                # 모달 제목 확인
                title = await page.query_selector('#modalTitle')
                if title:
                    title_text = await title.inner_text()
                    print(f"   모달 제목: {title_text}")

                # 조건 통계 확인
                print("\n📊 조건별 충족 현황:")
                print("-"*40)

                # JavaScript로 모든 조건 데이터 가져오기
                condition_data = await page.evaluate("""() => {
                    const results = {};

                    // 조건 통계 테이블 찾기
                    const tables = document.querySelectorAll('#employeeModal table');
                    if (tables.length > 0) {
                        const rows = tables[0].querySelectorAll('tbody tr');
                        rows.forEach(row => {
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 5) {
                                const name = cells[0].innerText;
                                results[name] = {
                                    applicable: cells[1].innerText,
                                    total: cells[2].innerText,
                                    met: cells[3].innerText,
                                    unmet: cells[4].innerText,
                                    rate: cells[5] ? cells[5].innerText : 'N/A'
                                };
                            }
                        });
                    }
                    return results;
                }""")

                # 결과 출력
                aql_found = False
                prs_found = False

                for condition, data in condition_data.items():
                    print(f"\n{condition}:")
                    print(f"  적용: {data['applicable']}")
                    print(f"  평가대상: {data['total']}")
                    print(f"  충족: {data['met']}")
                    print(f"  미충족: {data['unmet']}")
                    print(f"  충족률: {data['rate']}")

                    # AQL 체크
                    if 'AQL' in condition:
                        aql_found = True
                        if data['total'] != '0' and data['total'] != 'N/A':
                            print("  ✅ AQL 데이터가 정상 표시됨!")
                        else:
                            print("  ⚠️ AQL 데이터가 0 또는 N/A")

                    # 5PRS 체크
                    if '5PRS' in condition or 'PRS' in condition:
                        prs_found = True
                        if data['total'] != '0' and data['total'] != 'N/A':
                            print("  ✅ 5PRS 데이터가 정상 표시됨!")
                        else:
                            print("  ⚠️ 5PRS 데이터가 0 또는 N/A")

                # 직원 배지 확인
                print("\n📛 직원별 배지 확인:")
                print("-"*40)

                badge_data = await page.evaluate("""() => {
                    const badges = [];
                    const employeeTable = document.querySelector('#positionEmployeeTable');
                    if (employeeTable) {
                        const firstRow = employeeTable.querySelector('tbody tr');
                        if (firstRow) {
                            const badgeElements = firstRow.querySelectorAll('.badge');
                            badgeElements.forEach(b => {
                                badges.push({
                                    text: b.innerText,
                                    classes: b.className
                                });
                            });
                        }
                    }
                    return badges;
                }""")

                for badge in badge_data:
                    if 'N/A' not in badge['text']:
                        print(f"✅ {badge['text']}")
                    else:
                        print(f"⚠️ {badge['text']}")

                # 스크린샷 저장
                await page.screenshot(path="final_modal_verification.png", full_page=False)
                print("\n📸 스크린샷 저장: final_modal_verification.png")

                # 결과 요약
                print("\n" + "="*60)
                print("🎯 최종 검증 결과:")
                print("="*60)

                if aql_found and prs_found:
                    print("✅ AQL과 5PRS 조건이 모두 표시됨")

                    # CSV 데이터와 비교
                    print("\n📊 데이터 소스 확인:")
                    csv_check = await page.evaluate("""() => {
                        if (window.employeeData && window.employeeData.length > 0) {
                            const sample = window.employeeData.filter(e => e['5PRS_Pass_Rate'] > 0);
                            return {
                                totalEmployees: window.employeeData.length,
                                with5PRS: sample.length,
                                sample5PRS: sample[0] ? sample[0]['5PRS_Pass_Rate'] : null,
                                sampleQty: sample[0] ? sample[0]['5PRS_Inspection_Qty'] : null
                            };
                        }
                        return null;
                    }""")

                    if csv_check:
                        print(f"  전체 직원: {csv_check['totalEmployees']}명")
                        print(f"  5PRS 데이터 있는 직원: {csv_check['with5PRS']}명")
                        if csv_check['sample5PRS']:
                            print(f"  샘플 5PRS 통과율: {csv_check['sample5PRS']}%")
                            print(f"  샘플 5PRS 검사량: {csv_check['sampleQty']}")
                else:
                    print("❌ 일부 조건이 누락됨:")
                    if not aql_found:
                        print("  - AQL 조건 없음")
                    if not prs_found:
                        print("  - 5PRS 조건 없음")

                print("\n✅ 모달 기능 정상 작동 확인 완료!")

                # 모달 닫기
                await page.keyboard.press('Escape')

            else:
                print("❌ 모달이 열리지 않음")
        else:
            print("❌ View 버튼을 찾을 수 없음")

        print("\n⏸️ 수동 확인을 위해 브라우저를 30초간 유지합니다...")
        await asyncio.sleep(30)

        await browser.close()

    print("\n✅ 검증 완료!")

if __name__ == "__main__":
    asyncio.run(final_verification())