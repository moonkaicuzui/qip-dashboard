# AQL 파일 검증 가이드

## 문제 개요

### October 2025 사례
- **문제**: October AQL 파일에 September 데이터(MONTH=9) 1건 포함
- **원인**: 첫 행 MONTH=9 → Validation 실패 → September 데이터가 October로 사용됨
- **결과**: CSV에 31명(September) 대신 5명(October)이어야 하는데 잘못된 데이터 포함

### 근본 원인
```python
# 기존 validation (src/step1_인센티브_계산_개선버전.py:1195-1243)
month_value = df['MONTH'].iloc[0]  # ❌ 첫 행만 확인!
```

**위험**:
- 첫 행만 올바르면 통과 → 나머지 행의 오류 미검출
- Mixed-month 데이터 → 전체 파일 거부 → 이전 월 데이터 사용

## 예방 방법

### 1. 매월 AQL 파일 검증 (필수)

**11월 보고서 생성 전**:
```bash
# AQL 파일 검증
python3 scripts/validation/validate_aql_file.py \
  "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv"

# 문제 발견 시 자동 수정
python3 scripts/validation/validate_aql_file.py \
  "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv" \
  --fix
```

**12월, 1월 등 모든 월 동일**:
```bash
python3 scripts/validation/validate_aql_file.py \
  "input_files/AQL history/1.HSRG AQL REPORT-DECEMBER.2025.csv"
```

### 2. action.sh에 자동 통합 (권장)

**action.sh에 다음 단계 추가**:
```bash
# Step 2.5: AQL 파일 사전 검증 (인센티브 계산 전)
echo "=================================="
echo "Step 2.5: AQL 파일 검증 중..."
echo "=================================="

AQL_FILE="input_files/AQL history/1.HSRG AQL REPORT-${MONTH_UPPER}.${YEAR}.csv"

if [ -f "$AQL_FILE" ]; then
    python3 scripts/validation/validate_aql_file.py "$AQL_FILE" --month $MONTH_NUM

    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  AQL 파일에서 문제가 발견되었습니다!"
        echo ""
        read -p "자동으로 수정하시겠습니까? (y/n): " fix_choice

        if [[ $fix_choice == "y" ]]; then
            python3 scripts/validation/validate_aql_file.py "$AQL_FILE" --month $MONTH_NUM --fix
            echo "✅ AQL 파일 수정 완료"
        else
            echo "❌ AQL 파일 문제를 수정하지 않으면 계산 결과가 부정확할 수 있습니다."
            read -p "계속 진행하시겠습니까? (y/n): " continue_choice
            if [[ $continue_choice != "y" ]]; then
                exit 1
            fi
        fi
    else
        echo "✅ AQL 파일 검증 통과"
    fi
else
    echo "⚠️  AQL 파일을 찾을 수 없습니다: $AQL_FILE"
fi
```

### 3. 검증 항목

스크립트가 자동으로 확인하는 항목:

1. **첫 행 월 확인** (기존 로직 호환)
   - 파일명의 월과 첫 행 MONTH 값 비교
   - 불일치 시 CRITICAL 오류

2. **전체 행 월 확인** (NEW)
   - 모든 행의 MONTH 값 검사
   - 여러 월 혼재 시 CRITICAL 오류
   - 잘못된 월 레코드 상세 정보 제공

3. **날짜 일관성 확인**
   - DATE 컬럼이 MONTH 값과 일치하는지 확인
   - 불일치 시 WARNING

4. **통계 제공**
   - 총 레코드 수
   - 월별 분포 ({9: 1, 10: 233})
   - 잘못된 레코드 예시 (날짜, 직원 번호)

### 4. 자동 수정 기능

`--fix` 옵션 사용 시:
```bash
python3 scripts/validation/validate_aql_file.py \
  "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv" \
  --fix
```

**동작**:
1. 자동 백업 생성 (`.backup_YYYYMMdd_HHmmss`)
2. 잘못된 월 레코드 제거
3. 수정된 파일 저장
4. 재검증 실행
5. 결과 리포트

## 실제 사용 예시

### October 2025 문제 파일

**검증 결과**:
```
📋 AQL 파일 검증 리포트
================================================================================
파일: input_files/AQL history/1.HSRG AQL REPORT-OCTOBER.2025.csv.backup
검증 시각: 2025-10-07 11:25:17

📊 통계:
   총 레코드: 234건
   파일명 월: 10
   예상 월: 10
   월별 분포: {10: 233, 9: 1}

🔍 검증 결과: ❌ FAIL

📝 발견된 문제 (5건):
   ❌ CRITICAL: 첫 행 월 불일치 - 예상=10, 실제=9
               (기존 validation 로직에서 파일 거부됨!)
   ❌ CRITICAL: 여러 월 데이터 혼재 - [9, 10]
               (총 234건 중 월별: {10: 233, 9: 1})
      → 월 9: 1건 (날짜 예시: ['9/3/2025'], 직원 예시: [625060019])
   ⚠️ WARNING: 1건의 레코드가 예상 월(10)과 다릅니다
   ⚠️ WARNING: 1건의 DATE가 예상 월과 다릅니다
```

