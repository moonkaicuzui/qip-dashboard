import { state } from '../../state.js';
import { translations } from '../../config.js';
import { parseDate, parseDefectTypes, calculateLinearRegression } from '../helpers/uiUtils.js';
import { createLineChart, createBarChart, createPieChart } from '../helpers/chartHelpers.js';

/**
 * 불량 분석 탭의 모든 컨텐츠를 업데이트하는 메인 함수
 */
export function updateDefectAnalysis() {
    updateDefectTrendChart();
    updateDefectDetail();
    updateModelDefectAnalysis();
    updateDefectBuildingHeatmap();
    updateModelDefectHeatmap();
    
    // 탭별 특화 필터 이벤트 리스너 등록
    initializeDefectsFilters();
}

/**
 * 불량 분석 탭의 필터 이벤트 리스너를 초기화하는 함수
 */
function initializeDefectsFilters() {
    // 불량 유형 상세 필터
    const defectDetailFilter = document.getElementById('defectTypeDetailFilter');
    if (defectDetailFilter) {
        defectDetailFilter.removeEventListener('change', handleDefectDetailFilterChange);
        defectDetailFilter.addEventListener('change', handleDefectDetailFilterChange);
    }
    
    // 모델 필터
    const modelFilter = document.getElementById('modelFilter');
    if (modelFilter) {
        modelFilter.removeEventListener('change', updateModelDefectAnalysis);
        modelFilter.addEventListener('change', updateModelDefectAnalysis);
    }
    
    // 모델별 불량 유형 필터
    const modelDefectTypeFilter = document.getElementById('modelDefectTypeFilter');
    if (modelDefectTypeFilter) {
        modelDefectTypeFilter.removeEventListener('change', updateModelDefectAnalysis);
        modelDefectTypeFilter.addEventListener('change', updateModelDefectAnalysis);
    }
    
    // 구역 필터 (전체 차트 업데이트)
    const buildingFilter = document.getElementById('defectsBuildingFilter');
    if (buildingFilter) {
        buildingFilter.removeEventListener('change', handleBuildingFilterChange);
        buildingFilter.addEventListener('change', handleBuildingFilterChange);
    }
}

/**
 * 불량 유형 상세 필터 변경 핸들러
 */
function handleDefectDetailFilterChange() {
    updateDefectTrendChart();
    updateDefectDetail();
}

/**
 * 구역 필터 변경 핸들러
 */
function handleBuildingFilterChange() {
    updateDefectTrendChart();
}

/**
 * 불량 유형별 발생 추이 차트를 업데이트하는 함수
 */
function updateDefectTrendChart() {
    const filterElement = document.getElementById('defectTypeDetailFilter');
    if (!filterElement) return;
    const defectTypeFilter = filterElement.value;
    const dates = Object.keys(state.processedData.dailyData).sort();
    const { buildings } = state.processedData;
    const { rawData } = state;
    if (!rawData) return;

    const colors = ['#ef4444', '#f97316', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];
    let datasets = [];

    const createTrendlineDataset = (dataPoints, label, color) => ({
        label,
        data: calculateLinearRegression(dataPoints),
        borderColor: color,
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        type: 'line',
        backgroundColor: 'transparent'
    });

    if (defectTypeFilter === 'ALL') {
        datasets = buildings.map((building, index) => {
            const dataPoints = dates.map(date => {
                let validation = 0, reject = 0;
                rawData.forEach(row => {
                    const rowDate = parseDate(row['Inspection Date']);
                    if (rowDate && rowDate.toISOString().split('T')[0] === date && row['Building'] === building) {
                        validation += parseInt(row['Validation Qty']) || 0;
                        reject += parseInt(row['Reject Qty']) || 0;
                    }
                });
                return validation > 0 ? (reject / validation * 100) : 0;
            });
            return createTrendlineDataset(dataPoints, building, colors[index % colors.length]);
        });
    } else {
        datasets = buildings.map((building, index) => {
            const dataPoints = dates.map(date => {
                let count = 0;
                rawData.forEach(row => {
                    const rowDate = parseDate(row['Inspection Date']);
                    if (rowDate && rowDate.toISOString().split('T')[0] === date && row['Building'] === building && row['Error']?.includes(defectTypeFilter)) {
                        count += (parseInt(row['Reject Qty']) || 0) / (parseDefectTypes(row['Error']).length || 1);
                    }
                });
                return count;
            });
            return createTrendlineDataset(dataPoints, building, colors[index % colors.length]);
        });
    }
    createLineChart('defectTrendChart', { labels: dates, datasets });
}

