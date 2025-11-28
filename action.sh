#!/bin/bash

# ============================================================
# QIP 인센티브 보고서 One-Click 생성 스크립트
# macOS 전용
# ============================================================

# 색상 코드 정의 (macOS Terminal 호환)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 현재 스크립트 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 타이틀 출력
clear
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}         📊 QIP Incentive Report One-Click Generator${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed.${NC}"
    echo "Install with Homebrew: brew install python3"
    exit 1
fi

# Year selection
echo -e "${YELLOW}📅 Select year:${NC}"
echo "  1) 2025"
echo "  2) 2026"
echo -e "${WHITE}Choice (1 or 2): ${NC}\c"
read year_choice

case $year_choice in
    1)
        YEAR=2025
        ;;
    2)
        YEAR=2026
        ;;
    *)
        echo -e "${RED}❌ Invalid choice.${NC}"
        exit 1
        ;;
esac

# Month selection
echo ""
echo -e "${YELLOW}📅 Select month:${NC}"
echo "  1) January"
echo "  2) February"
echo "  3) March"
echo "  4) April"
echo "  5) May"
echo "  6) June"
echo "  7) July"
echo "  8) August"
echo "  9) September"
echo "  10) October"
echo "  11) November"
echo "  12) December"
echo -e "${WHITE}Choice (1-12): ${NC}\c"
read month_choice

# Month name mapping
case $month_choice in
    1) MONTH="january" ; MONTH_EN="January" ; MONTH_NUM=1 ;;
    2) MONTH="february" ; MONTH_EN="February" ; MONTH_NUM=2 ;;
    3) MONTH="march" ; MONTH_EN="March" ; MONTH_NUM=3 ;;
    4) MONTH="april" ; MONTH_EN="April" ; MONTH_NUM=4 ;;
    5) MONTH="may" ; MONTH_EN="May" ; MONTH_NUM=5 ;;
    6) MONTH="june" ; MONTH_EN="June" ; MONTH_NUM=6 ;;
    7) MONTH="july" ; MONTH_EN="July" ; MONTH_NUM=7 ;;
    8) MONTH="august" ; MONTH_EN="August" ; MONTH_NUM=8 ;;
    9) MONTH="september" ; MONTH_EN="September" ; MONTH_NUM=9 ;;
    10) MONTH="october" ; MONTH_EN="October" ; MONTH_NUM=10 ;;
    11) MONTH="november" ; MONTH_EN="November" ; MONTH_NUM=11 ;;
    12) MONTH="december" ; MONTH_EN="December" ; MONTH_NUM=12 ;;
    *)
        echo -e "${RED}❌ Invalid choice.${NC}"
        exit 1
        ;;
esac

# Confirmation
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}Selected date: ${YEAR} ${MONTH_EN}${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Continue? (y/n): ${NC}\c"
read confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}Cancelled.${NC}"
    exit 0
fi

# Config 파일 경로
CONFIG_FILE="config_files/config_${MONTH}_${YEAR}.json"

# Execution function
run_step() {
    local step_name=$1
    local command=$2

    echo ""
    echo -e "${PURPLE}▶ ${step_name}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    eval $command
    local result=$?

    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✅ ${step_name} completed!${NC}"
        return 0
    else
        echo -e "${RED}❌ ${step_name} failed!${NC}"
        echo -e "${YELLOW}An error occurred. Please check the logs.${NC}"
        return $result
    fi
}

# Start execution
echo ""
echo -e "${GREEN}🚀 Starting report generation...${NC}"

# Step 0: Check/create config file
if [ ! -f "$CONFIG_FILE" ]; then
    echo ""
    echo -e "${YELLOW}⚠️ Config file not found. Create it? (y/n): ${NC}\c"
    read create_config

    if [ "$create_config" = "y" ] || [ "$create_config" = "Y" ]; then
        run_step "Step 0: Config file creation" "python3 src/step0_create_monthly_config.py --month $MONTH --year $YEAR --auto"
    else
        echo -e "${RED}Config file is required. Exiting.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Config file verified: $CONFIG_FILE${NC}"
fi

# Step 0.5: Google Drive sync (CRITICAL for accurate data)
echo ""
echo -e "${YELLOW}📥 Syncing required files from Google Drive...${NC}"
echo -e "${CYAN}   (Using --force-download to ensure latest data)${NC}"
python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR --force-download

SYNC_RESULT=$?

