#!/usr/bin/env python3
"""
Extract and analyze employeeData from dashboard HTML
"""
import re
import base64
import json
import pandas as pd

# Read the dashboard HTML
html_path = 'output_files/Incentive_Dashboard_2025_09_Version_6.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract Base64 encoded employee data from <script> tag
pattern = r'<script type="application/json" id="employeeDataBase64">\s*([^<]+)\s*</script>'
match = re.search(pattern, html_content, re.DOTALL)

if not match:
    print("❌ Could not find employeeDataBase64 script tag in HTML")
    exit(1)

base64_data = match.group(1).strip()
print(f"✅ Found Base64 data: {len(base64_data)} characters")

# Decode Base64 to JSON
try:
    json_str = base64.b64decode(base64_data).decode('utf-8')
    employee_data = json.loads(json_str)
except Exception as e:
    print(f"❌ Error decoding data: {e}")
    # Try direct JSON parse (in case it's not Base64)
    try:
        employee_data = json.loads(base64_data)
        print("✅ Data was plain JSON, not Base64")
    except:
        exit(1)

print(f"\n📊 Dashboard Employee Data Analysis:")
print(f"   Total employees in dashboard: {len(employee_data)}")

# Analyze TYPE distribution
type_counts = {}
for emp in employee_data:
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD', 'Unknown')
    type_counts[emp_type] = type_counts.get(emp_type, 0) + 1

print(f"\n   TYPE Distribution:")
for emp_type, count in sorted(type_counts.items()):
    print(f"      {emp_type}: {count}")

# Check for condition 4 fields
print(f"\n🔍 Condition 4 Field Analysis:")

# Check all possible field names
field_names = set()
for emp in employee_data:
    field_names.update(emp.keys())

condition4_fields = [f for f in field_names if 'condition' in f.lower() and '4' in f]
minimum_days_fields = [f for f in field_names if 'minimum' in f.lower() and 'days' in f.lower()]

print(f"   Condition 4 related fields:")
for field in condition4_fields:
    print(f"      - {field}")

print(f"   Minimum days related fields:")
for field in minimum_days_fields:
    print(f"      - {field}")

# Count employees with condition4 = "yes"
condition4_yes = 0
condition4_no = 0
condition4_missing = 0

minimum_days_met_false = 0
minimum_days_met_true = 0
minimum_days_met_missing = 0

actual_days_below_12 = 0

for emp in employee_data:
    # Check condition4 field
    cond4 = emp.get('condition4') or emp.get('attendancy condition 4 - minimum working days')
    if cond4 == 'yes':
        condition4_yes += 1
    elif cond4 == 'no':
        condition4_no += 1
    else:
        condition4_missing += 1

    # Check Minimum_Days_Met field
    min_met = emp.get('Minimum_Days_Met')
    if min_met is False or min_met == 'False' or min_met == 0:
        minimum_days_met_false += 1
    elif min_met is True or min_met == 'True' or min_met == 1:
        minimum_days_met_true += 1
    else:
        minimum_days_met_missing += 1

    # Check actual working days
    actual_days = emp.get('Actual Working Days') or emp.get('actual_working_days')
    if actual_days is not None:
        try:
            if float(actual_days) < 12:
                actual_days_below_12 += 1
        except:
            pass

print(f"\n📈 Condition Fulfillment Counts:")
print(f"   condition4 = 'yes' (not met): {condition4_yes}")
print(f"   condition4 = 'no' (met): {condition4_no}")
print(f"   condition4 missing: {condition4_missing}")

print(f"\n   Minimum_Days_Met = false: {minimum_days_met_false}")
print(f"   Minimum_Days_Met = true: {minimum_days_met_true}")
print(f"   Minimum_Days_Met missing: {minimum_days_met_missing}")

print(f"\n   Actual Working Days < 12: {actual_days_below_12}")

# Simulate KPI calculation
print(f"\n🎯 KPI Calculation Simulation:")
kpi_count = 0
for emp in employee_data:
    # TYPE-3 제외 (인센티브 대상 아님)
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD')
    if emp_type == 'TYPE-3':
        continue

    minimumDaysMet = emp.get('Minimum_Days_Met')
    if minimumDaysMet is not None:
        if minimumDaysMet is False or minimumDaysMet == 'False' or minimumDaysMet == 0:
            kpi_count += 1
    else:
        # Fallback
        if emp.get('condition4') == 'yes' or emp.get('attendancy condition 4 - minimum working days') == 'yes':
            kpi_count += 1

