# Web Dashboard 배포 가이드

> **목적**: 이 문서는 QIP 인센티브 대시보드 프로젝트의 웹 기반 배포 구조를 설명하고, 다른 프로젝트에서 동일한 방식으로 웹 대시보드를 구축하고 **네비게이터를 통해 서로 연결**할 수 있도록 가이드를 제공합니다.

---

## 1. 아키텍처 개요

### 1.1 시스템 구성도

```
┌─────────────────────────────────────────────────────────────────────┐
│                         사용자 브라우저                               │
│  (Chrome, Safari, Firefox, Edge - 모바일/데스크탑)                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      GitHub Pages (무료 호스팅)                       │
│  URL: https://{username}.github.io/{repository}/                    │
├─────────────────────────────────────────────────────────────────────┤
│  /docs/                        ← GitHub Pages 루트 디렉토리          │
│  ├── index.html               ← 리다이렉트 (→ selector.html)         │
│  ├── auth.html                ← 비밀번호 인증 페이지                  │
│  ├── selector.html            ← 월 선택 네비게이터                    │
│  ├── Dashboard_2025_11.html   ← 대시보드 HTML (자체 완결형)           │
│  ├── *.csv, *.xlsx            ← 다운로드 파일                        │
│  └── *_SelfContained.html     ← 오프라인 버전                        │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │ 자동 배포 (30분마다)
                                 │
┌─────────────────────────────────────────────────────────────────────┐
│                      GitHub Actions (CI/CD)                          │
│  .github/workflows/auto-update.yml                                   │
├─────────────────────────────────────────────────────────────────────┤
│  1. Google Drive 데이터 동기화                                        │
│  2. 인센티브 계산 (Python)                                            │
│  3. 대시보드 HTML 생성                                                │
│  4. /docs 폴더에 파일 복사                                            │
│  5. Git commit & push → GitHub Pages 자동 배포                       │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │ API 호출
                                 │
┌─────────────────────────────────────────────────────────────────────┐
│                      Google Drive (데이터 소스)                       │
│  - 출근 데이터 (attendance)                                          │
│  - AQL 검사 데이터                                                   │
│  - 5PRS 검사 데이터                                                  │
│  - 기본 인력 정보                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 핵심 구성 요소

| 구성 요소 | 역할 | 기술 |
|----------|------|------|
| **GitHub Pages** | 무료 정적 웹 호스팅 | HTML, CSS, JS |
| **GitHub Actions** | 자동화된 CI/CD 파이프라인 | YAML, Python |
| **Google Drive** | 실시간 데이터 소스 | Google API |
| **Service Account** | API 인증 | JSON 키 파일 |

---

## 2. GitHub Pages 설정

### 2.1 저장소 설정

1. **GitHub 저장소 생성** (또는 기존 저장소 사용)
2. **Settings → Pages** 이동
3. **Source**: `Deploy from a branch` 선택
4. **Branch**: `main` / `/docs` 선택
5. **Save** 클릭

```
Settings → Pages → Source: Deploy from a branch
                   Branch: main / /docs
```

### 2.2 폴더 구조

```
project-root/
├── .github/
│   └── workflows/
│       └── auto-update.yml      ← GitHub Actions 워크플로우
├── docs/                        ← GitHub Pages 루트 (필수!)
│   ├── index.html               ← 진입점 (리다이렉트)
│   ├── auth.html                ← 인증 페이지
│   ├── selector.html            ← 네비게이터/선택 페이지
│   ├── Dashboard_*.html         ← 대시보드 파일들
│   ├── *.csv, *.xlsx            ← 다운로드 파일
│   └── .nojekyll                ← Jekyll 비활성화 (필수!)
├── src/                         ← Python 소스 코드
├── scripts/                     ← 유틸리티 스크립트
├── config_files/                ← 설정 JSON 파일
├── input_files/                 ← 입력 데이터
└── output_files/                ← 생성된 출력 파일
```

### 2.3 필수 파일: `.nojekyll`

GitHub Pages는 기본적으로 Jekyll을 사용합니다. `_`로 시작하는 파일/폴더를 무시하므로, 이를 비활성화해야 합니다.

```bash
# docs 폴더에 빈 .nojekyll 파일 생성
touch docs/.nojekyll
```

### 2.4 index.html (리다이렉트)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=selector.html">
    <title>대시보드</title>
</head>
<body>
    <p>월 선택 페이지로 이동 중...</p>
</body>
</html>
```

---

## 3. 인증 시스템 (auth.html)

### 3.1 보안 기능

| 기능 | 설명 |
|------|------|
| **SHA-256 해시** | 비밀번호를 해시로 저장 (평문 X) |
| **세션 타임아웃** | 30분 후 자동 로그아웃 |
| **로그인 시도 제한** | 5회 실패 시 5분 잠금 |
| **sessionStorage** | 브라우저 탭 닫으면 세션 종료 |

