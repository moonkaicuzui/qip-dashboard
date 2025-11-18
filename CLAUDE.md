# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QIP (Quality Inspection Process) Incentive Dashboard System - Factory worker incentive calculation with interactive dashboards, Google Drive sync, and multi-language support (Korean/English/Vietnamese).

## Core Development Principles

### 1. No Fake Data Policy (절대 가짜 데이터 금지)
- **NEVER generate fake/dummy data** - display empty, 0, or "데이터 없음"
- "우리사전에 가짜 데이타는 없다" - fundamental principle
- When previous month data missing, DO NOT generate estimates

### 2. JSON-Driven Configuration (하드코딩 금지)
- **ALL business logic in JSON files** - never hardcode conditions/thresholds
- Use `position_condition_matrix.json` for all condition definitions
- Business rule changes require only JSON updates, not code changes

### 3. 100% Condition Fulfillment Rule (100% 조건 충족 필수)
- **Incentives ONLY for 100% condition pass rate** - no partial incentives
- 80-99% fulfillment = NO incentive (인센티브 지급조건을 100% 충족하지 못하는 경우는 인센티브를 받으면 안됨)
- This is a strict business requirement - never apply thresholds like 80%

### 4. Resigned Employee Exclusion (퇴사자 제외 정책)
- **Employees who resigned before the calculation month are excluded from subordinate mappings**
- Affects LINE LEADER, SUPERVISOR, and other manager incentive calculations
- Resignation date check: `Stop working Date < month_start` → excluded from subordinate count
- Example: September calculation excludes employees who resigned before 2025-09-01
- Implementation: `src/step1_인센티브_계산_개선버전.py:3146-3156` (create_manager_subordinate_mapping)

## Key Commands

### Complete Workflow Execution
```bash
# One-command full pipeline (RECOMMENDED)
./action.sh
# Guides through month/year selection, handles:
#   1. Config generation
#   2. Google Drive sync
#   3. Attendance calculation
#   4. Incentive calculation
#   5. Dashboard generation
#   6. Optional data validation

# Standalone validation pipeline
./run_full_validation.sh
# Validates all 10 conditions, incentive amounts, dashboard consistency
```

### Dashboard Generation
```bash
# Version 8 (Current - single-file, stable)
python integrated_dashboard_final.py --month 9 --year 2025

# Version 6 (Modular architecture, maintenance mode)
python dashboard_v2/generate_dashboard.py --month september --year 2025
```

### Data Validation (NEW)
```bash
# Complete validation suite
./run_full_validation.sh

# Individual validators
python scripts/verification/validate_condition_evaluation.py september 2025
python scripts/verification/validate_incentive_amounts.py september 2025
python scripts/verification/validate_dashboard_consistency.py september 2025

# Integrated report generation
python scripts/verification/generate_final_report.py september 2025 --run-all
```

### Consecutive AQL Failure Update
```bash
# Auto-detect from latest config
python src/update_continuous_fail_column.py

# Specify month/year
python src/update_continuous_fail_column.py --month november --year 2025
```

### HR Data Validation
```bash
# Validate position mappings and data integrity
python src/validate_hr_data.py 9 2025
```

## High-Level Architecture

### Data Flow Pipeline
```
[1] Input Files                [2] Config Generation
├── attendance CSV             ├── position_condition_matrix.json (master rules)
├── AQL history CSV            └── config_[month]_[year].json (working_days, etc)
├── 5PRS data CSV                     ↓
└── Basic info CSV             [3] Incentive Calculation (step1_인센티브_계산_개선버전.py)
       ↓                       ├── Evaluate 10 conditions (YES/NO)
[src/auto_run_with_drive.py]  ├── Calculate continuous_months (0-15)
[src/sync_previous_incentive]  ├── Determine TYPE (1/2/3)
[src/convert_attendance_data]  └── Assign final incentive amount
                                       ↓
                               [4] Excel/CSV Output
                               ├── output_QIP_incentive_[month]_[year]_Complete_V9.0_Complete.xlsx
                               └── output_QIP_incentive_[month]_[year]_Complete_V9.0_Complete.csv
                                       ↓
                               [5] Dashboard Generation (integrated_dashboard_final.py)
                               ├── Self-contained HTML with inline JS/CSS
                               ├── Chart.js visualizations
                               └── Multi-language support (KO/EN/VN)
                                       ↓
                               [6] Data Validation (NEW - scripts/verification/)
                               ├── validate_condition_evaluation.py (10 conditions)
                               ├── validate_incentive_amounts.py (TYPE-1/2/3 logic)
                               ├── validate_dashboard_consistency.py (CSV vs Dashboard)
                               └── generate_final_report.py (integrated Excel report)
```

