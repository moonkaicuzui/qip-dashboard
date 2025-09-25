#!/usr/bin/env python3
"""
Apply complete refresh solution directly to Incentive_Dashboard_2025_09_Version_5.html
원본 파일에 직접 개선 코드 적용
"""

import re

def apply_complete_refresh_to_original():
    """Apply the complete refresh solution to the original dashboard file"""

    # Read the original dashboard file
    original_file = 'output_files/Incentive_Dashboard_2025_09_Version_5.html'
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"🔧 Applying complete refresh solution to {original_file}...")

    # 1. First, remove any existing updateConditionsTabContent function if it exists
    content = re.sub(r'function updateConditionsTabContent\(\)[^}]*\}', '', content)
    print("✅ Cleaned up any existing updateConditionsTabContent function")

    # 2. Add the complete refresh functions
    complete_refresh_functions = """
        // ============================================
        // Complete Refresh Solution for Conditions Tab
        // ============================================

        // Generate complete tab content with selected language
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
                document.querySelector('.conditions-position-content'),
                document.querySelector('[data-bs-target="#conditions-position"]')?.getAttribute('data-bs-target')?.slice(1)
            ];

            let tabContent = null;
            for (const container of tabContainers) {
                if (container) {
                    const element = typeof container === 'string'
                        ? document.getElementById(container)
                        : container;
                    if (element) {
                        tabContent = element;
                        break;
                    }
                }
            }

            // If still not found, try to find by content
            if (!tabContent) {
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
                tabContent.innerHTML = '<div class="text-center p-5"><i class="fas fa-spinner fa-spin fa-2x"></i><br><span class="mt-2">Loading...</span></div>';

                // Generate new content after a brief delay for visual feedback
                setTimeout(() => {
                    tabContent.innerHTML = generateConditionsTabContent(currentLanguage);
                    console.log('Conditions tab refreshed successfully');
                }, 100);
            } else {
                console.warn('Conditions tab content container not found');
            }
        }

        // ============================================
        // End of Complete Refresh Solution
        // ============================================
"""

    # Find the last </script> tag and insert the functions before it
    script_end = content.rfind('</script>')
    if script_end != -1:
        content = content[:script_end] + complete_refresh_functions + '\n' + content[script_end:]
        print("✅ Added generateConditionsTabContent and refreshConditionsTab functions")

    # 3. Update the updateAllTexts function to use refreshConditionsTab
    update_all_texts_match = re.search(r'function updateAllTexts\(\) \{.*?\n        \}', content, re.DOTALL)

    if update_all_texts_match:
        func_content = update_all_texts_match.group()

        # Remove any existing calls to updateConditionsTabContent
        func_content = re.sub(r'updateConditionsTabContent\(\);?\s*', '', func_content)

        # Check if refreshConditionsTab is already being called
        if 'refreshConditionsTab' not in func_content:
            # Find the last closing brace
            last_brace_pos = func_content.rfind('}')

            # Add the refresh call
            refresh_call = """
            // Complete refresh of Conditions by Position tab
            if (typeof refreshConditionsTab === 'function') {
                refreshConditionsTab();
            }
"""

            new_func_content = func_content[:last_brace_pos] + refresh_call + '\n        ' + func_content[last_brace_pos:]
            content = content.replace(func_content, new_func_content)
            print("✅ Modified updateAllTexts to call refreshConditionsTab")

    # 4. If there's a showTab function, add refresh trigger when conditions tab is selected
    show_tab_match = re.search(r'function showTab\([^)]*\) \{.*?\n        \}', content, re.DOTALL)

    if show_tab_match:
        func = show_tab_match.group()

        # Check if refresh for conditions tab already exists
        if 'conditions-position' not in func or 'refreshConditionsTab' not in func:
            last_brace = func.rfind('}')

            tab_check = """
            // Refresh Conditions tab when selected
            if (tabName === 'conditions-position' || tabName === 'conditions' ||
                tabName === 'criteria' || tabName?.includes('condition')) {
                setTimeout(() => {
                    if (typeof refreshConditionsTab === 'function') {
                        refreshConditionsTab();
                    }
                }, 100);
            }
"""

            new_func = func[:last_brace] + tab_check + '\n        ' + func[last_brace:]
            content = content.replace(func, new_func)
            print("✅ Added refresh trigger when tab is selected")

    # Save the updated original file
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ Successfully updated {original_file} with complete refresh solution!")
    print("\n🎉 Applied improvements:")
    print("   • Complete tab refresh on language change")
    print("   • Loading indicator during refresh")
    print("   • No more mixed language issues")
    print("   • Clean content replacement")
    print("\n📌 The original file has been directly updated.")

    return original_file

if __name__ == "__main__":
    apply_complete_refresh_to_original()