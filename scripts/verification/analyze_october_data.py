#!/usr/bin/env python3
"""
10월 인센티브 보고서 원본 데이터 기반 문제점 분석
"""

import pandas as pd
import json
import sys
from pathlib import Path

def load_config():
    """설정 파일 로드"""
    config_path = Path("config_files/config_october_2025.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_position_matrix():
    """직급 조건 매트릭스 로드"""
    matrix_path = Path("config_files/position_condition_matrix.json")
    with open(matrix_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_output_data():
    """출력 데이터 분석"""
    # CSV 파일 로드 (Try V9.0 first, then fallback to V8.02 - 버전 전환 호환성)
    output_path_v9 = Path("output_files/output_QIP_incentive_october_2025_Complete_V9.0_Complete.csv")
    output_path_v8 = Path("output_files/output_QIP_incentive_october_2025_Complete_V8.02_Complete.csv")

    if output_path_v9.exists():
        output_path = output_path_v9
    elif output_path_v8.exists():
        output_path = output_path_v8
    else:
        output_path = output_path_v9  # For error message

    df = pd.read_csv(output_path, encoding='utf-8-sig')

    print("="*100)
    print(" "*30 + "📊 10월 인센티브 보고서 데이터 분석")
    print("="*100)
    print()

    # 기본 통계
    print("📌 기본 통계")
    print("-"*100)
    print(f"총 직원 수: {len(df):,}명")
    print(f"인센티브 지급 대상: {len(df[df['Final Incentive amount'] > 0]):,}명 ({len(df[df['Final Incentive amount'] > 0])/len(df)*100:.1f}%)")
    print(f"인센티브 미지급: {len(df[df['Final Incentive amount'] == 0]):,}명 ({len(df[df['Final Incentive amount'] == 0])/len(df)*100:.1f}%)")
    print(f"총 인센티브 금액: ₫{df['Final Incentive amount'].sum():,.0f}")
    print()

    # 조건 통과율 분석
    print("📌 10개 조건 통과율 분석")
    print("-"*100)

    condition_names = {
        1: ('cond_1_attendance_rate', '출근율 >= 88%'),
        2: ('cond_2_unapproved_absence', '무단결근 <= 2일'),
        3: ('cond_3_actual_working_days', '실제 출근일 > 0'),
        4: ('cond_4_minimum_days', '최소 근무일 >= 12일'),
        5: ('cond_5_aql_personal_failure', '개인 AQL 불량 = 0'),
        6: ('cond_6_aql_continuous', 'AQL 3개월 연속 불량 없음'),
        7: ('cond_7_aql_team_area', '팀/구역 AQL 3개월 연속 불량 없음'),
        8: ('cond_8_area_reject', '구역 리젝률 < 3%'),
        9: ('cond_9_5prs_pass_rate', '5PRS 합격률 >= 95%'),
        10: ('cond_10_5prs_inspection_qty', '5PRS 검사량 >= 100')
    }

    for i in range(1, 11):
        cond_col, cond_desc = condition_names[i]

        if cond_col in df.columns:
            passed = len(df[df[cond_col] == 'PASS'])
            failed = len(df[df[cond_col] == 'FAIL'])
            na = len(df[df[cond_col] == 'NOT_APPLICABLE'])
            total_applicable = passed + failed

            if total_applicable > 0:
                pass_rate = passed / total_applicable * 100
                print(f"조건 {i:2d} ({cond_desc:30s}): PASS {passed:3d}명 ({pass_rate:5.1f}%) | FAIL {failed:3d}명 | N/A {na:3d}명")

    print()

    # 조건 통과율 분포 분석
    print("📌 조건 통과율 분포 (100% 룰 검증)")
    print("-"*100)
    pass_rate_dist = df['conditions_pass_rate'].value_counts().sort_index(ascending=False)
    print(f"{'통과율':<15} {'인원수':<10} {'비율':<10} {'인센티브 지급'}")
    print("-"*100)

    for rate in sorted(pass_rate_dist.index, reverse=True):
        count = pass_rate_dist[rate]
        pct = count / len(df) * 100
        subset = df[df['conditions_pass_rate'] == rate]
        paid_count = len(subset[subset['Final Incentive amount'] > 0])

        # 100% 미만인데 인센티브 받은 경우 경고
        if rate < 100 and paid_count > 0:
            print(f"{rate:>5.1f}%         {count:>5}명     {pct:>5.1f}%      ⚠️  {paid_count}명 지급 (100% 룰 위반 가능성)")
        else:
            print(f"{rate:>5.1f}%         {count:>5}명     {pct:>5.1f}%      {'✅ '+str(paid_count)+'명' if paid_count > 0 else '❌ 미지급'}")

    print()

    # TYPE별 분석
    print("📌 직원 TYPE별 인센티브 분석")
    print("-"*100)

    # ROLE TYPE 분석
    type_analysis = df.groupby('ROLE TYPE STD').agg({
        'Employee No': 'count',
        'Final Incentive amount': ['sum', 'mean', 'max']
    }).round(0)

    type_analysis.columns = ['인원수', '총액', '평균', '최대']
    print(type_analysis.to_string())
    print()

    # Continuous Months 분석
    print("📌 연속 개월수 (Continuous_Months) 분석")
    print("-"*100)
    cm_analysis = df[df['Continuous_Months'] > 0].groupby('Continuous_Months').agg({
        'Employee No': 'count',
        'Final Incentive amount': ['sum', 'mean']
    }).round(0)

    if len(cm_analysis) > 0:
        cm_analysis.columns = ['인원수', '총액', '평균']
        print(cm_analysis.to_string())
    else:
        print("연속 개월수 > 0인 직원 없음")

    print()

    # 문제점 검출
    print("="*100)
    print(" "*35 + "🔍 문제점 검출")
    print("="*100)
    print()

    issues = []

    # 1. 100% 미만인데 인센티브 지급된 경우
    less_than_100 = df[(df['conditions_pass_rate'] < 100) & (df['Final Incentive amount'] > 0)]
    if len(less_than_100) > 0:
        issues.append({
            'severity': 'CRITICAL',
            'category': '100% 룰 위반',
            'count': len(less_than_100),
            'description': f'{len(less_than_100)}명이 조건 통과율 100% 미만인데 인센티브 지급됨',
            'sample': less_than_100[['Employee No', 'Full Name', 'conditions_pass_rate', 'Final Incentive amount']].head(5)
        })

    # 2. 출근일 = 0인데 인센티브 지급된 경우
    zero_workdays = df[(df['Actual Working Days'] == 0) & (df['Final Incentive amount'] > 0)]
    if len(zero_workdays) > 0:
        issues.append({
            'severity': 'CRITICAL',
            'category': '출근일 0일 인센티브 지급',
            'count': len(zero_workdays),
            'description': f'{len(zero_workdays)}명이 실제 출근일 0일인데 인센티브 지급됨',
            'sample': zero_workdays[['Employee No', 'Full Name', 'Actual Working Days', 'Final Incentive amount']].head(5)
        })

    # 3. Continuous Months 불일치 (이전 달 vs 현재 달)
    cm_mismatch = df[
        (df['Previous_Continuous_Months'].notna()) &
        (df['Current_Expected_Months'].notna()) &
        (df['Previous_Continuous_Months'] != df['Current_Expected_Months']) &
        (df['conditions_pass_rate'] == 100)
    ]
    if len(cm_mismatch) > 0:
        issues.append({
            'severity': 'WARNING',
            'category': 'Continuous Months 불일치',
            'count': len(cm_mismatch),
            'description': f'{len(cm_mismatch)}명의 연속 개월수가 예상값과 불일치',
            'sample': cm_mismatch[['Employee No', 'Full Name', 'Previous_Continuous_Months', 'Current_Expected_Months', 'Continuous_Months']].head(5)
        })

    # 4. TYPE-3인데 인센티브 지급된 경우
    type3_paid = df[(df['ROLE TYPE STD'] == 'TYPE-3') & (df['Final Incentive amount'] > 0)]
    if len(type3_paid) > 0:
        issues.append({
            'severity': 'CRITICAL',
            'category': 'TYPE-3 인센티브 지급',
            'count': len(type3_paid),
            'description': f'{len(type3_paid)}명의 TYPE-3 직원에게 인센티브 지급됨 (정책상 0 VND)',
            'sample': type3_paid[['Employee No', 'Full Name', 'ROLE TYPE STD', 'Final Incentive amount']].head(5)
        })

    # 5. 무단 결근 > 2일인데 조건 2 통과
    high_absence_passed = df[
        (df['Unapproved Absences'] > 2) &
        (df['cond_2_unapproved_absence'] == 'PASS')
    ]
    if len(high_absence_passed) > 0:
        issues.append({
            'severity': 'ERROR',
            'category': '조건 2 평가 오류',
            'count': len(high_absence_passed),
            'description': f'{len(high_absence_passed)}명이 무단결근 > 2일인데 조건 2 통과로 평가됨',
            'sample': high_absence_passed[['Employee No', 'Full Name', 'Unapproved Absences', 'cond_2_unapproved_absence']].head(5)
        })

    # 6. 출근율 < 88%인데 조건 1 통과
    low_attendance_passed = df[
        (df['출근율_Attendance_Rate_Percent'] < 88) &
        (df['cond_1_attendance_rate'] == 'PASS')
    ]
    if len(low_attendance_passed) > 0:
        issues.append({
            'severity': 'ERROR',
            'category': '조건 1 평가 오류',
            'count': len(low_attendance_passed),
            'description': f'{len(low_attendance_passed)}명이 출근율 < 88%인데 조건 1 통과로 평가됨',
            'sample': low_attendance_passed[['Employee No', 'Full Name', '출근율_Attendance_Rate_Percent', 'cond_1_attendance_rate']].head(5)
        })

    # 문제점 출력
    if issues:
        for idx, issue in enumerate(issues, 1):
            severity_emoji = '🚨' if issue['severity'] == 'CRITICAL' else '⚠️' if issue['severity'] == 'WARNING' else '❌'
            print(f"{severity_emoji} 문제 {idx}: [{issue['severity']}] {issue['category']}")
            print(f"   설명: {issue['description']}")
            print(f"   영향 인원: {issue['count']}명")
            print()
            print("   샘플 데이터:")
            print(issue['sample'].to_string(index=False))
            print()
            print("-"*100)
            print()
    else:
        print("✅ 심각한 문제점이 발견되지 않았습니다.")
        print()

    # 데이터 품질 점수 계산
    print("="*100)
    print(" "*30 + "📈 데이터 품질 점수")
    print("="*100)
    print()

    total_issues = sum(1 for issue in issues if issue['severity'] in ['CRITICAL', 'ERROR'])
    affected_employees = sum(issue['count'] for issue in issues if issue['severity'] in ['CRITICAL', 'ERROR'])

    quality_score = max(0, 100 - (total_issues * 10) - (affected_employees / len(df) * 30))

    print(f"총 문제점: {total_issues}건")
    print(f"영향 받은 직원: {affected_employees}명 ({affected_employees/len(df)*100:.1f}%)")
    print(f"데이터 품질 점수: {quality_score:.1f}/100")
    print()

    if quality_score >= 90:
        print("✅ 우수 - 데이터 품질이 매우 양호합니다.")
    elif quality_score >= 70:
        print("⚠️  양호 - 일부 개선이 필요합니다.")
    elif quality_score >= 50:
        print("❌ 미흡 - 상당한 개선이 필요합니다.")
    else:
        print("🚨 불량 - 긴급한 조치가 필요합니다.")

    print()
    print("="*100)

    return issues

if __name__ == "__main__":
    analyze_output_data()
