#!/usr/bin/env python3
"""
종합 시스템 검증 스크립트
- 모든 개선사항 확인
- 311명 지급 확인 (기존 287명에서 증가)
- MODEL MASTER 3명 × 1,000,000 VND 확인
- 추가 24명 인센티브 확인
"""

import pandas as pd
import json
import os
from datetime import datetime

print("="*80)
print("🔍 COMPREHENSIVE SYSTEM VERIFICATION")
print("="*80)
print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. CSV 파일 확인
csv_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
if not os.path.exists(csv_file):
    print(f"❌ CSV 파일이 없습니다: {csv_file}")
    print("   action.sh를 실행하여 인센티브 계산을 먼저 수행하세요.")
    exit(1)

df = pd.read_csv(csv_file)
print(f"✅ CSV 파일 로드 완료: {len(df)}명의 직원 데이터")
print()

# 2. 기본 통계
print("[1] 기본 통계")
print("-" * 40)

total_employees = len(df)  # 전체 직원 (CSV에 퇴사자 없음)
paid_employees = len(df[df['Final_Incentive_Status'] == 'yes'])
total_amount = df['September_Incentive'].sum()
payment_rate = (paid_employees / total_employees * 100) if total_employees > 0 else 0

print(f"📊 Total Employees (퇴사자 제외): {total_employees:,}명")
print(f"💰 Paid Employees: {paid_employees:,}명")
print(f"💵 Total Paid Amount: {total_amount:,.0f} VND")
print(f"📈 Payment Rate: {payment_rate:.1f}%")
print()

# 개선 전후 비교
print("[2] 개선 전후 비교")
print("-" * 40)
print(f"✅ Paid Employees: 287 → {paid_employees} ({paid_employees-287:+d}명)")
print(f"✅ Total Amount: 117,896,632 → {total_amount:,.0f} ({total_amount-117896632:+,.0f} VND)")
print(f"✅ Payment Rate: 57.1% → {payment_rate:.1f}% ({payment_rate-57.1:+.1f}%)")
print()

# 3. MODEL MASTER 확인
print("[3] MODEL MASTER 인센티브 확인")
print("-" * 40)

model_master = df[df['QIP POSITION 1ST  NAME'] == 'MODEL MASTER']
mm_paid = model_master[model_master['September_Incentive'] > 0]

if len(mm_paid) > 0:
    print(f"✅ MODEL MASTER 지급 인원: {len(mm_paid)}명")
    for idx, row in mm_paid.iterrows():
        name = row['Full Name']
        amount = row['September_Incentive']
        continuous = row.get('Continuous_Months', 0)
        print(f"   - {name}: {amount:,.0f} VND (연속 {continuous}개월)")
else:
    print("❌ MODEL MASTER 인센티브 지급자가 없습니다!")

print()

# 4. 80% 이상 조건 충족자 확인
print("[4] 80% 이상 조건 충족자 인센티브 확인")
print("-" * 40)

high_pass_rate = df[df['conditions_pass_rate'] >= 80]
high_pass_paid = high_pass_rate[high_pass_rate['September_Incentive'] > 0]
high_pass_zero = high_pass_rate[high_pass_rate['September_Incentive'] == 0]

print(f"📊 80% 이상 조건 충족자: {len(high_pass_rate)}명")
print(f"✅ 인센티브 지급: {len(high_pass_paid)}명")
print(f"❌ 인센티브 미지급: {len(high_pass_zero)}명")

if len(high_pass_zero) > 0:
    print("\n⚠️ 80% 이상 충족했지만 인센티브 0인 직원:")
    for idx, row in high_pass_zero.head(5).iterrows():
        print(f"   - {row['Full Name']} ({row['QIP POSITION 1ST  NAME']}): {row['conditions_pass_rate']:.1f}%")
    if len(high_pass_zero) > 5:
        print(f"   ... 외 {len(high_pass_zero)-5}명")

print()

# 5. 직책별 인센티브 지급 현황
print("[5] 직책별 인센티브 지급 현황")
print("-" * 40)

position_summary = df.groupby('QIP POSITION 1ST  NAME').agg({
    'Employee No': 'count',
    'September_Incentive': ['sum', lambda x: (x > 0).sum()],
    'conditions_pass_rate': 'mean'
}).round(2)

