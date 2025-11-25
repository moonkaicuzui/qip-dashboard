# AQL Inspector 월별 업데이트 및 검증 가이드
## Monthly Update Process and Verification Method

**작성일**: 2025-11-25
**대상**: TYPE-1 AQL INSPECTOR 인센티브 계산

---

## 목차
1. [개요](#개요)
2. [엑셀 파일에서 매월 업데이트되는 데이터](#엑셀-파일에서-매월-업데이트되는-데이터)
3. [자동 vs 수동 업데이트](#자동-vs-수동-업데이트)
4. [전월 대비 검증 방법](#전월-대비-검증-방법)
5. [11월 인센티브 검증 (10월 데이터 기준)](#11월-인센티브-검증-10월-데이터-기준)

---

## 개요

AQL Inspector는 **TYPE-1 직급**으로 3가지 구성 요소(Part 1, 2, 3)를 합산하여 인센티브를 받습니다:

```
총 인센티브 = Part 1 + Part 2 + Part 3

Part 1: AQL 검사 평가 결과 (연속 달성 개월에 따라 차등)
Part 2: CFA 자격증 보유 인센티브 (고정 700,000 VND)
Part 3: HWK 클레임 방지 인센티브 (연속 개월에 따라 차등)
```

### 핵심 메커니즘: **Continuous Months (연속 달성 개월)**

- **Part 1**: 2개월 이상 Level-A 평가 시 차등 인센티브
  - 1개월: 150,000 VND
  - 2-11개월: 150K → 950K (progression_table 기준)
  - 12개월 이상: 1,000,000 VND (cap)

- **Part 3**: HWK 클레임 없는 개월 수 누적
  - 0-3개월: 0 VND
  - 4-6개월: 300,000 VND
  - 7-9개월: 500,000 VND
  - 10-12개월: 700,000 VND
  - 13-15개월: 900,000 VND

**중요**: 조건 실패 시 연속 개월 수가 0으로 리셋됩니다!

---

## 엑셀 파일에서 매월 업데이트되는 데이터

### 파일 경로
```
output_files/output_QIP_incentive_[month]_[year]_Complete_V9.0_Complete.csv
output_files/output_QIP_incentive_[month]_[year]_Complete_V9.0_Complete.xlsx
```

### 매월 변경되는 칼럼 (AQL Inspector 대상)

#### 1. **Continuous_Months** (연속 달성 개월)
- **설명**: 현재 월의 연속 달성 개월 수
- **업데이트 로직**:
  ```python
  if 모든 조건 충족:
      Continuous_Months = 전월 Continuous_Months + 1
  else:
      Continuous_Months = 0  # 리셋
  ```
- **예시**:
  - 10월: 13개월 (모든 조건 충족)
  - 11월: 14개월 (10월 13 + 1) ← **예상값**
  - 11월 실제: 13개월 ← **실제값 (BUG!)**

#### 2. **{Month}_Incentive** (해당 월 인센티브)
- **설명**: 해당 월에 받는 총 인센티브 금액
- **업데이트 로직**:
  ```python
  if Continuous_Months >= 2:  # Part 1 적용
      part1 = progression_table[Continuous_Months]
  else:
      part1 = 150000  # 1개월만 달성

  part2 = 700000  # CFA 자격증 (고정)

  part3 = hwk_prevention_table[Continuous_Months]

  Total = part1 + part2 + part3
  ```
- **예시**:
  - 13개월: 1,000,000 + 700,000 + 900,000 = **2,600,000 VND**
  - 7개월: 500,000 + 700,000 + 500,000 = **1,700,000 VND**

#### 3. **Next_Month_Expected** (다음 달 예상 개월)
- **설명**: 다음 달에 예상되는 연속 개월 수
- **업데이트 로직**:
  ```python
  if 현재 월 모든 조건 충족:
      Next_Month_Expected = Continuous_Months + 1
  else:
      Next_Month_Expected = 0  # 리셋 예상
  ```
- **예시**:
  - 10월 Continuous_Months: 13 → Next_Month_Expected: 14
  - 11월 Continuous_Months: 14 → Next_Month_Expected: 15 (cap at 15)

#### 4. **조건 충족 여부** (Condition 1-10)
- 매월 새로운 출근 데이터, AQL 데이터, 5PRS 데이터로 재평가
- YES/NO 값 변경 가능

---

## 자동 vs 수동 업데이트

### ✅ **자동 업데이트** (현재 시스템)

#### Google Drive → CSV 다운로드
- **주기**: 매시간 (GitHub Actions cron)
- **파일**:
  - 출근 데이터 (attendance data november.csv)
  - AQL 히스토리 (1.HSRG AQL REPORT-NOVEMBER.2025.csv)
  - 5PRS 데이터 (5prs data november.csv)
  - 기본 인력 데이터 (basic manpower data november.csv)

#### 인센티브 계산 실행
- **스크립트**: `src/step1_인센티브_계산_개선버전.py`
- **자동 실행**: GitHub Actions workflow
- **결과**: Excel/CSV 파일 생성

#### 대시보드 HTML 생성
- **스크립트**: `integrated_dashboard_final.py`
- **자동 실행**: GitHub Actions workflow
- **배포**: GitHub Pages (1-2분 후 웹 반영)

### ❌ **수동 업데이트 필요** (현재 시스템의 문제점)

#### config_files/aql_inspector_incentive_config.json
- **문제**: 이 파일은 자동으로 업데이트되지 않습니다!
- **현재 상태**: June 2025 데이터 (6개월 전 데이터)
- **필요 상태**: November 2025 데이터 (최신 데이터)

**파일 구조**:
```json
{
  "aql_inspectors": {
    "620020923": {
      "name": "BÙI TRƯƠNG NGỌC NHỨT",
      "cfa_certified": true,
      "november_2025_incentive": {
        "part1_months": 13,  ← 이 값이 다음 달 계산의 기준
        "part3_months": 14,
        "total": 2600000
      }
    }
  }
}
```

**영향**:
- 11월 계산 시 10월 데이터를 읽어야 하는데, 6월 데이터를 읽음
- 결과: Continuous_Months 증가하지 않음 (13 → 13, should be 13 → 14)

**해결 방법** (2025-11-25 현재):
1. **임시 스크립트 생성**: Python 스크립트로 수동 업데이트
2. **향후 개선**: action.sh 또는 GitHub Actions에 통합 필요

---

## 전월 대비 검증 방법

### 검증할 칼럼 (10월 → 11월 비교)

#### 1. **Continuous_Months 증가 확인**
```
10월 파일: output_QIP_incentive_october_2025_Complete_V9.1_Complete.csv
11월 파일: output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv

검증 공식:
IF (10월 모든 조건 충족):
    11월 Continuous_Months = 10월 Continuous_Months + 1
ELSE:
    11월 Continuous_Months = 0
```

#### 2. **인센티브 금액 변화 확인**
```
10월 Continuous_Months → 11월 Continuous_Months → 인센티브 변화

예시 1: 13 → 14 (증가)
  - 10월: 1,000K + 700K + 900K = 2,600K VND
  - 11월: 1,000K + 700K + 900K = 2,600K VND (동일 - cap 도달)

예시 2: 7 → 8 (증가)
  - 10월: 500K + 700K + 500K = 1,700K VND
  - 11월: 650K + 700K + 500K = 1,850K VND (+150K)
```

#### 3. **Next_Month_Expected 검증**
```
10월 Next_Month_Expected = 14
11월 Continuous_Months should be = 14

실제:
10월 Next_Month_Expected = NaN (비어있음)
11월 Continuous_Months = 13 (잘못됨!)
```

---

## 11월 인센티브 검증 (10월 데이터 기준)

### 실제 검증 결과 (2025-11-25)

#### Employee: LÊ NGỌC LÂM MỸ HUỲNH (618110077)
```
10월 데이터:
  - Continuous_Months: 13
  - October_Incentive: 2,600,000 VND
  - Next_Month_Expected: NaN

11월 데이터:
  - Continuous_Months: 13 ← 예상: 14 ❌
  - November_Incentive: 2,600,000 VND
  - Next_Month_Expected: NaN

검증 결과:
  - Continuous_Months 증가하지 않음 (13 → 13)
  - 인센티브 동일 (cap 도달이므로 정상)
  - **ROOT CAUSE**: Config 파일이 June 데이터 사용 (12개월 + 1 = 13)
```

#### Employee: NGUYỄN NGÔ TUYẾT NGÂN (620120306)
```
10월 데이터:
  - Continuous_Months: 7
  - October_Incentive: 1,700,000 VND
  - Next_Month_Expected: NaN

11월 데이터:
  - Continuous_Months: 7 ← 예상: 8 ❌
  - November_Incentive: 1,700,000 VND (예상: 1,850,000) ❌
  - Next_Month_Expected: NaN

검증 결과:
  - Continuous_Months 증가하지 않음 (7 → 7)
  - 인센티브 150,000 VND 부족
  - **ROOT CAUSE**: 동일 (Config 파일 문제)
```

### 검증 단계 (Excel 파일 사용)

#### Step 1: 10월 Excel 파일 열기
```
파일: output_QIP_incentive_october_2025_Complete_V9.1_Complete.xlsx
시트: Complete Data
```

#### Step 2: AQL Inspector 필터링
```
Column: QIP POSITION 1ST NAME
Filter: "AQL INSPECTOR"

Column: ROLE TYPE STD
Filter: "TYPE-1"
```

#### Step 3: 핵심 칼럼 확인
```
Employee No | Full Name | Continuous_Months | October_Incentive | Next_Month_Expected
```

#### Step 4: 11월 Excel과 비교
```
파일: output_QIP_incentive_november_2025_Complete_V9.0_Complete.xlsx

비교 공식:
  Nov_Continuous_Months == Oct_Continuous_Months + 1 (if all conditions met)
  Nov_Incentive == calculated_from_progression_table(Nov_Continuous_Months)
```

---

## 전월 대비 수치 기준

### Continuous_Months 기준

| 전월 개월 | 조건 충족 | 당월 개월 | 인센티브 변화 (Part 1 + Part 3) |
|---------|---------|---------|---------------------------|
| 0       | YES     | 1       | 150K + 0 = 150K VND      |
| 1       | YES     | 2       | 250K + 0 = 250K VND (+100K) |
| 3       | YES     | 4       | 350K + 300K = 650K VND (+400K) |
| 6       | YES     | 7       | 500K + 500K = 1,000K VND (+350K) |
| 7       | YES     | 8       | 650K + 500K = 1,150K VND (+150K) |
| 11      | YES     | 12      | 1,000K + 700K = 1,700K VND (+250K) |
| 12      | YES     | 13      | 1,000K + 900K = 1,900K VND (+200K) |
| 13      | YES     | 14      | 1,000K + 900K = 1,900K VND (±0) |
| 14      | YES     | 15 (cap) | 1,000K + 900K = 1,900K VND (±0) |
| 任意     | NO      | 0       | 150K + 0 = 150K VND (리셋) |

**Note**: Part 2 (CFA 자격증 700K VND) 는 항상 고정

### 인센티브 총액 기준 (Part 1 + Part 2 + Part 3)

| Continuous_Months | Part 1  | Part 2 | Part 3 | 총액     | 전월 대비 변화 |
|------------------|---------|--------|--------|----------|-------------|
| 1                | 150K    | 700K   | 0      | 850K     | -           |
| 2                | 250K    | 700K   | 0      | 950K     | +100K       |
| 4                | 350K    | 700K   | 300K   | 1,350K   | +400K       |
| 7                | 500K    | 700K   | 500K   | 1,700K   | +350K       |
| 8                | 650K    | 700K   | 500K   | 1,850K   | +150K       |
| 12               | 1,000K  | 700K   | 700K   | 2,400K   | +250K       |
| 13               | 1,000K  | 700K   | 900K   | 2,600K   | +200K       |
| 14               | 1,000K  | 700K   | 900K   | 2,600K   | ±0 (cap)    |
| 15 (cap)         | 1,000K  | 700K   | 900K   | 2,600K   | ±0 (cap)    |

---

## 향후 개선 사항

### 1. Config 파일 자동 업데이트
```bash
# action.sh에 다음 단계 추가:
# Step 7: AQL Inspector Config Update
python scripts/update_aql_inspector_config.py --month 11 --year 2025

# 또는 GitHub Actions workflow에 통합
```

### 2. 검증 자동화
```bash
# 월별 검증 스크립트 추가
python scripts/verification/validate_aql_inspector_progression.py \
  --prev_month october --current_month november --year 2025

# 검증 내용:
# - Continuous_Months 증가 로직
# - 인센티브 금액 계산 정확성
# - Config 파일 업데이트 여부
```

### 3. 대시보드 표시 개선
```html
<!-- 전월 대비 변화 표시 -->
<div class="aql-inspector-progress">
  <span class="prev-month">10월: 13개월 (2,600K VND)</span>
  <span class="arrow">→</span>
  <span class="current-month">11월: 14개월 (2,600K VND)</span>
  <span class="change">±0 VND (cap 도달)</span>
</div>
```

---

## 요약

### 매월 업데이트되는 데이터
1. ✅ **자동**: Google Drive CSV 파일 (출근, AQL, 5PRS, 인력)
2. ✅ **자동**: 조건 평가 결과 (YES/NO)
3. ✅ **자동**: Continuous_Months 계산 (단, config 파일이 최신이어야 함)
4. ✅ **자동**: 인센티브 금액 계산
5. ❌ **수동**: `config_files/aql_inspector_incentive_config.json` 업데이트

### 검증 방법
1. **10월 Excel 파일** 에서 `Continuous_Months` 확인
2. **11월 Excel 파일** 에서 `Continuous_Months` 확인
3. **비교**: 11월 = 10월 + 1 (조건 충족 시)
4. **인센티브 검증**: progression_table 기준 금액 확인

### 현재 문제 (2025-11-25)
- ❌ Config 파일이 June 2025 데이터를 사용
- ❌ Continuous_Months가 증가하지 않음 (10월 13 → 11월 13, should be 14)
- ❌ 2명의 직원이 150K VND씩 손실 (7개월 → 8개월 미반영)

### 해결 방법
- ✅ 임시: Python 스크립트로 config 파일 수동 업데이트
- ⏳ 향후: action.sh 또는 GitHub Actions에 자동화 통합

---

**마지막 업데이트**: 2025-11-25
**작성자**: Claude Code Analysis
**참조**: CLAUDE.md, MANAGER_INCENTIVE_CALCULATION_LOGIC.md
