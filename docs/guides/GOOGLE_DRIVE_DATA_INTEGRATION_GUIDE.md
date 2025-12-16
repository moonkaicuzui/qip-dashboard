# Google Drive 데이터 통합 가이드

이 문서는 QIP Incentive Dashboard 프로젝트에서 사용하는 Google Drive 데이터 소스에 대한 종합 가이드입니다. 다른 프로젝트에서 동일한 데이터를 활용할 수 있도록 필요한 모든 정보를 포함합니다.

---

## 📋 목차

1. [개요](#1-개요)
2. [Google Drive 폴더 구조](#2-google-drive-폴더-구조)
3. [데이터 파일 상세 명세](#3-데이터-파일-상세-명세)
4. [서비스 계정 설정](#4-서비스-계정-설정)
5. [데이터 다운로드 구현](#5-데이터-다운로드-구현)
6. [설정 파일 구성](#6-설정-파일-구성)
7. [데이터 검증](#7-데이터-검증)
8. [GitHub Actions 자동화](#8-github-actions-자동화)
9. [문제 해결](#9-문제-해결)
10. [빠른 시작 체크리스트](#10-빠른-시작-체크리스트)

---

## 1. 개요

### 1.1 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Google Drive (Single Source of Truth)             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  monthly_data   │  │   aql_history   │  │     configs     │         │
│  │  ├── 2025_11    │  │  AQL_REPORT_... │  │  mappings.json  │         │
│  │  ├── 2025_12    │  └─────────────────┘  └─────────────────┘         │
│  │  └── ...        │                                                     │
│  └─────────────────┘                                                     │
└────────────────────────────────────────┬────────────────────────────────┘
                                         │
                                         ▼ Service Account (OAuth 2.0)
┌────────────────────────────────────────┴────────────────────────────────┐
│                           GitHub Actions                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ GOOGLE_SERVICE_ACCOUNT (JSON Secret)                             │   │
│  │ GDRIVE_FOLDER_ID (Folder ID Secret)                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  📥 Download → 📊 Process → 🎨 Generate Dashboard → 🚀 Deploy           │
└────────────────────────────────────────┬────────────────────────────────┘
                                         │
                                         ▼
                    ┌────────────────────┴────────────────────┐
                    │  Project A (QIP Dashboard)              │
                    │  Project B (Your New Project)           │
                    │  Project C (Future Projects)            │
                    └─────────────────────────────────────────┘
```

### 1.2 데이터 유형 요약

| 데이터 유형 | 파일 패턴 | 갱신 주기 | 용도 |
|------------|----------|----------|------|
| **기본 인사정보** | `basic manpower data {month}.csv` | 월간 | 직원 기본정보, 직급, 입사일 |
| **출근 데이터** | `attendance data {month}.csv` | 일간 | 출근/결근 기록 |
| **5PRS 검사 데이터** | `5prs data {month}.csv` | 일간 | 품질 검사 결과 |
| **AQL 이력** | `1.HSRG AQL REPORT-{MONTH}.{YEAR}.csv` | 월간 | AQL 품질 검사 이력 |

---

## 2. Google Drive 폴더 구조

### 2.1 폴더 ID 정보

```
Root Folder: 1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D
├── monthly_data: 1yFbEIjfpLgPKB7CQhTWyrdKLkn55NlXv
│   ├── 2025_07
│   ├── 2025_08
│   ├── 2025_09
│   ├── 2025_10
│   ├── 2025_11
│   └── 2025_12 (최신)
│
├── aql_history: 18yWygciJczt7fnEKjzGCAC21VVPWmlVi
│   ├── AQL_REPORT_JULY_2025.csv
│   ├── AQL_REPORT_AUGUST_2025.csv
│   └── ...
│
└── configs: 1rQ0atIZ-8FxY7fW9wZGBQ7us2-oJl67S
    ├── auditor_trainer_area_mapping.json
    └── type2_position_mapping.json
```

### 2.2 월별 폴더 명명 규칙

```
패턴: {year}_{month:02d}
예시:
  - 2025_07 (2025년 7월)
  - 2025_11 (2025년 11월)
  - 2025_12 (2025년 12월)
```

### 2.3 폴더 공유 설정

**중요**: 서비스 계정 이메일에 폴더 접근 권한을 부여해야 합니다.

1. Google Drive에서 공유할 폴더 선택
2. 우클릭 → "공유"
3. 서비스 계정 이메일 추가 (예: `qip-dashboard@qip-dashboard.iam.gserviceaccount.com`)
4. 권한: **뷰어** (읽기 전용) 또는 **편집자** (읽기/쓰기)
5. "알림 전송" 체크 해제 (서비스 계정은 이메일 수신 불가)

---

## 3. 데이터 파일 상세 명세

### 3.1 기본 인사정보 (Basic Manpower Data)

**파일명 패턴**: `basic manpower data {month}.csv`

**용도**: 직원의 기본 정보, 직급, 입사일, 상사 정보 등

**인코딩**: UTF-8 (BOM 포함)

**컬럼 명세**:

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `STT` | Integer | 순번 | 1, 2, 3 |
| `Employee No` | String | 직원 번호 (9자리) | "617100049" |
| `Full Name` | String | 직원 전체 이름 (베트남어) | "ĐINH KIM NGOAN" |
| `QIP POSITION 1ST NAME` | String | 1차 직급명 | "GROUP LEADER" |
| `QIP POSITION NAME CODE1` | String | 1차 직급 코드 | "OF" |
| `QIP POSITION 2ND NAME` | String | 2차 직급명 | "REPORT TEAM" |
| `QIP POSITION NAME CODE2` | String | 2차 직급 코드 | "OF2" |
| `QIP POSITION 3RD NAME` | String | 3차 직급명 | "TEAM OPERATION MANAGEMENT" |
| `FINAL QIP POSITION NAME CODE` | String | 최종 직급 코드 | "OF2" |
| `ROLE TYPE STD` | String | 역할 타입 | "TYPE-1", "TYPE-2" |
| `Entrance Date` | Date | 입사일 (MM/DD/YYYY) | "10/24/2017" |
| `Final Incentive amount` | Integer | 최종 인센티브 금액 (VND) | 468634 |
| `Personnel Number_manpower` | String | 인사번호 | "617100049" |
| `Need Manual Update` | Boolean | 수동 업데이트 필요 여부 | "TRUE", "FALSE" |
| `MST direct boss name` | String | MST 직속 상사 번호 | "620070050" |
| `direct boss name` | String | 직속 상사 이름 | "MAI TUYẾT ANH" |
| `Stop working Date` | Date | 퇴사일 (빈 값이면 재직중) | "" or "10/15/2025" |
| `remark -lab or qip` | String | 비고 (LAB 또는 QIP) | "QIP" |
| `pregnant vacation-yes or no` | String | 출산휴가 여부 | "yes", "no" |
| `Display Pregnant Women (Thai san)` | Date | 출산휴가 시작일 | "2025.09.01" |
| `RE MARK` | String | 추가 비고 | "On maternity leave" |
| `Personnel Number` | String | 인사번호 (중복) | "617100049" |

**샘플 데이터**:
```csv
STT,Employee No,Full Name,QIP POSITION 1ST  NAME,QIP POSITION NAME CODE1,QIP POSITION 2ND  NAME,QIP POSITION NAME CODE2,QIP POSITION 3RD  NAME,FINAL QIP POSITION NAME CODE,ROLE TYPE STD,Entrance Date,Final Incentive amount,Personnel Number_manpower,Need Manual Update,MST direct boss name,direct boss name,Stop working Date,remark -lab or qip,pregnant vacation-yes or no,Display Pregnant Women (Thai san) ,RE MARK ,Personnel Number
1,617100049,ĐINH KIM NGOAN,GROUP LEADER,OF,REPORT TEAM,OF2,TEAM OPERATION MANAGEMENT,OF2,TYPE-2,10/24/2017,0,617100049,TRUE,620070050,MAI TUYẾT ANH,,QIP,no,2025.02.22,Returningemployee(maternity leave),617100049
2,618030024,TRẦN KIỀU EM,(V) SUPERVISOR,T,(V) SUPERVISOR,T,HWK OSC/MTL QUALITY IN CHARGE,T,TYPE-2,3/5/2018,468634,618030024,FALSE,620070012,TRẦN THỊ BÍCH LY,,QIP,no,,Promotion on July,618030024
```

### 3.2 출근 데이터 (Attendance Data)

**파일명 패턴**: `attendance data {month}.csv`

**용도**: 일별 출근/결근 기록, 결근 사유

**인코딩**: UTF-8 (BOM 포함)

**컬럼 명세**:

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `No.` | Integer | 순번 | 1, 2, 3 |
| `Work Date` | Date | 근무일 (YYYY.MM.DD) | "2025.11.01" |
| `CoCode` | String | 회사 코드 | "R100" |
| `Department` | String | 부서 코드 | "PRGMRQI1" |
| `ID No` | String | 직원 번호 | "617100049" |
| `Last name` | String | 직원 이름 | "ĐINH KIM NGOAN" |
| `compAdd` | String | 출근 상태 | "Đi làm" (출근), "Vắng mặt" (결근) |
| `Reason Description` | String | 결근 사유 | "Phép năm" (연차), "Không quẹt thẻ" (카드 미체크) |
| `WTime` | String | 근무 시간 코드 | "7T", "9J" |

**출근 상태 값**:
- `Đi làm` - 정상 출근
- `Vắng mặt` - 결근

**결근 사유 값**:
- `Phép năm` - 연차 휴가 (승인된 휴가)
- `Không quẹt thẻ` - 카드 미체크 (출근했으나 기록 누락)
- (빈 값) - 정상 출근 또는 무단 결근

**샘플 데이터**:
```csv
No.,Work Date,CoCode,Department,ID No,Last name,compAdd,Reason Description,WTime,,,,
1,2025.11.01,R100,PRGMRQI1,617100049,ĐINH KIM NGOAN,Đi làm,,7T,,,,
24,2025.11.28,R100,PRGMRQI1,617100049,ĐINH KIM NGOAN,Vắng mặt,Phép năm,7T,,,,
```

### 3.3 5PRS 검사 데이터 (5PRS Data)

**파일명 패턴**: `5prs data {month}.csv`

**용도**: 5PRS 품질 검사 결과, 합격/불합격 수량

**인코딩**: UTF-8 (BOM 포함)

**컬럼 명세**:

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `Inspection Date` | Date | 검사일 (MM/DD/YYYY) | "11/5/2025" |
| `Inspector ID` | String | 검사자 직원 번호 | "623080475" |
| `Inspector Name` | String | 검사자 이름 | "SẦM TRÍ THÀNH" |
| `Time` | String | 검사 시간대 | "AM", "PM" |
| `Building` | String | 건물명 | "ASSEMBLY B" |
| `Line` | String | 라인명 | "RG B ASSEMBLY aSC 01-1" |
| `PO No` | String | PO 번호 | "901728989" |
| `PO Item` | Integer | PO 항목 번호 | 1 |
| `Model` | String | 모델명 | "TENSAUR SPORT 3.0 CF K" |
| `TQC ID` | String | TQC 담당자 직원 번호 | "619020468" |
| `TQC Name` | String | TQC 담당자 이름 | "THỊ MY" |
| `Valiation Qty` | Integer | 검사 수량 | 20 |
| `Pass Qty` | Integer | 합격 수량 | 20 |
| `Reject Qty` | Integer | 불합격 수량 | 0 |
| `Error` | String | 에러 유형 | "DIRTY BOTTOM (DƠ ĐẾ)" |

**샘플 데이터**:
```csv
Inspection Date,Inspector ID,Inspector Name,Time,Building,Line,PO No,PO Item,Model,TQC ID,TQC Name,Valiation Qty,Pass Qty,Reject Qty,Error
11/5/2025,623080475,SẦM TRÍ THÀNH,AM,ASSEMBLY B,RG B  ASSEMBLY   aSC 01-1,901728989,1,TENSAUR SPORT 3.0  CF K,619020468,THỊ MY,20,20,0,
11/5/2025,620070013,NGUYỄN THANH TRÚC,AM,ASSEMBLY A,RG A  ASSEMBLY   aSC 05-2,901268027,1,VL COURT 3.0 K,619060201,BÙI THỊ KIỀU LY,10,9,1,DIRTY BOTTOM (DƠ ĐẾ)
```

### 3.4 AQL 이력 데이터 (AQL History)

**파일명 패턴**: `1.HSRG AQL REPORT-{MONTH}.{YEAR}.csv`

**Google Drive 파일명**: `AQL_REPORT_{MONTH}_{YEAR}.csv`

**용도**: AQL 품질 검사 이력, CFA/비CFA 검사 결과

**인코딩**: UTF-8 (BOM 포함)

**컬럼 명세**:

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `MONTH` | Integer | 월 | 11 |
| `DATE` | Date | 검사일 (MM/DD/YYYY) | "11/1/2025" |
| `MODEL` | String | 모델명 | "VL COURT 3.0 K" |
| `PO NO 1.` | String | PO 번호 1 | "901673784" |
| `Item` | Integer | 항목 번호 | 1 |
| `PO NO 2.` | String | PO 번호 2 | "901673784-1" |
| `DEST` | String | 목적지 국가 | "Netherlands" |
| `QTY` | String | 수량 (쉼표 포함) | "2,920" |
| `REPACKING` | Integer | 재포장 수량 | 12 or empty |
| `RESULT` | String | 검사 결과 | "PASS", "FAIL" |
| `PARTIAL Q'TY` | Integer | 부분 수량 | empty or number |
| `PARTIAL NO` | String | 부분 번호 | empty or string |
| `BUILDING` | String | 건물 코드 | "A", "B", "B3", "C", "D" |
| `LINE` | String | 라인명 | "Asc 03-1" |
| `TQC NUM` | String | TQC 번호 | "R4A" |
| `EMPLOYEE NO` | String | 직원 번호 | "620080362" |
| `QTY INSPECTION` | Integer | 검사 수량 | 125 |
| `OFFICIAL INSPECTOR` | String | 공식 검사자 | "MS.HUỲNH" |
| `INSPECTOR TYPE` | String | 검사자 타입 | "CFA" |
| `DESCRIPTION` | String | 불량 설명 | "Wobbling(4)" |
| `REMARKS` | String | 비고 | empty |
| `INTERNAL INSPECTOR` | String | 내부 검사자 | empty |
| `Stitching issue` | String | 스티칭 이슈 | empty |
| `Wrong Packing issue(prs)` | String | 포장 이슈 | empty |
| `NOTE` | String | 노트 | empty |

**RESULT 값**:
- `PASS` - 합격
- `FAIL` - 불합격

**BUILDING 값**:
- `A` - Assembly A (Building A)
- `B` - Assembly B (Building B)
- `B3` - Assembly B3 (Building B3)
- `C` - Assembly C (Building C)
- `D` - Assembly D (Building D)

**샘플 데이터**:
```csv
MONTH,DATE,MODEL,PO NO 1.,Item,PO NO 2.,DEST,QTY,REPACKING ,RESULT,PARTIAL Q'TY,PARTIAL NO,BUILDING,LINE,TQC NUM,EMPLOYEE NO,QTY INSPECTION,OFFICIAL INSPECTOR,INSPECTOR TYPE,DESCRIPTION,REMARKS,INTERNAL INSPECTOR,Stitching issue,Wrong Packing issue(prs),NOTE
11,11/1/2025,VL COURT 3.0 K,901673784,1,901673784-1,Netherlands,"2,920",,PASS,,,A,Asc 03-1,R4A,620080362,125,MS.HUỲNH,CFA,Wobbling(4),,,,,
```

---

## 4. 서비스 계정 설정

### 4.1 서비스 계정 생성

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 프로젝트 생성 또는 선택
3. "IAM 및 관리자" → "서비스 계정" 이동
4. "서비스 계정 만들기" 클릭
   - 이름: `qip-dashboard` (예시)
   - 설명: "QIP Dashboard data sync"
5. 역할 선택: 없음 (Google Drive는 폴더 공유로 접근 제어)
6. "완료" 클릭

### 4.2 서비스 계정 키 생성

1. 생성된 서비스 계정 클릭
2. "키" 탭 이동
3. "키 추가" → "새 키 만들기"
4. JSON 형식 선택 → "만들기"
5. JSON 파일 다운로드 (보안 유지!)

### 4.3 서비스 계정 JSON 구조

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id-here",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@your-project.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### 4.4 Google Drive API 활성화

1. Google Cloud Console → "API 및 서비스" → "라이브러리"
2. "Google Drive API" 검색
3. "사용 설정" 클릭

### 4.5 폴더 접근 권한 부여

1. Google Drive에서 공유할 폴더 우클릭 → "공유"
2. 서비스 계정 이메일 추가 (`client_email` 값)
3. 권한: **뷰어** (읽기 전용)
4. "알림 전송" 체크 해제

---

## 5. 데이터 다운로드 구현

### 5.1 Python 구현 예시

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import io
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def init_google_drive_service():
    """Google Drive 서비스 초기화"""
    # 환경변수에서 서비스 계정 정보 로드
    service_account_info = json.loads(
        os.environ.get('GOOGLE_SERVICE_ACCOUNT', '{}')
    )

    if not service_account_info:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT 환경변수가 설정되지 않았습니다")

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )

    return build('drive', 'v3', credentials=credentials)

def list_files_in_folder(service, folder_id, file_type='csv'):
    """폴더 내 파일 목록 조회"""
    query = f"'{folder_id}' in parents and trashed=false"

    if file_type == 'csv':
        query += " and (mimeType='text/csv' or name contains '.csv')"

    results = service.files().list(
        q=query,
        fields="files(id, name, modifiedTime, mimeType)",
        orderBy="modifiedTime desc"
    ).execute()

    return results.get('files', [])

def download_file(service, file_id, output_path):
    """파일 다운로드"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(output_path, 'wb') as f:
        f.write(fh.getvalue())

    return True

def detect_latest_month_folder(service, monthly_data_folder_id):
    """최신 월 폴더 자동 감지"""
    import re

    query = f"'{monthly_data_folder_id}' in parents and " \
            f"mimeType='application/vnd.google-apps.folder' and trashed=false"

    results = service.files().list(
        q=query,
        fields="files(id, name)",
        orderBy="name desc"
    ).execute()

    folders = results.get('files', [])
    month_names = {
        1: 'january', 2: 'february', 3: 'march', 4: 'april',
        5: 'may', 6: 'june', 7: 'july', 8: 'august',
        9: 'september', 10: 'october', 11: 'november', 12: 'december'
    }

    month_folders = []
    for folder in folders:
        match = re.match(r'(\d{4})_(\d{1,2})', folder['name'])
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            month_folders.append({
                'id': folder['id'],
                'name': folder['name'],
                'year': year,
                'month': month,
                'month_name': month_names.get(month, 'unknown')
            })

    # 최신 순 정렬
    month_folders.sort(key=lambda x: (x['year'], x['month']), reverse=True)
    return month_folders

# 사용 예시
if __name__ == "__main__":
    service = init_google_drive_service()

    MONTHLY_DATA_FOLDER_ID = "1yFbEIjfpLgPKB7CQhTWyrdKLkn55NlXv"

    # 최신 월 폴더 찾기
    month_folders = detect_latest_month_folder(service, MONTHLY_DATA_FOLDER_ID)
    latest = month_folders[0]

    print(f"최신 월: {latest['name']} ({latest['month_name']} {latest['year']})")

    # 파일 목록 조회
    files = list_files_in_folder(service, latest['id'])

    # 파일 다운로드
    for file in files:
        file_name = file['name'].lower()

        if 'basic' in file_name and 'manpower' in file_name:
            output_path = f"input_files/basic manpower data {latest['month_name']}.csv"
        elif 'attendance' in file_name:
            output_path = f"input_files/attendance/original/attendance data {latest['month_name']}.csv"
        elif '5prs' in file_name:
            output_path = f"input_files/5prs data {latest['month_name']}.csv"
        else:
            continue

        download_file(service, file['id'], output_path)
        print(f"✅ 다운로드: {file['name']} → {output_path}")
```

### 5.2 필요 Python 패키지

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

또는 `requirements.txt`:
```
google-auth>=2.0.0
google-auth-oauthlib>=0.4.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
```

---

## 6. 설정 파일 구성

### 6.1 drive_config.json

```json
{
  "google_drive": {
    "root_folder_id": "1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D",
    "folder_structure": {
      "monthly_data": {
        "id": "1yFbEIjfpLgPKB7CQhTWyrdKLkn55NlXv",
        "naming_pattern": "{year}_{month:02d}"
      },
      "aql_history": {
        "id": "18yWygciJczt7fnEKjzGCAC21VVPWmlVi",
        "file_pattern": "AQL_REPORT_{month}_{year}.csv"
      },
      "configs": {
        "id": "1rQ0atIZ-8FxY7fW9wZGBQ7us2-oJl67S"
      }
    }
  },
  "sync_settings": {
    "auto_sync_enabled": true,
    "sync_interval_minutes": 60,
    "retry_attempts": 3
  },
  "file_mappings": [
    {
      "drive_pattern": "monthly_data/{year}_{month:02d}/basic_manpower_data.csv",
      "local_path": "input_files/basic manpower data {month}.csv",
      "required": true
    },
    {
      "drive_pattern": "monthly_data/{year}_{month:02d}/attendance_data.csv",
      "local_path": "input_files/attendance/original/attendance data {month}.csv",
      "required": true
    },
    {
      "drive_pattern": "monthly_data/{year}_{month:02d}/5prs_data.csv",
      "local_path": "input_files/5prs data {month}.csv",
      "required": true
    },
    {
      "drive_pattern": "aql_history/AQL_REPORT_{MONTH}_{year}.csv",
      "local_path": "input_files/AQL history/1.HSRG AQL REPORT-{MONTH}.{year}.csv",
      "required": true
    }
  ]
}
```

### 6.2 월별 설정 파일 (config_{month}_{year}.json)

```json
{
  "year": 2025,
  "month": "december",
  "working_days": 12,
  "previous_months": ["october", "november"],
  "file_paths": {
    "5prs": "input_files/5prs data december.csv",
    "attendance": "input_files/attendance/original/attendance data december.csv",
    "basic_manpower": "input_files/basic manpower data december.csv",
    "aql_current": "input_files/AQL history/1.HSRG AQL REPORT-DECEMBER.2025.csv"
  },
  "data_source": "google_drive",
  "files_modified_times": {
    "5prs": "2025-12-15T09:08:18.000Z",
    "attendance": "2025-12-15T08:50:28.000Z",
    "basic_manpower": "2025-12-15T08:48:37.000Z",
    "aql_current": "2025-12-15T09:04:33.000Z"
  },
  "last_updated": "2025-12-15T09:08:18.000Z"
}
```

---

## 7. 데이터 검증

### 7.1 필수 검증 항목

```python
def validate_basic_manpower(df):
    """기본 인사정보 검증"""
    required_columns = [
        'Employee No', 'Full Name', 'QIP POSITION 1ST NAME',
        'FINAL QIP POSITION NAME CODE', 'ROLE TYPE STD', 'Entrance Date'
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼 누락: {col}")

    # 직원 번호 형식 검증 (9자리 숫자)
    invalid_emp_no = df[~df['Employee No'].astype(str).str.match(r'^\d{9}$')]
    if len(invalid_emp_no) > 0:
        print(f"⚠️ 잘못된 직원 번호: {len(invalid_emp_no)}건")

    return True

def validate_attendance(df):
    """출근 데이터 검증"""
    required_columns = ['Work Date', 'ID No', 'compAdd']

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼 누락: {col}")

    # 날짜 형식 검증 (YYYY.MM.DD)
    try:
        df['Work Date'].apply(lambda x: datetime.strptime(x, '%Y.%m.%d'))
    except:
        raise ValueError("날짜 형식 오류: YYYY.MM.DD 형식이어야 합니다")

    return True
```

### 7.2 데이터 무결성 검사

```python
def check_data_integrity(basic_manpower_df, attendance_df):
    """데이터 무결성 검사"""
    # 인사정보에 있는 직원이 출근 데이터에도 있는지 확인
    manpower_employees = set(basic_manpower_df['Employee No'].astype(str))
    attendance_employees = set(attendance_df['ID No'].astype(str))

    missing_in_attendance = manpower_employees - attendance_employees
    if missing_in_attendance:
        print(f"⚠️ 출근 데이터 누락 직원: {len(missing_in_attendance)}명")

    extra_in_attendance = attendance_employees - manpower_employees
    if extra_in_attendance:
        print(f"⚠️ 인사정보 누락 직원: {len(extra_in_attendance)}명")

    return True
```

---

## 8. GitHub Actions 자동화

### 8.1 Workflow 예시

```yaml
name: 🔄 Auto Sync Google Drive Data

on:
  schedule:
    # 30분마다 실행
    - cron: '*/30 * * * *'

  workflow_dispatch:  # 수동 실행 가능

permissions:
  contents: write

jobs:
  sync-data:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: 🐍 Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: 📚 Install dependencies
      run: |
        pip install google-auth google-api-python-client pandas

    - name: 📥 Download from Google Drive
      env:
        GOOGLE_SERVICE_ACCOUNT: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}
        GDRIVE_FOLDER_ID: ${{ secrets.GDRIVE_FOLDER_ID }}
      run: |
        python scripts/download_from_gdrive.py

    - name: 📤 Commit and push
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"

        if [[ -n $(git status -s) ]]; then
          git add input_files/*.csv
          git add input_files/**/*.csv
          git commit -m "🔄 Auto sync from Google Drive $(date '+%Y-%m-%d %H:%M')"
          git push
        fi
```

### 8.2 GitHub Secrets 설정

| Secret 이름 | 설명 | 예시 |
|------------|------|------|
| `GOOGLE_SERVICE_ACCOUNT` | 서비스 계정 JSON 전체 내용 | `{"type":"service_account",...}` |
| `GDRIVE_FOLDER_ID` | 루트 폴더 ID | `1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D` |

**설정 방법**:
1. GitHub Repository → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. 이름과 값 입력 → "Add secret"

---

## 9. 문제 해결

### 9.1 일반적인 오류

| 오류 | 원인 | 해결책 |
|------|------|--------|
| `403 Forbidden` | 폴더 접근 권한 없음 | 서비스 계정 이메일에 폴더 공유 |
| `404 Not Found` | 폴더/파일 ID 오류 | 올바른 ID 확인 |
| `Invalid credentials` | 서비스 계정 JSON 오류 | JSON 형식 및 내용 확인 |
| `API not enabled` | Drive API 미활성화 | Google Cloud Console에서 활성화 |

### 9.2 디버깅 팁

```python
# 서비스 계정 이메일 확인
service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT'))
print(f"Service Account: {service_account_info['client_email']}")

# 폴더 목록 확인
files = service.files().list(
    q=f"'{folder_id}' in parents",
    fields="files(id, name, mimeType)"
).execute()
print(json.dumps(files, indent=2))
```

### 9.3 로컬 테스트

```bash
# 환경변수 설정 (macOS/Linux)
export GOOGLE_SERVICE_ACCOUNT=$(cat /path/to/service-account.json)
export GDRIVE_FOLDER_ID="1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D"

# 스크립트 실행
python scripts/download_from_gdrive.py
```

---

## 10. 빠른 시작 체크리스트

### 10.1 사전 준비

- [ ] Google Cloud 프로젝트 생성
- [ ] Google Drive API 활성화
- [ ] 서비스 계정 생성 및 JSON 키 다운로드
- [ ] 데이터 폴더에 서비스 계정 이메일 공유

### 10.2 프로젝트 설정

- [ ] Python 패키지 설치 (`google-auth`, `google-api-python-client`)
- [ ] `drive_config.json` 생성 (폴더 ID 설정)
- [ ] 다운로드 스크립트 작성 또는 복사

### 10.3 GitHub 설정

- [ ] `GOOGLE_SERVICE_ACCOUNT` Secret 추가
- [ ] `GDRIVE_FOLDER_ID` Secret 추가
- [ ] GitHub Actions Workflow 생성

### 10.4 테스트

- [ ] 로컬에서 다운로드 스크립트 테스트
- [ ] GitHub Actions 수동 실행 테스트
- [ ] 데이터 무결성 검증

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **서비스 계정 이메일**이 폴더에 공유되어 있는지
2. **폴더 ID**가 올바른지 (URL에서 확인)
3. **Google Drive API**가 활성화되어 있는지
4. **서비스 계정 JSON**이 올바른 형식인지

---

*이 문서는 QIP Incentive Dashboard 프로젝트 기준으로 작성되었습니다.*
*최종 업데이트: 2025-12-16*
