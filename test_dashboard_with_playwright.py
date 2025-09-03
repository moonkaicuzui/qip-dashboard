#!/usr/bin/env python3
"""
Playwright를 사용하여 대시보드 팀/역할 매핑 검증
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_dashboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 대시보드 열기
        dashboard_path = "file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트8.3_구글 연동 완료_by Macbook pro_조건 매트릭스 JSON 파일 도입_버전 5_action.sh 테스트/output_files/management_dashboard_2025_08.html"
        await page.goto(dashboard_path)
        
        print("=" * 80)
        print("대시보드 팀/역할 매핑 시각적 검증")
        print("=" * 80)
        
        # 페이지 로드 대기
        await page.wait_for_timeout(2000)
        
        # 트리맵 섹션 찾기
        treemap_exists = await page.locator("#teamTreemap").is_visible()
        print(f"\n✅ 트리맵 렌더링: {'성공' if treemap_exists else '실패'}")
        
        # 팀별 인원 확인 (트리맵 셀에서)
        team_cells = await page.locator(".treemap-cell").all()
        print(f"\n📊 트리맵에 표시된 팀 수: {len(team_cells)}개")
        
        # 각 팀 셀 정보 추출
        print("\n🏢 팀별 정보:")
        print("-" * 80)
        
        for i, cell in enumerate(team_cells[:5], 1):  # 상위 5개 팀만
            try:
                # 팀 이름과 인원 수 추출
                team_text = await cell.inner_text()
                lines = team_text.strip().split('\n')
                
                if len(lines) >= 2:
                    team_name = lines[0]
                    count_info = lines[1] if len(lines) > 1 else ""
                    
                    print(f"{i}. {team_name}: {count_info}")
                    
                    # 팀 클릭하여 역할 분포 확인
                    await cell.click()
                    await page.wait_for_timeout(500)
                    
                    # 모달 또는 팝업 확인
                    modal_visible = await page.locator(".modal").is_visible()
                    if modal_visible:
                        modal_content = await page.locator(".modal-body").inner_text()
                        print(f"   └─ 역할 정보 팝업: 표시됨")
                        # 모달 닫기
                        close_btn = page.locator(".close-modal").first
                        if await close_btn.is_visible():
                            await close_btn.click()
                            await page.wait_for_timeout(300)
                    
            except Exception as e:
                print(f"   ⚠️ 셀 {i} 처리 중 오류: {e}")
        
        # ASSEMBLY 팀 특별 확인
        print("\n🔍 ASSEMBLY 팀 상세 확인:")
        print("-" * 80)
        
        assembly_cells = await page.locator(".treemap-cell:has-text('ASSEMBLY')").all()
        if assembly_cells:
            assembly_cell = assembly_cells[0]
            assembly_text = await assembly_cell.inner_text()
            print(f"ASSEMBLY 팀 정보: {assembly_text}")
            
            # ASSEMBLY 클릭하여 역할 확인
            await assembly_cell.click()
            await page.wait_for_timeout(1000)
            
            # 역할 분포 확인
            role_info = await page.evaluate("""
                () => {
                    const cells = document.querySelectorAll('.treemap-cell');
                    for (let cell of cells) {
                        if (cell.textContent.includes('ASSEMBLY')) {
                            // onclick 속성에서 데이터 추출 시도
                            const onclick = cell.getAttribute('onclick');
                            if (onclick && onclick.includes('showTeamDetails')) {
                                return onclick;
                            }
                        }
                    }
                    return null;
                }
            """)
            
            if role_info:
                print(f"   역할 매핑 함수 호출 확인: ✅")
        
        # 주요 통계 확인
        print("\n📈 대시보드 주요 통계:")
        print("-" * 80)
        
        # 총 직원 수 확인
        stat_cards = await page.locator(".stat-card").all()
        for card in stat_cards[:4]:  # 상위 4개 통계만
            card_text = await card.inner_text()
            print(f"   {card_text.replace(chr(10), ' - ')}")
        
        # 5초 대기 후 종료
        print("\n⏳ 5초 후 브라우저가 자동으로 닫힙니다...")
        await page.wait_for_timeout(5000)
        
        await browser.close()
        
        print("\n✅ 검증 완료!")

if __name__ == "__main__":
    asyncio.run(test_dashboard())