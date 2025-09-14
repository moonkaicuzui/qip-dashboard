import { state } from './state.js';
import { translations } from './config.js';
import { parseDate } from './ui/helpers/uiUtils.js';

// 🔥 탭별 모듈 import - 올바른 경로: ui/tab/
import { updateOverviewCharts } from './ui/tab/overviewTab.js';
import { updateTQCAnalysis, updateTrainingChart } from './ui/tab/tqcTab.js';
import { updateDefectAnalysis } from './ui/tab/defectsTab.js';
import { updateRiskAnalysis } from './ui/tab/riskTab.js';
import { updateActionItems } from './ui/tab/actionsTab.js';
import { updateSustainabilityAnalysis } from './ui/tab/sustainabilityTab.js';
import { updateManagementInsights } from './ui/tab/managementTab.js';

// 헬퍼 모듈 export (main.js에서 사용)
export { openModal, closeModal, showTQCDetail, showTqcHeatmapDetail, showHeatmapDetail, showRiskDetail } from './ui/helpers/modalHelpers.js';

// 탭별 개별 함수 export (필터 이벤트에서 사용)
export { updateTrainingChart } from './ui/tab/tqcTab.js';
export { updateDefectDetailTable } from './ui/tab/defectsTab.js';

/**
 * 대시보드 초기화 함수
 */
export function initializeDashboard() {
    console.log('🔄 대시보드 초기화 시작');
    
    try {
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('dashboardSection').style.display = 'block';
        
        changeLanguageUI();
        updateDashboard();
        
        console.log('✅ 대시보드 초기화 완료');
    } catch (error) {
        console.error('❌ 대시보드 초기화 오류:', error);
    }
}

/**
 * 언어 변경 UI 업데이트 함수
 */
export function changeLanguageUI() {
    try {
        const lang = state.currentLanguage;
        
        document.querySelectorAll('[data-lang]').forEach(elem => {
            const key = elem.getAttribute('data-lang');
            if (translations[lang]?.[key]) {
                elem.textContent = translations[lang][key];
            }
        });
        
        const titleElement = document.getElementById('dashboardTitle');
        if (titleElement && translations[lang]?.dashboardTitle) {
            titleElement.textContent = translations[lang].dashboardTitle;
        }
        
        console.log(`✅ 언어 UI 업데이트 완료: ${lang}`);
    } catch (error) {
        console.error('❌ 언어 UI 업데이트 오류:', error);
    }
}

/**
 * 전체 대시보드 업데이트 함수
 */
export function updateDashboard() {
    console.log('🔄 전체 대시보드 업데이트 시작');
    
    try {
        if (!state.processedData || !state.processedData.tqcData) {
            console.warn('⚠️ 처리된 데이터가 없어서 대시보드를 업데이트할 수 없습니다.');
            return;
        }
        
        updateSummaryStats();
        updateFilterOptions();
        updateAllChartsAndTables();
        
        console.log('✅ 전체 대시보드 업데이트 완료');
    } catch (error) {
        console.error('❌ 전체 대시보드 업데이트 오류:', error);
    }
}

/**
 * 요약 통계 업데이트 함수
 */
function updateSummaryStats() {
    try {
        const { totalValidation, totalRejectRate, tqcData, avgDailyValidation } = state.processedData;
        const lang = state.currentLanguage;
        
        // 🔥 안전한 요소 업데이트
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            } else {
                console.warn(`⚠️ 요소를 찾을 수 없습니다: ${id}`);
            }
        };
        
        updateElement('totalValidation', totalValidation.toLocaleString());
        updateElement('totalRejectRate', `${totalRejectRate.toFixed(2)}%`);
        
        // 고위험 TQC 계산
        const highRiskTQCs = Object.values(tqcData).filter(t => 
            t.totalValidation > 100 && (t.totalReject / t.totalValidation * 100) > 5
        ).length;
        updateElement('highRiskTQC', `${highRiskTQCs}${translations[lang].name || '명'}`);
        
        // 활성 어딧터 계산
        const now = new Date();
        let cutoffDate = new Date(0);
        
        if (state.currentPeriod === 'week') {
            cutoffDate = new Date();
            cutoffDate.setDate(now.getDate() - 7);
        } else if (state.currentPeriod === 'month') {
            cutoffDate = new Date();
            cutoffDate.setMonth(now.getMonth() - 1);
        }
        
        const activeInspectors = new Set();
        if (state.rawData) {
            state.rawData.forEach(row => {
                const date = parseDate(row['Inspection Date']);
                const validationQty = parseInt(row['Validation Qty']) || 0;
                
                if (row['Inspector ID'] && date && date >= cutoffDate && validationQty > 0) {
                    activeInspectors.add(row['Inspector ID']);
                }
            });
        }
        updateElement('activeInspectors', `${activeInspectors.size}${translations[lang].name || '명'}`);
        updateElement('avgValidationQty', Math.round(avgDailyValidation).toLocaleString());
        
        console.log('✅ 요약 통계 업데이트 완료');
    } catch (error) {
        console.error('❌ 요약 통계 업데이트 오류:', error);
    }
}

