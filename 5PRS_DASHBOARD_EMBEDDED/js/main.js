import { state } from './state.js';
import { processData } from './dataProcessor.js';
import * as fileHandler from './fileHandler.js';
import * as ui from './uiController.js';

/**
 * 애플리케이션 초기화 및 모든 이벤트 리스너 설정
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 5PRS Dashboard 초기화 시작');
    
    try {
        // ----------------------------------------------------
        // 초기 언어 설정
        // ----------------------------------------------------
        initializeLanguage();
        
        // ----------------------------------------------------
        // 🔥 자동으로 서버에서 데이터 로드
        // ----------------------------------------------------
        console.log('📡 서버에서 데이터를 자동으로 로드합니다...');
        await fileHandler.loadDataFromServer();
        
        // ----------------------------------------------------
        // 파일 업로드 관련 이벤트 (옵션으로 유지)
        // ----------------------------------------------------
        // initializeFileUpload();  // 필요시 주석 해제
        
        // ----------------------------------------------------
        // 새로고침 버튼 이벤트 추가
        // ----------------------------------------------------
        initializeRefreshButton();
        
        // ----------------------------------------------------
        // 언어 변경 이벤트
        // ----------------------------------------------------
        initializeLanguageSelector();

        // ----------------------------------------------------
        // 기간 변경 이벤트
        // ----------------------------------------------------
        initializePeriodSelector();
        
        // ----------------------------------------------------
        // 탭 전환 이벤트
        // ----------------------------------------------------
        initializeTabSelector();

        // ----------------------------------------------------
        // 필터 변경 이벤트
        // ----------------------------------------------------
        initializeFilters();
        
        // ----------------------------------------------------
        // PDF 다운로드 이벤트
        // ----------------------------------------------------
        initializePdfExport();

        // ----------------------------------------------------
        // 모달 관련 이벤트
        // ----------------------------------------------------
        initializeModal();

        // ----------------------------------------------------
        // 동적 컨텐츠 클릭 이벤트 (이벤트 위임 방식)
        // ----------------------------------------------------
        initializeDynamicContentEvents();
        
        // ----------------------------------------------------
        // 글로벌 에러 핸들러 설정
        // ----------------------------------------------------
        initializeErrorHandlers();
        
        // ----------------------------------------------------
        // 디버깅 도구 설정
        // ----------------------------------------------------
        setupDebuggingTools();
        
        console.log('✅ 5PRS Dashboard 초기화 완료');
        
    } catch (error) {
        console.error('❌ 애플리케이션 초기화 중 오류 발생:', error);
        showErrorMessage('애플리케이션 초기화 중 오류가 발생했습니다.');
    }
});

/**
 * 초기 언어 설정
 */
function initializeLanguage() {
    try {
        ui.changeLanguageUI();
        console.log('✅ 초기 언어 설정 완료');
    } catch (error) {
        console.error('❌ 초기 언어 설정 오류:', error);
    }
}

/**
 * 파일 업로드 관련 이벤트 리스너 초기화
 */
function initializeFileUpload() {
    try {
        const uploadBtn = document.getElementById('uploadBtn');
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.querySelector('.upload-area');

        if (!uploadBtn || !fileInput || !uploadArea) {
            console.warn('⚠️ 파일 업로드 관련 요소를 찾을 수 없습니다.');
            return;
        }

        // 업로드 버튼 클릭 시 파일 선택 다이얼로그 열기
        uploadBtn.addEventListener('click', () => {
            console.log('📁 파일 선택 다이얼로그 열기');
            fileInput.click();
        });

        // 파일 선택 시
        fileInput.addEventListener('change', (e) => {
            console.log('📄 파일 선택됨:', e.target.files[0]?.name);
            fileHandler.handleFileSelect(e);
        });

        // 업로드 영역 클릭 시
        uploadArea.addEventListener('click', () => {
            console.log('📁 업로드 영역 클릭');
            fileInput.click();
        });

        // 드래그 오버 시
        uploadArea.addEventListener('dragover', (e) => {
            fileHandler.handleDragOver(e);
        });

        // 드래그 떠날 시
        uploadArea.addEventListener('dragleave', (e) => {
            fileHandler.handleDragLeave(e);
        });

        // 드롭 시
        uploadArea.addEventListener('drop', (e) => {
            console.log('📂 파일 드롭됨');
            fileHandler.handleDrop(e);
        });

        console.log('✅ 파일 업로드 이벤트 리스너 초기화 완료');
        
    } catch (error) {
        console.error('❌ 파일 업로드 이벤트 초기화 오류:', error);
    }
}

