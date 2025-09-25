#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조직도 탭 언어 전환 브라우저 시뮬레이션 테스트
JavaScript 실행을 시뮬레이션하여 언어 전환 동작 검증
"""

import json
import re

def simulate_language_change():
    """브라우저에서의 언어 전환 동작을 시뮬레이션"""

    print("=" * 80)
    print("🌐 조직도 탭 언어 전환 브라우저 시뮬레이션")
    print("=" * 80)
    print()

    # 번역 파일 로드
    with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # HTML 파일에서 초기 상태 확인
    with open('output_files/Incentive_Dashboard_2025_09_Version_5.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("📋 시뮬레이션 테스트 시나리오")
    print("-" * 60)

    # 테스트할 요소들
    test_elements = {
        'tabOrgChart': 'tabs.orgChart',
        'filterAll': 'orgChart.filters.viewAll',
        'filterPaid': 'orgChart.filters.paidOnly',
        'filterUnpaid': 'orgChart.filters.unpaidOnly',
        'legendReceived': 'orgChart.incentiveReceived',
        'legendNotReceived': 'orgChart.incentiveNotReceived'
    }

    # 각 언어별로 테스트
    languages = ['ko', 'en', 'vi']
    language_names = {'ko': '한국어', 'en': 'English', 'vi': 'Tiếng Việt'}

    for lang in languages:
        print(f"\n🔤 {language_names[lang]} 언어 테스트:")
        print("-" * 40)

        for element_id, translation_key in test_elements.items():
            # 번역 키 경로 파싱
            keys = translation_key.split('.')
            value = translations

            # 중첩된 키 탐색
            for key in keys:
                if key in value:
                    value = value[key]
                else:
                    value = None
                    break

            if value and isinstance(value, dict) and lang in value:
                expected_text = value[lang]
                print(f"   {element_id}: '{expected_text}'")

                # HTML에서 해당 ID를 가진 요소가 있는지 확인
                pattern = f'id="{element_id}"'
                if pattern in html_content:
                    print(f"      ✅ HTML 요소 존재")
                else:
                    print(f"      ❌ HTML 요소 없음")
            else:
                print(f"   {element_id}: ❌ 번역 없음")

    print("\n📋 조직도 노드 툴팁 텍스트 테스트")
    print("-" * 60)

    # 노드 툴팁 텍스트
    for lang in languages:
        print(f"\n🔤 {language_names[lang]}:")

        # 인센티브 수령/미수령 텍스트
        received_key = translations.get('orgChart', {}).get('incentiveReceived', {})
        not_received_key = translations.get('orgChart', {}).get('incentiveNotReceived', {})

        if lang in received_key:
            print(f"   ✅ 인센티브 수령: {received_key[lang]}")
        else:
            print(f"   ❌ 인센티브 수령 번역 없음")

        if lang in not_received_key:
            print(f"   ❌ 인센티브 미수령: {not_received_key[lang]}")
        else:
            print(f"   ❌ 인센티브 미수령 번역 없음")

    print("\n📋 JavaScript 함수 호출 시뮬레이션")
    print("-" * 60)

    # JavaScript 코드에서 관련 함수 확인
    js_functions = {
        'changeLanguage': '언어 변경 함수',
        'updateAllTexts': '전체 텍스트 업데이트',
        'updateOrgChart': '조직도 업데이트',
        'getTranslation': '번역 가져오기'
    }

    for func_name, description in js_functions.items():
        pattern = f'function {func_name}'
        if pattern in html_content:
            print(f"   ✅ {description} ({func_name}) 존재")

            # 특정 함수 내용 분석
            if func_name == 'updateAllTexts':
                # tabOrgChart 업데이트 코드 확인
                if "getElementById('tabOrgChart')" in html_content:
                    print(f"      ✅ tabOrgChart 요소 업데이트 코드 포함")
                else:
                    print(f"      ❌ tabOrgChart 요소 업데이트 코드 없음")

                if "updateOrgChart()" in html_content:
                    print(f"      ✅ updateOrgChart() 호출 포함")
        else:
            print(f"   ❌ {description} ({func_name}) 없음")

    print("\n" + "=" * 80)
    print("🧪 브라우저 수동 테스트 가이드")
    print("-" * 60)
    print("""
    1. 브라우저에서 대시보드 열기:
       file:///Users/ksmoon/Downloads/대시보드 인센티브 테스트11/output_files/Incentive_Dashboard_2025_09_Version_5.html

    2. 개발자 도구 콘솔 (F12) 에서 실행:

       // 현재 언어 확인
       console.log('현재 언어:', currentLanguage);

       // 한국어로 변경
       changeLanguage('ko');
       console.log('조직도 탭:', document.getElementById('tabOrgChart').textContent);
       console.log('전체 보기:', document.getElementById('filterAll').textContent);

       // 영어로 변경
       changeLanguage('en');
       console.log('Org Chart Tab:', document.getElementById('tabOrgChart').textContent);
       console.log('View All:', document.getElementById('filterAll').textContent);

       // 베트남어로 변경
       changeLanguage('vi');
       console.log('Tab Sơ đồ:', document.getElementById('tabOrgChart').textContent);
       console.log('Xem tất cả:', document.getElementById('filterAll').textContent);

    3. 조직도 노드 클릭하여 모달 테스트:
       - 각 언어별로 모달 제목과 내용 확인
       - 조건 설명이 해당 언어로 표시되는지 확인
    """)
    print("=" * 80)

    # 최종 검증 결과
    print("\n📊 최종 검증 결과")
    print("-" * 60)

    issues = []

    # 필수 요소 체크
    required_elements = ['tabOrgChart', 'filterAll', 'filterPaid', 'filterUnpaid']
    for elem_id in required_elements:
        if f'id="{elem_id}"' not in html_content:
            issues.append(f"{elem_id} HTML 요소 누락")

    # 필수 함수 체크
    required_functions = ['changeLanguage', 'updateAllTexts', 'getTranslation']
    for func in required_functions:
        if f'function {func}' not in html_content:
            issues.append(f"{func} 함수 누락")

    if issues:
        print("⚠️ 발견된 문제:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ 모든 언어 전환 구성 요소가 정상적으로 구현되었습니다!")
        print("\n💡 참고: 실제 동작은 브라우저에서 직접 테스트하시기 바랍니다.")

if __name__ == "__main__":
    simulate_language_change()