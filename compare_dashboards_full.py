#!/usr/bin/env python3
"""원본 대시보드와 개선 대시보드 전체 비교"""

import pandas as pd
import os
import json

print("=== 원본 vs 개선 대시보드 인센티브 비교 ===\n")

# 1. 원본 대시보드 데이터 확인 (integrated_dashboard_final.py 결과)
original_html = "output_files/Incentive_Dashboard_2025_09_Version_5.html"
improved_html = "output_files/Incentive_Dashboard_2025_09_Version_6.html"

# Excel 파일로 비교
original_excel = "output_files/output_QIP_incentive_september_2025_최종완성버전_v5.0_Complete.xlsx"
improved_excel = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx"

# CSV 파일도 확인
improved_csv = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"

# 개선 버전 CSV 로드
if os.path.exists(improved_csv):
    df_improved = pd.read_csv(improved_csv, encoding='utf-8-sig')
    print(f"개선 버전 로드: {len(df_improved)}명")
else:
    print("❌ 개선 버전 CSV 파일이 없습니다")
    df_improved = None

# 원본 버전도 확인
backup_csv = "output_files/output_backup_september_2025.csv"
if os.path.exists(backup_csv):
    df_original = pd.read_csv(backup_csv, encoding='utf-8-sig')
    print(f"원본 백업 로드: {len(df_original)}명")
else:
    # 백업이 없으면 현재 소스 파일 확인
    source_csv = "input_files/2025년 9월 인센티브 지급 세부 정보.csv"
    df_original = pd.read_csv(source_csv, encoding='utf-8-sig')
    print(f"소스 파일 로드: {len(df_original)}명")

# 특정 직책 비교 - 모델 마스터
print("\n=== 모델 마스터 팀 비교 ===")

if df_improved is not None:
    # 모델 마스터 찾기
    model_master_improved = df_improved[
        df_improved['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False, case=False)
    ]

    print(f"\n개선 버전 - 모델 마스터: {len(model_master_improved)}명")
    if len(model_master_improved) > 0:
        incentive_col = 'September_Incentive'
        if incentive_col in model_master_improved.columns:
            avg_incentive = model_master_improved[incentive_col].mean()
            total_incentive = model_master_improved[incentive_col].sum()
            print(f"  평균 인센티브: {avg_incentive:,.0f} VND")
            print(f"  총 인센티브: {total_incentive:,.0f} VND")

            # 샘플 출력
            for idx, row in model_master_improved.head(3).iterrows():
                print(f"  {row['Employee No']} | {row['Full Name'][:20]:20} | {row.get(incentive_col, 0):,.0f} VND")

# 원본과 비교
if 'September_Incentive' in df_original.columns:
    model_master_original = df_original[
        df_original['QIP POSITION 1ST  NAME'].str.contains('MODEL MASTER', na=False, case=False)
    ]

    print(f"\n원본/소스 - 모델 마스터: {len(model_master_original)}명")
    if len(model_master_original) > 0:
        avg_incentive = model_master_original['September_Incentive'].mean()
        total_incentive = model_master_original['September_Incentive'].sum()
        print(f"  평균 인센티브: {avg_incentive:,.0f} VND")
        print(f"  총 인센티브: {total_incentive:,.0f} VND")

        # 샘플 출력
        for idx, row in model_master_original.head(3).iterrows():
            print(f"  {row['Employee No']} | {row['Full Name'][:20]:20} | {row.get('September_Incentive', 0):,.0f} VND")

# 전체 TYPE별 비교
print("\n=== TYPE별 인센티브 총액 비교 ===")

for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
    print(f"\n{type_name}:")

    if df_improved is not None and 'September_Incentive' in df_improved.columns:
        type_improved = df_improved[df_improved['ROLE TYPE STD'] == type_name]
        total_improved = type_improved['September_Incentive'].sum()
        count_improved = (type_improved['September_Incentive'] > 0).sum()
        print(f"  개선 버전: {count_improved}명, 총 {total_improved:,.0f} VND")

    if 'September_Incentive' in df_original.columns:
        type_original = df_original[df_original['ROLE TYPE STD'] == type_name]
        total_original = type_original['September_Incentive'].sum()
        count_original = (type_original['September_Incentive'] > 0).sum()
        print(f"  원본/소스: {count_original}명, 총 {total_original:,.0f} VND")

# 주요 포지션별 비교
print("\n=== 주요 포지션별 비교 ===")

positions = ['GROUP LEADER', 'LINE LEADER', 'AUDITOR', 'TRAINER', 'ASSEMBLY INSPECTOR']

for position in positions:
    print(f"\n{position}:")

    if df_improved is not None and 'September_Incentive' in df_improved.columns:
        pos_improved = df_improved[
            df_improved['QIP POSITION 1ST  NAME'].str.contains(position, na=False, case=False)
        ]
        if len(pos_improved) > 0:
            avg_improved = pos_improved['September_Incentive'].mean()
            print(f"  개선 버전: {len(pos_improved)}명, 평균 {avg_improved:,.0f} VND")

    if 'September_Incentive' in df_original.columns:
        pos_original = df_original[
            df_original['QIP POSITION 1ST  NAME'].str.contains(position, na=False, case=False)
        ]
        if len(pos_original) > 0:
            avg_original = pos_original['September_Incentive'].mean()
            print(f"  원본/소스: {len(pos_original)}명, 평균 {avg_original:,.0f} VND")

# ĐINH KIM NGOAN 특별 확인
print("\n=== ĐINH KIM NGOAN (617100049) 비교 ===")

if df_improved is not None:
    ngoan_improved = df_improved[df_improved['Employee No'] == '617100049']
    if not ngoan_improved.empty:
        row = ngoan_improved.iloc[0]
        print(f"개선 버전:")
        print(f"  인센티브: {row.get('September_Incentive', 0):,.0f} VND")
        print(f"  조건 충족률: {row.get('conditions_pass_rate', 0)}%")

ngoan_original = df_original[df_original['Employee No'] == '617100049']
if not ngoan_original.empty:
    row = ngoan_original.iloc[0]
    print(f"원본/소스:")
    print(f"  인센티브: {row.get('September_Incentive', 0):,.0f} VND")
    if 'conditions_pass_rate' in row:
        print(f"  조건 충족률: {row.get('conditions_pass_rate', 0)}%")