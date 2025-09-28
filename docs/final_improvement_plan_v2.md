# 최종 개선 계획: Python 자체 계산 구현
## Final Improvement Plan: Python Self-Calculation Implementation

작성일: 2025-09-28
버전: 2.0

## 1. 현재 상황 정리

### 발견된 문제
1. **ĐINH KIM NGOAN (617100049)**: TYPE-2 GROUP LEADER, 조건 100% 충족, 0 VND
2. **다른 5명 GROUP LEADER**: 동일 조건 100% 충족, 214,720 VND
3. **원인**: Python 계산 순서 문제 (GROUP LEADER가 LINE LEADER 계산에 의존)

### Python 계산 로직 (확인됨)
```
TYPE-1 GROUP LEADER 평균이 0 → TYPE-2 LINE LEADER 평균 × 2 사용
TYPE-2 LINE LEADER 5명이 107,360원 받음
평균 × 2 = 214,720원 (정상 계산)
하지만 ĐINH KIM NGOAN만 0원 (비정상)
```

## 2. 개선 방안: 2단계 계산 방식

### Phase 1: Python 스크립트 수정

#### A. 계산 순서 분리 (step1_인센티브_계산_개선버전.py)

```python
def calculate_all_incentives(self):
    """모든 타입별 인센티브 계산 - 2단계 방식"""
    print("\n🎯 인센티브 계산 시작...")

    # STEP 1: LINE LEADER & 일반 직원 먼저 계산
    print("\n[STEP 1] LINE LEADER 및 일반 직원 계산...")
    self.calculate_type1_non_leaders()  # TYPE-1 일반 직원
    self.calculate_type2_line_leaders() # TYPE-2 LINE LEADER

    # STEP 2: GROUP LEADER 계산 (LINE LEADER 평균 사용)
    print("\n[STEP 2] GROUP LEADER 계산...")
    self.calculate_type1_group_leaders()
    self.calculate_type2_group_leaders()

    # TYPE-3 계산 (항상 0원)
    self.calculate_type3_incentives()
```

#### B. TYPE-2 GROUP LEADER 계산 개선

```python
def calculate_type2_group_leaders(self):
    """TYPE-2 GROUP LEADER 계산 - 개선된 버전"""

    type2_group_mask = (
        (self.month_data['ROLE TYPE STD'] == 'TYPE-2') &
        (self.month_data['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
    )

    # TYPE-1 GROUP LEADER 평균
    type1_avg = self.get_type1_group_leader_average()

    # TYPE-2 LINE LEADER 평균
    type2_line_avg = self.get_type2_line_leader_average()

    for idx, row in self.month_data[type2_group_mask].iterrows():
        # 조건 충족 확인 (출근 조건 1-4만)
        if not self.check_attendance_conditions(row):
            incentive = 0
        elif type1_avg > 0:
            # TYPE-1 평균 사용
            incentive = type1_avg
        elif type2_line_avg > 0:
            # TYPE-2 LINE LEADER 평균 × 2
            incentive = int(type2_line_avg * 2)
        else:
            # 기본값 (position_condition_matrix.json에서)
            incentive = 107360 * 2  # 기본 LINE LEADER × 2

        self.month_data.loc[idx, 'September_Incentive'] = incentive

        # 디버깅 정보
        if row['Employee No'] == '617100049':
            print(f"ĐINH KIM NGOAN 계산:")
            print(f"  조건 충족: {self.check_attendance_conditions(row)}")
            print(f"  TYPE-1 평균: {type1_avg}")
            print(f"  TYPE-2 LINE 평균: {type2_line_avg}")
            print(f"  최종 인센티브: {incentive}")
```

#### C. 소스 CSV 값 무시 옵션 추가

```python
def prepare_integrated_data(self):
    """통합 데이터 준비"""

    # 설정 옵션 추가
    IGNORE_SOURCE_VALUES = True  # 소스 값 무시하고 재계산

    if IGNORE_SOURCE_VALUES:
        # 기존 인센티브 칼럼 백업 후 제거
        if 'September_Incentive' in self.month_data.columns:
            self.month_data['Source_September_Incentive'] = self.month_data['September_Incentive']
            self.month_data['September_Incentive'] = 0
            print("⚠️ 소스 CSV의 September_Incentive 무시하고 재계산")

        if 'Final Incentive amount' in self.month_data.columns:
            self.month_data['Source_Final_Amount'] = self.month_data['Final Incentive amount']
            del self.month_data['Final Incentive amount']
```

### Phase 2: 대시보드 개선

#### A. 계산 투명성 표시 (dashboard_complete.js)

