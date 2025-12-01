#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대시보드-CSV 데이터 일치성 검증 스크립트
Dashboard와 Excel/CSV 파일의 데이터가 정확히 일치하는지 검증합니다.

Single Source of Truth 원칙:
- CSV 파일 = 유일한 데이터 소스
- Dashboard HTML = CSV에서 직접 생성
- 두 데이터는 100% 일치해야 함

실행 방법:
    python scripts/verification/validate_dashboard_consistency.py september 2025
"""

import pandas as pd
import json
import os
import re
from pathlib import Path
from datetime import datetime
import argparse
from bs4 import BeautifulSoup
import sys

class DashboardConsistencyValidator:
    """Dashboard-CSV 데이터 일치성 검증기"""

    def __init__(self, month: str, year: int):
        self.month = month
        self.year = year
        self.base_path = Path(__file__).parent.parent.parent
        self.errors = []
        self.warnings = []

        # 데이터 저장
        self.df_csv = None
        self.dashboard_data = None

    def load_csv_data(self):
        """CSV 데이터 로드"""
        # V9.1 → V9.0 → V8.02 순서로 확인 - 통일된 fallback 패턴 (2025-12-01)
        csv_file_v91 = self.base_path / 'output_files' / f'output_QIP_incentive_{self.month}_{self.year}_Complete_V9.1_Complete.csv'
        csv_file_v9 = self.base_path / 'output_files' / f'output_QIP_incentive_{self.month}_{self.year}_Complete_V9.0_Complete.csv'
        csv_file_v8 = self.base_path / 'output_files' / f'output_QIP_incentive_{self.month}_{self.year}_Complete_V8.02_Complete.csv'

        if csv_file_v91.exists():
            csv_file = csv_file_v91
        elif csv_file_v9.exists():
            csv_file = csv_file_v9
        elif csv_file_v8.exists():
            csv_file = csv_file_v8
        else:
            csv_file = csv_file_v91  # For error message

        if not csv_file.exists():
            print(f"❌ CSV 파일 없음: {csv_file}")
            return False

        print(f"\n📊 CSV 데이터 로드: {csv_file.name}")
        self.df_csv = pd.read_csv(csv_file, encoding='utf-8-sig')
        print(f"   ✅ {len(self.df_csv)}명의 직원 데이터 로드")

        return True

    def load_dashboard_html(self):
        """Dashboard HTML 파일 로드 및 데이터 추출"""
        # Dashboard 파일명 결정
        month_num = self._get_month_number(self.month)
        month_padded = f"{month_num:02d}"

        # Try V9.0 first, then fallback to V8.02 (버전 전환 호환성)
        dashboard_file_v9 = self.base_path / 'output_files' / f'Incentive_Dashboard_{self.year}_{month_padded}_Version_9.0.html'
        dashboard_file_v8 = self.base_path / 'output_files' / f'Incentive_Dashboard_{self.year}_{month_padded}_Version_8.02.html'

        if dashboard_file_v9.exists():
            dashboard_file = dashboard_file_v9
        elif dashboard_file_v8.exists():
            dashboard_file = dashboard_file_v8
        else:
            dashboard_file = dashboard_file_v9  # For error message

        if not dashboard_file.exists():
            print(f"❌ Dashboard HTML 없음: {dashboard_file}")
            return False

        print(f"\n📄 Dashboard HTML 로드: {dashboard_file.name}")

        # HTML 파일 읽기
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(html_content, 'html.parser')

        # JavaScript에서 dashboardData 추출
        script_tags = soup.find_all('script')

        dashboard_data_found = False
        for script in script_tags:
            if script.string and 'const dashboardData' in script.string:
                # dashboardData 객체 추출
                match = re.search(r'const dashboardData\s*=\s*({.*?});', script.string, re.DOTALL)
                if match:
                    dashboard_json_str = match.group(1)

                    # JavaScript 객체를 JSON으로 변환 (NaN 처리)
                    dashboard_json_str = dashboard_json_str.replace('NaN', 'null')

                    try:
                        self.dashboard_data = json.loads(dashboard_json_str)
                        dashboard_data_found = True
                        print(f"   ✅ Dashboard 데이터 추출 완료")
                        print(f"   📊 Dashboard 직원 수: {len(self.dashboard_data.get('employees', []))}명")
                        break
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️ JSON 파싱 오류: {e}")
                        continue

        if not dashboard_data_found:
            print("   ❌ Dashboard 데이터를 추출할 수 없습니다")
            return False

        return True

    def _get_month_number(self, month_name: str) -> int:
        """월 이름을 숫자로 변환"""
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return month_map.get(month_name.lower(), 1)

    def validate_kpi_summary(self):
        """KPI 요약 통계 검증"""
        print("\n🔍 KPI 요약 통계 검증 중...")

        errors = []

        # CSV 통계 계산
        csv_total_employees = len(self.df_csv)
        csv_incentive_recipients = len(self.df_csv[self.df_csv['Final Incentive amount'] > 0])
        csv_total_incentive = self.df_csv['Final Incentive amount'].sum()

        # Dashboard 통계 추출
        dashboard_employees = self.dashboard_data.get('employees', [])
        dashboard_total_employees = len(dashboard_employees)
        dashboard_incentive_recipients = len([e for e in dashboard_employees if e.get('Final Incentive amount', 0) > 0])
        dashboard_total_incentive = sum(e.get('Final Incentive amount', 0) for e in dashboard_employees)

        # 비교
        if csv_total_employees != dashboard_total_employees:
            errors.append({
                'Metric': 'Total Employees',
                'CSV_Value': csv_total_employees,
                'Dashboard_Value': dashboard_total_employees,
                'Difference': dashboard_total_employees - csv_total_employees,
                'Severity': 'CRITICAL'
            })

        if csv_incentive_recipients != dashboard_incentive_recipients:
            errors.append({
                'Metric': 'Incentive Recipients',
                'CSV_Value': csv_incentive_recipients,
                'Dashboard_Value': dashboard_incentive_recipients,
                'Difference': dashboard_incentive_recipients - csv_incentive_recipients,
                'Severity': 'CRITICAL'
            })

        if abs(csv_total_incentive - dashboard_total_incentive) > 1:
            errors.append({
                'Metric': 'Total Incentive Amount',
                'CSV_Value': f"{csv_total_incentive:,.0f} VND",
                'Dashboard_Value': f"{dashboard_total_incentive:,.0f} VND",
                'Difference': f"{dashboard_total_incentive - csv_total_incentive:,.0f} VND",
                'Severity': 'CRITICAL'
            })

        print(f"   ✅ KPI 검증 완료, {len(errors)}건 오류 발견")

        # 통계 출력
        print(f"\n   📊 CSV 통계:")
        print(f"      • 총 직원: {csv_total_employees:,}명")
        print(f"      • 인센티브 수령자: {csv_incentive_recipients:,}명")
        print(f"      • 총 인센티브: {csv_total_incentive:,.0f} VND")

        print(f"\n   📊 Dashboard 통계:")
        print(f"      • 총 직원: {dashboard_total_employees:,}명")
        print(f"      • 인센티브 수령자: {dashboard_incentive_recipients:,}명")
        print(f"      • 총 인센티브: {dashboard_total_incentive:,.0f} VND")

        return errors

    def validate_position_summary(self):
        """Position/TYPE별 요약 통계 검증"""
        print("\n🔍 Position/TYPE 요약 통계 검증 중...")

        errors = []

        # CSV Position 요약
        csv_type_summary = self.df_csv.groupby('Type').agg({
            'ID No': 'count',
            'Final Incentive amount': ['sum', lambda x: (x > 0).sum()]
        }).to_dict()

        # Dashboard Position 요약
        dashboard_employees = self.dashboard_data.get('employees', [])
        dashboard_type_counts = {}
        dashboard_type_incentives = {}
        dashboard_type_recipients = {}

        for emp in dashboard_employees:
            emp_type = emp.get('Type', 'Unknown')
            incentive = emp.get('Final Incentive amount', 0)

            dashboard_type_counts[emp_type] = dashboard_type_counts.get(emp_type, 0) + 1
            dashboard_type_incentives[emp_type] = dashboard_type_incentives.get(emp_type, 0) + incentive

            if incentive > 0:
                dashboard_type_recipients[emp_type] = dashboard_type_recipients.get(emp_type, 0) + 1

        # TYPE별 비교
        for emp_type in set(list(csv_type_summary.get(('ID No', 'count'), {}).keys()) + list(dashboard_type_counts.keys())):
            csv_count = len(self.df_csv[self.df_csv['Type'] == emp_type])
            dashboard_count = dashboard_type_counts.get(emp_type, 0)

            if csv_count != dashboard_count:
                errors.append({
                    'Type': emp_type,
                    'Metric': 'Employee Count',
                    'CSV_Value': csv_count,
                    'Dashboard_Value': dashboard_count,
                    'Severity': 'ERROR'
                })

        print(f"   ✅ Position/TYPE 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_employee_details_sample(self, sample_size: int = None):
        """개별 직원 데이터 전체 검증"""
        print(f"\n🔍 개별 직원 데이터 전체 검증 중...")

        errors = []

        # Dashboard 직원 데이터를 딕셔너리로 변환 (ID로 인덱싱)
        dashboard_employees = self.dashboard_data.get('employees', [])
        dashboard_dict = {str(emp.get('ID No', '')): emp for emp in dashboard_employees}

        # 주요 필드 검증
        critical_fields = [
            'Name', 'Position', 'Type',
            'conditions_pass_rate', 'Final Incentive amount',
            'Updated_Continuous_Months'
        ]

        checked_count = 0
        for idx, csv_row in self.df_csv.iterrows():
            emp_id = str(csv_row['ID No'])
            emp_name = csv_row.get('Name', '')

            # Dashboard에서 해당 직원 찾기
            dashboard_emp = dashboard_dict.get(emp_id)

            if not dashboard_emp:
                errors.append({
                    'Employee': f"{emp_name} ({emp_id})",
                    'Field': 'Employee Record',
                    'Issue': 'Dashboard에 해당 직원 없음',
                    'Severity': 'CRITICAL'
                })
                continue

            # 각 필드 비교
            for field in critical_fields:
                csv_value = csv_row.get(field)
                dashboard_value = dashboard_emp.get(field)

                # NaN 처리
                if pd.isna(csv_value):
                    csv_value = 0 if field in ['Final Incentive amount', 'conditions_pass_rate', 'Updated_Continuous_Months'] else ''
                if dashboard_value is None or (isinstance(dashboard_value, float) and pd.isna(dashboard_value)):
                    dashboard_value = 0 if field in ['Final Incentive amount', 'conditions_pass_rate', 'Updated_Continuous_Months'] else ''

                # 숫자 필드는 근사 비교 (소수점 오차 허용)
                if field in ['Final Incentive amount', 'conditions_pass_rate', 'Updated_Continuous_Months']:
                    if abs(float(csv_value) - float(dashboard_value)) > 1:
                        errors.append({
                            'Employee': f"{emp_name} ({emp_id})",
                            'Field': field,
                            'CSV_Value': f"{csv_value:,.2f}" if isinstance(csv_value, (int, float)) else str(csv_value),
                            'Dashboard_Value': f"{dashboard_value:,.2f}" if isinstance(dashboard_value, (int, float)) else str(dashboard_value),
                            'Severity': 'ERROR'
                        })
                else:
                    # 문자열 필드는 정확 비교
                    if str(csv_value).strip() != str(dashboard_value).strip():
                        errors.append({
                            'Employee': f"{emp_name} ({emp_id})",
                            'Field': field,
                            'CSV_Value': str(csv_value),
                            'Dashboard_Value': str(dashboard_value),
                            'Severity': 'WARNING'
                        })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_fields_sample(self, sample_size: int = None):
        """조건 평가 필드 전체 검증 (10개 조건)"""
        print(f"\n🔍 조건 평가 필드 전체 검증 중...")

        errors = []

        # Dashboard 직원 데이터를 딕셔너리로 변환
        dashboard_employees = self.dashboard_data.get('employees', [])
        dashboard_dict = {str(emp.get('ID No', '')): emp for emp in dashboard_employees}

        # 조건 필드 목록 (attendancy condition 1-4, AQL condition 5-8, 5PRS condition 9-10)
        condition_fields = [
            'attendancy condition 1 - attendance rate',
            'attendancy condition 2 - unapproved absence',
            'attendancy condition 3 - working day',
            'attendancy condition 4 - leaving early 3 times or more',
            'AQL condition 5 - personal failure',
            'AQL condition 6 - personal failure rate',
            'AQL condition 7 - team failure',
            'AQL condition 8 - consecutive failure 3 months',
            '5PRS condition 9 - rating 3',
            '5PRS condition 10 - PRS rating 4 or 5'
        ]

        checked_count = 0
        for idx, csv_row in self.df_csv.iterrows():
            emp_id = str(csv_row['ID No'])
            emp_name = csv_row.get('Name', '')

            dashboard_emp = dashboard_dict.get(emp_id)

            if not dashboard_emp:
                continue

            # 각 조건 필드 비교
            for field in condition_fields:
                csv_value = str(csv_row.get(field, '')).strip()
                dashboard_value = str(dashboard_emp.get(field, '')).strip()

                if csv_value != dashboard_value:
                    errors.append({
                        'Employee': f"{emp_name} ({emp_id})",
                        'Field': field,
                        'CSV_Value': csv_value,
                        'Dashboard_Value': dashboard_value,
                        'Severity': 'ERROR'
                    })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def generate_report(self, all_errors):
        """검증 리포트 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.base_path / 'validation_reports' / f'dashboard_consistency_report_{self.month}_{self.year}_{timestamp}.xlsx'

        print(f"\n📝 리포트 생성 중: {report_file.name}")

        # Excel 작성
        with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
            # Sheet 1: 요약
            kpi_errors = [e for e in all_errors if e.get('Metric') in ['Total Employees', 'Incentive Recipients', 'Total Incentive Amount']]
            position_errors = [e for e in all_errors if e.get('Type') and e.get('Metric')]
            employee_errors = [e for e in all_errors if e.get('Employee') and e.get('Field')]
            condition_errors = [e for e in all_errors if 'condition' in e.get('Field', '').lower()]

            summary_data = {
                '검증 항목': [
                    'KPI 요약 통계',
                    'Position/TYPE 요약',
                    '개별 직원 데이터',
                    '조건 평가 필드',
                    '총계'
                ],
                '오류 건수': [
                    len(kpi_errors),
                    len(position_errors),
                    len(employee_errors),
                    len(condition_errors),
                    len(all_errors)
                ],
                'Critical': [
                    len([e for e in kpi_errors if e.get('Severity') == 'CRITICAL']),
                    len([e for e in position_errors if e.get('Severity') == 'CRITICAL']),
                    len([e for e in employee_errors if e.get('Severity') == 'CRITICAL']),
                    len([e for e in condition_errors if e.get('Severity') == 'CRITICAL']),
                    len([e for e in all_errors if e.get('Severity') == 'CRITICAL'])
                ]
            }

            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='요약', index=False)

            # Sheet 2: 상세 오류
            if all_errors:
                df_errors = pd.DataFrame(all_errors)
                df_errors.to_excel(writer, sheet_name='상세 오류', index=False)

            # Sheet 3: KPI 오류
            if kpi_errors:
                df_kpi = pd.DataFrame(kpi_errors)
                df_kpi.to_excel(writer, sheet_name='KPI 오류', index=False)

            # Sheet 4: Position 오류
            if position_errors:
                df_position = pd.DataFrame(position_errors)
                df_position.to_excel(writer, sheet_name='Position 오류', index=False)

            # Sheet 5: 직원 데이터 오류
            if employee_errors:
                df_employee = pd.DataFrame(employee_errors)
                df_employee.to_excel(writer, sheet_name='직원 데이터 오류', index=False)

            # Sheet 6: 조건 필드 오류
            if condition_errors:
                df_condition = pd.DataFrame(condition_errors)
                df_condition.to_excel(writer, sheet_name='조건 필드 오류', index=False)

        print(f"   ✅ 리포트 저장 완료")
        return report_file

    def run_validation(self):
        """전체 검증 실행"""
        print("="*80)
        print(f"📊 Dashboard-CSV 데이터 일치성 검증 - {self.year}년 {self.month}")
        print("="*80)

        # 데이터 로드
        if not self.load_csv_data():
            return False

        if not self.load_dashboard_html():
            return False

        # 검증 실행
        all_errors = []

        # KPI 요약 통계
        all_errors.extend(self.validate_kpi_summary())

        # Position/TYPE 요약
        all_errors.extend(self.validate_position_summary())

        # 개별 직원 데이터 전체 검증
        all_errors.extend(self.validate_employee_details_sample())

        # 조건 평가 필드 전체 검증
        all_errors.extend(self.validate_condition_fields_sample())

        # 리포트 생성
        report_file = self.generate_report(all_errors)

        # 결과 출력
        print("\n" + "="*80)
        print("📊 검증 결과 요약")
        print("="*80)
        print(f"✅ 검증 완료: {self.year}년 {self.month}")
        print(f"📋 CSV 직원 수: {len(self.df_csv)}명")
        print(f"📋 Dashboard 직원 수: {len(self.dashboard_data.get('employees', []))}명")
        print(f"🚨 발견된 오류: {len(all_errors)}건")
        print(f"   - CRITICAL: {len([e for e in all_errors if e.get('Severity') == 'CRITICAL'])}건")
        print(f"   - ERROR: {len([e for e in all_errors if e.get('Severity') == 'ERROR'])}건")
        print(f"   - WARNING: {len([e for e in all_errors if e.get('Severity') == 'WARNING'])}건")
        print(f"\n📄 상세 리포트: {report_file}")
        print("="*80)

        return len(all_errors) == 0


def main():
    parser = argparse.ArgumentParser(description='Dashboard-CSV 데이터 일치성 검증')
    parser.add_argument('month', help='월 (예: september)')
    parser.add_argument('year', type=int, help='년도 (예: 2025)')
    args = parser.parse_args()

    validator = DashboardConsistencyValidator(args.month, args.year)
    success = validator.run_validation()

    # Exit code 설정
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