/**
 * 새로고침 버튼 이벤트 리스너 초기화
 */
function initializeRefreshButton() {
    try {
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (uploadBtn) {
            // 기존 업로드 버튼을 새로고침 버튼으로 변경
            const refreshIcon = uploadBtn.querySelector('svg');
            if (refreshIcon) {
                refreshIcon.innerHTML = `
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                `;
            }
            
            const buttonText = uploadBtn.querySelector('span[data-lang="fileUpload"]');
            if (buttonText) {
                buttonText.setAttribute('data-lang', 'refreshData');
                buttonText.textContent = '데이터 새로고침';
            }
            
            // 클릭 이벤트 재정의
            uploadBtn.replaceWith(uploadBtn.cloneNode(true));
            const newRefreshBtn = document.getElementById('uploadBtn');
            
            newRefreshBtn.addEventListener('click', async () => {
                console.log('🔄 데이터 새로고침 버튼 클릭');
                await fileHandler.refreshData();
            });
            
            console.log('✅ 새로고침 버튼 초기화 완료');
        }
    } catch (error) {
        console.error('❌ 새로고침 버튼 초기화 오류:', error);
    }
}

/**
 * 언어 변경 이벤트 리스너 초기화
 */
function initializeLanguageSelector() {
    try {
        const langButtons = document.querySelectorAll('.lang-btn');
        
        if (langButtons.length === 0) {
            console.warn('⚠️ 언어 선택 버튼을 찾을 수 없습니다.');
            return;
        }

        langButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                try {
                    const previousLang = state.currentLanguage;
                    const newLang = e.currentTarget.dataset.langCode;
                    
                    console.log(`🌐 언어 변경: ${previousLang} → ${newLang}`);
                    
                    // 활성 언어 버튼 변경
                    document.querySelector('.lang-btn.active')?.classList.remove('active');
                    e.currentTarget.classList.add('active');
                    
                    // 상태 업데이트
                    state.currentLanguage = newLang;
                    
                    // UI 언어 변경
                    ui.changeLanguageUI();
                    
                    // 데이터가 있으면 대시보드 업데이트
                    if (state.rawData && state.rawData.length > 0) {
                        console.log('📊 언어 변경으로 인한 대시보드 업데이트');
                        ui.updateDashboard();
                    }
                    
                } catch (error) {
                    console.error('❌ 언어 변경 처리 오류:', error);
                }
            });
        });

        console.log('✅ 언어 선택 이벤트 리스너 초기화 완료');
        
    } catch (error) {
        console.error('❌ 언어 선택 이벤트 초기화 오류:', error);
    }
}

/**
 * 기간 변경 이벤트 리스너 초기화
 */
function initializePeriodSelector() {
    try {
        const periodButtons = document.querySelectorAll('.period-btn');
        
        if (periodButtons.length === 0) {
            console.warn('⚠️ 기간 선택 버튼을 찾을 수 없습니다.');
            return;
        }

        periodButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                try {
                    const previousPeriod = state.currentPeriod;
                    const newPeriod = e.currentTarget.dataset.period;
                    
                    console.log(`📅 기간 변경: ${previousPeriod} → ${newPeriod}`);
                    
                    // 활성 기간 버튼 변경
                    document.querySelector('.period-btn.active')?.classList.remove('active');
                    e.currentTarget.classList.add('active');
                    
                    // 상태 업데이트
                    state.currentPeriod = newPeriod;
                    
                    // 데이터가 있으면 재처리 및 대시보드 업데이트
                    if (state.rawData && state.rawData.length > 0) {
                        console.log('🔄 기간 변경으로 인한 데이터 재처리 및 대시보드 업데이트');
                        processData();
                        ui.updateDashboard();
                    }
                    
                } catch (error) {
                    console.error('❌ 기간 변경 처리 오류:', error);
                }
            });
        });

        console.log('✅ 기간 선택 이벤트 리스너 초기화 완료');
        
    } catch (error) {
        console.error('❌ 기간 선택 이벤트 초기화 오류:', error);
    }
}