```javascript
// Individual Details 모달에 계산 근거 추가
function showCalculationDetails(employee) {
    let calcHTML = '';

    if (employee.role_type === 'TYPE-2' && employee.position === 'GROUP LEADER') {
        calcHTML = `
            <div class="alert alert-info mt-3">
                <h6>💡 계산 근거</h6>
                <p>TYPE-2 GROUP LEADER 계산 방식:</p>
                <ul>
                    <li>TYPE-1 GROUP LEADER 평균이 있으면 → 그 값 사용</li>
                    <li>TYPE-1 평균이 0이면 → TYPE-2 LINE LEADER 평균 × 2</li>
                    <li>현재: TYPE-2 LINE LEADER 평균 107,360 × 2 = 214,720 VND</li>
                </ul>
                ${employee.september_incentive === 0 ?
                    '<p class="text-danger">⚠️ 조건을 충족했지만 0원인 경우 시스템 점검이 필요합니다.</p>' : ''}
            </div>
        `;
    }

    return calcHTML;
}
```

#### B. 공정성 검증 추가

```javascript
// 대시보드 로드 시 공정성 체크
function checkFairness() {
    const type2GroupLeaders = employeeData.filter(e =>
        e.role_type === 'TYPE-2' &&
        e.position === 'GROUP LEADER' &&
        e.conditions_pass_rate === 100
    );

    const incentives = [...new Set(type2GroupLeaders.map(e => e.september_incentive))];

    if (incentives.length > 1) {
        console.warn('⚠️ 공정성 문제 발견:');
        console.warn('동일 조건의 TYPE-2 GROUP LEADER들이 다른 인센티브를 받고 있습니다.');
        console.table(type2GroupLeaders.map(e => ({
            name: e.full_name,
            employee_no: e.employee_no,
            incentive: e.september_incentive
        })));

        // 사용자에게 경고 표시
        showFairnessWarning(type2GroupLeaders);
    }
}
```

### Phase 3: 검증 스크립트 생성

```python
# verify_calculation_fairness.py
def verify_type2_group_leaders():
    """TYPE-2 GROUP LEADER 공정성 검증"""

    df = pd.read_csv('output_files/latest_output.csv', encoding='utf-8-sig')

    # TYPE-2 GROUP LEADER 100% 충족자 확인
    type2_100 = df[
        (df['ROLE TYPE STD'] == 'TYPE-2') &
        (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') &
        (df['conditions_pass_rate'] == 100)
    ]

    if len(type2_100) > 0:
        incentives = type2_100['September_Incentive'].unique()

        if len(incentives) > 1:
            print("❌ 공정성 문제 발견!")
            print(f"동일 조건 충족자들이 다른 금액을 받음: {incentives}")

            for idx, row in type2_100.iterrows():
                print(f"  {row['Employee No']} {row['Full Name']}: {row['September_Incentive']:,.0f} VND")
        else:
            print("✅ 공정성 검증 통과")
            print(f"모든 100% 충족자가 동일 금액 수령: {incentives[0]:,.0f} VND")
```

## 3. 실행 계획

### 즉시 실행 (Day 1)
1. [ ] Python 스크립트 2단계 계산 방식 구현
2. [ ] ĐINH KIM NGOAN 특별 케이스 테스트
3. [ ] 공정성 검증 스크립트 실행

### 단기 개선 (Week 1)
1. [ ] 대시보드에 계산 투명성 UI 추가
2. [ ] 공정성 경고 시스템 구현
3. [ ] 전체 시스템 테스트

### 중기 개선 (Week 2)
1. [ ] 계산 로그 시스템 구축
2. [ ] 관리자 대시보드에 공정성 모니터링 추가
3. [ ] 문서화 및 교육

## 4. 기대 효과

1. **즉각적 해결**: ĐINH KIM NGOAN이 정당한 214,720 VND 수령
2. **공정성 확보**: 모든 TYPE-2 GROUP LEADER 동일 조건 → 동일 금액
3. **투명성 향상**: 계산 근거 명확히 표시
4. **신뢰도 제고**: 시스템 기반 공정한 계산

## 5. 핵심 수정 사항

### src/step1_인센티브_계산_개선버전.py
- Line 2615-2617: 조건부 스킵 로직 제거 또는 수정
- Line 3233-3244: GROUP LEADER 계산을 별도 단계로 분리
- Line 3276-3322: calculate_type2_group_leader_independent 함수 개선
- Line 4032: Final Incentive amount 복사 로직 검증

### dashboard_v2/static/js/dashboard_complete.js
- Line 8818: TYPE-2 조건 매핑 확인
- Line 8978: 공정성 검증 로직 추가
- Individual Details 모달에 계산 근거 표시

## 6. 검증 방법

```bash
# 1. Python 계산 테스트
python src/step1_인센티브_계산_개선버전.py

# 2. 공정성 검증
python verify_calculation_fairness.py

# 3. 대시보드 생성
python dashboard_v2/generate_dashboard.py --month september --year 2025

# 4. 결과 확인
grep "617100049" output_files/*.csv | grep September_Incentive
```

---

*이 계획은 원본 대시보드와 동일한 Python 자체 계산을 구현하면서 공정성을 확보합니다.*