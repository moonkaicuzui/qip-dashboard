# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QIP (Quality Inspection Process) Incentive Dashboard System - A comprehensive incentive calculation and visualization system for factory workers with Google Drive integration, JSON-based business rule configuration, and multi-language support (Korean, English, Vietnamese).

**System Purpose**: Calculate monthly incentives for quality inspection workers based on configurable business rules, generate interactive HTML dashboards with detailed analytics, and maintain historical tracking of performance metrics.

## Core Development Principles

### 1. No Fake Data Policy (절대 가짜 데이터 금지)
- **NEVER generate fake/dummy data under any circumstances**
- If data doesn't exist, display as empty, 0, or "데이터 없음"
- "우리사전에 가짜 데이타는 없다" - This is a fundamental principle
- When previous month data is missing, DO NOT generate estimates or random values

### 2. JSON-Driven Configuration (하드코딩 금지)
- **ALL business logic must be configured through JSON files**
- Never hardcode conditions, thresholds, or business rules in Python/JavaScript code
- Use `position_condition_matrix.json` for all condition definitions
- Any business rule change should only require JSON file updates, not code changes
- This ensures maintainability and flexibility without developer intervention

## Quick Reference

### File Structure Convention
- Input data: `input_files/[year]년 [month] 인센티브 지급 세부 정보.csv`
- Output Excel: `output_files/output_QIP_incentive_[month]_[year]_최종완성버전_v6.0_Complete.xlsx`
- Dashboard HTML: `output_files/Incentive_Dashboard_[year]_[MM]_Version_5.html`
- Config files: `config_files/config_[month]_[year].json`

### Month Naming Convention
- Korean files: Use Korean month names (e.g., "9월")
- English files: Use lowercase full names (e.g., "september")
- Config keys: Always lowercase (e.g., "september_2025")

## Key Commands

### One-Click Full Process
```bash
# Run complete incentive report generation (recommended)
./action.sh

# The action.sh script will:
# 1. Guide through month/year selection
# 2. Create config if needed
# 3. Sync with Google Drive
# 4. Convert attendance data
# 5. Calculate working days automatically
# 6. Validate HR data
# 7. Calculate incentives
# 8. Generate Excel/CSV outputs
# 9. Create both Incentive and Management dashboards
# 10. Optionally open dashboards in browser
```

### Individual Components
```bash
# Generate dashboard for specific month
python integrated_dashboard_final.py --month 9 --year 2025

# With Google Drive sync
python integrated_dashboard_final.py --month 9 --year 2025 --sync

# Step-by-step execution
python src/step0_create_monthly_config.py --month september --year 2025
python src/step1_인센티브_계산_개선버전.py --config config_files/config_september_2025.json
python src/step2_dashboard_version4.py --month september --year 2025

# Management dashboard with enhanced error detection
python generate_management_dashboard_v6_enhanced.py --month 9 --year 2025
```

### Testing and Validation
```bash
# Run all tests
./test_final.sh

# Validate dashboard output
python validate_dashboard.py

# Check position conditions
python verify_all_positions.py

# Verify LINE LEADER counts
python verify_line_leader_counts.py

# Test language switching
python test_language_switch.py

# Check dynamic month references
python verify_dynamic_month.py

# Validate HR data integrity
python src/validate_hr_data.py 9 2025

# Check Excel vs JSON consistency
python src/validate_excel_json_consistency.py \
    --excel "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv" \
    --json "config_files/assembly_inspector_continuous_months.json"

# Validate JSON consistency with code
python validate_json_consistency.py
```

## High-Level Architecture

### Key Architectural Decisions

1. **Single-File HTML Dashboards**: All data and JavaScript embedded inline for portability
2. **JSON-Driven Business Logic**: No business rules in code, only in JSON configuration files
3. **Stateless Processing**: Each month processed independently (except Assembly Inspector tracking)
4. **Fallback Design**: Google Drive sync optional - system works offline with local files
5. **Multi-Source Data Integration**: Combines incentive, attendance, AQL, and 5PRS data sources
6. **No External Dependencies for Viewing**: Dashboards use CDN-hosted libraries (Chart.js, Bootstrap)

### Processing Pipeline Flow
```
Google Drive → Input Files → Config Generation → Incentive Calculation → Dashboard Generation
                    ↓              ↓                    ↓                      ↓
              attendance/     monthly config      Excel/CSV output      HTML dashboards
              AQL history/    JSON rules          metadata JSON        (Incentive & Mgmt)
              5PRS data/
```

### Core Module Responsibilities

