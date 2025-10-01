#!/usr/bin/env python3
"""
3개월 연속 AQL FAIL 모달 디버깅 테스트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 3개월 연속 AQL FAIL 모달 디버깅\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless=False to see what's happening
    page = browser.new_page()
    
    # Console log capture
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: print(f"[ERROR] {err}"))
    
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Go to Validation tab
    print("📊 Opening Validation tab...")
    page.click("#tabValidation")
    time.sleep(2)
    
    # Check if the card exists
    print("\n🔍 Checking card #7...")
    card_check = page.evaluate("""
        () => {
            const cards = document.querySelectorAll('.kpi-card');
            const card7 = cards[6];  // 0-indexed, so index 6 is card #7
            if (!card7) return { exists: false };
            
            const label = card7.querySelector('.kpi-label')?.textContent;
            const onclick = card7.getAttribute('onclick');
            
            return {
                exists: true,
                label: label,
                onclick: onclick,
                hasOnclick: onclick !== null
            };
        }
    """)
    
    print(f"Card exists: {card_check['exists']}")
    print(f"Label: {card_check.get('label', 'N/A')}")
    print(f"Onclick: {card_check.get('onclick', 'N/A')}")
    print(f"Has onclick: {card_check.get('hasOnclick', False)}")
    
    # Try to click the card
    print("\n🖱️  Attempting to click card...")
    try:
        page.evaluate("""
            () => {
                const cards = document.querySelectorAll('.kpi-card');
                const card7 = cards[6];
                if (card7) {
                    console.log('Clicking card 7...');
                    card7.click();
                }
            }
        """)
        time.sleep(3)  # Wait longer for modal to appear
        
        # Check if modal appeared
        modal_check = page.evaluate("""
            () => {
                const modal = document.getElementById('consecutiveAqlFailModal');
                if (!modal) {
                    console.log('Modal element not found');
                    return { found: false };
                }
                
                const isVisible = modal.style.display === 'block';
                console.log('Modal display style:', modal.style.display);
                
                return {
                    found: true,
                    visible: isVisible,
                    display: modal.style.display,
                    innerHTML: modal.innerHTML.substring(0, 200)
                };
            }
        """)
        
        print(f"\nModal found: {modal_check.get('found', False)}")
        print(f"Modal visible: {modal_check.get('visible', False)}")
        print(f"Display style: {modal_check.get('display', 'N/A')}")
        if modal_check.get('innerHTML'):
            print(f"HTML preview: {modal_check['innerHTML']}...")
            
    except Exception as e:
        print(f"❌ Error during click: {e}")
    
    time.sleep(5)  # Keep browser open to inspect
    browser.close()

print("\n✅ Debug test complete")
