"""
[OPTIONAL] Google Drive 자동 실행 시스템
Google Drive에서 데이터를 자동으로 다운로드하고 모든 단계를 한번에 실행합니다.

터미널 실행 명령어:
python src/auto_run_with_drive.py --month september --year 2025

12개월 실행 예시:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2025년
python src/auto_run_with_drive.py --month july --year 2025      # 7월
python src/auto_run_with_drive.py --month august --year 2025    # 8월
python src/auto_run_with_drive.py --month september --year 2025 # 9월
python src/auto_run_with_drive.py --month october --year 2025   # 10월
python src/auto_run_with_drive.py --month november --year 2025  # 11월
python src/auto_run_with_drive.py --month december --year 2025  # 12월

# 2026년
python src/auto_run_with_drive.py --month january --year 2026   # 1월
python src/auto_run_with_drive.py --month february --year 2026  # 2월
python src/auto_run_with_drive.py --month march --year 2026     # 3월
python src/auto_run_with_drive.py --month april --year 2026     # 4월
python src/auto_run_with_drive.py --month may --year 2026       # 5월
python src/auto_run_with_drive.py --month june --year 2026      # 6월
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

주의: 이 파일은 step0, step1, step2를 모두 자동으로 실행합니다.
개별 실행을 원하면 step0, step1, step2를 순서대로 실행하세요.
"""

