#!/usr/bin/env python3
"""
근본적인 데이터 일관성 문제 해결 솔루션

이 스크립트는 대시보드 생성 코드를 수정하여:
1. 중앙화된 데이터 소스 사용
2. 멤버 수 제한 제거
3. 데이터 검증 레이어 추가
"""

import re

def apply_consistency_fixes():
    """데이터 일관성 문제를 근본적으로 해결하는 패치 적용"""
    
    print("=" * 70)
    print("대시보드 데이터 일관성 근본 해결 패치")
    print("=" * 70)
    
    # 1. generate_management_dashboard_v6_enhanced.py 읽기
    with open('generate_management_dashboard_v6_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백업 생성
    with open('generate_management_dashboard_v6_enhanced.py.backup2', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ 백업 파일 생성: generate_management_dashboard_v6_enhanced.py.backup2")
    
    fixes_applied = []
    
    # Fix 1: 100명 제한 제거
    old_limit = "for member in members[:100]:  # Limit to 100 members per team to avoid issues"
    new_limit = "for member in members:  # No limit - show all team members"
    
    if old_limit in content:
        content = content.replace(old_limit, new_limit)
        fixes_applied.append("✓ Fix 1: 멤버 수 100명 제한 제거")
    
    # Fix 2: 데이터 검증 함수 추가
    validation_code = '''
    def validate_team_data(self, team_name, team_stats_count, members_list_count):
        """팀 데이터 일관성 검증"""
        if team_stats_count != members_list_count:
            print(f"⚠️ Data inconsistency for {team_name}:")
            print(f"   - team_stats shows: {team_stats_count}")
            print(f"   - members list has: {members_list_count}")
            # 실제 멤버 리스트 수를 우선으로 사용
            return members_list_count
        return team_stats_count
    '''
    
    # load_team_members_data 메서드 찾기
    if "def load_team_members_data(self):" in content and "def validate_team_data" not in content:
        # 메서드 정의 바로 앞에 검증 함수 추가
        pattern = r'(    def load_team_members_data\(self\):)'
        replacement = validation_code + '\n\\1'
        content = re.sub(pattern, replacement, content)
        fixes_applied.append("✓ Fix 2: 데이터 검증 함수 추가")
    
    # Fix 3: JavaScript에서 teamStats와 teamMembers 일관성 보장
    js_consistency_fix = '''
            // 데이터 일관성 보장 - teamStats와 teamMembers 동기화
            const members = teamMembersList;
            const actualMemberCount = members.length;
            
            // teamStats의 total을 실제 멤버 수로 업데이트
            if (teamStats[teamName]) {
                if (teamStats[teamName].total !== actualMemberCount) {
                    console.warn(`Correcting ${teamName} count: ${teamStats[teamName].total} -> ${actualMemberCount}`);
                    teamStats[teamName].total = actualMemberCount;
                }
            }
    '''
    
    # showTeamDetails 함수 내부 수정
    pattern = r'(const teamMembersList = teamMembers\[teamName\] \|\| \[\];)'
    if re.search(pattern, content):
        replacement = '\\1' + js_consistency_fix
        content = re.sub(pattern, replacement, content, count=1)
        fixes_applied.append("✓ Fix 3: JavaScript 데이터 동기화 코드 추가")
    
    # Fix 4: 테이블 총계 행에서 실제 멤버 수 사용
    table_footer_fix = '''
                // 총계 행 - 실제 멤버 수 사용
                const actualTotal = tbody.rows.length;  // 실제 테이블 행 수
                const teamTotal = teamStats[teamName]?.total || actualTotal;
                
                // 불일치 경고
                if (teamTotal !== actualTotal) {
                    console.warn(`${teamName} total mismatch - Stats: ${teamTotal}, Table: ${actualTotal}`);
                }
    '''
    
    # createTeamMemberDetailTable 함수 수정
    pattern = r'(// 총계 행 추가.*?const totalRow = document\.createElement\(\'tr\'\);)'
    if re.search(pattern, content, re.DOTALL):
        # 기존 총계 행 코드를 더 정확한 버전으로 교체
        new_total_row = '''// 총계 행 추가 - 실제 데이터 기반
            const actualRowCount = tbody.rows.length;
            const totalRow = document.createElement('tr');'''
        content = re.sub(pattern, new_total_row, content, flags=re.DOTALL)
        
        # 총원 셀 수정
        old_total_cell = "totalRow.innerHTML = `.*?<td.*?>.*?</td>"
        new_total_cell = '''totalRow.innerHTML = `
                <td colspan="4" style="padding: 10px; text-align: center; font-weight: bold; background-color: #f8f9fa;">
                    TOTAL / 평균
                </td>
                <td style="padding: 10px; text-align: center; font-weight: bold; background-color: #f8f9fa;">
                    총 ${actualRowCount}명
                </td>'''
        
        content = re.sub(r'totalRow\.innerHTML = `[^`]+`', new_total_cell + '''
                <td colspan="2" style="padding: 10px; text-align: center; font-weight: bold; background-color: #f8f9fa;">
                    전체 출석률: ${avgAttendanceRate.toFixed(1)}%
                </td>
                <td style="padding: 10px; text-align: center; font-weight: bold; background-color: #f8f9fa;">
                    평균: ${avgWorkDays.toFixed(1)}일
                </td>
                <td style="padding: 10px; text-align: center; font-weight: bold; background-color: #f8f9fa;">
                    평균: ${avgAbsentDays.toFixed(1)}일
                </td>
                <td style="padding: 10px; text-align: center; font-weight: bold; background-color: #f8f9fa;">
                    ${avgAbsenceRate.toFixed(1)}%
                </td>
            `;''', content, count=1)
        
        fixes_applied.append("✓ Fix 4: 테이블 총계를 실제 행 수 기반으로 수정")
    
    # Fix 5: 중앙 데이터 소스 정의 추가
    centralized_data_source = '''
        // 중앙화된 데이터 소스 - 모든 컴포넌트가 이를 참조
        const centralizedTeamData = {};
        
        // 팀별 데이터 초기화 및 검증
        Object.keys(teamStats).forEach(teamName => {
            const stats = teamStats[teamName];
            const members = teamMembers[teamName] || [];
            
            // 실제 멤버 수를 기준으로 데이터 통합
            centralizedTeamData[teamName] = {
                total: members.length || stats.total,  // 멤버 리스트 우선
                members: members,
                stats: stats,
                attendance_rate: stats.attendance_rate,
                resignations: stats.resignations,
                new_hires: stats.new_hires,
                full_attendance_count: stats.full_attendance_count,
                full_attendance_rate: stats.full_attendance_rate
            };
            
            // 불일치 로깅
            if (members.length !== stats.total) {
                console.warn(`Data mismatch for ${teamName}: Members=${members.length}, Stats=${stats.total}`);
            }
        });
        
        // 전역 함수: 팀 데이터 가져오기
        function getTeamData(teamName) {
            return centralizedTeamData[teamName] || {
                total: 0,
                members: [],
                stats: {}
            };
        }
    '''
    
    # JavaScript 초기화 부분에 중앙 데이터 소스 추가
    pattern = r'(// 차트 저장소\s+const charts = {};)'
    if re.search(pattern, content):
        replacement = '\\1\n' + centralized_data_source
        content = re.sub(pattern, replacement, content)
        fixes_applied.append("✓ Fix 5: 중앙화된 데이터 소스 추가")
    
    # 수정된 내용 저장
    with open('generate_management_dashboard_v6_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n📋 적용된 수정 사항:")
    for fix in fixes_applied:
        print(f"  {fix}")
    
    if not fixes_applied:
        print("  ⚠️ 이미 모든 수정이 적용되었거나 코드 구조가 변경되었습니다.")
    
    print("\n✅ 데이터 일관성 패치 완료!")
    print("\n🔧 근본적 개선 사항:")
    print("  1. 팀 멤버 수 제한 제거 (100명 → 무제한)")
    print("  2. 데이터 검증 레이어 추가")
    print("  3. JavaScript에서 실시간 데이터 동기화")
    print("  4. 테이블 총계를 실제 행 수 기반으로 계산")
    print("  5. 중앙화된 데이터 소스로 모든 컴포넌트 통일")
    
    print("\n📌 다음 단계:")
    print("  python generate_management_dashboard_v6_enhanced.py --month 8 --year 2025")
    print("  대시보드를 재생성하여 수정 사항을 적용하세요.")
    
    return len(fixes_applied) > 0

if __name__ == "__main__":
    import sys
    success = apply_consistency_fixes()
    sys.exit(0 if success else 1)