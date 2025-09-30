#!/usr/bin/env python3
"""
조직도 계층 구조 빠른 검증
"""

from playwright.sync_api import sync_playwright
import time
import os
import re

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 조직도 계층 구조 빠른 검증\n")

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

    print("\n📊 분석 결과:\n")

    # 주요 로그 추출
    hierarchy_log = None
    type1_log = None
    boss_mapping_count = 0

    for msg in console_messages:
        if "Hierarchy built:" in msg:
            hierarchy_log = msg
        elif "TYPE-1 employees for hierarchy:" in msg:
            type1_log = msg
        elif "Mapped boss for" in msg:
            boss_mapping_count += 1

    # TYPE-1 직원 수
    if type1_log:
        match = re.search(r'(\d+)', type1_log)
        if match:
            print(f"✅ TYPE-1 직원: {match.group(1)}명")

    # Boss 매핑 성공
    print(f"✅ Boss 매핑 성공: {boss_mapping_count}명")

    # Root nodes 개수
    if hierarchy_log:
        match = re.search(r'(\d+) root nodes', hierarchy_log)
        if match:
            root_count = int(match.group(1))
            print(f"✅ Root nodes: {root_count}개")

            if root_count <= 3:
                print("\n🎉 ✅ 계층 구조가 올바르게 형성되었습니다!")
                print("   → Root nodes ≤ 3: 정상적인 조직도 계층 구조")
            elif root_count <= 10:
                print("\n⚠️  Root nodes가 다소 많습니다.")
                print(f"   → {root_count}개의 최상위 노드 (일부 상사가 누락되었을 수 있음)")
            else:
                print(f"\n❌ Root nodes가 너무 많습니다! ({root_count}개)")
                print("   → 계층 구조에 문제가 있습니다.")

    # JavaScript 오류 확인
    if page_errors:
        print(f"\n❌ JavaScript 오류: {len(page_errors)}개")
        for err in page_errors[:3]:
            print(f"   - {err}")
    else:
        print("\n✅ JavaScript 오류 없음")

    browser.close()

print("\n✅ 검증 완료")