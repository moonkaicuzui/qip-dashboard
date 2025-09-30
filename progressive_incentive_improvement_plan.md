# TYPE-1 Progressive Incentive 개선 계획

## 1. 현재 문제점 분석

### 핵심 이슈
- **인센티브 금액과 연속 개월 불일치**
  - Model Masters: 300,000 VND 지급 (3개월 연속 달성 금액)
  - Continuous_Months: 1로 표시 (잘못된 값)
  - 실제로는 3개월 연속 달성을 의미함

### 근본 원인
1. **전월 데이터 추적 시스템 부재**
   - August_Incentive 컬럼 없음
   - 이전 월 인센티브 수령 이력 추적 불가

2. **calculate_continuous_months_from_history 함수 오류**
   - 9월 계산 시 8월 데이터를 제대로 로드하지 못함
   - Progressive 로직이 하드코딩되어 있음

3. **JSON 파일 생성 로직 오류**
   - september_continuous_months가 모두 1로 설정됨
   - 실제 progressive months를 계산하지 않음

## 2. 개선 방안

### 2.1 데이터 구조 개선

```python
# 전월 인센티브 데이터 로드 개선
def load_previous_month_incentive(self, month, year):
    """전월 인센티브 데이터를 로드하여 progressive tracking 지원"""

    # 전월 계산
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # 전월 파일 경로
    prev_file = f'output_files/output_QIP_incentive_{get_month_name(prev_month)}_{prev_year}_*.xlsx'

    # 파일 로드 및 인센티브 컬럼 추출
    if os.path.exists(prev_file):
        prev_df = pd.read_excel(prev_file)
        prev_incentive_col = f'{get_month_name(prev_month).capitalize()}_Incentive'

        # 현재 데이터에 병합
        self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(
            prev_df.set_index('Employee No')[prev_incentive_col]
        )
```

### 2.2 Progressive 개월 수 계산 로직 개선

```python
def calculate_progressive_months(self, emp_id, current_month_passed, previous_incentive):
    """Progressive 개월 수 정확히 계산"""

    # 현재 월 조건을 충족하지 못하면 0으로 리셋
    if not current_month_passed:
        return 0

    # 전월 인센티브 금액으로부터 연속 개월 역산
    incentive_to_months = {
        0: 0,          # 전월 미수령 → 0개월
        150000: 1,     # 전월 1개월 달성
        250000: 2,     # 전월 2개월 달성
        300000: 3,     # 전월 3개월 달성
        350000: 4,     # 전월 4개월 달성
        400000: 5,     # 전월 5개월 달성
        450000: 6,     # 전월 6개월 달성
        500000: 7,     # 전월 7개월 달성
        550000: 8,     # 전월 8개월 달성
        600000: 9,     # 전월 9개월 달성
        650000: 10,    # 전월 10개월 달성
        700000: 11,    # 전월 11개월 달성
        750000: 12     # 전월 12개월 달성
    }

    # 전월 연속 개월 수 확인
    prev_months = incentive_to_months.get(previous_incentive, 0)

    # 당월 연속 개월 = 전월 + 1
    current_months = prev_months + 1

    # 최대 12개월 제한
    return min(current_months, 12)
```

### 2.3 인센티브 계산 함수 수정

```python
def calculate_assembly_inspector_incentive_type1_only(self):
    """TYPE-1 Assembly Inspector 인센티브 계산 (Progressive 로직 포함)"""

    # ... 기존 조건 체크 코드 ...

    # 모든 조건 충족 시
    if all_conditions_met:
        # 전월 인센티브 확인
        previous_incentive = row.get('Previous_Incentive', 0)

        # Progressive 개월 수 계산
        continuous_months = self.calculate_progressive_months(
            emp_id,
            current_month_passed=True,
            previous_incentive=previous_incentive
        )

        # Progressive 테이블에서 금액 결정
        incentive = self.get_progressive_amount(continuous_months)

        # Continuous_Months 컬럼 업데이트
        self.month_data.loc[idx, 'Continuous_Months'] = continuous_months

        print(f"→ {emp_name}: 전월 {previous_incentive:,} VND → "
              f"{continuous_months}개월 연속 → {incentive:,} VND")
```

