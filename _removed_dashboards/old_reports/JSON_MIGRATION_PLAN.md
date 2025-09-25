# 📋 JSON 구조 개선 마이그레이션 계획

## 🎯 목표
TYPE-3 처리의 명확성을 개선하고 JSON과 코드 간 불일치를 해결

## 📅 마이그레이션 일정

### Phase 1: 준비 단계 (완료)
- [x] 개선된 JSON 구조 설계
- [x] 호환 가능한 버전 생성 (`position_condition_matrix_compatible.json`)
- [x] 호환성 테스트 통과
- [x] 테스트 스크립트 작성

### Phase 2: 테스트 환경 배포 (1주차)
```bash
# 1. 백업 생성
cp config_files/position_condition_matrix.json config_files/position_condition_matrix_backup_$(date +%Y%m%d).json

# 2. 테스트 환경에서 새 JSON 테스트
cp config_files/position_condition_matrix_compatible.json config_files/position_condition_matrix_test.json

# 3. 테스트 실행
python test_json_compatibility.py
./test_final.sh
```

### Phase 3: 코드 업데이트 (2주차)
필요한 코드 수정사항:

#### A. condition_matrix_manager.py 업데이트
```python
def get_type3_policy_status(self):
    """TYPE-3 정책 상태 확인"""
    type3 = self.matrix.get('position_matrix', {}).get('TYPE-3', {}).get('default', {})
    return {
        'eligible': type3.get('eligible_for_incentive', False),
        'status': type3.get('policy_status', 'UNKNOWN'),
        'reason': type3.get('policy_reason', '')
    }
```

#### B. step2_dashboard_version4.py 업데이트
```python
# TYPE-3 처리 개선
if emp_type == 'TYPE-3':
    # JSON에서 정책 정보 읽기
    policy_info = matrix_manager.get_type3_policy_status()
    if not policy_info['eligible']:
        policy_reason = policy_info['reason']
        # 기존 코드와 호환
```

### Phase 4: 단계적 전환 (3주차)

#### 4.1 A/B 테스트
- 50% 사용자: 기존 JSON
- 50% 사용자: 개선된 JSON
- 결과 비교 및 검증

#### 4.2 점진적 롤아웃
```python
# config_selector.py
import random

def get_config_file():
    """점진적 롤아웃을 위한 설정 파일 선택"""
    rollout_percentage = 30  # 30%만 새 버전 사용

    if random.random() < rollout_percentage / 100:
        return 'position_condition_matrix_compatible.json'
    else:
        return 'position_condition_matrix.json'
```

### Phase 5: 전체 배포 (4주차)

#### 5.1 최종 전환
```bash
# 1. 최종 백업
cp config_files/position_condition_matrix.json config_files/position_condition_matrix_old.json

# 2. 새 버전으로 교체
cp config_files/position_condition_matrix_compatible.json config_files/position_condition_matrix.json

# 3. 검증
python validate_dashboard.py
./action.sh
```

#### 5.2 모니터링
- 에러 로그 확인
- 대시보드 출력 검증
- TYPE-3 직원 인센티브 확인 (모두 0이어야 함)

## 🔄 롤백 계획

문제 발생 시 즉시 롤백:
```bash
# 롤백 스크립트
cp config_files/position_condition_matrix_backup_*.json config_files/position_condition_matrix.json
./action.sh
```

## ✅ 체크리스트

### 배포 전 확인사항
- [ ] 모든 테스트 통과
- [ ] 백업 생성 완료
- [ ] 롤백 스크립트 준비
- [ ] 관련 팀 공지

### 배포 후 확인사항
- [ ] TYPE-3 인센티브 = 0 확인
- [ ] 에러 로그 없음
- [ ] 대시보드 정상 표시
- [ ] validation_rules 동작 확인

## 📊 성공 지표

1. **기술적 지표**
   - JSON 로드 에러: 0건
   - TYPE-3 인센티브 오지급: 0건
   - 대시보드 표시 오류: 0건

2. **개선 지표**
   - 코드-JSON 불일치 해결: 100%
   - 명확성 개선: eligible_for_incentive 필드 활용
   - 유지보수성: JSON만으로 정책 파악 가능

## 🚨 위험 요소 및 대응

| 위험 요소 | 발생 가능성 | 영향도 | 대응 방안 |
|---------|------------|--------|----------|
| JSON 파싱 오류 | 낮음 | 높음 | 사전 테스트 완료, 즉시 롤백 |
| 기존 코드 호환성 | 낮음 | 중간 | 호환성 테스트 통과, 점진적 배포 |
| TYPE-3 처리 변경 | 매우 낮음 | 낮음 | amount_range 0 설정으로 이중 방어 |

## 📝 문서화

마이그레이션 완료 후:
1. CLAUDE.md 업데이트 - TYPE-3 정책 명시
2. position_condition_matrix.json 주석 추가
3. 개발자 가이드 업데이트

---

**작성일**: 2025-01-27
**작성자**: Claude Code
**검토 필요**: 시스템 관리자