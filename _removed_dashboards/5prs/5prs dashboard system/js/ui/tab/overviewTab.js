import { state } from '../../state.js';
import { translations } from '../../config.js';
import { parseDate, calculateLinearRegression, analyzeTrend, addTrendIndicator } from '../helpers/uiUtils.js';
import { createLineChart, createPieChart, createBarChart } from '../helpers/chartHelpers.js';

/**
 * 전체 현황 탭의 모든 차트를 업데이트하는 메인 함수
 */
export function updateOverviewCharts() {
    try {
        console.log('🔄 updateOverviewCharts 시작');
        
        // 필터 값 가져오기
        const buildingFilter = document.getElementById('overviewBuildingFilter')?.value || 'ALL';
        
        // 프로세스된 데이터 확인
        const { dailyData, defectTypes, buildingData, dailyTqcCount, dailyLineCount } = state.processedData || {};
        const { rawData } = state;
        
        // 🔥 디버깅: 데이터 상태 로그
        console.log('📊 데이터 상태 확인:', {
            rawDataExists: !!rawData,
            rawDataLength: rawData?.length || 0,
            buildingFilter,
            dailyDataKeys: Object.keys(dailyData || {}).length,
            buildingDataKeys: Object.keys(buildingData || {}).length,
            defectTypesKeys: Object.keys(defectTypes || {}).length
        });
        
        // rawData가 없으면 경고하고 빈 차트 생성
        if (!rawData || rawData.length === 0) {
            console.warn('⚠️ rawData가 없어서 빈 차트를 생성합니다.');
            createEmptyChartsForOverview();
            return;
        }

        // processedData가 없으면 경고
        if (!dailyData || !buildingData || !defectTypes) {
            console.warn('⚠️ processedData가 완전하지 않습니다:', {
                dailyData: !!dailyData,
                buildingData: !!buildingData,
                defectTypes: !!defectTypes
            });
            createEmptyChartsForOverview();
            return;
        }

        // 필터링된 데이터 준비
        let filteredDailyData = {};
        let filteredDefectTypes = {};
        
        if (buildingFilter === 'ALL') {
            filteredDailyData = dailyData;
            filteredDefectTypes = defectTypes;
        } else {
            // 특정 구역으로 필터링
            filteredDailyData = {};
            const filteredRows = rawData.filter(row => row['Building'] === buildingFilter);
            
            console.log(`🏢 구역 '${buildingFilter}' 필터링 결과: ${filteredRows.length}개 행`);
            
            filteredRows.forEach(row => {
                const date = parseDate(row['Inspection Date']);
                if (date) {
                    const dateStr = date.toISOString().split('T')[0];
                    if (dailyData[dateStr]) { // 해당 날짜가 전체 데이터에 있는 경우만
                        if (!filteredDailyData[dateStr]) {
                            filteredDailyData[dateStr] = { totalValidation: 0, totalReject: 0 };
                        }
                        filteredDailyData[dateStr].totalValidation += parseInt(row['Validation Qty']) || 0;
                        filteredDailyData[dateStr].totalReject += parseInt(row['Reject Qty']) || 0;
                    }
                }
            });
            
            if (buildingData[buildingFilter]) {
                filteredDefectTypes = buildingData[buildingFilter].defects || {};
            }
        }

        // 일별 불량률 추이 차트 생성
        createDailyRejectTrendChart(filteredDailyData);
        
        // 불량 유형 분포 파이 차트 생성
        createDefectTypeDistributionChart(filteredDefectTypes);
        
        // 구역별 품질 현황 바 차트 생성
        createBuildingQualityChart(buildingData);
        
        // 탭별 특화 필터 이벤트 리스너 등록
        initializeOverviewFilters();
        
        console.log('✅ updateOverviewCharts 완료');
        
    } catch (error) {
        console.error('❌ updateOverviewCharts 오류:', error);
        createEmptyChartsForOverview();
    }
}

/**
 * 일별 불량률 추이 차트 생성
 */
