#!/usr/bin/env python3
"""
Patch the team assignment logic to handle position conflicts correctly
This will update generate_management_dashboard_v6_enhanced.py to fix the ASSEMBLY count issue
"""

import re

# Read the current file
with open('generate_management_dashboard_v6_enhanced.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup the original
with open('generate_management_dashboard_v6_enhanced.py.backup', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Created backup: generate_management_dashboard_v6_enhanced.py.backup")

# Find and replace the problematic load_team_structure method
# The issue is that positions with multiple team assignments get overwritten

old_pattern = r'''(def load_team_structure\(self\):.*?)"positions"\]\):
                team_name = position_data\.get\('team_name', ''\)
                position_1st = position_data\.get\('position_1st', ''\)\.strip\(\)
                position_2nd = position_data\.get\('position_2nd', ''\)\.strip\(\)  
                position_3rd = position_data\.get\('position_3rd', ''\)\.strip\(\)
                role_category = position_data\.get\('role_category', ''\)
                
                # Position 조합 매핑
                combo_key = f"\{position_1st\}\|\{position_2nd\}\|\{position_3rd\}"
                self\.position_combo_to_team\[combo_key\] = team_name
                
                # 개별 position 매핑 \(ASSEMBLY INSPECTOR 제외 - 여러 팀에 속할 수 있음\)
                if position_1st and position_1st != 'ASSEMBLY INSPECTOR':
                    self\.position_to_team\[position_1st\] = team_name'''

# New logic that tracks conflicts and only uses unambiguous mappings
new_code = '''def load_team_structure(self):
        """팀 구조 데이터 로드"""
        self.position_to_team = {}
        self.position_combo_to_team = {}
        
        # Default mappings (simplified and corrected)
        self.position_to_team = {
            # Only include unambiguous position mappings
            'HWK QIP': 'HWK QIP',
            'CUTTING INSPECTOR': 'CUTTING',
            'OFFICE INSPECTOR': 'OFFICE & OCPT',
            # Remove conflicting positions like ASSEMBLY INSPECTOR, LINE LEADER, etc.
        }
        
        try:
            # Load from JSON file
            import json
            with open('HR info/team_structure_updated.json', 'r', encoding='utf-8') as f:
                team_structure = json.load(f)
            
            # Track position conflicts
            position_teams = {}  # position -> set of teams
            
            for position_data in team_structure.get('positions', []):
                team_name = position_data.get('team_name', '')
                position_1st = position_data.get('position_1st', '').strip()
                position_2nd = position_data.get('position_2nd', '').strip()  
                position_3rd = position_data.get('position_3rd', '').strip()
                role_category = position_data.get('role_category', '')
                
                # Position combo mapping (always accurate)
                combo_key = f"{position_1st}|{position_2nd}|{position_3rd}"
                self.position_combo_to_team[combo_key] = team_name
                
                # Track which teams each position_1st belongs to
                if position_1st:
                    if position_1st not in position_teams:
                        position_teams[position_1st] = set()
                    position_teams[position_1st].add(team_name)
            
            # Only add position mappings that are unambiguous (belong to only one team)
            for position, teams in position_teams.items():
                if len(teams) == 1:  # Unambiguous position
                    self.position_to_team[position] = list(teams)[0]
                # else: Skip positions with multiple teams (like ASSEMBLY INSPECTOR, LINE LEADER)
            
            print(f"  ✓ Team structure loaded")
            print(f"    - {len(self.position_combo_to_team)} position combinations")
            print(f"    - {len(self.position_to_team)} unambiguous positions")
            print(f"    - {len([p for p, t in position_teams.items() if len(t) > 1])} conflicting positions skipped")
            
        except FileNotFoundError:
            print(f"  ⚠ Team structure file not found, using defaults")
        except Exception as e:
            print(f"  ❌ Error loading team structure: {e}")'''

print("\nApplying patch...")

# Check if we can find the method to replace
if 'def load_team_structure(self):' in content:
    # Find the full method and replace it
    import re
    
    # Pattern to match the entire load_team_structure method
    pattern = r'def load_team_structure\(self\):.*?(?=\n    def |\n\nclass |\Z)'
    
    # Find the method
    match = re.search(pattern, content, re.DOTALL)
    if match:
        old_method = match.group()
        
        # Replace with new method
        content = content.replace(old_method, new_code)
        
        # Save the patched file
        with open('generate_management_dashboard_v6_enhanced.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully patched generate_management_dashboard_v6_enhanced.py")
        print("\nThe fix:")
        print("1. Now tracks position conflicts (positions assigned to multiple teams)")
        print("2. Only uses unambiguous positions in simple mapping")
        print("3. Relies on combo mapping for accurate team assignment")
        print("\nThis should fix the ASSEMBLY count to be 109 instead of 120.")
    else:
        print("❌ Could not find the load_team_structure method pattern")
else:
    print("❌ Could not find load_team_structure method")

print("\nTo apply the fix, run:")
print("python generate_management_dashboard_v6_enhanced.py --month 8 --year 2025")