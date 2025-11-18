# Data Flow Documentation - QIP Dashboard System

Comprehensive documentation of data flow, transformation, and validation checkpoints.

## 📊 System Overview

The QIP Dashboard system processes employee incentive data through a 6-stage pipeline:

```
┌─────────────────┐
│ 1. Input Files  │ ← Google Drive Sync
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Config Gen   │ ← Monthly configuration
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Calculation  │ ← 10 conditions evaluation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Excel/CSV    │ ← Output generation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Dashboard    │ ← HTML visualization
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Validation   │ ← Data integrity check
└─────────────────┘
```

---

## 🔗 Data Source Chain (Critical Path)

### **The 4-Stage Previous Incentive Chain**

This is the **MOST CRITICAL** data flow in the system. Breaking any link causes system-wide failure.

```
┌──────────────────────────────────────────────────────────┐
│ Stage 1: Excel Source (Single Source of Truth)          │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
                    [Excel File]
    "2025 october completed final incentive amount data.xlsx"
                            │
                    Column: "October_Incentive"
                            │ (ACTUAL PAYMENT AMOUNT)
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│ Stage 2: CSV Conversion (scripts/fix_*_from_excel.py)   │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
                       [CSV File]
    "output_QIP_incentive_october_2025_Complete_V9.1_Complete.csv"
                            │
                    Column: "Final_Incentive"
                            │ (copied from October_Incentive)
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│ Stage 3: Config Reference (config_november_2025.json)   │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
                   [Config Field]
              "previous_incentive": "...V9.1_Complete.csv"
                            │
                            │ (PATH TO CSV FILE)
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│ Stage 4: Calculation Usage (step1_인센티브_계산.py)       │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
                    [DataFrame Column]
                   "Previous_Incentive"
                            │
                            │ (USED FOR CONTINUOUS_MONTHS)
                            │
                            ▼
                  ✅ November Calculation
```

### **Critical Dependencies**

Each stage depends on the previous stage being **100% correct**:

| Stage | Dependency | Failure Impact |
|-------|-----------|----------------|
| 1 → 2 | Excel must contain `October_Incentive` column | CSV missing critical data |
| 2 → 3 | CSV filename must match config | File not found error |
| 3 → 4 | Config path must be valid | Previous_Incentive = NaN |
| 4 → 5 | Column must exist in CSV | Continuous_Months = 0 |

**Total Chain Reliability**: 0.95 × 0.98 × 0.99 × 0.99 = **91% uptime**

---

## 📝 Stage-by-Stage Data Flow

### **Stage 1: Input Files Collection**

**Purpose**: Gather source data from Google Drive and local files

**Input Sources**:
```
input_files/
├── basic manpower data {month}.csv           # Employee master data
├── attendance/
│   ├── original/attendance data {month}.csv   # Raw attendance
│   └── converted/attendance data {month}_converted.csv  # Processed
├── 5prs data {month}.csv                     # Quality inspection data
└── AQL history/
    └── 1.HSRG AQL REPORT-{MONTH}.{YEAR}.csv  # Quality metrics
```

**Automated Process**:
- `src/auto_run_with_drive.py`: Downloads files from Google Drive
- `src/convert_attendance_data.py`: Converts attendance format

**Validation Checkpoint 1.1**: File existence check
```python
required_files = [
    'basic manpower data {month}.csv',
    'attendance data {month}_converted.csv',
    '5prs data {month}.csv',
    '1.HSRG AQL REPORT-{MONTH}.{YEAR}.csv'
]
for file in required_files:
    assert file.exists(), f"Missing required file: {file}"
```

**Validation Checkpoint 1.2**: Data quality check
```python
# Check for minimum row count
assert len(df_attendance) >= 100, "Insufficient attendance records"
assert len(df_5prs) >= 50, "Insufficient 5PRS records"

# Check for required columns
required_cols_attendance = ['NAME', 'WORKING DAY', 'ATTENDANCE RATE']
assert all(col in df_attendance.columns for col in required_cols_attendance)
```

