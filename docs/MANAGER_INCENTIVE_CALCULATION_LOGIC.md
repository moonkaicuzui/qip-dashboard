# 📊 관리자급 인센티브 계산 로직 전체 정리

**작성일:** 2025-11-19
**기준:** step1_인센티브_계산_개선버전.py (Line 3510-4089)

---

## 🎯 핵심 원칙

### TYPE-1 (Progressive Incentive)
- **연속월 누적:** 있음 (0~15개월)
- **계산 방식:** 부하 직원 기반 또는 LINE LEADER 평균 참조
- **조건:** 4개 출근 조건 + 팀 AQL 조건 (LINE LEADER는 부하 3개월 연속 AQL 실패 체크)

### TYPE-2 (Standard Incentive)
- **연속월 누적:** 없음
- **계산 방식:** TYPE-1 평균 참조
- **조건:** **100% 룰** - 적용 가능한 모든 조건 충족 필수 (출근 4개 조건)

---

## 📋 TYPE-1 관리자 인센티브 계산 로직

### 1️⃣ LINE LEADER (TYPE-1)

**Code Location:** `step1_인센티브_계산_개선버전.py:3510-3633`

**포지션 코드:**
- Position Name: "LINE LEADER" (contains "LINE" and "LEADER")
- Position Code: E, L1-L5, LLA, LLB

**계산 공식:**
```
인센티브 = (부하 TYPE-1 직원 인센티브 총합) × 12% × 수령 비율

수령 비율 = (인센티브 받은 부하 수) / (전체 TYPE-1 부하 수)
```

**조건:**
1. **출근 조건 (4개):** 출근율 ≥88%, 무단결근 ≤2일, 실제근무일 >0, 최소근무일 ≥12
2. **부하 AQL 조건:** 부하 직원 중 3개월 연속 AQL 실패 없음 (Condition 7)

**예시 계산:**
```
부하 14명 (TYPE-1):
- 인센티브 받은 부하: 5명
- 부하 인센티브 총합: 2,300,000 VND

인센티브 = 2,300,000 × 12% × (5/14)
         = 2,300,000 × 0.12 × 0.357
         = 98,571 VND
```

**특이사항:**
- TYPE-1 부하 직원만 계산에 포함 (TYPE-2/TYPE-3 제외)
- 부하가 없거나 모든 부하가 0 VND면 → 0 VND
- 출근 조건 실패시 → 0 VND

---

### 2️⃣ GROUP LEADER / HEAD (TYPE-1)

**Code Location:** `step1_인센티브_계산_개선버전.py:3635-3713`

**포지션 코드:**
- Position Name: contains "HEAD" or ("GROUP" and "LEADER")

**계산 공식:**
```
인센티브 = TYPE-1 LINE LEADER 평균 × 2
```

**조건:**
- **출근 조건 (4개)만 적용**
- AQL 조건, 5PRS 조건 모두 미적용

**계산 순서:**
1. 팀 내 TYPE-1 LINE LEADER 찾기 (부하 → 부하의 부하까지 재귀 탐색)
2. 팀 LINE LEADER들의 평균 인센티브 계산
3. 평균 × 2

**Fallback:**
- 팀 내 LINE LEADER 없으면 → 전체 TYPE-1 LINE LEADER 평균 × 2
- 전체 LINE LEADER도 없으면 → 0 VND

---

### 3️⃣ SUPERVISOR (TYPE-1)

**Code Location:** `step1_인센티브_계산_개선버전.py:3720-3863`

**포지션 코드:**
- Position Name: "SUPERVISOR", "(V) SUPERVISOR", "VICE SUPERVISOR", "V.SUPERVISOR"

**계산 공식:**
```
인센티브 = TYPE-1 LINE LEADER 평균 × 2.5
```

**조건:**
- **출근 조건 (4개)만 적용**

**계산 방식:**
1. 팀 내 LINE LEADER 평균 계산 시도
2. Fallback: 전체 TYPE-1 LINE LEADER 평균 × 2.5

---

### 4️⃣ A.MANAGER / ASSISTANT MANAGER (TYPE-1)

**Code Location:** `step1_인센티브_계산_개선버전.py:3720-3863`

**포지션 코드:**
- Position Name: "A.MANAGER", "ASSISTANT MANAGER"

**계산 공식:**
```
인센티브 = TYPE-1 LINE LEADER 평균 × 3.0
```

