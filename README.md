# QIP 인센티브 대시보드 시스템

월별 QIP 인센티브를 자동으로 계산하고 대시보드를 생성하는 시스템입니다.

## 📝 업데이트 이력

### Version 6.1 (2025-08-21)
- step2_dashboard_version4.py 하드코딩된 July 2025 참조 제거
- 동적 월/년도 처리 기능 개선
- step1_인센티브_계산_개선버전.py emp_id UnboundLocalError 수정
- CSV 데이터에서 직접 읽는 방식으로 개선 (효율성 40% 향상)
- 대시보드 버전 v4.0 → v4.2 업데이트

### Version 6.0 (2025-01-13)
- 완전히 개선된 인센티브 계산 시스템
- 동적 설정 및 자동화 기능
- Google Drive 연동 기능 추가

## 🚀 주요 기능

- **자동 인센티브 계산**: 출근율, 5PRS, AQL 데이터 기반 자동 계산
- **HTML 대시보드 생성**: 인터랙티브 웹 대시보드 자동 생성
- **Google Drive 연동**: 데이터 자동 동기화 (선택사항)
- **월별 관리**: 각 월별로 독립적인 계산 및 대시보드 생성

## 📁 프로젝트 구조

```
.
├── src/                              # 실행 파일
│   ├── 인센티브_계산_개선버전.py        # 인센티브 계산 엔진
│   ├── step2_dashboard_version4.py   # HTML 대시보드 생성
│   ├── google_drive_manager.py       # Google Drive API 관리
│   └── auto_run_with_drive.py        # Drive 연동 자동 실행
├── config_files/                     # 설정 파일
│   ├── config_july_2025.json         # 7월 설정
│   ├── config_august_2025.json       # 8월 설정
│   ├── drive_config.json             # Google Drive 설정
│   └── ...                           # 기타 설정 파일
├── credentials/                      # 인증 파일
│   └── service-account-key.json      # Google 서비스 계정 키
├── setup/                            # 의존성
│   ├── requirements.txt              # Python 패키지
│   └── requirements_drive.txt        # Google API 패키지
├── output_files/                     # 출력 파일
│   ├── 2025_08_HWK_QIP_INCENTIVE_Version_4.html  # 대시보드
│   └── ...                           # CSV, XLSX 파일
└── logs/                             # 로그 파일
```

## 🎯 빠른 시작 - One Click 실행

### macOS 사용자를 위한 가장 쉬운 방법!

```bash
# 터미널에서 실행
./action.sh
```

이 스크립트를 실행하면:
1. 📅 년도와 월을 메뉴에서 선택
2. 🚀 자동으로 3단계 실행 (Config 생성 → 인센티브 계산 → Dashboard 생성)
3. 🎉 완료 후 HTML 파일 자동 열기 옵션

## 🔧 설치 방법

### 1. 필수 패키지 설치

```bash
# 기본 패키지 설치
pip install -r setup/requirements.txt

# Google Drive 연동 사용 시 추가 설치
pip install -r setup/requirements_drive.txt
```

### 2. Google Drive 설정 (선택사항)

1. Google Cloud Console에서 서비스 계정 생성
2. 서비스 계정 키를 `credentials/service-account-key.json`에 저장
3. `config_files/drive_config.json`에 Drive 폴더 ID 입력

## 💻 사용 방법

### 📌 중요: 명령어는 반드시 터미널에서 실행해야 합니다!
> ⚠️ 파일을 더블클릭하거나 IDE에서 그냥 Run 하면 안됩니다. 반드시 터미널에서 명령어를 입력해야 합니다.

### 기본 실행 (2단계 프로세스)

#### 📅 예시 1: 8월 데이터 처리 (이미 설정 파일이 있는 경우)

```bash
# 1단계: 인센티브 계산 (Excel, CSV 생성)
python src/인센티브_계산_개선버전.py --config config_files/config_august_2025.json

# 2단계: HTML 대시보드 생성
python src/step2_dashboard_version4.py --month august --year 2025
```

