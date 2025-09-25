import pandas as pd

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

print("="*80)
print("문제 케이스 상세 분석")
print("="*80)
print()

# Manager: TRẦN THỊ BÍCH LY
manager = df[(df['Employee No'] == '620070012') | (df['Employee No'] == 620070012)].iloc[0]
print(f"MANAGER: {manager['Full Name']} ({manager['Employee No']})")
print(f"인센티브: {manager['August_Incentive']:,.0f} VND")
print()

# Find manager's LINE LEADERs
manager_line_leaders = df[
    ((df['MST direct boss name'] == '620070012') | (df['MST direct boss name'] == 620070012)) &
    (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER') &
    (df['ROLE TYPE STD'] == 'TYPE-1')
]

print("Manager의 팀 LINE LEADER들:")
manager_total = 0
manager_count = 0
for _, leader in manager_line_leaders.iterrows():
    incentive = leader['August_Incentive']
    print(f"  - {leader['Full Name']}: {incentive:,.0f} VND")
    if incentive > 0:
        manager_total += incentive
        manager_count += 1

if manager_count > 0:
    manager_avg = manager_total / manager_count
    print(f"\n평균 (0 제외): {manager_avg:,.0f} VND")
    print(f"Manager 계산: {manager_avg:,.0f} × 3.5 = {manager_avg * 3.5:,.0f} VND")
else:
    print("\n인센티브 받는 LINE LEADER 없음")

print()
print("-"*80)
print()

# Supervisors with higher incentive
supervisors = df[
    (df['QIP POSITION 1ST  NAME'].isin(['SUPERVISOR', '(V) SUPERVISOR', 'V.SUPERVISOR'])) &
    (df['ROLE TYPE STD'] == 'TYPE-1') &
    (df['August_Incentive'] > manager['August_Incentive'])
]

for _, supervisor in supervisors.iterrows():
    print(f"SUPERVISOR: {supervisor['Full Name']} ({supervisor['Employee No']})")
    print(f"인센티브: {supervisor['August_Incentive']:,.0f} VND")

    # Find supervisor's LINE LEADERs
    sup_line_leaders = df[
        ((df['MST direct boss name'] == supervisor['Employee No']) |
         (df['MST direct boss name'] == str(supervisor['Employee No']))) &
        (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER') &
        (df['ROLE TYPE STD'] == 'TYPE-1')
    ]

    print("Supervisor의 팀 LINE LEADER들:")
    sup_total = 0
    sup_count = 0
    for _, leader in sup_line_leaders.iterrows():
        incentive = leader['August_Incentive']
        print(f"  - {leader['Full Name']}: {incentive:,.0f} VND")
        if incentive > 0:
            sup_total += incentive
            sup_count += 1

    if sup_count > 0:
        sup_avg = sup_total / sup_count
        print(f"\n평균 (0 제외): {sup_avg:,.0f} VND")
        print(f"Supervisor 계산: {sup_avg:,.0f} × 2.5 = {sup_avg * 2.5:,.0f} VND")
    else:
        print("\n인센티브 받는 LINE LEADER 없음")
    print()
    print("-"*80)
    print()

print("🔍 문제 분석:")
print()
print("Manager는 3.5배 배수를 받지만, Supervisor는 2.5배를 받습니다.")
print("하지만 각자의 팀 내 LINE LEADER 평균이 다르기 때문에")
print("Supervisor의 팀 LINE LEADER 평균이 더 높으면")
print("Manager보다 높은 인센티브를 받을 수 있습니다.")
print()
print("예: Manager 팀 평균 140,969 × 3.5 = 493,390 VND")
print("    Supervisor 팀 평균 203,000 × 2.5 = 507,500 VND")
print()
print("⚠️ 이는 직급 체계와 맞지 않는 결과입니다!")
print("   상위 직급이 더 많은 인센티브를 받도록 보정이 필요할 수 있습니다.")