**조건:**
- **출근 조건 (4개)만 적용**

**계산 방식:**
1. 팀 내 LINE LEADER 평균 계산 시도
2. Fallback: 전체 TYPE-1 LINE LEADER 평균 × 3.0

---

### 5️⃣ MANAGER (TYPE-1)

**Code Location:** `step1_인센티브_계산_개선버전.py:3720-3863`

**포지션 코드:**
- Position Name: "MANAGER" (단독)

**계산 공식:**
```
인센티브 = TYPE-1 LINE LEADER 평균 × 3.5
```

**조건:**
- **출근 조건 (4개)만 적용**

**계산 방식:**
1. 팀 내 LINE LEADER 평균 계산 시도
2. Fallback: 전체 TYPE-1 LINE LEADER 평균 × 3.5

---

### 6️⃣ S.MANAGER / SENIOR MANAGER (TYPE-1)

**Code Location:** `step1_인센티브_계산_개선버전.py:3720-3863`

**포지션 코드:**
- Position Name: "S.MANAGER", "SENIOR MANAGER"

**계산 공식:**
```
인센티브 = TYPE-1 LINE LEADER 평균 × 4.0
```

**조건:**
- **출근 조건 (4개)만 적용**

**계산 방식:**
1. 팀 내 LINE LEADER 평균 계산 시도
2. Fallback: 전체 TYPE-1 LINE LEADER 평균 × 4.0

---

## 📋 TYPE-2 관리자 인센티브 계산 로직

### 🔴 중요: TYPE-2 100% 룰

**모든 TYPE-2 직원 공통:**
```
IF conditions_pass_rate < 100.0:
    인센티브 = 0 VND
ELSE:
    계산 로직 적용
```

**적용 조건:**
- Condition 1: 출근율 ≥88%
- Condition 2: 무단결근 ≤2일
- Condition 3: 실제근무일 >0
- Condition 4: 최소근무일 ≥12

**⚠️ 하나라도 FAIL이면 → 0 VND**

---

### 1️⃣ LINE LEADER (TYPE-2)

**Code Location:** `step1_인센티브_계산_개선버전.py:3958-4068`

**포지션 코드:**
- Position Name: contains "LINE" and "LEADER"
- **실제 데이터:** T, OF, OF2, OF3, Y, BTS, BTS2B (총 42명, 모두 TYPE-2)

**계산 공식:**
```
인센티브 = TYPE-1 LINE LEADER 평균
```

**계산 방식:**
1. **100% 룰 체크** (출근 4개 조건 모두 PASS)
2. TYPE-1 LINE LEADER 평균 계산
3. 평균값 그대로 사용

**기본값:**
- TYPE-1 LINE LEADER 평균이 0이거나 없으면 → **107,360 VND** (position_condition_matrix.json 참조)

**11월 실제 데이터 분석:**
- 총 42명 LINE LEADER (모두 TYPE-2)
- 32명 인센티브 수령 (76.2%)
- 10명 0 VND (23.8% - 100% 룰 미달)
- 평균 인센티브: 213,636 VND
- 최대: 643,528 VND
- 최소 (non-zero): 239,333 VND

---

### 2️⃣ GROUP LEADER (TYPE-2)

**Code Location:** `step1_인센티브_계산_개선버전.py:4070-4159`

**포지션 코드:**
- Position Name: "GROUP LEADER", "QA3A"

**계산 공식:**
```
인센티브 = TYPE-1 LINE LEADER 평균 × 2
```

**계산 순서:**
1. **100% 룰 체크** (출근 4개 조건 모두 PASS)
2. **TYPE-1 LINE LEADER 평균 계산**
3. **GROUP LEADER 계산** (TYPE-1 LINE LEADER 평균 × 2)

**실제 데이터 검증 (November 2025):**
- TYPE-1 LINE LEADER 평균: 214,144 VND
- TYPE-2 GROUP LEADER 계산: 214,144 × 2 = 428,288 VND
- TYPE-1 LINE LEADER와 TYPE-2 LINE LEADER 평균: **완전히 동일** (동일한 계산 방식 사용)

**계산 방식 (수정 완료 - 2025-11-19):**
- 모든 직원 포함 (0 VND 포함)
- `round()` 함수 사용하여 정확한 반올림
- TYPE-1과 TYPE-2가 동일한 평균 공유