/**
 * 불량 유형 상세 정보를 업데이트하는 함수
 */
function updateDefectDetail() {
    const defectTypeFilter = document.getElementById('defectTypeDetailFilter').value;
    const tableContainer = document.querySelector('#defects-panel .table-container');
    const oldChartContainer = document.getElementById('defectDetailPieChartContainer');
    if(oldChartContainer) oldChartContainer.remove();

    if (defectTypeFilter === 'ALL') {
        tableContainer.style.display = 'block';
        updateDefectDetailTable();
    } else {
        tableContainer.style.display = 'none';
        const buildingCounts = {};
        state.rawData.forEach(row => {
            if (row['Error']?.includes(defectTypeFilter)) {
                const building = row['Building'] || 'Unknown';
                buildingCounts[building] = (buildingCounts[building] || 0) + (parseInt(row['Reject Qty']) || 0) / (parseDefectTypes(row['Error']).length || 1);
            }
        });
        const chartContainer = document.createElement('div');
        chartContainer.id = 'defectDetailPieChartContainer';
        chartContainer.className = 'chart-container';
        chartContainer.innerHTML = `<canvas id="defectDetailPieChart"></canvas>`;
        tableContainer.parentNode.insertBefore(chartContainer, tableContainer.nextSibling);
        createPieChart('defectDetailPieChart', {
            labels: Object.keys(buildingCounts),
            datasets: [{ data: Object.values(buildingCounts), backgroundColor: ['#ef4444', '#f97316', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'] }]
        });
    }
}

/**
 * 불량 상세 테이블을 업데이트하는 함수
 */
export function updateDefectDetailTable() {
    const defectDetailBody = document.getElementById('defectDetailBody');
    const { defectTypes } = state.processedData;
    const top5Defects = Object.keys(defectTypes).sort((a,b) => defectTypes[b] - defectTypes[a]).slice(0, 5);
    const totalTop5Count = top5Defects.reduce((sum, key) => sum + defectTypes[key], 0);
    defectDetailBody.innerHTML = top5Defects.map(defect => {
        const buildingCounts = {};
        state.rawData.forEach(row => {
            if (row['Error']?.includes(defect)) {
                buildingCounts[row['Building'] || 'Unknown'] = (buildingCounts[row['Building'] || 'Unknown'] || 0) + 1;
            }
        });
        const mainBuilding = Object.keys(buildingCounts).sort((a, b) => buildingCounts[b] - buildingCounts[a])[0] || '-';
        return `<tr><td>${defect}</td><td>${Math.round(defectTypes[defect]).toLocaleString()}</td><td>${totalTop5Count > 0 ? (defectTypes[defect] / totalTop5Count * 100).toFixed(1) : 0}%</td><td>${mainBuilding}</td></tr>`;
    }).join('');
}

/**
 * 모델별 불량 분석을 업데이트하는 함수
 */
export function updateModelDefectAnalysis() {
    const modelFilter = document.getElementById('modelFilter').value;
    const defectTypeFilter = document.getElementById('modelDefectTypeFilter').value;
    const { modelData } = state.processedData;
    let labels, data, title;

    if (modelFilter === 'ALL') {
        const modelsToShow = Object.entries(modelData).filter(([, val]) => val.totalValidation > 50).sort((a, b) => b[1].totalValidation - a[1].totalValidation).slice(0, 15);
        labels = modelsToShow.map(m => m[0]);
        data = modelsToShow.map(([model, mData]) => {
            const rejectCount = (defectTypeFilter === 'ALL') ? mData.totalReject : (mData.defects[defectTypeFilter] || 0);
            return mData.totalValidation > 0 ? (rejectCount / mData.totalValidation * 100) : 0;
        });
        title = translations[state.currentLanguage].rejectRate + ' (%)';
    } else {
        const buildingStats = {};
        state.rawData.filter(row => row['Model'] === modelFilter).forEach(row => {
            const building = row['Building'] || 'Unknown';
            if (!buildingStats[building]) buildingStats[building] = { validation: 0, reject: 0 };
            const validationQty = parseInt(row['Validation Qty']) || 0;
            let rejectQty = 0;
            if (defectTypeFilter === 'ALL') {
                rejectQty = parseInt(row['Reject Qty']) || 0;
            } else if (row['Error']?.includes(defectTypeFilter)) {
                rejectQty = (parseInt(row['Reject Qty']) || 0) / (parseDefectTypes(row['Error']).length || 1);
            }
            buildingStats[building].validation += validationQty;
            buildingStats[building].reject += rejectQty;
        });
        labels = Object.keys(buildingStats);
        data = labels.map(b => buildingStats[b].validation > 0 ? (buildingStats[b].reject / buildingStats[b].validation * 100) : 0);
        title = `${modelFilter} - ${translations[state.currentLanguage].buildingRejectComparison}`;
    }
    createBarChart('modelDefectChart', { labels, datasets: [{ label: title, data: data.map(d => d.toFixed(2)), backgroundColor: '#3b82f6' }] });
}

/**
 * 구역별 불량 유형 히트맵을 업데이트하는 함수
 */
function updateDefectBuildingHeatmap() {
    const heatmapTable = document.getElementById('defectBuildingHeatmap');
    const { buildingData, defectTypes } = state.processedData;
    const topDefects = Object.keys(defectTypes).sort((a, b) => defectTypes[b] - defectTypes[a]).slice(0, 5);
    
    let html = `<thead><tr><th>${translations[state.currentLanguage].building}</th>`;
    topDefects.forEach(defect => html += `<th>${defect}</th>`);
    html += '</tr></thead><tbody>';

    let maxRate = 0;
    Object.values(buildingData).forEach(data => {
        topDefects.forEach(defect => {
            const rate = data.totalValidation > 0 ? ((data.defects[defect] || 0) / data.totalValidation * 100) : 0;
            if (rate > maxRate) maxRate = rate;
        });
    });

    Object.entries(buildingData).forEach(([building, data]) => {
        html += `<tr><td class="heatmap-label">${building}</td>`;
        topDefects.forEach(defect => {
            const value = data.totalValidation > 0 ? ((data.defects[defect] || 0) / data.totalValidation * 100) : 0;
            const intensity = maxRate > 0 ? value / maxRate : 0;
            const color = `rgba(239, 68, 68, ${intensity})`;
            html += `<td class="heatmap-cell" style="background-color: ${color}; color: ${intensity > 0.5 ? 'white' : 'black'};" data-type="building" data-item="${building}" data-defect="${defect}">${value.toFixed(2)}%</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';
    heatmapTable.innerHTML = html;
}

/**
 * 모델별 불량 유형 히트맵을 업데이트하는 함수
 */
function updateModelDefectHeatmap() {
    const heatmapTable = document.getElementById('modelDefectHeatmap');
    const { modelData, defectTypes } = state.processedData;
    const topDefects = Object.keys(defectTypes).sort((a, b) => defectTypes[b] - defectTypes[a]).slice(0, 5);
    const topModels = Object.entries(modelData).sort((a,b) => b[1].totalValidation - a[1].totalValidation).slice(0,15);

    let html = `<thead><tr><th>${translations[state.currentLanguage].model}</th>`;
    topDefects.forEach(defect => html += `<th>${defect}</th>`);
    html += '</tr></thead><tbody>';

    let maxRate = 0;
    topModels.forEach(([, data]) => {
        topDefects.forEach(defect => {
            const rate = data.totalValidation > 0 ? ((data.defects[defect] || 0) / data.totalValidation * 100) : 0;
            if(rate > maxRate) maxRate = rate;
        });
    });

    topModels.forEach(([model, data]) => {
        html += `<tr><td class="heatmap-label">${model}</td>`;
        topDefects.forEach(defect => {
            const value = data.totalValidation > 0 ? ((data.defects[defect] || 0) / data.totalValidation * 100) : 0;
            const intensity = maxRate > 0 ? value / maxRate : 0;
            const color = `rgba(239, 68, 68, ${intensity})`;
            html += `<td class="heatmap-cell" style="background-color: ${color}; color: ${intensity > 0.5 ? 'white' : 'black'};" data-type="model" data-item="${model}" data-defect="${defect}">${value.toFixed(2)}%</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';
    heatmapTable.innerHTML = html;
}
