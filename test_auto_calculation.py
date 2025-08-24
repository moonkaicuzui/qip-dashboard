#!/usr/bin/env python3
"""
7월 자동 계산 테스트 스크립트
8월 보고서 생성 시 7월이 자동으로 계산되는지 확인
"""

import sys
from pathlib import Path

# src 디렉토리를 경로에 추가
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

from step1_인센티브_계산_개선버전 import IncentiveProcessor
from config import Config, Month

def test_auto_calculation():
    """자동 계산 테스트"""
    print("=" * 60)
    print("7월 자동 계산 테스트")
    print("=" * 60)
    
    # 현재 경로
    base_path = Path.cwd()
    
    # 7월 결과 파일 삭제 (테스트를 위해)
    july_output = base_path / 'output_files' / 'output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv'
    if july_output.exists():
        print(f"\n기존 7월 파일 삭제: {july_output.name}")
        july_output.unlink()
    
    # 8월 계산 시작
    print("\n8월 인센티브 계산 시작...")
    print("-" * 40)
    
    # 8월 프로세서 생성
    august_processor = IncentiveProcessor(
        month=Month.august,
        year=2025,
        base_path=base_path
    )
    
    # ensure_previous_month_exists 실행
    print("\n이전 월 체크 시작...")
    august_processor.ensure_previous_month_exists()
    
    # 결과 확인
    print("\n" + "=" * 60)
    print("테스트 결과:")
    print("-" * 40)
    
    if july_output.exists():
        print("✅ 7월 파일이 자동으로 생성되었습니다!")
        print(f"   파일: {july_output.name}")
    else:
        print("❌ 7월 파일이 생성되지 않았습니다.")
        print("   필요한 파일이 없어서 중단되었을 수 있습니다.")
    
    print("\n필요한 파일 체크:")
    july_month = Month.july
    required_files = {
        'basic': base_path / 'input_files' / f'basic manpower data july.csv',
        'aql': base_path / 'input_files' / 'AQL history' / f'1.HSRG AQL REPORT-JULY.2025.csv',
        '5prs': base_path / 'input_files' / f'5prs data july.csv',
        'attendance': base_path / 'input_files' / 'attendance' / 'converted' / f'attendance data july_converted.csv'
    }
    
    for file_type, file_path in required_files.items():
        if file_path.exists():
            print(f"  ✅ {file_type}: {file_path.name}")
        else:
            print(f"  ❌ {file_type}: {file_path.name} (없음)")
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_auto_calculation())