#!/usr/bin/env python3
"""
실제 데이터 기반 모달 기능 심층 테스트
"""
import json
import re

def test_real_data_modal():
    """실제 데이터로 모달 기능 심층 테스트"""

    print("="*60)
    print("🔬 실제 데이터 기반 심층 테스트")
    print("="*60)

    html_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html"

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # JavaScript 변수에서 employeeData 추출
    print("\n[DATA TEST 1] 직원 데이터 추출 및 분석")
    emp_data_match = re.search(r'const employeeData = (\[.*?\]);', content, re.DOTALL)

    if emp_data_match:
        data_str = emp_data_match.group(1)
        # NaN을 null로 변경
        data_str = re.sub(r'\bNaN\b', 'null', data_str)

        try:
            employees = json.loads(data_str)
            print(f"✅ 직원 데이터 추출 성공: {len(employees)}명")

            # TYPE-1 LINE LEADER 찾기
            line_leaders = []
            for emp in employees:
                if (emp.get('type') == 'TYPE-1' and
                    emp.get('position') and
                    'LINE LEADER' in emp['position'].upper()):
                    line_leaders.append(emp)

            print(f"✅ TYPE-1 LINE LEADER 발견: {len(line_leaders)}명")

            if line_leaders:
                # 첫 번째 LINE LEADER 테스트
                test_leader = line_leaders[0]
                print(f"\n📋 테스트 대상: {test_leader['name']} (ID: {test_leader['emp_no']})")
                print(f"   직급: {test_leader['position']}")
                print(f"   9월 인센티브: {test_leader.get('september_incentive', '0')}")

                # 부하직원 확인
                subordinates = []
                for emp in employees:
                    if emp.get('boss_id') == test_leader['emp_no'] and emp.get('type') == 'TYPE-1':
                        subordinates.append(emp)

                print(f"   TYPE-1 부하직원: {len(subordinates)}명")

                if subordinates:
                    # 인센티브 계산 검증
                    total_sub_incentive = 0
                    receiving_count = 0

                    for sub in subordinates:
                        incentive = float(sub.get('september_incentive', '0') or '0')
                        if incentive > 0:
                            total_sub_incentive += incentive
                            receiving_count += 1

                    if len(subordinates) > 0:
                        ratio = receiving_count / len(subordinates)
                        expected = total_sub_incentive * 0.12 * ratio

                        print(f"\n💡 인센티브 계산 검증:")
                        print(f"   부하 인센티브 합계: ₫{total_sub_incentive:,.0f}")
                        print(f"   수령 비율: {receiving_count}/{len(subordinates)} = {ratio:.1%}")
                        print(f"   예상 계산: ₫{expected:,.0f}")
                        print(f"   실제 인센티브: ₫{float(test_leader.get('september_incentive', '0') or '0'):,.0f}")

                        # 차이 확인
                        actual = float(test_leader.get('september_incentive', '0') or '0')
                        if abs(actual - expected) < 1000:
                            print("   ✅ 계산 일치")
                        else:
                            print(f"   ⚠️ 계산 차이: ₫{abs(actual - expected):,.0f}")

        except Exception as e:
            print(f"❌ 데이터 파싱 오류: {e}")
    else:
        print("❌ employeeData를 찾을 수 없음")

    # HTML 노드 구조 테스트
    print("\n[DATA TEST 2] HTML 노드 구조 검증")

    # node-incentive-info 요소 찾기
    node_pattern = r'<div class="node-incentive-info" data-node-id="(\d+)">'
    nodes = re.findall(node_pattern, content)

    if nodes:
        print(f"✅ 인센티브 클릭 가능 노드: {len(nodes)}개")
        print(f"   예시 Node IDs: {nodes[:5]}")
    else:
        print("❌ 클릭 가능한 인센티브 노드가 없음")

    # 인센티브 금액 표시 확인
    amount_pattern = r'<span class="incentive-amount">₫([\d,]+)</span>'
    amounts = re.findall(amount_pattern, content)

    if amounts:
        print(f"✅ 인센티브 금액 표시: {len(amounts)}개")
        print(f"   금액 예시: {amounts[:3]}")
    else:
        print("❌ 인센티브 금액이 표시되지 않음")

    # 모달 트리거 테스트
    print("\n[DATA TEST 3] 모달 트리거 메커니즘 검증")

    # showIncentiveModal 호출 확인
    if "window.showIncentiveModal" in content:
        print("✅ 전역 모달 함수 존재")

        # 함수 내부 로직 확인
        if "employeeData.find(emp => emp.emp_no === nodeId)" in content:
            print("✅ 직원 데이터 검색 로직 존재")
        else:
            print("❌ 직원 데이터 검색 로직 없음")

        if "new bootstrap.Modal" in content:
            print("✅ Bootstrap 모달 생성 코드 존재")
        else:
            print("❌ Bootstrap 모달 생성 코드 없음")
    else:
        print("❌ 전역 모달 함수 없음")

    # 이벤트 리스너 확인
    if "handleIncentiveClick" in content:
        print("✅ 인센티브 클릭 핸들러 존재")
    else:
        print("❌ 인센티브 클릭 핸들러 없음")

    print("\n[DATA TEST 4] 부하직원 테이블 구조 검증")

    # 부하직원 테이블 헤더 확인
    if "📋 인센티브 계산 기반 부하직원 상세" in content:
        print("✅ 부하직원 상세 섹션 존재")

        # 테이블 구조 확인
        table_headers = ['이름', '직급', '인센티브', '수령 여부', '계산 기여']
        missing_headers = []

        for header in table_headers:
            # 다양한 형태로 확인 (th 태그 내, td 태그 내 등)
            if f'>{header}<' in content or f'<th>{header}</th>' in content:
                print(f"   ✅ 헤더 '{header}' 존재")
            else:
                missing_headers.append(header)
                print(f"   ❌ 헤더 '{header}' 없음")

        if not missing_headers:
            print("✅ 모든 테이블 헤더 완비")
        else:
            print(f"⚠️ 누락된 헤더: {', '.join(missing_headers)}")

    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)

if __name__ == "__main__":
    test_real_data_modal()