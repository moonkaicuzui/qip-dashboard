from playwright.sync_api import sync_playwright
import time

def test_consecutive_modal():
    """연속 AQL 실패 모달의 번역 표시 확인"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 대시보드 열기
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')
        time.sleep(3)
        
        try:
            # "요약 및 시스템 검증" 탭 클릭
            page.evaluate("showTab('validation')")
            print("✅ '요약 및 시스템 검증' 탭으로 전환")
            time.sleep(2)
            
            # 페이지 스크롤하여 KPI 카드 영역 보이게 하기
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            
            # JavaScript로 직접 모달 함수 호출
            print("✅ 연속 AQL 실패 모달 열기 시도...")
            page.evaluate("showValidationModal('consecutiveAqlFail')")
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
                    print("="*80)
                    
                    # 모달 제목 확인
                    title = page.query_selector('#consecutiveAqlFailModal h2')
                    if title:
                        title_text = title.inner_text()
                        print(f"📋 모달 제목:")
                        print(f"   '{title_text}'")
                        
                        if 'validationTab' in title_text or '${' in title_text or '.title' in title_text:
                            print("   ❌ 번역 키가 그대로 표시됨 - 수정 필요!")
                        else:
                            print("   ✅ 번역 정상")
                    print("="*80)
                    
                    # 섹션 헤더 확인
                    h3_headers = page.query_selector_all('#consecutiveAqlFailModal h3')
                    if h3_headers:
                        print(f"\n📑 섹션 헤더 ({len(h3_headers)}개):")
                        print("-"*80)
                        for idx, h3 in enumerate(h3_headers, 1):
                            text = h3.inner_text()
                            has_error = (
                                'validationTab' in text or 
                                '${' in text or 
                                'Section' in text or 
                                'threeMonth' in text or 
                                'twoMonth' in text or
                                '.three' in text or
                                '.two' in text
                            )
                            status = "❌" if has_error else "✅"
                            print(f"  {status} {idx}. '{text}'")
                    print("="*80)
                    
                    # 테이블 헤더 확인
                    tables = page.query_selector_all('#consecutiveAqlFailModal table')
                    for table_idx, table in enumerate(tables, 1):
                        headers = table.query_selector_all('th')
                        if headers:
                            print(f"\n📊 테이블 {table_idx} - 헤더 컬럼 ({len(headers)}개):")
                            print("-"*80)
                            for i, header in enumerate(headers, 1):
                                text = header.inner_text()
                                has_error = (
                                    'validationTab' in text or 
                                    '${' in text or 
                                    'headers.' in text or 
                                    '.empNo' in text or 
                                    '.name' in text or
                                    '.position' in text or
                                    '.supervisor' in text
                                )
                                status = "❌" if has_error else "✅"
                                print(f"  {status} 컬럼 {i}: '{text}'")
                    print("="*80)
                    
                    # 전체 모달 내용에서 오류 검색
                    content = page.query_selector('#consecutiveAqlFailModal .modal-content')
                    if content:
                        full_text = content.inner_text()
                        error_patterns = [
                            'validationTab',
                            '${',
                            'headers.',
                            'threeMonthSection',
                            'twoMonthSection',
                            '.title',
                            'consecutiveAqlFail'
                        ]
                        errors_found = []
                        for pattern in error_patterns:
                            if pattern in full_text:
                                # 해당 패턴이 포함된 줄 찾기
                                lines_with_error = [line for line in full_text.split('\n') if pattern in line]
                                errors_found.append(f"{pattern} ({len(lines_with_error)} occurrences)")
                        
                        print(f"\n🔍 번역 오류 패턴 검색 결과:")
                        print("-"*80)
                        if errors_found:
                            print(f"❌ 발견된 오류:")
                            for error in errors_found:
                                print(f"   • {error}")
                        else:
                            print(f"✅ 오류 패턴 없음 - 모든 번역이 정상적으로 표시됨")
                    print("="*80)
                    
                    # 스크린샷 저장
                    page.screenshot(path='output_files/consecutive_modal_test.png', full_page=True)
                    print("\n📸 스크린샷 저장: output_files/consecutive_modal_test.png")
                    
                    time.sleep(3)
                else:
                    print("❌ 모달이 숨겨져 있음")
            else:
                print("❌ 모달 요소를 찾을 수 없음")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    test_consecutive_modal()
