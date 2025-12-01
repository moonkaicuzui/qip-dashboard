#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
인센티브 자동 계산 스크립트
생성된 config 파일을 기반으로 모든 월의 인센티브를 계산합니다.
"""

import os
import sys
import glob
import subprocess
from pathlib import Path

# 상위 디렉토리를 경로에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def find_config_files():
    """config_files 디렉토리에서 config 파일 찾기"""
    config_pattern = "config_files/config_*_*.json"
    config_files = glob.glob(config_pattern)

    # 파일명에서 월과 연도 추출
    configs_info = []
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    for config_file in config_files:
        try:
            filename = os.path.basename(config_file)
            # config_november_2025.json → november, 2025 추출
            parts = filename.replace('config_', '').replace('.json', '').split('_')

            if len(parts) >= 2:
                month_str = parts[0].lower()
                year = int(parts[1])

                if month_str in month_names:
                    month_num = month_names[month_str]
                    configs_info.append({
                        'file': config_file,
                        'month': month_num,
                        'month_str': month_str,
                        'year': year,
                        'sort_key': year * 100 + month_num
                    })
                    print(f"  ✅ 발견: {month_str.capitalize()} {year} - {config_file}")

        except Exception as e:
            print(f"  ⚠️ Config 파싱 실패 {config_file}: {e}")
            continue

    # 정렬 (오래된 월 → 최신 월 순서로, 의존성 고려)
    configs_info.sort(key=lambda x: x['sort_key'])

    return configs_info

def calculate_incentive(month_str, year):
    """
    특정 월의 인센티브 계산

    Args:
        month_str: 월 이름 (예: 'november')
        year: 연도

    Returns:
        bool: 성공 여부
    """
    try:
        print(f"\n💰 인센티브 계산 중: {year}년 {month_str}")

        # Config 파일 경로
        config_file = f"config_files/config_{month_str}_{year}.json"

        # Config 파일 존재 확인
        if not os.path.exists(os.path.join(parent_dir, config_file)):
            print(f"  ⚠️ Config 파일이 없습니다: {config_file}")
            return False

        # step1_인센티브_계산_개선버전.py 실행 (--config 인자 사용)
        cmd = [
            sys.executable,
            "src/step1_인센티브_계산_개선버전.py",
            "--config", config_file
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=parent_dir,
            timeout=300  # 5분 타임아웃
        )

        if result.returncode == 0:
            print(f"  ✅ 인센티브 계산 성공")

            # Print stdout for debugging
            if result.stdout:
                print(f"  📝 계산 로그:")
                for line in result.stdout.split('\n')[-20:]:  # Print last 20 lines
                    if line.strip():
                        print(f"    {line}")

            # 생성된 파일 확인
            month_names = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            month_num = month_names[month_str.lower()]

            # V9.1 → V9.0 → V8.02 순서로 확인 - 통일된 fallback 패턴 (2025-12-01)
            csv_pattern_v91 = f"output_files/output_QIP_incentive_{month_str}_{year}_Complete_V9.1_Complete.csv"
            csv_pattern_v9 = f"output_files/output_QIP_incentive_{month_str}_{year}_Complete_V9.0_Complete.csv"
            csv_pattern_v8 = f"output_files/output_QIP_incentive_{month_str}_{year}_Complete_V8.02_Complete.csv"
            csv_files = glob.glob(csv_pattern_v91) or glob.glob(csv_pattern_v9) or glob.glob(csv_pattern_v8)

            if csv_files:
                print(f"  📄 생성된 CSV: {csv_files[0]}")
                return True
            else:
                print(f"  ⚠️ CSV 파일을 찾을 수 없습니다")
                return False
        else:
            print(f"  ❌ 인센티브 계산 실패")
            if result.stderr:
                print(f"  오류: {result.stderr[:500]}")  # 처음 500자만
            return False

    except subprocess.TimeoutExpired:
        print(f"  ❌ 타임아웃: 계산 시간 초과 (5분)")
        return False
    except Exception as e:
        print(f"  ❌ 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("💰 인센티브 자동 계산 시작")
    print("=" * 70)

    # Config 파일 찾기
    print("\n📂 Config 파일 검색 중...")
    configs = find_config_files()

    if not configs:
        print("⚠️ Config 파일을 찾을 수 없습니다")
        print("먼저 scripts/auto_generate_configs.py를 실행하세요")
        sys.exit(1)

    print(f"\n📊 {len(configs)}개월 Config 발견")

    # 각 월별로 인센티브 계산 (순서대로)
    successful_calculations = []
    failed_calculations = []

    for config_info in configs:
        result = calculate_incentive(config_info['month_str'], config_info['year'])

        if result:
            successful_calculations.append(config_info)
        else:
            failed_calculations.append(config_info)

    # 결과 출력
    print("\n" + "=" * 70)
    if successful_calculations:
        print(f"✅ 총 {len(successful_calculations)}개월 인센티브 계산 완료\n")
        print("계산 완료:")
        for info in successful_calculations:
            print(f"  - {info['year']}년 {info['month']}월 ({info['month_str']})")
    else:
        print("❌ 성공한 계산이 없습니다")

    if failed_calculations:
        print(f"\n⚠️ {len(failed_calculations)}개월 계산 실패:")
        for info in failed_calculations:
            print(f"  - {info['year']}년 {info['month']}월 ({info['month_str']})")

    print("=" * 70)

    # 모든 월이 실패한 경우에만 에러 코드 반환 (일부 실패는 허용)
    if not successful_calculations:
        print("\n❌ 모든 월의 계산이 실패했습니다. 워크플로우를 중단합니다.")
        sys.exit(1)
    elif failed_calculations:
        print(f"\n⚠️ 일부 월({len(failed_calculations)}개) 계산 실패했지만 워크플로우를 계속합니다.")
        # 일부 실패는 정상 종료 (exit code 0) - 후속 단계 진행 허용

if __name__ == "__main__":
    main()
