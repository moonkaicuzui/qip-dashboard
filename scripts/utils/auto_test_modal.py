from playwright.sync_api import sync_playwright
import time

def auto_test():
    with sync_playwright() as p:
        # 이미 열린 브라우저에 연결하는 대신 새 브라우저 열기
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1400, 'height': 900})
        page = context.new_page()
        
        print("\n" + "="*80)
        print("자동 테스트 시작 - 연속 AQL 실패 모달")
        print("="*80)
        
        # 대시보드 열기
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')
        print("\n✅ 대시보드 로드 중...")
        
        # 충분한 시간 대기
        page.wait_for_load_state('domcontentloaded')
        time.sleep(6)  # JavaScript 초기화 대기
        
        # 탭 클릭
        print("✅ 'Validation' 탭 클릭 시도...")
        page.evaluate('''() => {
            const tab = document.getElementById('tabValidation');
            if (tab) {
                tab.click();
                return true;
            }
            return false;
        }''')
        time.sleep(2)
        
        # 페이지 스크롤
        page.evaluate('window.scrollTo(0, 400)')
        time.sleep(1)
        
        # 모달 함수 존재 확인 및 실행
        print("✅ 모달 함수 호출 시도...")
        result = page.evaluate('''() => {
            console.log('Checking for function...');
            console.log('showConsecutiveAqlFailDetails:', typeof showConsecutiveAqlFailDetails);
            
            if (typeof showConsecutiveAqlFailDetails !== 'undefined') {
                try {
                    showConsecutiveAqlFailDetails();
                    return { success: true, message: 'Modal opened' };
                } catch (e) {
                    return { success: false, message: 'Error: ' + e.message };
                }
            } else {
                return { success: false, message: 'Function not defined' };
            }
        }''')
        
        print(f"   결과: {result}")
        time.sleep(2)
        
        # 모달 내용 확인
        modal_check = page.evaluate('''() => {
            const modal = document.getElementById('consecutiveAqlFailModal');
            if (!modal) return { exists: false };
            
            const style = window.getComputedStyle(modal);
            if (style.display === 'none') return { exists: true, visible: false };
            
            const h2 = modal.querySelector('h2');
            const h3s = Array.from(modal.querySelectorAll('h3'));
            const ths = Array.from(modal.querySelectorAll('th'));
            
            const fullText = modal.innerText;
            
            return {
                exists: true,
                visible: true,
                title: h2 ? h2.innerText : '',
                sectionCount: h3s.length,
                sections: h3s.map(h => h.innerText),
                headerCount: ths.length,
                headers: ths.map(th => th.innerText),
                hasValidationTabError: fullText.includes('validationTab'),
                hasTemplateError: fullText.includes('${'),
                hasHeadersDotError: fullText.includes('headers.')
            };
        }''')
        
        print("\n" + "="*80)
        print("모달 검증 결과:")
        print("="*80)
        
        if not modal_check['exists']:
            print("❌ 모달이 생성되지 않음")
        elif not modal_check['visible']:
            print("❌ 모달이 숨겨져 있음")
        else:
            print(f"\n✅ 모달 표시됨!\n")
            print(f"📋 제목: {modal_check['title']}")
            print(f"\n📑 섹션 헤더 ({modal_check['sectionCount']}개):")
            for i, section in enumerate(modal_check['sections'], 1):
                print(f"  {i}. {section}")
            
            print(f"\n📊 테이블 헤더 ({modal_check['headerCount']}개):")
            for i, header in enumerate(modal_check['headers'], 1):
                print(f"  {i}. {header}")
            
            print("\n" + "="*80)
            print("오류 검사:")
            print("-"*80)
            
            errors = []
            if modal_check['hasValidationTabError']:
                errors.append("'validationTab' 텍스트 발견")
            if modal_check['hasTemplateError']:
                errors.append("'${' 템플릿 리터럴 발견")
            if modal_check['hasHeadersDotError']:
                errors.append("'headers.' 텍스트 발견")
            
            if errors:
                print("❌ 발견된 오류:")
                for error in errors:
                    print(f"   • {error}")
            else:
                print("✅✅✅ 오류 없음 - 모든 번역이 정상! ✅✅✅")
            
            print("="*80)
        
        # 스크린샷
        page.screenshot(path='output_files/modal_auto_test.png', full_page=True)
        print("\n📸 스크린샷 저장: output_files/modal_auto_test.png")
        
        print("\n⏳ 10초간 확인 후 종료...")
        time.sleep(10)
        
        browser.close()

if __name__ == '__main__':
    auto_test()
