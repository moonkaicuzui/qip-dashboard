#!/usr/bin/env python3
"""
대시보드 Type별 요약 테이블 수정 검증 스크립트
"""

import os
import json
import pandas as pd
from pathlib import Path

print("=" * 60)
print("🔍 대시보드 Type별 요약 테이블 검증")
print("=" * 60)

# 1. HTML 파일 존재 확인
html_file = Path("output_files/Incentive_Dashboard_2025_09_Version_5.html")
if not html_file.exists():
    print("❌ 대시보드 HTML 파일이 없습니다!")
    exit(1)

print(f"✅ HTML 파일 존재: {html_file}")

# 2. JavaScript 코드 검증
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 필수 코드 패턴 확인
required_patterns = [
    ("Type 필드 매핑", "emp['ROLE TYPE STD']"),
    ("인센티브 필드 매핑", "emp['Final Incentive amount']"),
    ("ForceUpdate 함수", "window.forceUpdateTypeSummary"),
    ("자동 실행 타이머", "setTimeout(window.forceUpdateTypeSummary"),
    ("console.log 위치", "const amount =.*\\n.*console.log\\('Type 확인:'")
]

print("\n📋 JavaScript 코드 검증:")
all_passed = True
for name, pattern in required_patterns:
    if pattern in html_content:
        print(f"  ✅ {name}: OK")
    else:
        print(f"  ❌ {name}: 패턴을 찾을 수 없음")
        all_passed = False

# 3. 데이터 검증
print("\n📊 데이터 검증:")
csv_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_enhanced.csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)

    # Type별 집계
    # 먼저 컬럼명 확인
    print(f"  CSV 컬럼: {', '.join(df.columns[:5])}...")

    # 실제 컬럼명에 맞춰 집계
    id_col = 'Employee ID' if 'Employee ID' in df.columns else df.columns[0]
    type_col = 'ROLE TYPE STD' if 'ROLE TYPE STD' in df.columns else 'Type'

    type_summary = df.groupby(type_col).agg({
        id_col: 'count',
        'September_Incentive': lambda x: (x > 0).sum() if 'September_Incentive' in df.columns else 0,
        'Final Incentive amount': 'sum'
    }).rename(columns={
        id_col: '전체',
        'September_Incentive': '지급',
        'Final Incentive amount': '총액'
    })

    print("\nType별 요약 (CSV 데이터 기준):")
    for type_name in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        if type_name in type_summary.index:
            row = type_summary.loc[type_name]
            print(f"  {type_name}: 전체 {row['전체']}명, 지급 {row['지급']}명, 총액 {row['총액']:,.0f} VND")
else:
    print("  ⚠️ CSV 파일을 찾을 수 없습니다")

# 4. 최종 결과
print("\n" + "=" * 60)
if all_passed:
    print("✅ 모든 검증 통과! Type별 요약 테이블이 정상 작동할 것입니다.")
    print("\n📌 브라우저에서 확인 방법:")
    print("1. 대시보드 열기:")
    print(f"   open {html_file}")
    print("\n2. 개발자 도구 콘솔에서 실행:")
    print("   window.forceUpdateTypeSummary()")
    print("\n3. 또는 browser_debug_code.js 전체 복사하여 실행")
else:
    print("❌ 일부 검증 실패. 수정이 필요합니다.")

print("=" * 60)