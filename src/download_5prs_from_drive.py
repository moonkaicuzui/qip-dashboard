#!/usr/bin/env python3
"""
Google Drive에서 5PRS 데이터 파일 다운로드
월별 5PRS 데이터를 Google Drive에서 input_files/5prs 폴더로 다운로드
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Google Drive API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaIoBaseDownload
    import io
except ImportError:
    print("Google API 라이브러리가 필요합니다. 설치해주세요:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class DriveDownloader:
    """Google Drive에서 5PRS 데이터 다운로드"""
    
    def __init__(self):
        self.service = None
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.json'
        self.output_dir = Path('input_files/5prs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def authenticate(self) -> bool:
        """Google Drive 인증"""
        creds = None
        
        # 저장된 토큰 확인
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                logger.warning(f"토큰 파일 로드 실패: {e}")
        
        # 토큰이 없거나 유효하지 않으면 새로 인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"토큰 갱신 실패: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"인증 파일이 없습니다: {self.credentials_file}")
                    logger.info("Google Cloud Console에서 credentials.json을 다운로드하세요.")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"인증 실패: {e}")
                    return False
            
            # 토큰 저장
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.warning(f"토큰 저장 실패: {e}")
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("✅ Google Drive 인증 성공")
            return True
        except Exception as e:
            logger.error(f"서비스 생성 실패: {e}")
            return False
    
    def search_files(self, query: str) -> List[Dict]:
        """파일 검색"""
        try:
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, size)',
                pageSize=100
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"검색 결과: {len(files)}개 파일")
            return files
        except HttpError as e:
            logger.error(f"파일 검색 실패: {e}")
            return []
    
    def download_file(self, file_id: str, file_name: str, output_path: Path) -> bool:
        """파일 다운로드"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"다운로드 진행률: {int(status.progress() * 100)}%")
            
            # 파일 저장
            fh.seek(0)
            with open(output_path, 'wb') as f:
                f.write(fh.read())
            
            logger.info(f"✅ 다운로드 완료: {file_name} → {output_path}")
            return True
            
        except HttpError as e:
            logger.error(f"다운로드 실패: {e}")
            return False
    
    def download_monthly_5prs(self, month: str, year: int) -> bool:
        """월별 5PRS 데이터 다운로드"""
        
        # 전체 월 처리
        if month.lower() == 'all':
            logger.info(f"📅 {year}년 전체 월 데이터 다운로드 시작...")
            all_months = ['january', 'february', 'march', 'april', 'may', 'june',
                         'july', 'august', 'september', 'october', 'november', 'december']
            
            total_success = 0
            for m in all_months:
                logger.info(f"\n🔄 {m.capitalize()} 데이터 다운로드 중...")
                if self.download_single_month(m, year):
                    total_success += 1
            
            logger.info(f"\n✅ 전체 다운로드 완료: {total_success}/12개월")
            return total_success > 0
        else:
            # 개별 월 처리
            return self.download_single_month(month, year)
    
    def download_single_month(self, month: str, year: int) -> bool:
        """단일 월 데이터 다운로드"""
        
        # 파일명 패턴들
        patterns = [
            f"5prs data {month}",
            f"5PRS_{month}_{year}",
            f"qip_trainer_data_{year}_{self.get_month_number(month):02d}",
            f"basic manpower data {month}"
        ]
        
        downloaded_count = 0
        
        for pattern in patterns:
            # Google Drive에서 파일 검색
            query = f"name contains '{pattern}' and (mimeType='text/csv' or mimeType='application/vnd.ms-excel' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')"
            files = self.search_files(query)
            
            for file in files:
                file_name = file['name']
                file_id = file['id']
                
                # 확장자 추출
                ext = Path(file_name).suffix or '.csv'
                
                # 출력 파일명 생성
                output_file = self.output_dir / f"5prs_data_{year}_{self.get_month_number(month):02d}_{downloaded_count}{ext}"
                
                # 다운로드
                if self.download_file(file_id, file_name, output_file):
                    downloaded_count += 1
                    
                    # 표준 파일명으로도 복사
                    standard_name = self.output_dir / f"5prs data {month}{ext}"
                    if not standard_name.exists():
                        import shutil
                        shutil.copy2(output_file, standard_name)
                        logger.info(f"📁 표준 파일명으로 복사: {standard_name.name}")
        
        if downloaded_count > 0:
            logger.info(f"✅ 총 {downloaded_count}개 파일 다운로드 완료")
            return True
        else:
            logger.warning(f"⚠️ {month} {year} 데이터를 찾을 수 없습니다")
            return False
    
    def get_month_number(self, month: str) -> int:
        """월 이름을 숫자로 변환"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month.lower(), 0)
    
    def create_fallback_data(self, month: str, year: int):
        """폴백 데이터 생성"""
        logger.info("📝 폴백 데이터 생성 중...")
        
        # 샘플 CSV 데이터 생성
        import csv
        
        output_file = self.output_dir / f"5prs data {month}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 헤더
            writer.writerow([
                'Date', 'Inspector ID', 'TQC ID', 'Building', 'Line',
                'Product', 'Pass Qty', 'Reject Qty', 'Defect Type'
            ])
            
            # 샘플 데이터
            import random
            from datetime import datetime, timedelta
            
            base_date = datetime(year, self.get_month_number(month), 1)
            
            for day in range(30):
                date = base_date + timedelta(days=day)
                date_str = date.strftime('%m/%d/%Y')
                
                for _ in range(50):  # 하루 50개 검사 기록
                    inspector_id = f"INS{random.randint(1, 20):03d}"
                    tqc_id = f"TQC{random.randint(1, 50):03d}"
                    building = random.choice(['5PRS', '5PRE', '5PRW'])
                    line = f"Line {random.randint(1, 10)}"
                    product = f"Product {random.randint(100, 999)}"
                    
                    # 97% 합격률
                    if random.random() < 0.97:
                        pass_qty = random.randint(100, 500)
                        reject_qty = 0
                        defect_type = ''
                    else:
                        pass_qty = random.randint(80, 480)
                        reject_qty = random.randint(1, 20)
                        defect_type = random.choice(['Minor', 'Major', 'Critical'])
                    
                    writer.writerow([
                        date_str, inspector_id, tqc_id, building, line,
                        product, pass_qty, reject_qty, defect_type
                    ])
        
        logger.info(f"✅ 폴백 데이터 생성 완료: {output_file}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Google Drive에서 5PRS 데이터 다운로드')
    parser.add_argument('--month', type=str, required=True, help='월 (예: august)')
    parser.add_argument('--year', type=int, default=2025, help='년도')
    parser.add_argument('--fallback', action='store_true', help='폴백 데이터 생성')
    
    args = parser.parse_args()
    
    # 다운로더 초기화
    downloader = DriveDownloader()
    
    # Google Drive 인증 시도
    if downloader.authenticate():
        # 월별 데이터 다운로드
        success = downloader.download_monthly_5prs(args.month, args.year)
        
        if not success and args.fallback:
            # 실패 시 폴백 데이터 생성
            downloader.create_fallback_data(args.month, args.year)
    else:
        logger.warning("Google Drive 인증 실패 - 폴백 모드 사용")
        if args.fallback:
            downloader.create_fallback_data(args.month, args.year)
        else:
            logger.info("--fallback 옵션을 사용하여 샘플 데이터를 생성할 수 있습니다")
            sys.exit(1)


if __name__ == '__main__':
    main()