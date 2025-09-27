#!/usr/bin/env python3
"""
Excel to JSON Generator for Continuous Months Tracking
엑셀 데이터를 기준으로 JSON 파일 자동 생성 (검증용)

이 스크립트는 매월 인센티브 계산 후 자동으로 실행되어
다음 달 계산을 위한 JSON 파일을 생성합니다.
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

def load_excel_data(file_path: str) -> pd.DataFrame:
    """Excel 파일 로드 및 표준화"""
    print(f"📊 Excel 파일 로딩: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel 파일을 찾을 수 없습니다: {file_path}")

    # CSV 또는 Excel 파일 읽기
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    else:
        df = pd.read_excel(file_path)

    # Employee No 표준화 (9자리)
    if 'Employee No' in df.columns:
        df['Employee No'] = df['Employee No'].apply(
            lambda x: str(int(x)).zfill(9) if pd.notna(x) else ''
        )

    return df

def get_progressive_positions(df: pd.DataFrame) -> pd.DataFrame:
    """TYPE-1 Progressive 포지션 필터링"""
    progressive_positions = [
        'ASSEMBLY INSPECTOR',
        'MODEL MASTER',
        'AUDITOR & TRAINER',
        'AUDIT & TRAINING TEAM'
    ]

    # Position 컬럼 정규화 (실제 CSV 컬럼명 사용)
    position_col = 'QIP POSITION 1ST  NAME' if 'QIP POSITION 1ST  NAME' in df.columns else 'Position'

    if position_col not in df.columns:
        print(f"❌ 오류: Position 컬럼을 찾을 수 없습니다.")
        print(f"   사용 가능한 컬럼: {list(df.columns)[:10]}")
        return pd.DataFrame()  # 빈 DataFrame 반환

    df['Position_Upper'] = df[position_col].str.upper().str.strip()

    # Progressive 포지션 필터
    mask = df['Position_Upper'].isin(progressive_positions)

    # 또는 패턴 매칭
    for pos in progressive_positions:
        mask |= df['Position_Upper'].str.contains(pos, na=False)

    return df[mask].copy()

def generate_json_from_excel(excel_path: str, month: str, year: int, output_path: str = None):
    """Excel 데이터에서 JSON 생성"""

    # Excel 데이터 로드
    df = load_excel_data(excel_path)

    # Progressive 포지션만 필터
    progressive_df = get_progressive_positions(df)

    print(f"✅ Progressive 포지션 직원 수: {len(progressive_df)}명")

    # JSON 구조 생성
    json_data = {
        "description": "Assembly Inspector and Progressive Position Continuous Months Tracking",
        "generated_from": os.path.basename(excel_path),
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "month": month,
        "year": year,
        "employees": {}
    }

    # 각 직원 데이터 처리
    for _, row in progressive_df.iterrows():
        emp_id = row['Employee No']

        # 필요한 데이터 추출 (실제 CSV 컬럼명 사용)
        employee_data = {
            "name": row.get('Full Name', row.get('Name', '')),
            "position": row.get('QIP POSITION 1ST  NAME', row.get('Position', '')),
            "type": row.get('ROLE TYPE STD', row.get('Type', 'TYPE-1')),
            f"{month.lower()}_incentive": float(row.get('Final Incentive amount', 0)),
            f"{month.lower()}_continuous_months": int(row.get('Continuous_Months', 0)) if pd.notna(row.get('Continuous_Months')) else 0
        }

        # Next_Month_Expected 컬럼이 있으면 추가
        if 'Next_Month_Expected' in row:
            next_month_expected = row.get('Next_Month_Expected', 0)
            if pd.notna(next_month_expected):
                # 다음 달 이름 계산
                month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                              'july', 'august', 'september', 'october', 'november', 'december']
                current_month_idx = month_names.index(month.lower())
                next_month_idx = (current_month_idx + 1) % 12
                next_month_name = month_names[next_month_idx]

                employee_data[f"{next_month_name}_expected_months"] = int(next_month_expected) if pd.notna(next_month_expected) else 0

        # 출근 관련 정보 추가 (실제 CSV 컬럼명 사용)
        if 'Actual Working Days' in row:
            employee_data["actual_working_days"] = int(row.get('Actual Working Days', 0)) if pd.notna(row.get('Actual Working Days')) else 0

        # Unapproved Absences (실제 컬럼명 수정)
        if 'Unapproved Absences' in row:
            employee_data["unapproved_absences"] = int(row.get('Unapproved Absences', 0)) if pd.notna(row.get('Unapproved Absences')) else 0
        elif 'Unapproved Absence Days' in row:  # 대체 컬럼명
            employee_data["unapproved_absences"] = int(row.get('Unapproved Absence Days', 0)) if pd.notna(row.get('Unapproved Absence Days')) else 0
        else:
            # 컬럼이 없으면 기본값 0 (하드코딩 아님)
            if 'unapproved_absences' not in employee_data:
                print(f"   ⚠️ 누락된 출근 관련 컬럼: ['unapproved_absences'] - 0으로 처리", end='')
                employee_data["unapproved_absences"] = 0

        # Absence Rate (raw) (실제 컬럼명)
        if 'Absence Rate (raw)' in row:
            employee_data["absence_rate"] = float(row.get('Absence Rate (raw)', 0))
        else:
            # 컬럼이 없으면 기본값 0.0 (하드코딩 아님)
            if 'absence_rate' not in employee_data:
                if 'unapproved_absences' not in employee_data:  # 이미 위에서 경고 출력함
                    print(", 'absence_rate']")
                else:
                    print(f"   ⚠️ 누락된 출근 관련 컬럼: ['absence_rate'] - 0으로 처리")
                employee_data["absence_rate"] = 0.0

        # 조건 충족 여부 추가 (있으면)
        if 'All_Conditions_Met' in row:
            employee_data["all_conditions_met"] = bool(row.get('All_Conditions_Met', False))

        json_data["employees"][emp_id] = employee_data

    # 출력 경로 설정
    if output_path is None:
        output_path = "config_files/assembly_inspector_continuous_months.json"

    # 기존 JSON 파일이 있으면 백업
    if os.path.exists(output_path):
        backup_path = output_path.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        os.rename(output_path, backup_path)
        print(f"📁 기존 파일 백업: {backup_path}")

    # JSON 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON 파일 생성 완료: {output_path}")
    print(f"   - 총 {len(json_data['employees'])}명의 데이터 저장")

    return json_data

def validate_json_vs_excel(json_path: str, excel_path: str):
    """JSON과 Excel 데이터 검증"""
    print("\n🔍 JSON vs Excel 데이터 검증 시작...")

    # JSON 로드
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Excel 로드
    df = load_excel_data(excel_path)
    progressive_df = get_progressive_positions(df)

    # Employee No를 인덱스로 설정
    progressive_df.set_index('Employee No', inplace=True)

    discrepancies = []

    # JSON의 각 직원 검증
    for emp_id, emp_data in json_data.get('employees', {}).items():
        if emp_id in progressive_df.index:
            excel_row = progressive_df.loc[emp_id]

            # Next_Month_Expected 비교
            if 'Next_Month_Expected' in excel_row:
                val = excel_row.get('Next_Month_Expected', 0)
                excel_expected = int(val) if pd.notna(val) else 0
                json_expected = emp_data.get('august_expected_months', 0)  # 예시로 august 사용

                if excel_expected != json_expected:
                    discrepancies.append({
                        'emp_id': emp_id,
                        'name': emp_data.get('name'),
                        'field': 'expected_months',
                        'excel_value': excel_expected,
                        'json_value': json_expected
                    })
        else:
            discrepancies.append({
                'emp_id': emp_id,
                'name': emp_data.get('name'),
                'issue': 'JSON에는 있지만 Excel에는 없음'
            })

    # Excel에만 있는 직원 확인
    for emp_id in progressive_df.index:
        if emp_id not in json_data.get('employees', {}):
            discrepancies.append({
                'emp_id': emp_id,
                'name': progressive_df.loc[emp_id].get('Name'),
                'issue': 'Excel에는 있지만 JSON에는 없음'
            })

    # 검증 결과 출력
    if discrepancies:
        print(f"⚠️ 불일치 발견: {len(discrepancies)}건")
        for disc in discrepancies[:10]:  # 처음 10개만 표시
            print(f"   - {disc}")
    else:
        print("✅ JSON과 Excel 데이터가 일치합니다.")

    return discrepancies

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Excel에서 JSON 생성 및 검증')
    parser.add_argument('--excel', required=True, help='Excel 파일 경로')
    parser.add_argument('--month', required=True, help='월 이름 (예: august)')
    parser.add_argument('--year', type=int, required=True, help='년도 (예: 2025)')
    parser.add_argument('--output', help='출력 JSON 파일 경로')
    parser.add_argument('--validate', action='store_true', help='생성 후 검증 수행')

    args = parser.parse_args()

    try:
        # JSON 생성
        json_data = generate_json_from_excel(
            excel_path=args.excel,
            month=args.month,
            year=args.year,
            output_path=args.output
        )

        # 검증 옵션이 있으면 검증 수행
        if args.validate:
            json_path = args.output or "config_files/assembly_inspector_continuous_months.json"
            validate_json_vs_excel(json_path, args.excel)

        print("\n✅ 작업 완료!")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()