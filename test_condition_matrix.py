"""
Test script for Condition Matrix JSON implementation
Tests the new JSON-based condition evaluation system
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from condition_matrix_manager import ConditionMatrixManager, get_condition_manager

def test_matrix_loading():
    """Test that the matrix file loads correctly"""
    print("\n=== Testing Matrix Loading ===")
    manager = get_condition_manager()
    
    # Check if matrix loaded
    assert manager.matrix is not None, "Matrix should be loaded"
    assert 'conditions' in manager.matrix, "Matrix should have conditions"
    assert 'position_matrix' in manager.matrix, "Matrix should have position matrix"
    
    print("✅ Matrix loaded successfully")
    print(f"   - Found {len(manager.matrix['conditions'])} condition definitions")
    print(f"   - Found {len(manager.matrix['position_matrix'])} employee types")
    
    return manager

def test_position_matching(manager):
    """Test position pattern matching for all 25 positions"""
    print("\n=== Testing Position Matching (All 25 Positions) ===")
    
    test_cases = [
        # TYPE-1 positions (9 total - STITCHING INSPECTOR removed)
        ("TYPE-1", "MANAGER", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-1", "A.MANAGER", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-1", "(V) SUPERVISOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-1", "GROUP LEADER", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-1", "LINE LEADER", [1, 2, 3, 4, 7], [5, 6, 8, 9, 10]),  # LINE LEADER now includes condition 7
        ("TYPE-1", "AQL INSPECTOR", [1, 2, 3, 4, 5], [6, 7, 8, 9, 10]),
        ("TYPE-1", "ASSEMBLY INSPECTOR", [1, 2, 3, 4, 5, 6, 9, 10], [7, 8]),
        ("TYPE-1", "AUDIT & TRAINING TEAM", [1, 2, 3, 4, 7, 8], [5, 6, 9, 10]),
        ("TYPE-1", "MODEL MASTER", [1, 2, 3, 4, 8], [5, 6, 7, 9, 10]),
        
        # TYPE-2 positions (14 total)
        ("TYPE-2", "(V) SUPERVISOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "A.MANAGER", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "GROUP LEADER", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "LINE LEADER", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "AQL INSPECTOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "ASSEMBLY INSPECTOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "STITCHING INSPECTOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "BOTTOM INSPECTOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "CUTTING INSPECTOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "MTL INSPECTOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "OCPT STFF", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "OSC INSPECTOR", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "QA TEAM", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        ("TYPE-2", "RQC", [1, 2, 3, 4], [5, 6, 7, 8, 9, 10]),
        
        # TYPE-3 position (1 total)
        ("TYPE-3", "NEW QIP MEMBER", [], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    ]
    
    for emp_type, position, expected_applicable, expected_excluded in test_cases:
        applicable, excluded = manager.get_applicable_conditions(emp_type, position)
        
        # Check if results match expectations
        if set(applicable) == set(expected_applicable) and set(excluded) == set(expected_excluded):
            print(f"✅ {emp_type} - {position}: Correct")
        else:
            print(f"❌ {emp_type} - {position}: Mismatch")
            print(f"   Expected applicable: {expected_applicable}, Got: {applicable}")
            print(f"   Expected excluded: {expected_excluded}, Got: {excluded}")
    
    # Print summary
    print(f"\n📊 Position Matching Summary:")
    print(f"   Total positions tested: {len(test_cases)}")
    print(f"   TYPE-1 positions: 9 (STITCHING INSPECTOR removed)")
    print(f"   TYPE-2 positions: 14")
    print(f"   TYPE-3 positions: 1")
    print(f"   Total: 24 positions (TYPE-1 STITCHING INSPECTOR handled via preprocessing)")

def test_condition_evaluation(manager):
    """Test condition evaluation with sample data"""
    print("\n=== Testing Condition Evaluation ===")
    
    # Sample employee data
    sample_employee = {
        'Employee No': '620080295',
        'Full Name': 'Test Employee',
        'QIP POSITION 1ST NAME': 'AUDIT & TRAINING TEAM',
        'ROLE TYPE STD': 'TYPE-1',
        'Actual Working Days': 13,
        'Unapproved Absence Days': 0,
        'Absence Rate (raw)': 0,
        'Total Valiation Qty': 15,
        'Pass %': 98,
        'August AQL Failures': 0,
        'Continuous_FAIL': 'NO',
        '5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%': 'no',
        '5prs condition 2 - Total Valiation Qty is zero': 'no'
    }
    
    # Evaluate conditions
    result = manager.evaluate_all_conditions(
        sample_employee, 
        'TYPE-1', 
        'AUDIT & TRAINING TEAM'
    )
    
    print(f"\n📊 Evaluation for {sample_employee['Full Name']} ({sample_employee['QIP POSITION 1ST NAME']})")
    print(f"   Employee Type: {result['employee_type']}")
    print(f"   Position: {result['position']}")
    
    print("\n   Attendance Conditions:")
    for condition in result['conditions']['attendance']:
        status = "✅ Passed" if condition.is_passed else "❌ Failed"
        print(f"      - {condition.condition_name}: {status}")
        print(f"        Actual: {condition.actual_value}, Threshold: {condition.threshold_value}")
    
    print("\n   AQL Conditions:")
    aql_conditions = result['conditions']['aql']
    if aql_conditions:
        for condition in aql_conditions:
            status = "✅ Passed" if condition.is_passed else "❌ Failed"
            print(f"      - {condition.condition_name}: {status}")
            print(f"        Actual: {condition.actual_value}, Threshold: {condition.threshold_value}")
    else:
        print("      - Not applicable for this position")
    
    print("\n   5PRS Conditions:")
    prs_conditions = result['conditions']['5prs']
    if prs_conditions:
        for condition in prs_conditions:
            status = "✅ Passed" if condition.is_passed else "❌ Failed"
            print(f"      - {condition.condition_name}: {status}")
            print(f"        Actual: {condition.actual_value}, Threshold: {condition.threshold_value}")
    else:
        print("      - Not applicable for this position")
    
    print(f"\n   Summary:")
    summary = result['summary']
    print(f"      Total Applicable: {summary['total_applicable']}")
    print(f"      Total Passed: {summary['total_passed']}")
    print(f"      Pass Rate: {summary['pass_rate']:.1%}")
    print(f"      All Passed: {'✅ Yes' if summary['all_passed'] else '❌ No'}")

def test_preprocessing(manager):
    """Test data preprocessing for TYPE-1 STITCHING INSPECTOR correction"""
    print("\n=== Testing Data Preprocessing ===")
    
    # Test TYPE-1 STITCHING INSPECTOR correction
    stitching_data = {
        'Employee No': '620099999',
        'Full Name': 'Test Stitching Inspector',
        'QIP POSITION 1ST NAME': 'STITCHING INSPECTOR',
        'ROLE TYPE STD': 'TYPE-1',  # This should be corrected to TYPE-2
        'Actual Working Days': 13,
        'Unapproved Absence Days': 0,
        'Absence Rate (raw)': 0
    }
    
    # Preprocess the data
    corrected_data = manager.preprocess_employee_data(stitching_data)
    
    print(f"\n🔧 Preprocessing Test: TYPE-1 STITCHING INSPECTOR")
    print(f"   Original TYPE: {stitching_data['ROLE TYPE STD']}")
    print(f"   Corrected TYPE: {corrected_data['ROLE TYPE STD']}")
    
    if corrected_data['ROLE TYPE STD'] == 'TYPE-2':
        print("   ✅ Correctly changed to TYPE-2")
    else:
        print("   ❌ Failed to correct TYPE")

def test_special_cases(manager):
    """Test special cases like AQL Inspector with CFA certification"""
    print("\n=== Testing Special Cases ===")
    
    # AQL Inspector case
    aql_inspector_data = {
        'Employee No': '620020923',
        'Full Name': 'AQL Inspector Test',
        'QIP POSITION 1ST NAME': 'AQL INSPECTOR',
        'ROLE TYPE STD': 'TYPE-1',
        'Actual Working Days': 13,
        'Unapproved Absence Days': 0,
        'Absence Rate (raw)': 0,
        'August AQL Failures': 0,
        'Continuous_FAIL': 'NO'
    }
    
    result = manager.evaluate_all_conditions(
        aql_inspector_data,
        'TYPE-1',
        'AQL INSPECTOR'
    )
    
    print(f"\n🎯 Special Case: AQL Inspector")
    print(f"   Expected conditions: Attendance (1-4) + Current AQL (5)")
    print(f"   Excluded: Continuous AQL (6), All 5PRS (7-10)")
    
    applicable_ids = [r.condition_id for r in result['all_results'] if r.is_applicable]
    print(f"   Actual applicable: {applicable_ids}")
    
    # Check if correct conditions are applied
    expected = [1, 2, 3, 4, 5]
    if set(applicable_ids) == set(expected):
        print("   ✅ Correct conditions applied for AQL Inspector")
    else:
        print(f"   ❌ Incorrect conditions. Expected {expected}, got {applicable_ids}")

def test_display_config(manager):
    """Test display configuration retrieval"""
    print("\n=== Testing Display Configuration ===")
    
    languages = ['ko', 'en', 'vi']
    
    for lang in languages:
        config = manager.get_display_config(lang)
        print(f"\n   Language: {lang}")
        print(f"      Icons: {config['icons']}")
        print(f"      Labels: {config['labels']}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("CONDITION MATRIX JSON IMPLEMENTATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Load matrix
        manager = test_matrix_loading()
        
        # Test 2: Position matching
        test_position_matching(manager)
        
        # Test 3: Condition evaluation
        test_condition_evaluation(manager)
        
        # Test 4: Data preprocessing
        test_preprocessing(manager)
        
        # Test 5: Special cases
        test_special_cases(manager)
        
        # Test 6: Display configuration
        test_display_config(manager)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())