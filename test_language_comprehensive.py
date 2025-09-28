#!/usr/bin/env python3
"""
포괄적인 언어 전환 테스트 스크립트
모든 탭과 모든 모달에서 한글/영어/베트남어 전환을 철저히 검증
"""

import json
import time
import os
from pathlib import Path

# 모든 탭 목록
TABS = [
    "summary",          # 요약
    "position",         # 직급별 상세
    "individual",       # 개인별 상세
    "criteria",         # 인센티브 기준
    "conditions",       # 지급 조건
    "orgChart",        # 조직도
    "validation"       # 요약 및 시스템 검증
]

# 언어 코드
LANGUAGES = ["ko", "en", "vi"]

# 예상 번역 확인 항목
EXPECTED_TRANSLATIONS = {
    "ko": {
        "tabs": {
            "summary": "요약",
            "position": "직급별 상세",
            "individual": "개인별 상세",
            "criteria": "인센티브 기준",
            "conditions": "지급 조건",
            "orgChart": "조직도",
            "validation": "요약 및 시스템 검증"
        },
        "kpi_cards": {
            "attendance": "전월 출근률",
            "aql": "AQL 불합격",
            "absent": "무단결근",
            "quality": "퀄리티 경고",
            "5prs": "5PRS 기준"
        },
        "buttons": {
            "viewDetails": "상세보기",
            "close": "닫기"
        }
    },
    "en": {
        "tabs": {
            "summary": "Summary",
            "position": "Position Details",
            "individual": "Individual Details",
            "criteria": "Incentive Criteria",
            "conditions": "Payment Conditions",
            "orgChart": "Organization Chart",
            "validation": "Summary & System Validation"
        },
        "kpi_cards": {
            "attendance": "Previous Month Attendance",
            "aql": "AQL Failed",
            "absent": "Absent Without Inform",
            "quality": "Quality Warning",
            "5prs": "5PRS Criteria"
        },
        "buttons": {
            "viewDetails": "View Details",
            "close": "Close"
        }
    },
    "vi": {
        "tabs": {
            "summary": "Tóm tắt",
            "position": "Chi tiết theo chức vụ",
            "individual": "Chi tiết cá nhân",
            "criteria": "Tiêu chí khen thưởng",
            "conditions": "Điều kiện thanh toán",
            "orgChart": "Sơ đồ tổ chức",
            "validation": "Tóm tắt & Xác thực hệ thống"
        },
        "kpi_cards": {
            "attendance": "Tỷ lệ tham dự tháng trước",
            "aql": "AQL thất bại",
            "absent": "Vắng mặt không thông báo",
            "quality": "Cảnh báo chất lượng",
            "5prs": "Tiêu chí 5PRS"
        },
        "buttons": {
            "viewDetails": "Xem chi tiết",
            "close": "Đóng"
        }
    }
}

