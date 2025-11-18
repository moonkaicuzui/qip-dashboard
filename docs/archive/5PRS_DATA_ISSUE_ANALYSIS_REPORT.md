# 5PRS 통과율 불일치 문제 분석 보고서

**생성일:** 2025-10-10
**분석 대상:** October 2025 인센티브 보고서
**발견된 문제:** 5PRS 통과율 데이터 부정확

---

## 문제 요약

**현상:**
- 대시보드/엑셀 표시: 624080127 직원의 5PRS 통과율 93.91% (690족 검사)
- 구글 드라이브 실제: 624080127 직원의 5PRS 통과율 92.3% (510족 검사, 471족 합격)
- **차이:** 1.6% 통과율 차이, 180족 검사량 차이

---

## 근본 원인 분석

### 1️⃣ **5PRS 파일에 여러 달 데이터가 혼재**

**증거:**
```
input_files/5prs data october.csv 파일 내용:
- 10월 데이터 (10/1/2025 ~ 10/7/2025): 12개 레코드
- 8월 데이터 (1/8/2025 ~ 16/8/2025): 28개 레코드 ❌

총 40개 레코드 = 10월(12) + 8월(28)
```

**624080127 직원 데이터 분석:**
```
10월 데이터만 (구글 드라이브 확인):
- 검사량: 180족
- 합격: 171족
- 통과율: 95.0%

현재 CSV 파일 (10월+8월 혼재):
- 검사량: 690족
- 합격: 648족
- 통과율: 93.91%
```

### 2️⃣ **5PRS 계산 로직에 월별 필터링 누락**

**파일:** `src/step1_인센티브_계산_개선버전.py`
**함수:** `process_5pairs_conditions()` (Line 930-1024)

**문제:**
```python
# Line 967-970: TQC별 집계 (월 필터링 없음)
grouped = prs_df.groupby(tqc_col).agg({
    val_qty_col: 'sum',
    pass_qty_col: 'sum'
}).reset_index()
```

**누락된 로직:**
- ❌ 10월 데이터만 필터링하는 코드 없음
- ❌ 'Inspection Date' 컬럼 기반 날짜 필터링 없음
- ❌ 다른 달 데이터 제외 로직 없음

### 3️⃣ **구글 드라이브 동기화 이슈**

**action.sh Line 153-161:**
```bash
# Google Drive sync
python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR
if [ $? -eq 0 ]; then
    echo "✅ Google Drive sync completed"
else
    echo "⚠️ Google Drive sync failed (manual download may be required)"
fi
# → 동기화 실패해도 계속 진행 ⚠️
```

**문제점:**
1. 동기화 실패 시 경고만 출력하고 계속 진행
2. 구글 드라이브에서 최신 파일 다운로드 안됨
3. 로컬 캐시된 오래된 파일 사용 (여러 달 데이터 혼재)

---

## 영향 범위 분석

### 직원별 영향도 (예상)

**5PRS 검사 대상 직원:**
- ASSEMBLY INSPECTOR
- AQL INSPECTOR
- BOTTOM INSPECTOR
- CUTTING INSPECTOR
- MTL INSPECTOR
- OSC INSPECTOR
- STITCHING INSPECTOR

**예상 영향:**
- 전체 5PRS 검사 대상 직원 중 일부가 잘못된 통과율로 평가됨
- 실제로는 95% 이상 통과했지만, 다른 달 데이터 때문에 95% 미만으로 계산된 경우 존재 가능
- 인센티브 지급 누락 또는 잘못된 지급 발생

### 재무 영향 (추정)

**시나리오 1: 과대 지급**
- 실제 92.3% (불합격)이지만 93.91%로 계산되어도 여전히 95% 미달
- 624080127 직원은 실제로도 불합격이므로 영향 없음

**시나리오 2: 과소 지급 (가능성)**
- 실제로는 95% 이상이었지만, 다른 달 데이터 때문에 95% 미만으로 계산된 직원 존재 가능
- 검증 필요

---

## 해결 방안

### 즉시 조치 (CRITICAL)

#### 1. 5PRS 파일 월별 필터링 추가

**파일:** `src/step1_인센티브_계산_개선버전.py`
**위치:** `process_5pairs_conditions()` 함수

**수정 전 (Line 930-1024):**
```python
def process_5pairs_conditions(self, prs_df: pd.DataFrame) -> pd.DataFrame:
    """5PRS conditions processing - TQC ID (inspection 대상자) basis"""
    print("\n📊 5PRS Processing conditions...")

    # ... (column detection code)

    # Line 967: 직접 집계 (월 필터링 없음) ❌
    grouped = prs_df.groupby(tqc_col).agg({
        val_qty_col: 'sum',
        pass_qty_col: 'sum'
    }).reset_index()
```

