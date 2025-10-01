#!/usr/bin/env python3
"""
ATTENDANCE < 88% 검증
"""
import re
import base64
import json

# Read the dashboard HTML
html_path = 'output_files/Incentive_Dashboard_2025_09_Version_6.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract Base64 data
pattern = r'<script type="application/json" id="employeeDataBase64">\s*([^<]+)\s*</script>'
match = re.search(pattern, html_content, re.DOTALL)
base64_data = match.group(1).strip()

# Decode
json_str = base64.b64decode(base64_data).decode('utf-8')
employee_data = json.loads(json_str)

print(f"📊 ATTENDANCE < 88% 검증")
print(f"=" * 70)

# Count employees with attendance < 88%
below_88_count = 0
below_88_type1 = 0
below_88_type2 = 0
below_88_type3 = 0

for emp in employee_data:
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD')
    attendance_rate = emp.get('Attendance Rate') or emp.get('attendance_rate')

    if attendance_rate is not None:
        try:
            rate = float(attendance_rate)
            if rate < 88:
                below_88_count += 1
                if emp_type == 'TYPE-1':
                    below_88_type1 += 1
                elif emp_type == 'TYPE-2':
                    below_88_type2 += 1
                elif emp_type == 'TYPE-3':
                    below_88_type3 += 1
        except:
            pass

print(f"\n전체 직원 중 출근율 < 88%: {below_88_count}명")
print(f"  TYPE-1: {below_88_type1}명")
print(f"  TYPE-2: {below_88_type2}명")
print(f"  TYPE-3: {below_88_type3}명")

# TYPE-3 제외한 카운트
below_88_without_type3 = below_88_type1 + below_88_type2
print(f"\nTYPE-3 제외 (인센티브 대상만): {below_88_without_type3}명")

# Show first 10 employees
print(f"\n출근율 < 88% 직원 상위 10명:")
count = 0
for emp in employee_data:
    attendance_rate = emp.get('Attendance Rate') or emp.get('attendance_rate')
    if attendance_rate is not None:
        try:
            rate = float(attendance_rate)
            if rate < 88:
                count += 1
                emp_no = emp.get('Employee No')
                name = emp.get('Full Name') or emp.get('Full Name English') or 'N/A'
                emp_type = emp.get('type') or emp.get('ROLE TYPE STD')
                print(f"  {count}. {emp_no} | {name[:20]:20s} | {emp_type:7s} | {rate:.2f}%")
                if count >= 10:
                    break
        except:
            pass

print(f"\n{'='*70}")
print(f"예상 KPI 값:")
print(f"  전체: {below_88_count}명")
print(f"  TYPE-3 제외: {below_88_without_type3}명 (인센티브 대상만)")
print(f"{'='*70}")