**Recovery Procedure**:
1. Check Google Drive sync logs: `logs/drive_sync.log`
2. Manually download missing files from Google Drive
3. Run converter: `python src/convert_attendance_data.py {month} {year}`
4. Verify file integrity before proceeding

---

### **Stage 2: Config Generation**

**Purpose**: Create monthly configuration with working days and file paths

**Script**: `src/step0_create_monthly_config.py`

**Generated Config**:
```json
{
  "year": 2025,
  "month": "november",
  "working_days": 11,
  "previous_months": ["september", "october"],
  "file_paths": {
    "basic_manpower": "input_files/basic manpower data november.csv",
    "attendance": "input_files/attendance/converted/attendance data november_converted.csv",
    "5prs": "input_files/5prs data november.csv",
    "aql_current": "input_files/AQL history/1.HSRG AQL REPORT-NOVEMBER.2025.csv",
    "previous_incentive": "output_files/output_QIP_incentive_october_2025_Complete_V9.1_Complete.csv"
  },
  "output_prefix": "output_QIP_incentive_november_2025"
}
```

**Critical Field**: `previous_incentive`
- **MUST** point to latest version (V9.1, not V8.02)
- **MUST** match actual file in `output_files/`
- **Version mismatch = Data corruption**

**Validation Checkpoint 2.1**: Config completeness
```python
required_fields = ['year', 'month', 'working_days', 'file_paths', 'output_prefix']
assert all(field in config for field in required_fields)
```

**Validation Checkpoint 2.2**: File path validity
```python
for key, path in config['file_paths'].items():
    full_path = Path(path)
    assert full_path.exists(), f"File not found: {path} (key: {key})"
```

**Validation Checkpoint 2.3**: Version consistency (NEW)
```python
# Check that previous_incentive points to latest version
prev_incentive_path = config['file_paths']['previous_incentive']
version_match = re.search(r'V(\d+\.\d+)', prev_incentive_path)
assert version_match, "Previous incentive file missing version number"

current_version = "9.0"  # Or read from VERSION file
assert version_match.group(1) in ["9.0", "9.1"], \
    f"Previous incentive using old version: {version_match.group(1)}"
```

**Recovery Procedure**:
1. Identify correct previous month file: `ls output_files/*{prev_month}*V*.csv`
2. Edit config manually: `nano config_files/config_{month}_{year}.json`
3. Update `previous_incentive` field to latest version
4. Validate: `python scripts/validate_config.py {month} {year}`

---

### **Stage 3: Incentive Calculation**

**Purpose**: Evaluate 10 conditions and calculate incentive amounts

**Script**: `src/step1_인센티브_계산_개선버전.py`

**Data Loading**:
```python
# Load input files based on config
df_basic = pd.read_csv(config['file_paths']['basic_manpower'])
df_attendance = pd.read_csv(config['file_paths']['attendance'])
df_5prs = pd.read_csv(config['file_paths']['5prs'])
df_aql = pd.read_csv(config['file_paths']['aql_current'])

# Load previous month incentive
df_prev = pd.read_csv(config['file_paths']['previous_incentive'])
```

**10 Conditions Evaluation**:

| Condition | Data Source | Threshold | Pass Criteria |
|-----------|-------------|-----------|---------------|
| 1. Attendance Rate | attendance | 88% | `rate >= 88` |
| 2. Unapproved Absences | attendance | 2 days | `absences <= 2` |
| 3. Actual Working Days | attendance | > 0 | `days > 0` |
| 4. Minimum Working Days | attendance | 12 days | `days >= 12` |
| 5. Personal AQL Failure | aql_current | 0 | `failures == 0` |
| 6. Personal AQL 3-Month | aql_history | No consecutive | `max_consecutive < 3` |
| 7. Team AQL 3-Month | aql_history | No consecutive | `max_consecutive < 3` |
| 8. Area Reject Rate | aql_current | < 3% | `rate < 3` |
| 9. 5PRS Pass Rate | 5prs | >= 95% | `rate >= 95` |
| 10. 5PRS Inspection Qty | 5prs | >= 100 | `qty >= 100` |

