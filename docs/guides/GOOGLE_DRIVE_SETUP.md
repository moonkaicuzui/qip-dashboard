# Google Drive API 설정 가이드

## 📋 설정 단계

### 1. Google Cloud Console 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 프로젝트 이름: `QIP-Trainer-Dashboard`

### 2. Google Drive API 활성화

1. 왼쪽 메뉴에서 **API 및 서비스** > **라이브러리** 선택
2. "Google Drive API" 검색
3. **사용 설정** 클릭

### 3. OAuth 2.0 클라이언트 ID 생성

1. **API 및 서비스** > **사용자 인증 정보** 이동
2. **사용자 인증 정보 만들기** > **OAuth 클라이언트 ID** 선택
3. 애플리케이션 유형: **웹 애플리케이션**
4. 설정:
   ```
   이름: QIP Trainer Dashboard
   승인된 JavaScript 원본:
   - http://localhost:8889
   - http://localhost:8888
   - https://your-domain.com (프로덕션 도메인)
   
   승인된 리디렉션 URI:
   - http://localhost:8889/callback
   - https://your-domain.com/callback
   ```
5. **만들기** 클릭

### 4. API 키 생성

1. **사용자 인증 정보 만들기** > **API 키** 선택
2. API 키 제한사항 설정:
   - 애플리케이션 제한사항: HTTP 리퍼러
   - 웹사이트 제한사항:
     ```
     http://localhost:8889/*
     http://localhost:8888/*
     https://your-domain.com/*
     ```
   - API 제한사항: Google Drive API만 선택

### 5. 클라이언트 설정

`src/api/googleDriveAPI.js` 파일에서 다음 값 업데이트:

```javascript
class GoogleDriveAPI {
    constructor() {
        this.CLIENT_ID = 'YOUR_CLIENT_ID.apps.googleusercontent.com';
        this.API_KEY = 'YOUR_API_KEY';
        // ...
    }
}
```

또는 환경 변수 파일 생성 (`.env`):

```
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GOOGLE_API_KEY=YOUR_API_KEY
```

### 6. Google Drive 폴더 구조

권장 폴더 구조:
```
📁 QIP Trainer Data (루트 폴더)
  ├── 📁 2025
  │   ├── 📄 qip_trainer_data_2025_07.json
  │   ├── 📄 qip_trainer_data_2025_08.json
  │   ├── 📄 qip_trainer_data_2025_09.json
  │   └── 📄 metadata.json
  ├── 📁 backups
  └── 📁 exports
```

### 7. 데이터 파일 형식

#### JSON 형식 (권장)
```json
{
  "metadata": {
    "version": "1.0",
    "created": "2025-09-11",
    "period": "2025_08"
  },
  "rawData": [
    {
      "date": "8/1/2025",
      "line": "5PRS",
      "factory": "5PRE",
      "pcs": "Air Jordan 1 Retro High OG",
      "checker": "TQC001",
      "result": "Pass",
      "defects": 0
    }
  ]
}
```

#### CSV 형식 (대안)
```csv
date,line,factory,pcs,checker,result,defects
8/1/2025,5PRS,5PRE,Air Jordan 1 Retro High OG,TQC001,Pass,0
```

## 🔐 보안 고려사항

### 필수 보안 설정

1. **API 키 보호**
   - 절대 공개 저장소에 커밋하지 않음
   - 환경 변수 사용
   - `.gitignore`에 추가

2. **도메인 제한**
   - API 키에 도메인 제한 설정
   - OAuth 리디렉션 URI 검증

3. **권한 최소화**
   - 읽기 전용 권한만 요청
   - 필요한 폴더만 접근

4. **토큰 관리**
   - 액세스 토큰 안전한 저장
   - 자동 갱신 구현

## 🧪 테스트

### 연결 테스트
```javascript
// 브라우저 콘솔에서 실행
async function testGoogleDrive() {
    try {
        await googleDriveAPI.initialize();
        await googleDriveAPI.signIn();
        
        const files = await googleDriveAPI.listFiles({
            pageSize: 10
        });
        
        console.log('Files:', files);
    } catch (error) {
        console.error('Test failed:', error);
    }
}

testGoogleDrive();
```

### 데이터 로드 테스트
```javascript
async function testDataLoad() {
    try {
        const data = await googleDriveAPI.loadQIPTrainerData('2025_08');
        console.log('Data loaded:', data);
    } catch (error) {
        console.error('Data load failed:', error);
    }
}

testDataLoad();
```

## 📝 환경별 설정

### 개발 환경
```javascript
const config = {
    development: {
        clientId: 'DEV_CLIENT_ID',
        apiKey: 'DEV_API_KEY',
        folderId: 'DEV_FOLDER_ID'
    }
};
```

### 프로덕션 환경
```javascript
const config = {
    production: {
        clientId: process.env.GOOGLE_CLIENT_ID,
        apiKey: process.env.GOOGLE_API_KEY,
        folderId: process.env.GOOGLE_FOLDER_ID
    }
};
```

## 🚨 일반적인 오류 해결

### 1. "401 Unauthorized"
- API 키 확인
- OAuth 토큰 만료 → 재로그인

### 2. "403 Forbidden"
- API 활성화 확인
- 도메인 제한 설정 확인

### 3. "404 Not Found"
- 파일/폴더 ID 확인
- 권한 확인

### 4. CORS 오류
- 승인된 JavaScript 원본 확인
- 로컬 개발 시 http://localhost:포트 추가

## 📚 참고 자료

- [Google Drive API 문서](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth 2.0 가이드](https://developers.google.com/identity/protocols/oauth2)
- [JavaScript 클라이언트 라이브러리](https://github.com/google/google-api-javascript-client)

---
*작성일: 2025-09-11*
*버전: 1.0*