/**
 * 탭 전환 이벤트 리스너 초기화
 */
function initializeTabSelector() {
    try {
        const tabButtons = document.querySelectorAll('.tab-button');
        
        if (tabButtons.length === 0) {
            console.warn('⚠️ 탭 버튼을 찾을 수 없습니다.');
            return;
        }

        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                try {
                    const previousTab = document.querySelector('.tab-button.active')?.dataset.tab;
                    const newTab = e.currentTarget.dataset.tab;
                    
                    console.log(`📋 탭 변경: ${previousTab} → ${newTab}`);
                    
                    // 활성 탭 버튼 및 패널 변경
                    document.querySelector('.tab-button.active')?.classList.remove('active');
                    document.querySelector('.tab-panel.active')?.classList.remove('active');
                    
                    e.currentTarget.classList.add('active');
                    
                    const tabPanel = document.getElementById(`${newTab}-panel`);
                    if (tabPanel) {
                        tabPanel.classList.add('active');
                        console.log(`✅ 탭 패널 활성화: ${newTab}-panel`);
                    } else {
                        console.warn(`⚠️ 탭 패널을 찾을 수 없습니다: ${newTab}-panel`);
                    }
                    
                    // 탭 변경 시 해당 탭의 차트와 테이블 업데이트
                    if (state.rawData && state.rawData.length > 0) {
                        console.log(`📊 탭 변경으로 인한 ${newTab} 탭 업데이트`);
                        ui.updateAllChartsAndTables();
                    }
                    
                } catch (error) {
                    console.error('❌ 탭 변경 처리 오류:', error);
                }
            });
        });

        console.log('✅ 탭 선택 이벤트 리스너 초기화 완료');
        
    } catch (error) {
        console.error('❌ 탭 선택 이벤트 초기화 오류:', error);
    }
}

/**
 * 필터 변경 이벤트 리스너 초기화
 */
function initializeFilters() {
    try {
        // 🔥 탭별로 자체 처리하는 필터들 목록 (이들은 각 탭에서 별도 처리)
        const tabSpecificFilters = [
            'trainingDefectFilter',           // TQC 탭에서 처리
            'defectTypeDetailFilter',         // 불량 분석 탭에서 처리
            'modelFilter',                    // 불량 분석 탭에서 처리
            'modelDefectTypeFilter',          // 불량 분석 탭에서 처리
            'defectsBuildingFilter',          // 불량 분석 탭에서 처리
            'overviewBuildingFilter',         // 전체 현황 탭에서 처리
            'sustainabilityTqcBuildingFilter' // 지속성 탭에서 처리
        ];
        
        // 🔥 공통 필터들 (탭 관계없이 전체 대시보드에 영향)
        const commonFilters = document.querySelectorAll('.filter-select');
        let commonFilterCount = 0;
        
        commonFilters.forEach(select => {
            if (!tabSpecificFilters.includes(select.id)) {
                select.addEventListener('change', (e) => {
                    try {
                        console.log(`🔍 공통 필터 변경: ${select.id} = ${e.target.value}`);
                        
                        if (state.rawData && state.rawData.length > 0) {
                            ui.updateAllChartsAndTables();
                        }
                        
                    } catch (error) {
                        console.error(`❌ 공통 필터 변경 처리 오류 (${select.id}):`, error);
                    }
                });
                commonFilterCount++;
            }
        });
        
        console.log(`✅ 필터 이벤트 리스너 초기화 완료 (공통 필터: ${commonFilterCount}개)`);
        
    } catch (error) {
        console.error('❌ 필터 이벤트 초기화 오류:', error);
    }
}

/**
 * PDF 다운로드 이벤트 리스너 초기화
 */
