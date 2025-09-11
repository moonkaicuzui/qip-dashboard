/**
 * Data Fetcher Module
 * Google Drive 및 로컬 소스에서 데이터를 가져오는 통합 모듈
 * @module dataFetcher
 */

import googleDriveAPI from './googleDriveAPI.js';
import errorHandler from '../core/errorHandler.js';

class DataFetcher {
    constructor() {
        this.sources = {
            googleDrive: true,
            local: true,
            fallback: true
        };
        
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5분
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1초
    }

    /**
     * 데이터 소스 초기화
     */
    async initialize() {
        const results = {
            googleDrive: false,
            local: false
        };

        // Google Drive 초기화 시도
        if (this.sources.googleDrive) {
            try {
                await googleDriveAPI.initialize();
                results.googleDrive = true;
                console.log('✅ Google Drive source initialized');
            } catch (error) {
                console.warn('⚠️ Google Drive initialization failed, will use fallback');
                errorHandler.handleError({
                    type: 'initialization',
                    message: 'Google Drive API initialization failed',
                    error: error
                });
            }
        }

        // 로컬 데이터 소스 확인
        if (this.sources.local) {
            results.local = await this.checkLocalDataAvailability();
        }

        return results;
    }

    /**
     * 기간별 데이터 가져오기
     * @param {string} period - 기간 (예: '2025_08', 'today', 'month')
     * @param {Object} options - 옵션
     */
    async fetchData(period, options = {}) {
        // 캐시 확인
        const cacheKey = `${period}_${JSON.stringify(options)}`;
        const cachedData = this.getFromCache(cacheKey);
        if (cachedData && !options.forceRefresh) {
            console.log('📦 Using cached data');
            return cachedData;
        }

        let data = null;
        let source = null;

        // 1. Google Drive 시도
        if (this.sources.googleDrive && googleDriveAPI.isAuthenticated) {
            try {
                data = await this.fetchFromGoogleDrive(period, options);
                source = 'googleDrive';
            } catch (error) {
                console.warn('Google Drive fetch failed:', error);
            }
        }

        // 2. 로컬 파일 시도
        if (!data && this.sources.local) {
            try {
                data = await this.fetchFromLocal(period, options);
                source = 'local';
            } catch (error) {
                console.warn('Local fetch failed:', error);
            }
        }

        // 3. 폴백 데이터 사용
        if (!data && this.sources.fallback) {
            data = await this.getFallbackData(period);
            source = 'fallback';
        }

        if (data) {
            // 캐시에 저장
            this.saveToCache(cacheKey, data);
            
            // 소스 정보 추가
            data.source = source;
            data.fetchTime = new Date().toISOString();
            
            console.log(`✅ Data fetched from ${source}`);
            return data;
        }

        throw new Error(`No data available for period: ${period}`);
    }

    /**
     * Google Drive에서 데이터 가져오기
     * @param {string} period - 기간
     * @param {Object} options - 옵션
     */
    async fetchFromGoogleDrive(period, options) {
        // 기간 변환
        const periods = this.convertPeriodToMonths(period);
        
        // 여러 기간 데이터 로드
        const results = await googleDriveAPI.loadMultiplePeriods(periods);
        
        if (results.length === 0) {
            return null;
        }

        // 데이터 병합
        const mergedData = this.mergeDataResults(results);
        
        return {
            period: period,
            data: mergedData,
            metadata: {
                periods: periods,
                fileCount: results.length,
                totalRecords: mergedData.length
            }
        };
    }

    /**
     * 로컬 파일에서 데이터 가져오기
     * @param {string} period - 기간
     * @param {Object} options - 옵션
     */
    async fetchFromLocal(period, options) {
        const periods = this.convertPeriodToMonths(period);
        const allData = [];
        
        for (const monthKey of periods) {
            const paths = [
                `/data/qip_trainer_data_${monthKey}.json`,
                `./data/qip_trainer_data_${monthKey}.json`,
                `../data/qip_trainer_data_${monthKey}.json`
            ];

            for (const path of paths) {
                try {
                    const response = await fetch(path);
                    if (response.ok) {
                        const jsonData = await response.json();
                        if (jsonData.rawData && Array.isArray(jsonData.rawData)) {
                            allData.push(...jsonData.rawData);
                            console.log(`✅ Loaded local data: ${monthKey}`);
                            break;
                        }
                    }
                } catch (error) {
                    // 다음 경로 시도
                }
            }
        }

        if (allData.length === 0) {
            return null;
        }

        return {
            period: period,
            data: allData,
            metadata: {
                periods: periods,
                totalRecords: allData.length
            }
        };
    }

