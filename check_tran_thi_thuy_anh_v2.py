#!/usr/bin/env python3
"""
TRẦN THỊ THÚY ANH 직원의 상세 데이터 확인 V2
Excel의 조건 계산 결과를 직접 확인
"""

import pandas as pd
import json

# Excel 파일 읽기
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv', encoding='utf-8-sig')

# TRẦN THỊ THÚY ANH 찾기
employee = df[df['Full Name'].str.contains('TRẦN THỊ THÚY ANH', na=False)]

if not employee.empty:
    emp = employee.iloc[0]

    print("="*80)
    print("🔍 TRẦN THỊ THÚY ANH 상세 정보")
    print("="*80)

    print(f"\n📌 기본 정보:")
    print(f"  - 이름: {emp['Full Name']}")
    print(f"  - 직급: {emp['FINAL QIP POSITION NAME CODE']}")
    print(f"  - TYPE: {emp['ROLE TYPE STD']}")
    print(f"  - 9월 인센티브: {emp['September_Incentive']:,} VND")
    print(f"  - 최종 인센티브: {emp['Final Incentive amount']:,} VND")

    print(f"\n📊 조건별 충족 현황 (Excel 계산값):")
    # 각 조건 확인
    for i in range(1, 11):
        cond_name_col = f'cond_{i}_'
        value_col = f'cond_{i}_value'
        threshold_col = f'cond_{i}_threshold'

        # 조건 이름 찾기
        cond_name = ""
        for col in emp.index:
            if col.startswith(cond_name_col) and not col.endswith('_value') and not col.endswith('_threshold'):
                # 조건 충족 여부
                passed = emp[col]
                if passed == 'PASS' or passed == True or passed == 1:
                    status = "✅ PASS"
                elif passed == 'N/A' or pd.isna(passed):
                    status = "⚫ N/A"
                else:
                    status = "❌ FAIL"

                # 조건 이름 매핑
                condition_names = {
                    'cond_1_attendance_rate': '출근율',
                    'cond_2_unapproved_absence': '무단결근',
                    'cond_3_actual_working_days': '실제근무일',
                    'cond_4_minimum_days': '최소근무일',
                    'cond_5_aql_personal_failure': '개인AQL실패',
                    'cond_6_aql_continuous': '3개월연속AQL실패',
                    'cond_7_aql_team_area': '팀/구역AQL',
                    'cond_8_area_reject': '구역Reject율',
                    'cond_9_5prs_pass_rate': '5PRS통과율',
                    'cond_10_5prs_inspection_qty': '5PRS검사량'
                }

                cond_name = condition_names.get(col, col)

                # 값과 기준 출력
                if value_col in emp.index:
                    value = emp[value_col]
                    threshold = emp.get(threshold_col, 'N/A')
                    print(f"  조건{i} ({cond_name}): {status}")
                    print(f"    - 실제값: {value}, 기준: {threshold}")
                break

    print(f"\n📈 Excel 계산 요약:")
    print(f"  - 적용 가능한 조건 수: {emp.get('conditions_applicable', 'N/A')}개")
    print(f"  - 통과한 조건 수: {emp.get('conditions_passed', 'N/A')}개")
    print(f"  - 통과율: {emp.get('conditions_pass_rate', 'N/A')}%")

    # position_condition_matrix.json 로드
    with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)

    position = emp['FINAL QIP POSITION NAME CODE']
    type_std = emp['ROLE TYPE STD']

    print(f"\n⚙️ JSON 설정 분석:")
    print(f"  - TYPE: {type_std}")
    print(f"  - 직급: {position}")

    # 적용되어야 할 조건 찾기
    if type_std in matrix['position_matrix']:
        type_config = matrix['position_matrix'][type_std]

        # 직급별 조건 찾기
        applicable_conditions = None
        matched_config = None

        for key, config in type_config.items():
            if 'patterns' in config:
                for pattern in config['patterns']:
                    if pattern in position:
                        applicable_conditions = config['applicable_conditions']
                        matched_config = key
                        print(f"\n  📍 매칭된 설정: {key}")
                        print(f"  - 설명: {config['description']}")
                        print(f"  - JSON 적용 조건: {applicable_conditions}")
                        break
            if applicable_conditions:
                break

        # 기본 조건 사용
        if not applicable_conditions and 'default' in type_config:
            applicable_conditions = type_config['default']['applicable_conditions']
            print(f"\n  📍 기본 설정 사용")
            print(f"  - 설명: {type_config['default']['description']}")
            print(f"  - JSON 적용 조건: {applicable_conditions}")

        print(f"\n🔴 문제 분석:")
        print(f"  - JSON 설정상 필요 조건: {applicable_conditions} ({len(applicable_conditions)}개)")
        print(f"  - Excel 계산 적용 조건: {emp.get('conditions_applicable', 'N/A')}개")
        print(f"  - Excel 계산 통과 조건: {emp.get('conditions_passed', 'N/A')}개")

        if emp.get('conditions_passed', 0) < len(applicable_conditions):
            print(f"\n  ⚠️ 경고: JSON 설정상 필요한 모든 조건을 충족하지 못했는데 인센티브가 지급됨!")
            print(f"  - 이는 Excel 계산 로직이 JSON 설정과 다르게 적용되고 있음을 의미함")

        # 실제로 통과한 조건 확인
        passed_conditions = []
        for i in range(1, 11):
            cond_col = f'cond_{i}_'
            for col in emp.index:
                if col.startswith(cond_col) and not col.endswith('_value') and not col.endswith('_threshold'):
                    if emp[col] == 'PASS' or emp[col] == True or emp[col] == 1:
                        passed_conditions.append(i)
                    break

        print(f"\n  📊 실제 통과한 조건 번호: {passed_conditions}")
        print(f"  - JSON 필요 조건 중 미충족: {[c for c in applicable_conditions if c not in passed_conditions]}")

else:
    print("직원을 찾을 수 없습니다.")