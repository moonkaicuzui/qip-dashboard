import { state } from './state.js';

/**
 * 데이터 처리의 메인 함수
 * 원본 데이터를 필터링하고 모든 필요한 통계 지표를 계산합니다.
 */
export function processData() {
    try {
        const filteredData = filterDataByPeriod(state.rawData);
        const processed = initializeProcessedDataObject();
        processRawData(filteredData, processed);
        calculateFinalStatistics(processed);

        state.processedData = { ...state.processedData, ...processed };
        state.processedData.buildings = Array.from(processed.buildings).sort();
        state.processedData.models = Array.from(processed.models).sort();

    } catch (error) {
        console.error('데이터 처리 중 오류:', error);
    }
}

/**
 * 처리된 데이터를 저장할 객체를 초기화합니다.
 */
function initializeProcessedDataObject() {
    return {
        totalValidation: 0, totalReject: 0, totalRejectRate: 0,
        avgDailyValidation: 0,
        buildings: new Set(), models: new Set(),
        tqcData: {}, inspectorData: {}, buildingData: {}, 
        poData: {}, lineData: {}, modelData: {},
        dailyData: {},
        dailyTqcCount: {},
        dailyLineCount: {}, // 일별 라인 수 저장을 위해 추가
        tqcMissingDefects: {},
        defectTypes: {},
    };
}

/**
 * 필터링된 원본 데이터를 순회하며 주요 데이터를 집계하고 구조화합니다.
 */
function processRawData(data, processed) {
    const dailyAggregates = {
        tqc: {},
        building: {},
        model: {},
        inspector: {}
    };

    // 🔥 일별 고유 TQC/라인 추적을 위한 객체들
    const dailyUniqueTqcs = {};
    const dailyUniqueLines = {};

    data.forEach(row => {
        const validationQty = parseInt(row['Validation Qty']) || 0;
        const passQty = parseInt(row['Pass Qty']) || 0;
        const rejectQty = parseInt(row['Reject Qty']) || 0;

        // Skip only if all quantities are 0
        if (validationQty === 0 && passQty === 0 && rejectQty === 0) return;

        processed.totalValidation += validationQty;
        processed.totalReject += rejectQty;

        const date = parseDate(row['Inspection Date']);
        if (date) {
            const dateStr = date.toISOString().split('T')[0];
            
            // 일별 검증/불량 데이터 집계
            if (!processed.dailyData[dateStr]) {
                processed.dailyData[dateStr] = { totalValidation: 0, totalReject: 0 };
            }
            processed.dailyData[dateStr].totalValidation += validationQty;
            processed.dailyData[dateStr].totalReject += rejectQty;
            
            // 🔥 일별 고유 TQC 추적 (TQC ID가 있는 경우만)
            if (row['TQC ID'] && row['TQC ID'].toString().trim() !== '') {
                if (!dailyUniqueTqcs[dateStr]) dailyUniqueTqcs[dateStr] = new Set();
                dailyUniqueTqcs[dateStr].add(row['TQC ID'].toString().trim());
            }
            
            // 🔥 일별 고유 라인 추적 (Line이 있는 경우만)
            if (row['Line'] && row['Line'].toString().trim() !== '') {
                if (!dailyUniqueLines[dateStr]) dailyUniqueLines[dateStr] = new Set();
                dailyUniqueLines[dateStr].add(row['Line'].toString().trim());
            }
        }

        const building = row['Building'] || 'Unknown';
        const model = row['Model'] || 'Unknown';
        processed.buildings.add(building);
        processed.models.add(model);

        aggregateTqcData(row, validationQty, rejectQty, processed);
        aggregateBuildingData(row, validationQty, rejectQty, processed);
        aggregateModelData(row, validationQty, rejectQty, processed);
        aggregatePoAndLineData(row, validationQty, rejectQty, processed);
        aggregateTqcMissingDefects(row, validationQty, rejectQty, processed);

        if (date) {
            const dateStr = date.toISOString().split('T')[0];
            aggregateForSustainability(row, dateStr, validationQty, rejectQty, dailyAggregates);
        }
    });
    
    // 🔥 일별 고유 TQC/라인 수를 카운트로 변환
    Object.keys(dailyUniqueTqcs).forEach(dateStr => {
        processed.dailyTqcCount[dateStr] = dailyUniqueTqcs[dateStr].size;
    });
    
    Object.keys(dailyUniqueLines).forEach(dateStr => {
        processed.dailyLineCount[dateStr] = dailyUniqueLines[dateStr].size;
    });

    // 🔥 누락된 날짜에 대해 0으로 초기화
    Object.keys(processed.dailyData).forEach(dateStr => {
        if (!processed.dailyTqcCount[dateStr]) {
            processed.dailyTqcCount[dateStr] = 0;
        }
        if (!processed.dailyLineCount[dateStr]) {
            processed.dailyLineCount[dateStr] = 0;
        }
    });

    processed.sustainabilityAggregates = dailyAggregates;
    
    // 🔥 디버그를 위한 로그 (잠시 활성화)
    console.log('📊 집계 완료:', {
        totalDays: Object.keys(processed.dailyData).length,
        tqcCountDays: Object.keys(processed.dailyTqcCount).length,
        lineCountDays: Object.keys(processed.dailyLineCount).length,
        sampleTqcCount: Object.values(processed.dailyTqcCount).slice(0, 5),
        sampleLineCount: Object.values(processed.dailyLineCount).slice(0, 5)
    });
}


