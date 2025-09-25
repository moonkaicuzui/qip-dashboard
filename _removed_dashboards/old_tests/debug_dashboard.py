import pandas as pd
import sys
import os
sys.path.append('/Users/ksmoon/Downloads/대시보드 인센티브 테스트11')

from integrated_dashboard_final import load_incentive_data, load_condition_matrix, evaluate_conditions

# 데이터 로드
df = load_incentive_data('august', 2025)
condition_matrix = load_condition_matrix()

# 622030022 직원 데이터 찾기
emp_row = df[df['emp_no'] == '622030022']

if not emp_row.empty:
    emp_data = emp_row.iloc[0].to_dict()
    print(f"Employee: {emp_data.get('name')} ({emp_data.get('emp_no')})")
    print(f"Position: {emp_data.get('position')}")
    print(f"Type: {emp_data.get('type')}")

    # CSV에서 조건 7 관련 필드 확인
    print(f"\nCSV fields for condition 7:")
    print(f"  cond_7_aql_team_area: {emp_data.get('cond_7_aql_team_area')}")
    print(f"  cond_7_value: {emp_data.get('cond_7_value')}")
    print(f"  cond_7_threshold: {emp_data.get('cond_7_threshold')}")

    # evaluate_conditions 실행
    condition_results = evaluate_conditions(emp_data, condition_matrix)

    print(f"\nCondition evaluation results:")
    for cond in condition_results:
        if cond['id'] == 7:
            print(f"  Condition 7:")
            print(f"    name: {cond['name']}")
            print(f"    is_met: {cond['is_met']}")
            print(f"    actual: {cond['actual']}")
            print(f"    is_na: {cond['is_na']}")

    # emp_data의 모든 키 확인
    print(f"\nAll condition-related fields in emp_data:")
    for key in sorted(emp_data.keys()):
        if 'cond' in key.lower():
            print(f"  {key}: {emp_data[key]}")
else:
    print("Employee 622030022 not found")