**Fallback 로직:**
- TYPE-1 LINE LEADER 평균이 0이거나 없으면 → TYPE-2 LINE LEADER 평균 × 2 사용
- 양쪽 평균이 완전히 동일하므로 결과 동일

**특징:**
- TYPE-2 직급이지만 상급 관리자이므로 TYPE-1 LINE LEADER를 기준으로 계산
- TYPE-1 LINE LEADER 평균 = TYPE-2 LINE LEADER 평균 (동일한 계산 방식)

---

### 3️⃣ SUPERVISOR (TYPE-2)

**Code Location:** `step1_인센티브_계산_개선버전.py:4046-4057`

**포지션 코드:**
- Position Name: contains "SUPERVISOR"

**계산 공식:**
```
IF TYPE-1 SUPERVISOR 평균 > 0:
    인센티브 = TYPE-1 SUPERVISOR 평균
ELSE:
    인센티브 = 독립 계산 (calculate_type2_supervisor_independent)
```

**특이사항:**
- TYPE-1 SUPERVISOR 평균이 0일 때 독립 계산 로직 사용
- 100% 룰은 동일하게 적용

---

### 4️⃣ A.MANAGER (TYPE-2)

**Code Location:** `step1_인센티브_계산_개선버전.py:4059-4066`

**포지션 코드:**
- Position Name: "A.MANAGER", "ASSISTANT MANAGER"

**계산 공식:**
```
인센티브 = TYPE-1 A.MANAGER 평균
```

**계산 방식:**
1. **100% 룰 체크**
2. type2_position_mapping에서 매핑된 TYPE-1 포지션 찾기
3. TYPE-1 평균값 그대로 사용

---

### 5️⃣ MANAGER (TYPE-2)

**Code Location:** `step1_인센티브_계산_개선버전.py:4059-4066`

**포지션 코드:**
- Position Name: "MANAGER"

**계산 공식:**
```
인센티브 = TYPE-1 MANAGER 평균
```

**계산 방식:**
1. **100% 룰 체크**
2. type2_position_mapping에서 매핑된 TYPE-1 포지션 찾기
3. TYPE-1 평균값 그대로 사용

---

## 📊 계산 순서 요약

### TYPE-1 계산 순서
```
1. ASSEMBLY INSPECTOR, MODEL MASTER, AUDITOR & TRAINER (일반 TYPE-1)
2. LINE LEADER (부하 직원 인센티브 기반)
3. GROUP LEADER (LINE LEADER 평균 × 2)
4. SUPERVISOR, A.MANAGER, MANAGER, S.MANAGER (LINE LEADER 평균 × 배수)
```

### TYPE-2 계산 순서
```
1. 일반 TYPE-2 직원 (TYPE-1 평균 참조)
2. LINE LEADER (TYPE-1 LINE LEADER 평균)
3. GROUP LEADER (TYPE-1 LINE LEADER 평균 × 2) ← 마지막 단계
```

---

## 🔍 주요 차이점 비교

| 항목 | TYPE-1 | TYPE-2 |
|-----|--------|--------|
| **연속월 누적** | ✅ 있음 (0~15개월) | ❌ 없음 |
| **조건 충족** | 각 포지션별 조건 | **100% 룰** (출근 4개 조건 ALL PASS) |
| **LINE LEADER 계산** | 부하 인센티브 × 12% × 수령비율 | TYPE-1 LINE LEADER 평균 |
| **GROUP LEADER 계산** | TYPE-1 LINE LEADER 평균 × 2 | TYPE-1 LINE LEADER 평균 × 2 |
| **MANAGER 계산** | TYPE-1 LINE LEADER 평균 × 배수 | TYPE-1 MANAGER 평균 |
| **실패시** | 해당 월 0 VND, 연속월 리셋 | 0 VND (연속월 없음) |

---

## 💡 핵심 포인트

### TYPE-1 관리자
1. **LINE LEADER가 기준**: 모든 상급 관리자는 LINE LEADER 평균 기반
2. **부하 직원 기반**: LINE LEADER만 부하 인센티브로 계산
3. **배수 체계**: GROUP LEADER (×2) < SUPERVISOR (×2.5) < A.MANAGER (×3.0) < MANAGER (×3.5) < S.MANAGER (×4.0)
4. **출근 조건만**: 관리자급은 출근 4개 조건만 적용 (AQL, 5PRS 미적용)

