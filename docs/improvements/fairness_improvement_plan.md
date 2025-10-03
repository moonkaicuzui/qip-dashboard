# 인센티브 공정성 개선 계획
## Incentive Fairness Improvement Plan

작성일: 2025-09-28
버전: 2.0

## 1. 문제 상황

### 1.1 핵심 발견
- **ĐINH KIM NGOAN (617100049)**: TYPE-2 GROUP LEADER, 조건 100% 충족, 0 VND
- **다른 5명 GROUP LEADER**: 같은 조건 100% 충족, 214,720 VND
- **원인**: 소스 CSV에서 출산휴가 복귀자에게 임의로 0 입력

### 1.2 현재 처리 방식
```python
# Line 4032 in step1_인센티브_계산_개선버전.py
# Python이 계산한 September_Incentive를 Final로 복사
self.month_data['Final Incentive amount'] = self.month_data[incentive_col].copy()
```

**문제점**:
- 소스 CSV에 이미 "Final Incentive amount"가 있으면?
- Python은 소스 값을 먼저 로드하고, 나중에 덮어씀
- 하지만 일부 로직에서 소스 값을 유지할 가능성

## 2. 개선 방안

### 2.1 즉시 적용 가능한 수정

#### A. Python 스크립트 수정 - 자체 계산 우선
```python
def prepare_integrated_data(self):
    """통합 데이터 준비"""
    # 기존 코드...

    # 소스 CSV의 Final Incentive amount 백업 (검증용)
    if 'Final Incentive amount' in self.month_data.columns:
        self.month_data['Source_Final_Amount'] = self.month_data['Final Incentive amount']
        # 소스 값 제거 - 자체 계산만 사용
        del self.month_data['Final Incentive amount']

    # 인센티브 칼럼 초기화
    incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
    self.month_data[incentive_col] = 0

def save_final_data(self):
    """최종 데이터 저장"""
    # 계산 완료 후

    # 불일치 검증 및 경고
    if 'Source_Final_Amount' in self.month_data.columns:
        discrepancy = self.month_data[
            (self.month_data['Source_Final_Amount'] != self.month_data['Final Incentive amount']) &
            (self.month_data['conditions_pass_rate'] == 100)  # 조건 100% 충족
        ]

        if len(discrepancy) > 0:
            print("\n⚠️ 경고: 조건 100% 충족했지만 소스와 계산값 불일치")
            for idx, row in discrepancy.iterrows():
                print(f"  {row['Employee No']} {row['Full Name']}: "
                      f"소스={row['Source_Final_Amount']:,.0f}, "
                      f"계산={row['Final Incentive amount']:,.0f}")
```

#### B. 검증 스크립트 생성
```python
# verify_fairness.py
def verify_incentive_fairness():
    """동일 조건 동일 금액 검증"""

    # TYPE별 포지션별 그룹화
    groups = df.groupby(['ROLE TYPE STD', 'QIP POSITION 1ST  NAME', 'conditions_pass_rate'])

    for (role_type, position, pass_rate), group in groups:
        if pass_rate == 100 and len(group) > 1:
            incentives = group['September_Incentive'].unique()

            if len(incentives) > 1:
                print(f"\n⚠️ 불공정 발견: {role_type} {position}")
                print(f"  조건 충족률: {pass_rate}%")
                print(f"  다른 인센티브 금액: {incentives}")

                for idx, row in group.iterrows():
                    re_mark = row.get('RE MARK', '')
                    print(f"    {row['Employee No']} {row['Full Name']}: "
                          f"{row['September_Incentive']:,.0f} VND "
                          f"({'RE MARK: ' + re_mark if re_mark else ''})")
```

### 2.2 중장기 개선 방안

#### A. 데이터 파이프라인 개선
1. **소스 CSV 생성 단계**
   - "Final Incentive amount" 칼럼 제거
   - Python에서만 계산하도록 변경
   - RE MARK는 정보용으로만 사용

