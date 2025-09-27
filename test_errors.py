import asyncio
from playwright.async_api import async_playwright
import os

async def test():
    dashboard = os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Collect errors
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        
        await page.goto(f'file://{dashboard}')
        await page.wait_for_timeout(1000)
        
        # Check if employeeData is defined
        result = await page.evaluate('''() => ({
            hasEmployeeData: typeof window.employeeData !== 'undefined',
            dataLength: typeof window.employeeData !== 'undefined' ? window.employeeData.length : 0,
            hasShowTab: typeof showTab === 'function'
        })''')
        
        print(f"Has employeeData: {result['hasEmployeeData']}")
        print(f"Data length: {result['dataLength']}")
        print(f"Has showTab: {result['hasShowTab']}")
        
        if errors:
            print(f"\nJavaScript errors: {len(errors)}")
            for err in errors:
                print(f"  - {err}")
        
        await browser.close()

asyncio.run(test())
