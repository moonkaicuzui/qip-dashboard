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

### 0. NEVER LIE TO USER (절대 거짓말 금지 - 최우선 원칙)
- **NEVER claim completion when not actually done** - 실제로 완료하지 않았으면 완료했다고 하지 마라
- **NEVER make excuses or blame caching** - 핑계 대지 말고 문제의 근본 원인을 찾아라
- **ALWAYS verify before claiming success** - 성공했다고 주장하기 전에 반드시 검증하라
- **ADMIT mistakes immediately** - 실수는 즉시 인정하고 수정하라
- **ASK for help when stuck** - 막히면 포기하지 말고 사용자에게 물어봐라

### Google Drive Data-First Principle (Google Drive 데이터 우선 원칙)
- **ALWAYS use Google Drive as single source of truth** - 항상 Google Drive를 유일한 데이터 소스로 사용
- **NEVER rely on outdated local data** - 오래된 로컬 데이터에 의존하지 마라
- **Service account credentials location**: `/Users/ksmoon/Downloads/qip-dashboard-dabdc4d51ac9.json`
- **Manual download when GitHub Actions fails**:
  ```bash
  GOOGLE_SERVICE_ACCOUNT=$(cat /Users/ksmoon/Downloads/qip-dashboard-dabdc4d51ac9.json) \
  python scripts/download_from_gdrive.py
  ```
- **ALWAYS verify data freshness** - Check file modification dates and content dates
- **Data validation after download** - Verify expected date ranges exist in downloaded files

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

### 5. Continuous Months Calculation Priority (연속월 계산 우선순위 - 2025-12-03)
- **ALWAYS use `Continuous_Months + 1` as primary calculation method**
- **NEVER trust `Next_Month_Expected` as primary source** - this field can contain corrupted/wrong values
- **Priority Order** (MUST follow this order):
  1. **Priority 1**: `Continuous_Months + 1` (가장 신뢰성 높음 - 수학적으로 검증 가능)
  2. **Priority 2**: `Next_Month_Expected` (fallback only - 오류 가능성 있음)
  3. **Priority 3**: Reverse calculation from incentive amount (last resort)
- **Why Continuous_Months + 1 is more reliable**:
  - Direct calculation from validated monthly data
  - No intermediate computation that can introduce errors
  - Mathematically verifiable: if October = 12 and all conditions pass → November = 13
- **Why Next_Month_Expected can be unreliable**:
  - Pre-calculated value that can be corrupted during data processing
  - Subject to errors in previous month's calculation logic
  - Not validated against actual monthly conditions
- **Implementation**: `src/step1_인센티브_계산_개선버전.py:1105-1124` (calculate_continuous_months_from_history)
- **Historical Bug** (2025-12-03): October file had `Next_Month_Expected: 2` but `Continuous_Months: 12` - using wrong priority caused 12-month employees to show as 2-month

### 6. Always Sync Google Drive Before Calculation (계산 전 Google Drive 동기화 필수)
- **NEVER calculate incentives with potentially outdated local data**
- **ALWAYS download fresh data from Google Drive before any calculation**
- **Verification required**: Compare local file dates with Google Drive `modifiedTime`
- **Historical Bug** (2025-12-03): Local attendance data showed 13 days, Google Drive had 25 days - caused all employees to fail attendance condition
- **Command to sync**:
  ```python
  # Load service account and download fresh data
  import os, json
  with open("/Users/ksmoon/Downloads/qip-dashboard-dabdc4d51ac9.json") as f:
      os.environ['GOOGLE_SERVICE_ACCOUNT'] = json.dumps(json.load(f))
  exec(open('scripts/download_from_gdrive.py').read())
  ```
- **Workflow**: Download → Convert Attendance → Calculate → Generate Dashboard

### 7. Deployment and Documentation Workflow (배포 및 문서화 필수 원칙)
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

6. **Employee Detail Modal Not Opening** (FIXED: 2025-11-20):
   - **Problem**: Clicking employee names doesn't open detail modal
   - **Error**: `ReferenceError: isInterimReport is not defined` at showEmployeeDetail()
   - **Root Cause**: Variable `isInterimReport` defined in validation tab scope but referenced globally
   - **Solution**: Calculate `isInterimReport` inside showEmployeeDetail() function
   - **Implementation**: `integrated_dashboard_final.py:16122-16125`
   - **Critical Fix**: Must regenerate HTML after code fix: `python integrated_dashboard_final.py --month 11 --year 2025`
   - **Verification**: Modal opens without console errors after deployment
   - **Commit**: `d5cb492` (2025-11-20)

