# Excel 파일 컬럼 매핑 문서 (Excel Column Mapping Documentation)

## 📊 Excel 파일 구조 개요
- **파일명**: `output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv/xlsx`
- **목적**: QIP 인센티브 계산 결과의 단일 진실 소스 (Single Source of Truth)
- **레코드 수**: 401명 (활성 직원 기준)

## 🗂️ 컬럼 카테고리별 분류

### 1. 기본 정보 (Basic Information)
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| STT | 일련번호 | - |
| Employee No | 사번 | 모든 탭 - 직원 식별자 |
| Full Name | 성명 | 개인별 상세 탭 |
| Entrance Date | 입사일 | 개인별 상세 탭 |
| Personnel Number | 인사번호 | - |
| Stop working Date | 퇴사일 | 0일 근무자 모달 |

### 2. 직책 정보 (Position Information)
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| QIP POSITION 1ST NAME | QIP 1차 직책 | 직급별 상세 탭 |
| QIP POSITION NAME CODE1 | 1차 직책 코드 | - |
| QIP POSITION 2ND NAME | QIP 2차 직책 | - |
| QIP POSITION NAME CODE2 | 2차 직책 코드 | - |
| QIP POSITION 3RD NAME | QIP 3차 직책 | - |
| FINAL QIP POSITION NAME CODE | 최종 직책 코드 | - |
| ROLE TYPE STD | 역할 타입 (TYPE-1/2/3) | Type별 요약, 직급별 상세 탭 |

### 3. 인센티브 정보 (Incentive Information)
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| Final Incentive amount | 최종 인센티브 금액 | 요약 탭 - 총 지급액 |
| September_Incentive | 9월 인센티브 | 개인별 상세 탭 |
| Previous_Incentive | 이전 월 인센티브 | - |
| Previous_Month_Incentive | 이전 월 인센티브 금액 | - |
| Previous_Continuous_Months | 이전 연속 개월 수 | - |
| Current_Expected_Months | 현재 예상 개월 수 | - |
| Continuous_Months | 연속 개월 수 | 개인별 상세 탭 |
| Next_Month_Expected | 다음 월 예상 | - |
| Talent_Pool_Bonus | 탤런트풀 보너스 | 개인별 상세 탭 |
| Talent_Pool_Member | 탤런트풀 멤버 여부 | - |

### 4. 출근 데이터 (Attendance Data) ⚠️ 핵심
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| **Total Working Days** | **총 근무일수 (전체)** | **검증 탭 - 총 근무일수 모달** |
| **Actual Working Days** | **실제 근무일수** | **검증 탭 - 0일 근무자 모달** |
| AR1 Absences | AR1 결근 | - |
| Unapproved Absences | 무단결근 일수 | 검증 탭 - 무단결근 모달 ✅ |
| Absence Rate (raw) | 결근율 (원시) | - |
| attendance_rate | 출근율 | 개인별 상세 탭 |

### 5. 출근 조건 (Attendance Conditions)
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| attendancy condition 1 | 실제 근무일 0일 | 검증 탭 - 0일 근무자 |
| attendancy condition 2 | 무단결근 3일 이상 | 검증 탭 - 무단결근 |
| attendancy condition 3 | 결근율 12% 초과 | - |
| attendancy condition 4 | 최소 근무일 미충족 | 검증 탭 - 최소일 미충족 |

### 6. 품질 데이터 (Quality Data)
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| Total Valiation Qty | 총 검증 수량 | - |
| Total Pass Qty | 총 통과 수량 | - |
| Pass % | 통과율 | - |
| 5PRS_Pass_Rate | 5PRS 통과율 | 검증 탭 - 5PRS 통과율 |
| 5PRS_Inspection_Qty | 5PRS 검사량 | 검증 탭 - 5PRS 검사량 |
| September AQL Failures | 9월 AQL 실패 | 검증 탭 - AQL FAIL |
| Continuous_FAIL | 연속 실패 | 검증 탭 - 3개월 연속 |
| BUILDING | 건물 | - |
| Area_Reject_Rate | 구역 불량률 | 검증 탭 - 구역 AQL |

