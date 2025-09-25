"""
직원 수 차이 진단 스크립트
385명 vs 392명 차이 분석
"""

import pandas as pd
import os
from datetime import datetime

def parse_date(date_str):
    """날짜 파싱 함수"""
    if pd.isna(date_str) or date_str == '' or date_str == 'N/A':
        return pd.NaT
    
    if isinstance(date_str, (int, float)):
        try:
            return pd.Timestamp('1900-01-01') + pd.Timedelta(days=int(date_str)-2)
        except:
            return pd.NaT
    
    date_str = str(date_str).strip()
    formats = [
        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y.%m.%d',
        '%d.%m.%Y', '%d-%m-%Y', '%Y%m%d', '%Y년 %m월 %d일'
    ]
    
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    
    try:
        return pd.to_datetime(date_str, dayfirst=True)
    except:
        return pd.NaT

def analyze_employee_counts():
    """직원 수 차이 분석"""
    
    # 1. 8월 인센티브 파일 로드
    file_path = "input_files/2025년 8월 인센티브 지급 세부 정보.csv"
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return
    
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"\n📊 전체 데이터 행 수: {len(df)}")
    
    # 날짜 파싱
    if 'Stop working Date' in df.columns:
        df['Stop working Date'] = df['Stop working Date'].apply(parse_date)
    if 'Entrance Date' in df.columns:
        df['Entrance Date'] = df['Entrance Date'].apply(parse_date)
    
    # 2. 8월 1일 기준 활성 직원 필터링 (인센티브 대시보드 로직)
    month_start = pd.Timestamp(2025, 8, 1)
    
    # 인센티브 대시보드 필터링 방식
    if 'Stop working Date' in df.columns:
        active_mask_incentive = (
            df['Stop working Date'].isna() |  # 퇴사일이 없는 직원
            (df['Stop working Date'] >= month_start)  # 8월 1일 이후 퇴사
        )
        active_employees_incentive = df[active_mask_incentive]
    else:
        active_employees_incentive = df
    
    print(f"\n✅ 인센티브 대시보드 로직 활성 직원: {len(active_employees_incentive)}명")
    
    # 3. 관리 대시보드 통합 필터 로직 (수정된 구현 - 인센티브와 동일)
    active_mask_management = pd.Series([True] * len(df), index=df.index)
    
    if 'Stop working Date' in df.columns:
        active_mask_management = (
            df['Stop working Date'].isna() |
            (df['Stop working Date'] >= month_start)
        )
    elif 'RE MARK' in df.columns:
        active_mask_management = df['RE MARK'] != 'Stop working'
    
    # 인센티브 대시보드와 동일하게 입사일 필터링 제거
    # 해당 월 인센티브 파일에 있으면 모두 포함
    
    active_employees_management = df[active_mask_management]
    
    print(f"✅ 관리 대시보드 통합 필터 활성 직원: {len(active_employees_management)}명")
    
    # 4. 차이 분석
    diff = len(active_employees_incentive) - len(active_employees_management)
    print(f"\n📌 차이: {diff}명")
    
    if diff != 0:
        # 인센티브에는 있지만 관리에는 없는 직원
        in_incentive_not_management = active_employees_incentive[
            ~active_employees_incentive.index.isin(active_employees_management.index)
        ]
        
        # 관리에는 있지만 인센티브에는 없는 직원
        in_management_not_incentive = active_employees_management[
            ~active_employees_management.index.isin(active_employees_incentive.index)
        ]
        
        if len(in_incentive_not_management) > 0:
            print(f"\n🔍 인센티브에는 포함되지만 관리 대시보드에서 제외된 직원: {len(in_incentive_not_management)}명")
            for idx, row in in_incentive_not_management.head(10).iterrows():
                print(f"  - {row.get('Name', 'N/A')} (ID: {row.get('ID No', 'N/A')})")
                print(f"    입사일: {row.get('Entrance Date', 'N/A')}")
                print(f"    퇴사일: {row.get('Stop working Date', 'N/A')}")
                print(f"    RE MARK: {row.get('RE MARK', 'N/A')}")
        
        if len(in_management_not_incentive) > 0:
            print(f"\n🔍 관리 대시보드에는 포함되지만 인센티브에서 제외된 직원: {len(in_management_not_incentive)}명")
            for idx, row in in_management_not_incentive.head(10).iterrows():
                print(f"  - {row.get('Name', 'N/A')} (ID: {row.get('ID No', 'N/A')})")
                print(f"    입사일: {row.get('Entrance Date', 'N/A')}")
                print(f"    퇴사일: {row.get('Stop working Date', 'N/A')}")
                print(f"    RE MARK: {row.get('RE MARK', 'N/A')}")
    
    # 5. 입사일 필터링 영향 분석
    print("\n📈 입사일 필터링 영향 분석:")
    if 'Entrance Date' in df.columns:
        month_end = pd.Timestamp(2025, 8, 31)
        
        # Stop working Date 기준 활성 직원
        stop_working_filter = (
            df['Stop working Date'].isna() |
            (df['Stop working Date'] >= month_start)
        ) if 'Stop working Date' in df.columns else pd.Series([True] * len(df))
        
        # 입사일이 8월 31일 이후인 직원
        late_entrance = df[stop_working_filter & (df['Entrance Date'] > month_end)]
        print(f"  - 8월 31일 이후 입사로 제외된 직원: {len(late_entrance)}명")
        
        if len(late_entrance) > 0:
            print(f"\n  상세 정보:")
            for idx, row in late_entrance.head(10).iterrows():
                print(f"    • {row.get('Name', 'N/A')} - 입사일: {row.get('Entrance Date', 'N/A')}")
    
    # 6. RE MARK 영향 분석
    if 'RE MARK' in df.columns:
        stop_working_count = (df['RE MARK'] == 'Stop working').sum()
        print(f"\n  - RE MARK가 'Stop working'인 직원: {stop_working_count}명")
    
    return active_employees_incentive, active_employees_management

if __name__ == "__main__":
    print("=" * 60)
    print("직원 수 차이 진단 분석")
    print("=" * 60)
    
    incentive_df, management_df = analyze_employee_counts()
    
    print("\n" + "=" * 60)
    print("분석 완료")
    print("=" * 60)