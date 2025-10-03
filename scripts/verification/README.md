# QIP Incentive Data Validation System

Complete data validation pipeline for QIP Incentive Dashboard System to ensure data accuracy and consistency across the entire workflow.

## 🎯 Purpose

Verify data accuracy following the **Single Source of Truth** principle:
- **Data Sources** → **Python Calculation** → **Excel/CSV Files** ✅
- **Excel/CSV Files** → **Dashboard Display** ✅
- **Incentive Recipients** vs **Non-Recipients** ✅
- **Incentive Amounts** for recipients ✅

## 📋 Validation Architecture

### Phase 1: Existing Validation Tools (Already in place)
- `validate_hr_data.py` - Position mapping validation
- `validate_incentive_data.py` - Continuous months logic
- `validate_excel_json_consistency.py` - Excel-JSON consistency

### Phase 2: Core Calculation Validation (NEW ✨)
**validate_condition_evaluation.py**
- Validates all 10 conditions evaluation accuracy:
  - **Conditions 1-4 (Attendance)**:
    - Condition 1: Attendance Rate >= 88%
    - Condition 2: Unapproved Absence <= 2 days
    - Condition 3: Actual Working Days > 0
    - Condition 4: Minimum Working Days >= 12
  - **Conditions 5-8 (AQL Quality)**:
    - Condition 5: Personal AQL Failure = 0
    - Condition 6: Personal AQL 3-month Consecutive Failures
    - Condition 7: Team/Area AQL 3-month Consecutive Failures
    - Condition 8: Area Reject Rate < 3%
  - **Conditions 9-10 (5PRS)**:
    - Condition 9: 5PRS Pass Rate >= 95%
    - Condition 10: 5PRS Inspection Quantity >= 100
- Validates **100% Rule**: conditions_pass_rate < 100% = 0 VND (all conditions must pass)
- Full validation (all employees)

**validate_incentive_amounts.py**
- TYPE-1 Progressive: Validates amounts against progression_table
- TYPE-2 Standard: Validates 100% rule (TYPE-2 uses TYPE-1 average, no fixed range)
- TYPE-3 New Members: Validates 0 VND policy
- Continuous Months Logic: Validates increment (+1) and reset (0)

### Phase 3: Dashboard Consistency Validation (NEW ✨)
**validate_dashboard_consistency.py**
- Validates Dashboard HTML vs CSV data match
- KPI Summary Statistics verification
- Position/TYPE summary verification
- Individual employee data validation (all employees)
- Condition fields validation (10 conditions × all employees)

### Phase 4: Integrated Reporting (NEW ✨)
**generate_final_report.py**
- Aggregates all validation results
- Generates comprehensive Excel report with:
  - Executive Summary
  - Findings by severity (CRITICAL/ERROR/WARNING)
  - Priority-ordered action items with recommendations
  - Detailed findings from all validations

## 🚀 Quick Start

### Recommended: Integrated Workflow (NEW ✨)
```bash
# Run complete report generation + validation in one command
./action.sh

# After dashboard generation completes, you'll be prompted:
# "Run automated data validation? (y/n)"
#
# Choose 'y' to automatically validate:
#   • Condition evaluation accuracy
#   • Incentive amount calculations
#   • Dashboard vs CSV consistency
#   • 100% rule enforcement
#
# If issues are found, you can open the integrated report for review
```

### Standalone Validation
```bash
# Run validation pipeline independently
./run_full_validation.sh

# Interactive prompts will guide you:
# 1. Select year (2025/2026)
# 2. Select month (1-12)
# 3. Confirm and execute
```

### Manual Step-by-Step Execution
```bash
# Step 1: Condition Evaluation
python3 scripts/verification/validate_condition_evaluation.py september 2025

# Step 2: Incentive Amounts
python3 scripts/verification/validate_incentive_amounts.py september 2025

# Step 3: Dashboard Consistency
python3 scripts/verification/validate_dashboard_consistency.py september 2025

# Step 4: Generate Integrated Report
python3 scripts/verification/generate_final_report.py september 2025

# Or run all validations first, then generate report
python3 scripts/verification/generate_final_report.py september 2025 --run-all
```

## 📊 Output Reports

All reports are saved to `validation_reports/` directory:

### Individual Validation Reports
- `condition_evaluation_report_[month]_[year]_[timestamp].xlsx`
- `incentive_amount_report_[month]_[year]_[timestamp].xlsx`
- `dashboard_consistency_report_[month]_[year]_[timestamp].xlsx`

