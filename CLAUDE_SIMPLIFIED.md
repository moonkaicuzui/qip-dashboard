# QIP Incentive Dashboard System

## 프로젝트 개요

QIP 인센티브 대시보드 시스템 - 공장 근로자를 위한 인센티브 계산 및 시각화 시스템

**핵심 기능**:
- 월간 인센티브 자동 계산
- 인터랙티브 HTML 대시보드 생성
- 다국어 지원 (한국어, 영어, 베트남어)
- Google Drive 연동
- JSON 기반 비즈니스 룰 설정

## 핵심 원칙

### 1. 가짜 데이터 금지
- **절대 가짜/더미 데이터를 생성하지 마세요**
- 데이터가 없으면 0 또는 "데이터 없음"으로 표시
- "우리사전에 가짜 데이타는 없다"

### 2. JSON 기반 설정
- 모든 비즈니스 로직은 JSON 파일로 관리
- 하드코딩 금지
- `position_condition_matrix.json`에서 모든 조건 정의

## 빠른 실행

### 전체 프로세스 실행
```bash
./action.sh
# 월/연도 선택 → Google Drive 동기화 → 인센티브 계산 → 대시보드 생성
```

### 개별 실행
```bash
# 대시보드 생성
python integrated_dashboard_final.py --month 9 --year 2025

# Google Drive 동기화 포함
python integrated_dashboard_final.py --month 9 --year 2025 --sync
```

## 프로젝트 구조

```
├── action.sh                       # 메인 실행 스크립트
├── integrated_dashboard_final.py   # 대시보드 생성
├── CLAUDE.md                       # 프로젝트 가이드
│
├── src/                            # 소스 코드
│   ├── step0_create_monthly_config.py      # 월간 설정 생성
│   ├── step1_인센티브_계산_개선버전.py      # 인센티브 계산
│   ├── common_condition_checker.py         # 조건 체크
│   ├── condition_matrix_manager.py         # 비즈니스 룰 관리
│   ├── google_drive_manager.py             # Google Drive 연동
│   └── validate_hr_data.py                 # 데이터 검증
│
├── config_files/                   # 설정 파일
│   ├── position_condition_matrix.json      # 비즈니스 룰
│   ├── dashboard_translations.json         # 다국어 번역
│   └── config_september_2025.json          # 월별 설정
│
├── input_files/                    # 입력 데이터
│   ├── [year]년 [month] 인센티브 지급 세부 정보.csv
│   ├── attendance/
│   └── AQL history/
│
├── output_files/                   # 출력 결과
│   ├── Incentive_Dashboard_[year]_[MM]_Version_5.html
│   └── output_QIP_incentive_[month]_[year]_최종완성버전_v6.0_Complete.xlsx
│
└── credentials/                    # 인증 정보
    └── service-account-key.json
```

## 파일 명명 규칙

- **입력 파일**: `[year]년 [month] 인센티브 지급 세부 정보.csv`
- **출력 Excel**: `output_QIP_incentive_[month]_[year]_최종완성버전_v6.0_Complete.xlsx`
- **대시보드**: `Incentive_Dashboard_[year]_[MM]_Version_5.html`
- **설정**: `config_[month]_[year].json`

## 데이터 처리 흐름

```
Google Drive → 데이터 수집 → 설정 생성 → 인센티브 계산 → 대시보드 생성
```

### 처리 단계
1. **Step 0**: 월간 설정 생성 (`step0_create_monthly_config.py`)
2. **Step 0.5**: Google Drive 동기화 (`auto_run_with_drive.py`)
3. **Step 1**: 인센티브 계산 (`step1_인센티브_계산_개선버전.py`)
4. **Step 2**: 대시보드 생성 (`integrated_dashboard_final.py`)

## 비즈니스 로직 설정

### position_condition_matrix.json
- 모든 조건 정의 (출석, AQL, 5PRS 등)
- TYPE별 포지션 매핑 (TYPE-1, TYPE-2, TYPE-3)
- 검증 임계값 및 규칙

### dashboard_translations.json
- 한국어, 영어, 베트남어 번역
- 동적 언어 전환
- 모든 UI 텍스트

### assembly_inspector_continuous_months.json
- Assembly Inspector 연속 월 추적
- 3개월 연속 실패 감지

## TYPE 분류

- **TYPE-1**: 관리직 및 특수 포지션 (100K-200K VND)
- **TYPE-2**: 표준 검사직 (50K-100K VND)
- **TYPE-3**: 신규 QIP 멤버 (0 VND, 조건 없음)

## 주의사항

### JavaScript 생성
- f-string에서 중괄호는 `{{}}`로 이스케이프
- Chart.js 인스턴스는 재생성 전 반드시 제거
- `updateAllTexts()` 함수로 언어 전환

### 모달 디자인
- 통합 파란색 그라데이션 테마 (#e3f2fd → #bbdefb)
- 다크 블루 제목 텍스트 (#1565c0)
- Bootstrap 5 배지 클래스 사용

### Assembly Inspector 특별 로직
- 3개월 연속 AQL 실패 추적
- 연속 실패 시 자동 차단
- `common_condition_checker.py`에서 처리

## 일반적인 문제 해결

1. **템플릿 리터럴 오류**: f-string에서 `{{}}` 이스케이프 확인
2. **차트 애니메이션 버그**: Chart.js 인스턴스 제거 확인
3. **조건 평가**: `position_condition_matrix.json` 확인
4. **Google Drive 동기화 실패**: `service-account-key.json` 확인
5. **언어 전환 안됨**: `updateAllTexts()` 함수 확인

## 검증

```bash
# HR 데이터 검증
python src/validate_hr_data.py 9 2025

# Excel vs JSON 일관성 체크
python src/validate_excel_json_consistency.py \
    --excel "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv" \
    --json "config_files/assembly_inspector_continuous_months.json"
```

## 의존성

- pandas>=1.3.0
- numpy>=1.21.0
- openpyxl>=3.0.9
- gspread>=5.7.0
- google-auth>=2.16.0

---

**Note**: 이 프로젝트는 인센티브 대시보드에만 집중하도록 단순화되었습니다.
다른 대시보드(5PRS, Management, Attendance)는 `_removed_dashboards/` 폴더에 보관되어 있습니다.