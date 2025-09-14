import { state } from '../../state.js';
import { translations } from '../../config.js';
import { createLineChart, createBarChart } from '../helpers/chartHelpers.js';
import { showTqcConsistencyDetail, showAuditorConsistencyDetail, showBuildingDetailPopup, showModelConsistencyDetail } from '../helpers/modalHelpers.js';


/**
 * 지속성 탭의 모든 컨텐츠를 업데이트하는 메인 함수
 */
export function updateSustainabilityAnalysis() {
    const container = document.getElementById('sustainability-panel');
    if (!container) return;
    const lang = state.currentLanguage;

    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title" data-lang="tqcVolatility">${translations[lang].tqcVolatility}</h3>
                <p class="card-subtitle">${translations[lang].tqcVolatilitySubtitle}</p>
            </div>
            <div class="filter-section" style="margin-bottom: 1rem; padding: 0.5rem;">
                <div class="filter-group">
                    <span class="filter-label" data-lang="filterBuilding">${translations[lang].filterBuilding}</span>
                    <select class="filter-select" id="sustainabilityTqcBuildingFilter"></select>
                </div>
            </div>
            <div class="info-box" style="background: #f0f9ff; border: 1px solid #0284c7; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                <h5 style="margin-top: 0; color: #0c4a6e;">📊 일관성 점수 계산 방법</h5>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>일관성 점수 = (표준편차 ÷ 평균) × 100 ÷ 가중치</strong><br>
                    • 낮은 점수(0-25): 안정적인 품질 - 일정한 불량률 유지<br>
                    • 중간 점수(25-50): 주의 필요 - 변동성 증가 추세<br>
                    • 높은 점수(50-100): 고위험 - 품질 불안정, 즉각 조치 필요
                </p>
            </div>
            <div id="tqc-consistency-container" class="table-container"></div>
        </div>
        <div class="card">
             <div class="card-header">
                <h3 class="card-title" data-lang="auditorActivityConsistency">${translations[lang].auditorActivityConsistency}</h3>
                 <p class="card-subtitle">${translations[lang].auditorActivitySubtitle}</p>
            </div>
            <div class="info-box" style="background: #f0fdf4; border: 1px solid #16a34a; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                <h5 style="margin-top: 0; color: #14532d;">📈 일평균 검증 수량 계산 로직</h5>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>일평균 = 총 검증 수량 ÷ 활동 일수 (최근 30일 기준)</strong><br>
                    • 일평균 검증 수량: 어딧터가 하루에 검사하는 평균 제품 수<br>
                    • 일평균 TQC 수: 하루에 담당하는 평균 검사자 수<br>
                    • 일평균 모델 수: 하루에 검사하는 평균 제품 모델 종류<br>
                    • 추세선: 이동평균으로 활동 패턴 변화 시각화
                </p>
            </div>
            <div id="auditor-consistency-container" class="grid grid-cols-1" style="gap: 1.5rem;"></div>
        </div>
        <div class="card">
            <div class="card-header">
                <h3 class="card-title" data-lang="buildingPerformanceConsistency">${translations[lang].buildingPerformanceConsistency}</h3>
                <p class="card-subtitle">${translations[lang].buildingPerformanceSubtitle}</p>
            </div>
            <div class="chart-container" style="height: 350px;"><canvas id="buildingVolatilityChart"></canvas></div>
            <div id="building-interpretation" class="interpretation-guide"></div>
        </div>
        <div class="card">
            <div class="card-header">
                <h3 class="card-title" data-lang="modelQualityConsistency">${translations[lang].modelQualityConsistency}</h3>
                <p class="card-subtitle">${translations[lang].modelQualitySubtitle}</p>
            </div>
            <div class="chart-container" style="height: 350px;"><canvas id="modelVolatilityChart"></canvas></div>
            <div id="model-interpretation" class="interpretation-guide"></div>
        </div>
    `;

    updateSustainabilityFilterOptions();
    
    // 필터 이벤트 리스너 추가
    const sustainabilityFilter = document.getElementById('sustainabilityTqcBuildingFilter');
    if (sustainabilityFilter) {
        sustainabilityFilter.addEventListener('change', () => {
            renderTqcConsistencyTable();
        });
    }
    
    renderTqcConsistencyTable();
    renderAuditorConsistencyCards();
    renderBuildingVolatilityChart();
    renderModelVolatilityChart();
}

/**
 * 지속성 탭의 필터 옵션을 업데이트하는 함수
 */
export function updateSustainabilityFilterOptions() {
    const { buildings } = state.processedData;
    const lang = state.currentLanguage;
    const allOption = `<option value="ALL">${translations[lang].all}</option>`;
    
    const sustainabilityFilter = document.getElementById('sustainabilityTqcBuildingFilter');
    if (sustainabilityFilter) {
        const currentValue = sustainabilityFilter.value;
        sustainabilityFilter.innerHTML = allOption + buildings.map(opt => `<option value="${opt}">${opt}</option>`).join('');
        sustainabilityFilter.value = currentValue && buildings.includes(currentValue) ? currentValue : "ALL";
    }
}

/**
 * TQC 일관성 테이블을 렌더링하는 함수
 */
function renderTqcConsistencyTable() {
    const container = document.getElementById('tqc-consistency-container');
    const buildingFilter = document.getElementById('sustainabilityTqcBuildingFilter')?.value || 'ALL';
    if (!container) return;
    const lang = state.currentLanguage;

    let tqcs = Object.values(state.processedData.tqcData)
        .filter(t => t.sustainability && t.sustainability.rejectRates.length > 1);

    if (buildingFilter !== 'ALL') {
        tqcs = tqcs.filter(t => t.buildings.has(buildingFilter));
    }

    tqcs.sort((a, b) => b.sustainability.volatilityScore - a.sustainability.volatilityScore);
    
    const top10Tqcs = tqcs.slice(0, 10);

    const getStatusBadge = (category) => {
        if (category === '고위험') return `<span class="badge badge-danger">${translations[lang].emergency}</span>`;
        if (category === '관심') return `<span class="badge badge-warning">${translations[lang].warning}</span>`;
        return `<span class="badge badge-success">${translations[lang].normal}</span>`;
    };

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>TQC</th>
                    <th>${translations[lang].avgRejectRateColumn}</th>
                    <th data-lang="fluctuationRange">${translations[lang].fluctuationRangeColumn}</th>
                    <th data-lang="consistencyScore">${translations[lang].consistencyScoreColumn}</th>
                    <th data-lang="status">${translations[lang].status}</th>
                </tr>
            </thead>
            <tbody>
                ${top10Tqcs.map(tqc => `
                    <tr class="clickable-row" data-type="tqc" data-key="${tqc.id}-${tqc.name}">
                        <td>${tqc.name}</td>
                        <td>${tqc.sustainability.avg.toFixed(2)}%</td>
                        <td>±${tqc.sustainability.stdDev.toFixed(2)}%p</td>
                        <td>${tqc.sustainability.volatilityScore.toFixed(1)}${translations[lang].pointsUnit}</td>
                        <td>${getStatusBadge(tqc.sustainability.volatilityCategory)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.querySelectorAll('.clickable-row[data-type="tqc"]').forEach(row => {
        row.addEventListener('click', (e) => showTqcConsistencyDetail(e.currentTarget.dataset.key));
    });
}

/**
 * 어딧터 일관성 카드들을 렌더링하는 함수
 */
function renderAuditorConsistencyCards() {
    const container = document.getElementById('auditor-consistency-container');
    if (!container) return;
    const lang = state.currentLanguage;

    const allDates = Object.keys(state.processedData.dailyData).sort();
    const lastDateStr = allDates[allDates.length - 1];
    if (!lastDateStr) return;
    
    const lastDate = new Date(lastDateStr);
    const thirtyDaysAgo = new Date(lastDate);
    thirtyDaysAgo.setDate(lastDate.getDate() - 30);
    
    const auditors = Object.values(state.processedData.inspectorData)
        .filter(a => {
            if (!a.trends || a.trends.dates.length === 0) return false;
            const auditorLastDate = new Date(a.trends.dates[a.trends.dates.length - 1]);
            return auditorLastDate >= thirtyDaysAgo;
        });

    container.innerHTML = auditors.map(auditor => `
        <div class="auditor-card clickable-row" data-type="auditor" data-key="${auditor.id}-${auditor.name}">
            <h5>${auditor.name}</h5>
            <div class="auditor-metrics">
                <div><span data-lang="avgDailyValidation">${translations[lang].avgDailyValidation}</span><strong>${Math.round(auditor.avgDailyValidation)}</strong></div>
                <div><span data-lang="avgDailyTqcCount">${translations[lang].avgDailyTqcCount}</span><strong>${auditor.avgDailyTqcCount.toFixed(1)}</strong></div>
                <div><span data-lang="avgDailyModelCount">${translations[lang].avgDailyModelCount}</span><strong>${auditor.avgDailyModelCount.toFixed(1)}</strong></div>
            </div>
            <div class="mini-chart-container">
                <h6 class="mini-chart-title">${translations[lang].dailyValidationQty} ${translations[lang].dailyRejectTrendChart}</h6>
                <canvas id="auditor-chart-${auditor.id}"></canvas>
            </div>
        </div>
    `).join('');

    auditors.forEach(auditor => {
        const canvas = document.getElementById(`auditor-chart-${auditor.id}`);
        if (!canvas) return;
        
        const avg = auditor.trends.validation.reduce((a, b) => a + b, 0) / auditor.trends.validation.length;
        const yAxisMax = auditor.trends.yAxisMax.validation;

        createLineChart(canvas.id, {
            labels: auditor.trends.dates,
            datasets: [{
                label: translations[lang].validationQty,
                data: auditor.trends.validation,
                borderColor: '#3b82f6',
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.4
            }, {
                label: translations[lang].average,
                data: Array(auditor.trends.dates.length).fill(avg),
                borderColor: '#9ca3af',
                borderWidth: 1,
                borderDash: [5,5],
                pointRadius: 0,
            }]
        }, {
            plugins: { legend: { display: false } },
            scales: { 
                x: { display: false }, 
                y: { display: false, suggestedMax: yAxisMax } 
            }
        });
    });

    container.querySelectorAll('.clickable-row[data-type="auditor"]').forEach(row => {
        row.addEventListener('click', (e) => showAuditorConsistencyDetail(e.currentTarget.dataset.key));
    });
}

/**
 * 빌딩 변동성 차트를 렌더링하는 함수
 */
function renderBuildingVolatilityChart() {
    const buildings = Object.entries(state.processedData.buildingData)
        .filter(([, data]) => data.sustainability && data.sustainability.rejectRates.length > 1)
        .sort((a, b) => b[1].sustainability.volatilityScore - a[1].sustainability.volatilityScore);

    if (buildings.length === 0) return;
    
    const labels = buildings.map(([name]) => name);
    const data = buildings.map(([, bData]) => bData.sustainability.volatilityScore);
    const overallAvg = data.length > 0 ? data.reduce((sum, val) => sum + val, 0) / data.length : 0;

    const chartData = {
        labels: labels,
        datasets: [{
            label: translations[state.currentLanguage].consistencyScore,
            data: data,
            backgroundColor: data.map(score => score > 50 ? '#ef4444' : score > 25 ? '#f59e0b' : '#10b981'),
        }, {
            type: 'line',
            label: translations[state.currentLanguage].overallAverage,
            data: Array(data.length).fill(overallAvg),
            borderColor: '#4b5563',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
        }]
    };
    
    const canvas = document.getElementById('buildingVolatilityChart');
    if (!canvas) return;
    createBarChart(canvas.id, chartData);
    renderInterpretationGuide('building-interpretation', buildings[0], translations[state.currentLanguage].building);
    
    canvas.onclick = (e) => {
        const activePoints = state.charts[canvas.id]?.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
        if (activePoints && activePoints.length) {
            const buildingName = labels[activePoints[0].index];
            showBuildingDetailPopup(buildingName);
        }
    };
}

/**
 * 모델 변동성 차트를 렌더링하는 함수
 */
function renderModelVolatilityChart() {
    const models = Object.entries(state.processedData.modelData)
        .filter(([, data]) => data.sustainability && data.sustainability.rejectRates.length > 1)
        .sort((a, b) => b[1].sustainability.volatilityScore - a[1].sustainability.volatilityScore);
        
    if (models.length === 0) return;

    const topModels = models.slice(0, 15);
    const labels = topModels.map(([name]) => name);
    const data = topModels.map(([, mData]) => mData.sustainability.volatilityScore);
    const overallAvg = data.length > 0 ? data.reduce((sum, val) => sum + val, 0) / data.length : 0;

    const canvas = document.getElementById('modelVolatilityChart');
    if (!canvas) return;

    createBarChart(canvas.id, {
        labels,
        datasets: [{
            label: translations[state.currentLanguage].consistencyScore,
            data: data,
            backgroundColor: data.map(score => score > 50 ? '#ef4444' : score > 25 ? '#f59e0b' : '#10b981'),
        }, {
            type: 'line',
            label: translations[state.currentLanguage].overallAverage,
            data: Array(data.length).fill(overallAvg),
            borderColor: '#4b5563',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
        }]
    });
    renderInterpretationGuide('model-interpretation', models[0], translations[state.currentLanguage].model);

    canvas.onclick = (e) => {
        const activePoints = state.charts[canvas.id]?.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
        if (activePoints && activePoints.length) {
            const modelName = labels[activePoints[0].index];
            showModelConsistencyDetail(modelName);
        }
    };
}

/**
 * 해석 가이드를 렌더링하는 함수
 */
function renderInterpretationGuide(elementId, highestItem, itemType) {
    const container = document.getElementById(elementId);
    if (!container || !highestItem) return;

    const [name, data] = highestItem;
    const score = data.sustainability.volatilityScore;
    const avg = data.sustainability.avg;
    const stdDev = data.sustainability.stdDev;
    const lang = state.currentLanguage;

    container.innerHTML = `
        <h5 class="guide-title">${translations[lang].evaluationGuide}</h5>
        <p class="guide-text">
            ${translations[lang].currentMostVolatile} ${itemType}${translations[lang].relatedToThis} <strong>'${name}'</strong>${translations[lang].andRelatedTqcLineProcess}, ${translations[lang].consistencyScorePoints} <strong>${score.toFixed(1)}${translations[lang].pointsUnit}</strong>${translations[lang].shouldInspectCloselyToIdentify} 
            ${translations[lang].avgRejectRateBaseline} ${avg.toFixed(1)}%${translations[lang].asBaselineDailyDeviation} ±${stdDev.toFixed(1)}%p ${translations[lang].levelIndicator}${translations[lang].levelShowingUnstableQuality}
        </p>
        <p class="guide-action">
            <strong>${translations[lang].actionSuggestion}</strong> ${translations[lang].relatedToThis} ${itemType}${translations[lang].andRelatedTqcLineProcess}${translations[lang].shouldInspectCloselyToIdentify}${translations[lang].improveCauseOfVolatility}
        </p>
    `;
}

