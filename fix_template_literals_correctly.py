#!/usr/bin/env python3
"""
Correct fix for JavaScript template literals in Python f-strings
Replaces ${{...}} with ${...} by removing one set of braces
"""

import re

def fix_template_literals_correctly():
    file_path = 'integrated_dashboard_final.py'
    print(f"📖 Reading {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup
    with open(f'{file_path}.backup_correct', 'w', encoding='utf-8') as f:
        f.write(content)

    print("🔍 Finding and fixing template literal patterns...")

    # Count occurrences before fix
    before_count = len(re.findall(r'\$\{\{', content))
    print(f"  Found {before_count} instances of '${{{{' pattern")

    # Replace ${{ with ${
    content = content.replace('${{', '${')

    # Count occurrences after fix
    after_count = len(re.findall(r'\$\{\{', content))
    print(f"  After fix: {after_count} instances remaining")

    # Count the actual replacements
    replacements = before_count - after_count
    print(f"  ✅ Fixed {replacements} patterns")

    # Save the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ Fix completed successfully!")
    return True

def verify_python_syntax():
    """Verify Python syntax is still valid"""
    print("\n🔍 Verifying Python syntax...")

    try:
        with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
            source = f.read()

        compile(source, 'integrated_dashboard_final.py', 'exec')
        print("✅ Python syntax is valid!")
        return True
    except SyntaxError as e:
        print(f"❌ Python syntax error at line {e.lineno}: {e.msg}")
        print(f"  {e.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("JavaScript Template Literal Correct Fix")
    print("=" * 60)

    if fix_template_literals_correctly():
        if verify_python_syntax():
            print("\n🎉 All fixes applied successfully!")
            print("\nNext steps:")
            print("1. python integrated_dashboard_final.py --month 9 --year 2025")
            print("2. Check the dashboard in browser")
        else:
            print("\n❌ Python syntax error - restoring backup")
            print("Run: cp integrated_dashboard_final.py.backup_correct integrated_dashboard_final.py")