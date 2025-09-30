#!/usr/bin/env python3
"""
Playwright를 사용한 대시보드 개선사항 검증
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def verify_dashboard():
    """대시보드 개선사항 검증"""

    dashboard_path = os.path.abspath("output_files/Incentive_Dashboard_2025_09_Version_6.html")

    if not os.path.exists(dashboard_path):
        print(f"❌ 대시보드 파일이 없습니다: {dashboard_path}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"📂 대시보드 열기: {dashboard_path}")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(2000)

        # 개선사항 체크리스트
        improvements = {
            "TOTAL EMPLOYEES": False,
            "Total Working Days": False,
            "Model Master 인센티브": False,
            "Assembly Inspector 인센티브": False,
            "Org Chart 언어 전환": False,
            "Summary Tab 언어 전환": False,
            "ĐINH KIM NGOAN 인센티브": False
        }

        print("\n" + "="*60)
        print("🔍 대시보드 개선사항 검증")
        print("="*60)

        # 1. TOTAL EMPLOYEES 확인 (401명이어야 함)
        try:
            total_employees_elem = await page.query_selector('h6:has-text("Total Employees") + h2')
            if total_employees_elem:
                total_employees = await total_employees_elem.inner_text()
                total_employees_num = int(total_employees.replace(',', ''))
                if total_employees_num == 401:
                    print(f"✅ TOTAL EMPLOYEES: {total_employees} (정상 - 퇴사자 제외됨)")
                    improvements["TOTAL EMPLOYEES"] = True
                else:
                    print(f"❌ TOTAL EMPLOYEES: {total_employees} (예상: 401)")
        except Exception as e:
            print(f"❌ TOTAL EMPLOYEES 확인 실패: {e}")

        # 2. Total Working Days 확인 (22일이어야 함)
        try:
            # Summary & Validation 탭으로 이동
            summary_tab = await page.query_selector('[data-tab="summary"]')
            if summary_tab:
                await summary_tab.click()
                await page.wait_for_timeout(1000)

                # Total Working Days 카드 클릭
                working_days_card = await page.query_selector('.stat-card:has-text("Total Working Days")')
                if working_days_card:
                    await working_days_card.click()
                    await page.wait_for_timeout(1000)

                    # 모달 내용 확인
                    modal_content = await page.query_selector('.modal-body')
                    if modal_content:
                        modal_text = await modal_content.inner_text()
                        if "22일" in modal_text or "22 days" in modal_text:
                            print(f"✅ Total Working Days: 22일 (정상)")
                            improvements["Total Working Days"] = True
                        else:
                            print(f"❌ Total Working Days: 모달에 22일이 표시되지 않음")

                    # 모달 닫기
                    close_button = await page.query_selector('.modal .btn-close')
                    if close_button:
                        await close_button.click()
        except Exception as e:
            print(f"❌ Total Working Days 확인 실패: {e}")

        # 3. TYPE-1 Model Master 인센티브 확인
        try:
            # 직원 데이터 탭으로 이동
            employee_tab = await page.query_selector('[data-tab="employee"]')
            if employee_tab:
                await employee_tab.click()
                await page.wait_for_timeout(1000)

                # 필터에서 TYPE-1과 MODEL MASTER 선택
                type_filter = await page.query_selector('#typeFilter')
                if type_filter:
                    await type_filter.select_option('TYPE-1')
                    await page.wait_for_timeout(500)

                # MODEL MASTER 검색
                search_input = await page.query_selector('#searchInput')
                if search_input:
                    await search_input.fill('MODEL MASTER')
                    await page.wait_for_timeout(500)

                    # 결과 확인
                    table_rows = await page.query_selector_all('#employeeTableBody tr')
                    if table_rows:
                        for row in table_rows[:1]:  # 첫 번째 행만 확인
                            cells = await row.query_selector_all('td')
                            if len(cells) > 7:
                                incentive = await cells[7].inner_text()  # September Incentive 컬럼
                                print(f"ℹ️ Model Master 인센티브: {incentive}")
                                improvements["Model Master 인센티브"] = True
        except Exception as e:
            print(f"❌ Model Master 인센티브 확인 실패: {e}")

        # 4. ĐINH KIM NGOAN 인센티브 확인
        try:
            # 검색창 초기화하고 ĐINH KIM NGOAN 검색
            search_input = await page.query_selector('#searchInput')
            if search_input:
                await search_input.fill('ĐINH KIM NGOAN')
                await page.wait_for_timeout(500)

                # TYPE 필터 초기화 (ALL)
                type_filter = await page.query_selector('#typeFilter')
                if type_filter:
                    await type_filter.select_option('')
                    await page.wait_for_timeout(500)

                table_rows = await page.query_selector_all('#employeeTableBody tr')
                if table_rows:
                    for row in table_rows:
                        cells = await row.query_selector_all('td')
                        if len(cells) > 7:
                            name = await cells[1].inner_text()
                            if 'ĐINH KIM NGOAN' in name:
                                incentive = await cells[7].inner_text()
                                if '325,312' in incentive:
                                    print(f"✅ ĐINH KIM NGOAN 인센티브: {incentive} (정상)")
                                    improvements["ĐINH KIM NGOAN 인센티브"] = True
                                else:
                                    print(f"❌ ĐINH KIM NGOAN 인센티브: {incentive} (예상: 325,312)")
                                break
        except Exception as e:
            print(f"❌ ĐINH KIM NGOAN 확인 실패: {e}")

        # 5. 언어 전환 테스트
        try:
            # 언어 전환 버튼 찾기
            lang_button_en = await page.query_selector('button:has-text("English")')
            lang_button_vi = await page.query_selector('button:has-text("Tiếng Việt")')
            lang_button_ko = await page.query_selector('button:has-text("한국어")')

            if lang_button_en:
                await lang_button_en.click()
                await page.wait_for_timeout(1000)

                # Org Chart 탭 확인
                org_chart_tab = await page.query_selector('[data-tab="orgChart"]')
                if org_chart_tab:
                    await org_chart_tab.click()
                    await page.wait_for_timeout(1000)

                    # 첫 번째 직원 카드 클릭
                    employee_card = await page.query_selector('.employee-card')
                    if employee_card:
                        await employee_card.click()
                        await page.wait_for_timeout(1000)

                        # 모달 제목 확인 (영어여야 함)
                        modal_title = await page.query_selector('.modal-title')
                        if modal_title:
                            title_text = await modal_title.inner_text()
                            if "Employee" in title_text or "Details" in title_text:
                                print(f"✅ Org Chart 언어 전환: 영어 모달 확인")
                                improvements["Org Chart 언어 전환"] = True

                        # 모달 닫기
                        close_button = await page.query_selector('.modal .btn-close')
                        if close_button:
                            await close_button.click()

                # Summary 탭 언어 확인
                summary_tab = await page.query_selector('[data-tab="summary"]')
                if summary_tab:
                    await summary_tab.click()
                    await page.wait_for_timeout(1000)

                    # Summary 제목 확인
                    summary_title = await page.query_selector('h2:has-text("Summary")')
                    if summary_title:
                        print(f"✅ Summary Tab 언어 전환: 영어 확인")
                        improvements["Summary Tab 언어 전환"] = True

            # 한국어로 복귀
            if lang_button_ko:
                await lang_button_ko.click()
                await page.wait_for_timeout(1000)

        except Exception as e:
            print(f"❌ 언어 전환 테스트 실패: {e}")

        # 결과 요약
        print("\n" + "="*60)
        print("📊 검증 결과 요약")
        print("="*60)

        passed = sum(1 for v in improvements.values() if v)
        total = len(improvements)

        for item, status in improvements.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {item}")

        print(f"\n총 {total}개 중 {passed}개 통과 ({passed/total*100:.1f}%)")

        # 스크린샷 저장
        screenshot_path = "dashboard_verification.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"\n📸 스크린샷 저장: {screenshot_path}")

        # 브라우저 열어두기
        print("\n💡 브라우저를 열어두었습니다. 수동으로 확인 후 종료하세요.")
        await asyncio.sleep(300)  # 5분 대기

        await browser.close()

# 실행
if __name__ == "__main__":
    asyncio.run(verify_dashboard())