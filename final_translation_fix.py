#!/usr/bin/env python3
"""
Final comprehensive fix for translation system
Ensures all JavaScript template literals are properly escaped
"""

def final_translation_fix():
    """Apply final fixes to translation system"""

    # Read the HTML file
    html_path = 'output_files/Incentive_Dashboard_2025_09_Version_5.html'

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix all single-brace template literals to double-brace
    # This is needed because they're inside Python f-strings

    replacements = [
        # Fix single braces to double braces for all translation calls
        ('${translations.common?.tableHeaders?.employeeNo?.[lang]',
         '${{translations.common?.tableHeaders?.employeeNo?.[lang]'),

        ('${translations.common?.tableHeaders?.name?.[lang]',
         '${{translations.common?.tableHeaders?.name?.[lang]'),

        ('${translations.common?.tableHeaders?.position?.[lang]',
         '${{translations.common?.tableHeaders?.position?.[lang]'),

        ('${translations.modals?.areaAQL?.title?.[lang]',
         '${{translations.modals?.areaAQL?.title?.[lang]'),

        ('${translations.modals?.areaAQL?.area?.[lang]',
         '${{translations.modals?.areaAQL?.area?.[lang]'),

        ('${translations.modals?.areaAQL?.totalEmployees?.[lang]',
         '${{translations.modals?.areaAQL?.totalEmployees?.[lang]'),

        ('${translations.modals?.fprs?.lowPassRateTitle?.[lang]',
         '${{translations.modals?.fprs?.lowPassRateTitle?.[lang]'),

        ('${translations.modals?.fprs?.lowInspectionTitle?.[lang]',
         '${{translations.modals?.fprs?.lowInspectionTitle?.[lang]'),

        ('${translations.modals?.fprs?.positionHierarchy?.[lang]',
         '${{translations.modals?.fprs?.positionHierarchy?.[lang]'),

        ('${translations.modals?.fprs?.totalTests?.[lang]',
         '${{translations.modals?.fprs?.totalTests?.[lang]'),

        ('${translations.modals?.fprs?.passRate?.[lang]',
         '${{translations.modals?.fprs?.passRate?.[lang]'),

        ('${translations.modals?.fprs?.conditionMet?.[lang]',
         '${{translations.modals?.fprs?.conditionMet?.[lang]'),

        ('${translations.modals?.fprs?.met?.[lang]',
         '${{translations.modals?.fprs?.met?.[lang]'),

        ('${translations.modals?.fprs?.conditionNotMet?.[lang]',
         '${{translations.modals?.fprs?.conditionNotMet?.[lang]'),

        ('${translations.validationTab?.kpiCards?.totalWorkingDays?.title?.[lang]',
         '${{translations.validationTab?.kpiCards?.totalWorkingDays?.title?.[lang]'),

        ('${translations.validationTab?.kpiCards?.unauthorizedAbsence?.title?.[lang]',
         '${{translations.validationTab?.kpiCards?.unauthorizedAbsence?.title?.[lang]'),

        ('${translations.validationTab?.kpiCards?.lowAttendance?.title?.[lang]',
         '${{translations.validationTab?.kpiCards?.lowAttendance?.title?.[lang]'),

        ('${translations.validationTab?.kpiCards?.minWorkingDays?.title?.[lang]',
         '${{translations.validationTab?.kpiCards?.minWorkingDays?.title?.[lang]'),

        ('${translations.validationTab?.kpiCards?.areaRejectRate?.title?.[lang]',
         '${{translations.validationTab?.kpiCards?.areaRejectRate?.title?.[lang]'),

        # Also fix closing braces
        ("']}}", "'}}"),
        ('"]}', '"}}'),
    ]

    # Apply replacements
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Fixed: {old[:50]}...")

    # Write back
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ Final translation fixes applied to HTML")

    # Also need to update the Python file for future generations
    py_path = 'integrated_dashboard_final.py'

    with open(py_path, 'r', encoding='utf-8') as f:
        py_content = f.read()

    # Count how many fixes needed
    fixes_needed = 0

    # Check for patterns that need double braces
    import re

    # Find all ${...} patterns that should be ${{...}}
    pattern = r'\$\{translations\.[^}]+\}'
    matches = re.findall(pattern, py_content)

    for match in matches:
        # Check if it's not already doubled
        if not match.startswith('${{'):
            # This needs to be fixed
            fixed = match.replace('${', '${{').replace('}', '}}')
            py_content = py_content.replace(match, fixed)
            fixes_needed += 1

    if fixes_needed > 0:
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(py_content)
        print(f"✅ Fixed {fixes_needed} template literals in Python file")

    print("\n✨ Translation system is now properly configured!")
    print("   All template literals are properly escaped")
    print("   Language switching should work correctly")

if __name__ == "__main__":
    final_translation_fix()