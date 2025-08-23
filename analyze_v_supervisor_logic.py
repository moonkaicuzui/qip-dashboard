#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(V) SUPERVISOR 조건 평가 로직 분석
"""

import pandas as pd
from pathlib import Path

# CSV 파일 읽기
csv_path = Path("output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv")
df = pd.read_csv(csv_path)

# (V) SUPERVISOR만 필터링
v_supervisor_df = df[df['QIP POSITION 1ST  NAME'] == '(V) SUPERVISOR'].copy()

print("=" * 80)
print("(V) SUPERVISOR 조건 평가 분석")
print("=" * 80)
print(f"\n총 {len(v_supervisor_df)}명의 (V) SUPERVISOR\n")

# 각 직원별 상세 분석
for idx, row in v_supervisor_df.iterrows():
    emp_id = row['Employee No']
    name = row['Full Name']
    incentive = row['July_Incentive']
    actual_days = row['Actual Working Days']
    
    print(f"\n직원: {emp_id} - {name}")
    print(f"  실제 근무일: {actual_days}일")
    print(f"  인센티브: {incentive:,} VND")
    print("\n  출근 조건 평가:")
    
    # 조건 1: 실제 근무일이 0일인가?
    cond1 = row['attendancy condition 1 - acctual working days is zero']
    print(f"    1. 실제 근무일 0일: {cond1} (yes=실패, no=통과)")
    print(f"       → 실제값: {actual_days}일 → {'실패' if cond1 == 'yes' else '통과'}")
    
    # 조건 2: 무단결근 2일 초과
    cond2 = row['attendancy condition 2 - unapproved Absence Day is more than 2 days']
    print(f"    2. 무단결근 >2일: {cond2} (yes=실패, no=통과)")
    
    # 조건 3: 결근율 12% 초과
    cond3 = row['attendancy condition 3 - absent % is over 12%']
    print(f"    3. 결근율 >12%: {cond3} (yes=실패, no=통과)")
    
    # 조건 4: 최소 근무일 12일 미만 (여기가 문제!)
    cond4 = row['attendancy condition 4 - minimum working days']
    print(f"    4. 최소 근무일 <12일: {cond4} (yes=실패, no=통과)")
    print(f"       → 실제값: {actual_days}일 → {'실패 (< 12일)' if actual_days < 12 else '통과 (≥ 12일)'}")
    print(f"       → CSV 값: {cond4} → {'정상' if cond4 == 'no' else '오류!'}")
    
    # (V) SUPERVISOR는 출근 조건만 평가
    all_attendance_pass = (cond1 == 'no' and cond2 == 'no' and 
                          cond3 == 'no' and cond4 == 'no')
    
    print(f"\n  최종 평가:")
    print(f"    모든 출근 조건 통과: {all_attendance_pass}")
    print(f"    인센티브 지급: {incentive:,} VND")
    
    if all_attendance_pass and incentive > 0:
        print(f"    → ✅ 정상: 조건 통과, 인센티브 지급")
    elif not all_attendance_pass and incentive == 0:
        print(f"    → ✅ 정상: 조건 실패, 인센티브 미지급")
    elif all_attendance_pass and incentive == 0:
        print(f"    → ⚠️ 문제: 조건 통과했으나 인센티브 미지급")
    else:
        print(f"    → ⚠️ 문제: 조건 실패했으나 인센티브 지급됨")
    
    print("-" * 60)

# 전체 통계
print("\n" + "=" * 80)
print("전체 통계")
print("=" * 80)

# 실제로 조건 4를 통과한 사람 (실제 근무일 >= 12)
actual_pass_cond4 = (v_supervisor_df['Actual Working Days'] >= 12).sum()
csv_pass_cond4 = (v_supervisor_df['attendancy condition 4 - minimum working days'] == 'no').sum()

print(f"\n조건 4 (최소 근무일 ≥12일) 분석:")
print(f"  실제 데이터 기준 통과: {actual_pass_cond4}/{len(v_supervisor_df)} ({actual_pass_cond4/len(v_supervisor_df)*100:.1f}%)")
print(f"  CSV 컬럼 기준 통과: {csv_pass_cond4}/{len(v_supervisor_df)} ({csv_pass_cond4/len(v_supervisor_df)*100:.1f}%)")

# 인센티브 지급 현황
paid_count = (v_supervisor_df['July_Incentive'] > 0).sum()
print(f"\n인센티브 지급 현황:")
print(f"  지급: {paid_count}/{len(v_supervisor_df)} ({paid_count/len(v_supervisor_df)*100:.1f}%)")

# 모든 조건 통과 여부 체크
all_pass = []
for idx, row in v_supervisor_df.iterrows():
    pass_all = (
        row['attendancy condition 1 - acctual working days is zero'] == 'no' and
        row['attendancy condition 2 - unapproved Absence Day is more than 2 days'] == 'no' and
        row['attendancy condition 3 - absent % is over 12%'] == 'no' and
        row['attendancy condition 4 - minimum working days'] == 'no'
    )
    all_pass.append(pass_all)

all_pass_count = sum(all_pass)
print(f"\n모든 출근 조건 통과:")
print(f"  통과: {all_pass_count}/{len(v_supervisor_df)} ({all_pass_count/len(v_supervisor_df)*100:.1f}%)")

print("\n" + "=" * 80)
print("결론")
print("=" * 80)
print("\n문제점:")
print("1. CSV의 'attendancy condition 4' 컬럼은 역논리 사용:")
print("   - 'yes' = 조건 실패 (근무일 < 12)")
print("   - 'no' = 조건 통과 (근무일 ≥ 12)")
print("\n2. 대시보드가 이 역논리를 잘못 해석하고 있음")
print("3. 실제로는 모든 (V) SUPERVISOR가 23일 근무로 조건 4를 통과함")
print("4. 하지만 대시보드는 0% 충족률로 표시하고 있음")