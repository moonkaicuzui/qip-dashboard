"""
Condition Matrix Manager for QIP Incentive System
Centralizes condition application logic using JSON configuration
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConditionResult:
    """Result of condition evaluation"""
    condition_id: int
    condition_name: str
    is_applicable: bool
    is_passed: Optional[bool]
    actual_value: Any = None
    threshold_value: Any = None
    message: str = ""


class ConditionMatrixManager:
    """
    Manages position-based condition application using JSON matrix
    """
    
    def __init__(self, matrix_path: str = None):
        """
        Initialize the Condition Matrix Manager
        
        Args:
            matrix_path: Path to the JSON matrix file
        """
        if matrix_path is None:
            matrix_path = Path(__file__).parent.parent / "config_files" / "position_condition_matrix.json"
        
        self.matrix_path = Path(matrix_path)
        self.matrix = self._load_matrix()
        self._build_pattern_cache()
    
    def _load_matrix(self) -> Dict:
        """Load the condition matrix from JSON file"""
        try:
            with open(self.matrix_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Matrix file not found: {self.matrix_path}")
            return self._get_default_matrix()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in matrix file: {e}")
            return self._get_default_matrix()
    
    def _get_default_matrix(self) -> Dict:
        """Return a minimal default matrix if file not found"""
        return {
            "conditions": {},
            "position_matrix": {
                "TYPE-1": {"default": {"applicable_conditions": [1,2,3,4], "excluded_conditions": [5,6,7,8,9,10]}},
                "TYPE-2": {"default": {"applicable_conditions": [1,2,3,4,9,10], "excluded_conditions": [5,6,7,8]}},
                "TYPE-3": {"default": {"applicable_conditions": [1,2,3,4], "excluded_conditions": [5,6,7,8,9,10]}}
            }
        }
    
    def _build_pattern_cache(self):
        """Build regex patterns for position matching"""
        self.pattern_cache = {}
        
        for type_key, type_positions in self.matrix.get('position_matrix', {}).items():
            self.pattern_cache[type_key] = {}
            
            for pos_key, pos_config in type_positions.items():
                if pos_key == 'default':
                    continue
                    
                patterns = pos_config.get('patterns', [])
                if patterns:
                    # Create a regex pattern that matches any of the patterns
                    pattern_str = '|'.join([re.escape(p) for p in patterns])
                    self.pattern_cache[type_key][pos_key] = re.compile(pattern_str, re.IGNORECASE)
    
    def get_applicable_conditions(self, employee_type: str, position: str) -> Tuple[List[int], List[int]]:
        """
        Get applicable and excluded conditions for a given position
        
        Args:
            employee_type: Employee type (TYPE-1, TYPE-2, TYPE-3)
            position: Employee position/role
            
        Returns:
            Tuple of (applicable_conditions, excluded_conditions)
        """
        # Normalize employee type
        employee_type = employee_type.upper().replace(' ', '-')
        if not employee_type.startswith('TYPE'):
            employee_type = f'TYPE-{employee_type}'
        
        # Get type configuration
        type_config = self.matrix.get('position_matrix', {}).get(employee_type, {})
        
        # Try to match specific position
        matched_config = None
        for pos_key, pattern in self.pattern_cache.get(employee_type, {}).items():
            if pattern.search(position):
                matched_config = type_config.get(pos_key)
                logger.info(f"Matched position '{position}' to pattern '{pos_key}'")
                break
        
        # Fall back to default if no match
        if not matched_config:
            matched_config = type_config.get('default', {})
            logger.info(f"Using default config for {employee_type}")
        
        applicable = matched_config.get('applicable_conditions', [])
        excluded = matched_config.get('excluded_conditions', [])
        
        return applicable, excluded
    
    def is_condition_applicable(self, condition_id: int, employee_type: str, position: str) -> bool:
        """
        Check if a specific condition is applicable to a position
        
        Args:
            condition_id: Condition ID to check
            employee_type: Employee type
            position: Employee position
            
        Returns:
            True if condition is applicable
        """
        applicable, excluded = self.get_applicable_conditions(employee_type, position)
        return condition_id in applicable
    
    def evaluate_attendance_conditions(self, employee_data: Dict, employee_type: str, position: str) -> List[ConditionResult]:
        """
        Evaluate attendance conditions for an employee
        
        Args:
            employee_data: Dictionary containing employee attendance data
            employee_type: Employee type
            position: Employee position
            
        Returns:
            List of condition evaluation results
        """
        results = []
        applicable, _ = self.get_applicable_conditions(employee_type, position)
        
        # Condition 1: Attendance rate >= 88%
        if 1 in applicable:
            # Calculate attendance rate (100% - absence rate)
            absence_rate = employee_data.get('결근율_Absence_Rate_Percent', 0)
            if absence_rate > 1:  # If given as percentage (e.g., 12 instead of 0.12)
                absence_rate = absence_rate / 100
            attendance_rate = 1 - absence_rate
            
            threshold = self.matrix.get('validation_rules', {}).get('attendance', {}).get('attendance_rate_threshold', 0.88)
            result = ConditionResult(
                condition_id=1,
                condition_name="Attendance Rate >= 88%",
                is_applicable=True,
                is_passed=attendance_rate >= threshold,
                actual_value=attendance_rate,
                threshold_value=threshold,
                message=f"Attendance rate: {attendance_rate:.1%}"
            )
            results.append(result)
        
        # Condition 2: Unapproved absence <= 2 days
        if 2 in applicable:
            unapproved_absence = employee_data.get('Unapproved Absence Days', 0)
            threshold = self.matrix.get('validation_rules', {}).get('attendance', {}).get('unapproved_absence_threshold', 2)
            result = ConditionResult(
                condition_id=2,
                condition_name="Unapproved Absence <= 2 days",
                is_applicable=True,
                is_passed=unapproved_absence <= threshold,
                actual_value=unapproved_absence,
                threshold_value=threshold,
                message=f"Unapproved absence: {unapproved_absence} days"
            )
            results.append(result)
        
        # Condition 3: Actual working days > 0
        if 3 in applicable:
            actual_days = employee_data.get('Actual Working Days', 0)
            threshold = self.matrix.get('validation_rules', {}).get('attendance', {}).get('minimum_actual_days', 0)
            result = ConditionResult(
                condition_id=3,
                condition_name="Actual Working Days > 0",
                is_applicable=True,
                is_passed=actual_days > threshold,
                actual_value=actual_days,
                threshold_value=threshold,
                message=f"Actual working days: {actual_days}"
            )
            results.append(result)
        
        # Condition 4: Minimum working days >= 12
        if 4 in applicable:
            actual_days = employee_data.get('Actual Working Days', 0)
            threshold = self.matrix.get('validation_rules', {}).get('attendance', {}).get('minimum_days_threshold', 12)
            result = ConditionResult(
                condition_id=4,
                condition_name="Minimum Working Days >= 12",
                is_applicable=True,
                is_passed=actual_days >= threshold,
                actual_value=actual_days,
                threshold_value=threshold,
                message=f"Working days: {actual_days}/{threshold}"
            )
            results.append(result)
        
        return results
    
    def evaluate_aql_conditions(self, employee_data: Dict, employee_type: str, position: str) -> List[ConditionResult]:
        """
        Evaluate AQL conditions for an employee
        
        Args:
            employee_data: Dictionary containing employee AQL data
            employee_type: Employee type
            position: Employee position
            
        Returns:
            List of condition evaluation results
        """
        results = []
        applicable, _ = self.get_applicable_conditions(employee_type, position)
        
        # Condition 5: Personal AQL - Current month failures = 0
        if 5 in applicable:
            # Try different column names for current month AQL failures
            aql_failures = employee_data.get('August AQL Failures', 
                          employee_data.get('July AQL Failures',
                          employee_data.get('Current Month AQL Failures', 0)))
            threshold = self.matrix.get('validation_rules', {}).get('aql', {}).get('personal_failure_threshold', 0)
            result = ConditionResult(
                condition_id=5,
                condition_name="Personal AQL: Current Month Failures = 0",
                is_applicable=True,
                is_passed=aql_failures == threshold,
                actual_value=aql_failures,
                threshold_value=threshold,
                message=f"Personal AQL failures: {aql_failures}"
            )
            results.append(result)
        
        # Condition 6: Personal AQL - No 3-month consecutive failures
        if 6 in applicable:
            continuous_fail = employee_data.get('Continuous_FAIL', 'NO')
            result = ConditionResult(
                condition_id=6,
                condition_name="Personal AQL: No 3-month Consecutive Failures",
                is_applicable=True,
                is_passed=continuous_fail != 'YES',
                actual_value=continuous_fail,
                threshold_value='NO',
                message=f"3-month consecutive failure: {continuous_fail}"
            )
            results.append(result)
        
        # Condition 7: Team/Area AQL - No 3-month consecutive failures
        if 7 in applicable:
            # This would need team/area data which may not be in individual employee data
            team_area_fail = employee_data.get('Team_Area_Consecutive_Fail', 
                            employee_data.get('BUILDING', 'NO'))
            result = ConditionResult(
                condition_id=7,
                condition_name="Team/Area AQL: No 3-month Consecutive Failures",
                is_applicable=True,
                is_passed=team_area_fail != 'YES',
                actual_value=team_area_fail,
                threshold_value='NO',
                message=f"Team/Area consecutive failure: {team_area_fail}"
            )
            results.append(result)
        
        # Condition 8: Area reject rate < 3%
        if 8 in applicable:
            # Area reject rate might be a calculated field or from separate data
            area_reject_rate = employee_data.get('Area_Reject_Rate', 
                              employee_data.get('Rejection_Rate', 0))
            if area_reject_rate > 1:  # If given as percentage
                area_reject_rate = area_reject_rate / 100
            threshold = self.matrix.get('validation_rules', {}).get('aql', {}).get('area_reject_threshold', 0.03)
            result = ConditionResult(
                condition_id=8,
                condition_name="Area Reject Rate < 3%",
                is_applicable=True,
                is_passed=area_reject_rate < threshold,
                actual_value=area_reject_rate,
                threshold_value=threshold,
                message=f"Area reject rate: {area_reject_rate:.1%}"
            )
            results.append(result)
        
        return results
    
    def evaluate_5prs_conditions(self, employee_data: Dict, employee_type: str, position: str) -> List[ConditionResult]:
        """
        Evaluate 5PRS conditions for an employee
        
        Args:
            employee_data: Dictionary containing employee 5PRS data
            employee_type: Employee type
            position: Employee position
            
        Returns:
            List of condition evaluation results
        """
        results = []
        applicable, _ = self.get_applicable_conditions(employee_type, position)
        
        # Condition 9: 5PRS pass rate >= 95%
        if 9 in applicable:
            pass_rate = employee_data.get('Pass %', 0)
            if pass_rate > 1:  # If given as percentage (e.g., 95 instead of 0.95)
                pass_rate = pass_rate / 100
            threshold = self.matrix.get('validation_rules', {}).get('5prs', {}).get('pass_rate_threshold', 0.95)
            result = ConditionResult(
                condition_id=9,
                condition_name="5PRS Pass Rate >= 95%",
                is_applicable=True,
                is_passed=pass_rate >= threshold,
                actual_value=pass_rate,
                threshold_value=threshold,
                message=f"5PRS pass rate: {pass_rate:.1%}"
            )
            results.append(result)
        
        # Condition 10: 5PRS inspection quantity >= 100
        if 10 in applicable:
            inspection_qty = employee_data.get('Total Valiation Qty', 
                           employee_data.get('Total Validation Qty', 0))
            threshold = self.matrix.get('validation_rules', {}).get('5prs', {}).get('minimum_inspection_qty', 100)
            result = ConditionResult(
                condition_id=10,
                condition_name="5PRS Inspection Quantity >= 100",
                is_applicable=True,
                is_passed=inspection_qty >= threshold,
                actual_value=inspection_qty,
                threshold_value=threshold,
                message=f"5PRS inspection quantity: {inspection_qty} pairs"
            )
            results.append(result)
        
        return results
    
    def preprocess_employee_data(self, employee_data: Dict) -> Dict:
        """
        Preprocess employee data to correct any data inconsistencies
        
        Main corrections:
        - TYPE-1 STITCHING INSPECTOR → TYPE-2
        
        Args:
            employee_data: Original employee data
            
        Returns:
            Corrected employee data
        """
        data = employee_data.copy()
        
        # Correct TYPE-1 STITCHING INSPECTOR to TYPE-2
        if data.get('ROLE TYPE STD') == 'TYPE-1':
            position = str(data.get('QIP POSITION 1ST NAME', '')).upper()
            if 'STITCHING' in position and 'INSPECTOR' in position:
                data['ROLE TYPE STD'] = 'TYPE-2'
                if data.get('Employee No'):
                    print(f"  → Data correction: {data['Employee No']} TYPE-1 → TYPE-2 (STITCHING INSPECTOR)")
        
        return data
    
    def evaluate_all_conditions(self, employee_data: Dict, employee_type: str, position: str) -> Dict[str, Any]:
        """
        Evaluate all applicable conditions for an employee
        
        Args:
            employee_data: Complete employee data dictionary
            employee_type: Employee type
            position: Employee position
            
        Returns:
            Dictionary containing evaluation results and summary
        """
        # Get all condition results
        attendance_results = self.evaluate_attendance_conditions(employee_data, employee_type, position)
        aql_results = self.evaluate_aql_conditions(employee_data, employee_type, position)
        prs_results = self.evaluate_5prs_conditions(employee_data, employee_type, position)
        
        all_results = attendance_results + aql_results + prs_results
        
        # Calculate summary
        total_applicable = len(all_results)
        total_passed = sum(1 for r in all_results if r.is_passed)
        all_passed = all([r.is_passed for r in all_results if r.is_applicable])
        
        # Get condition display settings
        display_config = self.matrix.get('condition_display', {})
        
        return {
            'employee_no': employee_data.get('Employee No', ''),
            'employee_type': employee_type,
            'position': position,
            'conditions': {
                'attendance': attendance_results,
                'aql': aql_results,
                '5prs': prs_results
            },
            'all_results': all_results,
            'summary': {
                'total_applicable': total_applicable,
                'total_passed': total_passed,
                'all_passed': all_passed,
                'pass_rate': total_passed / total_applicable if total_applicable > 0 else 0
            },
            'display_config': display_config
        }
    
    def get_condition_info(self, condition_id: int) -> Dict:
        """
        Get information about a specific condition
        
        Args:
            condition_id: Condition ID
            
        Returns:
            Dictionary with condition information
        """
        return self.matrix.get('conditions', {}).get(str(condition_id), {})
    
    def get_display_config(self, language: str = 'ko') -> Dict:
        """
        Get display configuration for UI
        
        Args:
            language: Language code (ko, en, vi)
            
        Returns:
            Display configuration dictionary
        """
        display = self.matrix.get('condition_display', {})
        labels = display.get('labels', {}).get(language, display.get('labels', {}).get('ko', {}))
        
        return {
            'icons': display.get('icons', {}),
            'colors': display.get('colors', {}),
            'labels': labels
        }
    
    def get_ui_metadata(self, employee_type: str, position: str, language: str = 'ko') -> Dict:
        """
        Generate UI metadata for dynamic rendering
        
        Args:
            employee_type: Employee type (TYPE-1, TYPE-2, TYPE-3)
            position: Employee position
            language: Language code (ko, en, vi)
            
        Returns:
            Complete UI metadata for rendering
        """
        applicable, excluded = self.get_applicable_conditions(employee_type, position)
        
        # Condition categories with all 10 conditions
        all_conditions = {
            'attendance': [1, 2, 3, 4],
            'aql': [5, 6, 7, 8],
            '5prs': [9, 10]
        }
        
        # Category names and icons
        category_info = {
            'attendance': {
                'ko': {'name': '출근 조건', 'icon': '📅'},
                'en': {'name': 'Attendance', 'icon': '📅'},
                'vi': {'name': 'Điều kiện tham dự', 'icon': '📅'}
            },
            'aql': {
                'ko': {'name': 'AQL 조건', 'icon': '🎯'},
                'en': {'name': 'AQL Conditions', 'icon': '🎯'},
                'vi': {'name': 'Điều kiện AQL', 'icon': '🎯'}
            },
            '5prs': {
                'ko': {'name': '5PRS 조건', 'icon': '📊'},
                'en': {'name': '5PRS Conditions', 'icon': '📊'},
                'vi': {'name': 'Điều kiện 5PRS', 'icon': '📊'}
            }
        }
        
        # Build condition groups
        condition_groups = {}
        
        for category, condition_ids in all_conditions.items():
            applicable_in_category = [cid for cid in condition_ids if cid in applicable]
            
            conditions_list = []
            for cid in condition_ids:
                cond_info = self.get_condition_info(cid)
                conditions_list.append({
                    'id': cid,
                    'name': cond_info.get('name', f'Condition {cid}'),
                    'description': cond_info.get('description', ''),
                    'applicable': cid in applicable
                })
            
            condition_groups[category] = {
                'name': category_info[category][language]['name'],
                'icon': category_info[category][language]['icon'],
                'applicable_count': len(applicable_in_category),
                'total_count': len(condition_ids),
                'conditions': conditions_list
            }
        
        # Build metadata
        metadata = {
            'position_info': {
                'type': employee_type,
                'position': position,
                'description': self._get_position_description(employee_type, position)
            },
            'condition_groups': condition_groups,
            'display_config': {
                'show_empty_groups': False,
                'group_order': ['attendance', 'aql', '5prs'],
                'language': language,
                'colors': self.matrix.get('condition_display', {}).get('colors', {}),
                'icons': self.matrix.get('condition_display', {}).get('icons', {})
            },
            'statistics': {
                'total_conditions': 10,
                'applicable_conditions': len(applicable),
                'excluded_conditions': len(excluded)
            }
        }
        
        return metadata
    
    def _get_position_description(self, employee_type: str, position: str) -> str:
        """Get position description from matrix"""
        type_matrix = self.matrix.get('position_matrix', {}).get(employee_type, {})
        
        # Search for position in type matrix
        for key, config in type_matrix.items():
            if key == 'default':
                continue
            if isinstance(config, dict) and 'patterns' in config:
                for pattern in config['patterns']:
                    if pattern.upper() == position.upper():
                        return config.get('description', position)
        
        return position
    
    def export_condition_summary(self, employee_type: str, position: str) -> Dict:
        """
        Export a summary of applicable conditions for documentation
        
        Args:
            employee_type: Employee type
            position: Employee position
            
        Returns:
            Summary dictionary
        """
        applicable, excluded = self.get_applicable_conditions(employee_type, position)
        
        summary = {
            'employee_type': employee_type,
            'position': position,
            'applicable_conditions': [],
            'excluded_conditions': []
        }
        
        # Add condition details
        for cond_id in applicable:
            cond_info = self.get_condition_info(cond_id)
            summary['applicable_conditions'].append({
                'id': cond_id,
                'name': cond_info.get('name', f'Condition {cond_id}'),
                'category': cond_info.get('category', 'unknown'),
                'description': cond_info.get('description', '')
            })
        
        for cond_id in excluded:
            cond_info = self.get_condition_info(cond_id)
            summary['excluded_conditions'].append({
                'id': cond_id,
                'name': cond_info.get('name', f'Condition {cond_id}'),
                'category': cond_info.get('category', 'unknown'),
                'description': cond_info.get('description', '')
            })
        
        return summary


# Helper functions for backward compatibility
def get_condition_manager(matrix_path: str = None) -> ConditionMatrixManager:
    """Get or create a condition matrix manager instance"""
    return ConditionMatrixManager(matrix_path)


def check_conditions_for_position(employee_type: str, position: str, employee_data: Dict) -> Dict:
    """
    Quick helper function to check all conditions for a position
    
    Args:
        employee_type: Employee type
        position: Employee position
        employee_data: Employee data dictionary
        
    Returns:
        Evaluation results
    """
    manager = get_condition_manager()
    return manager.evaluate_all_conditions(employee_data, employee_type, position)