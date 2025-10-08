#!/usr/bin/env python3
"""
AQL 파일 사전 검증 스크립트
11월, 12월 등 향후 월에도 October와 같은 문제 방지
"""

import pandas as pd
import sys
import os
import re
from datetime import datetime

def validate_aql_file(file_path, expected_month=None):
    """
    AQL 파일의 월 데이터 일관성 검증

    Args:
        file_path: AQL 파일 경로
        expected_month: 예상 월 (1-12), None이면 파일명에서 추출

    Returns:
        (is_valid, issues, stats)
    """
    issues = []
    stats = {
        'total_records': 0,
        'by_month': {},
        'expected_month': expected_month,
        'filename_month': None
    }

    # 파일 존재 확인
    if not os.path.exists(file_path):
        issues.append(f"❌ CRITICAL: 파일이 존재하지 않습니다: {file_path}")
        return False, issues, stats

    # 파일명에서 월 추출
    filename = os.path.basename(file_path)
    month_match = re.search(r'AQL REPORT-([A-Z]+)\.', filename)

    month_map = {
        'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
        'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
        'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
    }

    if month_match:
        month_name = month_match.group(1).upper()
        stats['filename_month'] = month_map.get(month_name)
        if expected_month is None:
            expected_month = stats['filename_month']
            stats['expected_month'] = expected_month

    if expected_month is None:
        issues.append(f"⚠️ WARNING: 예상 월을 파일명에서 추출할 수 없습니다")

    # 파일 읽기
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
    except Exception as e:
        issues.append(f"❌ CRITICAL: 파일 읽기 실패: {e}")
        return False, issues, stats

    # MONTH 컬럼 확인
    if 'MONTH' not in df.columns:
        issues.append(f"❌ CRITICAL: 'MONTH' 컬럼이 없습니다")
        return False, issues, stats

    # 통계 수집
    stats['total_records'] = len(df)
    month_counts = df['MONTH'].value_counts().to_dict()
    stats['by_month'] = {int(k): int(v) for k, v in month_counts.items()}

    # 검증 1: 첫 행 월 확인 (기존 로직 호환)
    first_month = int(df['MONTH'].iloc[0])
    if expected_month and first_month != expected_month:
        issues.append(
            f"❌ CRITICAL: 첫 행 월 불일치 - "
            f"예상={expected_month}, 실제={first_month} "
            f"(기존 validation 로직에서 파일 거부됨!)"
        )

    # 검증 2: 전체 행 월 확인 (NEW - October 문제 방지)
    unique_months = df['MONTH'].unique()
    if len(unique_months) > 1:
        issues.append(
            f"❌ CRITICAL: 여러 월 데이터 혼재 - {sorted(unique_months)} "
            f"(총 {len(df)}건 중 월별: {stats['by_month']})"
        )

        # 상세 정보
        for month_val in sorted(unique_months):
            if expected_month and month_val != expected_month:
                wrong_records = df[df['MONTH'] == month_val]
                sample_dates = wrong_records['DATE'].head(3).tolist() if 'DATE' in df.columns else []
                sample_emp = wrong_records['EMPLOYEE NO'].head(3).tolist() if 'EMPLOYEE NO' in df.columns else []

                issues.append(
                    f"   → 월 {month_val}: {len(wrong_records)}건 "
                    f"(날짜 예시: {sample_dates}, 직원 예시: {sample_emp})"
                )

    # 검증 3: 모든 행이 예상 월과 일치하는지
    if expected_month:
        wrong_month_rows = df[df['MONTH'] != expected_month]
        if len(wrong_month_rows) > 0:
            issues.append(
                f"⚠️ WARNING: {len(wrong_month_rows)}건의 레코드가 예상 월({expected_month})과 다릅니다"
            )

    # 검증 4: 날짜 일관성 (DATE 컬럼이 있는 경우)
    if 'DATE' in df.columns:
        try:
            df['DATE_parsed'] = pd.to_datetime(df['DATE'], errors='coerce')
            date_months = df['DATE_parsed'].dt.month.dropna()

            if expected_month:
                wrong_date_months = date_months[date_months != expected_month]
                if len(wrong_date_months) > 0:
                    issues.append(
                        f"⚠️ WARNING: {len(wrong_date_months)}건의 DATE가 예상 월과 다릅니다"
                    )
        except Exception as e:
            issues.append(f"⚠️ WARNING: DATE 컬럼 파싱 실패: {e}")

    # 최종 판정
    is_valid = len([i for i in issues if 'CRITICAL' in i]) == 0

    return is_valid, issues, stats


def print_validation_report(file_path, is_valid, issues, stats):
    """검증 결과 출력"""
    print("=" * 80)
    print(f"📋 AQL 파일 검증 리포트")
    print("=" * 80)
    print(f"파일: {file_path}")
    print(f"검증 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📊 통계:")
    print(f"   총 레코드: {stats['total_records']}건")
    print(f"   파일명 월: {stats['filename_month']}")
    print(f"   예상 월: {stats['expected_month']}")
    print(f"   월별 분포: {stats['by_month']}")

    print(f"\n🔍 검증 결과: {'✅ PASS' if is_valid else '❌ FAIL'}")

    if issues:
        print(f"\n📝 발견된 문제 ({len(issues)}건):")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\n✅ 문제 없음 - 모든 검증 통과!")

    print("=" * 80)


def auto_fix_month_data(file_path, expected_month):
    """
    잘못된 월 데이터 자동 수정

    Args:
        file_path: AQL 파일 경로
        expected_month: 올바른 월 (1-12)

    Returns:
        (fixed_count, backup_path)
    """
    # 백업 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.backup_{timestamp}"

    import shutil
    shutil.copy2(file_path, backup_path)

    # 파일 읽기
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()

    # 잘못된 월 필터링
    original_count = len(df)
    df_clean = df[df['MONTH'] == expected_month].copy()
    fixed_count = original_count - len(df_clean)

    # 저장
    df_clean.to_csv(file_path, index=False, encoding='utf-8-sig')

    return fixed_count, backup_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='AQL 파일 월 데이터 검증')
    parser.add_argument('file_path', help='AQL 파일 경로')
    parser.add_argument('--month', type=int, help='예상 월 (1-12)')
    parser.add_argument('--fix', action='store_true', help='자동 수정 (잘못된 월 제거)')

    args = parser.parse_args()

    # 검증 실행
    is_valid, issues, stats = validate_aql_file(args.file_path, args.month)

    # 결과 출력
    print_validation_report(args.file_path, is_valid, issues, stats)

    # 자동 수정
    if not is_valid and args.fix:
        if stats['expected_month']:
            print(f"\n🔧 자동 수정 시작...")
            fixed_count, backup_path = auto_fix_month_data(args.file_path, stats['expected_month'])
            print(f"   ✅ {fixed_count}건의 잘못된 월 데이터 제거")
            print(f"   ✅ 백업 생성: {backup_path}")

            # 재검증
            print(f"\n🔍 재검증 중...")
            is_valid2, issues2, stats2 = validate_aql_file(args.file_path, stats['expected_month'])
            print_validation_report(args.file_path, is_valid2, issues2, stats2)
        else:
            print(f"\n⚠️ 예상 월을 알 수 없어 자동 수정 불가")

    # Exit code
    sys.exit(0 if is_valid else 1)
