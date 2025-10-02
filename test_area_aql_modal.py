from playwright.sync_api import sync_playwright
import time

def test_area_aql_modal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={'width': 1920, 'height': 1200})
        page = context.new_page()

        print("\n" + "="*80)
        print("🔍 Area AQL Reject Rate 모달 검증 테스트")
        print("="*80)

        # 대시보드 로드
        print("\n1️⃣ 대시보드 로드 중...")
        page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html')

        page.wait_for_load_state('networkidle')
        time.sleep(10)

        # Validation 탭 클릭
        print("\n2️⃣ 'Validation' 탭으로 이동 중...")
        page.click('#tabValidation')
        time.sleep(3)

        # 스크롤하여 AREA AQL 카드 찾기
        page.evaluate('window.scrollTo(0, 800)')
        time.sleep(2)

        # Area AQL Reject Rate 모달 열기
        print("\n3️⃣ Area AQL Reject Rate 모달 열기 중...")
        modal_opened = page.evaluate('''() => {
            try {
                if (typeof showAreaRejectRateDetails === 'function') {
                    showAreaRejectRateDetails();
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

        # 모달 내용 검증
        print("\n4️⃣ 모달 내용 검증 중...")
        verification = page.evaluate('''() => {
            const modal = document.getElementById('detailModal');

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

            // 모달 제목
            const h5 = modal.querySelector('h5.modal-title');
            const title = h5 ? h5.innerText : 'N/A';

            // 전체 텍스트
            const fullText = modal.innerText;

            // 테이블 찾기
            const tables = modal.querySelectorAll('table');
            const tableCount = tables.length;

            // 첫 번째 테이블 헤더
            const firstTableHeaders = tables[0] ?
                Array.from(tables[0].querySelectorAll('th')).map(th => th.innerText) : [];

            // 첫 번째 테이블 데이터 행 수
            const firstTableRows = tables[0] ?
                tables[0].querySelectorAll('tbody tr').length : 0;

            // Building 정보 추출 (tbody의 첫 번째 셀)
            const buildings = tables[0] ?
                Array.from(tables[0].querySelectorAll('tbody tr')).map(tr => {
                    const cells = tr.querySelectorAll('td');
                    return {
                        building: cells[0] ? cells[0].innerText : '',
                        employees: cells[1] ? cells[1].innerText : '',
                        cond7Fail: cells[2] ? cells[2].innerText : '',
                        cond8Fail: cells[3] ? cells[3].innerText : '',
                        rejectRate: cells[4] ? cells[4].innerText : '',
                        grade: cells[5] ? cells[5].innerText : ''
                    };
                }) : [];

            // AQL 관련 직원 수 확인
            const employeeCountMatch = fullText.match(/AQL 검사 수행 직원 (\d+)명/);
            const aqlEmployeeCount = employeeCountMatch ? parseInt(employeeCountMatch[1]) : null;

            return {
                success: true,
                visible: true,
                title: title,
                tableCount: tableCount,
                firstTableHeaders: firstTableHeaders,
                firstTableRows: firstTableRows,
                buildings: buildings,
                aqlEmployeeCount: aqlEmployeeCount,
                textSample: fullText.substring(0, 500)
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

        # AQL 직원 수
        if verification['aqlEmployeeCount']:
            print(f"\n👥 AQL 관련 직원 수: {verification['aqlEmployeeCount']}명")
            if verification['aqlEmployeeCount'] == 38:
                print(f"   ✅ 예상 인원 (38명) 일치!")
            else:
                print(f"   ⚠️ 예상 인원 38명과 불일치!")

        # 테이블 수
        print(f"\n📊 테이블 수: {verification['tableCount']}개")

        # 첫 번째 테이블 헤더
        if verification['firstTableHeaders']:
            print(f"\n📋 첫 번째 테이블 헤더:")
            for i, header in enumerate(verification['firstTableHeaders'], 1):
                print(f"   {i}. {header}")

        # Building 데이터
        if verification['buildings']:
            print(f"\n🏢 Building 데이터 ({verification['firstTableRows']}개):")
            for building in verification['buildings']:
                print(f"\n   Building: {building['building']}")
                print(f"   - AQL 팀 인원: {building['employees']}")
                print(f"   - 조건7 미충족: {building['cond7Fail']}")
                print(f"   - 조건8 미충족: {building['cond8Fail']}")
                print(f"   - Reject Rate: {building['rejectRate']}")
                print(f"   - 성과 등급: {building['grade']}")

        # 텍스트 샘플
        print(f"\n📝 모달 텍스트 샘플 (처음 500자):")
        print(f"{verification['textSample']}")

        print("\n" + "="*80)

        # 스크린샷
        print(f"\n📸 스크린샷 저장 중...")
        page.screenshot(path='output_files/area_aql_modal_verification.png', full_page=True)
        print(f"   ✅ 전체 페이지: output_files/area_aql_modal_verification.png")

        modal_elem = page.query_selector('#detailModal')
        if modal_elem:
            modal_elem.screenshot(path='output_files/area_aql_modal_closeup.png')
            print(f"   ✅ 모달 클로즈업: output_files/area_aql_modal_closeup.png")

        print(f"\n⏳ 브라우저를 20초간 유지합니다...")
        time.sleep(20)

        browser.close()
        print(f"\n✅ 검증 완료!")

if __name__ == '__main__':
    test_area_aql_modal()
