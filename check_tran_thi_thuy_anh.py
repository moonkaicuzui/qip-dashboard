#!/usr/bin/env python3
"""
TRẦN THỊ THÚY ANH 직원의 상세 데이터 확인
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

    print(f"\n📊 조건 충족 현황:")
    print(f"  1. 출근율: {emp['Attendance Rate']}% (기준: >=88%)")
    print(f"  2. 무단결근: {emp['Unapproved Absences']}일 (기준: <=2일)")
    print(f"  3. 실제근무일: {emp['Actual Working Days']}일 (기준: >0일)")
    print(f"  4. 총근무일: {emp['Total Working Days']}일 (기준: >=12일)")
    print(f"  5. 당월 AQL 실패: {emp['AQL Failures Current Month']} (기준: 0)")
    print(f"  6. 3개월 연속 AQL 실패: {emp['3-Month Consecutive AQL Failures']} (기준: No)")
    print(f"  7. 팀/구역 3개월 연속 실패: 데이터 없음")
    print(f"  8. 담당구역 Reject율: 데이터 없음")
    print(f"  9. 5PRS 통과율: {emp['5prs_pass_rate']}% (기준: >=95%)")
    print(f"  10. 5PRS 검사량: {emp['5prs_inspection_qty']} (기준: >=100)")

    # position_condition_matrix.json 로드
    with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)

    # 직급에 따른 적용 조건 확인
    position = emp['FINAL QIP POSITION NAME CODE']
    type_std = emp['ROLE TYPE STD']

    print(f"\n⚠️ 조건 매트릭스 분석:")
    print(f"  - TYPE: {type_std}")
    print(f"  - 직급: {position}")

    # 적용되어야 할 조건 찾기
    if type_std in matrix['position_matrix']:
        type_config = matrix['position_matrix'][type_std]

        # 직급별 조건 찾기
        applicable_conditions = None
        for key, config in type_config.items():
            if 'patterns' in config:
                for pattern in config['patterns']:
                    if pattern in position:
                        applicable_conditions = config['applicable_conditions']
                        print(f"\n  📍 매칭된 설정: {key}")
                        print(f"  - 설명: {config['description']}")
                        print(f"  - 적용 조건: {applicable_conditions}")
                        break
            if applicable_conditions:
                break

        # 기본 조건 사용
        if not applicable_conditions and 'default' in type_config:
            applicable_conditions = type_config['default']['applicable_conditions']
            print(f"\n  📍 기본 설정 사용")
            print(f"  - 설명: {type_config['default']['description']}")
            print(f"  - 적용 조건: {applicable_conditions}")

    # 실제 충족 조건 확인
    conditions_met = []
    if emp['Attendance Rate'] >= 88:
        conditions_met.append(1)
    if emp['Unapproved Absences'] <= 2:
        conditions_met.append(2)
    if emp['Actual Working Days'] > 0:
        conditions_met.append(3)
    if emp['Total Working Days'] >= 12:
        conditions_met.append(4)
    if emp['AQL Failures Current Month'] == 0:
        conditions_met.append(5)
    if emp['3-Month Consecutive AQL Failures'] == 'No':
        conditions_met.append(6)
    if emp['5prs_pass_rate'] >= 95:
        conditions_met.append(9)
    if emp['5prs_inspection_qty'] >= 100:
        conditions_met.append(10)

    print(f"\n📊 충족된 조건: {conditions_met}")
    print(f"  - 충족 조건 수: {len(conditions_met)}개")

    if applicable_conditions:
        print(f"\n🔴 문제 분석:")
        print(f"  - 필요 조건: {applicable_conditions} ({len(applicable_conditions)}개)")
        print(f"  - 충족된 조건: {conditions_met} ({len(conditions_met)}개)")

        # 필요한 조건 중 충족된 것 계산
        met_required = [c for c in conditions_met if c in applicable_conditions]
        print(f"  - 필요 조건 중 충족: {met_required} ({len(met_required)}/{len(applicable_conditions)}개)")

        if len(met_required) < len(applicable_conditions):
            print(f"\n  ⚠️ 경고: 필요 조건을 모두 충족하지 못했는데 인센티브가 지급됨!")
            print(f"  - 미충족 조건: {[c for c in applicable_conditions if c not in conditions_met]}")
else:
    print("직원을 찾을 수 없습니다.")