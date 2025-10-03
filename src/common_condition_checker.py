"""
공통 조건 체크 모듈
QIP 인센티브 시스템의 모든 조건을 통합 관리

작성일: 2025-01-24
버전: 1.0

이 모듈은 position_condition_matrix.json을 기반으로
모든 타입/직급별 조건을 일관되게 체크합니다.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

class ConditionChecker:
    """통합 조건 체크 클래스"""
    
    def __init__(self, matrix_path: str = None):
        """
        초기화
        
        Args:
            matrix_path: position_condition_matrix.json 경로
        """
        self.matrix = self._load_matrix(matrix_path)
        self.condition_mapping = {
            1: '출근율_Attendance_Rate_Percent',           # 출근율 ≥88% (Phase 3: 한국어 라벨 추가)
            2: 'unapproved_absence',        # 무단결근 ≤2일
            3: 'actual_working_days',       # 실제 근무일 >0일
            4: 'minimum_working_days',      # 최소 근무일 ≥12일
            5: 'aql_monthly_failure',       # 개인 AQL: 당월 실패 0건
            6: 'aql_3month_continuous',     # 개인 AQL: 3개월 연속 실패 없음
            7: 'team_area_aql_continuous',  # 팀/구역 AQL: 3개월 연속 실패 없음
            8: 'area_reject_rate',          # 담당구역 reject율 <3%
            9: '5prs_pass_rate',            # 5PRS 통과율 ≥95%
            10: '5prs_inspection_qty'       # 5PRS 검사량 ≥100개
        }
    
    def _load_matrix(self, matrix_path: str = None) -> Dict:
        """position_condition_matrix.json 로드"""
        if matrix_path is None:
            matrix_path = Path(__file__).parent.parent / 'config_files' / 'position_condition_matrix.json'
        
        try:
            with open(matrix_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Matrix 로드 실패: {e}")
            return {}
    
    def get_position_config(self, emp_type: str, position: str) -> Dict:
        """
        직급별 조건 설정 반환
        
        Args:
            emp_type: 직원 타입 (TYPE-1, TYPE-2, TYPE-3)
            position: 직급명
            
        Returns:
            직급별 조건 설정 딕셔너리
        """
        if not self.matrix:
            return {}
        
        position_upper = position.upper()
        type_config = self.matrix.get('position_matrix', {}).get(emp_type, {})
        
        # 직급별 설정 찾기
        for pos_key, pos_config in type_config.items():
            if pos_key == 'default':
                continue
            patterns = pos_config.get('patterns', [])
            for pattern in patterns:
                if pattern in position_upper:
                    return pos_config
        
        # 기본값 반환
        return type_config.get('default', {})
    
    def check_attendance_conditions(self, employee_data: Dict) -> Dict[int, bool]:
        """
        출근 조건 체크 (조건 1-4)
        
        Args:
            employee_data: 직원 데이터
            
        Returns:
            {조건ID: 충족여부} 딕셔너리
        """
        results = {}
        
        # 조건 1: 출근율 ≥88%
        attendance_rate = 100 - employee_data.get('결근율_Absence_Rate_Percent', 0)
        results[1] = attendance_rate >= 88
        
        # 조건 2: 무단결근 ≤2일
        unapproved_absence = employee_data.get('Unapproved Absence Days', 0)
        results[2] = unapproved_absence <= 2
        
        # 조건 3: 실제 근무일 >0일
        actual_days = employee_data.get('Actual Working Days', 0)
        results[3] = actual_days > 0
        
        # 조건 4: 최소 근무일 ≥12일
        results[4] = actual_days >= 12
        
        return results
    
    def check_aql_monthly_failure(self, employee_data: Dict, month: str) -> bool:
        """
        조건 5: 개인 AQL 당월 실패 0건
        
        Args:
            employee_data: 직원 데이터
            month: 월 (예: 'July')
            
        Returns:
            조건 충족 여부
        """
        aql_col = f"{month} AQL Failures"
        failures = employee_data.get(aql_col, 0)
        return failures == 0
    
    def check_aql_3month_continuous(self, employee_data: Dict, aql_history: pd.DataFrame = None) -> bool:
        """
        조건 6: 개인 AQL 3개월 연속 실패 없음
        
        Args:
            employee_data: 직원 데이터
            aql_history: AQL 이력 데이터프레임
            
        Returns:
            조건 충족 여부
        """
        # Continuous_FAIL 컬럼 확인
        continuous_fail = employee_data.get('Continuous_FAIL', 'NO')
        if continuous_fail == 'YES':
            return False
        
        # AQL history에서 추가 확인 (옵션)
        if aql_history is not None:
            emp_id = employee_data.get('Employee No')
            emp_history = aql_history[aql_history['Employee No'] == emp_id]
            
            if not emp_history.empty:
                # 최근 3개월 실패 확인
                recent_failures = 0
                for month_col in aql_history.columns:
                    if 'FAIL' in month_col.upper():
                        if emp_history[month_col].values[0] > 0:
                            recent_failures += 1
                
                if recent_failures >= 3:
                    return False
        
        return True
    
    def check_team_area_aql_continuous(self, 
                                       manager_id: str, 
                                       subordinates_data: pd.DataFrame,
                                       area_data: Dict = None) -> bool:
        """
        조건 7: 팀/구역 AQL 3개월 연속 실패 없음
        
        Args:
            manager_id: 관리자 ID
            subordinates_data: 부하직원 데이터
            area_data: 구역 데이터 (옵션)
            
        Returns:
            조건 충족 여부
        """
        # 부하직원 중 3개월 연속 실패자 확인
        subordinates = subordinates_data[subordinates_data['MST direct boss name'] == manager_id]
        
        for _, sub in subordinates.iterrows():
            if sub.get('Continuous_FAIL', 'NO') == 'YES':
                return False
        
        # 구역 데이터가 있으면 추가 확인
        if area_data:
            area_continuous_fail = area_data.get('continuous_fail_count', 0)
            if area_continuous_fail > 0:
                return False
        
        return True
    
    def check_area_reject_rate(self, 
                               employee_id: str,
                               area_mapping: Dict,
                               aql_data: pd.DataFrame) -> Tuple[bool, float]:
        """
        조건 8: 담당구역 reject율 <3%
        
        Args:
            employee_id: 직원 ID
            area_mapping: 구역 매핑 정보
            aql_data: AQL 데이터
            
        Returns:
            (조건 충족 여부, reject율)
        """
        # 담당 구역 찾기
        area_config = None
        if 'auditor_trainer_areas' in area_mapping:
            area_config = area_mapping['auditor_trainer_areas'].get(employee_id)
        elif 'model_master' in area_mapping:
            model_masters = area_mapping['model_master'].get('employees', {})
            if employee_id in model_masters:
                # Model Master는 전체 구역 담당
                area_config = {'type': 'ALL'}
        
        if not area_config:
            return True, 0.0  # 담당 구역 없으면 조건 충족으로 처리
        
        # 구역별 reject율 계산
        total_inspections = 0
        total_failures = 0
        
        if area_config.get('type') == 'ALL':
            # 전체 구역
            for _, row in aql_data.iterrows():
                inspections = row.get('Total Inspections', 0)
                failures = row.get('Total Failures', 0)
                total_inspections += inspections
                total_failures += failures
        else:
            # 특정 구역 조건에 따라 필터링
            conditions = area_config.get('conditions', [])
            for condition in conditions:
                filters = condition.get('filters', [])
                # 필터 적용 로직 (실제 구현 필요)
                # ...
        
        if total_inspections > 0:
            reject_rate = (total_failures / total_inspections) * 100
            return reject_rate < 3.0, reject_rate
        
        return True, 0.0
    
    def check_5prs_conditions(self, employee_data: Dict) -> Dict[int, bool]:
        """
        5PRS 조건 체크 (조건 9-10)
        
        Args:
            employee_data: 직원 데이터
            
        Returns:
            {조건ID: 충족여부} 딕셔너리
        """
        results = {}
        
        # 조건 9: 5PRS 통과율 ≥95%
        pass_rate = employee_data.get('Pass %', 0)
        results[9] = pass_rate >= 95
        
        # 조건 10: 5PRS 검사량 ≥100개
        inspection_qty = employee_data.get('Total Valiation Qty', 0)
        results[10] = inspection_qty >= 100
        
        return results
    
    def check_all_conditions(self, 
                            employee_data: Dict,
                            emp_type: str,
                            position: str,
                            month: str = 'July',
                            subordinates_data: pd.DataFrame = None,
                            aql_history: pd.DataFrame = None,
                            area_mapping: Dict = None,
                            aql_data: pd.DataFrame = None) -> Dict:
        """
        직원의 모든 조건 체크
        
        Args:
            employee_data: 직원 데이터
            emp_type: 직원 타입
            position: 직급
            month: 월
            subordinates_data: 부하직원 데이터 (옵션)
            aql_history: AQL 이력 (옵션)
            area_mapping: 구역 매핑 (옵션)
            aql_data: AQL 데이터 (옵션)
            
        Returns:
            {
                'applicable_conditions': [적용 조건 ID 리스트],
                'results': {조건ID: 충족여부},
                'all_passed': 모든 적용 조건 충족 여부,
                'details': {조건ID: 상세정보}
            }
        """
        # 직급별 설정 가져오기
        pos_config = self.get_position_config(emp_type, position)
        applicable_conditions = pos_config.get('applicable_conditions', [])
        
        results = {}
        details = {}
        
        # 출근 조건 (1-4)
        if any(c in applicable_conditions for c in [1, 2, 3, 4]):
            attendance_results = self.check_attendance_conditions(employee_data)
            for cond_id, passed in attendance_results.items():
                if cond_id in applicable_conditions:
                    results[cond_id] = passed
                    details[cond_id] = {
                        'name': self.matrix['conditions'][str(cond_id)]['description'],
                        'passed': passed
                    }
        
        # 조건 5: 개인 AQL 당월
        if 5 in applicable_conditions:
            passed = self.check_aql_monthly_failure(employee_data, month)
            results[5] = passed
            details[5] = {
                'name': '개인 AQL: 당월 실패 0건',
                'passed': passed,
                'failures': employee_data.get(f'{month} AQL Failures', 0)
            }
        
        # 조건 6: 개인 AQL 3개월 연속
        if 6 in applicable_conditions:
            passed = self.check_aql_3month_continuous(employee_data, aql_history)
            results[6] = passed
            details[6] = {
                'name': '개인 AQL: 3개월 연속 실패 없음',
                'passed': passed,
                'continuous_fail': employee_data.get('Continuous_FAIL', 'NO')
            }
        
        # 조건 7: 팀/구역 AQL 3개월 연속
        if 7 in applicable_conditions and subordinates_data is not None:
            manager_id = employee_data.get('Employee No')
            passed = self.check_team_area_aql_continuous(manager_id, subordinates_data)
            results[7] = passed
            details[7] = {
                'name': '팀/구역 AQL: 3개월 연속 실패 없음',
                'passed': passed
            }
        
        # 조건 8: 담당구역 reject율
        if 8 in applicable_conditions and area_mapping and aql_data is not None:
            emp_id = employee_data.get('Employee No')
            passed, reject_rate = self.check_area_reject_rate(emp_id, area_mapping, aql_data)
            results[8] = passed
            details[8] = {
                'name': '담당구역 reject율 <3%',
                'passed': passed,
                'reject_rate': reject_rate
            }
        
        # 5PRS 조건 (9-10)
        if any(c in applicable_conditions for c in [9, 10]):
            prs_results = self.check_5prs_conditions(employee_data)
            for cond_id, passed in prs_results.items():
                if cond_id in applicable_conditions:
                    results[cond_id] = passed
                    details[cond_id] = {
                        'name': self.matrix['conditions'][str(cond_id)]['description'],
                        'passed': passed
                    }
        
        # 모든 적용 조건 충족 여부
        all_passed = all(results.get(c, False) for c in applicable_conditions)
        
        return {
            'applicable_conditions': applicable_conditions,
            'results': results,
            'all_passed': all_passed,
            'details': details
        }
    
    def format_condition_summary(self, check_result: Dict, language: str = 'ko') -> str:
        """
        조건 체크 결과를 보기 좋게 포맷팅
        
        Args:
            check_result: check_all_conditions의 반환값
            language: 언어 ('ko', 'en', 'vi')
            
        Returns:
            포맷팅된 문자열
        """
        lines = []
        
        if language == 'ko':
            lines.append("📊 조건 충족 현황")
            lines.append("-" * 40)
            
            for cond_id in check_result['applicable_conditions']:
                detail = check_result['details'].get(cond_id, {})
                status = "✅" if detail.get('passed', False) else "❌"
                name = detail.get('name', f'조건 {cond_id}')
                lines.append(f"{status} {name}")
            
            lines.append("-" * 40)
            if check_result['all_passed']:
                lines.append("✅ 모든 조건 충족 → 인센티브 지급")
            else:
                lines.append("❌ 조건 미충족 → 인센티브 미지급")
        
        return "\n".join(lines)


# 전역 인스턴스 생성 (싱글톤 패턴)
_condition_checker = None

def get_condition_checker() -> ConditionChecker:
    """전역 ConditionChecker 인스턴스 반환"""
    global _condition_checker
    if _condition_checker is None:
        _condition_checker = ConditionChecker()
    return _condition_checker