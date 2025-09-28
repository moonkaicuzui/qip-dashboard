#!/usr/bin/env python3
"""Python이 실제로 계산을 하는지 테스트"""

import pandas as pd
import shutil
import os

# 1. 소스 파일 백업
source_file = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
backup_file = "input_files/2025년 9월 인센티브 지급 세부 정보_backup.csv"

if not os.path.exists(backup_file):
    shutil.copy(source_file, backup_file)
    print(f"✅ 백업 생성: {backup_file}")

# 2. 소스 파일 수정 - September_Incentive 칼럼 제거
df = pd.read_csv(source_file, encoding='utf-8-sig')
print(f"\n=== 원본 소스 파일 ===")
print(f"칼럼 수: {len(df.columns)}")
print(f"September_Incentive 있음: {'September_Incentive' in df.columns}")

# ĐINH KIM NGOAN 원본 값
ngoan = df[df['Employee No'] == '617100049']
if not ngoan.empty:
    print(f"\nĐINH KIM NGOAN 원본:")
    print(f"  September_Incentive: {ngoan.iloc[0]['September_Incentive']}")
    print(f"  Final Incentive amount: {ngoan.iloc[0]['Final Incentive amount']}")

# September_Incentive 칼럼 제거하고 저장
if 'September_Incentive' in df.columns:
    df_no_sept = df.drop(columns=['September_Incentive'])
    df_no_sept.to_csv("input_files/test_no_september.csv", index=False, encoding='utf-8-sig')
    print(f"\n✅ September_Incentive 칼럼 제거한 테스트 파일 생성")
    print(f"   칼럼 수: {len(df_no_sept.columns)}")

    # 이제 Python 스크립트가 계산하는지 확인해야 함
    print("\n이제 다음 명령을 실행하세요:")
    print("1. 원본 백업: mv input_files/2025년\\ 9월\\ 인센티브\\ 지급\\ 세부\\ 정보.csv input_files/original.csv")
    print("2. 테스트 파일로 교체: mv input_files/test_no_september.csv input_files/2025년\\ 9월\\ 인센티브\\ 지급\\ 세부\\ 정보.csv")
    print("3. Python 실행: python src/step1_인센티브_계산_개선버전.py")
    print("4. 결과 확인 후 원복: mv input_files/original.csv input_files/2025년\\ 9월\\ 인센티브\\ 지급\\ 세부\\ 정보.csv")