/**
 * 집계된 데이터를 기반으로 최종 통계(평균, CV, 변동성 점수 등)를 계산합니다.
 */
function calculateFinalStatistics(processed) {
    processed.totalRejectRate = processed.totalValidation > 0 
        ? (processed.totalReject / processed.totalValidation * 100) : 0;

    const totalDays = Object.keys(processed.dailyData).length;
    processed.avgDailyValidation = totalDays > 0 ? processed.totalValidation / totalDays : 0;

    const { tqc, building, model, inspector } = processed.sustainabilityAggregates;

    calculateSustainabilityMetrics(processed.tqcData, tqc, 'rejectRates');
    calculateSustainabilityMetrics(processed.buildingData, building, 'rejectRates');
    calculateSustainabilityMetrics(processed.modelData, model, 'rejectRates');
    
    calculateInspectorSustainability(processed.inspectorData, inspector);
}


/**
 * TQC 데이터를 집계합니다.
 */
function aggregateTqcData(row, validationQty, rejectQty, processed) {
    if (!row['TQC ID'] || !row['TQC Name']) return;
    
    const tqcKey = `${row['TQC ID']}-${row['TQC Name']}`;
    if (!processed.tqcData[tqcKey]) {
        processed.tqcData[tqcKey] = {
            id: row['TQC ID'], name: row['TQC Name'], buildings: new Set(),
            totalValidation: 0, totalReject: 0, defects: {}, dailyDefects: {} // 일별 불량 데이터 추가
        };
    }
    const tqc = processed.tqcData[tqcKey];
    tqc.totalValidation += validationQty;
    tqc.totalReject += rejectQty;
    tqc.buildings.add(row['Building'] || 'Unknown');
    
    const date = parseDate(row['Inspection Date']);
    if (row['Error'] && rejectQty > 0) {
        const defectList = parseDefectTypes(row['Error']);
        const defectCountPerType = rejectQty / defectList.length;
        defectList.forEach(defect => {
            tqc.defects[defect] = (tqc.defects[defect] || 0) + defectCountPerType;
            processed.defectTypes[defect] = (processed.defectTypes[defect] || 0) + defectCountPerType;

            // TQC 팝업의 Top3 불량 추세를 위한 데이터 집계
            if (date) {
                const dateStr = date.toISOString().split('T')[0];
                if (!tqc.dailyDefects[defect]) tqc.dailyDefects[defect] = {};
                tqc.dailyDefects[defect][dateStr] = (tqc.dailyDefects[defect][dateStr] || 0) + defectCountPerType;
            }
        });
    }
}

/**
 * 빌딩 데이터를 집계합니다.
 */
