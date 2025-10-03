# 프로젝트 재구성 계획

## 1. 파일 분류

### 인센티브 대시보드 전용 (유지)
**핵심 실행 파일**
- `action.sh` - 인센티브 계산 메인 실행 스크립트
- `action_enhanced.sh` - 향상된 인센티브 실행 스크립트
- `integrated_dashboard_final.py` - 인센티브 대시보드 메인 생성기
- `test_final.sh` - 인센티브 테스트 스크립트

**핵심 소스 파일 (src/)**
- `src/step0_create_monthly_config.py` - 월간 설정 생성
- `src/step1_인센티브_계산_개선버전.py` - 인센티브 계산 엔진
- `src/common_condition_checker.py` - 조건 체크 로직
- `src/condition_matrix_manager.py` - 조건 매트릭스 관리
- `src/generate_json_from_excel.py` - Excel→JSON 변환
- `src/validate_hr_data.py` - HR 데이터 검증
- `src/validate_excel_json_consistency.py` - Excel/JSON 일관성 체크
- `src/calculate_working_days_from_attendance.py` - 근무일 계산
- `src/convert_attendance_data.py` - 출석 데이터 변환

**설정 파일 (config_files/)**
- `config_files/position_condition_matrix.json` - 핵심 비즈니스 룰
- `config_files/dashboard_translations.json` - 다국어 지원
- `config_files/assembly_inspector_continuous_months.json` - 연속 월 추적
- `config_files/config_september_2025.json` 등 월별 설정

**Google Drive 관련**
- `src/google_drive_manager.py` - Google Drive 연동
- `src/auto_run_with_drive.py` - Drive 자동 연동
- `credentials/service-account-key.json` - 인증 키

### 5PRS 대시보드 전용 (제거 대상)
- `5prs.sh` - 5PRS 실행 스크립트
- `5prs_data_api.py` - 5PRS API
- `src/5prs_data_api.py`
- `src/create_new_5prs_dashboard.py`
- `src/generate_5prs_dashboard_v2.py`
- `src/integrate_5prs_data.py`
- `src/download_5prs_from_drive.py`
- `5PRS DASHBOARD/` 전체 폴더
- `5prs dashboard system/` 전체 폴더
- `output_files/dashboards/5prs/` 폴더
- `test_5prs_api.py`

### Management 대시보드 전용 (제거 대상)
- `generate_management_dashboard*.py` (v2, v3, v4, v5, v6 등)
- `output_files/management_dashboard_*.html`
- `employee_risk_dashboard.html`
- `generate_risk_dashboard.py`
- `config_files/risk_dashboard_config.json`

### Attendance/Absence 대시보드 전용 (제거 대상)
- `attendance_dashboard*.py` (v2, v3, v4 등)
- `src/process_absence_data*.py`
- `src/update_absence_dashboard.py`
- `src/inject_absence_improvements*.py`
- `src/absence_language_config.py`
- `config_files/absence_*.json`
- `output_files/attendance_dashboard*.html`
- `output_files/absence_analytics_data*.json`
- `test_absence_analytics.sh`
- `tests/test_absence_*.py`

### 테스트/분석/디버깅 파일 (정리 대상)
**인센티브 관련 테스트 (유지)**
- `validate_dashboard.py`
- `validate_json_consistency.py`
- `verify_all_positions.py`
- `verify_line_leader_counts.py`
- `test_language_switching.py`
- `verify_dynamic_month.py`

**기타 테스트/디버깅 (제거)**
- 100개 이상의 test_*, analyze_*, debug_*, verify_*, check_* 파일들

### 문서 파일 (정리 대상)
**유지**
- `CLAUDE.md` - 프로젝트 가이드
- `GOOGLE_DRIVE_SETUP.md` - Google Drive 설정 가이드
- `requirements.txt` - 의존성 목록

**제거**
- 각종 REPORT, SUMMARY, ANALYSIS .md 파일들

