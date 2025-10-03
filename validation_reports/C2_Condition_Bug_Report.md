# 🐛 C2 조건 버그 보고서

**발견 일시**: 2025-10-03
**버그 유형**: NaN 값 처리 오류
**심각도**: Medium (2명 영향)
**상태**: 🔴 수정 필요

---

## 📊 버그 요약

**Excel 파일에서 무단결근 > 2일인 직원이 14명인데, Validation 리포트는 C2 FAIL이 10명으로 표시**

- Excel: 무단결근 > 2일 = 14명
  - TYPE-3: 6명 (C2 조건 = NaN, 정책적 평가 제외) ✅
  - TYPE-1/2: 8명 (C2 조건 = FAIL, 정상) ✅

- Validation 리포트: C2 FAIL = 10명
  - 정상 FAIL: 8명 ✅
  - **버그로 인한 FAIL: 2명** ❌

**차이 원인**: 2명의 신입사원이 **Unapproved Absences = NaN**임에도 불구하고 **C2 조건이 FAIL**로 잘못 평가됨

---

## 🐛 버그 상세 분석

### 버그 위치

**파일**: `src/step1_인센티브_계산_개선버전.py:4396-4402`

```python
# condition 2: 무단결근 <= 2 days
unapproved_absence = self.month_data.loc[idx, 'Unapproved Absences'] \
    if 'Unapproved Absences' in self.month_data.columns else 0
cond_2_result = 'PASS' if unapproved_absence <= 2 else 'FAIL'  # ❌ 버그!
cond_2_applicable = 'Y' if 2 in applicable_conditions else 'N/A'
self.month_data.loc[idx, 'cond_2_unapproved_absence'] = \
    cond_2_applicable if cond_2_applicable == 'N/A' else cond_2_result
```

### 버그 원인

**NaN 값 비교 오류**:

1. `unapproved_absence`가 **NaN**일 때 (출결 데이터 없는 신입사원)
2. `NaN <= 2`는 Python/pandas에서 **False**로 평가됨
3. 따라서 `else` 블록 실행 → `'FAIL'`로 잘못 평가

```python
import pandas as pd
import numpy as np

# 버그 재현
unapproved_absence = np.nan
result = 'PASS' if unapproved_absence <= 2 else 'FAIL'
# result = 'FAIL' ❌ (잘못된 결과)
```

---

## 👥 영향 받는 직원 (2명)

### 1. THỊ THANH THẢO (ID: 622021338)

- **TYPE**: TYPE-1
- **Position**: ASSEMBLY INSPECTOR
- **Unapproved Absences**: NaN (출결 데이터 없음)
- **현재 C2 조건**: FAIL ❌
- **올바른 C2 조건**: N/A (평가 불가능)

**출근 데이터**:
- Total Working Days: 3.0
- Actual Working Days: 0.0
- AR1 Absences: NaN
- 원본 출결 데이터: 없음 (9월 말 입사 추정)

---

### 2. HỒ THỊ TỐ TRINH (ID: 623100203)

- **TYPE**: TYPE-2
- **Position**: MTL INSPECTOR
- **Unapproved Absences**: NaN (출결 데이터 없음)
- **현재 C2 조건**: FAIL ❌
- **올바른 C2 조건**: N/A (평가 불가능)

**출근 데이터**:
- Total Working Days: 3.0 (9월 말 일부만 근무)
- Actual Working Days: 0.0
- AR1 Absences: NaN
- 원본 출결 데이터: 없음 (9월 말 입사 추정)

---

## ✅ 수정 방안

### 1. 코드 수정

**파일**: `src/step1_인센티브_계산_개선버전.py:4396-4402`

**현재 코드** (Lines 4396-4402):
```python
# condition 2: 무단결근 <= 2 days
unapproved_absence = self.month_data.loc[idx, 'Unapproved Absences'] \
    if 'Unapproved Absences' in self.month_data.columns else 0
cond_2_result = 'PASS' if unapproved_absence <= 2 else 'FAIL'
cond_2_applicable = 'Y' if 2 in applicable_conditions else 'N/A'
self.month_data.loc[idx, 'cond_2_unapproved_absence'] = \
    cond_2_applicable if cond_2_applicable == 'N/A' else cond_2_result
self.month_data.loc[idx, 'cond_2_value'] = unapproved_absence
self.month_data.loc[idx, 'cond_2_threshold'] = 2
```