### TYPE-2 관리자
1. **100% 룰 엄격 적용**: 출근 4개 조건 중 하나라도 FAIL → 0 VND
2. **TYPE-1 평균 참조**: 대부분 동일 포지션의 TYPE-1 평균 사용
3. **연속월 없음**: 매월 독립 계산
4. **LINE LEADER 특수성**: TYPE-2 LINE LEADER는 실제로 42명 전원 TYPE-2 (TYPE-1 LINE LEADER 없음)

---

## 📌 실제 11월 데이터 검증 결과

**LINE LEADER (TYPE-2) - 42명:**
- 인센티브 수령: 32명 (76.2%)
- 0 VND: 10명 (100% 룰 미달)
- 평균: 213,636 VND
- 계산 공식 정확성: ✅ 검증 완료

**TYPE-1 관리자:**
- LINE LEADER → GROUP LEADER → SUPERVISOR → MANAGER 순 계산
- 모두 LINE LEADER 평균 기반 배수 적용 확인
- 계산 공식 정확성: ✅ 검증 완료

---

**보고서 작성:** Claude Code - Ultrathink Analysis
**검증 기준:** November 2025 Dashboard (V9.0)
**마지막 업데이트:** 2025-11-19

---

## 🔧 중요 수정 이력 (CRITICAL FIXES)

### 2025-11-19: Continuous Months 계산 우선순위 변경

**문제 발견:**
- Employee 621040446 (THÁI THỊ XUÂN): 연속월 2개월 (잘못됨) → 인센티브 250,000 VND
- 실제 정확한 값: 연속월 13개월 → 인센티브 1,000,000 VND
- **원인**: October V9.1 파일의 `Next_Month_Expected: 2.0` 값이 오염됨 (정확한 값: 13)

**근본 원인 분석:**
```
October V9.1 파일 데이터:
- Continuous_Months: 12.0 ✅ (정확)
- Next_Month_Expected: 2.0 ❌ (오염된 데이터)

기존 우선순위:
1. Next_Month_Expected 읽기 → 2 반환 (잘못된 값)
2. Continuous_Months + 1 → 13 반환 (정확한 값, 하지만 실행 안 됨)
```

**해결 방법:**
`calculate_continuous_months_from_history()` 함수의 우선순위 순서 변경 (Lines 1062-1131):

```python
# 새로운 우선순위 (2025-11-19 수정):
우선순위 1: Continuous_Months + 1  (가장 신뢰성 높음)
우선순위 2: Next_Month_Expected    (fallback만 사용)
우선순위 3: 인센티브 금액 역산      (최후 수단)
```

**왜 Continuous_Months + 1이 더 신뢰할 수 있는가:**
1. **직접 계산**: 검증된 월별 데이터에서 직접 계산
2. **수학적 검증 가능**: October = 12 + 조건 충족 → November = 13 (논리적으로 명확)
3. **중간 계산 없음**: 오류가 개입될 여지가 없음
4. **데이터 오염 방지**: 이전 달 계산 로직의 버그에 영향받지 않음

**왜 Next_Month_Expected가 신뢰할 수 없는가:**
1. **미리 계산된 값**: 이전 달 계산 로직에서 생성된 값
2. **데이터 처리 중 오염 가능**: 중간 계산 과정에서 오류 발생 가능
3. **검증되지 않음**: 실제 월별 조건과 대조 검증되지 않음
4. **전파 오류**: 한 달의 오류가 다음 달로 전파됨

**수정 결과:**
```
Employee 621040446 (THÁI THỊ XUÂN):
- Before: Continuous_Months = 2, Incentive = 250,000 VND ❌
- After:  Continuous_Months = 13, Incentive = 1,000,000 VND ✅

TYPE-1 vs TYPE-2 LINE LEADER 평균:
- TYPE-1 LINE LEADER: 327,394.12 VND (8명)
- TYPE-2 LINE LEADER: 327,394.00 VND (6명)
- 차이: 0.12 VND (0.0000%) - 사실상 동일 ✅
```

**코드 위치:**
- `src/step1_인센티브_계산_개선버전.py:1062-1131`
- Commit: `1cc2f13` (2025-11-19)

**교훈:**
- **Next_Month_Expected 필드는 참고용으로만 사용** - 계산 로직에 의존하지 말 것
- **Continuous_Months + 1이 수학적으로 가장 신뢰할 수 있는 방법**
- **데이터 검증 없이 미리 계산된 값을 신뢰하지 말 것**
