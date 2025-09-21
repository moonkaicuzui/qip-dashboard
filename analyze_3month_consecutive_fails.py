#!/usr/bin/env python3
"""
3개월 연속 AQL 실패 분석 스크립트
Single Source of Truth 원칙: AQL history 파일에서 직접 분석
No Fake Data 원칙: 실제 데이터만 사용
"""

import pandas as pd
from pathlib import Path
import json

def analyze_monthly_fails(month_file):
    """각 월의 AQL 실패자 분석"""
    df = pd.read_csv(month_file, encoding='utf-8-sig')

    # 컬럼명 확인
    print(f"\n  분석 파일: {month_file.name}")

    # RESULT와 EMPLOYEE NO 컬럼 직접 사용
    if 'RESULT' not in df.columns:
        print(f"  ⚠️ RESULT 컬럼을 찾을 수 없습니다")
        return {}

    if 'EMPLOYEE NO' not in df.columns:
        print(f"  ⚠️ EMPLOYEE NO 컬럼을 찾을 수 없습니다")
        return {}

    # Fail 케이스 필터링
    fail_df = df[df['RESULT'].str.upper() == 'FAIL']
    print(f"  → FAIL 레코드 수: {len(fail_df)}")

    # 직원별 실패 횟수 집계
    fail_counts = fail_df['EMPLOYEE NO'].value_counts().to_dict()
    print(f"  → FAIL 보유 직원 수: {len(fail_counts)}")

    return fail_counts

# AQL history 디렉토리
aql_dir = Path('input_files/AQL history')

# 각 월별 실패 데이터 수집
monthly_fails = {
    'July': {},
    'August': {},
    'September': {}
}

print("=" * 80)
print("📊 3개월 연속 AQL 실패 분석 (Single Source of Truth)")
print("=" * 80)

# 7월 데이터
july_file = aql_dir / '1.HSRG AQL REPORT-JULY.2025.csv'
if july_file.exists():
    monthly_fails['July'] = analyze_monthly_fails(july_file)
    print(f"\n7월 AQL 실패자: {len(monthly_fails['July'])}명")
    print(f"  상위 5명: {dict(list(monthly_fails['July'].items())[:5])}")

# 8월 데이터
august_file = aql_dir / '1.HSRG AQL REPORT-AUGUST.2025.csv'
if august_file.exists():
    monthly_fails['August'] = analyze_monthly_fails(august_file)
    print(f"\n8월 AQL 실패자: {len(monthly_fails['August'])}명")
    print(f"  상위 5명: {dict(list(monthly_fails['August'].items())[:5])}")

# 9월 데이터
september_file = aql_dir / '1.HSRG AQL REPORT-SEPTEMBER.2025.csv'
if september_file.exists():
    monthly_fails['September'] = analyze_monthly_fails(september_file)
    print(f"\n9월 AQL 실패자: {len(monthly_fails['September'])}명")
    print(f"  상위 5명: {dict(list(monthly_fails['September'].items())[:5])}")

# 3개월 연속 실패자 찾기
print("\n" + "=" * 80)
print("🔍 3개월 연속 실패 분석")
print("=" * 80)

# 모든 직원 ID 수집
all_employees = set()
all_employees.update(monthly_fails['July'].keys())
all_employees.update(monthly_fails['August'].keys())
all_employees.update(monthly_fails['September'].keys())

# 3개월 연속 실패자 찾기
consecutive_3month = []
for emp_id in all_employees:
    if emp_id and str(emp_id) != '0':  # 유효한 ID만
        july_fail = emp_id in monthly_fails['July'] and monthly_fails['July'][emp_id] > 0
        aug_fail = emp_id in monthly_fails['August'] and monthly_fails['August'][emp_id] > 0
        sep_fail = emp_id in monthly_fails['September'] and monthly_fails['September'][emp_id] > 0

        if july_fail and aug_fail and sep_fail:
            consecutive_3month.append({
                'emp_id': emp_id,
                'july_fails': monthly_fails['July'].get(emp_id, 0),
                'aug_fails': monthly_fails['August'].get(emp_id, 0),
                'sep_fails': monthly_fails['September'].get(emp_id, 0),
                'total_fails': (monthly_fails['July'].get(emp_id, 0) +
                               monthly_fails['August'].get(emp_id, 0) +
                               monthly_fails['September'].get(emp_id, 0))
            })

# 결과 출력
if consecutive_3month:
    print(f"\n✅ 3개월 연속 AQL 실패자: {len(consecutive_3month)}명")
    print("\n상세 정보:")
    print("-" * 80)
    for emp in sorted(consecutive_3month, key=lambda x: x['total_fails'], reverse=True):
        print(f"직원 ID: {emp['emp_id']}")
        print(f"  7월: {emp['july_fails']}회, 8월: {emp['aug_fails']}회, 9월: {emp['sep_fails']}회")
        print(f"  총 실패: {emp['total_fails']}회")
else:
    print("\n❌ 3개월 연속 AQL 실패자: 0명")
    print("\n분석 결과:")
    print("  - 7월, 8월, 9월 모두에서 실패한 직원이 없습니다.")
    print("  - 각 월별로 실패자는 있지만 3개월 연속은 없습니다.")

# 2개월 연속 실패자 분석 (참고)
print("\n" + "=" * 80)
print("📈 참고: 2개월 연속 실패 분석")
print("=" * 80)

two_month_consecutive = []

# 7-8월 연속
for emp_id in all_employees:
    if emp_id and str(emp_id) != '0':
        july_fail = emp_id in monthly_fails['July'] and monthly_fails['July'][emp_id] > 0
        aug_fail = emp_id in monthly_fails['August'] and monthly_fails['August'][emp_id] > 0
        sep_fail = emp_id in monthly_fails['September'] and monthly_fails['September'][emp_id] > 0

        if (july_fail and aug_fail) or (aug_fail and sep_fail):
            period = "7-8월" if (july_fail and aug_fail and not sep_fail) else (
                     "8-9월" if (aug_fail and sep_fail and not july_fail) else
                     "7-8-9월" if (july_fail and aug_fail and sep_fail) else "")
            if period and period != "7-8-9월":  # 3개월 연속은 제외
                two_month_consecutive.append({
                    'emp_id': emp_id,
                    'period': period
                })

print(f"2개월 연속 실패자: {len(two_month_consecutive)}명")
if two_month_consecutive[:5]:
    print("샘플:")
    for emp in two_month_consecutive[:5]:
        print(f"  - {emp['emp_id']}: {emp['period']}")

# 결과 저장
result = {
    'analysis_date': pd.Timestamp.now().isoformat(),
    'monthly_fail_counts': {
        'July': len(monthly_fails['July']),
        'August': len(monthly_fails['August']),
        'September': len(monthly_fails['September'])
    },
    'consecutive_3month_count': len(consecutive_3month),
    'consecutive_3month_employees': consecutive_3month,
    'consecutive_2month_count': len(two_month_consecutive),
    'note': 'Single Source of Truth - AQL history files'
}

output_file = Path('3month_consecutive_analysis.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n💾 분석 결과 저장: {output_file}")
print("\n" + "=" * 80)
print("💡 결론")
print("=" * 80)
print(f"3개월 연속 AQL 실패자: {len(consecutive_3month)}명")
print("Single Source of Truth 원칙 준수: AQL history 파일에서 직접 분석")
print("No Fake Data 원칙 준수: 실제 데이터만 사용")