function aggregateBuildingData(row, validationQty, rejectQty, processed) {
    const building = row['Building'] || 'Unknown';
    if (!processed.buildingData[building]) {
        processed.buildingData[building] = { totalValidation: 0, totalReject: 0, defects: {} };
    }
    const bData = processed.buildingData[building];
    bData.totalValidation += validationQty;
    bData.totalReject += rejectQty;
    if (row['Error'] && rejectQty > 0) {
        const defectList = parseDefectTypes(row['Error']);
        bData.defects = bData.defects || {};
        defectList.forEach(defect => {
             bData.defects[defect] = (bData.defects[defect] || 0) + (rejectQty / defectList.length);
        });
    }
}

/**
 * 모델 데이터를 집계합니다.
 */
function aggregateModelData(row, validationQty, rejectQty, processed) {
    const model = row['Model'] || 'Unknown';
    if (!processed.modelData[model]) {
        processed.modelData[model] = { totalValidation: 0, totalReject: 0, defects: {} };
    }
    const mData = processed.modelData[model];
    mData.totalValidation += validationQty;
    mData.totalReject += rejectQty;
    if (row['Error'] && rejectQty > 0) {
        const defectList = parseDefectTypes(row['Error']);
        mData.defects = mData.defects || {};
        defectList.forEach(defect => {
             mData.defects[defect] = (mData.defects[defect] || 0) + (rejectQty / defectList.length);
        });
    }
}

/**
 * PO 및 라인 데이터를 집계합니다.
 */
function aggregatePoAndLineData(row, validationQty, rejectQty, processed) {
    const po = row['PO No'] || 'Unknown';
    if (!processed.poData[po]) {
        processed.poData[po] = { totalValidation: 0, totalReject: 0 };
    }
    processed.poData[po].totalValidation += validationQty;
    processed.poData[po].totalReject += rejectQty;

    const line = row['Line'] || 'Unknown';
    if (!processed.lineData[line]) {
        processed.lineData[line] = { totalValidation: 0, totalReject: 0 };
    }
    processed.lineData[line].totalValidation += validationQty;
    processed.lineData[line].totalReject += rejectQty;
}

/**
 * 감사관(Auditor)의 재검사 데이터를 집계합니다. (TQC 불량 유출 분석용)
 */
function aggregateTqcMissingDefects(row, validationQty, rejectQty, processed) {
    const inspectorId = row['Inspector ID'] || '';
    const tqcId = row['TQC ID'] || '';
    if (!inspectorId || !tqcId || validationQty <= 0) return;

    const tqcKey = `${row['TQC ID']}-${row['TQC Name']}`;
    if (!processed.tqcMissingDefects[tqcKey]) {
        processed.tqcMissingDefects[tqcKey] = {
            id: row['TQC ID'], name: row['TQC Name'], totalAuditorInspection: 0,
            totalAuditorReject: 0, defectBreakdown: {}, 
            buildingBreakdown: {}, modelBreakdown: {}
        };
    }
    const tqcMissing = processed.tqcMissingDefects[tqcKey];
    tqcMissing.totalAuditorInspection += validationQty;
    tqcMissing.totalAuditorReject += rejectQty;

    if (row['Error'] && rejectQty > 0) {
        const defectList = parseDefectTypes(row['Error']);
        defectList.forEach(defect => {
            tqcMissing.defectBreakdown[defect] = (tqcMissing.defectBreakdown[defect] || 0) + (rejectQty / defectList.length);
        });
    }

    const building = row['Building'] || 'Unknown';
    if (!tqcMissing.buildingBreakdown[building]) {
        tqcMissing.buildingBreakdown[building] = { validation: 0, reject: 0 };
    }
    tqcMissing.buildingBreakdown[building].validation += validationQty;
    tqcMissing.buildingBreakdown[building].reject += rejectQty;

    const model = row['Model'] || 'Unknown';
    if (!tqcMissing.modelBreakdown[model]) {
        tqcMissing.modelBreakdown[model] = { validation: 0, reject: 0 };
    }
    tqcMissing.modelBreakdown[model].validation += validationQty;
    tqcMissing.modelBreakdown[model].reject += rejectQty;
}