import os
import sys
import json
import logging
import schedule
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_drive_manager import GoogleDriveManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomatedQIPRunner:
    """
    Automated runner for QIP Incentive calculations with Google Drive sync
    """
    
    def __init__(self, drive_config: str = 'config_files/drive_config.json'):
        """
        Initialize the automated runner
        
        Args:
            drive_config: Path to Drive configuration file
        """
        self.drive_manager = GoogleDriveManager(drive_config)
        self.initialized = False
        
    def initialize(self, auth_type: str = 'service_account', 
                  credentials_path: Optional[str] = None) -> bool:
        """
        Initialize Google Drive connection
        
        Args:
            auth_type: Authentication type ('service_account' or 'oauth2')
            credentials_path: Path to credentials file
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # Try to get credentials from environment variable first
            if not credentials_path and auth_type == 'service_account':
                credentials_path = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            
            self.initialized = self.drive_manager.initialize(auth_type, credentials_path)
            
            if self.initialized:
                logger.info("✅ Google Drive connection established")
            else:
                logger.error("❌ Failed to establish Google Drive connection")
                
            return self.initialized
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    def run_monthly_calculation(self, year: Optional[int] = None, 
                              month: Optional[str] = None) -> bool:
        """
        Run the complete monthly calculation workflow
        
        Args:
            year: Year to process (default: current year)
            month: Month to process (default: current month)
            
        Returns:
            bool: True if successful
        """
        try:
            # Get current month if not specified
            if not year or not month:
                now = datetime.now()
                year = year or now.year
                month = month or now.strftime('%B').lower()
            
            logger.info(f"🚀 Starting monthly calculation for {month} {year}")
            
            # Step 1: Sync data from Google Drive
            if self.initialized:
                logger.info("📥 Syncing data from Google Drive...")
                sync_result = self.drive_manager.sync_monthly_data(year, month)
                
                # 선택적 파일은 실패해도 계속 진행
                if sync_result.files_synced == 0 and sync_result.files_failed > 0:
                    logger.error(f"❌ Data sync completely failed: {sync_result.error_message}")
                    return False
                elif sync_result.files_failed > 0:
                    logger.warning(f"⚠️ Some files failed to sync ({sync_result.files_failed} files), but continuing with {sync_result.files_synced} synced files")
                    
                logger.info(f"✅ Successfully synced {sync_result.files_synced} files")
                
                # Validate synced data
                validation = self.drive_manager.validate_synced_data(month)
                
                # Check critical files (basic, attendance, 5prs)
                critical_files = [
                    f'input_files/basic manpower data {month}.csv',
                    f'input_files/attendance/original/attendance data {month}.csv',
                    f'input_files/5prs data {month}.csv'
                ]
                
                critical_missing = []
                for file in critical_files:
                    if not validation.get(file, False):
                        critical_missing.append(file)
                
                if critical_missing:
                    logger.error("❌ Critical files are missing:")
                    for file in critical_missing:
                        logger.error(f"  ❌ {file}")
                    logger.error("Cannot proceed without critical data files!")
                    return False
                    
                if not all(validation.values()):
                    logger.warning("⚠️ Some optional files failed validation")
                    for file, valid in validation.items():
                        if not valid and file not in critical_files:
                            logger.warning(f"  ⚠️ {file}")
            else:
                logger.warning("⚠️ Drive not initialized, using local files")
            
            # Step 2: Convert attendance data if needed
            logger.info("📊 Converting attendance data...")
            self._convert_attendance_data(month)
            
            # Step 3: Prepare configuration file
            logger.info("⚙️ Preparing configuration...")
            config_file = self._prepare_config(year, month)
            
            # Step 4: Run main incentive calculation
            logger.info("💰 Running incentive calculation...")
            calc_result = self._run_calculation(config_file)
            
            if not calc_result:
                logger.error("❌ Incentive calculation failed")
                return False
            
            # Step 5: Generate dashboards
            logger.info("📈 Generating dashboards...")
            dashboard_result = self._generate_dashboards(month, year)
            
            if dashboard_result:
                logger.info(f"✅ Monthly calculation completed successfully for {month} {year}")
                self._send_notification('success', month, year)
                return True
            else:
                logger.error("❌ Dashboard generation failed")
                return False
                
        except Exception as e:
            logger.error(f"Error in monthly calculation: {e}")
            self._send_notification('error', month, year, str(e))
            return False
    
    def _convert_attendance_data(self, month: str) -> bool:
        """
        Convert attendance data to required format
        
        Args:
            month: Month name
            
        Returns:
            bool: True if successful
        """
        try:
            # Check if conversion script exists
            converter_path = Path('input_files/attendance/convert_attendance.py')
            if not converter_path.exists():
                logger.warning("Attendance converter not found, skipping conversion")
                return True
            
            # Run conversion
            result = subprocess.run(
                [sys.executable, str(converter_path)],
                capture_output=True,
                text=True,
                cwd='input_files/attendance'
            )
            
            if result.returncode == 0:
                logger.info("✅ Attendance data converted successfully")
                return True
            else:
                logger.error(f"Attendance conversion failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error converting attendance data: {e}")
            return False
    
    def _prepare_config(self, year: int, month: str) -> str:
        """
        Prepare configuration file for the calculation
        
        Args:
            year: Year
            month: Month name
            
        Returns:
            str: Path to configuration file
        """
        config_file = f"config_{month}_{year}.json"
        
        # Check if config already exists
        if Path(config_file).exists():
            logger.info(f"Using existing config: {config_file}")
            return config_file
        
        # Create new config from template
        config = {
            "year": year,
            "month": month,
            "working_days": 23,  # Default, should be updated
            "previous_months": self._get_previous_months(month),
            "file_paths": {
                "basic": f"input_files/basic manpower data {month}.csv",
                "previous_incentive": f"input_files/{year}년 {self._get_month_number(month)-1}월 인센티브 지급 세부 정보.csv",
                "aql": f"input_files/AQL history/1.HSRG AQL REPORT-{month.upper()}.{year}.csv",
                "5prs": f"input_files/5prs data {month}.csv",
                "attendance": f"input_files/attendance/converted/attendance data {month}_converted.csv"
            },
            "output_prefix": f"output_QIP_incentive_{month}_{year}"
        }
        
        # Save config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created new config: {config_file}")
        return config_file
    
    def _get_previous_months(self, month: str) -> list:
        """Get list of two previous months"""
        months = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        current_idx = months.index(month.lower())
        prev_months = []
        
        for i in range(1, 3):
            idx = (current_idx - i) % 12
            prev_months.append(months[idx])
        
        return prev_months
    
    def _get_month_number(self, month: str) -> int:
        """Convert month name to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month.lower(), 0)
    
    def _run_calculation(self, config_file: str) -> bool:
        """
        Run the main incentive calculation
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            bool: True if successful
        """
        try:
            # Check if main script exists
            calc_script = Path('step1_인센티브_계산_개선버전.py')
            if not calc_script.exists():
                # Try src folder
                calc_script = Path('src/step1_인센티브_계산_개선버전.py')
                if not calc_script.exists():
                    logger.error("Main calculation script not found")
                    return False
            
            # Run calculation
            result = subprocess.run(
                [sys.executable, str(calc_script), '--config', config_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Incentive calculation completed")
                return True
            else:
                logger.error(f"Calculation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running calculation: {e}")
            return False
    
    def _generate_dashboards(self, month: str = None, year: int = None) -> bool:
        """
        Generate all dashboard versions
        
        Args:
            month: Month name for dashboard filename
            year: Year for dashboard filename
            
        Returns:
            bool: True if successful
        """
        try:
            # Dashboard version 4 (최신 버전) - 월별 파일명 지원
            dashboard_v4 = Path(__file__).parent / 'step2_dashboard_version4.py'
            if dashboard_v4.exists():
                logger.info(f"Generating dashboard v4 for {month} {year}...")
                cmd = [sys.executable, str(dashboard_v4)]
                if month and year:
                    cmd.extend(['--month', month, '--year', str(year)])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"Dashboard v4 generation warning: {result.stderr}")
            
            # 다른 버전들도 생성 (호환성 유지)
            dashboard_scripts = [
                '../dashboard_version3/dashboard_version3.py',
                '../dashboard_version2/dashboard_version2.py'
            ]
            
            for script in dashboard_scripts:
                if Path(script).exists():
                    logger.info(f"Generating {script}...")
                    result = subprocess.run(
                        [sys.executable, script],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        logger.warning(f"Dashboard generation warning for {script}: {result.stderr}")
            
            logger.info("✅ Dashboard generation completed")
            return True
            
        except Exception as e:
            logger.error(f"Error generating dashboards: {e}")
            return False
    
    def _send_notification(self, status: str, month: str, year: int, 
                          error_msg: str = ""):
        """
        Send notification about the run status
        
        Args:
            status: 'success' or 'error'
            month: Month processed
            year: Year processed
            error_msg: Error message if failed
        """
        # This is a placeholder for notification logic
        # Could implement email, Slack, etc.
        if status == 'success':
            logger.info(f"📧 Notification: Successfully processed {month} {year}")
        else:
            logger.info(f"📧 Notification: Failed to process {month} {year}: {error_msg}")
    
    def schedule_monthly_runs(self):
        """
        Schedule monthly runs
        """
        # Schedule for the 1st day of each month at 8:00 AM
        schedule.every().month.at("08:00").do(self.run_monthly_calculation)
        
        logger.info("📅 Scheduled monthly runs at 8:00 AM on the 1st of each month")
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated QIP Incentive System with Google Drive Integration'
    )
    parser.add_argument('--month', type=str, help='Month to process (e.g., july)')
    parser.add_argument('--year', type=int, help='Year to process (e.g., 2025)')
    parser.add_argument('--schedule', action='store_true', 
                       help='Run in scheduled mode')
    parser.add_argument('--auth', type=str, choices=['service_account', 'oauth2'],
                       default='service_account', help='Authentication type')
    parser.add_argument('--credentials', type=str, 
                       help='Path to credentials file')
    parser.add_argument('--no-drive', action='store_true',
                       help='Run without Google Drive sync')
    parser.add_argument('--sync-only', action='store_true',
                       help='Only sync data from Google Drive, do not run calculations')
    
    args = parser.parse_args()
    
    # Check if month is specified when not in schedule mode
    if not args.schedule and not args.month:
        print("\n❌ Error: Month parameter is required!")
        print("\n📋 Usage examples:")
        print("  python src/auto_run_with_drive.py --month july --year 2025")
        print("  python src/auto_run_with_drive.py --month august --year 2025")
        print("\n💡 Available months:")
        print("  january, february, march, april, may, june,")
        print("  july, august, september, october, november, december")
        print("\n📖 For more help: python src/auto_run_with_drive.py --help")
        return
    
    # Create runner
    runner = AutomatedQIPRunner()
    
    # Initialize Drive connection if not disabled
    if not args.no_drive:
        if not runner.initialize(args.auth, args.credentials):
            logger.warning("⚠️ Continuing without Google Drive sync")
    
    # Run based on mode
    if args.schedule:
        # Scheduled mode
        logger.info("🔄 Starting scheduled mode...")
        runner.schedule_monthly_runs()
    elif args.sync_only:
        # Sync only mode
        logger.info("📥 Sync-only mode - downloading data from Google Drive...")
        if runner.initialized:
            sync_result = runner.drive_manager.sync_monthly_data(args.year, args.month)
            if sync_result.files_synced > 0:
                logger.info(f"✅ Successfully synced {sync_result.files_synced} files")
            else:
                logger.error("❌ No files were synced")
        else:
            logger.error("❌ Google Drive not initialized")
    else:
        # Single run mode with specified month
        runner.run_monthly_calculation(args.year, args.month)


if __name__ == "__main__":
    main()