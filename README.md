# QIP 인센티브 대시보드 시스템

월별 QIP 인센티브를 자동으로 계산하고 대시보드를 생성하는 시스템입니다.

## 🏆 주요 성과: 0 VND → 121,996,842 VND 문제 완벽 해결!

> **2025년 1월 21일** - 모든 직원의 인센티브가 0으로 표시되던 치명적 버그를 완벽히 해결했습니다.
> - **Before**: 모든 직원 0 VND (100% 오류)
> - **After**: 121,996,842 VND 정확히 계산 (84.5% 매칭률)
> - **자세한 이력**: [PROJECT_HISTORY.md](PROJECT_HISTORY.md) 참조

## 📝 업데이트 이력

### Version 8.0 (2025-08-21) 🎉 **Type별 구분 및 완전한 다국어 지원**
- **Type별 데이터 구분 문제 해결**: CSV 컬럼명 수정 ('TYPE' → 'ROLE TYPE STD')
- **언어 변경 시 단위 표시 문제 해결**: changeLanguage()에 데이터 재생성 로직 추가
- **베트남어 번역 완성**: 누락된 번역 변수 추가 (unitPeople, detailButton 등)
- **동적 월 정보 처리**: 하드코딩된 월 정보를 템플릿 변수로 대체
- **결과**: TYPE-1 (150명), TYPE-2 (276명), TYPE-3 (38명) 정확히 구분
- **다국어 지원**: 한국어, 영어, 베트남어 완벽 지원

### Version 7.0 (2025-01-21) 🎉 **0 VND → 121,996,842 VND 완벽 해결**
- **핵심 문제 해결**: 출석 데이터 컬럼 매칭 오류 수정 ("No." → "ID No")
- **데이터 타입 불일치 해결**: int64/string ID 매칭 문제 수정
- **출석 상태 체크 수정**: 'compAdd' == 'Đi làm' 정확한 체크
- **JavaScript 동적화**: 모든 하드코딩된 `july_incentive` 제거
- **Google Drive 자동화**: `sync_previous_incentive.py` 구현
- **방어적 코딩**: IndexError 방지 코드 추가
- **결과**: 84.5% 직원 매칭 성공, 총 121,996,842 VND 정확히 계산

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

**문제 10**: Type별 데이터가 구분되지 않음
- **증상**: Type별 현황 테이블에서 모든 Type이 동일한 값으로 표시
- **원인**: CSV 컬럼명 불일치 ('TYPE' vs 실제 'ROLE TYPE STD')
- **해결**: step2_dashboard_version4.py에서 `row.get('ROLE TYPE STD', '')` 로 수정

**문제 11**: 언어 변경 시 단위가 안 바뀜
- **증상**: 베트남어로 변경해도 "명"이 계속 표시됨
- **원인**: changeLanguage() 함수가 UI 텍스트만 변경하고 테이블 데이터는 재생성하지 않음
- **해결**: changeLanguage() 함수에 `generateSummaryData()` 및 `generatePositionData()` 추가

**문제 12**: 베트남어 번역 누락
- **증상**: 베트남어 선택 시 일부 UI 요소가 번역되지 않음
- **원인**: 번역 객체에 일부 변수 누락
- **해결**: vi 객체에 unitPeople, detailButton, positionStatusByType 등 추가

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

## 📚 Git 주요 명령어 가이드

### 🔍 기본 명령어

#### 1. Git 초기 설정
```bash
# 사용자 정보 설정
git config --global user.name "당신의 이름"
git config --global user.email "your.email@hotmail.com"

# 설정 확인
git config --list
```

#### 2. 저장소 초기화
```bash
# 새 저장소 만들기
git init

# 원격 저장소 복제
git clone https://github.com/username/repository.git
```

### 📝 일상적인 작업 흐름

#### 🔥 중요: Git의 3단계 작업 흐름 이해하기

```
1️⃣ 파일 수정 (Working Directory)
      ↓
2️⃣ git add . (Staging Area로 이동) ← ⚠️ 필수 단계!
      ↓
3️⃣ git commit -m "메시지" (Repository에 저장)
```

**⚠️ 핵심 포인트**: `git add`를 반드시 먼저 해야 합니다!
- `git add` 없이 `commit`하면 → "no changes added to commit" 오류 발생
- 새로 만든 파일은 특히 `git add`가 필수입니다

#### 1. 상태 확인
```bash
# 현재 상태 확인
git status

# 변경 내용 확인
git diff                    # 스테이징 전 변경사항
git diff --staged           # 스테이징된 변경사항
```

#### 2. 변경사항 저장 (⭐ 가장 중요!)
```bash
# ✅ 올바른 방법 (2단계)
git add .                   # 1단계: 모든 변경사항을 스테이징
git commit -m "테스트 커밋"  # 2단계: 스테이징된 내용을 커밋

# ❌ 자주 하는 실수
git commit -m "테스트 커밋"  # 실패! add를 안했음 → "no changes added to commit"

# 💡 단축 방법 (수정된 파일만 가능, 새 파일 X)
git commit -am "메시지"      # add + commit 동시에

# 파일별로 추가하기
git add 파일명               # 특정 파일만 추가
git add *.py                # 특정 패턴 파일 추가
```

