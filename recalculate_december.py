#!/usr/bin/env python3
"""
December 2025 단독 재계산 스크립트
"""

import subprocess
import sys

def main():
    print("=" * 70)
    print("December 2025 단독 재계산")
    print("=" * 70)

    # Call auto_calculate_incentives.py but only process December
    result = subprocess.run(
        ['python', 'scripts/auto_calculate_incentives.py'],
        cwd='/Users/ksmoon/Coding/Dashboard  Incentive Version 9 _Web Dashboard',
        capture_output=False
    )

    if result.returncode != 0:
        print("❌ 계산 실패!")
        sys.exit(1)

    # Verify result
    import pandas as pd
    df = pd.read_csv('output_files/output_QIP_incentive_december_2025_Complete_V10.0_Complete.csv')

    print("\n" + "=" * 70)
    print("검증: 직원 621030996 (DANH MINH HIẾU)")
    print("=" * 70)

    emp = df[df['Employee No'].astype(str) == '621030996']
    if not emp.empty:
        print(f"December_Incentive: {emp['December_Incentive'].values[0]:,.0f} VND")
        print(f"Continuous_Months: {emp['Continuous_Months'].values[0]}")
        print(f"Previous_Month_Incentive: {emp['Previous_Month_Incentive'].values[0]:,.0f} VND")

        dec_incentive = emp['December_Incentive'].values[0]
        if dec_incentive == 150000:
            print("\n✅ December = 150,000 VND (1개월) - 정확!")
            return 0
        else:
            print(f"\n❌ December = {dec_incentive:,.0f} VND (expected 150,000 VND)")
            return 1
    else:
        print("❌ 직원을 찾을 수 없습니다!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
