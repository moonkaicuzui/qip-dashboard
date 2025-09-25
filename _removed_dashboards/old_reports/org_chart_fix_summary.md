# Org Chart Tab 언어 전환 수정 내역

## 수정 완료 항목

### 1. ✅ tabs.orgchart 표기 문제 해결
- **문제**: 탭 제목이 "tabs.orgchart"로 표시됨
- **원인**: 번역 키 불일치 (tabs.orgchart vs tabs.orgChart)
- **해결**: `dashboard_translations.json`에 두 키 모두 추가 (`orgChart`, `orgchart`)

### 2. ✅ "참고: AQL INSPECTOR..." 메시지 언어 전환
- **문제**: 하드코딩된 한글 텍스트
- **해결**:
  - `orgChart.noteLabel`: "참고" / "Note" / "Lưu ý"
  - `orgChart.excludedPositions`: 제외 직급 안내 메시지

### 3. ✅ "전체 조직" 언어 전환
- **문제**: Breadcrumb에 하드코딩된 한글
- **해결**: `orgChart.entireOrganization` 번역 추가

### 4. ✅ "TYPE-1 관리자 인센티브 구조" 언어 전환
- **문제**: 메인 제목이 하드코딩
- **해결**: `orgChart.title` 번역 사용

### 5. ✅ 모달 타이틀 날짜 형식
- **문제**: 모달의 타이틀과 날짜가 적절히 번역되지 않음
- **해결**: `orgChart.modalTitle` 번역 추가

### 6. ✅ 모달 내 하드코딩된 한글 제거
- **해결**: 모든 하드코딩된 텍스트를 번역 키로 교체

### 7. ✅ A.MANAGER 모달의 깨진 번역 참조
- **문제**: "orgChart.calculationFormulas.assistantManager" 텍스트 그대로 표시
- **원인**: assistantManager 키 누락
- **해결**: `calculationFormulas.assistantManager` 번역 추가

## 번역 파일 추가 내용

```json
{
  "tabs": {
    "orgchart": {
      "ko": "조직도",
      "en": "Org Chart",
      "vi": "Sơ đồ tổ chức"
    }
  },
  "orgChart": {
    "entireOrganization": {
      "ko": "전체 조직",
      "en": "Entire Organization",
      "vi": "Toàn bộ tổ chức"
    },
    "modalTitle": {
      "ko": "인센티브 계산 상세",
      "en": "Incentive Calculation Details",
      "vi": "Chi tiết tính khen thưởng"
    },
    "calculationFormulas": {
      "assistantManager": {
        "ko": "LINE LEADER 평균 × 3",
        "en": "LINE LEADER Average × 3",
        "vi": "Trung bình LINE LEADER × 3"
      }
    }
  }
}
```

## Python 코드 수정 내용

1. HTML에 ID 추가:
   - `orgChartNoteLabel`
   - `orgChartExcludedPositions`
   - `orgBreadcrumbText`
   - `orgChartTitleMain`
   - `orgChartSubtitleMain`

2. `updateOrgChartUIText()` 함수 개선:
   - 모든 Org Chart 관련 텍스트 업데이트
   - 번역 키 fallback 처리

3. `updateAllTexts()`에 `updateOrgChartUIText()` 호출 추가

## 테스트 방법

1. 대시보드 열기
2. Org Chart 탭 클릭
3. 언어 전환 버튼(한국어/English/Tiếng Việt) 클릭
4. 다음 항목들이 올바르게 번역되는지 확인:
   - 탭 제목
   - "참고" 메시지
   - "전체 조직" 텍스트
   - "TYPE-1 관리자 인센티브 구조" 제목
   - 조직도 노드 클릭 시 나타나는 모달의 모든 텍스트

## 결과

모든 Org Chart 탭의 하드코딩된 한글 텍스트가 제거되고, 완전한 다국어 지원이 구현되었습니다.