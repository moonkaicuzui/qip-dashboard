#!/bin/bash

echo "========================================"
echo "🚀 QIP 대시보드 웹 서버 시작"
echo "========================================"

# 필요한 패키지 확인 및 설치
echo "📦 의존성 확인 중..."

# Flask 확인
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Flask 설치 중..."
    pip3 install flask flask-cors
fi

# gspread 확인
python3 -c "import gspread" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Google Drive 패키지 설치 중..."
    pip3 install gspread oauth2client google-auth google-auth-oauthlib google-auth-httplib2
fi

# pandas 확인
python3 -c "import pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "데이터 처리 패키지 설치 중..."
    pip3 install pandas numpy openpyxl
fi

# IP 주소 확인
IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()")

echo ""
echo "✅ 서버 시작 준비 완료!"
echo ""
echo "📱 접속 방법:"
echo "   로컬: http://localhost:5000"
echo "   네트워크: http://$IP:5000"
echo ""
echo "🔐 기본 비밀번호: qip2025admin"
echo ""
echo "종료: Ctrl+C"
echo "========================================"
echo ""

# 서버 실행
cd "$(dirname "$0")/.."
python3 webapp/app.py