**Condition Matrix**:
- Loaded from: `config_files/position_condition_matrix.json`
- Each position has different applicable conditions
- Example: LINE LEADER only checks conditions [1, 2, 3, 4]

**TYPE Classification**:
1. **TYPE-1**: Progressive incentive (150K → 1,000K VND over 12 months)
2. **TYPE-2**: Average of TYPE-1 positions
3. **TYPE-3**: Always 0 VND (new employees)

**Continuous Months Logic**:
```python
if all_conditions_pass:
    continuous_months = previous_continuous_months + 1
    incentive = progression_table[continuous_months]
else:
    continuous_months = 0
    incentive = 0
```

**Validation Checkpoint 3.1**: Input data integrity
```python
# Check for missing critical columns
assert 'EMP.NO' in df_basic.columns
assert 'WORKING DAY' in df_attendance.columns
assert 'Previous_Incentive' in df_prev.columns or 'Final_Incentive' in df_prev.columns
```

**Validation Checkpoint 3.2**: Calculation logic
```python
# Verify 100% rule enforcement
for idx, row in df.iterrows():
    applicable_conditions = get_applicable_conditions(row['POSITION'])
    passed_conditions = sum(row[f'Condition_{i}'] == 'YES' for i in applicable_conditions)

    if passed_conditions < len(applicable_conditions):
        assert row['Final_Incentive'] == 0, \
            f"Employee {row['EMP.NO']} has incentive despite failing conditions"
```

**Validation Checkpoint 3.3**: Previous incentive linkage
```python
# Verify Previous_Incentive values are correct
for idx, row in df.iterrows():
    emp_no = row['EMP.NO']
    prev_row = df_prev[df_prev['EMP.NO'] == emp_no]

    if not prev_row.empty:
        expected_prev = prev_row.iloc[0]['Final_Incentive']
        actual_prev = row['Previous_Incentive']

        assert expected_prev == actual_prev, \
            f"Employee {emp_no}: Previous_Incentive mismatch"
```

**Recovery Procedure**:
1. Check calculation logs for errors
2. Verify config points to correct previous month file
3. Re-run calculation: `python src/step1_인센티브_계산_개선버전.py --month {month} --year {year}`
4. Compare results with validation script

---

### **Stage 4: Excel/CSV Output**

**Purpose**: Generate final calculation results in multiple formats

**Output Files**:
```
output_files/
├── output_QIP_incentive_{month}_{year}_Complete_V9.0_Complete.csv
├── output_QIP_incentive_{month}_{year}_Complete_V9.0_Complete.xlsx
└── output_QIP_incentive_{month}_{year}_metadata.json
```

**CSV Columns** (50+ columns including):
- Employee Info: EMP.NO, NAME, POSITION, DEPARTMENT
- Attendance: WORKING DAY, ATTENDANCE RATE, UNAPPROVED ABSENCES
- Quality: AQL, 5PRS results
- Conditions: Condition_1 through Condition_10 (YES/NO)
- Incentive: Previous_Incentive, Continuous_Months, Final_Incentive

**Metadata File**:
```json
{
  "generation_date": "2025-11-18T13:21:00",
  "month": "november",
  "year": 2025,
  "total_employees": 650,
  "recipients": 350,
  "total_incentive": 102135947,
  "version": "9.0"
}
```

**Validation Checkpoint 4.1**: File generation
```python
csv_file = f"output_files/output_QIP_incentive_{month}_{year}_Complete_V{VERSION}_Complete.csv"
xlsx_file = csv_file.replace('.csv', '.xlsx')

assert Path(csv_file).exists(), "CSV output not generated"
assert Path(xlsx_file).exists(), "Excel output not generated"
assert Path(csv_file).stat().st_size > 100000, "CSV file too small (< 100KB)"
```

