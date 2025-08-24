#!/usr/bin/env python3
"""
경로 수정 테스트
"""

from pathlib import Path

def test_path_fix():
    """경로 수정 확인"""
    base_path = Path.cwd()
    
    print("=" * 60)
    print("경로 수정 테스트")
    print("=" * 60)
    print(f"\n현재 작업 디렉토리: {base_path}")
    
    # 7월 파일 경로 테스트
    print("\n7월 파일 경로 확인:")
    print("-" * 40)
    
    july_files = {
        'basic': base_path / 'input_files' / 'basic manpower data july.csv',
        'aql': base_path / 'input_files' / 'AQL history' / '1.HSRG AQL REPORT-JULY.2025.csv',
        '5prs': base_path / 'input_files' / '5prs data july.csv',
        'attendance': base_path / 'input_files' / 'attendance' / 'converted' / 'attendance data july_converted.csv'
    }
    
    all_exist = True
    for file_type, file_path in july_files.items():
        if file_path.exists():
            print(f"✅ {file_type:12}: {file_path.name}")
        else:
            print(f"❌ {file_type:12}: {file_path.name}")
            print(f"   전체 경로: {file_path}")
            all_exist = False
    
    print("\n" + "=" * 60)
    
    if all_exist:
        print("✅ 모든 7월 파일을 찾았습니다!")
        print("   경로 수정이 성공적으로 적용되었습니다.")
    else:
        print("❌ 일부 파일을 찾을 수 없습니다.")
        print("   경로를 다시 확인해주세요.")
    
    # 8월 파일도 확인
    print("\n8월 AQL 파일 경로 확인:")
    print("-" * 40)
    
    august_aql = base_path / 'input_files' / 'AQL history' / '1.HSRG AQL REPORT-AUGUST.2025.csv'
    if august_aql.exists():
        print(f"✅ AQL: {august_aql.name}")
        print(f"   전체 경로: {august_aql}")
    else:
        print(f"❌ AQL: {august_aql.name}")
        print(f"   전체 경로: {august_aql}")
    
    print("=" * 60)
    
    return all_exist

if __name__ == "__main__":
    test_path_fix()