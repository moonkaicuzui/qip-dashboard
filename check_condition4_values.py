#!/usr/bin/env python3
"""
Check actual condition4 field values in dashboard data
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

print(f"Total employees: {len(employee_data)}")

# Check condition4 values
condition4_values = {}
for emp in employee_data:
    val = emp.get('condition4')
    val_repr = repr(val)
    condition4_values[val_repr] = condition4_values.get(val_repr, 0) + 1

print(f"\ncondition4 field value distribution:")
for val, count in sorted(condition4_values.items()):
    print(f"  {val}: {count}")

# Check attendancy condition 4 field
attendance_cond4_values = {}
for emp in employee_data:
    val = emp.get('attendancy condition 4 - minimum working days')
    val_repr = repr(val)
    attendance_cond4_values[val_repr] = attendance_cond4_values.get(val_repr, 0) + 1

print(f"\nattendancy condition 4 - minimum working days field value distribution:")
for val, count in sorted(attendance_cond4_values.items()):
    print(f"  {val}: {count}")

# Show employees where actual < 12 but condition4 = 'no'
print(f"\n🔍 Employees with actual < 12 but condition4 = 'no':")
count = 0
for emp in employee_data:
    actual_days = emp.get('Actual Working Days')
    cond4 = emp.get('condition4') or emp.get('attendancy condition 4 - minimum working days')

    if actual_days is not None and float(actual_days) < 12 and cond4 == 'no':
        count += 1
        if count <= 5:
            print(f"  Employee {emp.get('Employee No')}: actual={actual_days}, condition4={cond4}")

print(f"  Total: {count} employees")

# Check if condition4 field even exists or is always None
has_condition4 = sum(1 for emp in employee_data if 'condition4' in emp)
has_attendance_cond4 = sum(1 for emp in employee_data if 'attendancy condition 4 - minimum working days' in emp)

print(f"\nField presence:")
print(f"  'condition4' field exists: {has_condition4}/{len(employee_data)}")
print(f"  'attendancy condition 4 - minimum working days' field exists: {has_attendance_cond4}/{len(employee_data)}")
