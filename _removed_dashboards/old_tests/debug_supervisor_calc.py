import pandas as pd
import sys
import os
sys.path.append('/Users/ksmoon/Downloads/대시보드 인센티브 테스트11')

# Load the August CSV data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

# Find CAO THỊ MIỀN - handle both string and numeric
cao_df = df[(df['Employee No'] == '618040412') | (df['Employee No'] == 618040412)]
if cao_df.empty:
    print("CAO THỊ MIỀN not found in data")
    sys.exit(1)
cao = cao_df.iloc[0]
print(f"CAO THỊ MIỀN ({cao['Employee No']})")
print(f"Position: {cao['QIP POSITION 1ST  NAME']}")
print(f"Type: {cao['ROLE TYPE STD']}")
print(f"August Incentive: {cao['August_Incentive']:,.0f} VND")
print()

# Find all LINE LEADERs
line_leaders = df[(df['QIP POSITION 1ST  NAME'] == 'LINE LEADER') & (df['ROLE TYPE STD'] == 'TYPE-1')]
print(f"Total TYPE-1 LINE LEADERs: {len(line_leaders)}")
print()

# Calculate average (excluding zeros)
line_leader_incentives = line_leaders['August_Incentive']
non_zero_incentives = line_leader_incentives[line_leader_incentives > 0]
print(f"LINE LEADERs with incentive > 0: {len(non_zero_incentives)}")
print(f"Their incentives: {list(non_zero_incentives)}")

if len(non_zero_incentives) > 0:
    avg = non_zero_incentives.mean()
    print(f"Average: {avg:,.0f} VND")
    print(f"Expected SUPERVISOR amount: {avg * 2.5:,.0f} VND")
else:
    print("No LINE LEADERs with positive incentive")

print()
print("But CAO THỊ MIỀN actually received: 300,000 VND")
print()

# Check CAO THỊ MIỀN's subordinates specifically
print("Checking CAO THỊ MIỀN's direct subordinates:")
# Handle both string and numeric comparison
subordinates = df[(df['MST direct boss name'] == '618040412') | (df['MST direct boss name'] == 618040412)]
for _, sub in subordinates.iterrows():
    print(f"  - {sub['Full Name']} ({sub['Employee No']}): {sub['QIP POSITION 1ST  NAME']}, {sub['August_Incentive']:,.0f} VND")

# Check if there's a team/department association
print("\nChecking team LINE LEADERs (same department):")
cao_dept = cao.get('Department', '')
if cao_dept:
    same_dept = df[(df['Department'] == cao_dept) &
                   (df['QIP POSITION 1ST  NAME'] == 'LINE LEADER') &
                   (df['ROLE TYPE STD'] == 'TYPE-1')]
    print(f"Department: {cao_dept}")
    print(f"LINE LEADERs in same department: {len(same_dept)}")
    for _, leader in same_dept.iterrows():
        print(f"  - {leader['Full Name']}: {leader['August_Incentive']:,.0f} VND")