#### 실제 예시로 이해하기
```bash
# 상황: README.md를 수정했을 때

# ❌ 잘못된 방법
echo "수정 내용" >> README.md
git commit -m "README 수정"     # 실패! "no changes added to commit"

# ✅ 올바른 방법
echo "수정 내용" >> README.md
git add README.md               # 또는 git add .
git commit -m "README 수정"      # 성공!

# 💡 팁: 상태 확인 습관화
git status                      # 어떤 파일이 변경되었는지 확인
git add .                       # 변경사항 스테이징
git status                      # 스테이징 확인 (녹색으로 표시)
git commit -m "수정 완료"        # 커밋
```

#### 3. 커밋 기록 확인
```bash
# 커밋 로그 보기
git log                     # 전체 로그
git log --oneline          # 한 줄로 요약
git log --oneline -5       # 최근 5개만
git log --graph            # 그래프로 보기
git log -p 파일명           # 특정 파일 변경 이력

# 특정 커밋 상세 보기
git show                    # 최근 커밋
git show 커밋ID             # 특정 커밋
```

### 🌿 브랜치 작업

#### 1. 브랜치 관리
```bash
# 브랜치 목록
git branch                  # 로컬 브랜치
git branch -a              # 모든 브랜치 (원격 포함)

# 브랜치 생성
git branch 브랜치명

# 브랜치 전환
git checkout 브랜치명
git checkout -b 브랜치명     # 생성 + 전환

# 브랜치 삭제
git branch -d 브랜치명       # 안전 삭제
git branch -D 브랜치명       # 강제 삭제
```

#### 2. 브랜치 병합
```bash
# 현재 브랜치에 다른 브랜치 병합
git merge 브랜치명

# 충돌 해결 후
git add .
git commit -m "충돌 해결"
```

### 🔄 되돌리기

#### 1. 작업 되돌리기
```bash
# 수정한 파일 되돌리기 (스테이징 전)
git checkout -- 파일명
git restore 파일명          # 새로운 방식

# 스테이징 취소
git reset HEAD 파일명
git restore --staged 파일명  # 새로운 방식
```

#### 2. 커밋 되돌리기
```bash
# 커밋 취소 (내용은 유지)
git reset --soft HEAD~1

# 커밋 취소 (내용도 삭제)
git reset --hard HEAD~1

# 특정 커밋으로 되돌리기
git reset --hard 커밋ID

# 되돌린 것을 되돌리기 (새 커밋 생성)
git revert HEAD
```

### 🌐 원격 저장소

#### 1. 원격 저장소 관리
```bash
# 원격 저장소 확인
git remote -v

# 원격 저장소 추가
git remote add origin URL

# 원격 저장소 변경
git remote set-url origin 새URL
```

#### 2. Push & Pull
```bash
# 원격에 올리기
git push origin main
git push -u origin main     # 처음 푸시할 때

# 원격에서 가져오기
git pull origin main        # fetch + merge
git fetch origin            # 가져오기만 (병합 X)
```

### 🔍 유용한 추가 명령어

#### 1. 파일 관리
```bash
# 파일 삭제
git rm 파일명
git rm --cached 파일명      # Git에서만 삭제 (파일은 유지)

# 파일 이동/이름 변경
git mv 원래이름 새이름
```

#### 2. 임시 저장 (Stash)
```bash
# 작업 내용 임시 저장
git stash
git stash save "메시지"

# 임시 저장 목록
git stash list

# 임시 저장 복원
git stash pop              # 복원 + 삭제
git stash apply            # 복원만
```

#### 3. 태그
```bash
# 태그 생성
git tag v1.0.0
git tag -a v1.0.0 -m "버전 1.0.0"

# 태그 목록
git tag

# 태그 푸시
git push origin v1.0.0
git push origin --tags     # 모든 태그
```

### 🆘 문제 해결

#### 1. 자주 발생하는 문제
```bash
# 마지막 커밋 메시지 수정
git commit --amend -m "새 메시지"

# 마지막 커밋에 파일 추가
git add 빠진파일
git commit --amend --no-edit

# .gitignore 적용 안될 때
git rm -r --cached .
git add .
git commit -m "gitignore 재적용"
```

#### 2. 충돌 해결
```bash
# 충돌 발생 시
1. 충돌 파일 수정
2. git add 충돌파일
3. git commit -m "충돌 해결"

# 병합 취소
git merge --abort
```

### 📊 프로젝트에서 실제 사용 예시

```bash
# 1. 오늘 작업한 내용 저장하기
git status                  # 변경사항 확인
git add .                   # 모든 변경사항 추가
git commit -m "Report HTML 제거 및 CSV 직접 읽기 구현"

# 2. 커밋 히스토리 확인
git log --oneline -5

# 3. 이전 상태로 되돌리기 (실수했을 때)
git reset --soft HEAD~1    # 마지막 커밋만 취소
```

### 💡 Git 작업 팁

1. **커밋은 자주, 작은 단위로**: 한 번에 한 가지 변경사항만
2. **명확한 커밋 메시지**: 무엇을, 왜 변경했는지 작성
3. **브랜치 활용**: main/master는 안정적으로 유지
4. **Pull 먼저**: push 전에 항상 pull로 최신 상태 유지
5. **.gitignore 활용**: 불필요한 파일은 처음부터 제외

---

*마지막 업데이트: 2025년 8월 21일 - Version 8.0*
*프로젝트 상태: ✅ Type별 구분 및 다국어 지원 완벽 구현*

