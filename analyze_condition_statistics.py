#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
조건 충족 통계 분석 스크립트
10개 조건 체계의 적용 현황을 Type별 직급별로 분석
"""

import pandas as pd
from pathlib import Path

def analyze_condition_statistics():
    """조건 충족 통계 분석"""
    
    # CSV 파일 읽기
    csv_path = Path("output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv")
    df = pd.read_csv(csv_path)
    
    print("=" * 80)
    print("10개 조건 체계 통계 분석")
    print("=" * 80)
    
    # 인센티브 금액을 숫자로 변환
    if df['August_Incentive'].dtype == 'object':
        df['Incentive_Amount'] = pd.to_numeric(df['August_Incentive'].str.replace(',', '').str.replace(' VND', ''), errors='coerce').fillna(0)
    else:
        df['Incentive_Amount'] = pd.to_numeric(df['August_Incentive'], errors='coerce').fillna(0)
    
    # Type별 통계
    print("\n📊 Type별 인센티브 지급 현황")
    print("-" * 40)
    
    type_stats = df.groupby('ROLE TYPE STD').agg({
        'Employee No': 'count',
        'Incentive_Amount': ['sum', lambda x: (x > 0).sum()]
    }).round(0)
    
    type_stats.columns = ['전체 인원', '총 지급액', '지급 인원']
    type_stats['지급률(%)'] = (type_stats['지급 인원'] / type_stats['전체 인원'] * 100).round(1)
    type_stats['평균 지급액'] = (type_stats['총 지급액'] / type_stats['지급 인원']).fillna(0).round(0)
    
    print(type_stats)
    
    # Type별 직급별 상세 분석
    print("\n📋 Type별 직급별 상세 분석")
    print("=" * 80)
    
    for type_name in df['ROLE TYPE STD'].unique():
        if pd.isna(type_name):
            continue
            
        print(f"\n### {type_name}")
        print("-" * 60)
        
        type_df = df[df['ROLE TYPE STD'] == type_name]
        
        # 직급별 통계
        position_stats = type_df.groupby('QIP POSITION 1ST  NAME').agg({
            'Employee No': 'count',
            'Incentive_Amount': ['sum', lambda x: (x > 0).sum()]
        }).round(0)
        
        position_stats.columns = ['인원', '총액', '지급']
        position_stats['지급률'] = (position_stats['지급'] / position_stats['인원'] * 100).round(1)
        
        # 예상 조건 수 추가
        position_stats['예상 조건'] = position_stats.index.map(lambda pos: get_expected_conditions(type_name, pos))
        
        # 정렬 및 출력
        position_stats = position_stats.sort_values('인원', ascending=False)
        print(position_stats.head(10))
    
    # 조건별 충족률 추정 (인센티브 지급 여부 기반)
    print("\n🎯 조건별 충족률 추정 (인센티브 지급 여부 기반)")
    print("-" * 80)
    
    # Type-2 분석 (출근 4 + 5PRS 2 조건)
    type2_df = df[df['ROLE TYPE STD'] == 'TYPE-2']
    type2_paid_rate = (type2_df['Incentive_Amount'] > 0).sum() / len(type2_df) * 100
    
    print(f"\nTYPE-2 조건 충족 분석:")
    print(f"  전체 인원: {len(type2_df)}명")
    print(f"  인센티브 지급: {(type2_df['Incentive_Amount'] > 0).sum()}명")
    print(f"  지급률: {type2_paid_rate:.1f}%")
    print(f"  적용 조건: 출근 4개 + 5PRS 2개 (총 6개)")
    
    # Type-3 분석 (출근 4 조건만)
    type3_df = df[df['ROLE TYPE STD'] == 'TYPE-3']
    type3_paid_rate = (type3_df['Incentive_Amount'] > 0).sum() / len(type3_df) * 100
    
    print(f"\nTYPE-3 조건 충족 분석:")
    print(f"  전체 인원: {len(type3_df)}명")
    print(f"  인센티브 지급: {(type3_df['Incentive_Amount'] > 0).sum()}명")
    print(f"  지급률: {type3_paid_rate:.1f}%")
    print(f"  적용 조건: 출근 4개만")
    
    # Type-1 직급별 분석
    type1_df = df[df['ROLE TYPE STD'] == 'TYPE-1']
    
    print(f"\nTYPE-1 주요 직급별 조건 충족 분석:")
    
    key_positions = [
        ('SUPERVISOR', '9개 조건 (6번 제외)'),
        ('MANAGER', '9개 조건 (6번 제외)'),
        ('GROUP LEADER', '8개 조건 (6,7번 제외)'),
        ('ASSEMBLY INSPECTOR', '8개 조건 (7,8번 제외)'),
        ('AQL INSPECTOR', '8개 조건 (7,8번 제외)')
    ]
    
    for position, expected in key_positions:
        pos_df = type1_df[type1_df['QIP POSITION 1ST  NAME'].str.contains(position, na=False)]
        if len(pos_df) > 0:
            paid_count = (pos_df['Incentive_Amount'] > 0).sum()
            paid_rate = paid_count / len(pos_df) * 100
            print(f"\n  {position}:")
            print(f"    인원: {len(pos_df)}명")
            print(f"    지급: {paid_count}명")
            print(f"    지급률: {paid_rate:.1f}%")
            print(f"    조건: {expected}")

def get_expected_conditions(type_name, position):
    """Type과 직급에 따른 예상 조건 설명"""
    
    if pd.isna(position):
        return "N/A"
    
    position_upper = str(position).upper()
    
    if type_name == "TYPE-3":
        return "4개 (출근)"
    elif type_name == "TYPE-2":
        return "6개 (출근+5PRS)"
    else:  # TYPE-1
        if "GROUP LEADER" in position_upper:
            return "8개 (6,7제외)"
        elif any(x in position_upper for x in ["SUPERVISOR", "MANAGER", "DEPUTY", "TEAM LEADER"]):
            return "9개 (6제외)"
        elif "ASSEMBLY INSPECTOR" in position_upper or "AQL INSPECTOR" in position_upper:
            return "8개 (7,8제외)"
        elif any(x in position_upper for x in ["BOTTOM", "STITCHING", "MTL"]):
            return "6개 (출근+5PRS)"
        else:
            return "미정의"

if __name__ == "__main__":
    analyze_condition_statistics()
    
    print("\n" + "=" * 80)
    print("✅ 분석 완료")
    print("=" * 80)