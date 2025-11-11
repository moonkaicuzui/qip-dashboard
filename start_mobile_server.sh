#!/bin/bash

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# IP 주소 가져오기
get_ip() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "localhost"
    else
        hostname -I | awk '{print $1}' || echo "localhost"
    fi
}

IP=$(get_ip)

echo -e "${BLUE}📱 모바일 대시보드 서버${NC}"
echo "1) Streamlit 서버"
echo "2) HTML 서버"
read -p "선택: " choice

case $choice in
    1)
        echo -e "${GREEN}Streamlit: http://${IP}:8501${NC}"
        streamlit run webapp/streamlit_dashboard.py --server.address 0.0.0.0
        ;;
    2)
        echo -e "${GREEN}HTML: http://${IP}:8080${NC}"
        python3 -m http.server 8080 --bind 0.0.0.0
        ;;
esac
