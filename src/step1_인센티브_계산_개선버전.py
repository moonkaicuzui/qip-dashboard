"""
[STEP 1] QIP 인센티브 계산 시스템 - Excel/CSV 생성
작성일: 2025-08-12
버전: 6.0

터미널 실행 명령어 예시 (2025년 7월 ~ 2026년 6월):

# 2025년
python src/step1_인센티브_계산_개선버전.py --config config_files/config_july_2025.json      # 7월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_august_2025.json    # 8월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_september_2025.json # 9월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_october_2025.json   # 10월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_november_2025.json  # 11월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_december_2025.json  # 12월

# 2026년
python src/step1_인센티브_계산_개선버전.py --config config_files/config_january_2026.json   # 1월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_february_2026.json  # 2월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_march_2026.json     # 3월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_april_2026.json     # 4월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_may_2026.json       # 5월
python src/step1_인센티브_계산_개선버전.py --config config_files/config_june_2026.json      # 6월

실행 순서:
1. step0_create_monthly_config.py - Config 생성 (완료)
2. 이 파일 실행 (step1) - Excel/CSV 계산 ← 현재 단계
3. step2_dashboard_version4.py - HTML 생성

주요 개선사항:
1. 월별 파라미터화 - 6월에 하드코딩된 값들을 설정 가능하게 변경
2. 설정 관리 시스템 추가
3. 데이터 검증 강화
4. 에러 처리 개선
5. 재사용성 향상
"""

import pandas as pd
import numpy as np
import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path
import warnings
import traceback
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

warnings.filterwarnings('ignore')


class Month(Enum):
    """월 열거형"""
    JANUARY = (1, "january", "jan", "1월")
    FEBRUARY = (2, "february", "feb", "2월")
    MARCH = (3, "march", "mar", "3월")
    APRIL = (4, "april", "apr", "4월")
    MAY = (5, "may", "may", "5월")
    JUNE = (6, "june", "jun", "6월")
    JULY = (7, "july", "jul", "7월")
    AUGUST = (8, "august", "aug", "8월")
    SEPTEMBER = (9, "september", "sep", "9월")
    OCTOBER = (10, "october", "oct", "10월")
    NOVEMBER = (11, "november", "nov", "11월")
    DECEMBER = (12, "december", "dec", "12월")
    
    def __init__(self, number, full_name, short_name, korean_name):
        self.number = number
        self.full_name = full_name
        self.short_name = short_name
        self.korean_name = korean_name
    
    @classmethod
    def from_number(cls, number: int):
        """월 번호로부터 Month 객체 반환"""
        for month in cls:
            if month.number == number:
                return month
        raise ValueError(f"Invalid month number: {number}")
    
    @classmethod
    def from_name(cls, name: str):
        """월 이름으로부터 Month 객체 반환"""
        name_lower = name.lower()
        for month in cls:
            if name_lower in [month.full_name, month.short_name] or name == month.korean_name:
                return month
        raise ValueError(f"Invalid month name: {name}")