/**
 * '지속성' 탭 분석을 위해 차원/날짜별로 상세 데이터를 집계합니다.
 */
function aggregateForSustainability(row, dateStr, validationQty, rejectQty, dailyAggregates) {
    const tqcKey = row['TQC ID'] ? `${row['TQC ID']}-${row['TQC Name']}` : null;
    const inspectorKey = row['Inspector ID'] ? `${row['Inspector ID']}-${row['Inspector Name']}` : null;
    const buildingKey = row['Building'] || 'Unknown';
    const modelKey = row['Model'] || 'Unknown';

    const updateDaily = (agg, key) => {
        if (!key) return;
        if (!agg[key]) agg[key] = {};
        if (!agg[key][dateStr]) agg[key][dateStr] = { v: 0, r: 0, tqcs: new Set(), models: new Set() };
        agg[key][dateStr].v += validationQty;
        agg[key][dateStr].r += rejectQty;
        if (tqcKey) agg[key][dateStr].tqcs.add(tqcKey);
        if (modelKey) agg[key][dateStr].models.add(modelKey);
    };

    updateDaily(dailyAggregates.tqc, tqcKey);
    updateDaily(dailyAggregates.building, buildingKey);
    updateDaily(dailyAggregates.model, modelKey);
    updateDaily(dailyAggregates.inspector, inspectorKey);
}


/**
 * TQC, 빌딩, 모델의 지속성 지표(CV, 4분위수 등)를 계산합니다.
 */
function calculateSustainabilityMetrics(targetData, dailyAggregates, metricName) {
    for (const key in dailyAggregates) {
        const dailyValues = dailyAggregates[key];
        const dataPoints = Object.values(dailyValues).map(day => day.v > 0 ? (day.r / day.v * 100) : 0);
        
        if (dataPoints.length > 1 && targetData[key]) {
            const stats = calculateStats(dataPoints);
            const quartiles = calculateQuartiles(dataPoints);
            const avgRejectRate = targetData[key].totalValidation > 0 ? (targetData[key].totalReject / targetData[key].totalValidation * 100) : 0;
            const volatility = categorizeVolatility(stats.cv, avgRejectRate, stats.stdDev);

            targetData[key].sustainability = {
                [metricName]: dataPoints,
                ...stats,
                quartiles,
                volatilityScore: volatility.score,
                volatilityCategory: volatility.category,
            };
        }
    }
}

/**
 * 감사관(Inspector)의 활동 일관성 지표를 계산합니다.
 */
function calculateInspectorSustainability(targetData, dailyAggregates) {
    for (const key in dailyAggregates) {
        const dailyValues = dailyAggregates[key];
        const daysActive = Object.keys(dailyValues).length;
        if (daysActive === 0) continue;

        let totalValidation = 0, totalReject = 0, totalTqcCount = 0, totalModelCount = 0;
        const dailyValidation = [];
        const dailyTqcCounts = [];
        const dailyModelCounts = [];

        for (const date in dailyValues) {
            totalValidation += dailyValues[date].v;
            totalReject += dailyValues[date].r;
            totalTqcCount += dailyValues[date].tqcs.size;
            totalModelCount += dailyValues[date].models.size;
            dailyValidation.push(dailyValues[date].v);
            dailyTqcCounts.push(dailyValues[date].tqcs.size);
            dailyModelCounts.push(dailyValues[date].models.size);
        }

        const [id, ...nameParts] = key.split('-');
        const name = nameParts.join('-');
        
        const validationQuartiles = calculateQuartiles(dailyValidation);
        const validationIQR = validationQuartiles.q3 - validationQuartiles.q1;
        const validationYAxisMax = validationQuartiles.q3 + 1.5 * validationIQR;

        targetData[key] = {
            id, name,
            totalValidation,
            totalReject,
            buildings: new Set(Object.values(dailyValues).flatMap(d => Array.from(d.tqcs).map(tqcKey => state.processedData.tqcData[tqcKey]?.buildings).flat()).filter(Boolean)),
            avgDailyValidation: totalValidation / daysActive,
            avgDailyTqcCount: totalTqcCount / daysActive,
            avgDailyModelCount: totalModelCount / daysActive,
            trends: {
                validation: dailyValidation,
                tqcCount: dailyTqcCounts,
                modelCount: dailyModelCounts,
                dates: Object.keys(dailyValues).sort(),
                yAxisMax: {
                    validation: validationYAxisMax
                }
            }
        };
    }
}