function initializePdfExport() {
    try {
        const exportPdfBtn = document.getElementById('exportPdfBtn');
        
        if (!exportPdfBtn) {
            console.warn('⚠️ PDF 다운로드 버튼을 찾을 수 없습니다.');
            return;
        }

        exportPdfBtn.addEventListener('click', () => {
            try {
                console.log('📄 PDF 다운로드 시도');
                
                // PDF 다운로드 기능이 구현되면 여기에 추가
                if (typeof ui.exportToPDF === 'function') {
                    ui.exportToPDF();
                } else {
                    console.warn('⚠️ PDF 다운로드 기능이 아직 구현되지 않았습니다.');
                    showInfoMessage('PDF 다운로드 기능은 곧 제공될 예정입니다.');
                }
                
            } catch (error) {
                console.error('❌ PDF 다운로드 오류:', error);
                showErrorMessage('PDF 다운로드 중 오류가 발생했습니다.');
            }
        });

        console.log('✅ PDF 다운로드 이벤트 리스너 초기화 완료');
        
    } catch (error) {
        console.error('❌ PDF 다운로드 이벤트 초기화 오류:', error);
    }
}

/**
 * 모달 관련 이벤트 리스너 초기화
 */
function initializeModal() {
    try {
        const modalCloseBtn = document.getElementById('modalCloseBtn');
        const detailModal = document.getElementById('detailModal');
        
        if (!modalCloseBtn || !detailModal) {
            console.warn('⚠️ 모달 관련 요소를 찾을 수 없습니다.');
            return;
        }

        // 모달 닫기 버튼 클릭 시
        modalCloseBtn.addEventListener('click', () => {
            console.log('❌ 모달 닫기 버튼 클릭');
            ui.closeModal();
        });

        // 모달 배경 클릭 시 (모달 외부 클릭)
        detailModal.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                console.log('❌ 모달 외부 클릭으로 모달 닫기');
                ui.closeModal();
            }
        });

        // ESC 키로 모달 닫기
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && detailModal.classList.contains('show')) {
                console.log('❌ ESC 키로 모달 닫기');
                ui.closeModal();
            }
        });

        console.log('✅ 모달 이벤트 리스너 초기화 완료');
        
    } catch (error) {
        console.error('❌ 모달 이벤트 초기화 오류:', error);
    }
}

/**
 * 동적 컨텐츠 클릭 이벤트 리스너 초기화 (이벤트 위임 방식)
 */
function initializeDynamicContentEvents() {
    try {
        // TQC 테이블 행 클릭 이벤트
        initializeTqcTableEvents();
        
        // 불량 분석 탭 히트맵 클릭 이벤트
        initializeDefectsHeatmapEvents();
        
        // TQC 분석 탭 히트맵 클릭 이벤트
        initializeTqcHeatmapEvents();
        
        // 위험도 분석 탭 클릭 이벤트
        initializeRiskAnalysisEvents();
        
        // 업무 지시 탭 클릭 이벤트
        initializeActionsEvents();
        
        console.log('✅ 동적 컨텐츠 이벤트 리스너 초기화 완료');
        
    } catch (error) {
        console.error('❌ 동적 컨텐츠 이벤트 초기화 오류:', error);
    }
}

/**
 * TQC 테이블 클릭 이벤트 초기화
 */
function initializeTqcTableEvents() {
    try {
        const tqcTableBody = document.getElementById('tqcTableBody');
        
        if (!tqcTableBody) {
            console.warn('⚠️ TQC 테이블 body를 찾을 수 없습니다.');
            return;
        }

        tqcTableBody.addEventListener('click', (e) => {
            try {
                const row = e.target.closest('.tqc-row');
                if (row && row.dataset.tqcKey) {
                    console.log(`👤 TQC 행 클릭: ${row.dataset.tqcKey}`);
                    ui.showTQCDetail(row.dataset.tqcKey);
                }
            } catch (error) {
                console.error('❌ TQC 행 클릭 처리 오류:', error);
            }
        });

        console.log('✅ TQC 테이블 이벤트 초기화 완료');
        
    } catch (error) {
        console.error('❌ TQC 테이블 이벤트 초기화 오류:', error);
    }
}

/**
 * 불량 분석 탭 히트맵 클릭 이벤트 초기화
 */
