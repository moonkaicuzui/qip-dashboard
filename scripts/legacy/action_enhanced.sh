#!/bin/bash

# ============================================================
# QIP 인센티브 보고서 One-Click 생성 스크립트 (Enhanced Version)
# 출결 파일 동기화 개선 버전
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
echo -e "${WHITE}         📊 QIP 인센티브 보고서 One-Click 생성기 (Enhanced)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 출결 파일 동기화 체크 함수
check_attendance_sync() {
    local month=$1
    local original_file="input_files/attendance/original/attendance data $month.csv"
    local converted_file="input_files/attendance/converted/attendance data ${month}_converted.csv"

    if [ -f "$original_file" ]; then
        if [ -f "$converted_file" ]; then
            # 파일 수정 시간 비교
            if [ "$original_file" -nt "$converted_file" ]; then
                echo -e "${YELLOW}🔄 출결 파일이 업데이트되어 재변환이 필요합니다.${NC}"
                return 1
            else
                echo -e "${GREEN}✅ 출결 파일이 최신 상태입니다.${NC}"
                return 0
            fi
        else
            echo -e "${YELLOW}⚠️ 변환된 출결 파일이 없습니다.${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ 원본 출결 파일이 없습니다.${NC}"
        return 2
    fi
}

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
    1) YEAR=2025 ;;
    2) YEAR=2026 ;;
    *)
        echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

# 월 선택
echo ""
echo -e "${YELLOW}📅 월을 선택하세요:${NC}"
echo "  1) 1월    7) 7월"
echo "  2) 2월    8) 8월"
echo "  3) 3월    9) 9월"
echo "  4) 4월    10) 10월"
echo "  5) 5월    11) 11월"
echo "  6) 6월    12) 12월"
echo -e "${WHITE}선택 (1-12): ${NC}\c"
read month_choice

# 월 이름 매핑
case $month_choice in
    1) MONTH="january" ; MONTH_KR="1월" ;;
    2) MONTH="february" ; MONTH_KR="2월" ;;
    3) MONTH="march" ; MONTH_KR="3월" ;;
    4) MONTH="april" ; MONTH_KR="4월" ;;
    5) MONTH="may" ; MONTH_KR="5월" ;;
    6) MONTH="june" ; MONTH_KR="6월" ;;
    7) MONTH="july" ; MONTH_KR="7월" ;;
    8) MONTH="august" ; MONTH_KR="8월" ;;
    9) MONTH="september" ; MONTH_KR="9월" ;;
    10) MONTH="october" ; MONTH_KR="10월" ;;
    11) MONTH="november" ; MONTH_KR="11월" ;;
    12) MONTH="december" ; MONTH_KR="12월" ;;
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
python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR --sync-only 2>/dev/null
SYNC_RESULT=$?

