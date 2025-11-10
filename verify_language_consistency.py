#!/usr/bin/env python3
"""
Language consistency verification script
Checks that Korean, English, and Vietnamese translations are consistent
특히 월 표시가 올바른지 검증
"""

import re
from bs4 import BeautifulSoup

def verify_dashboard_languages(html_file_path):
    """대시보드 HTML 파일의 언어 일관성 검증"""

    print("=" * 60)
    print("📊 Dashboard Language Consistency Verification")
    print("=" * 60)

    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract month and year from the data
    year_match = re.search(r'const yearText = [\'"](\d{4})[\'"]', html_content)
    if year_match:
        year = year_match.group(1)
        print(f"📅 Year detected: {year}")

    # Check month translations in JavaScript
    print("\n🔍 Checking month translations in JavaScript code...")

    # Find the monthText variable assignment
    month_text_pattern = r"const monthText = currentLanguage === 'ko' \? '([^']+)' :\s*currentLanguage === 'en' \? '([^']+)' :\s*'([^']+)';"
    month_match = re.search(month_text_pattern, html_content)

    if month_match:
        ko_month = month_match.group(1)
        en_month = month_match.group(2)
        vi_month = month_match.group(3)

        print(f"  Korean: {ko_month}")
        print(f"  English: {en_month}")
        print(f"  Vietnamese: {vi_month}")

        # Verify month consistency
        month_number = None

        # Extract month number from Korean
        ko_month_match = re.search(r'(\d+)월', ko_month)
        if ko_month_match:
            month_number = int(ko_month_match.group(1))
            print(f"\n✅ Month number from Korean: {month_number}")

        # Verify English month name
        month_names_en = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
        if en_month in month_names_en:
            en_month_number = month_names_en.index(en_month) + 1
            print(f"✅ Month number from English: {en_month_number}")

            if month_number and month_number != en_month_number:
                print(f"❌ ERROR: Korean month ({month_number}) doesn't match English month ({en_month_number})")

        # Verify Vietnamese month
        vi_month_match = re.search(r'Tháng (\d+)', vi_month)
        if vi_month_match:
            vi_month_number = int(vi_month_match.group(1))
            print(f"✅ Month number from Vietnamese: {vi_month_number}")

            if month_number and month_number != vi_month_number:
                print(f"❌ ERROR: Korean month ({month_number}) doesn't match Vietnamese month ({vi_month_number})")
        else:
            print(f"❌ ERROR: Vietnamese month format is incorrect: {vi_month}")

    # Check modal month translations
    print("\n🔍 Checking modal month translations...")
    modal_month_pattern = r"const monthNames = \{\s*'ko': '([^']+)',\s*'en': '([^']+)',\s*'vi': '([^']+)'\s*\}"
    modal_match = re.search(modal_month_pattern, html_content)

    if modal_match:
        modal_ko = modal_match.group(1)
        modal_en = modal_match.group(2)
        modal_vi = modal_match.group(3)

        print(f"  Modal Korean: {modal_ko}")
        print(f"  Modal English: {modal_en}")
        print(f"  Modal Vietnamese: {modal_vi}")

        # Check if they contain placeholders or actual values
        if '__MONTH_' in modal_ko or '__MONTH_' in modal_en or '__MONTH_' in modal_vi:
            print("  ⚠️ Warning: Placeholders found that should have been replaced")

    # Check for hardcoded "Tháng 8" or "Tháng 9"
    print("\n🔍 Checking for hardcoded month values...")
    hardcoded_months = re.findall(r'[\'"]Tháng \d+[\'"]', html_content)
    if hardcoded_months:
        print(f"  ⚠️ Found hardcoded Vietnamese months: {set(hardcoded_months)}")
        for hardcoded in set(hardcoded_months):
            # Count occurrences
            count = html_content.count(hardcoded)
            print(f"    {hardcoded}: {count} occurrences")

    # Check data period display
    print("\n🔍 Checking data period display...")
    data_period_pattern = r'data-year="(\d+)" data-month="(\d+)"'
    periods = re.findall(data_period_pattern, html_content)
    if periods:
        for year, month in periods[:3]:  # Show first 3 occurrences
            print(f"  Data period found: {year}-{month:0>2}")

    print("\n" + "=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)

    # Final consistency check
    if month_number:
        all_consistent = True

        # Check if all detected months match
        if vi_month_match and int(vi_month_match.group(1)) != month_number:
            print(f"❌ Vietnamese month inconsistency detected!")
            print(f"   Expected: Tháng {month_number}")
            print(f"   Found: Tháng {vi_month_match.group(1)}")
            all_consistent = False

        if all_consistent:
            print(f"✅ All languages show the same month: {month_number}월 / {month_names_en[month_number-1]} / Tháng {month_number}")
        else:
            print("❌ Language inconsistency detected - please fix the issues above")
    else:
        print("⚠️ Could not determine month number for verification")

if __name__ == "__main__":
    import sys

    # Default to the most recent dashboard
    if len(sys.argv) > 1:
        html_file = sys.argv[1]
    else:
        html_file = "output_files/Incentive_Dashboard_2025_11_Version_8.02.html"

    print(f"Verifying: {html_file}\n")
    verify_dashboard_languages(html_file)