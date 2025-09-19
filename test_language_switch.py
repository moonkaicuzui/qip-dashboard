#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조직도 및 모달 언어 전환 테스트 스크립트
"""

import json

def test_language_switch():
    """언어 전환 지원 확인"""

    print("=" * 60)
    print("🌐 조직도 및 모달 언어 전환 테스트")
    print("=" * 60)
    print()

    # 번역 파일 로드
    with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # 조직도 관련 번역 키 확인
    print("📋 조직도 탭 번역 확인:")
    print("-" * 40)

    org_keys = [
        ('tabs.orgChart', '탭 이름'),
        ('orgChart.title', '조직도 제목'),
        ('orgChart.incentiveReceived', '인센티브 수령'),
        ('orgChart.incentiveNotReceived', '인센티브 미수령'),
        ('orgChart.filters.viewAll', '전체 보기'),
        ('orgChart.filters.paidOnly', '수령자만'),
        ('orgChart.filters.unpaidOnly', '미수령자만')
    ]

    for key_path, description in org_keys:
        parts = key_path.split('.')
        value = translations
        for part in parts:
            if part in value:
                value = value[part]
            else:
                value = None
                break

        if value and isinstance(value, dict):
            print(f"\n✅ {description} ({key_path}):")
            print(f"   한국어: {value.get('ko', '❌ 없음')}")
            print(f"   English: {value.get('en', '❌ Missing')}")
            print(f"   Tiếng Việt: {value.get('vi', '❌ Thiếu')}")
        else:
            print(f"\n❌ {description} ({key_path}): 번역 키 없음")

    # 모달 관련 번역 키 확인
    print("\n\n📋 모달 번역 확인:")
    print("-" * 40)

    modal_keys = [
        ('modal.modalTitle', '모달 제목'),
        ('modal.calculationStatus.conditionsMet', '조건 충족'),
        ('modal.calculationStatus.conditionsNotMet', '조건 미충족'),
        ('modal.actualVsExpected.actual', '실제 인센티브'),
        ('modal.actualVsExpected.expected', '예상 인센티브'),
        ('modal.subordinateInfo.total', '팀원 전체'),
        ('modal.subordinateInfo.receiving', '인센티브 수령'),
        ('modal.subordinateInfo.notReceiving', '인센티브 미수령'),
        ('modal.tenConditions.1', '조건 1번'),
        ('modal.tenConditions.2', '조건 2번'),
        ('modal.tenConditions.3', '조건 3번'),
        ('modal.tenConditions.4', '조건 4번'),
        ('modal.tenConditions.5', '조건 5번'),
        ('modal.tenConditions.6', '조건 6번'),
        ('modal.tenConditions.7', '조건 7번'),
        ('modal.tenConditions.8', '조건 8번'),
        ('modal.tenConditions.9', '조건 9번'),
        ('modal.tenConditions.10', '조건 10번')
    ]

    for key_path, description in modal_keys:
        parts = key_path.split('.')
        value = translations
        for part in parts:
            if part in value:
                value = value[part]
            else:
                value = None
                break

        if value and isinstance(value, dict):
            has_all = all(lang in value for lang in ['ko', 'en', 'vi'])
            if has_all:
                print(f"✅ {description} ({key_path})")
            else:
                print(f"⚠️ {description} ({key_path}) - 일부 언어 누락")
        else:
            print(f"❌ {description} ({key_path}) - 키 없음")

    print("\n" + "=" * 60)
    print("🎯 테스트 방법:")
    print("  1. 브라우저에서 대시보드 열기")
    print("  2. 조직도 탭 클릭")
    print("  3. 언어 전환 (한국어 → English → Tiếng Việt)")
    print()
    print("✅ 확인 포인트:")
    print("  - 탭 이름이 변경되는지")
    print("  - 필터 옵션 텍스트가 변경되는지")
    print("  - 범례 텍스트가 변경되는지")
    print("  - 노드 툴팁의 '인센티브 수령/미수령'이 변경되는지")
    print("  - 모달 제목과 내용이 변경되는지")
    print("  - 조건 설명이 해당 언어로 표시되는지")
    print("=" * 60)

if __name__ == "__main__":
    test_language_switch()