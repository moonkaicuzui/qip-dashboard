#!/usr/bin/env python3
"""
대시보드 검증 스크립트
생성된 dashboard_version4.html이 제대로 작동하는지 확인
"""

import re
from pathlib import Path

def validate_dashboard():
    """대시보드 HTML 검증"""
    
    dashboard_path = Path("output_files/dashboard_version4.html")
    
    if not dashboard_path.exists():
        print(f"❌ 대시보드 파일을 찾을 수 없습니다: {dashboard_path}")
        return False
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 검증 항목들
    checks = {
        "Bootstrap CSS": '<link href="https://cdn.jsdelivr.net/npm/bootstrap',
        "Chart.js": '<script src="https://cdn.jsdelivr.net/npm/chart.js',
        "Employee Data": 'const employeeData = [',
        "Type Summary Function": 'function generateSummaryData()',
        "July Incentive": 'july_incentive',
        "Type-1 Data": '"type":"TYPE-1"',
        "Type-2 Data": '"type":"TYPE-2"',
        "Type-3 Data": '"type":"TYPE-3"',
        "Window Onload": 'window.onload = function()',
        "Payment Rate": 'window.currentPaymentRate',
        "Type Summary Table": 'id="typeSummaryBody"'
    }
    
    print("📋 대시보드 검증 결과:")
    print("-" * 60)
    
    all_passed = True
    for check_name, pattern in checks.items():
        if pattern in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Not Found")
            all_passed = False
    
    # JavaScript 오류 체크
    print("\n📝 JavaScript 구문 검증:")
    print("-" * 60)
    
    # const 중복 선언 체크
    const_declarations = re.findall(r'const (\w+) =', content)
    duplicates = set([x for x in const_declarations if const_declarations.count(x) > 1])
    
    if duplicates:
        print(f"⚠️ 중복 const 선언 발견: {', '.join(duplicates)}")
        # paymentRate는 함수 스코프 내에서 중복될 수 있으므로 경고만
        if 'paymentRate' in duplicates:
            print("   (paymentRate는 다른 함수 스코프에서 사용되므로 정상일 수 있음)")
    else:
        print("✅ const 중복 선언 없음")
    
    # 템플릿 변수 체크
    template_vars = re.findall(r'\$\{\{(\w+)', content)
    print(f"\n📊 템플릿 변수 수: {len(set(template_vars))}")
    
    # 직원 데이터 카운트
    employee_count = content.count('"emp_no":"')
    print(f"👥 직원 데이터 수: {employee_count}명")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 대시보드 검증 완료 - 모든 항목 통과!")
    else:
        print("⚠️ 일부 검증 항목 실패 - 확인 필요")
    
    return all_passed

if __name__ == "__main__":
    validate_dashboard()