# Version 6 Dashboard Deployment Guide

## 📋 배포 전 체크리스트

### 필수 확인 사항
- [ ] 모든 데이터 파일이 최신 상태인지 확인
- [ ] `config_files/position_condition_matrix.json` 검증
- [ ] `config_files/dashboard_translations.json` 다국어 확인
- [ ] Google Drive 동기화 상태 확인
- [ ] 이전 달 데이터 백업 완료

### Version 6 파일 구조
```
dashboard_v2/
├── modules/
│   ├── incentive_calculator.py    # 데이터 처리 엔진
│   └── complete_renderer.py       # HTML 렌더링 엔진
├── static/
│   ├── css/
│   │   └── complete_dashboard.css # 23.31 KB 스타일시트
│   └── js/
│       └── dashboard_complete.js  # 9,293줄, 121개 함수
└── output_files/
    └── Incentive_Dashboard_2025_09_Version_6.html  # 5.6 MB
```

## 🚀 배포 절차

### Step 1: 백업
```bash
# 기존 Version 5 백업
cp output_files/Incentive_Dashboard_2025_09_Version_5.html \
   output_files/backup/Version_5_$(date +%Y%m%d).html
```

### Step 2: Version 6 생성
```bash
# 모듈 방식 사용
cd dashboard_v2
python -c "from modules.complete_renderer import CompleteRenderer; \
          renderer = CompleteRenderer(); \
          renderer.save_dashboard('september', 2025)"
```

### Step 3: 검증
```bash
# 자동 검증 실행
python final_verification.py

# 핵심 기능 검증
python verify_version6_features.py
```

### Step 4: 배포
```bash
# Version 6를 메인 대시보드로 설정
cp output_files/Incentive_Dashboard_2025_09_Version_6.html \
   output_files/Incentive_Dashboard_Current.html
```

## ⚠️ 주의사항

### f-string 이스케이핑
- Version 6는 f-string 이스케이핑 문제가 해결됨
- JavaScript 코드는 별도 파일에서 관리
- `{{` `}}` 문제 없음

### 언어 전환 수정
- `dashboard_v2/static/js/dashboard_complete.js`에서 수정
- `translations` 객체 직접 수정 가능
- 재생성 불필요, JavaScript만 수정

### 데이터 업데이트
- IncentiveCalculator가 모든 데이터 처리
- Excel 데이터가 Single Source of Truth
- JSON 설정 파일로 비즈니스 룰 관리

## 🔄 롤백 계획

문제 발생 시:
```bash
# Version 5로 즉시 롤백
cp output_files/backup/Version_5_[날짜].html \
   output_files/Incentive_Dashboard_Current.html
```

## 📊 성능 비교

| 메트릭 | Version 5 | Version 6 |
|--------|-----------|-----------|
| 파일 크기 | 3.6 MB | 5.6 MB |
| 로딩 시간 | ~2초 | ~2.5초 |
| 함수 개수 | 166개 | 121개 (최적화) |
| 유지보수성 | ❌ 어려움 | ✅ 용이 |
| 언어 전환 수정 | ❌ 불가능 | ✅ 가능 |

## 📞 문제 해결

### 탭이 보이지 않을 때
- CSS 충돌 확인: `.tab-content { display: none; }` 제거
- Bootstrap 5 CDN 로드 확인

### 언어 전환 안될 때
- `updateAllTexts()` 함수 확인
- localStorage 초기화: `localStorage.clear()`

### 데이터 없을 때
- Excel 파일 경로 확인
- JSON 메타데이터 파일 확인
- IncentiveCalculator 로그 확인

## ✅ 배포 완료 확인

- [ ] 모든 6개 탭 정상 작동
- [ ] 언어 전환 (한/영/베트남어) 작동
- [ ] 조직도 렌더링 정상
- [ ] 모달 창 정상 표시
- [ ] 차트 애니메이션 정상
- [ ] 필터링 기능 작동
- [ ] Summary Cards 데이터 정확