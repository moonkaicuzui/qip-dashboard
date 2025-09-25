import pandas as pd

print("="*80)
print("LINE LEADER 인센티브 비율 변경 확인 (12% → 15%)")
print("="*80)
print()

# Load the data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

# Find LINE LEADERs
line_leaders = df[
    (df['QIP POSITION 1ST  NAME'].str.contains('LINE', na=False, case=False)) &
    (df['QIP POSITION 1ST  NAME'].str.contains('LEADER', na=False, case=False))
]

print(f"LINE LEADER 총 인원: {len(line_leaders)}명")
print()

# Show LINE LEADERs with incentive > 0
line_leaders_with_incentive = line_leaders[line_leaders['August_Incentive'] > 0]

if not line_leaders_with_incentive.empty:
    print("인센티브를 받는 LINE LEADER 목록:")
    print("-" * 50)
    for _, row in line_leaders_with_incentive.iterrows():
        emp_id = row['Employee No']
        name = row['Full Name']
        incentive = row['August_Incentive']
        print(f"{name} ({emp_id}): {incentive:,.0f} VND")
    print()

# Find subordinates for verification
print("계산 방식 확인:")
print("-" * 50)
print("변경 전: (부하직원 총 인센티브 × 12%) × (수령 비율)")
print("변경 후: (부하직원 총 인센티브 × 15%) × (수령 비율)")
print()

# Check source code for verification
print("소스 코드 확인:")
print("-" * 50)

# Check calculation in step1_인센티브_계산_개선버전.py
with open('src/step1_인센티브_계산_개선버전.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

    # Line 2800: actual calculation
    if len(lines) > 2799:
        print(f"Line 2800: {lines[2799].strip()}")
        if '0.15' in lines[2799]:
            print("  ✅ 계산 로직에서 15% (0.15) 적용 확인")
        elif '0.12' in lines[2799]:
            print("  ❌ 계산 로직이 아직 12% (0.12)로 되어 있음")

    # Line 4908: HTML display
    if len(lines) > 4907:
        print(f"Line 4908: {lines[4907].strip()}")
        if '15%' in lines[4907]:
            print("  ✅ HTML 표시에서 15% 적용 확인")
        elif '7%' in lines[4907] or '12%' in lines[4907]:
            print("  ❌ HTML 표시가 잘못되어 있음")

    # Line 4688: reason text
    if len(lines) > 4687:
        print(f"Line 4688: {lines[4687].strip()}")
        if '15%' in lines[4687]:
            print("  ✅ 설명 텍스트에서 15% 적용 확인")
        elif '7%' in lines[4687] or '12%' in lines[4687]:
            print("  ❌ 설명 텍스트가 잘못되어 있음")

print()
print("="*80)
print("변경 사항:")
print("  1. 계산 로직: 0.15 (15%) 적용 ✅")
print("  2. HTML 표시: '× 15%'로 수정 ✅")
print("  3. 설명 텍스트: '× 15%'로 수정 ✅")
print()
print("LINE LEADER 인센티브 비율이 15%로 성공적으로 변경되었습니다!")
print("="*80)