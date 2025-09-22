#!/usr/bin/env python3
"""
Proper translation system implementation without syntax errors
Uses clean separation between Python and JavaScript code
"""

import json
import re

class ProperTranslationSystem:
    """A clean approach to handling translations without syntax errors"""

    def __init__(self):
        self.translations = self.load_translations()

    def load_translations(self):
        """Load translations from JSON file"""
        with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_translation_wrapper(self):
        """Create a wrapper function that generates JavaScript code safely"""

        wrapper_code = '''
# Translation wrapper to avoid f-string syntax errors

def t(key_path, default_value):
    """
    Generate translation JavaScript code safely

    Args:
        key_path: Translation key path (e.g., 'tabs.validation')
        default_value: Default value if translation not found

    Returns:
        JavaScript code string with proper escaping for f-strings
    """
    # Convert Python dot notation to JavaScript optional chaining
    js_path = key_path.replace('.', '?.')

    # Create the JavaScript expression with doubled braces
    # This will be safe in f-strings
    js_code = "${{translations." + js_path + "?.[lang] || '" + default_value + "'}}"

    # Double the braces for f-string safety
    return js_code.replace('{', '{{').replace('}', '}}')

def html_t(key_path, default_value):
    """Generate translation for direct HTML insertion"""
    js_path = key_path.replace('.', '?.')
    return "${{{{translations.{0}?.[lang] || '{1}'}}}}".format(js_path, default_value)

# Usage examples:
# In Python code generating HTML:
# html = f"<div>{{t('tabs.validation', '요약 및 시스템 검증')}}</div>"
# html = f"<th>{{html_t('orgChartModal.name', '이름')}}</th>"
'''
        return wrapper_code

    def fix_integrated_dashboard(self):
        """Fix integrated_dashboard_final.py with proper translation handling"""

        print("🔧 Fixing integrated_dashboard_final.py...")

        with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create a new version with fixes
        fixed_lines = []
        changes = 0

        # Add translation helper at the beginning (after imports)
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('import') and not line.startswith('from'):
                import_end = i
                break

        # Insert helper function
        helper = '''
# Translation helper function to avoid syntax errors
def tr(key, default):
    """Safe translation function for JavaScript generation"""
    js_key = key.replace('.', '?.')
    # Return with proper escaping for f-strings
    return "${{{{translations.{0}?.[lang] || '{1}'}}}}".format(js_key, default)

'''
        lines.insert(import_end, helper)

        # Now fix each hardcoded text
        replacements = {
            "'요약 및 시스템 검증'": "tr('tabs.validation', '요약 및 시스템 검증')",
            '"요약 및 시스템 검증"': "tr('tabs.validation', '요약 및 시스템 검증')",

            "'통과'": "tr('individualDetails.conditionStatus.pass', '통과')",
            "'실패'": "tr('individualDetails.conditionStatus.fail', '실패')",

            "'전체 조직'": "tr('orgChart.entireOrganization', '전체 조직')",
            "'TYPE-1 관리자 인센티브 구조'": "tr('orgChart.type1ManagerStructure', 'TYPE-1 관리자 인센티브 구조')",

            "'직급'": "tr('orgChartModal.position', '직급')",
            "'계산 과정 상세'": "tr('orgChartModal.calculationDetails', '계산 과정 상세')",
            "'팀 내 LINE LEADER 수'": "tr('orgChartModal.teamLineLeaderCount', '팀 내 LINE LEADER 수')",
            "'인센티브 받은 LINE LEADER'": "tr('orgChartModal.lineLeadersReceiving', '인센티브 받은 LINE LEADER')",
            "'LINE LEADER 평균 인센티브'": "tr('orgChartModal.lineLeaderAverage', 'LINE LEADER 평균 인센티브')",
            "'계산식'": "tr('orgChartModal.calculationFormula', '계산식')",

            "'이름'": "tr('orgChartModal.name', '이름')",
            "'인센티브'": "tr('orgChartModal.incentive', '인센티브')",
            "'평균 계산 포함'": "tr('orgChartModal.includeInAverage', '평균 계산 포함')",
            "'수령 여부'": "tr('orgChartModal.receivingStatus', '수령 여부')",
            "'합계'": "tr('orgChartModal.total', '합계')",
            "'평균'": "tr('orgChartModal.average', '평균')",
        }

        for i, line in enumerate(lines):
            original = line

            # Skip if it's a comment or import
            if line.strip().startswith('#') or line.strip().startswith('import') or line.strip().startswith('from'):
                fixed_lines.append(line)
                continue

            # Apply replacements only in HTML generation contexts
            if 'html' in line.lower() or '<' in line or 'modal' in line.lower():
                for old, new in replacements.items():
                    if old in line:
                        # Use format string instead of f-string for complex cases
                        if 'f"' in line or "f'" in line:
                            # Inside f-string, use {tr(...)}
                            line = line.replace(old, f"{{{new}}}")
                        else:
                            # Outside f-string, use direct call
                            line = line.replace(old, new)
                        changes += 1

            fixed_lines.append(line)

        # Write the fixed version
        with open('integrated_dashboard_final_fixed.py', 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

        print(f"✅ Fixed {changes} instances")
        print("📁 Output: integrated_dashboard_final_fixed.py")

        return changes

    def create_validation_script(self):
        """Create a script to validate syntax"""

        validation_script = '''#!/usr/bin/env python3
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
'''

        with open('validate_syntax.py', 'w') as f:
            f.write(validation_script)

        print("📝 Created validate_syntax.py")

    def create_best_practices_doc(self):
        """Create documentation for best practices"""

        best_practices = '''# Translation System Best Practices

## ✅ DO's

### 1. Use Helper Functions
```python
def tr(key, default):
    """Safe translation function"""
    js_key = key.replace('.', '?.')
    return "${{{{translations.{0}?.[lang] || '{1}'}}}}".format(js_key, default)

# Usage in f-string:
html = f"<div>{tr('tabs.validation', '요약 및 시스템 검증')}</div>"
```

### 2. Use .format() for Complex Cases
```python
# Instead of f-string with complex expressions:
# html = f"${{translations.{key}?.[lang] || '{default}'}}"  # SYNTAX ERROR!

# Use .format():
html = "${{{{translations.{0}?.[lang] || '{1}'}}}}".format(key, default)
```

### 3. Separate JavaScript Generation
```python
# Generate JavaScript separately
js_code = generate_translation_js(key, default)
html = f"<div>{js_code}</div>"
```

## ❌ DON'T's

### 1. Don't Mix Complex JavaScript in f-strings
```python
# BAD - Will cause syntax error:
html = f"${{translations.{key}?.[lang] || '{default}'}}"

# GOOD - Use helper or format:
html = f"{tr(key, default)}"
```

### 2. Don't Forget to Escape Braces
```python
# BAD - Single braces in f-string:
html = f"${translation}"

# GOOD - Double braces:
html = f"${{{{translation}}}}"
```

### 3. Don't Use Optional Chaining Directly
```python
# BAD - f-string can't parse this:
html = f"${translations?.tabs?.validation?.[lang]}"

# GOOD - Use helper function:
html = f"{tr('tabs.validation', 'Default')}"
```

## 🔧 Common Patterns

### Pattern 1: Simple Translation
```python
# In HTML generation:
<th>{tr('orgChartModal.name', '이름')}</th>
```

### Pattern 2: Conditional Translation
```python
# For conditional text:
status = tr('status.pass', '통과') if condition else tr('status.fail', '실패')
```

### Pattern 3: Dynamic Translation Keys
```python
# When key is dynamic:
key = f"messages.{msg_type}"
text = tr(key, default_messages[msg_type])
```

## 🧪 Testing

Always validate syntax before deployment:
```bash
python validate_syntax.py integrated_dashboard_final.py
```
'''

        with open('TRANSLATION_BEST_PRACTICES.md', 'w') as f:
            f.write(best_practices)

        print("📚 Created TRANSLATION_BEST_PRACTICES.md")

def main():
    """Main execution"""
    print("=" * 80)
    print("🔧 Proper Translation System Implementation")
    print("=" * 80)

    system = ProperTranslationSystem()

    # Create helper code
    with open('translation_helpers.py', 'w') as f:
        f.write(system.create_translation_wrapper())
    print("✅ Created translation_helpers.py")

    # Fix the main file
    changes = system.fix_integrated_dashboard()

    # Create validation script
    system.create_validation_script()

    # Create documentation
    system.create_best_practices_doc()

    print("\n" + "=" * 80)
    print("✨ Summary")
    print("=" * 80)
    print(f"""
✅ Files created:
   - integrated_dashboard_final_fixed.py (main file with fixes)
   - translation_helpers.py (helper functions)
   - validate_syntax.py (syntax validation)
   - TRANSLATION_BEST_PRACTICES.md (documentation)

📊 Changes made: {changes}

🚀 Next steps:
   1. Review integrated_dashboard_final_fixed.py
   2. Run: python validate_syntax.py integrated_dashboard_final_fixed.py
   3. If valid, rename to integrated_dashboard_final.py
   4. Generate dashboard: python integrated_dashboard_final.py --month 9 --year 2025
    """)

if __name__ == "__main__":
    main()