#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 인센티브 대시보드 웹 애플리케이션
실시간 Google Drive 연동 및 대시보드 자동 생성
"""

from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import os
import sys
import json
from datetime import datetime, timedelta
import subprocess
import threading
import time
import hashlib
import secrets

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.google_drive_manager import GoogleDriveManager
import integrated_dashboard_final as dashboard_generator

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # 세션을 위한 시크릿 키
CORS(app)

# 설정
CONFIG = {
    'UPDATE_INTERVAL': 3600,  # 1시간마다 자동 업데이트 (초)
    'CACHE_DURATION': 1800,   # 30분 캐시 (초)
    'ADMIN_PASSWORD': 'qip2025admin',  # 실제 운영 시 환경변수로 관리
    'ALLOWED_USERS': ['admin', 'viewer'],  # 허용된 사용자
}

# 글로벌 변수
last_update = None
dashboard_cache = {}
update_lock = threading.Lock()
drive_manager = None

def init_drive_manager():
    """Google Drive Manager 초기화"""
    global drive_manager
    try:
        drive_manager = GoogleDriveManager()
        return True
    except Exception as e:
        print(f"❌ Google Drive 초기화 실패: {e}")
        return False

def login_required(f):
    """로그인 체크 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """메인 페이지 - 대시보드 목록"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == CONFIG['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session['user'] = 'admin'
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='비밀번호가 올바르지 않습니다')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard/<int:year>/<int:month>')
@login_required
def view_dashboard(year, month):
    """특정 월 대시보드 보기"""
    global dashboard_cache, last_update

    cache_key = f"{year}_{month}"

    # 캐시 확인
    if cache_key in dashboard_cache:
        cached_data = dashboard_cache[cache_key]
        if (datetime.now() - cached_data['timestamp']).seconds < CONFIG['CACHE_DURATION']:
            print(f"✅ 캐시된 대시보드 제공: {year}년 {month}월")
            return cached_data['html']

    # 새로 생성
    try:
        html_content = generate_dashboard_realtime(year, month)

        # 캐시 저장
        dashboard_cache[cache_key] = {
            'html': html_content,
            'timestamp': datetime.now()
        }

        return html_content
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync-drive')
@login_required
def sync_drive():
    """Google Drive 수동 동기화"""
    try:
        result = sync_google_drive_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-dashboard', methods=['POST'])
@login_required
def generate_dashboard_api():
    """대시보드 수동 생성 API"""
    data = request.json
    year = data.get('year', datetime.now().year)
    month = data.get('month', datetime.now().month)

    try:
        result = run_dashboard_generation(year, month)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """시스템 상태 확인"""
    return jsonify({
        'status': 'running',
        'last_update': last_update.isoformat() if last_update else None,
        'cache_count': len(dashboard_cache),
        'drive_connected': drive_manager is not None
    })

@app.route('/api/available-dashboards')
@login_required
def available_dashboards():
    """사용 가능한 대시보드 목록"""
    dashboards = []

    # output_files 디렉토리 스캔
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_files')
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.startswith('Incentive_Dashboard') and file.endswith('.html'):
                try:
                    # 파일명에서 년월 추출
                    parts = file.replace('.html', '').split('_')
                    year = int(parts[2])
                    month = int(parts[3])
                    dashboards.append({
                        'year': year,
                        'month': month,
                        'filename': file,
                        'display': f"{year}년 {month}월"
                    })
                except:
                    pass

    # 정렬 (최신 순)
    dashboards.sort(key=lambda x: (x['year'], x['month']), reverse=True)

    return jsonify(dashboards)

def sync_google_drive_data():
    """Google Drive 데이터 동기화"""
    global last_update

    if not drive_manager:
        if not init_drive_manager():
            return {'success': False, 'message': 'Google Drive 연결 실패'}

    try:
        print("🔄 Google Drive 동기화 시작...")

        # 현재 월 기준으로 데이터 다운로드
        current_date = datetime.now()
        month_num = current_date.month
        year = current_date.year

        # 여러 패턴으로 시도
        patterns = [
            f"{year}년 {month_num}월",
            f"{year}year {month_num}month",
            f"QIP_incentive_{year}_{month_num:02d}"
        ]

        total_files = 0
        for pattern in patterns:
            files = drive_manager.download_files(pattern, 'input_files')
            total_files += len(files)

        last_update = datetime.now()

        return {
            'success': True,
            'files_synced': total_files,
            'timestamp': last_update.isoformat()
        }

    except Exception as e:
        return {'success': False, 'message': str(e)}

def generate_dashboard_realtime(year, month):
    """실시간 대시보드 생성"""
    with update_lock:
        print(f"🔨 대시보드 생성 중: {year}년 {month}월")

        # 1. Google Drive 동기화
        sync_result = sync_google_drive_data()
        if not sync_result['success']:
            print(f"⚠️ Drive 동기화 실패, 로컬 데이터 사용")

        # 2. 인센티브 계산 실행
        run_incentive_calculation(year, month)

        # 3. 대시보드 HTML 생성
        month_names = ['', 'january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        month_name = month_names[month]

        # integrated_dashboard_final의 함수 직접 호출
        df = dashboard_generator.load_incentive_data(month_name, year)
        if df.empty:
            raise Exception("데이터 로드 실패")

        html_content = dashboard_generator.generate_html_dashboard(df, {}, month_name, year)

        print(f"✅ 대시보드 생성 완료: {year}년 {month}월")
        return html_content

def run_incentive_calculation(year, month):
    """인센티브 계산 스크립트 실행"""
    try:
        # action.sh 스크립트 실행 (비대화형 모드)
        env = os.environ.copy()
        env['YEAR'] = str(year)
        env['MONTH'] = str(month)
        env['AUTO_MODE'] = 'true'  # 자동 모드 플래그

        cmd = ['bash', 'action.sh']
        result = subprocess.run(cmd,
                              capture_output=True,
                              text=True,
                              env=env,
                              timeout=300)  # 5분 타임아웃

        if result.returncode == 0:
            print(f"✅ 인센티브 계산 완료: {year}년 {month}월")
            return True
        else:
            print(f"❌ 인센티브 계산 실패: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ 인센티브 계산 타임아웃")
        return False
    except Exception as e:
        print(f"❌ 인센티브 계산 오류: {e}")
        return False

def run_dashboard_generation(year, month):
    """대시보드 생성 프로세스 실행"""
    try:
        # 1. Google Drive 동기화
        sync_result = sync_google_drive_data()

        # 2. 인센티브 계산
        calc_success = run_incentive_calculation(year, month)

        # 3. 대시보드 생성
        if calc_success:
            cache_key = f"{year}_{month}"
            dashboard_cache.pop(cache_key, None)  # 캐시 클리어

            return {
                'success': True,
                'message': f'{year}년 {month}월 대시보드 생성 완료',
                'sync': sync_result,
                'calculation': calc_success
            }
        else:
            return {
                'success': False,
                'message': '인센티브 계산 실패'
            }

    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def background_updater():
    """백그라운드 자동 업데이트"""
    while True:
        try:
            time.sleep(CONFIG['UPDATE_INTERVAL'])

            # 현재 월 대시보드 자동 업데이트
            current = datetime.now()
            result = run_dashboard_generation(current.year, current.month)
            print(f"🔄 자동 업데이트 완료: {result}")

        except Exception as e:
            print(f"❌ 자동 업데이트 실패: {e}")

# 백그라운드 스레드 시작
update_thread = threading.Thread(target=background_updater, daemon=True)
update_thread.start()

if __name__ == '__main__':
    # 초기화
    init_drive_manager()

    # 개발 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=False)