### Dashboard Versions
- **Version 8** (`integrated_dashboard_final.py`): Current production version, single-file, stable
  - Self-contained HTML (3.5-5.7MB)
  - Inline JavaScript with Chart.js
  - Bootstrap 5 modals

- **Version 6** (`dashboard_v2/`): Modular architecture (maintenance mode)
  - `modules/complete_renderer.py`: HTML generation with NaN handling
  - `modules/incentive_calculator.py`: Core calculation logic
  - `static/js/dashboard_complete.js`: Frontend logic (9000+ lines)

### 10 Conditions System
Defined in `position_condition_matrix.json`:

**Conditions 1-4: Attendance (출근)**
1. Attendance Rate >= 88%
2. Unapproved Absence <= 2 days
3. Actual Working Days > 0
4. Minimum Working Days >= 12

**Conditions 5-8: AQL Quality (품질)**
5. Personal AQL Failure = 0 (당월)
6. Personal AQL: No 3-month Consecutive Failures
7. Team/Area AQL: No 3-month Consecutive Failures
8. Area Reject Rate < 3%

**Conditions 9-10: 5PRS Inspection (검사)**
9. 5PRS Pass Rate >= 95%
10. 5PRS Inspection Quantity >= 100

### Employee TYPE Classification
- **TYPE-1 Progressive**: ASSEMBLY INSPECTOR, MODEL MASTER, AUDITOR & TRAINER
  - Progression table: 1월=150K → 12월=1,000K VND
  - Continuous months accumulation (0-15)
  - Reset to 0 if any condition fails

- **TYPE-2 Standard**: LINE LEADER and similar positions
  - Uses TYPE-1 position average (NOT fixed 50K-300K range)
  - Must meet 100% condition pass rate

- **TYPE-3 New Members**: Policy excluded
  - Always 0 VND regardless of conditions

### LINE LEADER Incentive Calculation
- **Formula**: `(Total Subordinate Incentive) × 12% × Receiving Ratio`
- **Receiving Ratio**: `(Subordinates with incentive > 0) / (Total active subordinates)`
- **Subordinate Count**: Excludes employees who resigned before calculation month
- **Example**:
  - 14 active subordinates (1 resigned before Sept excluded)
  - 5 subordinates received incentive (total ₫2,300,000)
  - Calculation: ₫2,300,000 × 12% × (5/14) = ₫98,571
- **Implementation**: `src/step1_인센티브_계산_개선버전.py:3255-3323`

## Business Logic Configuration

### Core JSON Files

**`config_files/position_condition_matrix.json`** (MASTER RULES)
- 10 conditions definitions with thresholds
- Position → TYPE mapping (64 position codes)
- Applicable conditions per position
- Progressive incentive table (12 months)
- TYPE-2 mapping to TYPE-1 positions

**`config_files/config_[month]_[year].json`**
- Monthly working days
- File paths for attendance/AQL/5PRS data
- Configuration parameters

**`config_files/assembly_inspector_continuous_months.json`**
- Historical continuous months tracking
- Previous month incentive data
- Carry-over logic

**`dashboard_translations.json`**
- Korean/English/Vietnamese translations
- Dynamic language switching

### File Naming Conventions
```
Input:  input_files/[year]년 [month] 인센티브 지급 세부 정보.csv
        input_files/attendance/출근부_september_2025.csv
        input_files/AQL history/9월_AQL_HISTORY.csv
        input_files/5PRS/9월_5PRS_DATA.csv

Output: output_files/output_QIP_incentive_september_2025_Complete_V9.0_Complete.xlsx
        output_files/output_QIP_incentive_september_2025_Complete_V9.0_Complete.csv
        output_files/Incentive_Dashboard_2025_09_Version_9.0.html

Config: config_files/config_september_2025.json

Reports: validation_reports/INTEGRATED_VALIDATION_REPORT_september_2025_[timestamp].xlsx
```

## Data Validation System (NEW)

### Validation Architecture
**Single Source of Truth Validation**:
```
Original Data Sources → Python Calculation → Excel Output → Dashboard Display
        ↓                      ↓                   ↓              ↓
   (validate_condition_evaluation)  (validate_incentive_amounts)  (validate_dashboard_consistency)
```

### What Gets Validated

**validate_condition_evaluation.py**
- Recalculates all 10 conditions from source data
- Compares with Excel output conditions (YES/NO)
- Validates 100% rule enforcement
- Full validation (all employees, no sampling)

**validate_incentive_amounts.py**
- TYPE-1: Validates against progression_table
- TYPE-2: Validates 100% rule + TYPE-1 average usage
- TYPE-3: Validates 0 VND policy
- Continuous months: Validates increment/reset logic

