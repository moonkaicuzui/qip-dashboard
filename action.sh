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
echo -e "${WHITE}         📊 QIP 인센티브 보고서 One-Click 생성기${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    echo "Homebrew로 설치: brew install python3"
    exit 1
fi

# 년도 선택
echo -e "${YELLOW}📅 년도를 선택하세요:${NC}"
echo "  1) 2025년"
echo "  2) 2026년"
echo -e "${WHITE}선택 (1 또는 2): ${NC}\c"
read year_choice

case $year_choice in
    1)
        YEAR=2025
        ;;
    2)
        YEAR=2026
        ;;
    *)
        echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

# 월 선택
echo ""
echo -e "${YELLOW}📅 월을 선택하세요:${NC}"
echo "  1) 1월 (January)"
echo "  2) 2월 (February)"
echo "  3) 3월 (March)"
echo "  4) 4월 (April)"
echo "  5) 5월 (May)"
echo "  6) 6월 (June)"
echo "  7) 7월 (July)"
echo "  8) 8월 (August)"
echo "  9) 9월 (September)"
echo "  10) 10월 (October)"
echo "  11) 11월 (November)"
echo "  12) 12월 (December)"
echo -e "${WHITE}선택 (1-12): ${NC}\c"
read month_choice

# 월 이름 매핑
case $month_choice in
    1) MONTH="january" ; MONTH_KR="1월" ; MONTH_NUM=1 ;;
    2) MONTH="february" ; MONTH_KR="2월" ; MONTH_NUM=2 ;;
    3) MONTH="march" ; MONTH_KR="3월" ; MONTH_NUM=3 ;;
    4) MONTH="april" ; MONTH_KR="4월" ; MONTH_NUM=4 ;;
    5) MONTH="may" ; MONTH_KR="5월" ; MONTH_NUM=5 ;;
    6) MONTH="june" ; MONTH_KR="6월" ; MONTH_NUM=6 ;;
    7) MONTH="july" ; MONTH_KR="7월" ; MONTH_NUM=7 ;;
    8) MONTH="august" ; MONTH_KR="8월" ; MONTH_NUM=8 ;;
    9) MONTH="september" ; MONTH_KR="9월" ; MONTH_NUM=9 ;;
    10) MONTH="october" ; MONTH_KR="10월" ; MONTH_NUM=10 ;;
    11) MONTH="november" ; MONTH_KR="11월" ; MONTH_NUM=11 ;;
    12) MONTH="december" ; MONTH_KR="12월" ; MONTH_NUM=12 ;;
    *)
        echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

# 선택 확인
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}선택하신 날짜: ${YEAR}년 ${MONTH_KR}${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}계속 진행하시겠습니까? (y/n): ${NC}\c"
read confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}취소되었습니다.${NC}"
    exit 0
fi

# Config 파일 경로
CONFIG_FILE="config_files/config_${MONTH}_${YEAR}.json"

# 실행 함수
run_step() {
    local step_name=$1
    local command=$2
    
    echo ""
    echo -e "${PURPLE}▶ ${step_name}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    eval $command
    local result=$?
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✅ ${step_name} 완료!${NC}"
        return 0
    else
        echo -e "${RED}❌ ${step_name} 실패!${NC}"
        echo -e "${YELLOW}오류가 발생했습니다. 로그를 확인해주세요.${NC}"
        return $result
    fi
}

# 실행 시작
echo ""
echo -e "${GREEN}🚀 보고서 생성을 시작합니다...${NC}"

# Step 0: Config 파일 확인/생성
if [ ! -f "$CONFIG_FILE" ]; then
    echo ""
    echo -e "${YELLOW}⚠️ Config 파일이 없습니다. 생성하시겠습니까? (y/n): ${NC}\c"
    read create_config
    
    if [ "$create_config" = "y" ] || [ "$create_config" = "Y" ]; then
        run_step "Step 0: Config 파일 생성" "python3 src/step0_create_monthly_config.py --month $MONTH --year $YEAR --auto"
    else
        echo -e "${RED}Config 파일이 필요합니다. 종료합니다.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Config 파일 확인 완료: $CONFIG_FILE${NC}"
fi

