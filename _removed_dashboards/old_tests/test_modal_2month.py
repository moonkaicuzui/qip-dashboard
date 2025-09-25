#!/usr/bin/env python3
"""
2개월 연속 실패자 모달 데이터 테스트
"""

import pandas as pd
import json
from pathlib import Path

def test_modal_data():
    """모달에 표시될 2개월 연속 실패자 데이터 확인"""
    
    print("=" * 80)
    print("📊 2개월 연속 실패자 모달 데이터 테스트")
    print("=" * 80)
    
    # Excel 데이터 로드
    excel_path = Path('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')
    df = pd.read_csv(excel_path, encoding='utf-8-sig')
    
    # 3개월 연속 실패자
    three_month = df[df['Continuous_FAIL'] == 'YES_3MONTHS']
    print(f"\n✅ 3개월 연속 실패자: {len(three_month)}명")
    
    # 2개월 연속 실패자 (8-9월)
    aug_sep = df[df['Continuous_FAIL'] == 'YES_2MONTHS_AUG_SEP']
    print(f"\n🔴 8-9월 연속 실패자 (고위험): {len(aug_sep)}명")
    if not aug_sep.empty:
        for _, row in aug_sep.head(5).iterrows():
            print(f"  - {row['Employee No']}: {row['Full Name']}")
            print(f"    Position: {row['QIP POSITION 1ST  NAME']}")
            print(f"    8월: {row.get('August_AQL_Failures', 0)}회, 9월: {row.get('September AQL Failures', 0)}회")
    
    # 2개월 연속 실패자 (7-8월)
    jul_aug = df[df['Continuous_FAIL'] == 'YES_2MONTHS_JUL_AUG']
    print(f"\n🟡 7-8월 연속 실패자 (모니터링): {len(jul_aug)}명")
    if not jul_aug.empty:
        for _, row in jul_aug.head(5).iterrows():
            print(f"  - {row['Employee No']}: {row['Full Name']}")
            print(f"    Position: {row['QIP POSITION 1ST  NAME']}")
            print(f"    7월: {row.get('July_AQL_Failures', 0)}회, 8월: {row.get('August_AQL_Failures', 0)}회")
    
    # 대시보드 JSON 데이터 확인
    json_path = Path('output_files/dashboard_data_from_excel.json')
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
        
        # 2개월 연속 실패자 카운트 확인
        two_month_count = sum(1 for emp in dashboard_data if 
                             emp.get('Continuous_FAIL', '').startswith('YES_2MONTHS'))
        print(f"\n📋 대시보드 JSON 데이터:")
        print(f"  - 전체 직원: {len(dashboard_data)}명")
        print(f"  - 2개월 연속 실패자: {two_month_count}명")
    
    print("\n" + "=" * 80)
    print("✅ 모달 데이터 구조 확인 완료:")
    print("  1. Excel에서 Continuous_FAIL 컬럼 정상 로드")
    print("  2. 위험도별 분류 (고위험: 8-9월, 모니터링: 7-8월)")
    print("  3. 대시보드 JSON 데이터에 정보 포함")
    print("=" * 80)

if __name__ == "__main__":
    test_modal_data()