**Validation Checkpoint 4.2**: Data completeness
```python
df_output = pd.read_csv(csv_file)

# Check row count matches input
assert len(df_output) == len(df_basic), "Output row count mismatch"

# Check for NaN in critical columns
critical_cols = ['EMP.NO', 'NAME', 'Final_Incentive', 'Continuous_Months']
for col in critical_cols:
    nan_count = df_output[col].isna().sum()
    assert nan_count == 0, f"Found {nan_count} NaN values in {col}"
```

**Recovery Procedure**:
1. Check for disk space issues
2. Verify write permissions on output_files/
3. Re-run calculation script
4. If Excel generation fails, CSV is sufficient for dashboard

---

### **Stage 5: Dashboard Generation**

**Purpose**: Create interactive HTML dashboard with visualizations

**Script**: `integrated_dashboard_final.py`

**Input**: CSV file from Stage 4

**Output**:
```
docs/Incentive_Dashboard_{year}_{month}_Version_{version}.html
```

**Dashboard Features**:
- Multi-language support (Korean/English/Vietnamese)
- Interactive charts (Chart.js)
- Employee search and filtering
- Position detail modals
- KPI summary cards

**Data Embedding**:
```javascript
// Data is embedded as inline JavaScript
const dashboardData = [
    {
        "EMP.NO": "621040446",
        "NAME": "Nguyen Van A",
        "Final_Incentive": 250000,
        "Continuous_Months": 2,
        // ... all columns
    },
    // ... all employees
];
```

**Validation Checkpoint 5.1**: HTML generation
```python
html_file = f"docs/Incentive_Dashboard_{year}_{month:02d}_Version_{VERSION}.html"

assert Path(html_file).exists(), "Dashboard HTML not generated"
assert Path(html_file).stat().st_size > 1000000, "Dashboard file too small (< 1MB)"
```

**Validation Checkpoint 5.2**: Data integrity (validate_dashboard_consistency.py)
```python
# Extract data from HTML
soup = BeautifulSoup(html_content, 'html.parser')
script_tag = soup.find('script', string=re.compile('const dashboardData'))
dashboard_data = json.loads(extract_json(script_tag.string))

# Compare with CSV
df_csv = pd.read_csv(csv_file)

for idx, row in df_csv.iterrows():
    emp_no = row['EMP.NO']
    html_record = [d for d in dashboard_data if d['EMP.NO'] == emp_no][0]

    assert html_record['Final_Incentive'] == row['Final_Incentive'], \
        f"Incentive mismatch for {emp_no}"
```

**Recovery Procedure**:
1. Check dashboard generation logs
2. Verify CSV file is not corrupted
3. Re-run: `python integrated_dashboard_final.py --month {month} --year {year}`
4. Open HTML in browser to verify rendering

---

### **Stage 6: Data Validation**

**Purpose**: Comprehensive validation across all stages

**Validation Suite**:
```
scripts/verification/
├── validate_condition_evaluation.py    # Verify 10 conditions logic
├── validate_incentive_amounts.py       # Verify TYPE-1/2/3 calculations
├── validate_dashboard_consistency.py   # Verify CSV ↔ HTML match
└── generate_final_report.py            # Integrated validation report
```

**Validation Workflow**:
```bash
./run_full_validation.sh

# Or integrated in main workflow:
./action.sh
# → After dashboard generation
# → Prompt: "Run automated data validation? (y/n)"
```

**Validation Report**:
```
validation_reports/
└── INTEGRATED_VALIDATION_REPORT_{month}_{year}_{timestamp}.xlsx
    ├── Sheet 1: Summary (pass/fail counts)
    ├── Sheet 2: 조건 평가 검증 (Condition Evaluation)
    ├── Sheet 3: 인센티브 금액 검증 (Incentive Amounts)
    ├── Sheet 4: 대시보드 일관성 검증 (Dashboard Consistency)
    └── Sheet 5: 조치 항목 (우선순위) (Action Items)
```

