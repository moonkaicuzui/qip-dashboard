#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Individual Details Modal 언어 전환 테스트
[PASS], [FAIL] 플레이스홀더가 올바르게 번역되는지 확인
"""

import os
import re
import json
from bs4 import BeautifulSoup

def test_modal_translation():
    """모달의 언어 전환 테스트"""

    # HTML 파일 읽기
    html_path = "output_files/Incentive_Dashboard_2025_09_Version_5.html"

    if not os.path.exists(html_path):
        print(f"❌ 대시보드 파일이 없습니다: {html_path}")
        print("   먼저 integrated_dashboard_final.py를 실행하세요.")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 번역 파일 확인
    translation_path = "config_files/dashboard_translations.json"
    with open(translation_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    print("=" * 60)
    print("Individual Details Modal 언어 전환 테스트")
    print("=" * 60)

    # 1. 플레이스홀더 체크
    print("\n1. 플레이스홀더 교체 확인:")
    print("-" * 40)

    placeholders = ['[PASS]', '[FAIL]', '[CONSECUTIVE_FAIL]']
    found_placeholders = []

    for placeholder in placeholders:
        if placeholder in content:
            found_placeholders.append(placeholder)
            # 해당 플레이스홀더가 있는 부분 찾기
            pattern = f".*{re.escape(placeholder)}.*"
            matches = re.findall(pattern, content)[:3]  # 처음 3개만
            print(f"⚠️  {placeholder} 발견:")
            for match in matches:
                # 긴 라인은 잘라서 보여주기
                if len(match) > 100:
                    match = match[:100] + "..."
                print(f"    {match.strip()}")

    if not found_placeholders:
        print("✅ 플레이스홀더 교체 정상 - JavaScript에서 번역됨")
    else:
        print(f"\n❌ 아직 교체되지 않은 플레이스홀더: {', '.join(found_placeholders)}")

    # 2. JavaScript 번역 코드 확인
    print("\n2. JavaScript 번역 코드 확인:")
    print("-" * 40)

    # 플레이스홀더 교체 코드 찾기
    js_replacements = [
        "actualValue.replace('[PASS]'",
        "actualValue.replace('[FAIL]'",
        "actualValue.replace('[CONSECUTIVE_FAIL]'"
    ]

    for js_code in js_replacements:
        if js_code in content:
            print(f"✅ {js_code} 코드 존재")
        else:
            print(f"❌ {js_code} 코드 없음")

    # 3. 번역 키 존재 확인
    print("\n3. 번역 파일 키 확인:")
    print("-" * 40)

    required_keys = [
        ("modal.conditions.pass", "통과/Pass/Đạt"),
        ("modal.conditions.fail", "실패/Fail/Không đạt"),
        ("modal.conditions.consecutiveFail", "3개월 연속 실패/3-month consecutive failure/Thất bại 3 tháng liên tiếp")
    ]

    for key_path, expected in required_keys:
        keys = key_path.split('.')
        value = translations
        try:
            for key in keys:
                value = value[key]

            if isinstance(value, dict):
                ko = value.get('ko', 'N/A')
                en = value.get('en', 'N/A')
                vi = value.get('vi', 'N/A')
                print(f"✅ {key_path}:")
                print(f"   - 한국어: {ko}")
                print(f"   - English: {en}")
                print(f"   - Tiếng Việt: {vi}")
            else:
                print(f"⚠️ {key_path}: 번역 형식 오류")
        except KeyError:
            print(f"❌ {key_path}: 키가 존재하지 않음")

    # 4. 실제 데이터 확인
    print("\n4. condition_results 데이터 확인:")
    print("-" * 40)

    # employeeData에서 condition_results 찾기
    pattern = r"condition_results.*?\[(.*?)\]"
    matches = re.findall(pattern, content, re.DOTALL)

    if matches:
        # 첫 번째 직원의 condition_results 확인
        first_match = matches[0]
        if '[PASS]' in first_match or '[FAIL]' in first_match:
            print("✅ condition_results에 플레이스홀더 존재 (JavaScript로 번역됨)")
        else:
            print("ℹ️ condition_results에 플레이스홀더 없음 (다른 값 사용 중)")

    # 5. 하드코딩된 한글 확인
    print("\n5. 하드코딩된 한글 텍스트 확인:")
    print("-" * 40)

    hardcoded_korean = ['통과', '실패', '3개월 연속 실패']
    found_hardcoded = []

    # JavaScript 코드 내에서만 확인
    script_pattern = r'<script>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)

    for script in scripts:
        for korean in hardcoded_korean:
            if korean in script and f"'{korean}'" in script:
                found_hardcoded.append(korean)

    if found_hardcoded:
        print(f"⚠️ 하드코딩된 한글 발견: {', '.join(set(found_hardcoded))}")
        print("   (번역 파일에서 가져오지 않는 텍스트)")
    else:
        print("✅ 하드코딩된 한글 없음")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("브라우저에서 대시보드를 열고 Individual Details 모달에서")
    print("언어를 전환하여 실제 동작을 확인하세요.")
    print("=" * 60)

if __name__ == "__main__":
    test_modal_translation()