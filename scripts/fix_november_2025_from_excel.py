#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11월 2025 Previous_Incentive 수정 스크립트
목적: '2025 october completed final incentive amount data.xlsx'를 기반으로
      11월 CSV의 Previous_Incentive를 정확히 업데이트
"""

import pandas as pd
import os
from pathlib import Path
import shutil
from datetime import datetime

def main():
    print("=" * 100)
    print("11월 2025 Previous_Incentive 수정 (Excel 기반)")
    print("=" * 100)

    base_path = Path(__file__).parent.parent

    # 1. Excel 파일 로드
    excel_file = base_path / "2025 october completed final incentive amount data.xlsx"

    if not excel_file.exists():
        print(f"❌ Excel 파일 없음: {excel_file}")
        return 1

    print(f"\n[Step 1] Excel 파일 로드: {excel_file.name}")
    df_excel = pd.read_excel(excel_file)
    df_excel['Employee No'] = df_excel['Employee No'].astype(str).str.zfill(9)

    print(f"  ✅ {len(df_excel)}명 직원 데이터 로드")
    print(f"  ✅ Source_Final_Incentive: {(df_excel['Source_Final_Incentive'] > 0).sum()}명, {df_excel['Source_Final_Incentive'].sum():,.0f} VND")

    # 2. 11월 CSV 로드 (V8.02 백업)
    nov_file_v8 = base_path / "output_files" / "output_QIP_incentive_november_2025_Complete_V8.02_Complete.csv"

    if not nov_file_v8.exists():
        print(f"❌ 11월 CSV 파일 없음: {nov_file_v8}")
        return 1

    print(f"\n[Step 2] 11월 CSV 로드: {nov_file_v8.name}")
    df_nov = pd.read_csv(nov_file_v8, encoding='utf-8-sig')
    df_nov['Employee No'] = df_nov['Employee No'].astype(str).str.zfill(9)

    print(f"  ✅ {len(df_nov)}명 직원 데이터 로드")

    # 3. Previous_Incentive 업데이트 (Excel 기준)
    print(f"\n[Step 3] Previous_Incentive 업데이트 (Excel Source_Final_Incentive 기준)")

    # Excel의 Source_Final_Incentive 매핑
    incentive_map = df_excel.set_index('Employee No')['Source_Final_Incentive'].to_dict()

    # 기존 Previous_Incentive 백업
    df_nov['Previous_Incentive_OLD'] = df_nov['Previous_Incentive']

    # 새로운 Previous_Incentive 설정
    df_nov['Previous_Incentive'] = df_nov['Employee No'].map(incentive_map).fillna(0)

    # 변경 통계
    changes = (df_nov['Previous_Incentive'] != df_nov['Previous_Incentive_OLD']).sum()
    old_total = df_nov['Previous_Incentive_OLD'].sum()
    new_total = df_nov['Previous_Incentive'].sum()

    print(f"  ✅ 변경된 직원: {changes}명")
    print(f"  ✅ 이전 총액: {old_total:,.0f} VND")
    print(f"  ✅ 신규 총액: {new_total:,.0f} VND")
    print(f"  ✅ 차이: {new_total - old_total:+,.0f} VND")

    # 4. Continuous_Months 업데이트 (Excel 기준)
    print(f"\n[Step 4] Continuous_Months 업데이트 (Excel 기준)")

    if 'Continuous_Months' in df_excel.columns:
        cont_months_map = df_excel.set_index('Employee No')['Continuous_Months'].to_dict()
        df_nov['Continuous_Months_OLD'] = df_nov.get('Continuous_Months', 0)
        df_nov['Continuous_Months'] = df_nov['Employee No'].map(cont_months_map).fillna(0)

        cm_changes = (df_nov['Continuous_Months'] != df_nov['Continuous_Months_OLD']).sum()
        print(f"  ✅ 변경된 직원: {cm_changes}명")
    else:
        print(f"  ⚠️ Excel에 Continuous_Months 없음 - 스킵")

    # 5. Next_Month_Expected 업데이트 (Excel 기준)
    print(f"\n[Step 5] Next_Month_Expected 업데이트 (Excel 기준)")

    if 'Next_Month_Expected' in df_excel.columns:
        next_month_map = df_excel.set_index('Employee No')['Next_Month_Expected'].to_dict()
        df_nov['Next_Month_Expected_OLD'] = df_nov.get('Next_Month_Expected', 0)
        df_nov['Next_Month_Expected'] = df_nov['Employee No'].map(next_month_map).fillna(1)

        nme_changes = (df_nov['Next_Month_Expected'] != df_nov['Next_Month_Expected_OLD']).sum()
        print(f"  ✅ 변경된 직원: {nme_changes}명")
    else:
        print(f"  ⚠️ Excel에 Next_Month_Expected 없음 - 스킵")

    # 6. V9.0로 저장 (백업 유지)
    output_file = base_path / "output_files" / "output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv"
    backup_file = base_path / "output_files" / f"output_QIP_incentive_november_2025_Complete_V9.0_Complete.csv.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"\n[Step 6] 저장")

    # 기존 V9.0 파일 백업
    if output_file.exists():
        shutil.copy2(output_file, backup_file)
        print(f"  ✅ 기존 파일 백업: {backup_file.name}")

    # OLD 컬럼 제거 (디버깅용만 유지)
    df_nov_clean = df_nov.drop(columns=['Previous_Incentive_OLD', 'Continuous_Months_OLD', 'Next_Month_Expected_OLD'], errors='ignore')

    # CSV 저장
    df_nov_clean.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"  ✅ 저장 완료: {output_file.name}")
    print(f"  ✅ 파일 크기: {output_file.stat().st_size / 1024:.1f} KB")

    # 7. 요약
    print(f"\n{'=' * 100}")
    print(f"완료 요약")
    print(f"{'=' * 100}")
    print(f"✅ 총 직원: {len(df_nov_clean)}명")
    print(f"✅ Previous_Incentive 업데이트: {changes}명")
    print(f"✅ 새로운 Previous_Incentive 총액: {new_total:,.0f} VND")
    print(f"✅ Excel Source_Final_Incentive 총액: {df_excel['Source_Final_Incentive'].sum():,.0f} VND")

    if abs(new_total - df_excel['Source_Final_Incentive'].sum()) < 1:
        print(f"\n🎉 검증 성공: Previous_Incentive = Excel Source_Final_Incentive")
    else:
        print(f"\n⚠️ 검증 실패: 금액 불일치")
        print(f"   차이: {abs(new_total - df_excel['Source_Final_Incentive'].sum()):,.0f} VND")

    print(f"\n다음 단계:")
    print(f"  1. 11월 인센티브 재계산: python3 src/step1_인센티브_계산_개선버전.py --config config_files/config_november_2025.json")
    print(f"  2. 11월 대시보드 재생성: python3 integrated_dashboard_final.py --month 11 --year 2025")
    print(f"  3. 검증 스크립트 실행")

    return 0

if __name__ == "__main__":
    exit(main())
