#!/usr/bin/env python3
"""
출근 데이터 변환 스크립트
original 폴더의 attendance data를 converted 폴더로 변환
"""

import pandas as pd
import os
import sys
from pathlib import Path

def convert_attendance(month, year=2025):
    """
    출근 데이터를 변환하는 함수
    
    Args:
        month: 월 이름 (예: 'july', 'august')
        year: 연도 (기본값: 2025)
    
    Returns:
        bool: 성공 여부
    """
    try:
        # 경로 설정
        base_dir = Path(__file__).parent.parent
        original_file = base_dir / f"input_files/attendance/original/attendance data {month}.csv"
        converted_file = base_dir / f"input_files/attendance/converted/attendance data {month}_converted.csv"
        
        # converted 폴더 생성
        converted_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 원본 파일이 없으면 건너뛰기
        if not original_file.exists():
            print(f"⚠️ 원본 파일이 없습니다: {original_file}")
            return False
        
        # 변환된 파일이 있고 원본보다 최신이면 건너뛰기
        if converted_file.exists():
            original_mtime = original_file.stat().st_mtime
            converted_mtime = converted_file.stat().st_mtime

            if converted_mtime >= original_mtime:
                print(f"ℹ️ 변환된 파일이 최신입니다: {converted_file}")
                return True
            else:
                print(f"🔄 원본 파일이 업데이트되어 재변환합니다: {original_file}")
                # 기존 변환 파일 삭제
                converted_file.unlink()
        
        # CSV 파일 읽기
        df = pd.read_csv(original_file, encoding='utf-8-sig')
        
        # 간단한 변환 처리 (필요한 경우 여기에 변환 로직 추가)
        # 예: 컬럼명 정리, 데이터 타입 변환 등
        df.columns = df.columns.str.strip()
        
        # 변환된 파일 저장
        df.to_csv(converted_file, index=False, encoding='utf-8-sig')
        print(f"✅ 출근 데이터 변환 완료: {converted_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 출근 데이터 변환 실패: {e}")
        return False

def convert_all_attendance():
    """모든 월의 출근 데이터 변환"""
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december']
    
    for month in months:
        convert_attendance(month)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        month = sys.argv[1]
        convert_attendance(month)
    else:
        # 모든 월 변환
        convert_all_attendance()