#!/usr/bin/env python3
"""
최소 근무일 및 실제 근무일 분석
Single Source of Truth: Excel 파일 기반 분석
"""

import pandas as pd
import json
from pathlib import Path

def analyze_working_days():
    print("=" * 80)
    print("📊 근무일 관련 데이터 분석 (Single Source of Truth)")
    print("=" * 80)

    # 1. Excel 데이터 로드
    excel_path = Path('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')
    df = pd.read_csv(excel_path, encoding='utf-8-sig')

    print(f"\n✅ Excel 파일 로드: {len(df)} 명")

    # 2. 최소 근무일 미충족 분석 (조건 4)
    print("\n1️⃣ 최소 근무일 미충족 직원 분석:")
    print("   Excel 컬럼: 'attendancy condition 4 - minimum working days'")

    if 'attendancy condition 4 - minimum working days' in df.columns:
        min_days_fail = df[df['attendancy condition 4 - minimum working days'] == 'yes']
        print(f"   최소 근무일 미충족 (yes): {len(min_days_fail)}명")

        # 샘플 데이터 출력
        if not min_days_fail.empty:
            print("\n   📋 샘플 데이터 (처음 5명):")
            for idx, row in min_days_fail.head().iterrows():
                emp_no = row['Employee No']
                name = row['Full Name']
                actual_days = row.get('actual_working_days', 0)
                print(f"     - {emp_no}: {name} - 실제 근무일: {actual_days}일")

    # 3. 실제 근무일 0일 분석
    print("\n2️⃣ 실제 근무일 0일 직원 분석:")
    print("   Excel 컬럼: 'actual_working_days'")

    if 'actual_working_days' in df.columns:
        zero_days = df[df['actual_working_days'] == 0]
        print(f"   실제 근무일 0일: {len(zero_days)}명")

        # 622021338과 623100203 확인
        specific_emps = ['622021338', '623100203']
        for emp_id in specific_emps:
            emp_data = df[df['Employee No'] == emp_id]
            if not emp_data.empty:
                row = emp_data.iloc[0]
                print(f"\n   🔍 {emp_id} 상세 정보:")
                print(f"     - 이름: {row['Full Name']}")
                print(f"     - 실제 근무일: {row['actual_working_days']}일")
                print(f"     - 출근율: {row.get('attendance_rate', 0)}%")
                print(f"     - 조건1 (근무일 0): {row.get('attendancy condition 1 - acctual working days is zero', 'no')}")
                print(f"     - 조건4 (최소 근무일): {row.get('attendancy condition 4 - minimum working days', 'no')}")
                print(f"     - 9월 인센티브: {row.get('september_incentive', 0)} VND")

        # 실제 근무일 0인 모든 직원 리스트
        print(f"\n   📋 실제 근무일 0일인 직원 전체 ({len(zero_days)}명):")
        if len(zero_days) <= 30:
            for idx, row in zero_days.iterrows():
                print(f"     - {row['Employee No']}: {row['Full Name']}")
        else:
            print(f"     (총 {len(zero_days)}명 - 처음 10명만 표시)")
            for idx, row in zero_days.head(10).iterrows():
                print(f"     - {row['Employee No']}: {row['Full Name']}")

    # 4. 조건1 (실제 근무일 0) 분석
    print("\n3️⃣ 조건1 (실제 근무일 0) 분석:")
    print("   Excel 컬럼: 'attendancy condition 1 - acctual working days is zero'")

    if 'attendancy condition 1 - acctual working days is zero' in df.columns:
        cond1_yes = df[df['attendancy condition 1 - acctual working days is zero'] == 'yes']
        print(f"   조건1 충족 못함 (yes): {len(cond1_yes)}명")

        # 실제 근무일 0과 비교
        if 'actual_working_days' in df.columns:
            actual_zero = len(df[df['actual_working_days'] == 0])
            print(f"   실제 근무일 0: {actual_zero}명")
            print(f"   차이: {abs(actual_zero - len(cond1_yes))}명")

    # 5. 출근율 88% 미만 분석
    print("\n4️⃣ 출근율 88% 미만 직원 분석:")
    print("   Excel 컬럼: 'attendance_rate'")

    if 'attendance_rate' in df.columns:
        low_attendance = df[df['attendance_rate'] < 88]
        print(f"   출근율 88% 미만: {len(low_attendance)}명")

        if not low_attendance.empty:
            print("\n   📋 출근율 분포:")
            print(f"     - 0%: {len(df[df['attendance_rate'] == 0])}명")
            print(f"     - 1-50%: {len(df[(df['attendance_rate'] > 0) & (df['attendance_rate'] < 50)])}명")
            print(f"     - 50-88%: {len(df[(df['attendance_rate'] >= 50) & (df['attendance_rate'] < 88)])}명")
            print(f"     - 88% 이상: {len(df[df['attendance_rate'] >= 88])}명")

    # 6. 구역 AQL Reject Rate 분석
    print("\n5️⃣ 구역 AQL Reject Rate 3% 초과 분석:")
    print("   Excel 컬럼: 'area_reject_rate'")

    if 'area_reject_rate' in df.columns:
        area_reject_over3 = df[df['area_reject_rate'] > 3]
        print(f"   구역 Reject Rate 3% 초과: {len(area_reject_over3)}명")

        # 조건7과 비교
        if 'aql condition 7 - team/area fail AQL' in df.columns:
            cond7_yes = df[df['aql condition 7 - team/area fail AQL'] == 'yes']
            print(f"   조건7 충족 못함 (yes): {len(cond7_yes)}명")

    # 7. 메타데이터와 비교
    print("\n6️⃣ 메타데이터와 비교:")
    metadata_path = Path('output_files/output_QIP_incentive_september_2025_metadata.json')
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        if 'condition_statistics' in metadata:
            stats = metadata['condition_statistics']
            print("   메타데이터 통계:")
            for cond_name, cond_stats in stats.items():
                if 'failed_count' in cond_stats:
                    print(f"     - {cond_name}: {cond_stats['failed_count']}명 실패")

    print("\n" + "=" * 80)
    print("📊 분석 결과 요약:")
    print("=" * 80)
    print("\n🔍 Single Source of Truth 원칙:")
    print("   - 모든 데이터는 Excel 파일에서 직접 가져옴")
    print("   - 가짜 데이터 생성 없음")
    print("   - Excel 컬럼명과 정확히 일치하는 필드 사용")

    return df

if __name__ == "__main__":
    df = analyze_working_days()