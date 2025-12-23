# HR 및 출결 데이터 통합 가이드

> **문서 목적**: 이 문서는 QIP 인센티브 대시보드에서 사용하는 HR/출결 데이터의 Google Drive 연동 방법을 설명합니다.
> 다른 프로젝트(교육 프로그램 등)에서 동일한 데이터 소스를 활용할 수 있도록 상세한 정보를 제공합니다.

---

## 📋 목차

1. [시스템 개요](#1-시스템-개요)
2. [Google Drive 인증](#2-google-drive-인증)
3. [폴더 구조 및 파일 ID](#3-폴더-구조-및-파일-id)
4. [데이터 파일 상세](#4-데이터-파일-상세)
5. [데이터 다운로드 방법](#5-데이터-다운로드-방법)
6. [데이터 처리 파이프라인](#6-데이터-처리-파이프라인)
7. [대시보드 활용](#7-대시보드-활용)
8. [다른 프로젝트 연동 가이드](#8-다른-프로젝트-연동-가이드)

---

## 1. 시스템 개요

### 1.1 데이터 흐름 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Google Drive                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ monthly_data │  │  aql_history │  │   configs    │              │
│  │   폴더       │  │    폴더      │  │    폴더      │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼─────────────────┼─────────────────┼──────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Service Account 인증 (OAuth 2.0)                       │
│              JSON 키 파일 → Google Drive API v3                     │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    다운로드 스크립트                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐  │
│  │ download_from_gdrive.py │  │ enhanced_download_with_config.py│  │
│  │ (기본 다운로드)          │  │ (다운로드 + Config 자동 업데이트) │  │
│  └─────────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      로컬 파일 시스템                                │
│  input_files/                                                       │
│  ├── basic manpower data {month}.csv      ← 인사 기본 정보          │
│  ├── attendance/original/                  ← 출결 원본 데이터        │
│  │   └── attendance data {month}.csv                                │
│  ├── attendance/converted/                 ← 출결 변환 데이터        │
│  │   └── attendance data {month}_converted.csv                      │
│  ├── 5prs data {month}.csv                 ← 5PRS 검사 데이터        │
│  └── AQL history/                          ← AQL 품질 데이터         │
│      └── 1.HSRG AQL REPORT-{MONTH}.{YEAR}.csv                       │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      데이터 처리 엔진                                │
│  1. convert_attendance_data.py  → 출결 데이터 집계                   │
│  2. step1_인센티브_계산_개선버전.py → 인센티브 계산                    │
│  3. integrated_dashboard_final.py → 대시보드 HTML 생성               │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        출력물                                        │
│  output_files/                                                       │
│  ├── output_QIP_incentive_{month}_{year}_Complete_V9.0_Complete.csv │
│  ├── output_QIP_incentive_{month}_{year}_Complete_V9.0_Complete.xlsx│
│  └── Incentive_Dashboard_{year}_{month}_Version_9.0.html            │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 자동 동기화 주기

| 환경 | 주기 | 트리거 |
|------|------|--------|
| **GitHub Actions** | 30분마다 | Cron: `*/30 * * * *` |
| **수동 실행** | 필요시 | `workflow_dispatch` 또는 로컬 스크립트 |
| **코드 변경 시** | 자동 | Push to main branch |

---

## 2. Google Drive 인증

### 2.1 Service Account 방식

Google Drive API 접근에 **Service Account (서비스 계정)** 방식을 사용합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                    Service Account                            │
│                                                               │
│  이메일: qip-dashboard@qip-dashboard.iam.gserviceaccount.com │
│  프로젝트: qip-dashboard                                      │
│  권한: Google Drive API (읽기 전용)                           │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 인증 키 파일 구조

**파일명**: `qip-dashboard-dabdc4d51ac9.json`

```json
{
  "type": "service_account",
  "project_id": "qip-dashboard",
  "private_key_id": "dabdc4d51ac9...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "qip-dashboard@qip-dashboard.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### 2.3 인증 설정 방법

#### 로컬 개발 환경

```bash
# 방법 1: 환경 변수로 설정 (권장)
export GOOGLE_SERVICE_ACCOUNT=$(cat /path/to/service-account.json)
python scripts/download_from_gdrive.py

# 방법 2: 직접 JSON 로드
GOOGLE_SERVICE_ACCOUNT=$(cat /Users/ksmoon/Downloads/qip-dashboard-dabdc4d51ac9.json) \
python scripts/download_from_gdrive.py
```

#### GitHub Actions

```yaml
# .github/workflows/auto-update.yml
env:
  GOOGLE_SERVICE_ACCOUNT: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}
```

**GitHub Secret 설정**:
1. Repository → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. Name: `GOOGLE_SERVICE_ACCOUNT`
4. Value: JSON 파일 전체 내용 붙여넣기

### 2.4 Python 인증 코드

```python
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def init_google_drive_service():
    """Google Drive API 서비스 초기화"""

    # 환경 변수에서 서비스 계정 JSON 로드
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT', '{}')
    service_account_info = json.loads(service_account_json)

    # 인증 정보 생성 (읽기 전용 권한)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )

    # Google Drive API 서비스 빌드
    service = build('drive', 'v3', credentials=credentials)

    return service
```

---

## 3. 폴더 구조 및 파일 ID

### 3.1 Google Drive 폴더 구조

```
📁 Root Folder (ID: 1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D)
│
├── 📁 monthly_data (ID: 1yFbEIjfpLgPKB7CQhTWyrdKLkn55NlXv)
│   │
│   ├── 📁 2025_07/
│   │   ├── 📄 basic_manpower_data.csv
│   │   ├── 📄 attendance_data.csv
│   │   └── 📄 5prs_data.csv
│   │
│   ├── 📁 2025_08/
│   │   └── ... (동일 구조)
│   │
│   ├── 📁 2025_09/
│   ├── 📁 2025_10/
│   ├── 📁 2025_11/
│   └── 📁 2025_12/
│       ├── 📄 basic_manpower_data.csv      ← 인사 기본 정보
│       ├── 📄 attendance_data.csv          ← 출결 일별 데이터
│       └── 📄 5prs_data.csv                ← 5PRS 검사 데이터
│
├── 📁 aql_history (ID: 18yWygciJczt7fnEKjzGCAC21VVPWmlVi)
│   ├── 📄 AQL_REPORT_JULY_2025.csv
│   ├── 📄 AQL_REPORT_AUGUST_2025.csv
│   ├── 📄 AQL_REPORT_SEPTEMBER_2025.csv
│   ├── 📄 AQL_REPORT_OCTOBER_2025.csv
│   ├── 📄 AQL_REPORT_NOVEMBER_2025.csv
│   └── 📄 AQL_REPORT_DECEMBER_2025.csv
│
└── 📁 configs (ID: 1rQ0atIZ-8FxY7fW9wZGBQ7us2-oJl67S)
    ├── 📄 auditor_trainer_area_mapping.json
    └── 📄 type2_position_mapping.json
```

### 3.2 Drive Config 파일

**파일**: `config_files/drive_config.json`

```json
{
  "root_folder_id": "1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D",
  "folders": {
    "monthly_data": "1yFbEIjfpLgPKB7CQhTWyrdKLkn55NlXv",
    "aql_history": "18yWygciJczt7fnEKjzGCAC21VVPWmlVi",
    "configs": "1rQ0atIZ-8FxY7fW9wZGBQ7us2-oJl67S"
  },
  "file_patterns": {
    "basic_manpower": ["basic", "manpower"],
    "attendance": ["attendance", "출근"],
    "5prs": ["5prs", "5PRS"],
    "aql": ["AQL", "REPORT"]
  }
}
```

### 3.3 파일 명명 규칙

| 데이터 유형 | Google Drive 파일명 | 로컬 저장 경로 |
|------------|-------------------|---------------|
| **인사 기본정보** | `basic_manpower_data.csv` | `input_files/basic manpower data {month}.csv` |
| **출결 데이터** | `attendance_data.csv` | `input_files/attendance/original/attendance data {month}.csv` |
| **5PRS 검사** | `5prs_data.csv` | `input_files/5prs data {month}.csv` |
| **AQL 품질** | `AQL_REPORT_{MONTH}_{YEAR}.csv` | `input_files/AQL history/1.HSRG AQL REPORT-{MONTH}.{YEAR}.csv` |

---

## 4. 데이터 파일 상세

### 4.1 인사 기본 정보 (Basic Manpower Data)

**용도**: 직원 기본 정보, 직급, 입사일, 퇴사일, 상사 정보 등

#### 컬럼 구조

| 컬럼명 | 설명 | 데이터 타입 | 예시 |
|--------|------|------------|------|
| `STT` | 순번 | Integer | 1, 2, 3... |
| `Employee No` | 사원번호 (9자리) | String | "617100049" |
| `Full Name` | 직원 성명 | String | "ĐINH KIM NGOAN" |
| `QIP POSITION NAME CODE` | 직급 코드 | String | "OF", "T", "A", "D" |
| `FINAL QIP POSITION NAME CODE` | 최종 직급 코드 | String | "OF2", "T", "A1" |
| `ROLE TYPE STD` | 인센티브 유형 | String | "TYPE-1", "TYPE-2", "TYPE-3" |
| `Entrance Date` | 입사일 | Date | "10/24/2017" |
| `Stop working Date` | 퇴사일 (빈값=재직중) | Date | "2025.02.22" 또는 빈값 |
| `direct boss name` | 직속 상사 성명 | String | "MAI TUYẾT ANH" |
| `Personnel Number_manpower` | 사원번호 (숫자) | Integer | 617100049 |
| `Display Pregnant Women` | 출산휴가 여부 | String | "yes" / "no" |
| `Department` | 부서 코드 | String | "PRGMRQI1" |
| `Building` | 빌딩 | String | "A", "B", "C" |

#### 샘플 데이터

```csv
STT,Employee No,Full Name,QIP POSITION NAME CODE,FINAL QIP POSITION NAME CODE,ROLE TYPE STD,Entrance Date,Stop working Date,direct boss name,Department,Building
1,617100049,ĐINH KIM NGOAN,OF,OF2,TYPE-2,10/24/2017,,MAI TUYẾT ANH,PRGMRQI1,A
2,618030024,TRẦN KIỀU EM,T,T,TYPE-2,3/5/2018,,TRẦN THỊ BÍCH LY,PRGMRQI2,B
3,620060128,NGUYỄN VĂN A,A,A1,TYPE-1,6/15/2020,,LÊ THỊ B,PRGMRQI1,A
```

#### 직급 코드 설명

| 코드 | 직급명 | TYPE |
|------|--------|------|
| A, A1-A5 | ASSEMBLY INSPECTOR | TYPE-1 |
| D | MODEL MASTER | TYPE-1 |
| E | AUDITOR & TRAINER | TYPE-1 |
| T | LINE LEADER | TYPE-1/2 |
| G | GROUP LEADER | TYPE-2 |
| S | SUPERVISOR | TYPE-2 |
| OF, OF2 | OFFICER (신입) | TYPE-2/3 |
| M | MANAGER | TYPE-2 |

---

### 4.2 출결 데이터 (Attendance Data)

**용도**: 직원별 일별 출근/결근 기록

#### 원본 데이터 (Daily Records)

**파일 위치**: `input_files/attendance/original/attendance data {month}.csv`

| 컬럼명 | 설명 | 데이터 타입 | 예시 |
|--------|------|------------|------|
| `Work Date` | 근무 날짜 | Date | "2025.11.01" |
| `Personnel Number` | 사원번호 | String | "617100049" |
| `Last name` | 직원 성명 | String | "ĐINH KIM NGOAN" |
| `CoCode` | 회사 코드 | String | "R100" |
| `Department` | 부서 코드 | String | "PRGMRQI1" |
| `Reason Description` | 출결 사유 | String | (아래 표 참조) |
| `compAdd` | 출근 상태 | String | "Đi làm" / "Vắng mặt" |

#### 출결 사유 코드

| 사유 코드 | 설명 (베트남어) | 설명 (한국어) | 분류 |
|----------|---------------|--------------|------|
| `Đi làm` | Đi làm | 출근 | 정상 출근 |
| `AR1` | AR1 - Vắng không phép | 무단 결근 | 무단 결근 ⚠️ |
| `AR2` | AR2 - Nghỉ phép có lương | 유급 휴가 | 승인 휴가 ✅ |
| `AR3` | AR3 - Nghỉ thai sản | 출산 휴가 | 승인 휴가 ✅ |
| `AR4` | AR4 - Nghỉ ốm | 병가 | 승인 휴가 ✅ |
| `AR5` | AR5 - Nghỉ việc riêng | 개인 사유 휴가 | 승인 휴가 ✅ |
| `Vắng mặt` | Vắng mặt | 결근 | 무단 결근 ⚠️ |

#### 변환된 데이터 (Aggregated Per-Employee)

**파일 위치**: `input_files/attendance/converted/attendance data {month}_converted.csv`

| 컬럼명 | 설명 | 계산 방법 |
|--------|------|----------|
| `ID No` | 사원번호 | 원본에서 추출 |
| `Last name` | 직원 성명 | 원본에서 추출 |
| `ACTUAL WORK DAY` | 실제 출근일 | "Đi làm" 레코드 수 |
| `TOTAL WORK DAY` | 총 근무일 | 해당 월의 고유 날짜 수 |
| `AR1 Absences` | 무단 결근일 | "AR1" 사유 레코드 수 |
| `Unapproved Absences` | 무단 결근일 (동의어) | AR1 Absences와 동일 |
| `Approved Leave Days` | 승인 휴가일 | 총 결근 - 무단 결근 |
| `Absence Rate (%)` | 결근율 | (무단결근 / 총근무일) × 100 |
| `Attendance Rate (%)` | 출근율 | 100 - 결근율 |

#### 출근율 계산 공식 (중요!)

```python
# 핵심 공식: 승인휴가는 출근으로 인정
결근일 = 총근무일 - 실제출근일 - 승인휴가
결근율 = (결근일 / 총근무일) × 100
출근율 = 100 - 결근율

# 예시: 총근무일=25, 실제출근=20, 승인휴가=3, 무단결근=2
# 결근율 = (2 / 25) × 100 = 8%
# 출근율 = 100 - 8 = 92% ✅ (88% 이상이면 조건 충족)
```

---

### 4.3 5PRS 검사 데이터

**용도**: 5PRS (5-Point Random Sampling) 품질 검사 기록

#### 컬럼 구조

| 컬럼명 | 설명 | 데이터 타입 | 예시 |
|--------|------|------------|------|
| `Inspection Date` | 검사 날짜 | Date | "11/5/2025" |
| `Inspector ID` | 검사관 사원번호 | String | "623080475" |
| `Inspector Name` | 검사관 성명 | String | "SẦM TRÍ THÀNH" |
| `Building` | 빌딩 | String | "ASSEMBLY B" |
| `Line` | 생산 라인 | String | "RG B ASSEMBLY aSC 01-1" |
| `Model` | 제품 모델 | String | "TENSAUR SPORT 3.0 CF K" |
| `TQC ID` | 품질 검사원 ID | String | "619020468" |
| `TQC Name` | 품질 검사원 성명 | String | "THỊ MY" |
| `Validation Qty` | 검사 수량 | Integer | 20 |
| `Pass Qty` | 합격 수량 | Integer | 20 |
| `Reject Qty` | 불합격 수량 | Integer | 0 |

#### 5PRS 조건 평가

| 조건 | 설명 | 계산 방법 | 기준 |
|------|------|----------|------|
| **조건 9** | 5PRS 합격률 | Pass_Qty / Validation_Qty | ≥ 95% |
| **조건 10** | 5PRS 검사 수량 | SUM(Validation_Qty) | ≥ 100개 |

---

### 4.4 AQL 품질 데이터

**용도**: AQL (Acceptable Quality Level) 품질 검사 이력

#### 컬럼 구조

| 컬럼명 | 설명 | 데이터 타입 | 예시 |
|--------|------|------------|------|
| `MONTH` | 월 | Integer | 11 |
| `DATE` | 검사 날짜 | Date | "11/1/2025" |
| `MODEL` | 제품 모델 | String | "VL COURT 3.0 K" |
| `QTY INSPECTION` | 검사 수량 | Integer | 125 |
| `RESULT` | 결과 | String | "PASS" / "FAIL" |
| `EMPLOYEE NO` | 검사관 사원번호 | String | "620080362" |
| `OFFICIAL INSPECTOR` | 검사관 성명 | String | "MS.HUỲNH" |
| `INSPECTOR TYPE` | 검사관 유형 | String | "CFA" / "General" |
| `DESCRIPTION` | 불합격 사유 | String | "Wobbling(4)" |
| `BUILDING` | 빌딩 | String | "A", "B", "C" |
| `LINE` | 생산 라인 | String | "Asc 03-1" |

#### AQL 조건 평가

| 조건 | 설명 | 기준 |
|------|------|------|
| **조건 5** | 당월 개인 AQL 실패 | = 0 (FAIL 없음) |
| **조건 6** | 개인 3개월 연속 실패 | 없음 |
| **조건 7** | 팀/영역 3개월 연속 실패 | 없음 |
| **조건 8** | 영역 불합격률 | < 3% |

---

## 5. 데이터 다운로드 방법

### 5.1 기본 다운로드 스크립트

**파일**: `scripts/download_from_gdrive.py`

```python
#!/usr/bin/env python3
"""Google Drive에서 HR/출결 데이터 다운로드"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

def init_google_drive_service():
    """Google Drive API 서비스 초기화"""
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT', '{}')
    service_account_info = json.loads(service_account_json)

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )

    return build('drive', 'v3', credentials=credentials)

def list_files_in_folder(service, folder_id, file_type='csv'):
    """폴더 내 파일 목록 조회 (최신순 정렬)"""
    query = f"'{folder_id}' in parents and trashed = false"
    if file_type:
        query += f" and mimeType contains '{file_type}'"

    results = service.files().list(
        q=query,
        fields="files(id, name, modifiedTime, size)",
        orderBy="modifiedTime desc"
    ).execute()

    return results.get('files', [])

def download_file(service, file_id, output_path, force=True):
    """파일 다운로드"""
    if force and os.path.exists(output_path):
        os.remove(output_path)
        print(f"🔄 기존 파일 삭제: {output_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    request = service.files().get_media(fileId=file_id)

    with io.FileIO(output_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    print(f"✅ 다운로드 완료: {output_path}")
    return True

def download_monthly_data(service, month_folder_id, month_name):
    """월별 데이터 다운로드"""
    files = list_files_in_folder(service, month_folder_id)

    downloaded_patterns = set()

    for file in files:
        file_name = file['name'].lower()

        # 파일 유형 판별
        if 'basic' in file_name and 'manpower' in file_name:
            pattern_type = 'basic_manpower'
            output_path = f"input_files/basic manpower data {month_name}.csv"
        elif 'attendance' in file_name:
            pattern_type = 'attendance'
            output_path = f"input_files/attendance/original/attendance data {month_name}.csv"
        elif '5prs' in file_name:
            pattern_type = '5prs'
            output_path = f"input_files/5prs data {month_name}.csv"
        else:
            continue

        # 중복 방지 (최신 파일만 다운로드)
        if pattern_type in downloaded_patterns:
            print(f"⏭️ 건너뜀 (이미 다운로드됨): {file['name']}")
            continue

        if download_file(service, file['id'], output_path):
            downloaded_patterns.add(pattern_type)

# 사용 예시
if __name__ == '__main__':
    service = init_google_drive_service()

    # drive_config.json에서 폴더 ID 로드
    with open('config_files/drive_config.json', 'r') as f:
        config = json.load(f)

    monthly_folder_id = config['folders']['monthly_data']

    # 최신 월 데이터 다운로드
    download_monthly_data(service, monthly_folder_id, 'december')
```

### 5.2 통합 다운로드 + Config 업데이트

**파일**: `scripts/enhanced_download_with_config.py`

이 스크립트는 다운로드 후 자동으로:
1. `config_{month}_{year}.json` 파일 생성/업데이트
2. `working_days` 자동 계산
3. Google Drive `modifiedTime` 저장 (마지막 업데이트 시간)

```bash
# 실행 방법
GOOGLE_SERVICE_ACCOUNT=$(cat /path/to/credentials.json) \
python scripts/enhanced_download_with_config.py
```

### 5.3 로컬 실행 명령어 요약

```bash
# 1. 환경 변수 설정
export GOOGLE_SERVICE_ACCOUNT=$(cat /Users/ksmoon/Downloads/qip-dashboard-dabdc4d51ac9.json)

# 2. 데이터 다운로드
python scripts/download_from_gdrive.py

# 3. 출결 데이터 변환 (일별 → 직원별 집계)
python src/convert_attendance_data.py

# 4. 인센티브 계산
python scripts/auto_calculate_incentives.py

# 5. 대시보드 생성
python integrated_dashboard_final.py --month 12 --year 2025
```

---

## 6. 데이터 처리 파이프라인

### 6.1 출결 데이터 변환

**입력**: `attendance data {month}.csv` (일별 레코드)
**출력**: `attendance data {month}_converted.csv` (직원별 집계)

```python
# src/convert_attendance_data.py 핵심 로직

import pandas as pd

def convert_attendance_data(input_file, output_file):
    # 원본 데이터 로드
    df = pd.read_csv(input_file)

    # 총 근무일 계산 (고유 날짜 수)
    total_working_days = df['Work Date'].nunique()

    # 직원별 집계
    aggregated = df.groupby('Personnel Number').agg({
        'Last name': 'first',
        'Work Date': 'count',  # 전체 레코드 수
    }).reset_index()

    # 출근일 계산 (compAdd = 'Đi làm')
    actual_days = df[df['compAdd'] == 'Đi làm'].groupby('Personnel Number').size()

    # 무단 결근 계산 (AR1로 시작하는 사유)
    ar1_absences = df[df['Reason Description'].str.startswith('AR1', na=False)]\
                    .groupby('Personnel Number').size()

    # 결과 데이터프레임 구성
    result = pd.DataFrame({
        'ID No': aggregated['Personnel Number'],
        'Last name': aggregated['Last name'],
        'ACTUAL WORK DAY': actual_days.reindex(aggregated['Personnel Number']).fillna(0).astype(int),
        'TOTAL WORK DAY': total_working_days,
        'AR1 Absences': ar1_absences.reindex(aggregated['Personnel Number']).fillna(0).astype(int),
    })

    # 승인 휴가 계산
    result['Approved Leave Days'] = result['TOTAL WORK DAY'] - result['ACTUAL WORK DAY'] - result['AR1 Absences']
    result['Approved Leave Days'] = result['Approved Leave Days'].clip(lower=0)

    # 출근율 계산 (핵심 공식)
    result['Unapproved Absences'] = result['AR1 Absences']
    absence_rate = (result['Unapproved Absences'] / result['TOTAL WORK DAY']) * 100
    result['Absence Rate (%)'] = absence_rate.round(2)
    result['Attendance Rate (%)'] = (100 - absence_rate).round(2)

    result.to_csv(output_file, index=False)
    return result
```

### 6.2 Config 파일 구조

**파일**: `config_files/config_{month}_{year}.json`

```json
{
  "year": 2025,
  "month": "december",
  "working_days": 18,
  "file_paths": {
    "basic_manpower": "input_files/basic manpower data december.csv",
    "attendance": "input_files/attendance/original/attendance data december.csv",
    "attendance_converted": "input_files/attendance/converted/attendance data december_converted.csv",
    "5prs": "input_files/5prs data december.csv",
    "aql_current": "input_files/AQL history/1.HSRG AQL REPORT-DECEMBER.2025.csv",
    "previous_incentive": "output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"
  },
  "files_modified_times": {
    "basic_manpower": "2025-12-22T09:43:58.000Z",
    "attendance": "2025-12-20T08:15:30.000Z",
    "5prs": "2025-12-21T03:22:45.000Z"
  },
  "last_updated": "2025-12-22T09:43:58.000Z"
}
```

---

## 7. 대시보드 활용

### 7.1 대시보드 데이터 구조

대시보드 HTML에 포함된 JavaScript 데이터:

```javascript
// 전역 변수로 접근 가능
window.employeeData = [
  {
    "emp_no": "617100049",
    "name": "ĐINH KIM NGOAN",
    "position": "OFFICER",
    "type": "TYPE-2",
    "department": "PRGMRQI1",
    "building": "A",

    // 출결 정보
    "Total Working Days": 18,
    "Actual Working Days": 16,
    "Approved Leave": 1,
    "Unapproved Absences": 1,
    "Attendance Rate": 94.44,

    // 조건 충족 여부
    "Condition_1": "YES",  // 출근율 >= 88%
    "Condition_2": "YES",  // 무단결근 <= 2일
    "Condition_3": "YES",  // 실제 근무일 > 0
    "Condition_4": "YES",  // 최소 근무일 >= 12일

    // 인센티브
    "december_incentive": 468634,
    "Previous_Incentive": 450000,
    "Continuous_Months": 8
  },
  // ... 더 많은 직원 데이터
];

// 출결 원본 데이터
window.excelDashboardData = {
  "attendance": {
    "total_working_days": 18,
    "daily_data": { /* 일별 출결 데이터 */ }
  }
};
```

### 7.2 개인 출결 조회 탭

대시보드에 새로 추가된 "🔍 개인 출결 조회" 탭:

```javascript
function lookupEmployeeAttendance() {
    const empNo = document.getElementById('attendance-lookup-input').value.trim();

    // 직원 찾기
    const employee = window.employeeData.find(emp =>
        String(emp.emp_no) === empNo || String(emp['Employee No']) === empNo
    );

    if (!employee) {
        alert('직원을 찾을 수 없습니다.');
        return;
    }

    // 출결 정보 표시
    displayAttendanceSummary(employee);
    displayDailyAttendance(employee);
    displayAbsencePatterns(employee);
}
```

---

## 8. 다른 프로젝트 연동 가이드

### 8.1 필요 파일 복사

다른 프로젝트에서 동일한 데이터를 사용하려면:

```bash
# 1. 필수 설정 파일
cp config_files/drive_config.json <새_프로젝트>/config_files/

# 2. 다운로드 스크립트
cp scripts/download_from_gdrive.py <새_프로젝트>/scripts/
cp scripts/enhanced_download_with_config.py <새_프로젝트>/scripts/

# 3. 데이터 변환 스크립트
cp src/convert_attendance_data.py <새_프로젝트>/src/
```

### 8.2 Python 의존성

```txt
# requirements.txt
pandas>=1.3.0
google-api-python-client>=2.0.0
google-auth>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=0.5.0
```

### 8.3 간단한 데이터 로드 예시

```python
"""다른 프로젝트에서 HR/출결 데이터 로드하는 예시"""

import pandas as pd
import json
import os

class HRDataLoader:
    def __init__(self, config_path='config_files/config_december_2025.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def load_employee_data(self):
        """인사 기본 정보 로드"""
        path = self.config['file_paths']['basic_manpower']
        return pd.read_csv(path, encoding='utf-8')

    def load_attendance_data(self, converted=True):
        """출결 데이터 로드"""
        if converted:
            path = self.config['file_paths'].get(
                'attendance_converted',
                self.config['file_paths']['attendance'].replace('.csv', '_converted.csv')
            )
        else:
            path = self.config['file_paths']['attendance']
        return pd.read_csv(path, encoding='utf-8')

    def get_employee_attendance(self, emp_no):
        """특정 직원의 출결 정보 조회"""
        employees = self.load_employee_data()
        attendance = self.load_attendance_data()

        emp_info = employees[employees['Employee No'] == emp_no]
        att_info = attendance[attendance['ID No'] == emp_no]

        if emp_info.empty:
            return None

        result = {
            'employee_no': emp_no,
            'name': emp_info.iloc[0]['Full Name'],
            'position': emp_info.iloc[0]['FINAL QIP POSITION NAME CODE'],
            'department': emp_info.iloc[0]['Department'],
        }

        if not att_info.empty:
            result.update({
                'actual_days': int(att_info.iloc[0]['ACTUAL WORK DAY']),
                'total_days': int(att_info.iloc[0]['TOTAL WORK DAY']),
                'approved_leave': int(att_info.iloc[0].get('Approved Leave Days', 0)),
                'unapproved_absences': int(att_info.iloc[0]['Unapproved Absences']),
                'attendance_rate': float(att_info.iloc[0]['Attendance Rate (%)']),
            })

        return result


# 사용 예시
if __name__ == '__main__':
    loader = HRDataLoader()

    # 전체 직원 데이터
    employees = loader.load_employee_data()
    print(f"총 직원 수: {len(employees)}")

    # 특정 직원 출결 조회
    emp_info = loader.get_employee_attendance('620060128')
    if emp_info:
        print(f"직원: {emp_info['name']}")
        print(f"출근율: {emp_info['attendance_rate']}%")
```

### 8.4 GitHub Actions 연동

다른 프로젝트에서 동일한 자동화를 설정하려면:

```yaml
# .github/workflows/sync-hr-data.yml
name: Sync HR Data from Google Drive

on:
  schedule:
    - cron: '0 * * * *'  # 매 시간
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install pandas google-api-python-client google-auth

      - name: Download from Google Drive
        env:
          GOOGLE_SERVICE_ACCOUNT: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}
        run: python scripts/download_from_gdrive.py

      - name: Convert attendance data
        run: python src/convert_attendance_data.py

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add input_files/ config_files/
          git diff --staged --quiet || git commit -m "🔄 Auto sync HR data"
          git push
```

### 8.5 Service Account 공유

**중요**: 동일한 Google Drive 데이터에 접근하려면 **동일한 Service Account 사용** 필요

1. 기존 Service Account JSON을 새 프로젝트 GitHub Secrets에 추가
2. Secret 이름: `GOOGLE_SERVICE_ACCOUNT`
3. 값: 전체 JSON 내용

---

## 📝 요약

| 항목 | 설명 |
|------|------|
| **데이터 소스** | Google Drive (Service Account 인증) |
| **동기화 주기** | 30분마다 자동 (GitHub Actions) |
| **주요 데이터** | 인사정보, 출결, 5PRS 검사, AQL 품질 |
| **인증 방식** | Service Account JSON (환경 변수) |
| **처리 결과** | CSV, Excel, HTML 대시보드 |

**핵심 스크립트**:
- `scripts/download_from_gdrive.py` - 데이터 다운로드
- `src/convert_attendance_data.py` - 출결 데이터 변환
- `integrated_dashboard_final.py` - 대시보드 생성

---

> **문의**: 이 문서에 대한 질문이나 추가 정보가 필요하시면 프로젝트 담당자에게 문의하세요.
>
> **마지막 업데이트**: 2025-12-23
