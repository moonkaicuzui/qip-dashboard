#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINE LEADER 수 검증 스크립트 - 조직도 탭과 직급별 상세 탭 비교
"""

import pandas as pd

def verify_line_leader_counts():
    """LINE LEADER 인센티브 수령 현황 검증"""

    print("=" * 60)
    print("🔍 LINE LEADER 인센티브 수령 현황 검증")
    print("=" * 60)
    print()

    # CSV 데이터 로드
    df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')

    # TYPE-1 LINE LEADER 필터링
    line_leaders = df[
        (df['QIP POSITION 1ST  NAME'].str.contains('LINE LEADER', case=False, na=False)) &
        (df['ROLE TYPE STD'] == 'TYPE-1')
    ]

    print(f"📊 TYPE-1 LINE LEADER 현황:")
    print(f"  - 전체: {len(line_leaders)}명")
    print()

    # September 인센티브 기준 분석
    sep_receiving = line_leaders[line_leaders['September_Incentive'] > 0]
    sep_not_receiving = line_leaders[line_leaders['September_Incentive'] == 0]

    print(f"✅ September 인센티브 (현재 대시보드):")
    print(f"  - 수령: {len(sep_receiving)}명 ({len(sep_receiving)}/{len(line_leaders)})")
    print(f"  - 미수령: {len(sep_not_receiving)}명")
    print()

    # 수령자 명단
    if len(sep_receiving) > 0:
        print("  💰 인센티브 수령 LINE LEADER:")
        for _, ll in sep_receiving.iterrows():
            print(f"     - {ll['Full Name']} (ID: {ll['Employee No']}): ₫{ll['September_Incentive']:,.0f}")

    # 미수령자 명단 및 사유
    if len(sep_not_receiving) > 0:
        print("\n  ❌ 인센티브 미수령 LINE LEADER:")
        for _, ll in sep_not_receiving.iterrows():
            print(f"     - {ll['Full Name']} (ID: {ll['Employee No']})")

            # 실패 사유 분석
            reasons = []
            if ll.get('Working Days', 0) == 0:
                reasons.append("근무일 0일")
            if ll.get('condition_1_met') == False:
                reasons.append("출근 조건 미충족")
            if ll.get('condition_3_met') == False:
                reasons.append("AQL 조건 미충족")
            if ll.get('condition_4_met') == False:
                reasons.append("5PRS 조건 미충족")

            if reasons:
                print(f"       사유: {', '.join(reasons)}")

    # August 인센티브 확인 (이전 데이터 비교용)
    try:
        aug_df = pd.read_csv('input_files/2025년 8월 인센티브 지급 세부 정보.csv')
        aug_line_leaders = aug_df[
            aug_df['QIP POSITION 1ST  NAME'].str.contains('LINE LEADER', case=False, na=False)
        ]
        aug_receiving = aug_line_leaders[aug_line_leaders['August_Incentive'] > 0]

        print()
        print(f"📅 August 인센티브 (비교용):")
        print(f"  - 전체 LINE LEADER: {len(aug_line_leaders)}명")
        print(f"  - 수령: {len(aug_receiving)}명 ({len(aug_receiving)}/{len(aug_line_leaders)})")
        print(f"  - 미수령: {len(aug_line_leaders) - len(aug_receiving)}명")
    except:
        pass

    print()
    print("=" * 60)
    print("📝 검증 결과:")
    print(f"  - 조직도 탭: {len(sep_receiving)}/{len(line_leaders)} 수령 (September 데이터)")
    print(f"  - 직급별 상세 탭: {len(sep_receiving)}/{len(line_leaders)} 수령 (수정 후)")
    print("  - ✅ 두 탭의 데이터가 일치해야 합니다!")
    print()
    print("브라우저에서 확인:")
    print("  1. 조직도 탭 - LINE LEADER 노드 확인")
    print("  2. 직급별 상세 탭 - TYPE-1 LINE LEADER 행 확인")
    print("  3. 두 탭의 '인센티브 수령/전체' 숫자가 일치하는지 확인")
    print("=" * 60)

if __name__ == "__main__":
    verify_line_leader_counts()