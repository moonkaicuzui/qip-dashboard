#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
모바일에서 대시보드 보기 - 초간단 버전
같은 와이파이에 연결된 모바일에서 대시보드를 볼 수 있게 해줍니다.
"""

import os
import socket
import http.server
import socketserver
import webbrowser
import qrcode
import io
import base64
from datetime import datetime

def get_local_ip():
    """컴퓨터의 로컬 IP 주소 찾기"""
    try:
        # 외부와 연결하여 실제 IP 확인
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def generate_qr_code(url):
    """URL을 QR 코드로 변환"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # QR 코드를 base64로 인코딩
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return img_str

def create_index_page():
    """대시보드 목록 페이지 생성"""
    # output_files 폴더의 모든 대시보드 찾기
    dashboard_files = []
    for file in os.listdir('output_files'):
        if file.startswith('Incentive_Dashboard') and file.endswith('.html'):
            # 파일명에서 연도와 월 추출
            try:
                parts = file.replace('.html', '').split('_')
                year = parts[2]
                month = parts[3]
                dashboard_files.append({
                    'filename': file,
                    'year': year,
                    'month': month,
                    'display': f"{year}년 {int(month)}월 대시보드"
                })
            except:
                dashboard_files.append({
                    'filename': file,
                    'display': file
                })

    # 최신 파일이 위로 오도록 정렬
    dashboard_files.sort(key=lambda x: x['filename'], reverse=True)

    # HTML 생성
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QIP 인센티브 대시보드 - 모바일 뷰어</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            .header {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                font-size: 28px;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .subtitle {{
                color: #666;
                font-size: 16px;
                margin-bottom: 20px;
            }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .info-box p {{
                margin: 5px 0;
                color: #555;
            }}
            .dashboard-list {{
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            .dashboard-item {{
                display: block;
                padding: 20px;
                margin: 10px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                transition: transform 0.3s, box-shadow 0.3s;
                cursor: pointer;
            }}
            .dashboard-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }}
            .dashboard-item .title {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .dashboard-item .date {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .qr-section {{
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-top: 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            .qr-code {{
                margin: 20px auto;
            }}
            .url-box {{
                background: #f0f0f0;
                padding: 15px;
                border-radius: 10px;
                word-break: break-all;
                font-family: monospace;
                font-size: 16px;
                color: #333;
                margin: 20px 0;
            }}
            @media (max-width: 600px) {{
                h1 {{
                    font-size: 24px;
                }}
                .dashboard-item {{
                    padding: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 QIP 인센티브 대시보드</h1>
                <p class="subtitle">모바일에서 편하게 보세요!</p>

                <div class="info-box">
                    <p>✅ <strong>컴퓨터와 모바일이 같은 와이파이에 연결되어 있어야 합니다</strong></p>
                    <p>📱 모바일에서 아래 QR 코드를 스캔하거나 URL을 입력하세요</p>
                    <p>💡 대시보드를 클릭하면 바로 열립니다</p>
                </div>
            </div>

            <div class="dashboard-list">
                <h2 style="margin-bottom: 20px; color: #333;">📁 사용 가능한 대시보드</h2>
    """

    if dashboard_files:
        for dash in dashboard_files:
            if 'year' in dash and 'month' in dash:
                html += f"""
                <a href="/output_files/{dash['filename']}" class="dashboard-item">
                    <div class="title">{dash['display']}</div>
                    <div class="date">파일: {dash['filename']}</div>
                </a>
                """
            else:
                html += f"""
                <a href="/output_files/{dash['filename']}" class="dashboard-item">
                    <div class="title">{dash['display']}</div>
                </a>
                """
    else:
        html += """
        <p style="color: #999; text-align: center; padding: 40px;">
            대시보드 파일이 없습니다.<br>
            먼저 대시보드를 생성해주세요.
        </p>
        """

    html += """
            </div>
        </div>
    </body>
    </html>
    """

    return html

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """커스텀 HTTP 핸들러"""

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            # 인덱스 페이지 제공
            html = create_index_page()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            # 기본 파일 서빙
            super().do_GET()

def main():
    PORT = 8000

    print("\n" + "="*60)
    print("🚀 모바일 대시보드 뷰어 시작")
    print("="*60)

    # IP 주소 가져오기
    ip_address = get_local_ip()
    url = f"http://{ip_address}:{PORT}"

    print(f"\n📱 모바일에서 접속하는 방법:")
    print(f"\n1️⃣  모바일 브라우저에서 다음 주소를 입력하세요:")
    print(f"    {url}")

    # QR 코드 생성 (qrcode 패키지가 설치된 경우)
    try:
        qr_data = generate_qr_code(url)
        print(f"\n2️⃣  또는 아래 링크를 클릭해서 QR 코드를 확인하세요:")
        print(f"    http://localhost:{PORT}")
        print("\n📌 QR 코드는 브라우저에서 확인할 수 있습니다.")
    except:
        print("\n(QR 코드 생성을 위해서는 'pip install qrcode pillow' 설치가 필요합니다)")

    print("\n⚠️  주의사항:")
    print("  • 컴퓨터와 모바일이 같은 와이파이에 연결되어 있어야 합니다")
    print("  • 방화벽이 차단하고 있다면 허용해주세요")
    print("  • 종료하려면 Ctrl+C를 누르세요")
    print("\n" + "="*60)

    # 웹 브라우저 자동 열기
    try:
        webbrowser.open(f'http://localhost:{PORT}')
        print(f"\n✅ 브라우저가 자동으로 열렸습니다!")
    except:
        print(f"\n브라우저에서 http://localhost:{PORT} 를 열어주세요")

    # 서버 시작
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"\n🌐 서버가 실행 중입니다... (종료: Ctrl+C)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 서버를 종료합니다. 안녕히 가세요!")
            httpd.shutdown()

if __name__ == "__main__":
    main()