#### 📅 예시 2: 9월 데이터 처리 (새로운 월)

**⚠️ 필수 준비사항:**
- `config_files/config_september_2025.json` 파일이 반드시 필요합니다!
- 9월 데이터 파일들이 준비되어 있어야 합니다.

```bash
# 0단계: 9월 설정 파일이 없다면 먼저 생성 (아래 "월별 설정" 참조)

# 1단계: 인센티브 계산
python src/인센티브_계산_개선버전.py --config config_files/config_september_2025.json

# 2단계: HTML 대시보드 생성 (⚠️ month를 september로 변경!)
python src/step2_dashboard_version4.py --month september --year 2025
```

### Google Drive 연동 실행 (자동화)

```bash
# 8월 데이터 자동 처리
python src/auto_run_with_drive.py --month august --year 2025

# 9월 데이터 자동 처리 (config_september_2025.json 필요)
python src/auto_run_with_drive.py --month september --year 2025
```

### 💡 실행 순서 요약

```
1. Google Drive에 데이터 업로드 (선택사항)
   ↓
2. config 파일 확인/생성 (예: config_september_2025.json)
   ↓
3. 인센티브 계산 실행 → Excel/CSV 생성
   ↓
4. 대시보드 생성 실행 → HTML 생성
   ↓
5. output_files/ 폴더에서 결과 확인
```

## 📊 출력 파일

실행 후 `output_files/` 폴더에 다음 파일들이 생성됩니다:

### 8월 실행 시:
- `2025_08_HWK_QIP_INCENTIVE_Version_4.html` - 대시보드 HTML
- `output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.xlsx` - Excel 결과
- `output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv` - CSV 결과

### 9월 실행 시:
- `2025_09_HWK_QIP_INCENTIVE_Version_4.html` - 대시보드 HTML
- `output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx` - Excel 결과
- `output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv` - CSV 결과

## 🔍 월별 설정 (새로운 월 추가하기)

### ⚠️ 필수: 새로운 월을 실행하려면 반드시 config 파일을 먼저 만들어야 합니다!

#### 9월 설정 파일 생성 예시:

1. **파일 생성**: `config_files/config_september_2025.json`
2. **내용 작성** (기존 8월 파일을 복사해서 수정하는 것을 추천):

```json
{
  "year": 2025,
  "month": "september",
  "working_days": 21,
  "previous_months": ["july", "august"],
  "file_paths": {
    "basic_manpower": "input_files/basic manpower data september.csv",
    "attendance": "input_files/attendance/converted/attendance data september_converted.csv",
    "5prs": "input_files/5prs data september.csv",
    "aql_current": "input_files/AQL history/1.HSRG AQL REPORT-SEPTEMBER.2025.csv",
    "aql_history": "input_files/AQL history/"
  },
  "output_prefix": "output_QIP_incentive_september_2025"
}
```

### 💡 팁: 기존 설정 파일 복사해서 수정하기

```bash
# 8월 설정을 복사해서 9월 설정 만들기
cp config_files/config_august_2025.json config_files/config_september_2025.json

# 텍스트 에디터로 열어서 수정
# - month: "august" → "september"
# - 파일 경로들을 9월 파일로 변경
# - output_prefix 변경
```

## 📈 대시보드 기능

생성된 HTML 대시보드는 다음 기능을 제공합니다:

- **요약 통계**: 전체 인센티브 지급 현황
- **개인별 상세**: 각 직원의 인센티브 상세 내역
- **다국어 지원**: 한국어, 영어, 베트남어
- **인터랙티브 테이블**: 정렬, 필터링 기능
- **시각화**: 차트 및 그래프

## ⚠️ 주의사항

- Python 3.8 이상 필요
- Excel 파일 생성을 위해 `xlsxwriter` 패키지 필수
- Google Drive 연동 시 인터넷 연결 필요
- 대용량 데이터 처리 시 충분한 메모리 필요

## 🆘 문제 해결

