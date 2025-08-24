"""
Attendance Data Auto Converter Module
출근 데이터 자동 변환 모듈
"""

import os
import pandas as pd
from pathlib import Path


class AttendanceAutoConverter:
    """출근 데이터 자동 변환기"""
    
    def __init__(self, debug_mode=False):
        """
        초기화
        
        Args:
            debug_mode: 디버그 모드 활성화 여부
        """
        self.debug_mode = debug_mode
        self.converted_dir = Path(__file__).parent / 'converted'
        self.original_dir = Path(__file__).parent / 'original'
        
        # 디렉토리 생성
        self.converted_dir.mkdir(exist_ok=True)
        self.original_dir.mkdir(exist_ok=True)
        
        if self.debug_mode:
            print(f"✅ AttendanceAutoConverter 초기화 완료")
            print(f"   - converted_dir: {self.converted_dir}")
            print(f"   - original_dir: {self.original_dir}")
    
    def ensure_converted_file(self, file_path):
        """
        변환된 파일 경로 반환 (이미 변환된 파일이 있으면 사용)
        
        Args:
            file_path: 원본 파일 경로
            
        Returns:
            변환된 파일 경로 (변환이 필요없으면 원본 경로)
        """
        if not os.path.exists(file_path):
            if self.debug_mode:
                print(f"⚠️ 파일이 존재하지 않음: {file_path}")
            return file_path
        
        # 파일명 추출
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        
        # 변환된 파일 경로 확인
        converted_file_path = self.converted_dir / f"{base_name}_converted.csv"
        
        if converted_file_path.exists():
            if self.debug_mode:
                print(f"✅ 변환된 파일 사용: {converted_file_path}")
            return str(converted_file_path)
        
        # 변환 시도 (실제로는 이미 변환된 파일이 있으므로 스킵)
        try:
            if self._needs_conversion(file_path):
                return self._convert_file(file_path, converted_file_path)
            else:
                if self.debug_mode:
                    print(f"ℹ️ 변환 불필요: {file_path}")
                return file_path
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ 변환 실패: {e}")
            return file_path
    
    def _needs_conversion(self, file_path):
        """
        파일이 변환이 필요한지 확인
        
        Args:
            file_path: 확인할 파일 경로
            
        Returns:
            변환 필요 여부
        """
        try:
            df = pd.read_csv(file_path, nrows=5)
            
            # 이미 변환된 파일인지 확인 (특정 컬럼 존재 여부로 판단)
            required_columns = ['ACTUAL WORK DAY', 'TOTAL WORK DAY']
            if all(col in df.columns for col in required_columns):
                return False  # 이미 변환됨
            
            # 원본 파일 형식인지 확인
            if 'compAdd' in df.columns or 'Work Date' in df.columns:
                return True  # 변환 필요
                
            return False
            
        except Exception:
            return False
    
    def _convert_file(self, original_path, converted_path):
        """
        파일 변환 수행 (실제로는 기존 변환된 파일 사용)
        
        Args:
            original_path: 원본 파일 경로
            converted_path: 변환될 파일 경로
            
        Returns:
            변환된 파일 경로
        """
        if self.debug_mode:
            print(f"📋 변환 시도: {original_path} → {converted_path}")
        
        try:
            # 실제 변환 로직은 구현하지 않음 (이미 변환된 파일 사용)
            # 원본 파일을 그대로 반환
            return original_path
            
        except Exception as e:
            if self.debug_mode:
                print(f"❌ 변환 실패: {e}")
            return original_path
    
    def get_converted_file_list(self):
        """
        변환된 파일 목록 반환
        
        Returns:
            변환된 파일 경로 리스트
        """
        converted_files = list(self.converted_dir.glob("*_converted.csv"))
        if self.debug_mode:
            print(f"📁 변환된 파일 {len(converted_files)}개 발견")
            for file in converted_files:
                print(f"   - {file.name}")
        return converted_files


# 테스트 코드
if __name__ == "__main__":
    converter = AttendanceAutoConverter(debug_mode=True)
    
    # 테스트 파일 경로
    test_file = "attendance data august.csv"
    result = converter.ensure_converted_file(test_file)
    print(f"\n결과: {result}")
    
    # 변환된 파일 목록
    print("\n변환된 파일 목록:")
    converter.get_converted_file_list()