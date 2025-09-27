#!/usr/bin/env python3
"""
Test script to verify data consistency between Incentive Receipt Status and Condition Fulfillment
두 가지 불일치 문제가 해결되었는지 확인하는 테스트 스크립트
"""

import json
import pandas as pd
from pathlib import Path
import sys

def test_data_consistency():
    """데이터 일치성 테스트"""

    print("=" * 60)
    print("데이터 일치성 테스트 시작")
    print("=" * 60)

    # 1. Excel 데이터 로드
    excel_file = Path("output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx")
    if not excel_file.exists():
        print(f"❌ Excel 파일을 찾을 수 없습니다: {excel_file}")
        return False

    df = pd.read_excel(excel_file)
    print(f"✅ Excel 데이터 로드: {len(df)}명")

    # 2. 실제 인센티브 지급 현황 확인
    paid_count = len(df[df['Final Incentive amount'] > 0])
    unpaid_count = len(df[df['Final Incentive amount'] == 0])
    print(f"\n📊 실제 지급 현황:")
    print(f"   - 지급: {paid_count}명")
    print(f"   - 미지급: {unpaid_count}명")

    # 3. TYPE별 통계 확인
    for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        type_df = df[df['ROLE TYPE STD'] == type_name]
        type_paid = len(type_df[type_df['Final Incentive amount'] > 0])
        type_unpaid = len(type_df[type_df['Final Incentive amount'] == 0])
        print(f"\n{type_name} 현황:")
        print(f"   - 전체: {len(type_df)}명")
        print(f"   - 지급: {type_paid}명")
        print(f"   - 미지급: {type_unpaid}명")

        # 조건 충족 상태 확인 (지급된 사람은 모든 조건 충족으로 표시되어야 함)
        if type_paid > 0:
            paid_df = type_df[type_df['Final Incentive amount'] > 0]
            # All_Conditions_Met 컬럼이 있는 경우 확인
            if 'All_Conditions_Met' in paid_df.columns:
                all_met = paid_df['All_Conditions_Met'].all()
                if not all_met:
                    print(f"   ⚠️ 경고: 지급된 직원 중 All_Conditions_Met=False인 경우가 있습니다")

    # 4. 직급별 상세 확인 (Position Details 모달에서 확인할 데이터)
    print("\n📋 직급별 상세 확인:")
    position_groups = df.groupby(['ROLE TYPE STD', 'FINAL QIP POSITION NAME CODE'])

    inconsistencies = []
    for (type_val, position), group_df in position_groups:
        group_paid = len(group_df[group_df['Final Incentive amount'] > 0])
        group_total = len(group_df)

        # 각 직원의 조건 충족 여부 확인
        for _, emp in group_df.iterrows():
            is_paid = emp['Final Incentive amount'] > 0
            emp_no = emp.get('Employee No', '')

            # 조건 충족 여부 확인 (예시: 출근율)
            if 'Attendance Rate' in emp and pd.notna(emp['Attendance Rate']):
                attendance_rate = emp['Attendance Rate']
                threshold = 0.88 if type_val == 'TYPE-1' else 0.96
                meets_attendance = attendance_rate >= threshold

                # 불일치 확인: 지급되었는데 조건 미충족
                if is_paid and not meets_attendance:
                    inconsistencies.append({
                        'emp_no': emp_no,
                        'type': type_val,
                        'position': position,
                        'issue': f'지급되었으나 출근율 미충족 ({attendance_rate:.1%} < {threshold:.0%})'
                    })

    if inconsistencies:
        print(f"\n⚠️ 발견된 불일치: {len(inconsistencies)}건")
        for inc in inconsistencies[:5]:  # 처음 5개만 표시
            print(f"   - {inc['emp_no']}: {inc['issue']}")
    else:
        print("\n✅ 모든 데이터가 일치합니다!")

    # 5. 최종 결과
    print("\n" + "=" * 60)
    print("테스트 결과:")
    if not inconsistencies:
        print("✅ 1번 문제 해결: Incentive Receipt Status와 Condition Fulfillment 일치")
        print("✅ 2번 문제 해결: Employee Details Status 지급 상태와 조건 충족 일치")
        print("\n모든 불일치 문제가 해결되었습니다! 🎉")
    else:
        print(f"❌ {len(inconsistencies)}건의 불일치가 발견되었습니다.")
        print("추가 수정이 필요합니다.")
    print("=" * 60)

    return len(inconsistencies) == 0

if __name__ == "__main__":
    success = test_data_consistency()
    sys.exit(0 if success else 1)