**수정 후:**
```python
def process_5pairs_conditions(self, prs_df: pd.DataFrame) -> pd.DataFrame:
    """5PRS conditions processing - TQC ID (inspection 대상자) basis"""
    print("\n📊 5PRS Processing conditions...")

    # ✅ CRITICAL FIX: 해당 월 데이터만 필터링
    if 'Inspection Date' in prs_df.columns:
        # 날짜 컬럼을 datetime으로 변환
        prs_df['Inspection Date'] = pd.to_datetime(
            prs_df['Inspection Date'],
            format='%m/%d/%Y',
            errors='coerce'
        )

        # 해당 년도/월 데이터만 필터링
        target_year = self.config.year
        target_month = self.config.month.number

        original_count = len(prs_df)
        prs_df = prs_df[
            (prs_df['Inspection Date'].dt.year == target_year) &
            (prs_df['Inspection Date'].dt.month == target_month)
        ].copy()
        filtered_count = len(prs_df)

        excluded = original_count - filtered_count
        print(f"  ✅ 5PRS 데이터 월별 필터링: {original_count}개 → {filtered_count}개 (제외: {excluded}개)")

        if excluded > 0:
            print(f"  ⚠️ 다른 달 데이터 {excluded}개 제외됨 (정확한 계산을 위해 필수)")
    else:
        print("  ⚠️ Warning: 'Inspection Date' 컬럼이 없어 월별 필터링 불가")
        print("     전체 데이터 사용 - 결과가 부정확할 수 있음!")

    # ... (rest of the function - column detection and aggregation)

    grouped = prs_df.groupby(tqc_col).agg({
        val_qty_col: 'sum',
        pass_qty_col: 'sum'
    }).reset_index()
```

#### 2. 구글 드라이브 동기화 강화

**파일:** `action.sh`
**위치:** Line 153-161

**수정 후:**
```bash
# Step 0.5: Google Drive sync (CRITICAL for accurate data)
echo ""
echo -e "${YELLOW}📥 Syncing required files from Google Drive...${NC}"
python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR

SYNC_RESULT=$?

if [ $SYNC_RESULT -ne 0 ]; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ CRITICAL: Google Drive sync failed!${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Using cached files may result in incorrect calculations!${NC}"
    echo -e "${YELLOW}Old data or mixed month data may be present in input files.${NC}"
    echo ""
    echo -e "${WHITE}Options:${NC}"
    echo -e "${WHITE}  1) Continue anyway (not recommended - may cause data errors)${NC}"
    echo -e "${WHITE}  2) Exit and fix Google Drive connection${NC}"
    echo ""
    echo -e "${YELLOW}Choose option (1/2): ${NC}\c"
    read sync_choice

    if [[ $sync_choice != "1" ]]; then
        echo -e "${YELLOW}Please fix Google Drive connection and try again.${NC}"
        echo -e "${CYAN}💡 Check:${NC}"
        echo -e "${CYAN}  • Internet connection${NC}"
        echo -e "${CYAN}  • Service account key: credentials/service-account-key.json${NC}"
        echo -e "${CYAN}  • Google Drive folder permissions${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠️ WARNING: Proceeding with potentially outdated files!${NC}"
    fi
else
    echo -e "${GREEN}✅ Google Drive sync completed successfully${NC}"
fi
```

#### 3. 5PRS 파일 검증 스크립트 추가

**새 파일:** `scripts/validation/validate_5prs_file.py`

