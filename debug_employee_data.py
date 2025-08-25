#!/usr/bin/env python3
"""
직원 데이터 디버깅 스크립트
"""

import pandas as pd
import json
from pathlib import Path

def debug_employee_data():
    """직원 데이터 확인"""
    
    # CSV 로드
    csv_path = Path("output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv")
    df = pd.read_csv(csv_path)
    
    print(f"✅ CSV 로드: {len(df)}명")
    
    # 첫 번째 직원 데이터 확인
    first_row = df.iloc[0]
    
    print("\n📊 첫 번째 직원 데이터:")
    print("-" * 60)
    
    # Type 정보
    type_value = first_row.get('ROLE TYPE STD', '')
    print(f"ROLE TYPE STD: {type_value}")
    
    # 직원 객체 생성 (dashboard 코드와 동일)
    emp = {
        'emp_no': str(first_row.get('Employee No', '')),
        'name': first_row.get('Full Name', ''),
        'position': first_row.get('QIP POSITION 1ST  NAME', ''),
        'type': str(type_value).strip() if not pd.isna(type_value) else '',
        'june_incentive': str(first_row.get('June_Incentive', '0')),
        'july_incentive': str(first_row.get('July_Incentive', '0')),
        'august_incentive': str(first_row.get('August_Incentive', '0')),
    }
    
    print("\n생성된 직원 객체:")
    for key, value in emp.items():
        print(f"  {key}: {value}")
    
    # JSON 직렬화 테스트
    print("\n📝 JSON 직렬화 테스트:")
    print("-" * 60)
    
    employees = []
    for idx, row in df.head(3).iterrows():
        type_value = row.get('ROLE TYPE STD', '')
        if pd.isna(type_value):
            type_value = ''
        else:
            type_value = str(type_value).strip()
            
        emp = {
            'emp_no': str(row.get('Employee No', '')),
            'name': row.get('Full Name', ''),
            'position': row.get('QIP POSITION 1ST  NAME', ''),
            'type': type_value,
            'july_incentive': str(row.get('July_Incentive', '0')),
        }
        employees.append(emp)
    
    # JSON 직렬화
    json_str = json.dumps(employees, ensure_ascii=False, default=str)
    print(f"JSON 길이: {len(json_str)} 문자")
    print(f"JSON 샘플: {json_str[:500]}...")
    
    # Type별 카운트
    print("\n📊 Type별 분포:")
    print("-" * 60)
    type_counts = df['ROLE TYPE STD'].value_counts()
    for type_val, count in type_counts.items():
        print(f"  {type_val}: {count}명")

if __name__ == "__main__":
    debug_employee_data()