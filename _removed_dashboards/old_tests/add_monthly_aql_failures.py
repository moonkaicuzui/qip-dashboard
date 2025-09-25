#!/usr/bin/env python3
"""
Excel 파일에 7월, 8월 AQL 실패 건수 추가
Single Source of Truth 원칙 준수
"""

import pandas as pd
from pathlib import Path

def get_monthly_aql_failures(month_file):
    """각 월의 AQL 실패 건수 집계"""
    df = pd.read_csv(month_file, encoding='utf-8-sig')

    # FAIL 레코드만 필터링
    fail_df = df[df['RESULT'].str.upper() == 'FAIL']

    # 직원별 실패 횟수 집계
    fail_counts = fail_df.groupby('EMPLOYEE NO').size().to_dict()

    # ID 표준화 (float 제거)
    standardized = {}
    for emp_id, count in fail_counts.items():
        emp_id_str = str(emp_id).strip().replace('.0', '')
        standardized[emp_id_str] = count

    return standardized

print("=" * 80)
print("📊 7, 8, 9월 AQL 실패 건수를 Excel에 추가")
print("=" * 80)

# AQL history 파일에서 각 월별 실패 데이터 수집
aql_dir = Path('input_files/AQL history')

print("\n📈 월별 AQL 실패 데이터 수집 중...")

# 7월 데이터
july_fails = get_monthly_aql_failures(aql_dir / '1.HSRG AQL REPORT-JULY.2025.csv')
print(f"  7월: {len(july_fails)}명 실패")

# 8월 데이터
aug_fails = get_monthly_aql_failures(aql_dir / '1.HSRG AQL REPORT-AUGUST.2025.csv')
print(f"  8월: {len(aug_fails)}명 실패")

# 9월 데이터
sep_fails = get_monthly_aql_failures(aql_dir / '1.HSRG AQL REPORT-SEPTEMBER.2025.csv')
print(f"  9월: {len(sep_fails)}명 실패")

# Excel 파일 로드
excel_path = Path('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')
df = pd.read_csv(excel_path, encoding='utf-8-sig')

print(f"\n📝 Excel 파일 업데이트 중...")
print(f"  파일: {excel_path}")
print(f"  총 직원: {len(df)}명")

# Employee No 표준화
df['emp_no_str'] = df['Employee No'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

# 새로운 컬럼 추가
df['July_AQL_Failures'] = 0
df['August_AQL_Failures'] = 0

# 기존 September 컬럼 확인
if 'September AQL Failures' not in df.columns:
    df['September AQL Failures'] = 0

# 각 월별 실패 건수 매핑
july_updated = 0
aug_updated = 0
sep_updated = 0

for idx, row in df.iterrows():
    emp_id = row['emp_no_str']

    # 7월 실패 건수
    if emp_id in july_fails:
        df.loc[idx, 'July_AQL_Failures'] = july_fails[emp_id]
        july_updated += 1

    # 8월 실패 건수
    if emp_id in aug_fails:
        df.loc[idx, 'August_AQL_Failures'] = aug_fails[emp_id]
        aug_updated += 1

    # 9월 실패 건수 (기존 값 검증)
    if emp_id in sep_fails:
        actual_sep_fails = sep_fails[emp_id]
        existing_sep_fails = df.loc[idx, 'September AQL Failures']

        if existing_sep_fails != actual_sep_fails:
            print(f"  ⚠️ 9월 데이터 불일치: {emp_id} - Excel: {existing_sep_fails}, 실제: {actual_sep_fails}")
            df.loc[idx, 'September AQL Failures'] = actual_sep_fails
            sep_updated += 1

# 3개월 총 실패 건수 컬럼 추가
df['Total_3Month_AQL_Failures'] = df['July_AQL_Failures'] + df['August_AQL_Failures'] + df['September AQL Failures']

# 실패 패턴 컬럼 추가 (어느 달에 실패했는지)
def get_fail_pattern(row):
    pattern = []
    if row['July_AQL_Failures'] > 0:
        pattern.append('Jul')
    if row['August_AQL_Failures'] > 0:
        pattern.append('Aug')
    if row['September AQL Failures'] > 0:
        pattern.append('Sep')
    return '-'.join(pattern) if pattern else 'None'

df['AQL_Fail_Pattern'] = df.apply(get_fail_pattern, axis=1)

print(f"\n✅ 업데이트 완료:")
print(f"  7월 실패 건수 추가: {july_updated}명")
print(f"  8월 실패 건수 추가: {aug_updated}명")
print(f"  9월 실패 건수 검증: {sep_updated}명 수정")

# 통계 출력
print(f"\n📊 실패 패턴 분석:")
pattern_counts = df['AQL_Fail_Pattern'].value_counts()
for pattern, count in pattern_counts.head(10).items():
    if pattern != 'None':
        print(f"  {pattern}: {count}명")

# 3개월 모두 실패한 직원 확인
three_month_fail = df[df['AQL_Fail_Pattern'] == 'Jul-Aug-Sep']
print(f"\n🔍 7-8-9월 모두 실패: {len(three_month_fail)}명")

if not three_month_fail.empty:
    print("  상세 정보:")
    for idx, row in three_month_fail.head(5).iterrows():
        print(f"    - {row['Employee No']}: {row['Full Name']}")
        print(f"      7월: {row['July_AQL_Failures']}회, 8월: {row['August_AQL_Failures']}회, 9월: {row['September AQL Failures']}회")

# 임시 컬럼 제거
df = df.drop(columns=['emp_no_str'])

# 백업 생성
backup_path = excel_path.with_name(excel_path.stem + '_before_monthly_aql.csv')
pd.read_csv(excel_path, encoding='utf-8-sig').to_csv(backup_path, index=False, encoding='utf-8-sig')
print(f"\n💾 백업 생성: {backup_path}")

# 업데이트된 파일 저장
df.to_csv(excel_path, index=False, encoding='utf-8-sig')
print(f"💾 CSV 파일 업데이트: {excel_path}")

# Excel XLSX 파일도 업데이트
excel_xlsx = excel_path.with_suffix('.xlsx')
df.to_excel(excel_xlsx, index=False, engine='openpyxl')
print(f"💾 Excel XLSX 파일 업데이트: {excel_xlsx}")

# 샘플 데이터 출력
print(f"\n📋 샘플 데이터 (실패 기록이 있는 직원):")
sample = df[df['Total_3Month_AQL_Failures'] > 0][
    ['Employee No', 'Full Name', 'July_AQL_Failures', 'August_AQL_Failures',
     'September AQL Failures', 'Total_3Month_AQL_Failures', 'AQL_Fail_Pattern']
].head(5)

if not sample.empty:
    print(sample.to_string(index=False))

print("\n" + "=" * 80)
print("✅ 작업 완료:")
print("  - 7월 AQL 실패 건수 추가 (July_AQL_Failures)")
print("  - 8월 AQL 실패 건수 추가 (August_AQL_Failures)")
print("  - 9월 AQL 실패 건수 유지 (September AQL Failures)")
print("  - 3개월 총 실패 건수 추가 (Total_3Month_AQL_Failures)")
print("  - 실패 패턴 추가 (AQL_Fail_Pattern)")
print("=" * 80)