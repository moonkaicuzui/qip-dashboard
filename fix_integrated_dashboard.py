#!/usr/bin/env python3
"""
integrated_dashboard_final.py의 Type별 요약 테이블 문제 수정
action.sh가 사용하는 실제 파일을 수정
"""

import shutil
from datetime import datetime

print("=" * 60)
print("🔧 integrated_dashboard_final.py 수정")
print("=" * 60)

# 백업 생성
original_file = "integrated_dashboard_final.py"
backup_file = f"integrated_dashboard_final.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(original_file, backup_file)
print(f"✅ 백업 생성: {backup_file}")

# 파일 읽기
with open(original_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. updateTypeSummaryTable 함수에서 type 필드 매핑 수정
old_type_code = """            // 직원 데이터 순회하며 집계
            employeeData.forEach(emp => {{
                const type = emp.type;
                if (typeData[type]) {{"""

new_type_code = """            // 직원 데이터 순회하며 집계
            employeeData.forEach(emp => {{
                // type 필드를 여러 가능한 이름에서 찾기
                const type = emp.type || emp['ROLE TYPE STD'] || emp['Type'] || 'UNKNOWN';
                if (typeData[type]) {{"""

if old_type_code in content:
    content = content.replace(old_type_code, new_type_code)
    print("✅ Type 필드 매핑 수정 완료")
else:
    print("⚠️ Type 필드 매핑 패턴을 찾을 수 없습니다.")

# 2. 인센티브 금액 필드 수정
old_amount_code = """                    const amount = parseInt(emp[dashboardMonth + '_incentive']) || 0;"""

new_amount_code = """                    // 여러 가능한 인센티브 필드명 확인
                    const amount = parseInt(
                        emp['Final Incentive amount'] ||
                        emp['September_Incentive'] ||
                        emp['september_incentive'] ||
                        emp[dashboardMonth + '_incentive'] ||
                        emp[dashboardMonth.charAt(0).toUpperCase() + dashboardMonth.slice(1) + '_Incentive'] ||
                        0
                    );"""

if old_amount_code in content:
    content = content.replace(old_amount_code, new_amount_code)
    print("✅ 인센티브 금액 필드 매핑 수정 완료")
else:
    print("⚠️ 인센티브 금액 패턴을 찾을 수 없습니다.")

# 3. 초기화 시 강제 실행 코드 추가
force_update_code = """
        // Type별 테이블 강제 업데이트 함수
        window.forceUpdateTypeSummary = function() {{
            console.log('=== Type별 요약 테이블 강제 업데이트 실행 ===');
            updateTypeSummaryTable();
        }};

        // 페이지 로드 후 1초 뒤 자동 실행
        setTimeout(function() {{
            console.log('Type별 테이블 자동 업데이트 시도...');
            if (typeof updateTypeSummaryTable === 'function') {{
                updateTypeSummaryTable();
            }}
            if (window.forceUpdateTypeSummary) {{
                window.forceUpdateTypeSummary();
            }}
        }}, 1000);
"""

# window.onload 함수 끝부분 찾기
window_onload_pattern = "window.onload = function() {"

if window_onload_pattern in content:
    # window.onload 함수의 끝 찾기
    onload_start = content.find(window_onload_pattern)
    if onload_start != -1:
        # 해당 함수의 마지막 중괄호 찾기
        brace_count = 0
        i = onload_start + len(window_onload_pattern)
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                if brace_count == 0:
                    # window.onload 함수의 끝
                    content = content[:i] + force_update_code + "\n" + content[i:]
                    print("✅ 강제 업데이트 코드 추가 완료")
                    break
                brace_count -= 1
            i += 1
else:
    print("⚠️ window.onload 패턴을 찾을 수 없습니다.")

# 4. 디버깅 로그 추가
debug_log = """
                console.log('Type 확인:', type, '직원:', emp.name || emp['Full Name'], '금액:', amount);
"""

type_check_pattern = "if (typeData[type]) {{"
if type_check_pattern in content:
    content = content.replace(type_check_pattern, type_check_pattern + debug_log)
    print("✅ 디버깅 로그 추가 완료")

# 파일 저장
with open(original_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ integrated_dashboard_final.py 수정 완료!")
print("\n📌 테스트 방법:")
print("1. action.sh 실행 또는")
print("2. 직접 실행: python integrated_dashboard_final.py --month 9 --year 2025")
print("3. 브라우저에서 확인: open output_files/Incentive_Dashboard_2025_09_Version_5.html")
print("4. 콘솔에서 확인(F12): window.forceUpdateTypeSummary()")
print("=" * 60)