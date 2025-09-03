#!/usr/bin/env python3
"""
Verify team and role mappings from team_structure_updated.json against actual employee data
"""

import pandas as pd
import json
from collections import defaultdict

def load_team_structure():
    """Load team structure from JSON"""
    with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_employee_data():
    """Load actual employee data from CSV"""
    csv_path = 'input_files/2025년 8월 인센티브 지급 세부 정보.csv'
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    # Rename columns for easier access
    df = df.rename(columns={
        'QIP POSITION 1ST  NAME': 'Position_1st',
        'QIP POSITION 2ND  NAME': 'Position_2nd',
        'QIP POSITION 3RD  NAME': 'Position_3rd',
        'Full Name': 'Name'
    })
    return df

def verify_mappings():
    """Verify all team-role mappings"""
    print("=" * 80)
    print("TEAM-ROLE MAPPING VERIFICATION")
    print("=" * 80)
    
    # Load data
    team_structure = load_team_structure()
    employees_df = load_employee_data()
    
    # Create mapping dictionaries
    position_to_team = {}
    position_to_role = {}
    
    for position in team_structure.get('positions', []):
        pos1 = position.get('position_1st', '')
        pos2 = position.get('position_2nd', '')
        pos3 = position.get('position_3rd', '')
        
        # Create combination key
        combo_key = f"{pos1}|{pos2}|{pos3}"
        
        position_to_team[combo_key] = position.get('team_name', 'unidentified')
        position_to_role[combo_key] = position.get('role_category', 'unidentified')
    
    # Track actual mappings
    team_role_count = defaultdict(lambda: defaultdict(int))
    unmapped_employees = []
    
    # Process each employee
    for _, row in employees_df.iterrows():
        pos1 = str(row.get('Position_1st', '')).strip()
        pos2 = str(row.get('Position_2nd', '')).strip()
        pos3 = str(row.get('Position_3rd', '')).strip()
        
        # Skip if no position data
        if not pos1 or pos1 == 'nan':
            continue
        
        # Create combination key
        combo_key = f"{pos1}|{pos2}|{pos3}"
        
        # Get team and role
        team = position_to_team.get(combo_key, 'UNIDENTIFIED')
        role = position_to_role.get(combo_key, 'unidentified')
        
        if team == 'UNIDENTIFIED':
            unmapped_employees.append({
                'name': row.get('Name', ''),
                'position': combo_key
            })
        else:
            team_role_count[team][role] += 1
    
    # Expected mappings from team_structure_updated.json
    expected_mappings = {
        'AQL': ['CFA', 'PACKING', 'REPORT'],
        'ASSEMBLY': ['TOP-MANAGEMENT', 'MID-MANAGEMENT', 'INSPECTOR', 'PO COMPLETION', 'SUPPORT', 'PACKING'],
        'BOTTOM': ['MID-MANAGEMENT', 'INSPECTOR', 'SUPPORT'],
        'CUTTING': ['TOP-MANAGEMENT', 'MID-MANAGEMENT', ''],
        'MTL': ['MID-MANAGEMENT', 'INSPECTOR'],
        'NEW': ['NEW'],
        'OFFICE & OCPT': ['TOP-MANAGEMENT', 'REPORT'],
        'OSC': ['TOP-MANAGEMENT', 'MID-MANAGEMENT', 'INSPECTOR'],
        'QA': ['TOP-MANAGEMENT', 'MID-MANAGEMENT', 'AUDITOR', 'REPORT'],
        'HWK QIP': ['TOP-MANAGEMENT'],
        'REPACKING': ['INSPECTOR', 'MID-MANAGEMENT', 'PACKING', 'SUPPORT'],
        'STITCHING': ['TOP-MANAGEMENT', 'MID-MANAGEMENT', 'INSPECTOR']
    }
    
    # Print verification results
    print("\n📊 TEAM-ROLE DISTRIBUTION (Actual vs Expected):")
    print("-" * 80)
    
    for team in sorted(team_role_count.keys()):
        print(f"\n🏢 {team} Team:")
        print(f"   Total: {sum(team_role_count[team].values())} employees")
        
        # Check expected roles
        expected_roles = expected_mappings.get(team, [])
        actual_roles = list(team_role_count[team].keys())
        
        print(f"   Expected roles: {', '.join(expected_roles) if expected_roles else 'None defined'}")
        print(f"   Actual roles found:")
        
        for role, count in sorted(team_role_count[team].items()):
            status = "✅" if role in expected_roles or not expected_roles else "⚠️"
            print(f"      {status} {role}: {count} employees")
        
        # Check for missing expected roles
        missing_roles = [r for r in expected_roles if r and r not in actual_roles]
        if missing_roles:
            print(f"   ❌ Missing expected roles: {', '.join(missing_roles)}")
    
    # Print unmapped employees
    if unmapped_employees:
        print(f"\n⚠️ UNMAPPED EMPLOYEES: {len(unmapped_employees)}")
        print("-" * 80)
        for i, emp in enumerate(unmapped_employees[:10], 1):
            print(f"   {i}. {emp['name']}: {emp['position']}")
        if len(unmapped_employees) > 10:
            print(f"   ... and {len(unmapped_employees) - 10} more")
    
    # Summary statistics
    print("\n📈 SUMMARY:")
    print("-" * 80)
    total_mapped = sum(sum(roles.values()) for roles in team_role_count.values())
    # Count non-empty position employees as active
    total_active = len(employees_df[employees_df['Position_1st'].notna()])
    print(f"   Total active employees: {total_active}")
    print(f"   Successfully mapped: {total_mapped} ({100*total_mapped/total_active:.1f}%)")
    print(f"   Unmapped: {len(unmapped_employees)} ({100*len(unmapped_employees)/total_active:.1f}%)")
    
    # Specific ASSEMBLY INSPECTOR analysis
    print("\n🔍 ASSEMBLY INSPECTOR ANALYSIS:")
    print("-" * 80)
    assembly_inspectors = employees_df[
        (employees_df['Position_1st'] == 'ASSEMBLY INSPECTOR')
    ]
    print(f"   Total ASSEMBLY INSPECTORs: {len(assembly_inspectors)}")
    
    # Count by team
    assembly_by_team = defaultdict(int)
    for _, row in assembly_inspectors.iterrows():
        pos1 = str(row.get('Position_1st', '')).strip()
        pos2 = str(row.get('Position_2nd', '')).strip()
        pos3 = str(row.get('Position_3rd', '')).strip()
        combo_key = f"{pos1}|{pos2}|{pos3}"
        team = position_to_team.get(combo_key, 'UNIDENTIFIED')
        assembly_by_team[team] += 1
    
    for team, count in sorted(assembly_by_team.items()):
        print(f"      → {team}: {count} employees")
    
    return team_role_count, unmapped_employees

if __name__ == "__main__":
    team_role_count, unmapped = verify_mappings()