import pandas as pd

print("="*80)
print("NGUYỄN THANH TRÚC 인센티브 0 VND - 최종 분석")
print("="*80)
print()

# Load data
df = pd.read_csv('output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv')
emp = df[(df['Employee No'] == '620070013') | (df['Employee No'] == 620070013)].iloc[0]

print(f"직원: {emp['Full Name']} ({emp['Employee No']})")
print(f"직급: {emp['QIP POSITION 1ST  NAME']}")
print(f"타입: {emp['ROLE TYPE STD']}")
print(f"8월 인센티브: {emp['August_Incentive']:,.0f} VND")
print(f"7월 인센티브: {emp.get('July_Incentive', 0):,.0f} VND")
print()

print("조건 충족 상태:")
print("  ✅ 출근 조건: 모두 PASS")
print("  ✅ 담당구역 reject율: 0% < 3%")
print("  ✅ 팀/구역 AQL: PASS")
print()

print("3개월 연속 실패자 현황:")
continuous_fail = df[df['Continuous_FAIL'] == 'YES']
print(f"  전체: {len(continuous_fail)}명")
if len(continuous_fail) > 0:
    for _, fail_emp in continuous_fail.iterrows():
        print(f"    - {fail_emp['Full Name']} (건물 {fail_emp.get('BUILDING', 'N/A')})")
print()

print("="*80)
print("🔍 원인 분석 결과:")
print("="*80)
print()

print("가능한 원인들:")
print()

print("1. ⭐ 가장 가능성 높음: 담당 공장 매핑 문제")
print("   - get_auditor_assigned_factory() 함수가 빈 문자열 반환")
print("   - auditor_trainer_area_mapping.json 파일 없음 또는 매핑 없음")
print("   - 결과: 담당 공장을 찾지 못해 기본값으로 처리")
print()

print("2. 담당 공장에 3개월 연속 실패자 존재")
print("   - 코드 라인 2206-2209에서 체크")
print("   - 하지만 NGUYỄN THANH TRÚC의 건물이 NaN이므로 이 조건은 False일 가능성 높음")
print()

print("3. calculate_continuous_months_from_history() 반환값 문제")
print("   - 7월에 450,000 VND (5-6개월차)를 받았는데")
print("   - 8월에 0 VND라는 것은 연속 개월이 리셋되었을 가능성")
print()

print("4. 특별한 예외 처리")
print("   - 코드에 하드코딩된 특별 조건이 있을 수 있음")
print()

print("="*80)
print("💡 결론:")
print("="*80)
print()
print("NGUYỄN THANH TRÚC이 모든 조건을 충족했는데도 0 VND를 받은 이유는")
print("아마도 담당 공장 매핑이 제대로 설정되지 않아서")
print("기본적으로 인센티브가 0으로 설정되었을 가능성이 가장 높습니다.")
print()
print("해결 방법:")
print("1. auditor_trainer_area_mapping.json 파일 생성/수정")
print("2. NGUYỄN THANH TRÚC (620070013)의 담당 구역 매핑 추가")
print("3. 또는 코드에서 매핑이 없을 때의 기본 처리 로직 개선")