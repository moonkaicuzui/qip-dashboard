#!/usr/bin/env python3
"""
Automated test to verify dashboard fixes for multi-language support and calculation logic
Tests the following issues:
1. Fulfilled/Not Fulfilled calculation logic
2. 'people' unit suffix removal from position filter  
3. Calculation basis values display
4. '평가 대상 아님' switches to English/Vietnamese
5. '5PRS 조건' header switches languages
6. Fulfillment rate calculation
"""

import asyncio
import time
from pathlib import Path

# Initialize Playwright browser
print("🔧 Initializing Playwright browser...")
import mcp__playwright__browser_navigate
import mcp__playwright__browser_snapshot
import mcp__playwright__browser_click
import mcp__playwright__browser_evaluate
import mcp__playwright__browser_take_screenshot

async def test_dashboard():
    """Test dashboard fixes for all reported issues"""
    
    # Navigate to dashboard
    dashboard_path = Path("/Users/ksmoon/Downloads/대시보드 인센티브 테스트8_구글 연동 완료_by Macbook air copy/output_files/dashboard_version4.html")
    file_url = f"file://{dashboard_path}"
    
    print(f"📂 Opening dashboard: {file_url}")
    await mcp__playwright__browser_navigate.browser_navigate({"url": file_url})
    time.sleep(2)
    
    # Test 1: Check initial Korean state
    print("\n✅ Test 1: Korean language state")
    await mcp__playwright__browser_take_screenshot.browser_take_screenshot({
        "filename": "test_korean_state.png",
        "fullPage": False
    })
    
    # Switch to English
    print("\n✅ Test 2: Switching to English...")
    await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": "() => { document.getElementById('languageSelector').value = 'en'; changeLanguage(); }"
    })
    time.sleep(1)
    
    # Take snapshot to check English translations
    print("   Checking English translations...")
    snapshot = await mcp__playwright__browser_snapshot.browser_snapshot({})
    
    # Check for Korean text that should be translated
    issues_found = []
    
    # Check if '평가 대상 아님' is still present (should be 'Not Applicable')
    if '평가 대상 아님' in str(snapshot):
        issues_found.append("❌ '평가 대상 아님' still present in English mode")
    else:
        print("   ✅ '평가 대상 아님' correctly translated")
    
    # Check if '5PRS 조건' is still present (should be '5PRS Conditions')
    if '5PRS 조건' in str(snapshot):
        issues_found.append("❌ '5PRS 조건' still present in English mode")
    else:
        print("   ✅ '5PRS 조건' correctly translated")
        
    # Check if Korean '명' unit is still present (should be 'people' or removed)
    if '명' in str(snapshot) and 'people' not in str(snapshot):
        issues_found.append("❌ Korean '명' unit still present")
    else:
        print("   ✅ Unit translations working")
    
    await mcp__playwright__browser_take_screenshot.browser_take_screenshot({
        "filename": "test_english_state.png",
        "fullPage": False
    })
    
    # Test 3: Click on Position Detail tab
    print("\n✅ Test 3: Testing Position Detail tab...")
    await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": "() => { showTab('position'); }"
    })
    time.sleep(1)
    
    # Click on a detail button to open modal
    print("   Opening position detail modal...")
    await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": """() => {
            const buttons = document.querySelectorAll('button[onclick*="showPositionDetail"]');
            if (buttons.length > 0) {
                buttons[0].click();
                return true;
            }
            return false;
        }"""
    })
    time.sleep(2)
    
    # Check modal content
    print("   Checking modal content...")
    modal_check = await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": """() => {
            const modal = document.getElementById('positionDetailModal');
            if (!modal) return {error: 'Modal not found'};
            
            // Check for Fulfilled/Not Fulfilled values
            const tables = modal.querySelectorAll('table');
            let hasValues = false;
            let calculationBasis = [];
            
            tables.forEach(table => {
                const cells = table.querySelectorAll('td');
                cells.forEach(cell => {
                    const text = cell.textContent;
                    // Check if we have actual numbers for fulfilled/not fulfilled
                    if (text.includes('명') || text.includes('people')) {
                        const match = text.match(/\\d+/);
                        if (match && parseInt(match[0]) > 0) {
                            hasValues = true;
                        }
                    }
                    // Check calculation basis column
                    if (cell.classList.contains('text-muted')) {
                        calculationBasis.push(text.trim());
                    }
                });
            });
            
            // Check fulfillment rate
            const progressBars = modal.querySelectorAll('.progress-bar');
            let rates = [];
            progressBars.forEach(bar => {
                const width = bar.style.width;
                if (width && width !== '0%') {
                    rates.push(width);
                }
            });
            
            return {
                hasValues: hasValues,
                calculationBasisCount: calculationBasis.filter(b => b && b !== '-').length,
                fulfillmentRates: rates,
                modalVisible: modal.style.display !== 'none'
            };
        }"""
    })
    
    if modal_check.get('hasValues'):
        print("   ✅ Fulfilled/Not Fulfilled values are being calculated")
    else:
        issues_found.append("❌ Fulfilled/Not Fulfilled showing 0 values")
    
    if modal_check.get('calculationBasisCount', 0) > 0:
        print("   ✅ Calculation basis values are displayed")
    else:
        issues_found.append("❌ Calculation basis column is empty")
        
    if len(modal_check.get('fulfillmentRates', [])) > 0:
        print(f"   ✅ Fulfillment rates calculated: {modal_check.get('fulfillmentRates')[:3]}...")
    else:
        issues_found.append("❌ Fulfillment rates showing 0%")
    
    await mcp__playwright__browser_take_screenshot.browser_take_screenshot({
        "filename": "test_modal_english.png",
        "fullPage": False
    })
    
    # Close modal
    await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": "() => { bootstrap.Modal.getInstance(document.getElementById('positionDetailModal')).hide(); }"
    })
    time.sleep(1)
    
    # Test 4: Switch to Vietnamese
    print("\n✅ Test 4: Switching to Vietnamese...")
    await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": "() => { document.getElementById('languageSelector').value = 'vi'; changeLanguage(); }"
    })
    time.sleep(1)
    
    # Check Vietnamese translations
    snapshot_vi = await mcp__playwright__browser_snapshot.browser_snapshot({})
    
    if '평가 대상 아님' in str(snapshot_vi):
        issues_found.append("❌ Korean text still present in Vietnamese mode")
    else:
        print("   ✅ Vietnamese translations working")
    
    await mcp__playwright__browser_take_screenshot.browser_take_screenshot({
        "filename": "test_vietnamese_state.png",
        "fullPage": False
    })
    
    # Test 5: Check position filter dropdown
    print("\n✅ Test 5: Checking position filter dropdown...")
    await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": "() => { showTab('detail'); updatePositionFilter(); }"
    })
    time.sleep(1)
    
    dropdown_check = await mcp__playwright__browser_evaluate.browser_evaluate({
        "function": """() => {
            const select = document.getElementById('positionFilter');
            if (!select) return {error: 'Dropdown not found'};
            
            const options = Array.from(select.options).map(opt => opt.textContent);
            const hasPeopleSuffix = options.some(opt => opt.includes(' people'));
            
            return {
                optionCount: options.length,
                hasPeopleSuffix: hasPeopleSuffix,
                sampleOptions: options.slice(0, 5)
            };
        }"""
    })
    
    if not dropdown_check.get('hasPeopleSuffix', True):
        print("   ✅ 'people' suffix removed from dropdown")
    else:
        issues_found.append("❌ 'people' suffix still present in dropdown")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if len(issues_found) == 0:
        print("✅ ALL TESTS PASSED! All fixes are working correctly.")
    else:
        print(f"⚠️ {len(issues_found)} issues found:")
        for issue in issues_found:
            print(f"   {issue}")
    
    print("\n📸 Screenshots saved:")
    print("   - test_korean_state.png")
    print("   - test_english_state.png")
    print("   - test_modal_english.png")
    print("   - test_vietnamese_state.png")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_dashboard())
    exit(0 if success else 1)