#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive 다운로드 + Config 자동 업데이트 통합 스크립트

주요 개선사항:
1. 구글 드라이브에서 데이터 다운로드
2. 실제 다운로드된 파일 경로를 config에 자동 반영
3. attendance 데이터에서 working_days 자동 계산
4. 한 번의 실행으로 모든 자동화 완료
"""

import os
import json
import sys
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pandas as pd
import re

def init_google_drive_service():
    """Google Drive 서비스 초기화"""
    try:
        service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT', '{}'))

        if not service_account_info:
            print("❌ 오류: GOOGLE_SERVICE_ACCOUNT 환경변수가 설정되지 않았습니다")
            sys.exit(1)

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )

        service = build('drive', 'v3', credentials=credentials)
        print("✅ Google Drive 서비스 초기화 성공")
        return service

    except Exception as e:
        print(f"❌ Google Drive 서비스 초기화 실패: {e}")
        sys.exit(1)

def list_files_in_folder(service, folder_id, file_type='csv'):
    """특정 폴더의 파일 목록 가져오기"""
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        if file_type:
            if file_type == 'csv':
                query += " and (mimeType='text/csv' or name contains '.csv')"

        results = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime, mimeType)",
            orderBy="modifiedTime desc"
        ).execute()

        return results.get('files', [])

    except Exception as e:
        print(f"❌ 폴더 목록 조회 실패 ({folder_id}): {e}")
        return []

def download_file(service, file_id, output_path, force=True):
    """Google Drive 파일 다운로드"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if os.path.exists(output_path):
            if force:
                old_mtime = datetime.fromtimestamp(os.path.getmtime(output_path))
                print(f"  🔄 기존 파일 삭제 (수정일: {old_mtime.strftime('%Y-%m-%d %H:%M:%S')})")
                os.remove(output_path)
            else:
                print(f"  ⚠️ 파일이 이미 존재합니다 (건너뜀)")
                return False

        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        with open(output_path, 'wb') as f:
            f.write(fh.getvalue())

        new_mtime = datetime.fromtimestamp(os.path.getmtime(output_path))
        file_size = os.path.getsize(output_path)
        print(f"  ✅ 다운로드 완료 ({file_size:,} bytes, 수정일: {new_mtime.strftime('%Y-%m-%d %H:%M:%S')})")

        return True

    except Exception as e:
        print(f"  ❌ 다운로드 실패: {e}")
        return False

def month_number_to_name(month_num):
    """월 숫자를 영문 이름으로 변환"""
    month_names = {
        1: 'january', 2: 'february', 3: 'march', 4: 'april',
        5: 'may', 6: 'june', 7: 'july', 8: 'august',
        9: 'september', 10: 'october', 11: 'november', 12: 'december'
    }
    return month_names.get(month_num, 'unknown')

def calculate_working_days_from_attendance(attendance_file_path):
    """Attendance 데이터에서 실제 근무일수를 계산"""
    try:
        df = pd.read_csv(attendance_file_path, encoding='utf-8-sig')

        if 'Work Date' in df.columns:
            unique_dates = df['Work Date'].dropna().unique()
            working_days = len(unique_dates)
            print(f"    📊 Work Date 기준 총 근무일수: {working_days}일")
            return working_days

        day_columns = [col for col in df.columns if col.startswith('Day_')]
        if day_columns:
            working_days = len(day_columns)
            print(f"    📊 Day 컬럼 기준 총 근무일수: {working_days}일")
            return working_days

        return None

    except Exception as e:
        print(f"    ❌ Attendance 파일 분석 실패: {e}")
        return None