### 2.4 JSON 파일 생성 로직 수정

```python
def generate_continuous_months_json(df, month, year):
    """정확한 continuous months를 포함한 JSON 생성"""

    progressive_data = {
        "month": month,
        "year": year,
        "employees": {}
    }

    for _, row in df.iterrows():
        if row['ROLE TYPE STD'] == 'TYPE-1':
            emp_id = row['Employee No']

            # Continuous_Months 컬럼에서 실제 값 사용
            continuous_months = row.get('Continuous_Months', 0)

            # 인센티브 금액과 continuous months 검증
            incentive = row[f'{month.capitalize()}_Incentive']
            expected_amount = get_progressive_amount(continuous_months)

            if incentive != expected_amount:
                print(f"⚠️ Warning: {emp_id} incentive mismatch - "
                      f"Months: {continuous_months}, "
                      f"Expected: {expected_amount}, "
                      f"Actual: {incentive}")

            progressive_data["employees"][emp_id] = {
                "name": row['Full Name'],
                "position": row['QIP POSITION 1ST  NAME'],
                "type": row['ROLE TYPE STD'],
                f"{month}_incentive": incentive,
                f"{month}_continuous_months": continuous_months,
                f"{get_next_month(month)}_expected_months": continuous_months + 1
            }
```

## 3. 구현 우선순위

1. **[긴급] 전월 데이터 로드 시스템 구현**
   - load_previous_month_incentive 함수 추가
   - 8월 데이터 로드 및 병합

2. **[중요] Progressive 개월 계산 로직 수정**
   - calculate_progressive_months 함수 개선
   - 인센티브 금액 → 연속 개월 역산 로직

3. **[필수] 인센티브 계산 함수 업데이트**
   - Assembly Inspector 계산 함수 수정
   - Model Master 계산 함수 수정
   - Auditor & Training 계산 함수 수정

4. **[검증] JSON 파일 생성 로직 개선**
   - 정확한 continuous_months 기록
   - 다음 월 예상 개월 수 계산

## 4. 테스트 계획

### 4.1 단위 테스트
- Progressive 개월 계산 로직 테스트
- 인센티브 금액 매핑 테스트
- 전월 데이터 로드 테스트

### 4.2 통합 테스트
- 8월 → 9월 progression 검증
- Model Master 300,000 VND = 3개월 검증
- Assembly Inspector progressive 금액 검증

### 4.3 검증 체크리스트
- [ ] Model Master 3명 모두 Continuous_Months = 3
- [ ] Assembly Inspector progressive 금액 정확성
- [ ] JSON 파일 continuous_months 정확성
- [ ] October_expected_months 계산 정확성

## 5. 예상 결과

### 수정 전
```
Employee: 618030241 (MODEL MASTER)
- September_Incentive: 300,000 VND
- Continuous_Months: 1 (❌ 잘못됨)
```

### 수정 후
```
Employee: 618030241 (MODEL MASTER)
- August_Incentive: 250,000 VND (2개월 달성)
- September_Incentive: 300,000 VND
- Continuous_Months: 3 (✅ 정확함)
- October_Expected: 4 개월
```

## 6. 장기 개선 사항

1. **데이터베이스 도입**
   - 월별 인센티브 이력을 DB에 저장
   - Progressive tracking을 위한 전용 테이블

2. **자동화된 Progressive Tracking**
   - 매월 자동으로 이전 월 데이터 연결
   - Progressive 상태 실시간 모니터링

3. **대시보드 개선**
   - Progressive 진행 상황 시각화
   - 개인별 연속 달성 그래프 추가

## 7. 리스크 및 대응 방안

### 리스크 1: 과거 데이터 부재
- **문제**: 7월 이전 데이터가 없을 수 있음
- **해결**: 7월을 시작점으로 설정, 이전은 0개월로 처리

### 리스크 2: 데이터 불일치
- **문제**: 수동 입력 데이터와 계산 결과 불일치
- **해결**: Validation 로직 강화, 불일치 시 경고 메시지

### 리스크 3: 성능 이슈
- **문제**: 전월 데이터 로드 시 성능 저하
- **해결**: 캐싱 메커니즘 도입, 필요한 컬럼만 로드