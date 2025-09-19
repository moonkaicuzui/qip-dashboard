#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모달 수정 사항 구현 검증 스크립트
"""

import pandas as pd
import os

def verify_modal_implementation():
    """모달 수정 사항 구현 확인"""

    print("=" * 60)
    print("🔍 모달 수정 사항 구현 검증")
    print("=" * 60)
    print()

    # 1. CSV 데이터 확인
    print("📁 CSV 데이터 분석...")
    csv_path = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        print(f"  - 전체 직원 수: {len(df)}명")
        print(f"  - 컬럼 수: {len(df.columns)}개")
        print()

        # 2. 주요 문제점 확인
        print("🔍 주요 이슈 확인...")

        # A.MANAGER 찾기
        a_managers = df[df['QIP POSITION 1ST  NAME'].str.contains('A.MANAGER|ASSISTANT', case=False, na=False)]
        print(f"\n1. A.MANAGER 직원:")
        for _, mgr in a_managers.iterrows():
            print(f"   - {mgr['Full Name']} (ID: {mgr['Employee No']})")
            print(f"     Boss ID: {mgr.get('Direct Manager ID', 'N/A')}")
            print(f"     Incentive: ₫{mgr.get('September_Incentive', 0):,.0f}")

        # 0 인센티브 LINE LEADER 찾기
        line_leaders_zero = df[
            (df['QIP POSITION 1ST  NAME'].str.contains('LINE LEADER', case=False, na=False)) &
            (df['September_Incentive'] == 0) &
            (df['ROLE TYPE STD'] == 'TYPE-1')
        ]

        print(f"\n2. 0 인센티브 LINE LEADER:")
        for _, ll in line_leaders_zero.head(3).iterrows():
            print(f"   - {ll['Full Name']} (ID: {ll['Employee No']})")

            # 실패 조건 분석
            reasons = []
            if ll.get('Working Days', 0) == 0:
                reasons.append("출근일 0일")
            if ll.get('condition_1_met') == False:
                reasons.append("출근 조건 1번")
            if ll.get('condition_2_met') == False:
                reasons.append("출근 조건 2번")
            if ll.get('condition_3_met') == False:
                reasons.append("AQL 조건")
            if ll.get('condition_4_met') == False:
                reasons.append("5PRS 조건")

            if reasons:
                print(f"     실패 사유: {', '.join(reasons)} 미충족")

        # SUPERVISOR/GROUP LEADER 계산 검증
        print(f"\n3. SUPERVISOR/GROUP LEADER 예상 vs 실제:")

        supervisors = df[df['QIP POSITION 1ST  NAME'].str.contains('SUPERVISOR', case=False, na=False)]
        for _, sup in supervisors.head(2).iterrows():
            sup_id = str(sup['Employee No'])
            actual = sup.get('September_Incentive', 0)

            # 팀 LINE LEADER 찾기 (재귀적)
            team_line_leaders = []

            def find_team_line_leaders(mgr_id, visited=None):
                if visited is None:
                    visited = set()
                if mgr_id in visited:
                    return []
                visited.add(mgr_id)

                result = []
                # 직접 부하 찾기
                subs = df[df['Direct Manager ID'] == mgr_id]
                for _, sub in subs.iterrows():
                    pos = sub['QIP POSITION 1ST  NAME'] or ''
                    if 'LINE' in pos.upper() and 'LEADER' in pos.upper() and sub['ROLE TYPE STD'] == 'TYPE-1':
                        result.append(sub)
                    # 재귀 탐색
                    result.extend(find_team_line_leaders(str(sub['Employee No']), visited))
                return result

            team_ll = find_team_line_leaders(sup_id)
            receiving_ll = [ll for ll in team_ll if ll['September_Incentive'] > 0]

            if receiving_ll:
                avg_ll = sum(ll['September_Incentive'] for ll in receiving_ll) / len(receiving_ll)
                expected = avg_ll * 2.5  # SUPERVISOR 배수
            else:
                expected = 0

            match = "✅" if abs(actual - expected) < 1000 else "❌"
            print(f"   - {sup['Full Name']}")
            print(f"     팀 LINE LEADER: {len(team_ll)}명 (수령: {len(receiving_ll)}명)")
            print(f"     예상: ₫{expected:,.0f}")
            print(f"     실제: ₫{actual:,.0f} {match}")

        print("\n=" * 60)
        print("📝 테스트 포인트:")
        print("  1. 대시보드를 열고 조직도 탭 클릭")
        print("  2. A.MANAGER 노드 클릭 → 모달이 열리는지")
        print("  3. 0 인센티브 직원 클릭 → 실패 사유 표시")
        print("  4. SUPERVISOR/GROUP LEADER → 금액 일치 확인")
        print("  5. 모달 외부 클릭/ESC → 정상 닫힘")
        print("=" * 60)

    else:
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")

if __name__ == "__main__":
    verify_modal_implementation()