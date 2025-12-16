# 무료 웹 기반 대시보드 구현 가이드

## 개요

이 문서는 QIP 인센티브 대시보드 프로젝트가 **100% 무료**로 실시간 웹 기반 시스템을 구현한 방법을 설명합니다. 다른 프로젝트에서 벤치마킹할 수 있도록 전체 아키텍처와 구현 방법을 상세히 기술합니다.

## 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        무료 웹 대시보드 아키텍처                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐   │
│  │ Google Drive │───▶│GitHub Actions│───▶│    GitHub Pages          │   │
│  │   (데이터)    │    │  (자동화)     │    │   (웹 호스팅)             │   │
│  │   무료 15GB   │    │ 무료 2000분/월│    │    무료 무제한            │   │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘   │
│         │                   │                        │                   │
│         │                   ▼                        ▼                   │
│         │           ┌──────────────┐         ┌──────────────┐           │
│         │           │Python 스크립트│         │ 정적 HTML    │           │
│         │           │ - 데이터 처리 │         │ - 대시보드   │           │
│         └──────────▶│ - 계산 로직  │────────▶│ - 인증 페이지│           │
│                     │ - HTML 생성  │         │ - 셀렉터     │           │
│                     └──────────────┘         └──────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 사용된 무료 서비스

| 서비스 | 용도 | 무료 한도 | 실제 사용량 |
|--------|------|----------|------------|
| **GitHub Pages** | 웹 호스팅 | 1GB 저장, 100GB/월 트래픽 | ~10MB |
| **GitHub Actions** | CI/CD 자동화 | 2,000분/월 | ~300분/월 |
| **Google Drive** | 데이터 저장소 | 15GB | ~50MB |
| **Google Drive API** | 데이터 동기화 | 1억 쿼리/일 | ~400 쿼리/일 |

### 총 비용: **$0/월** (영구 무료)

---

## 1. GitHub Pages 웹 호스팅

### 1.1 설정 방법

```yaml
# 저장소 Settings > Pages
Source: Deploy from a branch
Branch: main
Folder: /docs
```

### 1.2 폴더 구조

```
/docs/                          # GitHub Pages 루트
├── index.html                  # 리다이렉트 (→ selector.html)
├── auth.html                   # 로그인 페이지
├── selector.html               # 월 선택 페이지
├── admin.html                  # 관리자 페이지
├── robots.txt                  # 검색엔진 차단
├── Incentive_Dashboard_*.html  # 월별 대시보드
├── *.csv                       # 다운로드용 데이터
└── *.xlsx                      # 다운로드용 Excel
```

### 1.3 URL 구조

```
기본 URL: https://{username}.github.io/{repo-name}/
예시:     https://moonkaicuzui.github.io/qip-dashboard/
```

### 1.4 장점

- **무료 HTTPS**: SSL 인증서 자동 제공
- **전역 CDN**: GitHub의 CDN으로 빠른 로딩
- **무제한 트래픽**: 합리적 사용 범위 내 무제한
- **커스텀 도메인**: 자체 도메인 연결 가능

---

## 2. GitHub Actions 자동화

### 2.1 워크플로우 구조

```yaml
# .github/workflows/auto-update.yml

name: Auto Update Dashboard

on:
  schedule:
    - cron: '0 * * * *'  # 매시간 실행
  workflow_dispatch:      # 수동 실행 가능

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Download from Google Drive
        env:
          GOOGLE_SERVICE_ACCOUNT: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}
        run: python scripts/download_from_gdrive.py

      - name: Calculate Incentives
        run: python scripts/auto_calculate_incentives.py

      - name: Generate Dashboard
        run: python integrated_dashboard_final.py --month $MONTH --year $YEAR

      - name: Deploy to GitHub Pages
        run: |
          cp output_files/*.html docs/
          cp output_files/*.csv docs/
          git add docs/
          git commit -m "Auto update dashboard"
          git push
```

### 2.2 핵심 단계 설명

| 단계 | 설명 | 소요 시간 |
|------|------|----------|
| Download CSV | Google Drive에서 최신 데이터 다운로드 | ~30초 |
| Convert Attendance | 출근부 데이터 변환 | ~10초 |
| Calculate | 인센티브 계산 (Python) | ~60초 |
| Generate HTML | Self-contained 대시보드 생성 | ~30초 |
| Deploy | GitHub Pages 자동 배포 | ~60초 |

### 2.3 비밀 설정 (Secrets)

```yaml
# 저장소 Settings > Secrets and variables > Actions

GOOGLE_SERVICE_ACCOUNT: {서비스 계정 JSON 전체 내용}
```

