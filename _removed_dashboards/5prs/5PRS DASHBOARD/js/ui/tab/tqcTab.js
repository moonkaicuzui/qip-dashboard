import { state } from '../../state.js';
import { translations } from '../../config.js';
import { createBarChart } from '../helpers/chartHelpers.js';

/**
 * TQC 분석 탭의 모든 컨텐츠를 업데이트하는 메인 함수
 */
export function updateTQCAnalysis() {
    updateTQCtable();
    updateTQCDistributionChart();
    updateTrainingPriorityCharts();
    updateTQCBuildingHeatmaps();
    
    // 탭별 특화 필터 이벤트 리스너 등록
    initializeTQCFilters();
}

/**
 * TQC 탭의 필터 이벤트 리스너를 초기화하는 함수
 */
function initializeTQCFilters() {
    // 교육 우선순위 불량 유형 필터
    const trainingFilter = document.getElementById('trainingDefectFilter');
    if (trainingFilter) {
        // 기존 이벤트 리스너 제거 후 새로 등록
        trainingFilter.removeEventListener('change', updateTrainingChart);
        trainingFilter.addEventListener('change', updateTrainingChart);
    }
    
    // TQC 테이블 필터들 (건물, 불량률, 위험도)
    const buildingFilter = document.getElementById('tqcBuildingFilter');
    const rejectRateFilter = document.getElementById('tqcRejectRateFilter');
    const riskFilter = document.getElementById('tqcRiskFilter');
    
    if (buildingFilter) {
        buildingFilter.removeEventListener('change', updateTQCtable);
        buildingFilter.addEventListener('change', updateTQCtable);
    }
    
    if (rejectRateFilter) {
        rejectRateFilter.removeEventListener('change', updateTQCtable);
        rejectRateFilter.addEventListener('change', updateTQCtable);
    }
    
    if (riskFilter) {
        riskFilter.removeEventListener('change', updateTQCtable);
        riskFilter.addEventListener('change', updateTQCtable);
    }
}

/**
 * TQC별 품질 성과 테이블을 업데이트하는 함수
 */
export function updateTQCtable() {
    const tqcTableBody = document.getElementById('tqcTableBody');
    const buildingFilter = document.getElementById('tqcBuildingFilter').value;
    const rejectRateFilter = document.getElementById('tqcRejectRateFilter').value;
    const riskFilter = document.getElementById('tqcRiskFilter')?.value || 'ALL';
    
    let filteredTQCs = Object.values(state.processedData.tqcData)
        .map(tqc => ({
            ...tqc,
            rejectRate: tqc.totalValidation > 0 ? (tqc.totalReject / tqc.totalValidation * 100) : 0,
        }))
        .filter(tqc => tqc.totalValidation > 0);

    if (buildingFilter !== 'ALL') {
        filteredTQCs = filteredTQCs.filter(tqc => tqc.buildings.has(buildingFilter));
    }

    if (rejectRateFilter !== 'ALL') {
        const [minStr, maxStr] = rejectRateFilter.split('-');
        const min = parseFloat(minStr);
        const max = maxStr ? parseFloat(maxStr) : Infinity;
        filteredTQCs = filteredTQCs.filter(tqc => tqc.rejectRate >= min && (maxStr ? tqc.rejectRate < max : true));
    }
    
    // 위험도 필터 적용
    if (riskFilter !== 'ALL') {
        if (riskFilter === 'HIGH') {
            // 고위험: 불량률 5% 이상 AND 검증량 100개 이상
            filteredTQCs = filteredTQCs.filter(tqc => tqc.rejectRate >= 5 && tqc.totalValidation >= 100);
        } else if (riskFilter === 'MEDIUM') {
            // 주의: 불량률 3-5%
            filteredTQCs = filteredTQCs.filter(tqc => tqc.rejectRate >= 3 && tqc.rejectRate < 5);
        } else if (riskFilter === 'LOW') {
            // 정상: 불량률 3% 미만
            filteredTQCs = filteredTQCs.filter(tqc => tqc.rejectRate < 3);
        }
    }
    
    filteredTQCs.sort((a, b) => b.rejectRate - a.rejectRate);

    tqcTableBody.innerHTML = filteredTQCs.slice(0, 10).map((tqc, index) => {
        const mainDefect = Object.entries(tqc.defects).sort((a, b) => b[1] - a[1])[0]?.[0] || '-';
        const lang = state.currentLanguage;
        const statusClass = tqc.rejectRate > 5 ? 'badge-danger' : tqc.rejectRate > 3 ? 'badge-warning' : 'badge-success';
        const statusText = tqc.rejectRate > 5 ? translations[lang].emergency : tqc.rejectRate > 3 ? translations[lang].warning : translations[lang].normal;
        return `
            <tr class="tqc-row" data-tqc-key="${tqc.id}-${tqc.name}">
                <td>${index + 1}</td>
                <td>${tqc.id}</td>
                <td>${tqc.name}</td>
                <td>${Array.from(tqc.buildings).join(', ')}</td>
                <td>${tqc.totalValidation.toLocaleString()}</td>
                <td>${tqc.totalReject.toLocaleString()}</td>
                <td>${tqc.rejectRate.toFixed(2)}%</td>
                <td>${mainDefect}</td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
            </tr>
        `;
    }).join('');
}

/**
 * TQC 불량률 분포 히스토그램을 업데이트하는 함수
 */
