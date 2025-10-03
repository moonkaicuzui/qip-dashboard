# 정책 제외 인원 처리 개선 계획
## Policy Exclusion Handling Improvement Plan

작성일: 2025-09-28
버전: 1.0

## 1. 현재 상황 분석

### 1.1 문제점 확인
- **ĐINH KIM NGOAN (617100049)**: 출산휴가 복귀자로 0 VND 인센티브
- **원인**: 소스 CSV에 이미 "Final Incentive amount" = 0으로 설정됨
- **RE MARK 필드**: "Returningemployee(maternity leave)" 표시
- **대시보드 표시**: TYPE-3와 구분 없이 단순 조건 미충족으로 표시

### 1.2 데이터 흐름 검증 결과
```
Source CSV → Python Script → Output Excel/CSV → Dashboard HTML
    ↓              ↓                ↓                  ↓
Already 0     Preserves 0      Shows 0         Display 0
```

#### 칼럼 매칭 검증:
- **소스 CSV**: "Final Incentive amount" (column 12) = 0
- **Python 계산**: "{Month}_Incentive" 칼럼에서 계산
- **최종 출력**: line 4032에서 "Final Incentive amount"로 복사
- **결론**: 칼럼 매칭은 정확하나, 소스 데이터의 0값이 유지됨

### 1.3 현재 정책 제외 처리 방식
```python
# TYPE-3만 명시적으로 정책 제외
if emp.type === 'TYPE-3':
    passRate = 'N/A'  # 정책 제외
else if (incentive === 0):
    passRate = 0      # 일반 미충족
```

## 2. 개선 방안

### 2.1 RE MARK 필드 활용 강화

#### A. Python 스크립트 개선
```python
def identify_policy_exclusion(row):
    """정책 제외 사유 식별"""
    re_mark = str(row.get('RE MARK', '')).lower()

    # TYPE-3는 항상 정책 제외
    if row.get('TYPE') == 'TYPE-3':
        return 'NEW_EMPLOYEE'

    # RE MARK 기반 특수 상태
    if 'maternity' in re_mark:
        return 'MATERNITY_RETURN'
    if 'military' in re_mark:
        return 'MILITARY_RETURN'
    if 'longterm' in re_mark or 'long term' in re_mark:
        return 'LONGTERM_LEAVE_RETURN'

    return None

def add_policy_exclusion_flag(self):
    """정책 제외 플래그 추가"""
    self.month_data['Policy_Exclusion'] = self.month_data.apply(
        identify_policy_exclusion, axis=1
    )
    self.month_data['Is_Policy_Excluded'] = self.month_data['Policy_Exclusion'].notna()
```

### 2.2 대시보드 UI/UX 개선

