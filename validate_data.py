#!/usr/bin/env python3
"""
데이터 검증 스크립트
AQL 데이터의 reject rate를 사전 검증하여 문제를 미리 확인
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.step1_인센티브_계산_개선버전 import IncentiveProcessor
from src.config import Config, Month

def main():
    print("=" * 60)
    print("QIP 인센티브 데이터 검증")
    print("=" * 60)
    
    # 8월 데이터 검증
    config = Config(month=Month.august, year=2025)
    processor = IncentiveProcessor(
        month=config.month,
        year=config.year,
        base_path=Path.cwd()
    )
    
    # 검증 실행
    processor.validate_and_report_issues()
    
    print("\n✅ 검증 완료")
    return 0

if __name__ == "__main__":
    sys.exit(main())