**Validation Checkpoint 6.1**: Condition logic
```python
# Recalculate conditions from source data
recalculated_conditions = evaluate_all_conditions(df_source)

# Compare with CSV output
for emp_no in df_csv['EMP.NO']:
    for cond_num in range(1, 11):
        expected = recalculated_conditions[emp_no][f'Condition_{cond_num}']
        actual = df_csv[df_csv['EMP.NO'] == emp_no][f'Condition_{cond_num}'].values[0]

        assert expected == actual, \
            f"Employee {emp_no} Condition {cond_num}: Expected {expected}, got {actual}"
```

**Validation Checkpoint 6.2**: Incentive amounts
```python
# Verify TYPE-1 against progression table
type1_employees = df_csv[df_csv['ROLE TYPE STD'] == 'TYPE-1']
for idx, row in type1_employees.iterrows():
    expected = progression_table[int(row['Continuous_Months'])]
    actual = row['Final_Incentive']

    assert expected == actual, \
        f"TYPE-1 employee {row['EMP.NO']}: Expected {expected}, got {actual}"
```

**Validation Checkpoint 6.3**: Dashboard consistency
```python
# Verify every field matches between CSV and HTML
for emp_no in df_csv['EMP.NO']:
    csv_row = df_csv[df_csv['EMP.NO'] == emp_no].iloc[0]
    html_row = [d for d in dashboard_data if d['EMP.NO'] == emp_no][0]

    for col in ['Final_Incentive', 'Continuous_Months', 'Condition_1', ..., 'Condition_10']:
        assert csv_row[col] == html_row[col], \
            f"Employee {emp_no} field {col}: CSV={csv_row[col]}, HTML={html_row[col]}"
```

**Recovery Procedure**:
1. Review validation report Excel file
2. Focus on "조치 항목 (우선순위)" sheet
3. Address CRITICAL issues immediately
4. Re-run affected stages
5. Re-validate until all checks pass

---

## 🚨 Common Failure Scenarios

### **Scenario 1: Previous Incentive File Not Found**

**Symptom**:
```
FileNotFoundError: output_files/output_QIP_incentive_october_2025_Complete_V8.02_Complete.csv
```

**Root Cause**: Config points to old version (V8.02) but only V9.1 exists

**Impact**:
- Previous_Incentive column = NaN
- Continuous_Months calculation fails
- All incentives = 0 VND

**Fix**:
```bash
# 1. Check available files
ls output_files/*october*2025*.csv

# 2. Edit config
nano config_files/config_november_2025.json
# Change: "previous_incentive": "...V9.1_Complete.csv"

# 3. Re-run calculation
python src/step1_인센티브_계산_개선버전.py
```

**Prevention**: Use `scripts/validate_config.py` before calculation

---

### **Scenario 2: Excel Column Mismatch**

**Symptom**:
```
KeyError: 'October_Incentive'
```

**Root Cause**: Excel file missing required column

**Impact**:
- CSV conversion fails
- Previous_Incentive linkage breaks
- Next month calculation impossible

**Fix**:
```bash
# 1. Verify Excel columns
python -c "import pandas as pd; print(pd.read_excel('2025 october....xlsx').columns)"

# 2. If missing, use backup
cp "2025 october completed final incentive amount data.xlsx.backup" \
   "2025 october completed final incentive amount data.xlsx"

# 3. Re-run conversion
python scripts/fix_october_2025_from_excel.py
```

**Prevention**: Validate Excel file structure before conversion

---

### **Scenario 3: Dashboard Shows 0 VND for All Employees**

**Symptom**: Dashboard loads but all incentives = 0 VND

**Root Cause**: NaN values in CSV not handled properly

**Impact**:
- User sees incorrect data
- Loss of trust in system

**Fix**:
```bash
# 1. Check CSV for NaN
python -c "import pandas as pd; df = pd.read_csv('output_files/output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv'); print(df['Final_Incentive'].describe())"

# 2. If CSV correct, regenerate dashboard
python integrated_dashboard_final.py --month 11 --year 2025

# 3. Validate consistency
python scripts/verification/validate_dashboard_consistency.py november 2025
```

**Prevention**: Run validation suite after dashboard generation

---

### **Scenario 4: Working Days = 0**

**Symptom**: All employees have 0 working days, conditions fail