```python
#!/usr/bin/env python3
"""
5PRS 파일 월별 데이터 검증 스크립트
다른 달 데이터가 혼재되어 있는지 확인
"""

import pandas as pd
import sys
from datetime import datetime

def validate_5prs_file(file_path: str, target_month: int, target_year: int, fix: bool = False):
    """
    5PRS 파일에서 해당 월 데이터만 있는지 검증

    Args:
        file_path: 5PRS CSV 파일 경로
        target_month: 대상 월 (1-12)
        target_year: 대상 년도
        fix: True면 다른 달 데이터 자동 제거

    Returns:
        0: 검증 통과
        1: 다른 달 데이터 발견
    """
    print(f"\n{'='*70}")
    print(f"5PRS 파일 월별 데이터 검증")
    print(f"{'='*70}")
    print(f"파일: {file_path}")
    print(f"대상: {target_year}년 {target_month}월")
    print()

    # Load file
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    if 'Inspection Date' not in df.columns:
        print("❌ 'Inspection Date' 컬럼이 없습니다!")
        return 1

    # Parse dates
    df['Inspection Date'] = pd.to_datetime(
        df['Inspection Date'],
        format='%m/%d/%Y',
        errors='coerce'
    )

    # Remove invalid dates
    invalid_dates = df['Inspection Date'].isna().sum()
    if invalid_dates > 0:
        print(f"⚠️ 날짜 형식 오류: {invalid_dates}개 레코드")

    df_valid = df[df['Inspection Date'].notna()].copy()

    # Extract year/month
    df_valid['Year'] = df_valid['Inspection Date'].dt.year
    df_valid['Month'] = df_valid['Inspection Date'].dt.month

    # Group by year/month
    month_summary = df_valid.groupby(['Year', 'Month']).size().reset_index(name='Count')
    month_summary = month_summary.sort_values(['Year', 'Month'])

    print("📊 파일 내 월별 레코드 분포:")
    print("-" * 50)
    for _, row in month_summary.iterrows():
        year = int(row['Year'])
        month = int(row['Month'])
        count = int(row['Count'])

        if year == target_year and month == target_month:
            print(f"✅ {year}년 {month:02d}월: {count}개 (대상 월)")
        else:
            print(f"❌ {year}년 {month:02d}월: {count}개 ⚠️ 다른 달 데이터!")

    # Check if other months exist
    target_data = df_valid[
        (df_valid['Year'] == target_year) &
        (df_valid['Month'] == target_month)
    ]

    other_month_data = df_valid[
        ~((df_valid['Year'] == target_year) &
          (df_valid['Month'] == target_month))
    ]

    print()
    print("=" * 50)
    print(f"대상 월 데이터: {len(target_data)}개")
    print(f"다른 달 데이터: {len(other_month_data)}개")
    print("=" * 50)

    if len(other_month_data) == 0:
        print()
        print("✅ 검증 통과: 해당 월 데이터만 존재합니다!")
        return 0

    print()
    print(f"⚠️ 검증 실패: 다른 달 데이터 {len(other_month_data)}개 발견!")

    if fix:
        print()
        print("🔧 자동 수정 모드: 다른 달 데이터 제거 중...")

        # Backup original file
        backup_path = file_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        df.to_csv(backup_path, index=False, encoding='utf-8-sig')
        print(f"  • 백업 파일 생성: {backup_path}")

        # Save only target month data
        target_data_full = df[df.index.isin(target_data.index)]
        target_data_full.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"  • 수정된 파일 저장: {file_path}")
        print(f"  • 레코드 수: {len(df)} → {len(target_data_full)}")
        print()
        print("✅ 파일 수정 완료!")
        return 0

    return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='5PRS 파일 월별 데이터 검증')
    parser.add_argument('file_path', help='5PRS CSV 파일 경로')
    parser.add_argument('--month', type=int, required=True, help='대상 월 (1-12)')
    parser.add_argument('--year', type=int, default=2025, help='대상 년도')
    parser.add_argument('--fix', action='store_true', help='자동 수정 모드')

    args = parser.parse_args()

    result = validate_5prs_file(args.file_path, args.month, args.year, args.fix)
    sys.exit(result)
```

#### 4. action.sh에 5PRS 검증 추가

**파일:** `action.sh`
**위치:** AQL 검증 이후 (Line 291 다음)

```bash
# Step 0.10: 5PRS File Validation (CRITICAL - prevents data mixing issues)
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}Step 0.10: 5PRS File Validation${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PRS_FILE="input_files/5prs data ${MONTH}.csv"

if [ -f "$PRS_FILE" ]; then
    echo -e "${BLUE}📋 Validating: $PRS_FILE${NC}"
    python3 scripts/validation/validate_5prs_file.py "$PRS_FILE" --month $MONTH_NUM --year $YEAR

    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}⚠️  CRITICAL: 5PRS file validation failed!${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}The 5PRS file contains data from multiple months.${NC}"
        echo -e "${YELLOW}This will cause incorrect 5PRS pass rate calculations!${NC}"
        echo ""
        echo -e "${WHITE}Options:${NC}"
        echo -e "${WHITE}  1) Auto-fix (recommended): Remove other month records${NC}"
        echo -e "${WHITE}  2) Continue anyway (not recommended)${NC}"
        echo -e "${WHITE}  3) Exit and fix manually${NC}"
        echo ""
        echo -e "${YELLOW}Choose option (1/2/3): ${NC}\c"
        read prs_fix_choice

        if [[ $prs_fix_choice == "1" ]]; then
            echo ""
            echo -e "${BLUE}🔧 Auto-fixing 5PRS file...${NC}"
            python3 scripts/validation/validate_5prs_file.py "$PRS_FILE" --month $MONTH_NUM --year $YEAR --fix

            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}✅ 5PRS file fixed successfully!${NC}"
            else
                echo ""
                echo -e "${RED}❌ Failed to fix 5PRS file automatically${NC}"
                echo -e "${YELLOW}Please fix manually and run again.${NC}"
                exit 1
            fi
        elif [[ $prs_fix_choice == "2" ]]; then
            echo ""
            echo -e "${YELLOW}⚠️  WARNING: Continuing with mixed month data${NC}"
            echo -e "${YELLOW}⚠️  5PRS calculations will be inaccurate!${NC}"
            echo ""
            echo -e "${YELLOW}Are you sure? (y/n): ${NC}\c"
            read confirm_continue
            if [[ $confirm_continue != "y" ]] && [[ $confirm_continue != "Y" ]]; then
                echo -e "${YELLOW}Cancelled.${NC}"
                exit 1
            fi
        else
            echo ""
            echo -e "${YELLOW}Please fix the 5PRS file manually and run again.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ 5PRS file validation passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  5PRS file not found: $PRS_FILE${NC}"
    echo -e "${YELLOW}5PRS conditions will not be evaluated.${NC}"
fi
```