**validate_dashboard_consistency.py**
- Validates Dashboard HTML vs CSV exact match
- KPI summary statistics
- Individual employee data (all fields)
- All 10 condition fields

**generate_final_report.py**
- Aggregates all validation results
- Priority-ordered action items (CRITICAL/ERROR/WARNING)
- Comprehensive Excel report with recommendations

### Running Validation

**Integrated into action.sh** (Recommended):
```bash
./action.sh
# After dashboard generation, prompted: "Run automated data validation? (y/n)"
# Choose 'y' → automatic validation → option to open report
```

**Standalone**:
```bash
./run_full_validation.sh
# Interactive year/month selection → runs all 4 validators → integrated report
```

**Exit Codes**:
- 0 = No issues detected
- 1 = Findings detected, review reports

## Common Issues & Solutions

### TYPE-2 Calculation Logic
**CRITICAL**: TYPE-2 does NOT use fixed 50K-300K range
- TYPE-2 uses TYPE-1 position average
- Example: LINE LEADER (TYPE-2) gets LINE LEADER (TYPE-1) average
- Only validates 100% rule compliance
- Reference: `src/step1_인센티브_계산_개선버전.py:3478-3571`

### Condition Thresholds
- **Condition 2**: <= 2 days (NOT = 0)
- **100% Rule**: ALL applicable conditions must pass (not 80% or 90%)
- **Continuous Months**: Resets to 0 when any condition fails

### JavaScript/Dashboard Issues
1. **NaN handling**: Python NaN → JavaScript NaN in `complete_renderer.py`
2. **Bootstrap 5 Modals**: Use `new bootstrap.Modal(element).show()` not jQuery
3. **Template literals**: Escape braces as `{{}}` in Python f-strings
4. **Chart.js**: Always destroy existing instances before recreation

### Position Modal Issues (Fixed)
- **TYPE-2 Condition Mapping**: Shows only conditions [1, 2, 3, 4] (attendance)
  - Reference: `dashboard_complete.js:8818`
  - `position_condition_matrix.json` defines per-position conditions

- **Field Name Mappings**: Must match Excel column names exactly
  - `Attendance Rate`, `Unapproved Absences`, `Actual Working Days`, `Total Working Days`

### Data Processing Issues
1. **Working days = 0**: Run attendance calculation before incentive calculation
2. **Missing previous month**: System shows 0 (never fake data)
3. **MODEL MASTER**: Position code 'D' must be in position_condition_matrix.json
4. **Consecutive AQL Failure**: Run update_continuous_fail_column.py before dashboard
5. **LINE LEADER Expected vs Actual mismatch**:
   - Check if resigned employees are properly excluded from subordinate count
   - Verify subordinate mapping in `create_manager_subordinate_mapping()`
   - Dashboard and calculation script must use same subordinate filtering logic

### Debugging Dashboard Issues
```bash
# After modifying dashboard code
python integrated_dashboard_final.py --month 9 --year 2025
./run_full_validation.sh  # Validate changes

# If dashboard shows 0 values
# → Check NaN serialization in complete_renderer.py (Version 6)
# → Check data file paths in config_[month]_[year].json

# If validation fails
# → Check validation_reports/INTEGRATED_VALIDATION_REPORT_*.xlsx
# → Focus on "조치 항목 (우선순위)" sheet for action items
```

## Testing

```bash
# Full system test (if exists)
./test_final.sh

# Validation test suite
./run_full_validation.sh

# Legacy test scripts (in scripts/legacy/)
python scripts/legacy/simple_deep_test.py      # Browser-based dashboard test
python scripts/legacy/quick_verify.py          # Quick dashboard validation
```

## Dependencies

```
Python 3.9+
pandas>=1.3.0
numpy>=1.21.0
openpyxl>=3.0.9
beautifulsoup4>=4.9.3  # For dashboard validation
playwright           # For testing
gspread>=5.7.0      # For Google Drive
```

## Project Organization

```
/                                    # Root (clean - only 6 essential files)
├── action.sh                        # Main execution script
├── run_full_validation.sh           # Validation pipeline
├── integrated_dashboard_final.py    # Dashboard generator (Version 8)
├── CLAUDE.md                        # This file
├── README.md                        # Project documentation
└── .gitignore

/src/                                # Core business logic (25 modules)
├── step0_create_monthly_config.py
├── step1_인센티브_계산_개선버전.py    # Main calculation engine
├── update_continuous_fail_column.py
├── validate_hr_data.py
└── ...

/scripts/verification/               # Data validation system (NEW)
├── validate_condition_evaluation.py
├── validate_incentive_amounts.py
├── validate_dashboard_consistency.py
└── generate_final_report.py

/scripts/legacy/                     # Legacy/backup scripts
/docs/                               # Documentation
/dashboard_v2/                       # Modular dashboard (Version 6)
/config_files/                       # JSON configuration
/input_files/                        # Source data
/output_files/                       # Generated reports/dashboards
/validation_reports/                 # Validation Excel reports
```

