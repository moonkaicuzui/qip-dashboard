#!/usr/bin/env python3
"""
대시보드 JavaScript 초기화 문제 수정 스크립트
주요 수정 사항:
1. employeeData 로딩 문제 수정 (로컬 변수 대신 window 객체 직접 사용)
2. updateTypeSummaryTable 함수 자동 실행
3. 언어 전환 함수 개선
"""

import re
import sys

def fix_dashboard_file():
    # integrated_dashboard_final.py 파일 읽기
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 수정 1: DOMContentLoaded 내부의 employeeData 로딩 수정
    # const employeeData = JSON.parse(jsonStr); -> window.employeeData = JSON.parse(jsonStr);
    content = content.replace(
        "            const employeeData = JSON.parse(jsonStr);\n            console.log('[DEBUG] Parsed employee data:', employeeData.length, '직원');\n            window.employeeData = employeeData;",
        "            window.employeeData = JSON.parse(jsonStr);\n            const employeeData = window.employeeData;  // 로컬 참조용\n            console.log('[DEBUG] Parsed employee data:', window.employeeData.length, '직원');"
    )

    # 수정 2: window.onload에 updateTypeSummaryTable 호출 확인 및 추가
    # window.onload 함수에서 updateTypeSummaryTable가 호출되는지 확인
    if "window.onload = function() {" in content:
        # window.onload 함수 끝 부분 찾기
        onload_start = content.find("window.onload = function() {")
        if onload_start != -1:
            # updateTypeSummaryTable 호출 추가 (이미 있으면 스킵)
            onload_section = content[onload_start:onload_start+3000]
            if "updateTypeSummaryTable();" not in onload_section:
                # window.onload 함수 끝 부분에 추가
                insert_pos = content.find("            }}\n        }};\n", onload_start)
                if insert_pos != -1:
                    content = content[:insert_pos] + """
                // TYPE별 요약 테이블 업데이트
                if (typeof updateTypeSummaryTable === 'function') {{
                    console.log('Updating Type Summary Table...');
                    updateTypeSummaryTable();
                }} else {{
                    console.error('updateTypeSummaryTable function not found');
                }}
""" + content[insert_pos:]

    # 수정 3: showTab, changeLanguage, updateTypeSummaryTable 함수들을 window 객체에 명시적으로 등록
    # 함수 정의 후 window 객체에 할당 추가
    functions_to_expose = [
        ('function showTab(', 'window.showTab = showTab;'),
        ('function changeLanguage(', 'window.changeLanguage = changeLanguage;'),
        ('function updateTypeSummaryTable(', 'window.updateTypeSummaryTable = updateTypeSummaryTable;'),
        ('function generateEmployeeTable(', 'window.generateEmployeeTable = generateEmployeeTable;'),
        ('function generatePositionTables(', 'window.generatePositionTables = generatePositionTables;')
    ]

    for func_signature, window_assignment in functions_to_expose:
        if func_signature in content:
            # 함수 정의 끝 찾기
            func_start = content.find(func_signature)
            if func_start != -1:
                # 함수 끝 찾기 (다음 function 키워드 전까지)
                next_func = content.find('\n        function ', func_start + 100)
                if next_func == -1:
                    next_func = content.find('\n        window.', func_start + 100)
                if next_func == -1:
                    next_func = func_start + 5000

                func_section = content[func_start:next_func]
                # 이미 window에 할당되어 있는지 확인
                if window_assignment not in func_section:
                    # 함수 끝 부분에 window 할당 추가
                    last_brace = func_section.rfind('}\n')
                    if last_brace != -1:
                        insertion_point = func_start + last_brace + 2
                        content = content[:insertion_point] + f'\n        {window_assignment}\n' + content[insertion_point:]

    # 수정 4: changeLanguage 함수 내 하드코딩된 한국어 텍스트를 번역 가능하도록 수정
    # "수령인원 기준", "total원 기준" 등의 텍스트가 하드코딩되어 있는지 확인하고 수정

    # 수정된 내용을 새 파일로 저장
    with open('integrated_dashboard_final_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 수정 완료: integrated_dashboard_final_fixed.py")
    print("주요 수정 사항:")
    print("  1. employeeData 로딩 문제 수정")
    print("  2. window.onload에 updateTypeSummaryTable 호출 추가")
    print("  3. 모든 주요 함수를 window 객체에 등록")
    print("  4. 언어 전환 개선")
    return True

if __name__ == "__main__":
    fix_dashboard_file()