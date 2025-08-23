#!/usr/bin/env python3
"""
Google Drive Permissions 진단 스크립트
Service Account 권한, 폴더 구조, 파일 접근성을 상세히 진단
"""

import os
import json
import logging
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveDiagnostic:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.service = None
        self.service_account_email = None
        
    def initialize_service(self):
        """Google Drive 서비스 초기화"""
        try:
            # Service Account 키 파일 확인
            key_files = [
                'credentials/service-account-key.json',
                'config_files/service-account-key.json',
                'service-account-key.json',
                'credentials.json'
            ]
            
            service_key_path = None
            for key_file in key_files:
                full_path = self.base_dir / key_file
                if full_path.exists():
                    service_key_path = str(full_path)
                    break
            
            if not service_key_path:
                print("❌ Service Account 키 파일을 찾을 수 없습니다.")
                print("   예상 위치:")
                for key_file in key_files:
                    print(f"   - {self.base_dir / key_file}")
                return False
            
            print(f"✅ Service Account 키 파일 발견: {service_key_path}")
            
            # 자격 증명 생성
            scopes = ['https://www.googleapis.com/auth/drive.readonly']
            credentials = Credentials.from_service_account_file(
                service_key_path, scopes=scopes
            )
            
            # Service Account 이메일 추출
            with open(service_key_path, 'r') as f:
                key_data = json.load(f)
                self.service_account_email = key_data.get('client_email', 'Unknown')
            
            self.service = build('drive', 'v3', credentials=credentials)
            print(f"✅ Google Drive API 연결 성공")
            print(f"📧 Service Account: {self.service_account_email}")
            return True
            
        except Exception as e:
            print(f"❌ Google Drive 서비스 초기화 실패: {e}")
            return False
    
    def test_root_access(self):
        """루트 폴더 접근 테스트"""
        print("\n" + "="*60)
        print("📁 루트 폴더 접근 테스트")
        print("="*60)
        
        try:
            # Config에서 root_folder_id 가져오기
            config_path = self.base_dir / 'config_files' / 'drive_config.json'
            with open(config_path, 'r') as f:
                config = json.load(f)
                root_folder_id = config['google_drive']['root_folder_id']
            
            print(f"🎯 대상 Root Folder ID: {root_folder_id}")
            
            # Root 폴더 정보 가져오기
            root_folder = self.service.files().get(
                fileId=root_folder_id,
                fields='id, name, owners, permissions'
            ).execute()
            
            print(f"✅ Root 폴더 접근 성공: {root_folder.get('name', 'Unknown')}")
            
            # 권한 정보 확인
            if 'owners' in root_folder:
                print("👤 소유자:")
                for owner in root_folder['owners']:
                    print(f"   - {owner.get('displayName', 'Unknown')} ({owner.get('emailAddress', 'Unknown')})")
            
            return True, root_folder_id
            
        except HttpError as e:
            print(f"❌ Root 폴더 접근 실패: {e}")
            return False, None
        except Exception as e:
            print(f"❌ 오류: {e}")
            return False, None
    
    def list_folder_contents(self, folder_id, folder_name="Folder"):
        """폴더 내용 나열"""
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields='files(id, name, mimeType, size, modifiedTime, owners)',
                pageSize=100
            ).execute()
            
            items = results.get('files', [])
            print(f"\n📂 {folder_name} 내용 ({len(items)}개 항목):")
            
            if not items:
                print("   (비어있음)")
                return []
            
            folders = []
            files = []
            
            for item in items:
                item_type = "📁" if item['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
                size = f" ({item.get('size', 'Unknown')} bytes)" if 'size' in item else ""
                modified = item.get('modifiedTime', 'Unknown')
                
                print(f"   {item_type} {item['name']}{size}")
                print(f"     ID: {item['id']}")
                print(f"     수정일: {modified}")
                
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folders.append(item)
                else:
                    files.append(item)
            
            return folders, files
            
        except HttpError as e:
            print(f"❌ 폴더 내용 조회 실패: {e}")
            return [], []
    
    def find_monthly_data_folder(self, root_folder_id):
        """monthly_data 폴더 찾기"""
        print("\n" + "="*60)
        print("📁 monthly_data 폴더 검색")
        print("="*60)
        
        folders, files = self.list_folder_contents(root_folder_id, "Root")
        
        monthly_data_folder = None
        for folder in folders:
            if folder['name'] == 'monthly_data':
                monthly_data_folder = folder
                print(f"✅ monthly_data 폴더 발견!")
                break
        
        if not monthly_data_folder:
            print("❌ monthly_data 폴더를 찾을 수 없습니다.")
            print("📋 사용 가능한 폴더:")
            for folder in folders:
                print(f"   - {folder['name']}")
            return None
        
        return monthly_data_folder['id']
    
    def check_month_folder(self, monthly_data_id, target_month="2025_07"):
        """특정 월 폴더 확인"""
        print(f"\n📅 {target_month} 폴더 검색")
        print("-" * 40)
        
        folders, files = self.list_folder_contents(monthly_data_id, "monthly_data")
        
        target_folder = None
        for folder in folders:
            if folder['name'] == target_month:
                target_folder = folder
                print(f"✅ {target_month} 폴더 발견!")
                break
        
        if not target_folder:
            print(f"❌ {target_month} 폴더를 찾을 수 없습니다.")
            print("📋 사용 가능한 월 폴더:")
            for folder in folders:
                print(f"   - {folder['name']}")
            return None
        
        return target_folder['id']
    
    def search_incentive_file(self, month_folder_id, target_filename="2025년 7월 인센티브 지급 세부 정보.csv"):
        """인센티브 파일 검색"""
        print(f"\n🔍 인센티브 파일 검색: {target_filename}")
        print("-" * 60)
        
        folders, files = self.list_folder_contents(month_folder_id, "2025_07")
        
        # 정확한 파일명 검색
        exact_match = None
        similar_files = []
        
        for file in files:
            if file['name'] == target_filename:
                exact_match = file
            elif '인센티브' in file['name'] or 'incentive' in file['name'].lower():
                similar_files.append(file)
        
        if exact_match:
            print(f"✅ 정확한 파일 발견!")
            print(f"   파일명: {exact_match['name']}")
            print(f"   파일ID: {exact_match['id']}")
            print(f"   크기: {exact_match.get('size', 'Unknown')} bytes")
            return exact_match['id']
        
        print(f"❌ 정확한 파일을 찾을 수 없습니다: {target_filename}")
        
        if similar_files:
            print("🔍 유사한 파일들:")
            for file in similar_files:
                print(f"   - {file['name']}")
                print(f"     ID: {file['id']}")
        else:
            print("   유사한 파일도 없습니다.")
        
        return None
    
    def test_file_access(self, file_id, filename):
        """파일 접근 권한 테스트"""
        print(f"\n🔐 파일 접근 권한 테스트: {filename}")
        print("-" * 50)
        
        try:
            # 파일 메타데이터 가져오기
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='id, name, size, mimeType, permissions, owners'
            ).execute()
            
            print(f"✅ 파일 메타데이터 접근 성공")
            print(f"   크기: {file_metadata.get('size', 'Unknown')} bytes")
            print(f"   타입: {file_metadata.get('mimeType', 'Unknown')}")
            
            # 다운로드 테스트 (첫 100바이트만)
            try:
                request = self.service.files().get_media(fileId=file_id)
                # 실제 다운로드는 하지 않고 요청만 테스트
                print("✅ 파일 다운로드 권한 확인됨")
                return True
            except HttpError as e:
                print(f"❌ 파일 다운로드 권한 없음: {e}")
                return False
                
        except HttpError as e:
            print(f"❌ 파일 접근 실패: {e}")
            return False
    
    def provide_sharing_instructions(self):
        """공유 설정 안내"""
        print("\n" + "="*60)
        print("🔧 Google Drive 공유 설정 안내")
        print("="*60)
        
        print(f"📧 Service Account 이메일: {self.service_account_email}")
        print()
        print("다음 폴더들을 Service Account와 공유해주세요:")
        print()
        print("1. 루트 폴더 (QIP 프로젝트 메인 폴더)")
        print("   - 공유 대상:", self.service_account_email)
        print("   - 권한: 뷰어 (Viewer)")
        print()
        print("2. monthly_data 폴더")
        print("   - 공유 대상:", self.service_account_email)
        print("   - 권한: 뷰어 (Viewer)")
        print()
        print("3. 각 월별 하위 폴더 (예: 2025_07, 2025_08)")
        print("   - 공유 대상:", self.service_account_email)
        print("   - 권한: 뷰어 (Viewer)")
        print()
        print("📋 공유 방법:")
        print("   1. Google Drive에서 폴더 우클릭")
        print("   2. '공유' 선택")
        print("   3. 위 이메일 주소 입력")
        print("   4. '뷰어' 권한 설정")
        print("   5. '보내기' 클릭")
    
    def run_full_diagnostic(self):
        """전체 진단 실행"""
        print("Google Drive 권한 및 구조 진단을 시작합니다...")
        print("=" * 80)
        
        # 1. 서비스 초기화
        if not self.initialize_service():
            return
        
        # 2. 루트 폴더 접근 테스트
        root_success, root_folder_id = self.test_root_access()
        if not root_success:
            print("\n❌ 루트 폴더에 접근할 수 없습니다.")
            self.provide_sharing_instructions()
            return
        
        # 3. monthly_data 폴더 찾기
        monthly_data_id = self.find_monthly_data_folder(root_folder_id)
        if not monthly_data_id:
            print("\n❌ monthly_data 폴더에 접근할 수 없습니다.")
            self.provide_sharing_instructions()
            return
        
        # 4. 2025_07 폴더 확인
        month_folder_id = self.check_month_folder(monthly_data_id, "2025_07")
        if not month_folder_id:
            print("\n❌ 2025_07 폴더가 없거나 접근할 수 없습니다.")
            print("   - 폴더가 실제로 존재하지 않을 수 있습니다.")
            print("   - 또는 공유 설정이 필요할 수 있습니다.")
            self.provide_sharing_instructions()
            return
        
        # 5. 인센티브 파일 검색
        incentive_file_id = self.search_incentive_file(
            month_folder_id, 
            "2025년 7월 인센티브 지급 세부 정보.csv"
        )
        
        if not incentive_file_id:
            print("\n❌ 2025년 7월 인센티브 파일이 존재하지 않습니다.")
            print("   결론: 파일이 실제로 Google Drive에 없는 것 같습니다.")
        else:
            # 6. 파일 접근 권한 테스트
            if self.test_file_access(incentive_file_id, "2025년 7월 인센티브 지급 세부 정보.csv"):
                print("\n✅ 모든 권한이 정상적으로 설정되어 있습니다!")
                print("   문제: 파일은 존재하고 접근 가능하지만 기존 코드에 버그가 있을 수 있습니다.")
            else:
                print("\n⚠️ 파일은 존재하지만 다운로드 권한이 없습니다.")
                self.provide_sharing_instructions()
        
        print("\n" + "="*80)
        print("진단 완료!")
        print("="*80)


if __name__ == "__main__":
    diagnostic = GoogleDriveDiagnostic()
    diagnostic.run_full_diagnostic()