import { state } from '../../state.js';
import { translations } from '../../config.js';

/**
 * 날짜 파싱 유틸리티 함수
 * 다양한 형태의 날짜 데이터를 Date 객체로 변환
 */
export function parseDate(dateValue) {
    if (!dateValue) return null;
    
    // 이미 Date 객체인 경우
    if (dateValue instanceof Date && !isNaN(dateValue.getTime())) return dateValue;
    
    // Excel 시리얼 번호인 경우 (숫자)
    if (typeof dateValue === 'number') { 
        return new Date(Math.round((dateValue - 25569) * 86400 * 1000));
    }
    
    // 문자열인 경우
    if (typeof dateValue === 'string') {
        // 표준 ISO 형식 시도
        const standardDate = new Date(dateValue);
        if (!isNaN(standardDate.getTime())) return standardDate;
        
        // 다양한 날짜 형식 파싱 시도
        const parts = dateValue.match(/(\d+)/g);
        if (parts && parts.length === 3) {
            let y = parts[0].length === 4 ? parts[0] : parts[2];
            let m = parts[0].length === 4 ? parts[1] : parts[0];
            let d = parts[0].length === 4 ? parts[2] : parts[1];
            
            // 2자리 연도를 4자리로 변환
            if (y.length === 2) y = `20${y}`;
            
            const date = new Date(`${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`);
            if (!isNaN(date.getTime())) return date;
        }
    }
    
    return null;
}

/**
 * 불량 유형 파싱 함수
 * 쉼표로 구분된 불량 유형 문자열을 배열로 변환
 */
export function parseDefectTypes(errorString) {
    if (!errorString || typeof errorString !== 'string' || errorString.trim() === '') return [];
    
    return errorString
        .split(',')
        .map(defect => defect.trim())
        .filter(defect => defect.length > 0);
}

/**
 * 기본 통계 계산 함수
 * 평균, 표준편차, 변동계수 등을 계산
 */
export function calculateStats(dataArray) {
    const n = dataArray.length;
    if (n === 0) return { sum: 0, avg: 0, stdDev: 0, cv: 0, min: 0, max: 0 };
    
    const sum = dataArray.reduce((a, b) => a + b, 0);
    const avg = sum / n;
    const variance = dataArray.reduce((acc, val) => acc + Math.pow(val - avg, 2), 0) / n;
    const stdDev = Math.sqrt(variance);
    const cv = avg !== 0 ? (stdDev / avg) * 100 : 0;
    const min = Math.min(...dataArray);
    const max = Math.max(...dataArray);
    
    return { sum, avg, stdDev, cv, min, max };
}

/**
 * 4분위수 계산 함수
 */
export function calculateQuartiles(dataArray) {
    if (dataArray.length === 0) return { min: 0, q1: 0, median: 0, q3: 0, max: 0 };
    
    const sorted = [...dataArray].sort((a, b) => a - b);
    const n = sorted.length;
    
    const getPercentile = (arr, p) => {
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
        q1: getPercentile(sorted, 0.25),
        median: getPercentile(sorted, 0.5),
        q3: getPercentile(sorted, 0.75),
        max: sorted[n - 1],
    };
}

/**
 * 선형 회귀 추세선 계산
 * 데이터 포인트들에 대한 최적 직선을 계산
 */
export function calculateLinearRegression(dataPoints) {
    const n = dataPoints.length;
    if (n < 2) return dataPoints;
    
    const xValues = Array.from({length: n}, (_, i) => i);
    const sumX = xValues.reduce((a, b) => a + b, 0);
    const sumY = dataPoints.reduce((a, b) => a + b, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * dataPoints[i], 0);
    const sumXX = xValues.reduce((sum, x) => sum + x * x, 0);
    
    // 기울기와 y절편 계산
    const denominator = n * sumXX - sumX * sumX;
    if (denominator === 0) return dataPoints; // 분모가 0인 경우 원본 반환
    
    const slope = (n * sumXY - sumX * sumY) / denominator;
    const intercept = (sumY - slope * sumX) / n;
    
    return xValues.map(x => slope * x + intercept);
}

/**
 * 추세 분석 함수
 * 추세선을 바탕으로 증가/감소/안정 추세를 판단
 */
export function analyzeTrend(trendLine) {
    if (trendLine.length < 2) return 'stable';
    
    const start = trendLine[0];
    const end = trendLine[trendLine.length - 1];
    const diff = end - start;
    
    // 시작값의 5%를 임계값으로 설정
    const threshold = Math.abs(start) * 0.05;
    
    if (Math.abs(diff) < threshold) return 'stable';
    return diff > 0 ? 'increasing' : 'decreasing';
}

/**
 * 상관계수 계산 함수
 * 두 데이터셋 간의 선형 관계 강도를 측정
 */
