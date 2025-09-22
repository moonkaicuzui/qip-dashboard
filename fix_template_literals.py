#!/usr/bin/env python3
"""
템플릿 리터럴 문제 해결 - JavaScript 오류의 실제 원인 수정
"""

import re
import shutil

def fix_template_literals():
    """템플릿 리터럴을 단순 텍스트로 변경"""

    print("=" * 80)
    print("🔧 템플릿 리터럴 수정 - JavaScript 오류 해결")
    print("=" * 80)

    # Python 파일 백업
    py_file = 'integrated_dashboard_final.py'
    backup_file = py_file + '.backup2'
    shutil.copy(py_file, backup_file)
    print(f"✅ 백업 생성: {backup_file}")

    # Python 파일 읽기
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 템플릿 리터럴 패턴을 찾아서 교체
    replacements = [
        # 번역 템플릿 리터럴을 직접 텍스트로 변경
        (r"\$\{\{translations\.tabs\?\.validation\?\.\[lang\] \|\| '요약 및 시스템 검증'\}\}", "'요약 및 시스템 검증'"),
        (r"\$\{\{translations\.individualDetails\?\.conditionStatus\?\.pass\?\.\[lang\] \|\| '통과'\}\}", "'통과'"),
        (r"\$\{\{translations\.individualDetails\?\.conditionStatus\?\.fail\?\.\[lang\] \|\| '실패'\}\}", "'실패'"),
        (r"\$\{\{translations\.orgChart\?\.entireOrganization\?\.\[lang\] \|\| '전체 조직'\}\}", "'전체 조직'"),
        (r"\$\{\{translations\.orgChart\?\.type1ManagerStructure\?\.\[lang\] \|\| 'TYPE-1 관리자 인센티브 구조'\}\}", "'TYPE-1 관리자 인센티브 구조'"),

        # 모달 관련 템플릿 리터럴
        (r"\$\{\{translations\.orgChartModal\?\.position\?\.\[lang\] \|\| '직급'\}\}", "'직급'"),
        (r"\$\{\{translations\.orgChartModal\?\.calculationDetails\?\.\[lang\] \|\| '계산 과정 상세'\}\}", "'계산 과정 상세'"),
        (r"\$\{\{translations\.orgChartModal\?\.teamLineLeaderCount\?\.\[lang\] \|\| '팀 내 LINE LEADER 수'\}\}", "'팀 내 LINE LEADER 수'"),
        (r"\$\{\{translations\.orgChartModal\?\.lineLeadersReceiving\?\.\[lang\] \|\| '인센티브 받은 LINE LEADER'\}\}", "'인센티브 받은 LINE LEADER'"),
        (r"\$\{\{translations\.orgChartModal\?\.lineLeaderAverage\?\.\[lang\] \|\| 'LINE LEADER 평균 인센티브'\}\}", "'LINE LEADER 평균 인센티브'"),
        (r"\$\{\{translations\.orgChartModal\?\.calculationFormula\?\.\[lang\] \|\| '계산식'\}\}", "'계산식'"),
        (r"\$\{\{translations\.orgChartModal\?\.name\?\.\[lang\] \|\| '이름'\}\}", "'이름'"),
        (r"\$\{\{translations\.orgChartModal\?\.incentive\?\.\[lang\] \|\| '인센티브'\}\}", "'인센티브'"),
        (r"\$\{\{translations\.orgChartModal\?\.includeInAverage\?\.\[lang\] \|\| '평균 계산 포함'\}\}", "'평균 계산 포함'"),
        (r"\$\{\{translations\.orgChartModal\?\.receivingStatus\?\.\[lang\] \|\| '수령 여부'\}\}", "'수령 여부'"),
        (r"\$\{\{translations\.orgChartModal\?\.total\?\.\[lang\] \|\| '합계'\}\}", "'합계'"),
        (r"\$\{\{translations\.orgChartModal\?\.average\?\.\[lang\] \|\| '평균'\}\}", "'평균'"),
    ]

    fixes = 0
    for pattern, replacement in replacements:
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            fixes += matches
            print(f"✅ 수정: {pattern[:50]}... → {replacement} ({matches}개)")

    # 더 일반적인 패턴으로 나머지 캐치
    general_pattern = r"\$\{\{translations\.[^}]+\}\}"
    remaining = re.findall(general_pattern, content)

    if remaining:
        print(f"\n⚠️ 추가로 {len(remaining)}개의 번역 템플릿 발견")
        for item in set(remaining[:5]):  # 처음 5개만 표시
            print(f"   - {item[:80]}...")

    # 수정된 파일 저장
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ 총 {fixes}개 템플릿 리터럴 수정")
    print(f"📁 파일 업데이트: {py_file}")

    return fixes

def main():
    """메인 실행"""

    # 템플릿 리터럴 수정
    fixes = fix_template_literals()

    if fixes > 0:
        print("\n🔄 대시보드를 재생성해야 합니다:")
        print("   python integrated_dashboard_final.py --month 9 --year 2025")
    else:
        print("\n⚠️ 수정할 템플릿 리터럴을 찾지 못했습니다.")
        print("   Python 파일의 실제 패턴을 다시 확인해야 합니다.")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()