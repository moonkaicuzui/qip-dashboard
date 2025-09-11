/**
 * Google Drive API Integration Module
 * Google Drive와의 데이터 동기화를 담당
 * @module googleDriveAPI
 */

class GoogleDriveAPI {
    constructor() {
        this.CLIENT_ID = ''; // Google Cloud Console에서 발급
        this.API_KEY = ''; // Google Cloud Console에서 발급
        this.DISCOVERY_DOCS = ['https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'];
        this.SCOPES = 'https://www.googleapis.com/auth/drive.readonly';
        
        this.isInitialized = false;
        this.isAuthenticated = false;
        this.authInstance = null;
        this.currentUser = null;
        this.listeners = new Set();
    }

    /**
     * Google API 초기화
     */
    async initialize() {
        try {
            // Google API 라이브러리 로드
            await this.loadGoogleAPI();
            
            // 클라이언트 초기화
            await gapi.client.init({
                apiKey: this.API_KEY,
                clientId: this.CLIENT_ID,
                discoveryDocs: this.DISCOVERY_DOCS,
                scope: this.SCOPES
            });

            // 인증 인스턴스 가져오기
            this.authInstance = gapi.auth2.getAuthInstance();
            
            // 로그인 상태 리스너 등록
            this.authInstance.isSignedIn.listen(this.updateSigninStatus.bind(this));
            
            // 초기 로그인 상태 확인
            this.updateSigninStatus(this.authInstance.isSignedIn.get());
            
            this.isInitialized = true;
            console.log('✅ Google Drive API initialized');
            
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize Google Drive API:', error);
            throw new Error('Google Drive API 초기화 실패: ' + error.message);
        }
    }