function createDailyRejectTrendChart(filteredDailyData) {
    try {
        const dailyDates = Object.keys(filteredDailyData).sort();
        const dailyRejectRates = dailyDates.map(date => {
            const data = filteredDailyData[date];
            return data.totalValidation > 0 ? (data.totalReject / data.totalValidation * 100) : 0;
        });

        if (dailyDates.length === 0) {
            console.warn('⚠️ 일별 데이터가 없어서 빈 차트를 생성합니다.');
            createEmptyChart('dailyTrendChart', '일별 불량률 추이 (데이터 없음)');
            return;
        }

        // 추세선 계산 및 추세 판단
        const trendLine = calculateLinearRegression(dailyRejectRates);
        const trendType = analyzeTrend(trendLine);

        // 날짜 레이블을 MM-DD 형식으로 단축
        const shortDailyLabels = dailyDates.map(date => date.substring(5));

        const dailyChartDatasets = [{
            label: translations[state.currentLanguage].rejectRate + ' (%)',
            data: dailyRejectRates,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4,
            fill: true
        }, {
            label: translations[state.currentLanguage].trendLine,
            data: trendLine,
            borderColor: '#9ca3af',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 0,
            fill: false
        }];
        
        createLineChart('dailyTrendChart', { 
            labels: shortDailyLabels, 
            datasets: dailyChartDatasets 
        }, getStandardChartOptions());
        
        // 추세 표시 추가
        const chartCard = document.getElementById('dailyTrendChart')?.closest('.card');
        if (chartCard) {
            addTrendIndicator(chartCard, trendType, dailyRejectRates);
        }
        
        console.log('✅ 일별 불량률 추이 차트 생성 완료');
        
    } catch (error) {
        console.error('❌ 일별 불량률 추이 차트 생성 오류:', error);
        createEmptyChart('dailyTrendChart', '일별 불량률 추이 (오류 발생)');
    }
}

/**
 * 불량 유형 분포 파이 차트 생성
 */
function createDefectTypeDistributionChart(filteredDefectTypes) {
    try {
        const defectLabels = Object.keys(filteredDefectTypes).sort((a, b) => filteredDefectTypes[b] - filteredDefectTypes[a]).slice(0, 10);
        
        if (defectLabels.length === 0) {
            console.warn('⚠️ 불량 유형 데이터가 없어서 빈 차트를 생성합니다.');
            createEmptyChart('defectTypeChart', '불량 유형 분포 (데이터 없음)', 'pie');
            return;
        }
        
        createPieChart('defectTypeChart', {
            labels: defectLabels,
            datasets: [{
                data: defectLabels.map(label => Math.round(filteredDefectTypes[label])),
                backgroundColor: [
                    '#ef4444', '#f97316', '#10b981', '#3b82f6', '#8b5cf6', 
                    '#ec4899', '#14b8a6', '#f59e0b', '#a855f7', '#6b7280'
                ]
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    bottom: 15,
                    top: 10,
                    left: 10,
                    right: 10
                }
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: { size: 10 },
                        boxWidth: 12
                    }
                }
            }
        });
        
        console.log('✅ 불량 유형 분포 차트 생성 완료');
        
    } catch (error) {
        console.error('❌ 불량 유형 분포 차트 생성 오류:', error);
        createEmptyChart('defectTypeChart', '불량 유형 분포 (오류 발생)', 'pie');
    }
}

/**
 * 구역별 품질 현황 바 차트 생성
 */
function createBuildingQualityChart(buildingData) {
    try {
        const buildingLabels = Object.keys(buildingData || {});
        
        if (buildingLabels.length === 0) {
            console.warn('⚠️ 구역별 데이터가 없어서 빈 차트를 생성합니다.');
            createEmptyChart('buildingChart', '구역별 품질 현황 (데이터 없음)', 'bar');
            return;
        }
        
        const buildingRejectRates = buildingLabels.map(b => {
            const data = buildingData[b];
            return data.totalValidation > 0 ? (data.totalReject / data.totalValidation * 100) : 0;
        });
        
        createBarChart('buildingChart', {
            labels: buildingLabels,
            datasets: [{
                label: translations[state.currentLanguage].rejectRate + ' (%)',
                data: buildingRejectRates.map(r => r.toFixed(2)),
                backgroundColor: buildingRejectRates.map(r => 
                    r > 5 ? '#ef4444' : r > 3 ? '#f59e0b' : '#10b981'
                )
            }]
        }, getStandardChartOptions());
        
        console.log('✅ 구역별 품질 현황 차트 생성 완료');
        
    } catch (error) {
        console.error('❌ 구역별 품질 현황 차트 생성 오류:', error);
        createEmptyChart('buildingChart', '구역별 품질 현황 (오류 발생)', 'bar');
    }
}

