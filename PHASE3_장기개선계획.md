# Phase 3: 장기 개선 계획 - QIP 인센티브 시스템 아키텍처 혁신

## 📋 Executive Summary

현재 QIP 인센티브 시스템은 계산 로직(step1)과 표시 로직(step2)이 분리되어 있어 데이터 불일치 문제가 발생하고 있습니다. 이 문서는 1-2개월에 걸쳐 시스템을 근본적으로 재설계하는 장기 개선 계획을 제시합니다.

## 🎯 목표

1. **단일 진실 원천(Single Source of Truth)** 구현
2. **컴포넌트 기반 아키텍처** 도입
3. **실시간 검증 시스템** 구축
4. **확장 가능한 플러그인 구조** 설계

## 🏗️ 아키텍처 개선

### 1. 단일 진실 원천(Single Source of Truth) 구조

#### 현재 문제점
- step1과 step2가 독립적으로 조건을 해석
- 하드코딩된 로직이 여러 파일에 분산
- 데이터 동기화 누락으로 인한 불일치

#### 제안 아키텍처

```
┌─────────────────────────────────┐
│   Configuration Layer           │
│   (JSON/YAML 설정 파일)         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   Calculation Engine            │
│   (단일 계산 엔진)              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   Unified Data Store            │
│   (통합 데이터 저장소)          │
│   - SQLite/PostgreSQL           │
│   - 계산 결과 + 메타데이터      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   API Layer                     │
│   (RESTful/GraphQL API)         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   Presentation Layer            │
│   (Dashboard/Reports)           │
└─────────────────────────────────┘
```

#### 구현 단계

**1단계: 데이터베이스 설계 (1주)**
```sql
-- 직원 정보
CREATE TABLE employees (
    emp_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    position VARCHAR(100),
    type VARCHAR(20),
    department VARCHAR(100)
);

-- 인센티브 계산 결과
CREATE TABLE incentive_calculations (
    id SERIAL PRIMARY KEY,
    emp_id VARCHAR(20),
    year INT,
    month INT,
    amount DECIMAL(12,2),
    calculation_basis TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 조건 충족 상세
CREATE TABLE condition_evaluations (
    id SERIAL PRIMARY KEY,
    calculation_id INT,
    condition_id INT,
    is_applicable BOOLEAN,
    is_passed BOOLEAN,
    actual_value VARCHAR(100),
    threshold_value VARCHAR(100),
    FOREIGN KEY (calculation_id) REFERENCES incentive_calculations(id),
    FOREIGN KEY (condition_id) REFERENCES conditions(id)
);

-- 조건 정의
CREATE TABLE conditions (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    description TEXT,
    evaluation_logic JSON
);
```

**2단계: API 설계 (1주)**
```python
# FastAPI 기반 REST API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class IncentiveRequest(BaseModel):
    year: int
    month: str
    employee_ids: Optional[List[str]] = None

class IncentiveResponse(BaseModel):
    employee_id: str
    amount: float
    conditions: dict
    calculation_basis: str

@app.post("/calculate", response_model=List[IncentiveResponse])
async def calculate_incentives(request: IncentiveRequest):
    """인센티브 계산 API"""
    # 계산 엔진 호출
    results = calculation_engine.calculate(
        year=request.year,
        month=request.month,
        employee_ids=request.employee_ids
    )
    
    # 데이터베이스 저장
    await save_to_database(results)
    
    return results

@app.get("/employee/{emp_id}/incentive")
async def get_employee_incentive(emp_id: str, year: int, month: str):
    """특정 직원의 인센티브 조회"""
    result = await db.fetch_incentive(emp_id, year, month)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result
```

### 2. 컴포넌트 기반 아키텍처

#### 핵심 컴포넌트 설계

```python
# base_component.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IncentiveComponent(ABC):
    """인센티브 계산 컴포넌트 기본 클래스"""
    
    @abstractmethod
    def calculate(self, employee: Dict[str, Any]) -> float:
        """인센티브 계산"""
        pass
    
    @abstractmethod
    def get_conditions(self) -> List[Condition]:
        """적용 조건 반환"""
        pass
    
    @abstractmethod
    def evaluate_conditions(self, employee: Dict[str, Any]) -> Dict[str, bool]:
        """조건 평가"""
        pass
    
    def get_display_data(self) -> Dict[str, Any]:
        """UI 표시용 데이터 반환"""
        return {
            'amount': self.amount,
            'conditions': self.condition_results,
            'basis': self.calculation_basis
        }
```

