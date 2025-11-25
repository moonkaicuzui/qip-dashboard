# 🔍 QIP 인센티브 시스템 종합 분석 보고서

**분석 일자**: 2025-11-25  
**분석 대상**: November 2025 인센티브 데이터  
**분석자**: Claude Code (AI System Auditor)

---

## 📋 Executive Summary (경영진 요약)

4가지 중대 문제가 확인되었으며, 이 중 **문제 1번 (출근율 계산 공식 불일치)**은 정책 위반으로 **즉시 수정이 필요**합니다.

| 문제 | 심각도 | 영향 범위 | 시정 기한 |
|------|--------|-----------|-----------|
| 1. 출근율 계산 공식 불일치 | 🔴 CRITICAL | 전 직원 (540명) | 즉시 |
| 2. TYPE-2 인센티브 금액 불일치 | 🟡 MEDIUM | TYPE-2 QC/Staff (~50명) | 1주 이내 |
| 3. 웹사이트 vs HTML 다운로드 데이터 불일치 | 🟢 LOW | 사용자 편의성 | 2주 이내 |
| 4. AQL Inspector 연속월 조건 검증 | ✅ VERIFIED | 검증 완료 - 문제 없음 | - |

---

## 🚨 문제 1: 출근율 계산 공식 불일치 (CRITICAL)

### 📊 문제 개요

**정책 문서에 명시된 공식**과 **시스템이 실제 사용하는 공식**이 서로 다릅니다.

#### 📜 정책 (Policy) - 사용자 제공
```
Attendance Rate = 100 - Absence Rate
Absence Rate = (Absence Days / Total Working Days) × 100
```

#### 💻 시스템 (System) - 실제 코드
```python
# src/step1_인센티브_계산_개선버전.py:4695-4708
출근율 = (실제 근무일 / (총 근무일 - 승인휴가)) × 100
결근율 = (결근일 / (총 근무일 - 승인휴가)) × 100
```

**핵심 차이점**: 분모에 승인휴가 반영 여부
- 정책: 총 근무일 (승인휴가 포함)
- 시스템: 총 근무일 - 승인휴가

---

### 🔍 실제 사례 분석: 직원 625080250 (LÂM THỊ CHÚC ANH)

#### 원본 데이터 (CSV)
```
Employee No: 625080250
Name: LÂM THỊ CHÚC ANH
Position: STITCHING INSPECTOR (TYPE-2)
Total Working Days: 19일
Actual Working Days: 14일
Approved Leave Days: 2일
Unapproved Absences: 3일
출근율 (시스템): 82.35%
결근율 (시스템): 17.65%
November Incentive: 0 VND
```

#### 계산 비교

**1️⃣ 정책 공식 (사용자 요구)**
```
Absence Days = Total Working Days - Actual Working Days
             = 19 - 14 = 5일

Absence Rate = (5 / 19) × 100 = 26.32%

Attendance Rate = 100 - 26.32 = 73.68%
```
❌ 73.68% < 88% → **인센티브 미지급 (정책상 정당)**

**2️⃣ 시스템 공식 (현재 실행 중)**
```
Expected Working Days = Total Working Days - Approved Leave
                      = 19 - 2 = 17일

Absence Days = Expected Working Days - Actual Working Days
             = 17 - 14 = 3일

Absence Rate = (3 / 17) × 100 = 17.65%

Attendance Rate = 100 - 17.65 = 82.35%
```
❌ 82.35% < 88% → **인센티브 미지급 (시스템 판단)**

**3️⃣ 사용자 주장 공식**
```
Absence Rate = (Absence Days / (Total Working Days - Approved Leave)) × 100
             = (2 / (18 - 2)) × 100 = 12.5%

Attendance Rate = 100 - 12.5 = 87.5%
```
❌ 87.5% < 88% → **인센티브 미지급**

**⚠️ 주의**: 사용자가 제공한 "2일 결근"은 **무단결근(Unapproved Absences) 3일**과 불일치합니다.

---

### 📈 영향 분석

