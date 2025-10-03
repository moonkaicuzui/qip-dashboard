#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard V2 - Data Processing Module
Handles all data loading, processing, and transformation
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from common_employee_filter import EmployeeFilter
from common_date_parser import DateParser


class DataProcessor:
    """Central data processing class for the dashboard"""

    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.config = None
        self.translations = None
        self.position_matrix = None
        self.df = None
        self.stats = {}

    def load_configurations(self):
        """Load all configuration files"""
        # Load monthly config
        config_file = f'config_files/config_{self.month}_{self.year}.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # Load translations
        trans_file = 'config_files/dashboard_translations.json'
        with open(trans_file, 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

        # Load position matrix
        matrix_file = 'config_files/position_condition_matrix.json'
        with open(matrix_file, 'r', encoding='utf-8') as f:
            self.position_matrix = json.load(f)

        return True

    def load_data(self):
        """Load and process incentive data"""
        # Check for Google Drive sync status file
        sync_status_file = Path('.cache/drive_sync/last_sync.json')
        if sync_status_file.exists():
            with open(sync_status_file, 'r') as f:
                sync_info = json.load(f)
                timestamp_str = sync_info.get('timestamp', '2000-01-01')
                # Remove timezone info if present for comparison
                if '+' in timestamp_str or 'T' in timestamp_str:
                    timestamp_str = timestamp_str.split('+')[0].split('Z')[0]
                    last_sync = datetime.fromisoformat(timestamp_str.replace('Z', ''))
                else:
                    last_sync = datetime.fromisoformat(timestamp_str)
                # Check if sync is recent (within 24 hours)
                if (datetime.now() - last_sync).days > 1:
                    raise RuntimeError("❌ Data is outdated! Google Drive sync required.\nPlease run: python src/auto_run_with_drive.py --sync")
        else:
            raise RuntimeError("❌ No Google Drive sync detected!\nData must be synchronized from Google Drive before generating dashboard.\nPlease run: python src/auto_run_with_drive.py --sync")

        # Determine file path
        excel_file = f'output_files/output_QIP_incentive_{self.month}_{self.year}_최종완성버전_v6.0_Complete.xlsx'
        csv_file = excel_file.replace('.xlsx', '.csv')

        # Try CSV first (faster)
        if os.path.exists(csv_file):
            self.df = pd.read_csv(csv_file)
        elif os.path.exists(excel_file):
            self.df = pd.read_excel(excel_file)
        else:
            raise FileNotFoundError("❌ No data file found. Please run the complete pipeline with Google Drive sync.")

        # Apply employee filter FIRST (before renaming columns)
        filter_obj = EmployeeFilter()
        # Get month number for filtering
        month_num = self._get_month_number(self.month)
        self.df = filter_obj.filter_active_employees(
            self.df,
            target_month=month_num,
            target_year=self.year,
            include_future=False
        )

        # THEN standardize column names for easier access
        column_mapping = {
            'Employee No': 'employee_id',
            'Full Name': 'name',
            'FINAL QIP POSITION NAME CODE': 'position',
            'ROLE TYPE STD': 'type',
            'Final Incentive amount': 'amount',
            'Entrance Date': 'work_start_date',
            'Attendance Rate': '출근율_Attendance_Rate_Percent',
            'TARGET AQL': 'aql_target',
            'ACTUAL AQL': 'aql_actual',
            'AQL FAIL': 'aql_failure',
            '5PRS SCORE': '5prs_score',
            'Direct Manager ID': 'boss_id'
        }

        # Rename columns that exist
        for old_name, new_name in column_mapping.items():
            if old_name in self.df.columns:
                self.df.rename(columns={old_name: new_name}, inplace=True)

        # Ensure amount column exists and is numeric
        if 'amount' not in self.df.columns:
            self.df['amount'] = 0
        else:
            self.df['amount'] = pd.to_numeric(self.df['amount'], errors='coerce').fillna(0)

        # Process dates
        date_columns = ['work_start_date', 'aql_failure_date', 'previous_aql_date']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(DateParser.parse_date)

        # Calculate statistics
        self._calculate_statistics()

        return True

    def _get_month_number(self, month_str):
        """Convert month string to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3,
            'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9,
            'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month_str.lower(), 0)

    def _calculate_statistics(self):
        """Calculate dashboard statistics"""
        total_emp = len(self.df)
        paid_emp = len(self.df[self.df['amount'] > 0])
        total_amt = self.df['amount'].sum() if 'amount' in self.df.columns else 0

        self.stats = {
            'totalEmployees': int(total_emp),
            'paidEmployees': int(paid_emp),
            'paymentRate': float((paid_emp / total_emp * 100) if total_emp > 0 else 0),
            'totalAmount': float(total_amt)
        }

    def get_employees_data(self):
        """Get processed employee data as dictionary"""
        if self.df is None:
            return []

        # Convert DataFrame to list of dictionaries
        employees = self.df.to_dict('records')

        # Process each employee
        for emp in employees:
            # Clean up data for JSON serialization
            cleaned = {}
            for key, value in emp.items():
                # Handle NaN/NaT values
                if pd.isna(value):
                    cleaned[key] = None
                # Handle Timestamp objects
                elif isinstance(value, pd.Timestamp):
                    cleaned[key] = value.strftime('%Y-%m-%d')
                # Handle datetime64
                elif hasattr(value, 'dtype') and pd.api.types.is_datetime64_any_dtype(value.dtype):
                    cleaned[key] = str(value)
                # Handle numpy numbers
                elif hasattr(value, 'item'):
                    cleaned[key] = value.item()
                else:
                    cleaned[key] = value

            # Update employee dict with cleaned values
            emp.update(cleaned)

            # Ensure all required fields exist
            emp['employee_id'] = str(emp.get('employee_id', ''))
            emp['name'] = str(emp.get('name', ''))
            emp['position'] = str(emp.get('position', ''))
            emp['type'] = str(emp.get('type', 'Unknown'))
            emp['amount'] = float(emp.get('amount', 0))
            emp['paid'] = emp['amount'] > 0

            # Add condition results if available
            if 'condition_results' in emp and isinstance(emp['condition_results'], str):
                try:
                    emp['condition_results'] = json.loads(emp['condition_results'])
                except:
                    emp['condition_results'] = []
            else:
                emp['condition_results'] = []

        return employees

    def get_position_summary(self):
        """Get position-based summary data"""
        if self.df is None:
            return []

        # Group by position
        position_groups = self.df.groupby('position').agg({
            'employee_id': 'count',
            'amount': ['sum', lambda x: (x > 0).sum()]
        }).round(2)

        # Flatten column names
        position_groups.columns = ['total_count', 'total_amount', 'paid_count']
        position_groups = position_groups.reset_index()

        # Add type information
        position_groups['type'] = position_groups['position'].apply(
            lambda x: self._get_type_for_position(x)
        )

        # Calculate payment rate
        position_groups['payment_rate'] = (
            position_groups['paid_count'] / position_groups['total_count'] * 100
        ).round(1)

        return position_groups.to_dict('records')

    def _get_type_for_position(self, position):
        """Get TYPE classification for a position"""
        if not self.position_matrix:
            return 'Unknown'

        # Check position mapping
        position_mapping = self.position_matrix.get('position_mapping', {})

        for type_key, positions in position_mapping.items():
            if position in positions:
                return type_key

        return 'Unknown'

    def get_individual_details(self):
        """Get detailed individual employee data"""
        if self.df is None:
            return []

        # Select relevant columns
        columns = [
            'employee_id', 'name', 'position', 'type',
            '출근율_Attendance_Rate_Percent', 'aql_failure', '5prs_score',
            'amount', 'condition_results'
        ]

        # Filter to available columns
        available_cols = [col for col in columns if col in self.df.columns]
        details = self.df[available_cols].copy()

        # Sort by amount (descending)
        details = details.sort_values('amount', ascending=False)

        return details.to_dict('records')

    def get_conditions_analysis(self):
        """Analyze condition pass/fail rates"""
        if self.df is None or not self.position_matrix:
            return {}

        conditions_def = self.position_matrix.get('conditions', {})
        analysis = {}

        for condition_key, condition_info in conditions_def.items():
            analysis[condition_key] = {
                'name': condition_info.get('name', condition_key),
                'description': condition_info.get('description', ''),
                'total_evaluated': 0,
                'passed': 0,
                'failed': 0,
                'pass_rate': 0
            }

        # Analyze condition results
        for _, row in self.df.iterrows():
            if 'condition_results' in row:
                results = row['condition_results']
                if isinstance(results, str):
                    try:
                        results = json.loads(results)
                    except:
                        continue

                for result in results:
                    condition = result.get('condition')
                    if condition in analysis:
                        analysis[condition]['total_evaluated'] += 1
                        if result.get('met'):
                            analysis[condition]['passed'] += 1
                        else:
                            analysis[condition]['failed'] += 1

        # Calculate pass rates
        for condition in analysis.values():
            if condition['total_evaluated'] > 0:
                condition['pass_rate'] = round(
                    (condition['passed'] / condition['total_evaluated']) * 100, 1
                )

        return analysis

    def get_org_chart_data(self):
        """Get organization chart data (TYPE-1 hierarchy)"""
        if self.df is None:
            return []

        # Filter TYPE-1 employees
        type1_df = self.df[self.df['type'] == 'TYPE-1'].copy()

        if type1_df.empty:
            return []

        # Build hierarchy
        hierarchy = []

        # Find top-level managers (no boss_id or boss_id is empty)
        top_managers = type1_df[
            (type1_df['boss_id'].isna()) |
            (type1_df['boss_id'] == '') |
            (type1_df['boss_id'] == '0')
        ]

        for _, manager in top_managers.iterrows():
            manager_data = self._build_manager_node(manager, type1_df)
            hierarchy.append(manager_data)

        return hierarchy

    def _build_manager_node(self, manager, all_employees):
        """Build a manager node with team members"""
        node = {
            'employee_id': manager['employee_id'],
            'name': manager['name'],
            'position': manager['position'],
            'amount': float(manager['amount']),
            'team_members': []
        }

        # Find direct reports
        direct_reports = all_employees[
            all_employees['boss_id'] == manager['employee_id']
        ]

        for _, report in direct_reports.iterrows():
            # Recursively build sub-nodes
            node['team_members'].append(
                self._build_manager_node(report, all_employees)
            )

        return node

    def export_to_json(self):
        """Export all processed data to JSON format"""
        return {
            'employees': self.get_employees_data(),
            'stats': self.stats,
            'config': {
                'month': self.month,
                'year': self.year,
                'workingDays': self.config.get('working_days', 0) if self.config else 0
            },
            'translations': self.translations,
            'positionMatrix': self.position_matrix
        }


def main():
    """Test the data processor"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--month', type=str, default='september')
    parser.add_argument('--year', type=int, default=2025)
    args = parser.parse_args()

    processor = DataProcessor(args.month, args.year)

    try:
        print(f"Loading configurations for {args.month} {args.year}...")
        processor.load_configurations()
        print("✅ Configurations loaded")

        print("\nLoading data...")
        processor.load_data()
        print(f"✅ Data loaded: {len(processor.df)} employees")

        print("\nStatistics:")
        for key, value in processor.stats.items():
            print(f"  {key}: {value}")

        print("\nExporting to JSON...")
        data = processor.export_to_json()
        print(f"✅ Export complete: {len(data['employees'])} employees")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())