### 3.2 인증 흐름

```
사용자 접속
    │
    ▼
[index.html] → 리다이렉트 → [selector.html]
                                   │
                                   ▼
                           세션 확인 (validateSession)
                                   │
                    ┌──────────────┴──────────────┐
                    │                              │
              세션 유효                        세션 없음/만료
                    │                              │
                    ▼                              ▼
            대시보드 표시                    [auth.html]로 이동
                                                  │
                                                  ▼
                                           비밀번호 입력
                                                  │
                                    ┌─────────────┴─────────────┐
                                    │                            │
                              SHA-256 일치                   불일치
                                    │                            │
                                    ▼                            ▼
                            세션 생성 & 이동              시도 횟수 증가
                                                    (5회 실패 시 5분 잠금)
```

### 3.3 핵심 코드 (auth.html)

```javascript
// 보안 설정
const SECURITY_CONFIG = {
    PASSWORD_HASH: '19e49d5a0a97333a704097653034a76eaddb6cff5aeff18e4efec4c871d4caae', // SHA-256("qip")
    SESSION_TIMEOUT: 30 * 60 * 1000, // 30분
    MAX_ATTEMPTS: 5,
    LOCKOUT_TIME: 5 * 60 * 1000, // 5분
    SESSION_KEY: 'qip_auth_session',
    ATTEMPTS_KEY: 'qip_auth_attempts',
    LOCKOUT_KEY: 'qip_auth_lockout'
};

// SHA-256 해시 함수
async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// 세션 검증 함수 (다른 페이지에서 사용)
function validateSession() {
    const session = sessionStorage.getItem(SECURITY_CONFIG.SESSION_KEY);
    if (!session) return false;

    try {
        const sessionData = JSON.parse(session);
        const now = Date.now();

        if (now - sessionData.loginTime < SECURITY_CONFIG.SESSION_TIMEOUT) {
            return true;
        }
        sessionStorage.removeItem(SECURITY_CONFIG.SESSION_KEY);
        return false;
    } catch (e) {
        return false;
    }
}
```

### 3.4 대시보드에서 세션 검증

모든 보호된 페이지(selector.html, Dashboard.html)에 추가:

```javascript
// 페이지 로드 시 세션 검증
(function() {
    const SESSION_KEY = 'qip_auth_session';
    const SESSION_TIMEOUT = 30 * 60 * 1000;

    function validateSession() {
        const session = sessionStorage.getItem(SESSION_KEY);
        if (!session) return false;

        try {
            const data = JSON.parse(session);
            return (Date.now() - data.loginTime) < SESSION_TIMEOUT;
        } catch (e) {
            return false;
        }
    }

    if (!validateSession()) {
        window.location.href = 'auth.html';
    }
})();
```

---

## 4. 네비게이터 시스템 (selector.html)

### 4.1 구조

```html
<!-- 월 선택 카드 -->
<div class="month-cards-container">
    <a href="Dashboard_2025_11.html" class="month-card" data-month="11">
        <div class="month-year" data-lang-show="ko">2025년</div>
        <div class="month-name" data-i18n="month-11">11월</div>
        <button class="view-btn" data-i18n="view-btn">보기 →</button>
    </a>

    <a href="Dashboard_2025_10.html" class="month-card" data-month="10">
        <div class="month-year" data-lang-show="ko">2025년</div>
        <div class="month-name" data-i18n="month-10">10월</div>
        <button class="view-btn" data-i18n="view-btn">보기 →</button>
    </a>
    <!-- ... 추가 월 ... -->
</div>
```

### 4.2 다국어 지원

```javascript
const translations = {
    ko: {
        'page-title': 'QIP 인센티브 대시보드 - 월 선택',
        'header-title': '📊 QIP 인센티브 대시보드',
        'view-btn': '보기 →',
        'month-11': '11월',
        'month-10': '10월',
        // ...
    },
    en: {
        'page-title': 'QIP Incentive Dashboard - Select Month',
        'header-title': '📊 QIP Incentive Dashboard',
        'view-btn': 'View →',
        'month-11': 'November 2025',
        'month-10': 'October 2025',
        // ...
    },
    vi: {
        'page-title': 'Bảng điều khiển Khuyến khích QIP - Chọn Tháng',
        'header-title': '📊 Bảng điều khiển Khuyến khích QIP',
        'view-btn': 'Xem →',
        'month-11': 'Tháng 11 năm 2025',
        'month-10': 'Tháng 10 năm 2025',
        // ...
    }
};

function switchLanguage(lang) {
    localStorage.setItem('preferredLanguage', lang);
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            el.innerHTML = translations[lang][key];
        }
    });
}
```