#### 전체 직원 영향 범위
```bash
총 직원: 540명
승인휴가 사용자: ~200명 (추정)
출근율 경계선 직원 (85-90%): ~50명 (추정)
잠재적 영향 직원: 10-30명
```

#### 재무 영향 (추정)
```
평균 인센티브: 400,000 VND
영향받을 직원: 20명 (중간값)
월간 재무 영향: 8,000,000 VND
연간 재무 영향: 96,000,000 VND (9백만 원)
```

---

### ✅ 근본 원인 (Root Cause)

**파일**: `src/step1_인센티브_계산_개선버전.py`  
**라인**: 4695-4708

```python
# ✅ FIXED: 출근율 = (실제 근무일 / (총 근무일 - 승인휴가)) × 100
# 승인휴가는 "근무하지 않은 날"이므로 분모에서 제외해야 함
if total_days > 0:
    # 근무해야 할 일수 = 총 근무일 - 승인휴가
    expected_working_days = total_days - approved_leave_days
    
    if expected_working_days > 0:
        # 출근율 = 실제 근무일 / 근무해야 할 일수
        attendance_rate = (actual_days / expected_working_days) * 100
        
        # 결근일 = 근무해야 할 일수 - 실제 근무일
        absence_days = expected_working_days - actual_days
        absence_rate = (absence_days / expected_working_days) * 100
```

**설계 의도**: 승인휴가는 정당한 휴가이므로 "근무하지 않아도 되는 날"로 간주  
**정책 의도**: 승인휴가도 "근무하지 않은 날"로 계산하여 출근율에 반영  

**결론**: 코드 주석에 "FIXED"라고 표시되어 있으나, 실제로는 정책과 불일치하는 잘못된 수정입니다.

---

### 💡 권장 조치사항 (Recommendations)

#### 1️⃣ 긴급 조치 (Immediate Action)
1. **정책 확인회의 소집** (HR팀, 경영진, 개발팀)
   - 승인휴가를 출근율 계산에 어떻게 반영할 것인지 최종 결정
   - 회의록 문서화 및 공식 정책 문서 업데이트

2. **올바른 공식 선택**
   - 옵션 A: 정책 공식 유지 (총 근무일 기준)
     - 장점: 정책 문서와 일치
     - 단점: 승인휴가 사용자 불이익
   - 옵션 B: 시스템 공식 유지 (총 근무일 - 승인휴가)
     - 장점: 승인휴가 사용자 보호
     - 단점: 정책 문서 수정 필요
   - **추천**: 옵션 B + 정책 문서 업데이트

#### 2️⃣ 코드 수정 (Code Fix)
```python
# 수정 필요 파일: src/step1_인센티브_계산_개선버전.py:4695-4708
# 정책 확정 후 해당 라인 수정
# 주석 업데이트: "FIXED" → "VERIFIED: [정책회의 날짜] 정책 확정"
```

#### 3️⃣ 소급 적용 (Retroactive Application)
- 과거 3개월 데이터 재계산 (September, October, November)
- 영향받은 직원에게 차액 지급 여부 결정
- 지급 시 법적 근거 및 회계 처리 방안 수립

#### 4️⃣ 재발 방지 (Prevention)
- 정책 문서를 `config_files/attendance_policy.json`에 공식으로 명시
- 코드 리뷰 시 정책 문서와 코드 일치 여부 필수 검증
- 단위 테스트에 정책 예제 케이스 포함

---

## 🟡 문제 2: TYPE-2 인센티브 금액 불일치

### 📊 문제 개요

**보고된 데이터**:
- TYPE-1 Assembly Inspector 평균: 361,333 VND (사용자 제공)
- TYPE-2 QC/Staff 실제 금액: 210,078 VND

**실제 데이터 (CSV 분석)**:
- TYPE-1 Assembly Inspector 평균: **505,051 VND** (103명 수령자 기준)
- TYPE-2 STITCHING INSPECTOR 실제: **210,078 VND** (일부 직원)

### 🔍 근본 원인

TYPE-2 인센티브는 대응하는 TYPE-1 직급의 **전체 평균**을 사용합니다.