if [ $SYNC_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Google Drive 동기화 완료${NC}"

    # 동기화된 파일 정보 표시
    echo -e "${BLUE}📋 동기화된 파일 상태:${NC}"

    # 출결 파일 확인
    ATTENDANCE_ORIG="input_files/attendance/original/attendance data $MONTH.csv"
    if [ -f "$ATTENDANCE_ORIG" ]; then
        FILE_SIZE=$(du -h "$ATTENDANCE_ORIG" | cut -f1)
        FILE_TIME=$(date -r "$ATTENDANCE_ORIG" "+%Y-%m-%d %H:%M")
        echo -e "  ${GREEN}✓${NC} 출결 데이터 (Original): ${FILE_TIME} [${FILE_SIZE}]"
    fi
else
    echo -e "${YELLOW}⚠️ Google Drive 동기화 실패 (수동 다운로드 필요할 수 있음)${NC}"
fi

# Step 0.6: 이전 월 인센티브 파일 동기화
echo ""
echo -e "${YELLOW}📥 이전 월 인센티브 파일 확인 중...${NC}"
python3 src/sync_previous_incentive.py $MONTH $YEAR 2>/dev/null

# Step 0.7: 출결 데이터 변환 (개선된 버전)
echo ""
echo -e "${PURPLE}▶ Step 0.7: 출결 데이터 변환 (Enhanced)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 출결 파일 동기화 상태 확인
check_attendance_sync $MONTH
SYNC_STATUS=$?

if [ $SYNC_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ 출결 데이터가 이미 최신 상태입니다.${NC}"
elif [ $SYNC_STATUS -eq 1 ]; then
    echo -e "${YELLOW}🔄 출결 데이터 변환 시작...${NC}"
    python3 src/convert_attendance_data.py $MONTH

    if [ $? -eq 0 ]; then
        # 변환 후 파일 정보 표시
        CONVERTED_FILE="input_files/attendance/converted/attendance data ${MONTH}_converted.csv"
        if [ -f "$CONVERTED_FILE" ]; then
            FILE_SIZE=$(du -h "$CONVERTED_FILE" | cut -f1)
            FILE_TIME=$(date -r "$CONVERTED_FILE" "+%Y-%m-%d %H:%M")
            echo -e "${GREEN}✅ 출결 데이터 변환 완료!${NC}"
            echo -e "  파일: ${CONVERTED_FILE}"
            echo -e "  크기: ${FILE_SIZE}, 시간: ${FILE_TIME}"
        fi
    else
        echo -e "${YELLOW}⚠️ 출결 데이터 변환 실패. working_days 자동 계산이 불가능할 수 있습니다.${NC}"
    fi
else
    echo -e "${RED}❌ 원본 출결 파일이 없어 변환할 수 없습니다.${NC}"
fi

# Step 0.7.5: working_days 자동 계산
echo ""
echo -e "${YELLOW}🔄 Attendance 데이터에서 근무일수를 자동 계산하여 Config 업데이트 중...${NC}"

if [ -f "src/calculate_working_days_from_attendance.py" ]; then
    python3 src/calculate_working_days_from_attendance.py $MONTH $YEAR
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Config의 working_days가 실제 데이터 기반으로 자동 업데이트되었습니다${NC}"

        WORKING_DAYS=$(python3 -c "import json; config = json.load(open('$CONFIG_FILE')); print(config.get('working_days', 'N/A'))" 2>/dev/null)
        if [ ! -z "$WORKING_DAYS" ] && [ "$WORKING_DAYS" != "N/A" ]; then
            echo -e "${GREEN}   📅 ${MONTH} 근무일수: ${WORKING_DAYS}일${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️ 근무일수 자동 계산 스크립트가 없습니다.${NC}"
fi

# Step 0.8: HR 데이터 검증
echo ""
echo -e "${YELLOW}🔍 HR 데이터 정합성 검증 중...${NC}"
python3 src/validate_hr_data.py $month_choice $YEAR 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ HR 데이터 검증 완료 (결과는 error_review 폴더 확인)${NC}"
else
    echo -e "${YELLOW}⚠️ HR 데이터 검증 중 문제 발견 (error_review 폴더 확인)${NC}"
fi

# Step 1: 인센티브 계산
run_step "Step 1: 인센티브 계산" "python3 src/step1_인센티브_계산_개선버전.py --config $CONFIG_FILE"
STEP1_RESULT=$?

if [ $STEP1_RESULT -ne 0 ]; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ 인센티브 계산 중 오류가 발생하여 작업을 중단합니다.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi

# Step 1.5: Excel에서 JSON 생성
echo ""
echo -e "${YELLOW}📝 Excel 데이터에서 JSON 파일 생성 중...${NC}"
python3 src/generate_json_from_excel.py \
    --excel "output_files/output_QIP_incentive_${MONTH}_${YEAR}_최종완성버전_v6.0_Complete.csv" \
    --month "$MONTH" \
    --year "$YEAR" \
    --validate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ JSON 파일 생성 및 검증 완료${NC}"
fi

# Step 2: Dashboard 생성 (최신 v5.0 버전)
run_step "Step 2: HTML Dashboard 생성 (v5.0)" "python3 integrated_dashboard_final.py --month $month_choice --year $YEAR"

# Step 3: Management Dashboard 생성
if [ -f "generate_management_dashboard_v6_enhanced.py" ]; then
    run_step "Step 3: Management Dashboard 생성" "python3 generate_management_dashboard_v6_enhanced.py --month $month_choice --year $YEAR"
fi

# 완료 메시지
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 모든 작업이 완료되었습니다!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${WHITE}📁 생성된 파일:${NC}"
echo -e "  ${BLUE}• Excel: output_files/output_QIP_incentive_${MONTH}_${YEAR}_최종완성버전_v6.0_Complete.xlsx${NC}"
echo -e "  ${BLUE}• CSV: output_files/output_QIP_incentive_${MONTH}_${YEAR}_최종완성버전_v6.0_Complete.csv${NC}"

# 월 번호를 두 자리로 포맷
if [ "$month_choice" -lt 10 ]; then
    MONTH_PADDED="0${month_choice}"
else
    MONTH_PADDED="${month_choice}"
fi

echo -e "  ${BLUE}• Incentive Dashboard: output_files/Incentive_Dashboard_${YEAR}_${MONTH_PADDED}_Version_5.html${NC}"

if [ -f "output_files/management_dashboard_${YEAR}_${MONTH_PADDED}.html" ]; then
    echo -e "  ${BLUE}• Management Dashboard: output_files/management_dashboard_${YEAR}_${MONTH_PADDED}.html${NC}"
fi

echo ""
echo -e "${YELLOW}💡 HTML 파일을 브라우저에서 열어 결과를 확인하세요.${NC}"
echo ""