## 2. 새로운 프로젝트 구조

```
incentive-dashboard/
├── README.md                     # 프로젝트 소개 및 사용법
├── requirements.txt              # Python 의존성
├── action.sh                     # 메인 실행 스크립트
├── test.sh                       # 테스트 스크립트
├── CLAUDE.md                     # AI 코딩 가이드
│
├── src/                          # 소스 코드
│   ├── __init__.py
│   ├── core/                     # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── incentive_calculator.py     # step1_인센티브_계산_개선버전.py
│   │   ├── condition_checker.py        # common_condition_checker.py
│   │   └── condition_matrix.py         # condition_matrix_manager.py
│   │
│   ├── data/                     # 데이터 처리
│   │   ├── __init__.py
│   │   ├── config_generator.py         # step0_create_monthly_config.py
│   │   ├── attendance_converter.py     # convert_attendance_data.py
│   │   ├── working_days_calculator.py  # calculate_working_days_from_attendance.py
│   │   └── excel_json_converter.py     # generate_json_from_excel.py
│   │
│   ├── dashboard/                # 대시보드 생성
│   │   ├── __init__.py
│   │   └── generator.py               # integrated_dashboard_final.py
│   │
│   ├── validation/               # 검증 로직
│   │   ├── __init__.py
│   │   ├── hr_validator.py           # validate_hr_data.py
│   │   └── consistency_validator.py  # validate_excel_json_consistency.py
│   │
│   └── integration/              # 외부 연동
│       ├── __init__.py
│       ├── google_drive.py          # google_drive_manager.py
│       └── auto_sync.py            # auto_run_with_drive.py
│
├── config/                       # 설정 파일
│   ├── position_condition_matrix.json
│   ├── dashboard_translations.json
│   ├── assembly_inspector_continuous_months.json
│   └── monthly/                 # 월별 설정
│       ├── config_september_2025.json
│       └── ...
│
├── input_files/                  # 입력 데이터
│   ├── attendance/
│   ├── AQL history/
│   └── ...
│
├── output_files/                 # 출력 결과
│   ├── dashboards/              # 생성된 대시보드
│   └── reports/                 # Excel/CSV 리포트
│
├── credentials/                  # 인증 정보
│   └── service-account-key.json
│
├── tests/                        # 테스트 코드
│   ├── __init__.py
│   ├── test_incentive_calculation.py
│   ├── test_dashboard_generation.py
│   └── test_validation.py
│
└── _archive/                     # 제거된 파일들 (임시 보관)
    ├── 5prs_dashboard/
    ├── management_dashboard/
    ├── attendance_dashboard/
    └── old_tests/
```

## 3. 실행 계획

### Phase 1: 백업 및 준비
1. 전체 프로젝트 백업
2. `_removed_dashboards` 폴더 생성

### Phase 2: 파일 이동
1. 5PRS 관련 파일들을 `_removed_dashboards/5prs/`로 이동
2. Management 대시보드 파일들을 `_removed_dashboards/management/`로 이동
3. Attendance/Absence 파일들을 `_removed_dashboards/attendance/`로 이동
4. 불필요한 테스트 파일들을 `_removed_dashboards/old_tests/`로 이동

### Phase 3: 구조 재구성
1. 새로운 폴더 구조 생성
2. 인센티브 관련 파일들을 새 구조로 재배치
3. 파일명 정리 및 단순화

### Phase 4: 코드 정리
1. import 경로 수정
2. 불필요한 의존성 제거
3. action.sh 스크립트 업데이트

### Phase 5: 검증
1. 인센티브 대시보드 생성 테스트
2. 기능 검증
3. 문서 업데이트

## 4. 예상 결과

- **파일 수 감소**: 400+ 파일 → ~50 파일
- **구조 단순화**: 명확한 모듈 구조
- **유지보수 개선**: 바이브 코딩 작업 용이
- **성능 향상**: 불필요한 코드 제거로 실행 속도 개선