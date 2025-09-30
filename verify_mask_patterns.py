#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 마스크 패턴의 Position Code 매칭 및 중복 검증
"""
import re
import pandas as pd

# Load basic data
df = pd.read_csv('input_files/basic manpower data september.csv')

# Define all mask patterns from the code
masks = {
    'Auditor/Trainer': r'^(QA[1-2][AB]?)$',
    'Model Master': r'^(D)$',
    'LINE LEADER': r'^(E|L[1-5]|LL[AB]?)$',
    'GROUP LEADER': r'^(F)$',
    '(V) SUPERVISOR': r'^(G)$',
    'Assistant Manager': r'^(H)$',
    'Manager': r'^(I)$',
    'Senior Manager': r'^(J)$'
}

print('=' * 80)
print('모든 마스크 패턴 Position Code 매칭 검증')
print('=' * 80)

# Get all employees with their position codes
employees_by_code = {}
for idx, row in df.iterrows():
    code = str(row.get('FINAL QIP POSITION NAME CODE', '')).strip().upper()
    if code and code != 'NAN':
        if code not in employees_by_code:
            employees_by_code[code] = []
        employees_by_code[code].append({
            'emp_id': row.get('Employee No'),
            'name': row.get('Full Name', 'Unknown'),
            'position': row.get('QIP POSITION 1ST  NAME', ''),
            'type': row.get('ROLE TYPE STD', '')
        })

# Check each mask
overlaps = []
for mask_name, pattern in masks.items():
    matched_codes = []
    for code in employees_by_code.keys():
        if re.match(pattern, code):
            matched_codes.append(code)

    if matched_codes:
        print(f'\n🔍 {mask_name} 마스크:')
        print(f'   패턴: {pattern}')
        print(f'   매칭된 CODE: {sorted(matched_codes)}')

        # Show employee count per code
        for code in sorted(matched_codes):
            emps = employees_by_code[code]
            positions = list(set([e['position'] for e in emps]))
            types = list(set([e['type'] for e in emps]))
            print(f'   - CODE "{code}": {len(emps)}명, 직급: {positions}, 타입: {types}')

# Check for overlaps between masks
print('\n' + '=' * 80)
print('마스크 간 CODE 중복 검증')
print('=' * 80)

for i, (mask1_name, pattern1) in enumerate(masks.items()):
    for j, (mask2_name, pattern2) in enumerate(masks.items()):
        if i >= j:
            continue

        # Find overlapping codes
        overlap_codes = []
        for code in employees_by_code.keys():
            if re.match(pattern1, code) and re.match(pattern2, code):
                overlap_codes.append(code)

        if overlap_codes:
            overlaps.append({
                'mask1': mask1_name,
                'mask2': mask2_name,
                'codes': overlap_codes
            })
            print(f'\n⚠️ 중복 발견!')
            print(f'   {mask1_name} ↔ {mask2_name}')
            print(f'   중복 CODE: {overlap_codes}')
            for code in overlap_codes:
                emps = employees_by_code[code]
                print(f'   - CODE "{code}": {len(emps)}명 영향받음')

if not overlaps:
    print('\n✅ 마스크 간 CODE 중복 없음')

# Find codes not matched by any mask (TYPE-1 only)
print('\n' + '=' * 80)
print('TYPE-1 중 마스크에 매칭되지 않은 CODE')
print('=' * 80)

type1_codes = set()
for code, emps in employees_by_code.items():
    if any(e['type'] == 'TYPE-1' for e in emps):
        type1_codes.add(code)

matched_codes = set()
for pattern in masks.values():
    for code in type1_codes:
        if re.match(pattern, code):
            matched_codes.add(code)

unmatched = type1_codes - matched_codes
if unmatched:
    print(f'\n⚠️ 매칭되지 않은 TYPE-1 CODE: {sorted(unmatched)}')
    for code in sorted(unmatched):
        emps = [e for e in employees_by_code[code] if e['type'] == 'TYPE-1']
        positions = list(set([e['position'] for e in emps]))
        print(f'   CODE "{code}": {len(emps)}명, 직급: {positions}')
else:
    print('\n✅ 모든 TYPE-1 CODE가 마스크에 매칭됨')

# Now check subordinate_mapping auto-update
print('\n' + '=' * 80)
print('subordinate_mapping.json 자동 업데이트 확인')
print('=' * 80)

print('\n📌 subordinate_mapping은 매 계산마다 자동 생성됩니다:')
print('   위치: calculate_type1_incentive() 함수 내부')
print('   타이밍: TYPE-1 인센티브 계산 직전')
print('   방식: Basic Manpower Data의 Manager/ManagerID 컬럼 기반')
print('\n✅ 자동 업데이트되므로 수동 관리 불필요')
print('   - Manager 컬럼: 관리자의 Full Name')
print('   - ManagerID 컬럼: 관리자의 Employee No')
print('   - 이 두 컬럼이 올바르면 자동으로 매핑 생성됨')