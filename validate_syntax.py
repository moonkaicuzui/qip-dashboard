#!/usr/bin/env python3
"""
Validation script for translation syntax
"""

import ast
import sys

def validate_file(filename):
    """Validate Python syntax in file"""

    print(f"Validating {filename}...")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to parse the file
        ast.parse(content)
        print("✅ Syntax is valid!")
        return True

    except SyntaxError as e:
        print(f"❌ Syntax error at line {e.lineno}:")
        print(f"   {e.text}")
        print(f"   {' ' * (e.offset - 1)}^")
        print(f"   {e.msg}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "integrated_dashboard_final.py"

    if validate_file(filename):
        sys.exit(0)
    else:
        sys.exit(1)
