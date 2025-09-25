#!/usr/bin/env python3
"""
직속상사가 TYPE-1이지만 본인은 TYPE-1이 아닌 직원 필터링 분석
"""
import json
import re
from collections import defaultdict

def extract_employee_data(html_path):
    """HTML 파일에서 직원 데이터 추출"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # employeeData 추출
    pattern = r'const employeeData = (\[[\s\S]*?\]);'
    match = re.search(pattern, content)

    if match:
        data_str = match.group(1)
        # NaN을 null로 변환
        data_str = re.sub(r'\bNaN\b', 'null', data_str)
        return json.loads(data_str)
    return []

def analyze_type1_boss_filtering(employees):
    """TYPE-1 보스 필터링 분석"""

    # 통계 초기화
    stats = {
        'total_employees': len(employees),
        'bottom_inspector': 0,
        'new_position': 0,
        'type1_employees': 0,
        'type2_employees': 0,
        'type3_employees': 0,
        'type1_with_type1_boss': 0,
        'non_type1_with_type1_boss': 0,
        'affected_subordinates': 0,
        'excluded_employees': [],
        'broken_chains': []
    }

    # 직원 매핑 생성
    employee_map = {emp['emp_no']: emp for emp in employees}

    # TYPE-1 직원 ID 수집
    type1_ids = set()

    for emp in employees:
        position = (emp.get('position', '') or '').upper()
        emp_type = emp.get('type', '')

        # 통계 수집
        if 'BOTTOM' in position:
            stats['bottom_inspector'] += 1
        if position == 'NEW':
            stats['new_position'] += 1

        if emp_type == 'TYPE-1':
            stats['type1_employees'] += 1
            type1_ids.add(emp['emp_no'])
        elif emp_type == 'TYPE-2':
            stats['type2_employees'] += 1
        elif emp_type == 'TYPE-3':
            stats['type3_employees'] += 1

    # TYPE-1 보스를 가진 직원 분석
    for emp in employees:
        boss_id = emp.get('boss_id', '')
        emp_type = emp.get('type', '')
        position = (emp.get('position', '') or '').upper()

        # BOTTOM INSPECTOR와 NEW는 이미 제외되므로 스킵
        if 'BOTTOM' in position or position == 'NEW':
            continue

        if boss_id and boss_id in type1_ids:
            if emp_type == 'TYPE-1':
                stats['type1_with_type1_boss'] += 1
            else:
                # TYPE-1 보스를 가진 비-TYPE-1 직원
                stats['non_type1_with_type1_boss'] += 1
                stats['excluded_employees'].append({
                    'emp_no': emp['emp_no'],
                    'name': emp['name'],
                    'position': emp['position'],
                    'type': emp_type,
                    'boss_name': employee_map.get(boss_id, {}).get('name', 'Unknown'),
                    'boss_position': employee_map.get(boss_id, {}).get('position', 'Unknown'),
                    'incentive': emp.get('august_incentive', 0)
                })

    # 제외될 직원들의 부하직원 수 계산
    excluded_ids = {e['emp_no'] for e in stats['excluded_employees']}

    for emp in employees:
        boss_id = emp.get('boss_id', '')
        position = (emp.get('position', '') or '').upper()

        # BOTTOM INSPECTOR와 NEW는 이미 제외되므로 스킵
        if 'BOTTOM' in position or position == 'NEW':
            continue

        if boss_id in excluded_ids:
            stats['affected_subordinates'] += 1
            stats['broken_chains'].append({
                'emp_no': emp['emp_no'],
                'name': emp['name'],
                'position': emp['position'],
                'disconnected_from': employee_map.get(boss_id, {}).get('name', 'Unknown')
            })

    return stats

def print_analysis_report(stats):
    """분석 결과 출력"""
    print("\n" + "="*80)
    print("TYPE-1 보스 필터링 영향 분석 보고서")
    print("="*80)

    print("\n### 현재 상태 (BOTTOM INSPECTOR, NEW 제외 후)")
    print(f"- 전체 직원 수: {stats['total_employees']}명")
    print(f"- BOTTOM INSPECTOR: {stats['bottom_inspector']}명 (이미 제외)")
    print(f"- NEW: {stats['new_position']}명 (이미 제외)")
    print(f"- TYPE-1 직원: {stats['type1_employees']}명")
    print(f"- TYPE-2 직원: {stats['type2_employees']}명")
    print(f"- TYPE-3 직원: {stats['type3_employees']}명")

    print("\n### TYPE-1 보스 관계 분석")
    print(f"- TYPE-1 보스를 가진 TYPE-1 직원: {stats['type1_with_type1_boss']}명 (유지)")
    print(f"- TYPE-1 보스를 가진 비-TYPE-1 직원: {stats['non_type1_with_type1_boss']}명 (제외 대상)")

    print("\n### 제외될 직원 상세 (TYPE-1 보스를 가진 비-TYPE-1)")
    if stats['excluded_employees']:
        for i, emp in enumerate(stats['excluded_employees'][:10], 1):  # 처음 10명만 표시
            print(f"{i}. {emp['name']} ({emp['position']}, {emp['type']})")
            print(f"   보스: {emp['boss_name']} ({emp['boss_position']})")
            print(f"   인센티브: {emp['incentive']} VND")

        if len(stats['excluded_employees']) > 10:
            print(f"   ... 외 {len(stats['excluded_employees'])-10}명")
    else:
        print("   해당 없음")

    print("\n### 영향받는 부하직원 (조직도 단절)")
    print(f"- 제외될 직원의 부하직원 수: {stats['affected_subordinates']}명")
    if stats['broken_chains']:
        for i, emp in enumerate(stats['broken_chains'][:5], 1):  # 처음 5명만 표시
            print(f"   {i}. {emp['name']} ({emp['position']}) - {emp['disconnected_from']}과 단절")

        if len(stats['broken_chains']) > 5:
            print(f"   ... 외 {len(stats['broken_chains'])-5}명")

    print("\n### 영향 요약")
    total_affected = len(stats['excluded_employees']) + stats['affected_subordinates']
    org_chart_size = stats['total_employees'] - stats['bottom_inspector'] - stats['new_position']
    impact_rate = (total_affected / org_chart_size * 100) if org_chart_size > 0 else 0

    print(f"- 직접 제외: {len(stats['excluded_employees'])}명")
    print(f"- 간접 영향: {stats['affected_subordinates']}명")
    print(f"- 총 영향: {total_affected}명 (조직도의 {impact_rate:.1f}%)")

    print("\n### 권장사항")
    if stats['non_type1_with_type1_boss'] > 20:
        print("⚠️  많은 수의 중간관리자가 제외됩니다.")
        print("    - 조직도의 연속성이 크게 손상될 수 있습니다.")
        print("    - TYPE-1 중심 조직도는 인센티브 계산에는 유용하나,")
        print("    - 전체 조직 구조 파악이 어려워집니다.")

    if stats['affected_subordinates'] > 30:
        print("⚠️  많은 부하직원들이 상위 조직과 단절됩니다.")
        print("    - 대안: TYPE 표시를 강조하되 전체 구조는 유지")
        print("    - 또는: TYPE-1 전용 뷰와 전체 뷰를 분리 제공")

    # 인센티브 받는 직원 중 제외되는 비율 체크
    incentive_excluded = sum(1 for emp in stats['excluded_employees']
                            if float(str(emp['incentive']).replace('', '')) > 0)
    if incentive_excluded > 0:
        print(f"⚠️  {incentive_excluded}명의 인센티브 수령자가 조직도에서 제외됩니다.")

if __name__ == "__main__":
    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    print("직원 데이터 추출 중...")
    employees = extract_employee_data(html_path)

    if employees:
        print(f"총 {len(employees)}명의 직원 데이터 분석 중...")
        stats = analyze_type1_boss_filtering(employees)
        print_analysis_report(stats)
    else:
        print("직원 데이터를 찾을 수 없습니다.")