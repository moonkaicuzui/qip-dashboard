# Translation System Best Practices

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
