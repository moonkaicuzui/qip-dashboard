#!/usr/bin/env python3
"""
TYPE-1 관리자 필터링 검증 스크립트
"""
import json
import re

def extract_employee_data(html_path):
    """HTML에서 직원 데이터 추출"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'const employeeData = (\[[\s\S]*?\]);'
    match = re.search(pattern, content)

    if match:
        data_str = match.group(1)
        data_str = re.sub(r'\bNaN\b', 'null', data_str)
        return json.loads(data_str)
    return []

def verify_type1_filtering(employees):
    """TYPE-1 필터링 검증"""

    # Special positions that should be excluded
    special_positions = [
        'AQL INSPECTOR',
        'AUDIT & TRAINING TEAM',
        'MODEL MASTER'
    ]

    # Manager positions that should be included
    manager_positions = [
        'MANAGER',
        'SUPERVISOR',
        'GROUP LEADER',
        'LINE LEADER',
        'A.MANAGER',
        'ASSISTANT MANAGER'
    ]

    type1_employees = [emp for emp in employees if emp.get('type') == 'TYPE-1']

    print("=" * 80)
    print("TYPE-1 필터링 검증 결과")
    print("=" * 80)
    print(f"\n전체 직원: {len(employees)}명")
    print(f"TYPE-1 직원: {len(type1_employees)}명")

    # Check special positions (should be excluded)
    excluded_count = 0
    included_special = []

    for emp in type1_employees:
        position = (emp.get('position') or '').upper()
        for special in special_positions:
            if special in position:
                included_special.append(f"  - {emp['name']} ({emp['position']})")
                excluded_count += 1

    if included_special:
        print(f"\n⚠️ 제외되어야 하는데 포함된 직원 ({len(included_special)}명):")
        for item in included_special[:5]:
            print(item)
    else:
        print("\n✅ 특수 직급(AQL, AUDIT, MODEL MASTER)이 모두 제외됨")

    # Check manager positions (should be included)
    manager_count = 0
    managers = []

    for emp in type1_employees:
        position = (emp.get('position') or '').upper()
        is_manager = False

        for manager_pos in ['MANAGER', 'SUPERVISOR', 'GROUP LEADER', 'LINE LEADER']:
            if manager_pos in position:
                is_manager = True
                manager_count += 1
                managers.append(f"  - {emp['name']} ({emp['position']})")
                break

    print(f"\n✅ 포함된 관리자 직급: {manager_count}명")
    if managers:
        print("예시 (처음 5명):")
        for item in managers[:5]:
            print(item)

    # Check if filtering logic would work in JavaScript
    print("\n" + "=" * 80)
    print("JavaScript 필터링 시뮬레이션")
    print("=" * 80)

    # Simulate the JavaScript filtering logic
    filtered_for_org = []

    for emp in employees:
        # Check TYPE-1
        if emp.get('type') != 'TYPE-1':
            continue

        position = (emp.get('position') or '').upper()

        # Check for special positions (should be excluded)
        is_special = False
        if 'AQL' in position and 'INSPECTOR' in position:
            is_special = True
        elif 'AUDIT' in position or 'TRAINING' in position:
            is_special = True
        elif 'MODEL' in position and 'MASTER' in position:
            is_special = True

        if is_special:
            continue

        # Check for manager positions
        is_manager = ('MANAGER' in position or
                     'SUPERVISOR' in position or
                     'GROUP LEADER' in position or
                     'LINE LEADER' in position)

        if is_manager:
            filtered_for_org.append(emp)

    print(f"필터링 후 조직도에 표시될 직원: {len(filtered_for_org)}명")

    # Show breakdown
    position_counts = {}
    for emp in filtered_for_org:
        pos = emp.get('position', 'Unknown')
        position_counts[pos] = position_counts.get(pos, 0) + 1

    print("\n직급별 분포:")
    for pos, count in sorted(position_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {pos}: {count}명")

if __name__ == "__main__":
    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_08_Version_5.html"

    print("직원 데이터 추출 중...")
    employees = extract_employee_data(html_path)

    if employees:
        verify_type1_filtering(employees)
    else:
        print("데이터를 찾을 수 없습니다.")