if [ $SYNC_RESULT -ne 0 ]; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ CRITICAL: Google Drive sync failed!${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Using cached files may result in incorrect calculations!${NC}"
    echo -e "${YELLOW}Risks:${NC}"
    echo -e "${YELLOW}  • Old data or mixed month data may be present${NC}"
    echo -e "${YELLOW}  • 5PRS and AQL data accuracy cannot be guaranteed${NC}"
    echo -e "${YELLOW}  • Incentive calculations may be incorrect${NC}"
    echo ""
    echo -e "${WHITE}Options:${NC}"
    echo -e "${WHITE}  1) Continue anyway (not recommended - may cause data errors)${NC}"
    echo -e "${WHITE}  2) Exit and fix Google Drive connection${NC}"
    echo ""
    echo -e "${YELLOW}Choose option (1/2): ${NC}\c"
    read sync_choice

    if [[ $sync_choice != "1" ]]; then
        echo ""
        echo -e "${YELLOW}Please fix Google Drive connection and try again.${NC}"
        echo ""
        echo -e "${CYAN}💡 Troubleshooting:${NC}"
        echo -e "${CYAN}  • Check internet connection${NC}"
        echo -e "${CYAN}  • Verify service account key: credentials/service-account-key.json${NC}"
        echo -e "${CYAN}  • Confirm Google Drive folder permissions${NC}"
        echo -e "${CYAN}  • Check if files are shared with service account email${NC}"
        exit 1
    else
        echo ""
        echo -e "${YELLOW}⚠️ WARNING: Proceeding with potentially outdated files!${NC}"
        echo -e "${YELLOW}⚠️ Please verify calculation results carefully!${NC}"
    fi
else
    echo -e "${GREEN}✅ Google Drive sync completed successfully${NC}"
fi

# Step 0.6: Previous month incentive file sync
echo ""
echo -e "${YELLOW}📥 Checking previous month incentive files...${NC}"
python3 src/sync_previous_incentive.py $MONTH $YEAR

# Step 0.7: Attendance data conversion
run_step "Step 0.7: Attendance data conversion" "python3 src/convert_attendance_data.py $MONTH"
CONVERT_RESULT=$?

# Warning if attendance data conversion fails
if [ $CONVERT_RESULT -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Problem with attendance data conversion. Automatic working_days calculation may not be possible.${NC}"
fi

# Step 0.7.5: Auto-calculate working_days from attendance data and update config
echo ""
echo -e "${YELLOW}🔄 Auto-calculating working days from attendance data and updating config...${NC}"

# Check if script file exists
if [ ! -f "src/calculate_working_days_from_attendance.py" ]; then
    echo -e "${RED}❌ calculate_working_days_from_attendance.py file not found.${NC}"
    echo -e "${YELLOW}⚠️ Using existing working_days value from config.${NC}"
else
    python3 src/calculate_working_days_from_attendance.py $MONTH $YEAR
    CALC_RESULT=$?

    if [ $CALC_RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ Config working_days auto-updated based on actual data${NC}"

        # Display updated working_days value
        WORKING_DAYS=$(python3 -c "import json; config = json.load(open('$CONFIG_FILE')); print(config.get('working_days', 'N/A'))" 2>/dev/null)
        if [ ! -z "$WORKING_DAYS" ] && [ "$WORKING_DAYS" != "N/A" ]; then
            echo -e "${GREEN}   📅 ${MONTH} working days: ${WORKING_DAYS} days${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Auto-calculation failed - using existing working_days value from config${NC}"

        # Display existing working_days value
        EXISTING_DAYS=$(python3 -c "import json; config = json.load(open('$CONFIG_FILE')); print(config.get('working_days', 'N/A'))" 2>/dev/null)
        if [ ! -z "$EXISTING_DAYS" ] && [ "$EXISTING_DAYS" != "N/A" ]; then
            echo -e "${YELLOW}   📅 Existing working_days: ${EXISTING_DAYS} days${NC}"
            echo -e "${YELLOW}   ⚠️ Warning: Please verify if this value is accurate${NC}"
        fi
    fi
fi

# Step 0.8: HR data validation
echo ""
echo -e "${YELLOW}🔍 Validating HR data integrity...${NC}"
python3 src/validate_hr_data.py $month_choice $YEAR
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ HR data validation completed (check error_review folder for results)${NC}"
else
    echo -e "${YELLOW}⚠️ Issues found during HR data validation (check error_review folder)${NC}"
fi

# Step 0.9: AQL file validation (CRITICAL - prevents October 2025 type issues)
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}Step 0.9: AQL File Validation${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MONTH_UPPER=$(echo $MONTH_EN | tr '[:lower:]' '[:upper:]')
AQL_FILE="input_files/AQL history/1.HSRG AQL REPORT-${MONTH_UPPER}.${YEAR}.csv"

if [ -f "$AQL_FILE" ]; then
    echo -e "${BLUE}📋 Validating: $AQL_FILE${NC}"
    python3 scripts/validation/validate_aql_file.py "$AQL_FILE" --month $MONTH_NUM

    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}⚠️  CRITICAL: AQL file validation failed!${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}The AQL file contains data from multiple months or incorrect month data.${NC}"
        echo -e "${YELLOW}This can cause incorrect incentive calculations (like October 2025 issue).${NC}"
        echo ""
        echo -e "${WHITE}Options:${NC}"
        echo -e "${WHITE}  1) Auto-fix (recommended): Remove incorrect month records${NC}"
        echo -e "${WHITE}  2) Continue anyway (not recommended)${NC}"
        echo -e "${WHITE}  3) Exit and fix manually${NC}"
        echo ""
        echo -e "${YELLOW}Choose option (1/2/3): ${NC}\c"
        read aql_fix_choice

        if [[ $aql_fix_choice == "1" ]]; then
            echo ""
            echo -e "${BLUE}🔧 Auto-fixing AQL file...${NC}"
            python3 scripts/validation/validate_aql_file.py "$AQL_FILE" --month $MONTH_NUM --fix

            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}✅ AQL file fixed successfully!${NC}"
            else
                echo ""
                echo -e "${RED}❌ Failed to fix AQL file automatically${NC}"
                echo -e "${YELLOW}Please fix manually and run again.${NC}"
                exit 1
            fi
        elif [[ $aql_fix_choice == "2" ]]; then
            echo ""
            echo -e "${YELLOW}⚠️  WARNING: Continuing with potentially incorrect data${NC}"
            echo -e "${YELLOW}⚠️  Calculation results may be inaccurate!${NC}"
            echo ""
            echo -e "${YELLOW}Are you sure? (y/n): ${NC}\c"
            read confirm_continue
            if [[ $confirm_continue != "y" ]] && [[ $confirm_continue != "Y" ]]; then
                echo -e "${YELLOW}Cancelled.${NC}"
                exit 1
            fi
        else
            echo ""
            echo -e "${YELLOW}Please fix the AQL file manually and run again.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ AQL file validation passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  AQL file not found: $AQL_FILE${NC}"
    echo -e "${YELLOW}Calculations will use available data.${NC}"
    echo ""
    echo -e "${YELLOW}Continue without AQL file? (y/n): ${NC}\c"
    read continue_without_aql
    if [[ $continue_without_aql != "y" ]] && [[ $continue_without_aql != "Y" ]]; then
        exit 1
    fi
fi

# Step 0.10: 5PRS File Validation (CRITICAL - prevents data mixing issues)
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}Step 0.10: 5PRS File Validation${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PRS_FILE="input_files/5prs data ${MONTH}.csv"

if [ -f "$PRS_FILE" ]; then
    echo -e "${BLUE}📋 Validating: $PRS_FILE${NC}"
    python3 scripts/validation/validate_5prs_file.py "$PRS_FILE" --month $MONTH_NUM --year $YEAR

    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}⚠️  CRITICAL: 5PRS file validation failed!${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}The 5PRS file contains data from multiple months.${NC}"
        echo -e "${YELLOW}This will cause incorrect 5PRS pass rate calculations!${NC}"
        echo ""
        echo -e "${WHITE}Options:${NC}"
        echo -e "${WHITE}  1) Auto-fix (recommended): Remove other month records${NC}"
        echo -e "${WHITE}  2) Continue anyway (not recommended)${NC}"
        echo -e "${WHITE}  3) Exit and fix manually${NC}"
        echo ""
        echo -e "${YELLOW}Choose option (1/2/3): ${NC}\c"
        read prs_fix_choice

        if [[ $prs_fix_choice == "1" ]]; then
            echo ""
            echo -e "${BLUE}🔧 Auto-fixing 5PRS file...${NC}"
            python3 scripts/validation/validate_5prs_file.py "$PRS_FILE" --month $MONTH_NUM --year $YEAR --fix

            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}✅ 5PRS file fixed successfully!${NC}"
            else
                echo ""
                echo -e "${RED}❌ Failed to fix 5PRS file automatically${NC}"
                echo -e "${YELLOW}Please fix manually and run again.${NC}"
                exit 1
            fi
        elif [[ $prs_fix_choice == "2" ]]; then
            echo ""
            echo -e "${YELLOW}⚠️  WARNING: Continuing with mixed month data${NC}"
            echo -e "${YELLOW}⚠️  5PRS calculations will be inaccurate!${NC}"
            echo ""
            echo -e "${YELLOW}Are you sure? (y/n): ${NC}\c"
            read confirm_continue
            if [[ $confirm_continue != "y" ]] && [[ $confirm_continue != "Y" ]]; then
                echo -e "${YELLOW}Cancelled.${NC}"
                exit 1
            fi
        else
            echo ""
            echo -e "${YELLOW}Please fix the 5PRS file manually and run again.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ 5PRS file validation passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  5PRS file not found: $PRS_FILE${NC}"
    echo -e "${YELLOW}5PRS conditions will not be evaluated.${NC}"
