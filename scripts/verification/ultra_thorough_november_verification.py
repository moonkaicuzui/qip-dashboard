#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
초철저 11월 2025 인센티브 검증 스크립트
목적: Excel 파일 기준으로 11월 인센티브 계산 결과를 4가지 관점에서 철저히 검증

검증 항목:
1. 과다 지급 (Overpayment): 받아야 할 금액보다 더 많이 받은 경우
2. 과소 지급 (Underpayment): 받아야 할 금액보다 적게 받은 경우
3. 연속월 계산 정확성: Continuous_Months 계산 로직 오류
4. 부적격자 수령: 조건 미충족인데 인센티브를 받은 경우
"""

import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime

def load_excel_data():
    """10월 Excel 파일 로드 (Single Source of Truth)"""
    excel_file = Path("2025 october completed final incentive amount data.xlsx")

    if not excel_file.exists():
        print(f"❌ Excel 파일 없음: {excel_file}")
        return None

    print(f"📂 Loading Excel: {excel_file.name}")
    df = pd.read_excel(excel_file)
    df['Employee No'] = df['Employee No'].astype(str).str.zfill(9)

    print(f"  ✅ {len(df)}명 직원 데이터 로드")
    print(f"  ✅ Source_Final_Incentive: {(df['Source_Final_Incentive'] > 0).sum()}명, {df['Source_Final_Incentive'].sum():,.0f} VND")

    return df

def load_november_csv():
    """11월 재계산 CSV 로드"""
    # Try V8.02 first (current version)
    csv_patterns = [
        Path("output_files/output_QIP_incentive_november_2025_Complete_V8.02_Complete.csv"),
        Path("output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv")
    ]

    for csv_file in csv_patterns:
        if csv_file.exists():
            print(f"📂 Loading November CSV: {csv_file.name}")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            df['Employee No'] = df['Employee No'].astype(str).str.zfill(9)

            print(f"  ✅ {len(df)}명 직원 데이터 로드")
            print(f"  ✅ Final Incentive amount: {(df['Final Incentive amount'] > 0).sum()}명, {df['Final Incentive amount'].sum():,.0f} VND")

            return df

    print(f"❌ 11월 CSV 파일 없음")
    return None

def load_position_matrix():
    """Position condition matrix 로드"""
    matrix_file = Path("config_files/position_condition_matrix.json")

    with open(matrix_file, 'r', encoding='utf-8') as f:
        matrix = json.load(f)

    # Extract progression table from the correct path
    progression_table = matrix['incentive_progression']['TYPE_1_PROGRESSIVE']['progression_table']

    print(f"📂 Position matrix loaded: {len(progression_table)} month entries")

    return matrix

def verification_1_overpayment(df_excel, df_nov):
    """
    검증 1: 과다 지급 케이스 분석
    Excel의 Next_Month_Expected를 기준으로 11월에 받아야 할 금액보다 더 많이 받은 경우
    """
    print("\n" + "="*100)
    print("검증 1: 과다 지급 케이스 분석 (Overpayment Detection)")
    print("="*100)

    # Load progression table
    matrix = load_position_matrix()
    progression_table = {int(k): v for k, v in matrix['incentive_progression']['TYPE_1_PROGRESSIVE']['progression_table'].items()}

    overpayment_cases = []

    # Merge Excel and November data
    df_merged = df_excel.merge(
        df_nov[['Employee No', 'Final Incentive amount', 'Continuous_Months', 'ROLE TYPE STD']],
        on='Employee No',
        how='inner',
        suffixes=('_Excel', '_Nov')
    )

    print(f"\n📊 매칭된 직원: {len(df_merged)}명")

    for idx, row in df_merged.iterrows():
        emp_id = row['Employee No']
        emp_name = row['Full Name']

        # Excel 기준 예상 금액 (Next_Month_Expected 기준)
        next_expected = row.get('Next_Month_Expected', 0)
        if pd.isna(next_expected) or next_expected == '':
            next_expected = 0
        else:
            next_expected = int(float(next_expected))

        # TYPE 확인
        role_type_nov = row.get('ROLE TYPE STD_Nov', '')

        # Excel 기준 Expected Amount
        if 'TYPE-1' in role_type_nov:
            expected_amount = progression_table.get(next_expected, 0)
        elif 'TYPE-2' in role_type_nov:
            # TYPE-2는 조건 충족 시 TYPE-1 평균 사용
            # 여기서는 단순화: Excel의 Source_Final_Incentive가 기준
            expected_amount = row['Source_Final_Incentive']
        elif 'TYPE-3' in role_type_nov:
            expected_amount = 0
        else:
            expected_amount = 0

        # 실제 11월 지급액
        actual_amount = row['Final Incentive amount_Nov']
        if pd.isna(actual_amount):
            actual_amount = 0

        # 과다 지급 검사 (tolerance: 1 VND)
        if actual_amount > expected_amount + 1:
            overpayment_cases.append({
                'Employee No': emp_id,
                'Full Name': emp_name,
                'ROLE TYPE': role_type_nov,
                'Next_Month_Expected': next_expected,
                'Expected_Amount': expected_amount,
                'Actual_Amount': actual_amount,
                'Overpayment': actual_amount - expected_amount,
                'Excel_Source_Final': row['Source_Final_Incentive'],
                'Excel_Continuous_Months': row.get('Continuous_Months_Excel', 0),
                'Nov_Continuous_Months': row.get('Continuous_Months_Nov', 0)
            })

    if overpayment_cases:
        print(f"\n🚨 과다 지급 케이스 발견: {len(overpayment_cases)}명")
        print(f"{'='*100}")

        df_over = pd.DataFrame(overpayment_cases)
        print(df_over.to_string(index=False))

        total_overpayment = df_over['Overpayment'].sum()
        print(f"\n💰 총 과다 지급액: {total_overpayment:,.0f} VND")
    else:
        print(f"\n✅ 과다 지급 케이스 없음 - 모든 직원이 정확한 금액 수령")

    return overpayment_cases

def verification_2_underpayment(df_excel, df_nov):
    """
    검증 2: 과소 지급 케이스 분석
    Excel의 Next_Month_Expected를 기준으로 11월에 받아야 할 금액보다 적게 받은 경우
    """
    print("\n" + "="*100)
    print("검증 2: 과소 지급 케이스 분석 (Underpayment Detection)")
    print("="*100)

    # Load progression table
    matrix = load_position_matrix()
    progression_table = {int(k): v for k, v in matrix['incentive_progression']['TYPE_1_PROGRESSIVE']['progression_table'].items()}

    underpayment_cases = []

    # Merge Excel and November data
    df_merged = df_excel.merge(
        df_nov[['Employee No', 'Final Incentive amount', 'Continuous_Months', 'ROLE TYPE STD',
                'cond_1_attendance_rate', 'cond_2_unapproved_absence', 'cond_3_actual_working_days',
                'cond_4_minimum_days', 'cond_5_aql_personal_failure', 'cond_6_aql_continuous',
                'cond_7_aql_team_area', 'cond_8_area_reject', 'cond_9_5prs_pass_rate',
                'cond_10_5prs_inspection_qty', 'conditions_pass_rate']],
        on='Employee No',
        how='inner',
        suffixes=('_Excel', '_Nov')
    )

    print(f"\n📊 매칭된 직원: {len(df_merged)}명")

    for idx, row in df_merged.iterrows():
        emp_id = row['Employee No']
        emp_name = row['Full Name']

        # 11월 조건 통과율 확인
        pass_rate = row.get('conditions_pass_rate', 0)
        if pd.isna(pass_rate):
            pass_rate = 0

        # 100% 조건 충족하지 못한 경우 Skip (정상적으로 0 VND)
        if pass_rate < 100:
            continue

        # Excel 기준 예상 금액 (Next_Month_Expected 기준)
        next_expected = row.get('Next_Month_Expected', 0)
        if pd.isna(next_expected) or next_expected == '':
            next_expected = 0
        else:
            next_expected = int(float(next_expected))

        # TYPE 확인
        role_type_nov = row.get('ROLE TYPE STD_Nov', '')

        # Excel 기준 Expected Amount (조건 100% 충족 시)
        if 'TYPE-1' in role_type_nov:
            expected_amount = progression_table.get(next_expected, 0)
        elif 'TYPE-2' in role_type_nov:
            # TYPE-2는 TYPE-1 평균 사용 - 여기서는 Excel Source_Final_Incentive 기준
            expected_amount = row['Source_Final_Incentive']
        elif 'TYPE-3' in role_type_nov:
            expected_amount = 0
        else:
            expected_amount = 0

        # 실제 11월 지급액
        actual_amount = row['Final Incentive amount_Nov']
        if pd.isna(actual_amount):
            actual_amount = 0

        # 과소 지급 검사 (tolerance: 1 VND, expected_amount > 0인 경우만)
        if expected_amount > 0 and actual_amount < expected_amount - 1:
            # Failed conditions 확인
            failed_conditions = []
            for cond_num in range(1, 11):
                cond_col = f'cond_{cond_num}_{"attendance_rate" if cond_num == 1 else "unapproved_absence" if cond_num == 2 else "actual_working_days" if cond_num == 3 else "minimum_days" if cond_num == 4 else "aql_personal_failure" if cond_num == 5 else "aql_continuous" if cond_num == 6 else "aql_team_area" if cond_num == 7 else "area_reject" if cond_num == 8 else "5prs_pass_rate" if cond_num == 9 else "5prs_inspection_qty"}'

                cond_result = row.get(cond_col, 'UNKNOWN')
                if cond_result == 'FAIL':
                    failed_conditions.append(f"Cond_{cond_num}")

            underpayment_cases.append({
                'Employee No': emp_id,
                'Full Name': emp_name,
                'ROLE TYPE': role_type_nov,
                'Next_Month_Expected': next_expected,
                'Expected_Amount': expected_amount,
                'Actual_Amount': actual_amount,
                'Underpayment': expected_amount - actual_amount,
                'Pass_Rate': pass_rate,
                'Failed_Conditions': ', '.join(failed_conditions) if failed_conditions else 'None',
                'Excel_Source_Final': row['Source_Final_Incentive'],
                'Excel_Continuous_Months': row.get('Continuous_Months_Excel', 0),
                'Nov_Continuous_Months': row.get('Continuous_Months_Nov', 0)
            })

    if underpayment_cases:
        print(f"\n🚨 과소 지급 케이스 발견: {len(underpayment_cases)}명")
        print(f"{'='*100}")

        df_under = pd.DataFrame(underpayment_cases)
        print(df_under.to_string(index=False))

        total_underpayment = df_under['Underpayment'].sum()
        print(f"\n💰 총 과소 지급액: {total_underpayment:,.0f} VND")
    else:
        print(f"\n✅ 과소 지급 케이스 없음 - 조건 충족 시 정확한 금액 수령")

    return underpayment_cases

def verification_3_continuous_months(df_excel, df_nov):
    """
    검증 3: 연속월 계산 정확성 검증
    Excel의 Next_Month_Expected와 11월 Continuous_Months 비교
    """
    print("\n" + "="*100)
    print("검증 3: 연속월 계산 정확성 검증 (Continuous_Months Validation)")
    print("="*100)

    calculation_errors = []

    # Merge Excel and November data
    df_merged = df_excel.merge(
        df_nov[['Employee No', 'Final Incentive amount', 'Continuous_Months', 'ROLE TYPE STD',
                'conditions_pass_rate', 'Previous_Incentive']],
        on='Employee No',
        how='inner',
        suffixes=('_Excel', '_Nov')
    )

    print(f"\n📊 매칭된 직원: {len(df_merged)}명")

    for idx, row in df_merged.iterrows():
        emp_id = row['Employee No']
        emp_name = row['Full Name']

        # Excel 기준 Next_Month_Expected
        next_expected = row.get('Next_Month_Expected', 0)
        if pd.isna(next_expected) or next_expected == '':
            next_expected = 0
        else:
            next_expected = int(float(next_expected))

        # 11월 실제 Continuous_Months
        actual_months = row.get('Continuous_Months_Nov', 0)
        if pd.isna(actual_months):
            actual_months = 0
        else:
            actual_months = int(actual_months)

        # 11월 조건 통과율
        pass_rate = row.get('conditions_pass_rate', 0)
        if pd.isna(pass_rate):
            pass_rate = 0

        # 로직 검증:
        # 1. 조건 100% 충족 시: Continuous_Months = Next_Month_Expected
        # 2. 조건 미충족 시: Continuous_Months = 0

        if pass_rate >= 100:
            # 조건 충족 시 Next_Month_Expected와 일치해야 함
            if actual_months != next_expected:
                calculation_errors.append({
                    'Employee No': emp_id,
                    'Full Name': emp_name,
                    'Issue': 'Continuous_Months Mismatch (조건 충족)',
                    'Excel_Next_Expected': next_expected,
                    'Nov_Continuous_Months': actual_months,
                    'Difference': actual_months - next_expected,
                    'Pass_Rate': pass_rate,
                    'Nov_Final_Amount': row['Final Incentive amount_Nov'],
                    'Previous_Incentive': row.get('Previous_Incentive', 0),
                    'Excel_Source_Final': row['Source_Final_Incentive']
                })
        else:
            # 조건 미충족 시 0이어야 함
            if actual_months != 0:
                calculation_errors.append({
                    'Employee No': emp_id,
                    'Full Name': emp_name,
                    'Issue': 'Continuous_Months Not Reset (조건 미충족)',
                    'Excel_Next_Expected': next_expected,
                    'Nov_Continuous_Months': actual_months,
                    'Difference': actual_months,
                    'Pass_Rate': pass_rate,
                    'Nov_Final_Amount': row['Final Incentive amount_Nov'],
                    'Previous_Incentive': row.get('Previous_Incentive', 0),
                    'Excel_Source_Final': row['Source_Final_Incentive']
                })

    if calculation_errors:
        print(f"\n🚨 연속월 계산 오류 발견: {len(calculation_errors)}건")
        print(f"{'='*100}")

        df_errors = pd.DataFrame(calculation_errors)
        print(df_errors.to_string(index=False))

        # 통계
        mismatch_count = len([e for e in calculation_errors if '조건 충족' in e['Issue']])
        not_reset_count = len([e for e in calculation_errors if '조건 미충족' in e['Issue']])

        print(f"\n📊 오류 유형 통계:")
        print(f"  - 조건 충족 시 불일치: {mismatch_count}건")
        print(f"  - 조건 미충족 시 미리셋: {not_reset_count}건")
    else:
        print(f"\n✅ 연속월 계산 정확 - 모든 직원의 Continuous_Months가 올바르게 계산됨")

    return calculation_errors

def verification_4_ineligible_recipients(df_excel, df_nov):
    """
    검증 4: 부적격자 수령 케이스 분석
    조건을 충족하지 못했는데 인센티브를 받은 경우
    """
    print("\n" + "="*100)
    print("검증 4: 부적격자 수령 케이스 분석 (Ineligible Recipients Detection)")
    print("="*100)

    ineligible_cases = []

    # 11월 데이터에서 조건 미충족인데 인센티브를 받은 경우
    df_ineligible = df_nov[
        (df_nov['conditions_pass_rate'] < 100) &
        (df_nov['Final Incentive amount'] > 0)
    ].copy()

    print(f"\n📊 조건 미충족 직원: {len(df_nov[df_nov['conditions_pass_rate'] < 100])}명")
    print(f"📊 인센티브 수령 직원: {len(df_nov[df_nov['Final Incentive amount'] > 0])}명")

    if len(df_ineligible) > 0:
        print(f"\n🚨 부적격자 수령 케이스 발견: {len(df_ineligible)}명")
        print(f"{'='*100}")

        for idx, row in df_ineligible.iterrows():
            emp_id = row['Employee No']
            emp_name = row['Full Name']

            # Failed conditions 확인
            failed_conditions = []
            condition_details = []

            for cond_num in range(1, 11):
                # 조건 컬럼명 매핑
                cond_mapping = {
                    1: 'cond_1_attendance_rate',
                    2: 'cond_2_unapproved_absence',
                    3: 'cond_3_actual_working_days',
                    4: 'cond_4_minimum_days',
                    5: 'cond_5_aql_personal_failure',
                    6: 'cond_6_aql_continuous',
                    7: 'cond_7_aql_team_area',
                    8: 'cond_8_area_reject',
                    9: 'cond_9_5prs_pass_rate',
                    10: 'cond_10_5prs_inspection_qty'
                }

                cond_col = cond_mapping.get(cond_num, '')
                cond_result = row.get(cond_col, 'UNKNOWN')

                if cond_result == 'FAIL':
                    # 조건명
                    cond_name_mapping = {
                        1: '출근율 >= 88%',
                        2: '무단결근 <= 2일',
                        3: '실제 출근일 > 0',
                        4: '최소 근무일 >= 12',
                        5: '개인 AQL 불량 = 0',
                        6: 'AQL 3개월 연속 불량 없음',
                        7: '팀/구역 AQL 3개월 연속 불량 없음',
                        8: '구역 리젝률 < 3%',
                        9: '5PRS 합격률 >= 95%',
                        10: '5PRS 검사량 >= 100'
                    }

                    failed_conditions.append(f"Cond_{cond_num}")
                    condition_details.append(f"조건{cond_num}: {cond_name_mapping.get(cond_num, 'Unknown')}")

            ineligible_cases.append({
                'Employee No': emp_id,
                'Full Name': emp_name,
                'ROLE TYPE': row.get('ROLE TYPE STD', ''),
                'Pass_Rate': row.get('conditions_pass_rate', 0),
                'Failed_Conditions': ', '.join(failed_conditions),
                'Condition_Details': ' | '.join(condition_details),
                'Final_Amount': row['Final Incentive amount'],
                'Continuous_Months': row.get('Continuous_Months', 0),
                'Previous_Incentive': row.get('Previous_Incentive', 0)
            })

        df_inelig = pd.DataFrame(ineligible_cases)
        print(df_inelig.to_string(index=False))

        total_ineligible_amount = df_inelig['Final_Amount'].sum()
        print(f"\n💰 총 부적격 지급액: {total_ineligible_amount:,.0f} VND")

        # 조건별 통계
        print(f"\n📊 실패 조건별 통계:")
        all_failed = []
        for case in ineligible_cases:
            all_failed.extend(case['Failed_Conditions'].split(', '))

        from collections import Counter
        cond_counts = Counter(all_failed)
        for cond, count in sorted(cond_counts.items()):
            print(f"  - {cond}: {count}명")
    else:
        print(f"\n✅ 부적격자 수령 케이스 없음 - 조건 미충족 시 정확히 0 VND")

    return ineligible_cases

def generate_summary_report(over_cases, under_cases, months_errors, ineligible_cases):
    """종합 검증 보고서 생성"""
    print("\n" + "="*100)
    print(" "*35 + "검증 종합 보고서")
    print("="*100)

    print(f"\n📋 검증 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 검증 대상: 2025년 11월 인센티브")
    print(f"📋 기준 파일: 2025 october completed final incentive amount data.xlsx")

    print(f"\n{'='*100}")
    print("검증 결과 요약")
    print(f"{'='*100}")

    # 검증 1: 과다 지급
    print(f"\n1️⃣  과다 지급 케이스:")
    if over_cases:
        total_over = sum([c['Overpayment'] for c in over_cases])
        print(f"   🚨 {len(over_cases)}명 발견 (총 과다 지급액: {total_over:,.0f} VND)")
    else:
        print(f"   ✅ 없음")

    # 검증 2: 과소 지급
    print(f"\n2️⃣  과소 지급 케이스:")
    if under_cases:
        total_under = sum([c['Underpayment'] for c in under_cases])
        print(f"   🚨 {len(under_cases)}명 발견 (총 과소 지급액: {total_under:,.0f} VND)")
    else:
        print(f"   ✅ 없음")

    # 검증 3: 연속월 계산
    print(f"\n3️⃣  연속월 계산 오류:")
    if months_errors:
        print(f"   🚨 {len(months_errors)}건 발견")
    else:
        print(f"   ✅ 없음")

    # 검증 4: 부적격자 수령
    print(f"\n4️⃣  부적격자 수령 케이스:")
    if ineligible_cases:
        total_inelig = sum([c['Final_Amount'] for c in ineligible_cases])
        print(f"   🚨 {len(ineligible_cases)}명 발견 (총 부적격 지급액: {total_inelig:,.0f} VND)")
    else:
        print(f"   ✅ 없음")

    # 최종 결론
    print(f"\n{'='*100}")
    print("최종 결론")
    print(f"{'='*100}")

    total_issues = len(over_cases) + len(under_cases) + len(months_errors) + len(ineligible_cases)

    if total_issues == 0:
        print(f"\n🎉 축하합니다! 모든 검증 통과 - 11월 인센티브 계산이 정확합니다.")
        print(f"\n✅ Excel 기준 데이터와 100% 일치")
        print(f"✅ 연속월 계산 로직 정확")
        print(f"✅ 조건 충족 여부 정확히 반영")
        print(f"✅ 인센티브 금액 정확히 계산")
    else:
        print(f"\n⚠️  총 {total_issues}건의 이슈가 발견되었습니다.")
        print(f"\n조치 필요:")

        if over_cases:
            print(f"  1. 과다 지급 {len(over_cases)}명 - 금액 조정 또는 로직 수정 필요")
        if under_cases:
            print(f"  2. 과소 지급 {len(under_cases)}명 - 금액 조정 또는 로직 수정 필요")
        if months_errors:
            print(f"  3. 연속월 계산 {len(months_errors)}건 - 로직 검토 및 수정 필요")
        if ineligible_cases:
            print(f"  4. 부적격자 수령 {len(ineligible_cases)}명 - 조건 평가 로직 검토 필요")

    print(f"\n{'='*100}\n")

def main():
    print("="*100)
    print(" "*30 + "초철저 11월 2025 인센티브 검증")
    print("="*100)
    print("\n검증 항목:")
    print("  1. 과다 지급 케이스 (Overpayment)")
    print("  2. 과소 지급 케이스 (Underpayment)")
    print("  3. 연속월 계산 정확성 (Continuous_Months)")
    print("  4. 부적격자 수령 케이스 (Ineligible Recipients)")
    print()

    # 데이터 로드
    df_excel = load_excel_data()
    if df_excel is None:
        return 1

    df_nov = load_november_csv()
    if df_nov is None:
        return 1

    print(f"\n{'='*100}\n")

    # 검증 실행
    over_cases = verification_1_overpayment(df_excel, df_nov)
    under_cases = verification_2_underpayment(df_excel, df_nov)
    months_errors = verification_3_continuous_months(df_excel, df_nov)
    ineligible_cases = verification_4_ineligible_recipients(df_excel, df_nov)

    # 종합 보고서
    generate_summary_report(over_cases, under_cases, months_errors, ineligible_cases)

    # 종료 코드
    if len(over_cases) + len(under_cases) + len(months_errors) + len(ineligible_cases) == 0:
        return 0  # 성공
    else:
        return 1  # 이슈 발견

if __name__ == "__main__":
    exit(main())