1. **Configuration Management** (`src/condition_matrix_manager.py`)
   - Loads and manages `position_condition_matrix.json`
   - Provides condition evaluation API for all business rules
   - Handles position-to-TYPE mapping dynamically

2. **Data Processing Pipeline**
   - `src/step0_create_monthly_config.py`: Monthly configuration generator
   - `src/step1_인센티브_계산_개선버전.py`: Main incentive calculation engine
   - `src/common_condition_checker.py`: Unified condition validation logic
   - `integrated_dashboard_final.py`: Primary dashboard generator with all features

3. **Google Drive Integration** (`src/google_drive_manager.py`)
   - Service account authentication
   - Automatic file synchronization
   - Fallback to manual mode if sync fails

4. **Data Validation Layer**
   - `src/validate_hr_data.py`: HR data integrity checks
   - `src/validate_excel_json_consistency.py`: Cross-format validation
   - `validate_json_consistency.py`: JSON-code consistency verification

### Business Logic Configuration System

The system uses JSON-based configuration to define all business rules, eliminating hardcoding:

1. **`config_files/position_condition_matrix.json`** - Master configuration defining:
   - All condition definitions (attendance, AQL, 5PRS, etc.)
   - Position-to-condition mapping by TYPE (TYPE-1, TYPE-2, TYPE-3)
   - Validation thresholds and rules
   - Special calculation cases (e.g., AQL_INSPECTOR)
   - Incentive amount ranges per TYPE

2. **`config_files/dashboard_translations.json`** - UI translations:
   - Korean, English, Vietnamese language support
   - Dynamic language switching in dashboards
   - All UI text elements including modals and tooltips

3. **`config_files/assembly_inspector_continuous_months.json`** - Historical tracking:
   - Continuous month counters for Assembly Inspectors
   - AQL failure tracking across months
   - Used for 3-month consecutive failure detection

4. **Monthly Config Files** (`config_files/config_[month]_[year].json`)
   - Generated by `step0_create_monthly_config.py`
   - Contains month-specific parameters and file paths
   - Working days (auto-calculated from attendance data)

### Data Flow Pipeline

1. **Data Input Sources**
   - Incentive files: `input_files/[year]년 [month] 인센티브 지급 세부 정보.csv`
   - Attendance data: `input_files/attendance/converted/` (after conversion)
   - AQL history: `input_files/AQL history/`
   - 5PRS data: `input_files/5prs data [month].csv`
   - Basic manpower: `input_files/basic manpower data [month].csv`

2. **Processing Steps**
   - **Step 0**: Config generation (`src/step0_create_monthly_config.py`)
   - **Step 0.5**: Google Drive sync (`src/auto_run_with_drive.py`)
   - **Step 0.7**: Attendance conversion (`src/convert_attendance_data.py`)
   - **Step 0.7.5**: Working days calculation (`src/calculate_working_days_from_attendance.py`)
   - **Step 1**: Incentive calculation (`src/step1_인센티브_계산_개선버전.py`)
   - **Step 1.5**: JSON generation from Excel (`src/generate_json_from_excel.py`)
   - **Step 2**: Dashboard generation (`integrated_dashboard_final.py`)
   - **Step 3**: Management dashboard (`generate_management_dashboard_v6_enhanced.py`)

3. **Output Files**
   - Excel: `output_files/output_QIP_incentive_[month]_[year]_최종완성버전_v6.0_Complete.xlsx`
   - CSV: Same name with .csv extension
   - HTML Dashboards:
     - Incentive: `output_files/Incentive_Dashboard_[year]_[MM]_Version_5.html`
     - Management: `output_files/management_dashboard_[year]_[MM].html`
   - Metadata: `output_files/output_QIP_incentive_[month]_[year]_metadata.json`
   - Dashboard data: `output_files/dashboard_data_from_excel.json`

### Critical Implementation Details

#### Dynamic Condition Evaluation
- All conditions are evaluated dynamically from `position_condition_matrix.json`
- Each employee gets a `condition_results` array with detailed evaluation results
- No hardcoded conditions - everything is configuration-driven
- Special handling for Assembly Inspector AQL tracking
- Conditions are grouped by TYPE (TYPE-1, TYPE-2, TYPE-3) for different validation rules

#### Previous Month Data Handling
- System attempts to load previous month data for comparison
- Automatic generation of missing July data (special case)
- If data doesn't exist, shows as 0 or empty (NO fake data generation)
- Important: "우리사전에 가짜 데이타는 없다" (No fake data in our dictionary)
- Historical data tracked in `assembly_inspector_continuous_months.json`