# Step 0.5: Google Drive 동기화 (파일 다운로드)
echo ""
echo -e "${YELLOW}📥 Google Drive에서 필요한 파일 동기화 중...${NC}"
python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Google Drive 동기화 완료${NC}"
else
    echo -e "${YELLOW}⚠️ Google Drive 동기화 실패 (수동 다운로드 필요할 수 있음)${NC}"
fi

# Step 0.6: 이전 월 인센티브 파일 동기화
echo ""
echo -e "${YELLOW}📥 이전 월 인센티브 파일 확인 중...${NC}"
python3 src/sync_previous_incentive.py $MONTH $YEAR

# Step 0.7: 출근 데이터 변환
run_step "Step 0.7: 출근 데이터 변환" "python3 src/convert_attendance_data.py $MONTH"
CONVERT_RESULT=$?

# 출근 데이터 변환 실패 시 경고
if [ $CONVERT_RESULT -ne 0 ]; then
    echo -e "${YELLOW}⚠️ 출근 데이터 변환에 문제가 있습니다. working_days 자동 계산이 불가능할 수 있습니다.${NC}"
fi

# Step 0.7.5: Attendance 데이터에서 working_days 자동 계산 및 Config 업데이트
echo ""
echo -e "${YELLOW}🔄 Attendance 데이터에서 근무일수를 자동 계산하여 Config 업데이트 중...${NC}"

# 스크립트 파일 존재 확인
if [ ! -f "src/calculate_working_days_from_attendance.py" ]; then
    echo -e "${RED}❌ calculate_working_days_from_attendance.py 파일이 없습니다.${NC}"
    echo -e "${YELLOW}⚠️ Config의 기존 working_days 값을 사용합니다.${NC}"
