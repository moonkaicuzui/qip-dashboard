
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
    console.log(`\n========== ${lang} 언어 테스트 ==========`);

    // 언어 변경
    changeLanguage(lang);

    // 잠시 대기
    setTimeout(() => {
        // 탭 텍스트 확인
        document.querySelectorAll('.nav-link').forEach(tab => {
            const text = tab.textContent.trim();
            console.log(`탭 텍스트: "${text}"`);

            // 예상 텍스트와 비교
            const tabId = tab.getAttribute('onclick')?.match(/showTab\('(\w+)'\)/)?.[1];
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
    console.log('\n========== 테스트 결과 ==========');
    console.log(`✅ 통과: ${testResults.passed.length}개`);
    console.log(`❌ 실패: ${testResults.failed.length}개`);
    console.log(`⚠️ 경고: ${testResults.warnings.length}개`);

    if (testResults.failed.length > 0) {
        console.log('\n실패 항목:');
        testResults.failed.forEach(f => {
            console.log(`- [${f.language}] ${f.type} ${f.tabId}: "${f.expected}" != "${f.actual}"`);
        });
    }

    // Type별 요약 테이블 확인
    console.log('\n========== Type별 요약 테이블 확인 ==========');
    const tbody = document.getElementById('typeSummaryBody');
    if (tbody && tbody.rows.length > 0) {
        console.log(`✅ Type별 요약 테이블 정상: ${tbody.rows.length}개 행`);
    } else {
        console.log('❌ Type별 요약 테이블이 비어있습니다!');
    }

    // 조직도 탭 확인
    console.log('\n========== 조직도 탭 확인 ==========');
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
        const tabId = tab.getAttribute('onclick')?.match(/showTab\('(\w+)'\)/)?.[1];
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
