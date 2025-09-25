import { state } from '../../state.js';
import { translations } from '../../config.js';
import { parseDate, parseDefectTypes } from '../helpers/uiUtils.js';
import { createLineChart } from '../helpers/chartHelpers.js';
import { openModal } from '../helpers/modalHelpers.js';


/**
 * 업무 지시 탭의 모든 컨텐츠를 업데이트하는 메인 함수
 */
export function updateActionItems() {
    const urgentItems = generateUrgentItems();
    const defectSurges = detectDefectSurges();
    populateTodayFocus(urgentItems, defectSurges);
    populateInspectorAssignments(urgentItems, defectSurges);
    populateWeeklyActionPlan(urgentItems, defectSurges);
}

/**
 * 긴급 조치가 필요한 항목들을 생성하는 함수
 */
function generateUrgentItems() {
    const { tqcData, poData } = state.processedData;
    const urgentItems = [];
    const lang = state.currentLanguage;

    Object.values(tqcData).forEach(tqc => {
        const rejectRate = tqc.totalValidation > 0 ? (tqc.totalReject / tqc.totalValidation * 100) : 0;
        if (tqc.totalValidation > 100 && rejectRate > 5) {
            urgentItems.push({
                type: 'TQC',
                key: `${tqc.id}-${tqc.name}`,
                name: tqc.name,
                id: tqc.id,
                detail: `${translations[lang].rejectRate} ${rejectRate.toFixed(1)}%`,
                rejectRate: rejectRate,
                reason: translations[lang].immediateInspection,
                buildings: Array.from(tqc.buildings)
            });
        }
    });

    Object.entries(poData).forEach(([po, data]) => {
        const rejectRate = data.totalValidation > 0 ? (data.totalReject / data.totalValidation * 100) : 0;
        if (data.totalValidation > 100 && rejectRate > 5) {
            urgentItems.push({
                type: 'PO',
                key: po,
                name: po,
                detail: `${translations[lang].rejectRate} ${rejectRate.toFixed(1)}%`,
                rejectRate: rejectRate,
                reason: translations[lang].focusVerificationNeeded
            });
        }
    });
    return urgentItems.sort((a,b) => b.rejectRate - a.rejectRate);
}

/**
 * 불량 급증을 감지하는 함수
 */
function detectDefectSurges() {
    const { buildingData, defectTypes, rawData } = state.processedData;
    const surges = [];
    if (!rawData || rawData.length === 0) return surges;
    
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
    const fourWeeksAgo = new Date();
    fourWeeksAgo.setDate(fourWeeksAgo.getDate() - 28);
    
    Object.keys(buildingData).forEach(building => {
        Object.keys(defectTypes).forEach(defect => {
            let recentCount = 0, recentValidation = 0, pastCount = 0, pastValidation = 0;
            
            rawData.forEach(row => {
                const date = parseDate(row['Inspection Date']);
                if (!date || row['Building'] !== building) return;
                
                const validationQty = parseInt(row['Validation Qty']) || 0;
                const rejectQty = parseInt(row['Reject Qty']) || 0;
                const hasDefect = row['Error']?.includes(defect);
                
                if (date >= threeDaysAgo) {
                    recentValidation += validationQty;
                    if (hasDefect && rejectQty > 0) recentCount += rejectQty / (parseDefectTypes(row['Error']).length || 1);
                } else if (date >= fourWeeksAgo && date < threeDaysAgo) {
                    pastValidation += validationQty;
                    if (hasDefect && rejectQty > 0) pastCount += rejectQty / (parseDefectTypes(row['Error']).length || 1);
                }
            });
            
            const recentRate = recentValidation > 0 ? (recentCount / recentValidation * 100) : 0;
            const pastRate = pastValidation > 0 ? (pastCount / pastValidation * 100) : 0;
            
            if (pastRate > 0 && recentRate > pastRate * 2 && recentRate > 3) {
                const increasePercent = ((recentRate - pastRate) / pastRate * 100).toFixed(0);
                const problemTQCs = Object.values(state.processedData.tqcData)
                    .filter(tqc => tqc.buildings.has(building) && tqc.defects[defect])
                    .map(tqc => ({ ...tqc, tqcDefectRate: tqc.totalValidation > 0 ? (tqc.defects[defect] / tqc.totalValidation * 100) : 0 }))
                    .filter(tqc => tqc.tqcDefectRate > 3)
                    .sort((a, b) => b.tqcDefectRate - a.tqcDefectRate)
                    .slice(0, 3);
                
                surges.push({ building, defect, recentRate, pastRate, increasePercent, problemTQCs });
            }
        });
    });
    
    return surges.sort((a, b) => b.recentRate - a.recentRate);
}