fi

# Step 1: Incentive calculation
run_step "Step 1: Incentive calculation" "python3 src/step1_인센티브_계산_개선버전.py --config $CONFIG_FILE"
STEP1_RESULT=$?

# Stop if Step 1 fails
if [ $STEP1_RESULT -ne 0 ]; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Error occurred during incentive calculation. Stopping execution.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi

# Step 1.5: Generate JSON from Excel (prepare data for next month calculation)
echo ""
echo -e "${YELLOW}📝 Generating JSON files from Excel data...${NC}"
python3 src/generate_json_from_excel.py \
    --excel "output_files/output_QIP_incentive_${MONTH}_${YEAR}_Complete_V9.0_Complete.csv" \
    --month "$MONTH" \
    --year "$YEAR" \
    --validate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ JSON file generation and validation completed${NC}"
else
    echo -e "${YELLOW}⚠️ Warning during JSON file generation (execution continues)${NC}"
fi

# Step 1.6: Excel vs JSON data consistency validation
echo ""
echo -e "${YELLOW}🔍 Validating Excel vs JSON data consistency...${NC}"
python3 src/validate_excel_json_consistency.py \
    --excel "output_files/output_QIP_incentive_${MONTH}_${YEAR}_Complete_V9.0_Complete.csv" \
    --json "config_files/assembly_inspector_continuous_months.json"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Data consistency validation completed${NC}"