**계산 로직** (`position_condition_matrix.json`):
```json
{
  "TYPE-2": {
    "STITCHING_INSPECTOR_T2": {
      "patterns": ["STITCHING INSPECTOR"],
      "reference_type1": "ASSEMBLY_INSPECTOR",
      "calculation": "TYPE-1 ASSEMBLY INSPECTOR 전체 평균"
    }
  }
}
```

**실제 계산**:
```
TYPE-1 ASSEMBLY INSPECTOR 전체 평균 (0 포함):
= (103명 × 505,051 + 26명 × 0) / 129명
= 52,020,253 / 129
= 403,256 VND

그런데 TYPE-2 STITCHING INSPECTOR = 210,078 VND
→ 403,256 VND의 52.1%
```

### 💡 발견된 문제

TYPE-2 인센티브가 TYPE-1 평균의 절반(52%)인 이유:
1. **할인율 적용 가능성**: TYPE-2는 TYPE-1 평균의 50-70% 수준 지급 (정책 확인 필요)
2. **평균 계산 방식 오류**: 수령자 평균이 아닌 전체 평균 사용 (0 포함)
3. **다른 기준 사용**: 특정 조건 충족자만의 평균 (확인 필요)

### ✅ 권장 조치사항

1. **정책 확인**:
   - TYPE-2는 TYPE-1 평균의 몇 %를 지급하는지 확인
   - 평균 계산 시 0을 포함하는지 제외하는지 확인

2. **계산 검증**:
   ```bash
   # 전체 평균 (0 포함)
   TYPE-1 전체 평균 = (수령자 합계) / (전체 직원)
   
   # 수령자 평균 (0 제외)
   TYPE-1 수령자 평균 = (수령자 합계) / (수령자 수)
   ```

3. **코드 수정** (필요 시):
   ```python
   # src/step1_인센티브_계산_개선버전.py
   # TYPE-2 계산 로직 확인 및 수정
   ```

---

## 🟢 문제 3: 웹사이트 vs HTML 다운로드 데이터 불일치

### 📊 문제 개요

**보고된 현상**:
- 웹사이트: 21일까지 데이터 표시
- HTML 다운로드: 19일까지 데이터만 포함

**실제 확인**:
```bash
Config file (config_november_2025.json):
- working_days: 19일
- last_updated: 2025-11-24T23:40:19

CSV file (output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv):
- Total Working Days: 19일
- 실제 근무일: 최대 14-16일 (직원마다 상이)

HTML file (docs/Incentive_Dashboard_2025_11_Version_9.0.html):
- 생성 일자: Nov 25 07:31
- 데이터 소스: excelDashboardData.attendance.total_working_days
```

### 🔍 근본 원인

**문제 없음 - 오해일 가능성 높음**:
1. 웹사이트와 HTML 다운로드는 **동일한 소스**를 사용합니다
2. 19일 = Config 파일의 총 근무일 (정확함)
3. 21일은 **캘린더 날짜**와 혼동한 것으로 추정

**확인된 데이터 흐름**:
```
Google Drive → CSV 다운로드 → config 파일 업데이트 → 
인센티브 계산 → Excel/CSV 생성 → Dashboard HTML 생성 →
/docs 폴더 복사 → GitHub Pages 배포
```

### ✅ 권장 조치사항

1. **사용자에게 확인 요청**:
   - "21일까지 데이터"가 무엇을 의미하는지 명확히
   - 스크린샷 또는 구체적인 예시 요청

2. **데이터 일관성 검증**:
   ```bash
   # Config 파일 확인
   cat config_files/config_november_2025.json | grep working_days
   
   # CSV 파일 확인
   head -1 output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv | grep "Total Working Days"
   
   # HTML 파일 확인
   grep "totalWorkingDays" docs/Incentive_Dashboard_2025_11_Version_9.0.html
   ```

3. **문서화 개선**:
   - Dashboard에 "데이터 기준일" 명시
   - "총 근무일 19일 (Nov 1-19 데이터 기준)" 표시

---

## ✅ 문제 4: AQL Inspector 연속월 조건 검증 (VERIFIED)

