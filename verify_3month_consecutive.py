#!/usr/bin/env python3
"""
3개월 연속 실패 상세 검증
ID 형식 문제 해결
"""

import pandas as pd
from pathlib import Path

# 각 월별 데이터 로드
july_df = pd.read_csv('input_files/AQL history/1.HSRG AQL REPORT-JULY.2025.csv', encoding='utf-8-sig')
aug_df = pd.read_csv('input_files/AQL history/1.HSRG AQL REPORT-AUGUST.2025.csv', encoding='utf-8-sig')
sep_df = pd.read_csv('input_files/AQL history/1.HSRG AQL REPORT-SEPTEMBER.2025.csv', encoding='utf-8-sig')

# FAIL 데이터만 필터링
july_fail = july_df[july_df['RESULT'].str.upper() == 'FAIL']['EMPLOYEE NO'].astype(str).str.strip()
aug_fail = aug_df[aug_df['RESULT'].str.upper() == 'FAIL']['EMPLOYEE NO'].astype(str).str.strip()
sep_fail = sep_df[sep_df['RESULT'].str.upper() == 'FAIL']['EMPLOYEE NO'].astype(str).str.strip()

# float 형식 제거 (예: 621030996.0 -> 621030996)
july_fail = july_fail.str.replace(r'\.0$', '', regex=True)
aug_fail = aug_fail.str.replace(r'\.0$', '', regex=True)
sep_fail = sep_fail.str.replace(r'\.0$', '', regex=True)

# unique 직원들
july_unique = set(july_fail.unique())
aug_unique = set(aug_fail.unique())
sep_unique = set(sep_fail.unique())

print("=" * 80)
print("📊 3개월 연속 AQL 실패 상세 검증")
print("=" * 80)

print(f"\n7월 실패자: {len(july_unique)}명")
print(f"8월 실패자: {len(aug_unique)}명")
print(f"9월 실패자: {len(sep_unique)}명")

# 교집합 찾기
july_aug = july_unique & aug_unique
aug_sep = aug_unique & sep_unique
all_three = july_unique & aug_unique & sep_unique

print(f"\n7-8월 둘 다 실패: {len(july_aug)}명")
if july_aug:
    print(f"  샘플: {list(july_aug)[:5]}")

print(f"\n8-9월 둘 다 실패: {len(aug_sep)}명")
if aug_sep:
    print(f"  샘플: {list(aug_sep)[:5]}")

print(f"\n✨ 7-8-9월 3개월 연속 실패: {len(all_three)}명")
if all_three:
    print("\n3개월 연속 실패자 명단:")
    print("-" * 40)
    for emp_id in sorted(all_three):
        # 각 월별 실패 횟수
        july_count = (july_fail == emp_id).sum()
        aug_count = (aug_fail == emp_id).sum()
        sep_count = (sep_fail == emp_id).sum()

        print(f"  {emp_id}: 7월 {july_count}회, 8월 {aug_count}회, 9월 {sep_count}회")
else:
    print("  → 3개월 연속 실패자 없음 확인")

# 특정 직원 추적 (디버깅용)
print("\n" + "=" * 80)
print("🔍 특정 직원 추적 (예: 622070194)")
print("=" * 80)

test_id = '622070194'
print(f"\n직원 {test_id}:")
print(f"  7월 실패: {'예' if test_id in july_unique else '아니오'}")
print(f"  8월 실패: {'예' if test_id in aug_unique else '아니오'}")
print(f"  9월 실패: {'예' if test_id in sep_unique else '아니오'}")

if test_id in july_unique:
    print(f"    7월 실패 횟수: {(july_fail == test_id).sum()}회")
if test_id in aug_unique:
    print(f"    8월 실패 횟수: {(aug_fail == test_id).sum()}회")
if test_id in sep_unique:
    print(f"    9월 실패 횟수: {(sep_fail == test_id).sum()}회")

# 실제로 3개월 연속인지 확인
if test_id in july_unique and test_id in aug_unique and test_id in sep_unique:
    print(f"  → ✅ 3개월 연속 실패!")
else:
    print(f"  → ❌ 3개월 연속 실패 아님")

print("\n" + "=" * 80)
print("💡 최종 결론")
print("=" * 80)
print(f"3개월 연속 AQL 실패자: {len(all_three)}명")
if all_three:
    print(f"실패자 ID: {sorted(all_three)}")

    # Excel 데이터와 매칭
    excel_df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')

    print("\n직원 정보:")
    for emp_id in sorted(all_three):
        emp_row = excel_df[excel_df['Employee No'].astype(str) == emp_id]
        if not emp_row.empty:
            name = emp_row.iloc[0]['Full Name']
            position = emp_row.iloc[0]['QIP POSITION 1ST  NAME']
            print(f"  - {emp_id}: {name} ({position})")
else:
    print("Single Source of Truth 원칙에 따라 실제 데이터 확인 결과:")
    print("  - 7, 8, 9월 각각 실패자는 있지만")
    print("  - 3개월 모두 실패한 직원은 없음")
    print("  - 대시보드 표시 '0명'이 정확함")