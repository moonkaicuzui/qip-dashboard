#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 파일에서 연속 개월 추적 JSON 자동 생성 스크립트
Single Source of Truth: Excel → JSON 자동 변환
하드코딩 없음
"""

import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

def load_position_matrix():
    """position_condition_matrix.json에서 인센티브 테이블 로드"""
    try:
        with open('config_files/position_condition_matrix.json', 'r', encoding='utf-8') as f:
            matrix = json.load(f)
            return matrix.get('incentive_progression', {}).get('TYPE_1_PROGRESSIVE', {})
    except Exception as e:
        print(f"⚠️ position_condition_matrix.json 로드 실패: {e}")
        return {}

def calculate_expected_months(row, progression_config):
    """다음 달 예상 개월 계산"""
    current_incentive = row.get('August_Incentive', 0)
    position = str(row.get('QIP POSITION 1ST  NAME', '')).upper()
    role_type = row.get('ROLE TYPE STD', '')

    # TYPE-1 진보형 인센티브 직급만 해당
    if role_type != 'TYPE-1':
        return None

    if not any(x in position for x in ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR', 'TRAINING']):
        return None

    # 인센티브가 0이면 연속성 끊김
    if current_incentive <= 0:
        return 0

    # 인센티브 금액으로 현재 개월 수 역산
    table = progression_config.get('progression_table', {})
    current_months = 0

    for months_str, amount in table.items():
        if abs(current_incentive - amount) < 1:
            current_months = int(months_str)
            break

    # 최대 개월 확인
    max_months = progression_config.get('max_months', 12)

    # 다음 달 예상 개월 (현재가 최대면 유지, 아니면 +1)
    if current_months >= max_months:
        return max_months
    else:
        return current_months + 1

def generate_json_from_excel(excel_path, output_path, month, year):
    """Excel 파일에서 JSON 자동 생성"""

    print(f"\n🔄 Excel → JSON 자동 변환 시작")
    print(f"  입력: {excel_path}")
    print(f"  출력: {output_path}")

    try:
        # Excel 파일 로드
        df = pd.read_csv(excel_path, encoding='utf-8-sig')
        print(f"✅ Excel 파일 로드: {len(df)} 명")

        # 인센티브 테이블 로드
        progression = load_position_matrix()
        if not progression:
            print("❌ 인센티브 테이블을 찾을 수 없습니다")
            return False

        # JSON 구조 생성
        json_data = {
            "description": f"TYPE-1 ASSEMBLY INSPECTOR 연속 근무 개월수 추적 (자동 생성)",
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_file": excel_path,
            "month": month,
            "year": year,
            "incentive_table": progression.get('progression_table', {}),
            "employees": {}
        }

        # 직원별 데이터 처리
        type1_count = 0
        for _, row in df.iterrows():
            emp_id = str(row.get('Employee No', '')).zfill(9)
            position = str(row.get('QIP POSITION 1ST  NAME', '')).upper()
            role_type = row.get('ROLE TYPE STD', '')

            # TYPE-1 진보형 인센티브 직급만 처리
            if role_type != 'TYPE-1':
                continue

            if not any(x in position for x in ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR', 'TRAINING']):
                continue

            type1_count += 1

            # 현재 월 인센티브
            current_incentive = row.get(f'{month.capitalize()}_Incentive', 0)

            # 이전 월 연속 개월 (컬럼이 있으면 사용, 없으면 계산)
            if 'Previous_Continuous_Months' in row:
                previous_months = row['Previous_Continuous_Months']
            else:
                # 인센티브 금액으로 역산
                previous_months = 0
                for months_str, amount in progression.get('progression_table', {}).items():
                    if abs(current_incentive - amount) < 1:
                        previous_months = max(0, int(months_str) - 1)
                        break

            # 다음 달 예상 개월
            if 'Current_Expected_Months' in row:
                expected_months = row['Current_Expected_Months']
            else:
                expected_months = calculate_expected_months(row, progression)

            if expected_months is not None:
                json_data['employees'][emp_id] = {
                    "name": row.get('Full Name', 'Unknown'),
                    "position": row.get('QIP POSITION 1ST  NAME', ''),
                    f"{month.lower()}_incentive": int(current_incentive),
                    f"{month.lower()}_continuous_months": int(previous_months) if previous_months else 0,
                    f"next_month_expected_months": int(expected_months) if expected_months else 0
                }

        # JSON 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON 파일 생성 완료")
        print(f"  - TYPE-1 진보형 직원: {type1_count}명")
        print(f"  - JSON 등록 직원: {len(json_data['employees'])}명")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Excel에서 연속 개월 JSON 자동 생성')
    parser.add_argument('--excel', required=True, help='입력 Excel/CSV 파일 경로')
    parser.add_argument('--output', default='config_files/assembly_inspector_continuous_months.json',
                       help='출력 JSON 파일 경로')
    parser.add_argument('--month', required=True, help='월 (예: august, september)')
    parser.add_argument('--year', type=int, required=True, help='연도 (예: 2025)')

    args = parser.parse_args()

    # 경로 확인
    excel_path = Path(args.excel)
    if not excel_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)

    # JSON 생성
    success = generate_json_from_excel(
        str(excel_path),
        args.output,
        args.month,
        args.year
    )

    if success:
        print("\n✅ JSON 자동 생성 성공!")
        print(f"   다음 명령으로 인센티브 계산 실행:")
        print(f"   python src/step1_인센티브_계산_개선버전.py --config config_files/config_{args.month}_{args.year}.json")
    else:
        print("\n❌ JSON 생성 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()