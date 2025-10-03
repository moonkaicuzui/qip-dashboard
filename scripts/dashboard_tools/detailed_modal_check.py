#!/usr/bin/env python3
"""
모달 상세 검증 - 각 섹션별 스크린샷 캡처
"""

from playwright.sync_api import sync_playwright
import time

def detailed_modal_check():
    print("=" * 60)
    print("🔍 모달 상세 검증 시작")
    print("=" * 60)

    dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto(dashboard_path)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 개인별 상세 탭 클릭
        page.click("#tabIndividual")
        time.sleep(2)

        # 첫 번째 직원의 상세보기 클릭
        page.locator("#employeeTableBody tr").first.locator("button.btn-primary").click()
        time.sleep(3)

        # 모달 확인
        modal = page.locator(".modal.show")
        if modal.count() > 0:
            print("\n✅ 모달 열림 성공")

            # 모달 전체 HTML 가져오기
            modal_html = modal.inner_html()

            print("\n📊 모달 구조 분석:")
            print(f"   - 모달 HTML 길이: {len(modal_html)} 문자")

            # 테이블 찾기
            tables = modal.locator("table")
            print(f"   - 테이블 개수: {tables.count()}")

            for i in range(tables.count()):
                table = tables.nth(i)
                headers = table.locator("thead th")
                rows = table.locator("tbody tr")
                print(f"\n   테이블 {i+1}:")
                print(f"      - 헤더 수: {headers.count()}")
                print(f"      - 데이터 행 수: {rows.count()}")

                if headers.count() > 0:
                    print(f"      - 헤더: ", end="")
                    for j in range(min(headers.count(), 5)):
                        print(f"'{headers.nth(j).inner_text().strip()}' ", end="")
                    print()

            # 조건 충족 현황 섹션 찾기
            print("\n🔍 조건 충족 현황 섹션 검색:")

            # 다양한 방법으로 조건 테이블 찾기
            condition_keywords = ["조건", "충족", "실적", "Condition", "Performance"]

            for keyword in condition_keywords:
                elements = modal.locator(f"text={keyword}")
                if elements.count() > 0:
                    print(f"   - '{keyword}' 키워드: {elements.count()}개 발견")

            # h4, h5 태그 찾기
            headings = modal.locator("h4, h5, h6")
            print(f"\n   소제목 ({headings.count()}개):")
            for i in range(headings.count()):
                heading_text = headings.nth(i).inner_text().strip()
                print(f"      {i+1}. {heading_text}")

            # Payment Status 확인
            print("\n💰 Payment Status 섹션:")
            if "✅" in modal_html:
                print("   ✅ 지급 완료 아이콘 발견")
            elif "❌" in modal_html:
                print("   ✅ 미지급 아이콘 발견")

            # 스크린샷 캡처
            print("\n📸 스크린샷 캡처:")

            # 1. 모달 전체
            modal.screenshot(path="output_files/modal_full.png")
            print("   ✅ modal_full.png 저장")

            # 2. 페이지 전체
            page.screenshot(path="output_files/page_with_modal.png", full_page=False)
            print("   ✅ page_with_modal.png 저장")

            # 모달 내용 일부 출력
            print("\n📄 모달 HTML 샘플 (첫 2000자):")
            print(modal_html[:2000])
            print("\n   ...")

            # 20초 대기
            print("\n⏸️  20초간 대기 (수동 확인 시간)...")
            time.sleep(20)
        else:
            print("\n❌ 모달을 찾을 수 없음")

        browser.close()

    print("\n" + "=" * 60)
    print("✅ 검증 완료!")
    print("=" * 60)

if __name__ == "__main__":
    detailed_modal_check()