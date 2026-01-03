#!/usr/bin/env python3
"""
December 2025 단독 계산 스크립트 (November V10.0 기준)
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

# Import calculation module
import step1_인센티브_계산_개선버전 as calc_module

def main():
    print("=" * 70)
    print("December 2025 인센티브 계산")
    print("기준: November V10.0 (Final Nov incentive.xlsx 적용)")
    print("=" * 70)

    # Change to project directory
    os.chdir('/Users/ksmoon/Coding/Dashboard  Incentive Version 9 _Web Dashboard')

    # Create calculator instance
    calculator = calc_module.CompleteQIPCalculator(
        config_path='config_files/config_december_2025.json',
        config=None  # Will be loaded from file
    )

    # Run calculation
    print("\n🔄 계산 시작...")
    calculator.calculate_all_incentives()

    print("\n" + "=" * 70)
    print("✅ December 2025 계산 완료!")
    print("=" * 70)

    # Verify result
    import pandas as pd
    df = pd.read_csv('output_files/output_QIP_incentive_december_2025_Complete_V10.0_Complete.csv')

    print("\n검증: 직원 621030996 (DANH MINH HIẾU)")
    print("-" * 70)

    emp = df[df['Employee No'].astype(str) == '621030996']
    if not emp.empty:
        dec_incentive = emp['December_Incentive'].values[0]
        cont_months = emp['Continuous_Months'].values[0]
        prev_incentive = emp['Previous_Month_Incentive'].values[0]

        print(f"December_Incentive: {dec_incentive:,.0f} VND")
        print(f"Continuous_Months: {cont_months}")
        print(f"Previous_Month_Incentive: {prev_incentive:,.0f} VND")

        if dec_incentive == 150000 and cont_months == 1 and prev_incentive == 0:
            print("\n✅ 모든 값이 정확합니다!")
            print("   - December: 150,000 VND (1개월)")
            print("   - Previous: 0 VND (November)")
            return 0
        else:
            print(f"\n⚠️ 예상과 다릅니다:")
            print(f"   - December: {dec_incentive:,.0f} (expected 150,000)")
            print(f"   - Months: {cont_months} (expected 1)")
            print(f"   - Previous: {prev_incentive:,.0f} (expected 0)")
            return 1
    else:
        print("❌ 직원을 찾을 수 없습니다!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
