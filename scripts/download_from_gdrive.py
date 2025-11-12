#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive CSV 자동 다운로드 스크립트
GitHub Actions에서 실행되어 Google Drive의 CSV 파일들을 다운로드
"""

import os
import json
import sys
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

def init_google_drive_service():
    """Google Drive 서비스 초기화"""
    try:
        # GitHub Secrets에서 서비스 계정 정보 가져오기
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

def download_csv_files(service, folder_id):
    """Google Drive 폴더에서 모든 CSV 파일 다운로드"""

    try:
        # output_files 디렉토리 생성
        os.makedirs('output_files', exist_ok=True)

        # 폴더 내 CSV 파일 목록 가져오기
        query = f"'{folder_id}' in parents and mimeType='text/csv' and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()

        items = results.get('files', [])

        if not items:
            print(f"⚠️ 폴더 {folder_id}에 CSV 파일이 없습니다")
            return []

        print(f"📁 {len(items)}개의 CSV 파일 발견")

        downloaded_files = []

        for item in items:
            try:
                file_name = item['name']
                file_id = item['id']
                modified_time = item['modifiedTime']

                print(f"📥 다운로드 중: {file_name}")

                # 파일 다운로드
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"    진행률: {int(status.progress() * 100)}%")

                # 파일 저장
                output_path = f"output_files/{file_name}"

                # 파일명 패턴 확인 및 정규화
                if 'QIP_incentive' in file_name and file_name.endswith('.csv'):
                    # 기존 패턴 유지
                    pass
                elif 'incentive' in file_name.lower() and file_name.endswith('.csv'):
                    # 파일명 정규화 시도
                    # 예: "november_2025_incentive.csv" → "output_QIP_incentive_november_2025_Complete_V8.02_Complete.csv"
                    parts = file_name.lower().replace('.csv', '').split('_')
                    if any(month in parts for month in ['january', 'february', 'march', 'april', 'may', 'june',
                                                         'july', 'august', 'september', 'october', 'november', 'december']):
                        # 월 찾기
                        month = next((m for m in parts if m in ['january', 'february', 'march', 'april', 'may', 'june',
                                                                 'july', 'august', 'september', 'october', 'november', 'december']), None)
                        # 연도 찾기
                        year = next((p for p in parts if p.isdigit() and len(p) == 4), '2025')

                        if month:
                            file_name = f"output_QIP_incentive_{month}_{year}_Complete_V8.02_Complete.csv"
                            output_path = f"output_files/{file_name}"

                with open(output_path, 'wb') as f:
                    f.write(fh.getvalue())

                print(f"    ✅ 저장 완료: {output_path}")
                print(f"    📅 수정 시간: {modified_time}")

                downloaded_files.append({
                    'name': file_name,
                    'path': output_path,
                    'modified': modified_time
                })

            except Exception as e:
                print(f"    ❌ 다운로드 실패: {e}")
                continue

        return downloaded_files

    except Exception as e:
        print(f"❌ 파일 목록 가져오기 실패: {e}")
        return []

def create_metadata_file(downloaded_files):
    """다운로드 메타데이터 파일 생성"""
    metadata = {
        'last_update': datetime.now().isoformat(),
        'files': downloaded_files,
        'total_files': len(downloaded_files)
    }

    with open('output_files/gdrive_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"📝 메타데이터 파일 생성 완료")

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 Google Drive CSV 다운로드 시작")
    print("=" * 60)

    # Google Drive 폴더 ID 가져오기
    folder_id = os.environ.get('GDRIVE_FOLDER_ID')

    if not folder_id:
        print("❌ 오류: GDRIVE_FOLDER_ID 환경변수가 설정되지 않았습니다")
        print("GitHub Secrets에 GDRIVE_FOLDER_ID를 설정하세요")
        sys.exit(1)

    print(f"📁 대상 폴더 ID: {folder_id}")

    # Google Drive 서비스 초기화
    service = init_google_drive_service()

    # CSV 파일 다운로드
    downloaded_files = download_csv_files(service, folder_id)

    if downloaded_files:
        # 메타데이터 파일 생성
        create_metadata_file(downloaded_files)

        print("=" * 60)
        print(f"✅ 다운로드 완료: {len(downloaded_files)}개 파일")
        print("=" * 60)

        # 다운로드된 파일 목록 출력
        for file_info in downloaded_files:
            print(f"  - {file_info['name']}")
    else:
        print("⚠️ 다운로드된 파일이 없습니다")
        sys.exit(0)

if __name__ == "__main__":
    main()