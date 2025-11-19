# 🌐 QIP Incentive Dashboard - 웹 배포 프로젝트 정체성

**최종 업데이트:** 2025-11-19
**프로젝트 타입:** GitHub Pages 기반 실시간 웹 대시보드

---

## 🎯 프로젝트 핵심 정체성

### ✅ 이 프로젝트는:
```
실시간 인터넷 웹기반 인센티브 대시보드
GitHub Pages Auto-Deploy 시스템
Google Drive 연동 자동 업데이트
```

### ❌ 이 프로젝트는 아닙니다:
```
로컬 HTML 파일 생성기
오프라인 대시보드
수동 업데이트 시스템
```

---

## 🌐 웹 배포 정보

### 공식 웹 주소
```
https://moonkaicuzui.github.io/qip-dashboard/
```

**접속 방법:**
1. 웹 브라우저 열기 (Chrome, Safari, Firefox, Edge 등)
2. 위 URL 입력 또는 북마크
3. 인터넷 연결 필요 (모바일/데스크톱 모두 가능)

**선택기 페이지:**
```
https://moonkaicuzui.github.io/qip-dashboard/selector.html
```

**월별 대시보드 (직접 접근):**
```
https://moonkaicuzui.github.io/qip-dashboard/Incentive_Dashboard_2025_11_Version_9.0.html
https://moonkaicuzui.github.io/qip-dashboard/Incentive_Dashboard_2025_10_Version_9.0.html
...
```

---

## 🔄 자동 배포 시스템

### GitHub Actions Workflow
**파일:** `.github/workflows/auto-update.yml`

**실행 주기:** 매시간 자동 실행 (Cron: `0 * * * *`)

**자동 업데이트 프로세스:**
```
1. Google Drive에서 최신 데이터 동기화 (src/auto_run_with_drive.py)
2. 인센티브 계산 실행 (src/step1_인센티브_계산_개선버전.py)
3. 대시보드 HTML 생성 (integrated_dashboard_final.py)
4. Selector 페이지 재생성 (scripts/create_month_selector.py)
5. docs/ 폴더에 빌드 산출물 저장
6. Git commit & push
7. GitHub Pages 자동 배포 (1-2분 소요)
```

**결과:**
- 매시간 웹사이트가 최신 데이터로 자동 업데이트
- 수동 개입 없이 실시간 운영

---

## 📁 디렉토리 구조 (웹 배포 관점)

### `/docs` - GitHub Pages 웹 루트
```
docs/
├── selector.html                          # 웹 시작 페이지 ← 웹 서빙
├── Incentive_Dashboard_2025_11_Version_9.0.html  # 11월 대시보드 ← 웹 서빙
├── Incentive_Dashboard_2025_10_Version_9.0.html  # 10월 대시보드 ← 웹 서빙
├── output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv   # 다운로드용
├── output_QIP_incentive_november_2025_Complete_V9.0_Complete.xlsx  # 다운로드용
└── auth.html                              # 인증 페이지 ← 웹 서빙
```

**중요:**
- `/docs` 폴더의 모든 HTML 파일은 **웹에서 접근 가능**
- GitHub Pages 설정: `Settings > Pages > Source: docs/ folder`
- 로컬 파일이 아닌 **웹 배포 산출물**

### `/src` - 빌드 스크립트 (웹에 노출 안 됨)
```
src/
├── step1_인센티브_계산_개선버전.py      # 인센티브 계산 엔진
├── auto_run_with_drive.py              # Google Drive 동기화
├── sync_previous_incentive.py          # 이전 달 데이터 동기화
└── ...
```

### `/scripts` - 유틸리티 스크립트 (웹에 노출 안 됨)
```
scripts/
├── create_month_selector.py            # selector.html 생성기
├── verification/                       # 데이터 검증 스크립트
└── ...
```

### `/input_files` - 소스 데이터 (웹에 노출 안 됨)
```
input_files/
├── basic manpower data november.csv
├── attendance/
├── AQL history/
└── 5prs data november.csv
```

### `/output_files` - 계산 결과 (웹 배포 전 단계)
```
output_files/
├── output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv
└── output_QIP_incentive_november_2025_Complete_V9.0_Complete.xlsx
```
→ 이 파일들이 `/docs`로 복사되어 웹 다운로드 가능

---

## 🔐 웹 보안 및 접근 제어

### 인증 시스템
**파일:** `docs/auth.html`

**기능:**
- SHA-256 해시 기반 비밀번호 인증
- 세션 쿠키 (30분 유효)
- 5회 실패 시 5분 잠금

**인증 흐름:**
```
1. https://moonkaicuzui.github.io/qip-dashboard/ 접속
2. auth.html로 자동 리다이렉트
3. 비밀번호 입력
4. 인증 성공 → selector.html로 이동
5. 세션 쿠키로 30분간 자유롭게 탐색
```

---

## 📊 웹 대시보드 기능

### 1. 월 선택기 (selector.html)
- 사용 가능한 모든 월 대시보드 표시
- 다국어 지원 (한국어/English/Vietnamese)
- 빨간색 테마
- 버전 중복 제거 (최신 버전만 표시)

