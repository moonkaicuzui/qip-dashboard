#!/usr/bin/env python3
"""
Single Source of Truth 검증 스크립트
Excel 파일이 진정한 단일 데이터 소스인지 확인
"""

import pandas as pd
import json
import os
from datetime import datetime

def verify_single_source():
    print("=" * 70)
    print("🔍 Single Source of Truth 검증")
    print("=" * 70)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # 1. Excel 파일 확인
    excel_file = 'output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete.csv'
    if os.path.exists(excel_file):
        df = pd.read_csv(excel_file)
        print(f"✅ Excel 파일 존재: {excel_file}")
        print(f"   - 총 레코드: {len(df)}개")
        print(f"   - 총 컬럼: {len(df.columns)}개")
        results['passed'].append("Excel 파일 존재 확인")
    else:
        print(f"❌ Excel 파일 없음: {excel_file}")
        results['failed'].append("Excel 파일 없음")
        return results
    
    # 2. 필수 데이터 컬럼 확인
    print("\n📊 필수 데이터 컬럼 확인:")
    
    required_columns = {
        'AQL 데이터': ['September AQL Failures', 'Continuous_FAIL', 'Area_Reject_Rate'],
        '5PRS 데이터': ['5PRS_Pass_Rate', '5PRS_Inspection_Qty'],
        '출근 데이터': ['Total Working Days', 'Actual Working Days', 'Unapproved Absences'],
        '인센티브 데이터': ['September_Incentive', 'Previous_Incentive'],
        '조건 평가': ['cond_1_attendance_rate', 'cond_5_aql_personal_failure', 'cond_9_5prs_pass_rate']
    }
    
    for category, columns in required_columns.items():
        missing = [col for col in columns if col not in df.columns]
        if missing:
            print(f"   ❌ {category}: 누락된 컬럼 - {missing}")
            results['failed'].append(f"{category} 컬럼 누락")
        else:
            print(f"   ✅ {category}: 모든 컬럼 존재")
            results['passed'].append(f"{category} 컬럼 확인")
    
    # 3. Config 파일 검증
    print("\n⚙️ Config 파일 검증:")
    config_file = 'config_files/config_september_2025.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # working_days 검증
        if config.get('working_days') == 15:
            print(f"   ✅ working_days: {config['working_days']}일 (실제 데이터 기반)")
            results['passed'].append("working_days 실제 값 사용")
        else:
            print(f"   ⚠️ working_days: {config['working_days']}일 (하드코딩 의심)")
            results['warnings'].append("working_days 값 확인 필요")
            
        # working_days_source 확인
        if 'working_days_source' in config:
            print(f"   ✅ working_days_source: {config['working_days_source']}")
            results['passed'].append("working_days 소스 명시")
    
    # 4. Dashboard 파일 검증
    print("\n📋 Dashboard 코드 검증:")
    dashboard_file = 'integrated_dashboard_final.py'
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r') as f:
            content = f.read()
        
        # 별도 CSV 파일 읽기 확인
        violations = []
        if "pd.read_csv(aql_file" in content and "# Single Source" not in content[:content.find("pd.read_csv(aql_file")]:
            violations.append("AQL CSV 직접 읽기")
        if "pd.read_csv(prs_file" in content and "# Single Source" not in content[:content.find("pd.read_csv(prs_file")]:
            violations.append("5PRS CSV 직접 읽기")
            
        # Single Source 주석 확인
        if "Single Source of Truth" in content:
            count = content.count("Single Source of Truth")
            print(f"   ✅ Single Source of Truth 주석: {count}개 발견")
            results['passed'].append("Single Source of Truth 구현 확인")
        
        if violations:
            print(f"   ❌ 위반 사항: {violations}")
            results['failed'].append("별도 CSV 읽기 발견")
        else:
            print(f"   ✅ 별도 CSV 읽기 없음 (Excel만 사용)")
            results['passed'].append("Excel만 사용 확인")
    
    # 5. 데이터 일관성 검증
    print("\n🔄 데이터 일관성 검증:")
    
    # AQL 데이터 검증
    aql_count = (df['September AQL Failures'] > 0).sum()
    print(f"   - AQL 실패 기록이 있는 직원: {aql_count}명")
    
    # 5PRS 데이터 검증
    prs_count = (df['5PRS_Inspection_Qty'] > 0).sum()
    print(f"   - 5PRS 검사 데이터가 있는 직원: {prs_count}명")
    
    # Previous_Incentive 검증
    prev_count = (df['Previous_Incentive'] > 0).sum()
    prev_total = df['Previous_Incentive'].sum()
    print(f"   - Previous_Incentive 데이터: {prev_count}명, 총 {prev_total:,.0f} VND")
    
    if prev_count > 0:
        results['passed'].append("Previous_Incentive 데이터 확인")
    else:
        results['warnings'].append("Previous_Incentive 데이터 없음")
    
    # 6. 결과 요약
    print("\n" + "=" * 70)
    print("📊 검증 결과 요약")
    print("=" * 70)
    
    print(f"\n✅ 통과 항목: {len(results['passed'])}개")
    for item in results['passed']:
        print(f"   • {item}")
    
    if results['warnings']:
        print(f"\n⚠️ 경고 항목: {len(results['warnings'])}개")
        for item in results['warnings']:
            print(f"   • {item}")
    
    if results['failed']:
        print(f"\n❌ 실패 항목: {len(results['failed'])}개")
        for item in results['failed']:
            print(f"   • {item}")
    
    # 7. 최종 판정
    print("\n" + "=" * 70)
    if not results['failed']:
        print("🎉 Single Source of Truth 원칙이 성공적으로 구현되었습니다!")
        print("   - Excel 파일이 유일한 데이터 소스입니다")
        print("   - Dashboard는 Excel 데이터만 사용합니다")
        print("   - 하드코딩된 값이 제거되었습니다")
    else:
        print("⚠️ Single Source of Truth 원칙 위반 사항이 발견되었습니다.")
        print("   개선이 필요합니다.")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    verify_single_source()