export function calculateCorrelation(xArray, yArray) {
    if (xArray.length !== yArray.length || xArray.length < 2) return 0;
    
    const n = xArray.length;
    const sumX = xArray.reduce((a, b) => a + b, 0);
    const sumY = yArray.reduce((a, b) => a + b, 0);
    const sumXY = xArray.reduce((sum, x, i) => sum + x * yArray[i], 0);
    const sumXX = xArray.reduce((sum, x) => sum + x * x, 0);
    const sumYY = yArray.reduce((sum, y) => sum + y * y, 0);
    
    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumXX - sumX * sumX) * (n * sumYY - sumY * sumY));
    
    return denominator === 0 ? 0 : numerator / denominator;
}

/**
 * 이동평균 계산 함수
 */
export function calculateMovingAverage(dataArray, windowSize) {
    if (dataArray.length < windowSize) return dataArray;
    
    const result = [];
    for (let i = 0; i <= dataArray.length - windowSize; i++) {
        const window = dataArray.slice(i, i + windowSize);
        const average = window.reduce((sum, val) => sum + val, 0) / windowSize;
        result.push(average);
    }
    
    return result;
}

/**
 * 변동성 점수 계산 함수
 */
export function calculateVolatilityScore(dataArray, avgRejectRate) {
    const stats = calculateStats(dataArray);
    
    // 가중치 계산 (평균 불량률에 따라)
    const weight = avgRejectRate < 3 ? 2.0 :
                   avgRejectRate < 7 ? 1.5 :
                   1.0;
    
    // Cap volatility score at 100 for better readability
    const volatilityScore = stats.avg !== 0 ? Math.min(stats.cv / weight, 100) : 0;
    
    // 카테고리 분류
    let category = '안정';
    if (volatilityScore > 50 || stats.stdDev > 3.0) {
        category = '고위험';
    } else if (volatilityScore > 25 || stats.stdDev > 1.5) {
        category = '관심';
    }
    
    return {
        score: volatilityScore,
        category: category,
        cv: stats.cv,
        stdDev: stats.stdDev
    };
}

/**
 * 차트 카드에 추세 표시를 추가하는 함수
 */
export function addTrendIndicator(chartCard, trendType, dataPoints) {
    if (!chartCard) return;
    
    const existingIndicator = chartCard.querySelector('.trend-indicator');
    if (existingIndicator) existingIndicator.remove();
    
    const lang = state.currentLanguage;
    const subtitle = chartCard.querySelector('.card-subtitle');
    if (!subtitle) return;
    
    const indicator = document.createElement('div');
    indicator.className = 'trend-indicator';
    indicator.style.cssText = `
        margin-top: 0.5rem; 
        padding: 0.25rem 0.5rem; 
        border-radius: 0.25rem; 
        font-size: 0.75rem; 
        font-weight: 500;
        display: inline-block;
        text-align: center;
    `;
    
    const lastValue = dataPoints[dataPoints.length - 1];
    const firstValue = dataPoints[0];
    const changePercent = firstValue !== 0 ? ((lastValue - firstValue) / firstValue * 100).toFixed(1) : '0.0';
    
    switch(trendType) {
        case 'increasing':
            indicator.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
            indicator.style.color = '#dc2626';
            indicator.textContent = `📈 ${translations[lang].increasingTrendPercent} (+${Math.abs(changePercent)}%)`;
            break;
        case 'decreasing':
            indicator.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
            indicator.style.color = '#059669';
            indicator.textContent = `📉 ${translations[lang].decreasingTrendPercent} (-${Math.abs(changePercent)}%)`;
            break;
        default:
            indicator.style.backgroundColor = 'rgba(156, 163, 175, 0.1)';
            indicator.style.color = '#6b7280';
            indicator.textContent = `📊 ${translations[lang].stableTrendPercent}`;
    }
    
    subtitle.parentNode.insertBefore(indicator, subtitle.nextSibling);
}

/**
 * 특정 DOM 요소에 추세 표시를 추가하는 함수 (개선된 버전)
 */
export function addTrendIndicatorToElement(elementId, trendType, dataPoints) {
    const container = document.getElementById(elementId);
    if (!container) return;
    
    // 기존 추세 표시기 제거
    const existingIndicator = container.querySelector('.trend-indicator');
    if (existingIndicator) existingIndicator.remove();
    
    const lang = state.currentLanguage;
    const indicator = document.createElement('div');
    indicator.className = 'trend-indicator';
    indicator.style.cssText = `
        text-align: center;
        margin-bottom: 0.75rem;
        padding: 0.375rem 0.75rem;
        border-radius: 0.375rem;
        font-size: 0.8125rem;
        font-weight: 500;
        display: inline-block;
        width: auto;
        min-width: 120px;
    `;
    
    const lastValue = dataPoints[dataPoints.length - 1];
    const firstValue = dataPoints[0];
    const changePercent = firstValue !== 0 ? ((lastValue - firstValue) / firstValue * 100).toFixed(1) : '0.0';
    
    switch(trendType) {
        case 'increasing':
            indicator.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
            indicator.style.color = '#dc2626';
            indicator.textContent = `📈 ${translations[lang].trendIndicatorIncreasing} (+${Math.abs(changePercent)}%)`;
            break;
        case 'decreasing':
            indicator.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
            indicator.style.color = '#059669';
            indicator.textContent = `📉 ${translations[lang].trendIndicatorDecreasing} (-${Math.abs(changePercent)}%)`;
            break;
        default:
            indicator.style.backgroundColor = 'rgba(156, 163, 175, 0.1)';
            indicator.style.color = '#6b7280';
            indicator.textContent = `📊 ${translations[lang].trendIndicatorStable}`;
    }
    
    // 컨테이너를 중앙 정렬로 설정
    container.style.textAlign = 'center';
    container.appendChild(indicator);
}

