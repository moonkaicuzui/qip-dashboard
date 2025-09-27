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

## Key Commands

### Full Pipeline Execution
```bash
# Complete incentive report generation (RECOMMENDED)
./action.sh
# Guides through month/year selection, handles entire pipeline

# Version 6 dashboard with modular architecture
python dashboard_v2/generate_dashboard.py --month september --year 2025

# Version 5 dashboard (fallback if v6 has issues)
python integrated_dashboard_final.py --month 9 --year 2025
```

### Testing & Validation
```bash
./test_final.sh                        # Full system test
python quick_verify.py                  # Quick dashboard validation
python validate_json_consistency.py     # JSON-code alignment check
python src/validate_hr_data.py 9 2025  # HR data integrity
```

### Debugging Tools
```bash
python simple_deep_test.py             # Browser-based dashboard testing
python deep_verification.py             # Comprehensive functionality check
```

## High-Level Architecture

### Dashboard Versions
- **Version 5** (`integrated_dashboard_final.py`): Stable single-file dashboard
- **Version 6** (`dashboard_v2/`): Modular architecture for maintainability
  - `modules/complete_renderer.py`: HTML generation with NaN handling
  - `modules/incentive_calculator.py`: Core calculation logic
  - `static/js/dashboard_complete.js`: Frontend logic (9000+ lines)

### Critical Data Flow
```
Input Files → Config Generation → Incentive Calculation → Dashboard Generation
     ↓              ↓                    ↓                      ↓
attendance/    position_matrix     Excel/CSV output      HTML dashboards
AQL/5PRS       JSON rules          metadata JSON         (self-contained)
```

### File Naming Conventions
- Input: `input_files/[year]년 [month] 인센티브 지급 세부 정보.csv`
- Output: `output_files/Incentive_Dashboard_[year]_[MM]_Version_[5|6].html`
- Config: `config_files/config_[month]_[year].json`
- Korean months: "9월" | English: "september" | Config keys: lowercase

## Business Logic Configuration

### Core JSON Files
1. **`position_condition_matrix.json`** - Master business rules:
   - All conditions (attendance, AQL, 5PRS)
   - Position→TYPE mapping (TYPE-1/2/3)
   - Incentive amount ranges

2. **`dashboard_translations.json`** - UI translations:
   - Korean/English/Vietnamese support
   - Dynamic language switching

3. **`assembly_inspector_continuous_months.json`** - Historical tracking:
   - 3-month consecutive AQL failure detection
   - Continuous month counters

### Employee TYPE Classification
- **TYPE-1**: Management (100K-200K VND)
- **TYPE-2**: Standard inspectors (50K-100K VND)
- **TYPE-3**: New members (0 VND, policy excluded)

## Common Issues & Solutions

### JavaScript/Dashboard Issues
1. **NaN in JavaScript**: dashboard_v2 converts Python NaN → JS NaN in `complete_renderer.py`
2. **Template literal errors**: Escape braces as `{{}}` in Python f-strings
3. **Chart.js bugs**: Always destroy existing instances before recreation
4. **Syntax errors at line 9267**: Fixed in dashboard_v2/static/js/dashboard_complete.js

### Position Modal Issues (Fixed Sep 27, 2025)
1. **TYPE-2 Condition Mapping**:
   - **Issue**: TYPE-2 employees incorrectly showed conditions 5-8 (AQL conditions)
   - **Fix**: Updated `dashboard_complete.js:8818` to map TYPE-2 to `[1, 2, 3, 4]` only (출근 조건만)
   - **Reference**: `position_condition_matrix.json` defines TYPE-2 should only have attendance conditions

2. **Statistics Mismatch**:
   - **Issue**: Condition Fulfillment table showed 0 for all conditions
   - **Fix**: Updated field name mappings in `dashboard_complete.js:8866-8919` to match Excel column names
   - **Key fields**: `Attendance Rate`, `Unapproved Absences`, `Actual Working Days`, `Total Working Days`

3. **Employee Details Status**:
   - **Issue**: Condition badges not displaying correctly
   - **Fix**: Removed TYPE-2 specific logic for conditions 5-8 at `dashboard_complete.js:8978`

### Data Processing Issues
1. **Working days = 0**: Run attendance calculation before incentive calculation
2. **Missing previous month**: System shows 0 (never generates fake data)
3. **Assembly Inspector tracking**: Check `assembly_inspector_continuous_months.json`
4. **LINE LEADER counts**: Ensure consistent logic across tabs

### Version 6 Specific
- If dashboard shows 0 values: Check NaN serialization in `complete_renderer.py`
- If tabs don't work: Verify JavaScript syntax in `dashboard_complete.js`
- Use `integrated_dashboard_final.py` as fallback if v6 fails

## Testing Dashboard Changes

```bash
# After modifying dashboard code:
python dashboard_v2/generate_dashboard.py --month september --year 2025
python quick_verify.py  # Check for errors
python simple_deep_test.py  # Visual browser test

# If issues persist, use Version 5:
python integrated_dashboard_final.py --month 9 --year 2025
```

## Dependencies

```
pandas>=1.3.0, numpy>=1.21.0, openpyxl>=3.0.9
playwright (for testing), gspread>=5.7.0 (Google Drive)
```

## Development Notes

- Dashboard HTML is self-contained with inline data/JS/CSS
- action.sh updated to use `integrated_dashboard_final.py` (was dashboard_v2)
- Position Details modal requires proper 5PRS/AQL field mapping
- Language switching updates ALL elements via `updateAllTexts()`
- Modal CSS uses unified Bootstrap 5 classes for consistency