---

## 5. GitHub Actions 자동화

### 5.1 워크플로우 파일 (.github/workflows/auto-update.yml)

```yaml
name: 🔄 Auto Update Dashboard

on:
  schedule:
    - cron: '*/30 * * * *'  # 30분마다 실행
  workflow_dispatch:         # 수동 실행 가능
  push:
    branches: [main]
    paths:
      - 'integrated_dashboard_final.py'
      - 'scripts/*.py'

permissions:
  contents: write
  pages: write

jobs:
  update-dashboard:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
      with:
        persist-credentials: true
        fetch-depth: 0

    - name: 🐍 Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: 📚 Install dependencies
      run: |
        pip install pandas numpy openpyxl google-auth google-api-python-client

    - name: 📥 Download from Google Drive
      env:
        GOOGLE_SERVICE_ACCOUNT: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}
        GDRIVE_FOLDER_ID: ${{ secrets.GDRIVE_FOLDER_ID }}
      run: python scripts/download_from_gdrive.py

    - name: 💰 Calculate & Generate Dashboard
      run: |
        python scripts/auto_calculate_incentives.py
        python scripts/generate_dashboard.py

    - name: 📂 Prepare GitHub Pages
      run: |
        mkdir -p docs
        cp output_files/*.html docs/
        cp output_files/*.csv docs/
        cp output_files/*.xlsx docs/
        python scripts/create_month_selector.py

    - name: 📤 Commit and push
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/
        git commit -m "🔄 Auto update dashboard $(date '+%Y-%m-%d %H:%M')" || exit 0
        git push
```

### 5.2 GitHub Secrets 설정

**Settings → Secrets and variables → Actions** 에서 설정:

| Secret Name | 값 |
|-------------|-----|
| `GOOGLE_SERVICE_ACCOUNT` | Service Account JSON 키 전체 내용 |
| `GDRIVE_FOLDER_ID` | Google Drive 폴더 ID |

### 5.3 Service Account JSON 형식

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "dashboard@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

---

## 6. 다중 대시보드 연결 (네비게이터 통합)

