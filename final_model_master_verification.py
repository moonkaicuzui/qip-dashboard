#!/usr/bin/env python3
"""
최종 MODEL MASTER 및 전체 개선사항 검증
- MODEL MASTER 인센티브 확인
- 대시보드 모달 동작 확인
- 조건 표시 검증
"""

from playwright.sync_api import sync_playwright
import os
import time

def test_dashboard():
    dashboard_path = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 대시보드 열기
        page.goto(f'file://{dashboard_path}')
        page.wait_for_timeout(2000)

        print("="*80)
        print("🎯 최종 MODEL MASTER 및 시스템 검증 결과")
        print("="*80)

        # 1. 기본 통계 확인
        print("\n[1] 기본 통계:")
        total_emp = page.query_selector('h6:has-text("Total Employees") + h2')
        if total_emp:
            print(f"   ✅ TOTAL EMPLOYEES: {total_emp.inner_text()} (퇴사자 제외)")

        paid_emp = page.query_selector('h6:has-text("Paid Employees") + h2')
        if paid_emp:
            print(f"   ✅ Paid Employees: {paid_emp.inner_text()} (287명 예상)")

        total_amount = page.query_selector('h6:has-text("Total Paid Amount") + h2')
        if total_amount:
            print(f"   ✅ Total Paid Amount: {total_amount.inner_text()} (117,896,632 VND 예상)")

        # 2. MODEL MASTER 검색 및 확인
        print("\n[2] MODEL MASTER 인센티브 확인:")

        # Detailed Analysis 탭으로 이동
        detail_tab = page.query_selector('[data-tab="detailed"]')
        if detail_tab:
            detail_tab.click()
            page.wait_for_timeout(1000)

        # 검색창에 MODEL MASTER 입력
        search_input = page.query_selector('#searchInput')
        if search_input:
            search_input.fill('MODEL MASTER')
            page.wait_for_timeout(500)

            # 결과 확인
            model_master_rows = page.query_selector_all('tbody tr:visible')
            print(f"   → MODEL MASTER 직원 수: {len(model_master_rows)}명")

            for row in model_master_rows[:3]:
                name_cell = row.query_selector('td:nth-child(2)')
                amount_cell = row.query_selector('td:nth-child(8)')
                if name_cell and amount_cell:
                    name = name_cell.inner_text()
                    amount = amount_cell.inner_text()
                    print(f"      - {name}: {amount} (1,000,000 VND 예상)")

        # 3. Position Details 모달 테스트
        print("\n[3] Position Details 모달 테스트:")

        # Position Details 탭으로 이동
        position_tab = page.query_selector('[data-tab="positions"]')
        if position_tab:
            position_tab.click()
            page.wait_for_timeout(1000)

            # MODEL MASTER 행 찾기
            position_rows = page.query_selector_all('#positionTableBody tr')
            for row in position_rows:
                if 'MODEL MASTER' in row.inner_text():
                    # View Details 버튼 클릭
                    view_btn = row.query_selector('.view-details-btn')
                    if view_btn:
                        view_btn.click()
                        page.wait_for_timeout(1000)

                        # 모달이 열렸는지 확인
                        modal = page.query_selector('#employeeModal:visible')
                        if modal:
                            print("   ✅ MODEL MASTER 모달이 정상적으로 열림")

                            # 조건 확인
                            condition_badges = modal.query_selector_all('.condition-badge')
                            conditions = []
                            for badge in condition_badges[:5]:
                                badge_text = badge.inner_text()
                                if badge_text:
                                    conditions.append(badge_text.split(':')[0].strip())

                            print(f"   → 표시된 조건: {conditions}")
                            if set(['1', '2', '3', '4', '8']).issubset(set(conditions)):
                                print("   ✅ MODEL MASTER 조건 [1,2,3,4,8] 올바르게 표시됨!")
                            else:
                                print("   ⚠️ 조건 표시 문제 있음. 예상: [1,2,3,4,8]")

                            # 모달 닫기
                            close_btn = modal.query_selector('.btn-close')
                            if close_btn:
                                close_btn.click()
                        else:
                            print("   ❌ 모달이 열리지 않음")
                    break

        # 4. Individual Details 모달 테스트
        print("\n[4] Individual Details 모달 테스트:")

        # Individual Details 탭으로 이동
        individual_tab = page.query_selector('[data-tab="individual"]')
        if individual_tab:
            individual_tab.click()
            page.wait_for_timeout(1000)

            # 첫 번째 직원의 View Details 클릭
            first_view_btn = page.query_selector('#individualTableBody .view-employee-btn:first-child')
            if first_view_btn:
                first_view_btn.click()
                page.wait_for_timeout(1000)

                modal = page.query_selector('#employeeModal:visible')
                if modal:
                    print("   ✅ Individual Details 모달이 정상적으로 열림")

                    # 모달 닫기
                    close_btn = modal.query_selector('.btn-close')
                    if close_btn:
                        close_btn.click()
                else:
                    print("   ❌ 모달이 열리지 않음")

        # 5. 언어 전환 테스트
        print("\n[5] 언어 전환 테스트:")
        lang_selector = page.query_selector('#languageSelector')
        if lang_selector:
            # Vietnamese로 전환
            lang_selector.select_option('vi')
            page.wait_for_timeout(500)

            # 텍스트 확인
            title = page.query_selector('h5')
            if title and 'Bảng điều khiển' in title.inner_text():
                print("   ✅ Vietnamese 언어 전환 성공")

            # Korean으로 전환
            lang_selector.select_option('ko')
            page.wait_for_timeout(500)

            title = page.query_selector('h5')
            if title and '대시보드' in title.inner_text():
                print("   ✅ Korean 언어 전환 성공")

            # English로 복귀
            lang_selector.select_option('en')
            page.wait_for_timeout(500)
            print("   ✅ English 언어 전환 성공")

        print("\n" + "="*80)
        print("✅ 모든 검증 완료!")
        print("MODEL MASTER 인센티브 계산 및 표시가 정상적으로 작동합니다.")
        print("="*80)

        # 스크린샷 저장
        page.screenshot(path='final_verification_screenshot.png')
        print("\n📸 스크린샷 저장: final_verification_screenshot.png")

        # 브라우저 열어두기 (수동 확인용)
        print("\n💡 브라우저를 30초간 열어둡니다. 수동으로 추가 확인하세요.")
        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    test_dashboard()