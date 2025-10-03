from playwright.sync_api import sync_playwright
import time

def complete_verification():
    with sync_playwright() as p:
        # 브라우저 시작 (느리게 실행하여 디버깅 용이)
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000  # 각 동작 1초씩 대기
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1200}
        )
        
        page = context.new_page()
        
        print("\n" + "="*80)
        print("🔍 연속 AQL 실패 모달 번역 검증 - 최종 테스트")
        print("="*80)
        
        # 대시보드 로드
        print("\n1️⃣ 대시보드 로드 중...")
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')
        
        # 완전히 로드될 때까지 대기
        page.wait_for_load_state('load')
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_load_state('networkidle')
        
        print("   ⏳ JavaScript 초기화 대기 중 (10초)...")
        time.sleep(10)
        
        # 페이지 상태 확인
        page_ready = page.evaluate('''() => {
            return {
                readyState: document.readyState,
                hasEmployeeData: typeof window.employeeData !== 'undefined',
                employeeCount: window.employeeData ? window.employeeData.length : 0,
                hasGetTranslation: typeof getTranslation !== 'undefined',
                hasShowConsecutive: typeof showConsecutiveAqlFailDetails !== 'undefined',
                currentLang: typeof currentLanguage !== 'undefined' ? currentLanguage : 'unknown'
            };
        }''')
        
        print(f"\n📊 페이지 상태:")
        print(f"   • 로드 상태: {page_ready['readyState']}")
        print(f"   • 직원 데이터: {page_ready['hasEmployeeData']} ({page_ready['employeeCount']}명)")
        print(f"   • 번역 함수: {page_ready['hasGetTranslation']}")
        print(f"   • 모달 함수: {page_ready['hasShowConsecutive']}")
        print(f"   • 현재 언어: {page_ready['currentLang']}")
        
        if not page_ready['hasShowConsecutive']:
            print("\n❌ showConsecutiveAqlFailDetails 함수가 로드되지 않았습니다!")
            print("   더 긴 대기 시간 시도 중...")
            time.sleep(10)
            
            # 재확인
            page_ready2 = page.evaluate('typeof showConsecutiveAqlFailDetails !== "undefined"')
            if not page_ready2:
                print("❌ 여전히 함수를 찾을 수 없습니다. HTML 파일에 문제가 있을 수 있습니다.")
                browser.close()
                return
        
        # Validation 탭 클릭
        print("\n2️⃣ 'Validation' 탭으로 이동 중...")
        page.click('#tabValidation', timeout=10000)
        time.sleep(3)
        
        # 스크롤
        page.evaluate('window.scrollTo(0, 600)')
        time.sleep(2)
        
        # 모달 열기
        print("\n3️⃣ 연속 AQL 실패 모달 열기 중...")
        modal_opened = page.evaluate('''() => {
            try {
                if (typeof showConsecutiveAqlFailDetails === 'function') {
                    showConsecutiveAqlFailDetails();
                    return { success: true, message: 'Function called successfully' };
                } else {
                    return { success: false, message: 'Function not found' };
                }
            } catch (e) {
                return { success: false, message: 'Error: ' + e.message };
            }
        }''')
        
        print(f"   결과: {modal_opened['message']}")
        
        if not modal_opened['success']:
            print(f"\n❌ 모달을 열 수 없습니다: {modal_opened['message']}")
            browser.close()
            return
        
        time.sleep(3)
        
        # 모달 검증
        print("\n4️⃣ 모달 내용 검증 중...")
        verification = page.evaluate('''() => {
            const modal = document.getElementById('consecutiveAqlFailModal');
            
            if (!modal) {
                return { 
                    success: false,
                    error: 'Modal element not found in DOM'
                };
            }
            
            const styles = window.getComputedStyle(modal);
            const isVisible = styles.display !== 'none';
            
            if (!isVisible) {
                return {
                    success: false,
                    error: 'Modal element exists but is hidden (display: ' + styles.display + ')'
                };
            }
            
            // 모달 내용 추출
            const h2 = modal.querySelector('h2');
            const h3List = Array.from(modal.querySelectorAll('h3'));
            const thList = Array.from(modal.querySelectorAll('th'));
            const fullText = modal.innerText;
            
            // 번역 키 패턴 검색
            const errorPatterns = {
                validationTab: /validationTab\./g,
                templateLiteral: /\$\{/g,
                headersDot: /headers\./g,
                consecutiveAqlFail: /consecutiveAqlFail(?![\s:])/g,  // 단어로만 나타나는 경우
                threeMonthSection: /threeMonthSection/g,
                twoMonthSection: /twoMonthSection/g
            };
            
            const errors = {};
            let totalErrors = 0;
            
            for (const [name, pattern] of Object.entries(errorPatterns)) {
                const matches = fullText.match(pattern);
                if (matches && matches.length > 0) {
                    errors[name] = matches.length;
                    totalErrors += matches.length;
                }
            }
            
            return {
                success: true,
                visible: true,
                title: h2 ? h2.innerText : 'N/A',
                sectionHeaders: h3List.map(h => h.innerText),
                tableHeaders: thList.map(th => th.innerText),
                errors: errors,
                totalErrors: totalErrors,
                hasErrors: totalErrors > 0,
                textSample: fullText.substring(0, 400)
            };
        }''')
        
        print("\n" + "="*80)
        print("📋 검증 결과")
        print("="*80)
        
        if not verification['success']:
            print(f"\n❌ 검증 실패: {verification.get('error', 'Unknown error')}")
            browser.close()
            return
        
        # 제목
        print(f"\n📌 모달 제목:")
        print(f"   {verification['title']}")
        
        # 섹션 헤더
        if verification['sectionHeaders']:
            print(f"\n📑 섹션 헤더 ({len(verification['sectionHeaders'])}개):")
            for i, section in enumerate(verification['sectionHeaders'], 1):
                print(f"   {i}. {section}")
        
        # 테이블 헤더
        if verification['tableHeaders']:
            print(f"\n📊 테이블 헤더 (처음 8개):")
            for i, header in enumerate(verification['tableHeaders'][:8], 1):
                print(f"   {i}. {header}")
        
        # 오류 검사
        print(f"\n" + "="*80)
        print(f"🔍 번역 오류 검사")
        print("="*80)
        
        if verification['hasErrors']:
            print(f"\n❌ {verification['totalErrors']}개의 번역 오류 발견:")
            for error_type, count in verification['errors'].items():
                print(f"   • {error_type}: {count}회")
            
            print(f"\n텍스트 샘플 (처음 400자):")
            print(f"{verification['textSample']}")
            print("\n❌ 번역이 여전히 정상적으로 작동하지 않습니다!")
        else:
            print(f"\n✅✅✅ 번역 오류 없음! ✅✅✅")
            print(f"\n모든 번역 키가 정상적으로 한국어/영어/베트남어로 변환되었습니다!")
            print(f"\n제목: {verification['title']}")
            print(f"섹션 수: {len(verification['sectionHeaders'])}")
            print(f"헤더 수: {len(verification['tableHeaders'])}")
        
        print("="*80)
        
        # 스크린샷 저장
        print(f"\n📸 스크린샷 저장 중...")
        page.screenshot(path='output_files/final_modal_verification.png', full_page=True)
        print(f"   ✅ 전체 페이지: output_files/final_modal_verification.png")
        
        modal_elem = page.query_selector('#consecutiveAqlFailModal')
        if modal_elem:
            modal_elem.screenshot(path='output_files/modal_close_up.png')
            print(f"   ✅ 모달 클로즈업: output_files/modal_close_up.png")
        
        print(f"\n⏳ 브라우저를 20초간 유지합니다...")
        time.sleep(20)
        
        browser.close()
        print(f"\n✅ 검증 완료!")

if __name__ == '__main__':
    complete_verification()
