#!/usr/bin/env python3
"""
이전 월 인센티브 파일 동기화 스크립트
Google Drive에서 이전 월 인센티브 파일을 다운로드
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

def get_previous_month(year, month):
    """이전 월 계산"""
    date = datetime(year, month, 1) - timedelta(days=1)
    return date.year, date.month

def get_korean_month(month):
    """월 번호를 한글로 변환"""
    months = {
        1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
        7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12"
    }
    return months.get(month, str(month))

def sync_previous_incentive(month_str, year):
    """
    이전 월 인센티브 파일 동기화
    
    Args:
        month_str: 월 이름 (예: 'august')
        year: 연도 (예: 2025)
    """
    # 월 이름을 숫자로 변환
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    current_month = month_map.get(month_str.lower())
    if not current_month:
        print(f"❌ 잘못된 월 이름: {month_str}")
        return False
    
    # 이전 월 계산
    prev_year, prev_month = get_previous_month(year, current_month)
    prev_month_kr = get_korean_month(prev_month)
    
    # 파일 경로 설정
    base_dir = Path(__file__).parent.parent
    target_file = base_dir / f"input_files/{prev_year}년 {prev_month_kr}월 인센티브 지급 세부 정보.csv"
    
    print(f"📥 {prev_year}년 {prev_month_kr}월 인센티브 파일 확인 중...")
    
    if target_file.exists():
        print(f"✅ 이미 존재: {target_file.name}")
        return True
    
    # Google Drive에서 다운로드 시도
    try:
        # google_drive_manager를 사용한 다운로드
        from google_drive_manager import GoogleDriveManager
        
        # config 파일 로드
        config_path = base_dir / 'config_files' / 'drive_config.json'
        manager = GoogleDriveManager(str(config_path))
        
        # 파일 패턴 설정
        drive_pattern = f"monthly_data/{prev_year}_{prev_month:02d}/{prev_year}년 {prev_month_kr}월 인센티브 지급 세부 정보.csv"
        
        print(f"🔍 Google Drive에서 검색: {drive_pattern}")
        
        # 실제 다운로드 실행
        success = manager.download_specific_file(drive_pattern, str(target_file))
        
        if success:
            print(f"✅ Google Drive에서 다운로드 성공!")
            return True
        else:
            print(f"❌ Google Drive 다운로드 실패")
            print(f"📂 수동으로 다운로드해주세요:")
            print(f"   Google Drive: {drive_pattern}")
            print(f"   저장 위치: {target_file}")
            return False
        
    except ImportError:
        print(f"⚠️ Google Drive Manager를 로드할 수 없습니다.")
        print(f"📂 수동으로 다운로드해주세요:")
        print(f"   Google Drive: monthly_data/{prev_year}_{prev_month:02d}/")
        print(f"   파일명: {prev_year}년 {prev_month_kr}월 인센티브 지급 세부 정보.csv")
        print(f"   저장 위치: {target_file}")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        month = sys.argv[1]
        year = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
        sync_previous_incentive(month, year)
    else:
        print("사용법: python sync_previous_incentive.py [month] [year]")
        print("예: python sync_previous_incentive.py august 2025")