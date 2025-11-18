# QIP Incentive Dashboard System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Private-red.svg)]()

**Quality Inspection Process (QIP) Incentive Calculation and Dashboard System** for factory worker incentive management with automated data processing, interactive dashboards, and multi-language support (Korean/English/Vietnamese).

---

## 🚀 Quick Start

### One-Click Execution

```bash
./action.sh
```

Select month and year, and the system will automatically:
1. Generate monthly configuration
2. Sync data from Google Drive
3. Calculate incentives
4. Generate interactive HTML dashboard
5. Validate data integrity

---

## 📊 Features

### Core Capabilities
- ✅ **Automated Incentive Calculation** - JSON-driven business rules
- ✅ **Interactive Dashboards** - Self-contained HTML with Chart.js
- ✅ **Multi-Language Support** - Korean, English, Vietnamese
- ✅ **Google Drive Integration** - Automatic data synchronization
- ✅ **Data Validation** - Comprehensive HR data integrity checks
- ✅ **Progressive Incentives** - 12-month accumulation tracking
- ✅ **Consecutive AQL Failure Detection** - 3-month tracking

### Technical Highlights
- **Zero Fake Data Policy** - "우리사전에 가짜 데이타는 없다"
- **100% Condition Fulfillment** - No partial incentives (80-99% = 0 VND)
- **JSON-Driven Configuration** - All business logic externalized
- **Type-Based Classification** - TYPE-1/2/3 employee differentiation

---

## 📁 Project Structure

```
Dashboard Incentive Version 8_1_sharing/
├── 📄 integrated_dashboard_final.py  # Main dashboard generator (Version 8)
├── 📄 action.sh                      # One-click execution script
├── 📄 requirements.txt               # Python dependencies
├── 📄 CLAUDE.md                      # Detailed project documentation
│
├── 📂 src/                           # Core business logic (25 modules)
│   ├── step0_create_monthly_config.py
│   ├── step1_인센티브_계산_개선버전.py  # Incentive calculation engine
│   ├── step2_dashboard_version4.py
│   ├── google_drive_manager.py
│   ├── validate_hr_data.py
│   └── ...
│
├── 📂 dashboard_v2/                  # Modular dashboard (Version 6)
│   ├── modules/
│   │   ├── complete_renderer.py
│   │   └── incentive_calculator.py
│   ├── static/js/
│   └── templates/
│
├── 📂 config_files/                  # Configuration files (141 JSONs)
│   ├── position_condition_matrix.json  # Master business rules
│   ├── assembly_inspector_continuous_months.json
│   └── config_[month]_[year].json
│
├── 📂 scripts/                       # Utility scripts
│   ├── verification/
│   ├── analysis/
│   ├── utils/
│   ├── dashboard_tools/
│   └── legacy/
│
├── 📂 docs/                          # Documentation
│   ├── guides/
│   ├── reports/
│   ├── architecture/
│   └── improvements/
│
├── 📂 input_files/                   # Input data
│   ├── attendance/
│   ├── AQL history/
│   └── [year]년 [month] 인센티브 지급 세부 정보.csv
│
└── 📂 output_files/                  # Generated outputs
    ├── *.xlsx                        # Excel reports
    ├── *.csv                         # CSV data
    └── Incentive_Dashboard_*.html    # Interactive dashboards
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup

```bash
# 1. Clone or extract the project
cd "Dashboard  Incentive Version 8_1_sharing"

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure Google Drive credentials
# Follow: docs/guides/GOOGLE_DRIVE_SETUP.md
```

---

## 📖 Usage

### Method 1: Automated Execution (Recommended)

```bash
./action.sh
```

Follow the interactive prompts to select month and year.

### Method 2: Manual Step-by-Step

```bash
# Step 1: Create monthly configuration
python src/step0_create_monthly_config.py --month september --year 2025

# Step 2: Calculate incentives
python src/step1_인센티브_계산_개선버전.py --config config_files/config_september_2025.json

