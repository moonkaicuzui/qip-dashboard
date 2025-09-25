#!/usr/bin/env python3
"""
Fix language switching for Conditions by Position tab
"""

import re

def fix_conditions_tab_language():
    """Fix the language switching issue for Conditions by Position tab"""

    # Read the current dashboard file
    with open('output_files/Incentive_Dashboard_2025_09_Version_5_fixed.html', 'r', encoding='utf-8') as f:
        content = f.read()

    print("🔍 Analyzing dashboard for Conditions by Position tab...")

    # First, let's find if there's a function that creates the conditions tab
    conditions_tab_found = False

    # Check if there's any hardcoded text in the tab content
    hardcoded_patterns = [
        # Vietnamese text
        ('Chỉ điều kiện chấm công', 'attendanceOnly'),
        ('Chấm công \\+ AQL tháng hiện tại \\(Đặc biệt\\)', 'attendanceMonthAql'),
        ('Điều kiện chức vụ TYPE', 'typeHeaders'),

        # Mixed language issues
        ('Attendance \\+ Team/Area AQL', 'attendanceTeamAql'),
        ('Attendance \\+ Personal AQL \\+ 5PRS', 'attendancePersonalAql5prs'),
        ('Attendance \\+ Area reject', 'attendanceAreaReject'),
    ]

    replacements_made = []

    # Look for the tab content generation
    if 'Conditions by Position' in content or 'conditionsByPosition' in content:
        conditions_tab_found = True
        print("✅ Found Conditions by Position tab")

        # Fix hardcoded text in JavaScript sections
        # Find all JavaScript that might be generating the tab content

        # Pattern 1: Direct HTML generation with hardcoded text
        for pattern, translation_key in hardcoded_patterns:
            # Look for the pattern in HTML string literals
            regex_patterns = [
                f'>{pattern}<',  # In HTML tags
                f'"{pattern}"',  # In double quotes
                f"'{pattern}'",  # In single quotes
                f'`{pattern}`',  # In template literals
                f'innerHTML.*{pattern}',  # In innerHTML assignments
                f'textContent.*{pattern}',  # In textContent assignments
            ]

            for regex_pattern in regex_patterns:
                if re.search(regex_pattern, content):
                    # Replace with translation function call
                    if 'TYPE' in pattern:
                        # TYPE headers need special handling
                        for i in [1, 2, 3]:
                            old_pattern = f'{pattern}-{i}'
                            new_text = f'${{getTranslation("conditionsByPosition.typeHeaders.type{i}", currentLanguage)}}'
                            content = re.sub(old_pattern, new_text, content)
                            if old_pattern in content:
                                replacements_made.append(f"TYPE-{i} header")
                    else:
                        new_text = f'${{getTranslation("conditionsByPosition.notes.{translation_key}", currentLanguage)}}'
                        content = re.sub(pattern, new_text, content)
                        replacements_made.append(translation_key)

    # Add a comprehensive function to update all conditions tab content
    update_conditions_tab = """
        // Function to update Conditions by Position tab content
        function updateConditionsTabContent() {
            // Update all elements in conditions tab
            const conditionsTab = document.querySelector('[data-tab="conditions-position"], #conditions-position-tab, .conditions-position-content');

            if (!conditionsTab) return;

            // Update TYPE headers
            const typeHeaders = conditionsTab.querySelectorAll('h4, h5, h6, .type-header');
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

            // Update table headers
            const tables = conditionsTab.querySelectorAll('table');
            tables.forEach(table => {
                const headers = table.querySelectorAll('th');
                headers.forEach((th, index) => {
                    const text = th.textContent.trim().toLowerCase();
                    if (text.includes('position') || text.includes('chức vụ')) {
                        th.textContent = getTranslation('conditionsByPosition.tableHeaders.position', currentLanguage);
                    } else if (text.includes('applied') || text.includes('điều kiện áp dụng')) {
                        th.textContent = getTranslation('conditionsByPosition.tableHeaders.appliedConditions', currentLanguage);
                    } else if (text.includes('count') || text.includes('số điều kiện')) {
                        th.textContent = getTranslation('conditionsByPosition.tableHeaders.conditionCount', currentLanguage);
                    } else if (text.includes('notes') || text.includes('ghi chú')) {
                        th.textContent = getTranslation('conditionsByPosition.tableHeaders.notes', currentLanguage);
                    }
                });

                // Update notes in table cells
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const notesCell = row.cells[row.cells.length - 1]; // Last cell is usually notes
                    if (notesCell) {
                        const text = notesCell.textContent.trim();

                        // Map text to translation keys
                        const notesMappings = {
                            'Chỉ điều kiện chấm công': 'attendanceOnly',
                            'Attendance only': 'attendanceOnly',
                            'Chi điều kiện chấm công': 'attendanceOnly',

                            'Attendance + Team/Area AQL': 'attendanceTeamAql',
                            'Chấm công + AQL nhóm/khu vực': 'attendanceTeamAql',

                            'Chấm công + AQL tháng hiện tại (Đặc biệt)': 'attendanceMonthAql',
                            'Attendance + Monthly AQL (Special calculation)': 'attendanceMonthAql',

                            'Attendance + Personal AQL + 5PRS': 'attendancePersonalAql5prs',
                            'Chấm công + AQL cá nhân + 5PRS': 'attendancePersonalAql5prs',

                            'Attendance + Team/Area AQL + Area reject': 'attendanceTeamAreaReject',
                            'Chấm công + AQL nhóm/khu vực + Từ chối khu vực': 'attendanceTeamAreaReject',

                            'Attendance + Area reject': 'attendanceAreaReject',
                            'Chấm công + Từ chối khu vực': 'attendanceAreaReject',

                            'New employee - No incentive': 'newEmployee',
                            'Nhân viên mới - Không có thưởng': 'newEmployee'
                        };

                        for (const [searchText, translationKey] of Object.entries(notesMappings)) {
                            if (text === searchText || text.includes(searchText)) {
                                notesCell.textContent = getTranslation('conditionsByPosition.notes.' + translationKey, currentLanguage);
                                break;
                            }
                        }
                    }
                });
            });

            // Update tab title if it exists
            const tabButton = document.querySelector('[onclick*="conditions-position"], [data-bs-target*="conditions-position"]');
            if (tabButton) {
                tabButton.textContent = getTranslation('conditionsByPosition.title', currentLanguage);
            }
        }
"""

    # Find updateAllTexts function and add the conditions tab update
    update_all_texts_match = re.search(r'function updateAllTexts\(\) \{.*?\n        \}', content, re.DOTALL)

    if update_all_texts_match:
        func_content = update_all_texts_match.group()

        # Check if conditions update already exists
        if 'updateConditionsTabContent' not in func_content:
            # Add the update call before the closing brace
            last_brace_pos = func_content.rfind('}')

            update_call = """
            // Update Conditions by Position tab
            updateConditionsTabContent();
"""

            new_func_content = func_content[:last_brace_pos] + update_call + '\n        ' + func_content[last_brace_pos:]
            content = content.replace(func_content, new_func_content)
            print("✅ Added conditions tab update to updateAllTexts()")

    # Add the updateConditionsTabContent function if it doesn't exist
    if 'updateConditionsTabContent' not in content:
        # Find the last </script> tag
        script_end = content.rfind('</script>')
        if script_end != -1:
            content = content[:script_end] + update_conditions_tab + '\n' + content[script_end:]
            print("✅ Added updateConditionsTabContent() function")

    # Save the fixed file
    output_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_final_fix.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ Fixed dashboard saved to: {output_file}")

    if replacements_made:
        print(f"✅ Replaced {len(replacements_made)} hardcoded text instances:")
        for item in set(replacements_made):
            print(f"   - {item}")

    print("\n🎉 Language switching for Conditions by Position tab should now work properly!")
    print("   All text including Notes column will update when language is changed")

    return output_file

if __name__ == "__main__":
    fix_conditions_tab_language()