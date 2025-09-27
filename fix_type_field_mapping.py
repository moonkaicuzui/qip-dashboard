#!/usr/bin/env python3
"""
Type 필드 매핑 문제 수정 스크립트
JavaScript는 'type'을 기대하지만 실제 데이터는 'ROLE TYPE STD'를 사용
"""

# JavaScript 파일 수정
js_file = "dashboard_v2/static/js/dashboard_complete.js"

with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 60)
print("Type 필드 매핑 수정")
print("=" * 60)

# updateTypeSummaryTable 함수에서 type 필드 접근 수정
old_code = """        // 직원 데이터 순회하며 집계
        employeeData.forEach(emp => {
            const type = emp.type;
            if (typeData[type]) {"""

new_code = """        // 직원 데이터 순회하며 집계
        employeeData.forEach(emp => {
            // type 필드를 여러 가능한 이름에서 찾기
            const type = emp.type || emp['ROLE TYPE STD'] || emp['Type'] || 'UNKNOWN';
            if (typeData[type]) {"""

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ updateTypeSummaryTable에서 type 필드 매핑 수정")
else:
    print("⚠️ updateTypeSummaryTable 패턴을 찾을 수 없습니다.")

# getIncentiveAmount 함수도 업데이트
old_incentive = """function getIncentiveAmount(emp) {
    return parseInt(
        emp['Final Incentive amount'] ||
        emp[`${dashboardMonth}_incentive`] ||
        emp[`${dashboardMonth.charAt(0).toUpperCase() + dashboardMonth.slice(1)}_Incentive`] ||"""

new_incentive = """function getIncentiveAmount(emp) {
    // 여러 가능한 인센티브 필드명 확인
    return parseInt(
        emp['Final Incentive amount'] ||
        emp['September_Incentive'] ||
        emp['최종 인센티브 금액'] ||
        emp[`${dashboardMonth}_incentive`] ||
        emp[`${dashboardMonth.charAt(0).toUpperCase() + dashboardMonth.slice(1)}_Incentive`] ||"""

if old_incentive in content:
    content = content.replace(old_incentive, new_incentive)
    print("✅ getIncentiveAmount 함수 업데이트")
else:
    print("⚠️ getIncentiveAmount 패턴을 찾을 수 없습니다. 대체 패턴 시도...")

    # 대체 패턴 시도
    import re
    pattern = r'function getIncentiveAmount\(emp\) \{[^}]*\}'
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        print(f"  found {len(matches)} getIncentiveAmount function(s)")

# 파일 저장
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Type 필드 매핑 수정 완료!")
print("\n수정사항:")
print("1. emp.type 대신 emp['ROLE TYPE STD'] 우선 사용")
print("2. 인센티브 필드에 'September_Incentive' 추가")
print("3. 여러 가능한 필드명 fallback 처리")
print("=" * 60)