from playwright.sync_api import sync_playwright
import time

def test_modal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print("="*80)
        print("연속 AQL 실패 모달 번역 테스트")
        print("="*80)
        
        # 대시보드 열기
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        
        # Validation 탭으로 이동
        tab = page.query_selector('#tabValidation')
        if tab:
            page.evaluate("(el) => el.click()", tab)
            print("\n✅ Validation 탭 클릭")
            time.sleep(2)
        
        # 모달 열기 (JavaScript로)
        result = page.evaluate('''() => {
            if (typeof showConsecutiveAqlFailDetails === 'function') {
                showConsecutiveAqlFailDetails();
                return 'opened';
            }
            return 'function not found';
        }''')
        
        print(f"✅ 모달 열기: {result}")
        time.sleep(2)
        
        # 모달 내용 추출
        modal_data = page.evaluate('''() => {
            const modal = document.getElementById('consecutiveAqlFailModal');
            if (!modal) return null;
            
            const h2 = modal.querySelector('h2');
            const h3s = Array.from(modal.querySelectorAll('h3'));
            const ths = Array.from(modal.querySelectorAll('th'));
            
            return {
                title: h2 ? h2.innerText : 'N/A',
                sections: h3s.map(h => h.innerText),
                headers: ths.map(th => th.innerText),
                hasError: modal.innerText.includes('validationTab') || modal.innerText.includes('${')
            };
        }''')
        
        if modal_data:
            print("\n" + "="*80)
            print("모달 제목:")
            print("-"*80)
            print(f"  {modal_data['title']}")
            
            print("\n" + "="*80)
            print(f"섹션 헤더 ({len(modal_data['sections'])}개):")
            print("-"*80)
            for i, section in enumerate(modal_data['sections'], 1):
                print(f"  {i}. {section}")
            
            print("\n" + "="*80)
            print(f"테이블 헤더 ({len(modal_data['headers'])}개):")
            print("-"*80)
            for i, header in enumerate(modal_data['headers'], 1):
                print(f"  {i}. {header}")
            
            print("\n" + "="*80)
            if modal_data['hasError']:
                print("❌ 번역 오류 발견 - 'validationTab' 또는 '${' 문자열 포함")
            else:
                print("✅✅✅ 모든 번역이 정상적으로 표시됨! ✅✅✅")
            print("="*80)
            
            # 스크린샷
            page.screenshot(path='output_files/final_test.png', full_page=True)
            print("\n📸 스크린샷: output_files/final_test.png")
        else:
            print("\n❌ 모달을 찾을 수 없음")
        
        print("\n⏳ 5초 후 브라우저 종료...")
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    test_modal()
