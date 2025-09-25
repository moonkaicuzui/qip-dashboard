#!/usr/bin/env python3
"""
Fix language switching for position conditions modal/view
"""

import re

def fix_position_conditions_language():
    """Fix the language switching issue for position conditions"""

    # Read the current dashboard file
    with open('output_files/Incentive_Dashboard_2025_09_Version_5.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and fix the showPositionConditionsModal function if it exists
    if 'showPositionConditionsModal' in content:
        print("✅ Found showPositionConditionsModal function")

        # Replace hardcoded text with translation calls
        replacements = [
            # Replace hardcoded Vietnamese text
            (r'Điều kiện chức vụ TYPE-1', "getTranslation('conditionsByPosition.typeHeaders.type1', currentLanguage)"),
            (r'Điều kiện chức vụ TYPE-2', "getTranslation('conditionsByPosition.typeHeaders.type2', currentLanguage)"),
            (r'Điều kiện chức vụ TYPE-3', "getTranslation('conditionsByPosition.typeHeaders.type3', currentLanguage)"),

            # Replace hardcoded English text
            (r'TYPE-1 Position Conditions', "getTranslation('conditionsByPosition.typeHeaders.type1', currentLanguage)"),
            (r'TYPE-2 Position Conditions', "getTranslation('conditionsByPosition.typeHeaders.type2', currentLanguage)"),
            (r'TYPE-3 Position Conditions', "getTranslation('conditionsByPosition.typeHeaders.type3', currentLanguage)"),

            # Replace hardcoded Korean text
            (r'TYPE-1 직급별 조건', "getTranslation('conditionsByPosition.typeHeaders.type1', currentLanguage)"),
            (r'TYPE-2 직급별 조건', "getTranslation('conditionsByPosition.typeHeaders.type2', currentLanguage)"),
            (r'TYPE-3 직급별 조건', "getTranslation('conditionsByPosition.typeHeaders.type3', currentLanguage)"),

            # Fix tab titles
            (r'Điều kiện theo chức vụ', "getTranslation('conditionsByPosition.title', currentLanguage)"),
            (r'Conditions by Position', "getTranslation('conditionsByPosition.title', currentLanguage)"),
            (r'직급별 적용 조건', "getTranslation('conditionsByPosition.title', currentLanguage)"),
        ]

        for old_text, new_text in replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                print(f"  ✅ Replaced: {old_text[:30]}...")

    # Add a function to update position conditions modal if it doesn't exist in updateAllTexts
    update_position_conditions = """
            // Update position conditions modal if it exists
            if (typeof updatePositionConditionsModal === 'function') {
                updatePositionConditionsModal();
            }

            // Update any position conditions content that might be cached
            const positionConditionElements = document.querySelectorAll('[data-position-condition]');
            positionConditionElements.forEach(element => {
                const conditionKey = element.getAttribute('data-position-condition');
                if (conditionKey) {
                    element.textContent = getTranslation(conditionKey, currentLanguage);
                }
            });

            // Update TYPE headers if they exist
            const typeHeaders = document.querySelectorAll('[id*="typeHeader"], [class*="type-header"]');
            typeHeaders.forEach(header => {
                const text = header.textContent.trim();
                if (text.includes('TYPE-1') || text.includes('Điều kiện chức vụ TYPE-1')) {
                    header.textContent = getTranslation('conditionsByPosition.typeHeaders.type1', currentLanguage);
                } else if (text.includes('TYPE-2') || text.includes('Điều kiện chức vụ TYPE-2')) {
                    header.textContent = getTranslation('conditionsByPosition.typeHeaders.type2', currentLanguage);
                } else if (text.includes('TYPE-3') || text.includes('Điều kiện chức vụ TYPE-3')) {
                    header.textContent = getTranslation('conditionsByPosition.typeHeaders.type3', currentLanguage);
                }
            });

            // Update any modal titles that might contain position conditions text
            const modalTitles = document.querySelectorAll('.modal-title');
            modalTitles.forEach(title => {
                const text = title.textContent.trim();
                if (text.includes('Conditions by Position') || text.includes('Điều kiện theo chức vụ') || text.includes('직급별 적용 조건')) {
                    title.textContent = getTranslation('conditionsByPosition.title', currentLanguage);
                }
            });
"""

    # Find the end of updateAllTexts function and add the update code
    pattern = r'(function updateAllTexts\(\) \{[^}]*)(}\s*$)'

    # First, find the updateAllTexts function
    update_all_texts_match = re.search(r'function updateAllTexts\(\) \{.*?\n        \}', content, re.DOTALL)

    if update_all_texts_match:
        # Get the function content
        func_content = update_all_texts_match.group()

        # Add the update code before the closing brace if not already there
        if 'updatePositionConditionsModal' not in func_content:
            # Find the last closing brace of the function
            last_brace_pos = func_content.rfind('}')

            # Insert the update code before the closing brace
            new_func_content = func_content[:last_brace_pos] + update_position_conditions + '\n        ' + func_content[last_brace_pos:]

            # Replace in the main content
            content = content.replace(func_content, new_func_content)
            print("✅ Added position conditions update to updateAllTexts function")

    # Save the fixed file
    output_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_fixed.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Fixed dashboard saved to: {output_file}")
    return output_file

if __name__ == "__main__":
    fix_position_conditions_language()