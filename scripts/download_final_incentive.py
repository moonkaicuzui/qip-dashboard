#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Final Incentive 데이터 다운로드 스크립트

Google Drive에서 "Final [Month] incentive.xlsx" 파일을 다운로드합니다.
이 파일은 실제 급여 데이터로, Previous_Incentive의 Single Source of Truth입니다.

사용법:
    python scripts/download_final_incentive.py november 2025
    python scripts/download_final_incentive.py december 2025
"""

import os
import sys
import json
import io
from datetime import datetime
from pathlib import Path

# Google API imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
except ImportError:
    print("❌ Google API 라이브러리가 설치되지 않았습니다")
    print("   pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)


# Month name mappings
MONTH_NAMES = {
    1: 'january', 2: 'february', 3: 'march', 4: 'april',
    5: 'may', 6: 'june', 7: 'july', 8: 'august',
    9: 'september', 10: 'october', 11: 'november', 12: 'december'
}

MONTH_NAMES_REVERSE = {v: k for k, v in MONTH_NAMES.items()}

# Display names for file search (as user named them)
MONTH_DISPLAY_NAMES = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}


def init_google_drive_service():
    """Google Drive 서비스 초기화"""
    try:
        service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT', '{}'))

        if not service_account_info:
            # Try loading from local file for development
            local_key_path = "/Users/ksmoon/Downloads/qip-dashboard-dabdc4d51ac9.json"
            if os.path.exists(local_key_path):
                with open(local_key_path, 'r') as f:
                    service_account_info = json.load(f)
                print("✅ 로컬 서비스 계정 키 사용")
            else:
                print("❌ GOOGLE_SERVICE_ACCOUNT 환경변수가 설정되지 않았습니다")
                return None

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )

        service = build('drive', 'v3', credentials=credentials)
        print("✅ Google Drive 서비스 초기화 성공")
        return service

    except Exception as e:
        print(f"❌ Google Drive 서비스 초기화 실패: {e}")
        return None


def load_drive_config():
    """drive_config.json 로드"""
    config_path = Path("config_files/drive_config.json")

    if not config_path.exists():
        print(f"❌ {config_path} 파일이 없습니다")
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_monthly_folder(service, parent_folder_id, year, month):
    """월별 폴더 찾기 (예: 2025_11)"""
    folder_name = f"{year}_{month:02d}"

    try:
        query = f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if files:
            print(f"✅ 월별 폴더 찾음: {folder_name} (ID: {files[0]['id']})")
            return files[0]['id']
        else:
            print(f"❌ 월별 폴더를 찾을 수 없음: {folder_name}")
            return None

    except Exception as e:
        print(f"❌ 폴더 검색 실패: {e}")
        return None


def find_final_incentive_file(service, folder_id, month_name):
    """Final Incentive 파일 찾기"""
    # 가능한 파일명 패턴들
    search_patterns = [
        f"Final {month_name.capitalize()} incentive",
        f"Final {month_name} incentive",
        f"Final_{month_name}_incentive",
        f"final {month_name} incentive",
        f"Final {MONTH_DISPLAY_NAMES.get(MONTH_NAMES_REVERSE.get(month_name.lower(), 0), month_name)} incentive"
    ]

    try:
        # 폴더 내 모든 Excel 파일 검색
        query = f"'{folder_id}' in parents and (mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or name contains '.xlsx') and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()
        files = results.get('files', [])

        print(f"📂 폴더 내 Excel 파일 {len(files)}개 발견")

        for file in files:
            file_name = file['name'].lower()
            for pattern in search_patterns:
                if pattern.lower() in file_name:
                    print(f"✅ Final Incentive 파일 찾음: {file['name']}")
                    print(f"   수정일: {file['modifiedTime']}")
                    return file

        # 패턴 매칭 실패 시, "final"과 "incentive"가 포함된 파일 검색
        for file in files:
            file_name = file['name'].lower()
            if 'final' in file_name and 'incentive' in file_name:
                print(f"✅ Final Incentive 파일 찾음 (유사 매칭): {file['name']}")
                return file

        print(f"❌ Final Incentive 파일을 찾을 수 없습니다")
        print(f"   검색 패턴: {search_patterns}")
        print(f"   폴더 내 파일: {[f['name'] for f in files]}")
        return None

    except Exception as e:
        print(f"❌ 파일 검색 실패: {e}")
        return None


def download_file(service, file_id, file_name, output_path):
    """파일 다운로드"""
    try:
        # 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 기존 파일 삭제
        if os.path.exists(output_path):
            print(f"  🔄 기존 파일 삭제: {output_path}")
            os.remove(output_path)

        # 다운로드
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"  📥 다운로드 진행: {int(status.progress() * 100)}%")

        # 저장
        with open(output_path, 'wb') as f:
            f.write(fh.getvalue())

        file_size = os.path.getsize(output_path)
        print(f"✅ 다운로드 완료: {output_path} ({file_size:,} bytes)")
        return True

    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        return False


def verify_downloaded_file(file_path, expected_month_name):
    """다운로드된 파일 검증"""
    try:
        import pandas as pd

        df = pd.read_excel(file_path)
        print(f"\n📊 다운로드된 파일 검증:")
        print(f"   행 수: {len(df)}")
        print(f"   컬럼: {list(df.columns)[:5]}...")

        # 인센티브 컬럼 찾기
        incentive_col = None
        for col in df.columns:
            if 'incentive' in col.lower() and expected_month_name.lower() in col.lower():
                incentive_col = col
                break
            elif '_incentive' in col.lower():
                incentive_col = col

        if incentive_col:
            total = df[incentive_col].fillna(0).sum()
            receiving = (df[incentive_col].fillna(0) > 0).sum()
            print(f"   인센티브 컬럼: {incentive_col}")
            print(f"   총액: ₫{total:,.0f}")
            print(f"   수령자: {receiving}명")

        return True

    except Exception as e:
        print(f"⚠️ 파일 검증 중 오류: {e}")
        return False


def download_final_incentive(month_name, year):
    """메인 다운로드 함수"""
    print("=" * 70)
    print(f"📥 Final Incentive 다운로드: {month_name.capitalize()} {year}")
    print("=" * 70)

    # 1. 서비스 초기화
    service = init_google_drive_service()
    if not service:
        return None

    # 2. 설정 로드
    config = load_drive_config()
    if not config:
        return None

    monthly_data_folder_id = config['google_drive']['folder_structure']['monthly_data']['id']

    # 3. 월 번호 변환
    month_num = MONTH_NAMES_REVERSE.get(month_name.lower())
    if not month_num:
        print(f"❌ 잘못된 월 이름: {month_name}")
        return None

    # 4. 월별 폴더 찾기
    folder_id = find_monthly_folder(service, monthly_data_folder_id, year, month_num)
    if not folder_id:
        return None

    # 5. Final Incentive 파일 찾기
    file_info = find_final_incentive_file(service, folder_id, month_name)
    if not file_info:
        return None

    # 6. 다운로드
    output_path = f"input_files/final_incentive/Final_{month_name}_{year}_incentive.xlsx"
    success = download_file(service, file_info['id'], file_info['name'], output_path)

    if not success:
        return None

    # 7. 검증
    verify_downloaded_file(output_path, month_name)

    print("\n" + "=" * 70)
    print(f"✅ Final Incentive 다운로드 완료!")
    print(f"   파일: {output_path}")
    print("=" * 70)

    return output_path


def main():
    """메인 함수"""
    if len(sys.argv) < 3:
        print("사용법: python download_final_incentive.py <month> <year>")
        print("예: python download_final_incentive.py november 2025")
        sys.exit(1)

    month_name = sys.argv[1].lower()
    year = int(sys.argv[2])

    result = download_final_incentive(month_name, year)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
