#!/usr/bin/env python3
"""수정된 계산 로직 테스트"""

import pandas as pd
import shutil
import os
import sys

print("=== TYPE-2 GROUP LEADER 계산 수정 테스트 ===\n")

# 소스 파일 백업
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
backup_file = "input_files/test_backup.csv"

# 현재 파일 백업
shutil.copy(source_file, backup_file)

# 테스트용 파일 사용 (인센티브 칼럼 없는 버전)
if os.path.exists("input_files/test_no_incentive_columns.csv"):
    shutil.copy("input_files/test_no_incentive_columns.csv", source_file)
    print("✅ 테스트 파일 준비 완료 (인센티브 칼럼 제거된 버전)")
else:
    # 인센티브 칼럼 제거
    df = pd.read_csv(source_file, encoding='utf-8-sig')
    if 'September_Incentive' in df.columns:
        df = df.drop(columns=['September_Incentive'])
    if 'Final Incentive amount' in df.columns:
        df = df.drop(columns=['Final Incentive amount'])
    df.to_csv(source_file, index=False, encoding='utf-8-sig')
    print("✅ 인센티브 칼럼 제거 완료")

print("\n📊 Python 스크립트 실행 중...")
print("=" * 50)

# Python 스크립트 실행
sys.path.append('src')
from step1_인센티브_계산_개선버전 import main as calculate_main

# Mock input
class MockInput:
    def __init__(self):
        self.responses = ['9', '2025']
        self.index = 0

    def __call__(self, prompt=''):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            print(f"{prompt}{response}")
            return response
        return ''

import builtins
original_input = builtins.input
builtins.input = MockInput()

try:
    # 계산 실행
    calculate_main()

    print("\n" + "=" * 50)
    print("✅ 계산 완료!")

    # 결과 확인
    output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
    if os.path.exists(output_file):
        result_df = pd.read_csv(output_file, encoding='utf-8-sig')

        # TYPE-2 GROUP LEADER 확인
        type2_group_leaders = result_df[
            (result_df['ROLE TYPE STD'] == 'TYPE-2') &
            (result_df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER')
        ]

        print("\n=== TYPE-2 GROUP LEADER 계산 결과 ===")
        print(f"총 {len(type2_group_leaders)}명")

        for idx, row in type2_group_leaders.iterrows():
            emp_no = row['Employee No']
            name = row['Full Name']
            incentive = row.get('September_Incentive', 0)
            pass_rate = row.get('conditions_pass_rate', 0)

            status = "✅" if incentive > 0 else "❌"
            print(f"{status} {emp_no} | {name[:20]:20} | 충족률: {pass_rate:5.1f}% | 인센티브: {incentive:,.0f} VND")

        # ĐINH KIM NGOAN 특별 확인
        ngoan = type2_group_leaders[type2_group_leaders['Employee No'] == '617100049']
        if not ngoan.empty:
            ngoan_row = ngoan.iloc[0]
            print(f"\n🎯 ĐINH KIM NGOAN 상세:")
            print(f"  조건 충족률: {ngoan_row.get('conditions_pass_rate', 0)}%")
            print(f"  계산된 인센티브: {ngoan_row.get('September_Incentive', 0):,.0f} VND")
            print(f"  최종 인센티브: {ngoan_row.get('Final Incentive amount', 0):,.0f} VND")

            # 공정성 검증
            other_100 = type2_group_leaders[
                (type2_group_leaders['conditions_pass_rate'] == 100) &
                (type2_group_leaders['Employee No'] != '617100049')
            ]

            if len(other_100) > 0:
                other_incentives = other_100['September_Incentive'].unique()
                ngoan_incentive = ngoan_row.get('September_Incentive', 0)

                if ngoan_incentive in other_incentives:
                    print(f"\n✅ 공정성 검증 통과!")
                    print(f"   ĐINH KIM NGOAN과 다른 100% 충족자들이 동일한 금액 받음")
                else:
                    print(f"\n❌ 공정성 문제 발견!")
                    print(f"   ĐINH KIM NGOAN: {ngoan_incentive:,.0f} VND")
                    print(f"   다른 100% 충족자들: {other_incentives}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    # 원본 파일 복구
    builtins.input = original_input
    shutil.copy(backup_file, source_file)
    os.remove(backup_file)
    print("\n✅ 원본 파일 복구 완료")