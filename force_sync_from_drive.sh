#!/bin/bash

# ============================================================
# Google Drive 강제 동기화 스크립트
# 캐시를 무시하고 새로운 파일을 다운로드합니다
# ============================================================

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}         📥 Google Drive 강제 동기화 도구${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 옵션 선택
echo -e "${YELLOW}동기화 옵션을 선택하세요:${NC}"
echo "  1) 캐시 유지하며 동기화 (빠름)"
echo "  2) 캐시 삭제 후 전체 동기화 (느리지만 최신 파일 보장)"
echo -e "${WHITE}선택 (1 또는 2): ${NC}\c"
read sync_option

# 캐시 처리
if [ "$sync_option" = "2" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  캐시를 삭제하고 모든 파일을 다시 다운로드합니다.${NC}"
    echo -e "${YELLOW}계속하시겠습니까? (y/n): ${NC}\c"
    read confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo -e "${RED}🗑️  캐시 디렉토리 삭제 중...${NC}"
        rm -rf .cache/drive_sync/*
        echo -e "${GREEN}✅ 캐시가 삭제되었습니다.${NC}"
    else
        echo -e "${YELLOW}캐시 삭제를 건너뜁니다.${NC}"
    fi
fi

# 년도 선택
echo ""
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

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 ${YEAR}년 ${MONTH_KR} 데이터 동기화를 시작합니다...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Python 스크립트 실행 (sync-only 모드)
echo ""
echo -e "${YELLOW}📥 Google Drive에서 파일 다운로드 중...${NC}"

if [ "$sync_option" = "2" ]; then
    # 캐시를 무시하고 강제 다운로드
    python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR --sync-only --force-refresh 2>/dev/null || \
    python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR --sync-only
else
    # 일반 동기화
    python3 src/auto_run_with_drive.py --month $MONTH --year $YEAR --sync-only
fi

SYNC_RESULT=$?

if [ $SYNC_RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Google Drive 동기화가 완료되었습니다!${NC}"

    # 동기화된 파일 확인
    echo ""
    echo -e "${BLUE}📁 동기화된 파일 확인:${NC}"

    # 출근 데이터
    ATTENDANCE_FILE="input_files/attendance/original/attendance data $MONTH.csv"
    if [ -f "$ATTENDANCE_FILE" ]; then
        FILE_DATE=$(date -r "$ATTENDANCE_FILE" "+%Y-%m-%d %H:%M:%S")
        echo -e "  ${GREEN}✓${NC} 출근 데이터: $FILE_DATE"
    else
        echo -e "  ${RED}✗${NC} 출근 데이터 없음"
    fi

    # Basic manpower 데이터
    MANPOWER_FILE="input_files/basic manpower data $MONTH.csv"
    if [ -f "$MANPOWER_FILE" ]; then
        FILE_DATE=$(date -r "$MANPOWER_FILE" "+%Y-%m-%d %H:%M:%S")
        echo -e "  ${GREEN}✓${NC} Basic manpower: $FILE_DATE"
    else
        echo -e "  ${RED}✗${NC} Basic manpower 데이터 없음"
    fi

    # 5PRS 데이터
    PRS_FILE="input_files/5prs data $MONTH.csv"
    if [ -f "$PRS_FILE" ]; then
        FILE_DATE=$(date -r "$PRS_FILE" "+%Y-%m-%d %H:%M:%S")
        echo -e "  ${GREEN}✓${NC} 5PRS 데이터: $FILE_DATE"
    else
        echo -e "  ${RED}✗${NC} 5PRS 데이터 없음"
    fi

    # AQL 데이터
    AQL_FILE="input_files/AQL history/1.HSRG AQL REPORT-${MONTH^^}.$YEAR.csv"
    if [ -f "$AQL_FILE" ]; then
        FILE_DATE=$(date -r "$AQL_FILE" "+%Y-%m-%d %H:%M:%S")
        echo -e "  ${GREEN}✓${NC} AQL 데이터: $FILE_DATE"
    else
        echo -e "  ${RED}✗${NC} AQL 데이터 없음"
    fi

else
    echo ""
    echo -e "${RED}❌ Google Drive 동기화 중 문제가 발생했습니다.${NC}"
    echo -e "${YELLOW}💡 다음을 확인하세요:${NC}"
    echo "  1. 인터넷 연결 상태"
    echo "  2. Google Drive 인증 정보 (credentials/service-account-key.json)"
    echo "  3. Google Drive 폴더 구조"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 다음 작업 안내
echo ""
echo -e "${YELLOW}📌 다음 단계:${NC}"
echo "  1. 동기화된 파일들이 최신 버전인지 확인"
echo "  2. action.sh를 실행하여 보고서 생성"
echo ""
echo -e "${CYAN}실행 명령: ./action.sh${NC}"
echo ""