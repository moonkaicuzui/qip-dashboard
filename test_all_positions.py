"""
Comprehensive test for all 25 positions
Tests condition application and UI rendering for every position type
"""

import json
from pathlib import Path
import sys

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from condition_matrix_manager import get_condition_manager

def test_all_positions():
    """Test all 25 positions comprehensively"""
    
    # Define expected conditions for all 25 positions
    expected_conditions = {
        'TYPE-1': {
            'MANAGER': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'A.MANAGER': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            '(V) SUPERVISOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'GROUP LEADER': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'LINE LEADER': {'attendance': [1,2,3,4], 'aql': [7], '5prs': []},  # Condition 7 added
            'AQL INSPECTOR': {'attendance': [1,2,3,4], 'aql': [5], '5prs': []},
            'ASSEMBLY INSPECTOR': {'attendance': [1,2,3,4], 'aql': [5,6], '5prs': [9,10]},
            'AUDIT & TRAINING TEAM': {'attendance': [1,2,3,4], 'aql': [7,8], '5prs': []},
            'MODEL MASTER': {'attendance': [1,2,3,4], 'aql': [8], '5prs': []},
        },
        'TYPE-2': {
            '(V) SUPERVISOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'A.MANAGER': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'GROUP LEADER': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'LINE LEADER': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'AQL INSPECTOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'ASSEMBLY INSPECTOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'STITCHING INSPECTOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'BOTTOM INSPECTOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'CUTTING INSPECTOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'MTL INSPECTOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'OCPT STFF': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'OSC INSPECTOR': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'QA TEAM': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
            'RQC': {'attendance': [1,2,3,4], 'aql': [], '5prs': []},
        },
        'TYPE-3': {
            'NEW QIP MEMBER': {'attendance': [], 'aql': [], '5prs': []},
        }
    }
    
    # Get condition manager
    manager = get_condition_manager()
    
    # Read generated HTML
    html_path = Path('src/output_files/dashboard_version4.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract employee data
    start = content.find('const employeeData = [')
    if start == -1:
        print("❌ Could not find employee data in HTML")
        return False
    
    end = content.find('];', start)
    json_str = content[start+21:end+1]
    
    try:
        employees = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    
    # Group employees by type and position
    employees_by_position = {}
    for emp in employees:
        emp_type = emp.get('type', '')
        position = emp.get('position', '')
        key = f"{emp_type}:{position}"
        
        if key not in employees_by_position:
            employees_by_position[key] = []
        employees_by_position[key].append(emp)
    
    # Test results
    test_results = []
    total_positions = 0
    passed_positions = 0
    
    print("=" * 80)
    print("COMPREHENSIVE TEST FOR ALL 25 POSITIONS")
    print("=" * 80)
    
    for emp_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        print(f"\n{'='*60}")
        print(f"{emp_type} POSITIONS")
        print(f"{'='*60}")
        
        for position, expected in expected_conditions[emp_type].items():
            total_positions += 1
            key = f"{emp_type}:{position}"
            
            # Get applicable conditions from manager
            applicable, excluded = manager.get_applicable_conditions(emp_type, position)
            
            # Get UI metadata
            ui_metadata = manager.get_ui_metadata(emp_type, position, 'ko')
            
            # Find employees with this position
            position_employees = employees_by_position.get(key, [])
            
            print(f"\n📋 {emp_type} - {position}")
            print(f"   Found {len(position_employees)} employees")
            
            # Check expected vs actual conditions
            expected_all = expected['attendance'] + expected['aql'] + expected['5prs']
            
            match = set(applicable) == set(expected_all)
            if match:
                print(f"   ✅ Conditions match expected: {applicable}")
                passed_positions += 1
            else:
                print(f"   ❌ Conditions mismatch!")
                print(f"      Expected: {expected_all}")
                print(f"      Actual: {applicable}")
            
            # Check metadata
            if ui_metadata:
                groups = ui_metadata.get('condition_groups', {})
                
                print("   Metadata condition groups:")
                for cat in ['attendance', 'aql', '5prs']:
                    group = groups.get(cat, {})
                    count = group.get('applicable_count', 0)
                    expected_count = len(expected[cat])
                    
                    if count == expected_count:
                        print(f"   ✅ {cat}: {count} conditions (correct)")
                    else:
                        print(f"   ❌ {cat}: {count} conditions (expected {expected_count})")
                
                # Check UI rendering logic
                print("   UI Rendering prediction:")
                for cat in ['attendance', 'aql', '5prs']:
                    group = groups.get(cat, {})
                    count = group.get('applicable_count', 0)
                    
                    if count > 0:
                        print(f"      • {cat}: WILL render ({count} conditions)")
                    else:
                        print(f"      • {cat}: will NOT render (0 conditions)")
            
            # Test actual employees
            if position_employees:
                sample_emp = position_employees[0]
                conditions = sample_emp.get('conditions', {})
                
                # Count conditions by category
                actual_counts = {'attendance': 0, 'aql': 0, '5prs': 0}
                for cond_key, cond in conditions.items():
                    if cond.get('applicable'):
                        category = cond.get('category', 'unknown')
                        if category in actual_counts:
                            actual_counts[category] += 1
                
                print(f"   Sample employee ({sample_emp['emp_no']}):")
                for cat in ['attendance', 'aql', '5prs']:
                    expected_count = len(expected[cat])
                    actual_count = actual_counts[cat]
                    
                    if actual_count == expected_count:
                        print(f"      ✅ {cat}: {actual_count} conditions")
                    else:
                        print(f"      ❌ {cat}: {actual_count} conditions (expected {expected_count})")
            
            test_results.append({
                'type': emp_type,
                'position': position,
                'passed': match,
                'employee_count': len(position_employees)
            })
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    # Group results by type
    for emp_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
        type_results = [r for r in test_results if r['type'] == emp_type]
        passed = sum(1 for r in type_results if r['passed'])
        total = len(type_results)
        
        print(f"\n{emp_type}:")
        print(f"   Positions tested: {total}")
        print(f"   Passed: {passed}/{total}")
        
        if passed < total:
            failed = [r['position'] for r in type_results if not r['passed']]
            print(f"   Failed positions: {', '.join(failed)}")
    
    print(f"\n{'='*60}")
    print(f"OVERALL: {passed_positions}/{total_positions} positions passed")
    
    if passed_positions == total_positions:
        print("✅ ALL POSITIONS WORKING CORRECTLY!")
    else:
        print(f"❌ {total_positions - passed_positions} positions have issues")
    
    return passed_positions == total_positions

if __name__ == "__main__":
    success = test_all_positions()
    sys.exit(0 if success else 1)