else
    echo -e "${YELLOW}⚠️ Data inconsistencies found (check validation_report)${NC}"
fi

# Step 1.7: Auto-update consecutive AQL failure data
echo ""
echo -e "${YELLOW}🔄 Analyzing and updating 3-month consecutive AQL failure data...${NC}"
python3 src/update_continuous_fail_column.py --month $MONTH --year $YEAR
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Consecutive AQL failure data update completed${NC}"
    echo -e "${CYAN}   • Auto-analyzed previous 2 months AQL files${NC}"
    echo -e "${CYAN}   • Auto-tagged 2-month/3-month consecutive failures${NC}"
else
    echo -e "${YELLOW}⚠️ Warning during consecutive AQL failure update (dashboard generation continues)${NC}"
fi

# Step 1.8: Auto-update AQL Inspector incentive config (Part 1/2/3 tracking)
echo ""
echo -e "${YELLOW}🔄 Updating AQL Inspector incentive config (3-Part calculation)...${NC}"
python3 scripts/auto_update_aql_config.py $MONTH $YEAR
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ AQL Inspector config auto-update completed${NC}"
    echo -e "${CYAN}   • Part 1 (AQL 평가): Updated continuous months${NC}"
    echo -e "${CYAN}   • Part 2 (CFA 자격증): Verified certification status${NC}"
    echo -e "${CYAN}   • Part 3 (HWK 클레임 방지): Updated continuous months${NC}"
else
    echo -e "${YELLOW}⚠️ Warning during AQL Inspector config update (dashboard generation continues)${NC}"
fi

# Step 2: Modular Dashboard generation (improved structure v6.0)
echo ""
echo -e "${GREEN}✨ Generating improved modular dashboard v6.0${NC}"
echo -e "${CYAN}  • Code reduced by 82%: 13,374 → 2,394 lines${NC}"
echo -e "${CYAN}  • Fully modularized for easy maintenance${NC}"
echo -e "${CYAN}  • Compatible with AI tools like Vibe${NC}"
echo ""

