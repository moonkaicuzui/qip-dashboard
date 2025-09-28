#!/usr/bin/env python3
"""소스 CSV의 September_Incentive 칼럼 확인"""

import pandas as pd

# 소스 CSV 로드
source = pd.read_csv("input_files/2025년 9월 인센티브 지급 세부 정보.csv", encoding="utf-8-sig")

print("=== 소스 CSV 칼럼 목록 (incentive 관련) ===")
for col in source.columns:
    if "incentive" in col.lower() or "september" in col.lower():
        print(f"  {col}")

# September_Incentive가 이미 있고 0이 아닌 값들 확인
if "September_Incentive" in source.columns:
    non_zero = source[source["September_Incentive"] != 0]
    print(f"\nSeptember_Incentive != 0인 행: {len(non_zero)}개")

    # 전체 통계
    total_rows = len(source)
    zero_rows = len(source[source["September_Incentive"] == 0])
    print(f"\n전체: {total_rows}행")
    print(f"0인 행: {zero_rows}개")
    print(f"0이 아닌 행: {non_zero.shape[0]}개")

    # 몇 개 샘플 출력
    if len(non_zero) > 0:
        print("\n0이 아닌 샘플 (처음 3개):")
        for idx, row in non_zero.head(3).iterrows():
            print(f"  {row['Employee No']} | {row['Full Name'][:20]:20} | September_Incentive: {row['September_Incentive']:,.0f}")

    # ĐINH KIM NGOAN 확인
    ngoan = source[source['Employee No'] == '617100049']
    if not ngoan.empty:
        print(f"\nĐINH KIM NGOAN:")
        print(f"  September_Incentive: {ngoan.iloc[0]['September_Incentive']}")
        print(f"  Final Incentive amount: {ngoan.iloc[0]['Final Incentive amount']}")
else:
    print("\n❌ September_Incentive 칼럼이 소스 CSV에 없음")

# Final Incentive amount도 확인
if "Final Incentive amount" in source.columns:
    final_non_zero = source[source["Final Incentive amount"] != 0]
    print(f"\n=== Final Incentive amount 분석 ===")
    print(f"0이 아닌 행: {len(final_non_zero)}개")

    # September와 Final 비교
    if "September_Incentive" in source.columns:
        diff = source[source["September_Incentive"] != source["Final Incentive amount"]]
        print(f"September != Final인 행: {len(diff)}개")