#!/usr/bin/env python3
"""
Verify that all 31 translation fixes have been properly applied
"""

def verify_translation_fixes():
    """Verify all translation fixes are applied"""

    print("=" * 80)
    print("🔍 Translation Fix Verification Report")
    print("=" * 80)

    # Read the generated HTML
    with open('output_files/Incentive_Dashboard_2025_09_Version_5.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Track verification results
    checks = []

    # 1. Validation tab
    checks.append(('Validation tab translation',
                  'translations.tabs?.validation?.[lang]' in html))

    # 2. Individual details - pass/fail
    checks.append(('Pass/Fail status translation',
                  'translations.individualDetails?.conditionStatus?.pass' in html or
                  'translations.individualDetails?.conditionStatus?.fail' in html))

    # 3. Org Chart main texts
    checks.append(('Org chart excluded positions note',
                  'translations.orgChart?.excludedPositionsNote' in html))
    checks.append(('Entire organization translation',
                  'translations.orgChart?.entireOrganization' in html))
    checks.append(('TYPE-1 manager structure',
                  'translations.orgChart?.type1ManagerStructure' in html))

    # 4. Org Chart modal labels
    modal_translations = [
        'orgChartModal?.position',
        'orgChartModal?.calculationDetails',
        'orgChartModal?.teamLineLeaderCount',
        'orgChartModal?.lineLeadersReceiving',
        'orgChartModal?.lineLeaderAverage',
        'orgChartModal?.calculationFormula',
        'orgChartModal?.teamLineLeaderDetails',
        'orgChartModal?.assemblyInspectorDetails',
        'orgChartModal?.name',
        'orgChartModal?.incentive',
        'orgChartModal?.includeInAverage',
        'orgChartModal?.receivingStatus',
        'orgChartModal?.total',
        'orgChartModal?.average',
        'orgChartModal?.people'
    ]

    for trans in modal_translations:
        checks.append((f'Org chart modal: {trans.split("?.")[-1]}',
                      trans in html))

    # 5. Non-payment reasons
    payment_reasons = [
        'actualWorkingDays0',
        'unauthorizedAbsence',
        'absenceRate12',
        'minWorkingDays',
        'teamAreaAQL',
        'fprsPassRate',
        'fprsZeroQty'
    ]

    for reason in payment_reasons:
        checks.append((f'Non-payment reason: {reason}',
                      f'nonPaymentReasons?.{reason}' in html))

    # Print results
    print("\n📊 Verification Results:")
    print("-" * 40)

    passed = 0
    failed = 0

    for check_name, result in checks:
        if result:
            print(f"✅ {check_name}")
            passed += 1
        else:
            print(f"❌ {check_name}")
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print("📈 Summary:")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{len(checks)}")
    print(f"❌ Failed: {failed}/{len(checks)}")

    if failed == 0:
        print("\n🎉 All translation fixes have been successfully applied!")
    else:
        print(f"\n⚠️  {failed} items still need attention")

    # Check for remaining hardcoded Korean
    print("\n📋 Checking for remaining hardcoded Korean text:")
    print("-" * 40)

    korean_patterns = [
        '요약 및 시스템 검증',
        '전체 조직',
        'TYPE-1 관리자 인센티브 구조',
        '직급:',
        '계산 과정 상세',
        '팀 내 LINE LEADER 수',
        '인센티브 받은 LINE LEADER',
        '평균 계산 포함',
        '수령 여부',
        '실제 근무일 0일',
        '결근율 12% 초과',
        '최소 근무일 미달'
    ]

    remaining_hardcoded = []
    for pattern in korean_patterns:
        # Check if pattern exists outside of translation fallback
        if pattern in html:
            # Count occurrences
            total = html.count(pattern)
            in_fallback = html.count(f"|| '{pattern}'")
            if total > in_fallback:
                remaining_hardcoded.append((pattern, total - in_fallback))

    if remaining_hardcoded:
        print("⚠️  Found remaining hardcoded text:")
        for text, count in remaining_hardcoded:
            print(f"  - '{text}': {count} instances")
    else:
        print("✅ No remaining hardcoded Korean text found")

    return passed, failed

if __name__ == "__main__":
    passed, failed = verify_translation_fixes()

    # Exit with appropriate code
    exit(0 if failed == 0 else 1)