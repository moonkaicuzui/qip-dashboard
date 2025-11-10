#!/usr/bin/env python3
"""
언어 전환 개선 스크립트
하드코딩된 한국어 텍스트를 번역 시스템과 통합
"""

import json
import re

def fix_translations():
    # 1. dashboard_translations.json에 누락된 번역 추가
    with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # 테이블 헤더 번역 추가
    if 'tableHeaders' not in translations:
        translations['tableHeaders'] = {}

    translations['tableHeaders']['avgPaymentPaid'] = {
        'ko': '평균 지급액',
        'en': 'Avg Payment',
        'vi': 'TB thanh toán'
    }
    translations['tableHeaders']['avgPaymentPaidBasis'] = {
        'ko': '수령인원 기준',
        'en': 'Based on Paid',
        'vi': 'Dựa trên đã trả'
    }
    translations['tableHeaders']['avgPaymentTotal'] = {
        'ko': '평균 지급액',
        'en': 'Avg Payment',
        'vi': 'TB thanh toán'
    }
    translations['tableHeaders']['avgPaymentTotalBasis'] = {
        'ko': '전체인원 기준',
        'en': 'Based on Total',
        'vi': 'Dựa trên tổng'
    }

    # 섹션 제목 번역 추가
    if 'sectionTitles' not in translations:
        translations['sectionTitles'] = {}

    translations['sectionTitles']['positionDetails'] = {
        'ko': '직급별 상세 현황',
        'en': 'Position Details Status',
        'vi': 'Tình trạng chi tiết theo vị trí'
    }
    translations['sectionTitles']['individualDetails'] = {
        'ko': '개인별 상세 정보',
        'en': 'Individual Details Information',
        'vi': 'Thông tin chi tiết cá nhân'
    }
    translations['sectionTitles']['typeSummary'] = {
        'ko': 'Type별 현황',
        'en': 'Type Summary',
        'vi': 'Tóm tắt theo loại'
    }

    # 모달 제목 번역 추가
    if 'modalTitles' not in translations:
        translations['modalTitles'] = {}

    translations['modalTitles']['positionModal'] = {
        'ko': '직급별 상세 정보',
        'en': 'Position Detail Information',
        'vi': 'Thông tin chi tiết vị trí'
    }

    # 업데이트된 번역 파일 저장
    with open('config_files/dashboard_translations.json', 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print("✅ dashboard_translations.json 업데이트 완료")

    # 2. integrated_dashboard_final.py 수정
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 탭 버튼 텍스트 수정 (하드코딩 -> 번역 시스템 사용)
    replacements = [
        # 탭 버튼 - ID 속성 추가하여 JavaScript에서 번역 가능하도록
        (
            '<div class="tab" data-tab="position" onclick="showTab(\'position\')" id="tabPosition">직급by 상세</div>',
            '<div class="tab" data-tab="position" onclick="showTab(\'position\')" id="tabPosition">직급별 상세</div>'
        ),
        (
            '<div class="tab" data-tab="detail" onclick="showTab(\'detail\')" id="tabIndividual">개인by 상세</div>',
            '<div class="tab" data-tab="detail" onclick="showTab(\'detail\')" id="tabIndividual">개인별 상세</div>'
        ),
        (
            '<div class="tab" data-tab="criteria" onclick="showTab(\'criteria\')" id="tabCriteria">incentive 기준</div>',
            '<div class="tab" data-tab="criteria" onclick="showTab(\'criteria\')" id="tabCriteria">인센티브 기준</div>'
        ),

        # 테이블 헤더
        (
            '<th class="sub-header" id="summaryAvgEligibleHeader">수령인원 기준</th>',
            '<th class="sub-header" id="summaryAvgEligibleHeader"><span data-translate="avgPaymentPaidBasis">수령인원 기준</span></th>'
        ),
        (
            '<th class="sub-header" id="summaryAvgTotalHeader">total원 기준</th>',
            '<th class="sub-header" id="summaryAvgTotalHeader"><span data-translate="avgPaymentTotalBasis">전체인원 기준</span></th>'
        ),

        # 섹션 제목들
        (
            '<h3 id="positionTabTitle">직급by 상세 현황</h3>',
            '<h3 id="positionTabTitle" data-translate="positionDetails">직급별 상세 현황</h3>'
        ),
        (
            '<h3 id="individualDetailTitle">개인by 상세 정보</h3>',
            '<h3 id="individualDetailTitle" data-translate="individualDetails">개인별 상세 정보</h3>'
        ),

        # 모달 제목
        (
            '<h5 class="modal-title" id="positionModalLabel">직급by 상세 정보</h5>',
            '<h5 class="modal-title" id="positionModalLabel" data-translate="positionModal">직급별 상세 정보</h5>'
        ),

        # FAQ 텍스트 내 "개인by" -> "개인별"
        ('개인by 상세 페이지에서', '개인별 상세 페이지에서'),
        ('조건by 충족', '조건별 충족'),

        # "직급by" -> "직급별" 전체 치환
        ('직급by', '직급별'),
        ('개인by', '개인별'),

        # "total원" -> "전체인원"
        ('total원', '전체인원'),
    ]

    for old_text, new_text in replacements:
        content = content.replace(old_text, new_text)

    # JavaScript changeLanguage 함수 개선
    # updateAllTexts 함수에 새 번역 추가
    update_texts_addition = '''
            // 탭 버튼 텍스트 업데이트
            const tabPosition = document.getElementById('tabPosition');
            const tabIndividual = document.getElementById('tabIndividual');
            const tabCriteria = document.getElementById('tabCriteria');

            if (tabPosition) tabPosition.textContent = translations.tabs?.position?.[lang] || '직급별 상세';
            if (tabIndividual) tabIndividual.textContent = translations.tabs?.individual?.[lang] || '개인별 상세';
            if (tabCriteria) tabCriteria.textContent = translations.tabs?.criteria?.[lang] || '인센티브 기준';

            // 테이블 헤더 업데이트
            const avgPaymentHeaders = document.querySelectorAll('[data-translate]');
            avgPaymentHeaders.forEach(elem => {
                const key = elem.getAttribute('data-translate');
                if (translations.tableHeaders && translations.tableHeaders[key]) {
                    elem.textContent = translations.tableHeaders[key][lang] || elem.textContent;
                }
            });

            // 섹션 제목 업데이트
            const positionTabTitle = document.getElementById('positionTabTitle');
            const individualDetailTitle = document.getElementById('individualDetailTitle');
            const summaryTabTitle = document.getElementById('summaryTabTitle');

            if (positionTabTitle) positionTabTitle.textContent = translations.sectionTitles?.positionDetails?.[lang] || '직급별 상세 현황';
            if (individualDetailTitle) individualDetailTitle.textContent = translations.sectionTitles?.individualDetails?.[lang] || '개인별 상세 정보';
            if (summaryTabTitle) summaryTabTitle.textContent = translations.sectionTitles?.typeSummary?.[lang] || 'Type별 현황';

            // 모달 제목 업데이트
            const positionModalLabel = document.getElementById('positionModalLabel');
            if (positionModalLabel) positionModalLabel.textContent = translations.modalTitles?.positionModal?.[lang] || '직급별 상세 정보';
'''

    # updateAllTexts 함수 찾아서 추가 코드 삽입
    update_pos = content.find('function updateAllTexts() {')
    if update_pos != -1:
        # 함수 끝 부분 찾기
        func_end = content.find('// 차트 라벨 업데이트', update_pos)
        if func_end != -1:
            # 차트 라벨 업데이트 직전에 새 코드 삽입
            content = content[:func_end] + update_texts_addition + '\n            ' + content[func_end:]

    # 수정된 파일 저장
    with open('integrated_dashboard_final_translation_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ integrated_dashboard_final_translation_fixed.py 생성 완료")
    print("\n주요 개선 사항:")
    print("  1. '직급by 상세' → '직급별 상세' (올바른 한국어)")
    print("  2. '개인by 상세' → '개인별 상세' (올바른 한국어)")
    print("  3. 'incentive 기준' → '인센티브 기준' (일관된 한국어)")
    print("  4. '수령인원 기준' → 영어/베트남어 번역 추가")
    print("  5. 'total원 기준' → '전체인원 기준' (올바른 한국어)")
    print("\n다음 명령어로 대시보드를 재생성하세요:")
    print("  python integrated_dashboard_final_translation_fixed.py --month 10 --year 2025")

if __name__ == "__main__":
    fix_translations()