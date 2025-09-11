import { state } from '../../state.js';
import { translations } from '../../config.js';
import { parseDefectTypes } from '../helpers/uiUtils.js';
import { createChart } from '../helpers/chartHelpers.js';

/**
 * 위험도 분석 탭의 모든 컨텐츠를 업데이트하는 메인 함수
 */
export function updateRiskAnalysis() {
    populateHighRiskLists();
    updateRiskMatrix();
}

/**
 * 고위험 PO, 빌딩, 라인 리스트를 생성하는 함수
 */
function populateHighRiskLists() {
    const { poData, buildingData, lineData } = state.processedData;
    const { rawData } = state;
    const lang = state.currentLanguage;

    const createRiskList = (data, type, containerId, keyName) => {
        const container = document.getElementById(containerId);
        if (!container || !rawData) return;
        
        const topItems = Object.entries(data)
            .map(([name, stats]) => ({
                name,
                rejectRate: stats.totalValidation > 0 ? (stats.totalReject / stats.totalValidation * 100) : 0,
                totalValidation: stats.totalValidation,
            }))
            .filter(item => item.totalValidation > 30)
            .sort((a, b) => b.rejectRate - a.rejectRate)
            .slice(0, 8);

        container.innerHTML = topItems.map(item => {
            const auditors = new Set();
            rawData.filter(row => row[keyName] === item.name && row['Inspector Name']).forEach(row => auditors.add(row['Inspector Name']));
            return `
                <div class="risk-item" data-type="${type}" data-name="${item.name}">
                    <div>
                        <span class="item-name">${item.name}</span>
                        <span class="item-detail">${translations[lang].auditor}: ${Array.from(auditors).slice(0,2).join(', ')}</span>
                    </div>
                    <span class="badge ${item.rejectRate > 10 ? 'badge-danger' : 'badge-warning'}">${item.rejectRate.toFixed(1)}%</span>
                </div>`;
        }).join('');
    };

    createRiskList(poData, 'po', 'highRiskPOs', 'PO No');
    createRiskList(buildingData, 'building', 'highRiskBuildings', 'Building');
    createRiskList(lineData, 'line', 'highRiskLines', 'Line');
}

/**
 * 위험도 예측 매트릭스 차트를 업데이트하는 함수
 */
function updateRiskMatrix() {
    const { tqcData, poData } = state.processedData;
    const { rawData } = state;
    if (!rawData) return;

    const topTQCs = Object.values(tqcData).sort((a,b) => b.totalValidation - a.totalValidation).slice(0,10).map(t => t.name);
    const topPOs = Object.keys(poData).sort((a,b) => poData[b].totalValidation - poData[a].totalValidation).slice(0,10);

    const matrixData = [];
    topTQCs.forEach(tqcName => {
        topPOs.forEach(po => {
            const relevantRows = rawData.filter(row => row['TQC Name'] === tqcName && row['PO No'] === po);
            if (relevantRows.length > 0) {
                const validation = relevantRows.reduce((sum, r) => sum + (parseInt(r['Validation Qty']) || 0), 0);
                const reject = relevantRows.reduce((sum, r) => sum + (parseInt(r['Reject Qty']) || 0), 0);
                if (validation > 0) {
                    const auditor = relevantRows[0]['Inspector Name'] || 'N/A';
                    const defectBreakdown = {};
                    relevantRows.forEach(row => {
                        if (row['Error'] && parseInt(row['Reject Qty']) > 0) {
                            const defects = parseDefectTypes(row['Error']);
                            const qtyPerDefect = (parseInt(row['Reject Qty']) || 0) / defects.length;
                            defects.forEach(d => {
                                defectBreakdown[d] = (defectBreakdown[d] || 0) + qtyPerDefect;
                            });
                        }
                    });
                    matrixData.push({
                        x: po,
                        y: tqcName,
                        v: (reject / validation) * 100,
                        r: Math.sqrt(validation) / 2,
                        auditor, validation, reject, defectBreakdown
                    });
                }
            }
        });
    });

    createChart('riskMatrixChart', 'bubble', {
        datasets: [{
            label: translations[state.currentLanguage].riskScore,
            data: matrixData,
            backgroundColor: matrixData.map(d => d.v > 10 ? '#ef4444' : d.v > 5 ? '#f97316' : '#10b981')
        }]
    }, {
        responsive: true, 
        maintainAspectRatio: false,
        scales: {
            y: { 
                type: 'category', 
                labels: topTQCs, 
                title: { display: true, text: 'TQC' } 
            },
            x: { 
                type: 'category', 
                labels: topPOs, 
                title: { display: true, text: 'PO Number' } 
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const dataPoint = context.raw;
                        const lang = state.currentLanguage;
                        const tooltipLines = [
                            `${translations[lang].riskScore || translations[lang].riskScore}: ${dataPoint.v.toFixed(1)}%`,
                            `${translations[lang].auditor}: ${dataPoint.auditor}`,
                            `${translations[lang].validationQty}: ${dataPoint.validation}`,
                            `${translations[lang].rejectQty}: ${dataPoint.reject}`,
                            '---'
                        ];
                        const defectBreakdown = Object.entries(dataPoint.defectBreakdown)
                            .sort((a, b) => b[1] - a[1]);
                        defectBreakdown.forEach(([defect, count]) => {
                            tooltipLines.push(`${defect}: ${Math.round(count)}`);
                        });
                        return tooltipLines;
                    }
                }
            }
        }
    });
}