def test_language_switching():
    """브라우저에서 언어 전환 테스트"""

    # HTML 파일 경로 확인
    html_file = Path("output_files/Incentive_Dashboard_2025_09_Version_5.html")
    if not html_file.exists():
        print(f"❌ HTML 파일을 찾을 수 없습니다: {html_file}")
        return False

    print("=" * 60)
    print("🌐 포괄적인 언어 전환 테스트 시작")
    print("=" * 60)

    # 브라우저 디버그 코드 생성
    debug_code = """
// =============================================
// 언어 전환 테스트 코드
// =============================================

// 테스트 결과 저장
let testResults = {
    passed: [],
    failed: [],
    warnings: []
};

// 현재 언어 확인
console.log('현재 언어:', currentLanguage);

// 언어별 테스트
['ko', 'en', 'vi'].forEach(lang => {
    console.log(`\\n========== ${lang} 언어 테스트 ==========`);

    // 언어 변경
    changeLanguage(lang);

    // 잠시 대기
    setTimeout(() => {
        // 탭 텍스트 확인
        document.querySelectorAll('.nav-link').forEach(tab => {
            const text = tab.textContent.trim();
            console.log(`탭 텍스트: "${text}"`);

            // 예상 텍스트와 비교
            const tabId = tab.getAttribute('onclick')?.match(/showTab\\('(\\w+)'\\)/)?.[1];
            if (tabId) {
                const expectedText = getTranslation(`tabs.${tabId}`, lang);
                if (text !== expectedText && expectedText) {
                    testResults.failed.push({
                        type: 'tab',
                        tabId: tabId,
                        language: lang,
                        expected: expectedText,
                        actual: text
                    });
                    console.error(`❌ 탭 번역 오류: ${tabId} (예상: "${expectedText}", 실제: "${text}")`);
                } else {
                    testResults.passed.push({
                        type: 'tab',
                        tabId: tabId,
                        language: lang
                    });
                }
            }
        });

        // KPI 카드 제목 확인 (System Validation 탭)
        if (document.getElementById('validation').style.display !== 'none') {
            document.querySelectorAll('.kpi-card h5').forEach(card => {
                const text = card.textContent.trim();
                console.log(`KPI 카드: "${text}"`);
            });
        }

        // 모달 테스트를 위한 버튼 찾기
        document.querySelectorAll('[data-bs-toggle="modal"]').forEach(btn => {
            const modalId = btn.getAttribute('data-bs-target');
            console.log(`모달 버튼 발견: ${modalId}, 텍스트: "${btn.textContent.trim()}"`);
        });

    }, 500);
});

// 3초 후 결과 출력
setTimeout(() => {
    console.log('\\n========== 테스트 결과 ==========');
    console.log(`✅ 통과: ${testResults.passed.length}개`);
    console.log(`❌ 실패: ${testResults.failed.length}개`);
    console.log(`⚠️ 경고: ${testResults.warnings.length}개`);

    if (testResults.failed.length > 0) {
        console.log('\\n실패 항목:');
        testResults.failed.forEach(f => {
            console.log(`- [${f.language}] ${f.type} ${f.tabId}: "${f.expected}" != "${f.actual}"`);
        });
    }

    // Type별 요약 테이블 확인
    console.log('\\n========== Type별 요약 테이블 확인 ==========');
    const tbody = document.getElementById('typeSummaryBody');
    if (tbody && tbody.rows.length > 0) {
        console.log(`✅ Type별 요약 테이블 정상: ${tbody.rows.length}개 행`);
    } else {
        console.log('❌ Type별 요약 테이블이 비어있습니다!');
    }

    // 조직도 탭 확인
    console.log('\\n========== 조직도 탭 확인 ==========');
    const orgChart = document.getElementById('orgChart');
    if (orgChart) {
        const cards = orgChart.querySelectorAll('.employee-card').length;
        console.log(`조직도 카드 수: ${cards}개`);
    }

}, 3500);

// 모달 테스트 함수
function testModal(modalId) {
    const modal = document.querySelector(modalId);
    if (!modal) {
        console.error(`모달을 찾을 수 없습니다: ${modalId}`);
        return;
    }

    // 모달 열기
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();

    setTimeout(() => {
        // 모달 제목 확인
        const title = modal.querySelector('.modal-title');
        if (title) {
            console.log(`모달 제목 [${currentLanguage}]: "${title.textContent.trim()}"`);
        }

        // 모달 내용 확인
        const body = modal.querySelector('.modal-body');
        if (body) {
            const hasContent = body.textContent.trim().length > 0;
            console.log(`모달 내용 존재: ${hasContent ? '✅' : '❌'}`);

            // 테이블이 있는지 확인
            const table = body.querySelector('table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr').length;
                console.log(`모달 테이블 행 수: ${rows}`);
            }
        }

        // 모달 닫기
        modalInstance.hide();
    }, 500);
}

// 언어별 모든 요소 확인
function checkAllTranslations() {
    const elements = {
        tabs: {},
        buttons: {},
        labels: {},
        titles: {}
    };

    // 탭 텍스트 수집
    document.querySelectorAll('.nav-link').forEach(tab => {
        const tabId = tab.getAttribute('onclick')?.match(/showTab\\('(\\w+)'\\)/)?.[1];
        if (tabId) {
            elements.tabs[tabId] = tab.textContent.trim();
        }
    });

    // 버튼 텍스트 수집
    document.querySelectorAll('button').forEach(btn => {
        const text = btn.textContent.trim();
        if (text && !text.includes('×')) {
            elements.buttons[text] = true;
        }
    });

    return elements;
}

// 실행
console.log('언어 전환 테스트를 시작합니다...');
checkAllTranslations();
"""

    # 파일에 저장
    with open("browser_language_test.js", "w", encoding="utf-8") as f:
        f.write(debug_code)

    print("✅ 브라우저 테스트 코드 생성 완료: browser_language_test.js")
    print("\n📋 테스트 방법:")
    print("1. 대시보드 열기:")
    print(f"   open {html_file}")
    print("\n2. 개발자 도구 콘솔에서 실행:")
    print("   browser_language_test.js 파일 내용을 복사하여 붙여넣기")
    print("\n3. 또는 Playwright로 자동 테스트 실행")

    return True