function initializeDefectsHeatmapEvents() {
    try {
        const defectsPanel = document.getElementById('defects-panel');
        
        if (!defectsPanel) {
            console.warn('⚠️ 불량 분석 패널을 찾을 수 없습니다.');
            return;
        }

        defectsPanel.addEventListener('click', (e) => {
            try {
                const cell = e.target.closest('.heatmap-cell');
                if (cell && cell.dataset.type) {
                    console.log(`🔥 불량 분석 히트맵 셀 클릭: ${cell.dataset.type} - ${cell.dataset.item} - ${cell.dataset.defect}`);
                    ui.showHeatmapDetail(cell.dataset.type, cell.dataset.item, cell.dataset.defect);
                }
            } catch (error) {
                console.error('❌ 불량 분석 히트맵 클릭 처리 오류:', error);
            }
        });

        console.log('✅ 불량 분석 히트맵 이벤트 초기화 완료');
        
    } catch (error) {
        console.error('❌ 불량 분석 히트맵 이벤트 초기화 오류:', error);
    }
}

/**
 * TQC 분석 탭 히트맵 클릭 이벤트 초기화
 */
function initializeTqcHeatmapEvents() {
    try {
        const tqcPanel = document.getElementById('tqc-panel');
        
        if (!tqcPanel) {
            console.warn('⚠️ TQC 분석 패널을 찾을 수 없습니다.');
            return;
        }

        tqcPanel.addEventListener('click', (e) => {
            try {
                const cell = e.target.closest('.heatmap-cell');
                if (cell && cell.dataset.type === 'tqc-defect') {
                    console.log(`🔥 TQC 히트맵 셀 클릭: ${cell.dataset.tqcKey} - ${cell.dataset.defect}`);
                    ui.showTqcHeatmapDetail(cell.dataset.tqcKey, cell.dataset.defect);
                }
            } catch (error) {
                console.error('❌ TQC 히트맵 클릭 처리 오류:', error);
            }
        });

        console.log('✅ TQC 히트맵 이벤트 초기화 완료');
        
    } catch (error) {
        console.error('❌ TQC 히트맵 이벤트 초기화 오류:', error);
    }
}

/**
 * 위험도 분석 탭 클릭 이벤트 초기화
 */
function initializeRiskAnalysisEvents() {
    try {
        const riskPanel = document.getElementById('risk-panel');
        
        if (!riskPanel) {
            console.warn('⚠️ 위험도 분석 패널을 찾을 수 없습니다.');
            return;
        }

        riskPanel.addEventListener('click', e => {
            try {
                const item = e.target.closest('.risk-item');
                if (item && item.dataset.type && item.dataset.name) {
                    console.log(`⚠️ 위험 아이템 클릭: ${item.dataset.type} - ${item.dataset.name}`);
                    ui.showRiskDetail(item.dataset.type, item.dataset.name);
                }
            } catch (error) {
                console.error('❌ 위험도 분석 클릭 처리 오류:', error);
            }
        });

        console.log('✅ 위험도 분석 이벤트 초기화 완료');
        
    } catch (error) {
        console.error('❌ 위험도 분석 이벤트 초기화 오류:', error);
    }
}

/**
 * 업무 지시 탭 클릭 이벤트 초기화
 */
function initializeActionsEvents() {
    try {
        const actionsPanel = document.getElementById('actions-panel');
        
        if (!actionsPanel) {
            console.warn('⚠️ 업무 지시 패널을 찾을 수 없습니다.');
            return;
        }

        actionsPanel.addEventListener('click', e => {
            try {
                const item = e.target.closest('.risk-item');
                if (!item) return;

                const type = item.dataset.type;
                const name = item.dataset.name;

                console.log(`📋 업무 지시 아이템 클릭: ${type} - ${name}`);

                if (type === 'TQC') {
                    ui.showTQCDetail(name);
                } else if (type === 'PO') {
                    ui.showRiskDetail('po', name);
                } else if (type === 'surge') {
                    // 불량 급증 항목 클릭 시 처리
                    const building = item.dataset.building;
                    const defect = item.dataset.defect;
                    console.log(`📈 불량 급증 클릭: ${building} - ${defect}`);
                    // 필요시 추가 처리 로직 구현
                }
            } catch (error) {
                console.error('❌ 업무 지시 클릭 처리 오류:', error);
            }
        });

        console.log('✅ 업무 지시 이벤트 초기화 완료');
        
    } catch (error) {
        console.error('❌ 업무 지시 이벤트 초기화 오류:', error);
    }
}

/**
 * 글로벌 에러 핸들러 설정
 */
