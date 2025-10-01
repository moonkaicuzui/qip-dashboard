#!/usr/bin/env python3
"""
Excel 파일에 3개월 연속 AQL 실패 정보 업데이트
Single Source of Truth 원칙 준수
자동 월 감지 및 동적 파일 로딩
"""

import pandas as pd
from pathlib import Path
import numpy as np
import argparse
import json
from datetime import datetime
import calendar

# 월 이름 매핑
MONTH_NAMES = {
    1: 'january', 2: 'february', 3: 'march', 4: 'april',
    5: 'may', 6: 'june', 7: 'july', 8: 'august',
    9: 'september', 10: 'october', 11: 'november', 12: 'december'
}

MONTH_NAMES_KR = {
    1: '1월', 2: '2월', 3: '3월', 4: '4월',
    5: '5월', 6: '6월', 7: '7월', 8: '8월',
    9: '9월', 10: '10월', 11: '11월', 12: '12월'
}

MONTH_NAMES_UPPER = {
    1: 'JANUARY', 2: 'FEBRUARY', 3: 'MARCH', 4: 'APRIL',
    5: 'MAY', 6: 'JUNE', 7: 'JULY', 8: 'AUGUST',
    9: 'SEPTEMBER', 10: 'OCTOBER', 11: 'NOVEMBER', 12: 'DECEMBER'
}

def get_previous_months(current_month, current_year, num_months=2):
    """현재 월로부터 이전 N개월 계산"""
    months = []
    month = current_month
    year = current_year

    for _ in range(num_months):
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        months.append((month, year))

    return list(reversed(months))  # 오래된 순서부터

def find_aql_file(month_num, year, aql_dir):
    """월에 해당하는 AQL 파일 찾기 (다양한 형식 지원)"""
    month_upper = MONTH_NAMES_UPPER[month_num]

    # 가능한 파일명 패턴들
    patterns = [
        f'1.HSRG AQL REPORT-{month_upper}.{year}.csv',
        f'HSRG AQL REPORT-{month_upper}.{year}.csv',
        f'AQL REPORT-{month_upper}.{year}.csv',
        f'aql_report_{MONTH_NAMES[month_num]}_{year}.csv',
    ]

    for pattern in patterns:
        file_path = aql_dir / pattern
        if file_path.exists():
            return file_path

    # 파일을 찾지 못한 경우
    return None