```python
# aql_inspector_component.py
class AQLInspectorComponent(IncentiveComponent):
    """AQL Inspector 인센티브 컴포넌트"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.part1_base = config['part1_base_amount']
        self.part2_amount = config['part2_cfa_amount']
        self.part3_rates = config['part3_achievement_rates']
    
    def calculate(self, employee: Dict[str, Any]) -> float:
        """AQL Inspector 3파트 인센티브 계산"""
        amount = 0
        
        # Part 1: AQL 검사 평가
        if self._check_aql_conditions(employee):
            continuous_months = self._get_continuous_months(employee)
            amount += self._calculate_part1(continuous_months)
        
        # Part 2: CFA 자격증
        if employee.get('has_cfa', False):
            amount += self.part2_amount
        
        # Part 3: 목표 달성
        achievement_rate = employee.get('achievement_rate', 0)
        amount += self._calculate_part3(achievement_rate)
        
        return amount
    
    def _calculate_part1(self, months: int) -> float:
        """Part 1 계산 로직"""
        if months >= 3:
            return self.part1_base * 1.3
        elif months >= 2:
            return self.part1_base * 1.2
        elif months >= 1:
            return self.part1_base * 1.1
        return self.part1_base
    
    def _calculate_part3(self, rate: float) -> float:
        """Part 3 계산 로직"""
        for threshold, amount in self.part3_rates.items():
            if rate >= threshold:
                return amount
        return 0
```

#### 컴포넌트 레지스트리

```python
# component_registry.py
from typing import Type, Dict

class ComponentRegistry:
    """컴포넌트 등록 및 관리"""
    
    def __init__(self):
        self._components: Dict[str, Type[IncentiveComponent]] = {}
    
    def register(self, position: str, component: Type[IncentiveComponent]):
        """컴포넌트 등록"""
        self._components[position] = component
    
    def get_component(self, position: str) -> IncentiveComponent:
        """포지션에 맞는 컴포넌트 반환"""
        component_class = self._components.get(position)
        if not component_class:
            # 기본 컴포넌트 반환
            return DefaultIncentiveComponent()
        return component_class()

# 컴포넌트 등록
registry = ComponentRegistry()
registry.register('AQL INSPECTOR', AQLInspectorComponent)
registry.register('ASSEMBLY INSPECTOR', AssemblyInspectorComponent)
registry.register('AUDIT & TRAINING TEAM', AuditTrainerComponent)
```

### 3. 실시간 검증 시스템

#### 일관성 검증기

```python
# consistency_validator.py
from typing import Dict, List, Any
import logging

class ConsistencyValidator:
    """계산 결과와 표시 데이터 일관성 검증"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_rules = []
    
    def add_rule(self, rule: ValidationRule):
        """검증 규칙 추가"""
        self.validation_rules.append(rule)
    
    def validate(self, 
                 calculation_result: Dict[str, Any],
                 display_data: Dict[str, Any]) -> ValidationResult:
        """검증 실행"""
        errors = []
        warnings = []
        
        for rule in self.validation_rules:
            result = rule.validate(calculation_result, display_data)
            if result.has_errors():
                errors.extend(result.errors)
            if result.has_warnings():
                warnings.extend(result.warnings)
        
        return ValidationResult(errors, warnings)
    
    def validate_amount_consistency(self, calc_amount: float, display_amount: float):
        """금액 일치 검증"""
        if abs(calc_amount - display_amount) > 0.01:
            raise ValidationError(
                f"Amount mismatch: calculated={calc_amount}, displayed={display_amount}"
            )
    
    def validate_condition_consistency(self, calc_conditions: Dict, display_conditions: Dict):
        """조건 충족 상태 일치 검증"""
        for condition_id, calc_result in calc_conditions.items():
            display_result = display_conditions.get(condition_id)
            if not display_result:
                self.logger.warning(f"Condition {condition_id} missing in display")
                continue
            
            if calc_result['passed'] != display_result['passed']:
                raise ValidationError(
                    f"Condition {condition_id} mismatch: "
                    f"calculated={calc_result['passed']}, "
                    f"displayed={display_result['passed']}"
                )
```

