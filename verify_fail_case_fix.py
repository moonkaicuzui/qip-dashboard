#!/usr/bin/env python3
"""
FAIL 케이스 실제 데이터 표시 검증
특정 직원(622020174)의 모달을 열어서 확인
"""

from playwright.sync_api import sync_playwright
import time

def verify_fail_case():
    print("=" * 60)
    print("🔍 FAIL 케이스 실제 데이터 표시 검증")
    print("=" * 60)

    dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"
    target_emp_id = "622020174"  # NGUYỄN NGỌC BÍCH THỦY

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto(dashboard_path)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        print(f"\n📋 대상 직원: {target_emp_id}")

        # 개인별 상세 탭 클릭
        page.click("#tabIndividual")
        time.sleep(2)

        # 검색창에 직원번호 입력
        search_input = page.locator("#searchInput")
        search_input.fill(target_emp_id)
        time.sleep(1)

        # 해당 직원의 행 찾기
        table_body = page.locator("#employeeTableBody")
        rows = table_body.locator("tr:visible")

        if rows.count() > 0:
            print(f"✅ 직원 {target_emp_id} 발견")

            # 첫 번째 (유일한) 행의 상세보기 클릭
            detail_button = rows.first.locator("button.btn-primary")
            detail_button.click()
            time.sleep(3)

            # 모달 확인
            modal = page.locator(".modal.show")
            if modal.count() > 0:
                print("\n✅ 모달 열림 성공")

                # 조건 테이블 찾기
                tables = modal.locator("table")
                if tables.count() > 0:
                    conditions_table = tables.first
                    rows = conditions_table.locator("tbody tr")

                    print(f"\n📊 조건 충족 현황 ({rows.count()}개 조건):")
                    print("=" * 80)

                    fail_with_actual_data = []
                    fail_with_text = []

                    for i in range(rows.count()):
                        row = rows.nth(i)
                        cells = row.locator("td")

                        if cells.count() >= 4:
                            cond_num = cells.nth(0).inner_text().strip()
                            cond_name = cells.nth(1).inner_text().strip()
                            performance = cells.nth(2).inner_text().strip()
                            result = cells.nth(3).inner_text().strip()

                            status = "✅" if "Met" in result or "충족" in result else "❌"

                            print(f"{status} 조건 {cond_num}: {cond_name}")
                            print(f"   Performance: {performance}")
                            print(f"   Result: {result}")

                            # FAIL이면서 실제 데이터가 있는지 확인
                            if status == "❌":
                                # 숫자가 포함되어 있으면 실제 데이터
                                if any(char.isdigit() for char in performance):
                                    fail_with_actual_data.append({
                                        'num': cond_num,
                                        'name': cond_name,
                                        'value': performance
                                    })
                                # Fail/Pass 같은 텍스트만 있으면 문제
                                elif performance.lower() in ['fail', 'pass', 'no', 'yes']:
                                    fail_with_text.append({
                                        'num': cond_num,
                                        'name': cond_name,
                                        'value': performance
                                    })

                    print("\n" + "=" * 80)
                    print("📈 검증 결과:")
                    print("=" * 80)

                    if fail_with_actual_data:
                        print(f"\n✅ FAIL이지만 실제 데이터 표시된 조건 ({len(fail_with_actual_data)}개):")
                        for item in fail_with_actual_data:
                            print(f"   - 조건 {item['num']} ({item['name']}): {item['value']}")

                    if fail_with_text:
                        print(f"\n❌ FAIL이면서 텍스트만 표시된 조건 ({len(fail_with_text)}개):")
                        for item in fail_with_text:
                            print(f"   - 조건 {item['num']} ({item['name']}): {item['value']}")
                    else:
                        print("\n✅ 모든 FAIL 조건에 실제 데이터가 표시됨!")

                    # 스크린샷
                    print("\n📸 스크린샷 저장 중...")
                    modal.screenshot(path="output_files/fail_case_verification.png")
                    print("   ✅ 저장: output_files/fail_case_verification.png")

                    # 대기
                    print("\n⏸️  15초 대기 (수동 확인 시간)...")
                    time.sleep(15)

                else:
                    print("\n❌ 조건 테이블을 찾을 수 없음")
            else:
                print("\n❌ 모달이 열리지 않음")
        else:
            print(f"\n❌ 직원 {target_emp_id}를 찾을 수 없음")

        browser.close()

    print("\n" + "=" * 60)
    print("✅ 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    verify_fail_case()