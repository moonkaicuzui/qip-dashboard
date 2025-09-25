# 5PRS Dashboard 실행 가이드

## 🚀 빠른 시작

### 1. 기본 실행
```bash
./5prs.sh
```

### 2. 실행 권한 설정 (처음 한 번만)
```bash
chmod +x 5prs.sh
```

## 📋 실행 단계별 설명

### Step 1: 5prs.sh 실행
```bash
cd /Users/ksmoon/Downloads/대시보드\ 인센티브\ 테스트10_정리
./5prs.sh
```

### Step 2: 년도 선택
```
📅 년도를 선택하세요:
  1) 2025년
  2) 2026년
선택 (1 또는 2): 1
```

### Step 3: 월 선택
```
📅 월을 선택하세요:
  1) 1월   7) 7월
  2) 2월   8) 8월
  3) 3월   9) 9월
  4) 4월   10) 10월
  5) 5월   11) 11월
  6) 6월   12) 12월
선택 (1-12): 8
```

### Step 4: 확인
```
선택: 2025년 8월

다음 작업을 수행합니다:
  1. Google Drive에서 5PRS 데이터 다운로드
  2. 월별 데이터 통합
  3. 대시보드 생성 및 업데이트

계속하시겠습니까? (y/n): y
```

### Step 5: 자동 실행
스크립트가 자동으로 다음 작업을 수행합니다:
1. ✅ 디렉토리 구조 확인
2. 📥 Google Drive에서 데이터 다운로드
3. 🔄 데이터 통합
4. 📊 대시보드 생성

### Step 6: 완료
```
🎉 모든 작업이 완료되었습니다!

대시보드를 브라우저에서 열어보시겠습니까? (y/n): y
```

## 🔧 고급 사용법

### 개별 단계 실행

#### 1. Google Drive 다운로드만
```bash
python3 src/download_5prs_from_drive.py --month august --year 2025
```

#### 2. 데이터 통합만
```bash
python3 src/integrate_5prs_data.py --month august --year 2025
```

#### 3. 대시보드 생성만
```bash
python3 src/generate_5prs_dashboard_v2.py --month august --year 2025
```

### 폴백 모드 (Google Drive 접근 불가 시)
```bash
python3 src/download_5prs_from_drive.py --month august --year 2025 --fallback
```

## 📁 생성되는 파일

### 입력 파일 (다운로드)
```
input_files/5prs/
├── 5prs data august.csv
├── 5prs_data_2025_08_0.xlsx
└── basic manpower data august.csv
```

### 출력 파일 (생성)
```
output_files/dashboards/5prs/
├── data/
│   └── integrated_5prs_2025_08.json
└── 5prs_dashboard_2025_08.html
```

## 🔍 문제 해결

### 1. Permission denied 오류
```bash
# 해결 방법
chmod +x 5prs.sh
```

### 2. Python3 not found
```bash
# 해결 방법 (macOS)
brew install python3

# 확인
python3 --version
```

### 3. Google Drive 인증 실패
```
문제: credentials.json not found
해결: 
1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성
2. credentials.json 다운로드
3. 프로젝트 루트에 저장
```

### 4. 데이터 파일을 찾을 수 없음
```
문제: No data files found for august 2025
해결:
1. Google Drive에 파일이 있는지 확인
2. 파일명 패턴 확인 (5prs data august.csv)
3. --fallback 옵션으로 샘플 데이터 사용
```

## 📊 대시보드 확인

### 자동 열기
스크립트 실행 완료 후 "y"를 선택하면 자동으로 브라우저에서 열립니다.

### 수동 열기
```bash
# macOS
open output_files/dashboards/5prs/5prs_dashboard_2025_08.html

# 또는 브라우저에서 직접 열기
```

### 대시보드 URL (로컬 서버 실행 시)
```
http://localhost:8889/output_files/dashboards/5prs/5prs_dashboard_2025_08.html
```

## 🌟 주요 기능

1. **자동화된 데이터 수집**
   - Google Drive에서 월별 5PRS 데이터 자동 다운로드
   - 다양한 파일 형식 지원 (CSV, Excel, JSON)

2. **데이터 통합**
   - 여러 파일 자동 병합
   - 컬럼명 표준화
   - 중복 제거 및 정제

3. **대시보드 생성**
   - 반응형 HTML 대시보드
   - 실시간 차트 (Chart.js)
   - 통계 요약 카드
   - 상위 검사원 테이블

## 📝 로그 확인

### 실행 로그
```bash
# 콘솔에 실시간 출력됨
```

### 상세 로그 (디버깅용)
```bash
# Python 스크립트 직접 실행 시 상세 로그 확인 가능
python3 src/download_5prs_from_drive.py --month august --year 2025
```

## 🔄 정기 실행 설정 (선택사항)

### cron을 이용한 자동 실행
```bash
# crontab 편집
crontab -e

# 매월 1일 오전 9시에 실행 (예시)
0 9 1 * * cd /Users/ksmoon/Downloads/대시보드\ 인센티브\ 테스트10_정리 && echo "1\n8\ny\ny" | ./5prs.sh
```

## 💡 팁

1. **빠른 테스트**: 폴백 모드로 샘플 데이터 사용
2. **오프라인 작업**: 한 번 다운로드 후 로컬 데이터로 계속 작업
3. **데이터 백업**: input_files/5prs 폴더 백업 권장

## 📞 지원

문제가 발생하면:
1. 이 가이드의 문제 해결 섹션 확인
2. 로그 메시지 확인
3. 필요시 개발팀 문의

---
*버전: 2.0*
*최종 업데이트: 2025-09-11*