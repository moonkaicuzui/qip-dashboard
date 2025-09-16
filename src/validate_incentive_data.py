#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인센티브 데이터 검증 시스템
데이터 일관성 검증, 이상치 감지, 변경 이력 추적
하드코딩 없음
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import argparse
from typing import Dict, List, Tuple

class IncentiveValidator:
    """인센티브 데이터 검증 클래스"""

    def __init__(self, current_file: str, previous_file: str = None):
        self.current_file = current_file
        self.previous_file = previous_file
        self.validation_results = []
        self.warnings = []
        self.errors = []

        # Position matrix 로드
        self.load_position_matrix()

    def load_position_matrix(self):
        """position_condition_matrix.json 로드"""
        try:
            with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
                matrix = json.load(f)
                self.progression = matrix.get('incentive_progression', {}).get('TYPE_1_PROGRESSIVE', {})
                self.incentive_table = self.progression.get('progression_table', {})
        except Exception as e:
            self.errors.append(f"position_condition_matrix.json 로드 실패: {e}")
            self.progression = {}
            self.incentive_table = {}

    def validate_continuous_months_logic(self, df: pd.DataFrame) -> List[Dict]:
        """연속 개월 로직 검증"""
        issues = []

        for _, row in df.iterrows():
            emp_id = row.get('Employee No', '')
            name = row.get('Full Name', 'Unknown')
            position = str(row.get('QIP POSITION 1ST  NAME', '')).upper()
            role_type = row.get('ROLE TYPE STD', '')

            # TYPE-1 진보형만 검증
            if role_type != 'TYPE-1':
                continue

            if not any(x in position for x in ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR', 'TRAINING']):
                continue

            # 연속 개월 컬럼 확인
            prev_months = row.get('Previous_Continuous_Months', 0)
            expected_months = row.get('Current_Expected_Months', 0)
            current_incentive = 0

            # 인센티브 컬럼 찾기
            for col in df.columns:
                if 'Incentive' in col and col != 'Previous_Incentive':
                    current_incentive = row.get(col, 0)
                    break

            # 검증 1: 인센티브 금액과 개월수 일치 확인
            if current_incentive > 0:
                expected_amount = self.incentive_table.get(str(expected_months), 0)
                if abs(current_incentive - expected_amount) > 1:
                    issues.append({
                        'employee': f"{name} ({emp_id})",
                        'type': 'AMOUNT_MISMATCH',
                        'message': f"금액 불일치: {expected_months}개월 → {expected_amount:,} VND 예상, 실제 {current_incentive:,} VND",
                        'severity': 'ERROR'
                    })

            # 검증 2: 연속성 체크
            if prev_months > 0 and expected_months == 0 and current_incentive > 0:
                issues.append({
                    'employee': f"{name} ({emp_id})",
                    'type': 'CONTINUITY_BREAK',
                    'message': f"연속성 끊김: 이전 {prev_months}개월 → 현재 0개월 but 인센티브 {current_incentive:,} VND 지급",
                    'severity': 'WARNING'
                })

        return issues

    def detect_anomalies(self, current_df: pd.DataFrame, previous_df: pd.DataFrame = None) -> List[Dict]:
        """이상치 감지"""
        anomalies = []

        if previous_df is None:
            return anomalies

        # 직원별 비교
        for _, curr_row in current_df.iterrows():
            emp_id = curr_row.get('Employee No', '')
            name = curr_row.get('Full Name', 'Unknown')

            # 이전 월 데이터 찾기
            prev_row = previous_df[previous_df['Employee No'] == emp_id]
            if prev_row.empty:
                continue

            prev_row = prev_row.iloc[0]

            # 인센티브 금액 비교
            curr_incentive = 0
            prev_incentive = 0

            for col in current_df.columns:
                if 'Incentive' in col and col != 'Previous_Incentive':
                    curr_incentive = curr_row.get(col, 0)
                    break

            for col in previous_df.columns:
                if 'Incentive' in col and col != 'Previous_Incentive':
                    prev_incentive = prev_row.get(col, 0)
                    break

            # 이상치 감지 규칙
            # 1. 갑작스런 큰 증가 (500,000 VND 이상)
            if curr_incentive - prev_incentive > 500000:
                anomalies.append({
                    'employee': f"{name} ({emp_id})",
                    'type': 'SUDDEN_INCREASE',
                    'message': f"급격한 인센티브 증가: {prev_incentive:,} → {curr_incentive:,} VND (+{curr_incentive - prev_incentive:,})",
                    'severity': 'INFO'
                })

            # 2. 갑작스런 감소 (이전 월 대비 50% 이상 감소)
            if prev_incentive > 0 and curr_incentive < prev_incentive * 0.5:
                anomalies.append({
                    'employee': f"{name} ({emp_id})",
                    'type': 'SUDDEN_DECREASE',
                    'message': f"급격한 인센티브 감소: {prev_incentive:,} → {curr_incentive:,} VND (-{prev_incentive - curr_incentive:,})",
                    'severity': 'WARNING'
                })

            # 3. 0에서 갑자기 높은 금액 (250,000 이상)
            if prev_incentive == 0 and curr_incentive > 250000:
                anomalies.append({
                    'employee': f"{name} ({emp_id})",
                    'type': 'ZERO_TO_HIGH',
                    'message': f"0에서 높은 금액으로 급증: 0 → {curr_incentive:,} VND",
                    'severity': 'WARNING'
                })

        return anomalies

    def validate_data_consistency(self, df: pd.DataFrame) -> List[Dict]:
        """데이터 일관성 검증"""
        issues = []

        # 필수 컬럼 확인
        required_columns = ['Employee No', 'Full Name', 'QIP POSITION 1ST  NAME', 'ROLE TYPE STD']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            issues.append({
                'type': 'MISSING_COLUMNS',
                'message': f"필수 컬럼 누락: {', '.join(missing_columns)}",
                'severity': 'ERROR'
            })

        # 중복 직원 확인
        duplicates = df[df.duplicated(subset=['Employee No'], keep=False)]
        if not duplicates.empty:
            dup_ids = duplicates['Employee No'].unique()
            issues.append({
                'type': 'DUPLICATE_EMPLOYEES',
                'message': f"중복 직원 ID 발견: {', '.join(map(str, dup_ids))}",
                'severity': 'ERROR'
            })

        # NULL 값 확인
        null_counts = df[required_columns].isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                issues.append({
                    'type': 'NULL_VALUES',
                    'message': f"{col} 컬럼에 NULL 값 {count}개",
                    'severity': 'WARNING'
                })

        return issues

    def generate_report(self) -> str:
        """검증 보고서 생성"""
        report = []
        report.append("=" * 60)
        report.append("인센티브 데이터 검증 보고서")
        report.append(f"검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"대상 파일: {self.current_file}")
        if self.previous_file:
            report.append(f"비교 파일: {self.previous_file}")
        report.append("=" * 60)

        # 에러
        if self.errors:
            report.append("\n❌ 에러:")
            for error in self.errors:
                report.append(f"  - {error}")

        # 경고
        if self.warnings:
            report.append("\n⚠️ 경고:")
            for warning in self.warnings:
                report.append(f"  - {warning}")

        # 검증 결과
        if self.validation_results:
            report.append("\n📊 검증 결과:")

            # 심각도별 분류
            errors = [r for r in self.validation_results if r.get('severity') == 'ERROR']
            warnings = [r for r in self.validation_results if r.get('severity') == 'WARNING']
            infos = [r for r in self.validation_results if r.get('severity') == 'INFO']

            if errors:
                report.append(f"\n  🔴 오류 ({len(errors)}건):")
                for err in errors[:10]:  # 처음 10개만 표시
                    if 'employee' in err:
                        report.append(f"    - {err['employee']}: {err['message']}")
                    else:
                        report.append(f"    - {err['message']}")
                if len(errors) > 10:
                    report.append(f"    ... 외 {len(errors) - 10}건")

            if warnings:
                report.append(f"\n  🟡 경고 ({len(warnings)}건):")
                for warn in warnings[:10]:
                    if 'employee' in warn:
                        report.append(f"    - {warn['employee']}: {warn['message']}")
                    else:
                        report.append(f"    - {warn['message']}")
                if len(warnings) > 10:
                    report.append(f"    ... 외 {len(warnings) - 10}건")

            if infos:
                report.append(f"\n  🔵 정보 ({len(infos)}건):")
                for info in infos[:5]:
                    if 'employee' in info:
                        report.append(f"    - {info['employee']}: {info['message']}")
                    else:
                        report.append(f"    - {info['message']}")
                if len(infos) > 5:
                    report.append(f"    ... 외 {len(infos) - 5}건")

        # 요약
        report.append("\n" + "=" * 60)
        error_count = len([r for r in self.validation_results if r.get('severity') == 'ERROR'])
        warning_count = len([r for r in self.validation_results if r.get('severity') == 'WARNING'])

        if error_count == 0 and warning_count == 0:
            report.append("✅ 검증 통과: 심각한 문제가 발견되지 않았습니다.")
        else:
            report.append(f"검증 완료: 오류 {error_count}건, 경고 {warning_count}건 발견")

        return "\n".join(report)

    def validate(self) -> bool:
        """전체 검증 실행"""
        try:
            # 현재 파일 로드
            print(f"📂 파일 로드 중: {self.current_file}")
            current_df = pd.read_csv(self.current_file, encoding='utf-8-sig')
            print(f"  ✅ {len(current_df)}명 데이터 로드")

            # 이전 파일 로드 (있으면)
            previous_df = None
            if self.previous_file and Path(self.previous_file).exists():
                print(f"📂 비교 파일 로드 중: {self.previous_file}")
                previous_df = pd.read_csv(self.previous_file, encoding='utf-8-sig')
                print(f"  ✅ {len(previous_df)}명 데이터 로드")

            # 1. 데이터 일관성 검증
            print("\n🔍 데이터 일관성 검증 중...")
            consistency_issues = self.validate_data_consistency(current_df)
            self.validation_results.extend(consistency_issues)

            # 2. 연속 개월 로직 검증
            print("🔍 연속 개월 로직 검증 중...")
            logic_issues = self.validate_continuous_months_logic(current_df)
            self.validation_results.extend(logic_issues)

            # 3. 이상치 감지
            if previous_df is not None:
                print("🔍 이상치 감지 중...")
                anomalies = self.detect_anomalies(current_df, previous_df)
                self.validation_results.extend(anomalies)

            # 보고서 생성
            report = self.generate_report()
            print("\n" + report)

            # 보고서 파일 저장
            report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 보고서 저장: {report_file}")

            # 오류가 있으면 False 반환
            error_count = len([r for r in self.validation_results if r.get('severity') == 'ERROR'])
            return error_count == 0

        except Exception as e:
            print(f"❌ 검증 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='인센티브 데이터 검증')
    parser.add_argument('--current', required=True, help='검증할 현재 파일')
    parser.add_argument('--previous', help='비교할 이전 파일 (선택)')

    args = parser.parse_args()

    # 검증 실행
    validator = IncentiveValidator(args.current, args.previous)
    success = validator.validate()

    if success:
        print("\n✅ 검증 성공!")
    else:
        print("\n❌ 검증 실패 - 오류를 확인하세요")
        exit(1)


if __name__ == "__main__":
    main()