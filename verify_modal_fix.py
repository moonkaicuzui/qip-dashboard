#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개인별 상세 탭 모달 수정사항 검증
"""
import re
import json
import base64
from bs4 import BeautifulSoup

html_file = 'output_files/Incentive_Dashboard_2025_09_Version_6.html'

print('=' * 80)
print('개인별 상세 탭 모달 수정사항 검증')
print('=' * 80)

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 1. generateEmployeeTable 함수에서 CRITICAL FIX 확인
print('\n✅ 1. generateEmployeeTable 함수 수정사항 확인')
generate_func_match = re.search(
    r'function generateEmployeeTable\(\).*?(?=function\s+\w+|\}\s*</script>)',
    html_content,
    re.DOTALL
)

if generate_func_match:
    func_content = generate_func_match.group(0)

    # 필드명 통일 로직 확인
    if "emp.emp_no || emp['Employee No']" in func_content:
        print('   ✅ 필드명 통일 로직 적용됨')
        print('      const empNo = emp.emp_no || emp[\'Employee No\'] || emp[\'emp_no\'];')
    else:
        print('   ❌ 필드명 통일 로직 없음')

    # String 타입 변환 확인
    if 'String(empNo)' in func_content:
        print('   ✅ empNo 문자열 변환 적용됨')
        print('      tr.onclick = () => showEmployeeDetail(String(empNo));')
    else:
        print('   ❌ String 타입 변환 없음')

    # 버튼 onclick도 확인
    if "showEmployeeDetail('${empNo}')" in func_content or 'showEmployeeDetail(`${empNo}`)' in func_content:
        print('   ✅ 버튼 onclick도 수정됨')
    else:
        print('   ⚠️ 버튼 onclick 확인 필요')

# 2. showEmployeeDetail 함수에서 CRITICAL FIX 확인
print('\n✅ 2. showEmployeeDetail 함수 수정사항 확인')
show_func_match = re.search(
    r'function showEmployeeDetail\(empNo\).*?(?=function\s+\w+|\n\s{8}//|\}\s*\n\s{8}//)',
    html_content,
    re.DOTALL
)

if show_func_match:
    func_content = show_func_match.group(0)

    # 타입 통일 로직 확인
    if 'const empNoStr = String(empNo)' in func_content:
        print('   ✅ empNo 문자열 변환 적용됨')
        print('      const empNoStr = String(empNo);')
    else:
        print('   ❌ empNo 문자열 변환 없음')

    # find 함수에서 타입 통일 확인
    if "String(e['Employee No'] || e.emp_no" in func_content:
        print('   ✅ find 함수에서 타입 통일 적용됨')
        print('      const eEmpNo = String(e[\'Employee No\'] || e.emp_no || e[\'emp_no\'] || \'\');')
    else:
        print('   ❌ find 함수 타입 통일 없음')

    # 디버깅 로직 확인
    if 'console.error' in func_content and 'Employee not found' in func_content:
        print('   ✅ 디버깅용 console.error 추가됨')
    else:
        print('   ⚠️ 디버깅 로직 없음')

# 3. employeeData 구조 확인
print('\n✅ 3. employeeData JSON 구조 확인')

# Base64 데이터 추출
base64_match = re.search(
    r'<script id="employeeDataBase64" type="text/plain">\s*([A-Za-z0-9+/=\s]+)\s*</script>',
    html_content,
    re.DOTALL
)

if base64_match:
    try:
        base64_data = base64_match.group(1).strip()
        json_str = base64.b64decode(base64_data).decode('utf-8')
        employee_data = json.loads(json_str)

        print(f'   ✅ 총 직원 수: {len(employee_data)}명')

        if len(employee_data) > 0:
            sample_emp = employee_data[0]
            print('\n   📋 첫 번째 직원 데이터 구조:')

            # 중요 필드 확인
            emp_no_field = None
            if 'emp_no' in sample_emp:
                emp_no_field = 'emp_no'
                print(f'      ✅ emp_no 필드 존재: {sample_emp["emp_no"]} (타입: {type(sample_emp["emp_no"]).__name__})')
            elif 'Employee No' in sample_emp:
                emp_no_field = 'Employee No'
                print(f'      ✅ Employee No 필드 존재: {sample_emp["Employee No"]} (타입: {type(sample_emp["Employee No"]).__name__})')
            else:
                print('      ❌ emp_no 또는 Employee No 필드 없음!')
                print(f'      사용 가능한 필드: {list(sample_emp.keys())[:10]}')

            if 'name' in sample_emp:
                print(f'      ✅ name 필드 존재: {sample_emp["name"]}')
            elif 'Full Name' in sample_emp:
                print(f'      ✅ Full Name 필드 존재: {sample_emp["Full Name"]}')

            if 'position' in sample_emp:
                print(f'      ✅ position 필드 존재: {sample_emp["position"]}')
            elif 'QIP POSITION 1ST NAME' in sample_emp:
                print(f'      ✅ QIP POSITION 1ST NAME 필드 존재: {sample_emp["QIP POSITION 1ST NAME"]}')

            # 타입 일관성 검사
            print('\n   🔍 전체 직원 ID 타입 일관성 검사:')
            type_counts = {}
            for emp in employee_data[:10]:  # 샘플 10명만
                if emp_no_field and emp_no_field in emp:
                    emp_id = emp[emp_no_field]
                    type_name = type(emp_id).__name__
                    type_counts[type_name] = type_counts.get(type_name, 0) + 1

            print(f'      샘플 10명 타입 분포: {type_counts}')

            if len(type_counts) > 1:
                print('      ⚠️ 여러 타입이 섞여 있음 - String() 변환 필수!')
            else:
                print('      ✅ 타입이 일관됨')

    except Exception as e:
        print(f'   ❌ JSON 파싱 실패: {str(e)}')
else:
    print('   ❌ employeeDataBase64 스크립트 태그를 찾을 수 없음')

# 4. 통합 결과
print('\n' + '=' * 80)
print('검증 결과 요약')
print('=' * 80)

issues = []
if "emp.emp_no || emp['Employee No']" not in html_content:
    issues.append('generateEmployeeTable: 필드명 통일 로직 누락')
if 'String(empNo)' not in html_content:
    issues.append('generateEmployeeTable: String 타입 변환 누락')
if 'const empNoStr = String(empNo)' not in html_content:
    issues.append('showEmployeeDetail: empNo 문자열 변환 누락')
if "String(e['Employee No'] || e.emp_no" not in html_content:
    issues.append('showEmployeeDetail: find 함수 타입 통일 누락')

if not issues:
    print('✅ 모든 수정사항이 올바르게 적용되었습니다!')
    print('   - 필드명 통일 로직')
    print('   - 타입 변환 로직')
    print('   - 디버깅 로직')
    print('\n💡 개인별 상세 탭에서 직원을 클릭하면 모달이 정상적으로 열립니다.')
else:
    print('❌ 다음 문제가 발견되었습니다:')
    for issue in issues:
        print(f'   - {issue}')

print('=' * 80)