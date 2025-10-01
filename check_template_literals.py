#!/usr/bin/env python3
"""
HTML 파일에서 template literal 사용 확인
"""
import re

html_path = 'output_files/Incentive_Dashboard_2025_09_Version_6.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all ${...} patterns
pattern = r'\$\{[^}]+\}'
matches = re.findall(pattern, content)

print(f"Total ${{...}} occurrences: {len(matches)}")
print("\n처음 20개:")
for i, match in enumerate(matches[:20], 1):
    # Truncate if too long
    display = match if len(match) < 80 else match[:80] + '...'
    print(f"{i:3d}. {display}")

# Check if these are inside backticks
print("\n\n백틱(`) 안에 있는지 확인:")
# Find template literals with ${
template_literal_pattern = r'`[^`]*\$\{[^`]*`'
template_literals = re.findall(template_literal_pattern, content, re.DOTALL)
print(f"Template literals with ${{}}: {len(template_literals)}")

# Check if there are ${} outside of backticks
print("\n\n백틱 밖에 있는 ${{}} 패턴 확인...")
# This is tricky, but we can check if ${} appears in strings with quotes
quoted_pattern = r'["\'][^"\']*\$\{[^"\']*["\']'
quoted_matches = re.findall(quoted_pattern, content)
if quoted_matches:
    print(f"⚠️ 따옴표 안에 ${{}} 발견: {len(quoted_matches)}개")
    for i, match in enumerate(quoted_matches[:5], 1):
        print(f"   {i}. {match[:100]}")
else:
    print("✅ 따옴표 안에 ${{}}가 없음 (정상)")