def analyze_consecutive_failures(current_month, current_year):
    """
    현재 월 기준으로 3개월 연속 AQL 실패 분석

    Args:
        current_month: 현재 월 (1-12)
        current_year: 현재 연도

    Returns:
        분석 결과 딕셔너리
    """

    print("=" * 80)
    print(f"📊 3개월 연속 AQL 실패 분석 - {current_year}년 {MONTH_NAMES_KR[current_month]}")
    print("=" * 80)

    # AQL history 디렉토리
    aql_dir = Path('input_files/AQL history')

    if not aql_dir.exists():
        raise FileNotFoundError(f"AQL history 디렉토리를 찾을 수 없습니다: {aql_dir}")

    # 이전 2개월 계산
    prev_months = get_previous_months(current_month, current_year, num_months=2)
    month_2_ago = prev_months[0]  # 2개월 전
    month_1_ago = prev_months[1]  # 1개월 전

    print(f"\n📅 분석 대상 월:")
    print(f"  2개월 전: {month_2_ago[1]}년 {MONTH_NAMES_KR[month_2_ago[0]]}")
    print(f"  1개월 전: {month_1_ago[1]}년 {MONTH_NAMES_KR[month_1_ago[0]]}")
    print(f"  현재 월:   {current_year}년 {MONTH_NAMES_KR[current_month]}")

    # AQL 파일 찾기
    file_month2 = find_aql_file(month_2_ago[0], month_2_ago[1], aql_dir)
    file_month1 = find_aql_file(month_1_ago[0], month_1_ago[1], aql_dir)
    file_current = find_aql_file(current_month, current_year, aql_dir)

    # 파일 존재 확인
    files_info = {
        'month_2_ago': (month_2_ago, file_month2),
        'month_1_ago': (month_1_ago, file_month1),
        'current_month': ((current_month, current_year), file_current)
    }

    print(f"\n📁 AQL 파일 확인:")
    for key, (month_info, file_path) in files_info.items():
        month_num, year = month_info
        status = "✅" if file_path else "❌"
        file_name = file_path.name if file_path else "파일 없음"
        print(f"  {status} {year}년 {MONTH_NAMES_KR[month_num]}: {file_name}")

    # FAIL 레코드 추출 함수
    def get_fail_employees(df):
        if df is None or df.empty:
            return set()
        fail_df = df[df['RESULT'].str.upper() == 'FAIL']
        emp_ids = fail_df['EMPLOYEE NO'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
        return set(emp_ids.unique())

    # 각 월별 데이터 로드
    df_month2 = pd.read_csv(file_month2, encoding='utf-8-sig') if file_month2 else pd.DataFrame()
    df_month1 = pd.read_csv(file_month1, encoding='utf-8-sig') if file_month1 else pd.DataFrame()
    df_current = pd.read_csv(file_current, encoding='utf-8-sig') if file_current else pd.DataFrame()

    # 실패자 추출
    fails_month2 = get_fail_employees(df_month2)
    fails_month1 = get_fail_employees(df_month1)
    fails_current = get_fail_employees(df_current)

    print(f"\n📈 월별 실패자:")
    print(f"  {MONTH_NAMES_KR[month_2_ago[0]]}: {len(fails_month2)}명")
    print(f"  {MONTH_NAMES_KR[month_1_ago[0]]}: {len(fails_month1)}명")
    print(f"  {MONTH_NAMES_KR[current_month]}: {len(fails_current)}명")

    # 연속 실패 분석
    consecutive_2month_old = fails_month2 & fails_month1  # 2개월 전 + 1개월 전
    consecutive_2month_recent = fails_month1 & fails_current  # 1개월 전 + 현재 월
    consecutive_3month = fails_month2 & fails_month1 & fails_current  # 3개월 모두

    # 월 이름 태그 생성
    month2_name = MONTH_NAMES_UPPER[month_2_ago[0]][:3]  # JUL, AUG 등
    month1_name = MONTH_NAMES_UPPER[month_1_ago[0]][:3]
    current_name = MONTH_NAMES_UPPER[current_month][:3]

    print(f"\n🔗 연속 실패 분석:")
    print(f"  {MONTH_NAMES_KR[month_2_ago[0]]}-{MONTH_NAMES_KR[month_1_ago[0]]} 연속: {len(consecutive_2month_old)}명")
    print(f"  {MONTH_NAMES_KR[month_1_ago[0]]}-{MONTH_NAMES_KR[current_month]} 연속: {len(consecutive_2month_recent)}명")
    print(f"  {MONTH_NAMES_KR[month_2_ago[0]]}-{MONTH_NAMES_KR[month_1_ago[0]]}-{MONTH_NAMES_KR[current_month]} 3개월 연속: {len(consecutive_3month)}명")

    # 결과 딕셔너리 생성
    result = {
        'month_2_ago': month_2_ago,
        'month_1_ago': month_1_ago,
        'current_month': (current_month, current_year),
        'fails_month2': fails_month2,
        'fails_month1': fails_month1,
        'fails_current': fails_current,
        'consecutive_2month_old': consecutive_2month_old,
        'consecutive_2month_recent': consecutive_2month_recent,
        'consecutive_3month': consecutive_3month,
        'tag_2month_old': f'YES_2MONTHS_{month2_name}_{month1_name}',
        'tag_2month_recent': f'YES_2MONTHS_{month1_name}_{current_name}',
        'tag_3month': 'YES_3MONTHS'
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
            df.loc[mask, 'Continuous_FAIL'] = analysis_result['tag_3month']
            consecutive_3month_count += 1

    # 2개월 연속 실패자 표시
    consecutive_2month_count = 0

    # 최신 2개월 연속 (1개월 전 + 현재 월)
    for emp_id in analysis_result['consecutive_2month_recent']:
        if emp_id not in analysis_result['consecutive_3month']:  # 3개월 연속이 아닌 경우만
            mask = df['emp_no_str'] == emp_id
            if mask.any():
                df.loc[mask, 'Continuous_FAIL'] = analysis_result['tag_2month_recent']
                consecutive_2month_count += 1

    # 이전 2개월 연속 (2개월 전 + 1개월 전)
    for emp_id in analysis_result['consecutive_2month_old']:
        if emp_id not in analysis_result['consecutive_3month'] and emp_id not in analysis_result['consecutive_2month_recent']:
            mask = df['emp_no_str'] == emp_id
            if mask.any():
                df.loc[mask, 'Continuous_FAIL'] = analysis_result['tag_2month_old']
                consecutive_2month_count += 1

    # 연속 실패 월 수 컬럼 추가
    df['Consecutive_Fail_Months'] = 0

    # 3개월 연속
    df.loc[df['Continuous_FAIL'] == 'YES_3MONTHS', 'Consecutive_Fail_Months'] = 3

    # 2개월 연속
    df.loc[df['Continuous_FAIL'].str.contains('2MONTHS', na=False), 'Consecutive_Fail_Months'] = 2

    # 당월만 실패 (1개월)
    current_only_fails = analysis_result['fails_current'] - analysis_result['consecutive_2month_recent']
    for emp_id in current_only_fails:
        mask = df['emp_no_str'] == emp_id
        if mask.any():
            df.loc[mask, 'Consecutive_Fail_Months'] = 1

    month_2_ago = analysis_result['month_2_ago']
    month_1_ago = analysis_result['month_1_ago']
    current_month = analysis_result['current_month']

    print(f"\n✅ 업데이트 결과:")
    print(f"  3개월 연속 실패 ({MONTH_NAMES_KR[month_2_ago[0]]}-{MONTH_NAMES_KR[month_1_ago[0]]}-{MONTH_NAMES_KR[current_month[0]]}): {consecutive_3month_count}명")
    print(f"  2개월 연속 실패 (총): {consecutive_2month_count}명")
    print(f"    - {MONTH_NAMES_KR[month_1_ago[0]]}-{MONTH_NAMES_KR[current_month[0]]} 연속: {len(analysis_result['consecutive_2month_recent'])}명")
    print(f"    - {MONTH_NAMES_KR[month_2_ago[0]]}-{MONTH_NAMES_KR[month_1_ago[0]]} 연속: {len(analysis_result['consecutive_2month_old'])}명")
    print(f"  Continuous_FAIL 컬럼 업데이트 완료")

    # emp_no_str 임시 컬럼 제거
    df = df.drop(columns=['emp_no_str'])

    return df

def find_excel_file(month, year):
    """월/연도에 해당하는 Excel 파일 자동 찾기"""
    output_dir = Path('output_files')
    month_name = MONTH_NAMES[month]

    # 가능한 파일명 패턴들
    patterns = [
        f'output_QIP_incentive_{month_name}_{year}_최종완성버전_v6.0_Complete.csv',
        f'output_QIP_incentive_{month_name}_{year}_Complete.csv',
        f'output_QIP_incentive_{month}_{year}_최종완성버전_v6.0_Complete.csv',
        f'output_QIP_incentive_{month:02d}_{year}_Complete.csv',
    ]

    for pattern in patterns:
        file_path = output_dir / pattern
        if file_path.exists():
            return file_path

    # 와일드카드 검색
    possible_files = list(output_dir.glob(f'*{month_name}*{year}*.csv'))
    if possible_files:
        return possible_files[0]

    return None

def load_config(month, year):
    """config 파일에서 월 정보 로드"""
    month_name = MONTH_NAMES[month]
    config_path = Path(f'config_files/config_{month_name}_{year}.json')

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def main():
    """메인 실행 함수"""

    parser = argparse.ArgumentParser(description='3개월 연속 AQL 실패 분석 및 Excel 업데이트')
    parser.add_argument('--month', type=str, help='월 (예: september 또는 9)')
    parser.add_argument('--year', type=int, help='연도 (예: 2025)')

    args = parser.parse_args()

    # 월/연도 결정
    if args.month and args.year:
        # 월 이름을 숫자로 변환
        if args.month.isdigit():
            month_num = int(args.month)
        else:
            month_lower = args.month.lower()
            month_num = next((k for k, v in MONTH_NAMES.items() if v == month_lower), None)
            if month_num is None:
                print(f"❌ 올바르지 않은 월 이름: {args.month}")
                return

        year = args.year
    else:
        # config 파일에서 가장 최근 파일 찾기
        config_dir = Path('config_files')
        config_files = list(config_dir.glob('config_*.json'))

        if not config_files:
            print("❌ config 파일을 찾을 수 없습니다.")
            print("사용법: python update_continuous_fail_column.py --month september --year 2025")
            return

        # 가장 최근 config 파일
        latest_config = max(config_files, key=lambda p: p.stat().st_mtime)

        with open(latest_config, 'r', encoding='utf-8') as f:
            config = json.load(f)

        year = config['year']
        month_name = config['month'].lower()
        month_num = next((k for k, v in MONTH_NAMES.items() if v == month_name), None)

        print(f"ℹ️  Config 파일에서 자동 감지: {year}년 {MONTH_NAMES_KR[month_num]}")

    # 3개월 연속 실패 분석
    analysis_result = analyze_consecutive_failures(month_num, year)

    # Excel 파일 경로 찾기
    excel_path = find_excel_file(month_num, year)

    if not excel_path:
        print(f"\n❌ Excel 파일을 찾을 수 없습니다.")
        print(f"예상 경로: output_files/output_QIP_incentive_{MONTH_NAMES[month_num]}_{year}_*.csv")
        return

    print(f"\n✅ Excel 파일 찾음: {excel_path.name}")

    # Excel 업데이트
    updated_df = update_excel_with_continuous_fail(excel_path, analysis_result)

    # 백업 생성
    backup_path = excel_path.with_suffix('.backup.csv')
    pd.read_csv(excel_path, encoding='utf-8-sig').to_csv(backup_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 백업 생성: {backup_path.name}")

    # 업데이트된 파일 저장
    updated_df.to_csv(excel_path, index=False, encoding='utf-8-sig')
    print(f"💾 Excel 파일 업데이트 완료: {excel_path.name}")

    # Excel XLSX 파일도 생성
    excel_xlsx_path = excel_path.with_suffix('.xlsx')
    updated_df.to_excel(excel_xlsx_path, index=False, engine='openpyxl')
    print(f"💾 Excel XLSX 파일도 업데이트: {excel_xlsx_path.name}")

    # 검증
    print("\n🔍 검증:")
    print(f"  Continuous_FAIL = 'YES_3MONTHS': {(updated_df['Continuous_FAIL'] == 'YES_3MONTHS').sum()}명")
    print(f"  Consecutive_Fail_Months = 3: {(updated_df['Consecutive_Fail_Months'] == 3).sum()}명")
    print(f"  Consecutive_Fail_Months = 2: {(updated_df['Consecutive_Fail_Months'] == 2).sum()}명")

    # 샘플 출력
    sample = updated_df[updated_df['Consecutive_Fail_Months'] > 0][['Employee No', 'Full Name', 'Continuous_FAIL', 'Consecutive_Fail_Months']].head(10)
    if not sample.empty:
        print(f"\n📋 샘플 데이터 (연속 실패자):")
        print(sample.to_string(index=False))

    print("\n" + "=" * 80)
    print("✅ Single Source of Truth 원칙 준수:")
    print("  - AQL history 파일에서 실제 데이터 분석")
    print("  - 자동으로 이전 2개월 계산 및 파일 로드")
    print("  - Excel 파일에 결과 저장")
    print("  - 대시보드는 Excel 파일 참조")
    print("=" * 80)

if __name__ == "__main__":
    main()
