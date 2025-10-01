#!/usr/bin/env python3
"""
Verify exact modal count and TYPE distribution
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

print("📊 Modal Filtering Simulation (Exact JavaScript Logic):")
print("=" * 70)

# Simulate exact modal logic
minimumRequired = 12
notMetEmployees = []

for emp in employee_data:
    # TYPE-3 제외 (인센티브 대상 아님)
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD')
    if emp_type == 'TYPE-3':
        continue  # Skip TYPE-3 employees

    # Method 1: Minimum_Days_Met field
    minimumDaysMet = emp.get('Minimum_Days_Met')
    if minimumDaysMet is not None and minimumDaysMet != '':
        if minimumDaysMet is False or minimumDaysMet == 'False' or minimumDaysMet == 0:
            notMetEmployees.append(emp)
        continue  # Skip to next employee

    # Method 2: condition4 field - Single Source of Truth
    condition4 = emp.get('condition4')
    if condition4 is not None and condition4 != '':
        if condition4 == 'yes':
            notMetEmployees.append(emp)
        # condition4 필드가 있으면 그 값을 신뢰하고 Method 3로 넘어가지 않음
        continue

    # Method 3: Fallback - actual calculation
    actualDays = emp.get('Actual Working Days') or emp.get('actual_working_days')
    if actualDays is not None:
        try:
            if float(actualDays) < minimumRequired:
                notMetEmployees.append(emp)
        except:
            pass

print(f"\nModal would show: {len(notMetEmployees)} employees")

# Analyze TYPE distribution
type_counts = {}
for emp in notMetEmployees:
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD', 'Unknown')
    type_counts[emp_type] = type_counts.get(emp_type, 0) + 1

print(f"\nTYPE Distribution in modal:")
for emp_type, count in sorted(type_counts.items()):
    print(f"  {emp_type}: {count}")

# Show first 10 employees
print(f"\nFirst 10 employees that would appear in modal:")
for i, emp in enumerate(notMetEmployees[:10], 1):
    emp_no = emp.get('Employee No')
    name = emp.get('Full Name') or emp.get('Full Name English') or 'N/A'
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD')
    actual_days = emp.get('Actual Working Days')
    print(f"  {i}. {emp_no} | {name[:20]:20s} | {emp_type:7s} | {actual_days} days")

# Check attendancy condition 4 field for these employees
print(f"\nChecking 'attendancy condition 4' field for first 10:")
for i, emp in enumerate(notMetEmployees[:10], 1):
    emp_no = emp.get('Employee No')
    cond4_attendance = emp.get('attendancy condition 4 - minimum working days')
    cond4 = emp.get('condition4')
    print(f"  {i}. {emp_no} | attendancy cond4: {cond4_attendance:3s} | condition4: {cond4}")

# Double-check: how many have 'attendancy condition 4' = 'yes'?
attendance_yes_count = sum(1 for emp in notMetEmployees if emp.get('attendancy condition 4 - minimum working days') == 'yes')
attendance_no_count = sum(1 for emp in notMetEmployees if emp.get('attendancy condition 4 - minimum working days') == 'no')

print(f"\n'attendancy condition 4 - minimum working days' field in modal results:")
print(f"  'yes': {attendance_yes_count}")
print(f"  'no': {attendance_no_count}")
print(f"  Total: {attendance_yes_count + attendance_no_count}")

# Summary
print(f"\n{'='*70}")
print(f"SUMMARY:")
print(f"  KPI Card shows: 16 (only 'attendancy condition 4' = 'yes')")
print(f"  Modal should show: {len(notMetEmployees)} (Method 3 fallback → actual < 12)")
print(f"  User reported: 50+ people")
print(f"  Discrepancy: Modal logic falls through to Method 3 because")
print(f"               'condition4' field doesn't exist (is None/undefined)")
print(f"{'='*70}")
