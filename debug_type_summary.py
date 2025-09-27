#!/usr/bin/env python3
"""
Type별 요약 테이블이 비어있는 문제 디버깅
"""

import pandas as pd
import json
from pathlib import Path

# 데이터 파일 읽기
excel_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx"
json_file = "output_files/dashboard_data_from_excel.json"

print("=" * 60)
print("Type별 요약 테이블 디버깅")
print("=" * 60)

# Excel 데이터 확인
if Path(excel_file).exists():
    df = pd.read_excel(excel_file)
    print(f"\n📊 Excel 데이터:")
    print(f"  총 행: {len(df)}")
    print(f"  컬럼: {df.columns.tolist()[:5]}...")

    # TYPE 관련 컬럼 찾기
    type_columns = [col for col in df.columns if 'type' in col.lower() or 'role' in col.lower()]
    print(f"\n  TYPE 관련 컬럼:")
    for col in type_columns:
        print(f"    - {col}")
        if col in df.columns:
            unique_types = df[col].dropna().unique()
            print(f"      값: {list(unique_types)[:5]}...")

    # 인센티브 금액 컬럼 찾기
    incentive_columns = [col for col in df.columns if 'incentive' in col.lower() or '인센티브' in col.lower()]
    print(f"\n  인센티브 관련 컬럼:")
    for col in incentive_columns:
        print(f"    - {col}")
        if col in df.columns:
            non_zero = df[df[col] > 0][col].count() if pd.api.types.is_numeric_dtype(df[col]) else 0
            print(f"      0이 아닌 값: {non_zero}개")

# JSON 데이터 확인
if Path(json_file).exists():
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n📋 JSON 데이터:")

    # employees 키가 있는지 확인
    if 'employees' in data:
        employees = data['employees']
    elif isinstance(data, list):
        employees = data
    else:
        # 첫 번째 키 사용
        first_key = list(data.keys())[0] if data else None
        employees = data.get(first_key, []) if first_key else []

    print(f"  총 직원: {len(employees) if employees else 0}")

    if employees:
        first_emp = employees[0]
        print(f"\n  첫 번째 직원 데이터 키:")
        for key in list(first_emp.keys())[:10]:
            value = first_emp[key]
            value_str = str(value)[:50] if value else "None"
            print(f"    - {key}: {value_str}")

        # type 필드 확인
        print(f"\n  TYPE 필드 분석:")
        type_field_candidates = ['type', 'TYPE', 'Type', 'ROLE TYPE STD', 'role_type']
        for field in type_field_candidates:
            if field in first_emp:
                print(f"    ✓ '{field}' 필드 존재: {first_emp[field]}")

                # TYPE 값 분포 확인
                type_counts = {}
                for emp in employees:
                    type_val = emp.get(field, 'UNKNOWN')
                    type_counts[type_val] = type_counts.get(type_val, 0) + 1

                print(f"      TYPE 분포:")
                for type_val, count in sorted(type_counts.items())[:5]:
                    print(f"        - {type_val}: {count}명")

        # 인센티브 필드 확인
        print(f"\n  인센티브 금액 필드 분석:")
        incentive_candidates = [
            'Final Incentive amount',
            'september_incentive',
            'September_Incentive',
            '최종 인센티브 금액',
            'incentive_amount'
        ]

        for field in incentive_candidates:
            if field in first_emp:
                print(f"    ✓ '{field}' 필드 존재: {first_emp[field]}")

                # 인센티브 금액 분포
                amount_count = 0
                total_amount = 0
                for emp in employees:
                    amount = emp.get(field, 0)
                    if amount and amount > 0:
                        amount_count += 1
                        total_amount += amount

                print(f"      지급 인원: {amount_count}명")
                print(f"      총 지급액: {total_amount:,} VND")

print("\n" + "=" * 60)
print("💡 분석 결과:")

# JavaScript에서 사용해야 할 필드명 제안
if Path(json_file).exists() and employees:
    emp = employees[0]

    # type 필드 찾기
    type_field = None
    for field in ['type', 'TYPE', 'Type', 'ROLE TYPE STD']:
        if field in emp:
            type_field = field
            break

    # incentive 필드 찾기
    incentive_field = None
    for field in ['Final Incentive amount', 'september_incentive', 'September_Incentive']:
        if field in emp:
            incentive_field = field
            break

    print(f"  JavaScript에서 사용해야 할 필드:")
    print(f"    - TYPE 필드: emp['{type_field}'] (현재: emp['type'])")
    print(f"    - 인센티브 필드: emp['{incentive_field}']")

    if type_field != 'type':
        print(f"\n  ⚠️ 경고: 'type' 필드가 없습니다. '{type_field}'를 사용해야 합니다!")

print("=" * 60)