/**
 * 필터 옵션 업데이트 함수
 */
function updateFilterOptions() {
    try {
        const { buildings, models, defectTypes } = state.processedData;
        const lang = state.currentLanguage;
        const allOption = `<option value="ALL">${translations[lang]?.all || '전체'}</option>`;

        const updateSelect = (selectId, options) => {
            const select = document.getElementById(selectId);
            if (!select) {
                console.warn(`⚠️ 선택 요소를 찾을 수 없습니다: ${selectId}`);
                return;
            }
            
            const currentValue = select.value;
            select.innerHTML = allOption + options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
            select.value = currentValue && options.includes(currentValue) ? currentValue : "ALL";
        };

        // 기본 필터 업데이트
        updateSelect('overviewBuildingFilter', buildings);
        updateSelect('tqcBuildingFilter', buildings);
        updateSelect('defectsBuildingFilter', buildings);
        updateSelect('modelFilter', models);
        
        // 지속성 탭 필터
        const sustainabilityFilter = document.getElementById('sustainabilityTqcBuildingFilter');
        if (sustainabilityFilter) {
            updateSelect('sustainabilityTqcBuildingFilter', buildings);
        }
        
        // 상위 불량 유형 계산
        const topDefects = Object.keys(defectTypes).sort((a, b) => defectTypes[b] - defectTypes[a]).slice(0, 10);
        
        // 불량 유형 상세 필터
        const defectDetailSelect = document.getElementById('defectTypeDetailFilter');
        if (defectDetailSelect) {
            const currentValue = defectDetailSelect.value;
            defectDetailSelect.innerHTML = allOption;
            topDefects.forEach((opt, index) => {
                defectDetailSelect.innerHTML += `<option value="${opt}">Top ${index + 1}: ${opt}</option>`;
            });
            defectDetailSelect.value = currentValue && topDefects.includes(currentValue) ? currentValue : "ALL";
        }

        updateSelect('modelDefectTypeFilter', topDefects);
        
        // 교육 우선순위 필터
        const trainingSelect = document.getElementById('trainingDefectFilter');
        if (trainingSelect) {
            trainingSelect.innerHTML = topDefects.map((defect, index) => 
                `<option value="${index}">Top ${index + 1}: ${defect}</option>`
            ).join('');
        }
        
        console.log('✅ 필터 옵션 업데이트 완료');
    } catch (error) {
        console.error('❌ 필터 옵션 업데이트 오류:', error);
    }
}

/**
 * 모든 차트와 테이블 업데이트 함수
 */
export function updateAllChartsAndTables() {
    try {
        const activeTab = document.querySelector('.tab-button.active')?.dataset.tab;
        if (!activeTab) {
            console.warn('⚠️ 활성 탭을 찾을 수 없습니다.');
            return;
        }
        
        console.log(`📊 ${activeTab} 탭 차트/테이블 업데이트 시작`);
        
        switch (activeTab) {
            case 'overview': 
                updateOverviewCharts(); 
                break;
            case 'tqc': 
                updateTQCAnalysis(); 
                break;
            case 'defects': 
                updateDefectAnalysis(); 
                break;
            case 'risk': 
                updateRiskAnalysis(); 
                break;
            case 'actions': 
                updateActionItems(); 
                break;
            case 'sustainability': 
                updateSustainabilityAnalysis(); 
                break;
            case 'management':
                updateManagementInsights();
                break;
            default:
                console.warn(`⚠️ 알 수 없는 탭: ${activeTab}`);
        }
        
        console.log(`✅ ${activeTab} 탭 차트/테이블 업데이트 완료`);
    } catch (error) {
        console.error('❌ 차트/테이블 업데이트 오류:', error);
    }
}

/**
 * PDF 내보내기 함수 (구현 예정)
 */
export function exportToPDF() {
    try {
        console.log('📄 PDF 내보내기 시작');
        
        // PDF 내보내기 로직은 향후 구현
        // jsPDF와 html2canvas를 사용하여 구현 예정
        
        console.warn('⚠️ PDF 내보내기 기능은 아직 구현되지 않았습니다.');
        alert('PDF 내보내기 기능은 곧 제공될 예정입니다.');
        
    } catch (error) {
        console.error('❌ PDF 내보내기 오류:', error);
    }
}