from playwright.sync_api import sync_playwright
import time

def test_consecutive_modal():
    """연속 AQL 실패 모달의 번역 표시 확인"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 대시보드 열기
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')
        time.sleep(2)
        
        # Validation Summary 탭으로 이동
        page.click('button[data-tab="validation-tab"]')
        time.sleep(1)
        
        # 연속 AQL 실패 버튼 찾기 및 클릭
        try:
            # 버튼 찾기
            button = page.query_selector('text="연속 AQL 실패 (3개월)"')
            if button:
                print("✅ 버튼 발견: '연속 AQL 실패 (3개월)'")
                button.click()
                time.sleep(2)
                
                # 모달 확인
                modal = page.query_selector('#consecutiveAqlFailModal')
                if modal and modal.is_visible():
                    print("✅ 모달이 열림")
                    
                    # 모달 제목 확인
                    title = page.query_selector('#consecutiveAqlFailModal h2')
                    if title:
                        title_text = title.inner_text()
                        print(f"📋 모달 제목: {title_text}")
                        
                        if 'validationTab' in title_text or '${' in title_text:
                            print("❌ 번역 키가 그대로 표시됨 (수정 필요)")
                        else:
                            print("✅ 번역이 정상적으로 표시됨")
                    
                    # 테이블 헤더 확인
                    headers = page.query_selector_all('#consecutiveAqlFailModal th')
                    print(f"\n📊 테이블 헤더 ({len(headers)}개):")
                    for i, header in enumerate(headers[:6], 1):
                        text = header.inner_text()
                        print(f"  {i}. {text}")
                        if 'validationTab' in text or '${' in text:
                            print(f"     ❌ 번역 키가 그대로 표시됨")
                    
                    # 섹션 헤더 확인
                    h3_headers = page.query_selector_all('#consecutiveAqlFailModal h3')
                    if h3_headers:
                        print(f"\n📑 섹션 헤더 ({len(h3_headers)}개):")
                        for h3 in h3_headers:
                            text = h3.inner_text()
                            print(f"  • {text}")
                            if 'validationTab' in text or '${' in text:
                                print(f"    ❌ 번역 키가 그대로 표시됨")
                    
                    time.sleep(3)
                else:
                    print("❌ 모달이 열리지 않음")
            else:
                print("❌ 버튼을 찾을 수 없음")
                # 페이지의 모든 버튼 출력
                all_buttons = page.query_selector_all('button')
                print(f"\n사용 가능한 버튼 ({len(all_buttons)}개):")
                for btn in all_buttons[:10]:
                    print(f"  • {btn.inner_text()}")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    test_consecutive_modal()