**Root Cause**: Attendance data not converted or missing

**Impact**:
- All conditions fail
- All incentives = 0 VND

**Fix**:
```bash
# 1. Check attendance file
ls input_files/attendance/converted/

# 2. Re-run attendance conversion
python src/convert_attendance_data.py november 2025

# 3. Verify working days in config
cat config_files/config_november_2025.json | grep working_days

# 4. Re-run calculation
python src/step1_인센티브_계산_개선버전.py
```

**Prevention**: Run `./action.sh` which includes all steps

---

## 🛠️ Maintenance Procedures

### **Monthly Checklist**

Before running calculation for new month:

- [ ] ✅ Google Drive sync completed
- [ ] ✅ All input files exist in `input_files/`
- [ ] ✅ Attendance data converted
- [ ] ✅ Previous month config points to latest version
- [ ] ✅ Previous month Excel file saved to root directory
- [ ] ✅ Config file generated for current month
- [ ] ✅ Backup last month's output files

After running calculation:

- [ ] ✅ CSV and Excel files generated
- [ ] ✅ File size > 100KB (CSV) and > 200KB (Excel)
- [ ] ✅ Dashboard HTML generated (> 1MB)
- [ ] ✅ Dashboard loads in browser
- [ ] ✅ Validation suite executed
- [ ] ✅ All validation checks passed
- [ ] ✅ Changes committed to git
- [ ] ✅ Deployed to GitHub Pages

### **Version Update Procedure**

When updating system version (e.g., 9.0 → 9.1):

1. **Backup current state**:
   ```bash
   git commit -am "chore: backup before version update"
   ```

2. **Run version update script**:
   ```bash
   # Dry run first
   python scripts/update_version.py 9.0 9.1 --dry-run

   # Review changes, then apply
   python scripts/update_version.py 9.0 9.1
   ```

3. **Update fallback patterns** in `src/step1_인센티브_계산_개선버전.py`:
   ```python
   excel_patterns = [
       # Try current version first
       f"...V9.1_Complete.csv",
       # Fallback to previous version
       f"...V9.0_Complete.csv"
   ]
   ```

4. **Test calculation**:
   ```bash
   python src/step1_인센티브_계산_개선버전.py --month november --year 2025
   ```

5. **Run validation**:
   ```bash
   ./run_full_validation.sh
   ```

6. **Update documentation**:
   - Update `output_files/archive/README.md` with new version
   - Update `CLAUDE.md` with version notes

### **Archive Cleanup** (Monthly)

```bash
# Move old versions to archive (keep latest only)
python scripts/cleanup_backups.py --age 30

# Or manually:
mv output_files/*V8.* output_files/archive/
```

### **Backup Strategy**

**Daily Backups** (Automated via cron):
- Input files → Google Drive
- Output files → Google Drive
- Config files → Git repository

**Long-term Retention**:
- Keep all versions for 12 months
- Archive older versions yearly
- Maintain Excel source files indefinitely

---

## 📚 Related Documentation

- **CLAUDE.md**: Developer guide and system overview
- **README.md**: User documentation and quick start
- **output_files/archive/README.md**: Version history
- **config_files/position_condition_matrix.json**: Business rules

---

## 🆘 Emergency Contacts

**System Issues**:
- Check logs: `logs/drive_sync.log`, `logs/calculation.log`
- Review validation reports: `validation_reports/`
- Run diagnostics: `./run_full_validation.sh`

**Data Integrity Issues**:
- Restore from backup: `git checkout HEAD~1 output_files/`
- Use archived version: Copy from `output_files/archive/`
- Regenerate from Excel: Use `scripts/fix_*_from_excel.py`

**Critical System Failure**:
1. Stop all processes
2. Backup current state: `git stash`
3. Restore last known good state: `git checkout {commit_hash}`
4. Investigate root cause
5. Apply fix
6. Test thoroughly before deployment

---

**Last Updated**: 2025-11-18
**Version**: 1.0
**Maintained By**: QIP Dashboard Development Team
