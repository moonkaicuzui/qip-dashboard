#!/usr/bin/env python3
"""Playwright를 사용하여 대시보드 콘솔 확인"""

from playwright.sync_api import sync_playwright
import json
import time

def check_dashboard_console():
    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 콘솔 메시지 수집
        console_messages = []
        
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text
            })
            print(f"[{msg.type}] {msg.text}")
        
        # 콘솔 이벤트 리스너 등록
        page.on("console", handle_console)
        
        # 페이지 로드
        print("Loading dashboard...")
        page.goto(f"file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트8.3_구글 연동 완료_by Macbook pro_조건 매트릭스 JSON 파일 도입_버전 5_action.sh 테스트/output_files/management_dashboard_2025_08.html")
        
        # 페이지 로드 대기
        page.wait_for_timeout(3000)
        
        # ASSEMBLY 팀 클릭
        print("\nClicking ASSEMBLY team...")
        assembly_card = page.locator('div.team-card:has-text("ASSEMBLY")')
        if assembly_card.count() > 0:
            assembly_card.first.click()
            page.wait_for_timeout(2000)
            
            # 모달이 열렸는지 확인
            modal = page.locator('#team-detail-modal')
            if modal.count() > 0 and modal.is_visible():
                print("Modal opened successfully")
                
                # Sunburst 차트 컨테이너 확인
                sunburst_container = page.locator('[id^="team-role-sunburst"]')
                if sunburst_container.count() > 0:
                    print(f"Sunburst container found: {sunburst_container.count()} container(s)")
                    
                    # 컨테이너 내용 확인
                    for i in range(sunburst_container.count()):
                        container = sunburst_container.nth(i)
                        inner_html = container.inner_html()
                        if inner_html:
                            print(f"Container {i} has content: {len(inner_html)} characters")
                            if "svg" in inner_html.lower():
                                print("  - SVG element found")
                            if "차트를 로드할 수 없습니다" in inner_html:
                                print("  - Error message found: Chart cannot be loaded")
                            if "데이터 구조에 문제가 있습니다" in inner_html:
                                print("  - Error message found: Data structure problem")
                        else:
                            print(f"Container {i} is empty")
                else:
                    print("No Sunburst container found")
            else:
                print("Modal not visible")
        else:
            print("ASSEMBLY team card not found")
        
        # 콘솔 메시지 요약
        print("\n=== Console Summary ===")
        error_count = sum(1 for msg in console_messages if msg['type'] == 'error')
        warning_count = sum(1 for msg in console_messages if msg['type'] == 'warning')
        log_count = sum(1 for msg in console_messages if msg['type'] == 'log')
        
        print(f"Errors: {error_count}")
        print(f"Warnings: {warning_count}")
        print(f"Logs: {log_count}")
        
        # Sunburst 관련 메시지 찾기
        print("\n=== Sunburst Related Messages ===")
        for msg in console_messages:
            if 'sunburst' in msg['text'].lower() or 'plotly' in msg['text'].lower():
                print(f"[{msg['type']}] {msg['text']}")
        
        # 멤버 구조 확인
        print("\n=== Member Structure Messages ===")
        for msg in console_messages:
            if 'member' in msg['text'].lower() or 'position' in msg['text'].lower():
                print(f"[{msg['type']}] {msg['text']}")
        
        # 대기
        print("\nPress Enter to close browser...")
        input()
        
        browser.close()

if __name__ == "__main__":
    check_dashboard_console()