from playwright.sync_api import sync_playwright
import time

def test_consecutive_modal():
    """연속 AQL 실패 모달의 번역 표시 확인"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 대시보드 열기
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')
        time.sleep(3)
        
        # 페이지가 완전히 로드될 때까지 대기
        page.wait_for_load_state('networkidle')
        
        # Validation Summary 탭 찾기 (여러 방법 시도)
        try:
            # 방법 1: 텍스트로 찾기
            validation_tab = page.query_selector('text="Validation Summary"')
            if not validation_tab:
                validation_tab = page.query_selector('text="검증 요약"')
            if not validation_tab:
                # 방법 2: 모든 탭 버튼 확인
                print("📋 사용 가능한 탭 버튼:")
                tab_buttons = page.query_selector_all('.tab-button')
                for i, btn in enumerate(tab_buttons, 1):
                    text = btn.inner_text()
                    print(f"  {i}. {text}")
                    if 'Validation' in text or '검증' in text:
                        validation_tab = btn
                        break
            
            if validation_tab:
                print(f"✅ Validation Summary 탭 발견")
                validation_tab.click()
                time.sleep(2)
                
                # 연속 AQL 실패 버튼 찾기
                consecutive_button = page.query_selector('text="연속 AQL 실패"')
                if not consecutive_button:
                    # 버튼의 정확한 텍스트 확인
                    print("\n📋 Validation Summary 탭의 버튼들:")
                    buttons = page.query_selector_all('button')
                    for btn in buttons:
                        text = btn.inner_text()
                        if 'AQL' in text or '실패' in text:
                            print(f"  • {text}")
                            if '연속' in text:
                                consecutive_button = btn
                
                if consecutive_button:
                    print(f"✅ 연속 AQL 실패 버튼 발견")
                    consecutive_button.click()
                    time.sleep(2)
                    
                    # 모달 확인
                    modal = page.query_selector('#consecutiveAqlFailModal')
                    if modal and modal.is_visible():
                        print("✅ 모달이 열림\n")
                        
                        # 모달 제목 확인
                        title = page.query_selector('#consecutiveAqlFailModal h2')
                        if title:
                            title_text = title.inner_text()
                            print(f"📋 모달 제목: '{title_text}'")
                            
                            if 'validationTab' in title_text or '${' in title_text:
                                print("   ❌ 번역 키가 그대로 표시됨")
                            else:
                                print("   ✅ 번역 정상")
                        
                        # 섹션 헤더 확인
                        h3_headers = page.query_selector_all('#consecutiveAqlFailModal h3')
                        if h3_headers:
                            print(f"\n📑 섹션 헤더 ({len(h3_headers)}개):")
                            for h3 in h3_headers:
                                text = h3.inner_text()
                                has_error = 'validationTab' in text or '${' in text
                                status = "❌" if has_error else "✅"
                                print(f"  {status} {text}")
                        
                        # 테이블 헤더 확인
                        headers = page.query_selector_all('#consecutiveAqlFailModal th')
                        if headers:
                            print(f"\n📊 테이블 헤더 ({len(headers)}개):")
                            for i, header in enumerate(headers, 1):
                                text = header.inner_text()
                                has_error = 'validationTab' in text or '${' in text or 'headers.' in text
                                status = "❌" if has_error else "✅"
                                print(f"  {status} {i}. {text}")
                        
                        # 요약 통계 확인
                        summary = page.query_selector('#consecutiveAqlFailModal p')
                        if summary:
                            print(f"\n📈 요약 통계:")
                            summary_text = summary.inner_text()
                            for line in summary_text.split('\n'):
                                if line.strip():
                                    has_error = 'validationTab' in line or '${' in line
                                    status = "❌" if has_error else "✅"
                                    print(f"  {status} {line.strip()}")
                        
                        time.sleep(3)
                    else:
                        print("❌ 모달이 열리지 않음")
                else:
                    print("❌ 연속 AQL 실패 버튼을 찾을 수 없음")
            else:
                print("❌ Validation Summary 탭을 찾을 수 없음")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    test_consecutive_modal()
