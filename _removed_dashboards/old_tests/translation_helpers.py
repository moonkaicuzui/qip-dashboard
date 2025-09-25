
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