else
    python3 src/calculate_working_days_from_attendance.py $MONTH $YEAR
    CALC_RESULT=$?

    if [ $CALC_RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ Config의 working_days가 실제 데이터 기반으로 자동 업데이트되었습니다${NC}"

        # 업데이트된 working_days 값 표시
        WORKING_DAYS=$(python3 -c "import json; config = json.load(open('$CONFIG_FILE')); print(config.get('working_days', 'N/A'))" 2>/dev/null)
        if [ ! -z "$WORKING_DAYS" ] && [ "$WORKING_DAYS" != "N/A" ]; then
            echo -e "${GREEN}   📅 ${MONTH} 근무일수: ${WORKING_DAYS}일${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ 자동 계산 실패 - Config의 기존 working_days 값을 사용합니다${NC}"

        # 기존 working_days 값 표시
        EXISTING_DAYS=$(python3 -c "import json; config = json.load(open('$CONFIG_FILE')); print(config.get('working_days', 'N/A'))" 2>/dev/null)
        if [ ! -z "$EXISTING_DAYS" ] && [ "$EXISTING_DAYS" != "N/A" ]; then
            echo -e "${YELLOW}   📅 기존 working_days: ${EXISTING_DAYS}일${NC}"
            echo -e "${YELLOW}   ⚠️ 주의: 이 값이 정확한지 확인이 필요합니다${NC}"
        fi
    fi
fi

# Step 0.8: HR 데이터 검증
echo ""
echo -e "${YELLOW}🔍 HR 데이터 정합성 검증 중...${NC}"
python3 src/validate_hr_data.py $month_choice $YEAR
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ HR 데이터 검증 완료 (결과는 error_review 폴더 확인)${NC}"
else
    echo -e "${YELLOW}⚠️ HR 데이터 검증 중 문제 발견 (error_review 폴더 확인)${NC}"
fi

# Step 1: 인센티브 계산
run_step "Step 1: 인센티브 계산" "python3 src/step1_인센티브_계산_개선버전.py --config $CONFIG_FILE"
STEP1_RESULT=$?

# Step 1이 실패하면 중단
if [ $STEP1_RESULT -ne 0 ]; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ 인센티브 계산 중 오류가 발생하여 작업을 중단합니다.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi

# Step 1.5: Excel에서 JSON 생성 (다음 달 계산을 위한 데이터 준비)
echo ""
echo -e "${YELLOW}📝 Excel 데이터에서 JSON 파일 생성 중...${NC}"
python3 src/generate_json_from_excel.py \
    --excel "output_files/output_QIP_incentive_${MONTH}_${YEAR}_최종완성버전_v6.0_Complete.csv" \
    --month "$MONTH" \
    --year "$YEAR" \
    --validate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ JSON 파일 생성 및 검증 완료${NC}"
else
    echo -e "${YELLOW}⚠️ JSON 파일 생성 중 경고 (작업은 계속됨)${NC}"
fi

# Step 1.6: Excel vs JSON 데이터 일관성 검증
echo ""
echo -e "${YELLOW}🔍 Excel vs JSON 데이터 일관성 검증 중...${NC}"
python3 src/validate_excel_json_consistency.py \
    --excel "output_files/output_QIP_incentive_${MONTH}_${YEAR}_최종완성버전_v6.0_Complete.csv" \
    --json "config_files/assembly_inspector_continuous_months.json"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 데이터 일관성 검증 완료${NC}"
else
    echo -e "${YELLOW}⚠️ 데이터 불일치 발견 (validation_report 확인 필요)${NC}"
fi

# Step 1.7: 연속 AQL 실패 데이터 자동 업데이트
echo ""
echo -e "${YELLOW}🔄 3개월 연속 AQL 실패 데이터 분석 및 업데이트 중...${NC}"
python3 src/update_continuous_fail_column.py --month $MONTH --year $YEAR
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 연속 AQL 실패 데이터 업데이트 완료${NC}"
    echo -e "${CYAN}   • 자동으로 이전 2개월 AQL 파일 분석${NC}"
    echo -e "${CYAN}   • 2개월/3개월 연속 실패자 자동 태깅${NC}"
else
    echo -e "${YELLOW}⚠️ 연속 AQL 실패 업데이트 중 경고 (대시보드는 계속 생성됨)${NC}"
fi

# Step 2: 모듈형 Dashboard 생성 (구조 개선된 v6.0)
echo ""
echo -e "${GREEN}✨ 구조 개선된 모듈형 대시보드 v6.0을 생성합니다${NC}"
echo -e "${CYAN}  • 13,374줄 → 2,394줄로 코드 82% 감소${NC}"
echo -e "${CYAN}  • 완전한 모듈화로 유지보수 용이${NC}"
echo -e "${CYAN}  • Vibe 등 AI 도구 호환${NC}"
echo ""

run_step "Step 2: HTML Dashboard 생성 (v6.0 통합형)" "python3 integrated_dashboard_final.py --month $MONTH_NUM --year $YEAR"
DASHBOARD_VERSION="6"

# 완료 메시지
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 모든 작업이 완료되었습니다!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${WHITE}📁 생성된 파일:${NC}"
echo -e "  ${BLUE}• Excel: output_files/output_QIP_incentive_${MONTH}_${YEAR}_최종완성버전_v6.0_Complete.xlsx${NC}"
echo -e "  ${BLUE}• CSV: output_files/output_QIP_incentive_${MONTH}_${YEAR}_최종완성버전_v6.0_Complete.csv${NC}"
if [ "$month_choice" -lt 10 ]; then
    echo -e "  ${BLUE}• Incentive Dashboard: output_files/Incentive_Dashboard_${YEAR}_0${month_choice}_Version_${DASHBOARD_VERSION}.html${NC}"
else
    echo -e "  ${BLUE}• Incentive Dashboard: output_files/Incentive_Dashboard_${YEAR}_${month_choice}_Version_${DASHBOARD_VERSION}.html${NC}"
fi
echo ""
echo -e "${YELLOW}💡 HTML 파일을 브라우저에서 열어 결과를 확인하세요.${NC}"
echo ""

# HTML 파일 자동으로 열기 옵션
echo -e "${CYAN}대시보드를 지금 열어보시겠습니까?${NC}"
echo "  1) Incentive Dashboard 열기"
echo "  2) 열지 않음"
echo -e "${WHITE}선택 (1-2): ${NC}\c"
read open_choice

# 월 번호를 두 자리로 포맷
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
            echo -e "${GREEN}✅ Incentive Dashboard v${DASHBOARD_VERSION}가 브라우저에서 열렸습니다!${NC}"
        else
            echo -e "${YELLOW}⚠️ HTML 파일을 찾을 수 없습니다: $HTML_FILE${NC}"
        fi
        ;;
    2)
        echo -e "${YELLOW}대시보드를 열지 않았습니다.${NC}"
        ;;
    *)
        echo -e "${YELLOW}잘못된 선택입니다.${NC}"
        ;;
esac

echo ""
echo -e "${CYAN}감사합니다! 😊${NC}"