function updateTQCDistributionChart() {
    const tqcRates = Object.values(state.processedData.tqcData)
        .map(t => t.totalValidation > 0 ? (t.totalReject / t.totalValidation * 100) : 0);
    
    const bins = [0, 1, 2, 3, 5, 10, 100];
    const labels = bins.slice(0, -1).map((b, i) => i === bins.length - 2 ? `${b}%+` : `${b}-${bins[i+1]}%`);
    const data = new Array(bins.length - 1).fill(0);
    tqcRates.forEach(rate => {
        let binIndex = bins.findIndex(b => rate < b) -1;
        if (binIndex < 0) {
            if(rate >= bins[bins.length - 2]) binIndex = bins.length - 2;
        }
        if (binIndex >= 0) data[binIndex]++;
    });
    
    createBarChart('tqcDistributionChart', {
        labels,
        datasets: [{ label: 'TQC ' + translations[state.currentLanguage].count, data, backgroundColor: '#3b82f6' }]
    });
}

/**
 * 교육 우선순위 차트 데이터를 준비하는 함수
 */
function updateTrainingPriorityCharts() {
    const { defectTypes, tqcMissingDefects, tqcData } = state.processedData;
    const topDefects = Object.keys(defectTypes).sort((a, b) => defectTypes[b] - defectTypes[a]).slice(0, 5);

    state.trainingDefectData = topDefects.map(defect => {
        const tqcDefectData = Object.entries(tqcMissingDefects)
            .filter(([, tqcMissing]) => tqcMissing.defectBreakdown[defect] && tqcMissing.totalAuditorInspection > 50)
            .map(([tqcKey, tqcMissing]) => {
                const missingRate = (tqcMissing.defectBreakdown[defect] / tqcMissing.totalAuditorInspection * 100);
                const buildings = tqcData[tqcKey] ? Array.from(tqcData[tqcKey].buildings).join(', ') : 'N/A';
                return { name: tqcMissing.name, id: tqcMissing.id, buildings, missingRate };
            })
            .sort((a, b) => b.missingRate - a.missingRate);
        return { defectType: defect, tqcData: tqcDefectData.slice(0, 10) };
    });
    updateTrainingChart();
}

/**
 * 선택된 불량 유형에 대한 교육 우선순위 차트를 업데이트하는 함수
 */
export function updateTrainingChart() {
    const defectIndex = parseInt(document.getElementById('trainingDefectFilter').value);
    if (isNaN(defectIndex) || !state.trainingDefectData || !state.trainingDefectData[defectIndex]) {
        createBarChart('trainingPriorityChart', { labels:[], datasets:[] });
        return;
    };

    const data = state.trainingDefectData[defectIndex];
    createBarChart('trainingPriorityChart', {
        labels: data.tqcData.map(t => t.name),
        datasets: [{
            label: `${translations[state.currentLanguage].defectMissingRate} (%)`,
            data: data.tqcData.map(t => t.missingRate.toFixed(2)),
            backgroundColor: data.tqcData.map(t => t.missingRate > 1 ? '#ef4444' : t.missingRate > 0.5 ? '#f59e0b' : '#10b981')
        }]
    }, {
        plugins: {
            tooltip: {
                callbacks: {
                    title: tooltipItems => tooltipItems[0].label,
                    footer: tooltipItems => {
                        const tqcInfo = data.tqcData[tooltipItems[0].dataIndex];
                        return [`TQC ID: ${tqcInfo.id}`, `${translations[state.currentLanguage].workingArea}: ${tqcInfo.buildings}`];
                    }
                }
            }
        }
    });
}

/**
 * 구역별 TQC Defect Missing 히트맵을 업데이트하는 함수
 */
function updateTQCBuildingHeatmaps() {
    const container = document.getElementById('tqcBuildingHeatmapContainer');
    if (!container) return;
    
    container.innerHTML = '';
    const { buildings, tqcMissingDefects, defectTypes, tqcData } = state.processedData;
    const topDefects = Object.keys(defectTypes).sort((a, b) => defectTypes[b] - defectTypes[a]).slice(0, 5);

    buildings.forEach(building => {
        const buildingTQCs = Object.keys(tqcData).filter(key => tqcData[key].buildings.has(building));
        if (buildingTQCs.length === 0) return;

        const section = document.createElement('div');
        section.className = 'building-heatmap-section';
        section.innerHTML = `<div class="building-heatmap-title">${building}</div>`;

        const table = document.createElement('table');
        table.className = 'heatmap-table';
        
        let headerHtml = `<thead><tr><th>TQC</th>`;
        topDefects.forEach(defect => headerHtml += `<th>${defect}</th>`);
        headerHtml += `</tr></thead>`;

        let bodyHtml = '<tbody>';
        buildingTQCs.forEach(tqcKey => {
            const tqcName = tqcData[tqcKey]?.name || '';
            const tqcMissing = tqcMissingDefects[tqcKey];
            if (!tqcMissing) return;

            bodyHtml += `<tr><td class="heatmap-label">${tqcName}</td>`;
            topDefects.forEach(defect => {
                const defectCount = tqcMissing.defectBreakdown[defect] || 0;
                const missingRate = tqcMissing.totalAuditorInspection > 0 ? (defectCount / tqcMissing.totalAuditorInspection * 100) : 0;
                const intensity = missingRate / 2;
                const color = `rgba(239, 68, 68, ${intensity})`;
                bodyHtml += `<td class="heatmap-cell" style="background-color: ${color}; color: ${intensity > 0.5 ? 'white' : 'black'};" 
                                data-type="tqc-defect" data-tqc-key="${tqcKey}" data-defect="${defect}">
                                ${missingRate.toFixed(2)}%
                             </td>`;
            });
            bodyHtml += '</tr>';
        });
        bodyHtml += '</tbody>';

        table.innerHTML = headerHtml + bodyHtml;
        section.appendChild(table);
        container.appendChild(section);
    });
}