### 6.1 목표 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                       통합 네비게이터 (Portal)                        │
│  URL: https://username.github.io/portal/                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │ QIP 대시보드  │    │ 품질 대시보드 │    │ 생산 대시보드 │             │
│  │  (Project A) │    │  (Project B) │    │  (Project C) │             │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘             │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ qip-dashboard/  │  │ quality-dash/   │  │ production-dash/│
│ GitHub Pages    │  │ GitHub Pages    │  │ GitHub Pages    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 6.2 통합 네비게이터 구현 (portal.html)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>대시보드 포털</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .portal-header {
            text-align: center;
            color: white;
            margin-bottom: 50px;
        }
        .portal-title {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .dashboard-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .dashboard-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }
        .card-icon { font-size: 3rem; margin-bottom: 15px; }
        .card-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 10px; }
        .card-description { color: #666; margin-bottom: 20px; }
        .card-status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        .status-live { background: #d4edda; color: #155724; }
    </style>
</head>
<body>
    <div class="portal-header">
        <div class="portal-title">📊 대시보드 포털</div>
        <p style="color: rgba(255,255,255,0.7);">원하시는 대시보드를 선택하세요</p>
    </div>

    <div class="dashboard-grid">
        <!-- QIP 인센티브 대시보드 -->
        <a href="https://moonkaicuzui.github.io/qip-dashboard/" class="dashboard-card" target="_blank">
            <div class="card-icon">💰</div>
            <div class="card-title">QIP 인센티브 대시보드</div>
            <div class="card-description">품질검사 인센티브 관리 및 현황 분석</div>
            <span class="card-status status-live">🟢 실시간 운영중</span>
        </a>

        <!-- 품질 대시보드 (예시) -->
        <a href="https://moonkaicuzui.github.io/quality-dashboard/" class="dashboard-card" target="_blank">
            <div class="card-icon">🔍</div>
            <div class="card-title">품질 관리 대시보드</div>
            <div class="card-description">품질 지표 및 불량률 분석</div>
            <span class="card-status status-live">🟢 실시간 운영중</span>
        </a>

        <!-- 생산 대시보드 (예시) -->
        <a href="https://moonkaicuzui.github.io/production-dashboard/" class="dashboard-card" target="_blank">
            <div class="card-icon">🏭</div>
            <div class="card-title">생산 현황 대시보드</div>
            <div class="card-description">일일 생산량 및 효율 분석</div>
            <span class="card-status status-live">🟢 실시간 운영중</span>
        </a>
    </div>
</body>
</html>
```

### 6.3 각 대시보드에 포털 링크 추가

각 대시보드의 헤더에 "포털로 돌아가기" 버튼 추가:

```html
<!-- selector.html 또는 대시보드 헤더에 추가 -->
<a href="https://moonkaicuzui.github.io/portal/" class="portal-link">
    🏠 대시보드 포털로 이동
</a>
```

### 6.4 동일 인증 공유 (선택사항)

여러 대시보드가 같은 인증을 공유하려면:

```javascript
// 모든 대시보드에서 동일한 SESSION_KEY 사용
const SHARED_SESSION_KEY = 'company_dashboard_session';

// 또는 localStorage 사용 (도메인 간 공유 시)
// 주의: 같은 도메인(*.github.io)에서만 공유 가능
localStorage.setItem(SHARED_SESSION_KEY, JSON.stringify({
    loginTime: Date.now(),
    validated: true
}));
```

---

## 7. 새 프로젝트 체크리스트

### 7.1 초기 설정

- [ ] GitHub 저장소 생성
- [ ] `/docs` 폴더 생성
- [ ] `docs/.nojekyll` 파일 생성
- [ ] GitHub Pages 활성화 (Settings → Pages → Source: main / /docs)
- [ ] Python 스크립트 작성 (데이터 처리, 대시보드 생성)

### 7.2 인증 설정

- [ ] `docs/auth.html` 복사 및 수정
- [ ] 비밀번호 해시 변경 (SHA-256)
- [ ] SESSION_KEY 변경 (프로젝트별 고유값)

### 7.3 네비게이터 설정

- [ ] `docs/selector.html` 생성 (월/일/카테고리 선택)
- [ ] `docs/index.html` 리다이렉트 설정
- [ ] 다국어 번역 추가 (필요시)

### 7.4 자동화 설정

- [ ] `.github/workflows/auto-update.yml` 작성
- [ ] GitHub Secrets 설정 (GOOGLE_SERVICE_ACCOUNT, GDRIVE_FOLDER_ID)
- [ ] Google Cloud 프로젝트 생성 및 Service Account 키 발급
- [ ] Google Drive API 활성화
- [ ] 데이터 폴더에 Service Account 이메일 공유 권한 추가

### 7.5 포털 연동

- [ ] 통합 포털 저장소 생성 (또는 기존 포털에 추가)
- [ ] 포털 페이지에 새 대시보드 카드 추가
- [ ] 새 대시보드에 포털 링크 추가
- [ ] 교차 인증 테스트 (필요시)

---

## 8. URL 구조 예시

```
통합 포털:
https://moonkaicuzui.github.io/portal/

QIP 대시보드:
https://moonkaicuzui.github.io/qip-dashboard/
https://moonkaicuzui.github.io/qip-dashboard/selector.html
https://moonkaicuzui.github.io/qip-dashboard/Incentive_Dashboard_2025_11_Version_9.0.html

품질 대시보드 (새 프로젝트):
https://moonkaicuzui.github.io/quality-dashboard/
https://moonkaicuzui.github.io/quality-dashboard/selector.html
https://moonkaicuzui.github.io/quality-dashboard/Quality_Dashboard_2025_12.html

생산 대시보드 (새 프로젝트):
https://moonkaicuzui.github.io/production-dashboard/
https://moonkaicuzui.github.io/production-dashboard/selector.html
https://moonkaicuzui.github.io/production-dashboard/Production_Dashboard_2025_12.html
```

---

## 9. 트러블슈팅

### 9.1 GitHub Pages가 업데이트되지 않음

```bash
# 해결방법
1. Settings → Pages 에서 Source 확인 (main / /docs)
2. .nojekyll 파일 존재 확인
3. GitHub Actions 로그 확인
4. 브라우저 캐시 삭제 또는 시크릿 모드에서 확인
```

### 9.2 GitHub Actions 실패

```bash
# 확인사항
1. Secrets 설정 확인 (GOOGLE_SERVICE_ACCOUNT)
2. Service Account 키 JSON 형식 확인
3. Google Drive 폴더 권한 확인 (Service Account 이메일에 공유)
4. Python 의존성 확인 (requirements.txt)
```

### 9.3 인증 문제

```bash
# sessionStorage 확인
sessionStorage.getItem('qip_auth_session')

# localStorage 확인 (잠금 상태)
localStorage.getItem('qip_auth_lockout')

# 강제 세션 생성 (개발용)
sessionStorage.setItem('qip_auth_session', JSON.stringify({loginTime: Date.now()}))
```

---

## 10. 참고 자료

- [GitHub Pages 공식 문서](https://docs.github.com/en/pages)
- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Google Drive API 문서](https://developers.google.com/drive/api/v3/quickstart/python)
- [Web Crypto API (SHA-256)](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest)

---

**작성일**: 2025-12-15
**버전**: 1.0
**프로젝트**: QIP 인센티브 대시보드
**저자**: Claude Code (Anthropic)
