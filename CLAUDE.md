# QIP 인센티브 대시보드 프로젝트 지침

## 🚨 필수 준수 원칙

### 데이터 처리 원칙
1. **가짜 데이터 사용 금지**
   - 테스트용 가짜 데이터 생성 금지
   - 실제 데이터만 사용
   - 데이터가 없으면 가짜로 채우지 말고 오류 표시

2. **명확한 오류 메시지**
   - 데이터가 없을 때 "데이터 오류" 메시지 표시
   - 누락된 파일명을 구체적으로 표시
   - 해결 방법 안내 포함

3. **실제 데이터 우선**
   - Google Drive 또는 실제 소스에서 데이터 가져오기
   - 임의로 데이터를 생성하지 않기
   - 시스템은 실제 운영 데이터만 처리

### UI 개선 검증 원칙
1. **Playwright 자동 검증**
   - UI 개선 작업 후 반드시 Playwright로 자동 검증 수행
   - 모든 언어(한국어, 영어, 베트남어)에서 번역 확인
   - 개선되지 않은 부분을 구체적으로 파악하여 보고

2. **검증 항목**
   - 언어 전환 시 모든 UI 요소 번역 확인
   - 팝업 창의 제목, 차트 레이블, 테이블 헤더 검증
   - 동적으로 생성되는 콘텐츠의 번역 상태 확인
   - JavaScript 콘솔 오류 체크

3. **최종 보고**
   - 개선 완료된 항목 명시
   - 아직 개선되지 않은 항목 구체적 보고
   - 스크린샷 캡처를 통한 시각적 검증 포함

## 📁 프로젝트 구조

```
/
├── action.sh                    # 메인 실행 스크립트
├── src/
│   ├── step0_create_monthly_config.py
│   ├── step1_인센티브_계산_개선버전.py
│   └── step2_dashboard_version4.py
├── config_files/               # 월별 설정 파일
├── input_files/                # 입력 데이터 (실제 데이터만)
└── output_files/               # 출력 결과
```

## ⚠️ 주의사항

### 하지 말아야 할 것:
- ❌ 테스트 데이터 생성 (`test_*.py` 파일 생성 금지)
- ❌ 가짜 출근 데이터 생성
- ❌ 임의의 인센티브 금액 설정
- ❌ 데이터 없을 때 0이 아닌 값으로 채우기

### 해야 할 것:
- ✅ 실제 데이터 파일 확인
- ✅ 누락된 데이터 명확히 표시
- ✅ 데이터 오류 시 사용자에게 알림
- ✅ Google Drive 동기화 안내

## 🔍 데이터 검증

필수 데이터 파일:
1. `attendance/converted/attendance data {month}_converted.csv`
2. `{year}년 {month-1}월 인센티브 지급 세부 정보.csv`
3. `config_files/type2_position_mapping.json`
4. `config_files/auditor_trainer_area_mapping.json`

이 파일들이 없으면:
- 인센티브 계산 진행하지 않음
- 대시보드에 오류 메시지 표시
- 0 VND로 표시 (정상 동작)

## 💡 개발 가이드라인

1. **UI/UX 원칙**
   - 데이터 문제를 숨기지 말고 명확히 표시
   - 사용자가 문제를 이해하고 해결할 수 있도록 안내

2. **코드 수정 시**
   - 실제 데이터 경로만 사용
   - 하드코딩된 테스트 값 사용 금지
   - 오류 처리 강화

3. **Git 커밋 시**
   - 테스트 파일은 커밋하지 않음
   - 실제 운영 코드만 커밋

## 🏆 극복한 주요 문제들 (2025년 1월)

### 1. **0 VND 인센티브 문제** ✅ 해결
- **증상**: 대시보드에서 모든 직원 인센티브가 0 VND로 표시
- **원인**: 출석 데이터 컬럼 매칭 오류 ("No." vs "ID No")
- **해결**: 올바른 컬럼명 탐지 알고리즘 개선
- **결과**: 121,996,842 VND 정확히 계산됨

### 2. **IndexError: Out of Bounds** ✅ 해결
- **증상**: `single positional indexer is out-of-bounds` 오류
- **원인**: 빈 DataFrame에 .iloc[0] 접근
- **해결**: 방어적 코딩 - empty DataFrame 체크 추가
- **교훈**: 데이터가 없을 수 있는 모든 경우 고려

### 3. **데이터 타입 불일치** ✅ 해결
- **증상**: int64 ID가 string ID와 매칭 안됨
- **원인**: 표준화된 ID (문자열)와 원본 ID (정수) 타입 차이
- **해결**: `.astype(str).str.zfill(9)` 일관된 비교
- **영향**: 392/464명 매칭 성공

### 4. **하드코딩된 월 처리** ✅ 해결
- **증상**: JavaScript가 항상 `july_incentive`만 참조
- **원인**: 템플릿에 하드코딩된 변수명
- **해결**: 동적 템플릿 `emp.{month}_incentive` 구현
- **결과**: 모든 월에 대해 자동화 달성

### 5. **Google Drive 동기화** ✅ 해결
- **증상**: 이전 월 인센티브 파일 수동 다운로드 필요
- **원인**: 자동화 스크립트 부재
- **해결**: `sync_previous_incentive.py` 생성
- **효과**: 완전 자동화된 워크플로우

### 6. **출석 상태 잘못된 컬럼 참조** ✅ 해결
- **증상**: 근무일수 항상 0으로 계산
- **원인**: 'Work Date' 값 체크 대신 'compAdd' 상태 필요
- **해결**: 'compAdd' == 'Đi làm' 체크로 변경
- **결과**: 실제 근무일수 정확히 계산 (예: 13일)

