#!/usr/bin/env python3
"""
Test script to verify employeeData format issue
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from dashboard_v2.modules.incentive_calculator import IncentiveCalculator

# 데이터 로드 및 확인
calculator = IncentiveCalculator('september', 2025)
data = calculator.process_all_data()

print("=" * 60)
print("Employee Data Format Test")
print("=" * 60)

# employees 데이터 타입 확인
print(f"1. employees 타입: {type(data['employees'])}")
print(f"2. employees 길이: {len(data['employees'])}")

if isinstance(data['employees'], list) and len(data['employees']) > 0:
    first_employee = data['employees'][0]
    print(f"3. 첫 번째 직원 데이터 타입: {type(first_employee)}")
    print(f"4. 첫 번째 직원 필드들:")
    for key in list(first_employee.keys())[:10]:
        print(f"   - {key}: {type(first_employee[key])}")

    # type 필드 확인
    if 'type' in first_employee:
        print(f"\n5. type 필드 확인:")
        print(f"   - 값: {first_employee['type']}")
        print(f"   - 타입: {type(first_employee['type'])}")
    else:
        print("\n5. ⚠️ 'type' 필드가 없습니다!")
        # 가능한 type 관련 필드 찾기
        type_fields = [k for k in first_employee.keys() if 'type' in k.lower() or 'role' in k.lower()]
        print(f"   가능한 필드들: {type_fields}")

# Type별 집계 테스트
type_counts = {}
for emp in data['employees']:
    # type 필드 확인 - 여러 가능한 필드명 시도
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD') or emp.get('Type') or 'UNKNOWN'
    if emp_type not in type_counts:
        type_counts[emp_type] = 0
    type_counts[emp_type] += 1

print(f"\n6. Type별 집계:")
for type_name, count in type_counts.items():
    print(f"   - {type_name}: {count}명")

print("\n✅ 테스트 완료")
print("=" * 60)