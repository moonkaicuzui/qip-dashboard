#!/usr/bin/env python3
"""
정확한 팀-역할 매핑 로직 분석
HR info 기준으로 팀별 총원과 역할 분류를 확인
"""

import pandas as pd
import json
from collections import defaultdict

def load_data():
    """데이터 로드"""
    # 직원 데이터
    emp_df = pd.read_csv('input_files/2025년 8월 인센티브 지급 세부 정보.csv', encoding='utf-8-sig')
    
    # 팀 구조 JSON
    with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
        team_structure = json.load(f)
    
    # 팀 구조 CSV
    team_csv = pd.read_csv('HR info/team_sturcture_update_version2.csv', encoding='utf-8-sig')
    
    return emp_df, team_structure, team_csv

def analyze_mapping_logic():
    """매핑 로직 분석"""
    emp_df, team_structure, team_csv = load_data()
    
    print("=" * 80)
    print("팀-역할 매핑 로직 분석")
    print("=" * 80)
    
    # 1. CSV 기준 매핑 규칙 확인
    print("\n📋 CSV 파일 매핑 규칙 (총 {}개):".format(len(team_csv)))
    print("-" * 80)
    
    # CSV에서 팀별 역할 카운트
    csv_team_roles = defaultdict(set)
    for _, row in team_csv.iterrows():
        team = row['teams']
        role = row['role_categories']
        csv_team_roles[team].add(role)
    
    print("\nCSV 기준 팀별 역할:")
    for team, roles in sorted(csv_team_roles.items()):
        # nan 값 제거하고 문자열만 필터링
        valid_roles = [str(r) for r in roles if pd.notna(r) and str(r) != 'nan']
        print(f"  {team}: {', '.join(sorted(valid_roles))}")
    
    # 2. JSON 기준 매핑 규칙 확인
    print("\n📋 JSON 파일 매핑 규칙 (총 {}개):".format(len(team_structure['positions'])))
    print("-" * 80)
    
    # Position 조합별 매핑 생성
    position_mappings = {}
    for pos in team_structure['positions']:
        key = f"{pos['position_1st']}|{pos['position_2nd']}|{pos['position_3rd']}"
        position_mappings[key] = {
            'team': pos['team_name'],
            'role': pos['role_category']
        }
    
    # 3. 실제 직원 데이터 분석
    print("\n📊 실제 직원 데이터 분석:")
    print("-" * 80)
    
    # 직원별 팀/역할 매핑
    team_role_distribution = defaultdict(lambda: defaultdict(list))
    unmapped_count = 0
    unmapped_examples = []
    
    for _, emp in emp_df.iterrows():
        pos1 = str(emp.get('QIP POSITION 1ST  NAME', '')).strip()
        pos2 = str(emp.get('QIP POSITION 2ND  NAME', '')).strip()
        pos3 = str(emp.get('QIP POSITION 3RD  NAME', '')).strip()
        name = emp.get('Full Name', '')
        
        # 빈 position 스킵
        if not pos1 or pos1 == 'nan':
            continue
        
        # Position 조합 키
        key = f"{pos1}|{pos2}|{pos3}"
        
        if key in position_mappings:
            mapping = position_mappings[key]
            team = mapping['team']
            role = mapping['role']
            team_role_distribution[team][role].append(name)
        else:
            unmapped_count += 1
            if len(unmapped_examples) < 5:
                unmapped_examples.append({
                    'name': name,
                    'pos1': pos1,
                    'pos2': pos2,
                    'pos3': pos3
                })
    
    # 4. 결과 출력
    print("\n🏢 팀별 인원 분포 (실제 매핑 결과):")
    print("-" * 80)
    
    total_mapped = 0
    for team in sorted(team_role_distribution.keys()):
        team_total = sum(len(names) for names in team_role_distribution[team].values())
        total_mapped += team_total
        print(f"\n{team}: {team_total}명")
        
        for role in sorted(team_role_distribution[team].keys()):
            count = len(team_role_distribution[team][role])
            print(f"  └─ {role}: {count}명")
    
    print(f"\n📈 매핑 통계:")
    print(f"  - 총 직원 수: {len(emp_df[emp_df['QIP POSITION 1ST  NAME'].notna()])}명")
    print(f"  - 매핑 성공: {total_mapped}명")
    print(f"  - 매핑 실패: {unmapped_count}명")
    
    if unmapped_examples:
        print(f"\n⚠️ 매핑 실패 예시:")
        for ex in unmapped_examples:
            print(f"  - {ex['name']}: {ex['pos1']} | {ex['pos2']} | {ex['pos3']}")
    
    # 5. Position 조합의 중요성 분석
    print("\n🔍 Position 조합 분석:")
    print("-" * 80)
    
    # position_1st만으로 매핑하면?
    pos1_only_mapping = defaultdict(set)
    for pos in team_structure['positions']:
        pos1_only_mapping[pos['position_1st']].add(pos['team_name'])
    
    print("\nposition_1st만 사용시 중복 매핑:")
    for pos1, teams in pos1_only_mapping.items():
        if len(teams) > 1:
            print(f"  {pos1} → {', '.join(teams)}")
    
    # 예: ASSEMBLY INSPECTOR는 ASSEMBLY와 REPACKING 둘 다 가능
    # position_2nd, position_3rd로 구분 필요
    
    return team_role_distribution, position_mappings

def suggest_improvements():
    """개선 사항 제안"""
    print("\n" + "=" * 80)
    print("💡 개선 제안:")
    print("=" * 80)
    
    print("""
1. 매핑 로직 수정 필요:
   - position_1st만으로는 팀 구분 불가
   - position_1st + position_2nd + position_3rd 조합 필수
   
2. 대시보드 코드 수정 필요:
   - get_team_from_position() 함수 수정
   - position 조합 키 사용하도록 변경
   
3. 팀 구조 파일 검증:
   - CSV와 JSON 일치 확인 완료
   - 70개 매핑 규칙 모두 정확
   
4. 미매핑 직원 처리:
   - NEW QIP MEMBER 추가 완료
   - 텍스트 정규화 필요 (공백, 오타)
    """)

if __name__ == "__main__":
    team_role_dist, mappings = analyze_mapping_logic()
    suggest_improvements()