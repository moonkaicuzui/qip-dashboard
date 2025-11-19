# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QIP (Quality Inspection Process) Incentive Dashboard System - **Real-time Internet Web-based Incentive Dashboard** with automatic updates, factory worker incentive calculation, interactive dashboards, Google Drive sync, and multi-language support (Korean/English/Vietnamese).

## 🌐 Web Deployment Information

**CRITICAL**: This is a **GitHub Pages web deployment project**, NOT a local HTML file generator.

### Official Web URL (Production)
```
https://moonkaicuzui.github.io/qip-dashboard/
```

**Access Method:**
1. Open web browser (Chrome, Safari, Firefox, Edge - mobile or desktop)
2. Navigate to the URL above
3. Internet connection required
4. Authentication required (password protection)

### Web Pages
- **Selector**: https://moonkaicuzui.github.io/qip-dashboard/selector.html
- **November 2025**: https://moonkaicuzui.github.io/qip-dashboard/Incentive_Dashboard_2025_11_Version_9.0.html
- **October 2025**: https://moonkaicuzui.github.io/qip-dashboard/Incentive_Dashboard_2025_10_Version_9.0.html

### Automatic Deployment System
**GitHub Actions Workflow**: `.github/workflows/auto-update.yml`
- **Frequency**: Hourly automatic execution (Cron: `0 * * * *`)
- **Process**:
  1. Google Drive sync (latest data)
  2. Incentive calculation
  3. Dashboard HTML generation
  4. Selector page regeneration
  5. Git commit & push
  6. GitHub Pages auto-deploy (1-2 min)

### Local Files vs Web Deployment
| Aspect | Web Deployment (Production) | Local Files (Development) |
|--------|---------------------------|-------------------------|
| **Access** | Web browser + Internet | File explorer |
| **URL** | `https://ksmooncoding.github.io/...` | `file:///Users/...` |
| **Update** | GitHub Actions (hourly) | Manual script execution |
| **Purpose** | End-user access | Development & testing |
| **Location** | `/docs` folder (GitHub Pages) | Entire project |

**IMPORTANT**: When users ask for "웹주소" (web address), provide the `https://` URL, NOT `file:///` paths.

### Detailed Documentation
See `PROJECT_IDENTITY_WEB_DASHBOARD.md` for comprehensive web deployment architecture.

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

### 5. Deployment and Documentation Workflow (배포 및 문서화 필수 원칙)
**MANDATORY FOR ALL PROJECT WORK** - Every code change MUST follow this complete workflow:

#### Step 1: Code Changes
- Make necessary code modifications
- Test locally to verify functionality
- Never skip testing before deployment

#### Step 2: File Regeneration (if applicable)
- Regenerate affected files after code changes
- Dashboard code change → Regenerate dashboard HTML
- Selector code change → Regenerate selector.html
- Calculation logic change → Recalculate incentive data
- **Example**: `python integrated_dashboard_final.py --month 11 --year 2025`

#### Step 3: Web Deployment (CRITICAL)
**Copy latest files to `/docs` folder for GitHub Pages:**
```bash
# Dashboard HTML
cp output_files/Incentive_Dashboard_2025_11_Version_9.0.html docs/

# Selector page (if changed)
cp docs/selector.html docs/

# Any other web-accessible files
```
**Why**: `/docs` folder is GitHub Pages root - files MUST be here for web access

#### Step 4: Documentation Update (MANDATORY)
**Update CLAUDE.md with:**
- Problem description and root cause
- Solution implemented with file/line references
- Verification steps performed
- Commit hash for future reference
- Prevention measures for similar issues

**Example documentation format:**
```markdown
X. **[Issue Name]** (FIXED: YYYY-MM-DD):
   - **Problem**: Clear description of the issue
   - **Root Cause**: Technical explanation
   - **Solution**: Code changes made (file:line)
   - **Verification**: How it was tested
   - **Commit**: [commit_hash]
   - **Prevention**: How to avoid in future
```

