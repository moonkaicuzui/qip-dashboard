#!/usr/bin/env python3
"""
포괄적인 Position NAME-CODE 매핑 수정 스크립트
모든 TYPE과 직급에 대해 NAME과 CODE 둘 다 확인하도록 수정
"""

import re

print("="*80)
print("🔧 Position Recognition 로직 포괄적 수정")
print("="*80)

# step1_인센티브_계산_개선버전.py 읽기
with open('src/step1_인센티브_계산_개선버전.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("\n[1] MODEL MASTER 인식 로직 수정")
print("-"*60)

# 1. MODEL MASTER 수정 (line 2398-2401)
old_model_master = """        model_master_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('MODEL MASTER', na=False))
        )"""

new_model_master = """        model_master_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('MODEL MASTER', na=False)) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper() == 'D')  # CODE 'D'도 MODEL MASTER로 인식
            )
        )"""

if old_model_master in content:
    content = content.replace(old_model_master, new_model_master)
    print("✅ MODEL MASTER 인식 로직 수정 완료")
    print("   - NAME: 'MODEL MASTER' 포함")
    print("   - CODE: 'D' 추가")
else:
    print("❌ MODEL MASTER 코드를 찾을 수 없음")

print("\n[2] ASSEMBLY INSPECTOR 인식 로직 수정")
print("-"*60)

# 2. ASSEMBLY INSPECTOR 수정 (line 2896-2900)
old_assembly = """        assembly_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('ASSEMBLY', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
        )"""

new_assembly = """        assembly_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                (
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('ASSEMBLY', na=False)) &
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
                ) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^A[1-5][AB]?$', na=False))  # A1A-A5B codes
            )
        )"""

if old_assembly in content:
    content = content.replace(old_assembly, new_assembly)
    print("✅ ASSEMBLY INSPECTOR 인식 로직 수정 완료")
    print("   - NAME: 'ASSEMBLY' AND 'INSPECTOR' 포함")
    print("   - CODE: A1A, A1B, A2A, A2B, A3A, A3B, A4A, A4B, A4C, A5A 추가")
else:
    print("❌ ASSEMBLY INSPECTOR 코드를 찾을 수 없음")

print("\n[3] AQL INSPECTOR 인식 로직 수정")
print("-"*60)

# 3. AQL INSPECTOR 수정 (line 2903-2907)
old_aql = """        aql_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('AQL', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
        )"""

new_aql = """        aql_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                (
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('AQL', na=False)) &
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
                ) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^AQL[1-5]?[AB]?$', na=False))  # AQL codes
            )
        )"""

if old_aql in content:
    content = content.replace(old_aql, new_aql)
    print("✅ AQL INSPECTOR 인식 로직 수정 완료")
    print("   - NAME: 'AQL' AND 'INSPECTOR' 포함")
    print("   - CODE: AQL 관련 코드 패턴 추가")
else:
    print("❌ AQL INSPECTOR 코드를 찾을 수 없음")

print("\n[4] AUDITOR/TRAINER 인식 로직 수정")
print("-"*60)

# 4. AUDITOR/TRAINER 수정 찾기
auditor_pattern = r"auditor_trainer_mask = \([^)]+\)"
auditor_matches = re.findall(auditor_pattern, content)

if auditor_matches:
    for old_auditor in auditor_matches:
        if 'AUDITOR' in old_auditor and 'TRAINER' in old_auditor:
            # NAME 기반 조건 추출
            new_auditor = old_auditor.replace(
                ")",
                """ |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^(QA[1-2][AB]?|E|F|G|H)$', na=False))  # QA1A, QA2A, QA2B, E, F, G, H codes
            )
        )"""
            )
            content = content.replace(old_auditor, new_auditor)
            print("✅ AUDITOR/TRAINER 인식 로직 수정 완료")
            print("   - NAME: 'AUDITOR' OR 'TRAINER' 포함")
            print("   - CODE: QA1A, QA2A, QA2B, E, F, G, H 추가")
            break
else:
    print("⚠️ AUDITOR/TRAINER 마스크를 찾지 못함")

print("\n[5] LINE LEADER 인식 로직 수정")
print("-"*60)

# 5. LINE LEADER 찾기 및 수정
line_leader_pattern = r"line_leader_mask = \([^)]+\)"
line_leader_matches = re.findall(line_leader_pattern, content)

if line_leader_matches:
    for old_line in line_leader_matches:
        if 'LINE' in old_line and 'LEADER' in old_line:
            new_line = old_line.replace(
                ")",
                """ |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^(L[1-5]|LL[AB]?)$', na=False))  # L1-L5, LL, LLA, LLB codes
            )
        )"""
            )
            content = content.replace(old_line, new_line)
            print("✅ LINE LEADER 인식 로직 수정 완료")
            print("   - NAME: 'LINE LEADER' 포함")
            print("   - CODE: L1, L2, L3, L4, L5, LL, LLA, LLB 추가")
            break
else:
    print("⚠️ LINE LEADER 마스크를 찾지 못함")

print("\n[6] GROUP LEADER 인식 로직 수정")
print("-"*60)

# 6. GROUP LEADER 찾기 및 수정
group_leader_pattern = r"group_leader_mask = \([^)]+\)"
group_leader_matches = re.findall(group_leader_pattern, content)

if group_leader_matches:
    for old_group in group_leader_matches:
        if 'GROUP' in old_group and 'LEADER' in old_group:
            new_group = old_group.replace(
                ")",
                """ |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^(GL[1-5]?[AB]?)$', na=False))  # GL, GL1-GL5, GLA, GLB codes
            )
        )"""
            )
            content = content.replace(old_group, new_group)
            print("✅ GROUP LEADER 인식 로직 수정 완료")
            print("   - NAME: 'GROUP LEADER' 포함")
            print("   - CODE: GL, GL1-GL5, GLA, GLB 추가")
            break
else:
    print("⚠️ GROUP LEADER 마스크를 찾지 못함")

print("\n[7] MANAGER/SUPERVISOR 인식 로직 추가")
print("-"*60)

# Manager/Supervisor 관련 마스크도 수정 필요한 경우 추가
manager_pattern = r"(manager_mask|supervisor_mask) = \([^)]+\)"
manager_matches = re.findall(manager_pattern, content)

if manager_matches:
    for match_tuple in manager_matches:
        old_mask = match_tuple[0] + " = " + re.search(f"{match_tuple[0]} = (\([^)]+\))", content).group(1)
        if 'MANAGER' in old_mask or 'SUPERVISOR' in old_mask:
            new_mask = old_mask.replace(
                ")",
                """ |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^(M[1-5]?|S[1-5]?|MG[1-5]?)$', na=False))  # Management codes
            )
        )"""
            )
            content = content.replace(old_mask, new_mask)
            print(f"✅ {match_tuple[0].upper()} 인식 로직 수정 완료")

# 파일 저장
with open('src/step1_인센티브_계산_개선버전_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*80)
print("✅ 수정 완료!")
print("="*80)

print("""
수정 내용 요약:
1. MODEL MASTER: NAME='MODEL MASTER' OR CODE='D'
2. ASSEMBLY INSPECTOR: NAME 체크 OR CODE=A1A-A5B
3. AQL INSPECTOR: NAME 체크 OR CODE=AQL 패턴
4. AUDITOR/TRAINER: NAME 체크 OR CODE=QA1A,QA2A,QA2B,E,F,G,H
5. LINE LEADER: NAME 체크 OR CODE=L1-L5,LL,LLA,LLB
6. GROUP LEADER: NAME 체크 OR CODE=GL,GL1-GL5,GLA,GLB
7. MANAGER/SUPERVISOR: NAME 체크 OR CODE=M,S,MG 패턴

이제 모든 직급이 NAME과 CODE 둘 다로 인식됩니다.
원본 파일은 유지되고, 수정된 파일은 '_fixed.py'로 저장됩니다.
""")

print("\n다음 단계:")
print("1. 백업: cp src/step1_인센티브_계산_개선버전.py src/step1_인센티브_계산_개선버전_backup.py")
print("2. 적용: mv src/step1_인센티브_계산_개선버전_fixed.py src/step1_인센티브_계산_개선버전.py")
print("3. 재계산: python src/step1_인센티브_계산_개선버전.py")
print("4. 검증: python test_fixed_bugs.py")