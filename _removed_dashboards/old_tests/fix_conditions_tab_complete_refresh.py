#!/usr/bin/env python3
"""
Fix Conditions by Position tab with complete refresh approach
완전한 탭 리프레시로 언어 전환 시 2개 언어 동시 표시 문제 해결
"""

import re

def fix_conditions_tab_with_complete_refresh():
    """Fix the language switching issue using complete tab refresh"""

    # Read the current dashboard file
    dashboard_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_final_fix.html'
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("🔧 Implementing complete tab refresh solution...")

    # 1. Add the generateConditionsTabContent function
    generate_conditions_tab = """
        // Complete refresh function for Conditions by Position tab
        function generateConditionsTabContent(language) {
            console.log('Generating Conditions tab content for language:', language);

            // Position conditions data structure
            const conditionsData = {
                'TYPE-1': [
                    { position: 'MANAGER', conditions: '1, 2, 3, 4', count: 4, noteKey: 'attendanceOnly' },
                    { position: 'A.MANAGER', conditions: '1, 2, 3, 4', count: 4, noteKey: 'attendanceOnly' },
                    { position: '(V) SUPERVISOR', conditions: '1, 2, 3, 4', count: 4, noteKey: 'attendanceOnly' },
                    { position: 'GROUP LEADER', conditions: '1, 2, 3, 4', count: 4, noteKey: 'attendanceOnly' },
                    { position: 'LINE LEADER', conditions: '1, 2, 3, 4, 7', count: 5, noteKey: 'attendanceTeamAql' },
                    { position: 'AQL INSPECTOR', conditions: '1, 2, 3, 4, 5', count: 5, noteKey: 'attendanceMonthAql' },
                    { position: 'ASSEMBLY INSPECTOR', conditions: '1, 2, 3, 4, 5, 6, 9, 10', count: 8, noteKey: 'attendancePersonalAql5prs' },
                    { position: 'AUDIT & TRAINING TEAM', conditions: '1, 2, 3, 4, 7, 8', count: 6, noteKey: 'attendanceTeamAreaReject' },
                    { position: 'MODEL MASTER', conditions: '1, 2, 3, 4, 8', count: 5, noteKey: 'attendanceAreaReject' }
                ],
                'TYPE-2': [
                    { position: 'All TYPE-2 Positions', conditions: '1, 2, 3, 4', count: 4, noteKey: 'attendanceOnly' }
                ],
                'TYPE-3': [
                    { position: 'NEW QIP MEMBER', conditions: 'None', count: 0, noteKey: 'newEmployee' }
                ]
            };

            // Build complete tab content HTML
            let tabContent = `
                <div class="conditions-position-wrapper" style="padding: 20px;">
                    <h4 class="text-primary mb-4">
                        ${getTranslation('conditionsByPosition.title', language)}
                    </h4>
            `;

            // TYPE-1 Section
            tabContent += `
                <div class="mb-5">
                    <h5 class="text-info mb-3">
                        ${getTranslation('conditionsByPosition.typeHeaders.type1', language)}
                    </h5>
                    <div class="table-responsive">
                        <table class="table table-hover table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.position', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.appliedConditions', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.conditionCount', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.notes', language)}</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            // Add TYPE-1 rows
            conditionsData['TYPE-1'].forEach(item => {
                const noteText = getTranslation('conditionsByPosition.notes.' + item.noteKey, language);
                tabContent += `
                    <tr>
                        <td><strong>${item.position}</strong></td>
                        <td>${item.conditions}</td>
                        <td class="text-center">${item.count}</td>
                        <td>${noteText}</td>
                    </tr>
                `;
            });

            tabContent += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            // TYPE-2 Section
            tabContent += `
                <div class="mb-5">
                    <h5 class="text-info mb-3">
                        ${getTranslation('conditionsByPosition.typeHeaders.type2', language)}
                    </h5>
                    <div class="table-responsive">
                        <table class="table table-hover table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.position', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.appliedConditions', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.conditionCount', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.notes', language)}</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            // Add TYPE-2 rows
            conditionsData['TYPE-2'].forEach(item => {
                const noteText = getTranslation('conditionsByPosition.notes.' + item.noteKey, language);
                const positionText = item.position === 'All TYPE-2 Positions'
                    ? getTranslation('conditionsByPosition.allType2', language)
                    : item.position;
                tabContent += `
                    <tr>
                        <td><strong>${positionText}</strong></td>
                        <td>${item.conditions}</td>
                        <td class="text-center">${item.count}</td>
                        <td>${noteText}</td>
                    </tr>
                `;
            });

            tabContent += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            // TYPE-3 Section
            tabContent += `
                <div class="mb-5">
                    <h5 class="text-info mb-3">
                        ${getTranslation('conditionsByPosition.typeHeaders.type3', language)}
                    </h5>
                    <div class="table-responsive">
                        <table class="table table-hover table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.position', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.appliedConditions', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.conditionCount', language)}</th>
                                    <th>${getTranslation('conditionsByPosition.tableHeaders.notes', language)}</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            // Add TYPE-3 rows
            conditionsData['TYPE-3'].forEach(item => {
                const noteText = getTranslation('conditionsByPosition.notes.' + item.noteKey, language);
                const conditionsText = item.conditions === 'None'
                    ? getTranslation('conditionsByPosition.none', language)
                    : item.conditions;
                tabContent += `
                    <tr>
                        <td><strong>${item.position}</strong></td>
                        <td>${conditionsText}</td>
                        <td class="text-center">${item.count}</td>
                        <td>${noteText}</td>
                    </tr>
                `;
            });

            tabContent += `
                            </tbody>
                        </table>
                    </div>
                </div>
                </div>
            `;

            return tabContent;
        }

        // Refresh function that completely replaces tab content
        function refreshConditionsTab() {
            console.log('Refreshing Conditions by Position tab...');

            // Find the conditions tab content container
            const tabContainers = [
                document.getElementById('conditions-position'),
                document.getElementById('conditions-position-tab'),
                document.querySelector('[data-tab-content="conditions-position"]'),
                document.querySelector('.conditions-position-content')
            ];

            let tabContent = null;
            for (const container of tabContainers) {
                if (container) {
                    tabContent = container;
                    break;
                }
            }

            if (!tabContent) {
                // If no container found, try to find by content
                const allDivs = document.querySelectorAll('div');
                for (const div of allDivs) {
                    if (div.textContent.includes('TYPE-1 Position Conditions') ||
                        div.textContent.includes('Điều kiện chức vụ TYPE-1') ||
                        div.textContent.includes('TYPE-1 직급별 조건')) {
                        tabContent = div;
                        break;
                    }
                }
            }

            if (tabContent) {
                // Show loading indicator
                tabContent.innerHTML = '<div class="text-center p-5"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

                // Generate new content after a brief delay for visual feedback
                setTimeout(() => {
                    tabContent.innerHTML = generateConditionsTabContent(currentLanguage);
                    console.log('Conditions tab refreshed successfully');
                }, 100);
            } else {
                console.warn('Conditions tab content container not found');
            }
        }
"""

    # 2. Replace or add the updateConditionsTabContent function with refreshConditionsTab
    # First, remove any existing updateConditionsTabContent function
    content = re.sub(r'function updateConditionsTabContent\(\)[^}]*\}', '', content)

    # Find where to insert the new functions (before the last </script> tag)
    script_end = content.rfind('</script>')
    if script_end != -1:
        content = content[:script_end] + generate_conditions_tab + '\n' + content[script_end:]
        print("✅ Added generateConditionsTabContent and refreshConditionsTab functions")

    # 3. Modify updateAllTexts to call refreshConditionsTab instead of updateConditionsTabContent
    update_all_texts_match = re.search(r'function updateAllTexts\(\) \{.*?\n        \}', content, re.DOTALL)

    if update_all_texts_match:
        func_content = update_all_texts_match.group()

        # Remove old updateConditionsTabContent call
        func_content = re.sub(r'updateConditionsTabContent\(\);?', '', func_content)

        # Add new refreshConditionsTab call
        if 'refreshConditionsTab' not in func_content:
            last_brace_pos = func_content.rfind('}')
            refresh_call = """
            // Complete refresh of Conditions by Position tab
            refreshConditionsTab();
"""
            new_func_content = func_content[:last_brace_pos] + refresh_call + '\n        ' + func_content[last_brace_pos:]
            content = content.replace(func_content, new_func_content)
            print("✅ Modified updateAllTexts to use refreshConditionsTab")

    # 4. Also add refresh call when tab is clicked (if there's a tab switching function)
    if 'showTab' in content:
        # Find showTab function and add refresh when conditions tab is selected
        show_tab_pattern = r'(function showTab\([^)]*\) \{[^}]*)(}\s*$)'
        show_tab_match = re.search(r'function showTab\(.*?\) \{.*?\n        \}', content, re.DOTALL)

        if show_tab_match and 'refreshConditionsTab' not in show_tab_match.group():
            func = show_tab_match.group()
            last_brace = func.rfind('}')

            tab_check = """
            // Refresh Conditions tab when selected
            if (tabName === 'conditions-position' || tabName === 'conditions') {
                setTimeout(() => {
                    refreshConditionsTab();
                }, 100);
            }
"""
            new_func = func[:last_brace] + tab_check + '\n        ' + func[last_brace:]
            content = content.replace(func, new_func)
            print("✅ Added refresh trigger when tab is selected")

    # Save the fixed file
    output_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_complete_fix.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ Complete refresh solution implemented!")
    print(f"📁 Saved to: {output_file}")
    print("\n🎉 Benefits of this solution:")
    print("   - Completely removes old content before adding new")
    print("   - No more mixed languages")
    print("   - Clean and predictable behavior")
    print("   - Loading indicator for better UX")

    return output_file

if __name__ == "__main__":
    fix_conditions_tab_with_complete_refresh()