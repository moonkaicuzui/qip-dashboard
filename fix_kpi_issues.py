#!/usr/bin/env python3
"""
KPI 데이터 문제 분석 및 수정
Single Source of Truth: Excel 파일 기반
"""

import pandas as pd
import json
from pathlib import Path

def analyze_and_fix_kpi_issues():
    print("=" * 80)
    print("📊 KPI 문제 분석 및 수정")
    print("=" * 80)

    # Excel 데이터 로드
    excel_path = Path('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')
    df = pd.read_csv(excel_path, encoding='utf-8-sig')

    print(f"\n✅ Excel 파일 로드: 총 {len(df)}명")

    # ========== 문제 1: 최소 근무일 미충족 (condition4) ==========
    print("\n" + "=" * 80)
    print("1️⃣ 최소 근무일 미충족 분석")
    print("=" * 80)

    # 초기화
    cond4_fail = pd.DataFrame()
    cond4_pass = pd.DataFrame()
    zero_days_df = pd.DataFrame()

    # condition4 분석
    if 'attendancy condition 4 - minimum working days' in df.columns:
        # condition4가 'yes'인 경우 = 조건 충족 못함 (FAIL)
        # condition4가 'no'인 경우 = 조건 충족 (PASS)
        cond4_fail = df[df['attendancy condition 4 - minimum working days'] == 'yes']
        cond4_pass = df[df['attendancy condition 4 - minimum working days'] == 'no']

        print(f"\n📊 Excel 데이터 분석:")
        print(f"  - condition4 = 'yes' (미충족/FAIL): {len(cond4_fail)}명")
        print(f"  - condition4 = 'no' (충족/PASS): {len(cond4_pass)}명")

        # JavaScript는 condition4 === 'no'를 찾고 있음 (잘못된 로직)
        print(f"\n⚠️ 문제 발견:")
        print(f"  - JavaScript는 condition4 === 'no'를 최소 근무일 미충족으로 계산")
        print(f"  - 실제로는 condition4 === 'yes'가 미충족을 의미")
        print(f"  - 현재 표시: {len(cond4_pass)}명 (잘못됨)")
        print(f"  - 정확한 수: {len(cond4_fail)}명 (condition4 === 'yes')")

    # 622021338과 623100203 확인
    print("\n📋 특정 직원 확인:")
    specific_emps = ['622021338', '623100203']
    for emp_id in specific_emps:
        emp_data = df[df['Employee No'] == emp_id]
        if not emp_data.empty:
            row = emp_data.iloc[0]
            print(f"\n  {emp_id}: {row['Full Name']}")
            print(f"    - Actual Working Days: {row['Actual Working Days']}")
            print(f"    - condition4: {row['attendancy condition 4 - minimum working days']}")
            print(f"    - Type: {row['type']}")

    # ========== 문제 2: 실제 근무일 0일 ==========
    print("\n" + "=" * 80)
    print("2️⃣ 실제 근무일 0일 분석")
    print("=" * 80)

    if 'Actual Working Days' in df.columns:
        zero_days_df = df[df['Actual Working Days'] == 0]
        print(f"\n📊 Excel 데이터:")
        print(f"  - Actual Working Days = 0: {len(zero_days_df)}명")

        # condition1과 비교
        if 'attendancy condition 1 - acctual working days is zero' in df.columns:
            cond1_yes = df[df['attendancy condition 1 - acctual working days is zero'] == 'yes']
            print(f"  - condition1 = 'yes' (근무일 0): {len(cond1_yes)}명")

            # 차이 분석
            if len(zero_days_df) != len(cond1_yes):
                print(f"\n⚠️ 불일치 발견:")
                print(f"  - Actual Working Days = 0: {len(zero_days_df)}명")
                print(f"  - condition1 = 'yes': {len(cond1_yes)}명")
                print(f"  - 차이: {abs(len(zero_days_df) - len(cond1_yes))}명")

    # JavaScript는 actual_working_days 필드를 사용
    print("\n📊 JavaScript 필드 매핑 확인:")
    print("  - JavaScript: emp['actual_working_days'] || 0")
    print("  - Excel: 'Actual Working Days' 컬럼")
    print("  - Python은 'actual_working_days'로 매핑해야 함")

    # ========== 문제 3: 구역 AQL Reject Rate ==========
    print("\n" + "=" * 80)
    print("3️⃣ 구역 AQL Reject Rate 3% 초과")
    print("=" * 80)

    above_3_percent = pd.DataFrame()  # 초기화
    above_065_percent = pd.DataFrame()  # 초기화

    if 'area_reject_rate' in df.columns:
        # 3% 초과 직원
        above_3_percent = df[df['area_reject_rate'] > 3]
        print(f"\n📊 Excel 데이터:")
        print(f"  - area_reject_rate > 3%: {len(above_3_percent)}명")

        # 현재 JavaScript는 0.65% 사용 중
        above_065_percent = df[df['area_reject_rate'] > 0.65]
        print(f"  - area_reject_rate > 0.65% (현재 기준): {len(above_065_percent)}명")
    else:
        print("\n⚠️ area_reject_rate 컬럼이 없음")

    # ========== 문제 4: 출근율 88% 미만 ==========
    print("\n" + "=" * 80)
    print("4️⃣ 출근율 88% 미만 (새로운 KPI)")
    print("=" * 80)

    below_88 = pd.DataFrame()  # 초기화

    if 'attendance_rate' in df.columns:
        below_88 = df[df['attendance_rate'] < 88]
        print(f"\n📊 Excel 데이터:")
        print(f"  - attendance_rate < 88%: {len(below_88)}명")

        # 상세 분포
        print("\n📊 출근율 분포:")
        print(f"  - 0%: {len(df[df['attendance_rate'] == 0])}명")
        print(f"  - 1-50%: {len(df[(df['attendance_rate'] > 0) & (df['attendance_rate'] < 50)])}명")
        print(f"  - 50-88%: {len(df[(df['attendance_rate'] >= 50) & (df['attendance_rate'] < 88)])}명")
        print(f"  - 88% 이상: {len(df[df['attendance_rate'] >= 88])}명")
    else:
        print("\n⚠️ attendance_rate 컬럼이 없음")

    # ========== 수정 사항 요약 ==========
    print("\n" + "=" * 80)
    print("🔧 필요한 수정 사항")
    print("=" * 80)

    fixes = [
        {
            "issue": "최소 근무일 미충족 로직",
            "current": "condition4 === 'no'를 미충족으로 계산",
            "fix": "condition4 === 'yes'로 변경",
            "impact": f"{len(cond4_pass)}명 → {len(cond4_fail)}명"
        },
        {
            "issue": "실제 근무일 0일 필드명",
            "current": "actual_working_days (소문자)",
            "fix": "Actual Working Days도 지원",
            "impact": f"정확한 {len(zero_days_df)}명 표시"
        },
        {
            "issue": "구역 AQL Reject Rate",
            "current": "> 0.65%",
            "fix": "> 3%로 변경",
            "impact": f"{len(above_065_percent)}명 → {len(above_3_percent)}명"
        },
        {
            "issue": "출근율 88% 미만 KPI",
            "current": "없음",
            "fix": "새 KPI 카드 추가",
            "impact": f"{len(below_88)}명 표시"
        }
    ]

    for i, fix in enumerate(fixes, 1):
        print(f"\n{i}. {fix['issue']}:")
        print(f"   현재: {fix['current']}")
        print(f"   수정: {fix['fix']}")
        print(f"   영향: {fix['impact']}")

    print("\n" + "=" * 80)
    print("✅ Single Source of Truth 준수:")
    print("  - 모든 데이터는 Excel 파일 기준")
    print("  - 가짜 데이터 생성 없음")
    print("  - Excel 컬럼명과 일치하는 필드 사용")
    print("=" * 80)

    return df

if __name__ == "__main__":
    df = analyze_and_fix_kpi_issues()