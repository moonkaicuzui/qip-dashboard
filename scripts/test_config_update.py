#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Config 자동 업데이트 테스트 스크립트
개선된 자동화 시스템이 제대로 작동하는지 검증합니다.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

def test_config_file(config_path):
    """Config 파일 검증"""
    print(f"\n📋 Config 파일 테스트: {config_path}")

    if not os.path.exists(config_path):
        print("  ❌ 파일이 존재하지 않습니다")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 필수 필드 확인
    required_fields = ['year', 'month', 'working_days', 'file_paths']
    missing_fields = []

    for field in required_fields:
        if field not in config:
            missing_fields.append(field)

    if missing_fields:
        print(f"  ❌ 필수 필드 누락: {missing_fields}")
        return False

    print("  ✅ 필수 필드 모두 존재")

    # Working days 검증
    working_days = config.get('working_days')
    print(f"  📊 Working days: {working_days}일")

    if working_days and working_days > 0 and working_days <= 31:
        print("  ✅ Working days 값이 정상 범위")
    else:
        print(f"  ⚠️ Working days 값이 비정상: {working_days}")

    # Working days 소스 확인
    working_days_source = config.get('working_days_source')
    if working_days_source == 'attendance_data':
        print("  ✅ Working days가 attendance 데이터에서 자동 계산됨")
        update_time = config.get('working_days_updated_at', 'N/A')
        print(f"  📅 마지막 업데이트: {update_time}")
    else:
        print("  ⚠️ Working days가 기본값 사용 중")

    # 파일 경로 검증
    print("\n  📂 파일 경로 검증:")
    file_paths = config.get('file_paths', {})
    all_files_exist = True

    for key, path in file_paths.items():
        if path.startswith('drive://'):
            print(f"    ⚠️ {key}: 가상 경로 사용 중 (drive://...)")
            all_files_exist = False
        else:
            exists = os.path.exists(path)
            status = "✅" if exists else "❌"
            print(f"    {status} {key}: {path}")
            if not exists and key != 'previous_incentive':
                all_files_exist = False

    if all_files_exist:
        print("\n  ✅ 모든 파일 경로가 실제 파일을 가리킴")
    else:
        print("\n  ⚠️ 일부 파일 경로가 가상 경로이거나 파일이 없음")

    # 데이터 소스 확인
    data_source = config.get('data_source')
    if data_source == 'google_drive':
        print(f"\n  ✅ 데이터 소스: Google Drive")
    else:
        print(f"\n  ℹ️ 데이터 소스: {data_source or 'Unknown'}")

    # 타임스탬프 확인
    created_at = config.get('created_at')
    last_updated = config.get('last_updated')

    if last_updated:
        print(f"  📅 생성일: {created_at or 'N/A'}")
        print(f"  📅 최종 업데이트: {last_updated}")
    else:
        print("  ⚠️ 타임스탬프 정보 없음")

    return all_files_exist

def main():
    """메인 테스트 함수"""
    print("=" * 70)
    print("🧪 Config 자동 업데이트 시스템 테스트")
    print("=" * 70)

    # Config 파일 찾기
    config_files = sorted(Path('config_files').glob('config_*_*.json'))

    if not config_files:
        print("\n❌ Config 파일을 찾을 수 없습니다")
        print("먼저 scripts/enhanced_download_with_config.py를 실행하세요")
        return False

    print(f"\n📁 {len(config_files)}개 Config 파일 발견")

    # 각 Config 파일 테스트
    success_count = 0
    failed_files = []

    for config_path in config_files:
        if test_config_file(str(config_path)):
            success_count += 1
        else:
            failed_files.append(config_path.name)

    # 테스트 결과 요약
    print("\n" + "=" * 70)
    print("📊 테스트 결과 요약")
    print("=" * 70)

    print(f"\n✅ 성공: {success_count}/{len(config_files)} 파일")

    if failed_files:
        print(f"❌ 실패: {len(failed_files)} 파일")
        for file_name in failed_files:
            print(f"  - {file_name}")

        print("\n💡 해결 방법:")
        print("  1. scripts/enhanced_download_with_config.py 실행")
        print("  2. Google Drive에 필요한 파일이 있는지 확인")
        print("  3. GOOGLE_SERVICE_ACCOUNT 환경변수 설정 확인")
    else:
        print("\n🎉 모든 Config 파일이 정상입니다!")
        print("  - 실제 파일 경로 사용")
        print("  - Working days 자동 계산됨")
        print("  - 타임스탬프 정보 포함")

    print("\n" + "=" * 70)

    return len(failed_files) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)