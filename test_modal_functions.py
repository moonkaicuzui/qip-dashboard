#!/usr/bin/env python3
"""
모달 함수 검증 스크립트
"""

import re
from pathlib import Path

def test_modal_functions():
    html_path = Path('output_files/Incentive_Dashboard_2025_09_Version_5.html')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("=" * 80)
    print("📊 모달 함수 검증")
    print("=" * 80)
    
    # 함수 존재 확인
    functions_to_check = [
        'showConsecutiveAqlFailDetails',
        'showAqlFailDetails',
        'showValidationModal',
        'closeValidationModal'
    ]
    
    print("\n✅ 함수 존재 확인:")
    for func_name in functions_to_check:
        pattern = f'function {func_name}'
        if pattern in html_content:
            print(f"  ✅ {func_name} 함수 존재")
        else:
            print(f"  ❌ {func_name} 함수 없음")
    
    # consecutiveAqlFail 처리 확인
    print("\n✅ consecutiveAqlFail 처리 확인:")
    if "else if (conditionType === 'consecutiveAqlFail')" in html_content:
        print("  ✅ showValidationModal에 consecutiveAqlFail 처리 추가됨")
        if "showConsecutiveAqlFailDetails()" in html_content:
            print("  ✅ showConsecutiveAqlFailDetails() 호출 확인")
        else:
            print("  ❌ showConsecutiveAqlFailDetails() 호출 없음")
    else:
        print("  ❌ consecutiveAqlFail 조건 처리 없음")
    
    # 모달 클릭 이벤트 확인
    print("\n✅ 모달 클릭 이벤트:")
    if 'onclick="showValidationModal(\'consecutiveAqlFail\')"' in html_content:
        print("  ✅ 3개월 연속 AQL FAIL 카드 클릭 이벤트 설정됨")
    else:
        print("  ❌ 3개월 연속 AQL FAIL 카드 클릭 이벤트 없음")
    
    # backdrop 클릭 처리
    print("\n✅ Backdrop 클릭 처리:")
    if "backdrop.addEventListener('click', closeModal)" in html_content:
        print("  ✅ AQL FAIL 상세 모달 backdrop 클릭 이벤트 설정")
    else:
        print("  ❌ AQL FAIL 상세 모달 backdrop 클릭 이벤트 없음")
    
    if "modal.onclick = function(event)" in html_content:
        print("  ✅ 일반 모달 backdrop 클릭 이벤트 설정")
    
    print("\n" + "=" * 80)
    print("📊 검증 완료")
    print("=" * 80)

if __name__ == "__main__":
    test_modal_functions()
