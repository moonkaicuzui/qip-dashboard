"""
Debug script to check metadata generation for TYPE-1 LINE LEADER
"""

import sys
import json
from pathlib import Path
import pandas as pd

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from condition_matrix_manager import get_condition_manager
from step2_dashboard_version4 import analyze_conditions_from_csv_row

def test_line_leader_metadata():
    """Test metadata generation for TYPE-1 LINE LEADER"""
    print("\n=== Testing TYPE-1 LINE LEADER Metadata ===")
    
    # Create sample LINE LEADER data (employee 619020468)
    sample_data = {
        'Employee No': 619020468,
        'Full Name': 'LINE LEADER Test',
        'QIP POSITION 1ST NAME': 'LINE LEADER',
        'ROLE TYPE STD': 'TYPE-1',
        'Actual Working Days': 17,
        'Unapproved Absence Days': 0,
        'Absence Rate (raw)': 0,
        'Total Valiation Qty': 0,
        'Pass %': 0,
        'August AQL Failures': 0,
        'Continuous_FAIL': 'NO',
        '5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%': 'yes',
        '5prs condition 2 - Total Valiation Qty is zero': 'yes'
    }
    
    # Convert to pandas Series (simulating CSV row)
    row = pd.Series(sample_data)
    
    # Analyze conditions
    print("\n1. Calling analyze_conditions_from_csv_row...")
    result = analyze_conditions_from_csv_row(row, 'TYPE-1', 'LINE LEADER', 'august')
    
    print("\n2. Result structure:")
    print(f"   - Has 'conditions': {'conditions' in result}")
    print(f"   - Has 'metadata': {'metadata' in result}")
    print(f"   - Has 'summary': {'summary' in result}")
    
    if 'metadata' in result and result['metadata']:
        metadata = result['metadata']
        print("\n3. Metadata content:")
        print(f"   - Position info: {metadata.get('position_info', {})}")
        print(f"   - Statistics: {metadata.get('statistics', {})}")
        
        print("\n4. Condition groups in metadata:")
        for group_key, group in metadata.get('condition_groups', {}).items():
            print(f"   - {group_key}: {group['name']}")
            print(f"     Applicable: {group['applicable_count']} conditions")
            if group['applicable_count'] > 0:
                print(f"     Conditions: {[c['id'] for c in group['conditions']]}")
    else:
        print("\n3. ❌ No metadata found in result!")
    
    print("\n5. Conditions returned:")
    conditions = result.get('conditions', {})
    for key, cond in conditions.items():
        if cond.get('applicable', False):
            print(f"   - {key}: applicable={cond['applicable']}, passed={cond.get('passed', 'N/A')}")
    
    print("\n6. Summary:")
    summary = result.get('summary', {})
    print(f"   - Total applicable: {summary.get('total_applicable', 0)}")
    print(f"   - Total passed: {summary.get('total_passed', 0)}")
    
    # Check what the manager returns directly
    print("\n7. Direct manager check:")
    manager = get_condition_manager()
    
    # Check applicable conditions
    applicable, excluded = manager.get_applicable_conditions('TYPE-1', 'LINE LEADER')
    print(f"   - Applicable conditions from matrix: {applicable}")
    print(f"   - Excluded conditions from matrix: {excluded}")
    
    # Check UI metadata
    ui_metadata = manager.get_ui_metadata('TYPE-1', 'LINE LEADER', 'ko')
    if ui_metadata:
        print("\n8. UI Metadata from manager:")
        for group_key, group in ui_metadata.get('condition_groups', {}).items():
            print(f"   - {group_key}: {group['applicable_count']} applicable conditions")
    
    return result

def test_json_serialization():
    """Test if metadata survives JSON serialization"""
    print("\n=== Testing JSON Serialization ===")
    
    result = test_line_leader_metadata()
    
    print("\n9. Testing JSON serialization:")
    try:
        # Simulate what happens in the dashboard generation
        emp_data = {
            'id': '619020468',
            'name': 'LINE LEADER Test',
            'position': 'LINE LEADER',
            'type': 'TYPE-1',
            'conditions': result.get('conditions', {}),
            'metadata': result.get('metadata', {}),
            'condition_summary': result.get('summary', {})
        }
        
        # Serialize
        json_str = json.dumps([emp_data], ensure_ascii=False, default=str)
        
        # Deserialize
        deserialized = json.loads(json_str)
        
        print(f"   - Original has metadata: {'metadata' in emp_data and emp_data['metadata']}")
        print(f"   - Serialized length: {len(json_str)} chars")
        print(f"   - Deserialized has metadata: {'metadata' in deserialized[0] and deserialized[0]['metadata']}")
        
        if 'metadata' in deserialized[0] and deserialized[0]['metadata']:
            metadata = deserialized[0]['metadata']
            print(f"   - Metadata preserved: ✅")
            print(f"   - Condition groups: {list(metadata.get('condition_groups', {}).keys())}")
        else:
            print(f"   - Metadata lost: ❌")
            
    except Exception as e:
        print(f"   - Serialization error: {e}")

if __name__ == "__main__":
    test_json_serialization()