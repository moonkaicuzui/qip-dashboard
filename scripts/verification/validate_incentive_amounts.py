#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인센티브 금액 계산 정확성 검증 스크립트
100% 조건 충족자의 인센티브 금액이 올바르게 계산되었는지 검증합니다.

실행 방법:
    python scripts/verification/validate_incentive_amounts.py september 2025
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import argparse

class IncentiveAmountValidator:
    """인센티브 금액 정확성 검증기"""

    def __init__(self, month: str, year: int):
        self.month = month
        self.year = year
        self.base_path = Path(__file__).parent.parent.parent
        self.errors = []
        self.warnings = []

        # Position Matrix 로드
        self.load_position_matrix()

        # 계산 결과 CSV
        self.df_output = None

    def load_position_matrix(self):
        """Position Condition Matrix 로드"""
        matrix_path = self.base_path / 'config_files' / 'position_condition_matrix.json'
        print(f"📂 Position Matrix 로드: {matrix_path.name}")

        with open(matrix_path, 'r', encoding='utf-8') as f:
            matrix = json.load(f)

        # Progressive 테이블 추출
        self.progression = matrix.get('incentive_progression', {}).get('TYPE_1_PROGRESSIVE', {})
        self.progression_table = self.progression.get('progression_table', {})

        print(f"   ✅ Progressive 테이블 로드: 0-15개월")
        print(f"   📊 예시: 1개월={self.progression_table.get('1'):,} VND, 12개월={self.progression_table.get('12'):,} VND")

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
            return False

        print(f"\n📊 출력 CSV 로드: {output_file.name}")
        self.df_output = pd.read_csv(output_file, encoding='utf-8-sig')
        print(f"   ✅ {len(self.df_output)}명의 직원 데이터 로드")

        return True

    def validate_type1_progressive_amounts(self):
        """TYPE-1 Progressive 금액 검증"""
        print("\n🔍 TYPE-1 Progressive 인센티브 금액 검증 중...")

        errors = []

        # TYPE-1 Progressive 대상 필터링
        type1_progressive = self.df_output[
            (self.df_output['Type'] == 'TYPE-1') &
            (self.df_output['Position'].str.upper().str.contains(
                'ASSEMBLY INSPECTOR|MODEL MASTER|AUDITOR|TRAINER',
                na=False,
                regex=True
            ))
        ].copy()

        print(f"   📋 TYPE-1 Progressive 대상: {len(type1_progressive)}명")

        checked_count = 0
        for idx, row in type1_progressive.iterrows():
            emp_id = row.get('ID No', '')
            name = row.get('Name', '')
            position = row.get('Position', '')
            pass_rate = row.get('conditions_pass_rate', 0)
            incentive = row.get('Final Incentive amount', 0)
            continuous_months = row.get('Updated_Continuous_Months', 0)

            # 100% 조건 충족자만 검증
            if pass_rate == 100:
                # Progressive 테이블에서 예상 금액 찾기
                expected_amount = int(self.progression_table.get(str(int(continuous_months)), 0))

                # 금액 비교 (소수점 오차 허용)
                if abs(incentive - expected_amount) > 1:
                    errors.append({
                        'Employee': f"{name} ({emp_id})",
                        'Position': position,
                        'Pass_Rate': f"{pass_rate}%",
                        'Continuous_Months': int(continuous_months),
                        'Expected_Amount': f"{expected_amount:,} VND",
                        'Actual_Amount': f"{int(incentive):,} VND",
                        'Difference': f"{int(incentive - expected_amount):+,} VND",
                        'Type': 'TYPE-1 Progressive',
                        'Severity': 'ERROR'
                    })

            # 100% 미달인데 인센티브가 있는 경우
            elif pass_rate < 100 and incentive > 0:
                errors.append({
                    'Employee': f"{name} ({emp_id})",
                    'Position': position,
                    'Pass_Rate': f"{pass_rate}%",
                    'Continuous_Months': int(continuous_months),
                    'Expected_Amount': '0 VND',
                    'Actual_Amount': f"{int(incentive):,} VND",
                    'Difference': f"{int(incentive):+,} VND",
                    'Type': '100% 미달',
                    'Severity': 'CRITICAL'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_type2_standard_amounts(self):
        """TYPE-2 Standard 금액 검증

        TYPE-2는 TYPE-1 포지션별 평균 인센티브를 참조합니다.
        고정 금액 범위가 아닌, TYPE-1의 평균을 그대로 사용하는 방식입니다.
        따라서 금액 범위 검증 대신 100% 규칙 준수 여부만 확인합니다.
        """
        print("\n🔍 TYPE-2 Standard 인센티브 금액 검증 중...")
        print("   ℹ️ TYPE-2는 TYPE-1 평균을 참조 (고정 범위 아님)")

        errors = []

        # TYPE-2 필터링
        type2 = self.df_output[self.df_output['Type'] == 'TYPE-2'].copy()

        print(f"   📋 TYPE-2 대상: {len(type2)}명")

        # TYPE-2는 출근 조건(1-4)만 적용
        # 100% 충족 여부 확인
        checked_count = 0
        for idx, row in type2.iterrows():
            emp_id = row.get('ID No', '')
            name = row.get('Name', '')
            position = row.get('Position', '')
            pass_rate = row.get('conditions_pass_rate', 0)
            incentive = row.get('Final Incentive amount', 0)

            # 100% 충족인데 0인 경우
            if pass_rate == 100 and incentive == 0:
                self.warnings.append({
                    'Employee': f"{name} ({emp_id})",
                    'Position': position,
                    'Pass_Rate': f"{pass_rate}%",
                    'Expected': '> 0 VND (TYPE-1 평균)',
                    'Actual_Amount': '0 VND',
                    'Issue': 'TYPE-1 평균 미반영',
                    'Type': 'TYPE-2 Standard',
                    'Severity': 'WARNING'
                })

            # 100% 미달인데 인센티브가 있는 경우
            elif pass_rate < 100 and incentive > 0:
                errors.append({
                    'Employee': f"{name} ({emp_id})",
                    'Position': position,
                    'Pass_Rate': f"{pass_rate}%",
                    'Expected_Amount': '0 VND',
                    'Actual_Amount': f"{int(incentive):,} VND",
                    'Type': 'TYPE-2 100% 미달',
                    'Severity': 'CRITICAL'
                })

            checked_count += 1

        print(f"   ✅ {checked_count}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_type3_new_members(self):
        """TYPE-3 New Members 검증"""
        print("\n🔍 TYPE-3 New Members 검증 중...")

        errors = []

        # TYPE-3 필터링
        type3 = self.df_output[self.df_output['Type'] == 'TYPE-3'].copy()

        print(f"   📋 TYPE-3 대상: {len(type3)}명")

        # TYPE-3는 무조건 0이어야 함
        for idx, row in type3.iterrows():
            emp_id = row.get('ID No', '')
            name = row.get('Name', '')
            incentive = row.get('Final Incentive amount', 0)
            pass_rate = row.get('conditions_pass_rate', 0)

            if incentive != 0:
                errors.append({
                    'Employee': f"{name} ({emp_id})",
                    'Type': 'TYPE-3',
                    'Pass_Rate': f"{pass_rate}%",
                    'Expected_Amount': '0 VND',
                    'Actual_Amount': f"{int(incentive):,} VND",
                    'Rule': 'TYPE-3는 무조건 0 VND',
                    'Severity': 'CRITICAL'
                })

        print(f"   ✅ {len(type3)}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def validate_continuous_months_logic(self):
        """연속 개월 로직 검증"""
        print("\n🔍 연속 개월 로직 검증 중...")

        errors = []

        # TYPE-1 Progressive만
        type1_progressive = self.df_output[
            (self.df_output['Type'] == 'TYPE-1') &
            (self.df_output['Position'].str.upper().str.contains(
                'ASSEMBLY INSPECTOR|MODEL MASTER|AUDITOR|TRAINER',
                na=False,
                regex=True
            ))
        ].copy()

        for idx, row in type1_progressive.iterrows():
            emp_id = row.get('ID No', '')
            name = row.get('Name', '')
            pass_rate = row.get('conditions_pass_rate', 0)
            prev_months = row.get('Previous_Continuous_Months', 0)
            updated_months = row.get('Updated_Continuous_Months', 0)

            # 규칙 1: 조건 미달이면 리셋 (0으로)
            if pass_rate < 100:
                if updated_months != 0:
                    errors.append({
                        'Employee': f"{name} ({emp_id})",
                        'Rule': '조건 미달 시 리셋',
                        'Pass_Rate': f"{pass_rate}%",
                        'Previous_Months': int(prev_months),
                        'Expected_Updated': 0,
                        'Actual_Updated': int(updated_months),
                        'Severity': 'ERROR'
                    })

            # 규칙 2: 조건 충족이면 +1 (최대 12)
            else:
                expected_updated = min(prev_months + 1, 12)
                if updated_months != expected_updated:
                    errors.append({
                        'Employee': f"{name} ({emp_id})",
                        'Rule': '조건 충족 시 +1',
                        'Pass_Rate': f"{pass_rate}%",
                        'Previous_Months': int(prev_months),
                        'Expected_Updated': int(expected_updated),
                        'Actual_Updated': int(updated_months),
                        'Severity': 'ERROR'
                    })

        print(f"   ✅ {len(type1_progressive)}명 검증 완료, {len(errors)}건 오류 발견")
        return errors

    def generate_report(self, all_errors):
        """검증 리포트 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.base_path / 'validation_reports' / f'incentive_amount_report_{self.month}_{self.year}_{timestamp}.xlsx'

        print(f"\n📝 리포트 생성 중: {report_file.name}")

        # Excel 작성
        with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
            # Sheet 1: 요약
            type1_errors = [e for e in all_errors if 'TYPE-1' in e.get('Type', '')]
            type2_errors = [e for e in all_errors if 'TYPE-2' in e.get('Type', '')]
            type3_errors = [e for e in all_errors if 'TYPE-3' in e.get('Type', '')]
            continuous_errors = [e for e in all_errors if 'Rule' in e and '개월' in e.get('Rule', '')]

            summary_data = {
                '검증 항목': [
                    'TYPE-1 Progressive',
                    'TYPE-2 Standard',
                    'TYPE-3 New Members',
                    '연속 개월 로직',
                    '총계'
                ],
                '오류 건수': [
                    len(type1_errors),
                    len(type2_errors),
                    len(type3_errors),
                    len(continuous_errors),
                    len(all_errors)
                ],
                'Critical': [
                    len([e for e in type1_errors if e.get('Severity') == 'CRITICAL']),
                    len([e for e in type2_errors if e.get('Severity') == 'CRITICAL']),
                    len([e for e in type3_errors if e.get('Severity') == 'CRITICAL']),
                    0,
                    len([e for e in all_errors if e.get('Severity') == 'CRITICAL'])
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

            # Sheet 4: 통계
            stats_data = {
                '항목': [
                    '총 직원 수',
                    'TYPE-1 Progressive',
                    'TYPE-2 Standard',
                    'TYPE-3 New Members',
                    '100% 조건 충족자',
                    '인센티브 수령자',
                    '평균 인센티브 (수령자)'
                ],
                '값': [
                    len(self.df_output),
                    len(self.df_output[self.df_output['Type'] == 'TYPE-1']),
                    len(self.df_output[self.df_output['Type'] == 'TYPE-2']),
                    len(self.df_output[self.df_output['Type'] == 'TYPE-3']),
                    len(self.df_output[self.df_output['conditions_pass_rate'] == 100]),
                    len(self.df_output[self.df_output['Final Incentive amount'] > 0]),
                    f"{self.df_output[self.df_output['Final Incentive amount'] > 0]['Final Incentive amount'].mean():,.0f} VND"
                ]
            }

            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='통계', index=False)

        print(f"   ✅ 리포트 저장 완료")
        return report_file

    def run_validation(self):
        """전체 검증 실행"""
        print("="*80)
        print(f"💰 인센티브 금액 계산 정확성 검증 - {self.year}년 {self.month}")
        print("="*80)

        # 데이터 로드
        if not self.load_output_data():
            return False

        # 검증 실행
        all_errors = []

        # TYPE-1 Progressive
        all_errors.extend(self.validate_type1_progressive_amounts())

        # TYPE-2 Standard
        all_errors.extend(self.validate_type2_standard_amounts())

        # TYPE-3 New Members
        all_errors.extend(self.validate_type3_new_members())

        # 연속 개월 로직
        all_errors.extend(self.validate_continuous_months_logic())

        # 리포트 생성
        report_file = self.generate_report(all_errors)

        # 결과 출력
        print("\n" + "="*80)
        print("📊 검증 결과 요약")
        print("="*80)
        print(f"✅ 검증 완료: {self.year}년 {self.month}")
        print(f"📋 총 직원 수: {len(self.df_output)}명")
        print(f"🚨 발견된 오류: {len(all_errors)}건")
        print(f"   - CRITICAL: {len([e for e in all_errors if e.get('Severity') == 'CRITICAL'])}건")
        print(f"   - ERROR: {len([e for e in all_errors if e.get('Severity') == 'ERROR'])}건")
        print(f"⚠️ 경고: {len(self.warnings)}건")
        print(f"\n📄 상세 리포트: {report_file}")
        print("="*80)

        return len(all_errors) == 0


def main():
    parser = argparse.ArgumentParser(description='인센티브 금액 계산 정확성 검증')
    parser.add_argument('month', help='월 (예: september)')
    parser.add_argument('year', type=int, help='년도 (예: 2025)')
    args = parser.parse_args()

    validator = IncentiveAmountValidator(args.month, args.year)
    success = validator.run_validation()

    # Exit code 설정
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
