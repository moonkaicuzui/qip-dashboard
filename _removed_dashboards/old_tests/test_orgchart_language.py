#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조직도 탭 언어 전환 상세 검증 스크립트
HTML 파일을 파싱하여 언어 전환 구현 상태를 검증
"""

import re
from bs4 import BeautifulSoup
import json

def test_orgchart_language_implementation():
    """조직도 탭의 언어 전환 구현 상태를 근본적으로 검증"""

    print("=" * 80)
    print("🔍 조직도 탭 언어 전환 구현 상세 검증")
    print("=" * 80)
    print()

    # 1. HTML 파일 로드 및 파싱
    html_path = "output_files/Incentive_Dashboard_2025_09_Version_5.html"
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"❌ HTML 파일을 찾을 수 없습니다: {html_path}")
        return

    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 2. JavaScript 코드 추출
    script_tags = soup.find_all('script')
    js_code = '\n'.join([tag.string for tag in script_tags if tag.string])

    print("📋 1. 조직도 탭 HTML 요소 확인")
    print("-" * 60)

    # 조직도 탭 버튼 확인
    org_tab = soup.find('div', id='tabOrgChart')
    if org_tab:
        print(f"✅ 조직도 탭 버튼 발견: {org_tab.get_text(strip=True)}")
        print(f"   - ID: tabOrgChart")
        print(f"   - onclick: {org_tab.get('onclick', 'N/A')}")
    else:
        print("❌ 조직도 탭 버튼을 찾을 수 없습니다 (id='tabOrgChart')")

    # 조직도 필터 드롭다운 확인
    org_filter = soup.find('select', id='orgIncentiveFilter')
    if org_filter:
        options = org_filter.find_all('option')
        print(f"\n✅ 조직도 필터 드롭다운 발견:")
        for opt in options:
            opt_id = opt.get('id', 'ID 없음')
            opt_text = opt.get_text(strip=True)
            opt_value = opt.get('value', '')
            print(f"   - {opt_id}: '{opt_text}' (value='{opt_value}')")
    else:
        print("\n❌ 조직도 필터 드롭다운을 찾을 수 없습니다")

    # 조직도 범례 확인
    legend_elements = {
        'legendReceived': '인센티브 수령 범례',
        'legendNotReceived': '인센티브 미수령 범례',
        'legendIncentiveReceived': '인센티브 수령 범례 (대체)',
        'legendNoIncentive': '인센티브 미수령 범례 (대체)'
    }

    print("\n📋 2. 조직도 범례 요소 확인")
    print("-" * 60)
    for elem_id, description in legend_elements.items():
        elem = soup.find(id=elem_id)
        if elem:
            print(f"✅ {description}: {elem.get_text(strip=True)} (id='{elem_id}')")
        else:
            print(f"❌ {description}을 찾을 수 없습니다 (id='{elem_id}')")

    print("\n📋 3. JavaScript 언어 전환 함수 확인")
    print("-" * 60)

    # updateAllTexts 함수 내 조직도 관련 코드 확인
    if 'updateAllTexts' in js_code:
        print("✅ updateAllTexts 함수 발견")

        # 조직도 관련 업데이트 코드 패턴들
        patterns = {
            'tabOrgChart 업데이트': r"getElementById\('tabOrgChart'\)",
            'filterAll 업데이트': r"getElementById\('filterAll'\)",
            'filterPaid 업데이트': r"getElementById\('filterPaid'\)",
            'filterUnpaid 업데이트': r"getElementById\('filterUnpaid'\)",
            'legendReceived 업데이트': r"getElementById\('legendReceived'\)",
            'legendNotReceived 업데이트': r"getElementById\('legendNotReceived'\)",
            'getTranslation 호출': r"getTranslation\('orgChart\.",
            'updateOrgChart 호출': r"updateOrgChart\(\)"
        }

        for desc, pattern in patterns.items():
            if re.search(pattern, js_code):
                print(f"   ✅ {desc} 코드 확인")
            else:
                print(f"   ❌ {desc} 코드 없음")
    else:
        print("❌ updateAllTexts 함수를 찾을 수 없습니다")

    print("\n📋 4. 조직도 노드 생성 시 언어 지원 확인")
    print("-" * 60)

    # 조직도 노드 툴팁 생성 코드 확인
    if "hasIncentive(d.data)" in js_code:
        print("✅ 조직도 노드 인센티브 표시 코드 발견")

        # 동적 번역 사용 여부 확인
        if "getTranslation('orgChart.incentiveReceived'" in js_code:
            print("   ✅ 인센티브 수령 텍스트 동적 번역 사용")
        else:
            print("   ❌ 인센티브 수령 텍스트 하드코딩됨")

        if "getTranslation('orgChart.incentiveNotReceived'" in js_code:
            print("   ✅ 인센티브 미수령 텍스트 동적 번역 사용")
        else:
            print("   ❌ 인센티브 미수령 텍스트 하드코딩됨")
    else:
        print("❌ 조직도 노드 인센티브 표시 코드를 찾을 수 없습니다")

    print("\n📋 5. 번역 데이터 확인")
    print("-" * 60)

    # translations 객체 확인
    translations_match = re.search(r'const translations = ({[\s\S]*?});', js_code)
    if translations_match:
        try:
            # JavaScript 객체를 Python dict로 변환 (간단한 파싱)
            translations_str = translations_match.group(1)

            # 조직도 관련 번역 키 존재 확인
            org_translation_keys = [
                'tabs.orgChart',
                'orgChart.title',
                'orgChart.incentiveReceived',
                'orgChart.incentiveNotReceived',
                'orgChart.filters.viewAll',
                'orgChart.filters.paidOnly',
                'orgChart.filters.unpaidOnly'
            ]

            for key in org_translation_keys:
                key_pattern = key.replace('.', r'\.')
                if re.search(f'"{key_pattern}"\\s*:', translations_str) or \
                   re.search(f"'{key_pattern}'\\s*:", translations_str):
                    print(f"   ✅ {key} 번역 키 존재")
                else:
                    # 중첩 객체로 확인
                    parts = key.split('.')
                    if all(part in translations_str for part in parts):
                        print(f"   ✅ {key} 번역 키 존재 (중첩 구조)")
                    else:
                        print(f"   ⚠️ {key} 번역 키 확인 필요")
        except Exception as e:
            print(f"   ⚠️ 번역 객체 파싱 실패: {e}")
    else:
        print("❌ translations 객체를 찾을 수 없습니다")

    print("\n📋 6. 언어 전환 이벤트 핸들러 확인")
    print("-" * 60)

    # changeLanguage 함수 확인
    if 'function changeLanguage' in js_code:
        print("✅ changeLanguage 함수 발견")

        # updateAllTexts 호출 여부
        if re.search(r'changeLanguage[\s\S]*?updateAllTexts\(\)', js_code):
            print("   ✅ updateAllTexts() 호출 확인")
        else:
            print("   ❌ updateAllTexts() 호출 없음")

        # updateOrgChart 호출 여부
        if re.search(r'changeLanguage[\s\S]*?updateOrgChart\(\)', js_code):
            print("   ✅ updateOrgChart() 직접 호출")
        elif 'updateOrgChart' in js_code and 'updateAllTexts' in js_code:
            # updateAllTexts 내에서 호출하는지 확인
            if re.search(r'updateAllTexts[\s\S]*?updateOrgChart\(\)', js_code):
                print("   ✅ updateOrgChart()가 updateAllTexts 내에서 호출됨")
            else:
                print("   ⚠️ updateOrgChart() 호출 위치 불명확")
    else:
        print("❌ changeLanguage 함수를 찾을 수 없습니다")

    print("\n" + "=" * 80)
    print("📊 검증 결과 요약")
    print("-" * 60)

    issues = []

    # HTML 요소 체크
    if not org_tab:
        issues.append("조직도 탭 버튼 ID 누락")
    if not org_filter:
        issues.append("필터 드롭다운 ID 누락")

    # JavaScript 체크
    if 'updateAllTexts' not in js_code:
        issues.append("updateAllTexts 함수 누락")
    elif 'tabOrgChart' not in js_code:
        issues.append("조직도 탭 번역 코드 누락")

    if "getTranslation('orgChart.incentiveReceived'" not in js_code:
        issues.append("노드 툴팁 번역 미적용")

    if issues:
        print("⚠️ 발견된 문제:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ 모든 언어 전환 요소가 올바르게 구현되어 있습니다!")

    print("\n🧪 브라우저 테스트 권장사항:")
    print("   1. 대시보드를 브라우저에서 열기")
    print("   2. 개발자 도구 콘솔 열기 (F12)")
    print("   3. 다음 명령 실행:")
    print("      - currentLanguage 확인: console.log(currentLanguage)")
    print("      - 언어 변경: changeLanguage('en')")
    print("      - 조직도 탭 텍스트 확인: document.getElementById('tabOrgChart').textContent")
    print("      - 필터 옵션 확인: document.getElementById('filterAll').textContent")
    print("=" * 80)

if __name__ == "__main__":
    test_orgchart_language_implementation()