### 7. 조건 평가 결과 (Condition Evaluation) - 10개 조건
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| cond_1_attendance_rate | 조건1: 출근율 | 인센티브 기준 탭 |
| cond_2_unapproved_absence | 조건2: 무단결근 | 인센티브 기준 탭 |
| cond_3_actual_working_days | 조건3: 실제 근무일 | 인센티브 기준 탭 |
| cond_4_minimum_days | 조건4: 최소 근무일 | 인센티브 기준 탭 |
| cond_5_aql_personal_failure | 조건5: 개인 AQL 실패 | 인센티브 기준 탭 |
| cond_6_aql_continuous | 조건6: 연속 AQL 실패 | 인센티브 기준 탭 |
| cond_7_aql_team_area | 조건7: 팀/구역 AQL | 인센티브 기준 탭 |
| cond_8_area_reject | 조건8: 구역 불량률 | 인센티브 기준 탭 |
| cond_9_5prs_pass_rate | 조건9: 5PRS 통과율 | 인센티브 기준 탭 |
| cond_10_5prs_inspection_qty | 조건10: 5PRS 검사량 | 인센티브 기준 탭 |

### 8. 조건 평가 메타데이터
| 컬럼명 | 설명 | 대시보드 사용처 |
|--------|------|----------------|
| conditions_applicable | 적용 가능 조건 수 | - |
| conditions_passed | 통과한 조건 수 | - |
| conditions_pass_rate | 조건 통과율 | - |

## 🚨 해결된 문제점 및 개선 사항

### 1. ~~근무일수 불일치 문제~~ ✅ 해결됨
**문제**: 모달에서 하드코딩된 13일 vs Excel의 실제 데이터
- Excel `Total Working Days`: 출근 데이터 기반 실제 값
- 모달 표시: 하드코딩된 13일

**해결**:
1. Excel의 실제 출근 데이터를 읽어서 사용 (15일)
2. 일별 출근 데이터를 Excel에 추가하여 캘린더 뷰 생성

### 2. ~~무단결근 데이터 중복 컬럼~~ ✅ 해결됨
**문제**: 두 개의 유사한 컬럼이 혼란 야기
- `Unapproved Absences`: 실제 무단결근 데이터 (정상)
- `Unapproved Absence Days`: 모두 0 (버그)

**해결**:
1. Python 코드에서 중복 컬럼 생성 코드 제거
2. `Unapproved Absences` 컬럼만 사용하도록 통일

### 2. 데이터 소스 통합 필요
**현재 상황**:
- 일부 데이터는 Excel에서 읽음
- 일부 데이터는 JavaScript에서 계산/하드코딩

**개선 방안**:
- 모든 계산 결과를 Excel에 저장
- 대시보드는 Excel 데이터만 표시

## 📋 구현 계획

### Phase 1: Excel 데이터 확장
1. 일별 출근 데이터 컬럼 추가 (Day_1 ~ Day_19)
2. 캘린더 뷰용 메타데이터 추가
3. 모달별 필요 데이터 컬럼 추가

### Phase 2: 대시보드 수정
1. 모든 하드코딩된 값을 Excel 읽기로 변경
2. `window.excelData` 객체로 모든 Excel 데이터 로드
3. 모달 함수를 Excel 데이터 기반으로 수정

### Phase 3: 검증 시스템
1. Excel과 대시보드 데이터 일치 검증 함수
2. 자동화된 데이터 일관성 체크
3. 불일치 발견 시 경고 표시

## 🔄 데이터 플로우
```
[출근 데이터 CSV] → [인센티브 계산 Python] → [Excel 파일 생성] → [대시보드 HTML]
                                                    ↓
                                            [Single Source of Truth]
                                                    ↓
                                            모든 탭/모달이 참조
```

## 📝 사용 가이드
1. 이 문서를 참조하여 Excel 컬럼의 의미 파악
2. 대시보드 개발 시 필요한 데이터의 Excel 컬럼명 확인
3. 새로운 기능 추가 시 Excel에 먼저 컬럼 추가
4. 대시보드는 Excel 데이터만 읽어서 표시

---
*Last Updated: 2025-09-20*
*Version: 1.1*
*Changes: Removed duplicate Unapproved Absence Days column*