@dataclass
class MonthConfig:
    """월별 설정 데이터 클래스"""
    year: int
    month: Month
    working_days: int  # 해당 월의 총 근무일 (주말/공휴일 제외)
    previous_months: List[Month]  # 연속 실패 체크를 위한 이전 월들
    file_paths: Dict[str, str]  # 필요한 파일 경로들
    output_prefix: str  # 출력 파일 접두사
    
    def get_month_str(self, format_type: str = "full") -> str:
        """월 문자열 반환"""
        if format_type == "full":
            return self.month.full_name
        elif format_type == "short":
            return self.month.short_name
        elif format_type == "korean":
            return self.month.korean_name
        elif format_type == "capital":
            return self.month.full_name.capitalize()
        return str(self.month.number)
    
    def get_file_path(self, file_type: str) -> str:
        """파일 타입별 경로 반환"""
        return self.file_paths.get(file_type, "")
    
    def to_dict(self) -> Dict:
        """설정을 딕셔너리로 변환"""
        return {
            "year": self.year,
            "month": self.month.full_name,
            "working_days": self.working_days,
            "previous_months": [m.full_name for m in self.previous_months],
            "file_paths": self.file_paths,
            "output_prefix": self.output_prefix
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """딕셔너리로부터 설정 생성"""
        return cls(
            year=data["year"],
            month=Month.from_name(data["month"]),
            working_days=data["working_days"],
            previous_months=[Month.from_name(m) for m in data["previous_months"]],
            file_paths=data["file_paths"],
            output_prefix=data["output_prefix"]
        )


class ConfigManager:
    """설정 관리 클래스"""
    
    @staticmethod
    def create_auto_config(attendance_file: str = None) -> MonthConfig:
        """attendance 파일에서 자동으로 월 감지하여 설정 생성"""
        import os
        import glob
        
        # attendance 파일 자동 찾기
        if not attendance_file:
            attendance_patterns = [
                "input_files/attendance data *.csv",
                "input_files/attendance_data_*.csv",
                "attendance*.csv"
            ]
            
            for pattern in attendance_patterns:
                files = glob.glob(pattern)
                if files:
                    # converted 파일은 제외하고 원본 파일 선택
                    original_files = [f for f in files if 'converted' not in f]
                    if original_files:
                        attendance_file = max(original_files, key=os.path.getmtime)
                    else:
                        attendance_file = max(files, key=os.path.getmtime)
                    print(f"✅ Attendance 파일 자동 감지: {attendance_file}")
                    break
            
            if not attendance_file:
                print("⚠️ Attendance 파일을 찾을 수 없습니다.")
                return None
        
        # attendance 파일에서 년월 감지
        year, month = detect_month_from_attendance(attendance_file)
        
        if not year or not month:
            print("⚠️ Attendance 파일에서 년월을 감지할 수 없습니다.")
            return None
        
        month_obj = Month.from_number(month)
        
        # 근무일 수 계산
        working_days = calculate_working_days_from_attendance(attendance_file, year, month)
        if not working_days:
            working_days = 23  # 기본값
            print(f"  → 기본 근무일 사용: {working_days}일")
        
        # 이전 2개월 자동 계산
        prev_month1_num = (month - 2) % 12 or 12
        prev_month2_num = (month - 1) % 12 or 12
        prev_month1 = Month.from_number(prev_month1_num)
        prev_month2 = Month.from_number(prev_month2_num)
        
        # 파일 자동 감지
        file_paths = ConfigManager.auto_detect_files(month_obj.full_name, prev_month2.korean_name, year)
        
        print(f"\n📊 자동 설정 생성 완료:")
        print(f"  - 년도: {year}")
        print(f"  - 월: {month_obj.korean_name} ({month_obj.full_name})")
        print(f"  - 근무일: {working_days}일")
        print(f"  - 이전 월: {prev_month1.korean_name}, {prev_month2.korean_name}")
        
        return MonthConfig(
            year=year,
            month=month_obj,
            working_days=working_days,
            previous_months=[prev_month1, prev_month2],
            file_paths=file_paths,
            output_prefix=f"output_QIP_incentive_{month_obj.full_name}_{year}"
        )
    
    @staticmethod
    def auto_detect_files(month_name: str, prev_month_korean: str, year: int) -> dict:
        """파일 자동 감지"""
        import os
        
        detected_files = {}
        
        # 파일 패턴 정의
        patterns = {
            "basic": [
                f"input_files/basic manpower data {month_name}.csv",
                f"input_files/basic_manpower_data_{month_name}.csv"
            ],
            "previous_incentive": [
                f"input_files/{year}년 {prev_month_korean} 인센티브 지급 세부 정보.csv",
                f"input_files/incentive_{prev_month_korean}_{year}.csv"
            ],
            "aql": [
                f"input_files/aql data {month_name}.csv",
                f"input_files/aql_data_{month_name}.csv"
            ],
            "5prs": [
                f"input_files/5prs data {month_name}.csv",
                f"input_files/5prs_data_{month_name}.csv"
            ],
            "attendance": [
                f"input_files/attendance data {month_name}_converted.csv",
                f"input_files/attendance data {month_name}.csv",
                f"input_files/attendance_data_{month_name}.csv"
            ]
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                if os.path.exists(pattern):
                    detected_files[key] = pattern
                    print(f"  ✓ {key}: {os.path.basename(pattern)}")
                    break
            
            if key not in detected_files:
                print(f"  ⚠️ {key}: 파일을 찾을 수 없음")
        
        return detected_files
    
    @staticmethod
    def create_july_config() -> MonthConfig:
        """7월 설정 생성"""
        return MonthConfig(
            year=2025,
            month=Month.JULY,
            working_days=23,  # 7월 근무일 (예시 - 실제 값으로 조정 필요)
            previous_months=[Month.MAY, Month.JUNE],  # 5월, 6월 데이터로 연속 실패 체크
            file_paths={
                "basic": "input_files/basic manpower data july.csv",
                "previous_incentive": "input_files/2025년 6월 인센티브 지급 세부 정보.csv",  # 6월 파일로 수정
                "aql": "input_files/AQL history/1.HSRG AQL REPORT-JULY.2025.csv",  # AQL history 사용
                "5prs": "input_files/5prs data july.csv",
                "attendance": "input_files/attendance/converted/attendance data july_converted.csv"  # 변환된 파일 사용
            },
            output_prefix="output_QIP_incentive_july_2025"
        )
    
    @staticmethod
    def create_june_config() -> MonthConfig:
        """6월 설정 생성 (기존 코드 호환)"""
        return MonthConfig(
            year=2025,
            month=Month.JUNE,
            working_days=22,
            previous_months=[Month.APRIL, Month.MAY],
            file_paths={
                "basic": "input_files/basic manpower data june.csv",
                "previous_incentive": "input_files/may qip incentive data.csv",
                "aql": "input_files/aql data june.csv",
                "5prs": "input_files/5prs data june.csv",
                "attendance": "input_files/attendance/converted/attendance data june_converted.csv"
            },
            output_prefix="output_QIP_incentive_june_2025"
        )
    
    @staticmethod
    def save_config(config: MonthConfig, filepath: str = None):
        """설정을 JSON 파일로 저장"""
        if filepath is None:
            filepath = f"config_{config.month.full_name}_{config.year}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"✅ 설정 저장 완료: {filepath}")
    
    @staticmethod
    def load_config(filepath: str) -> MonthConfig:
        """JSON 파일에서 설정 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 설정 로드 완료: {filepath}")
        return MonthConfig.from_dict(data)


class SpecialCaseHandler:
    """특별 케이스 처리 핸들러 (개선된 버전)"""
    
    def __init__(self, config: MonthConfig):
        self.config = config
        self.special_positions = [
            'AQL INSPECTOR',
            'MODEL MASTER',
            'AUDIT',
            'TRAINING'
        ]
    
    def handle_aql_inspector_manual_input(self, employee_data: Dict) -> float:
        """AQL Inspector 수동 입력 처리"""
        name = employee_data.get('Full Name', 'Unknown')
        emp_id = employee_data.get('Employee No', 'Unknown')
        position = employee_data.get('QIP POSITION 1ST  NAME', '')
        
        print(f"\n{'='*60}")
        print(f"특별 케이스: AQL INSPECTOR")
        print(f"직원명: {name}")
        print(f"직원번호: {emp_id}")
        print(f"포지션: {position}")
        
        try:
            incentive = self._get_manual_input(name)
            print(f"✅ 입력된 인센티브: {incentive:,.0f} VND")
            return incentive
        except Exception as e:
            print(f"❌ 입력 오류: {e}")
            return 0
    
    def handle_model_master_manual_input(self, employee_data: Dict) -> float:
        """Model Master 수동 입력 처리"""
        name = employee_data.get('Full Name', 'Unknown')
        emp_id = employee_data.get('Employee No', 'Unknown')
        position = employee_data.get('QIP POSITION 1ST  NAME', '')
        
        print(f"\n{'='*60}")
        print(f"특별 케이스: MODEL MASTER")
        print(f"직원명: {name}")
        print(f"직원번호: {emp_id}")
        print(f"포지션: {position}")
        
        try:
            incentive = self._get_manual_input(name)
            print(f"✅ 입력된 인센티브: {incentive:,.0f} VND")
            return incentive
        except Exception as e:
            print(f"❌ 입력 오류: {e}")
            return 0
    
    def handle_audit_training_manual_input(self, employee_data: Dict) -> float:
        """Audit/Training 수동 입력 처리"""
        name = employee_data.get('Full Name', 'Unknown')
        emp_id = employee_data.get('Employee No', 'Unknown')
        position = employee_data.get('QIP POSITION 1ST  NAME', '')
        
        print(f"\n{'='*60}")
        print(f"특별 케이스: AUDIT/TRAINING")
        print(f"직원명: {name}")
        print(f"직원번호: {emp_id}")
        print(f"포지션: {position}")
        
        try:
            incentive = self._get_manual_input(name)
            print(f"✅ 입력된 인센티브: {incentive:,.0f} VND")
            return incentive
        except Exception as e:
            print(f"❌ 입력 오류: {e}")
            return 0
    
    def _get_manual_input(self, name: str) -> float:
        """수동 입력 받기"""
        while True:
            try:
                month_str = self.config.get_month_str("korean")
                user_input = input(f"\n{name}의 {month_str} 인센티브 금액 입력 (VND): ")
                if not user_input.strip():
                    if input("입력 없음. 0으로 처리? (y/n): ").lower() == 'y':
                        return 0
                    continue
                
                # 쉼표 제거 후 숫자 변환
                amount = float(user_input.replace(',', '').strip())
                if amount < 0:
                    print("❌ 음수는 입력할 수 없습니다.")
                    continue
                    
                return amount
            except ValueError:
                print("❌ 올바른 숫자를 입력해주세요.")
                continue


class DataProcessor:
    """데이터 처리 클래스 (개선된 버전)"""
    
    def __init__(self, config: MonthConfig):
        self.config = config
        self.column_cache = {}
    
    def standardize_employee_id(self, emp_id: Any) -> str:
        """직원 ID 표준화"""
        if pd.isna(emp_id):
            return ""
        
        emp_str = str(emp_id).strip()
        
        # 소수점 제거
        if '.' in emp_str:
            emp_str = emp_str.split('.')[0]
        
        # 쉼표 제거
        emp_str = emp_str.replace(',', '')
        
        # 공백 제거
        emp_str = emp_str.replace(' ', '')
        
        # 대시 제거
        emp_str = emp_str.replace('-', '')
        
        return emp_str
    
    def detect_column_names(self, df: pd.DataFrame, target_patterns: List[str]) -> Optional[str]:
        """칼럼명 자동 감지 (개선된 버전)"""
        cache_key = f"{id(df)}_{','.join(target_patterns)}"
        if cache_key in self.column_cache:
            return self.column_cache[cache_key]
        
        df_columns = df.columns.tolist()
        
        # 정확한 매칭 우선
        for pattern in target_patterns:
            if pattern in df_columns:
                self.column_cache[cache_key] = pattern
                return pattern
        
        # 대소문자 무시 매칭
        for col in df_columns:
            col_upper = col.upper()
            for pattern in target_patterns:
                if pattern.upper() == col_upper:
                    self.column_cache[cache_key] = col
                    return col
        
        # 부분 매칭
        for col in df_columns:
            col_clean = re.sub(r'[^a-zA-Z0-9]', '', col.upper())
            for pattern in target_patterns:
                pattern_clean = re.sub(r'[^a-zA-Z0-9]', '', pattern.upper())
                if pattern_clean in col_clean or col_clean in pattern_clean:
                    self.column_cache[cache_key] = col
                    return col
        
        return None
    
    def process_attendance_conditions(self, att_df: pd.DataFrame) -> pd.DataFrame:
        """출석 조건 처리 (개선된 버전)"""
        print("\n📊 출석 조건 처리 중...")
        
        # 직원 ID 칼럼 찾기 (ID No를 우선으로)
        emp_col = self.detect_column_names(att_df, [
            'ID No', 'Employee No', 'EMPLOYEE NO', 'EMPLOYEE_NO', 'EMP_NO', 
            'EMPLOYEE ID', 'EMPLOYEE_ID', 'ID',
            'WORKER ID', 'STAFF ID'
        ])
        
        if not emp_col:
            print("❌ 직원 ID 칼럼을 찾을 수 없습니다.")
            return pd.DataFrame()
        
        # Stop working 직원 목록 가져오기 (month_data에서)
        stop_working_employees = set()
        if hasattr(self, 'month_data') and 'Stop working Date' in self.month_data.columns:
            stop_working_mask = self.month_data['Stop working Date'].notna() & (self.month_data['Stop working Date'] != '')
            stop_working_employees = set(self.month_data[stop_working_mask]['Employee No'].astype(str))
            print(f"  → Stop working 직원 {len(stop_working_employees)}명 제외 처리")
        
        # 변환된 파일 형식 체크
        if 'ACTUAL WORK DAY' in att_df.columns and 'TOTAL WORK DAY' in att_df.columns:
            # 이미 변환된 파일
            print("✅ 변환된 출석 파일 감지")
            attendance_results = []
            
            for idx, row in att_df.iterrows():
                emp_id = self.standardize_employee_id(row[emp_col])
                if not emp_id or emp_id == '0':
                    continue
                
                # Stop working 직원도 정상 처리 (제외하지 않음)
                
                actual_days = float(row.get('ACTUAL WORK DAY', 0))
                total_days = float(row.get('TOTAL WORK DAY', 27))  # 기본값을 27로 변경
                
                # 새로운 칼럼 처리
                ar1_absences = float(row.get('AR1 Absences', 0))
                unapproved_absences = float(row.get('Unapproved Absences', 0))
                absence_rate = float(row.get('Absence Rate (%)', 0))
                
                # 이전 형식과의 호환성을 위해
                if 'Absence (without permission) time' in row:
                    unapproved_absences = float(row.get('Absence (without permission) time', 0))
                if 'Absence (without permission) Ratio (%)' in row:
                    absence_rate = float(row.get('Absence (without permission) Ratio (%)', 0))
                
                # 실제 근무일이 전체 근무일보다 많은 경우 조정
                if actual_days > total_days:
                    actual_days = total_days
                    absence_rate = 0  # 전체 근무일 이상 근무한 경우 결근율 0
                
                # 음수 결근율은 0으로 처리
                if absence_rate < 0:
                    absence_rate = 0
                
                # 조건 체크 (AR1 무단결근 사용)
                cond1_fail = actual_days <= 0
                cond2_fail = ar1_absences > 2  # AR1 무단결근이 2일 초과
                cond3_fail = absence_rate > 12  # 결근율 12% 초과
                cond4_fail = actual_days < 12  # 최소 근무일 12일 미만 (신규 조건)
                
                attendance_results.append({
                    'Employee No': emp_id,
                    'Total Working Days': total_days,
                    'Actual Working Days': actual_days,
                    'AR1 Absences': ar1_absences,
                    'Unapproved Absences': unapproved_absences,
                    'Absence Rate (raw)': absence_rate,
                    'attendancy condition 1 - acctual working days is zero': 'yes' if cond1_fail else 'no',
                    'attendancy condition 2 - unapproved Absence Day is more than 2 days': 'yes' if cond2_fail else 'no',
                    'attendancy condition 3 - absent % is over 12%': 'yes' if cond3_fail else 'no',
                    'attendancy condition 4 - minimum working days': 'yes' if cond4_fail else 'no'
                })
            
            result_df = pd.DataFrame(attendance_results)
            print(f"✅ 출석 조건 처리 완료: {len(result_df)} 명")
            return result_df
        
        # 원본 일별 데이터 처리 (기존 코드)
        # Work Date 컬럼 포함하여 날짜 컬럼 찾기
        date_columns = []
        
        # 먼저 명시적인 날짜 컬럼명 확인
        known_date_cols = ['Work Date', 'WorkDate', 'Date', '날짜', '일자']
        for col in att_df.columns:
            if col in known_date_cols:
                date_columns.append(col)
        
        # 없으면 패턴으로 찾기
        if not date_columns:
            date_patterns = [r'\d{1,2}[-/]\d{1,2}', r'\d{4}[-/]\d{2}[-/]\d{2}']
            for col in att_df.columns:
                for pattern in date_patterns:
                    if re.search(pattern, str(col)):
                        date_columns.append(col)
                        break
        
        if not date_columns:
            print("❌ 날짜 칼럼을 찾을 수 없습니다.")
            return pd.DataFrame()
        
        attendance_results = []
        
        # 직원별 처리
        for emp_id in att_df[emp_col].unique():
            if pd.isna(emp_id):
                continue
            
            emp_id = self.standardize_employee_id(emp_id)
            if not emp_id:
                continue
            
            # Stop working 직원도 정상 처리 (제외하지 않음)
            
            total_working_days = self.config.working_days
            actual_working_days = 0
            unapproved_absence = 0
            
            # 타입 호환성을 위해 출석 데이터의 ID도 문자열로 변환하여 매칭
            emp_data = att_df[att_df[emp_col].astype(str).str.zfill(9) == emp_id]
            
            # 방어적 코딩: 출석 데이터가 없는 직원 처리
            if emp_data.empty:
                print(f"⚠️ 출석 데이터 없음: {emp_id}")
                # 출석 데이터 없는 직원은 0일로 처리하고 다음 직원으로
                continue
            
            # 실제 출석 데이터에서 출근/결근 계산 (각 행이 하루씩)
            if 'compAdd' in emp_data.columns:
                for idx, row in emp_data.iterrows():
                    comp_add = row['compAdd']
                    if pd.notna(comp_add):
                        comp_str = str(comp_add).strip()
                        
                        # 출근 체크 ('Đi làm' = 출근)
                        if comp_str == 'Đi làm':
                            actual_working_days += 1
                        # 무단결근 체크 (필요 시 다른 패턴 추가)
                        elif '무단' in comp_str or 'UNAPP' in comp_str.upper():
                            unapproved_absence += 1
            
            # 실제 근무일이 전체 근무일보다 많은 경우 조정
            if actual_working_days > total_working_days:
                actual_working_days = total_working_days
            
            # 결근율 계산
            if total_working_days > 0:
                absence_rate = ((total_working_days - actual_working_days) / total_working_days) * 100
            else:
                absence_rate = 0
            
            # 음수 결근율은 0으로 처리
            if absence_rate < 0:
                absence_rate = 0
            
            attendance_results.append({
                'Employee No': emp_id,
                'Total Working Days': total_working_days,
                'Actual Working Days': actual_working_days,
                'Unapproved Absence Days': unapproved_absence,
                'Absence Rate (raw)': round(absence_rate, 2),
                'attendancy condition 1 - acctual working days is zero': 'yes' if actual_working_days == 0 else 'no',
                'attendancy condition 2 - unapproved Absence Day is more than 2 days': 'yes' if unapproved_absence > 2 else 'no',
                'attendancy condition 3 - absent % is over 12%': 'yes' if absence_rate > 12 else 'no',
                'attendancy condition 4 - minimum working days': 'yes' if actual_working_days < 12 else 'no'
            })
        
        result_df = pd.DataFrame(attendance_results)
        print(f"✅ 출석 조건 처리 완료: {len(result_df)} 명")
        return result_df
    
    def process_5pairs_conditions(self, prs_df: pd.DataFrame) -> pd.DataFrame:
        """5PRS 조건 처리 - TQC ID (검사 대상자) 기준"""
        print("\n📊 5PRS 조건 처리 중...")
        
        # TQC ID는 검사 대상자 (Assembly Inspector 등)
        # Inspector ID는 검사 수행자 (Auditor/Trainer)
        
        # TQC ID 칼럼 찾기 (검사 대상자)
        tqc_col = self.detect_column_names(prs_df, [
            'TQC ID', 'TQC_ID', 'TQC', 'Target ID'
        ])
        
        if not tqc_col:
            print("⚠️ TQC ID 칼럼을 찾을 수 없습니다. Inspector ID로 대체 시도...")
            # Fallback: Inspector ID 사용 (이전 버전 호환)
            tqc_col = self.detect_column_names(prs_df, [
                'Inspector ID', 'INSPECTOR_ID', 'Inspector'
            ])
            if not tqc_col:
                print("❌ 직원 ID 칼럼을 찾을 수 없습니다.")
                return pd.DataFrame()
        
        # 검사량과 통과량 칼럼 찾기
        val_qty_col = self.detect_column_names(prs_df, [
            'Valiation Qty', 'Validation Qty', 'Val Qty',
            'Total Valiation Qty', 'Total Validation Qty'
        ])
        
        pass_qty_col = self.detect_column_names(prs_df, [
            'Pass Qty', 'Passed Qty', 'Pass',
            'Total Pass Qty', 'PASS QTY'
        ])
        
        # TQC별 집계가 필요한지 확인
        if val_qty_col and pass_qty_col:
            # TQC별로 그룹화하여 합계 계산
            print(f"  - TQC ID 기준으로 집계 중... (칼럼: {tqc_col})")
            grouped = prs_df.groupby(tqc_col).agg({
                val_qty_col: 'sum',
                pass_qty_col: 'sum'
            }).reset_index()
            
            grouped.columns = [tqc_col, 'Total Valiation Qty', 'Total Pass Qty']
        else:
            # 이미 집계된 데이터인 경우
            grouped = prs_df.copy()
            
            # 칼럼명 표준화
            total_qty_col = self.detect_column_names(grouped, [
                'Total Valiation Qty', 'Total Validation Qty',
                'TOTAL QTY', 'TOTAL_QTY', 'Total Qty'
            ])
            
            pass_qty_col = self.detect_column_names(grouped, [
                'Total Pass Qty', 'PASS QTY', 'PASS_QTY',
                'Pass Qty', 'Passed Qty'
            ])
            
            if total_qty_col:
                grouped['Total Valiation Qty'] = grouped[total_qty_col]
            if pass_qty_col:
                grouped['Total Pass Qty'] = grouped[pass_qty_col]
        
        prs_results = []
        
        for _, row in grouped.iterrows():
            emp_id = self.standardize_employee_id(row.get(tqc_col))
            if not emp_id or emp_id == '0' or emp_id == '000000000':
                continue
            
            total_qty = float(row.get('Total Valiation Qty', 0))
            pass_qty = float(row.get('Total Pass Qty', 0))
            pass_rate = 0
            
            if total_qty > 0:
                pass_rate = (pass_qty / total_qty) * 100
            
            # 조건 체크 - 5PRS는 검사량 100개 이상 AND 통과율 95% 이상 필요
            condition1 = 'yes' if (total_qty >= 100 and pass_rate >= 95) else 'no'
            condition2 = 'yes' if total_qty == 0 else 'no'
            
            prs_results.append({
                'Employee No': emp_id,
                'Total Valiation Qty': total_qty,
                'Total Pass Qty': pass_qty,
                'Pass %': round(pass_rate, 2),
                '5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%': condition1,
                '5prs condition 2 - Total Valiation Qty is zero': condition2
            })
        
        result_df = pd.DataFrame(prs_results)
        print(f"✅ 5PRS 조건 처리 완료: {len(result_df)} 명 (TQC 기준)")
        return result_df
    
    def get_months_from_incentive_amount(self, amount: float) -> int:
        """인센티브 금액으로 연속 개월 수 역산"""
        incentive_map = {
            150000: 1,
            250000: 2,
            300000: 3,
            350000: 4,
            400000: 5,
            450000: 6,
            500000: 7,
            650000: 8,
            750000: 9,
            850000: 10,
            950000: 11,
            1000000: 12
        }
        
        # 정확한 매칭 찾기
        for incentive_amount, months in incentive_map.items():
            if abs(amount - incentive_amount) < 1:  # 부동소수점 비교
                return months
        
        # 1,000,000 이상이면 12개월 이상으로 간주
        if amount >= 1000000:
            return 12
        
        return 0  # 매칭 없으면 0
    
    def calculate_continuous_months_from_history(self, emp_id: str) -> int:
        """연속 인센티브 수령 개월 수 계산 (이전 월 인센티브 파일 기반)"""
        continuous_months = 0
        
        # 먼저 직전 월(i=1)의 인센티브 금액으로 연속 개월 수 추정
        for i in range(1, 2):  # 직전 월만 확인
            month_num = (self.config.month.number - i) % 12 or 12
            year = self.config.year if month_num < self.config.month.number else self.config.year - 1
            month_obj = Month.from_number(month_num)
            
            # 이전 월 인센티브 파일 찾기 - 여러 위치 확인
            file_patterns = [
                f"{year}년 {month_num}월 인센티브 지급 세부 정보.csv",
                f"input_files/{year}년 {month_num}월 인센티브 지급 세부 정보.csv",
                f"{year}_{month_num:02d}_incentive_details.csv",
                f"input_files/{year}_{month_num:02d}_incentive_details.csv",
                f"incentive_{year}_{month_obj.full_name}.csv",
                f"input_files/incentive_{year}_{month_obj.full_name}.csv",
                f"output_QIP_incentive_{month_obj.full_name}_{year}_최종완성버전_v6.0_Complete.csv",
                f"output_files/output_QIP_incentive_{month_obj.full_name}_{year}_최종완성버전_v6.0_Complete.csv"
            ]
            
            file_found = False
            file_pattern = None
            for pattern in file_patterns:
                if os.path.exists(pattern):
                    file_pattern = pattern
                    file_found = True
                    break
            
            if not file_found:
                # 파일이 없으면 연속성 끊김 (0개월)
                return 0
            
            try:
                # 파일 읽기
                prev_month_df = pd.read_csv(file_pattern, encoding='utf-8-sig')
                
                # 직원 ID 표준화
                if 'Employee No' in prev_month_df.columns:
                    prev_month_df['Employee No'] = prev_month_df['Employee No'].apply(
                        self.standardize_employee_id
                    )
                
                # 해당 직원의 인센티브 확인
                emp_data = prev_month_df[prev_month_df['Employee No'] == emp_id]
                
                if not emp_data.empty:
                    # Final Incentive amount 칼럼 확인
                    incentive_col = 'Final Incentive amount'
                    if incentive_col not in emp_data.columns:
                        # 대체 칼럼명 시도
                        for col in emp_data.columns:
                            if 'incentive' in col.lower() and month_obj.full_name.lower() in col.lower():
                                incentive_col = col
                                break
                    
                    if incentive_col in emp_data.columns:
                        incentive_amount = emp_data.iloc[0].get(incentive_col, 0)
                        if pd.notna(incentive_amount) and float(incentive_amount) > 0:
                            # 인센티브 금액으로 연속 개월 수 역산
                            prev_months = self.get_months_from_incentive_amount(float(incentive_amount))
                            if prev_months > 0:
                                # 이전 월에 받았으면 +1
                                continuous_months = prev_months + 1
                            else:
                                # 금액을 인식할 수 없으면 1개월로 시작
                                continuous_months = 1
                        else:
                            # 인센티브 0이면 연속성 끊김 (0개월)
                            return 0
                    else:
                        return 0
                else:
                    # 직원 데이터 없으면 연속성 끊김 (0개월)
                    return 0
            
            except Exception as e:
                print(f"  ⚠️ {month_num}월 데이터 읽기 실패: {e}")
                return 0
        
        return continuous_months
    
    def process_aql_conditions_with_history(self, aql_df: pd.DataFrame = None) -> pd.DataFrame:
        """AQL history 파일을 활용한 3개월 연속 실패 체크"""
        print("\n📊 AQL History 파일 기반 3개월 연속 실패 체크...")
        
        import tempfile
        import os
        import glob
        import re
        
        def load_aql_history(month_name):
            """AQL history 파일 로드 (헤더 처리 포함)"""
            file_path = f'input_files/AQL history/1.HSRG AQL REPORT-{month_name}.2025.csv'
            
            if not os.path.exists(file_path):
                return None
            
            try:
                # 파일을 텍스트로 먼저 읽어서 헤더 처리
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                
                # 임시 파일에 정리된 데이터 쓰기
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
                    # 표준 헤더 작성
                    tmp.write('MONTH,DATE,MODEL,PO NO 1.,Item,PO NO 2.,DEST,QTY,PO TYPE,REPACKING PO,')
                    tmp.write('REPACKING,RESULT,PARTIAL QTY,PARTIAL NO,BUILDING,LINE,TQC NUM,EMPLOYEE NO,')
                    tmp.write('QTY INSPECTION,OFFICIAL INSPECTOR,INSPECTOR TYPE,DESCRIPTION,REMARKS,')
                    tmp.write('INTERNAL INSPECTOR,Stitching issue,Wrong Packing issue(prs),NOTE\n')
                    
                    # 데이터 라인들 쓰기 (3번째 줄부터)
                    for line in lines[2:]:
                        tmp.write(line)
                    tmp_path = tmp.name
                
                # 임시 파일에서 데이터 읽기
                df = pd.read_csv(tmp_path)
                os.unlink(tmp_path)  # 임시 파일 삭제
                
                return df
                
            except Exception as e:
                return None
        
        def get_latest_three_months():
            """최신 3개월 자동 선택 (파일명과 MONTH 컬럼 검증)"""
            print("\n  🔍 AQL history 파일 스캔 중...")
            
            # AQL history 폴더의 모든 CSV 파일 찾기
            files = glob.glob('input_files/AQL history/*.csv')
            
            month_map = {
                1: 'JANUARY', 2: 'FEBRUARY', 3: 'MARCH', 4: 'APRIL',
                5: 'MAY', 6: 'JUNE', 7: 'JULY', 8: 'AUGUST',
                9: 'SEPTEMBER', 10: 'OCTOBER', 11: 'NOVEMBER', 12: 'DECEMBER'
            }
            
            valid_months = {}
            
            for file_path in files:
                # 파일명에서 월 추출 (예: "1.HSRG AQL REPORT-JULY.2025.csv" → "JULY")
                match = re.search(r'AQL REPORT-([A-Z]+)\.', os.path.basename(file_path))
                if match:
                    filename_month = match.group(1)
                    
                    # 파일 로드
                    df = load_aql_history(filename_month)
                    if df is not None and not df.empty:
                        # MONTH 컬럼의 첫 번째 값 확인
                        month_value = df['MONTH'].iloc[0]
                        
                        # 숫자를 월 이름으로 변환
                        if pd.notna(month_value):
                            month_num = int(month_value)
                            month_name = month_map.get(month_num, '')
                            
                            # 파일명과 MONTH 컬럼 값이 일치하는지 검증
                            if filename_month.upper() == month_name.upper():
                                valid_months[month_num] = filename_month
                                print(f"    ✅ {filename_month}: 검증 통과 (MONTH={month_num})")
                            else:
                                print(f"    ⚠️ {filename_month}: 불일치 - 파일명={filename_month}, MONTH 컬럼={month_name}")
            
            if not valid_months:
                print("    ❌ 유효한 AQL history 파일이 없습니다.")
                return None
            
            # 최신 3개월 선택
            sorted_months = sorted(valid_months.keys(), reverse=True)[:3]
            latest_three = [valid_months[m] for m in sorted(sorted_months)]
            
            print(f"    📅 최신 3개월 선택: {latest_three}")
            return latest_three
        
        # 1. 최신 3개월 자동 선택
        latest_months = get_latest_three_months()
        
        if not latest_months or len(latest_months) < 3:
            # 폴백: 하드코딩된 월 사용
            print("  ⚠️ 자동 선택 실패, 기본값 사용 (MAY, JUNE, JULY)")
            latest_months = ['MAY', 'JUNE', 'JULY']
        
        # 2. 3개월 AQL history 파일 로드
        month_dfs = {}
        for month_name in latest_months:
            df = load_aql_history(month_name)
            if df is not None:
                month_dfs[month_name] = df
                # 빈 행 제거한 실제 데이터 건수 표시
                valid_rows = df.dropna(how='all')
                print(f"  ✅ {month_name} AQL history 로드: {len(valid_rows)}건")
            else:
                print(f"  ⚠️ {month_name} AQL history 파일 로드 실패")
        
        # 3개월 모두 로드되었는지 확인
        if len(month_dfs) < 3:
            print("  ❌ 필요한 AQL history 파일을 모두 로드할 수 없습니다. 기존 방식으로 처리합니다.")
            return self.process_aql_conditions(aql_df)
        
        # 월별 DataFrame 할당 (latest_months 순서대로)
        month1_df = month_dfs[latest_months[0]]
        month2_df = month_dfs[latest_months[1]]
        month3_df = month_dfs[latest_months[2]]
        
        # 2. 각 월의 실패자 추출
        def get_failures(df, month_name):
            """각 월의 실패 직원과 건수 추출"""
            failures = {}
            
            # EMPLOYEE NO가 유효한 데이터만 필터링
            valid_df = df[df['EMPLOYEE NO'].notna()].copy()
            valid_df['EMPLOYEE NO'] = valid_df['EMPLOYEE NO'].astype(str).str.strip()
            
            # 직원별 실패 건수 계산
            for emp_id_raw in valid_df['EMPLOYEE NO'].unique():
                if emp_id_raw == 'nan' or len(emp_id_raw) < 3:
                    continue
                
                # 9자리로 패딩
                emp_id = emp_id_raw.split('.')[0].zfill(9)  # float 형식 처리
                
                # 원본 ID로 검색
                emp_data = valid_df[valid_df['EMPLOYEE NO'].astype(str).str.strip() == emp_id_raw]
                fail_count = len(emp_data[emp_data['RESULT'].str.upper() == 'FAIL'])
                
                if fail_count > 0:
                    failures[emp_id] = fail_count
            
            print(f"  → {month_name}: {len(failures)}명 실패")
            return failures
        
        # 각 월의 실패자 추출
        month1_failures = get_failures(month1_df, latest_months[0])
        month2_failures = get_failures(month2_df, latest_months[1])
        month3_failures = get_failures(month3_df, latest_months[2])
        
        # 3. 3개월 연속 실패자 찾기
        continuous_fail_employees = set()
        
        # 모든 직원 ID 수집
        all_employees = set(month1_failures.keys()) | set(month2_failures.keys()) | set(month3_failures.keys())
        
        for emp_id in all_employees:
            month1_fail = month1_failures.get(emp_id, 0) > 0
            month2_fail = month2_failures.get(emp_id, 0) > 0
            month3_fail = month3_failures.get(emp_id, 0) > 0
            
            if month1_fail and month2_fail and month3_fail:
                continuous_fail_employees.add(emp_id)
                print(f"    ✅ {emp_id}: 3개월 연속 실패 ({latest_months[0]}:{month1_failures.get(emp_id)}건, {latest_months[1]}:{month2_failures.get(emp_id)}건, {latest_months[2]}:{month3_failures.get(emp_id)}건)")
        
        print(f"\n  📊 3개월 연속 실패자: {len(continuous_fail_employees)}명")
        
        # 4. 결과 DataFrame 생성 (BUILDING 정보 포함)
        aql_results = []
        current_month_fail_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # 최신 월(3번째 월) 데이터에서 BUILDING 정보 추출
        employee_buildings = {}
        if 'BUILDING' in month3_df.columns:
            for _, row in month3_df.iterrows():
                emp_no = str(row['EMPLOYEE NO']).strip()
                if emp_no and emp_no != 'nan':
                    if '.' in emp_no:
                        emp_no = str(int(float(emp_no)))
                    emp_no = emp_no.zfill(9)
                    if emp_no not in employee_buildings:
                        employee_buildings[emp_no] = row['BUILDING']
        
        # 이전 월에서도 BUILDING 정보 수집 (최신 월에 없는 경우 대비)
        for month_df in [month2_df, month1_df]:
            if 'BUILDING' in month_df.columns:
                for _, row in month_df.iterrows():
                    emp_no = str(row['EMPLOYEE NO']).strip()
                    if emp_no and emp_no != 'nan':
                        if '.' in emp_no:
                            emp_no = str(int(float(emp_no)))
                        emp_no = emp_no.zfill(9)
                        if emp_no not in employee_buildings:
                            employee_buildings[emp_no] = row['BUILDING']
        
        for emp_id in all_employees:
            continuous_fail = 'YES' if emp_id in continuous_fail_employees else 'NO'
            # 최신 월(3번째 월)의 실패 건수
            current_month_fail_count = month3_failures.get(emp_id, 0)
            
            aql_results.append({
                'Employee No': emp_id,
                current_month_fail_col: current_month_fail_count,
                'Continuous_FAIL': continuous_fail,
                'BUILDING': employee_buildings.get(emp_id, '')
            })
        
        result_df = pd.DataFrame(aql_results)
        print(f"✅ AQL History 기반 처리 완료: {len(result_df)}명")
        return result_df
    
    def process_aql_conditions(self, aql_df: pd.DataFrame, historical_incentive_df: pd.DataFrame = None) -> pd.DataFrame:
        """AQL 조건 처리 (기존 방식 - 이전 인센티브 파일 기반)"""
        print("\n📊 AQL 조건 처리 중...")
        
        # 직원 ID 칼럼 찾기 (AQL 데이터는 'EMPLOYEE NO' 사용)
        emp_col = self.detect_column_names(aql_df, [
            'EMPLOYEE NO', 'EMPLOYEE_NO', 'EMP_NO',
            'EMPLOYEE ID', 'EMPLOYEE_ID', 'ID',
            'Employee No', 'Personnel Number',
            'employee no'  # 소문자 버전도 추가
        ])
        
        if not emp_col:
            print("❌ 직원 ID 칼럼을 찾을 수 없습니다.")
            return pd.DataFrame()
        
        # AQL 데이터의 직원 번호를 문자열로 변환 (float 처리)
        aql_df[emp_col] = aql_df[emp_col].fillna(0).astype(float).astype(int).astype(str).str.zfill(9)
        
        aql_results = []
        current_month_fail_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # 현재 월 실패 건수 처리
        for emp_id in aql_df[emp_col].unique():
            if pd.isna(emp_id) or emp_id == '000000000':
                continue
            
            # 이미 표준화된 emp_id 사용
            if not emp_id:
                continue
            
            emp_data = aql_df[aql_df[emp_col] == emp_id]
            # 대소문자 호환성을 위해 RESULT와 FAIL을 대문자로 처리
            if 'RESULT' in emp_data.columns:
                # 'F' 또는 'FAIL' 둘 다 처리
                fail_condition = (emp_data['RESULT'] == 'F') | (emp_data['RESULT'] == 'FAIL')
                current_fail_count = len(emp_data[fail_condition])
            elif 'Result' in emp_data.columns:
                # 'F' 또는 'FAIL' 둘 다 처리 (대소문자 무관)
                fail_condition = (emp_data['Result'].str.upper() == 'F') | (emp_data['Result'].str.upper() == 'FAIL')
                current_fail_count = len(emp_data[fail_condition])
            else:
                current_fail_count = 0
            
            # 이전 월 실패 데이터 확인
            continuous_fail = 'NO'
            
            if historical_incentive_df is not None and len(self.config.previous_months) > 0:
                # 이전 월들의 실패 건수 확인
                prev_fails = []
                
                # 디버깅: TRẦN VĂN HÀ에 대해 출력
                if emp_id == '624040283':
                    print(f"    → TRẦN VĂN HÀ ({emp_id}) - 이전 월 실패 확인 중...")
                    print(f"      현재 월(July) 실패: {current_fail_count}건")
                    print(f"      사용 가능한 컬럼: {[col for col in historical_incentive_df.columns if 'Failures' in col or 'may' in col.lower() or 'jun' in col.lower()]}")
                
                for prev_month in self.config.previous_months:
                    # 여러 가능한 컬럼명 형식 시도
                    possible_columns = [
                        f"2025_{prev_month.full_name.capitalize()}_Failures",  # 예: 2025_May_Failures
                        f"{self.config.year}_{prev_month.full_name.capitalize()}_Failures",
                        f"{self.config.year}-{prev_month.short_name}",  # 예: 2025-may
                        f"{prev_month.full_name.capitalize()} AQL Failures"  # 예: May AQL Failures
                    ]
                    
                    prev_col = None
                    for col in possible_columns:
                        if col in historical_incentive_df.columns:
                            prev_col = col
                            break
                    
                    if prev_col:
                        # 디버깅: TRẦN VĂN HÀ에 대해 출력
                        if emp_id == '624040283':
                            print(f"    → {prev_month.full_name} 실패 데이터 컬럼: {prev_col}")
                    
                    if prev_col:
                        # historical_incentive_df에서 직원 ID 컬럼 찾기
                        hist_emp_col = self.detect_column_names(historical_incentive_df, [
                            'Employee No', 'Employee ID', 'EMPLOYEE NO', 
                            'Employee_No', 'Personnel Number'
                        ])
                        
                        if hist_emp_col:
                            # 직원 ID 표준화 (9자리)
                            historical_incentive_df[hist_emp_col] = historical_incentive_df[hist_emp_col].astype(str).str.strip().str.zfill(9)
                            hist_data = historical_incentive_df[
                                historical_incentive_df[hist_emp_col] == emp_id
                            ]
                            if not hist_data.empty:
                                prev_fail = hist_data.iloc[0].get(prev_col, 0)
                                if emp_id == '624040283':
                                    print(f"      {prev_month.full_name} 실패 건수: {prev_fail}")
                                prev_fails.append(prev_fail > 0)
                            else:
                                if emp_id == '624040283':
                                    print(f"      {prev_month.full_name}: 데이터 없음")
                                prev_fails.append(False)
                        else:
                            prev_fails.append(False)
                    else:
                        # 컬럼을 찾지 못한 경우 False로 처리
                        prev_fails.append(False)
                
                # 연속 실패 체크: 이전 월들과 현재 월 모두 실패가 있는 경우
                # 모든 이전 월에 대한 데이터가 있고, 모두 실패가 있으며, 현재 월도 실패가 있는 경우
                if len(prev_fails) == len(self.config.previous_months) and all(prev_fails) and current_fail_count > 0:
                    continuous_fail = 'YES'
                    # 특별히 TRẦN VĂN HÀ의 경우 디버깅
                    if emp_id == '624040283':
                        print(f"    → TRẦN VĂN HÀ - 3개월 연속 실패 확인됨!")
                        print(f"      이전 월 실패: {prev_fails}")
                        print(f"      현재 월 실패: {current_fail_count}")
            
            # 연속 인센티브 수령 개월 수는 별도로 계산 (필요 시)
            
            aql_results.append({
                'Employee No': emp_id,
                current_month_fail_col: current_fail_count,
                'Continuous_FAIL': continuous_fail
            })
        
        result_df = pd.DataFrame(aql_results)
        print(f"✅ AQL 조건 처리 완료: {len(result_df)} 명")
        return result_df


class CompleteQIPCalculator:
    """완전한 QIP 인센티브 계산기 (개선된 버전)"""
    
    def __init__(self, data: Dict[str, pd.DataFrame], config: MonthConfig):
        self.config = config
        self.month_data = None
        self.special_handler = SpecialCaseHandler(config)
        self.data_processor = DataProcessor(config)
        
        # base_path 설정 (프로젝트 루트 디렉토리)
        from pathlib import Path
        self.base_path = Path.cwd()
        
        # 데이터 저장
        self.raw_data = data
        
        # 준비 작업
        self.prepare_integrated_data()
    
    def prepare_integrated_data(self):
        """통합 데이터 준비"""
        print(f"\n📊 {self.config.get_month_str('korean')} 통합 데이터 준비 중...")
        
        # 기본 데이터 설정
        basic_key = f"{self.config.month.full_name}_basic"
        if basic_key in self.raw_data:
            # Employee No가 있는 유효한 데이터만 필터링
            raw_data = self.raw_data[basic_key]
            self.month_data = raw_data[raw_data['Employee No'].notna()].copy()
            print(f"  → 유효한 직원 데이터: {len(self.month_data)}명 (전체 {len(raw_data)}행 중)")
        else:
            print(f"❌ {self.config.get_month_str('korean')} 기본 데이터를 찾을 수 없습니다.")
            self.month_data = pd.DataFrame()
            return
        
        # 직원 ID 표준화
        emp_col = self.data_processor.detect_column_names(self.month_data, [
            'Employee No', 'EMPLOYEE NO', 'EMPLOYEE_NO', 'EMP_NO',
            'EMPLOYEE ID', 'EMPLOYEE_ID', 'ID',
            'Employee No', 'Personnel Number'
        ])
        
        if emp_col:
            # Employee No 칼럼이 이미 있으면 표준화, 없으면 생성
            if emp_col != 'Employee No':
                self.month_data['Employee No'] = self.month_data[emp_col]
            
            # 타입을 문자열로 변환하고 표준화
            self.month_data['Employee No'] = self.month_data['Employee No'].apply(
                lambda x: self.data_processor.standardize_employee_id(x) if pd.notna(x) else ''
            )
        
        # 인센티브 칼럼 초기화
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        self.month_data[incentive_col] = 0
        
        # 모든 조건 데이터 병합
        self._merge_all_conditions()
        
        # 기본값 설정
        self._set_improved_default_values()
        
        # TYPE-1 STITCHING INSPECTOR를 TYPE-2로 수정하는 전처리
        self._preprocess_position_type_corrections()
        
        print(f"✅ {self.config.get_month_str('korean')} 데이터 준비 완료: {len(self.month_data)} 명")
    
    def _merge_all_conditions(self):
        """모든 조건 데이터 병합"""
        # 출석 데이터 병합
        attendance_key = f"{self.config.month.full_name}_attendance"
        if attendance_key in self.raw_data:
            att_conditions = self.data_processor.process_attendance_conditions(
                self.raw_data[attendance_key]
            )
            if not att_conditions.empty:
                # Stop Working Date가 있는 직원 확인
                calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
                stop_working_emps = set()
                
                if 'Stop working Date' in self.month_data.columns:
                    for idx, row in self.month_data.iterrows():
                        stop_date_str = row.get('Stop working Date')
                        if pd.notna(stop_date_str) and stop_date_str != '':
                            try:
                                if '.' in str(stop_date_str):
                                    stop_date = pd.to_datetime(stop_date_str, format='%Y.%m.%d', errors='coerce')
                                else:
                                    stop_date = pd.to_datetime(stop_date_str, errors='coerce')
                                
                                if pd.notna(stop_date) and stop_date < calc_month_start:
                                    stop_working_emps.add(row['Employee No'])
                            except:
                                pass
                
                # 병합 전에 Stop Working 직원의 attendance 데이터 수정
                for emp_id in stop_working_emps:
                    if emp_id in att_conditions['Employee No'].values:
                        att_idx = att_conditions[att_conditions['Employee No'] == emp_id].index
                        if len(att_idx) > 0:
                            att_conditions.loc[att_idx[0], 'Actual Working Days'] = 0
                            att_conditions.loc[att_idx[0], 'Total Working Days'] = 0
                            att_conditions.loc[att_idx[0], 'attendancy condition 1 - acctual working days is zero'] = 'yes'
                            att_conditions.loc[att_idx[0], 'Absence Rate (raw)'] = 100.0
                
                self.month_data = pd.merge(
                    self.month_data,
                    att_conditions,
                    on='Employee No',
                    how='left'
                )
                
                # 병합 후 퇴사자 결근율 재계산
                self._recalculate_absence_rate_for_resigned()
        
        # 5PRS 데이터 병합
        prs_key = f"{self.config.month.full_name}_5prs"
        if prs_key in self.raw_data:
            prs_conditions = self.data_processor.process_5pairs_conditions(
                self.raw_data[prs_key]
            )
            if not prs_conditions.empty:
                self.month_data = pd.merge(
                    self.month_data,
                    prs_conditions,
                    on='Employee No',
                    how='left'
                )
        
        # AQL 데이터 병합
        aql_key = f"{self.config.month.full_name}_aql"
        prev_incentive_key = f"{self.config.previous_months[-1].full_name}_incentive" if self.config.previous_months else None
        
        if aql_key in self.raw_data:
            historical_data = self.raw_data.get(prev_incentive_key) if prev_incentive_key else None
            
            # 디버깅: historical_data가 제대로 로드되었는지 확인
            if historical_data is not None:
                print(f"  → 이전 인센티브 데이터 로드 성공: {len(historical_data)}건")
                # 실패 관련 컬럼 확인
                failure_cols = [col for col in historical_data.columns if 'Failure' in col or 'FAIL' in col]
                if failure_cols:
                    print(f"    실패 관련 컬럼: {failure_cols[:5]}")  # 처음 5개만 표시
            else:
                print(f"  ⚠️ 이전 인센티브 데이터 없음 (key: {prev_incentive_key})")
            # AQL history 파일이 있는지 확인
            import os
            aql_history_path = 'input_files/AQL history'
            use_history = (
                os.path.exists(f'{aql_history_path}/1.HSRG AQL REPORT-MAY.2025.csv') and
                os.path.exists(f'{aql_history_path}/1.HSRG AQL REPORT-JUNE.2025.csv') and
                os.path.exists(f'{aql_history_path}/1.HSRG AQL REPORT-JULY.2025.csv')
            )
            
            if use_history:
                print("  → AQL History 파일 사용")
                aql_conditions = self.data_processor.process_aql_conditions_with_history()
            else:
                print("  → 기존 방식 사용 (이전 인센티브 파일 기반)")
                aql_conditions = self.data_processor.process_aql_conditions(
                    self.raw_data[aql_key],
                    historical_data
                )
            if not aql_conditions.empty:
                # Employee No 표준화 (병합 전)
                aql_conditions['Employee No'] = aql_conditions['Employee No'].apply(
                    lambda x: self.data_processor.standardize_employee_id(x) if pd.notna(x) else ''
                )
                
                # 병합 전 AQL 실패 건수 확인
                aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
                if aql_col in aql_conditions.columns:
                    aql_fail_count = (aql_conditions[aql_col] > 0).sum()
                    if aql_fail_count > 0:
                        print(f"  → AQL 병합 전: {aql_fail_count}명이 AQL 실패 기록 보유")
                
                # 3개월 연속 실패자 확인
                if 'Continuous_FAIL' in aql_conditions.columns:
                    continuous_fail_count = (aql_conditions['Continuous_FAIL'] == 'YES').sum()
                    if continuous_fail_count > 0:
                        print(f"  → AQL 병합 전: {continuous_fail_count}명이 3개월 연속 실패")
                        # 624040283 확인
                        tran = aql_conditions[aql_conditions['Employee No'] == '624040283']
                        if not tran.empty:
                            print(f"    → 624040283 Continuous_FAIL: {tran.iloc[0]['Continuous_FAIL']}")
                
                self.month_data = pd.merge(
                    self.month_data,
                    aql_conditions,
                    on='Employee No',
                    how='left'
                )
                
                # 병합 후 AQL 실패 건수 확인
                if aql_col in self.month_data.columns:
                    aql_fail_count_after = (self.month_data[aql_col] > 0).sum()
                    print(f"  → AQL 병합 후: {aql_fail_count_after}명이 AQL 실패 기록 보유")
                
                # 병합 후 3개월 연속 실패자 확인
                if 'Continuous_FAIL' in self.month_data.columns:
                    continuous_fail_count_after = (self.month_data['Continuous_FAIL'] == 'YES').sum()
                    print(f"  → AQL 병합 후: {continuous_fail_count_after}명이 3개월 연속 실패")
                    # 624040283 확인
                    tran_after = self.month_data[self.month_data['Employee No'] == '624040283']
                    if not tran_after.empty:
                        print(f"    → 624040283 Continuous_FAIL 병합 후: {tran_after.iloc[0]['Continuous_FAIL']}")
    
    def _recalculate_absence_rate_for_resigned(self):
        """퇴사자를 위한 결근율 재계산"""
        import numpy as np
        from datetime import datetime, timedelta
        
        if 'Stop working Date' not in self.month_data.columns:
            return
        
        calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
        calc_month_end = pd.Timestamp(self.config.year, self.config.month.number + 1, 1) - pd.Timedelta(days=1) if self.config.month.number < 12 else pd.Timestamp(self.config.year, 12, 31)
        
        for idx, row in self.month_data.iterrows():
            stop_date_str = row.get('Stop working Date')
            if pd.notna(stop_date_str) and stop_date_str != '':
                try:
                    # 날짜 파싱
                    if '.' in str(stop_date_str):
                        stop_date = pd.to_datetime(stop_date_str, format='%Y.%m.%d', errors='coerce')
                    else:
                        stop_date = pd.to_datetime(stop_date_str, errors='coerce')
                    
                    if pd.notna(stop_date):
                        # 해당 월 중 퇴사자인 경우
                        if calc_month_start <= stop_date <= calc_month_end:
                            # 근무 가능일 계산 (주말 제외)
                            working_days_possible = 0
                            current_date = calc_month_start
                            while current_date <= stop_date:
                                if current_date.weekday() < 5:  # 월-금 (0-4)
                                    working_days_possible += 1
                                current_date += pd.Timedelta(days=1)
                            
                            actual_days = row.get('Actual Working Days', 0)
                            
                            # 결근율 재계산
                            if working_days_possible > 0:
                                new_absence_rate = ((working_days_possible - actual_days) / working_days_possible) * 100
                            else:
                                new_absence_rate = 0
                            
                            # 업데이트
                            self.month_data.loc[idx, 'Total Working Days'] = working_days_possible
                            self.month_data.loc[idx, 'Absence Rate (raw)'] = round(new_absence_rate, 2)
                            self.month_data.loc[idx, 'attendancy condition 3 - absent % is over 12%'] = 'yes' if new_absence_rate > 12 else 'no'
                            
                            # 최소 근무일 조건도 체크
                            self.month_data.loc[idx, 'attendancy condition 4 - minimum working days'] = 'yes' if actual_days < 12 else 'no'
                            
                            print(f"  → 퇴사자 {row.get('Employee No', '')}: {stop_date.strftime('%Y-%m-%d')} 퇴사, 근무가능일 {working_days_possible}일, 결근율 {new_absence_rate:.1f}%")
                        
                        # 계산 월 이전 퇴사자
                        elif stop_date < calc_month_start:
                            self.month_data.loc[idx, 'Actual Working Days'] = 0
                            self.month_data.loc[idx, 'Total Working Days'] = 0
                            self.month_data.loc[idx, 'attendancy condition 1 - acctual working days is zero'] = 'yes'
                            self.month_data.loc[idx, 'attendancy condition 4 - minimum working days'] = 'yes'
                            
                except Exception as e:
                    print(f"  ⚠️ 퇴사자 결근율 재계산 오류 (직원 {row.get('Employee No', '')}): {e}")
    
    def _set_improved_default_values(self):
        """개선된 기본값 설정"""
        # AQL 실패 기본값 - 이미 병합된 데이터는 건드리지 않음
        aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
        if aql_col not in self.month_data.columns:
            self.month_data[aql_col] = 0
        else:
            # NaN 값만 0으로 채우고, 기존 값은 유지
            self.month_data[aql_col] = self.month_data[aql_col].fillna(0)
        
        # 출석 관련 기본값 - attendance 데이터 없으면 0으로 설정
        if 'Total Working Days' not in self.month_data.columns:
            self.month_data['Total Working Days'] = self.config.working_days
            self.month_data['Actual Working Days'] = 0  # 기본값 0으로 변경 (기존 23)
            self.month_data['Unapproved Absence Days'] = 0
            self.month_data['Absence Rate (raw)'] = 0.0
            print("  → 출석 데이터 없는 직원들에게 기본값 0 적용")
        
        # Stop Working Date 처리 - 계산 월 이전 퇴사자는 Actual Working Days = 0
        if 'Stop working Date' in self.month_data.columns:
            calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
            
            for idx, row in self.month_data.iterrows():
                stop_date_str = row.get('Stop working Date')
                if pd.notna(stop_date_str) and stop_date_str != '':
                    try:
                        # 다양한 날짜 형식 처리
                        if '.' in str(stop_date_str):
                            stop_date = pd.to_datetime(stop_date_str, format='%Y.%m.%d', errors='coerce')
                        else:
                            stop_date = pd.to_datetime(stop_date_str, errors='coerce')
                        
                        if pd.notna(stop_date) and stop_date < calc_month_start:
                            # 계산 월 이전에 퇴사한 경우
                            self.month_data.loc[idx, 'Actual Working Days'] = 0
                            self.month_data.loc[idx, 'Total Working Days'] = 0
                            self.month_data.loc[idx, 'attendancy condition 1 - acctual working days is zero'] = 'yes'
                            self.month_data.loc[idx, 'Absence Rate (raw)'] = 100.0
                            print(f"  → Stop Working 직원 {row.get('Employee No', '')}: {stop_date.strftime('%Y-%m-%d')} 퇴사 → Actual Working Days = 0")
                    except Exception as e:
                        print(f"  ⚠️ Stop Working Date 처리 오류 (직원 {row.get('Employee No', '')}): {e}")
        
        # 조건 칼럼 기본값
        default_conditions = {
            'attendancy condition 1 - acctual working days is zero': 'yes',  # 기본값 0이므로 yes
            'attendancy condition 2 - unapproved Absence Day is more than 2 days': 'no',
            'attendancy condition 3 - absent % is over 12%': 'no',
            'attendancy condition 4 - minimum working days': 'yes',  # 기본값 0이므로 12일 미만
            '5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%': 'no',
            '5prs condition 2 - Total Valiation Qty is zero': 'yes',
            'Total Working Days': self.config.working_days,
            'Actual Working Days': 0,  # 기본값 0으로 변경
            'Unapproved Absence Days': 0,
            'Absence Rate (raw)': 0.0,
            'Continuous_FAIL': 'NO'
        }
        
        for col, default_val in default_conditions.items():
            if col not in self.month_data.columns:
                self.month_data[col] = default_val
            else:
                self.month_data[col] = self.month_data[col].fillna(default_val)
    
    def _preprocess_position_type_corrections(self):
        """직급과 타입 불일치를 수정하는 전처리 함수
        
        주요 수정사항:
        - TYPE-1 STITCHING INSPECTOR → TYPE-2로 변경
        """
        print("\n🔧 직급-타입 데이터 전처리 중...")
        correction_count = 0
        
        # TYPE-1이면서 STITCHING INSPECTOR인 경우를 TYPE-2로 수정
        if 'ROLE TYPE STD' in self.month_data.columns and 'QIP POSITION 1ST  NAME' in self.month_data.columns:
            # 수정이 필요한 직원 찾기
            stitching_mask = (
                (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('STITCHING', na=False)) &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
            )
            
            # 수정 대상 확인 및 로깅
            if stitching_mask.any():
                affected_employees = self.month_data[stitching_mask]
                for idx, row in affected_employees.iterrows():
                    emp_no = row.get('Employee No', 'Unknown')
                    emp_name = row.get('Full Name', 'Unknown')
                    position = row.get('QIP POSITION 1ST  NAME', 'Unknown')
                    print(f"  → TYPE-1 → TYPE-2 수정: {emp_no} ({emp_name}) - {position}")
                    correction_count += 1
                
                # TYPE을 TYPE-2로 수정
                self.month_data.loc[stitching_mask, 'ROLE TYPE STD'] = 'TYPE-2'
        
        if correction_count > 0:
            print(f"  ✅ 총 {correction_count}명의 직급-타입 불일치 수정 완료")
        else:
            print(f"  ✅ 수정이 필요한 직급-타입 불일치 없음")
    
    def check_required_files_for_month(self, month_obj, year):
        """특정 월 계산에 필요한 파일들이 존재하는지 확인"""
        month_name = month_obj.full_name
        
        required_files = {
            'basic': self.base_path / 'input_files' / f'basic manpower data {month_name}.csv',
            'aql': self.base_path / 'input_files' / 'AQL history' / f'1.HSRG AQL REPORT-{month_name.upper()}.{year}.csv',
            '5prs': self.base_path / 'input_files' / f'5prs data {month_name}.csv',
            'attendance': self.base_path / 'input_files' / 'attendance' / 'converted' / f'attendance data {month_name}_converted.csv'
        }
        
        missing_files = []
        for file_type, file_path in required_files.items():
            if not file_path.exists():
                missing_files.append({
                    'type': file_type,
                    'path': str(file_path),
                    'name': file_path.name
                })
        
        if missing_files:
            print(f"\n⚠️ {month_obj.number}월 계산에 필요한 파일이 없습니다:")
            print(f"   현재 작업 디렉토리: {self.base_path}")
            print(f"\n   찾을 수 없는 파일:")
            for missing in missing_files:
                print(f"   - {missing['type']}: {missing['name']}")
                print(f"     전체 경로: {missing['path']}")
            return False
        
        return True
    
    def ensure_previous_month_exists(self):
        """이전 월 인센티브 파일 확인 및 자동 생성"""
        if self.config.month.number == 1:
            prev_month = 12
            prev_year = self.config.year - 1
        else:
            prev_month = self.config.month.number - 1
            prev_year = self.config.year
        
        prev_month_obj = Month.from_number(prev_month)
        prev_file_path = self.base_path / 'output_files' / f'output_QIP_incentive_{prev_month_obj.full_name}_{prev_year}_최종완성버전_v6.0_Complete.csv'
        
        if not prev_file_path.exists():
            print(f"\n📊 {prev_month}월 인센티브 파일이 없습니다.")
            print(f"   {prev_month}월을 자동으로 계산합니다...")
            
            # 이전 월 계산에 필요한 파일들 체크
            if not self.check_required_files_for_month(prev_month_obj, prev_year):
                print(f"\n❌ {prev_month}월 계산을 중단합니다.")
                print(f"   필요한 파일들을 먼저 준비해주세요.")
                print(f"\n❌ {self.config.month.number}월 계산도 중단합니다.")
                print(f"   이전 월 데이터가 필요하므로 {prev_month}월을 먼저 준비해주세요.")
                raise Exception(f"{prev_month}월 데이터가 없어 {self.config.month.number}월 계산을 중단합니다.")
            
            print(f"\n✅ {prev_month}월 계산에 필요한 파일이 모두 있습니다.")
            print(f"   {prev_month}월 계산 시작...")
            
            # 이전 월 계산기 생성 및 실행
            # 이전 월 config 파일 로드
            prev_config_file = self.base_path / 'config_files' / f'config_{prev_month_obj.full_name}_{prev_year}.json'
            if not prev_config_file.exists():
                print(f"❌ {prev_month}월 config 파일이 없습니다: {prev_config_file}")
                raise Exception(f"{prev_month}월 config 파일이 없어 {self.config.month.number}월 계산을 중단합니다.")
            
            # JSON 파일 로드
            import json
            with open(prev_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # previous_months를 Month 객체로 변환
            prev_months_str = config_data.get('previous_months', [])
            prev_months_obj = []
            for month_str in prev_months_str:
                # Month enum 찾기
                for m in Month:
                    if m.full_name == month_str:
                        prev_months_obj.append(m)
                        break
            
            # MonthConfig 생성
            prev_config = MonthConfig(
                month=prev_month_obj,
                year=prev_year,
                working_days=config_data.get('working_days', 22),
                previous_months=prev_months_obj,
                file_paths=config_data.get('file_paths', {}),
                output_prefix=config_data.get('output_prefix', f'output_QIP_incentive_{prev_month_obj.full_name}_{prev_year}')
            )
            
            prev_data_loader = CompleteDataLoader(prev_config)
            prev_data = prev_data_loader.load_all_files()
            
            if not prev_data:
                print(f"❌ {prev_month}월 데이터 로드 실패")
                raise Exception(f"{prev_month}월 데이터 로드 실패로 {self.config.month.number}월 계산을 중단합니다.")
            
            # 이전 월 계산기 생성
            prev_processor = CompleteQIPCalculator(prev_data, prev_config)
            
            # 재귀 방지를 위해 이전 월의 이전 월은 체크하지 않음
            prev_processor.calculate_all_incentives_without_check()
            
            # 결과 저장
            output_path = self.base_path / 'output_files' / f'output_QIP_incentive_{prev_month_obj.full_name}_{prev_year}_최종완성버전_v6.0_Complete.csv'
            prev_processor.month_data.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"✅ {prev_month}월 계산 완료\n")
    
    def calculate_all_incentives_without_check(self):
        """이전 월 체크 없이 인센티브 계산 (재귀 방지용)"""
        print(f"📊 TYPE별 인센티브 계산 시작...")
        
        # 관리자-부하 매핑 생성
        subordinate_mapping = self.create_manager_subordinate_mapping()
        
        # 동일한 로직 실행
        self.calculate_auditor_trainer_incentive(subordinate_mapping)
        self.calculate_assembly_inspector_incentive_type1_only()
        self.calculate_type2_incentive()
        self.calculate_line_leader_incentive_type1_only(subordinate_mapping)
        self.calculate_head_incentive(subordinate_mapping)
        
        print(f"✅ 인센티브 계산 완료")
    
    def calculate_all_incentives(self):
        """모든 인센티브 계산 실행"""
        print(f"\n🚀 {self.config.get_month_str('korean')} QIP 인센티브 계산 시작...")
        
        # 0. 데이터 검증
        self.validate_and_report_issues()
        
        # 0.5. 이전 월 데이터 확인
        self.ensure_previous_month_exists()
        
        # 1. 특별 케이스 처리
        self.handle_special_cases()
        
        # 2. Type-1 Assembly Inspector 계산
        self.calculate_assembly_inspector_incentive_type1_only()
        
        # 3. 관리자-부하 매핑 생성
        subordinate_mapping = self.create_manager_subordinate_mapping()
        
        # 4. Type-1 Auditor/Trainer 계산
        self.calculate_auditor_trainer_incentive(subordinate_mapping)
        
        # 5. Type-1 Line Leader 계산
        self.calculate_line_leader_incentive_type1_only(subordinate_mapping)
        
        # 5. Head(Group Leader) 계산
        self.calculate_head_incentive(subordinate_mapping)
        
        # 6. 관리자 계산
        self.calculate_managers_by_manual_logic_fixed(subordinate_mapping)
        
        # 6. Type-2 계산
        self.calculate_type2_incentive()
        
        # 7. Type-3 계산
        self.calculate_type3_incentive()
        
        print(f"\n✅ {self.config.get_month_str('korean')} 인센티브 계산 완료!")
    
    def handle_special_cases(self):
        """특별 케이스 처리 - 자동 계산"""
        # 특별 케이스는 이제 calculate_assembly_inspector_incentive_type1_only와
        # calculate_auditor_trainer_incentive에서 자동으로 처리됨
        pass
    
    def identify_special_cases(self) -> Dict[str, List]:
        """특별 케이스 식별 (Audit/Training 제외)"""
        special_cases = {
            'aql': [],
            'model_master': []
        }
        
        for idx, row in self.month_data.iterrows():
            position = str(row.get('QIP POSITION 1ST  NAME', '')).upper()
            
            if 'AQL' in position and 'INSPECTOR' in position:
                special_cases['aql'].append(idx)
            elif 'MODEL' in position and 'MASTER' in position:
                special_cases['model_master'].append(idx)
            # Audit/Training은 이제 별도로 처리
        
        return special_cases
    
    def check_subordinates_continuous_fail(self, manager_id: str, subordinate_mapping: Dict[str, List[str]]) -> bool:
        """
        부하직원 중 3개월 연속 AQL 실패자가 있는지 확인
        Returns: True if 연속 실패자 있음, False if 없음
        """
        if manager_id not in subordinate_mapping:
            return False
        
        for sub_id in subordinate_mapping[manager_id]:
            sub_data = self.month_data[self.month_data['Employee No'] == sub_id]
            if not sub_data.empty:
                if sub_data.iloc[0].get('Continuous_FAIL', 'NO') == 'YES':
                    return True
        return False
    
    def get_continuous_fail_by_factory(self) -> Dict[str, int]:
        """
        3개월 연속 실패자의 공장별 분포 반환
        Returns: {공장명: 연속실패자수}
        """
        continuous_fail_mask = self.month_data['Continuous_FAIL'] == 'YES'
        continuous_fail_employees = self.month_data[continuous_fail_mask]
        
        factory_counts = {}
        for _, row in continuous_fail_employees.iterrows():
            factory = self.get_employee_factory(row['Employee No'])
            if factory:
                factory_counts[factory] = factory_counts.get(factory, 0) + 1
        
        return factory_counts
    
    def get_employee_factory(self, emp_id: str) -> str:
        """
        직원의 소속 공장(Building) 반환
        """
        emp_data = self.month_data[self.month_data['Employee No'] == emp_id]
        if not emp_data.empty:
            # Building 정보 찾기
            if 'BUILDING' in emp_data.columns:
                return str(emp_data.iloc[0]['BUILDING'])
            elif 'Building' in emp_data.columns:
                return str(emp_data.iloc[0]['Building'])
        return ''
    
    def validate_and_report_issues(self):
        """데이터 문제 검증 및 보고"""
        print("\n🔍 데이터 검증 중...")
        
        # AQL reject rate 검증
        aql_data = self.load_aql_data_for_area_calculation()
        if aql_data is not None and not aql_data.empty:
            buildings = ['A', 'B', 'C', 'D']
            problems_found = False
            
            for building in buildings:
                # REPACKING PO가 NORMAL PO인 데이터만 필터
                building_data = aql_data[
                    (aql_data['BUILDING'] == building) & 
                    (aql_data['REPACKING PO'] == 'NORMAL PO')
                ]
                
                if not building_data.empty:
                    total = len(building_data)
                    fails = len(building_data[building_data['RESULT'] == 'FAIL'])
                    rate = (fails / total * 100) if total > 0 else 0
                    
                    if rate >= 3.0:
                        problems_found = True
                        print(f"   ⚠️ Building {building}: Reject Rate {rate:.2f}% (>=3%)")
                        
                        # 해당 Building 담당자 찾기
                        area_mapping = self.load_auditor_trainer_area_mapping()
                        for emp_id, config in area_mapping.get('auditor_trainer_areas', {}).items():
                            for cond in config.get('conditions', []):
                                for filter_item in cond.get('filters', []):
                                    if filter_item.get('column') == 'BUILDING' and filter_item.get('value') == building:
                                        emp_name = config.get('name', 'Unknown')
                                        print(f"      → 영향받는 직원: {emp_name} ({emp_id})")
                                        break
            
            if problems_found:
                print("\n   인센티브가 0이 될 수 있는 조건이 발견되었습니다.")
        else:
            print("   ⚠️ AQL 데이터를 찾을 수 없습니다.")
    
    def get_auditor_assigned_factory(self, auditor_id: str) -> str:
        """
        Auditor/Trainer가 담당하는 공장(Building) 반환
        매핑 파일에서 담당 구역 확인
        """
        # auditor_trainer_area_mapping.json 로드
        area_mapping = self.load_auditor_trainer_area_mapping()
        
        if not area_mapping:
            return ''
        
        # 해당 auditor의 담당 구역 찾기
        auditor_id_str = str(auditor_id)
        if auditor_id_str in area_mapping.get('auditor_trainer_areas', {}):
            config = area_mapping['auditor_trainer_areas'][auditor_id_str]
            
            # conditions에서 BUILDING 찾기
            for condition in config.get('conditions', []):
                if condition['type'] == 'AND':
                    for filter_item in condition['filters']:
                        if filter_item['column'] == 'BUILDING':
                            return filter_item['value']
        
        return ''
    
    def calculate_total_factory_reject_rate(self) -> float:
        """
        전체 공장의 AQL reject율 계산 (Model Master용)
        """
        # AQL 데이터 로드
        aql_data = self.load_aql_data_for_area_calculation()
        if aql_data is None or aql_data.empty:
            return 0.0
        
        # 전체 검사 수
        total_inspections = len(aql_data)
        
        # Result 컬럼 찾기
        result_col = None
        for col in aql_data.columns:
            if col.upper() == 'RESULT':
                result_col = col
                break
        
        if result_col:
            # FAIL 수 계산
            total_failures = len(aql_data[aql_data[result_col].str.upper() == 'FAIL'])
        else:
            total_failures = 0
        
        if total_inspections > 0:
            reject_rate = (total_failures / total_inspections) * 100
            print(f"    → 전체 공장: 검사 {total_inspections}건, 실패 {total_failures}건, reject율 {reject_rate:.2f}%")
            return reject_rate
        
        return 0.0
    
    def calculate_auditor_trainer_incentive(self, subordinate_mapping: Dict[str, List[str]]):
        """Auditor/Trainer 및 Model Master 인센티브 계산 (자동화)"""
        print("\n👥 TYPE-1 AUDITOR/TRAINER & MODEL MASTER 인센티브 계산...")
        
        # Auditor/Trainer 필터링
        auditor_trainer_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            ((self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('AUDIT', na=False)) |
             (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('TRAINER', na=False)) |
             (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('TRAINING', na=False)))
        )
        
        # Model Master 필터링 - 두 가지 방법으로 식별
        # 1. QA2A 코드를 가진 직원 (예: 620080295)
        # 2. QIP POSITION 1ST NAME이 'MODEL MASTER'인 직원
        model_master_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') & 
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('MODEL MASTER', na=False))
        )
        
        if 'FINAL QIP POSITION NAME CODE' in self.month_data.columns:
            qa2a_mask = (
                (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                (self.month_data['FINAL QIP POSITION NAME CODE'] == 'QA2A')
            )
            model_master_mask = model_master_mask | qa2a_mask
        
        # 3개월 연속 실패자의 공장별 분포 찾기
        continuous_fail_by_factory = self.get_continuous_fail_by_factory()
        
        # Model Master를 위한 전체 공장 reject율 계산
        total_factory_reject_rate = self.calculate_total_factory_reject_rate()
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # Model Master 처리 (별도로 먼저 처리)
        for idx, row in self.month_data[model_master_mask].iterrows():
            # 이미 계산된 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            emp_id = row.get('Employee No', '')
            
            # 기본 조건 체크
            attendance_fail = (
                row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
                row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
                row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
                row.get('attendancy condition 4 - minimum working days') == 'yes'
            )
            
            aql_fail = row.get(aql_col, 0) > 0
            continuous_fail = row.get('Continuous_FAIL', 'NO') == 'YES'
            
            # Model Master는 전체 공장 reject율 적용
            if attendance_fail or continuous_fail or aql_fail:
                incentive = 0
            elif total_factory_reject_rate >= 3.0:  # 전체 공장 reject율 3% 이상
                incentive = 0
                print(f"    → {row.get('Full Name', 'Unknown')} (Model Master): 전체 공장 AQL reject율 {total_factory_reject_rate:.1f}% → 0 VND")
            else:
                # Assembly Inspector와 동일한 연속 충족 개월 기준 적용
                continuous_months = self.data_processor.calculate_continuous_months_from_history(emp_id)
                incentive = self.get_assembly_inspector_amount(continuous_months)
                if continuous_months > 0:
                    print(f"    → {row.get('Full Name', 'Unknown')} (Model Master): {continuous_months}개월 연속 → {incentive:,} VND")
            
            self.month_data.loc[idx, incentive_col] = incentive
        
        # 일반 Auditor/Trainer 처리 (Model Master 제외)
        auditor_only_mask = auditor_trainer_mask & ~model_master_mask
        
        for idx, row in self.month_data[auditor_only_mask].iterrows():
            # 이미 계산된 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            emp_id = row.get('Employee No', '')
            
            # 1. 담당 구역 AQL reject율 계산
            area_reject_rate = self.calculate_area_aql_reject_rate(emp_id, subordinate_mapping)
            
            # 2. 담당 공장에 3개월 연속 실패자가 있는지 확인
            # Auditor/Trainer의 담당 공장을 매핑에서 찾기
            auditor_factory = self.get_auditor_assigned_factory(emp_id)
            has_continuous_fail_in_factory = auditor_factory in continuous_fail_by_factory and continuous_fail_by_factory[auditor_factory] > 0
            
            # 3. 기본 조건 체크
            attendance_fail = (
                row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
                row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
                row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
                row.get('attendancy condition 4 - minimum working days') == 'yes'
            )
            
            aql_fail = row.get(aql_col, 0) > 0
            continuous_fail = row.get('Continuous_FAIL', 'NO') == 'YES'
            
            # 인센티브 결정
            if attendance_fail or continuous_fail or aql_fail:
                incentive = 0
            elif area_reject_rate >= 3.0:  # 담당 구역 reject율 3% 이상으로 변경
                incentive = 0
                print(f"    → {row.get('Full Name', 'Unknown')}: 담당 구역 AQL reject율 {area_reject_rate:.1f}% → 0 VND")
            elif has_continuous_fail_in_factory:  # 담당 공장에 3개월 연속 실패자 있음
                incentive = 0
                fail_count = continuous_fail_by_factory.get(auditor_factory, 0)
                print(f"    → {row.get('Full Name', 'Unknown')}: 담당 공장({auditor_factory})에 3개월 연속 AQL 실패자 {fail_count}명 → 0 VND")
            else:
                # Assembly Inspector와 동일한 연속 충족 개월 기준 적용
                continuous_months = self.data_processor.calculate_continuous_months_from_history(emp_id)
                incentive = self.get_assembly_inspector_amount(continuous_months)
                if continuous_months > 0:
                    print(f"    → {row.get('Full Name', 'Unknown')}: {continuous_months}개월 연속 → {incentive:,} VND")
            
            self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력 (전체)
        all_mask = auditor_trainer_mask | model_master_mask
        receiving_count = (self.month_data[all_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[all_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def calculate_area_aql_reject_rate(self, auditor_id: str, subordinate_mapping: Dict[str, List[str]]) -> float:
        """
        담당 구역의 AQL reject율 계산
        JSON 파일에서 담당 구역 조건을 읽어 해당 구역의 AQL reject율 계산
        """
        # JSON 파일에서 담당 구역 정보 로드
        area_mapping = self.load_auditor_trainer_area_mapping()
        
        # Model Master 체크
        if area_mapping and auditor_id in area_mapping.get('model_master', {}).get('employees', {}):
            # Model Master는 전체 구역 담당
            area_config = area_mapping['model_master']['employees'][auditor_id]
            conditions = area_config.get('conditions', [])
        elif area_mapping and auditor_id in area_mapping.get('auditor_trainer_areas', {}):
            # 일반 Auditor/Trainer
            area_config = area_mapping['auditor_trainer_areas'][auditor_id]
            conditions = area_config.get('conditions', [])
        else:
            # 매핑이 없으면 부하직원 기반으로 계산 (fallback)
            return self.calculate_area_aql_reject_rate_by_subordinates(auditor_id, subordinate_mapping)
        
        # AQL 데이터 로드
        aql_data = self.load_aql_data_for_area_calculation()
        if aql_data is None or aql_data.empty:
            return 0.0
        
        # conditions는 이미 위에서 설정됨
        
        # 조건에 맞는 데이터 필터링
        filtered_data = pd.DataFrame()
        for condition in conditions:
            if condition['type'] == 'ALL':
                # 전체 데이터 사용
                filtered_data = aql_data
                break
            elif condition['type'] == 'AND':
                # AND 조건으로 필터링
                temp_data = aql_data.copy()
                for filter_item in condition['filters']:
                    col = filter_item['column']
                    val = filter_item['value']
                    if col in temp_data.columns:
                        temp_data = temp_data[temp_data[col] == val]
                if not filtered_data.empty:
                    filtered_data = pd.concat([filtered_data, temp_data], ignore_index=True)
                else:
                    filtered_data = temp_data
            elif condition['type'] == 'OR':
                # OR 조건으로 필터링
                for filter_item in condition['filters']:
                    col = filter_item['column']
                    val = filter_item['value']
                    if col in aql_data.columns:
                        temp_data = aql_data[aql_data[col] == val]
                        if not filtered_data.empty:
                            filtered_data = pd.concat([filtered_data, temp_data], ignore_index=True)
                        else:
                            filtered_data = temp_data
        
        # reject율 계산
        if filtered_data.empty:
            return 0.0
        
        total_inspections = len(filtered_data)
        # Result 컬럼 이름 찾기 (대소문자 구분 없이)
        result_col = None
        for col in filtered_data.columns:
            if col.upper() == 'RESULT':
                result_col = col
                break
        
        if result_col:
            # FAIL 찾기 (대소문자 구분 없이)
            total_failures = len(filtered_data[filtered_data[result_col].str.upper() == 'FAIL'])
        else:
            total_failures = 0
        
        if total_inspections > 0:
            reject_rate = (total_failures / total_inspections) * 100
            print(f"    → {auditor_id} ({area_config.get('name', 'Unknown')}): 담당 구역 검사 {total_inspections}건, 실패 {total_failures}건, reject율 {reject_rate:.2f}%")
            return reject_rate
        
        return 0.0
    
    def calculate_area_aql_reject_rate_by_subordinates(self, auditor_id: str, subordinate_mapping: Dict[str, List[str]]) -> float:
        """
        부하직원 기반 AQL reject율 계산 (fallback)
        """
        if auditor_id not in subordinate_mapping:
            return 0.0
        
        total_inspections = 0
        total_failures = 0
        aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        for sub_id in subordinate_mapping[auditor_id]:
            sub_data = self.month_data[self.month_data['Employee No'] == sub_id]
            if not sub_data.empty:
                failures = sub_data.iloc[0].get(aql_col, 0)
                total_failures += failures
                total_inspections += 100  # 가정: 각 직원당 평균 100개 검사
        
        if total_inspections > 0:
            return (total_failures / total_inspections) * 100
        return 0.0
    
    def normalize_column_name(self, col: str) -> str:
        """
        컬럼명 정규화: 공백, 특수문자, 줄바꿈 제거
        """
        if not isinstance(col, str):
            return str(col)
        # 공백 제거, 작은따옴표 제거, 줄바꿈을 공백으로 변경
        return col.strip().replace("'", "").replace("\n", " ").replace("  ", " ")
    
    def load_auditor_trainer_area_mapping(self) -> Dict:
        """
        Auditor/Trainer 담당 구역 매핑 JSON 파일 로드
        """
        try:
            # config_files 폴더에서 찾기
            json_path = self.base_path / 'config_files' / 'auditor_trainer_area_mapping.json'
            if not json_path.exists():
                # 없으면 프로젝트 루트의 config_files에서 찾기
                from pathlib import Path
                json_path = Path('config_files/auditor_trainer_area_mapping.json')
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("⚠️ auditor_trainer_area_mapping.json 파일을 찾을 수 없습니다.")
        except Exception as e:
            print(f"⚠️ JSON 파일 로드 중 오류: {e}")
        return {}
    
    def load_aql_data_for_area_calculation(self) -> pd.DataFrame:
        """
        담당 구역 계산을 위한 AQL 데이터 로드
        AQL history 폴더에서 파일 로드
        """
        try:
            # AQL history 파일 경로 설정
            month_upper = self.config.get_month_str('capital').upper()
            year = self.config.year
            file_path = self.base_path / 'input_files' / 'AQL history' / f'1.HSRG AQL REPORT-{month_upper}.{year}.csv'
            
            if file_path.exists():
                # 파일 로드
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                
                # 빈 행 제거 (모든 값이 NaN인 행)
                df = df.dropna(how='all')
                
                # 컬럼명 정규화
                df.columns = [self.normalize_column_name(col) for col in df.columns]
                
                # 실제 데이터 건수 로그
                print(f"  → AQL 데이터 로드: {len(df)}건")
                
                return df
            else:
                print(f"⚠️ AQL history 파일을 찾을 수 없습니다: {file_path}")
                
        except Exception as e:
            print(f"⚠️ AQL 데이터 로드 중 오류: {e}")
        
        return pd.DataFrame()
    
    def check_subordinates_continuous_fail(self, manager_id: str, subordinate_mapping: Dict[str, List[str]]) -> bool:
        """
        부하직원 중 3개월 연속 AQL 실패자가 있는지 확인
        """
        if manager_id not in subordinate_mapping:
            return False
        
        for sub_id in subordinate_mapping[manager_id]:
            sub_data = self.month_data[self.month_data['Employee No'] == sub_id]
            if not sub_data.empty:
                if sub_data.iloc[0].get('Continuous_FAIL', 'NO') == 'YES':
                    return True
        
        return False
    
    def calculate_aql_inspector_incentive(self, aql_mask, incentive_col: str, aql_col: str):
        """Type-1 AQL Inspector 3파트 인센티브 계산"""
        print("\n📊 TYPE-1 AQL INSPECTOR 3파트 인센티브 계산...")
        
        # AQL Inspector 설정 로드
        aql_config = self.load_aql_inspector_config()
        if not aql_config:
            print("⚠️ AQL Inspector 설정 파일을 찾을 수 없습니다.")
            return
        
        for idx, row in self.month_data[aql_mask].iterrows():
            # 이미 계산된 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            emp_id = row.get('Employee No', '')
            
            # Stop working 직원도 정상 계산 (제외하지 않음)
            
            # 조건 체크 - 모든 타입에 적용되는 공통 조건
            attendance_fail = (
                row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
                row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
                row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
                row.get('attendancy condition 4 - minimum working days') == 'yes'  # 최소 12일 근무 조건 추가
            )
            
            # AQL Inspector는 5PRS 조건 적용 안 함
            # prs_pass = row.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%') == 'yes'
            
            # AQL 조건: 당월 실패 건수 0건, 3개월 연속 실패 아님
            aql_fail = row.get(aql_col, 0) > 0
            continuous_fail = row.get('Continuous_FAIL', 'NO') == 'YES'
            
            # 기본 조건 미충족 시 0원 (5PRS 조건 제외)
            if attendance_fail or continuous_fail or aql_fail:
                incentive = 0
                self.month_data.loc[idx, incentive_col] = incentive
                continue
            
            # Part 1, Part 3 연속 달성 개월 수 계산
            part1_months, part3_months = self.get_aql_inspector_continuous_months(emp_id, aql_config)
            
            # Part 1: AQL 검사 평가 결과 인센티브
            part1_amount = self.calculate_aql_part1_amount(part1_months, aql_config)
            
            # Part 2: CFA 자격증 인센티브
            part2_amount = self.calculate_aql_part2_amount(emp_id, aql_config)
            
            # Part 3: HWK 클레임 방지 인센티브
            part3_amount = self.calculate_aql_part3_amount(part3_months, aql_config)
            
            # 총 인센티브 계산
            total_incentive = part1_amount + part2_amount + part3_amount
            
            self.month_data.loc[idx, incentive_col] = total_incentive
            
            # 디버깅 출력
            print(f"    → {row.get('Full Name', 'Unknown')} ({emp_id}):")
            print(f"      Part 1 ({part1_months}개월): {part1_amount:,} VND")
            print(f"      Part 2 (CFA): {part2_amount:,} VND")
            print(f"      Part 3 ({part3_months}개월): {part3_amount:,} VND")
            print(f"      총액: {total_incentive:,} VND")
        
        # 통계 출력
        receiving_count = (self.month_data[aql_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[aql_mask][incentive_col].sum()
        print(f"  → AQL Inspector 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def load_aql_inspector_config(self) -> Dict:
        """AQL Inspector 인센티브 설정 로드"""
        try:
            # config_files 폴더에서 찾기
            config_path = self.base_path / 'config_files' / 'aql_inspector_incentive_config.json'
            if not config_path.exists():
                # 없으면 프로젝트 루트의 config_files에서 찾기
                from pathlib import Path
                config_path = Path('config_files/aql_inspector_incentive_config.json')
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ AQL Inspector 설정 로드 중 오류: {e}")
        return {}
    
    def get_aql_inspector_continuous_months(self, emp_id: str, aql_config: Dict) -> Tuple[int, int]:
        """AQL Inspector의 Part 1과 Part 3 연속 달성 개월 수 계산"""
        # 이전 달 정보에서 읽기 (6월 정보 기반)
        if emp_id in aql_config.get('aql_inspectors', {}):
            june_info = aql_config['aql_inspectors'][emp_id].get('june_2025_incentive', {})
            # 7월은 6월 + 1개월 (조건 충족 가정)
            part1_months = june_info.get('part1_months', 0) + 1
            part3_months = june_info.get('part3_months', 0) + 1
            
            # 최대값 제한
            part1_months = min(part1_months, 15)
            part3_months = min(part3_months, 15)
            
            return part1_months, part3_months
        
        # 신규 직원인 경우
        return 1, 1
    
    def calculate_aql_part1_amount(self, months: int, aql_config: Dict) -> int:
        """Part 1: AQL 검사 평가 결과 인센티브 계산"""
        part1_config = aql_config.get('parts', {}).get('part1', {})
        amounts = part1_config.get('incentive_table', {}).get('sustained_performance', {}).get('amounts', {})
        
        # 문자열 키를 정수로 변환하여 조회
        return amounts.get(str(months), 150000)
    
    def calculate_aql_part2_amount(self, emp_id: str, aql_config: Dict) -> int:
        """Part 2: CFA 자격증 인센티브 계산"""
        # 직원별 CFA 자격증 보유 여부 확인
        if emp_id in aql_config.get('aql_inspectors', {}):
            if aql_config['aql_inspectors'][emp_id].get('cfa_certified', False):
                return aql_config.get('parts', {}).get('part2', {}).get('amount', 700000)
        return 0
    
    def calculate_aql_part3_amount(self, months: int, aql_config: Dict) -> int:
        """Part 3: HWK 클레임 방지 인센티브 계산"""
        part3_config = aql_config.get('parts', {}).get('part3', {})
        amounts = part3_config.get('incentive_table', {})
        
        # 문자열 키를 정수로 변환하여 조회
        return amounts.get(str(months), 0)
    
    def get_assembly_inspector_amount(self, continuous_months: int) -> int:
        """연속 충족 개월 수에 따른 Assembly Inspector 인센티브 금액 결정"""
        # 인센티브 금액 테이블
        incentive_table = {
            0: 150000,    # 처음 충족 또는 연속 끊김 후 재충족
            1: 150000,    # 1개월 연속
            2: 250000,    # 2개월 연속
            3: 300000,    # 3개월 연속
            4: 350000,    # 4개월 연속
            5: 400000,    # 5개월 연속
            6: 450000,    # 6개월 연속
            7: 500000,    # 7개월 연속
            8: 650000,    # 8개월 연속
            9: 750000,    # 9개월 연속
            10: 850000,   # 10개월 연속
            11: 950000,   # 11개월 연속
        }
        
        # 12개월 이상은 1,000,000 VND
        if continuous_months >= 12:
            return 1000000
        
        return incentive_table.get(continuous_months, 150000)
    
    def calculate_assembly_inspector_incentive_type1_only(self):
        """Type-1 Assembly Inspector 및 AQL Inspector 인센티브 계산
        
        10개 조건 체계 (4-4-2 구조):
        - 출근 조건 (4개): 출근율, 무단결근, 실제 근무일, 최소 12일
        - AQL 조건 (4개): 당월 실패, 3개월 연속(ASSEMBLY만), 부하직원(해당없음), 구역(해당없음)
        - 5PRS 조건 (2개): 검사량, 통과율
        
        ASSEMBLY INSPECTOR: 8/10 조건 적용 (6번 조건 포함)
        AQL INSPECTOR: 5/10 조건 적용 (6번 조건 제외)
        """
        print("\n👥 TYPE-1 ASSEMBLY/AQL INSPECTOR 인센티브 계산...")
        
        # Type-1 Assembly Inspector 필터링
        assembly_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('ASSEMBLY', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
        )
        
        # Type-1 AQL Inspector 필터링
        aql_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('AQL', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
        )
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # AQL Inspector 처리
        if aql_mask.any():
            self.calculate_aql_inspector_incentive(aql_mask, incentive_col, aql_col)
        
        # Assembly Inspector 처리
        for idx, row in self.month_data[assembly_mask].iterrows():
            # 이미 계산된 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            # Stop working 직원도 정상 계산 (제외하지 않음)
            
            # [조건 1-4] 출근 조건 체크 (4개)
            attendance_fail = (
                row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or  # 조건3: 실제근무일>0
                row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or  # 조건2: 무단결근≤2
                row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or  # 조건1: 출근율≥88%
                row.get('attendancy condition 4 - minimum working days') == 'yes'  # 조건4: 최소근무일≥12
            )
            
            # [조건 9-10] 5PRS 조건: 검사량 100개 이상 AND 통과율 95% 이상
            prs_pass = row.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%') == 'yes'
            
            # [조건 5] AQL 당월 실패 건수 0건
            aql_fail = row.get(aql_col, 0) > 0
            # [조건 6] ASSEMBLY INSPECTOR는 3개월 연속 실패 체크 적용
            continuous_fail = row.get('Continuous_FAIL', 'NO') == 'YES'
            
            # emp_id를 먼저 정의 (디버깅 목적으로 사용됨)
            emp_id = row.get('Employee No', '')
            
            # 인센티브 결정 로직 - 모든 조건 충족 시만 지급
            if attendance_fail:
                incentive = 0
            elif continuous_fail:  # 3개월 연속 AQL 실패
                incentive = 0
            elif aql_fail:  # 당월 AQL 실패
                incentive = 0
            elif not prs_pass:  # 5PRS 조건 미충족
                incentive = 0
            else:
                # 연속 충족 개월 수 계산
                continuous_months = self.data_processor.calculate_continuous_months_from_history(emp_id)
                
                # 연속 충족 개월 수에 따른 차등 지급
                incentive = self.get_assembly_inspector_amount(continuous_months)
                
                # 디버깅을 위한 출력
                if continuous_months > 0:
                    print(f"    → {row.get('Full Name', 'Unknown')} ({emp_id}): {continuous_months}개월 연속 → {incentive:,} VND")
            
            self.month_data.loc[idx, incentive_col] = incentive
            
            # 디버깅: 619060201 직원 확인
            if emp_id == '619060201':
                print(f"    [디버그] 619060201 업데이트: {incentive_col} = {incentive:,.0f} VND")
                actual_value = self.month_data.loc[idx, incentive_col]
                print(f"    [디버그] 실제 저장된 값: {actual_value:,.0f} VND")
        
        # 통계 출력
        receiving_count = (self.month_data[assembly_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[assembly_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def create_manager_subordinate_mapping(self) -> Dict[str, List[str]]:
        """관리자-부하 직원 매핑 생성"""
        print("\n📊 관리자-부하 직원 매핑 생성 중...")
        
        subordinate_mapping = {}
        
        # Direct boss name 칼럼 찾기
        boss_col = self.data_processor.detect_column_names(self.month_data, [
            'direct boss name', 'Direct Boss Name', 'DIRECT BOSS NAME',
            'Manager', 'MANAGER', 'Boss Name'
        ])
        
        if not boss_col:
            print("❌ 상사 정보 칼럼을 찾을 수 없습니다.")
            return subordinate_mapping
        
        for _, row in self.month_data.iterrows():
            boss_name = row.get(boss_col)
            if pd.notna(boss_name) and boss_name.strip():
                emp_id = row.get('Employee No', '')
                
                # 상사의 Employee No 찾기
                boss_data = self.month_data[
                    self.month_data.get('Full Name', '') == boss_name
                ]
                
                if not boss_data.empty:
                    boss_id = boss_data.iloc[0].get('Employee No', '')
                    if boss_id:
                        if boss_id not in subordinate_mapping:
                            subordinate_mapping[boss_id] = []
                        subordinate_mapping[boss_id].append(emp_id)
        
        print(f"✅ 매핑 완료: {len(subordinate_mapping)} 명의 관리자")
        return subordinate_mapping
    
    def calculate_line_leader_incentive_type1_only(self, subordinate_mapping: Dict[str, List[str]]):
        """Type-1 Line Leader 인센티브 계산"""
        print("\n👥 TYPE-1 LINE LEADER 인센티브 계산 (7% 적용 + 인센티브 수령 비율 반영)...")
        
        # Type-1 Line Leader 필터링
        line_leader_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
        )
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        for idx, row in self.month_data[line_leader_mask].iterrows():
            # 이미 계산된 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            leader_id = row.get('Employee No', '')
            
            # 출근 조건 체크 - 모든 직급에 공통 적용
            attendance_fail = (
                row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
                row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
                row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
                row.get('attendancy condition 4 - minimum working days') == 'yes'
            )
            
            # 출근 조건 미충족 시 인센티브 0
            if attendance_fail:
                incentive = 0
                print(f"    → Line Leader {row.get('Full Name', 'Unknown')} ({leader_id}): 출근 조건 미충족")
            # 부하직원 인센티브 계산
            elif leader_id in subordinate_mapping:
                subordinates = subordinate_mapping[leader_id]
                total_sub_incentive = 0
                receiving_count = 0  # 인센티브 받는 직원 수
                total_count = 0      # 전체 부하직원 수
                
                for sub_id in subordinates:
                    sub_data = self.month_data[self.month_data['Employee No'] == sub_id]
                    if not sub_data.empty:
                        sub_row = sub_data.iloc[0]
                        # Type-1 부하직원만 계산
                        if sub_row.get('ROLE TYPE STD') == 'TYPE-1':
                            total_count += 1
                            sub_incentive = float(sub_row.get(incentive_col, 0))
                            if sub_incentive > 0:
                                receiving_count += 1
                                total_sub_incentive += sub_incentive
                
                # 부하직원 중 3개월 연속 AQL 실패자 확인
                has_continuous_fail = self.check_subordinates_continuous_fail(leader_id, subordinate_mapping)
                
                if has_continuous_fail:
                    incentive = 0
                    print(f"    → Line Leader {row.get('Full Name', 'Unknown')}: 부하직원 중 3개월 연속 AQL 실패자 있음")
                elif total_count > 0 and receiving_count > 0:
                    # 7% 계산 및 인센티브 수령 비율 반영
                    receiving_ratio = receiving_count / total_count
                    incentive = int(total_sub_incentive * 0.07 * receiving_ratio)
                else:
                    incentive = 0
            else:
                incentive = 0
            
            self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력
        receiving_count = (self.month_data[line_leader_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[line_leader_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def calculate_head_incentive(self, subordinate_mapping: Dict[str, List[str]]):
        """Type-1 Head(Group Leader) 인센티브 계산
        
        10개 조건 체계 중 4/10 조건만 적용:
        - 출근 조건 (4개): 출근율, 무단결근, 실제 근무일, 최소 12일
        - AQL 조건 (4개): 모두 미적용 (부하직원 조건도 미적용)
        - 5PRS 조건 (2개): 모두 미적용
        
        GROUP LEADER: 4/10 조건 적용 (출근 조건만)
        """
        print("\n👥 TYPE-1 HEAD(GROUP LEADER) 인센티브 계산 (Line Leader 평균 × 2)...")
        
        # Type-1 Head/Group Leader 필터링
        head_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            ((self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('HEAD', na=False)) |
             (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('GROUP', na=False) & 
              self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False)))
        )
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        for idx, row in self.month_data[head_mask].iterrows():
            # 이미 계산된 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            head_id = row.get('Employee No', '')
            
            # 출근 조건 체크 - 모든 직급에 공통 적용
            attendance_fail = (
                row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
                row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
                row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
                row.get('attendancy condition 4 - minimum working days') == 'yes'
            )
            
            # 출근 조건 미충족 시 인센티브 0
            if attendance_fail:
                incentive = 0
                print(f"    → Head/Group Leader {row.get('Full Name', 'Unknown')} ({head_id}): 출근 조건 미충족")
            else:
                # 자신의 팀 내 Line Leader들 찾기 및 평균 계산
                line_leaders = self._find_team_line_leaders(head_id, subordinate_mapping)
                
                if line_leaders:
                    avg_incentive = self._calculate_line_leader_average_unified(
                        line_leaders, head_id, 'HEAD'
                    )
                    # Line Leader 평균의 2배
                    incentive = int(avg_incentive * 2)
                else:
                    incentive = 0
            
            self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력
        receiving_count = (self.month_data[head_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[head_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def calculate_managers_by_manual_logic_fixed(self, subordinate_mapping: Dict[str, List[str]]):
        """관리자 인센티브 계산"""
        print("\n👔 관리자 인센티브 계산...")
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        # 각 관리자 직급별로 처리 - 정확한 직급명 매칭 사용
        manager_configs = [
            {'position_names': ['S.MANAGER', 'SENIOR MANAGER'], 'multiplier': 4.0, 'name': 'Senior Manager'},
            {'position_names': ['MANAGER'], 'multiplier': 3.5, 'name': 'Manager'},
            {'position_names': ['A.MANAGER', 'ASSISTANT MANAGER'], 'multiplier': 3.0, 'name': 'Assistant Manager'},
            {'position_names': ['(V) SUPERVISOR', 'VICE SUPERVISOR', 'V.SUPERVISOR'], 'multiplier': 2.5, 'name': '(Vice) Supervisor'},
            {'position_names': ['SUPERVISOR'], 'multiplier': 2.5, 'name': 'Supervisor'},
        ]
        
        for config in manager_configs:
            print(f"\n  🔹 {config['name']} 계산 중...")
            
            # 해당 직급 필터링 - 정확한 직급명 매칭
            mask = (self.month_data['ROLE TYPE STD'] == 'TYPE-1') & (
                self.month_data['QIP POSITION 1ST  NAME'].isin(config['position_names'])
            )
            
            for idx in self.month_data[mask].index:
                row = self.month_data.loc[idx]
                
                # 이미 계산된 경우 스킵
                if row[incentive_col] > 0:
                    continue
                
                manager_id = row.get('Employee No', '')
                
                # 출근 조건 체크 - 모든 직급에 공통 적용
                attendance_fail = (
                    row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
                    row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
                    row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
                    row.get('attendancy condition 4 - minimum working days') == 'yes'
                )
                
                # 출근 조건 미충족 시 인센티브 0
                if attendance_fail:
                    incentive = 0
                    print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): 출근 조건 미충족")
                else:
                    # 자신의 팀 내 Line Leader들의 평균 계산
                    line_leaders = self._find_team_line_leaders(manager_id, subordinate_mapping)
                    
                    if line_leaders:
                        avg_incentive = self._calculate_line_leader_average_unified(
                            line_leaders, manager_id, config['name']
                        )
                        # Line Leader 평균에 배수 적용
                        incentive = int(avg_incentive * config['multiplier'])
                    else:
                        incentive = 0
                
                self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력 - 모든 관리자 대상
        # 관리자 마스크 생성
        manager_mask = pd.Series([False] * len(self.month_data))
        for config in manager_configs:
            temp_mask = (self.month_data['ROLE TYPE STD'] == 'TYPE-1') & (
                self.month_data['QIP POSITION 1ST  NAME'].isin(config['position_names'])
            )
            manager_mask |= temp_mask
        
        receiving_count = (self.month_data[manager_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[manager_mask][incentive_col].sum()
        print(f"  → 관리자 총 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def _find_team_line_leaders(self, manager_id: str, subordinate_mapping: Dict[str, List[str]]) -> List:
        """팀 내 모든 Line Leader 찾기 (직접 부하 + 부하의 부하)"""
        line_leaders = []
        visited = set()
        
        def find_line_leaders_recursive(boss_id: str, depth: int = 0):
            if depth > 5 or boss_id in visited:  # 무한 루프 방지
                return
            visited.add(boss_id)
            
            if boss_id in subordinate_mapping:
                for sub_id in subordinate_mapping[boss_id]:
                    sub_data = self.month_data[self.month_data['Employee No'] == sub_id]
                    if not sub_data.empty:
                        sub_row = sub_data.iloc[0]
                        position = str(sub_row.get('QIP POSITION 1ST  NAME', '')).upper()
                        role_type = sub_row.get('ROLE TYPE STD', '')
                        
                        if (role_type == 'TYPE-1' and 
                            'LINE' in position and 'LEADER' in position):
                            line_leaders.append(sub_row.to_dict())
                        
                        # 재귀적으로 부하의 부하 탐색
                        find_line_leaders_recursive(sub_id, depth + 1)
        
        find_line_leaders_recursive(manager_id)
        return line_leaders
    
    def _calculate_line_leader_average_unified(self, line_leaders: List, manager_id: str, position: str) -> float:
        """Line Leader 평균 인센티브 계산"""
        if not line_leaders:
            return 0
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        total_incentive = 0
        count = 0
        
        for leader in line_leaders:
            if isinstance(leader, dict):
                current_incentive = float(leader.get(incentive_col, 0))
            else:
                current_leader_data = self.month_data[
                    self.month_data['Employee No'] == leader
                ]
                if not current_leader_data.empty:
                    current_incentive = float(current_leader_data.iloc[0].get(incentive_col, 0))
                else:
                    current_incentive = 0
            
            if current_incentive > 0:
                total_incentive += current_incentive
                count += 1
        
        if count > 0:
            return total_incentive / count
        return 0
    
    def calculate_type2_incentive(self):
        """Type-2 인센티브 계산"""
        print("\n📊 TYPE-2 인센티브 계산...")
        
        type2_mask = self.month_data['ROLE TYPE STD'] == 'TYPE-2'
        
        # Type-1 참조 맵 생성
        type1_reference = self._create_type1_reference_map()
        
        # TYPE-2 포지션 매칭 규칙 로드
        type2_mapping = self.load_type2_position_mapping()
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        for idx, row in self.month_data[type2_mask].iterrows():
            # 이미 계산된 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            position = row.get('QIP POSITION 1ST  NAME', '')
            position_upper = position.upper() if pd.notna(position) else ''
            
            # Stop Working Date 체크 추가
            stop_working_check = False
            if 'Stop working Date' in row.index:
                stop_date_str = row.get('Stop working Date')
                if pd.notna(stop_date_str) and stop_date_str != '':
                    try:
                        if '.' in str(stop_date_str):
                            stop_date = pd.to_datetime(stop_date_str, format='%Y.%m.%d', errors='coerce')
                        else:
                            stop_date = pd.to_datetime(stop_date_str, errors='coerce')
                        
                        calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
                        if pd.notna(stop_date) and stop_date < calc_month_start:
                            stop_working_check = True
                    except:
                        pass
            
            # TYPE-2는 출근 조건만 체크 (AQL, 5PRS 조건 제외)
            attendance_fail = (
                stop_working_check or  # Stop Working Date 체크 추가
                row.get('attendancy condition 1 - acctual working days is zero') == 'yes' or
                row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes' or
                row.get('attendancy condition 3 - absent % is over 12%') == 'yes' or
                row.get('attendancy condition 4 - minimum working days') == 'yes'  # 최소 12일 근무 조건 추가
            )
            
            # 출근 조건 미충족 시 0원
            if attendance_fail:
                incentive = 0
            else:
                # 매칭된 TYPE-1 포지션 찾기
                mapped_position = self.get_mapped_type1_position(position_upper, row, type2_mapping)
                
                if mapped_position and mapped_position in type1_reference:
                    incentive = type1_reference[mapped_position]
                elif position_upper in type1_reference:
                    # 직접 매칭
                    incentive = type1_reference[position_upper]
                else:
                    incentive = 0
                    print(f"  ⚠️ TYPE-2 '{position}'에 대한 매칭 실패 → 0원")
            
            self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력
        receiving_count = (self.month_data[type2_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[type2_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def load_type2_position_mapping(self) -> Dict:
        """TYPE-2 포지션 매칭 규칙 로드"""
        try:
            # 프로젝트 루트에서 매핑 파일 로드
            import os
            mapping_path = 'config_files/type2_position_mapping.json'
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ TYPE-2 매칭 규칙 파일을 찾을 수 없습니다: {mapping_path}")
        except Exception as e:
            print(f"⚠️ TYPE-2 매칭 규칙 로드 중 오류: {e}")
        return {}
    
    def get_mapped_type1_position(self, position: str, row: pd.Series, mapping: Dict) -> str:
        """TYPE-2 포지션에 대한 TYPE-1 매칭 포지션 반환"""
        if not mapping:
            return ''
        
        # position_mappings 가져오기
        position_mappings = mapping.get('position_mappings', {})
        
        # QA TEAM 특별 처리
        if position == 'QA TEAM':
            qip_code = row.get('FINAL QIP POSITION NAME CODE', '')
            qa_mapping = position_mappings.get('QA TEAM', {})
            
            if qip_code == 'QA3A' and 'QA3A' in qa_mapping:
                return qa_mapping['QA3A'].get('mapped_to', '').upper()
            elif qip_code == 'QA3B' and 'QA3B' in qa_mapping:
                return qa_mapping['QA3B'].get('mapped_to', '').upper()
            elif 'default' in qa_mapping:
                return qa_mapping['default'].get('mapped_to', '').upper()
            else:
                # 기본값: Assembly Inspector
                return 'ASSEMBLY INSPECTOR'
        
        # 일반 포지션 매칭
        if position in position_mappings:
            mapping_info = position_mappings[position]
            if isinstance(mapping_info, dict) and 'mapped_to' in mapping_info:
                return mapping_info['mapped_to'].upper()
        
        return ''
    
    def _create_type1_reference_map(self) -> Dict[str, int]:
        """Type-1 참조 맵 생성"""
        reference_map = {}
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        type1_mask = self.month_data['ROLE TYPE STD'] == 'TYPE-1'
        
        # 포지션별 평균 계산
        for position in self.month_data[type1_mask]['QIP POSITION 1ST  NAME'].unique():
            if pd.notna(position):
                pos_employees = self.month_data[
                    (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                    (self.month_data['QIP POSITION 1ST  NAME'] == position)
                ]
                
                receiving_employees = pos_employees[pos_employees[incentive_col] > 0]
                
                if len(receiving_employees) > 0:
                    avg_incentive = int(receiving_employees[incentive_col].mean())
                    reference_map[position.upper()] = avg_incentive
        
        return reference_map
    
    def calculate_type3_incentive(self):
        """Type-3 인센티브 계산"""
        print("\n📊 TYPE-3 인센티브 계산...")
        
        type3_mask = self.month_data['ROLE TYPE STD'] == 'TYPE-3'
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        # Type-3는 인센티브 없음
        for idx in self.month_data[type3_mask].index:
            self.month_data.loc[idx, incentive_col] = 0
        
        print(f"  → Type-3 직원들은 인센티브를 받지 않습니다.")
    
    def generate_summary(self):
        """계산 결과 요약"""
        print(f"\n{'='*60}")
        print(f"📊 {self.config.get_month_str('korean')} QIP 인센티브 계산 결과 요약")
        print('='*60)
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        # 전체 통계 - Employee No가 있는 실제 직원만 계산
        valid_employees = self.month_data[self.month_data['Employee No'].notna()]
        
        # 계산 월 이전 퇴사자 제외
        calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
        if 'Stop working Date' in valid_employees.columns:
            valid_employees['Stop working Date'] = pd.to_datetime(valid_employees['Stop working Date'], errors='coerce')
            active_employees = valid_employees[
                (valid_employees['Stop working Date'].isna()) |  # 퇴사일 없는 직원
                (valid_employees['Stop working Date'] >= calc_month_start)  # 계산 월 이후 퇴사자
            ]
        else:
            active_employees = valid_employees
        
        total_employees = len(active_employees)
        receiving_employees = (active_employees[incentive_col] > 0).sum()
        total_amount = active_employees[incentive_col].sum()
        
        print(f"\n📌 전체 현황:")
        print(f"  • 전체 직원: {total_employees}명")
        print(f"  • 수령 직원: {receiving_employees}명 ({receiving_employees/total_employees*100:.1f}%)")
        print(f"  • 총 지급액: {total_amount:,.0f} VND")
        
        if receiving_employees > 0:
            avg_receiving = self.month_data[self.month_data[incentive_col] > 0][incentive_col].mean()
            print(f"  • 평균 지급액: {avg_receiving:,.0f} VND")
        
        # Type별 통계
        print(f"\n📌 Type별 현황:")
        for role_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
            type_data = self.month_data[self.month_data['ROLE TYPE STD'] == role_type]
            if not type_data.empty:
                type_total = len(type_data)
                type_receiving = (type_data[incentive_col] > 0).sum()
                type_not_receiving = type_total - type_receiving
                type_amount = type_data[incentive_col].sum()
                type_avg = type_data[type_data[incentive_col] > 0][incentive_col].mean() if type_receiving > 0 else 0
                
                print(f"\n  {role_type}:")
                print(f"    • 총 인원: {type_total}명")
                print(f"    • 수령 인원: {type_receiving}명")
                print(f"    • 미수령 인원: {type_not_receiving}명")
                print(f"    • 수령률: {type_receiving/type_total*100:.1f}%")
                print(f"    • 총 지급액: {type_amount:,.0f} VND")
                if type_receiving > 0:
                    print(f"    • 평균 지급액: {type_avg:,.0f} VND")
                
                # 직급별 상세 통계
                print(f"\n    📊 {role_type} 직급별 상세:")
                position_col = 'QIP POSITION 1ST  NAME'
                if position_col in type_data.columns:
                    positions = type_data.groupby(position_col).agg({
                        incentive_col: ['count', lambda x: (x > 0).sum(), 'sum', 
                                       lambda x: x[x > 0].mean() if (x > 0).sum() > 0 else 0]
                    }).round(0)
                    positions.columns = ['총원', '수령인원', '총지급액', '평균지급액']
                    positions['미수령인원'] = positions['총원'] - positions['수령인원']
                    positions['수령률'] = (positions['수령인원'] / positions['총원'] * 100).round(1)
                    
                    # 수령인원이 많은 순으로 정렬
                    positions = positions.sort_values('수령인원', ascending=False)
                    
                    for position, row in positions.head(10).iterrows():
                        if row['총원'] > 0:
                            print(f"      • {position}:")
                            print(f"        - 총원: {int(row['총원'])}명, 수령: {int(row['수령인원'])}명, 미수령: {int(row['미수령인원'])}명")
                            print(f"        - 수령률: {row['수령률']}%, 총액: {row['총지급액']:,.0f} VND")
                            if row['수령인원'] > 0:
                                print(f"        - 평균: {row['평균지급액']:,.0f} VND")
    
    def save_results(self):
        """결과 저장"""
        print(f"\n💾 결과 파일 저장 중...")
        
        try:
            # output_files 폴더 생성
            import os
            import shutil
            import json
            output_dir = "output_files"
            os.makedirs(output_dir, exist_ok=True)
            
            # 이전 달 인센티브 데이터를 병합
            if self.config.previous_months:
                prev_month = self.config.previous_months[-1]
                prev_file_path = f"input_files/{self.config.year}년 {prev_month.number}월 인센티브 지급 세부 정보.csv"
                
                if os.path.exists(prev_file_path):
                    try:
                        prev_incentive_data = pd.read_csv(prev_file_path, encoding='utf-8-sig')
                        
                        # 직원번호로 6월 인센티브 매칭
                        if 'June_Incentive' in prev_incentive_data.columns:
                            # Employee No를 숫자로 변환하여 매핑
                            prev_incentive_data['Employee No'] = pd.to_numeric(prev_incentive_data['Employee No'], errors='coerce')
                            self.month_data['Employee No'] = pd.to_numeric(self.month_data['Employee No'], errors='coerce')
                            
                            prev_incentive_map = prev_incentive_data.set_index('Employee No')['June_Incentive'].to_dict()
                            self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)
                            print(f"  → {prev_month.korean_name} 인센티브 매핑 완료: {len(prev_incentive_map)} 건")
                            # 디버그: 618030024 확인
                            if 618030024 in prev_incentive_map:
                                print(f"    618030024의 {prev_month.korean_name} 인센티브: {prev_incentive_map[618030024]}")
                            # Employee No 타입 확인 및 변환
                            print(f"    Employee No 타입: {self.month_data['Employee No'].dtype}")
                            emp_data = self.month_data[self.month_data['Employee No'] == 618030024]
                            if not emp_data.empty:
                                print(f"    매핑 후 Previous_Incentive: {emp_data['Previous_Incentive'].values[0]}")
                            else:
                                print(f"    618030024 직원을 찾을 수 없음")
                        elif f'{prev_month.full_name.capitalize()}_Incentive' in prev_incentive_data.columns:
                            col_name = f'{prev_month.full_name.capitalize()}_Incentive'
                            prev_incentive_map = prev_incentive_data.set_index('Employee No')[col_name].to_dict()
                            self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)
                        else:
                            self.month_data['Previous_Incentive'] = 0
                    except Exception as e:
                        print(f"  ⚠️ {prev_month.korean_name} 인센티브 데이터 로드 실패: {e}")
                        self.month_data['Previous_Incentive'] = 0
                else:
                    self.month_data['Previous_Incentive'] = 0
            else:
                self.month_data['Previous_Incentive'] = 0
            
            incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
            
            # Final Incentive amount 칼럼을 July_Incentive 값으로 덮어쓰기
            self.month_data['Final Incentive amount'] = self.month_data[incentive_col].copy()
            
            # CSV 저장
            csv_file = os.path.join(output_dir, f"{self.config.output_prefix}_최종완성버전_v6.0_Complete.csv")
            self.month_data.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            # CSV 파일 생성 검증
            if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
                print(f"✅ CSV 파일 저장 완료: {csv_file}")
            else:
                print(f"⚠️ CSV 파일 생성 실패: {csv_file}")
            
            # Excel 저장
            excel_file = os.path.join(output_dir, f"{self.config.output_prefix}_최종완성버전_v6.0_Complete.xlsx")
            self.month_data.to_excel(excel_file, index=False)
            
            # Excel 파일 생성 검증
            if os.path.exists(excel_file) and os.path.getsize(excel_file) > 0:
                print(f"✅ Excel 파일 저장 완료: {excel_file}")
            else:
                print(f"⚠️ Excel 파일 생성 실패: {excel_file}")
            
            # 메타데이터 저장 (조건 충족 상세 정보)
            metadata_file = self.save_calculation_metadata(output_dir)
            if metadata_file:
                print(f"✅ 메타데이터 파일 저장 완료: {metadata_file}")
            
            # HTML 리포트 생성 (비활성화 - dashboard_version4.html만 사용)
            # html_file = self.generate_html_report()
            # if html_file:
            #     print(f"✅ HTML 리포트 생성 완료: {html_file}")
            print("ℹ️ HTML Report 생성 건너뜀 (dashboard_version4.html만 사용)")
            
            # 다음 달 계산용 파일 자동 생성
            self.prepare_next_month_file(csv_file)
            
            return True
        except Exception as e:
            print(f"❌ 파일 저장 중 오류: {e}")
            traceback.print_exc()
            return False
    
    def save_calculation_metadata(self, output_dir: str) -> Optional[str]:
        """계산 메타데이터를 JSON으로 저장 (조건 충족 상세 정보 포함)"""
        try:
            import json
            import os
            
            metadata = {}
            incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
            
            for _, row in self.month_data.iterrows():
                emp_id = str(row['Employee No'])
                amount = row[incentive_col] if pd.notna(row[incentive_col]) else 0
                
                # 기본 정보
                # Position 컬럼 동적 처리
                position_value = ''
                if 'QIP POSITION 1ST  NAME' in row.index:
                    position_value = row['QIP POSITION 1ST  NAME']
                elif 'Position' in row.index:
                    position_value = row['Position']
                elif 'POSITION' in row.index:
                    position_value = row['POSITION']
                
                emp_metadata = {
                    'name': row['Full Name'],
                    'position': position_value,
                    'type': row['ROLE TYPE STD'],
                    'amount': float(amount),
                    'calculation_basis': '',
                    'conditions': {}
                }
                
                # 조건 충족 정보 구성
                # 출근 조건
                emp_metadata['conditions']['attendance'] = {
                    'attendance_rate': {
                        'passed': row.get('Absence Rate (raw)', 0) <= 12 if pd.notna(row.get('Absence Rate (raw)')) else True,
                        'value': 100 - row.get('Absence Rate (raw)', 0) if pd.notna(row.get('Absence Rate (raw)')) else 100,
                        'threshold': 88,
                        'applicable': True
                    },
                    'unapproved_absence': {
                        'passed': row.get('Unapproved Absence Days', 0) <= 2 if pd.notna(row.get('Unapproved Absence Days')) else True,
                        'value': int(row.get('Unapproved Absence Days', 0)) if pd.notna(row.get('Unapproved Absence Days')) else 0,
                        'threshold': 2,
                        'applicable': True
                    },
                    'working_days': {
                        'passed': row.get('Actual Working Days', 0) > 0 if pd.notna(row.get('Actual Working Days')) else False,
                        'value': int(row.get('Actual Working Days', 0)) if pd.notna(row.get('Actual Working Days')) else 0,
                        'threshold': 1,
                        'applicable': True
                    },
                    'minimum_days': {
                        'passed': row.get('Actual Working Days', 0) >= 12 if pd.notna(row.get('Actual Working Days')) else False,
                        'value': int(row.get('Actual Working Days', 0)) if pd.notna(row.get('Actual Working Days')) else 0,
                        'threshold': 12,
                        'applicable': True
                    }
                }
                
                # AQL 조건 (TYPE-1만)
                if row['ROLE TYPE STD'] == 'TYPE-1':
                    # AQL INSPECTOR 특별 처리
                    if 'AQL INSPECTOR' in str(position_value):
                        emp_metadata['conditions']['aql'] = {
                            'monthly_failure': {
                                'passed': amount > 0,  # 인센티브를 받았으면 통과로 간주
                                'value': 0 if amount > 0 else int(row.get('July AQL Failures', 0)) if pd.notna(row.get('July AQL Failures')) else 0,
                                'threshold': 0,
                                'applicable': True
                            },
                            '3month_continuous': {'applicable': False},
                            'subordinate_aql': {'applicable': False},
                            'area_reject_rate': {'applicable': False}
                        }
                        emp_metadata['calculation_basis'] = 'AQL Inspector 3-part incentive'
                    else:
                        emp_metadata['conditions']['aql'] = {
                            'monthly_failure': {
                                'passed': row.get('July AQL Failures', 0) == 0 if pd.notna(row.get('July AQL Failures')) else True,
                                'value': int(row.get('July AQL Failures', 0)) if pd.notna(row.get('July AQL Failures')) else 0,
                                'threshold': 0,
                                'applicable': True
                            },
                            '3month_continuous': {
                                'passed': row.get('Continuous_FAIL', 'NO') != 'YES' if pd.notna(row.get('Continuous_FAIL')) else True,
                                'value': row.get('Continuous_FAIL', 'NO'),
                                'threshold': 'NO',
                                'applicable': True
                            }
                        }
                
                # 5PRS 조건 (TYPE-1, TYPE-2 일부)
                if row['ROLE TYPE STD'] in ['TYPE-1', 'TYPE-2'] and 'AQL INSPECTOR' not in str(position_value):
                    emp_metadata['conditions']['5prs'] = {
                        'volume': {
                            'passed': row.get('Total Valiation Qty', 0) >= 100 if pd.notna(row.get('Total Valiation Qty')) else False,
                            'value': int(row.get('Total Valiation Qty', 0)) if pd.notna(row.get('Total Valiation Qty')) else 0,
                            'threshold': 100,
                            'applicable': True
                        },
                        'pass_rate': {
                            'passed': row.get('Pass %', 0) >= 95 if pd.notna(row.get('Pass %')) else False,
                            'value': float(row.get('Pass %', 0)) if pd.notna(row.get('Pass %')) else 0,
                            'threshold': 95,
                            'applicable': True
                        }
                    }
                else:
                    emp_metadata['conditions']['5prs'] = {'applicable': False}
                
                metadata[emp_id] = emp_metadata
            
            # JSON 파일로 저장
            metadata_file = os.path.join(output_dir, f"{self.config.output_prefix}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 파일 생성 검증
            if os.path.exists(metadata_file) and os.path.getsize(metadata_file) > 0:
                return metadata_file
            else:
                print(f"⚠️ 메타데이터 파일 생성 실패: {metadata_file}")
                return None
            
        except Exception as e:
            print(f"  ⚠️ 메타데이터 저장 실패: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def prepare_next_month_file(self, csv_file_path):
        """다음 달 계산용 파일 자동 생성 (월 자동 순환 포함)"""
        try:
            import shutil
            import os
            from datetime import datetime
            
            # 월 이름 매핑
            month_korean = {
                'january': '1월', 'february': '2월', 'march': '3월',
                'april': '4월', 'may': '5월', 'june': '6월',
                'july': '7월', 'august': '8월', 'september': '9월',
                'october': '10월', 'november': '11월', 'december': '12월'
            }
            
            # 월 순서 매핑 (자동 순환용)
            month_order = [
                'january', 'february', 'march', 'april', 'may', 'june',
                'july', 'august', 'september', 'october', 'november', 'december'
            ]
            
            # 현재 월 인덱스 찾기
            current_month_name = self.config.month.full_name.lower()
            current_month_index = month_order.index(current_month_name)
            current_year = self.config.year
            
            # 다음 달 계산 (12월 → 1월 자동 처리)
            if current_month_index == 11:  # 12월인 경우
                next_month_index = 0  # 1월로
                next_year = current_year + 1  # 연도 증가
                print(f"  📅 연도 전환: {current_year}년 12월 → {next_year}년 1월")
            else:
                next_month_index = current_month_index + 1
                next_year = current_year
            
            next_month_name = month_order[next_month_index]
            next_korean_month = month_korean[next_month_name]
            
            # 현재 월의 한글 이름 (저장용)
            current_korean_month = month_korean.get(current_month_name, self.config.month.korean_name)
            
            # input_files 폴더 생성
            os.makedirs("input_files", exist_ok=True)
            os.makedirs("input_files/backup", exist_ok=True)
            
            # 현재 월 파일 (이전 월 데이터로 사용될 파일)
            target_file = f"input_files/{current_year}년 {current_korean_month} 인센티브 지급 세부 정보.csv"
            
            # 기존 파일 백업
            if os.path.exists(target_file):
                backup_file = f"input_files/backup/{current_year}년 {current_korean_month} 인센티브 지급 세부 정보_backup.csv"
                shutil.copy2(target_file, backup_file)
                print(f"  📦 기존 파일 백업: {backup_file}")
            
            # 파일 복사
            shutil.copy2(csv_file_path, target_file)
            print(f"\n🎯 다음 달 계산용 파일 자동 생성:")
            print(f"  → {target_file}")
            print(f"  ℹ️ {next_year}년 {next_korean_month} 계산 시 이 파일이 자동으로 사용됩니다.")
            
            # 다음 달 설정 정보 생성 (선택적)
            next_month_info = f"""
📌 다음 달({next_year}년 {next_korean_month}) 계산 준비 완료:
   - 이전 월 데이터: {current_year}년 {current_korean_month} ✅
   - 필요한 파일:
     • basic manpower data {next_month_name}.csv
     • aql data {next_month_name}.csv
     • 5prs data {next_month_name}.csv
     • attendance data {next_month_name}.csv
            """
            print(next_month_info)
            
        except Exception as e:
            print(f"  ⚠️ 다음 달 파일 자동 생성 실패: {e}")
            print(f"     수동으로 파일명을 변경해주세요.")
    
    def generate_html_report(self) -> Optional[str]:
        """HTML 리포트 생성 (개선된 버전)"""
        try:
            month_str = self.config.get_month_str('capital')
            month_kr = self.config.get_month_str('korean')
            incentive_col = f"{month_str}_Incentive"
            
            # Previous_Incentive 컬럼이 이미 있는지 확인 (save_results에서 추가됨)
            if 'Previous_Incentive' not in self.month_data.columns:
                # 이전 달 인센티브 데이터 로드 (6월 데이터)
                prev_incentive_data = None
                if self.config.previous_months:
                    prev_month = self.config.previous_months[-1]  # 마지막 이전 달 (6월)
                    prev_file_path = f"input_files/{self.config.year}년 {prev_month.number}월 인센티브 지급 세부 정보.csv"
                    
                    import os
                    if os.path.exists(prev_file_path):
                        try:
                            prev_incentive_data = pd.read_csv(prev_file_path, encoding='utf-8-sig')
                            print(f"  ✅ {prev_month.korean_name} 인센티브 데이터 로드 성공")
                            
                            # 직원번호로 6월 인센티브 매칭
                            if 'June_Incentive' in prev_incentive_data.columns:
                                prev_incentive_map = prev_incentive_data.set_index('Employee No')['June_Incentive'].to_dict()
                                self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)
                            elif f'{prev_month.full_name.capitalize()}_Incentive' in prev_incentive_data.columns:
                                col_name = f'{prev_month.full_name.capitalize()}_Incentive'
                                prev_incentive_map = prev_incentive_data.set_index('Employee No')[col_name].to_dict()
                                self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)
                            else:
                                print(f"  ⚠️ {prev_month.korean_name} 인센티브 컬럼을 찾을 수 없습니다")
                                self.month_data['Previous_Incentive'] = 0
                        except Exception as e:
                            print(f"  ⚠️ {prev_month.korean_name} 인센티브 데이터 로드 실패: {e}")
                            self.month_data['Previous_Incentive'] = 0
                    else:
                        print(f"  ⚠️ {prev_month.korean_name} 인센티브 파일이 없습니다: {prev_file_path}")
                        self.month_data['Previous_Incentive'] = 0
                else:
                    self.month_data['Previous_Incentive'] = 0
            
            # 통계 계산 - Employee No가 있는 실제 직원만
            valid_employees = self.month_data[self.month_data['Employee No'].notna()]
            
            # 계산 월 이전 퇴사자 제외
            calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
            if 'Stop working Date' in valid_employees.columns:
                valid_employees['Stop working Date'] = pd.to_datetime(valid_employees['Stop working Date'], errors='coerce')
                active_employees = valid_employees[
                    (valid_employees['Stop working Date'].isna()) |  # 퇴사일 없는 직원
                    (valid_employees['Stop working Date'] >= calc_month_start)  # 계산 월 이후 퇴사자
                ]
            else:
                active_employees = valid_employees
            
            total_employees = len(active_employees)
            receiving_employees = (active_employees[incentive_col] > 0).sum()
            total_amount = active_employees[incentive_col].sum()
            
            # 이전 월 인센티브 칼럼명 찾기
            prev_incentive_col = 'Previous_Incentive' if 'Previous_Incentive' in valid_employees.columns else None
            prev_month_kr = self.config.previous_months[-1].korean_name if self.config.previous_months else "이전월"
            
            # HTML 템플릿
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 계산 결과 리포트 - {self.config.year}년 {month_kr}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            border-left: 4px solid #667eea;
        }}
        
        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .summary-card .unit {{
            font-size: 0.8em;
            color: #666;
            margin-left: 5px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 500;
        }}
        
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
        }}
        
        .type-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .type-1 {{ background: #e8f5e8; color: #2e7d2e; }}
        .type-2 {{ background: #e8f0ff; color: #1e3a8a; }}
        .type-3 {{ background: #fff5e8; color: #9a3412; }}
        
        .filter-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .filter-row {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            flex: 1;
            min-width: 150px;
        }}
        
        .filter-button {{
            padding: 8px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
        
        .filter-button:hover {{
            background: #5a67d8;
        }}
        
        .detail-table {{
            width: 100%;
            font-size: 0.9em;
            margin-top: 20px;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .detail-table th {{
            position: sticky;
            top: 0;
            background: #667eea;
            z-index: 10;
        }}
        
        .highlight {{
            background: #fffacd !important;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}
        
        .tab:hover {{
            background: #f5f5f5;
        }}
        
        .tab.active {{
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: bold;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
    </style>
    <script>
        function filterTable() {{
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const positionFilter = document.getElementById('positionFilter').value.toLowerCase();
            const table = document.getElementById('detailTable');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {{
                const row = rows[i];
                const cells = row.getElementsByTagName('td');
                
                const empNo = cells[0]?.textContent.toLowerCase() || '';
                const name = cells[1]?.textContent.toLowerCase() || '';
                const position = cells[2]?.textContent.toLowerCase() || '';
                const type = cells[3]?.textContent || '';
                
                const matchSearch = empNo.includes(searchInput) || name.includes(searchInput);
                const matchType = typeFilter === '' || type.includes(typeFilter);
                const matchPosition = positionFilter === '' || position.includes(positionFilter);
                
                if (matchSearch && matchType && matchPosition) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }}
        }}
        
        function showTab(tabName) {{
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {{
                if (tab.dataset.tab === tabName) {{
                    tab.classList.add('active');
                }} else {{
                    tab.classList.remove('active');
                }}
            }});
            
            contents.forEach(content => {{
                if (content.id === tabName) {{
                    content.classList.add('active');
                }} else {{
                    content.classList.remove('active');
                }}
            }});
        }}
        
        window.onload = function() {{
            showTab('summary');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>QIP 인센티브 계산 결과</h1>
            <p>{self.config.year}년 {month_kr} | 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>전체 직원</h3>
                    <div class="value">{total_employees}<span class="unit">명</span></div>
                </div>
                <div class="summary-card">
                    <h3>수령 직원</h3>
                    <div class="value">{receiving_employees}<span class="unit">명</span></div>
                </div>
                <div class="summary-card">
                    <h3>수령률</h3>
                    <div class="value">{receiving_employees/total_employees*100:.1f}<span class="unit">%</span></div>
                </div>
                <div class="summary-card">
                    <h3>총 지급액</h3>
                    <div class="value">{total_amount/1000000:.1f}<span class="unit">M VND</span></div>
                </div>
            </div>
            
            <!-- 탭 메뉴 -->
            <div class="tabs">
                <div class="tab active" data-tab="summary" onclick="showTab('summary')">요약</div>
                <div class="tab" data-tab="position" onclick="showTab('position')">직급별 상세</div>
                <div class="tab" data-tab="detail" onclick="showTab('detail')">개인별 상세</div>
                <div class="tab" data-tab="criteria" onclick="showTab('criteria')">인센티브 기준</div>
            </div>
            
            <!-- 요약 탭 -->
            <div id="summary" class="tab-content active">
                <div class="section">
                    <h2 class="section-title">Type별 현황</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>전체 인원</th>
                            <th>수령 인원</th>
                            <th>수령률</th>
                            <th>총 지급액</th>
                            <th>평균 지급액</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            # Type별 데이터 추가
            for role_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
                type_data = self.month_data[self.month_data['ROLE TYPE STD'] == role_type]
                if not type_data.empty:
                    type_total = len(type_data)
                    type_receiving = (type_data[incentive_col] > 0).sum()
                    type_amount = type_data[incentive_col].sum()
                    type_avg = type_data[type_data[incentive_col] > 0][incentive_col].mean() if type_receiving > 0 else 0
                    
                    type_class = f"type-{role_type.split('-')[1]}"
                    
                    html_content += f"""
                        <tr>
                            <td><span class="type-badge {type_class}">{role_type}</span></td>
                            <td>{type_total}명</td>
                            <td>{type_receiving}명</td>
                            <td>{type_receiving/type_total*100:.1f}%</td>
                            <td>{type_amount:,.0f} VND</td>
                            <td>{type_avg:,.0f} VND</td>
                        </tr>"""
            
            html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- 직급별 상세 탭 -->
    <div id="position" class="tab-content">
        <div class="section">
            <h2 class="section-title">직급별 상세 현황</h2>"""
            
            # 직급별 상세 테이블 추가
            for role_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
                type_data = valid_employees[valid_employees['ROLE TYPE STD'] == role_type]
                if not type_data.empty:
                    html_content += f"""
            <h3 style="margin-top: 30px; color: #667eea;">{role_type} 직급별 통계</h3>
            <table>
                <thead>
                    <tr>
                        <th>직급</th>
                        <th>총원</th>
                        <th>수령인원</th>
                        <th>미수령인원</th>
                        <th>수령률</th>
                        <th>총지급액</th>
                        <th>평균지급액</th>
                    </tr>
                </thead>
                <tbody>"""
                    
                    position_col = 'QIP POSITION 1ST  NAME'
                    if position_col in type_data.columns:
                        positions = type_data.groupby(position_col).agg({
                            incentive_col: ['count', lambda x: (x > 0).sum(), 'sum', 
                                           lambda x: x[x > 0].mean() if (x > 0).sum() > 0 else 0]
                        }).round(0)
                        positions.columns = ['총원', '수령인원', '총지급액', '평균지급액']
                        positions['미수령인원'] = positions['총원'] - positions['수령인원']
                        positions['수령률'] = (positions['수령인원'] / positions['총원'] * 100).round(1)
                        positions = positions.sort_values('수령인원', ascending=False)
                        
                        for position, row in positions.iterrows():
                            if row['총원'] > 0:
                                html_content += f"""
                    <tr>
                        <td>{position}</td>
                        <td>{int(row['총원'])}명</td>
                        <td>{int(row['수령인원'])}명</td>
                        <td>{int(row['미수령인원'])}명</td>
                        <td>{row['수령률']}%</td>
                        <td>{row['총지급액']:,.0f} VND</td>
                        <td>{row['평균지급액']:,.0f} VND</td>
                    </tr>"""
                    
                    html_content += """
                </tbody>
            </table>"""
            
            html_content += f"""
        </div>
    </div>
    
    <!-- 개인별 상세 탭 -->
    <div id="detail" class="tab-content">
        <div class="section">
            <h2 class="section-title">개인별 상세 정보</h2>
            
            <!-- 필터 영역 -->
            <div class="filter-container">
                <div class="filter-row">
                    <input type="text" id="searchInput" class="filter-input" placeholder="직원번호 또는 이름 검색..." onkeyup="filterTable()">
                    <select id="typeFilter" class="filter-input" onchange="filterTable()">
                        <option value="">모든 Type</option>
                        <option value="TYPE-1">TYPE-1</option>
                        <option value="TYPE-2">TYPE-2</option>
                        <option value="TYPE-3">TYPE-3</option>
                    </select>
                    <input type="text" id="positionFilter" class="filter-input" placeholder="직급 검색..." onkeyup="filterTable()">
                </div>
            </div>
            
            <!-- 상세 테이블 -->
            <div style="overflow-x: auto;">
                <table id="detailTable" class="detail-table">
                    <thead>
                        <tr>
                            <th>직원번호</th>
                            <th>이름</th>
                            <th>직급</th>
                            <th>Type</th>
                            <th>{prev_month_kr} 인센티브</th>
                            <th>{month_kr} 인센티브</th>
                            <th>증감</th>
                            <th>계산 근거</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            # 개인별 상세 데이터 추가
            for idx, row in valid_employees.iterrows():
                emp_no = row.get('Employee No', '')
                name = row.get('Full Name', '')
                position = row.get('QIP POSITION 1ST  NAME', '')
                role_type = row.get('ROLE TYPE STD', '')
                prev_amount = row.get('Previous_Incentive', 0) if 'Previous_Incentive' in row else 0
                curr_amount = row.get(incentive_col, 0)
                diff = curr_amount - prev_amount
                
                # 계산 근거 생성 (복수 사유 표시)
                reason = ""
                if curr_amount > 0:
                    if role_type == 'TYPE-1':
                        if 'ASSEMBLY INSPECTOR' in str(position).upper():
                            # 연속 개월 수 찾기 (로그에서 추출하거나 계산)
                            reason = f"조건 충족 - 연속 달성"
                        elif 'LINE LEADER' in str(position).upper():
                            reason = "부하직원 인센티브 × 7%"
                        elif 'GROUP LEADER' in str(position).upper():
                            reason = "Line Leader 평균 × 2"
                        else:
                            reason = "TYPE-1 기준 충족"
                    elif role_type == 'TYPE-2':
                        reason = "TYPE-1 평균 기준"
                    elif role_type == 'TYPE-3':
                        reason = "TYPE-3 정책 제외"
                else:
                    # 미수령 사유 - 복수 사유 수집
                    reasons = []
                    
                    # TYPE-3는 항상 정책 제외
                    if role_type == 'TYPE-3':
                        reasons.append("TYPE-3 정책 제외")
                    else:
                        # 출근 조건 체크
                        if row.get('attendancy condition 1 - acctual working days is zero') == 'yes':
                            reasons.append("출근일수 0")
                        if row.get('attendancy condition 2 - unapproved Absence Day is more than 2 days') == 'yes':
                            reasons.append("무단결근 >2일")
                        if row.get('attendancy condition 3 - absent % is over 12%') == 'yes':
                            reasons.append("결근율 >12%")
                        
                        # AQL 조건 체크
                        if row.get('Continuous_FAIL', 'NO') == 'YES':
                            reasons.append("3개월 연속 AQL 실패")
                        elif row.get(f"{month_str} AQL Failures", 0) > 0:
                            reasons.append("AQL 실패")
                        
                        # 직책별 차별화된 체크
                        position_upper = str(position).upper()
                        
                        # AUDITOR/TRAINER는 5PRS 체크 제외
                        if 'AUDIT' not in position_upper and 'TRAINER' not in position_upper:
                            # Assembly Inspector만 5PRS 체크
                            if 'ASSEMBLY INSPECTOR' in position_upper:
                                if row.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%') == 'no':
                                    reasons.append("5PRS 조건 미달")
                        
                        # LINE LEADER 특수 조건
                        if 'LINE LEADER' in position_upper and curr_amount == 0:
                            subordinates = valid_employees[valid_employees['MST direct boss name'] == emp_no]
                            if (subordinates['Continuous_FAIL'] == 'YES').any():
                                reasons.append("부하직원 3개월 연속 AQL 실패")
                        
                        # AUDITOR/TRAINER 특수 조건
                        if ('AUDIT' in position_upper or 'TRAINER' in position_upper) and curr_amount == 0:
                            # 담당 구역 관련 체크만 (이미 5PRS는 제외됨)
                            if not reasons:  # 다른 사유가 없는 경우에만
                                reasons.append("담당 구역 reject율 초과 또는 3개월 연속 실패자 발생")
                    
                    # 사유 조합
                    if reasons:
                        if len(reasons) == 1:
                            reason = reasons[0]
                        else:
                            # 주요 사유와 추가 사유 구분
                            reason = f"{reasons[0]} / 추가: {', '.join(reasons[1:])}"
                    else:
                        reason = "조건 미충족"
                
                diff_color = 'green' if diff > 0 else 'red' if diff < 0 else 'black'
                
                html_content += f"""
                    <tr>
                        <td>{emp_no}</td>
                        <td>{name}</td>
                        <td>{position}</td>
                        <td><span class="type-badge type-{role_type.split('-')[1] if '-' in role_type else '0'}">{role_type}</span></td>
                        <td>{prev_amount:,.0f} VND</td>
                        <td><strong>{curr_amount:,.0f} VND</strong></td>
                        <td style="color: {diff_color}">{diff:+,.0f}</td>
                        <td>{reason}</td>
                    </tr>"""
            
            html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- 인센티브 기준 탭 -->
    <div id="criteria" class="tab-content">
        <div class="section">
            <h2 class="section-title">TYPE-1 인센티브 계산 기준</h2>
            
            <!-- Assembly Inspector -->
            <h3 style="color: #667eea; margin-top: 20px;">Assembly Inspector</h3>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ 출근 조건: 실제 근무일 > 0일, 무단결근 ≤ 2일, 결근율 ≤ 12%</li>
                <li>✅ AQL 조건: 당월 AQL 실패 0건, 최근 3개월 연속 실패 아님</li>
                <li>✅ 5PRS 조건: 검사량 ≥ 100개 AND 통과율 ≥ 95%</li>
            </ul>
            
            <h4>인센티브 계산 (연속 충족 개월 수에 따른 차등 지급):</h4>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>연속 충족 개월 수</th>
                        <th>인센티브 금액 (VND)</th>
                        <th>비고</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>처음 충족 / 연속성 끊김 후</td><td style="text-align: right;">150,000</td><td>기본 금액</td></tr>
                    <tr><td>1개월</td><td style="text-align: right;">150,000</td><td></td></tr>
                    <tr><td>2개월</td><td style="text-align: right;">250,000</td><td></td></tr>
                    <tr><td>3개월</td><td style="text-align: right;">300,000</td><td></td></tr>
                    <tr><td>4개월</td><td style="text-align: right;">350,000</td><td></td></tr>
                    <tr><td>5개월</td><td style="text-align: right;">400,000</td><td></td></tr>
                    <tr><td>6개월</td><td style="text-align: right;">450,000</td><td></td></tr>
                    <tr><td>7개월</td><td style="text-align: right;">500,000</td><td></td></tr>
                    <tr><td>8개월</td><td style="text-align: right;">650,000</td><td>급증</td></tr>
                    <tr><td>9개월</td><td style="text-align: right;">750,000</td><td></td></tr>
                    <tr><td>10개월</td><td style="text-align: right;">850,000</td><td></td></tr>
                    <tr><td>11개월</td><td style="text-align: right;">950,000</td><td></td></tr>
                    <tr><td>12개월 이상</td><td style="text-align: right;">1,000,000</td><td>최대 금액</td></tr>
                </tbody>
            </table>
            
            <!-- AQL Inspector -->
            <h3 style="color: #667eea; margin-top: 30px;">AQL Inspector</h3>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ 출근 조건: 실제 근무일 > 0일, 무단결근 ≤ 2일, 결근율 ≤ 12%</li>
                <li>✅ AQL 조건: 당월 AQL 실패 0건</li>
                <li>❌ 5PRS 조건: 면제</li>
            </ul>
            
            <h4>인센티브 계산 (3파트 합산):</h4>
            <p style="margin: 10px 0;">총 인센티브 = Part 1 + Part 2 + Part 3</p>
            
            <h5 style="margin-top: 20px;">Part 1: AQL 검사 평가 결과 (Rejection Rate < 3%)</h5>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>연속 충족 개월 수</th>
                        <th>인센티브 금액 (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1개월</td><td style="text-align: right;">150,000</td></tr>
                    <tr><td>2개월</td><td style="text-align: right;">250,000</td></tr>
                    <tr><td>3개월</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>4개월</td><td style="text-align: right;">350,000</td></tr>
                    <tr><td>5개월</td><td style="text-align: right;">400,000</td></tr>
                    <tr><td>6개월</td><td style="text-align: right;">450,000</td></tr>
                    <tr><td>7개월</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>8개월</td><td style="text-align: right;">650,000</td></tr>
                    <tr><td>9개월</td><td style="text-align: right;">750,000</td></tr>
                    <tr><td>10개월</td><td style="text-align: right;">850,000</td></tr>
                    <tr><td>11개월</td><td style="text-align: right;">950,000</td></tr>
                    <tr><td>12개월 이상</td><td style="text-align: right;">1,000,000</td></tr>
                </tbody>
            </table>
            
            <h5 style="margin-top: 20px;">Part 2: CFA 자격증</h5>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>조건</th>
                        <th>인센티브 금액 (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>CFA 자격증 보유</td><td style="text-align: right;">700,000</td></tr>
                    <tr><td>자격증 미보유</td><td style="text-align: right;">0</td></tr>
                </tbody>
            </table>
            
            <h5 style="margin-top: 20px;">Part 3: HWK 클레임 방지</h5>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>연속 충족 개월 수</th>
                        <th>인센티브 금액 (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1-3개월</td><td style="text-align: right;">0</td></tr>
                    <tr><td>4-6개월</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>7-9개월</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>10-12개월</td><td style="text-align: right;">700,000</td></tr>
                    <tr><td>13개월 이상</td><td style="text-align: right;">900,000</td></tr>
                </tbody>
            </table>
            
            <!-- Line Leader -->
            <h3 style="color: #667eea; margin-top: 30px;">Line Leader</h3>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ 출근 조건: 실제 근무일 > 0일, 무단결근 ≤ 2일, 결근율 ≤ 12%</li>
                <li>❌ AQL 조건: 면제</li>
                <li>❌ 5PRS 조건: 면제</li>
                <li>⚠️ 특별 조건: 부하직원 중 3개월 연속 AQL 실패자가 있으면 인센티브 0원</li>
            </ul>
            
            <h4>인센티브 계산:</h4>
            <p style="margin: 10px 0;">
                <strong>계산식:</strong> (부하직원 인센티브 총합 × 7%) × (인센티브 받는 부하직원 수 / 전체 부하직원 수)
            </p>
            
            <!-- 관리자급 -->
            <h3 style="color: #667eea; margin-top: 30px;">관리자급 (Group Leader, Supervisor, Manager)</h3>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ 출근 조건: 실제 근무일 > 0일, 무단결근 ≤ 2일, 결근율 ≤ 12%</li>
                <li>❌ AQL 조건: 면제</li>
                <li>❌ 5PRS 조건: 면제</li>
            </ul>
            
            <h4>인센티브 계산:</h4>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>직책</th>
                        <th>계산 방식</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Group Leader</td><td>팀 내 Line Leader 평균 인센티브 × 2</td></tr>
                    <tr><td>(Vice) Supervisor</td><td>팀 내 Line Leader 평균 인센티브 × 2.5</td></tr>
                    <tr><td>Assistant Manager</td><td>팀 내 Line Leader 평균 인센티브 × 3</td></tr>
                    <tr><td>Manager</td><td>팀 내 Line Leader 평균 인센티브 × 3.5</td></tr>
                    <tr><td>Senior Manager</td><td>팀 내 Line Leader 평균 인센티브 × 4</td></tr>
                </tbody>
            </table>
            
            <!-- Auditor/Trainer -->
            <h3 style="color: #667eea; margin-top: 30px;">Auditor/Trainer</h3>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ 출근 조건: 실제 근무일 > 0일, 무단결근 ≤ 2일, 결근율 ≤ 12%</li>
                <li>⚠️ 담당 구역 조건:
                    <ul>
                        <li>담당 구역 AQL reject율 < 3%</li>
                        <li>담당 구역에 3개월 연속 AQL 실패자 없음</li>
                    </ul>
                </li>
                <li>❌ 5PRS 조건: 면제</li>
            </ul>
            
            <h4>인센티브 계산:</h4>
            <p style="margin: 10px 0;">조건 충족 시 Assembly Inspector와 동일한 연속 충족 개월 수 기준 적용</p>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>연속 충족 개월 수</th>
                        <th>인센티브 금액 (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1개월</td><td style="text-align: right;">150,000</td></tr>
                    <tr><td>2개월</td><td style="text-align: right;">250,000</td></tr>
                    <tr><td>3개월</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>4개월</td><td style="text-align: right;">350,000</td></tr>
                    <tr><td>5개월</td><td style="text-align: right;">400,000</td></tr>
                    <tr><td>6개월</td><td style="text-align: right;">450,000</td></tr>
                    <tr><td>7개월</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>8개월</td><td style="text-align: right;">650,000</td></tr>
                    <tr><td>9개월</td><td style="text-align: right;">750,000</td></tr>
                    <tr><td>10개월</td><td style="text-align: right;">850,000</td></tr>
                    <tr><td>11개월</td><td style="text-align: right;">950,000</td></tr>
                    <tr><td>12개월 이상</td><td style="text-align: right;">1,000,000</td></tr>
                </tbody>
            </table>
            
            <!-- Model Master -->
            <h3 style="color: #667eea; margin-top: 30px;">Model Master</h3>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ 출근 조건: 실제 근무일 > 0일, 무단결근 ≤ 2일, 결근율 ≤ 12%</li>
                <li>⚠️ 전체 공장 조건: 전체 공장 AQL reject율 < 3%</li>
                <li>❌ 5PRS 조건: 면제</li>
            </ul>
            
            <h4>인센티브 계산:</h4>
            <p style="margin: 10px 0;">조건 충족 시 Assembly Inspector와 동일한 연속 충족 개월 수 기준 적용</p>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>연속 충족 개월 수</th>
                        <th>인센티브 금액 (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1개월</td><td style="text-align: right;">150,000</td></tr>
                    <tr><td>2개월</td><td style="text-align: right;">250,000</td></tr>
                    <tr><td>3개월</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>4개월</td><td style="text-align: right;">350,000</td></tr>
                    <tr><td>5개월</td><td style="text-align: right;">400,000</td></tr>
                    <tr><td>6개월</td><td style="text-align: right;">450,000</td></tr>
                    <tr><td>7개월</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>8개월</td><td style="text-align: right;">650,000</td></tr>
                    <tr><td>9개월</td><td style="text-align: right;">750,000</td></tr>
                    <tr><td>10개월</td><td style="text-align: right;">850,000</td></tr>
                    <tr><td>11개월</td><td style="text-align: right;">950,000</td></tr>
                    <tr><td>12개월 이상</td><td style="text-align: right;">1,000,000</td></tr>
                </tbody>
            </table>
            
            <!-- TYPE-2 인센티브 -->
            <h2 class="section-title" style="margin-top: 40px;">TYPE-2 인센티브 계산 기준</h2>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ 출근 조건: 실제 근무일 > 0일, 무단결근 ≤ 2일, 결근율 ≤ 12%</li>
                <li>❌ AQL 조건: 면제</li>
                <li>❌ 5PRS 조건: 면제</li>
            </ul>
            
            <h4>인센티브 계산:</h4>
            <p style="margin: 10px 0;">출근 조건 충족 시 매칭된 TYPE-1 포지션의 평균 인센티브 지급</p>
            
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>TYPE-2 포지션</th>
                        <th>매칭되는 TYPE-1 포지션</th>
                        <th>평균 인센티브 (예시)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>BOTTOM INSPECTOR</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>STITCHING INSPECTOR</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>MTL INSPECTOR</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>OSC INSPECTOR</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>CUTTING INSPECTOR</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>OCPT STFF</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>AQL INSPECTOR</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>RQC</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>QA TEAM (QA3A)</td><td>GROUP LEADER</td><td>350,117 VND</td></tr>
                    <tr><td>QA TEAM (QA3B)</td><td>ASSEMBLY INSPECTOR</td><td>400,000 VND</td></tr>
                    <tr><td>GROUP LEADER</td><td>GROUP LEADER</td><td>350,117 VND</td></tr>
                    <tr><td>LINE LEADER</td><td>LINE LEADER</td><td>194,668 VND</td></tr>
                    <tr><td>(V) SUPERVISOR</td><td>(VICE) SUPERVISOR</td><td>549,052 VND</td></tr>
                    <tr><td>A.MANAGER</td><td>ASSISTANT MANAGER</td><td>659,462 VND</td></tr>
                </tbody>
            </table>
            
            <!-- TYPE-3 인센티브 -->
            <h2 class="section-title" style="margin-top: 40px;">TYPE-3 인센티브 계산 기준</h2>
            
            <h4>지급 조건:</h4>
            <ul style="margin-left: 20px;">
                <li>❌ 인센티브 지급 대상에서 제외</li>
            </ul>
            
            <h4>대상자:</h4>
            <ul style="margin-left: 20px;">
                <li>입사일 기준 1개월 미만 신입 직원</li>
            </ul>
        </div>
    </div>
        
        <div class="footer">
            <p>© 2025 QIP 인센티브 관리 시스템</p>
            <p>본 리포트는 자동으로 생성되었습니다.</p>
        </div>
    </div>
</body>
</html>"""
            
            # 파일 저장
            import os
            output_dir = "output_files"
            os.makedirs(output_dir, exist_ok=True)
            html_filename = os.path.join(output_dir, f"QIP_Incentive_Report_{month_str}_{self.config.year}.html")
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_filename
        
        except Exception as e:
            print(f"❌ HTML 리포트 생성 중 오류: {e}")
            traceback.print_exc()
            return None


class CompleteDataLoader:
    """데이터 로더 클래스 (개선된 버전 - 자동 변환 지원)"""
    
    def __init__(self, config: MonthConfig):
        self.config = config
        self.file_mapping = {
            f"{config.month.full_name}_basic": config.get_file_path("basic"),
            f"{config.previous_months[-1].full_name}_incentive" if config.previous_months else "prev_incentive": 
                config.get_file_path("previous_incentive"),
            f"{config.month.full_name}_aql": config.get_file_path("aql"),
            f"{config.month.full_name}_5prs": config.get_file_path("5prs"),
            f"{config.month.full_name}_attendance": config.get_file_path("attendance")
        }
        
        # 자동 변환 설정 로드
        self.auto_convert_config = self.load_auto_convert_config()
        self.attendance_converter = None
    
    def load_auto_convert_config(self) -> Dict:
        """자동 변환 설정 로드"""
        try:
            config_path = Path('attendance_conversion_config.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        # 기본 설정
        return {
            "auto_convert": True,
            "debug_mode": False,
            "validate_conversion": True,
            "cache_enabled": True
        }
    
    def get_attendance_file_path(self, file_path: str, file_key: str) -> str:
        """출결 파일 경로 처리 (자동 변환 포함)"""
        # attendance 파일이 아니면 그대로 반환
        if 'attendance' not in file_key.lower():
            return file_path
        
        # 자동 변환이 비활성화면 그대로 반환
        if not self.auto_convert_config.get('auto_convert', True):
            return file_path
        
        # 자동 변환기 초기화 (필요시)
        if self.attendance_converter is None:
            try:
                # Try different import methods
                try:
                    from input_files.attendance.attendance_auto_converter import AttendanceAutoConverter
                except ImportError:
                    try:
                        # Alternative import path
                        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        from input_files.attendance.attendance_auto_converter import AttendanceAutoConverter
                    except ImportError:
                        # If still fails, set converter to None
                        AttendanceAutoConverter = None
                if AttendanceAutoConverter:
                    self.attendance_converter = AttendanceAutoConverter(
                        debug_mode=self.auto_convert_config.get('debug_mode', False)
                    )
                    print("✅ 출결 자동 변환 모듈 로드 완료")
                else:
                    self.attendance_converter = None
                    print("⚠️ 자동 변환 모듈 로드 실패: 수동 변환 경로 사용")
            except ImportError as e:
                print(f"⚠️ 자동 변환 모듈 로드 실패: {e}")
                return file_path
        
        # 자동 변환 실행
        try:
            converted_path = self.attendance_converter.ensure_converted_file(file_path)
            if converted_path != file_path:
                print(f"✅ 출결 데이터 자동 변환 완료: {os.path.basename(converted_path)}")
            return converted_path
        except Exception as e:
            print(f"⚠️ 자동 변환 실패, 원본 파일 사용: {e}")
            return file_path
    
    def load_single_file(self, file_path: str, file_key: str) -> Optional[pd.DataFrame]:
        """단일 파일 로딩 (자동 변환 지원)"""
        # attendance 파일의 경우 자동 변환 처리
        file_path = self.get_attendance_file_path(file_path, file_key)
        
        if not file_path or not os.path.exists(file_path):
            print(f"⚠️ 파일 없음: {file_path}")
            return None
        
        try:
            # 다양한 인코딩과 구분자 시도
            for enc in ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr']:
                for sep in [',', ';', '\t', '|']:
                    try:
                        df = pd.read_csv(file_path, sep=sep, encoding=enc)
                        if len(df) > 0 and len(df.columns) > 1:
                            # AQL 파일의 경우 빈 행 제거 후 건수 표시
                            if 'aql' in file_key.lower():
                                valid_df = df.dropna(how='all')
                                print(f"✅ {file_key} 로드 성공: {len(valid_df)} 건")
                            else:
                                print(f"✅ {file_key} 로드 성공: {len(df)} 건")
                            return df
                    except:
                        continue
            
            print(f"❌ {file_key} 로드 실패")
            return None
        
        except Exception as e:
            print(f"❌ 파일 로드 오류 ({file_key}): {e}")
            return None
    
    def load_all_files(self) -> Dict[str, pd.DataFrame]:
        """모든 파일 로드"""
        print(f"\n📂 {self.config.get_month_str('korean')} 데이터 파일 로딩 중...")
        
        data = {}
        for file_key, file_path in self.file_mapping.items():
            if file_path:  # None이 아닌 경우만
                df = self.load_single_file(file_path, file_key)
                if df is not None:
                    data[file_key] = df
        
        print(f"✅ 총 {len(data)}개 파일 로드 완료")
        return data


def detect_month_from_attendance(file_path: str) -> tuple:
    """Attendance 파일의 Work Date에서 년도와 월 자동 감지"""
    try:
        import pandas as pd
        
        # 파일 읽기
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Work Date 칼럼 찾기
        date_cols = ['Work Date', 'WorkDate', 'Date', '날짜']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            print("⚠️ 날짜 칼럼을 찾을 수 없습니다.")
            return None, None
        
        # 날짜 파싱 및 년월 추출
        dates = pd.to_datetime(df[date_col], format='%Y.%m.%d', errors='coerce')
        dates = dates.dropna()
        
        if dates.empty:
            print("⚠️ 유효한 날짜를 찾을 수 없습니다.")
            return None, None
        
        # 가장 많이 나타나는 년월 찾기
        year_months = dates.dt.to_period('M')
        most_common = year_months.value_counts().index[0]
        
        year = most_common.year
        month = most_common.month
        
        print(f"✅ Attendance 파일에서 감지된 년월: {year}년 {month}월")
        return year, month
        
    except Exception as e:
        print(f"⚠️ Attendance 파일 년월 감지 실패: {e}")
        return None, None


def calculate_working_days_from_attendance(file_path: str, year: int, month: int) -> int:
    """Attendance 파일에서 실제 근무일 계산"""
    try:
        import pandas as pd
        
        # 파일 읽기
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Work Date 칼럼에서 해당 년월 필터링
        date_pattern = f"{year}.{month:02d}"
        
        # Work Date 칼럼 찾기
        date_cols = ['Work Date', 'WorkDate', 'Date', '날짜']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            print("⚠️ 날짜 칼럼을 찾을 수 없습니다. 기본값 사용")
            return None
        
        # 해당 월의 유니크한 날짜 수 계산
        month_dates = df[df[date_col].str.contains(date_pattern, na=False)][date_col]
        unique_dates = month_dates.str.extract(r'(\d{4}\.\d{2}\.\d{2})')[0].unique()
        working_days = len(unique_dates)
        
        print(f"✅ Attendance 파일에서 계산된 {year}년 {month}월 근무일: {working_days}일")
        return working_days
        
    except Exception as e:
        print(f"⚠️ Attendance 파일 분석 실패: {e}")
        return None


def init_command():
    """초기 설정 명령어 - 파일 자동 감지 및 설정"""
    print("\n🔧 초기 설정 시작...")
    print("📂 현재 디렉토리의 파일을 분석합니다...")
    
    import os
    import glob
    
    # 현재 디렉토리의 CSV 파일 목록
    csv_files = glob.glob("*.csv")
    excel_files = glob.glob("*.xlsx")
    
    print(f"\n발견된 파일:")
    print(f"  CSV 파일: {len(csv_files)}개")
    print(f"  Excel 파일: {len(excel_files)}개")
    
    # Attendance 파일 찾기
    attendance_file = None
    for file in csv_files + excel_files:
        if 'attendance' in file.lower():
            attendance_file = file
            print(f"\n✅ Attendance 파일 발견: {attendance_file}")
            break
    
    if not attendance_file:
        print("⚠️ Attendance 파일을 찾을 수 없습니다.")
        attendance_file = input("Attendance 파일 경로를 입력하세요: ").strip()
    
    # 년도와 월 입력
    year = int(input("\n📅 연도를 입력하세요 (예: 2025): "))
    month_num = int(input("📅 월을 입력하세요 (1-12): "))
    
    # Attendance 파일에서 근무일 자동 계산
    working_days = None
    if attendance_file and os.path.exists(attendance_file):
        if attendance_file.endswith('.csv'):
            working_days = calculate_working_days_from_attendance(attendance_file, year, month_num)
    
    if working_days is None:
        print("\n⚠️ Attendance 파일에서 근무일을 계산할 수 없습니다.")
        working_days = int(input("근무일을 직접 입력하세요: "))
    
    # Month 객체 생성
    month = Month.from_number(month_num)
    
    # 이전 월 설정
    prev_month1 = Month.from_number((month_num - 2) % 12 or 12)
    prev_month2 = Month.from_number((month_num - 1) % 12 or 12)
    
    # 파일 패턴 감지
    print("\n📁 데이터 파일 자동 감지 중...")
    
    # 기본 파일 패턴
    file_patterns = {
        "basic": f"basic.*{month.full_name}|{month.short_name}.*manpower",
        "previous_incentive": f"{prev_month2.full_name}.*incentive|{prev_month2.short_name}.*qip",
        "aql": f"aql.*{month.full_name}|{month.short_name}.*aql",
        "5prs": f"5.*p.*{month.full_name}|{month.short_name}.*5.*p",
        "attendance": f"attendance.*{month.full_name}|{month.short_name}.*attendance"
    }
    
    detected_files = {}
    for key, pattern in file_patterns.items():
        for file in csv_files + excel_files:
            if re.search(pattern, file, re.IGNORECASE):
                detected_files[key] = file
                print(f"  ✅ {key}: {file}")
                break
    
    # 수동 입력이 필요한 파일
    for key in file_patterns:
        if key not in detected_files:
            print(f"\n⚠️ {key} 파일을 자동으로 찾을 수 없습니다.")
            file_path = input(f"{key} 파일 경로 입력 (Enter: 건너뛰기): ").strip()
            if file_path:
                detected_files[key] = file_path
    
    # 설정 생성
    config = MonthConfig(
        year=year,
        month=month,
        working_days=working_days,
        previous_months=[prev_month1, prev_month2],
        file_paths=detected_files,
        output_prefix=f"output_QIP_incentive_{month.full_name}_{year}"
    )
    
    # 설정 저장
    config_file = f"config_{month.full_name}_{year}.json"
    ConfigManager.save_config(config, config_file)
    print(f"\n✅ 설정이 {config_file}에 저장되었습니다.")
    
    # 실행 여부 확인
    if input("\n지금 바로 인센티브 계산을 실행하시겠습니까? (y/n): ").lower() == 'y':
        return config
    
    return None


def main():
    """메인 실행 함수"""
    print("="*60)
    print(f"🚀 QIP 인센티브 계산 시스템 v6.0 (개선된 버전)")
    print("="*60)
    
    # 명령어 체크
    import sys
    import argparse
    
    # argparse로 명령줄 인자 처리
    parser = argparse.ArgumentParser(description='QIP 인센티브 계산 시스템')
    parser.add_argument('--config', type=str, help='설정 파일 경로')
    parser.add_argument('--init', action='store_true', help='자동 설정 초기화')
    args = parser.parse_args()
    
    # config 파일이 지정된 경우
    if args.config:
        config = ConfigManager.load_config(args.config)
        if config is None:
            print(f"\n❌ 설정 파일을 찾을 수 없습니다: {args.config}")
            return
        print(f"\n✅ 설정 파일 로드 완료: {args.config}")
    elif args.init or (len(sys.argv) > 1 and sys.argv[1] == '/init'):
        config = init_command()
        if config is None:
            print("\n프로그램을 종료합니다.")
            return
    else:
        # 월 선택
        print("\n📅 계산할 월을 선택하세요:")
        print("1. 6월 (June)")
        print("2. 7월 (July)")
        print("3. 사용자 정의")
        print("4. /init - 자동 설정 (권장)")
        
        choice = input("\n선택 (1/2/3/4): ").strip()
    
        if choice == "4":
            config = init_command()
            if config is None:
                print("\n프로그램을 종료합니다.")
                return
        elif choice == "1":
            config = ConfigManager.create_june_config()
        elif choice == "2":
            config = ConfigManager.create_july_config()
        elif choice == "3":
            # 사용자 정의 설정
            year = int(input("연도 입력 (예: 2025): "))
            month_num = int(input("월 입력 (1-12): "))
            working_days = int(input("근무일 수 입력: "))
            
            month = Month.from_number(month_num)
            prev_month1 = Month.from_number((month_num - 2) % 12 or 12)
            prev_month2 = Month.from_number((month_num - 1) % 12 or 12)
            
            config = MonthConfig(
                year=year,
                month=month,
                working_days=working_days,
                previous_months=[prev_month1, prev_month2],
                file_paths={
                    "basic": input(f"{month.korean_name} 기본 데이터 파일명: "),
                    "previous_incentive": input(f"{prev_month2.korean_name} 인센티브 데이터 파일명: "),
                    "aql": input(f"{month.korean_name} AQL 데이터 파일명: "),
                    "5prs": input(f"{month.korean_name} 5PRS 데이터 파일명: "),
                    "attendance": input(f"{month.korean_name} 출석 데이터 파일명: ")
                },
                output_prefix=f"output_QIP_incentive_{month.full_name}_{year}"
            )
        else:
            print("❌ 잘못된 선택입니다.")
            return
    
    # 설정 저장 옵션 (config 파라미터로 실행한 경우에는 건너뛰기)
    if not args.config:
        if input("\n설정을 저장하시겠습니까? (y/n): ").lower() == 'y':
            ConfigManager.save_config(config)
    
    try:
        # 데이터 로드
        loader = CompleteDataLoader(config)
        data = loader.load_all_files()
        
        if not data:
            print("❌ 로드된 데이터가 없습니다.")
            return
        
        # 계산기 초기화 및 실행
        calculator = CompleteQIPCalculator(data, config)
        
        # 인센티브 계산
        calculator.calculate_all_incentives()
        
        # 결과 요약
        calculator.generate_summary()
        
        # 결과 저장
        if calculator.save_results():
            print(f"\n🎉 {config.get_month_str('korean')} 인센티브 계산이 완료되었습니다!")
        else:
            print("\n⚠️ 결과 저장 중 일부 오류가 발생했습니다.")
    
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

    