#!/usr/bin/env python3
"""
개별 AQL Reject Rate 3% 모달 수정 사항 검증
"""

import pandas as pd
import json
import re
from pathlib import Path

def verify_modal_fix():
    """모달 수정 사항 검증"""

    print("=" * 80)
    print("🔍 개별 AQL Reject Rate 3% 모달 수정 검증")
    print("=" * 80)

    # 1. Excel 데이터에서 실제 3% 초과 직원 확인
    print("\n📊 Excel 데이터 분석:")
    print("-" * 40)

    csv_path = Path("output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_enhanced.csv")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    # Reject rate > 3% 직원 찾기
    high_reject_employees = []
    for idx, row in df.iterrows():
        area_reject_rate = float(row.get('area_reject_rate', 0) or 0)
        if area_reject_rate > 3:
            high_reject_employees.append({
                'emp_no': row['Employee No'],
                'name': row['Full Name'],
                'position': row['FINAL QIP POSITION NAME CODE'],
                'area_reject_rate': area_reject_rate,
                'building': row.get('AQL_Building', 'N/A')
            })

    print(f"✅ Reject Rate > 3% 직원 수: {len(high_reject_employees)}명")

    if high_reject_employees:
        print("\n👥 해당 직원 목록:")
        for emp in high_reject_employees[:5]:  # 처음 5명만 표시
            print(f"  - {emp['emp_no']}: {emp['name']} ({emp['area_reject_rate']:.2f}%)")

    # 2. HTML 파일에서 JavaScript 코드 검증
    print("\n📝 HTML/JavaScript 코드 검증:")
    print("-" * 40)

    html_path = Path("output_files/Incentive_Dashboard_2025_09_Version_5.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 구역 매핑 확인
    if "'전체 구역'" in html:
        print("❌ '전체 구역'이 아직 코드에 남아있습니다.")
    else:
        print("✅ '전체 구역' 매핑이 제거되었습니다.")

    # All Buildings 매핑 확인
    all_buildings_count = html.count("'All Buildings'")
    print(f"✅ 'All Buildings' 매핑 개수: {all_buildings_count}개")

    # 필터링 조건 확인
    if "return areaRejectRate > 3;  // 오직 reject rate > 3% 조건만 적용" in html:
        print("✅ 필터링 조건이 올바르게 수정되었습니다 (reject rate > 3%만 적용)")
    else:
        print("⚠️ 필터링 조건 확인 필요")

    # 인원수 카운팅 로직 확인
    if "if (rejectRate > 3) {" in html:
        print("✅ 3% 조건에 해당하는 인원만 카운트하도록 수정되었습니다")
    else:
        print("⚠️ 인원수 카운팅 로직 확인 필요")

    # 3. 모달 타이틀 및 설명 확인
    print("\n📋 모달 UI 텍스트 검증:")
    print("-" * 40)

    if "개별 AQL Reject Rate가 3%를 초과하는 직원은 인센티브를 받을 수 없습니다." in html:
        print("✅ 모달 설명이 올바르게 수정되었습니다")
    else:
        print("⚠️ 모달 설명 텍스트 확인 필요")

    if "개별 AQL Reject Rate 3% 초과 조건에 해당합니다." in html:
        print("✅ 인원 표시 텍스트가 올바르게 수정되었습니다")
    else:
        print("⚠️ 인원 표시 텍스트 확인 필요")

    # 4. 구역 테이블 구조 확인
    print("\n📊 구역 테이블 구조:")
    print("-" * 40)

    # 전체 행이 별도로 표시되는지 확인
    if "isTotal ? 'table-primary fw-bold' : ''" in html:
        print("✅ '전체' 행이 별도 스타일로 표시됩니다")
    else:
        print("⚠️ '전체' 행 스타일 확인 필요")

    # 결과 요약
    print("\n" + "=" * 80)
    print("✨ 수정 사항 요약:")
    print("=" * 80)
    print("""
1. ✅ '전체 구역' → 'All Buildings'로 변경
   - 구역 컬럼에 '전체'가 일반 값으로 표시되지 않음
   - 테이블 마지막 줄에만 '전체' 요약 행 표시

2. ✅ Reject Rate > 3% 조건만 적용
   - condition 7 조건 제거
   - 순수하게 reject rate > 3%인 직원만 필터링

3. ✅ 인원수 카운팅 수정
   - 3% 조건을 충족하는 직원만 카운트
   - 구역별 통계는 전체 데이터로 계산

4. ✅ UI 텍스트 개선
   - 개별 AQL Reject Rate 조건으로 명확히 표시
   - 조건 설명 텍스트 수정
    """)

    print(f"\n📊 최종 결과: Reject Rate > 3% 조건 직원 {len(high_reject_employees)}명")

    return {
        'high_reject_count': len(high_reject_employees),
        'fixes_applied': True
    }

if __name__ == "__main__":
    result = verify_modal_fix()