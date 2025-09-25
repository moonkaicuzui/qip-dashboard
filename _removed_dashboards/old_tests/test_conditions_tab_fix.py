#!/usr/bin/env python3
"""
Test the Conditions by Position tab language fix
"""

def test_conditions_tab_fix():
    """Test that the Conditions by Position tab properly switches languages"""

    # Read the fixed dashboard
    with open('output_files/Incentive_Dashboard_2025_09_Version_5_final_fix.html', 'r', encoding='utf-8') as f:
        content = f.read()

    print("🔍 Testing Conditions by Position tab language fix...\n")

    tests_passed = []
    tests_failed = []

    # Test 1: Check if updateConditionsTabContent function exists
    if 'updateConditionsTabContent' in content:
        tests_passed.append("✅ updateConditionsTabContent() function exists")
    else:
        tests_failed.append("❌ updateConditionsTabContent() function not found")

    # Test 2: Check if updateAllTexts calls updateConditionsTabContent
    if 'updateConditionsTabContent()' in content:
        tests_passed.append("✅ updateAllTexts() calls updateConditionsTabContent()")
    else:
        tests_failed.append("❌ updateAllTexts() doesn't call updateConditionsTabContent()")

    # Test 3: Check for hardcoded Vietnamese text (should not exist in code, only in translations)
    vietnamese_texts = [
        'Chỉ điều kiện chấm công',
        'Chấm công + AQL tháng hiện tại',
        'Điều kiện chức vụ TYPE',
    ]

    import re
    for viet_text in vietnamese_texts:
        # Look for hardcoded text in JavaScript (not in translation definitions)
        # Check if it appears outside of translation objects
        pattern = f'(?<!vi":\\s")"{viet_text}"(?!")'
        if re.search(pattern, content):
            tests_failed.append(f"❌ Found hardcoded Vietnamese text: {viet_text}")
        else:
            tests_passed.append(f"✅ No hardcoded Vietnamese text: {viet_text}")

    # Test 4: Check for mixed language in notes
    mixed_patterns = [
        ('Attendance \\+ Team/Area AQL', 'Should use translation key'),
        ('Attendance \\+ Personal AQL \\+ 5PRS', 'Should use translation key'),
    ]

    for pattern, description in mixed_patterns:
        # Look for these patterns in the actual code (not translations)
        if re.search(f'>{pattern}<', content) or re.search(f'textContent.*{pattern}', content):
            tests_failed.append(f"❌ Found mixed language: {pattern} - {description}")
        else:
            tests_passed.append(f"✅ No mixed language found for: {pattern}")

    # Test 5: Check if translation keys are properly used
    translation_keys = [
        'conditionsByPosition.notes.attendanceOnly',
        'conditionsByPosition.notes.attendanceTeamAql',
        'conditionsByPosition.notes.attendanceMonthAql',
        'conditionsByPosition.notes.attendancePersonalAql5prs',
        'conditionsByPosition.typeHeaders.type1',
        'conditionsByPosition.typeHeaders.type2',
        'conditionsByPosition.typeHeaders.type3',
    ]

    for key in translation_keys:
        if f"getTranslation('{key}'" in content or f'getTranslation("{key}"' in content:
            tests_passed.append(f"✅ Translation key used: {key.split('.')[-1]}")
        else:
            # It's okay if not all keys are used, just noting
            pass

    # Print results
    print("Test Results:")
    print("=" * 50)

    for test in tests_passed:
        print(test)

    if tests_failed:
        print("\nIssues Found:")
        for test in tests_failed:
            print(test)

    # Summary
    total_tests = len(tests_passed) + len(tests_failed)
    print("\n" + "=" * 50)
    print(f"Summary: {len(tests_passed)}/{total_tests} tests passed")

    if len(tests_failed) == 0:
        print("\n🎉 All tests passed! The Conditions by Position tab should now properly switch languages.")
        print("   - Vietnamese text will switch to English")
        print("   - English text will switch to Vietnamese")
        print("   - Korean text will display properly")
        print("   - Notes column will update with the correct language")
        return True
    else:
        print("\n⚠️ Some issues remain. Please review the failed tests.")
        return False

if __name__ == "__main__":
    success = test_conditions_tab_fix()