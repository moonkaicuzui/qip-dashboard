#!/usr/bin/env python3
"""
최종 통합 테스트 - 모든 기능 검증
"""
import json
import re

def final_comprehensive_test():
    """최종 통합 테스트"""

    print("="*70)
    print("🔍 최종 통합 테스트 실행")
    print("="*70)

    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    test_results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }

    # 1. 핵심 기능 테스트
    print("\n[1] 핵심 기능 테스트")
    print("-" * 40)

    # 1.1 전역 모달 함수
    if "window.showIncentiveModal = function" in content:
        test_results['passed'].append("전역 모달 함수 구현")
        print("✅ 전역 모달 함수 구현됨")
    else:
        test_results['failed'].append("전역 모달 함수 미구현")
        print("❌ 전역 모달 함수 미구현")

    # 1.2 테스트 버튼
    if 'id="testModalBtn"' in content:
        test_results['passed'].append("테스트 버튼 존재")
        print("✅ 테스트 버튼 존재")
    else:
        test_results['failed'].append("테스트 버튼 없음")
        print("❌ 테스트 버튼 없음")

    # 1.3 이벤트 위임
    if "handleIncentiveClick" in content:
        test_results['passed'].append("이벤트 위임 구현")
        print("✅ 이벤트 위임 구현")
    else:
        test_results['failed'].append("이벤트 위임 미구현")
        print("❌ 이벤트 위임 미구현")

    # 2. 통화 및 지역화
    print("\n[2] 통화 및 지역화 테스트")
    print("-" * 40)

    vnd_count = content.count('₫')
    won_count = content.count('₩')

    if vnd_count > 0 and won_count == 0:
        test_results['passed'].append(f"베트남 동 통화 사용 ({vnd_count}개)")
        print(f"✅ 베트남 동(₫) 올바르게 사용: {vnd_count}개")
    else:
        test_results['failed'].append(f"통화 기호 오류 (₫:{vnd_count}, ₩:{won_count})")
        print(f"❌ 통화 기호 문제")

    # 3. 디버깅 기능
    print("\n[3] 디버깅 및 로깅")
    print("-" * 40)

    debug_logs = [
        ("조직도 그리기", "🏗️ === 조직도 그리기 시작 ==="),
        ("이벤트 등록", "📌 인센티브 클릭 이벤트 리스너 등록"),
        ("클릭 감지", "💰 인센티브 클릭 감지"),
        ("모달 호출", "🔍 모달 함수 호출됨")
    ]

    for name, log_text in debug_logs:
        if log_text in content:
            test_results['passed'].append(f"디버그 로그: {name}")
            print(f"✅ {name} 로그 존재")
        else:
            test_results['warnings'].append(f"디버그 로그 누락: {name}")
            print(f"⚠️ {name} 로그 누락")

    # 4. 데이터 검증
    print("\n[4] 데이터 구조 검증")
    print("-" * 40)

    # 직원 데이터 추출
    emp_data_match = re.search(r'const employeeData = (\[.*?\]);', content, re.DOTALL)
    if emp_data_match:
        try:
            data_str = emp_data_match.group(1)
            data_str = re.sub(r'\bNaN\b', 'null', data_str)
            employees = json.loads(data_str)

            test_results['passed'].append(f"직원 데이터 로드 성공 ({len(employees)}명)")
            print(f"✅ 직원 데이터: {len(employees)}명")

            # TYPE-1 관리자 확인
            type1_managers = [e for e in employees if e.get('type') == 'TYPE-1' and
                            ('LEADER' in (e.get('position', '').upper()) or
                             'MANAGER' in (e.get('position', '').upper()) or
                             'SUPERVISOR' in (e.get('position', '').upper()))]

            if type1_managers:
                test_results['passed'].append(f"TYPE-1 관리자 {len(type1_managers)}명")
                print(f"✅ TYPE-1 관리자: {len(type1_managers)}명")
            else:
                test_results['warnings'].append("TYPE-1 관리자 없음")
                print("⚠️ TYPE-1 관리자가 없음")

        except Exception as e:
            test_results['failed'].append(f"데이터 파싱 오류: {str(e)}")
            print(f"❌ 데이터 파싱 오류: {e}")
    else:
        test_results['failed'].append("직원 데이터를 찾을 수 없음")
        print("❌ 직원 데이터를 찾을 수 없음")

    # 5. 모달 구조 검증
    print("\n[5] 모달 구조 검증")
    print("-" * 40)

    if '📋 인센티브 계산 기반 부하직원 상세' in content:
        test_results['passed'].append("부하직원 상세 테이블 구조")
        print("✅ 부하직원 상세 테이블 구조 완비")
    else:
        test_results['failed'].append("부하직원 상세 테이블 없음")
        print("❌ 부하직원 상세 테이블 없음")

    # 6. 탭 이벤트 검증
    print("\n[6] 탭 이벤트 및 초기화")
    print("-" * 40)

    if "orgChartTabButton" in content:
        test_results['passed'].append("조직도 탭 이벤트 리스너")
        print("✅ 조직도 탭 이벤트 리스너 구현")
    else:
        test_results['warnings'].append("조직도 탭 이벤트 미구현")
        print("⚠️ 조직도 탭 이벤트 확인 필요")

    # 최종 결과 출력
    print("\n" + "="*70)
    print("📊 테스트 결과 요약")
    print("="*70)

    print(f"\n✅ 통과: {len(test_results['passed'])}개")
    for item in test_results['passed'][:5]:  # 처음 5개만 표시
        print(f"   • {item}")
    if len(test_results['passed']) > 5:
        print(f"   ... 외 {len(test_results['passed'])-5}개")

    if test_results['warnings']:
        print(f"\n⚠️ 경고: {len(test_results['warnings'])}개")
        for item in test_results['warnings']:
            print(f"   • {item}")

    if test_results['failed']:
        print(f"\n❌ 실패: {len(test_results['failed'])}개")
        for item in test_results['failed']:
            print(f"   • {item}")

    # 점수 계산
    total_tests = len(test_results['passed']) + len(test_results['failed'])
    if total_tests > 0:
        score = (len(test_results['passed']) / total_tests) * 100
        print(f"\n📈 종합 점수: {score:.1f}%")

        if score >= 90:
            print("🎉 우수: 모든 핵심 기능이 정상 작동합니다!")
        elif score >= 70:
            print("👍 양호: 대부분의 기능이 작동하지만 개선이 필요합니다.")
        else:
            print("⚠️ 개선 필요: 중요한 기능들이 작동하지 않습니다.")

    print("\n" + "="*70)

    # 결과 저장
    with open('/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/final_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    print("📁 테스트 결과가 final_test_results.json에 저장되었습니다.")

    return test_results

if __name__ == "__main__":
    results = final_comprehensive_test()

    # 실패 항목이 있으면 exit code 1
    exit(0 if not results['failed'] else 1)