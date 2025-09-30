#!/usr/bin/env python3
"""
boss_id 매핑 디버깅 스크립트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 Boss ID 매핑 디버깅\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 콘솔 메시지 캡처
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    print("\n📋 콘솔 메시지 (필터링):")
    for msg in console_messages:
        if any(keyword in msg for keyword in ['name-to-empno', 'Mapped boss', 'TYPE-1 employees', 'Hierarchy built']):
            print(f"  {msg}")

    # JavaScript로 데이터 확인
    print("\n🔍 JavaScript 데이터 확인:")
    try:
        result = page.evaluate("""
            () => {
                // 전체 직원 수
                const totalEmployees = employeeData ? employeeData.length : 0;

                // TYPE-1 직원 수
                const type1Employees = employeeData ? employeeData.filter(e => e.type === 'TYPE-1').length : 0;

                // boss_id가 있는 TYPE-1 직원 수
                const type1WithBoss = employeeData ?
                    employeeData.filter(e => e.type === 'TYPE-1' && e.boss_id && e.boss_id !== '').length : 0;

                // 샘플 TYPE-1 직원
                const type1Sample = employeeData ?
                    employeeData.filter(e => e.type === 'TYPE-1').slice(0, 5).map(e => ({
                        name: e.name,
                        emp_no: e.emp_no,
                        boss_id: e.boss_id,
                        boss_name: e['MST direct boss name'] || e['direct boss name'] || 'N/A'
                    })) : [];

                return {
                    totalEmployees,
                    type1Employees,
                    type1WithBoss,
                    type1Sample
                };
            }
        """)

        print(f"  전체 직원: {result['totalEmployees']}명")
        print(f"  TYPE-1 직원: {result['type1Employees']}명")
        print(f"  boss_id가 있는 TYPE-1 직원: {result['type1WithBoss']}명")

        print(f"\n  TYPE-1 직원 샘플 (5명):")
        for emp in result['type1Sample']:
            print(f"    - {emp['name']} ({emp['emp_no']})")
            print(f"      boss_id: {emp['boss_id']}")
            print(f"      boss_name: {emp['boss_name']}")

    except Exception as e:
        print(f"  ❌ JavaScript 평가 오류: {e}")

    print("\n⏸️  브라우저를 10초간 유지합니다...")
    time.sleep(10)

    browser.close()

print("\n✅ 디버깅 완료")