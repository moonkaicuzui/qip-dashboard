#!/usr/bin/env python3
"""
간단한 심층 테스트
"""

import asyncio
from playwright.async_api import async_playwright

async def simple_deep_test():
    dashboard = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    print("="*60)
    print("🔍 대시보드 심층 검증")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 브라우저 표시
        page = await browser.new_page()

        # 에러 수집
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

        # 페이지 로드
        print("\n[1] 페이지 로드 중...")
        await page.goto(f"file://{dashboard}")
        await page.wait_for_timeout(2000)

        # 기본 체크
        basic = await page.evaluate("""() => ({
            hasData: typeof employeeData !== 'undefined' && employeeData.length > 0,
            dataCount: typeof employeeData !== 'undefined' ? employeeData.length : 0,
            type1Count: typeof employeeData !== 'undefined' ?
                employeeData.filter(e => e.type === 'TYPE-1').length : 0,
            type2Count: typeof employeeData !== 'undefined' ?
                employeeData.filter(e => e.type === 'TYPE-2').length : 0,
            with5PRS: typeof employeeData !== 'undefined' ?
                employeeData.filter(e => e['5PRS_Pass_Rate'] > 0).length : 0,
            showTab: typeof showTab === 'function',
            summaryRows: document.querySelectorAll('#typeSummaryBody tr').length
        })""")

        print(f"\n✅ 데이터 로드: {basic['dataCount']}명")
        print(f"   TYPE-1: {basic['type1Count']}명")
        print(f"   TYPE-2: {basic['type2Count']}명")
        print(f"   5PRS 데이터: {basic['with5PRS']}명")
        print(f"   요약 테이블: {basic['summaryRows']}행")

        # 탭 전환 테스트
        print("\n[2] 탭 전환 테스트...")

        # Position 탭
        await page.click('div.tab[data-tab="position"]')
        await page.wait_for_timeout(1000)
        position_content = await page.query_selector('#positionContent')
        if position_content:
            html = await position_content.inner_html()
            print(f"✅ Position 탭: {len(html)} 글자")

            # View 버튼 확인
            buttons = await page.query_selector_all('button.btn-outline-primary')
            print(f"   View 버튼: {len(buttons)}개")

            if len(buttons) > 0:
                # 첫 번째 버튼 클릭
                await buttons[0].click()
                await page.wait_for_timeout(1500)

                # 모달 확인
                modal = await page.query_selector('#employeeModal')
                if modal and await modal.is_visible():
                    print("   ✅ 모달 열림!")

                    # AQL/5PRS 체크
                    modal_data = await page.evaluate("""() => {
                        const tables = document.querySelectorAll('#employeeModal table');
                        if (tables.length === 0) return null;

                        const rows = tables[0].querySelectorAll('tbody tr');
                        let hasAQL = false, has5PRS = false;

                        rows.forEach(row => {
                            const text = row.innerText;
                            if (text.includes('AQL')) hasAQL = true;
                            if (text.includes('5PRS') || text.includes('PRS')) has5PRS = true;
                        });

                        return { hasAQL, has5PRS };
                    }""")

                    if modal_data:
                        print(f"   AQL 조건: {'✅' if modal_data['hasAQL'] else '❌'}")
                        print(f"   5PRS 조건: {'✅' if modal_data['has5PRS'] else '❌'}")

                    # 모달 닫기
                    await page.keyboard.press('Escape')
                else:
                    print("   ❌ 모달이 안 열림")
        else:
            print("❌ Position 탭 콘텐츠 없음")

        # Detail 탭
        await page.click('div.tab[data-tab="detail"]')
        await page.wait_for_timeout(1000)
        detail_table = await page.query_selector('#detailTable')
        if detail_table:
            rows = await page.query_selector_all('#detailTable tbody tr')
            print(f"✅ Detail 탭: {len(rows)}명 표시")

        # 언어 변경
        print("\n[3] 언어 변경 테스트...")
        language = await page.query_selector('#languageSelect')
        if language:
            await language.select_option('en')
            await page.wait_for_timeout(500)

            title = await page.query_selector('#mainTitle')
            if title:
                text = await title.inner_text()
                if 'QIP' in text:
                    print("✅ 영어 변경 성공")

            await language.select_option('ko')
            print("✅ 한국어 복원")

        # 에러 확인
        print(f"\n[4] JavaScript 에러: {len(errors)}개")
        if errors:
            for err in errors[:3]:
                print(f"   - {str(err)[:100]}")

        # 총평
        print("\n" + "="*60)
        print("📊 검증 결과:")

        score = 0
        if basic['hasData']: score += 1
        if basic['showTab']: score += 1
        if basic['summaryRows'] > 0: score += 1
        if len(buttons) > 0: score += 1
        if basic['with5PRS'] > 0: score += 1

        print(f"점수: {score}/5")

        if score == 5:
            print("✅ 모든 기능 정상!")
        elif score >= 3:
            print("⚠️ 일부 기능 수정 필요")
        else:
            print("❌ 주요 문제 발견")

        print("\n브라우저를 15초간 열어둡니다...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_deep_test())