run_step "Step 2: HTML Dashboard generation (V9.0 Web-based)" "python3 integrated_dashboard_final.py --month $MONTH_NUM --year $YEAR"
DASHBOARD_VERSION="9.0"

# Step 3: Data validation (optional)
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔍 Generate validation report? (Recommended)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${WHITE}This report includes:${NC}"
echo -e "  ${CYAN}• Condition evaluation statistics (10 conditions)${NC}"
echo -e "  ${CYAN}• Incentive distribution analysis${NC}"
echo -e "  ${CYAN}• Failed conditions breakdown${NC}"
echo -e "  ${CYAN}• TYPE-based statistics${NC}"
echo ""
echo -e "${YELLOW}Generate validation report now? (y/n): ${NC}\c"
read run_validation

if [ "$run_validation" = "y" ] || [ "$run_validation" = "Y" ]; then
    echo ""
    echo -e "${GREEN}🚀 Generating validation report...${NC}"
    echo ""

    # Run new simple validation report generator
    python3 scripts/verification/generate_simple_validation_report.py "$MONTH" "$YEAR"
    VALIDATION_RESULT=$?

    echo ""
    if [ $VALIDATION_RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ Validation report generated successfully!${NC}"

        # Offer to open validation report
        echo ""
        echo -e "${YELLOW}📊 Open validation report now? (y/n): ${NC}\c"
        read open_report

        if [ "$open_report" = "y" ] || [ "$open_report" = "Y" ]; then
            # Find latest validation report
            LATEST_REPORT=$(ls -t validation_reports/VALIDATION_REPORT_${MONTH}_${YEAR}_*.xlsx 2>/dev/null | head -n 1)

            if [ ! -z "$LATEST_REPORT" ] && [ -f "$LATEST_REPORT" ]; then
                open "$LATEST_REPORT"
                echo -e "${GREEN}✅ Validation report opened!${NC}"
            else
                echo -e "${YELLOW}⚠️ Validation report not found${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️ Validation report generation failed${NC}"
        echo -e "${CYAN}   Check the error messages above${NC}"
    fi
else
    echo -e "${YELLOW}Validation report generation skipped.${NC}"
    echo -e "${CYAN}💡 You can generate it later with: python3 scripts/verification/generate_simple_validation_report.py $MONTH $YEAR${NC}"
fi

# Completion message
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 All tasks completed!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${WHITE}📁 Generated files:${NC}"
echo -e "  ${BLUE}• Excel: output_files/output_QIP_incentive_${MONTH}_${YEAR}_Complete_V9.0_Complete.xlsx${NC}"
echo -e "  ${BLUE}• CSV: output_files/output_QIP_incentive_${MONTH}_${YEAR}_Complete_V9.0_Complete.csv${NC}"
if [ "$month_choice" -lt 10 ]; then
    echo -e "  ${BLUE}• Incentive Dashboard: output_files/Incentive_Dashboard_${YEAR}_0${month_choice}_Version_${DASHBOARD_VERSION}.html${NC}"
else
    echo -e "  ${BLUE}• Incentive Dashboard: output_files/Incentive_Dashboard_${YEAR}_${month_choice}_Version_${DASHBOARD_VERSION}.html${NC}"
fi
echo ""
echo -e "${YELLOW}💡 Open the HTML file in your browser to view the results.${NC}"
echo ""

# Option to auto-open HTML file
echo -e "${CYAN}Would you like to open the dashboard now?${NC}"
echo "  1) Open Incentive Dashboard"
echo "  2) Don't open"
echo -e "${WHITE}Choice (1-2): ${NC}\c"
read open_choice

# Format month number to two digits
if [ "$month_choice" -lt 10 ]; then
    MONTH_PADDED="0${month_choice}"
else
    MONTH_PADDED="${month_choice}"
fi

case $open_choice in
    1)
        HTML_FILE="output_files/Incentive_Dashboard_${YEAR}_${MONTH_PADDED}_Version_${DASHBOARD_VERSION}.html"
        if [ -f "$HTML_FILE" ]; then
            open "$HTML_FILE"
            echo -e "${GREEN}✅ Incentive Dashboard v${DASHBOARD_VERSION} opened in browser!${NC}"
        else
            echo -e "${YELLOW}⚠️ HTML file not found: $HTML_FILE${NC}"
        fi
        ;;
    2)
        echo -e "${YELLOW}Dashboard not opened.${NC}"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice.${NC}"
        ;;
esac

echo ""
echo -e "${CYAN}Thank you! 😊${NC}"