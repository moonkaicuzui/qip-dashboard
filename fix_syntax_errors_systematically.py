#!/usr/bin/env python3
"""
Systematic solution for syntax errors in translation system
Handles f-string and JavaScript template literal conflicts
"""

import re
import json

class TranslationSystemFixer:
    """Systematic approach to fixing translation syntax errors"""

    def __init__(self):
        self.load_translations()
        self.syntax_errors = []
        self.fixes_applied = []

    def load_translations(self):
        """Load translation keys from JSON"""
        with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

    def create_translation_function(self):
        """Create a helper function that handles translations properly"""

        translation_helper = '''
def get_translation(key_path, default_value, lang='ko'):
    """Helper function to get translations without syntax errors

    Args:
        key_path: Dot-separated path like 'tabs.validation'
        default_value: Default text if translation not found
        lang: Language code (ko/en/vi)

    Returns:
        Properly escaped translation string for use in f-strings
    """
    keys = key_path.split('.')
    value = translations

    try:
        for key in keys:
            value = value[key]
        return value.get(lang, default_value)
    except (KeyError, TypeError):
        return default_value

def js_translation(key_path, default_value):
    """Generate JavaScript translation code with proper escaping

    Args:
        key_path: JavaScript object path like 'tabs?.validation'
        default_value: Default text if translation not found

    Returns:
        JavaScript template literal safe for f-strings
    """
    # Double the braces for f-string safety
    return f"${{{{translations.{key_path}?.[lang] || '{default_value}'}}}}"
'''
        return translation_helper

    def fix_f_string_templates(self, content):
        """Fix f-string and template literal conflicts"""

        print("\n🔧 Fixing f-string template conflicts...")

        # Rule 1: JavaScript template literals in f-strings need double braces
        # ${...} must become ${{...}} when inside f-strings

        patterns_to_fix = [
            # Fix single brace template literals
            (r'\$\{([^}]+)\}', r'${{\1}}'),

            # Fix closing braces that were missed
            (r'\}\}(?!\})', r'}}'),

            # Fix optional chaining syntax
            (r'\?\.\[', r'?.['),
        ]

        for pattern, replacement in patterns_to_fix:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                self.fixes_applied.append(f"Applied pattern: {pattern[:30]}...")

        return content

    def create_safe_translation_calls(self, content):
        """Replace hardcoded text with safe translation calls"""

        print("\n📝 Creating safe translation calls...")

        # Mapping of Korean text to translation keys
        translation_map = {
            # Tabs
            '요약 및 시스템 검증': ('tabs.validation', 'tabs?.validation'),

            # Status
            '통과': ('individualDetails.conditionStatus.pass', 'individualDetails?.conditionStatus?.pass'),
            '실패': ('individualDetails.conditionStatus.fail', 'individualDetails?.conditionStatus?.fail'),

            # Org Chart
            '전체 조직': ('orgChart.entireOrganization', 'orgChart?.entireOrganization'),
            'TYPE-1 관리자 인센티브 구조': ('orgChart.type1ManagerStructure', 'orgChart?.type1ManagerStructure'),

            # Modal labels
            '직급': ('orgChartModal.position', 'orgChartModal?.position'),
            '계산 과정 상세': ('orgChartModal.calculationDetails', 'orgChartModal?.calculationDetails'),
            '팀 내 LINE LEADER 수': ('orgChartModal.teamLineLeaderCount', 'orgChartModal?.teamLineLeaderCount'),
            '인센티브 받은 LINE LEADER': ('orgChartModal.lineLeadersReceiving', 'orgChartModal?.lineLeadersReceiving'),
            'LINE LEADER 평균 인센티브': ('orgChartModal.lineLeaderAverage', 'orgChartModal?.lineLeaderAverage'),
            '계산식': ('orgChartModal.calculationFormula', 'orgChartModal?.calculationFormula'),

            # Table headers
            '이름': ('orgChartModal.name', 'orgChartModal?.name'),
            '인센티브': ('orgChartModal.incentive', 'orgChartModal?.incentive'),
            '평균 계산 포함': ('orgChartModal.includeInAverage', 'orgChartModal?.includeInAverage'),
            '수령 여부': ('orgChartModal.receivingStatus', 'orgChartModal?.receivingStatus'),
            '합계': ('orgChartModal.total', 'orgChartModal?.total'),
            '평균': ('orgChartModal.average', 'orgChartModal?.average'),
        }

        for korean_text, (python_key, js_key) in translation_map.items():
            # For JavaScript contexts (in HTML generation)
            if f"'{korean_text}'" in content:
                safe_replacement = f"${{{{translations.{js_key}?.[lang] || '{korean_text}'}}}}"
                content = content.replace(f"'{korean_text}'", safe_replacement)
                self.fixes_applied.append(f"Replaced '{korean_text}' with translation")

            if f'"{korean_text}"' in content:
                safe_replacement = f"${{{{translations.{js_key}?.[lang] || '{korean_text}'}}}}"
                content = content.replace(f'"{korean_text}"', safe_replacement)
                self.fixes_applied.append(f"Replaced \"{korean_text}\" with translation")

            # For direct HTML text
            if f">{korean_text}<" in content:
                safe_replacement = f">${{{{{translations.{js_key}?.[lang] || '{korean_text}'}}}}<"
                content = content.replace(f">{korean_text}<", safe_replacement)
                self.fixes_applied.append(f"Replaced HTML >{korean_text}< with translation")

        return content

    def validate_syntax(self, content):
        """Validate Python syntax after fixes"""

        print("\n✅ Validating Python syntax...")

        try:
            compile(content, 'integrated_dashboard_final.py', 'exec')
            print("✅ Python syntax is valid!")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error found: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            self.syntax_errors.append({
                'line': e.lineno,
                'message': str(e),
                'text': e.text
            })
            return False

    def create_test_cases(self):
        """Create test cases for common patterns"""

        test_cases = '''
# Test cases for translation syntax

def test_translation_escaping():
    """Test that all translation patterns work without syntax errors"""

    test_patterns = [
        # Single translation
        f"${{{{translations.tabs?.validation?.[lang] || '요약 및 시스템 검증'}}}}",

        # Nested translation
        f"<div>${{{{translations.orgChart?.entireOrganization?.[lang] || '전체 조직'}}}}</div>",

        # Multiple translations in one string
        f"""
        <th>${{{{translations.orgChartModal?.name?.[lang] || '이름'}}}}</th>
        <th>${{{{translations.orgChartModal?.incentive?.[lang] || '인센티브'}}}}</th>
        """,

        # Translation with variable substitution
        f"${{{{translations.orgChartModal?.averageRecipients?.[lang]?.replace('{{recipients}}', '5').replace('{{total}}', '8') || '(수령자 5명 / 전체 8명)'}}}}",
    ]

    for pattern in test_patterns:
        try:
            # Test that pattern compiles
            exec(f'test = "{pattern}"')
            print(f"✅ Pattern OK: {pattern[:50]}...")
        except SyntaxError as e:
            print(f"❌ Pattern failed: {pattern[:50]}...")
            print(f"   Error: {e}")

    return True

if __name__ == "__main__":
    test_translation_escaping()
'''
        return test_cases

    def apply_fixes(self):
        """Apply all fixes to integrated_dashboard_final.py"""

        print("=" * 80)
        print("🔧 Systematic Translation Syntax Fix")
        print("=" * 80)

        # Read the file
        with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply fixes
        content = self.fix_f_string_templates(content)
        content = self.create_safe_translation_calls(content)

        # Validate
        if self.validate_syntax(content):
            # Write back if valid
            with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
                f.write(content)

            print("\n✅ File updated successfully!")
        else:
            # Save to a different file for debugging
            with open('integrated_dashboard_final_debug.py', 'w', encoding='utf-8') as f:
                f.write(content)

            print("\n⚠️ Syntax errors detected. Debug file saved as integrated_dashboard_final_debug.py")

        # Report
        print("\n📊 Summary:")
        print(f"  - Fixes applied: {len(self.fixes_applied)}")
        print(f"  - Syntax errors: {len(self.syntax_errors)}")

        if self.fixes_applied:
            print("\n📝 Fixes applied:")
            for fix in self.fixes_applied[:10]:  # Show first 10
                print(f"  - {fix}")

        if self.syntax_errors:
            print("\n❌ Remaining syntax errors:")
            for error in self.syntax_errors:
                print(f"  Line {error['line']}: {error['message']}")

        # Save helper function
        with open('translation_helper.py', 'w', encoding='utf-8') as f:
            f.write(self.create_translation_function())

        print("\n💡 Helper function saved to translation_helper.py")

        # Save test cases
        with open('test_translation_syntax.py', 'w', encoding='utf-8') as f:
            f.write(self.create_test_cases())

        print("🧪 Test cases saved to test_translation_syntax.py")

def main():
    """Main execution"""
    fixer = TranslationSystemFixer()
    fixer.apply_fixes()

    print("\n" + "=" * 80)
    print("✨ Recommendations to prevent syntax errors:")
    print("=" * 80)
    print("""
1. **Always use double braces**: ${{{{...}}}} in f-strings
2. **Test incrementally**: Add translations one at a time
3. **Use helper functions**: Create wrapper functions for complex translations
4. **Validate before deployment**: Run syntax check before generating dashboard
5. **Keep fallbacks simple**: Avoid complex expressions in default values
6. **Document patterns**: Maintain examples of working translation patterns
7. **Use raw strings**: For complex patterns, use r-strings to avoid escaping issues
    """)

if __name__ == "__main__":
    main()