/**
 * 긴급 중점 관리 대상을 표시하는 함수
 */
function populateTodayFocus(urgentItems, defectSurges) {
    const container = document.getElementById('todayFocus');
    if (!container) return;
    const lang = state.currentLanguage;
    let html = '';
    
    urgentItems.filter(item => item.type === 'TQC').slice(0, 3).forEach(item => {
        html += `
            <div class="risk-item" data-type="${item.type}" data-name="${item.key}">
                <div>
                    <span class="badge badge-danger">${item.type}</span>
                    <span class="item-name" style="margin-left: 8px;">${item.name}</span>
                    <span class="item-detail">${item.detail}</span>
                </div>
                <span style="color: var(--danger-color); font-size: 0.8rem; font-weight: 500;">${item.reason}</span>
            </div>`;
    });
    
    defectSurges.slice(0, 2).forEach(surge => {
        const affectedTQCs = surge.problemTQCs.map(t => t.name).join(', ');
        html += `
            <div class="risk-item" data-type="surge" data-building="${surge.building}" data-defect="${surge.defect}">
                <div>
                    <span class="badge badge-warning">${translations[lang].surgeIncrease}</span>
                    <span class="item-name" style="margin-left: 8px;">${surge.building} - ${surge.defect}</span>
                    <span class="item-detail">${translations[lang].pastCompared} ${surge.increasePercent}% ↑</span>
                </div>
                <span style="color: var(--warning-color); font-size: 0.8rem;">${translations[lang].specialAttention}: ${affectedTQCs}</span>
            </div>`;
    });
    
    container.innerHTML = html || `<p style="color: var(--gray-400);">${translations[lang].noUrgentItemsMessage}</p>`;
}

/**
 * 어딧터별 추천 업무를 표시하는 함수
 */
function populateInspectorAssignments(urgentItems, defectSurges) {
    const container = document.getElementById('inspectorAssignments');
    if (!container) return;
    const lang = state.currentLanguage;
    const inspectorData = state.processedData.inspectorData;
    
    if (!inspectorData || Object.keys(inspectorData).length === 0) {
        container.innerHTML = `<p style="color: var(--gray-400);">${translations[lang].loadingDataMessage}</p>`;
        return;
    }
    
    // 최근 2주내 데이터가 있는 어딧터만 필터링
    const twoWeeksAgo = new Date();
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
    
    const activeInspectors = Object.values(inspectorData).filter(inspector => {
        if (!inspector.trends || inspector.trends.dates.length === 0) return false;
        const lastDate = new Date(inspector.trends.dates[inspector.trends.dates.length - 1]);
        return lastDate >= twoWeeksAgo;
    });
    
    activeInspectors.forEach(inspector => {
        inspector.urgentItems = urgentItems;
        inspector.defectSurges = defectSurges;
    });
    
    container.innerHTML = `
        <div class="table-container">
            <table class="auditor-table">
                <thead>
                    <tr>
                        <th>${translations[lang].auditor} ${translations[lang].name}</th>
                        <th>${translations[lang].avgDailyTqcCount}</th>
                        <th>${translations[lang].avgDailyValidation}</th>
                        <th>${translations[lang].rejectRate}</th>
                    </tr>
                </thead>
                <tbody>
                    ${activeInspectors.map(auditor => {
                        const rejectRate = auditor.totalValidation > 0 ? (auditor.totalReject / auditor.totalValidation * 100).toFixed(1) : '0.0';
                        return `
                            <tr class="auditor-row" data-auditor-key="${auditor.id}-${auditor.name}" style="cursor: pointer;">
                                <td><strong>${auditor.name}</strong></td>
                                <td>${auditor.avgDailyTqcCount.toFixed(1)}${translations[lang].name}</td>
                                <td>${Math.round(auditor.avgDailyValidation).toLocaleString()}</td>
                                <td>
                                    <span class="badge ${rejectRate > 5 ? 'badge-danger' : rejectRate > 3 ? 'badge-warning' : 'badge-success'}">
                                        ${rejectRate}%
                                    </span>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    container.querySelectorAll('.auditor-row').forEach(row => {
        row.addEventListener('click', (e) => {
            const auditorKey = e.currentTarget.dataset.auditorKey;
            showAuditorDetailWithRecommendations(auditorKey);
        });
    });
}