### 2. 월별 대시보드 (Incentive_Dashboard_*.html)
- **인터랙티브 차트:** Chart.js 기반 시각화
- **다국어 전환:** 실시간 언어 변경 (KO/EN/VN)
- **데이터 다운로드:** Excel/CSV/HTML 파일 다운로드
- **직원 검색:** Employee No 또는 이름으로 검색
- **상세 모달:** 개별 직원 인센티브 상세 정보
- **통계 대시보드:** KPI, 분포도, 조건별 분석

### 3. 반응형 디자인
- 모바일 최적화 (375px ~ 768px)
- 태블릿 지원 (768px ~ 1024px)
- 데스크톱 (1024px+)

---

## 🚀 배포 프로세스

### 수동 배포 (필요시)
```bash
# 1. 인센티브 계산 실행
./action.sh

# 2. 대시보드 생성
python integrated_dashboard_final.py --month 11 --year 2025

# 3. Selector 재생성
python scripts/create_month_selector.py

# 4. Git commit & push
git add docs/
git commit -m "Update November 2025 dashboard"
git push origin main

# 5. GitHub Pages 자동 배포 (1-2분 대기)
```

### 자동 배포 (권장)
```
Git push → GitHub Actions 실행 → 자동 배포
```

---

## 🔍 웹 vs 로컬 파일 명확한 구분

| 항목 | 웹 배포 (Production) | 로컬 파일 (Development) |
|-----|---------------------|----------------------|
| **접근 방법** | 웹 브라우저 + 인터넷 | 파일 탐색기 |
| **URL** | `https://ksmooncoding.github.io/...` | `file:///Users/...` |
| **업데이트** | GitHub Actions 자동 | 수동 스크립트 실행 |
| **사용 목적** | 최종 사용자 접근 | 개발 및 테스트 |
| **파일 위치** | `/docs` (GitHub Pages 서빙) | 전체 프로젝트 |
| **데이터 최신성** | 매시간 자동 | 수동 실행 시점 |

**중요:**
- 사용자가 "웹 주소"를 물으면 → `https://moonkaicuzui.github.io/qip-dashboard/`
- 로컬 `file:///` 경로는 **개발용**이며 최종 사용자에게 제공하지 않음

---

## 📱 모바일 접근

### iOS/Android
```
1. 모바일 브라우저 (Safari, Chrome) 열기
2. https://moonkaicuzui.github.io/qip-dashboard/ 입력
3. 인증 후 대시보드 사용
4. 홈 화면에 추가 가능 (웹앱처럼 사용)
```

### 홈 화면 추가 (iOS)
```
1. Safari에서 웹사이트 열기
2. 공유 버튼 → "홈 화면에 추가"
3. 아이콘 생성 → 앱처럼 실행
```

---

## 🔄 Google Drive 연동

### 실시간 데이터 동기화
**스크립트:** `src/auto_run_with_drive.py`

**동기화 파일:**
```
Google Drive → Local:
1. Basic manpower data
2. Attendance data
3. AQL history
4. 5PRS data
5. Previous month incentive data
```

**동기화 주기:**
- GitHub Actions: 매시간
- 수동 실행: `./action.sh`

---

## 📊 웹 트래픽 및 성능

### 파일 크기
- `selector.html`: ~18 KB
- `Incentive_Dashboard_2025_11_Version_9.0.html`: ~4.9 MB

### 로딩 성능
- 초기 로딩: ~2-3초 (3G)
- 캐싱 후: ~500ms (WiFi)
- 모바일 최적화: ✅

### 브라우저 지원
- Chrome 90+
- Safari 14+
- Firefox 88+
- Edge 90+

---

## 🛠️ 문제 해결

### "웹사이트에 접속할 수 없음"
1. 인터넷 연결 확인
2. GitHub Pages 상태 확인: https://www.githubstatus.com
3. URL 정확성 확인: `https://ksmooncoding.github.io/...`

### "대시보드 데이터가 오래됨"
1. GitHub Actions 실행 확인: `.github/workflows/auto-update.yml`
2. 마지막 커밋 시간 확인
3. 브라우저 캐시 삭제 (Ctrl+Shift+R / Cmd+Shift+R)

### "로컬 파일로 열림"
- **잘못됨**: `file:///Users/...`
- **올바름**: `https://ksmooncoding.github.io/...`

---

## 📌 핵심 요약

### 프로젝트 정체성
```
✅ GitHub Pages 웹 배포 프로젝트
✅ 실시간 자동 업데이트 대시보드
✅ 인터넷 접근 필수
✅ 모바일/데스크톱 반응형
```

### 웹 주소 (Production)
```
https://moonkaicuzui.github.io/qip-dashboard/
```

### 로컬 파일 (Development Only)
```
/docs/*.html  ← 웹 배포 산출물
file:///... ← 개발 및 테스트 전용
```

### 자동화
```
Google Drive → GitHub Actions → 웹 배포
매시간 자동 실행
```

---

**결론:** 이 프로젝트는 **실시간 인터넷 웹기반 인센티브 대시보드**입니다. 로컬 파일은 개발 과정의 부산물이며, 최종 사용자는 항상 웹 URL로 접근합니다.

**웹 주소:** https://moonkaicuzui.github.io/qip-dashboard/

---

**작성:** Claude Code - Project Identity Redefinition
**최종 검토:** 2025-11-19
