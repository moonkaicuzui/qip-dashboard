#!/usr/bin/env python3
"""
Fix specific template literal patterns that cause JavaScript errors
Only targets ${{getTranslation patterns which are the main issue
"""

import re

def fix_specific_patterns():
    file_path = 'integrated_dashboard_final.py'
    print(f"📖 Reading {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup
    with open(f'{file_path}.backup_specific', 'w', encoding='utf-8') as f:
        f.write(content)

    print("🔍 Fixing specific problematic patterns...")

    # Fix specific patterns only
    # Pattern 1: ${{getTranslation( → ${getTranslation(
    pattern1 = r'\$\{\{(getTranslation\([^}]+\))'
    content = re.sub(pattern1, r'${\1', content)

    # Pattern 2: Fix closing braces after getTranslation
    # Look for patterns like: getTranslation(...) || 'default'}}
    # Should become: getTranslation(...) || 'default'}
    pattern2 = r'(getTranslation\([^)]+\)[^}]*)\}\}'

    # Only fix if it's inside a template literal context (not at end of f-string)
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        if 'getTranslation' in line and '}}' in line and '${' in line:
            # This line has both ${ and }}, likely a template literal
            # Replace the }} after getTranslation with single }
            line = re.sub(r'(getTranslation\([^)]+\)[^}]*)\}\}(?!})', r'\1}', line)
        fixed_lines.append(line)

    content = '\n'.join(fixed_lines)

    # Fix other ${{ patterns for simple variables
    # Pattern 3: ${{variable}} → ${variable}
    content = re.sub(r'\$\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', r'${\1}', content)

    # Pattern 4: ${{expression.method()}} → ${expression.method()}
    content = re.sub(r'\$\{\{([^}]+\.toLocaleString\([^)]*\))\}\}', r'${\1}', content)

    print(f"  ✅ Fixed specific patterns")

    # Save the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def verify_patterns():
    """Check if problematic patterns remain"""
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for remaining ${{ patterns
    remaining = re.findall(r'\$\{\{getTranslation', content)
    if remaining:
        print(f"⚠️ Still {len(remaining)} ${{{{getTranslation patterns remaining")
    else:
        print("✅ All ${{getTranslation patterns fixed")

    # Check Python syntax
    try:
        compile(content, 'integrated_dashboard_final.py', 'exec')
        print("✅ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Python syntax error at line {e.lineno}: {e.msg}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Specific Template Literal Pattern Fix")
    print("=" * 60)

    if fix_specific_patterns():
        if verify_patterns():
            print("\n🎉 All specific patterns fixed successfully!")
            print("\nNext steps:")
            print("1. python integrated_dashboard_final.py --month 9 --year 2025")
            print("2. Check the dashboard in browser")
        else:
            print("\n❌ Some issues remain")
            print("Restore with: cp integrated_dashboard_final.py.backup_specific integrated_dashboard_final.py")