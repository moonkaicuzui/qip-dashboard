import pandas as pd

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

print("="*80)
print("MANAGER 계산 로직 재확인")
print("="*80)
print()

# Manager
manager = df[(df['Employee No'] == '620070012') | (df['Employee No'] == 620070012)].iloc[0]
print(f"MANAGER: {manager['Full Name']} ({manager['Employee No']})")
print(f"실제 인센티브: {manager['August_Incentive']:,.0f} VND")
print()

# 직속 부하 확인
direct_subs = df[
    (df['MST direct boss name'] == '620070012') |
    (df['MST direct boss name'] == 620070012)
]

print(f"직속 부하 총 {len(direct_subs)}명:")
for _, sub in direct_subs.iterrows():
    print(f"  - {sub['Full Name']}: {sub['QIP POSITION 1ST  NAME']}")

# LINE LEADER 직속 부하
direct_line_leaders = direct_subs[
    (direct_subs['QIP POSITION 1ST  NAME'] == 'LINE LEADER') &
    (direct_subs['ROLE TYPE STD'] == 'TYPE-1')
]
print(f"\n직속 LINE LEADER: {len(direct_line_leaders)}명")

# 부하의 부하 확인 (재귀적)
print("\n부하의 부하 검색 중...")
all_subordinates = set()
to_check = set([str(manager['Employee No']), manager['Employee No']])
checked = set()

while to_check:
    current = to_check.pop()
    if current in checked:
        continue
    checked.add(current)

    subs = df[(df['MST direct boss name'] == current) | (df['MST direct boss name'] == str(current))]
    for _, sub in subs.iterrows():
        sub_id = str(sub['Employee No'])
        all_subordinates.add(sub_id)
        to_check.add(sub_id)

print(f"총 부하 (재귀적): {len(all_subordinates)}명")

# 그 중 LINE LEADER
all_sub_line_leaders = df[
    df['Employee No'].astype(str).isin(all_subordinates) &
    (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER') &
    (df['ROLE TYPE STD'] == 'TYPE-1')
]

print(f"팀 내 모든 LINE LEADER: {len(all_sub_line_leaders)}명")
if len(all_sub_line_leaders) > 0:
    for _, leader in all_sub_line_leaders.iterrows():
        print(f"  - {leader['Full Name']}: {leader['August_Incentive']:,.0f} VND")

    non_zero = all_sub_line_leaders[all_sub_line_leaders['August_Incentive'] > 0]
    if len(non_zero) > 0:
        avg = non_zero['August_Incentive'].mean()
        print(f"\n평균 (0 제외): {avg:,.0f} VND")
        print(f"Manager 계산: {avg:,.0f} × 3.5 = {avg * 3.5:,.0f} VND")

# 전체 TYPE-1 LINE LEADER 평균으로 계산해보기
print("\n" + "="*80)
print("전체 TYPE-1 LINE LEADER 평균 사용 가능성 확인:")
all_line_leaders = df[
    (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER') &
    (df['ROLE TYPE STD'] == 'TYPE-1') &
    (df['August_Incentive'] > 0)
]
if len(all_line_leaders) > 0:
    avg_all = all_line_leaders['August_Incentive'].mean()
    print(f"전체 LINE LEADER 평균: {avg_all:,.0f} VND")
    print(f"Manager 계산: {avg_all:,.0f} × 3.5 = {avg_all * 3.5:,.0f} VND")

    if abs(avg_all * 3.5 - manager['August_Incentive']) < 1:
        print("\n✅ Manager는 전체 TYPE-1 LINE LEADER 평균을 사용하는 것으로 보입니다!")
    else:
        print("\n❌ 전체 평균도 아닙니다. 다른 계산 방식이 사용되었습니다.")