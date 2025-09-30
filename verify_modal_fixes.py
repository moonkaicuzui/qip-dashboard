#!/usr/bin/env python3
"""
개인별 상세 모달 개선사항 검증 스크립트
- 소수점 첫째자리까지만 표시
- 실적 컬럼에 실제 데이터 표시
- Payment Status 아이콘 정상 표시
"""

from playwright.sync_api import sync_playwright
import time
import sys

def verify_modal_improvements():
    print("=" * 60)
    print("🔍 개인별 상세 모달 개선사항 검증 시작")
    print("=" * 60)

    dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    with sync_playwright() as p:
        print("\n1️⃣ 브라우저 실행 중...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        print("2️⃣ 대시보드 로딩 중...")
        page.goto(dashboard_path)
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        print("3️⃣ 개인별 상세 탭으로 이동 중...")
        detail_tab = page.locator("#tabIndividual")
        if detail_tab.count() > 0:
            print("   ✅ 개인별 상세 탭 발견")
            detail_tab.click()
            time.sleep(3)
        else:
            print("   ❌ 개인별 상세 탭을 찾을 수 없음")
            browser.close()
            return

        print("4️⃣ 직원 테이블 확인 중...")
        employee_table = page.locator("#employeeTableBody")
        if employee_table.count() > 0:
            rows = employee_table.locator("tr")
            print(f"   ✅ 직원 테이블 발견 ({rows.count()}개 행)")

            if rows.count() > 0:
                print("\n5️⃣ 첫 번째 직원의 상세보기 버튼 찾기...")
                first_row = rows.first
                detail_button = first_row.locator("button.btn-primary")

                if detail_button.count() > 0:
                    button_text = detail_button.inner_text()
                    print(f"   ✅ 상세보기 버튼 발견: '{button_text}'")

                    print("\n6️⃣ 모달 열기...")
                    detail_button.click()
                    time.sleep(3)

                    # 모달 확인
                    print("\n7️⃣ 모달 확인 중...")
                    modal = page.locator(".modal.show")
                    if modal.count() > 0:
                        print("   ✅ 모달이 정상적으로 표시됨")

                        print("\n" + "=" * 60)
                        print("📋 확인 사항:")
                        print("=" * 60)

                        # 조건 충족 현황 테이블 찾기
                        modal_tables = modal.locator("table")
                        table_count = modal_tables.count()
                        print(f"\n   모달 내 테이블 수: {table_count}")

                        if table_count >= 2:
                            conditions_table = modal_tables.nth(1)  # 두 번째 테이블

                            print("\n📊 조건 충족 현황 테이블 분석:")

                            rows = conditions_table.locator("tbody tr")
                            row_count = rows.count()
                            print(f"   조건 행 수: {row_count}")

                            decimal_issues = []
                            pass_fail_issues = []

                            for i in range(row_count):
                                row = rows.nth(i)
                                cells = row.locator("td")

                                if cells.count() >= 4:
                                    condition_name = cells.nth(1).inner_text().strip()
                                    actual_value = cells.nth(2).inner_text().strip()

                                    print(f"\n   조건 {i+1}: {condition_name}")
                                    print(f"      실적: {actual_value}")

                                    # 소수점 검사
                                    if '.' in actual_value:
                                        parts = actual_value.split('.')
                                        if len(parts) == 2:
                                            decimal_part = parts[1].rstrip('%일건족')
                                            if len(decimal_part) > 1:
                                                decimal_issues.append(f"  ⚠️  {condition_name}: {actual_value} (소수점 {len(decimal_part)}자리)")

                                    # "통과" 또는 "실패" 텍스트 검사
                                    if actual_value in ['통과', '실패', 'PASS', 'FAIL']:
                                        if '연속' not in condition_name and '팀' not in condition_name and '구역' not in condition_name:
                                            pass_fail_issues.append(f"  ⚠️  {condition_name}: {actual_value}")

                            print("\n" + "=" * 60)
                            if not decimal_issues:
                                print("✅ 소수점 첫째자리까지만 표시 - 정상")
                            else:
                                print("❌ 소수점 문제 발견:")
                                for issue in decimal_issues:
                                    print(issue)

                            if not pass_fail_issues:
                                print("✅ 실적 데이터 표시 - 정상")
                            else:
                                print("❌ 통과/실패 텍스트 발견:")
                                for issue in pass_fail_issues:
                                    print(issue)

                        # Payment Status 섹션 확인
                        print("\n" + "=" * 60)
                        print("💰 Payment Status 섹션 분석:")
                        print("=" * 60)

                        # 전체 모달 HTML에서 Payment Status 찾기
                        modal_html = modal.inner_html()

                        if "Payment Status" in modal_html or "지급 상태" in modal_html:
                            # 이모지 확인
                            if "✅" in modal_html:
                                print("   ✅ 지급 완료 아이콘 (✅) 발견")
                            elif "❌" in modal_html:
                                print("   ✅ 미지급 아이콘 (❌) 발견")
                            else:
                                print("   ⚠️  이모지 아이콘을 찾을 수 없음")
                        else:
                            print("   ⚠️  Payment Status 섹션을 찾을 수 없음")

                        print("\n" + "=" * 60)
                        print("📸 스크린샷 촬영 중...")
                        page.screenshot(path="output_files/modal_verification_screenshot.png", full_page=True)
                        print("   ✅ 저장됨: output_files/modal_verification_screenshot.png")

                        print("\n⏸️  10초간 대기 중 (수동 확인 시간)...")
                        time.sleep(10)

                    else:
                        print("   ❌ 모달이 표시되지 않음")
                else:
                    print("   ❌ 상세보기 버튼을 찾을 수 없음")
            else:
                print("   ❌ 테이블에 행이 없음")
        else:
            print("   ❌ 직원 테이블을 찾을 수 없음")

        print("\n8️⃣ 브라우저 종료 중...")
        browser.close()

    print("\n" + "=" * 60)
    print("✅ 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        verify_modal_improvements()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)