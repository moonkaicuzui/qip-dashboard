# C1 조건 검증 결과 보고서

**검증 일시**: 2025-10-03
**검증 대상**: C1 조건 (출근율 >= 88%)
**검증 월**: September 2025

---

## 1️⃣ 승인 휴가 계산 로직 분석

**파일**: `src/step1_인센티브_계산_개선버전.py` (Lines 4302-4307)

```python
def calculate_approved_leave_days(self, emp_no: str) -> int:
    """직원의 승인된 휴가 일수 계산 (AR1 아닌 모든 Reason Description)"""
    # AR1 아닌 사유만 승인휴가로 집계
    # AR1 = 무단결근, 나머지 = 승인휴가 (출산휴, 연차, 병가, 출장 등)
    approved_leave = emp_attendance[
        emp_attendance['Reason Description'].notna() &
        ~emp_attendance['Reason Description'].str.startswith('AR1', na=False)
    ]
    return len(approved_leave)
```

### ⚠️ 핵심 발견

- 스크립트는 **AR1이 아닌 모든 Reason Description**을 승인 휴가로 처리
- **AR2 (단기 병가)도 승인 휴가로 간주됨**
- 이는 attendance rate를 인위적으로 높이는 효과 발생

---

## 2️⃣ AR1 vs AR2 차이점

### 📌 AR1 (무단 결근 - Unauthorized Absence)

- AR1 - Vắng không phép (무단 결근)
- AR1 - Gửi thư (경고장 발송)
- 출근율 계산 시 분모에서 제외되지 않음
- Unapproved Absences 카운트에 포함

### 📌 AR2 (단기 병가 - Short-term Sick Leave)

- AR2 - ốm ngắn ngày, tai nạn ngoài giờ lv (단기 병가, 근무 외 사고)
- **현재 스크립트**: 승인 휴가로 처리 → 분모에서 제외 → 출근율 상승
- **검증 스크립트**: 승인 휴가 아님 → 분모에 포함 → 출근율 하락

---

## 3️⃣ 문제 직원 상세 분석

### 👤 직원 1: HUỲNH HOÀI THƯƠNG (ID: 623120027)

**📊 출근 데이터**
- 실제 출근일: 5일
- 총 근무일: 19일

**🟢 진짜 승인 휴가 (2일)**
- 2025-09-03: Vắng có phép
- 2025-09-08: Vắng có phép

**🟡 AR2 단기 병가 (2일) - 논쟁 중**
- 2025-09-04: AR2 - ốm ngắn ngày
- 2025-09-05: AR2 - ốm ngắn ngày

**📈 출근율 계산 차이**

**스크립트 방식 (AR2를 승인휴가로 처리)**
- 승인 휴가: 4일 (진짜 2일 + AR2 2일)
- 계산: 5 / (19 - 4) × 100
- 결과: **33.33%** ✅ (CSV 값)

**검증 방식 (AR2를 일반 결근으로 처리)**
- 승인 휴가: 2일 (진짜 승인 휴가만)
- 계산: 5 / (19 - 2) × 100
- 결과: **29.41%** ❌ (검증 스크립트 값)

**🔺 차이: 3.92%p**

---

### 👤 직원 2: DƯƠNG LÝ BẰNG (ID: 619080448)

**📊 출근 데이터**
- 실제 출근일: 17일
- 총 근무일: 24일

**🟢 진짜 승인 휴가 (2일)**
- 2025-09-16: Vắng có phép
- 2025-09-19: Phép năm

**🟡 AR2 단기 병가 (2일) - 논쟁 중**
- 2025-09-22: AR2 - ốm ngắn ngày
- 2025-09-23: AR2 - ốm ngắn ngày

**📈 출근율 계산 차이**

**스크립트 방식 (AR2를 승인휴가로 처리)**
- 승인 휴가: 4일 (진짜 2일 + AR2 2일)
- 계산: 17 / (24 - 4) × 100
- 결과: **85.00%** ✅ (CSV 값)

**검증 방식 (AR2를 일반 결근으로 처리)**
- 승인 휴가: 2일 (진짜 승인 휴가만)
- 계산: 17 / (24 - 2) × 100
- 결과: **77.27%** ❌ (검증 스크립트 값)

**🔺 차이: 7.73%p**

---

## 4️⃣ 비즈니스 로직 질문

### ❓ AR2 (단기 병가) 처리 방식 결정 필요

#### 옵션 A: AR2를 승인 휴가로 처리 (현재 스크립트 방식)
- **장점**: 단기 병가로 인한 불이익 최소화
- **단점**: 출근율이 실제보다 높게 계산됨
- **예시**: DƯƠNG LÝ BẰNG 85.00% → C1 FAIL (88% 미만)

#### 옵션 B: AR2를 일반 결근으로 처리 (엄격한 방식)
- **장점**: 실제 출근율 반영
- **단점**: 병가로 인한 출근율 하락
- **예시**: DƯƠNG LÝ BẰNG 77.27% → C1 FAIL (88% 미만)

#### 옵션 C: AR2를 별도 카테고리로 처리
- 분모에서 제외하지 않되, 무단결근으로도 카운트 안함
- position_condition_matrix.json에 별도 조건 추가

---

## 5️⃣ 검증 결과 요약

### ✅ 확인된 사항

1. **CSV 데이터는 스크립트 로직대로 정확하게 계산되었음**
2. 차이는 **AR2 (단기 병가)를 승인 휴가로 처리**하는 비즈니스 로직 때문
3. 6/10 C1 FAIL 직원은 AR2 없어서 완벽 일치
4. 2/10 C1 FAIL 직원은 AR2 때문에 출근율 차이 발생
5. 2/10 C1 FAIL 직원은 신입사원 (출근 데이터 없음)

### ⚠️ 조치 필요

1. **AR2 처리 방식에 대한 비즈니스 결정 필요**
2. 결정 후 필요시 `calculate_approved_leave_days()` 함수 수정
3. 수정 시 전체 직원 재계산 필요 (`action.sh` 재실행)

---

## 📌 결론

**현재 시스템은 정확하게 작동하고 있습니다.**

CSV와 검증 스크립트의 차이는 **AR2 (단기 병가) 처리 방식의 차이**입니다.

### 회사 정책에 따라 AR2를 어떻게 처리할지 결정해주세요

- **승인 휴가로 인정** → 현재 로직 유지
- **일반 결근으로 처리** → 스크립트 수정 필요
  - 파일: `src/step1_인센티브_계산_개선버전.py:4302-4307`
  - 수정: AR2도 approved leave에서 제외하도록 로직 변경
- **별도 카테고리** → JSON 설정 추가 필요
  - 파일: `config_files/position_condition_matrix.json`
  - 추가: AR2 관련 별도 조건 정의

---

## 📎 참고 자료

### 관련 파일
- `src/step1_인센티브_계산_개선버전.py` - 출근율 계산 로직
- `input_files/attendance/converted/attendance data september_converted.csv` - 원본 출근 데이터
- `output_files/output_QIP_incentive_september_2025_Complete_V8.01_Complete.csv` - 계산 결과

### 주요 함수
- `calculate_approved_leave_days()` - Lines 4283-4311
- `add_condition_evaluation_to_excel()` - Lines 4313-4533