**수정 후**:
```
📋 AQL 파일 검증 리포트
================================================================================
파일: input_files/AQL history/1.HSRG AQL REPORT-OCTOBER.2025.csv
검증 시각: 2025-10-07 11:25:06

📊 통계:
   총 레코드: 233건
   파일명 월: 10
   예상 월: 10
   월별 분포: {10: 233}

🔍 검증 결과: ✅ PASS

✅ 문제 없음 - 모든 검증 통과!
```

## 향후 발생 방지

### 단기 대책 (즉시 적용)

1. **매월 검증 루틴 추가**
   ```bash
   # 11월 인센티브 계산 전
   python3 scripts/validation/validate_aql_file.py \
     "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv"
   ```

2. **action.sh 자동화** (위 가이드 참조)

3. **월별 체크리스트**:
   - [ ] AQL 파일 업로드
   - [ ] **검증 스크립트 실행** (NEW)
   - [ ] 인센티브 계산
   - [ ] Dashboard 생성
   - [ ] 데이터 검증

### 중기 대책 (개발 필요)

**src/step1_인센티브_계산_개선버전.py 개선**:

```python
# 기존 (첫 행만 확인)
def get_latest_three_months():
    # ...
    month_value = df['MONTH'].iloc[0]  # ❌ 취약점

# 개선안 (전체 행 확인)
def get_latest_three_months():
    # ...
    # 1. 첫 행 확인 (기존 로직)
    first_month = df['MONTH'].iloc[0]

    # 2. 전체 행 확인 (NEW)
    unique_months = df['MONTH'].unique()
    if len(unique_months) > 1:
        print(f"⚠️ {filename_month}: 여러 월 혼재 - {sorted(unique_months)}")
        print(f"   → 자동 필터링: 월 {month_num}만 사용")
        df = df[df['MONTH'] == month_num]  # 올바른 월만 필터링

    # 3. Validation
    if filename_month.upper() == month_name.upper():
        valid_months[month_num] = filename_month
    # ...
```

### 장기 대책 (프로세스 개선)

1. **데이터 입력 자동화**
   - Google Drive에서 AQL 파일 다운로드 시 월 필터 자동 적용
   - 파일명과 데이터 월 일치 강제

2. **CI/CD 파이프라인**
   - AQL 파일 업로드 시 자동 검증
   - 문제 발견 시 이메일 알림
   - 자동 수정 후 재검증

3. **데이터 품질 모니터링**
   - 월별 데이터 품질 리포트
   - 이상 패턴 자동 감지
   - 예방적 알림 시스템

## FAQ

### Q1: 11월 보고서 생성 시 무엇을 확인해야 하나요?

```bash
# 1. AQL 파일 검증
python3 scripts/validation/validate_aql_file.py \
  "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv"

# 2. 문제 발견 시 자동 수정
python3 scripts/validation/validate_aql_file.py \
  "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv" \
  --fix

# 3. 인센티브 계산 진행
./action.sh
```

### Q2: 이 문제가 왜 발생했나요?

**데이터 입력 단계**: AQL 파일 생성 시 월 필터링 부족
- October 파일에 September 데이터(9/3/2025, employee 625060019) 포함
- 수동 작업 또는 데이터 병합 시 검증 누락

**Validation 약점**: 첫 행만 확인 → 나머지 행 오류 미검출

### Q3: 같은 문제가 12월, 1월에도 발생할 수 있나요?

**예, 발생 가능합니다.**
- 데이터 입력 프로세스가 개선되지 않으면 재발 가능
- **해결책**: 매월 검증 스크립트 실행 (이 가이드 따르기)

### Q4: 자동 수정이 안전한가요?

**안전합니다**:
- 수정 전 자동 백업 생성 (`.backup_타임스탬프`)
- 원본 파일 보존
- 수정 후 재검증 실행
- 되돌리기 가능: `mv 백업파일 원본파일`

### Q5: action.sh에 통합하면 어떻게 되나요?

**자동 워크플로우**:
1. 월/년 선택
2. Config 생성
3. **AQL 파일 자동 검증** (NEW)
4. 문제 발견 시 수정 옵션 제공
5. 인센티브 계산
6. Dashboard 생성
7. 데이터 검증

**장점**:
- 사람이 깜빡할 가능성 제거
- 일관된 품질 보장
- 문제 조기 발견

## 체크리스트

### 11월 보고서 생성 전 필수 확인사항

- [ ] AQL 파일 업로드 완료
- [ ] **검증 스크립트 실행**: `python3 scripts/validation/validate_aql_file.py "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv"`
- [ ] 검증 결과 ✅ PASS 확인
- [ ] 문제 발견 시 `--fix` 옵션으로 자동 수정
- [ ] 재검증 통과 확인
- [ ] 인센티브 계산 진행

### 12월, 1월 등 매월 동일 체크리스트 적용

---

**생성일**: 2025-10-07
**작성자**: Claude Code
**버전**: 1.0
**관련 이슈**: October 2025 AQL 데이터 불일치 문제