#### Step 5: Git Commit and Push (ALWAYS)
```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "fix: [brief description]

- Detailed change 1
- Detailed change 2
- Updated documentation in CLAUDE.md"

# Push to GitHub (triggers GitHub Pages deployment)
git push origin main
```

**Important Git Notes:**
- Use `git pull --rebase origin main` before push if needed
- Resolve conflicts carefully (prefer `--ours` for auto-generated files)
- Never force push without explicit user permission
- GitHub Pages deploys automatically within 1-2 minutes after push

#### Step 6: Web Verification (FINAL CHECK)
**Verify changes are live on web:**
1. Wait 2 minutes for GitHub Pages deployment
2. Open browser in incognito/private mode
3. Navigate to production URL: `https://moonkaicuzui.github.io/qip-dashboard/`
4. Verify changes are visible on live site
5. Test affected functionality in browser

**Common verification checks:**
- Language switcher shows correct text
- CSV download contains data
- Dashboard displays correct values
- Selector page shows all months
- Mobile responsive layout works

#### Workflow Summary Checklist
- [ ] Code changes completed and tested locally
- [ ] Files regenerated (if applicable)
- [ ] Latest files copied to `/docs` folder
- [ ] CLAUDE.md updated with comprehensive documentation
- [ ] Git add, commit with descriptive message
- [ ] Git push to GitHub (handle conflicts if needed)
- [ ] Wait 2 minutes for GitHub Pages deployment
- [ ] Verify changes live on web URL
- [ ] Confirm all functionality works in browser

**Rationale**: This workflow ensures:
1. No confusion from outdated files
2. Complete documentation for future work
3. Web deployment always reflects latest code
4. All changes are version-controlled
5. Issues can be traced and prevented

**NEVER skip any step** - incomplete workflows cause confusion and rework.

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
                               [6] Data Validation (scripts/verification/)
                               ├── validate_condition_evaluation.py (10 conditions)
                               ├── validate_incentive_amounts.py (TYPE-1/2/3 logic)
                               ├── validate_dashboard_consistency.py (CSV vs Dashboard)
                               └── generate_final_report.py (integrated Excel report)
                                       ↓
                               [7] Web Deployment (GitHub Pages)
                               ├── Copy outputs to /docs folder
                               ├── Regenerate selector.html (create_month_selector.py)
                               ├── Git commit & push
                               └── GitHub Pages auto-deploy → https://moonkaicuzui.github.io/qip-dashboard/
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
**CRITICAL**: TYPE-2 does NOT use fixed 50K-300K range - Each position has specific calculation method

**LINE LEADER (TYPE-2)**: Special subordinate-based formula
- Formula: `(Total Subordinate Incentive) × 12% × Receiving Ratio`
- Receiving Ratio: `(Subordinates with incentive > 0) / (Total active subordinates)`
- NOT based on TYPE-1 average like other TYPE-2 positions
- Reference: `src/step1_인센티브_계산_개선버전.py:3255-3323`

**GROUP LEADER (TYPE-2)**: Based on LINE LEADER (TYPE-1) average
- Primary: TYPE-1 LINE LEADER average × 2
- Fallback (if TYPE-1 avg = 0): TYPE-2 LINE LEADER average × 2
- Reference: `src/step1_인센티브_계산_개선버전.py:4070-4165`

**Other TYPE-2 positions**: Use corresponding TYPE-1 position average
- (V) SUPERVISOR → TYPE-1 (V) SUPERVISOR average
- A.MANAGER → TYPE-1 A.MANAGER average
- STITCHING INSPECTOR → TYPE-1 ASSEMBLY INSPECTOR average
- Only validates 100% rule compliance (conditions 1-4: attendance)

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

