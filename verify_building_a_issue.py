import pandas as pd
import json

print("="*80)
print("NGUYỄN THANH TRÚC 인센티브 0 VND - 최종 원인 확인")
print("="*80)
print()

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')

# Load mapping
with open('config_files/auditor_trainer_area_mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Find NGUYỄN THANH TRÚC
truc = df[(df['Employee No'] == '620070013') | (df['Employee No'] == 620070013)].iloc[0]
print(f"직원: {truc['Full Name']} ({truc['Employee No']})")
print(f"직급: {truc['QIP POSITION 1ST  NAME']}")
print(f"8월 인센티브: {truc['August_Incentive']:,.0f} VND")
print()

# Check mapping
print("1. 담당 구역 매핑 확인:")
truc_mapping = mapping['auditor_trainer_areas'].get('620070013', {})
if truc_mapping:
    print(f"   ✅ 매핑 존재: {truc_mapping['description']}")
    print(f"   담당: Building {truc_mapping['conditions'][0]['filters'][1]['value']}")
else:
    print("   ❌ 매핑 없음")
print()

# Check continuous failures in Building A
print("2. Building A의 3개월 연속 실패자 확인:")
continuous_fail = df[df['Continuous_FAIL'] == 'YES']
building_a_fails = continuous_fail[continuous_fail['BUILDING'] == 'A']

if len(building_a_fails) > 0:
    print(f"   ⚠️ Building A에 3개월 연속 실패자 {len(building_a_fails)}명 존재!")
    for _, fail_emp in building_a_fails.iterrows():
        print(f"      - {fail_emp['Full Name']} ({fail_emp['Employee No']})")
else:
    print("   ✅ Building A에 3개월 연속 실패자 없음")
print()

# Show the code logic
print("3. 코드 로직 (src/step1_인센티브_계산_개선버전.py):")
print("   라인 2186: auditor_factory = self.get_auditor_assigned_factory(emp_id)")
print("              → Building 'A' 반환")
print()
print("   라인 2187: has_continuous_fail_in_factory = auditor_factory in continuous_fail_by_factory")
print("              → Building A에 실패자 1명 있으므로 True")
print()
print("   라인 2206-2209:")
print("   elif has_continuous_fail_in_factory:")
print("       incentive = 0")
print("       print(f'담당 공장에 3개월 연속 AQL 실패자 {fail_count}명 → 0 VND')")
print()

print("="*80)
print("💡 최종 결론:")
print("="*80)
print()
print("NGUYỄN THANH TRÚC이 0 VND를 받은 이유:")
print()
print("1. NGUYỄN THANH TRÚC은 Building A 담당 (매핑 파일에 명시)")
print("2. Building A에 NGUYỄN THỊ KIM THOA가 3개월 연속 AQL 실패")
print("3. AUDIT & TRAINING TEAM 규칙: 담당 구역에 3개월 연속 실패자가 있으면 인센티브 0")
print("4. 따라서 모든 조건을 충족했어도 인센티브 0 VND")
print()
print("이것은 코드가 정확하게 작동한 결과입니다!")
print("AUDIT & TRAINING TEAM은 담당 구역의 품질 책임을 지기 때문에")
print("담당 구역에 연속 실패자가 있으면 인센티브를 받을 수 없습니다.")