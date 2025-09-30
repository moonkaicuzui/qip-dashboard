#!/usr/bin/env python3
"""
모달 빠른 테스트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 모달 기능 빠른 테스트\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    console_messages = []
    page_errors = []

    page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Org Chart 탭 클릭
    page.click("#tabOrgChart")
    time.sleep(2)

    # showIncentiveModal 함수 확인
    print("\n🔍 showIncentiveModal 함수 확인...")
    try:
        result = page.evaluate("""
            () => {
                return {
                    functionExists: typeof window.showIncentiveModal === 'function',
                    employeeDataLength: employeeData ? employeeData.length : 0,
                    sampleEmpNo: employeeData && employeeData.length > 0 ? employeeData[0].emp_no : null
                };
            }
        """)

        print(f"  showIncentiveModal 함수: {'✅ 존재' if result['functionExists'] else '❌ 없음'}")
        print(f"  employeeData: {result['employeeDataLength']}명")
        if result['sampleEmpNo']:
            print(f"  샘플 emp_no: {result['sampleEmpNo']}")

            # 직접 모달 호출 시도
            print("\n🖱️  showIncentiveModal() 직접 호출 테스트...")
            try:
                page.evaluate(f"""
                    () => {{
                        try {{
                            showIncentiveModal('{result['sampleEmpNo']}');
                        }} catch (error) {{
                            console.error('Modal error:', error.message);
                        }}
                    }}
                """)
                time.sleep(1)

                # 최근 콘솔 메시지 확인
                print("\n📋 콘솔 메시지:")
                for msg in console_messages[-10:]:
                    if 'error' in msg.lower() or 'modal' in msg.lower():
                        print(f"  {msg}")

            except Exception as e:
                print(f"  ❌ 모달 호출 오류: {e}")

    except Exception as e:
        print(f"  ❌ JavaScript 평가 오류: {e}")

    if page_errors:
        print("\n❌ JavaScript 오류:")
        for err in page_errors[:5]:
            print(f"  {err}")
    else:
        print("\n✅ JavaScript 오류 없음")

    browser.close()

print("\n✅ 테스트 완료")