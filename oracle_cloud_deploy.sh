#!/bin/bash

#########################################
# Oracle Cloud 무료 인스턴스 배포 스크립트
# QIP 인센티브 대시보드 시스템
#########################################

echo "======================================"
echo "🌩️  Oracle Cloud 무료 배포 자동화"
echo "======================================"

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 서버 접속 정보 설정
configure_connection() {
    echo -e "\n${BLUE}🔗 서버 접속 정보 설정${NC}"
    read -p "Oracle 인스턴스의 공개 IP 주소를 입력하세요: " SERVER_IP
    echo "서버 IP: $SERVER_IP"
}

echo "Oracle Cloud Free Tier 배포 스크립트"
echo "상세 내용은 배포 가이드를 참조하세요"
configure_connection
