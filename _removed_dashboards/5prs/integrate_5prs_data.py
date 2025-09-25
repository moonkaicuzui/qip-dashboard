#!/usr/bin/env python3
"""
5PRS 데이터 통합 스크립트
Google Drive와 로컬 폴더에서 데이터를 가져와 기존 5PRS Dashboard와 통합
"""

import os
import sys
import json
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import numpy as np

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Google Drive Manager
try:
    from src.google_drive_manager import GoogleDriveManager
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    logger.warning("Google Drive Manager not available")
    GOOGLE_DRIVE_AVAILABLE = False


class DataIntegrator:
    """5PRS 데이터 통합 클래스"""
    
    def __init__(self, month: str, year: int, use_google_drive: bool = True):
        self.month = month
        self.year = year
        self.month_num = self.get_month_number(month)
        self.input_dir = Path('input_files')
        self.output_dir = Path('output_files/dashboards/5prs/data')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_google_drive = use_google_drive and GOOGLE_DRIVE_AVAILABLE
        self.drive_manager = None
        
        # Initialize Google Drive if enabled
        if self.use_google_drive:
            try:
                self.drive_manager = GoogleDriveManager()
                if not self.drive_manager.initialize():
                    logger.warning("Google Drive initialization failed, falling back to local files")
                    self.use_google_drive = False
            except Exception as e:
                logger.warning(f"Google Drive setup failed: {e}, using local files only")
                self.use_google_drive = False
        
    def get_month_number(self, month: str) -> int:
        """월 이름을 숫자로 변환"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month.lower(), 0)
    
    def find_data_files(self) -> List[Path]:
        """Google Drive와 로컬 폴더에서 데이터 파일 찾기"""
        files = []
        
        # 1. Google Drive에서 데이터 가져오기
        if self.use_google_drive and self.drive_manager:
            google_file = self._download_from_google_drive()
            if google_file and google_file.exists():
                files.append(google_file)
                logger.info(f"✅ Google Drive에서 데이터 로드: {google_file.name}")
        
        # 2. 로컬 폴더에서 데이터 찾기
        local_files = self._find_local_files()
        files.extend(local_files)
        
        # 중복 제거
        files = list(set(files))
        
        logger.info(f"총 찾은 데이터 파일: {len(files)}개")
        for f in files:
            logger.info(f"  - {f.name}")
        
        return files
    
    def _download_from_google_drive(self) -> Optional[Path]:
        """Google Drive에서 5PRS 데이터 다운로드"""
        try:
            # Google Drive 경로 설정
            drive_path = f"monthly_data/{self.year}_{self.month_num:02d}/5prs_data.csv"
            local_path = Path(f".cache/5prs_data_{self.month}_{self.year}.csv")
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 다운로드 실행
            if self.drive_manager.download_specific_file(drive_path, str(local_path)):
                return local_path
            else:
                logger.warning(f"Google Drive에서 파일을 찾을 수 없음: {drive_path}")
                return None
                
        except Exception as e:
            logger.error(f"Google Drive 다운로드 실패: {e}")
            return None
    
    def _find_local_files(self) -> List[Path]:
        """로컬 폴더에서 5PRS 데이터 파일 찾기"""
        files = []
        
        # 지원하는 확장자
        extensions = ['.csv', '.xlsx', '.xls', '.json']
        
        # 검색할 디렉토리들
        search_dirs = [
            self.input_dir,
            self.input_dir / '5prs',
            self.input_dir / '5PRS',
            Path('output_files/dashboards/5prs/data')
        ]
        
        # 파일 패턴 정의
        if self.month.lower() == 'all':
            patterns = ["*5prs*", "*PRS*", "*qip_trainer*"]
        else:
            patterns = [
                f"*5prs*{self.month}*",
                f"*5prs*{self.year}_{self.month_num:02d}*",
                f"*{self.month}*5prs*",
                f"5prs_data_{self.month}.csv"
            ]
        
        # 각 디렉토리에서 파일 검색
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in patterns:
                    for ext in extensions:
                        found = list(search_dir.glob(f"{pattern}{ext}"))
                        files.extend(found)
                        # 대소문자 구분 없이 검색
                        found = list(search_dir.glob(f"{pattern.upper()}{ext}"))
                        files.extend(found)
        
        return list(set(files))  # 중복 제거
    
    def read_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """파일 읽기 (CSV, Excel, JSON 지원)"""
        try:
            ext = file_path.suffix.lower()
            
            if ext == '.csv':
                # Use on_bad_lines='skip' for pandas >= 1.3.0
                try:
                    df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
                except TypeError:
                    # Fallback for older pandas versions
                    df = pd.read_csv(file_path, encoding='utf-8')
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'rawData' in data:
                        df = pd.DataFrame(data['rawData'])
                    else:
                        df = pd.DataFrame(data)
            else:
                logger.warning(f"지원하지 않는 파일 형식: {ext}")
                return None
            
            logger.info(f"✅ 파일 읽기 성공: {file_path.name} ({len(df)} rows)")
            return df
            
        except Exception as e:
            logger.error(f"파일 읽기 실패 {file_path.name}: {e}")
            return None
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """컬럼명 표준화"""
        column_mapping = {
            # 날짜
            'date': 'date',
            'Date': 'date',
            'inspection date': 'date',
            'Inspection Date': 'date',
            
            # 검사원
            'inspector id': 'inspector_id',
            'Inspector ID': 'inspector_id',
            'inspector': 'inspector_id',
            'checker': 'inspector_id',
            
            # TQC
            'tqc id': 'tqc_id',
            'TQC ID': 'tqc_id',
            'tqc': 'tqc_id',
            'TQC': 'tqc_id',
            
            # 건물/라인
            'building': 'building',
            'Building': 'building',
            'area': 'building',
            'AREA': 'building',
            'line': 'line',
            'Line': 'line',
            
            # 제품
            'product': 'product',
            'Product': 'product',
            'pcs': 'product',
            'item': 'product',
            
            # 수량
            'validation qty': 'validation_qty',
            'Validation Qty': 'validation_qty',
            'Valiation Qty': 'validation_qty',  # 오타 처리
            'validated qty': 'validation_qty',
            'pass qty': 'pass_qty',
            'Pass Qty': 'pass_qty',
            'pass': 'pass_qty',
            'passed': 'pass_qty',
            'reject qty': 'reject_qty',
            'Reject Qty': 'reject_qty',
            'reject': 'reject_qty',
            'failed': 'reject_qty',
            
            # 결과
            'result': 'result',
            'Result': 'result',
            '5PRS_PASS': 'result',
            
            # 불량 유형
            'defect type': 'defect_type',
            'Defect Type': 'defect_type',
            'defects': 'defect_type'
        }
        
        # 컬럼명 변경
        df = df.rename(columns=column_mapping)
        
        # 필수 컬럼이 없으면 기본값 추가
        if 'date' not in df.columns:
            df['date'] = f"{self.month_num}/1/{self.year}"
        
        if 'inspector_id' not in df.columns and 'tqc_id' in df.columns:
            df['inspector_id'] = df['tqc_id']
        
        if 'building' not in df.columns:
            df['building'] = '5PRS'
        
        if 'line' not in df.columns:
            df['line'] = 'Line 1'
        
        if 'pass_qty' not in df.columns and 'result' in df.columns:
            df['pass_qty'] = df['result'].apply(lambda x: 100 if str(x).lower() == 'pass' else 0)
            df['reject_qty'] = df['result'].apply(lambda x: 0 if str(x).lower() == 'pass' else 10)
        
        return df
    
    def integrate_data(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """여러 데이터프레임 통합"""
        if not dataframes:
            logger.warning("통합할 데이터가 없습니다")
            return pd.DataFrame()
        
        # 모든 데이터프레임 합치기
        integrated = pd.concat(dataframes, ignore_index=True)
        
        # 중복 제거 (사용 가능한 컬럼만 사용)
        dedup_cols = []
        if 'date' in integrated.columns:
            dedup_cols.append('date')
        if 'inspector_id' in integrated.columns:
            dedup_cols.append('inspector_id')
        if 'product' in integrated.columns:
            dedup_cols.append('product')
        elif 'Model' in integrated.columns:
            dedup_cols.append('Model')
            
        if dedup_cols:
            integrated = integrated.drop_duplicates(subset=dedup_cols, keep='first')
        
        logger.info(f"✅ 데이터 통합 완료: {len(integrated)} rows")
        return integrated
    
    def calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """통계 계산"""
        stats = {
            'total_records': len(df),
            'unique_inspectors': df['inspector_id'].nunique() if 'inspector_id' in df else 0,
            'unique_tqcs': df['tqc_id'].nunique() if 'tqc_id' in df else 0,
            'unique_buildings': df['building'].nunique() if 'building' in df else 0,
            'total_pass': 0,
            'total_reject': 0,
            'pass_rate': 0,
            'date_range': None
        }
        
        # Pass/Reject 계산
        if 'pass_qty' in df and 'reject_qty' in df:
            stats['total_pass'] = int(df['pass_qty'].sum())
            stats['total_reject'] = int(df['reject_qty'].sum())
            total = stats['total_pass'] + stats['total_reject']
            if total > 0:
                stats['pass_rate'] = round((stats['total_pass'] / total) * 100, 2)
        
        # 날짜 범위
        if 'date' in df:
            try:
                df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
                valid_dates = df['date_parsed'].dropna()
                if not valid_dates.empty:
                    stats['date_range'] = {
                        'start': valid_dates.min().strftime('%Y-%m-%d'),
                        'end': valid_dates.max().strftime('%Y-%m-%d')
                    }
            except:
                pass
        
        return stats
    
    def generate_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """차트용 데이터 생성"""
        charts = {}
        
        # 일별 추이 차트
        if 'date' in df and 'pass_qty' in df and 'reject_qty' in df:
            try:
                df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
                daily = df.groupby('date_parsed').agg({
                    'pass_qty': 'sum',
                    'reject_qty': 'sum'
                }).reset_index()
                
                daily['pass_rate'] = (daily['pass_qty'] / (daily['pass_qty'] + daily['reject_qty']) * 100).round(2)
                
                charts['daily_trend'] = {
                    'labels': [d.strftime('%m/%d') if pd.notna(d) else '' for d in daily['date_parsed']],
                    'pass_rates': daily['pass_rate'].tolist(),
                    'pass_qty': daily['pass_qty'].tolist(),
                    'reject_qty': daily['reject_qty'].tolist()
                }
            except:
                pass
        
        # 건물별 성과
        if 'building' in df and 'pass_qty' in df and 'reject_qty' in df:
            building_stats = df.groupby('building').agg({
                'pass_qty': 'sum',
                'reject_qty': 'sum'
            }).reset_index()
            
            building_stats['total'] = building_stats['pass_qty'] + building_stats['reject_qty']
            building_stats['pass_rate'] = (building_stats['pass_qty'] / building_stats['total'] * 100).round(2)
            
            charts['building_performance'] = {
                'labels': building_stats['building'].tolist(),
                'pass_rates': building_stats['pass_rate'].tolist(),
                'totals': building_stats['total'].tolist()
            }
        
        # Top 10 검사원
        if 'inspector_id' in df and 'pass_qty' in df and 'reject_qty' in df:
            inspector_stats = df.groupby('inspector_id').agg({
                'pass_qty': 'sum',
                'reject_qty': 'sum'
            }).reset_index()
            
            inspector_stats['total'] = inspector_stats['pass_qty'] + inspector_stats['reject_qty']
            inspector_stats['pass_rate'] = (inspector_stats['pass_qty'] / inspector_stats['total'] * 100).round(2)
            inspector_stats = inspector_stats.nlargest(10, 'total')
            
            charts['top_inspectors'] = {
                'labels': inspector_stats['inspector_id'].tolist(),
                'pass_rates': inspector_stats['pass_rate'].tolist(),
                'totals': inspector_stats['total'].tolist()
            }
        
        return charts
    
    def save_integrated_data(self, df: pd.DataFrame, stats: Dict, charts: Dict) -> str:
        """통합 데이터를 JSON으로 저장"""
        
        # 출력 파일 경로
        if self.month.lower() == 'all':
            output_file = self.output_dir / f"integrated_5prs_{self.year}_all.json"
        else:
            output_file = self.output_dir / f"integrated_5prs_{self.year}_{self.month_num:02d}.json"
        
        # NaN 및 Infinity 처리
        def clean_value(v):
            if isinstance(v, float):
                if np.isnan(v) or np.isinf(v):
                    return None
            return v
        
        # DataFrame을 딕셔너리로 변환 (NaN 처리)
        records = []
        for _, row in df.iterrows():
            record = {}
            for col, val in row.items():
                record[col] = clean_value(val)
            records.append(record)
        
        # 최종 데이터 구조
        output_data = {
            'metadata': {
                'month': self.month,
                'year': self.year,
                'generated_at': datetime.now().isoformat(),
                'version': '2.0'
            },
            'statistics': stats,
            'charts': charts,
            'raw_data': records[:1000],  # 대시보드용으로 최대 1000개만
            'full_data_count': len(records)
        }
        
        # JSON 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"✅ 통합 데이터 저장: {output_file}")
        return str(output_file)
    
    def run(self) -> bool:
        """통합 프로세스 실행"""
        logger.info(f"📊 {self.year}년 {self.month} 데이터 통합 시작")
        
        # 1. 데이터 파일 찾기
        files = self.find_data_files()
        if not files:
            logger.warning("데이터 파일을 찾을 수 없습니다")
            # 빈 데이터로 파일 생성
            self.save_integrated_data(pd.DataFrame(), {}, {})
            return False
        
        # 2. 파일 읽기 및 표준화
        dataframes = []
        for file_path in files:
            df = self.read_file(file_path)
            if df is not None and not df.empty:
                df = self.standardize_columns(df)
                dataframes.append(df)
        
        if not dataframes:
            logger.warning("읽을 수 있는 데이터가 없습니다")
            self.save_integrated_data(pd.DataFrame(), {}, {})
            return False
        
        # 3. 데이터 통합
        integrated_df = self.integrate_data(dataframes)
        
        # 4. 통계 계산
        stats = self.calculate_statistics(integrated_df)
        
        # 5. 차트 데이터 생성
        charts = self.generate_chart_data(integrated_df)
        
        # 6. 저장
        output_path = self.save_integrated_data(integrated_df, stats, charts)
        
        # 7. 요약 출력
        logger.info("=" * 50)
        logger.info(f"📊 통합 완료 요약")
        logger.info(f"  - 총 레코드: {stats['total_records']:,}")
        logger.info(f"  - 검사원 수: {stats['unique_inspectors']}")
        logger.info(f"  - 합격률: {stats['pass_rate']}%")
        logger.info(f"  - 출력 파일: {output_path}")
        logger.info("=" * 50)
        
        return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='5PRS 데이터 통합 (Google Drive + 로컬)')
    parser.add_argument('--month', type=str, required=True, help='월 (예: august)')
    parser.add_argument('--year', type=int, default=2025, help='년도')
    parser.add_argument('--no-google', action='store_true', help='Google Drive 사용 안함')
    parser.add_argument('--api-mode', action='store_true', help='API 모드로 실행 (JSON 출력)')
    
    args = parser.parse_args()
    
    # 통합 실행
    use_google = not args.no_google
    integrator = DataIntegrator(args.month, args.year, use_google_drive=use_google)
    
    if args.api_mode:
        # API 모드: JSON 형식으로 데이터 반환
        success = integrator.run()
        if success:
            # 생성된 JSON 파일 경로 출력
            output_file = integrator.output_dir / f"integrated_5prs_{args.year}_{integrator.month_num:02d}.json"
            print(json.dumps({"status": "success", "file": str(output_file)}))
        else:
            print(json.dumps({"status": "error", "message": "Data integration failed"}))
    else:
        # 일반 모드
        success = integrator.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()