## 🏆 극복한 주요 문제들 (2025년 8월)

### 7. **Type별 데이터 구분 문제** ✅ 해결
- **증상**: Type별 현황 테이블에서 모든 Type이 동일한 값 (464명)으로 표시
- **원인**: CSV 컬럼명 불일치 ('TYPE' vs 실제 'ROLE TYPE STD')
- **해결**: `row.get('ROLE TYPE STD', '')` 올바른 컬럼명으로 수정
- **결과**: TYPE-1 (150명), TYPE-2 (276명), TYPE-3 (38명) 정확히 구분

### 8. **언어 변경 시 단위 표시 문제** ✅ 해결
- **증상**: 베트남어로 변경해도 "명"이 계속 표시됨
- **원인**: `changeLanguage()` 함수가 UI 텍스트만 변경하고 테이블 데이터는 재생성하지 않음
- **해결**: 
  ```javascript
  // changeLanguage() 함수에 추가
  generateSummaryData();  // Type별 요약 데이터 재생성
  generatePositionData(); // 직급별 상세 데이터 재생성
  ```
- **결과**: 
  - 한국어: "150명", "276명", "38명"
  - 영어: "150 people", "276 people", "38 people"
  - 베트남어: "150 người", "276 người", "38 người"

### 9. **베트남어 번역 누락** ✅ 해결
- **증상**: 베트남어 선택 시 일부 UI 요소가 번역되지 않음
- **원인**: 베트남어 번역 객체에 `unitPeople`, `detailButton`, `positionStatusByType` 누락
- **해결**: 베트남어 번역 객체에 누락된 변수들 추가
  ```javascript
  vi: {
    unitPeople: ' người',
    detailButton: 'Xem chi tiết',
    positionStatusByType: 'Trạng thái theo chức vụ',
    // ...
  }
  ```
- **결과**: 완전한 3개 언어 지원 (한국어, 영어, 베트남어)

### 10. **동적 월 정보 처리** ✅ 해결
- **증상**: 대시보드 타이틀이 "July 2025"로 하드코딩됨
- **원인**: JavaScript 번역 객체에 월 정보가 하드코딩
- **해결**: Python에서 월 정보 매핑 후 HTML 문자열 치환
  ```python
  html_content = html_content.replace('{year}', str(year))
  html_content = html_content.replace('{month_korean}', month_korean)
  html_content = html_content.replace('{month_english}', month_english)
  html_content = html_content.replace('{month_vietnamese}', month_vietnamese)
  ```
- **결과**: action.sh에서 지정한 월이 모든 언어에서 올바르게 표시

### 11. **Position Detail 탭 직급 구분 문제** ✅ 해결 (2025년 8월 21일)
- **증상**: Position Detail 탭에서 모든 직급이 빈 값으로 표시되어 TYPE별로 구분되지 않음
- **원인**: CSV 데이터에서 존재하지 않는 'Position' 컬럼을 참조
  - 기존 코드: `'position': row.get('Position', '')`
  - 실제 CSV에는 'Position' 컬럼이 존재하지 않음
- **진단 과정**: 
  1. basic manpower data august.csv 컬럼 구조 분석
  2. 실제 컬럼명 확인: 'QIP POSITION 1ST  NAME', 'QIP POSITION 2ND  NAME' 등
  3. step2_dashboard_version4.py의 load_employees 함수에서 잘못된 컬럼 참조 발견
- **해결**: step2_dashboard_version4.py:225 라인 수정
  ```python
  # 기존
  'position': row.get('Position', ''),
  
  # 수정 후
  'position': row.get('QIP POSITION 1ST  NAME', ''),
  ```
- **결과**: 
  - TYPE-1: 10개 직급 정확히 구분 (SUPERVISOR, MANAGER, AQL INSPECTOR 등)
  - TYPE-2: 14개 직급 정확히 구분 (BOTTOM INSPECTOR, MTL INSPECTOR 등)
  - TYPE-3: 1개 직급 정확히 구분 (NEW QIP MEMBER)
  - 464명 전체 직원의 직급 정보가 Position Detail 탭에서 완벽하게 표시됨

## 📈 성과 지표

- **초기 상태**: 0 VND (100% 오류)
- **최종 상태**: 121,996,842 VND (100% 정확)
- **매칭률**: 84.5% (392/464 직원)
- **자동화**: 수동 작업 5단계 → 완전 자동화
- **동적 처리**: 하드코딩 제거, 모든 월 지원
- **다국어 지원**: 한국어, 영어, 베트남어 완벽 지원
- **Type별 분석**: TYPE-1, TYPE-2, TYPE-3 정확한 구분

## 🔑 핵심 교훈

1. **컬럼명 정확성**: CSV 파일의 실제 컬럼명 확인 필수
   - 코드에서 참조하는 컬럼명과 실제 CSV 파일의 컬럼명이 일치해야 함
   - 'Position' 대신 'QIP POSITION 1ST  NAME' 같은 실제 컬럼명 사용
2. **언어 변경 시 데이터 재생성**: UI 텍스트뿐만 아니라 데이터도 재생성 필요
3. **완전한 번역 객체**: 모든 언어에 동일한 변수 세트 필요
4. **동적 변수 처리**: 하드코딩 대신 템플릿 변수 사용
5. **Playwright 자동 검증**: UI 개선 후 반드시 자동 검증으로 문제 조기 발견

---

*이 지침은 프로젝트 완료 시까지 항상 준수되어야 합니다.*
*Claude는 대화 시작 시 이 파일을 자동으로 읽고 적용합니다.*
*최종 업데이트: 2025년 8월 21일 - Position Detail 탭 직급 구분 문제 해결*