7. **Config File Automation** (ADDED: 2025-11-20):
   - **Problem**: Config files needed manual update after Google Drive downloads
   - **Solution**: Created automated config update system
   - **Scripts Added**:
     - `scripts/enhanced_download_with_config.py`: Integrated download + config update
     - `scripts/update_config_after_download.py`: Standalone config updater
     - `scripts/test_config_update.py`: Automation testing utility
   - **Features**:
     - Auto-detect downloaded file paths
     - Calculate working_days from attendance data
     - Update config with actual paths (not virtual drive://)
     - Add timestamps for tracking
   - **GitHub Actions**: `.github/workflows/auto-update-enhanced.yml`
   - **Usage**: `python scripts/enhanced_download_with_config.py`

8. **Continuous Months Calculation Priority Order** (FIXED: 2025-11-19):
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

9. **Language Switcher - Korean Date Format Visibility** (FIXED: 2025-11-19):
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

10. **CSV Download Empty File Bug** (FIXED: 2025-11-19):
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

11. **TYPE-2 Incentive Calculation Method Display Error** (FIXED: 2025-11-19):
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
   - **Commit**: `78260a0` (2025-11-19)
   - **Prevention**: Always verify dashboard display text matches actual calculation logic in calculation engine

12. **CSV Download Button Removal** (CHANGED: 2025-11-19):
   - **User Request**: Remove CSV download button from dashboard
   - **Reason**: CSV download functionality no longer needed
   - **Changes Made**:
     - Line 6414-6416: Removed CSV download button from header
     - Line 9782-9788: Disabled `downloadCSV()` function with comment
     - Line 10195: Removed CSV button text update in language switcher
   - **Remaining Download Options**:
     - HTML download: Full dashboard as standalone HTML file
     - Excel download: Excel file from GitHub Pages
   - **Implementation**: `integrated_dashboard_final.py:6414-6416, 9782-9788, 10195`
   - **Commit**: [to be committed]

13. **TYPE-2 LINE LEADER Calculation Method - BFS 관리자 인센티브** (INTENTIONAL CHANGE: 2025-12-01):
   - **Original Issue (2025-11-19)**: All TYPE-2 LINE LEADER employees received identical amount
   - **Implemented Solution**: BFS (Breadth-First Search) 관리자 인센티브 계산 방식
     - TYPE-2 LINE LEADER가 관리하는 부하직원 중 LINE LEADER 직급 검색
     - BFS로 모든 부하 LINE LEADER의 인센티브 합계 계산
     - 해당 합계의 일정 비율로 TYPE-2 LINE LEADER 인센티브 결정
   - **Status**: ✅ **의도된 변경** - BFS 로직이 정상 작동 중
   - **Implementation**: `src/step1_인센티브_계산_개선버전.py` BFS manager incentive logic
   - **Note**: 이전에 "CALCULATION ENGINE BUG"로 표시되었으나, 사용자 요청에 따른 의도된 변경임
   - **Verification**: TYPE-2 LINE LEADER 인센티브가 부하 LINE LEADER 인센티브 기반으로 계산됨

14. **Condition Fulfillment Display Error** (FIXED: 2025-11-19):
   - **Problem**: Employee 619100392 (PHẠM MINH HUY) shows "3/3 conditions met (100%)" but receives 0 VND
   - **Employee Data**:
     - Position: TYPE-1 LINE LEADER
     - Actual Working Days: 1일 (only 1 day worked)
     - November Incentive: 0 VND ✅ (correct - did not meet minimum days)
     - Dashboard display: "3/3 조건 충족" ❌ (incorrect)
   - **Root Cause**: Condition fulfillment text logic did not check incentive payment status
     - Line 16119-16126: Modal shows "X/Y conditions fulfilled" based on applicable conditions only
     - Did not account for employees who failed to receive incentive despite passing some conditions
   - **Solution**: Added incentive payment status check before displaying condition count
     - Line 16123: Added `!isPaidEmployee && totalConditions > 0 ?` condition
     - If employee received 0 VND → displays "Conditions not met" message instead of count
   - **Verification**:
     1. Regenerate dashboard: `python integrated_dashboard_final.py --month 11 --year 2025`
     2. Open employee modal for 619100392 (PHẠM MINH HUY)
     3. Verify shows "Conditions not met" instead of "3/3 충족"
   - **Implementation**: `integrated_dashboard_final.py:16119-16127`
   - **Commit**: [to be committed]
   - **Prevention**: Always cross-check display logic with actual business logic (incentive amount = 0 → conditions not met)

13. **TYPE-2 LINE LEADER Calculation Method Display Update** (FIXED: 2025-11-19):
   - **Problem**: Dashboard displayed incorrect calculation method for TYPE-2 LINE LEADER
     - Displayed: "참조: 부하직원 인센티브", "계산: 부하직원 인센티브 합계 × 12% × 수령 비율"
     - Reality: Calculation engine uses TYPE-1 LINE LEADER average (Common Issue #11)
   - **User Request**: Update display to match actual calculation logic
   - **Solution**: Updated "인센티브 기준" tab TYPE-2 calculation table
     - Line 7077-7081: LINE LEADER row updated
     - "참조 TYPE-1 직급": Changed from "부하직원 인센티브" → "TYPE-1 LINE LEADER"
     - "calculation 방법": Changed from "부하직원 인센티브 합계 × 12% × 수령 비율" → "TYPE-1 LINE LEADER 평균"
   - **Verification**:
     1. Open "인센티브 기준" tab → "TYPE-2 전체 직급 인센티브 계산 방법" table
     2. LINE LEADER row shows "TYPE-1 LINE LEADER" and "TYPE-1 LINE LEADER 평균"
   - **Implementation**: `integrated_dashboard_final.py:7077-7081`
   - **Commit**: [to be committed]
   - **Note**: This aligns dashboard display with actual calculation engine behavior (Issue #11)

14. **Talent Pool Members Translation Error** (FIXED: 2025-11-19):
   - **Problem**: English/Vietnamese mode still shows "1직원" (Korean) in Talent Pool section
   - **Root Cause**: Hardcoded Korean suffix in Talent Pool count display
     - Line 15247: `talentPoolMembers.length + '직원'` (no translation logic)
   - **Solution**: Added language-specific translation for employee count suffix
     - Line 15247-15250: Added conditional logic for Korean/English/Vietnamese
     - English: "employee" (singular) or "employees" (plural)
     - Korean: "직원"
     - Vietnamese: "nhân viên"
   - **Verification**:
     1. Regenerate dashboard: `python integrated_dashboard_final.py --month 11 --year 2025`
     2. Switch to English mode
     3. Verify Talent Pool section shows "1 employee" or "N employees" (not "1직원")
   - **Implementation**: `integrated_dashboard_final.py:15247-15250`
   - **Commit**: [to be committed]
   - **Prevention**: Always use translation system for dynamic text, avoid hardcoded language strings

15. **Google Drive Force Download Enhancement** (FIXED: 2025-11-19):
   - **Problem**: User concern about file synchronization - files may not be re-downloaded if already exist
   - **User Request**: Force re-download even if file with same name exists
   - **Solution**: Enhanced `download_from_gdrive.py` with explicit force download logic
     - Line 74-119: Updated `download_file()` function
       - Added `force=True` parameter (default)
       - Explicit file deletion before download if file exists
       - Added detailed logging: old file modification time, new file size and time
     - Line 188, 248, 262: All download calls use `force=True` explicitly
   - **Benefits**:
     - Clear logs showing old file deletion and new file download
     - File size and modification time verification
     - Prevents stale data issues

16. **Google Drive Multiple File Overwrite Bug** (FIXED: 2025-11-19):
   - **Problem**: Dashboard showing Nov 13 data despite Google Drive having Nov 15 data
     - Google Drive folder contains multiple files matching same pattern (e.g., "attendance_data.csv", "attendance_data_new.csv")
     - Files sorted by modifiedTime desc (newest first)
     - ALL matching files downloaded sequentially to SAME output path
     - Older files overwrite newer files → Final result contains OLD data
     - **Affects**: Monthly data (attendance, basic_manpower, 5prs) AND AQL history files
   - **Root Cause**: `scripts/download_from_gdrive.py` downloaded all matching files without tracking
     - Pattern: 'attendance' in filename → matches multiple files
     - Loop downloads file 1 (newest) → then file 2 (older) → file 2 OVERWRITES file 1
     - No break or tracking mechanism to stop after first match
     - Same issue for AQL files: Multiple files with same month/year go to same output_path
   - **Solution**: Added pattern tracking system to download only FIRST (newest) file per pattern
     - **Monthly Data** (Lines 240-277):
       - Line 240: Added `downloaded_patterns = set()` to track downloaded patterns
       - Line 246: Added `pattern_type` variable ('basic_manpower', 'attendance', '5prs')
       - Lines 268-271: Skip file if pattern already downloaded
       - Lines 274-277: Add pattern to downloaded_patterns after successful download
     - **AQL History** (Lines 287-313):
       - Line 287: Added `aql_downloaded_months = set()` to track month/year combinations
       - Line 298: Create `month_year_key` (e.g., "NOVEMBER_2025")
       - Lines 300-303: Skip file if month/year already downloaded
       - Line 306: Add month_year_key to aql_downloaded_months after successful download
   - **Verification**:
     1. Trigger GitHub Actions from Admin page
     2. Check "Download CSV from Google Drive" logs
     3. Should see "⏭️ 건너뜀: [filename]" messages for duplicate patterns
     4. Verify all data types (attendance, basic_manpower, 5prs, AQL) reflect latest files
     5. Dashboard should show Nov 15 data (13 working days)
   - **Implementation**: `scripts/download_from_gdrive.py:240-277, 287-313`
   - **Commit**: df0ac5c (monthly data), [to be committed] (AQL fix)
   - **Prevention**: Always use pattern tracking when multiple files may match the same output destination
   - **Verification**:
     - Check GitHub Actions logs for "🔄 기존 파일 삭제" and "✅ 다운로드 완료" messages
     - Verify file modification times are updated
   - **Implementation**: `scripts/download_from_gdrive.py:74-119, 188, 248, 262`
   - **Commit**: cc2627f
   - **Note**: This ensures GitHub Actions always downloads latest Google Drive data

17. **KPI vs Calendar Working Days Mismatch** (FIXED: 2025-11-19):
   - **Problem**: Calendar modal shows 13 working days (correct) but KPI card shows 11 days (wrong)
     - KPI used hardcoded config value: `const totalWorkingDays = {working_days};`
     - Calendar used actual attendance data: `window.excelDashboardData.attendance.total_working_days`
     - When data updates from Nov 13 (11 days) to Nov 15 (13 days), config wasn't regenerated
     - Result: Calendar and KPI showed different values
   - **Root Cause**: `integrated_dashboard_final.py:11284` used static config value instead of dynamic data
     - Config value comes from Python template: `{working_days}` (11)
     - Actual attendance data has correct value from CSV processing
   - **Solution**: Changed KPI calculation to use excelDashboardData instead of config
     - Lines 11283-11287: Added conditional to read from `window.excelDashboardData.attendance.total_working_days`
     - Fallback to config value only if excelDashboardData not available
     - Now KPI and calendar use same data source (Single Source of Truth)
   - **Verification**:
     1. Regenerate dashboard: `python integrated_dashboard_final.py --month 11 --year 2025`
     2. Open "요약 및 시스템 검증" tab
     3. KPI card should show same value as calendar modal
     4. After Google Drive sync with Nov 15 data, both should show 13 days
   - **Implementation**: `integrated_dashboard_final.py:11283-11287`
   - **Commit**: [to be committed]
   - **Prevention**: Always use actual data sources (excelDashboardData) instead of config templates for dynamic values

17. **GitHub Actions Google Drive Sync Failure** (IDENTIFIED: 2025-11-19):
   - **Problem**: Google Drive has attendance data up to Nov 15, but system only shows Nov 13 data
   - **User Report**: "구글드라이브엔 15일까지 출근 데이타가 있어" (Google Drive has attendance data up to the 15th)
   - **Root Cause**: GitHub Actions workflow running but not downloading latest data
     - Service account authentication may be failing silently
     - Workflow shows success but data not updated since Nov 17
   - **Impact**:
     - Working days shows 11 (Nov 1-13) instead of 13 (Nov 1-15)
     - Missing 2 days of attendance data affects incentive calculations
   - **Temporary Fix Applied**:
     - Manually updated `config_november_2025.json` working_days from 11 to 13
     - Commit: `bd8d933` (2025-11-19)
   - **Permanent Fix Required**:
     - Verify GitHub Actions service account authentication
     - Check GOOGLE_SERVICE_ACCOUNT secret in GitHub repository settings
     - Ensure service account has proper Google Drive API access permissions
   - **Verification**:
     - Attendance data only has dates: Nov 1, 3-8, 10-13 (11 unique dates)
     - Should have: Nov 1, 3-8, 10-15 (13 unique dates)
   - **Status**: **GITHUB ACTIONS AUTH ISSUE** - requires service account fix

18. **HTML Download Local File Error** (FIXED: 2025-11-21):
   - **Problem**: Users download HTML file from dashboard but cannot open locally
     - Error: `ERR_FILE_NOT_FOUND` when opening `file:///C:/Users/ASUS/Downloads/auth.html`
     - Expected behavior unclear - users assume downloaded HTML should work offline
   - **User Impact**: Confusion about why downloaded file doesn't work
   - **Root Cause**: Project is **GitHub Pages web-only application**
     - Dashboard designed for web server environment (`https://` URLs)
     - Local file system (`file://` URLs) lacks web server capabilities
     - Resources and paths depend on web server structure
   - **Solution**: Added confirmation warning before HTML download
     - Lines 9781-9791: Multi-language warning dialog before download
       - Korean: "다운로드된 HTML 파일은 로컬 파일 시스템에서 열 수 없습니다"
       - English: "The downloaded HTML file cannot be opened from local file system"
       - Vietnamese: "Tệp HTML đã tải xuống không thể mở từ hệ thống tệp cục bộ"
     - Warning includes production web URL: `https://moonkaicuzui.github.io/qip-dashboard/`
     - User must confirm to proceed with download
     - Lines 9811-9816: Post-download reminder to use web URL instead
   - **Verification**:
     1. Click HTML download button → warning dialog appears
     2. Warning explains ERR_FILE_NOT_FOUND will occur locally
     3. Warning provides web URL for proper access
     4. User can cancel or proceed after confirmation
   - **Implementation**: `integrated_dashboard_final.py:9781-9816`
   - **Commit**: `cb23100` (2025-11-21)
   - **Prevention**: Always warn users when downloaded files won't work as expected
   - **Related**: See "Web-First Deployment Architecture" (CLAUDE.md Lines 79-107)
   - **Note**: Issue #18 identified the problem, Issue #19 provides the complete solution

19. **Self-Contained HTML for Offline Access** (IMPLEMENTED: 2025-11-21):
   - **Problem**: Downloaded HTML files cannot be opened locally (continuation of Issue #18)
     - Users want to share dashboards with others (경영진, 관리자, 외부 감사관)
     - Downloaded files require web server environment
     - Password authentication blocks local file access
     - Excel download depends on GitHub Pages hosting
   - **User Impact**: Unable to share dashboard files that "just work" when double-clicked
   - **Solution**: Created Self-Contained HTML generator system
     - **Generator Script**: `create_self_contained_html.py` (7.8KB)
       - Converts web dashboard to self-contained offline version
       - Inlines all external CDN resources (Bootstrap, Font Awesome, Chart.js, D3.js)
       - Removes authentication checks (local files already shared with trusted users)
       - Removes Excel download button (web-only feature)
       - Replaces Google Fonts with system fonts (saves 500KB)
       - Adds "📦 Offline Version" indicator badge
     - **Modified Download Button**: `integrated_dashboard_final.py`
       - Line 6412: Button text changed to "📦 Offline 버전"
       - Lines 9779-9816: downloadDashboard() now downloads Self-Contained version
       - Lines 10160-10164: Multi-language support (Korean/English/Vietnamese)
       - Informative confirmation dialog explaining offline features
   - **File Sizes**:
     - Web version: 4.90 MB (requires web server)
     - Self-Contained: 5.68 MB (+0.78 MB, works offline)
     - CDN libraries: ~800KB total (Bootstrap, Font Awesome, Chart.js, D3.js)
   - **Features**:
     - ✅ Works offline (double-click to open in any browser)
     - ✅ No password required (file sharing = trust established)
     - ✅ All charts and interactive features functional
     - ✅ Language switching (Korean/English/Vietnamese)
     - ✅ All filters, search, modals work
     - ✅ System fonts (Windows: Malgun Gothic, Mac: Apple SD Gothic Neo)
     - ❌ Excel download removed (use web version for Excel)
   - **Usage Workflow**:
     1. Web dashboard: https://moonkaicuzui.github.io/qip-dashboard/
     2. Click "📦 Offline 버전" button
     3. Confirmation dialog explains features/limitations
     4. Download `Incentive_Dashboard_2025_11_Version_9.0_SelfContained.html`
     5. Share file via email/USB/network drive
     6. Recipient double-clicks → Opens in browser → No password needed
   - **Generation Process**:
     ```bash
     # Automatic (recommended)
     python integrated_dashboard_final.py --month 11 --year 2025
     # Creates: output_files/Incentive_Dashboard_2025_11_Version_9.0.html

     cp output_files/Incentive_Dashboard_2025_11_Version_9.0.html docs/
     python create_self_contained_html.py --month 11 --year 2025
     # Creates: docs/Incentive_Dashboard_2025_11_Version_9.0_SelfContained.html
     ```
   - **Technical Implementation**:
     - **CDN Replacement**: All `<link>` and `<script>` tags with external URLs replaced with inline content
     - **Font Strategy**: Google Fonts removed, CSS updated to system font stack
     - **Authentication Bypass**: `validateSession()` function modified to always return true
     - **Path Dependencies**: All `window.location.href = 'auth.html'` disabled
     - **Blob Generation**: Removed (not needed - direct file download from GitHub Pages)
   - **Verification Steps**:
     1. Download Self-Contained HTML from web dashboard
     2. Locate file in Downloads folder (check filename has `_SelfContained`)
     3. Double-click file → Should open in default browser
     4. Verify: No password screen, dashboard loads immediately
     5. Test: Charts display, language switching works, filters functional
   - **Implementation**:
     - `create_self_contained_html.py`: Generator script (new file)
     - `integrated_dashboard_final.py:6412, 9779-9816, 10160-10164`: Download button changes
     - `static/cdn_libraries/`: Downloaded CDN resources (~800KB)
     - `docs/Incentive_Dashboard_2025_11_Version_9.0_SelfContained.html`: Generated offline version (5.68MB)
   - **Commit**: `c7a33bc` (2025-11-21)
   - **Prevention**: For future dashboards requiring offline access, use Self-Contained generator
   - **Trade-offs**:
     - **Pros**: True offline access, no technical knowledge required, shareable
     - **Cons**: +0.78MB file size, Excel download unavailable, no automatic updates
   - **Related**: Issue #18 (identified problem), Web-First Deployment Architecture (CLAUDE.md Lines 79-107)

20. **November 2025 Dashboard Comprehensive Fix** (FIXED: 2025-11-21):
   - **Context**: User reported 5 critical issues via screenshots after November data became available
   - **All Issues Fixed and Verified**: Complete end-to-end testing with Single Source of Truth validation

   **Issue 20.1: Google Drive Sync - Working Days Update**
   - **Problem**: Dashboard showed only 15 days when Google Drive had 18 days (actually 19)
   - **Root Cause**: Stale local data, Google Drive sync needed
   - **Solution**: Executed `python scripts/download_from_gdrive.py` to fetch latest attendance data
   - **Result**:
     - Google Drive: 16 working days (Nov 1, 3-8, 10-15, 17-19)
     - Config file: 16 days (auto-updated at 2025-11-21 12:54:38)
     - Dashboard CSV: 16 days
     - All data sources perfectly aligned ✅
   - **Verification**: `input_files/attendance/converted/attendance data november_converted.csv`
   - **Last working day**: 2025-11-19

   **Issue 20.2: QC Assembly Inspector - Condition 1&4 Application Logic**
   - **Problem**: "Total working date is 13 days, Dashboard don't apply 1&4 condition. QC assembly inspector type applied 6/8 conditions"
   - **User Request**: "After 15th in month, could we apply 1 and 4 condition"
   - **Root Cause**: Position-specific cutoff date logic needed implementation
   - **Solution**: Implemented date-based condition application in calculation engine
     - QC Assembly Inspector (Position Code A1-A5): 15-day cutoff
     - Other positions: 20-day cutoff
     - Before cutoff: Apply only Conditions 1&4 (attendance basics)
     - After cutoff: Apply all applicable conditions (1,2,3,4,5,6,9,10 for QC Assembly)
   - **Implementation**: `src/step1_인센티브_계산_개선버전.py:4747-4775`
   - **Result**:
     - Nov 19 > 15 days → All 8 conditions applied to QC Assembly Inspector
     - 167 QC Assembly employees: 129 have full conditions, 38 excluded (maternity leave, etc.)
   - **Verification**: Checked actual employee data - conditions correctly applied based on date

   **Issue 20.3: Vietnamese Translation - "Bộ" → "Đôi"**
   - **Problem**: Condition 10 (5PRS inspection quantity) showed "Bộ" instead of "Đôi" in Vietnamese
   - **Root Cause**: Incorrect translation in `dashboard_translations.json`
   - **Solution**: Updated translation file
     - Changed: `"vi": "Bộ"` → `"vi": "Đôi"`
     - Path: `incentiveCalculation.pieces.vi`
   - **Implementation**: `config_files/dashboard_translations.json:2527-2528, 6354-6355`
   - **Result**: Vietnamese correctly displays "Đôi" (pairs) ✅

   **Issue 20.4: English Translation - "pcs" → "prs"**
   - **Problem**: Condition 9 (5PRS pass rate) showed "pcs" (pieces) instead of "prs" (pairs) in English
   - **Root Cause**: Incorrect translation in `dashboard_translations.json`
   - **Solution**: Updated translation file
     - Changed: `"en": "pcs"` → `"en": "prs"`
     - Path: `incentiveCalculation.pieces.en`
   - **Implementation**: `config_files/dashboard_translations.json:2527-2528, 6354-6355`
   - **Result**: English correctly displays "prs" (pairs) ✅

   **Issue 20.5: AQL Statistics - Pass/Fail Quantity Display**
   - **Problem**: User questioned AQL fail/pass quantity calculation accuracy in summary validation
   - **Verification Method**: Mathematical re-calculation from raw CSV data
     - Formula: `Fail_Percent = (Total_Tests - Pass_Count) / Total_Tests × 100`
     - Compared calculated values with CSV `AQL_Fail_Percent` column
   - **Result**:
     - Total employees: 540
     - Employees with AQL tests: 100
     - Calculation accuracy: 100/100 matched (100% ✅)
     - Sample: Employee 621030996 - 12 tests, 11 pass, 1 fail (8.3%) ✅
   - **Implementation**: Data calculation in `src/step1_인센티브_계산_개선버전.py`
   - **Verification**: Python-based independent recalculation confirmed 100% accuracy

   **Complete Workflow Executed**:
   1. ✅ Google Drive sync: `python scripts/download_from_gdrive.py`
   2. ✅ Translation updates: `config_files/dashboard_translations.json` (2 languages)
   3. ✅ Calculation engine update: `src/step1_인센티브_계산_개선버전.py:4747-4775`
   4. ✅ Dashboard regeneration: `python integrated_dashboard_final.py --month 11 --year 2025`
   5. ✅ Web deployment: Files copied to `/docs` folder
   6. ✅ Selector regeneration: `python scripts/create_month_selector.py`
   7. ✅ Comprehensive verification: All 5 issues independently tested

   **Data Integrity Validation**:
   - Single Source of Truth: Google Drive → CSV → Config → Dashboard
   - Cross-validation: All data sources show 16 working days
   - Mathematical verification: AQL statistics 100% accurate
   - Business logic verification: Condition application correct for all 167 QC Assembly employees

   **Files Modified**:
   - `src/step1_인센티브_계산_개선버전.py` (condition logic)
   - `config_files/dashboard_translations.json` (translations)
   - `config_files/config_november_2025.json` (auto-updated by sync)
   - `input_files/attendance/converted/attendance data november_converted.csv` (Google Drive sync)
   - `output_files/Incentive_Dashboard_2025_11_Version_9.0.html` (regenerated)
   - `output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv` (regenerated)
   - `docs/*` (web deployment)

   **Verification Date**: 2025-11-21 16:14:46
   - **Commit**: [to be committed]
   - **Prevention**:
     - Always sync Google Drive before generating reports
     - Validate translations in all 3 languages (KO/EN/VN)
     - Test position-specific logic with actual employee data
     - Run independent mathematical verification for statistics

21. **November 2025 Recalculation with Formula Fixes** (COMPLETED: 2025-11-25):
   - **Context**: Implemented and deployed two critical formula fixes identified in previous session
   - **Formula Fix 1: TYPE-2 Average Calculation** (Line 4328-4354)
     - **Change**: "모든 직원 포함 (0 VND 포함)" → "수령자만 평균 (0 VND 제외)"
     - **Code**: `receiving_employees = pos_employees[pos_employees[incentive_col] > 0]`
     - **Expected Impact**: TYPE-2 incentives increase ~72% when TYPE-1 employees receive incentive
     - **November Result**: 0 VND (correct - no TYPE-1 employees passed 100% of conditions)
     - **Verification**: Formula verified in code at `src/step1_인센티브_계산_개선버전.py:4340`

   - **Formula Fix 2: Attendance Rate Calculation** (Line 4869-4892, Updated 2025-12-01)
     - **Change**: `(actual / (total - approved_leave))` → `100 - (무단결근/total×100)`
     - **Policy Formula** (정책 반영):
       ```
       결근일 = 총 근무일 - 실제 근무일 - 승인휴가 (무단결근만 카운트)
       결근율 = 결근일 / 총 근무일 × 100
       출근율 = 100 - 결근율 (승인휴가는 출근으로 인정)
       ```
     - **Code**:
       ```python
       absence_days = total_days - actual_days - approved_leave_days
       absence_rate = (absence_days / total_days) * 100
       attendance_rate = 100 - absence_rate
       ```
     - **Verification**: ✅ Tested with policy example - formula working correctly
     - **Example**: Worker 625080250 (Total=18, Actual=14, ApprovedLeave=2)
       - 결근일: 18-14-2 = 2일
       - 결근율: 2/18 = 11.1%
       - 출근율: 100-11.1 = **88.9%** (PASS ✅, threshold 88%)

   - **November 2025 Calculation Results**:
     - Total employees: 541
     - Eligible (not resigned before Nov): 420 employees
     - **Receiving incentive: 1 employee** (100% Condition Fulfillment Rule enforced)
     - **Total amount: 150,000 VND**
     - **TYPE-1 ASSEMBLY INSPECTOR**: 0/129 employees passed 100% (most at 75-87.5%)
     - **AQL Inspector Config**: Auto-updated - all 6 inspectors 0 months → 0 VND

   - **Business Logic Validation**:
     - ✅ **100% Condition Fulfillment Rule**: Strictly enforced (no partial incentives)
     - ✅ **TYPE-2 Reference Average**: Correctly uses receiving-only average (0 when none received)
     - ✅ **Attendance Rate Formula**: Policy-aligned (승인휴가=출근 인정, 무단결근만 결근 처리)
     - ✅ **AQL Config Auto-Update**: Step 7.5 integration working (backup created)

   - **Complete Workflow Executed**:
     1. ✅ Backup existing files: CSV and Excel outputs
     2. ✅ Recalculation: `python scripts/auto_calculate_incentives.py`
     3. ✅ AQL config update: `python scripts/auto_update_aql_config.py november 2025`
     4. ✅ Dashboard generation: `python integrated_dashboard_final.py --month 11 --year 2025`
     5. ✅ Web deployment: Files copied to `/docs` folder
     6. ✅ Selector regeneration: `python scripts/create_month_selector.py`
     7. ✅ Git commit & push: Commit `9023fd3` (2025-11-25 13:23)

   - **Files Modified**:
     - `output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv`
     - `output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.xlsx`
     - `config_files/aql_inspector_incentive_config.json` (auto-updated via Step 7.5)
     - `docs/Incentive_Dashboard_2025_11_Version_9.0.html`
     - `docs/output_QIP_incentive_november_2025_Complete_V9.0_Complete.*`
     - `docs/selector.html`

   - **Verification**:
     - Formula Fix 1: Verified in code (line 4340) and calculation results (0 VND correct)
     - Formula Fix 2: Verified with 3 sample employees with approved leave (84.21%, 63.16%, 78.95%)
     - AQL Config: Backup created `aql_inspector_incentive_config.json.backup.20251125_132339`
     - GitHub Pages: Deployed successfully after push

   - **Commit**: `9023fd3` (2025-11-25 13:23)
   - **Prevention**:
     - Both formula fixes are permanent and will apply to all future calculations
     - AQL Inspector config auto-update integrated in GitHub Actions Step 7.5
     - Validate calculation results against business logic (100% rule, reference averages)

22. **Google Drive modifiedTime Accurate "Last Update" Detection** (IMPLEMENTED: 2025-11-25):
   - **Problem**: "Last Update" badge showed inaccurate times
     - Used `working_days` value comparison (inaccurate)
     - Missed file changes when working_days didn't change
     - Example: Google Drive had 11/19, 11/25 data but dashboard showed 11/24 as last update
   - **Root Cause**: Detection logic only compared `working_days` count, not actual file modification times
     - CSV content analysis missed actual file upload times
     - Local file `mtime` showed download time, not Google Drive original time
   - **Solution**: Implemented Google Drive API `modifiedTime` tracking (Option 1)
     - `download_file()` now retrieves and returns `modifiedTime` from Google Drive API
     - Each file's `modifiedTime` stored in `config['files_modified_times']`
     - `config['last_updated']` now uses `max(files_modified_times.values())`
     - Dashboard displays accurate file modification time from Google Drive
   - **API Cost Analysis**:
     - Current: 192 API calls/day
     - After improvement: 384 API calls/day (+100%)
     - Google Drive free quota: 1,000,000,000 queries/day
     - Usage: 0.0000384% (100% free forever)
   - **Verification**:
     - Logic tested with simulated data (attendance: 11/19, 5prs: 11/25 18:22, basic_manpower: 11/25 18:36)
     - Correctly identified latest: 2025-11-25T18:36:00.000Z
     - Expected dashboard: "Last Update: [time] ago" based on actual file modification
   - **Files Modified**:
     - `scripts/enhanced_download_with_config.py:67-108` - Added modifiedTime retrieval
     - `scripts/enhanced_download_with_config.py:142-246` - Store modifiedTime in config
     - `scripts/enhanced_download_with_config.py:350-357, 373-381` - Pass modifiedTime in file info
   - **Benefits**:
     - ✅ 100% accurate file modification time detection
     - ✅ All file types tracked (attendance, 5PRS, basic_manpower, AQL)
     - ✅ Download optimization possible (skip if not modified)
     - ✅ Simple logic (timestamp comparison)
     - ✅ Forever free (0.00004% of API quota)
   - **Commit**: [to be committed]
   - **Prevention**: Always use Google Drive API modifiedTime for accurate file change detection

23. **AQL Inspector Part 1/2/3 Breakdown Display** (IMPLEMENTED: 2025-11-28):
   - **Problem**: AQL Inspector employees shown with generic modal, no 3-Part incentive breakdown
   - **User Request**: "AQL Inspector 인센티브 정책 확인 및 자동 표시"
   - **Root Cause**: Dashboard modal did not have special handling for AQL Inspector position
   - **Solution**: Implemented comprehensive AQL Inspector display system
     - **Dashboard Modal Enhancement** (`integrated_dashboard_final.py:16349-16458`):
       - Detect AQL Inspector position from employee data
       - Load `aql_inspector_incentive_config.json` data
       - Display Part 1/2/3 breakdown table with amounts
       - 3-language support (Korean/English/Vietnamese)
       - Warning message when attendance condition not met
     - **Config Data Integration** (`integrated_dashboard_final.py:1179-1189, 8274-8276, 8574-8585`):
       - Load AQL Inspector incentive config as Base64
       - Decode and make available as `window.aqlIncentiveConfig`
     - **Workflow Integration** (`action.sh:447-458`):
       - Added Step 1.8: Auto-update AQL Inspector config after calculation
       - Runs `scripts/auto_update_aql_config.py` automatically
   - **AQL Inspector 3-Part Calculation Logic**:
     - **Part 1** (AQL 평가): Progression table 1-15 months (150K → 1,000K VND)
     - **Part 2** (CFA 자격증): Fixed 700,000 VND if certified
     - **Part 3** (HWK 클레임 방지): 4개월부터 시작 (300K → 900K VND)
     - **Total** = Part 1 + Part 2 + Part 3
   - **Config Data Correction**:
     - Fixed ĐOÀN PHAN NHI (621110376) October data: 1,350,000 → 0 (per screenshot)
   - **Files Modified**:
     - `integrated_dashboard_final.py` (+145 lines)
     - `action.sh` (+13 lines - Step 1.8)
     - `config_files/aql_inspector_incentive_config.json` (data correction)
   - **Verification**:
     - Dashboard modal shows Part 1/2/3 breakdown for AQL Inspector employees
     - Language switching works correctly
     - Condition warning displayed when attendance fails
   - **Commit**: [to be committed]
   - **Prevention**:
     - Always verify config data against actual source (Excel/screenshot)
     - Test AQL Inspector modal with different language settings

24. **SelfContained HTML Auto-Sync with Web Dashboard** (IMPLEMENTED: 2025-12-04):
   - **Problem**: SelfContained HTML was outdated compared to Web Dashboard
     - Web Dashboard: Updated every 30 minutes by GitHub Actions
     - SelfContained: Generated manually, often 24+ hours behind
     - Users downloading offline version received stale data
   - **User Request**: "웹대시보드가 30분마다 업데이트 된다고 했지? 그때 selfcontained html도 30분마다 재생성되어야 sync가 되고 말이 되는거야"
   - **Solution**: Implemented automatic SelfContained HTML generation in GitHub Actions
     - **Step 9.5 Added** (`.github/workflows/auto-update-enhanced.yml:136-155`):
       - Runs after Step 9 (Dashboard HTML generation)
       - Generates SelfContained versions for ALL available months
       - Logs generated files for verification
     - **New Script** (`scripts/generate_all_selfcontained.py`):
       - Finds all dashboard HTML files in docs/
       - Generates SelfContained version for each (7월~11월)
       - Validates CDN library availability before processing
     - **CDN Libraries Added to Git** (`static/cdn_libraries/`):
       - `bootstrap.bundle.min.js` (78KB)
       - `chart.min.js` (208KB)
       - `d3.v7.min.js` (279KB)
       - Updated `.gitignore` to allow `!static/cdn_libraries/*.js`
   - **Automation Flow**:
     ```
     [Every 30 minutes]
     Step 9: Generate Dashboard HTML
         ↓
     Step 9.5: Generate SelfContained HTML (NEW!)
         ↓
     Step 10: Prepare GitHub Pages
     ```
   - **Verification Results** (2025-12-04):
     - 직원 수: Web=422 / Self=422 ✅
     - 총 인센티브: 140,886,342 VND (both) ✅
     - 수령자 수: 353명 (both) ✅
     - 데이터 해시: 100% 일치 ✅
   - **Files Modified**:
     - `.github/workflows/auto-update-enhanced.yml` (Step 9.5 추가)
     - `.gitignore` (CDN JS 파일 예외 추가)
     - `scripts/generate_all_selfcontained.py` (신규)
     - `static/cdn_libraries/*.js` (Git 추적 추가)
   - **Commit**: `74611d60`
   - **Prevention**: SelfContained HTML is now automatically kept in sync with Web Dashboard

25. **AQL Inspector 인센티브 계산 버그 - Month 객체 문자열 변환** (FIXED: 2025-12-04):
   - **Problem**: TYPE-1 AQL Inspector 인센티브가 잘못 계산됨
     - 수정 전: `Continuous_Months=1`, `Incentive=850,000 VND` (모든 AQL Inspector)
     - 예상값: `Continuous_Months=14`, `Incentive=2,600,000 VND`
   - **Root Cause**: `get_aql_inspector_continuous_months()` 함수에서 Month 객체를 JSON 키 형식과 다르게 변환
     - **잘못된 변환**: `str(Month.OCTOBER)` = `"Month.OCTOBER"`
     - **올바른 변환**: `Month.OCTOBER.full_name.lower()` = `"october"`
     - JSON 키: `"october_2025_incentive"` (lowercase)
     - 생성된 키: `"Month.OCTOBER_2025_incentive"` (불일치!)
     - 결과: 이전 달 데이터를 찾지 못함 → 기본값 0 반환 → 1개월로 리셋
   - **Solution**: Line 3204, 3211에서 Month 객체 변환 방식 수정
     ```python
     # 수정 전
     prev_month_key = f"{prev_month}_{self.config.year}_incentive"

     # 수정 후
     prev_month_key = f"{prev_month.full_name.lower()}_{self.config.year}_incentive"
     ```
   - **Impact**:
     | Employee | 수정 전 | 수정 후 |
     |----------|---------|---------|
     | 620020923 | 1개월, 850K VND | **14개월, 2,600K VND** ✅ |
     | 618110077 | 1개월, 850K VND | **14개월, 2,600K VND** ✅ |
     | 619100307 | 1개월, 850K VND | **14개월, 2,600K VND** ✅ |
     | 620120306 | 1개월, 850K VND | **8개월, 1,850K VND** ✅ |
     | 622030225 | 1개월, 850K VND | **8개월, 1,850K VND** ✅ |
   - **Incentive Calculation Verification**:
     - 14개월: Part1(1,000K) + Part2(700K) + Part3(900K) = 2,600,000 VND ✅
     - 8개월: Part1(650K) + Part2(700K) + Part3(500K) = 1,850,000 VND ✅
   - **Implementation**: `src/step1_인센티브_계산_개선버전.py:3195-3212`
   - **Commit**: `5f1a6b43`
   - **Prevention**: Always use `.full_name.lower()` when converting Month objects to JSON key strings

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

### Current Version: 9.0 (as of 2025-12-01)

**Critical Architecture Decision**: The system implements **fallback pattern** for version transitions to ensure backward compatibility when reading previous month data.

**Important Version Fix (2025-12-01):**
- **V9.0 is the correct/latest version** with BFS logic applied for manager incentive calculation
- **V9.1 was an older version** created on 2025-11-18 (BEFORE BFS fix) - now archived
- File reading priority: **V9.0 → V8.02** (V9.1 removed from fallback)

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

**Problem**: When December 2025 needs November 2025 data, multiple versions may exist.

**Solution**: Fallback pattern in `step1_인센티브_계산_개선버전.py` (Updated 2025-12-01):

```python
# Lines 1214-1223: Previous month file loading (V9.0 first, V9.1 removed)
excel_patterns = [
    # V9.0 version (latest - BFS applied)
    f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
    f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
    # V8.02 version (backward compatibility)
    f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv",
    f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv"
]
```

**Why V9.1 Was Removed (2025-12-01)**:
- V9.1 was created on 2025-11-18 BEFORE BFS logic was applied
- V9.0 files were regenerated on 2025-12-01 WITH BFS logic
- V9.1 files moved to `output_files/archive/` to prevent confusion
- **V9.0 is now the only current version** with correct manager incentive calculations

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
