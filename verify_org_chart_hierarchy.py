#!/usr/bin/env python3
"""
조직도 계층 구조 검증 스크립트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 조직도 계층 구조 검증")
print(f"대시보드: {dashboard_path}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    # 콘솔 메시지 캡처
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

    # 페이지 오류 캡처
    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    print("\n📋 JavaScript 오류 확인...")
    if page_errors:
        print("❌ JavaScript 오류 발견:")
        for err in page_errors:
            print(f"  {err}")
    else:
        print("✅ JavaScript 오류 없음")

    # Org Chart 탭 클릭
    print("\n📊 Org Chart 탭 클릭...")
    try:
        page.click("#tabOrgChart")
        time.sleep(3)
        print("✅ Org Chart 탭 열림")

        # 스크린샷 저장
        page.screenshot(path="output_files/orgchart_hierarchy_verification.png")
        print("📸 스크린샷 저장: orgchart_hierarchy_verification.png")

    except Exception as e:
        print(f"❌ Org Chart 탭 열기 실패: {e}")
        browser.close()
        exit(1)

    # 콘솔 로그에서 계층 구조 정보 추출
    print("\n🔍 조직도 계층 구조 분석...")

    hierarchy_log = None
    type1_count_log = None

    for msg in console_messages:
        if "Hierarchy built:" in msg:
            hierarchy_log = msg
        elif "TYPE-1 employees for hierarchy:" in msg:
            type1_count_log = msg

    if type1_count_log:
        print(f"✅ {type1_count_log}")
    else:
        print("⚠️  TYPE-1 employees 로그를 찾을 수 없음")

    if hierarchy_log:
        print(f"✅ {hierarchy_log}")

        # Root nodes 개수 추출
        if "root nodes" in hierarchy_log:
            import re
            match = re.search(r'(\d+) root nodes', hierarchy_log)
            if match:
                root_count = int(match.group(1))
                print(f"\n📊 Root nodes 개수: {root_count}")

                if root_count <= 3:
                    print("✅ 계층 구조가 올바르게 형성되었습니다! (Root nodes ≤ 3)")
                elif root_count <= 10:
                    print("⚠️  Root nodes가 다소 많습니다. 일부 관리자의 상사가 누락되었을 수 있습니다.")
                else:
                    print("❌ Root nodes가 너무 많습니다! 계층 구조에 문제가 있습니다.")
    else:
        print("❌ Hierarchy built 로그를 찾을 수 없음")

    # 조직도 노드 개수 확인
    print("\n🔍 조직도 노드 확인...")
    try:
        # 직원 카드 개수
        card_count = page.locator(".org-chart-node, .tree-node, [data-emp-id]").count()
        print(f"✅ 조직도에 표시된 노드: {card_count}개")

        # 연결선 확인 (SVG path 또는 CSS로 구현된 line)
        link_count = page.locator("svg path.link, .org-chart-link, .tree-link").count()

        if link_count > 0:
            print(f"✅ 계층 연결선 발견: {link_count}개")
            print("✅ 조직도에 계층 구조가 시각적으로 표현되고 있습니다!")
        else:
            print("⚠️  계층 연결선을 찾을 수 없음 (HTML 트리 구조일 수 있음)")

    except Exception as e:
        print(f"⚠️  노드 확인 중 오류: {e}")

    # 특정 관리자의 children 확인 (JavaScript 평가)
    print("\n🔍 계층 구조 데이터 확인 (JavaScript)...")
    try:
        # buildHierarchyData 함수가 생성한 구조 확인
        result = page.evaluate("""
            () => {
                // employeeData에서 TYPE-1 직원 수 확인
                const type1Count = employeeData ? employeeData.filter(e => e.type === 'TYPE-1').length : 0;

                return {
                    employeeDataLength: employeeData ? employeeData.length : 0,
                    type1Count: type1Count
                };
            }
        """)

        print(f"✅ EmployeeData 로드: {result['employeeDataLength']}명")
        print(f"✅ TYPE-1 직원: {result['type1Count']}명")

    except Exception as e:
        print(f"⚠️  계층 구조 데이터 확인 실패: {e}")

    print("\n⏸️  브라우저를 15초간 유지합니다. 조직도를 직접 확인하세요...")
    print("   - 계층 구조가 트리 형태로 표시되는지 확인")
    print("   - 연결선이 부모-자식 관계를 나타내는지 확인")
    print("   - 노드를 클릭하여 expand/collapse가 작동하는지 확인")
    time.sleep(15)

    browser.close()

print("\n✅ 검증 완료")