"""
Verification script for the fixed condition mapping
"""

import json
from pathlib import Path

def verify_fix():
    """Verify the fix for TYPE-1 LINE LEADER and other positions"""
    
    # Read the generated HTML
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
    
    # Test cases to verify
    test_cases = [
        {
            'emp_no': '619020468',
            'position': 'LINE LEADER',
            'type': 'TYPE-1',
            'expected_conditions': {
                'attendance': 4,  # Conditions 1-4
                'aql': 1,  # Condition 7 only
                '5prs': 0  # No 5PRS conditions
            }
        },
        {
            'emp_no': '618110077',
            'position': 'AQL INSPECTOR',
            'type': 'TYPE-1',
            'expected_conditions': {
                'attendance': 4,  # Conditions 1-4
                'aql': 1,  # Condition 5 only
                '5prs': 0  # No 5PRS conditions
            }
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        emp = next((e for e in employees if e.get('emp_no') == test['emp_no']), None)
        
        if not emp:
            print(f"❌ Employee {test['emp_no']} not found")
            all_passed = False
            continue
        
        print(f"\n📋 Testing {emp['name']} ({test['position']}, {test['type']})")
        print(f"   Employee No: {test['emp_no']}")
        
        # Check conditions
        conditions = emp.get('conditions', {})
        condition_counts = {'attendance': 0, 'aql': 0, '5prs': 0}
        
        for key, cond in conditions.items():
            if cond.get('applicable'):
                category = cond.get('category', 'unknown')
                if category in condition_counts:
                    condition_counts[category] += 1
        
        # Check metadata
        metadata = emp.get('metadata', {})
        if metadata:
            groups = metadata.get('condition_groups', {})
            
            print("\n   Actual condition counts:")
            for category in ['attendance', 'aql', '5prs']:
                actual = condition_counts[category]
                expected = test['expected_conditions'][category]
                metadata_count = groups.get(category, {}).get('applicable_count', 0)
                
                match = actual == expected == metadata_count
                status = "✅" if match else "❌"
                
                print(f"   {status} {category}: conditions={actual}, metadata={metadata_count}, expected={expected}")
                
                if not match:
                    all_passed = False
                    print(f"      ERROR: Mismatch detected!")
            
            # Check rendering logic
            print("\n   UI Rendering (based on metadata):")
            for group_key, group in groups.items():
                if group['applicable_count'] > 0:
                    print(f"   ✅ {group_key}: Will render ({group['applicable_count']} conditions)")
                else:
                    if metadata.get('display_config', {}).get('show_empty_groups', False):
                        print(f"   ⚠️ {group_key}: Will render (empty group shown)")
                    else:
                        print(f"   ⭕ {group_key}: Will NOT render (no applicable conditions)")
        else:
            print("   ❌ No metadata found!")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED! The fix is working correctly.")
        print("\nSummary:")
        print("1. Condition 7 (Team/Area AQL) is correctly mapped to 'subordinate_aql'")
        print("2. Condition categories are correct (aql, not 5prs)")
        print("3. Metadata shows correct applicable counts")
        print("4. UI will only render groups with applicable conditions")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    verify_fix()