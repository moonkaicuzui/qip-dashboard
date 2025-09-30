#!/usr/bin/env python3
"""
특정 직원(622020174)의 모달 검증 - FAIL 케이스 확인
"""

from playwright.sync_api import sync_playwright
import time

def verify_specific_employee():
    print("=" * 60)
    print("🔍 특정 직원 모달 검증: 622020174")
    print("=" * 60)

    dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto(dashboard_path)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 개인별 상세 탭
        page.click("#tabIndividual")
        time.sleep(2)

        # 검색창에 직원번호 입력
        print("\n📋 직원 622020174 검색 중...")
        search_input = page.locator("#searchInput")
        search_input.fill("622020174")
        time.sleep(2)

        # 필터된 테이블 확인
        table_body = page.locator("#employeeTableBody")
        visible_rows = table_body.locator("tr:visible")
        total_rows = table_body.locator("tr")

        print(f"   전체 행: {total_rows.count()}개")
        print(f"   보이는 행: {visible_rows.count()}개")

        if visible_rows.count() > 0:
            # 첫 번째 보이는 행의 정보 출력
            first_row = visible_rows.first
            cells = first_row.locator("td")

            emp_no = cells.nth(0).inner_text().strip() if cells.count() > 0 else "N/A"
            emp_name = cells.nth(1).inner_text().strip() if cells.count() > 1 else "N/A"

            print(f"\n✅ 검색된 직원:")
            print(f"   - 사번: {emp_no}")
            print(f"   - 이름: {emp_name}")

            # 상세보기 버튼 클릭
            detail_button = first_row.locator("button.btn-primary")
            if detail_button.count() > 0:
                print("\n📋 상세보기 버튼 클릭...")
                detail_button.click()
                time.sleep(3)

                # 모달 확인
                modal = page.locator(".modal.show")
                if modal.count() > 0:
                    print("✅ 모달 열림 성공\n")

                    # 모달 제목 확인
                    modal_title = modal.locator(".modal-title")
                    if modal_title.count() > 0:
                        title_text = modal_title.inner_text()
                        print(f"모달 제목: {title_text}\n")

                    # 조건 테이블 찾기
                    tables = modal.locator("table")
                    print(f"테이블 수: {tables.count()}")

                    if tables.count() > 0:
                        # 조건 충족 현황 테이블 (일반적으로 첫 번째 또는 두 번째)
                        for table_idx in range(tables.count()):
                            table = tables.nth(table_idx)
                            headers = table.locator("thead th")

                            # "실적" 또는 "Performance" 헤더가 있는 테이블 찾기
                            has_performance = False
                            for h_idx in range(headers.count()):
                                header_text = headers.nth(h_idx).inner_text().strip()
                                if "실적" in header_text or "Performance" in header_text:
                                    has_performance = True
                                    break

                            if has_performance:
                                print(f"\n📊 조건 충족 현황 테이블 (테이블 #{table_idx + 1}):")
                                print("=" * 80)

                                rows = table.locator("tbody tr")
                                for i in range(rows.count()):
                                    row = rows.nth(i)
                                    cells = row.locator("td")

                                    if cells.count() >= 4:
                                        cond_num = cells.nth(0).inner_text().strip()
                                        cond_name = cells.nth(1).inner_text().strip()
                                        performance = cells.nth(2).inner_text().strip()
                                        result = cells.nth(3).inner_text().strip()

                                        # 결과 아이콘
                                        if "Met" in result or "충족" in result:
                                            icon = "✅"
                                        else:
                                            icon = "❌"

                                        print(f"{icon} 조건 {cond_num}: {cond_name}")
                                        print(f"   실적: {performance}")
                                        print(f"   결과: {result}")

                                        # "Fail" 텍스트 체크
                                        if performance.lower() == "fail":
                                            print(f"   ⚠️  WARNING: 'Fail' 텍스트만 표시됨! 실제 데이터가 필요합니다.")

                                break

                    # 스크린샷
                    print("\n📸 스크린샷 저장...")
                    modal.screenshot(path="output_files/specific_employee_622020174.png")
                    print("   ✅ 저장: output_files/specific_employee_622020174.png")

                    # 대기
                    print("\n⏸️  20초 대기 (수동 확인)...")
                    time.sleep(20)

                else:
                    print("❌ 모달이 열리지 않음")
            else:
                print("❌ 상세보기 버튼을 찾을 수 없음")
        else:
            print("❌ 검색 결과가 없습니다")

        browser.close()

    print("\n" + "=" * 60)
    print("✅ 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    verify_specific_employee()