#!/bin/bash

# 5PRS Dashboard 실행 스크립트
# 사용법: ./5prs.sh

echo "============================================================"
echo "           5PRS Quality Dashboard Launcher                 "
echo "============================================================"
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 현재 디렉토리 저장
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

# 필요한 패키지 확인
echo -e "${YELLOW}📦 필요한 패키지 확인 중...${NC}"
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Flask 설치 중...${NC}"
    pip3 install flask flask-cors pandas --quiet
fi

# 기존 서버 프로세스 종료
echo -e "${YELLOW}🔄 기존 서버 종료 중...${NC}"
lsof -ti:5001 | xargs kill -9 2>/dev/null

# API 서버 시작
echo -e "${GREEN}🚀 5PRS Data API 서버 시작 중...${NC}"
python3 5prs_data_api.py > /tmp/5prs_server.log 2>&1 &
SERVER_PID=$!

# 서버가 시작될 때까지 대기
echo -e "${YELLOW}⏳ 서버 초기화 대기 중...${NC}"
sleep 3

# 서버 상태 확인
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 서버가 성공적으로 시작되었습니다!${NC}"
    echo ""
    echo "============================================================"
    echo -e "${GREEN}📊 5PRS Dashboard 정보${NC}"
    echo "------------------------------------------------------------"
    echo -e "  대시보드 URL: ${GREEN}http://localhost:5001/${NC}"
    echo -e "  API 엔드포인트: ${GREEN}http://localhost:5001/api/5prs-data${NC}"
    echo -e "  서버 PID: ${GREEN}$SERVER_PID${NC}"
    echo "------------------------------------------------------------"
    
    # 데이터 요약 정보 표시
    echo -e "\n${YELLOW}📈 데이터 요약:${NC}"
    RECORDS=$(curl -s http://localhost:5001/api/5prs-data | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['summary']['total_records'])" 2>/dev/null)
    echo -e "  총 레코드 수: ${GREEN}${RECORDS}개${NC}"
    echo ""
    
    # 브라우저 열기
    echo -e "${GREEN}🌐 브라우저를 여는 중...${NC}"
    
    # OS별 브라우저 열기 명령
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open http://localhost:5001/
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:5001/
        elif command -v gnome-open &> /dev/null; then
            gnome-open http://localhost:5001/
        fi
    fi
    
    echo ""
    echo "============================================================"
    echo -e "${GREEN}✨ 5PRS Dashboard가 실행 중입니다!${NC}"
    echo ""
    echo -e "${YELLOW}종료하려면 Ctrl+C를 누르세요.${NC}"
    echo "============================================================"
    
    # 서버 프로세스 모니터링
    trap "echo -e '\n${YELLOW}🛑 서버를 종료합니다...${NC}'; kill $SERVER_PID 2>/dev/null; echo -e '${GREEN}✅ 종료 완료${NC}'; exit 0" INT TERM
    
    # 서버 로그 표시 (선택적)
    # tail -f /tmp/5prs_server.log
    
    # 서버가 실행 중인 동안 대기
    wait $SERVER_PID
    
else
    echo -e "${RED}❌ 서버 시작 실패!${NC}"
    echo -e "${YELLOW}로그 확인: cat /tmp/5prs_server.log${NC}"
    exit 1
fi