/**
 * 전체 현황 탭의 필터 이벤트 리스너를 초기화하는 함수
 */
function initializeOverviewFilters() {
    try {
        // 메인 구역 필터 (전체 차트 업데이트)
        const buildingFilter = document.getElementById('overviewBuildingFilter');
        if (buildingFilter) {
            // 기존 이벤트 리스너 제거 후 새로 추가
            buildingFilter.removeEventListener('change', handleMainBuildingFilterChange);
            buildingFilter.addEventListener('change', handleMainBuildingFilterChange);
            console.log('✅ 메인 구역 필터 이벤트 리스너 등록 완료');
        }
    } catch (error) {
        console.error('❌ 필터 이벤트 리스너 초기화 오류:', error);
    }
}

/**
 * 메인 구역 필터 변경 핸들러
 */
function handleMainBuildingFilterChange() {
    console.log('🔄 메인 구역 필터 변경됨');
    try {
        if (state.rawData && state.rawData.length > 0) {
            updateOverviewCharts();
        }
    } catch (error) {
        console.error('❌ 메인 구역 필터 변경 처리 오류:', error);
    }
}

/**
 * 🔥 빈 차트 생성 함수 (개선된 버전)
 */
function createEmptyChart(canvasId, label, chartType = 'line') {
    try {
        const defaultDates = [];
        const defaultData = [];
        
        // 최근 30일 기본 날짜 생성
        for (let i = 29; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            defaultDates.push(date.toISOString().split('T')[0].substring(5)); // MM-DD
            defaultData.push(0);
        }
        
        const chartConfig = {
            labels: defaultDates,
            datasets: [{
                label: label,
                data: defaultData,
                borderColor: '#e5e7eb',
                backgroundColor: 'rgba(229, 231, 235, 0.1)',
                fill: chartType === 'line',
                tension: 0.4
            }]
        };
        
        const options = {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    bottom: 25,
                    top: 15,
                    left: 15,
                    right: 15
                }
            },
            scales: {
                x: {
                    display: true,
                    ticks: { font: { size: 11 } }
                },
                y: {
                    display: true,
                    ticks: { font: { size: 10 } }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: { size: 11 },
                        boxWidth: 12
                    }
                }
            }
        };
        
        if (chartType === 'line') {
            createLineChart(canvasId, chartConfig, options);
        } else if (chartType === 'bar') {
            createBarChart(canvasId, chartConfig, options);
        } else if (chartType === 'pie') {
            createPieChart(canvasId, {
                labels: ['데이터 없음'],
                datasets: [{
                    data: [1],
                    backgroundColor: ['#e5e7eb']
                }]
            }, options);
        }
        
        console.log(`✅ 빈 차트 생성 완료: ${canvasId}`);
        
    } catch (error) {
        console.error(`❌ 빈 차트 생성 오류 (${canvasId}):`, error);
    }
}

/**
 * 🔥 전체 현황 탭의 모든 빈 차트 생성
 */
function createEmptyChartsForOverview() {
    try {
        console.log('📊 전체 현황 탭 빈 차트들 생성 중...');
        
        createEmptyChart('dailyTrendChart', '일별 불량률 추이 (데이터 없음)');
        createEmptyChart('defectTypeChart', '불량 유형 분포 (데이터 없음)', 'pie');
        createEmptyChart('buildingChart', '구역별 품질 현황 (데이터 없음)', 'bar');
        
        console.log('✅ 전체 현황 탭 빈 차트들 생성 완료');
        
    } catch (error) {
        console.error('❌ 전체 현황 탭 빈 차트들 생성 오류:', error);
    }
}

/**
 * 🔥 표준 차트 옵션 반환
 */
function getStandardChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: {
                bottom: 25,
                top: 15,
                left: 15,
                right: 15
            }
        },
        scales: {
            x: {
                display: true,
                ticks: {
                    maxRotation: 45,
                    minRotation: 0,
                    font: { size: 11 }
                },
                grid: { display: true }
            },
            y: {
                display: true,
                ticks: { font: { size: 10 } }
            }
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    font: { size: 11 },
                    boxWidth: 12
                }
            }
        }
    };
}