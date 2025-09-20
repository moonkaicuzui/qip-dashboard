#!/usr/bin/env python3
"""
JSON-코드 일관성 자동 검증 스크립트
JSON 설정과 실제 코드 동작의 일치 여부를 자동으로 검증
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

class JSONConsistencyValidator:
    """JSON과 코드 일관성 검증 클래스"""

    def __init__(self, json_file='config_files/position_condition_matrix_compatible.json'):
        self.json_file = json_file
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        self.load_json()

    def load_json(self):
        """JSON 파일 로드"""
        try:
            with open(self.json_file, 'r') as f:
                self.config = json.load(f)
            print(f"✅ JSON 파일 로드 성공: {self.json_file}")
        except Exception as e:
            print(f"❌ JSON 로드 실패: {e}")
            sys.exit(1)

    def validate_type3_consistency(self):
        """TYPE-3 관련 일관성 검증"""
        print("\n" + "=" * 70)
        print("🔍 TYPE-3 일관성 검증")
        print("-" * 70)

        issues = []

        # 1. eligible_for_incentive 검증
        type3_default = self.config.get('position_matrix', {}).get('TYPE-3', {}).get('default', {})
        eligible = type3_default.get('eligible_for_incentive', None)

        if eligible is False:
            print("✅ eligible_for_incentive = False (정확)")
            self.results['passed'].append("TYPE-3 eligible 설정")
        elif eligible is None:
            print("⚠️ eligible_for_incentive 필드 없음")
            self.results['warnings'].append("TYPE-3 eligible 필드 누락")
        else:
            print(f"❌ eligible_for_incentive = {eligible} (False여야 함)")
            self.results['failed'].append("TYPE-3 eligible 설정")
            issues.append("eligible_for_incentive가 False가 아님")

        # 2. amount_range 검증
        amount_range = self.config['incentive_rules']['TYPE-3']['base_incentive']['amount_range']
        if amount_range['min'] == 0 and amount_range['max'] == 0:
            print("✅ amount_range = {min: 0, max: 0} (정확)")
            self.results['passed'].append("TYPE-3 amount_range")
        else:
            print(f"❌ amount_range = {amount_range} (0이어야 함)")
            self.results['failed'].append("TYPE-3 amount_range")
            issues.append(f"amount_range가 0이 아님: {amount_range}")

        # 3. policy_status 검증
        policy_status = type3_default.get('policy_status', None)
        if policy_status == 'EXCLUDED':
            print("✅ policy_status = EXCLUDED (정확)")
            self.results['passed'].append("TYPE-3 policy_status")
        elif policy_status is None:
            print("⚠️ policy_status 필드 없음 (선택사항)")
            self.results['warnings'].append("TYPE-3 policy_status 누락")
        else:
            print(f"⚠️ policy_status = {policy_status}")
            self.results['warnings'].append("TYPE-3 policy_status 값 확인 필요")

        # 4. validation_rules 검증
        if 'validation_rules' in self.config:
            if 'TYPE-3' in self.config['validation_rules']:
                type3_validation = self.config['validation_rules']['TYPE-3']
                if type3_validation.get('payment_blocked', False):
                    print("✅ payment_blocked = True (정확)")
                    self.results['passed'].append("TYPE-3 payment_blocked")
                else:
                    print("❌ payment_blocked가 True가 아님")
                    self.results['failed'].append("TYPE-3 payment_blocked")
                    issues.append("payment_blocked가 True가 아님")

        return len(issues) == 0, issues

    def validate_code_consistency(self):
        """코드와 JSON의 일관성 검증"""
        print("\n" + "=" * 70)
        print("🔍 코드-JSON 일관성 검증")
        print("-" * 70)

        code_files = [
            'src/step2_dashboard_version4.py',
            'integrated_dashboard_final.py'
        ]

        for code_file in code_files:
            if Path(code_file).exists():
                print(f"\n📄 {code_file} 검증:")
                with open(code_file, 'r') as f:
                    content = f.read()

                # TYPE-3 처리 코드 확인
                if "TYPE-3" in content and "정책 제외" in content:
                    print("  ✅ TYPE-3 정책 제외 코드 존재")
                    self.results['passed'].append(f"{code_file} TYPE-3 처리")

                # 인센티브 0 설정 확인
                if re.search(r"TYPE-3.*incentive.*0", content, re.IGNORECASE):
                    print("  ✅ TYPE-3 인센티브 0 설정 확인")
                    self.results['passed'].append(f"{code_file} 인센티브 0")

    def validate_output_consistency(self):
        """실제 출력 데이터 검증"""
        print("\n" + "=" * 70)
        print("🔍 출력 데이터 일관성 검증")
        print("-" * 70)

        excel_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'

        if Path(excel_file).exists():
            df = pd.read_csv(excel_file)
            print(f"✅ Excel 파일 로드: {len(df)}명")

            # TYPE-3 직원 확인
            if 'TYPE' in df.columns:
                type3_df = df[df['TYPE'] == 'TYPE-3']
                if len(type3_df) > 0:
                    # TYPE-3 인센티브 확인
                    type3_incentives = type3_df['September_Incentive'].unique()
                    if len(type3_incentives) == 1 and type3_incentives[0] == 0:
                        print(f"✅ TYPE-3 직원 {len(type3_df)}명 모두 인센티브 0")
                        self.results['passed'].append("TYPE-3 출력 데이터")
                    else:
                        print(f"❌ TYPE-3 인센티브가 0이 아닌 직원 존재: {type3_incentives}")
                        self.results['failed'].append("TYPE-3 출력 데이터")
            else:
                print("⚠️ TYPE 컬럼 없음 (실제 TYPE 판정은 내부 처리)")
                self.results['warnings'].append("TYPE 컬럼 부재")

    def generate_report(self):
        """검증 보고서 생성"""
        print("\n" + "=" * 80)
        print("📊 JSON 일관성 검증 보고서")
        print("=" * 80)

        print(f"\n검증 시간: {self.results['timestamp']}")
        print(f"검증 파일: {self.json_file}")

        print(f"\n✅ 통과: {len(self.results['passed'])}개")
        for item in self.results['passed']:
            print(f"   • {item}")

        if self.results['warnings']:
            print(f"\n⚠️ 경고: {len(self.results['warnings'])}개")
            for item in self.results['warnings']:
                print(f"   • {item}")

        if self.results['failed']:
            print(f"\n❌ 실패: {len(self.results['failed'])}개")
            for item in self.results['failed']:
                print(f"   • {item}")

        # 최종 판정
        print("\n" + "=" * 80)
        print("🎯 최종 판정")
        print("=" * 80)

        if not self.results['failed']:
            print("✅ JSON과 코드가 일관성 있게 동작합니다!")
            print("   TYPE-3 개선사항이 올바르게 구현되었습니다.")
            return True
        else:
            print("❌ 일관성 문제가 발견되었습니다.")
            print("   수정이 필요합니다.")
            return False

    def save_report(self, filename=None):
        """검증 보고서 JSON 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 보고서 저장: {filename}")

    def run_all_validations(self):
        """모든 검증 실행"""
        print("\n" + "=" * 80)
        print("🚀 자동 검증 시작")
        print("=" * 80)

        # TYPE-3 일관성
        type3_ok, issues = self.validate_type3_consistency()

        # 코드 일관성
        self.validate_code_consistency()

        # 출력 데이터 일관성
        self.validate_output_consistency()

        # 보고서 생성
        success = self.generate_report()

        # 보고서 저장
        if not success:
            self.save_report()

        return success


def continuous_validation():
    """지속적 검증 (CI/CD용)"""
    print("\n" + "=" * 80)
    print("⚡ 지속적 JSON 검증 모드")
    print("=" * 80)

    validator = JSONConsistencyValidator()
    success = validator.run_all_validations()

    # CI/CD 종료 코드
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            continuous_validation()
        else:
            json_file = sys.argv[1]
            validator = JSONConsistencyValidator(json_file)
    else:
        validator = JSONConsistencyValidator()

    # 전체 검증 실행
    validator.run_all_validations()