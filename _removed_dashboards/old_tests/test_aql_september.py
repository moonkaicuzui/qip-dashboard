#!/usr/bin/env python3
"""
9월 AQL FAIL 데이터 검증 스크립트
실제 AQL 데이터와 처리된 데이터를 비교하여 문제점 파악
"""

import pandas as pd
import json
import sys
from pathlib import Path

def analyze_september_aql():
    """9월 AQL 데이터 분석"""
    print("=" * 80)
    print("9월 AQL FAIL 데이터 검증 스크립트")
    print("=" * 80)

    # 1. 원본 AQL 데이터 로드
    print("\n1. 원본 AQL 데이터 로드...")
    aql_file = "input_files/AQL history/1.HSRG AQL REPORT-SEPTEMBER.2025.csv"
    aql_df = pd.read_csv(aql_file, encoding='utf-8-sig')

    # 컬럼 출력
    print(f"   AQL 데이터 컬럼: {list(aql_df.columns)[:10]}...")
    print(f"   총 레코드 수: {len(aql_df)}")

    # RESULT 컬럼에서 FAIL 찾기
    if 'RESULT' in aql_df.columns:
        # FAIL 데이터 필터링
        fail_df = aql_df[aql_df['RESULT'].str.contains('FAIL', na=False)]
        print(f"   FAIL 레코드 수: {len(fail_df)}")

        # FAIL PO만 필터링
        fail_po_df = fail_df[fail_df['PO TYPE'] == 'FAIL PO']
        print(f"   FAIL PO 레코드 수: {len(fail_po_df)}")

        # EMPLOYEE NO별 FAIL 집계
        if 'EMPLOYEE NO' in fail_df.columns:
            # Employee별 FAIL 카운트
            employee_fails = {}
            for _, row in fail_df.iterrows():
                emp_no = str(row['EMPLOYEE NO']).strip()
                if emp_no and emp_no != 'nan':
                    # 숫자 형태로 변환
                    try:
                        if '.' in emp_no:
                            emp_no = str(int(float(emp_no)))
                        emp_no = emp_no.zfill(9)  # 9자리로 패딩

                        if emp_no not in employee_fails:
                            employee_fails[emp_no] = {
                                'count': 0,
                                'inspector_name': row.get('OFFICIAL INSPECTOR', ''),
                                'inspector_type': row.get('INSPECTOR TYPE', ''),
                                'dates': []
                            }
                        employee_fails[emp_no]['count'] += 1
                        employee_fails[emp_no]['dates'].append(row.get('DATE', ''))
                    except:
                        pass

            print(f"\n   FAIL을 기록한 직원 수: {len(employee_fails)}명")
            print("\n   Top 10 FAIL 직원:")
            sorted_fails = sorted(employee_fails.items(), key=lambda x: x[1]['count'], reverse=True)
            for emp_id, data in sorted_fails[:10]:
                print(f"      {emp_id}: {data['count']}건 - {data['inspector_name']} ({data['inspector_type']})")

    # 2. 생성된 Excel 데이터 확인
    print("\n2. 생성된 Excel 데이터 확인...")
    excel_file = "output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv"
    excel_df = pd.read_csv(excel_file, encoding='utf-8-sig')

    if 'September AQL Failures' in excel_df.columns:
        non_zero_aql = excel_df[excel_df['September AQL Failures'] > 0]
        print(f"   Excel에서 AQL Failure가 있는 직원: {len(non_zero_aql)}명")

        if len(non_zero_aql) > 0:
            print("\n   Excel의 AQL Failure 직원 샘플:")
            print(non_zero_aql[['Employee No', 'Full Name', 'September AQL Failures']].head(10))

    # 3. 매칭 확인
    print("\n3. 데이터 매칭 확인...")
    if len(employee_fails) > 0 and 'Employee No' in excel_df.columns:
        # Excel에서 직원 번호 정규화
        excel_employees = set()
        for emp in excel_df['Employee No'].unique():
            if pd.notna(emp):
                emp_str = str(emp).strip().zfill(9)
                excel_employees.add(emp_str)

        # AQL FAIL 직원과 Excel 직원 비교
        aql_fail_employees = set(employee_fails.keys())

        matched = aql_fail_employees & excel_employees
        only_in_aql = aql_fail_employees - excel_employees

        print(f"   AQL FAIL 직원 중 Excel에 있는 직원: {len(matched)}/{len(aql_fail_employees)}")

        if only_in_aql:
            print(f"\n   ⚠️ AQL에는 있지만 Excel에 없는 직원: {len(only_in_aql)}명")
            for emp_id in list(only_in_aql)[:5]:
                print(f"      {emp_id}: {employee_fails[emp_id]['count']}건 실패")

        # Excel에서 실제 September AQL Failures 값 확인
        if len(matched) > 0:
            print(f"\n   매칭된 직원의 Excel 데이터 확인:")
            for emp_id in list(matched)[:5]:
                excel_row = excel_df[excel_df['Employee No'].astype(str).str.zfill(9) == emp_id]
                if not excel_row.empty:
                    excel_fail_count = excel_row['September AQL Failures'].iloc[0]
                    aql_fail_count = employee_fails[emp_id]['count']
                    print(f"      {emp_id}: AQL={aql_fail_count}건, Excel={excel_fail_count}건")

    # 4. TYPE-1 직원만 필터링해서 확인
    print("\n4. TYPE-1 직원 AQL FAIL 확인...")
    if 'ROLE TYPE STD' in excel_df.columns:
        type1_df = excel_df[excel_df['ROLE TYPE STD'] == 'TYPE-1']
        print(f"   TYPE-1 직원 수: {len(type1_df)}")

        # TYPE-1 직원 중 관리자급 포지션 필터링
        if 'FINAL QIP POSITION NAME CODE' in type1_df.columns:
            manager_positions = ['SUPERVISOR', 'GROUP LEADER', 'LINE LEADER', 'MANAGER', 'QA TEAM']
            manager_mask = type1_df['FINAL QIP POSITION NAME CODE'].str.upper().apply(
                lambda x: any(pos in str(x).upper() for pos in manager_positions) if pd.notna(x) else False
            )
            type1_managers = type1_df[manager_mask]
            print(f"   TYPE-1 관리자급 직원 수: {len(type1_managers)}")

            # 이들 중 AQL FAIL이 있는 직원
            type1_manager_fails = type1_managers[type1_managers['September AQL Failures'] > 0]
            print(f"   TYPE-1 관리자급 중 AQL FAIL 있는 직원: {len(type1_manager_fails)}")

            if len(type1_manager_fails) > 0:
                print("\n   TYPE-1 관리자급 AQL FAIL 직원:")
                for _, row in type1_manager_fails.head(10).iterrows():
                    print(f"      {row['Employee No']}: {row['Full Name']} ({row['FINAL QIP POSITION NAME CODE']}) - {row['September AQL Failures']}건")

    print("\n" + "=" * 80)
    print("검증 완료")

if __name__ == "__main__":
    analyze_september_aql()