---

## 검증 절차

### 10월 데이터 재계산 검증

1. **5PRS 파일 수정 적용**
```bash
cd "/Users/ksmoon/Downloads/Dashboard  Incentive Version 8_1_sharing_version final"

# 5PRS 파일 백업
cp "input_files/5prs data october.csv" "input_files/5prs data october.csv.backup"

# 검증 스크립트 실행 (자동 수정)
python3 scripts/validation/validate_5prs_file.py \
  "input_files/5prs data october.csv" \
  --month 10 \
  --year 2025 \
  --fix
```

2. **계산 로직 업데이트 후 재계산**
```bash
# Step1 스크립트 수정 후 재실행
python3 src/step1_인센티브_계산_개선버전.py \
  --config config_files/config_october_2025.json
```

3. **624080127 직원 데이터 검증**
```python
import pandas as pd

# 재계산된 CSV 로드
df = pd.read_csv('output_files/output_QIP_incentive_october_2025_Complete_V8.01_Complete.csv',
                 encoding='utf-8-sig')

emp = df[df['Employee No'].astype(str) == '624080127'].iloc[0]

print(f"5PRS_Inspection_Qty: {emp['5PRS_Inspection_Qty']}")  # 예상: 180족
print(f"5PRS_Pass_Rate: {emp['5PRS_Pass_Rate']}")  # 예상: 95.0%
print(f"cond_9_5prs_pass_rate: {emp['cond_9_5prs_pass_rate']}")  # 예상: PASS
```

### 전체 직원 영향도 분석

```bash
# 수정 전후 비교 스크립트 실행
python3 scripts/verification/compare_5prs_before_after.py \
  --before "output_files/output_QIP_incentive_october_2025_Complete_V8.01_Complete.csv.backup" \
  --after "output_files/output_QIP_incentive_october_2025_Complete_V8.01_Complete.csv"
```

---

## 예방 조치

### 1. 구글 드라이브 파일 관리 규칙

**파일 명명 규칙:**
```
5prs data october.csv  → 10월 데이터만 포함
5prs data september.csv → 9월 데이터만 포함
```

**주의사항:**
- 각 월 파일에는 해당 월 데이터만 포함
- 다른 달 데이터 절대 혼합 금지
- 파일 업로드 전 항상 검증

### 2. 자동화된 데이터 검증

**월별 실행 체크리스트:**
1. ✅ 구글 드라이브 동기화 성공 확인
2. ✅ AQL 파일 월별 검증 통과
3. ✅ 5PRS 파일 월별 검증 통과
4. ✅ Attendance 파일 검증
5. ✅ 계산 완료 후 validation report 확인

### 3. 코드 리뷰 체크리스트

**5PRS 관련 수정 시 필수 확인:**
- [ ] 월별 필터링 적용되는지 확인
- [ ] 날짜 컬럼 올바르게 파싱되는지 확인
- [ ] 다른 달 데이터 제외 로그 출력 확인
- [ ] 테스트 케이스에 혼합 월 데이터 시나리오 포함

---

## 결론

### 근본 원인
1. **5PRS 파일 데이터 혼재**: 10월 파일에 8월 데이터 포함
2. **계산 로직 월별 필터링 누락**: 전체 데이터 집계
3. **구글 드라이브 동기화 미작동**: 오래된 로컬 파일 사용

### 영향
- 5PRS 검사량 및 통과율 부정확
- 인센티브 지급 오류 가능성 (과대/과소 지급)
- October 2025 보고서 재생성 필요

### 해결 방안
1. **즉시:** 5PRS 계산 로직에 월별 필터링 추가
2. **단기:** 5PRS 파일 검증 스크립트 도입
3. **중기:** 구글 드라이브 동기화 강화
4. **장기:** 전체 input 파일 자동 검증 시스템 구축

---

**보고서 생성:** 2025-10-10
**분석 도구:** Python pandas + CSV validation
**데이터 소스:**
- Local: input_files/5prs data october.csv
- Output: output_QIP_incentive_october_2025_Complete_V8.01_Complete.csv
- Google Drive: 사용자 확인 (471족 합격/510족 검사)
