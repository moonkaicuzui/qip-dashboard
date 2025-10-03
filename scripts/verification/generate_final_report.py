#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 검증 리포트 생성기
모든 validation 스크립트의 결과를 통합하여 최종 리포트를 생성합니다.

실행 방법:
    # 자동으로 최신 리포트 찾아서 통합
    python scripts/verification/generate_final_report.py september 2025

    # 또는 모든 검증 스크립트를 실행한 후 통합
    python scripts/verification/generate_final_report.py september 2025 --run-all
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import argparse
import sys
import subprocess
import glob

class IntegratedReportGenerator:
    """통합 검증 리포트 생성기"""

    def __init__(self, month: str, year: int):
        self.month = month
        self.year = year
        self.base_path = Path(__file__).parent.parent.parent
        self.validation_reports_dir = self.base_path / 'validation_reports'

        # 통합 결과
        self.all_findings = []
        self.validation_summary = {}

    def run_all_validations(self):
        """모든 검증 스크립트 실행"""
        print("="*80)
        print("🚀 모든 검증 스크립트 실행 중...")
        print("="*80)

        scripts_dir = self.base_path / 'scripts' / 'verification'

        # 실행할 스크립트 목록
        validation_scripts = [
            ('validate_condition_evaluation.py', 'Condition Evaluation'),
            ('validate_incentive_amounts.py', 'Incentive Amounts'),
            ('validate_dashboard_consistency.py', 'Dashboard Consistency')
        ]

        for script_name, description in validation_scripts:
            script_path = scripts_dir / script_name

            if not script_path.exists():
                print(f"   ⚠️ {description} 스크립트 없음: {script_name}")
                continue

            print(f"\n📝 {description} 검증 실행 중...")

            try:
                result = subprocess.run(
                    ['python3', str(script_path), self.month, str(self.year)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5분 타임아웃
                )

                if result.returncode == 0:
                    print(f"   ✅ {description} 검증 완료")
                else:
                    print(f"   ⚠️ {description} 검증 경고 (Exit code: {result.returncode})")

                # 출력 표시
                if result.stdout:
                    print(result.stdout)

            except subprocess.TimeoutExpired:
                print(f"   ❌ {description} 검증 시간 초과 (5분)")
            except Exception as e:
                print(f"   ❌ {description} 검증 오류: {e}")

        print("\n" + "="*80)
        print("✅ 모든 검증 스크립트 실행 완료")
        print("="*80)

    def find_latest_report(self, pattern: str):
        """가장 최근 리포트 파일 찾기"""
        report_files = glob.glob(str(self.validation_reports_dir / pattern))

        if not report_files:
            return None

        # 파일명의 타임스탬프로 정렬 (가장 최근 파일)
        latest_file = max(report_files, key=os.path.getmtime)
        return Path(latest_file)

    def load_validation_reports(self):
        """모든 validation 리포트 로드"""
        print("\n📂 Validation 리포트 로드 중...")

        # 리포트 패턴 정의
        report_patterns = {
            'Condition Evaluation': f'condition_evaluation_report_{self.month}_{self.year}_*.xlsx',
            'Incentive Amounts': f'incentive_amount_report_{self.month}_{self.year}_*.xlsx',
            'Dashboard Consistency': f'dashboard_consistency_report_{self.month}_{self.year}_*.xlsx'
        }

        loaded_reports = {}

        for validation_type, pattern in report_patterns.items():
            report_file = self.find_latest_report(pattern)

            if report_file:
                print(f"   ✅ {validation_type}: {report_file.name}")
                try:
                    # Excel 파일의 모든 시트 로드
                    excel_data = pd.read_excel(report_file, sheet_name=None)
                    loaded_reports[validation_type] = excel_data
                except Exception as e:
                    print(f"   ❌ {validation_type} 로드 실패: {e}")
            else:
                print(f"   ⚠️ {validation_type} 리포트 없음")

        return loaded_reports

    def aggregate_findings(self, reports: dict):
        """모든 리포트에서 findings 통합"""
        print("\n🔍 Findings 통합 중...")

        all_findings = []

        for validation_type, excel_data in reports.items():
            # '상세 오류' 시트 찾기
            error_sheets = [sheet for sheet in excel_data.keys() if '오류' in sheet or 'error' in sheet.lower()]

            for sheet_name in error_sheets:
                df_errors = excel_data[sheet_name]

                if df_errors.empty:
                    continue

                # 각 오류에 validation_type 추가
                for idx, row in df_errors.iterrows():
                    finding = row.to_dict()
                    finding['Validation_Type'] = validation_type
                    finding['Sheet'] = sheet_name
                    all_findings.append(finding)

        print(f"   ✅ 총 {len(all_findings)}개 findings 통합 완료")
        self.all_findings = all_findings

        return all_findings

    def generate_executive_summary(self, reports: dict):
        """Executive Summary 생성"""
        summary = {
            'Total_Validations': len(reports),
            'Total_Findings': len(self.all_findings),
            'Critical': len([f for f in self.all_findings if f.get('Severity') == 'CRITICAL']),
            'Error': len([f for f in self.all_findings if f.get('Severity') == 'ERROR']),
            'Warning': len([f for f in self.all_findings if f.get('Severity') == 'WARNING']),
            'Validations_Details': {}
        }

        # Validation별 요약
        for validation_type, excel_data in reports.items():
            if '요약' in excel_data:
                df_summary = excel_data['요약']
                total_errors = df_summary['오류 건수'].sum() if '오류 건수' in df_summary.columns else 0
                critical_errors = df_summary['Critical'].sum() if 'Critical' in df_summary.columns else 0

                summary['Validations_Details'][validation_type] = {
                    'Total_Errors': int(total_errors),
                    'Critical_Errors': int(critical_errors)
                }

        self.validation_summary = summary
        return summary

    def generate_priority_action_items(self):
        """우선순위 기반 조치 항목 생성"""
        print("\n📋 우선순위 조치 항목 생성 중...")

        # Severity별 그룹화
        critical_items = [f for f in self.all_findings if f.get('Severity') == 'CRITICAL']
        error_items = [f for f in self.all_findings if f.get('Severity') == 'ERROR']
        warning_items = [f for f in self.all_findings if f.get('Severity') == 'WARNING']

        action_items = []

        # Priority 1: CRITICAL
        for idx, item in enumerate(critical_items, 1):
            action_items.append({
                'Priority': 1,
                'Severity': 'CRITICAL',
                'Validation_Type': item.get('Validation_Type', ''),
                'Issue': self._format_issue_description(item),
                'Recommendation': self._get_recommendation(item)
            })

        # Priority 2: ERROR
        for idx, item in enumerate(error_items, 1):
            action_items.append({
                'Priority': 2,
                'Severity': 'ERROR',
                'Validation_Type': item.get('Validation_Type', ''),
                'Issue': self._format_issue_description(item),
                'Recommendation': self._get_recommendation(item)
            })

        # Priority 3: WARNING
        for idx, item in enumerate(warning_items, 1):
            action_items.append({
                'Priority': 3,
                'Severity': 'WARNING',
                'Validation_Type': item.get('Validation_Type', ''),
                'Issue': self._format_issue_description(item),
                'Recommendation': self._get_recommendation(item)
            })

        print(f"   ✅ {len(action_items)}개 조치 항목 생성 완료")
        return action_items

    def _format_issue_description(self, item: dict) -> str:
        """Finding을 사람이 읽기 쉬운 형태로 포맷"""
        # Employee 정보
        if 'Employee' in item:
            prefix = f"{item['Employee']}: "
        elif 'Metric' in item:
            prefix = f"{item['Metric']}: "
        else:
            prefix = ""

        # 핵심 문제
        if 'Rule' in item:
            issue = item['Rule']
        elif 'Field' in item:
            issue = f"{item['Field']} 불일치"
        elif 'Type' in item:
            issue = f"{item.get('Type', '')} 오류"
        else:
            issue = "데이터 불일치"

        # 상세 정보
        details = []
        if 'Expected' in item or 'Expected_Amount' in item:
            expected = item.get('Expected', item.get('Expected_Amount', ''))
            details.append(f"Expected: {expected}")

        if 'Actual' in item or 'Actual_Amount' in item:
            actual = item.get('Actual', item.get('Actual_Amount', ''))
            details.append(f"Actual: {actual}")

        if 'CSV_Value' in item and 'Dashboard_Value' in item:
            details.append(f"CSV: {item['CSV_Value']}, Dashboard: {item['Dashboard_Value']}")

        detail_str = " | ".join(details) if details else ""

        return f"{prefix}{issue} ({detail_str})" if detail_str else f"{prefix}{issue}"

    def _get_recommendation(self, item: dict) -> str:
        """Finding에 대한 권장 조치 생성"""
        validation_type = item.get('Validation_Type', '')
        severity = item.get('Severity', '')

        # Validation 타입별 권장 조치
        if validation_type == 'Condition Evaluation':
            if '100%' in str(item.get('Rule', '')):
                return "step1_인센티브_계산_개선버전.py에서 100% 규칙 적용 로직 검토. pass_rate < 100인 경우 무조건 0 VND 적용 확인."
            elif 'attendancy' in str(item.get('Condition', '')).lower():
                return "출근 데이터 계산 로직 검토. attendance CSV와 config의 working_days 값 확인."
            elif 'aql' in str(item.get('Condition', '')).lower():
                return "AQL 데이터 처리 로직 검토. AQL history 파일과 계산 로직 일치 확인."

        elif validation_type == 'Incentive Amounts':
            if 'TYPE-1' in str(item.get('Type', '')):
                return "position_condition_matrix.json의 progression_table 확인. Continuous_Months 계산 로직 검토."
            elif 'TYPE-3' in str(item.get('Type', '')):
                return "TYPE-3는 무조건 0 VND. 계산 로직에서 TYPE-3 분기 확인."
            elif '연속 개월' in str(item.get('Rule', '')):
                return "assembly_inspector_continuous_months.json 업데이트 로직 검토. +1 증가 및 리셋 조건 확인."

        elif validation_type == 'Dashboard Consistency':
            if 'KPI' in str(item.get('Metric', '')):
                return "integrated_dashboard_final.py의 KPI 계산 로직 검토. CSV 직접 읽기 확인."
            elif 'Employee' in item:
                return "Dashboard HTML 생성 시 데이터 변환 로직 검토. NaN 처리 확인."

        # 기본 권장 조치
        if severity == 'CRITICAL':
            return "즉시 조치 필요. 데이터 정확성에 직접적 영향."
        elif severity == 'ERROR':
            return "빠른 시일 내 수정 필요. 보고서 신뢰성 영향."
        else:
            return "검토 필요. 데이터 품질 개선 기회."

    def generate_integrated_report(self, reports: dict):
        """통합 리포트 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.validation_reports_dir / f'INTEGRATED_VALIDATION_REPORT_{self.month}_{self.year}_{timestamp}.xlsx'

        print(f"\n📝 통합 리포트 생성 중: {report_file.name}")

        # Excel 작성
        with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
            # Sheet 1: Executive Summary
            summary_data = {
                '항목': [
                    '총 Validation 수',
                    '총 Findings',
                    'CRITICAL',
                    'ERROR',
                    'WARNING'
                ],
                '값': [
                    self.validation_summary.get('Total_Validations', 0),
                    self.validation_summary.get('Total_Findings', 0),
                    self.validation_summary.get('Critical', 0),
                    self.validation_summary.get('Error', 0),
                    self.validation_summary.get('Warning', 0)
                ]
            }

            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Executive Summary', index=False)

            # Sheet 2: Validation별 요약
            validation_details = []
            for validation_type, details in self.validation_summary.get('Validations_Details', {}).items():
                validation_details.append({
                    'Validation Type': validation_type,
                    'Total Errors': details.get('Total_Errors', 0),
                    'Critical Errors': details.get('Critical_Errors', 0)
                })

            if validation_details:
                df_validation = pd.DataFrame(validation_details)
                df_validation.to_excel(writer, sheet_name='Validation 요약', index=False)

            # Sheet 3: 모든 Findings (통합)
            if self.all_findings:
                df_all_findings = pd.DataFrame(self.all_findings)
                df_all_findings.to_excel(writer, sheet_name='모든 Findings', index=False)

            # Sheet 4: CRITICAL Findings
            critical_findings = [f for f in self.all_findings if f.get('Severity') == 'CRITICAL']
            if critical_findings:
                df_critical = pd.DataFrame(critical_findings)
                df_critical.to_excel(writer, sheet_name='CRITICAL Findings', index=False)

            # Sheet 5: ERROR Findings
            error_findings = [f for f in self.all_findings if f.get('Severity') == 'ERROR']
            if error_findings:
                df_error = pd.DataFrame(error_findings)
                df_error.to_excel(writer, sheet_name='ERROR Findings', index=False)

            # Sheet 6: WARNING Findings
            warning_findings = [f for f in self.all_findings if f.get('Severity') == 'WARNING']
            if warning_findings:
                df_warning = pd.DataFrame(warning_findings)
                df_warning.to_excel(writer, sheet_name='WARNING Findings', index=False)

            # Sheet 7: 우선순위 조치 항목
            action_items = self.generate_priority_action_items()
            if action_items:
                df_actions = pd.DataFrame(action_items)
                df_actions.to_excel(writer, sheet_name='조치 항목 (우선순위)', index=False)

            # Sheet 8: Validation별 상세 (각 리포트의 요약)
            validation_summaries = []
            for validation_type, excel_data in reports.items():
                if '요약' in excel_data:
                    df = excel_data['요약'].copy()
                    df['Validation_Type'] = validation_type
                    validation_summaries.append(df)

            if validation_summaries:
                df_validation_summary = pd.concat(validation_summaries, ignore_index=True)
                df_validation_summary.to_excel(writer, sheet_name='Validation 상세 요약', index=False)

        print(f"   ✅ 통합 리포트 저장 완료")
        return report_file

    def run(self, run_all_validations: bool = False):
        """통합 리포트 생성 실행"""
        print("="*80)
        print(f"📊 통합 검증 리포트 생성 - {self.year}년 {self.month}")
        print("="*80)

        # 옵션: 모든 검증 스크립트 실행
        if run_all_validations:
            self.run_all_validations()

        # 리포트 로드
        reports = self.load_validation_reports()

        if not reports:
            print("\n❌ 로드할 validation 리포트가 없습니다.")
            print("   --run-all 옵션으로 모든 검증을 먼저 실행하세요.")
            return False

        # Findings 통합
        self.aggregate_findings(reports)

        # Executive Summary 생성
        self.generate_executive_summary(reports)

        # 통합 리포트 생성
        report_file = self.generate_integrated_report(reports)

        # 결과 출력
        print("\n" + "="*80)
        print("📊 통합 리포트 생성 완료")
        print("="*80)
        print(f"📋 총 Validation 수: {self.validation_summary.get('Total_Validations', 0)}")
        print(f"🚨 총 Findings: {self.validation_summary.get('Total_Findings', 0)}건")
        print(f"   - CRITICAL: {self.validation_summary.get('Critical', 0)}건")
        print(f"   - ERROR: {self.validation_summary.get('Error', 0)}건")
        print(f"   - WARNING: {self.validation_summary.get('Warning', 0)}건")
        print(f"\n📄 통합 리포트: {report_file}")
        print("="*80)

        return len(self.all_findings) == 0


def main():
    parser = argparse.ArgumentParser(description='통합 검증 리포트 생성')
    parser.add_argument('month', help='월 (예: september)')
    parser.add_argument('year', type=int, help='년도 (예: 2025)')
    parser.add_argument('--run-all', action='store_true', help='모든 검증 스크립트 실행 후 통합')
    args = parser.parse_args()

    generator = IntegratedReportGenerator(args.month, args.year)
    success = generator.run(run_all_validations=args.run_all)

    # Exit code 설정
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
