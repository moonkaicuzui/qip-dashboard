import { state } from '../../state.js';
import { translations } from '../../config.js';
import { parseDate, parseDefectTypes, calculateStats, calculateLinearRegression, analyzeTrend, addTrendIndicatorToElement } from './uiUtils.js';
import { createLineChart, createBarChart, createPieChart } from './chartHelpers.js';


/**
 * 모달 열기 함수
 */
export function openModal(title, bodyContent) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = bodyContent;
    document.getElementById('detailModal').classList.add('show');
}

/**
 * 모달 닫기 함수
 */
export function closeModal() {
    document.getElementById('detailModal').classList.remove('show');
    document.getElementById('modalBody').innerHTML = '';
}

/**
 * TQC 상세 정보 표시
 */
export function showTQCDetail(tqcKey) {
    const tqc = state.processedData.tqcData[tqcKey];
    if (!tqc) return;
    const rejectRate = tqc.totalValidation > 0 ? (tqc.totalReject / tqc.totalValidation * 100) : 0;
    const lang = state.currentLanguage;
    let defectListHtml = Object.entries(tqc.defects).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([defect, count]) => `<li>${defect}: ${Math.round(count)}</li>`).join('');
    const body = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h4 style="margin-bottom: 0.5rem;">${tqc.name} (${tqc.id})</h4>
                <div style="font-size: 0.875rem; color: var(--gray-600);">
                    <p style="margin: 0.25rem 0;">${translations[lang].totalInspection}: <strong>${tqc.totalValidation.toLocaleString()}</strong></p>
                    <p style="margin: 0.25rem 0;">${translations[lang].rejectQty}: <strong>${tqc.totalReject.toLocaleString()}</strong></p>
                    <p style="margin: 0.25rem 0;">${translations[lang].rejectRate}: <strong>${rejectRate.toFixed(2)}%</strong></p>
                    <p style="margin: 0.25rem 0;">${translations[lang].workingArea}: <strong>${Array.from(tqc.buildings).join(', ')}</strong></p>
                </div>
            </div>
        </div>
        <div class="tqc-detail-charts">
            <div class="tqc-detail-chart"><h5>${translations[lang].auditorInspectionTrend}</h5><div class="tqc-detail-chart-container"><canvas id="tqcAuditorTrendChart"></canvas></div></div>
            <div class="tqc-detail-chart"><h5>${translations[lang].buildingRejectRate}</h5><div class="tqc-detail-chart-container"><canvas id="tqcBuildingRejectChart"></canvas></div></div>
            <div class="tqc-detail-chart"><h5>${translations[lang].modelRejectRate}</h5><div class="tqc-detail-chart-container"><canvas id="tqcModelRejectChart"></canvas></div></div>
            <div class="tqc-detail-chart"><h5>${translations[lang].top3DefectMissing}</h5><div class="tqc-detail-chart-container"><canvas id="tqcTop3DefectChart"></canvas></div></div>
        </div>
        <div style="margin-top: 1.5rem;">
            <h5 style="margin-bottom: 0.5rem;">${translations[lang].defectTypeBreakdown}</h5>
            <ul style="font-size: 0.875rem; padding-left: 1.25rem; columns: 2;">${defectListHtml}</ul>
        </div>
    `;
    openModal(`${translations[lang].tqcInfo}: ${tqc.name}`, body);
    setTimeout(() => renderTQCDetailCharts(tqcKey), 100);
}

/**
 * TQC 상세 차트 렌더링
 */
function renderTQCDetailCharts(tqcKey) {
    const tqcMissing = state.processedData.tqcMissingDefects[tqcKey];
    if (!tqcMissing) return;

    const dates = Object.keys(state.processedData.dailyData).sort();
    const trendData = dates.map(date => {
        const dayData = state.rawData.filter(row => {
            const rowDate = parseDate(row['Inspection Date']);
            return rowDate && rowDate.toISOString().split('T')[0] === date && `${row['TQC ID']}-${row['TQC Name']}` === tqcKey && row['Inspector ID'];
        });
        const validation = dayData.reduce((sum, r) => sum + (parseInt(r['Validation Qty']) || 0), 0);
        const reject = dayData.reduce((sum, r) => sum + (parseInt(r['Reject Qty']) || 0), 0);
        return validation > 0 ? (reject / validation) * 100 : 0;
    });

    // 선형 추세선 추가
    const trendLine = calculateLinearRegression(trendData);
    const shortLabels = dates.map(date => date.substring(5));
    
    createLineChart('tqcAuditorTrendChart', { 
        labels: shortLabels, 
        datasets: [
            { label: translations[state.currentLanguage].rejectRate + ' (%)', data: trendData, borderColor: '#ef4444' },
            { label: translations[state.currentLanguage].trendLine, data: trendLine, borderColor: '#9ca3af', borderDash: [5, 5], borderWidth: 2, pointRadius: 0 }
        ] 
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
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    font: { size: 9 }
                }
            }
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: { size: 9 },
                    boxWidth: 10
                }
            }
        }
    });

    const buildingData = Object.entries(tqcMissing.buildingBreakdown || {}).map(([building, data]) => ({ name: building, rate: data.validation > 0 ? (data.reject / data.validation * 100) : 0 }));
    createBarChart('tqcBuildingRejectChart', { 
        labels: buildingData.map(d => d.name), 
        datasets: [{ 
            label: translations[state.currentLanguage].rejectRate + ' (%)', 
            data: buildingData.map(d => d.rate.toFixed(2)), 
            backgroundColor: '#f97316' 
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
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    font: { size: 9 }
                }
            }
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: { size: 9 },
                    boxWidth: 10
                }
            }
        }
    });
    
    const modelData = Object.entries(tqcMissing.modelBreakdown || {}).map(([model, data]) => ({ name: model, rate: data.validation > 0 ? (data.reject / data.validation * 100) : 0 })).sort((a,b) => b.rate - a.rate).slice(0, 10);
    createBarChart('tqcModelRejectChart', { 
        labels: modelData.map(d => d.name), 
        datasets: [{ 
            label: translations[state.currentLanguage].rejectRate + ' (%)', 
            data: modelData.map(d => d.rate.toFixed(2)), 
            backgroundColor: '#3b82f6' 
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
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    font: { size: 9 }
                }
            }
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: { size: 9 },
                    boxWidth: 10
                }
            }
        }
    });
    
    const topDefects = Object.entries(tqcMissing.defectBreakdown || {}).sort((a,b) => b[1] - a[1]).slice(0, 3);
    createBarChart('tqcTop3DefectChart', { 
        labels: topDefects.map(d => d[0]), 
        datasets: [{ 
            label: translations[state.currentLanguage].count, 
            data: topDefects.map(d => d[1]), 
            backgroundColor: ['#10b981', '#f59e0b', '#ec4899'] 
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
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    font: { size: 9 }
                }
            }
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: { size: 9 },
                    boxWidth: 10
                }
            }
        }
    });
}

/**
 * TQC 히트맵 상세 정보 표시
 */
export function showTqcHeatmapDetail(tqcKey, defectName) {
    const tqc = state.processedData.tqcData[tqcKey];
    const tqcMissing = state.processedData.tqcMissingDefects[tqcKey];
    if (!tqc || !tqcMissing) return;
    const lang = state.currentLanguage;
    const defectCount = tqcMissing.defectBreakdown[defectName] || 0;
    const missingRate = tqcMissing.totalAuditorInspection > 0 ? (defectCount / tqcMissing.totalAuditorInspection * 100) : 0;
    
    const body = `
        <h4>${tqc.name} - ${defectName}</h4>
        <p><strong>${translations[lang].missingRate}:</strong> ${missingRate.toFixed(2)}%</p>
        <p><strong>${translations[lang].defectsLabel} ${translations[lang].count}:</strong> ${Math.round(defectCount)} / <strong>${translations[lang].totalInspectionField}:</strong> ${tqcMissing.totalAuditorInspection}</p>
        <div class="chart-container" style="height: 200px; margin-top: 1rem;">
            <canvas id="heatmapDetailTrendChart"></canvas>
        </div>
    `;
    openModal(translations[lang].defectDetails, body);

    setTimeout(() => {
        const dates = Object.keys(state.processedData.dailyData).sort().slice(-30);
        const dataPoints = dates.map(date => {
            let count = 0;
            state.rawData.filter(row => {
                const rowDate = parseDate(row['Inspection Date']);
                return rowDate && rowDate.toISOString().split('T')[0] === date && `${row['TQC ID']}-${row['TQC Name']}` === tqcKey && row['Error']?.includes(defectName);
            }).forEach(row => {
                count += (parseInt(row['Reject Qty']) || 0) / (parseDefectTypes(row['Error']).length || 1);
            });
            return count;
        });
        
        // 선형 추세선 추가
        const trendLine = calculateLinearRegression(dataPoints);
        const shortLabels = dates.map(date => date.substring(5));
        
        createLineChart('heatmapDetailTrendChart', { 
            labels: shortLabels, 
            datasets: [
                { label: `${defectName} ${translations[state.currentLanguage].occurrenceCount}`, data: dataPoints, borderColor: '#ef4444' },
                { label: translations[state.currentLanguage].trendLine, data: trendLine, borderColor: '#9ca3af', borderDash: [5, 5], borderWidth: 2, pointRadius: 0 }
            ] 
        }, {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    bottom: 20,
                    top: 10,
                    left: 10,
                    right: 10
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        font: { size: 10 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: { size: 10 },
                        boxWidth: 12
                    }
                }
            }
        });
    }, 100);
}

/**
 * 일반 히트맵 상세 정보 표시
 */
export function showHeatmapDetail(type, itemName, defectName) {
    const lang = state.currentLanguage;
    const { rawData } = state;
    if (!rawData) return;
    const relevantRows = rawData.filter(row => (type === 'building' ? row['Building'] === itemName : row['Model'] === itemName) && row['Error']?.includes(defectName) && (parseInt(row['Reject Qty']) > 0));
    const relatedTqcs = {};
    relevantRows.forEach(row => {
        if(row['TQC ID']) {
            const tqcKey = `[${row['Building']}] ${row['TQC Name']}`;
            relatedTqcs[tqcKey] = (relatedTqcs[tqcKey] || 0) + (parseInt(row['Reject Qty']) || 0) / (parseDefectTypes(row['Error']).length || 1);
        }
    });
    const tqcListHtml = Object.entries(relatedTqcs).sort((a, b) => b[1] - a[1]).map(([tqc, count]) => `<li>${tqc}: ${Math.round(count)}${translations[lang].count}</li>`).join('');
    let body = ``;
    if (type === 'building') {
        const buildingData = state.processedData.buildingData[itemName];
        const defectRate = buildingData.totalValidation > 0 ? ((buildingData.defects[defectName] || 0) / buildingData.totalValidation * 100) : 0;
        body = `<h4>${translations[lang].building}: ${itemName}</h4><p>${translations[lang].defectType}: ${defectName}</p><p>${translations[lang].rejectRate}: ${defectRate.toFixed(2)}%</p><h5>${translations[lang].relatedTqcLabel}:</h5><ul>${tqcListHtml}</ul>`;
    } else if (type === 'model') {
        const modelData = state.processedData.modelData[itemName];
        const defectRate = modelData.totalValidation > 0 ? ((modelData.defects[defectName] || 0) / modelData.totalValidation * 100) : 0;
        body = `<h4>${translations[lang].model}: ${itemName}</h4><p>${translations[lang].defectType}: ${defectName}</p><p>${translations[lang].rejectRate}: ${defectRate.toFixed(2)}%</p><h5>${translations[lang].relatedTqcLabel}:</h5><ul>${tqcListHtml}</ul>`;
    }
    openModal(translations[lang].defectDetails, body);
}

/**
 * 위험도 상세 정보 표시
 */
export function showRiskDetail(type, itemName) {
    const lang = state.currentLanguage;
    const { rawData } = state;
    if (!rawData) return;
    const keyName = type === 'po' ? 'PO No' : type === 'building' ? 'Building' : 'Line';
    const relevantRows = rawData.filter(row => row[keyName] === itemName);
    const validation = relevantRows.reduce((sum, r) => sum + (parseInt(r['Validation Qty']) || 0), 0);
    const reject = relevantRows.reduce((sum, r) => sum + (parseInt(r['Reject Qty']) || 0), 0);
    const rejectRate = validation > 0 ? (reject / validation * 100) : 0;
    const defectCounts = {}, tqcCounts = {}, auditors = new Set();
    relevantRows.forEach(row => {
        if(row['Inspector Name']) auditors.add(row['Inspector Name']);
        if(row['Error'] && parseInt(row['Reject Qty']) > 0) {
            const defects = parseDefectTypes(row['Error']);
            defects.forEach(d => defectCounts[d] = (defectCounts[d] || 0) + (parseInt(row['Reject Qty']) || 0) / defects.length);
        }
        if(row['TQC Name']) {
            tqcCounts[row['TQC Name']] = (tqcCounts[row['TQC Name']] || 0) + 1;
        }
    });
    const defectList = Object.entries(defectCounts).sort((a,b) => b[1] - a[1]).map(([name, count]) => `<li>${name}: ${Math.round(count)}</li>`).join('');
    const tqcList = Object.entries(tqcCounts).sort((a,b) => b[1] - a[1]).map(([name, count]) => `<li>${name} (${count}${translations[lang].count})</li>`).join('');
    const body = `<h4>${itemName}</h4><div>${translations[lang].totalInspectionField}: ${validation}, ${translations[lang].totalReject}: ${reject}, ${translations[lang].rejectRateLabel}: ${rejectRate.toFixed(2)}%</div><p>${translations[lang].auditorsLabel}: ${Array.from(auditors).join(', ')}</p><div><h5>${translations[lang].defectsLabel}</h5><ul>${defectList}</ul></div><div><h5>${translations[lang].relatedTqcLabel}</h5><ul>${tqcList}</ul></div>`;
    openModal(`${translations[lang].detailInfoFor}: ${itemName}`, body);
}

/**
 * TQC 일관성 상세 정보 표시
 */
export function showTqcConsistencyDetail(tqcKey) {
    const tqc = state.processedData.tqcData[tqcKey];
    if (!tqc || !tqc.sustainability) return;
    
    const lang = state.currentLanguage;
    const sus = tqc.sustainability;
    
    const body = `
        <div class="grid grid-cols-3" style="gap: 1rem; margin-bottom: 1.5rem; text-align: center;">
            <div>
                <div class="stat-label">${translations[lang].avgRejectRateColumn}</div>
                <div class="stat-value" style="font-size: 1.5rem">${sus.avg.toFixed(2)}%</div>
            </div>
            <div>
                <div class="stat-label">${translations[lang].fluctuationRangeColumn}</div>
                <div class="stat-value" style="font-size: 1.5rem">±${sus.stdDev.toFixed(2)}%p</div>
            </div>
            <div>
                <div class="stat-label">${translations[lang].consistencyScoreColumn}</div>
                <div class="stat-value" style="font-size: 1.5rem">${sus.volatilityScore.toFixed(1)}${translations[lang].pointsUnit}</div>
            </div>
        </div>
        
        <div class="score-explanation">
            <h5>${translations[lang].consistencyScoreCalculationMethod}</h5>
            <p>${translations[lang].consistencyScoreIndicatesVolatility}</p>
            <div class="score-formula">
                ${translations[lang].scoreFormulaText}<br>
                ${translations[lang].weightLabel}: ${translations[lang].avgRejectRateLessThan3} ${translations[lang].equals2Point0}, ${translations[lang].lessThan7Percent} ${translations[lang].equals1Point5}, ${translations[lang].othersWeight} ${translations[lang].equals1Point0}
            </div>
            <p>${translations[lang].lowerScoreHigherConsistency}</p>
        </div>
        
        <div class="tqc-detail-chart">
            <h5>${translations[lang].dailyRejectTrendChart}</h5>
            <div id="tqcConsistencyTrendIndicator"></div>
            <div class="tqc-detail-chart-container" style="height: 250px;">
                <canvas id="tqcConsistencyTrendChart"></canvas>
            </div>
        </div>
        
        <div class="chart-grid">
            <div class="chart-item">
                <h6>${translations[lang].top3DefectTrends}</h6>
                <div class="chart-container" style="height: 200px;">
                    <canvas id="tqcTop3DefectTrendsChart"></canvas>
                </div>
            </div>
        </div>
    `;
    openModal(`${tqc.name} - ${translations[lang].tqcVolatility}`, body);

    setTimeout(() => {
        const avgLine = {
            label: translations[state.currentLanguage].average,
            data: Array(sus.rejectRates.length).fill(sus.avg),
            borderColor: '#f59e0b',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            type: 'line'
        };
        
        // 추세선 추가
        const trendLine = calculateLinearRegression(sus.rejectRates);
        const trendType = analyzeTrend(trendLine);

        createLineChart('tqcConsistencyTrendChart', {
            labels: Array.from({length: sus.rejectRates.length}, (_, i) => `${translations[lang].day} ${i+1}`),
            datasets: [
                {
                    label: translations[lang].rejectRate,
                    data: sus.rejectRates,
                    borderColor: '#3b82f6',
                    tension: 0.1
                },
                avgLine,
                {
                    label: translations[state.currentLanguage].trendLine,
                    data: trendLine,
                    borderColor: '#9ca3af',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 0,
                    type: 'line'
                }
            ]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    bottom: 20,
                    top: 10,
                    left: 10,
                    right: 10
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        font: { size: 10 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: { size: 10 },
                        boxWidth: 12
                    }
                }
            }
        });
        
        // 추세 표시 추가
        addTrendIndicatorToElement('tqcConsistencyTrendIndicator', trendType, sus.rejectRates);

        // TOP 3 불량 추세 차트 추가
        const top3Defects = Object.entries(tqc.defects)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([defect]) => defect);

        if (top3Defects.length > 0 && tqc.dailyDefects) {
            const dates = Object.keys(state.processedData.dailyData).sort().slice(-30);
            const shortLabels = dates.map(d => d.substring(5));
            const datasets = top3Defects.map((defect, index) => {
                const data = dates.map(date => tqc.dailyDefects[defect]?.[date] || 0);
                const trend = calculateLinearRegression(data);
                
                return [
                    {
                        label: defect,
                        data: data,
                        borderColor: ['#ef4444', '#f59e0b', '#10b981'][index],
                        tension: 0.4
                    },
                    {
                        label: `${defect} ${translations[state.currentLanguage].trendLine}`,
                        data: trend,
                        borderColor: ['#ef4444', '#f59e0b', '#10b981'][index],
                        borderDash: [5, 5],
                        borderWidth: 2,
                        pointRadius: 0
                    }
                ];
            }).flat();

            createLineChart('tqcTop3DefectTrendsChart', {
                labels: shortLabels,
                datasets: datasets
            }, {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        bottom: 20,
                        top: 10,
                        left: 10,
                        right: 10
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45,
                            font: { size: 9 }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: { size: 9 },
                            boxWidth: 10
                        }
                    }
                }
            });
        }
    }, 100);
}

/**
 * 감사관 일관성 상세 정보 표시 (1열 3행 레이아웃)
 */
export function showAuditorConsistencyDetail(auditorKey) {
    const auditor = state.processedData.inspectorData[auditorKey];
    if (!auditor) return;
    const lang = state.currentLanguage;

    // 추세 분석
    const validationTrend = calculateLinearRegression(auditor.trends.validation);
    const validationTrendType = analyzeTrend(validationTrend);
    const tqcTrend = calculateLinearRegression(auditor.trends.tqcCount);
    const tqcTrendType = analyzeTrend(tqcTrend);
    const modelTrend = calculateLinearRegression(auditor.trends.modelCount);
    const modelTrendType = analyzeTrend(modelTrend);

    const body = `
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h4>${auditor.name}</h4>
        </div>
        <div class="grid grid-cols-3" style="gap: 1rem; margin-bottom: 1.5rem; text-align: center;">
             <div>
                <div class="stat-label">${translations[lang].avgDailyValidation}</div>
                <div class="stat-value" style="font-size: 1.5rem">${Math.round(auditor.avgDailyValidation).toLocaleString()}</div>
            </div>
            <div>
                <div class="stat-label">${translations[lang].avgDailyTqcCount}</div>
                <div class="stat-value" style="font-size: 1.5rem">${auditor.avgDailyTqcCount.toFixed(1)}</div>
            </div>
             <div>
                <div class="stat-label">${translations[lang].avgDailyModelCount}</div>
                <div class="stat-value" style="font-size: 1.5rem">${auditor.avgDailyModelCount.toFixed(1)}</div>
            </div>
        </div>
        
        <!-- 차트들을 1열 3행으로 배치 -->
        <div class="chart-grid" style="display: flex; flex-direction: column; gap: 2rem;">
            <div class="chart-item">
                <h6 style="text-align: center; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">${translations[lang].avgDailyValidation}</h6>
                <div id="validationTrendIndicator"></div>
                <div class="chart-container" style="height: 250px; margin-bottom: 1rem;">
                    <canvas id="auditorPopupValidationChart"></canvas>
                </div>
            </div>
            
            <div class="chart-item">
                <h6 style="text-align: center; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">${translations[lang].avgDailyTqcCount}</h6>
                <div id="tqcTrendIndicator"></div>
                <div class="chart-container" style="height: 250px; margin-bottom: 1rem;">
                    <canvas id="auditorPopupTqcChart"></canvas>
                </div>
            </div>
            
            <div class="chart-item">
                <h6 style="text-align: center; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">${translations[lang].avgDailyModelCount}</h6>
                <div id="modelTrendIndicator"></div>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="auditorPopupModelChart"></canvas>
                </div>
            </div>
        </div>
    `;
    openModal(`${auditor.name} - ${translations[lang].auditorActivityConsistency}`, body);
    
    setTimeout(() => {
        const shortLabels = auditor.trends.dates.map(date => date.substring(5));
        
        // 일평균 검증 수량 차트 (추세선 포함)
        createLineChart('auditorPopupValidationChart', {
            labels: shortLabels,
            datasets: [{
                label: translations[lang].validationQty,
                data: auditor.trends.validation,
                borderColor: '#3b82f6',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
            }, {
                label: translations[state.currentLanguage].trendLine,
                data: validationTrend,
                borderColor: '#9ca3af',
                borderDash: [5, 5],
                borderWidth: 2,
                pointRadius: 0,
                fill: false
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    bottom: 20,
                    top: 10,
                    left: 10,
                    right: 10
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        font: { size: 11 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: { size: 11 },
                        boxWidth: 12
                    }
                }
            }
        });
        
        // 일평균 TQC 수 차트
        createLineChart('auditorPopupTqcChart', {
            labels: shortLabels,
            datasets: [{
                label: translations[lang].avgDailyTqcCount,
                data: auditor.trends.tqcCount,
                borderColor: '#10b981',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(16, 185, 129, 0.1)'
            }, {
                label: translations[state.currentLanguage].trendLine,
                data: tqcTrend,
                borderColor: '#9ca3af',
                borderDash: [5, 5],
                borderWidth: 2,
                pointRadius: 0,
                fill: false
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    bottom: 20,
                    top: 10,
                    left: 10,
                    right: 10
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        font: { size: 11 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: { size: 11 },
                        boxWidth: 12
                    }
                }
            }
        });
        
        // 일평균 모델 수 차트
        createLineChart('auditorPopupModelChart', {
            labels: shortLabels,
            datasets: [{
                label: translations[lang].avgDailyModelCount,
                data: auditor.trends.modelCount,
                borderColor: '#f59e0b',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(245, 158, 11, 0.1)'
            }, {
                label: translations[state.currentLanguage].trendLine,
                data: modelTrend,
                borderColor: '#9ca3af',
                borderDash: [5, 5],
                borderWidth: 2,
                pointRadius: 0,
                fill: false
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    bottom: 20,
                    top: 10,
                    left: 10,
                    right: 10
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        font: { size: 11 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: { size: 11 },
                        boxWidth: 12
                    }
                }
            }
        });
        
        // 추세 표시 추가
        addTrendIndicatorToElement('validationTrendIndicator', validationTrendType, auditor.trends.validation);
        addTrendIndicatorToElement('tqcTrendIndicator', tqcTrendType, auditor.trends.tqcCount);
        addTrendIndicatorToElement('modelTrendIndicator', modelTrendType, auditor.trends.modelCount);
    }, 100);
}

/**
 * 빌딩 상세 팝업 표시
 */
export function showBuildingDetailPopup(buildingName) {
    let tqcsInBuilding = Object.values(state.processedData.tqcData)
        .filter(t => t.buildings.has(buildingName) && t.sustainability);
    
    const lang = state.currentLanguage;
    
    const renderTable = () => {
        const tbody = document.getElementById('building-tqc-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = tqcsInBuilding.map(tqc => {
            const sus = tqc.sustainability;
            const q = sus.quartiles;
            return `
                <tr>
                    <td>${tqc.name}</td>
                    <td>${tqc.totalValidation.toLocaleString()}</td>
                    <td>${sus.avg.toFixed(2)}%</td>
                    <td>${sus.volatilityScore.toFixed(1)}</td>
                    <td>±${sus.stdDev.toFixed(2)}%p</td>
                    <td>
                        <div class="quartile-visual" style="position: relative; display: inline-block; width: 150px; height: 20px;">
                            <div style="position: absolute; left: 0; right: 0; top: 9px; height: 2px; background: #e5e7eb;"></div>
                            <div style="position: absolute; left: ${((q.q1 - q.min) / (q.max - q.min) * 100)}%; 
                                        right: ${100 - ((q.q3 - q.min) / (q.max - q.min) * 100)}%; 
                                        top: 5px; height: 10px; background: rgba(59, 130, 246, 0.3); 
                                        border: 1px solid #3b82f6;"></div>
                            <div style="position: absolute; left: ${((q.median - q.min) / (q.max - q.min) * 100)}%; 
                                        top: 5px; width: 2px; height: 10px; background: #ef4444;"
                                 title="${translations[lang].redLineIsMedian}: ${q.median.toFixed(1)}%"></div>
                            <div style="position: absolute; left: ${((sus.avg - q.min) / (q.max - q.min) * 100)}%; 
                                        top: 5px; width: 2px; height: 10px; background: #10b981;"
                                 title="${translations[lang].greenLineIsAverage}: ${sus.avg.toFixed(1)}%"></div>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    };
    
    const sortTable = (colIndex, isAsc) => {
        tqcsInBuilding.sort((tqc_a, tqc_b) => {
            let val_a, val_b;
            switch(colIndex) {
                case 0: val_a = tqc_a.name; val_b = tqc_b.name; break;
                case 1: val_a = tqc_a.totalValidation; val_b = tqc_b.totalValidation; break;
                case 2: val_a = tqc_a.sustainability.avg; val_b = tqc_b.sustainability.avg; break;
                case 3: val_a = tqc_a.sustainability.volatilityScore; val_b = tqc_b.sustainability.volatilityScore; break;
                case 4: val_a = tqc_a.sustainability.stdDev; val_b = tqc_b.sustainability.stdDev; break;
                case 5: val_a = tqc_a.sustainability.quartiles.median; val_b = tqc_b.sustainability.quartiles.median; break;
                default: val_a = 0; val_b = 0; break;
            }

            if (typeof val_a === 'string') {
                return val_a.localeCompare(val_b) * (isAsc ? 1 : -1);
            }
            return isAsc ? val_a - val_b : val_b - val_a;
        });
        
        renderTable();
    };
    
    tqcsInBuilding.sort((a,b) => b.sustainability.volatilityScore - a.sustainability.volatilityScore);

    const modalBody = `
        <p style="margin-bottom: 1rem;"><strong>'${buildingName}'</strong> ${translations[lang].detailedConsistencyDataForTqcs} ${translations[lang].clickColumnNamesToSort}</p>
        <div class="table-container">

            <table class="data-table">
                <thead>
                    <tr id="building-tqc-thead">
                        <th data-col="0" class="sortable-header" style="width: 25%; min-width: 150px;">${translations[lang].tqcNameColumn}</th>
                        <th data-col="1" class="sortable-header" style="width: 12%;">${translations[lang].totalValidationQtyColumn}</th>
                        <th data-col="2" class="sortable-header" style="width: 12%;">${translations[lang].avgRejectRateColumn}</th>
                        <th data-col="3" class="sortable-header sort-desc" style="width: 12%;">${translations[lang].consistencyScoreColumn}</th>
                        <th data-col="4" class="sortable-header" style="width: 12%;">${translations[lang].fluctuationRangeColumn}</th>
                        <th data-col="5" class="sortable-header" style="width: 27%;">${translations[lang].quartileDistributionColumn}</th>
                    </tr>
                </thead>

                <tbody id="building-tqc-tbody">
                </tbody>
            </table>
        </div>
        <div class="quartile-explanation" style="margin-top: 1rem; padding: 1rem; background-color: var(--gray-50); border-radius: 0.5rem;">
            <h5 style="margin-bottom: 0.5rem;">${translations[lang].howToReadQuartileDistribution}</h5>
            <p style="font-size: 0.875rem; color: var(--gray-700); margin-bottom: 0.5rem;">
                ${translations[lang].boxLeftEnd} <strong>${translations[lang].isQ1Lower25}</strong> ${translations[lang].boxRightEnd} <strong>${translations[lang].isQ3Upper25}</strong><br>
                <span style="color: #ef4444;">${translations[lang].redLineIsMedian}</span> <strong>${translations[lang].centralValueOfData}</strong><br>
                <span style="color: #10b981;">${translations[lang].greenLineIsAverage}</span> <strong>${translations[lang].arithmeticMeanOfAllValues}</strong>
            </p>
            <p style="font-size: 0.875rem; color: var(--gray-600);">
                ${translations[lang].medianAvgDifferenceIndicatesSkew}
            </p>
        </div>
    `;

    openModal(`${buildingName} ${translations[lang].consistencyAnalysisFor}`, modalBody);
    renderTable();

    const thead = document.getElementById('building-tqc-thead');
    if (thead) {
        thead.addEventListener('click', e => {
            const th = e.target.closest('th');
            if (!th || !th.classList.contains('sortable-header')) return;

            const colIndex = parseInt(th.dataset.col, 10);
            const isAsc = th.classList.contains('sort-asc');
            
            th.parentElement.querySelectorAll('th').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            th.classList.toggle('sort-asc', !isAsc);
            th.classList.toggle('sort-desc', isAsc);

            sortTable(colIndex, !isAsc);
        });
    }
}

