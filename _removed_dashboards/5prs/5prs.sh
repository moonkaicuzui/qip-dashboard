#!/bin/bash

# ============================================================
# 5PRS Quality Dashboard 실행 스크립트
# Google Drive 연동 + API 서버 방식
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
echo -e "${WHITE}         📊 5PRS Quality Dashboard${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    echo "Homebrew로 설치: brew install python3"
    exit 1
fi

# 옵션 선택
echo -e "${YELLOW}📅 대시보드 옵션을 선택하세요:${NC}"
echo "  1) 현재 월 데이터로 실행"
echo "  2) 특정 월 선택"
echo "  3) API 서버만 시작 (백그라운드)"
echo "  4) 실행 중인 서버 종료"
echo -e "${WHITE}선택 (1-4): ${NC}\c"
read option_choice

case $option_choice in
    1)
        # 현재 월 자동 설정
        MONTH=$(date +%B | tr '[:upper:]' '[:lower:]')
        YEAR=$(date +%Y)
        echo -e "${GREEN}✅ ${YEAR}년 ${MONTH} 데이터로 실행합니다.${NC}"
        ;;
    2)
        # 월 선택
        echo ""
        echo -e "${YELLOW}📅 년도를 입력하세요 (예: 2025): ${NC}\c"
        read YEAR
        echo -e "${YELLOW}📅 월을 선택하세요:${NC}"
        echo "  1) January   7) July"
        echo "  2) February  8) August"
        echo "  3) March     9) September"
        echo "  4) April    10) October"
        echo "  5) May      11) November"
        echo "  6) June     12) December"
        echo -e "${WHITE}선택 (1-12): ${NC}\c"
        read month_choice

        case $month_choice in
            1) MONTH="january" ;;
            2) MONTH="february" ;;
            3) MONTH="march" ;;
            4) MONTH="april" ;;
            5) MONTH="may" ;;
            6) MONTH="june" ;;
            7) MONTH="july" ;;
            8) MONTH="august" ;;
            9) MONTH="september" ;;
            10) MONTH="october" ;;
            11) MONTH="november" ;;
            12) MONTH="december" ;;
            *) echo -e "${RED}❌ 잘못된 선택입니다.${NC}"; exit 1 ;;
        esac
        echo -e "${GREEN}✅ ${YEAR}년 ${MONTH} 데이터로 실행합니다.${NC}"
        ;;
    3)
        # API 서버만 시작
        MONTH=$(date +%B | tr '[:upper:]' '[:lower:]')
        YEAR=$(date +%Y)
        ;;
    4)
        # 서버 종료
        echo -e "${YELLOW}🔄 5PRS API 서버를 종료합니다...${NC}"
        pkill -f "5prs_data_api.py"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 서버가 종료되었습니다.${NC}"
        else
            echo -e "${YELLOW}⚠️ 실행 중인 서버가 없습니다.${NC}"
        fi
        exit 0
        ;;
    *)
        echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

# 기존 5PRS API 서버 확인 및 종료
echo ""
echo -e "${YELLOW}🔍 기존 API 서버 확인 중...${NC}"
if pgrep -f "5prs_data_api.py" > /dev/null; then
    echo -e "${YELLOW}⚠️ 기존 서버를 종료합니다...${NC}"
    pkill -f "5prs_data_api.py"
    sleep 2
fi

# Step 1: 5PRS 데이터 통합 (필요시)
echo ""
echo -e "${PURPLE}▶ Step 1: 5PRS 데이터 통합${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python3 src/integrate_5prs_data.py --month "$MONTH" --year "$YEAR"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 5PRS 데이터 통합 완료${NC}"
else
    echo -e "${YELLOW}⚠️ 5PRS 데이터 통합 실패 (기존 데이터 사용)${NC}"
fi

# Step 2: API 서버 시작
echo ""
echo -e "${PURPLE}▶ Step 2: 5PRS API 서버 시작${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 로그 디렉토리 생성
mkdir -p logs

# API 서버 백그라운드 실행
nohup python3 src/5prs_data_api.py --host 0.0.0.0 --port 5003 > logs/5prs_api.log 2>&1 &
API_PID=$!

# 서버 시작 대기
echo -e "${YELLOW}⏳ API 서버 시작 중...${NC}"
sleep 3

# 서버 상태 확인
if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}✅ 5PRS API 서버 시작됨 (PID: $API_PID, Port: 5003)${NC}"
else
    echo -e "${RED}❌ API 서버 시작 실패. 로그를 확인하세요: logs/5prs_api.log${NC}"
    tail -10 logs/5prs_api.log
    exit 1
fi

# 완료 메시지
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 5PRS Dashboard 준비 완료!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${WHITE}📊 5PRS Dashboard 접속:${NC}"
echo -e "  ${BLUE}• URL: http://localhost:5003${NC}"
echo -e "  ${GREEN}• 상태: API 서버 실행 중 (포트 5003)${NC}"
echo ""

# 브라우저 열기 옵션
if [ "$option_choice" != "3" ]; then
    echo -e "${CYAN}Dashboard를 브라우저에서 열까요?${NC}"
    echo "  1) 예 - 브라우저에서 열기"
    echo "  2) 아니오 - 나중에 열기"
    echo -e "${WHITE}선택 (1-2): ${NC}\c"
    read open_choice

    case $open_choice in
        1)
            echo -e "${YELLOW}🌐 브라우저에서 5PRS Dashboard를 엽니다...${NC}"
            sleep 1
            open "http://localhost:5003"
            echo -e "${GREEN}✅ Dashboard가 브라우저에서 열렸습니다!${NC}"
            echo -e "${CYAN}💡 주소: http://localhost:5003${NC}"
            ;;
        2)
            echo -e "${YELLOW}Dashboard를 열지 않았습니다.${NC}"
            echo -e "${CYAN}💡 나중에 열려면: http://localhost:5003${NC}"
            ;;
        *)
            echo -e "${YELLOW}잘못된 선택입니다. Dashboard를 열지 않았습니다.${NC}"
            echo -e "${CYAN}💡 수동으로 열려면: http://localhost:5003${NC}"
            ;;
    esac
else
    echo -e "${GREEN}✅ API 서버가 백그라운드에서 실행 중입니다.${NC}"
    echo -e "${CYAN}💡 Dashboard 접속: http://localhost:5003${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}💡 도움말:${NC}"
echo -e "  • API 서버 로그 확인: ${YELLOW}tail -f logs/5prs_api.log${NC}"
echo -e "  • 서버 종료: ${YELLOW}./5prs.sh 후 옵션 4 선택${NC}"
echo -e "  • Dashboard 주소: ${CYAN}http://localhost:5003${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""