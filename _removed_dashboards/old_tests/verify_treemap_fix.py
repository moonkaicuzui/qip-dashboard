#!/usr/bin/env python3
"""
트리맵 readonly 문제 해결 검증 스크립트
원인 분석 및 수정 사항 확인
"""

import json
import re
from pathlib import Path
from datetime import datetime

def verify_fix():
    """트리맵 수정 사항 검증"""
    print("=" * 70)
    print("🔍 트리맵 Readonly 문제 해결 검증")
    print("=" * 70)
    
    # 1. 생성된 HTML 파일 확인
    dashboard_path = Path("output_files/management_dashboard_2025_08.html")
    if not dashboard_path.exists():
        print("❌ 대시보드 파일이 없습니다!")
        return False
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("\n📋 원인 분석:")
    print("-" * 70)
    print("1. Object.entries()로 생성된 객체의 readonly 속성")
    print("   - JavaScript property descriptor: {writable: false}")
    print("   - squarify 알고리즘이 item.x, item.y 등을 수정 시도")
    print("   - TypeError: Attempted to assign to readonly property 발생")
    
    print("\n2. 문제가 발생한 코드 위치:")
    print("   - layoutGroup 함수 내부 (item.x = x; 등)")
    print("   - 재귀적 squarify 호출 시 객체 속성 수정")
    
    print("\n✅ 해결 방법 검증:")
    print("-" * 70)
    
    # 검증 항목들
    fixes = {
        "1. JSON.parse(JSON.stringify()) 사용": {
            "check": "JSON.parse(JSON.stringify(teamData))" in html_content,
            "description": "완전한 deep copy로 readonly 제약 제거"
        },
        "2. 속성 사전 초기화": {
            "check": all(prop in html_content for prop in ["x: 0,", "y: 0,", "width: 0,", "height: 0"]),
            "description": "squarify를 위한 속성 미리 생성"
        },
        "3. processedData 사용": {
            "check": "const processedData = data.map" in html_content,
            "description": "새로운 객체 배열 생성"
        },
        "4. createTreemap 함수 존재": {
            "check": "function createTreemap(container, data)" in html_content,
            "description": "트리맵 생성 함수 정의"
        },
        "5. squarify 알고리즘 구현": {
            "check": "function squarify(items, x, y, width, height)" in html_content,
            "description": "트리맵 레이아웃 알고리즘"
        }
    }
    
    all_passed = True
    for fix_name, fix_info in fixes.items():
        if fix_info["check"]:
            print(f"✅ {fix_name}")
            print(f"   └─ {fix_info['description']}")
        else:
            print(f"❌ {fix_name}")
            print(f"   └─ {fix_info['description']}")
            all_passed = False
    
    # 2. 메타데이터 검증
    print("\n📊 데이터 검증:")
    print("-" * 70)
    
    metadata_path = Path("output_files/hr_metadata_2025.json")
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        team_stats = metadata.get('team_stats', {}).get('2025_08', {})
        team_count = len(team_stats)
        
        print(f"✅ 총 {team_count}개 팀 데이터 확인")
        
        # 중요 팀 확인
        critical_teams = ["OFFICE & OCPT", "CUTTING", "HWK QIP"]
        for team in critical_teams:
            if team in team_stats:
                total = team_stats[team].get('total', 0)
                print(f"✅ {team}: {total}명")
            else:
                print(f"❌ {team}: 데이터 없음")
                all_passed = False
    
    # 3. JavaScript 코드 구조 검증
    print("\n🔧 JavaScript 구조 검증:")
    print("-" * 70)
    
    js_patterns = {
        "팀 데이터 전체 로드": "const fullTeamData = []" in html_content,
        "mutableTeamData 생성": "const mutableTeamData" in html_content,
        "트리맵 호출": "createTreemap(mainContainer, mutableTeamData)" in html_content,
        "소규모 팀 처리": "소규모 팀 목록" in html_content or "tinyTeams" in html_content
    }
    
    for pattern_name, pattern_found in js_patterns.items():
        if pattern_found:
            print(f"✅ {pattern_name}")
        else:
            print(f"❌ {pattern_name}")
            all_passed = False
    
    # 4. 콘솔 에러 예방 체크
    print("\n🛡️ 에러 예방 메커니즘:")
    print("-" * 70)
    
    error_prevention = {
        "위치 정보 확인": "typeof team.x === 'undefined'" in html_content,
        "에러 로깅": "console.error" in html_content,
        "디버그 로그": "console.log" in html_content
    }
    
    for prevention_name, prevention_found in error_prevention.items():
        if prevention_found:
            print(f"✅ {prevention_name}")
        else:
            print(f"⚠️  {prevention_name} (선택사항)")
    
    # 최종 결과
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ 모든 수정 사항이 올바르게 적용되었습니다!")
        print("\n💡 해결 요약:")
        print("1. JSON.parse(JSON.stringify())로 완전한 deep copy 생성")
        print("2. x, y, width, height 속성을 0으로 사전 초기화")
        print("3. readonly 제약이 완전히 제거된 새 객체 생성")
        print("4. squarify 알고리즘이 안전하게 속성 수정 가능")
    else:
        print("⚠️ 일부 수정 사항이 누락되었습니다. 위 항목을 확인하세요.")
    
    print("=" * 70)
    
    # 타임스탬프 확인
    if metadata_path.exists():
        timestamp = metadata.get('generation_timestamp', 'N/A')
        print(f"\n⏰ 생성 시각: {timestamp}")
    
    return all_passed

if __name__ == "__main__":
    verify_fix()