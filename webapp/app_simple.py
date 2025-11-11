#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QIP 대시보드 - 간단한 버전 (무료 호스팅용)
PythonAnywhere, Render 등에서 사용하기 위한 경량 버전
"""

from flask import Flask, render_template, send_file, jsonify, request, session, redirect, url_for
import os
import glob
from datetime import datetime
import secrets
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# 간단한 설정
CONFIG = {
    'ADMIN_PASSWORD': os.environ.get('ADMIN_PASSWORD', 'qip2025admin')
}

def login_required(f):
    """로그인 체크"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """메인 페이지"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index_simple.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == CONFIG['ADMIN_PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='비밀번호가 올바르지 않습니다')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/dashboards')
@login_required
def list_dashboards():
    """대시보드 파일 목록"""
    try:
        # output_files 디렉토리에서 HTML 파일 찾기
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, 'output_files')

        dashboards = []
        if os.path.exists(output_dir):
            pattern = os.path.join(output_dir, 'Incentive_Dashboard_*.html')
            for filepath in glob.glob(pattern):
                filename = os.path.basename(filepath)
                # 파일명에서 년월 추출
                try:
                    parts = filename.replace('.html', '').split('_')
                    year = parts[2]
                    month = parts[3]
                    dashboards.append({
                        'filename': filename,
                        'year': year,
                        'month': month,
                        'display': f"{year}년 {int(month)}월",
                        'size': os.path.getsize(filepath) // 1024  # KB
                    })
                except:
                    pass

        # 최신순 정렬
        dashboards.sort(key=lambda x: (x['year'], x['month']), reverse=True)
        return jsonify(dashboards)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/view/<filename>')
@login_required
def view_dashboard(filename):
    """대시보드 HTML 파일 보기"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, 'output_files', filename)

        if os.path.exists(filepath) and filename.endswith('.html'):
            return send_file(filepath)
        else:
            return "파일을 찾을 수 없습니다", 404

    except Exception as e:
        return f"오류: {str(e)}", 500

@app.route('/api/status')
def status():
    """서버 상태"""
    return jsonify({
        'status': 'running',
        'time': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(e):
    """404 에러 페이지"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    # 로컬 테스트용
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)