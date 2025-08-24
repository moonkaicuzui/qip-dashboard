#!/usr/bin/env python3
"""
7월 계산 실패 시 8월도 중단되는지 테스트
"""

import subprocess
import sys
from pathlib import Path

def test_stop_on_failure():
    """7월 실패 시 8월도 중단되는지 테스트"""
    base_path = Path.cwd()
    
    print("=" * 60)
    print("7월 계산 실패 시 8월 중단 테스트")
    print("=" * 60)
    
    # 7월 출력 파일이 있으면 삭제 (테스트를 위해)
    july_output = base_path / 'output_files' / 'output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv'
    if july_output.exists():
        print(f"\n기존 7월 파일 삭제: {july_output.name}")
        july_output.unlink()
    
    # 8월 계산 실행
    print("\n8월 인센티브 계산 시작...")
    print("-" * 40)
    
    cmd = [
        'python3',
        'src/step1_인센티브_계산_개선버전.py',
        '--config',
        'config_files/config_august_2025.json'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=base_path
        )
        
        print("\n실행 결과:")
        print("-" * 40)
        
        # 출력에서 주요 메시지 찾기
        output_lines = result.stdout.split('\n') + result.stderr.split('\n')
        
        july_stop_found = False
        august_stop_found = False
        exception_found = False
        
        for line in output_lines:
            if '7월 계산을 중단합니다' in line:
                july_stop_found = True
                print(f"✅ 7월 중단 메시지 확인: {line.strip()}")
            if '8월 계산도 중단합니다' in line:
                august_stop_found = True
                print(f"✅ 8월 중단 메시지 확인: {line.strip()}")
            if '월 데이터가 없어' in line and '월 계산을 중단합니다' in line:
                exception_found = True
                print(f"✅ 예외 메시지 확인: {line.strip()}")
        
        print("\n" + "=" * 60)
        print("테스트 결과:")
        print("-" * 40)
        
        if july_stop_found and august_stop_found:
            print("✅ 성공: 7월 실패 시 8월도 정상적으로 중단됨")
        else:
            print("❌ 실패: 예상된 중단 메시지를 찾을 수 없음")
            print("\n전체 출력 (처음 50줄):")
            for i, line in enumerate(output_lines[:50]):
                if line.strip():
                    print(f"  {i+1}: {line}")
        
        # 반환 코드 확인
        if result.returncode != 0:
            print(f"\n프로세스 종료 코드: {result.returncode} (오류로 종료됨)")
        else:
            print(f"\n프로세스 종료 코드: {result.returncode} (정상 종료)")
            
    except subprocess.TimeoutExpired:
        print("⚠️ 실행 시간 초과 (10초)")
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
    
    print("=" * 60)
    print("테스트 완료")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_stop_on_failure())