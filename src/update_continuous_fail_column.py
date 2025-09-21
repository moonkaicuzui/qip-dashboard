#!/usr/bin/env python3
"""
Excel 파일에 3개월 연속 AQL 실패 정보 업데이트
Single Source of Truth 원칙 준수
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_3month_consecutive_failures():
    """AQL history 파일에서 3개월 연속 실패 분석"""

    print("=" * 80)
    print("📊 3개월 연속 AQL 실패 분석 및 Excel 업데이트")
    print("=" * 80)

    # AQL history 파일 로드
    aql_dir = Path('input_files/AQL history')

    # 각 월별 실패 데이터 수집
    july_df = pd.read_csv(aql_dir / '1.HSRG AQL REPORT-JULY.2025.csv', encoding='utf-8-sig')
    aug_df = pd.read_csv(aql_dir / '1.HSRG AQL REPORT-AUGUST.2025.csv', encoding='utf-8-sig')
    sep_df = pd.read_csv(aql_dir / '1.HSRG AQL REPORT-SEPTEMBER.2025.csv', encoding='utf-8-sig')

    # FAIL 레코드만 추출하고 직원 ID 표준화
    def get_fail_employees(df):
        fail_df = df[df['RESULT'].str.upper() == 'FAIL']
        emp_ids = fail_df['EMPLOYEE NO'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
        return set(emp_ids.unique())

    july_fails = get_fail_employees(july_df)
    aug_fails = get_fail_employees(aug_df)
    sep_fails = get_fail_employees(sep_df)

    print(f"\n📈 월별 실패자:")
    print(f"  7월: {len(july_fails)}명")
    print(f"  8월: {len(aug_fails)}명")
    print(f"  9월: {len(sep_fails)}명")

    # 연속 실패 분석
    consecutive_2month_jul_aug = july_fails & aug_fails
    consecutive_2month_aug_sep = aug_fails & sep_fails
    consecutive_3month = july_fails & aug_fails & sep_fails

    print(f"\n🔗 연속 실패 분석:")
    print(f"  7-8월 연속: {len(consecutive_2month_jul_aug)}명")
    print(f"  8-9월 연속: {len(consecutive_2month_aug_sep)}명")
    print(f"  7-8-9월 3개월 연속: {len(consecutive_3month)}명")

    # 결과 딕셔너리 생성
    result = {
        'july_fails': july_fails,
        'aug_fails': aug_fails,
        'sep_fails': sep_fails,
        'consecutive_2month_jul_aug': consecutive_2month_jul_aug,
        'consecutive_2month_aug_sep': consecutive_2month_aug_sep,
        'consecutive_3month': consecutive_3month
    }

    return result

def update_excel_with_continuous_fail(excel_path, analysis_result):
    """Excel 파일의 Continuous_FAIL 컬럼 업데이트"""

    print(f"\n📝 Excel 파일 업데이트 중: {excel_path}")

    # Excel 파일 로드
    df = pd.read_csv(excel_path, encoding='utf-8-sig')

    # Employee No 표준화
    df['emp_no_str'] = df['Employee No'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

    # Continuous_FAIL 컬럼 초기화
    df['Continuous_FAIL'] = 'NO'

    # 3개월 연속 실패자 표시
    consecutive_3month_count = 0
    for emp_id in analysis_result['consecutive_3month']:
        mask = df['emp_no_str'] == emp_id
        if mask.any():
            df.loc[mask, 'Continuous_FAIL'] = 'YES_3MONTHS'
            consecutive_3month_count += 1

    # 2개월 연속 실패자 표시 (참고용)
    consecutive_2month_count = 0

    # 8-9월 연속 실패자 (최신)
    for emp_id in analysis_result['consecutive_2month_aug_sep']:
        if emp_id not in analysis_result['consecutive_3month']:  # 3개월 연속이 아닌 경우만
            mask = df['emp_no_str'] == emp_id
            if mask.any():
                df.loc[mask, 'Continuous_FAIL'] = 'YES_2MONTHS_AUG_SEP'
                consecutive_2month_count += 1

    # 7-8월 연속 실패자
    for emp_id in analysis_result['consecutive_2month_jul_aug']:
        if emp_id not in analysis_result['consecutive_3month'] and emp_id not in analysis_result['consecutive_2month_aug_sep']:
            mask = df['emp_no_str'] == emp_id
            if mask.any():
                df.loc[mask, 'Continuous_FAIL'] = 'YES_2MONTHS_JUL_AUG'
                consecutive_2month_count += 1

    # 연속 실패 월 수 컬럼 추가
    df['Consecutive_Fail_Months'] = 0

    # 3개월 연속
    df.loc[df['Continuous_FAIL'] == 'YES_3MONTHS', 'Consecutive_Fail_Months'] = 3

    # 2개월 연속
    df.loc[df['Continuous_FAIL'].str.contains('2MONTHS'), 'Consecutive_Fail_Months'] = 2

    # 당월만 실패 (1개월)
    sep_only_fails = analysis_result['sep_fails'] - analysis_result['consecutive_2month_aug_sep']
    for emp_id in sep_only_fails:
        mask = df['emp_no_str'] == emp_id
        if mask.any():
            df.loc[mask, 'Consecutive_Fail_Months'] = 1

    print(f"\n✅ 업데이트 결과:")
    print(f"  3개월 연속 실패: {consecutive_3month_count}명")
    print(f"  2개월 연속 실패: {consecutive_2month_count}명")
    print(f"  Continuous_FAIL 컬럼 업데이트 완료")

    # emp_no_str 임시 컬럼 제거
    df = df.drop(columns=['emp_no_str'])

    return df

def main():
    """메인 실행 함수"""

    # 3개월 연속 실패 분석
    analysis_result = analyze_3month_consecutive_failures()

    # Excel 파일 경로
    excel_path = Path('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv')

    if not excel_path.exists():
        print(f"❌ Excel 파일을 찾을 수 없습니다: {excel_path}")
        return

    # Excel 업데이트
    updated_df = update_excel_with_continuous_fail(excel_path, analysis_result)

    # 백업 생성
    backup_path = excel_path.with_suffix('.backup.csv')
    pd.read_csv(excel_path, encoding='utf-8-sig').to_csv(backup_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 백업 생성: {backup_path}")

    # 업데이트된 파일 저장
    updated_df.to_csv(excel_path, index=False, encoding='utf-8-sig')
    print(f"💾 Excel 파일 업데이트 완료: {excel_path}")

    # Excel 파일도 생성
    excel_xlsx_path = excel_path.with_suffix('.xlsx')
    updated_df.to_excel(excel_xlsx_path, index=False, engine='openpyxl')
    print(f"💾 Excel XLSX 파일도 업데이트: {excel_xlsx_path}")

    # 검증
    print("\n🔍 검증:")
    print(f"  Continuous_FAIL = 'YES_3MONTHS': {(updated_df['Continuous_FAIL'] == 'YES_3MONTHS').sum()}명")
    print(f"  Consecutive_Fail_Months = 3: {(updated_df['Consecutive_Fail_Months'] == 3).sum()}명")

    # 샘플 출력
    sample = updated_df[updated_df['Consecutive_Fail_Months'] > 0][['Employee No', 'Full Name', 'Continuous_FAIL', 'Consecutive_Fail_Months']].head(5)
    if not sample.empty:
        print(f"\n📋 샘플 데이터:")
        print(sample.to_string(index=False))

    print("\n" + "=" * 80)
    print("✅ Single Source of Truth 원칙 준수:")
    print("  - AQL history 파일에서 실제 데이터 분석")
    print("  - Excel 파일에 결과 저장")
    print("  - 대시보드는 Excel 파일 참조")
    print("=" * 80)

if __name__ == "__main__":
    main()