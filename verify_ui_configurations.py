#!/usr/bin/env python3
"""
UI 구성 검증 스크립트
모든 타입/직급 조합에 대한 UI 표시 검증
"""

import json
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from common_condition_checker import ConditionChecker, get_condition_checker

class UIConfigurationVerifier:
    """UI 구성 검증 클래스"""
    
    def __init__(self):
        self.checker = get_condition_checker()
        self.matrix_path = Path(__file__).parent / 'config_files' / 'position_condition_matrix.json'
        self.matrix = self._load_matrix()
        self.verification_results = []
        
    def _load_matrix(self) -> Dict:
        """position_condition_matrix.json 로드"""
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_positions(self) -> List[Tuple[str, str, List[int]]]:
        """모든 타입/직급 조합 추출"""
        all_positions = []
        
        for emp_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
            type_config = self.matrix['position_matrix'].get(emp_type, {})
            
            for position_key, position_config in type_config.items():
                if position_key == 'default':
                    continue
                    
                # 직급명 생성 (패턴의 첫 번째 값 사용)
                patterns = position_config.get('patterns', [])
                if patterns:
                    position_name = patterns[0]
                else:
                    position_name = position_key.replace('_', ' ')
                
                applicable = position_config.get('applicable_conditions', [])
                all_positions.append((emp_type, position_name, applicable))
        
        return all_positions
    
    def create_test_employee(self, emp_type: str, position: str, 
                           emp_id: str = 'TEST001') -> Dict:
        """테스트용 직원 데이터 생성"""
        return {
            'Employee No': emp_id,
            'Full Name': f'Test {position}',
            'Employee Type': emp_type,
            'Position': position,
            'Absence Rate (raw)': 5,  # 출근율 95%
            'Unapproved Absence Days': 0,
            'Actual Working Days': 22,
            'July AQL Failures': 0,
            'Continuous_FAIL': 'NO',
            'Pass %': 98,
            'Total Valiation Qty': 150,
            'MST direct boss name': None
        }
    
    def verify_condition_display(self, emp_type: str, position: str, 
                                expected_conditions: List[int]) -> Dict:
        """조건 표시 검증"""
        # 테스트 직원 데이터 생성
        employee_data = self.create_test_employee(emp_type, position)
        
        # 부하직원 데이터 (LINE LEADER 테스트용)
        subordinates_df = pd.DataFrame([
            {'Employee No': 'SUB001', 'MST direct boss name': 'TEST001', 'Continuous_FAIL': 'NO'},
            {'Employee No': 'SUB002', 'MST direct boss name': 'TEST001', 'Continuous_FAIL': 'YES'},
        ])
        
        # 조건 체크 실행
        result = self.checker.check_all_conditions(
            employee_data=employee_data,
            emp_type=emp_type,
            position=position,
            month='July',
            subordinates_data=subordinates_df if position == 'LINE LEADER' else None
        )
        
        # 검증 결과
        actual_conditions = result['applicable_conditions']
        
        verification = {
            'type': emp_type,
            'position': position,
            'expected_conditions': expected_conditions,
            'actual_conditions': actual_conditions,
            'match': set(expected_conditions) == set(actual_conditions),
            'condition_results': result['results'],
            'all_passed': result['all_passed']
        }
        
        # 특별 검증: 3개월 연속 실패 체크 조건들
        if any(c in actual_conditions for c in [6, 7, 8]):
            verification['3month_check'] = self._verify_3month_logic(
                emp_type, position, result, subordinates_df
            )
        
        return verification
    
    def _verify_3month_logic(self, emp_type: str, position: str, 
                            result: Dict, subordinates_df: pd.DataFrame) -> Dict:
        """3개월 연속 실패 로직 검증"""
        checks = {}
        
        # 조건 6: 개인 AQL 3개월 연속
        if 6 in result['applicable_conditions']:
            checks['condition_6'] = {
                'name': '개인 AQL 3개월 연속 실패 없음',
                'result': result['results'].get(6, None),
                'logic_exists': True,
                'detail': result['details'].get(6, {})
            }
        
        # 조건 7: 팀/구역 AQL 3개월 연속 (LINE LEADER)
        if 7 in result['applicable_conditions']:
            # 부하직원 중 연속 실패자 확인
            has_failing_subordinate = any(
                subordinates_df[subordinates_df['MST direct boss name'] == 'TEST001']['Continuous_FAIL'] == 'YES'
            )
            
            checks['condition_7'] = {
                'name': '팀/구역 AQL 3개월 연속 실패 없음',
                'result': result['results'].get(7, None),
                'logic_exists': True,
                'has_failing_subordinate': has_failing_subordinate,
                'expected_result': not has_failing_subordinate,
                'detail': result['details'].get(7, {})
            }
        
        # 조건 8: 담당구역 reject율
        if 8 in result['applicable_conditions']:
            checks['condition_8'] = {
                'name': '담당구역 reject율 <3%',
                'result': result['results'].get(8, None),
                'logic_exists': True,
                'detail': result['details'].get(8, {})
            }
        
        return checks
    
    def run_full_verification(self) -> None:
        """전체 검증 실행"""
        print("\n" + "=" * 80)
        print("🔍 UI 구성 전체 검증 시작")
        print("=" * 80)
        
        all_positions = self.get_all_positions()
        total_positions = len(all_positions)
        passed_count = 0
        failed_positions = []
        
        # 타입별로 그룹화하여 검증
        for emp_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
            print(f"\n📌 {emp_type} 검증")
            print("-" * 60)
            
            type_positions = [p for p in all_positions if p[0] == emp_type]
            
            for type_name, position, expected_conditions in type_positions:
                verification = self.verify_condition_display(
                    type_name, position, expected_conditions
                )
                self.verification_results.append(verification)
                
                # 결과 출력
                status = "✅" if verification['match'] else "❌"
                print(f"\n  {status} {position:30}")
                print(f"     예상 조건: {expected_conditions}")
                print(f"     실제 조건: {verification['actual_conditions']}")
                
                if verification['match']:
                    passed_count += 1
                    
                    # 조건별 충족 상태
                    print(f"     조건 충족 상태:")
                    for cond_id, passed in verification['condition_results'].items():
                        cond_status = "✓" if passed else "✗"
                        cond_name = self.matrix['conditions'][str(cond_id)]['description']
                        print(f"       {cond_status} 조건 {cond_id}: {cond_name}")
                    
                    # 3개월 연속 체크 로직 검증
                    if '3month_check' in verification:
                        print(f"     📊 3개월 연속 체크 로직:")
                        for cond_key, check_info in verification['3month_check'].items():
                            print(f"       - {check_info['name']}: ", end="")
                            if 'expected_result' in check_info:
                                match = check_info['result'] == check_info['expected_result']
                                status = "✓" if match else "✗"
                                print(f"{status} (예상: {check_info['expected_result']}, 실제: {check_info['result']})")
                            else:
                                print(f"{'✓' if check_info['result'] else '✗'}")
                else:
                    failed_positions.append(f"{type_name} - {position}")
                    print(f"     ⚠️ 조건 불일치!")
        
        # 최종 결과 요약
        print("\n" + "=" * 80)
        print("📊 검증 결과 요약")
        print("=" * 80)
        print(f"  총 검증 대상: {total_positions}개 직급")
        print(f"  성공: {passed_count}개")
        print(f"  실패: {total_positions - passed_count}개")
        
        if failed_positions:
            print(f"\n  ❌ 실패한 직급:")
            for pos in failed_positions:
                print(f"     - {pos}")
        else:
            print(f"\n  ✅ 모든 직급이 올바르게 구성되었습니다!")
        
        # 특별 검증: 핵심 직급들
        self._verify_critical_positions()
    
    def _verify_critical_positions(self) -> None:
        """핵심 직급 특별 검증"""
        print("\n" + "=" * 80)
        print("🎯 핵심 직급 특별 검증")
        print("=" * 80)
        
        critical_checks = [
            {
                'type': 'TYPE-1',
                'position': 'LINE LEADER',
                'expected_conditions': [1, 2, 3, 4, 7],
                'special_check': '조건 7 (팀/구역 AQL) 포함 여부'
            },
            {
                'type': 'TYPE-1',
                'position': 'AQL INSPECTOR',
                'expected_conditions': [1, 2, 3, 4, 5],
                'special_check': '조건 5 (당월 AQL) 포함, 조건 6 제외'
            },
            {
                'type': 'TYPE-1',
                'position': 'ASSEMBLY INSPECTOR',
                'expected_conditions': [1, 2, 3, 4, 5, 6, 9, 10],
                'special_check': '5PRS 조건 (9, 10) 포함 여부'
            },
            {
                'type': 'TYPE-2',
                'position': 'LINE LEADER',
                'expected_conditions': [1, 2, 3, 4],
                'special_check': '조건 7 제외 (TYPE-1과 다름)'
            }
        ]
        
        for check in critical_checks:
            result = next(
                (r for r in self.verification_results 
                 if r['type'] == check['type'] and r['position'] == check['position']),
                None
            )
            
            if result:
                status = "✅" if result['match'] else "❌"
                print(f"\n  {status} {check['type']} - {check['position']}")
                print(f"     특별 체크: {check['special_check']}")
                print(f"     예상: {check['expected_conditions']}")
                print(f"     실제: {result['actual_conditions']}")
                
                # 특정 조건 확인
                if check['position'] == 'LINE LEADER' and check['type'] == 'TYPE-1':
                    if 7 in result['actual_conditions']:
                        print(f"     ✅ 조건 7이 올바르게 포함됨")
                        if '3month_check' in result and 'condition_7' in result['3month_check']:
                            cond7 = result['3month_check']['condition_7']
                            print(f"     ✅ 부하직원 연속 실패 체크 로직 작동 중")
                            print(f"        - 테스트 결과: {cond7.get('result')}")
                            print(f"        - 실패 부하직원 있음: {cond7.get('has_failing_subordinate')}")
                    else:
                        print(f"     ❌ 조건 7이 누락됨!")
    
    def export_verification_report(self) -> None:
        """검증 보고서 출력"""
        report_path = Path(__file__).parent / f'ui_verification_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_positions': len(self.verification_results),
                'passed': sum(1 for r in self.verification_results if r['match']),
                'failed': sum(1 for r in self.verification_results if not r['match'])
            },
            'details': self.verification_results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 검증 보고서 저장됨: {report_path}")

def main():
    """메인 실행 함수"""
    verifier = UIConfigurationVerifier()
    
    # 전체 검증 실행
    verifier.run_full_verification()
    
    # 보고서 출력
    verifier.export_verification_report()
    
    print("\n" + "=" * 80)
    print("✅ UI 구성 검증 완료!")
    print("=" * 80)

if __name__ == "__main__":
    main()