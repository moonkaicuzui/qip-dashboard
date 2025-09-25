import { state } from '../../state.js';
import { translations } from '../../config.js';
import { createBarChart, createLineChart, createDoughnutChart } from '../helpers/chartHelpers.js';

/**
 * Management Insights Tab - Executive-level dashboard for quality department managers
 * Provides KPIs, rankings, trends, and actionable recommendations
 */
export function updateManagementInsights() {
    const container = document.getElementById('management-panel');
    if (!container) return;
    const lang = state.currentLanguage;

    // Generate executive KPIs
    const kpis = calculateExecutiveKPIs();
    const rankings = generatePerformanceRankings();
    const trends = analyzeQualityTrends();
    const recommendations = generateActionableRecommendations();

    container.innerHTML = `
        <!-- Executive KPI Dashboard -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">🎯 핵심 성과 지표 (Executive KPIs)</h3>
                <p class="card-subtitle">실시간 품질 관리 현황 및 목표 달성도</p>
            </div>
            <div class="kpi-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; padding: 1rem;">
                ${renderKPICards(kpis)}
            </div>
        </div>

        <!-- Performance Rankings -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">🏆 성과 순위 분석</h3>
                <p class="card-subtitle">TQC, 어딧터, 건물별 품질 성과 순위</p>
            </div>
            <div class="grid grid-cols-3" style="gap: 1rem;">
                <div class="ranking-section">
                    <h4 style="text-align: center; margin-bottom: 1rem;">우수 TQC Top 5</h4>
                    ${renderRankingList(rankings.topTQCs, 'tqc')}
                </div>
                <div class="ranking-section">
                    <h4 style="text-align: center; margin-bottom: 1rem;">우수 어딧터 Top 5</h4>
                    ${renderRankingList(rankings.topAuditors, 'auditor')}
                </div>
                <div class="ranking-section">
                    <h4 style="text-align: center; margin-bottom: 1rem;">개선 필요 TQC</h4>
                    ${renderRankingList(rankings.bottomTQCs, 'tqc', true)}
                </div>
            </div>
        </div>

        <!-- Quality Trend Analysis -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📈 품질 추세 분석</h3>
                <p class="card-subtitle">주요 지표의 시간별 변화 추이</p>
            </div>
            <div class="grid grid-cols-2" style="gap: 1rem;">
                <div class="chart-container" style="height: 300px;">
                    <canvas id="rejectRateTrendChart"></canvas>
                </div>
                <div class="chart-container" style="height: 300px;">
                    <canvas id="validationVolumeTrendChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Resource Allocation Insights -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 자원 배치 현황</h3>
                <p class="card-subtitle">검사 인력 및 업무량 분포</p>
            </div>
            <div class="grid grid-cols-2" style="gap: 1rem;">
                <div class="chart-container" style="height: 300px;">
                    <canvas id="workloadDistributionChart"></canvas>
                </div>
                <div class="chart-container" style="height: 300px;">
                    <canvas id="inspectorEfficiencyChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Actionable Recommendations -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">💡 실행 가능한 권장 사항</h3>
                <p class="card-subtitle">데이터 기반 개선 제안</p>
            </div>
            <div class="recommendations-container" style="padding: 1rem;">
                ${renderRecommendations(recommendations)}
            </div>
        </div>

        <!-- Risk Alert Dashboard -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">⚠️ 위험 경보 대시보드</h3>
                <p class="card-subtitle">즉각적인 주의가 필요한 영역</p>
            </div>
            <div class="alert-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; padding: 1rem;">
                ${renderRiskAlerts()}
            </div>
        </div>
    `;

    // Render charts after DOM is ready
    setTimeout(() => {
        renderTrendCharts(trends);
        renderResourceCharts();
    }, 100);
}

/**
 * Calculate executive-level KPIs
 */
