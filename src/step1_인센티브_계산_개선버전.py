"""
[STEP 1] QIP Incentive Calculation System - Excel/CSV created
Created: 2025-08-12
Version: 6.0

Terminal execution command examples (2025year July ~ 2026year 6월):

# 2025year
python src/step1_incentive_계산_개선버전.py --config config_files/config_july_2025.json      # July
python src/step1_incentive_계산_개선버전.py --config config_files/config_august_2025.json    # August
python src/step1_incentive_계산_개선버전.py --config config_files/config_september_2025.json # September
python src/step1_incentive_계산_개선버전.py --config config_files/config_october_2025.json   # October
python src/step1_incentive_계산_개선버전.py --config config_files/config_november_2025.json  # November
python src/step1_incentive_계산_개선버전.py --config config_files/config_december_2025.json  # December

# 2026year
python src/step1_incentive_계산_개선버전.py --config config_files/config_january_2026.json   # 1월
python src/step1_incentive_계산_개선버전.py --config config_files/config_february_2026.json  # 2월
python src/step1_incentive_계산_개선버전.py --config config_files/config_march_2026.json     # 3월
python src/step1_incentive_계산_개선버전.py --config config_files/config_april_2026.json     # 4월
python src/step1_incentive_계산_개선버전.py --config config_files/config_may_2026.json       # 5월
python src/step1_incentive_계산_개선버전.py --config config_files/config_june_2026.json      # 6월

Execution order:
1. step0_create_monthly_config.py - Config created (completed)
2. 2. Run this file (step1) - Excel/CSV calculation ← Current step
3. step2_dashboard_version4.py - HTML created

Key improvements:
1. month별 파라미터화 - 6월to 하load코ingdone value들 configuration 능하게 변경
2. 2. Added configuration management system
3. 3. Enhanced data validation
4. to러 processing 개선
5. 5. Improved reusability
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

# Import common employee filter module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils.common_employee_filter import EmployeeFilter
except ImportError:
    # Fallback for different directory structures
    from common_employee_filter import EmployeeFilter

warnings.filterwarnings('ignore')

# Import common condition check module
try:
    from common_condition_checker import get_condition_checker
except ImportError:
    print("⚠️ Common condition check module not found. Using legacy logic.")
    get_condition_checker = None

# Position condition matrix withload
def load_position_condition_matrix():
    """Load position condition matrix JSON file"""
    try:
        config_path = Path(__file__).parent.parent / 'config_files' / 'position_condition_matrix.json'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                matrix = json.load(f)
                print("✅ Position condition matrix loaded successfully")
                return matrix
        else:
            print(f"⚠️ Position condition matrix file not found: {config_path}")
    except Exception as e:
        print(f"❌ Position condition matrix load failed: {e}")
    return None

# Load matrix as global variable
POSITION_CONDITION_MATRIX = load_position_condition_matrix()

def get_position_config_from_matrix(emp_type, position):
    """
    Find and return configuration for the position from JSON matrix

    Args:
        emp_type: 'TYPE-1', 'TYPE-2', 'TYPE-3' etc.
        position: Position name

    Returns:
        dict: Position configuration (applicable conditions, excluded conditions, etc.)
    """
    if not POSITION_CONDITION_MATRIX:
        return None

    position_upper = position.upper()
    type_config = POSITION_CONDITION_MATRIX.get('position_matrix', {}).get(emp_type, {})

    # Find configuration by position
    for pos_key, pos_config in type_config.items():
        if pos_key == 'default':
            continue
        patterns = pos_config.get('patterns', [])
        for pattern in patterns:
            if pattern in position_upper:
                return pos_config

    # Return default value
    return type_config.get('default', {})


class Month(Enum):
    """Month enumeration"""
    JANUARY = (1, "january", "jan", "1월")
    FEBRUARY = (2, "february", "feb", "2월")
    MARCH = (3, "march", "mar", "3월")
    APRIL = (4, "april", "apr", "4월")
    MAY = (5, "may", "may", "5월")
    JUNE = (6, "june", "jun", "6월")
    JULY = (7, "july", "jul", "July")
    AUGUST = (8, "august", "aug", "August")
    SEPTEMBER = (9, "september", "sep", "September")
    OCTOBER = (10, "october", "oct", "October")
    NOVEMBER = (11, "november", "nov", "November")
    DECEMBER = (12, "december", "dec", "December")
    
    def __init__(self, number, full_name, short_name, korean_name):
        self.number = number
        self.full_name = full_name
        self.short_name = short_name
        self.korean_name = korean_name
    
    @classmethod
    def from_number(cls, number: int):
        """Return Month object from month number"""
        for month in cls:
            if month.number == number:
                return month
        raise ValueError(f"Invalid month number: {number}")
    
    @classmethod
    def from_name(cls, name: str):
        """Return Month object from month name"""
        name_lower = name.lower()
        for month in cls:
            if name_lower in [month.full_name, month.short_name] or name == month.korean_name:
                return month
        raise ValueError(f"Invalid month name: {name}")


@dataclass
class MonthConfig:
    """Monthly configuration data class"""
    year: int
    month: Month
    working_days: int  # Total working days for the month (excluding weekends/holidays)
    previous_months: List[Month]  # Previous months for consecutive failure check
    file_paths: Dict[str, str]  # Required file paths
    output_prefix: str  # Output file prefix
    
    def get_month_str(self, format_type: str = "full") -> str:
        """Return month string"""
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
        """Return path by file type (converts drive:// to input_files/)"""
        path = self.file_paths.get(file_type, "")

        # Convert drive:// protocol to local input_files/ path
        if path.startswith("drive://"):
            path = path.replace("drive://", "input_files/", 1)

        return path
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
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
        """Create configuration from dictionary"""
        return cls(
            year=data["year"],
            month=Month.from_name(data["month"]),
            working_days=data["working_days"],
            previous_months=[Month.from_name(m) for m in data["previous_months"]],
            file_paths=data["file_paths"],
            output_prefix=data["output_prefix"]
        )


class ConfigManager:
    """Configuration management class"""
    
    @staticmethod
    def create_auto_config(attendance_file: str = None) -> MonthConfig:
        """Auto-detect month from attendance file and create configuration"""
        import os
        import glob
        
        # Auto-find attendance file
        if not attendance_file:
            attendance_patterns = [
                "input_files/attendance data *.csv",
                "input_files/attendance_data_*.csv",
                "attendance*.csv"
            ]
            
            for pattern in attendance_patterns:
                files = glob.glob(pattern)
                if files:
                    # Select original file excluding converted files
                    original_files = [f for f in files if 'converted' not in f]
                    if original_files:
                        attendance_file = max(original_files, key=os.path.getmtime)
                    else:
                        attendance_file = max(files, key=os.path.getmtime)
                    print(f"✅ Attendance file Auto-detected: {attendance_file}")
                    break
            
            if not attendance_file:
                print("⚠️ Attendance file not found.")
                return None
        
        # attendance 파일에서 yearmonth detection
        year, month = detect_month_from_attendance(attendance_file)
        
        if not year or not month:
            print("⚠️ Attendance filecannot detect year/month from.")
            return None
        
        month_obj = Month.from_number(month)
        
        # 근무 days 수 calculation
        working_days = calculate_working_days_from_attendance(attendance_file, year, month)
        if not working_days:
            print("❌ Error: attendance 파일에서 cannot calculate working days from.")
            print("   attendance CSV fileplease check if exists and has correct format.")
            return None
        
        # previous 2-month 자same calculation
        prev_month1_num = (month - 2) % 12 or 12
        prev_month2_num = (month - 1) % 12 or 12
        prev_month1 = Month.from_number(prev_month1_num)
        prev_month2 = Month.from_number(prev_month2_num)
        
        # 파일 자동 detection
        file_paths = ConfigManager.auto_detect_files(month_obj.full_name, prev_month2.korean_name, year)
        
        print(f"\n📊 Auto-configuration creation completed:")
        print(f"  - Year: {year}")
        print(f"  - Month: {month_obj.korean_name} ({month_obj.full_name})")
        print(f"  - Working days: {working_days} days")
        print(f"  - previous Month: {prev_month1.korean_name}, {prev_month2.korean_name}")
        
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
        """파일 자동 detection"""
        import os
        
        detected_files = {}
        
        # file 패턴 정of
        patterns = {
            "basic": [
                f"input_files/basic manpower data {month_name}.csv",
                f"input_files/basic_manpower_data_{month_name}.csv"
            ],
            "previous_incentive": [
                f"input_files/{year}year {prev_month_korean} incentive 지급 세부 정보.csv",
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
                print(f"  ⚠️ {key}: file not found")
        
        return detected_files
    
    @staticmethod
    def create_july_config() -> MonthConfig:
        """July configuration created"""
        return MonthConfig(
            year=2025,
            month=Month.JULY,
            working_days=23,  # July 근무 days (예시 - 실제 valuewith 조정 필요)
            previous_months=[Month.MAY, Month.JUNE],  # 5월, 6월 datawith consecutive failure 체크
            file_paths={
                "basic": "input_files/basic manpower data july.csv",
                "previous_incentive": "input_files/2025year 6월 incentive 지급 세부 정보.csv",  # 6월 filewith 수정
                "aql": "input_files/AQL history/1.HSRG AQL REPORT-JULY.2025.csv",  # AQL history 사용
                "5prs": "input_files/5prs data july.csv",
                "attendance": "input_files/attendance/converted/attendance data july_converted.csv"  # converted file 사용
            },
            output_prefix="output_QIP_incentive_july_2025"
        )
    
    @staticmethod
    def create_june_config() -> MonthConfig:
        """6월 configuration created (existing 코load 호환)"""
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
        """configuration JSON filewith saved"""
        if filepath is None:
            filepath = f"config_{config.month.full_name}_{config.year}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"✅ configuration 저장 완료: {filepath}")
    
    @staticmethod
    def load_config(filepath: str) -> MonthConfig:
        """JSON 파일에서 configuration withload"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Configuration loaded successfully: {filepath}")
        return MonthConfig.from_dict(data)


class SpecialCaseHandler:
    """특별 케스 processing 핸들러 (improved 버전)"""
    
    def __init__(self, config: MonthConfig):
        self.config = config
        self.special_positions = [
            'AQL INSPECTOR',
            'MODEL MASTER',
            'AUDIT',
            'TRAINING'
        ]
    
    def handle_aql_inspector_manual_input(self, employee_data: Dict) -> float:
        """AQL Inspector 수same 입력 processing"""
        name = employee_data.get('Full Name', 'Unknown')
        emp_id = employee_data.get('Employee No', 'Unknown')
        position = employee_data.get('QIP POSITION 1ST  NAME', '')
        
        print(f"\n{'='*60}")
        print(f"Special case: AQL INSPECTOR")
        print(f"Employee name: {name}")
        print(f"Employee No: {emp_id}")
        print(f"Position: {position}")
        
        try:
            incentive = self._get_manual_input(name)
            print(f"✅ Input incentive: {incentive:,.0f} VND")
            return incentive
        except Exception as e:
            print(f"❌ Input error: {e}")
            return 0
    
    def handle_model_master_manual_input(self, employee_data: Dict) -> float:
        """Model Master 수same 입력 processing"""
        name = employee_data.get('Full Name', 'Unknown')
        emp_id = employee_data.get('Employee No', 'Unknown')
        position = employee_data.get('QIP POSITION 1ST  NAME', '')
        
        print(f"\n{'='*60}")
        print(f"Special case: MODEL MASTER")
        print(f"Employee name: {name}")
        print(f"Employee No: {emp_id}")
        print(f"Position: {position}")
        
        try:
            incentive = self._get_manual_input(name)
            print(f"✅ Input incentive: {incentive:,.0f} VND")
            return incentive
        except Exception as e:
            print(f"❌ Input error: {e}")
            return 0
    
    def handle_audit_training_manual_input(self, employee_data: Dict) -> float:
        """Audit/Training 수same 입력 processing"""
        name = employee_data.get('Full Name', 'Unknown')
        emp_id = employee_data.get('Employee No', 'Unknown')
        position = employee_data.get('QIP POSITION 1ST  NAME', '')
        
        print(f"\n{'='*60}")
        print(f"Special case: AUDIT/TRAINING")
        print(f"Employee name: {name}")
        print(f"Employee No: {emp_id}")
        print(f"Position: {position}")
        
        try:
            incentive = self._get_manual_input(name)
            print(f"✅ Input incentive: {incentive:,.0f} VND")
            return incentive
        except Exception as e:
            print(f"❌ Input error: {e}")
            return 0
    
    def _get_manual_input(self, name: str) -> float:
        """수same 입력 받기"""
        while True:
            try:
                month_str = self.config.get_month_str("korean")
                user_input = input(f"\n{name}of {month_str} incentive amount 입력 (VND): ")
                if not user_input.strip():
                    if input("입력 없음. 0with processing? (y/n): ").lower() == 'y':
                        return 0
                    continue
                
                # 쉼표 제거 후 숫자 변환
                amount = float(user_input.replace(',', '').strip())
                if amount < 0:
                    print("❌ Cannot input negative numbers.")
                    continue
                    
                return amount
            except ValueError:
                print("❌ Please enter a valid number.")
                continue


class DataProcessor:
    """data processing 클래스 (improved 버전)"""

    def __init__(self, config: MonthConfig):
        self.config = config
        self.column_cache = {}
        self.progression_table = self._load_progression_table()
        print(f"✅ Progression table loaded: {len(self.progression_table)} entries")

    def _load_progression_table(self) -> dict:
        """
        progression_table을 position_condition_matrix.json에서 동적으로 로딩

        Returns:
            dict: {개월수(int): 인센티브금액(int)} 형태의 딕셔너리
        """
        try:
            config_path = "config_files/position_condition_matrix.json"

            if not os.path.exists(config_path):
                print(f"⚠️ Warning: {config_path} not found. Using default progression table.")
                # 기본값 (하드코딩 fallback)
                return {
                    0: 0, 1: 150000, 2: 250000, 3: 300000, 4: 350000,
                    5: 400000, 6: 450000, 7: 500000, 8: 650000, 9: 750000,
                    10: 850000, 11: 950000, 12: 1000000, 13: 1000000,
                    14: 1000000, 15: 1000000
                }

            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # progression_table 추출
            prog_table_str = config_data.get('incentive_progression', {}).get('TYPE_1_PROGRESSIVE', {}).get('progression_table', {})

            # 문자열 키 → 정수 키로 변환
            progression_table = {int(k): int(v) for k, v in prog_table_str.items()}

            return progression_table

        except Exception as e:
            print(f"⚠️ Error loading progression_table: {e}")
            print("Using default progression table.")
            return {
                0: 0, 1: 150000, 2: 250000, 3: 300000, 4: 350000,
                5: 400000, 6: 450000, 7: 500000, 8: 650000, 9: 750000,
                10: 850000, 11: 950000, 12: 1000000, 13: 1000000,
                14: 1000000, 15: 1000000
            }

    def _reverse_calculate_months_from_incentive(self, incentive_amount: float) -> int:
        """
        인센티브 금액에서 개월 수를 역산

        Args:
            incentive_amount: 인센티브 금액

        Returns:
            int: 해당 금액에 대응하는 개월 수 (찾지 못하면 1)
        """
        if pd.isna(incentive_amount) or incentive_amount <= 0:
            return 1

        incentive_int = int(float(incentive_amount))

        # progression_table에서 역산
        for months, amount in self.progression_table.items():
            if months == 0:
                continue
            if incentive_int == amount:
                return months + 1  # 다음 달 개월 수

        # 찾지 못한 경우
        print(f"  ⚠️ Incentive amount {incentive_int:,} VND not found in progression_table → defaulting to 1 month")
        print(f"  ⚠️ This may indicate a special bonus or manual adjustment. Manual verification recommended.")
        return 1
    
    def standardize_employee_id(self, emp_id: Any) -> str:
        """employee ID 표준화"""
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
        """columnemployees 자same detection (improved 버전)"""
        cache_key = f"{id(df)}_{','.join(target_patterns)}"
        if cache_key in self.column_cache:
            return self.column_cache[cache_key]
        
        df_columns = df.columns.tolist()
        
        # accurate matching 우선
        for pattern in target_patterns:
            if pattern in df_columns:
                self.column_cache[cache_key] = pattern
                return pattern
        
        # 대소문자 무시 matching
        for col in df_columns:
            col_upper = col.upper()
            for pattern in target_patterns:
                if pattern.upper() == col_upper:
                    self.column_cache[cache_key] = col
                    return col
        
        # 부분 matching
        for col in df_columns:
            col_clean = re.sub(r'[^a-zA-Z0-9]', '', col.upper())
            for pattern in target_patterns:
                pattern_clean = re.sub(r'[^a-zA-Z0-9]', '', pattern.upper())
                if pattern_clean in col_clean or col_clean in pattern_clean:
                    self.column_cache[cache_key] = col
                    return col
        
        return None
    
    def load_july_incentive_data(self):
        """July incentive data withload (August calculation 시 특별 processing)"""
        # August calculation 시toonly 실행
        if self.config.month.number == 8 and self.config.year == 2025:
            print("\n📊 July incentive Loading data (Single Source of Truth)...")
            july_file_path = self.base_path / "input_files" / "2025 July Incentive_final_Sep_15.csv"

            if july_file_path.exists():
                try:
                    july_df = pd.read_csv(july_file_path, encoding='utf-8-sig')
                    print(f"  ✅ July incentive file loaded successfully: {len(july_df)} employees")

                    # Employee No 표준화
                    july_df['Employee No'] = july_df['Employee No'].apply(
                        lambda x: str(int(x)).zfill(9) if pd.notna(x) else ''
                    )
                    self.month_data['Employee No'] = self.month_data['Employee No'].apply(
                        lambda x: str(int(x)).zfill(9) if pd.notna(x) else ''
                    )

                    # July_Incentive mapping
                    july_map = july_df.set_index('Employee No')['July_Incentive'].to_dict()
                    self.month_data['July_Incentive'] = self.month_data['Employee No'].map(july_map).fillna(0)

                    # 통계 출력
                    mapped_count = (self.month_data['July_Incentive'] > 0).sum()
                    zero_count = (self.month_data['July_Incentive'] == 0).sum()
                    print(f"  → July incentive mapping completed: {mapped_count}명 (>0), {zero_count}명 (=0)")

                    # DANH MINH HIẾU checking
                    hiếu_data = self.month_data[self.month_data['Employee No'] == '621030996']
                    if not hiếu_data.empty:
                        july_amt = hiếu_data.iloc[0]['July_Incentive']
                        print(f"  → DANH MINH HIẾU (621030996) July incentive: {july_amt:,.0f}VND")

                    return True

                except Exception as e:
                    print(f"  ❌ July incentive file load failed: {e}")
                    return False
            else:
                print(f"  ⚠️ July incentive file not found: {july_file_path}")
                return False

        # September 후 previous month Excelfrom 자동으로 읽음
        return True

    def process_attendance_conditions(self, att_df: pd.DataFrame) -> pd.DataFrame:
        """attendance condition processing (improved 버전)"""
        print("\n📊 Processing attendance conditions...")

        # minimum 근무 days수 condition apply 여부 안내
        from datetime import datetime
        current_date = datetime.now()
        if current_date.day < 20:
            print(f"  ℹ️ current date {current_date.day} th - Before 20th of every month, so minimum 12 days worked condition not applied.")
            print(f"     (interim exception processing for interim report creation)")
        else:
            print(f"  ℹ️ current date {current_date.day} th - Minimum 12 days worked condition normally applied.")
        
        # employee ID column 찾기 (ID No 우선with)
        emp_col = self.detect_column_names(att_df, [
            'ID No', 'Employee No', 'EMPLOYEE NO', 'EMPLOYEE_NO', 'EMP_NO', 
            'EMPLOYEE ID', 'EMPLOYEE_ID', 'ID',
            'WORKER ID', 'STAFF ID'
        ])
        
        if not emp_col:
            print("❌ employee ID column not found.")
            return pd.DataFrame()
        
        # Stop working employee 목록 져오기 (month_datafrom)
        stop_working_employees = set()
        if hasattr(self, 'month_data') and 'Stop working Date' in self.month_data.columns:
            stop_working_mask = self.month_data['Stop working Date'].notna() & (self.month_data['Stop working Date'] != '')
            stop_working_employees = set(self.month_data[stop_working_mask]['Employee No'].astype(str))
            print(f"  → Stop working employee {len(stop_working_employees)}명 excluded from processing")
        
        # converted file 형식 체크
        if 'ACTUAL WORK DAY' in att_df.columns and 'TOTAL WORK DAY' in att_df.columns:
            # 미 converted file
            print("✅ converted attendance file detected")
            attendance_results = []
            
            for idx, row in att_df.iterrows():
                emp_id = self.standardize_employee_id(row[emp_col])
                if not emp_id or emp_id == '0':
                    continue

                # Stop working employeealso 정상 processing (exclude하지 않음)

                actual_days = float(row.get('ACTUAL WORK DAY', 0))
                total_days = float(row.get('TOTAL WORK DAY', 27))  # defaultvalue 27with 변경
                
                # 새with운 column processing
                ar1_absences = float(row.get('AR1 Absences', 0))
                unapproved_absences = float(row.get('Unapproved Absences', 0))
                absence_rate = float(row.get('Absence Rate (%)', 0))
                
                # previous 형식andof 호환성 위해
                if 'Absence (without permission) time' in row:
                    unapproved_absences = float(row.get('Absence (without permission) time', 0))
                if 'Absence (without permission) Ratio (%)' in row:
                    absence_rate = float(row.get('Absence (without permission) Ratio (%)', 0))
                
                # 실제 근무 days 전체 근무 days보다 많은 경우 조정
                if actual_days > total_days:
                    actual_days = total_days
                    absence_rate = 0  # 전체 근무 days 상 근무한 경우 absence rate 0
                
                # 음수 absence rate은 0with processing
                if absence_rate < 0:
                    absence_rate = 0
                
                # minimum 근무 days수 condition date basedwith apply
                from datetime import datetime
                current_date = datetime.now()

                # Check if we're calculating for current month or past month
                is_current_month = (current_date.year == self.config.year and
                                   current_date.month == self.config.month.number)

                if is_current_month:
                    # Current month: apply condition only after 20th (interim vs final report)
                    apply_min_days_condition = current_date.day >= 20
                else:
                    # Past month: always apply normal conditions
                    apply_min_days_condition = True

                # condition 체크 (AR1 무단결근 사용)
                cond1_fail = actual_days <= 0
                cond2_fail = ar1_absences > 2  # AR1 무단결근 2 days 초and
                cond3_fail = absence_rate > 12  # absence rate 12% 초and

                # minimum 근무 days condition: 20 days 후toonly apply
                if apply_min_days_condition:
                    cond4_fail = actual_days < 12  # minimum 근무 days 12 days 미only
                else:
                    cond4_fail = False  # 20 days previousto condition 미apply

                attendance_results.append({
                    'Employee No': emp_id,
                    'Total Working Days': total_days,
                    'Actual Working Days': actual_days,
                    'AR1 Absences': ar1_absences,
                    'Unapproved Absences': unapproved_absences,
                    '결근율_Absence_Rate_Percent': absence_rate
                    # 레거시 컬럼 삭제: cond_1~10 표준 컬럼으로 통합
                })
            
            result_df = pd.DataFrame(attendance_results)
            print(f"✅ Attendance condition processing completed: {len(result_df)} employees")
            return result_df
        
        # original  days별 data processing (existing 코load)
        # Work Date column include하여 date column 찾기
        date_columns = []
        
        # first employees시적인 date columnemployees checking
        known_date_cols = ['Work Date', 'WorkDate', 'Date', 'date', ' days자']
        for col in att_df.columns:
            if col in known_date_cols:
                date_columns.append(col)
        
        # 없으면 패턴with 찾기
        if not date_columns:
            date_patterns = [r'\d{1,2}[-/]\d{1,2}', r'\d{4}[-/]\d{2}[-/]\d{2}']
            for col in att_df.columns:
                for pattern in date_patterns:
                    if re.search(pattern, str(col)):
                        date_columns.append(col)
                        break
        
        if not date_columns:
            print("❌ Date column not found.")
            return pd.DataFrame()
        
        attendance_results = []
        
        # employee별 processing
        for emp_id in att_df[emp_col].unique():
            if pd.isna(emp_id):
                continue
            
            emp_id = self.standardize_employee_id(emp_id)
            if not emp_id:
                continue
            
            # Stop working employeealso 정상 processing (exclude하지 않음)
            
            # defaultvalue configuration
            total_working_days = self.config.working_days
            actual_working_days = 0
            unapproved_absence = 0
            
            # 타입 호환성 위해 attendance dataof IDalso 문자열with 변환하여 matching
            emp_data = att_df[att_df[emp_col].astype(str).str.zfill(9) == emp_id]
            
            # 방어적 코ing: attendance data 없 employee processing
            if emp_data.empty:
                print(f"⚠️ Attendance data not found: {emp_id}")
                # attendance data 없 employee은 0 dayswith processing하고 next employeewith
                continue
            
            # 실제 attendance datafrom attendance/결근 calculation
            # in progress요: 같은 date 여러 번 나올 수 있으므with unique한 dateonly 카운트
            worked_dates = set()  # in progress복 제거 위한 set 사용

            if 'compAdd' in emp_data.columns:
                # Date column 있지 checking (Work Date 추)
                date_col = None
                for possible_date_col in ['Work Date', 'Date', 'date', 'DATE', 'Ngày', 'ngày', 'WorkDate']:
                    if possible_date_col in emp_data.columns:
                        date_col = possible_date_col
                        break

                if date_col:
                    # Total Working Days config.working_days 사용
                    # (attendance fileof 레코load 수 사용하면 approved leave 미 include되어 있어서
                    #  나in progressto approved leave 빼면 음수 done)
                    # total_working_days Line 715from 미 config.working_dayswith configurationdone

                    # Date column 있으면 date별with 유니크하게 카운트
                    for idx, row in emp_data.iterrows():
                        comp_add = row['compAdd']
                        work_date = row[date_col]
                        # Reason Description columnalso checking (출장 체크용)
                        reason_desc = row.get('Reason Description', '') if 'Reason Description' in row else ''

                        if pd.notna(comp_add):
                            comp_str = str(comp_add).strip()
                            reason_str = str(reason_desc).strip() if pd.notna(reason_desc) else ''

                            # attendance 체크 ('Đi làm' = attendance)
                            if comp_str == 'Đi làm' and pd.notna(work_date):
                                worked_dates.add(str(work_date))  # date setto 추 (in progress복 자same 제거)
                            # 출장 체크 ('Đi công tác' in Reason Description = 출장also attendancewith processing)
                            elif reason_str == 'Đi công tác' and pd.notna(work_date):
                                worked_dates.add(str(work_date))  # 출장also attendancewith processing
                            # 결근 체크 (Vắng mặt = 결근)
                            elif comp_str == 'Vắng mặt':
                                # AR1 무단결근 체크 (Reason Descriptionto AR1 있으면 무단결근)
                                if 'AR1' in reason_str or 'Vắng không phép' in reason_str or 'không phép' in reason_str.lower():
                                    unapproved_absence += 1

                    # 유니크한 attendance dateof items수 실제 근무 days
                    actual_working_days = len(worked_dates)
                else:
                    # Date column 없으면 existing 방식 사용 (하지only Warning 출력)
                    print(f"⚠️ Date column 없어 Accurate attendance days calculation may be difficult: {emp_id}")
                    for idx, row in emp_data.iterrows():
                        comp_add = row['compAdd']
                        reason_desc = row.get('Reason Description', '') if 'Reason Description' in row else ''

                        if pd.notna(comp_add):
                            comp_str = str(comp_add).strip()
                            reason_str = str(reason_desc).strip() if pd.notna(reason_desc) else ''

                            # attendance 체크
                            if comp_str == 'Đi làm':
                                actual_working_days += 1
                            # 출장 체크 (Reason Description checking)
                            elif reason_str == 'Đi công tác':
                                actual_working_days += 1
                            # 결근 체크 (Vắng mặt = 결근)
                            elif comp_str == 'Vắng mặt':
                                # AR1 무단결근 체크 (Reason Descriptionto AR1 있으면 무단결근)
                                if 'AR1' in reason_str or 'Vắng không phép' in reason_str or 'không phép' in reason_str.lower():
                                    unapproved_absence += 1
            
            # 실제 근무 days 전체 근무 days보다 많은 경우 조정
            if actual_working_days > total_working_days:
                actual_working_days = total_working_days
            
            # absence rate calculation
            if total_working_days > 0:
                absence_rate = ((total_working_days - actual_working_days) / total_working_days) * 100
            else:
                absence_rate = 0
            
            # 음수 absence rate은 0with processing
            if absence_rate < 0:
                absence_rate = 0
            
            # date basedwith condition apply 여부 결정
            from datetime import datetime
            current_date = datetime.now()

            # every month 20 days previous: interim 보고서with 간주, condition 완화
            # every month 20 days 후: 정상 condition apply
            # Check if we're calculating for current month or past month
            is_current_month = (current_date.year == self.config.year and
                               current_date.month == self.config.month.number)

            if is_current_month:
                # Current month: interim report before 20th
                is_mid_month_report = current_date.day < 20
            else:
                # Past month: always apply full conditions
                is_mid_month_report = False

            if is_mid_month_report:
                # monthin progress 보고서: minimum 근무 days 및 absence rate condition 미apply
                min_days_condition = 'no'  # minimum 12 days condition 미apply
                # absence rate conditionalso 완화: 실제 data 기간 짧아 absence rate 높게 나올 수 있음
                absence_rate_condition = 'no'  # absence rate condition 미apply
            else:
                # month말 보고서: 정상 condition apply
                min_days_condition = 'yes' if actual_working_days < 12 else 'no'
                absence_rate_condition = 'yes' if absence_rate > 12 else 'no'

            attendance_results.append({
                'Employee No': emp_id,
                'Total Working Days': total_working_days,
                'Actual Working Days': actual_working_days,
                'AR1 Absences': unapproved_absence,  # AR1 absences are the unapproved absences
                'Unapproved Absences': unapproved_absence,
                '결근율_Absence_Rate_Percent': round(absence_rate, 2)
                # 레거시 컬럼 삭제: cond_1~10 표준 컬럼으로 통합
            })
        
        result_df = pd.DataFrame(attendance_results)
        print(f"✅ Attendance condition processing completed: {len(result_df)} employees")
        return result_df
    
    def process_5pairs_conditions(self, prs_df: pd.DataFrame) -> pd.DataFrame:
        """5PRS conditions processing - TQC ID (inspection 대상자) basis"""
        print("\n📊 5PRS Processing conditions...")

        # ✅ CRITICAL FIX: 해당 월 데이터만 필터링 (다른 달 데이터 제외)
        if 'Inspection Date' in prs_df.columns:
            # 날짜 컬럼을 datetime으로 변환
            prs_df['Inspection Date'] = pd.to_datetime(
                prs_df['Inspection Date'],
                format='%m/%d/%Y',
                errors='coerce'
            )

            # 해당 년도/월 데이터만 필터링
            target_year = self.config.year
            target_month = self.config.month.number

            original_count = len(prs_df)
            prs_df = prs_df[
                (prs_df['Inspection Date'].dt.year == target_year) &
                (prs_df['Inspection Date'].dt.month == target_month)
            ].copy()
            filtered_count = len(prs_df)

            excluded = original_count - filtered_count
            print(f"  ✅ 5PRS 데이터 월별 필터링: {original_count}개 → {filtered_count}개 (제외: {excluded}개)")

            if excluded > 0:
                print(f"  ⚠️ 다른 달 데이터 {excluded}개 제외됨 (정확한 계산을 위해 필수)")
        else:
            print("  ⚠️ Warning: 'Inspection Date' 컬럼이 없어 월별 필터링 불가")
            print("     전체 데이터 사용 - 결과가 부정확할 수 있음!")

        # TQC ID inspection 대상자 (Assembly Inspector etc.)
        # Inspector ID inspection 수행자 (Auditor/Trainer)

        # TQC ID column 찾기 (inspection 대상자)
        tqc_col = self.detect_column_names(prs_df, [
            'TQC ID', 'TQC_ID', 'TQC', 'Target ID'
        ])
        
        if not tqc_col:
            print("⚠️ TQC ID column not found. Inspector IDreplacement attempt with...")
            # Fallback: Inspector ID 사용 (previous 버전 호환)
            tqc_col = self.detect_column_names(prs_df, [
                'Inspector ID', 'INSPECTOR_ID', 'Inspector'
            ])
            if not tqc_col:
                print("❌ employee ID column not found.")
                return pd.DataFrame()
        
        # inspection량and passed량 column 찾기
        val_qty_col = self.detect_column_names(prs_df, [
            'Valiation Qty', 'Validation Qty', 'Val Qty',
            'Total Valiation Qty', 'Total Validation Qty'
        ])
        
        pass_qty_col = self.detect_column_names(prs_df, [
            'Pass Qty', 'Passed Qty', 'Pass',
            'Total Pass Qty', 'PASS QTY'
        ])
        
        # TQC별 집계 필요한지 checking
        if val_qty_col and pass_qty_col:
            # TQC별with 그룹화하여 합계 calculation
            print(f"  - TQC ID basiswith aggregating... (column: {tqc_col})")
            grouped = prs_df.groupby(tqc_col).agg({
                val_qty_col: 'sum',
                pass_qty_col: 'sum'
            }).reset_index()
            
            grouped.columns = [tqc_col, 'Total Valiation Qty', 'Total Pass Qty']
        else:
            # 미 집계done data인 경우
            grouped = prs_df.copy()
            
            # columnemployees 표준화
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
            
            # condition 체크 - 5PRS inspection량 100items 상 AND passed율 95% 상 필요
            condition1 = 'yes' if (total_qty >= 100 and pass_rate >= 95) else 'no'
            condition2 = 'yes' if total_qty == 0 else 'no'
            
            prs_results.append({
                'Employee No': emp_id,
                'Total Valiation Qty': total_qty,
                'Total Pass Qty': pass_qty,
                'Pass %': round(pass_rate, 2),
                '5PRS_Pass_Rate': round(pass_rate, 2),  # 표준화done columnemployees 추
                '5PRS_Inspection_Qty': total_qty,  # 표준화done columnemployees 추
                '5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%': condition1,
                '5prs condition 2 - Total Valiation Qty is zero': condition2
            })
        
        result_df = pd.DataFrame(prs_results)
        print(f"✅ 5PRS conditions processing completed: {len(result_df)} employees (TQC basis)")
        return result_df
    
    
    def calculate_continuous_months_from_history(self, emp_id: str, month_data: pd.DataFrame = None) -> int:
        """
        연속 인센티브 수령 개월 수 계산 (우선순위 기반 로직)

        우선순위 (수정: 2025-11-19 - Continuous_Months가 더 신뢰성 높음):
        1. Continuous_Months 컬럼 + 1 (가장 신뢰성 높음)
        2. Next_Month_Expected 컬럼 직접 읽기 (fallback)
        3. 인센티브 금액 역산 (progression_table 동적 사용)

        Args:
            emp_id: 직원 ID
            month_data: 현재 달 데이터 (옵션)

        Returns:
            int: 다음 달 연속 개월 수 (1-15)
        """
        continuous_months = 0

        # month_data 전달되지 않으면 self.month_data 사용 (호환성 유지)
        if month_data is None and hasattr(self, 'month_data'):
            month_data = self.month_data

        # Employee ID 9자리 패딩
        emp_id_padded = str(emp_id).zfill(9)

        # ============================================
        # 이전 달 데이터 로딩
        # ============================================
        prev_df, prev_month_name = self._load_previous_month_data()

        if prev_df is None or prev_df.empty:
            print(f"[New Employee] {emp_id_padded}: No previous month data → Starting at 1 month")
            return 1

        # 이전 달에서 해당 직원 찾기
        emp_prev = prev_df[prev_df['Employee No'] == emp_id_padded]

        if emp_prev.empty:
            print(f"[New Employee] {emp_id_padded}: Not found in {prev_month_name} data → Starting at 1 month")
            return 1

        prev_row = emp_prev.iloc[0]

        # ============================================
        # 우선순위 1: Continuous_Months + 1 (가장 신뢰성 높음)
        # ============================================
        if 'Continuous_Months' in prev_df.columns:
            cont_months = prev_row.get('Continuous_Months', 0)
            if pd.notna(cont_months) and cont_months != '' and float(cont_months) >= 0:
                continuous_months = int(cont_months) + 1
                print(f"✅ {emp_id_padded}: [Priority 1] Continuous_Months + 1 → {int(cont_months)} + 1 = {continuous_months} months")
                return continuous_months

        # ============================================
        # 우선순위 2: Next_Month_Expected 컬럼 (fallback)
        # ============================================
        if 'Next_Month_Expected' in prev_df.columns:
            next_expected = prev_row.get('Next_Month_Expected', 0)
            if pd.notna(next_expected) and next_expected != '' and float(next_expected) > 0:
                continuous_months = int(next_expected)
                print(f"✅ {emp_id_padded}: [Priority 2] Next_Month_Expected column → {continuous_months} months")
                return continuous_months

        # ============================================
        # 우선순위 3: 인센티브 금액 역산
        # ============================================
        # 이전 달 인센티브 금액 확인 (여러 가능한 컬럼명 시도)
        incentive_columns = [
            f'{prev_month_name}_Incentive',
            f'{prev_month_name.capitalize()}_Incentive',
            'Final Incentive amount',
            'incentive 지급액',
            'Source_Final_Incentive'
        ]

        prev_incentive = None
        for col_name in incentive_columns:
            if col_name in prev_df.columns:
                val = prev_row.get(col_name, 0)
                if pd.notna(val) and val != '' and float(val) > 0:
                    prev_incentive = float(val)
                    print(f"  📊 {emp_id_padded}: Found incentive in column '{col_name}': {prev_incentive:,.0f} VND")
                    break

        if prev_incentive is not None and prev_incentive > 0:
            continuous_months = self._reverse_calculate_months_from_incentive(prev_incentive)
            print(f"✅ {emp_id_padded}: [Priority 3] Reverse calculation from {prev_incentive:,.0f} VND → {continuous_months} months")
            return continuous_months

        # ============================================
        # Fallback: 데이터 없음 → 1개월로 시작
        # ============================================
        print(f"⚠️ {emp_id_padded}: No valid data in {prev_month_name} → Defaulting to 1 month")
        return 1

    def _load_previous_month_data(self) -> tuple:
        """
        이전 달 데이터 로딩 헬퍼 메서드

        Returns:
            tuple: (DataFrame, month_name) 또는 (None, None)
        """
        # 이전 달 계산
        prev_month_num = (self.config.month.number - 1) % 12 or 12
        prev_year = self.config.year if prev_month_num < self.config.month.number else self.config.year - 1
        prev_month_obj = Month.from_number(prev_month_num)
        prev_month_name = prev_month_obj.full_name.lower()

        # ============================================
        # Case 1: August 계산 - July_Incentive 컬럼 사용
        # ============================================
        if self.config.month.number == 8 and self.config.year == 2025:
            if hasattr(self, 'month_data') and self.month_data is not None:
                if 'July_Incentive' in self.month_data.columns:
                    print(f"📂 August calculation: Using July_Incentive column from current month_data")
                    # Employee No 표준화
                    if 'Employee No' in self.month_data.columns:
                        self.month_data['Employee No'] = self.month_data['Employee No'].astype(str).str.zfill(9)
                    return (self.month_data.copy(), 'july')

            print(f"⚠️ August calculation: July_Incentive column not found in month_data")
            return (None, None)

        # ============================================
        # Case 2: September 이후 - 이전 달 CSV/Excel 파일 로딩
        # ============================================
        if self.config.month.number == 9 and self.config.year == 2025:
            # September: August CSV 파일 로딩
            august_file = self.config.file_paths.get('previous_incentive',
                                                     'input_files/2025년 8월 인센티브 지급 세부 정보.csv')

            if os.path.exists(august_file):
                try:
                    print(f"📂 September calculation: Loading August CSV from {august_file}")
                    august_df = pd.read_csv(august_file, encoding='utf-8-sig')

                    # Employee No 표준화
                    if 'Employee No' in august_df.columns:
                        august_df['Employee No'] = august_df['Employee No'].astype(str).str.zfill(9)

                    return (august_df, 'august')

                except Exception as e:
                    print(f"⚠️ Error loading August CSV: {e}")
                    return (None, None)
            else:
                print(f"⚠️ August CSV file not found: {august_file}")
                return (None, None)

        # ============================================
        # Case 3: October 이후 - 이전 달 Excel/CSV 파일 로딩
        # ============================================
        # Fallback pattern: 최신 버전 우선 (V9.1 → V9.0 → V8.02 → V8.01)
        excel_patterns = [
            # V9.1 버전 (최신)
            f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.1_Complete.csv",
            f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.1_Complete.csv",
            # V9.0 버전
            f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
            f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V9.0_Complete.csv",
            # V8.02 버전 (하위 호환성)
            f"output_files/output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv",
            f"output_QIP_incentive_{prev_month_name}_{prev_year}_Complete_V8.02_Complete.csv"
        ]

        for excel_path in excel_patterns:
            if os.path.exists(excel_path):
                try:
                    print(f"📂 Loading previous month data from {os.path.basename(excel_path)}")
                    prev_df = pd.read_csv(excel_path, encoding='utf-8-sig')

                    # Employee No 표준화
                    if 'Employee No' in prev_df.columns:
                        prev_df['Employee No'] = prev_df['Employee No'].apply(
                            lambda x: str(int(x)).zfill(9) if pd.notna(x) else ''
                        )

                    return (prev_df, prev_month_name)

                except Exception as e:
                    print(f"⚠️ Error loading {excel_path}: {e}")
                    continue

        # 파일을 찾지 못함
        print(f"⚠️ Previous month CSV not found for {prev_month_name} {prev_year}")
        return (None, None)
    
    def process_aql_conditions_with_history(self, aql_df: pd.DataFrame = None) -> pd.DataFrame:
        """AQL history file 활용한 3-month consecutive failure 체크"""
        print("\n📊 AQL History Checking 3-month consecutive failures based on files...")
        
        import tempfile
        import os
        import glob
        import re
        
        def load_aql_history(month_name):
            """AQL history file withload (헤더 processing include)

            개선사항 (2025-10-07):
            - Mixed-month 데이터 자동 필터링
            - October 2025 이슈 재발 방지
            """
            file_path = f'input_files/AQL history/1.HSRG AQL REPORT-{month_name}.2025.csv'

            if not os.path.exists(file_path):
                return None

            try:
                # file 텍스트with first 읽어서 헤더 processing
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()

                # 임시 fileto 정리done data 쓰기
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as tmp:
                    # 실제 파일의 헤더 사용 (1-2번째 줄 결합)
                    # 1번째 줄과 2번째 줄을 결합하여 완전한 헤더 생성
                    header_line1 = lines[0].rstrip('\n').rstrip('\r')
                    header_line2 = lines[1].rstrip('\n').rstrip('\r')

                    # 2번째 줄이 quote로 시작하는 경우 처리
                    if header_line2.startswith('"') or header_line2.startswith('NO"'):
                        # 이전 줄의 마지막 필드와 결합
                        full_header = header_line1 + header_line2
                    else:
                        full_header = header_line1 + ',' + header_line2

                    tmp.write(full_header + '\n')

                    # data 라인들 쓰기 (3번째 줄from)
                    for line in lines[2:]:
                        tmp.write(line)
                    tmp_path = tmp.name

                # 임시 파일에서 data 읽기
                df = pd.read_csv(tmp_path)
                os.unlink(tmp_path)  # 임시 file 삭제

                # ==========================================
                # 자동 필터링 로직 추가 (2025-10-07)
                # ==========================================
                if 'MONTH' in df.columns and not df.empty:
                    # 파일명에서 예상되는 월 번호 추출
                    month_map = {
                        'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
                        'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
                        'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
                    }

                    expected_month = month_map.get(month_name.upper())

                    if expected_month is not None:
                        # 전체 행의 MONTH 값 확인
                        unique_months = df['MONTH'].dropna().unique()

                        # Mixed-month 데이터 검출 시 자동 필터링
                        if len(unique_months) > 1:
                            original_count = len(df)
                            df = df[df['MONTH'] == expected_month].copy()

                            # Silent filtering (get_latest_three_months에서 이미 출력했으므로)
                            # 단, 레코드가 완전히 사라진 경우만 경고
                            if len(df) == 0:
                                print(f"       ⚠️ {month_name}: All records filtered out (no matching month)")
                                return None

                return df

            except Exception as e:
                return None
        
        def get_latest_three_months():
            """최신 3-month 자same 선택 (fileemployeesand MONTH column validation)

            개선사항 (2025-10-07):
            - 첫 행뿐만 아니라 전체 행의 MONTH 값 검증
            - Mixed-month 데이터 자동 필터링
            - October 2025 이슈 재발 방지
            """
            print("\n  🔍 Scanning AQL history files...")

            # AQL history 폴더of 모든 CSV file 찾기
            files = glob.glob('input_files/AQL history/*.csv')

            month_map = {
                1: 'JANUARY', 2: 'FEBRUARY', 3: 'MARCH', 4: 'APRIL',
                5: 'MAY', 6: 'JUNE', 7: 'JULY', 8: 'AUGUST',
                9: 'SEPTEMBER', 10: 'OCTOBER', 11: 'NOVEMBER', 12: 'DECEMBER'
            }

            valid_months = {}

            for file_path in files:
                # fileemployeesfrom month 추출 (예: "1.HSRG AQL REPORT-JULY.2025.csv" → "JULY")
                match = re.search(r'AQL REPORT-([A-Z]+)\.', os.path.basename(file_path))
                if match:
                    filename_month = match.group(1)

                    # file withload
                    df = load_aql_history(filename_month)
                    if df is not None and not df.empty:
                        # ==========================================
                        # 개선된 검증 로직 (2025-10-07)
                        # ==========================================

                        # 1. 첫 행 MONTH 확인 (기존 로직 호환)
                        first_month = df['MONTH'].iloc[0]

                        # 2. 전체 행의 MONTH 확인 (NEW - October 2025 문제 방지)
                        unique_months = df['MONTH'].dropna().unique()

                        # 3. 파일명과 일치하는 월 번호 찾기
                        expected_month_num = None
                        for num, name in month_map.items():
                            if name.upper() == filename_month.upper():
                                expected_month_num = num
                                break

                        if expected_month_num is None:
                            print(f"    ⚠️ {filename_month}: Unknown month name")
                            continue

                        # 4. Mixed-month 데이터 검출 및 자동 필터링
                        if len(unique_months) > 1:
                            print(f"    ⚠️ {filename_month}: Multiple months detected - {sorted([int(m) for m in unique_months])}")

                            # 올바른 월만 필터링
                            original_count = len(df)
                            df = df[df['MONTH'] == expected_month_num].copy()
                            filtered_count = original_count - len(df)

                            print(f"       → Auto-filtered: removed {filtered_count} records from other months")
                            print(f"       → Keeping {len(df)} records for month {expected_month_num}")

                            if len(df) == 0:
                                print(f"    ❌ {filename_month}: No valid records after filtering")
                                continue

                        # 5. 첫 행 검증 (기존 로직)
                        month_value = df['MONTH'].iloc[0]

                        if pd.notna(month_value):
                            month_num = int(month_value)
                            month_name = month_map.get(month_num, '')

                            # 6. 최종 검증: 파일명 == MONTH 컬럼
                            if filename_month.upper() == month_name.upper():
                                valid_months[month_num] = filename_month
                                print(f"    ✅ {filename_month}: validation passed (MONTH={month_num})")
                            else:
                                print(f"    ⚠️ {filename_month}: 불 days치 - fileemployees={filename_month}, MONTH column={month_name}")

            if not valid_months:
                print("    ❌ No valid AQL history files available.")
                return None

            # 최신 3-month 선택
            sorted_months = sorted(valid_months.keys(), reverse=True)[:3]
            latest_three = [valid_months[m] for m in sorted(sorted_months)]

            print(f"    📅 최신 3-month 선택: {latest_three}")
            return latest_three
        
        # 1. 최신 3-month 자same 선택
        latest_months = get_latest_three_months()
        
        if not latest_months or len(latest_months) < 3:
            # 폴백: 하load코ingdone month 사용
            print("  ⚠️ Auto-selection failed, using default values (MAY, JUNE, JULY)")
            latest_months = ['MAY', 'JUNE', 'JULY']
        
        # 2. 3-month AQL history file withload
        month_dfs = {}
        for month_name in latest_months:
            df = load_aql_history(month_name)
            if df is not None:
                month_dfs[month_name] = df
                # 빈 행 제거한 실제 data cases수 표시
                valid_rows = df.dropna(how='all')
                print(f"  ✅ {month_name} AQL history withload: {len(valid_rows)}cases")
            else:
                print(f"  ⚠️ {month_name} AQL history file load failed")
        
        # 3-month 모두 withload되었지 checking
        if len(month_dfs) < 3:
            print("  ❌ Cannot load all required AQL history files. Processing with legacy method.")
            return self.process_aql_conditions(aql_df)
        
        # month별 DataFrame 할당 (latest_months 순서대with)
        month1_df = month_dfs[latest_months[0]]
        month2_df = month_dfs[latest_months[1]]
        month3_df = month_dfs[latest_months[2]]
        
        # 2. 각 monthof failures 추출
        def get_failures(df, month_name):
            """각 monthof failure employeeand cases수 추출"""
            failures = {}
            
            # EMPLOYEE NO 유효한 dataonly 필터링
            valid_df = df[df['EMPLOYEE NO'].notna()].copy()
            valid_df['EMPLOYEE NO'] = valid_df['EMPLOYEE NO'].astype(str).str.strip()
            
            # employee별 failure cases수 calculation
            for emp_id_raw in valid_df['EMPLOYEE NO'].unique():
                if emp_id_raw == 'nan' or len(emp_id_raw) < 3:
                    continue
                
                # 9자리with 패ing
                emp_id = emp_id_raw.split('.')[0].zfill(9)  # float 형식 processing
                
                # original IDwith 검색
                emp_data = valid_df[valid_df['EMPLOYEE NO'].astype(str).str.strip() == emp_id_raw]
                fail_count = len(emp_data[emp_data['RESULT'].str.upper() == 'FAIL'])
                
                if fail_count > 0:
                    failures[emp_id] = fail_count
            
            print(f"  → {month_name}: {len(failures)}명 failure")
            return failures
        
        # 각 monthof failures 추출
        month1_failures = get_failures(month1_df, latest_months[0])
        month2_failures = get_failures(month2_df, latest_months[1])
        month3_failures = get_failures(month3_df, latest_months[2])
        
        # 3. 3-month consecutive failures 찾기
        continuous_fail_employees = set()

        # 모든 employee ID 수집 (current month basiswith 모든 employee include)
        all_employees = set(month1_failures.keys()) | set(month2_failures.keys()) | set(month3_failures.keys())

        for emp_id in all_employees:
            month1_fail = month1_failures.get(emp_id, 0) > 0
            month2_fail = month2_failures.get(emp_id, 0) > 0
            month3_fail = month3_failures.get(emp_id, 0) > 0

            if month1_fail and month2_fail and month3_fail:
                continuous_fail_employees.add(emp_id)
                print(f"    ✅ {emp_id}: 3-month consecutive failure ({latest_months[0]}:{month1_failures.get(emp_id)}cases, {latest_months[1]}:{month2_failures.get(emp_id)}cases, {latest_months[2]}:{month3_failures.get(emp_id)}cases)")

        print(f"\n  📊 3-month consecutive failures: {len(continuous_fail_employees)}명")

        # 4. 결and DataFrame created (BUILDING 정보 include)
        aql_results = []
        current_month_fail_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # 최신 month(3번째 month) datafrom BUILDING 정보 추출
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
        
        # previous monthfromalso BUILDING 정보 수집 (최신 monthto 없 경우 대비)
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
        
        # 모든 employeeof 결and include (failure 없더라also)
        # first default data프레임from 모든 employee ID 져오기
        if self.df is not None and 'Employee No' in self.df.columns:
            all_company_employees = self.df['Employee No'].unique()
        else:
            all_company_employees = []

        # 모든 employee ID 통합 (AQL data + 회사 전체 employee)
        all_employees_combined = set(all_employees)
        for emp_id in all_company_employees:
            if pd.notna(emp_id):
                emp_id_str = str(emp_id).strip().zfill(9)
                all_employees_combined.add(emp_id_str)

        for emp_id in all_employees_combined:
            continuous_fail = 'YES' if emp_id in continuous_fail_employees else 'NO'
            # 최신 month(3번째 month)of failure cases수
            current_month_fail_count = month3_failures.get(emp_id, 0)

            aql_results.append({
                'Employee No': emp_id,
                current_month_fail_col: current_month_fail_count,
                'Continuous_FAIL': continuous_fail,
                'BUILDING': employee_buildings.get(emp_id, '')
            })
        
        result_df = pd.DataFrame(aql_results)
        print(f"✅ AQL History based processing completed: {len(result_df)}명")
        return result_df
    
    def process_aql_conditions(self, aql_df: pd.DataFrame, historical_incentive_df: pd.DataFrame = None) -> pd.DataFrame:
        """AQL condition processing (existing 방식 - previous incentive file based)"""
        print("\n📊 AQL Processing conditions...")
        
        # employee ID column 찾기 (AQL data 'EMPLOYEE NO' 사용)
        emp_col = self.detect_column_names(aql_df, [
            'EMPLOYEE NO', 'EMPLOYEE_NO', 'EMP_NO',
            'EMPLOYEE ID', 'EMPLOYEE_ID', 'ID',
            'Employee No', 'Personnel Number',
            'employee no'  # 소문자 버전also 추
        ])
        
        if not emp_col:
            print("❌ employee ID column not found.")
            return pd.DataFrame()
        
        # AQL dataof employee 번호 문자열with 변환 (float processing)
        aql_df[emp_col] = aql_df[emp_col].fillna(0).astype(float).astype(int).astype(str).str.zfill(9)
        
        aql_results = []
        current_month_fail_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # current month failure cases수 processing
        for emp_id in aql_df[emp_col].unique():
            if pd.isna(emp_id) or emp_id == '000000000':
                continue
            
            # 미 표준화done emp_id 사용
            if not emp_id:
                continue
            
            emp_data = aql_df[aql_df[emp_col] == emp_id]
            # 대소문자 호환성 위해 RESULTand FAIL 대문자with processing
            if 'RESULT' in emp_data.columns:
                # 'F' 또 'FAIL' 둘 다 processing
                fail_condition = (emp_data['RESULT'] == 'F') | (emp_data['RESULT'] == 'FAIL')
                current_fail_count = len(emp_data[fail_condition])
            elif 'Result' in emp_data.columns:
                # 'F' 또 'FAIL' 둘 다 processing (대소문자 무관)
                fail_condition = (emp_data['Result'].str.upper() == 'F') | (emp_data['Result'].str.upper() == 'FAIL')
                current_fail_count = len(emp_data[fail_condition])
            else:
                current_fail_count = 0
            
            # previous month failure data checking
            continuous_fail = 'NO'
            
            if historical_incentive_df is not None and len(self.config.previous_months) > 0:
                # previous month들of failure cases수 checking
                prev_fails = []
                
                # debugging: TRẦN VĂN HÀto 대해 출력
                if emp_id == '624040283':
                    print(f"    → TRẦN VĂN HÀ ({emp_id}) - previous month failure checking in progress...")
                    print(f"      current month(July) failure: {current_fail_count}cases")
                    print(f"      사용 능한 column: {[col for col in historical_incentive_df.columns if 'Failures' in col or 'may' in col.lower() or 'jun' in col.lower()]}")
                
                for prev_month in self.config.previous_months:
                    # 여러 능한 columnemployees 형식 attempt
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
                        # debugging: TRẦN VĂN HÀto 대해 출력
                        if emp_id == '624040283':
                            print(f"    → {prev_month.full_name} failure data column: {prev_col}")
                    
                    if prev_col:
                        # historical_incentive_dffrom employee ID column 찾기
                        hist_emp_col = self.detect_column_names(historical_incentive_df, [
                            'Employee No', 'Employee ID', 'EMPLOYEE NO', 
                            'Employee_No', 'Personnel Number'
                        ])
                        
                        if hist_emp_col:
                            # employee ID 표준화 (9자리)
                            historical_incentive_df[hist_emp_col] = historical_incentive_df[hist_emp_col].astype(str).str.strip().str.zfill(9)
                            hist_data = historical_incentive_df[
                                historical_incentive_df[hist_emp_col] == emp_id
                            ]
                            if not hist_data.empty:
                                prev_fail = hist_data.iloc[0].get(prev_col, 0)
                                if emp_id == '624040283':
                                    print(f"      {prev_month.full_name} failure cases수: {prev_fail}")
                                prev_fails.append(prev_fail > 0)
                            else:
                                if emp_id == '624040283':
                                    print(f"      {prev_month.full_name}: data not found")
                                prev_fails.append(False)
                        else:
                            prev_fails.append(False)
                    else:
                        # column 찾지 못한 경우 Falsewith processing
                        prev_fails.append(False)
                
                # consecutive failure 체크: previous month들and current month 모두 failure 있 경우
                # 모든 previous monthto for data 있고, 모두 failure 있으며, current monthalso failure 있 경우
                if len(prev_fails) == len(self.config.previous_months) and all(prev_fails) and current_fail_count > 0:
                    continuous_fail = 'YES'
                    # 특별히 TRẦN VĂN HÀof 경우 debugging
                    if emp_id == '624040283':
                        print(f"    → TRẦN VĂN HÀ - 3-month consecutive failure checkingdone!")
                        print(f"      previous month failure: {prev_fails}")
                        print(f"      current month failure: {current_fail_count}")
            
            # consecutive incentive 수령 month 수 별alsowith calculation (필요 시)
            
            aql_results.append({
                'Employee No': emp_id,
                current_month_fail_col: current_fail_count,
                'Continuous_FAIL': continuous_fail
            })
        
        result_df = pd.DataFrame(aql_results)
        print(f"✅ AQL condition processing completed: {len(result_df)} employees")
        return result_df


class CompleteQIPCalculator:
    """완전한 QIP incentive calculation기 (improved 버전)"""

    def __init__(self, data: Dict[str, pd.DataFrame], config: MonthConfig):
        self.config = config
        self.month_data = None
        self.special_handler = SpecialCaseHandler(config)
        self.data_processor = DataProcessor(config)

        # Position matrix withload (하load코ing 제거 위해 필수)
        self.position_matrix = POSITION_CONDITION_MATRIX

        # base_path configuration (프with젝트 루트 directory)
        from pathlib import Path
        self.base_path = Path.cwd()

        # data saved
        self.raw_data = data

        # preparation 작업
        self.prepare_integrated_data()

    def load_july_incentive_data(self):
        """July incentive data withload (August calculation 시 특별 processing)"""
        # August calculation 시toonly 실행
        if self.config.month.number == 8 and self.config.year == 2025:
            print("\n📊 July incentive Loading data (Single Source of Truth)...")
            july_file_path = self.base_path / "input_files" / "2025 July Incentive_final_Sep_15.csv"

            if july_file_path.exists():
                try:
                    july_df = pd.read_csv(july_file_path, encoding='utf-8-sig')
                    print(f"  ✅ July incentive file loaded successfully: {len(july_df)} employees")

                    # Employee No 표준화
                    july_df['Employee No'] = july_df['Employee No'].apply(
                        lambda x: str(int(x)).zfill(9) if pd.notna(x) else ''
                    )
                    self.month_data['Employee No'] = self.month_data['Employee No'].apply(
                        lambda x: str(int(x)).zfill(9) if pd.notna(x) else ''
                    )

                    # July_Incentive mapping
                    july_map = july_df.set_index('Employee No')['July_Incentive'].to_dict()
                    self.month_data['July_Incentive'] = self.month_data['Employee No'].map(july_map).fillna(0)

                    # 통계 출력
                    mapped_count = (self.month_data['July_Incentive'] > 0).sum()
                    zero_count = (self.month_data['July_Incentive'] == 0).sum()
                    print(f"  → July incentive mapping completed: {mapped_count}명 (>0), {zero_count}명 (=0)")

                    # DANH MINH HIẾU checking
                    hiếu_data = self.month_data[self.month_data['Employee No'] == '621030996']
                    if not hiếu_data.empty:
                        july_amt = hiếu_data.iloc[0]['July_Incentive']
                        print(f"  → DANH MINH HIẾU (621030996) July incentive: {july_amt:,.0f}VND")

                    return True

                except Exception as e:
                    print(f"  ❌ July incentive file load failed: {e}")
                    return False
            else:
                print(f"  ⚠️ July incentive file not found: {july_file_path}")
                return False

        # September 후 previous month Excelfrom 자동으로 읽음
        return True

    def prepare_integrated_data(self):
        """통합 data preparation"""
        print(f"\n📊 {self.config.get_month_str('korean')} 통합 data preparation in progress...")
        
        # default data configuration
        basic_key = f"{self.config.month.full_name}_basic"
        if basic_key in self.raw_data:
            # Employee No 있 유효한 dataonly 필터링
            raw_data = self.raw_data[basic_key]
            self.month_data = raw_data[raw_data['Employee No'].notna()].copy()
            print(f"  → 유효한 employee data: {len(self.month_data)}명 (전체 {len(raw_data)}행 in progress)")
        else:
            print(f"❌ {self.config.get_month_str('korean')} default data 찾 수 없습니다.")
            self.month_data = pd.DataFrame()
            return
        
        # employee ID 표준화
        emp_col = self.data_processor.detect_column_names(self.month_data, [
            'Employee No', 'EMPLOYEE NO', 'EMPLOYEE_NO', 'EMP_NO',
            'EMPLOYEE ID', 'EMPLOYEE_ID', 'ID',
            'Employee No', 'Personnel Number'
        ])
        
        if emp_col:
            # Employee No column 미 있으면 표준화, 없으면 created
            if emp_col != 'Employee No':
                self.month_data['Employee No'] = self.month_data[emp_col]
            
            # 타입 문자열with 변환하고 표준화
            self.month_data['Employee No'] = self.month_data['Employee No'].apply(
                lambda x: self.data_processor.standardize_employee_id(x) if pd.notna(x) else ''
            )
        
        # 소스 CSVof Final Incentive amount 백업하고 제거
        if 'Final Incentive amount' in self.month_data.columns:
            self.month_data['Source_Final_Incentive'] = self.month_data['Final Incentive amount']
            # 소스 value 제거 - 재calculation 후 새with configuration
            del self.month_data['Final Incentive amount']
            print(f"  → 소스 CSVof Final Incentive amount 백업 및 제거")

        # incentive column 초기화
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        self.month_data[incentive_col] = 0
        
        # 모든 condition data 병합
        self._merge_all_conditions()
        
        # defaultvalue configuration
        self._set_improved_default_values()
        
        # TYPE-1 STITCHING INSPECTOR TYPE-2with 수정하 전processing
        self._preprocess_position_type_corrections()
        
        print(f"✅ {self.config.get_month_str('korean')} data preparation completed: {len(self.month_data)} employees")
    
    def _merge_all_conditions(self):
        """모든 condition data 병합"""
        # attendance data 병합
        attendance_key = f"{self.config.month.full_name}_attendance"
        if attendance_key in self.raw_data:
            att_conditions = self.data_processor.process_attendance_conditions(
                self.raw_data[attendance_key]
            )
            if not att_conditions.empty:
                # Stop Working Date 있 employee checking
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
                
                # 병합 전to Stop Working employeeof attendance data 수정
                for emp_id in stop_working_emps:
                    if emp_id in att_conditions['Employee No'].values:
                        att_idx = att_conditions[att_conditions['Employee No'] == emp_id].index
                        if len(att_idx) > 0:
                            att_conditions.loc[att_idx[0], 'Actual Working Days'] = 0
                            att_conditions.loc[att_idx[0], 'Total Working Days'] = 0
                            # 레거시 컬럼 삭제: cond_3_actual_working_days로 통합
                            # att_conditions.loc[att_idx[0], 'attendancy condition 1 - acctual working days is zero'] = 'yes'
                            att_conditions.loc[att_idx[0], '결근율_Absence_Rate_Percent'] = 100.0
                
                self.month_data = pd.merge(
                    self.month_data,
                    att_conditions,
                    on='Employee No',
                    how='left'
                )
                
                # 병합 후 퇴사자 absence rate 재calculation
                self._recalculate_absence_rate_for_resigned()
        
        # 5PRS data 병합
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
        
        # AQL data 병합
        aql_key = f"{self.config.month.full_name}_aql"
        prev_incentive_key = f"{self.config.previous_months[-1].full_name}_incentive" if self.config.previous_months else None
        
        if aql_key in self.raw_data:
            historical_data = self.raw_data.get(prev_incentive_key) if prev_incentive_key else None
            
            # debugging: historical_data 제대with withload되었지 checking
            if historical_data is not None:
                print(f"  → previous incentive data loaded successfully: {len(historical_data)}cases")
                # failure related column checking
                failure_cols = [col for col in historical_data.columns if 'Failure' in col or 'FAIL' in col]
                if failure_cols:
                    print(f"    failure related column: {failure_cols[:5]}")  # 처음 5itemsonly 표시
            else:
                print(f"  ⚠️ previous incentive data not found (key: {prev_incentive_key})")
            # AQL history file 있지 checking
            import os
            aql_history_path = 'input_files/AQL history'

            # current monthand previous 2-monthof AQL history file checking
            current_month = self.config.month.full_name.upper()
            prev_months = [m.full_name.upper() for m in self.config.previous_months] if self.config.previous_months else []

            # 3-month file 모두 있지 checking (current month + previous 2-month)
            if len(prev_months) >= 2:
                month1 = prev_months[1]  # 2-month 전
                month2 = prev_months[0]  # 1-month 전
                month3 = current_month   # current month

                use_history = (
                    os.path.exists(f'{aql_history_path}/1.HSRG AQL REPORT-{month1}.{self.config.year}.csv') and
                    os.path.exists(f'{aql_history_path}/1.HSRG AQL REPORT-{month2}.{self.config.year}.csv') and
                    os.path.exists(f'{aql_history_path}/1.HSRG AQL REPORT-{month3}.{self.config.year}.csv')
                )
            else:
                use_history = False
            
            if use_history:
                print("  → Using AQL History files")
                # DataProcessorto month_data 전month하여 모든 employee 목록 제공
                self.data_processor.df = self.month_data
                aql_conditions = self.data_processor.process_aql_conditions_with_history()
            else:
                print("  → Using legacy method (based on previous incentive file)")
                aql_conditions = self.data_processor.process_aql_conditions(
                    self.raw_data[aql_key],
                    historical_data
                )
            if not aql_conditions.empty:
                # Employee No 표준화 (병합 전)
                aql_conditions['Employee No'] = aql_conditions['Employee No'].apply(
                    lambda x: self.data_processor.standardize_employee_id(x) if pd.notna(x) else ''
                )
                
                # 병합 전 AQL failure cases수 checking
                aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
                if aql_col in aql_conditions.columns:
                    aql_fail_count = (aql_conditions[aql_col] > 0).sum()
                    if aql_fail_count > 0:
                        print(f"  → AQL 병합 전: {aql_fail_count}명 AQL failure record 보유")
                
                # 3-month consecutive failures checking
                if 'Continuous_FAIL' in aql_conditions.columns:
                    continuous_fail_count = (aql_conditions['Continuous_FAIL'] == 'YES').sum()
                    if continuous_fail_count > 0:
                        print(f"  → AQL 병합 전: {continuous_fail_count}명 3-month consecutive failure")
                        # 624040283 checking
                        tran = aql_conditions[aql_conditions['Employee No'] == '624040283']
                        if not tran.empty:
                            print(f"    → 624040283 Continuous_FAIL: {tran.iloc[0]['Continuous_FAIL']}")
                
                # 병합 전 data 타입 checking
                print(f"  → 병합 전 month_data Employee No 타입: {self.month_data['Employee No'].dtype}")
                print(f"  → 병합 전 aql_conditions Employee No 타입: {aql_conditions['Employee No'].dtype}")

                # 샘플 ID 비교
                month_sample = self.month_data['Employee No'].iloc[:3].tolist()
                aql_sample = aql_conditions['Employee No'].iloc[:3].tolist()
                print(f"  → month_data 샘플: {month_sample}")
                print(f"  → aql_conditions 샘플: {aql_sample}")

                self.month_data = pd.merge(
                    self.month_data,
                    aql_conditions,
                    on='Employee No',
                    how='left'
                )

                # 병합 후 AQL failure cases수 checking
                if aql_col in self.month_data.columns:
                    aql_fail_count_after = (self.month_data[aql_col] > 0).sum()
                    print(f"  → AQL 병합 후: {aql_fail_count_after}명 AQL failure record 보유")

                    # 특정 employee checking
                    test_emp = '625060019'
                    test_row = self.month_data[self.month_data['Employee No'] == test_emp]
                    if not test_row.empty:
                        print(f"  → employee {test_emp} AQL failure: {test_row.iloc[0][aql_col]}")
                
                # 병합 후 3-month consecutive failures checking
                if 'Continuous_FAIL' in self.month_data.columns:
                    continuous_fail_count_after = (self.month_data['Continuous_FAIL'] == 'YES').sum()
                    print(f"  → AQL 병합 후: {continuous_fail_count_after}명 3-month consecutive failure")
                    # 624040283 checking
                    tran_after = self.month_data[self.month_data['Employee No'] == '624040283']
                    if not tran_after.empty:
                        print(f"    → 624040283 Continuous_FAIL 병합 후: {tran_after.iloc[0]['Continuous_FAIL']}")

        # AQL Area Reject Rate calculation 및 추
        self._add_area_reject_rates()

    def _add_area_reject_rates(self):
        """각 employeeof in charge area reject rate calculation 및 추"""
        print("\n📊 Area Reject Rate Calculating...")

        # AQL data withload
        aql_data = self.load_aql_data_for_area_calculation()
        if aql_data is None or aql_data.empty:
            print("  ⚠️ Cannot calculate Area Reject Rate due to missing AQL data.")
            self.month_data['Area_Reject_Rate'] = 0
            return

        # REPACKING PO 컬럼 생성/확인 (load_aql_data_for_area_calculation에서 생성되지만 이중 체크)
        if 'REPACKING PO' not in aql_data.columns:
            if 'REPACKING ' in aql_data.columns or 'REPACKING' in aql_data.columns:
                repacking_col = 'REPACKING ' if 'REPACKING ' in aql_data.columns else 'REPACKING'
                aql_data['REPACKING PO'] = aql_data[repacking_col].apply(
                    lambda x: 'NORMAL PO' if pd.isna(x) else 'REPACKING PO'
                )
                normal_count = (aql_data['REPACKING PO'] == 'NORMAL PO').sum()
                repack_count = (aql_data['REPACKING PO'] == 'REPACKING PO').sum()
                print(f"  ℹ️ REPACKING PO auto-generated: NORMAL PO={normal_count}, REPACKING PO={repack_count}")
            else:
                aql_data['REPACKING PO'] = 'NORMAL PO'
                print(f"  ℹ️ No REPACKING column found - treating all {len(aql_data)} records as NORMAL PO")

        # Building별 reject rate calculation
        building_reject_rates = {}
        for building in ['A', 'B', 'C', 'D']:
            building_data = aql_data[
                (aql_data['BUILDING'] == building) &
                (aql_data['REPACKING PO'] == 'NORMAL PO')
            ]

            if not building_data.empty:
                total = len(building_data)
                fails = len(building_data[building_data['RESULT'].str.upper() == 'FAIL'])
                rate = (fails / total * 100) if total > 0 else 0
                building_reject_rates[building] = rate
                if rate >= 3:
                    print(f"  ⚠️ Building {building}: {rate:.2f}% (≥3%)")

        # 각 employeeto게 해당 buildingof reject rate 할당
        self.month_data['Area_Reject_Rate'] = 0

        # Auditor/Trainerof in charge area mapping withload
        area_mapping = self.load_auditor_trainer_area_mapping()

        for idx, row in self.month_data.iterrows():
            emp_id = row.get('Employee No', '')
            position = str(row.get('QIP POSITION 1ST  NAME', '')).upper()

            # MODEL MASTER인 경우 - 전체 area in charge
            if 'MODEL' in position and 'MASTER' in position:
                # 전체 areaof reject rate calculation
                total_all = len(aql_data[aql_data['REPACKING PO'] == 'NORMAL PO'])
                fails_all = len(aql_data[
                    (aql_data['REPACKING PO'] == 'NORMAL PO') &
                    (aql_data['RESULT'].str.upper() == 'FAIL')
                ])
                rate = (fails_all / total_all * 100) if total_all > 0 else 0
                self.month_data.loc[idx, 'Area_Reject_Rate'] = rate
                print(f"  → MODEL MASTER {emp_id}: 전체 area reject율 = {rate:.2f}%")

            # Auditor & Training Team인 경우
            elif 'AUDIT' in position or 'TRAINING' in position:
                # in charge area 찾기
                if area_mapping and str(emp_id) in area_mapping.get('auditor_trainer_areas', {}):
                    config = area_mapping['auditor_trainer_areas'][str(emp_id)]
                    for condition in config.get('conditions', []):
                        if condition.get('type') == 'ALL':
                            # 전체 area in charge - 전체 reject rate
                            total_all = len(aql_data[aql_data['REPACKING PO'] == 'NORMAL PO'])
                            fails_all = len(aql_data[(aql_data['REPACKING PO'] == 'NORMAL PO') &
                                                    (aql_data['RESULT'].str.upper() == 'FAIL')])
                            rate = (fails_all / total_all * 100) if total_all > 0 else 0
                            self.month_data.loc[idx, 'Area_Reject_Rate'] = rate
                            break
                        elif condition.get('type') == 'AND':
                            # 특정 Building in charge
                            for filter_item in condition.get('filters', []):
                                if filter_item.get('column') == 'BUILDING':
                                    building = filter_item.get('value')
                                    self.month_data.loc[idx, 'Area_Reject_Rate'] = building_reject_rates.get(building, 0)
                                    break

            #  day-shift employees은 자신 속한 Buildingof reject rate (필요시)
            # current Auditor/Traineronly apply

        area_reject_count = (self.month_data['Area_Reject_Rate'] >= 3).sum()
        print(f"✅ Area Reject Rate calculation completed: {area_reject_count}명 3% 상")

    def _recalculate_absence_rate_for_resigned(self):
        """퇴사자 위한 absence rate 재calculation"""
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
                    # date 파싱
                    if '.' in str(stop_date_str):
                        stop_date = pd.to_datetime(stop_date_str, format='%Y.%m.%d', errors='coerce')
                    else:
                        stop_date = pd.to_datetime(stop_date_str, errors='coerce')
                    
                    if pd.notna(stop_date):
                        # 해당 month in progress 퇴사자인 경우
                        if calc_month_start <= stop_date <= calc_month_end:
                            # 근무 능 days calculation (주말 exclude)
                            working_days_possible = 0
                            current_date = calc_month_start
                            while current_date <= stop_date:
                                if current_date.weekday() < 5:  # month-금 (0-4)
                                    working_days_possible += 1
                                current_date += pd.Timedelta(days=1)
                            
                            actual_days = row.get('Actual Working Days', 0)

                            # Total Working Daysonly updated
                            # Absence Rate (raw)and conditionare add_condition_evaluation_to_excelfrom
                            # 승인휴 반영하여 통 days되게 calculationdone
                            self.month_data.loc[idx, 'Total Working Days'] = working_days_possible

                            # 레거시 컬럼 삭제:                             # minimum 근무 days conditiononly 체크 (Absence Rate 나in progressto calculation)
                            # 레거시 컬럼 삭제: self.month_data.loc[idx, 'attendancy condition 4 - minimum working days'] = 'yes' if actual_days < 12 else 'no'

                            print(f"  → 퇴사자 {row.get('Employee No', '')}: {stop_date.strftime('%Y-%m-%d')} 퇴사, 근무능 days {working_days_possible} days (Absence Rate 승인휴 반영하여 나in progressto calculation)")
                        
                        # calculation month previous 퇴사자
                        elif stop_date < calc_month_start:
                            self.month_data.loc[idx, 'Actual Working Days'] = 0
                            # 레거시 컬럼 삭제:                             self.month_data.loc[idx, 'Total Working Days'] = 0
                            # 레거시 컬럼 삭제:                             self.month_data.loc[idx, 'attendancy condition 1 - acctual working days is zero'] = 'yes'
                            # 레거시 컬럼 삭제: self.month_data.loc[idx, 'attendancy condition 4 - minimum working days'] = 'yes'
                            
                except Exception as e:
                    print(f"  ⚠️ 퇴사자 absence rate 재calculation 오류 (employee {row.get('Employee No', '')}): {e}")
    
    def _set_improved_default_values(self):
        """improved defaultvalue configuration"""
        # AQL failure defaultvalue - 미 병합done data casesload리지 않음
        aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
        if aql_col not in self.month_data.columns:
            self.month_data[aql_col] = 0
        else:
            # NaN valueonly 0with 채우고, existing value은 유지
            self.month_data[aql_col] = self.month_data[aql_col].fillna(0)
        
        # attendance related defaultvalue - attendance data 없으면 0with configuration
        if 'Total Working Days' not in self.month_data.columns:
            self.month_data['Total Working Days'] = self.config.working_days
            self.month_data['Actual Working Days'] = 0  # defaultvalue 0with 변경 (existing 23)
            # Unapproved Absence Days column 제거 - Unapproved Absences columnonly 사용
            self.month_data['결근율_Absence_Rate_Percent'] = 0.0
            print("  → Applying default value 0 to employees without attendance data")
        
        # Stop Working Date processing - calculation month previous 퇴사자 Actual Working Days = 0
        if 'Stop working Date' in self.month_data.columns:
            calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
            
            for idx, row in self.month_data.iterrows():
                stop_date_str = row.get('Stop working Date')
                if pd.notna(stop_date_str) and stop_date_str != '':
                    try:
                        # 다양한 date 형식 processing
                        if '.' in str(stop_date_str):
                            stop_date = pd.to_datetime(stop_date_str, format='%Y.%m.%d', errors='coerce')
                        else:
                            stop_date = pd.to_datetime(stop_date_str, errors='coerce')
                        
                        if pd.notna(stop_date) and stop_date < calc_month_start:
                            # calculation month previousto 퇴사한 경우
                            self.month_data.loc[idx, 'Actual Working Days'] = 0
                            # 레거시 컬럼 삭제:                             self.month_data.loc[idx, 'Total Working Days'] = 0
                            # 레거시 컬럼 삭제: self.month_data.loc[idx, 'attendancy condition 1 - acctual working days is zero'] = 'yes'
                            self.month_data.loc[idx, '결근율_Absence_Rate_Percent'] = 100.0
                            print(f"  → Stop Working employee {row.get('Employee No', '')}: {stop_date.strftime('%Y-%m-%d')} 퇴사 → Actual Working Days = 0")
                    except Exception as e:
                        print(f"  ⚠️ Stop Working Date processing 오류 (employee {row.get('Employee No', '')}): {e}")
        
        # condition column defaultvalue
        # 레거시 컬럼 삭제: cond_1~10 표준 컬럼으로 통합
        default_conditions = {
            # 'attendancy condition 1-4': 삭제됨 (cond_1~4로 통합)
            # '5prs condition 1-2': 삭제됨 (cond_9~10으로 통합)
            'Total Working Days': self.config.working_days,
            'Actual Working Days': 0,  # defaultvalue 0with 변경
            '결근율_Absence_Rate_Percent': 0.0,
            'Continuous_FAIL': 'NO'
        }
        
        for col, default_val in default_conditions.items():
            if col not in self.month_data.columns:
                self.month_data[col] = default_val
            else:
                self.month_data[col] = self.month_data[col].fillna(default_val)
    
    def _preprocess_position_type_corrections(self):
        """positionand 타입 불 days치 수정하 전processing 함수
        
        주요 수정사항:
        - TYPE-1 STITCHING INSPECTOR → TYPE-2with 변경
        """
        print("\n🔧 Position-TYPE data Pre-processing data...")
        correction_count = 0
        
        # TYPE-1면서 STITCHING INSPECTOR인 경우 TYPE-2with 수정
        if 'ROLE TYPE STD' in self.month_data.columns and 'QIP POSITION 1ST  NAME' in self.month_data.columns:
            # 수정 필요한 employee 찾기
            stitching_mask = (
                (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('STITCHING', na=False)) &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
            )
            
            # 수정 대상 checking 및 with깅
            if stitching_mask.any():
                affected_employees = self.month_data[stitching_mask]
                for idx, row in affected_employees.iterrows():
                    emp_no = row.get('Employee No', 'Unknown')
                    emp_name = row.get('Full Name', 'Unknown')
                    position = row.get('QIP POSITION 1ST  NAME', 'Unknown')
                    print(f"  → TYPE-1 → TYPE-2 수정: {emp_no} ({emp_name}) - {position}")
                    correction_count += 1
                
                # TYPE TYPE-2with 수정
                self.month_data.loc[stitching_mask, 'ROLE TYPE STD'] = 'TYPE-2'
        
        if correction_count > 0:
            print(f"  ✅ 총 {correction_count}명of position-타입 불 days치 수정 completed")
        else:
            print(f"  ✅ 수정 필요한 position-타입 불 days치 없음")
    
    def check_required_files_for_month(self, month_obj, year):
        """특정 month calculationto 필요한 file들 존재하지 checking"""
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
            print(f"\n⚠️ {month_obj.number}month calculationto 필요한 file not found:")
            print(f"   current 작업 directory: {self.base_path}")
            print(f"\n   찾 수 없 file:")
            for missing in missing_files:
                print(f"   - {missing['type']}: {missing['name']}")
                print(f"     전체 경with: {missing['path']}")
            return False
        
        return True
    
    def ensure_previous_month_exists(self):
        """previous month incentive file checking 및 자same created"""
        if self.config.month.number == 1:
            prev_month = 12
            prev_year = self.config.year - 1
        else:
            prev_month = self.config.month.number - 1
            prev_year = self.config.year
        
        prev_month_obj = Month.from_number(prev_month)

        # Fallback pattern: V9.0 먼저 확인, 없으면 V8.02, V8.01로 폴백
        prev_file_patterns = [
            self.base_path / 'output_files' / f'output_QIP_incentive_{prev_month_obj.full_name}_{prev_year}_Complete_V9.0_Complete.csv',
            self.base_path / 'output_files' / f'output_QIP_incentive_{prev_month_obj.full_name}_{prev_year}_Complete_V8.02_Complete.csv',
            self.base_path / 'output_files' / f'output_QIP_incentive_{prev_month_obj.full_name}_{prev_year}_Complete_V8.01_Complete.csv'
        ]

        prev_file_path = None
        for pattern in prev_file_patterns:
            if pattern.exists():
                prev_file_path = pattern
                break

        if prev_file_path is None:
            print(f"\n📊 {prev_month}month incentive file not found.")
            print(f"   {prev_month}month 자동으로 calculation합니다...")
            
            # previous month calculationto 필요한 file들 체크
            if not self.check_required_files_for_month(prev_month_obj, prev_year):
                print(f"\n❌ {prev_month}month calculation in progressproceed.")
                print(f"   필요한 file들 first preparation해주세요.")
                print(f"\n❌ {self.config.month.number}month calculationalso in progressproceed.")
                print(f"   previous month data 필요하므with {prev_month}month first preparation해주세요.")
                raise Exception(f"{prev_month}month data 없어 {self.config.month.number}month calculation in progressproceed.")
            
            print(f"\n✅ {prev_month}month calculationto 필요한 file 모두 있습니다.")
            print(f"   {prev_month}month calculation started...")
            
            # previous month calculation기 created 및 실행
            # previous month config file withload
            prev_config_file = self.base_path / 'config_files' / f'config_{prev_month_obj.full_name}_{prev_year}.json'
            if not prev_config_file.exists():
                print(f"❌ {prev_month}month config file not found: {prev_config_file}")
                raise Exception(f"{prev_month}month config file 없어 {self.config.month.number}month calculation in progressproceed.")
            
            # JSON file withload
            import json
            with open(prev_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # previous_months Month 객체with 변환
            prev_months_str = config_data.get('previous_months', [])
            prev_months_obj = []
            for month_str in prev_months_str:
                # Month enum 찾기
                for m in Month:
                    if m.full_name == month_str:
                        prev_months_obj.append(m)
                        break
            
            # MonthConfig created
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
                print(f"❌ {prev_month}month data load failed")
                raise Exception(f"{prev_month}month data load failedwith {self.config.month.number}month calculation in progressproceed.")
            
            # previous month calculation기 created
            prev_processor = CompleteQIPCalculator(prev_data, prev_config)
            
            # 재귀 방지 위해 previous monthof previous month은 체크하지 않음
            prev_processor.calculate_all_incentives_without_check()

            # 결and saved
            output_path = self.base_path / 'output_files' / f'output_QIP_incentive_{prev_month_obj.full_name}_{prev_year}_Complete_V9.0_Complete.csv'
            prev_processor.month_data.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"✅ {prev_month}month calculation completed\n")
    
    def calculate_all_incentives_without_check(self):
        """previous month 체크 없 incentive calculation (재귀 방지용)"""
        print(f"📊 TYPE별 incentive calculation started...")
        
        # manager-부하 mapping created
        subordinate_mapping = self.create_manager_subordinate_mapping()
        
        # same days한 with직 실행
        self.calculate_auditor_trainer_incentive(subordinate_mapping)
        self.calculate_assembly_inspector_incentive_type1_only()
        self.calculate_line_leader_incentive_type1_only(subordinate_mapping)
        self.calculate_head_incentive(subordinate_mapping)
        self.calculate_type2_incentive()
        
        print(f"✅ incentive calculation completed")
    
    def calculate_all_incentives(self):
        """모든 incentive calculation 실행"""
        print(f"\n🚀 {self.config.get_month_str('korean')} QIP incentive calculation started...")

        # 0. data validation
        self.validate_and_report_issues()

        # 0.5. previous month data checking
        self.ensure_previous_month_exists()

        # 0.6. July incentive data withload (August calculation 시)
        self.load_july_incentive_data()

        # 1. 특별 케스 processing
        self.handle_special_cases()

        # 1.5. 승인휴 반영 및 attendance condition 재calculation (incentive calculation 전 필수!)
        # ⚠️ CRITICAL: approved leave를 포함한 정확한 absence rate로 condition 재평가
        print(f"\n🔄 Updating attendance conditions with approved leave...")
        self.add_condition_evaluation_to_excel()

        # 2. Type-1 Assembly Inspector calculation
        self.calculate_assembly_inspector_incentive_type1_only()
        
        # 3. manager-부하 mapping created
        subordinate_mapping = self.create_manager_subordinate_mapping()
        
        # 4. Type-1 Auditor/Trainer calculation
        self.calculate_auditor_trainer_incentive(subordinate_mapping)
        
        # 5. Type-1 Line Leader calculation
        self.calculate_line_leader_incentive_type1_only(subordinate_mapping)
        
        # 5. Head(Group Leader) calculation
        self.calculate_head_incentive(subordinate_mapping)
        
        # 6. manager calculation
        self.calculate_managers_by_manual_logic_fixed(subordinate_mapping)
        
        # 6. Type-2 calculation
        self.calculate_type2_incentive()
        
        # 7. Type-3 calculation
        self.calculate_type3_incentive()
        
        # 8. QIP Talent Pool 보너스 apply
        self.apply_talent_pool_bonus()
        
        print(f"\n✅ {self.config.get_month_str('korean')} incentive calculation completed!")
    
    def handle_special_cases(self):
        """특별 케스 processing - 자same calculation"""
        # 특별 케스 제 calculate_assembly_inspector_incentive_type1_onlyand
        # calculate_auditor_trainer_incentivefrom 자동으로 processingdone
        pass
    
    def identify_special_cases(self) -> Dict[str, List]:
        """특별 케스 식별 (Audit/Training exclude)"""
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
            # Audit/Training은 제 별alsowith processing
        
        return special_cases
    
    def check_subordinates_continuous_fail(self, manager_id: str, subordinate_mapping: Dict[str, List[str]]) -> bool:
        """
        부하employee in progress 3-month consecutive AQL failures 있지 checking
        Returns: True if consecutive failures 있음, False if 없음
        """
        if manager_id not in subordinate_mapping:
            return False

        for sub_id in subordinate_mapping[manager_id]:
            # FIX: Type-safe comparison - Employee No might be int64 after save_results() conversion
            sub_data = self.month_data[self.month_data['Employee No'].astype(str) == str(sub_id)]
            if not sub_data.empty:
                # FIX: Check if starts with 'YES' to match 'YES', 'YES_3MONTHS', 'YES_2MONTHS_AUG_SEP'
                continuous_fail_value = str(sub_data.iloc[0].get('Continuous_FAIL', 'NO'))
                if continuous_fail_value.startswith('YES'):
                    return True
        return False

    def get_auditor_area_employees(self, auditor_id: str, area_mapping: dict) -> List[str]:
        """
        AUDIT & TRAINING TEAM의 담당 구역 직원 목록 반환

        Args:
            auditor_id: Auditor Employee No
            area_mapping: auditor_trainer_area_mapping.json 내용

        Returns:
            담당 구역의 Employee No 리스트
        """
        if str(auditor_id) not in area_mapping.get('auditor_trainer_areas', {}):
            return []

        config = area_mapping['auditor_trainer_areas'][str(auditor_id)]
        area_employees = []

        for condition in config.get('conditions', []):
            condition_type = condition.get('type')
            filters = condition.get('filters', [])

            # AND 조건: 모든 필터를 만족하는 직원
            if condition_type == 'AND':
                mask = pd.Series([True] * len(self.month_data))
                for filter_item in filters:
                    column = filter_item.get('column')
                    value = filter_item.get('value')
                    if column in self.month_data.columns:
                        mask &= (self.month_data[column] == value)

                matched_employees = self.month_data[mask]['Employee No'].astype(str).tolist()
                area_employees.extend(matched_employees)

            # OR 조건: 어느 하나라도 만족하는 직원
            elif condition_type == 'OR':
                for filter_item in filters:
                    column = filter_item.get('column')
                    value = filter_item.get('value')
                    if column in self.month_data.columns:
                        matched = self.month_data[self.month_data[column] == value]['Employee No'].astype(str).tolist()
                        area_employees.extend(matched)

        return list(set(area_employees))  # 중복 제거

    def get_continuous_fail_by_factory(self) -> Dict[str, int]:
        """
        3-month consecutive failuresof factory별 분포 반환
        Returns: {factoryemployees: consecutivefailures수}
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
        employeeof 소속 factory(Building) 반환
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
        """data 문제 validation 및 보고"""
        print("\n🔍 data Validating data...")
        
        # AQL reject rate validation
        aql_data = self.load_aql_data_for_area_calculation()
        if aql_data is not None and not aql_data.empty:
            buildings = ['A', 'B', 'C', 'D']
            problems_found = False
            
            for building in buildings:
                # REPACKING PO NORMAL PO인 dataonly 필터
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
                        
                        # 해당 Building in charge자 찾기
                        area_mapping = self.load_auditor_trainer_area_mapping()
                        for emp_id, config in area_mapping.get('auditor_trainer_areas', {}).items():
                            for cond in config.get('conditions', []):
                                for filter_item in cond.get('filters', []):
                                    if filter_item.get('column') == 'BUILDING' and filter_item.get('value') == building:
                                        emp_name = config.get('name', 'Unknown')
                                        print(f"      → 영향받은 직원: {emp_name} ({emp_id})")
                                        break
            
            if problems_found:
                print("\n   Found conditions that may result in 0 incentive.")
        else:
            print("   ⚠️ AQL data not found.")
    
    def is_all_buildings_team_leader(self, auditor_id: str) -> bool:
        """
        Auditor/Trainer 전체 area in charge Team Leader인지 checking
        """
        area_mapping = self.load_auditor_trainer_area_mapping()

        if not area_mapping:
            return False

        auditor_id_str = str(auditor_id)
        if auditor_id_str in area_mapping.get('auditor_trainer_areas', {}):
            config = area_mapping['auditor_trainer_areas'][auditor_id_str]

            # conditions ALL type면 전체 area in charge
            for condition in config.get('conditions', []):
                if condition.get('type') == 'ALL':
                    return True

        return False

    def get_auditor_assigned_factory(self, auditor_id: str) -> str:
        """
        Auditor/Trainer in charge하 factory(Building) 반환
        mapping 파일에서 in charge area checking
        """
        # auditor_trainer_area_mapping.json withload
        area_mapping = self.load_auditor_trainer_area_mapping()
        
        if not area_mapping:
            return ''
        
        # 해당 auditorof in charge area 찾기
        auditor_id_str = str(auditor_id)
        if auditor_id_str in area_mapping.get('auditor_trainer_areas', {}):
            config = area_mapping['auditor_trainer_areas'][auditor_id_str]
            
            # conditionsfrom BUILDING 찾기
            for condition in config.get('conditions', []):
                if condition['type'] == 'AND':
                    for filter_item in condition['filters']:
                        if filter_item['column'] == 'BUILDING':
                            return filter_item['value']
        
        return ''
    
    def calculate_total_factory_reject_rate(self) -> float:
        """
        전체 factoryof AQL reject율 calculation (Model Master용)
        """
        # AQL data withload
        aql_data = self.load_aql_data_for_area_calculation()
        if aql_data is None or aql_data.empty:
            return 0.0
        
        # 전체 inspection 수
        total_inspections = len(aql_data)
        
        # Result column 찾기
        result_col = None
        for col in aql_data.columns:
            if col.upper() == 'RESULT':
                result_col = col
                break
        
        if result_col:
            # FAIL 수 calculation
            total_failures = len(aql_data[aql_data[result_col].str.upper() == 'FAIL'])
        else:
            total_failures = 0
        
        if total_inspections > 0:
            reject_rate = (total_failures / total_inspections) * 100
            print(f"    → 전체 factory: inspection {total_inspections}cases, failure {total_failures}cases, reject율 {reject_rate:.2f}%")
            return reject_rate
        
        return 0.0
    
    def calculate_auditor_trainer_incentive(self, subordinate_mapping: Dict[str, List[str]]):
        """Auditor/Trainer 및 Model Master incentive calculation (자same화)"""
        print("\n👥 TYPE-1 AUDITOR/TRAINER & MODEL MASTER incentive calculation...")

        # in charge area reject율 saved할 딕셔너리
        if not hasattr(self, 'auditor_area_reject_rates'):
            self.auditor_area_reject_rates = {}
        
        # Auditor/Trainer 필터링
        # NOTE: H (A.MANAGER), F (GROUP LEADER), G ((V) SUPERVISOR), E+LINE LEADER (LINE LEADER) exclude - 별also 함수from processingdone
        auditor_trainer_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                ((self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('AUDIT', na=False)) |
                 (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('TRAINER', na=False)) |
                 (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('TRAINING', na=False))) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^(QA[1-2][AB]?)$', na=False))  # AUDITOR/TRAINER codes only (QA1A/QA1B/QA2A/QA2B=AUDIT TEAM, E excludedone - LINE LEADER 사용)
            )
        )
        
        # Model Master 필터링 - QIP POSITION NAME 'MODEL MASTER'인 employeeonly
        # QA2A AUDIT & TRAINING TEAM LEADERso exclude
        model_master_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('MODEL MASTER', na=False)) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper() == 'D')  # CODE 'D'also MODEL MASTERwith 인식
            )
        )
        
        # 3-month consecutive failuresof factory별 분포 찾기
        continuous_fail_by_factory = self.get_continuous_fail_by_factory()
        
        # Model Master 위한 전체 factory reject율 calculation
        total_factory_reject_rate = self.calculate_total_factory_reject_rate()
        
        # Model Masterof area_reject_rate saved 위한 전역 변수
        self.model_master_reject_rate = total_factory_reject_rate
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # Model Master processing (별alsowith first processing)
        for idx, row in self.month_data[model_master_mask].iterrows():
            # 미 calculationdone 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            emp_id = row.get('Employee No', '')
            
            # Single Source of Truth: 새 표준 컬럼(cond_1~10) 사용
            # 출근 조건 체크 (C1: 출근율, C2: 무단결근, C3: 실근무일, C4: 최소근무일)
            attendance_fail = (
                row.get('cond_1_attendance_rate') == 'FAIL' or
                row.get('cond_2_unapproved_absence') == 'FAIL' or
                row.get('cond_3_actual_working_days') == 'FAIL' or
                row.get('cond_4_minimum_days') == 'FAIL'
            )

            aql_fail = row.get(aql_col, 0) > 0
            continuous_fail = row.get('Continuous_FAIL', 'NO') == 'YES'

            # 100% 충족 validation - MODEL MASTER condition 1,2,3,4,8 모두 충족해야 함
            # MODEL MASTER condition 체크 (1,2,3,4,8)
            # position_condition_matrix.jsonof CODE 'D' configurationto 따라 condition checking
            # FIX: NOT_APPLICABLE should be treated as PASS for interim reports
            condition_1_pass = row.get('cond_1_attendance_rate') in ['PASS', 'NOT_APPLICABLE']
            condition_2_pass = row.get('cond_2_unapproved_absence') == 'PASS'
            condition_3_pass = row.get('cond_3_actual_working_days') == 'PASS'
            # FIX: NOT_APPLICABLE should be treated as PASS (e.g., interim reports with < 12 working days)
            condition_4_pass = row.get('cond_4_minimum_days') in ['PASS', 'NOT_APPLICABLE']

            # Condition 8: in charge area reject율 < 3%
            area_reject_rate = total_factory_reject_rate  # MODEL MASTER 전체 factory reject율 사용
            condition_8_pass = area_reject_rate < 3.0

            # MODEL MASTER 모든 condition(1,2,3,4,8) 충족해야 함
            all_conditions_pass = (condition_1_pass and condition_2_pass and
                                  condition_3_pass and condition_4_pass and
                                  condition_8_pass)

            # pass_rate calculation (100% or 0%)
            if all_conditions_pass:
                pass_rate = 100
            else:
                failed_conditions = []
                if not condition_1_pass: failed_conditions.append('1')
                if not condition_2_pass: failed_conditions.append('2')
                if not condition_3_pass: failed_conditions.append('3')
                if not condition_4_pass: failed_conditions.append('4')
                if not condition_8_pass: failed_conditions.append('8')
                pass_rate = 0
                print(f"    → {row.get('Full Name', 'Unknown')} failed conditions: {', '.join(failed_conditions)}")


            # Model Master 전체 factory reject율 apply
            # 100% condition 충족 필수 (No Fake Data Policy)
            if not all_conditions_pass:
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                failed_conditions = []
                if not condition_1_pass: failed_conditions.append('1')
                if not condition_2_pass: failed_conditions.append('2')
                if not condition_3_pass: failed_conditions.append('3')
                if not condition_4_pass: failed_conditions.append('4')
                if not condition_8_pass: failed_conditions.append('8(reject율)')
                print(f"    → {row.get('Full Name', 'Unknown')} (Model Master): condition 미충족 [{', '.join(failed_conditions)}] → 0 VND")
            elif total_factory_reject_rate >= 3.0:  # 전체 factory reject율 3% 상
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                print(f"    → {row.get('Full Name', 'Unknown')} (Model Master): 전체 factory AQL reject율 {total_factory_reject_rate:.1f}% → 0 VND")
            else:
                # MODEL MASTER ASSEMBLY INSPECTORand 같은 Progressive Table 사용
                # position_condition_matrix.jsonof incentive_progression.TYPE_1_PROGRESSIVE apply
                continuous_months = self.data_processor.calculate_continuous_months_from_history(emp_id, self.month_data)
                incentive = self.get_assembly_inspector_amount(continuous_months)
                self.month_data.loc[idx, 'Continuous_Months'] = continuous_months
                print(f"    → {row.get('Full Name', 'Unknown')} (Model Master): {continuous_months}month consecutive → {incentive:,} VND")

            self.month_data.loc[idx, incentive_col] = incentive
        
        #  days반 Auditor/Trainer processing (Model Master exclude)
        auditor_only_mask = auditor_trainer_mask & ~model_master_mask
        
        for idx, row in self.month_data[auditor_only_mask].iterrows():
            # 미 calculationdone 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            emp_id = row.get('Employee No', '')
            
            # 1. in charge area AQL reject율 calculation
            area_reject_rate = self.calculate_area_aql_reject_rate(emp_id, subordinate_mapping)
            
            # reject율 saved (메타data용)
            self.auditor_area_reject_rates[str(emp_id)] = area_reject_rate
            
            # 2. in charge factoryto 3-month consecutive failures 있지 checking
            # Auditor/Trainerof in charge factory mappingfrom 찾기
            auditor_factory = self.get_auditor_assigned_factory(emp_id)

            # Team Leader (전체 area in charge) consecutive failures 체크from exclude
            is_team_leader = self.is_all_buildings_team_leader(emp_id)
            if is_team_leader:
                has_continuous_fail_in_factory = False  # Team Leader consecutive failures 영향 받지 않음
            else:
                has_continuous_fail_in_factory = auditor_factory in continuous_fail_by_factory and continuous_fail_by_factory[auditor_factory] > 0
            
            # 3. Single Source of Truth: 새 표준 컬럼(cond_1~10) 사용
            # 출근 조건 체크 (C1: 출근율, C2: 무단결근, C3: 실근무일, C4: 최소근무일)
            attendance_fail = (
                row.get('cond_1_attendance_rate') == 'FAIL' or
                row.get('cond_2_unapproved_absence') == 'FAIL' or
                row.get('cond_3_actual_working_days') == 'FAIL' or
                row.get('cond_4_minimum_days') == 'FAIL'
            )

            aql_fail = row.get(aql_col, 0) > 0
            continuous_fail = row.get('Continuous_FAIL', 'NO') == 'YES'

            # incentive 결정
            # Direct condition evaluation for Auditor/Trainer positions
            position_code = row.get('FINAL QIP POSITION NAME CODE', '')
            position_name = row.get('QIP POSITION 1ST  NAME', '')

            # Get applicable conditions from position matrix
            if position_code in self.position_matrix.get('positions', {}):
                applicable_conditions = self.position_matrix['positions'][position_code].get('applicable_conditions', [1,2,3,4])
            else:
                # Default conditions based on position name
                if 'AUDIT' in position_name.upper():
                    applicable_conditions = [1,2,3,4,7,8]
                else:
                    applicable_conditions = [1,2,3,4]

            # Evaluate each condition
            conditions_met = {}

            # Attendance conditions (1-4) - 새 표준 컬럼 사용
            if 1 in applicable_conditions:
                # FIX: NOT_APPLICABLE should be treated as PASS for interim reports
                conditions_met[1] = row.get('cond_1_attendance_rate') in ['PASS', 'NOT_APPLICABLE']
            if 2 in applicable_conditions:
                conditions_met[2] = row.get('cond_2_unapproved_absence') == 'PASS'
            if 3 in applicable_conditions:
                conditions_met[3] = row.get('cond_3_actual_working_days') == 'PASS'
            if 4 in applicable_conditions:
                # FIX: NOT_APPLICABLE should be treated as PASS (e.g., interim reports with < 12 working days)
                conditions_met[4] = row.get('cond_4_minimum_days') in ['PASS', 'NOT_APPLICABLE']

            # Condition 7: in charge area reject율 < 3%
            if 7 in applicable_conditions:
                conditions_met[7] = area_reject_rate < 3.0

            # Condition 8: in charge factoryto 3-month consecutive failures 없음
            if 8 in applicable_conditions:
                conditions_met[8] = not has_continuous_fail_in_factory

            # Check if all applicable conditions are met
            all_conditions_pass = all(conditions_met.values())

            # incentive 결정
            if not all_conditions_pass:
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                failed = [k for k,v in conditions_met.items() if not v]
                print(f"    → {row.get('Full Name', 'Unknown')} failed conditions: {failed} → 0 VND")
            elif area_reject_rate >= 3.0:  # in charge area reject율 3% 상with 변경
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                print(f"    → {row.get('Full Name', 'Unknown')}: in charge area AQL reject율 {area_reject_rate:.1f}% → 0 VND")
            elif has_continuous_fail_in_factory:  # in charge factoryto 3-month consecutive failures 있음
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                fail_count = continuous_fail_by_factory.get(auditor_factory, 0)
                print(f"    → {row.get('Full Name', 'Unknown')}: in charge factory({auditor_factory})to 3-month consecutive AQL failures {fail_count}명 → 0 VND")
            else:
                # Assembly Inspectorand same days한 consecutive 충족 month basis apply
                continuous_months = self.data_processor.calculate_continuous_months_from_history(emp_id, self.month_data)
                incentive = self.get_assembly_inspector_amount(continuous_months)

                # Continuous_Months column updated
                self.month_data.loc[idx, 'Continuous_Months'] = continuous_months

                if continuous_months > 0:
                    print(f"    → {row.get('Full Name', 'Unknown')}: {continuous_months}month consecutive → {incentive:,} VND")

            self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력 (전체)
        all_mask = auditor_trainer_mask | model_master_mask
        receiving_count = (self.month_data[all_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[all_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def calculate_area_aql_reject_rate(self, auditor_id: str, subordinate_mapping: Dict[str, List[str]]) -> float:
        """
        in charge areaof AQL reject율 calculation
        JSON 파일에서 in charge area condition 읽어 해당 areaof AQL reject율 calculation
        """
        # JSON 파일에서 in charge area 정보 withload
        area_mapping = self.load_auditor_trainer_area_mapping()
        
        # Model Master 체크
        if area_mapping and auditor_id in area_mapping.get('model_master', {}).get('employees', {}):
            # Model Master 전체 area in charge
            area_config = area_mapping['model_master']['employees'][auditor_id]
            conditions = area_config.get('conditions', [])
        elif area_mapping and auditor_id in area_mapping.get('auditor_trainer_areas', {}):
            #  days반 Auditor/Trainer
            area_config = area_mapping['auditor_trainer_areas'][auditor_id]
            conditions = area_config.get('conditions', [])
        else:
            # mapping 없으면 부하employee basedwith calculation (fallback)
            return self.calculate_area_aql_reject_rate_by_subordinates(auditor_id, subordinate_mapping)
        
        # AQL data withload
        aql_data = self.load_aql_data_for_area_calculation()
        if aql_data is None or aql_data.empty:
            return 0.0
        
        # conditions 미 위from configurationdone
        
        # conditionto 맞 data 필터링
        filtered_data = pd.DataFrame()
        for condition in conditions:
            if condition['type'] == 'ALL':
                # 전체 data 사용
                filtered_data = aql_data
                break
            elif condition['type'] == 'AND':
                # AND conditionwith 필터링
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
                # OR conditionwith 필터링
                for filter_item in condition['filters']:
                    col = filter_item['column']
                    val = filter_item['value']
                    if col in aql_data.columns:
                        temp_data = aql_data[aql_data[col] == val]
                        if not filtered_data.empty:
                            filtered_data = pd.concat([filtered_data, temp_data], ignore_index=True)
                        else:
                            filtered_data = temp_data
        
        # reject율 calculation
        if filtered_data.empty:
            return 0.0
        
        total_inspections = len(filtered_data)
        # Result column 름 찾기 (대소문자 구분 없)
        result_col = None
        for col in filtered_data.columns:
            if col.upper() == 'RESULT':
                result_col = col
                break
        
        if result_col:
            # FAIL 찾기 (대소문자 구분 없)
            total_failures = len(filtered_data[filtered_data[result_col].str.upper() == 'FAIL'])
        else:
            total_failures = 0
        
        if total_inspections > 0:
            reject_rate = (total_failures / total_inspections) * 100
            print(f"    → {auditor_id} ({area_config.get('name', 'Unknown')}): in charge area inspection {total_inspections}cases, failure {total_failures}cases, reject율 {reject_rate:.2f}%")
            return reject_rate
        
        return 0.0
    
    def calculate_area_aql_reject_rate_by_subordinates(self, auditor_id: str, subordinate_mapping: Dict[str, List[str]]) -> float:
        """
        부하employee based AQL reject율 calculation (fallback)
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
                total_inspections += 100  # 정: 각 employee당 평균 100items inspection
        
        if total_inspections > 0:
            return (total_failures / total_inspections) * 100
        return 0.0
    
    def normalize_column_name(self, col: str) -> str:
        """
        columnemployees 정규화: 공백, special문자, 줄바꿈 제거
        """
        if not isinstance(col, str):
            return str(col)
        # 공백 제거, 작은따옴표 제거, 줄바꿈 공백with 변경
        return col.strip().replace("'", "").replace("\n", " ").replace("  ", " ")
    
    def load_auditor_trainer_area_mapping(self) -> Dict:
        """
        Auditor/Trainer in charge area mapping JSON file withload
        """
        try:
            # config_files 폴더from 찾기
            json_path = self.base_path / 'config_files' / 'auditor_trainer_area_mapping.json'
            if not json_path.exists():
                # 없으면 프with젝트 루트of config_filesfrom 찾기
                from pathlib import Path
                json_path = Path('config_files/auditor_trainer_area_mapping.json')
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("⚠️ auditor_trainer_area_mapping.json file not found.")
        except Exception as e:
            print(f"⚠️ JSON file withload in progress Error: {e}")
        return {}
    
    def load_aql_data_for_area_calculation(self) -> pd.DataFrame:
        """
        in charge area calculation 위한 AQL data withload
        AQL history 폴더from file withload
        """
        try:
            # AQL history file 경with configuration
            month_upper = self.config.get_month_str('capital').upper()
            year = self.config.year
            file_path = self.base_path / 'input_files' / 'AQL history' / f'1.HSRG AQL REPORT-{month_upper}.{year}.csv'
            
            if file_path.exists():
                # file withload
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                
                # 빈 행 제거 (모든 value NaN인 행)
                df = df.dropna(how='all')
                
                # columnemployees 정규화
                df.columns = [self.normalize_column_name(col) for col in df.columns]

                # 실제 data cases수 with그
                print(f"  → AQL data withload: {len(df)}cases")

                # REPACKING PO 컬럼 생성 (REPACKING  컬럼 기반)
                # REPACKING  컬럼이 NaN이면 NORMAL PO, 값이 있으면 REPACKING PO
                if 'REPACKING PO' not in df.columns:
                    if 'REPACKING ' in df.columns or 'REPACKING' in df.columns:
                        # REPACKING  또는 REPACKING 컬럼 찾기
                        repacking_col = 'REPACKING ' if 'REPACKING ' in df.columns else 'REPACKING'
                        df['REPACKING PO'] = df[repacking_col].apply(
                            lambda x: 'NORMAL PO' if pd.isna(x) else 'REPACKING PO'
                        )
                        normal_count = (df['REPACKING PO'] == 'NORMAL PO').sum()
                        repack_count = (df['REPACKING PO'] == 'REPACKING PO').sum()
                        print(f"  ℹ️ REPACKING PO auto-generated: NORMAL PO={normal_count}, REPACKING PO={repack_count}")
                    else:
                        # REPACKING 관련 컬럼이 아예 없으면 모두 NORMAL PO로 간주
                        df['REPACKING PO'] = 'NORMAL PO'
                        print(f"  ℹ️ REPACKING PO column not found - treating all {len(df)} records as NORMAL PO")

                return df
            else:
                print(f"⚠️ AQL history file not found: {file_path}")
                
        except Exception as e:
            print(f"⚠️ AQL data withload in progress Error: {e}")
        
        return pd.DataFrame()
    
    def check_subordinates_continuous_fail(self, manager_id: str, subordinate_mapping: Dict[str, List[str]]) -> bool:
        """
        부하employee in progress 3-month consecutive AQL failures 있지 checking
        """
        if manager_id not in subordinate_mapping:
            return False

        for sub_id in subordinate_mapping[manager_id]:
            # FIX: Type-safe comparison - Employee No might be int64 after save_results() conversion
            sub_data = self.month_data[self.month_data['Employee No'].astype(str) == str(sub_id)]
            if not sub_data.empty:
                # FIX: Check if starts with 'YES' to match 'YES', 'YES_3MONTHS', 'YES_2MONTHS_AUG_SEP'
                continuous_fail_value = str(sub_data.iloc[0].get('Continuous_FAIL', 'NO'))
                if continuous_fail_value.startswith('YES'):
                    return True

        return False
    
    def calculate_aql_inspector_incentive(self, aql_mask, incentive_col: str, aql_col: str):
        """Type-1 AQL Inspector 3-part incentive calculation"""
        print("\n📊 TYPE-1 AQL INSPECTOR 3-part incentive calculation...")
        
        # AQL Inspector configuration withload
        aql_config = self.load_aql_inspector_config()
        if not aql_config:
            print("⚠️ AQL Inspector configuration file not found.")
            return
        
        for idx, row in self.month_data[aql_mask].iterrows():
            # 미 calculationdone 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            emp_id = row.get('Employee No', '')
            
            # Stop working employeealso 정상 calculation (exclude하지 않음)

            # Single Source of Truth: 새 표준 컬럼(cond_1~10) 사용
            # 출근 조건 체크 (C1: 출근율, C2: 무단결근, C3: 실근무일, C4: 최소근무일)
            attendance_fail = (
                row.get('cond_1_attendance_rate') == 'FAIL' or
                row.get('cond_2_unapproved_absence') == 'FAIL' or
                row.get('cond_3_actual_working_days') == 'FAIL' or
                row.get('cond_4_minimum_days') == 'FAIL'
            )
            
            # AQL Inspector 5PRS conditions apply 안 함
            # prs_pass = row.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%') == 'yes'
            
            # AQL condition: 당month failure cases수 0cases, 3-month consecutive failure 아님
            aql_fail = row.get(aql_col, 0) > 0
            continuous_fail = row.get('Continuous_FAIL', 'NO') == 'YES'
            
            # AQL INSPECTOR attendance condition(1-4) + 당month AQL condition(5)only 체크
            # 3-Part calculation은 default condition 충족 시toonly 실행
            if attendance_fail or aql_fail:
                incentive = 0
                # condition 미충족 시 Continuous_Months = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0
                fail_reason = []
                if attendance_fail:
                    fail_reason.append("attendance condition 미충족")
                if aql_fail:
                    fail_reason.append("당month AQL failure")
                print(f"    → {row.get('Full Name', 'Unknown')}: {', '.join(fail_reason)} → 0 VND")
                self.month_data.loc[idx, incentive_col] = incentive
                continue
            
            # Part 1, Part 3 consecutive month성 month 수 calculation
            part1_months, part3_months = self.get_aql_inspector_continuous_months(emp_id, aql_config)
            
            # Part 1: AQL inspection 평 결and incentive
            part1_amount = self.calculate_aql_part1_amount(part1_months, aql_config)
            
            # Part 2: CFA 자격증 incentive
            part2_amount = self.calculate_aql_part2_amount(emp_id, aql_config)
            
            # Part 3: HWK 클레임 방지 incentive
            part3_amount = self.calculate_aql_part3_amount(part3_months, aql_config)
            
            # 총 incentive calculation
            total_incentive = part1_amount + part2_amount + part3_amount

            self.month_data.loc[idx, incentive_col] = total_incentive

            # Continuous_Months column updated (Part 1 basis)
            self.month_data.loc[idx, 'Continuous_Months'] = part1_months

            # debugging 출력
            print(f"    → {row.get('Full Name', 'Unknown')} ({emp_id}):")
            print(f"      Part 1 ({part1_months}month): {part1_amount:,} VND")
            print(f"      Part 2 (CFA): {part2_amount:,} VND")
            print(f"      Part 3 ({part3_months}month): {part3_amount:,} VND")
            print(f"      총액: {total_incentive:,} VND")
        
        # 통계 출력
        receiving_count = (self.month_data[aql_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[aql_mask][incentive_col].sum()
        print(f"  → AQL Inspector 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def load_aql_inspector_config(self) -> Dict:
        """AQL Inspector incentive configuration withload"""
        try:
            # config_files 폴더from 찾기
            config_path = self.base_path / 'config_files' / 'aql_inspector_incentive_config.json'
            if not config_path.exists():
                # 없으면 프with젝트 루트of config_filesfrom 찾기
                from pathlib import Path
                config_path = Path('config_files/aql_inspector_incentive_config.json')
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ AQL Inspector configuration withload in progress Error: {e}")
        return {}
    
    def get_aql_inspector_continuous_months(self, emp_id: str, aql_config: Dict) -> Tuple[int, int]:
        """AQL Inspector Part 1 and Part 3 continuous months calculation"""
        if emp_id in aql_config.get('aql_inspectors', {}):
            # 동적으로 이전 달 키 생성 (Fixed: 2025-11-26 - removed hardcoded 'june_2025_incentive')
            prev_month_info = {}

            if self.config.previous_months:
                # Try to read from previous month (e.g., October for November calculation)
                prev_month = self.config.previous_months[-1]
                prev_month_key = f"{prev_month}_{self.config.year}_incentive"
                prev_month_info = aql_config['aql_inspectors'][emp_id].get(prev_month_key, {})

                # Fallback: if previous month data not found, try second-to-last month
                if not prev_month_info and len(self.config.previous_months) > 1:
                    fallback_month = self.config.previous_months[-2]
                    fallback_key = f"{fallback_month}_{self.config.year}_incentive"
                    prev_month_info = aql_config['aql_inspectors'][emp_id].get(fallback_key, {})

            # If conditions met, increment months; if failed, will be reset by caller
            part1_months = prev_month_info.get('part1_months', 0) + 1
            part3_months = prev_month_info.get('part3_months', 0) + 1

            # Cap at 15 months max
            part1_months = min(part1_months, 15)
            part3_months = min(part3_months, 15)

            return part1_months, part3_months

        # New employee case
        return 1, 1
    
    def calculate_aql_part1_amount(self, months: int, aql_config: Dict) -> int:
        """Part 1: AQL inspection 평 결and incentive calculation"""
        part1_config = aql_config.get('parts', {}).get('part1', {})
        amounts = part1_config.get('incentive_table', {}).get('sustained_performance', {}).get('amounts', {})
        
        # 문자열 키 정수with 변환하여 조회
        return amounts.get(str(months), 150000)
    
    def calculate_aql_part2_amount(self, emp_id: str, aql_config: Dict) -> int:
        """Part 2: CFA 자격증 incentive calculation"""
        # employee별 CFA 자격증 보유 여부 checking
        if emp_id in aql_config.get('aql_inspectors', {}):
            if aql_config['aql_inspectors'][emp_id].get('cfa_certified', False):
                return aql_config.get('parts', {}).get('part2', {}).get('amount', 700000)
        return 0
    
    def calculate_aql_part3_amount(self, months: int, aql_config: Dict) -> int:
        """Part 3: HWK 클레임 방지 incentive calculation"""
        part3_config = aql_config.get('parts', {}).get('part3', {})
        amounts = part3_config.get('incentive_table', {})
        
        # 문자열 키 정수with 변환하여 조회
        return amounts.get(str(months), 0)
    
    def get_assembly_inspector_amount(self, continuous_months: int) -> int:
        """consecutive 충족 month 수to 따른 Assembly Inspector incentive amount 결정 테블은 Assembly Inspector, Model Master, Audit & Training
        3items position 모두to same days하게 apply됩니다.
        JSON configurationfrom 테블 withload (하load코ing 없음)

        Condition 1: consecutivewith performance 유지 시 (2-month 상)
        Condition 2: 1-monthonly month성 시 150,000 VND 고정
        """
        # JSON configurationfrom incentive 테블 져오기 (필수)
        if not hasattr(self, 'position_matrix') or 'incentive_progression' not in self.position_matrix:
            print(f"⚠️ Warning: position_condition_matrix.jsonto incentive_progression 없습니다")
            return 0

        progression = self.position_matrix['incentive_progression'].get('TYPE_1_PROGRESSIVE', {})
        table = progression.get('progression_table', {})

        if not table:
            print(f"⚠️ Warning: progression_table 비어있습니다")
            return 0

        max_months = progression.get('max_months', 12)

        # 최대 month수 상은 최대 amount
        if continuous_months >= max_months:
            return table.get(str(max_months), 0)

        # 테블from amount 찾기
        return table.get(str(continuous_months), 0)
    
    def calculate_assembly_inspector_incentive_type1_only(self):
        """Type-1 Assembly Inspector 및 AQL Inspector incentive calculation
        
        10 conditions 체계 (4-4-2 구조):
        - attendance condition (4items): attendance율, 무단결근, 실제 근무 days, minimum 12 days
        - AQL condition (4items): 당month failure, 3-month consecutive(ASSEMBLYonly), 부하employee(해당없음), area(해당없음)
        - 5PRS conditions (2items): inspection량, passed율
        
        ASSEMBLY INSPECTOR: 8/10 condition apply (6번 condition include)
        AQL INSPECTOR: 5/10 condition apply (6번 condition exclude)
        """
        print("\n👥 TYPE-1 ASSEMBLY/AQL INSPECTOR incentive calculation...")
        
        # Type-1 Assembly Inspector 필터링
        assembly_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                (
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('ASSEMBLY', na=False)) &
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
                ) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^A[1-5][AB]?$', na=False))  # A1A-A5B codes
            )
        )
        
        # Type-1 AQL Inspector 필터링
        aql_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                (
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('AQL', na=False)) &
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('INSPECTOR', na=False))
                ) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^AQL[1-5]?[AB]?$', na=False))  # AQL codes
            )
        )
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
        
        # AQL Inspector processing
        if aql_mask.any():
            self.calculate_aql_inspector_incentive(aql_mask, incentive_col, aql_col)
        
        # Assembly Inspector processing
        for idx, row in self.month_data[assembly_mask].iterrows():
            # 미 calculationdone 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            # Stop working employeealso 정상 calculation (exclude하지 않음)
            
            # emp_id first 정of (debugging 목적with 사용done)
            emp_id = row.get('Employee No', '')

            # ========================================
            # 100% 조건 충족 규칙 적용
            # ========================================
            # 인센티브는 모든 적용 가능한 조건을 100% 충족할 때만 지급
            # conditions_pass_rate가 100.0이 아니면 무조건 0 VND

            pass_rate = row.get('conditions_pass_rate', 0)

            if pass_rate < 100.0:
                # 조건 미충족: 인센티브 0, Continuous_Months 리셋
                incentive = 0
                self.month_data.loc[idx, 'Continuous_Months'] = 0

                # 디버깅: 어떤 조건이 실패했는지 기록
                failed_conditions = []
                if row.get('cond_1_attendance_rate') == 'FAIL':
                    failed_conditions.append('출근율<88%')
                if row.get('cond_2_unapproved_absence') == 'FAIL':
                    failed_conditions.append('무단결근>2일')
                if row.get('cond_3_actual_working_days') == 'FAIL':
                    failed_conditions.append('실제근무일=0')
                if row.get('cond_4_minimum_days') == 'FAIL':
                    failed_conditions.append('최소근무일<12')
                if row.get('cond_5_aql_personal_failure') == 'FAIL':
                    failed_conditions.append('개인AQL실패>0')
                if row.get('cond_6_aql_continuous') == 'FAIL':
                    failed_conditions.append('3개월연속AQL실패')
                if row.get('cond_7_aql_team_area') == 'FAIL':
                    failed_conditions.append('팀/지역AQL실패')
                if row.get('cond_8_area_reject') == 'FAIL':
                    failed_conditions.append('지역불량률≥3%')
                if row.get('cond_9_5prs_pass_rate') == 'FAIL':
                    failed_conditions.append('5PRS합격률<95%')
                if row.get('cond_10_5prs_inspection_qty') == 'FAIL':
                    failed_conditions.append('5PRS검사량<100')

                if failed_conditions:
                    print(f"      {row.get('Full Name', emp_id)}: 조건 미충족 → 0 VND (실패: {', '.join(failed_conditions)})")
            else:
                # consecutive 충족 month 수 calculation
                continuous_months = self.data_processor.calculate_continuous_months_from_history(emp_id, self.month_data)

                # consecutive 충족 month 수to 따른 차etc. 지급
                incentive = self.get_assembly_inspector_amount(continuous_months)

                # Continuous_Months column updated
                self.month_data.loc[idx, 'Continuous_Months'] = continuous_months

                # debugging 위한 출력
                if continuous_months > 0:
                    print(f"    → {row.get('Full Name', 'Unknown')} ({emp_id}): {continuous_months}month consecutive → {incentive:,} VND")

            self.month_data.loc[idx, incentive_col] = incentive
            
            # debugging: 619060201 employee checking
            if emp_id == '619060201':
                print(f"    [debug] 619060201 updated: {incentive_col} = {incentive:,.0f} VND")
                actual_value = self.month_data.loc[idx, incentive_col]
                print(f"    [debug] 실제 saveddone value: {actual_value:,.0f} VND")
        
        # 통계 출력
        receiving_count = (self.month_data[assembly_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[assembly_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def create_manager_subordinate_mapping(self) -> Dict[str, List[str]]:
        """manager-부하 employee mapping created"""
        print("\n📊 manager-부하 employee mapping created in progress...")

        subordinate_mapping = {}

        # 계산 월 시작일 (퇴사자 필터링용)
        calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
        print(f"  → 계산 월: {calc_month_start.strftime('%Y-%m')}")

        # Direct boss name column 찾기
        boss_col = self.data_processor.detect_column_names(self.month_data, [
            'direct boss name', 'Direct Boss Name', 'DIRECT BOSS NAME',
            'Manager', 'MANAGER', 'Boss Name'
        ])

        if not boss_col:
            print("❌ 상사 정보 column not found.")
            return subordinate_mapping

        print(f"  → 사용 중인 boss column: '{boss_col}'")

        # 디버그용 카운터
        debug_employees = {619020468, 621110013}  # THỊ MY, SỬ HUYỀN TRANG
        debug_found = {emp_id: 0 for emp_id in debug_employees}
        debug_names = {}  # 문제 직원들의 실제 이름 저장

        # 문제 직원들의 이름 찾기
        print(f"  → Employee No column dtype: {self.month_data['Employee No'].dtype}")
        print(f"  → 총 직원 수: {len(self.month_data)}")

        for debug_id in debug_employees:
            # int와 str 모두 시도
            emp_row1 = self.month_data[self.month_data['Employee No'] == debug_id]
            emp_row2 = self.month_data[self.month_data['Employee No'] == str(debug_id)]

            if not emp_row1.empty:
                name = emp_row1.iloc[0]['Full Name']
                debug_names[debug_id] = name
                print(f"  → 찾은 직원 (int): {debug_id} = '{name}'")
            elif not emp_row2.empty:
                name = emp_row2.iloc[0]['Full Name']
                debug_names[debug_id] = name
                print(f"  → 찾은 직원 (str): {debug_id} = '{name}'")
            else:
                print(f"  → 직원 찾을 수 없음: {debug_id}")
                # 샘플 Employee No 출력
                sample_ids = self.month_data['Employee No'].head(3).tolist()
                print(f"     샘플 Employee No: {sample_ids}")

        # 디버그: boss_name이 debug_names와 일치하는지 추적
        boss_name_matches = {debug_name: 0 for debug_name in debug_names.values()}

        # 퇴사자 필터링 카운터
        excluded_resigned_count = 0

        for _, row in self.month_data.iterrows():
            boss_name = row.get(boss_col)
            if pd.notna(boss_name) and boss_name.strip():
                emp_id = row.get('Employee No', '')

                # ✅ 퇴사자 필터링: 계산 월 이전 퇴사자는 부하 직원 매핑에서 제외
                stop_date_str = row.get('Stop working Date')
                if pd.notna(stop_date_str):
                    try:
                        stop_date = pd.to_datetime(stop_date_str)
                        if stop_date < calc_month_start:
                            # 계산 월 이전에 퇴사한 직원은 매핑에서 제외
                            excluded_resigned_count += 1
                            continue
                    except (ValueError, TypeError):
                        pass  # 날짜 변환 실패 시 퇴사자 아님으로 처리

                # 디버그: 문제 직원 이름과 매칭되는지 확인
                if boss_name in debug_names.values():
                    boss_name_matches[boss_name] += 1

                # 상사의 Employee No 찾기
                boss_data = self.month_data[
                    self.month_data['Full Name'] == boss_name
                ]

                # 디버그: 문제 직원인 경우 상세 출력
                if boss_name in debug_names.values() and not boss_data.empty:
                    boss_id_test = boss_data.iloc[0].get('Employee No', '')
                    print(f"  [DEBUG] Boss '{boss_name}' 찾음, boss_id = {boss_id_test} (type: {type(boss_id_test)})")

                if not boss_data.empty:
                    boss_id = boss_data.iloc[0].get('Employee No', '')
                    # Employee No를 int로 변환 (일관성 유지)
                    if boss_id:
                        try:
                            boss_id = int(boss_id) if boss_id != '' else None
                            emp_id = int(emp_id) if emp_id != '' else None
                        except (ValueError, TypeError):
                            pass

                    if boss_id:
                        if boss_id not in subordinate_mapping:
                            subordinate_mapping[boss_id] = []
                        subordinate_mapping[boss_id].append(emp_id)

                        # 디버그: 문제 LINE LEADER의 부하직원 카운트
                        if boss_id in debug_employees:
                            debug_found[boss_id] += 1
                            print(f"  [DEBUG] {boss_id}의 부하직원 추가: {emp_id}")
                    else:
                        if boss_name in debug_names.values():
                            print(f"  [DEBUG] Boss '{boss_name}' 찾았지만 boss_id가 비어있음!")
                else:
                    # 디버그: boss_name이 문제 직원 이름인 경우 출력
                    for debug_id, debug_name in debug_names.items():
                        if boss_name == debug_name:
                            print(f"  [DEBUG] '{boss_name}'를 상사로 가진 직원 발견, 하지만 month_data에서 '{boss_name}' 찾을 수 없음!")
                            # month_data에 이 이름이 있는지 확인
                            name_exists = (self.month_data['Full Name'] == boss_name).any()
                            print(f"  [DEBUG] month_data에 '{boss_name}' 존재 여부: {name_exists}")

        if excluded_resigned_count > 0:
            print(f"  → 퇴사자 제외: {excluded_resigned_count}명 (계산 월 이전 퇴사)")

        # 디버그: boss_name 매칭 결과 출력
        print(f"\n  → Boss name 매칭 결과:")
        for name, count in boss_name_matches.items():
            print(f"     '{name}': {count}명이 이 직원을 상사로 가짐")

        # 디버그 출력
        for debug_id in debug_employees:
            count = debug_found.get(debug_id, 0)
            if count > 0:
                print(f"  [DEBUG] Employee {debug_id}: {count}명의 부하직원 매핑됨")
            else:
                print(f"  [DEBUG] Employee {debug_id}: 부하직원 없음 (boss로 인식되지 않음)")
        
        print(f"✅ mapping completed: {len(subordinate_mapping)} employeesof manager")
        return subordinate_mapping
    
    def calculate_line_leader_incentive_type1_only(self, subordinate_mapping: Dict[str, List[str]]):
        """Type-1 Line Leader incentive calculation"""
        print("\n👥 TYPE-1 LINE LEADER incentive calculation (12% applied + incentive receipt ratio reflected)...")
        
        # Type-1 Line Leader 필터링
        line_leader_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (
                (
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
                    (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
                ) |
                (self.month_data['FINAL QIP POSITION NAME CODE'].str.upper().str.match(r'^(E|L[1-5]|LL[AB]?)$', na=False))  # LINE LEADER codes (E 실제with LINE LEADERwith 사용done)
            )
        )
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        for idx, row in self.month_data[line_leader_mask].iterrows():
            # 미 calculationdone 경우 스킵
            if row[incentive_col] > 0:
                continue
            
            leader_id = row.get('Employee No', '')
            # Employee No를 int로 변환 (subordinate_mapping key와 타입 일치)
            try:
                leader_id = int(leader_id) if leader_id != '' else None
            except (ValueError, TypeError):
                leader_id = None

            # attendance condition 체크 - 모든 positionto 공통 apply
            # Phase 1: Single Source of Truth - 새 표준 컬럼(cond_1~4) 사용
            cond1 = row.get('cond_1_attendance_rate')
            cond2 = row.get('cond_2_unapproved_absence')
            cond3 = row.get('cond_3_actual_working_days')
            cond4 = row.get('cond_4_minimum_days')

            attendance_fail = (
                cond1 == 'FAIL' or
                cond2 == 'FAIL' or
                cond3 == 'FAIL' or
                cond4 == 'FAIL'
            )

            # 디버그: 문제 직원인 경우 출근 조건 값 출력
            if leader_id in {619020468, 621110013}:
                print(f"    [DEBUG] {row.get('Full Name')} ({leader_id}):")
                print(f"       cond1={cond1}, cond2={cond2}, cond3={cond3}, cond4={cond4}")
                print(f"       attendance_fail={attendance_fail}")

            # attendance condition 미충족 시 incentive 0
            if attendance_fail:
                incentive = 0
                print(f"    → Line Leader {row.get('Full Name', 'Unknown')} ({leader_id}): attendance condition 미충족")
            # 부하employee incentive calculation
            elif leader_id in subordinate_mapping:
                subordinates = subordinate_mapping[leader_id]
                total_sub_incentive = 0
                receiving_count = 0  # incentive 받 employee 수
                total_count = 0      # 전체 부하employee 수

                # 디버그: 문제 직원인 경우
                if leader_id in {619020468, 621110013}:
                    print(f"       부하직원 수: {len(subordinates)}")

                for sub_id in subordinates:
                    # Employee No 타입 일치를 위해 str로 변환하여 검색
                    sub_data = self.month_data[self.month_data['Employee No'] == str(sub_id)]

                    # 디버그: 부하직원을 찾지 못하는 경우
                    if leader_id in {619020468, 621110013} and sub_data.empty:
                        print(f"       [WARNING] 부하직원 {sub_id} (type: {type(sub_id)}) 찾을 수 없음!")
                        # Employee No 컬럼의 타입 확인
                        sample_emp_no = self.month_data['Employee No'].iloc[0]
                        print(f"       month_data Employee No 타입: {type(sample_emp_no)}")

                    if not sub_data.empty:
                        sub_row = sub_data.iloc[0]
                        # Type-1 부하employeeonly calculation
                        if sub_row.get('ROLE TYPE STD') == 'TYPE-1':
                            total_count += 1
                            sub_incentive = float(sub_row.get(incentive_col, 0))
                            if sub_incentive > 0:
                                receiving_count += 1
                                total_sub_incentive += sub_incentive
                
                # JSON matrix based condition 체크
                should_check_subordinates = False
                if POSITION_CONDITION_MATRIX:
                    pos_config = get_position_config_from_matrix('TYPE-1', 'LINE LEADER')
                    if pos_config:
                        applicable_conditions = pos_config.get('applicable_conditions', [])
                        # condition 7: 팀/area AQL (부하employee AQL 체크)
                        if 7 in applicable_conditions:
                            should_check_subordinates = True
                            print(f"    → Line Leader - JSON based condition 7 apply")
                else:
                    # 폴백: existing with직
                    should_check_subordinates = True
                
                # 부하employee in progress 3-month consecutive AQL failures checking
                has_continuous_fail = False
                if should_check_subordinates:
                    has_continuous_fail = self.check_subordinates_continuous_fail(leader_id, subordinate_mapping)
                
                if has_continuous_fail:
                    incentive = 0
                    print(f"    → Line Leader {row.get('Full Name', 'Unknown')}: 부하employee in progress 3-month consecutive AQL failures 있음 (condition 7 미충족)")
                elif total_count > 0 and receiving_count > 0:
                    # 12% calculation 및 incentive 수령 비율 반영
                    receiving_ratio = receiving_count / total_count
                    incentive = int(total_sub_incentive * 0.12 * receiving_ratio)
                    
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
        """Type-1 Head(Group Leader) incentive calculation
        
        10 conditions 체계 in progress 4/10 conditiononly apply:
        - attendance condition (4items): attendance율, 무단결근, 실제 근무 days, minimum 12 days
        - AQL condition (4items): 모두 미apply (부하employee conditionalso 미apply)
        - 5PRS conditions (2items): 모두 미apply
        
        GROUP LEADER: 4/10 condition apply (attendance conditiononly)
        """
        print("\n👥 TYPE-1 HEAD (GROUP LEADER) incentive calculation (Line Leader average × 2)...")
        
        # Type-1 Head/Group Leader 필터링
        head_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            ((self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('HEAD', na=False)) |
             (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('GROUP', na=False) & 
              self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False)))
        )
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        for idx, row in self.month_data[head_mask].iterrows():
            # 미 calculationdone 경우 스킵
            if row[incentive_col] > 0:
                continue

            # FIX: Employee No를 int로 변환 (subordinate_mapping key와 타입 일치)
            head_id = row.get('Employee No', '')
            try:
                head_id = int(head_id) if head_id != '' else None
            except (ValueError, TypeError):
                head_id = None

            # attendance condition 체크 - 모든 positionto 공통 apply
            # Phase 1: Single Source of Truth - 새 표준 컬럼(cond_1~4) 사용
            attendance_fail = (
                row.get('cond_1_attendance_rate') == 'FAIL' or
                row.get('cond_2_unapproved_absence') == 'FAIL' or
                row.get('cond_3_actual_working_days') == 'FAIL' or
                row.get('cond_4_minimum_days') == 'FAIL'
            )
            
            # attendance condition 미충족 시 incentive 0
            if attendance_fail:
                incentive = 0
                print(f"    → Head/Group Leader {row.get('Full Name', 'Unknown')} ({head_id}): attendance condition 미충족")
            else:
                # 자신of 팀 내 Line Leader들 찾기 및 평균 calculation
                line_leaders = self._find_team_line_leaders(head_id, subordinate_mapping)

                avg_incentive = 0
                if line_leaders:
                    avg_incentive = self._calculate_line_leader_average_unified(
                        line_leaders, head_id, 'HEAD'
                    )

                # Line Leader 평균 0인 경우 fallback 사용
                if avg_incentive > 0:
                    # Line Leader 평균of 2배
                    incentive = int(avg_incentive * 2)
                    print(f"    → Head/Group Leader {row.get('Full Name', 'Unknown')} ({head_id}): Line Leader 평균 {avg_incentive:,.0f} × 2 = {incentive:,} VND")
                else:
                    # Fallback: 전체 TYPE-1 LINE LEADER 평균 사용 (0 포함) - 2025-11-30 변경
                    all_line_leaders = self.month_data[
                        (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                        (self.month_data['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
                    ]

                    if len(all_line_leaders) > 0:
                        avg_incentive = int(all_line_leaders[incentive_col].mean())
                        incentive = int(avg_incentive * 2)
                        print(f"    → Head/Group Leader {row.get('Full Name', 'Unknown')} ({head_id}): 전체 LINE LEADER 평균 {avg_incentive:,.0f} × 2 = {incentive:,} VND (Fallback)")
                    else:
                        incentive = 0
                        print(f"    → Head/Group Leader {row.get('Full Name', 'Unknown')} ({head_id}): LINE LEADER 없음 → 0 VND")
            
            self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력
        receiving_count = (self.month_data[head_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[head_mask][incentive_col].sum()
        print(f"  → 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def calculate_managers_by_manual_logic_fixed(self, subordinate_mapping: Dict[str, List[str]]):
        """manager incentive calculation"""
        print("\n👔 manager incentive calculation...")
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        # 각 manager position별with processing - accurate Position name matching 사용
        manager_configs = [
            {'position_names': ['S.MANAGER', 'SENIOR MANAGER'], 'multiplier': 4.0, 'name': 'Senior Manager'},
            {'position_names': ['MANAGER'], 'multiplier': 3.5, 'name': 'Manager'},
            {'position_names': ['A.MANAGER', 'ASSISTANT MANAGER'], 'multiplier': 3.0, 'name': 'Assistant Manager'},
            {'position_names': ['(V) SUPERVISOR', 'VICE SUPERVISOR', 'V.SUPERVISOR'], 'multiplier': 2.5, 'name': '(Vice) Supervisor'},
            {'position_names': ['SUPERVISOR'], 'multiplier': 2.5, 'name': 'Supervisor'},
        ]
        
        for config in manager_configs:
            print(f"\n  🔹 {config['name']} Calculating...")

            # 해당 position 필터링 - accurate Position name matching
            mask = (self.month_data['ROLE TYPE STD'] == 'TYPE-1') & (
                self.month_data['QIP POSITION 1ST  NAME'].isin(config['position_names'])
            )

            # 이미 처리된 직원들은 스킵
            for idx in self.month_data[mask].index:
                row = self.month_data.loc[idx]
                emp_name = row.get('Full Name', 'Unknown')

                # 미 calculationdone 경우 스킵
                if row[incentive_col] > 0:
                    continue

                # FIX: Employee No를 int로 변환 (subordinate_mapping key와 타입 일치)
                manager_id = row.get('Employee No', '')
                try:
                    manager_id = int(manager_id) if manager_id != '' else None
                except (ValueError, TypeError):
                    manager_id = None

                # attendance condition 체크 - 모든 positionto 공통 apply (100% 충족 필수)
                # Phase 1: Single Source of Truth - 새 표준 컬럼(cond_1~4) 사용
                # FIX: NOT_APPLICABLE should be treated as PASS for interim reports
                condition_1_pass = row.get('cond_1_attendance_rate') in ['PASS', 'NOT_APPLICABLE']
                condition_2_pass = row.get('cond_2_unapproved_absence') == 'PASS'
                condition_3_pass = row.get('cond_3_actual_working_days') == 'PASS'
                # FIX: NOT_APPLICABLE should be treated as PASS (e.g., interim reports with < 12 working days)
                condition_4_pass = row.get('cond_4_minimum_days') in ['PASS', 'NOT_APPLICABLE']

                all_conditions_pass = (condition_1_pass and condition_2_pass and
                                      condition_3_pass and condition_4_pass)

                # 100% 충족 여부 checking
                if not all_conditions_pass:
                    incentive = 0
                    failed_conditions = []
                    if not condition_1_pass: failed_conditions.append('1')
                    if not condition_2_pass: failed_conditions.append('2')
                    if not condition_3_pass: failed_conditions.append('3')
                    if not condition_4_pass: failed_conditions.append('4')
                    print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): condition 미충족 [{', '.join(failed_conditions)}]")
                else:
                    # JSON configurationfrom calculation 방법 checking
                    position_code = row.get('FINAL QIP POSITION NAME CODE', '')
                    position_config = self.position_matrix.get('positions', {}).get(position_code, {})
                    incentive_config = position_config.get('incentive_amount', {})
                    calc_method = incentive_config.get('calculation_method', '')

                    if calc_method == 'line_leader_average':
                        # Line Leader 평균 based calculation (JSON same적 calculation)
                        multiplier = incentive_config.get('multiplier', config['multiplier'])
                        line_leaders = self._find_team_line_leaders(manager_id, subordinate_mapping)

                        if line_leaders:
                            avg_incentive = self._calculate_line_leader_average_unified(
                                line_leaders, manager_id, config['name']
                            )
                            incentive = int(avg_incentive * multiplier)
                            print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): Line Leader 평균 {avg_incentive:,.0f} × {multiplier} = {incentive:,} VND")
                        else:
                            # Fallback: 전체 TYPE-1 LINE LEADER 평균 사용 (0 포함) - 2025-11-30 변경
                            all_line_leaders = self.month_data[
                                (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                                (self.month_data['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
                            ]

                            if len(all_line_leaders) > 0:
                                avg_incentive = int(all_line_leaders[incentive_col].mean())
                                incentive = int(avg_incentive * multiplier)
                                print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): 전체 LINE LEADER 평균 {avg_incentive:,.0f} × {multiplier} = {incentive:,} VND")
                            else:
                                incentive = 0
                                print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): LINE LEADER 없음 → 0 VND")
                    else:
                        # existing with직 (고정 amount etc.)
                        min_amt = incentive_config.get('min', 0)
                        max_amt = incentive_config.get('max', min_amt)

                        if min_amt > 0 and min_amt == max_amt:
                            incentive = min_amt
                            print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): JSON 고정value → {incentive:,} VND")
                        else:
                            # Line Leader 평균 based calculation (Fallback)
                            line_leaders = self._find_team_line_leaders(manager_id, subordinate_mapping)

                            if line_leaders:
                                avg_incentive = self._calculate_line_leader_average_unified(
                                    line_leaders, manager_id, config['name']
                                )
                                incentive = int(avg_incentive * config['multiplier'])
                                print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): Line Leader 평균 based (fallback) → {incentive:,} VND")
                            else:
                                # Fallback: 전체 TYPE-1 LINE LEADER 평균 사용 (0 포함) - 2025-11-30 변경
                                all_line_leaders = self.month_data[
                                    (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                                    (self.month_data['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
                                ]

                                if len(all_line_leaders) > 0:
                                    avg_incentive = int(all_line_leaders[incentive_col].mean())
                                    incentive = int(avg_incentive * config['multiplier'])
                                    print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): 전체 LINE LEADER 평균 {avg_incentive:,.0f} × {config['multiplier']} = {incentive:,} VND")
                                else:
                                    if min_amt > 0:
                                        incentive = min_amt
                                    else:
                                        incentive = 0
                                        print(f"      → {config['name']} {row.get('Full Name', 'Unknown')} ({manager_id}): LINE LEADER 없음 → 0 VND")

                self.month_data.loc[idx, incentive_col] = incentive
        
        # 통계 출력 - 모든 manager 대상
        # manager 마스크 created
        manager_mask = pd.Series([False] * len(self.month_data))
        for config in manager_configs:
            temp_mask = (self.month_data['ROLE TYPE STD'] == 'TYPE-1') & (
                self.month_data['QIP POSITION 1ST  NAME'].isin(config['position_names'])
            )
            manager_mask |= temp_mask
        
        receiving_count = (self.month_data[manager_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[manager_mask][incentive_col].sum()
        print(f"  → manager 총 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")
    
    def _find_team_line_leaders(self, manager_id, subordinate_mapping: Dict[str, List[str]]) -> List:
        """팀 내 소속 Line Leader 찾기 (역방향 매핑 - direct boss 기준)

        2025-12-01 수정:
        - 기존 subordinate_mapping 대신 역방향 매핑 사용
        - LINE LEADER의 'direct boss name' 또는 'MST direct boss name'이
          manager와 일치하는 경우 소속으로 판단
        - 임산부, 퇴사자 제외
        """
        line_leaders = []

        # manager의 이름과 ID 가져오기
        manager_data = self.month_data[
            (self.month_data['Employee No'] == str(manager_id)) |
            (self.month_data['Employee No'] == int(manager_id) if str(manager_id).isdigit() else False)
        ]

        if manager_data.empty:
            print(f"      → Manager {manager_id} 정보 없음")
            return line_leaders

        manager_name = manager_data.iloc[0].get('Full Name', '')

        # 계산 월 시작일 (퇴사자 필터링용)
        calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)

        # TYPE-1 LINE LEADER 필터링
        line_leader_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
        )

        type1_line_leaders = self.month_data[line_leader_mask]

        for _, ll_row in type1_line_leaders.iterrows():
            # 역방향 매핑: LINE LEADER의 boss가 이 manager인지 확인
            mst_boss = ll_row.get('MST direct boss name', '')
            direct_boss = ll_row.get('direct boss name', '')

            # MST direct boss name은 Employee No (숫자)
            # direct boss name은 Full Name (문자열)
            is_my_subordinate = False

            # MST direct boss name으로 매칭 (Employee No 비교)
            if pd.notna(mst_boss) and str(mst_boss).strip():
                try:
                    mst_boss_id = int(float(str(mst_boss).strip()))
                    if mst_boss_id == int(manager_id):
                        is_my_subordinate = True
                except (ValueError, TypeError):
                    pass

            # direct boss name으로 매칭 (Full Name 비교)
            if not is_my_subordinate and pd.notna(direct_boss) and str(direct_boss).strip():
                if str(direct_boss).strip() == manager_name:
                    is_my_subordinate = True

            if is_my_subordinate:
                # 퇴사자 제외: 계산 월 이전 퇴사자 제외
                stop_date_str = ll_row.get('Stop working Date')
                if pd.notna(stop_date_str):
                    try:
                        stop_date = pd.to_datetime(stop_date_str)
                        if stop_date < calc_month_start:
                            print(f"      → {ll_row.get('Full Name')} 제외 (퇴사자)")
                            continue
                    except (ValueError, TypeError):
                        pass

                # 임산부 제외
                pregnant = ll_row.get('pregnant vacation-yes or no', '')
                if pd.notna(pregnant) and str(pregnant).strip().lower() == 'yes':
                    print(f"      → {ll_row.get('Full Name')} 제외 (임산부)")
                    continue

                line_leaders.append(ll_row.to_dict())

        if line_leaders:
            incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
            print(f"      → {manager_name} ({manager_id}) 소속 LINE LEADER {len(line_leaders)}명 발견")
            for ll in line_leaders:
                ll_incentive = ll.get(incentive_col, 0) or 0
                print(f"         - {ll.get('Full Name')}: {ll_incentive:,.0f} VND")

        return line_leaders
    
    def _calculate_line_leader_average_unified(self, line_leaders: List, manager_id: str, position: str) -> float:
        """Line Leader 평균 incentive calculation - 전체 평균 (0 포함)

        2025-12-01 수정:
        - 기존: 수령자만 평균 (incentive > 0인 직원만)
        - 변경: 전체 평균 (0 포함) - 단, 임산부/퇴사자는 _find_team_line_leaders에서 이미 제외됨
        - 소속 LINE LEADER 중 0 VND 수령자도 평균 계산에 포함
        - 이유: 내 팀원이 인센티브를 못 받으면 내 인센티브도 줄어들어야 함
        """
        if not line_leaders:
            return 0

        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        total_incentive = 0
        count = 0

        for leader in line_leaders:
            if isinstance(leader, dict):
                current_incentive = float(leader.get(incentive_col, 0) or 0)
            else:
                current_leader_data = self.month_data[
                    self.month_data['Employee No'] == leader
                ]
                if not current_leader_data.empty:
                    current_incentive = float(current_leader_data.iloc[0].get(incentive_col, 0) or 0)
                else:
                    current_incentive = 0

            # ✅ 변경: 모든 LINE LEADER 포함 (0 VND도 포함)
            total_incentive += current_incentive
            count += 1

        if count > 0:
            avg = total_incentive / count
            print(f"      → 평균 계산: {total_incentive:,.0f} / {count} = {avg:,.0f} VND (0 포함 전체 평균)")
            return avg
        return 0
    
    def calculate_type2_incentive(self):
        """Type-2 incentive calculation - 2단계 방식"""
        print("\n📊 TYPE-2 incentive calculation (2-stage method)...")

        # STEP 1: LINE LEADER 및  day-shift employees first calculation
        print("  [STEP 1] TYPE-2 LINE LEADER 및  day-shift employees calculation...")
        self.calculate_type2_non_group_leaders()

        # STEP 2: GROUP LEADER calculation (LINE LEADER 평균 사용)
        print("  [STEP 2] TYPE-2 GROUP LEADER calculation...")
        self.calculate_type2_group_leaders_final()

        # 통계 출력
        type2_mask = self.month_data['ROLE TYPE STD'] == 'TYPE-2'
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        receiving_count = (self.month_data[type2_mask][incentive_col] > 0).sum()
        total_amount = self.month_data[type2_mask][incentive_col].sum()
        print(f"  → 전체 TYPE-2 수령 인원: {receiving_count}명, 총액: {total_amount:,.0f} VND")

    def calculate_type2_non_group_leaders(self):
        """TYPE-2 GROUP LEADER exclude한 모든 employee calculation"""
        type2_mask = self.month_data['ROLE TYPE STD'] == 'TYPE-2'

        # Type-1 참조 맵 created
        type1_reference = self._create_type1_reference_map()

        # TYPE-2 포지션 matching rule withload
        type2_mapping = self.load_type2_position_mapping()

        # 부하employee mapping (GROUP LEADER 계산용)
        subordinate_mapping = self.create_manager_subordinate_mapping()

        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"

        # GROUP LEADER exclude한 employee들only calculation
        for idx, row in self.month_data[type2_mask].iterrows():
            # 미 calculationdone 경우 스킵
            if row[incentive_col] > 0:
                continue

            position = row.get('QIP POSITION 1ST  NAME', '')
            position_upper = position.upper() if pd.notna(position) else ''
            emp_id = row.get('Employee No', '')

            # GROUP LEADER STEP 2from processing하므with 여기서 스킵
            if position_upper == 'GROUP LEADER' or (position_upper == 'QA3A'):
                continue

            # Stop Working Date 체크 추
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

            # ========================================
            # 100% 조건 충족 규칙 적용 (TYPE-2)
            # ========================================
            # TYPE-2는 출근 조건만 적용되지만, 적용되는 조건은 100% 충족해야 함

            pass_rate = row.get('conditions_pass_rate', 0)

            # 100% 충족 규칙: 적용 가능한 모든 조건을 충족해야 함
            if pass_rate < 100.0:
                # 조건 미충족: 0 VND
                # (Continuous_Months는 TYPE-2에 적용되지 않음)
                incentive = 0

                # 디버깅: 어떤 조건이 실패했는지
                failed_conditions = []
                if row.get('cond_1_attendance_rate') == 'FAIL':
                    failed_conditions.append('출근율<88%')
                if row.get('cond_2_unapproved_absence') == 'FAIL':
                    failed_conditions.append('무단결근>2일')
                if row.get('cond_3_actual_working_days') == 'FAIL':
                    failed_conditions.append('실제근무일=0')
                if row.get('cond_4_minimum_days') == 'FAIL':
                    failed_conditions.append('최소근무일<12')

                if failed_conditions:
                    print(f"      TYPE-2 {position} {row.get('Full Name', emp_id)}: 조건 미충족 → 0 VND (실패: {', '.join(failed_conditions)})")
            elif stop_working_check:
                incentive = 0
            else:
                # matchingdone TYPE-1 포지션 찾기
                mapped_position = self.get_mapped_type1_position(position_upper, row, type2_mapping)

                # LINE LEADER calculation
                if 'LINE' in position_upper and 'LEADER' in position_upper:
                    # LINE LEADER TYPE-1of LINE LEADER 평균 사용
                    if mapped_position and mapped_position in type1_reference:
                        incentive = type1_reference[mapped_position]
                    else:
                        # defaultvalue 사용
                        incentive = 107360  # position_condition_matrix.json 참조

                # SUPERVISOR 특별 processing - TYPE-1 평균 0 days 때 independent calculation
                elif 'SUPERVISOR' in position_upper:
                    # TYPE-1 SUPERVISOR 평균 checking
                    type1_supervisor_avg = type1_reference.get(position_upper, 0)

                    if type1_supervisor_avg > 0:
                        # TYPE-1 평균 있으면 그대with 사용
                        incentive = type1_supervisor_avg
                    else:
                        # TYPE-1 평균 0면 independent적with calculation
                        incentive = self.calculate_type2_supervisor_independent(position_upper)
                        if incentive > 0:
                            print(f"  → TYPE-2 {position} {row.get('Full Name', 'Unknown')} ({emp_id}): independent calculation → {incentive:,} VND")

                elif mapped_position and mapped_position in type1_reference:
                    incentive = type1_reference[mapped_position]
                elif position_upper in type1_reference:
                    # 직접 matching
                    incentive = type1_reference[position_upper]
                else:
                    incentive = 0
                    print(f"  ⚠️ TYPE-2 '{position}'to for matching failure → 0VND")

            self.month_data.loc[idx, incentive_col] = incentive

    def calculate_type2_group_leaders_final(self):
        """TYPE-2 GROUP LEADER 최종 calculation (STEP 2)"""
        type2_group_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-2') &
            ((self.month_data['QIP POSITION 1ST  NAME'] == 'GROUP LEADER') |
             (self.month_data['QIP POSITION 1ST  NAME'] == 'QA3A'))
        )

        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"

        print(f"    TYPE-2 GROUP LEADER 수: {type2_group_mask.sum()}명")

        # TYPE-1 LINE LEADER 평균 (GROUP LEADER 계산 기준)
        type1_line_leaders = self.month_data[
            (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
            (self.month_data['QIP POSITION 1ST  NAME'] == 'LINE LEADER')
        ]

        # 전체 평균 사용 (0 포함) - 2025-11-30 변경: 수령자만 → 전체 평균
        if len(type1_line_leaders) > 0 and incentive_col in self.month_data.columns:
            type1_line_avg = type1_line_leaders[incentive_col].mean()
        else:
            type1_line_avg = 0

        # TYPE-2 LINE LEADER 평균 calculation (fallback용)
        type2_line_leaders = self.month_data[
            (self.month_data['ROLE TYPE STD'] == 'TYPE-2') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
        ]

        # 전체 평균 사용 (0 포함) - 2025-11-30 변경: 수령자만 → 전체 평균
        if len(type2_line_leaders) > 0:
            type2_line_avg = type2_line_leaders[incentive_col].mean()
        else:
            type2_line_avg = 0

        print(f"    TYPE-1 LINE LEADER 평균 (전체): {type1_line_avg:,.0f} VND")
        print(f"    TYPE-2 LINE LEADER 평균 (전체): {type2_line_avg:,.0f} VND")

        # 각 GROUP LEADER calculation
        for idx, row in self.month_data[type2_group_mask].iterrows():
            emp_id = row.get('Employee No', '')
            name = row.get('Full Name', '')

            # 모든 GROUP LEADER 출력with ĐINH KIM NGOAN include checking
            print(f"    processing in progress: {name} ({emp_id}) - Type: {type(emp_id)}")

            # ĐINH KIM NGOAN 특별 debugging - 다양한 형태with checking
            if str(emp_id) == '617100049' or emp_id == 617100049 or name.startswith('ĐINH KIM NGOAN'):
                print(f"\n    🔍 ĐINH KIM NGOAN 발견! 특별 debugging:")
                print(f"      emp_id: {emp_id} (type: {type(emp_id)})")
                print(f"      name: {name}")
                print(f"      current September_Incentive: {self.month_data.loc[idx, incentive_col]}")
                print(f"      condition1 (cond_1): {row.get('cond_1_attendance_rate', 'PASS')}")
                print(f"      condition2 (cond_2): {row.get('cond_2_unapproved_absence', 'PASS')}")
                print(f"      condition3 (cond_3): {row.get('cond_3_actual_working_days', 'PASS')}")
                print(f"      condition4 (cond_4): {row.get('cond_4_minimum_days', 'PASS')}")

            # attendance condition 체크
            attendance_fail = (
                row.get('cond_1_attendance_rate') == 'FAIL' or
                row.get('cond_2_unapproved_absence') == 'FAIL' or
                row.get('cond_3_actual_working_days') == 'FAIL' or
                row.get('cond_4_minimum_days') == 'FAIL'  # Phase 1: Single Source of Truth
            )

            # debugging용 current value checking
            current_value = self.month_data.loc[idx, incentive_col]

            # ĐINH KIM NGOAN 특별 추적
            if str(emp_id) == '617100049' or emp_id == 617100049 or name.startswith('ĐINH KIM NGOAN'):
                print(f"      [DEBUG] current value(무시done): {current_value}")
                print(f"      [DEBUG] attendance_fail: {attendance_fail}")
                print(f"      [DEBUG] type1_line_avg: {type1_line_avg}")
                print(f"      [DEBUG] type2_line_avg: {type2_line_avg}")

            # 무condition 재calculation - existing value 완전 무시
            if attendance_fail:
                incentive = 0
                if str(emp_id) == '617100049' or emp_id == 617100049 or name.startswith('ĐINH KIM NGOAN'):
                    print(f"      ❌ attendance_fail = True → 0VND")
            elif type1_line_avg > 0:
                # TYPE-1 LINE LEADER 평균 × 2 사용
                incentive = int(type1_line_avg * 2)
                if str(emp_id) == '617100049' or emp_id == 617100049 or name.startswith('ĐINH KIM NGOAN'):
                    print(f"      → TYPE-1 LINE LEADER 평균 × 2: {type1_line_avg} × 2 = {incentive}")
            elif type2_line_avg > 0:
                # TYPE-2 LINE LEADER 평균 × 2 (fallback)
                incentive = int(type2_line_avg * 2)
                if str(emp_id) == '617100049' or emp_id == 617100049 or name.startswith('ĐINH KIM NGOAN'):
                    print(f"      → TYPE-2 LINE LEADER 평균 × 2 (fallback): {type2_line_avg} × 2 = {incentive}")
            else:
                # defaultvalue (LINE LEADER defaultvalue × 2)
                incentive = 107360 * 2
                if str(emp_id) == '617100049' or emp_id == 617100049 or name.startswith('ĐINH KIM NGOAN'):
                    print(f"      → defaultvalue 사용: 107360 × 2 = {incentive}")

            self.month_data.loc[idx, incentive_col] = incentive

            if str(emp_id) == '617100049' or emp_id == 617100049 or name.startswith('ĐINH KIM NGOAN'):
                print(f"      최종 calculationvalue: {incentive}")

            # debugging 정보 - 모든 GROUP LEADER 출력
            print(f"    {name} ({emp_id}):")
            print(f"      condition 충족: {'NO' if attendance_fail else 'YES'}")
            print(f"      TYPE-1 LINE 평균: {type1_line_avg:,.0f}, TYPE-2 LINE 평균: {type2_line_avg:,.0f}")
            print(f"      calculationdone incentive: {incentive:,.0f} VND")

    def calculate_type2_group_leader_independent(self, emp_id: str, subordinate_mapping: Dict[str, List[str]]) -> int:
        """TYPE-2 GROUP LEADER independent incentive calculation
        TYPE-1 평균 0 days 때 independent적with calculation

        calculation 방식:
        1. 전체 TYPE-2 Line Leader들 찾기 (부하employee 관계 무시)
        2. Line Leader들of 평균 incentive calculation
        3. 평균 × 2 apply (TYPE-1 GROUP LEADERand same days한 calculation식)
        """
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"

        # 전체 TYPE-2 Line Leader들 찾기 (부하employee 관계 무시)
        type2_line_leader_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-2') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
        )

        type2_line_leaders = self.month_data[type2_line_leader_mask]

        if type2_line_leaders.empty:
            # TYPE-2 Line Leader 없으면 TYPE-1 Line Leader 평균 사용 (폴백)
            type1_line_leader_mask = (
                (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
            )
            type2_line_leaders = self.month_data[type1_line_leader_mask]

            if type2_line_leaders.empty:
                return 0

        # incentive 받 Line Leader들of 평균 calculation
        receiving_line_leaders = type2_line_leaders[type2_line_leaders[incentive_col] > 0]

        if len(receiving_line_leaders) > 0:
            avg_incentive = receiving_line_leaders[incentive_col].mean()
            # Line Leader 평균of 2배 (TYPE-1 GROUP LEADERand same days한 calculation식)
            result = int(avg_incentive * 2)

            # debugging 정보 출력
            print(f"    → TYPE-2 LINE LEADER {len(receiving_line_leaders)}명 평균: {avg_incentive:,.0f} VND")
            print(f"    → GROUP LEADER incentive (평균 × 2): {result:,.0f} VND")

            return result

        return 0

    def calculate_type2_supervisor_independent(self, supervisor_position: str) -> int:
        """TYPE-2 SUPERVISOR independent incentive calculation
        TYPE-1 SUPERVISOR 평균 0 days 때 independent적with calculation

        calculation 방식:
        1. 전체 TYPE-2 Line Leader들 찾기 (부하employee 관계 무시)
        2. Line Leader들of 평균 incentive calculation
        3. SUPERVISOR 종류to 따른 배수 apply:
           - (V) SUPERVISOR / VICE SUPERVISOR: 평균 × 2.5
           - SUPERVISOR: 평균 × 2.5
        """
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"

        # 전체 TYPE-2 Line Leader들 찾기 (부하employee 관계 무시)
        type2_line_leader_mask = (
            (self.month_data['ROLE TYPE STD'] == 'TYPE-2') &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
            (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
        )

        type2_line_leaders = self.month_data[type2_line_leader_mask]

        if type2_line_leaders.empty:
            # TYPE-2 Line Leader 없으면 TYPE-1 Line Leader 평균 사용 (폴백)
            type1_line_leader_mask = (
                (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LINE', na=False)) &
                (self.month_data['QIP POSITION 1ST  NAME'].str.upper().str.contains('LEADER', na=False))
            )
            type2_line_leaders = self.month_data[type1_line_leader_mask]

            if type2_line_leaders.empty:
                return 0

        # 전체 평균 사용 (0 포함) - 2025-11-30 변경: 수령자만 → 전체 평균
        if len(type2_line_leaders) > 0:
            avg_incentive = type2_line_leaders[incentive_col].mean()

            # SUPERVISOR 배수 apply (2.5배)
            multiplier = 2.5
            result = int(avg_incentive * multiplier)

            # debugging 정보 출력
            print(f"    → TYPE-2 LINE LEADER {len(type2_line_leaders)}명 전체 평균: {avg_incentive:,.0f} VND")
            print(f"    → {supervisor_position} incentive (평균 × {multiplier}): {result:,.0f} VND")

            return result

        return 0

    def load_type2_position_mapping(self) -> Dict:
        """TYPE-2 포지션 matching rule withload"""
        try:
            # 프with젝트 루트from mapping file withload
            import os
            mapping_path = 'config_files/type2_position_mapping.json'
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ TYPE-2 matching rule file not found: {mapping_path}")
        except Exception as e:
            print(f"⚠️ TYPE-2 matching rule withload in progress Error: {e}")
        return {}
    
    def get_mapped_type1_position(self, position: str, row: pd.Series, mapping: Dict) -> str:
        """TYPE-2 포지션to for TYPE-1 matching 포지션 반환"""
        if not mapping:
            return ''
        
        # position_mappings 져오기
        position_mappings = mapping.get('position_mappings', {})
        
        # QA TEAM 특별 processing
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
                # defaultvalue: Assembly Inspector
                return 'ASSEMBLY INSPECTOR'
        
        #  days반 포지션 matching
        if position in position_mappings:
            mapping_info = position_mappings[position]
            if isinstance(mapping_info, dict) and 'mapped_to' in mapping_info:
                return mapping_info['mapped_to'].upper()
        
        return ''
    
    def _create_type1_reference_map(self) -> Dict[str, int]:
        """Type-1 참조 맵 created (수령자만 평균, 반올림 사용)"""
        reference_map = {}
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"

        type1_mask = self.month_data['ROLE TYPE STD'] == 'TYPE-1'

        # 포지션별 평균 calculation (수령자만 평균 - 0 VND 제외)
        for position in self.month_data[type1_mask]['QIP POSITION 1ST  NAME'].unique():
            if pd.notna(position):
                pos_employees = self.month_data[
                    (self.month_data['ROLE TYPE STD'] == 'TYPE-1') &
                    (self.month_data['QIP POSITION 1ST  NAME'] == position)
                ]

                # ✅ POLICY CHANGE (2025-11-25): 수령자만 평균 (0 VND 제외)
                # 인센티브를 받은 직원들만 평균 계산
                receiving_employees = pos_employees[pos_employees[incentive_col] > 0]

                if len(receiving_employees) > 0:
                    avg_incentive = round(receiving_employees[incentive_col].mean())
                    reference_map[position.upper()] = avg_incentive
                else:
                    # 수령자가 한 명도 없으면 0
                    reference_map[position.upper()] = 0

        return reference_map
    
    def calculate_type3_incentive(self):
        """Type-3 incentive calculation"""
        print("\n📊 TYPE-3 incentive calculation...")
        
        type3_mask = self.month_data['ROLE TYPE STD'] == 'TYPE-3'
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        # Type-3 incentive 없음
        for idx in self.month_data[type3_mask].index:
            self.month_data.loc[idx, incentive_col] = 0
        
        print(f"  → Type-3 employeeare incentive 받지 않습니다.")
    
    def apply_talent_pool_bonus(self):
        """QIP Talent Pool 보너스 apply - JSON configuration based"""
        print("\n🌟 QIP Talent Pool Applying bonuses...")
        
        # Talent Pool JSON file withload
        talent_pool_file = Path(self.base_path) / 'config_files' / 'qip_talent_pool.json'
        
        if not talent_pool_file.exists():
            print("  → Talent Pool configuration file not found. Skipping.")
            return
        
        try:
            with open(talent_pool_file, 'r', encoding='utf-8') as f:
                talent_pool_config = json.load(f)
            
            # current month checking
            current_year = self.config.year
            current_month = self.config.month.number
            
            # Talent Pool 멤버 processing
            members = talent_pool_config.get('talent_pool', {}).get('members', [])
            settings = talent_pool_config.get('talent_pool', {}).get('settings', {})
            
            applied_count = 0
            total_bonus = 0
            
            incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
            
            # 새with운 column 추 (없으면)
            if 'Talent_Pool_Bonus' not in self.month_data.columns:
                self.month_data['Talent_Pool_Bonus'] = 0
            if 'Talent_Pool_Member' not in self.month_data.columns:
                self.month_data['Talent_Pool_Member'] = 'N'
            
            for member in members:
                # 상태 checking
                if member.get('status') != 'active':
                    continue
                
                # 기간 checking
                start_date = pd.to_datetime(member.get('start_date'))
                end_date = pd.to_datetime(member.get('end_date'))
                current_date = pd.to_datetime(f"{current_year}-{current_month:02d}-01")
                
                if not (start_date <= current_date <= end_date):
                    continue
                
                # employee 찾기 (여러 column 체크)
                emp_id = str(member.get('employee_id'))
                
                # Employee No, Personnel Number_manpower, Personnel Number in progress 하나라also matching되지 checking
                mask = (
                    (self.month_data['Employee No'].astype(str) == emp_id) |
                    (self.month_data.get('Personnel Number_manpower', pd.Series()).astype(str) == emp_id) |
                    (self.month_data.get('Personnel Number', pd.Series()).astype(str) == emp_id)
                )
                
                matching_rows = self.month_data[mask]
                
                if len(matching_rows) == 0:
                    print(f"  ⚠️ employee {emp_id} 찾 수 없습니다.")
                    continue
                
                # 보너스 apply
                for idx in matching_rows.index:
                    # 퇴사자 체크
                    if 'Stop working Date' in self.month_data.columns:
                        stop_date = pd.to_datetime(self.month_data.loc[idx, 'Stop working Date'], errors='coerce')
                        if pd.notna(stop_date) and stop_date < current_date:
                            print(f"  → employee {emp_id} 퇴사했습니다. 스킵합니다.")
                            continue
                    
                    bonus_amount = member.get('monthly_bonus', 0)
                    
                    # Talent Pool 보너스 columnto saved
                    self.month_data.loc[idx, 'Talent_Pool_Bonus'] = bonus_amount
                    self.month_data.loc[idx, 'Talent_Pool_Member'] = 'Y'
                    
                    # existing incentive 져오기
                    current_incentive = self.month_data.loc[idx, incentive_col]
                    if pd.isna(current_incentive):
                        current_incentive = 0

                    # existing incentiveand 합산 (settingsto 따라)
                    if settings.get('stack_with_regular', True):
                        # existing incentive + 보너스
                        final_incentive = current_incentive + bonus_amount
                        self.month_data.loc[idx, incentive_col] = final_incentive

                        emp_name = self.month_data.loc[idx, 'Full Name']
                        print(f"  ✅ {emp_name} ({emp_id}): +{bonus_amount:,} VND (Talent Pool 보너스)")
                        print(f"     → existing: {current_incentive:,.0f} VND → 최종: {final_incentive:,.0f} VND")
                    else:
                        # 보너스only 별also 지급 (existing incentive 유지하고 보너스only 추)
                        # 주of: 경우toalso existing incentive 유지되어야 함
                        final_incentive = current_incentive + bonus_amount
                        self.month_data.loc[idx, incentive_col] = final_incentive
                        emp_name = self.month_data.loc[idx, 'Full Name']
                        print(f"  ✅ {emp_name} ({emp_id}): existing {current_incentive:,.0f} + 보너스 {bonus_amount:,.0f} = {final_incentive:,.0f} VND")
                    
                    applied_count += 1
                    total_bonus += bonus_amount
            
            if applied_count > 0:
                print(f"\n📊 Talent Pool 보너스 apply completed:")
                print(f"  • 적용 인원: {applied_count}명")
                print(f"  • 총 보너스: {total_bonus:,} VND")
            else:
                print("  → No applicable employees for this month.")
                
        except Exception as e:
            print(f"  ❌ Talent Pool Applying bonuses Error: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_summary(self):
        """계산 결과 요약"""
        print(f"\n{'='*60}")
        print(f"📊 {self.config.get_month_str('korean')} QIP incentive 계산 결과 요약")
        print('='*60)
        
        incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
        
        # 공통 필터 사용하여 Filtering active employees
        print("\n[Using Common Module] Filtering active employees...")
        active_employees = EmployeeFilter.filter_active_employees(
            self.month_data, 
            self.config.month.number, 
            self.config.year
        )
        
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
                
                # position별 상세 통계
                print(f"\n    📊 {role_type} position별 상세:")
                position_col = 'QIP POSITION 1ST  NAME'
                if position_col in type_data.columns:
                    positions = type_data.groupby(position_col).agg({
                        incentive_col: ['count', lambda x: (x > 0).sum(), 'sum', 
                                       lambda x: x[x > 0].mean() if (x > 0).sum() > 0 else 0]
                    }).round(0)
                    positions.columns = ['총VND', '수령인VND', '총지급액', '평균지급액']
                    positions['미수령인VND'] = positions['총VND'] - positions['수령인VND']
                    positions['수령률'] = (positions['수령인VND'] / positions['총VND'] * 100).round(1)
                    
                    # 수령인VND 많은 순with 정렬
                    positions = positions.sort_values('수령인VND', ascending=False)
                    
                    for position, row in positions.head(10).iterrows():
                        if row['총VND'] > 0:
                            print(f"      • {position}:")
                            print(f"        - 총VND: {int(row['총VND'])}명, 수령: {int(row['수령인VND'])}명, 미수령: {int(row['미수령인VND'])}명")
                            print(f"        - 수령률: {row['수령률']}%, 총액: {row['총지급액']:,.0f} VND")
                            if row['수령인VND'] > 0:
                                print(f"        - 평균: {row['평균지급액']:,.0f} VND")
    
    def add_continuous_months_tracking(self):
        """consecutive months 추적 column 추 (Expected_Months)"""
        print("\n📊 연속 개월 추가 tracking columns...")

        # previous month consecutive monthsand current month expected month calculation
        previous_continuous = []
        current_expected = []

        for idx, row in self.month_data.iterrows():
            emp_id = str(row.get('Employee No', '')).zfill(9)
            position = str(row.get('QIP POSITION 1ST  NAME', '')).upper()
            role_type = row.get('ROLE TYPE STD', '')

            # TYPE-1 ASSEMBLY INSPECTOR, MODEL MASTER, AUDITOR & TRAINERonly 해당
            if role_type == 'TYPE-1' and any(x in position for x in ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR', 'TRAINING']):
                # JSON 파일에서 checking
                prev_months = 0
                expected_months = 0

                try:
                    json_path = Path('config_files/assembly_inspector_continuous_months.json')
                    if json_path.exists():
                        import json
                        with open(json_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)

                        if emp_id in config.get('employees', {}):
                            emp_data = config['employees'][emp_id]
                            prev_months = emp_data.get('july_continuous_months', 0)
                            expected_months = emp_data.get('august_expected_months', 0)
                except:
                    pass

                # incentive 수령 여부with 실제 consecutive months checking
                current_incentive = row.get(f'{self.config.get_month_str("capital")}_Incentive', 0)
                if current_incentive > 0 and expected_months == 0:
                    # JSONto 없지only incentive 받았다면 condition 충족with 간주
                    expected_months = 1

                previous_continuous.append(prev_months)
                current_expected.append(expected_months)
            else:
                # 해당 없 position
                previous_continuous.append('')
                current_expected.append('')

        # next month expected month수 calculation
        next_month_expected = []
        for idx, row in self.month_data.iterrows():
            emp_id = str(row.get('Employee No', '')).zfill(9)
            position = str(row.get('QIP POSITION 1ST  NAME', '')).upper()
            role_type = row.get('ROLE TYPE STD', '')

            # TYPE-1 ASSEMBLY INSPECTOR, MODEL MASTER, AUDITOR & TRAINERonly 해당
            if role_type == 'TYPE-1' and any(x in position for x in ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR', 'TRAINING']):
                # current incentive 수령 여부 checking
                current_incentive = row.get(f'{self.config.get_month_str("capital")}_Incentive', 0)
                # 변수employees 충돌 수정: current_expected_valuewith 변경
                current_expected_value = current_expected[idx] if idx < len(current_expected) and isinstance(current_expected[idx], int) else 0

                if current_incentive > 0 and current_expected_value > 0:
                    # condition 충족 - next month은 +1
                    next_expected = current_expected_value + 1
                    # 최대 12-monthwith 제한
                    next_expected = min(next_expected, 12)
                else:
                    # condition 미충족 - next month은 1-monthfrom started
                    next_expected = 1

                next_month_expected.append(next_expected)
            else:
                # 해당 없 position
                next_month_expected.append('')

        # column 추
        self.month_data['Previous_Continuous_Months'] = previous_continuous
        self.month_data['Current_Expected_Months'] = current_expected
        # Continuous_Months 미 각 TYPE-1 calculation 함수from 정확히 configurationdone
        # 여기서 덮어쓰면 안done!
        # self.month_data['Continuous_Months'] = current_expected  # 줄 문제였음!

        # Continuous_Months column 없 경우toonly 초기화
        if 'Continuous_Months' not in self.month_data.columns:
            self.month_data['Continuous_Months'] = 0

        self.month_data['Next_Month_Expected'] = next_month_expected

        print(f"✅ consecutive months 추적 column 추가 완료 (Next_Month_Expected include)")

    def calculate_approved_leave_days(self, emp_no: str) -> int:
        """employeeof 승인done 휴  days수 calculation (AR1 아닌 모든 Reason Description)"""
        try:
            # attendance file 경with 져오기
            attendance_path = self.config.get_file_path('attendance')
            if not os.path.exists(attendance_path):
                return 0

            # attendance file 읽기
            att_df = pd.read_csv(attendance_path)

            # employee 번호 표준화 (앞of 0 제거)
            emp_no_str = str(emp_no).lstrip('0')

            # 해당 employeeof attendance record 필터링
            emp_attendance = att_df[att_df['ID No'].astype(str).str.lstrip('0') == emp_no_str]

            # AR1 아닌 사유only 승인휴with 집계
            # AR1 = 무단결근, 나머지 = 승인휴 (출산휴, 연차, 병, 출장 etc.)
            approved_leave = emp_attendance[
                emp_attendance['Reason Description'].notna() &
                ~emp_attendance['Reason Description'].str.startswith('AR1', na=False)
            ]

            return len(approved_leave)

        except Exception as e:
            # to러 발생 시 0 반환 (with그 출력하지 않음 - 조용히 processing)
            return 0

    def add_condition_evaluation_to_excel(self):
        """10 conditions 평 결and Excelto 추"""
        print("\n📊 10items Adding condition evaluation results to Excel...")

        if not POSITION_CONDITION_MATRIX:
            print("⚠️ Position condition matrix 찾 수 없습니다.")
            return

        # first attendance_rate column 없으면 calculation하여 추
        if '출근율_Attendance_Rate_Percent' not in self.month_data.columns:
            print("  → attendance_rate column Calculating (승인휴 반영)...")
            self.month_data['출근율_Attendance_Rate_Percent'] = 0.0
            self.month_data['Approved Leave Days'] = 0
            self.month_data['결근율_Absence_Rate_Percent'] = 0.0

            for idx in self.month_data.index:
                emp_no = self.month_data.loc[idx, 'Employee No']
                total_days = self.month_data.loc[idx, 'Total Working Days'] if 'Total Working Days' in self.month_data.columns else 27
                actual_days = self.month_data.loc[idx, 'Actual Working Days'] if 'Actual Working Days' in self.month_data.columns else 0

                # 승인휴  days수 calculation
                approved_leave_days = self.calculate_approved_leave_days(emp_no)
                self.month_data.loc[idx, 'Approved Leave Days'] = approved_leave_days

                # ✅ POLICY ALIGNED (Fixed 2025-11-29): 승인휴가는 결근에서 제외
                # 정책 공식:
                #   결근일 = 총 근무일 - 실제 근무일 - 승인휴가
                #   결근율 = 결근일 / 총 근무일 × 100
                #   출근율 = 100 - 결근율
                # 예시: 총 18일, 실제 14일, 승인휴가 2일 → 결근 2일 → 출근율 88.9%
                if total_days > 0:
                    # 결근일 = 총 근무일 - 실제 근무일 - 승인휴가 (무단결근만 카운트)
                    absence_days = total_days - actual_days - approved_leave_days
                    absence_days = max(0, absence_days)  # 음수 방지

                    # 결근율 = 결근일 / 총 근무일 × 100
                    absence_rate = (absence_days / total_days) * 100

                    # 출근율 = 100 - 결근율 (승인휴가는 출근으로 인정)
                    attendance_rate = 100 - absence_rate

                    # 100% 초과 방지
                    attendance_rate = min(100, max(0, attendance_rate))
                else:
                    attendance_rate = 0
                    absence_rate = 0
                    absence_days = 0
                    absence_days = 0

                self.month_data.loc[idx, '출근율_Attendance_Rate_Percent'] = attendance_rate
                self.month_data.loc[idx, '결근율_Absence_Rate_Percent'] = absence_rate

                # 레거시 컬럼 삭제:                 # attendancy condition 3also updated (absence rate > 12%)
                # 레거시 컬럼 삭제: self.month_data.loc[idx, 'attendancy condition 3 - absent % is over 12%'] = 'yes' if absence_rate > 12 else 'no'

            print(f"  ✅ 승인휴 반영 completed - 평균 승인휴: {self.month_data['Approved Leave Days'].mean():.1f} days")

        # 조건 평가 컬럼 초기화 (object dtype으로 설정하여 'N/A' 문자열 저장 가능하도록)
        condition_columns = [
            'cond_1_attendance_rate', 'cond_2_unapproved_absence', 'cond_3_actual_working_days',
            'cond_4_minimum_days', 'cond_5_aql_personal_failure', 'cond_6_aql_continuous',
            'cond_7_aql_team_area', 'cond_8_area_reject', 'cond_9_5prs_pass_rate', 'cond_10_5prs_inspection_qty'
        ]
        for col in condition_columns:
            self.month_data[col] = None  # Initialize as None to create object dtype
            self.month_data[col] = self.month_data[col].astype('object')

        # Interim vs Final report 판정 (조건 1&4 예외 처리용)
        from datetime import datetime
        current_date = datetime.now()
        is_current_month = (current_date.year == self.config.year and
                           current_date.month == self.config.month.number)

        # 각 employee별with 10 conditions 평
        for idx in self.month_data.index:
            emp_type = self.month_data.loc[idx, 'ROLE TYPE STD']
            position = self.month_data.loc[idx, 'QIP POSITION 1ST  NAME']
            position_code = self.month_data.loc[idx, 'FINAL QIP POSITION NAME CODE']

            # Check if this is QC Assembly Inspector type
            is_qc_assembly = False
            if pd.notna(position):
                position_upper = str(position).upper()
                is_qc_assembly = (
                    ('QC' in position_upper and 'ASSEMBLY' in position_upper and 'INSPECTOR' in position_upper) or
                    ('ASSEMBLY' in position_upper and 'INSPECTOR' in position_upper)
                )
            if pd.notna(position_code):
                position_code_upper = str(position_code).upper()
                if position_code_upper.startswith('A') and len(position_code_upper) >= 2 and position_code_upper[1].isdigit():
                    is_qc_assembly = True  # A1-A5 codes

            # Determine if this is an interim report based on position type
            if is_current_month:
                cutoff_day = 15 if is_qc_assembly else 20
                is_interim_report = current_date.day < cutoff_day

                # Log only for QC Assembly Inspector types
                if is_interim_report and is_qc_assembly:
                    print(f"  ℹ️ QC Assembly Inspector Interim report: {self.month_data.loc[idx, 'Full Name']} (day {current_date.day} < {cutoff_day}) - 조건 1&4 예외 처리")
            else:
                # Past month: always apply full conditions
                is_interim_report = False

            # position_condition_matrix.jsonfrom 해당 positionof condition configuration 져오기
            pos_config = get_position_config_from_matrix(emp_type, position)

            if not pos_config:
                # defaultvalue configuration (default 사용)
                type_matrix = POSITION_CONDITION_MATRIX.get('position_matrix', {}).get(emp_type, {})
                pos_config = type_matrix.get('default', {})

            applicable_conditions = pos_config.get('applicable_conditions', [])

            # 10 conditions 각각 평
            # condition 1: attendance율 >= 88%
            attendance_rate = self.month_data.loc[idx, '출근율_Attendance_Rate_Percent'] if '출근율_Attendance_Rate_Percent' in self.month_data.columns else 0

            # Expected working days 확인 (Total - Approved Leave)
            # 근무해야 할 날이 0 이하면 출근율 조건 평가 불가 (예: 전체 기간 출산휴가)
            total_days = self.month_data.loc[idx, 'Total Working Days'] if 'Total Working Days' in self.month_data.columns else 0
            approved_leave = self.month_data.loc[idx, 'Approved Leave Days'] if 'Approved Leave Days' in self.month_data.columns else 0
            expected_working_days = total_days - approved_leave

            # Interim report (20일 이전)에는 조건 1 예외 처리
            if is_interim_report and 1 in applicable_conditions:
                # Interim report: 조건 1을 NOT_APPLICABLE로 처리 (중간 보고서에서는 출근율 조건 완화)
                cond_1_result = 'NOT_APPLICABLE'
                cond_1_applicable = 'NOT_APPLICABLE'
                cond_1_threshold = 'N/A (Interim)'
            elif expected_working_days <= 0:
                # 근무해야 할 날이 없으므로 출근율 조건 평가 불가
                cond_1_result = 'NOT_APPLICABLE'
                cond_1_applicable = 'Y' if 1 in applicable_conditions else 'NOT_APPLICABLE'
                cond_1_threshold = 88
            else:
                cond_1_result = 'PASS' if attendance_rate >= 88 else 'FAIL'
                cond_1_applicable = 'Y' if 1 in applicable_conditions else 'NOT_APPLICABLE'
                cond_1_threshold = 88

            # 'N/A' 대신 'NOT_APPLICABLE' 사용 (pandas가 'N/A'를 NaN으로 변환하는 문제 해결)
            self.month_data.loc[idx, 'cond_1_attendance_rate'] = cond_1_applicable if cond_1_applicable == 'NOT_APPLICABLE' else cond_1_result
            self.month_data.loc[idx, 'cond_1_value'] = attendance_rate
            self.month_data.loc[idx, 'cond_1_threshold'] = cond_1_threshold

            # condition 2: 무단결근 <= 2 days
            unapproved_absence = self.month_data.loc[idx, 'Unapproved Absences'] if 'Unapproved Absences' in self.month_data.columns else 0

            # NaN 처리 추가 (출결 데이터 없는 신입사원)
            if pd.isna(unapproved_absence):
                cond_2_result = 'NOT_APPLICABLE'  # 출결 데이터 없음
            else:
                cond_2_result = 'PASS' if unapproved_absence <= 2 else 'FAIL'

            cond_2_applicable = 'Y' if 2 in applicable_conditions else 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_2_unapproved_absence'] = cond_2_applicable if cond_2_applicable == 'NOT_APPLICABLE' else cond_2_result
            self.month_data.loc[idx, 'cond_2_value'] = unapproved_absence
            self.month_data.loc[idx, 'cond_2_threshold'] = 2

            # condition 3: 실근무 days > 0
            actual_working_days = self.month_data.loc[idx, 'Actual Working Days'] if 'Actual Working Days' in self.month_data.columns else 0
            cond_3_result = 'PASS' if actual_working_days > 0 else 'FAIL'
            cond_3_applicable = 'Y' if 3 in applicable_conditions else 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_3_actual_working_days'] = cond_3_applicable if cond_3_applicable == 'NOT_APPLICABLE' else cond_3_result
            self.month_data.loc[idx, 'cond_3_value'] = actual_working_days
            self.month_data.loc[idx, 'cond_3_threshold'] = 0

            # condition 4: minimum근무 days >= 12
            # Interim report (20일 이전)에는 조건 4 예외 처리
            if is_interim_report and 4 in applicable_conditions:
                # Interim report: 조건 4를 NOT_APPLICABLE로 처리 (다른 조건만으로 100% 평가)
                cond_4_result = 'NOT_APPLICABLE'
                cond_4_applicable = 'NOT_APPLICABLE'
            else:
                # Final report 또는 조건 미적용 position
                cond_4_result = 'PASS' if actual_working_days >= 12 else 'FAIL'
                cond_4_applicable = 'Y' if 4 in applicable_conditions else 'NOT_APPLICABLE'

            self.month_data.loc[idx, 'cond_4_minimum_days'] = cond_4_applicable if cond_4_applicable == 'NOT_APPLICABLE' else cond_4_result
            self.month_data.loc[idx, 'cond_4_value'] = actual_working_days
            self.month_data.loc[idx, 'cond_4_threshold'] = 12 if not is_interim_report else 'N/A (Interim)'

            # condition 5: items인 AQL 당month failure = 0
            aql_col = f"{self.config.get_month_str('capital')} AQL Failures"
            aql_fail = self.month_data.loc[idx, aql_col] if aql_col in self.month_data.columns else 0
            cond_5_result = 'PASS' if aql_fail == 0 else 'FAIL'
            cond_5_applicable = 'Y' if 5 in applicable_conditions else 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_5_aql_personal_failure'] = cond_5_applicable if cond_5_applicable == 'NOT_APPLICABLE' else cond_5_result
            self.month_data.loc[idx, 'cond_5_value'] = aql_fail
            self.month_data.loc[idx, 'cond_5_threshold'] = 0

            # condition 6: 3-month consecutive AQL failure 없음
            continuous_fail = self.month_data.loc[idx, 'Continuous_FAIL'] if 'Continuous_FAIL' in self.month_data.columns else 'NO'
            cond_6_result = 'PASS' if continuous_fail != 'YES' else 'FAIL'
            cond_6_applicable = 'Y' if 6 in applicable_conditions else 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_6_aql_continuous'] = cond_6_applicable if cond_6_applicable == 'NOT_APPLICABLE' else cond_6_result
            self.month_data.loc[idx, 'cond_6_value'] = continuous_fail
            self.month_data.loc[idx, 'cond_6_threshold'] = 'NO'

            # condition 7: 팀/area AQL (3-month consecutive failure 없음)
            # condition은 LINE LEADER나 특정 포지션toonly apply
            team_aql_fail = False  # defaultvalue
            if 7 in applicable_conditions:
                # LINE LEADERof 경우 부하employee in progress 3-month consecutive failures checking
                emp_id = str(self.month_data.loc[idx, 'Employee No'])
                position_value = self.month_data.loc[idx, 'QIP POSITION 1ST  NAME']
                position = str(position_value).upper() if pd.notna(position_value) else ''

                if 'LINE' in position and 'LEADER' in position:
                    # subordinate_mapping 있으면 사용, 없으면 created
                    if not hasattr(self, 'subordinate_mapping_cache'):
                        subordinate_mapping = {}
                        for _, row_inner in self.month_data.iterrows():
                            manager_id_raw = row_inner.get('MST direct boss name', '')
                            # Convert to int if it's a float to match Employee No format
                            if pd.notna(manager_id_raw):
                                try:
                                    manager_id = str(int(manager_id_raw))
                                except (ValueError, TypeError):
                                    manager_id = str(manager_id_raw)
                            else:
                                manager_id = ''

                            sub_id = str(row_inner['Employee No'])
                            if manager_id and sub_id:
                                if manager_id not in subordinate_mapping:
                                    subordinate_mapping[manager_id] = []
                                subordinate_mapping[manager_id].append(sub_id)
                        self.subordinate_mapping_cache = subordinate_mapping

                    # 부하employee in progress consecutive failures checking
                    if emp_id in self.subordinate_mapping_cache:
                        for sub_id in self.subordinate_mapping_cache[emp_id]:
                            # FIX: Convert both sides to string for type-safe comparison
                            # Employee No might be int64 after save_results() numeric conversion
                            sub_data = self.month_data[self.month_data['Employee No'].astype(str) == str(sub_id)]
                            if not sub_data.empty:
                                # FIX: Check if Continuous_FAIL starts with 'YES' to match 'YES', 'YES_3MONTHS', 'YES_2MONTHS_AUG_SEP'
                                continuous_fail_value = str(sub_data.iloc[0].get('Continuous_FAIL', 'NO'))
                                if continuous_fail_value.startswith('YES'):
                                    team_aql_fail = True
                                    break

                # AUDIT & TRAINING TEAM의 경우 담당 구역 직원 중 3개월 연속 실패 확인
                # MODEL MASTER는 전체 구역 담당이므로 제외
                elif ('AUDIT' in position or 'TRAINING' in position) and 'MODEL MASTER' not in position:
                    # auditor_trainer_area_mapping.json 로드
                    area_mapping_file = Path('config_files') / 'auditor_trainer_area_mapping.json'
                    if area_mapping_file.exists():
                        with open(area_mapping_file, 'r', encoding='utf-8') as f:
                            area_mapping = json.load(f)

                        # 담당 구역 직원 가져오기
                        area_employees = self.get_auditor_area_employees(emp_id, area_mapping)

                        # 담당 구역 직원 중 3개월 연속 실패자 확인
                        for area_emp_id in area_employees:
                            area_emp_data = self.month_data[self.month_data['Employee No'].astype(str) == str(area_emp_id)]
                            if not area_emp_data.empty:
                                continuous_fail_value = str(area_emp_data.iloc[0].get('Continuous_FAIL', 'NO'))
                                if continuous_fail_value.startswith('YES'):
                                    team_aql_fail = True
                                    break

                cond_7_result = 'PASS' if not team_aql_fail else 'FAIL'
                self.month_data.loc[idx, 'cond_7_aql_team_area'] = cond_7_result
                self.month_data.loc[idx, 'cond_7_value'] = 'YES' if team_aql_fail else 'NO'
            else:
                self.month_data.loc[idx, 'cond_7_aql_team_area'] = 'NOT_APPLICABLE'
                self.month_data.loc[idx, 'cond_7_value'] = 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_7_threshold'] = 'NO'

            # condition 8: in chargearea reject < 3%
            if 8 in applicable_conditions:
                reject_rate = self.month_data.loc[idx, 'Area_Reject_Rate'] if 'Area_Reject_Rate' in self.month_data.columns else 0
                # PASS = reject rate < 3%, FAIL = reject rate >= 3%
                cond_8_result = 'PASS' if reject_rate < 3 else 'FAIL'
                self.month_data.loc[idx, 'cond_8_area_reject'] = cond_8_result
                self.month_data.loc[idx, 'cond_8_value'] = reject_rate
            else:
                self.month_data.loc[idx, 'cond_8_area_reject'] = 'NOT_APPLICABLE'
                self.month_data.loc[idx, 'cond_8_value'] = 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_8_threshold'] = 3

            # condition 9: 5PRS passed율 >= 95%
            prs_pass_rate = self.month_data.loc[idx, '5PRS_Pass_Rate'] if '5PRS_Pass_Rate' in self.month_data.columns else 0
            cond_9_result = 'PASS' if prs_pass_rate >= 95 else 'FAIL'
            cond_9_applicable = 'Y' if 9 in applicable_conditions else 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_9_5prs_pass_rate'] = cond_9_applicable if cond_9_applicable == 'NOT_APPLICABLE' else cond_9_result
            self.month_data.loc[idx, 'cond_9_value'] = prs_pass_rate
            self.month_data.loc[idx, 'cond_9_threshold'] = 95

            # condition 10: 5PRS inspection량 >= 100
            prs_qty = self.month_data.loc[idx, '5PRS_Inspection_Qty'] if '5PRS_Inspection_Qty' in self.month_data.columns else 0
            cond_10_result = 'PASS' if prs_qty >= 100 else 'FAIL'
            cond_10_applicable = 'Y' if 10 in applicable_conditions else 'NOT_APPLICABLE'
            self.month_data.loc[idx, 'cond_10_5prs_inspection_qty'] = cond_10_applicable if cond_10_applicable == 'NOT_APPLICABLE' else cond_10_result
            self.month_data.loc[idx, 'cond_10_value'] = prs_qty
            self.month_data.loc[idx, 'cond_10_threshold'] = 100

            # 전체 condition 충족 비율 calculation
            applicable_count = 0
            passed_count = 0
            for i in range(1, 11):
                cond_col = f'cond_{i}_' + ['attendance_rate', 'unapproved_absence', 'actual_working_days', 'minimum_days',
                                           'aql_personal_failure', 'aql_continuous', 'aql_team_area', 'area_reject',
                                           '5prs_pass_rate', '5prs_inspection_qty'][i-1]
                if cond_col in self.month_data.columns:
                    result = self.month_data.loc[idx, cond_col]
                    # NOT_APPLICABLE인 조건은 제외 (interim report 조건 4 등)
                    if result not in ['N/A', 'NOT_APPLICABLE', None] and pd.notna(result):
                        applicable_count += 1
                        if result == 'PASS':
                            passed_count += 1

            self.month_data.loc[idx, 'conditions_applicable'] = applicable_count
            self.month_data.loc[idx, 'conditions_passed'] = passed_count
            self.month_data.loc[idx, 'conditions_pass_rate'] = (passed_count / applicable_count * 100) if applicable_count > 0 else 0

        print(f"✅ 10 conditions 평 결and 추가 완료")

    def add_aql_statistics_to_excel(self):
        """AQL 통계 정보 Excelto 추"""
        print("\n📊 AQL Adding statistics to Excel...")

        # AQL 통계 AQL 파일에서 직접 calculation
        aql_stats = {}

        # AQL file 경with
        month_upper = self.config.month.full_name.upper()
        aql_file = f"input_files/AQL history/1.HSRG AQL REPORT-{month_upper}.{self.config.year}.csv"

        if os.path.exists(aql_file):
            print(f"  → AQL 파일에서 직접 통계 계산: {aql_file}")
            aql_df = pd.read_csv(aql_file)

            # 모든 PO TYPE include (FAIL은 주with FAIL POto 있음)
            for emp_no in aql_df['EMPLOYEE NO'].unique():
                emp_tests = aql_df[aql_df['EMPLOYEE NO'] == emp_no]
                total = len(emp_tests)
                pass_count = (emp_tests['RESULT'] == 'PASS').sum()
                fail_count = (emp_tests['RESULT'] == 'FAIL').sum()

                aql_stats[str(emp_no)] = {
                    'total': int(total),
                    'pass': int(pass_count),
                    'fail': int(fail_count)
                }

            print(f"  → AQL 파일에서 {len(aql_stats)}명 검사자 통계 생성 완료")
        else:
            print(f"  ⚠️ AQL file not found: {aql_file}")
            print("  → Using default values based on September AQL Failures column")

        # 새with운 column 추
        self.month_data['AQL_Total_Tests'] = 0
        self.month_data['AQL_Pass_Count'] = 0
        self.month_data['AQL_Fail_Percent'] = 0.0

        # 각 employee별with AQL 통계 추
        for idx in self.month_data.index:
            emp_no = str(self.month_data.loc[idx, 'Employee No'])

            if emp_no in aql_stats:
                stats = aql_stats[emp_no]
                total_tests = stats.get('total', 0)
                pass_count = stats.get('pass', 0)
                fail_count = stats.get('fail', 0)

                self.month_data.loc[idx, 'AQL_Total_Tests'] = total_tests
                self.month_data.loc[idx, 'AQL_Pass_Count'] = pass_count

                # FAIL % calculation
                if total_tests > 0:
                    fail_percent = (fail_count / total_tests) * 100
                else:
                    fail_percent = 0.0

                self.month_data.loc[idx, 'AQL_Fail_Percent'] = round(fail_percent, 1)
            # else 블록 제거 - AQL fileto 없 employee은 0with 유지 (inspection 하지 않은 employee)

        # 통계 출력
        aql_with_data = (self.month_data['AQL_Total_Tests'] > 0).sum()
        aql_with_fail = (self.month_data['AQL_Total_Tests'] > 0) & (self.month_data['AQL_Pass_Count'] < self.month_data['AQL_Total_Tests'])
        aql_fail_count = aql_with_fail.sum()

        print(f"  → AQL 통계 추가 완료:")
        print(f"     • AQL inspection data 있음: {aql_with_data}명")
        print(f"     • FAIL 1cases 상: {aql_fail_count}명")
        print(f"     • PASSonly: {aql_with_data - aql_fail_count}명")

    def save_results(self):
        """결and saved"""
        print(f"\n💾 결과 파일 saved in progress...")

        try:
            # output_files 폴더 created
            import os
            import shutil
            import json
            output_dir = "output_files"
            os.makedirs(output_dir, exist_ok=True)
            
            # previous month incentive data 병합
            if self.config.previous_months:
                prev_month = self.config.previous_months[-1]
                # ✅ Use config path instead of hardcoded path (2025-10-04)
                prev_file_path = self.config.file_paths.get('previous_incentive',
                                                             f"input_files/{self.config.year}year {prev_month.number}month incentive 지급 세부 정보.csv")

                if os.path.exists(prev_file_path):
                    try:
                        prev_incentive_data = pd.read_csv(prev_file_path, encoding='utf-8-sig')
                        
                        # Employee No 숫자with 변환하여 mapping
                        prev_incentive_data['Employee No'] = pd.to_numeric(prev_incentive_data['Employee No'], errors='coerce')
                        self.month_data['Employee No'] = pd.to_numeric(self.month_data['Employee No'], errors='coerce')

                        # previous month incentive column 찾기 (우선순위: month 름 based → Final Incentive amount)
                        prev_incentive_col = None
                        possible_cols = [
                            f'{prev_month.full_name.capitalize()}_Incentive',
                            f'{prev_month.full_name.upper()}_Incentive',
                            f'{prev_month.full_name.lower()}_incentive',
                            'Final Incentive amount',
                            f'{prev_month.korean_name} incentive'
                        ]

                        for col in possible_cols:
                            if col in prev_incentive_data.columns:
                                prev_incentive_col = col
                                print(f"  → previous month incentive column 발견: {col}")
                                break

                        if prev_incentive_col:
                            prev_incentive_map = prev_incentive_data.set_index('Employee No')[prev_incentive_col].to_dict()
                            self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)

                            # mapping 결and checking
                            mapped_count = (self.month_data['Previous_Incentive'] > 0).sum()
                            print(f"  → {prev_month.korean_name} incentive mapping completed: {mapped_count}/{len(self.month_data)} employees")

                            # 샘플 data checking
                            sample_data = self.month_data[self.month_data['Previous_Incentive'] > 0].head(3)
                            if not sample_data.empty:
                                print(f"  → 샘플 data:")
                                for idx, row in sample_data.iterrows():
                                    print(f"    - {row['Employee No']}: {row['Previous_Incentive']:,.0f} VND")
                        elif f'{prev_month.full_name.capitalize()}_Incentive' in prev_incentive_data.columns:
                            col_name = f'{prev_month.full_name.capitalize()}_Incentive'
                            prev_incentive_map = prev_incentive_data.set_index('Employee No')[col_name].to_dict()
                            self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)
                        else:
                            self.month_data['Previous_Incentive'] = 0
                    except Exception as e:
                        print(f"  ⚠️ {prev_month.korean_name} incentive data load failed: {e}")
                        self.month_data['Previous_Incentive'] = 0
                else:
                    self.month_data['Previous_Incentive'] = 0
            else:
                self.month_data['Previous_Incentive'] = 0
            
            incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
            
            # Final Incentive amount column current month incentive valuewith configuration
            self.month_data['Final Incentive amount'] = self.month_data[incentive_col].copy()

            # Single Source of Truth 위한 column 추
            if self.config.month.number == 8 and self.config.year == 2025:
                # 8Month: July_Incentive column 유지 (미 load_july_incentive_datafrom 추done)
                pass
            else:
                # September 후: Previous_Month_Incentive column 추
                if 'Previous_Incentive' in self.month_data.columns:
                    self.month_data['Previous_Month_Incentive'] = self.month_data['Previous_Incentive']

            # consecutive months 추적 column 추 (Next_Month_Expected include)
            self.add_continuous_months_tracking()

            # Next_Month_Expected 미 add_continuous_months_trackingfrom 추done
            # in progress복 추 제거

            # 10 conditions 평 결and Exceland CSVto 추
            self.add_condition_evaluation_to_excel()

            # AQL 통계 정보 추
            self.add_aql_statistics_to_excel()

            # CSV saved (condition 평 후)
            csv_file = os.path.join(output_dir, f"{self.config.output_prefix}_Complete_V9.0_Complete.csv")
            self.month_data.to_csv(csv_file, index=False, encoding='utf-8-sig')

            # CSV file created validation
            if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
                print(f"✅ CSV file 저장 완료: {csv_file}")
            else:
                print(f"⚠️ CSV file created failure: {csv_file}")

            # Excel saved
            excel_file = os.path.join(output_dir, f"{self.config.output_prefix}_Complete_V9.0_Complete.xlsx")
            self.month_data.to_excel(excel_file, index=False)
            
            # Excel file created validation
            if os.path.exists(excel_file) and os.path.getsize(excel_file) > 0:
                print(f"✅ Excel file 저장 완료: {excel_file}")
            else:
                print(f"⚠️ Excel file created failure: {excel_file}")
            
            # 메타data saved (condition 충족 상세 정보)
            metadata_file = self.save_calculation_metadata(output_dir)
            if metadata_file:
                print(f"✅ 메타data file 저장 완료: {metadata_file}")
            
            # HTML report created (비활성화 - dashboard_version4.htmlonly 사용)
            # html_file = self.generate_html_report()
            # if html_file:
            #     print(f"✅ HTML report 생성 완료: {html_file}")
            print("ℹ️ HTML Report created casesskip (dashboard_version4.htmlonly 사용)")
            
            # next month 계산용 파일 자동 created
            self.prepare_next_month_file(csv_file)
            
            return True
        except Exception as e:
            print(f"❌ file saved in progress Error: {e}")
            traceback.print_exc()
            return False
    
    def save_calculation_metadata(self, output_dir: str) -> Optional[str]:
        """calculation 메타data JSONwith saved (condition 충족 상세 정보 include)"""
        try:
            import json
            import os
            
            metadata = {}
            incentive_col = f"{self.config.get_month_str('capital')}_Incentive"
            
            for _, row in self.month_data.iterrows():
                emp_id = str(row['Employee No'])
                amount = row[incentive_col] if pd.notna(row[incentive_col]) else 0
                
                # default 정보
                # Position column same적 processing
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
                
                # condition 충족 정보 구성
                # attendance condition
                emp_metadata['conditions']['attendance'] = {
                    '출근율_Attendance_Rate_Percent': {
                        'passed': row.get('결근율_Absence_Rate_Percent', 0) <= 12 if pd.notna(row.get('결근율_Absence_Rate_Percent')) else True,
                        'value': 100 - row.get('결근율_Absence_Rate_Percent', 0) if pd.notna(row.get('결근율_Absence_Rate_Percent')) else 100,
                        'threshold': 88,
                        'applicable': True
                    },
                    'unapproved_absence': {
                        'passed': row.get('Unapproved Absences', 0) <= 2 if pd.notna(row.get('Unapproved Absences')) else True,
                        'value': int(row.get('Unapproved Absences', 0)) if pd.notna(row.get('Unapproved Absences')) else 0,
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
                
                # AQL condition (TYPE-1only)
                if row['ROLE TYPE STD'] == 'TYPE-1':
                    # MODEL MASTER 특별 processing
                    if 'MODEL MASTER' in str(position_value).upper():
                        # Model Master 전체 factory reject율 사용
                        area_reject_rate = 0.0
                        if hasattr(self, 'model_master_reject_rate'):
                            area_reject_rate = self.model_master_reject_rate
                        
                        emp_metadata['conditions']['aql'] = {
                            'monthly_failure': {
                                'passed': row.get(f'{self.config.get_month_str("capital")} AQL Failures', 0) == 0 if pd.notna(row.get(f'{self.config.get_month_str("capital")} AQL Failures')) else True,
                                'value': int(row.get(f'{self.config.get_month_str("capital")} AQL Failures', 0)) if pd.notna(row.get(f'{self.config.get_month_str("capital")} AQL Failures')) else 0,
                                'threshold': 0,
                                'applicable': False  # Model Master items인 AQL 체크 안함
                            },
                            '3월_continuous': {
                                'passed': row.get('Continuous_FAIL', 'NO') != 'YES' if pd.notna(row.get('Continuous_FAIL')) else True,
                                'value': row.get('Continuous_FAIL', 'NO'),
                                'threshold': 'NO',
                                'applicable': True
                            },
                            'subordinate_aql': {
                                'passed': True,
                                'value': 'N/A',
                                'threshold': 'N/A',
                                'applicable': False
                            },
                            'area_reject_rate': {
                                'passed': area_reject_rate < 3.0,
                                'value': round(area_reject_rate, 2),
                                'threshold': 3.0,
                                'applicable': True
                            }
                        }
                        
                        # 미지급 사유 추
                        if amount == 0 and area_reject_rate >= 3.0:
                            emp_metadata['calculation_basis'] = f'전체 factory AQL reject율 {area_reject_rate:.1f}% (basis: 3% 미only)'
                        elif amount == 0:
                            emp_metadata['calculation_basis'] = '기타 condition 미충족'
                        else:
                            emp_metadata['calculation_basis'] = 'Model Master incentive'
                    # AUDIT & TRAINING TEAM 특별 processing
                    elif 'AUDIT' in str(position_value).upper() or 'TRAINING' in str(position_value).upper():
                        # in charge area reject율 calculation
                        emp_id_str = str(row['Employee No'])
                        area_reject_rate = 0.0
                        
                        # in charge area reject율 져오기 (미 calculationdone value 참조해야 함)
                        if hasattr(self, 'auditor_area_reject_rates') and emp_id_str in self.auditor_area_reject_rates:
                            area_reject_rate = self.auditor_area_reject_rates[emp_id_str]
                        
                        emp_metadata['conditions']['aql'] = {
                            'monthly_failure': {
                                'passed': row.get(f'{self.config.get_month_str("capital")} AQL Failures', 0) == 0 if pd.notna(row.get(f'{self.config.get_month_str("capital")} AQL Failures')) else True,
                                'value': int(row.get(f'{self.config.get_month_str("capital")} AQL Failures', 0)) if pd.notna(row.get(f'{self.config.get_month_str("capital")} AQL Failures')) else 0,
                                'threshold': 0,
                                'applicable': True
                            },
                            '3월_continuous': {
                                'passed': row.get('Continuous_FAIL', 'NO') != 'YES' if pd.notna(row.get('Continuous_FAIL')) else True,
                                'value': row.get('Continuous_FAIL', 'NO'),
                                'threshold': 'NO',
                                'applicable': True
                            },
                            'subordinate_aql': {
                                'passed': True,  # 부하employee AQL은 별also 체크
                                'value': 'N/A',
                                'threshold': 'N/A',
                                'applicable': True
                            },
                            'area_reject_rate': {
                                'passed': area_reject_rate < 3.0,
                                'value': round(area_reject_rate, 2),
                                'threshold': 3.0,
                                'applicable': True
                            }
                        }
                        
                        # 미지급 사유 추
                        if amount == 0 and area_reject_rate >= 3.0:
                            emp_metadata['calculation_basis'] = f'in charge area AQL reject율 {area_reject_rate:.1f}% (basis: 3% 미only)'
                        elif amount == 0:
                            emp_metadata['calculation_basis'] = '기타 condition 미충족'
                        else:
                            emp_metadata['calculation_basis'] = 'Auditor/Trainer incentive'
                    # AQL INSPECTOR 특별 processing
                    elif 'AQL INSPECTOR' in str(position_value):
                        aql_col = f'{self.config.get_month_str("capital")} AQL Failures'
                        emp_metadata['conditions']['aql'] = {
                            'monthly_failure': {
                                'passed': amount > 0,  # incentive 받았으면 passedwith 간주
                                'value': 0 if amount > 0 else int(row.get(aql_col, 0)) if pd.notna(row.get(aql_col)) else 0,
                                'threshold': 0,
                                'applicable': True
                            },
                            '3월_continuous': {'applicable': False},
                            'subordinate_aql': {'applicable': False},
                            'area_reject_rate': {'applicable': False}
                        }
                        emp_metadata['calculation_basis'] = 'AQL Inspector 3-part incentive'
                    else:
                        aql_col = f'{self.config.get_month_str("capital")} AQL Failures'
                        emp_metadata['conditions']['aql'] = {
                            'monthly_failure': {
                                'passed': row.get(aql_col, 0) == 0 if pd.notna(row.get(aql_col)) else True,
                                'value': int(row.get(aql_col, 0)) if pd.notna(row.get(aql_col)) else 0,
                                'threshold': 0,
                                'applicable': True
                            },
                            '3월_continuous': {
                                'passed': row.get('Continuous_FAIL', 'NO') != 'YES' if pd.notna(row.get('Continuous_FAIL')) else True,
                                'value': row.get('Continuous_FAIL', 'NO'),
                                'threshold': 'NO',
                                'applicable': True
                            }
                        }
                
                # 5PRS conditions (TYPE-1, TYPE-2  days부)
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
            
            # JSON filewith saved
            metadata_file = os.path.join(output_dir, f"{self.config.output_prefix}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # file created validation
            if os.path.exists(metadata_file) and os.path.getsize(metadata_file) > 0:
                return metadata_file
            else:
                print(f"⚠️ 메타data file created failure: {metadata_file}")
                return None
            
        except Exception as e:
            print(f"  ⚠️ 메타data saved failure: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def prepare_next_month_file(self, csv_file_path):
        """next month 계산용 파일 자동 created (month 자same 순환 include)"""
        try:
            import shutil
            import os
            from datetime import datetime
            
            # month 름 mapping
            month_korean = {
                'january': '1월', 'february': '2월', 'march': '3월',
                'april': '4월', 'may': '5월', 'june': '6월',
                'july': 'July', 'august': 'August', 'september': 'September',
                'october': 'October', 'november': 'November', 'december': 'December'
            }
            
            # month 순서 mapping (자same 순환용)
            month_order = [
                'january', 'february', 'march', 'april', 'may', 'june',
                'july', 'august', 'september', 'october', 'november', 'december'
            ]
            
            # current month 인덱스 찾기
            current_month_name = self.config.month.full_name.lower()
            current_month_index = month_order.index(current_month_name)
            current_year = self.config.year
            
            # next month calculation (December → 1월 자same processing)
            if current_month_index == 11:  # December인 경우
                next_month_index = 0  # 1월with
                next_year = current_year + 1  # 연also 증
                print(f"  📅 연also 전환: {current_year}year December → {next_year}year 1월")
            else:
                next_month_index = current_month_index + 1
                next_year = current_year
            
            next_month_name = month_order[next_month_index]
            next_korean_month = month_korean[next_month_name]
            
            # current monthof 한글 름 (saved용)
            current_korean_month = month_korean.get(current_month_name, self.config.month.korean_name)
            
            # input_files 폴더 created
            os.makedirs("input_files", exist_ok=True)
            os.makedirs("input_files/backup", exist_ok=True)
            
            # current month file (previous month datawith 사용될 file)
            target_file = f"input_files/{current_year}year {current_korean_month} incentive 지급 세부 정보.csv"
            
            # existing file 백업
            if os.path.exists(target_file):
                backup_file = f"input_files/backup/{current_year}year {current_korean_month} incentive 지급 세부 정보_backup.csv"
                shutil.copy2(target_file, backup_file)
                print(f"  📦 existing file 백업: {backup_file}")
            
            # file 복사
            shutil.copy2(csv_file_path, target_file)
            print(f"\n🎯 next month 계산용 파일 자동 created:")
            print(f"  → {target_file}")
            print(f"  ℹ️ {next_year}year {next_korean_month} calculation 시 파일 자동with 사용됩니다.")
            
            # next month configuration 정보 created (선택적)
            next_month_info = f"""
📌 next month({next_year}year {next_korean_month}) calculation preparation completed:
   - previous month data: {current_year}year {current_korean_month} ✅
   - 필요한 file:
     • basic manpower data {next_month_name}.csv
     • aql data {next_month_name}.csv
     • 5prs data {next_month_name}.csv
     • attendance data {next_month_name}.csv
            """
            print(next_month_info)
            
        except Exception as e:
            print(f"  ⚠️ next month 파일 자동 created failure: {e}")
            print(f"     수samewith fileemployees 변경해주세요.")
    
    def generate_html_report(self) -> Optional[str]:
        """HTML report created (improved 버전)"""
        try:
            month_str = self.config.get_month_str('capital')
            month_kr = self.config.get_month_str('korean')
            incentive_col = f"{month_str}_Incentive"
            
            # Previous_Incentive column 미 있지 checking (save_resultsfrom 추done)
            if 'Previous_Incentive' not in self.month_data.columns:
                # previous month incentive data withload (6월 data)
                prev_incentive_data = None
                if self.config.previous_months:
                    prev_month = self.config.previous_months[-1]  # 마지막 previous month (6월)
                    # ✅ Use config path instead of hardcoded path (2025-10-04)
                    prev_file_path = self.config.file_paths.get('previous_incentive',
                                                                 f"input_files/{self.config.year}year {prev_month.number}month incentive 지급 세부 정보.csv")

                    import os
                    if os.path.exists(prev_file_path):
                        try:
                            prev_incentive_data = pd.read_csv(prev_file_path, encoding='utf-8-sig')
                            print(f"  ✅ {prev_month.korean_name} incentive data loaded successfully")
                            
                            # employee번호with 6월 incentive matching
                            if 'June_Incentive' in prev_incentive_data.columns:
                                prev_incentive_map = prev_incentive_data.set_index('Employee No')['June_Incentive'].to_dict()
                                self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)
                            elif f'{prev_month.full_name.capitalize()}_Incentive' in prev_incentive_data.columns:
                                col_name = f'{prev_month.full_name.capitalize()}_Incentive'
                                prev_incentive_map = prev_incentive_data.set_index('Employee No')[col_name].to_dict()
                                self.month_data['Previous_Incentive'] = self.month_data['Employee No'].map(prev_incentive_map).fillna(0)
                            else:
                                print(f"  ⚠️ {prev_month.korean_name} incentive column 찾 수 없습니다")
                                self.month_data['Previous_Incentive'] = 0
                        except Exception as e:
                            print(f"  ⚠️ {prev_month.korean_name} incentive data load failed: {e}")
                            self.month_data['Previous_Incentive'] = 0
                    else:
                        print(f"  ⚠️ {prev_month.korean_name} incentive file not found: {prev_file_path}")
                        self.month_data['Previous_Incentive'] = 0
                else:
                    self.month_data['Previous_Incentive'] = 0
            
            # 통계 계산 - Employee No 있 실제 employeeonly
            valid_employees = self.month_data[self.month_data['Employee No'].notna()]
            
            # calculation month previous 퇴사자 exclude
            calc_month_start = pd.Timestamp(self.config.year, self.config.month.number, 1)
            if 'Stop working Date' in valid_employees.columns:
                valid_employees['Stop working Date'] = pd.to_datetime(valid_employees['Stop working Date'], errors='coerce')
                active_employees = valid_employees[
                    (valid_employees['Stop working Date'].isna()) |  # 퇴사 days 없 employee
                    (valid_employees['Stop working Date'] >= calc_month_start)  # calculation month 후 퇴사자
                ]
            else:
                active_employees = valid_employees
            
            total_employees = len(active_employees)
            receiving_employees = (active_employees[incentive_col] > 0).sum()
            total_amount = active_employees[incentive_col].sum()
            
            # previous month incentive columnemployees 찾기
            prev_incentive_col = 'Previous_Incentive' if 'Previous_Incentive' in valid_employees.columns else None
            prev_month_kr = self.config.previous_months[-1].korean_name if self.config.previous_months else "previousmonth"
            
            # HTML 템플릿
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP incentive 계산 결과 report - {self.config.year}year {month_kr}</title>
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
            <h1>QIP incentive 계산 결과</h1>
            <p>{self.config.year}year {month_kr} | created days: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>전체 employee</h3>
                    <div class="value">{total_employees}<span class="unit">employees</span></div>
                </div>
                <div class="summary-card">
                    <h3>수령 employee</h3>
                    <div class="value">{receiving_employees}<span class="unit">employees</span></div>
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
                <div class="tab" data-tab="position" onclick="showTab('position')">position별 상세</div>
                <div class="tab" data-tab="detail" onclick="showTab('detail')">items인별 상세</div>
                <div class="tab" data-tab="criteria" onclick="showTab('criteria')">incentive basis</div>
            </div>
            
            <!-- 요약 탭 -->
            <div id="summary" class="tab-content active">
                <div class="section">
                    <h2 class="section-title">Type별 현황</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>전체 인VND</th>
                            <th>수령 인VND</th>
                            <th>수령률</th>
                            <th>총 지급액</th>
                            <th>평균 지급액</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            # Type별 data 추
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
    
    <!-- position별 상세 탭 -->
    <div id="position" class="tab-content">
        <div class="section">
            <h2 class="section-title">position별 상세 현황</h2>"""
            
            # position별 상세 테블 추
            for role_type in ['TYPE-1', 'TYPE-2', 'TYPE-3']:
                type_data = valid_employees[valid_employees['ROLE TYPE STD'] == role_type]
                if not type_data.empty:
                    html_content += f"""
            <h3 style="margin-top: 30px; color: #667eea;">{role_type} position별 통계</h3>
            <table>
                <thead>
                    <tr>
                        <th>position</th>
                        <th>총VND</th>
                        <th>수령인VND</th>
                        <th>미수령인VND</th>
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
                        positions.columns = ['총VND', '수령인VND', '총지급액', '평균지급액']
                        positions['미수령인VND'] = positions['총VND'] - positions['수령인VND']
                        positions['수령률'] = (positions['수령인VND'] / positions['총VND'] * 100).round(1)
                        positions = positions.sort_values('수령인VND', ascending=False)
                        
                        for position, row in positions.iterrows():
                            if row['총VND'] > 0:
                                html_content += f"""
                    <tr>
                        <td>{position}</td>
                        <td>{int(row['총VND'])}명</td>
                        <td>{int(row['수령인VND'])}명</td>
                        <td>{int(row['미수령인VND'])}명</td>
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
    
    <!-- items인별 상세 탭 -->
    <div id="detail" class="tab-content">
        <div class="section">
            <h2 class="section-title">items인별 상세 정보</h2>
            
            <!-- 필터 영역 -->
            <div class="filter-container">
                <div class="filter-row">
                    <input type="text" id="searchInput" class="filter-input" placeholder="employee번호 또 름 검색..." onkeyup="filterTable()">
                    <select id="typeFilter" class="filter-input" onchange="filterTable()">
                        <option value="">모든 Type</option>
                        <option value="TYPE-1">TYPE-1</option>
                        <option value="TYPE-2">TYPE-2</option>
                        <option value="TYPE-3">TYPE-3</option>
                    </select>
                    <input type="text" id="positionFilter" class="filter-input" placeholder="position 검색..." onkeyup="filterTable()">
                </div>
            </div>
            
            <!-- 상세 테블 -->
            <div style="overflow-x: auto;">
                <table id="detailTable" class="detail-table">
                    <thead>
                        <tr>
                            <th>employee번호</th>
                            <th>름</th>
                            <th>position</th>
                            <th>Type</th>
                            <th>{prev_month_kr} incentive</th>
                            <th>{month_kr} incentive</th>
                            <th>증감</th>
                            <th>calculation 근거</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            # items인별 상세 data 추
            for idx, row in valid_employees.iterrows():
                emp_no = row.get('Employee No', '')
                name = row.get('Full Name', '')
                position = row.get('QIP POSITION 1ST  NAME', '')
                role_type = row.get('ROLE TYPE STD', '')
                prev_amount = row.get('Previous_Incentive', 0) if 'Previous_Incentive' in row else 0
                curr_amount = row.get(incentive_col, 0)
                diff = curr_amount - prev_amount
                
                # calculation 근거 created (복수 사유 표시)
                reason = ""
                if curr_amount > 0:
                    if role_type == 'TYPE-1':
                        if 'ASSEMBLY INSPECTOR' in str(position).upper():
                            # consecutive months 수 찾기 (with그from 추출하거나 calculation)
                            reason = f"condition 충족 - consecutive month성"
                        elif 'LINE LEADER' in str(position).upper():
                            reason = "부하employee incentive × 15%"
                        elif 'GROUP LEADER' in str(position).upper():
                            reason = "Line Leader 평균 × 2"
                        else:
                            reason = "TYPE-1 basis 충족"
                    elif role_type == 'TYPE-2':
                        reason = "TYPE-1 평균 basis"
                    elif role_type == 'TYPE-3':
                        reason = "TYPE-3 정책 exclude"
                else:
                    # 미수령 사유 - 복수 사유 수집
                    reasons = []
                    
                    # TYPE-3 항상 정책 exclude
                    if role_type == 'TYPE-3':
                        reasons.append("TYPE-3 정책 exclude")
                    else:
                        # attendance condition 체크
                        if row.get('cond_3_actual_working_days') == 'FAIL':
                            reasons.append('실근무일=0')
                        if row.get('cond_2_unapproved_absence') == 'FAIL':
                            reasons.append('무단결근>2일')
                        if row.get('cond_1_attendance_rate') == 'FAIL':
                            reasons.append('출근율<88%')  # Phase 1: Single Source of Truth
                            reasons.append("absence rate >12%")
                        
                        # AQL condition 체크
                        if row.get('Continuous_FAIL', 'NO') == 'YES':
                            reasons.append("3-month consecutive AQL failure")
                        elif row.get(f"{month_str} AQL Failures", 0) > 0:
                            reasons.append("AQL failure")
                        
                        # 직책별 차별화done 체크
                        position_upper = str(position).upper()
                        
                        # AUDITOR/TRAINER 5PRS 체크 exclude
                        if 'AUDIT' not in position_upper and 'TRAINER' not in position_upper:
                            # Assembly Inspectoronly 5PRS 체크
                            if 'ASSEMBLY INSPECTOR' in position_upper:
                                if row.get('5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%') == 'no':
                                    reasons.append("5PRS conditions 미month")
                        
                        # LINE LEADER special condition (JSON matrix based)
                        if 'LINE LEADER' in position_upper and curr_amount == 0:
                            # JSON matrixfrom configuration checking
                            should_check_subordinates = False
                            if POSITION_CONDITION_MATRIX:
                                pos_config = get_position_config_from_matrix('TYPE-1', position)
                                if pos_config:
                                    applicable_conditions = pos_config.get('applicable_conditions', [])
                                    # condition 7: 팀/area AQL
                                    if 7 in applicable_conditions:
                                        should_check_subordinates = True
                            else:
                                # 폴백: existing with직
                                should_check_subordinates = True
                            
                            if should_check_subordinates:
                                subordinates = valid_employees[valid_employees['MST direct boss name'] == emp_no]
                                if (subordinates['Continuous_FAIL'] == 'YES').any():
                                    reasons.append("부하employee 3-month consecutive AQL failure (condition 7 미충족)")
                        
                        # AUDITOR/TRAINER special condition
                        if ('AUDIT' in position_upper or 'TRAINER' in position_upper) and curr_amount == 0:
                            # in charge area related 체크only (미 5PRS excludedone)
                            if not reasons:  # other 사유 없 경우toonly
                                reasons.append("in charge area reject율 초and 또 3-month consecutive failures 발생")
                    
                    # 사유 조합
                    if reasons:
                        if len(reasons) == 1:
                            reason = reasons[0]
                        else:
                            # 주요 사유and 추 사유 구분
                            reason = f"{reasons[0]} / 추: {', '.join(reasons[1:])}"
                    else:
                        reason = "condition 미충족"
                
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
    
    <!-- incentive basis 탭 -->
    <div id="criteria" class="tab-content">
        <div class="section">
            <h2 class="section-title">TYPE-1 incentive calculation basis</h2>
            
            <!-- Assembly Inspector -->
            <h3 style="color: #667eea; margin-top: 20px;">Assembly Inspector</h3>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ attendance condition: 실제 근무 days > 0 days, 무단결근 ≤ 2 days, absence rate ≤ 12%</li>
                <li>✅ AQL condition: 당month AQL failure 0cases, 최근 3-month consecutive failure 아님</li>
                <li>✅ 5PRS conditions: inspection량 ≥ 100items AND passed율 ≥ 95%</li>
            </ul>
            
            <h4>incentive calculation (consecutive 충족 month 수to 따른 차etc. 지급):</h4>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>consecutive 충족 month 수</th>
                        <th>incentive amount (VND)</th>
                        <th>비고</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>처음 충족 / consecutive성 끊김 후</td><td style="text-align: right;">150,000</td><td>default amount</td></tr>
                    <tr><td>1-month</td><td style="text-align: right;">150,000</td><td></td></tr>
                    <tr><td>2-month</td><td style="text-align: right;">250,000</td><td></td></tr>
                    <tr><td>3-month</td><td style="text-align: right;">300,000</td><td></td></tr>
                    <tr><td>4-month</td><td style="text-align: right;">350,000</td><td></td></tr>
                    <tr><td>5-month</td><td style="text-align: right;">400,000</td><td></td></tr>
                    <tr><td>6-month</td><td style="text-align: right;">450,000</td><td></td></tr>
                    <tr><td>7-month</td><td style="text-align: right;">500,000</td><td></td></tr>
                    <tr><td>8-month</td><td style="text-align: right;">650,000</td><td>급증</td></tr>
                    <tr><td>9-month</td><td style="text-align: right;">750,000</td><td></td></tr>
                    <tr><td>10-month</td><td style="text-align: right;">850,000</td><td></td></tr>
                    <tr><td>11-month</td><td style="text-align: right;">950,000</td><td></td></tr>
                    <tr><td>12-month 상</td><td style="text-align: right;">1,000,000</td><td>최대 amount</td></tr>
                </tbody>
            </table>
            
            <!-- AQL Inspector -->
            <h3 style="color: #667eea; margin-top: 30px;">AQL Inspector</h3>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ attendance condition: 실제 근무 days > 0 days, 무단결근 ≤ 2 days, absence rate ≤ 12%</li>
                <li>✅ AQL condition: 당month AQL failure 0cases</li>
                <li>❌ 5PRS conditions: 면제</li>
            </ul>
            
            <h4>incentive calculation (3-part 합산):</h4>
            <p style="margin: 10px 0;">총 incentive = Part 1 + Part 2 + Part 3</p>
            
            <h5 style="margin-top: 20px;">Part 1: AQL inspection 평 결and (Rejection Rate < 3%)</h5>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>consecutive 충족 month 수</th>
                        <th>incentive amount (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1-month</td><td style="text-align: right;">150,000</td></tr>
                    <tr><td>2-month</td><td style="text-align: right;">250,000</td></tr>
                    <tr><td>3-month</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>4-month</td><td style="text-align: right;">350,000</td></tr>
                    <tr><td>5-month</td><td style="text-align: right;">400,000</td></tr>
                    <tr><td>6-month</td><td style="text-align: right;">450,000</td></tr>
                    <tr><td>7-month</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>8-month</td><td style="text-align: right;">650,000</td></tr>
                    <tr><td>9-month</td><td style="text-align: right;">750,000</td></tr>
                    <tr><td>10-month</td><td style="text-align: right;">850,000</td></tr>
                    <tr><td>11-month</td><td style="text-align: right;">950,000</td></tr>
                    <tr><td>12-month 상</td><td style="text-align: right;">1,000,000</td></tr>
                </tbody>
            </table>
            
            <h5 style="margin-top: 20px;">Part 2: CFA 자격증</h5>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>condition</th>
                        <th>incentive amount (VND)</th>
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
                        <th>consecutive 충족 month 수</th>
                        <th>incentive amount (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1-3-month</td><td style="text-align: right;">0</td></tr>
                    <tr><td>4-6-month</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>7-9-month</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>10-12-month</td><td style="text-align: right;">700,000</td></tr>
                    <tr><td>13-month 상</td><td style="text-align: right;">900,000</td></tr>
                </tbody>
            </table>
            
            <!-- Line Leader -->
            <h3 style="color: #667eea; margin-top: 30px;">Line Leader</h3>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ attendance condition: 실제 근무 days > 0 days, 무단결근 ≤ 2 days, absence rate ≤ 12%</li>
                <li>❌ AQL condition: 면제</li>
                <li>❌ 5PRS conditions: 면제</li>
                <li>⚠️ 특별 condition: 부하employee in progress 3-month consecutive AQL failures 있으면 incentive 0VND</li>
            </ul>
            
            <h4>incentive calculation:</h4>
            <p style="margin: 10px 0;">
                <strong>calculation식:</strong> (부하employee incentive 총합 × 15%) × (incentive 받 부하employee 수 / 전체 부하employee 수)
            </p>
            
            <!-- manager급 -->
            <h3 style="color: #667eea; margin-top: 30px;">manager급 (Group Leader, Supervisor, Manager)</h3>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ attendance condition: 실제 근무 days > 0 days, 무단결근 ≤ 2 days, absence rate ≤ 12%</li>
                <li>❌ AQL condition: 면제</li>
                <li>❌ 5PRS conditions: 면제</li>
            </ul>
            
            <h4>incentive calculation:</h4>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>직책</th>
                        <th>calculation 방식</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Group Leader</td><td>팀 내 Line Leader 평균 incentive × 2</td></tr>
                    <tr><td>(Vice) Supervisor</td><td>팀 내 Line Leader 평균 incentive × 2.5</td></tr>
                    <tr><td>Assistant Manager</td><td>팀 내 Line Leader 평균 incentive × 3</td></tr>
                    <tr><td>Manager</td><td>팀 내 Line Leader 평균 incentive × 3.5</td></tr>
                    <tr><td>Senior Manager</td><td>팀 내 Line Leader 평균 incentive × 4</td></tr>
                </tbody>
            </table>
            
            <!-- Auditor/Trainer -->
            <h3 style="color: #667eea; margin-top: 30px;">Auditor/Trainer</h3>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ attendance condition: 실제 근무 days > 0 days, 무단결근 ≤ 2 days, absence rate ≤ 12%</li>
                <li>⚠️ in charge area condition:
                    <ul>
                        <li>in charge area AQL reject율 < 3%</li>
                        <li>in charge areato 3-month consecutive AQL failures 없음</li>
                    </ul>
                </li>
                <li>❌ 5PRS conditions: 면제</li>
            </ul>
            
            <h4>incentive calculation:</h4>
            <p style="margin: 10px 0;">condition 충족 시 Assembly Inspectorand same days한 consecutive 충족 month 수 basis apply</p>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>consecutive 충족 month 수</th>
                        <th>incentive amount (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1-month</td><td style="text-align: right;">150,000</td></tr>
                    <tr><td>2-month</td><td style="text-align: right;">250,000</td></tr>
                    <tr><td>3-month</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>4-month</td><td style="text-align: right;">350,000</td></tr>
                    <tr><td>5-month</td><td style="text-align: right;">400,000</td></tr>
                    <tr><td>6-month</td><td style="text-align: right;">450,000</td></tr>
                    <tr><td>7-month</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>8-month</td><td style="text-align: right;">650,000</td></tr>
                    <tr><td>9-month</td><td style="text-align: right;">750,000</td></tr>
                    <tr><td>10-month</td><td style="text-align: right;">850,000</td></tr>
                    <tr><td>11-month</td><td style="text-align: right;">950,000</td></tr>
                    <tr><td>12-month 상</td><td style="text-align: right;">1,000,000</td></tr>
                </tbody>
            </table>
            
            <!-- Model Master -->
            <h3 style="color: #667eea; margin-top: 30px;">Model Master</h3>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ attendance condition: 실제 근무 days > 0 days, 무단결근 ≤ 2 days, absence rate ≤ 12%</li>
                <li>⚠️ 전체 factory condition: 전체 factory AQL reject율 < 3%</li>
                <li>❌ 5PRS conditions: 면제</li>
            </ul>
            
            <h4>incentive calculation:</h4>
            <p style="margin: 10px 0;">condition 충족 시 Assembly Inspectorand same days한 consecutive 충족 month 수 basis apply</p>
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>consecutive 충족 month 수</th>
                        <th>incentive amount (VND)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1-month</td><td style="text-align: right;">150,000</td></tr>
                    <tr><td>2-month</td><td style="text-align: right;">250,000</td></tr>
                    <tr><td>3-month</td><td style="text-align: right;">300,000</td></tr>
                    <tr><td>4-month</td><td style="text-align: right;">350,000</td></tr>
                    <tr><td>5-month</td><td style="text-align: right;">400,000</td></tr>
                    <tr><td>6-month</td><td style="text-align: right;">450,000</td></tr>
                    <tr><td>7-month</td><td style="text-align: right;">500,000</td></tr>
                    <tr><td>8-month</td><td style="text-align: right;">650,000</td></tr>
                    <tr><td>9-month</td><td style="text-align: right;">750,000</td></tr>
                    <tr><td>10-month</td><td style="text-align: right;">850,000</td></tr>
                    <tr><td>11-month</td><td style="text-align: right;">950,000</td></tr>
                    <tr><td>12-month 상</td><td style="text-align: right;">1,000,000</td></tr>
                </tbody>
            </table>
            
            <!-- TYPE-2 incentive -->
            <h2 class="section-title" style="margin-top: 40px;">TYPE-2 incentive calculation basis</h2>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ attendance condition: 실제 근무 days > 0 days, 무단결근 ≤ 2 days, absence rate ≤ 12%</li>
                <li>❌ AQL condition: 면제</li>
                <li>❌ 5PRS conditions: 면제</li>
            </ul>
            
            <h4>incentive calculation:</h4>
            <p style="margin: 10px 0;">attendance condition 충족 시 matchingdone TYPE-1 포지션of 평균 incentive 지급</p>
            
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th>TYPE-2 포지션</th>
                        <th>matching되 TYPE-1 포지션</th>
                        <th>평균 incentive (예시)</th>
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
            
            <!-- TYPE-3 incentive -->
            <h2 class="section-title" style="margin-top: 40px;">TYPE-3 incentive calculation basis</h2>
            
            <h4>지급 condition:</h4>
            <ul style="margin-left: 20px;">
                <li>❌ incentive 지급 대상from exclude</li>
            </ul>
            
            <h4>대상자:</h4>
            <ul style="margin-left: 20px;">
                <li>입사 days basis 1-month 미only 신입 employee</li>
            </ul>
        </div>
    </div>
        
        <div class="footer">
            <p>© 2025 QIP incentive 관리 시스템</p>
            <p>본 report 자동으로 createdcompleted.</p>
        </div>
    </div>
</body>
</html>"""
            
            # file saved
            import os
            output_dir = "output_files"
            os.makedirs(output_dir, exist_ok=True)
            html_filename = os.path.join(output_dir, f"QIP_Incentive_Report_{month_str}_{self.config.year}.html")
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_filename
        
        except Exception as e:
            print(f"❌ HTML report created in progress Error: {e}")
            traceback.print_exc()
            return None


class CompleteDataLoader:
    """data with더 클래스 (improved 버전 - 자same 변환 지VND)"""
    
    def __init__(self, config: MonthConfig):
        self.config = config
        self.file_mapping = {
            f"{config.month.full_name}_basic": config.get_file_path("basic_manpower"),
            f"{config.previous_months[-1].full_name}_incentive" if config.previous_months else "prev_incentive":
                config.get_file_path("previous_incentive"),
            f"{config.month.full_name}_aql": config.get_file_path("aql_current"),
            f"{config.month.full_name}_5prs": config.get_file_path("5prs"),
            f"{config.month.full_name}_attendance": config.get_file_path("attendance")
        }
        
        # 자same 변환 configuration withload
        self.auto_convert_config = self.load_auto_convert_config()
        self.attendance_converter = None
    
    def load_auto_convert_config(self) -> Dict:
        """자same 변환 configuration withload"""
        try:
            config_path = Path('attendance_conversion_config.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        # default configuration
        return {
            "auto_convert": True,
            "debug_mode": False,
            "validate_conversion": True,
            "cache_enabled": True
        }
    
    def get_attendance_file_path(self, file_path: str, file_key: str) -> str:
        """출결 file 경with processing (자same 변환 include)"""
        # attendance file 아니면 그대with 반환
        if 'attendance' not in file_key.lower():
            return file_path
        
        # 자same 변환 비활성화면 그대with 반환
        if not self.auto_convert_config.get('auto_convert', True):
            return file_path
        
        # 자same 변환기 초기화 (필요시)
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
                    print("✅ 출결 자same 변환 모듈 loaded successfully")
                else:
                    self.attendance_converter = None
                    print("⚠️ 자same 변환 모듈 load failed: 수same 변환 경with 사용")
            except ImportError as e:
                print(f"⚠️ 자same 변환 모듈 load failed: {e}")
                return file_path
        
        # 자same 변환 실행
        try:
            converted_path = self.attendance_converter.ensure_converted_file(file_path)
            if converted_path != file_path:
                print(f"✅ 출결 data 자same 변환 completed: {os.path.basename(converted_path)}")
            return converted_path
        except Exception as e:
            print(f"⚠️ 자same 변환 failure, original file 사용: {e}")
            return file_path
    
    def load_single_file(self, file_path: str, file_key: str) -> Optional[pd.DataFrame]:
        """단 days file withing (자same 변환 지VND)"""
        # attendance fileof 경우 자same 변환 processing
        file_path = self.get_attendance_file_path(file_path, file_key)
        
        if not file_path or not os.path.exists(file_path):
            print(f"⚠️ file not found: {file_path}")
            return None
        
        try:
            # 다양한 인코ingand 구분자 attempt
            for enc in ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr']:
                for sep in [',', ';', '\t', '|']:
                    try:
                        df = pd.read_csv(file_path, sep=sep, encoding=enc)
                        if len(df) > 0 and len(df.columns) > 1:
                            # AQL fileof 경우 빈 행 제거 후 cases수 표시
                            if 'aql' in file_key.lower():
                                valid_df = df.dropna(how='all')
                                print(f"✅ {file_key} loaded successfully: {len(valid_df)} cases")
                            else:
                                print(f"✅ {file_key} loaded successfully: {len(df)} cases")
                            return df
                    except:
                        continue
            
            print(f"❌ {file_key} load failed")
            return None
        
        except Exception as e:
            print(f"❌ file withload 오류 ({file_key}): {e}")
            return None
    
    def load_all_files(self) -> Dict[str, pd.DataFrame]:
        """모든 file withload"""
        print(f"\n📂 {self.config.get_month_str('korean')} data file withing in progress...")
        
        data = {}
        for file_key, file_path in self.file_mapping.items():
            if file_path:  # None 아닌 경우only
                df = self.load_single_file(file_path, file_key)
                if df is not None:
                    data[file_key] = df
        
        print(f"✅ 총 {len(data)}items file loaded successfully")
        return data


def detect_month_from_attendance(file_path: str) -> tuple:
    """Attendance fileof Work Datefrom yearalsoand month 자same detection"""
    try:
        import pandas as pd
        
        # file 읽기
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Work Date column 찾기
        date_cols = ['Work Date', 'WorkDate', 'Date', 'date']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            print("⚠️ Date column not found.")
            return None, None
        
        # date 파싱 및 yearmonth 추출
        dates = pd.to_datetime(df[date_col], format='%Y.%m.%d', errors='coerce')
        dates = dates.dropna()
        
        if dates.empty:
            print("⚠️ 유효한 date 찾 수 없습니다.")
            return None, None
        
        # 장 많 나타나 yearmonth 찾기
        year_months = dates.dt.to_period('M')
        most_common = year_months.value_counts().index[0]
        
        year = most_common.year
        month = most_common.month
        
        print(f"✅ Attendance 파일에서 detectiondone yearMonth: {year}year {month}month")
        return year, month
        
    except Exception as e:
        print(f"⚠️ Attendance file yearmonth detection failure: {e}")
        return None, None


def calculate_working_days_from_attendance(file_path: str, year: int, month: int) -> int:
    """Attendance 파일에서 실제 근무 days calculation"""
    try:
        import pandas as pd
        
        # file 읽기
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Work Date columnfrom 해당 yearmonth 필터링
        date_pattern = f"{year}.{month:02d}"
        
        # Work Date column 찾기
        date_cols = ['Work Date', 'WorkDate', 'Date', 'date']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            print("⚠️ Date column not found. defaultvalue 사용")
            return None
        
        # 해당 monthof 유니크한 date 수 calculation
        month_dates = df[df[date_col].str.contains(date_pattern, na=False)][date_col]
        unique_dates = month_dates.str.extract(r'(\d{4}\.\d{2}\.\d{2})')[0].unique()
        working_days = len(unique_dates)
        
        print(f"✅ Attendance 파일에서 calculationdone {year}year {month}month Working days: {working_days} days")
        return working_days
        
    except Exception as e:
        print(f"⚠️ Attendance file 분석 failure: {e}")
        return None


def init_command():
    """초기 configuration employees령어 - 파일 자동 detection 및 configuration"""
    print("\n🔧 Initial configuration started...")
    print("📂 current directoryof file 분석합니다...")
    
    import os
    import glob
    
    # current directoryof CSV file 목록
    csv_files = glob.glob("*.csv")
    excel_files = glob.glob("*.xlsx")
    
    print(f"\n발견done file:")
    print(f"  CSV file: {len(csv_files)}items")
    print(f"  Excel file: {len(excel_files)}items")
    
    # Attendance file 찾기
    attendance_file = None
    for file in csv_files + excel_files:
        if 'attendance' in file.lower():
            attendance_file = file
            print(f"\n✅ Attendance file 발견: {attendance_file}")
            break
    
    if not attendance_file:
        print("⚠️ Attendance file not found.")
        attendance_file = input("Attendance file 경with 입력하세요: ").strip()
    
    # yearalsoand month 입력
    year = int(input("\n📅 연also 입력하세요 (예: 2025): "))
    month_num = int(input("📅 month 입력하세요 (1-12): "))
    
    # Attendance 파일에서 근무 days 자same calculation
    working_days = None
    if attendance_file and os.path.exists(attendance_file):
        if attendance_file.endswith('.csv'):
            working_days = calculate_working_days_from_attendance(attendance_file, year, month_num)
    
    if working_days is None:
        print("\n⚠️ Attendance 파일에서 cannot calculate working days from.")
        working_days = int(input("근무 days 직접 입력하세요: "))
    
    # Month 객체 created
    month = Month.from_number(month_num)
    
    # previous month configuration
    prev_month1 = Month.from_number((month_num - 2) % 12 or 12)
    prev_month2 = Month.from_number((month_num - 1) % 12 or 12)
    
    # file 패턴 detection
    print("\n📁 data Auto-detecting files...")
    
    # default file 패턴
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
    
    # 수same 입력 필요한 file
    for key in file_patterns:
        if key not in detected_files:
            print(f"\n⚠️ {key} 파일 자동with 찾 수 없습니다.")
            file_path = input(f"{key} file 경with 입력 (Enter: cases너뛰기): ").strip()
            if file_path:
                detected_files[key] = file_path
    
    # configuration created
    config = MonthConfig(
        year=year,
        month=month,
        working_days=working_days,
        previous_months=[prev_month1, prev_month2],
        file_paths=detected_files,
        output_prefix=f"output_QIP_incentive_{month.full_name}_{year}"
    )
    
    # configuration saved
    config_file = f"config_{month.full_name}_{year}.json"
    ConfigManager.save_config(config, config_file)
    print(f"\n✅ configuration {config_file}to savedcompleted.")
    
    # 실행 여부 checking
    if input("\n지금 바with incentive calculation 실행하시겠습니까? (y/n): ").lower() == 'y':
        return config
    
    return None


def main():
    """메인 실행 함수"""
    print("="*60)
    print(f"🚀 QIP Incentive Calculation System v8.02")
    print("="*60)
    
    # employees령어 체크
    import sys
    import argparse
    
    # argparsewith employees령줄 인자 processing
    parser = argparse.ArgumentParser(description='QIP Incentive Calculation System')
    parser.add_argument('--config', type=str, help='configuration file 경with')
    parser.add_argument('--init', action='store_true', help='자same configuration 초기화')
    args = parser.parse_args()
    
    # config file 지정done 경우
    if args.config:
        config = ConfigManager.load_config(args.config)
        if config is None:
            print(f"\n❌ configuration file not found: {args.config}")
            return
        print(f"\n✅ configuration file loaded successfully: {args.config}")
    elif args.init or (len(sys.argv) > 1 and sys.argv[1] == '/init'):
        config = init_command()
        if config is None:
            print("\n프with그램 종료합니다.")
            return
    else:
        # month 선택
        print("\n📅 Select month to calculate:")
        print("1. 6월 (June)")
        print("2. July (July)")
        print("3. Custom configuration")
        print("4. /init - Auto-configuration (recommended)")
        
        choice = input("\n선택 (1/2/3/4): ").strip()
    
        if choice == "4":
            config = init_command()
            if config is None:
                print("\n프with그램 종료합니다.")
                return
        elif choice == "1":
            config = ConfigManager.create_june_config()
        elif choice == "2":
            config = ConfigManager.create_july_config()
        elif choice == "3":
            # Custom configuration configuration
            year = int(input("연also 입력 (예: 2025): "))
            month_num = int(input("month 입력 (1-12): "))
            working_days = int(input("근무 days 수 입력: "))
            
            month = Month.from_number(month_num)
            prev_month1 = Month.from_number((month_num - 2) % 12 or 12)
            prev_month2 = Month.from_number((month_num - 1) % 12 or 12)
            
            config = MonthConfig(
                year=year,
                month=month,
                working_days=working_days,
                previous_months=[prev_month1, prev_month2],
                file_paths={
                    "basic": input(f"{month.korean_name} default data fileemployees: "),
                    "previous_incentive": input(f"{prev_month2.korean_name} incentive data fileemployees: "),
                    "aql": input(f"{month.korean_name} AQL data fileemployees: "),
                    "5prs": input(f"{month.korean_name} 5PRS data fileemployees: "),
                    "attendance": input(f"{month.korean_name} attendance data fileemployees: ")
                },
                output_prefix=f"output_QIP_incentive_{month.full_name}_{year}"
            )
        else:
            print("❌ 잘못done 선택입니다.")
            return
    
    # configuration saved 옵션 (config 파라미터with 실행한 경우to cases너뛰기)
    if not args.config:
        if input("\nconfiguration saved하시겠습니까? (y/n): ").lower() == 'y':
            ConfigManager.save_config(config)
    
    try:
        # data withload
        loader = CompleteDataLoader(config)
        data = loader.load_all_files()
        
        if not data:
            print("❌ withloaddone data 없습니다.")
            return
        
        # calculation기 초기화 및 실행
        calculator = CompleteQIPCalculator(data, config)
        
        # incentive calculation
        calculator.calculate_all_incentives()
        
        # 결and 요약
        calculator.generate_summary()
        
        # 결and saved
        if calculator.save_results():
            print(f"\n🎉 {config.get_month_str('korean')} incentive calculation 완료!")
        else:
            print("\n⚠️ 결and saved in progress  days부 오류 발생했습니다.")
    
    except Exception as e:
        print(f"\n❌ 실행 in progress 오류 발생: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

    