6. **Continuous Months Calculation Priority Order** (FIXED: 2025-11-19):
   - **Problem**: October V9.1 file contained corrupted `Next_Month_Expected` values
     - Example: Employee 621040446 had `Next_Month_Expected: 2` (wrong) vs `Continuous_Months: 12` (correct)
     - Old priority read `Next_Month_Expected` first → returned wrong value (2)
   - **Solution**: Priority order changed in `calculate_continuous_months_from_history()` (Lines 1066-1123)
     - **NEW Priority 1**: `Continuous_Months + 1` (most reliable - mathematically sound)
     - **NEW Priority 2**: `Next_Month_Expected` (fallback only - can contain errors)
     - **Priority 3**: Reverse calculation from incentive amount (last resort)
   - **Why Continuous_Months + 1 is more reliable**:
     - Direct calculation from validated monthly data
     - No intermediate computation that can introduce errors
     - Mathematically verifiable: if October = 12 and all conditions pass → November = 13
   - **Why Next_Month_Expected can be unreliable**:
     - Pre-calculated value that can be corrupted during data processing
     - Subject to errors in previous month's calculation logic
     - Not validated against actual monthly conditions
   - **Implementation**: `src/step1_인센티브_계산_개선버전.py:1062-1131`
   - **Verification**: Employee 621040446 now correctly shows 13 months → 1,000,000 VND

7. **Language Switcher - Korean Date Format Visibility** (FIXED: 2025-11-19):
   - **Problem 1**: English/Vietnamese selected, but "2025년 11월" (Korean format) still visible
   - **Root Cause 1**: `month-year` div with hardcoded "YYYY년 MM월" format always displayed
     - Korean translations: `month-11: "11월"` (needs separate year display)
     - English translations: `month-11: "November 2025"` (already includes year)
     - Vietnamese translations: `month-11: "Tháng 11 năm 2025"` (already includes year)
   - **Solution 1**: Added `data-lang-show="ko"` attribute to hide Korean-specific elements
     - Line 275: Added `data-lang-show="ko"` to `month-year` div
     - Lines 456-464: Added language-specific visibility logic in `switchLanguage()`
   - **Commit**: `45c22f4` (2025-11-19)

   - **Problem 2**: English shows "November" only (year missing), Vietnamese shows "Tháng 11" only
   - **Root Cause 2**: Translation override bug in `switchLanguage()` function
     - Lines 434-439: Sets `month-name` to "November 2025" via `data-i18n="month-11"` ✅
     - Lines 441-448: Overrides with `months[11]` = "November" (year lost) ❌
   - **Solution 2**: Modified Lines 441-448 to skip if `data-i18n` attribute exists
     - Added `!monthNameElement.hasAttribute('data-i18n')` condition
     - Prevents second translation from overriding first translation
   - **How it works**:
     - Korean: Shows "2025년 11월" + "11월" ✅
     - English: Shows "November 2025" (not overridden) ✅
     - Vietnamese: Shows "Tháng 11 năm 2025" (not overridden) ✅
   - **Pattern for future use**: Use `data-i18n="[key]"` for specific translations, `data-lang-show="[lang]"` for visibility
   - **Implementation**: `docs/selector.html:275, 441-451`, `scripts/create_month_selector.py:530-540`
   - **Commit**: `775e48c` (2025-11-19)

8. **CSV Download Empty File Bug** (FIXED: 2025-11-19):
   - **Problem**: CSV download button returns empty file (header only, no data)
   - **User Impact**: Unable to download employee data from dashboard
   - **Root Cause**: Variable name mismatch in downloadCSV() function
     - Dashboard defines: `window.employeeData` (singular)
     - Download function uses: `employeesData` (plural - incorrect)
     - Result: `typeof employeesData` is undefined → no data written to CSV
   - **Solution**: Changed `employeesData` to `employeeData` in CSV download function
     - Line 9807-9809 in `integrated_dashboard_final.py`
     - Added comment: "employeeData 배열 사용 (단수형 - window.employeeData와 일치)"
   - **Verification Steps**:
     1. Regenerate dashboard: `python integrated_dashboard_final.py --month 11 --year 2025`
     2. Check HTML: `grep "typeof employee" output_files/Incentive_Dashboard_2025_11_Version_9.0.html`
     3. Expected: `typeof employeeData` (singular) ✅
   - **Data Consistency Verified**:
     - CSV, Excel, Dashboard all show identical values ✅
     - October incentive: `Previous_Month_Incentive` column
     - November incentive: `November_Incentive` column
     - Total: 115,654,952 VND (350 employees receiving)
   - **Implementation**: `integrated_dashboard_final.py:9807-9809`
   - **Commit**: `45c0f9d` (2025-11-19)
   - **Prevention**: Always verify variable names match between definition and usage