function calculateExecutiveKPIs() {
    const { tqcData, inspectorData, buildingData, dailyData } = state.processedData;
    
    // Overall quality metrics
    const totalValidation = Object.values(tqcData).reduce((sum, tqc) => sum + tqc.totalValidation, 0);
    const totalReject = Object.values(tqcData).reduce((sum, tqc) => sum + tqc.totalReject, 0);
    const overallRejectRate = totalValidation > 0 ? (totalReject / totalValidation * 100) : 0;
    
    // Target achievement (assuming 3% target reject rate)
    const targetRejectRate = 3.0;
    const targetAchievement = Math.max(0, 100 - (overallRejectRate - targetRejectRate) * 20);
    
    // Productivity metrics
    const activeInspectors = Object.values(inspectorData).filter(i => i.totalValidation > 0).length;
    const avgProductivity = totalValidation / Math.max(activeInspectors, 1) / 30; // per day
    
    // Risk metrics
    const highRiskTQCs = Object.values(tqcData).filter(t => 
        t.totalValidation > 100 && (t.totalReject / t.totalValidation * 100) > 5
    ).length;
    
    // Trend calculation (comparing to previous period)
    const dates = Object.keys(dailyData).sort();
    const recentDates = dates.slice(-7);
    const previousDates = dates.slice(-14, -7);
    
    const recentRejectRate = calculatePeriodRejectRate(recentDates);
    const previousRejectRate = calculatePeriodRejectRate(previousDates);
    const rejectRateTrend = ((recentRejectRate - previousRejectRate) / previousRejectRate * 100) || 0;
    
    return {
        overallRejectRate: {
            value: overallRejectRate.toFixed(2),
            unit: '%',
            label: '전체 불량률',
            status: overallRejectRate <= 3 ? 'good' : overallRejectRate <= 5 ? 'warning' : 'danger',
            trend: rejectRateTrend.toFixed(1)
        },
        targetAchievement: {
            value: targetAchievement.toFixed(0),
            unit: '%',
            label: '목표 달성률',
            status: targetAchievement >= 90 ? 'good' : targetAchievement >= 70 ? 'warning' : 'danger',
            trend: null
        },
        avgProductivity: {
            value: Math.round(avgProductivity),
            unit: '개/일',
            label: '인당 일일 검사량',
            status: avgProductivity >= 500 ? 'good' : avgProductivity >= 300 ? 'warning' : 'danger',
            trend: null
        },
        highRiskCount: {
            value: highRiskTQCs,
            unit: '명',
            label: '고위험 TQC',
            status: highRiskTQCs === 0 ? 'good' : highRiskTQCs <= 5 ? 'warning' : 'danger',
            trend: null
        },
        activeInspectors: {
            value: activeInspectors,
            unit: '명',
            label: '활성 검사원',
            status: 'neutral',
            trend: null
        },
        totalValidation: {
            value: totalValidation.toLocaleString(),
            unit: '개',
            label: '총 검사량',
            status: 'neutral',
            trend: null
        }
    };
}

/**
 * Generate performance rankings
 */
function generatePerformanceRankings() {
    const { tqcData, inspectorData } = state.processedData;
    
    // TQC rankings by reject rate (lower is better)
    const tqcList = Object.values(tqcData)
        .filter(t => t.totalValidation > 50)
        .map(t => ({
            ...t,
            rejectRate: t.totalValidation > 0 ? (t.totalReject / t.totalValidation * 100) : 0
        }));
    
    const topTQCs = tqcList
        .sort((a, b) => a.rejectRate - b.rejectRate)
        .slice(0, 5);
    
    const bottomTQCs = tqcList
        .sort((a, b) => b.rejectRate - a.rejectRate)
        .slice(0, 5);
    
    // Auditor rankings by effectiveness
    const topAuditors = Object.values(inspectorData)
        .filter(a => a.totalValidation > 100)
        .map(a => ({
            ...a,
            effectiveness: a.totalValidation / Math.max(a.avgDailyValidation, 1)
        }))
        .sort((a, b) => b.effectiveness - a.effectiveness)
        .slice(0, 5);
    
    return { topTQCs, bottomTQCs, topAuditors };
}

/**
 * Analyze quality trends
 */
