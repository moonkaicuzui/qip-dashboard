#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json

# Basic manpower 데이터 로드
df = pd.read_csv('input_files/basic manpower data september.csv', encoding='utf-8-sig')

print("="*80)
print("BASIC MANPOWER DATA ANALYSIS")
print("="*80)

# 칼럼 확인
print("\n칼럼 목록:")
print(df.columns.tolist())

print(f"\n전체 직원 수: {len(df)}")

# MST direct boss name과 direct boss name 분석
print("\n=== BOSS 관련 칼럼 분석 ===")

# MST direct boss name (Employee No)
mst_boss = df['MST direct boss name'].dropna()
print(f"\nMST direct boss name (Employee No) 샘플:")
print(mst_boss.head(10).tolist())

# direct boss name (이름)
boss_names = df['direct boss name'].dropna()
print(f"\ndirect boss name (이름) 샘플:")
print(boss_names.head(10).tolist())

# 상사가 없는 직원 찾기 (루트 노드)
no_boss = df[df['MST direct boss name'].isna() | (df['MST direct boss name'] == '')]
print(f"\n상사가 없는 직원 수: {len(no_boss)}")
if len(no_boss) > 0:
    print("상사가 없는 직원 목록:")
    for _, emp in no_boss.iterrows():
        print(f"  - {emp['Full Name']} ({emp['Employee No']}) - {emp['QIP POSITION 1ST  NAME']}")

# Manager 레벨 직원 찾기
managers = df[df['QIP POSITION 1ST  NAME'].str.contains('MANAGER', case=False, na=False)]
print(f"\n매니저 직급 직원 수: {len(managers)}")
print("매니저 목록:")
for _, mgr in managers.head(10).iterrows():
    boss_id = mgr['MST direct boss name']
    boss_name = mgr['direct boss name']
    print(f"  - {mgr['Full Name']} ({mgr['Employee No']}) - {mgr['QIP POSITION 1ST  NAME']}")
    print(f"    → Boss: {boss_name} ({boss_id})")

# 순환 참조 확인
print("\n=== 순환 참조 확인 ===")
boss_map = {}
for _, row in df.iterrows():
    emp_id = str(row['Employee No'])
    boss_id = str(row['MST direct boss name']) if pd.notna(row['MST direct boss name']) else None
    if boss_id:
        boss_map[emp_id] = boss_id

def find_cycle(emp_id, visited=None):
    if visited is None:
        visited = set()

    if emp_id in visited:
        return True, visited

    visited.add(emp_id)

    if emp_id in boss_map:
        boss_id = boss_map[emp_id]
        if boss_id and boss_id != 'nan':
            return find_cycle(boss_id, visited)

    return False, visited

cycles_found = []
for emp_id in boss_map.keys():
    has_cycle, path = find_cycle(emp_id, set())
    if has_cycle:
        cycles_found.append((emp_id, path))

if cycles_found:
    print(f"순환 참조 발견: {len(cycles_found)}개")
    for emp_id, path in cycles_found[:5]:
        print(f"  - Employee {emp_id}: {path}")
else:
    print("순환 참조 없음")

# 계층 구조 깊이 분석
print("\n=== 계층 구조 깊이 분석 ===")

def get_depth(emp_id, depth=0, max_depth=20):
    if depth > max_depth:
        return depth

    if emp_id not in boss_map:
        return depth

    boss_id = boss_map[emp_id]
    if not boss_id or boss_id == 'nan':
        return depth

    return get_depth(boss_id, depth + 1, max_depth)

depths = {}
for _, row in df.iterrows():
    emp_id = str(row['Employee No'])
    depth = get_depth(emp_id)
    depths[emp_id] = depth

max_depth = max(depths.values())
print(f"최대 계층 깊이: {max_depth}")

for d in range(max_depth + 1):
    count = sum(1 for v in depths.values() if v == d)
    print(f"  Level {d}: {count}명")

# 상사가 존재하는지 확인
print("\n=== 상사 존재 여부 확인 ===")
all_emp_ids = set(df['Employee No'].astype(str))
boss_not_in_list = []

for _, row in df.iterrows():
    boss_id = str(row['MST direct boss name']) if pd.notna(row['MST direct boss name']) else None
    if boss_id and boss_id != 'nan' and boss_id not in all_emp_ids:
        boss_not_in_list.append({
            'emp': row['Full Name'],
            'emp_id': row['Employee No'],
            'boss_id': boss_id,
            'boss_name': row['direct boss name']
        })

if boss_not_in_list:
    print(f"직원 목록에 없는 상사를 가진 직원: {len(boss_not_in_list)}명")
    for item in boss_not_in_list[:10]:
        print(f"  - {item['emp']} ({item['emp_id']}) → Boss: {item['boss_name']} ({item['boss_id']}) [NOT FOUND]")
else:
    print("모든 상사가 직원 목록에 존재함")

print("\n" + "="*80)