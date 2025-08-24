#!/usr/bin/env python3
"""간단한 검증 테스트"""

import pandas as pd
from pathlib import Path

# AQL 파일 읽기
file_path = Path('input_files/AQL history/1.HSRG AQL REPORT-AUGUST.2025.csv')
df = pd.read_csv(file_path, encoding='utf-8-sig')

print("=" * 60)
print("Building별 AQL Reject Rate 검증")
print("=" * 60)

buildings = ['A', 'B', 'C', 'D']
for building in buildings:
    # NORMAL PO 데이터만 필터
    building_data = df[
        (df['BUILDING'] == building) & 
        (df['REPACKING PO'] == 'NORMAL PO')
    ]
    
    if not building_data.empty:
        total = len(building_data)
        fails = len(building_data[building_data['RESULT'] == 'FAIL'])
        rate = (fails / total * 100) if total > 0 else 0
        
        status = "⚠️ 문제" if rate >= 3.0 else "✅ 정상"
        print(f"{status} Building {building}: {total}건 중 {fails}건 실패, Reject Rate: {rate:.2f}%")

print("\n담당자별 영향:")
print("- Building B (5.10%) → CAO THỊ TỐ NGUYÊN (618060092)")
print("- Building D (2.89%) → DANH THỊ KIM ANH (619070185)")
print("\n⚠️ Building B의 reject rate가 3%를 초과하여 해당 담당자는 인센티브가 0이 됩니다.")