function analyzeQualityTrends() {
    const { dailyData } = state.processedData;
    const dates = Object.keys(dailyData).sort().slice(-30); // Last 30 days
    
    const rejectRates = [];
    const validationVolumes = [];
    
    dates.forEach(date => {
        const dayData = dailyData[date];
        const totalValidation = Object.values(dayData.tqcData).reduce((sum, t) => sum + t.validationQty, 0);
        const totalReject = Object.values(dayData.tqcData).reduce((sum, t) => sum + t.rejectQty, 0);
        
        rejectRates.push(totalValidation > 0 ? (totalReject / totalValidation * 100) : 0);
        validationVolumes.push(totalValidation);
    });
    
    return { dates, rejectRates, validationVolumes };
}

/**
 * Generate actionable recommendations based on data analysis
 */
function generateActionableRecommendations() {
    const { tqcData, defectTypes, buildingData } = state.processedData;
    const recommendations = [];
    
    // High-risk TQC recommendation
    const highRiskTQCs = Object.values(tqcData)
        .filter(t => t.totalValidation > 100 && (t.totalReject / t.totalValidation * 100) > 5);
    
    if (highRiskTQCs.length > 0) {
        recommendations.push({
            priority: 'high',
            title: '고위험 TQC 즉시 교육 필요',
            description: `${highRiskTQCs.length}명의 TQC가 5% 이상의 불량률을 보이고 있습니다.`,
            action: '집중 재교육 프로그램 실시 권장',
            targets: highRiskTQCs.slice(0, 3).map(t => t.name).join(', ')
        });
    }
    
    // Top defect type recommendation
    const topDefect = Object.entries(defectTypes).sort((a, b) => b[1] - a[1])[0];
    if (topDefect && topDefect[1] > 100) {
        recommendations.push({
            priority: 'medium',
            title: '주요 불량 유형 개선 필요',
            description: `'${topDefect[0]}' 불량이 ${topDefect[1]}건 발생했습니다.`,
            action: '해당 불량 유형에 대한 공정 개선 검토',
            targets: '전 공정'
        });
    }
    
    // Building performance recommendation
    const poorBuildings = Object.entries(buildingData)
        .filter(([, data]) => data.totalValidation > 1000)
        .map(([name, data]) => ({
            name,
            rejectRate: data.totalReject / data.totalValidation * 100
        }))
        .filter(b => b.rejectRate > 4)
        .sort((a, b) => b.rejectRate - a.rejectRate);
    
    if (poorBuildings.length > 0) {
        recommendations.push({
            priority: 'medium',
            title: '건물별 품질 격차 해소 필요',
            description: `${poorBuildings[0].name} 건물의 불량률이 ${poorBuildings[0].rejectRate.toFixed(2)}%입니다.`,
            action: '해당 건물 품질 관리 체계 점검',
            targets: poorBuildings[0].name
        });
    }
    
    return recommendations;
}

/**
 * Helper function to calculate period reject rate
 */
function calculatePeriodRejectRate(dates) {
    const { dailyData } = state.processedData;
    let totalValidation = 0;
    let totalReject = 0;
    
    dates.forEach(date => {
        if (dailyData[date]) {
            const dayData = dailyData[date];
            Object.values(dayData.tqcData).forEach(t => {
                totalValidation += t.validationQty;
                totalReject += t.rejectQty;
            });
        }
    });
    
    return totalValidation > 0 ? (totalReject / totalValidation * 100) : 0;
}

/**
 * Render KPI cards
 */