---

## 3. Google Drive 데이터 동기화

### 3.1 서비스 계정 설정

1. **Google Cloud Console** (https://console.cloud.google.com)
2. 프로젝트 생성
3. Google Drive API 활성화
4. 서비스 계정 생성
5. JSON 키 다운로드
6. Google Drive 폴더 공유 (서비스 계정 이메일에 권한 부여)

### 3.2 폴더 구조

```
Google Drive/
└── QIP Dashboard Data/
    ├── monthly_data/           # 월별 데이터
    │   ├── attendance data november.csv
    │   ├── basic manpower data november.csv
    │   └── 5prs data november.csv
    ├── aql_history/            # AQL 이력
    │   └── 1.HSRG AQL REPORT-NOVEMBER.2025.csv
    └── configs/                # 설정 파일
```

### 3.3 Python 다운로드 코드

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io, os, json

# 서비스 계정 인증
credentials = service_account.Credentials.from_service_account_info(
    json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT']),
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)
service = build('drive', 'v3', credentials=credentials)

# 파일 다운로드
def download_file(file_id, output_path):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(output_path, 'wb') as f:
        f.write(fh.getvalue())

# 폴더 내 파일 목록 조회
def list_files(folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, modifiedTime)"
    ).execute()
    return results.get('files', [])
```

### 3.4 API 비용 분석

```
일일 쿼리 수: ~400개
- 파일 목록 조회: ~10개
- 파일 다운로드: ~20개
- 메타데이터 조회: ~10개
× 24시간 = ~400개

Google Drive API 무료 한도: 1,000,000,000 쿼리/일
사용률: 0.00004%

결론: 영구 무료
```

---

## 4. 클라이언트 사이드 인증

### 4.1 인증 흐름

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ auth.html│────▶│ selector │────▶│Dashboard │
│  (로그인) │     │  (선택)   │     │  (조회)  │
└──────────┘     └──────────┘     └──────────┘
     │                │                │
     ▼                ▼                ▼
┌─────────────────────────────────────────┐
│         sessionStorage 세션 검증          │
│  - 인증 상태                              │
│  - 로그인 시간                            │
│  - 브라우저 핑거프린트                     │
│  - 30분 타임아웃                          │
└─────────────────────────────────────────┘
```

### 4.2 보안 기능

```javascript
// 비밀번호 해시 (SHA-256)
async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    return Array.from(new Uint8Array(hashBuffer))
        .map(b => b.toString(16).padStart(2, '0')).join('');
}

// 브라우저 핑거프린트
function getBrowserFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = '14px Arial';
    ctx.fillText('fp', 2, 2);
    const fp = canvas.toDataURL().slice(-50);
    return btoa(navigator.userAgent + screen.width + screen.height + fp);
}

// 세션 검증
function validateSession() {
    const session = sessionStorage.getItem('qip_auth_session_v2');
    if (!session) return false;

    const data = JSON.parse(session);
    const now = Date.now();

    // 타임아웃 확인 (30분)
    if (now - data.loginTime > 30 * 60 * 1000) return false;

    // 핑거프린트 확인
    if (data.fingerprint !== getBrowserFingerprint()) return false;

    return true;
}
```

### 4.3 로그인 시도 제한

```javascript
const MAX_ATTEMPTS = 3;
const LOCKOUT_TIME = 15 * 60 * 1000; // 15분

function recordAttempt() {
    const attempts = parseInt(localStorage.getItem('attempts') || '0') + 1;
    localStorage.setItem('attempts', attempts);

    if (attempts >= MAX_ATTEMPTS) {
        const lockoutUntil = Date.now() + LOCKOUT_TIME;
        localStorage.setItem('lockout', lockoutUntil);
        return true; // 잠금
    }
    return false;
}
```

### 4.4 보안 한계 및 대응

| 한계 | 설명 | 대응 방안 |
|------|------|----------|
| 클라이언트 사이드 | 코드가 브라우저에 노출됨 | 해시 난독화, 다층 방어 |
| 세션 조작 가능 | 개발자 도구로 수정 가능 | 핑거프린트 바인딩 |
| 직접 URL 접근 | HTML 파일 직접 접근 가능 | 세션 검증 필수 |

**참고**: 정적 호스팅의 근본적 한계로, 민감한 데이터는 서버 사이드 인증이 필요합니다.

---

## 5. Self-Contained HTML 대시보드

### 5.1 개념

모든 리소스(CSS, JS, 데이터)를 단일 HTML 파일에 인라인으로 포함하여 독립 실행 가능하게 만듦.

