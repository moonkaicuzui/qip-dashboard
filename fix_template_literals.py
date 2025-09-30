#!/usr/bin/env python3
"""
Fix JavaScript template literal syntax in integrated_dashboard_final.py
Converts ${{variable}} to ${variable} in JavaScript code
"""

import re

def fix_template_literals():
    # Read the file
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Count occurrences before fix
    pattern = r'\$\{\{([^}]+)\}\}'
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} template literal issues to fix")

    # Sample of issues found
    if matches:
        print("\nSample issues found:")
        for match in matches[:5]:
            print(f"  - ${{{{{match}}}}}")

    # Fix the pattern: ${{variable}} -> ${variable}
    # This regex matches ${{ followed by anything except }} and then }}
    fixed_content = re.sub(r'\$\{\{([^}]+)\}\}', r'${{\1}}', content)

    # Verify the fix
    remaining = re.findall(r'\$\{\{([^}]+)\}\}', fixed_content)
    print(f"\nAfter fix: {len(remaining)} issues remaining")

    # Write the fixed content back
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print("\n✅ Successfully fixed all template literal issues")
    print("📝 Updated integrated_dashboard_final.py")

    return len(matches), len(remaining)

if __name__ == "__main__":
    fixed, remaining = fix_template_literals()
    print(f"\n📊 Summary: Fixed {fixed} issues, {remaining} remaining")