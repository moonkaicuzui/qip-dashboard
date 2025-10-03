#!/bin/bash

# ============================================================
# QIP 인센티브 데이터 완전 검증 파이프라인
# Complete Validation Pipeline for QIP Incentive Data
# macOS/Linux 호환
# ============================================================

# 색상 코드 정의
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
echo -e "${WHITE}    📊 QIP Incentive Data Complete Validation Pipeline${NC}"
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
echo "  1) January      7) July"
echo "  2) February     8) August"
echo "  3) March        9) September"
echo "  4) April       10) October"
echo "  5) May         11) November"
echo "  6) June        12) December"
echo -e "${WHITE}Choice (1-12): ${NC}\c"
read month_choice

# Month name mapping
case $month_choice in
    1) MONTH="january" ; MONTH_EN="January" ;;
    2) MONTH="february" ; MONTH_EN="February" ;;
    3) MONTH="march" ; MONTH_EN="March" ;;
    4) MONTH="april" ; MONTH_EN="April" ;;
    5) MONTH="may" ; MONTH_EN="May" ;;
    6) MONTH="june" ; MONTH_EN="June" ;;
    7) MONTH="july" ; MONTH_EN="July" ;;
    8) MONTH="august" ; MONTH_EN="August" ;;
    9) MONTH="september" ; MONTH_EN="September" ;;
    10) MONTH="october" ; MONTH_EN="October" ;;
    11) MONTH="november" ; MONTH_EN="November" ;;
    12) MONTH="december" ; MONTH_EN="December" ;;
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

# 실행 함수
run_validation() {
    local step_name=$1
    local script_path=$2

    echo ""
    echo -e "${PURPLE}▶ ${step_name}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    python3 "$script_path" "$MONTH" "$YEAR"
    local result=$?

    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✅ ${step_name} completed successfully!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ ${step_name} completed with warnings (Exit code: ${result})${NC}"
        echo -e "${YELLOW}Findings detected - check the report for details.${NC}"
        return $result
    fi
}

# 검증 시작
echo ""
echo -e "${GREEN}🚀 Starting complete validation pipeline...${NC}"
echo ""

# Step 1: Condition Evaluation Validation
run_validation \
    "Step 1: Condition Evaluation Validation" \
    "scripts/verification/validate_condition_evaluation.py"
STEP1_RESULT=$?

# Step 2: Incentive Amounts Validation
run_validation \
    "Step 2: Incentive Amounts Validation" \
    "scripts/verification/validate_incentive_amounts.py"
STEP2_RESULT=$?

# Step 3: Dashboard Consistency Validation
run_validation \
    "Step 3: Dashboard Consistency Validation" \
    "scripts/verification/validate_dashboard_consistency.py"
STEP3_RESULT=$?

# Step 4: Generate Integrated Report
echo ""
echo -e "${PURPLE}▶ Step 4: Generate Integrated Report${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python3 scripts/verification/generate_final_report.py "$MONTH" "$YEAR"
STEP4_RESULT=$?

if [ $STEP4_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Integrated report generated successfully!${NC}"
else
    echo -e "${YELLOW}⚠️ Integrated report generated with warnings${NC}"
fi

# 완료 메시지
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Complete validation pipeline finished!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 결과 요약
echo -e "${WHITE}📊 Validation Results Summary:${NC}"
if [ $STEP1_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Condition Evaluation: PASS${NC}"
else
    echo -e "  ${YELLOW}⚠️ Condition Evaluation: FINDINGS DETECTED${NC}"
fi

if [ $STEP2_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Incentive Amounts: PASS${NC}"
else
    echo -e "  ${YELLOW}⚠️ Incentive Amounts: FINDINGS DETECTED${NC}"
fi

if [ $STEP3_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Dashboard Consistency: PASS${NC}"
else
    echo -e "  ${YELLOW}⚠️ Dashboard Consistency: FINDINGS DETECTED${NC}"
fi

echo ""
echo -e "${WHITE}📁 Generated Reports:${NC}"
echo -e "  ${BLUE}• Individual validation reports: validation_reports/${NC}"
echo -e "  ${BLUE}• Integrated report: validation_reports/INTEGRATED_VALIDATION_REPORT_${MONTH}_${YEAR}_*.xlsx${NC}"
echo ""

# 리포트 열기 옵션
echo -e "${CYAN}Would you like to open the integrated report?${NC}"
echo "  1) Open integrated report"
echo "  2) Open validation_reports folder"
echo "  3) Don't open"
echo -e "${WHITE}Choice (1-3): ${NC}\c"
read open_choice

case $open_choice in
    1)
        # 가장 최근 통합 리포트 찾기
        LATEST_REPORT=$(ls -t validation_reports/INTEGRATED_VALIDATION_REPORT_${MONTH}_${YEAR}_*.xlsx 2>/dev/null | head -n 1)
        if [ ! -z "$LATEST_REPORT" ]; then
            open "$LATEST_REPORT"
            echo -e "${GREEN}✅ Integrated report opened!${NC}"
        else
            echo -e "${YELLOW}⚠️ Integrated report not found${NC}"
        fi
        ;;
    2)
        open validation_reports/
        echo -e "${GREEN}✅ Validation reports folder opened!${NC}"
        ;;
    3)
        echo -e "${YELLOW}Reports not opened.${NC}"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice.${NC}"
        ;;
esac

echo ""
echo -e "${CYAN}Thank you! 😊${NC}"
echo ""

# Exit code: 성공(모든 검증 통과)=0, 경고(일부 findings)=1
if [ $STEP1_RESULT -eq 0 ] && [ $STEP2_RESULT -eq 0 ] && [ $STEP3_RESULT -eq 0 ]; then
    exit 0
else
    exit 1
fi
