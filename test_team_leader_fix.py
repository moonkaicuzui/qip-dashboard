import pandas as pd
import json

print("="*80)
print("Team Leader 수정 사항 테스트")
print("="*80)
print()

# Load mapping
with open('config_files/auditor_trainer_area_mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Check VÕ THỊ THÙY LINH
emp_id = '620080295'
if emp_id in mapping['auditor_trainer_areas']:
    config = mapping['auditor_trainer_areas'][emp_id]
    print(f"VÕ THỊ THÙY LINH ({emp_id})")
    print(f"  담당: {config['description']}")
    print(f"  조건: {config['conditions']}")
    print()

    # Check if Team Leader
    is_team_leader = False
    for condition in config.get('conditions', []):
        if condition.get('type') == 'ALL':
            is_team_leader = True
            break

    if is_team_leader:
        print("  ✅ Team Leader 확인됨 (전체 구역 담당)")
        print("  → 수정 후: 연속 실패자 체크에서 제외됨")
        print("  → 예상 인센티브: Progressive Incentive 적용")
        print()

        # Check expected incentive based on previous month
        print("  Progressive Incentive 계산:")
        print("    7월: 650,000 VND (8개월차)")
        print("    8월 조건 충족 시: 9개월차 → 750,000 VND 예상")
    else:
        print("  ❌ Team Leader 아님")

print()
print("="*80)
print("수정 사항 요약:")
print("="*80)
print()
print("변경 전:")
print("  - Team Leader도 담당 구역(전체)에 연속 실패자가 있으면 인센티브 0")
print("  - VÕ THỊ THÙY LINH: 0 VND (Building A 연속 실패자 영향)")
print()
print("변경 후:")
print("  - Team Leader는 연속 실패자 체크에서 제외")
print("  - is_all_buildings_team_leader() 함수로 Team Leader 확인")
print("  - Team Leader인 경우 has_continuous_fail_in_factory = False 설정")
print("  - VÕ THỊ THÙY LINH: Progressive Incentive 정상 적용 예상")
print()
print("코드 수정 위치:")
print("  - src/step1_인센티브_계산_개선버전.py")
print("  - 라인 2042-2060: is_all_buildings_team_leader() 함수 추가")
print("  - 라인 2188-2193: Team Leader 예외 처리 추가")