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
        
        try:
            # "요약 및 시스템 검증" 탭 클릭
            validation_tab = page.query_selector('#tabValidation')
            if validation_tab:
                print("✅ '요약 및 시스템 검증' 탭 발견")
                validation_tab.click()
                time.sleep(2)
                
                # 페이지 스크롤 다운 (버튼이 아래에 있을 수 있음)
                page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
                time.sleep(1)
                
                # 연속 AQL 실패 버튼 찾기 - 여러 방법 시도
                consecutive_button = None
                
                # 방법 1: 부분 텍스트 매칭
                buttons = page.query_selector_all('button')
                for btn in buttons:
                    text = btn.inner_text()
                    if '연속' in text and 'AQL' in text:
                        print(f"✅ 버튼 발견: '{text}'")
                        consecutive_button = btn
                        break
                
                if consecutive_button:
                    consecutive_button.click()
                    time.sleep(2)
                    
                    # 모달 확인
                    modal = page.query_selector('#consecutiveAqlFailModal')
                    if modal:
                        # 모달이 보이는지 확인
                        is_visible = page.evaluate('''() => {
                            const modal = document.getElementById('consecutiveAqlFailModal');
                            if (!modal) return false;
                            const style = window.getComputedStyle(modal);
                            return style.display !== 'none';
                        }''')
                        
                        if is_visible:
                            print("✅ 모달이 열림\n")
                            
                            # 모달 제목 확인
                            title = page.query_selector('#consecutiveAqlFailModal h2')
                            if title:
                                title_text = title.inner_text()
                                print(f"📋 모달 제목: '{title_text}'")
                                
                                if 'validationTab' in title_text or '${' in title_text or '.title' in title_text:
                                    print("   ❌ 번역 키가 그대로 표시됨")
                                else:
                                    print("   ✅ 번역 정상")
                            
                            # 섹션 헤더 확인
                            h3_headers = page.query_selector_all('#consecutiveAqlFailModal h3')
                            if h3_headers:
                                print(f"\n📑 섹션 헤더 ({len(h3_headers)}개):")
                                for h3 in h3_headers:
                                    text = h3.inner_text()
                                    has_error = 'validationTab' in text or '${' in text or 'Section' in text
                                    status = "❌" if has_error else "✅"
                                    print(f"  {status} {text}")
                            
                            # 테이블 헤더 확인
                            tables = page.query_selector_all('#consecutiveAqlFailModal table')
                            for table_idx, table in enumerate(tables, 1):
                                headers = table.query_selector_all('th')
                                if headers:
                                    print(f"\n📊 테이블 {table_idx} 헤더 ({len(headers)}개):")
                                    for i, header in enumerate(headers, 1):
                                        text = header.inner_text()
                                        has_error = 'validationTab' in text or '${' in text or 'headers.' in text
                                        status = "❌" if has_error else "✅"
                                        print(f"  {status} {i}. {text}")
                            
                            # 요약 통계 확인
                            content = page.query_selector('#consecutiveAqlFailModal .modal-content')
                            if content:
                                full_text = content.inner_text()
                                # 마지막 부분 (요약 통계)
                                lines = full_text.split('\n')
                                print(f"\n📈 모달 내용 샘플 (마지막 10줄):")
                                for line in lines[-10:]:
                                    if line.strip():
                                        has_error = 'validationTab' in line or '${' in line
                                        status = "❌" if has_error else "✅"
                                        print(f"  {status} {line.strip()[:80]}")
                            
                            # 스크린샷 저장
                            page.screenshot(path='output_files/consecutive_modal_test.png')
                            print("\n📸 스크린샷 저장: output_files/consecutive_modal_test.png")
                            
                            time.sleep(3)
                        else:
                            print("❌ 모달이 숨겨져 있음")
                    else:
                        print("❌ 모달 요소를 찾을 수 없음")
                else:
                    print("❌ 연속 AQL 실패 버튼을 찾을 수 없음")
                    print("\n📋 Validation 탭의 버튼들:")
                    for btn in buttons[:20]:
                        text = btn.inner_text()
                        if text.strip():
                            print(f"  • {text[:50]}")
            else:
                print("❌ Validation 탭을 찾을 수 없음")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    test_consecutive_modal()
