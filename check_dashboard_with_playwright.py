"""
Playwright를 사용하여 대시보드의 모든 팝업과 데이터를 확인하는 스크립트
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

async def check_dashboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 대시보드 파일 열기
        dashboard_path = os.path.abspath("output_files/management_dashboard_2025_08.html")
        await page.goto(f"file://{dashboard_path}")
        await asyncio.sleep(2)
        
        print("=" * 60)
        print("대시보드 데이터 확인")
        print("=" * 60)
        
        # 1. 총인원 카드 확인
        print("\n1. 총인원 카드 확인:")
        # Check if the card exists first
        if await page.locator('div.card:has-text("총인원 정보")').count() > 0:
            # Get the total employee count from the summary section
            total_text = await page.locator('.summary-content').inner_text()
            print(f"   Summary content: {total_text}")
        else:
            print("   총인원 카드를 찾을 수 없습니다.")
        
        # 총인원 상세 분석 팝업 열기
        if await page.locator('div.card:has-text("총인원 정보")').count() > 0:
            await page.locator('div.card:has-text("총인원 정보")').click()
            await asyncio.sleep(1)
        else:
            print("   총인원 카드를 클릭할 수 없습니다.")
        
        # 팝업 내용 확인
        if await page.locator('#modal-total-employees').is_visible():
            print("\n   총인원 상세 분석 팝업:")
            
            # 팝업 내 차트 데이터 확인을 위한 JavaScript 실행
            chart_data = await page.evaluate('''
                () => {
                    const charts = {};
                    Chart.instances.forEach((chart, index) => {
                        if (chart.canvas.id) {
                            charts[chart.canvas.id] = {
                                type: chart.config.type,
                                labels: chart.config.data.labels,
                                datasets: chart.config.data.datasets.map(d => ({
                                    label: d.label,
                                    data: d.data
                                }))
                            };
                        }
                    });
                    return charts;
                }
            ''')
            
            if chart_data:
                for chart_id, data in chart_data.items():
                    if 'total-employees' in chart_id:
                        print(f"   차트 ID: {chart_id}")
                        print(f"   차트 타입: {data['type']}")
                        if 'datasets' in data:
                            for dataset in data['datasets']:
                                print(f"   데이터셋: {dataset['label']} = {dataset['data']}")
            
            # 팝업 닫기
            await page.locator('.modal .close-modal').first.click()
            await asyncio.sleep(0.5)
        
        # 2. 팀별 카드 데이터 확인
        print("\n2. 팀별 카드 확인:")
        # Find team cards with different selector
        team_cards = await page.locator('.card[onclick*="showModal"]').all()
        
        for i, card in enumerate(team_cards[:3]):  # 처음 3개 팀만 확인
            team_name = await card.locator('.card-title').inner_text()
            # Extract count from the card content
            card_content = await card.inner_text()
            # Parse the count from the content
            import re
            count_match = re.search(r'총인원:\s*(\d+)', card_content)
            team_count = count_match.group(1) if count_match else 'N/A'
            print(f"\n   팀: {team_name}")
            print(f"   인원: {team_count}")
            
            # 팀 상세 정보 팝업 열기
            await card.click()
            await asyncio.sleep(1)
            
            # 팝업이 열렸는지 확인
            modal_selector = f'.modal[style*="display: block"]'
            if await page.locator(modal_selector).count() > 0:
                print(f"   {team_name} 팀 상세 정보 팝업 열림")
                
                # 주차별 팀 인원 트렌드 차트 데이터 확인
                team_chart_data = await page.evaluate('''
                    () => {
                        const chartData = {};
                        Chart.instances.forEach((chart) => {
                            if (chart.canvas.id && chart.canvas.id.includes('weekly-trend')) {
                                const datasets = chart.config.data.datasets;
                                if (datasets && datasets.length > 0) {
                                    chartData[chart.canvas.id] = {
                                        labels: chart.config.data.labels,
                                        data: datasets[0].data
                                    };
                                }
                            }
                        });
                        return chartData;
                    }
                ''')
                
                for chart_id, data in team_chart_data.items():
                    if team_name.replace(' ', '_') in chart_id:
                        print(f"   주차별 트렌드: {data['data']}")
                
                # 테이블 데이터 확인
                table_rows = await page.locator(f'{modal_selector} table tbody tr').count()
                if table_rows > 0:
                    print(f"   테이블 행 수: {table_rows}")
                    
                    # 첫 번째 행 데이터 확인
                    first_row_data = await page.locator(f'{modal_selector} table tbody tr').first.inner_text()
                    print(f"   첫 번째 행: {first_row_data[:100]}...")
                
                # 팝업 닫기
                await page.locator(f'{modal_selector} .close-modal').click()
                await asyncio.sleep(0.5)
        
        # 3. 하드코딩된 값 검색
        print("\n3. 하드코딩된 값 검색:")
        
        # HTML 소스에서 하드코딩된 숫자 패턴 찾기
        html_content = await page.content()
        
        # 의심스러운 패턴들
        suspicious_patterns = [
            "108, 109, 109, 109",  # ASSEMBLY 팀 하드코딩
            "weekData = [108",
            "total: 100",
            "members[:100]"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in html_content:
                print(f"   ⚠️ 하드코딩 발견: '{pattern}'")
                # 패턴 주변 컨텍스트 찾기
                index = html_content.find(pattern)
                context = html_content[max(0, index-50):min(len(html_content), index+100)]
                print(f"      컨텍스트: ...{context}...")
        
        # JavaScript 변수 확인
        print("\n4. JavaScript 변수 확인:")
        js_data = await page.evaluate('''
            () => {
                return {
                    teamStats: typeof teamStats !== 'undefined' ? teamStats : null,
                    weeklyTeamData: typeof weeklyTeamData !== 'undefined' ? weeklyTeamData : null,
                    currentWeeklyData: typeof currentWeeklyData !== 'undefined' ? currentWeeklyData : null
                };
            }
        ''')
        
        if js_data['teamStats']:
            for team, stats in js_data['teamStats'].items():
                if team in ['ASSEMBLY', 'STITCHING', 'BOTTOM']:
                    print(f"   {team}: total = {stats.get('total', 'N/A')}")
        
        if js_data['weeklyTeamData']:
            print("\n   주차별 팀 데이터:")
            for week, teams in js_data['weeklyTeamData'].items():
                if 'ASSEMBLY' in teams:
                    print(f"   {week} ASSEMBLY: {teams['ASSEMBLY']}")
        
        print("\n" + "=" * 60)
        print("검사 완료")
        print("=" * 60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_dashboard())