import { state } from '../../state.js';

// ✅ CDN으로 로드된 Chart.js를 명시적으로 참조
const Chart = window.Chart;

/**
 * 범용 차트 생성 함수
 * Chart.js를 사용하여 다양한 타입의 차트를 생성
 */
export function createChart(canvasId, type, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    if (state.charts[canvasId]) {
        state.charts[canvasId].destroy();
    }
    
    const ctx = canvas.getContext('2d');
    state.charts[canvasId] = new Chart(ctx, {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            ...options
        }
    });
}

/**
 * 라인 차트 생성 함수
 */
export function createLineChart(canvasId, data, options = {}) {
    createChart(canvasId, 'line', data, options);
}

/**
 * 바 차트 생성 함수
 */
export function createBarChart(canvasId, data, options = {}) {
    createChart(canvasId, 'bar', data, options);
}

/**
 * 파이 차트 생성 함수
 */
export function createPieChart(canvasId, data, options = {}) {
    createChart(canvasId, 'pie', data, {
        plugins: {
            legend: {
                position: 'right'
            }
        },
        ...options
    });
}

/**
 * 도넛 차트 생성 함수
 */
export function createDoughnutChart(canvasId, data, options = {}) {
    createChart(canvasId, 'doughnut', data, {
        plugins: {
            legend: {
                position: 'right'
            }
        },
        ...options
    });
}

// 이 파일에는 Chart.js를 사용한 차트 생성 함수들이 포함되어 있습니다:

// createChart() - 범용 차트 생성 (Chart.js 기반)
// createLineChart() - 라인 차트 생성
// createBarChart() - 바 차트 생성
// createPieChart() - 파이 차트 생성 (범례를 오른쪽에 배치)

// 모든 차트 함수들이 state.charts 객체를 통해 차트 인스턴스를 관리하므로 state를 import했습니다.