#### A. Individual Details 모달 수정
```javascript
// 정책 제외 사유별 메시지
const policyMessages = {
    'NEW_EMPLOYEE': {
        ko: '신입직원 (3개월 정책 제외)',
        en: 'New Employee (3-month policy exclusion)',
        vi: 'Nhân viên mới (Loại trừ chính sách 3 tháng)'
    },
    'MATERNITY_RETURN': {
        ko: '출산휴가 복귀 (정책 제외)',
        en: 'Maternity Leave Return (Policy Exclusion)',
        vi: 'Trở lại sau nghỉ thai sản (Loại trừ chính sách)'
    },
    'MILITARY_RETURN': {
        ko: '군복무 복귀 (정책 제외)',
        en: 'Military Service Return (Policy Exclusion)',
        vi: 'Trở lại sau nghĩa vụ quân sự (Loại trừ chính sách)'
    }
};

// 조건 충족률 표시 개선
if (emp.is_policy_excluded) {
    fulfillmentHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            <strong>${translations[currentLang].policyExcluded}:</strong>
            ${policyMessages[emp.policy_exclusion][currentLang]}
        </div>
        <div class="text-muted mt-2">
            ${translations[currentLang].conditionFulfillment}: N/A
        </div>
    `;
} else if (incentive === 0) {
    fulfillmentHTML = `
        <div class="text-danger">
            ${translations[currentLang].conditionFulfillment}: 0%
        </div>
    `;
}
```

#### B. Summary Table 개선
```javascript
// Summary table에 정책 제외 표시
function renderSummaryTable(data) {
    data.forEach(emp => {
        let statusBadge = '';

        if (emp.is_policy_excluded) {
            // 정책 제외자는 특별 배지
            statusBadge = `<span class="badge bg-info">
                <i class="fas fa-ban"></i> ${getPolicyBadgeText(emp.policy_exclusion)}
            </span>`;
        } else if (emp.september_incentive > 0) {
            statusBadge = '<span class="badge bg-success">Eligible</span>';
        } else {
            statusBadge = '<span class="badge bg-danger">Not Met</span>';
        }

        // 테이블 행 렌더링...
    });
}
```

### 2.3 번역 파일 업데이트

#### dashboard_translations.json 추가
```json
{
    "policyExclusion": {
        "ko": "정책 제외",
        "en": "Policy Exclusion",
        "vi": "Loại trừ chính sách"
    },
    "maternityReturn": {
        "ko": "출산휴가 복귀",
        "en": "Maternity Leave Return",
        "vi": "Trở lại sau nghỉ thai sản"
    },
    "militaryReturn": {
        "ko": "군복무 복귀",
        "en": "Military Service Return",
        "vi": "Trở lại sau nghĩa vụ quân sự"
    },
    "longtermReturn": {
        "ko": "장기휴가 복귀",
        "en": "Long-term Leave Return",
        "vi": "Trở lại sau nghỉ dài hạn"
    },
    "policyExcludedNote": {
        "ko": "이 직원은 회사 정책에 따라 인센티브 대상에서 제외되었습니다",
        "en": "This employee is excluded from incentives per company policy",
        "vi": "Nhân viên này bị loại trừ khỏi ưu đãi theo chính sách công ty"
    }
}
```

### 2.4 Position Details 탭 개선

```javascript
// Position Details에 정책 제외 통계 추가
function calculatePositionStats(data) {
    const stats = {
        total: 0,
        eligible: 0,
        notMet: 0,
        policyExcluded: {
            total: 0,
            byReason: {}
        }
    };

    data.forEach(emp => {
        stats.total++;

        if (emp.is_policy_excluded) {
            stats.policyExcluded.total++;
            const reason = emp.policy_exclusion;
            stats.policyExcluded.byReason[reason] =
                (stats.policyExcluded.byReason[reason] || 0) + 1;
        } else if (emp.september_incentive > 0) {
            stats.eligible++;
        } else {
            stats.notMet++;
        }
    });

    return stats;
}
```

## 3. 구현 계획

### Phase 1: 데이터 처리 개선 (Week 1)
1. **Python 스크립트 수정**
   - [ ] RE MARK 필드 파싱 로직 추가
   - [ ] Policy_Exclusion 칼럼 생성
   - [ ] Excel/CSV 출력에 정책 제외 정보 포함

2. **데이터 검증**
   - [ ] 출산휴가 복귀자 정확히 식별되는지 확인
   - [ ] TYPE-3와 구분되어 처리되는지 검증

### Phase 2: 대시보드 UI 개선 (Week 2)
1. **JavaScript 수정**
   - [ ] employeeData에 policy_exclusion 필드 추가
   - [ ] Individual Details 모달 조건부 렌더링
   - [ ] Summary Table 배지 시스템 구현

2. **CSS 스타일링**
   - [ ] 정책 제외 배지 스타일 추가
   - [ ] Alert 박스 스타일 정의

### Phase 3: 번역 및 문서화 (Week 3)
1. **다국어 지원**
   - [ ] dashboard_translations.json 업데이트
   - [ ] 모든 정책 제외 메시지 번역

2. **문서화**
   - [ ] 정책 제외 사유 목록 문서화
   - [ ] 관리자 가이드 작성

### Phase 4: 테스트 및 검증 (Week 4)
1. **단위 테스트**
   - [ ] RE MARK 파싱 테스트
   - [ ] 정책 제외 플래그 테스트

2. **통합 테스트**
   - [ ] 엔드투엔드 플로우 테스트
   - [ ] 다국어 전환 테스트

## 4. 기대 효과

1. **명확한 구분**: 정책 제외자와 조건 미충족자 명확히 구분
2. **투명성 향상**: 인센티브 0원 사유 명확히 표시
3. **관리 효율성**: 정책 제외 사유별 통계 및 관리
4. **사용자 경험**: 직관적인 UI로 혼란 방지

## 5. 주의사항

1. **Single Source of Truth 원칙 유지**
   - CSV의 Final Incentive amount 값은 변경하지 않음
   - 추가 메타데이터만 생성

2. **하위 호환성**
   - 기존 대시보드와 호환 유지
   - 점진적 마이그레이션 지원

3. **성능 고려**
   - RE MARK 파싱 최적화
   - 대용량 데이터 처리 시 성능 테스트

## 6. 추가 고려사항

### 6.1 장기적 개선
- HR 시스템과 연동하여 정책 제외 사유 자동화
- 정책 제외 기간 추적 및 자동 해제
- 관리자 대시보드에 정책 제외 관리 기능 추가

### 6.2 데이터 품질
- RE MARK 필드 표준화 (오타, 대소문자 등)
- 정기적인 데이터 품질 검증 프로세스 구축

---

*이 문서는 지속적으로 업데이트됩니다.*