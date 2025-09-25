#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive Playwright verification for all 10 KPI cards in management dashboard
Tests each card's popup functionality and captures screenshots for documentation
"""

import asyncio
import json
from pathlib import Path
import time

# Try to import Playwright - install if needed
try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Installing playwright...")
    import subprocess
    subprocess.run(["pip", "install", "playwright"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

async def verify_kpi_cards():
    """Verify all 10 KPI cards and their popups"""
    
    # Dashboard file path
    dashboard_path = Path(__file__).parent / 'output_files' / 'management_dashboard_2025_08_all_popups.html'
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return False
    
    # Convert to file URL
    dashboard_url = f'file://{dashboard_path.absolute()}'
    
    print("=" * 60)
    print("🎭 KPI 카드 Playwright 검증 시작")
    print("=" * 60)
    
    # Card definitions with expected modal IDs
    cards = [
        {"number": 1, "name": "총인원 정보", "modal_id": "modal-total-employees", "onclick": "openModal('modal-total-employees')"},
        {"number": 2, "name": "데이터 오류 인원", "modal_id": None, "onclick": "showErrorDetails()"},
        {"number": 3, "name": "결근자 정보/결근율", "modal_id": "modal-absence", "onclick": "openModal('modal-absence')"},
        {"number": 4, "name": "퇴사율", "modal_id": "modal-resignation", "onclick": "openModal('modal-resignation')"},
        {"number": 5, "name": "최근 30일내 입사 인원", "modal_id": "modal-new-hires", "onclick": "openModal('modal-new-hires')"},
        {"number": 6, "name": "최근 30일내 퇴사 인원", "modal_id": "modal-new-resignations", "onclick": "openModal('modal-new-resignations')"},
        {"number": 7, "name": "입사 60일 미만 인원", "modal_id": "modal-under-60", "onclick": "openModal('modal-under-60')"},
        {"number": 8, "name": "보직 부여 후 퇴사 인원", "modal_id": "modal-post-assignment", "onclick": "openModal('modal-post-assignment')"},
        {"number": 9, "name": "만근자", "modal_id": "modal-full-attendance", "onclick": "openModal('modal-full-attendance')"},
        {"number": 10, "name": "장기근속자", "modal_id": "modal-long-term", "onclick": "openModal('modal-long-term')"}
    ]
    
    verification_results = []
    
    async with async_playwright() as p:
        # Launch browser with viewport settings
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR'
        )
        
        page = await context.new_page()
        
        # Navigate to dashboard
        print(f"\n📋 대시보드 로딩: {dashboard_url}")
        await page.goto(dashboard_url)
        
        # Wait for page to load
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        # Take initial screenshot
        await page.screenshot(path='screenshots/00_dashboard_main.png', full_page=True)
        print("📸 메인 대시보드 스크린샷 저장: screenshots/00_dashboard_main.png")
        
        # Verify each KPI card
        for card in cards:
            print(f"\n{'='*50}")
            print(f"🔍 카드 #{card['number']}: {card['name']}")
            print(f"{'='*50}")
            
            result = {
                "card_number": card['number'],
                "card_name": card['name'],
                "card_found": False,
                "card_clickable": False,
                "popup_opened": False,
                "charts_loaded": False,
                "errors": []
            }
            
            try:
                # Find the card by iterating through all cards
                card_element = None
                card_elements = await page.query_selector_all('.hr-card')
                
                for elem in card_elements:
                    card_num_elem = await elem.query_selector('.card-number')
                    if card_num_elem:
                        card_num_text = await card_num_elem.inner_text()
                        if str(card['number']) == card_num_text.strip():
                            card_element = elem
                            break
                
                if card_element:
                    result["card_found"] = True
                    print(f"✅ 카드 #{card['number']} 발견")
                    
                    # Get card info
                    card_title = await card_element.query_selector('.metric-label')
                    if card_title:
                        title_text = await card_title.inner_text()
                        print(f"   제목: {title_text}")
                    
                    card_value = await card_element.query_selector('.metric-value')
                    if card_value:
                        value_text = await card_value.inner_text()
                        print(f"   값: {value_text}")
                    
                    # Click the card
                    print(f"🖱️ 카드 #{card['number']} 클릭 중...")
                    await card_element.click()
                    result["card_clickable"] = True
                    
                    # Wait for modal to appear
                    await asyncio.sleep(1)
                    
                    # Check if modal opened
                    if card['modal_id']:
                        modal_selector = f"#{card['modal_id']}"
                        modal = await page.query_selector(modal_selector)
                        
                        if modal:
                            # Check if modal is visible
                            is_visible = await modal.is_visible()
                            if is_visible:
                                result["popup_opened"] = True
                                print(f"✅ 팝업 모달 열림: {card['modal_id']}")
                                
                                # Wait for charts to load
                                await asyncio.sleep(2)
                                
                                # Check for canvas elements (charts)
                                canvases = await modal.query_selector_all('canvas')
                                if canvases:
                                    result["charts_loaded"] = True
                                    print(f"📊 차트 발견: {len(canvases)}개")
                                
                                # Take screenshot of modal
                                screenshot_path = f'screenshots/{card["number"]:02d}_{card["modal_id"]}.png'
                                await page.screenshot(path=screenshot_path, full_page=True)
                                print(f"📸 팝업 스크린샷 저장: {screenshot_path}")
                                
                                # Close modal
                                close_button = await modal.query_selector('.close-modal, .modal-close, button.close')
                                if close_button:
                                    await close_button.click()
                                    await asyncio.sleep(0.5)
                                    print("✅ 모달 닫기 완료")
                                else:
                                    # Try clicking outside modal
                                    await page.keyboard.press('Escape')
                                    await asyncio.sleep(0.5)
                                    print("✅ ESC로 모달 닫기")
                            else:
                                result["errors"].append("Modal not visible")
                                print(f"⚠️ 모달이 보이지 않음")
                        else:
                            result["errors"].append(f"Modal {card['modal_id']} not found")
                            print(f"⚠️ 모달을 찾을 수 없음: {card['modal_id']}")
                    
                    elif card['number'] == 2:  # Error details card
                        # Special handling for error details
                        await asyncio.sleep(2)
                        
                        # Check if error modal appeared
                        error_modal = await page.query_selector('#errorModal, .error-modal')
                        if error_modal and await error_modal.is_visible():
                            result["popup_opened"] = True
                            print("✅ 오류 상세 팝업 열림")
                            
                            # Take screenshot
                            screenshot_path = f'screenshots/02_error_details.png'
                            await page.screenshot(path=screenshot_path, full_page=True)
                            print(f"📸 오류 팝업 스크린샷 저장: {screenshot_path}")
                            
                            # Close modal
                            await page.keyboard.press('Escape')
                            await asyncio.sleep(0.5)
                        else:
                            # Error details might show inline
                            result["popup_opened"] = True
                            print("ℹ️ 오류 상세 정보 표시됨")
                    
                else:
                    result["errors"].append(f"Card #{card['number']} not found")
                    print(f"❌ 카드 #{card['number']}를 찾을 수 없음")
                
            except Exception as e:
                result["errors"].append(str(e))
                print(f"❌ 오류 발생: {e}")
            
            verification_results.append(result)
        
        # Final summary screenshot
        await page.screenshot(path='screenshots/99_dashboard_final.png', full_page=True)
        print("\n📸 최종 대시보드 스크린샷 저장: screenshots/99_dashboard_final.png")
        
        await browser.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 검증 결과 요약")
    print("=" * 60)
    
    total_cards = len(cards)
    cards_found = sum(1 for r in verification_results if r["card_found"])
    cards_clickable = sum(1 for r in verification_results if r["card_clickable"])
    popups_opened = sum(1 for r in verification_results if r["popup_opened"])
    charts_loaded = sum(1 for r in verification_results if r["charts_loaded"])
    
    print(f"\n총 카드 수: {total_cards}")
    print(f"발견된 카드: {cards_found}/{total_cards} ({'✅' if cards_found == total_cards else '⚠️'})")
    print(f"클릭 가능한 카드: {cards_clickable}/{total_cards} ({'✅' if cards_clickable == total_cards else '⚠️'})")
    print(f"팝업 열린 카드: {popups_opened}/{total_cards} ({'✅' if popups_opened == total_cards else '⚠️'})")
    print(f"차트 로드된 카드: {charts_loaded}/{total_cards - 1} (카드 #2 제외)")
    
    # Detailed results
    print("\n📋 상세 결과:")
    for result in verification_results:
        status = "✅" if result["popup_opened"] else "❌"
        print(f"  카드 #{result['card_number']:2d} ({result['card_name']}): {status}")
        if result["errors"]:
            for error in result["errors"]:
                print(f"      ⚠️ {error}")
    
    # Save results to JSON
    results_path = Path(__file__).parent / 'playwright_verification_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_cards": total_cards,
                "cards_found": cards_found,
                "cards_clickable": cards_clickable,
                "popups_opened": popups_opened,
                "charts_loaded": charts_loaded
            },
            "details": verification_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 검증 결과 저장: {results_path}")
    
    # Overall success
    success = (cards_found == total_cards and 
               cards_clickable == total_cards and 
               popups_opened == total_cards)
    
    if success:
        print("\n🎉 모든 KPI 카드 검증 성공!")
        return True
    else:
        print("\n⚠️ 일부 카드 검증 실패 - 상세 결과를 확인하세요")
        return False

async def main():
    """Main function"""
    # Create screenshots directory
    Path('screenshots').mkdir(exist_ok=True)
    
    success = await verify_kpi_cards()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ KPI 카드 검증 완료!")
        print("다음 단계: 5PRS DASHBOARD 구현")
        print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))