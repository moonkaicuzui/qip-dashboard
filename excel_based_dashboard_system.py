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
        """실제 근무일 분석 (출산휴가자 전용 날짜 제외)"""
        # 출근 데이터에서 유니크한 날짜 추출
        self.attendance_df['Work Date'] = pd.to_datetime(
            self.attendance_df['Work Date'],
            format='%Y.%m.%d'
        )

        # 9월 데이터만 필터링
        september_data = self.attendance_df[
            self.attendance_df['Work Date'].dt.month == 9
        ]

        # compAdd가 'Đi làm' (출근)인 데이터만 필터링
        actual_attendance = september_data[september_data['compAdd'] == 'Đi làm']

        # 출산휴가자만 있는 날짜 확인
        maternity_only_data = september_data[
            (september_data['compAdd'] == 'Vắng mặt') &
            (september_data['Reason Description'].str.contains('Sinh thường', na=False))
        ]

        # 실제 출근자가 있는 날짜만 근무일로 설정
        actual_working_dates = sorted(actual_attendance['Work Date'].unique())
        all_dates = sorted(september_data['Work Date'].unique())
        maternity_only_dates = []

        # 각 날짜별로 실제 출근자 수 계산
        for date in all_dates:
            date_data = september_data[september_data['Work Date'] == date]
            actual_workers = len(date_data[date_data['compAdd'] == 'Đi làm'])
            maternity_only = len(date_data[
                (date_data['compAdd'] == 'Vắng mặt') &
                (date_data['Reason Description'].str.contains('Sinh thường', na=False))
            ])

            day = date.day

            # 실제 출근자가 있으면 근무일, 출산휴가자만 있으면 비근무일
            is_working = actual_workers > 0

            if not is_working and maternity_only > 0:
                maternity_only_dates.append(day)

            self.daily_attendance[day] = {
                'date': date.strftime('%Y-%m-%d'),
                'day': day,
                'actual_workers': actual_workers,
                'maternity_leave': maternity_only,
                'total_records': len(date_data),
                'is_working_day': is_working,
                'is_maternity_only': not is_working and maternity_only > 0
            }

        # 비근무일 추가 (1-19일 중 데이터가 없는 날)
        for day in range(1, 20):
            if day not in [d.day for d in all_dates]:
                self.daily_attendance[day] = {
                    'date': f'2025-09-{day:02d}',
                    'day': day,
                    'actual_workers': 0,
                    'maternity_leave': 0,
                    'total_records': 0,
                    'is_working_day': False,
                    'is_maternity_only': False
                }

        # 실제 근무일수 (출산휴가자만 있는 날 제외)
        actual_working_days = len([d for d in self.daily_attendance.values()
                                  if d['is_working_day']])

        print("\n📅 2025년 9월 실제 근무일 분석 (개선된 로직):")
        print(f"  • 원래 기록상 날짜: {len(all_dates)}일")
        print(f"  • 출산휴가자만 있는 날: {maternity_only_dates}")
        print(f"  • 실제 근무일수: {actual_working_days}일 (출산휴가 전용일 제외)")
        print(f"  • 근무일 목록: {[d['day'] for d in self.daily_attendance.values() if d['is_working_day']]}")

        return self.daily_attendance

    def add_daily_attendance_to_excel(self):
        """일별 출근 데이터를 Excel에 추가"""
        # 각 날짜별로 컬러 추가
        for day in range(1, 20):
            col_name = f'Day_{day:02d}_Attendance'
            if day in self.daily_attendance:
                if self.daily_attendance[day]['is_working_day']:
                    self.df[col_name] = 'WORK'
                elif self.daily_attendance[day]['is_maternity_only']:
                    self.df[col_name] = 'MATERNITY_ONLY'
                else:
                    self.df[col_name] = 'HOLIDAY'
            else:
                self.df[col_name] = 'NO_DATA'

        # 실제 총 근무일수 계산 (출근 데이터 기반, 출산휴가자만 있는 날 제외)
        actual_working_days = len([d for d in self.daily_attendance.values()
                                  if d['is_working_day']])
        self.df['Actual_Total_Working_Days'] = actual_working_days

        # 출산휴가자 전용일을 제외한 총 근무일수
        self.df['Adjusted_Total_Working_Days'] = actual_working_days

        # 각 직원의 출근율 재계산 (조정된 총 근무일 기준)
        if 'Actual Working Days' in self.df.columns:
            self.df['Adjusted_Attendance_Rate'] = (
                self.df['Actual Working Days'] / actual_working_days * 100
            ).fillna(0).round(1)

        # 최소 근무일 계산 (Single Source of Truth) - 고정 12일 기준
        current_day = datetime.now().day
        if current_day < 20:
            # 중간 보고서: 최소 7일
            minimum_days_required = 7
        else:
            # 최종 보고서: 최소 12일 (고정 기준)
            minimum_days_required = 12

        # 최소 근무일 충족 여부 계산
        self.df['Minimum_Working_Days_Required'] = minimum_days_required
        self.df['Minimum_Days_Met'] = self.df['Actual Working Days'] >= minimum_days_required

        # 부족 일수 계산 (0보다 작으면 0으로)
        self.df['Minimum_Days_Shortage'] = (minimum_days_required - self.df['Actual Working Days']).clip(lower=0)

        print(f"\n✅ 일별 출근 데이터를 Excel에 추가했습니다:")
        print(f"  • Day_01_Attendance ~ Day_19_Attendance 컬럼 추가")
        print(f"  • WORK: 실제 근무일, MATERNITY_ONLY: 출산휴가자만 있는 날, HOLIDAY: 휴일")
        print(f"  • Actual_Total_Working_Days: {actual_working_days}일 (출산휴가 전용일 제외)")
        print(f"  • Adjusted_Attendance_Rate: 조정된 출근율 추가")
        print(f"  • Minimum_Working_Days_Required: {minimum_days_required}일 (고정 기준)")
        print(f"  • Minimum_Days_Met: 최소 근무일 충족 여부")

    def add_filtering_columns(self):
        """Excel에 필터링 정보 컬럼 추가 (Single Source of Truth)"""
        # Stop working Date를 datetime으로 변환
        self.df['Stop working Date'] = pd.to_datetime(self.df['Stop working Date'], errors='coerce')

        # 현재 기준일 설정 (9월 19일 기준)
        reference_date = pd.Timestamp('2025-09-19')
        month_start = pd.Timestamp('2025-09-01')

        # 1. 퇴사/계약종료 구분
        self.df['Stop_Working_Type'] = self.df['Stop working Date'].apply(
            lambda x: 'resigned' if pd.notna(x) and x <= reference_date
                     else 'contract_end' if pd.notna(x) and x > reference_date
                     else 'active'
        )

        # 2. 9월 활성 직원 표시 (대시보드 포함 여부)
        self.df['September_Active'] = self.df.apply(
            lambda row: True if (
                pd.isna(row['Stop working Date']) or
                row['Stop working Date'] >= month_start
            ) else False,
            axis=1
        )

        # 3. 대시보드 포함 여부 (명시적 컬럼)
        self.df['Include_In_Dashboard'] = self.df['September_Active']

        # 4. 제외 사유 기록
        self.df['Exclusion_Reason'] = self.df.apply(
            lambda row: '' if row['September_Active']
            else '9월 이전 퇴사' if pd.notna(row['Stop working Date'])
                 and row['Stop working Date'] < month_start
            else '기타 사유',
            axis=1
        )

        # 5. 통계 출력
        total_employees = len(self.df)
        active_employees = self.df['September_Active'].sum()
        excluded_employees = total_employees - active_employees

        print(f"\n✅ 필터링 정보를 Excel에 추가했습니다:")
        print(f"  • 전체 직원: {total_employees}명")
        print(f"  • 9월 활성 직원: {active_employees}명")
        print(f"  • 제외된 직원: {excluded_employees}명")

        # 제외 사유별 통계
        exclusion_stats = self.df[self.df['September_Active'] == False]['Exclusion_Reason'].value_counts()
        if not exclusion_stats.empty:
            print(f"\n  제외 사유 상세:")
            for reason, count in exclusion_stats.items():
                print(f"    - {reason}: {count}명")

    def generate_dashboard_data_json(self):
        """대시보드용 JSON 데이터 생성"""
        # Excel의 필터링 컬럼을 기준으로 활성 직원만 선택 (Single Source of Truth)
        df_active = self.df.copy()

        # Include_In_Dashboard 컬럼이 있으면 사용, 없으면 기존 로직 사용 (하위 호환성)
        if 'Include_In_Dashboard' in df_active.columns:
            # Excel의 명시적 필터링 정보 사용
            df_active = df_active[df_active['Include_In_Dashboard'] == True]
            print(f"\n📊 Excel 필터링 컬럼 사용: Include_In_Dashboard")
        elif 'September_Active' in df_active.columns:
            # September_Active 컬럼 사용
            df_active = df_active[df_active['September_Active'] == True]
            print(f"\n📊 Excel 필터링 컬럼 사용: September_Active")
        else:
            # 기존 필터링 로직 (하위 호환성)
            print(f"\n⚠️ 필터링 컬럼이 없어 기존 로직 사용")
            if 'Stop working Date' in df_active.columns:
                df_active['Stop working Date'] = pd.to_datetime(df_active['Stop working Date'], errors='coerce')
                df_active = df_active[
                    (df_active['Stop working Date'].isna()) |  # 재직자
                    (df_active['Stop working Date'] >= '2025-09-01')  # 9월 이후 퇴사
                ]

        dashboard_data = {
            'generated_at': datetime.now().isoformat(),
            'data_source': 'Excel File (Single Source of Truth)',
            'total_records': len(df_active),  # 9월 재직자 수

            # 요약 데이터
            'summary': {
                'total_employees': len(df_active),  # 9월 재직자
                'employees_with_incentive': len(df_active[df_active['September_Incentive'] > 0]),
                'total_incentive_amount': float(df_active['September_Incentive'].sum()),
                'average_incentive': float(df_active[df_active['September_Incentive'] > 0]['September_Incentive'].mean()) if len(df_active[df_active['September_Incentive'] > 0]) > 0 else 0
            },

            # 출근 데이터 (실제 데이터 기반)
            'attendance': {
                'total_working_days': len([d for d in self.daily_attendance.values() if d['is_working_day']]),
                'daily_data': self.daily_attendance,
                'working_days_list': sorted([d['day'] for d in self.daily_attendance.values() if d['is_working_day']]),
                'holiday_list': sorted([d['day'] for d in self.daily_attendance.values() if not d['is_working_day']])
            },

            # KPI 데이터 (Excel 기반 - 9월 재직자만)
            'kpi_metrics': {
                'total_working_days': len([d for d in self.daily_attendance.values() if d['is_working_day']]),
                'adjusted_total_days': len([d for d in self.daily_attendance.values() if d['is_working_day']]),  # 출산호가 전용일 제외
                'absent_without_inform': len(df_active[df_active['Unapproved Absences'] >= 1]),
                'zero_working_days': len(df_active[df_active['Actual Working Days'] == 0]),
                'minimum_days_not_met': len(df_active[
                    df_active['Minimum_Days_Met'] == False
                ]),
                'attendance_below_88': len(df_active[
                    df_active.get('Adjusted_Attendance_Rate', df_active.get('attendance_rate', 0)) < 88
                ]),
                'aql_fail': len(df_active[df_active['September AQL Failures'] > 0]),
                'continuous_aql_fail': len(df_active[df_active['Continuous_FAIL'] == 'YES']),
                'area_reject_rate': len(df_active[df_active['Area_Reject_Rate'] > 3]),
                'low_5prs_pass_rate': len(df_active[
                    (df_active['5PRS_Pass_Rate'] < 95) &
                    (df_active['5PRS_Pass_Rate'] > 0)
                ]),
                'low_5prs_inspection_qty': len(df_active[df_active['5PRS_Inspection_Qty'] < 100])
            },

            # 모달용 상세 데이터 (9월 재직자만)
            'modal_data': {
                'zero_working_days_employees': df_active[
                    df_active['Actual Working Days'] == 0
                ][['Employee No', 'Full Name', 'FINAL QIP POSITION NAME CODE', 'Total Working Days', 'Actual Working Days', 'Stop working Date', 'Stop_Working_Type']].fillna('').to_dict('records'),

                'absent_without_inform_employees': df_active[
                    df_active['Unapproved Absences'] >= 1
                ][['Employee No', 'Full Name', 'FINAL QIP POSITION NAME CODE', 'Unapproved Absences']].fillna('').to_dict('records'),

                'minimum_days_not_met_employees': df_active[
                    df_active['Minimum_Days_Met'] == False
                ][['Employee No', 'Full Name', 'FINAL QIP POSITION NAME CODE', 'Actual Working Days', 'Minimum_Working_Days_Required', 'Minimum_Days_Shortage']].fillna('').to_dict('records')
            },

            # 전체 직원 데이터 (9월 재직자만) - NaN/NaT를 문자열로 변환
            'employee_data': df_active.fillna('').to_dict('records')
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
        if 'Unapproved Absences' in self.df.columns:
            absent_workers = len(self.df[self.df['Unapproved Absences'] >= 1])
            print(f"  • 무단결근자 (1일 이상): {absent_workers}명")
        elif 'Unapproved Absence Days' in self.df.columns:
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

    # Excel에 필터링 컬럼 추가 (Single Source of Truth)
    system.add_filtering_columns()

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