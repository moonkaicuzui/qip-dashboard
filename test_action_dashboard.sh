#!/bin/bash

# 색상 코드
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📊 대시보드 생성 테스트 (신규 모듈형 vs 기존 통합형)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 현재 디렉토리 설정
cd "$(dirname "$0")"

echo -e "${YELLOW}테스트 옵션을 선택하세요:${NC}"
echo "  1) 새로운 모듈형 대시보드 v6.0 테스트"
echo "  2) 기존 통합형 대시보드 v5.0 테스트"
echo "  3) 두 버전 모두 테스트 (비교)"
echo -e "${GREEN}선택 (1-3): ${NC}\c"
read choice

MONTH="september"
YEAR=2025

case $choice in
    1)
        echo -e "\n${BLUE}▶ 모듈형 대시보드 v6.0 생성 중...${NC}"
        python3 dashboard_v2/generate_dashboard.py --month $MONTH --year $YEAR
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 모듈형 대시보드 생성 성공!${NC}"
            ls -lh output_files/Incentive_Dashboard_2025_09_Version_6.html
        else
            echo -e "${YELLOW}❌ 모듈형 대시보드 생성 실패${NC}"
        fi
        ;;
    2)
        echo -e "\n${BLUE}▶ 통합형 대시보드 v5.0 생성 중...${NC}"
        python3 integrated_dashboard_final.py --month 9 --year $YEAR
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 통합형 대시보드 생성 성공!${NC}"
            ls -lh output_files/Incentive_Dashboard_2025_09_Version_5.html
        else
            echo -e "${YELLOW}❌ 통합형 대시보드 생성 실패${NC}"
        fi
        ;;
    3)
        echo -e "\n${BLUE}▶ 두 버전 모두 생성 중...${NC}"

        # 모듈형 생성
        echo -e "\n${CYAN}[1/2] 모듈형 대시보드 v6.0${NC}"
        python3 dashboard_v2/generate_dashboard.py --month $MONTH --year $YEAR
        RESULT1=$?

        # 통합형 생성
        echo -e "\n${CYAN}[2/2] 통합형 대시보드 v5.0${NC}"
        python3 integrated_dashboard_final.py --month 9 --year $YEAR
        RESULT2=$?

        # 결과 표시
        echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}📊 비교 결과:${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        if [ $RESULT1 -eq 0 ]; then
            echo -e "모듈형 v6.0: ${GREEN}✅ 성공${NC}"
            ls -lh output_files/Incentive_Dashboard_2025_09_Version_6.html | awk '{print "  크기: " $5}'
        else
            echo -e "모듈형 v6.0: ${YELLOW}❌ 실패${NC}"
        fi

        if [ $RESULT2 -eq 0 ]; then
            echo -e "통합형 v5.0: ${GREEN}✅ 성공${NC}"
            ls -lh output_files/Incentive_Dashboard_2025_09_Version_5.html | awk '{print "  크기: " $5}'
        else
            echo -e "통합형 v5.0: ${YELLOW}❌ 실패${NC}"
        fi
        ;;
    *)
        echo -e "${YELLOW}잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}테스트 완료!${NC}"