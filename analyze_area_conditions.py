#!/usr/bin/env python3
"""
조건 7번(팀/구역 AQL 연속 실패)과 8번(구역 reject rate 3% 초과) 분석
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_area_conditions():
    """구역별 AQL 조건 분석"""

    print("=" * 80)
    print("🔍 조건 7번과 8번 분석: 구역별 AQL 상태")
    print("=" * 80)

    # Excel 데이터 로드
    csv_path = Path("output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_enhanced.csv")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    # 활성 직원만 필터링 (9월 기준)
    # Include_In_Dashboard 컬럼이 있으면 사용, 없으면 전체 사용
    if 'Include_In_Dashboard' in df.columns:
        # boolean True 또는 문자열 'Y' 모두 처리
        df_active = df[(df['Include_In_Dashboard'] == True) | (df['Include_In_Dashboard'] == 'Y')].copy()
    else:
        # September_Active가 있으면 사용
        if 'September_Active' in df.columns:
            df_active = df[df['September_Active'] == 'Y'].copy()
        else:
            df_active = df.copy()

    print(f"\n📊 전체 활성 직원: {len(df_active)}명")

    # 구역 매핑 (Building 정보 사용)
    area_mapping = {
        'A': 'Building A',
        'B': 'Building B',
        'C': 'Building C',
        'D': 'Building D',
        'All': 'All Buildings',
        'B & Repacking': 'Building B & Repacking'
    }

    # 각 직원의 구역 할당
    for idx, row in df_active.iterrows():
        building = row.get('AQL_Building', '')
        if pd.notna(building) and building:
            area = area_mapping.get(building, f'Building {building}')
            df_active.at[idx, 'Area'] = area
        else:
            df_active.at[idx, 'Area'] = 'Unknown'

    # 조건 7번: 팀/구역 AQL 연속 실패 (3개월)
    print("\n📌 조건 7번: 팀/구역 AQL 3개월 연속 실패")
    print("-" * 40)

    cond7_fail = df_active[df_active['cond_7_aql_team_area'] == 'FAIL']
    print(f"조건 7번 미충족 직원: {len(cond7_fail)}명")

    if len(cond7_fail) > 0:
        print("\n조건 7번 미충족 직원 목록:")
        for idx, row in cond7_fail.iterrows():
            print(f"  - {row['Employee No']}: {row['Full Name']} ({row.get('Area', 'Unknown')})")

    # 조건 8번: 구역 reject rate > 3%
    print("\n📌 조건 8번: 구역 reject rate 3% 초과")
    print("-" * 40)

    # 구역별 AQL 통계 계산
    area_stats = {}

    # Area 컬럼이 존재하는지 확인
    if 'Area' not in df_active.columns:
        print("⚠️ Area 컬럼이 없습니다. 구역별 통계를 생성할 수 없습니다.")
        return {'cond7_fail': 0, 'cond8_fail': 0, 'area_stats': {}}

    for area in df_active['Area'].unique():
        area_df = df_active[df_active['Area'] == area]

        # AQL 테스트 데이터 합산
        total_tests = area_df['AQL_Total_Tests'].sum() if 'AQL_Total_Tests' in area_df.columns else 0
        total_pass = area_df['AQL_Pass_Count'].sum() if 'AQL_Pass_Count' in area_df.columns else 0
        # FAIL 건수 계산: Total - Pass
        total_fail = total_tests - total_pass if total_tests > 0 else 0

        # Reject rate 계산
        reject_rate = (total_fail / total_tests * 100) if total_tests > 0 else 0

        # 해당 구역 직원 중 조건 8번 미충족자
        cond8_fail_in_area = area_df[
            (area_df['cond_8_area_reject'] == 'FAIL') |
            (area_df['Area_Reject_Rate'] > 3)
        ]

        area_stats[area] = {
            'total_employees': len(area_df),
            'total_pass_tests': int(total_pass),
            'total_fail_tests': int(total_fail),
            'total_tests': int(total_tests),
            'reject_rate': round(reject_rate, 2),
            'cond8_fail_count': len(cond8_fail_in_area),
            'exceeds_3pct': reject_rate > 3
        }

    # 구역별 통계 출력
    print("\n구역별 AQL 통계:")
    print(f"{'구역':<20} {'직원수':<10} {'총테스트':<12} {'PASS':<12} {'FAIL':<12} {'Reject%':<10} {'3%초과':<10}")
    print("-" * 100)

    for area, stats in sorted(area_stats.items()):
        status = "⚠️ 초과" if stats['exceeds_3pct'] else "✅ 정상"
        print(f"{area:<20} {stats['total_employees']:<10} {stats['total_tests']:<12} "
              f"{stats['total_pass_tests']:<12} {stats['total_fail_tests']:<12} "
              f"{stats['reject_rate']:<10.2f} {status:<10}")

    # 조건 8번 미충족 인원 상세
    cond8_fail = df_active[
        (df_active['cond_8_area_reject'] == 'FAIL') |
        (df_active['Area_Reject_Rate'] > 3)
    ]

    print(f"\n조건 8번 미충족 직원: {len(cond8_fail)}명")

    if len(cond8_fail) > 0:
        print("\n조건 8번 미충족 직원 목록 (상위 10명):")
        for idx, row in cond8_fail.head(10).iterrows():
            area = row.get('Area', 'Unknown')
            reject_rate = row.get('Area_Reject_Rate', 0)
            print(f"  - {row['Employee No']}: {row['Full Name']} ({area}, Reject: {reject_rate:.2f}%)")

    # 요약
    print("\n" + "=" * 80)
    print("📊 요약:")
    print("=" * 80)

    total_affected = len(cond7_fail) + len(cond8_fail)
    print(f"""
- 조건 7번 (팀/구역 연속 실패) 미충족: {len(cond7_fail)}명
- 조건 8번 (구역 reject > 3%) 미충족: {len(cond8_fail)}명
- 전체 영향받은 직원: {total_affected}명

구역별 3% 초과 현황:""")

    for area, stats in area_stats.items():
        if stats['exceeds_3pct']:
            print(f"  • {area}: {stats['reject_rate']:.2f}% (직원 {stats['total_employees']}명)")

    return {
        'cond7_fail': len(cond7_fail),
        'cond8_fail': len(cond8_fail),
        'area_stats': area_stats
    }

if __name__ == "__main__":
    result = analyze_area_conditions()