#!/usr/bin/env python3
"""
TYPE-2 직원이 TYPE-1 인센티브 계산에 미치는 영향 검증
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

def analyze_type1_calculations(employees):
    """TYPE-1 인센티브 계산 분석"""

    # 직원 매핑
    emp_map = {emp['emp_no']: emp for emp in employees}

    # TYPE-1 LINE LEADER 찾기
    type1_line_leaders = []
    for emp in employees:
        if (emp.get('type') == 'TYPE-1' and
            'LINE' in emp.get('position', '').upper() and
            'LEADER' in emp.get('position', '').upper()):
            type1_line_leaders.append(emp)

    print("="*80)
    print("TYPE-1 LINE LEADER 인센티브 계산 분석")
    print("="*80)

    for leader in type1_line_leaders[:3]:  # 처음 3명만 분석
        print(f"\n### {leader['name']} ({leader['position']})")
        print(f"    인센티브: {leader.get('august_incentive', 0)} VND")

        # 부하직원 찾기
        subordinates = []
        for emp in employees:
            if emp.get('boss_id') == leader['emp_no']:
                subordinates.append(emp)

        if subordinates:
            print(f"    부하직원 총 {len(subordinates)}명:")

            # TYPE별로 분류
            type1_subs = [s for s in subordinates if s.get('type') == 'TYPE-1']
            type2_subs = [s for s in subordinates if s.get('type') == 'TYPE-2']
            type3_subs = [s for s in subordinates if s.get('type') == 'TYPE-3']

            # TYPE-1 부하직원 인센티브
            type1_total = sum(float(s.get('august_incentive', 0) or 0) for s in type1_subs)
            type2_total = sum(float(s.get('august_incentive', 0) or 0) for s in type2_subs)

            print(f"      - TYPE-1: {len(type1_subs)}명 (인센티브 합: {type1_total:,.0f} VND)")
            if type1_subs:
                for sub in type1_subs[:2]:  # 처음 2명만 표시
                    print(f"        • {sub['name']}: {sub.get('august_incentive', 0)} VND")

            print(f"      - TYPE-2: {len(type2_subs)}명 (인센티브 합: {type2_total:,.0f} VND)")
            if type2_subs:
                for sub in type2_subs[:2]:  # 처음 2명만 표시
                    print(f"        • {sub['name']}: {sub.get('august_incentive', 0)} VND")

            print(f"      - TYPE-3: {len(type3_subs)}명")

            # 계산 검증
            if type1_subs and type1_total > 0:
                receiving_count = sum(1 for s in type1_subs if float(s.get('august_incentive', 0) or 0) > 0)
                receiving_ratio = receiving_count / len(type1_subs) if type1_subs else 0
                expected = type1_total * 0.12 * receiving_ratio
                print(f"\n    💡 예상 계산:")
                print(f"       TYPE-1 부하 인센티브 합: {type1_total:,.0f}")
                print(f"       수령 비율: {receiving_count}/{len(type1_subs)} = {receiving_ratio:.2%}")
                print(f"       예상 인센티브: {type1_total:,.0f} × 12% × {receiving_ratio:.2%} = {expected:,.0f} VND")
                print(f"       실제 인센티브: {leader.get('august_incentive', 0)} VND")

                if type2_total > 0:
                    print(f"\n    ⚠️ TYPE-2 부하직원 인센티브 {type2_total:,.0f} VND는 계산에 포함되지 않음")

    print("\n" + "="*80)
    print("GROUP LEADER 계산 분석")
    print("="*80)

    # GROUP LEADER 찾기
    type1_group_leaders = []
    for emp in employees:
        if (emp.get('type') == 'TYPE-1' and
            'GROUP' in emp.get('position', '').upper() and
            'LEADER' in emp.get('position', '').upper()):
            type1_group_leaders.append(emp)

    for leader in type1_group_leaders[:2]:  # 처음 2명만
        print(f"\n### {leader['name']} ({leader['position']})")
        print(f"    인센티브: {leader.get('august_incentive', 0)} VND")

        # 팀 내 LINE LEADER 찾기
        team_line_leaders = []

        # 직접 부하 중 LINE LEADER
        for emp in employees:
            if (emp.get('boss_id') == leader['emp_no'] and
                emp.get('type') == 'TYPE-1' and
                'LINE' in emp.get('position', '').upper() and
                'LEADER' in emp.get('position', '').upper()):
                team_line_leaders.append(emp)

        if team_line_leaders:
            line_leader_incentives = [float(ll.get('august_incentive', 0) or 0) for ll in team_line_leaders]
            receiving_ll = [i for i in line_leader_incentives if i > 0]

            if receiving_ll:
                avg = sum(receiving_ll) / len(receiving_ll)
                expected = avg * 2

                print(f"    팀 내 TYPE-1 LINE LEADER: {len(team_line_leaders)}명")
                for ll in team_line_leaders[:2]:
                    print(f"      • {ll['name']}: {ll.get('august_incentive', 0)} VND")

                print(f"\n    💡 예상 계산:")
                print(f"       LINE LEADER 평균: {avg:,.0f} VND")
                print(f"       예상 인센티브: {avg:,.0f} × 2 = {expected:,.0f} VND")
                print(f"       실제 인센티브: {leader.get('august_incentive', 0)} VND")

if __name__ == "__main__":
    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    print("직원 데이터 추출 중...")
    employees = extract_employee_data(html_path)

    if employees:
        print(f"총 {len(employees)}명 데이터 분석...")
        analyze_type1_calculations(employees)
    else:
        print("데이터를 찾을 수 없습니다.")