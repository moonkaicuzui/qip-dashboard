#!/usr/bin/env python3
"""
출근율 데이터 검증 스크립트
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
if not match:
    print("❌ Base64 데이터를 찾을 수 없습니다!")
    exit(1)

base64_data = match.group(1).strip()

# Decode
json_str = base64.b64decode(base64_data).decode('utf-8')
employee_data = json.loads(json_str)

print(f"📊 출근율 데이터 검증")
print(f"=" * 80)
print(f"\n전체 직원 수: {len(employee_data)}")

# Check attendance rate fields
print(f"\n📋 첫 10명의 출근율 관련 필드:")
for i, emp in enumerate(employee_data[:10], 1):
    emp_no = emp.get('Employee No', 'N/A')
    name = emp.get('Full Name', 'N/A')[:20]

    # 모든 출근율 관련 필드 확인
    attendance_fields = {}
    for key in emp.keys():
        if 'attendance' in key.lower() and 'rate' in key.lower():
            attendance_fields[key] = emp[key]

    print(f"\n{i}. {emp_no} | {name:20s}")
    if attendance_fields:
        for field, value in attendance_fields.items():
            print(f"   {field}: {value}")
    else:
        print(f"   ⚠️  출근율 필드 없음!")

# Check below 88% employees
print(f"\n" + "=" * 80)
print(f"📊 출근율 < 88% 직원 분석")
print(f"=" * 80)

below_88_count = 0
type3_count = 0
no_data_count = 0

for emp in employee_data:
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD')

    # 모든 가능한 출근율 필드 확인
    attendance_rate = None
    for field in ['Attendance Rate', 'attendance_rate', 'cond_1_attendance_rate']:
        if field in emp:
            try:
                attendance_rate = float(emp[field])
                break
            except:
                pass

    if attendance_rate is None:
        no_data_count += 1
        continue

    if attendance_rate < 88:
        below_88_count += 1
        if emp_type == 'TYPE-3':
            type3_count += 1

print(f"\n출근율 < 88% 전체: {below_88_count}명")
print(f"  TYPE-3: {type3_count}명")
print(f"  TYPE-1/2: {below_88_count - type3_count}명")
print(f"  출근율 데이터 없음: {no_data_count}명")

# Sample of below 88% employees
print(f"\n📋 출근율 < 88% 직원 샘플 (처음 5명):")
count = 0
for emp in employee_data:
    attendance_rate = None
    field_name = None
    for field in ['Attendance Rate', 'attendance_rate', 'cond_1_attendance_rate']:
        if field in emp:
            try:
                attendance_rate = float(emp[field])
                field_name = field
                break
            except:
                pass

    if attendance_rate and attendance_rate < 88:
        count += 1
        emp_no = emp.get('Employee No', 'N/A')
        name = emp.get('Full Name', 'N/A')[:25]
        emp_type = emp.get('type') or emp.get('ROLE TYPE STD', 'N/A')

        print(f"  {count}. {str(emp_no):12s} | {name:25s} | {str(emp_type):7s} | {field_name}: {attendance_rate:.1f}%")

        if count >= 5:
            break

print(f"\n" + "=" * 80)