def update_config_for_month(year, month_name, downloaded_files):
    """특정 월의 config 파일을 업데이트"""
    config_path = f"config_files/config_{month_name}_{year}.json"

    print(f"\n  📝 Config 업데이트: {config_path}")

    # 기존 config 로드 또는 새로 생성
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("    기존 config 파일 로드")
    else:
        print("    새 config 파일 생성")
        config = {
            "year": year,
            "month": month_name,
            "working_days": 23
        }

    # 실제 다운로드된 파일 경로 매핑
    file_paths = {}

    for file_info in downloaded_files:
        file_path = file_info['local_path']
        file_name = os.path.basename(file_path).lower()

        if 'basic' in file_name and 'manpower' in file_name:
            file_paths['basic_manpower'] = file_path
        elif 'attendance' in file_name or '출근' in file_name:
            if 'converted' in file_path:
                file_paths['attendance'] = file_path
            elif 'attendance' not in file_paths:  # converted가 없으면 original 사용
                file_paths['attendance'] = file_path
        elif '5prs' in file_name.lower():
            file_paths['5prs'] = file_path
        elif 'aql' in file_name.lower() and month_name.upper() in file_name.upper():
            file_paths['aql_current'] = file_path

    # Previous incentive 파일 경로 설정
    prev_month_names = {
        'january': 'december', 'february': 'january', 'march': 'february',
        'april': 'march', 'may': 'april', 'june': 'may',
        'july': 'june', 'august': 'july', 'september': 'august',
        'october': 'september', 'november': 'october', 'december': 'november'
    }
    prev_month = prev_month_names.get(month_name.lower())
    prev_year = year if month_name.lower() != 'january' else year - 1

    # 여러 버전 체크 (V9.1 → V9.0 → V8.02)
    for version in ['V9.1', 'V9.0', 'V8.02']:
        prev_path = f"output_files/output_QIP_incentive_{prev_month}_{prev_year}_Complete_{version}_Complete.csv"
        if os.path.exists(prev_path):
            file_paths['previous_incentive'] = prev_path
            break
    else:
        file_paths['previous_incentive'] = f"output_files/output_QIP_incentive_{prev_month}_{prev_year}_Complete_V9.1_Complete.csv"

    config['file_paths'] = file_paths

    # Working days 계산 및 업데이트
    if 'attendance' in file_paths and os.path.exists(file_paths['attendance']):
        print(f"    📊 Working days 계산 중...")
        working_days = calculate_working_days_from_attendance(file_paths['attendance'])
        if working_days:
            old_days = config.get('working_days', 'N/A')
            config['working_days'] = working_days
            config['working_days_source'] = 'attendance_data'
            config['working_days_updated_at'] = datetime.now().isoformat()
            print(f"    ✅ Working days 업데이트: {old_days} → {working_days}")

    # Previous months 설정
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    month_idx = months.index(month_name.lower())
    prev_months = []
    for i in range(1, 3):
        prev_idx = (month_idx - i) % 12
        prev_months.append(months[prev_idx])
    config['previous_months'] = list(reversed(prev_months))

    # 기타 필드 업데이트
    config['output_prefix'] = f"output_QIP_incentive_{month_name}_{year}"
    config['data_source'] = 'google_drive'
    config['created_at'] = config.get('created_at', datetime.now().isoformat())
    config['last_updated'] = datetime.now().isoformat()

    # Config 저장
    os.makedirs('config_files', exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"    ✅ Config 업데이트 완료")

    # 파일 검증
    print(f"    🔍 파일 존재 여부 검증:")
    for key, path in file_paths.items():
        exists = os.path.exists(path)
        status = "✅" if exists else "⚠️"
        print(f"      {status} {key}: {os.path.basename(path)}")

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("🚀 Google Drive 다운로드 + Config 자동 업데이트 통합 시스템")
    print("=" * 70)

    # Google Drive 서비스 초기화
    service = init_google_drive_service()

    # drive_config.json 로드
    drive_config = None
    if os.path.exists('config_files/drive_config.json'):
        with open('config_files/drive_config.json', 'r', encoding='utf-8') as f:
            drive_config = json.load(f)
        print("✅ drive_config.json 로드 완료")

    # 폴더 ID 가져오기
    if drive_config:
        folder_structure = drive_config.get('google_drive', {}).get('folder_structure', {})
        monthly_data_id = folder_structure.get('monthly_data', {}).get('id')
        aql_folder_id = folder_structure.get('aql_history', {}).get('id')
    else:
        monthly_data_id = os.environ.get('GDRIVE_FOLDER_ID')
        aql_folder_id = None

    if not monthly_data_id:
        print("❌ 월별 데이터 폴더 ID를 찾을 수 없습니다")
        sys.exit(1)

    # 최신 월 폴더 찾기
    print(f"\n📁 월별 데이터 폴더 스캔 중...")
    query = f"'{monthly_data_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name)",
        orderBy="name desc"
    ).execute()

    month_folders = []
    for folder in results.get('files', []):
        match = re.match(r'(\d{4})_(\d{1,2})', folder['name'])
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            month_folders.append({
                'id': folder['id'],
                'name': folder['name'],
                'year': year,
                'month': month,
                'month_name': month_number_to_name(month)
            })

    month_folders.sort(key=lambda x: (x['year'], x['month']), reverse=True)

    if not month_folders:
        print("⚠️ 월 폴더를 찾을 수 없습니다")
        sys.exit(1)

    print(f"✅ {len(month_folders)}개 월 폴더 발견")

    # 각 월별로 처리 (최신 3개월만)
    for month_folder in month_folders[:3]:
        print(f"\n{'='*50}")
        print(f"📅 {month_folder['name']} ({month_folder['month_name']} {month_folder['year']}) 처리 중...")

        # 해당 월 파일 다운로드
        files = list_files_in_folder(service, month_folder['id'])
        print(f"  📥 {len(files)}개 파일 발견")

        downloaded_files = []
        for file in files:
            file_name = file['name'].lower()
            output_path = None

            # 파일 타입별 경로 설정
            if 'basic' in file_name and 'manpower' in file_name:
                output_path = f"input_files/basic manpower data {month_folder['month_name']}.csv"
            elif 'attendance' in file_name or '출근' in file_name:
                output_path = f"input_files/attendance/original/attendance data {month_folder['month_name']}.csv"
            elif '5prs' in file_name:
                output_path = f"input_files/5prs data {month_folder['month_name']}.csv"
            else:
                backup_dir = f"input_files/monthly_data/{month_folder['name']}"
                os.makedirs(backup_dir, exist_ok=True)
                output_path = f"{backup_dir}/{file['name']}"

            if output_path:
                print(f"  다운로드: {file['name']} → {output_path}")
                if download_file(service, file['id'], output_path, force=True):
                    downloaded_files.append({
                        'google_name': file['name'],
                        'local_path': output_path,
                        'file_id': file['id']
                    })

        # AQL 파일 다운로드
        if aql_folder_id:
            print(f"\n  📊 AQL History 다운로드 중...")
            aql_files = list_files_in_folder(service, aql_folder_id)
            os.makedirs('input_files/AQL history', exist_ok=True)

            for file in aql_files:
                match = re.search(r'AQL_REPORT_([A-Z]+)_(\d{4})', file['name'], re.IGNORECASE)
                if match:
                    aql_month = match.group(1).upper()
                    aql_year = match.group(2)
                    if aql_month == month_folder['month_name'].upper() and aql_year == str(month_folder['year']):
                        output_path = f"input_files/AQL history/1.HSRG AQL REPORT-{aql_month}.{aql_year}.csv"
                        print(f"  다운로드: {file['name']} → {output_path}")
                        if download_file(service, file['id'], output_path, force=True):
                            downloaded_files.append({
                                'google_name': file['name'],
                                'local_path': output_path,
                                'file_id': file['id']
                            })
                        break

        # Config 파일 자동 업데이트
        update_config_for_month(month_folder['year'], month_folder['month_name'], downloaded_files)

    print("\n" + "=" * 70)
    print("✅ Google Drive 다운로드 + Config 업데이트 완료!")
    print("=" * 70)

if __name__ == "__main__":
    main()