## Version Management & Backward Compatibility

### Current Version: 9.0

**Critical Architecture Decision**: The system implements **fallback pattern** for version transitions to ensure backward compatibility when reading previous month data.

### Version Update Requirements

When updating version numbers (e.g., 9.0 → 9.1), you MUST update these files:

**Tier 1 - Core Calculation Engine**:
1. **`src/step1_인센티브_계산_개선버전.py`** (7 locations)
   - Lines 1209-1213: Previous month file loading with fallback pattern
   - Lines 2260-2270: Ensure previous month exists with fallback
   - Line 2333: Auto-generated previous month output path
   - Line 5126: CSV output filename
   - Line 5136: Excel output filename
   - Line 6712: Console version message

2. **`integrated_dashboard_final.py`** (8 locations)
   - Line 151: CSV file pattern for data loading
   - Line 5951: HTML title version badge
   - Line 9097: JavaScript language switcher version badge
   - Lines 15739-15744: CSV file loading logic with comments
   - Line 15866: HTML output filename

3. **`action.sh`** (5 locations)
   - Line 413, 427: Validation script Excel file parameters
   - Line 455-456: Dashboard generation description and DASHBOARD_VERSION variable
   - Lines 518-519: Completion message file paths

**Tier 2 - Verification Scripts**:
4. **`scripts/verification/`** (5 files)
   - `validate_incentive_amounts.py`: Line 51
   - `validate_condition_evaluation.py`: Lines 64-65
   - `validate_dashboard_consistency.py`: Lines 42, 60 (CRITICAL - must match dashboard filename)
   - `generate_simple_validation_report.py`: Line 24
   - `analyze_october_data.py`: Line 26

5. **`src/update_continuous_fail_column.py`**
   - Lines 257-258: Primary file pattern (with fallback to older versions)

**Tier 3 - Documentation**:
6. **`README.md`** and **`CLAUDE.md`**
   - Update all version references in examples and file paths

### Backward Compatibility Pattern (CRITICAL)

**Problem**: When December 2025 (V9.0) needs November 2025 data, but November was generated with V8.02.

**Solution**: Fallback pattern in `step1_인센티브_계산_개선버전.py`:

```python
# Lines 1214-1220: Previous month file loading
excel_patterns = [
    # Try current version first
    f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
    f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
    # Fallback to previous versions (backward compatibility)
    f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv",
    f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv"
]
```

**Why This Matters**:
- Month 1 (V9.0): Reads Month 0 (V8.02) - SUCCESS with fallback
- Month 2 (V9.0): Reads Month 1 (V9.0) - SUCCESS with primary pattern
- Without fallback: Month 1 calculation would FAIL

### Common Version Update Pitfalls

1. **Filename Mismatch in Validators**:
   - Bug: `validate_dashboard_consistency.py` looking for "Version_9.0.html" but generator creates different version
   - Impact: All dashboard validation fails silently
   - Fix: Line 60 must match `integrated_dashboard_final.py` line 15866

2. **Missing Fallback Pattern**:
   - Impact: Cannot read previous month files during version transitions
   - Fix: Always maintain fallback to previous version in file loading logic

3. **Incomplete Updates**:
   - Impact: Mixed version references cause confusion and validation failures
   - Fix: Use comprehensive grep search to find all references

### Version Update Validation Checklist

After version update, verify:
```bash
# 1. Check all V8.XX references updated
grep -r "V8\\.0[0-9]" . --exclude-dir=.git --include="*.py" --include="*.sh"

# 2. Verify fallback patterns include previous version
grep -A 5 "excel_patterns\|prev_file_patterns" src/step1_인센티브_계산_개선버전.py

# 3. Test file generation
./action.sh  # Select a test month

# 4. Verify output filenames
ls output_files/*Complete_V8*

# 5. Run validation suite
./run_full_validation.sh
```

## Development Notes

- Dashboard HTML is self-contained (3.5-5.7MB) with inline data/JS/CSS
- action.sh uses `integrated_dashboard_final.py` (Version 8)
- Position Details modal requires proper 5PRS/AQL field mapping
- Language switching updates ALL elements via `updateAllTexts()`
- Modal CSS uses unified Bootstrap 5 classes
- Validation system integrated into monthly workflow (optional step in action.sh)
- All backup files excluded from git (.gitignore: *.backup, *backup*.py)
