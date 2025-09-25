#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 테스트 - 인센티브와 매니지먼트 대시보드의 직원 카운트 일치성 검증
"""

import pandas as pd
import json
import sys
from common_employee_filter import EmployeeFilter

def test_unified_counts():
    """두 대시보드가 동일한 직원 카운트를 사용하는지 검증"""
    
    year = 2025
    month = 8
    
    print("=" * 80)
    print("통합 직원 카운트 테스트")
    print("=" * 80)
    
    # 인센티브 대시보드용 데이터 로드
    incentive_file = f"input_files/{year}년 8월 인센티브 지급 세부 정보.csv"
    
    print(f"\n📊 인센티브 대시보드 데이터 로드...")
    try:
        incentive_df = pd.read_csv(incentive_file, encoding='utf-8-sig')
        print(f"  ✓ 파일 로드 성공: {len(incentive_df)} 레코드")
    except Exception as e:
        print(f"  ✗ 파일 로드 실패: {e}")
        return False
        
    # 공통 모듈을 사용하여 필터링
    print("\n🔧 공통 필터링 모듈 적용...")
    filtered_incentive = EmployeeFilter.filter_active_employees(
        incentive_df, month, year, include_future=False
    )
    
    print(f"\n📌 인센티브 대시보드 결과:")
    print(f"  • 원본 레코드: {len(incentive_df)}")
    print(f"  • 활성 직원: {len(filtered_incentive)}")
    
    # TYPE별 카운트
    type1_incentive, type2_incentive, type3_incentive = EmployeeFilter.get_type_statistics(filtered_incentive)
    print(f"  • TYPE-1: {type1_incentive}")
    print(f"  • TYPE-2: {type2_incentive}")
    print(f"  • TYPE-3: {type3_incentive}")
    
    # 팀별 통계 (Team 컬럼 존재시)
    if 'Team' in filtered_incentive.columns or 'TEAM' in filtered_incentive.columns:
        team_col = 'Team' if 'Team' in filtered_incentive.columns else 'TEAM'
        team_stats_incentive = EmployeeFilter.get_team_statistics(
            filtered_incentive, month, year, team_column=team_col
        )
        print(f"\n  팀별 직원 수:")
        for team, stats in sorted(team_stats_incentive.items()):
            print(f"    • {team}: {stats['total']}명")
    
    # 매니지먼트 대시보드 메타데이터 확인
    print(f"\n📊 매니지먼트 대시보드 메타데이터 확인...")
    metadata_file = f"output_files/hr_metadata_{year}.json"
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        month_key = f"{year}_0{month}"
        monthly_data = metadata.get('monthly_data', {}).get(month_key, {})
        
        print(f"\n📌 매니지먼트 대시보드 결과 (메타데이터):")
        print(f"  • 활성 직원: {monthly_data.get('total_employees', 0)}")
        print(f"  • TYPE-1: {monthly_data.get('type1_count', 0)}")
        print(f"  • TYPE-2: {monthly_data.get('type2_count', 0)}")
        print(f"  • TYPE-3: {monthly_data.get('type3_count', 0)}")
        
        team_stats_mgmt = metadata.get('team_stats', {}).get(month_key, {})
        if team_stats_mgmt:
            print(f"\n  팀별 직원 수:")
            for team, stats in sorted(team_stats_mgmt.items()):
                print(f"    • {team}: {stats['total']}명")
        
        # 비교 결과
        print("\n" + "=" * 80)
        print("📊 비교 결과:")
        print("=" * 80)
        
        total_match = len(filtered_incentive) == monthly_data.get('total_employees', 0)
        type1_match = str(type1_incentive) == str(monthly_data.get('type1_count', 0))
        type2_match = str(type2_incentive) == str(monthly_data.get('type2_count', 0))
        type3_match = str(type3_incentive) == str(monthly_data.get('type3_count', 0))
        
        print(f"  • 전체 직원 수 일치: {'✅ YES' if total_match else '❌ NO'}")
        print(f"    - 인센티브: {len(filtered_incentive)}")
        print(f"    - 매니지먼트: {monthly_data.get('total_employees', 0)}")
        
        print(f"  • TYPE-1 일치: {'✅ YES' if type1_match else '❌ NO'}")
        print(f"    - 인센티브: {type1_incentive}")
        print(f"    - 매니지먼트: {monthly_data.get('type1_count', 0)}")
        
        print(f"  • TYPE-2 일치: {'✅ YES' if type2_match else '❌ NO'}")
        print(f"    - 인센티브: {type2_incentive}")
        print(f"    - 매니지먼트: {monthly_data.get('type2_count', 0)}")
        
        print(f"  • TYPE-3 일치: {'✅ YES' if type3_match else '❌ NO'}")
        print(f"    - 인센티브: {type3_incentive}")
        print(f"    - 매니지먼트: {monthly_data.get('type3_count', 0)}")
        
        if total_match and type1_match and type2_match and type3_match:
            print("\n🎉 성공: 모든 직원 카운트가 일치합니다!")
            return True
        else:
            print("\n⚠️ 경고: 일부 카운트가 일치하지 않습니다.")
            print("매니지먼트 대시보드를 다시 생성해보세요.")
            return False
            
    except FileNotFoundError:
        print(f"  ✗ 메타데이터 파일이 없습니다: {metadata_file}")
        print("  매니지먼트 대시보드를 먼저 실행하세요.")
        return False
    except Exception as e:
        print(f"  ✗ 메타데이터 로드 실패: {e}")
        return False
    
if __name__ == "__main__":
    success = test_unified_counts()
    sys.exit(0 if success else 1)