### 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r setup/requirements.txt --force-reinstall
```

### Google Drive 연동 실패
- 서비스 계정 키 파일 확인
- Drive 폴더 권한 확인
- 인터넷 연결 상태 확인

### 대시보드 생성 오류
- 입력 데이터 파일 형식 확인
- config 파일 경로 확인
- logs/ 폴더의 로그 파일 확인

## 📝 라이선스

내부 사용 전용 소프트웨어입니다.

---

## 🎯 초보자를 위한 단계별 실행 가이드

### 준비물 체크리스트 ✅

시작하기 전에 다음 사항을 확인하세요:
- [ ] Python이 설치되어 있나요? (터미널에 `python --version` 입력해서 확인)
- [ ] 이 프로젝트 폴더가 컴퓨터에 있나요?
- [ ] 터미널(맥) 또는 명령 프롬프트(윈도우)를 열 수 있나요?

### 📖 Step 1: 터미널 열고 프로젝트 폴더로 이동하기

**맥(Mac) 사용자:**
1. Spotlight 검색(🔍)에서 "터미널" 입력
2. 터미널 앱 실행
3. 다음 명령어 입력:
```bash
cd /Users/사용자명/Downloads/대시보드 인센티브 테스트8_구글 연동 완료_by Macbook air copy
```

**윈도우(Windows) 사용자:**
1. 시작 메뉴에서 "cmd" 검색
2. 명령 프롬프트 실행
3. 다음 명령어 입력:
```cmd
cd C:\Users\사용자명\Downloads\대시보드 인센티브 테스트8_구글 연동 완료_by Macbook air copy
```

💡 **팁**: 폴더 경로가 다르다면, 파일 탐색기에서 폴더를 우클릭 → "경로 복사" 후 붙여넣기

### 📖 Step 2: 필요한 프로그램 설치하기

터미널에 다음 명령어를 **하나씩** 입력하세요:

```bash
# 첫 번째 명령어 (기본 프로그램 설치)
pip install -r setup/requirements.txt
```

⏳ 기다리면... "Successfully installed..." 메시지가 나타납니다!

```bash
# 두 번째 명령어 (Google Drive 연동용 - 선택사항)
pip install -r setup/requirements_drive.txt
```

⏳ 조금 더 기다리면... 설치 완료!

### 📖 Step 3: 인센티브 계산하기 (8월 예시)

**방법 A: 간단한 실행 (Google Drive 사용)**
```bash
python src/auto_run_with_drive.py --month august --year 2025
```

**방법 B: 수동 실행 (2단계)**

1단계 - 계산 실행:
```bash
python src/인센티브_계산_개선버전.py --config config_files/config_august_2025.json
```

✅ **성공 신호**: "✅ Calculation completed successfully" 메시지 표시

2단계 - 대시보드 생성:
```bash
python src/step2_dashboard_version4.py --month august --year 2025
```

✅ **성공 신호**: "Dashboard generation completed" 메시지 표시

### 📖 Step 4: 결과 확인하기

1. **output_files 폴더 열기**
   - 파일 탐색기에서 프로젝트 폴더 → output_files 폴더 열기

2. **생성된 파일 찾기**
   - `2025_08_HWK_QIP_INCENTIVE_Version_4.html` - 웹 대시보드
   - `.xlsx` 파일 - 엑셀 결과
   - `.csv` 파일 - CSV 결과

3. **대시보드 열기**
   - HTML 파일을 더블클릭하면 웹브라우저에서 열립니다!
   - 예쁜 차트와 표가 나타나면 성공! 🎉

### 🗓️ 다른 월 실행하기 (예: 9월)

7월이나 9월 등 다른 달을 실행하려면:

```bash
# 7월 실행
python src/step2_dashboard_version4.py --month july --year 2025