2. **계산 투명성 강화**
   ```python
   # 계산 근거 추가
   self.month_data['Calculation_Method'] = ''
   self.month_data['Calculation_Detail'] = ''

   # TYPE-2 GROUP LEADER 계산 시
   self.month_data.loc[idx, 'Calculation_Method'] = 'TYPE-2_LINE_LEADER_AVG_x2'
   self.month_data.loc[idx, 'Calculation_Detail'] = f'Base_Avg={base_avg}, Multiplier=2'
   ```

3. **감사 로그 생성**
   ```python
   # audit_log.csv 생성
   audit_log = []

   if source_amount != calculated_amount:
       audit_log.append({
           'Employee_No': emp_id,
           'Name': name,
           'Source_Amount': source_amount,
           'Calculated_Amount': calculated_amount,
           'Difference': calculated_amount - source_amount,
           'Reason': 'Source override detected',
           'Action': 'Using calculated value'
       })
   ```

### 2.3 대시보드 개선

#### A. 공정성 지표 추가
```javascript
// 대시보드에 공정성 체크 섹션 추가
function checkFairness(data) {
    const fairnessIssues = [];

    // 같은 TYPE, 포지션, 조건 충족률 그룹화
    const groups = _.groupBy(data, d =>
        `${d.role_type}_${d.position}_${d.pass_rate}`
    );

    Object.entries(groups).forEach(([key, group]) => {
        const uniqueAmounts = [...new Set(group.map(d => d.incentive))];

        if (uniqueAmounts.length > 1 && group[0].pass_rate === 100) {
            fairnessIssues.push({
                group: key,
                employees: group,
                amounts: uniqueAmounts
            });
        }
    });

    return fairnessIssues;
}

// 공정성 경고 표시
if (fairnessIssues.length > 0) {
    showFairnessWarning(fairnessIssues);
}
```

#### B. RE MARK 정보 표시 개선
```javascript
// Individual Details 모달에 추가 정보
if (employee.re_mark) {
    modalContent += `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            <strong>특이사항:</strong> ${employee.re_mark}
        </div>
    `;

    // 하지만 금액은 계산값 사용
    if (employee.calculated_amount !== employee.source_amount) {
        modalContent += `
            <div class="text-muted">
                <small>참고: 소스 데이터(${employee.source_amount})와 다르게
                공정한 계산값(${employee.calculated_amount})을 사용합니다.</small>
            </div>
        `;
    }
}
```

## 3. 실행 계획

### Phase 1: 긴급 수정 (1일)
- [ ] Python 스크립트에서 소스 Final Amount 무시하도록 수정
- [ ] 검증 스크립트 작성 및 실행
- [ ] 불공정 사례 문서화

### Phase 2: 시스템 개선 (1주)
- [ ] 계산 투명성 강화 (계산 근거 칼럼 추가)
- [ ] 감사 로그 시스템 구축
- [ ] 대시보드에 공정성 지표 추가

### Phase 3: 프로세스 개선 (2주)
- [ ] 소스 CSV 생성 프로세스 검토
- [ ] 데이터 입력 가이드라인 작성
- [ ] 교육 및 공지

## 4. 기대 효과

1. **공정성 확보**: 동일 조건 → 동일 금액
2. **투명성 향상**: 계산 근거 명확화
3. **신뢰도 제고**: 객관적 시스템 기반 계산
4. **분쟁 방지**: 명확한 규칙과 투명한 처리

## 5. 주의사항

### 5.1 호환성 유지
- 기존 Excel 보고서 형식 유지
- 대시보드 기능 정상 작동 확인

### 5.2 데이터 검증
- 변경 전후 전체 인원 비교
- 특히 출산휴가 복귀자 확인
- 군복무 복귀자 등 다른 특수 케이스도 확인

### 5.3 커뮤니케이션
- 변경 사항 사전 공지
- 영향받는 직원들에게 설명
- HR 부서와 협의

---

*이 문서는 공정한 인센티브 시스템 구축을 위한 개선 계획입니다.*