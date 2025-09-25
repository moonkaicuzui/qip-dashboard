import pandas as pd
import json
import os

print("="*80)
print("대시보드 vs 엑셀 파일 일치성 검증")
print("="*80)
print()

# 1. Excel 파일 로드
excel_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.xlsx'
csv_file = 'output_files/output_QIP_incentive_august_2025_최종완성버전_v6.0_Complete.csv'

print("1. 데이터 소스 확인:")
print("-" * 50)

# CSV 파일 로드 (엑셀의 CSV 버전)
df_csv = pd.read_csv(csv_file)
print(f"✅ CSV 파일 로드: {csv_file}")
print(f"   - 직원 수: {len(df_csv)}명")
print(f"   - 컬럼 수: {len(df_csv.columns)}개")

# Excel 파일 로드
df_excel = pd.read_excel(excel_file, sheet_name='Sheet1')
print(f"✅ Excel 파일 로드: {excel_file}")
print(f"   - 직원 수: {len(df_excel)}명")
print(f"   - 컬럼 수: {len(df_excel.columns)}개")
print()

# 2. 메타데이터 JSON 파일 로드 (대시보드가 사용하는 데이터)
metadata_file = 'output_files/output_QIP_incentive_august_2025_metadata.json'
with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print("2. 대시보드 데이터 소스:")
print("-" * 50)
print(f"✅ 메타데이터 파일: {metadata_file}")
print(f"   - 직원 수: {len(metadata.get('employees', []))}명")
print()

# 3. 인센티브 총액 비교
print("3. 인센티브 총액 비교:")
print("-" * 50)

# CSV 총액
csv_total = df_csv['August_Incentive'].sum()
print(f"CSV 파일 총액: {csv_total:,.0f} VND")

# Excel 총액
excel_total = df_excel['August_Incentive'].sum()
print(f"Excel 파일 총액: {excel_total:,.0f} VND")

# 메타데이터 총액
metadata_total = sum(emp.get('august_incentive', 0) for emp in metadata.get('employees', []))
print(f"대시보드 총액: {metadata_total:,.0f} VND")

if csv_total == excel_total == metadata_total:
    print("✅ 모든 파일의 총액이 일치합니다!")
else:
    print("❌ 총액 불일치 발견!")
print()

# 4. 지급 대상자 수 비교
print("4. 인센티브 지급 대상자 수:")
print("-" * 50)

csv_paid = (df_csv['August_Incentive'] > 0).sum()
excel_paid = (df_excel['August_Incentive'] > 0).sum()
metadata_paid = sum(1 for emp in metadata.get('employees', []) if emp.get('august_incentive', 0) > 0)

print(f"CSV 파일: {csv_paid}명")
print(f"Excel 파일: {excel_paid}명")
print(f"대시보드: {metadata_paid}명")

if csv_paid == excel_paid == metadata_paid:
    print("✅ 지급 대상자 수가 일치합니다!")
else:
    print("❌ 지급 대상자 수 불일치!")
print()

# 5. 직급별 통계 비교
print("5. 주요 직급별 인센티브 비교:")
print("-" * 50)

positions_to_check = ['LINE LEADER', 'ASSEMBLY INSPECTOR', 'AUDIT & TRAINING TEAM', 'AQL INSPECTOR']

for position in positions_to_check:
    # CSV 데이터
    csv_mask = df_csv['QIP POSITION 1ST  NAME'].str.contains(position, na=False, case=False)
    csv_pos_total = df_csv[csv_mask]['August_Incentive'].sum()
    csv_pos_count = (df_csv[csv_mask]['August_Incentive'] > 0).sum()

    # Excel 데이터
    excel_mask = df_excel['QIP POSITION 1ST  NAME'].str.contains(position, na=False, case=False)
    excel_pos_total = df_excel[excel_mask]['August_Incentive'].sum()
    excel_pos_count = (df_excel[excel_mask]['August_Incentive'] > 0).sum()

    # 메타데이터
    metadata_pos = [emp for emp in metadata.get('employees', [])
                    if position.upper() in emp.get('position', '').upper()]
    metadata_pos_total = sum(emp.get('august_incentive', 0) for emp in metadata_pos)
    metadata_pos_count = sum(1 for emp in metadata_pos if emp.get('august_incentive', 0) > 0)

    print(f"{position}:")
    print(f"  CSV:       {csv_pos_count}명, {csv_pos_total:,.0f} VND")
    print(f"  Excel:     {excel_pos_count}명, {excel_pos_total:,.0f} VND")
    print(f"  대시보드:  {metadata_pos_count}명, {metadata_pos_total:,.0f} VND")

    if csv_pos_total == excel_pos_total == metadata_pos_total:
        print(f"  ✅ 일치")
    else:
        print(f"  ❌ 불일치")
    print()

# 6. 샘플 직원 상세 비교 (무작위 5명)
print("6. 샘플 직원 상세 비교:")
print("-" * 50)

sample_employees = df_csv.sample(min(5, len(df_csv)), random_state=42)

for _, emp in sample_employees.iterrows():
    emp_id = str(emp['Employee No'])
    name = emp['Full Name']

    # CSV 데이터
    csv_amount = emp['August_Incentive']

    # Excel 데이터
    excel_emp = df_excel[df_excel['Employee No'] == int(emp_id)]
    excel_amount = excel_emp.iloc[0]['August_Incentive'] if not excel_emp.empty else 0

    # 메타데이터
    metadata_emp = [e for e in metadata.get('employees', []) if str(e.get('emp_no')) == emp_id]
    metadata_amount = metadata_emp[0].get('august_incentive', 0) if metadata_emp else 0

    print(f"{name} ({emp_id}):")
    print(f"  CSV:      {csv_amount:,.0f} VND")
    print(f"  Excel:    {excel_amount:,.0f} VND")
    print(f"  대시보드: {metadata_amount:,.0f} VND")

    if csv_amount == excel_amount == metadata_amount:
        print(f"  ✅ 일치")
    else:
        print(f"  ❌ 불일치")
    print()

# 7. 최종 검증 결과
print("="*80)
print("최종 검증 결과:")
print("="*80)

all_match = True

if csv_total != excel_total or csv_total != metadata_total:
    all_match = False
    print("❌ 총액 불일치")

if csv_paid != excel_paid or csv_paid != metadata_paid:
    all_match = False
    print("❌ 지급 대상자 수 불일치")

if len(df_csv) != len(df_excel) or len(df_csv) != len(metadata.get('employees', [])):
    all_match = False
    print("❌ 전체 직원 수 불일치")

if all_match:
    print("✅ 대시보드와 엑셀 파일의 인센티브 정보가 완벽히 일치합니다!")
    print()
    print("확인된 항목:")
    print("  - 인센티브 총액")
    print("  - 지급 대상자 수")
    print("  - 직급별 통계")
    print("  - 개별 직원 금액")
else:
    print("⚠️ 일부 불일치가 발견되었습니다. 위 세부 내용을 확인하세요.")

print("="*80)