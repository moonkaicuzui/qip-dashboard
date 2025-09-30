#!/usr/bin/env python3
"""
Final_Incentive_Status 필드 수정
- September_Incentive > 0인 직원들의 Final_Incentive_Status를 'yes'로 설정
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("🔧 FIXING FINAL_INCENTIVE_STATUS FIELD")
print("="*80)
print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. CSV 파일 로드
csv_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
df = pd.read_csv(csv_file)
print(f"✅ CSV 파일 로드: {len(df)}명")

# 2. 현재 상태 확인
print("\n[1] 현재 상태 분석")
print("-" * 40)

has_incentive = df[df['September_Incentive'] > 0]
has_status_yes = df[df['Final_Incentive_Status'] == 'yes']
missing_status = df[(df['September_Incentive'] > 0) & (df['Final_Incentive_Status'] != 'yes')]

print(f"September_Incentive > 0: {len(has_incentive)}명")
print(f"Final_Incentive_Status == 'yes': {len(has_status_yes)}명")
print(f"인센티브 있지만 status != 'yes': {len(missing_status)}명")

# 3. Final_Incentive_Status 수정
print("\n[2] Final_Incentive_Status 수정")
print("-" * 40)

# September_Incentive > 0인 모든 직원을 'yes'로 설정
df.loc[df['September_Incentive'] > 0, 'Final_Incentive_Status'] = 'yes'

# September_Incentive == 0인 직원을 'no'로 설정
df.loc[df['September_Incentive'] == 0, 'Final_Incentive_Status'] = 'no'

# NaN 값 처리
df['Final_Incentive_Status'] = df['Final_Incentive_Status'].fillna('no')

print("✅ Final_Incentive_Status 업데이트 완료")

# 4. 수정 후 검증
print("\n[3] 수정 후 검증")
print("-" * 40)

updated_yes = len(df[df['Final_Incentive_Status'] == 'yes'])
updated_no = len(df[df['Final_Incentive_Status'] == 'no'])
total_incentive = df[df['Final_Incentive_Status'] == 'yes']['September_Incentive'].sum()

print(f"Final_Incentive_Status == 'yes': {updated_yes}명")
print(f"Final_Incentive_Status == 'no': {updated_no}명")
print(f"총 지급액 (status='yes'): {total_incentive:,.0f} VND")

# 5. 직책별 상태 확인
print("\n[4] 주요 직책별 지급 현황")
print("-" * 40)

key_positions = ['MODEL MASTER', 'ASSEMBLY INSPECTOR', 'AUDIT & TRAINING TEAM',
                 'LINE LEADER', 'MANAGER']

for position in key_positions:
    pos_df = df[df['QIP POSITION 1ST  NAME'] == position]
    pos_paid = pos_df[pos_df['Final_Incentive_Status'] == 'yes']
    if len(pos_df) > 0:
        total_amount = pos_paid['September_Incentive'].sum()
        print(f"{position:25s}: {len(pos_paid):3d}/{len(pos_df):3d}명, {total_amount:,.0f} VND")

# 6. 파일 저장
print("\n[5] 파일 저장")
print("-" * 40)

# CSV 저장
df.to_csv(csv_file, index=False)
print(f"✅ CSV 파일 업데이트: {csv_file}")

# Excel 저장
excel_file = csv_file.replace('.csv', '.xlsx')
df.to_excel(excel_file, index=False)
print(f"✅ Excel 파일 업데이트: {excel_file}")

# 7. 최종 통계
print("\n[6] 최종 통계")
print("="*80)
print(f"📊 Total Employees: {len(df)}명")
print(f"💰 Paid Employees: {updated_yes}명")
print(f"💵 Total Paid Amount: {total_incentive:,.0f} VND")
print(f"📈 Payment Rate: {updated_yes/len(df)*100:.1f}%")

print()
print("✅ Final_Incentive_Status 수정 완료!")
print("   이제 대시보드를 다시 생성하면 정확한 통계가 표시됩니다.")
print("="*80)