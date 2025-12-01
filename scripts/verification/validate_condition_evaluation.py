#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조건 평가 정확성 검증 스크립트
10개 조건(1-10)이 데이터 소스 기반으로 정확히 평가되었는지 검증합니다.

실행 방법:
    python scripts/verification/validate_condition_evaluation.py september 2025
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import PatternFill, Font
import argparse

class ConditionEvaluationValidator:
    """조건 평가 정확성 검증기"""

    def __init__(self, month: str, year: int):
        self.month = month
        self.year = year
        self.month_num = self._get_month_number(month)
        self.base_path = Path(__file__).parent.parent.parent
        self.errors = []
        self.warnings = []

        # 파일 경로 설정
        self.config_path = self.base_path / 'config_files' / f'config_{month}_{year}.json'
        self.output_csv = None
        self.config = None

        # 데이터 소스
        self.df_output = None  # 계산 결과 CSV
        self.df_attendance = None
        self.df_aql = None
        self.df_5prs = None
        self.df_basic = None

    def _get_month_number(self, month: str) -> int:
        """월 이름을 숫자로 변환"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month.lower(), 0)

    def load_config(self):
        """Config 파일 로드"""
        print(f"📂 Config 로드: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        print(f"   ✅ Working days: {self.config.get('working_days')} days")
        return True

    def load_output_data(self):
        """계산 결과 CSV 로드"""
        # V9.1 → V9.0 → V8.02 순서로 확인 - 통일된 fallback 패턴 (2025-12-01)
        output_file_v91 = self.base_path / 'output_files' / f'output_QIP_incentive_{self.month}_{self.year}_Complete_V9.1_Complete.csv'
        output_file_v9 = self.base_path / 'output_files' / f'output_QIP_incentive_{self.month}_{self.year}_Complete_V9.0_Complete.csv'
        output_file_v8 = self.base_path / 'output_files' / f'output_QIP_incentive_{self.month}_{self.year}_Complete_V8.02_Complete.csv'

        if output_file_v91.exists():
            output_file = output_file_v91
        elif output_file_v9.exists():
            output_file = output_file_v9
        elif output_file_v8.exists():
            output_file = output_file_v8
        else:
            output_file = output_file_v91  # For error message

        if not output_file.exists():
            print(f"❌ 출력 파일 없음: {output_file}")
            print(f"   먼저 인센티브 계산을 실행하세요:")
            print(f"   python src/step1_인센티브_계산_개선버전.py --config {self.config_path}")
            return False

        print(f"📊 출력 CSV 로드: {output_file}")
        self.df_output = pd.read_csv(output_file, encoding='utf-8-sig')
        print(f"   ✅ {len(self.df_output)}명의 직원 데이터 로드")

        # 필수 컬럼 확인
        required_cols = [
            'ID No', 'Name', 'Final Incentive amount', 'conditions_pass_rate',
            'attendancy condition 1 - attendance rate',
            'attendancy condition 2 - unapproved absence',
            'attendancy condition 3 - actual working days',
            'attendancy condition 4 - minimum working days'
        ]

        missing_cols = [col for col in required_cols if col not in self.df_output.columns]
        if missing_cols:
            print(f"⚠️ 누락된 컬럼: {missing_cols}")

        return True

    def load_source_data(self):
        """원본 데이터 소스 로드"""
        file_paths = self.config.get('file_paths', {})

        # Attendance 데이터
        attendance_path = self.base_path / file_paths.get('attendance', '')
        if attendance_path.exists():
            print(f"📅 Attendance 로드: {attendance_path.name}")
            self.df_attendance = pd.read_csv(attendance_path, encoding='utf-8-sig')
            print(f"   ✅ {len(self.df_attendance)} 출근 기록")
        else:
            print(f"⚠️ Attendance 파일 없음")

        # AQL 데이터
        aql_path = self.base_path / file_paths.get('aql', '')
        if aql_path.exists():
            print(f"🔍 AQL 로드: {aql_path.name}")
            self.df_aql = pd.read_csv(aql_path, encoding='utf-8-sig')
            print(f"   ✅ {len(self.df_aql)} AQL 기록")
        else:
            print(f"⚠️ AQL 파일 없음")

        # 5PRS 데이터
        prs_path = self.base_path / file_paths.get('5prs', '')
        if prs_path.exists():
            print(f"📋 5PRS 로드: {prs_path.name}")
            self.df_5prs = pd.read_csv(prs_path, encoding='utf-8-sig')
            print(f"   ✅ {len(self.df_5prs)} 5PRS 기록")
        else:
            print(f"⚠️ 5PRS 파일 없음")

        # Basic 데이터
        basic_path = self.base_path / file_paths.get('basic', '')
        if basic_path.exists():
            print(f"👤 Basic 로드: {basic_path.name}")
            self.df_basic = pd.read_csv(basic_path, encoding='utf-8-sig')
            print(f"   ✅ {len(self.df_basic)} 직원 기본 정보")
        else:
            print(f"⚠️ Basic 파일 없음")

        return True

    def validate_condition_1_attendance_rate(self):
        """조건 1: 출근율 >= 88% 검증"""
        print("\n🔍 조건 1: 출근율 >= 88% 검증 중...")

        if self.df_attendance is None:
            print("   ⚠️ Attendance 데이터 없음, 건너뜀")
            return []

        errors = []
        working_days = self.config.get('working_days', 23)

        # ID No 컬럼 찾기
        id_col = None
        for col in ['ID No', 'ID', 'Employee No', 'Emp No']:
            if col in self.df_attendance.columns:
                id_col = col
                break

        if not id_col:
            print(f"   ❌ ID 컬럼을 찾을 수 없음")
            return errors

        # 직원별 실제 출근일 계산
        attendance_counts = self.df_attendance.groupby(id_col).size().to_dict()

        # 전체 직원 검증
        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])
            actual_days = attendance_counts.get(emp_id, 0)
            attendance_rate = (actual_days / working_days) * 100 if working_days > 0 else 0

            expected = 'YES' if attendance_rate >= 88 else 'NO'
            actual = row.get('attendancy condition 1 - attendance rate', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 1 (출근율)',
                    'Expected': expected,
                    'Actual': actual,
                    'Calculated_Rate': f"{attendance_rate:.2f}%",
                    'Actual_Days': actual_days,
                    'Working_Days': working_days,
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_2_unapproved_absence(self):
        """조건 2: 무단결근 <= 2일 검증"""
        print("\n🔍 조건 2: 무단결근 <= 2일 검증 중...")

        errors = []

        # Excel 출력 파일에 이미 계산된 Unapproved Absences 컬럼 사용
        if 'Unapproved Absences' not in self.df_output.columns:
            print("   ⚠️ 'Unapproved Absences' 컬럼 없음, 건너뜀")
            return errors

        # 전체 직원 검증
        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])
            unapproved_days = row.get('Unapproved Absences', 0)

            # 조건 2: 무단결근 <= 2일
            expected = 'YES' if unapproved_days <= 2 else 'NO'
            actual = row.get('attendancy condition 2 - unapproved absence', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 2 (무단결근)',
                    'Expected': expected,
                    'Actual': actual,
                    'Unapproved_Days': int(unapproved_days),
                    'Threshold': '2일 이하',
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_3_actual_working_days(self):
        """조건 3: 실제 근무일 > 0 검증"""
        print("\n🔍 조건 3: 실제 근무일 > 0 검증 중...")

        errors = []

        # Excel 출력 파일에 이미 계산된 Actual Working Days 컬럼 사용
        if 'Actual Working Days' not in self.df_output.columns:
            print("   ⚠️ 'Actual Working Days' 컬럼 없음, 건너뜀")
            return errors

        # 전체 직원 검증
        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])
            actual_days = row.get('Actual Working Days', 0)

            # 조건 3: 실제 근무일 > 0
            expected = 'YES' if actual_days > 0 else 'NO'
            actual = row.get('attendancy condition 3 - actual working days', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 3 (실제근무일)',
                    'Expected': expected,
                    'Actual': actual,
                    'Actual_Working_Days': int(actual_days),
                    'Threshold': '> 0일',
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_4_minimum_working_days(self):
        """조건 4: 최소 근무일 >= 12일 검증"""
        print("\n🔍 조건 4: 최소 근무일 >= 12일 검증 중...")

        errors = []

        # Excel 출력 파일에 이미 계산된 Actual Working Days 컬럼 사용
        if 'Actual Working Days' not in self.df_output.columns:
            print("   ⚠️ 'Actual Working Days' 컬럼 없음, 건너뜀")
            return errors

        # 전체 직원 검증
        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])
            actual_days = row.get('Actual Working Days', 0)

            # 조건 4: 최소 근무일 >= 12일
            expected = 'YES' if actual_days >= 12 else 'NO'
            actual = row.get('attendancy condition 4 - minimum working days', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 4 (최소근무일)',
                    'Expected': expected,
                    'Actual': actual,
                    'Actual_Working_Days': int(actual_days),
                    'Threshold': '>= 12일',
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_5_personal_aql(self):
        """조건 5: 개인 AQL 당월 실패 = 0 검증"""
        print("\n🔍 조건 5: 개인 AQL 당월 실패 = 0 검증 중...")

        if self.df_aql is None:
            print("   ⚠️ AQL 데이터 없음, 건너뜀")
            return []

        errors = []

        # AQL 데이터에서 ID 컬럼 찾기
        id_col = None
        for col in ['ID No', 'Employee No', 'ID']:
            if col in self.df_aql.columns:
                id_col = col
                break

        if not id_col:
            print("   ⚠️ AQL 데이터에 ID 컬럼 없음")
            return errors

        # 전체 직원 검증
        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])

            # AQL 데이터에서 해당 직원의 실패 건수 확인
            emp_aql = self.df_aql[self.df_aql[id_col].astype(str) == emp_id]
            failure_count = 0

            # AQL 실패 확인 (컬럼명은 실제 데이터에 따라 다를 수 있음)
            if 'Result' in self.df_aql.columns:
                failure_count = len(emp_aql[emp_aql['Result'].str.upper().str.contains('FAIL|NG', na=False)])
            elif 'AQL_Result' in self.df_aql.columns:
                failure_count = len(emp_aql[emp_aql['AQL_Result'].str.upper().str.contains('FAIL|NG', na=False)])

            expected = 'YES' if failure_count == 0 else 'NO'
            actual = row.get('aql condition 5 - personal failure', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 5 (개인AQL)',
                    'Expected': expected,
                    'Actual': actual,
                    'Failure_Count': failure_count,
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_6_personal_aql_consecutive(self):
        """조건 6: 개인 AQL 3개월 연속 실패 없음 검증"""
        print("\n🔍 조건 6: 개인 AQL 3개월 연속 실패 없음 검증 중...")

        errors = []

        # Excel 출력 파일에 이미 계산된 Continuous_FAIL 컬럼 사용
        if 'Continuous_FAIL' not in self.df_output.columns:
            print("   ⚠️ 'Continuous_FAIL' 컬럼 없음, 건너뜀")
            return errors

        # 전체 직원 검증
        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])
            continuous_fail = str(row.get('Continuous_FAIL', 'NO')).upper()

            # 조건 6: 3개월 연속 실패 없음 (YES_3MONTHS가 아니어야 함)
            has_3month_fail = 'YES_3MONTHS' in continuous_fail or '3' in continuous_fail
            expected = 'NO' if has_3month_fail else 'YES'
            actual = row.get('aql condition 6 - personal consecutive failure', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 6 (개인AQL 3개월연속)',
                    'Expected': expected,
                    'Actual': actual,
                    'Continuous_FAIL': continuous_fail,
                    'Note': '3개월 연속 실패 없어야 함',
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_7_team_aql_consecutive(self):
        """조건 7: 팀/구역 AQL 3개월 연속 실패 없음 검증"""
        print("\n🔍 조건 7: 팀/구역 AQL 3개월 연속 실패 없음 검증 중...")

        errors = []

        # 현재는 개인 AQL 연속 실패만 추적하고 있으므로
        # 팀/구역 AQL 연속 실패는 Excel 출력 파일의 값을 그대로 사용
        if 'aql condition 7 - team area consecutive failure' not in self.df_output.columns:
            print("   ⚠️ 'aql condition 7' 컬럼 없음, 건너뜀")
            return errors

        # 팀/구역 AQL 데이터가 없으므로 일단 검증 스킵
        print("   ℹ️ 팀/구역 AQL 연속 실패 데이터 소스 없음 - 검증 스킵")
        print("   ℹ️ 향후 확장: 팀/구역별 AQL 이력 추적 필요")

        return errors

    def validate_condition_8_area_reject_rate(self):
        """조건 8: 담당구역 reject율 < 3% 검증"""
        print("\n🔍 조건 8: 담당구역 reject율 < 3% 검증 중...")

        if self.df_aql is None:
            print("   ⚠️ AQL 데이터 없음, 건너뜀")
            return []

        errors = []

        # AQL 데이터에서 reject rate 계산 (데이터 구조에 따라 다를 수 있음)
        if 'Reject_Rate' in self.df_aql.columns or 'Reject Rate' in self.df_aql.columns:
            reject_col = 'Reject_Rate' if 'Reject_Rate' in self.df_aql.columns else 'Reject Rate'

            # ID 컬럼 찾기
            id_col = None
            for col in ['ID No', 'Employee No', 'ID']:
                if col in self.df_aql.columns:
                    id_col = col
                    break

            if id_col:
                # 직원별 평균 reject rate 계산
                emp_reject_rates = self.df_aql.groupby(id_col)[reject_col].mean().to_dict()

                checked_count = 0
                for idx, row in self.df_output.iterrows():
                    emp_id = str(row['ID No'])
                    reject_rate = emp_reject_rates.get(emp_id, 0)

                    # 조건 8: reject율 < 3%
                    expected = 'YES' if reject_rate < 3 else 'NO'
                    actual = row.get('aql condition 8 - area reject rate', '')

                    if expected != actual:
                        errors.append({
                            'Employee': f"{row.get('Name', '')} ({emp_id})",
                            'Condition': '조건 8 (구역reject율)',
                            'Expected': expected,
                            'Actual': actual,
                            'Reject_Rate': f"{reject_rate:.2f}%",
                            'Threshold': '< 3%',
                            'Severity': 'ERROR'
                        })

                    checked_count += 1

                print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
            else:
                print("   ⚠️ AQL 데이터에 ID 컬럼 없음 - 검증 스킵")
        else:
            print("   ℹ️ AQL 데이터에 Reject_Rate 컬럼 없음 - 검증 스킵")
            print("   ℹ️ 향후 확장: Reject_Rate 계산 로직 필요")

        return errors

    def validate_condition_9_5prs_pass_rate(self):
        """조건 9: 5PRS 통과율 >= 95% 검증"""
        print("\n🔍 조건 9: 5PRS 통과율 >= 95% 검증 중...")

        if self.df_5prs is None:
            print("   ⚠️ 5PRS 데이터 없음, 건너뜀")
            return []

        errors = []

        # 5PRS 데이터에서 ID 컬럼 찾기
        id_col = None
        for col in ['ID No', 'Employee No', 'ID', 'Emp No']:
            if col in self.df_5prs.columns:
                id_col = col
                break

        if not id_col:
            print("   ⚠️ 5PRS 데이터에 ID 컬럼 없음")
            return errors

        # 5PRS 통과율 계산 (Pass/Total)
        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])

            # 5PRS 데이터에서 해당 직원의 Pass/Total 계산
            emp_5prs = self.df_5prs[self.df_5prs[id_col].astype(str) == emp_id]

            if len(emp_5prs) == 0:
                # 5PRS 데이터가 없는 직원은 0%
                pass_rate = 0
                total_qty = 0
            else:
                # Pass/Fail 컬럼 확인
                if 'Result' in self.df_5prs.columns:
                    total_qty = len(emp_5prs)
                    pass_qty = len(emp_5prs[emp_5prs['Result'].str.upper().str.contains('PASS|OK', na=False)])
                    pass_rate = (pass_qty / total_qty * 100) if total_qty > 0 else 0
                elif 'Pass_Rate' in self.df_5prs.columns:
                    pass_rate = emp_5prs['Pass_Rate'].mean()
                    total_qty = len(emp_5prs)
                else:
                    print("   ℹ️ 5PRS 데이터에 Result 또는 Pass_Rate 컬럼 없음")
                    continue

            # 조건 9: 5PRS 통과율 >= 95%
            expected = 'YES' if pass_rate >= 95 else 'NO'
            actual = row.get('5prs condition 9 - pass rate', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 9 (5PRS통과율)',
                    'Expected': expected,
                    'Actual': actual,
                    'Pass_Rate': f"{pass_rate:.2f}%",
                    'Total_Qty': total_qty,
                    'Threshold': '>= 95%',
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_condition_10_5prs_inspection_qty(self):
        """조건 10: 5PRS 검사량 >= 100족 검증"""
        print("\n🔍 조건 10: 5PRS 검사량 >= 100족 검증 중...")

        if self.df_5prs is None:
            print("   ⚠️ 5PRS 데이터 없음, 건너뜀")
            return []

        errors = []

        # 5PRS 데이터에서 ID 컬럼 찾기
        id_col = None
        for col in ['ID No', 'Employee No', 'ID', 'Emp No']:
            if col in self.df_5prs.columns:
                id_col = col
                break

        if not id_col:
            print("   ⚠️ 5PRS 데이터에 ID 컬럼 없음")
            return errors

        # 직원별 검사량 계산
        inspection_counts = self.df_5prs.groupby(id_col).size().to_dict()

        checked_count = 0
        for idx, row in self.df_output.iterrows():
            emp_id = str(row['ID No'])
            inspection_qty = inspection_counts.get(emp_id, 0)

            # 조건 10: 5PRS 검사량 >= 100족
            expected = 'YES' if inspection_qty >= 100 else 'NO'
            actual = row.get('5prs condition 10 - inspection quantity', '')

            if expected != actual:
                errors.append({
                    'Employee': f"{row.get('Name', '')} ({emp_id})",
                    'Condition': '조건 10 (5PRS검사량)',
                    'Expected': expected,
                    'Actual': actual,
                    'Inspection_Qty': inspection_qty,
                    'Threshold': '>= 100족',
                    'Severity': 'ERROR'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_100_percent_rule(self):
        """100% 조건 충족 규칙 검증"""
        print("\n🔍 100% 조건 충족 규칙 검증 중...")

        errors = []

        for idx, row in self.df_output.iterrows():
            pass_rate = row.get('conditions_pass_rate', 0)
            incentive = row.get('Final Incentive amount', 0)
            emp_id = row.get('ID No', '')
            name = row.get('Name', '')

            # 규칙 1: 100% 미만이면 무조건 0
            if pass_rate < 100 and incentive > 0:
                errors.append({
                    'Employee': f"{name} ({emp_id})",
                    'Rule': '100% 규칙 위반',
                    'Pass_Rate': f"{pass_rate}%",
                    'Incentive': f"{incentive:,.0f} VND",
                    'Expected': '0 VND',
                    'Severity': 'CRITICAL'
                })

            # 규칙 2: 80-99%도 0이어야 함
            if 80 <= pass_rate < 100 and incentive > 0:
                self.warnings.append({
                    'Employee': f"{name} ({emp_id})",
                    'Rule': '80-99% 규칙',
                    'Pass_Rate': f"{pass_rate}%",
                    'Incentive': f"{incentive:,.0f} VND",
                    'Note': '80-99%도 0 VND이어야 함',
                    'Severity': 'WARNING'
                })

        print(f"   ✅ {len(self.df_output)}명 검증 완료")
        print(f"   🚨 CRITICAL: {len(errors)}건")
        print(f"   ⚠️ WARNING: {len([w for w in self.warnings if w.get('Rule') == '80-99% 규칙'])}건")

        return errors

    def generate_report(self, all_errors):
        """검증 리포트 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.base_path / 'validation_reports' / f'condition_evaluation_report_{self.month}_{self.year}_{timestamp}.xlsx'

        # 디렉토리 생성
        report_file.parent.mkdir(exist_ok=True)

        print(f"\n📝 리포트 생성 중: {report_file.name}")

        # Excel 작성
        with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
            # Sheet 1: 요약 (10개 조건 전체)
            summary_data = {
                '검증 항목': [
                    '조건 1 (출근율 ≥88%)',
                    '조건 2 (무단결근 ≤2일)',
                    '조건 3 (실제근무일 >0)',
                    '조건 4 (최소근무일 ≥12일)',
                    '조건 5 (개인AQL 실패=0)',
                    '조건 6 (개인AQL 3개월연속)',
                    '조건 7 (팀AQL 3개월연속)',
                    '조건 8 (구역reject율 <3%)',
                    '조건 9 (5PRS통과율 ≥95%)',
                    '조건 10 (5PRS검사량 ≥100족)',
                    '100% 규칙',
                    '총계'
                ],
                '검증 건수': [
                    len([e for e in all_errors if '조건 1' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 2' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 3' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 4' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 5' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 6' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 7' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 8' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 9' in e.get('Condition', '')]),
                    len([e for e in all_errors if '조건 10' in e.get('Condition', '')]),
                    len([e for e in all_errors if '100%' in e.get('Rule', '')]),
                    len(all_errors)
                ],
                '오류 건수': [
                    len([e for e in all_errors if '조건 1' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 2' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 3' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 4' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 5' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 6' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 7' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 8' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 9' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '조건 10' in e.get('Condition', '') and e['Severity'] == 'ERROR']),
                    len([e for e in all_errors if '100%' in e.get('Rule', '') and e['Severity'] == 'CRITICAL']),
                    len([e for e in all_errors if e.get('Severity') in ['ERROR', 'CRITICAL']])
                ]
            }

            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='요약', index=False)

            # Sheet 2: 상세 오류
            if all_errors:
                df_errors = pd.DataFrame(all_errors)
                df_errors.to_excel(writer, sheet_name='상세 오류', index=False)

            # Sheet 3: 경고
            if self.warnings:
                df_warnings = pd.DataFrame(self.warnings)
                df_warnings.to_excel(writer, sheet_name='경고', index=False)

        print(f"   ✅ 리포트 저장 완료")
        print(f"   📊 총 {len(all_errors)}건의 오류 발견")

        return report_file

    def run_validation(self):
        """전체 검증 실행"""
        print("="*80)
        print(f"🔍 조건 평가 정확성 검증 - {self.year}년 {self.month}")
        print("="*80)

        # 1. 데이터 로드
        if not self.load_config():
            return False

        if not self.load_output_data():
            return False

        if not self.load_source_data():
            return False

        # 2. 조건별 검증 (10개 조건 전체)
        all_errors = []

        # 조건 1-4: 출근 관련
        all_errors.extend(self.validate_condition_1_attendance_rate())
        all_errors.extend(self.validate_condition_2_unapproved_absence())
        all_errors.extend(self.validate_condition_3_actual_working_days())
        all_errors.extend(self.validate_condition_4_minimum_working_days())

        # 조건 5-8: AQL 품질 관련
        all_errors.extend(self.validate_condition_5_personal_aql())
        all_errors.extend(self.validate_condition_6_personal_aql_consecutive())
        all_errors.extend(self.validate_condition_7_team_aql_consecutive())
        all_errors.extend(self.validate_condition_8_area_reject_rate())

        # 조건 9-10: 5PRS 관련
        all_errors.extend(self.validate_condition_9_5prs_pass_rate())
        all_errors.extend(self.validate_condition_10_5prs_inspection_qty())

        # 100% 규칙 검증
        all_errors.extend(self.validate_100_percent_rule())

        # 3. 리포트 생성
        report_file = self.generate_report(all_errors)

        # 4. 결과 출력
        print("\n" + "="*80)
        print("📊 검증 결과 요약")
        print("="*80)
        print(f"✅ 검증 완료: {self.year}년 {self.month}")
        print(f"📋 총 직원 수: {len(self.df_output)}명")
        print(f"🚨 발견된 오류: {len(all_errors)}건")
        print(f"⚠️ 경고: {len(self.warnings)}건")
        print(f"\n📄 상세 리포트: {report_file}")
        print("="*80)

        return True


def main():
    parser = argparse.ArgumentParser(description='조건 평가 정확성 검증')
    parser.add_argument('month', help='월 (예: september)')
    parser.add_argument('year', type=int, help='년도 (예: 2025)')
    args = parser.parse_args()

    validator = ConditionEvaluationValidator(args.month, args.year)
    validator.run_validation()


if __name__ == '__main__':
    main()