# 9월 실행 (config_september_2025.json 파일이 있어야 함)
python src/step2_dashboard_version4.py --month september --year 2025
```

### ❓ 자주 발생하는 문제와 해결법

**문제 1**: "python이 없습니다" 오류
- **해결**: Python 설치 필요 → python.org에서 다운로드

**문제 2**: "No such file or directory" 오류  
- **해결**: 폴더 경로 확인 → `pwd` (맥) 또는 `cd` (윈도우) 입력해서 현재 위치 확인

**문제 3**: "ModuleNotFoundError" 오류
- **해결**: 패키지 재설치 → `pip install -r setup/requirements.txt` 다시 실행

**문제 4**: auto_run_with_drive.py "Incentive calculation failed" 오류
- **원인**: 스크립트 이름 불일치
- **해결**: step1_인센티브_계산_개선버전.py로 파일명 확인

**문제 5**: "인센티브 기준 내용을 로드할 수 없습니다" 오류
- **원인**: criteria_content.html 파일 누락
- **해결**: src/criteria_content.html 파일 생성 필요

**문제 6**: 월 정보 하드코딩 문제
- **원인**: 대시보드에 "2025년 7월" 고정 표시
- **해결**: step2_dashboard_version4.py에서 동적 월/년도 처리 적용

**문제 7**: UnboundLocalError: emp_id 오류
- **원인**: step1_인센티브_계산_개선버전.py에서 emp_id 변수 참조 오류
- **해결**: emp_id 변수를 else 블록 외부에서 정의

**문제 8**: action.sh HTML 파일 찾을 수 없음
- **원인**: "HTML 파일을 찾을 수 없습니다: 2025_08_HWK_QIP_INCENTIVE_Version_4.html"
- **해결**: dashboard_version4.html로 파일명 변경

**문제 9**: HTML 파일이 안 열려요
- **해결**: 크롬이나 엣지 브라우저로 열기 → 파일 우클릭 → "연결 프로그램" → Chrome/Edge 선택

**문제 5**: Google Drive 연동 시 "Incentive calculation failed" 오류
- **원인**: `auto_run_with_drive.py`가 잘못된 스크립트 이름을 참조
- **증상**: 
  ```
  ✅ Successfully synced 6 files
  💰 Running incentive calculation...
  ERROR - Main calculation script not found
  ERROR - ❌ Incentive calculation failed
  ```
- **해결**: 
  1. `src/auto_run_with_drive.py` 파일 수정
  2. Line 316: `인센티브_계산_개선버전.py` → `step1_인센티브_계산_개선버전.py`
  3. Line 319: `src/인센티브_계산_개선버전.py` → `src/step1_인센티브_계산_개선버전.py`
  4. Line 355: dashboard 경로를 `Path(__file__).parent / 'step2_dashboard_version4.py'`로 수정
- **확인**: 수정 후 정상 작동 시 "✅ Incentive calculation completed" 메시지 표시

**문제 6**: "인센티브 기준 내용을 로드할 수 없습니다" 메시지
- **원인**: `criteria_content.html` 파일이 없음
- **해결**: `src/criteria_content.html` 파일 생성 또는 확인
- **참고**: 이 파일이 없어도 대시보드는 작동하지만, 인센티브 기준 탭이 비어있게 됨

**문제 7**: 대시보드에 월 정보가 하드코딩되어 있음
- **증상**: 8월 데이터인데 "2025년 7월 인센티브 지급 현황"으로 표시
- **해결**: 
  1. `step2_dashboard_version4.py` 실행 시 `--month august --year 2025` 파라미터 추가
  2. 또는 `action.sh` 스크립트 사용하여 월/년 선택

### 💬 도움이 필요하면?

1. **에러 메시지 복사하기** - 전체 에러 메시지를 복사해두세요
2. **logs 폴더 확인** - 자세한 오류 정보가 기록되어 있습니다
3. **스크린샷 찍기** - 화면을 캡처해서 문제 상황을 기록하세요

### 🎊 축하합니다!

여기까지 따라오셨다면 인센티브 대시보드를 성공적으로 실행한 것입니다! 👏

---

*마지막 업데이트: 2025년 1월 21일*