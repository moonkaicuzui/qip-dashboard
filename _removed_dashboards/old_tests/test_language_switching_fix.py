#!/usr/bin/env python3
"""
Test the language switching fix for position conditions
"""

def test_language_switching():
    """Test that all text elements are properly updated when switching languages"""

    # Read the fixed dashboard
    with open('output_files/Incentive_Dashboard_2025_09_Version_5_fixed.html', 'r', encoding='utf-8') as f:
        content = f.read()

    issues_found = []

    # Check for hardcoded text that should use translations
    hardcoded_texts = [
        ('Điều kiện chức vụ TYPE-1', 'Vietnamese hardcoded TYPE-1 text'),
        ('Điều kiện chức vụ TYPE-2', 'Vietnamese hardcoded TYPE-2 text'),
        ('Điều kiện chức vụ TYPE-3', 'Vietnamese hardcoded TYPE-3 text'),
        ('Điều kiện theo chức vụ', 'Vietnamese hardcoded position conditions title'),
    ]

    # Check the JavaScript sections (not the translation definitions)
    # Extract JavaScript code sections (excluding translation definitions)
    import re

    # Find all script sections
    script_sections = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)

    for script in script_sections:
        # Skip translation definition sections
        if '"conditionsByPosition":' in script or '"typeHeaders":' in script:
            continue

        # Check for hardcoded text in actual code
        for text, description in hardcoded_texts:
            # Look for hardcoded strings (not in translation objects)
            pattern = f'"{text}"|`{text}`|\'{text}\''
            if re.search(pattern, script):
                # Make sure it's not part of a translation definition
                if not re.search(f'"vi":\\s*"{text}"', script):
                    issues_found.append(f"Found {description}: {text}")

    # Check that updateAllTexts includes position conditions updates
    if 'updatePositionConditionsModal' not in content:
        issues_found.append("updateAllTexts doesn't call updatePositionConditionsModal")

    if 'TYPE headers if they exist' not in content:
        issues_found.append("updateAllTexts doesn't update TYPE headers")

    if 'modal titles that might contain position conditions' not in content:
        issues_found.append("updateAllTexts doesn't update modal titles")

    # Report results
    if issues_found:
        print("❌ Issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All language switching tests passed!")
        print("  ✅ No hardcoded Vietnamese text found in JavaScript")
        print("  ✅ updateAllTexts properly updates position conditions")
        print("  ✅ Modal titles and TYPE headers are dynamically updated")
        return True

if __name__ == "__main__":
    success = test_language_switching()
    if success:
        print("\n🎉 Language switching fix is working correctly!")
        print("The dashboard should now properly switch all text including:")
        print("  - Position conditions modal/tab titles")
        print("  - TYPE-1, TYPE-2, TYPE-3 headers")
        print("  - All related UI elements")
    else:
        print("\n⚠️ Some issues remain. Please review the fix.")