#!/usr/bin/env python3
"""
Extract complete JavaScript from integrated_dashboard_final.py
Handles the {{ }} escaping properly
"""

import re

def extract_javascript_from_original():
    """Extract all JavaScript functions from the original dashboard file"""

    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the main JavaScript sections in the file
    # Look for JavaScript code blocks between script tags or in modal_scripts

    javascript_sections = []

    # 1. Extract modal_scripts content
    modal_match = re.search(r'modal_scripts = """(.*?)"""', content, re.DOTALL)
    if modal_match:
        modal_js = modal_match.group(1)
        # Remove Python f-string escaping ({{ becomes {, }} becomes })
        modal_js = modal_js.replace('{{', '{').replace('}}', '}')
        javascript_sections.append("// Modal Functions")
        javascript_sections.append(modal_js)

    # 2. Find inline JavaScript after the employees_json line
    # Look for JavaScript that starts after window.employeeData
    js_start = content.find('window.employeeData = ')
    if js_start != -1:
        # Find where the script tag ends
        js_end = content.find('</script>', js_start)
        if js_end != -1:
            # Extract the JavaScript portion
            js_content = content[js_start:js_end]

            # Clean up the JavaScript
            lines = js_content.split('\n')
            cleaned_lines = []

            for line in lines:
                # Skip Python code lines (those with f-string markers or triple quotes)
                if '"""' in line or "'''" in line:
                    continue
                if line.strip().startswith('#'):
                    continue

                # Remove leading Python indentation if present
                if line.startswith('    '):
                    line = line[4:]  # Remove 4-space Python indentation

                # Replace {{ with { and }} with }
                line = line.replace('{{', '{').replace('}}', '}')

                # Remove f-string syntax
                line = re.sub(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', 'null', line)
                line = re.sub(r"f'", "'", line)
                line = re.sub(r'f"', '"', line)

                cleaned_lines.append(line)

            javascript_sections.append("\n// Main Dashboard JavaScript")
            javascript_sections.append('\n'.join(cleaned_lines))

    # 3. Look for any other JavaScript function definitions
    function_pattern = re.compile(r'(function\s+\w+\s*\([^)]*\)\s*\{[^}]*\})', re.DOTALL)

    # Combine all JavaScript sections
    complete_js = '\n\n'.join(javascript_sections)

    # Final cleanup
    complete_js = complete_js.replace('{{', '{').replace('}}', '}')

    # Remove any remaining Python artifacts
    complete_js = re.sub(r"'{3,}", '"', complete_js)
    complete_js = re.sub(r'"{3,}', '"', complete_js)

    return complete_js

def main():
    print("Extracting complete JavaScript from integrated_dashboard_final.py...")

    try:
        javascript = extract_javascript_from_original()

        # Save to file
        output_file = 'dashboard_v2/static/js/complete_extracted.js'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(javascript)

        # Count lines and functions
        lines = javascript.count('\n')
        functions = javascript.count('function ')

        print(f"✅ Extraction complete!")
        print(f"   - Lines: {lines}")
        print(f"   - Functions: {functions}")
        print(f"   - Output: {output_file}")

        # Show first few lines as preview
        preview_lines = javascript.split('\n')[:20]
        print("\n📝 Preview (first 20 lines):")
        for i, line in enumerate(preview_lines, 1):
            print(f"{i:3}: {line}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()