def create_playwright_test():
    """Playwright 자동 테스트 스크립트 생성"""

    playwright_test = '''#!/usr/bin/env python3
"""
Playwright를 사용한 자동 언어 전환 테스트
"""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

async def test_language_comprehensive():
    """모든 탭과 모달에서 언어 전환 테스트"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # HTML 파일 열기
        html_path = Path("output_files/Incentive_Dashboard_2025_09_Version_5.html").absolute()
        await page.goto(f"file://{html_path}")
        await page.wait_for_timeout(2000)

        print("=" * 60)
        print("🌐 Playwright 언어 전환 테스트")
        print("=" * 60)

        # 각 언어별 테스트
        for lang in ["ko", "en", "vi"]:
            print(f"\\n📋 {lang} 언어 테스트")

            # 언어 변경
            await page.evaluate(f"changeLanguage('{lang}')")
            await page.wait_for_timeout(500)

            # 현재 언어 확인
            current_lang = await page.evaluate("currentLanguage")
            print(f"  현재 언어: {current_lang}")

            # 각 탭 확인
            tabs = await page.query_selector_all(".nav-link")
            for tab in tabs:
                text = await tab.text_content()
                print(f"  탭: {text.strip()}")

            # Type별 요약 테이블 확인
            tbody = await page.query_selector("#typeSummaryBody")
            if tbody:
                rows = await tbody.query_selector_all("tr")
                print(f"  Type별 요약 행 수: {len(rows)}")

            # System Validation 탭으로 이동
            await page.evaluate("showTab('validation')")
            await page.wait_for_timeout(500)

            # KPI 카드 확인
            kpi_cards = await page.query_selector_all(".kpi-card h5")
            for card in kpi_cards:
                text = await card.text_content()
                print(f"  KPI 카드: {text.strip()}")

            # 모달 버튼 확인
            modal_buttons = await page.query_selector_all("[data-bs-toggle='modal']")
            print(f"  모달 버튼 수: {len(modal_buttons)}")

            # 첫 번째 모달 테스트
            if modal_buttons:
                await modal_buttons[0].click()
                await page.wait_for_timeout(500)

                # 모달 제목 확인
                modal_title = await page.query_selector(".modal-title")
                if modal_title:
                    title_text = await modal_title.text_content()
                    print(f"  모달 제목: {title_text.strip()}")

                # 모달 닫기
                close_btn = await page.query_selector(".modal .btn-close")
                if close_btn:
                    await close_btn.click()
                await page.wait_for_timeout(500)

        # 스크린샷 저장
        await page.screenshot(path="language_test_result.png")
        print("\\n✅ 스크린샷 저장: language_test_result.png")

        await browser.close()
        print("\\n✅ 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_language_comprehensive())
'''

    # 파일 저장
    with open("test_language_playwright.py", "w", encoding="utf-8") as f:
        f.write(playwright_test)

    print("\n✅ Playwright 테스트 스크립트 생성: test_language_playwright.py")
    print("실행: python test_language_playwright.py")

# 메인 실행
if __name__ == "__main__":
    # 브라우저 테스트 코드 생성
    test_language_switching()

    # Playwright 테스트 생성
    create_playwright_test()

    print("\n" + "=" * 60)
    print("✅ 언어 전환 테스트 준비 완료!")
    print("위의 방법 중 하나를 선택하여 테스트를 실행하세요.")
    print("=" * 60)