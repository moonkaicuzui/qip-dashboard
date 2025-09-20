#!/usr/bin/env python3
"""
Excel 기반 대시보드 통합 시스템
모든 대시보드 데이터를 Excel 파일에서 읽어오도록 통합
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
import os

class ExcelBasedDashboardSystem:
    """Excel 파일을 단일 진실 소스로 사용하는 대시보드 시스템"""

    def __init__(self, excel_path, attendance_path):
        """
        Args:
            excel_path: 인센티브 Excel 파일 경로
            attendance_path: 출근 데이터 CSV 파일 경로
        """
        self.excel_path = excel_path
        self.attendance_path = attendance_path
        self.df = None
        self.attendance_df = None
        self.daily_attendance = {}

    def load_data(self):
        """Excel과 출근 데이터 로드"""
        # Excel 데이터 로드
        if self.excel_path.endswith('.csv'):
            self.df = pd.read_csv(self.excel_path)
        else:
            self.df = pd.read_excel(self.excel_path)

        # 출근 데이터 로드
        self.attendance_df = pd.read_csv(self.attendance_path)

        print(f"✅ Excel 데이터 로드: {len(self.df)}개 레코드")
        print(f"✅ 출근 데이터 로드: {len(self.attendance_df)}개 레코드")

    def analyze_working_days(self):
        """실제 근무일 분석"""
        # 출근 데이터에서 유니크한 날짜 추출
        self.attendance_df['Work Date'] = pd.to_datetime(
            self.attendance_df['Work Date'],
            format='%Y.%m.%d'
        )

        # 9월 데이터만 필터링
        september_data = self.attendance_df[
            self.attendance_df['Work Date'].dt.month == 9
        ]

        # 일별 출근 인원 계산
        daily_counts = september_data.groupby('Work Date').size()

        # 유니크한 근무일
        unique_dates = sorted(september_data['Work Date'].unique())

        print("\n📅 2025년 9월 실제 근무일 분석:")
        print(f"  • 총 근무일수: {len(unique_dates)}일")
        print(f"  • 근무일 목록: {[d.day for d in unique_dates]}")

        # 일별 출근 데이터 저장
        for date in unique_dates:
            day = date.day
            count = daily_counts[date]
            self.daily_attendance[day] = {
                'date': date.strftime('%Y-%m-%d'),
                'day': day,
                'count': int(count),
                'is_working_day': True
            }

        # 비근무일 추가 (1-19일 중 근무일이 아닌 날)
        for day in range(1, 20):
            if day not in [d.day for d in unique_dates]:
                self.daily_attendance[day] = {
                    'date': f'2025-09-{day:02d}',
                    'day': day,
                    'count': 0,
                    'is_working_day': False
                }

        return self.daily_attendance

    def add_daily_attendance_to_excel(self):
        """일별 출근 데이터를 Excel에 추가"""
        # 각 날짜별로 컬럼 추가
        for day in range(1, 20):
            col_name = f'Day_{day:02d}_Attendance'
            if day in self.daily_attendance:
                if self.daily_attendance[day]['is_working_day']:
                    self.df[col_name] = 'WORK'
                else:
                    self.df[col_name] = 'HOLIDAY'
            else:
                self.df[col_name] = 'NO_DATA'

        # 실제 총 근무일수 계산 (출근 데이터 기반)
        actual_working_days = len([d for d in self.daily_attendance.values()
                                  if d['is_working_day']])
        self.df['Actual_Total_Working_Days'] = actual_working_days

        print(f"\n✅ 일별 출근 데이터를 Excel에 추가했습니다:")
        print(f"  • Day_01_Attendance ~ Day_19_Attendance 컬럼 추가")
        print(f"  • Actual_Total_Working_Days: {actual_working_days}일")

    def generate_dashboard_data_json(self):
        """대시보드용 JSON 데이터 생성"""
        dashboard_data = {
            'generated_at': datetime.now().isoformat(),
            'data_source': 'Excel File (Single Source of Truth)',
            'total_records': len(self.df),

            # 요약 데이터
            'summary': {
                'total_employees': len(self.df),
                'employees_with_incentive': len(self.df[self.df['September_Incentive'] > 0]),
                'total_incentive_amount': float(self.df['September_Incentive'].sum()),
                'average_incentive': float(self.df[self.df['September_Incentive'] > 0]['September_Incentive'].mean()) if len(self.df[self.df['September_Incentive'] > 0]) > 0 else 0
            },

            # 출근 데이터 (실제 데이터 기반)
            'attendance': {
                'total_working_days': len([d for d in self.daily_attendance.values() if d['is_working_day']]),
                'daily_data': self.daily_attendance,
                'working_days_list': sorted([d['day'] for d in self.daily_attendance.values() if d['is_working_day']]),
                'holiday_list': sorted([d['day'] for d in self.daily_attendance.values() if not d['is_working_day']])
            },

            # KPI 데이터 (Excel 기반)
            'kpi_metrics': {
                'total_working_days': len([d for d in self.daily_attendance.values() if d['is_working_day']]),
                'absent_without_inform': len(self.df[self.df['Unapproved Absences'] >= 1]),
                'zero_working_days': len(self.df[self.df['Actual Working Days'] == 0]),
                'minimum_days_not_met': len(self.df[
                    (self.df['Actual Working Days'] > 0) &
                    (self.df['Actual Working Days'] < 12)  # 20일 이후 기준
                ]),
                'aql_fail': len(self.df[self.df['September AQL Failures'] > 0]),
                'continuous_aql_fail': len(self.df[self.df['Continuous_FAIL'] == 'YES']),
                'area_reject_rate': len(self.df[self.df['Area_Reject_Rate'] > 3]),
                'low_5prs_pass_rate': len(self.df[
                    (self.df['5PRS_Pass_Rate'] < 95) &
                    (self.df['5PRS_Pass_Rate'] > 0)
                ]),
                'low_5prs_inspection_qty': len(self.df[self.df['5PRS_Inspection_Qty'] < 100])
            },

            # 모달용 상세 데이터
            'modal_data': {
                'zero_working_days_employees': self.df[
                    self.df['Actual Working Days'] == 0
                ][['Employee No', 'Full Name', 'QIP POSITION 1ST  NAME', 'Stop working Date']].to_dict('records'),

                'absent_without_inform_employees': self.df[
                    self.df['Unapproved Absences'] >= 1
                ][['Employee No', 'Full Name', 'QIP POSITION 1ST  NAME', 'Unapproved Absences']].to_dict('records'),

                'minimum_days_not_met_employees': self.df[
                    (self.df['Actual Working Days'] > 0) &
                    (self.df['Actual Working Days'] < 12)
                ][['Employee No', 'Full Name', 'QIP POSITION 1ST  NAME', 'Actual Working Days']].to_dict('records')
            },

            # 전체 직원 데이터
            'employee_data': self.df.to_dict('records')
        }

        # JSON 파일로 저장
        output_path = 'output_files/dashboard_data_from_excel.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n✅ 대시보드 데이터 JSON 생성 완료: {output_path}")
        print(f"  • 총 직원: {dashboard_data['summary']['total_employees']}명")
        print(f"  • 인센티브 수령: {dashboard_data['summary']['employees_with_incentive']}명")
        print(f"  • 실제 총 근무일: {dashboard_data['attendance']['total_working_days']}일")

        return dashboard_data

    def validate_data_consistency(self):
        """데이터 일관성 검증"""
        issues = []

        # 1. Total Working Days 일관성 체크
        excel_working_days = self.df['Total Working Days'].iloc[0] if 'Total Working Days' in self.df.columns else None
        actual_working_days = len([d for d in self.daily_attendance.values() if d['is_working_day']])

        if excel_working_days and excel_working_days != actual_working_days:
            issues.append({
                'type': 'INCONSISTENCY',
                'field': 'Total Working Days',
                'excel_value': excel_working_days,
                'actual_value': actual_working_days,
                'message': f'Excel의 Total Working Days({excel_working_days})와 실제 출근 데이터({actual_working_days})가 일치하지 않습니다.'
            })

        # 2. 0일 근무자 검증
        zero_workers_count = len(self.df[self.df['Actual Working Days'] == 0])
        print(f"\n🔍 데이터 검증:")
        print(f"  • 0일 근무자: {zero_workers_count}명")

        # 3. 무단결근 검증
        absent_workers = len(self.df[self.df['Unapproved Absence Days'] >= 1])
        print(f"  • 무단결근자 (1일 이상): {absent_workers}명")

        if issues:
            print("\n⚠️ 데이터 일관성 문제 발견:")
            for issue in issues:
                print(f"  • {issue['message']}")
        else:
            print("\n✅ 데이터 일관성 검증 통과")

        return issues

    def save_enhanced_excel(self):
        """개선된 Excel 파일 저장"""
        output_path = self.excel_path.replace('.csv', '_enhanced.csv')
        self.df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"\n✅ 개선된 Excel 파일 저장: {output_path}")
        print(f"  • 일별 출근 데이터 추가됨")
        print(f"  • 실제 총 근무일수 컬럼 추가됨")

        return output_path


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("📊 Excel 기반 대시보드 통합 시스템")
    print("=" * 60)

    # 파일 경로 설정
    excel_path = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
    attendance_path = 'input_files/attendance/converted/attendance data september_converted.csv'

    # 시스템 초기화
    system = ExcelBasedDashboardSystem(excel_path, attendance_path)

    # 데이터 로드
    system.load_data()

    # 실제 근무일 분석
    system.analyze_working_days()

    # Excel에 일별 데이터 추가
    system.add_daily_attendance_to_excel()

    # 대시보드 JSON 생성
    dashboard_data = system.generate_dashboard_data_json()

    # 데이터 일관성 검증
    system.validate_data_consistency()

    # 개선된 Excel 저장
    system.save_enhanced_excel()

    print("\n" + "=" * 60)
    print("✅ Excel 기반 대시보드 시스템 구축 완료!")
    print("=" * 60)

    return dashboard_data


if __name__ == "__main__":
    main()