#!/usr/bin/env python3
"""
Self-Contained HTML Generator for QIP Dashboard
================================================
Converts web-based dashboard HTML to self-contained version
that works offline by inlining all external resources.

Usage:
    python create_self_contained_html.py --month 11 --year 2025
"""

import re
import argparse
from pathlib import Path


def load_library(library_path):
    """Load library file content."""
    try:
        with open(library_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error loading {library_path}: {e}")
        return ""


def create_self_contained_html(input_html_path, output_html_path):
    """
    Convert web-based HTML to self-contained HTML.

    Steps:
    1. Read original HTML
    2. Replace CDN links with inline content
    3. Remove Google Fonts
    4. Update system fonts
    5. Remove Excel download button
    6. Save self-contained HTML
    """

    print(f"📖 Reading: {input_html_path}")

    # Read original HTML
    with open(input_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Load libraries
    print("📦 Loading libraries...")
    bootstrap_css = load_library('static/cdn_libraries/bootstrap.min.css')
    bootstrap_js = load_library('static/cdn_libraries/bootstrap.bundle.min.js')
    fontawesome_css = load_library('static/cdn_libraries/fontawesome.min.css')
    chartjs = load_library('static/cdn_libraries/chart.min.js')
    d3js = load_library('static/cdn_libraries/d3.v7.min.js')

    # 1. Replace Bootstrap CSS CDN with inline
    print("🔄 Replacing Bootstrap CSS...")
    bootstrap_link = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">'
    bootstrap_inline = f'<style id="bootstrap-css">\n{bootstrap_css}\n</style>'
    html_content = html_content.replace(bootstrap_link, bootstrap_inline)

    # 2. Replace Font Awesome CDN with inline
    print("🔄 Replacing Font Awesome CSS...")
    fontawesome_link = '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">'
    fontawesome_inline = f'<style id="fontawesome-css">\n{fontawesome_css}\n</style>'
    html_content = html_content.replace(fontawesome_link, fontawesome_inline)

    # 3. Remove Google Fonts (replace with system fonts in CSS later)
    print("🔄 Removing Google Fonts...")
    html_content = re.sub(
        r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*',
        '',
        html_content
    )
    html_content = re.sub(
        r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*',
        '',
        html_content
    )
    html_content = re.sub(
        r'<link href="https://fonts\.googleapis\.com/css2\?family=Noto\+Sans\+KR:wght@300;400;500;700&family=Noto\+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">',
        '',
        html_content
    )

    # 4. Update font-family in CSS to use system fonts
    print("🔄 Updating to system fonts...")
    html_content = html_content.replace(
        "font-family: 'Noto Sans KR', 'Noto Sans', sans-serif;",
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;"
    )
    html_content = html_content.replace(
        "font-family: 'Noto Sans', sans-serif;",
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;"
    )

    # 5. Replace Bootstrap JS CDN with inline
    print("🔄 Replacing Bootstrap JS...")
    bootstrap_js_link = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>'
    bootstrap_js_inline = f'<script id="bootstrap-js">\n{bootstrap_js}\n</script>'
    html_content = html_content.replace(bootstrap_js_link, bootstrap_js_inline)

    # 6. Replace Chart.js CDN with inline
    print("🔄 Replacing Chart.js...")
    chartjs_link = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
    chartjs_inline = f'<script id="chartjs">\n{chartjs}\n</script>'
    html_content = html_content.replace(chartjs_link, chartjs_inline)

    # 7. Replace D3.js CDN with inline
    print("🔄 Replacing D3.js...")
    d3js_link = '<script src="https://d3js.org/d3.v7.min.js"></script>'
    d3js_inline = f'<script id="d3js">\n{d3js}\n</script>'
    html_content = html_content.replace(d3js_link, d3js_inline)

    # 8. Remove Excel download button
    print("🔄 Removing Excel download button...")
    # Find and remove the Excel download button
    html_content = re.sub(
        r'<button id="downloadExcelBtn".*?</button>',
        '<!-- Excel download removed in Self-Contained version -->',
        html_content,
        flags=re.DOTALL
    )

    # Also disable Excel download function
    html_content = html_content.replace(
        'function downloadExcel() {',
        'function downloadExcel() {\n            alert("Excel download is not available in Self-Contained version. Please use the web version for Excel download.");\n            return;\n            // Original function disabled below:'
    )

    # 9. Remove authentication/password check
    print("🔄 Removing authentication check...")
    # Replace validateSession function to always return true
    html_content = html_content.replace(
        'function validateSession() {',
        'function validateSession() {\n                // Authentication disabled in Self-Contained version\n                return true;\n                // Original function disabled below:'
    )
    # Remove redirect to auth.html
    html_content = html_content.replace(
        "window.location.href = 'auth.html';",
        "// Redirect disabled in Self-Contained version"
    )

    # 10. Add Self-Contained indicator
    print("🔄 Adding Self-Contained indicator...")
    self_contained_badge = '''
    <!-- Self-Contained Version Indicator -->
    <style>
        .self-contained-badge {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(40, 167, 69, 0.9);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            z-index: 10000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
    </style>
    <div class="self-contained-badge">
        📦 Offline Version (No Password Required)
    </div>
    '''

    # Insert badge after <body> tag
    html_content = html_content.replace('<body>', f'<body>\n{self_contained_badge}')

    # 10. Save self-contained HTML
    print(f"💾 Saving: {output_html_path}")
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Get file sizes
    original_size = Path(input_html_path).stat().st_size / 1024 / 1024  # MB
    selfcontained_size = Path(output_html_path).stat().st_size / 1024 / 1024  # MB

    print(f"\n✅ Self-Contained HTML created successfully!")
    print(f"   Original size: {original_size:.2f} MB")
    print(f"   Self-Contained size: {selfcontained_size:.2f} MB")
    print(f"   Size increase: +{selfcontained_size - original_size:.2f} MB")
    print(f"\n📂 Output: {output_html_path}")
    print(f"\n📋 Features:")
    print(f"   ✅ Works offline (double-click to open)")
    print(f"   ✅ All charts functional")
    print(f"   ✅ All interactive features")
    print(f"   ❌ Excel download removed (use web version)")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Self-Contained HTML for QIP Dashboard'
    )
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--year', type=int, required=True, help='Year (e.g., 2025)')

    args = parser.parse_args()

    # Construct file paths
    month_str = str(args.month).zfill(2)
    input_html = f"docs/Incentive_Dashboard_{args.year}_{month_str}_Version_9.0.html"
    output_html = f"docs/Incentive_Dashboard_{args.year}_{month_str}_Version_9.0_SelfContained.html"

    # Check if input exists
    if not Path(input_html).exists():
        print(f"❌ Error: Input file not found: {input_html}")
        print(f"   Please generate the dashboard first:")
        print(f"   python integrated_dashboard_final.py --month {args.month} --year {args.year}")
        return 1

    # Check if libraries exist
    lib_dir = Path('static/cdn_libraries')
    if not lib_dir.exists():
        print(f"❌ Error: Library directory not found: {lib_dir}")
        print(f"   Please ensure CDN libraries are downloaded.")
        return 1

    # Generate self-contained HTML
    create_self_contained_html(input_html, output_html)

    return 0


if __name__ == '__main__':
    exit(main())
