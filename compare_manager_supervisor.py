import pandas as pd
import numpy as np

# Load the August CSV data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

print("="*80)
print("MANAGER vs SUPERVISOR 인센티브 비교 분석")
print("="*80)
print()

# Filter TYPE-1 positions
type1_df = df[df['ROLE TYPE STD'] == 'TYPE-1'].copy()

# Categorize positions
managers = type1_df[type1_df['QIP POSITION 1ST  NAME'].isin(['MANAGER', 'S.MANAGER', 'SENIOR MANAGER'])]
supervisors = type1_df[type1_df['QIP POSITION 1ST  NAME'].isin(['(V) SUPERVISOR', 'SUPERVISOR', 'V.SUPERVISOR', 'VICE SUPERVISOR'])]

print("📊 통계:")
print(f"  - Managers 수: {len(managers)}")
print(f"  - Supervisors 수: {len(supervisors)}")
print()

# Calculate statistics
print("💰 인센티브 금액 분석:")
print()
print("MANAGERS:")
manager_incentives = managers[managers['August_Incentive'] > 0]['August_Incentive']
if len(manager_incentives) > 0:
    print(f"  - 평균: {manager_incentives.mean():,.0f} VND")
    print(f"  - 최소: {manager_incentives.min():,.0f} VND")
    print(f"  - 최대: {manager_incentives.max():,.0f} VND")
    print(f"  - 인센티브 받는 인원: {len(manager_incentives)}명")
else:
    print("  - 인센티브 받는 Manager 없음")

print()
print("SUPERVISORS:")
supervisor_incentives = supervisors[supervisors['August_Incentive'] > 0]['August_Incentive']
if len(supervisor_incentives) > 0:
    print(f"  - 평균: {supervisor_incentives.mean():,.0f} VND")
    print(f"  - 최소: {supervisor_incentives.min():,.0f} VND")
    print(f"  - 최대: {supervisor_incentives.max():,.0f} VND")
    print(f"  - 인센티브 받는 인원: {len(supervisor_incentives)}명")
else:
    print("  - 인센티브 받는 Supervisor 없음")

print()
print("="*80)
print("⚠️  MANAGER < SUPERVISOR 케이스 찾기")
print("="*80)
print()

# Find problematic cases
problem_cases = []

for _, manager in managers.iterrows():
    if manager['August_Incentive'] > 0:
        manager_incentive = manager['August_Incentive']
        manager_name = manager['Full Name']
        manager_id = manager['Employee No']

        # Find subordinate supervisors
        subordinate_supervisors = supervisors[
            (supervisors['MST direct boss name'] == manager_id) |
            (supervisors['MST direct boss name'] == str(manager_id))
        ]

        for _, supervisor in subordinate_supervisors.iterrows():
            if supervisor['August_Incentive'] > manager_incentive:
                problem_cases.append({
                    'manager': manager_name,
                    'manager_id': manager_id,
                    'manager_incentive': manager_incentive,
                    'supervisor': supervisor['Full Name'],
                    'supervisor_id': supervisor['Employee No'],
                    'supervisor_incentive': supervisor['August_Incentive']
                })

# Also check all managers vs all supervisors
for _, manager in managers.iterrows():
    if manager['August_Incentive'] > 0:
        for _, supervisor in supervisors.iterrows():
            if supervisor['August_Incentive'] > manager['August_Incentive']:
                found = False
                for case in problem_cases:
                    if case['manager_id'] == manager['Employee No'] and case['supervisor_id'] == supervisor['Employee No']:
                        found = True
                        break
                if not found:
                    problem_cases.append({
                        'manager': manager['Full Name'],
                        'manager_id': manager['Employee No'],
                        'manager_incentive': manager['August_Incentive'],
                        'supervisor': supervisor['Full Name'],
                        'supervisor_id': supervisor['Employee No'],
                        'supervisor_incentive': supervisor['August_Incentive']
                    })

if problem_cases:
    print(f"발견된 문제 케이스: {len(problem_cases)}건")
    print()
    for i, case in enumerate(problem_cases[:10], 1):  # Show first 10 cases
        print(f"{i}. MANAGER: {case['manager']} ({case['manager_id']})")
        print(f"   인센티브: {case['manager_incentive']:,.0f} VND")
        print(f"   SUPERVISOR: {case['supervisor']} ({case['supervisor_id']})")
        print(f"   인센티브: {case['supervisor_incentive']:,.0f} VND")
        print(f"   차이: {case['supervisor_incentive'] - case['manager_incentive']:,.0f} VND (Supervisor가 더 많음)")
        print()
else:
    print("✅ 문제 케이스 없음: 모든 Manager가 Supervisor보다 높거나 같은 인센티브를 받고 있습니다.")

print()
print("="*80)
print("🔍 배수(Multiplier) 확인")
print("="*80)
print()
print("현재 설정된 배수 (src/step1_인센티브_계산_개선버전.py):")
print("  - Senior Manager: 4.0배")
print("  - Manager: 3.5배")
print("  - Assistant Manager: 3.0배")
print("  - (V) Supervisor: 2.5배")
print("  - Supervisor: 2.5배")
print()
print("문제 원인 분석:")
print("  Manager와 Supervisor 모두 같은 LINE LEADER 평균을 사용하지만,")
print("  각자의 팀 내 LINE LEADER들만 계산하므로 평균이 다를 수 있습니다.")
print("  따라서 Manager(3.5배)가 Supervisor(2.5배)보다 낮을 수 있습니다.")