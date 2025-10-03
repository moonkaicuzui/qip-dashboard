#!/usr/bin/env python3
"""
JavaScript를 사용해서 직접 특정 직원의 모달 열기
"""

from playwright.sync_api import sync_playwright
import time

def find_and_open_modal():
    print("=" * 60)
    print("🔍 JavaScript로 직접 모달 열기: 622020174")
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

        # JavaScript로 직접 showEmployeeDetail 함수 호출
        print("\n📋 JavaScript로 모달 열기...")

        # 먼저 해당 직원이 employeeData에 있는지 확인
        employee_exists = page.evaluate("""
            () => {
                const empId = '622020174';
                const emp = employeeData.find(e =>
                    String(e.emp_no) === empId ||
                    String(e['Employee No']) === empId
                );
                if (emp) {
                    return {
                        found: true,
                        name: emp.name || emp['Full Name'],
                        position: emp.position || emp['QIP POSITION 1ST NAME'],
                        type: emp.type || emp['ROLE TYPE STD']
                    };
                }
                return { found: false };
            }
        """)

        print(f"\n직원 데이터 검색 결과: {employee_exists}")

        if employee_exists.get('found'):
            print(f"   ✅ 직원 발견:")
            print(f"      이름: {employee_exists.get('name')}")
            print(f"      직급: {employee_exists.get('position')}")
            print(f"      Type: {employee_exists.get('type')}")

            # showEmployeeDetail 함수 직접 호출
            print("\n📋 showEmployeeDetail('622020174') 호출...")

            page.evaluate("showEmployeeDetail('622020174')")
            time.sleep(3)

            # 모달 확인
            modal = page.locator(".modal.show")
            if modal.count() > 0:
                print("✅ 모달 열림 성공\n")

                # 모달 제목
                modal_title = modal.locator(".modal-title")
                if modal_title.count() > 0:
                    print(f"모달 제목: {modal_title.inner_text()}\n")

                # 조건 테이블 찾기
                tables = modal.locator("table")

                for table_idx in range(tables.count()):
                    table = tables.nth(table_idx)
                    headers = table.locator("thead th")

                    # Performance 컬럼이 있는 테이블 찾기
                    has_performance = False
                    for h_idx in range(headers.count()):
                        header_text = headers.nth(h_idx).inner_text().strip()
                        if "실적" in header_text or "Performance" in header_text:
                            has_performance = True
                            break

                    if has_performance:
                        print(f"📊 조건 충족 현황:")
                        print("=" * 100)

                        rows = table.locator("tbody tr")
                        fail_with_text_only = []

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
                                print(f"      실적: [{performance}]")
                                print(f"      결과: {result}")

                                # FAIL이면서 "Fail" 텍스트만 있는지 체크
                                if icon == "❌" and performance.lower() == "fail":
                                    fail_with_text_only.append({
                                        'num': cond_num,
                                        'name': cond_name
                                    })
                                    print(f"      ⚠️  WARNING: 'Fail' 텍스트만 표시! 실제 데이터 필요")

                        print("\n" + "=" * 100)

                        if fail_with_text_only:
                            print(f"\n❌ 문제 발견: {len(fail_with_text_only)}개 조건에서 'Fail' 텍스트만 표시됨:")
                            for item in fail_with_text_only:
                                print(f"   - 조건 {item['num']}: {item['name']}")
                        else:
                            print("\n✅ 모든 조건에 실제 데이터가 표시됨!")

                        break

                # 스크린샷
                print("\n📸 스크린샷 저장...")
                modal.screenshot(path="output_files/employee_622020174_modal.png")
                page.screenshot(path="output_files/employee_622020174_page.png")
                print("   ✅ 저장 완료")

                # 대기
                print("\n⏸️  20초 대기...")
                time.sleep(20)

            else:
                print("❌ 모달이 열리지 않음")
        else:
            print("❌ 직원 데이터를 찾을 수 없음")

        browser.close()

    print("\n" + "=" * 60)
    print("✅ 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    find_and_open_modal()