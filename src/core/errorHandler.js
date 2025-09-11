/**
 * Error Handler Module
 * 전역 에러 처리 및 로깅 시스템
 * @module errorHandler
 */

class ErrorHandler {
    constructor() {
        this.errors = [];
        this.maxErrors = 100;
        this.listeners = new Set();
        this.initializeGlobalHandlers();
    }

    /**
     * 전역 에러 핸들러 초기화
     */
    initializeGlobalHandlers() {
        // 일반 JavaScript 에러 처리
        window.addEventListener('error', (event) => {
            this.handleError({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error
            });
            event.preventDefault();
        });

        // Promise rejection 처리
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'promise',
                message: event.reason?.message || event.reason,
                promise: event.promise,
                reason: event.reason
            });
            event.preventDefault();
        });

        // Console error 오버라이드
        const originalConsoleError = console.error;
        console.error = (...args) => {
            this.handleError({
                type: 'console',
                message: args.join(' '),
                args: args
            });
            originalConsoleError.apply(console, args);
        };
    }

    /**
     * 에러 처리
     * @param {Object} error - 에러 객체
     */
    handleError(error) {
        // 에러 정보 보강
        const enrichedError = {
            ...error,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            id: this.generateErrorId()
        };

        // 에러 저장
        this.storeError(enrichedError);

        // 에러 분류 및 심각도 결정
        const severity = this.classifyError(enrichedError);
        enrichedError.severity = severity;

        // 리스너에게 알림
        this.notifyListeners(enrichedError);

        // 심각한 에러는 사용자에게 알림
        if (severity === 'critical' || severity === 'high') {
            this.showUserNotification(enrichedError);
        }

        // 로그 전송 (프로덕션 환경)
        if (this.shouldSendToServer()) {
            this.sendToServer(enrichedError);
        }
    }

    /**
     * 에러 심각도 분류
     * @param {Object} error - 에러 객체
     * @returns {string} severity level
     */
    classifyError(error) {
        const criticalPatterns = [
            /Google.*API/i,
            /authentication/i,
            /authorization/i,
            /network.*fail/i
        ];

        const highPatterns = [
            /data.*corrupt/i,
            /undefined.*null/i,
            /cannot.*read/i,
            /memory/i
        ];

        const message = error.message || '';

        if (criticalPatterns.some(pattern => pattern.test(message))) {
            return 'critical';
        }

        if (highPatterns.some(pattern => pattern.test(message))) {
            return 'high';
        }

        if (error.type === 'promise') {
            return 'medium';
        }

        return 'low';
    }

    /**
     * 에러 저장
     * @param {Object} error - 에러 객체
     */
    storeError(error) {
        this.errors.push(error);

        // 최대 개수 유지
        if (this.errors.length > this.maxErrors) {
            this.errors.shift();
        }

        // 로컬 스토리지에 저장
        try {
            localStorage.setItem('dashboard_errors', JSON.stringify(this.errors.slice(-10)));
        } catch (e) {
            // 스토리지 에러는 무시
        }
    }

    /**
     * 사용자에게 알림 표시
     * @param {Object} error - 에러 객체
     */
    showUserNotification(error) {
        // 기존 알림 제거
        const existingNotification = document.querySelector('.error-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // 알림 생성
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="error-notification-content">
                <div class="error-notification-icon">⚠️</div>
                <div class="error-notification-message">
                    <strong>오류 발생</strong>
                    <p>${this.getUserFriendlyMessage(error)}</p>
                </div>
                <button class="error-notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // 스타일 적용
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fff;
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // 자동 제거
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * 사용자 친화적 메시지 생성
     * @param {Object} error - 에러 객체
     * @returns {string} 사용자 메시지
     */
    getUserFriendlyMessage(error) {
        const messageMap = {
            'network': '네트워크 연결을 확인해 주세요.',
            'authentication': '로그인이 필요합니다.',
            'data': '데이터 로딩 중 문제가 발생했습니다.',
            'permission': '권한이 필요합니다.',
            'default': '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
        };

        for (const [key, message] of Object.entries(messageMap)) {
            if (error.message && error.message.toLowerCase().includes(key)) {
                return message;
            }
        }

        return messageMap.default;
    }

    /**
     * 에러 ID 생성
     * @returns {string} 고유 ID
     */
    generateErrorId() {
        return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * 리스너 등록
     * @param {Function} callback - 콜백 함수
     */
    addListener(callback) {
        this.listeners.add(callback);
    }

    /**
     * 리스너 제거
     * @param {Function} callback - 콜백 함수
     */
    removeListener(callback) {
        this.listeners.delete(callback);
    }

    /**
     * 리스너에게 알림
     * @param {Object} error - 에러 객체
     */
    notifyListeners(error) {
        this.listeners.forEach(callback => {
            try {
                callback(error);
            } catch (e) {
                // 리스너 에러는 무시
            }
        });
    }

    /**
     * 서버로 전송 여부 결정
     * @returns {boolean}
     */
    shouldSendToServer() {
        // 프로덕션 환경이고 너무 많은 에러가 발생하지 않았을 때만
        return window.location.hostname !== 'localhost' && 
               this.errors.length < 50;
    }

    /**
     * 서버로 에러 전송
     * @param {Object} error - 에러 객체
     */
    async sendToServer(error) {
        try {
            // 실제 구현 시 엔드포인트 설정 필요
            const endpoint = '/api/errors';
            
            await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    error: error,
                    sessionId: this.getSessionId(),
                    timestamp: error.timestamp
                })
            });
        } catch (e) {
            // 전송 실패는 무시
        }
    }

    /**
     * 세션 ID 가져오기
     * @returns {string}
     */
    getSessionId() {
        let sessionId = sessionStorage.getItem('sessionId');
        if (!sessionId) {
            sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            sessionStorage.setItem('sessionId', sessionId);
        }
        return sessionId;
    }

    /**
     * 에러 로그 내보내기
     * @returns {Array} 에러 목록
     */
    exportErrors() {
        return this.errors;
    }

    /**
     * 에러 로그 초기화
     */
    clearErrors() {
        this.errors = [];
        localStorage.removeItem('dashboard_errors');
    }

    /**
     * 에러 통계
     * @returns {Object} 통계 정보
     */
    getStatistics() {
        const stats = {
            total: this.errors.length,
            bySeverity: {},
            byType: {},
            recent: this.errors.slice(-5)
        };

        this.errors.forEach(error => {
            // 심각도별 집계
            stats.bySeverity[error.severity] = (stats.bySeverity[error.severity] || 0) + 1;
            
            // 타입별 집계
            stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;
        });

        return stats;
    }
}

// 싱글톤 인스턴스 생성 및 내보내기
const errorHandler = new ErrorHandler();

// 전역 객체에 추가 (디버깅용)
if (typeof window !== 'undefined') {
    window.errorHandler = errorHandler;
}

export default errorHandler;