/**
 * 어딧터 상세 정보와 추천사항을 표시하는 함수
 */
function showAuditorDetailWithRecommendations(auditorKey) {
    const lang = state.currentLanguage;
    const auditorData = state.processedData.inspectorData[auditorKey];
    if (!auditorData) return;
    
    const fixedBuilding = auditorData.buildings ? Array.from(auditorData.buildings)[0] : 'N/A';
    
    const buildingTQCs = auditorData.urgentItems.filter(item => item.type === 'TQC' && item.buildings.includes(fixedBuilding));
    const buildingSurges = auditorData.defectSurges.filter(surge => surge.building === fixedBuilding);
    
    let recommendationHtml = '';
    if (buildingTQCs.length > 0 || buildingSurges.length > 0) {
        recommendationHtml = `
            <div class="recommendation-box">
                <h4 class="recommendation-title">${translations[lang].weeklyRecommendedWorkTitle}</h4>
                <ul class="recommendation-list">
                    ${buildingTQCs.map(tqc => `
                        <li>
                            <strong>TQC '${tqc.name}' ${translations[lang].urgentFocusInspection}</strong>
                            <span>${translations[lang].reason}: ${tqc.detail} (${tqc.buildings.join(', ')})</span>
                        </li>
                    `).join('')}
                    ${buildingSurges.map(surge => `
                        <li>
                            <strong>${surge.defect} ${translations[lang].specialAttention}</strong>
                            <span>${translations[lang].pastCompared} ${surge.increasePercent}% ${translations[lang].surgeIncrease} (${translations[lang].highRiskTQC}: ${surge.problemTQCs.map(t => t.name).join(', ')})</span>
                        </li>
                    `).join('')}
                </ul>
            </div>`;
    } else {
        recommendationHtml = `
            <div class="recommendation-box">
                <h4 class="recommendation-title">${translations[lang].weeklyRecommendedWorkTitle}</h4>
                <p style="color: var(--gray-500);">${translations[lang].noSpecialInstructionsCurrently}</p>
            </div>`;
    }
    
    const body = `
        <div>
            <h4>${auditorData.name} (${auditorData.id})</h4>
            <p class="auditor-meta">
                ${translations[lang].fixedWorkingArea}: ${fixedBuilding}<br>
                ${translations[lang].avgDailyTqcCount}: ${auditorData.avgDailyTqcCount.toFixed(1)}${translations[lang].name}<br>
                ${translations[lang].avgDailyValidation}: ${Math.round(auditorData.avgDailyValidation).toLocaleString()}
            </p>
        </div>
        ${recommendationHtml}
        <div class="grid grid-cols-2" style="gap: 1rem; margin-top: 1.5rem;">
            <div class="chart-container" style="height: 200px;">
                <h5 class="chart-title">${translations[lang].avgDailyValidation} (30${translations[lang].day})</h5>
                <canvas id="auditorValidationChart"></canvas>
            </div>
            <div class="chart-container" style="height: 200px;">
                <h5 class="chart-title">${translations[lang].avgDailyTqcCount} (30${translations[lang].day})</h5>
                <canvas id="auditorTqcChart"></canvas>
            </div>
        </div>
    `;
    
    openModal(`${translations[lang].auditor} ${translations[lang].detailInfo}`, body);
    
    setTimeout(() => renderAuditorDetailCharts(auditorData), 100);
}

/**
 * 어딧터 상세 차트들을 렌더링하는 함수
 */
function renderAuditorDetailCharts(auditorData) {
    if (!auditorData || !auditorData.trends) return;
    
    const { dates, validation, tqcCount } = auditorData.trends;
    
    createLineChart('auditorValidationChart', { 
        labels: dates, 
        datasets: [{ label: translations[state.currentLanguage].validationQty, data: validation, borderColor: '#10b981', tension: 0.4 }] 
    });
    
    createLineChart('auditorTqcChart', { 
        labels: dates, 
        datasets: [{ label: translations[state.currentLanguage].avgDailyTqcCount, data: tqcCount, borderColor: '#3b82f6', tension: 0.4 }]
    });
}

/**
 * 주간 액션 플랜을 표시하는 함수
 */
