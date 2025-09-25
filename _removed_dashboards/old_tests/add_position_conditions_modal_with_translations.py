#!/usr/bin/env python3
"""
Add Conditions by Position modal with proper translations to dashboard
"""

import re
import json

def add_position_conditions_modal():
    """Add a properly translated Conditions by Position modal to the dashboard"""

    # Read the dashboard HTML
    dashboard_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_fixed.html'
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if the modal already exists
    if 'showPositionConditionsModal' in content:
        print("✅ Position conditions modal already exists")
        return

    # Add the modal function
    modal_function = """
        // Position Conditions Modal Function
        function showPositionConditionsModal() {
            const modalContent = `
                <div class="modal fade show" tabindex="-1" style="display: block;">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header bg-primary text-white">
                                <h5 class="modal-title" id="positionConditionsTitle">
                                    ${getTranslation('conditionsByPosition.title', currentLanguage)}
                                </h5>
                                <button type="button" class="btn-close btn-close-white" onclick="closePositionConditionsModal()"></button>
                            </div>
                            <div class="modal-body">
                                <!-- TYPE-1 Conditions -->
                                <div class="mb-4">
                                    <h6 class="text-primary position-type-header" data-type="1">
                                        ${getTranslation('conditionsByPosition.typeHeaders.type1', currentLanguage)}
                                    </h6>
                                    <table class="table table-hover">
                                        <thead class="table-light">
                                            <tr>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.position', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.appliedConditions', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.conditionCount', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.notes', currentLanguage)}</th>
                                            </tr>
                                        </thead>
                                        <tbody id="type1ConditionsBody">
                                            <!-- Content will be generated dynamically -->
                                        </tbody>
                                    </table>
                                </div>

                                <!-- TYPE-2 Conditions -->
                                <div class="mb-4">
                                    <h6 class="text-primary position-type-header" data-type="2">
                                        ${getTranslation('conditionsByPosition.typeHeaders.type2', currentLanguage)}
                                    </h6>
                                    <table class="table table-hover">
                                        <thead class="table-light">
                                            <tr>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.position', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.appliedConditions', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.conditionCount', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.notes', currentLanguage)}</th>
                                            </tr>
                                        </thead>
                                        <tbody id="type2ConditionsBody">
                                            <!-- Content will be generated dynamically -->
                                        </tbody>
                                    </table>
                                </div>

                                <!-- TYPE-3 Conditions -->
                                <div class="mb-4">
                                    <h6 class="text-primary position-type-header" data-type="3">
                                        ${getTranslation('conditionsByPosition.typeHeaders.type3', currentLanguage)}
                                    </h6>
                                    <table class="table table-hover">
                                        <thead class="table-light">
                                            <tr>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.position', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.appliedConditions', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.conditionCount', currentLanguage)}</th>
                                                <th>${getTranslation('conditionsByPosition.tableHeaders.notes', currentLanguage)}</th>
                                            </tr>
                                        </thead>
                                        <tbody id="type3ConditionsBody">
                                            <!-- Content will be generated dynamically -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-backdrop fade show"></div>
            `;

            // Create and show modal
            const modalDiv = document.createElement('div');
            modalDiv.id = 'positionConditionsModal';
            modalDiv.innerHTML = modalContent;
            document.body.appendChild(modalDiv);

            // Populate the tables with data
            populatePositionConditions();
        }

        function closePositionConditionsModal() {
            const modal = document.getElementById('positionConditionsModal');
            if (modal) {
                modal.remove();
            }
        }

        function populatePositionConditions() {
            // Position conditions data
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
                    { position: getTranslation('conditionsByPosition.allType2', currentLanguage), conditions: '1, 2, 3, 4', count: 4, noteKey: 'attendanceOnly' }
                ],
                'TYPE-3': [
                    { position: 'NEW QIP MEMBER', conditions: getTranslation('conditionsByPosition.none', currentLanguage), count: 0, noteKey: 'newEmployee' }
                ]
            };

            // Populate TYPE-1
            const type1Body = document.getElementById('type1ConditionsBody');
            if (type1Body) {
                type1Body.innerHTML = conditionsData['TYPE-1'].map(item => `
                    <tr>
                        <td>${item.position}</td>
                        <td>${item.conditions}</td>
                        <td>${item.count}</td>
                        <td>${getTranslation('conditionsByPosition.notes.' + item.noteKey, currentLanguage)}</td>
                    </tr>
                `).join('');
            }

            // Populate TYPE-2
            const type2Body = document.getElementById('type2ConditionsBody');
            if (type2Body) {
                type2Body.innerHTML = conditionsData['TYPE-2'].map(item => `
                    <tr>
                        <td>${item.position}</td>
                        <td>${item.conditions}</td>
                        <td>${item.count}</td>
                        <td>${getTranslation('conditionsByPosition.notes.' + item.noteKey, currentLanguage)}</td>
                    </tr>
                `).join('');
            }

            // Populate TYPE-3
            const type3Body = document.getElementById('type3ConditionsBody');
            if (type3Body) {
                type3Body.innerHTML = conditionsData['TYPE-3'].map(item => `
                    <tr>
                        <td>${item.position}</td>
                        <td>${item.conditions}</td>
                        <td>${item.count}</td>
                        <td>${getTranslation('conditionsByPosition.notes.' + item.noteKey, currentLanguage)}</td>
                    </tr>
                `).join('');
            }
        }

        // Function to update position conditions modal text
        function updatePositionConditionsModal() {
            // Update modal title
            const modalTitle = document.getElementById('positionConditionsTitle');
            if (modalTitle) {
                modalTitle.textContent = getTranslation('conditionsByPosition.title', currentLanguage);
            }

            // Update type headers
            document.querySelectorAll('.position-type-header').forEach(header => {
                const type = header.getAttribute('data-type');
                if (type) {
                    header.textContent = getTranslation('conditionsByPosition.typeHeaders.type' + type, currentLanguage);
                }
            });

            // Update table headers
            const tableHeaders = document.querySelectorAll('#positionConditionsModal th');
            if (tableHeaders.length > 0) {
                const headerKeys = ['position', 'appliedConditions', 'conditionCount', 'notes'];
                let headerIndex = 0;
                tableHeaders.forEach(th => {
                    if (headerIndex < headerKeys.length) {
                        th.textContent = getTranslation('conditionsByPosition.tableHeaders.' + headerKeys[headerIndex % 4], currentLanguage);
                    }
                    headerIndex++;
                });
            }

            // Re-populate tables with translated notes
            if (document.getElementById('positionConditionsModal')) {
                populatePositionConditions();
            }
        }
"""

    # Find where to insert the modal function (before the closing script tag)
    script_end = content.rfind('</script>')
    if script_end == -1:
        print("❌ Could not find script tag")
        return

    # Insert the modal function
    content = content[:script_end] + modal_function + '\n' + content[script_end:]

    # Add button to show the modal (if not exists)
    button_html = """
        <button class="btn btn-primary mb-3" onclick="showPositionConditionsModal()">
            <i class="fas fa-list-check"></i>
            <span id="showConditionsButtonText">Conditions by Position</span>
        </button>
"""

    # Add button after the overview section if not exists
    if 'showPositionConditionsModal()' not in content:
        # Find a good place to insert the button (after summary cards)
        insert_pos = content.find('<div id="overview"')
        if insert_pos != -1:
            # Find the end of the overview div
            end_div_pos = content.find('</div>', insert_pos)
            if end_div_pos != -1:
                content = content[:end_div_pos] + button_html + content[end_div_pos:]

    # Update the updateAllTexts function to include modal updates
    update_all_texts_pattern = r'(function updateAllTexts\(\) \{.*?)(}\s*$)'
    update_all_texts_match = re.search(r'function updateAllTexts\(\) \{.*?\n        \}', content, re.DOTALL)

    if update_all_texts_match and 'updatePositionConditionsModal' not in update_all_texts_match.group():
        func_content = update_all_texts_match.group()
        last_brace_pos = func_content.rfind('}')

        # Add call to updatePositionConditionsModal
        update_call = """
            // Update position conditions modal button
            const conditionsButton = document.getElementById('showConditionsButtonText');
            if (conditionsButton) {
                conditionsButton.textContent = getTranslation('conditionsByPosition.title', currentLanguage);
            }

            // Update modal if it's open
            if (document.getElementById('positionConditionsModal')) {
                updatePositionConditionsModal();
            }
"""

        new_func_content = func_content[:last_brace_pos] + update_call + '\n        ' + func_content[last_brace_pos:]
        content = content.replace(func_content, new_func_content)

    # Save the updated file
    output_file = 'output_files/Incentive_Dashboard_2025_09_Version_5_complete_fix.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Added position conditions modal with proper translations")
    print(f"✅ Saved to: {output_file}")
    print("✅ The modal will now properly update all text when language is changed")

    return output_file

if __name__ == "__main__":
    add_position_conditions_modal()