### 5.2 구조

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Bootstrap CSS 인라인 */
        /* Custom CSS 인라인 */
    </style>
</head>
<body>
    <!-- 대시보드 HTML -->

    <script>
        // Chart.js 인라인
        // D3.js 인라인
        // 대시보드 데이터 인라인
        window.employeeData = [...];
        window.summaryData = {...};
        // 대시보드 로직
    </script>
</body>
</html>
```

### 5.3 생성 방법

```python
def generate_self_contained_html(data, output_path):
    # CDN 리소스 로드
    bootstrap_css = requests.get('https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css').text
    chart_js = requests.get('https://cdn.jsdelivr.net/npm/chart.js').text

    # HTML 템플릿에 인라인
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>{bootstrap_css}</style>
    </head>
    <body>
        {dashboard_html}
        <script>{chart_js}</script>
        <script>
            window.employeeData = {json.dumps(data['employees'])};
            // ... 대시보드 로직
        </script>
    </body>
    </html>
    """

    with open(output_path, 'w') as f:
        f.write(html)
```

### 5.4 파일 크기

| 항목 | 크기 |
|------|------|
| Bootstrap CSS | ~150KB |
| Chart.js | ~200KB |
| D3.js | ~280KB |
| 대시보드 데이터 | ~500KB |
| 대시보드 로직 | ~300KB |
| **총계** | **~1.5MB** (gzip: ~400KB) |

---

## 6. 다국어 지원

### 6.1 번역 데이터 구조

```javascript
const translations = {
    ko: {
        'header-title': '📊 QIP 인센티브 대시보드',
        'view-btn': '보기 →',
        'month-11': '11월',
        // ...
    },
    en: {
        'header-title': '📊 QIP Incentive Dashboard',
        'view-btn': 'View →',
        'month-11': 'November 2025',
        // ...
    },
    vi: {
        'header-title': '📊 Bảng điều khiển Khuyến khích QIP',
        'view-btn': 'Xem →',
        'month-11': 'Tháng 11 năm 2025',
        // ...
    }
};
```

### 6.2 HTML 태그 방식

```html
<span data-i18n="header-title">📊 QIP 인센티브 대시보드</span>
<button data-i18n="view-btn">보기 →</button>
```

### 6.3 언어 전환 함수

```javascript
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

## 7. 검색엔진 차단

### 7.1 robots.txt

```
User-agent: *
Disallow: /

User-agent: Googlebot
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: Claude-Web
Disallow: /
```

### 7.2 Meta 태그

```html
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
<meta name="googlebot" content="noindex, nofollow">
```

---

## 8. 프로젝트 적용 체크리스트

### 8.1 필수 준비물

- [ ] GitHub 계정
- [ ] Google Cloud 프로젝트 (서비스 계정)
- [ ] 데이터 소스 (Google Drive 또는 기타)

### 8.2 설정 단계

1. [ ] GitHub 저장소 생성
2. [ ] `/docs` 폴더 생성 (GitHub Pages 루트)
3. [ ] GitHub Pages 활성화 (Settings > Pages)
4. [ ] Google Cloud 서비스 계정 생성
5. [ ] GitHub Secrets에 서비스 계정 JSON 추가
6. [ ] GitHub Actions 워크플로우 작성
7. [ ] 인증 페이지 생성 (auth.html)
8. [ ] 대시보드 생성 스크립트 작성
9. [ ] 테스트 및 배포

### 8.3 유지보수

- 매시간 자동 업데이트 (GitHub Actions)
- Google Drive 데이터만 업데이트하면 자동 반영
- 코드 수정 시 자동 재배포

---

## 9. 비용 요약

| 항목 | 월 비용 |
|------|--------|
| 웹 호스팅 | $0 (GitHub Pages) |
| CI/CD | $0 (GitHub Actions) |
| 데이터 저장 | $0 (Google Drive) |
| API 호출 | $0 (무료 한도 내) |
| SSL 인증서 | $0 (GitHub 제공) |
| CDN | $0 (GitHub CDN) |
| **총계** | **$0/월** |

---

## 10. 참고 링크

- [GitHub Pages 문서](https://docs.github.com/pages)
- [GitHub Actions 문서](https://docs.github.com/actions)
- [Google Drive API](https://developers.google.com/drive/api)
- [Google Cloud Console](https://console.cloud.google.com)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-12-16 | 1.0 | 최초 작성 |

---

**작성**: QIP Dashboard Team
**목적**: 다른 프로젝트 벤치마킹용 기술 문서
