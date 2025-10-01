#!/usr/bin/env python3
"""
근무일 현황 카드 개선사항 검증 스크립트
"""
import sys
from playwright.sync_api import sync_playwright
import time

def test_working_days_modal():
    """근무일 현황 모달 테스트"""
    print("📊 근무일 현황 카드 검증 시작...")

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 대시보드 열기
        dashboard_path = f"file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"
        print(f"📂 대시보드 로드: {dashboard_path}")
        page.goto(dashboard_path)

        # 페이지 로드 대기
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # 요약 및 시스템 검증 탭 클릭
        print("🔍 요약 및 시스템 검증 탭 이동...")
        page.click('a[href="#validation"]')
        time.sleep(1)

        # 총 근무일수 KPI 카드 확인
        print("\n✅ KPI 카드 값 확인:")
        total_working_days = page.locator('#kpiTotalWorkingDays').text_content()
        print(f"   총 근무일수: {total_working_days}")

        # 총 근무일수 카드 클릭하여 모달 열기
        print("\n🔍 근무일 현황 모달 열기...")
        page.click('.kpi-card:has-text("총 근무일수")')
        time.sleep(2)

        # 모달이 열렸는지 확인
        modal_visible = page.is_visible('#detailModal')
        if not modal_visible:
            print("❌ 모달이 열리지 않았습니다.")
            browser.close()
            return False

        print("✅ 모달 열림 성공")

        # 모달 내부 통계 확인
        print("\n📊 모달 내부 통계:")
        stat_cards = page.locator('.stat-card .stat-value').all_text_contents()
        stat_labels = page.locator('.stat-card .stat-label').all_text_contents()

        for label, value in zip(stat_labels, stat_cards):
            print(f"   {label}: {value}")

        # 달력 일수 확인
        calendar_days = page.locator('.calendar-day').count()
        print(f"\n📅 달력 표시 일수: {calendar_days}일")

        # 근무일과 데이터 없음 개수 확인
        work_days_count = page.locator('.calendar-day.work-day').count()
        no_data_count = page.locator('.calendar-day.no-data').count()

        print(f"   💼 근무일: {work_days_count}일")
        print(f"   ❌ 데이터 없음: {no_data_count}일")

        # 검증 결과
        print("\n" + "="*60)
        print("검증 결과:")
        print("="*60)

        success = True

        # 1. 달력이 30일 표시되는지 확인
        if calendar_days == 30:
            print("✅ 달력 30일 표시 정상")
        else:
            print(f"❌ 달력 일수 오류: {calendar_days}일 (예상: 30일)")
            success = False

        # 2. 총 일수가 30일인지 확인
        if "30" in stat_cards[1]:
            print("✅ 총 일수 30일 표시 정상")
        else:
            print(f"❌ 총 일수 오류: {stat_cards[1]} (예상: 30일)")
            success = False

        # 3. 총 근무일이 21일인지 확인
        if "21" in stat_cards[0]:
            print("✅ 총 근무일 21일 표시 정상")
        else:
            print(f"⚠️ 총 근무일 확인 필요: {stat_cards[0]} (예상: 21일)")

        # 4. 근무일 + 데이터없음 = 30일인지 확인
        if work_days_count + no_data_count == 30:
            print("✅ 근무일 + 데이터없음 = 30일 정상")
        else:
            print(f"❌ 합계 오류: {work_days_count} + {no_data_count} = {work_days_count + no_data_count} (예상: 30)")
            success = False

        # 스크린샷 저장
        screenshot_path = "test_working_days_modal_fixed.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 스크린샷 저장: {screenshot_path}")

        # 5초 대기 (확인용)
        print("\n⏳ 5초 후 브라우저 종료...")
        time.sleep(5)

        browser.close()

        if success:
            print("\n✅ 모든 검증 통과!")
            return True
        else:
            print("\n❌ 일부 검증 실패")
            return False

if __name__ == "__main__":
    try:
        result = test_working_days_modal()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
