# 데이터 흐름 분석 및 문제 해결 방안

작성일: 2025-09-28

## 질문에 대한 답변

### Q: "원본 대시보드에는 이런 경우 어떻게 금액을 계산해서 반영해?"

**답: 원본 대시보드는 계산을 하지 않습니다.**

구글 드라이브에서 가져온 CSV 파일에 이미 계산된 값이 들어있고, Python 스크립트는 이 값을 그대로 사용합니다.

### Q: "값이 덮어쓰기 업데이트가 안된다는 말이야?"

**답: 맞습니다. Python이 계산한 값으로 덮어쓰지 않고, 소스 CSV의 값을 그대로 유지합니다.**

## 실제 데이터 흐름

```
구글 드라이브
    ↓
input_files/2025년 9월 인센티브 지급 세부 정보.csv
(이미 September_Incentive, Final Incentive amount 포함)
    ↓
Python step1_인센티브_계산_개선버전.py
(소스 값 그대로 사용, 계산하지 않음)
    ↓
output_files/최종완성버전_v6.0_Complete.csv
(소스 값 그대로 복사)
    ↓
대시보드 HTML
(그대로 표시)
```

## 핵심 문제

### 1. 소스 CSV에 이미 계산된 값이 있음

```python
# input_files/2025년 9월 인센티브 지급 세부 정보.csv
September_Incentive: 286명 값 있음, 212명은 0
Final Incentive amount: September_Incentive와 동일

# ĐINH KIM NGOAN (617100049)
September_Incentive: 0
Final Incentive amount: 0
RE MARK: Returningemployee(maternity leave)
```

### 2. Python 스크립트의 동작

```python
# step1_인센티브_계산_개선버전.py

# Line 1520-1521: 초기화
incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
self.month_data[incentive_col] = 0  # September_Incentive = 0

# 하지만...
# 소스 CSV를 로드할 때 이미 있는 September_Incentive 값이 덮어씀
# 결과적으로 소스 값을 그대로 사용
```

### 3. 불공정한 처리의 원인

**소스 CSV 생성 단계에서 이미 차별이 발생:**
- 같은 TYPE-2 GROUP LEADER, 같은 조건 100% 충족
- ĐINH KIM NGOAN: 0 VND (출산휴가 복귀자)
- 다른 5명: 214,720 VND

**Python은 이를 수정하지 않고 그대로 사용**

## 해결 방안

### 방안 1: Python이 실제로 계산하도록 수정

```python
def prepare_integrated_data(self):
    """통합 데이터 준비"""
    # 기존 코드...

    # 소스 CSV의 계산값 무시하고 자체 계산 사용
    if 'September_Incentive' in self.month_data.columns:
        print("⚠️ 소스 CSV의 September_Incentive 무시")
        self.month_data['Source_September_Incentive'] = self.month_data['September_Incentive']
        del self.month_data['September_Incentive']

    if 'Final Incentive amount' in self.month_data.columns:
        print("⚠️ 소스 CSV의 Final Incentive amount 무시")
        self.month_data['Source_Final_Amount'] = self.month_data['Final Incentive amount']
        del self.month_data['Final Incentive amount']

    # 인센티브 칼럼 초기화 (자체 계산)
    incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
    self.month_data[incentive_col] = 0
```

### 방안 2: 계산 로직 실제 구현 확인

현재 `calculate_all_incentives()` 함수가 실제로 호출되고 계산이 이루어지는지 확인 필요:

```python
def calculate_all_incentives(self):
    """모든 타입별 인센티브 계산"""
    print("\n🎯 인센티브 계산 시작...")

    # TYPE-1 계산
    self.calculate_type1_incentives()

    # TYPE-2 계산 (TYPE-1 평균 기반)
    self.calculate_type2_incentives()

    # TYPE-3 계산 (0원)
    self.calculate_type3_incentives()
```

### 방안 3: 소스 데이터 생성 프로세스 개선

**근본적 해결책: 구글 드라이브 CSV 생성 시점에서 개선**

1. CSV에서 September_Incentive, Final Incentive amount 제거
2. Python이 모든 계산 담당
3. 공정한 규칙 기반 계산

## 테스트 방법

```bash
# 1. 백업
cp "input_files/2025년 9월 인센티브 지급 세부 정보.csv" backup.csv

# 2. September_Incentive 칼럼 제거한 테스트
python -c "
import pandas as pd
df = pd.read_csv('backup.csv', encoding='utf-8-sig')
df = df.drop(columns=['September_Incentive'])
df.to_csv('test_input.csv', index=False, encoding='utf-8-sig')
"

# 3. 테스트 실행
mv "input_files/2025년 9월 인센티브 지급 세부 정보.csv" original.csv
mv test_input.csv "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
python src/step1_인센티브_계산_개선버전.py

# 4. 결과 확인
grep "617100049" output_files/*Complete.csv

# 5. 원복
mv original.csv "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
```

## 결론

1. **현재 시스템은 계산하지 않고 소스 값을 그대로 사용**
2. **불공정은 소스 CSV 생성 시점에서 발생**
3. **Python 스크립트 수정으로 해결 가능**
4. **근본적으로는 데이터 입력 프로세스 개선 필요**

---

*이 문서는 실제 데이터 흐름을 분석한 결과입니다.*