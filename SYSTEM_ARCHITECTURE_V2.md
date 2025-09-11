# 5PRS 대시보드 시스템 아키텍처 v2.0

## 📋 개요

새로운 시스템 구조는 Google Drive 접근과 대시보드 실행을 분리하여 보안과 성능을 개선했습니다.

## 🏗️ 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                      action_v2.sh                            │
│                   (메인 실행 스크립트)                         │
└─────────────┬───────────────────────────────────────────────┘
              │
              ├─── Step 1: Google Drive 다운로드
              │     └── src/download_5prs_from_drive.py
              │         ├── Google Drive API 인증
              │         ├── 월별 5PRS 파일 검색
              │         └── input_files/5prs/ 로 다운로드
              │
              ├─── Step 2: 데이터 통합
              │     └── src/integrate_5prs_data.py
              │         ├── 다운로드된 파일들 읽기
              │         ├── 데이터 표준화 및 병합
              │         └── output_files/dashboards/5prs/data/ 에 JSON 저장
              │
              └─── Step 3: 대시보드 생성
                    └── src/generate_5prs_dashboard_v2.py
                        ├── 통합 JSON 데이터 로드
                        ├── HTML 대시보드 생성
                        └── output_files/dashboards/5prs/ 에 저장
```

## 📁 디렉토리 구조

```
/대시보드 인센티브 테스트10_정리/
│
├── action_v2.sh                    # 메인 실행 스크립트
│
├── /src/
│   ├── download_5prs_from_drive.py # Google Drive 다운로더
│   ├── integrate_5prs_data.py      # 데이터 통합기
│   └── generate_5prs_dashboard_v2.py # 대시보드 생성기
│
├── /input_files/
│   └── /5prs/                      # Google Drive에서 다운로드된 원본 파일
│       ├── 5prs data august.csv
│       ├── 5prs_data_2025_08_0.xlsx
│       └── ...
│
├── /output_files/
│   └── /dashboards/
│       └── /5prs/
│           ├── /data/              # 통합된 JSON 데이터
│           │   └── integrated_5prs_2025_08.json
│           └── 5prs_dashboard_2025_08.html  # 최종 대시보드
│
├── credentials.json                # Google API 인증 파일 (필요시)
└── token.json                      # 인증 토큰 (자동 생성)
```

## 🔧 주요 컴포넌트

### 1. action_v2.sh
- **역할**: 전체 프로세스 오케스트레이션
- **기능**:
  - 사용자 인터페이스 (년도/월 선택)
  - 단계별 실행 및 에러 처리
  - 결과 확인 및 대시보드 열기

### 2. download_5prs_from_drive.py
- **역할**: Google Drive에서 데이터 다운로드
- **기능**:
  - Google OAuth 2.0 인증
  - 파일 검색 (다양한 패턴 지원)
  - 파일 다운로드 및 저장
  - 폴백 데이터 생성 (옵션)

### 3. integrate_5prs_data.py
- **역할**: 다운로드된 데이터 통합
- **기능**:
  - 다양한 형식 지원 (CSV, Excel, JSON)
  - 컬럼명 표준화
  - 중복 제거 및 데이터 정제
  - 통계 및 차트 데이터 생성

### 4. generate_5prs_dashboard_v2.py
- **역할**: HTML 대시보드 생성
- **기능**:
  - 통합 데이터 로드
  - 반응형 HTML 생성
  - Chart.js 차트 구현
  - 통계 카드 및 테이블 생성

## 🚀 실행 방법

### 1. 기본 실행
```bash
./action_v2.sh
```

### 2. 개별 단계 실행

#### Google Drive 다운로드만
```bash
python3 src/download_5prs_from_drive.py --month august --year 2025
```

#### 데이터 통합만
```bash
python3 src/integrate_5prs_data.py --month august --year 2025
```

#### 대시보드 생성만
```bash
python3 src/generate_5prs_dashboard_v2.py --month august --year 2025
```

## 🔑 Google Drive 설정

### 1. Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성
3. Google Drive API 활성화
4. OAuth 2.0 클라이언트 ID 생성
5. `credentials.json` 다운로드

### 2. 인증 파일 위치
```
/대시보드 인센티브 테스트10_정리/
├── credentials.json  # Google Cloud Console에서 다운로드
└── token.json       # 첫 실행 시 자동 생성
```

### 3. 필요한 권한
- Google Drive 읽기 권한 (`drive.readonly`)

## 📊 데이터 흐름

```
Google Drive
     ↓
[다운로드] → input_files/5prs/*.csv
     ↓
[통합] → output_files/dashboards/5prs/data/integrated_*.json
     ↓
[생성] → output_files/dashboards/5prs/5prs_dashboard_*.html
     ↓
브라우저에서 열기
```

## ⚙️ 설정 옵션

### 폴백 모드
Google Drive 접근 실패 시 샘플 데이터 사용:
```bash
python3 src/download_5prs_from_drive.py --month august --year 2025 --fallback
```

### 파일 패턴 커스터마이징
`download_5prs_from_drive.py`의 patterns 리스트 수정:
```python
patterns = [
    f"5prs data {month}",
    f"5PRS_{month}_{year}",
    f"qip_trainer_data_{year}_{month_num:02d}",
    # 추가 패턴...
]
```

## 🔒 보안 고려사항

1. **토큰 관리**
   - `token.json`은 `.gitignore`에 추가
   - 정기적으로 토큰 갱신

2. **권한 최소화**
   - 읽기 전용 권한만 요청
   - 필요한 폴더만 접근

3. **로컬 캐싱**
   - 다운로드된 파일은 로컬에 캐싱
   - 대시보드는 로컬 파일만 사용

## 📈 성능 최적화

1. **병렬 다운로드** (향후 구현)
2. **증분 동기화** (변경된 파일만)
3. **데이터 압축** (대용량 파일)
4. **캐시 활용** (반복 접근 최소화)

## 🐛 문제 해결

### Google Drive 인증 실패
```
문제: "credentials.json not found"
해결: Google Cloud Console에서 OAuth 2.0 클라이언트 ID 다운로드
```

### 데이터 파일을 찾을 수 없음
```
문제: "No files found for august 2025"
해결: Google Drive의 파일명 패턴 확인 또는 --fallback 옵션 사용
```

### 대시보드 표시 오류
```
문제: 차트가 표시되지 않음
해결: 브라우저 콘솔에서 JavaScript 에러 확인
```

## 📝 로그 파일

- 실행 로그: 콘솔 출력
- 에러 로그: `logs/drive_sync.log` (생성 예정)

## 🔄 업데이트 이력

- **v2.0** (2025-09-11): 초기 버전
  - Google Drive 다운로드 분리
  - 로컬 데이터 통합
  - 독립적인 대시보드 생성

---
*작성일: 2025-09-11*
*버전: 2.0*