/**
 * 모델 일관성 상세 정보 표시
 */
export function showModelConsistencyDetail(modelName) {
    const lang = state.currentLanguage;
    const modelData = state.processedData.modelData[modelName];
    if (!modelData) return;

    const defectDaily = {};
    state.rawData.filter(row => row['Model'] === modelName).forEach(row => {
        const defects = parseDefectTypes(row.Error);
        const date = parseDate(row['Inspection Date']);
        if (defects.length === 0 || !date) return;

        const dateStr = date.toISOString().split('T')[0];
        const qtyPerDefect = (parseInt(row['Reject Qty']) || 0) / defects.length;

        defects.forEach(defect => {
            if (!defectDaily[defect]) defectDaily[defect] = {};
            if (!defectDaily[defect][dateStr]) defectDaily[defect][dateStr] = 0;
            defectDaily[defect][dateStr] += qtyPerDefect;
        });
    });

    const defectVolatility = Object.entries(defectDaily).map(([defect, dailyData]) => {
        const dailyCounts = Object.values(dailyData);
        if (dailyCounts.length < 2) return null;
        const stats = calculateStats(dailyCounts);
        return {
            defect,
            avg: stats.avg,
            stdDev: stats.stdDev,
            score: stats.avg > 0 ? (stats.stdDev / stats.avg * 100) : 0
        };
    }).filter(Boolean).sort((a,b) => b.score - a.score);

    const body = `
        <p style="margin-bottom: 1rem;"><strong>'${modelName}'</strong> ${translations[lang].defectTypeConsistencyScores}</p>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>${translations[lang].defectType}</th>
                        <th>${translations[lang].avgOccurrenceCountColumn}</th>
                        <th>${translations[lang].occurrenceFluctuationRangeColumn}</th>
                        <th>${translations[lang].consistencyScoreColumn}</th>
                    </tr>
                </thead>
                <tbody>
                    ${defectVolatility.map(d => `
                        <tr>
                            <td>${d.defect}</td>
                            <td>${d.avg.toFixed(1)}</td>
                            <td>±${d.stdDev.toFixed(1)}</td>
                            <td>${d.score.toFixed(1)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    openModal(`${modelName} - ${translations[lang].defectTypeConsistency}`, body);
}