### Integrated Report (Recommended)
- `INTEGRATED_VALIDATION_REPORT_[month]_[year]_[timestamp].xlsx`
  - Executive Summary
  - Validation 요약
  - 모든 Findings (통합)
  - CRITICAL Findings
  - ERROR Findings
  - WARNING Findings
  - 조치 항목 (우선순위) ⭐ **Most Important**
  - Validation 상세 요약

## 🎯 Understanding Validation Results

### Severity Levels
- **CRITICAL** 🚨: Data accuracy issues, immediate action required
  - Examples: 100% rule violations, KPI mismatches, TYPE-3 receiving incentives
- **ERROR** ⚠️: Calculation discrepancies, review needed
  - Examples: Wrong incentive amounts, condition evaluation errors
- **WARNING** ℹ️: Data quality issues, improvement opportunities
  - Examples: Minor field mismatches, formatting inconsistencies

### Exit Codes
- **0**: All validations passed, no findings detected ✅
- **1**: Findings detected, review the reports ⚠️

## 🔍 What Each Validation Checks

### validate_condition_evaluation.py
```yaml
Checks:
  - Condition 1: Attendance rate >= 88% from attendance CSV
  - Condition 2: Unapproved absence <= 2 days verification
  - Condition 3: Actual working days > 0 from attendance data
  - Condition 4: Minimum working days >= 12 verification
  - Condition 5: Personal AQL failure = 0 from AQL history
  - Condition 6: Personal AQL 3-month consecutive failures check
  - Condition 7: Team/Area AQL 3-month consecutive failures check
  - Condition 8: Area reject rate < 3% from AQL data
  - Condition 9: 5PRS pass rate >= 95% from 5PRS data
  - Condition 10: 5PRS inspection quantity >= 100 from 5PRS data
  - 100% Rule: Ensures conditions_pass_rate < 100% receives 0 VND
    (All applicable conditions must pass, not just some)

Validation Scope: All employees (full validation)

Common Issues:
  - Working days mismatch in config
  - Attendance data calculation errors
  - Unapproved absence threshold (2 days, not 0)
  - 80-99% fulfillment incorrectly receiving incentives
  - Missing 5PRS or AQL data for some employees
  - Continuous failure tracking inconsistencies
```

### validate_incentive_amounts.py
```yaml
Checks:
  - TYPE-1: Progressive amounts match progression_table
  - TYPE-2: 100% rule compliance (TYPE-2 uses TYPE-1 position average)
    * No fixed range - depends on TYPE-1 average
    * Only validates 100% pass_rate requirement
  - TYPE-3: Must be 0 VND (policy excluded)
  - Continuous Months: +1 increment when 100%, reset to 0 when <100%

Common Issues:
  - Progressive table lookup errors
  - Continuous months not resetting on failure
  - TYPE-3 incorrectly receiving incentives
  - TYPE-2 100% pass but 0 VND (TYPE-1 average not applied)
```

### validate_dashboard_consistency.py
```yaml
Checks:
  - Total employees count match
  - Incentive recipients count match
  - Total incentive amount match (within 1 VND tolerance)
  - Position/TYPE summary statistics
  - Individual employee data (all employees)
  - All 10 condition fields (all employees)

Validation Scope: All employees (full validation)

Common Issues:
  - NaN handling in JavaScript
  - Data transformation errors
  - Field name mismatches
```

## 💡 Best Practices

### When to Run Validation
1. **After incentive calculation** - Validate calculation accuracy
2. **After dashboard generation** - Verify single source of truth
3. **Before stakeholder review** - Ensure data quality
4. **Monthly routine** - Part of regular process

### Recommended Workflow
```bash
# 1. Generate incentive reports (includes optional validation)
./action.sh

# During execution:
# - Select year and month
# - Wait for report generation
# - When prompted "Run automated data validation?", choose 'y'
# - Validation runs automatically
# - Option to open integrated report

# 2. Review integrated report (if issues found)
# Open: validation_reports/INTEGRATED_VALIDATION_REPORT_*.xlsx
# Focus on: "조치 항목 (우선순위)" sheet (Action Items - Priority Ordered)

# 3. Fix critical issues
# Follow recommendations in the report

# 4. Re-run validation to confirm fixes
./action.sh  # Or ./run_full_validation.sh for standalone validation
```

## 🛠️ Extending Validation

