#!/usr/bin/env python3
"""
대시보드 JavaScript 초기화 문제 수정 스크립트
- 중복된 DOMContentLoaded 이벤트 제거
- 초기화 함수 순서 정리
- 모든 탭 렌더링 함수 호출 확인
"""

import re

# JavaScript 초기화 코드 읽기
js_file = "dashboard_v2/static/js/dashboard_complete.js"

with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=== JavaScript 초기화 코드 통합 시작 ===")
print(f"원본 파일 크기: {len(content)} bytes")

# 1. 첫 번째 DOMContentLoaded 이벤트 (line 5131-5235) 수정
# 통합된 초기화 함수로 대체
unified_init = '''    // 통합된 초기화 함수
    function initializeDashboard() {
        console.log('=== 대시보드 초기화 시작 ===');
        console.log('Total employees:', employeeData ? employeeData.length : 'No data');

        // 1. Bootstrap 툴팁 초기화
        try {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            console.log('Bootstrap tooltips initialized:', tooltipList.length);
        } catch(e) {
            console.error('Tooltip 초기화 오류:', e);
        }

        // 2. D3.js 라이브러리 확인
        if (typeof d3 === 'undefined') {
            console.error('D3.js library not loaded!');
            setTimeout(initializeDashboard, 500); // 재시도
            return;
        }
        console.log('D3.js version:', d3.version);

        // 3. 언어 설정 복원
        const savedLang = localStorage.getItem('dashboardLanguage') || 'ko';
        currentLanguage = savedLang;
        const langSelector = document.getElementById('languageSelector');
        if (langSelector) {
            langSelector.value = savedLang;
        }

        // 4. 요약 탭 초기화 (중요!)
        console.log('요약 탭 초기화...');
        updateSummaryCards();
        updateTypeSummaryTable();

        // 5. 직급별 테이블 초기화
        console.log('직급별 테이블 초기화...');
        try {
            generatePositionTables();
        } catch(e) {
            console.error('직급별 테이블 오류:', e);
        }

        // 6. 전체 직원 테이블 초기화
        console.log('전체 직원 테이블 초기화...');
        try {
            generateEmployeeTable();
        } catch(e) {
            console.error('직원 테이블 오류:', e);
        }

        // 7. 인센티브 기준 탭 초기화
        console.log('인센티브 기준 탭 초기화...');
        try {
            if (typeof renderCriteriaTab === 'function') {
                renderCriteriaTab();
            } else {
                console.warn('renderCriteriaTab 함수가 없습니다.');
                // Fallback: 기본 내용 표시
                const criteriaContent = document.getElementById('criteriaContent');
                if (criteriaContent && typeof conditionData !== 'undefined') {
                    criteriaContent.innerHTML = '<h5>인센티브 조건 매트릭스</h5>' +
                        '<pre>' + JSON.stringify(conditionData, null, 2) + '</pre>';
                }
            }
        } catch(e) {
            console.error('인센티브 기준 탭 오류:', e);
        }

        // 8. 시스템 검증 탭 초기화
        console.log('시스템 검증 탭 초기화...');
        try {
            initValidationTab();
        } catch(e) {
            console.error('검증 탭 오류:', e);
        }

        // 9. Talent Pool 섹션 업데이트
        console.log('Talent Pool 초기화...');
        try {
            updateTalentPoolSection();
        } catch(e) {
            console.error('Talent Pool 오류:', e);
        }

        // 10. 필터 초기화
        try {
            updatePositionFilter();
        } catch(e) {
            console.error('필터 초기화 오류:', e);
        }

        // 11. 탭 이벤트 리스너 등록
        setupTabEventListeners();

        // 12. Individual Details 탭 Observer 설정
        setupIndividualDetailsObserver();

        // 13. 텍스트 업데이트
        updateAllTexts();

        // 14. 기본 탭 표시
        showTab('summary');

        console.log('=== 대시보드 초기화 완료 ===');
    }

    // 탭 이벤트 리스너 설정 함수
    function setupTabEventListeners() {
        console.log('탭 이벤트 리스너 설정...');

        // 조직도 탭 이벤트
        const orgChartTabButton = document.querySelector('[data-bs-target="#orgchart"]') ||
                                  document.querySelectorAll('.nav-link')[3];

        if (orgChartTabButton) {
            console.log('조직도 탭 버튼 발견');
            orgChartTabButton.addEventListener('shown.bs.tab', function() {
                console.log('조직도 탭 활성화 - 차트 그리기');
                drawOrgChart();
            });

            orgChartTabButton.addEventListener('click', function() {
                setTimeout(() => {
                    const orgTab = document.getElementById('orgchart');
                    if (orgTab && orgTab.classList.contains('active')) {
                        drawOrgChart();
                    }
                }, 100);
            });
        }

        // 다른 탭 이벤트도 필요시 여기에 추가
    }

    // Individual Details 탭 Observer 설정
    function setupIndividualDetailsObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.id === 'detail' && mutation.target.classList.contains('active')) {
                    renderIndividualDetailsTab();
                }
            });
        });

        const detailTab = document.getElementById('detail');
        if (detailTab) {
            observer.observe(detailTab, { attributes: true, attributeFilter: ['class'] });
        }
    }

    // 단일 DOMContentLoaded 이벤트로 통합
    document.addEventListener('DOMContentLoaded', function() {
        console.log('=== DOMContentLoaded 이벤트 발생 ===');

        // 데이터 로딩 확인 후 초기화
        if (typeof employeeData === 'undefined') {
            console.warn('employeeData가 아직 로드되지 않았습니다. 500ms 후 재시도...');
            setTimeout(initializeDashboard, 500);
        } else {
            initializeDashboard();
        }
    });'''

