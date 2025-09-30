#!/usr/bin/env python3
"""
조직도 필터링 상세 디버깅
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 조직도 필터링 상세 분석\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 콘솔 메시지 캡처
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Org Chart 탭 클릭
    page.click("#tabOrgChart")
    time.sleep(2)

    print("\n📊 필터링 분석:\n")

    # 콘솔 메시지에서 필터링 정보 추출
    print("=== 제외된 직원들 ===")
    for msg in console_messages:
        if "Excluding" in msg:
            print(f"  {msg}")

    print("\n=== TYPE-1 직원 통계 ===")
    for msg in console_messages:
        if "TYPE-1 employees for hierarchy" in msg:
            print(f"  {msg}")

    # JavaScript로 상세 데이터 확인
    print("\n=== JavaScript 데이터 상세 분석 ===")
    try:
        result = page.evaluate("""
            () => {
                const allType1 = employeeData.filter(e => e.type === 'TYPE-1');

                const positionGroups = {};
                allType1.forEach(emp => {
                    const pos = emp.position || 'Unknown';
                    if (!positionGroups[pos]) {
                        positionGroups[pos] = [];
                    }
                    positionGroups[pos].push(emp.name);
                });

                return {
                    totalType1: allType1.length,
                    positionBreakdown: Object.entries(positionGroups).map(([pos, names]) => ({
                        position: pos,
                        count: names.length,
                        names: names.slice(0, 3)  // 처음 3명만
                    }))
                };
            }
        """)

        print(f"  전체 TYPE-1 직원: {result['totalType1']}명\n")
        print("  포지션별 분포:")
        for item in result['positionBreakdown']:
            print(f"    • {item['position']}: {item['count']}명")
            if item['names']:
                print(f"      예시: {', '.join(item['names'])}")

    except Exception as e:
        print(f"  ❌ JavaScript 평가 오류: {e}")

    if page_errors:
        print(f"\n❌ JavaScript 오류: {len(page_errors)}개")
        for err in page_errors[:3]:
            print(f"   - {err}")
    else:
        print("\n✅ JavaScript 오류 없음")

    browser.close()

print("\n✅ 분석 완료")