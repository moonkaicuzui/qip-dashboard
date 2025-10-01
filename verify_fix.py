from playwright.sync_api import sync_playwright
import time

def verify_translation_fix():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1400, 'height': 1000})
        page = context.new_page()
        
        print("\n" + "="*80)
        print("번역 수정 검증 테스트")
        print("="*80)
        
        # 대시보드 열기
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')
        print("\n✅ 대시보드 로드 완료")
        
        # 페이지 완전 로드 대기
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(8000)  # 8초 대기
        
        # 전역 함수 목록 확인
        functions_check = page.evaluate('''() => {
            return {
                hasShowConsecutive: typeof showConsecutiveAqlFailDetails !== 'undefined',
                hasEmployeeData: typeof window.employeeData !== 'undefined',
                employeeCount: window.employeeData ? window.employeeData.length : 0
            };
        }''')
        
        print(f"\n📋 전역 함수 확인:")
        print(f"   showConsecutiveAqlFailDetails: {functions_check['hasShowConsecutive']}")
        print(f"   window.employeeData: {functions_check['hasEmployeeData']}")
        print(f"   직원 데이터 수: {functions_check['employeeCount']}")
        
        if not functions_check['hasShowConsecutive']:
            print("\n❌ 함수가 정의되지 않았습니다!")
            print("   스크립트 로딩 문제일 수 있습니다.")
            browser.close()
            return
        
        # Validation 탭 클릭
        print("\n✅ 'Validation' 탭 클릭...")
        page.click('#tabValidation')
        page.wait_for_timeout(2000)
        
        # 페이지 스크롤
        page.evaluate('window.scrollTo(0, 500)')
        page.wait_for_timeout(1000)
        
        # 모달 직접 호출
        print("✅ 모달 호출 중...")
        modal_result = page.evaluate('''() => {
            try {
                showConsecutiveAqlFailDetails();
                
                // 모달이 생성될 때까지 짧은 대기
                setTimeout(() => {}, 500);
                
                return { success: true };
            } catch (e) {
                return { success: false, error: e.message };
            }
        }''')
        
        print(f"   모달 호출 결과: {modal_result}")
        page.wait_for_timeout(2000)
        
        # 모달 내용 상세 검증
        verification = page.evaluate('''() => {
            const modal = document.getElementById('consecutiveAqlFailModal');
            if (!modal) {
                return { 
                    exists: false,
                    error: 'Modal element not found'
                };
            }
            
            const style = window.getComputedStyle(modal);
            const isVisible = style.display !== 'none';
            
            if (!isVisible) {
                return {
                    exists: true,
                    visible: false,
                    error: 'Modal exists but not visible'
                };
            }
            
            // 제목
            const h2 = modal.querySelector('h2');
            const title = h2 ? h2.innerText : '';
            
            // 섹션 헤더
            const h3Elements = modal.querySelectorAll('h3');
            const sections = Array.from(h3Elements).map(h => h.innerText);
            
            // 테이블 헤더
            const thElements = modal.querySelectorAll('th');
            const headers = Array.from(thElements).map(th => th.innerText);
            
            // 전체 텍스트
            const fullText = modal.innerText;
            
            // 오류 패턴 검사
            const errors = {
                hasValidationTab: fullText.includes('validationTab'),
                hasTemplateLiteral: fullText.includes('${'),
                hasHeadersDot: fullText.includes('headers.'),
                hasConsecutiveAqlFail: fullText.includes('consecutiveAqlFail'),
                hasThreeMonthSection: fullText.includes('threeMonthSection'),
                hasTwoMonthSection: fullText.includes('twoMonthSection')
            };
            
            return {
                exists: true,
                visible: true,
                title: title,
                sections: sections,
                headers: headers,
                errors: errors,
                hasAnyError: Object.values(errors).some(v => v === true),
                textSample: fullText.substring(0, 300)
            };
        }''');
        
        print("\n" + "="*80)
        print("모달 검증 결과")
        print("="*80)
        
        if not verification['exists']:
            print(f"\n❌ 모달이 생성되지 않음")
            print(f"   오류: {verification.get('error', 'Unknown')}")
        elif not verification['visible']:
            print(f"\n❌ 모달이 숨겨져 있음")
            print(f"   오류: {verification.get('error', 'Unknown')}")
        else:
            print(f"\n✅ 모달 정상 표시!\n")
            
            # 제목 확인
            print(f"📋 모달 제목:")
            print(f"   '{verification['title']}'")
            if 'validationTab' in verification['title'] or '${' in verification['title']:
                print(f"   ❌ 번역 키가 그대로 표시됨!")
            else:
                print(f"   ✅ 번역 정상")
            
            # 섹션 헤더 확인
            print(f"\n📑 섹션 헤더 ({len(verification['sections'])}개):")
            for i, section in enumerate(verification['sections'], 1):
                has_error = any(pattern in section for pattern in ['validationTab', '${', 'Section', 'Month'])
                status = "❌" if has_error else "✅"
                print(f"   {status} {i}. '{section}'")
            
            # 테이블 헤더 확인
            if verification['headers']:
                print(f"\n📊 테이블 헤더 (처음 6개):")
                for i, header in enumerate(verification['headers'][:6], 1):
                    has_error = any(pattern in header for pattern in ['validationTab', '${', 'headers.'])
                    status = "❌" if has_error else "✅"
                    print(f"   {status} {i}. '{header}'")
            
            # 오류 패턴 종합
            print(f"\n🔍 오류 패턴 검사:")
            print("-"*80)
            error_found = False
            for key, value in verification['errors'].items():
                if value:
                    print(f"   ❌ {key}: 발견됨")
                    error_found = True
            
            if not error_found:
                print(f"   ✅ 오류 패턴 없음")
            
            print("\n" + "="*80)
            if verification['hasAnyError']:
                print("❌ 번역 오류가 여전히 존재합니다!")
                print("\n텍스트 샘플:")
                print(verification['textSample'])
            else:
                print("✅✅✅ 모든 번역이 정상적으로 표시됩니다! ✅✅✅")
            print("="*80)
        
        # 스크린샷
        page.screenshot(path='output_files/final_verification.png', full_page=True)
        print(f"\n📸 스크린샷 저장: output_files/final_verification.png")
        
        # 모달만 스크린샷
        modal_elem = page.query_selector('#consecutiveAqlFailModal')
        if modal_elem:
            modal_elem.screenshot(path='output_files/modal_only_verification.png')
            print(f"📸 모달 스크린샷: output_files/modal_only_verification.png")
        
        print(f"\n⏳ 브라우저를 15초간 유지합니다. 직접 확인해보세요...")
        page.wait_for_timeout(15000)
        
        browser.close()
        print("\n✅ 테스트 완료")

if __name__ == '__main__':
    verify_translation_fix()
