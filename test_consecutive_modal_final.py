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
        
        # 페이지 완전히 로드 대기
        page.wait_for_load_state('networkidle')
        page.wait_for_load_state('domcontentloaded')
        time.sleep(5)  # 충분한 대기
        
        try:
            # 탭 클릭
            tab_element = page.query_selector('#tabValidation')
            if tab_element:
                page.evaluate("(el) => el.click()", tab_element)
                print("✅ 'Validation' 탭 클릭")
                time.sleep(2)
            
            # KPI 카드 클릭 - JavaScript로 직접
            result = page.evaluate('''() => {
                try {
                    // KPI 카드 직접 클릭 시뮬레이션
                    if (typeof showValidationModal === 'function') {
                        showValidationModal('consecutiveAqlFail');
                        return 'success';
                    } else {
                        return 'showValidationModal not found';
                    }
                } catch (e) {
                    return 'error: ' + e.message;
                }
            }''')
            
            print(f"✅ 모달 열기 결과: {result}")
            time.sleep(2)
            
            # 모달 확인
            modal_info = page.evaluate('''() => {
                const modal = document.getElementById('consecutiveAqlFailModal');
                if (!modal) return { exists: false };
                
                const style = window.getComputedStyle(modal);
                const isVisible = style.display !== 'none';
                
                if (!isVisible) return { exists: true, visible: false };
                
                // 제목 확인
                const h2 = modal.querySelector('h2');
                const title = h2 ? h2.innerText : '';
                
                // 섹션 헤더
                const h3s = Array.from(modal.querySelectorAll('h3')).map(h => h.innerText);
                
                // 테이블 헤더
                const tables = Array.from(modal.querySelectorAll('table'));
                const tableHeaders = tables.map(table => 
                    Array.from(table.querySelectorAll('th')).map(th => th.innerText)
                );
                
                // 전체 텍스트에서 오류 패턴 검색
                const fullText = modal.innerText;
                const errorPatterns = ['validationTab', '${', 'headers.', 'threeMonthSection', 'twoMonthSection'];
                const errors = errorPatterns.filter(pattern => fullText.includes(pattern));
                
                return {
                    exists: true,
                    visible: true,
                    title: title,
                    sectionHeaders: h3s,
                    tableHeaders: tableHeaders,
                    errors: errors,
                    hasErrors: errors.length > 0
                };
            }''')
            
            if not modal_info['exists']:
                print("❌ 모달 요소를 찾을 수 없음")
                return
            
            if not modal_info['visible']:
                print("❌ 모달이 숨겨져 있음")
                return
            
            print("✅ 모달이 열림\n")
            print("="*80)
            
            # 결과 출력
            print(f"📋 모달 제목:")
            print(f"   '{modal_info['title']}'")
            has_title_error = any(pattern in modal_info['title'] for pattern in ['validationTab', '${', '.title'])
            if has_title_error:
                print("   ❌ 번역 키가 그대로 표시됨")
            else:
                print("   ✅ 번역 정상")
            print("="*80)
            
            if modal_info['sectionHeaders']:
                print(f"\n📑 섹션 헤더 ({len(modal_info['sectionHeaders'])}개):")
                print("-"*80)
                for idx, header in enumerate(modal_info['sectionHeaders'], 1):
                    has_error = any(pattern in header for pattern in ['validationTab', '${', 'Section', 'Month'])
                    status = "❌" if has_error else "✅"
                    print(f"  {status} {idx}. '{header}'")
                print("="*80)
            
            if modal_info['tableHeaders']:
                for table_idx, headers in enumerate(modal_info['tableHeaders'], 1):
                    if headers:
                        print(f"\n📊 테이블 {table_idx} - 헤더 컬럼 ({len(headers)}개):")
                        print("-"*80)
                        for i, header in enumerate(headers, 1):
                            has_error = any(pattern in header for pattern in ['validationTab', '${', 'headers.', '.empNo'])
                            status = "❌" if has_error else "✅"
                            print(f"  {status} 컬럼 {i}: '{header}'")
                print("="*80)
            
            print(f"\n🔍 번역 오류 패턴 검색 결과:")
            print("-"*80)
            if modal_info['hasErrors']:
                print(f"❌ 발견된 오류 패턴:")
                for error in modal_info['errors']:
                    print(f"   • {error}")
            else:
                print(f"✅ 오류 패턴 없음 - 모든 번역이 정상적으로 표시됨!")
            print("="*80)
            
            # 스크린샷 저장
            page.screenshot(path='output_files/consecutive_modal_test.png', full_page=True)
            print("\n📸 스크린샷 저장: output_files/consecutive_modal_test.png")
            
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    test_consecutive_modal()
