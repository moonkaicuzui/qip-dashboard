#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
"""
PythonAnywhere WSGI configuration
이 파일을 PythonAnywhere의 WSGI configuration file 란에 붙여넣으세요
"""

import sys
import os
from pathlib import Path

# 프로젝트 경로 추가 (username을 자신의 PythonAnywhere 사용자명으로 변경)
username = 'your_username'  # ⚠️ 여기를 변경하세요!
project_home = f'/home/{username}/qip-dashboard'

if project_home not in sys.path:
    sys.path.insert(0, project_home)
    sys.path.insert(0, f'{project_home}/webapp')

# 작업 디렉토리 설정
os.chdir(project_home)

# Flask 앱 임포트
from webapp.app import app as application

# PythonAnywhere용 설정 추가
application.config['ENV'] = 'production'
application.config['DEBUG'] = False

print(f"✅ WSGI loaded successfully from {project_home}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")