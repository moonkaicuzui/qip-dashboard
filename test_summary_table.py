#!/usr/bin/env python3
"""
Type Summary Table 테스트 스크립트
대시보드의 Type별 요약 테이블이 제대로 표시되는지 확인
"""

import pandas as pd
from pathlib import Path

def test_summary_data():
    """Type별 요약 데이터 테스트"""
    
    # CSV 데이터 로드
    csv_path = Path("output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    print(f"✅ CSV 로드 완료: {len(df)}명의 직원 데이터")
    
    # Type별 집계
    type_summary = {}
    
    for _, row in df.iterrows():
        emp_type = row.get('Type', '')
        if not emp_type:
            continue
        
        if emp_type not in type_summary:
            type_summary[emp_type] = {
                'total': 0,
                'paid': 0,
                'total_amount': 0
            }
        
        type_summary[emp_type]['total'] += 1
        
        # July_incentive 컬럼 확인
        incentive_col = 'July_incentive'
        if incentive_col in row:
            incentive_str = str(row[incentive_col])
            # 숫자만 추출
            amount = 0
            if incentive_str and incentive_str != 'nan':
                try:
                    # 쉼표와 VND 제거
                    clean_str = incentive_str.replace(',', '').replace('VND', '').strip()
                    amount = float(clean_str) if clean_str else 0
                except:
                    amount = 0
            
            if amount > 0:
                type_summary[emp_type]['paid'] += 1
                type_summary[emp_type]['total_amount'] += amount
    
    # 결과 출력
    print("\n📊 Type별 요약 데이터:")
    print("-" * 80)
    print(f"{'Type':<10} {'Total':<10} {'Paid':<10} {'Payment Rate':<15} {'Total Amount':<20}")
    print("-" * 80)
    
    for emp_type in sorted(type_summary.keys()):
        data = type_summary[emp_type]
        payment_rate = (data['paid'] / data['total'] * 100) if data['total'] > 0 else 0
        
        print(f"{emp_type:<10} {data['total']:<10} {data['paid']:<10} "
              f"{payment_rate:>6.1f}%        {data['total_amount']:>15,.0f} VND")
    
    print("-" * 80)
    
    # JavaScript에서 사용할 형식으로 출력
    print("\n📝 JavaScript 형식 (테스트용):")
    print("const typeSummary = {")
    for emp_type in sorted(type_summary.keys()):
        data = type_summary[emp_type]
        print(f"    '{emp_type}': {{ total: {data['total']}, paid: {data['paid']}, "
              f"totalAmount: {data['total_amount']:.0f} }},")
    print("};")
    
    return type_summary

if __name__ == "__main__":
    test_summary_data()