/**
 * 색상 생성 유틸리티 함수
 */
export function getColorPalette(count) {
    const baseColors = [
        '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
        '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
        '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
        '#ec4899', '#f43f5e', '#e11d48', '#dc2626', '#b91c1c'
    ];
    
    if (count <= baseColors.length) {
        return baseColors.slice(0, count);
    }
    
    // 색상이 부족한 경우 HSL을 사용하여 동적 생성
    const colors = [];
    for (let i = 0; i < count; i++) {
        const hue = (i * 360 / count) % 360;
        const saturation = 65 + (i % 3) * 10; // 65-85%
        const lightness = 45 + (i % 4) * 5;   // 45-60%
        colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
    }
    
    return colors;
}

/**
 * 투명도가 적용된 색상 생성 함수
 */
export function addAlphaToColor(color, alpha) {
    if (color.startsWith('#')) {
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    if (color.startsWith('rgb(')) {
        return color.replace('rgb(', 'rgba(').replace(')', `, ${alpha})`);
    }
    
    return color; // HSL이나 다른 형식은 그대로 반환
}

/**
 * 숫자 포맷팅 함수
 */
export function formatNumber(num, decimals = 0) {
    if (num === null || num === undefined || isNaN(num)) return '0';
    
    return new Intl.NumberFormat('ko-KR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
}

/**
 * 퍼센트 포맷팅 함수
 */
export function formatPercent(num, decimals = 1) {
    if (num === null || num === undefined || isNaN(num)) return '0.0%';
    
    return new Intl.NumberFormat('ko-KR', {
        style: 'percent',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num / 100);
}

/**
 * 날짜 포맷팅 함수
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
    if (!date) return '';
    
    const d = date instanceof Date ? date : parseDate(date);
    if (!d) return '';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    switch (format) {
        case 'MM-DD':
            return `${month}-${day}`;
        case 'YYYY-MM':
            return `${year}-${month}`;
        case 'DD/MM/YYYY':
            return `${day}/${month}/${year}`;
        case 'MM/DD/YYYY':
            return `${month}/${day}/${year}`;
        default:
            return `${year}-${month}-${day}`;
    }
}

/**
 * 배열에서 최빈값(mode) 찾기
 */
export function findMode(array) {
    if (array.length === 0) return null;
    
    const frequency = {};
    let maxFreq = 0;
    let mode = null;
    
    array.forEach(item => {
        frequency[item] = (frequency[item] || 0) + 1;
        if (frequency[item] > maxFreq) {
            maxFreq = frequency[item];
            mode = item;
        }
    });
    
    return mode;
}

/**
 * 배열 그룹화 함수
 */
export function groupBy(array, keyFn) {
    return array.reduce((groups, item) => {
        const key = keyFn(item);
        if (!groups[key]) {
            groups[key] = [];
        }
        groups[key].push(item);
        return groups;
    }, {});
}

/**
 * 깊은 복사 함수
 */
export function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj);
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (obj instanceof Object) {
        const clonedObj = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
}

/**
 * 디바운싱 함수
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 스로틀링 함수
 */
export function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 범위 생성 함수
 */
export function range(start, end, step = 1) {
    const result = [];
    for (let i = start; i < end; i += step) {
        result.push(i);
    }
    return result;
}

/**
 * 배열 셔플 함수
 */
export function shuffle(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

/**
 * 안전한 나눗셈 함수 (0으로 나누기 방지)
 */
export function safeDivide(numerator, denominator, defaultValue = 0) {
    return denominator === 0 ? defaultValue : numerator / denominator;
}

/**
 * 값 클램핑 함수 (최소/최대값 제한)
 */
export function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

/**
 * 배열에서 이상치 제거 함수 (IQR 방법)
 */
export function removeOutliers(array, multiplier = 1.5) {
    if (array.length < 4) return array;
    
    const quartiles = calculateQuartiles(array);
    const iqr = quartiles.q3 - quartiles.q1;
    const lowerBound = quartiles.q1 - multiplier * iqr;
    const upperBound = quartiles.q3 + multiplier * iqr;
    
    return array.filter(value => value >= lowerBound && value <= upperBound);
}

/**
 * 문자열에서 숫자만 추출하는 함수
 */
export function extractNumbers(str) {
    if (typeof str !== 'string') return [];
    const matches = str.match(/\d+\.?\d*/g);
    return matches ? matches.map(Number) : [];
}