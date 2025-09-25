# Individual Details Modal 언어 전환 수정 내역

## 문제점
Individual Details 탭에서 View Details를 클릭해 모달을 열었을 때, Condition Fulfillment Details 섹션에 하드코딩된 한글 텍스트가 있어 언어 전환이 되지 않았음:
- "통과" (Pass)
- "실패" (Fail)
- "3개월 연속 실패" (3-month consecutive failure)

## 해결 방법

### 1. 번역 파일 업데이트
`config_files/dashboard_translations.json`에 다음 번역 추가:
```json
"modal": {
  "conditions": {
    "pass": {
      "ko": "통과",
      "en": "Pass",
      "vi": "Đạt"
    },
    "fail": {
      "ko": "실패",
      "en": "Fail",
      "vi": "Không đạt"
    },
    "consecutiveFail": {
      "ko": "3개월 연속 실패",
      "en": "3-month consecutive failure",
      "vi": "Thất bại 3 tháng liên tiếp"
    }
  }
}
```

### 2. Python 백엔드 코드 수정
`integrated_dashboard_final.py`에서 하드코딩된 한글을 플레이스홀더로 변경:
- `'통과'` → `'[PASS]'`
- `'실패'` → `'[FAIL]'`
- `'3개월 연속 실패'` → `'[CONSECUTIVE_FAIL]'`

수정 위치:
- Line 531, 533: Excel 결과가 PASS일 때
- Line 545, 547: Excel 결과가 FAIL일 때
- Line 569-570: Fallback 로직

### 3. JavaScript 프론트엔드 코드 수정
모달에서 actualValue를 표시하기 전에 플레이스홀더를 현재 언어로 교체:
```javascript
actualValue = actualValue.replace('[PASS]', getTranslation('modal.conditions.pass', currentLanguage));
actualValue = actualValue.replace('[FAIL]', getTranslation('modal.conditions.fail', currentLanguage));
actualValue = actualValue.replace('[CONSECUTIVE_FAIL]', getTranslation('modal.conditions.consecutiveFail', currentLanguage));
```

## 검증 결과
✅ 플레이스홀더가 백엔드에서 정상적으로 생성됨
✅ JavaScript 교체 코드가 정상적으로 포함됨
✅ 번역 파일에 필요한 모든 키가 존재함
✅ 언어 전환 시 올바른 언어로 표시됨

## 테스트 방법
1. 대시보드를 브라우저에서 열기
2. Individual Details 탭으로 이동
3. View Details 클릭하여 모달 열기
4. 언어 전환 버튼으로 한국어/영어/베트남어 전환
5. Condition Fulfillment Details의 "통과", "실패" 텍스트가 올바르게 번역되는지 확인