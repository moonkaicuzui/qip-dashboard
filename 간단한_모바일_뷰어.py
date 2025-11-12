#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
초간단 모바일 대시보드 뷰어
추가 패키지 설치 없이 바로 실행 가능
"""

import http.server
import socketserver
import socket
import os

# 컴퓨터 IP 주소 찾기
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "IP를 찾을 수 없음"

# 서버 시작
PORT = 8080
ip = get_ip()

print("\n" + "="*60)
print("🚀 초간단 모바일 대시보드 뷰어")
print("="*60)
print(f"\n📱 모바일에서 이렇게 접속하세요:")
print(f"\n   1. 모바일 브라우저 열기")
print(f"   2. 주소창에 입력: http://{ip}:{PORT}")
print(f"   3. output_files 폴더 클릭")
print(f"   4. 대시보드 HTML 파일 클릭")
print("\n⚠️  컴퓨터와 모바일이 같은 와이파이에 연결되어 있어야 합니다")
print("\n종료: Ctrl+C")
print("="*60 + "\n")

# 웹 서버 실행 (현재 폴더를 공유)
os.chdir('.')  # 현재 디렉토리에서 실행
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"서버 실행 중... (http://{ip}:{PORT})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 서버를 종료합니다!")
        httpd.shutdown()