    /**
     * Google API 라이브러리 동적 로드
     */
    loadGoogleAPI() {
        return new Promise((resolve, reject) => {
            // 이미 로드되어 있으면 즉시 반환
            if (window.gapi) {
                resolve();
                return;
            }

            // 스크립트 태그 생성
            const script = document.createElement('script');
            script.src = 'https://apis.google.com/js/api.js';
            script.async = true;
            script.defer = true;
            
            script.onload = () => {
                // gapi 로드 후 client 로드
                gapi.load('client:auth2', () => {
                    resolve();
                });
            };
            
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * 로그인 상태 업데이트
     */
    updateSigninStatus(isSignedIn) {
        this.isAuthenticated = isSignedIn;
        
        if (isSignedIn) {
            this.currentUser = this.authInstance.currentUser.get();
            const profile = this.currentUser.getBasicProfile();
            console.log(`✅ Logged in as: ${profile.getName()}`);
            
            // 리스너에게 알림
            this.notifyListeners('authenticated', {
                user: {
                    id: profile.getId(),
                    name: profile.getName(),
                    email: profile.getEmail(),
                    imageUrl: profile.getImageUrl()
                }
            });
        } else {
            this.currentUser = null;
            console.log('❌ Not logged in');
            this.notifyListeners('unauthenticated', null);
        }
    }

    /**
     * 사용자 로그인
     */
    async signIn() {
        try {
            if (!this.isInitialized) {
                await this.initialize();
            }
            
            await this.authInstance.signIn();
            return true;
        } catch (error) {
            console.error('❌ Sign in failed:', error);
            throw new Error('로그인 실패: ' + error.message);
        }
    }

    /**
     * 사용자 로그아웃
     */
    async signOut() {
        try {
            await this.authInstance.signOut();
            return true;
        } catch (error) {
            console.error('❌ Sign out failed:', error);
            throw new Error('로그아웃 실패: ' + error.message);
        }
    }

    /**
     * 파일 목록 가져오기
     * @param {Object} options - 검색 옵션
     */
    async listFiles(options = {}) {
        if (!this.isAuthenticated) {
            throw new Error('인증이 필요합니다');
        }

        try {
            const params = {
                pageSize: options.pageSize || 100,
                fields: 'nextPageToken, files(id, name, mimeType, modifiedTime, size)',
                orderBy: options.orderBy || 'modifiedTime desc'
            };

            // 검색 쿼리 추가
            if (options.query) {
                params.q = options.query;
            } else if (options.folderId) {
                params.q = `'${options.folderId}' in parents`;
            }

            const response = await gapi.client.drive.files.list(params);
            return response.result.files || [];
        } catch (error) {
            console.error('❌ Failed to list files:', error);
            throw new Error('파일 목록 조회 실패: ' + error.message);
        }
    }

    /**
     * 특정 파일 내용 가져오기
     * @param {string} fileId - 파일 ID
     */
    async getFileContent(fileId) {
        if (!this.isAuthenticated) {
            throw new Error('인증이 필요합니다');
        }

        try {
            // 파일 메타데이터 가져오기
            const fileResponse = await gapi.client.drive.files.get({
                fileId: fileId,
                fields: 'id, name, mimeType, modifiedTime'
            });

            const file = fileResponse.result;
            
            // 파일 내용 가져오기
            const contentResponse = await gapi.client.drive.files.get({
                fileId: fileId,
                alt: 'media'
            });

            // JSON 파일인 경우 파싱
            if (file.mimeType === 'application/json') {
                return {
                    metadata: file,
                    content: JSON.parse(contentResponse.body)
                };
            }

            // CSV 파일인 경우
            if (file.mimeType === 'text/csv') {
                return {
                    metadata: file,
                    content: this.parseCSV(contentResponse.body)
                };
            }

            // 기타 텍스트 파일
            return {
                metadata: file,
                content: contentResponse.body
            };
        } catch (error) {
            console.error('❌ Failed to get file content:', error);
            throw new Error('파일 내용 조회 실패: ' + error.message);
        }
    }

    /**
     * QIP Trainer 데이터 파일 찾기 및 로드
     * @param {string} period - 기간 (예: '2025_08')
     */
    async loadQIPTrainerData(period) {
        try {
            // QIP Trainer 데이터 파일 검색
            const query = `name contains 'qip_trainer_data_${period}' and (mimeType='application/json' or mimeType='text/csv')`;
            
            const files = await this.listFiles({ query });
            
            if (files.length === 0) {
                console.warn(`⚠️ No data files found for period: ${period}`);
                return null;
            }

            // 가장 최근 파일 선택
            const latestFile = files[0];
            console.log(`📁 Loading file: ${latestFile.name}`);
            
            // 파일 내용 가져오기
            const fileData = await this.getFileContent(latestFile.id);
            
            return {
                metadata: fileData.metadata,
                data: fileData.content
            };
        } catch (error) {
            console.error('❌ Failed to load QIP Trainer data:', error);
            throw error;
        }
    }

    /**
     * 여러 기간의 데이터 로드
     * @param {Array} periods - 기간 배열
     */
    async loadMultiplePeriods(periods) {
        const results = [];
        
        for (const period of periods) {
            try {
                const data = await this.loadQIPTrainerData(period);
                if (data) {
                    results.push(data);
                }
            } catch (error) {
                console.error(`Failed to load data for ${period}:`, error);
            }
        }
        
        return results;
    }

    /**
     * CSV 파싱
     * @param {string} text - CSV 텍스트
     */
    parseCSV(text) {
        const lines = text.split('\n').filter(line => line.trim());
        const headers = lines[0].split(',').map(h => h.trim());
        
        return lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, i) => {
                row[header] = values[i] || '';
            });
            return row;
        });
    }

    /**
     * 폴더 내 파일 동기화
     * @param {string} folderId - 폴더 ID
     */
    async syncFolder(folderId) {
        try {
            // 폴더 내 모든 JSON/CSV 파일 가져오기
            const query = `'${folderId}' in parents and (mimeType='application/json' or mimeType='text/csv')`;
            const files = await this.listFiles({ query });
            
            console.log(`📂 Found ${files.length} files in folder`);
            
            const syncedData = [];
            for (const file of files) {
                try {
                    const content = await this.getFileContent(file.id);
                    syncedData.push({
                        file: file,
                        content: content
                    });
                } catch (error) {
                    console.error(`Failed to sync file ${file.name}:`, error);
                }
            }
            
            return syncedData;
        } catch (error) {
            console.error('❌ Folder sync failed:', error);
            throw error;
        }
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
     * @param {string} event - 이벤트 이름
     * @param {*} data - 데이터
     */
    notifyListeners(event, data) {
        this.listeners.forEach(callback => {
            try {
                callback(event, data);
            } catch (error) {
                console.error('Listener error:', error);
            }
        });
    }

    /**
     * 파일 변경 감지 (폴링)
     * @param {string} fileId - 파일 ID
     * @param {Function} callback - 변경 시 콜백
     * @param {number} interval - 폴링 간격 (ms)
     */
    watchFile(fileId, callback, interval = 30000) {
        let lastModifiedTime = null;
        
        const checkForChanges = async () => {
            try {
                const response = await gapi.client.drive.files.get({
                    fileId: fileId,
                    fields: 'modifiedTime'
                });
                
                const currentModifiedTime = response.result.modifiedTime;
                
                if (lastModifiedTime && lastModifiedTime !== currentModifiedTime) {
                    // 파일이 변경됨
                    const content = await this.getFileContent(fileId);
                    callback(content);
                }
                
                lastModifiedTime = currentModifiedTime;
            } catch (error) {
                console.error('Watch file error:', error);
            }
        };
        
        // 초기 체크
        checkForChanges();
        
        // 주기적 체크
        const intervalId = setInterval(checkForChanges, interval);
        
        // 정리 함수 반환
        return () => {
            clearInterval(intervalId);
        };
    }

    /**
     * API 설정 업데이트
     * @param {Object} config - 설정 객체
     */
    updateConfig(config) {
        if (config.clientId) {
            this.CLIENT_ID = config.clientId;
        }
        if (config.apiKey) {
            this.API_KEY = config.apiKey;
        }
        
        // 재초기화 필요
        this.isInitialized = false;
    }
}

// 싱글톤 인스턴스 생성
const googleDriveAPI = new GoogleDriveAPI();

// 전역 객체에 추가 (디버깅용)
if (typeof window !== 'undefined') {
    window.googleDriveAPI = googleDriveAPI;
}

export default googleDriveAPI;