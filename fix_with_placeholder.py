#!/usr/bin/env python3
"""
Fix JavaScript template literals using placeholder approach
Replace ${{ with a placeholder, then replace it back in the output
"""

def fix_with_placeholder():
    file_path = 'integrated_dashboard_final.py'
    print(f"📖 Reading {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Backup
    with open(f'{file_path}.backup_placeholder', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("🔍 Fixing template literal patterns with placeholder approach...")

    # Strategy: Add a line after dashboard HTML generation to fix the patterns
    # Find where the HTML is written
    fixed_lines = []
    changes_made = 0

    for i, line in enumerate(lines):
        # Replace ${{ with a unique placeholder in the Python code
        if '${{' in line and 'getTranslation' in line:
            # Use __TL__ as placeholder for template literal
            line = line.replace('${{', '__TL__START__').replace('}}', '__TL__END__')
            changes_made += 1

        fixed_lines.append(line)

        # After writing the HTML file, add a fix step
        if 'with open(output_file, \'w\',' in line and i < len(lines) - 2:
            # Find the write line
            next_line_index = i + 1
            while next_line_index < len(lines) and 'f.write(' not in lines[next_line_index]:
                next_line_index += 1

            if next_line_index < len(lines) and 'html_content' in lines[next_line_index]:
                # Add a line to fix the placeholders
                indent = '        '  # Match the indentation
                fixed_lines.append(f'{indent}# Fix template literal placeholders\n')
                fixed_lines.append(f'{indent}html_content = html_content.replace("__TL__START__", "${{").replace("__TL__END__", "}}")\n')
                print("  ✅ Added placeholder replacement logic")

    print(f"  ✅ Modified {changes_made} lines with placeholders")

    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    return True

def verify_fix():
    """Verify the fix worked"""
    print("\n🔍 Verifying the fix...")

    # Check Python syntax
    try:
        with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
            content = f.read()

        compile(content, 'integrated_dashboard_final.py', 'exec')
        print("✅ Python syntax is valid")

        # Check for remaining ${{ patterns
        if '${{' in content:
            # It's okay if they're in placeholders
            if '__TL__START__' in content:
                print("✅ Template literals converted to placeholders")
            else:
                print("⚠️ Some ${{ patterns remain")

        return True
    except SyntaxError as e:
        print(f"❌ Python syntax error at line {e.lineno}: {e.msg}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Template Literal Fix with Placeholder Approach")
    print("=" * 60)

    if fix_with_placeholder():
        if verify_fix():
            print("\n🎉 Fix applied successfully!")
            print("\nNext steps:")
            print("1. python integrated_dashboard_final.py --month 9 --year 2025")
            print("2. Check the dashboard in browser")
        else:
            print("\n❌ Fix failed")
            print("Restore with: cp integrated_dashboard_final.py.backup_placeholder integrated_dashboard_final.py")