# Step 3: Generate dashboard
python integrated_dashboard_final.py --month 9 --year 2025
```

### Method 3: Version 6 Dashboard (Modular)

```bash
python dashboard_v2/generate_dashboard.py --month september --year 2025
```

---

## 📋 Business Logic

All business rules are defined in `config_files/position_condition_matrix.json`:

### Employee Types
- **TYPE-1**: Management & specialized inspectors (100K-1,000K VND)
  - Assembly Inspector, Model Master, Auditor & Trainer
  - Progressive incentives (12-month accumulation)

- **TYPE-2**: Standard inspectors (50K-300K VND)
  - Attendance-based conditions only

- **TYPE-3**: New members (0 VND)
  - Policy exclusion for first 3 months

### Conditions (10 total)
1. **Attendance Rate** ≥ 88%
2. **Unapproved Absence** ≤ 2 days
3. **Actual Working Days** > 0
4. **Minimum Working Days** ≥ 12
5. **Personal AQL**: Current month failures = 0
6. **Personal AQL**: No 3-month consecutive failures
7. **Team/Area AQL**: No 3-month consecutive failures
8. **Area Reject Rate** < 3%
9. **5PRS Pass Rate** ≥ 95%
10. **5PRS Inspection Quantity** ≥ 100

### Key Rules
- ✅ **100% Condition Fulfillment Required** - No partial incentives
- ✅ **No Fake Data** - Missing data = 0, never estimated
- ✅ **Reset on Failure** - Progressive counters reset on condition failure

---

## 🧪 Testing & Validation

```bash
# Full system test
./test_final.sh

# Quick dashboard validation
python quick_verify.py

# HR data validation
python src/validate_hr_data.py 9 2025

# JSON-Excel consistency check
python src/validate_excel_json_consistency.py
```

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive project guide
- **[docs/guides/](docs/guides/)** - Setup and usage guides
- **[docs/architecture/](docs/architecture/)** - System architecture
- **[docs/reports/](docs/reports/)** - Verification reports

---

## 🔧 Configuration

### Monthly Config Example

```json
{
  "month": "september",
  "year": 2025,
  "working_days": 26,
  "attendance_file": "input_files/attendance/converted/2025년 09월 출근.xlsx",
  "aql_file": "input_files/AQL history/2025년 09월 AQL 이력.xlsx",
  "5prs_file": "input_files/5PRS history/2025년 09월 5PRS 검사현황.xlsx"
}
```

### Business Rules (JSON-Driven)

All conditions, position mappings, and incentive ranges are defined in:
`config_files/position_condition_matrix.json`

---

## 🌐 Multi-Language Support

Toggle languages in the dashboard:
- 🇰🇷 **Korean** (한국어)
- 🇬🇧 **English**
- 🇻🇳 **Vietnamese** (Tiếng Việt)

Translations managed in: `config_files/dashboard_translations.json`

---

## 📊 Output Files

### Excel/CSV Reports
```
output_files/output_QIP_incentive_[month]_[year]_Complete_V9.0_Complete.xlsx
output_files/output_QIP_incentive_[month]_[year]_Complete_V9.0_Complete.csv
```

### Interactive Dashboard
```
output_files/Incentive_Dashboard_[year]_[MM]_Version_9.0.html
```

**Dashboard Features**:
- KPI summary cards
- Position/TYPE summary tables
- Condition fulfillment statistics
- Organization chart hierarchy
- Employee details with search/filter
- Interactive modals for detailed views

---

## 🚨 Common Issues

### Issue: Working Days = 0
**Solution**: Run attendance calculation before incentive calculation
```bash
python src/calculate_working_days_from_attendance.py september 2025
```

### Issue: Missing Previous Month Data
**Solution**: System shows 0 (no fake data generated)
```bash
python src/sync_previous_incentive.py september 2025
```

### Issue: Dashboard Shows 0 Values
**Solution**: Check NaN handling in Version 6
```bash
# Use Version 8 instead
python integrated_dashboard_final.py --month 9 --year 2025
```

---

## 🤝 Contributing

This is a private project. For questions or support, contact the project maintainer.

---

## 📜 License

Private - All rights reserved

---

## 🎯 Version History

- **Version 9.0** (Current) - Web-based dashboard with enhanced features
- **Version 8.02** - Integrated dashboard with full feature set
- **Version 6.0** - Modular architecture (82% code reduction)
- **Version 5.0** - Stable single-file dashboard

---

## 📞 Support

For issues or questions:
1. Check [CLAUDE.md](CLAUDE.md) for detailed documentation
2. Review [docs/guides/](docs/guides/) for setup instructions
3. Check [docs/reports/](docs/reports/) for known issues

---

**Last Updated**: 2025-10-03
**Maintainer**: Project Team