#### Assembly Inspector Special Logic
- Tracked for 3 consecutive months of AQL failures
- Continuous failure counter resets on AQL pass
- Automatic blocking after 3 consecutive failures
- Separate handling in `src/common_condition_checker.py`

#### JavaScript Generation in Python
- Dashboard HTML is generated with embedded JavaScript
- Template literals use f-strings - escape braces as `{{}}` to avoid syntax errors
- Chart.js instances must be destroyed before recreation to prevent animation bugs
- Use `updateAllTexts()` function to handle language switching for all UI elements
- Modal designs use unified CSS classes for consistency

#### Organization Chart (Org Chart Tab)
- Displays TYPE-1 manager hierarchy with incentive calculations
- Recursive team member finding using `boss_id` field
- Modal windows show calculation details and failure reasons
- Field normalization handles various column name formats (Direct_Manager_ID, boss_id, etc.)
- LINE LEADER counts must be consistent across all tabs

#### Type Classification
- TYPE-1: Management and specialized positions (100K-200K VND range)
- TYPE-2: Standard inspection positions (50K-100K VND range)
- TYPE-3: New QIP members (0 VND, no conditions required, policy excluded)

#### Modal Design System
- Unified blue gradient theme (#e3f2fd → #bbdefb)
- Dark blue title text (#1565c0) for readability
- Sticky table headers with gray background
- Hover effects with transform animations
- Bootstrap 5 badge classes (bg-primary, bg-danger, etc.)

### Google Drive Integration

The system includes Google Drive sync capabilities:
- Credentials: `credentials/service-account-key.json`
- Manager: `src/google_drive_manager.py`
- Auto-sync: `src/auto_run_with_drive.py`
- Diagnostic tool: `src/diagnose_google_drive.py`

### Common Issues and Solutions

1. **Template Literal Errors**: Ensure `{{}}` escaping in f-strings for JavaScript objects
2. **Chart Animation Bug**: Always destroy existing Chart.js instances before creating new ones
3. **Missing July Data**: System will auto-generate minimal July data for August calculations
4. **Condition Evaluation**: Check `position_condition_matrix.json` for position mapping
5. **Working Days Mismatch**: Verify attendance data conversion and calculation
6. **Modal White Text Issue**: Use unified modal CSS classes for consistent styling
7. **LINE LEADER Count Discrepancy**: Ensure consistent counting logic across all tabs (Overview, Org Chart)
8. **Language Switch Not Working**: Verify `updateAllTexts()` includes all new UI elements
9. **Attendance Rate = 0**: Check if working days calculation completed before incentive calculation
10. **Google Drive Sync Failure**: Verify `credentials/service-account-key.json` exists and is valid

### Language Support

The system provides full multi-language support (Korean, English, Vietnamese):
- Translation file: `config_files/dashboard_translations.json`
- Dynamic language switching via `changeLanguage()` function
- All UI elements including org chart and modals support translation
- Language preference persists in localStorage
- Month references must use dynamic variables (e.g., `dashboardMonth + '_incentive'`), never hardcoded

## Testing Strategy

### Comprehensive Testing
```bash
# Full system test
./test_final.sh

# Component-specific tests
python test_attendance_calculation.py  # Attendance rate validation
python test_modal_functionality.py     # Modal window interactions
python test_language_switching.py      # Multi-language support
python test_orgchart_browser.py       # Organization chart rendering
python test_aql_september.py          # AQL failure detection
```

### Validation Tools
- `validate_dashboard.py`: Dashboard output integrity
- `verify_all_positions.py`: Position-to-TYPE mapping validation
- `verify_line_leader_counts.py`: LINE LEADER consistency across tabs
- `validate_json_consistency.py`: JSON-code alignment verification

## Dependencies

Core: pandas>=1.3.0, numpy>=1.21.0, openpyxl>=3.0.9
Google Drive: gspread>=5.7.0, google-auth>=2.16.0
See `requirements.txt` for full list

## Development Notes

- Always preserve existing data integrity - never generate fake data
- Maintain JSON-driven configuration approach for all business rules
- Test thoroughly with `test_final.sh` before deployment
- Dashboard HTML includes all data inline - no external dependencies required for viewing
- Use `action.sh` for production runs - it handles the complete pipeline
- Validate all changes with `validate_json_consistency.py` to ensure JSON-code alignment
- Use `{{}}` escaping in f-strings when generating JavaScript template literals
- Always destroy Chart.js instances before recreation to prevent animation bugs
- Maintain unified modal CSS classes for consistent styling across all tabs