#!/usr/bin/env python3
"""
100% 조건 충족하지 못한 직원들의 인센티브 제거
- 100% 미만 충족자는 인센티브 0으로 설정
- Final_Incentive_Status를 'no'로 변경
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("🔧 100% 미충족자 인센티브 제거")
print("="*80)
print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. CSV 파일 로드
csv_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
df = pd.read_csv(csv_file)
print(f"✅ CSV 파일 로드: {len(df)}명")

# 2. 현재 상태 확인
print("\n[1] 수정 전 상태")
print("-" * 40)

# 100% 충족자
perfect = df[df['conditions_pass_rate'] == 100]
print(f"100% 조건 충족: {len(perfect)}명")

# 100% 미만인데 인센티브 받는 사람 (문제!)
imperfect_paid = df[(df['conditions_pass_rate'] < 100) & (df['September_Incentive'] > 0)]
print(f"❌ 100% 미만인데 인센티브 받는 사람: {len(imperfect_paid)}명")

if len(imperfect_paid) > 0:
    total_wrong_amount = imperfect_paid['September_Incentive'].sum()
    print(f"   잘못 지급된 총액: {total_wrong_amount:,.0f} VND")
    print("\n   제거 대상자 명단:")
    for idx, row in imperfect_paid.iterrows():
        print(f"   - {row['Full Name']:30s} ({row['QIP POSITION 1ST  NAME']:25s}): {row['conditions_pass_rate']:5.1f}% → {row['September_Incentive']:,.0f} VND")

# 3. 인센티브 제거
print("\n[2] 인센티브 제거 작업")
print("-" * 40)

# 100% 미만 충족자의 인센티브를 0으로
removed_count = 0
for idx in imperfect_paid.index:
    # 인센티브 제거
    df.loc[idx, 'September_Incentive'] = 0
    df.loc[idx, 'Final Incentive amount'] = 0
    df.loc[idx, 'Final_Incentive_Status'] = 'no'
    # Continuous_Months도 리셋
    df.loc[idx, 'Continuous_Months'] = 0
    removed_count += 1

print(f"✅ {removed_count}명의 인센티브 제거 완료")

# 4. 수정 후 검증
print("\n[3] 수정 후 검증")
print("-" * 40)

# 100% 충족하고 인센티브 받는 사람
perfect_paid = df[(df['conditions_pass_rate'] == 100) & (df['September_Incentive'] > 0)]
print(f"✅ 100% 충족 + 인센티브 지급: {len(perfect_paid)}명")

# 100% 미만인데 인센티브 받는 사람 (이제 없어야 함)
imperfect_paid_after = df[(df['conditions_pass_rate'] < 100) & (df['September_Incentive'] > 0)]
if len(imperfect_paid_after) == 0:
    print("✅ 100% 미만 충족자 인센티브 모두 제거됨")
else:
    print(f"❌ 아직 {len(imperfect_paid_after)}명이 잘못 인센티브 받고 있음!")

# 최종 통계
paid_employees = len(df[df['Final_Incentive_Status'] == 'yes'])
total_amount = df[df['Final_Incentive_Status'] == 'yes']['September_Incentive'].sum()

print(f"\n최종 인센티브 지급 현황:")
print(f"  - 지급 인원: {paid_employees}명 (100% 조건 충족자만)")
print(f"  - 총 지급액: {total_amount:,.0f} VND")

# 5. 파일 저장
print("\n[4] 파일 저장")
print("-" * 40)

# CSV 저장
df.to_csv(csv_file, index=False)
print(f"✅ CSV 파일 업데이트: {csv_file}")

# Excel 저장
excel_file = csv_file.replace('.csv', '.xlsx')
df.to_excel(excel_file, index=False)
print(f"✅ Excel 파일 업데이트: {excel_file}")

# 6. 직책별 최종 현황
print("\n[5] 직책별 지급 현황 (100% 충족자만)")
print("-" * 40)

position_summary = df[df['Final_Incentive_Status'] == 'yes'].groupby('QIP POSITION 1ST  NAME').agg({
    'Employee No': 'count',
    'September_Incentive': 'sum'
}).rename(columns={'Employee No': '지급인원', 'September_Incentive': '총지급액'})

position_summary = position_summary.sort_values('총지급액', ascending=False)
print(position_summary.head(10))

print("\n" + "="*80)
print("✅ 100% 조건 충족자만 인센티브 받도록 수정 완료!")
print("="*80)