print(f"   KPI Count (JavaScript logic): {kpi_count}")

# Simulate Modal calculation
print(f"\n🪟 Modal Calculation Simulation:")
modal_count = 0
minimumRequired = 12
for emp in employee_data:
    # TYPE-3 제외 (인센티브 대상 아님)
    emp_type = emp.get('type') or emp.get('ROLE TYPE STD')
    if emp_type == 'TYPE-3':
        continue

    # Method 1: Minimum_Days_Met field
    minimumDaysMet = emp.get('Minimum_Days_Met')
    if minimumDaysMet is not None:
        if minimumDaysMet is False or minimumDaysMet == 'False' or minimumDaysMet == 0:
            modal_count += 1
            continue

    # Method 2: condition4 field - Single Source of Truth
    condition4 = emp.get('condition4')
    if condition4 is not None and condition4 != '':
        if condition4 == 'yes':
            modal_count += 1
        # condition4 필드가 있으면 그 값을 신뢰하고 Method 3로 넘어가지 않음
        continue

    # Method 3: Fallback - actual calculation (condition4가 없을 때만)
    actualDays = emp.get('Actual Working Days') or emp.get('actual_working_days')
    if actualDays is not None:
        try:
            if float(actualDays) < minimumRequired:
                modal_count += 1
        except:
            pass

print(f"   Modal Count (JavaScript logic with all fallbacks): {modal_count}")

# Now load the CSV and compare
print(f"\n📄 CSV Comparison:")
csv_path = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
df = pd.read_csv(csv_path)

print(f"   Total employees in CSV: {len(df)}")

# Check if MONTH column exists, if not assume all data is for September
if 'MONTH' in df.columns:
    df_active = df[
        (df['MONTH'] == 'september') &
        (df['YEAR'] == 2025)
    ].copy()
else:
    # All data is already filtered to September
    df_active = df.copy()

print(f"   Active in CSV: {len(df_active)}")

# Filter TYPE-1 and TYPE-2
df_type12 = df_active[df_active['ROLE TYPE STD'].isin(['TYPE-1', 'TYPE-2'])].copy()
print(f"   TYPE-1 and TYPE-2: {len(df_type12)}")

# Count condition4 in CSV
csv_condition4_yes = len(df_type12[df_type12['attendancy condition 4 - minimum working days'] == 'yes'])
print(f"   CSV condition4 = 'yes': {csv_condition4_yes}")

# Count actual < 12
csv_actual_below_12 = len(df_type12[df_type12['Actual Working Days'] < 12])
print(f"   CSV Actual Working Days < 12: {csv_actual_below_12}")

# Find employees in CSV but not in dashboard
csv_emp_ids = set(df_type12['Employee No'].astype(str))
dashboard_emp_ids = set(str(emp.get('Employee No') or emp.get('employee_id', '')) for emp in employee_data)

missing_from_dashboard = csv_emp_ids - dashboard_emp_ids
extra_in_dashboard = dashboard_emp_ids - csv_emp_ids

print(f"\n🔍 Employee ID Comparison:")
print(f"   In CSV TYPE-1/2 but not in dashboard: {len(missing_from_dashboard)}")
if len(missing_from_dashboard) > 0 and len(missing_from_dashboard) <= 20:
    print(f"      {sorted(missing_from_dashboard)}")

print(f"   In dashboard but not in CSV TYPE-1/2: {len(extra_in_dashboard)}")
if len(extra_in_dashboard) > 0 and len(extra_in_dashboard) <= 20:
    print(f"      {sorted(extra_in_dashboard)}")

# Show sample employee with condition4 = yes
print(f"\n📋 Sample Employee with condition4 = 'yes':")
for emp in employee_data:
    if emp.get('condition4') == 'yes' or emp.get('attendancy condition 4 - minimum working days') == 'yes':
        print(f"   Employee No: {emp.get('Employee No')}")
        print(f"   Name: {emp.get('Full Name English')}")
        print(f"   Type: {emp.get('type')}")
        print(f"   Actual Working Days: {emp.get('Actual Working Days')}")
        print(f"   condition4: {emp.get('condition4')}")
        print(f"   attendancy condition 4: {emp.get('attendancy condition 4 - minimum working days')}")
        print(f"   Minimum_Days_Met: {emp.get('Minimum_Days_Met')}")
        break