**수정된 코드**:
```python
# condition 2: 무단결근 <= 2 days
unapproved_absence = self.month_data.loc[idx, 'Unapproved Absences'] \
    if 'Unapproved Absences' in self.month_data.columns else 0

# NaN 처리 추가
if pd.isna(unapproved_absence):
    cond_2_result = 'N/A'  # 출결 데이터 없음
else:
    cond_2_result = 'PASS' if unapproved_absence <= 2 else 'FAIL'

cond_2_applicable = 'Y' if 2 in applicable_conditions else 'N/A'
self.month_data.loc[idx, 'cond_2_unapproved_absence'] = \
    cond_2_applicable if cond_2_applicable == 'N/A' else cond_2_result
self.month_data.loc[idx, 'cond_2_value'] = unapproved_absence
self.month_data.loc[idx, 'cond_2_threshold'] = 2
```

### 2. 재계산 필요

수정 후 전체 데이터를 재계산해야 합니다:

```bash
./action.sh
```

---

## 📊 예상 결과 (수정 후)

### 현재 상태

| 구분 | Excel | Validation 리포트 | 설명 |
|------|-------|------------------|------|
| 무단결근 > 2일 | 14명 | - | Excel 기준 |
| C2 FAIL | - | 10명 | 버그 포함 |
| - TYPE-1/2 정상 FAIL | 8명 | 8명 | ✅ 정상 |
| - TYPE-3 (평가 제외) | 6명 | 0명 | ✅ 정상 (NaN) |
| - **버그로 인한 FAIL** | - | **2명** | ❌ **버그** |

### 수정 후 예상

| 구분 | Excel | Validation 리포트 | 설명 |
|------|-------|------------------|------|
| 무단결근 > 2일 | 14명 | - | Excel 기준 |
| C2 FAIL | - | 8명 | 정상 |
| - TYPE-1/2 정상 FAIL | 8명 | 8명 | ✅ 정상 |
| - TYPE-3 (평가 제외) | 6명 | 0명 | ✅ 정상 (NaN) |
| - NaN → N/A | 2명 | 0명 | ✅ 수정됨 |

---

## 🔍 다른 조건 검증 필요

같은 NaN 처리 버그가 다른 조건에도 있을 수 있습니다:

- **C1 (attendance_rate)**: 확인 필요 ⚠️
- **C3 (actual_working_days)**: 확인 필요 ⚠️
- **C4 (minimum_working_days)**: 확인 필요 ⚠️
- **C5-C10 (AQL, 5PRS)**: 확인 필요 ⚠️

같은 파일의 4313-4533 라인을 검토하여 모든 조건에서 NaN 처리가 올바른지 확인해야 합니다.

---

## 📌 조치 사항

### 1. 즉시 조치 (High Priority)

- [ ] `src/step1_인센티브_계산_개선버전.py:4396-4402` 수정
- [ ] 전체 데이터 재계산 (`./action.sh`)
- [ ] 2명의 직원 C2 조건 확인 (N/A로 변경되었는지)

### 2. 중기 조치 (Medium Priority)

- [ ] C1, C3, C4 조건의 NaN 처리 검증
- [ ] C5-C10 조건의 NaN 처리 검증
- [ ] 단위 테스트 추가 (NaN 케이스)

### 3. 장기 조치 (Low Priority)

- [ ] NaN 처리 표준 정책 수립
- [ ] 코드 리뷰 체크리스트에 NaN 처리 추가
- [ ] 자동 검증 스크립트 개선

---

## 📎 참고 자료

### 관련 파일
- `src/step1_인센티브_계산_개선버전.py:4313-4533` - 조건 평가 함수
- `validation_reports/C2_Condition_Verification_Report.md` - C2 조건 검증 보고서
- `output_files/output_QIP_incentive_september_2025_Complete_V8.01_Complete.xlsx` - 현재 데이터

### Python NaN 동작
```python
import pandas as pd
import numpy as np

# NaN 비교 동작
print(np.nan == np.nan)     # False
print(np.nan < 2)           # False
print(np.nan > 2)           # False
print(np.nan <= 2)          # False
print(np.nan >= 2)          # False

# 올바른 NaN 체크
print(pd.isna(np.nan))      # True
print(pd.notna(np.nan))     # False
```

---

## 📝 결론

**C2 조건 버그**는 NaN 값 처리 누락으로 인해 2명의 신입사원이 잘못 평가되었습니다.

- **버그 심각도**: Medium (2명만 영향, 어차피 인센티브 0원)
- **수정 난이도**: Easy (5줄 코드 추가)
- **재발 방지**: NaN 처리 표준 정책 필요

수정 후 재계산하면 C2 FAIL이 10명 → 8명으로 정상화됩니다.