// --- 유틸리티 및 헬퍼 함수들 ---

function calculateStats(dataArray) {
    const n = dataArray.length;
    if (n === 0) return { sum: 0, avg: 0, stdDev: 0, cv: 0 };
    const sum = dataArray.reduce((a, b) => a + b, 0);
    const avg = sum / n;
    const variance = dataArray.reduce((acc, val) => acc + Math.pow(val - avg, 2), 0) / n;
    const stdDev = Math.sqrt(variance);
    const cv = avg !== 0 ? (stdDev / avg) * 100 : 0;
    return { sum, avg, stdDev, cv };
}

function calculateQuartiles(dataArray) {
    if (dataArray.length === 0) return { min: 0, q1: 0, median: 0, q3: 0, max: 0 };
    const sorted = [...dataArray].sort((a, b) => a - b);
    const q = (arr, p) => {
        const pos = (arr.length - 1) * p;
        const base = Math.floor(pos);
        const rest = pos - base;
        if (arr[base + 1] !== undefined) {
            return arr[base] + rest * (arr[base + 1] - arr[base]);
        } else {
            return arr[base];
        }
    };
    return {
        min: sorted[0],
        q1: q(sorted, 0.25),
        median: q(sorted, 0.5),
        q3: q(sorted, 0.75),
        max: sorted[sorted.length - 1],
    };
}

function categorizeVolatility(cv, avgRejectRate, stdDev) {
    const weight = avgRejectRate < 3 ? 2.0 :
                   avgRejectRate < 7 ? 1.5 :
                   1.0;
    const volatilityScore = cv / weight; 
    if (volatilityScore > 50 || stdDev > 3.0) {
        return { category: '고위험', score: volatilityScore };
    }
    if (volatilityScore > 25 || stdDev > 1.5) {
        return { category: '관심', score: volatilityScore };
    }
    return { category: '안정', score: volatilityScore };
}

function filterDataByPeriod(data) {
    if (state.currentPeriod === 'all' || !data) return data;
    const now = new Date();
    const cutoffDate = new Date();
    if (state.currentPeriod === 'month') {
        cutoffDate.setMonth(now.getMonth() - 1);
    } else if (state.currentPeriod === 'week') {
        cutoffDate.setDate(now.getDate() - 7);
    }
    return data.filter(row => {
        const date = parseDate(row['Inspection Date']);
        return date && date >= cutoffDate;
    });
}

function parseDate(dateValue) {
    if (!dateValue) return null;
    if (dateValue instanceof Date && !isNaN(dateValue.getTime())) return dateValue;
    if (typeof dateValue === 'number') { 
        return new Date(Math.round((dateValue - 25569) * 86400 * 1000));
    }
    if (typeof dateValue === 'string') {
        const standardDate = new Date(dateValue);
        if (!isNaN(standardDate.getTime())) return standardDate;
        const parts = dateValue.match(/(\d+)/g);
        if (parts && parts.length === 3) {
            let y = parts[0].length === 4 ? parts[0] : parts[2];
            let m = parts[0].length === 4 ? parts[1] : parts[0];
            let d = parts[0].length === 4 ? parts[2] : parts[1];
            if (y.length === 2) y = `20${y}`;
            const date = new Date(`${y}-${m}-${d}`);
            if (!isNaN(date.getTime())) return date;
        }
    }
    return null;
}

function parseDefectTypes(errorString) {
    if (!errorString || typeof errorString !== 'string' || errorString.trim() === '') return [];
    return errorString.split(',').map(d => d.trim()).filter(Boolean);
}