9. **TYPE-2 Incentive Calculation Method Display Error** (FIXED: 2025-11-19):
   - **Problem**: Dashboard "인센티브 기준" tab showing incorrect calculation methods for TYPE-2 positions
     - GROUP LEADER showed: "GROUP LEADER 평균" (incorrect)
     - LINE LEADER showed: "LINE LEADER 평균" (incorrect)
   - **User Impact**: Misleading information about how TYPE-2 incentives are calculated
   - **Root Cause**: Hardcoded table in dashboard HTML with outdated calculation method descriptions
     - Lines 7074-7083 in `integrated_dashboard_final.py`
     - Table did not reflect actual calculation logic used in `step1_인센티브_계산_개선버전.py`
   - **Correct Calculation Methods**:
     - **GROUP LEADER (TYPE-2)**: TYPE-1 LINE LEADER average × 2 (NOT GROUP LEADER average)
     - **LINE LEADER (TYPE-2)**: Subordinate incentive total × 12% × receiving ratio (NOT simple average)
   - **Solution**: Updated TYPE-2 calculation method table
     - Line 7073-7078: GROUP LEADER row updated
       - "참조 TYPE-1 직급": Changed from "TYPE-1 GROUP LEADER" → "TYPE-1 LINE LEADER"
       - "calculation 방법": Changed from "GROUP LEADER 평균" → "TYPE-1 LINE LEADER 평균 × 2"
       - Added yellow highlight (background: #fff9e6) to emphasize special calculation
     - Line 7079-7084: LINE LEADER row updated
       - "참조 TYPE-1 직급": Changed from "TYPE-1 LINE LEADER" → "부하직원 인센티브"
       - "calculation 방법": Changed from "LINE LEADER 평균" → "부하직원 인센티브 합계 × 12% × 수령 비율"
       - Added blue highlight (background: #e8f5ff) to emphasize special formula
   - **Verification Steps**:
     1. Regenerate dashboard: `python integrated_dashboard_final.py --month 11 --year 2025`
     2. Open "인센티브 기준" tab → scroll to "TYPE-2 전체 직급 인센티브 계산 방법" table
     3. Verify GROUP LEADER shows "TYPE-1 LINE LEADER 평균 × 2"
     4. Verify LINE LEADER shows "부하직원 인센티브 합계 × 12% × 수령 비율"
   - **Related Documentation**: Updated TYPE-2 Calculation Logic section (Lines 425-443)
     - Clarified LINE LEADER uses subordinate-based formula, NOT TYPE-1 average
     - Clarified GROUP LEADER uses TYPE-1 LINE LEADER average × 2
   - **Implementation**: `integrated_dashboard_final.py:7073-7084`
   - **Commit**: [to be committed]
   - **Prevention**: Always verify dashboard display text matches actual calculation logic in calculation engine

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
├── integrated_dashboard_final.py    # Dashboard generator (Version 9)
├── CLAUDE.md                        # This file
├── README.md                        # Project documentation
├── PROJECT_IDENTITY_WEB_DASHBOARD.md  # Web deployment architecture
└── .gitignore

/docs/                               # 🌐 GitHub Pages Web Root (PUBLIC - WEB SERVED)
├── selector.html                    # ← https://...github.io/.../selector.html
├── Incentive_Dashboard_2025_11_Version_9.0.html  # ← November dashboard (web)
├── Incentive_Dashboard_2025_10_Version_9.0.html  # ← October dashboard (web)
├── output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv   # ← Download
├── output_QIP_incentive_november_2025_Complete_V9.0_Complete.xlsx  # ← Download
├── auth.html                        # ← Password authentication page
└── MANAGER_INCENTIVE_CALCULATION_LOGIC.md  # ← Manager calculation documentation

/src/                                # Core business logic (NOT web-served)
├── step0_create_monthly_config.py
├── step1_인센티브_계산_개선버전.py    # Main calculation engine
├── update_continuous_fail_column.py
├── validate_hr_data.py
└── ...

/scripts/                            # Utility scripts (NOT web-served)
├── verification/                    # Data validation system
│   ├── validate_condition_evaluation.py
│   ├── validate_incentive_amounts.py
│   ├── validate_dashboard_consistency.py
│   └── generate_final_report.py
├── create_month_selector.py        # Selector.html generator
└── legacy/                          # Legacy/backup scripts

/dashboard_v2/                       # Modular dashboard V6 (maintenance mode)
/config_files/                       # JSON configuration
/input_files/                        # Source data
/output_files/                       # Generated reports (→ copied to /docs)
/validation_reports/                 # Validation Excel reports
```

**Web vs Development**:
- `/docs/*` = Web-served files accessible via `https://moonkaicuzui.github.io/qip-dashboard/`
- All other folders = Development/build files (NOT web-accessible)

## Documentation Structure & Management Guidelines

### Official Documentation Structure (2025-11-19)

**Root Level Documentation (3 Core Files ONLY)**:
```
/CLAUDE.md                           # Technical guide for Claude Code
/README.md                           # Project overview for developers
/PROJECT_IDENTITY_WEB_DASHBOARD.md   # Web deployment architecture
```

**Active Technical Documentation** (`/docs/`):
```
/docs/
├── selector.html                    # Web-served month selector (GitHub Pages)
├── Incentive_Dashboard_*.html       # Web-served dashboards (GitHub Pages)
├── *.csv, *.xlsx                    # Web-served download files (GitHub Pages)
├── auth.html                        # Web-served authentication page (GitHub Pages)
├── AQL_VALIDATION_GUIDE.md          # AQL validation technical guide
├── DATA_FLOW.md                     # System data flow documentation
└── MANAGER_INCENTIVE_CALCULATION_LOGIC.md  # Manager incentive calculation formulas
```

**Archived Documentation** (`/docs/archive/`):
```
/docs/archive/
├── DASHBOARD_IMPROVEMENTS_2025_11.md        # Resolved: Dashboard enhancements
├── TYPE_TABLE_FIX_2025_11_05.md            # Resolved: TYPE table calculation fix
├── VIETNAMESE_MONTH_FIX_2025_11_10.md      # Resolved: Vietnamese month translation
├── SECURITY_TIMELINE.md                     # Resolved: Security incident timeline
├── SECURITY_URGENT.md                       # Resolved: Security urgent actions
└── [12 total resolved issue documents]
```

**User Guides** (`/docs/guides/`):
```
/docs/guides/
├── USER_ACCESS_GUIDE.md             # User access and deployment guide
├── SETUP_GUIDE.md                   # Project setup instructions
└── WEB_DEPLOYMENT_GUIDE.md          # Web deployment procedures
```

### Documentation Management Rules

**When to UPDATE existing docs (PREFERRED)**:
1. **Bug fixes**: Update `CLAUDE.md` "Common Issues & Solutions" section
2. **Calculation logic changes**: Update `MANAGER_INCENTIVE_CALCULATION_LOGIC.md`
3. **Data flow changes**: Update `DATA_FLOW.md`
4. **AQL validation changes**: Update `AQL_VALIDATION_GUIDE.md`
5. **Version updates**: Update `CLAUDE.md` and `README.md` version references

**When to CREATE new docs (RARELY)**:
1. **Entirely new system component** (e.g., new payment integration system)
2. **Major architectural change** (e.g., migration to new framework)
3. **New user guide** (place in `/docs/guides/`)
4. **NEVER for bug fixes or minor improvements** - use existing core docs

**When to MOVE to `/docs/archive/`**:
1. **Issue is resolved** and documented in core files (CLAUDE.md or MANAGER_INCENTIVE_CALCULATION_LOGIC.md)
2. **Temporary investigation** completed (e.g., TYPE_TABLE_FIX_2025_11_05.md)
3. **Time-bound incident** resolved (e.g., SECURITY_URGENT.md)
4. **Historical reference** needed but not actively referenced

**When to DELETE entirely**:
1. **Obsolete technology** no longer used (e.g., VERCEL_SETUP.md when using GitHub Pages)
2. **Temporary validation reports** after results integrated (e.g., COMPREHENSIVE_VALIDATION_REPORT_NOVEMBER_2025.md)
3. **Local file guides** for web-deployed project (e.g., 📱모바일에서_보는_방법.md)
4. **Duplicate information** already in core docs

### Documentation Cleanup History (2025-11-19)

**Deleted (3 files)**:
- `VERCEL_SETUP.md` - Project uses GitHub Pages, not Vercel
- `📱모바일에서_보는_방법.md` - Local file guide, project now web-deployed
- `COMPREHENSIVE_VALIDATION_REPORT_NOVEMBER_2025.md` - Temporary validation report

**Moved to `/docs/archive/` (5 files)**:
- `docs/DASHBOARD_IMPROVEMENTS_2025_11.md` - Dashboard improvements now in core docs
- `docs/TYPE_TABLE_FIX_2025_11_05.md` - TYPE table fix documented in CLAUDE.md
- `docs/VIETNAMESE_MONTH_FIX_2025_11_10.md` - Vietnamese fix documented in CLAUDE.md
- `SECURITY_TIMELINE.md` - Security incident resolved
- `SECURITY_URGENT.md` - Security urgent actions completed

**Moved to `/docs/guides/` (1 file)**:
- `USER_ACCESS_GUIDE.md` - User guide properly categorized

**Result**: Root directory reduced to 6 essential files (action.sh, CLAUDE.md, README.md, PROJECT_IDENTITY_WEB_DASHBOARD.md, integrated_dashboard_final.py, run_full_validation.sh)

### Anti-Pattern Prevention

**❌ DON'T DO THIS**:
```
# Creating new doc for every bug fix
docs/FIX_CONTINUOUS_MONTHS_BUG_2025_11_19.md
docs/FIX_LANGUAGE_SWITCHER_2025_11_19.md
docs/FIX_TYPE1_AVERAGE_2025_11_18.md
```

**✅ DO THIS INSTEAD**:
```
# Document fixes in existing core files
CLAUDE.md: "Common Issues & Solutions" section
MANAGER_INCENTIVE_CALCULATION_LOGIC.md: "중요 수정 이력 (CRITICAL FIXES)" section
```

**Rationale**:
- Prevents 50+ scattered markdown files (31 found before cleanup)
- Avoids orphaned documents causing old problems in new conversations
- Maintains single source of truth for each topic
- Enables context-aware Claude Code to find answers quickly

## Version Management & Backward Compatibility

### Current Version: 9.1 (as of 2025-11-19)

**Critical Architecture Decision**: The system implements **fallback pattern** for version transitions to ensure backward compatibility when reading previous month data.

**Important Version Fix (2025-11-19):**
- **V9.1 is the correct version** with proper continuous months calculation and average rounding
- **V9.0 created later has incorrect data** - fallback pattern now prioritizes V9.1 over V9.0
- File reading priority: **V9.1 → V9.0 → V8.02** (highest version first)

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

**Problem**: When December 2025 needs November 2025 data, but multiple versions exist (V9.1 correct, V9.0 incorrect).

**Solution**: Fallback pattern in `step1_인센티브_계산_개선버전.py` (Updated 2025-11-19):

```python
# Lines 1214-1225: Previous month file loading (highest version first)
excel_patterns = [
    # V9.1 version (latest - correct data)
    f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.1_Complete.csv",
    f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.1_Complete.csv",
    # V9.0 version
    f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
    f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
    # V8.02 version (backward compatibility)
    f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv",
    f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv"
]
```

**Why This Matters**:
- Month 1 (V9.1): Reads Month 0 (V9.1 or V9.0 or V8.02) - SUCCESS with fallback
- Month 2 (V9.1): Reads Month 1 (V9.1) - SUCCESS with primary pattern
- **V9.1 prioritized over V9.0** to use correct data with proper continuous months calculation
- Without correct priority: Would read V9.0 (wrong data) before V9.1 (correct data)

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