function populateWeeklyActionPlan(urgentItems, defectSurges) {
    const container = document.getElementById('weeklyActionPlan');
    if (!container) return;
    const lang = state.currentLanguage;
    const { totalReject, totalValidation, tqcData } = state.processedData;
    const totalRejectRate = totalValidation > 0 ? (totalReject / totalValidation * 100) : 0;
    
    const urgentTQCs = urgentItems.filter(i => i.type === 'TQC');
    let improvedRejectRate = totalRejectRate;
    let improvementPercent = 0;
    
    if (urgentTQCs.length > 0) {
        const urgentTotalValidation = urgentTQCs.reduce((sum, item) => sum + (tqcData[item.key]?.totalValidation || 0), 0);
        const urgentTotalReject = urgentTQCs.reduce((sum, item) => sum + (tqcData[item.key]?.totalReject || 0), 0);
        
        const improvedUrgentReject = urgentTotalValidation * (totalRejectRate / 100);
        const rejectReduction = urgentTotalReject - improvedUrgentReject;
        
        if (totalValidation > 0) {
            improvedRejectRate = ((totalReject - rejectReduction) / totalValidation * 100);
            improvementPercent = totalRejectRate > 0 ? ((totalRejectRate - improvedRejectRate) / totalRejectRate * 100) : 0;
        }
    }
    
    const preventiveData = analyzePreventiveActions();
    
    container.innerHTML = `
        <div class="grid grid-cols-2" style="gap: 1rem;">
            <div>
                <h4 class="action-plan-title danger">${translations[lang].emergencyActions}</h4>
                <ul class="action-plan-list">
                    ${urgentTQCs.slice(0, 3).map(tqc => `<li><strong>TQC '${tqc.name}' (${tqc.detail})</strong><span>${translations[lang].building}: ${tqc.buildings.join(', ')} / ${translations[lang].immediateActionRequired}: ${translations[lang].immediateInspection}</span></li>`).join('')}
                    ${defectSurges.slice(0, 2).map(surge => `<li><strong>${surge.defect} ${translations[lang].defectSurgeResponse}</strong><span>${translations[lang].building}: ${surge.building} (${surge.increasePercent}% ↑) / ${translations[lang].highRiskTQC}: ${surge.problemTQCs.map(t => t.name).join(', ')}</span></li>`).join('')}
                </ul>
            </div>
            <div>
                <h4 class="action-plan-title warning">${translations[lang].preventiveActions}</h4>
                <ul class="action-plan-list">
                    ${preventiveData.preventiveTQCs.length > 0 ? `<li><strong>${translations[lang].tqcEducationAction} (${preventiveData.preventiveTQCs.length}${translations[lang].peopleCount})</strong><span>${translations[lang].mainImprovementPoints}: ${preventiveData.mainDefects.join(', ')}</span></li>` : ''}
                    ${preventiveData.newModels.length > 0 ? `<li><strong>${translations[lang].newModelStabilization}</strong><span>${preventiveData.newModels.map(m => `${m.name}(${m.rate}%)`).join(', ')}</span></li>` : ''}
                </ul>
            </div>
        </div>
        <div class="weekly-goal">
            <h4>${translations[lang].weeklyGoal}</h4>
            <div>${translations[lang].overallRejectRateGoal} ${totalRejectRate.toFixed(2)}% → ${improvedRejectRate.toFixed(2)}% (${improvementPercent.toFixed(0)}% ${translations[lang].improvementPercent})</div>
        </div>`;
}

/**
 * 예방 조치 분석을 수행하는 함수
 */
function analyzePreventiveActions() {
    const { tqcData, modelData, rawData } = state.processedData;
    const preventiveTQCs = Object.values(tqcData).filter(tqc => {
        const rate = tqc.totalValidation > 0 ? (tqc.totalReject / tqc.totalValidation * 100) : 0;
        return rate >= 3 && rate < 5 && tqc.totalValidation > 100;
    });

    const mainDefects = [...new Set(preventiveTQCs.flatMap(t => Object.keys(t.defects)))].slice(0, 3);
    
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const modelFirstAppearance = {};
    if (rawData) {
        rawData.forEach(row => {
            const model = row['Model'];
            const date = parseDate(row['Inspection Date']);
            if (model && date && (!modelFirstAppearance[model] || date < modelFirstAppearance[model])) {
                modelFirstAppearance[model] = date;
            }
        });
    }
    
    const newModels = Object.entries(modelFirstAppearance)
        .filter(([model, firstDate]) => firstDate >= sevenDaysAgo && modelData[model])
        .map(([model, firstDate]) => ({
            name: model,
            rate: modelData[model].totalValidation > 0 ? (modelData[model].totalReject / modelData[model].totalValidation * 100).toFixed(1) : 0,
        }));

    return { preventiveTQCs, mainDefects, newModels };
}

