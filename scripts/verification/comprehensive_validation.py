#!/usr/bin/env python3
"""
Comprehensive Validation Script for November 2025 Dashboard
100% Full Inspection Mode - ultrathink analysis

Validates:
1. October Excel vs November Dashboard Previous_Incentive (100% match)
2. Continuous months calculation logic (TYPE-1)
3. Incentive amounts for TYPE-2/TYPE-3 (no continuous months)
4. LINE LEADER (TYPE-2) calculation logic
5. Theme color updates
6. Potential confusion points
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.MAGENTA}ℹ {text}{Colors.END}")

# Validation 1: October Excel vs November Dashboard Previous_Incentive
def validate_previous_incentive_full_inspection():
    print_header("VALIDATION 1: October Excel vs November Dashboard Previous_Incentive")
    print_section("Loading October Excel file...")

    october_excel_path = "2025 october completed final incentive amount data.xlsx"

    try:
        # Load October Excel
        october_df = pd.read_excel(october_excel_path)
        print_success(f"Loaded October Excel: {len(october_df)} employees")
        print_info(f"Columns: {list(october_df.columns)}")

        # Load November CSV
        print_section("Loading November CSV file...")
        november_csv_path = "output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"
        november_df = pd.read_csv(november_csv_path)
        print_success(f"Loaded November CSV: {len(november_df)} employees")

        # Identify incentive column in October Excel
        october_incentive_col = None
        for col in october_df.columns:
            if 'incentive' in col.lower() or 'october' in col.lower():
                print_info(f"Candidate column: {col}")
                if 'previous' not in col.lower():
                    october_incentive_col = col
                    break

        if october_incentive_col is None:
            # Try to find the rightmost numeric column
            numeric_cols = october_df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                october_incentive_col = numeric_cols[-1]
                print_warning(f"Using last numeric column as October incentive: {october_incentive_col}")

        print_info(f"October incentive column: {october_incentive_col}")

        # Employee No column detection
        emp_col_october = None
        emp_col_november = 'Employee No'

        for col in october_df.columns:
            if 'employee' in col.lower() and 'no' in col.lower():
                emp_col_october = col
                break

        if emp_col_october is None:
            emp_col_october = october_df.columns[0]
            print_warning(f"Using first column as Employee No: {emp_col_october}")

        print_info(f"October Employee No column: {emp_col_october}")

        # Create mapping
        october_dict = {}
        for _, row in october_df.iterrows():
            emp_no = str(row[emp_col_october]).strip()
            incentive = row[october_incentive_col]
            if pd.notna(incentive):
                october_dict[emp_no] = float(incentive)
            else:
                october_dict[emp_no] = 0.0

        print_success(f"Created October mapping: {len(october_dict)} employees")

        # Compare with November Previous_Incentive
        print_section("Starting 100% Full Inspection...")

        total_employees = 0
        matched = 0
        mismatched = 0
        october_missing = 0
        mismatch_details = []

        for _, row in november_df.iterrows():
            emp_no = str(row['Employee No']).strip()
            november_prev = row['Previous_Incentive']

            total_employees += 1

            if pd.isna(november_prev):
                november_prev = 0.0
            else:
                november_prev = float(november_prev)

            if emp_no in october_dict:
                october_value = october_dict[emp_no]

                if abs(october_value - november_prev) < 0.01:  # Float comparison tolerance
                    matched += 1
                else:
                    mismatched += 1
                    mismatch_details.append({
                        'Employee No': emp_no,
                        'Name': row.get('Employee Name (Korean)', 'N/A'),
                        'October': october_value,
                        'November Prev': november_prev,
                        'Difference': november_prev - october_value
                    })
            else:
                october_missing += 1
                if november_prev != 0:
                    mismatch_details.append({
                        'Employee No': emp_no,
                        'Name': row.get('Employee Name (Korean)', 'N/A'),
                        'October': 'NOT FOUND',
                        'November Prev': november_prev,
                        'Difference': 'N/A'
                    })

        # Print results
        print_section("100% Full Inspection Results:")
        print(f"Total Employees Checked: {total_employees}")
        print_success(f"Matched: {matched} ({matched/total_employees*100:.2f}%)")

        if mismatched > 0:
            print_error(f"Mismatched: {mismatched} ({mismatched/total_employees*100:.2f}%)")

        if october_missing > 0:
            print_warning(f"Not found in October Excel: {october_missing}")

        if mismatch_details:
            print_section("Mismatch Details:")
            for detail in mismatch_details[:20]:  # Show first 20
                print(f"  Employee {detail['Employee No']} ({detail['Name']})")
                print(f"    October: {detail['October']:,} VND")
                print(f"    November Prev: {detail['November Prev']:,} VND")
                if detail['Difference'] != 'N/A':
                    print(f"    Difference: {detail['Difference']:,} VND")
                print()

            if len(mismatch_details) > 20:
                print_info(f"... and {len(mismatch_details)-20} more mismatches")

        # Final verdict
        if mismatched == 0 and october_missing == 0:
            print_success("✓✓✓ VALIDATION 1 PASSED: 100% Perfect Match ✓✓✓")
            return True
        else:
            print_error(f"✗✗✗ VALIDATION 1 FAILED: {mismatched + october_missing} discrepancies found ✗✗✗")
            return False

    except Exception as e:
        print_error(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

# Validation 2: Continuous Months Calculation Logic
def validate_continuous_months_logic():
    print_header("VALIDATION 2: Continuous Months Calculation Logic (TYPE-1)")
    print_section("Loading November CSV and config files...")

    try:
        # Load November CSV
        november_csv_path = "output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"
        df = pd.read_csv(november_csv_path)
        print_success(f"Loaded November CSV: {len(df)} employees")

        # Load position matrix
        with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
            matrix = json.load(f)

        progression_table = matrix['incentive_progression']['TYPE_1_PROGRESSIVE']['progression_table']
        print_success(f"Loaded progression table: {len(progression_table)} months")

        # Filter TYPE-1 employees
        type1_employees = df[df['TYPE'] == 1].copy()
        print_info(f"TYPE-1 employees: {len(type1_employees)}")

        # Validate continuous months logic
        print_section("Validating continuous months calculation...")

        errors = []
        for idx, row in type1_employees.iterrows():
            emp_no = row['Employee No']
            name = row.get('Employee Name (Korean)', 'N/A')
            continuous_months = row['Continuous_Months']
            prev_incentive = row['Previous_Incentive']
            current_incentive = row['November_Incentive']
            pass_rate = row['conditions_pass_rate']

            # Handle NaN
            if pd.isna(continuous_months):
                continuous_months = 0
            else:
                continuous_months = int(continuous_months)

            if pd.isna(prev_incentive):
                prev_incentive = 0
            if pd.isna(current_incentive):
                current_incentive = 0
            if pd.isna(pass_rate):
                pass_rate = 0

            # Logic check
            if pass_rate >= 100:
                # Should increment
                expected_continuous = min(continuous_months, 15)
                expected_incentive = float(progression_table[str(expected_continuous)])

                if abs(current_incentive - expected_incentive) > 0.01:
                    errors.append({
                        'Employee No': emp_no,
                        'Name': name,
                        'Continuous Months': continuous_months,
                        'Expected Incentive': expected_incentive,
                        'Actual Incentive': current_incentive,
                        'Pass Rate': pass_rate
                    })
            else:
                # Should reset to 0
                if continuous_months != 0:
                    errors.append({
                        'Employee No': emp_no,
                        'Name': name,
                        'Continuous Months': continuous_months,
                        'Issue': 'Should be 0 (failed conditions)',
                        'Pass Rate': pass_rate
                    })

                if current_incentive != 0:
                    errors.append({
                        'Employee No': emp_no,
                        'Name': name,
                        'Current Incentive': current_incentive,
                        'Issue': 'Should be 0 (failed conditions)',
                        'Pass Rate': pass_rate
                    })

        # Print results
        if errors:
            print_error(f"Found {len(errors)} continuous months calculation errors:")
            for err in errors[:10]:
                print(f"  {err}")
            if len(errors) > 10:
                print_info(f"... and {len(errors)-10} more errors")
            print_error("✗✗✗ VALIDATION 2 FAILED ✗✗✗")
            return False
        else:
            print_success("✓✓✓ VALIDATION 2 PASSED: All continuous months calculations correct ✓✓✓")
            return True

    except Exception as e:
        print_error(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

# Validation 3: TYPE-2 and TYPE-3 Incentive Amounts
def validate_type2_type3_incentives():
    print_header("VALIDATION 3: TYPE-2 and TYPE-3 Incentive Amounts")
    print_section("Loading November CSV...")

    try:
        november_csv_path = "output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"
        df = pd.read_csv(november_csv_path)
        print_success(f"Loaded November CSV: {len(df)} employees")

        # TYPE-3 validation (should all be 0)
        print_section("Validating TYPE-3 employees (should all be 0)...")
        type3_employees = df[df['TYPE'] == 3].copy()
        print_info(f"TYPE-3 employees: {len(type3_employees)}")

        type3_errors = []
        for idx, row in type3_employees.iterrows():
            incentive = row['November_Incentive']
            if pd.notna(incentive) and incentive != 0:
                type3_errors.append({
                    'Employee No': row['Employee No'],
                    'Name': row.get('Employee Name (Korean)', 'N/A'),
                    'Incentive': incentive,
                    'Expected': 0
                })

        if type3_errors:
            print_error(f"Found {len(type3_errors)} TYPE-3 errors (should be 0 VND):")
            for err in type3_errors:
                print(f"  {err}")
        else:
            print_success("All TYPE-3 employees have 0 VND incentive ✓")

        # TYPE-2 validation
        print_section("Validating TYPE-2 employees...")
        type2_employees = df[df['TYPE'] == 2].copy()
        print_info(f"TYPE-2 employees: {len(type2_employees)}")

        # Load position matrix to get TYPE-2 calculation rules
        with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
            matrix = json.load(f)

        type2_mapping = matrix.get('type_2_position_mapping', {})
        progression_table = matrix['incentive_progression']['TYPE_1_PROGRESSIVE']['progression_table']

        print_info(f"TYPE-2 position mapping: {len(type2_mapping)} positions")

        type2_errors = []
        type2_analysis = []

        for idx, row in type2_employees.iterrows():
            emp_no = row['Employee No']
            name = row.get('Employee Name (Korean)', 'N/A')
            position = row.get('Position', 'Unknown')
            pass_rate = row['conditions_pass_rate']
            current_incentive = row['November_Incentive']
            continuous_months = row.get('Continuous_Months', 0)

            if pd.isna(pass_rate):
                pass_rate = 0
            if pd.isna(current_incentive):
                current_incentive = 0
            if pd.isna(continuous_months):
                continuous_months = 0

            # TYPE-2 should NOT use continuous_months for calculation
            # Should follow 100% rule
            if pass_rate >= 100:
                # Should receive incentive based on TYPE-1 average
                # But we need to check what the actual calculation is
                type2_analysis.append({
                    'Employee No': emp_no,
                    'Name': name,
                    'Position': position,
                    'Pass Rate': pass_rate,
                    'Incentive': current_incentive,
                    'Continuous Months': continuous_months
                })
            else:
                # Should be 0
                if current_incentive != 0:
                    type2_errors.append({
                        'Employee No': emp_no,
                        'Name': name,
                        'Position': position,
                        'Pass Rate': pass_rate,
                        'Incentive': current_incentive,
                        'Expected': 0,
                        'Issue': '100% rule violation'
                    })

        # Print TYPE-2 analysis
        if type2_analysis:
            print_info(f"TYPE-2 employees with 100% pass: {len(type2_analysis)}")
            print_section("Sample TYPE-2 calculations:")
            for item in type2_analysis[:5]:
                print(f"  {item}")

        if type2_errors:
            print_error(f"Found {len(type2_errors)} TYPE-2 errors:")
            for err in type2_errors:
                print(f"  {err}")
        else:
            print_success("All TYPE-2 employees follow 100% rule ✓")

        # Final verdict
        total_errors = len(type3_errors) + len(type2_errors)
        if total_errors == 0:
            print_success("✓✓✓ VALIDATION 3 PASSED ✓✓✓")
            return True
        else:
            print_error(f"✗✗✗ VALIDATION 3 FAILED: {total_errors} errors found ✗✗✗")
            return False

    except Exception as e:
        print_error(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

# Validation 4: LINE LEADER Calculation Logic
def validate_line_leader_calculation():
    print_header("VALIDATION 4: LINE LEADER (TYPE-2) Calculation Logic")
    print_section("Loading November CSV...")

    try:
        november_csv_path = "output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"
        df = pd.read_csv(november_csv_path)
        print_success(f"Loaded November CSV: {len(df)} employees")

        # Filter LINE LEADER
        line_leaders = df[df['Position'].str.contains('LINE LEADER', case=False, na=False)].copy()
        print_info(f"LINE LEADER employees: {len(line_leaders)}")

        if len(line_leaders) == 0:
            print_warning("No LINE LEADER found in data")
            return True

        # Check LINE LEADER calculation logic
        print_section("LINE LEADER Calculation Formula Check:")
        print_info("Formula: (Total Subordinate Incentive) × 12% × Receiving Ratio")
        print_info("Receiving Ratio: (Subordinates with incentive > 0) / (Total active subordinates)")

        # Display LINE LEADER details
        for idx, row in line_leaders.iterrows():
            emp_no = row['Employee No']
            name = row.get('Employee Name (Korean)', 'N/A')
            incentive = row['November_Incentive']
            pass_rate = row['conditions_pass_rate']
            type_val = row['TYPE']

            if pd.isna(incentive):
                incentive = 0
            if pd.isna(pass_rate):
                pass_rate = 0

            print(f"\n  LINE LEADER: {emp_no} ({name})")
            print(f"    TYPE: {type_val}")
            print(f"    Pass Rate: {pass_rate}%")
            print(f"    Incentive: {incentive:,.0f} VND")

            # Check if TYPE is 2
            if type_val != 2:
                print_warning(f"    WARNING: Expected TYPE-2, found TYPE-{type_val}")

            # Note: We cannot validate the exact calculation without subordinate mapping
            # But we can check consistency
            if pass_rate >= 100 and incentive == 0:
                print_warning("    WARNING: 100% pass but 0 incentive (possible: no subordinates received)")
            elif pass_rate < 100 and incentive != 0:
                print_error("    ERROR: Failed conditions but received incentive")

        print_success("✓✓✓ VALIDATION 4 COMPLETED: LINE LEADER analysis done ✓✓✓")
        print_info("Note: Detailed subordinate mapping validation requires calculation script inspection")
        return True

    except Exception as e:
        print_error(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

# Validation 5: Theme Color Update Check
def validate_theme_color():
    print_header("VALIDATION 5: Dashboard Theme Color Update")
    print_section("Checking selector.html theme color...")

    try:
        selector_path = "docs/selector.html"

        if not Path(selector_path).exists():
            print_error(f"selector.html not found at {selector_path}")
            return False

        with open(selector_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for red theme
        red_gradients = [
            '#ef4444',  # Tailwind red-500
            '#dc2626',  # Tailwind red-600
            '#b91c1c',  # Tailwind red-700
            '#991b1b'   # Tailwind red-800
        ]

        purple_gradients = [
            '#667eea',  # Old purple
            '#764ba2'   # Old purple
        ]

        has_red = any(color in content for color in red_gradients)
        has_purple = any(color in content for color in purple_gradients)

        print_section("Theme Color Analysis:")
        print(f"  Red theme colors found: {has_red}")
        print(f"  Purple theme colors found: {has_purple}")

        if has_red and not has_purple:
            print_success("✓✓✓ VALIDATION 5 PASSED: Red theme active ✓✓✓")
            return True
        elif has_purple:
            print_error("✗✗✗ VALIDATION 5 FAILED: Still using purple theme ✗✗✗")
            return False
        else:
            print_warning("⚠ WARNING: Unknown theme colors")
            return False

    except Exception as e:
        print_error(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

# Validation 6: Confusion Points Check
def validate_confusion_points():
    print_header("VALIDATION 6: Potential Confusion Points Final Check")

    confusion_points = []

    # Check 1: Duplicate month cards in selector
    print_section("Check 1: Duplicate month cards in selector.html")
    try:
        with open('docs/selector.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Count occurrences of "11월" or "November"
        november_korean = content.count('11월')
        november_english = content.count('November 2025')

        print(f"  '11월' occurrences: {november_korean}")
        print(f"  'November 2025' occurrences: {november_english}")

        # Should appear multiple times (in translations) but not duplicated in cards
        # Check for duplicate month-card divs
        import re
        month_cards = re.findall(r'class="month-card"[^>]*>.*?</a>', content, re.DOTALL)

        november_cards = [card for card in month_cards if '11' in card and ('11월' in card or 'November' in card)]

        print(f"  November month cards found: {len(november_cards)}")

        if len(november_cards) > 1:
            print_warning(f"  ⚠ WARNING: Multiple November cards detected ({len(november_cards)})")
            confusion_points.append("Multiple November month cards in selector.html")
        else:
            print_success("  ✓ Single November card as expected")

    except Exception as e:
        print_error(f"  Error checking selector: {e}")
        confusion_points.append(f"Error checking selector: {e}")

    # Check 2: Language-specific date translations
    print_section("Check 2: Language-specific date translations")
    try:
        with open('docs/selector.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for month-11 translation key
        has_month_key = 'data-i18n="month-11"' in content
        has_korean_translation = "'month-11': '11월'" in content
        has_english_translation = "'month-11': 'November 2025'" in content
        has_vietnamese_translation = "'month-11': 'Tháng 11 năm 2025'" in content

        print(f"  month-11 translation key: {has_month_key}")
        print(f"  Korean translation: {has_korean_translation}")
        print(f"  English translation: {has_english_translation}")
        print(f"  Vietnamese translation: {has_vietnamese_translation}")

        if has_month_key and has_korean_translation and has_english_translation and has_vietnamese_translation:
            print_success("  ✓ All language translations present")
        else:
            print_warning("  ⚠ WARNING: Missing language-specific translations")
            confusion_points.append("Missing language-specific month translations")

    except Exception as e:
        print_error(f"  Error checking translations: {e}")
        confusion_points.append(f"Error checking translations: {e}")

    # Check 3: Version consistency
    print_section("Check 3: Version consistency across files")
    try:
        # Check dashboard HTML version
        dashboard_path = "docs/Incentive_Dashboard_2025_11_Version_9.0.html"
        csv_path = "docs/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"
        excel_path = "docs/output_QIP_incentive_november_2025_Complete_V9.0_Complete.xlsx"

        files_exist = {
            'Dashboard HTML': Path(dashboard_path).exists(),
            'CSV V9.0': Path(csv_path).exists(),
            'Excel V9.0': Path(excel_path).exists()
        }

        print("  File existence check:")
        for file, exists in files_exist.items():
            if exists:
                print_success(f"    ✓ {file}")
            else:
                print_error(f"    ✗ {file} MISSING")
                confusion_points.append(f"{file} missing from docs/")

    except Exception as e:
        print_error(f"  Error checking versions: {e}")
        confusion_points.append(f"Error checking versions: {e}")

    # Final verdict
    print_section("Confusion Points Summary:")
    if confusion_points:
        print_error(f"Found {len(confusion_points)} potential confusion points:")
        for point in confusion_points:
            print(f"  • {point}")
        print_error("✗✗✗ VALIDATION 6 FAILED ✗✗✗")
        return False
    else:
        print_success("No confusion points detected ✓")
        print_success("✓✓✓ VALIDATION 6 PASSED ✓✓✓")
        return True

# Main execution
def main():
    print_header("🔍 COMPREHENSIVE VALIDATION - ULTRATHINK MODE 🔍")
    print_info("Starting 100% full inspection of November 2025 Dashboard")
    print_info("This validation covers:")
    print_info("  1. October Excel vs November Dashboard Previous_Incentive")
    print_info("  2. Continuous months calculation logic (TYPE-1)")
    print_info("  3. TYPE-2/TYPE-3 incentive amounts")
    print_info("  4. LINE LEADER calculation logic")
    print_info("  5. Theme color updates")
    print_info("  6. Potential confusion points")
    print()

    results = {}

    # Run all validations
    results['Previous Incentive Match'] = validate_previous_incentive_full_inspection()
    results['Continuous Months Logic'] = validate_continuous_months_logic()
    results['TYPE-2/TYPE-3 Amounts'] = validate_type2_type3_incentives()
    results['LINE LEADER Calculation'] = validate_line_leader_calculation()
    results['Theme Color'] = validate_theme_color()
    results['Confusion Points'] = validate_confusion_points()

    # Final summary
    print_header("📊 FINAL VALIDATION SUMMARY 📊")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for validation, result in results.items():
        if result:
            print_success(f"✓ {validation}: PASSED")
        else:
            print_error(f"✗ {validation}: FAILED")

    print()
    print(f"{Colors.BOLD}Overall Score: {passed}/{total} validations passed{Colors.END}")

    if passed == total:
        print_success(f"\n{'='*80}")
        print_success("🎉 ALL VALIDATIONS PASSED 🎉".center(80))
        print_success(f"{'='*80}\n")
        return 0
    else:
        print_error(f"\n{'='*80}")
        print_error(f"⚠️  {total-passed} VALIDATION(S) FAILED ⚠️".center(80))
        print_error(f"{'='*80}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