function initializeErrorHandlers() {
    try {
        // 글로벌 JavaScript 에러 처리
        window.addEventListener('error', (e) => {
            console.error('🚨 글로벌 JavaScript 에러:', e.error);
            console.error('파일:', e.filename, '라인:', e.lineno, '컬럼:', e.colno);
        });

        // Promise rejection 에러 처리
        window.addEventListener('unhandledrejection', (e) => {
            console.error('🚨 처리되지 않은 Promise rejection:', e.reason);
        });

        console.log('✅ 글로벌 에러 핸들러 설정 완료');
        
    } catch (error) {
        console.error('❌ 글로벌 에러 핸들러 설정 오류:', error);
    }
}

/**
 * 디버깅 도구 설정
 */
function setupDebuggingTools() {
    try {
        // 개발 모드에서만 디버깅 도구 활성화
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            
            // 글로벌 디버깅 함수들 등록
            window.debugState = () => {
                console.log('🔍 현재 상태:', state);
            };
            
            window.debugRawData = () => {
                console.log('📊 원본 데이터:', {
                    exists: !!state.rawData,
                    length: state.rawData?.length,
                    sample: state.rawData?.slice(0, 3)
                });
            };
            
            window.debugProcessedData = () => {
                console.log('⚙️ 처리된 데이터:', state.processedData);
            };
            
            window.debugCharts = () => {
                console.log('📈 차트 인스턴스들:', state.charts);
            };
            
            window.debugFilters = () => {
                const filters = {};
                document.querySelectorAll('.filter-select').forEach(select => {
                    filters[select.id] = select.value;
                });
                console.log('🔍 현재 필터 상태:', filters);
            };
            
            window.debugForceUpdate = () => {
                console.log('🔄 강제 대시보드 업데이트 실행');
                if (state.rawData && state.rawData.length > 0) {
                    ui.updateDashboard();
                } else {
                    console.warn('⚠️ 데이터가 없어서 업데이트할 수 없습니다.');
                }
            };
            
            console.log('🔧 디버깅 도구 활성화됨. 사용 가능한 함수들:');
            console.log('  - debugState(): 현재 상태 출력');
            console.log('  - debugRawData(): 원본 데이터 정보 출력');
            console.log('  - debugProcessedData(): 처리된 데이터 출력');
            console.log('  - debugCharts(): 차트 인스턴스들 출력');
            console.log('  - debugFilters(): 현재 필터 상태 출력');
            console.log('  - debugForceUpdate(): 강제 대시보드 업데이트');
        }
        
        console.log('✅ 디버깅 도구 설정 완료');
        
    } catch (error) {
        console.error('❌ 디버깅 도구 설정 오류:', error);
    }
}

/**
 * 사용자에게 오류 메시지 표시
 */
function showErrorMessage(message) {
    try {
        // 간단한 알림 표시 (나중에 더 예쁜 토스트 메시지로 교체 가능)
        alert(`❌ 오류: ${message}`);
    } catch (error) {
        console.error('❌ 오류 메시지 표시 실패:', error);
    }
}

/**
 * 사용자에게 정보 메시지 표시
 */
function showInfoMessage(message) {
    try {
        // 간단한 알림 표시 (나중에 더 예쁜 토스트 메시지로 교체 가능)
        alert(`ℹ️ 정보: ${message}`);
    } catch (error) {
        console.error('❌ 정보 메시지 표시 실패:', error);
    }
}

/**
 * 성능 모니터링을 위한 함수 (선택적)
 */
function initializePerformanceMonitoring() {
    try {
        // 페이지 로드 성능 측정
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('📊 페이지 로드 성능:', {
                        총로딩시간: `${perfData.loadEventEnd - perfData.fetchStart}ms`,
                        DOM준비시간: `${perfData.domContentLoadedEventEnd - perfData.fetchStart}ms`,
                        리소스로딩: `${perfData.loadEventEnd - perfData.domContentLoadedEventEnd}ms`
                    });
                }
            }, 0);
        });
        
        console.log('✅ 성능 모니터링 초기화 완료');
        
    } catch (error) {
        console.error('❌ 성능 모니터링 초기화 오류:', error);
    }
}

// 성능 모니터링 초기화 (선택적)
initializePerformanceMonitoring();