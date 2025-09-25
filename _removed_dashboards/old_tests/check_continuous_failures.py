import pandas as pd

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

print("="*80)
print("3개월 연속 AQL 실패자 확인")
print("="*80)
print()

# Find all employees with Continuous_FAIL = YES
continuous_fail_employees = df[df['Continuous_FAIL'] == 'YES']

print(f"3개월 연속 실패자 총 {len(continuous_fail_employees)}명:")
print()

# Group by building instead of factory
if 'BUILDING' in continuous_fail_employees.columns:
    for building in continuous_fail_employees['BUILDING'].unique():
        building_fails = continuous_fail_employees[continuous_fail_employees['BUILDING'] == building]
        print(f"건물 {building}: {len(building_fails)}명")
        for _, emp in building_fails.iterrows():
            print(f"  - {emp['Full Name']} ({emp['Employee No']}): {emp['QIP POSITION 1ST  NAME']}")
        print()
else:
    print("건물별 그룹화 불가 - BUILDING 컬럼 없음")
    for _, emp in continuous_fail_employees.iterrows():
        print(f"  - {emp['Full Name']} ({emp['Employee No']}): {emp['QIP POSITION 1ST  NAME']}")
    print()

# Check NGUYỄN THANH TRÚC's factory assignment
print("="*80)
print("NGUYỄN THANH TRÚC 담당 공장 확인")
print("="*80)
print()

truc = df[(df['Employee No'] == '620070013') | (df['Employee No'] == 620070013)].iloc[0]
print(f"NGUYỄN THANH TRÚC의 소속 건물: {truc.get('BUILDING', 'N/A')}")
print()

# Check if AUDIT & TRAINING team members are assigned to specific buildings
audit_training = df[df['QIP POSITION 1ST  NAME'].str.contains('AUDIT|TRAINING', na=False, case=False)]
print(f"AUDIT & TRAINING TEAM 멤버들의 건물 분포:")
if 'BUILDING' in audit_training.columns:
    for building in audit_training['BUILDING'].unique():
        members = audit_training[audit_training['BUILDING'] == building]
        print(f"  건물 {building}: {len(members)}명")
else:
    print("  건물 정보 없음")

print()
print("="*80)
print("분석 결과:")
print("="*80)

# Check if NGUYỄN THANH TRÚC's building has continuous failures
if 'BUILDING' in truc.index and 'BUILDING' in continuous_fail_employees.columns:
    truc_building = truc['BUILDING']
    if truc_building in continuous_fail_employees['BUILDING'].values:
        fail_count = len(continuous_fail_employees[continuous_fail_employees['BUILDING'] == truc_building])
        print(f"⚠️ NGUYỄN THANH TRÚC의 소속 건물({truc_building})에 3개월 연속 실패자가 {fail_count}명 있습니다!")
        print("   이것이 인센티브 0 VND의 원인일 수 있습니다.")
        print()
        print("코드 로직 (라인 2206-2209):")
        print("  if has_continuous_fail_in_factory:")
        print("      incentive = 0")
        print("      print(f'담당 공장에 3개월 연속 AQL 실패자 {fail_count}명 → 0 VND')")
    else:
        print(f"✅ NGUYỄN THANH TRÚC의 소속 건물({truc_building})에는 3개월 연속 실패자가 없습니다.")
        print("   다른 원인을 찾아야 합니다.")
else:
    print("건물 정보로 비교 불가")

# Additional check: Is the factory assignment the issue?
print()
print("추가 확인: 담당 공장 매핑 로직")
print("AUDIT & TRAINING TEAM은 특정 공장을 담당하는 것이 아니라")
print("전체 또는 특정 구역을 담당할 수 있습니다.")
print("get_auditor_assigned_factory() 함수의 로직을 확인해야 합니다.")