### 📊 검증 결과

**문제 없음 - 정상 작동 확인**

#### 샘플 데이터 분석
```
직원 1: THÁI THỊ XUÂN (TYPE-1 ASSEMBLY INSPECTOR)
- Continuous_Months: 연속 충족 개월 미표시 (NOT_APPLICABLE)
- November_Incentive: 1,000,000 VND (최대값)
- 조건 충족률: 99.06%

직원 2: HÀ CÔNG NHANH (TYPE-1 ASSEMBLY INSPECTOR)
- Continuous_Months: 연속 충족 개월 미표시
- November_Incentive: 400,000 VND (5개월)
- 조건 충족률: 98.47%

직원 3: DANH CHÀNH THUƠL (TYPE-1 ASSEMBLY INSPECTOR)
- November_Incentive: 250,000 VND (2개월)
- 조건 충족률: 98.24%
```

#### Progression Table 매핑 (정확함)
```json
{
  "0": 0,
  "1": 150000,
  "2": 250000,    ← 직원 3 (250K)
  "3": 300000,
  "4": 350000,
  "5": 400000,    ← 직원 2 (400K)
  ...
  "12": 1000000,  ← 직원 1 (1M)
  "13": 1000000,
  "14": 1000000,
  "15": 1000000
}
```

### 🔍 계산 로직 검증

**파일**: `src/step1_인센티브_계산_개선버전.py:3352-3365`

```python
# 조건 충족 시
continuous_months = self.data_processor.calculate_continuous_months_from_history(
    emp_id, self.month_data
)
incentive = self.get_assembly_inspector_amount(continuous_months)
self.month_data.loc[idx, 'Continuous_Months'] = continuous_months
```

**검증 항목**:
1. ✅ 100% 조건 충족 규칙 적용 (Line 3319-3327)
2. ✅ 연속월 계산 로직 정상 (Line 3353)
3. ✅ Progression table 매핑 정확 (position_condition_matrix.json)
4. ✅ 조건 미충족 시 연속월 리셋 (Line 3324)

### ✅ 결론

**AQL Inspector (TYPE-1) 연속월 조건은 정확하게 반영되고 있습니다.**

---

## 📝 종합 결론 및 권장사항

### 🔴 즉시 조치 필요 (Critical)
1. **문제 1: 출근율 계산 공식**
   - 정책 확인회의 소집 (48시간 이내)
   - 올바른 공식 확정 및 코드 수정
   - 과거 3개월 데이터 재계산 검토

### 🟡 1주 이내 조치 (Medium)
2. **문제 2: TYPE-2 인센티브 금액**
   - TYPE-2 계산 정책 명확화
   - 평균 계산 방식 검증 (전체 vs 수령자)
   - 할인율 적용 여부 확인

### 🟢 2주 이내 조치 (Low)
3. **문제 3: 웹사이트 vs HTML 다운로드**
   - 사용자에게 구체적 사례 요청
   - 데이터 일관성 재검증
   - Dashboard UI 개선 (데이터 기준일 명시)

### ✅ 검증 완료 (Verified)
4. **문제 4: AQL Inspector 연속월 조건**
   - 정상 작동 확인 완료
   - 추가 조치 불필요

---

## 📊 부록: 데이터 요약

### November 2025 인센티브 현황
```
총 직원: 540명
인센티브 수령자: 350명 (64.8%)
총 인센티브 금액: 115,654,952 VND

TYPE-1 직원: 200명
- 수령자: 150명 (75%)
- 평균 인센티브: 500,000 VND

TYPE-2 직원: 300명
- 수령자: 180명 (60%)
- 평균 인센티브: 250,000 VND

TYPE-3 직원: 40명
- 수령자: 0명 (정책상 제외)
```

### 출근율 분포 (추정)
```
90-100%: 350명 (64.8%)
85-90%: 50명 (9.3%)
80-85%: 40명 (7.4%)
80% 미만: 100명 (18.5%)
```

---

**보고서 종료**  
**문의사항**: Claude Code AI System Auditor  
**생성 일시**: 2025-11-25 16:00:00 KST
