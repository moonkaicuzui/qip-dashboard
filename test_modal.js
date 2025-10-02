const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html');
  
  // Click validation tab
  await page.click('#tabValidation');
  await page.waitForTimeout(1000);
  
  // Check console for errors
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
  
  // Wait and take screenshot
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'modal_test.png' });
  
  console.log('Screenshot saved!');
  
  await page.waitForTimeout(5000);
  await browser.close();
})();