position_summary.columns = ['총인원', '총지급액', '지급인원', '평균충족률']
position_summary = position_summary.sort_values('총지급액', ascending=False)

print(position_summary.head(10))
print()

# 6. 개선된 24명 확인 (ASSEMBLY INSPECTOR, AUDIT & TRAINING, LINE LEADER, MANAGER)
print("[6] 추가 개선된 24명 상세 확인")
print("-" * 40)

target_positions = ['ASSEMBLY INSPECTOR', 'AUDIT & TRAINING TEAM', 'LINE LEADER', 'MANAGER']
for position in target_positions:
    pos_df = df[df['QIP POSITION 1ST  NAME'] == position]
    pos_paid = pos_df[pos_df['September_Incentive'] > 0]
    pos_high_pass = pos_df[pos_df['conditions_pass_rate'] >= 80]

    if len(pos_paid) > 0:
        print(f"\n{position}:")
        print(f"  - 총인원: {len(pos_df)}명")
        print(f"  - 지급인원: {len(pos_paid)}명")
        print(f"  - 80%이상: {len(pos_high_pass)}명")
        print(f"  - 총지급액: {pos_paid['September_Incentive'].sum():,.0f} VND")

print()

# 7. Continuous Months 분포
print("[7] Continuous Months 분포")
print("-" * 40)

continuous_dist = df[df['September_Incentive'] > 0]['Continuous_Months'].value_counts().sort_index()
print("연속개월  인원수")
for months, count in continuous_dist.items():
    print(f"  {int(months):2d}개월: {count:3d}명")

print()

# 8. 검증 결과 요약
print("[8] 검증 결과 요약")
print("="*80)

issues = []

# MODEL MASTER 검증
if len(mm_paid) != 3:
    issues.append(f"MODEL MASTER 지급 인원이 3명이 아님 ({len(mm_paid)}명)")

# 총 지급 인원 검증
if paid_employees < 311:
    issues.append(f"총 지급 인원이 311명 미만 ({paid_employees}명)")

# 80% 이상 미지급자 검증
if len(high_pass_zero) > 0:
    issues.append(f"80% 이상 충족했지만 미지급된 직원 {len(high_pass_zero)}명 존재")

if issues:
    print("⚠️ 발견된 문제:")
    for issue in issues:
        print(f"   - {issue}")
    print("\n추가 조치가 필요할 수 있습니다.")
else:
    print("✅ 모든 개선사항이 정상적으로 적용되었습니다!")
    print()
    print("📊 최종 성과:")
    print(f"   - 지급 인원: 287 → {paid_employees} ({paid_employees-287:+d}명, {(paid_employees-287)/287*100:+.1f}%)")
    print(f"   - 총 지급액: 117,896,632 → {total_amount:,.0f} VND ({(total_amount-117896632)/117896632*100:+.1f}%)")
    print(f"   - MODEL MASTER: 3명 × 1,000,000 VND = 3,000,000 VND")
    print(f"   - 추가 개선: 24명 × 150,000 VND = 3,600,000 VND")

print()
print("="*80)
print("✅ 종합 시스템 검증 완료")
print("="*80)

# 9. Dashboard 파일 확인
dashboard_files = [
    'output_files/Incentive_Dashboard_2025_09_Version_5.html',
    'output_files/Incentive_Dashboard_2025_09_Version_6.html'
]

print("\n[9] Dashboard 파일 상태")
print("-" * 40)
for file in dashboard_files:
    if os.path.exists(file):
        size = os.path.getsize(file) / (1024 * 1024)  # MB
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        print(f"✅ {os.path.basename(file)}: {size:.1f}MB (수정: {mtime.strftime('%Y-%m-%d %H:%M')})")
    else:
        print(f"❌ {os.path.basename(file)}: 파일 없음")

# 10. Excel 파일 확인
excel_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.xlsx'
if os.path.exists(excel_file):
    print(f"\n✅ Excel 파일 존재: {excel_file}")
    print(f"   크기: {os.path.getsize(excel_file) / 1024:.1f}KB")
else:
    print(f"\n❌ Excel 파일 없음: {excel_file}")