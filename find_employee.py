import json
import re

# HTML 파일 읽기
with open('output_files/Incentive_Dashboard_2025_08_Version_5.html', 'r', encoding='utf-8') as f:
    content = f.read()

# employeeData 배열 찾기
pattern = r'const employeeData = (\[.*?\]);'
match = re.search(pattern, content, re.DOTALL)

if match:
    data_str = match.group(1)
    # JSON 파싱
    employees = json.loads(data_str)

    # 622030022 직원 찾기
    for emp in employees:
        if emp.get('emp_no') == '622030022':
            print(f"Found employee: {emp['name']}")
            print(f"Position: {emp['position']}")
            print(f"Type: {emp['type']}")
            print(f"August incentive: {emp['august_incentive']}")
            print(f"\nCondition results:")
            for cond in emp.get('condition_results', []):
                if cond['id'] == 7:
                    print(f"  Condition 7 (팀/구역 AQL):")
                    print(f"    is_met: {cond['is_met']}")
                    print(f"    actual: {cond['actual']}")
                    print(f"    is_na: {cond['is_na']}")
            break
    else:
        print("Employee 622030022 not found in dashboard")
else:
    print("Could not find employeeData in HTML")