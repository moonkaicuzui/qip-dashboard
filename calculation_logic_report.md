# 인센티브 계산 로직 검증 보고서

## 요약
TYPE-1 (V) SUPERVISOR 직급의 인센티브 계산 로직에서 심각한 불일치가 발견되었습니다.

## 발견된 문제점

### 1. 최소 근무일 조건 표시 오류
- **증상**: "최소 근무일 ≥12일" 조건이 0% 충족률로 표시됨
- **실제 데이터**: 
  - 618040412 (CAO THỊ MIỀN): 23일 근무 ✅
  - 619070072 (THÁI UYỂN NHI): 23일 근무 ✅
  - 620020691 (VÕ VĂN KIỆT): 20일 근무 ✅
- **예상 충족률**: 100% (3명 모두 12일 이상 근무)
- **실제 표시**: 0% (0명 충족, 3명 미충족)

### 2. AND 로직 위반
- **원칙**: 10개 조건 중 하나라도 실패하면 인센티브 미지급
- **실제 동작**: 
  - 조건 표시상 1개 조건 실패 (최소 근무일)
  - 그럼에도 2명이 인센티브 수령
  - AND 로직이 제대로 작동하지 않음

### 3. 평균 충족률 계산 오류
- **표시된 평균 충족률**: 77.8%
- **개별 조건 충족률**: 
  - 출근율 ≥88%: 100%
  - 무단결근 ≤2일: 100%
  - 실제 근무일 >0일: 100%
  - 최소 근무일 ≥12일: 0% (오류)
- **예상 평균**: 75% (3/4)
- **실제 평균**: 77.8% (계산 불일치)

### 4. 직원별 상세 조건 정보 누락
- **증상**: 개별 직원 클릭시 "조건 정보 없음" 표시
- **원인**: JavaScript에 조건 데이터가 제대로 전달되지 않음

## 근본 원인

### Python 코드 (정상 작동)
```python
# step2_dashboard_version4.py:720-728
if actual_data.get('actual_working_days') is not None:
    actual_days = int(actual_data['actual_working_days'])
    conditions['minimum_working_days']['actual'] = f"{actual_days}일"
    if actual_days < 12:
        conditions['minimum_working_days']['passed'] = False
        conditions['minimum_working_days']['value'] = '기준 미달'
    else:
        conditions['minimum_working_days']['passed'] = True
        conditions['minimum_working_days']['value'] = '정상'
```
✅ Python 코드는 올바르게 actual_working_days ≥ 12를 평가

### JavaScript 코드 (문제 발생)
```javascript
// analyzeConditions 함수에서
if (emp.conditions.minimum_working_days) {
    if (emp.conditions.minimum_working_days.passed) {
        conditions[labels.minimumDays].passed++;
    } else {
        conditions[labels.minimumDays].failed++;
    }
}
```
❌ JavaScript가 조건 데이터를 제대로 받지 못해 모두 failed로 처리

## CSV 데이터 분석

### 조건 컬럼의 역논리
- `attendancy condition 4 - minimum working days` 컬럼:
  - `yes` = 조건 실패 (근무일 < 12)
  - `no` = 조건 통과 (근무일 ≥ 12)

### TYPE-1 (V) SUPERVISOR 실제 데이터
| 직원번호 | 이름 | 실제 근무일 | 조건4 CSV값 | 인센티브 |
|---------|------|------------|------------|----------|
| 618040412 | CAO THỊ MIỀN | 23일 | no (통과) | 80,390 VND |
| 619070072 | THÁI UYỂN NHI | 23일 | no (통과) | 98,822 VND |
| 620020691 | VÕ VĂN KIỆT | 20일 | no (통과) | 0 VND |

참고: VÕ VĂN KIỆT는 결근율 12% 초과로 인센티브 미지급 (조건3 실패)

## 영향 범위

### 직접 영향
- TYPE-1 (V) SUPERVISOR: 3명
- TYPE-2 (V) SUPERVISOR: 8명
- 총 11명의 (V) SUPERVISOR 직급

### 잠재적 영향
- 모든 TYPE의 모든 직급에서 최소 근무일 조건이 잘못 표시될 가능성
- AND 로직이 제대로 작동하지 않아 잘못된 인센티브 지급 가능성

## 권장 수정 사항

### 1. 즉시 수정 필요
- JavaScript에서 minimum_working_days 조건 데이터 전달 확인
- analyzeConditions 함수의 조건 집계 로직 수정
- 평균 충족률 계산 로직 검증

### 2. 추가 검증 필요
- 모든 TYPE과 직급에 대한 조건 평가 로직 검증
- AND 로직 구현 확인
- 개별 직원 상세 정보 전달 체계 점검

## 결론

현재 대시보드는 실제 데이터와 다르게 조건 충족 현황을 표시하고 있으며, 이는 사용자에게 잘못된 정보를 제공하고 있습니다. Python 백엔드는 올바르게 작동하지만, JavaScript 프론트엔드에서 데이터를 제대로 처리하지 못하고 있습니다.

**긴급도: 높음** - 인센티브 지급 의사결정에 영향을 미칠 수 있음