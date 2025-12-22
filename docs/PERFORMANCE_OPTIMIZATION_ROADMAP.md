# Performance Optimization Roadmap

QIP Dashboard 성능 최적화 로드맵 (2025-12-22 작성)

**작성**: @Architect, @PerformanceEngineer, @FrontendArchitect, @BackendEngineer

---

## 📊 현재 상태 (Baseline)

| 항목 | 현재 | 목표 | 상태 |
|------|------|------|------|
| HTML 파일 크기 | 5.2 MB | 1.5-2.5 MB | 🔴 |
| 페이지 로딩 시간 | 6-15초 | <2초 | 🔴 |
| GitHub Actions 실행 | 5-8분 | 1-2분 | 🟡 |
| JavaScript 라인 | 22,357줄 | 5,000-8,000줄 | 🔴 |

---

## ✅ Phase 1: 즉시 개선 (완료)

### 1.1 현재 월만 처리 최적화

**파일**: `scripts/generate_dashboard_for_pages.py`

```python
# 기본: 현재 월만 처리 (최적화)
python scripts/generate_dashboard_for_pages.py

# 전체 월 처리 (필요시)
python scripts/generate_dashboard_for_pages.py --all
```

**효과**: 5-8분 → 1-2분 (60-75% 단축)

### 1.2 SelfContained HTML 최적화

**파일**: `scripts/generate_all_selfcontained.py`

동일한 현재 월만 처리 전략 적용.

---

## ✅ Phase 2: Python 최적화 유틸리티 (완료)

### 2.1 성능 유틸리티 라이브러리

**파일**: `scripts/utils/performance_utils.py`

```python
from scripts.utils.performance_utils import (
    fast_iterate_df,      # .iterrows() 대체 (10배 빠름)
    FastStringBuilder,    # += 대체 (3-5배 빠름)
    fast_filter_df,       # DataFrame 필터링 최적화
    PerformanceMonitor,   # 성능 측정
)

# 사용 예시
for row in fast_iterate_df(df, ['name', 'age']):
    print(row.name, row.age)

builder = FastStringBuilder()
for item in items:
    builder.append(f'<li>{item}</li>')
result = builder.build()
```

### 2.2 점진적 마이그레이션 가이드

**우선순위 높음** (자주 실행되는 코드):
- `integrated_dashboard_final.py`
- `src/step1_인센티브_계산_개선버전.py`

**우선순위 중간** (월 1회 실행):
- `scripts/verification/*.py`
- `src/validate_*.py`

---

## ✅ Phase 3: HTML 최적화 도구 (완료)

### 3.1 HTML Optimizer

**파일**: `scripts/optimize_html.py`

```bash
# 모든 대시보드 최적화
python scripts/optimize_html.py --all

# 단일 파일 최적화
python scripts/optimize_html.py -i docs/dashboard.html
```

**기능**:
- JavaScript minification (공백/주석 제거)
- CSS minification
- HTML 공백 최적화
- Gzip 압축 크기 측정

**예상 효과**: 10-20% 파일 크기 감소

---

## 🔄 Phase 4: 아키텍처 개선 (진행 중)

### 4.1 현재 아키텍처

```
[CSV 데이터] → [Python 계산] → [HTML 생성 (데이터 포함)]
                                        ↓
                              [5.2MB 단일 HTML 파일]
```

**문제점**:
- 데이터와 UI가 결합되어 있음
- 데이터 변경 시 전체 HTML 재생성 필요
- 파일 크기가 크고 로딩이 느림

### 4.2 목표 아키텍처 (단계별)

#### Stage 1: 데이터 분리 (권장)

```
[CSV 데이터] → [Python 계산] → [JSON 데이터 파일]
                                        ↓
[정적 HTML 템플릿] ← [JavaScript] ← [AJAX 로딩]
```