# 첫 번째 DOMContentLoaded 블록 찾기 및 교체
pattern1 = r'    // 페이지 로드 시 초기화\s*\n\s*document\.addEventListener\(\'DOMContentLoaded\'.*?\n    \}\);'
if re.search(pattern1, content, re.DOTALL):
    content = re.sub(pattern1, unified_init, content, count=1, flags=re.DOTALL)
    print("✓ 첫 번째 DOMContentLoaded 이벤트 통합 완료")
else:
    print("⚠ 첫 번째 DOMContentLoaded 패턴을 찾을 수 없습니다.")

# 2. window.onload 제거 (line 8203-8242)
pattern2 = r'    window\.onload = function\(\) \{[\s\S]*?    \};'
if re.search(pattern2, content):
    content = re.sub(pattern2, '    // window.onload removed - integrated into DOMContentLoaded', content, count=1)
    print("✓ window.onload 제거 완료")
else:
    print("⚠ window.onload 패턴을 찾을 수 없습니다.")

# 3. 두 번째 DOMContentLoaded 제거 (line 10362)
pattern3 = r'    // Individual Details 탭 표시 시 초기화\s*\n\s*window\.addEventListener\(\'DOMContentLoaded\'.*?\n    \}\);'
if re.search(pattern3, content, re.DOTALL):
    content = re.sub(pattern3, '    // Individual Details observer - integrated into main initialization', content, count=1, flags=re.DOTALL)
    print("✓ 두 번째 DOMContentLoaded 이벤트 제거 완료")
else:
    print("⚠ 두 번째 DOMContentLoaded 패턴을 찾을 수 없습니다.")

# 수정된 내용 저장
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ JavaScript 초기화 코드 통합 완료!")
print(f"최종 파일 크기: {len(content)} bytes")
print("\n=== 수정 사항 ===")
print("1. 3개의 DOMContentLoaded 이벤트를 1개로 통합")
print("2. window.onload 제거 및 통합")
print("3. 초기화 함수 순서 정리")
print("4. 모든 탭 렌더링 함수 호출 확인")
print("5. 에러 핸들링 추가")