function renderKPICards(kpis) {
    return Object.entries(kpis).map(([key, kpi]) => {
        const statusColor = kpi.status === 'good' ? '#10b981' : 
                           kpi.status === 'warning' ? '#f59e0b' : 
                           kpi.status === 'danger' ? '#ef4444' : '#6b7280';
        
        const trendIcon = kpi.trend ? (
            parseFloat(kpi.trend) > 0 ? '↑' : parseFloat(kpi.trend) < 0 ? '↓' : '→'
        ) : '';
        
        const trendColor = kpi.trend ? (
            parseFloat(kpi.trend) > 0 ? '#ef4444' : '#10b981'
        ) : '';
        
        return `
            <div class="kpi-card" style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">${kpi.label}</p>
                        <h3 style="font-size: 2rem; font-weight: bold; margin: 0.25rem 0; color: ${statusColor};">
                            ${kpi.value}${kpi.unit}
                        </h3>
                        ${kpi.trend ? `
                            <p style="color: ${trendColor}; font-size: 0.875rem; margin: 0;">
                                ${trendIcon} ${Math.abs(parseFloat(kpi.trend))}%
                            </p>
                        ` : ''}
                    </div>
                    <div style="width: 8px; height: 8px; border-radius: 50%; background: ${statusColor};"></div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render ranking list
 */
function renderRankingList(items, type, isBottom = false) {
    if (!items || items.length === 0) {
        return '<p style="text-align: center; color: #6b7280;">데이터 없음</p>';
    }
    
    return `
        <ol style="list-style: none; padding: 0; margin: 0;">
            ${items.map((item, index) => {
                const value = type === 'tqc' ? 
                    `${item.rejectRate.toFixed(2)}%` : 
                    `${Math.round(item.effectiveness)}점`;
                
                const badgeColor = isBottom ? '#ef4444' : 
                                  index === 0 ? '#fbbf24' : 
                                  index <= 2 ? '#9ca3af' : '#d1d5db';
                
                return `
                    <li style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #f3f4f6;">
                        <span style="display: flex; align-items: center;">
                            <span style="background: ${badgeColor}; color: white; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-right: 0.5rem;">
                                ${index + 1}
                            </span>
                            ${item.name}
                        </span>
                        <span style="font-weight: bold; color: ${isBottom ? '#ef4444' : '#10b981'};">
                            ${value}
                        </span>
                    </li>
                `;
            }).join('')}
        </ol>
    `;
}

/**
 * Render recommendations
 */
function renderRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        return '<p style="text-align: center; color: #6b7280;">현재 특별한 권장 사항이 없습니다.</p>';
    }
    
    return recommendations.map(rec => {
        const priorityColor = rec.priority === 'high' ? '#ef4444' : 
                             rec.priority === 'medium' ? '#f59e0b' : '#3b82f6';
        
        const priorityLabel = rec.priority === 'high' ? '긴급' : 
                             rec.priority === 'medium' ? '중요' : '권장';
        
        return `
            <div style="background: #f9fafb; border-left: 4px solid ${priorityColor}; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; font-weight: bold;">${rec.title}</h4>
                    <span style="background: ${priorityColor}; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">
                        ${priorityLabel}
                    </span>
                </div>
                <p style="margin: 0.5rem 0; color: #4b5563;">${rec.description}</p>
                <p style="margin: 0.5rem 0; font-weight: bold;">✅ ${rec.action}</p>
                <p style="margin: 0; font-size: 0.875rem; color: #6b7280;">대상: ${rec.targets}</p>
            </div>
        `;
    }).join('');
}

/**
 * Render risk alerts
 */
function renderRiskAlerts() {
    const { tqcData, buildingData } = state.processedData;
    const alerts = [];
    
    // Check for sudden spike in reject rate
    const recentTrend = analyzeRecentTrend();
    if (recentTrend.spike) {
        alerts.push({
            type: 'spike',
            title: '불량률 급증 감지',
            description: `최근 3일간 불량률이 ${recentTrend.increase.toFixed(1)}% 증가했습니다.`,
            severity: 'high'
        });
    }
    
    // Check for capacity issues
    const capacityIssues = checkCapacityIssues();
    if (capacityIssues.length > 0) {
        alerts.push({
            type: 'capacity',
            title: '검사 용량 부족',
            description: `${capacityIssues[0].building} 건물의 검사 인력이 부족합니다.`,
            severity: 'medium'
        });
    }
    
    // Check for consistency issues
    const consistencyIssues = checkConsistencyIssues();
    if (consistencyIssues.length > 0) {
        alerts.push({
            type: 'consistency',
            title: '품질 일관성 문제',
            description: `${consistencyIssues.length}개 TQC의 품질 변동성이 높습니다.`,
            severity: 'medium'
        });
    }
    
    if (alerts.length === 0) {
        return '<p style="text-align: center; color: #10b981;">✅ 현재 특별한 위험 사항이 없습니다.</p>';
    }
    
    return alerts.map(alert => {
        const severityColor = alert.severity === 'high' ? '#ef4444' : 
                             alert.severity === 'medium' ? '#f59e0b' : '#3b82f6';
        
        return `
            <div style="background: white; border: 1px solid ${severityColor}; border-radius: 8px; padding: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">
                        ${alert.type === 'spike' ? '📈' : alert.type === 'capacity' ? '👥' : '⚠️'}
                    </span>
                    <h4 style="margin: 0; color: ${severityColor};">${alert.title}</h4>
                </div>
                <p style="margin: 0; color: #4b5563;">${alert.description}</p>
            </div>
        `;
    }).join('');
}

/**
 * Analyze recent trend for spikes
 */
function analyzeRecentTrend() {
    const { dailyData } = state.processedData;
    const dates = Object.keys(dailyData).sort();
    const recentDates = dates.slice(-3);
    const previousDates = dates.slice(-6, -3);
    
    const recentRate = calculatePeriodRejectRate(recentDates);
    const previousRate = calculatePeriodRejectRate(previousDates);
    
    const increase = recentRate - previousRate;
    const spike = increase > 1.0; // More than 1% increase
    
    return { spike, increase };
}

/**
 * Check for capacity issues
 */
function checkCapacityIssues() {
    const { buildingData, inspectorData } = state.processedData;
    const issues = [];
    
    Object.entries(buildingData).forEach(([building, data]) => {
        const inspectorsInBuilding = Object.values(inspectorData)
            .filter(i => i.buildings && i.buildings.has(building)).length;
        
        const dailyVolume = data.totalValidation / 30;
        const capacityPerInspector = 500; // Expected daily capacity
        const requiredInspectors = Math.ceil(dailyVolume / capacityPerInspector);
        
        if (inspectorsInBuilding < requiredInspectors) {
            issues.push({
                building,
                shortage: requiredInspectors - inspectorsInBuilding
            });
        }
    });
    
    return issues;
}

/**
 * Check for consistency issues
 */
function checkConsistencyIssues() {
    const { tqcData } = state.processedData;
    
    return Object.values(tqcData)
        .filter(t => t.sustainability && t.sustainability.volatilityScore > 50)
        .map(t => ({
            name: t.name,
            score: t.sustainability.volatilityScore
        }));
}

/**
 * Render trend charts
 */
function renderTrendCharts(trends) {
    const shortLabels = trends.dates.map(d => d.substring(5));
    
    // Reject rate trend chart
    createLineChart('rejectRateTrendChart', {
        labels: shortLabels,
        datasets: [{
            label: '일별 불량률 (%)',
            data: trends.rejectRates,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4
        }, {
            label: '목표 불량률',
            data: Array(trends.dates.length).fill(3),
            borderColor: '#10b981',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 0
        }]
    });
    
    // Validation volume trend chart
    createLineChart('validationVolumeTrendChart', {
        labels: shortLabels,
        datasets: [{
            label: '일별 검사량',
            data: trends.validationVolumes,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
        }]
    });
}

/**
 * Render resource allocation charts
 */
function renderResourceCharts() {
    const { tqcData, inspectorData, buildingData } = state.processedData;
    
    // Workload distribution by building
    const buildingLabels = Object.keys(buildingData).slice(0, 10);
    const buildingWorkloads = buildingLabels.map(b => buildingData[b].totalValidation);
    
    createBarChart('workloadDistributionChart', {
        labels: buildingLabels,
        datasets: [{
            label: '건물별 검사량',
            data: buildingWorkloads,
            backgroundColor: '#3b82f6'
        }]
    });
    
    // Inspector efficiency chart
    const inspectorList = Object.values(inspectorData)
        .filter(i => i.totalValidation > 100)
        .sort((a, b) => b.avgDailyValidation - a.avgDailyValidation)
        .slice(0, 10);
    
    createBarChart('inspectorEfficiencyChart', {
        labels: inspectorList.map(i => i.name),
        datasets: [{
            label: '일평균 검사량',
            data: inspectorList.map(i => Math.round(i.avgDailyValidation)),
            backgroundColor: '#10b981'
        }]
    });
}