    /**
     * 기간을 월 단위로 변환
     * @param {string} period - 기간
     */
    convertPeriodToMonths(period) {
        const today = new Date();
        const currentYear = today.getFullYear();
        const currentMonth = today.getMonth() + 1;

        switch (period) {
            case 'today':
            case 'week':
            case 'month':
                // 현재 월 데이터만
                return [`${currentYear}_${String(currentMonth).padStart(2, '0')}`];
                
            case 'quarter':
            case '3months':
                // 최근 3개월
                const months = [];
                for (let i = 0; i < 3; i++) {
                    const date = new Date(currentYear, currentMonth - 1 - i, 1);
                    const year = date.getFullYear();
                    const month = date.getMonth() + 1;
                    months.push(`${year}_${String(month).padStart(2, '0')}`);
                }
                return months.reverse();
                
            default:
                // 특정 기간 (예: '2025_08')
                if (period.match(/^\d{4}_\d{2}$/)) {
                    return [period];
                }
                return [`${currentYear}_${String(currentMonth).padStart(2, '0')}`];
        }
    }

    /**
     * 데이터 결과 병합
     * @param {Array} results - 결과 배열
     */
    mergeDataResults(results) {
        const mergedData = [];
        
        for (const result of results) {
            if (result && result.data) {
                if (Array.isArray(result.data)) {
                    mergedData.push(...result.data);
                } else if (result.data.rawData && Array.isArray(result.data.rawData)) {
                    mergedData.push(...result.data.rawData);
                }
            }
        }
        
        return mergedData;
    }

    /**
     * 폴백 데이터 생성
     * @param {string} period - 기간
     */
    async getFallbackData(period) {
        console.warn('⚠️ Using fallback data');
        
        // 샘플 데이터 생성
        const sampleData = this.generateSampleData(period);
        
        return {
            period: period,
            data: sampleData,
            metadata: {
                isFallback: true,
                message: '실제 데이터를 사용할 수 없어 샘플 데이터를 표시합니다'
            }
        };
    }

    /**
     * 샘플 데이터 생성
     * @param {string} period - 기간
     */
    generateSampleData(period) {
        const data = [];
        const checkers = ['TQC001', 'TQC002', 'TQC003', 'TQC004', 'TQC005'];
        const results = ['Pass', 'Reject'];
        const lines = ['5PRS', '5PRE', '5PRW'];
        
        // 기간에 따른 데이터 수 결정
        let dataCount = 100;
        switch (period) {
            case 'today':
                dataCount = 50;
                break;
            case 'week':
                dataCount = 350;
                break;
            case 'month':
                dataCount = 1500;
                break;
            case 'quarter':
                dataCount = 4500;
                break;
        }
        
        for (let i = 0; i < dataCount; i++) {
            data.push({
                date: new Date(2025, 7, Math.floor(Math.random() * 30) + 1).toLocaleDateString(),
                line: lines[Math.floor(Math.random() * lines.length)],
                factory: '5PRE',
                pcs: `Sample Product ${i + 1}`,
                checker: checkers[Math.floor(Math.random() * checkers.length)],
                result: Math.random() > 0.03 ? 'Pass' : 'Reject',
                defects: Math.random() > 0.97 ? Math.floor(Math.random() * 3) + 1 : 0
            });
        }
        
        return data;
    }

    /**
     * 로컬 데이터 가용성 확인
     */
    async checkLocalDataAvailability() {
        try {
            const testPath = './data/metadata.json';
            const response = await fetch(testPath);
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    /**
     * 캐시에서 가져오기
     * @param {string} key - 캐시 키
     */
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached) {
            const age = Date.now() - cached.timestamp;
            if (age < this.cacheTimeout) {
                return cached.data;
            }
            // 만료된 캐시 제거
            this.cache.delete(key);
        }
        return null;
    }

    /**
     * 캐시에 저장
     * @param {string} key - 캐시 키
     * @param {*} data - 데이터
     */
    saveToCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
        
        // 캐시 크기 제한
        if (this.cache.size > 50) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }

    /**
     * 캐시 초기화
     */
    clearCache() {
        this.cache.clear();
        console.log('✅ Cache cleared');
    }

    /**
     * 데이터 스트림 (실시간 업데이트)
     * @param {string} period - 기간
     * @param {Function} callback - 콜백
     * @param {number} interval - 업데이트 간격 (ms)
     */
    streamData(period, callback, interval = 30000) {
        // 초기 데이터 로드
        this.fetchData(period).then(callback).catch(console.error);
        
        // 주기적 업데이트
        const intervalId = setInterval(async () => {
            try {
                const data = await this.fetchData(period, { forceRefresh: true });
                callback(data);
            } catch (error) {
                console.error('Stream update error:', error);
            }
        }, interval);
        
        // 정리 함수 반환
        return () => {
            clearInterval(intervalId);
        };
    }

    /**
     * 재시도 로직이 있는 fetch
     * @param {Function} fetchFn - fetch 함수
     * @param {number} attempts - 시도 횟수
     */
    async fetchWithRetry(fetchFn, attempts = this.retryAttempts) {
        for (let i = 0; i < attempts; i++) {
            try {
                return await fetchFn();
            } catch (error) {
                if (i === attempts - 1) {
                    throw error;
                }
                
                console.warn(`Retry attempt ${i + 1}/${attempts}`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay * (i + 1)));
            }
        }
    }
}

// 싱글톤 인스턴스 생성
const dataFetcher = new DataFetcher();

// 전역 객체에 추가 (디버깅용)
if (typeof window !== 'undefined') {
    window.dataFetcher = dataFetcher;
}

export default dataFetcher;