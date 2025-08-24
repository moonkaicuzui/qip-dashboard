#!/usr/bin/env python3
"""
7월 필요 파일 체크 테스트
"""

from pathlib import Path

def check_july_files():
    """7월 계산에 필요한 파일들 체크"""
    base_path = Path.cwd()
    
    print("=" * 60)
    print("7월 계산에 필요한 파일 체크")
    print("=" * 60)
    
    required_files = {
        'basic manpower': base_path / 'input_files' / 'basic manpower data july.csv',
        'AQL history': base_path / 'input_files' / 'AQL history' / '1.HSRG AQL REPORT-JULY.2025.csv',
        '5PRS data': base_path / 'input_files' / '5prs data july.csv',
        'attendance': base_path / 'input_files' / 'attendance' / 'converted' / 'attendance data july_converted.csv'
    }
    
    all_exist = True
    missing_files = []
    
    for file_type, file_path in required_files.items():
        if file_path.exists():
            print(f"✅ {file_type:15}: {file_path.name}")
        else:
            print(f"❌ {file_type:15}: {file_path.name} (없음)")
            missing_files.append(file_path.name)
            all_exist = False
    
    print("\n" + "=" * 60)
    
    if all_exist:
        print("✅ 모든 파일이 존재합니다. 7월 계산이 가능합니다.")
    else:
        print("⚠️ 일부 파일이 없습니다. 7월 계산이 중단될 것입니다.")
        print("\n없는 파일:")
        for missing in missing_files:
            print(f"  - {missing}")
    
    print("=" * 60)
    
    # 7월 출력 파일 존재 여부 체크
    july_output = base_path / 'output_files' / 'output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv'
    
    print("\n7월 출력 파일 상태:")
    if july_output.exists():
        print(f"✅ 이미 존재: {july_output.name}")
        print("   (8월 계산 시 이 파일이 있으면 7월을 다시 계산하지 않습니다)")
    else:
        print(f"❌ 없음: {july_output.name}")
        print("   (8월 계산 시 7월을 자동으로 계산하려고 시도합니다)")
    
    return all_exist

if __name__ == "__main__":
    check_july_files()