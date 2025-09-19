#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실패 사유 표시 테스트 스크립트
"""

import pandas as pd

def test_failure_reasons():
    """실패 사유가 올바르게 표시되는지 테스트"""

    print("=" * 60)
    print("🔍 실패 사유 표시 테스트")
    print("=" * 60)
    print()

    # CSV 파일 로드
    df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')

    # 인센티브가 0인 TYPE-1 직원 찾기
    zero_incentive = df[(df['September_Incentive'] == 0) & (df['ROLE TYPE STD'] == 'TYPE-1')]

    print(f"📊 인센티브 0인 TYPE-1 직원: {len(zero_incentive)}명")
    print()

    # 각 직원의 실패 사유 분석
    for idx, row in zero_incentive.head(5).iterrows():
        print(f"👤 {row['Full Name']} ({row['QIP POSITION 1ST  NAME']})")
        print(f"   ID: {row['Employee No']}")

        reasons = []

        # 출근 조건 체크
        if row.get('attendancy condition 1 - acctual working days is zero') == 'yes':
            reasons.append('실제 근무일 0일 (출근 조건 1번)')
        if row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes':
            reasons.append('무단결근 2일 초과 (출근 조건 2번)')
        if row.get('attendancy condition 3 - absent % is over 12%') == 'yes':
            reasons.append('결근율 12% 초과 (출근 조건 3번)')
        if row.get('attendancy condition 4 - minimum working days') == 'yes':
            reasons.append('최소 근무일 미달 (출근 조건 4번)')

        # AQL 조건 체크 (LINE LEADER만)
        if 'LINE' in row.get('QIP POSITION 1ST  NAME', '').upper() and 'LEADER' in row.get('QIP POSITION 1ST  NAME', '').upper():
            if row.get('aql condition 7 - team/area fail AQL') == 'yes':
                reasons.append('팀/구역 AQL 실패 (AQL 조건 7번)')
            if row.get('September AQL Failures', 0) > 0:
                reasons.append(f'9월 AQL 실패 {row["September AQL Failures"]}건')
            if row.get('Continuous_FAIL') == 'YES':
                reasons.append('3개월 연속 AQL 실패')

        # 5PRS 조건 체크
        if row.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%') == 'no':
            reasons.append('5PRS 검증 부족 또는 합격률 95% 미달')
        if row.get('5prs condition 2 - Total Valiation Qty is zero') == 'yes':
            reasons.append('5PRS 총 검증 수량 0')

        # 조건 통과율
        pass_rate = row.get('conditions_pass_rate', 0)
        if pass_rate < 100:
            passed = row.get('conditions_passed', 0)
            applicable = row.get('conditions_applicable', 0)
            reasons.append(f'조건 통과율: {passed}/{applicable} ({pass_rate:.1f}%)')

        if reasons:
            print("   🚫 실패 사유:")
            for reason in reasons:
                print(f"      - {reason}")
        else:
            print("   ❓ 실패 사유를 찾을 수 없음")

        print()

    print("=" * 60)
    print("📝 테스트 완료!")
    print("브라우저에서 다음을 확인하세요:")
    print("  1. 조직도 탭 클릭")
    print("  2. 인센티브 0인 직원 노드 클릭")
    print("  3. 모달에서 실패 사유 표시 확인")
    print("=" * 60)

if __name__ == "__main__":
    test_failure_reasons()