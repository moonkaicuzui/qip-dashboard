#!/usr/bin/env python3
"""
5PRS 파일 월별 데이터 검증 스크립트
다른 달 데이터가 혼재되어 있는지 확인하고 자동 수정 가능

Usage:
    python scripts/validation/validate_5prs_file.py "input_files/5prs data october.csv" --month 10 --year 2025
    python scripts/validation/validate_5prs_file.py "input_files/5prs data october.csv" --month 10 --year 2025 --fix
"""

import pandas as pd
import sys
from datetime import datetime
from pathlib import Path


def validate_5prs_file(file_path: str, target_month: int, target_year: int, fix: bool = False):
    """
    5PRS 파일에서 해당 월 데이터만 있는지 검증

    Args:
        file_path: 5PRS CSV 파일 경로
        target_month: 대상 월 (1-12)
        target_year: 대상 년도
        fix: True면 다른 달 데이터 자동 제거

    Returns:
        0: 검증 통과
        1: 다른 달 데이터 발견
    """
    print(f"\n{'='*70}")
    print(f"5PRS 파일 월별 데이터 검증")
    print(f"{'='*70}")
    print(f"파일: {file_path}")
    print(f"대상: {target_year}년 {target_month}월")
    print()

    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return 1

    # Load file
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        return 1

    if 'Inspection Date' not in df.columns:
        print("❌ 'Inspection Date' 컬럼이 없습니다!")
        print("   5PRS 파일에는 Inspection Date 컬럼이 필수입니다.")
        return 1

    # Parse dates - support multiple formats
    # Try ISO format (YYYY-MM-DD) first, then US format (MM/DD/YYYY)
    df['Inspection Date'] = pd.to_datetime(
        df['Inspection Date'],
        format='mixed',  # Auto-detect format
        errors='coerce'
    )

    # Remove invalid dates
    invalid_dates = df['Inspection Date'].isna().sum()
    if invalid_dates > 0:
        print(f"⚠️ 날짜 형식 오류: {invalid_dates}개 레코드 (무시됨)")

    df_valid = df[df['Inspection Date'].notna()].copy()

    if len(df_valid) == 0:
        print("❌ 유효한 날짜 데이터가 없습니다!")
        return 1

    # Extract year/month
    df_valid['Year'] = df_valid['Inspection Date'].dt.year
    df_valid['Month'] = df_valid['Inspection Date'].dt.month

    # Group by year/month
    month_summary = df_valid.groupby(['Year', 'Month']).size().reset_index(name='Count')
    month_summary = month_summary.sort_values(['Year', 'Month'])

    print("📊 파일 내 월별 레코드 분포:")
    print("-" * 50)
    for _, row in month_summary.iterrows():
        year = int(row['Year'])
        month = int(row['Month'])
        count = int(row['Count'])

        if year == target_year and month == target_month:
            print(f"✅ {year}년 {month:02d}월: {count:,}개 (대상 월)")
        else:
            print(f"❌ {year}년 {month:02d}월: {count:,}개 ⚠️ 다른 달 데이터!")

    # Check if other months exist
    target_data = df_valid[
        (df_valid['Year'] == target_year) &
        (df_valid['Month'] == target_month)
    ]

    other_month_data = df_valid[
        ~((df_valid['Year'] == target_year) &
          (df_valid['Month'] == target_month))
    ]

    print()
    print("=" * 50)
    print(f"대상 월 데이터: {len(target_data):,}개")
    print(f"다른 달 데이터: {len(other_month_data):,}개")
    print("=" * 50)

    if len(other_month_data) == 0:
        print()
        print("✅ 검증 통과: 해당 월 데이터만 존재합니다!")
        return 0

    print()
    print(f"⚠️ 검증 실패: 다른 달 데이터 {len(other_month_data):,}개 발견!")
    print()
    print("영향:")
    print(f"  • 5PRS 통과율이 부정확하게 계산될 수 있습니다")
    print(f"  • 인센티브 지급 오류가 발생할 수 있습니다")

    if fix:
        print()
        print("🔧 자동 수정 모드: 다른 달 데이터 제거 중...")

        # Backup original file
        backup_path = file_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        df.to_csv(backup_path, index=False, encoding='utf-8-sig')
        print(f"  • 백업 파일 생성: {backup_path}")

        # Save only target month data
        target_data_full = df[df.index.isin(target_data.index)]
        target_data_full.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"  • 수정된 파일 저장: {file_path}")
        print(f"  • 레코드 수: {len(df):,} → {len(target_data_full):,}")
        print()
        print("✅ 파일 수정 완료!")
        print(f"   • 제거된 레코드: {len(other_month_data):,}개")
        print(f"   • 남은 레코드: {len(target_data_full):,}개")
        return 0

    return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='5PRS 파일 월별 데이터 검증',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 검증만 수행
  python scripts/validation/validate_5prs_file.py "input_files/5prs data october.csv" --month 10 --year 2025

  # 검증 + 자동 수정
  python scripts/validation/validate_5prs_file.py "input_files/5prs data october.csv" --month 10 --year 2025 --fix
        """
    )
    parser.add_argument('file_path', help='5PRS CSV 파일 경로')
    parser.add_argument('--month', type=int, required=True, help='대상 월 (1-12)')
    parser.add_argument('--year', type=int, default=2025, help='대상 년도 (default: 2025)')
    parser.add_argument('--fix', action='store_true', help='자동 수정 모드 활성화')

    args = parser.parse_args()

    # Validate month
    if args.month < 1 or args.month > 12:
        print(f"❌ 잘못된 월: {args.month} (1-12 사이여야 합니다)")
        sys.exit(1)

    result = validate_5prs_file(args.file_path, args.month, args.year, args.fix)
    sys.exit(result)
