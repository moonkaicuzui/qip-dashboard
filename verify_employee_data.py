#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
employeeData JSON 구조 검증
"""
import re
import json
import base64

html_file = 'output_files/Incentive_Dashboard_2025_09_Version_6.html'

print('=' * 80)
print('employeeData JSON 구조 검증')
print('=' * 80)

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Base64 데이터 추출 - 더 넓은 패턴
base64_match = re.search(
    r'<script[^>]*id="employeeDataBase64"[^>]*>(.*?)</script>',
    html_content,
    re.DOTALL
)

if base64_match:
    try:
        base64_data = base64_match.group(1).strip()
        print(f'\n✅ Base64 데이터 발견 (길이: {len(base64_data)} bytes)')

        json_str = base64.b64decode(base64_data).decode('utf-8')
        employee_data = json.loads(json_str)

        print(f'✅ JSON 파싱 성공: {len(employee_data)}명 직원')

        if len(employee_data) > 0:
            # 첫 번째 직원 확인
            sample_emp = employee_data[0]
            print('\n📋 첫 번째 직원 데이터:')

            # 필드명 확인
            emp_no_fields = []
            if 'emp_no' in sample_emp:
                emp_no_fields.append('emp_no')
                print(f'   ✅ emp_no: {sample_emp["emp_no"]} (타입: {type(sample_emp["emp_no"]).__name__})')
            if 'Employee No' in sample_emp:
                emp_no_fields.append('Employee No')
                print(f'   ✅ Employee No: {sample_emp["Employee No"]} (타입: {type(sample_emp["Employee No"]).__name__})')

            if 'name' in sample_emp:
                print(f'   ✅ name: {sample_emp["name"]}')
            if 'Full Name' in sample_emp:
                print(f'   ✅ Full Name: {sample_emp["Full Name"]}')

            if 'position' in sample_emp:
                print(f'   ✅ position: {sample_emp["position"]}')
            if 'QIP POSITION 1ST NAME' in sample_emp:
                print(f'   ✅ QIP POSITION 1ST NAME: {sample_emp["QIP POSITION 1ST NAME"]}')

            if 'type' in sample_emp:
                print(f'   ✅ type: {sample_emp["type"]}')
            if 'ROLE TYPE STD' in sample_emp:
                print(f'   ✅ ROLE TYPE STD: {sample_emp["ROLE TYPE STD"]}')

            # 인센티브 필드
            if 'september_incentive' in sample_emp:
                print(f'   ✅ september_incentive: {sample_emp["september_incentive"]}')
            if 'august_incentive' in sample_emp:
                print(f'   ✅ august_incentive: {sample_emp["august_incentive"]}')

            # 타입 일관성 검사
            print('\n🔍 전체 직원 ID 타입 검사 (샘플 10명):')

            for field in emp_no_fields:
                type_counts = {}
                for i, emp in enumerate(employee_data[:10]):
                    if field in emp:
                        emp_id = emp[field]
                        type_name = type(emp_id).__name__
                        type_counts[type_name] = type_counts.get(type_name, 0) + 1

                print(f'\n   필드 "{field}": {type_counts}')

                if len(type_counts) > 1:
                    print(f'   ⚠️ 여러 타입이 섞여 있음 - String() 변환이 필수!')
                else:
                    print(f'   ✅ 타입이 일관됨')

            # 실제 매칭 테스트
            print('\n🧪 실제 find() 매칭 테스트:')
            test_emp_no = sample_emp.get('emp_no') or sample_emp.get('Employee No')

            if test_emp_no:
                print(f'   테스트 ID: {test_emp_no} (타입: {type(test_emp_no).__name__})')

                # 기존 방식 (타입 불일치 가능)
                old_match = None
                for e in employee_data[:5]:
                    if e.get('Employee No') == test_emp_no or e.get('emp_no') == test_emp_no:
                        old_match = e
                        break

                # 새로운 방식 (String 변환)
                empNoStr = str(test_emp_no)
                new_match = None
                for e in employee_data[:5]:
                    eEmpNo = str(e.get('Employee No') or e.get('emp_no') or e.get('emp_no') or '')
                    if eEmpNo == empNoStr:
                        new_match = e
                        break

                print(f'   기존 방식 매칭: {"✅ 성공" if old_match else "❌ 실패"}')
                print(f'   새 방식 매칭: {"✅ 성공" if new_match else "❌ 실패"}')

                if new_match and not old_match:
                    print('   💡 String 변환이 문제를 해결했습니다!')

            # 전체 필드 목록 (참고용)
            print('\n📚 사용 가능한 모든 필드:')
            all_keys = list(sample_emp.keys())
            print(f'   총 {len(all_keys)}개 필드')
            important_keys = [k for k in all_keys if any(x in k.upper() for x in ['EMP', 'NAME', 'POSITION', 'TYPE', 'INCENTIVE'])]
            print(f'   주요 필드: {important_keys[:15]}...')

    except Exception as e:
        print(f'❌ 처리 실패: {str(e)}')
        import traceback
        traceback.print_exc()
else:
    print('❌ employeeDataBase64 스크립트 태그를 찾을 수 없음')

print('\n' + '=' * 80)
print('검증 완료')
print('=' * 80)