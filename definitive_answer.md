# 결정적 답변: 원본 대시보드의 Python 계산 동작

## 질문: "원본 대시보드에서는 Python 자체 계산을 했다는 거지?"

## 답변: 네, 맞습니다만 복잡합니다.

### 1. Python은 실제로 계산 로직을 가지고 있습니다

**계산 로직 존재 (step1_인센티브_계산_개선버전.py)**:
- TYPE-1: 조건 충족 시 직접 금액 계산
- TYPE-2: TYPE-1 평균 기반 계산
- TYPE-3: 항상 0원 (정책 제외)

### 2. 하지만 소스 CSV에 이미 값이 있으면 건너뜁니다

**Line 3192 코드**:
```python
# 이미 계산된 경우 스킵
if row[incentive_col] > 0:
    continue
```

### 3. 실제 데이터 흐름

```
구글 드라이브 CSV (September_Incentive 칼럼 포함)
        ↓
Python Script 실행
        ↓
값이 이미 있으면? → 그대로 사용 (계산 스킵)
값이 0이거나 없으면? → 계산 시도
        ↓
출력 파일 생성
```

### 4. ĐINH KIM NGOAN의 케이스

#### 테스트 1: 소스 CSV에 값이 있을 때
- 소스 CSV: September_Incentive = 0 (이미 설정됨)
- Python: 0이므로 계산 시도
- 하지만: TYPE-2 GROUP LEADER 계산이 TYPE-2 LINE LEADER 평균에 의존
- 결과: LINE LEADER도 0이면 GROUP LEADER도 0

#### 테스트 2: 소스 CSV에서 칼럼 제거 후
- 소스 CSV: September_Incentive 칼럼 없음
- Python: 전체 계산 실행
- 결과:
  - ĐINH KIM NGOAN: 100% 충족, 0 VND
  - 다른 5명: 100% 충족, 214,720 VND

### 5. 왜 ĐINH KIM NGOAN만 0인가?

**계산 순서 문제**:
1. TYPE-2 계산 시 LINE LEADER부터 계산
2. GROUP LEADER는 LINE LEADER 평균의 2배로 계산
3. ĐINH KIM NGOAN의 LINE LEADER들이 0을 받으면
4. 평균도 0이 되어 GROUP LEADER도 0

**calculate_type2_group_leader_independent() 함수**:
```python
# Line 3308-3322
receiving_line_leaders = type2_line_leaders[type2_line_leaders[incentive_col] > 0]
if len(receiving_line_leaders) > 0:
    avg_incentive = receiving_line_leaders[incentive_col].mean()
    result = int(avg_incentive * 2)  # GROUP LEADER는 평균의 2배
    return result
return 0  # LINE LEADER가 없거나 모두 0이면 0 반환
```

### 6. 결론

**원본 대시보드의 Python 동작**:
1. ✅ **계산 로직은 있습니다**
2. ✅ **실제로 계산도 합니다**
3. ❌ **하지만 소스 CSV 값을 우선시합니다**
4. ❌ **계산 순서 의존성으로 일부는 0이 됩니다**

**불공정의 원인**:
- 주 원인: 계산 순서와 의존성 문제
- 부 원인: 소스 CSV의 기존 값 영향

### 7. 해결 방안

1. **즉시 해결**: TYPE-2 GROUP LEADER 계산을 독립적으로 변경
2. **근본 해결**: 계산 순서를 2단계로 분리
   - 1단계: 모든 LINE LEADER 계산
   - 2단계: GROUP LEADER 계산 (LINE LEADER 평균 사용)
3. **완전 해결**: 소스 CSV 값 무시하고 항상 재계산