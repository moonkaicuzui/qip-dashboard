#!/usr/bin/env python3
"""완전 수정된 계산 테스트"""

import pandas as pd
import shutil
import os
import sys

print("=== 완전 수정 테스트 ===\n")
print("1. 소스 CSV의 Final Incentive amount 무시")
print("2. 2단계 계산 방식 적용")
print("3. 공정성 검증\n")

# 원본 백업
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
backup_file = "input_files/original_backup.csv"
shutil.copy(source_file, backup_file)

# Python 스크립트 실행
print("📊 Python 계산 실행 중...")
print("=" * 50)

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
    calculate_main()

    print("\n" + "=" * 50)
    print("✅ 계산 완료!\n")

    # 결과 확인
    output_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
    if os.path.exists(output_file):
        df = pd.read_csv(output_file, encoding='utf-8-sig')

        print("=== 주요 검증 포인트 ===\n")

        # 1. ĐINH KIM NGOAN 확인
        print("1. ĐINH KIM NGOAN (617100049):")
        ngoan = df[df['Employee No'] == '617100049']
        if not ngoan.empty:
            row = ngoan.iloc[0]
            sept = row.get('September_Incentive', 0)
            final = row.get('Final Incentive amount', 0)
            pass_rate = row.get('conditions_pass_rate', 0)
            print(f"   조건 충족률: {pass_rate}%")
            print(f"   September_Incentive: {sept:,.0f} VND")
            print(f"   Final Incentive amount: {final:,.0f} VND")

            if final == 214720:
                print(f"   ✅ 공정하게 214,720 VND 받음!")
            else:
                print(f"   ❌ 여전히 문제 있음: {final:,.0f} VND")

        # 2. TYPE-2 GROUP LEADER 전체
        print("\n2. TYPE-2 GROUP LEADER 100% 충족자:")
        type2_gl_100 = df[
            (df['ROLE TYPE STD'] == 'TYPE-2') &
            (df['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') &
            (df['conditions_pass_rate'] == 100)
        ]

        for idx, row in type2_gl_100.iterrows():
            emp_no = row['Employee No']
            name = row['Full Name']
            final = row.get('Final Incentive amount', 0)
            print(f"   {emp_no} | {name[:20]:20} | {final:,.0f} VND")

        # 공정성 확인
        if len(type2_gl_100) > 0:
            unique_amounts = type2_gl_100['Final Incentive amount'].unique()
            if len(unique_amounts) == 1:
                print(f"\n   ✅ 모두 동일한 금액: {unique_amounts[0]:,.0f} VND")
            else:
                print(f"\n   ❌ 불공정: 다른 금액들 {unique_amounts}")

        # 3. 모델 마스터 확인
        print("\n3. 모델 마스터:")
        model_master = df[
            df['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False, case=False)
        ]

        if len(model_master) > 0:
            for idx, row in model_master.iterrows():
                emp_no = row['Employee No']
                name = row['Full Name']
                role_type = row['ROLE TYPE STD']
                final = row.get('Final Incentive amount', 0)
                print(f"   {emp_no} | {name[:20]:20} | {role_type} | {final:,.0f} VND")

            avg = model_master['Final Incentive amount'].mean()
            print(f"\n   평균: {avg:,.0f} VND")
            if avg > 0:
                print(f"   ✅ 모델 마스터 인센티브 계산됨")
            else:
                print(f"   ❌ 모델 마스터 인센티브 0원")

        # 4. TYPE별 총액
        print("\n4. TYPE별 총액:")
        for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
            type_data = df[df['ROLE TYPE STD'] == type_name]
            total = type_data['Final Incentive amount'].sum()
            count = (type_data['Final Incentive amount'] > 0).sum()
            print(f"   {type_name}: {count}명, 총 {total:,.0f} VND")

except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()

finally:
    builtins.input = original_input
    # 백업 복구
    shutil.copy(backup_file, source_file)
    os.remove(backup_file)
    print("\n✅ 원본 파일 복구 완료")