#### 실시간 모니터링

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# 메트릭 정의
calculation_counter = Counter('incentive_calculations_total', 'Total calculations')
calculation_duration = Histogram('incentive_calculation_duration_seconds', 'Calculation duration')
validation_errors = Counter('validation_errors_total', 'Total validation errors')
data_consistency_gauge = Gauge('data_consistency_score', 'Data consistency score (0-100)')

class PerformanceMonitor:
    """성능 및 일관성 모니터링"""
    
    @staticmethod
    def track_calculation(func):
        """계산 성능 추적 데코레이터"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                calculation_counter.inc()
                return result
            finally:
                duration = time.time() - start_time
                calculation_duration.observe(duration)
        return wrapper
    
    @staticmethod
    def track_validation(func):
        """검증 추적 데코레이터"""
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result.has_errors():
                    validation_errors.inc(len(result.errors))
                return result
            except Exception as e:
                validation_errors.inc()
                raise
        return wrapper
```

### 4. 플러그인 아키텍처

#### 플러그인 시스템

```python
# plugin_system.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import importlib
import os

class IncentivePlugin(ABC):
    """인센티브 플러그인 인터페이스"""
    
    @abstractmethod
    def get_name(self) -> str:
        """플러그인 이름"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """플러그인 버전"""
        pass
    
    @abstractmethod
    def calculate(self, employee: Dict[str, Any]) -> float:
        """인센티브 계산"""
        pass
    
    @abstractmethod
    def get_applicable_positions(self) -> List[str]:
        """적용 가능한 포지션 목록"""
        pass

class PluginManager:
    """플러그인 관리자"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, IncentivePlugin] = {}
        self.load_plugins()
    
    def load_plugins(self):
        """플러그인 디렉토리에서 플러그인 로드"""
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                module_path = f"{self.plugin_dir}.{module_name}"
                
                try:
                    module = importlib.import_module(module_path)
                    
                    # IncentivePlugin을 구현한 클래스 찾기
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, IncentivePlugin) and 
                            attr != IncentivePlugin):
                            
                            plugin = attr()
                            self.plugins[plugin.get_name()] = plugin
                            print(f"Loaded plugin: {plugin.get_name()} v{plugin.get_version()}")
                
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")
    
    def get_plugin_for_position(self, position: str) -> Optional[IncentivePlugin]:
        """포지션에 맞는 플러그인 반환"""
        for plugin in self.plugins.values():
            if position in plugin.get_applicable_positions():
                return plugin
        return None
```

#### 플러그인 예제

```python
# plugins/special_bonus_plugin.py
from plugin_system import IncentivePlugin

class SpecialBonusPlugin(IncentivePlugin):
    """특별 보너스 플러그인"""
    
    def get_name(self) -> str:
        return "SpecialBonus"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def calculate(self, employee: Dict[str, Any]) -> float:
        """특별 보너스 계산"""
        base_amount = 500000  # 기본 보너스
        
        # 연속 근무 개월에 따른 보너스
        continuous_months = employee.get('continuous_months', 0)
        if continuous_months >= 12:
            return base_amount * 2
        elif continuous_months >= 6:
            return base_amount * 1.5
        elif continuous_months >= 3:
            return base_amount * 1.2
        
        return base_amount
    
    def get_applicable_positions(self) -> List[str]:
        return ['SPECIAL POSITION', 'BONUS ELIGIBLE']