### All 10 Conditions Now Implemented ✅
The validation system now validates all 10 conditions from `position_condition_matrix.json`:
- ✅ Conditions 1-4: Attendance (출근)
- ✅ Conditions 5-8: AQL Quality (품질)
- ✅ Conditions 9-10: 5PRS Inspection (검사)

### Adding Custom Validation Logic
To add additional validation beyond the 10 conditions, edit `validate_condition_evaluation.py`:

```python
def validate_custom_rule(self):
    """Custom business rule validation"""
    errors = []
    # Add your custom validation logic
    for idx, row in self.df_output.iterrows():
        # Check custom conditions
        pass
    return errors

# Then call in run_validation():
all_errors.extend(self.validate_custom_rule())
```

### Adding Custom Validations
Create new script in `scripts/verification/`:

```python
# scripts/verification/validate_custom_logic.py
class CustomValidator:
    def run_validation(self):
        # Your validation logic
        pass
```

Update `generate_final_report.py`:
```python
# Add to report_patterns
'Custom Validation': f'custom_validation_report_{self.month}_{self.year}_*.xlsx'
```

## 📝 Report Interpretation Guide

### "조치 항목 (우선순위)" Sheet - Action Items
Priority-ordered list of issues with recommendations:

**Priority 1 (CRITICAL)**
- Immediate action required
- Data accuracy directly affected
- Example: "100% rule violation - 85% pass rate received 500K VND"
  - Recommendation: "Check step1_인센티브_계산_개선버전.py line 2441"

**Priority 2 (ERROR)**
- Review needed soon
- Calculation discrepancies
- Example: "TYPE-1 amount mismatch - Expected 250K, Got 300K"
  - Recommendation: "Verify continuous_months calculation and progression_table"

**Priority 3 (WARNING)**
- Data quality improvement opportunities
- Example: "Name field minor mismatch - CSV: 'Nguyen Van A', Dashboard: 'Nguyen  Van A'"
  - Recommendation: "Standardize whitespace handling in data processing"

## 🔗 Integration with Existing Tools

### Works With
- `action.sh` - Run validation after report generation
- `integrated_dashboard_final.py` - Validates dashboard output
- `position_condition_matrix.json` - Uses same business rules

### Dependencies
```python
pandas>=1.3.0
openpyxl>=3.0.9
beautifulsoup4>=4.9.3  # For dashboard HTML parsing
```

## ❓ Troubleshooting

### "CSV file not found"
```bash
# Run incentive calculation first
./action.sh
# Then run validation
./run_full_validation.sh
```

### "Dashboard HTML not found"
```bash
# Check month number padding
# Expected: Incentive_Dashboard_2025_09_Version_8.html
# Not: Incentive_Dashboard_2025_9_Version_8.html
```

### "No validation reports found"
```bash
# Use --run-all flag to execute all validations first
python3 scripts/verification/generate_final_report.py september 2025 --run-all
```

### "Import errors"
```bash
# Install missing dependencies
pip3 install beautifulsoup4
```

## 📚 Further Reading

- **CLAUDE.md** - Project overview and core principles
- **action.sh** - Main report generation workflow
- **position_condition_matrix.json** - Business rules reference
- **integrated_dashboard_final.py** - Dashboard generation logic

## 🎓 Key Insights

**Why This Validation System Matters:**

1. **No Fake Data Policy** - Ensures all displayed data is real and accurate
2. **100% Rule Enforcement** - Critical business requirement validation
3. **Single Source of Truth** - Verifies CSV = Dashboard, no drift
4. **Progressive Incentive Accuracy** - Complex 12-month calculation validation
5. **Automated Quality Gates** - Catches errors before stakeholder review

**Common Issues Prevented:**
- 80-99% conditions_pass_rate receiving incentives (100% rule violation)
- Unapproved absence threshold errors (2 days, not 0)
- Actual working days calculation errors (Conditions 3-4)
- Personal AQL failure count mismatches (Condition 5)
- 3-month consecutive failure tracking errors (Conditions 6-7)
- Area reject rate calculation mistakes (Condition 8)
- 5PRS pass rate and quantity verification (Conditions 9-10)
- Progressive amounts not matching progression_table
- TYPE-3 employees receiving incentives (policy violation)
- Dashboard showing different data than CSV
- Continuous months not resetting on condition failure

**Time Savings:**
- Manual validation: ~4-6 hours per month
- Automated pipeline: ~5-10 minutes per month
- ROI: ~30-40x faster with 100% consistency
