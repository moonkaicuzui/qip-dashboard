#!/usr/bin/env python3
"""
Excel vs JSON 데이터 일관성 검증 시스템
Excel이 Primary Source이고 JSON은 Validation용임을 확인

이 스크립트는 Excel과 JSON 간의 데이터 일관성을 검증하고
불일치를 발견하면 상세 보고서를 생성합니다.
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import argparse
from typing import Dict, List, Tuple

class DataConsistencyValidator:
    """Excel과 JSON 데이터 일관성 검증기"""

    def __init__(self, excel_path: str, json_path: str):
        self.excel_path = excel_path
        self.json_path = json_path
        self.excel_data = None
        self.json_data = None
        self.validation_results = []

    def load_data(self):
        """데이터 로드"""
        # Excel 데이터 로드
        print(f"📊 Excel 데이터 로드: {self.excel_path}")
        if self.excel_path.endswith('.csv'):
            self.excel_data = pd.read_csv(self.excel_path, encoding='utf-8-sig')
        else:
            self.excel_data = pd.read_excel(self.excel_path)

        # Employee No 표준화
        if 'Employee No' in self.excel_data.columns:
            self.excel_data['Employee No'] = self.excel_data['Employee No'].apply(
                lambda x: str(int(x)).zfill(9) if pd.notna(x) else ''
            )

        # JSON 데이터 로드
        print(f"📄 JSON 데이터 로드: {self.json_path}")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.json_data = json.load(f)

    def get_progressive_employees(self) -> pd.DataFrame:
        """Progressive 포지션 직원 필터링"""
        progressive_positions = [
            'ASSEMBLY INSPECTOR',
            'MODEL MASTER',
            'AUDITOR & TRAINER',
            'AUDIT & TRAINING TEAM'
        ]

        df = self.excel_data.copy()
        df['Position_Upper'] = df['Position'].str.upper().str.strip()

        mask = df['Position_Upper'].isin(progressive_positions)
        for pos in progressive_positions:
            mask |= df['Position_Upper'].str.contains(pos, na=False)

        return df[mask].copy()

    def validate_employee_data(self, emp_id: str) -> Dict:
        """개별 직원 데이터 검증"""
        validation = {
            'emp_id': emp_id,
            'status': 'OK',
            'issues': []
        }

        # Excel에서 직원 찾기
        excel_emp = self.excel_data[self.excel_data['Employee No'] == emp_id]
        json_emp = self.json_data.get('employees', {}).get(emp_id, None)

        if excel_emp.empty and json_emp:
            validation['status'] = 'WARNING'
            validation['issues'].append('JSON에만 존재 (Excel에 없음)')
            return validation

        if not excel_emp.empty and not json_emp:
            validation['status'] = 'ERROR'
            validation['issues'].append('Excel에만 존재 (JSON에 없음)')
            return validation

        if not excel_emp.empty and json_emp:
            excel_row = excel_emp.iloc[0]

            # 이름 비교
            if excel_row.get('Name', '') != json_emp.get('name', ''):
                validation['issues'].append(f"이름 불일치: Excel={excel_row.get('Name')}, JSON={json_emp.get('name')}")

            # 포지션 비교
            if excel_row.get('Position', '') != json_emp.get('position', ''):
                validation['issues'].append(f"포지션 불일치: Excel={excel_row.get('Position')}, JSON={json_emp.get('position')}")

            # Continuous Months 비교
            if 'Continuous_Months' in excel_row:
                excel_months = int(excel_row.get('Continuous_Months', 0))
                json_months = json_emp.get('august_continuous_months', 0)  # 월별로 조정 필요

                if excel_months != json_months:
                    validation['issues'].append(f"연속 개월 불일치: Excel={excel_months}, JSON={json_months}")

            # Next Month Expected 비교
            if 'Next_Month_Expected' in excel_row:
                excel_expected = int(excel_row.get('Next_Month_Expected', 0))
                json_expected = json_emp.get('september_expected_months', 0)  # 월별로 조정 필요

                if excel_expected != json_expected:
                    validation['issues'].append(f"예상 개월 불일치: Excel={excel_expected}, JSON={json_expected}")

            # 인센티브 금액 비교
            if 'Final Incentive amount' in excel_row:
                excel_amount = float(excel_row.get('Final Incentive amount', 0))
                json_amount = json_emp.get('august_incentive', 0)  # 월별로 조정 필요

                if abs(excel_amount - json_amount) > 1:  # 부동소수점 오차 허용
                    validation['issues'].append(f"인센티브 금액 불일치: Excel={excel_amount:,.0f}, JSON={json_amount:,.0f}")

        if validation['issues']:
            validation['status'] = 'MISMATCH'

        return validation

    def validate_all(self) -> Tuple[List[Dict], Dict]:
        """전체 데이터 검증"""
        print("\n🔍 데이터 일관성 검증 시작...")

        progressive_df = self.get_progressive_employees()
        all_emp_ids = set(progressive_df['Employee No'].unique())
        json_emp_ids = set(self.json_data.get('employees', {}).keys())

        # 모든 직원 ID 통합
        all_ids = all_emp_ids | json_emp_ids

        results = []
        for emp_id in all_ids:
            result = self.validate_employee_data(emp_id)
            results.append(result)

        # 통계 생성
        stats = {
            'total': len(results),
            'ok': len([r for r in results if r['status'] == 'OK']),
            'warnings': len([r for r in results if r['status'] == 'WARNING']),
            'errors': len([r for r in results if r['status'] == 'ERROR']),
            'mismatches': len([r for r in results if r['status'] == 'MISMATCH'])
        }

        return results, stats

    def generate_report(self, results: List[Dict], stats: Dict) -> str:
        """검증 보고서 생성"""
        report = []
        report.append("=" * 80)
        report.append("Excel vs JSON 데이터 일관성 검증 보고서")
        report.append("=" * 80)
        report.append(f"검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Excel 파일: {self.excel_path}")
        report.append(f"JSON 파일: {self.json_path}")
        report.append("")

        # 통계
        report.append("📊 검증 통계:")
        report.append(f"  총 검증 대상: {stats['total']}명")
        report.append(f"  ✅ 정상: {stats['ok']}명")
        report.append(f"  ⚠️ 경고: {stats['warnings']}명")
        report.append(f"  ❌ 오류: {stats['errors']}명")
        report.append(f"  🔍 불일치: {stats['mismatches']}명")
        report.append("")

        # 문제 상세
        if stats['errors'] + stats['warnings'] + stats['mismatches'] > 0:
            report.append("⚠️ 발견된 문제:")
            report.append("-" * 40)

            for result in results:
                if result['status'] != 'OK':
                    report.append(f"\n직원 ID: {result['emp_id']}")
                    report.append(f"상태: {result['status']}")
                    for issue in result['issues']:
                        report.append(f"  - {issue}")

        else:
            report.append("✅ 모든 데이터가 일치합니다!")

        return "\n".join(report)

    def save_report(self, report: str, output_path: str = None):
        """보고서 저장"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"validation_report_{timestamp}.txt"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 보고서 저장: {output_path}")

    def run(self, save_report: bool = True):
        """검증 실행"""
        try:
            # 데이터 로드
            self.load_data()

            # 검증 수행
            results, stats = self.validate_all()

            # 보고서 생성
            report = self.generate_report(results, stats)

            # 콘솔 출력
            print("\n" + report)

            # 보고서 저장
            if save_report:
                self.save_report(report)

            return stats['errors'] == 0 and stats['mismatches'] == 0

        except Exception as e:
            print(f"❌ 검증 중 오류 발생: {e}")
            return False


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Excel vs JSON 데이터 일관성 검증')
    parser.add_argument('--excel', required=True, help='Excel 파일 경로')
    parser.add_argument('--json', default='config_files/assembly_inspector_continuous_months.json',
                       help='JSON 파일 경로')
    parser.add_argument('--no-report', action='store_true', help='보고서 파일 생성 안함')

    args = parser.parse_args()

    # 검증기 생성 및 실행
    validator = DataConsistencyValidator(args.excel, args.json)
    success = validator.run(save_report=not args.no_report)

    # 종료 코드 반환 (CI/CD 연동용)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()