#!/usr/bin/env python3
"""
Fix unmapped positions by adding missing mappings to team_structure_updated.json
"""

import pandas as pd
import json

def analyze_unmapped():
    """Analyze unmapped employees to find patterns"""
    
    # Load employee data
    csv_path = 'input_files/2025년 8월 인센티브 지급 세부 정보.csv'
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # Load current team structure
    with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
        team_structure = json.load(f)
    
    # Create current mapping set
    existing_mappings = set()
    for position in team_structure.get('positions', []):
        pos1 = position.get('position_1st', '')
        pos2 = position.get('position_2nd', '')
        pos3 = position.get('position_3rd', '')
        combo_key = f"{pos1}|{pos2}|{pos3}"
        existing_mappings.add(combo_key)
    
    # Find unmapped positions
    unmapped_positions = []
    
    for _, row in df.iterrows():
        pos1 = str(row.get('QIP POSITION 1ST  NAME', '')).strip()
        pos2 = str(row.get('QIP POSITION 2ND  NAME', '')).strip()
        pos3 = str(row.get('QIP POSITION 3RD  NAME', '')).strip()
        
        if not pos1 or pos1 == 'nan':
            continue
            
        combo_key = f"{pos1}|{pos2}|{pos3}"
        
        if combo_key not in existing_mappings:
            unmapped_positions.append({
                'position_1st': pos1,
                'position_2nd': pos2,
                'position_3rd': pos3,
                'combo_key': combo_key,
                'name': row.get('Full Name', ''),
                'building': row.get('BUILDING', ''),
                'role_type': row.get('ROLE TYPE STD', '')
            })
    
    # Group unmapped by pattern
    print("\n📋 UNMAPPED POSITION PATTERNS:")
    print("-" * 80)
    
    position_patterns = {}
    for unmapped in unmapped_positions:
        key = unmapped['combo_key']
        if key not in position_patterns:
            position_patterns[key] = {
                'count': 0,
                'example': unmapped,
                'names': []
            }
        position_patterns[key]['count'] += 1
        position_patterns[key]['names'].append(unmapped['name'])
    
    # Sort by frequency
    sorted_patterns = sorted(position_patterns.items(), key=lambda x: x[1]['count'], reverse=True)
    
    # Print top unmapped patterns
    new_mappings = []
    for i, (pattern, info) in enumerate(sorted_patterns[:20], 1):
        print(f"\n{i}. Pattern: {pattern}")
        print(f"   Count: {info['count']} employees")
        print(f"   Example: {info['example']['name']}")
        print(f"   Building: {info['example']['building']}")
        print(f"   Role Type: {info['example']['role_type']}")
        
        # Suggest mapping based on pattern analysis
        pos1 = info['example']['position_1st']
        pos2 = info['example']['position_2nd']
        pos3 = info['example']['position_3rd']
        building = info['example']['building']
        role_type = info['example']['role_type']
        
        # Determine team and role based on position and building
        team_name = "UNIDENTIFIED"
        role_category = "unidentified"
        
        # Use building info and position patterns to determine team
        if building and str(building) != 'nan' and isinstance(building, str):
            if 'ASSEMBLY' in building.upper():
                team_name = "ASSEMBLY"
            elif 'STITCHING' in building.upper():
                team_name = "STITCHING"
            elif 'CUTTING' in building.upper():
                team_name = "CUTTING"
            elif 'BOTTOM' in building.upper():
                team_name = "BOTTOM"
        
        # Fallback to position-based detection
        if team_name == "UNIDENTIFIED":
            if 'NEW QIP MEMBER' in pos1.upper():
                team_name = "NEW"
                role_category = "NEW"
            elif 'ASSEMBLY' in pos1.upper():
                team_name = "ASSEMBLY"
            elif 'STITCHING' in pos1.upper():
                team_name = "STITCHING"
            elif 'MTL' in pos2.upper():
                team_name = "MTL"
            elif 'CUTTING' in pos1.upper():
                team_name = "CUTTING"
        
        # Determine role category (skip if already set for NEW)
        if role_category == "unidentified":
            if 'MANAGER' in pos1.upper():
                role_category = "TOP-MANAGEMENT"
            elif 'SUPERVISOR' in pos1.upper():
                role_category = "TOP-MANAGEMENT"
            elif 'GROUP LEADER' in pos1.upper():
                role_category = "MID-MANAGEMENT"
            elif 'LINE LEADER' in pos1.upper():
                role_category = "MID-MANAGEMENT"
            elif 'INSPECTOR' in pos1.upper():
                role_category = "INSPECTOR"
        
        print(f"   → Suggested: Team={team_name}, Role={role_category}")
        
        # Add to new mappings
        new_mappings.append({
            "position_1st": pos1,
            "position_2nd": pos2,
            "position_3rd": pos3,
            "final_code": f"AUTO_{i}",
            "team_name": team_name,
            "role_category": role_category,
            "role_type": role_type if role_type and role_type != 'nan' else "TYPE-2"
        })
    
    return new_mappings, team_structure

def update_team_structure(new_mappings, team_structure):
    """Add new mappings to team_structure"""
    
    # Add new mappings
    for mapping in new_mappings:
        # Check if already exists (with slight variations)
        exists = False
        for existing in team_structure['positions']:
            # Normalize for comparison (remove extra spaces)
            existing_key = f"{existing['position_1st']}|{existing['position_2nd']}|{existing['position_3rd']}"
            new_key = f"{mapping['position_1st']}|{mapping['position_2nd']}|{mapping['position_3rd']}"
            
            # Also check with normalized spaces
            existing_normalized = existing_key.replace(' ( ', '(').replace(' )', ')').replace('  ', ' ')
            new_normalized = new_key.replace(' ( ', '(').replace(' )', ')').replace('  ', ' ')
            
            if existing_normalized == new_normalized:
                exists = True
                break
        
        if not exists and mapping['team_name'] != "UNIDENTIFIED":
            team_structure['positions'].append(mapping)
            print(f"\n✅ Added mapping: {mapping['position_1st']} → {mapping['team_name']}/{mapping['role_category']}")
    
    return team_structure

if __name__ == "__main__":
    print("=" * 80)
    print("ANALYZING UNMAPPED POSITIONS")
    print("=" * 80)
    
    new_mappings, team_structure = analyze_unmapped()
    
    print("\n" + "=" * 80)
    print(f"Found {len(new_mappings)} new mapping patterns to add")
    
    # Ask for confirmation
    response = input("\nAdd these mappings to team_structure_updated.json? (y/n): ")
    
    if response.lower() == 'y':
        updated_structure = update_team_structure(new_mappings, team_structure)
        
        # Save updated structure
        with open('HR info/team_structure_updated.json', 'w', encoding='utf-8') as f:
            json.dump(updated_structure, f, ensure_ascii=False, indent=2)
        
        print("\n✅ team_structure_updated.json has been updated!")
    else:
        print("\n❌ No changes made.")