```

## 📊 구현 로드맵

### Phase 3-1: 기반 구축 (2주)

**Week 1: 데이터베이스 및 API 설계**
- [ ] 데이터베이스 스키마 설계 및 구현
- [ ] API 명세 작성
- [ ] 기본 CRUD API 구현
- [ ] 인증/권한 시스템 구축

**Week 2: 계산 엔진 통합**
- [ ] 기존 계산 로직 리팩토링
- [ ] 컴포넌트 기본 클래스 구현
- [ ] 주요 포지션별 컴포넌트 구현
- [ ] 단위 테스트 작성

### Phase 3-2: 핵심 기능 구현 (3주)

**Week 3: 컴포넌트 시스템**
- [ ] 컴포넌트 레지스트리 구현
- [ ] 모든 포지션별 컴포넌트 구현
- [ ] 컴포넌트 테스트 및 검증

**Week 4: 검증 시스템**
- [ ] ConsistencyValidator 구현
- [ ] 검증 규칙 정의 및 구현
- [ ] 실시간 모니터링 시스템 구축
- [ ] 알림 시스템 연동

**Week 5: 플러그인 시스템**
- [ ] 플러그인 인터페이스 정의
- [ ] PluginManager 구현
- [ ] 샘플 플러그인 개발
- [ ] 플러그인 문서화

### Phase 3-3: 통합 및 최적화 (3주)

**Week 6: 시스템 통합**
- [ ] 모든 컴포넌트 통합 테스트
- [ ] 기존 시스템과의 호환성 테스트
- [ ] 데이터 마이그레이션 스크립트 작성

**Week 7: 성능 최적화**
- [ ] 데이터베이스 쿼리 최적화
- [ ] 캐싱 전략 구현
- [ ] 병렬 처리 구현
- [ ] 부하 테스트

**Week 8: 배포 준비**
- [ ] 문서화 완성
- [ ] 운영 가이드 작성
- [ ] 모니터링 대시보드 구축
- [ ] 백업/복구 절차 수립

## 🎯 기대 효과

### 정량적 효과
- **데이터 일관성**: 99.9% 이상 달성
- **계산 성능**: 50% 향상 (병렬 처리)
- **유지보수 시간**: 70% 감소
- **버그 발생률**: 80% 감소

### 정성적 효과
- **확장성**: 새로운 인센티브 유형 쉽게 추가
- **투명성**: 모든 계산 과정 추적 가능
- **신뢰성**: 자동 검증으로 오류 사전 방지
- **유연성**: 플러그인으로 맞춤형 기능 추가

## 🚨 리스크 및 대응 방안

### 기술적 리스크

| 리스크 | 영향도 | 가능성 | 대응 방안 |
|--------|--------|--------|-----------|
| 데이터 마이그레이션 실패 | 높음 | 중간 | 단계적 마이그레이션, 롤백 계획 수립 |
| 성능 저하 | 중간 | 낮음 | 캐싱, 인덱싱, 쿼리 최적화 |
| 호환성 문제 | 중간 | 중간 | 병렬 운영 기간 설정, 점진적 전환 |
| 보안 취약점 | 높음 | 낮음 | 보안 감사, 침투 테스트 실시 |

### 운영적 리스크

| 리스크 | 영향도 | 가능성 | 대응 방안 |
|--------|--------|--------|-----------|
| 사용자 교육 부족 | 중간 | 중간 | 상세한 사용자 가이드, 교육 세션 |
| 시스템 장애 | 높음 | 낮음 | 이중화, 자동 복구, 24/7 모니터링 |
| 데이터 손실 | 높음 | 낮음 | 정기 백업, 복제 시스템 구축 |

## 📝 결론

이 장기 개선 계획을 통해 QIP 인센티브 시스템은 현재의 파편화된 구조에서 벗어나 통합되고 확장 가능한 엔터프라이즈급 시스템으로 진화할 것입니다. 단일 진실 원천 구현으로 데이터 일관성 문제를 근본적으로 해결하고, 컴포넌트 기반 아키텍처로 유지보수성과 확장성을 크게 향상시킬 수 있습니다.

특히 플러그인 시스템을 통해 향후 비즈니스 요구사항 변화에 유연하게 대응할 수 있으며, 실시간 검증 시스템으로 오류를 사전에 방지하여 시스템의 신뢰성을 획기적으로 높일 수 있을 것입니다.

---

**작성일**: 2024년 8월 24일  
**작성자**: Claude Code Assistant  
**버전**: 1.0.0