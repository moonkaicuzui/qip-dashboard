#!/usr/bin/env python3
"""
구역별 AQL Reject Rate 모달 개선 - 조건 7번, 8번 구분 표시
"""

import pandas as pd
import json

# Excel 데이터에서 구역별 통계 생성
df = pd.read_csv('output_files/output_QIP_incentive_september_2025_최종완성버전_v6.0_Complete_enhanced.csv', encoding='utf-8-sig')
df_active = df[(df['Include_In_Dashboard'] == True) | (df['Include_In_Dashboard'] == 'Y')]

# 구역 매핑
building_map = {
    'A': 'Building A', 'B': 'Building B', 'C': 'Building C',
    'D': 'Building D', 'All': 'All Buildings'
}

# 조건 7번, 8번 분석
cond7_fail = df_active[df_active['cond_7_aql_team_area'] == 'FAIL']
cond8_fail = df_active[df_active['cond_8_area_reject'] == 'FAIL']

print(f"""
========================================
📊 구역별 AQL 분석 결과
========================================

🔍 조건 충족 현황:
------------------
• 조건 7번 (팀/구역 3개월 연속 실패) 미충족: {len(cond7_fail)}명
• 조건 8번 (구역 reject rate > 3%) 미충족: {len(cond8_fail)}명

📌 개선할 모달 구조:
-------------------
1. 구역별 통계 테이블 (총 AQL 건수, PASS, FAIL, Reject%)
2. 조건 7번 미충족 직원 목록
3. 조건 8번 미충족 직원 목록 (reject rate > 3%)
4. KPI 카드에는 조건 8번 미충족 인원 표시

✅ 실제 데이터 기반으로 정확한 구역별 통계 표시
""")