**장점**:
- 데이터만 업데이트 가능 (HTML 재생성 불필요)
- 캐싱 효율성 향상
- 파일 크기 대폭 감소

**구현 계획**:

```javascript
// dashboard.html (정적 템플릿)
<script>
async function loadData() {
    const response = await fetch('data/december_2025.json');
    const data = await response.json();
    renderDashboard(data);
}
</script>
```

```
docs/
├── dashboard.html          # 정적 템플릿 (500KB)
├── data/
│   ├── december_2025.json  # 월별 데이터 (200KB)
│   ├── november_2025.json
│   └── ...
└── js/
    ├── core.js             # 핵심 기능
    ├── charts.js           # 차트 (lazy load)
    └── modals.js           # 모달 (on-demand)
```

#### Stage 2: JavaScript 코드 분리

```
현재:
integrated_dashboard_final.py → 22,357줄 인라인 JS

목표:
├── static/js/core.js       # 핵심 기능 (2,000줄)
├── static/js/charts.js     # 차트 관련 (3,000줄)
├── static/js/modals.js     # 모달 (5,000줄)
├── static/js/filters.js    # 필터 (2,000줄)
└── static/js/i18n.js       # 다국어 (500줄)
```

**마이그레이션 전략**:
1. 공통 함수 추출 (formatNumber, formatDate 등)
2. 차트 코드 분리 (Chart.js 관련)
3. 모달 코드 분리
4. 템플릿 엔진 도입 검토

#### Stage 3: 빌드 시스템 도입 (장기)

```
[소스 코드]
├── src/
│   ├── js/
│   ├── css/
│   └── templates/
        ↓
[빌드 프로세스] (Webpack/Vite)
        ↓
[최적화된 출력]
├── dist/
│   ├── dashboard.min.js
│   ├── dashboard.min.css
│   └── index.html
```

---

## 📈 예상 개선 효과

| 단계 | 파일 크기 | 로딩 시간 | 워크플로우 | 노력 |
|------|----------|----------|-----------|------|
| 현재 | 5.2 MB | 6-15초 | 5-8분 | - |
| Phase 1-3 | 4.5 MB | 5-12초 | 1-2분 | ✅ 완료 |
| Stage 1 | 1.5 MB | 2-3초 | 30초 | 1주 |
| Stage 2 | 1.2 MB | 1-2초 | 30초 | 2주 |
| Stage 3 | 0.8 MB | <1초 | 20초 | 1개월 |

---

## 🛠️ 즉시 사용 가능한 명령어

```bash
# 현재 월만 대시보드 생성 (최적화)
python scripts/generate_dashboard_for_pages.py

# 모든 월 생성 (필요시)
python scripts/generate_dashboard_for_pages.py --all

# HTML 최적화
python scripts/optimize_html.py --all

# 성능 측정
python scripts/utils/performance_utils.py
```

---

## 📋 다음 단계 권장 사항

### 단기 (1-2주)
1. [ ] Phase 1-3 결과 검증
2. [ ] 성능 베이스라인 측정 스크립트 작성
3. [ ] 주요 Python 파일에 성능 유틸리티 적용

### 중기 (1개월)
1. [ ] Stage 1 데이터 분리 시작
2. [ ] JSON 데이터 생성 스크립트 개발
3. [ ] AJAX 로딩 프로토타입

### 장기 (2개월+)
1. [ ] Stage 2 JavaScript 코드 분리
2. [ ] 빌드 시스템 검토
3. [ ] CDN 배포 검토

---

## 🔗 관련 문서

- [`AGENTS.md`](../AGENTS.md) - 에이전트 팀 성능 리뷰
- [`DATA_FLOW.md`](DATA_FLOW.md) - 데이터 흐름 문서
- [`CLAUDE.md`](../CLAUDE.md) - 프로젝트 가이드

---

*Last Updated: 2025-12-22*
*Authors: @Architect, @PerformanceEngineer, @FrontendArchitect, @BackendEngineer*
